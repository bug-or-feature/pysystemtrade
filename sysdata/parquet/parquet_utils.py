from syscore.dateutils import MIXED_FREQ, Frequency
from syscore.fileutils import resolve_path_and_filename_for_package
from sysdata.config.production_config import get_production_config
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData
from sysdata.data_blob import dataBlob
from sysdata.parquet.parquet_futures_per_contract_prices import (
    parquetFuturesContractPriceData,
)
from sysobjects.contracts import futuresContract

BARCHART_CONFIG = ConfigCsvFuturesPrices(
    input_date_index_name="Time",
    input_skiprows=0,
    input_skipfooter=0,
    input_date_format="%Y-%m-%dT%H:%M:%S",
    input_column_mapping=dict(
        OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
    ),
)


def convert_single_contract_csv_to_parquet(
    instr_code: str,
    date_str: str,
    target_instr_code: str = None,
    frequency: Frequency = MIXED_FREQ,
):
    datapath = resolve_path_and_filename_for_package(
        get_production_config().get_element_or_default("barchart_path", None)
    )

    csv_prices = csvFuturesContractPriceData(datapath, config=BARCHART_CONFIG)

    data = dataBlob(
        log_name="CSV_to_parquet",
        keep_original_prefix=True,
    )
    data.add_class_list([parquetFuturesContractPriceData])

    futures_contract = futuresContract(instr_code, date_str)

    csv_data = csv_prices.get_prices_at_frequency_for_contract_object(
        futures_contract, frequency=frequency
    )

    if target_instr_code:
        target_contract = futuresContract(target_instr_code, date_str)
    else:
        target_contract = futures_contract

    data.parquet_futures_contract_price.write_prices_at_frequency_for_contract_object(
        futures_contract_object=target_contract,
        futures_price_data=csv_data,
        frequency=frequency,
        ignore_duplication=True,
    )

    data.log.info(f"Converted .csv of prices for {str(futures_contract)}")


if __name__ == "__main__":
    convert_single_contract_csv_to_parquet(
        "GOLD", "20231000", target_instr_code="GOLD_micro"
    )
