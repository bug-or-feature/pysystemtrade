"""
Read and write FSB price data to and from Arctic / MongoDB
"""

from sysdata.arctic.arctic_connection import arcticData
from sysdata.futures.futures_per_contract_prices import (
    futuresContractPriceData,
    listOfFuturesContracts,
)
from sysobjects.fsb_contract_prices import FsbContractPrices
from sysobjects.contracts import futuresContract
from syslogdiag.log_to_screen import logtoscreen
from syscore.merge_data import merge_newer_data, spike_in_data
from syscore.objects import missing_data
import pandas as pd

CONTRACT_COLLECTION = "fsb_contract_prices"


class ArcticFsbContractPriceData(futuresContractPriceData):

    """
    Read and write FSB price data to and from Arctic / MongoDB
    """

    def __init__(self, mongo_db=None, log=logtoscreen("ArcticFsbContractPriceData")):
        super().__init__(log=log)
        self._arctic_connection = arcticData(CONTRACT_COLLECTION, mongo_db=mongo_db)

    def __repr__(self):
        return repr(self._arctic_connection)

    @property
    def arctic_connection(self):
        return self._arctic_connection

    def _get_merged_prices_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract
    ) -> FsbContractPrices:
        """
        Read back the prices for a given contract object

        :param futures_contract_object:  futuresContract
        :return: data
        """

        ident = from_contract_to_key(futures_contract_object)

        # Returns a data frame which should have the right format
        data = self.arctic_connection.read(ident)

        return FsbContractPrices(data)

    def _write_merged_prices_for_contract_object_no_checking(
        self,
        futures_contract_object: futuresContract,
        futures_price_data: FsbContractPrices,
    ):
        """
        Write prices
        CHECK prices are overriden on second write

        :param futures_contract_object: futuresContract
        :param futures_price_data: futuresContractPriceData
        :return: None
        """

        log = futures_contract_object.log(self.log)
        ident = from_contract_to_key(futures_contract_object)
        futures_price_data_as_pd = pd.DataFrame(futures_price_data)

        self.arctic_connection.write(ident, futures_price_data_as_pd)

        log.msg(
            "Wrote %s lines of prices for %s to %s"
            % (len(futures_price_data), str(futures_contract_object.key), str(self))
        )

    def get_contracts_with_merged_price_data(self) -> listOfFuturesContracts:
        """

        :return: list of contracts
        """

        list_of_contract_tuples = self._get_contract_tuples_with_price_data()
        list_of_contracts = [
            futuresContract.from_two_strings(contract_tuple[0], contract_tuple[1])
            for contract_tuple in list_of_contract_tuples
        ]

        list_of_contracts = listOfFuturesContracts(list_of_contracts)

        return list_of_contracts

    def has_merged_price_data_for_contract(
        self, contract_object: futuresContract
    ) -> bool:
        return self.arctic_connection.has_keyname(from_contract_to_key(contract_object))

    def _get_contract_tuples_with_price_data(self) -> list:
        """

        :return: list of futures contracts as tuples
        """

        all_keynames = self._all_keynames_in_library()
        list_of_contract_tuples = [
            from_key_to_tuple(keyname) for keyname in all_keynames
        ]

        return list_of_contract_tuples

    def _all_keynames_in_library(self) -> list:
        return self.arctic_connection.get_keynames()

    def _delete_merged_prices_for_contract_object_with_no_checks_be_careful(
        self, futures_contract_object: futuresContract
    ):
        """
        Delete prices for a given contract object without performing any checks

        WILL THIS WORK IF DOESN'T EXIST?
        :param futures_contract_object:
        :return: None
        """
        log = futures_contract_object.log(self.log)

        ident = from_contract_to_key(futures_contract_object)
        self.arctic_connection.delete(ident)
        log.msg(
            "Deleted all prices for %s from %s"
            % (futures_contract_object.key, str(self))
        )

    def update_prices_for_contract(
        self,
        contract_object: futuresContract,
        new_futures_per_contract_prices: FsbContractPrices,
        check_for_spike: bool = True,
    ) -> int:
        """
        Reads existing data, merges with new_futures_prices, writes merged data

        :param new_futures_per_contract_prices:
        :return: int, number of rows
        """
        new_log = contract_object.log(self.log)

        if len(new_futures_per_contract_prices) == 0:
            new_log.msg("No new data")
            return 0

        old_prices = self.get_merged_prices_for_contract_object(contract_object)
        merged_prices = old_prices.add_rows_to_existing_data(
            new_futures_per_contract_prices, check_for_spike=check_for_spike
        )

        if merged_prices is spike_in_data:
            new_log.msg(
                "Price has moved too much - will need to manually check - no price update done"
            )
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
                new_log.msg("No additional data since %s " % str(old_prices.index[-1]))
            return 0

        # We have guaranteed no duplication
        self.write_merged_prices_for_contract_object(
            contract_object, merged_prices, ignore_duplication=True
        )

        new_log.msg("Added %d additional rows of data" % rows_added)

        return rows_added

    def add_rows_to_existing_data(
        self, new_futures_per_contract_prices, check_for_spike=True
    ):
        """
        Merges self with new data.
        Only newer data will be added

        :param new_futures_per_contract_prices: another futures per contract prices object

        :return: merged futures_per_contract object
        """

        merged_futures_prices = merge_newer_data(
            pd.DataFrame(self),
            new_futures_per_contract_prices,
            check_for_spike=False,
        )

        if merged_futures_prices is spike_in_data:
            return spike_in_data

        merged_futures_prices = FsbContractPrices(merged_futures_prices)

        return merged_futures_prices

    def get_merged_prices_for_contract_object(
        self, contract_object: futuresContract, return_empty: bool = True
    ):
        """
        get all prices without worrying about frequency

        :param contract_object:  futuresContract
        :param return_empty:  return_empty
        :return: data
        """

        if self.has_merged_price_data_for_contract(contract_object):
            prices = self._get_merged_prices_for_contract_object_no_checking(
                contract_object
            )
        else:
            if return_empty:
                return FsbContractPrices.create_empty()
            else:
                return missing_data

        return prices


def from_key_to_tuple(keyname):
    return keyname.split(".")


def from_contract_to_key(contract: futuresContract):
    return from_tuple_to_key([contract.instrument_code, contract.date_str])


def from_tuple_to_key(keytuple):
    return keytuple[0] + "." + keytuple[1]
