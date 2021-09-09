import logging
from datetime import datetime, timedelta
import sys

import pandas as pd

from sysbrokers.IG.ig_connection import connectionIG
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
from systems.futures_spreadbet.rawdata import FuturesSpreadbetRawData
from systems.leveraged_trading.rules import smac, rasmac

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

conn = connectionIG()

# stop loss fraction
STOP_LOSS_FRACTION = 0.5

MAV_SCALING_FACTOR = 57.12


def get_spreadbet_costs():

    """
    calculates spreadbet costs using formulas from Leveraged Trading
    """

    print(f"Name of the script      : {sys.argv[0]=}")
    print(f"Arguments of the script : {sys.argv[1:]=}")

    args = None
    if len(sys.argv) > 1:
        args = sys.argv[1]

    config = Config("systems.leveraged_trading.leveraged_trading_config.yaml")
    ig_prices = CsvFsbContractPriceData()

    #if source == 'db':
    sim = dbFsbSimData()
    data_source = 'barchart'
    #else:
    #    sim = csvFsbSimData(csv_data_paths=dict(csvFuturesInstrumentData="data.futures_spreadbet.csvconfig"))
    #    data_source = 'provided'

    system = System(
        [
            Account(),
            Rules(),
            FuturesSpreadbetRawData()
        ], sim, config)
    roll_config = mongoRollParametersData()

    positions = get_position_list()
    cost_rows = []

    if args is not None:
        instr_list = sys.argv[1].split(",")
    else:
        instr_list = sim.db_futures_instrument_data.get_list_of_instruments()

    for instr in instr_list:

        if instr not in instr_list:
            continue

        # getting instrument config
        instr_obj = sim._get_instrument_object_with_cost_data(instr)
        instr_class = instr_obj.meta_data.AssetClass
        point_size = instr_obj.meta_data.Pointsize
        #instr_subclass = instr_obj.meta_data.AssetSubclass
        #multiplier = instr_obj.meta_data.Multiplier
        spread_in_points = instr_obj.meta_data.Slippage * 2
        min_bet_per_point = instr_obj.meta_data.Pointsize
        params = roll_config.get_roll_parameters(instr)
        roll_count = len(params.hold_rollcycle._as_list())

        # prices
        warn = ""
        prices = system.rawdata.get_daily_prices(instr)
        date_last_price = prices.index[-1]
        if not check_price(date_last_price):
            warn = "!!! dates !!!"
        sb_price = prices.iloc[-1]

        # risk (annual volatility of returns)
        #   - calculated as per 'Leveraged Trading' Appendix C, p.313,
        start_date = date_last_price - pd.DateOffset(days=25)
        average_price = float(prices[start_date:].mean())

        # this is good from parent class
        daily_returns = system.rawdata.daily_returns(instr)

        #daily_returns_volatility = system.rawdata.daily_returns_volatility(instr)
        #annual_returns_vol_series = daily_returns_volatility * ROOT_BDAYS_INYEAR
        #annual_vol = annual_returns_vol_series.iloc[-1]

        # this is good from parent class
        daily_percentage_returns = system.rawdata.get_daily_percentage_returns(instr)

        # this is good from parent class, EXCEPT * 100 for a formatted %
        # not used in LT?
        daily_percentage_volatility = system.rawdata.get_daily_percentage_volatility(instr)

        # defined in our subclass
        annual_vol_percent = system.rawdata.get_annual_percentage_volatility(instr)

        # STDEV of last 25 days of daily percentage returns
        daily_vol = daily_percentage_returns.ffill().rolling(window=25).std()
        annual_vol_series = daily_vol * ROOT_BDAYS_INYEAR
        #annual_vol = annual_vol_series[-1]

        annual_vol = recent_average_annual_perc_vol(annual_vol_series)


        risk_in_price_units = annual_vol * sb_price

        # costs
        turnover = 5.4
        tc_ccy = (spread_in_points * min_bet_per_point) / 2
        tc_ratio = tc_ccy / ((min_bet_per_point * sb_price) / point_size)
        tc_risk = tc_ratio / annual_vol
        hc_ratio = tc_ratio * roll_count * 2
        hc_risk = hc_ratio / annual_vol
        costs_total = (tc_risk * turnover) + hc_risk

        # forecasts
        #ewmac_series = ewmac(prices, daily_vol, 16, 64)
        #ewmac_series = ewmac_calc_vol(prices, 16, 64, vol_days=25)
        #ewmac_today = ewmac_series.iloc[-1]
        smac_series = smac(prices, 16, 64)
        smac_today = smac_series.iloc[-1]

        rasmac_series = rasmac(prices, 16, 64)
        rasmac_today = rasmac_series.iloc[-1]

        riskAdjMAC = smac_today / risk_in_price_units
        direction = 'L' if smac_today > 0 else 'S'
        if direction == 'L':
            rescaledForecast = min(20, riskAdjMAC * MAV_SCALING_FACTOR)
        else:
            rescaledForecast = max(-20, riskAdjMAC * MAV_SCALING_FACTOR)

        # scaledForecast = riskAdjMAC * MAV_SCALING_FACTOR
        # if direction == 'L':
        #     scaledCappedForecast = min(20, riskAdjMAC * MAV_SCALING_FACTOR)
        # else:
        #     scaledCappedForecast = max(-20, riskAdjMAC * MAV_SCALING_FACTOR)


        # positions
        min_exposure = (min_bet_per_point * average_price) / point_size
        orig_min_capital = (min_exposure * annual_vol) / ORIG_TARGET_RISK
        new_min_capital = orig_min_capital * (ORIG_TARGET_RISK / NEW_TARGET_RISK)
        trading_capital = CAPITAL_PER_INSTR + get_current_pandl(instr, positions, ig_prices)
        ideal_notional_exposure = ((rescaledForecast / 10) * INSTR_TARGET_RISK * trading_capital) / annual_vol
        current_pos = get_current_position(instr, positions, sb_price)
        #current_notional_exposure_old = (current_pos * sb_price) / (point_size)
        current_notional_exposure = get_current_exposure(instr, positions)
        average_notional_exposure = (INSTR_TARGET_RISK * trading_capital) / annual_vol
        deviation = (ideal_notional_exposure - current_notional_exposure) / average_notional_exposure
        pos_size = (ideal_notional_exposure * 1 * point_size) / average_price
        adjustment_required = adjustment_calc(sb_price, current_notional_exposure, ideal_notional_exposure) if abs(deviation) > 0.1 else 0.0
        #account = pandl_for_instrument_forecast(forecast=smac_series, price=system.rawdata.get_daily_prices(instr))
        #print(f"P&L stats for {instr}: {account.percent.stats()}")

        cost_rows.append(
            {
                'Instr': instr,
                #'Commission': 0,
                'Class': instr_class,
                #'Subclass': instr_subclass,
                #'PriceF': round(f_price, 2),
                'Price': round(sb_price, 2),
                'Date': date_last_price,
                #'mult': multiplier,
                'Spread': spread_in_points,
                'MinBet': min_bet_per_point,
                #'Xpoint': point_size,
                #'Risk': f"{round(avg_annual_vol_perc, 3)}",
                'Risk%': "{:.2%}".format(annual_vol),
                #'riskPU': round(risk_in_price_units, 2),
                #'TCccy': f"£{round(tc_ccy, 3)}",
                #'TCratio': "{:.3%}".format(tc_ratio),
                #'TCrisk': round(tc_risk, 6),
                #'HCratio': round(hc_ratio, 3),
                #'HCrisk': round(hc_risk, 3),
                'Ctotal': round(costs_total, 3),
                'minExp': round(min_exposure, 0),
                #'OMinCap': round(orig_min_capital, 0),
                'MinCap': round(new_min_capital, 0),
                'MAC': round(smac_today, 2),
                'raMAC': round(riskAdjMAC, 3),
                'scFC': round(rescaledForecast, 1),
                #'sFC': round(scaledForecast, 1),
                #'scFC': round(scaledCappedForecast, 1),
                'Dir': direction,
                'IdealExp': round(ideal_notional_exposure, 0),
                'CurrExp': round(current_notional_exposure, 0),
                'AvgExp': round(average_notional_exposure, 0),
                'Dev%': "{:.2%}".format(deviation),
                'CurrPos': round(current_pos, 2),
                'IdealPos': round(pos_size, 2),
                'AdjReq': round(adjustment_required, 2),
                'Msg': warn
                #'StopGap': round(stop_loss_gap, 0)
            }
        )

    # create dataframe
    cost_results = pd.DataFrame(cost_rows)

    # filter
    cost_results = cost_results[cost_results["Ctotal"] < 0.08] # costs
    #cost_results = cost_results[abs(cost_results["PosSize"]) > cost_results["MinBet"]] # min bet
    #cost_results = cost_results[cost_results["minCapital"] < ()] # costs

    # group, sort
    cost_results = cost_results.sort_values(by='Ctotal') # Ctotal, NMinCap
    #cost_results = cost_results.groupby('Class').apply(lambda x: x.sort_values(by='MinCap'))
    write_file(cost_results, 'costs', data_source, write=True)

