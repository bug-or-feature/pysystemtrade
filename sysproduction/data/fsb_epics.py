from sysdata.arctic.arctic_fsb_epics_history import ArcticFsbEpicHistoryData
from sysdata.mongodb.mongo_epic_periods import mongoEpicPeriodsData
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysdata.data_blob import dataBlob
from sysdata.futures_spreadbet.fsb_epic_history_data import FsbEpicsHistoryData
from sysdata.futures_spreadbet.epic_periods_data import epicPeriodsData
from sysdata.futures_spreadbet.market_info_data import marketInfoData
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


class UpdateFsbEpics(productionDataLayerGeneric):
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

    def delete_epic_history(self, instrument_code: str):
        self.db_fsb_epic_history_data.delete_epics_history(instrument_code)


class UpdateEpicPeriods(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                mongoEpicPeriodsData,
            ]
        )
        return data

    @property
    def db_epic_periods(self) -> epicPeriodsData:
        return self.data.db_epic_periods

    def delete_epic_periods(self, instrument_code: str):
        self.db_epic_periods.delete_epic_periods_for_instrument_code(instrument_code)


class UpdateMarketInfo(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                mongoMarketInfoData,
            ]
        )
        return data

    @property
    def db_market_info(self) -> marketInfoData:
        return self.data.db_market_info

    def delete_for_instrument_code(self, instrument_code: str):
        self.db_market_info.delete_for_instrument_code(instrument_code)
