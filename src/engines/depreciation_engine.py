import pandas as pd


def _slm_series(capex, life_years, years):
    """Annual SLM depreciation charge for each year given phased CapEx additions."""
    dep = [0.0] * years
    annual_rate = 1.0 / life_years
    for purchase_year in range(years):
        c = capex[purchase_year]
        if c == 0:
            continue
        for future_year in range(purchase_year, years):
            dep[future_year] += c * annual_rate
    return dep


def _wdv_series(capex, wdv_rate, years):
    """Annual WDV depreciation charge (IT Act).
    Each vintage's WDV declines at (1 - rate) per year.
    """
    dep = [0.0] * years
    for purchase_year in range(years):
        c = capex[purchase_year]
        if c == 0:
            continue
        for future_year in range(purchase_year, years):
            years_elapsed = future_year - purchase_year
            wdv_opening = c * (1 - wdv_rate) ** years_elapsed
            dep[future_year] += wdv_opening * wdv_rate
    return dep


def compute_depreciation(capex_output, assumptions):

    years = len(capex_output["metadata"]["years"])
    year_labels = capex_output["metadata"]["years"]

    civil_capex       = capex_output["capex_components"]["civil_capex"]
    electrical_capex  = capex_output["capex_components"]["electrical_capex"]
    mechanical_capex  = capex_output["capex_components"]["mechanical_capex"]
    network_capex     = capex_output["capex_components"]["network_capex"]
    software_capex    = capex_output["capex_components"]["software_capex"]
    it_hardware_capex = capex_output["capex_components"]["it_hardware_capex"]

    # ----------------------------------
    # BOOK DEPRECIATION (Companies Act SLM)
    # Used for P&L / EBIT reporting.
    # ----------------------------------

    civil_dep       = _slm_series(civil_capex,       assumptions["civil_life_years"],       years)
    electrical_dep  = _slm_series(electrical_capex,  assumptions["electrical_life_years"],  years)
    mechanical_dep  = _slm_series(mechanical_capex,  assumptions["mechanical_life_years"],  years)
    network_dep     = _slm_series(network_capex,     assumptions["network_life_years"],     years)
    software_dep    = _slm_series(software_capex,    assumptions["software_life_years"],    years)
    it_dep          = _slm_series(it_hardware_capex, assumptions["it_hardware_life_years"], years)

    book_depreciation = [
        civil_dep[i] + electrical_dep[i] + mechanical_dep[i]
        + network_dep[i] + software_dep[i] + it_dep[i]
        for i in range(years)
    ]

    accumulated_depreciation = []
    running = 0.0
    for d in book_depreciation:
        running += d
        accumulated_depreciation.append(running)

    cumulative_capex = capex_output["financials"]["cumulative_capex"]
    net_book_value = [
        cumulative_capex[i] - accumulated_depreciation[i]
        for i in range(years)
    ]

    # ----------------------------------
    # TAX DEPRECIATION (IT Act WDV)
    # Used for taxable income computation only.
    # ----------------------------------

    civil_tax_dep       = _wdv_series(civil_capex,       assumptions["civil_wdv_rate"],       years)
    electrical_tax_dep  = _wdv_series(electrical_capex,  assumptions["electrical_wdv_rate"],  years)
    mechanical_tax_dep  = _wdv_series(mechanical_capex,  assumptions["mechanical_wdv_rate"],  years)
    network_tax_dep     = _wdv_series(network_capex,     assumptions["network_wdv_rate"],     years)
    software_tax_dep    = _wdv_series(software_capex,    assumptions["software_wdv_rate"],    years)
    it_tax_dep          = _wdv_series(it_hardware_capex, assumptions["it_hardware_wdv_rate"], years)

    tax_depreciation = [
        civil_tax_dep[i] + electrical_tax_dep[i] + mechanical_tax_dep[i]
        + network_tax_dep[i] + software_tax_dep[i] + it_tax_dep[i]
        for i in range(years)
    ]

    tax_wdv = []
    running_wdv = 0.0
    for i in range(years):
        running_wdv += (
            civil_capex[i] + electrical_capex[i] + mechanical_capex[i]
            + network_capex[i] + software_capex[i] + it_hardware_capex[i]
            - tax_depreciation[i]
        )
        tax_wdv.append(running_wdv)

    # ----------------------------------
    # DATAFRAMES
    # ----------------------------------

    depreciation_df = pd.DataFrame({
        "Year":                    year_labels,
        "Civil Dep (Book)":        civil_dep,
        "Electrical Dep (Book)":   electrical_dep,
        "Mechanical Dep (Book)":   mechanical_dep,
        "Network Dep (Book)":      network_dep,
        "Software Amort (Book)":   software_dep,
        "IT Dep (Book)":           it_dep,
        "Total Book Dep":          book_depreciation,
        "Accumulated Book Dep":    accumulated_depreciation,
        "Net Book Value":          net_book_value,
    })

    tax_dep_df = pd.DataFrame({
        "Year":                    year_labels,
        "Civil Dep (Tax WDV)":     civil_tax_dep,
        "Electrical Dep (Tax WDV)": electrical_tax_dep,
        "Mechanical Dep (Tax WDV)": mechanical_tax_dep,
        "Network Dep (Tax WDV)":   network_tax_dep,
        "Software Dep (Tax WDV)":  software_tax_dep,
        "IT Dep (Tax WDV)":        it_tax_dep,
        "Total Tax Dep":           tax_depreciation,
    })

    return {

        "financials": {
            # Book (SLM) — used for P&L EBIT
            "total_depreciation":      book_depreciation,   # kept for backward compat
            "book_depreciation":       book_depreciation,
            "accumulated_depreciation": accumulated_depreciation,
            "net_book_value":          net_book_value,
            # Tax (WDV) — used for taxable income
            "tax_depreciation":        tax_depreciation,
        },

        "dataframes": {
            "depreciation_df": depreciation_df,
            "tax_dep_df":      tax_dep_df,
        },

        "assumption_register": assumptions.copy(),
    }
