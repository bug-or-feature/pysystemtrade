from syscore.constants import arg_not_supplied, success, failure
from sysdata.data_blob import dataBlob
from sysproduction.data.orders import dataOrders
from sysproduction.data.prices import diagPrices, updatePrices
from sysproduction.data.contracts import dataContracts
from sysproduction.data.broker import dataBroker
from sysproduction.data.fsb_epics import UpdateMarketInfo


class igHandler:
    def __init__(self, data: dataBlob = arg_not_supplied):
        if data is arg_not_supplied:
            data = dataBlob()

        self._data = data
        self._log = data.log

        order_data = dataOrders(data)

        instrument_stack = order_data.db_instrument_stack_data
        contract_stack = order_data.db_contract_stack_data
        broker_stack = order_data.db_broker_stack_data

        self._instrument_stack = instrument_stack
        self._contract_stack = contract_stack
        self._broker_stack = broker_stack

    @property
    def data(self):
        return self._data

    @property
    def log(self):
        return self._log

    @property
    def instrument_stack(self):
        return self._instrument_stack

    @property
    def contract_stack(self):
        return self._contract_stack

    @property
    def broker_stack(self):
        return self._broker_stack

    @property
    def diag_prices(self) -> diagPrices:
        diag_prices = getattr(self, "_diag_prices", None)
        if diag_prices is None:
            diag_prices = diagPrices(self.data)
            self._diag_prices = diag_prices

        return diag_prices

    @property
    def data_contracts(self) -> dataContracts:
        data_contracts = getattr(self, "_data_contracts", None)
        if data_contracts is None:
            data_contracts = dataContracts(self.data)
            self._data_contracts = data_contracts

        return data_contracts

    @property
    def data_broker(self) -> dataBroker:
        data_broker = getattr(self, "_data_broker", None)
        if data_broker is None:
            data_broker = dataBroker(self.data)
            self._data_broker = data_broker

        return data_broker

    @property
    def update_prices(self) -> updatePrices:
        update_prices = getattr(self, "_update_prices", None)
        if update_prices is None:
            update_prices = updatePrices(self.data)
            self._update_prices = update_prices

        return update_prices

    @property
    def update_market_info(self) -> UpdateMarketInfo:
        update_market_info = getattr(self, "_update_market_info", None)
        if update_market_info is None:
            update_market_info = UpdateMarketInfo(self.data)
            self._update_market_info = update_market_info

        return update_market_info
