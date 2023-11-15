import re

import pandas as pd
import pymongo
import pytz
from functools import cached_property
from munch import munchify
from syscore.constants import arg_not_supplied
from syscore.dateutils import ISO_DATE_FORMAT
from syscore.exceptions import missingContract, missingData
from sysdata.config.production_config import get_production_config
from sysdata.mongodb.mongo_generic import mongoDataWithMultipleKeys
from sysdata.futures_spreadbet.market_info_data import (
    marketInfoData,
    contract_date_from_expiry_key,
)
from syslogging.logger import *
from sysobjects.contracts import futuresContract as fc
from sysobjects.production.trading_hours.trading_hours import listOfTradingHours
from sysbrokers.IG.ig_trading_hours import parse_trading_hours

INSTRUMENT_COLLECTION = "market_info"
INDEX_CONFIG = {
    "keys": {
        "instrument_code": pymongo.ASCENDING,
        "epic": pymongo.ASCENDING,
        "instrument.expiry": pymongo.ASCENDING,
    },
    "unique": True,
}
# INDEX_CONFIG = [
#     {
#         "keys": {
#             "epic": pymongo.ASCENDING,
#         },
#         "unique": True,
#     },
#     {
#         "keys": {
#             "instrument_code": pymongo.ASCENDING,
#             "expiry": pymongo.DESCENDING,
#             "last_modified_utc": pymongo.DESCENDING,
#             "instrument.expiry": pymongo.ASCENDING,
#         },
#     },
#     {
#         "keys": {
#             "historic.last_modified_utc": pymongo.DESCENDING,
#         },
#         "sparse": True
#     },
# ]


