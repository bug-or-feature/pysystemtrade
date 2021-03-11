from syscore.merge_data import spike_in_data
from syscore.objects import missing_data, missing_contract
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysdata.barchart.bc_connection import bcConnection
from sysdata.barchart.bc_futures_contracts_data import BarchartFuturesContractData
from sysdata.barchart.bc_instruments_data import BarchartFuturesInstrumentData
from sysdata.futures.futures_per_contract_prices import futuresContractPriceData
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices


class BarchartFuturesContractPriceData(futuresContractPriceData):

    """
    Extends the futuresContractPriceData object to a data source that reads in prices
    for specific futures contracts

    This gets HISTORIC data from barchart.com
    In a live production system it is suitable for running on a daily basis to get end of day prices
    """

    def __init__(self, log=logtoscreen("barchartFuturesContractPriceData")):
        super().__init__(log=log)
        self._barchart = bcConnection()
        self._arctic = arcticFuturesContractPriceData()

    def __repr__(self):
        return f"Barchart Futures per contract price data {str(self._barchart)}"

    @property
    def log(self):
        return self._log

    @property
    def barchart(self):
        return self._barchart

    @property
    def futures_contract_data(self) -> BarchartFuturesContractData:
        return BarchartFuturesContractData(barchart=self._barchart, log=self.log)

    @property
    def futures_instrument_data(self) -> BarchartFuturesInstrumentData:
        return BarchartFuturesInstrumentData(log=self.log)

    def has_data_for_contract(self, futures_contract: futuresContract) -> bool:
        return self._barchart.has_data_for_contract(futures_contract)

    def get_list_of_instrument_codes_with_price_data(self) -> list:
        # return list of instruments for which pricing is configured
        list_of_instruments = self.futures_instrument_data.get_list_of_instruments()
        return list_of_instruments

    def get_contracts_with_price_data(self):
        raise NotImplementedError(
            "Do not use get_contracts_with_price_data() with Barchart")

    def update_prices_for_contract(self, contract_object: futuresContract,
                                   new_futures_per_contract_prices: futuresContractPrices,
                                   check_for_spike: bool = True) -> int:
        """
        Reads existing data, merges with new_futures_prices, writes merged data

        :param check_for_spike:
        :type check_for_spike:
        :param contract_object:
        :type contract_object:
        :param new_futures_per_contract_prices:
        :type new_futures_per_contract_prices:
        :return: int, number of rows
        """
        new_log = contract_object.log(self.log)

        if len(new_futures_per_contract_prices) == 0:
            new_log.msg("No new data")
            return 0

        old_prices = self._arctic.get_prices_for_contract_object(contract_object)
        merged_prices = old_prices.add_rows_to_existing_data(
            new_futures_per_contract_prices, check_for_spike=check_for_spike
        )

        if merged_prices is spike_in_data:
            new_log.msg("Price spike - manual check required - update not done")
            return spike_in_data

        rows_added = len(merged_prices) - len(old_prices)

        if rows_added < 0:
            new_log.critical("Can't remove prices something gone wrong!")
            return 0

        elif rows_added == 0:
            if len(old_prices) == 0:
                new_log.msg("No existing or additional data")
                return 0
            else:
                new_log.msg(f"No additional data since {str(old_prices.index[-1])}")
            return 0

        # We have guaranteed no duplication
        self._arctic.write_prices_for_contract_object(
            contract_object, merged_prices, ignore_duplication=True
        )

        new_log.msg(f"Added {rows_added} additional rows of data")

        return rows_added

    def _get_prices_for_contract_object_no_checking(self, contract_object: futuresContract) -> futuresContractPrices:
        return self._get_prices_at_frequency_for_contract_object_no_checking(contract_object, freq="D")

    def _get_prices_at_frequency_for_contract_object_no_checking(
            self, contract_object: futuresContract, freq: str) -> futuresContractPrices:

        """
        Get historical prices at a particular frequency

        We override this method, rather than _get_prices_at_frequency_for_contract_object_no_checking
        Because the list of dates returned by contracts_with_price_data is likely to not match (expiries)

        :param contract_object:  futuresContract
        :param freq: str; one of D, H, 15M, 5M, M, 10S, S
        :return: data
        """

        contract_object_plus = self.futures_contract_data.get_contract_object_with_bc_data(
                contract_object)

        if contract_object_plus is missing_contract:
            self.log.warn(f"Can't get data for {str(contract_object)}")
            return futuresContractPrices.create_empty()

        price_data = self._barchart.get_historical_futures_data_for_contract(
            contract_object_plus, bar_freq=freq)

        if price_data is missing_data:
            self.log.warn(f"Problem getting Barchart price data for {str(contract_object)}")
            price_data = futuresContractPrices.create_empty()

        elif len(price_data) == 0:
            self.log.warn(f"No Barchart price data found for {str(contract_object)}")
            price_data = futuresContractPrices.create_empty()
        else:
            price_data = futuresContractPrices(price_data)

        # It's important that the data is in local time zone so that this works
        price_data = price_data.remove_future_data()

        # Some contract data is marked to model, don't want this
        price_data = price_data.remove_zero_volumes()

        return price_data

    def _write_prices_for_contract_object_no_checking(self, *args, **kwargs):
        raise NotImplementedError("Barchart is a read only source of prices")

    def delete_prices_for_contract_object(self, *args, **kwargs):
        raise NotImplementedError("Barchart is a read only source of prices")

    def _delete_prices_for_contract_object_with_no_checks_be_careful(
            self, contract_object: futuresContract):
        raise NotImplementedError("Barchart is a read only source of prices")
