from sysdata.config.production_config import get_production_config
from syscore.fileutils import get_filename_for_package
from syscore.objects import missing_instrument
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices

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
        instr, datapath, csv_config=build_import_config(instr)
    )


def transfer_barchart_prices_to_arctic_single_contract(instr, contract, datapath):
    init_arctic_with_csv_futures_contract_prices_for_contract(
        instr, contract, datapath, csv_config=build_import_config(instr)
    )


def build_import_config(instr):
    instr_data = IgFuturesInstrumentData()
    config_data = get_instrument_object_from_config(instr, config=instr_data.config)
    if config_data is missing_instrument:
        print(f"No config for {instr}")
    else:
        return ConfigCsvFuturesPrices(
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

def build_norgate_import_config(instr):
    instr_data = IgFuturesInstrumentData()
    config_data = get_instrument_object_from_config(instr, config=instr_data.config)
    if config_data is missing_instrument:
        print(f"No config for {instr}")
    else:
        return ConfigCsvFuturesPrices(
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
    #input("Will overwrite existing prices are you sure?! CTL-C to abort")
    datapath = get_filename_for_package(
        get_production_config().get_element_or_missing_data("barchart_path")
    )

    # XXX
    # ['RICE', 'ROBUSTA', 'XX', 'XX', 'XX']
    for instr in ['ROBUSTA']:
        transfer_barchart_prices_to_arctic_single(instr, datapath=datapath)


    # transfer_barchart_prices_to_arctic_single_contract(instr, contract_date, datapath)
