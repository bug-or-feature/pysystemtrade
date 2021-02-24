from syscore.merge_data import spike_in_data
from syscore.objects import missing_data, missing_contract
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysdata.barchart.barchart import barchartConnection
from sysdata.barchart.barchart_futures_contracts_data import barchartFuturesContractData
from sysdata.futures.futures_per_contract_prices import futuresContractPriceData
from syslogdiag.log import logtoscreen
from sysobjects.contracts import futuresContract, listOfFuturesContracts
from sysobjects.futures_per_contract_prices import futuresContractPrices


class barchartFuturesContractPriceData(futuresContractPriceData):

    """
    Extends the baseData object to a data source that reads in prices for specific futures contracts

    This gets HISTORIC data from barchart.com
    In a live production system it is suitable for running on a daily basis to get end of day prices
    """

    def __init__(self, log=logtoscreen("barchartFuturesContractPriceData")):
        super().__init__(log=log)
        self._barchart = barchartConnection()
        self._arctic = arcticFuturesContractPriceData()

    def __repr__(self):
        return "Barchart Futures per contract price data %s" % str(self._barchart)

    @property
    def log(self):
        return self._log

    @property
    def barchart(self):
        return self._barchart

    @property
    def futures_contract_data(self) -> barchartFuturesContractData:
        return barchartFuturesContractData(barchart = self._barchart, log = self.log)

    def has_data_for_contract(self, futures_contract: futuresContract) -> bool:
        return self._barchart.has_data_for_contract(futures_contract)

    def get_list_of_instrument_codes_with_price_data(self) -> list:
        # return list of instruments for which pricing is configured
        list_of_instruments = self.futures_instrument_data.get_list_of_instruments()

        return list_of_instruments

    def contracts_with_price_data_for_instrument_code(self, instrument_code: str) -> listOfFuturesContracts:
        futures_instrument_with_ib_data = self.futures_instrument_data.get_futures_instrument_object_with_IB_data(instrument_code)
        list_of_date_str = self.ib_client.broker_get_futures_contract_list(futures_instrument_with_ib_data)

        list_of_contracts = [futuresContract(instrument_code, date_str) for date_str in list_of_date_str]

        list_of_contracts = listOfFuturesContracts(list_of_contracts)

        return list_of_contracts

    def get_contracts_with_price_data(self):
        raise NotImplementedError(
            "Do not use get_contracts_with_price_data() with Barchart")

    def update_prices_for_contract(
        self,
        contract_object: futuresContract,
        new_futures_per_contract_prices: futuresContractPrices,
        check_for_spike: bool=True,
    ) -> int:
        """
        Reads existing data, merges with new_futures_prices, writes merged data

        :param new_futures_prices:
        :return: int, number of rows
        """
        new_log = contract_object.log(self.log)

        if len(new_futures_per_contract_prices) == 0:
            new_log.msg("No new data")
            return 0

        old_prices = self._arctic.get_prices_for_contract_object(
            contract_object)
        merged_prices = old_prices.add_rows_to_existing_data(
            new_futures_per_contract_prices, check_for_spike=check_for_spike
        )

        if merged_prices is spike_in_data:
            new_log.msg(
                "Price has moved too much - will need to manually check - no price updated done")
            return spike_in_data

        rows_added = len(merged_prices) - len(old_prices)

        if rows_added<0:
            new_log.critical("Can't remove prices something gone wrong!")
            return 0

        elif rows_added == 0:
            if len(old_prices) == 0:
                new_log.msg("No existing or additional data")
                return 0
            else:
                new_log.msg("No additional data since %s " %
                        str(old_prices.index[-1]))
            return 0

        # We have guaranteed no duplication
        self._arctic.write_prices_for_contract_object(
            contract_object, merged_prices, ignore_duplication=True
        )

        new_log.msg("Added %d additional rows of data" % rows_added)

        return rows_added


    def _get_prices_for_contract_object_no_checking(self, contract_object: futuresContract) -> futuresContractPrices:
        return self._get_prices_at_frequency_for_contract_object_no_checking(contract_object, freq="D")

    def _get_prices_at_frequency_for_contract_object_no_checking(
            self, contract_object: futuresContract, freq: str) -> futuresContractPrices:

        #raise NotImplementedError("TODO")

        """
        Get historical prices at a particular frequency

        We override this method, rather than _get_prices_at_frequency_for_contract_object_no_checking
        Because the list of dates returned by contracts_with_price_data is likely to not match (expiries)

        :param contract_object:  futuresContract
        :param freq: str; one of D, H, 15M, 5M, M, 10S, S
        :return: data
        """


        contract_object_plus = self.futures_contract_data.get_contract_object_plus(
                contract_object)

        if contract_object_plus is missing_contract:
            self.log.warn("Can't get data for %s" % str(contract_object))
            return futuresContractPrices.create_empty()

        price_data = self._barchart.get_historical_futures_data_for_contract(
            contract_object_plus, bar_freq=freq)

        if price_data is missing_data:
            log.warn("Something went wrong getting Barchart price data for %s" %
                str(contract_object))
            price_data = futuresContractPrices.create_empty()

        elif len(price_data) == 0:
            self.log.warn(
                "No Barchart price data found for %s" %
                str(contract_object))
            price_data = futuresContractPrices.create_empty()
        else:
            price_data = futuresContractPrices(price_data)

        ## It's important that the data is in local time zone so that this works
        price_data = price_data.remove_future_data()

        ## Some contract data is marked to model, don't want this
        price_data = price_data.remove_zero_volumes()

        return price_data

    def _write_prices_for_contract_object_no_checking(self, *args, **kwargs):
        raise NotImplementedError("Barchart is a read only source of prices")

    def delete_prices_for_contract_object(self, *args, **kwargs):
        raise NotImplementedError("Barchart is a read only source of prices")

    def _delete_prices_for_contract_object_with_no_checks_be_careful(self,
            futures_contract_object: futuresContract):
        raise NotImplementedError("Barchart is a read only source of prices")







