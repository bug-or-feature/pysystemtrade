"""
FSB strategy specific order generation code

For the FSB buffered strategy we just compare actual positions with optimal positions, and minimum bets, and generate
orders accordingly

These are 'virtual' orders, because they are per instrument. We translate that to actual contracts downstream

"""
from collections import namedtuple

from sysdata.data_blob import dataBlob
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData

from sysexecution.orders.instrument_orders import instrumentOrder, market_order_type
from sysexecution.orders.list_of_orders import listOfOrders
from sysexecution.strategies.classic_buffered_positions import (
    orderGeneratorForBufferedPositions,
)
from sysexecution.strategies.classic_buffered_positions import optimalPositions


MIN_BET_DEMO_OVERRIDES = {
    "CAD_fsb": 0.5,
    "EUA_fsb": 0.5,
    "COPPER_fsb": 0.5,
    "CRUDE_W_fsb": 0.5,
    "EUROSTX_fsb": 0.5,
    "GOLD_fsb": 0.5,
    "HANG_fsb": 0.5,
}


class FsbOrderGenerator(orderGeneratorForBufferedPositions):
    def get_required_orders(self) -> listOfOrders:
        strategy_name = self.strategy_name

        optimal_positions = self.get_optimal_positions()
        actual_positions = self.get_actual_positions_for_strategy()

        list_of_trades = list_of_fsb_trades_given_optimal_and_actual_positions(
            self.data, strategy_name, optimal_positions, actual_positions
        )

        return list_of_trades


def list_of_fsb_trades_given_optimal_and_actual_positions(
    data: dataBlob,
    strategy_name: str,
    optimal_positions: optimalPositions,
    actual_positions: dict,
) -> listOfOrders:

    upper_positions = optimal_positions.upper_positions
    list_of_instruments = upper_positions.keys()
    trade_list = [
        fsb_trade_given_optimal_and_actual_positions(
            data, strategy_name, instrument_code, optimal_positions, actual_positions
        )
        for instrument_code in list_of_instruments
    ]

    trade_list = listOfOrders(trade_list)

    return trade_list


def fsb_trade_given_optimal_and_actual_positions(
    data: dataBlob,
    strategy_name: str,
    instrument_code: str,
    optimal_positions: optimalPositions,
    actual_positions: dict,
) -> instrumentOrder:

    data.add_class_object(csvFuturesInstrumentData)
    instr_data = data.db_futures_instrument.get_instrument_data(instrument_code)

    upper = optimal_positions.upper_positions[instrument_code]
    lower = optimal_positions.lower_positions[instrument_code]
    min_bet = instr_data.as_dict()["Pointsize"]
    if instrument_code in MIN_BET_DEMO_OVERRIDES:
        min_bet = MIN_BET_DEMO_OVERRIDES[instrument_code]

    current = actual_positions.get(instrument_code, 0.0)

    # TODO get buffer strategy from config?
    if current < lower:
        required_position = lower
    elif current > upper:
        required_position = upper
    else:
        required_position = current

    # Might seem weird to have a zero order, but since orders can be updated
    # it makes sense

    trade_required = required_position - current
    # if required_trade is less than minimum bet, make it zero
    if abs(trade_required) < min_bet:
        trade_required = 0.0

    reference_contract = optimal_positions.reference_contracts[instrument_code]
    reference_price = optimal_positions.reference_prices[instrument_code]

    ref_date = optimal_positions.ref_dates[instrument_code]

    # simple market orders for now
    order_required = instrumentOrder(
        strategy_name,
        instrument_code,
        trade_required,
        order_type=market_order_type,
        reference_price=reference_price,
        reference_contract=reference_contract,
        reference_datetime=ref_date,
    )

    data.log.debug(
        "Upper %.2f, Lower %.2f, Min %.2f, Curr %.2f, Req pos %.2f, Req trade %.2f, Ref price %f, contract %s"
        % (
            upper,
            lower,
            min_bet,
            current,
            required_position,
            trade_required,
            reference_price,
            reference_contract,
        ),
        **order_required.log_attributes(),
        method="temp",
    )

    return order_required
