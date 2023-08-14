from syscontrol.run_process import processToRun

from sysexecution.ig_handler.ig_handler import igHandler
from sysdata.data_blob import dataBlob


def run_ig_handler():
    process_name = "run_ig_handler"
    data = dataBlob(log_name=process_name)
    list_of_timer_names_and_functions = get_list_of_timer_functions_for_ig_handler()
    price_process = processToRun(process_name, data, list_of_timer_names_and_functions)
    price_process.run_process()


def get_list_of_timer_functions_for_ig_handler():
    ig_handler_data = dataBlob(log_name="ig_handler")
    ig_handler = igHandler(ig_handler_data)
    list_of_timer_names_and_functions = [
        ("do_market_info_updates", ig_handler),  # live
        ("refresh_additional_sampling_all_instruments", ig_handler),  # live
    ]

    return list_of_timer_names_and_functions


if __name__ == "__main__":
    run_ig_handler()
