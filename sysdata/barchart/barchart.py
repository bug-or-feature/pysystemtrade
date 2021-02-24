import io
import re
import urllib.parse
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup as scraper

from syscore.dateutils import contract_month_from_number
from sysdata.barchart.barchart_instruments_data import barchartFuturesInstrumentData
from syslogdiag.log import logger, logtoscreen
from sysobjects.contracts import futuresContract

BARCHART_URL = 'https://www.barchart.com/'

freq_mapping = {
    'H': '60',
    '15M': '15',
    '5M': '5',
    'M': '1'
}


class barchartConnection(object):


    def __init__(self, log=logtoscreen("Barchart")):
        self._log = log
        # start HTTP session
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def __repr__(self):
        return "Barchart instance: %s" % BARCHART_URL

    @property
    def log(self):
        return self._log

    @property
    def barchart_futures_instrument_data(self) -> barchartFuturesInstrumentData:
        return barchartFuturesInstrumentData(log = self.log)


    def has_data_for_contract(self, futures_contract: futuresContract) -> bool:

        try:
            contract_id = self.get_barchart_id(futures_contract)
            #print(contract_id)
            resp = self._get_overview(contract_id)
            return resp.status_code == 200

        except Exception as e:
            self._log.error('Error: %s' % e)
            return False

    def get_expiry_date(self, futures_contract: futuresContract):
        try:
            contract_id = self.get_barchart_id(futures_contract)
            #print(contract_id)
            resp = self._get_overview(contract_id)
            if resp.status_code == 200:
                overview_soup = scraper(resp.text, 'html.parser')
                table = overview_soup.find(name='div', attrs={'class': 'commodity-profile'})
                label = table.find(name='div', string='Expiration Date')
                expiry_date_raw = label.next_sibling.next_sibling # whitespace counts
                match = re.search('(\d{2}/\d{2}/\d{2})', expiry_date_raw.text) # compile pattern?
                expiry_date_clean = match.group()
                return expiry_date_clean

        except Exception as e:
            self._log.error('Error: %s' % e)
            return None


    def get_historical_futures_data_for_contract(
            self, contract_object: futuresContract, bar_freq="D") -> pd.DataFrame:

        """
        Get historical daily data

        :param contract_object: contract (where instrument has barchart metadata)
        :param freq: str; one of D, H, 5M, M, 10S, S
        :return: futuresContractPriceData
        """

        if bar_freq == "S" or bar_freq == "10S":
            raise NotImplementedError("Barchart supported data frequencies: 'D','H','15M','5M','M'")

        instr_symbol = self.get_barchart_id(contract_object)
        if instr_symbol is None:
            log.warn("Can't convert contract ID %s" % str(contract_object))
            return missing_data

        # GET the futures quote chart page, scrape to get XSRF token
        # https://www.barchart.com/futures/quotes/GCM21/interactive-chart
        chart_url = BARCHART_URL + f"futures/quotes/{instr_symbol}/interactive-chart"
        chart_resp = self._session.get(chart_url)
        soup = scraper(chart_resp.text, 'html.parser')
        xsrf = urllib.parse.unquote(chart_resp.cookies['XSRF-TOKEN'])
        #print('xsrf: %s' % xsrf)

        headers = {
            'content-type': 'text/plain; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': chart_url,
            'x-xsrf-token': xsrf
        }

        payload = {
            'symbol': instr_symbol,
            'maxrecords': '640', # TODO enough?
            'volume': 'contract',
            'order': 'asc',
            'dividends': 'false',
            'backadjust': 'false',
            'days to expiration': '1',
            'contractroll': 'combined'
        }

        if bar_freq == "D":
            data_url = BARCHART_URL + 'proxies/timeseries/queryeod.ashx'
            payload['data'] = 'daily'
        else:
            data_url = BARCHART_URL + 'proxies/timeseries/queryminutes.ashx'
            payload['interval'] = freq_mapping[bar_freq]

        # get prices for instrument from BC internal API
        prices_resp = self._session.get(data_url, headers=headers, params=payload)
        print('GET %s %s, %s' % (data_url, instr_symbol, prices_resp.status_code))
        #print('resp_data: %s' % prices_resp.text)
        iostr = io.StringIO(prices_resp.text)

        df = pd.read_csv(iostr, header=None)
        #print(df)

        return df
        #return self._raw_barchart_data_to_df(df, self.log)

    def _raw_barchart_data_to_df(self, price_data_raw: pd.DataFrame, log:logger, bar_freq="D") -> pd.DataFrame:

        if price_data_raw is None:
            log.warn("No historical price data from Barchart")
            return missing_data

        date_format = "%Y-%m-%d"
        date_col = 1

        if bar_freq == "D":
            price_data_as_df = price_data_raw.iloc[:, [2,3,4,5,7]]
        else:
            price_data_as_df = price_data_raw.iloc[:, [2,3,4,5,6]]
            date_format = "%Y-%m-%d %H:%M"
            date_col = 0

        price_data_as_df.columns = ["OPEN", "HIGH", "LOW", "FINAL", "VOLUME"]

        date_index = [
            pd.to_datetime(price_row, format=date_format)
            for price_row in price_data_raw[price_data_raw.columns[date_col]]
        ]
        price_data_as_df.index = date_index
        price_data_as_df.index.name='index'

        print(price_data_as_df)

        return price_data_as_df

    # TODO cache page results?
    def _get_overview(self, contract_id):

        # GET the futures overview page
        # https://www.barchart.com/futures/quotes/B6M21/overview
        url = BARCHART_URL + "futures/quotes/%s/overview" % contract_id
        resp = self._session.get(url)
        self._log.msg(f"GET {url}, response {resp.status_code}")
        return resp


    def get_barchart_id(self, futures_contract: futuresContract) -> str:
        date_obj = datetime.strptime(futures_contract.contract_date.date_str, '%Y%m00')
        bc_symbol = self.barchart_futures_instrument_data.get_brokers_instrument_code(futures_contract.instrument_code)
        symbol = "%s%s%s" % (bc_symbol,
                             contract_month_from_number(int(date_obj.strftime('%m'))),
                             date_obj.strftime('%y'))

        return symbol


if __name__ == "__main__":
    #print(convert_contract_id("KOSPI", "20210100"))

    bc = barchartConnection()
    #result = bc.get_barchart_id(futuresContract('GOLD', '20210600'))
    #result = bc.get_barchart_id(futuresContract('KOSPI', '20210600'))
    #result = bc.has_data_for_contract("KOSPI", "20210100")
    #result = bc.get_expiry_date(futuresContract('GOLD', '20210600'))

    #result = bc.get_historical_futures_data_for_contract(futuresContract('GOLD', '20210600'), bar_freq='D')
    df = bc.get_historical_futures_data_for_contract(futuresContract('GOLD', '20210600'), bar_freq='M') # 'D','H','15M','5M','M'

    #df = pd.read_csv("/Users/ageach/Dev/work/pysystemtrade3/sysdata/barchart/tests/daily_sample.csv", header=None)
    #df = pd.read_csv("/Users/ageach/Dev/work/pysystemtrade3/sysdata/barchart/tests/hourly_sample.csv", header=None)
    #df = pd.read_csv("/Users/ageach/Dev/work/pysystemtrade3/sysdata/barchart/tests/hourly_sample.csv", header=None)

    result = bc._raw_barchart_data_to_df(df, bc.log, bar_freq='M')

    print(result)
