import os

from syscore.dateutils import month_from_contract_letter
from syscore.fileutils import (
    files_with_extension_in_resolved_pathname,
    get_resolved_pathname,
)
from syscore.fileutils import resolve_path_and_filename_for_package
from sysdata.config.production_config import get_production_config
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysinit.futures.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices,
    init_arctic_with_csv_futures_contract_prices_for_code,
)
from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData
from sysobjects.contracts import futuresContract

from numpy import isnan

NORGATE_CONFIG = ConfigCsvFuturesPrices(
    input_date_index_name="Date",
    input_skiprows=0,
    input_skipfooter=0,
    input_date_format="%Y%m%d",
    input_column_mapping=dict(
        OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
    ),
)

BARCHART_CONFIG = ConfigCsvFuturesPrices(
    input_date_index_name="Time",
    input_skiprows=0,
    input_skipfooter=0,
    input_date_format="%Y-%m-%dT%H:%M:%S%z",
    # input_column_mapping=dict(
    #     OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
    # )
)


def convert_norgate_to_barchart(instrument_code: str, date_str: str):
    norgate_dir = resolve_path_and_filename_for_package(
        get_production_config().get_element_or_missing_data("norgate_path")
    )
    barchart_dir = resolve_path_and_filename_for_package(
        get_production_config().get_element_or_missing_data("barchart_path")
    )
    norgate_csv_prices = csvFuturesContractPriceData(norgate_dir, config=NORGATE_CONFIG)
    barchart_csv_prices = csvFuturesContractPriceData(
        barchart_dir, config=BARCHART_CONFIG
    )

    csv_price_dict = norgate_csv_prices.get_merged_prices_for_instrument(
        instrument_code
    )
    prices_for_contract = csv_price_dict[date_str]
    prices_for_contract = prices_for_contract.shift(6, freq="H")
    prices_for_contract.index = prices_for_contract.index.tz_localize(tz="UTC")
    prices_for_contract = prices_for_contract.rename(
        columns={
            "OPEN": "Open",
            "HIGH": "High",
            "LOW": "Low",
            "FINAL": "Close",
            "VOLUME": "Volume",
        }
    )

    print("Processing %s" % date_str)
    print(".csv prices are \n %s" % str(prices_for_contract))
    contract = futuresContract.from_two_strings(instrument_code, date_str)

    print("Writing to barchart")
    barchart_csv_prices.write_merged_prices_for_contract_object(
        contract, prices_for_contract, ignore_duplication=True
    )


if __name__ == "__main__":

    # for date in ["19990200", "19990300", "19990400", "19990500", "19990600", "19990700", "19990800", "19990900",
    #               "19991000", "19991100", "19991200"]:
    # #for date in ["19990100"]:
    #     convert_norgate_to_barchart("CAC", date)

    # for year in range ["1999","2000","2001","2002","2003","2004","2005","200","2000","2000","2000",]:
    # for year in range(2002, 2015):
    #     for month in ["03", "06", "09", "12"]:
    #         month_str = f"{str(year)}{month}00"
    #         #print(month_str)
    #         convert_norgate_to_barchart("RUSSELL", month_str)

    convert_norgate_to_barchart("LUMBER", "20220900")
