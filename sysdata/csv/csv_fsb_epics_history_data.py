import pandas as pd

from syscore.fileutils import get_filename_for_package, files_with_extension_in_pathname
from syscore.objects import arg_not_supplied
from syscore.pdutils import pd_readcsv
from sysdata.futures_spreadbet.fsb_epic_history_data import FsbHistoryData
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.epic_history import FsbEpicHistory


EPIC_HISTORY_DIRECTORY = "data.futures_spreadbet.epic_history_csv"


class CsvFsbEpicHistoryData(FsbHistoryData):

    def __init__(
        self,
        datapath=arg_not_supplied,
        log=logtoscreen("CsvFsbEpicHistoryData"),
    ):

        super().__init__(log=log)

        if datapath is arg_not_supplied:
            self._datapath = EPIC_HISTORY_DIRECTORY
        else:
            self._datapath = datapath

    def __repr__(self):
        return f"FSB epic history data from {self._datapath}"

    # @property
    # def datapath(self):
    #     return self.datapath

    def get_list_of_instruments(self) -> list:
        return files_with_extension_in_pathname(self._datapath, ".csv")
        #return ["BUXL_fsb", "CAD_fsb", "CRUDE_W_fsb", "EUROSTX_fsb", "GOLD_fsb", "NASDAQ_fsb", "NZD_fsb", "US10_fsb"]
        #return ["GOLD_fsb"]

    def get_epic_history(self, instrument_code: str):
        df = self.read_epic_history(instrument_code)
        df = df.tail(1)
        df = df.reset_index()
        del df['index']
        return df.to_dict()

    def update_epic_history(self, instrument_code: str, epic_history: FsbEpicHistory, remove_duplicates=True):
        filename = self._filename_given_instrument_code(instrument_code)
        if remove_duplicates:
            epic_history = epic_history.drop_duplicates()
        epic_history.to_csv(filename, index_label="Date")

        self.log.msg(
            f"Written epic history for {instrument_code} to {filename}",
            instrument_code=instrument_code
        )

    def read_epic_history(self, instrument_code: str) -> pd.DataFrame:
        filename = self._filename_given_instrument_code(instrument_code)

        try:
            instr_all_price_data = pd_readcsv(filename, date_index_name="Date")
        except OSError:
            self.log.warn(
                f"Can't find epic history file {filename} or error reading",
                instrument_code=instrument_code,
            )
            return FsbEpicHistory()

        return instr_all_price_data

    def _filename_given_instrument_code(self, instrument_code: str):
        return get_filename_for_package(self._datapath, f"{instrument_code}.csv")