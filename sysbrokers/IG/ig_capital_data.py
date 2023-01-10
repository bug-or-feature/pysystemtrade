from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_capital_data import brokerCapitalData

from syscore.objects import arg_not_supplied
from sysdata.production.timed_storage import classStrWithListOfEntriesAsListOfDicts

from sysobjects.spot_fx_prices import currencyValue, listOfCurrencyValues

from syslogdiag.logger import logger
from syslogdiag.log_to_screen import logtoscreen


class IgCapitalData(brokerCapitalData):
    def __init__(
        self, broker_conn: IGConnection, log: logger = logtoscreen("IGCapitalData")
    ):
        super().__init__(log=log)
        self._igconnection = broker_conn

    @property
    def igconnection(self) -> IGConnection:
        return self._igconnection

    def __repr__(self):
        return "IG capital data"

    def get_account_value_across_currency(
        self, account_id: str = arg_not_supplied
    ) -> listOfCurrencyValues:
        list_of_values_per_currency = list(
            [
                currencyValue(currency, self.igconnection.get_capital(account_id))
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
