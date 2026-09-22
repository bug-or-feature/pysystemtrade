from syscore.dateutils import MIXED_FREQ, HOURLY_FREQ, DAILY_PRICE_FREQ
from syscore.pandas.frequency import merge_data_with_different_freq
from sysinit.futures.contract_prices_from_split_freq_csv_to_db import (
    write_prices_for_contract_at_frequency,
)
from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices
from sysproduction.data.prices import diagPrices, get_valid_instrument_code_from_user

diag_prices = diagPrices()
db_prices = diag_prices.db_futures_contract_price_data


def merge_split_freq_prices_for_code(
    instrument_code: str,
    ignore_duplication: bool = False,
    dry_run: bool = True,
):
    print(f"Merging split freq csv prices for {instrument_code}")

    print("Getting split freq prices may take some time")
    hourly_dict = db_prices.get_prices_at_frequency_for_instrument(
        instrument_code,
        frequency=HOURLY_FREQ,
    )
    daily_dict = db_prices.get_prices_at_frequency_for_instrument(
        instrument_code,
        frequency=DAILY_PRICE_FREQ,
    )
    merged_dict = db_prices.get_merged_prices_for_instrument(instrument_code)

    hourly_and_daily = sorted(hourly_dict.keys() & daily_dict.keys())
    daily_only = sorted(set(daily_dict.keys()) - set(hourly_dict.keys()))
    hourly_only = sorted(set(hourly_dict.keys()) - set(daily_dict.keys()))
    merged = sorted(merged_dict.keys())
    unmerged = sorted((hourly_dict.keys() & daily_dict.keys()) - merged_dict.keys())

    print(f"hourly_and_daily: {hourly_and_daily}")
    print(f"daily_only: {daily_only}")
    print(f"hourly_only: {hourly_only}")
    print(f"merged: {merged}")
    print(f"unmerged: {unmerged}")

    print(f"Have unmerged hourly and daily prices for: {str(unmerged)}")
    for contract_date_str in unmerged:
        print(f"Processing {contract_date_str}")

        contract = futuresContract(instrument_code, contract_date_str)
        print(f"Contract object is {str(contract)}")

        hourly = hourly_dict[contract_date_str]
        daily = daily_dict[contract_date_str]

        print(
            f"We have {len(hourly)} hourly and {len(daily)} daily lines of prices for {str(contract)}"
        )

        merged = futuresContractPrices(merge_data_with_different_freq([hourly, daily]))
        if dry_run:
            print(
                f"DRY_RUN: would write {len(merged)} lines of merged prices for {str(contract)}"
            )
        else:
            write_prices_for_contract_at_frequency(
                contract, merged, MIXED_FREQ, ignore_duplication=ignore_duplication
            )


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    instrument_code = get_valid_instrument_code_from_user(source="config")

    merge_split_freq_prices_for_code(
        instrument_code,
        dry_run=False,
    )
