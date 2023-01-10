from syscore.objects import missing_instrument
from syscore.exceptions import missingContract
from sysdata.barchart.bc_instruments_data import BarchartFuturesInstrumentData
from sysdata.barchart.bc_connection import bcConnection
from sysbrokers.broker_futures_contract_data import brokerFuturesContractData
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contract_dates_and_expiries import expiryDate
from sysobjects.contracts import futuresContract
from syscore.dateutils import get_datetime_from_datestring
import datetime


class BarchartFuturesContractData(brokerFuturesContractData):
    def __init__(self, barchart=None, log=logtoscreen("barchartFuturesContractData")):
        super().__init__(log=log)
        if barchart is None:
            barchart = bcConnection()
        self._barchart = barchart

    def __repr__(self):
        return f"Barchart Futures per contract data: {self._barchart}"

    @property
    def barchart(self):
        return self._barchart

    @property
    def barchart_futures_instrument_data(self) -> BarchartFuturesInstrumentData:
        return BarchartFuturesInstrumentData(log=self.log)

    def get_actual_expiry_date_for_single_contract(
        self, futures_contract: futuresContract
    ) -> expiryDate:
        """
        Get the actual expiry date of a contract from Barchart

        :param futures_contract: type futuresContract
        :return: YYYYMMDD or None
        """

        rough_expiry = get_datetime_from_datestring(futures_contract.date_str)
        if rough_expiry < datetime.datetime(2000, 1, 1):
            raise Exception(
                "Cannot get expiry dates for older expired contracts from Barchart"
            )

        log = futures_contract.specific_log(self.log)
        if futures_contract.is_spread_contract():
            log.warn("Can't find expiry for multiple leg contract here")
            raise missingContract

        contract_object_plus = self.get_contract_object_with_config_data(
            futures_contract
        )

        expiry_date = contract_object_plus.expiry_date

        return expiry_date

    def get_contract_object_with_config_data(
        self, futures_contract: futuresContract
    ) -> futuresContract:
        """
        Return contract_object with BC config and correct expiry date added

        :param futures_contract:
        :return: modified contract_object
        """

        futures_contract_plus = self._get_contract_object_plus(futures_contract)

        futures_contract_plus = (
            futures_contract_plus.update_expiry_dates_one_at_a_time_with_method(
                self._get_actual_expiry_date_given_single_contract_plus
            )
        )

        return futures_contract_plus

    def _get_contract_object_plus(
        self, contract_object: futuresContract
    ) -> futuresContract:

        futures_contract_plus = (
            self.barchart_futures_instrument_data.get_bc_futures_instrument(
                contract_object.instrument_code
            )
        )
        if futures_contract_plus is missing_instrument:
            raise missingContract

        futures_contract_plus = (
            contract_object.new_contract_with_replaced_instrument_object(
                futures_contract_plus
            )
        )

        return futures_contract_plus

    def _get_actual_expiry_date_given_single_contract_plus(
        self, futures_contract_plus: futuresContract
    ) -> expiryDate:

        if futures_contract_plus.is_spread_contract():
            self.log.warn("Can't find expiry for multiple leg contract here")
            raise missingContract

        expiry_date = self._barchart.get_expiry_date(futures_contract_plus)

        if expiry_date is None:
            self.log.warn(
                f"Failed to get expiry for contract {futures_contract_plus}, returning approx date"
            )
            datestring = futures_contract_plus.date_str
            if datestring[6:8] == "00":
                datestring = datestring[:6] + "01"
            return expiryDate.from_str(datestring, format="%Y%m%d")
        else:
            expiry_date = expiryDate.from_str(expiry_date, format="%m/%d/%y")

        return expiry_date

    def get_list_of_contract_dates_for_instrument_code(self, instrument_code: str):
        raise NotImplementedError("Consider implementing for consistent interface")

    def get_all_contract_objects_for_instrument_code(self, *args, **kwargs):
        raise NotImplementedError("Consider implementing for consistent interface")

    def _get_contract_data_without_checking(
        self, instrument_code: str, contract_date: str
    ) -> futuresContract:
        raise NotImplementedError("Consider implementing for consistent interface")

    def is_contract_in_data(self, *args, **kwargs):
        raise NotImplementedError("Consider implementing for consistent interface")

    def _delete_contract_data_without_any_warning_be_careful(
        self, instrument_code: str, contract_date: str
    ):
        raise NotImplementedError("Barchart is read only")

    def _add_contract_object_without_checking_for_existing_entry(
        self, contract_object: futuresContract
    ):
        raise NotImplementedError("Barchart is read only")

    def get_min_tick_size_for_contract(self, contract_object: futuresContract) -> float:
        raise NotImplementedError("Barchart is a source of data, not a broker")

    def is_contract_okay_to_trade(self, futures_contract: futuresContract) -> bool:
        raise NotImplementedError("Barchart is a source of data, not a broker")

    def less_than_N_hours_of_trading_left_for_contract(
        self, contract_object: futuresContract, N_hours: float = 1.0
    ) -> bool:
        raise NotImplementedError("Barchart is a source of data, not a broker")

    def get_trading_hours_for_contract(self, futures_contract: futuresContract) -> list:
        raise NotImplementedError("Barchart is a source of data, not a broker")
