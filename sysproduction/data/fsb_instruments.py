from sysdata.data_blob import dataBlob
from sysdata.config.production_config import get_production_config
from sysdata.futures_spreadbet.market_info_data import marketInfoData

from sysobjects.production.trading_hours.trading_hours import listOfTradingHours
from sysobjects.contracts import futuresContract
from syscore.constants import arg_not_supplied
from syscore.exceptions import missingData
from sysproduction.data.instruments import diagInstruments
from sysproduction.data.production_data_objects import (
    STORED_SPREAD_DATA,
    get_class_for_data_type,
    FUTURES_INSTRUMENT_DATA,
    MARKET_INFO_DATA,
)


class diagFsbInstruments(diagInstruments):
    def __init__(self, data: dataBlob = arg_not_supplied):
        super().__init__(data)
        config = get_production_config()
        self._ig_config = config.get_element("ig_markets")
        self._min_bet_overrides = config.get_element_or_default("min_bet_overrides", {})

    def _add_required_classes_to_data(self, data: dataBlob) -> dataBlob:
        data.add_class_list(
            [
                get_class_for_data_type(FUTURES_INSTRUMENT_DATA),
                get_class_for_data_type(STORED_SPREAD_DATA),
                get_class_for_data_type(MARKET_INFO_DATA),
            ]
        )
        return data

    @property
    def db_market_info_data(self) -> marketInfoData:
        return self.data.db_market_info

    # def get_expiry_details(self, epic: str):
    #     return self.db_market_info_data.get_expiry_details(epic)

    def get_trading_hours_for_epic(self, key) -> listOfTradingHours:
        if isinstance(key, futuresContract):
            try:
                epic = self.db_market_info_data.get_epic_for_contract(key)
                return self.db_market_info_data.get_trading_hours_for_epic(epic)
            except missingData as exc:
                self.log.warning(f"Problem getting trading hours: {exc}")

        return self.db_market_info_data.get_trading_hours_for_epic(key)

    def get_minimum_bet(self, instr_code: str, env: str = None):
        is_live = env and env in self._ig_config["live_types"]
        if not is_live and instr_code in self._min_bet_overrides:
            return self._min_bet_overrides[instr_code]
        else:
            return self.get_point_size(instr_code)
