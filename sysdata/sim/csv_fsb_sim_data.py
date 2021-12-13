"""
Get simulation data from .csv files used for futures spreadbet trading
"""

from syscore.objects import arg_not_supplied
from sysdata.csv.csv_multiple_prices import csvFuturesMultiplePricesData
from sysdata.csv.csv_adjusted_prices import csvFuturesAdjustedPricesData
from sysdata.csv.csv_spot_fx import csvFxPricesData
from sysdata.csv.csv_fsb_instrument_data import CsvFsbInstrumentData
from sysdata.futures.instruments import futuresInstrumentData
from sysdata.data_blob import dataBlob
from sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData
from syslogdiag.log_to_screen import logtoscreen


class csvFsbSimData(genericBlobUsingFuturesSimData):
    """
    Uses default paths for .csv files, pass in dict of csv_data_paths to modify
    """

    def __init__(
        self, csv_data_paths=arg_not_supplied, log=logtoscreen("csvFsbSimData")
    ):
        data = dataBlob(
            log=log,
            csv_data_paths=csv_data_paths,
            class_list=[
                csvFuturesAdjustedPricesData,
                csvFuturesMultiplePricesData,
                CsvFsbInstrumentData,
                csvFxPricesData,
            ],
        )

        super().__init__(data=data)

    def __repr__(self):
        return f"csvFsbSimData object with {self.get_instrument_list()} instruments"

    @property
    def db_futures_instrument_data(self) -> futuresInstrumentData:
        return self.data.db_fsb_instrument
