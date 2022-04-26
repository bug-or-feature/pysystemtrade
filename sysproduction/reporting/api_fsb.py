import pandas as pd

from sysproduction.reporting.api import reportingApi
from sysproduction.reporting.reporting_functions import table
from sysproduction.reporting.data.risk_fsb import (
    minimum_capital_table
)


class ReportingApiFsb(reportingApi):

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

    def table_of_risk_all_fsb_instruments(
            self,
            table_header="Risk of all instruments with data - sorted by annualised % standard deviation",
            sort_by='annual_perc_stdev'
    ):
        instrument_risk_all = self.instrument_risk_data_all_instruments()
        instrument_risk_all = instrument_risk_all.rename(columns={
            "point_size_base": "min_bet",
            "contract_exposure": "exposure",
            "annual_risk_per_contract": "annual_risk_min_bet",
        })
        instrument_risk_sorted = instrument_risk_all.sort_values(sort_by)
        instrument_risk_sorted = instrument_risk_sorted[
            [
                'daily_price_stdev', 'annual_price_stdev', 'price', 'daily_perc_stdev',
                'annual_perc_stdev', 'min_bet', 'exposure', 'annual_risk_min_bet'
            ]
        ]
        instrument_risk_sorted = instrument_risk_sorted.round(
            {
                'daily_price_stdev': 2,
                'annual_price_stdev': 2,
                'price': 2,
                'daily_perc_stdev': 3,
                'annual_perc_stdev': 1,
                'min_bet': 2,
                'exposure': 0,
                'annual_risk_min_bet': 0
            }
        )
        instrument_risk_sorted_table = table(
            table_header,
            instrument_risk_sorted
        )

        return instrument_risk_sorted_table


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
