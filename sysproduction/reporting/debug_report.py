import pandas as pd
from syscore.pdutils import print_full
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysproduction.data.broker import dataBroker
from sysproduction.reporting.report_configs import *
from sysproduction.reporting.report_configs_fsb import *
from sysproduction.reporting.reporting_functions import (
    run_report_with_data_blob,
    pandas_display_for_reports,
)
from sysproduction.reporting.data.fsb_correlation_data import (
    fsb_correlation_data,
    contract_key,
)
from sysproduction.reporting.adhoc.fsb_contract_prices import (
    run_compare_fsb_contract_price_report,
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
        log_name=f"Test {config.title}",
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
        ),
    ) as data:
        data.add_class_object(mongoMarketInfoData)
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
    pass


def run_trade_report():
    do_report(trade_report_config.new_config_with_modified_output("console"))


def run_strategy_report():
    do_report(strategy_report_config.new_config_with_modified_output("console"))


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


def run_fsb_remove_markets_report():
    do_report(
        remove_fsb_markets_report_config.new_config_with_modified_output("console")
    )


def run_market_monitor_report():
    pass


def run_account_curve_report():
    pass


def run_min_capital_fsb_report():
    do_report(min_capital_fsb_report_config.new_config_with_modified_output("console"))


def run_fsb_report():
    do_report(fsb_report_config.new_config_with_modified_output("console"))


def run_instrument_risk_fsb_report():
    do_report(
        instrument_risk_fsb_report_config.new_config_with_modified_output("console")
    )


def run_fsb_roll_report(instr_code=None):
    config = fsb_roll_report_config.new_config_with_modified_output("console")
    if instr_code is not None:
        config = config.new_config_with_modify_kwargs(instrument_code=instr_code)
    do_report(config)


def run_adhoc_tradeable_report(instr_code: str):
    data = dataBlob()
    data.add_class_object(mongoMarketInfoData)
    expiries = data.db_market_info.expiry_dates

    rows = []
    for (
        key,
        value,
    ) in data.db_market_info.epic_mapping.items():

        if instr_code is None or key.startswith(instr_code):
            epic_info = data.broker_conn.rest_service.fetch_market_by_epic(value)
            status = epic_info.snapshot.marketStatus
            opening_hours = epic_info.instrument.openingHours

            rows.append(
                dict(
                    Contract=key,
                    Epic=value,
                    Expiry=expiries[key],
                    Status=status,
                    Hours=opening_hours,
                )
            )

    results = pd.DataFrame(rows)
    results.set_index("Contract", inplace=True)

    print_full(results)


def run_adhoc_correlation_report(key: str):
    fsb_correlation_data(contract_key(key), draw=True)


def run_adhoc_fsb_price_comparison_report(first: str, second: str, third: str):
    run_compare_fsb_contract_price_report(
        contract_key(first), contract_key(second), contract_key(third), draw=True
    )


if __name__ == "__main__":
    # run_slippage_report()
    # run_costs_report()
    # run_roll_report()
    # run_roll_report(instr_code="LEANHOG_fsb")
    # run_daily_pandl_report()
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

    run_fsb_report()
    # run_min_capital_fsb_report()
    # run_instrument_risk_fsb_report()
    # run_fsb_remove_markets_report()
    # run_fsb_roll_report()
    # run_fsb_roll_report(instr_code="LEANHOG_fsb")

    # run_adhoc_tradeable_report()
    # run_adhoc_tradeable_report(instr_code="EDOLLAR_fsb")
    # run_adhoc_correlation_report("LEANHOG_fsb/20230600")

    # run_adhoc_fsb_price_comparison_report(
    #     "HANG_fsb/20230300",
    #     "HANG_fsb/20230400",
    #     "HANG_fsb/20230500",
    # )
