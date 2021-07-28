from arctic import Arctic
import pymongo
from sysdata.config.production_config import get_production_config

def run_mongo_check():
    config = get_production_config()
    conn = pymongo.MongoClient(config.get_element_or_missing_data('mongo_host'))
    store = Arctic(conn)
    print("Store: %s" % store)

    print("Arctic libs: %s" % store.list_libraries())

if __name__ == "__main__":
    run_mongo_check()



