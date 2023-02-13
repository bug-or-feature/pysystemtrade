from collections import namedtuple
import pandas as pd

from sysdata.data_blob import dataBlob
from sysdata.alphavantage.av_connection import avConnection
from sysbrokers.broker_fx_prices_data import brokerFxPricesData

from sysobjects.spot_fx_prices import fxPrices
from syslogdiag.log_to_screen import logtoscreen
from syscore.fileutils import resolve_path_and_filename_for_package
from syscore.constants import missing_instrument, missing_file
from syscore.exceptions import missingData

fxConfig = namedtuple("avFXConfig", ["ccy1", "ccy2", "invert"])


class AvFxPricesData(brokerFxPricesData):
    def __init__(self, data: dataBlob, log=logtoscreen("avFxPricesData")):
        super().__init__(log=log, data=data)
        self._avConnection = avConnection()

    def __repr__(self):
        return "Alpha Vantage FX price data"

    @property
    def avConnection(self):
        return self._avConnection

    def get_list_of_fxcodes(self) -> list:
        config_data = self._get_fx_config()
        if config_data is missing_file:
            self.log.warn(
                "Can't get list of FX codes for Alpha Vantage as config file missing"
            )
            return []

        list_of_codes = list(config_data.CODE)

        return list_of_codes

    def _get_fx_prices_without_checking(self, currency_code: str) -> fxPrices:
        config_for_code = self._get_config_info_for_code(currency_code)
        if config_for_code is missing_instrument:
            self.log.warn(
                "Can't get prices as missing config for %s" % currency_code,
                fx_code=currency_code,
            )
            return fxPrices.create_empty()

        data = self._get_fx_prices_with_config(currency_code, config_for_code)

        return data

    def _get_fx_prices_with_config(
        self, currency_code: str, config_for_code: fxConfig
    ) -> fxPrices:
        raw_fx_prices_as_series = self._get_raw_fx_prices(config_for_code)

        if len(raw_fx_prices_as_series) == 0:
            self.log.warn(
                "No available AlphaVantage prices for %s %s"
                % (currency_code, str(config_for_code)),
                fx_code=currency_code,
            )
            return fxPrices.create_empty()

        if config_for_code.invert:
            raw_fx_prices = 1.0 / raw_fx_prices_as_series
        else:
            raw_fx_prices = raw_fx_prices_as_series

        # turn into a fxPrices
        fx_prices = fxPrices(raw_fx_prices)

        self.log.msg("Downloaded %d prices" % len(fx_prices), fx_code=currency_code)

        return fx_prices

    def _get_raw_fx_prices(self, config_for_code: fxConfig) -> pd.Series:
        try:
            raw_fx_prices = self.avConnection.broker_get_daily_fx_data(
                config_for_code.ccy1, ccy2=config_for_code.ccy2
            )
        except missingData:
            return pd.Series()
        raw_fx_prices_as_series = raw_fx_prices["close"]

        return raw_fx_prices_as_series

    def _get_config_info_for_code(self, currency_code: str) -> fxConfig:
        new_log = self.log.setup(currency_code=currency_code)

        config_data = self._get_fx_config()
        if config_data is missing_file:
            new_log.warn(
                "Can't get AV FX config for %s as config file missing" % currency_code,
                fx_code=currency_code,
            )

            return missing_instrument

        ccy1 = config_data[config_data.CODE == currency_code].CCY1.values[0]
        ccy2 = config_data[config_data.CODE == currency_code].CCY2.values[0]
        invert = (
            config_data[config_data.CODE == currency_code].INVERT.values[0] == "YES"
        )

        config_for_code = fxConfig(ccy1, ccy2, invert)

        return config_for_code

    # Configuration read in and cache
    def _get_fx_config(self) -> pd.DataFrame:
        config = getattr(self, "_config", None)
        if config is None:
            config = self._get_and_set_config_from_file()

        return config

    def _get_and_set_config_from_file(self) -> pd.DataFrame:

        try:
            config_data = pd.read_csv(self._get_fx_config_filename())
        except BaseException:
            self.log.warn("Can't read file %s" % self._get_fx_config_filename())
            config_data = missing_file

        self._config = config_data

        return config_data

    def update_fx_prices(self, *args, **kwargs):
        raise NotImplementedError("Alpha Vantage is a read only source of prices")

    def add_fx_prices(self, *args, **kwargs):
        raise NotImplementedError("Alpha Vantage is a read only source of prices")

    def _delete_fx_prices_without_any_warning_be_careful(self, *args, **kwargs):
        raise NotImplementedError("Alpha Vantage is a read only source of prices")

    def _add_fx_prices_without_checking_for_existing_entry(self, *args, **kwargs):
        raise NotImplementedError("Alpha Vantage is a read only source of prices")

    def _get_fx_config_filename(self):
        return resolve_path_and_filename_for_package(
            "sysdata.alphavantage.av_config_spot_FX.csv"
        )
