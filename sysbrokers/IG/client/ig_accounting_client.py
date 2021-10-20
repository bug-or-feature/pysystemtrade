from sysbrokers.IG.client.ig_client import IgClient
from syscore.objects import arg_not_supplied
from sysobjects.spot_fx_prices import currencyValue, listOfCurrencyValues


class IgAccountingClient(IgClient):

    def broker_get_account_value_across_currency(self, account_id: str = arg_not_supplied) -> listOfCurrencyValues:
        list_of_values_per_currency = list(
            [currencyValue(currency, self.ig_connection.get_capital(account_id)) for currency in ["GBP"]]
        )

        list_of_values_per_currency = listOfCurrencyValues(list_of_values_per_currency)

        return list_of_values_per_currency
