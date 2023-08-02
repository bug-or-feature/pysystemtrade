from datetime import datetime, timedelta
import pytz
from syscore.dateutils import Frequency, DAILY_PRICE_FREQ
from syscore.exceptions import missingContract, missingData

from sysbrokers.broker_futures_contract_data import brokerFuturesContractData
from sysbrokers.broker_instrument_data import brokerFuturesInstrumentData
from sysbrokers.IG.ig_connection import IGConnection, tickerConfig
from sysbrokers.broker_futures_contract_price_data import brokerFuturesContractPriceData
from sysdata.data_blob import dataBlob
from sysdata.barchart.bc_connection import bcConnection
from sysdata.futures_spreadbet.market_info_data import marketInfoData
from sysdata.futures.futures_per_contract_prices import futuresContractPriceData
from sysexecution.tick_data import dataFrameOfRecentTicks, tickerObject
from sysexecution.orders.contract_orders import contractOrder
from sysexecution.orders.broker_orders import brokerOrder
from sysexecution.trade_qty import tradeQuantity

from sysobjects.futures_per_contract_prices import futuresContractPrices
from sysobjects.contracts import futuresContract
from sysobjects.fsb_contract_prices import FsbContractPrices

from syslogging.logger import *


class igTickerObject(tickerObject):
    def __init__(
        self,
        ticker_info: tickerConfig,
        epic: str,
        expiry_key: str,
    ):
        super().__init__(ticker_info.ticker, qty=ticker_info.qty)
        self._log = get_logger("igTickerObject")
        self._direction = ticker_info.direction
        self._epic = epic
        self._expiry_key = expiry_key
        self._sub_key = ticker_info.sub_key

        # qty can just be +1 or -1 size of trade doesn't matter to ticker
        # qty = sign_from_BS(BorS)

    def refresh(self):
        # No need for this, IG pushes updates
        pass

    def bid(self):
        return self.ticker.bid

    def ask(self):
        return self.ticker.offer

    def bid_size(self):
        return self.ticker.last_traded_volume

    def ask_size(self):
        return self.ticker.last_traded_volume

    @property
    def epic(self):
        return self._epic

    @property
    def expiry_key(self):
        return self._expiry_key

    @property
    def direction(self):
        return self._direction

    @property
    def sub_key(self):
        return self._sub_key


