import logging
from munch import munchify
from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from syscore.constants import success


def update_fsb_market_info(instr_list=None):

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

    def do_market_info_updates(self, instrument_list=None, check_historic=True):

        if instrument_list is None:
            instr_list = [
                instr_code
                for instr_code in self.data.db_market_info.get_list_of_instruments()
            ]
        else:
            instr_list = instrument_list

        for instr in sorted(instr_list):

            self.data.log.debug(f"Starting market info update for '{instr}'")

            config = self.get_instr_config(instr)
            col_headers = []

            if not hasattr(config, "ig_data"):
                self.data.log.debug(f"Skipping {instr}, no IG config")
                continue

            if len(config.ig_data.periods) == 0:
                self.data.log.debug(f"Skipping {instr}, no epics defined")
                continue

            # list of what is currently in the db
            db_list = self.data.db_market_info.get_periods_for_instrument_code(instr)
            periods = config.ig_data.periods

            for period in periods:
                if period in db_list:
                    db_list.remove(period)
                col_headers.append(period)
                epic = f"{config.ig_data.epic}.{period}.IP"

                self.update_market_info_for_epic(
                    instr, epic, check_historic=check_historic
                )

            # anything remaining in db_list needs to be deleted
            for del_period in db_list:
                epic_to_delete = f"{config.ig_data.epic}.{del_period}.IP"
                self.data.log.debug(f"Removing unused epic {epic_to_delete}")
                self.data.db_market_info.delete_for_epic(epic_to_delete)

    def update_market_info_for_epic(self, instr, epic, check_historic=False):
        try:
            info = self.data.broker_conn.get_market_info(epic)
            if check_historic:
                historic = self._get_historic_data_for_epic(epic)
                if historic is not None:
                    info["historic"] = historic
            self.data.db_market_info.update_market_info(instr, epic, info)
        except Exception as exc:
            msg = (
                f"Problem updating market info for epic '{epic}' ({instr}) "
                f"- check config: {exc}"
            )
            self.data.log.error(msg)

    def _get_historic_data_for_epic(self, epic):
        for res in IGConnection.PRICE_RESOLUTIONS:
            try:
                hist_df = self.data.broker_conn.get_historical_fsb_data_for_epic(
                    epic=epic,
                    bar_freq=res,
                    numpoints=1,
                    warn_for_nans=True,
                )
                hist_dict = hist_df.to_dict(orient="records")
                historic = dict(
                    timestamp=hist_df.index[-1],
                    bid=hist_dict[0]["Close.bid"],
                    ask=hist_dict[0]["Close.ask"],
                    bar_freq=res,
                )
                return historic

            except Exception as exc:
                msg = (
                    f"Problem getting historic data for '{epic}' at "
                    f"resolution '{res}': {exc}"
                )
                self.data.log.error(msg)

        return None

    def do_historic_status_check(self, instrument_list=None):

        if instrument_list is None:
            instr_list = [
                instr_code
                for instr_code in self.data.db_market_info.get_list_of_instruments()
            ]
        else:
            instr_list = instrument_list

        for instr in sorted(instr_list):

            # self.data.log.debug(
            #     f"Starting market info historic status check for '{instr}'"
            # )

            config = self.get_instr_config(instr)

            if not hasattr(config, "ig_data"):
                self.data.log.debug(f"Skipping {instr}, no IG config")
                continue

            if len(config.ig_data.periods) == 0:
                self.data.log.debug(f"Skipping {instr}, no epics defined")
                continue

            for (
                info_dict
            ) in self.data.db_market_info.get_market_info_for_instrument_code(instr):
                info = munchify(info_dict)
                if "historic" in info:
                    bid_diff = round(info.snapshot.bid - info.historic.bid, 2)
                    bid_diff_pc = round((bid_diff / info.snapshot.bid) * 100, 2)
                    ask_diff = round(info.snapshot.offer - info.historic.ask)
                    ask_diff_pc = round((ask_diff / info.snapshot.offer) * 100, 2)
                    date_diff = info.last_modified_utc - info.historic.timestamp
                    if bid_diff_pc > 0.1 or ask_diff_pc > 0.1 or date_diff.days > 3:
                        self.data.log.debug(
                            f"Historic status for {instr} ({info.epic}): "
                            f"bid diff {bid_diff}, ({bid_diff_pc}%), "
                            f"ask diff {ask_diff}, ({ask_diff_pc}%), "
                            f"timestamp diff {date_diff}, "
                            f"bar_freq {info.historic.bar_freq}, "
                            f"status {info.in_hours_status}"
                        )

    def get_instr_config(self, instr) -> FsbInstrumentWithIgConfigData:
        return self.broker.broker_futures_instrument_data.get_futures_instrument_object_with_ig_data(
            instr
        )


def check_historic_status(instr_list=None):

    with dataBlob(log_name="Update-FSB-Market-Info") as data:
        historic_status_check_config = UpdateFsbMarketInfo(data)
        historic_status_check_config.do_historic_status_check(instr_list)

    return success


if __name__ == "__main__":
    # update_fsb_market_info()
    # check_historic_status()
    # epic = "GOLD_fsb"
    # epic = "SOYBEAN_fsb"
    # update_fsb_market_info([epic])
    # check_historic_status([epic])

    update_epic_config = UpdateFsbMarketInfo(dataBlob())
    update_epic_config.update_market_info_for_epic("GOLD_fsb", "MT.D.GC.Month3.IP")
