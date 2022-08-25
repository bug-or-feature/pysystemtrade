from syscore.interactive import true_if_answer_is_yes
from syscore.objects import arg_not_supplied

from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysobjects.roll_calendars import rollCalendar
from sysdata.csv.csv_roll_calendars import csvRollCalendarData
from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData
from syscore.fileutils import get_filename_for_package
from sysdata.config.production_config import get_production_config
from sysinit.futures_ag.barchart_futures_contract_prices import BARCHART_CONFIG

"""
Generate a 'best guess' roll calendar based on some price data for individual contracts

"""



def build_and_write_roll_calendar(
    instrument_code,
    output_datapath=arg_not_supplied,
    check_before_writing=True,
    input_prices=arg_not_supplied,
    input_config=arg_not_supplied,
):

    if output_datapath is arg_not_supplied:
        print(
            "*** WARNING *** This will overwrite the provided roll calendar. Might be better to use a temporary directory!"
        )
    else:
        print("Writing to %s" % output_datapath)

    if input_prices is arg_not_supplied:
        prices = arcticFuturesContractPriceData()
    else:
        prices = input_prices

    if input_config is arg_not_supplied:
        rollparameters = mongoRollParametersData()
    else:
        rollparameters = input_config

    csv_roll_calendars = csvRollCalendarData(output_datapath)

    dict_of_all_futures_contract_prices = prices.get_all_prices_for_instrument(
        instrument_code
    )
    dict_of_futures_contract_prices = dict_of_all_futures_contract_prices.final_prices()

    roll_parameters_object = rollparameters.get_roll_parameters(instrument_code)

    # might take a few seconds
    print("Prepping roll calendar... might take a few seconds")
    roll_calendar = rollCalendar.create_from_prices(
        dict_of_futures_contract_prices, roll_parameters_object
    )

    # checks - this might fail
    roll_calendar.check_if_date_index_monotonic()

    # this should never fail
    roll_calendar.check_dates_are_valid_for_prices(dict_of_futures_contract_prices)

    # Write to csv
    # Will not work if an existing calendar exists

    if check_before_writing:
        check_happy_to_write = true_if_answer_is_yes(
            "Are you ok to write this csv to path %s/%s.csv? [might be worth writing and hacking manually]?"
            % (csv_roll_calendars.datapath, instrument_code)
        )
    else:
        check_happy_to_write = True

    if check_happy_to_write:
        print("Adding roll calendar")
        csv_roll_calendars.add_roll_calendar(
            instrument_code, roll_calendar, ignore_duplication=True
        )
    else:
        print("Not writing")

    return roll_calendar


def check_saved_roll_calendar(
    instrument_code, input_datapath=arg_not_supplied, input_prices=arg_not_supplied
):

    if input_datapath is None:
        print(
            "This will check the roll calendar in the default directory : are you are that's what you want to do?"
        )

    csv_roll_calendars = csvRollCalendarData(input_datapath)

    roll_calendar = csv_roll_calendars.get_roll_calendar(instrument_code)

    if input_prices is arg_not_supplied:
        prices = arcticFuturesContractPriceData()
    else:
        prices = input_prices

    dict_of_all_futures_contract_prices = prices.get_all_prices_for_instrument(
        instrument_code
    )
    dict_of_futures_contract_prices = dict_of_all_futures_contract_prices.final_prices()

    print(roll_calendar)

    # checks - this might fail
    roll_calendar.check_if_date_index_monotonic()

    # this should never fail
    roll_calendar.check_dates_are_valid_for_prices(dict_of_futures_contract_prices)

    return roll_calendar


if __name__ == "__main__":

    #input("Will overwrite existing prices are you sure?! CTL-C to abort")

    # ['BUXL', 'GOLD', 'NASDAQ', 'NZD', 'US10']

    # ['ASX', 'BTP', 'CAD', 'COFFEE', 'COPPER', 'CRUDE_W', 'DOW', 'DX', 'EUA', 'EUROSTX', 'EUR', 'GAS_US',
    # 'GBP', 'GILT', 'HANG', 'JGB', 'JPY', 'NIKKEI', 'SILVER', 'SOYBEAN', 'SOYOIL', 'V2X', 'VIX', 'WHEAT']

    # ['AEX', 'AUD', 'CAC', 'CHF', 'DAX', 'EURGBP', 'FTSE100', 'IBXEX', 'JSE40', 'MSCISING', 'RUSSELL', 'SMI', 'SP500', 'SWE30']
    # TODO: EURGBP, JSE40, SWE30

    # ['BOBL', 'BUND', 'EDOLLAR', 'OAT', 'SHATZ', 'US5', 'US30', 'US30U']

    instrument_code = 'FED'
    # TODO: ['EURIBOR', 'FED', 'SONIA3']

    build_and_write_roll_calendar(
        instrument_code=instrument_code,
        output_datapath="data.futures_ag.roll_calendars_csv",
        input_prices=csvFuturesContractPriceData(
            datapath=get_filename_for_package(
                get_production_config().get_element_or_missing_data("barchart_path")
            ),
            config=BARCHART_CONFIG
        ),
        check_before_writing=False,
    )
