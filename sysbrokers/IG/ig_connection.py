import logging
from datetime import datetime

import pandas as pd
from pandas import json_normalize
from tenacity import Retrying, wait_exponential, retry_if_exception_type
from trading_ig.rest import IGService, ApiExceededException

from syscore.objects import missing_data
from sysdata.config.production_config import get_production_config
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contracts import futuresContract
from sysobjects.fsb_contract_prices import FsbContractPrices
from syscore.objects import missing_contract


class IGConnection(object):

    PRICE_RESOLUTIONS = ["D", "4H", "3H", "2H", "1H"]

    def __init__(self, log=logtoscreen("ConnectionIG", log_level="on"), auto_connect=True):
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
        if auto_connect:
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
        ig_service.create_session()
        #ig_service.create_session(version="3")
        return ig_service

    @property
    def service(self):
        return self._session

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

    def get_historical_fsb_data_for_epic(
        self,
        epic: str,
        bar_freq: str = "D",
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> pd.DataFrame:

        """
        Get historical daily data

        :param epic:
        :type str:
        :param bar_freq:
        :type bar_freq:
        :param start_date:
        :type start_date:
        :param end_date:
        :type end_date:
        :return:
        :rtype:
        """

        df = FsbContractPrices.create_empty()

        try:

            if bar_freq not in self.PRICE_RESOLUTIONS:
                raise NotImplementedError(
                    f"IG supported data frequencies: {self.PRICE_RESOLUTIONS}"
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
                    format=self._flat_prices_bid_ask_format,
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

    def get_expiry_details(self, epic: str):
        """
        Get the actual expiry date for a given contract, according to IG
        :param futures_contract:
        :return: str
        """

        if epic is not None:
            try:
                info = self.service.fetch_market_by_epic(epic)
                expiry_key = info["instrument"]["expiry"]
                last_dealing = info["instrument"]["expiryDetails"]["lastDealingDate"]
                last_dealing_date = datetime.strptime(last_dealing, '%Y-%m-%dT%H:%M')
            except Exception as exc:
                self.log.error(f"Problem getting expiry date for '{epic}': {exc}")
                return missing_contract
            return (expiry_key, last_dealing_date.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            return missing_contract

    def get_recent_bid_ask_price_data(self, epic):

        results = self.service.fetch_historical_prices_by_epic(
            epic,
            resolution="10Min",
            numpoints=6,
            format=self._flat_prices_tick_format,
            wait=0
        )

        return results["prices"]

    def broker_fx_balances(self, account_id: str):
        return 0.0

    def _flat_prices_tick_format(self, prices, version):

        """Format price data as a flat DataFrame, no hierarchy"""

        if len(prices) == 0:
            raise (Exception("Historical price data not found"))

        df = json_normalize(prices)
        df = df.set_index("snapshotTimeUTC")
        df.index = pd.to_datetime(df.index, format="%Y-%m-%dT%H:%M:%S")
        df.index.name = "DateTime"
        df = df.rename(
            columns={
                "closePrice.bid": "priceBid",
                "closePrice.ask": "priceAsk",
                "lastTradedVolume": "sizeAsk"
            }
        )
        df["sizeBid"] = df["sizeAsk"]
        df = df.drop(
            columns=[
                "openPrice.bid",
                "snapshotTime",
                "openPrice.ask",
                "highPrice.bid",
                "highPrice.ask",
                "lowPrice.bid",
                "lowPrice.ask",
                "openPrice.lastTraded",
                "closePrice.lastTraded",
                "highPrice.lastTraded",
                "lowPrice.lastTraded"
            ]
        )
        df = df[["priceBid", "priceAsk", "sizeAsk", "sizeBid"]]

        return df

    def _flat_prices_bid_ask_format(self, prices, version):

        """Format price data as a flat DataFrame, no hierarchy, with bid/ask OHLC prices"""

        if len(prices) == 0:
            raise (Exception("Historical price data not found"))

        df = json_normalize(prices)
        df = df.set_index("snapshotTimeUTC")
        df.index = pd.to_datetime(df.index, format="%Y-%m-%dT%H:%M:%S")
        df.index.name = "Date"
        df = df.rename(
            columns={
                "openPrice.bid": "Open.bid",
                "openPrice.ask": "Open.ask",
                "highPrice.bid": "High.bid",
                "highPrice.ask": "High.ask",
                "lowPrice.bid": "Low.bid",
                "lowPrice.ask": "Low.ask",
                "closePrice.bid": "Close.bid",
                "closePrice.ask": "Close.ask",
                "lastTradedVolume": "Volume"
            }
        )
        df = df.drop(
            columns=[
                "snapshotTime",
                "openPrice.lastTraded",
                "closePrice.lastTraded",
                "highPrice.lastTraded",
                "lowPrice.lastTraded"
            ]
        )
        df = df[
            [
                "Open.bid", "Open.ask",
                "High.bid", "High.ask",
                "Low.bid", "Low.ask",
                "Close.bid", "Close.ask",
                "Volume"
            ]
        ]

        return df