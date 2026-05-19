import builtins
from unittest.mock import MagicMock, patch

from ib_async import Contract, Order, OrderStatus, Trade

from sysbrokers.IB.ib_connection import connectionIB
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
from sysproduction.interactive_order_stack import view_broker_order_list

ACCOUNT = "DU123456"


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


def make_mock_ib(ib_trades: list, instrument_code: str = "SP500_micro") -> MagicMock:
    mock_ib = MagicMock()
    mock_ib.sleep.return_value = None
    mock_ib.reqAllOpenOrders.return_value = None
    mock_ib.trades.return_value = ib_trades

    # reqContractDetails powers the symbol → instrument_code lookup (IB config file).
    ib_data = get_instrument_object_from_config(instrument_code).ib_data
    mock_cd = MagicMock()
    mock_cd.contract.symbol = ib_data.symbol
    mock_cd.contract.multiplier = str(ib_data.ibMultiplier)
    mock_cd.contract.exchange = ib_data.exchange
    mock_cd.validExchanges = ib_data.exchange
    mock_ib.reqContractDetails.return_value = [mock_cd]

    return mock_ib


def build_data(
    ib_trades: list,
    stored_order: ibOrderWithControls = None,
    instrument_code: str = "SP500_micro",
) -> dataBlob:
    mock_ib = make_mock_ib(ib_trades, instrument_code=instrument_code)

    mock_conn = MagicMock(spec=connectionIB)
    mock_conn.ib = mock_ib
    mock_conn.account = ACCOUNT

    data = dataBlob(ib_conn=mock_conn)
    data.add_class_list(get_ib_class_list())

    if stored_order is not None:
        data.broker_execution_stack._traded_object_store = {
            stored_order.order.broker_tempid: stored_order
        }

    return data


def make_stored_order(ib_trade: Trade, instrument_code: str = "SP500_micro") -> ibOrderWithControls:
    trade_with_contract = tradeWithContract(
        ibcontractWithLegs(ib_trade.contract, legs=[]), ib_trade
    )
    broker_order = create_broker_order_from_trade_with_contract(
        trade_with_contract, instrument_code
    )
    return ibOrderWithControls(
        trade_with_contract,
        ibclient=MagicMock(),
        broker_order=broker_order,
    )


def printed_lines(data: dataBlob) -> list:
    with patch.object(builtins, "print") as mock_print:
        view_broker_order_list(data)

    return [str(call.args[0]) for call in mock_print.call_args_list]