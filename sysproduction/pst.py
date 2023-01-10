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
    # click.echo("outer")


@pst.command(name="c")
def con():
    """Interactive controls"""
    interactive_controls()


@pst.command(name="d")
def diag():
    """Interactive diagnostics"""
    interactive_diagnostics()


@pst.command(name="r")
def roll():
    """Interactive update roll status"""
    interactive_update_roll_status()


@pst.command(name="h")
def hist():
    """Interactive update historical prices"""
    interactive_manual_check_historical_prices()


@pst.command(name="p")
def cap():
    """Interactive update capital"""
    interactive_update_capital_manual()


@pst.command(name="s")
def ord():
    """Interactive order stack"""
    interactive_order_stack()


if __name__ == "__main__":
    pst()
