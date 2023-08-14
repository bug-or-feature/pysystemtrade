from sysexecution.ig_handler.additional_sampling import (
    igHandlerAdditionalSampling,
)
from sysexecution.ig_handler.market_info import (
    igHandlerMarketInfo,
)
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from syslogging.logger import *


def do_refresh_additional_sampling_all_instruments():
    ig_handler = igHandlerAdditionalSampling(
        # data=dataBlob(log=get_logger("stackHandlerAdditionalSampling"))
        data=dataBlob(log_name="refresh_additional_sampling_all_instruments")
    )
    ig_handler.data.add_class_object(mongoMarketInfoData)
    # stack_handler.log.label(type="stackHandlerAdditionalSampling")
    ig_handler.refresh_additional_sampling_all_instruments()
    ig_handler.data.close()


def do_market_info_updates():
    ig_handler = igHandlerMarketInfo(
        # data=dataBlob(log=get_logger("stackHandlerAdditionalSampling"))
        data=dataBlob(log_name="refresh_additional_sampling_all_instruments")
    )
    # ig_handler.data.add_class_object(mongoMarketInfoData)
    # stack_handler.log.label(type="stackHandlerAdditionalSampling")
    ig_handler.do_market_info_updates()
    ig_handler.data.close()


if __name__ == "__main__":
    # to run for just one instrument, edit
    # sysexecution/stack_handler/additional_sampling.py, line ~41
    # do_refresh_additional_sampling_all_instruments()
    do_market_info_updates()
    # debug_get_all_priced_epics()
