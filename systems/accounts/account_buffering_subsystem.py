import pandas as pd

from syscore.pandas.strategy_functions import turnover
from systems.system_cache import diagnostic
from systems.buffering import get_buffered_position
from systems.accounts.account_costs import accountCosts


class accountBufferingSubSystemLevel(accountCosts):
    @diagnostic()
    def subsystem_turnover(self, instrument_code: str) -> float:
        positions = self.get_subsystem_position(instrument_code)

        average_position_for_turnover = self.get_average_position_at_subsystem_level(
            instrument_code
        )

        subsystem_turnover = turnover(positions, average_position_for_turnover)

        return subsystem_turnover

    @diagnostic()
    def get_buffered_subsystem_position(
        self, instrument_code: str, roundpositions: bool = True
    ) -> pd.Series:
        """
        Get the buffered position

        :param instrument_code: instrument to get

        :param roundpositions: Round positions to whole contracts
        :type roundpositions: bool

        :returns: Tx1 pd.DataFrame

        >>> from systems.basesystem import System
        >>> from systems.tests.testdata import get_test_object_futures_with_portfolios
        >>> (portfolio, posobject, combobject, capobject, rules, rawdata, data, config)=get_test_object_futures_with_portfolios()
        >>> system=System([portfolio, posobject, combobject, capobject, rules, rawdata, Account()], data, config)
        >>>
        >>> system.accounts.get_buffered_position("EDOLLAR").tail(3)
                    position
        2015-12-09         1
        2015-12-10         1
        2015-12-11         1
        """

        buffered_position = get_buffered_position(
            optimal_position=self.get_subsystem_position(instrument_code),
            pos_buffers=self.get_buffers_for_subsystem_position(instrument_code),
            roundpositions=roundpositions,
            buffer_method=self.config.get_element_or_default("buffer_method", "none"),
            trade_to_edge=self.config.buffer_trade_to_edge,
            log=self.log,
        )

        return buffered_position

    @diagnostic()
    def get_buffers_for_subsystem_position(self, instrument_code: str) -> pd.DataFrame:
        """
        Get the buffered position from a previous module

        :param instrument_code: instrument to get values for
        :type instrument_code: str

        :returns: Tx2 pd.DataFrame: columns top_pos, bot_pos

        KEY INPUT
        """

        return self.parent.positionSize.get_buffers_for_subsystem_position(
            instrument_code
        )
