import json
from copy import deepcopy

from src.llm.prompts import (
    _CITY_MRC_RANGE,
    _FACILITY_MRC_MULTIPLIER,
    _CITY_CONSTRUCTION_COST,
    _ELECTRICAL_CAPEX_PER_MW,
    _MECHANICAL_CAPEX_PER_MW,
)

# ---------------------------------------------------------------------------
# Minimum confidence to accept a value. "low" is always rejected.
# ---------------------------------------------------------------------------
_ACCEPTED_CONFIDENCE = {"high", "medium"}

# ---------------------------------------------------------------------------
# Global bounds for fields that are not location-specific
# ---------------------------------------------------------------------------
_GLOBAL_BOUNDS = {
    "utility_tariff_rs_per_kwh":      (5.0,   14.0),
    "tenant_power_markup_rs_per_kwh": (0.5,    5.0),
    "land_cost_rs_per_sqft":          (1_000, 20_000),
    "pue":                            (1.2,    2.2),
    "interest_rate_pct":              (7.0,   15.0),
}

# ---------------------------------------------------------------------------
# LLM field → model mapping
# Each entry describes how to convert and where to write the validated value.
#
# "engines"  : list of (engine_name, key, transform_fn)
#   engine_name : "revenue" | "capex" | "loan"
#   key         : the assumption dict key
#   transform   : callable(llm_value, ctx) → model_value
#                 ctx = {"kw_per_rack": float, "utility_tariff": float}
# ---------------------------------------------------------------------------

def _div1e7(v, _ctx):        return round(v / 1e7, 6)
def _identity(v, _ctx):      return v
def _pct_to_dec(v, _ctx):    return round(v / 100.0, 4)
def _per_mw_to_rack(v, ctx): return round(v * ctx["kw_per_rack"] / 1000.0, 6)

FIELD_MAP = {
    "rack_mrc_rs_per_month": {
        "engines": [
            ("revenue", "rack_mrc_crore",            _div1e7),
            ("revenue", "rack_price_per_rack_crore",  _div1e7),
        ],
    },
    "utility_tariff_rs_per_kwh": {
        "engines": [
            ("revenue", "utility_tariff_rs_per_kwh", _identity),
        ],
    },
    "tenant_power_markup_rs_per_kwh": {
        "engines": [
            ("revenue", "power_markup_rs_per_kwh",   _identity),
        ],
        # tenant_power_rate is derived after both tariff + markup are validated
    },
    "land_cost_rs_per_sqft": {
        "engines": [
            ("capex", "land_cost_per_sqft_rs",       _identity),
        ],
    },
    "pue": {
        "engines": [
            ("revenue", "pue",                        _identity),
        ],
    },
    "interest_rate_pct": {
        "engines": [
            ("loan", "interest_rate",                 _pct_to_dec),
            ("loan", "market_interest_rate",          _pct_to_dec),
        ],
    },
    "civil_cost_cr_per_rack": {
        "engines": [
            ("capex", "civil_cost_per_rack",          _identity),
        ],
    },
    "electrical_capex_cr_per_mw": {
        "engines": [
            ("capex", "electrical_cost_per_rack",     _per_mw_to_rack),
        ],
    },
    "mechanical_capex_cr_per_mw": {
        "engines": [
            ("capex", "mechanical_cost_per_rack",     _per_mw_to_rack),
        ],
    },
}


# ---------------------------------------------------------------------------
# Build location + facility-type aware bounds for a given run
# ---------------------------------------------------------------------------

def _build_bounds(location, facility_type, effective_sqft_per_rack, kw_per_rack):
    bounds = dict(_GLOBAL_BOUNDS)

    _base_mrc = _CITY_MRC_RANGE.get(location, (30_000, 1_50_000))
    _mrc_mult = _FACILITY_MRC_MULTIPLIER.get(facility_type, 1.0)
    mrc_range = (round(_base_mrc[0] * _mrc_mult), round(_base_mrc[1] * _mrc_mult))
    bounds["rack_mrc_rs_per_month"] = mrc_range

    constr_range = _CITY_CONSTRUCTION_COST.get(location, (4_000, 8_000))
    civil_low  = round(constr_range[0] * effective_sqft_per_rack / 1e7, 4)
    civil_high = round(constr_range[1] * effective_sqft_per_rack / 1e7, 4)
    bounds["civil_cost_cr_per_rack"] = (civil_low, civil_high)

    elec_range = _ELECTRICAL_CAPEX_PER_MW.get(facility_type, (3.5, 5.5))
    mech_range = _MECHANICAL_CAPEX_PER_MW.get(facility_type, (2.5, 4.0))
    bounds["electrical_capex_cr_per_mw"] = elec_range
    bounds["mechanical_capex_cr_per_mw"] = mech_range

    return bounds