class IgFuturesContractPriceData(brokerFuturesContractPriceData):
    def __init__(
        self,
        broker_conn: IGConnection,
        data: dataBlob,
        log=get_logger("IgFuturesContractPriceData"),
    ):
        super().__init__(log=log, data=data)
        self._broker_conn = broker_conn
        self._barchart = bcConnection()

    def __repr__(self):
        return "IG/Barchart Spreadbet Futures per contract price data"

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

    @property
    def futures_contract_data(self) -> brokerFuturesContractData:
        return self.data.broker_futures_contract

    @property
    def barchart(self):
        return self._barchart

    @property
    def futures_instrument_data(self) -> brokerFuturesInstrumentData:
        return self.data.broker_futures_instrument

    @property
    def market_info_data(self) -> marketInfoData:
        return self.data.db_market_info

    @property
    def existing_prices(self) -> futuresContractPriceData:
        return self.data.db_fsb_contract_price

    def has_merged_price_data_for_contract(
        self, futures_contract: futuresContract
    ) -> bool:
        try:
            self.futures_contract_data.get_contract_object_with_config_data(
                futures_contract
            )
        except missingContract:
            return False
        else:
            return True

    def get_list_of_instrument_codes_with_merged_price_data(self) -> list:
        # return list of instruments for which pricing is configured
        list_of_instruments = self.futures_instrument_data.get_list_of_instruments()
        return list_of_instruments

    def contracts_with_merged_price_data_for_instrument_code(
        self, instrument_code: str, allow_expired=True
    ):  # -> listOfFuturesContracts:
        pass
        # futures_instrument_with_ib_data = (
        #     self.futures_instrument_data.get_futures_instrument_object_with_IB_data(
        #         instrument_code
        #     )
        # )
        # list_of_date_str = self.ib_client.broker_get_futures_contract_list(
        #     futures_instrument_with_ib_data, allow_expired=allow_expired
        # )
        #
        # list_of_contracts = [
        #     futuresContract(instrument_code, date_str) for date_str in list_of_date_str
        # ]
        #
        # list_of_contracts = listOfFuturesContracts(list_of_contracts)
        #
        # return list_of_contracts

    def get_contracts_with_merged_price_data(self):
        raise NotImplementedError(
            "Do not use get_contracts_with_merged_price_data with IG"
        )

    def get_prices_at_frequency_for_potentially_expired_contract_object(
        self, contract: futuresContract, freq: Frequency = DAILY_PRICE_FREQ
    ) -> futuresContractPrices:

        price_data = self._get_prices_at_frequency_for_contract_object_no_checking_with_expiry_flag(
            contract, frequency=freq, allow_expired=True
        )

        return price_data

    def _get_merged_prices_for_contract_object_no_checking(
        self, contract_object: futuresContract
    ) -> futuresContractPrices:

        raise Exception("Have to get prices from IB with specific frequency")

    def get_prices_at_frequency_for_contract_object(
        self,
        contract_object: futuresContract,
        frequency: Frequency,
        return_empty: bool = True,
    ):

        # Override this because don't want to check for existing data first
        try:
            prices = self._get_prices_at_frequency_for_contract_object_no_checking(
                futures_contract_object=contract_object, frequency=frequency
            )
        except missingData:
            if return_empty:
                return futuresContractPrices.create_empty()
            else:
                raise

        return prices

    def _get_prices_at_frequency_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract, frequency: Frequency
    ) -> futuresContractPrices:

        return self._get_prices_at_frequency_for_contract_object_no_checking_with_expiry_flag(
            futures_contract_object=futures_contract_object,
            frequency=frequency,
            allow_expired=False,
        )

    def _get_prices_at_frequency_for_contract_object_no_checking_with_expiry_flag(
        self,
        futures_contract_object: futuresContract,
        frequency: Frequency,
        allow_expired: bool = False,
    ) -> futuresContractPrices:

        """
        Get historical prices at a particular frequency

        We override this method, rather than _get_prices_at_frequency_for_contract_object_no_checking
        Because the list of dates returned by contracts_with_price_data is likely to not match (expiries)

        :param futures_contract_object:  futuresContract
        :param frequency: str; one of D, H, 15M, 5M, M, 10S, S
        :return: data
        """

        contract_object_plus = (
            self.futures_contract_data.get_contract_object_with_config_data(
                futures_contract_object, requery_expiries=False
            )
        )

        if futures_contract_object.params.data_source == "Barchart":
            return self._get_barchart_prices(contract_object_plus, frequency)
        else:
            return self._get_ig_prices(contract_object_plus)

    def get_ticker_object_for_order(self, order: contractOrder) -> tickerObject:
        futures_contract = order.futures_contract
        trade_list = order.trade

        ticker = self.get_ticker_object_for_contract_and_trade_qty(
            futures_contract=futures_contract,
            trade_qty=trade_list,
        )

        return ticker

    def get_ticker_object_for_contract(
        self, futures_contract: futuresContract
    ) -> tickerObject:
        return self.get_ticker_object_for_contract_and_trade_qty(
            futures_contract=futures_contract
        )

    def get_ticker_object_for_contract_and_trade_qty(
        self,
        futures_contract: futuresContract,
        trade_qty: tradeQuantity = None,
    ) -> tickerObject:

        epic = self.market_info_data.get_epic_for_contract(futures_contract)
        expiry_info = self.market_info_data.get_expiry_details(epic)
        ticker_with_bs = self.broker_conn.get_ticker_object(
            epic,
            trade_list_for_multiple_legs=trade_qty,
        )

        ticker_object = igTickerObject(ticker_with_bs, epic, expiry_info[0])
        return ticker_object

    def cancel_market_data_for_contract(self, contract: futuresContract):
        epic = self.market_info_data.get_epic_for_contract(contract)
        self.broker_conn.streamer.stop_tick_subscription(epic)

    def cancel_market_data_for_order(self, order: brokerOrder):
        epic = order.order_info["epic"]
        self.broker_conn.streamer.stop_tick_subscription(epic)

    def _get_ig_prices(self, contract_object: futuresContract) -> futuresContractPrices:
        """
        Get historical IG prices

        :param contract_object:  futuresContract
        :return: data
        """

        if contract_object.key not in self.market_info_data.epic_mapping:
            self.log.warn(
                f"No epic mapped for {str(contract_object.key)}",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
            return FsbContractPrices.create_empty()

        # calc dates and freq
        existing = self.existing_prices.get_merged_prices_for_contract_object(
            contract_object
        )
        end_date = datetime.datetime.now().astimezone(tz=pytz.utc)
        if existing.shape[0] > 0:
            last_index_date = existing.index[-1]
            # TODO switch to 4H or 3H?
            freq = "3H"
            start_date = last_index_date + timedelta(minutes=1)
            self.log.debug(
                f"Appending IG data: last row of existing {last_index_date}, freq {freq}, "
                f"start {start_date.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"end {end_date.strftime('%Y-%m-%d %H:%M:%S')}",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
        else:
            freq = "D"
            start_date = end_date - timedelta(
                days=30
            )  # TODO review. depends on instrument?
            self.log.debug(
                f"New IG data: freq {freq}, "
                f"start {start_date.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"end {end_date.strftime('%Y-%m-%d %H:%M:%S')}",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )

        epic = self.market_info_data.epic_mapping[contract_object.key]
        try:
            prices_df = self.broker_conn.get_historical_fsb_data_for_epic(
                epic=epic, bar_freq=freq, start_date=start_date, end_date=end_date
            )
        except missingData:
            self.log.warn(
                f"Problem getting IG price data for {str(contract_object)}",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
            return FsbContractPrices.create_empty()

        # sometimes the IG epics for info and historical prices don't match. the
        # logic here attempts to prevent that scenario from messing up the data
        last_df_date = prices_df.index[-1]
        last_df_date = last_df_date.replace(tzinfo=pytz.UTC)
        hist_diff = abs((last_df_date - end_date).days)
        if hist_diff <= 3:
            self.log.debug(
                f"Found {prices_df.shape[0]} rows of data",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
            price_data = FsbContractPrices(prices_df)

            # TODO update allowance data

        else:
            self.log.debug("Ignoring - IG epic/history config awaiting update")
            return FsbContractPrices.create_empty()

        # It's important that the data is in local time zone so that this works
        price_data = price_data.remove_future_data()

        # Some contract data is marked to model, don't want this
        # TODO review this - dunno if applicable for fsb
        # price_data = price_data.remove_zero_volumes()

        return price_data

    def _get_barchart_prices(
        self, contract_object: futuresContract, freq: Frequency
    ) -> futuresContractPrices:

        """
        Get historical Barchart prices at a particular frequency

        We override this method, rather than _get_prices_at_frequency_for_contract_object_no_checking
        Because the list of dates returned by contracts_with_price_data is likely to not match (expiries)

        :param contract_object:  futuresContract
        :param freq: str; one of D, H, 15M, 5M, M, 10S, S
        :return: data
        """

        barchart_id = self.futures_contract_data.get_barchart_id(contract_object)
        try:
            price_data = self._barchart.get_historical_futures_data_for_contract(
                barchart_id, bar_freq=freq
            )
        except missingData:
            self.log.warn(
                f"Problem getting Barchart price data for {str(contract_object)}",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
            return futuresContractPrices.create_empty()

        price_data = futuresContractPrices(price_data)

        # It's important that the data is in local time zone so that this works
        price_data = price_data.remove_future_data()

        # Some contract data is marked to model, don't want this
        price_data = price_data.remove_zero_volumes()

        return price_data


def from_bid_ask_tick_data_to_dataframe(tick_data) -> dataFrameOfRecentTicks:
    """

    :param tick_data: list of HistoricalTickBidAsk()
    :return: pd.DataFrame,['priceBid', 'priceAsk', 'sizeAsk', 'sizeBid']
    """
    time_index = [tick_item.timestamp for tick_item in tick_data]
    fields = ["priceBid", "priceAsk", "sizeAsk", "sizeBid"]

    value_dict = {}
    for field_name in fields:
        field_values = [getattr(tick_item, field_name) for tick_item in tick_data]
        value_dict[field_name] = field_values

    output = dataFrameOfRecentTicks(value_dict, time_index)

    print(f"tick_frame:\n{output}")

    return output
