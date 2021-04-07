from syscore.objects import arg_not_supplied
from sysdata.data_blob import dataBlob
from sysobjects.spot_fx_prices import fxPrices
from sysobjects.contracts import futuresContract
from sysobjects.contract_dates_and_expiries import expiryDate
from sysdata.arctic.arctic_futures_per_contract_prices import futuresContractPrices


class altDataSource(object):
    """
    Alternative (ie not Interactive Brokers) source of financial data
    """

    def __init__(self, data: dataBlob = arg_not_supplied):
        if data is arg_not_supplied:
            data = dataBlob()

        self.data = data

    def get_fx_prices(self, fx_code: str) -> fxPrices:
        # TODO check the source has been wired up ok?
        return self.data.db_fx_prices.get_fx_prices(fx_code)

    def get_prices_at_frequency_for_contract_object(
            self, contract_object: futuresContract, frequency: str) -> futuresContractPrices:

        # TODO check the source has been wired up ok?
        return self.data.db_futures_contract_price.get_prices_at_frequency_for_contract_object(
                contract_object, frequency)

    def get_actual_expiry_date_for_single_contract(
            self, futures_contract: futuresContract) -> expiryDate:

        # TODO check the source has been wired up ok?
        return self.data.db_futures_contract.get_actual_expiry_date_for_single_contract(
            futures_contract)

