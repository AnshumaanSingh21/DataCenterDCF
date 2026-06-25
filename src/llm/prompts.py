from src.extraction.assumption_schema import (
    ASSUMPTION_DEFINITIONS
)

# ---------------------------------------------------------------------------
# City → State → DISCOM mapping for power tariff grounding
# ---------------------------------------------------------------------------
_CITY_DISCOM = {
    "Mumbai":    ("Maharashtra", "MSEDCL", "MERC Tariff Order 2024",       "8.5–9.5"),
    "Pune":      ("Maharashtra", "MSEDCL", "MERC Tariff Order 2024",       "8.5–9.5"),
    "Bangalore": ("Karnataka",   "BESCOM", "KERC Tariff Order 2025-26",    "7.8–8.6"),
    "Delhi NCR": ("Delhi",       "BSES/Tata Power", "DERC Order 2025",     "8.2–9.0"),
    "Hyderabad": ("Telangana",   "TSSPDCL", "TGERC Tariff Order 2025-26", "7.2–7.9"),
    "Chennai":   ("Tamil Nadu",  "TANGEDCO", "TNERC Tariff Order 2025",   "8.4–9.1"),
}

# City-specific tighter valid ranges for rack MRC (space-only, Rs/rack/month)
_CITY_MRC_RANGE = {
    "Mumbai":    (45_000, 90_000),
    "Bangalore": (40_000, 80_000),
    "Delhi NCR": (42_000, 82_000),
    "Hyderabad": (35_000, 70_000),
    "Chennai":   (33_000, 68_000),
    "Pune":      (32_000, 65_000),
}

# Facility-type multipliers applied on top of city base range
_FACILITY_MRC_MULTIPLIER = {
    "retail_colo": 1.0,
    "wholesale":   0.70,
    "ai_hpc":      2.50,
    "hyperscale":  0.80,
}

# Borrower class context based on project description
_BORROWER_CLASS = "Greenfield, first project, no operational track record"

# City-specific DC-grade construction cost ranges (Rs/sqft)
# Covers: building shell + raised floor + false ceiling + fire suppression
# + access control + interiors. Excludes land, MEP, IT hardware.
# Source: CBRE India Construction Cost Guide 2024, JLL India DC Build Cost Survey 2024
_CITY_CONSTRUCTION_COST = {
    "Mumbai":    (6_000, 8_500),   # Highest — MCGM compliance, premium labor, coastal conditions
    "Bangalore": (5_000, 7_000),   # BBMP compliance, moderate labor market
    "Delhi NCR": (5_000, 7_000),   # Similar to Bangalore; seismic zone consideration
    "Hyderabad": (4_500, 6_000),   # Lower labor costs, HMDA approval overhead
    "Chennai":   (4_500, 6_000),   # Moderate; cyclone-resistant design adds ~5-8%
    "Pune":      (4_500, 6_500),   # Between Mumbai and Hyderabad
}

# Tier III N+1 DC equipment CapEx benchmarks (Cr per MW of IT load)
# Source: JM Financial Data Centre 101 (March 2025), CBRE India DC Cost Benchmarks 2024
# These are EQUIPMENT-ONLY costs (no civil, no land, no soft costs)
_ELECTRICAL_CAPEX_PER_MW = {
    "retail_colo": (3.5, 5.5),    # UPS, batteries, DGs, transformers, switchgear, cabling — N+1
    "wholesale":   (3.0, 5.0),    # Slightly simpler tenant fit-out; similar core infra
    "ai_hpc":      (5.0, 8.0),    # Higher power density → larger UPS, DG, transformer capacity
    "hyperscale":  (3.0, 5.0),    # Bulk procurement advantage; simpler redundancy design
}
_MECHANICAL_CAPEX_PER_MW = {
    "retail_colo": (2.5, 4.0),    # Chilled water plant + CRAC/CRAH + cooling towers — N+1
    "wholesale":   (2.0, 3.5),    # Similar cooling infra, slightly less redundancy
    "ai_hpc":      (4.0, 7.0),    # Liquid/immersion cooling significantly more expensive
    "hyperscale":  (2.0, 3.5),    # Scale economics; standardised cooling modules
}


