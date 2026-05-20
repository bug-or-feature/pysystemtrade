import pytest
from ib_async import Contract, Order, OrderStatus, Trade

from sysbrokers.IB.client.ib_client import ibClient
from sysbrokers.IB.ib_contracts import ibcontractWithLegs
from sysbrokers.IB.ib_instruments import ib_futures_instrument
from sysbrokers.IB.ib_orders import ibOrderWithControls
from sysbrokers.IB.ib_translate_broker_order_objects import (
    create_broker_order_from_trade_with_contract,
    tradeWithContract,
)
from sysbrokers.IB.config.ib_instrument_config import get_instrument_object_from_config
from sysbrokers.broker_factory import get_ib_class_list
from sysdata.data_blob import dataBlob

ACCOUNT = "DU123456"


class FakeContractInfo:
    def __init__(self, symbol, multiplier, exchange):
        self.symbol = symbol
        self.multiplier = multiplier
        self.exchange = exchange


class FakeContractDetails:
    def __init__(self, symbol, multiplier, exchange):
        self.contract = FakeContractInfo(symbol, multiplier, exchange)
        self.validExchanges = exchange


class FakeIB:
    """Replaces the ib_async.IB network connection. Returns canned responses."""

    def __init__(self, trades: list, instrument_code: str = "SP500_micro"):
        self._trades = trades
        ib_data = get_instrument_object_from_config(instrument_code).ib_data
        self._contract_details = FakeContractDetails(
            symbol=ib_data.symbol,
            multiplier=str(ib_data.ibMultiplier),
            exchange=ib_data.exchange,
        )

    def sleep(self, *args, **kwargs):
        pass

    def reqAllOpenOrders(self):
        pass

    def trades(self):
        return self._trades

    def reqContractDetails(self, *args, **kwargs):
        return [self._contract_details]


class FakeConnection:
    """Replaces connectionIB. Only the account attribute is used in tests."""

    account = ACCOUNT


class FakeIBClient:
    """Replaces ibOrdersClient for stored orders. Only refresh() is called."""

    def refresh(self):
        pass


def make_contract(instrument_code: str, contract_month: str) -> Contract:
    instrument_data = get_instrument_object_from_config(instrument_code)
    ib_data = instrument_data.ib_data
    contract = ib_futures_instrument(instrument_data)
    contract.lastTradeDateOrContractMonth = contract_month
    contract.currency = ib_data.currency
    return contract


def make_ib_trade(
    order_id: int = 42,
    action: str = "BUY",
    qty: float = 2.0,
    account: str = ACCOUNT,
    instrument_code: str = "SP500_micro",
    contract_month: str = "20250600",
) -> Trade:
    order = Order(
        orderId=order_id,
        action=action,
        totalQuantity=qty,
        orderType="MKT",
        account=account,
        permId=999,
        clientId=1,
    )
    return Trade(
        contract=make_contract(instrument_code, contract_month),
        order=order,
        orderStatus=OrderStatus(status="Submitted"),
        fills=[],
        log=[],
    )


def make_stored_order(
    ib_trade: Trade, instrument_code: str = "SP500_micro"
) -> ibOrderWithControls:
    trade_with_contract = tradeWithContract(
        ibcontractWithLegs(ib_trade.contract, legs=[]), ib_trade
    )
    broker_order = create_broker_order_from_trade_with_contract(
        trade_with_contract, instrument_code
    )
    return ibOrderWithControls(
        trade_with_contract,
        ibclient=FakeIBClient(),
        broker_order=broker_order,
    )


@pytest.fixture
def data(monkeypatch):
    """Factory fixture. Call with trades and an optional stored_order to get a
    dataBlob with the IB network layer replaced by FakeIB."""

    def _make(trades=None, instrument_code="SP500_micro", stored_order=None):
        fake_ib = FakeIB(trades or [], instrument_code)
        monkeypatch.setattr(ibClient, "ib", property(lambda self: fake_ib))
        d = dataBlob(ib_conn=FakeConnection())
        d.add_class_list(get_ib_class_list())
        if stored_order is not None:
            d.broker_execution_stack._traded_object_store = {
                stored_order.order.broker_tempid: stored_order
            }
        return d

    return _make
