from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysdata.futures_spreadbet.market_info_data import marketInfoData
from sysproduction.data.generic_production_data import productionDataLayerGeneric


class DiagMarketInfo(productionDataLayerGeneric):
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

    def market_info_for_instrument_code(self, instrument_code: str):
        return self.db_market_info.get_market_info_for_instrument_code(instrument_code)

    def get_epic_selection_info(self, instrument_code: str):
        return self.db_market_info.get_epic_selection_info(instrument_code)

    def get_market_info_for_epic(self, epic: str):
        return self.db_market_info.get_market_info_for_epic(epic)


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
