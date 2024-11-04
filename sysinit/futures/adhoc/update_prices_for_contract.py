import pandas as pd

from syscore.interactive.date_input import get_datetime_input
from sysdata.data_blob import dataBlob
from sysobjects.contracts import futuresContract
from sysproduction.data.contracts import (
    get_valid_instrument_code_and_contractid_from_user,
)
from sysproduction.data.prices import diagPrices, updatePrices


def update_prices_for_contract():
    with dataBlob(log_name="Update-Prices-For-Contract") as data:
        diag_prices = diagPrices(data)
        update_prices = updatePrices(data)
        (
            instr_code,
            contract_date_yyyy_mm,
        ) = get_valid_instrument_code_and_contractid_from_user(
            data, only_include_priced_contracts=True
        )
        contract = futuresContract(
            instrument_object=instr_code, contract_date_object=contract_date_yyyy_mm
        )
        print(f"Contract: {contract}")

        price_df = diag_prices.get_merged_prices_for_contract_object(contract)
        print(f"Existing prices:\n{price_df}")

        new_date = get_datetime_input(
            "New row date?\n",
            allow_default_datetime_of_now=False,
            allow_calendar_days=False,
            allow_period=False,
        )

        print(f"Adding a new row for date: {new_date}")
        first_date = price_df.index[0]
        price_df.loc[new_date] = pd.Series(dtype="float64")

        if new_date < first_date:
            price_df = price_df.sort_index().bfill()
        else:
            price_df = price_df.sort_index().ffill()

        print(f"Overwriting prices with:\n{price_df}")
        update_prices.overwrite_merged_prices_for_contract(contract, price_df)

        read_back_price = diag_prices.get_merged_prices_for_contract_object(contract)
        print(f"Read back prices:\n{read_back_price}")


if __name__ == "__main__":
    update_prices_for_contract()
