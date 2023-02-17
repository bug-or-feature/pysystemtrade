import logging

from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from syscore.constants import success


def update_fsb_market_info(instr_list=None):

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with dataBlob(log_name="Update-FSB-Market-Info") as data:
        update_epic_config = UpdateFsbMarketInfo(data)
        update_epic_config.do_market_info_updates(instr_list)

    return success


class UpdateFsbMarketInfo(object):
    def __init__(self, data):
        self.data = data
        self.data.add_class_object(mongoMarketInfoData)
        self._broker = dataBroker(self.data)

    @property
    def broker(self) -> dataBroker:
        return self._broker

    def do_market_info_updates(self, instrument_list=None):

        if instrument_list is None:
            instr_list = [
                instr_code
                for instr_code in self.data.db_market_info.get_list_of_instruments()
            ]
        else:
            instr_list = instrument_list

        for instr in sorted(instr_list):

            self.data.log.msg(f"Starting market info update for '{instr}'")

            config = self.get_instr_config(instr)
            col_headers = []

            if not hasattr(config, "ig_data"):
                self.data.log.msg(f"Skipping {instr}, no IG config")
                continue

            if len(config.ig_data.periods) == 0:
                self.data.log.msg(f"Skipping {instr}, no epics defined")
                continue

            # list of what is currently in the db
            db_list = self.data.db_market_info.get_periods_for_instrument_code(instr)

            for period in config.ig_data.periods:
                db_list.remove(period)
                col_headers.append(period)
                epic = f"{config.ig_data.epic}.{period}.IP"

                try:
                    info = self.data.broker_conn.get_market_info(epic)
                    self.data.db_market_info.update_market_info(instr, epic, info)
                except Exception as exc:
                    msg = (
                        f"Problem updating market info for instrument '{instr}' "
                        f"and periods {config.ig_data.periods} - check config: {exc}"
                    )
                    self.data.log.error(msg)

            # anything remaining in db_list needs to be deleted
            for del_period in db_list:
                epic_to_delete = f"{config.ig_data.epic}.{del_period}.IP"
                self.data.log.msg(f"Removing unused epic {epic_to_delete}")
                self.data.db_market_info.delete_for_epic(epic_to_delete)

    def get_instr_config(self, instr) -> FsbInstrumentWithIgConfigData:
        return self.broker.broker_futures_instrument_data.get_futures_instrument_object_with_ig_data(
            instr
        )


if __name__ == "__main__":
    # update_fsb_market_info()
    update_fsb_market_info(["GOLD_fsb"])
