import pandas as pd
from datetime import datetime

from sysdata.csv.csv_multiple_prices import csvFuturesMultiplePricesData
from sysdata.csv.csv_spot_fx import csvFxPricesData
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from sysdata.csv.csv_roll_parameters import csvRollParametersData

from sysdata.data_blob import dataBlob
from sysobjects.spot_fx_prices import fxPrices
from sysobjects.adjusted_prices import futuresAdjustedPrices
from sysobjects.multiple_prices import futuresMultiplePrices

from sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData
from syslogdiag.log_to_screen import logtoscreen
from syscore.dateutils import ARBITRARY_START


class CsvFuturesSimTestData(genericBlobUsingFuturesSimData):
    """
    Specialisation of futuresSimData that allows start and end dates to be configured.
    Useful for unit tests, so that new data added to the CSV price files doesn't mess with assertions,
    or if a test is needed at a certain date/time or period.
    Adjusted prices are calculated on the fly
    """

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    # latest in CSV at time of writing
    DEFAULT_END_DATE = datetime.strptime('2021-03-08 20:00:00', DATE_FORMAT)

    def __init__(self, start_date=None, end_date=None, log=logtoscreen("csvFuturesSimTestData")):

        data = dataBlob(
            log=log,
            class_list=[
                csvFuturesMultiplePricesData,
                csvFuturesInstrumentData,
                csvFxPricesData,
                csvRollParametersData
            ]
        )

        super().__init__(data=data)

        if start_date is not None:
            self._start_date = start_date
        else:
            self._start_date = ARBITRARY_START

        if end_date is not None:
            self._end_date = end_date
        else:
            self._end_date = self.DEFAULT_END_DATE

        self._adjusted_prices = dict()

    def __repr__(self):
        return f"csvFuturesSimTestData with {self.get_instrument_list()} instruments, " \
               f"start date {self.start_date.strftime(self.DATE_FORMAT)}, " \
               f"end date {self.end_date.strftime(self.DATE_FORMAT)}"

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    def get_backadjusted_futures_price(self, instrument_code: str) -> futuresAdjustedPrices:
        if instrument_code in self._adjusted_prices:
            return self._adjusted_prices[instrument_code]
        else:
            adj_prices = self._calc_adj_prices(instrument_code)
            self._adjusted_prices[instrument_code] = adj_prices
            return adj_prices

    def get_multiple_prices(self, instrument_code: str) -> futuresMultiplePrices:
        data = super().get_multiple_prices(instrument_code)
        date_adjusted = data[self.start_date:self.end_date]
        return date_adjusted

    def get_fx_for_instrument(self, instrument_code: str, base_currency: str) -> fxPrices:
        data = super().get_fx_for_instrument(instrument_code, base_currency)
        date_adjusted = data[self.start_date:self.end_date]
        return date_adjusted

    def daily_prices(self, instrument_code: str) -> pd.Series:
        data = super().daily_prices(instrument_code)
        date_adjusted = data[self.start_date:self.end_date]
        return date_adjusted

    def get_instrument_raw_carry_data(self, instrument_code: str) -> pd.DataFrame:
        data = super().get_instrument_raw_carry_data(instrument_code)
        date_adjusted = data[self.start_date:self.end_date]
        return date_adjusted

    def get_current_and_forward_price_data(self, instrument_code: str) -> pd.DataFrame:
        data = super().get_current_and_forward_price_data(instrument_code)
        date_adjusted = data[self.start_date:self.end_date]
        return date_adjusted

    def _calc_adj_prices(self, instrument_code):
        data = super().get_multiple_prices(instrument_code)
        date_adjusted = data[self.start_date:self.end_date]
        adjusted_prices = futuresAdjustedPrices.stitch_multiple_prices(date_adjusted)
        return adjusted_prices
