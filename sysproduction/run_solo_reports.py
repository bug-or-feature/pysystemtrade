from sysdata.data_blob import dataBlob
from sysproduction.reporting.reporting_functions import (
    run_report_with_data_blob,
    pandas_display_for_reports,
)
from sysproduction.reporting.roll_report import ALL_ROLL_INSTRUMENTS
from sysproduction.reporting.report_configs import reportConfig


def run_solo_report(format="console", title=None, function=None, instrument_code=None):

    if instrument_code is None:
        config = reportConfig(title=title, function=function, output=format)
    else:
        config = reportConfig(
            title=title,
            function=function,
            instrument_code=instrument_code,
            output=format,
        )
    pandas_display_for_reports()
    with dataBlob(log_name="Solo-Report") as data:
        run_report_with_data_blob(config, data)


def run_status_report():
    run_solo_report(
        title="Status report",
        function="sysproduction.reporting.status_reporting.system_status",
    )


def run_roll_report(instrument_code=ALL_ROLL_INSTRUMENTS):
    run_solo_report(
        title="Roll report",
        function="sysproduction.reporting.roll_report.roll_info",
        instrument_code=instrument_code,
    )


def run_pandl_report():
    run_solo_report(
        title="P&L report", function="sysproduction.reporting.pandl_report.pandl_info"
    )


def run_trade_report():
    run_solo_report(
        title="Trade report",
        function="sysproduction.reporting.trades_report.trades_info",
    )


def run_strategy_report():
    run_solo_report(
        title="Strategy report",
        function="sysproduction.reporting.strategies_report.strategy_report",
    )


def run_risk_report():
    run_solo_report(
        title="Risk report", function="sysproduction.reporting.risk_report.risk_report"
    )


if __name__ == "__main__":

    # costs_report:
    # run_solo_report(title="Costs report", function="sysproduction.reporting.costs_report.costs_report") # NOT WORKING

    # liquidity_report:
    # DONT CARE

    # status_report:
    # run_solo_report(title="Status report", function="sysproduction.reporting.status_reporting.system_status")

    # roll_report:
    # run_solo_report(title="Roll report", function="sysproduction.reporting.roll_report.roll_info", instrument_code=ALL_ROLL_INSTRUMENTS)

    # daily_pandl_report:
    # run_solo_report(title="P&L report", function="sysproduction.reporting.pandl_report.pandl_info")

    # reconcile_report:
    # run_solo_report(title="Reconcile report", function="sysproduction.reporting.reconcile_report.reconcile_info") # BROKEN

    # trade_report:
    # run_solo_report(title="Trade report", function="sysproduction.reporting.trades_report.trades_info")

    # strategy_report:
    run_solo_report(
        title="Strategy report",
        function="sysproduction.reporting.strategies_report.strategy_report",
    )

    # risk_report:
    # run_solo_report(title="Risk report", function="sysproduction.reporting.risk_report.risk_report")
