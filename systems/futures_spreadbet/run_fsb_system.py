from datetime import datetime

from syscore.fileutils import resolve_path_and_filename_for_package

from sysdata.config.production_config import Config
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from systems.diagoutput import systemDiag
from matplotlib.pyplot import show

from systems.futures_spreadbet.fsb_static_system import fsb_static_system
from systems.futures_spreadbet.fsb_dynamic_system import fsb_dynamic_system

SAVED_SYSTEM = "systems.futures_spreadbet.saved-system.pck"


def run_static():
    system = fsb_static_system(
        # data=csvFuturesSimData(),
        config=Config("systems.futures_spreadbet.fsb_static_system_v5_1.yaml"),
    )
    portfolio = system.accounts.portfolio()
    print(portfolio.percent.stats())
    portfolio.curve().plot()
    write_config(system)
    # write_pickle_file(system)
    show()


def run_dynamic():
    system = fsb_dynamic_system()
    portfolio = system.accounts.optimised_portfolio()
    print(portfolio.percent.stats())
    portfolio.curve().plot()
    write_pickle_file(system)
    # write_config(system)
    # system.accounts.portfolio().percent.stats()
    # system.optimisedPositions.get_optimised_position_df()
    # system.accounts.optimised_portfolio().costs.percent.ann_mean()
    # system.accounts.optimised_portfolio().gross.percent.curve()
    show()


def run_saved_dynamic():
    system = fsb_static_system()
    print(f"Loading system from {SAVED_SYSTEM}")
    system.cache.get_items_with_data()
    system.cache.unpickle(SAVED_SYSTEM)
    system.cache.get_items_with_data()

    portfolio = system.accounts.optimised_portfolio()

    print(portfolio.percent.stats())
    portfolio.curve().plot()
    # write_config(system)
    # system.accounts.portfolio().percent.stats()
    # system.optimisedPositions.get_optimised_position_df()
    # system.accounts.optimised_portfolio().costs.percent.ann_mean()
    # system.accounts.optimised_portfolio().gross.percent.curve()
    show()


def debug_single_instrument(instr):
    system = fsb_static_system()
    system.cache.unpickle(SAVED_SYSTEM)
    instr_pnl = system.accounts.pandl_for_instrument(instr)
    ss_pnl = system.accounts.pandl_for_subsystem("AEX_fsb")
    print(instr_pnl.stats())
    print(ss_pnl.stats())


def write_config(system):
    now = datetime.now()
    sysdiag = systemDiag(system)
    output_file = resolve_path_and_filename_for_package(
        f"systems.futures_spreadbet.estimate-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    print(f"writing estimate params to: {output_file}")
    sysdiag.yaml_config_with_estimated_parameters(
        output_file,
        [
            # "forecast_mapping",
            # "forecast_scalars",
            # "forecast_weights",
            # "instrument_weights",
            "forecast_div_multiplier",
            "instrument_div_multiplier",
        ],
    )


def write_pickle_file(system):
    print(f"Writing pickled system to {SAVED_SYSTEM}")
    system.cache.pickle(SAVED_SYSTEM)


if __name__ == "__main__":
    run_static()
    # run_dynamic()
    # run_saved_dynamic()
    # debug_single_instrument("AEX_fsb")
