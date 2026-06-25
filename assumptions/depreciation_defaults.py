def get_default_depreciation_assumptions():

    return {

        # ==========================================
        # CONSTRUCTION PERIOD
        # ==========================================

        "construction_years": 1,

        # ==========================================
        # ASSET LIVES (YEARS)
        # ==========================================

        "civil_life_years": 30,

        "electrical_life_years": 15,

        "mechanical_life_years": 15,

        "network_life_years": 7,

        "software_life_years": 5,

        "it_hardware_life_years": 5,

        # ==========================================
        # DEPRECIATION METHOD
        # ==========================================

        "depreciation_method": "straight_line",

        # ==========================================
        # SALVAGE VALUE
        # ==========================================

        "salvage_value_pct": 0.0,

        # ==========================================
        # IT ACT WDV RATES (Income Tax Act, 1961)
        # Used for taxable income computation only.
        # Higher than SLM in early years → lower tax.
        # ==========================================

        # Section 32: Building (not residential) → 10% WDV
        "civil_wdv_rate": 0.10,

        # Plant & Machinery → 15% WDV
        "electrical_wdv_rate": 0.15,
        "mechanical_wdv_rate": 0.15,

        # Computers & peripherals → 40% WDV
        "network_wdv_rate": 0.40,
        "it_hardware_wdv_rate": 0.40,

        # Computer software (intangible) → 25% WDV
        "software_wdv_rate": 0.25,
    }