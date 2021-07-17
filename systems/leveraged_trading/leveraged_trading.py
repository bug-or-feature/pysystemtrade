from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account


def lt_system(data=None, config=None, log_level="on"):
    """
    Emulates the Starter System from the book Leveraged Trading
    """
    if config is None:
        config = Config("systems.leveraged_trading.leveraged_trading_config.yaml")
    if data is None:
        data = csvFuturesSimData()

    system = System(
        [
            Account(),
            Portfolios(),
            PositionSizing(),
            ForecastCombine(),
            ForecastScaleCap(),
            Rules(),
        ],
        data,
        config
    )

    system.set_logging_level(log_level)

    return system
