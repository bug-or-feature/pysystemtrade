import datetime

from sysdata.arctic.arctic_fsb_per_contract_prices import (
    ArcticFsbContractPriceData,
)
from sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_futures_contracts import mongoFuturesContractData
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysobjects.contract_dates_and_expiries import (
    listOfContractDateStr,
)
from sysobjects.contracts import futuresContract
from sysproduction.data.contracts import dataContracts
from sysproduction.data.fsb_prices import diagFsbPrices
from sysproduction.data.generic_production_data import productionDataLayerGeneric
from sysproduction.data.prices import get_valid_instrument_code_from_user

missing_expiry = datetime.datetime(1900, 1, 1)


class DataFsbContracts(dataContracts, productionDataLayerGeneric):

    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                ArcticFsbContractPriceData,
                mongoRollParametersData,
                arcticFuturesMultiplePricesData,
                mongoFuturesContractData,
            ]
        )

        return data

    # @property
    # def db_contract_data(self) -> futuresContractData:
    #     return self.data.db_futures_contract
    #
    # @property
    # def db_multiple_prices_data(self) -> futuresMultiplePricesData:
    #     return self.data.db_futures_multiple_prices
    #
    # @property
    # def db_roll_parameters(self) -> rollParametersData:
    #     return self.data.db_roll_parameters


def get_valid_contract_object_from_user(
    data: dataBlob,
    instrument_code: str = None,
    only_include_priced_contracts: bool = False,
) -> futuresContract:

    (
        instrument_code,
        contract_date_str,
    ) = get_valid_fsb_instrument_code_and_contractid_from_user(
        data,
        instrument_code=instrument_code,
        only_include_priced_contracts=only_include_priced_contracts,
    )
    contract = futuresContract(instrument_code, contract_date_str)
    return contract

def get_valid_fsb_contract_object_from_user(
    data: dataBlob,
    instrument_code: str = None,
    only_include_priced_contracts: bool = False,
) -> futuresContract:

    (
        instrument_code,
        contract_date_str,
    ) = get_valid_fsb_instrument_code_and_contractid_from_user(
        data,
        instrument_code=instrument_code,
        only_include_priced_contracts=only_include_priced_contracts,
    )
    contract = futuresContract(instrument_code, contract_date_str)
    return contract


def get_valid_fsb_instrument_code_and_contractid_from_user(
    data: dataBlob,
    instrument_code: str = None,
    only_include_priced_contracts: bool = False,
) -> (str, str):

    diag_contracts = DataFsbContracts(data)

    invalid_input = True
    while invalid_input:
        if instrument_code is None:
            instrument_code = get_valid_instrument_code_from_user(data, source="single")

        dates_to_choose_from = get_dates_to_choose_from(
            data=data,
            instrument_code=instrument_code,
            only_priced_contracts=only_include_priced_contracts,
        )

        if len(dates_to_choose_from) == 0:
            print("%s is not an instrument with contract data" % instrument_code)
            instrument_code = None
            continue

        dates_to_display = (
            diag_contracts.get_labelled_list_of_contracts_from_contract_date_list(
                instrument_code, dates_to_choose_from
            )
        )

        print("Available contract dates %s" % str(dates_to_display))
        print("p = currently priced, c=current carry, f= current forward")
        contract_date = input("Contract date? [yyyymm or yyyymmdd] (ignore suffixes)")
        if len(contract_date) == 6:
            contract_date = contract_date + "00"
        if contract_date in dates_to_choose_from:
            break
        else:
            print("%s is not in list %s" % (contract_date, dates_to_choose_from))
            continue  # not required

    return instrument_code, contract_date

def get_dates_to_choose_from(
    data: dataBlob, instrument_code: str, only_priced_contracts: bool = False
) -> listOfContractDateStr:

    diag_contracts = DataFsbContracts(data)
    diag_prices = diagFsbPrices(data)
    if only_priced_contracts:
        dates_to_choose_from = (
            diag_prices.contract_dates_with_price_data_for_instrument_code(
                instrument_code
            )
        )
    else:
        contract_list = diag_contracts.get_all_contract_objects_for_instrument_code(
            instrument_code
        )
        dates_to_choose_from = contract_list.list_of_dates()

    dates_to_choose_from = listOfContractDateStr(dates_to_choose_from)
    dates_to_choose_from = dates_to_choose_from.sorted_date_str()

    return dates_to_choose_from




