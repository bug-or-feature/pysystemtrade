import logging
from datetime import datetime, timedelta
import pytz

import pandas as pd

from sysbrokers.IG.ig_connection import ConnectionIG
from syscore.dateutils import ROOT_BDAYS_INYEAR
from syscore.fileutils import get_filename_for_package
from syscore.pdutils import print_full
from sysdata.config.configdata import Config
from sysdata.config.production_config import get_production_config
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysdata.igcsv.csv_fsb_contract_prices import CsvFsbContractPriceData
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysdata.sim.csv_fsb_sim_data import csvFsbSimData
from sysdata.sim.db_fsb_sim_data import dbFsbSimData
from sysobjects.contracts import futuresContract
from systems.accounts.account_forecast import pandl_for_instrument_forecast
from systems.accounts.accounts_stage import Account
from systems.basesystem import System
from systems.forecasting import Rules
from systems.forecast_scale_cap import ForecastScaleCap
from systems.futures_spreadbet.rawdata import FuturesSpreadbetRawData
from systems.futures_spreadbet.rules import smac, rasmac
from systems.futures_spreadbet.fsb_system import fsb_system

# original account level target risk (%), when trading one instrument
ORIG_TARGET_RISK = 0.12

# updated account level target risk (%), per instrument count
#NEW_TARGET_RISK = 0.13 # 2 instruments
#NEW_TARGET_RISK = 0.14 # 3 instruments
NEW_TARGET_RISK = 0.17 # 4 instruments
#NEW_TARGET_RISK = 0.19 # 5 instruments
#NEW_TARGET_RISK = 0.24 # 8-14 instruments

# instrument level risk (%), per instrument count
#INSTR_TARGET_RISK = 0.156 # 2 instruments
#INSTR_TARGET_RISK = 0.207 # 3 instruments
INSTR_TARGET_RISK = 0.265 # 4 instruments
#INSTR_TARGET_RISK = 0.323 # 5 instruments
#INSTR_TARGET_RISK = 0.568 # 8-14 instruments

CAPITAL_PER_INSTR = 8000.00

conn = ConnectionIG()

# stop loss fraction
STOP_LOSS_FRACTION = 0.5

MAV_SCALING_FACTOR = 57.12

