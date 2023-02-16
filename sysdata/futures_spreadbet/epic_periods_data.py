from sysdata.base_data import baseData
from datetime import datetime
from sysobjects.production.trading_hours.trading_hours import listOfTradingHours

USE_CHILD_CLASS_ERROR = "You need to use a child class of epicPeriodsData"


class epicPeriodsData(baseData):

    def get_list_of_instruments(self) -> list:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def update_epic_periods(self, instr_code: str, epic_periods: dict):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def add_epic_periods(self, instr_code: str, epic_periods: dict):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_epic_periods_for_instrument_code(self, instr_code: str):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)
