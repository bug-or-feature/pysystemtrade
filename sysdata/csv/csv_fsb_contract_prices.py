from syscore.dateutils import Frequency
from syscore.objects import arg_not_supplied
from syscore.pdutils import pd_readcsv
from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData, ConfigCsvFuturesPrices
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contracts import futuresContract
from sysobjects.fsb_contract_prices import FsbContractPrices, PRICE_DATA_COLUMNS
from sysobjects.futures_per_contract_prices import futuresContractPrices


class CsvFsbContractPriceData(csvFuturesContractPriceData):
    """
    Class to read / write individual FSB contract price data to and from csv files
    """

    def __init__(
        self,
        datapath=arg_not_supplied,
        log=logtoscreen("CsvFsbContractPriceData"),
        config: ConfigCsvFuturesPrices = arg_not_supplied,
    ):
        super().__init__(log=log, datapath=datapath, config=config)

    def __repr__(self):
        return "CsvFsbContractPriceData accessing %s" % self._datapath

    def _get_prices_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract
    ) -> FsbContractPrices:
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
        multiplier = config.apply_multiplier
        inverse = config.apply_inverse

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
            log.warn("Can't find FSB price file %s" % filename)
            return FsbContractPrices.create_empty()

        instrpricedata = instrpricedata.groupby(level=0).last()
        for col_name in PRICE_DATA_COLUMNS:
            column_series = instrpricedata[col_name]
            if inverse:
                column_series = 1 / column_series
            column_series *= multiplier
            instrpricedata[col_name] = column_series.round(2)

        instrpricedata = FsbContractPrices(instrpricedata)

        return instrpricedata

    def _delete_prices_for_contract_object_with_no_checks_be_careful(
            self,
            futures_contract_object: futuresContract
    ):
        pass

    def _get_prices_at_frequency_for_contract_object_no_checking(
            self,
            contract_object: futuresContract,
            freq: Frequency
    ) -> futuresContractPrices:
        pass
