import logging
from datetime import datetime
import yaml
from functools import cached_property

import pandas as pd
from pandas import json_normalize
from tenacity import Retrying, wait_exponential, retry_if_exception_type
from trading_ig.rest import IGService, ApiExceededException

from syscore.objects import missing_data
from sysdata.config.production_config import get_production_config
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices
from syscore.fileutils import get_filename_for_package
from syscore.objects import missing_contract


class IGConnection(object):
    def __init__(self, log=logtoscreen("ConnectionIG", log_level="on")):
        production_config = get_production_config()
        self._ig_username = production_config.get_element_or_missing_data("ig_username")
        self._ig_password = production_config.get_element_or_missing_data("ig_password")
        self._ig_api_key = production_config.get_element_or_missing_data("ig_api_key")
        self._ig_acc_type = production_config.get_element_or_missing_data("ig_acc_type")
        self._ig_acc_number = production_config.get_element_or_missing_data(
            "ig_acc_number"
        )
        self._log = log
        logging.basicConfig(level=logging.DEBUG)
        self._session = self._create_ig_session()

    @property
    def log(self):
        return self._log

    def _create_ig_session(self):
        retryer = Retrying(
            wait=wait_exponential(), retry=retry_if_exception_type(ApiExceededException)
        )
        ig_service = IGService(
            self._ig_username,
            self._ig_password,
            self._ig_api_key,
            acc_number=self._ig_acc_number,
            retryer=retryer,
        )
        #ig_service.create_session()
        ig_service.create_session(version="3")
        return ig_service

    @property
    def service(self):
        return self._session

    @cached_property
    def epic_map(self) -> dict:
        epic_map_file = get_filename_for_package("sysbrokers.IG.epic_map.yaml")
        with open(epic_map_file) as file_to_parse:
            epic_map_dict = yaml.load(file_to_parse, Loader=yaml.FullLoader)
        return epic_map_dict['ig_epic_map']

    def logout(self):
        self._session.logout()

    def get_account_number(self):
        return self._ig_acc_number

    def get_capital(self, account: str):
        data = self.service.fetch_accounts()
        data = data.loc[data["accountId"] == account]
        # data = data.loc[data["accountType"] == "SPREADBET"]
        balance = float(data["balance"].loc[1])
        profitLoss = float(data["profitLoss"].loc[1])
        tot_capital = balance + profitLoss
        available_capital = tot_capital * 0.8 # leave 20% for margin

        return available_capital

    def get_positions(self):
        positions = self.service.fetch_open_positions()
        # print_full(positions)
        result_list = []
        for i in range(0, len(positions)):
            pos = dict()
            pos["account"] = self.service.ACC_NUMBER
            pos["name"] = positions.iloc[i]["instrumentName"]
            pos["size"] = positions.iloc[i]["size"]
            pos["dir"] = positions.iloc[i]["direction"]
            pos["level"] = positions.iloc[i]["level"]
            pos["expiry"] = positions.iloc[i]["expiry"]
            pos["epic"] = positions.iloc[i]["epic"]
            pos["currency"] = positions.iloc[i]["currency"]
            pos["createDate"] = positions.iloc[i]["createdDateUTC"]
            pos["dealId"] = positions.iloc[i]["dealId"]
            pos["dealReference"] = positions.iloc[i]["dealReference"]
            pos["instrumentType"] = positions.iloc[i]["instrumentType"]
            result_list.append(pos)

        return result_list

    def get_activity(self):
        activities = self.service.fetch_account_activity_by_period(48 * 60 * 60 * 1000)
        test_epics = ["CS.D.GBPUSD.TODAY.IP", "IX.D.FTSE.DAILY.IP"]
        activities = activities.loc[~activities["epic"].isin(test_epics)]

        result_list = []
        for i in range(0, len(activities)):
            row = activities.iloc[i]
            action = dict()
            action["epic"] = row["epic"]
            action["date"] = row["date"]
            action["time"] = row["time"]
            action["marketName"] = row["marketName"]
            action["size"] = row["size"]
            action["level"] = row["level"]
            action["actionStatus"] = row["actionStatus"]
            action["expiry"] = row["period"]

            result_list.append(action)

        return result_list

    def get_historical_futures_data_for_contract(
        self,
        contract_object: futuresContract,
        bar_freq: str = "D",
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> pd.DataFrame:

        """
        Get historical daily data

        :param contract_object:
        :type contract_object:
        :param bar_freq:
        :type bar_freq:
        :param start_date:
        :type start_date:
        :param end_date:
        :type end_date:
        :return:
        :rtype:
        """

        df = futuresContractPrices.create_empty()

        try:

            if bar_freq not in ["D", "4H"]:
                raise NotImplementedError(
                    f"IG supported data frequencies: 'D', '4H'"
                )  # TODO add 4H, 3H

            epic = self.get_ig_epic(contract_object)
            if epic is None:
                self.log.warn(
                    f"There is no IG epic for contract ID {str(contract_object)}"
                )
                return missing_data
            else:
                self.log.msg(
                    f"Contract ID {str(contract_object)} maps to IG epic {epic}"
                )

            # if hasattr(contract_object.instrument, 'freq') and contract_object.instrument.freq:
            #     bar_freq = from_config_frequency_to_frequency(contract_object.instrument.freq)

            self.log.msg(
                f"Getting historic data for {epic} ('{start_date.strftime('%Y-%m-%dT%H:%M:%S')}' "
                f"to '{end_date.strftime('%Y-%m-%dT%H:%M:%S')}')"
            )
            try:
                response = self.service.fetch_historical_prices_by_epic(
                    epic=epic,
                    resolution=bar_freq,
                    start_date=start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    end_date=end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    format=self.mid_prices,
                )
                df = response["prices"]

            except Exception as exc:
                self.log.error(f"Problem getting historic data for '{epic}': {exc}")
                if (
                    str(exc)
                    == "error.public-api.exceeded-account-historical-data-allowance"
                ):
                    self.log.error(f"No historic data allowance remaining, yikes!")

            return df

        except Exception as ex:
            self.log.error(f"Problem getting historical data: {ex}")
            return missing_data

    def get_snapshot_price_data_for_contract(
            self,
            futures_contract: futuresContract,
    ) -> pd.DataFrame:

        epic = self.get_ig_epic(futures_contract)

        if epic is not None:

            self.log.msg(
                f"Getting snapshot price data for {epic} ({futures_contract.key})"
            )
            snapshot_rows = []
            now = datetime.now()
            try:
                info = self.service.fetch_market_by_epic(epic)
                update_time = info["snapshot"]["updateTime"]
                bid = info["snapshot"]["bid"]
                offer = info["snapshot"]["offer"]
                high = info["snapshot"]["high"]
                low = info["snapshot"]["low"]
                mid = (bid + offer) / 2
                datetime_str = f"{now.strftime('%Y-%m-%d')}T{update_time}"

                snapshot_rows.append(
                    {
                        "DateTime": datetime_str,
                        "OPEN": mid,
                        "HIGH": high,
                        "LOW": low,
                        "FINAL": mid,
                        "VOLUME": 1
                    }
                )

                df = pd.DataFrame(snapshot_rows)
                df["Date"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%dT%H:%M:%S")
                df.set_index("Date", inplace=True)
                df.index = df.index.tz_localize(tz=None)
                new_cols = ["OPEN", "HIGH", "LOW", "FINAL", "VOLUME"]
                df = df[new_cols]

            except Exception as exc:
                self.log.error(f"Problem getting expiry date for '{futures_contract.key}': {exc}")
                return missing_data
            return df
        else:
            return missing_data

    def get_expiry_date(self, futures_contract: futuresContract):
        """
        Get the actual expiry date for a given contract, according to IG
        :param futures_contract:
        :return: str
        """
        epic = self.get_ig_epic(futures_contract)

        if epic is not None:
            try:
                info = self.service.fetch_market_by_epic(epic)
                expiry = info["instrument"]["expiryDetails"]["lastDealingDate"]
            except Exception as exc:
                self.log.error(f"Problem getting expiry date for '{futures_contract.key}': {exc}")
                return missing_contract
            return expiry
        else:
            return missing_contract

    # TODO properly
    def get_ig_epic(self, futures_contract: futuresContract):
        """
        Converts a contract identifier from internal format (GOLD/20200900), into IG format (MT.D.GC.MONTH1.IP)
        :param futures_contract: the internal format identifier
        :type futures_contract: futuresContract
        :return: IG epic
        :rtype: str
        """

        if futures_contract.key in self.epic_map:
            return self.epic_map[futures_contract.key]
        else:
            return None

    # TODO use the one from trading_ig, remember to rename cols
    def mid_prices(self, prices, version):

        """Format price data as a flat DataFrame, no hierarchy, mid prices"""

        if len(prices) == 0:
            raise (
                Exception(
                    "Converting historical data to pandas dataframe failed, none found"
                )
            )

        df = json_normalize(prices)

        df["Date"] = pd.to_datetime(df["snapshotTimeUTC"], format="%Y-%m-%dT%H:%M:%S")
        df.set_index("Date", inplace=True)
        df.index = df.index.tz_localize(tz="UTC")

        df = df.drop(
            columns=[
                "snapshotTime",
                "openPrice.lastTraded",
                "closePrice.lastTraded",
                "highPrice.lastTraded",
                "lowPrice.lastTraded",
            ]
        )

        df = df.rename(columns={"lastTradedVolume": "VOLUME"})

        df["OPEN"] = df[["openPrice.bid", "openPrice.ask"]].mean(axis=1).round(2)
        df["HIGH"] = df[["highPrice.bid", "highPrice.ask"]].mean(axis=1).round(2)
        df["LOW"] = df[["lowPrice.bid", "lowPrice.ask"]].mean(axis=1).round(2)
        df["FINAL"] = df[["closePrice.bid", "closePrice.ask"]].mean(axis=1).round(2)

        new_cols = ["OPEN", "HIGH", "LOW", "FINAL", "VOLUME"]
        df = df[new_cols]

        df.index = df.index.tz_localize(tz=None)

        return df

    # TODO properly
    def has_data_for_contract(self, futures_contract: futuresContract) -> bool:
        """
        Does IG have data for a given contract?

        :param futures_contract: internal contract identifier
        :type futures_contract: futuresContract
        :return: whether IG knows about the contract
        :rtype: bool
        """
        return futures_contract.key in self.epic_map

