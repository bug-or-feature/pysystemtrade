from sysdata.arctic.arctic_fsb_epics_history import ArcticFsbEpicHistoryData
from sysdata.data_blob import dataBlob
from sysdata.futures_spreadbet.fsb_epic_history_data import FsbEpicsHistoryData
from sysobjects.epic_history import FsbEpicsHistory
from sysproduction.data.generic_production_data import productionDataLayerGeneric


class DiagFsbEpics(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                ArcticFsbEpicHistoryData,
            ]
        )
        return data

    @property
    def db_fsb_epic_history_data(self) -> FsbEpicsHistoryData:
        return self.data.db_fsb_epic_history

    def get_epic_history(self, instrument_code: str) -> FsbEpicsHistory:
        epic_history = self.db_fsb_epic_history_data.get_epic_history(instrument_code)

        return epic_history
