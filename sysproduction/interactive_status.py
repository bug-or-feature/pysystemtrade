import pandas as pd
import logging
from syscore.constants import arg_not_supplied
from syscore.exceptions import missingData
from syscore.interactive.display import set_pd_print_options
from sysdata.data_blob import dataBlob
from sysexecution.stack_handler.stack_handler import stackHandler
from sysproduction.data.broker import dataBroker
from sysproduction.data.capital import dataCapital
from sysproduction.interactive_order_stack import view_generic_stack


def interactive_status():
    with dataBlob(log_name="Interactive-Order-Stack", ib_conn=arg_not_supplied) as data:
        set_pd_print_options()
        view_instrument_stack(data)
        view_capital(data)
        view_positions(data)


def view_instrument_stack(data):
    stack_handler = stackHandler(data)
    print("\nINSTRUMENT STACK \n")
    view_generic_stack(stack_handler.instrument_stack)


def view_capital(data):
    data_capital = dataCapital(data)
    print("\nCAPITAL")
    try:
        all_calcs = data_capital.get_series_of_all_global_capital()
    except missingData:
        print("No capital setup yet")
    else:
        print(all_calcs.tail(5))


def view_positions(data):
    logging.getLogger("ib_insync").setLevel(logging.WARNING)
    data_broker = dataBroker(data)
    positions = data_broker.get_all_current_contract_positions()
    positions = positions.as_pd_df()

    print("\nBROKER POSITIONS")
    print(positions.sort_values(["instrument_code", "contract_date"]))

    portfolio_items = data_broker.get_all_portfolio_items()
    full = positions.merge(portfolio_items, on="instrument_code")
    print("\nPORTFOLIO ITEMS")
    print(f"{full.sort_values(['instrument_code', 'contract_date'])}\n")

    return None


if __name__ == "__main__":
    interactive_status()
