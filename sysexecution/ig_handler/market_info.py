from syscore.exceptions import missingData
from sysexecution.ig_handler.ig_handler import igHandler
from sysobjects.contracts import futuresContract


class igHandlerMarketInfo(igHandler):
    def do_market_info_updates(self):

        """
        For a given max epics, say 10 (configurable), fill with:
        - the epic associated with any contract orders (rotate if more than max)
        - any epic about to expire (rotate if more than max)
        - the least recently updated epics
        """

        epic_list = []

        try:

            list_of_contract_order_ids = self.contract_stack.get_list_of_order_ids(
                exclude_inactive_orders=False
            )
            for contract_order_id in list_of_contract_order_ids:
                order = self.contract_stack.get_order_with_id_from_stack(
                    contract_order_id
                )
                epic = self.update_market_info.db_market_info.get_epic_for_contract(
                    order.futures_contract
                )
                epic_list.append(epic)

        except Exception as ex:
            self.data.log.error(f"Problem with blah: {ex}")
