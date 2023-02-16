from syscontrol.run_process import processToRun
from sysdata.data_blob import dataBlob
from sysproduction.update_fsb_epic_periods import updateFsbEpicPeriods


def run_epic_discovery():
    process_name = "run_epic_discovery"
    data = dataBlob(log_name=process_name)
    list_of_timer_names_and_functions = get_list_of_timer_functions()
    process = processToRun(process_name, data, list_of_timer_names_and_functions)
    process.run_process()


def get_list_of_timer_functions():
    epic_discovery_data = dataBlob(log_name="epic_discovery")
    update_fsb_epic_periods = updateFsbEpicPeriods(epic_discovery_data)

    list_of_timer_names_and_functions = [
        ("do_epic_discovery", update_fsb_epic_periods),
    ]

    return list_of_timer_names_and_functions


if __name__ == "__main__":
    run_epic_discovery()
