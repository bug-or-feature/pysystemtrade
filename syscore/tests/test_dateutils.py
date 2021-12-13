"""
Created on 27 Nov 2015

@author: rob
"""
import pandas as pd
from syscore.dateutils import get_datetime_from_datestring
import pytest


class TestDateUtils:
    def test_get_datetime_from_datestring(self):

        result = get_datetime_from_datestring("201503")
        assert result.year == 2015
        assert result.month == 3
        assert result.day == 1

        result = get_datetime_from_datestring("20150300")
        assert result.year == 2015
        assert result.month == 3
        assert result.day == 1

        result = get_datetime_from_datestring("20150305")
        assert result.year == 2015
        assert result.month == 3
        assert result.day == 5

        with pytest.raises(Exception):
            get_datetime_from_datestring("2015031")

        with pytest.raises(Exception):
            get_datetime_from_datestring("2015013")

    def test_data(self):
        x = pd.DataFrame(
            dict(
                CARRY_CONTRACT=[
                    "",
                    "201501",
                    "",
                    "201501",
                    "20150101",
                    "20150101",
                    "201501",
                ],
                PRICE_CONTRACT=[
                    "",
                    "",
                    "201504",
                    "201504",
                    "201504",
                    "20150115",
                    "201406",
                ],
            )
        )

        return x
