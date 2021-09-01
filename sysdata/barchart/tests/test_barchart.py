from sysdata.barchart.bc_connection import bcConnection
from sysdata.barchart.bc_instruments_data import BarchartFuturesInstrumentData
from sysdata.barchart.bc_futures_contracts_data import BarchartFuturesContractData
from sysdata.barchart.bc_futures_contract_price_data import BarchartFuturesContractPriceData

from sysobjects.contracts import futuresContract as fc
from syscore.dateutils import Frequency
from syscore.objects import missing_data

import pandas as pd
import pytest
import datetime


class TestBarchart:

    def test_gold_daily(self):
        bc = bcConnection()
        prices = bc.get_historical_futures_data_for_contract(fc('GOLD', '20210600'))

        assert isinstance(prices, pd.DataFrame)
        assert prices.shape[0] == 640
        assert prices.shape[1] == 5

        print(f"\n{prices}")

    def test_gold_hourly(self):
        bc = bcConnection()
        prices = bc.get_historical_futures_data_for_contract(
            fc('GOLD', '20210600'), bar_freq=Frequency.Hour)

        assert isinstance(prices, pd.DataFrame)
        assert prices.shape[0] == 640
        assert prices.shape[1] == 5

        print(f"\n{prices}")

    def test_gold_second(self):
        bc = bcConnection()
        result = bc.get_historical_futures_data_for_contract(fc('GOLD', '20210600'), bar_freq=Frequency.Second)
        assert result == missing_data

    def test_freq_names(self):
        for freq in Frequency:
            print(f"member= {freq}, name={freq.name}, value={freq.value}")

    def test_contract_ids(self):

        bc = bcConnection()

        assert bc.get_barchart_id(fc('GOLD', '20210600')) == "GCM21"

        assert bc.get_barchart_id(fc('EDOLLAR', '20200300')) == "GEH20"

        assert bc.get_barchart_id(fc('AEX', '20190900')) == "AEU19"

        assert bc.get_barchart_id(fc('GBP', '20181200')) == "B6Z18"

        assert bc.get_barchart_id(fc('LEANHOG', '20000200')) == "HEG00"

        assert bc.get_barchart_id(fc('PLAT', '20020400')) == "PLJ02"

        with pytest.raises(Exception):
            bc.get_barchart_id(fc('BLAH', '20210600'))

        with pytest.raises(Exception):
           bc.get_barchart_id(fc('AUD', '20201300'))

    # def test_bc_config(self):
    #     config = read_bc_config_from_file()
    #     assert config

    def test_config(self):
        bc_futures_instr = BarchartFuturesInstrumentData()

        assert len(bc_futures_instr.get_list_of_instruments()) == 35

        assert bc_futures_instr.get_brokers_instrument_code('GOLD') == 'GC'
        assert bc_futures_instr.get_brokers_instrument_code('COPPER') == 'HG'
        assert bc_futures_instr.get_brokers_instrument_code('EUROSTX') == 'FX'
        assert bc_futures_instr.get_brokers_instrument_code('PALLAD') == 'PA'
        with pytest.raises(Exception):
            bc_futures_instr.get_brokers_instrument_code('ABC')

        assert bc_futures_instr.get_instrument_code_from_broker_code('LE') == 'LIVECOW'
        assert bc_futures_instr.get_instrument_code_from_broker_code('PL') == 'PLAT'
        assert bc_futures_instr.get_instrument_code_from_broker_code('VI') == 'VIX'
        assert bc_futures_instr.get_instrument_code_from_broker_code('ZW') == 'WHEAT'
        with pytest.raises(Exception):
            bc_futures_instr.get_instrument_code_from_broker_code('XX')

        assert bc_futures_instr.get_bc_futures_instrument('CORN').bc_data.currency == ''
        assert bc_futures_instr.get_bc_futures_instrument('AEX').bc_data.currency == 'EUR'

    def test_expiry_dates(self):

        bc = bcConnection()
        data = BarchartFuturesContractData(bc)

        expiry = data.get_actual_expiry_date_for_single_contract(fc('GOLD', '20210600'))
        assert expiry == datetime.datetime(2021, 6, 28)

        expiry = data.get_actual_expiry_date_for_single_contract(fc('GBP', '20201200'))
        assert expiry == datetime.datetime(2020, 12, 14)

        expiry = data.get_actual_expiry_date_for_single_contract(fc('AUD', '20100900'))
        assert expiry == datetime.datetime(2010, 9, 13)

        # too old
        with pytest.raises(Exception):
            data.get_actual_expiry_date_for_single_contract(fc('EUR', '19900300'))

        # too new
        expiry = data.get_actual_expiry_date_for_single_contract(fc('PLAT', '21000300'))
        assert expiry == datetime.datetime(2100, 3, 1)

    def test_price_data(self):
        prices = BarchartFuturesContractPriceData()
        assert prices.has_data_for_contract(fc('GOLD', '20210600'))

        instr_list = prices.get_list_of_instrument_codes_with_price_data()
        assert(len(instr_list) == 35)