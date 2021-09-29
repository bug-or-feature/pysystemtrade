import pandas as pd

from sysobjects.carry_data import rawCarryData
from systems.rawdata import RawData
from systems.system_cache import input, output
from syscore.dateutils import ROOT_BDAYS_INYEAR


class FuturesSpreadbetRawData(RawData):
    """
    A SubSystem that does futures spreadbet specific raw data calculations

    The futures spreadbet markets at IG are all

    Name: rawdata
    """

    @input
    def get_daily_prices(self, instrument_code) -> pd.Series:
        return self.do_price_massage(
            instrument_code,
            self.data_stage.daily_prices(instrument_code),
            "FSB daily")

    @input
    def get_natural_frequency_prices(self, instrument_code: str) -> pd.Series:
        return self.do_price_massage(
            instrument_code,
            self.data_stage.get_raw_price(instrument_code),
            "FSB natural")

    @input
    def get_hourly_prices(self, instrument_code: str) -> pd.Series:
        return self.do_price_massage(
            instrument_code,
            self.get_natural_frequency_prices(instrument_code).resample("1H").last(),
            "FSB hourly")

    def get_instrument_raw_carry_data(self, instrument_code: str) -> rawCarryData:
        multiplier = self.get_multiplier(instrument_code)
        inverse = self.get_inverse(instrument_code)
        df = super().get_instrument_raw_carry_data(instrument_code)
        if inverse:
            df['PRICE'] = 1 / df['PRICE']
            df['CARRY'] = 1 / df['CARRY']
        df['PRICE'] *= multiplier
        df['CARRY'] *= multiplier
        return df

    def get_pointsize(self, instrument_code):
        instr_obj = self.data_stage._get_instrument_object_with_cost_data(instrument_code)
        pointsize = instr_obj.meta_data.Pointsize
        return pointsize

    def get_spread(self, instrument_code):
        instr_obj = self.data_stage._get_instrument_object_with_cost_data(instrument_code)
        spread = instr_obj.meta_data.Slippage * 2
        return spread

    def get_multiplier(self, instrument_code):
        instr_obj = self.data_stage._get_instrument_object_with_cost_data(instrument_code)
        multiplier = instr_obj.meta_data.Multiplier
        return multiplier

    def get_inverse(self, instrument_code):
        instr_obj = self.data_stage._get_instrument_object_with_cost_data(instrument_code)
        inverse = bool(instr_obj.meta_data.Inverse)
        return inverse

    def get_asset_class(self, instrument_code):
        instr_obj = self.data_stage._get_instrument_object_with_cost_data(instrument_code)
        asset_class = instr_obj.meta_data.AssetClass
        return asset_class

    @output()
    def daily_denominator_price(self, instrument_code: str) -> pd.Series:
        """
        Gets daily prices for use with % volatility. This version multiplies the raw futures price to get the
        futures spread bet price

        :param instrument_code: Instrument to get prices for
        :returns: Tx1 pd.DataFrame

        KEY OUTPUT
        """
        prices = self.get_instrument_raw_carry_data(instrument_code).PRICE
        daily_prices = prices.resample("1B").last()
        return daily_prices

    @output()
    def get_annual_percentage_volatility(self, instrument_code: str, span=25) -> pd.Series:
        daily_perc_vol = self.get_daily_percentage_returns(instrument_code).ffill().rolling(span).std()
        # daily_perc_vol = self.get_daily_percentage_returns(instrument_code).ffill().ewm(35).std()
        annual_perc_vol = daily_perc_vol * ROOT_BDAYS_INYEAR
        return annual_perc_vol

    def do_price_massage(self, instrument_code, prices, description):
        multiplier = self.get_multiplier(instrument_code)
        inverse = self.get_inverse(instrument_code)
        self.log.msg(f"Calculating {description} prices for {instrument_code}, multiplier {multiplier}, "
                     f"inverse {inverse}", instrument_code=instrument_code)
        if inverse:
            prices = 1 / prices
        prices *= multiplier

        return prices
