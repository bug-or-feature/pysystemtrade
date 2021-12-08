import pandas as pd
from syscore.fileutils import get_filename_for_package
from syscore.genutils import value_or_npnan
from sysobjects.instruments import futuresInstrument
from sysbrokers.broker_instrument_data import brokerFuturesInstrumentData
from syslogdiag.log_to_screen import logtoscreen
from syscore.objects import missing_instrument, missing_file
from sysdata.barchart.bc_instruments import BcInstrumentConfigData, BcFuturesInstrument

BC_FUTURES_CONFIG_FILE = get_filename_for_package(
    "sysdata.barchart.bc_config_futures.csv")


class BarchartConfig(pd.DataFrame):
    pass


def read_bc_config_from_file() -> BarchartConfig:
    df = pd.read_csv(BC_FUTURES_CONFIG_FILE)
    return BarchartConfig(df)


class BarchartFuturesInstrumentData(brokerFuturesInstrumentData):

    def __init__(self, log=logtoscreen("bcFuturesInstrumentData")):
        super().__init__(log=log)

    def __repr__(self):
        return "Barchart Futures per contract data"

    def get_brokers_instrument_code(self, instrument_code: str) -> str:
        if instrument_code.endswith('_fsb'):
            instrument_code = instrument_code[:-4]
        bc_futures_instrument = self.get_bc_futures_instrument(instrument_code)
        return bc_futures_instrument.bc_symbol

    def get_instrument_code_from_broker_code(self, bc_code: str) -> str:
        config = self._get_bc_config()
        config_row = config[config.Symbol == bc_code]
        if len(config_row) == 0:
            msg = f"BC symbol {bc_code} not found in config"
            self.log.critical(msg)
            raise Exception(msg)

        if len(config_row) > 1:
            msg = f"BC symbol {bc_code} appears more than once, likely an FSB, picking first one"
            self.log.msg(msg)
            # TODO total hack - to be fixed properly
            return config_row.iloc[0].Instrument

        return config_row.iloc[0].Instrument

    def _get_instrument_data_without_checking(self, instrument_code: str):
        return self.get_bc_futures_instrument(instrument_code)

    def get_bc_futures_instrument(self, instr_code: str) -> BcFuturesInstrument:
        new_log = self.log.setup(instrument_code=instr_code)

        try:
            assert instr_code in self.get_list_of_instruments()
        except Exception:
            new_log.warn(f"Instrument {instr_code} is not in BC config")
            return missing_instrument

        config = self._get_bc_config()
        if config is missing_file:
            new_log.warn(f"Can't get config for instrument {instr_code} as BC config file missing")
            return missing_instrument

        instrument_object = get_instrument_object_from_config(
            instr_code, config=config
        )

        return instrument_object

    def get_list_of_instruments(self) -> list:
        """
        Get instruments that have price data
        Pulls these in from a config file

        :return: list of str
        """

        config = self._get_bc_config()
        if config is missing_file:
            self.log.warn(
                "Can't get list of instruments because Barchart config file missing"
            )
            return []

        instrument_list = list(config.Instrument)

        return instrument_list

    # Configuration read in and cache
    def _get_bc_config(self) -> BarchartConfig:
        config = getattr(self, "_config", None)
        if config is None:
            config = self._get_and_set_bc_config_from_file()

        return config

    def _get_and_set_bc_config_from_file(self) -> BarchartConfig:

        try:
            config_data = read_bc_config_from_file()
        except BaseException:
            self.log.warn(f"Can't read file {BC_FUTURES_CONFIG_FILE}")
            config_data = missing_file

        self._config = config_data

        return config_data

    def _delete_instrument_data_without_any_warning_be_careful(self, instrument_code: str):
        raise NotImplementedError("BC instrument config is read only")

    def _add_instrument_data_without_checking_for_existing_entry(self, instrument_object):
        raise NotImplementedError("BC instrument config is read only")


def get_instrument_object_from_config(
        instr_code: str, config: BarchartConfig = None) -> BcFuturesInstrument:

    if config is None:
        config = read_bc_config_from_file()

    config_row = config[config.Instrument == instr_code]
    symbol = config_row.Symbol.values[0]
    currency = value_or_npnan(config_row.Currency.values[0], "")
    freq = value_or_npnan(config_row.Freq.values[0], "")

    # We use the flexibility of futuresInstrument to add additional arguments
    instrument = futuresInstrument(instr_code)
    bc_data = BcInstrumentConfigData(symbol, currency=currency, freq=freq)

    futures_instrument_with_bc_data = BcFuturesInstrument(instrument, bc_data)

    return futures_instrument_with_bc_data
