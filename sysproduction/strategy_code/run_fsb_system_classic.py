"""
this:

- gets capital from the database (earmarked with a strategy name)
- runs a backtest using that capital level, and mongodb data
- gets the final positions and position buffers
- writes these into a table (earmarked with a strategy name)


"""
from syscore.constants import arg_not_supplied

from sysdata.data_blob import dataBlob

from sysobjects.production.tradeable_object import instrumentStrategy
from sysproduction.strategy_code.run_system_classic import (
    runSystemClassic,
    get_position_buffers_from_system,
    construct_position_entry,
    production_classic_futures_system,
)
from sysproduction.data.fsb_instruments import diagFsbInstruments
from sysproduction.data.optimal_positions import dataOptimalPositions

from systems.basesystem import System


class runFsbSystemClassic(runSystemClassic):
    # MODIFY THIS WHEN INHERITING FOR A DIFFERENT STRATEGY
    # ARGUMENTS MUST BE: data: dataBlob, strategy_name: str, system: System
    @property
    def function_to_call_on_update(self):
        return updated_buffered_fsb_positions

    # DO NOT CHANGE THE NAME OF THIS FUNCTION; IT IS HARDCODED INTO CONFIGURATION FILES
    # BECAUSE IT IS ALSO USED TO LOAD BACKTESTS
    def system_method(
        self,
        notional_trading_capital: float = arg_not_supplied,
        base_currency: str = arg_not_supplied,
    ) -> System:
        data = self.data
        backtest_config_filename = self.backtest_config_filename

        system = production_classic_futures_system(
            data,
            backtest_config_filename,
            log=data.log,
            notional_trading_capital=notional_trading_capital,
            base_currency=base_currency,
        )

        return system


def updated_buffered_fsb_positions(data: dataBlob, strategy_name: str, system: System):
    log = data.log

    data_optimal_positions = dataOptimalPositions(data)
    diag_instruments = diagFsbInstruments(data)

    list_of_instruments = system.get_instrument_list()
    for instrument_code in list_of_instruments:
        lower_buffer, upper_buffer = get_position_buffers_from_system(
            system, instrument_code
        )
        position_entry = construct_position_entry(
            data=data,
            system=system,
            instrument_code=instrument_code,
            lower_position=lower_buffer,
            upper_position=upper_buffer,
        )
        instrument_strategy = instrumentStrategy(
            instrument_code=instrument_code, strategy_name=strategy_name
        )
        data_optimal_positions.update_optimal_position_for_instrument_strategy(
            instrument_strategy=instrument_strategy, position_entry=position_entry
        )
        min_bet = diag_instruments.get_minimum_bet(instrument_code, data.log.name)
        log.debug(
            f"New buffered positions {position_entry.lower_position:.2f} "
            f"{position_entry.upper_position:.2f} (min bet: {min_bet})",
            instrument_code=instrument_code,
        )
