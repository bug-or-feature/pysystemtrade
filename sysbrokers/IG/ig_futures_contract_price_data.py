from datetime import datetime, timedelta
import pytz

from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.IG.ig_futures_contract_data import IgFuturesContractData
from sysbrokers.IG.ig_instruments_data import IgFuturesInstrumentData
from sysbrokers.broker_futures_contract_price_data import brokerFuturesContractPriceData
from syscore.dateutils import Frequency, DAILY_PRICE_FREQ
from syscore.objects import missing_contract, missing_data
from sysdata.barchart.bc_connection import bcConnection
from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysexecution.orders.broker_orders import brokerOrder
from sysexecution.orders.contract_orders import contractOrder
from sysexecution.tick_data import dataFrameOfRecentTicks, tickerObject
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices
from sysobjects.fsb_contract_prices import FsbContractPrices


class IgFuturesContractPriceData(brokerFuturesContractPriceData):
    def __init__(self, broker_conn: IGConnection, log=logtoscreen("IgFuturesContractPriceData", log_level="on")):
        super().__init__(log=log)
        self._igconnection = broker_conn
        self._barchart = bcConnection()
        self._fsb_contract_data = IgFuturesContractData(broker_conn, log=self.log)
        self._futures_instrument_data = IgFuturesInstrumentData(broker_conn, log=self.log)
        self._existing_prices = ArcticFsbContractPriceData()

    def __repr__(self):
        return "IG/Barchart Spreadbet Futures per contract price data"

    @property
    def igconnection(self) -> IGConnection:
        return self._igconnection

    @property
    def fsb_contract_data(self) -> IgFuturesContractData:
        return self._fsb_contract_data

    @property
    def barchart(self):
        return self._barchart

    @property
    def futures_instrument_data(self) -> IgFuturesInstrumentData:
        return self._futures_instrument_data

    @property
    def existing_prices(self) -> ArcticFsbContractPriceData:
        return self._existing_prices

    def has_data_for_contract(self, futures_contract: futuresContract) -> bool:
        return futures_contract.key in self.futures_instrument_data.epic_mapping

    def get_list_of_instrument_codes_with_price_data(self) -> list:
        # return list of instruments for which pricing is configured
        list_of_instruments = self.futures_instrument_data.get_list_of_instruments()
        return list_of_instruments

    def get_prices_at_frequency_for_contract_object(
        self, contract_object: futuresContract, freq: Frequency = DAILY_PRICE_FREQ
    ):
        return self._get_prices_at_frequency_for_contract_object_no_checking(
            contract_object, freq=freq
        )

    def _get_prices_for_contract_object_no_checking(
        self, contract_object: futuresContract
    ) -> futuresContractPrices:
        return self._get_prices_at_frequency_for_contract_object_no_checking(
            contract_object, freq=Frequency.Day
        )

    def _get_prices_at_frequency_for_contract_object_no_checking(
        self, contract_object: futuresContract, freq: Frequency
    ) -> futuresContractPrices:
        """
        Get historical prices at a particular frequency

        :param contract_object:  futuresContract
        :param freq: str; one of D, H, 15M, 5M, M, 10S, S
        :return: data
        """
        if contract_object is missing_contract:
            self.log.warn(
                f"Can't get data for {str(contract_object)}",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
            return futuresContractPrices.create_empty()

        contract_object_plus = (
            self.fsb_contract_data.get_contract_object_with_config_data(
                contract_object, requery_expiries=False)
        )

        if contract_object.params.data_source == "Barchart":
            return self._get_barchart_prices(contract_object_plus, freq)
        else:
            return self._get_ig_prices(contract_object_plus)

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

        if contract_object is missing_contract:
            self.log.warn(f"Can't get data for {str(contract_object)}",
                          instrument_code=contract_object.instrument_code,
                          contract_date=contract_object.contract_date.date_str,
            )
            return futuresContractPrices.create_empty()

        barchart_id = self.fsb_contract_data.get_barchart_id(contract_object)
        price_data = self._barchart.get_historical_futures_data_for_contract(
            barchart_id, bar_freq=freq
        )

        if price_data is missing_data:
            self.log.warn(
                f"Problem getting Barchart price data for {str(contract_object)}",
                instrument_code=contract_object.instrument_code,
                contract_date=contract_object.contract_date.date_str,
            )
            price_data = futuresContractPrices.create_empty()

        elif len(price_data) == 0:
            self.log.warn(f"No Barchart price data found for {str(contract_object)}",
                          instrument_code=contract_object.instrument_code,
                          contract_date=contract_object.contract_date.date_str,
            )
            price_data = futuresContractPrices.create_empty()
        else:
            price_data = futuresContractPrices(price_data)

            # It's important that the data is in local time zone so that this works
            price_data = price_data.remove_future_data()

            # Some contract data is marked to model, don't want this
            price_data = price_data.remove_zero_volumes()

            # massage Barchart price data into IG format
            price_data = self._do_price_massage(contract_object, price_data)

        return price_data

    def _write_prices_for_contract_object_no_checking(self, *args, **kwargs):
        raise NotImplementedError("Read only source of prices")

    def _do_price_massage(self, contract_object: futuresContract, prices):
        instrument_code = contract_object.instrument_code
        multiplier = contract_object.instrument.multiplier
        inverse = bool(contract_object.instrument.inverse)
        self.log.msg(
            f"Massaging prices for IG: {instrument_code}, multiplier {multiplier}, "
            f"inverse {inverse}",
            instrument_code=instrument_code,
            contract_date=contract_object.contract_date.date_str,
        )
        for col_name in ["OPEN", "HIGH", "LOW", "FINAL"]:
            series = prices[col_name]
            if inverse:
                series = 1 / series
            series *= multiplier
            prices[col_name] = series

        return prices

    def delete_prices_for_contract_object(self, *args, **kwargs):
        raise NotImplementedError("Read only source of prices")

    def _delete_prices_for_contract_object_with_no_checks_be_careful(
        self, contract_object: futuresContract
    ):
        raise NotImplementedError("Read only source of prices")

    def get_ticker_object_for_order(self, order: contractOrder) -> tickerObject:
        raise NotImplementedError("Not implemented")

    def cancel_market_data_for_order(self, order: brokerOrder):
        raise NotImplementedError("Not implemented")

    def get_recent_bid_ask_tick_data_for_contract_object(
        self, contract_object: futuresContract
    ) -> dataFrameOfRecentTicks:

        new_log = contract_object.log(self.log)

        contract_object_with_config_data = (
            self.fsb_contract_data.get_contract_object_with_config_data(contract_object)
        )
        if contract_object_with_config_data is missing_contract:
            new_log.warn("Can't get recent price data for %s" % str(contract_object))
            return dataFrameOfRecentTicks.create_empty()

        epic = self.futures_instrument_data.epic_mapping[contract_object.key]
        price_data = self.igconnection.get_recent_bid_ask_price_data(epic)

        if price_data is missing_contract:
            return missing_data

        return dataFrameOfRecentTicks(price_data)

    def get_prices_at_frequency_for_potentially_expired_contract_object(
        self, contract: futuresContract, freq: Frequency = DAILY_PRICE_FREQ
    ) -> futuresContractPrices:
        raise NotImplementedError("Not implemented")

    def get_contracts_with_price_data(self):
        raise NotImplementedError(
            "Do not use get_contracts_with_price_data() with multibroker"
        )

    def _get_ig_prices(self, contract_object: futuresContract) -> futuresContractPrices:
        """
        Get historical IG prices

        :param contract_object:  futuresContract
        :return: data
        """

        if contract_object is missing_contract:
            self.log.warn(f"Can't get IG data for {str(contract_object)}",
                          instrument_code=contract_object.instrument_code,
                          contract_date=contract_object.contract_date.date_str,
            )
            return FsbContractPrices.create_empty()

        if contract_object.key not in self.futures_instrument_data.epic_mapping:
            self.log.warn(f"No epic mapped for {str(contract_object.key)}",
                          instrument_code=contract_object.instrument_code,
                          contract_date=contract_object.contract_date.date_str,
            )
            return FsbContractPrices.create_empty()

        # calc dates and freq
        existing = self.existing_prices.get_prices_for_contract_object(contract_object)
        end_date = datetime.now().astimezone(tz=pytz.utc)
        if existing.shape[0] > 0:
            last_index_date = existing.index[-1]
            # TODO switch to 4H or 3H?
            freq = '3H'
            start_date = last_index_date + timedelta(minutes=1)
            self.log.msg(f"Appending IG data: last row of existing {last_index_date}, freq {freq}, "
                         f"start {start_date.strftime('%Y-%m-%d %H:%M:%S')}, "
                         f"end {end_date.strftime('%Y-%m-%d %H:%M:%S')}",
                         instrument_code=contract_object.instrument_code,
                         contract_date=contract_object.contract_date.date_str
            )
        else:
            freq = 'D'
            start_date = end_date - timedelta(days=30)  # TODO review. depends on instrument?
            self.log.msg(f"New IG data: freq {freq}, "
                         f"start {start_date.strftime('%Y-%m-%d %H:%M:%S')}, "
                         f"end {end_date.strftime('%Y-%m-%d %H:%M:%S')}",
                         instrument_code=contract_object.instrument_code,
                         contract_date=contract_object.contract_date.date_str
            )

        epic = self.futures_instrument_data.epic_mapping[contract_object.key]
        prices_df = self.igconnection.get_historical_fsb_data_for_epic(
            epic=epic,
            bar_freq=freq,
            start_date=start_date,
            end_date=end_date)

        if prices_df is missing_data:
            self.log.warn(f"Problem getting IG price data for {str(contract_object)}",
                          instrument_code=contract_object.instrument_code,
                          contract_date=contract_object.contract_date.date_str)
            price_data = FsbContractPrices.create_empty()

        elif len(prices_df) == 0:
            self.log.warn(f"No IG price data found for {str(contract_object)}",
                          instrument_code=contract_object.instrument_code,
                          contract_date=contract_object.contract_date.date_str
            )
            price_data = FsbContractPrices.create_empty()
        else:
            # sometimes the IG epics for info and historical prices don't match. the logic here attempts to
            # prevent that scenario from messing up the data
            last_df_date = prices_df.index[-1]
            last_df_date = last_df_date.replace(tzinfo=pytz.UTC)
            hist_diff = abs((last_df_date - end_date).days)
            if hist_diff <= 3:
                self.log.msg(f"Found {prices_df.shape[0]} rows of data",
                             instrument_code=contract_object.instrument_code,
                             contract_date=contract_object.contract_date.date_str
                )
                price_data = FsbContractPrices(prices_df)
            else:
                self.log.msg(f"Ignoring - IG epic/history config awaiting update")
                price_data = FsbContractPrices.create_empty()

        # It's important that the data is in local time zone so that this works
        price_data = price_data.remove_future_data()

        # Some contract data is marked to model, don't want this
        # TODO review this - dunno if applicable for fsb
        # price_data = price_data.remove_zero_volumes()

        return price_data
