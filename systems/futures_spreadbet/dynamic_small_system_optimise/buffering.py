import numpy as np


def adjust_weights_with_factor(
    optimised_weights_as_np: np.array,
    prior_weights_as_np: np.array,
    per_contract_value_as_np: np.array,
    adj_factor: float,
    min_bets_as_np: np.array,
):
    desired_trades_weight_space = optimised_weights_as_np - prior_weights_as_np
    adjusted_trades_weight_space = adj_factor * desired_trades_weight_space

    rounded_adjusted_trades_as_weights = (
        calculate_adjusting_trades_rounding_in_minimum_bet_space(
            adjusted_trades_weight_space=adjusted_trades_weight_space,
            per_contract_value_as_np=per_contract_value_as_np,
            min_bets_as_np=min_bets_as_np,
        )
    )

    new_optimal_weights = prior_weights_as_np + rounded_adjusted_trades_as_weights

    return new_optimal_weights


def calculate_adjusting_trades_rounding_in_minimum_bet_space(
    adjusted_trades_weight_space: np.array,
    per_contract_value_as_np: np.array,
    min_bets_as_np: np.array
) -> np.array:

    # convert weights to positions
    adj_trades = adjusted_trades_weight_space / per_contract_value_as_np

    # adjusted trades that are less than half the min_bet become zero
    down_mask = np.abs(adj_trades) < (min_bets_as_np / 2)
    adj_trades[down_mask] = 0.0

    # adjusted trades that are less than min_bet and more than half min_bet
    # become min_bet
    up_mask = (adj_trades < min_bets_as_np) & (adj_trades >= (min_bets_as_np / 2))
    adj_trades[up_mask] = min_bets_as_np[up_mask]

    # round to 2 decimal places
    rounded_adjusted_trades = np.round(adj_trades, 2)

    # convert positions back to weights
    rounded_adjusted_trades_as_weights = (
        rounded_adjusted_trades * per_contract_value_as_np
    )

    return rounded_adjusted_trades_as_weights
