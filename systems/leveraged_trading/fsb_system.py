"""
This is a futures spreadbet system

"""
from syscore.objects import arg_not_supplied

from sysdata.config.configdata import Config
from sysdata.sim.db_fsb_sim_data import dbFsbSimData
from systems.futures_spreadbet.rawdata import FuturesSpreadbetRawData
from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account


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

    >>> from systems.leveraged_trading.fsb_system import fsb_system
    >>> system=fsb_system(log_level="off")
    >>> system
    System with stages: accounts, portfolio, positionSize, rawdata, combForecast, forecastScaleCap, rules
    >>> system.rules.get_raw_forecast("GOLD", "smac16_64").tail(20)
                ewmac2_8
    1983-10-10  0.695929
    1983-10-11 -0.604704

                ewmac2_8
    2015-04-21  0.172416
    2015-04-22 -0.477559
    >>> system.rules.get_raw_forecast("EDOLLAR", "carry").dropna().head(2)
                   carry
    1983-10-10  0.952297
    1983-10-11  0.854075

                   carry
    2015-04-21  0.350892
    2015-04-22  0.350892
    """

    if data is arg_not_supplied:
        data = dbFsbSimData()

    if config is arg_not_supplied:
        config = Config("systems.leveraged_trading.leveraged_trading_config.yaml")

    rules = Rules(trading_rules)

    system = System(
        [
            FuturesSpreadbetRawData(),
            Account(),
            Portfolios(),
            PositionSizing(),
            ForecastCombine(),
            ForecastScaleCap(),
            rules,
        ],
        data,
        config
    )

    system.set_logging_level(log_level)

    return system


if __name__ == "__main__":
    import doctest

    doctest.testmod()
