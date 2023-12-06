from sysdata.data_blob import dataBlob
from sysdata.futures_spreadbet.fsb_epic_history_data import FsbEpicsHistoryData
from sysdata.futures_spreadbet.epic_periods_data import epicPeriodsData
from sysobjects.epic_history import FsbEpicsHistory
from sysproduction.data.generic_production_data import productionDataLayerGeneric
from sysproduction.data.production_data_objects import (
    get_class_for_data_type,
    FSB_EPIC_HISTORY_DATA,
    EPIC_PERIODS_DATA,
)


class DiagFsbEpics(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                get_class_for_data_type(FSB_EPIC_HISTORY_DATA),
            ]
        )
        return data

    @property
    def db_fsb_epic_history_data(self) -> FsbEpicsHistoryData:
        return self.data.db_fsb_epic_history

    def get_epic_history(self, instrument_code: str) -> FsbEpicsHistory:
        epic_history = self.db_fsb_epic_history_data.get_epic_history(instrument_code)

        return epic_history


class UpdateFsbEpics(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                get_class_for_data_type(FSB_EPIC_HISTORY_DATA),
            ]
        )
        return data

    @property
    def db_fsb_epic_history_data(self) -> FsbEpicsHistoryData:
        return self.data.db_fsb_epic_history

    def delete_epic_history(self, instrument_code: str):
        self.db_fsb_epic_history_data.delete_epics_history(instrument_code)


class UpdateEpicPeriods(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                get_class_for_data_type(EPIC_PERIODS_DATA)
            ]
        )
        return data

    @property
    def db_epic_periods(self) -> epicPeriodsData:
        return self.data.db_epic_periods

    def delete_epic_periods(self, instrument_code: str):
        self.db_epic_periods.delete_epic_periods_for_instrument_code(instrument_code)
