import pandas as pd
from syscore.constants import arg_not_supplied
from syscore.dateutils import Frequency

from sysdata.arctic.arctic_fsb_epics_history import (
    FsbEpicsHistoryData,
)
from sysdata.arctic.arctic_fsb_per_contract_prices import (
    FsbContractPrices,
)

from sysdata.data_blob import dataBlob
from sysdata.futures.futures_per_contract_prices import futuresContractPriceData
from sysdata.futures.multiple_prices import futuresMultiplePricesData
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysobjects.contract_dates_and_expiries import listOfContractDateStr
from sysobjects.contracts import futuresContract
from sysproduction.data.generic_production_data import productionDataLayerGeneric
from sysproduction.data.production_data_objects import (
    get_class_for_data_type,
    FUTURES_ADJUSTED_PRICE_DATA,
    FUTURES_MULTIPLE_PRICE_DATA,
    FUTURES_CONTRACT_DATA,
    MARKET_INFO_DATA,
    FSB_EPIC_HISTORY_DATA,
    FSB_CONTRACT_PRICE_DATA,
)


class DiagFsbPrices(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                get_class_for_data_type(FSB_CONTRACT_PRICE_DATA),
                get_class_for_data_type(FUTURES_CONTRACT_DATA),
                get_class_for_data_type(FUTURES_ADJUSTED_PRICE_DATA),
                get_class_for_data_type(FUTURES_MULTIPLE_PRICE_DATA),
                get_class_for_data_type(FSB_EPIC_HISTORY_DATA),
                get_class_for_data_type(MARKET_INFO_DATA),
            ]
        )
        return data

    def get_prices_for_contract_object(
        self, contract_object: futuresContract
    ) -> FsbContractPrices:
        prices = self.db_fsb_contract_price_data.get_merged_prices_for_contract_object(
            contract_object
        )

        return prices

    # def get_spreads(self, instrument_code: str) -> spreadsForInstrument:
    #     return self.db_spreads_for_instrument_data.get_spreads(instrument_code)
    #
    # def get_list_of_instruments_with_spread_data(self) -> list:
    #     return self.db_spreads_for_instrument_data.get_list_of_instruments()

    @property
    def db_fsb_contract_price_data(self) -> futuresContractPriceData:
        return self.data.db_fsb_contract_price

    @property
    def db_futures_multiple_prices_data(self) -> futuresMultiplePricesData:
        return self.data.db_futures_multiple_prices

    @property
    def db_futures_contract_price_data(self) -> futuresContractPriceData:
        return self.data.db_futures_contract_price

    @property
    def db_fsb_epic_history_data(self) -> FsbEpicsHistoryData:
        return self.data.db_fsb_epic_history

    # @property
    # def db_spreads_for_instrument_data(self) -> spreadsForInstrumentData:
    #     return self.data.db_spreads_for_instrument

    def contract_dates_with_price_data_for_instrument_code(
        self, instrument_code: str
    ) -> listOfContractDateStr:
        list_of_contract_date_str = self.db_fsb_contract_price_data.contract_dates_with_merged_price_data_for_instrument_code(
            instrument_code
        )

        return list_of_contract_date_str

    def get_list_of_instruments_in_multiple_prices(self) -> list:
        return self.db_futures_multiple_prices_data.get_list_of_instruments()

    def get_list_of_instruments_with_contract_prices(self) -> list:
        return (
            self.db_futures_contract_price_data.get_list_of_instrument_codes_with_merged_price_data()
        )

    def get_list_of_instruments_with_epic_history(self) -> list:
        return self.db_fsb_epic_history_data.get_list_of_instruments()


class UpdateFsbPrices(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                get_class_for_data_type(FSB_CONTRACT_PRICE_DATA),
                get_class_for_data_type(FUTURES_CONTRACT_DATA),
                # arcticSpreadsForInstrumentData,
            ]
        )

        return data

    def update_prices_for_contract(
        self,
        contract_object: futuresContract,
        new_prices: pd.DataFrame,
        check_for_spike: bool = True,
    ) -> int:
        error_or_rows_added = (
            self.db_fsb_contract_price_data.update_prices_for_contract(
                contract_object, new_prices, check_for_spike=check_for_spike
            )
        )
        return error_or_rows_added

    def delete_merged_contract_prices_for_instrument_code(
        self, instrument_code: str, are_you_sure: bool = False
    ):
        self.db_fsb_contract_price_data.delete_merged_prices_for_instrument_code(
            instrument_code, areyousure=are_you_sure
        )

    def delete_contract_prices_at_frequency_for_instrument_code(
        self, instrument_code: str, frequency: Frequency, are_you_sure: bool = False
    ):
        self.db_fsb_contract_price_data.delete_prices_at_frequency_for_instrument_code(
            instrument_code, frequency=frequency, areyousure=are_you_sure
        )

    @property
    def db_futures_contract_price_data(self) -> futuresContractPriceData:
        return self.data.db_futures_contract_price

    @property
    def db_fsb_contract_price_data(self) -> futuresContractPriceData:
        return self.data.db_fsb_contract_price

    # @property
    # def db_spreads_for_instrument_data(self) -> spreadsForInstrumentData:
    #     return self.data.db_spreads_for_instrument


def get_valid_fsb_instrument_code_from_user(
    data: dataBlob = arg_not_supplied,
    allow_all: bool = False,
    allow_exit: bool = False,
    all_code="ALL",
    exit_code="",
    source="multiple",
) -> str:
    if data is arg_not_supplied:
        data = dataBlob()
    instrument_code_list = get_list_of_instruments(data, source=source)
    invalid_input = True
    input_prompt = "Instrument code?"
    if allow_all:
        input_prompt = input_prompt + "(Return for ALL)"
    elif allow_exit:
        input_prompt = input_prompt + "(Return to EXIT)"
    while invalid_input:
        instrument_code = input(input_prompt)

        if allow_all:
            if instrument_code == "" or instrument_code == "ALL":
                return all_code
        elif allow_exit:
            if instrument_code == "":
                return exit_code

        if instrument_code in instrument_code_list:
            break

        print(
            "%s is not in list %s derived from source: %s"
            % (instrument_code, instrument_code_list, source)
        )

    return instrument_code


def get_list_of_instruments(
    data: dataBlob = arg_not_supplied,
    source="multiple",
    use_db=True,
) -> list:
    if use_db:
        price_data = DiagFsbPrices(data)
        if source == "multiple":
            instrument_list = price_data.get_list_of_instruments_in_multiple_prices()
        elif source == "single":
            instrument_list = price_data.get_list_of_instruments_with_contract_prices()
        elif source == "fsb":
            instrument_list = price_data.get_list_of_instruments_with_epic_history()
        else:
            raise Exception("%s not recognised must be multiple or single" % source)
    else:
        price_data = csvFuturesSimData()
        instrument_list = price_data.get_instrument_list()
        # instrument_list = ["GOLD"]

    instrument_list.sort()

    return instrument_list
