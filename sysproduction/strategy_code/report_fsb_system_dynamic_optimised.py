import datetime
import pandas as pd

from sysproduction.reporting.reporting_functions import table, header, body_text
from sysdata.data_blob import dataBlob
from sysobjects.production.backtest_storage import interactiveBacktest
from sysproduction.strategy_code.report_system_classic import (
    report_system_classic_no_header_or_footer,
)
from sysproduction.data.optimal_positions import dataOptimalPositions


def report_fsb_system_dynamic(data: dataBlob, backtest: interactiveBacktest):
    format_output = []

    strategy_name = backtest.strategy_name
    timestamp = backtest.timestamp

    report_header = header(
        f"Strategy report for {strategy_name} (timestamp {timestamp}) "
        f"produced at {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    )
    format_output.append(report_header)

    optimal_positions_df = get_optimal_fsb_positions_table_as_df(
        data=data, strategy_name=backtest.strategy_name
    )
    optimal_positions_table = table("Optimal positions", optimal_positions_df)
    format_output.append(optimal_positions_table)

    format_output = report_system_classic_no_header_or_footer(
        data, backtest=backtest, format_output=format_output
    )

    format_output.append(body_text(f"End of report for {strategy_name}"))

    return format_output


def get_optimal_fsb_positions_table_as_df(
    data: dataBlob, strategy_name: str
) -> pd.DataFrame:
    data_optimal_positions = dataOptimalPositions(data)

    list_of_positions = (
        data_optimal_positions.get_list_of_current_optimal_positions_for_strategy_name(
            strategy_name
        )
    )
    as_verbose_pd = list_of_positions.as_verbose_pd()

    if len(as_verbose_pd) == 0:
        return pd.DataFrame()

    subset_of_pd = as_verbose_pd[
        [
            "dont_trade",
            "reduce_only",
            "weight_per_contract",
            "position_limit_weight",
            "optimum_weight",
            "start_weight",
            "maximum_weight",
            "minimum_weight",
            "previous_weight",
            "optimised_weight",
            "optimal_position",
            "position_limit_contracts",
            "min_bet",
            "previous_position",
            "optimised_position",
        ]
    ]
    subset_of_pd = subset_of_pd.rename(
        columns={
            "weight_per_contract": "weight_per_min_bet",
            "position_limit_contracts": "position_limit",
        },
    )

    subset_of_pd = subset_of_pd.round(2)

    subset_of_pd = subset_of_pd.sort_values("optimum_weight")

    return subset_of_pd
