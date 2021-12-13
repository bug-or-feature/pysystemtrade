import pandas as pd

from syscore.dateutils import ROOT_BDAYS_INYEAR
from systems.system_cache import diagnostic, output
from systems.positionsizing import PositionSizing


class FsbPositionSizing(PositionSizing):
    """
    Stage for futures spreadbet position sizing (take combined forecast; turn into subsystem positions)

    KEY INPUTS: a) system.combForecast.get_combined_forecast(instrument_code)
                 found in self.get_combined_forecast

                b) system.rawdata.get_daily_percentage_volatility(instrument_code)
                 found in self.get_price_volatility(instrument_code)

                 If not found, uses system.data.daily_prices to calculate

                c) system.rawdata.daily_denominator_price((instrument_code)
                 found in self.get_instrument_sizing_data(instrument_code)

                If not found, uses system.data.daily_prices

                d)  system.data.get_value_of_block_price_move(instrument_code)
                 found in self.get_instrument_sizing_data(instrument_code)

                e)  system.data.get_fx_for_instrument(instrument_code, base_currency)
                   found in self.get_fx_rate(instrument_code)


    KEY OUTPUT: system.positionSize.get_subsystem_position(instrument_code)

    Name: positionSize
    """

    # @diagnostic()
    # def get_ideal_exposure(self, instrument_code: str) -> pd.Series:
    #     daily_cash_vol_target = self.get_daily_cash_vol_target()
    #     forecast = self.get_combined_forecast(instrument_code)
    #     daily_vol = self.rawdata_stage.get_daily_percentage_volatility(instrument_code)
    #     ideal_exposure = ((forecast / 10) * daily_cash_vol_target / daily_vol) * ROOT_BDAYS_INYEAR
    #
    #     return ideal_exposure

    # @diagnostic()
    # def get_block_value(self, instrument_code: str) -> pd.Series:
    #     spreadbet_price = self.rawdata_stage.get_daily_prices(instrument_code)
    #     value_of_price_move = self.parent.data.get_value_of_block_price_move(instrument_code)
    #     block_value = spreadbet_price.ffill() * value_of_price_move * 0.01
    #
    #     return block_value

    @diagnostic()
    def get_block_value(self, instrument_code: str) -> pd.Series:

        underlying_price = self.get_underlying_price(instrument_code)
        value_of_price_move = self.parent.data.get_value_of_block_price_move(
            instrument_code
        )

        block_value = underlying_price.ffill() * value_of_price_move * 0.01

        return block_value

    # @output()
    # def get_subsystem_position(self, instrument_code: str) -> pd.Series:
    #     exp = self.get_ideal_exposure(instrument_code)
    #     point_size = self.rawdata_stage.get_pointsize(instrument_code)
    #     price = self.rawdata_stage.get_daily_prices(instrument_code)
    #     fsb_subsystem_position = (exp * point_size) / price
    #
    #     return fsb_subsystem_position

    # @diagnostic()
    # def get_annual_percentage_vol(self, instrument_code: str) -> pd.Series:
    #     ann_risk = self.calculate_daily_percentage_vol(instrument_code) * ROOT_BDAYS_INYEAR
    #     return ann_risk
