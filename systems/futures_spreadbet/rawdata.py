import pandas as pd
from systems.futures.rawdata import FuturesRawData
from systems.system_cache import input, output


class FuturesSpreadbetRawData(FuturesRawData):
    """
    A SubSystem that does futures spreadbet specific raw data calculations

    The futures spreadbet markets at IG are all

    Name: rawdata
    """

    # TODO override carry based methods to also apply multiplier

    @input
    def get_daily_prices(self, instrument_code) -> pd.Series:
        multiplier = self.get_multiplier(instrument_code)
        self.log.msg(f"Calculating FSB daily prices for {instrument_code}, with multiplier {multiplier}",
                     instrument_code=instrument_code)
        dailyprice = self.data_stage.daily_prices(instrument_code)
        dailyprice *= multiplier
        return dailyprice

    @input
    def get_natural_frequency_prices(self, instrument_code: str) -> pd.Series:
        multiplier = self.get_multiplier(instrument_code)
        self.log.msg(f"Retrieving FSB natural prices for {instrument_code}, with multiplier {multiplier}",
            instrument_code=instrument_code,
        )
        natural_prices = self.data_stage.get_raw_price(instrument_code)
        natural_prices *= multiplier
        return natural_prices

    @input
    def get_hourly_prices(self, instrument_code: str) -> pd.Series:
        multiplier = self.get_multiplier(instrument_code)
        self.log.msg(f"Retrieving FSB hourly prices for {instrument_code}, with multiplier {multiplier}",
                     instrument_code=instrument_code)
        raw_prices = self.get_natural_frequency_prices(instrument_code)
        hourly_prices = raw_prices.resample("1H").last()
        hourly_prices *= multiplier
        return hourly_prices

    def get_multiplier(self, instrument_code):
        instr_obj = self.data_stage._get_instrument_object_with_cost_data(instrument_code)
        multiplier = instr_obj.meta_data.Multiplier
        return multiplier

    @output()
    def daily_denominator_price(self, instrument_code: str) -> pd.Series:
        """
        Gets daily prices for use with % volatility. This version multiplies the raw futures price to get the
        futures spread bet price

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame

        KEY OUTPUT
        """
        multiplier = self.get_multiplier(instrument_code)
        prices = self.get_instrument_raw_carry_data(instrument_code).PRICE
        daily_prices = prices.resample("1B").last()
        daily_prices *= multiplier

        return daily_prices
