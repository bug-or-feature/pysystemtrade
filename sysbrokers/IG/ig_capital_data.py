from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_capital_data import brokerCapitalData

from syscore.objects import arg_not_supplied
from sysdata.data_blob import dataBlob
from sysdata.production.timed_storage import classStrWithListOfEntriesAsListOfDicts

from sysobjects.spot_fx_prices import currencyValue, listOfCurrencyValues

from syslogdiag.logger import logger
from syslogdiag.log_to_screen import logtoscreen


class IgCapitalData(brokerCapitalData):
    def __init__(
        self,
        data_blob: dataBlob,
        broker_conn: IGConnection,
        log: logger = logtoscreen("IGCapitalData"),
    ):
        super().__init__(log=log)
        self._dataBlob = data_blob
        self._broker_conn = broker_conn

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

    @property
    def data(self):
        return self._dataBlob

    def __repr__(self):
        return "IG capital data"

    def get_account_value_across_currency(
        self, account_id: str = arg_not_supplied
    ) -> listOfCurrencyValues:
        list_of_values_per_currency = list(
            [
                currencyValue(currency, self.broker_conn.get_capital(account_id))
                for currency in ["GBP"]
            ]
        )
        list_of_values_per_currency = listOfCurrencyValues(list_of_values_per_currency)
        return list_of_values_per_currency

    def _get_series_dict_with_data_class_for_args_dict(
        self, args_dict: dict
    ) -> classStrWithListOfEntriesAsListOfDicts:
        pass

    def _write_series_dict_for_args_dict(
        self,
        args_dict: dict,
        class_str_with_series_as_list_of_dicts: classStrWithListOfEntriesAsListOfDicts,
    ):
        pass

    def _get_list_of_args_dict(self) -> list:
        pass
