from syscore.dateutils import MIXED_FREQ, Frequency
from syscore.objects import arg_not_supplied
from syscore.pdutils import pd_readcsv
from sysdata.csv.csv_futures_contract_prices import (
    csvFuturesContractPriceData,
    ConfigCsvFuturesPrices,
)
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.contracts import futuresContract
from sysobjects.fsb_contract_prices import FsbContractPrices, PRICE_DATA_COLUMNS


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

    def _get_merged_prices_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract
    ) -> FsbContractPrices:
        """
        Read back the prices for a given contract object

        :param futures_contract_object:  futuresContract
        :return: data
        """

        return self._get_prices_at_frequency_for_contract_object_no_checking(
            futures_contract_object, MIXED_FREQ
        )

    def _get_prices_at_frequency_for_contract_object_no_checking(
        self, futures_contract_object: futuresContract, frequency: Frequency
    ) -> FsbContractPrices:

        keyname = self._keyname_given_contract_object_and_freq(
            futures_contract_object, frequency=frequency
        )
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

        instrpricedata = FsbContractPrices(instrpricedata)

        return instrpricedata

    def _write_merged_prices_for_contract_object_no_checking(
        self,
        futures_contract_object: futuresContract,
        futures_price_data: FsbContractPrices,
    ):
        """
        Write prices
        CHECK prices are overriden on second write

        :param futures_contract_object: futuresContract
        :param futures_price_data: futuresContractPriceData
        :return: None
        """
        self._write_prices_at_frequency_for_contract_object_no_checking(
            futures_contract_object=futures_contract_object,
            futures_price_data=futures_price_data,
            frequency=MIXED_FREQ,
        )

    def _write_prices_at_frequency_for_contract_object_no_checking(
        self,
        futures_contract_object: futuresContract,
        futures_price_data: FsbContractPrices,
        frequency: Frequency,
    ):

        keyname = self._keyname_given_contract_object_and_freq(
            futures_contract_object, frequency=frequency
        )
        filename = self._filename_given_key_name(keyname)
        futures_price_data.to_csv(
            filename, index_label=self.config.input_date_index_name
        )
