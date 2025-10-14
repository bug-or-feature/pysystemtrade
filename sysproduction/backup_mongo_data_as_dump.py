import os
from sysdata.config.production_config import get_production_config

from sysproduction.data.directories import (
    get_mongo_dump_directory,
    get_mongo_backup_directory,
)

from sysdata.data_blob import dataBlob


def backup_mongo_data_as_dump():
    data = dataBlob(log_name="backup_mongo_data_as_dump")
    backup_object = backupMongo(data)
    backup_object.backup_mongo_data_as_dump()

    return None


class backupMongo(object):
    def __init__(self, data):
        self.data = data

    def backup_mongo_data_as_dump(self):
        data = self.data
        log = data.log
        log.debug("Exporting mongo data")
        dump_mongo_data(data)
        log.debug("Copying data to offsystem backup destination")
        backup_mongo_dump(data)


def dump_mongo_data(data: dataBlob):
    config = data.config
    host = config.get_element_or_arg_not_supplied("mongo_host")
    path = get_mongo_dump_directory()
    if host.startswith("mongodb"):
        source = "uri"
    else:
        source = "host"

    dump_all = config.get_element_or_default("mongo_dump_all", True)
    if dump_all:
        data.log.debug(f"Dumping ALL mongo data to {path} (NOT TESTED IN WINDOWS)")
        os.system(f"mongodump --{source}='{host}' -o={path}")

    else:
        db_name = config.get_element("mongo_db")
        data.log.debug(
            f"Dumping mongo data from {db_name} to {path} (NOT TESTED IN WINDOWS)"
        )
        os.system(f"mongodump --{source}='{host}' -o={path} --db={db_name}")
        # will silently fail if arctic db does not exist
        os.system(f"mongodump --{source}='{host}' -o={path} --db=arctic_{db_name}")

    data.log.debug("Dumped")


def backup_mongo_dump(data):
    source_path = get_mongo_dump_directory()
    destination_path = get_mongo_backup_directory()
    data.log.debug("Copy from %s to %s" % (source_path, destination_path))
    options = get_production_config().get_element("offsystem_backup_options")
    os.system(f"rsync {options} {source_path} {destination_path}")


if __name__ == "__main__":
    backup_mongo_data_as_dump()
