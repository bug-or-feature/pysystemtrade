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
    stack_handler.create_broker_orders_from_contract_orders()
    stack_handler.data.close()


def do_refresh_additional_sampling_all_instruments():
    stack_handler = stackHandlerAdditionalSampling()
    stack_handler.log.label(type="stackHandlerAdditionalSampling")
    stack_handler.refresh_additional_sampling_all_instruments()
    stack_handler.data.close()


if __name__ == "__main__":
    # to run for just one instrument, edit
    # sysexecution/stack_handler/additional_sampling.py, line ~41
    do_refresh_additional_sampling_all_instruments()
