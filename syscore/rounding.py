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


class SimpleFsbRoundingStrategy(RoundingStrategy):
    """
    Simple RoundingStrategy implementation for FSBs; round to nearest multiple of
    minimum bet
    """

    def round_series(self, positions: pd.Series, min_bet: Optional[float] = None):
        """
        Round a series of FSB positions

        :param positions: input positions (pd.Series)
        :param min_bet: optional minimum bet (float)
        :return: rounded positions (pd.Series)
        """

        rounded = np.round(np.round(positions / min_bet) * min_bet, 2)
        # print(f"\n{rounded}")
        return rounded


class FancyFsbRoundingStrategy(RoundingStrategy):
    """
    Fancy RoundingStrategy implementation for FSBs
    """

    def round_series(self, positions: pd.Series, min_bet: Optional[float] = None):
        """
        Round a series of FSB positions

        :param positions: input positions (pd.Series)
        :param min_bet: optional minimum bet (float)
        :return: rounded positions (pd.Series)
        """

        positions = positions.ffill().bfill()

        prev_diff = np.abs(positions.diff()).round(2)
        next_diff = np.abs(positions.diff(periods=-1)).round(2)

        # mask for positions that need to be rounded up
        up_mask = (prev_diff.lt(min_bet)) & (prev_diff.ge(min_bet / 2)) & (next_diff > min_bet)

        # round up
        positions.loc[up_mask] = positions.shift() + min_bet

        # re-evaluate for changes
        prev_diff = np.abs(positions.diff()).round(2)

        # mask for positions that need to be rounded down
        down_mask = prev_diff.lt(min_bet)

        # round down
        positions[down_mask] = np.nan
        positions = positions.ffill()

        print(f"\n{positions}")

        return positions

    @staticmethod
    def _new_custom_round(value, min_bet):
        multiplier = 1 / min_bet

        if min_bet and min_bet != 1.0:
            value = value * 1 / min_bet

        value = round(value)

        if min_bet and min_bet != 1.0:
            value = value / multiplier

        return value


def get_rounding_strategy(
    roundpositions: bool = False, instr_code: Optional[str] = None
) -> RoundingStrategy:
    """
    Obtain a RoundingStrategy instance

    :param roundpositions: whether to round (bool)
    :param instr_code: optional instrument code (str)
    :return: RoundingStrategy instance
    """
    if roundpositions:
        if instr_code and instr_code.endswith("_fsb"):
            return SimpleFsbRoundingStrategy()
        return FuturesRoundingStrategy()

    return NoRoundingStrategy()


def validate_fsb_position_series(pos, min_bet):
    # mask out zeros and nan
    mask = (pos.diff().ne(0.0)) & (pos.diff().notna())
    gt_min_bet = pos[mask].abs().ge(min_bet).all()
    return gt_min_bet
