import datetime

import pandas as pd
import yaml
from matplotlib.pyplot import show

from syscore.constants import arg_not_supplied
from syscore.fileutils import resolve_path_and_filename_for_package
from sysdata.config.configdata import Config
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from syslogging.logger import get_logger
from systems.basesystem import System
from systems.diagoutput import systemDiag
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.forecasting import Rules
from systems.futures_spreadbet.dynamic_small_system_optimise.optimised_position_stage import (
    optimisedPositions,
)
from systems.portfolio_fsb import FsbPortfolios
from systems.positionsizing import PositionSizing
from systems.provided.dynamic_small_system_optimise.accounts_stage import (
    accountForOptimisedStage,
)
from systems.rawdata import RawData
from systems.risk import Risk


CONFIG = "systems.futures_spreadbet.config.fsb_do_minimal.yaml"
SAVED_SYSTEM = "systems.futures_spreadbet.pickle.saved-do-system-min.pck"

# CONFIG = "systems.futures_spreadbet.config.fsb_static_system_mid_est.yaml"
# SAVED_SYSTEM = "systems.futures_spreadbet.pickle.saved-do-system-mid.pck"

# CONFIG = "systems.futures_spreadbet.config.fsb_static_system_full_est.yaml"
# SAVED_SYSTEM = "systems.futures_spreadbet.pickle.saved-do-system.pck"

log = get_logger("backtest")


def run_do_system(
    load_pickle=False, write_pickle=False, do_estimate=False, write_config=False
):
    config = Config(CONFIG)
    if load_pickle:
        log.info(f"Loading DO system from {SAVED_SYSTEM}")
        system = fsb_do_system(config=config)
        system.cache.get_items_with_data()
        system.cache.unpickle(SAVED_SYSTEM)
        system.cache.get_items_with_data()
        write_pickle = False
    else:
        log.info(f"Building DO system from {CONFIG}")
        if do_estimate:
            config.use_forecast_div_mult_estimates = True
            config.use_instrument_div_mult_estimates = True
            config.use_forecast_weight_estimates = True
            config.use_instrument_weight_estimates = True
            config.use_forecast_scale_estimates = True
        system = fsb_do_system(config=config)

    # print_per_contract_values(system)
    print_system_stats(system)
    # plot_system_performance(system)

    if write_pickle:
        write_pickle_file(system)
    if do_estimate:
        write_estimate_file(system)
    if write_config:
        write_full_config_file(system)

    return system


def fsb_do_system(
    data=arg_not_supplied,
    config=arg_not_supplied,
    trading_rules=arg_not_supplied,
):
    if data is arg_not_supplied:
        data = build_fsb_db_sim_data()
        # data = build_fsb_csv_sim_data()

    if config is arg_not_supplied:
        config = Config("systems.futures_spreadbet.do_fsb.fsb_do_minimal.yaml")
        config.risk_overlay = arg_not_supplied

    rules = Rules(trading_rules)

    system = System(
        [
            Risk(),
            accountForOptimisedStage(),
            FsbPortfolios(),
            optimisedPositions(),
            PositionSizing(),
            ForecastCombine(),
            ForecastScaleCap(),
            RawData(),
            rules,
        ],
        data,
        config,
    )

    return system


def build_fsb_csv_sim_data():
    return csvFuturesSimData(
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
            csvFxPricesData="data.futures.fx_prices_csv",
            csvFuturesMultiplePricesData="fsb.multiple_prices_csv",
            csvFuturesAdjustedPricesData="fsb.adjusted_prices_csv",
            csvSpreadCostData="fsb.csvconfig",
        )
    )


def build_fsb_db_sim_data():
    return dbFuturesSimData(
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
            csvSpreadCostData="fsb.csvconfig",
        )
    )


def print_per_contract_values(system: System):
    for instr in system.portfolio.get_instrument_list():
        min_bet = system.data.get_value_of_block_price_move(instr)
        value_per_contract = system.portfolio.get_baseccy_value_per_contract(instr)[-1]
        per_con_val_as_proportion = (
            system.portfolio.get_per_contract_value_as_proportion_of_capital(instr)[-1]
        )
        notional_pos = system.portfolio.get_notional_position(instr)[-1]
        print(
            f"{instr}: {min_bet=}, value_per_min_bet={value_per_contract}, "
            f"min bet value as proportion of capital={per_con_val_as_proportion}, "
            f"notional position={notional_pos}"
        )


def print_system_stats(system: System):
    optimised = system.accounts.optimised_portfolio()
    log.info(f"Stats: {optimised.stats()}")
    opt_portfolio_percent = system.accounts.optimised_portfolio().percent
    log.info(f"% Stats: {opt_portfolio_percent.stats()}")


def plot_system_performance(system: System):
    system.config.use_SR_costs = True
    unrounded = system.accounts.portfolio(roundpositions=False)

    system.config.use_SR_costs = False
    rounded = system.accounts.portfolio()
    optimised = system.accounts.optimised_portfolio()

    performance = pd.concat(
        [unrounded.curve(), rounded.curve(), optimised.curve()], axis=1
    )
    performance.columns = [
        "unrounded",
        "rounded",
        "optimised",
    ]
    performance.plot(figsize=(15, 9))
    # performance.tail(1500).plot(figsize=(15, 9))
    # performance["1984-09-18":].plot()
    # performance["1980-01-01":"1989-12-31"].plot()
    # performance["1990-01-01":"1999-12-31"].plot()
    # performance["2000-01-01":"2009-12-31"].plot()
    # performance["2010-01-01":"2019-12-31"].plot()
    # performance["2020-01-01":].plot()
    show()


def write_pickle_file(system):
    log.info(f"Writing pickled system to {SAVED_SYSTEM}")
    system.cache.pickle(SAVED_SYSTEM)


def write_estimate_file(system):
    now = datetime.datetime.now()
    sysdiag = systemDiag(system)
    output_file = resolve_path_and_filename_for_package(
        f"systems.futures_spreadbet.estimate-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    print(f"writing estimate params to: {output_file}")
    estimates_needed = [
        "instrument_div_multiplier",
        "forecast_div_multiplier",
        "forecast_scalars",
        "instrument_weights",
        "forecast_weights",
        # "forecast_mapping",
    ]

    sysdiag.yaml_config_with_estimated_parameters(output_file, estimates_needed)


def write_full_config_file(system):
    now = datetime.datetime.now()
    output_file = resolve_path_and_filename_for_package(
        f"systems.futures_spreadbet.full_config-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    print(f"writing config to: {output_file}")
    system.config.save(output_file)


def config_from_file(path_string):
    path = resolve_path_and_filename_for_package(path_string)
    with open(path) as file_to_parse:
        config_dict = yaml.load(file_to_parse, Loader=yaml.CLoader)
    return config_dict


if __name__ == "__main__":
    # run_system(load_pickle=True)
    # run_system()
    # run_system(do_estimate=True)
    run_do_system(
        load_pickle=False, write_pickle=True, do_estimate=False, write_config=False
    )

# system = fsb_dynamic_system()
# print(system.accounts.portfolio().percent.stats())

# Yes those are before buffering and the algo

# After buffering (static system):
# system.accounts.get_buffered_position( instrument_code, roundpositions=True)
# After greedy algo (dynamic system):
# system.optimisedPositions.get_optimised_position_df()

# Note in production I don't do this - I run the buffering and or greedy algo on the unrounded positions,
# taking into account my actual live current positions, rather than what the backtest thought it had on yesterday

#
