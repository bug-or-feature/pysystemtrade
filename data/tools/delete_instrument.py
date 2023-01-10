from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData
from sysdata.arctic.arctic_spreads import arcticSpreadsForInstrumentData
from sysdata.data_blob import dataBlob
from sysproduction.data.prices import get_valid_instrument_code_from_user
from syscore.interactive import true_if_answer_is_yes


def delete_instrument():
    with dataBlob(log_name="Instrument-Deleter") as data:
        do_another = True
        while do_another:
            exit_str = "Finished: Exit"
            instr = get_valid_instrument_code_from_user(
                data, allow_all=False, allow_exit=True, exit_code=exit_str
            )
            if instr is exit_str:
                do_another = False
            else:
                if true_if_answer_is_yes(
                    f"OK to delete all contract, multiple, adjusted and spread price data for {instr}, "
                    f"are you sure? (y/n):"
                ):
                    # Delete contract data
                    contract_data = arcticFuturesContractPriceData()
                    contract_data.delete_all_prices_for_instrument_code(
                        instr, areyousure=True
                    )

                    # Delete multiple price data.
                    multiple_prices = arcticFuturesMultiplePricesData()
                    multiple_prices.delete_multiple_prices(instr, are_you_sure=True)

                    # Delete adjusted prices.
                    adjusted_prices = arcticFuturesAdjustedPricesData()
                    adjusted_prices.delete_adjusted_prices(instr, are_you_sure=True)

                    # delete spread data
                    spread_data = arcticSpreadsForInstrumentData()
                    spread_data.delete_spreads(instr, are_you_sure=True)

                    print(
                        f"Contract, multiple, adjusted and spread price data for {instr} deleted."
                    )

                else:
                    print("Deletion not confirmed, no action")


if __name__ == "__main__":
    delete_instrument()
