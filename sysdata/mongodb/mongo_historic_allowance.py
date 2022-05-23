from syscore.objects import arg_not_supplied, missing_data
from sysdata.mongodb.mongo_generic import mongoDataWithSingleKey
from syslogdiag.log_to_screen import logtoscreen

HA_COLLECTION = "historic_allowance"


class MongoHistoricAllowanceData:

    """
    Read and write data class for historic data allowance
    """

    def __init__(
        self,
        mongo_db=arg_not_supplied,
        log=logtoscreen("mongoHistoricAllowanceData"),
    ):

        self._mongo_data = mongoDataWithSingleKey(
            HA_COLLECTION, "Environment", mongo_db
        )
        self._log = log

    @property
    def log(self):
        return self._log

    @property
    def mongo_data(self):
        return self._mongo_data

    def _repr__(self):
        return f"Historic allowance data, mongodb {str(self.mongo_data)}"

    @property
    def _collection_name(self):
        return HA_COLLECTION

    def get_allowance(self, environment: str) -> dict:
        data_dict = self.mongo_data.get_result_dict_for_key(environment)
        if data_dict is missing_data:
            return dict()

        return data_dict

    def write_allowance(self, environment: str, data_dict: dict):
        self.mongo_data.add_data(
            environment,
            data_dict,
            allow_overwrite=True
        )
