from sysdata.arctic.arctic_fsb_epics_history import ArcticFsbEpicHistoryData
from sysdata.csv.csv_fsb_epics_history_data import CsvFsbEpicHistoryData, EPIC_HISTORY_DIRECTORY
from syscore.pdutils import print_full
from sysdata.config.production_config import get_production_config
from syscore.fileutils import get_filename_for_package

prod_backup = get_filename_for_package(get_production_config().get_element_or_missing_data('prod_backup'))
datapath = EPIC_HISTORY_DIRECTORY
#datapath = f"{prod_backup}/epic_history"

input_data = CsvFsbEpicHistoryData(
    datapath=datapath
)
output_data = ArcticFsbEpicHistoryData()


def import_epics_history_single(instrument_code):

    print(f"Importing epics history for {instrument_code}")

    status = output_data.add_epics_history(
        instrument_code,
        # TODO remove duplicates before importing
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


def delete_epics_history_single(instrument_code):

    print(f"Deleting epics history for {instrument_code}")

    status = output_data.delete_epics_history(instrument_code)
    print(f"\n{status}")

    return status


if __name__ == "__main__":
    #view_epics_history_single("SOYOIL_fsb")
    #for epic in ["GOLD_fsb" ]:
    for epic in ["OMXS30_fsb"]:
         import_epics_history_single(epic)
    #import_epics_history_all()
    for instr in ["SWE30_fsb"]:
        delete_epics_history_single(instr)
