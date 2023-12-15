from sysexecution.algos.algo_market import algoMarket
from sysexecution.order_stacks.broker_order_stack import orderWithControls
from sysexecution.orders.named_order_objects import missing_order
from syscore.exceptions import missingData


class algoMarketFsb(algoMarket):
    """
    Simplest possible market order execution method for FSBs. The only difference
    with the standard market algo is that we don't cut down the size
    """

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
