from syscore.constants import arg_not_supplied
from sysdata.config.configdata import Config
from sysdata.csv.csv_spread_costs import csvSpreadCostData
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from syslogging.logger import get_logger
from systems.accounts.accounts_stage import Account
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.provided.attenuate_vol.vol_attenuation_forecast_scale_cap import (
    volAttenForecastScaleCap,
)
from systems.forecasting import Rules
from systems.portfolio import Portfolios
from systems.positionsizing import PositionSizing
from systems.risk import Risk
from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import (
    optimisedPositions,
)
from systems.provided.dynamic_small_system_optimise.accounts_stage import (
    accountForOptimisedStage,
)
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.system_utils import (
    write_pickle_file,
    write_estimate_file,
    write_full_config_file,
    plot_performance,
)

# CONFIG = "systems.bof.config.fut_strategy_minimal.yaml"
# SAVED_SYSTEM = "systems.bof.pickle.fut_strategy_v1_0.pck"

# CONFIG = "systems.bof.config.fut_simple_test.yaml"
# CONFIG = "systems.bof.config.fut_strategy_v1_8.yaml"
CONFIG = "systems.bof.config.fut_strategy_v1_9.yaml"

# SAVED_SYSTEM = "systems.bof.config.fut_simple_test.pck"
SAVED_SYSTEM = "systems.bof.config.fut_strategy_v1_9.pck"

# CONFIG = "systems.bof.config.futures_static_estimation_min.yaml"
# CONFIG = "systems.bof.config.futures_static_estimation.yaml"
# SAVED_SYSTEM = "systems.bof.pickle.futures_static_estimation.pck"

log = get_logger("backtest")


def run_static_system(
    load_pickle=False, write_pickle=False, do_estimate=False, write_config=False
):
    if load_pickle:
        log.info(f"Loading STATIC system from {SAVED_SYSTEM}")
        system = futures_static_system()
        system.cache.get_items_with_data()
        system.cache.unpickle(SAVED_SYSTEM)
        system.cache.get_items_with_data()
        write_pickle = False
    else:
        log.info(f"Building STATIC system from {CONFIG}")
        config = Config(CONFIG)
        config.percentage_vol_target = 25.0
        config.notional_trading_capital = 500000
        if do_estimate:
            config.start_date = "1950-01-01"
            config.base_currency = "USD"  # so we're not restricted by FX history

            # forecast scalars
            #config.forecast_scalars = None
            config.use_forecast_scale_estimates = False

            # forecast weights
            #config.forecast_weights = None
            config.use_forecast_weight_estimates = False

            # forecast diversification multiplier
            config.forecast_div_multiplier = None
            config.use_forecast_div_mult_estimates = True

            # instrument weights
            config.instrument_weights = None
            config.use_instrument_weight_estimates = False

            # instrument diversification multiplier
            config.instrument_div_multiplier = None
            config.use_instrument_div_mult_estimates = False

            config.forecast_post_ceiling_cost_SR = 999

            # risk overlay
            config.risk_overlay = dict(
                max_risk_fraction_normal_risk=9999999999.0,
                max_risk_fraction_stdev_risk=9999999999.0,
                max_risk_limit_sum_abs_risk=9999999999.0,
                max_risk_leverage=9999999999.0,
            )

            # excluded
            config.exclude_instrument_lists = dict(
                duplicate_instruments=["ETHANOL"],
                ignore_instruments=[
                    "BB3M",
                    "GAS_NL",
                    "GAS_UK",
                    "NICKEL_LME",
                    "RUR",
                    "VNKI",
                ],
                trading_restrictions=[],
            )

            # duplicates
            config.duplicate_instruments = dict(
                include=dict(),
                exclude=dict(),
            )
            # config.allocate_zero_instrument_weights_to_these_instruments = ["ETHANOL"]
            config.allocate_zero_instrument_weights_to_these_instruments = []
        system = futures_static_system(config=config)

        log.info(f"Config: {system.config}")

    plot_performance(log, system)

    if write_pickle:
        write_pickle_file(log, system, SAVED_SYSTEM)
    if do_estimate:
        write_estimate_file(log, system, "systems.bof.config")
    if write_config:
        write_full_config_file(log, system, "systems.bof.config")

    return system


def run_dynamic_system(
    load_pickle=False, write_pickle=False, do_estimate=False, write_config=False
):
    config = Config(CONFIG)
    if load_pickle:
        log.info(f"Loading DO system from {SAVED_SYSTEM}")
        system = futures_do_system(config=config)
        system.cache.get_items_with_data()
        system.cache.unpickle(SAVED_SYSTEM)
        system.cache.get_items_with_data()
        write_pickle = False
    else:
        log.info(f"Building DO system from {CONFIG}")
        config.percentage_vol_target = 25.0
        config.notional_trading_capital = 200000
        config.start_date = "2020-01-01"
        # config.start_date = "1970-01-01"
        config.base_currency = "USD"  # so we're not restricted by FX history
        system = futures_do_system(config=config)

    plot_performance(log, system, optimised=True)

    if write_pickle:
        write_pickle_file(log, system, SAVED_SYSTEM)
    if do_estimate:
        write_estimate_file(log, system, "systems.bof.config")
    if write_config:
        write_full_config_file(log, system, "systems.bof.config")

    return system


def futures_static_system(
    data=arg_not_supplied,
    config=arg_not_supplied,
    trading_rules=arg_not_supplied,
):
    if data is arg_not_supplied:
        data = dbFuturesSimData()
        # data = csvFuturesSimData()

    if config is arg_not_supplied:
        config = Config("systems.bof.futures_static_system_v1_0.yaml")

    if trading_rules is arg_not_supplied:
        rules = Rules()
    else:
        rules = Rules(trading_rules)

    system = System(
        [
            Account(),
            Portfolios(),
            PositionSizing(),
            myFuturesRawData(),
            ForecastCombine(),
            ForecastScaleCap(),
            rules,
        ],
        data,
        config,
    )

    return system


def futures_do_system(
    data=arg_not_supplied,
    config=arg_not_supplied,
    trading_rules=arg_not_supplied,
):
    if data is arg_not_supplied:
        data = dbFuturesSimData()
        # data = csvFuturesSimData()

    if config is arg_not_supplied:
        config = Config("systems.bof.fut_strategy_v1_0.yaml")

    if trading_rules is arg_not_supplied:
        rules = Rules()
    else:
        rules = Rules(trading_rules)

    system = System(
        [
            Risk(),
            accountForOptimisedStage(),
            optimisedPositions(),
            Portfolios(),
            PositionSizing(),
            myFuturesRawData(),
            ForecastCombine(),
            volAttenForecastScaleCap(),
            rules,
        ],
        data,
        config,
    )

    return system


def check_no_costs():
    spread_costs = csvSpreadCostData()
    config = Config(CONFIG)
    system = futures_do_system(config=config)
    for instr in system.get_instrument_list():
        spread = spread_costs.get_spread_cost(instr)
        if spread == 0.0:
            print(f"%%%%% {instr}: {spread} %%%%%")
        else:
            print(f"{instr}: {spread}")


if __name__ == "__main__":
    run_static_system(
        load_pickle=False, write_pickle=False, do_estimate=True, write_config=False
    )

    # run_dynamic_system(
    #     load_pickle=False, write_pickle=True, do_estimate=False, write_config=False
    # )

    # check_no_costs()
