from sysbrokers.IB.ib_contracts import ibcontractWithLegs
from sysbrokers.IB.ib_translate_broker_order_objects import (
    create_broker_order_from_trade_with_contract,
    tradeWithContract,
)
from sysproduction.interactive_order_stack import view_broker_order_list
from sysproduction.tests.broker_test_utils import (
    data,  # pytest fixture
    make_ib_trade,
    make_stored_order,
)


class TestViewBrokerOrderList:
    def test_live_order_printed_with_str_repr(self, data, capsys):
        """The live order line matches brokerOrder.__str__."""
        ib_trade = make_ib_trade()
        view_broker_order_list(data(trades=[ib_trade]))
        output = capsys.readouterr().out

        trade_with_contract = tradeWithContract(
            ibcontractWithLegs(ib_trade.contract, legs=[]), ib_trade
        )
        expected = str(
            create_broker_order_from_trade_with_contract(
                trade_with_contract, "SP500_micro"
            )
        )
        assert expected in output

    def test_stored_order_printed_with_full_repr(self, data, capsys):
        """Stored orders are printed using full_repr(), which includes order_info."""
        ib_trade = make_ib_trade()
        stored = make_stored_order(ib_trade)
        view_broker_order_list(data(stored_order=stored))
        output = capsys.readouterr().out

        assert stored.order.full_repr() in output

    def test_live_order_uses_str_not_full_repr(self, data, capsys):
        """Live orders are printed with str(), not full_repr() — the shorter form."""
        ib_trade = make_ib_trade()
        view_broker_order_list(data(trades=[ib_trade]))
        output = capsys.readouterr().out

        trade_with_contract = tradeWithContract(
            ibcontractWithLegs(ib_trade.contract, legs=[]), ib_trade
        )
        broker_order = create_broker_order_from_trade_with_contract(
            trade_with_contract, "SP500_micro"
        )
        assert str(broker_order) in output
        assert broker_order.full_repr() not in output

    def test_empty_ib_response_prints_no_orders(self, data, capsys):
        """No order lines when IB returns nothing and there are no stored orders."""
        view_broker_order_list(data())
        output = capsys.readouterr().out

        assert "Order ID" not in output

    def test_order_filtered_by_account(self, data, capsys):
        """Orders belonging to a different account are silently dropped."""
        wrong_account_trade = make_ib_trade(account="WRONG_ACCOUNT")
        view_broker_order_list(data(trades=[wrong_account_trade]))
        output = capsys.readouterr().out

        assert "Order ID" not in output

    def test_section_headers_always_printed(self, data, capsys):
        """Both section headers are printed regardless of whether orders exist."""
        view_broker_order_list(data())
        output = capsys.readouterr().out

        assert "Orders received from broker API" in output
        assert "Stored" in output
