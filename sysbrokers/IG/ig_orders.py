from sysbrokers.IB.ib_translate_broker_order_objects import (
    create_broker_order_from_trade_with_contract,
    ibBrokerOrder,
    tradeWithContract,
    ibOrderCouldntCreateException,
)
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
from sysexecution.orders.named_order_objects import missing_order
from sysexecution.tick_data import tickerObject
from syslogging.logger import *


class IgOrderWithControls(orderWithControls):
    def __init__(
        self,
        trade_with_contract_from_ib: tradeWithContract,
        broker_conn: IGConnection,
        broker_order: brokerOrder = None,
        instrument_code: str = None,
        ticker_object: tickerObject = None,
    ):
        if broker_order is None:
            # This might happen if for example we are getting the orders from
            #   IB
            broker_order = create_broker_order_from_trade_with_contract(
                trade_with_contract_from_ib, instrument_code
            )

        super().__init__(
            control_object=trade_with_contract_from_ib,
            broker_order=broker_order,
            ticker_object=ticker_object,
        )

        self._broker_conn = broker_conn

    @property
    def trade_with_contract_from_IB(self):
        return self._control_object

    @property
    def broker_connection(self) -> IGConnection:
        return self._broker_conn

    def update_order(self):
        # Update the broker order using the control object
        # Can be used when first submitted, or when polling objects
        # Basically copies across the details from the control object that are
        # likely to be updated
        # self.ibclient.refresh()
        ib_broker_order = create_broker_order_from_trade_with_contract(
            self.trade_with_contract_from_IB, self.order.instrument_code
        )
        updated_broker_order = add_trade_info_to_broker_order(
            self.order, ib_broker_order
        )

        self._order = updated_broker_order

    def broker_limit_price(self):
        # self.ibclient.refresh()
        ib_broker_order = create_broker_order_from_trade_with_contract(
            self.trade_with_contract_from_IB, self.order.instrument_code
        )
        if ib_broker_order.limit_price == 0.0:
            broker_limit_price = None
        else:
            broker_limit_price = ib_broker_order.limit_price

        return broker_limit_price


