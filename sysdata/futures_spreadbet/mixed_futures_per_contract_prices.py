from syscore.dateutils import Frequency, MIXED_FREQ
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
    from_key_to_freq_and_contract as arctic_from_key_to_freq_and_contract,
)
from sysdata.mongodb.mongo_connection import mongoDb
from sysdata.parquet.parquet_access import ParquetAccess
from sysdata.parquet.parquet_futures_per_contract_prices import (
    parquetFuturesContractPriceData,
    from_key_to_freq_and_contract as parquet_from_key_to_freq_and_contract,
)
from sysdata.futures.futures_per_contract_prices import (
    futuresContractPriceData,
)
from sysobjects.contracts import futuresContract, listOfFuturesContracts
from sysobjects.futures_per_contract_prices import futuresContractPrices
from syslogging.logger import *


class mixedFuturesContractPriceData(futuresContractPriceData):
    """
    Handles contract prices for Futures (parquet) and FSBs (arctic) by delegating to an
    instance of parquetFuturesContractPriceData and arcticFuturesContractPriceData
    respectively.

    It decides which data source to use by looking at the instrument code
    """

    def __init__(
        self,
        mongo_db: mongoDb = None,
        parquet_access: ParquetAccess = None,
        log=get_logger("mixedFuturesContractPriceData"),
    ):
        super().__init__(log=log)

        self._arctic = arcticFuturesContractPriceData(mongo_db=mongo_db)
        self._parquet = parquetFuturesContractPriceData(parquet_access=parquet_access)

    def __repr__(self):
        return "mixedFuturesContractPriceData"

    @property
    def arctic(self):
        return self._arctic

    @property
    def parquet(self):
        return self._parquet

    def _get_source_for_contract_object(self, contract_object: futuresContract):
        return (
            self._arctic
            if contract_object.instrument_code.endswith("_fsb")
            else self._parquet
        )

    def _get_merged_prices_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract
    ) -> futuresContractPrices:
        source = self._get_source_for_contract_object(futures_contract_object)
        data = source._get_merged_prices_for_contract_object_no_checking(
            futures_contract_object
        )

        return data

    def _get_prices_at_frequency_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract, frequency: Frequency
    ) -> futuresContractPrices:
        source = self._get_source_for_contract_object(futures_contract_object)
        return source._get_prices_at_frequency_for_contract_object_no_checking(
            futures_contract_object, frequency
        )

    def _write_merged_prices_for_contract_object_no_checking(
        self,
        futures_contract_object: futuresContract,
        futures_price_data: futuresContractPrices,
    ):
        source = self._get_source_for_contract_object(futures_contract_object)
        source._write_merged_prices_for_contract_object_no_checking(
            futures_contract_object,
            futures_price_data,
        )

    def _write_prices_at_frequency_for_contract_object_no_checking(
        self,
        futures_contract_object: futuresContract,
        futures_price_data: futuresContractPrices,
        frequency: Frequency,
    ):
        source = self._get_source_for_contract_object(futures_contract_object)
        source._write_prices_at_frequency_for_contract_object_no_checking(
            futures_contract_object,
            futures_price_data,
            frequency,
        )

    def get_contracts_with_merged_price_data(self) -> listOfFuturesContracts:
        list_of_contracts = self.get_contracts_with_price_data_for_frequency(
            frequency=MIXED_FREQ
        )

        return list_of_contracts

    def get_contracts_with_price_data_for_frequency(
        self, frequency: Frequency
    ) -> listOfFuturesContracts:
        list_of_contract_and_freq_tuples = (
            self._get_contract_and_frequencies_with_price_data()
        )
        list_of_contracts = [
            freq_and_contract_tuple[1]
            for freq_and_contract_tuple in list_of_contract_and_freq_tuples
            if freq_and_contract_tuple[0] == frequency
        ]

        list_of_contracts = listOfFuturesContracts(list_of_contracts)

        return list_of_contracts

    def has_merged_price_data_for_contract(
        self, contract_object: futuresContract
    ) -> bool:
        source = self._get_source_for_contract_object(contract_object)
        return source.has_merged_price_data_for_contract(contract_object)

    def has_price_data_for_contract_at_frequency(
        self, contract_object: futuresContract, frequency: Frequency
    ) -> bool:
        source = self._get_source_for_contract_object(contract_object)
        return source.has_price_data_for_contract_at_frequency(
            contract_object, frequency
        )

    def _get_contract_and_frequencies_with_price_data(self) -> list:
        arctic_keys = self._arctic._all_keynames_in_library()
        arctic_tuples = [
            arctic_from_key_to_freq_and_contract(keyname) for keyname in arctic_keys
        ]
        parquet_keys = self._parquet._all_keynames_in_library()
        parquet_tuples = [
            parquet_from_key_to_freq_and_contract(keyname) for keyname in parquet_keys
        ]
        return arctic_tuples + parquet_tuples

    def _all_keynames_in_library(self) -> list:
        arctic_keys = self._arctic._all_keynames_in_library()
        parquet_keys = self._parquet._all_keynames_in_library()
        return arctic_keys + parquet_keys

    def _delete_merged_prices_for_contract_object_with_no_checks_be_careful(
        self, futures_contract_object: futuresContract
    ):
        source = self._get_source_for_contract_object(futures_contract_object)
        source._delete_merged_prices_for_contract_object_with_no_checks_be_careful(
            futures_contract_object
        )

    def _delete_prices_at_frequency_for_contract_object_with_no_checks_be_careful(
        self, futures_contract_object: futuresContract, frequency: Frequency
    ):
        source = self._get_source_for_contract_object(futures_contract_object)
        source._delete_prices_at_frequency_for_contract_object_with_no_checks_be_careful(
            futures_contract_object, frequency
        )
