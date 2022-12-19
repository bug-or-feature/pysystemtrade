from datetime import datetime
import logging

import numpy as np
import pandas as pd

from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.arctic.arctic_fsb_epics_history import ArcticFsbEpicHistoryData
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from syscore.objects import success


def update_epics():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    with dataBlob(log_name="Update-Epic-Mappings") as data:
        update_epic_history = UpdateEpicHistory(data)
        update_epic_history.update_epic_history()

    return success

class UpdateEpicHistory(object):

    def __init__(self, data):
        self.data = data
        self.data.add_class_object(ArcticFsbEpicHistoryData)
        self._broker = dataBroker(self.data)

    @property
    def broker(self) -> dataBroker:
        return self._broker

    def update_epic_history(self):

        now = datetime.now()
        list = self.data.db_fsb_epic_history.get_list_of_instruments()
        for instr in sorted(list):

            self.data.log.msg(f"Starting processing for '{instr}'")

            config = self.get_instr_config(instr)
            data = {}
            row = []
            col_headers = []
            valid = True
            key = now.strftime('%Y-%m-%d %H:%M:%S')

            if not hasattr(config, 'ig_data'):
                self.data.log.msg(f"Skipping {instr}, no IG config")
                continue

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
                try:
                    data[key] = row
                    df = pd.DataFrame.from_dict(data, orient='index', columns=col_headers)
                    df.index.name = 'Date'
                    df.index = pd.to_datetime(df.index)
                    self.data.db_fsb_epic_history.update_epic_history(instr, df)
                except Exception as exc:
                    msg = f"Problem updating epic data for instrument '{instr}' " \
                          f"and periods {config.ig_data.periods} - check config: {exc}"
                    self.data.log.critical(msg)
            else:
                msg = f"Problem getting expiry data for instrument '{instr}' " \
                      f"and periods {config.ig_data.periods} - check config"
                self.data.log.critical(msg)

    def get_instr_config(self, instr) -> FsbInstrumentWithIgConfigData:
        return self.broker.broker_futures_instrument_data.get_futures_instrument_object_with_ig_data(instr)


if __name__ == "__main__":
    update_epics()
