from syscore.constants import arg_not_supplied

from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.rawdata import RawData
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account


def fsb_static_system(
    data=arg_not_supplied,
    config=arg_not_supplied,
    trading_rules=arg_not_supplied,
):
    if data is arg_not_supplied:
        data = build_fsb_db_sim_data()
        # data = build_fsb_csv_sim_data()

    if config is arg_not_supplied:
        config = Config("systems.futures_spreadbet.config.fsb_static_system_v5_2.yaml")
        config.risk_overlay = arg_not_supplied

    rules = Rules(trading_rules)

    system = System(
        [
            Account(),
            Portfolios(),
            PositionSizing(),
            RawData(),
            ForecastCombine(),
            ForecastScaleCap(),
            rules,
        ],
        data,
        config,
    )

    return system


def build_fsb_csv_sim_data():
    return csvFuturesSimData(
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
            csvFxPricesData="data.futures.fx_prices_csv",
            csvFuturesMultiplePricesData="fsb.multiple_prices_csv",
            csvFuturesAdjustedPricesData="fsb.adjusted_prices_csv",
            csvSpreadCostData="fsb.csvconfig",
        )
    )


def build_fsb_db_sim_data():
    return dbFuturesSimData(
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
            csvSpreadCostData="fsb.csvconfig",
        )
    )


# system = fsb_dynamic_system()
# print(system.accounts.portfolio().percent.stats())

# Yes those are before buffering and the algo

# After buffering (static system):
# system.accounts.get_buffered_position( instrument_code, roundpositions=True)
# After greedy algo (dynamic system):
# system.optimisedPositions.get_optimised_position_df()

# Note in production I don't do this - I run the buffering and or greedy algo on the unrounded positions,
# taking into account my actual live current positions, rather than what the backtest thought it had on yesterday

#
