import pandas as pd
from sysdata.config.configdata import Config
from systems.basesystem import System
from systems.futures.rawdata import FuturesRawData
from systems.provided.example.rules import ewmac_forecast_with_defaults
from syscore.dateutils import ROOT_BDAYS_INYEAR
from syscore.pdutils import print_full
from datetime import datetime
import logging
from sysdata.sim.db_fsb_sim_data import dbFsbSimData
from sysdata.sim.csv_fsb_sim_data import csvFsbSimData
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData

# target risk 'magic number'
TARGET_RISK = 12.0

# trading capital
TRADING_CAPITAL = 6500.00

# stop loss fraction
STOP_LOSS_FRACTION = 0.5


def get_spreadbet_costs(source='db'):

    rawdata = FuturesRawData()
    config = Config("systems.leveraged_trading.leveraged_trading_config.yaml")

    if source == 'db':
        sim = dbFsbSimData()
        data_source = 'provided'
    else:
        sim = csvFsbSimData(csv_data_paths=dict(csvFuturesInstrumentData="data.futures_spreadbet.csvconfig"))
        data_source = 'barchart'

    system = System([rawdata], sim, config)
    roll_config = mongoRollParametersData()

    cost_rows = []
    position_rows = []

    for instr in sim.db_futures_instrument_data.get_list_of_instruments():

        #print(f"processing {instr}")

        # number of rolls per year
        params = roll_config.get_roll_parameters(instr)
        roll_count = len(params.hold_rollcycle._as_list())

        instr_obj = sim._get_instrument_object_with_cost_data(instr)
        instr_class = instr_obj.meta_data.AssetClass
        prices = sim.daily_prices(instr)
        date_last_price = prices.index[-1]

        # we need to adjust for the case where the spreadbet 'point' price is a multiple of the
        # underlying futures price. we'll create a data frame where the original futures price is in the first column,
        # and the spreadbet point price is in the second
        multiplier = instr_obj.meta_data.SpreadBetMultiplier
        cols = {'fPrice': sim.daily_prices(instr)}
        price_frame = pd.DataFrame(cols)
        price_frame['sbPrice'] = price_frame['fPrice'] * multiplier
        f_price = price_frame['fPrice'].iloc[-1]
        av_f_price = price_frame['fPrice'].tail(100).mean()
        sb_price = price_frame['sbPrice'].iloc[-1]
        av_sb_price = price_frame['sbPrice'].tail(100).mean()

        #f_price = sim.daily_prices(instr).tail(100).mean()
        #sb_price = f_price * instr_obj.meta_data.SpreadBetMultiplier
        #print(instr_obj.meta_data.SpreadBetMultiplier)
        #print(type(instr_obj.meta_data.SpreadBetMultiplier))
        # instr_obj.meta_data.SpreadBetMultiplier
        spread_in_points = 2 * instr_obj.meta_data.Slippage
        min_bet_per_point = instr_obj.meta_data.MinBetPerPoint
        point_size = instr_obj.meta_data.BetPointSize
        tc_ccy = (spread_in_points * min_bet_per_point) / 2
        tc_ratio = 100 * (tc_ccy / ((min_bet_per_point * sb_price) / point_size))

        # calculating volatility as per 'Leveraged Trading' Appendix C, p.313
        #daily_price = sim.daily_prices(instr)
        last_date = price_frame.index[-100]
        #last_date = daily_price.loc[:'2019-12-17']
        #start_date = last_date - pd.DateOffset(years=1)
        start_date = last_date - pd.DateOffset(days=25)
        average_price = float(price_frame['sbPrice'][start_date:].mean())
        #daily_vol = rawdata.daily_returns_volatility(instr)
        daily_vol = rawdata.daily_returns_volatility_mult(instr, int(instr_obj.meta_data.SpreadBetMultiplier))
        average_vol = float(daily_vol[start_date:].mean())
        avg_annual_vol = average_vol * ROOT_BDAYS_INYEAR
        avg_annual_vol_perc = (avg_annual_vol / average_price) * 100
        tc_risk = tc_ratio / avg_annual_vol_perc

        #hc_ratio = tc_ratio * instr_obj.meta_data.RollsPerYear * 2
        hc_ratio = tc_ratio * roll_count * 2
        hc_risk = hc_ratio / avg_annual_vol_perc
        costs_total = (tc_risk * 5.4) + hc_risk

        #if costs_total < 0.06:
        cost_rows.append(
            {
                'Instr': instr,
                #'Commission': 0,
                'Class': instr_class,
                'Date': date_last_price,
                'FuturesPrice': round(f_price, 4),
                'SpreadbetPrice': round(sb_price, 4),
                'SpreadInPoints': spread_in_points,
                'MinBetPerPoint': min_bet_per_point,
                'Xpoint': point_size,
                'TCccy': f"£{round(tc_ccy, 2)}",
                'TCratio': f"{round(tc_ratio, 4)}%",
                'Vol': f"{round(avg_annual_vol_perc, 4)}%",
                'TCrisk': round(tc_risk, 6),
                'HCratio': round(hc_ratio, 3),
                'HCrisk': round(hc_risk, 3),
                'Ctotal': round(costs_total, 3)
            }
        )

        notional_exposure = (TARGET_RISK * TRADING_CAPITAL) / avg_annual_vol_perc
        min_exposure = (min_bet_per_point * average_price) / point_size
        min_capital = (min_exposure * avg_annual_vol_perc) / TARGET_RISK
        pos_size = (notional_exposure * 1 * point_size) / average_price
        ewmac_series = ewmac_forecast_with_defaults(price_frame['sbPrice'], 16, 64)
        ewmac_today = ewmac_series.iloc[-1] # TODO check date. prices must be up to date
        direction = 'L' if ewmac_today > 0 else 'S'

        # instrument risk in price units
        risk_price_units = (avg_annual_vol_perc / 100) * sb_price
        stop_loss_gap = risk_price_units * STOP_LOSS_FRACTION


        #if costs_total < 0.06 and pos_size > min_bet_per_point:
        #         and TRADING_CAPITAL >= (2 * min_capital):

        position_rows.append(
            {
                'Instr': instr,
                #'Class': instr_class,
                'minExposure': round(min_exposure, 0),
                'minCapital': round(min_capital, 0),
                'notionalExposure': round(notional_exposure, 0),
                'positionSize': round(pos_size, 2),
                'ewmac': round(ewmac_today, 2),
                'dir': direction,
                'riskPriceUnits': risk_price_units,
                'stopLossGap': stop_loss_gap
            }
        )

    pd.set_option('display.max_columns', None)

    do_write = True

    cost_results = pd.DataFrame(cost_rows).sort_values(by='Ctotal') # Ctotal
    write_file(cost_results, 'costs', data_source, write=do_write)

    position_results = pd.DataFrame(position_rows).sort_values(by='Instr')
    write_file(position_results, 'position', data_source, write=do_write)


def write_file(df, calc_type, source, write=True):

    now = datetime.now()
    dir = '/data/cost_calcs'
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
