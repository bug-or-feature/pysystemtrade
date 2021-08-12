import pandas as pd


def simple_volatility_calc(series: pd.Series, days: int = 25) -> pd.Series:
    """
    Simple volatility calculation, assuming daily series of prices

    :param series: price data
    :type series: pd.Series

    :param days: Number of days in lookback (default 25)
    :type days: int

    :returns: pd.Series standard deviation of percentage daily returns
    """

    price = series.resample("1B").ffill()
    daily_returns = price.diff()
    vol = daily_returns.ffill().rolling(window=days).std()

    return vol
