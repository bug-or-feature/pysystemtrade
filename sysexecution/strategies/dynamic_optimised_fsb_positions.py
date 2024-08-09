"""
Strategy specific execution code for FSB dynamic optimised positions
"""
import datetime
from dataclasses import dataclass
from typing import List

from syscore.rounding import RoundingStrategy, get_rounding_strategy
from sysdata.data_blob import dataBlob
from sysexecution.orders.instrument_orders import instrumentOrder, market_order_type
from sysexecution.orders.list_of_orders import listOfOrders
from sysexecution.strategies.dynamic_optimised_positions import (
    orderGeneratorForDynamicPositions,
    get_weights_given_positions,
    get_maximum_position_contracts,
    get_per_contract_values,
    calculate_costs_per_portfolio_weight,
    get_constraints,
    get_covariance_matrix_for_instrument_returns_for_optimisation,
    get_speed_control,
    dataForObjectiveInstance,
)
from sysobjects.production.optimal_positions import (
    optimalPositionWithDynamicFsbCalculations,
)
from sysobjects.production.tradeable_object import instrumentStrategy
from sysproduction.data.optimal_positions import dataOptimalPositions
from sysquant.optimisation.weights import portfolioWeights
from systems.futures_spreadbet.dynamic_small_system_optimise.optimisation import (
    objectiveFsbFunctionForGreedy,
)


class orderGeneratorForDynamicFsbPositions(orderGeneratorForDynamicPositions):
    def get_required_orders(self) -> listOfOrders:
        strategy_name = self.strategy_name

        optimised_positions_data = (
            self.calculate_write_and_return_optimised_positions_data()
        )
        current_positions = self.get_actual_positions_for_strategy()
        self.data.log.debug("Getting minimum bets")
        min_bets = self.get_min_bets_as_dict()

        list_of_trades = list_of_trades_given_optimised_and_actual_positions(
            self.data,
            strategy_name=strategy_name,
            optimised_positions_data=optimised_positions_data,
            current_positions=current_positions,
            min_bets=min_bets,
        )

        return list_of_trades

    def calculate_write_and_return_optimised_positions_data(self) -> dict:
        previous_positions = self.get_actual_positions_for_strategy()
        raw_optimal_position_data = self.get_raw_optimal_position_data()
        min_bets = self.get_min_bets_as_dict()

        optimised_positions_data = calculate_optimised_positions_data(
            self.data,
            strategy_name=self.strategy_name,
            previous_positions=previous_positions,
            raw_optimal_position_data=raw_optimal_position_data,
            min_bets=min_bets,
            rounding_strategy=get_rounding_strategy(self.data.config, True),
        )

        self.write_optimised_positions_data(optimised_positions_data)

        return optimised_positions_data

    def get_min_bets_as_dict(self):
        min_bets = dict(
            [
                (
                    instr,
                    self.diag_instruments.get_minimum_bet(instr),
                )
                for instr in self.diag_instruments.get_list_of_instruments()
            ]
        )
        return min_bets


def calculate_optimised_positions_data(
    data: dataBlob,
    previous_positions: dict,
    strategy_name: str,
    raw_optimal_position_data: dict,
    min_bets: dict,
    rounding_strategy: RoundingStrategy,
) -> dict:
    data_for_objective = get_data_for_objective_instance(
        data,
        strategy_name=strategy_name,
        previous_positions=previous_positions,
        raw_optimal_position_data=raw_optimal_position_data,
        min_bets=min_bets,
        rounding_strategy=rounding_strategy,
    )

    objective_function = get_objective_instance(
        data=data, data_for_objective=data_for_objective
    )

    optimised_positions_data = get_optimised_positions_data_dict_given_optimisation(
        data_for_objective=data_for_objective, objective_function=objective_function
    )

    return optimised_positions_data


@dataclass
class dataForObjectiveFsbInstance(dataForObjectiveInstance):
    min_bets: portfolioWeights
    rounding_strategy: RoundingStrategy


