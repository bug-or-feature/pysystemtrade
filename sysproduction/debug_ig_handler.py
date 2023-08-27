from sysdata.data_blob import dataBlob
from sysexecution.stack_handler.additional_sampling import (
    stackHandlerAdditionalSampling,
)
from sysexecution.ig_handler.periodic_market_info import (
    igHandlerMarketInfo,
)


def do_refresh_additional_sampling_all_instruments():
    ig_handler = stackHandlerAdditionalSampling(
        data=dataBlob(log_name="refresh_additional_sampling_all_instruments")
    )
    ig_handler.refresh_additional_sampling_all_instruments()
    ig_handler.data.close()


def do_market_info_updates():
    ig_handler = igHandlerMarketInfo(
        data=dataBlob(log_name="IG-Handler-Market-Info-Updates")
    )
    ig_handler.do_market_info_updates()
    ig_handler.data.close()


def do_history_status_updates():
    ig_handler = igHandlerMarketInfo(
        data=dataBlob(log_name="IG-Handler-Historic-Market-Info-Updates")
    )
    ig_handler.do_history_status_updates()
    ig_handler.data.close()


if __name__ == "__main__":
    # to run for just one instrument, edit
    # sysexecution/stack_handler/additional_sampling.py, line ~41
    # do_refresh_additional_sampling_all_instruments()
    # do_market_info_updates()
    do_history_status_updates()
    # debug_get_all_priced_epics()
