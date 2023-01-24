from datetime import datetime, timedelta
import pytz

from syscore.dateutils import Frequency, DAILY_PRICE_FREQ
from syscore.exceptions import missingContract, missingData

from sysbrokers.broker_futures_contract_data import brokerFuturesContractData
from sysbrokers.broker_instrument_data import brokerFuturesInstrumentData
from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_futures_contract_price_data import brokerFuturesContractPriceData
from sysdata.data_blob import dataBlob
from sysdata.barchart.bc_connection import bcConnection
from sysdata.futures_spreadbet.market_info_data import marketInfoData

from sysdata.futures.futures_per_contract_prices import futuresContractPriceData
from sysexecution.tick_data import dataFrameOfRecentTicks, tickerObject
from sysexecution.orders.contract_orders import contractOrder
from sysexecution.orders.broker_orders import brokerOrder

from sysobjects.futures_per_contract_prices import futuresContractPrices
from sysobjects.contracts import futuresContract
from sysobjects.fsb_contract_prices import FsbContractPrices

from syslogdiag.log_to_screen import logtoscreen


class IgFuturesContractPriceData(brokerFuturesContractPriceData):
    def __init__(
        self,
        data_blob: dataBlob,
        broker_conn: IGConnection,
        log=logtoscreen("IgFuturesContractPriceData", log_level="on"),
    ):
        super().__init__(log=log)
        self._dataBlob = data_blob
        self._broker_conn = broker_conn
        self._barchart = bcConnection()

    def __repr__(self):
        return "IG/Barchart Spreadbet Futures per contract price data"

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

    @property
    def data(self):
        return self._dataBlob

    @property
    def fsb_contract_data(self) -> brokerFuturesContractData:
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
            self.fsb_contract_data.get_contract_object_with_config_data(
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

    def get_contracts_with_merged_price_data(self):
        raise NotImplementedError(
            "Do not use get_contracts_with_merged_price_data with IB"
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
            self.fsb_contract_data.get_contract_object_with_config_data(
                futures_contract_object, requery_expiries=False
            )
        )

        if futures_contract_object.params.data_source == "Barchart":
            return self._get_barchart_prices(contract_object_plus, frequency)
        else:
            return self._get_ig_prices(contract_object_plus)

    def get_ticker_object_for_order(self, order: contractOrder) -> tickerObject:
        raise NotImplementedError("Not implemented")

    def cancel_market_data_for_order(self, order: brokerOrder):
        raise NotImplementedError("Not implemented")

    def get_recent_bid_ask_tick_data_for_contract_object(
        self, contract_object: futuresContract
    ) -> dataFrameOfRecentTicks:

        new_log = contract_object.log(self.log)

        try:
            contract_object_with_config_data = (
                self.fsb_contract_data.get_contract_object_with_config_data(
                    contract_object
                )
            )
        except missingContract:
            new_log.warn("Can't get recent price data for %s" % str(contract_object))
            return dataFrameOfRecentTicks.create_empty()

        epic = self.market_info_data.get_epic_for_contract(contract_object)
        tick_list = self.broker_conn.get_recent_bid_ask_price_data(
            contract_object.instrument_code, epic
        )

        if len(tick_list) < 3:
            new_log.warn(
                f"Not enough recent price tick data for {contract_object} to record spreads"
            )
            raise missingData

        tick_data_as_df = from_bid_ask_tick_data_to_dataframe(tick_list)

        return dataFrameOfRecentTicks(tick_data_as_df)

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
        end_date = datetime.now().astimezone(tz=pytz.utc)
        if existing.shape[0] > 0:
            last_index_date = existing.index[-1]
            # TODO switch to 4H or 3H?
            freq = "3H"
            start_date = last_index_date + timedelta(minutes=1)
            self.log.msg(
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
            self.log.msg(
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
            self.log.msg(
                f"Found {prices_df.shape[0]} rows of data",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
            price_data = FsbContractPrices(prices_df)

            # TODO update allowance data

        else:
            self.log.msg("Ignoring - IG epic/history config awaiting update")
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

        barchart_id = self.fsb_contract_data.get_barchart_id(contract_object)
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