def get_data_for_objective_instance(
    data: dataBlob,
    strategy_name: str,
    previous_positions: dict,
    raw_optimal_position_data: dict,
    min_bets: dict,
    rounding_strategy: RoundingStrategy,
) -> dataForObjectiveFsbInstance:
    list_of_instruments = list(raw_optimal_position_data.keys())
    data.log.debug("Getting data for optimisation")

    previous_positions_as_weights_object = portfolioWeights(previous_positions)
    previous_positions_as_weights_object = (
        previous_positions_as_weights_object.with_zero_weights_for_missing_keys(
            list_of_instruments
        )
    )

    positions_optimal = portfolioWeights(
        [
            (instrument_code, raw_position_entry.optimal_position)
            for instrument_code, raw_position_entry in raw_optimal_position_data.items()
        ]
    )

    reference_prices = dict(
        [
            (instrument_code, raw_position_entry.reference_price)
            for instrument_code, raw_position_entry in raw_optimal_position_data.items()
        ]
    )

    reference_contracts = dict(
        [
            (instrument_code, raw_position_entry.reference_contract)
            for instrument_code, raw_position_entry in raw_optimal_position_data.items()
        ]
    )

    reference_dates = dict(
        [
            (instrument_code, raw_position_entry.reference_date)
            for instrument_code, raw_position_entry in raw_optimal_position_data.items()
        ]
    )

    data.log.debug("Getting maximum positions")
    maximum_position_contracts = get_maximum_position_contracts(
        data, strategy_name=strategy_name, list_of_instruments=list_of_instruments
    )

    data.log.debug("Getting per contract values")
    per_contract_value = get_per_contract_values(
        data, strategy_name=strategy_name, list_of_instruments=list_of_instruments
    )

    data.log.debug("Getting costs")
    costs = calculate_costs_per_portfolio_weight(
        data,
        per_contract_value=per_contract_value,
        strategy_name=strategy_name,
        list_of_instruments=list_of_instruments,
    )

    constraints = get_constraints(
        data, strategy_name=strategy_name, list_of_instruments=list_of_instruments
    )

    data.log.debug("Getting covariance matrix")
    covariance_matrix = get_covariance_matrix_for_instrument_returns_for_optimisation(
        data, list_of_instruments=list_of_instruments
    )

    speed_control = get_speed_control(data)

    data_for_objective = dataForObjectiveFsbInstance(
        positions_optimal=positions_optimal,
        per_contract_value=per_contract_value,
        covariance_matrix=covariance_matrix,
        costs=costs,
        reference_dates=reference_dates,
        reference_prices=reference_prices,
        reference_contracts=reference_contracts,
        previous_positions=previous_positions_as_weights_object,
        maximum_position_contracts=maximum_position_contracts,
        constraints=constraints,
        speed_control=speed_control,
        min_bets=portfolioWeights(min_bets),
        rounding_strategy=rounding_strategy,
    )

    return data_for_objective


def get_objective_instance(
    data: dataBlob, data_for_objective: dataForObjectiveFsbInstance
) -> objectiveFsbFunctionForGreedy:
    objective_function = objectiveFsbFunctionForGreedy(
        log=data.log,
        contracts_optimal=data_for_objective.positions_optimal,
        covariance_matrix=data_for_objective.covariance_matrix,
        costs=data_for_objective.costs,
        speed_control=data_for_objective.speed_control,
        previous_positions=data_for_objective.previous_positions,
        constraints=data_for_objective.constraints,
        maximum_positions=data_for_objective.maximum_position_contracts,
        per_contract_value=data_for_objective.per_contract_value,
        min_bets=data_for_objective.min_bets,
        rounding_strategy=data_for_objective.rounding_strategy,
    )

    return objective_function


def get_optimised_positions_data_dict_given_optimisation(
    data_for_objective: dataForObjectiveFsbInstance,
    objective_function: objectiveFsbFunctionForGreedy,
) -> dict:
    optimised_positions = objective_function.optimise_positions()

    optimised_position_weights = get_weights_given_positions(
        optimised_positions,
        per_contract_value=data_for_objective.per_contract_value,
    )
    instrument_list: List[str] = objective_function.keys_with_valid_data

    minima_weights = portfolioWeights.from_weights_and_keys(
        list_of_keys=instrument_list,
        list_of_weights=list(objective_function.minima_as_np),
    )
    maxima_weights = portfolioWeights.from_weights_and_keys(
        list_of_keys=instrument_list,
        list_of_weights=list(objective_function.maxima_as_np),
    )
    starting_weights = portfolioWeights.from_weights_and_keys(
        list_of_keys=instrument_list,
        list_of_weights=list(objective_function.starting_weights_as_np),
    )
    min_bets = data_for_objective.min_bets

    data_dict = dict(
        [
            (
                instrument_code,
                get_optimal_position_entry_with_calcs_for_code(
                    instrument_code=instrument_code,
                    data_for_objective=data_for_objective,
                    optimised_position_weights=optimised_position_weights,
                    optimised_positions=optimised_positions,
                    maxima_weights=maxima_weights,
                    starting_weights=starting_weights,
                    minima_weights=minima_weights,
                    min_bets=min_bets,
                ),
            )
            for instrument_code in instrument_list
        ]
    )

    return data_dict