# ---------------------------------------------------------------------------
# Core validator
# ---------------------------------------------------------------------------

def validate_market_intelligence(
    llm_response,
    location,
    facility_type,
    kw_per_rack,
    rev_defaults,
    capex_defaults,
    loan_defaults,
    effective_sqft_per_rack=100.0,
):
    """
    Validate LLM market intelligence output and merge into model assumptions.

    Returns
    -------
    rev_assumptions  : dict  merged revenue assumptions
    capex_assumptions: dict  merged capex assumptions
    loan_assumptions : dict  merged loan assumptions
    audit            : list  one entry per LLM field explaining accept/reject decision
    """
    rev   = deepcopy(rev_defaults)
    capex = deepcopy(capex_defaults)
    loan  = deepcopy(loan_defaults)
    audit = []

    # 1. Parse LLM output
    if isinstance(llm_response, str):
        try:
            parsed = json.loads(llm_response)
        except (json.JSONDecodeError, ValueError) as e:
            return rev, capex, loan, [{"error": f"JSON parse failed: {e}"}]
    else:
        parsed = llm_response

    bounds = _build_bounds(
        location, facility_type, effective_sqft_per_rack, kw_per_rack
    )

    ctx = {
        "kw_per_rack":    kw_per_rack,
        "utility_tariff": None,   # filled in after tariff field is processed
    }

    accepted_llm = {}  # track accepted raw llm values for cross-field derivations

    # 2. Validate each field
    for llm_field, field_cfg in FIELD_MAP.items():
        entry = parsed.get(llm_field, {})

        llm_value      = entry.get("value")       if isinstance(entry, dict) else None
        llm_confidence = entry.get("confidence")  if isinstance(entry, dict) else None
        llm_reasoning  = entry.get("reasoning", "") if isinstance(entry, dict) else ""

        rejection_reason = None
        accepted         = False

        if llm_value is None:
            rejection_reason = "null_value"

        elif llm_confidence not in _ACCEPTED_CONFIDENCE:
            rejection_reason = "low_confidence"

        else:
            lo, hi = bounds.get(llm_field, (None, None))
            if lo is not None and not (lo <= llm_value <= hi):
                rejection_reason = "out_of_bounds"
            else:
                accepted = True

        if accepted:
            accepted_llm[llm_field] = llm_value
            for engine_name, key, transform in field_cfg["engines"]:
                model_value = transform(llm_value, ctx)
                target = {"revenue": rev, "capex": capex, "loan": loan}[engine_name]
                target[key] = model_value
                audit.append({
                    "llm_field":        llm_field,
                    "source":           "llm",
                    "llm_value":        llm_value,
                    "llm_confidence":   llm_confidence,
                    "llm_reasoning":    llm_reasoning,
                    "engine":           engine_name,
                    "model_key":        key,
                    "model_value":      model_value,
                    "rejection_reason": None,
                })
            # Track utility tariff for tenant_rate derivation
            if llm_field == "utility_tariff_rs_per_kwh":
                ctx["utility_tariff"] = llm_value
        else:
            # Determine default value for audit log
            default_val = (
                rev_defaults.get(FIELD_MAP[llm_field]["engines"][0][1])
                or capex_defaults.get(FIELD_MAP[llm_field]["engines"][0][1])
                or loan_defaults.get(FIELD_MAP[llm_field]["engines"][0][1])
            )
            audit.append({
                "llm_field":        llm_field,
                "source":           "default",
                "llm_value":        llm_value,
                "llm_confidence":   llm_confidence,
                "llm_reasoning":    llm_reasoning,
                "engine":           FIELD_MAP[llm_field]["engines"][0][0],
                "model_key":        FIELD_MAP[llm_field]["engines"][0][1],
                "model_value":      default_val,
                "rejection_reason": rejection_reason,
            })

    # 3. Derive tenant_power_rate from accepted tariff + markup
    tariff = accepted_llm.get("utility_tariff_rs_per_kwh")
    markup = accepted_llm.get("tenant_power_markup_rs_per_kwh")
    if tariff is not None and markup is not None:
        derived_rate = round(tariff + markup, 2)
        rev["tenant_power_rate_rs_per_kwh"] = derived_rate
        audit.append({
            "llm_field":        "tenant_power_rate_rs_per_kwh",
            "source":           "derived",
            "llm_value":        derived_rate,
            "llm_confidence":   "high",
            "llm_reasoning":    f"utility_tariff ({tariff}) + markup ({markup}) = {derived_rate}",
            "engine":           "revenue",
            "model_key":        "tenant_power_rate_rs_per_kwh",
            "model_value":      derived_rate,
            "rejection_reason": None,
        })

    # 4. Include parity check in audit if present
    parity = parsed.get("parity_check")
    if isinstance(parity, dict):
        audit.append({
            "llm_field":        "parity_check",
            "source":           "info",
            "llm_value":        parity,
            "llm_confidence":   None,
            "llm_reasoning":    f"implied_all_in={parity.get('implied_all_in_rs_per_month')}, "
                                f"stated={parity.get('stated_all_in_rs_per_month')}, "
                                f"flag={parity.get('flag')}",
            "engine":           None,
            "model_key":        None,
            "model_value":      None,
            "rejection_reason": None,
        })

    # 5. Cross-field consistency checks
    # Per-field bounds can't catch values that are individually plausible but
    # mutually contradictory. These checks flag internal incoherence so a shaky
    # extraction is visible rather than silently trusted.
    flags = _cross_field_consistency(accepted_llm, ctx, bounds)
    audit.append({
        "llm_field":        "consistency_check",
        "source":           "validator",
        "llm_value":        {"flags": flags, "passed": len(flags) == 0},
        "llm_confidence":   None,
        "llm_reasoning":    "; ".join(flags) if flags else "all cross-field checks passed",
        "engine":           None,
        "model_key":        None,
        "model_value":      None,
        "rejection_reason": None,
    })

    return rev, capex, loan, audit


