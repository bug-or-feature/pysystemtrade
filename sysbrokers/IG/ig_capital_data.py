from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_capital_data import brokerCapitalData
from sysdata.data_blob import dataBlob
from syscore.constants import arg_not_supplied

from sysobjects.spot_fx_prices import currencyValue, listOfCurrencyValues

from syslogdiag.pst_logger import pst_logger
from syslogdiag.log_to_screen import logtoscreen


class IgCapitalData(brokerCapitalData):
    def __init__(
        self,
        broker_conn: IGConnection,
        data: dataBlob,
        log: pst_logger = logtoscreen("IGCapitalData"),
    ):
        super().__init__(log=log, data=data)
        self._broker_conn = broker_conn

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

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

    def get_excess_liquidity_value_across_currency(
        self, account_id: str = arg_not_supplied
    ) -> listOfCurrencyValues:
        # list_of_values_per_currency = list(
        #     [
        #         currencyValue(currency, self.broker_conn.get_available_capital(account_id))
        #         for currency in ["GBP"]
        #     ]
        # )
        # list_of_values_per_currency = listOfCurrencyValues(list_of_values_per_currency)
        # return list_of_values_per_currency
        # TODO
        pass

    """
    Can add other functions not in parent class to get IB specific stuff which could be required for
      strategy decomposition
    """
