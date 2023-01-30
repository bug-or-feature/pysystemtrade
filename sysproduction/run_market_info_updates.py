from syscontrol.run_process import processToRun
from sysdata.data_blob import dataBlob
from sysproduction.update_fsb_market_info import UpdateFsbMarketInfo


def run_market_info_updates():
    process_name = "run_market_info_updates"
    data = dataBlob(log_name=process_name)
    list_of_timer_names_and_functions = get_list_of_timer_functions()
    process = processToRun(process_name, data, list_of_timer_names_and_functions)
    process.run_process()


def get_list_of_timer_functions():
    data_fsb_market_info = dataBlob(log_name="data_fsb_market_info")
    fsb_market_info_object = UpdateFsbMarketInfo(data_fsb_market_info)

    list_of_timer_names_and_functions = [
        ("do_updates", fsb_market_info_object),
    ]

    return list_of_timer_names_and_functions


if __name__ == "__main__":
    run_market_info_updates()
