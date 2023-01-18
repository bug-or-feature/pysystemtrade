from datetime import datetime
import pytz
from syscore.objects import arg_not_supplied
from sysdata.futures_spreadbet.market_info_data import MarketInfoData
from sysdata.mongodb.mongo_generic import mongoDataWithMultipleKeys
from syslogdiag.log_to_screen import logtoscreen
from syscore.exceptions import missingContract, missingData

INSTRUMENT_COLLECTION = "market_info"


class mongoMarketInfoData(MarketInfoData):
    """
    Read and write mongo data class for market info
    """

    def __init__(
        self, mongo_db=arg_not_supplied, log=logtoscreen("mongoMarketInfoData")
    ):

        super().__init__(log=log)
        self._mongo_data = mongoDataWithMultipleKeys(
            INSTRUMENT_COLLECTION, mongo_db=mongo_db
        )

    def __repr__(self):
        return f"mongoMarketInfoData {str(self.mongo_data)}"

    @property
    def mongo_data(self):
        return self._mongo_data

    def add_market_info(self, instrument_code: str, epic: str, market_info: dict):
        self.log.msg(f"Adding market info for '{epic}'")
        self._save(instrument_code, epic, market_info)

    def update_market_info(self, instrument_code: str, epic: str, market_info: dict):
        self.log.msg(f"Updating market info for '{epic}'")
        self._save(instrument_code, epic, market_info, allow_overwrite=True)

    def get_market_info_for_epic(self, epic: str):
        return self.mongo_data._mongo.collection.find_one({"epic": epic})

    def get_market_info_for_instrument_code(self, instr_code: str):
        results = []
        for doc in self.mongo_data._mongo.collection.find(
            {"instrument_code": instr_code}
        ):
            results.append(doc)

        return results

    def get_list_of_instruments(self):
        results = self.mongo_data._mongo.collection.distinct("instrument_code")
        return results

    def get_expiry_details(self, epic: str):
        if epic is not None:
            try:
                market_info = self.get_market_info_for_epic(epic)
                expiry_key = market_info["instrument"]["expiry"]
                last_dealing = market_info["instrument"]["expiryDetails"][
                    "lastDealingDate"
                ]
                expiry_date = pytz.utc.localize(
                    datetime.strptime(last_dealing, "%Y-%m-%dT%H:%M")
                )
            except Exception as exc:
                self.log.error(f"Problem getting expiry date for '{epic}': {exc}")
                raise missingContract
            return expiry_key, expiry_date
        else:
            raise missingData

    def _save(
        self, instrument_code: str, epic: str, market_info: dict, allow_overwrite=False
    ):
        market_info["last_modified_utc"] = datetime.utcnow()
        dict_of_keys = {
            "instrument_code": instrument_code,
            "epic": epic,
        }
        self.mongo_data.add_data(
            dict_of_keys=dict_of_keys,
            data_dict=market_info,
            allow_overwrite=allow_overwrite,
        )
