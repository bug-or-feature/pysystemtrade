import datetime
import pandas as pd
from functools import cached_property

from syscore.constants import arg_not_supplied
from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.data_blob import dataBlob
from sysproduction.data.contracts import dataContracts
from sysproduction.data.prices import diagPrices
from sysproduction.data.fsb_instruments import diagFsbInstruments
from sysproduction.data.fsb_prices import DiagFsbPrices
from sysproduction.data.fsb_epics import DiagFsbEpics
from sysproduction.data.positions import diagPositions
from sysproduction.reporting.api import reportingApi
from sysproduction.reporting.data.fsb_correlation_data import fsb_correlation_data
from sysproduction.reporting.data.risk_fsb import minimum_capital_table
from sysproduction.reporting.reporting_functions import table, body_text
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
    def __init__(
        self,
        data: dataBlob,
        calendar_days_back: int = arg_not_supplied,
        end_date: datetime.datetime = arg_not_supplied,
        start_date: datetime.datetime = arg_not_supplied,
        start_period: str = arg_not_supplied,
        end_period: str = arg_not_supplied,
    ):
        super().__init__(
            data, calendar_days_back, end_date, start_date, start_period, end_period
        )
        self._prices = diagPrices(self.data)
        self._fsb_prices = DiagFsbPrices(self.data)
        self._instruments = diagFsbInstruments(self.data)
        self._epics = DiagFsbEpics(self.data)
        self._contracts = dataContracts(self.data)
        self._positions = diagPositions(self.data)

    def __repr__(self):
        return "ReportingApiFsb instance"

    @property
    def futures_prices(self) -> diagPrices:
        return self._prices

    @property
    def fsb_prices(self) -> DiagFsbPrices:
        return self._fsb_prices

    @property
    def positions(self) -> diagPositions:
        return self._positions

    @property
    def fsb_instruments(self) -> diagFsbInstruments:
        return self._instruments

    @property
    def contracts(self) -> dataContracts:
        return self._contracts

    @property
    def epics(self) -> DiagFsbEpics:
        return self._epics

    @property
    def broker_history(self) -> pd.DataFrame:
        return self.cache.get(self._get_broker_history)

    def _get_broker_history(self) -> pd.DataFrame:
        broker_orders = self.get_recent_broker_history(
            start_date=self.start_date, end_date=self.end_date
        )
        return broker_orders

    def get_recent_broker_history(self, start_date, end_date):
        history = self.data.broker_conn.get_history(start=start_date, end=end_date)
        return history

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
            roll_data = get_roll_data_for_fsb_instrument(
                instrument_code,
                data,
                self.contracts,
                self.positions,
                self.fsb_instruments,
            )
            roll_data_dict[instrument_code] = roll_data

        return roll_data_dict

    def _list_of_all_instruments(self):
        list_of_instruments = (
            self.fsb_prices.get_list_of_instruments_in_multiple_prices()
        )

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

    def table_of_missing_epics(
        self, table_header="Missing forward epic", style="fwd"
    ) -> table:
        df = pd.DataFrame(self.market_info_data)
        grouped = df.groupby("InstrCode")["Pos"].apply(
            lambda ser: ser.str.contains(style).sum()
        )
        rows = []
        for instr_code in grouped.index.values:
            if grouped[instr_code] == 0:
                since = self.get_time_since_last_roll_date(instr_code)
                rows.append(
                    dict(Instrument=instr_code, Since_Roll=f"{since.days: >10}")
                )

        new_df = pd.DataFrame(rows)
        return table(table_header, new_df)

    def get_time_since_last_roll_date(self, instr_code):
        now = datetime.datetime.now()
        df = self.data.db_futures_multiple_prices.get_multiple_prices(instr_code)
        df["diff"] = df.index.to_series().diff()
        roll_date = df[df["diff"] < datetime.timedelta(seconds=61)].index[-1]
        since = now - roll_date
        return since

    def table_of_wrong_min_bet_size(
        self, table_header="Misconfigured minimum bet size"
    ) -> table:
        df = pd.DataFrame(self.market_info_data)
        df = df[["Contract", "ExpectedMinBet", "ActualMinBet", "In_Hours_Status"]]
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
        in_hours_status = self.data.db_market_info.in_hours_status
        last_modified = self.data.db_market_info.last_modified
        min_bet = self.data.db_market_info.min_bet
        synced = self.data.db_market_info.sync_status

        rows = []

        for key, value in epics.items():
            instr_code = key[:-9]
            meta_data = self.fsb_instruments.get_meta_data(instr_code)
            if instr_code not in roll_data:
                continue
            if roll_data[instr_code]["priced"] == key[-8:]:
                pos = "priced"
            elif roll_data[instr_code]["fwd"] == key[-8:]:
                pos = "fwd"
            else:
                pos = "-"
            rows.append(
                dict(
                    InstrCode=instr_code,
                    Contract=key,
                    Epic=value,
                    Expiry=expiries[key],
                    In_Hours_Status=in_hours_status[key],
                    LastMod=last_modified[key],
                    Pos=pos,
                    ExpectedMinBet=meta_data.Pointsize,
                    ActualMinBet=min_bet[key],
                    HistorySynced=synced[key],
                )
            )

        return rows

    # FSB mappings_and_expiries
    def fsb_mappings_and_expiries(
        self, table_header="FSB mappings and expiries"
    ) -> table:
        results = pd.DataFrame(self.market_info_data)
        results = results[
            ["Contract", "Epic", "Expiry", "In_Hours_Status", "Pos", "HistorySynced"]
        ]
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
        # for instr in ["CAD_fsb"]:
        for instr in self._list_of_all_instruments():
            epic_history = self.epics.get_epic_history(instr)

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
        for (
            instr_code
        ) in self.futures_prices.get_list_of_instruments_in_multiple_prices():
            contract_priced = self.contracts.get_priced_contract_id(instr_code)
            contract_fwd = self.contracts.get_forward_contract_id(instr_code)

            all_contracts_list = (
                self.contracts.get_all_contract_objects_for_instrument_code(instr_code)
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

    ##### TRADES ######
    def table_of_orders_overview(self):
        broker_orders = self.broker_orders
        history = self.broker_history
        if len(broker_orders) == 0:
            return body_text("No trades")

        broker_orders["pnl"] = "n/a"
        history["profitAndLoss"] = (
            history["profitAndLoss"].replace("[\£,]", "", regex=True).astype(float)
        )

        for permid in broker_orders["broker_permid"].tolist():
            rows = history.loc[history["reference"] == permid]
            pnl = rows["profitAndLoss"].sum()
            if pnl != 0.0:
                broker_orders.loc[broker_orders["broker_permid"] == permid, "pnl"] = pnl

        overview = broker_orders[
            [
                "instrument_code",
                "strategy_name",
                "contract_date",
                "fill_datetime",
                "fill",
                "filled_price",
                "broker_permid",
                "pnl",
            ]
        ]
        overview = overview.sort_values("instrument_code")
        overview_table = table("Broker orders", overview)

        return overview_table


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
