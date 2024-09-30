from sysproduction.reporting.report_configs import reportConfig
from sysobjects.production.roll_state import ALL_ROLL_INSTRUMENTS

instrument_risk_fsb_report_config = reportConfig(
    title="FSB Instrument risk report",
    function="sysproduction.reporting.instrument_risk_fsb_report.instrument_risk_fsb_report",
    output="file",
)

min_capital_fsb_report_config = reportConfig(
    title="FSB Minimum capital report",
    function="sysproduction.reporting.minimum_capital_fsb_report.minimum_capital_fsb_report",
    output="file",
)

remove_fsb_markets_report_config = reportConfig(
    title="Remove FSB markets report",
    function="sysproduction.reporting.remove_fsb_markets_report.remove_fsb_markets_report",
    output="email",
)

fsb_report_config = reportConfig(
    title="Futures spread bet report",
    function="sysproduction.reporting.fsb_report.do_fsb_report",
    output="file",
)

fsb_roll_report_config = reportConfig(
    title="FSB Roll report",
    function="sysproduction.reporting.fsb_roll_report.fsb_roll_report",
    instrument_code=ALL_ROLL_INSTRUMENTS,
    output="email",
)

fsb_risk_report_config = reportConfig(
    title="Risk report",
    function="sysproduction.reporting.fsb_risk_report.risk_report",
    output="email",
)

fsb_trading_rule_pandl_report_config = reportConfig(
    title="Trading Rule P&L report",
    function="sysproduction.reporting.trading_rule_pandl_report.trading_rule_pandl_report",
    output="email",
    config_filename="systems.futures_spreadbet.config.fsb_dynamic_system_v1_4.yaml",
    dict_of_rule_groups=dict(
        carry=["carry10", "carry30", "carry60", "carry125"],
        ewmac_momentum=[
            "momentum4",
            "momentum8",
            "momentum16",
            "momentum32",
            "momentum64",
        ],
        acceleration=["accel16", "accel32", "accel64"],
        breakout=[
            "breakout10",
            "breakout20",
            "breakout40",
            "breakout80",
            "breakout160",
            "breakout320",
        ],
        normalised_momentum=[
            "normmom2",
            "normmom4",
            "normmom8",
            "normmom16",
            "normmom32",
            "normmom64",
        ],
    ),
    # list_of_periods=["YTD", "1Y", "3Y", "10Y", "99Y"],
    list_of_periods=["1Y", "3Y", "10Y"],
)
