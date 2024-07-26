import pandas as pd

from sysquant.optimisation.weights import portfolioWeights
from syscore.rounding import SimpleFsbRoundingStrategy, validate_fsb_position_series


class TestRounding:
    MIN_BETS = portfolioWeights(
        dict(
            COPPER_fsb=0.1,  # 0.10
            LEANHOG_fsb=0.1,
            EUA_fsb=0.25,  # 0.25
            GAS_US_fsb=0.5,
            US10_fsb=0.5,  # 0.50
            GOLD_fsb=1.0,  # 1.00
            SP500_fsb=1.0,  # 1.00
            PALLAD_fsb=2.0,  # 2.00
            RUSSELL_fsb=2.0,
            CORN_fsb=10.0,  # 10.00
            VIX_fsb=100.0,  # 100.00
        )
    )

    def test_round_to_fsb(self):
        self.assert_rounding(2.5, 1.0, 1.0, 2.5)
        self.assert_rounding(4.19, 4.1, 0.2, 4.1)
        self.assert_rounding(23.1, 21.0, 5.0, 21.0)
        self.assert_rounding(46.0, 40.0, 10.0, 50.0)

        self.assert_rounding(-2.5, -1.0, 1.0, -2.5)
        self.assert_rounding(-46.0, -40.0, 10.0, -50.0)

        self.assert_rounding(-22.5, 10.0, 10.0, -22.5)
        self.assert_rounding(-2.5, 10.0, 50.0, 10.0)
        self.assert_rounding(-22.5, 10.0, 50.0, -40.0)

    @staticmethod
    def assert_rounding(new_pos, prev_pos, min_bet, exp_pos):
        positions = portfolioWeights({"BLAH": new_pos})
        min_bets = portfolioWeights({"BLAH": min_bet})
        rounded = positions.round_to_fsb(min_bets, portfolioWeights({"BLAH": prev_pos}))
        assert rounded["BLAH"] == exp_pos

    def test_validate_fsb_position_series(self):
        assert validate_fsb_position_series(pd.Series([0.0, 1.0, 2.0]), 1.0)
        assert not validate_fsb_position_series(pd.Series([0.0, 0.05, 0.14]), 0.1)
        assert validate_fsb_position_series(pd.Series([2.0, 1.5, 1.0]), 0.5)
        assert validate_fsb_position_series(pd.Series([2.0, 1.5, 1.0]), 0.5)
        assert validate_fsb_position_series(pd.Series([-2.0, -1.5, -1.0]), 0.5)
        assert not validate_fsb_position_series(pd.Series([-0.25, -1.5, -1.0]), 2.0)
        assert validate_fsb_position_series(pd.Series([0.0, 1.0, 1.0]), 1.0)
        assert validate_fsb_position_series(pd.Series([0.0, -1.0, -1.0]), 1.0)
        assert validate_fsb_position_series(pd.Series([0.0, 0.2, 0.2, 0.3]), 0.2)
        assert validate_fsb_position_series(pd.Series([0.0, -0.2, -0.2, -0.3]), 0.2)

    def test_round_fsb_series(self):
        rs = SimpleFsbRoundingStrategy()

        rounded = rs.round_series(pd.Series([0.0, 0.4, 0.89]), 1.0)
        assert validate_fsb_position_series(rounded, 1.0)
        assert rounded.equals(pd.Series([0.0, 0.0, 1.0]))

        rounded = rs.round_series(pd.Series([0.0, 0.6, 1.2]), 1.0)
        assert validate_fsb_position_series(rounded, 1.0)
        assert rounded.equals(pd.Series([0.0, 1.0, 1.0]))

        rounded = rs.round_series(pd.Series([0.0, 1.0, 1.9]), 1.0)
        assert rounded.equals(pd.Series([0.0, 1.0, 2.0]))

        rounded = rs.round_series(pd.Series([0.0, 1.0, 2.1]), 1.0)
        assert rounded.equals(pd.Series([0.0, 1.0, 2.0]))

        rounded = rs.round_series(pd.Series([0.0, 0.6, 1.3]), 0.5)
        assert validate_fsb_position_series(rounded, 0.5)
        assert rounded.equals(pd.Series([0.0, 0.5, 1.5]))

        rounded = rs.round_series(pd.Series([0.0, 0.5, 0.7]), 0.5)
        assert validate_fsb_position_series(rounded, 0.5)
        assert rounded.equals(pd.Series([0.0, 0.5, 0.5]))

        rounded = rs.round_series(pd.Series([0.0, 0.5, 0.75]), 0.5)
        assert validate_fsb_position_series(rounded, 0.5)
        assert rounded.equals(pd.Series([0.0, 0.5, 1.0]))

        rounded = rs.round_series(pd.Series([0.11, 0.6, 1.31]), 0.2)
        assert validate_fsb_position_series(rounded, 0.2)
        assert rounded.equals(pd.Series([0.2, 0.6, 1.4]))

        rounded = rs.round_series(pd.Series([0.0, 0.2, 0.29]), 0.2)
        assert validate_fsb_position_series(rounded, 0.2)
        assert rounded.equals(pd.Series([0.0, 0.2, 0.2]))

        rounded = rs.round_series(pd.Series([8.0, -5.4, 25.01]), 10.0)
        assert validate_fsb_position_series(rounded, 10.0)
        assert rounded.equals(pd.Series([10.0, -10.0, 30.0]))
