import unittest

from sysbrokers.IB.ib_contracts import ibcontractWithLegs
from sysbrokers.IB.ib_translate_broker_order_objects import (
    create_broker_order_from_trade_with_contract,
    tradeWithContract,
)
from sysproduction.tests.broker_test_utils import (
    build_data,
    make_ib_trade,
    make_stored_order,
    printed_lines,
)


class TestViewBrokerOrderList(unittest.TestCase):
    def test_live_order_printed_with_str_repr(self):
        """The live order line matches brokerOrder.__str__."""
        ib_trade = make_ib_trade()

        # Derive the expected string from the same conversion pipeline
        # that production code uses, so we are testing the full data flow.
        trade_with_contract = tradeWithContract(
            ibcontractWithLegs(ib_trade.contract, legs=[]), ib_trade
        )
        expected = str(
            create_broker_order_from_trade_with_contract(trade_with_contract, "SP500_micro")
        )

        lines = printed_lines(build_data([ib_trade]))

        self.assertIn(expected, lines)

    def test_stored_order_printed_with_full_repr(self):
        """Stored orders are printed using full_repr(), which includes order_info."""
        ib_trade = make_ib_trade()
        stored = make_stored_order(ib_trade)
        expected = stored.order.full_repr()

        lines = printed_lines(build_data([], stored_order=stored))

        self.assertIn(expected, lines)

    def test_live_order_uses_str_not_full_repr(self):
        """Live orders are printed with str(), not full_repr() — the shorter form."""
        ib_trade = make_ib_trade()

        trade_with_contract = tradeWithContract(
            ibcontractWithLegs(ib_trade.contract, legs=[]), ib_trade
        )
        broker_order = create_broker_order_from_trade_with_contract(
            trade_with_contract, "SP500_micro"
        )
        terse = str(broker_order)
        full = broker_order.full_repr()

        lines = printed_lines(build_data([ib_trade]))

        self.assertIn(terse, lines)
        self.assertNotIn(full, lines)

    def test_empty_ib_response_prints_no_orders(self):
        """No order lines when IB returns nothing and there are no stored orders."""
        lines = printed_lines(build_data([]))

        self.assertFalse(any("Order ID" in ln for ln in lines))

    def test_order_filtered_by_account(self):
        """Orders belonging to a different account are silently dropped."""
        wrong_account_trade = make_ib_trade(account="WRONG_ACCOUNT")
        lines = printed_lines(build_data([wrong_account_trade]))

        self.assertFalse(any("Order ID" in ln for ln in lines))

    def test_section_headers_always_printed(self):
        """Both section headers are printed regardless of whether orders exist."""
        lines = printed_lines(build_data([]))

        self.assertTrue(any("Orders received from broker API" in ln for ln in lines))
        self.assertTrue(any("Stored" in ln for ln in lines))


if __name__ == "__main__":
    unittest.main()