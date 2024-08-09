import datetime

from syscore.constants import arg_not_supplied
from systems.futures_spreadbet.dynamic_small_system_optimise.optimisation import (
    objectiveFsbFunctionForGreedy,
)

from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import (
    optimisedPositions,
)

from sysquant.optimisation.weights import portfolioWeights


class optimisedFsbPositions(optimisedPositions):
    def get_optimal_positions_with_fixed_contract_values(
        self,
        relevant_date: datetime.datetime = arg_not_supplied,
        previous_positions: portfolioWeights = arg_not_supplied,
        maximum_positions: portfolioWeights = arg_not_supplied,
    ) -> portfolioWeights:
        obj_instance = self._get_optimal_positions_objective_instance(
            relevant_date=relevant_date,
            previous_positions=previous_positions,
            maximum_positions=maximum_positions,
        )

        try:
            optimal_positions = obj_instance.optimise_positions()
        except Exception as e:
            msg = "Error %s when optimising at %s with previous positions %s" % (
                str(e),
                str(relevant_date),
                str(previous_positions),
            )
            print(msg)
            return previous_positions

        return optimal_positions

    def _get_optimal_positions_objective_instance(
        self,
        relevant_date: datetime.datetime = arg_not_supplied,
        previous_positions: portfolioWeights = arg_not_supplied,
        maximum_positions: portfolioWeights = arg_not_supplied,
    ) -> objectiveFsbFunctionForGreedy:
        covariance_matrix = self.get_covariance_matrix(relevant_date=relevant_date)

        per_contract_value = self.get_per_contract_value(relevant_date)
        min_bets = self.get_minimum_bets()
        contracts_optimal = self.original_position_contracts_for_relevant_date(
            relevant_date
        )

        costs = self.get_costs_per_contract_as_proportion_of_capital_all_instruments(
            relevant_date
        )
        speed_control = self.get_speed_control()
        constraints = self.get_constraints()
        rounding_strategy = self.rounding_strategy

        obj_instance = objectiveFsbFunctionForGreedy(
            contracts_optimal=contracts_optimal,
            covariance_matrix=covariance_matrix,
            per_contract_value=per_contract_value,
            min_bets=min_bets,
            previous_positions=previous_positions,
            costs=costs,
            constraints=constraints,
            maximum_positions=maximum_positions,
            speed_control=speed_control,
            rounding_strategy=rounding_strategy,
        )

        return obj_instance

    def get_minimum_bets(self):
        return self.portfolio_stage.get_minimum_bets()
