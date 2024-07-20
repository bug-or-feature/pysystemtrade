from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class RoundingStrategy(ABC):
    """
    Abstract base class for position rounding strategies
    """

    @abstractmethod
    def round_series(
        self, positions: pd.Series, min_bet: Optional[float] = None
    ) -> pd.Series:
        """
        Round a series of positions
        :param positions: input positions (pd.Series)
        :param min_bet: optional minimum bet (float)
        :return: rounded positions (pd.Series)
        """
        pass


class NoRoundingStrategy(RoundingStrategy):
    """
    No-op RoundingStrategy implementation - does nothing
    """

    def round_series(self, positions: pd.Series, min_bet: Optional[float] = None):
        """
        Returns positions unchanged
        :param positions: input positions (pd.Series)
        :param min_bet: optional minimum bet (float)
        :return: rounded positions (pd.Series)
        """
        return positions


class FuturesRoundingStrategy(RoundingStrategy):
    """
    RoundingStrategy implementation for Futures - rounds positions to whole contract
    numbers
    """

    def round_series(self, positions: pd.Series, min_bet: Optional[float] = None):
        """
        Round a series of Futures positions - converts to whole contract numbers
        :param positions: input positions (pd.Series)
        :param min_bet: optional minimum bet (float)
        :return: rounded positions (pd.Series)
        """
        return positions.round()


def get_rounding_strategy(roundpositions: bool) -> RoundingStrategy:
    """
    Obtain a RoundingStrategy instance

    :param roundpositions: whether to round (bool)
    :return: RoundingStrategy instance
    """
    if roundpositions:
        return FuturesRoundingStrategy()

    return NoRoundingStrategy()