def get_spreadbet_costs(source='db'):

    """
    calculates spreadbet costs using formulas from Leveraged Trading
    """

    config = Config("systems.futures_spreadbet.leveraged_trading_config.yaml")

    #ig_prices = CsvFsbContractPriceData()

    data = dbFsbSimData()

    # system = System(
    #     [
    #         FuturesSpreadbetRawData(),
    #         Rules(),
    #         ForecastScaleCap()
    #     ], data, config)

    system = fsb_system()

    #roll_config = mongoRollParametersData()

    positions = get_position_list()
    cost_rows = []

    #for instr in system.data.get_instrument_list():
    list = system.get_instrument_list()
    for instr in system.get_instrument_list():

        #if instr not in ['GOLD']:
        if instr not in ['GOLD', 'BUND', 'NZD', 'SP500']:
        #if instr not in ["AEX","CAC","CORN","EUROSTX","GOLD","NASDAQ","PALLAD","PLAT","SMI","SOYBEAN","SP500","V2X","VIX","WHEAT"]:
            continue

        # prices
        warn = ""
        if not check_price(system.rawdata.get_daily_prices(instr).index[-1]):
            warn = "!!! dates !!!"

        # getting instrument config
        instr_obj = data._get_instrument_object_with_cost_data(instr)
        instr_class = instr_obj.meta_data.AssetClass
        # point_size = instr_obj.meta_data.Pointsize
        instr_subclass = instr_obj.meta_data.AssetSubclass
        spread_in_points = instr_obj.meta_data.Slippage * 2
        min_bet_per_point = instr_obj.meta_data.Pointsize

        # prices
        warn = ""
        prices = system.rawdata.get_daily_prices(instr)
        date_last_price = prices.index[-1]
        if not check_price(date_last_price):
            warn = "!!! dates !!!"
        sb_price = prices.iloc[-1]

        start_date = date_last_price - pd.DateOffset(days=25)
        average_price = float(prices[start_date:].mean())

        #annual_vol = recent_average_annual_perc_vol(annual_vol_series)

        # defined in our subclass
        annual_vol_percent = system.rawdata.get_annual_percentage_volatility(instr)

        # from accounts
        #annual_vol_percent = system.accounts._recent_average_annual_perc_vol(instr)

        # costs
        turnover = 5.4
        tc_risk = system.accounts.get_SR_cost_per_trade_for_instrument(instr)
        hc_only = system.accounts.get_SR_holding_cost_only(instr)
        total_costs = system.accounts.get_SR_cost_given_turnover(instr, turnover)

        # forecasts
        #ewmac_series = ewmac(prices, daily_vol, 16, 64)
        #ewmac_series = ewmac_calc_vol(prices, 16, 64, vol_days=25)
        #ewmac_today = ewmac_series.iloc[-1]
        #smac_series = smac(prices, 16, 64)
        #smac_today = smac_series.iloc[-1]

        notional_position_series = system.portfolio.get_notional_position(instr)
        notional_position = notional_position_series.iloc[-1]

        cost_rows.append(
            {
                'Instr': instr,
                #'Commission': 0,
                'Class': instr_class,
                #'Subclass': instr_subclass,
                #'PriceF': round(f_price, 2),
                'Price': round(system.rawdata.get_daily_prices(instr).iloc[-1], 2),
                'Date': system.rawdata.get_daily_prices(instr).index[-1],
                #'mult': multiplier,
                'Spread': spread_in_points,
                'MinBet': min_bet_per_point,
                #'Xpoint': point_size,
                #'Risk': f"{round(avg_annual_vol_perc, 3)}",
                'DailyVol%': round(system.rawdata.get_daily_percentage_volatility(instr).iloc[-1], 4),
                'AnnVol%': "{:.2%}".format(system.rawdata.get_annual_percentage_volatility(instr).iloc[-1]),
                #'riskPU': round(risk_in_price_units, 2),
                #'TCccy': f"£{round(tc_ccy, 2)}",
                #'TCratio': "{:.2%}".format(tc_ratio),
                'TCrisk': round(tc_risk, 3),
                'HConly': round(hc_only, 3),
                'Ctotal': round(total_costs, 3),

                #'instr_turnover': round(instr_turnover, 2),
                #'ss_turnover': round(ss_turnover, 2),
                #'fc_turnover': round(fc_turnover, 2),
                #'HCratio': round(hc_ratio, 3),
                #'HCrisk': round(hc_risk, 3),
                #'Ctotal': round(costs_total, 3),
                #'minExp': round(min_exposure, 0),
                #'OMinCap': round(orig_min_capital, 0),
                #'MinCap': round(new_min_capital, 0),
                #'MAC': round(system.rules.get_raw_forecast(instr, 'smac16_64').iloc[-1], 2),

                #'fcScalar': round(system.forecastScaleCap.get_forecast_scalar(instr, 'smac16_64').iloc[-1], 4),
                #'scaledFC': round(system.forecastScaleCap.get_scaled_forecast(instr, 'smac16_64').iloc[-1], 4),
                #'cappedFC': round(system.forecastScaleCap.get_capped_forecast(instr, 'smac16_64').iloc[-1], 4),

                'notPos': round(notional_position, 2),

                #'raMAC': round(riskAdjMAC, 3),
                #'scFC': round(rescaledForecast, 1),
                #'Dir': direction,
                #'notExp': round(notional_exposure, 0),
                #'PosSize': round(pos_size, 2),
                #'IdealExp': round(ideal_notional_exposure, 0),
                #'CurrExp': round(current_notional_exposure, 0),
                #'AvgExp': round(average_notional_exposure, 0),
                #'Dev%': "{:.2%}".format(deviation),
                #'PosSize': round(pos_size, 2),
                #'AdjReq': round(adjustment_required, 2),
                #'Msg': warn
                #'StopGap': round(stop_loss_gap, 0)
            }
        )

    # create dataframe
    cost_results = pd.DataFrame(cost_rows)

    # filter
    #cost_results = cost_results[cost_results["Ctotal"] < 0.08] # costs
    #cost_results = cost_results[abs(cost_results["PosSize"]) > cost_results["MinBet"]] # min bet
    #cost_results = cost_results[cost_results["minCapital"] < ()] # costs

    # group, sort
    #cost_results = cost_results.sort_values(by='Instr') # Instr
    cost_results = cost_results.sort_values(by='Ctotal') # Ctotal, NMinCap
    #cost_results = cost_results.groupby('Class').apply(lambda x: x.sort_values(by='MinCap'))
    write_file(cost_results, 'costs', write=False)


def write_file(df, calc_type, write=True):

    now = datetime.now()
    dir = 'data/cost_calcs'
    full_path = f"{dir}/{calc_type}_db_{now.strftime('%Y-%m-%d_%H%M%S')}.csv"

    if write:
        try:
            df.to_csv(full_path, date_format='%Y-%m-%dT%H:%M:%S%z')
        except Exception as ex:
            logging.warning(f"Problem with {full_path}: {ex}")

    #print(f"Printing {calc_type}:\n")
    print(f"\n{print_full(df)}\n")


def get_position_list():
    position_list = conn.get_positions()
    #print(position_list)
    return position_list


def get_current_position(instr, pos_list):
    total = 0.0
    filtered = filter(lambda p: p['instr'] == instr, pos_list)
    for pos in filtered:
        if pos['dir'] == 'BUY':
            total += pos['size']
        else:
            total -= pos['size']
    return total


def get_current_pandl(instr, pos_list, ig_prices: CsvFsbContractPriceData):

    result = 0.0
    filtered_list = [el for el in pos_list if el['instr'] == instr]

    if len(filtered_list) > 0:
        expiry_code = filtered_list[0]['expiry']

        expiry_code_date = datetime.strptime(f'01-{expiry_code}', '%d-%b-%y')
        #filename = f"{instr}_{expiry_code_date.strftime('%Y%m')}00.csv"

        contract = futuresContract(instr, expiry_code_date.strftime('%Y%m'))
        prices = ig_prices._get_prices_for_contract_object_no_checking(contract)
        last_price = prices.return_final_prices()[-1]

        for pos in filtered_list:
            size = pos['size']
            dir = pos['dir']
            level = pos['level']
            if dir == 'BUY':
                result += (last_price - level) * size
            else:
                result -= (last_price - level) * size

    return result


def check_price(price_date):
    now = datetime.now() #.astimezone(tz=pytz.utc)
    price_datetime = price_date.to_pydatetime()
    max_diff = 2 if datetime.now().weekday() == 1 else 1
    diff = now - price_datetime
    return diff <= timedelta(days=max_diff)

if __name__ == "__main__":
    get_spreadbet_costs()
