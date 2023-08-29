import random
import datetime

from syscore.constants import arg_not_supplied
from syscore.exceptions import missingData
from sysdata.data_blob import dataBlob
from sysexecution.ig_handler.igHandlerCore import igHandlerCore
from sysproduction.data.market_info import UpdateMarketInfo


class igHandlerMarketInfo(igHandlerCore):

    MAX_UPDATES = 10

    def __init__(self, data: dataBlob = arg_not_supplied):
        super().__init__(data)
        self._update_market_info = UpdateMarketInfo(self.data)

    def do_market_info_updates(self):

        """
        For a given max epics, say 5 (configurable), fill with:
        - the epic associated with any active contract orders (rotate if more than max)
        - any epic about to expire (rotate if more than max)
        - the least recently updated epics
        """

        count = 0

        order_epics = self.randomize_sublist(self.get_order_epics(), self.MAX_UPDATES)
        self.log.info(
            f"Updating {len(order_epics) if order_epics else 0} epics with live orders"
        )
        count = self.update_info_for_epics(order_epics, count)

        my_delta = datetime.timedelta(minutes=15)
        # my_delta = datetime.timedelta(days=4)
        expiry_epics = self.get_expiry_epics(
            delta=my_delta, limit=(self.MAX_UPDATES - count)
        )
        self.log.info(
            f"Updating {len(expiry_epics) if expiry_epics else 0} epics expiring shortly"
        )
        count = self.update_info_for_epics(expiry_epics, count)

        update_epics = self.get_update_epics(limit=self.MAX_UPDATES - count)
        self.log.info(f"Updating the {len(update_epics)} least recently updated epics")
        self.update_info_for_epics(update_epics, count)

        oldest = self.get_update_epics(limit=1)
        info = self.data.db_market_info.get_market_info_for_epic(oldest[0])
        oldest_ts = info["last_modified_utc"]
        diff = datetime.datetime.utcnow() - oldest_ts
        self.log.info(f"Oldest market info: {diff}")

    def update_info_for_epics(self, epic_list: list, count: int):
        for epic in epic_list:
            instr_code = self.data.db_market_info.instr_code[epic]
            self._update_market_info.update_market_info_for_epic(instr_code, epic)
            count = count + 1
        return count

    def get_order_epics(self):
        epics = []

        list_of_contract_order_ids = self.contract_stack.get_list_of_order_ids(
            exclude_inactive_orders=True
        )
        for contract_order_id in list_of_contract_order_ids:
            order = self.contract_stack.get_order_with_id_from_stack(contract_order_id)
            try:
                epic = self.update_market_info.db_market_info.get_epic_for_contract(
                    order.futures_contract
                )
                epics.append(epic)

            except missingData as ex:
                self.data.log.error(f"Problem getting epic for contract: {ex}")

        return epics

    def get_expiry_epics(self, delta=None, limit: int = 5):
        return self.update_market_info.db_market_info.find_epics_close_to_expiry(
            delta=delta, limit=limit
        )

    def get_update_epics(self, limit: int = 20):
        return self.update_market_info.db_market_info.find_epics_to_update(limit=limit)

    @staticmethod
    def randomize_sublist(data: list, size: int):
        if len(data) > 0:
            random.shuffle(data)
            if len(data) > size:
                return data[:size]
            else:
                return data
        else:
            return []
