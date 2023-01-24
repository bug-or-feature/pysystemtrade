from datetime import datetime
import pytz
from functools import cached_property
from munch import munchify

from syscore.objects import arg_not_supplied
from syscore.dateutils import ISO_DATE_FORMAT
from syscore.exceptions import missingContract, missingData
from sysdata.mongodb.mongo_generic import mongoDataWithMultipleKeys
from sysdata.futures_spreadbet.market_info_data import (
    marketInfoData,
    contract_date_from_expiry_key,
)
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.production.trading_hours.trading_hours import listOfTradingHours
from sysbrokers.IG.ig_trading_hours import parse_trading_hours

INSTRUMENT_COLLECTION = "market_info"


class mongoMarketInfoData(marketInfoData):
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
        self._epic_mappings = {}
        self._expiry_dates = {}

    def __repr__(self):
        return f"mongoMarketInfoData {str(self.mongo_data)}"

    @property
    def mongo_data(self):
        return self._mongo_data

    @cached_property
    def epic_mapping(self) -> dict:
        if len(self._epic_mappings) == 0:
            self._parse_market_info_for_mappings()
        return self._epic_mappings

    @cached_property
    def expiry_dates(self) -> dict:
        if len(self._expiry_dates) == 0:
            self._parse_market_info_for_mappings()
        return self._expiry_dates

    def _parse_market_info_for_mappings(self):
        for instr in self.get_list_of_instruments():
            for result in self.mongo_data._mongo.collection.find(
                {"instrument_code": instr},
                {
                    "_id": 0,
                    "epic": 1,
                    "instrument.expiry": 1,
                    "instrument.expiryDetails.lastDealingDate": 1,
                },
            ):

                doc = munchify(result)
                contract_date_str = (
                    f"{instr}/{contract_date_from_expiry_key(doc.instrument.expiry)}"
                )
                self._epic_mappings[contract_date_str] = doc["epic"]

                date_str = doc.instrument.expiryDetails.lastDealingDate
                last_dealing = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

                self._expiry_dates[contract_date_str] = last_dealing.strftime(
                    ISO_DATE_FORMAT
                )

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
                market_info = munchify(self.get_market_info_for_epic(epic))
                expiry_key = market_info.instrument.expiry
                last_dealing = market_info.instrument.expiryDetails.lastDealingDate
                expiry_date = pytz.utc.localize(
                    datetime.strptime(last_dealing, "%Y-%m-%dT%H:%M")
                )
            except Exception as exc:
                self.log.error(f"Problem getting expiry date for '{epic}': {exc}")
                raise missingContract
            return expiry_key, expiry_date
        else:
            raise missingData

    # TODO change name
    def get_trading_hours_for_epic(self, epic) -> listOfTradingHours:
        try:
            market_info = munchify(self.get_market_info_for_epic(epic))
            trading_hours = parse_trading_hours(market_info.instrument.openingHours)
            return trading_hours
        except Exception as exc:
            self.log.error(f"Problem getting expiry date for '{epic}': {exc}")
            raise missingContract

    def get_epic_for_contract(self, contract) -> str:
        instr_code = contract.instrument_code
        the_date = datetime.strptime(f"{contract.date_str[0:6]}01", "%Y%m%d")
        expiry_key = the_date.strftime("%b-%y").upper()
        result = self.mongo_data._mongo.collection.find_one(
            {"instrument_code": instr_code, "instrument.expiry": expiry_key},
            {"epic": 1},
        )

        if result:
            return result["epic"]
        else:
            raise missingData(f"No epic found for {instr_code} ({expiry_key})")

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