def build_market_intelligence_prompt(
    location: str,
    facility_type: str,
    total_racks: int,
    total_mw: float,
    kw_per_rack: float,
    year: int,
    effective_sqft_per_rack: float = 100.0,
) -> str:
    """
    Direct LLM market intelligence prompt — no RAG context needed.
    LLM reasons from injected anchor data + its own training knowledge.
    Returns structured JSON with value + confidence + reasoning per assumption.
    """
    discom_info = _CITY_DISCOM.get(location)
    if discom_info:
        state, discom, tariff_order, tariff_range = discom_info
        power_tariff_block = (
            f"- Location maps to: {state} → {discom} ({tariff_order})\n"
            f"- Published HT commercial rate: ₹{tariff_range}/kWh (blended annual average, 24/7 steady-state load)\n"
            f"- Source: State Electricity Regulatory Commission tariff order (publicly available on {discom} website)\n"
            f"- Note: Use annual blended rate, not peak/off-peak. Data centers run 24/7 steady-state."
        )
    else:
        power_tariff_block = (
            "- No specific DISCOM mapping for this location. Use national HT commercial average.\n"
            "- Reference ranges: Maharashtra ₹8.5–9.5, Karnataka ₹7.8–8.6, Delhi ₹8.2–9.0, Telangana ₹7.2–7.9, Tamil Nadu ₹8.4–9.1\n"
            "- Return medium confidence if location does not match any of the above."
        )

    _base_mrc = _CITY_MRC_RANGE.get(location, (30_000, 1_50_000))
    _mrc_mult = _FACILITY_MRC_MULTIPLIER.get(facility_type, 1.0)
    mrc_range = (round(_base_mrc[0] * _mrc_mult), round(_base_mrc[1] * _mrc_mult))
    power_component_low  = round(kw_per_rack * 730 * 9.0)
    power_component_high = round(kw_per_rack * 730 * 11.0)

    construction_range = _CITY_CONSTRUCTION_COST.get(location, (4_000, 8_000))
    civil_cost_low  = round(construction_range[0] * effective_sqft_per_rack / 1e7, 4)
    civil_cost_high = round(construction_range[1] * effective_sqft_per_rack / 1e7, 4)

    elec_range = _ELECTRICAL_CAPEX_PER_MW.get(facility_type, (3.5, 5.5))
    mech_range = _MECHANICAL_CAPEX_PER_MW.get(facility_type, (2.5, 4.0))

    facility_pricing_note = {
        "retail_colo": (
            "Retail colocation: multiple enterprise tenants, standard 6kW racks. "
            "Space-only charge (excluding power). "
            "DO NOT use wholesale, hyperscale, or managed-services pricing — exclude these explicitly."
        ),
        "wholesale": (
            "Wholesale: single large tenant, 1MW+ blocks. "
            "All-in price (space + power bundled). "
            "25–35% discount to retail colo same city. "
            "DO NOT use retail colo or AI/HPC pricing."
        ),
        "ai_hpc": (
            "AI/HPC: high-density racks 20–40kW+, liquid/immersion cooling. "
            "40–80% premium above retail colo. "
            "Only apply premium if context explicitly mentions GPU density or liquid cooling. "
            "If in doubt, use retail colo rate with 0% premium and medium confidence."
        ),
        "hyperscale": (
            "Hyperscale: single tenant, 10MW+ campus. "
            "30–40% discount to retail colo. "
            "DO NOT use retail colo pricing."
        ),
    }.get(facility_type, "Use retail colocation pricing as default.")

    return f"""You are a senior data center market analyst and infrastructure finance specialist \
with deep expertise in the Indian data center sector. You have studied operator financials, \
market reports from CBRE, Cushman & Wakefield, JM Financial, and state DISCOM tariff orders.

Your task: provide specific, defensible market assumptions for a greenfield data center DCF model.
Reason step by step before giving each value. If you cannot provide a defensible estimate with \
medium or high confidence, return null — do NOT fabricate numbers.

=== PROJECT CONTEXT ===
Location        : {location}
Facility Type   : {facility_type}
Total Capacity  : {total_racks} racks | {total_mw} MW IT load
kW per rack     : {kw_per_rack} kW
Projection Year : {year}
Borrower Class  : {_BORROWER_CLASS}

=== METHODOLOGY ===
For each assumption, in this exact order:
1. STATE the anchor data point and source you are reasoning from
2. SHOW the derivation or arithmetic
3. GIVE a single point estimate (not a range)
4. ASSIGN confidence using the matrix below — do not guess the tier

Confidence matrix:
- "high"   : Explicit value from SERC tariff order, audited operator report, or \
broker research <12 months old. Multiple sources agree within 10%.
- "medium" : Industry report (CBRE, JM Financial) or equity research citing basis. \
Single source, or sources agree within 20%.
- "low"    : Opinion/estimate without clear source, or data >24 months old. \
Set value to null if confidence is low.

=== FACILITY TYPE FILTER ===
{facility_pricing_note}
If context or training data contains pricing for OTHER facility types, explicitly \
exclude it and note this in reasoning.

=== MARKET ANCHOR DATA ===

--- RACK MRC (space-only monthly charge, excluding power) ---
- JM Financial Data Centre 101 (March 2025): Mumbai Tier III retail colo space-only ₹50,000–₹75,000/rack/month
- Cushman & Wakefield India DC Market 2024: All-in tenant cost (space + power) ₹90,000–₹1,10,000/rack/month in Mumbai
- Power component at {kw_per_rack}kW: {kw_per_rack} × 730 hrs × tenant_power_rate ≈ ₹{power_component_low:,}–₹{power_component_high:,}/month
- Derivation rule: space_only_MRC = all_in_tenant_cost − power_component
- City index relative to Mumbai (Mumbai = 100): Bangalore 88, Delhi NCR 90, Hyderabad 78, Chennai 75, Pune 72
- Apply city index to derive {location}-specific rate from Mumbai anchor
- Valid range for {location}: ₹{mrc_range[0]:,} – ₹{mrc_range[1]:,}/rack/month

--- POWER TARIFF (utility grid HT commercial rate, annual blended) ---
{power_tariff_block}

--- TENANT POWER MARKUP (above utility rate, Rs/kWh) ---
- Indian DC operators (Sify, CtrlS, STT GDC) charge tenants 15–25% above utility rate
- Retail colo standard: ₹1.0–2.0/kWh (covers distribution losses, metering, billing overhead, margin)
- Wholesale/hyperscale: ₹0.5–1.0/kWh (thin margin, high volume)
- Source: Kotak / Motilal Oswal equity research on Indian DC operators (2025)
- Derivation rule:
    IF utility_tariff and markup both known → tenant_rate = utility_tariff + markup
    IF only all-in tenant_rate known → markup = tenant_rate − utility_tariff
    Validate: markup must fall in ₹0.5–5.0/kWh range

--- LAND COST (per sqft of DC building footprint, industrial-grade land) ---
- Mumbai (Navi Mumbai, Taloja, Ghansoli industrial areas): ₹6,000–₹8,000/sqft
- Bangalore (Whitefield periphery, Yelahanka, Devanahalli): ₹4,000–₹6,000/sqft
- Delhi NCR (Noida, Greater Noida industrial corridors): ₹4,000–₹5,500/sqft
- Hyderabad (HITEC corridor, Patancheru, Sultanpur): ₹2,500–₹4,000/sqft
- Chennai (Siruseri IT Park, Ambattur industrial estate): ₹2,500–₹3,500/sqft
- Pune (Kharadi, Hinjewadi periphery, Chakan): ₹3,000–₹4,500/sqft
- Source: CBRE India Industrial & Logistics Report 2024, JLL India DC Land Survey 2024
- Unit: ₹ per sqft of building footprint (NOT total plot area)

--- PUE (Power Usage Effectiveness) ---
- This is a NEW BUILD greenfield facility commissioned in {year}. Use DESIGN PUE, not national average.
- BEE India DC Study 2022: national average ~1.8; modern Tier III design target ≤1.5
- Uptime Institute Global Survey 2023: India average (all ages) 1.65–1.75
- Modern Tier III retail colo (new build 2024–26): design 1.45–1.60, apply +0.1 buffer for realized = 1.55–1.70
- Wholesale/hyperscale (optimised cooling): 1.4–1.55
- AI/HPC (liquid/immersion cooling): 1.3–1.45
- If context mentions "design PUE": add 0.05–0.10 to get realized estimate
- Source: BEE India, Uptime Institute Annual Global DC Survey 2023

--- INTEREST RATE (project finance senior secured lending rate) ---
- Borrower: {_BORROWER_CLASS}
- RBI repo rate: ~6.25% (post rate cuts, 2025–26)
- Infrastructure project finance spread: +200–400 bps above repo
- GREENFIELD / first project range: 10.0–11.0% (use this, not established operator rates)
- Established operator (CARE/ICRA rated, track record): 9.0–9.5% — DO NOT use for this project
- Source: CARE Ratings, ICRA credit reports on Sify, CtrlS, Yotta (2025)
- Tenor assumed: 10–12 years senior secured

--- CIVIL CONSTRUCTION COST (building shell + fit-out, excluding land and MEP) ---
This is the per-rack civil cost: construction of the data center building including raised floor,
false ceiling, fire suppression, access control, interiors. Does NOT include land, UPS, cooling,
network, or IT hardware.

Derivation path:
  Step 1: Identify construction cost per sqft for {location} (DC-grade air-conditioned building)
  Step 2: Multiply by effective sqft per rack = {effective_sqft_per_rack:.0f} sqft/rack
           (This is pre-computed from our model: data hall + corridors + support spaces)
  Step 3: civil_cost_cr_per_rack = construction_cost_rs_per_sqft × {effective_sqft_per_rack:.0f} / 1,00,00,000

Anchor data for {location}:
- DC-grade construction cost: ₹{construction_range[0]:,}–₹{construction_range[1]:,}/sqft
- Includes: building shell, raised floor (600mm), false ceiling, fire suppression (FM200/Novec),
  precision air-conditioning room preparation, access control cabling, interiors finishing
- Excludes: land cost, MEP equipment (UPS, cooling, DG), IT hardware, external infrastructure
- Source: CBRE India Construction Cost Guide 2024, JLL India DC Build Cost Survey 2024,
  Turner & Townsend India Construction Intelligence Report 2024
- City premium drivers for {location}: construction labor market, local regulatory compliance
  (municipal approvals), material procurement lead times, foundation requirements

Implied civil_cost_cr_per_rack range: ₹{civil_cost_low} Cr – ₹{civil_cost_high} Cr per rack
Derive a single point estimate. Prefer the midpoint unless {location} has specific cost pressures.
If confidence is medium or high, show the arithmetic explicitly in reasoning.

--- ELECTRICAL CAPEX PER MW (equipment only: UPS, batteries, DG, transformers, switchgear, cabling) ---
This is total electrical infrastructure cost per MW of IT load. Does NOT include civil, land,
mechanical cooling, or IT hardware.

Redundancy tier: Tier III N+1 (assume this unless facility_type overrides it).
- AI/HPC may require 2N for electrical: increase estimate by 25–40%.

Anchor data (JM Financial Data Centre 101, March 2025; CBRE India DC Cost Benchmarks 2024):
- Retail colo / Wholesale (N+1): ₹{elec_range[0]}–₹{elec_range[1]} Cr/MW IT load
  Components: HT panel + transformers (~15%), UPS systems (~25%), battery banks (~20%),
  DG gensets (~20%), PDUs + cabling + earthing (~20%)
- AI/HPC (higher power density, 2N considered): ₹5.0–₹8.0 Cr/MW
  Additional cost: oversized UPS frames, larger DG capacity, denser cabling infrastructure
- Note: Per MW costs decline slightly at scale (bulk procurement savings ~8–12% above 5MW)
  For {total_mw} MW facility: apply {'-8 to -12% scale discount' if total_mw > 5 else 'no scale discount (sub-5MW)'}

Derivation rule:
  electrical_capex_cr_per_mw = total electrical equipment cost / IT load in MW
  Do NOT include civil or mechanical costs in this figure.
  Cross-check: electrical should be 35–45% of total construction CapEx (excl. land, soft costs)

--- MECHANICAL CAPEX PER MW (cooling: chilled water plant, CRAC/CRAH, cooling towers, piping) ---
This is total mechanical cooling infrastructure per MW of IT load. Does NOT include civil, land,
electrical, or IT hardware.

Cooling technology assumed: {
    'Chilled water + CRAC/CRAH (standard for retail colo Tier III)'
    if facility_type in ('retail_colo', 'wholesale')
    else 'Liquid/immersion cooling + residual air cooling (AI/HPC)'
    if facility_type == 'ai_hpc'
    else 'Chilled water plant (hyperscale standardised cooling modules)'
}

Anchor data (JM Financial Data Centre 101, March 2025; CBRE India DC Cost Benchmarks 2024):
- Retail colo / Wholesale (chilled water, N+1): ₹{mech_range[0]}–₹{mech_range[1]} Cr/MW IT load
  Components: chiller plant (~35%), CRAC/CRAH units (~30%), cooling towers (~15%),
  chilled water piping + insulation (~12%), BMS integration (~8%)
- AI/HPC (liquid cooling infrastructure): ₹4.0–₹7.0 Cr/MW
  Additional cost: CDU (Coolant Distribution Units), rear-door heat exchangers,
  liquid-to-liquid heat exchangers, dedicated chilled water loop for liquid cooling
- Note: PUE of {0} affects cooling sizing — lower PUE = more efficient cooling = lower mechanical cost
  At PUE ~1.6 for Tier III: cooling handles ~37.5% of total facility load (0.6/1.6 = 37.5%)
- Climate adjustment: {location} climate impacts free-cooling hours and chiller sizing
  Mumbai (hot + humid): limited free-cooling hours → higher mechanical CapEx vs. Hyderabad

Derivation rule:
  mechanical_capex_cr_per_mw = total cooling equipment cost / IT load in MW
  Cross-check: mechanical should be 20–30% of total construction CapEx (excl. land, soft costs)

=== INTERNAL PARITY CHECK ===
After deriving all values, verify consistency:
  implied_all_in = rack_mrc + ({kw_per_rack} kW × 730 hrs × (utility_tariff + markup))

If your training knowledge or anchor data states an all-in rate for {location} {facility_type}:
  - Compare implied_all_in against stated all-in
  - If gap > ₹15,000/rack/month: explain the discrepancy in rack_mrc reasoning
  - Adjust rack_mrc or reduce confidence accordingly

=== VALIDATION RULES ===
Return null (not a guess) if value falls outside these bounds:
- rack_mrc_rs_per_month          : {mrc_range[0]:,} – {mrc_range[1]:,}
- utility_tariff_rs_per_kwh      : 5.0 – 14.0
- tenant_power_markup_rs_per_kwh : 0.5 – 5.0
- land_cost_rs_per_sqft          : 1,000 – 20,000
- pue                            : 1.2 – 2.2
- interest_rate_pct              : 7.0 – 15.0
- civil_cost_cr_per_rack         : {civil_cost_low} – {civil_cost_high}
- electrical_capex_cr_per_mw     : {elec_range[0]} – {elec_range[1]}
- mechanical_capex_cr_per_mw     : {mech_range[0]} – {mech_range[1]}

=== OUTPUT FORMAT ===
Return ONLY valid JSON. No prose, no markdown outside the JSON.

{{
  "rack_mrc_rs_per_month": {{
    "reasoning": "<anchor stated> → <derivation shown> → <point estimate>",
    "value": <number or null>,
    "confidence": "high" | "medium" | "low"
  }},
  "utility_tariff_rs_per_kwh": {{
    "reasoning": "...",
    "value": <number or null>,
    "confidence": "..."
  }},
  "tenant_power_markup_rs_per_kwh": {{
    "reasoning": "...",
    "value": <number or null>,
    "confidence": "..."
  }},
  "land_cost_rs_per_sqft": {{
    "reasoning": "...",
    "value": <number or null>,
    "confidence": "..."
  }},
  "pue": {{
    "reasoning": "...",
    "value": <number or null>,
    "confidence": "..."
  }},
  "interest_rate_pct": {{
    "reasoning": "...",
    "value": <number or null>,
    "confidence": "..."
  }},
  "civil_cost_cr_per_rack": {{
    "reasoning": "<construction cost Rs/sqft for {location}> × <{effective_sqft_per_rack:.0f} sqft/rack> / 1,00,00,000 = <value> Cr/rack",
    "value": <number or null>,
    "confidence": "..."
  }},
  "electrical_capex_cr_per_mw": {{
    "reasoning": "<component breakdown: UPS + batteries + DG + transformers + switchgear + cabling> → <total per MW>",
    "value": <number or null>,
    "confidence": "..."
  }},
  "mechanical_capex_cr_per_mw": {{
    "reasoning": "<component breakdown: chiller plant + CRAC/CRAH + cooling towers + piping + BMS> → <total per MW>",
    "value": <number or null>,
    "confidence": "..."
  }},
  "parity_check": {{
    "implied_all_in_rs_per_month": <computed number>,
    "stated_all_in_rs_per_month": <number from training data or null>,
    "gap_rs_per_month": <implied - stated or null>,
    "flag": "ok" | "reconciled" | "gap_unexplained"
  }}
}}
"""


