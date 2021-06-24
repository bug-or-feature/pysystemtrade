import pandas as pd

from sysdata.alphavantage.av_connection import avConnection


class TestAlphaVantage:

    def test_aud_daily(self):
        av = avConnection()
        prices = av.broker_get_daily_fx_data('AUD')

        assert isinstance(prices, pd.DataFrame)
        #assert prices.shape[0] == 640
        assert prices.shape[1] == 4

        print(f"\n{prices}")