class IgExecutionStackData(brokerExecutionStackData):
    def __init__(
        self,
        broker_conn: IGConnection,
        data: dataBlob,
        log=get_logger("IgExecutionStackData"),
    ):
        super().__init__(log=log, data=data)
        self._broker_conn = broker_conn

    def __repr__(self):
        return f"IG orders {self.broker_conn}"

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

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
        raise NotImplementedError("Not implemented! build it now")

    def _get_dict_of_broker_control_orders(
        self, account_id: str = arg_not_supplied
    ) -> dict:
        raise NotImplementedError("Not implemented! build it now")

    def _get_list_of_broker_control_orders(
        self, account_id: str = arg_not_supplied
    ) -> list:
        raise NotImplementedError("Not implemented! build it now")

    def _create_broker_control_order_object(
        self, trade_with_contract_from_ib: tradeWithContract
    ):
        raise NotImplementedError("Not implemented! build it now")

    def get_list_of_orders_from_storage(self) -> listOfOrders:
        dict_of_stored_orders = self._get_dict_of_orders_from_storage()
        list_of_orders = listOfOrders(dict_of_stored_orders.values())

        return list_of_orders

    def _get_dict_of_orders_from_storage(self) -> dict:
        raise NotImplementedError("Not implemented! build it now")

    def _get_dict_of_control_orders_from_storage(self) -> dict:
        raise NotImplementedError("Not implemented! build it now")

    def put_order_on_stack(self, broker_order: brokerOrder) -> IgOrderWithControls:
        """
        :param broker_order: key properties are instrument_code, contract_id, quantity
        :return: ibOrderWithControls or missing_order
        """
        trade_with_contract_from_ib = self._send_broker_order_to_IB(broker_order)
        order_time = datetime.datetime.now()

        if trade_with_contract_from_ib is missing_order:
            return missing_order

        placed_broker_order_with_controls = IgOrderWithControls(
            trade_with_contract_from_ib,
            broker_conn=self.broker_conn,
            broker_order=broker_order,
        )

        placed_broker_order_with_controls.order.submit_datetime = order_time

        # We do this so the tempid is accurate
        placed_broker_order_with_controls.update_order()

        # We do this so we can cancel stuff and get things back more easily
        self._add_order_with_controls_to_store(placed_broker_order_with_controls)

        return placed_broker_order_with_controls

    def _send_broker_order_to_IB(self, broker_order: brokerOrder) -> tradeWithContract:
        """
        :param broker_order: key properties are instrument_code, contract_id, quantity
        :return: tradeWithContract object or missing_order
        """

        log = broker_order.log_with_attributes(self.log)
        log.debug("Going to submit order %s to IG" % str(broker_order))

        trade_list = broker_order.trade
        order_type = broker_order.order_type
        limit_price = broker_order.limit_price
        account_id = broker_order.broker_account

        contract_object = broker_order.futures_contract
        contract_object_with_ib_data = (
            self.futures_contract_data.get_contract_object_with_config_data(
                contract_object
            )
        )

        placed_broker_trade_object = self.broker_conn.broker_submit_order(
            contract_object_with_ib_data,
            trade_list=trade_list,
            account_id=account_id,
            order_type=order_type,
            limit_price=limit_price,
        )
        if placed_broker_trade_object is missing_order:
            log.warning("Couldn't submit order")
            return missing_order

        log.debug("Order submitted to IB")

        return placed_broker_trade_object

    def match_db_broker_order_to_order_from_brokers(
        self, broker_order_to_match: brokerOrder
    ) -> brokerOrder:
        raise NotImplementedError("Not implemented! build it now")

    def match_db_broker_order_to_control_order_from_brokers(
        self, broker_order_to_match: brokerOrder
    ) -> IgOrderWithControls:
        raise NotImplementedError("Not implemented! build it now")

    def cancel_order_on_stack(self, broker_order: brokerOrder):
        raise NotImplementedError("Not implemented! build it now")

    def cancel_order_given_control_object(
        self, broker_orders_with_controls: IgOrderWithControls
    ):
        raise NotImplementedError("Not implemented! build it now")

    def check_order_is_cancelled(self, broker_order: brokerOrder) -> bool:
        raise NotImplementedError("Not implemented! build it now")

    def check_order_is_cancelled_given_control_object(
        self, broker_order_with_controls: IgOrderWithControls
    ) -> bool:
        raise NotImplementedError("Not implemented! build it now")

    def _get_status_for_trade_object(
        self, original_trade_object
    ) -> str:  # was : ibTrade
        raise NotImplementedError("Not implemented! build it now")

    def modify_limit_price_given_control_object(
        self, broker_order_with_controls: IgOrderWithControls, new_limit_price: float
    ) -> IgOrderWithControls:
        raise NotImplementedError("Not implemented! build it now")

    def check_order_can_be_modified_given_control_object_throw_error_if_not(
        self, broker_order_with_controls: IgOrderWithControls
    ):
        raise NotImplementedError("Not implemented! build it now")

    def get_status_for_control_object(
        self, broker_order_with_controls: IgOrderWithControls
    ) -> str:
        raise NotImplementedError("Not implemented! build it now")


def add_trade_info_to_broker_order(
    broker_order: brokerOrder, broker_order_from_trade_object: ibBrokerOrder
) -> brokerOrder:

    new_broker_order = copy(broker_order)
    keys_to_replace = [
        "broker_permid",
        "commission",
        "algo_comment",
        "broker_tempid",
        "leg_filled_price",
    ]

    for key in keys_to_replace:
        new_broker_order._order_info[key] = broker_order_from_trade_object._order_info[
            key
        ]

    broker_order_is_filled = not broker_order_from_trade_object.fill.equals_zero()
    if broker_order_is_filled:
        new_broker_order.fill_order(
            broker_order_from_trade_object.fill,
            broker_order_from_trade_object.filled_price,
            broker_order_from_trade_object.fill_datetime,
        )

    return new_broker_order
