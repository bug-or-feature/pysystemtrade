from syscore.constants import arg_not_supplied
from sysdata.config.configdata import Config
from syslogging.logger import get_logger
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.forecasting import Rules
from systems.futures_spreadbet.dynamic_small_system_optimise.optimised_fsb_position_stage import (
    optimisedFsbPositions,
)
from systems.portfolio_fsb import FsbPortfolios
from systems.positionsizing import PositionSizing
from systems.provided.dynamic_small_system_optimise.accounts_stage import (
    accountForOptimisedStage,
)
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.risk import Risk
from systems.system_utils import (
    write_pickle_file,
    write_estimate_file,
    write_full_config_file,
    build_fsb_db_sim_data,
    print_per_contract_values,
    print_system_stats,
    plot_system_performance,
    plot_instrument_count_over_time,
    plot_trading_rule_pnl,
)

# min
# CONFIG = "systems.futures_spreadbet.config.fsb_do_minimal.yaml"
# SAVED_SYSTEM = "systems.futures_spreadbet.pickle.fsb_do_minimal.pck"

CONFIG = "systems.futures_spreadbet.config.fsb_dynamic_system_v1_2.yaml"
SAVED_SYSTEM = "systems.futures_spreadbet.pickle.fsb_dynamic_system_v1_2.pck"

# CONFIG = "systems.futures_spreadbet.config.fsb_dynamic_system_v1_6.yaml"
# SAVED_SYSTEM = "systems.futures_spreadbet.pickle.fsb_dynamic_system_v1_6.pck"


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

    # print_per_contract_values(log, system)
    print_system_stats(log, system)
    plot_system_performance(system)

    if write_pickle:
        write_pickle_file(log, system, SAVED_SYSTEM)
    if do_estimate:
        write_estimate_file(log, system, "systems.futures_spreadbet.config")
    if write_config:
        write_full_config_file(log, system, "systems.futures_spreadbet.config")

    # plot_instrument_count_over_time(system)
    # plot_trading_rule_pnl(system)


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

    rules = Rules(trading_rules)

    system = System(
        [
            Risk(),
            accountForOptimisedStage(),
            optimisedFsbPositions(),
            FsbPortfolios(),
            PositionSizing(),
            myFuturesRawData(),
            ForecastCombine(),
            ForecastScaleCap(),
            Rules(),
        ],
        data,
        config,
    )

    return system


if __name__ == "__main__":
    run_do_system(
        load_pickle=False, write_pickle=True, do_estimate=False, write_config=False
    )
