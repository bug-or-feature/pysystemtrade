from sysproduction.reporting.report_configs import reportConfig

instrument_risk_fsb_report_config = reportConfig(
    title="FSB Instrument risk report",
    function="sysproduction.reporting.instrument_risk_fsb_report.instrument_risk_fsb_report",
    output="file"
)

min_capital_fsb_report_config = reportConfig(
    title="FSB Minimum capital report",
    function="sysproduction.reporting.minimum_capital_fsb_report.minimum_capital_fsb_report",
    output="file"
)

remove_fsb_markets_report_config = reportConfig(
    title="Remove FSB markets report",
    function = "sysproduction.reporting.remove_fsb_markets_report.remove_fsb_markets_report",
    output="email"
)

fsb_report_config = reportConfig(
    title="Futures spread bet report",
    function="sysproduction.reporting.fsb_report.do_fsb_report",
    output="file"
)
