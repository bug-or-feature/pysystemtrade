import datetime

import pandas as pd

from syscore.objects import arg_not_supplied
from syscore.text import remove_suffix
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData
from sysdata.csv.csv_multiple_prices import csvFuturesMultiplePricesData
from sysdata.csv.csv_roll_calendars import csvRollCalendarData
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysinit.futures.build_roll_calendars import adjust_to_price_series
from sysobjects.contract_dates_and_expiries import contractDate
from sysobjects.dict_of_futures_per_contract_prices import (
    dictFuturesContractFinalPrices,
)
from sysobjects.multiple_prices import futuresMultiplePrices
from sysobjects.rolls import rollParameters, contractDateWithRollParameters

"""
We create multiple prices using:

- roll calendars, stored in csv
- individual fsb contract prices, stored in csv

We then store those multiple prices in: (depending on options)

- arctic
- csv
"""
def _get_data_inputs(csv_roll_data_path, csv_multiple_data_path):
    roll_calendars = csvRollCalendarData(csv_roll_data_path)
    contract_prices = arcticFuturesContractPriceData()
    arctic_multiple_prices = arcticFuturesMultiplePricesData()
    csv_multiple_prices = csvFuturesMultiplePricesData(csv_multiple_data_path)

    return (
        roll_calendars,
        contract_prices,
        arctic_multiple_prices,
        csv_multiple_prices,
    )


def process_multiple_prices_all_instruments(
    csv_multiple_data_path=arg_not_supplied,
    csv_roll_data_path=arg_not_supplied,
    ADD_TO_ARCTIC=True,
    ADD_TO_CSV=True,
):

    (
        _not_used1,
        arctic_individual_futures_prices,
        _not_used2,
        _not_used3,
    ) = _get_data_inputs(csv_roll_data_path, csv_multiple_data_path)
    instrument_list = (
        arctic_individual_futures_prices.get_list_of_instrument_codes_with_merged_price_data()
    )

    for instrument_code in instrument_list:
        print(instrument_code)
        process_multiple_prices_single_instrument(
            instrument_code,
            csv_multiple_data_path=csv_multiple_data_path,
            csv_roll_data_path=csv_roll_data_path,
            ADD_TO_ARCTIC=ADD_TO_ARCTIC,
            ADD_TO_CSV=ADD_TO_CSV,
        )


def process_multiple_prices_single_instrument(
    instrument_code,
    adjust_calendar_to_prices=True,
    csv_multiple_data_path=arg_not_supplied,
    csv_roll_data_path=arg_not_supplied,
    ADD_TO_ARCTIC=True,
    ADD_TO_CSV=True,
):

    (
        roll_calendars,
        contract_prices,
        arctic_multiple_prices,
        csv_multiple_prices,
    ) = _get_data_inputs(
        csv_roll_data_path,
        csv_multiple_data_path
    )

    print(f"Generating multiple prices for {instrument_code}")
    dict_of_futures_contract_prices = contract_prices.get_merged_prices_for_instrument(
        instrument_code
    )
    dict_of_futures_contract_closing_prices = (
        dict_of_futures_contract_prices.final_prices()
    )

    roll_calendar = roll_calendars.get_roll_calendar(instrument_code)

    # Add first phantom row so that the last calendar entry won't be consumed by adjust_roll_calendar()
    #m = mongoRollParametersData()
    roll_config = csvRollParametersData(datapath="data.futures_spreadbet.csvconfig")
    roll_parameters = roll_config.get_roll_parameters(instrument_code)
    print(f"{instrument_code}: {roll_parameters}")
    roll_calendar = add_phantom_row(
        roll_calendar, dict_of_futures_contract_closing_prices, roll_parameters
    )

    if adjust_calendar_to_prices:
        roll_calendar = adjust_roll_calendar(instrument_code,
            roll_calendar,
            contract_prices
        )

    # Second phantom row is needed in order to process the whole set of closing prices (and not stop after the last roll-over)
    roll_calendar = add_phantom_row(
        roll_calendar, dict_of_futures_contract_closing_prices, roll_parameters
    )

    multiple_prices = futuresMultiplePrices.create_from_raw_data(
        roll_calendar, dict_of_futures_contract_closing_prices
    )

    print(multiple_prices)

    if ADD_TO_ARCTIC:
        arctic_multiple_prices.add_multiple_prices(
            instrument_code, multiple_prices, ignore_duplication=True
        )
    if ADD_TO_CSV:
        csv_multiple_prices.add_multiple_prices(
            instrument_code, multiple_prices, ignore_duplication=True
        )

    return multiple_prices


def adjust_roll_calendar(instrument_code, roll_calendar, prices):
    print(f"Getting prices for '{instrument_code}' to adjust roll calendar")
    dict_of_prices = prices.get_merged_prices_for_instrument(
        remove_suffix(instrument_code, "_fsb")
    )
    dict_of_futures_contract_prices = dict_of_prices.final_prices()
    roll_calendar = adjust_to_price_series(
        roll_calendar, dict_of_futures_contract_prices
    )

    return roll_calendar


def add_phantom_row(
    roll_calendar,
    dict_of_futures_contract_prices: dictFuturesContractFinalPrices,
    roll_parameters: rollParameters,
):
    final_row = roll_calendar.iloc[-1]
    if datetime.datetime.now() < final_row.name:
        return roll_calendar
    virtual_datetime = datetime.datetime.now() + datetime.timedelta(days=5)
    current_contract_date_str = str(final_row.next_contract)
    current_contract = contractDateWithRollParameters(
        contractDate(current_contract_date_str), roll_parameters
    )
    next_contract = current_contract.next_held_contract()
    carry_contract = current_contract.carry_contract()

    list_of_contract_names = dict_of_futures_contract_prices.keys()
    try:
        assert current_contract.date_str in list_of_contract_names
    except:
        print("Can't add extra row as data missing")
        return roll_calendar

    new_row = pd.DataFrame(
        dict(
            current_contract=current_contract_date_str,
            next_contract=next_contract.date_str,
            carry_contract=carry_contract.date_str,
        ),
        index=[virtual_datetime],
    )

    roll_calendar = pd.concat([roll_calendar, new_row], axis=0)

    return roll_calendar


if __name__ == "__main__":
    #input("Will overwrite existing prices are you sure?! CTL-C to abort")

    # change if you want to write elsewhere
    csv_multiple_data_path = "data.futures_spreadbet.multiple_prices_csv"

    # only change if you have written the files elsewhere
    csv_roll_data_path = "data.futures_spreadbet.roll_calendars_csv"

    for instrument_code in ['COCOA_fsb', 'CORN_fsb', 'COTTON2_fsb', 'GASOIL_fsb']:
        process_multiple_prices_single_instrument(
            instrument_code=instrument_code,
            adjust_calendar_to_prices=True,
            csv_multiple_data_path=csv_multiple_data_path,
            csv_roll_data_path=csv_roll_data_path,
            ADD_TO_ARCTIC=True,
            ADD_TO_CSV=True,
        )
