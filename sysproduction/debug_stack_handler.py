from sysexecution.stack_handler.checks import stackHandlerChecks
from sysexecution.stack_handler.spawn_children_from_instrument_orders import (
    stackHandlerForSpawning,
)
from sysexecution.stack_handler.roll_orders import stackHandlerForRolls
from sysexecution.stack_handler.create_broker_orders_from_contract_orders import (
    stackHandlerCreateBrokerOrders,
)
from sysexecution.stack_handler.additional_sampling import (
    stackHandlerAdditionalSampling,
)
from sysexecution.stack_handler.completed_orders import (
    stackHandlerForCompletions,
)
from sysexecution.stack_handler.fills import stackHandlerForFills
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from syslogging.logger import *


def do_check_external_position_break():
    stack_handler = stackHandlerChecks()
    stack_handler.log.label(type="stackHandlerChecks")
    stack_handler.check_external_position_break()
    stack_handler.data.close()


def do_spawn_children_from_new_instrument_orders():
    stack_handler = stackHandlerForSpawning()
    stack_handler.log.label(type="stackHandlerForSpawning")
    stack_handler.spawn_children_from_new_instrument_orders()
    stack_handler.data.close()


def do_force_roll_orders():
    stack_handler = stackHandlerForRolls()
    stack_handler.log.label(type="stackHandlerForRolls")
    stack_handler.generate_force_roll_orders()
    stack_handler.data.close()


def do_create_broker_orders_from_contract_orders():
    stack_handler = stackHandlerCreateBrokerOrders()
    stack_handler.log.label(type="stackHandlerCreateBrokerOrders")
    stack_handler.create_broker_orders_from_contract_orders(test_mode=False)
    stack_handler.data.close()


def do_refresh_additional_sampling_all_instruments():
    stack_handler = stackHandlerAdditionalSampling(
        # data=dataBlob(log=get_logger("stackHandlerAdditionalSampling"))
        data=dataBlob(log=get_logger("refresh_additional_sampling_all_instruments"))
    )
    stack_handler.data.add_class_object(mongoMarketInfoData)
    # stack_handler.log.label(type="stackHandlerAdditionalSampling")
    stack_handler.refresh_additional_sampling_all_instruments()
    stack_handler.data.close()


def do_process_fills_stack():
    stack_handler = stackHandlerForFills()
    stack_handler.log.label(type="stackHandlerForFills")
    stack_handler.process_fills_stack()
    stack_handler.data.close()


def do_completed_orders():
    stack_handler = stackHandlerForCompletions()
    stack_handler.log.label(type="stackHandlerForCompletions")
    stack_handler.handle_completed_orders()
    stack_handler.data.close()


def debug_get_all_priced_epics():
    stack_handler = stackHandlerAdditionalSampling(
        # data=dataBlob(log=get_logger("debug_get_all_priced_epics"))
        # data=dataBlob(log=get_logger("refresh_additional_sampling_all_instruments"))
    )
    stack_handler.data.add_class_object(mongoMarketInfoData)

    # stack_handler.log.label(type="stackHandlerAdditionalSampling")
    stack_handler.debug_get_all_priced_epics()
    stack_handler.data.close()


if __name__ == "__main__":
    # to run for just one instrument, edit
    # sysexecution/stack_handler/additional_sampling.py, line ~41
    # do_refresh_additional_sampling_all_instruments()
    # do_process_fills_stack()
    # do_create_broker_orders_from_contract_orders()
    # do_force_roll_orders()
    do_check_external_position_break()
    # do_completed_orders()
    # debug_get_all_priced_epics()
