from sysdata.data_blob import dataBlob
from sysproduction.reporting.reporting_functions import (
    run_report_with_data_blob,
    pandas_display_for_reports,
)
from sysproduction.reporting.roll_report import ALL_ROLL_INSTRUMENTS
from sysproduction.reporting.report_configs import reportConfig


def test_report(
        format="console",
        title=None,
        function=None,
        instrument_code=None,
        use_db=True,
):

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
    if use_db:
        my_data = dataBlob(log_name="Test-Report-DB")
    else:
        my_data = dataBlob(
            log_name="Test-Report-CSV",
            class_list=[],
        )
    with my_data as data:
        run_report_with_data_blob(config, data)


def run_slippage_report():
    pass


def run_costs_report():
    pass


def run_roll_report(instrument_code=ALL_ROLL_INSTRUMENTS):
    test_report(
        title="Roll report",
        function="sysproduction.reporting.roll_report.roll_info",
        instrument_code=instrument_code,
    )


def run_daily_pandl_report():
    test_report(
        title="P&L report", function="sysproduction.reporting.pandl_report.pandl_info"
    )


def run_reconcile_report():
    pass


def run_trade_report():
    test_report(
        title="Trade report",
        function="sysproduction.reporting.trades_report.trades_info",
    )


def run_strategy_report():
    test_report(
        title="Strategy report",
        function="sysproduction.reporting.strategies_report.strategy_report",
    )


def run_risk_report():
    test_report(
        title="Risk report", function="sysproduction.reporting.risk_report.risk_report"
    )


def run_status_report():
    test_report(
        title="Status report",
        function="sysproduction.reporting.status_reporting.system_status",
    )


def run_liquidity_report():
    pass


def run_instrument_risk_report():
    test_report(
        title="Instrument Risk report",
        function="sysproduction.reporting.instrument_risk_report.instrument_risk_report"
    )


def run_min_capital_report():
    test_report(
        title="Minimum Capital report",
        function="sysproduction.reporting.minimum_capital_report.minimum_capital_report"
    )


def run_duplicate_market_report():
    pass


def run_remove_markets_report():
    test_report(
        title="Removed markets report",
        function="sysproduction.reporting.remove_markets_report.remove_markets_report"
    )


def run_market_monitor_report():
    pass


def run_account_curve_report():
    pass


# def run_min_capital_fsb_report():
#     test_report(
#         title="Minimum Capital FSB report",
#         function="sysproduction.reporting.minimum_capital_fsb_report.minimum_capital_fsb_report"
#     )
#
#
# def run_fsb_report():
#     test_report(
#         title="FSB report",
#         function="sysproduction.reporting.fsb_report.do_fsb_report"
#     )
#
# def run_instrument_risk_fsb_report():
#     test_report(
#         title="Instrument Risk FSB report",
#         function="sysproduction.reporting.instrument_risk_fsb_report.instrument_risk_fsb_report"
#     )


if __name__ == "__main__":
    # run_slippage_report()
    # run_costs_report()
    # run_roll_report()
    # run_daily_pandl_report()
    # run_reconcile_report()
    # run_trade_report()
    # run_strategy_report()
    # run_risk_report()
    run_status_report()
    # run_liquidity_report()
    # run_instrument_risk_report()
    # run_min_capital_report()
    # run_duplicate_market_report()
    # run_remove_markets_report()
    # run_market_monitor_report()
    # run_account_curve_report()