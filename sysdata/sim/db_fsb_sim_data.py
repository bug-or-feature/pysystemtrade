"""
Get simulation data from mongo and arctic used for futures spreadbet trading

"""

from syscore.objects import arg_not_supplied

from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData
from sysdata.arctic.arctic_spotfx_prices import arcticFxPricesData
from sysdata.mongodb.mongo_fsb_instruments import mongoFsbInstrumentData
from sysdata.data_blob import dataBlob
from sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData
from sysdata.futures.instruments import futuresInstrumentData
from syslogdiag.log_to_screen import logtoscreen


class dbFsbSimData(genericBlobUsingFuturesSimData):
    def __init__(self, data: dataBlob = arg_not_supplied,
                 log=logtoscreen("dbFsbSimData")):

        if data is arg_not_supplied:
            data = dataBlob(log=log,
                            class_list=[
                                arcticFuturesAdjustedPricesData,
                                arcticFuturesMultiplePricesData,
                                arcticFxPricesData,
                                mongoFsbInstrumentData])

        super().__init__(data=data)

    def __repr__(self):
        return f"dbFsbSimData object with {self.get_instrument_list()} instruments"

    @property
    def db_futures_instrument_data(self) -> futuresInstrumentData:
        return self.data.db_fsb_instrument


if __name__ == "__main__":
    import doctest

    doctest.testmod()
