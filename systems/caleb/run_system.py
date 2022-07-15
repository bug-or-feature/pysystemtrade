from datetime import datetime

from syscore.fileutils import get_filename_for_package

from sysdata.config.production_config import Config
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from systems.diagoutput import systemDiag
from matplotlib.pyplot import show



# from systems.caleb.run_system import *
# system = static_system()
# portfolio = system.accounts.portfolio()
# print(portfolio.percent.stats())
# write_system(system)
def static_system():
    from systems.provided.futures_chapter15.basesystem import futures_system
    system = futures_system(
        data=dbFuturesSimData(),
        config=Config("systems.caleb.simple_config.yaml")
    )
    return system


# from systems.caleb.run_system import *
# system = do_system()
# portfolio = system.accounts.optimised_portfolio()
# print(portfolio.percent.stats())
# write_system(system)
def do_system():
    from sysproduction.strategy_code.run_dynamic_optimised_system import futures_system
    system = futures_system(
        data=dbFuturesSimData(),
        #data=csvFuturesSimData(),
        #config=Config("systems.caleb.estimate_config.yaml")
        #config=Config("systems.caleb.simple_config.yaml")
        config=Config("systems.caleb.andy_strategy_v1.yaml")
    )
    return system


def write_config(system):
    now = datetime.now()
    sysdiag = systemDiag(system)
    output_file = get_filename_for_package(
        f"systems.caleb.estimate-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    print(f"writing estimate params to: {output_file}")
    sysdiag.yaml_config_with_estimated_parameters(
        output_file,
        [
            "forecast_scalars",
            "forecast_weights",
            "forecast_div_multiplier",
            "forecast_mapping",
            "instrument_weights",
            "instrument_div_multiplier",
        ]
    )


def run_dynamic():
    system = do_system()
    portfolio = system.accounts.optimised_portfolio()
    print(portfolio.percent.stats())
    portfolio.curve().plot()
    write_config(system)
    show()

if __name__ == "__main__":
    #static_system()
    run_dynamic()
