from sysdata.futures_spreadbet.fsb_epic_history_data import FsbEpicsHistoryData
from sysobjects.epic_history import FsbEpicsHistory
from sysdata.arctic.arctic_connection import arcticData
from syslogging.logger import *
from syscore.constants import success, failure, status
import pandas as pd

EPICS_HISTORY_COLLECTION = "fsb_epics_history"


class ArcticFsbEpicHistoryData(FsbEpicsHistoryData):
    """
    Class to read / write IG epics history data to and from arctic
    """

    def __init__(self, mongo_db=None, log=get_logger("arcticFsbEpicsHistory")):
        super().__init__(log=log)
        self._arctic = arcticData(EPICS_HISTORY_COLLECTION, mongo_db=mongo_db)

    def __repr__(self):
        return repr(self._arctic)

    @property
    def arctic(self):
        return self._arctic

    def get_list_of_instruments(self) -> list:
        # return ['BUXL_fsb','GOLD_fsb','NZD_fsb','NASDAQ_fsb','US10_fsb']
        return self.arctic.get_keynames()

    def get_epic_history(self, instrument_code: str) -> FsbEpicsHistory:
        data = self.arctic.read(instrument_code)
        return FsbEpicsHistory(data)

    def update_epic_history(
        self,
        instrument_code: str,
        epic_history: FsbEpicsHistory,
        remove_duplicates=True,
    ):
        log = self.log.setup(instrument_code=instrument_code)
        existing = self.get_epic_history(instrument_code)
        merged_data = pd.concat([existing, epic_history], axis=0)

        # we need to only drop sequential rows that are duplicates. Sometimes IG
        # initially publishes incorrect epic info, and later corrects it
        if remove_duplicates:
            merged_data = merged_data[~(merged_data.shift() == merged_data).all(axis=1)]
        count = merged_data.shape[0] - existing.shape[0]
        if count > 0:
            log.debug(f"Adding {count} row(s) of epic history for {instrument_code}")
            self.add_epics_history(
                instrument_code, FsbEpicsHistory(merged_data), ignore_duplication=True
            )
        else:
            log.debug(f"No change to epic history for {instrument_code}")

    def add_epics_history(
        self,
        instrument_code: str,
        epics_history: FsbEpicsHistory,
        ignore_duplication=False,
    ) -> status:
        log = self.log.setup(instrument_code=instrument_code)
        if self.is_code_in_data(instrument_code):
            if ignore_duplication:
                pass
            else:
                log.error(f"Data exists for {instrument_code}, delete it first")
                return failure

        data = pd.DataFrame(epics_history)
        # remove duplicate rows
        data = data[~(data.shift() == data).all(axis=1)]

        self.arctic.write(instrument_code, data)
        self.log.debug(
            f"Wrote {len(data)} lines of history for {instrument_code}",
            instrument_code=instrument_code,
        )

        return success

    def delete_epics_history(self, instrument_code: str):
        self._arctic.delete(instrument_code)
        self.log.debug(f"Deleted epic history for {instrument_code} from {self}")
