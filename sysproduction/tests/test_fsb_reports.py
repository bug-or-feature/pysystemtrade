from sysproduction.tests.test_reports import test_report


def run_min_capital_fsb_report():
    test_report(
        title="Minimum Capital FSB report",
        function="sysproduction.reporting.minimum_capital_fsb_report.minimum_capital_fsb_report"
    )


def run_fsb_report():
    test_report(
        title="FSB report",
        function="sysproduction.reporting.fsb_report.do_fsb_report"
    )


def run_instrument_risk_fsb_report():
    test_report(
        title="Instrument Risk FSB report",
        function="sysproduction.reporting.instrument_risk_fsb_report.instrument_risk_fsb_report"
    )


if __name__ == "__main__":
    run_fsb_report()
    # run_min_capital_fsb_report()
    # run_instrument_risk_fsb_report()