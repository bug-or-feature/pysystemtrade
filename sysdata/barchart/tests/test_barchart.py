from sysdata.barchart.bc_connection import bcConnection
from sysdata.barchart.bc_instruments_data import BarchartFuturesInstrumentData
from sysdata.barchart.bc_futures_contract_price_data import (
    BarchartFuturesContractPriceData,
)

from sysobjects.contracts import futuresContract as fc
from syscore.dateutils import Frequency

import pandas as pd
import pytest


class TestBarchart:
    def test_gold_daily(self):
        bc = bcConnection()
        prices = bc.get_historical_futures_data_for_contract("GCM16")

        assert isinstance(prices, pd.DataFrame)
        assert prices.shape[0] == 640
        assert prices.shape[1] == 5

        print(f"\n{prices}")

    def test_gold_hourly(self):
        bc = bcConnection()
        prices = bc.get_historical_futures_data_for_contract(
            "GCM16", bar_freq=Frequency.Hour
        )

        assert isinstance(prices, pd.DataFrame)
        assert prices.shape[0] == 640
        assert prices.shape[1] == 5

        print(f"\n{prices}")

    def test_gold_second(self):
        bc = bcConnection()
        with pytest.raises(NotImplementedError):
            bc.get_historical_futures_data_for_contract(
                "GCM16", bar_freq=Frequency.Second
            )

    def test_freq_names(self):
        for freq in Frequency:
            print(f"member= {freq}, name={freq.name}, value={freq.value}")

    def test_config(self):
        bc_futures_instr = BarchartFuturesInstrumentData()

        assert bc_futures_instr.get_brokers_instrument_code("GOLD") == "GC"
        assert bc_futures_instr.get_brokers_instrument_code("GOLD_fsb") == "GC"
        assert bc_futures_instr.get_brokers_instrument_code("COPPER") == "HG"
        assert bc_futures_instr.get_brokers_instrument_code("EUROSTX") == "FX"
        assert bc_futures_instr.get_brokers_instrument_code("EUROSTX_fsb") == "FX"
        assert bc_futures_instr.get_brokers_instrument_code("PALLAD") == "PA"
        with pytest.raises(Exception):
            bc_futures_instr.get_brokers_instrument_code("ABC")

        assert bc_futures_instr.get_instrument_code_from_broker_code("LE") == "LIVECOW"
        assert bc_futures_instr.get_instrument_code_from_broker_code("PL") == "PLAT"
        assert bc_futures_instr.get_instrument_code_from_broker_code("VI") == "VIX"
        assert bc_futures_instr.get_instrument_code_from_broker_code("ZW") == "WHEAT"
        with pytest.raises(Exception):
            bc_futures_instr.get_instrument_code_from_broker_code("XX")

        assert bc_futures_instr.get_bc_futures_instrument("CORN").bc_data.currency == ""
        assert (
            bc_futures_instr.get_bc_futures_instrument("AEX").bc_data.currency == "EUR"
        )

    @pytest.mark.skip
    def test_price_data(self):
        prices = BarchartFuturesContractPriceData()
        assert prices.has_data_for_contract(fc.from_two_strings("GOLD", "20210600"))

        instr_list = prices.get_list_of_instrument_codes_with_price_data()
        print(instr_list)
        assert len(instr_list) == 71
