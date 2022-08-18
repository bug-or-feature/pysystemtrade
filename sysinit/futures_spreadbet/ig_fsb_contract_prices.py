from sysdata.config.production_config import get_production_config
from syscore.fileutils import get_filename_for_package
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures_spreadbet.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_fsb_contract_prices_for_code,
    init_arctic_with_csv_fsb_contract_prices
)

"""
Import IG FSB contract price CSV files into system 
"""

def transfer_ig_prices_to_arctic_single(instr, datapath):
    init_arctic_with_csv_fsb_contract_prices_for_code(
        instr,
        datapath,
        # csv_config=ConfigCsvFuturesPrices(
        #     input_date_index_name="Date",
        #     input_skiprows=0,
        #     input_skipfooter=0,
        #     input_date_format="%Y-%m-%dT%H:%M:%S%z",
        # )
        csv_config = ConfigCsvFuturesPrices(
            input_date_index_name="DATETIME",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y-%m-%d %H:%M:%S",
        )
    )


def transfer_ig_prices_to_arctic(datapath):
    init_arctic_with_csv_fsb_contract_prices(
        datapath, csv_config=ConfigCsvFuturesPrices(
            input_date_index_name="Date",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y-%m-%dT%H:%M:%S%z",
        )
    )


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    #datapath = get_filename_for_package(get_production_config().get_element_or_missing_data("ig_path"))
    prod_backup = get_filename_for_package(get_production_config().get_element_or_missing_data('prod_backup'))
    datapath = f"{prod_backup}/fsb_contract_prices"


    # single instrument
    # for instr in ["GOLD_fsb"]:
    #for instr in ['BUXL_fsb', 'GOLD_fsb', 'NASDAQ_fsb', 'NZD_fsb', 'US10_fsb']:
    for instr in ['ASX_fsb', 'BTP_fsb', 'CAD_fsb', 'COFFEE_fsb', 'COPPER_fsb', 'CRUDE_W_fsb', 'DOW_fsb', 'DX_fsb',
                  'EUA_fsb', 'EUROSTX_fsb', 'EUR_fsb', 'GAS_US_fsb', 'GBP_fsb', 'GILT_fsb', 'HANG_fsb', 'JGB_fsb',
                  'JPY_fsb', 'NIKKEI_fsb', 'SILVER_fsb', 'SOYBEAN_fsb', 'SOYOIL_fsb', 'US2_fsb', 'V2X_fsb', 'WHEAT_fsb']:
        transfer_ig_prices_to_arctic_single(instr, datapath=datapath)

    # all instruments
    # transfer_ig_prices_to_arctic(datapath)