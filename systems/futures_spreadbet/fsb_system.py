"""
This is a futures spreadbet system

"""
from syscore.objects import arg_not_supplied

from sysdata.config.configdata import Config
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account
from systems.rawdata import RawData


def fsb_system(data=arg_not_supplied, config=arg_not_supplied, trading_rules=arg_not_supplied, log_level="on"):

    """
    :param data: data object (defaults to reading from csv files)
    :type data: sysdata.data.simData, or anything that inherits from it

    :param config: Configuration object (defaults to futuresconfig.yaml in this directory)
    :type config: sysdata.configdata.Config

    :param trading_rules: Set of trading rules to use (defaults to set specified in config object)
    :type trading_rules: list or dict of TradingRules, or something that can be parsed to that

    :param log_level: How much logging to do
    :type log_level: str
    """

    if data is arg_not_supplied:
        data = dbFuturesSimData()

    if config is arg_not_supplied:
        config = Config("systems.futures_spreadbet.config_fsb_system_v1.yaml")

    rules = Rules(trading_rules)

    system = System(
        [
            RawData(),
            Account(),
            Portfolios(),
            PositionSizing(),
            ForecastCombine(),
            ForecastScaleCap(),
            rules
        ],
        data,
        config
    )

    system.set_logging_level(log_level)

    return system


if __name__ == "__main__":
    import doctest

    doctest.testmod()
