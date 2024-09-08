from syscore.exceptions import missingData, spreadTooWide
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_spread_costs import mongoSpreadCostData
from sysexecution.tick_data import tickerObject
from sysexecution.algos.algo import benchmarkPriceCollection
from sysexecution.algos.algo_market import algoMarket
from sysexecution.order_stacks.broker_order_stack import orderWithControls
from sysexecution.orders.contract_orders import contractOrder
from sysexecution.orders.named_order_objects import missing_order


class algoMarketFsb(algoMarket):
    """
    Simplest possible market order execution method for FSBs. Differences:
      - we don't cut down the size
      - we check the spread is not too wide
    """

    def __init__(self, data: dataBlob, contract_order: contractOrder):
        super().__init__(data, contract_order)
        data.add_class_object(mongoSpreadCostData)

    def validate(
        self,
        contract_order: contractOrder,
        ticker_object: tickerObject,
        prices: benchmarkPriceCollection,
    ):
        instr_code = contract_order.instrument_code
        slippage = self.data.db_spread_cost.get_spread_cost(instr_code)
        expected_spread = slippage * 2 * 1.05
        actual_spread = ticker_object.last_tick_analysis.spread
        if actual_spread > expected_spread:
            msg = (
                f"Actual spread ({actual_spread}) for {instr_code} is "
                f"higher than expected ({expected_spread})"
            )
            raise spreadTooWide(msg)

    def prepare_and_submit_trade(self) -> orderWithControls:
        contract_order = self.contract_order

        self.data.log.debug(
            f"Not changing size {str(contract_order.trade)}, we are an FSB",
            **contract_order.log_attributes(),
            method="temp",
        )

        try:
            broker_order_with_controls = (
                self.get_and_submit_broker_order_for_contract_order(
                    contract_order, order_type=self.order_type_to_use
                )
            )
        except missingData as md:
            self.data.log.error(f"Problem submitting order: {md}")
            return missing_order

        return broker_order_with_controls
