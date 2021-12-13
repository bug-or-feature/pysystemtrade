from datetime import datetime

from sysbrokers.IG.ig_connection import ConnectionIG
from sysbrokers.IG.ig_instruments_data import IgFsbInstrumentData
from sysbrokers.IG.ig_positions import from_ig_positions_to_dict
from sysbrokers.broker_contract_position_data import brokerContractPositionData
from syscore.objects import arg_not_supplied, missing_contract
from sysdata.futures.contracts import futuresContractData
from sysdata.mongodb.mongo_futures_contracts import mongoFuturesContractData
from sysdata.production.timed_storage import classStrWithListOfEntriesAsListOfDicts
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contract_dates_and_expiries import contractDate
from sysobjects.contracts import futuresContract
from sysobjects.production.positions import contractPosition, listOfContractPositions


class IgContractPositionData(brokerContractPositionData):
    def __init__(self, log=logtoscreen("IgContractPositionData")):
        self._igconnection = ConnectionIG()
        self._contract_data = mongoFuturesContractData()
        super().__init__(log=log)

    @property
    def igconnection(self) -> ConnectionIG:
        return self._igconnection

    def __repr__(self):
        return "IG Futures per contract position data %s" % str(self.igconnection)

    @property
    def contract_data(self) -> futuresContractData:
        return self._contract_data

    @property
    def futures_instrument_data(self) -> IgFsbInstrumentData:
        return IgFsbInstrumentData(log=self.log)

    def get_all_current_positions_as_list_with_contract_objects(
        self, account_id=arg_not_supplied
    ) -> listOfContractPositions:

        all_positions = self._get_all_futures_positions_as_raw_list(
            account_id=account_id
        )
        current_positions = []
        for position_entry in all_positions:
            contract_position_object = self._get_contract_position_for_raw_entry(
                position_entry
            )
            if contract_position_object is missing_contract:
                continue
            else:
                current_positions.append(contract_position_object)
        list_of_contract_positions = listOfContractPositions(current_positions)
        list_of_contract_positions_no_duplicates = (
            list_of_contract_positions.sum_for_contract()
        )

        return list_of_contract_positions_no_duplicates

    def _get_contract_position_for_raw_entry(self, position_entry) -> contractPosition:
        position = position_entry["position"]
        if position_entry["dir"] == "SELL":
            position = position * -1
        if position == 0:
            return missing_contract
        epic = position_entry["symbol"]
        instrument_code = (
            self.futures_instrument_data.get_instrument_code_from_broker_code(epic)
        )
        expiry_key = position_entry["expiry"]
        contract = futuresContract(
            instrument_code,
            contractDate(self.get_actual_expiry(instrument_code, expiry_key)),
        )
        contract_position_object = contractPosition(position, contract)

        return contract_position_object

    def get_actual_expiry(self, instr_code, expiry_key):
        expiry_code_date = datetime.strptime(f"01-{expiry_key}", "%d-%b-%y")
        contract = self.contract_data.get_contract_object(
            instr_code, f"{expiry_code_date.strftime('%Y%m')}00"
        )
        actual_expiry = contract.expiry_date
        return actual_expiry.strftime("%Y%m%d")

    def _get_all_futures_positions_as_raw_list(
        self, account_id: str = arg_not_supplied
    ) -> list:
        raw_positions = self.igconnection.get_positions()
        dict_of_positions = from_ig_positions_to_dict(
            raw_positions, account_id=account_id
        )
        positions = dict_of_positions.get("FSB", [])

        return positions

    def get_position_as_df_for_contract_object(self, *args, **kwargs):
        raise Exception("Only current position data available from IG")

    def update_position_for_contract_object(self, *args, **kwargs):
        raise Exception("IG position data is read only")

    def delete_last_position_for_contract_object(self, *args, **kwargs):
        raise Exception("IG position data is read only")

    def _get_series_for_args_dict(self, *args, **kwargs):
        raise Exception("Only current position data available from IG")

    def _update_entry_for_args_dict(self, *args, **kwargs):
        raise Exception("IG position data is read only")

    def _delete_last_entry_for_args_dict(self, *args, **kwargs):
        raise Exception("IG position data is read only")

    def _get_list_of_args_dict(self) -> list:
        raise Exception("Args dict not used for IG")

    def get_list_of_instruments_with_any_position(self):
        raise Exception("Not implemented for IG")

    def _get_series_dict_with_data_class_for_args_dict(
        self, args_dict: dict
    ) -> classStrWithListOfEntriesAsListOfDicts:
        pass

    def _write_series_dict_for_args_dict(
        self,
        args_dict: dict,
        class_str_with_series_as_list_of_dicts: classStrWithListOfEntriesAsListOfDicts,
    ):
        pass
