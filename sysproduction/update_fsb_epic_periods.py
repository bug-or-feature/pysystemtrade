import logging
import datetime
import string
import random
from munch import munchify
from sysbrokers.IG.ig_instruments import (
    FsbInstrumentWithIgConfigData,
)
from sysdata.mongodb.mongo_epic_periods import mongoEpicPeriodsData
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from syscore.constants import success
from syscore.exceptions import missingContract

# start 2023-02-15 21:16:44
# end 2023-02-15 21:24:28  8 mins per instrument
def update_periods(instr_list=None, test_mode=False):

    with dataBlob(log_name="Update-FSB-Epic-Periods") as data:
        update_fsb_epic_periods = updateFsbEpicPeriods(data)
        update_fsb_epic_periods.do_epic_discovery(instr_list, test_mode=test_mode)

    return success


class updateFsbEpicPeriods(object):

    MAX_COUNT_PER_RUN = 20

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
            i_list = full_list[: self.MAX_COUNT_PER_RUN]
            random.shuffle(i_list)
        else:
            i_list = instrument_list

        for instr in i_list:

            self.data.log.msg(f"Starting IG Epic Discovery for '{instr}'")

            config = self.get_instr_config(instr)
            epic_base = config.epic

            if epic_base.startswith("CF."):
                self.data.log.msg(f"Ignoring '{instr}', regular quarterly HMUZ periods")
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
                    market_info = self.data.broker_conn.get_market_info(epic)
                    if self._is_valid(market_info):
                        periods.append(period)
                except missingContract:
                    # this is an invalid epic, happens a lot, we don't care
                    pass
                except Exception as exc:
                    self.data.log.error(f"Problem with epic {epic}: {exc}")

            if epic_base.startswith("CF."):
                self.data.log.msg(f"Not writing periods for {instr}, it's FX")
            else:
                self.data.log.msg(f"Epic periods: {periods}")
                if len(periods) == 0:
                    # TODO how to inform?
                    self.data.log.warning(
                        f"Zero periods for {instr}, something went wrong - "
                        f"not writing"
                    )
                else:
                    record = {
                        "epic_periods": periods,
                        "timestamp": datetime.datetime.now(),
                    }
                    self.data.db_epic_periods.update_epic_periods(instr, record)

    def get_instr_config(self, instr) -> FsbInstrumentWithIgConfigData:
        return self.broker.broker_futures_instrument_data.get_futures_instrument_object_with_ig_data(
            instr
        )

    def _is_valid(self, market_info):
        info = munchify(market_info)
        if info.instrument.expiry == "DFB":
            return False
        if info.snapshot.marketStatus == "CLOSED":
            return False
        return True

    # TODO check iterators for efficiency
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

        results.append("VNEAR")
        results.append("NEAR")
        results.append("VFAR")
        results.append("VVFAR")
        results.append("FAR")
        results.append("FAR1")
        results.append("FAR2")
        results.append("FAR3")
        results.append("FAR4")
        results.append("FAR5")
        results.append("FAR6")
        results.append("FAR7")
        results.append("FAR8")
        results.append("FAR9")

        self.data.log.msg(f"Periods to try: {results}")
        return results


if __name__ == "__main__":
    # update_periods(test_mode=True)
    instr_list = [
        "AEX_fsb",
        "ASX_fsb",
        "BOBL_fsb",
        "BRENT_W_fsb",
        "BTP_fsb",
        "BUND_fsb",
        "BUXL_fsb",
        "CAC_fsb",
        "COCOA_LDN_fsb",
        "COCOA_fsb",
        "COFFEE_fsb",
        "COPPER_fsb",
        "CORN_fsb",
        "COTTON2_fsb",
        "CRUDE_W_fsb",
        "DAX_fsb",
        "DOW_fsb",
        "DX_fsb",
        "EDOLLAR_fsb",
        "EUA_fsb",
        "EURIBOR_fsb",
        "EUROSTX_fsb",
        "FED_fsb",
        "FTSE100_fsb",
        "GASOIL_fsb",
        "GASOLINE_fsb",
        "GAS_US_fsb",
        "GILT_fsb",
        "GOLD_fsb",
        "HANG_fsb",
        "HEATOIL_fsb",
        "IBXEX_fsb",
        "JGB_fsb",
        "JSE40_fsb",
        "LEANHOG_fsb",
        "LIVECOW_fsb",
        "LUMBER_fsb",
        "MSCISING_fsb",
        "NASDAQ_fsb",
        "NIKKEI_fsb",
        "OATIES_fsb",
        "OAT_fsb",
        "OJ_fsb",
        "OMXS30_fsb",
        "PALLAD_fsb",
        "PLAT_fsb",
        "RICE_fsb",
        "ROBUSTA_fsb",
        "RUSSELL_fsb",
        "SHATZ_fsb",
        "SILVER_fsb",
        "SMI_fsb",
        "SONIA3_fsb",
        "SOYBEAN_fsb",
        "SOYMEAL_fsb",
        "SOYOIL_fsb",
        "SP500_fsb",
        "SUGAR11_fsb",
        "SUGAR_WHITE_fsb",
        "US10_fsb",
        "US2_fsb",
        "US30U_fsb",
        "US30_fsb",
        "US5_fsb",
        "V2X_fsb",
        "VIX_fsb",
        "WHEAT_ICE_fsb",
        "WHEAT_fsb",
    ]
    update_periods(instr_list, test_mode=True)
    # update_periods([], test_mode=True)
    # update_periods(["CAD_fsb"], test_mode=True)
