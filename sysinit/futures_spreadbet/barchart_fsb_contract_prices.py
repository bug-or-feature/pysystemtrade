from sysdata.config.production_config import get_production_config
from syscore.fileutils import get_filename_for_package
from sysdata.csv.csv_fsb_contract_prices import ConfigCsvFsbPrices
from sysinit.futures_spreadbet.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices_for_code,
    init_arctic_with_csv_futures_contract_prices_for_contract,
)
from sysbrokers.IG.ig_instruments_data import (
    IgFuturesInstrumentData,
    get_instrument_object_from_config
)




def transfer_barchart_prices_to_arctic_single(instr, datapath):

    init_arctic_with_csv_futures_contract_prices_for_code(
        instr, datapath, csv_config=build_import_config(instr, )
    )


def transfer_barchart_prices_to_arctic_single_contract(instr, contract, datapath):
    init_arctic_with_csv_futures_contract_prices_for_contract(
        instr, contract, datapath, csv_config=build_import_config(instr)
    )


def build_import_config(instr):
    instr_data = IgFuturesInstrumentData()
    config_data = get_instrument_object_from_config(instr, config=instr_data.config)
    return ConfigCsvFsbPrices(
        input_date_index_name="Time",
        input_skiprows=0,
        input_skipfooter=0,
        input_date_format="%Y-%m-%dT%H:%M:%S%z",
        input_column_mapping=dict(
            OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
        ),
        apply_multiplier=config_data.multiplier,
        apply_inverse=config_data.inverse
    )


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    datapath = get_filename_for_package(
        get_production_config().get_element_or_missing_data("barchart_path")
    )

    for instr in ["BUXL"]:
        transfer_barchart_prices_to_arctic_single(instr, datapath=datapath)

    # for instr in ["US30", "USTB", "EURIBOR", "STERLING3", "EURGBP", "JGB", "CAD", "CHF", "DOLLAR", "BRENT_W", "GASOLINE", "HEATOIL", "GASOIL_LDN"]:
    #    for contract_date in ['20200300', '20200600', '20200900', '20201200', '20210300', '20210600', '20210900', '20211200']:
    #        transfer_barchart_prices_to_arctic_single_contract(instr, contract_date, datapath)

    # for contract_date in ['DAX.20201200', 'DAX.20210300', 'DAX.20210600', 'DAX.20210900', 'DAX.20211200']:
    # for contract_date in ['20200100', '20200200', '20200300', '20200400','20200500', '20200600', '20200700', '20200800','20200900', '20201000', '20201100', '20201200','20210100', '20210200', '20210300', '20210400','20210500', '20210600', '20210700', '20210800','20210900', '20211000', '20211100', '20211200']:
    # for contract in ['DAX.20210600', 'DAX.20210900', 'DAX.20211200']:
    #instr = "SUGAR_LDN"
    # years = ["2020","2021","2022"]
    # months = ["01","03","05","07","08","09","10","12"]
    # for contract_date in ['20200900','20201200','20210300','20210500','20210700','20210900','20211200','20220300','20220500','20220700','20220900','20221200']:
    # for contract_date in ['20210300', '20210500', '20210700', '20210900', '20211100',   '20210300', '20210500', '20210700', '20210900', '20211100',]:
    # for contract_date in ["19950800"]:
    #     transfer_barchart_prices_to_arctic_single_contract(
    #         instr, contract_date, datapath
    #     )
    # for year in years:
    #     for month in months:
    #         contract_date = f"{year}{month}00"
    #         print(f"code: {contract_date}")

    # for contract_date in ['20080800']:
    # transfer_barchart_prices_to_arctic_single_contract(instr, contract_date, datapath)
