import pandas as pd

from syscore.dateutils import BUSINESS_DAYS_IN_YEAR
from sysproduction.reporting.data.constants import (
    RISK_TARGET_ASSUMED,
    INSTRUMENT_WEIGHT_ASSUMED,
    IDM_ASSUMED,
    MIN_CONTRACTS_HELD,
)

from sysproduction.reporting.data.risk import get_instrument_risk_table

DAILY_RISK_CALC_LOOKBACK = int(BUSINESS_DAYS_IN_YEAR * 2)

USE_DB = True

# only used for reporting purposes


def minimum_capital_table(
    data,
    only_held_instruments=False,
    risk_target=RISK_TARGET_ASSUMED,
    min_contracts_held=MIN_CONTRACTS_HELD,
    idm=IDM_ASSUMED,
    instrument_weight=INSTRUMENT_WEIGHT_ASSUMED,
) -> pd.DataFrame:

    instrument_risk_table = get_instrument_risk_table(
        data, only_held_instruments=only_held_instruments
    )

    min_capital_pd = from_risk_table_to_min_capital(
        instrument_risk_table,
        risk_target=risk_target,
        min_contracts_held=min_contracts_held,
        idm=idm,
        instrument_weight=instrument_weight,
    )

    return min_capital_pd


def from_risk_table_to_min_capital(
    instrument_risk_table: pd.DataFrame,
    risk_target=RISK_TARGET_ASSUMED,
    min_contracts_held=MIN_CONTRACTS_HELD,
    idm=IDM_ASSUMED,
    instrument_weight=INSTRUMENT_WEIGHT_ASSUMED,
) -> pd.DataFrame:

    base_multiplier = instrument_risk_table.point_size_base
    price = instrument_risk_table.price
    ann_perc_stdev = instrument_risk_table.annual_perc_stdev

    # perc stdev is 100% = 100, so divide by 100
    # risk target is 20 = 20, so divide by 100
    # These two effects cancel

    min_bet_min_capital = base_multiplier * price * ann_perc_stdev / risk_target
    min_cap_avg_fc = min_bet_min_capital * min_contracts_held
    min_capital_series = (
        min_contracts_held * min_bet_min_capital / (idm * instrument_weight)
    )

    instrument_list = instrument_risk_table.index
    instrument_count = len(instrument_list)

    min_capital_pd = pd.concat(
        [
            base_multiplier,
            price,
            ann_perc_stdev,
            pd.Series([risk_target] * instrument_count, index=instrument_list),
            min_bet_min_capital,
            pd.Series([min_contracts_held] * instrument_count, index=instrument_list),
            min_cap_avg_fc,
            pd.Series([instrument_weight] * instrument_count, index=instrument_list),
            pd.Series([idm] * instrument_count, index=instrument_list),
            min_capital_series,
        ],
        axis=1,
    )

    min_capital_pd.columns = [
        "min_bet",
        "price",
        "ann_perc_stdev",
        "risk_target",
        "min_cap_min_bet",
        "min_pos_avg_fc",
        "min_cap_avg_fc",
        "instr_weight",
        "IDM",
        "min_cap_portfolio",
    ]

    return min_capital_pd