def recent_average_annual_perc_vol(vol_series) -> float:
    last_date = vol_series.index[-1]
    start_date = last_date - pd.DateOffset(years=1)
    average_vol = float(vol_series[start_date:].mean())
    return average_vol

def write_file(df, calc_type, source, write=True):

    now = datetime.now()
    dir = 'data/cost_calcs'
    full_path = f"{dir}/{calc_type}_{source}_{now.strftime('%Y-%m-%d_%H%M%S')}.csv"

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


def get_current_position_old(instr, pos_list):
    total = 0.0
    filtered = filter(lambda p: p['instr'] == instr, pos_list)
    for pos in filtered:
        if pos['dir'] == 'BUY':
            total += pos['size']
        else:
            total -= pos['size']
    return total

def get_current_position(instr, pos_list, curr_price):
    curr_exp = get_current_exposure(instr, pos_list)
    position = (curr_exp * 1) / curr_price
    return position

# exposure = amount per point × price ÷ point size
def get_current_exposure(instr, pos_list):
    total = 0.0
    filtered = filter(lambda p: p['instr'] == instr, pos_list)
    for pos in filtered:
        size = pos['size']
        level = pos['level']
        part_exp = size * level * 1
        if pos['dir'] == 'BUY':
            total += part_exp
        else:
            total -= part_exp
    return total

def adjustment_calc(curr_price, current_exposure, ideal_exposure):
    exposure_diff = ideal_exposure - current_exposure
    #exposure_diff = current_exposure - ideal_exposure
    #filtered = filter(lambda p: p['instr'] == instr, positions)
    # LT p.264
    # bet per point = (exposure  x point size) / price
    adj = (exposure_diff * 1) / curr_price
    return adj


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
