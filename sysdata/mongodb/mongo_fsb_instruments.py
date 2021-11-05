from syscore.objects import arg_not_supplied, missing_data

from sysdata.futures.instruments import futuresInstrumentData
from sysobjects.spreadbet_instruments import FuturesSpreadbetWithMetaData
from sysdata.mongodb.mongo_generic import mongoDataWithSingleKey
from syslogdiag.log_to_screen import logtoscreen

INSTRUMENT_COLLECTION = "ig_fsb_instruments"


class mongoFsbInstrumentData(futuresInstrumentData):

    """
    Read and write data class to get futures spreadbet instrument data
    """

    def __init__(self, mongo_db=arg_not_supplied, log=logtoscreen(
            "mongoFsbInstrumentData"), collection_name=INSTRUMENT_COLLECTION):

        super().__init__(log=log)
        self._mongo_data = mongoDataWithSingleKey(collection_name, "instrument_code", mongo_db=mongo_db)

    def __repr__(self):
        return "mongoFsbInstrumentData %s" % str(self.mongo_data)

    @property
    def mongo_data(self):
        return self._mongo_data

    def get_list_of_instruments(self):
        return self.mongo_data.get_list_of_keys()

    def _get_instrument_data_without_checking(self, instrument_code):

        result_dict = self.mongo_data.get_result_dict_for_key(instrument_code)
        if result_dict is missing_data:
            # shouldn't happen...
            raise Exception("Data for %s gone AWOL" % instrument_code)

        instrument_object = FuturesSpreadbetWithMetaData.from_dict(result_dict)

        return instrument_object

    def _delete_instrument_data_without_any_warning_be_careful(
            self, instrument_code):
        self.mongo_data.delete_data_without_any_warning(instrument_code)

    def _add_instrument_data_without_checking_for_existing_entry(
        self, instrument_object
    ):
        instrument_object_dict = instrument_object.as_dict()
        instrument_code = instrument_object_dict.pop("instrument_code")
        self.mongo_data.add_data(instrument_code, instrument_object_dict, allow_overwrite=True)
