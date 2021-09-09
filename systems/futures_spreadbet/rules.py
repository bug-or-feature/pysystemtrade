"""
Trading rules for Leveraged Trading system
"""
import pandas as pd
from systems.leveraged_trading.volatility import simple_volatility_calc
from sysquant.estimators.vol import robust_vol_calc
from syscore.dateutils import ROOT_BDAYS_INYEAR


def smac(price, fast=16, slow=64):
    """
    Calculate the smac (Simple Moving Average Crossover) trading rule forecast, given a price and SMA speeds fast, slow

    Assumes that 'price' is daily data

    :param price: The price or other series to use (assumed Tx1)
    :type price: pd.Series

    :param fast: Lookback for fast in days
    :type fast: int

    :param slow: Lookback for slow in days
    :type slow: int

    :returns: pd.Series unscaled, uncapped forecast
    """

    fast_sma = price.ffill().rolling(window=fast).mean()
    slow_sma = price.ffill().rolling(window=slow).mean()
    raw_smac = fast_sma - slow_sma

    return raw_smac


def calc_smac_forecast(price, fast=16, slow=64):

    """
    Calculate the smac trading rule forecast, given a price and SMA speeds fast, slow
    """

    price = price.resample("1B").last()

    fast_sma = price.ffill().rolling(window=fast).mean()
    slow_sma = price.ffill().rolling(window=slow).mean()
    raw_smac = fast_sma - slow_sma

    vol = robust_vol_calc(price.diff())

    return raw_smac / vol


def rasmac(price, fast=16, slow=64, lookback=25):
    """
    Calculate the Risk Adjusted Simple Moving Average Crossover (rasmac) trading rule forecast, given price and
    SMA speeds fast, slow, and volatility lookback

    Assumes that 'price' is daily data

    :param price: The price or other series to use (assumed Tx1)
    :type price: pd.Series

    :param fast: Lookback for fast in days
    :type fast: int

    :param slow: Lookback for slow in days
    :type slow: int

    :param volatility_lookback_days
    :type volatility_lookback_days: int

    :returns: pd.Series unscaled, uncapped forecast
    """

    fast_sma = price.ffill().rolling(window=fast).mean()
    slow_sma = price.ffill().rolling(window=slow).mean()
    raw_smac = fast_sma - slow_sma

    # first we get the standard deviation of daily percentage returns
    vol = simple_volatility_calc(price, lookback)

    # multiply by 16 to get an annual figure
    annual_vol = vol * ROOT_BDAYS_INYEAR

    # then instrument risk in price units
    risk_in_price_units = annual_vol * price

    return raw_smac / risk_in_price_units
