from sysdata.barchart.bc_connection import bcConnection
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

    def test_expiry(self):
        bc = bcConnection()
        expiry = bc.get_expiry_date_for_symbol("GCG24")
        assert isinstance(expiry, str)
        assert expiry == "02/27/24"
        print(f"{expiry=}")

    def test_exchange(self):
        bc = bcConnection()
        exchange = bc.get_exchange_for_code("GC")
        assert exchange == "COMEX"
        print(f"{exchange=}")
