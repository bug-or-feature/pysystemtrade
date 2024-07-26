import datetime
import yaml
from matplotlib.pyplot import show
from syscore.fileutils import resolve_path_and_filename_for_package
from systems.diagoutput import systemDiag
from systems.futures_spreadbet.fsb_static_system import fsb_static_system
from syslogging.logger import get_logger
from sysdata.config.configdata import Config
from syscore.pdutils import print_full

#CONFIG = "systems.futures_spreadbet.config.fsb_static_minimal.yaml"
#SAVED_SYSTEM = "systems.futures_spreadbet.pickle.fsb_static_minimal.pck"

# SAVED_SYSTEM = "systems.futures_spreadbet.saved-system.pck"
# CONFIG = "systems.futures_spreadbet.config.fsb_static_system_full_est.yaml"

CONFIG = "systems.futures_spreadbet.config.fsb_static_system_mid_est.yaml"
SAVED_SYSTEM = "systems.futures_spreadbet.config.fsb_static_system_mid_est.pck"


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

    acc_portfolio_percent = system.accounts.portfolio().percent

    log.info(f"Stats: {acc_portfolio_percent.stats()}")
    log.info(f"Stats as %: {acc_portfolio_percent.stats()}\n")

    acc_portfolio_percent.curve().plot(legend=True)
    show()

    if write_pickle:
        write_pickle_file(system)
    if do_estimate:
        write_estimate_file(system)
    if write_config:
        write_full_config_file(system)

    return system


def write_pickle_file(system):
    # now = datetime.datetime.now()
    # #f = open("/home/rob/temp.pck", "wb")
    # pickle_file = open(f"systems.futures_spreadbet.system-{now.strftime('%Y-%m-%d_%H%M%S')}.pck", "wb")
    # pickle.dump(all_pandl, pickle_file)
    # pickle_file.close()
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
    run_system(
        load_pickle=False, write_pickle=False, do_estimate=False, write_config=False
    )
