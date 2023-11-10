"""
FSB strategy specific order generation code

For the FSB buffered strategy we just compare actual positions with optimal positions, and minimum bets, and generate
orders accordingly

These are 'virtual' orders, because they are per instrument. We translate that to actual contracts downstream

"""
from sysdata.data_blob import dataBlob

from sysexecution.orders.instrument_orders import instrumentOrder, market_order_type
from sysexecution.orders.list_of_orders import listOfOrders
from sysexecution.strategies.classic_buffered_positions import (
    orderGeneratorForBufferedPositions,
)
from sysproduction.data.fsb_instruments import diagFsbInstruments


class FsbOrderGenerator(orderGeneratorForBufferedPositions):
    def __init__(self, data: dataBlob, strategy_name: str):
        super().__init__(data, strategy_name)
        self._diag_instruments = diagFsbInstruments(data)

    @property
    def diag_instruments(self):
        return self._diag_instruments

    @property
    def optimals(self):
        return self.get_optimal_positions()

    @property
    def actuals(self):
        return self.get_actual_positions_for_strategy()

    def get_required_orders(self) -> listOfOrders:
        list_of_trades = self.build_list_of_fsb_trades()

        return list_of_trades

    def build_list_of_fsb_trades(self) -> listOfOrders:
        upper_positions = self.optimals.upper_positions
        list_of_instruments = upper_positions.keys()
        trade_list = [
            self.build_fsb_trade(instrument_code)
            for instrument_code in list_of_instruments
        ]

        trade_list = listOfOrders(trade_list)

        return trade_list

    def build_fsb_trade(self, instrument_code: str) -> instrumentOrder:
        upper = self.optimals.upper_positions[instrument_code]
        lower = self.optimals.lower_positions[instrument_code]
        min_bet = self.diag_instruments.get_minimum_bet(instrument_code, self.log.name)
        current = self.actuals.get(instrument_code, 0.0)

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

        reference_contract = self.optimals.reference_contracts[instrument_code]
        reference_price = self.optimals.reference_prices[instrument_code]

        ref_date = self.optimals.ref_dates[instrument_code]

        # simple market orders for now
        order_required = instrumentOrder(
            self.strategy_name,
            instrument_code,
            trade_required,
            order_type=market_order_type,
            reference_price=reference_price,
            reference_contract=reference_contract,
            reference_datetime=ref_date,
        )

        self.data.log.debug(
            "Upper %.2f, Lower %.2f, Min %.2f, Curr %.2f, Req pos %.2f, "
            "Req trade %.2f, Ref price %f, contract %s"
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
