from sysobjects.fsb_contract_prices import FsbContractPrices, FsbContractFinalPrices
from sysdata.csv.csv_fsb_contract_prices import CsvFsbContractPriceData
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysobjects.contracts import futuresContract as fc
from syscore.fileutils import get_filename_for_package


class TestFsbContractPrices:
    def test_csv(self):
        datapath = get_filename_for_package("sysobjects.tests.data")
        data = CsvFsbContractPriceData(
            datapath=datapath,
            config=ConfigCsvFuturesPrices(
                input_date_index_name="Date",
                input_skiprows=0,
                input_skipfooter=0,
                input_date_format="%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        prices = data.get_merged_prices_for_contract_object(
            fc.from_two_strings("GOLD_fsb", "20220600")
        )
        assert type(prices) == FsbContractPrices
        assert prices.at[prices.index[-1], "Open.bid"] == 1859.4

        final = prices.return_final_prices()
        assert type(final) == FsbContractFinalPrices
        assert final.iloc[-1] == 1863.3
