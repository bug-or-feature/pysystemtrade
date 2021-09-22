from sysproduction.update_fx_prices import update_fx_prices
from sysproduction.update_historical_prices import update_historical_prices
from sysproduction.update_multiple_adjusted_prices import update_multiple_adjusted_prices
from sysproduction.update_sampled_contracts import update_sampled_contracts


def update_all():

    # full_instr_list = ['AEX', 'ASX', 'AUD', 'BOBL', 'BRENT_W', 'BTP', 'BUND', 'BUXL', 'CAC', 'CARBON',
    #               'CHF', 'COCOA_LDN', 'COCOA_NY', 'COFFEE', 'COFFEE_LDN', 'COPPER', 'CORN', 'COTTON',
    #               'CRUDE_W', 'DAX', 'DOLLAR', 'DOW', 'EDOLLAR', 'EUR', 'EURGBP', 'EURIBOR', 'EUROSTX',
    #               'FTSE', 'GASOIL_LDN', 'GASOLINE', 'GAS_US', 'GBP', 'GILT', 'GOLD', 'HANG', 'HEATOIL',
    #               'JGB', 'JPY', 'LEANHOG', 'LIVECOW', 'LUMBER', 'MXP', 'NASDAQ', 'NIKKEI', 'NZD', 'OAT',
    #               'OATIES', 'OJ', 'PALLAD', 'PLAT', 'RICE', 'RUSSELL', 'SHATZ', 'SILVER', 'SMI', 'SOYBEAN',
    #               'SOYMEAL', 'SOYOIL', 'SP500', 'STERLING3', 'SUGAR', 'SUGAR_LDN', 'US10', 'US2', 'US30',
    #               'US5', 'USTB', 'V2X', 'VIX', 'WHEAT', 'WHEAT_LDN']

    instr_list = ['AEX', 'ASX', 'AUD', 'BOBL', 'BTP', 'BUND', 'BUXL', 'CAC',
                  'CHF', 'COPPER', 'CORN',
                  'CRUDE_W', 'DAX', 'DOLLAR', 'DOW', 'EDOLLAR', 'EUR', 'EURGBP', 'EUROSTX',
                  'FTSE', 'GAS_US', 'GBP', 'GILT', 'GOLD', 'HANG',
                  'JGB', 'JPY', 'LEANHOG', 'LIVECOW', 'NASDAQ', 'NIKKEI', 'NZD', 'OAT',
                  'PALLAD', 'PLAT', 'RUSSELL', 'SHATZ', 'SMI', 'SOYBEAN',
                  'SP500', 'US10', 'US2', 'US30',
                  'US5', 'USTB', 'V2X', 'VIX', 'WHEAT']

    update_fx_prices()
    update_sampled_contracts(instrument_list=instr_list)
    update_historical_prices(instrument_list=instr_list)
    update_multiple_adjusted_prices(instrument_list=instr_list)