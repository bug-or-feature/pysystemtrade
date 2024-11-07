from syscore.constants import arg_not_supplied

from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine

from systems.forecast_scale_cap import ForecastScaleCap
from systems.provided.attenuate_vol.vol_attenuation_forecast_scale_cap import (
    volAttenForecastScaleCap,
)

# from systems.rawdata import RawData
from systems.provided.rob_system.rawdata import myFuturesRawData
from systems.positionsizing import PositionSizing
from systems.portfolio_fsb import FsbPortfolios
from systems.accounts.accounts_stage import Account
from systems.system_utils import build_fsb_csv_sim_data, build_fsb_db_sim_data


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
            FsbPortfolios(),
            PositionSizing(),
            myFuturesRawData(),
            ForecastCombine(),
            ForecastScaleCap(),
            rules,
        ],
        data,
        config,
    )

    return system
