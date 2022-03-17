from sysdata.base_data import baseData
from sysobjects.epic_history import FsbEpicsHistory
from syscore.objects import status

USE_CHILD_CLASS_ERROR = "You need to use a child class of FsbHistoryData"


class FsbEpicsHistoryData(baseData):

    def get_list_of_instruments(self) -> list:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_epic_history(self, instrument_code: str) -> FsbEpicsHistory:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def update_epic_history(
        self, instrument_code: str, epic_history: FsbEpicsHistory
    ):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def add_epics_history(
        self,
        instrument_code: str,
        epics_history: FsbEpicsHistory
    ) -> status:

        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def is_code_in_data(self, instrument_code: str) -> bool:
        return instrument_code in self.get_list_of_instruments()
