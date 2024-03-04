from syscore.constants import arg_not_supplied

# from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.rawdata import RawData
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account


def fsb_system(
    sim_data=arg_not_supplied,
    config_filename="systems.futures_spreadbet.fsb_static_optimisation_system.yaml",
    # config_filename="systems.futures_spreadbet.fsb_static_optimisation_system.yaml",
):
    """
    This only exists to provide a system for static optimisation. It's an adaptation
    of /systems/provided/rob_system/run_system.py
    """

    if sim_data is arg_not_supplied:
        sim_data = dbFuturesSimData(
            csv_data_paths=dict(
                csvFuturesInstrumentData="fsb.csvconfig",
                csvRollParametersData="fsb.csvconfig",
                csvSpreadCostData="fsb.csvconfig",
            )
        )

    config = Config(config_filename)

    system = System(
        [
            Account(),
            Portfolios(),
            PositionSizing(),
            RawData(),
            ForecastCombine(),
            ForecastScaleCap(),
            Rules(),
        ],
        sim_data,
        config,
    )

    return system
