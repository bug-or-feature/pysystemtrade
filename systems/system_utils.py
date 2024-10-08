import datetime

import pandas as pd
import yaml
from matplotlib.pyplot import show

from syscore.fileutils import resolve_path_and_filename_for_package
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from systems.basesystem import System
from systems.diagoutput import systemDiag


def write_pickle_file(log, system: System, save_path: str):
    log.info(f"Writing pickled system to {save_path}")
    system.cache.pickle(save_path)


def write_estimate_file(log, system, save_dir: str):
    now = datetime.datetime.now()
    sysdiag = systemDiag(system)
    output_file = resolve_path_and_filename_for_package(
        f"{save_dir}.estimate-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    log.info(f"writing estimate params to: {output_file}")
    estimates_needed = [
        "instrument_div_multiplier",
        "forecast_div_multiplier",
        "forecast_scalars",
        "instrument_weights",
        "forecast_weights",
        # "forecast_mapping",
    ]

    sysdiag.yaml_config_with_estimated_parameters(output_file, estimates_needed)


def write_full_config_file(log, system, save_dir: str):
    now = datetime.datetime.now()
    output_file = resolve_path_and_filename_for_package(
        f"systems.futures_spreadbet.full_config-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    log.info(f"writing config to: {output_file}")
    system.config.save(output_file)


def config_from_file(path_string):
    path = resolve_path_and_filename_for_package(path_string)
    with open(path) as file_to_parse:
        config_dict = yaml.load(file_to_parse, Loader=yaml.CLoader)
    return config_dict


def plot_performance(log, system):
    acc_portfolio_percent = system.accounts.portfolio().percent
    log.info(f"Stats: {acc_portfolio_percent.stats()}")
    log.info(f"Stats as %: {acc_portfolio_percent.stats()}\n")
    acc_portfolio_percent.curve().plot(legend=True)
    show()


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


def plot_trading_rule_pnl(system: System):
    for rule in system.rules.trading_rules():
        pnl = system.accounts.pandl_for_trading_rule(rule)
        pnl.plot(title=f"{rule}")
        # pos.tail(1000).plot(title=f"{instr} (min bet {min_bet})")
        show()


def print_per_contract_values(log, system: System):
    for instr in system.portfolio.get_instrument_list():
        min_bet = system.data.get_value_of_block_price_move(instr)
        value_per_contract = system.portfolio.get_baseccy_value_per_contract(instr)[-1]
        per_con_val_as_proportion = (
            system.portfolio.get_per_contract_value_as_proportion_of_capital(instr)[-1]
        )
        notional_pos = system.portfolio.get_notional_position(instr)[-1]
        log.info(
            f"{instr}: {min_bet=}, value_per_min_bet={value_per_contract}, "
            f"min bet value as proportion of capital={per_con_val_as_proportion}, "
            f"notional position={notional_pos}"
        )


def print_system_stats(log, system: System):
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
    # performance["1980-01-01":"1989-12-31"].plot()
    # performance["2020-01-01":].plot()
    show()


def plot_instrument_count_over_time(system: System):
    pos_df = system.optimisedPositions.get_optimised_position_df()
    pos_df["instr_count"] = pos_df.notna().sum(axis=1)
    pos_df["instr_count"].plot(
        title="Instrument count (optimised portfolio)", figsize=(15, 9)
    )
    # pos_df["instr_count"][:"2015-01-01"].plot(title="Instrument count (optimised portfolio)", figsize=(15,9))
    show()
