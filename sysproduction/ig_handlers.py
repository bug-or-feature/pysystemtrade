from syscontrol.run_process import processToRun

from sysexecution.ig_handler.ig_handler import igHandler
from sysdata.data_blob import dataBlob


# weekday
def run_ig_handler_weekday():
    process_name = "IG-Handler-Weekday"
    data = dataBlob(log_name=process_name)
    handler = igHandler(data)
    process = processToRun(
        process_name,
        data,
        [
            ("do_market_info_updates", handler),  # live
            ("refresh_additional_sampling_all_instruments", handler),  # live
        ],
    )
    process.run_process()


# weekend
def run_ig_handler_weekend():
    process_name = "IG-Handler-Weekend"
    data = dataBlob(log_name=process_name)
    handler = igHandler(data)
    process = processToRun(
        process_name,
        data,
        [
            ("do_market_info_updates", handler),  # live
        ],
    )
    process.run_process()


# overnight
def run_ig_handler_overnight():
    process_name = "run_ig_handler_overnight"
    data = dataBlob(log_name=process_name)
    handler = igHandler(data)
    process = processToRun(
        process_name,
        data,
        [
            ("do_history_status_updates", handler),
        ],
    )
    process.run_process()


if __name__ == "__main__":
    # run_ig_handler_weekday()
    # run_ig_handler_weekend()
    run_ig_handler_overnight()
