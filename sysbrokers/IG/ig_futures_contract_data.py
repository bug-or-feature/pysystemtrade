from datetime import datetime
from sysbrokers.broker_futures_contract_data import brokerFuturesContractData
from sysbrokers.broker_instrument_data import brokerFuturesInstrumentData
from sysdata.futures_spreadbet.market_info_data import marketInfoData
from sysdata.data_blob import dataBlob
from sysobjects.contract_dates_and_expiries import expiryDate
from sysobjects.contracts import futuresContract
from sysobjects.production.trading_hours.trading_hours import listOfTradingHours
from syslogdiag.log_to_screen import logtoscreen
from sysbrokers.IG.ig_connection import IGConnection
from syscore.objects import missing_instrument
from syscore.exceptions import missingContract
from syscore.dateutils import contract_month_from_number
from sysbrokers.IG.ig_instruments_data import (
    get_instrument_object_from_config,
)
from sysdata.barchart.bc_connection import bcConnection


class IgFuturesContractData(brokerFuturesContractData):
    def __init__(
        self,
        data_blob: dataBlob,
        broker_conn: IGConnection,
        log=logtoscreen("IgFuturesContractData"),
    ):
        super().__init__(log=log)
        self._dataBlob = data_blob
        self._broker_conn = broker_conn
        self._barchart = bcConnection()

    def __repr__(self):
        return f"IG FSB per contract data: {self._broker_conn}"

    @property
    def broker_conn(self):
        return self._broker_conn

    @property
    def barchart(self):
        return self._barchart

    @property
    def data(self):
        return self._dataBlob

    @property
    def ig_instrument_data(self) -> brokerFuturesInstrumentData:
        return self.data.broker_futures_instrument

    @property
    def market_info_data(self) -> marketInfoData:
        return self.data.db_market_info

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
            raise missingContract

        if self._is_fsb(futures_contract):
            return self._get_fsb_expiry_date(futures_contract)
        else:
            return self._get_futures_expiry_date(futures_contract)

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

        if requery_expiries:
            futures_contract_plus = (
                futures_contract_plus.update_expiry_dates_one_at_a_time_with_method(
                    self._get_actual_expiry_date_given_single_contract_plus
                )
            )

        return futures_contract_plus

    def _is_fsb(self, contract_object: futuresContract) -> bool:
        return contract_object.instrument_code.endswith("_fsb")

    def _get_fsb_expiry_date(self, contract_object: futuresContract) -> expiryDate:

        contract_object_with_config_data = self.get_contract_object_with_config_data(
            contract_object
        )

        expiry_date = contract_object_with_config_data.expiry_date

        return expiry_date

    def _get_futures_expiry_date(self, contract_object: futuresContract) -> expiryDate:
        contract_object_with_config_data = self.get_contract_object_with_config_data(
            contract_object
        )

        barchart_id = self.get_barchart_id(contract_object_with_config_data)
        future_expiry = self.barchart.get_expiry_date_for_symbol(barchart_id)
        if future_expiry is None:
            self.log.warn("Unable to get expiry from broker, calculating approx date")
            exp_date = self.calc_approx_expiry(contract_object)
        else:
            exp_date = expiryDate.from_str(future_expiry, format="%m/%d/%y")
            exp_date.source = "B"

        return exp_date

    def _get_contract_object_plus(
        self, contract_object: futuresContract
    ) -> futuresContract:

        futures_contract_plus = (
            self.ig_instrument_data.get_futures_instrument_object_with_ig_data(
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

        if self._is_fsb(futures_contract_plus):
            expiry_date = self._get_expiry_fsb(futures_contract_plus)
            date_format_str = "%Y-%m-%d %H:%M:%S"
        else:
            expiry_date = self._get_expiry_future(futures_contract_plus)
            date_format_str = "%m/%d/%y"

        if expiry_date is None:
            self.log.warn(
                f"Failed to get expiry for contract {futures_contract_plus}, returning approx date"
            )
            return self.calc_approx_expiry(futures_contract_plus)
        else:
            expiry_date = expiryDate.from_str(expiry_date, format=date_format_str)
            expiry_date.source = "B"

        return expiry_date

    def calc_approx_expiry(self, futures_contract_plus):
        datestring = futures_contract_plus.date_str
        if datestring[6:8] == "00":
            datestring = datestring[:6] + "28"
        expiry_date = expiryDate.from_str(datestring, format="%Y%m%d")
        expiry_date.source = "E"
        return expiry_date

    def _get_expiry_fsb(self, futures_contract_plus: futuresContract) -> str:
        if futures_contract_plus.key in self.market_info_data.expiry_dates:
            date_str = self.market_info_data.expiry_dates[futures_contract_plus.key]
        else:
            date_str = None

        return date_str

    def _get_expiry_future(self, contract_object: futuresContract) -> str:
        barchart_id = self.get_barchart_id(contract_object)
        date_str = self.barchart.get_expiry_date_for_symbol(barchart_id)
        return date_str

    def get_min_tick_size_for_contract(self, contract_object: futuresContract) -> float:
        return 0.01

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

    def get_trading_hours_for_contract(
        self, futures_contract: futuresContract
    ) -> listOfTradingHours:
        return self.market_info_data.get_trading_hours_for_epic(futures_contract)

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
            futures_contract.instrument_code, config=self.ig_instrument_data.config
        )
        # bc_symbol = config_data.bc_code
        symbol = f"{config_data.bc_code}{contract_month_from_number(int(date_obj.strftime('%m')))}{date_obj.strftime('%y')}"
        return symbol
