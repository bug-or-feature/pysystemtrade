from sysobjects.contract_dates_and_expiries import expiryDate
import pytest


class TestContractDatesAndExpiries:
    def test_default_format(self):
        the_date = expiryDate.from_str("20210918")
        assert the_date.as_tuple()[0] == 2021
        assert the_date.as_tuple()[1] == 9
        assert the_date.as_tuple()[2] == 18

    def test_custom_format(self):
        the_date = expiryDate.from_str("2021-09-18", "%Y-%m-%d")
        assert the_date.as_tuple()[0] == 2021
        assert the_date.as_tuple()[1] == 9
        assert the_date.as_tuple()[2] == 18

    def test_empty(self):
        with pytest.raises(Exception):
            expiryDate.from_str("")
