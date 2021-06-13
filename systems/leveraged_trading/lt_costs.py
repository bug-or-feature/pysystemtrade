import pandas as pd
from sysdata.config.configdata import Config
from systems.basesystem import System
from systems.forecasting import Rules
from systems.accounts.accounts_stage import Account
from systems.futures_spreadbet.rawdata import FuturesSpreadbetRawData
from systems.leveraged_trading.rules import smac
from syscore.dateutils import ROOT_BDAYS_INYEAR
from syscore.pdutils import print_full
from datetime import datetime
import logging
from sysdata.sim.db_fsb_sim_data import dbFsbSimData
from sysdata.sim.csv_fsb_sim_data import csvFsbSimData
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData

# original account level target risk (%), when trading one instrument
#TARGET_RISK = 0.12
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

# trading capital, PER INSTRUMENT
TRADING_CAPITAL = {
    'BUND': 7700.00,
    'GOLD': 8370.00,
    'SP500': 7935.00,
    'NZD': 7995.00
}

current_positions = {
    'BUND': -3.58,
    'GOLD': 19.26,
    'SP500': 3.42,
    'NZD': 1.13
}

# stop loss fraction
STOP_LOSS_FRACTION = 0.5

MAV_SCALING_FACTOR = 57.12

def get_spreadbet_costs(source='db'):

    """
    calculates spreadbet costs using formulas from Leveraged Trading
    """

    config = Config("systems.leveraged_trading.leveraged_trading_config.yaml")

    if source == 'db':
        sim = dbFsbSimData()
        data_source = 'barchart'
    else:
        sim = csvFsbSimData(csv_data_paths=dict(csvFuturesInstrumentData="data.futures_spreadbet.csvconfig"))
        data_source = 'provided'

    system = System(
        [
            Account(),
            Rules(),
            FuturesSpreadbetRawData()
        ], sim, config)
    roll_config = mongoRollParametersData()

    cost_rows = []

    for instr in sim.db_futures_instrument_data.get_list_of_instruments():

        if instr not in ['GOLD', 'BUND', 'NZD', 'SP500']:
            continue

        #print(f"processing {instr}")

        # getting instrument config
        instr_obj = sim._get_instrument_object_with_cost_data(instr)
        instr_class = instr_obj.meta_data.AssetClass
        point_size = instr_obj.meta_data.Pointsize
        instr_subclass = instr_obj.meta_data.AssetSubclass
        multiplier = instr_obj.meta_data.Multiplier
        spread_in_points = instr_obj.meta_data.Spread
        min_bet_per_point = instr_obj.meta_data.MinBetPerPoint
        params = roll_config.get_roll_parameters(instr)
        roll_count = len(params.hold_rollcycle._as_list())

        # prices
        prices = system.rawdata.get_daily_prices(instr)
        date_last_price = prices.index[-1]
        sb_price = prices.iloc[-1]

        # risk (annual volatility of returns)
        #   - calculated as per 'Leveraged Trading' Appendix C, p.313,
        #   - and using code from systems.accounts.account_costs, except using 25 days, not 1 year
        start_date = date_last_price - pd.DateOffset(days=25) # TODO warning if not updated
        average_price = float(prices[start_date:].mean())
        daily_vol = system.rawdata.daily_returns_volatility(instr)
        average_vol = float(daily_vol[start_date:].mean())
        avg_annual_vol = average_vol * ROOT_BDAYS_INYEAR
        avg_annual_vol_perc = avg_annual_vol / average_price
        risk_in_price_units = avg_annual_vol_perc * sb_price

        # costs
        turnover = 5.4
        tc_ccy = (spread_in_points * min_bet_per_point) / 2
        tc_ratio = tc_ccy / ((min_bet_per_point * sb_price) / point_size)
        tc_risk = tc_ratio / avg_annual_vol_perc
        hc_ratio = tc_ratio * roll_count * 2
        hc_risk = hc_ratio / avg_annual_vol_perc
        costs_total = (tc_risk * turnover) + hc_risk

        # forecasts
        #ewmac_series = ewmac(prices, daily_vol, 16, 64)
        #ewmac_series = ewmac_calc_vol(prices, 16, 64, vol_days=25)
        #ewmac_today = ewmac_series.iloc[-1]
        smac_series = smac(prices, 16, 64)
        smac_today = smac_series.iloc[-1]
        riskAdjMAC = smac_today / risk_in_price_units
        direction = 'L' if smac_today > 0 else 'S'
        if direction == 'L':
            rescaledForecast = min(20, riskAdjMAC * MAV_SCALING_FACTOR)
        else:
            rescaledForecast = max(-20, riskAdjMAC * MAV_SCALING_FACTOR)

        # positions
        min_exposure = (min_bet_per_point * average_price) / point_size
        orig_min_capital = (min_exposure * avg_annual_vol_perc) / ORIG_TARGET_RISK
        new_min_capital = orig_min_capital * (ORIG_TARGET_RISK / NEW_TARGET_RISK)

        trading_capital = TRADING_CAPITAL[instr]
        ideal_notional_exposure = ((rescaledForecast / 10) * INSTR_TARGET_RISK * trading_capital) / avg_annual_vol_perc
        current_pos = current_positions[instr]
        current_notional_exposure = (current_pos * sb_price) / (point_size)

        average_notional_exposure = (INSTR_TARGET_RISK * trading_capital) / avg_annual_vol_perc
        deviation = (ideal_notional_exposure - current_notional_exposure) / average_notional_exposure
        adjustment_required = 'Y' if abs(deviation) > 0.1 else 'N'
        pos_size = (ideal_notional_exposure * 1 * point_size) / average_price
        adjustment_required = pos_size - current_pos if abs(deviation) > 0.1 else 0.0


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
                'Risk%': "{:.2%}".format(avg_annual_vol_perc),
                #'riskPU': round(risk_in_price_units, 2),
                #'TCccy': f"£{round(tc_ccy, 2)}",
                #'TCratio': "{:.2%}".format(tc_ratio),
                #'TCrisk': round(tc_risk, 4),
                #'HCratio': round(hc_ratio, 3),
                #'HCrisk': round(hc_risk, 3),
                'Ctotal': round(costs_total, 3),
                'minExp': round(min_exposure, 0),
                #'OMinCap': round(orig_min_capital, 0),
                'MinCap': round(new_min_capital, 0),
                'MAC': round(smac_today, 2),
                'raMAC': round(riskAdjMAC, 3),
                'scFC': round(rescaledForecast, 1),
                'Dir': direction,
                #'notExp': round(notional_exposure, 0),
                #'PosSize': round(pos_size, 2),
                'IdealExp': round(ideal_notional_exposure, 0),
                'CurrExp': round(current_notional_exposure, 0),
                'AvgExp': round(average_notional_exposure, 0),
                'Dev%': "{:.2%}".format(deviation),
                'PosSize': round(pos_size, 2),
                'AdjReq': round(adjustment_required, 2),

                #'StopGap': round(stop_loss_gap, 0)
            }
        )

    # create dataframe
    cost_results = pd.DataFrame(cost_rows)

    # filter
    cost_results = cost_results[cost_results["Ctotal"] < 0.08] # costs
    cost_results = cost_results[abs(cost_results["PosSize"]) > cost_results["MinBet"]] # min bet
    #cost_results = cost_results[cost_results["minCapital"] < ()] # costs

    # group, sort
    cost_results = cost_results.sort_values(by='MinCap') # Ctotal, NMinCap
    #cost_results = cost_results.groupby('Class').apply(lambda x: x.sort_values(by='MinCap'))
    write_file(cost_results, 'costs', data_source, write=False)


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


if __name__ == "__main__":
    get_spreadbet_costs()
