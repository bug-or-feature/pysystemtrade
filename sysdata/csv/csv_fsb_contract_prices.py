from syscore.dateutils import Frequency
from syscore.fileutils import get_filename_for_package
from syscore.objects import arg_not_supplied
from syscore.pdutils import pd_readcsv
from sysdata.config.production_config import get_production_config
from sysdata.csv.csv_futures_contract_prices import (
    csvFuturesContractPriceData,
    ConfigCsvFuturesPrices,
)
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices


class CsvFsbContractPriceData(csvFuturesContractPriceData):
    """
    Class to read / write individual futures spreadbet contract price data to and from csv files
    no default datapath supplied as this is not normally used
    """

    def __init__(
        self,
        datapath=arg_not_supplied,
        log=logtoscreen("csvFuturesContractPriceData"),
        config: ConfigCsvFuturesPrices = arg_not_supplied,
    ):

        prod_config = get_production_config()
        ig_path = get_filename_for_package(
            prod_config.get_element_or_missing_data("ig_path")
        )

        pd_config = ConfigCsvFuturesPrices(
            input_date_index_name="Date",
            input_skiprows=0,
            input_skipfooter=0,
            input_date_format="%Y-%m-%dT%H:%M:%S%z",
            input_column_mapping=dict(
                OPEN=dict(BID="Open.bid", ASK="Open.ask"),
                HIGH=dict(BID="High.bid", ASK="High.ask"),
                LOW=dict(BID="Low.bid", ASK="Low.ask"),
                FINAL=dict(BID="Close.bid", ASK="Close.ask"),
                VOLUME="Volume",
            ),
        )

        super().__init__(
            datapath=ig_path,
            log=logtoscreen("csvFuturesContractPriceData"),
            config=pd_config,
        )

    def __repr__(self):
        return f"CsvFsbContractPriceData accessing {self._datapath}"

    def _get_prices_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract
    ) -> futuresContractPrices:
        """
        Read back the prices for a given contract object

        :param contract_object:  futuresContract
        :return: data
        """
        keyname = self._keyname_given_contract_object(futures_contract_object)
        filename = self._filename_given_key_name(keyname)
        config = self.config

        date_format = config.input_date_format
        date_time_column = config.input_date_index_name
        input_column_mapping = config.input_column_mapping
        skiprows = config.input_skiprows
        skipfooter = config.input_skipfooter

        try:
            instrpricedata = pd_readcsv(
                filename,
                date_index_name=date_time_column,
                date_format=date_format,
                input_column_mapping=input_column_mapping,
                skiprows=skiprows,
                skipfooter=skipfooter,
            )
        except OSError:
            log = futures_contract_object.log(self.log)
            log.warning("Can't find adjusted price file %s" % filename)
            return futuresContractPrices.create_empty()

        instrpricedata = instrpricedata.groupby(level=0).last()

        instrpricedata = futuresContractPrices(instrpricedata)

        return instrpricedata

    # def _delete_prices_for_contract_object_with_no_checks_be_careful(self, futures_contract_object: futuresContract):
    #     pass
    #
    # def _get_prices_at_frequency_for_contract_object_no_checking(self, contract_object: futuresContract,
    #                                                              freq: Frequency) -> futuresContractPrices:
    #     pass
