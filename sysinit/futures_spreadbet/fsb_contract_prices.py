from sysdata.config.production_config import get_production_config
from sysdata.data_blob import dataBlob
from syscore.fileutils import resolve_path_and_filename_for_package
from syscore.exceptions import missingInstrument
from syscore.dateutils import MIXED_FREQ, DAILY_PRICE_FREQ, HOURLY_FREQ
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices

from sysinit.futures_spreadbet.contract_prices_from_csv_to_db import (
    init_db_with_csv_futures_prices_for_code,
    init_db_with_csv_futures_prices_for_contract,
)
from sysbrokers.IG.ig_instruments_data import (
    IgFuturesInstrumentData,
    get_instrument_object_from_config,
)


def transfer_barchart_prices_to_db_single(instr, datapath, freq=MIXED_FREQ):
    init_db_with_csv_futures_prices_for_code(
        instr, datapath, csv_config=build_import_config(instr), freq=freq
    )


def transfer_barchart_prices_to_db_single_contract(
    instr, contract, datapath, freq=MIXED_FREQ
):
    init_db_with_csv_futures_prices_for_contract(
        instr,
        contract,
        datapath,
        csv_config=build_import_config(instr),
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


if __name__ == "__main__":
    # input("Will overwrite existing prices are you sure?! CTL-C to abort")
    datapath = resolve_path_and_filename_for_package(
        get_production_config().get_element_or_default("barchart_path", None)
    )

    # MIXED frequency
    # "AUDJPY"
    for instr in ["AUDJPY", "BTP3"]:
        transfer_barchart_prices_to_db_single(instr, datapath=datapath)

    # split frequencies
    # "AUDJPY"
    for instr in ["AUDJPY", "BTP3"]:
        transfer_barchart_prices_to_db_single(
            instr, datapath=datapath, freq=HOURLY_FREQ
        )
        transfer_barchart_prices_to_db_single(
            instr, datapath=datapath, freq=DAILY_PRICE_FREQ
        )

    # MIXED frequency
    # "DOW_fsb"
    # for instr in ["DOW_fsb"]:
    #     for contract in ["20080900"]:
    #         transfer_barchart_prices_to_db_single_contract(
    #             instr, contract, datapath, frequency=MIXED_FREQ
    #         )

    # split frequencies
    # "HANG_fsb"
    for instr in ["HANG_fsb"]:
        for contract in ["20221100"]:
            transfer_barchart_prices_to_db_single_contract(
                instr, contract, datapath, freq=HOURLY_FREQ
            )
            transfer_barchart_prices_to_db_single_contract(
                instr, contract, datapath, freq=DAILY_PRICE_FREQ
            )
