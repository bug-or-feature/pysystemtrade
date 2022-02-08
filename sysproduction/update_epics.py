from datetime import datetime

import numpy as np
import pandas as pd

from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.csv.csv_fsb_epics_history_data import CsvFsbEpicHistoryData
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker


def update_epics():

    with dataBlob(log_name="Update-Epic-Mappings") as data:
        update_epic_history = UpdateEpicHistory(data)
        update_epic_history.update_epic_history()


class UpdateEpicHistory(object):

    def __init__(self, data):
        self.data = data
        self.data.add_class_object(CsvFsbEpicHistoryData)
        self._broker = dataBroker(self.data)

    @property
    def broker(self) -> dataBroker:
        return self._broker

    def update_epic_history(self):

        now = datetime.now()
        for instr in self.data.db_fsb_epic_history.get_list_of_instruments():

            self.data.log.msg(f"Starting processing for '{instr}'")

            config = self.get_instr_config(instr)
            data = {}
            row = []
            col_headers = []
            valid = True
            key = now.strftime('%Y-%m-%d %H:%M:%S')

            if len(config.ig_data.periods) == 0:
                self.data.log.msg(f"Skipping {instr}, no epics defined")
                continue

            for period in config.ig_data.periods:
                col_headers.append(period)
                epic = f"{config.ig_data.epic}.{period}.IP"

                try:
                    expiry_key, expiry = self.data.broker_conn.get_expiry_details(epic)
                    row.append(f"{expiry_key} ({expiry})")

                except Exception:
                    row.append(np.nan)
                    valid = False

            if valid:
                data[key] = row
                df = pd.DataFrame.from_dict(data, orient='index', columns=col_headers)
                df.index.name = 'Date'

                existing = self.data.db_fsb_epic_history.read_epic_history(instr)
                existing.index.name = 'Date'

                self.data.log.msg(f"Writing epic history for '{instr}'")
                existing.loc[pd.to_datetime(key)] = row
                self.data.db_fsb_epic_history.update_epic_history(instr, existing)
            else:
                msg = f"Problem updating epic data for instrument'{instr}' " \
                      f"and periods {config.ig_data.periods} - check config"
                self.data.log.critical(msg)

    def get_instr_config(self, instr) -> FsbInstrumentWithIgConfigData:
        return self.broker.broker_futures_instrument_data.get_ig_fsb_instrument(instr)
