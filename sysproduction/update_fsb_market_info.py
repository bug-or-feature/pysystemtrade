import logging

from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from syscore.objects import success


def update_fsb_market_info(instr_list=None):

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with dataBlob(log_name="Update-FSB-Market-Info") as data:
        update_epic_config = UpdateFsbMarketInfo(data)
        update_epic_config.do_updates(instr_list)

    return success


class UpdateFsbMarketInfo(object):
    def __init__(self, data):
        self.data = data
        self.data.add_class_object(mongoMarketInfoData)
        self._broker = dataBroker(self.data)

    @property
    def broker(self) -> dataBroker:
        return self._broker

    def do_updates(self, instrument_list):

        if instrument_list is None:
            instr_list = [
                instr_code
                for instr_code in self.data.broker_futures_instrument.get_list_of_instruments()
                if instr_code.endswith("_fsb")
            ]
        else:
            instr_list = instrument_list

        for instr in sorted(instr_list):

            self.data.log.msg(f"Starting processing for '{instr}'")

            config = self.get_instr_config(instr)
            col_headers = []

            if not hasattr(config, "ig_data"):
                self.data.log.msg(f"Skipping {instr}, no IG config")
                continue

            if len(config.ig_data.periods) == 0:
                self.data.log.msg(f"Skipping {instr}, no epics defined")
                continue

            for period in config.ig_data.periods:
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

    def get_instr_config(self, instr) -> FsbInstrumentWithIgConfigData:
        return self.broker.broker_futures_instrument_data.get_futures_instrument_object_with_ig_data(
            instr
        )


if __name__ == "__main__":
    # update_fsb_market_info()
    update_fsb_market_info(["EDOLLAR_fsb"])
