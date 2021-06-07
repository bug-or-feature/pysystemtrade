import pandas as pd
from sysdata.config.configdata import Config
from systems.basesystem import System
from systems.futures.rawdata import FuturesRawData
from systems.provided.example.rules import ewmac_forecast_with_defaults
from systems.provided.futures_chapter15.rules import ewmac
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
#NEW_TARGET_RISK = 0.17 # 4 instruments
NEW_TARGET_RISK = 0.19 # 5 instruments
#NEW_TARGET_RISK = 0.24 # 8-14 instruments

# instrument level risk (%), per instrument count
#INSTR_TARGET_RISK = 0.156 # 2 instruments
#INSTR_TARGET_RISK = 0.207 # 3 instruments
#INSTR_TARGET_RISK = 0.265 # 4 instruments
INSTR_TARGET_RISK = 0.323 # 5 instruments
#INSTR_TARGET_RISK = 0.568 # 8-14 instruments

# trading capital, PER INSTRUMENT
TRADING_CAPITAL = 6000.00

# stop loss fraction
STOP_LOSS_FRACTION = 0.5


def get_spreadbet_costs(source='db'):

    """
    calculates spreadbet costs using formulas from Leveraged Trading
    """

    rawdata = FuturesRawData()
    config = Config("systems.leveraged_trading.leveraged_trading_config.yaml")

    if source == 'db':
        sim = dbFsbSimData()
        data_source = 'barchart'
    else:
        sim = csvFsbSimData(csv_data_paths=dict(csvFuturesInstrumentData="data.futures_spreadbet.csvconfig"))
        data_source = 'provided'

    system = System([rawdata], sim, config)
    roll_config = mongoRollParametersData()

    cost_rows = []

    for instr in sim.db_futures_instrument_data.get_list_of_instruments():

        #if instr not in ['GOLD', 'CORN', 'EUROSTX', 'NASDAQ', 'SP500', 'AUD']:
        #    continue

        #print(f"processing {instr}")

        # number of rolls per year
        params = roll_config.get_roll_parameters(instr)
        roll_count = len(params.hold_rollcycle._as_list())

        instr_obj = sim._get_instrument_object_with_cost_data(instr)
        instr_class = instr_obj.meta_data.AssetClass
        instr_subclass = instr_obj.meta_data.AssetSubclass
        prices = sim.daily_prices(instr)
        date_last_price = prices.index[-1]

        # we need to adjust for the case where the spreadbet 'point' price is a multiple of the
        # underlying futures price. we'll create a data frame where the original futures price is in the first column,
        # and the spreadbet point price is in the second
        multiplier = instr_obj.meta_data.Multiplier
        point_size = instr_obj.meta_data.Pointsize
        cols = {'fPrice': sim.daily_prices(instr)}
        price_frame = pd.DataFrame(cols)
        price_frame['sbPrice'] = price_frame['fPrice'] * multiplier
        f_price = price_frame['fPrice'].iloc[-1]
        av_f_price = price_frame['fPrice'].tail(100).mean()
        sb_price = price_frame['sbPrice'].iloc[-1]
        av_sb_price = price_frame['sbPrice'].tail(100).mean()

        spread_in_points = instr_obj.meta_data.Spread
        min_bet_per_point = instr_obj.meta_data.MinBetPerPoint

        tc_ccy = (spread_in_points * min_bet_per_point) / 2
        tc_ratio = tc_ccy / ((min_bet_per_point * sb_price) / point_size)

        # calculating volatility as per 'Leveraged Trading' Appendix C, p.313

        last_date = price_frame.index[-100]
        start_date = last_date - pd.DateOffset(days=25)
        average_price = float(price_frame['sbPrice'][start_date:].mean())
        daily_vol = rawdata.daily_returns_volatility_mult(instr, int(multiplier))
        average_vol = float(daily_vol[start_date:].mean())
        avg_annual_vol = average_vol * ROOT_BDAYS_INYEAR
        avg_annual_vol_perc = avg_annual_vol / average_price
        tc_risk = tc_ratio / avg_annual_vol_perc

        turnover = 5.4
        hc_ratio = tc_ratio * roll_count * 2
        hc_risk = hc_ratio / avg_annual_vol_perc
        costs_total = (tc_risk * turnover) + hc_risk

        #notional_exposure = (ORIG_TARGET_RISK * TRADING_CAPITAL) / avg_annual_vol_perc
        notional_exposure = (INSTR_TARGET_RISK * TRADING_CAPITAL) / avg_annual_vol_perc
        min_exposure = (min_bet_per_point * average_price) / point_size
        orig_min_capital = (min_exposure * avg_annual_vol_perc) / ORIG_TARGET_RISK
        new_min_capital = orig_min_capital * (ORIG_TARGET_RISK / NEW_TARGET_RISK)
        pos_size = (notional_exposure * 1 * point_size) / average_price
        # ewmac(rawdata.get_daily_prices("EDOLLAR"), rawdata.daily_returns_volatility("EDOLLAR"), 64, 256).tail(2)
        ewmac_series = ewmac_forecast_with_defaults(price_frame['sbPrice'], 16, 64)
        #ewmac_series = ewmac(price_frame['sbPrice'], 16, 64)
        ewmac_today = ewmac_series.iloc[-1] # TODO check date. prices must be up to date
        direction = 'L' if ewmac_today > 0 else 'S'
        # instrument risk in price units
        risk_price_units = avg_annual_vol_perc * sb_price
        stop_loss_gap = risk_price_units * STOP_LOSS_FRACTION

        cost_rows.append(
            {
                'Instr': instr,
                #'Commission': 0,
                'Class': instr_class,
                'Subclass': instr_subclass,
                'Date': date_last_price,
                'PriceF': round(f_price, 2),
                'PriceSB': round(sb_price, 2),
                'Spread': spread_in_points,
                'MinBet': min_bet_per_point,
                #'Xpoint': point_size,
                'Risk': f"{round(avg_annual_vol_perc, 3)}",
                'Risk%': "{:.2%}".format(avg_annual_vol_perc),
                'TCccy': f"£{round(tc_ccy, 2)}",
                'TCratio': "{:.2%}".format(tc_ratio),
                'TCrisk': round(tc_risk, 4),
                'HCratio': round(hc_ratio, 3),
                'HCrisk': round(hc_risk, 3),
                'Ctotal': round(costs_total, 3),
                'minExp': round(min_exposure, 0),
                'OMinCap': round(orig_min_capital, 0),
                'NMinCap': round(new_min_capital, 0),
                'notExp': round(notional_exposure, 0),
                'PosSize': round(pos_size, 2),
                'Ewmac': round(ewmac_today, 2),
                'Dir': direction,
                #'riskPriceUnits': risk_price_units,
                'StopGap': round(stop_loss_gap, 0)
            }
        )

    # create dataframe
    cost_results = pd.DataFrame(cost_rows)

    # filter
    #cost_results = cost_results[cost_results["Instr"].isin(['GOLD', 'CORN', 'EUROSTX', 'NASDAQ', 'SP500', 'AUD'])]
    cost_results = cost_results[cost_results["Ctotal"] < 0.08] # costs
    cost_results = cost_results[cost_results["PosSize"] > cost_results["MinBet"]] # min bet
    #cost_results = cost_results[cost_results["minCapital"] < ()] # costs

    # group, sort
    #cost_results = cost_results.sort_values(by='NMinCap') # Ctotal, NMinCap
    cost_results = cost_results.groupby('Class').apply(lambda x: x.sort_values(by='NMinCap'))
    write_file(cost_results, 'costs', data_source, write=True)


def write_file(df, calc_type, source, write=True):

    now = datetime.now()
    dir = 'data/cost_calcs'
    full_path = f"{dir}/{calc_type}_{source}_{now.strftime('%Y-%m-%d_%H%M%S')}.csv"

    if write:
        try:
            df.to_csv(full_path, date_format='%Y-%m-%dT%H:%M:%S%z')
        except Exception as ex:
            logging.warning(f"Problem with {full_path}: {ex}")

    print(f"Printing {calc_type}:\n")
    print(f"\n{print_full(df)}\n")


if __name__ == "__main__":
    get_spreadbet_costs()
