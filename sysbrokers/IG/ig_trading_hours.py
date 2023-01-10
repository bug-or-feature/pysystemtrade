import datetime


from sysdata.config.private_directory import get_full_path_for_private_config
from sysobjects.production.trading_hours.trading_hours import (
    tradingHours,
    listOfTradingHours,
)
from syscore.fileutils import does_file_exist
from sysdata.config.production_config import get_production_config
from sysdata.production.trading_hours import read_trading_hours

IB_CONFIG_TRADING_HOURS_FILE = "sysbrokers.IG.ig_config_trading_hours.yaml"
PRIVATE_CONFIG_TRADING_HOURS_FILE = get_full_path_for_private_config(
    "private_config_trading_hours.yaml"
)


def get_saved_trading_hours():
    if does_file_exist(PRIVATE_CONFIG_TRADING_HOURS_FILE):
        return read_trading_hours(PRIVATE_CONFIG_TRADING_HOURS_FILE)
    else:
        return read_trading_hours(IB_CONFIG_TRADING_HOURS_FILE)
