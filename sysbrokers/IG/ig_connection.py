import datetime
import pandas as pd
from pandas import json_normalize
from tenacity import Retrying, wait_exponential, retry_if_exception_type
from trading_ig.rest import IGService, ApiExceededException, TokenInvalidException
from trading_ig.stream import IGStreamService

try:
    from trading_ig.streamer.manager import StreamingManager
except:
    pass

from sysbrokers.IG.ig_positions import resolveBS_for_list
from sysbrokers.IG.ig_translate_broker_order_objects import IgTradeWithContract
from syscore.exceptions import missingContract, missingData
from sysdata.config.production_config import get_production_config
from sysexecution.trade_qty import tradeQuantity
from syslogging.logger import *
from sysobjects.fsb_contract_prices import FsbContractPrices

from sysexecution.orders.broker_orders import (
    brokerOrderType,
    market_order_type,
)

RETRYABLE = (ApiExceededException, TokenInvalidException)


class tickerConfig(object):
    def __init__(self, ticker, direction: str, quantity: float, sub_key: int):
        self.ticker = ticker
        self.direction = direction
        self.qty = quantity
        self.sub_key = sub_key


class IGConnection(object):
    PRICE_RESOLUTIONS = [
        "1s",
        "1Min",
        "2Min",
        "3Min",
        "5Min",
        "10Min",
        "15Min",
        "30Min",
        "1H",
        "2H",
        "3H",
        "4H",
        "D",
    ]

    def __init__(self, log=get_logger("ConnectionIG"), auto_connect=True):
        self._log = log
        ig_config = get_production_config().get_element("ig_markets")
        live = self._is_live_app(ig_config)
        ig_creds = ig_config["live"] if live else ig_config["demo"]
        self._ig_username = ig_creds["ig_username"]
        self._ig_password = ig_creds["ig_password"]
        self._ig_api_key = ig_creds["ig_api_key"]
        self._ig_acc_type = ig_creds["ig_acc_type"]
        self._ig_acc_number = ig_creds["ig_acc_number"]

        if auto_connect:
            self._rest_session = self._create_rest_session()
            self._stream_session = self._create_stream_session()
            self._streamer = StreamingManager(self._stream_session)

    @property
    def log(self):
        return self._log

    def _create_rest_session(self):
        retryer = Retrying(
            wait=wait_exponential(), retry=retry_if_exception_type(RETRYABLE)
        )
        rest_service = IGService(
            self._ig_username,
            self._ig_password,
            self._ig_api_key,
            acc_type=self._ig_acc_type,
            acc_number=self._ig_acc_number,
            retryer=retryer,
        )
        # rest_service.create_session()
        rest_service.create_session(version="3")
        return rest_service

    def _create_stream_session(self):
        stream_service = IGStreamService(self.rest_service)
        stream_service.create_session(version="3")
        return stream_service

    def _is_live_app(self, config):
        is_live = self.log.name in config["live_types"]
        self.log.info(
            f"Logger name '{self.log.name}' configured as {'LIVE' if is_live else 'DEMO'}"
        )
        return is_live

    @property
    def rest_service(self):
        return self._rest_session

    @property
    def streamer(self):
        return self._streamer

    def logout(self):
        self.log.debug("Logging out of IG REST service")
        self.rest_service.logout()
        self.log.debug("Logging out of IG Stream service")
        self.streamer.stop_subscriptions()

    def get_account_number(self):
        return self._ig_acc_number

    def get_capital(self, account: str):
        data = self.rest_service.fetch_accounts()
        balance = float(data[data["accountId"] == account]["balance"])
        # profit_loss = float(data[data["accountId"] == account]["profitLoss"])
        # margin = float(data[data["accountId"] == account]["deposit"])
        # available = float(data[data["accountId"] == account]["available"])

        return balance

    def get_margin(self, account: str):
        data = self.rest_service.fetch_accounts()
        margin = float(data[data["accountId"] == account]["deposit"])

        return margin

    def get_positions(self):
        positions = self.rest_service.fetch_open_positions()
        # print_full(positions)
        result_list = []
        for i in range(0, len(positions)):
            pos = dict()
            pos["account"] = self.rest_service.ACC_NUMBER
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

    def get_activity(self, start, end, filter=None):
        activity = self.rest_service.fetch_account_activity(
            start, end, detailed=True, fiql_filter=filter
        )

        return activity

    def get_historical_fsb_data_for_epic(
        self,
        epic: str,
        bar_freq: str = "D",
        start_date: datetime = None,
        end_date: datetime = None,
        numpoints: int = None,
        warn_for_nans=False,
    ) -> pd.DataFrame:
        """
        Get historical FSB price data for the given epic

        :param epic: IG epic
        :type epic: str
        :param bar_freq: resolution
        :type bar_freq: str
        :param start_date: start date
        :type start_date: datetime
        :param end_date: end date
        :type end_date: datetime
        :param numpoints: number of data points
        :type numpoints: int
        :param warn_for_nans: raise an exception if results contain NaNs
        :type warn_for_nans: bool
        :return: historical price data
        :rtype: pd.DataFrame
        """

        df = FsbContractPrices.create_empty()

        try:
            if bar_freq not in self.PRICE_RESOLUTIONS:
                raise NotImplementedError(
                    f"IG supported data frequencies: {self.PRICE_RESOLUTIONS}"
                )

            try:
                if start_date is None and end_date is None:
                    self.log.debug(
                        f"Getting historic data for {epic} at resolution '{bar_freq}' "
                        f"(last {numpoints} datapoints)"
                    )
                    response = self.rest_service.fetch_historical_prices_by_epic(
                        epic=epic,
                        resolution=bar_freq,
                        numpoints=numpoints,
                        format=self._flat_prices_bid_ask_format,
                    )
                else:
                    self.log.debug(
                        f"Getting historic data for {epic} at resolution '{bar_freq}'"
                        f" ('{start_date.strftime('%Y-%m-%dT%H:%M:%S')}' to "
                        f"'{end_date.strftime('%Y-%m-%dT%H:%M:%S')}')"
                    )
                    response = self.rest_service.fetch_historical_prices_by_epic(
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
                    self.log.error("No historic data allowance remaining, yikes!")

            if len(df) == 0:
                raise missingData(f"Zero length IG price data found for {epic}")

            if warn_for_nans and df.isnull().values.any():
                raise missingData(f"NaNs in data for {epic}")

            return df

        except Exception as ex:
            self.log.error(f"Problem getting historical data: {ex}")
            raise missingData

    def get_snapshot_price_data_for_contract(
        self,
        epic: str,
    ) -> pd.DataFrame:
        if epic is not None:
            self.log.debug(f"Getting snapshot price data for {epic}")
            snapshot_rows = []
            now = datetime.datetime.now()
            try:
                info = self.rest_service.fetch_market_by_epic(epic)
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
                        "VOLUME": 1,
                    }
                )

                df = pd.DataFrame(snapshot_rows)
                df["Date"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%dT%H:%M:%S")
                df.set_index("Date", inplace=True)
                df.index = df.index.tz_localize(tz=None)
                new_cols = ["OPEN", "HIGH", "LOW", "FINAL", "VOLUME"]
                df = df[new_cols]

            except Exception as exc:
                self.log.error(
                    f"Problem getting snapshot price data for '{epic}': {exc}"
                )
                raise missingData
            return df
        else:
            raise missingData

    def get_market_info(self, epic: str):
        """
        Get the full set of market info for a given epic
        :param epic:
        :return: str
        """

        if epic is not None:
            try:
                info = self.rest_service.fetch_market_by_epic(epic)
                return info
            except Exception as exc:
                self.log.error(f"Problem getting market info for '{epic}': {exc}")
                raise missingContract(f"Cannot find epic '{epic}'")
        else:
            raise missingContract

    def get_ticker_object(
        self,
        epic: str,
        trade_qty: tradeQuantity = None,
    ) -> tickerConfig:
        subkey = self.streamer.start_tick_subscription(epic)
        try:
            ticker = self.streamer.ticker(epic)
            if trade_qty is None:
                dir = None
                qty = None
            else:
                dir, qty = resolveBS_for_list(trade_qty)

            ticker_with_bs = tickerConfig(ticker, dir, qty, subkey)
            return ticker_with_bs

        except Exception as exc:
            self.log.error(f"Problem getting ticker object: {exc}")
            self.streamer.stop_tick_subscription(epic)
            raise missingData(exc)

    def broker_submit_order(
        self,
        trade_list: tradeQuantity,
        epic: str,
        expiry_key: str,
        order_type: brokerOrderType = market_order_type,
        limit_price: float = None,
    ) -> IgTradeWithContract:
        # TODO validate
        self.log.info(f"broker_submit_order() trade_list: {trade_list}")
        size = trade_list[0]

        if size is None:
            raise TypeError("Bet size must be defined")

        if expiry_key is None:
            raise TypeError("Expiry key must be defined")

        direction = "BUY" if size > 0.0 else "SELL"

        result = self.rest_service.create_open_position(
            epic=epic,
            direction=direction,
            currency_code="GBP",
            order_type="MARKET",
            expiry=expiry_key,
            force_open="false",
            guaranteed_stop="false",
            size=abs(size),
            level=None,
            limit_level=None,
            limit_distance=None,
            quote_id=None,
            stop_distance=None,
            stop_level=None,
            trailing_stop=None,
            trailing_stop_increment=None,
        )

        trade_result = IgTradeWithContract(result)
        self.log.debug(f"result of broker_submit_order(): {trade_result}")

        return trade_result

    def broker_get_orders(self, account_id: str):
        self.log.debug(f"fetching working orders for account {account_id}")
        return self.rest_service.fetch_working_orders()

    def _is_tradeable(self, epic):
        market_info = self.rest_service.fetch_market_by_epic(epic)
        status = market_info.snapshot.marketStatus
        return status == "TRADEABLE"

    @staticmethod
    def broker_fx_balances(account_id: str):
        return 0.0

    @staticmethod
    def _flat_prices_tick_format(prices, version):
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
                "lastTradedVolume": "sizeAsk",
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
                "lowPrice.lastTraded",
            ]
        )
        df = df[["priceBid", "priceAsk", "sizeAsk", "sizeBid"]]

        return df

    @staticmethod
    def _flat_prices_bid_ask_format(prices, version):
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
                "lastTradedVolume": "Volume",
            }
        )
        df = df.drop(
            columns=[
                "snapshotTime",
                "openPrice.lastTraded",
                "closePrice.lastTraded",
                "highPrice.lastTraded",
                "lowPrice.lastTraded",
            ]
        )
        df = df[
            [
                "Open.bid",
                "Open.ask",
                "High.bid",
                "High.ask",
                "Low.bid",
                "Low.ask",
                "Close.bid",
                "Close.ask",
                "Volume",
            ]
        ]

        return df
