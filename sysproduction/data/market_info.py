import datetime
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

    def update_market_info_for_epic(self, instr, epic, check_historic=False):
        try:
            info = self.data.broker_conn.get_market_info(epic)
            if check_historic:
                historic = self._get_historic_data_for_epic(epic)
                if historic is not None:
                    info["historic"] = historic
            self.db_market_info.update_market_info(instr, epic, info)
        except Exception as exc:
            msg = (
                f"Problem updating market info for epic '{epic}' ({instr}) "
                f"- check config: {exc}"
            )
            self.data.log.error(msg)

    def update_historic_market_info_for_epic(self, epic):
        try:
            info = self.db_market_info.get_market_info_for_epic(epic)
            historic = self._get_historic_data_for_epic(epic)
            if historic is not None:
                info["historic"] = historic
            instr_code = self.db_market_info.instr_code[epic]
            self.db_market_info.update_market_info(instr_code, epic, info)
        except Exception as exc:
            msg = (
                f"Problem updating historic market info for epic '{epic}'"
                f"- check config: {exc}"
            )
            self.data.log.error(msg)

    def _get_historic_data_for_epic(self, epic):

        historic = dict(
            last_modified_utc=datetime.datetime.utcnow(),
        )

        res = "D"
        try:

            hist_df = self.data.broker_conn.get_historical_fsb_data_for_epic(
                epic=epic,
                bar_freq=res,
                numpoints=1,
                warn_for_nans=True,
            )
            hist_dict = hist_df.to_dict(orient="records")
            historic["timestamp"] = hist_df.index[-1]
            historic["bid"] = hist_dict[0]["Close.bid"]
            historic["ask"] = hist_dict[0]["Close.ask"]
            historic["bar_freq"] = res

            return historic

        except Exception as exc:
            msg = (
                f"Problem getting historic data for '{epic}' at "
                f"resolution '{res}': {exc}"
            )
            self.data.log.error(msg)

        return historic
