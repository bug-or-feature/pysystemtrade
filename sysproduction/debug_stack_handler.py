from sysexecution.stack_handler.checks import stackHandlerChecks
from sysexecution.stack_handler.spawn_children_from_instrument_orders import stackHandlerForSpawning
from sysexecution.stack_handler.roll_orders import stackHandlerForRolls
from sysexecution.stack_handler.create_broker_orders_from_contract_orders import stackHandlerCreateBrokerOrders


def do_check_external_position_break():
    checks = stackHandlerChecks()
    checks.check_external_position_break()


def do_spawn_children_from_new_instrument_orders():
    spawner = stackHandlerForSpawning()
    spawner.spawn_children_from_new_instrument_orders()


def do_force_roll_orders():
    roller = stackHandlerForRolls()
    roller.generate_force_roll_orders()


def do_create_broker_orders_from_contract_orders():
    handler = stackHandlerCreateBrokerOrders()
    handler.create_broker_orders_from_contract_orders()