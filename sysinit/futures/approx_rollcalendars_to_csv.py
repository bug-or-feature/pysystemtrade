from syscore.constants import arg_not_supplied
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysobjects.roll_calendars import rollCalendar
from sysproduction.data.prices import get_valid_instrument_code_from_user, diagPrices

"""
Generate a 'best guess' roll calendar based on some price data for individual contracts
"""


def show_expected_rolls_for_config(
    instrument_code,
    path=arg_not_supplied,
    input_prices=arg_not_supplied,
):
    diag_prices = diagPrices()
    rollparameters = csvRollParametersData(datapath=path)
    roll_parameters_object = rollparameters.get_roll_parameters(instrument_code)
    if input_prices is arg_not_supplied:
        prices = diag_prices.db_futures_contract_price_data
    else:
        prices = input_prices

    dict_of_all_futures_contract_prices = prices.get_merged_prices_for_instrument(
        instrument_code
    )
    dict_of_futures_contract_prices = dict_of_all_futures_contract_prices.final_prices()
    approx_roll_calendar = rollCalendar.create_approx_from_prices(
        dict_of_futures_contract_prices, roll_parameters_object
    )

    print(f"Approx roll calendar for: {instrument_code}")
    print(approx_roll_calendar.tail(30))


if __name__ == "__main__":
    # instr_code = get_valid_instrument_code_from_user()
    instr_code = "LEANHOG"

    show_expected_rolls_for_config(
        instrument_code=instr_code,
        path="data.futures.csvconfig",
    )
