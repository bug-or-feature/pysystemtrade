import sys
from syscore.genutils import true_if_answer_is_yes
from syscore.objects import arg_not_supplied
from syscore.fileutils import get_filename_for_package
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.csv.csv_fsb_contract_prices import CsvFsbContractPriceData
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysobjects.roll_calendars import rollCalendar
from sysdata.csv.csv_roll_calendars import csvRollCalendarData
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysdata.config.production_config import get_production_config
from syscore.pdutils import print_full
from sysinit.futures_spreadbet.barchart_fsb_contract_prices import build_import_config

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

    roll_parameters_object = rollparameters.get_roll_parameters(instrument_code + "_fsb")

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
            % (csv_roll_calendars.datapath, instrument_code + "_fsb")
        )
    else:
        check_happy_to_write = True

    if check_happy_to_write:
        print("Adding roll calendar")
        csv_roll_calendars.add_roll_calendar(
            instrument_code + "_fsb", roll_calendar, ignore_duplication=True
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
    instrument_code, path=arg_not_supplied
):

    rollparameters = csvRollParametersData(datapath=path)
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

    args = None
    if len(sys.argv) > 1:
        args = sys.argv[1]

    if args is not None:
        method = sys.argv[1]

    # DONE
    # 'BUXL_fsb','CAD_fsb','CRUDE_W_fsb','EUROSTX_fsb','GOLD_fsb','NASDAQ_fsb','NZD_fsb','US30_fsb'

    # to be done
    # "NIKKEI_fsb", "EUR_fsb", "GILT_fsb", "EUA_fsb"

    # AEX_fsb,ASX_fsb,CAC_fsb,DAX_fsb,DOW_fsb,FTSE100_fsb,HANG_fsb,OAT_fsb,RUSSELL_fsb,SMI_fsb,SP500_fsb,
    # AUD_fsb,CHF_fsb,DX_fsb,EURGBP_fsb,GBP_fsb,JPY_fsb,
    # BOBL_fsb,BTP_fsb,BUND_fsb,JGB_fsb,SHATZ_fsb,US2_fsb,US5_fsb,US10_fsb,USTB_fsb,
    # COCOA_LDN_fsb,COCOA_NY_fsb,COFFEE_fsb,CORN_fsb,COTTON_fsb,LEANHOG_fsb,LIVECOW_fsb,LUMBER_fsb,OATIES
    #     OJ_fsb,RICE_fsb,ROBUSTA_fsb,SOYBEAN_fsb,SOYMEAL_fsb,SOYOIL_fsb,SUGAR_fsb,SUGAR11_fsb,WHEAT_fsb,WHEAT_LDN
    # COPPER_fsb,PALLAD_fsb,PLAT_fsb,SILVER_fsb,
    # BRENT_W_fsb,GAS_US_fsb,GASOIL_fsb,GASOLINE_fsb,HEATOIL_fsb
    # EDOLLAR_fsb,EURIBOR_fsb,STERLING3_fsb,
    # VIX_fsb,V2X_fsb

    instr_code = "US30_fsb"

    prices = CsvFsbContractPriceData(
        datapath=get_filename_for_package(
            get_production_config().get_element_or_missing_data("barchart_path")
        ),
        config=build_import_config(instr_code)
    )

    if method == "build":
        build_and_write_roll_calendar(
            instrument_code=instr_code.removesuffix("_fsb"),
            output_datapath="data.futures_spreadbet.roll_calendars_csv",
            input_prices=prices,
            check_before_writing=False,
            input_config=csvRollParametersData(datapath="data.futures_spreadbet.csvconfig")
        )
    else:
        show_expected_rolls_for_config(
            instrument_code=instr_code,
            path="data.futures_spreadbet.csvconfig"
        )

    # check_saved_roll_calendar("AUD",
    #     #input_datapath='data.futures_spreadbet.roll_calendars_csv',
    #     input_datapath='sysinit.futures.tests.data.aud',
    #     input_prices=csvFuturesContractPriceData())



    #show_expected_rolls_for_config(instrument_code="CRUDE_W",path="data.futures.csvconfig", file="rollconfig.csv" )
