from sysexecution.stack_handler.additional_sampling import (
    stackHandlerAdditionalSampling,
)
from sysexecution.ig_handler.periodic_market_info import igHandlerMarketInfo


class igHandler(
    igHandlerMarketInfo,
    stackHandlerAdditionalSampling,
):
    pass
