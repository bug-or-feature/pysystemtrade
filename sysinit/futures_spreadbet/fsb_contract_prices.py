from sysdata.config.production_config import get_production_config
from sysdata.data_blob import dataBlob
from syscore.fileutils import resolve_path_and_filename_for_package
from syscore.exceptions import missingInstrument
from syscore.dateutils import Frequency, MIXED_FREQ, DAILY_PRICE_FREQ, HOURLY_FREQ
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysinit.futures_spreadbet.contract_prices_from_csv_to_db import (
    init_db_with_csv_futures_prices_for_code,
    init_db_with_csv_futures_prices_for_contract,
)
from sysbrokers.IG.ig_instruments_data import (
    IgFuturesInstrumentData,
    get_instrument_object_from_config,
)
from sysinit.futures_spreadbet.barchart_futures_contract_prices import BARCHART_CONFIG
from syscore.constants import arg_not_supplied


def transfer_barchart_prices_to_db_single(instr, datapath, freq=MIXED_FREQ):
    init_db_with_csv_futures_prices_for_code(
        instr, datapath, csv_config=BARCHART_CONFIG, freq=freq
    )


def transfer_barchart_prices_to_db_single_contract(
    instr, contract, datapath, freq=MIXED_FREQ
):
    init_db_with_csv_futures_prices_for_contract(
        instr,
        contract,
        datapath,
        csv_config=BARCHART_CONFIG,
        freq=freq,
    )


def build_import_config(instr):
    instr_data = IgFuturesInstrumentData(None, data=dataBlob())
    try:
        config_data = get_instrument_object_from_config(instr, config=instr_data.config)
        return ConfigCsvFuturesPrices(
            input_date_index_name="Time",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y-%m-%dT%H:%M:%S%z",
            input_column_mapping=dict(
                OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
            ),
            apply_multiplier=config_data.multiplier,
            apply_inverse=config_data.inverse,
        )
    except missingInstrument:
        print(f"No config for {instr}")


def build_norgate_import_config(instr):
    instr_data = IgFuturesInstrumentData(None, data=dataBlob())
    try:
        config_data = get_instrument_object_from_config(instr, config=instr_data.config)
        return ConfigCsvFuturesPrices(
            input_date_index_name="Date",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y%m%d",  # 19810507
            input_column_mapping=dict(
                OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
            ),  # Date,Symbol,Security Name,Open,High,Low,Close,Volume
            apply_multiplier=config_data.multiplier,
            apply_inverse=config_data.inverse,
        )
    except missingInstrument:
        print(f"No config for {instr}")


def find_contracts_for_instr(
    instr_code: str,
    date_str: str,
    datapath: str,
    csv_config=arg_not_supplied,
    freq: Frequency = MIXED_FREQ,
):
    # prices = csvFuturesContractPriceData(datapath, config=csv_config)
    prices = arcticFuturesContractPriceData()
    print(f"Getting .csv prices ({freq.name})")
    csv_price_dict = prices.get_prices_at_frequency_for_instrument(instr_code, freq)
    print(f"Have .csv prices ({freq.name}) for the following contracts:")
    print(str(csv_price_dict.keys()))


if __name__ == "__main__":
    # input("Will overwrite existing prices are you sure?! CTL-C to abort")
    datapath = resolve_path_and_filename_for_package(
        get_production_config().get_element_or_default("barchart_path", None)
    )

    # find_contracts_for_instr(
    #     "HANG", None, datapath, csv_config=BARCHART_CONFIG, freq=HOURLY_FREQ
    # )

    # MIXED frequency
    # "AUDJPY"
    # for instr in ["AUDJPY", "BTP3"]:
    #     transfer_barchart_prices_to_db_single(instr, datapath=datapath)

    # split frequencies
    # "AUDJPY"
    # for instr in ["AUDJPY", "BTP3"]:
    #     transfer_barchart_prices_to_db_single(
    #         instr, datapath=datapath, freq=HOURLY_FREQ
    #     )
    #     transfer_barchart_prices_to_db_single(
    #         instr, datapath=datapath, freq=DAILY_PRICE_FREQ
    #     )

    # MIXED frequency
    # "DOW"
    # for instr in ["DOW"]:
    #     for contract in ["20080900"]:
    #         transfer_barchart_prices_to_db_single_contract(
    #             instr, contract, datapath, freq=MIXED_FREQ
    #         )

    # "DOW"
    for instr in ["HANG"]:
        for contract in ["20160700", "20160800"]:
            transfer_barchart_prices_to_db_single_contract(
                instr, contract, datapath, freq=MIXED_FREQ
            )

    # split frequencies
    # "HANG"
    for instr in ["HANG"]:
        for contract in ["20160700", "20160800", "20221100"]:
            transfer_barchart_prices_to_db_single_contract(
                instr, contract, datapath, freq=HOURLY_FREQ
            )
            transfer_barchart_prices_to_db_single_contract(
                instr, contract, datapath, freq=DAILY_PRICE_FREQ
            )
