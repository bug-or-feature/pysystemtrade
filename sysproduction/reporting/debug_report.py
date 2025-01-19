import pickle
import pandas as pd

from syscore.fileutils import resolve_path_and_filename_for_package
from syscore.interactive.progress_bar import progressBar

# from syscore.pandas.pdutils import print_full
from sysdata.data_blob import dataBlob

from sysproduction.data.prices import get_list_of_instruments

from sysproduction.reporting.data.risk import get_risk_data_for_instrument
from sysproduction.reporting.report_configs import *
from sysproduction.reporting.reporting_functions import (
    run_report_with_data_blob,
    pandas_display_for_reports,
)

"""

>>> from sysproduction.reporting.debug_report import *
>>> run_roll_report()
>>> run_roll_report(instrument_code='GOLD')
>>> run_pandl_report()
>>> run_trade_report()
>>> run_strategy_report()
>>> run_risk_report()
>>> run_status_report()
>>> run_instrument_risk_report()
>>> run_min_capital_report()
>>> run_remove_markets_report()
>>> run_slippage_report()

"""


def do_report(config: reportConfig):
    pandas_display_for_reports()
    with dataBlob(
        log_name=f"Test_Report",
        csv_data_paths=dict(
            csvFuturesInstrumentData="/Users/ageach/Dev/work/pst-futures/data/futures/csvconfig",
        ),
    ) as data:
        run_report_with_data_blob(config, data)


def run_slippage_report():
    do_report(slippage_report_config.new_config_with_modified_output("console"))


def run_costs_report():
    do_report(costs_report_config.new_config_with_modified_output("console"))


def run_roll_report(instr_code=None):
    config = roll_report_config.new_config_with_modified_output("console")
    if instr_code is not None:
        config = config.new_config_with_modify_kwargs(instrument_code=instr_code)
    do_report(config)


def run_daily_pandl_report():
    do_report(daily_pandl_report_config.new_config_with_modified_output("console"))


def run_reconcile_report():
    do_report(reconcile_report_config.new_config_with_modified_output("console"))


def run_trade_report():
    do_report(
        trade_report_config.new_config_with_modify_kwargs(
            calendar_days_back=1,
        ).new_config_with_modified_output("console")
    )


def run_strategy_report():
    do_report(strategy_report_config.new_config_with_modified_output("console"))
    # do_report(
    #     strategy_report_config.new_config_with_modified_output("console").modify_kwargs(
    #         strategy_name="fsb_dynamic_strategy_v1_2",
    #         timestamp="20240801_120000",
    #     )
    # )


def run_risk_report():
    do_report(risk_report_config.new_config_with_modified_output("console"))


def run_status_report():
    do_report(status_report_config.new_config_with_modified_output("console"))


def run_liquidity_report():
    pass


def run_instrument_risk_report():
    do_report(instrument_risk_report_config.new_config_with_modified_output("console"))


def run_min_capital_report():
    do_report(min_capital_report_config.new_config_with_modified_output("console"))


def run_duplicate_market_report():
    pass


def run_remove_markets_report():
    do_report(remove_markets_report_config.new_config_with_modified_output("console"))


def run_market_monitor_report():
    do_report(market_monitor_report_config.new_config_with_modified_output("console"))


def run_account_curve_report():
    report_config = account_curve_report_config.new_config_with_modified_output("file")
    report_config.suffix = ".pdf"
    do_report(report_config)


if __name__ == "__main__":
    # run_slippage_report()
    # run_costs_report()
    # run_roll_report()
    # run_roll_report(instr_code="LEANHOG_fsb")
    run_daily_pandl_report()
    # run_reconcile_report()
    # run_trade_report()
    # run_strategy_report()
    # run_risk_report()
    # run_status_report()
    # run_liquidity_report()
    # run_instrument_risk_report()
    # run_min_capital_report()
    # run_duplicate_market_report()
    # run_remove_markets_report()
    # run_market_monitor_report()
    # run_account_curve_report()
    # run_slippage_report()

    # run_fsb_report()
    # run_min_capital_fsb_report()
    # run_instrument_risk_fsb_report()
    # run_fsb_remove_markets_report()
    # run_fsb_roll_report()
    # run_fsb_roll_report(instr_code="LEANHOG_fsb")
    # run_fsb_risk_report()
    # run_fsb_instrument_list_report()
    # run_fsb_static_selection_report()
    # run_fsb_trading_rule_pnl_report()

    # run_adhoc_tradeable_report()
    # run_adhoc_tradeable_report(instr_code="EDOLLAR_fsb")
    # run_adhoc_correlation_report("LEANHOG_fsb/20231200")
    # run_adhoc_correlation_report("LEANHOG_fsb/20231200", plot_returns=False)

    # run_adhoc_fsb_price_comparison_report(
    #     "HANG_fsb/20230300",
    #     "HANG_fsb/20230400",
    #     "HANG_fsb/20230500",
    # )
    # instrument_risk_csv()
    # run_fut_fsb_price_comparison_report()
    # run_adhoc_compare_adjusted_prices("BRENT_W_fsb")
