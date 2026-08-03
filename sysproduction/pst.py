import sys
import traceback
from functools import partial

import click

from sysproduction.interactive_controls import interactive_controls
from sysproduction.interactive_diagnostics import interactive_diagnostics
from sysproduction.interactive_update_roll_status import interactive_update_roll_status
from sysproduction.interactive_manual_check_historical_prices import (
    interactive_manual_check_historical_prices,
)
from sysproduction.interactive_update_capital_manual import (
    interactive_update_capital_manual,
)
from sysproduction.interactive_order_stack import interactive_order_stack
from sysproduction.interactive_manual_check_fx_prices import (
    interactive_manual_check_fx_prices,
)
from sysproduction.interactive_status import interactive_status

QUIT_KEY = "q"

TOOLS = [
    ("c", "Interactive controls", interactive_controls),
    ("d", "Interactive diagnostics", interactive_diagnostics),
    ("r", "Interactive update roll status", interactive_update_roll_status),
    (
        "h",
        "Interactive update historical prices",
        interactive_manual_check_historical_prices,
    ),
    ("p", "Interactive update capital", interactive_update_capital_manual),
    ("s", "Interactive order stack", interactive_order_stack),
    (
        "f",
        "Interactive update historical fx prices",
        interactive_manual_check_fx_prices,
    ),
    ("t", "Interactive status", interactive_status),
]


def _run_tool(tool_function):
    if not sys.stdin.isatty():
        tool_function()
        return
    try:
        tool_function()
    except SystemExit:
        # some tools call sys.exit() when finished; return to the menu instead
        pass
    except KeyboardInterrupt:
        print("\nInterrupted - returning to menu")
    except Exception:
        traceback.print_exc()


def _menu_loop():
    if not sys.stdin.isatty():
        return
    tool_functions = {key: tool_function for key, _, tool_function in TOOLS}
    while True:
        click.echo("\n==== pst ====\n")
        for key, label, _ in TOOLS:
            click.echo("%s: %s" % (key, label))
        click.echo("%s: Quit" % QUIT_KEY)
        try:
            choice = input("\nYour choice? ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if choice == QUIT_KEY:
            break
        tool_function = tool_functions.get(choice)
        if tool_function is None:
            click.echo("'%s' is not a valid option" % choice)
            continue
        click.clear()
        _run_tool(tool_function)


@click.group(invoke_without_command=True)
@click.pass_context
def pst(ctx):
    click.clear()
    if ctx.invoked_subcommand is None and not sys.stdin.isatty():
        click.echo(ctx.get_help())


@pst.result_callback()
def _return_to_menu(result, **kwargs):
    _menu_loop()


for _key, _label, _tool_function in TOOLS:
    pst.add_command(
        click.Command(
            name=_key, callback=partial(_run_tool, _tool_function), help=_label
        )
    )


if __name__ == "__main__":
    pst()
