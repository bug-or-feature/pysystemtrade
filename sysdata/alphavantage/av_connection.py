import io

import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry

from syscore.objects import missing_data
from syslogdiag.log import logtoscreen
from sysdata.config.production_config import get_production_config


class avConnection(object):

    """

    Simple web connection to the Alpha Vantage API for free financial data
    Needs an API key, reques one here: https://www.alphavantage.co/support/#api-key
    set the API key in your /private/private_config.yaml file, eg

    alpha_vantage_api_key: 'abc123'

    """

    ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/'

    def __init__(self, log=logtoscreen("Alpha Vantage")):
        self._log = log
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': 'Mozilla/5.0'})
        production_config = get_production_config()
        self._api_key = production_config.get_element_or_missing_data(
            'alpha_vantage_api_key')

    def __repr__(self):
        return "Alpha Vantage API %s" % self.ALPHA_VANTAGE_URL

    @sleep_and_retry # this blocks until safe to execute - should be fine as we only run once a day
    @limits(calls=1, period=12) # Alpha Vantage free API limit is max 5 requests per minute
    def broker_get_daily_fx_data(self, ccy1, ccy2="USD") -> pd.Series:

        """
        Get daily FX prices

        :param ccy1: first currency symbol
        :param ccy2: second currency symbol, defaults to USD
        :return: df: DataFrame
        """

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
            df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y-%m-%d')
            df = df.set_index('timestamp')

            return df

        except Exception as e:
            self._log.error('Error: %s' % e)
            return missing_data
