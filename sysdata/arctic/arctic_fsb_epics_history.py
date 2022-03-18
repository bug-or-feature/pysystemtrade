from sysdata.futures_spreadbet.fsb_epic_history_data import FsbEpicsHistoryData
from sysobjects.epic_history import FsbEpicsHistory
from sysdata.arctic.arctic_connection import arcticData
from syslogdiag.log_to_screen import logtoscreen
from syscore.objects import success, failure, status
import pandas as pd

EPICS_HISTORY_COLLECTION = "fsb_epics_history"


class ArcticFsbEpicHistoryData(FsbEpicsHistoryData):
    """
    Class to read / write IG epics history data to and from arctic
    """

    def __init__(self, mongo_db=None, log=logtoscreen("arcticFsbEpicsHistory")):
        super().__init__(log=log)
        self._arctic = arcticData(EPICS_HISTORY_COLLECTION, mongo_db=mongo_db)

    def __repr__(self):
        return repr(self._arctic)

    @property
    def arctic(self):
        return self._arctic

    def get_list_of_instruments(self) -> list:
        #return ["GOLD_fsb","EDOLLAR_fsb","VIX_fsb","V2X_fsb","ASX_fsb","AUD_fsb"]
        return self.arctic.get_keynames()

    def get_epic_history(self, instrument_code: str) -> FsbEpicsHistory:
        data = self.arctic.read(instrument_code)
        return FsbEpicsHistory(data)

    def update_epic_history(self, instrument_code: str, epic_history: FsbEpicsHistory, remove_duplicates=True):
        log = self.log.setup(instrument_code=instrument_code)
        existing = self.get_epic_history(instrument_code)
        if remove_duplicates:
            epic_history = epic_history.drop_duplicates()
        count = epic_history.shape[0] - existing.shape[0]
        if count > 0:
            log.msg(f"Adding {count} row(s) of epic history for {instrument_code}")
            self.add_epics_history(
                instrument_code,
                epic_history,
                ignore_duplication=True
            )
        else:
            log.msg(f"No change to epic history for {instrument_code}")

    def add_epics_history(
            self,
            instrument_code: str,
            epics_history: FsbEpicsHistory,
            ignore_duplication=False
    ) -> status:

        log = self.log.setup(instrument_code=instrument_code)
        if self.is_code_in_data(instrument_code):
            if ignore_duplication:
                pass
            else:
                log.error(f"Data exists for {instrument_code}, delete it first")
                return failure

        epics_history_data = pd.DataFrame(epics_history)

        self.arctic.write(instrument_code, epics_history_data)
        self.log.msg(
            f"Wrote {len(epics_history_data)} lines of history for {instrument_code}",
            instrument_code=instrument_code,
        )

        return success
