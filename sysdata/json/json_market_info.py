import json
from datetime import datetime
from functools import cached_property
from munch import munchify

from syscore.objects import arg_not_supplied
from syscore.dateutils import ISO_DATE_FORMAT
from sysdata.futures_spreadbet.market_info_data import (
    marketInfoData,
    contract_date_from_expiry_key,
)
from syslogdiag.log_to_screen import logtoscreen
from syscore.fileutils import (
    get_filename_for_package,
    files_with_extension_in_pathname,
    get_resolved_pathname,
)
from sysobjects.production.trading_hours.trading_hours import listOfTradingHours

MARKET_INFO_DIRECTORY = "data.futures_spreadbet.market_info_json"


class jsonMarketInfoData(marketInfoData):
    def __init__(
        self, datapath=arg_not_supplied, log=logtoscreen("jsonMarketInfoData")
    ):
        super().__init__(log=log)
        if datapath is arg_not_supplied:
            datapath = MARKET_INFO_DIRECTORY
        self._datapath = datapath
        self._epic_mappings = {}
        self._expiry_dates = {}

    @property
    def datapath(self):
        return self._datapath

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

    def get_market_info_for_epic(self, epic: str):
        pass

    def get_list_of_instruments(self) -> list:
        # return ["GOLD_fsb"]
        return list(
            set(
                file[:-9]
                for file in files_with_extension_in_pathname(self._datapath, ".json")
            )
        )

    def _filename_given_instrument_code(self, instr_code: str, expiry_key: str):
        contract_date_str = contract_date_from_expiry_key(expiry_key)
        return get_filename_for_package(
            f"{self._datapath}", f"{instr_code}_{contract_date_str}.json"
        )

    def update_market_info(self, instr_code: str, epic: str, market_info: dict):
        info = munchify(market_info)
        filename = self._filename_given_instrument_code(
            instr_code, info.instrument.expiry
        )
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(market_info, file, ensure_ascii=False, indent=4, skipkeys=True)

    def get_market_info_for_instrument_code(self, instr_code: str):
        results = []
        for filename in files_with_extension_in_pathname(self.datapath, ".json"):
            if filename.startswith(instr_code):
                with open(
                    f"{get_resolved_pathname(self.datapath)}/{filename}.json", "r"
                ) as file_obj:
                    info = munchify(json.loads(file_obj.read()))
                    info.instrument_code = instr_code
                    results.append(dict(info))

        return results

    def _parse_market_info_for_mappings(self):
        for filename in files_with_extension_in_pathname(self.datapath, ".json"):
            key = f"{filename[:-9]}/{filename[-8:]}"
            with open(
                f"{get_resolved_pathname(self.datapath)}/{filename}.json", "r"
            ) as file_obj:
                info = munchify(json.loads(file_obj.read()))

                date_str = info.instrument.expiryDetails.lastDealingDate
                last_dealing = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

                self._epic_mappings[key] = info.instrument.epic
                self._expiry_dates[key] = last_dealing.strftime(ISO_DATE_FORMAT)

        if len(self._epic_mappings) == 0:
            raise Exception("Invalid market info")

    def add_market_info(self, instrument_code: str, epic: str, market_info: dict):
        raise NotImplementedError("Consider implementing for consistent interface")

    def get_expiry_details(self, epic: str):
        raise NotImplementedError("Consider implementing for consistent interface")

    def get_trading_hours_for_epic(self, epic) -> listOfTradingHours:
        raise NotImplementedError("Consider implementing for consistent interface")

    def get_epic_for_contract(self, contract) -> str:
        raise NotImplementedError("Consider implementing for consistent interface")
