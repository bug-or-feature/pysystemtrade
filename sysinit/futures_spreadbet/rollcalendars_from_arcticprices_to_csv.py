from syscore.genutils import true_if_answer_is_yes
from syscore.objects import arg_not_supplied

from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysobjects.roll_calendars import rollCalendar
from sysdata.csv.csv_roll_calendars import csvRollCalendarData
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysproduction.data.prices import get_valid_instrument_code_from_user
from syscore.pdutils import print_full

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


def show_expected_rolls_for_config(
    instrument_code, path=arg_not_supplied, file=arg_not_supplied
):

    rollparameters = csvRollParametersData(datapath=path, filename=file)
    roll_parameters_object = rollparameters.get_roll_parameters(instrument_code)
    prices = arcticFuturesContractPriceData()
    dict_of_all_futures_contract_prices = prices.get_all_prices_for_instrument(
        instrument_code
    )
    dict_of_futures_contract_prices = dict_of_all_futures_contract_prices.final_prices()
    approx_roll_calendar = rollCalendar.create_approx_from_prices(
        dict_of_futures_contract_prices, roll_parameters_object
    )

    print(f"Approx roll calendar for: {instrument_code}")
    print_full(approx_roll_calendar.tail(20))


if __name__ == "__main__":
    # input("Will overwrite existing prices are you sure?! CTL-C to abort")
    # instrument_code = get_valid_instrument_code_from_user(source='single')

    # MODIFY DATAPATH IF REQUIRED
    # instrument_code = 'CAD_fsb' x
    # instrument_code = 'CRUDE_W_fsb' x
    # instrument_code = 'DAX_fsb' x
    # instrument_code = 'GILT_fsb' x
    # instrument_code = 'NASDAQ_fsb' x
    # instrument_code = 'NIKKEI_fsb' x
    # instrument_code = 'NZD_fsb' x
    #instrument_code = 'US30_fsb' x
    instrument_code = 'SOYOIL_fsb' # needs more data

    build_and_write_roll_calendar(
         instrument_code,
         output_datapath='/Users/ageach/Dev/work/pysystemtrade3/data/futures_spreadbet/roll_calendars_csv')

    # check_saved_roll_calendar("AUD",
    #     #input_datapath='/Users/ageach/Dev/work/pysystemtrade3/data/futures_bc/roll_calendars_csv',
    #     input_datapath='sysinit.futures.tests.data.aud',
    #     input_prices=csvFuturesContractPriceData())

    # !!! change update_all() and lt_costs() !!!

    # need further downloads due to missing data
    # SUGAR

    # need to redownload
    # SUGAR_LDN

    # No september contracts available on BC since 2005
    # WHEAT_LDN

    #show_expected_rolls_for_config(instrument_code="US30_fsb",path="data.futures_spreadbet.csvconfig", file="fsb_roll_config.csv" )
    #show_expected_rolls_for_config(instrument_code="CRUDE_W",path="data.futures.csvconfig", file="rollconfig.csv" )
