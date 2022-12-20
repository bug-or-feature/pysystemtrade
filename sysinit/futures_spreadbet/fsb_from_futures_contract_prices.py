from sysbrokers.IG.ig_instruments_data import (
    IgFuturesInstrumentData,
    get_instrument_object_from_config
)
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices
from syscore.objects import missing_instrument


def convert_futures_prices_to_fsb_single(instr):

    arctic_prices = arcticFuturesContractPriceData()
    instr_data = IgFuturesInstrumentData()
    instr_prices = arctic_prices.get_merged_prices_for_instrument(instr)
    fsb_code = f"{instr}_fsb"

    config = get_instrument_object_from_config(fsb_code, config=instr_data.config)
    if config is missing_instrument:
        print(f"FSB instrument {fsb_code} not configured, exiting")
        return
    print(f"IG instrument config for {fsb_code}; multiplier: {config.multiplier}, inverse {config.inverse}")

    print(f"Creating FSB prices from futures price for {instr}, found {len(instr_prices)} contracts")

    for contract_date_str, futures_prices in instr_prices.items():
        fsb_contract = futuresContract.from_two_strings(fsb_code, contract_date_str)
        for col_name in ["OPEN", "HIGH", "LOW", "FINAL"]:
            if config.inverse:
                futures_prices[col_name] = 1 / futures_prices[col_name]
            futures_prices[col_name] *= config.multiplier

        fsb_price_data = futuresContractPrices(futures_prices)

        print(f"Writing prices for contract {fsb_contract}, lines {len(fsb_price_data)}")
        arctic_prices.write_merged_prices_for_contract_object(
            fsb_contract, fsb_price_data, ignore_duplication=True
        )


if __name__ == "__main__":
    #input("Will overwrite existing prices are you sure?! CTL-C to abort")

    # 'XXX'
    # ['VIX', 'EURIBOR', 'FED', 'SONIA3', 'XXX']
    for instr in ['VIX', 'EURIBOR', 'FED', 'SONIA3']:
        convert_futures_prices_to_fsb_single(instr)
