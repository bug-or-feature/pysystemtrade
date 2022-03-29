import datetime
from datetime import datetime
from sysbrokers.broker_futures_contract_data import brokerFuturesContractData
from sysobjects.contract_dates_and_expiries import expiryDate
from sysobjects.contracts import futuresContract
from syslogdiag.log_to_screen import logtoscreen
from sysbrokers.IG.ig_connection import IGConnection
from syscore.objects import missing_contract, missing_instrument
from syscore.dateutils import contract_month_from_number
from sysbrokers.IG.ig_instruments_data import (
    IgFuturesInstrumentData,
    get_instrument_object_from_config
)


class IgFuturesContractData(brokerFuturesContractData):
    def __init__(
            self,
            broker_conn: IGConnection,
            instr_data: IgFuturesInstrumentData = None,
            log = logtoscreen("IgFuturesContractData")
    ):
        super().__init__(log=log)
        self._igconnection = broker_conn
        if instr_data is None:
            self._instrument_data = IgFuturesInstrumentData(broker_conn, log=self.log)
        else:
            self._instrument_data = instr_data

    def __repr__(self):
        return f"IG FSB per contract data: {self._igconnection}"

    @property
    def igconnection(self):
        return self._igconnection

    @property
    def ig_instrument_data(self) -> IgFuturesInstrumentData:
        return self._instrument_data

    def get_actual_expiry_date_for_single_contract(
        self, futures_contract: futuresContract
    ) -> expiryDate:
        """
        Get the actual expiry date of a contract

        :param futures_contract: type futuresContract
        :return: YYYYMMDD or None
        """

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

        futures_contract_plus = (
            self.ig_instrument_data.get_ig_fsb_instrument(
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
        if futures_contract_plus.key in self.ig_instrument_data.expiry_dates:
            expiry_date = self.ig_instrument_data.expiry_dates[futures_contract_plus.key]
            date_format_str = "%Y-%m-%d %H:%M:%S"
        else:
            expiry_date = missing_contract

        if expiry_date is missing_contract or expiry_date is None:
            self.log.warn(
                f"Failed to get expiry for contract {futures_contract_plus}, returning approx date"
            )
            datestring = futures_contract_plus.date_str
            if datestring[6:8] == "00":
                datestring = datestring[:6] + "28"
            expiry_date = expiryDate.from_str(datestring, format="%Y%m%d")
            expiry_date.source = "E"
            return expiry_date
        else:
            expiry_date = expiryDate.from_str(expiry_date, format=date_format_str)
            expiry_date.source = "B"

        return expiry_date

    def get_min_tick_size_for_contract(self, contract_object: futuresContract) -> float:
        raise NotImplementedError("Not implemented! build it now")

    def is_contract_okay_to_trade(self, futures_contract: futuresContract) -> bool:
        #print(f"futures_contract: {futures_contract.key}")
        #expiry_dates = self.ig_instrument_data.expiry_dates
        #has_expiry = futures_contract.key in self.ig_instrument_data.expiry_dates
        # TODO improve, eg trading hours etc
        has_epic = futures_contract.key in self.ig_instrument_data.epic_mapping
        return has_epic

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

    def get_barchart_id(self, futures_contract: futuresContract) -> str:
        """
        Converts a contract identifier from internal format (GOLD/20200900), into Barchart format (GCM20)
        :param futures_contract: the internal format identifier
        :type futures_contract: futuresContract
        :return: Barchart format identifier
        :rtype: str
        """
        date_obj = datetime.strptime(futures_contract.contract_date.date_str, "%Y%m00")

        config_data = get_instrument_object_from_config(
            futures_contract.instrument_code,
            config=self.ig_instrument_data.config
        )
        #bc_symbol = config_data.bc_code
        symbol = f"{config_data.bc_code}{contract_month_from_number(int(date_obj.strftime('%m')))}{date_obj.strftime('%y')}"
        return symbol
