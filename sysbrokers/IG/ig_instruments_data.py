import pandas as pd
from datetime import datetime
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
from sysdata.csv.csv_fsb_epics_history_data import CsvFsbEpicHistoryData

IG_FSB_CONFIG_FILE = get_filename_for_package("sysbrokers.IG.ig_config_fsb.csv")


class IGConfig(pd.DataFrame):
    pass


class IgFuturesInstrumentData(brokerFuturesInstrumentData):
    """
    IG Futures Spread Bet instrument data
    """

    def __init__(
            self,
            broker_conn: IGConnection = None,
            log=logtoscreen("IgFsbInstrumentData"),
            epic_history_datapath=None
    ):
        super().__init__(log=log)
        self._igconnection = broker_conn
        if epic_history_datapath is None:
            self._epic_history = CsvFsbEpicHistoryData()
        else:
            self._epic_history = CsvFsbEpicHistoryData(datapath=epic_history_datapath)
        self._epic_mappings = {}
        self._expiry_dates = {}

    def __repr__(self):
        return "IG Futures Spread Bet instrument data"

    @cached_property
    def config(self) -> IGConfig:

        try:
            df = pd.read_csv(IG_FSB_CONFIG_FILE)
            return IGConfig(df)

        except BaseException:
            self.log.warn("Can't read file %s" % IG_FSB_CONFIG_FILE)
            config_data = missing_file

        return config_data

    @cached_property
    def epic_mapping(self) -> dict:
        if len(self._epic_mappings) == 0:
            self._parse_epic_history_for_mappings()
        return self._epic_mappings

    @cached_property
    def expiry_dates(self) -> dict:
        if len(self._expiry_dates) == 0:
            self._parse_epic_history_for_expiries()
        return self._expiry_dates

    def get_ig_fsb_instrument(self, instr_code: str) -> FsbInstrumentWithIgConfigData:
        new_log = self.log.setup(instrument_code=instr_code)

        try:
            assert instr_code in self.get_list_of_instruments()
        except Exception:
            new_log.warn(f"Instrument {instr_code} is not in IG config")
            return missing_instrument

        instrument_object = get_instrument_object_from_config(instr_code, config=self.config)

        return instrument_object

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

    def _parse_epic_history_for_mappings(self):
        for instr in self._epic_history.get_list_of_instruments():
            instr_map = self._epic_history.get_epic_history(instr)
            config = self.get_ig_fsb_instrument(instr)
            if config is missing_instrument:
                self.log.warn(f"Missing IG config for {instr}")
                continue
            epic_base = config.ig_data.epic
            epic_periods = config.ig_data.periods

            for period in epic_periods:
                if self._validate_entry(period, instr_map):
                    expiry_code_date = datetime.strptime(f'01-{instr_map[period][0][:6]}', '%d-%b-%y')
                    self._epic_mappings[f"{instr}/{expiry_code_date.strftime('%Y%m')}00"] = f"{epic_base}.{period}.IP"
                else:
                    msg = f"No expiry info for instrument'{instr}' and period '{period}' - check config"
                    self.log.critical(msg)

    def _parse_epic_history_for_expiries(self):
        for instr in self._epic_history.get_list_of_instruments():
            history_df = self._epic_history.get_epic_history_df(instr)
            config = self.get_ig_fsb_instrument(instr)
            if config is missing_instrument:
                self.log.warn(f"Missing IG config for {instr}")
                continue
            epic_periods = config.ig_data.periods

            for i in range(history_df.shape[0] - 1, -1, -1):
                row_as_dict = history_df.iloc[i].to_dict()

                for period in epic_periods:
                    if self._validate_row(period, row_as_dict):
                        expiry_code_date = datetime.strptime(f'01-{row_as_dict[period][:6]}', '%d-%b-%y')
                        key = f"{instr}/{expiry_code_date.strftime('%Y%m')}00"
                        if key not in self._expiry_dates:
                            self._expiry_dates[key] = row_as_dict[period][8:27]
                    else:
                        msg = f"No expiry info for instrument '{instr}', row {i}, period '{period}' - check config"
                        self.log.warn(msg)

    def _validate_entry(self, period, instr_map):
        return period in instr_map and isinstance(instr_map[period][0], str)

    def _validate_row(self, period, instr_map):
        return period in instr_map and isinstance(instr_map[period], str)


def get_instrument_object_from_config(
        instrument_code: str, config: IGConfig = None
) -> FsbInstrumentWithIgConfigData:

    config_row = config[config.Instrument == f"{instrument_code}"]
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
        period_str=period_str
    )

    futures_instrument_with_ig_data = FsbInstrumentWithIgConfigData(
        instrument, ig_data
    )

    return futures_instrument_with_ig_data
