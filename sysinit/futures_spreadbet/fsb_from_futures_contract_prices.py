from sysbrokers.IG.ig_instruments_data import (
    IgFuturesInstrumentData,
    get_instrument_object_from_config,
)
from sysdata.data_blob import dataBlob
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices
from syscore.dateutils import Frequency, MIXED_FREQ, DAILY_PRICE_FREQ, HOURLY_FREQ
from syscore.exceptions import missingInstrument
from sysproduction.update_historical_prices import write_merged_prices_for_contract


def convert_futures_prices_to_fsb_single(instr, contract_keys=None):
    data = dataBlob()
    fsb_code = f"{instr}_fsb"
    instr_data = IgFuturesInstrumentData(None, data=data)
    contracts = set()

    try:
        config = get_instrument_object_from_config(fsb_code, config=instr_data.config)
    except missingInstrument:
        print(f"FSB instrument {fsb_code} not configured, exiting")
        return
    print(
        f"IG instrument config for {fsb_code}; multiplier: {config.multiplier}, inverse {config.inverse}"
    )

    arctic_prices = arcticFuturesContractPriceData()
    for freq in [MIXED_FREQ, HOURLY_FREQ, DAILY_PRICE_FREQ]:
        prices = arctic_prices.get_prices_at_frequency_for_instrument(instr, freq)

        if contract_keys is None:
            contract_keys = prices.keys()

        print(
            f"Attempting to create FSB prices ({freq.name}) from futures prices for "
            f"{instr}, and {contract_keys}. {len(prices)} contracts total found"
        )

        # for contract_date_str, futures_prices in prices.items():
        for contract_date_str in contract_keys:
            if contract_date_str in prices:
                futures_prices = prices[contract_date_str]

                fsb_contract = futuresContract.from_two_strings(
                    fsb_code, contract_date_str
                )
                contracts.add(fsb_contract)
                for col_name in ["OPEN", "HIGH", "LOW", "FINAL"]:
                    if config.inverse:
                        futures_prices[col_name] = 1 / futures_prices[col_name]
                    futures_prices[col_name] *= config.multiplier

                fsb_price_data = futuresContractPrices(futures_prices)

                print(
                    f"Writing prices ({freq.name}) for contract {fsb_contract}, "
                    f"lines {len(fsb_price_data)}"
                )
                arctic_prices.write_prices_at_frequency_for_contract_object(
                    fsb_contract,
                    fsb_price_data,
                    frequency=freq,
                    ignore_duplication=True,
                )
            else:
                print(
                    f"No futures prices at frequency '{freq.name}' found for "
                    f"contract {contract_date_str}"
                )
    for contract in contracts:
        if arctic_prices.has_price_data_for_contract_at_frequency(
            contract, HOURLY_FREQ
        ) and arctic_prices.has_price_data_for_contract_at_frequency(
            contract, DAILY_PRICE_FREQ
        ):
            write_merged_prices_for_contract(
                data, contract, [HOURLY_FREQ, DAILY_PRICE_FREQ]
            )


if __name__ == "__main__":
    # input("Will overwrite existing prices are you sure?! CTL-C to abort")

    # 'XXX'
    for instr in ["GAS_NL", "GAS_UK", "LUMBER-new"]:
        convert_futures_prices_to_fsb_single(instr)
        # convert_futures_prices_to_fsb_single(instr, ["20080900"])
