from systems.basesystem import System
from syscore.constants import arg_not_supplied
from systems.forecasting import Rules
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import *
from systems.futures_spreadbet.fsb_static_system import build_fsb_csv_sim_data
from systems.portfolio import Portfolios
from systems.positionsizing import PositionSizing
from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import (
    optimisedPositions,
)
from systems.provided.dynamic_small_system_optimise.accounts_stage import (
    accountForOptimisedStage,
)
from systems.rawdata import RawData
from systems.risk import Risk


def fsb_dynamic_system(
    sim_data=arg_not_supplied,
    config_filename="systems.futures_spreadbet.fsb_dynamic_minimal.yaml",
):
    if sim_data is arg_not_supplied:
        # sim_data = dbFuturesSimData()
        sim_data = build_fsb_csv_sim_data()

    config = Config(config_filename)

    system = System(
        [
            Risk(),
            accountForOptimisedStage(),
            optimisedPositions(),
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
