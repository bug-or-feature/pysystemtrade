import logging
import os
import os.path

from systems.futures_spreadbet.fsb_system import fsb_system
from systems.futures.futures_system import futures_system
import pandas as pd
from syscore.pdutils import print_full
from matplotlib.pyplot import show
from systems.diagoutput import systemDiag
from datetime import datetime
from syscore.fileutils import get_filename_for_package
from sysdata.config.production_config import get_production_config, Config
import yaml

FULL_ESTIMATES_ATTRS = [
    "forecast_scalars",
    "forecast_weights",
    "forecast_div_multiplier",
    "forecast_mapping",
    "instrument_weights",
    "instrument_div_multiplier",
]
SLIM_ESTIMATES_ATTRS = ["instrument_weights", "instrument_div_multiplier"]

DEPOSIT_FACTOR_MAP = {
    "Equity": 0.1,
    "Bond": 0.2,
    "FX": 0.05,
    "Metals": 0.1,
    "OilGas": 0.1,
    "Ags": 0.1,
}


def run_system():

    do_fsb = True
    do_estimate = False

    capital = config_from_file("systems.futures_spreadbet.config_capital.yaml")
    # rules = config_from_file("systems.futures_spreadbet.config_rules.yaml")
    rules = config_from_file("systems.futures_spreadbet.config_rules2.yaml")
    ignore = config_from_file("systems.futures_spreadbet.config_ignore.yaml")

    config_files = [rules, capital, ignore]

    if do_fsb:
        if do_estimate:
            estimates = config_from_file(
                "systems.futures_spreadbet.config_estimates.yaml"
            )
            config_files.append(estimates)
        else:
            # config_files.append("systems.futures_spreadbet.config_empty_instruments.yaml")
            # config_files.append("systems.futures_spreadbet.estimate_10_cheap.yaml")
            # config_files.append("systems.futures_spreadbet.estimate_10_cheap_full.yaml")
            config_files.append("systems.futures_spreadbet.config_fsb_system_v1.yaml")
            # config_files.append("systems.futures_spreadbet.config_fsb_system_v2.yaml")
        config = Config(config_files)
        system = fsb_system(config=config)
        # system = fsb_system()
        prod_label = "FSB"
        bet_label = "BetPerPoint"
        type_label = "estimate"
    else:
        config = Config(config_files)
        system = futures_system(config=config)
        prod_label = "FUT"
        bet_label = "NumContracts"
        type_label = "normal"

    # curve_group = system.accounts.portfolio()
    # calc_forecasts(system)
    portfolio = system.accounts.portfolio()
    portfolio_percent = system.accounts.portfolio().percent
    rows = []

    if hasattr(system.config, "instruments"):
        instr_list = system.config.instruments
    elif hasattr(system.config, "instrument_weights"):
        instr_list = system.config.instrument_weights.keys()
    else:
        instr_list = system.get_instrument_list()

    total_cap_req = 0.0

    for instr in instr_list:

        # config
        instr_obj = system.data.get_instrument_meta_data(instr)
        asset_class = instr_obj.meta_data.AssetClass
        spread_in_points = instr_obj.meta_data.Slippage * 2
        min_bet_per_point = instr_obj.meta_data.Pointsize
        # multi = instr_obj.meta_data.Multiplier
        if do_fsb:
            # deposit_factor = instr_obj.meta_data.Margin
            deposit_factor = DEPOSIT_FACTOR_MAP[asset_class]
            # asset_subclass = instr_obj.meta_data.AssetSubclass
        else:
            deposit_factor = "n/a"
            # asset_subclass = "n/a"

        # price
        price = system.rawdata.get_daily_prices(instr).iloc[-1]

        # asset_class = system.rawdata.get_asset_class(instr)
        # spread_in_points = system.rawdata.get_spread(instr)
        # min_bet_per_point = system.rawdata.get_pointsize(instr)
        # multi = system.rawdata.get_multiplier(instr)

        # pos size
        block_val_series = system.positionSize.get_block_value(instr)
        block_val = block_val_series.iloc[-1]
        comb_fc = system.positionSize.get_combined_forecast(instr).iloc[-1]
        instr_cur_vol = system.positionSize.get_instrument_currency_vol(instr).iloc[-1]
        instr_val_vol = system.positionSize.get_instrument_value_vol(instr).iloc[-1]
        vol_scalar = system.positionSize.get_volatility_scalar(instr).iloc[-1]
        subsys_pos = system.positionSize.get_subsystem_position(instr).iloc[-1]

        # portfolio
        pos_at_5 = calc_pos_for_fc(system, instr, 5.0)
        pos_at_10 = calc_pos_for_fc(system, instr, 10.0)
        pos_at_20 = calc_pos_for_fc(system, instr, 20.0)
        notional_position = system.portfolio.get_notional_position(instr).iloc[-1]

        can_trade = abs(notional_position) > min_bet_per_point

        # Bet size x price (in points) x deposit factor (%)
        # if can_trade:
        cap_req = notional_position * price * deposit_factor if can_trade else 0.0
        total_cap_req += cap_req
        # else:
        # cap_req = 0.0

        # accounts
        turnover = system.accounts.subsystem_turnover(instr)
        total_costs = system.accounts.get_SR_cost_given_turnover(instr, turnover)
        pandl = system.accounts.pandl_for_subsystem(instr)
        sharpe = portfolio[instr].annual.sharpe()
        costs_as_percent = (total_costs / sharpe) * 100

        buffers = system.portfolio.get_buffers_for_position(instr)
        lower_buffer = buffers.iloc[-1].bot_pos
        upper_buffer = buffers.iloc[-1].top_pos

        # if do_fsb:
        # ideal_exposure_series = system.positionSize.get_ideal_exposure(instr)
        # ideal_exposure = ideal_exposure_series.iloc[-1]
        # else:
        #    ideal_exposure = 0.0

        rows.append(
            {
                "Instr": instr,
                "Class": asset_class,
                #'Subclass': asset_subclass,
                "Spread": spread_in_points,
                "MinBet": min_bet_per_point,
                #'Deposit%': round(deposit_factor,2),
                #'Multi': multi,
                "Date start": system.rawdata.get_daily_prices(instr).index[0],
                "Date end": system.rawdata.get_daily_prices(instr).index[-1],
                "Price": round(price, 2),
                "DailyVol%": round(
                    system.rawdata.get_daily_percentage_volatility(instr).iloc[-1], 4
                ),
                "AnnVol%": round(
                    system.rawdata.get_daily_percentage_volatility(instr).iloc[-1] * 16,
                    2,
                ),
                "Turnover": round(turnover, 2),
                "Sharpe": round(sharpe, 2),
                "Costs": round(total_costs, 3),
                "Costs as %": round(costs_as_percent, 0),
                #'P&L': round(pandl, 2),
                "Forecast": round(comb_fc, 2),
                "BlockVal": round(block_val, 2),
                #'InstrCurrVol': round(instr_cur_vol, 2),
                #'InstValVol': round(instr_val_vol, 2),
                "VolScalar": round(vol_scalar, 2),
                "SubsysPos": round(subsys_pos, 2),
                "Pos5": round(pos_at_5, 2),
                "Pos10": round(pos_at_10, 2),
                "Pos20": round(pos_at_20, 2),
                bet_label: round(notional_position, 2),
                "Lower": round(lower_buffer, 2),
                "Upper": round(upper_buffer, 2),
                #'IdealExp': round(ideal_exposure, 2),
                "CanTrade": abs(notional_position) > min_bet_per_point,
                "CanTrade5": abs(pos_at_5) > min_bet_per_point,
                "CapReq": round(abs(cap_req), 2),
            }
        )

    # create dataframe
    results = pd.DataFrame(rows)
    results = results.sort_values(by="Costs")  # Ctotal, NMinCap
    write_file(results, type_label, prod_label)

    print(f"\nTotal capital required: £{round(total_cap_req, 2)}\n")
    print(f"\nStats: {portfolio.stats()}\n")
    print(f"\nStats as %: {portfolio_percent.stats()}\n")

    # print(system.portfolio._get_all_subsystem_positions())
    # system.accounts.portfolio().stats()  # see some statistics
    # system.accounts.portfolio().curve().plot()  # plot an account curve
    # system.accounts.portfolio().percent.curve().plot()  # plot an account curve in percentage terms
    # system.accounts.pandl_for_instrument("US10").percent.stats()  # produce % statistics for a 10 year bond
    # system.accounts.pandl_for_instrument_forecast("EDOLLAR", "carry").sharpe()
    # show()

    print(f"\nSharpe: {system.accounts.portfolio().sharpe()}\n")

    # portfolio.curve().plot()
    #portfolio_percent.curve().plot()
    #show()

    if do_estimate:
        write_estimate_file(system)

    return system