def get_optimal_position_entry_with_calcs_for_code(
    instrument_code: str,
    data_for_objective: dataForObjectiveFsbInstance,
    optimised_position_weights: portfolioWeights,
    optimised_positions: portfolioWeights,
    minima_weights: portfolioWeights,
    maxima_weights: portfolioWeights,
    starting_weights: portfolioWeights,
    min_bets: dict,
) -> optimalPositionWithDynamicFsbCalculations:
    return optimalPositionWithDynamicFsbCalculations(
        date=datetime.datetime.now(),
        reference_price=data_for_objective.reference_prices[instrument_code],
        reference_contract=data_for_objective.reference_contracts[instrument_code],
        reference_date=data_for_objective.reference_dates[instrument_code],
        optimal_position=data_for_objective.positions_optimal[instrument_code],
        weight_per_contract=data_for_objective.per_contract_value[instrument_code],
        previous_position=data_for_objective.previous_positions[instrument_code],
        previous_weight=data_for_objective.weights_prior[instrument_code],
        reduce_only=instrument_code in data_for_objective.constraints.reduce_only_keys,
        dont_trade=instrument_code in data_for_objective.constraints.no_trade_keys,
        position_limit_contracts=data_for_objective.maximum_position_contracts[
            instrument_code
        ],
        position_limit_weight=data_for_objective.maximum_position_weights[
            instrument_code
        ],
        optimum_weight=data_for_objective.weights_optimal[instrument_code],
        minimum_weight=minima_weights[instrument_code],
        maximum_weight=maxima_weights[instrument_code],
        start_weight=starting_weights[instrument_code],
        optimised_weight=optimised_position_weights[instrument_code],
        optimised_position=optimised_positions[instrument_code],
        min_bet=min_bets[instrument_code],
    )


def write_optimised_positions_data_for_code(
    data: dataBlob,
    strategy_name: str,
    instrument_code: str,
    optimised_position_entry: optimalPositionWithDynamicFsbCalculations,
):
    data_optimal_positions = dataOptimalPositions(data)
    instrument_strategy = instrumentStrategy(
        instrument_code=instrument_code, strategy_name=strategy_name
    )

    data.log.debug(
        f"Updating optimal position for {str(instrument_strategy)}: "
        f"{optimised_position_entry.verbose_repr()}"
    )
    data_optimal_positions.update_optimal_position_for_instrument_strategy(
        instrument_strategy=instrument_strategy, position_entry=optimised_position_entry
    )


def list_of_trades_given_optimised_and_actual_positions(
    data: dataBlob,
    strategy_name: str,
    optimised_positions_data: dict,
    current_positions: dict,
    min_bets: dict,
) -> listOfOrders:
    list_of_instruments = optimised_positions_data.keys()
    trade_list = [
        trade_given_optimal_and_actual_positions(
            data,
            strategy_name=strategy_name,
            instrument_code=instrument_code,
            optimised_position_entry=optimised_positions_data[instrument_code],
            current_position=current_positions.get(instrument_code, 0),
            min_bet=min_bets[instrument_code],
        )
        for instrument_code in list_of_instruments
    ]

    trade_list = listOfOrders(trade_list)

    return trade_list


def trade_given_optimal_and_actual_positions(
    data: dataBlob,
    strategy_name: str,
    instrument_code: str,
    optimised_position_entry: optimalPositionWithDynamicFsbCalculations,
    current_position: float,
    min_bet: float,
) -> instrumentOrder:
    optimised_position = optimised_position_entry.optimised_position

    trade_required = optimised_position - current_position

    reference_contract = optimised_position_entry.reference_contract
    reference_price = optimised_position_entry.reference_price
    reference_date = optimised_position_entry.reference_date

    # market orders for now
    order_required = instrumentOrder(
        strategy_name,
        instrument_code,
        trade_required,
        order_type=market_order_type,
        reference_price=reference_price,
        reference_contract=reference_contract,
        reference_datetime=reference_date,
    )

    data.log.debug(
        f"Current {current_position:.2f}, required {optimised_position:.2f}, "
        f"trade {trade_required:.2f}, min bet {min_bet:.2f}, "
        f"price {reference_price:.2f}, contract {reference_contract}",
        **order_required.log_attributes(),
        method="temp",
    )

    return order_required
