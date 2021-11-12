from syscore.objects import arg_not_supplied

from sysdata.sim.db_fsb_sim_data import dbFsbSimData
from sysdata.data_blob import dataBlob
from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysdata.arctic.arctic_multiple_prices import arcticFuturesMultiplePricesData
from sysdata.arctic.arctic_spotfx_prices import arcticFxPricesData
from sysdata.mongodb.mongo_fsb_instruments import mongoFsbInstrumentData
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData


def get_sim_fsb_data_object_for_production(data=arg_not_supplied) -> dataBlob:
    # Check data has the right elements to do this
    if data is arg_not_supplied:
        data = dataBlob()

    data.add_class_list([arcticFuturesAdjustedPricesData, arcticFuturesMultiplePricesData,
                         arcticFxPricesData, mongoFsbInstrumentData, mongoRollParametersData])

    return dbFsbSimData(data)