def calc_pos_for_fc(system, instrument_code, forecast, instr_weight=0.1):
    pos_at_average = system.positionSize.get_volatility_scalar(instrument_code)
    idm = system.config.instrument_div_multiplier
    pos_at_average_in_system = pos_at_average * instr_weight * idm
    forecast_multiplier = forecast / system.positionSize.avg_abs_forecast()
    pos_final = pos_at_average_in_system.iloc[-1] * forecast_multiplier
    return pos_final


def write_estimate_file(system):
    now = datetime.now()
    sysdiag = systemDiag(system)
    output_file = get_filename_for_package(
        f"systems.futures_spreadbet.estimate-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    print(f"writing to: {output_file}")
    sysdiag.yaml_config_with_estimated_parameters(output_file, FULL_ESTIMATES_ATTRS)


def write_file(df, run_type, product, write=True):
    now = datetime.now()
    dir = "data/run_systems"
    full_path = f"{dir}/run_{run_type}_{product}_{now.strftime('%Y-%m-%d_%H%M%S')}.csv"

    if write:
        try:
            df.to_csv(full_path, date_format="%Y-%m-%dT%H:%M:%S%z")
        except Exception as ex:
            logging.warning(f"Problem with {full_path}: {ex}")

    print(f"\n{product}")
    print(f"\n{print_full(df)}\n")


def config_from_file(path_string):
    path = get_filename_for_package(path_string)
    with open(path) as file_to_parse:
        config_dict = yaml.load(file_to_parse, Loader=yaml.CLoader)
    return config_dict


def get_daily_backtest_path():
    now = datetime.now()
    dir = get_production_config().get_element_or_missing_data(
        "backtest_store_directory"
    )
    return f"{dir}.daily_backtest_{now.strftime('%Y-%m-%d')}.pickle"


def calc_forecasts(system):
    saved_system = get_daily_backtest_path()
    if os.path.isfile(get_filename_for_package(saved_system)):
        system.cache.unpickle(saved_system)
    else:
        for instr in system.portfolio.get_instrument_list(for_instrument_weights=True):
            system.combForecast.get_combined_forecast(instr)
            # system.positionSize.get_subsystem_position(instr)
            # system.accounts.pandl_for_subsystem(instr)
        # save system for later
        system.cache.pickle(saved_system)


if __name__ == "__main__":
    run_system()
