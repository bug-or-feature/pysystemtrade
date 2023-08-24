import datetime
import pandas as pd
from functools import cached_property

from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.data_blob import dataBlob
from sysproduction.data.contracts import dataContracts
from sysproduction.data.prices import diagPrices
from sysproduction.data.instruments import diagInstruments
from sysproduction.data.fsb_prices import DiagFsbPrices
from sysproduction.data.fsb_epics import DiagFsbEpics
from sysproduction.reporting.api import reportingApi
from sysproduction.reporting.data.fsb_correlation_data import fsb_correlation_data
from sysproduction.reporting.data.risk_fsb import minimum_capital_table
from sysproduction.reporting.reporting_functions import table
from sysproduction.reporting.data.rolls_fsb import (
    get_roll_data_for_fsb_instrument,
)
from sysobjects.production.roll_state import ALL_ROLL_INSTRUMENTS
from sysproduction.update_sampled_contracts import (
    get_furthest_out_contract_with_roll_parameters,
    create_contract_date_chain,
)
from syscore.dateutils import contract_month_from_number


class ReportingApiFsb(reportingApi):

    ### MINIMUM CAPITAL
    def table_of_minimum_capital_fsb(self) -> table:
        min_capital = minimum_capital_table(
            self.data, instrument_weight=0.1, only_held_instruments=False
        )
        # min_capital = min_capital.sort_values('minimum_capital')
        min_capital = min_capital.sort_values("min_cap_portfolio")

        min_capital = nice_format_min_capital_table(min_capital)
        min_capital_table = table("Minimum capital in base currency", min_capital)

        return min_capital_table

    def _get_roll_data_dict(self, instrument_code: str = ALL_ROLL_INSTRUMENTS):
        # list_of_instruments = ["PALLAD_fsb"]
        if instrument_code is ALL_ROLL_INSTRUMENTS:
            list_of_instruments = self._list_of_all_instruments()
        else:
            list_of_instruments = [instrument_code]
        data = self.data

        roll_data_dict = {}
        for instrument_code in list_of_instruments:
            roll_data = get_roll_data_for_fsb_instrument(instrument_code, data)
            roll_data_dict[instrument_code] = roll_data

        return roll_data_dict

    def _list_of_all_instruments(self):
        diag_prices = DiagFsbPrices(self.data)
        list_of_instruments = diag_prices.get_list_of_instruments_in_multiple_prices()

        return list_of_instruments

    def table_of_fsb_instrument_risk(self):
        instrument_risk_data = self.instrument_risk_data()
        fsb_instrument_risk_data = nice_format_fsb_instrument_risk_table(
            instrument_risk_data
        )
        table_fsb_instrument_risk = table(
            "FSB Instrument risk", fsb_instrument_risk_data
        )
        return table_fsb_instrument_risk

    def table_of_risk_all_fsb_instruments(
        self,
        table_header="Risk of all instruments with data - sorted by annualised % standard deviation",
        sort_by="annual_perc_stdev",
    ):
        instrument_risk_all = self.instrument_risk_data_all_instruments()
        instrument_risk_all = instrument_risk_all.rename(
            columns={
                "point_size_base": "min_bet",
                "contract_exposure": "exposure",
                "annual_risk_per_contract": "annual_risk_min_bet",
            }
        )
        instrument_risk_sorted = instrument_risk_all.sort_values(sort_by)
        instrument_risk_sorted = instrument_risk_sorted[
            [
                "daily_price_stdev",
                "annual_price_stdev",
                "price",
                "daily_perc_stdev",
                "annual_perc_stdev",
                "min_bet",
                "exposure",
                "annual_risk_min_bet",
            ]
        ]
        instrument_risk_sorted = instrument_risk_sorted.round(
            {
                "daily_price_stdev": 2,
                "annual_price_stdev": 2,
                "price": 2,
                "daily_perc_stdev": 3,
                "annual_perc_stdev": 1,
                "min_bet": 2,
                "exposure": 0,
                "annual_risk_min_bet": 0,
            }
        )
        instrument_risk_sorted_table = table(table_header, instrument_risk_sorted)

        return instrument_risk_sorted_table

    def table_of_wrong_min_bet_size(
        self, table_header="Misconfigured minimum bet size"
    ) -> table:

        df = pd.DataFrame(self.market_info_data)
        df = df[["Contract", "ExpectedMinBet", "ActualMinBet", "Status"]]
        df = df.loc[(df["ExpectedMinBet"] != df["ActualMinBet"])]
        df.set_index("Contract", inplace=True)

        return table(table_header, df)

    def table_of_delayed_market_info(self, table_header="Delayed Market Info") -> table:
        delayed = datetime.datetime.now() - datetime.timedelta(days=3)
        df = pd.DataFrame(self.market_info_data)
        df = df[["Contract", "LastMod"]]
        df = df.loc[(df["LastMod"] < delayed)]
        df.set_index("Contract", inplace=True)

        return table(table_header, df)

    def table_of_epic_period_mismatches(self) -> table:
        df = pd.DataFrame(self.epic_periods)
        if len(self.epic_periods) > 0:
            df.set_index("Instrument", inplace=True)
            df = df.sort_values("Instrument")

        return table("Epic period mismatches", df)

    def table_of_problem_fsb_rolls(self) -> table:
        df = pd.DataFrame(self.chain_data)
        if len(self.chain_data) > 0:
            df.set_index("Instrument", inplace=True)
            df = df.sort_values("Instrument")

        return table("Problem FSB Rolls", df)

    # all FSB correlations
    def table_of_problem_fsb_correlations(
        self, min_price_corr=0.8, min_returns_corr=0.6
    ) -> table:

        df = pd.DataFrame(self.correlation_data)
        df.set_index("Contract", inplace=True)
        df.Price = df.Price.round(2)
        df.Returns = df.Returns.round(2)
        df = df.loc[(df["Price"] < min_price_corr) | (df["Returns"] < min_returns_corr)]
        df = df.sort_values("Returns")

        return table("Problem FSB Correlations", df)

    def table_of_problem_priced_fsb_correlations(
        self, min_price_corr=0.8, min_returns_corr=0.6
    ) -> table:

        df = pd.DataFrame(self.correlation_data)
        df.set_index("Contract", inplace=True)
        df.Price = df.Price.round(2)
        df.Returns = df.Returns.round(2)
        df = df.loc[
            df["IsPriced"]
            & ((df["Price"] < min_price_corr) | (df["Returns"] < min_returns_corr))
        ]
        df = df.sort_values("Returns")

        return table(
            "Problem FSB Correlations for priced contracts", df[["Price", "Returns"]]
        )

    def table_of_problem_forward_fsb_correlations(
        self, min_price_corr=0.8, min_returns_corr=0.6
    ) -> table:

        df = pd.DataFrame(self.correlation_data)
        df.set_index("Contract", inplace=True)
        df.Price = df.Price.round(2)
        df.Returns = df.Returns.round(2)
        df = df.loc[
            df["IsFwd"]
            & ((df["Price"] < min_price_corr) | (df["Returns"] < min_returns_corr))
        ]
        df = df.sort_values("Returns")

        return table(
            "Problem FSB Correlations for forward contracts", df[["Price", "Returns"]]
        )

    # all FSB correlations
    def table_of_fsb_correlations(self) -> table:
        df = pd.DataFrame(self.correlation_data)
        df.set_index("Contract", inplace=True)
        df.Price = df.Price.round(2)
        df.Returns = df.Returns.round(2)

        return table("FSB Correlations", df[["Price", "Returns"]])

    @cached_property
    def market_info_data(self):

        roll_data = self._get_roll_data_dict()

        epics = self.data.db_market_info.epic_mapping
        expiries = self.data.db_market_info.expiry_dates
        in_hours = self.data.db_market_info.in_hours
        in_hours_status = self.data.db_market_info.in_hours_status
        last_modified = self.data.db_market_info.last_modified
        min_bet = self.data.db_market_info.min_bet

        rows = []

        diag_instruments = diagInstruments(self.data)

        for key, value in epics.items():
            instr_code = key[:-9]
            meta_data = diag_instruments.get_meta_data(instr_code)
            if instr_code not in roll_data:
                continue
            if roll_data[instr_code]["contract_priced"] == key[-8:]:
                pos = "priced"
            elif roll_data[instr_code]["contract_fwd"] == key[-8:]:
                pos = "fwd"
            else:
                pos = "-"
            rows.append(
                dict(
                    InstrCode=instr_code,
                    Contract=key,
                    Epic=value,
                    Expiry=expiries[key],
                    Status=in_hours_status[key],
                    In_Hours=in_hours[key],
                    LastMod=last_modified[key],
                    Pos=pos,
                    ExpectedMinBet=meta_data.Pointsize,
                    ActualMinBet=min_bet[key],
                )
            )

        return rows

    # FSB mappings_and_expiries
    def fsb_mappings_and_expiries(
        self, table_header="FSB mappings and expiries"
    ) -> table:

        results = pd.DataFrame(self.market_info_data)
        results = results[["Contract", "Epic", "Expiry", "Status", "In_Hours", "Pos"]]
        results.set_index("Contract", inplace=True)

        return table(table_header, results)

    @cached_property
    def epic_periods(self):
        rows = []
        instr_list = self.data.db_epic_periods.get_list_of_instruments()
        # instr_list = ["EURIBOR-ICE_fsb"]
        for instr in instr_list:
            instr_config = self.data.broker_futures_instrument.get_futures_instrument_object_with_ig_data(
                instr
            )
            configured = instr_config.ig_data.periods
            calculated = self.data.db_epic_periods.get_epic_periods_for_instrument_code(
                instr
            )
            if sorted(configured) != sorted(calculated):
                rows.append(
                    dict(
                        Instrument=instr,
                        Configured=sorted(configured),
                        Calculated=sorted(calculated),
                    )
                )

        return rows

    @cached_property
    def chain_data(self):
        rows = []
        diagFsbEpics = DiagFsbEpics(self.data)
        # for instr in ["CAD_fsb"]:
        for instr in self._list_of_all_instruments():
            epic_history = diagFsbEpics.get_epic_history(instr)

            furthest_out_contract = get_furthest_out_contract_with_roll_parameters(
                self.data, instr
            )
            contract_date_chain = create_contract_date_chain(
                furthest_out_contract, use_priced=False
            )
            date_str_chain = [
                contract_date.date_str for contract_date in contract_date_chain
            ]

            expected_chain = list(reversed(date_str_chain))
            actual_chain = epic_history.roll_chain()

            length = min(len(expected_chain), len(actual_chain))

            if expected_chain[:length] == actual_chain[:length]:
                continue
            else:
                rows.append(
                    dict(
                        Instrument=instr,
                        Expected=self.pretty_print(expected_chain[:length]),
                        Actual=self.pretty_print(actual_chain[:length]),
                    )
                )

        return rows

    def pretty_print(self, contract_date_str_list):
        return [
            contract_month_from_number(int(contract[4:6]))
            for contract in contract_date_str_list
        ]

    @cached_property
    def correlation_data(self):
        futures_prices = arcticFuturesContractPriceData()
        fsb_prices = ArcticFsbContractPriceData()

        rows = []
        with dataBlob(log_name="FSB-Report") as data:
            price_data = diagPrices(data)
            diag_contracts = dataContracts(data)

            for instr_code in price_data.get_list_of_instruments_in_multiple_prices():

                contract_priced = diag_contracts.get_priced_contract_id(instr_code)
                contract_fwd = diag_contracts.get_forward_contract_id(instr_code)

                all_contracts_list = (
                    diag_contracts.get_all_contract_objects_for_instrument_code(
                        instr_code
                    )
                )
                for contract in all_contracts_list.currently_sampling():
                    if futures_prices.has_merged_price_data_for_contract(
                        contract
                    ) and fsb_prices.has_merged_price_data_for_contract(contract):

                        is_priced = contract.date_str == contract_priced
                        is_fwd = contract.date_str == contract_fwd

                        rows.append(
                            fsb_correlation_data(
                                contract,
                                futures_prices=futures_prices,
                                fsb_prices=fsb_prices,
                                is_priced=is_priced,
                                is_fwd=is_fwd,
                            )
                        )
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


