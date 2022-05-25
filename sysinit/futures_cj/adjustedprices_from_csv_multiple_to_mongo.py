"""
We create adjusted prices using CSV multiple prices

We then store those adjusted prices in arctic and/or csv

"""
from syscore.objects import arg_not_supplied
from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysdata.csv.csv_multiple_prices import csvFuturesMultiplePricesData
from sysdata.csv.csv_adjusted_prices import csvFuturesAdjustedPricesData

from sysobjects.adjusted_prices import futuresAdjustedPrices


def _get_data_inputs(csv_mult_data_path, csv_adj_data_path):
    csv_multiple_prices = csvFuturesMultiplePricesData(
        datapath=csv_mult_data_path
    )
    arctic_adjusted_prices = arcticFuturesAdjustedPricesData()
    csv_adjusted_prices = csvFuturesAdjustedPricesData(csv_adj_data_path)

    return csv_multiple_prices, arctic_adjusted_prices, csv_adjusted_prices


def process_adjusted_prices_all_instruments(
        csv_adj_data_path=arg_not_supplied, ADD_TO_ARCTIC=True, ADD_TO_CSV=False
):
    arctic_multiple_prices, _notused, _alsonotused = _get_data_inputs(csv_adj_data_path)
    instrument_list = arctic_multiple_prices.get_list_of_instruments()
    for instrument_code in instrument_list:
        print(instrument_code)
        process_adjusted_prices_single_instrument(
            instrument_code,
            csv_adj_data_path=csv_adj_data_path,
            ADD_TO_ARCTIC=ADD_TO_ARCTIC,
            ADD_TO_CSV=ADD_TO_CSV,
        )


def process_adjusted_prices_single_instrument(
        instrument_code,
        csv_mult_data_path=arg_not_supplied,
        csv_adj_data_path=arg_not_supplied,
        ADD_TO_ARCTIC=True,
        ADD_TO_CSV=False,
):
    (
        csv_multiple_prices,
        arctic_adjusted_prices,
        csv_adjusted_prices,
    ) = _get_data_inputs(csv_mult_data_path, csv_adj_data_path)
    print(f"Generating adjusted prices for {instrument_code}")
    multiple_prices = csv_multiple_prices.get_multiple_prices(instrument_code)
    adjusted_prices = futuresAdjustedPrices.stitch_multiple_prices(
        multiple_prices, forward_fill=True
    )

    print(adjusted_prices)

    if ADD_TO_ARCTIC:
        arctic_adjusted_prices.add_adjusted_prices(
            instrument_code, adjusted_prices, ignore_duplication=True
        )
    if ADD_TO_CSV:
        csv_adjusted_prices.add_adjusted_prices(
            instrument_code, adjusted_prices, ignore_duplication=True
        )

    return adjusted_prices


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")

    # for instrument_code in ['SP500']:
    # for instrument_code in ['BOBL', 'BTP', 'BUND', 'BUXL', 'EDOLLAR', 'EURIBOR', 'OAT', 'SHATZ', 'US10', 'US10U', 'US2', 'US20', 'US30', 'US5']:
    #for instrument_code in ['STERLING3']:
    #for instrument_code in ['CAC', 'DAX', 'DOW', 'EUROSTX', 'FTSE100', 'NASDAQ', 'NIKKEI', 'RUSSELL', 'SMI', 'SP400', 'VIX']:
    #for instrument_code in ['SILVER']:
    for instrument_code in ['CANOLA', 'COCOA', 'COFFEE', 'COPPER', 'CORN', 'COTTON', 'CRUDE_W', 'FEEDCOW', 'GASOIL',
                            'GASOILINE', 'GAS_US', 'GOLD', 'GOLD_micro', 'HEATOIL', 'LEANHOG', 'LIVECOW', 'LUMBER',
                            'MILK', 'OATIES', 'OJ', 'PALLAD', 'PLAT', 'REDWHEAT', 'RICE', 'ROBUSTA', 'SILVER-mini',
                            'SOYBEAN', 'SOYMEAL', 'SOYOIL', 'SUGAR11', 'WHEAT']:
        process_adjusted_prices_single_instrument(
            instrument_code,
            ADD_TO_ARCTIC=True,
            ADD_TO_CSV=True,
            csv_mult_data_path="data.futures_cj.multiple_prices_csv",
            csv_adj_data_path="data.futures_cj.adjusted_prices_csv",
        )
