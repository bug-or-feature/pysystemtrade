"""
Strategy specific execution code

For the classic buffered strategy we just compare actual positions with optimal positions, and generate orders
  accordingly

These are 'virtual' orders, because they are per instrument. We translate that to actual contracts downstream

Desired virtual orders have to be labelled with the desired type: limit, market,best-execution
"""
from collections import  namedtuple

from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_fsb_instruments import mongoFsbInstrumentData

from sysexecution.orders.instrument_orders import instrumentOrder, best_order_type
from sysexecution.orders.list_of_orders import listOfOrders
from sysexecution.strategies.classic_buffered_positions import orderGeneratorForBufferedPositions

optimalPositions = namedtuple("optimalPositions",  [
            "upper_positions",
            "lower_positions",
            "reference_prices",
            "reference_contracts",
            "ref_dates",
        ])


class FsbOrderGenerator(orderGeneratorForBufferedPositions):
    def get_required_orders(self) -> listOfOrders:
        strategy_name = self.strategy_name

        optimal_positions = self.get_optimal_positions()
        actual_positions = self.get_actual_positions_for_strategy()

        list_of_trades = get_fsb_trades_list(
            self.data, strategy_name, optimal_positions, actual_positions
        )

        return list_of_trades


def get_fsb_trades_list(
    data: dataBlob,
        strategy_name: str,
        optimal_positions: optimalPositions,
        actual_positions: dict
) -> listOfOrders:

    upper_positions = optimal_positions.upper_positions
    list_of_instruments = upper_positions.keys()
    trade_list = [
        trade_fsb(
            data, strategy_name, instrument_code, optimal_positions, actual_positions
        )
        for instrument_code in list_of_instruments
    ]

    trade_list = listOfOrders(trade_list)

    return trade_list


def trade_fsb(
    data: dataBlob,
        strategy_name: str,
        instrument_code: str,
        optimal_positions: optimalPositions,
        actual_positions: dict
) -> instrumentOrder:

    data.add_class_object(mongoFsbInstrumentData)
    instr_data = data.db_fsb_instrument.get_instrument_data(instrument_code)

    upper_for_instrument = optimal_positions.upper_positions[instrument_code]
    lower_for_instrument = optimal_positions.lower_positions[instrument_code]
    mid_for_instrument = (upper_for_instrument + lower_for_instrument) / 2
    min_bet = instr_data.as_dict()['Pointsize']

    actual_for_instrument = actual_positions.get(instrument_code, 0.0)

    if actual_for_instrument < lower_for_instrument:
        if actual_for_instrument == 0.0:
            required_position = mid_for_instrument
        else:
            required_position = lower_for_instrument
    elif actual_for_instrument > upper_for_instrument:
        if actual_for_instrument == 0.0:
            required_position = mid_for_instrument
        else:
            required_position = upper_for_instrument
    else:
        required_position = actual_for_instrument

    # Might seem weird to have a zero order, but since orders can be updated
    # it makes sense

    trade_required = required_position - actual_for_instrument
    # if required_trade is less than minimum bet, make it zero
    if trade_required < min_bet:
        trade_required = 0.0

    reference_contract = optimal_positions.reference_contracts[instrument_code]
    reference_price = optimal_positions.reference_prices[instrument_code]

    ref_date = optimal_positions.ref_dates[instrument_code]

    # No limit orders, just best execution
    order_required = instrumentOrder(
        strategy_name,
        instrument_code,
        trade_required,
        order_type=best_order_type,
        reference_price=reference_price,
        reference_contract=reference_contract,
        reference_datetime=ref_date,
    )

    log = order_required.log_with_attributes(data.log)
    log.msg(
        "Upper %.2f, Lower %.2f, Min %.2f, Curr %.2f, Req pos %.2f, Req trade %.2f, Ref price %f, contract %s" %
        (upper_for_instrument,
         lower_for_instrument,
         min_bet,
         actual_for_instrument,
         required_position,
         trade_required,
         reference_price,
         reference_contract,
         ))

    return order_required