class mongoMarketInfoData(marketInfoData):
    """
    Read and write mongo data class for market info
    """

    def __init__(
        self, mongo_db=arg_not_supplied, log=get_logger("mongoMarketInfoData")
    ):
        super().__init__(log=log)
        self._mongo_data = mongoDataWithMultipleKeys(
            INSTRUMENT_COLLECTION,
            mongo_db=mongo_db,
            index_config=INDEX_CONFIG,
        )
        self._epic_mappings = {}
        self._expiry_dates = {}
        self._in_hours_status = {}
        self._last_modified = {}
        self._min_bet = {}
        self._instr_code = {}
        self._contract_mappings = {}
        self._sync_status = {}

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

    @cached_property
    def in_hours_status(self) -> dict:
        if len(self._in_hours_status) == 0:
            self._parse_market_info_for_mappings()
        return self._in_hours_status

    @cached_property
    def last_modified(self) -> dict:
        if len(self._last_modified) == 0:
            self._parse_market_info_for_mappings()
        return self._last_modified

    @cached_property
    def min_bet(self) -> dict:
        if len(self._min_bet) == 0:
            self._parse_market_info_for_mappings()
        return self._min_bet

    @cached_property
    def instr_code(self) -> dict:
        if len(self._instr_code) == 0:
            self._parse_market_info_for_mappings()
        return self._instr_code

    @cached_property
    def contract_mapping(self) -> dict:
        if len(self._contract_mappings) == 0:
            self._parse_market_info_for_mappings()
        return self._contract_mappings

    @cached_property
    def sync_status(self) -> dict:
        if len(self._sync_status) == 0:
            self._parse_market_info_for_mappings()
        return self._sync_status

    def add_market_info(self, instrument_code: str, epic: str, market_info: dict):
        self.log.debug(f"Adding market info for '{epic}'")
        self._save(instrument_code, epic, market_info)

    def update_market_info(self, instrument_code: str, epic: str, market_info: dict):
        self.log.debug(f"Updating market info for '{epic}' ({instrument_code})")
        self._save(instrument_code, epic, market_info, allow_overwrite=True)

    def get_market_info_for_epic(self, epic: str):
        return self.mongo_data.collection.find_one(
            {"epic": epic},
            {
                "_id": 0,
            },
        )

    def get_market_info_for_instrument_code(self, instr_code: str):
        results = []
        for doc in self.mongo_data.collection.find(
            {"instrument_code": instr_code},
            {
                "_id": 0,
            },
        ):
            results.append(doc)

        return results

    def get_epic_selection_info(self, instr_code: str):
        results = []
        for doc in self.mongo_data.collection.find(
            {"instrument_code": instr_code},
            {
                "_id": 0,
                "epic": 1,
                "instrument.expiry": 1,
                "instrument.expiryDetails.lastDealingDate": 1,
            },
        ).sort("expiry", 1):
            info = munchify(doc)

            row = {
                "Instrument": instr_code,
                "Expiry key": info.instrument.expiry,
                "Expires": info.instrument.expiryDetails.lastDealingDate,
                "Epic": info.epic,
            }

            results.append(row)

        df = pd.DataFrame(results)

        return df

    def get_list_of_instruments(self):
        results = self.mongo_data.collection.distinct("instrument_code")
        return results

    def get_expiry_details(self, epic: str):
        if epic is not None:
            try:
                market_info = munchify(self.get_market_info_for_epic(epic))
                expiry_key = market_info.instrument.expiry
                last_dealing = market_info.instrument.expiryDetails.lastDealingDate
                expiry_date = pytz.utc.localize(
                    datetime.datetime.strptime(last_dealing, "%Y-%m-%dT%H:%M")
                )
            except Exception as exc:
                self.log.error(f"Problem getting expiry details for '{epic}': {exc}")
                raise missingContract
            return expiry_key, expiry_date
        else:
            raise missingData

    def get_status_for_epic(self, epic: str) -> str:
        if epic is not None:
            try:
                market_info = munchify(self.get_market_info_for_epic(epic))
                status = market_info.snapshot.marketStatus
            except Exception as exc:
                self.log.error(f"Problem getting status for '{epic}': {exc}")
                raise missingContract
            return status
        else:
            raise missingData

    def get_trading_hours_for_epic(self, epic) -> listOfTradingHours:
        try:
            market_info = munchify(self.get_market_info_for_epic(epic))
            mkt_hours_overrides = get_production_config().get_element_or_default(
                "market_hours_overrides", {}
            )
            if market_info.instrument_code in mkt_hours_overrides:
                self.log.info(
                    f"Market hours for '{epic}' are overriden: "
                    f"{mkt_hours_overrides[market_info.instrument_code]}"
                )
                trading_hours = parse_trading_hours(
                    munchify(mkt_hours_overrides[market_info.instrument_code])
                )
            else:
                trading_hours = parse_trading_hours(market_info.instrument.openingHours)
            return trading_hours
        except Exception as exc:
            self.log.error(f"Problem getting trading hours for '{epic}': {exc}")
            raise missingContract

    def get_epic_for_contract(self, contract) -> str:
        instr_code = contract.instrument_code
        the_date = datetime.datetime.strptime(f"{contract.date_str[0:6]}01", "%Y%m%d")
        expiry_key = the_date.strftime("%b-%y").upper()
        result = self.mongo_data.collection.find_one(
            {"instrument_code": instr_code, "instrument.expiry": expiry_key},
            {"epic": 1},
        )

        if result:
            return result["epic"]
        else:
            raise missingData(f"No epic found for {instr_code} ({expiry_key})")

    def get_periods_for_instrument_code(self, instr_code) -> list:
        results = []
        for doc in self.mongo_data.collection.find(
            {"instrument_code": instr_code},
            {"epic": 1},
        ):
            match = re.search("[^.]+.[^.]+.[^.]+.([^.]+).IP", doc["epic"])
            results.append(match.group(1))

        return results

    def delete_for_epic(self, epic):
        return self.mongo_data.collection.delete_one({"epic": epic})

    def get_history_sync_status_for_epic(self, epic: str) -> bool:
        try:
            market_info = munchify(self.get_market_info_for_epic(epic))
            history_synced = bool(market_info.history_synced)
        except AttributeError:
            return False
        except Exception as exc:
            self.log.error(f"Problem getting history sync status for '{epic}': {exc}")
            return False
        return history_synced

    def delete_for_instrument_code(self, instr_code):
        self.mongo_data.collection.delete_many({"instrument_code": instr_code})

    def find_epics_close_to_expiry(self, delta=None, limit=5):

        """
        Find any epics where the expiry dates is less than datetime delta from now
        :return:
        :rtype:
        """

        now = datetime.datetime.utcnow()
        if delta is None:
            my_delta = datetime.timedelta(minutes=15)
        else:
            my_delta = delta
        check_timestamp = now + my_delta

        results = []
        for doc in (
            self.mongo_data.collection.find(
                {
                    "expiry": {
                        "$lt": check_timestamp,
                    },
                },
                {
                    "_id": 0,
                    "epic": 1,
                    "last_modified_utc": 1,
                },
            )
            .sort("last_modified_utc", 1)
            .limit(limit)
        ):
            results.append(doc["epic"])

        return results

    def find_epics_to_update(self, limit=20):
        results = []
        for doc in (
            self.mongo_data.collection.find(
                {},
                {
                    "_id": 0,
                    "epic": 1,
                    "last_modified_utc": 1,
                },
            )
            .sort("last_modified_utc", 1)
            .limit(limit)
        ):
            results.append(doc["epic"])

        return results

    def find_history_epics_to_update(self, limit=50):
        results = []
        for doc in self.mongo_data.collection.find(
            {"historic.last_modified_utc": {"$exists": False}},
            {
                "_id": 0,
                "epic": 1,
            },
        ).limit(limit):
            results.append(doc["epic"])

        return results

    def _parse_market_info_for_mappings(self):
        for instr in self.get_list_of_instruments():
            for result in self.mongo_data.collection.find(
                {"instrument_code": instr},
                {
                    "_id": 0,
                    "epic": 1,
                    "instrument_code": 1,
                    "last_modified_utc": 1,
                    "in_hours_status": 1,
                    "instrument.expiry": 1,
                    "instrument.expiryDetails.lastDealingDate": 1,
                    "dealingRules.minDealSize.value": 1,
                    "history_synced": 1,
                },
            ):

                doc = munchify(result)
                contract_date = contract_date_from_expiry_key(doc.instrument.expiry)
                contract_date_str = f"{instr}/{contract_date}"
                self._epic_mappings[contract_date_str] = doc["epic"]
                self._contract_mappings[doc["epic"]] = fc.from_two_strings(
                    instr, contract_date
                )

                date_str = doc.instrument.expiryDetails.lastDealingDate
                last_dealing = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

                self._expiry_dates[contract_date_str] = last_dealing.strftime(
                    ISO_DATE_FORMAT
                )

                self._last_modified[contract_date_str] = doc["last_modified_utc"]

                self._min_bet[contract_date_str] = doc.dealingRules.minDealSize.value

                self._instr_code[doc["epic"]] = instr

                self._sync_status[contract_date_str] = bool(doc["history_synced"])

                try:
                    self._in_hours_status[contract_date_str] = doc["in_hours_status"]
                except:
                    self.log.error(
                        f"Problem getting 'in_hours_status' for {contract_date_str}"
                    )
                    self._in_hours_status[contract_date_str] = "n/a"

    def _save(
        self, instrument_code: str, epic: str, market_info: dict, allow_overwrite=True
    ):
        market_info = self._setup_expiry_as_datetime(market_info)
        market_info = self._adjust_for_hours(market_info)
        market_info = self._set_sync_status(market_info)
        dict_of_keys = {
            "instrument_code": instrument_code,
            "epic": epic,
        }
        self.mongo_data.add_data(
            dict_of_keys=dict_of_keys,
            data_dict=market_info,
            allow_overwrite=allow_overwrite,
        )

    def _set_sync_status(self, data):
        history_synced = False
        info = munchify(data)
        if "historic" in info:
            try:
                date_diff = abs(info.last_modified_utc - info.historic.timestamp)
                if date_diff.days < 3:
                    history_synced = True
            except Exception as ex:
                history_synced = False
        else:
            history_synced = False

        info["history_synced"] = history_synced
        return info

    def _adjust_for_hours(self, data: dict):
        data["last_modified_utc"] = datetime.datetime.utcnow()
        try:
            market_info = munchify(data)
            trading_hours = parse_trading_hours(market_info.instrument.openingHours)
            if trading_hours.okay_to_trade_now():
                data["in_hours_status"] = market_info.snapshot.marketStatus
        except Exception as exc:
            self.log.error(f"{exc}: No existing market info found, not adjusting")

        return data

    def _setup_expiry_as_datetime(self, data: dict):
        try:
            market_info = munchify(data)
            expiry_str = market_info.instrument.expiryDetails.lastDealingDate
            last_dealing = datetime.datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M")
            data["expiry"] = last_dealing
        except Exception as exc:
            self.log.error(f"Problem creating expiry: {exc}")

        return data