def _cross_field_consistency(accepted_llm, ctx, bounds):
    """Return a list of human-readable flags where accepted LLM values are
    individually in-bounds but mutually inconsistent. Empty list = coherent."""
    flags = []
    kw     = ctx.get("kw_per_rack", 6.0)
    mrc    = accepted_llm.get("rack_mrc_rs_per_month")
    tariff = accepted_llm.get("utility_tariff_rs_per_kwh")
    markup = accepted_llm.get("tenant_power_markup_rs_per_kwh")
    pue    = accepted_llm.get("pue")
    mech   = accepted_llm.get("mechanical_capex_cr_per_mw")

    # (a) Power should be a sane share of the all-in tenant bill.
    if mrc and tariff is not None and markup is not None:
        power_component = kw * 730 * (tariff + markup)   # Rs/month
        all_in = mrc + power_component
        if all_in > 0:
            share = power_component / all_in
            if not (0.30 <= share <= 0.75):
                flags.append(
                    f"power is {share:.0%} of all-in tenant bill (expected 30-75%) — "
                    f"rack MRC ({mrc:,.0f}) and power pricing are likely inconsistent"
                )

    # (b) Markup should be a sane fraction of the utility tariff.
    if tariff and markup is not None and tariff > 0:
        ratio = markup / tariff
        if not (0.03 <= ratio <= 0.50):
            flags.append(
                f"power markup is {ratio:.0%} of the utility tariff (expected 3-50%)"
            )

    # (c) A low (efficient) PUE implies more cooling spend, not less.
    if pue is not None and mech is not None:
        mlo, mhi = bounds.get("mechanical_capex_cr_per_mw", (2.5, 4.0))
        if mhi > mlo:
            mech_pos = (mech - mlo) / (mhi - mlo)   # 0 = cheap, 1 = expensive
            if pue < 1.45 and mech_pos < 0.40:
                flags.append(
                    f"PUE {pue} implies advanced/efficient cooling but mechanical "
                    f"capex {mech} Cr/MW sits at the low end — directionally inconsistent"
                )

    return flags


# ---------------------------------------------------------------------------
# Legacy single-field validator (kept for backward compatibility)
# ---------------------------------------------------------------------------

def validate_assumption(assumption_name, value):
    from src.extraction.assumption_schema import ASSUMPTION_DEFINITIONS
    if value is None:
        return False
    if assumption_name not in ASSUMPTION_DEFINITIONS:
        return False
    lo, hi = ASSUMPTION_DEFINITIONS[assumption_name]["valid_range"]
    return lo <= value <= hi
