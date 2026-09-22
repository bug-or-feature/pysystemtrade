from sysproduction.data.prices import get_valid_instrument_code_from_user
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysobjects.roll_calendars import rollCalendar
from sysproduction.data.prices import diagPrices


def show_expected_rolls_for_config(instrument_code):
    rollparameters = csvRollParametersData()
    roll_parameters_object = rollparameters.get_roll_parameters(instrument_code)
    diag_prices = diagPrices()
    prices = diag_prices.db_futures_contract_price_data

    dict_of_all_futures_contract_prices = prices.get_merged_prices_for_instrument(
        instrument_code
    )
    dict_of_futures_contract_prices = dict_of_all_futures_contract_prices.final_prices()
    rollCalendar.create_approx_from_prices(
        dict_of_futures_contract_prices, roll_parameters_object
    )


if __name__ == "__main__":
    instrument_code = get_valid_instrument_code_from_user(source="config")
    show_expected_rolls_for_config(
        instrument_code=instrument_code,
    )
