def get_default_depreciation_assumptions():

    return {

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

        "salvage_value_pct": 0.0
    }