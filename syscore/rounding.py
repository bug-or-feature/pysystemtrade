from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
import numpy as np

from syscore.objects import resolve_function


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

    def round_weights(
        self, weights: dict, prev: dict = None, min_bets: dict = None
    ) -> dict:
        """
        Round a dict of position weights

        :param weights: input weights (dict)
        :param weights: optional previous positions (dict)
        :param weights: optional minimum bets (dict)
        :return: rounded weights (dict)
        """

        new_weights_as_dict = dict(
            [
                (
                    instr,
                    self._round_to_nearest_multiple(val, prev[instr], min_bets[instr]),
                )
                for instr, val in weights.items()
            ]
        )

        return new_weights_as_dict

    @staticmethod
    def _round_down(new_val, prev_val, min_bet):
        """
        Return zero if new value is less than min bet
        """
        diff = round(new_val - prev_val, 2)
        if diff < min_bet:
            return 0.0
        else:
            return round(new_val, 2)

    @staticmethod
    def _round_to_nearest_multiple(new_val, prev_val, min_bet):
        """
        Rounds to nearest multiple of minimum bet
        """
        rounded = round(round(new_val / min_bet) * min_bet, 2)
        return rounded

    @staticmethod
    def _round_to_nearest_penny(new_val, prev_val, min_bet):
        diff_dir = round(new_val - prev_val, 2)
        plus = True if diff_dir >= 0 else False
        if abs(diff_dir) < min_bet:
            if abs(diff_dir) >= min_bet / 2:
                if plus:
                    return round(prev_val + min_bet, 2)
                else:
                    return round(prev_val - min_bet, 2)
            else:
                return prev_val
        return new_val


def get_rounding_strategy(config, roundpositions: bool = False) -> RoundingStrategy:
    """
    Obtain a RoundingStrategy instance. If roundpositions is False, return
    NoRoundingStrategy. Otherwise, look up the classname in config, and return an
    instance of it. Default is FuturesRoundingStrategy

    :param config: config source
    :param roundpositions: whether to round (bool)
    :return: RoundingStrategy instance
    """
    if roundpositions:
        class_name = config.get_element("rounding_strategy")
        rounding_type = resolve_function(class_name)
        return rounding_type()

    return NoRoundingStrategy()


def validate_fsb_position_series(pos, min_bet):
    # mask out zeros and nan
    mask = (pos.diff().ne(0.0)) & (pos.diff().notna())
    gt_min_bet = pos[mask].abs().ge(min_bet).all()
    return gt_min_bet
