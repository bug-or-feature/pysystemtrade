import pandas as pd
from sysdata.base_data import baseData
from sysobjects.epic_history import FsbEpicHistory

USE_CHILD_CLASS_ERROR = "You need to use a child class of FsbHistoryData"


class FsbHistoryData(baseData):

    def get_list_of_instruments(self) -> list:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_epic_history(self, instrument_code: str):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def update_epic_history(
        self, instrument_code: str, epic_history: FsbEpicHistory
    ):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def read_epic_history(self, instrument_code: str) -> pd.DataFrame:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)