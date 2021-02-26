import io

import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry

from syscore.objects import missing_data
from syslogdiag.log import logtoscreen
from sysdata.config.private_config import get_private_then_default_key_value

# TODO shorten names
# TODO comments
# TODO need for API key
class avConnection(object):

    ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/'

    def __init__(self, log=logtoscreen("AlphaVantage")):
        self._log = log
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self._api_key = get_private_then_default_key_value('alpha_vantage_api_key')

    def __repr__(self):
        return "Alpha Vantage endpoint: %s" % self.ALPHA_VANTAGE_URL

    @sleep_and_retry # this blocks until safe to execute - should be fine as we only run once a day
    @limits(calls=1, period=12) # Alpha Vantage free API limit is max 5 requests per minute
    def broker_get_daily_fx_data(self, ccy1, ccy2="USD", bar_freq="D") -> pd.Series:

        try:
            payload = {
                'function': 'FX_DAILY',
                'from_symbol': ccy1,
                'to_symbol': 'USD',
                'apikey': self._api_key,
                'datatype': 'csv'
            }

            fx_url = self.ALPHA_VANTAGE_URL + 'query'
            fx_resp = self._session.get(fx_url, params=payload)
            self._log.msg('GET %s %s/%s, %s' % (fx_url, ccy1, ccy2, fx_resp.status_code))

            # read response into dataframe
            iostr = io.StringIO(fx_resp.text)
            df = pd.read_csv(iostr)

            # convert first column to proper date time, and set as index
            df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y-%m-%d') # , format='%d%b%Y:%H:%M:%S.%f'
            df = df.set_index('timestamp')

            return df

        except Exception as e:
            self._log.error('Error: %s' % e)
            return missing_data
