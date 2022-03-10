"""
import matplotlib
matplotlib.use("TkAgg")
"""
from syscore.objects import arg_not_supplied

# from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.provided.rob_system.forecastScaleCap import volAttenForecastScaleCap
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import (
    optimisedPositions,
)
from systems.risk import Risk
from systems.provided.dynamic_small_system_optimise.accounts_stage import (
    accountForOptimisedStage,
)


def futures_system(
    sim_data=arg_not_supplied, config_filename="systems.provided.rob_system.config.yaml"
):

    if sim_data is arg_not_supplied:
        sim_data = dbFuturesSimData()

    config = Config(config_filename)

    system = System(
        [
            Risk(), # think OK as is. maybe change roundings?
            accountForOptimisedStage(), # should be OK as is. maybe?
            optimisedPositions(),
                # original_position_contracts_for_relevant_date()
                #
            Portfolios(),
                # get_position_contracts_for_relevant_date()
                # get_per_contract_value()
                # get_per_contract_value_as_proportion_of_capital_df()
                # get_position_contracts_as_df()
                # get_portfolio_weight_series_from_contract_positions()
                # get_per_contract_value_as_proportion_of_capital()
                # get_baseccy_value_per_contract()
                # get_portfolio_weights_from_contract_positions()
            PositionSizing(),
            myFuturesRawData(),
            ForecastCombine(),
            volAttenForecastScaleCap(),
            Rules(),
        ],
        sim_data,
        config,
    )
    system.set_logging_level("on")

    return system

