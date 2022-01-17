import datetime
from sysbrokers.broker_futures_contract_data import brokerFuturesContractData
from sysobjects.contract_dates_and_expiries import expiryDate
from sysobjects.contracts import futuresContract
from syslogdiag.log_to_screen import logtoscreen
from sysbrokers.IG.ig_connection import IGConnection
from sysdata.barchart.bc_connection import bcConnection
from sysbrokers.IG.ig_instruments_data import IgFuturesInstrumentData
from sysdata.barchart.bc_instruments_data import BarchartFuturesInstrumentData
from syscore.objects import missing_contract, missing_instrument
from syscore.dateutils import get_datetime_from_datestring


class IgFuturesContractData(brokerFuturesContractData):
    def __init__(self, broker_conn: IGConnection, log=logtoscreen("IgFuturesContractData")):
        super().__init__(log=log)
        self._igconnection = broker_conn
        self._barchart = bcConnection()
        self._instrument_data = IgFuturesInstrumentData(broker_conn, log=self.log)
        self._bc_instrument_data = BarchartFuturesInstrumentData(log=self.log)

    def __repr__(self):
        return f"IG FSB per contract data: {self._igconnection}"

    @property
    def igconnection(self):
        return self._igconnection

    @property
    def barchart(self):
        return self._barchart

    @property
    def ig_instrument_data(self) -> IgFuturesInstrumentData:
        return self._instrument_data

    @property
    def bc_instrument_data(self) -> BarchartFuturesInstrumentData:
        return self._bc_instrument_data

    def get_actual_expiry_date_for_single_contract(
        self, futures_contract: futuresContract
    ) -> expiryDate:
        """
        Get the actual expiry date of a contract

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
            return missing_contract

        contract_object_with_config_data = self.get_contract_object_with_config_data(
            futures_contract
        )
        if contract_object_with_config_data is missing_contract:
            return missing_contract

        expiry_date = contract_object_with_config_data.expiry_date

        return expiry_date

    def get_contract_object_with_config_data(
        self, futures_contract: futuresContract, requery_expiries: bool = True
    ) -> futuresContract:
        """
        Return contract_object with config data and correct expiry date added

        :param futures_contract:
        :return: modified contract_object
        :param requery_expiries:
        :type requery_expiries:
        """

        futures_contract_plus = self._get_contract_object_plus(futures_contract)
        if futures_contract_plus is missing_contract:
            return missing_contract

        if requery_expiries:
            futures_contract_plus = (
                futures_contract_plus.update_expiry_dates_one_at_a_time_with_method(
                    self._get_actual_expiry_date_given_single_contract_plus
                )
            )

        return futures_contract_plus

    def _get_contract_object_plus(
        self, contract_object: futuresContract
    ) -> futuresContract:

        if self._is_futures_spread_bet(contract_object):
            futures_contract_plus = (
                self.ig_instrument_data.get_ig_fsb_instrument(
                    contract_object.instrument_code
                )
            )
        else:
            futures_contract_plus = (
                self.bc_instrument_data.get_bc_futures_instrument(
                    contract_object.instrument_code
                )
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
        self, futures_contract_plus: futuresContract
    ) -> expiryDate:

        if futures_contract_plus.is_spread_contract():
            self.log.warn("Can't find expiry for multiple leg contract here")
            return missing_contract

        date_format_str = "%Y-%m-%dT%H:%M"
        if self._is_futures_spread_bet(futures_contract_plus):
            expiry_date = self.igconnection.get_expiry_date(futures_contract_plus)
        else:
            expiry_date = self._barchart.get_expiry_date(futures_contract_plus)
            date_format_str = "%m/%d/%y"

        if expiry_date is missing_contract or expiry_date is None:
            self.log.warn(
                f"Failed to get expiry for contract {futures_contract_plus}, returning approx date"
            )
            datestring = futures_contract_plus.date_str
            if datestring[6:8] == "00":
                datestring = datestring[:6] + "01"
            return expiryDate.from_str(datestring, format="%Y%m%d")
        else:
            expiry_date = expiryDate.from_str(expiry_date, format=date_format_str)

        return expiry_date

    # TODO common
    def _is_futures_spread_bet(self, contract_object: futuresContract):
        return "_fsb" in contract_object.instrument_code

    def get_min_tick_size_for_contract(self, contract_object: futuresContract) -> float:
        raise NotImplementedError("Not implemented! build it now")

    def is_contract_okay_to_trade(self, futures_contract: futuresContract) -> bool:
        raise NotImplementedError("Not implemented! build it now")

    def is_contract_conservatively_okay_to_trade(
        self, futures_contract: futuresContract
    ) -> bool:
        raise NotImplementedError("Not implemented! build it now")

    def less_than_N_hours_of_trading_left_for_contract(
        self, contract_object: futuresContract, N_hours: float = 1.0
    ) -> bool:
        raise NotImplementedError("Not implemented! build it now")

    def get_trading_hours_for_contract(self, futures_contract: futuresContract) -> list:
        raise NotImplementedError("Not implemented! build it now")

    def get_conservative_trading_hours_for_contract(
        self, futures_contract: futuresContract
    ) -> list:
        raise NotImplementedError("Not implemented! build it now")

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
        raise NotImplementedError("Consider implementing for consistent interface")

    def _add_contract_object_without_checking_for_existing_entry(
        self, contract_object: futuresContract
    ):
        raise NotImplementedError("Consider implementing for consistent interface")
