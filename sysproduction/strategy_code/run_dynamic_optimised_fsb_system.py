from syscore.constants import arg_not_supplied
from sysdata.config.configdata import Config
from sysdata.data_blob import dataBlob
from syslogging.logger import *
from sysproduction.data.sim_data import get_sim_data_object_for_production
from sysproduction.strategy_code.run_dynamic_optimised_system import (
    updated_optimal_positions_for_dynamic_system,
)
from sysproduction.strategy_code.run_fsb_system_classic import (
    runFsbSystemClassic,
)
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.forecasting import Rules
from systems.futures_spreadbet.dynamic_small_system_optimise.optimised_fsb_position_stage import (
    optimisedFsbPositions,
)
from systems.portfolio_fsb import FsbPortfolios
from systems.positionsizing import PositionSizing
from systems.provided.dynamic_small_system_optimise.accounts_stage import (
    accountForOptimisedStage,
)
from systems.rawdata import RawData
from systems.risk import Risk


class runFsbSystemCarryTrendDynamic(runFsbSystemClassic):
    # DO NOT CHANGE THE NAME OF THIS FUNCTION; IT IS HARDCODED INTO CONFIGURATION FILES
    # BECAUSE IT IS ALSO USED TO LOAD BACKTESTS
    def system_method(
        self,
        notional_trading_capital: float = arg_not_supplied,
        base_currency: str = arg_not_supplied,
    ) -> System:
        data = self.data
        backtest_config_filename = self.backtest_config_filename

        system = dynamic_fsb_system(
            data,
            backtest_config_filename,
            log=data.log,
            notional_trading_capital=notional_trading_capital,
            base_currency=base_currency,
        )

        return system

    @property
    def function_to_call_on_update(self):
        return updated_optimal_positions_for_dynamic_system


def dynamic_fsb_system(
    data: dataBlob,
    config_filename: str,
    log=get_logger("fsb_system"),
    notional_trading_capital: float = arg_not_supplied,
    base_currency: str = arg_not_supplied,
) -> System:
    sim_data = get_sim_data_object_for_production(data)
    config = Config(config_filename)

    # Overwrite capital and base currency
    if notional_trading_capital is not arg_not_supplied:
        config.notional_trading_capital = notional_trading_capital

    if base_currency is not arg_not_supplied:
        config.base_currency = base_currency

    system = fsb_system(data=sim_data, config=config)
    system._log = log

    return system


def fsb_system(data, config):
    system = System(
        [
            Risk(),
            accountForOptimisedStage(),
            optimisedFsbPositions(),
            FsbPortfolios(),
            PositionSizing(),
            RawData(),
            ForecastCombine(),
            ForecastScaleCap(),
            Rules(),
        ],
        data,
        config,
    )

    return system
