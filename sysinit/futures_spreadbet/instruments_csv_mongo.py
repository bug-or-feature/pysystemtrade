"""
Populate a mongo DB collection with futures spreadbet instrument data from CSV
"""

from sysdata.mongodb.mongo_fsb_instruments import mongoFsbInstrumentData
from sysdata.csv.csv_fsb_instrument_data import CsvFsbInstrumentData

INSTRUMENT_CONFIG_PATH = "data.futures_spreadbet.csvconfig"

data_out = mongoFsbInstrumentData(collection_name='ig_fsb_instruments')
data_in = CsvFsbInstrumentData(datapath=INSTRUMENT_CONFIG_PATH)
print(data_in)
instrument_list = data_in.get_list_of_instruments()

if __name__ == "__main__":
    input("Will overwrite existing data are you sure?! CTL-C to abort")
    # modify flags as required
    for instrument_code in instrument_list:
        instrument_object = data_in.get_instrument_data(instrument_code)
        #data_out.delete_instrument_data(instrument_code, are_you_sure=True)
        data_out.add_instrument_data(instrument_object)

        # check
        instrument_added = data_out.get_instrument_data(instrument_code)
        print("Added %s to %s" % (instrument_added.instrument_code, data_out))
