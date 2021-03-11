from syscore.objects import missing_contract, missing_instrument
from sysdata.barchart.bc_instruments_data import BarchartFuturesInstrumentData
from sysdata.barchart.bc_connection import bcConnection
from sysdata.futures.contracts import futuresContractData
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contract_dates_and_expiries import expiryDate
from sysobjects.contracts import futuresContract
from syscore.dateutils import get_datetime_from_datestring
import datetime


class BarchartFuturesContractData(futuresContractData):

    def __init__(self, barchart: bcConnection, log=logtoscreen("barchartFuturesContractData")):
        super().__init__(log=log)
        self._barchart = barchart

    def __repr__(self):
        return f"Barchart Futures per contract data: {self._barchart}"

    @property
    def barchart(self):
        return self._barchart

    @property
    def barchart_futures_instrument_data(self) -> BarchartFuturesInstrumentData:
        return BarchartFuturesInstrumentData(log=self.log)

    def get_actual_expiry_date_for_single_contract(self, futures_contract: futuresContract) -> expiryDate:
        """
        Get the actual expiry date of a contract from Barchart

        :param futures_contract: type futuresContract
        :return: YYYYMMDD or None
        """

        rough_expiry = get_datetime_from_datestring(futures_contract.date_str)
        if rough_expiry < datetime.datetime(2000, 1, 1):
            raise Exception("Cannot get expiry dates for older expired contracts from Barchart")

        log = futures_contract.specific_log(self.log)
        if futures_contract.is_spread_contract():
            log.warn("Can't find expiry for multiple leg contract here")
            return missing_contract

        contract_object_with_bc_data = self.get_contract_object_with_bc_data(futures_contract)
        if contract_object_with_bc_data is missing_contract:
            return missing_contract

        expiry_date = contract_object_with_bc_data.expiry_date

        return expiry_date

    def get_contract_object_with_bc_data(self, futures_contract: futuresContract) -> futuresContract:
        """
        Return contract_object with BC config and correct expiry date added

        :param futures_contract:
        :return: modified contract_object
        """

        futures_contract_plus = self._get_contract_object_plus(futures_contract)
        if futures_contract_plus is missing_contract:
            return missing_contract

        futures_contract_plus = futures_contract_plus.update_expiry_dates_one_at_a_time_with_method(
            self._get_actual_expiry_date_given_single_contract_plus)

        return futures_contract_plus

    def _get_contract_object_plus(self, contract_object: futuresContract) -> futuresContract:

        futures_contract_plus = self.barchart_futures_instrument_data.get_bc_futures_instrument(
            contract_object.instrument_code
        )
        if futures_contract_plus is missing_instrument:
            return missing_contract

        futures_contract_plus = (
            contract_object.new_contract_with_replaced_instrument_object(
                futures_contract_plus
            )
        )

        return futures_contract_plus

    def _get_actual_expiry_date_given_single_contract_plus(
            self, futures_contract_plus: futuresContract) -> expiryDate:

        if futures_contract_plus.is_spread_contract():
            self.log.warn("Can't find expiry for multiple leg contract here")
            return missing_contract

        expiry_date = self._barchart.get_expiry_date(futures_contract_plus)

        if expiry_date is missing_contract:
            return missing_contract
        else:
            expiry_date = expiryDate.from_str(expiry_date, format="%m/%d/%y")

        return expiry_date

    def get_list_of_contract_dates_for_instrument_code(self, instrument_code: str):
        raise NotImplementedError(
            "Consider implementing for consistent interface")

    def get_all_contract_objects_for_instrument_code(self, *args, **kwargs):
        raise NotImplementedError(
            "Consider implementing for consistent interface")

    def _get_contract_data_without_checking(
            self, instrument_code: str, contract_date: str) -> futuresContract:
        raise NotImplementedError(
            "Consider implementing for consistent interface")

    def is_contract_in_data(self, *args, **kwargs):
        raise NotImplementedError(
            "Consider implementing for consistent interface")

    def _delete_contract_data_without_any_warning_be_careful(self, instrument_code: str,
                                                             contract_date: str):
        raise NotImplementedError("Barchart is read only")

    def _add_contract_object_without_checking_for_existing_entry(
            self, contract_object: futuresContract):
        raise NotImplementedError("Barchart is read only")
