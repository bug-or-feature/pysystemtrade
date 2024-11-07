from sysdata.config.configdata import Config
from syslogging.logger import get_logger
from systems.futures_spreadbet.fsb_static_system import fsb_static_system
from systems.system_utils import (
    write_pickle_file,
    write_estimate_file,
    write_full_config_file,
    plot_performance,
)

# CONFIG = "systems.futures_spreadbet.config.fsb_static_minimal.yaml"
# SAVED_SYSTEM = "systems.futures_spreadbet.pickle.fsb_static_minimal.pck"

# SAVED_SYSTEM = "systems.futures_spreadbet.saved-system.pck"
# CONFIG = "systems.futures_spreadbet.config.fsb_static_system_full_est.yaml"

# CONFIG = "systems.futures_spreadbet.config.fsb_static_system_mid_est.yaml"
# SAVED_SYSTEM = "systems.futures_spreadbet.config.fsb_static_system_mid_est.pck"

CONFIG = "systems.futures_spreadbet.config.fsb_static_estimation.yaml"
# CONFIG = "systems.futures_spreadbet.config.fsb_static_estimation_redux.yaml"
SAVED_SYSTEM = "systems.futures_spreadbet.pickle.fsb_static_estimation.pck"

log = get_logger("backtest")


def run_system(
    load_pickle=False, write_pickle=False, do_estimate=False, write_config=False
):
    if load_pickle:
        log.info(f"Loading system from {SAVED_SYSTEM}")
        system = fsb_static_system()
        system.cache.get_items_with_data()
        system.cache.unpickle(SAVED_SYSTEM)
        system.cache.get_items_with_data()
        write_pickle = False
    else:
        log.info(f"Building system from {CONFIG}")
        config = Config(CONFIG)
        if do_estimate:
            config.use_forecast_div_mult_estimates = True
            config.use_instrument_div_mult_estimates = True
            config.use_forecast_weight_estimates = True
            config.use_instrument_weight_estimates = True
            config.use_forecast_scale_estimates = True
        system = fsb_static_system(config=config)
        system.config.exclude_instrument_lists["bad_markets"] = []
        # log.info(f"Config: {system.config}")

    plot_performance(log, system)

    # raw_weights = system.portfolio.get_unsmoothed_raw_instrument_weights()
    #
    # # weights = (
    # #     system.portfolio.get_unsmoothed_instrument_weights_fitted_to_position_lengths()
    # # )

    if write_pickle:
        write_pickle_file(log, system, SAVED_SYSTEM)
    if do_estimate:
        write_estimate_file(log, system, "systems.futures_spreadbet.config")
    if write_config:
        write_full_config_file(log, system, "systems.futures_spreadbet.config")

    return system


if __name__ == "__main__":
    # run_system(load_pickle=True)
    # run_system()
    # run_system(do_estimate=True)
    run_system(
        load_pickle=False, write_pickle=False, do_estimate=True, write_config=False
    )
