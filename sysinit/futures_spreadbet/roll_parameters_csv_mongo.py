"""
Populate a mongo DB collection with futures spreadbet roll data from a csv file

*** TODO: check changes in sysinit/futures/roll_parameters_csv_mongo.py ***

"""
import sys
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysdata.csv.csv_roll_parameters import csvRollParametersData, ROLLS_CONFIG_FILE

args = None
if len(sys.argv) > 1:
    args = sys.argv[1]

if args is not None:
    file_name = sys.argv[1]
else:
    file_name = ROLLS_CONFIG_FILE

if __name__ == "__main__":
    input("Will overwrite existing data are you sure?! CTL-C to abort")
    # modify flags as required

    data_out = mongoRollParametersData()
    data_in = csvRollParametersData(datapath="data.futures_spreadbet.csvconfig")

    instrument_list = data_in.get_list_of_instruments()

    for instrument_code in instrument_list:
        instrument_object = data_in.get_roll_parameters(instrument_code)

        data_out.delete_roll_parameters(instrument_code, are_you_sure=True)
        data_out.add_roll_parameters(instrument_code, instrument_object)

        # check
        instrument_added = data_out.get_roll_parameters(instrument_code)
        print("Added %s: %s to %s" % (instrument_code, instrument_added, data_out))
