from sysdata.base_data import baseData
from datetime import datetime
from sysobjects.production.trading_hours.trading_hours import listOfTradingHours

USE_CHILD_CLASS_ERROR = "You need to use a child class of marketInfoData"


class marketInfoData(baseData):
    def get_list_of_instruments(self) -> list:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def update_market_info(self, instr_code: str, epic: str, market_info: dict):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def add_market_info(self, instrument_code: str, epic: str, market_info: dict):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_market_info_for_epic(self, epic: str):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_market_info_for_instrument_code(self, instr_code: str):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_expiry_details(self, epic: str):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    # TODO change name
    def get_trading_hours_for_epic(self, epic) -> listOfTradingHours:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_epic_for_contract(self, contract) -> str:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)


def contract_date_from_expiry_key(expiry_key):
    expiry_code_date = datetime.strptime(f"01-{expiry_key}", "%d-%b-%y")
    return f"{expiry_code_date.strftime('%Y%m')}00"
