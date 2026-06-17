import os
os.environ['PYTHONPATH'] = '.'

from assumptions.revenue_defaults import get_default_revenue_assumptions
from assumptions.capex_defaults import get_default_capex_assumptions
from assumptions.opex_defaults import get_default_opex_assumptions
from assumptions.depreciation_defaults import get_default_depreciation_assumptions
from assumptions.loan_defaults import get_default_loan_assumptions
from assumptions.tax_defaults import get_default_tax_assumptions
from assumptions.working_capital_defaults import get_default_working_capital_assumptions

from src.engines.revenue_engine import compute_revenue
from src.engines.capex_engine import compute_capex
from src.engines.opex_engine import compute_opex
from src.engines.depreciation_engine import compute_depreciation
from src.engines.loan_engine import compute_loan
from src.engines.tax_engine import compute_tax
from src.engines.working_capital_engine import compute_working_capital
from src.engines.cashflow_engine import compute_cashflow

user_inputs = {
    'location': 'Mumbai',
    'total_racks': 1000,
    'facility_type': 'wholesale',
    'projection_years': 10,
}

revenue_output = compute_revenue(user_inputs, get_default_revenue_assumptions())
capex_output = compute_capex(user_inputs, get_default_capex_assumptions())
opex_output = compute_opex(revenue_output, capex_output, get_default_opex_assumptions())
depreciation_output = compute_depreciation(capex_output, get_default_depreciation_assumptions())
loan_output = compute_loan(capex_output, get_default_loan_assumptions())
tax_output = compute_tax(opex_output, depreciation_output, loan_output, get_default_tax_assumptions())
working_capital_output = compute_working_capital(revenue_output, get_default_working_capital_assumptions())
cashflow_output = compute_cashflow(opex_output, capex_output, depreciation_output, loan_output, tax_output, working_capital_output)

# Q1 interest by tranche for all years
tranche_interests = []
for tranche in loan_output['tranches']:
    tranche_interests.append(tranche['interest_payment'])

print('TRANCHE INTERESTS:')
for idx, ints in enumerate(tranche_interests, start=1):
    print(f'tranche_{idx}_interest = {[round(x,6) for x in ints]}')
print('total_interest =', [round(sum(tranche_interests[j][i] for j in range(len(tranche_interests))),6) for i in range(len(tranche_interests[0]))])

# Q2 debt service components
opening = loan_output['long_term_debt_account']['opening_balance']
drawdown = loan_output['long_term_debt_account']['drawdown']
interest = loan_output['long_term_debt_account']['interest_expense']
principal = loan_output['long_term_debt_account']['principal_repayment']
fees = [0]*len(opening)
print('\nDEBT SERVICE COMPONENTS:')
print('interest =', [round(x,6) for x in interest])
print('principal =', [round(x,6) for x in principal])
print('fees =', fees)
print('total_debt_service =', [round(interest[i]+principal[i]+fees[i],6) for i in range(len(opening))])

# Q3 interest base formula
print('\nINTEREST FORMULA: interest_payment[yr] = outstanding * interest_rate')
print('Outstanding year 0 for tranche 1:', loan_output['tranches'][0]['opening_balance'][0])
print('Loan amount tranche 1:', loan_output['tranches'][0]['loan_amount'])
print('Interest rate:', get_default_loan_assumptions()['interest_rate'])
print('Expected Year 1 interest = loan_amount * rate =', round(loan_output['tranches'][0]['loan_amount'] * get_default_loan_assumptions()['interest_rate'],6))
print('Actual Year 1 interest tranche 1:', round(loan_output['tranches'][0]['interest_payment'][0],6))

# Q4 draw_year semantics and repayment start
for idx, tranche in enumerate(loan_output['tranches'], start=1):
    print(f'\ntranche {idx}: draw_year={tranche["draw_year"]}, loan_amount={tranche["loan_amount"]}')
print('\nIn current model, draw_year is the same year revenue starts for that phase and draws occur in the same year as ramp/revenue.')
print('Phase 1 has revenue in year 0, so draw_year=0 behaves as the first operational year, not a pure pre-revenue construction year.')
print('Therefore the moratorium logic currently delays principal until year 2 (payment starts in year 2 index, year 3 of model) giving two interest-only years: year 0 and year 1.')

# Q5 phase capex and debt sanity
assumptions = get_default_loan_assumptions()
debt_pct = assumptions['debt_pct']
interest_rate = assumptions['interest_rate']
print('\nPHASE SANITY:')
for idx, tranche in enumerate(loan_output['tranches'], start=1):
    phase_year = tranche['draw_year']
    phase_capex = capex_output['financials']['total_capex'][phase_year]
    loan_amount = tranche['loan_amount']
    print(f'phase {idx} | year {phase_year} | racks {capex_output["drivers"]["racks_deployed"][phase_year]} | total_capex_for_phase {phase_capex} | debt_pct {debt_pct} | loan_amount {loan_amount} | annual_interest_at_10pct {round(loan_amount*interest_rate,6)}')
required_debt_pct = 5.57 / (capex_output['financials']['total_capex'][0] * interest_rate)
print('required debt_pct for Year 1 DSCR 1.20 =', required_debt_pct)

# Q6 tenure impact on Year 1 (same due to moratorium)
print('\nTENURE IMPACT:')
for tenure in [7,10]:
    annual_principal = loan_output['tranches'][0]['loan_amount'] / tenure
    repayment_start = loan_output['tranches'][0]['draw_year'] + assumptions['moratorium_years'] + 1
    principal_year0 = loan_output['tranches'][0]['principal_payment'][0]
    interest_year0 = loan_output['tranches'][0]['interest_payment'][0]
    total_ds = interest_year0 + principal_year0
    print(f'tenure {tenure}: Year 1 debt service = {round(total_ds,6)} (principal {principal_year0}, interest {round(interest_year0,6)})')

# Q7 full table
print('\nFULL DEBT SERVICE TABLE:')
print('Year | Opening_Debt | Drawdown | Interest | Principal | Closing_Debt | Debt_Service | CFADS | DSCR')
for i in range(len(opening)):
    opening_i = opening[i]
    draw_i = drawdown[i]
    int_i = interest[i]
    prin_i = principal[i]
    close_i = loan_output['long_term_debt_account']['closing_balance'][i]
    ds_i = int_i + prin_i
    cfads_i = cashflow_output['financials']['cfads'][i]
    dscr_i = cashflow_output['financials']['dscr'][i]
    print(f'{i} | {round(opening_i,6)} | {round(draw_i,6)} | {round(int_i,6)} | {round(prin_i,6)} | {round(close_i,6)} | {round(ds_i,6)} | {round(cfads_i,6)} | {round(dscr_i,6)}')
