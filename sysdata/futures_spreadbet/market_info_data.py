from sysdata.base_data import baseData
from syscore.objects import status

USE_CHILD_CLASS_ERROR = "You need to use a child class of MarketInfoData"


class MarketInfoData(baseData):
    def get_list_of_instruments(self) -> list:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def update_market_info(self, instr_code: str, epic: str, market_info: dict):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def add_market_info(self, instrument_code: str, epic: str, market_info: dict):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_market_info_for_instrument_code(self, instr_code: str):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_expiry_details(self, epic: str):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    # def get_market_info(self, instrument_code: str) -> dict:
    #     raise NotImplementedError(USE_CHILD_CLASS_ERROR)
