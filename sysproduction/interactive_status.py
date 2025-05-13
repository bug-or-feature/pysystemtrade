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
    data_broker = dataBroker(data)
    ans3 = data_broker.get_all_current_contract_positions()
    print("\nBROKER POSITIONS")
    print(ans3.as_pd_df().sort_values(["instrument_code", "contract_date"]))
    breaks = data_broker.get_list_of_breaks_between_broker_and_db_contract_positions()
    if len(breaks) > 0:
        print(
            "\nBREAKS between broker and DB stored contract positions: %s\n"
            % str(breaks)
        )
    else:
        print("(No breaks positions consistent)")
    return None


if __name__ == "__main__":
    interactive_status()
