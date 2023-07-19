import datetime


from collections import namedtuple
from dateutil.tz import tz

from ib_insync import Trade as ibTrade
from sysbrokers.IB.ib_contracts import ibcontractWithLegs, ibContract
from sysbrokers.broker_trade import brokerTrade
from syscore.exceptions import missingData
from syscore.constants import arg_not_supplied
from sysexecution.orders.named_order_objects import missing_order
from sysexecution.orders.base_orders import resolve_multi_leg_price_to_single_price

from sysobjects.spot_fx_prices import currencyValue
from sysexecution.orders.broker_orders import brokerOrder
from sysexecution.trade_qty import tradeQuantity


class tradeWithContract(brokerTrade):
    def __init__(self, ibcontract_with_legs: ibcontractWithLegs, trade_object: ibTrade):
        self._ibcontract_with_legs = ibcontract_with_legs
        self._trade = trade_object

    def __repr__(self):
        return str(self.trade) + " " + str(self.ibcontract_with_legs)

    @property
    def ibcontract_with_legs(self) -> ibcontractWithLegs:
        return self._ibcontract_with_legs

    @property
    def trade(self) -> ibTrade:
        return self._trade

    @property
    def ib_instrument_code(self):
        return self.trade.contract.symbol

    @property
    def ib_contract(self) -> ibContract:
        return self.trade.contract
