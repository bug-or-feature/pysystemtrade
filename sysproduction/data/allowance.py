from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_historic_allowance import MongoHistoricAllowanceData
from sysproduction.data.generic_production_data import productionDataLayerGeneric


class DataHistoricAllowance(productionDataLayerGeneric):

    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_object(MongoHistoricAllowanceData)
        return data

    @property
    def db_historic_allowance_data(self) :
        return self.data.db_historic_allowance

    def set_allowance(self, environment, data_dict):
        return self.db_historic_allowance_data.write_allowance(environment, data_dict)

    def get_allowance(self, environment) -> dict:
        return self.db_historic_allowance_data.get_allowance(environment)


if __name__ == "__main__":

    hist_data = DataHistoricAllowance()
    # expiry = datetime.datetime(2022, 6, 5)
    # data_dict = dict(
    #     Allowance=2800,
    #     Expiry=expiry
    # )
    #hist_data.set_allowance("demo", data_dict)
    result = hist_data.get_allowance("wang")
    print(result)
