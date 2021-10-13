from sysproduction.update_fx_prices import update_fx_prices
from sysproduction.update_historical_prices import update_historical_prices
from sysproduction.update_multiple_adjusted_prices import update_multiple_adjusted_prices
from sysproduction.update_sampled_contracts import update_sampled_contracts
from sysproduction.data.prices import diagPrices


def update_all():

    instr_list = ["AEX", "ASX", "AUD", "BOBL", "BRENT_W", "BTP", "BUND", "BUXL", "CAC", "CAD", "CHF", "COCOA_NY",
                  "COCOA_LDN", "COFFEE", "COFFEE_LDN", "COPPER", "CORN", "COTTON", "CRUDE_W", "DAX", "DOLLAR", "DOW",
                  "EDOLLAR", "EUR", "EURGBP", "EURIBOR", "EUROSTX", "FTSE", "GASOIL_LDN", "GASOIL_LDN", "GASOLINE",
                  "GAS_US", "GBP", "GILT", "GOLD", "HANG", "HEATOIL", "JGB", "JPY", "LEANHOG", "LIVECOW", "LUMBER",
                  "NASDAQ", "NIKKEI", "NZD", "OAT", "OATIES", "OJ", "PALLAD", "PLAT", "RICE", "RUSSELL", "SHATZ",
                  "SILVER", "SMI", "SOYBEAN", "SOYMEAL", "SOYOIL", "SP500", "STERLING3", "US10", "US2", "US30", "US5",
                  "USTB", "V2X", "VIX", "WHEAT"]
    # prices = diagPrices()
    # print(prices.get_list_of_instruments_in_multiple_prices())

    update_fx_prices()
    update_sampled_contracts(instrument_list=instr_list)
    update_historical_prices(instrument_list=instr_list)
    update_multiple_adjusted_prices(instrument_list=instr_list)