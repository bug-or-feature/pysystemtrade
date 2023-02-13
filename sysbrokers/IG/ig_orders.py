from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_execution_stack import brokerExecutionStackData
from syscore.constants import arg_not_supplied
from sysdata.data_blob import dataBlob
from sysdata.futures.contracts import futuresContractData
from sysdata.futures.instruments import futuresInstrumentData
from sysexecution.order_stacks.broker_order_stack import orderWithControls
from sysexecution.orders.base_orders import Order
from sysexecution.orders.broker_orders import brokerOrder
from sysexecution.orders.list_of_orders import listOfOrders
from sysexecution.tick_data import tickerObject
from syslogdiag.log_to_screen import logtoscreen


class IgOrderWithControls(orderWithControls):
    def __init__(
        self,
        control_object,
        broker_order: brokerOrder = None,
        ticker_object: tickerObject = None,
    ):
        super().__init__(broker_order, control_object, ticker_object)

    @property
    def trade_with_contract_from_ig(self):
        return self._control_object

    def update_order(self):
        pass

    def broker_limit_price(self):
        pass


class IgExecutionStackData(brokerExecutionStackData):
    def __init__(
        self,
        data_blob: dataBlob,
        broker_conn: IGConnection,
        log=logtoscreen("IgExecutionStackData"),
    ):
        super().__init__(log=log)
        self._dataBlob = data_blob
        self._broker_conn = broker_conn

    def __repr__(self):
        return f"IG orders {self.broker_conn}"

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

    @property
    def data(self):
        return self._dataBlob

    @property
    def traded_object_store(self) -> dict:
        store = getattr(self, "_traded_object_store", None)
        if store is None:
            store = self._traded_object_store = {}

        return store

    def _add_order_with_controls_to_store(
        self, order_with_controls: IgOrderWithControls
    ):
        storage_key = order_with_controls.order.broker_tempid
        self.traded_object_store[storage_key] = order_with_controls

    @property
    def futures_contract_data(self) -> futuresContractData:
        return self.data.broker_futures_contract

    @property
    def futures_instrument_data(self) -> futuresInstrumentData:
        return self.data.broker_futures_instrument

    def get_list_of_broker_orders_with_account_id(
        self, account_id: str = arg_not_supplied
    ) -> listOfOrders:
        pass

    def _create_broker_control_order_object(self, trade_with_contract_from_ib):
        pass

    def get_list_of_orders_from_storage(self) -> listOfOrders:
        pass

    def cancel_order_on_stack(self, broker_order: brokerOrder):
        pass

    def cancel_order_given_control_object(
        self, broker_orders_with_controls: IgOrderWithControls
    ):
        pass

    def check_order_is_cancelled(self, broker_order: brokerOrder) -> bool:
        pass

    def check_order_is_cancelled_given_control_object(
        self, broker_order_with_controls: IgOrderWithControls
    ) -> bool:
        pass

    def check_order_can_be_modified_given_control_object(
        self, broker_order_with_controls: IgOrderWithControls
    ) -> bool:
        pass

    def modify_limit_price_given_control_object(
        self, broker_order_with_controls: IgOrderWithControls, new_limit_price: float
    ) -> IgOrderWithControls:
        pass

    def _get_list_of_all_order_ids(self) -> list:
        pass

    def _remove_order_with_id_from_stack_no_checking(self, order_id: int):
        pass

    def _change_order_on_stack_no_checking(self, order_id: int, order: Order):
        pass

    def _put_order_on_stack_no_checking(self, order: Order):
        pass

    def _get_next_order_id(self):
        pass

    def match_db_broker_order_to_order_from_brokers(
        self, broker_order_to_match: brokerOrder
    ) -> brokerOrder:
        pass
