import pandas as pd
from datetime import datetime
from sysdata.arctic.arctic_fsb_epics_history import ArcticFsbEpicHistoryData
from sysdata.csv.csv_fsb_epics_history_data import (
    CsvFsbEpicHistoryData,
    EPIC_HISTORY_DIRECTORY,
)
from syscore.pdutils import print_full
from sysdata.config.production_config import get_production_config
from syscore.fileutils import get_filename_for_package
from sysobjects.epic_history import FsbEpicsHistory, BetExpiry
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData

prod_backup = get_filename_for_package(
    get_production_config().get_element_or_missing_data("prod_backup")
)
datapath = EPIC_HISTORY_DIRECTORY
# datapath = f"{prod_backup}/epic_history"

input_data = CsvFsbEpicHistoryData(datapath=datapath)
output_data = ArcticFsbEpicHistoryData()


def import_epics_history_single(instrument_code):

    print(f"Importing epics history for {instrument_code}")

    status = output_data.add_epics_history(
        instrument_code,
        # TODO remove duplicates before importing
        input_data.get_epic_history(instrument_code),
        ignore_duplication=True,
    )

    df = output_data.get_epic_history(instrument_code)
    print_full(df)
    print(f"\n{status}")

    return status


def import_epics_history_all():
    for instr in input_data.get_list_of_instruments():
        import_epics_history_single(instr)


def view_epics_history_single(instrument_code):

    print(f"Epics history for {instrument_code}:")

    df = output_data.get_epic_history(instrument_code)
    print_full(df)


def delete_epics_history_single(instrument_code):

    print(f"Deleting epics history for {instrument_code}")

    status = output_data.delete_epics_history(instrument_code)
    print(f"\n{status}")

    return status


def convert_to_new_format():

    market_info = mongoMarketInfoData()
    new_output_data = CsvFsbEpicHistoryData(
        datapath="data.futures_spreadbet.epic_history_new"
    )
    instr_list = input_data.get_list_of_instruments()
    # instr_list = ["GOLD_fsb"]
    for instr in instr_list:
        epic_hist = input_data.get_epic_history(instr)

        results = {}
        index = 0
        for row in epic_hist.to_dict(orient="records"):
            if index == (epic_hist.shape[0] - 1):
                now = datetime.now()
                results[epic_hist.index[index]] = _build_epic_history_row(
                    instr, market_info, row
                )
                results[now.strftime("%Y-%m-%d %H:%M:%S")] = _build_epic_history_row(
                    instr, market_info, row, calc_status=True
                )
            else:
                results[epic_hist.index[index]] = _build_epic_history_row(
                    instr, market_info, row
                )
            index = index + 1

        new_df = pd.DataFrame.from_dict(
            results, orient="index", columns=epic_hist.columns.values
        )

        new_output_data.add_epics_history(instr, FsbEpicsHistory(new_df))


def _build_epic_history_row(instr, market_info, row, calc_status=False):
    row_values = []
    for value in row.values():
        try:
            old_format_row = BetExpiry(value)
            if calc_status:
                status = market_info.in_hours_status[
                    f"{instr}/{old_format_row.pst_date_key}"
                ]
                row_values.append(
                    f"{old_format_row.epic_key}|{old_format_row.expiry_date}|{status}"
                )
            else:
                row_values.append(
                    f"{old_format_row.epic_key}|{old_format_row.expiry_date}|UNKNOWN"
                )
        except:
            row_values.append("UNMAPPED")
    return row_values


if __name__ == "__main__":
    # view_epics_history_single("SOYOIL_fsb")
    # for epic in ["GOLD_fsb"]:
    #     import_epics_history_single(epic)
    import_epics_history_all()
    # for instr in ["SWE30_fsb"]:
    #     delete_epics_history_single(instr)

    # test_new_format()
