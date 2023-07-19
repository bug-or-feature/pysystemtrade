import datetime
from dataclasses import dataclass

import pandas as pd
from pandas import json_normalize
from timeit import default_timer as timer
from tenacity import Retrying, wait_exponential, retry_if_exception_type
from trading_ig.rest import IGService, ApiExceededException
from trading_ig.stream import IGStreamService
from trading_ig.lightstreamer import Subscription

from syscore.constants import arg_not_supplied
from sysbrokers.IG.ig_positions import resolveBS_for_list
from sysbrokers.IG.ig_ticker import IgTicker
from syscore.exceptions import missingContract, missingData
from sysdata.config.production_config import get_production_config
from sysexecution.orders.named_order_objects import missing_order
from sysexecution.trade_qty import tradeQuantity
from syslogging.logger import *
from sysobjects.contracts import futuresContract
from sysobjects.fsb_contract_prices import FsbContractPrices

from sysbrokers.IG.ig_translate_broker_order_objects import (
    tradeWithContract,
    # listOfTradesWithContracts,
)
from sysexecution.orders.broker_orders import (
    brokerOrderType,
    market_order_type,
    limit_order_type,
    snap_mkt_type,
    snap_mid_type,
    snap_prim_type,
)


class tickerWithQtyDir(object):
    def __init__(self, ticker, direction: str, quantity: float):
        self.ticker = ticker
        self.direction = direction
        self.qty = quantity


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

    @property
    def log(self):
        return self._log

    def _create_rest_session(self):
        retryer = Retrying(
            wait=wait_exponential(), retry=retry_if_exception_type(ApiExceededException)
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
        self._spread_storage = []
        return stream_service

    def _is_live_app(self, config):
        return self.log.name in config["live_types"]

    @property
    def rest_service(self):
        return self._rest_session

    @property
    def stream_service(self):
        return self._stream_session

    def logout(self):
        self.log.debug("Logging out of IG REST service")
        self.rest_service.logout()
        self.log.debug("Logging out of IG Stream service")
        self.stream_service.disconnect()

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

    def get_activity(self):
        activities = self.rest_service.fetch_account_activity_by_period(
            48 * 60 * 60 * 1000
        )
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
                raise missingContract
        else:
            raise missingContract

    def get_ticker_object(
        self,
        epic: str,
        contract_object_with_ib_data: futuresContract,
        trade_list_for_multiple_legs: tradeQuantity = None,
    ) -> tickerWithQtyDir:

        # specific_log = contract_object_with_ib_data.specific_log(self.log)

        # self.ib.reqMktData(ibcontract, "", False, False)
        # ticker = self.ib.ticker(ibcontract)

        ticker = IgTicker.get_instance(self, epic)

        dir, qty = resolveBS_for_list(trade_list_for_multiple_legs)

        ticker_with_bs = tickerWithQtyDir(ticker, dir, qty)

        return ticker_with_bs

    def get_recent_bid_ask_price_data(self, instr_code, epic):

        self.log.label(instrument_code=instr_code)
        if self._is_tradeable(epic):
            start = timer()

            # override for testing at weekends, evenings
            # epic = "CS.D.BITCOIN.TODAY.IP"  # sample weekend crypto spreadbet epics
            subscription = Subscription(
                mode="DISTINCT",
                items=[f"CHART:{epic}:TICK"],
                fields=["UTM", "BID", "OFR", "LTV"],
            )

            subscription.addlistener(self.on_stream_update)
            sub_key = self.stream_service.ls_client.subscribe(subscription)
            self.log.debug(f"sub key: {sub_key}")

            max_data_points = 10
            duration = 0
            while (len(self._spread_storage) < max_data_points) and (duration < 10.0):
                duration = timer() - start

            result = self._spread_storage.copy()
            self._spread_storage.clear()
            self.stream_service.ls_client.unsubscribe(sub_key)
            duration = timer() - start
            self.log.debug(
                f"Collection of spread data for {instr_code} ({epic}) took {duration} seconds"
            )

            return result

        else:
            self.log.warning(
                f"Unable to sample spreads for {instr_code} ({epic}), market is not tradeable"
            )
            return []

    def broker_submit_order(
        self,
        futures_contract_with_ib_data: futuresContract,
        trade_list: tradeQuantity,
        account_id: str = arg_not_supplied,
        order_type: brokerOrderType = market_order_type,
        limit_price: float = None,
    ) -> tradeWithContract:

        """
        :param ibcontract: contract_object_with_ib_data: contract where instrument has ib metadata
        :param trade: int
        :param account: str
        :param order_type: str, market or limit
        :param limit_price: None or float
        :return: brokers trade object
        """

        try:
            ibcontract_with_legs = self.ib_futures_contract_with_legs(
                futures_contract_with_ib_data=futures_contract_with_ib_data,
                trade_list_for_multiple_legs=trade_list,
            )
        except missingContract:
            return missing_order

        ibcontract = ibcontract_with_legs.ibcontract

        ib_order = self._build_ib_order(
            trade_list=trade_list,
            account_id=account_id,
            order_type=order_type,
            limit_price=limit_price,
        )

        order_object = self.ib.placeOrder(ibcontract, ib_order)

        trade_with_contract = tradeWithContract(ibcontract_with_legs, order_object)

        return trade_with_contract

    def ib_futures_contract_with_legs(
        self,
        futures_contract_with_ib_data: futuresContract,
        allow_expired: bool = False,
        always_return_single_leg: bool = False,
        trade_list_for_multiple_legs: tradeQuantity = None,
    ) -> ibcontractWithLegs:
        """
        Return a complete and unique IB contract that matches contract_object_with_ib_data
        Doesn't actually get the data from IB, tries to get from cache

        :param futures_contract_with_ib_data: contract, containing instrument metadata suitable for IB
        :return: a single ib contract object
        """
        contract_object_to_use = copy(futures_contract_with_ib_data)
        if always_return_single_leg and contract_object_to_use.is_spread_contract():
            contract_object_to_use = (
                contract_object_to_use.new_contract_with_first_contract_date()
            )

        ibcontract_with_legs = self._get_stored_or_live_contract(
            contract_object_to_use=contract_object_to_use,
            trade_list_for_multiple_legs=trade_list_for_multiple_legs,
            allow_expired=allow_expired,
        )

        return ibcontract_with_legs

    def _get_stored_or_live_contract(
        self,
        contract_object_to_use: futuresContract,
        trade_list_for_multiple_legs: tradeQuantity = None,
        allow_expired: bool = False,
    ):

        ibcontract_with_legs = self.cache.get(
            self._get_ib_futures_contract_from_broker,
            contract_object_to_use,
            trade_list_for_multiple_legs=trade_list_for_multiple_legs,
            allow_expired=allow_expired,
        )

        return ibcontract_with_legs

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

    def on_stream_update(self, item_update):
        self.log.debug(f"item_update: {item_update}")
        update_values = item_update["values"]

        try:
            tick = BidAskTick(
                update_values["UTM"],
                update_values["BID"],
                update_values["OFR"],
                update_values["LTV"],
            )
            self._spread_storage.append(tick)
        except TypeError as err:
            # we don't care too much about these, in DISTINCT mode, we get updates for everything, and lots of them
            # are Volume changes
            self.log.debug(
                f"Problem trying to create tick data '{update_values}': {err}"
            )


@dataclass
class BidAskTick:
    timestamp: datetime
    priceBid: float
    priceAsk: float
    sizeBid: int
    sizeAsk: int

    def __init__(self, date_str: str, bid_str: str, ask_str: str, size_str: str):

        self.timestamp = datetime.datetime.fromtimestamp(int(date_str) / 1000)
        self.priceBid = float(bid_str)
        self.priceAsk = float(ask_str)

        try:
            self.sizeBid = int(size_str)
            self.sizeAsk = int(size_str)
        except TypeError:
            self.sizeBid = 0
            self.sizeAsk = 0
