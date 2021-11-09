import pandas as pd
from functools import lru_cache

from sysbrokers.IB.ib_instruments import NOT_REQUIRED_FOR_IB, ibInstrumentConfigData, futuresInstrumentWithIBConfigData
from sysbrokers.IB.ib_connection import connectionIB
from sysbrokers.broker_instrument_data import brokerFuturesInstrumentData

from syscore.fileutils import get_filename_for_package
from syscore.genutils import value_or_npnan
from syscore.objects import missing_instrument, missing_file

from sysobjects.instruments import futuresInstrument

from syslogdiag.log_to_screen import logtoscreen

IG_FSB_CONFIG_FILE = get_filename_for_package(
    "sysbrokers.IG.ig_config_fsb.csv")

class IGConfig(pd.DataFrame):
    pass

# def read_ib_config_from_file() -> IGConfig:
#     df = pd.read_csv(IG_FSB_CONFIG_FILE)
#     return IGConfig(df)


class IgFsbInstrumentData(brokerFuturesInstrumentData):
    """
    IG Futures Spread Bet instrument data
    """

    def __init__(self, log=logtoscreen("IgFsbInstrumentData")):
        super().__init__(log=log)

    def __repr__(self):
        return "IG Futures Spread Bet instrument data"

    def get_brokers_instrument_code(self, instrument_code:str) -> str:
        raise NotImplementedError

    def get_instrument_code_from_broker_code(self, broker_code: str) -> str:

        dot_pos = self.find_char_instances(broker_code, ".")
        code_base = broker_code[:dot_pos[2]]

        config_row = self.config[self.config.IGEpic == code_base]
        if len(config_row) == 0:
            msg = f"Broker symbol {broker_code} not found in configuration file!"
            self.log.critical(msg)
            raise Exception(msg)

        if len(config_row) > 1:
            msg = f"Broker symbol {broker_code} appears more than once in configuration file!"
            self.log.critical(msg)
            raise Exception(msg)

        return config_row.iloc[0].Instrument

    def get_list_of_instruments(self) -> list:
        """
        Get instruments that have price data
        Pulls these in from a config file

        :return: list of str
        """
        instrument_list = list(self.config.Instrument)
        return instrument_list

    def find_char_instances(self, search_str, ch):
        return [i for i, ltr in enumerate(search_str) if ltr == ch]

    @classmethod
    @property
    @lru_cache()
    def config(cls) -> IGConfig:

        try:
            df = pd.read_csv(IG_FSB_CONFIG_FILE)
            return IGConfig(df)

        except BaseException:
            IgFsbInstrumentData.log.warn("Can't read file %s" % IG_FSB_CONFIG_FILE)
            config_data = missing_file

        return config_data
