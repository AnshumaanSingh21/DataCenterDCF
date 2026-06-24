"""
Market intelligence agent.

Replaces the old RAG-based approach with a direct LLM call using
build_market_intelligence_prompt(). Results are validated and cached
with a 90-day TTL.

Return value of market_agent():
  {
    "rev_overrides"  : dict,   # validated assumption overrides for revenue engine
    "capex_overrides": dict,   # validated assumption overrides for capex engine
    "loan_overrides" : dict,   # validated assumption overrides for loan engine
    "audit"          : list,   # per-field accept/reject log
    "from_cache"     : bool,
    "cache_age_days" : float | None,
  }

Callers should apply these overrides ON TOP of fresh defaults — do not
use them as standalone assumption sets.
"""

from assumptions.revenue_defaults import (
    FACILITY_TYPE_OVERRIDES,
    DEFAULT_REVENUE_ASSUMPTIONS,
    get_default_revenue_assumptions,
)
from assumptions.capex_defaults import (
    get_default_capex_assumptions,
)
from assumptions.loan_defaults import (
    get_default_loan_assumptions,
)

from src.llm.prompts import build_market_intelligence_prompt
from src.llm.llm_interface import extract_with_llm
from src.extraction.validator import validate_market_intelligence
from src.agents.market_cache import get as cache_get, set as cache_set


# sqft_per_rack * effective_area_multiplier from capex_defaults
_DEFAULT_EFFECTIVE_SQFT_PER_RACK = 100.0   # 50 sqft * 2.0 multiplier


def _extract_overrides_from_audit(audit: list) -> dict:
    """
    Pull only the LLM-sourced and derived values from the audit log.
    These are the values that should be cached and applied over defaults.
    """
    overrides = {"revenue": {}, "capex": {}, "loan": {}}
    for entry in audit:
        if (
            entry.get("source") in ("llm", "derived")
            and entry.get("engine") in overrides
            and entry.get("model_key") is not None
            and entry.get("model_value") is not None
        ):
            overrides[entry["engine"]][entry["model_key"]] = entry["model_value"]
    return overrides


def market_agent(
    location: str,
    facility_type: str = "retail_colo",
    total_racks: int = 1000,
    kw_per_rack: float = 6.0,
    force_refresh: bool = False,
) -> dict:
    """
    Fetch market intelligence for a given location + facility type.

    1. Check TTL cache — return cached result if fresh and force_refresh=False
    2. Call LLM with structured market intelligence prompt
    3. Validate response (bounds + confidence filter)
    4. Store in cache
    5. Return overrides + audit

    Parameters
    ----------
    force_refresh : bool
        If True, bypass the cache and re-call the LLM regardless of TTL.
    """
    total_mw = round(total_racks * kw_per_rack / 1000.0, 1)

    # Resolve kw_per_rack from facility type overrides (same as revenue engine)
    ft_overrides = FACILITY_TYPE_OVERRIDES.get(facility_type, {})
    kw_per_rack  = ft_overrides.get(
        "kw_per_rack",
        DEFAULT_REVENUE_ASSUMPTIONS["kw_per_rack"]
    )

    # ------------------------------------------------------------------
    # 1. Cache lookup
    # ------------------------------------------------------------------
    if not force_refresh:
        cached = cache_get(location, facility_type)
        if cached is not None:
            rev_ov   = cached["overrides"].get("revenue", {})
            capex_ov = cached["overrides"].get("capex",   {})
            loan_ov  = cached["overrides"].get("loan",    {})
            return {
                "rev_overrides":   rev_ov,
                "capex_overrides": capex_ov,
                "loan_overrides":  loan_ov,
                "audit":           cached.get("audit", []),
                "from_cache":      True,
                "cache_age_days":  cached.get("age_days"),
            }

    # ------------------------------------------------------------------
    # 2. Build prompt and call LLM
    # ------------------------------------------------------------------
    prompt = build_market_intelligence_prompt(
        location               = location,
        facility_type          = facility_type,
        total_racks            = total_racks,
        total_mw               = total_mw,
        kw_per_rack            = kw_per_rack,
        year                   = 2026,
        effective_sqft_per_rack= _DEFAULT_EFFECTIVE_SQFT_PER_RACK,
    )

    llm_raw = extract_with_llm(prompt)

    # ------------------------------------------------------------------
    # 3. Validate
    # ------------------------------------------------------------------
    rev_merged, capex_merged, loan_merged, audit = validate_market_intelligence(
        llm_response           = llm_raw,
        location               = location,
        facility_type          = facility_type,
        kw_per_rack            = kw_per_rack,
        rev_defaults           = get_default_revenue_assumptions(),
        capex_defaults         = get_default_capex_assumptions(),
        loan_defaults          = get_default_loan_assumptions(),
        effective_sqft_per_rack= _DEFAULT_EFFECTIVE_SQFT_PER_RACK,
    )

    # Extract only LLM-sourced values (not the full merged dicts) for storage
    overrides = _extract_overrides_from_audit(audit)

    # ------------------------------------------------------------------
    # 4. Store in cache
    # ------------------------------------------------------------------
    cache_set(
        location      = location,
        facility_type = facility_type,
        llm_raw       = llm_raw,
        audit         = audit,
        overrides     = overrides,
    )

    return {
        "rev_overrides":   overrides["revenue"],
        "capex_overrides": overrides["capex"],
        "loan_overrides":  overrides["loan"],
        "audit":           audit,
        "from_cache":      False,
        "cache_age_days":  None,
    }