def build_extraction_prompt(
    assumption_name,
    context
):

    assumption = (
        ASSUMPTION_DEFINITIONS[
            assumption_name
        ]
    )

    description = (
        assumption["description"]
    )

    unit = (
        assumption["unit"]
    )

    valid_range = (
        assumption["valid_range"]
    )

    return f"""
You are a financial assumptions extraction engine.

Assumption Name:
{assumption_name}

Description:
{description}

Unit:
{unit}

Expected Range:
{valid_range[0]} to {valid_range[1]}

Context:

{context}

Instructions:

1. Extract the most relevant value.
2. Convert units if necessary.
3. If no reliable value exists, return null.
4. Confidence should be between 0 and 1.
5. Return ONLY valid JSON.

Format:

{{
    "value": number_or_null,
    "confidence": number_between_0_and_1,
    "reasoning": "short explanation"
}}
"""


def build_batch_extraction_prompt(
    location,
    facility_type,
    context_text,
    assumption_names,
    kw_per_rack=None,
    total_racks=None,
    total_mw=None
):

    assumption_block = ""

    for i, name in enumerate(assumption_names, start=1):

        defn = ASSUMPTION_DEFINITIONS[name]

        assumption_block += (
            f"{i}. {name}\n"
            f"   Description : {defn['description']}\n"
            f"   Unit        : {defn['unit']}\n"
            f"   Valid range : {defn['valid_range'][0]} to {defn['valid_range'][1]}\n\n"
        )

    keys_json = (
        "{\n"
        + ",\n".join(
            f'  "{name}": {{"value": <number_or_null>, "confidence": <0.0_to_1.0>, "reasoning": "<one line>"}}'
            for name in assumption_names
        )
        + "\n}"
    )

    density_line = (
        f"Rack density   : {kw_per_rack} kW per rack "
        f"(use EXACTLY this value for any per-kW → per-rack conversions)"
        if kw_per_rack is not None
        else ""
    )

    size_line = ""
    if total_racks is not None and total_mw is not None:
        pricing_guidance = (
            "retail pricing applies (multiple tenants, ₹50k-80k/rack/month)"
            if facility_type in ("retail_colo", "retail")
            else "wholesale/single-tenant pricing applies (₹30k-45k/rack/month)"
        )
        size_line = (
            f"Facility size  : {total_racks} racks / {total_mw} MW IT load — {pricing_guidance}"
        )

    return f"""You are a financial data extraction engine for an Indian data center investment model.

Location      : {location}
Facility type : {facility_type}
{size_line}
{density_line}

---
MARKET RESEARCH CONTEXT
{context_text}
---

Extract the following assumptions from the context above.

Rules:
- All monetary values must be in Indian Rupees (INR).
- Return the value in the unit specified for each assumption.
- Confidence 1.0 = explicitly stated in context. 0.0 = not found.
- If the context contains no reliable data for an assumption, set value to null.
- Do NOT guess. Prefer null over a fabricated number.
- If the source data is in ₹/kW/month and you need ₹/rack/month, multiply by the
  rack density stated above — do NOT use values from the context or your own knowledge.
- Return ONLY valid JSON — no markdown, no explanation outside the JSON.

Assumptions to extract:

{assumption_block}
Expected output format:
{keys_json}
"""
