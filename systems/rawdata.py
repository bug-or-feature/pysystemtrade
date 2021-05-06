from copy import copy

import pandas as pd

from systems.stage import SystemStage
from syscore.objects import resolve_function
from systems.system_cache import input, diagnostic, output

from sysdata.sim.futures_sim_data import futuresSimData
from sysdata.config.configdata import Config

class RawData(SystemStage):
    """
        A SystemStage that does some fairly common calculations before we do
        forecasting and which gives access to some widely used methods.

            This is optional; forecasts can go straight to system.data
            The advantages of using RawData are:
                   - preliminary calculations that are reused can be cached, to
                     save time (eg volatility)
                   - preliminary calculations are available for inspection when
                     diagnosing what is going on

    Name: rawdata
    """

    @property
    def name(self):
        return "rawdata"

    @property
    def data_stage(self) -> futuresSimData:
        return self.parent.data

    @property
    def config(self) -> Config:
        return self.parent.config

    @input
    def get_daily_prices(self, instrument_code) -> pd.Series:
        """
        Gets daily prices

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame

        KEY OUTPUT
        """
        self.log.msg(
            "Calculating daily prices for %s" % instrument_code,
            instrument_code=instrument_code,
        )
        dailyprice = self.data_stage.daily_prices(instrument_code)

        return dailyprice

    @input
    def get_natural_frequency_prices(self, instrument_code: str) -> pd.Series:
        self.log.msg(
            "Retrieving natural prices for %s" % instrument_code,
            instrument_code=instrument_code,
        )

        natural_prices = self.data_stage.get_raw_price(instrument_code)

        return natural_prices

    @input
    def get_hourly_prices(self, instrument_code: str) -> pd.Series:
        raw_prices = self.get_natural_frequency_prices(instrument_code)

        hourly_prices = raw_prices.resample("1H").last()

        return hourly_prices

    @output()
    def daily_denominator_price(self, instrument_code: str) -> pd.Series:
        """
        Gets daily prices for use with % volatility
        This won't always be the same as the normal 'price' which is normally a cumulated total return series

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame


        >>> from systems.tests.testdata import get_test_object
        >>> from systems.basesystem import System
        >>>
        >>> (rawdata, data, config)=get_test_object()

        >>> system=System([rawdata], data)
        >>> system.rawdata.daily_denominator_price("EDOLLAR").head(2)
                        price
        1983-09-26  71.241192
        1983-09-27  71.131192
        """

        dem_returns = self.get_daily_prices(instrument_code)
        return dem_returns

    @output()
    def daily_returns(self, instrument_code: str) -> pd.Series:
        """
        Gets daily returns (not % returns)

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame


        >>> from systems.tests.testdata import get_test_object
        >>> from systems.basesystem import System
        >>>
        >>> (rawdata, data, config)=get_test_object()
        >>> system=System([rawdata], data)
        >>> system.rawdata.daily_returns("EDOLLAR").tail(2)
                     price
        2015-12-10 -0.0650
        2015-12-11  0.1075
        """
        instrdailyprice = self.get_daily_prices(instrument_code)
        dailyreturns = instrdailyprice.diff()

        return dailyreturns

    @output()
    def daily_returns_volatility(self, instrument_code: str) -> pd.Series:
        """
        Gets volatility of daily returns (not % returns)

        This is done using a user defined function

        We get this from:
          the configuration object
          or if not found, system.defaults.py

        The dict must contain func key; anything else is optional

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame

        >>> from systems.tests.testdata import get_test_object
        >>> from systems.basesystem import System
        >>>
        >>> (rawdata, data, config)=get_test_object()
        >>> system=System([rawdata], data)
        >>> ## uses defaults
        >>> system.rawdata.daily_returns_volatility("EDOLLAR").tail(2)
                         vol
        2015-12-10  0.054145
        2015-12-11  0.058522
        >>>
        >>> from sysdata.configdata import Config
        >>> config=Config("systems.provided.example.exampleconfig.yaml")
        >>> system=System([rawdata], data, config)
        >>> system.rawdata.daily_returns_volatility("EDOLLAR").tail(2)
                         vol
        2015-12-10  0.054145
        2015-12-11  0.058522
        >>>
        >>> config=Config(dict(volatility_calculation=dict(func="sysquant.estimators.vol.robust_vol_calc", days=200)))
        >>> system2=System([rawdata], data, config)
        >>> system2.rawdata.daily_returns_volatility("EDOLLAR").tail(2)
                         vol
        2015-12-10  0.057946
        2015-12-11  0.058626

        """
        self.log.msg(
            "Calculating daily volatility for %s" % instrument_code,
            instrument_code=instrument_code,
        )

        dailyreturns = self.daily_returns(instrument_code)
        volconfig = copy(self.config.volatility_calculation)

        # volconfig contains 'func' and some other arguments
        # we turn func which could be a string into a function, and then
        # call it with the other args

        volfunction = resolve_function(volconfig.pop("func"))
        vol = volfunction(dailyreturns, **volconfig)

        return vol

    @output()
    def daily_returns_volatility_mult(self, instrument_code: str, mult: int) -> pd.Series:
        """
        Gets volatility of daily returns (not % returns)

        This is done using a user defined function

        We get this from:
          the configuration object
          or if not found, system.defaults.py

        The dict must contain func key; anything else is optional

        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame
        """
        self.log.msg(
            "Calculating daily volatility for %s" % instrument_code,
            instrument_code=instrument_code,
        )

        dailyreturns = self.daily_returns(instrument_code)
        volconfig = copy(self.config.volatility_calculation)
        volconfig['multiplier'] = mult

        # volconfig contains 'func' and some other arguments
        # we turn func which could be a string into a function, and then
        # call it with the other args

        volfunction = resolve_function(volconfig.pop("func"))
        vol = volfunction(dailyreturns, **volconfig)

        return vol

    @output()
    def get_daily_percentage_returns(self, instrument_code: str) -> pd.Series:
        """
        Get percentage returns

        Useful statistic, also used for some trading rules

        This is an optional subsystem; forecasts can go straight to system.data
        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame
        """

        # UGLY
        denom_price = self.daily_denominator_price(instrument_code)
        num_returns = self.daily_returns(instrument_code)
        perc_returns = num_returns / denom_price.ffill()

        return perc_returns

    @output()
    def get_daily_percentage_volatility(self, instrument_code: str) -> pd.Series:
        """
        Get percentage returns normalised by recent vol

        Useful statistic, also used for some trading rules

        This is an optional subsystem; forecasts can go straight to system.data
        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame

        >>> from systems.tests.testdata import get_test_object
        >>> from systems.basesystem import System
        >>>
        >>> (rawdata, data, config)=get_test_object()
        >>> system=System([rawdata], data)
        >>> system.rawdata.get_daily_percentage_volatility("EDOLLAR").tail(2)
                         vol
        2015-12-10  0.055281
        2015-12-11  0.059789
        """
        denom_price = self.daily_denominator_price(instrument_code)
        return_vol = self.daily_returns_volatility(instrument_code)
        (denom_price, return_vol) = denom_price.align(return_vol, join="right")
        perc_vol = 100.0 * (return_vol / denom_price.ffill())

        return perc_vol

    @diagnostic()
    def get_daily_vol_normalised_returns(self, instrument_code: str) -> pd.Series:
        """
        Get returns normalised by recent vol

        Useful statistic, also used for some trading rules

        This is an optional subsystem; forecasts can go straight to system.data
        :param instrument_code: Instrument to get prices for
        :type trading_rules: str

        :returns: Tx1 pd.DataFrame

        >>> from systems.tests.testdata import get_test_object
        >>> from systems.basesystem import System
        >>>
        >>> (rawdata, data, config)=get_test_object()
        >>> system=System([rawdata], data)
        >>> system.rawdata.get_daily_vol_normalised_returns("EDOLLAR").tail(2)
                    norm_return
        2015-12-10    -1.219510
        2015-12-11     1.985413
        """
        self.log.msg(
            "Calculating normalised return for %s" % instrument_code,
            instrument_code=instrument_code,
        )

        returnvol = self.daily_returns_volatility(instrument_code).shift(1)
        dailyreturns = self.daily_returns(instrument_code)
        norm_return = dailyreturns / returnvol

        return norm_return

    @diagnostic()
    def get_cumulative_daily_vol_normalised_returns(self, instrument_code: str) -> pd.Series:
        """
        Returns a cumulative normalised return. This is like a price, but with equal expected vol
        Used for a few different trading rules

        :param instrument_code: str
        :return: pd.Series
        """

        self.log.msg(
            "Calculating cumulative normalised return for %s" %
            instrument_code, instrument_code=instrument_code, )

        norm_returns = self.get_daily_vol_normalised_returns(instrument_code)

        cum_norm_returns = norm_returns.cumsum()

        return cum_norm_returns

    @diagnostic()
    def _aggregate_daily_vol_normalised_returns_for_asset_class(self, asset_class: str) -> pd.Series:
        """
        Average normalised returns across an asset class

        :param asset_class: str
        :return: pd.Series
        """

        instruments_in_asset_class = self.data_stage.all_instruments_in_asset_class(
            asset_class)

        aggregate_returns_across_asset_class = [
            self.get_daily_vol_normalised_returns(instrument_code)
            for instrument_code in instruments_in_asset_class
        ]

        aggregate_returns_across_asset_class = pd.concat(
            aggregate_returns_across_asset_class, axis=1
        )

        # we don't ffill before working out the median as this could lead to
        # bad data
        median_returns = aggregate_returns_across_asset_class.median(axis=1)

        return median_returns

    @diagnostic()
    def _by_asset_class_daily_vol_normalised_price_for_asset_class(self, asset_class: str) -> pd.Series:
        """
        Price for an asset class, built up from cumulative returns

        :param asset_class: str
        :return: pd.Series
        """

        norm_returns = self._aggregate_daily_vol_normalised_returns_for_asset_class(
            asset_class)
        norm_price = norm_returns.cumsum()

        return norm_price

    @output()
    def normalised_price_for_asset_class(self, instrument_code: str) -> pd.Series:
        """

        :param instrument_code:
        :return:
        """

        asset_class = self.data_stage.asset_class_for_instrument(
            instrument_code)
        normalised_price_for_asset_class = (
            self._by_asset_class_daily_vol_normalised_price_for_asset_class(asset_class)
        )
        normalised_price_this_instrument = self.get_cumulative_daily_vol_normalised_returns(
            instrument_code)

        # Align for an easy life
        # As usual forward fill at last moment
        normalised_price_for_asset_class = normalised_price_for_asset_class.reindex(
            normalised_price_this_instrument.index).ffill()

        return normalised_price_for_asset_class


if __name__ == "__main__":
    import doctest

    doctest.testmod()
