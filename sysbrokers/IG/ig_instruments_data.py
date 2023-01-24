import pandas as pd
from functools import cached_property

from sysbrokers.IG.ig_instruments import (
    IgInstrumentConfigData,
    FsbInstrumentWithIgConfigData,
)
from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_instrument_data import brokerFuturesInstrumentData

from syscore.fileutils import get_filename_for_package
from syscore.objects import missing_instrument, missing_file

from sysobjects.instruments import futuresInstrument

from syslogdiag.log_to_screen import logtoscreen
from sysdata.futures_spreadbet.fsb_epic_history_data import FsbEpicsHistoryData
from sysdata.data_blob import dataBlob

IG_INSTRUMENT_CONFIG_FILE = get_filename_for_package(
    "sysbrokers.IG.ig_instrument_config.csv"
)


class IGConfig(pd.DataFrame):
    pass


class IgFuturesInstrumentData(brokerFuturesInstrumentData):
    """
    IG Futures Spread Bet instrument data
    """

    def __init__(
        self,
        data_blob: dataBlob,
        broker_conn: IGConnection = None,
        log=logtoscreen("IgFsbInstrumentData"),
    ):
        super().__init__(log=log)
        self._dataBlob = data_blob
        self._broker_conn = broker_conn

    def __repr__(self):
        return "IG Futures Spread Bet instrument data"

    @cached_property
    def config(self) -> IGConfig:

        try:
            df = pd.read_csv(IG_INSTRUMENT_CONFIG_FILE)
            config_data = IGConfig(df)

        except BaseException:
            self.log.warn("Can't read file %s" % IG_INSTRUMENT_CONFIG_FILE)
            config_data = missing_file

        return config_data

    @property
    def data(self):
        return self._dataBlob

    @property
    def fsb_epic_history(self) -> FsbEpicsHistoryData:
        return self.data.db_fsb_epic_history

    def get_brokers_instrument_code(self, instrument_code: str) -> str:
        raise NotImplementedError

    def get_instrument_code_from_broker_code(self, broker_code: str) -> str:

        dot_pos = self.find_char_instances(broker_code, ".")
        code_base = broker_code[: dot_pos[2]]

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

    def _get_instrument_data_without_checking(self, instrument_code: str):
        return self.get_futures_instrument_object_with_ig_data(instrument_code)

    def get_futures_instrument_object_with_ig_data(
        self, instrument_code: str
    ) -> FsbInstrumentWithIgConfigData:

        new_log = self.log.setup(instrument_code=instrument_code)

        try:
            assert instrument_code in self.get_list_of_instruments()
        except Exception:
            new_log.warn(f"Instrument {instrument_code} is not in IG config")
            return missing_instrument

        instrument_object = get_instrument_object_from_config(
            instrument_code, config=self.config
        )

        return instrument_object

    def get_list_of_instruments(self) -> list:
        """
        Instruments that we can handle with this broker

        :return: list of str
        """
        instrument_list = list(self.config.Instrument)
        return instrument_list

    def find_char_instances(self, search_str, ch):
        return [i for i, ltr in enumerate(search_str) if ltr == ch]


def get_instrument_object_from_config(
    instrument_code: str, config: IGConfig = None
) -> FsbInstrumentWithIgConfigData:

    config_row = config[config.Instrument == f"{instrument_code}"]
    if len(config_row) > 0:
        epic = config_row.IGEpic.values[0]
        currency = config_row.IGCurrency.values[0]
        multiplier = config_row.IGMultiplier.values[0]
        inverse = config_row.IGInverse.values[0]
        bc_code = config_row.BarchartCode.values[0]
        period_str = config_row.IGPeriods.values[0]

        instrument = futuresInstrument(instrument_code)
        ig_data = IgInstrumentConfigData(
            epic=epic,
            currency=currency,
            multiplier=multiplier,
            inverse=inverse,
            bc_code=bc_code,
            period_str=period_str,
        )

        futures_instrument_with_ig_data = FsbInstrumentWithIgConfigData(
            instrument, ig_data
        )

        return futures_instrument_with_ig_data

    else:
        return missing_instrument
