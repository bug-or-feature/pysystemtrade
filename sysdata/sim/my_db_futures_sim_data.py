"""
Combination of my Barchart futures data with the default original futures instrument config from CSV.
Useful comparing default system behaviour with my customisations

"""

from syscore.objects import arg_not_supplied

from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData
from sysdata.arctic.arctic_spotfx_prices import arcticFxPricesData
#from sysdata.mongodb.mongo_futures_instruments import mongoFuturesInstrumentData
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from sysdata.data_blob import dataBlob
from sysdata.sim.futures_sim_data_with_data_blob import genericBlobUsingFuturesSimData

from syslogdiag.log_to_screen import logtoscreen


class MyDbFuturesSimData(genericBlobUsingFuturesSimData):
    def __init__(self, data: dataBlob = arg_not_supplied,
                 log =logtoscreen("myDbFuturesSimData")):

        if data is arg_not_supplied:
            data = dataBlob(
                log=log,
                class_list=[
                    arcticFuturesAdjustedPricesData,
                    arcticFuturesMultiplePricesData,
                    arcticFxPricesData,
                    csvFuturesInstrumentData
                ]
            )

        super().__init__(data=data)

    def __repr__(self):
        return "dbFuturesSimData object with %d instruments" % len(
            self.get_instrument_list())


if __name__ == "__main__":
    import doctest

    doctest.testmod()
