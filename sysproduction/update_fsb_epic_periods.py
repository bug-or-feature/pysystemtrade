import logging
from datetime import datetime
import string
from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.mongodb.mongo_epic_periods import mongoEpicPeriodsData
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from syscore.constants import success

# start 2023-02-15 21:16:44
# end 2023-02-15 21:24:28  8 mins per instrument
def update_periods(instr_list=None, test_mode=False):

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    with dataBlob(log_name="Update-FSB-Epic-Periods") as data:
        update_fsb_epic_periods = updateFsbEpicPeriods(data)
        update_fsb_epic_periods.do_epic_discovery(instr_list, test_mode=test_mode)

    return success


class updateFsbEpicPeriods(object):

    MAX_COUNT_PER_RUN = 10


    def __init__(self, data):
        self._data = data
        self.data.add_class_object(mongoEpicPeriodsData)
        self._broker = dataBroker(self._data)

    @property
    def data(self) -> dataBlob:
        return self._data

    @property
    def broker(self) -> dataBroker:
        return self._broker

    def do_epic_discovery(self, instrument_list=None, test_mode=False):

        # do MAX_COUNT_PER_RUN instruments, in reverse order of when it was last run
        if instrument_list is None:
            full_list = [
                instrument_code
                for instrument_code in self.data.db_epic_periods.get_list_of_instruments()
            ]
            instr_list = full_list[:self.MAX_COUNT_PER_RUN]
        else:
            instr_list = instrument_list[:self.MAX_COUNT_PER_RUN]

        for instr in instr_list:

            self.data.log.msg(f"Starting IG Epic Discovery for '{instr}'")

            config = self.get_instr_config(instr)
            epic_base = config.epic

            if epic_base.startswith("CF."):
                self.data.log.msg(f"Ignoring '{instr}' - regular quarterly periods")
                cycle_types = []
            else:
                if test_mode:
                    cycle_types = config.ig_data.periods
                else:
                    cycle_types = self._month_and_number_combinator()

            periods = []
            for period in cycle_types:
                epic = f"{epic_base}.{period}.IP"

                try:
                    self.data.broker_conn.get_market_info(epic)
                    periods.append(period)
                except Exception as exc:
                    self.data.log.error(f"Problem with info: {exc}")

            self.data.log.msg(f"Epic periods: {periods}")

            record = {
                "epic_periods": periods,
                "timestamp": datetime.now()
            }

            self.data.db_epic_periods.update_epic_periods(instr, record)

    def get_instr_config(self, instr) -> FsbInstrumentWithIgConfigData:
        return self.broker.broker_futures_instrument_data.get_futures_instrument_object_with_ig_data(
            instr
        )

    def _month_and_number_combinator(self):
        results = []
        numerator = []
        for count in range(1, 25):
            numerator.append(count)
        for cap in list(string.ascii_uppercase):
            numerator.append(cap)

        month_types = ("Month", "MONTH", "month", "Mnth")
        for num in numerator:
            for month in month_types:
                results.append(f"{month}{num}")

        results.append('VNEAR')
        results.append('NEAR')
        results.append('FAR')
        results.append('VFAR')
        results.append('VVFAR')

        self.data.log.msg(f"Periods to try: {results}")
        return results


if __name__ == "__main__":
    update_periods(test_mode=True)
    # update_periods(["GOLD_fsb"], test_mode=True)
