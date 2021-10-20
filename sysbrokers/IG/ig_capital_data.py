
from sysbrokers.IG.ig_connection import ConnectionIG
from sysbrokers.IG.client.ig_accounting_client import IgAccountingClient
from sysbrokers.broker_capital_data import brokerCapitalData

from syscore.objects import arg_not_supplied
from sysdata.production.timed_storage import classStrWithListOfEntriesAsListOfDicts

from sysobjects.spot_fx_prices import listOfCurrencyValues

from syslogdiag.logger import logger
from syslogdiag.log_to_screen import logtoscreen


class IgCapitalData(brokerCapitalData):
    def __init__(self, log: logger = logtoscreen("IGCapitalData")):
        super().__init__(log=log)
        self._igconnection = ConnectionIG()

    @property
    def igconnection(self) -> ConnectionIG:
        return self._igconnection

    @property
    def ig_client(self) -> IgAccountingClient:
        client = getattr(self, "_ig_client", None)
        if client is None:
            client = self._ig_client = IgAccountingClient(igconnection=self.igconnection, log = self.log)
        return client

    def __repr__(self):
        return "IG capital data"

    def get_account_value_across_currency(self, account_id: str = arg_not_supplied) -> listOfCurrencyValues:
        return self.ig_client.broker_get_account_value_across_currency(account_id=account_id)

    def _get_series_dict_with_data_class_for_args_dict(self, args_dict: dict) -> classStrWithListOfEntriesAsListOfDicts:
        pass

    def _write_series_dict_for_args_dict(self, args_dict: dict,
            class_str_with_series_as_list_of_dicts: classStrWithListOfEntriesAsListOfDicts):
        pass

    def _get_list_of_args_dict(self) -> list:
        pass