def nice_format_fsb_instrument_risk_table(
    instrument_risk_data: pd.DataFrame,
) -> pd.DataFrame:
    instrument_risk_data.daily_price_stdev = (
        instrument_risk_data.daily_price_stdev.round(3)
    )
    instrument_risk_data.annual_price_stdev = (
        instrument_risk_data.annual_price_stdev.round(3)
    )
    instrument_risk_data.price = instrument_risk_data.price.round(2)
    instrument_risk_data.daily_perc_stdev = instrument_risk_data.daily_perc_stdev.round(
        2
    )
    instrument_risk_data.annual_perc_stdev = (
        instrument_risk_data.annual_perc_stdev.round(1)
    )
    instrument_risk_data.point_size_base = instrument_risk_data.point_size_base.round(1)
    instrument_risk_data.contract_exposure = (
        instrument_risk_data.contract_exposure.astype(int)
    )
    instrument_risk_data.daily_risk_per_contract = (
        instrument_risk_data.daily_risk_per_contract.astype(int)
    )
    instrument_risk_data.annual_risk_per_contract = (
        instrument_risk_data.annual_risk_per_contract.astype(int)
    )
    instrument_risk_data.position = instrument_risk_data.position.round(2)
    instrument_risk_data.capital = instrument_risk_data.capital.astype(int)
    instrument_risk_data.exposure_held_perc_capital = (
        instrument_risk_data.exposure_held_perc_capital.round(1)
    )
    instrument_risk_data.annual_risk_perc_capital = (
        instrument_risk_data.annual_risk_perc_capital.round(1)
    )

    instrument_risk_data.rename(
        columns={
            "contract_exposure": "min_bet_exposure",
            "daily_risk_per_contract": "daily_risk_per_min_bet",
            "annual_risk_per_contract": "annual_risk_per_min_bet",
        },
        inplace=True,
    )

    return instrument_risk_data
