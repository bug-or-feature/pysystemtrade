import datetime
from sysobjects.production.process_control import controlProcess
from sysdata.production.process_control_data import controlProcessData
from syscore.constants import arg_not_supplied
from syscore.dateutils import (
    ISO_DATE_FORMAT,
    date_as_short_pattern_or_question_if_missing,
)
from sysdata.mongodb.mongo_generic import mongoDataWithSingleKey
from syslogdiag.log_to_screen import logtoscreen

PROCESS_CONTROL_COLLECTION = "process_control"
PROCESS_CONTROL_KEY = "process_name"


class mongoControlProcessData(controlProcessData):
    """
    Read and write data class to get process control data


    """

    def __init__(
        self, mongo_db=arg_not_supplied, log=logtoscreen("mongoControlProcessData")
    ):

        super().__init__(log=log)

        self._mongo_data = mongoDataWithSingleKey(
            PROCESS_CONTROL_COLLECTION, PROCESS_CONTROL_KEY, mongo_db=mongo_db
        )

    @property
    def mongo_data(self):
        return self._mongo_data

    def __repr__(self):
        return "Data connection for process control, mongodb %s" % str(self.mongo_data)

    def get_list_of_process_names(self):
        return self.mongo_data.get_list_of_keys()

    def _get_control_for_process_name_without_default(self, process_name):
        result_dict = self.mongo_data.get_result_dict_for_key_without_key_value(
            process_name
        )

        control_object = controlProcess.from_dict(result_dict)

        return control_object

    def _modify_existing_control_for_process_name(
        self, process_name, new_control_object
    ):
        self._log_status_change(process_name, new_control_object)
        self.mongo_data.add_data(
            process_name, new_control_object.as_dict(), allow_overwrite=True
        )

    def _add_control_for_process_name(self, process_name, new_control_object):
        self.mongo_data.add_data(
            process_name, new_control_object.as_dict(), allow_overwrite=False
        )

    def delete_control_for_process_name(self, process_name):
        self.mongo_data.delete_data_without_any_warning(process_name)

    def _log_status_change(self, process_name, new_control: controlProcess):
        existing_control = self._get_control_for_process_name_without_default(
            process_name
        )
        if not existing_control.has_same_status(new_control):
            msg = "Status of '%s' changed from '%s (%s)' to '%s (%s)' at %s" % (
                process_name,
                existing_control.running_mode_str,
                existing_control.status,
                new_control.running_mode_str,
                new_control.status,
                date_as_short_pattern_or_question_if_missing(
                    datetime.datetime.now(), date_format=ISO_DATE_FORMAT
                ),
            )
            self.log.terse(msg, sysmon="status_change")
