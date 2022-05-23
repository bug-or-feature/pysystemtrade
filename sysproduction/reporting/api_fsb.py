import pandas as pd
from functools import cached_property

from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.IG.ig_futures_contract_price_data import IgFuturesContractPriceData
from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysdata.data_blob import dataBlob
from sysproduction.data.contracts import dataContracts
from sysproduction.data.prices import diagPrices
from sysproduction.reporting.api import reportingApi
from sysproduction.reporting.data.fsb import fsb_correlation_data
from sysproduction.reporting.data.risk_fsb import (
    minimum_capital_table
)
from sysproduction.reporting.reporting_functions import table


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

    # all FSB correlations
    def table_of_problem_fsb_correlations(
            self,
            min_price_corr=0.8,
            min_returns_corr=0.6
    ) -> table:

        df = pd.DataFrame(self.correlation_data)
        df.set_index('Contract', inplace=True)
        df.Price = df.Price.round(2)
        df.Returns = df.Returns.round(2)
        df = df.loc[(df['Price'] < min_price_corr) | (df['Returns'] < min_returns_corr)]
        df = df.sort_values("Returns")

        return table("Problem FSB Correlations", df)

    # all FSB correlations
    def table_of_fsb_correlations(self) -> table:
        df = pd.DataFrame(self.correlation_data)
        df.set_index('Contract', inplace=True)
        df.Price = df.Price.round(2)
        df.Returns = df.Returns.round(2)

        return table("FSB Correlations", df)

    # FSB mappings_and_expiries
    def fsb_mappings_and_expiries(self, table_header="FSB mappings and expiries") -> table:
        contract_prices = IgFuturesContractPriceData(IGConnection())
        expiries = contract_prices.futures_instrument_data.expiry_dates

        rows = []
        for key, value in contract_prices.futures_instrument_data.epic_mapping.items():
            rows.append(
                dict(
                    Contract=key,
                    Epic=value,
                    Expiry=expiries[key]
                )
            )

        results = pd.DataFrame(rows)
        results.set_index("Contract", inplace=True)

        return table(table_header, results)

    @cached_property
    def correlation_data(self):
        futures_prices = arcticFuturesContractPriceData()
        fsb_prices = ArcticFsbContractPriceData()

        rows = []
        with dataBlob(log_name="FSB-Report") as data:
            price_data = diagPrices(data)
            diag_contracts = dataContracts(data)

            for instr_code in price_data.get_list_of_instruments_in_multiple_prices():
                all_contracts_list = diag_contracts.get_all_contract_objects_for_instrument_code(
                    instr_code
                )
                for contract in all_contracts_list.currently_sampling():
                    if futures_prices.has_data_for_contract(contract) and fsb_prices.has_data_for_contract(contract):
                        rows.append(fsb_correlation_data(contract, futures_prices, fsb_prices))
        return rows


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
