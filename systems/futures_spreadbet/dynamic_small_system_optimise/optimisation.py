from typing import Callable

import numpy as np

from syscore.constants import arg_not_supplied
from syscore.rounding import RoundingStrategy
from syslogging.logger import *

from sysquant.estimators.covariance import covarianceEstimate
from sysquant.estimators.mean_estimator import meanEstimates
from sysquant.optimisation.weights import portfolioWeights
from systems.provided.dynamic_small_system_optimise.optimisation import (
    constraintsForDynamicOpt,
)
from systems.provided.dynamic_small_system_optimise.buffering import (
    speedControlForDynamicOpt,
    calculate_adjustment_factor,
)
from systems.futures_spreadbet.dynamic_small_system_optimise.buffering import (
    adjust_weights_with_factor,
)
from systems.futures_spreadbet.dynamic_small_system_optimise.data_for_fsb_optimisation import (
    dataForFsbOptimisation,
)
from systems.provided.dynamic_small_system_optimise.optimisation import (
    objectiveFunctionForGreedy,
)


class objectiveFsbFunctionForGreedy(objectiveFunctionForGreedy):
    def __init__(
        self,
        contracts_optimal: portfolioWeights,
        covariance_matrix: covarianceEstimate,
        per_contract_value: portfolioWeights,
        costs: meanEstimates,
        speed_control: speedControlForDynamicOpt,
        min_bets: portfolioWeights,
        previous_positions: portfolioWeights = arg_not_supplied,
        constraints: constraintsForDynamicOpt = arg_not_supplied,
        maximum_positions: portfolioWeights = arg_not_supplied,
        log=get_logger("objectiveFsbFunctionForGreedy"),
        constraint_function: Callable = arg_not_supplied,
        rounding_strategy: RoundingStrategy = arg_not_supplied,
    ):
        super().__init__(
            contracts_optimal,
            covariance_matrix,
            per_contract_value,
            costs,
            speed_control,
            previous_positions,
            constraints,
            maximum_positions,
            log,
            constraint_function,
            rounding_strategy,
        )

        self.min_bets = min_bets

    def optimise_positions(self) -> portfolioWeights:
        optimal_weights = self.optimise_weights()
        optimal_positions = optimal_weights / self.per_contract_value
        # self.log.debug(f"%%% unrounded: {self.non_zero(optimal_positions)}")

        rounded_optimal_positions = portfolioWeights(
            self.rounding_strategy.round_weights(
                optimal_positions,
                self.previous_positions,
                self.min_bets,
            )
        )

        # self.log.debug(f"%%% rounded: {self.non_zero(rounded_optimal_positions)}")
        return rounded_optimal_positions

    @staticmethod
    def non_zero(weights):
        non_zero_weights = {k: v for k, v in weights.items() if v < 0.0 or v > 0.0}
        return non_zero_weights

    def adjust_weights_for_size_of_tracking_error(
        self, optimised_weights_as_np: np.array
    ) -> np.array:
        if self.no_prior_positions_provided:
            return optimised_weights_as_np

        prior_weights_as_np = self.weights_prior_as_np_replace_nans_with_zeros
        tracking_error_of_prior = self.tracking_error_against_passed_weights(
            prior_weights_as_np, optimised_weights_as_np
        )
        speed_control = self.speed_control
        per_contract_value_as_np = self.per_contract_value_as_np

        adj_factor = calculate_adjustment_factor(
            tracking_error_of_prior=tracking_error_of_prior, speed_control=speed_control
        )

        self.log.debug(
            "Tracking error current vs optimised %.4f vs buffer %.4f doing %.3f of adjusting trades (0 means no trade)"
            % (tracking_error_of_prior, speed_control.tracking_error_buffer, adj_factor)
        )

        if adj_factor <= 0:
            return prior_weights_as_np

        new_optimal_weights_as_np = adjust_weights_with_factor(
            optimised_weights_as_np=optimised_weights_as_np,
            adj_factor=adj_factor,
            per_contract_value_as_np=per_contract_value_as_np,
            prior_weights_as_np=prior_weights_as_np,
            min_bets_as_np=self.min_bets_as_np,
        )

        return new_optimal_weights_as_np

    @property
    def min_bets_as_np(self) -> np.array:
        return self.input_data.min_bets_as_np

    @property
    def labels_as_np(self) -> np.array:
        return self.input_data.labels_as_np

    @property
    def input_data(self):
        input_data = getattr(self, "_input_data", None)
        if input_data is None:
            input_data = dataForFsbOptimisation(self)
            self._input_data = input_data

        return input_data
