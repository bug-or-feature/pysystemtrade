from sysdata.arctic.arctic_fsb_epics_history import ArcticFsbEpicHistoryData
from sysdata.csv.csv_fsb_epics_history_data import CsvFsbEpicHistoryData
from syscore.pdutils import print_full

input_data = CsvFsbEpicHistoryData()
output_data = ArcticFsbEpicHistoryData()


def import_epics_history_single(instrument_code):

    print(f"Importing epics history for {instrument_code}")

    status = output_data.add_epics_history(
        instrument_code,
        input_data.get_epic_history(instrument_code),
        ignore_duplication=True
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


if __name__ == "__main__":
    #view_epics_history_single("SOYOIL_fsb")
    for epic in ["COCOA_fsb", "COTTON2_fsb", "FED_fsb", "SONIA3_fsb", "WHEAT_ICE_fsb", ]:
        import_epics_history_single(epic)
    #import_epics_history_all()