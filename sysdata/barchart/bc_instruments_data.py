import pandas as pd
from syscore.fileutils import get_filename_for_package
from syscore.genutils import value_or_npnan

from sysobjects.instruments import futuresInstrument
from sysdata.futures.instruments import futuresInstrumentData

from syslogdiag.log import logtoscreen
from syscore.objects import  missing_instrument, missing_file

from sysdata.barchart.bc_instruments import barchartInstrumentConfigData, futuresInstrumentWithBarchartConfigData


BARCHART_FUTURES_CONFIG_FILE = get_filename_for_package(
    "sysdata.barchart.bc_config_futures.csv")


class BarchartConfig(pd.DataFrame):
    pass


def read_barchart_config_from_file() -> BarchartConfig:
    df = pd.read_csv(BARCHART_FUTURES_CONFIG_FILE)
    return BarchartConfig(df)


class barchartFuturesInstrumentData(futuresInstrumentData):

    def __init__(self, log=logtoscreen("barchartFuturesContractData")):
        super().__init__(log=log)

    def __repr__(self):
        return "Barchart Futures per contract data '%s'" % "TBD"

    def get_brokers_instrument_code(self, instrument_code:str) -> str:
        futures_instrument_plus = self.get_futures_instrument_object_plus(instrument_code)
        return futures_instrument_plus.barchart_symbol

    def get_instrument_code_from_broker_code(self, broker_code: str) -> str:
        config = self._get_ib_config()
        config_row = config[config.Symbol == broker_code]
        if len(config_row) == 0:
            msg = "Broker symbol %s not found in configuration file!" % broker_code
            self.log.critical(msg)
            raise Exception(msg)

        if len(config_row) > 1:
            msg = (
                "Broker symbol %s appears more than once in configuration file!" %
                ib_code)
            self.log.critical(msg)
            raise Exception(msg)

        return config_row.iloc[0].Instrument

    def _get_instrument_data_without_checking(self, instrument_code: str):
        return self.get_futures_instrument_object_plus(instrument_code)

    def get_futures_instrument_object_plus(self, instrument_code:str) -> futuresInstrumentWithBarchartConfigData:
        new_log = self.log.setup(instrument_code=instrument_code)

        try:
            assert instrument_code in self.get_list_of_instruments()
        except:
            new_log.warn(
                "Instrument %s is not in Barchart configuration file" %
                instrument_code)
            return missing_instrument

        config = self._get_barchart_config()
        if config is missing_file:
            new_log.warn(
                "Can't get config for instrument %s as Barchart configuration file missing" %
                instrument_code)
            return missing_instrument

        instrument_object = get_instrument_object_from_config(
            instrument_code, config=config
        )

        return instrument_object

    def get_list_of_instruments(self) -> list:
        """
        Get instruments that have price data
        Pulls these in from a config file

        :return: list of str
        """

        config = self._get_barchart_config()
        if config is missing_file:
            self.log.warn(
                "Can't get list of instruments because Barchart config file missing"
            )
            return []

        instrument_list = list(config.Instrument)

        return instrument_list

    # Configuration read in and cache
    def _get_barchart_config(self) -> BarchartConfig:
        config = getattr(self, "_config", None)
        if config is None:
            config = self._get_and_set_barchart_config_from_file()

        return config

    def _get_and_set_barchart_config_from_file(self) -> BarchartConfig:

        try:
            config_data = read_barchart_config_from_file()
        except BaseException:
            self.log.warn("Can't read file %s" % BARCHART_FUTURES_CONFIG_FILE)
            config_data = missing_file

        self._config = config_data

        return config_data


    def _delete_instrument_data_without_any_warning_be_careful(self, instrument_code: str):
        raise NotImplementedError("Barchart instrument config is read only - edit .csv file %s" %
            BARCHART_FUTURES_CONFIG_FILE)

    def _add_instrument_data_without_checking_for_existing_entry(self, instrument_object):
        raise NotImplementedError("Barchart instrument config is read only - edit .csv file %s" %
            BARCHART_FUTURES_CONFIG_FILE)


def get_instrument_object_from_config(instrument_code: str,
                                      config: BarchartConfig=None) -> futuresInstrumentWithBarchartConfigData:
    if config is None:
        config = read_barchart_config_from_file()

    config_row = config[config.Instrument == instrument_code]
    symbol = config_row.Symbol.values[0]
    currency = value_or_npnan(config_row.Currency.values[0], "")

    # We use the flexibility of futuresInstrument to add additional arguments
    instrument = futuresInstrument(instrument_code)
    barchart_data = barchartInstrumentConfigData(symbol, currency=currency)

    futures_instrument_with_barchart_data = futuresInstrumentWithBarchartConfigData(instrument, barchart_data)

    return futures_instrument_with_barchart_data