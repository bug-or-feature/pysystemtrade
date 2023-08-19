from sysexecution.stack_handler.stackHandlerCore import stackHandlerCore
from sysproduction.data.fsb_epics import UpdateMarketInfo


class igHandlerCore(stackHandlerCore):
    @property
    def update_market_info(self) -> UpdateMarketInfo:
        update_market_info = getattr(self, "_update_market_info", None)
        if update_market_info is None:
            update_market_info = UpdateMarketInfo(self.data)
            self._update_market_info = update_market_info

        return update_market_info
