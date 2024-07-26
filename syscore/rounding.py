from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
import numpy as np


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

    def round_weights(
        self, weights: dict, prev: dict = None, min_bets: dict = None
    ) -> dict:
        """
        Default implementation does no rounding

        :param weights: input weights (dict)
        :param prev: optional previous positions (dict)
        :param min_bets: optional minimum bets (dict)
        :return: rounded weights (dict)
        """
        return weights


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

    def round_weights(
        self, weights: dict, prev: dict = None, min_bets: dict = None
    ) -> dict:
        """
        Round a dict of optimal positions to integer contracts

        We do the rounding to avoid floating point errors even though these should be
        integer values of float type

        :param weights: input weights
        :param prev: optional previous positions (dict)
        :param min_bets: optional minimum bets (dict)
        :return: rounded weights (dict)
        """
        new_weights_as_dict = dict(
            [
                (instrument_code, self._int_from_nan(np.round(value)))
                for instrument_code, value in weights.items()
            ]
        )

        return new_weights_as_dict

    @staticmethod
    def _int_from_nan(x: float):
        if np.isnan(x):
            return 0
        else:
            return int(x)


def get_rounding_strategy(roundpositions: bool = False) -> RoundingStrategy:
    """
    Obtain a RoundingStrategy instance

    :param roundpositions: whether to round (bool)
    :return: RoundingStrategy instance
    """
    if roundpositions:
        return FuturesRoundingStrategy()

    return NoRoundingStrategy()
