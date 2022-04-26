import pandas as pd

from sysproduction.reporting.api import reportingApi
from sysproduction.reporting.reporting_functions import table
from sysproduction.reporting.data.risk_fsb import (
    minimum_capital_table
)


class ReportingApiFsb(reportingApi):

    # def __init__(
    #         self,
    #         data: dataBlob,
    #         calendar_days_back: int = 250,
    #         end_date: datetime.datetime = arg_not_supplied,
    #         start_date: datetime.datetime = arg_not_supplied
    # ):
    #     super().__init__(
    #         data,
    #         calendar_days_back,
    #         end_date,
    #         start_date
    #     )

    # MINIMUM CAPITAL
    def table_of_minimum_capital_fsb(self) -> table:
        min_capital = minimum_capital_table(
            self.data,
            instrument_weight=0.1,
            only_held_instruments=False
        )
        # min_capital = min_capital.sort_values('minimum_capital')
        min_capital = min_capital.sort_values('min_cap_portfolio')

        min_capital = nice_format_min_capital_table(min_capital)
        min_capital_table = table("Minimum capital in base currency", min_capital)

        return min_capital_table


def nice_format_min_capital_table(df: pd.DataFrame) -> pd.DataFrame:
    df.min_bet = df.min_bet.round(2)
    df.price = df.price.round(2)
    df.ann_perc_stdev = df.ann_perc_stdev.round(1)
    df.risk_target = df.risk_target.astype(int)
    df.min_cap_min_bet = df.min_cap_min_bet.round(2)
    df.min_pos_avg_fc = df.min_pos_avg_fc.astype(int)
    df.min_cap_avg_fc = df.min_cap_avg_fc.round(2)
    df.instr_weight = df.instr_weight.round(2)
    df.IDM = df.IDM.round(2)
    df.min_cap_portfolio = df.min_cap_portfolio.astype(int)

    return df
