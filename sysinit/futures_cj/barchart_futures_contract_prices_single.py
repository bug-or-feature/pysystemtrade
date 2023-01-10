from sysdata.config.production_config import get_production_config
from syscore.fileutils import get_filename_for_package
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices_for_code,
)


def transfer_barchart_prices_to_arctic_single(instr, datapath):
    init_arctic_with_csv_futures_contract_prices_for_code(
        instr,
        datapath,
        csv_config=ConfigCsvFuturesPrices(
            input_date_index_name="Time",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y-%m-%dT%H:%M:%S%z",
            input_column_mapping=dict(
                OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
            ),
        ),
    )


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    datapath = get_filename_for_package(
        get_production_config().get_element_or_missing_data("barchart_path")
    )

    for instr in ["SP500"]:
        transfer_barchart_prices_to_arctic_single(instr, datapath=datapath)
