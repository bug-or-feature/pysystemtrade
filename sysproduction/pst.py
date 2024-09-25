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


@click.group()
def pst():
    click.clear()


@click.command(name="c")
def controls():
    """Interactive controls"""
    interactive_controls()


@click.command(name="d")
def diagnostics():
    """Interactive diagnostics"""
    interactive_diagnostics()


@click.command(name="r")
def roll():
    """Interactive update roll status"""
    interactive_update_roll_status()


@click.command(name="h")
def historic():
    """Interactive update historical prices"""
    interactive_manual_check_historical_prices()


@click.command(name="p")
def capital():
    """Interactive update capital"""
    interactive_update_capital_manual()


@click.command(name="s")
def orders():
    """Interactive order stack"""
    interactive_order_stack()


pst.add_command(controls)
pst.add_command(diagnostics)
pst.add_command(roll)
pst.add_command(historic)
pst.add_command(capital)
pst.add_command(orders)


if __name__ == "__main__":
    pst()
