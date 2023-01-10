from jinja2 import Environment, select_autoescape, PackageLoader
from copy import copy

from sysdata.data_blob import dataBlob
from sysdata.config.production_config import get_production_config

from syscore.fileutils import get_filename_for_package
from sysproduction.data.control_process import dataControlProcess
from sysproduction.data.control_process import diagControlProcess
from sysproduction.data.logs import diagLogs
from syscontrol.list_running_pids import describe_trading_server_login_data


def monitor():
    with dataBlob(log_name="system-monitor") as data:
        data.log.msg("Starting process monitor...")
        process_observatory = processMonitor(data)
        check_if_pid_running_and_if_not_finish(process_observatory)
        process_observatory.update_all_status_with_process_control()
        generate_html(process_observatory)
        data.log.msg("Process monitor done.")


UNKNOWN_STATUS = "Unknown"

MAX_LOG_LENGTH = 17


class processMonitor(dict):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._log_store = diagLogs(data)

        ## get initial status
        self.update_all_status_with_process_control()

    @property
    def data(self):
        return self._data

    @property
    def log_store(self):
        return self._log_store

    def process_dict_as_df(self):
        data_control = dataControlProcess(self.data)
        process_df = data_control.get_dict_of_control_processes().as_pd_df()
        return process_df

    def process_dict_to_html_table(self, file):
        data_control = dataControlProcess(self.data)
        dict_of_process = data_control.get_dict_of_control_processes()
        dict_of_process.to_html_table_in_file(file)

    def update_all_status_with_process_control(self):
        list_of_process = get_list_of_process_names(self)
        for process_name in list_of_process:
            process_running_status = get_running_mode_str_for_process(
                self, process_name
            )
            self.update_status(process_name, process_running_status)

    def update_status(self, process_name, new_status):
        current_status = self.get_current_status(process_name)
        if current_status == new_status:
            pass
        else:
            self.change_status(process_name, new_status)

    def change_status(self, process_name, new_status):
        self[process_name] = new_status

    def get_current_status(self, process_name):
        status = copy(self.get(process_name, UNKNOWN_STATUS))
        return status

    def get_recent_log_messages(self):
        msgs = [
            entry.text
            for entry in self.log_store.get_log_items(
                attribute_dict={"sysmon": "status_change"}
            )
        ]
        return msgs


def get_list_of_process_names(process_observatory: processMonitor):
    diag_control = diagControlProcess(process_observatory.data)
    return diag_control.get_list_of_process_names()


def get_running_mode_str_for_process(
    process_observatory: processMonitor, process_name: str
):
    control = get_control_for_process(process_observatory, process_name)
    return control.running_mode_str


def get_control_for_process(process_observatory: processMonitor, process_name: str):
    diag_control = diagControlProcess(process_observatory.data)
    control = diag_control.get_control_for_process_name(process_name)

    return control


def check_if_pid_running_and_if_not_finish(process_observatory: processMonitor):
    data_control = dataControlProcess(process_observatory.data)
    data_control.check_if_pid_running_and_if_not_finish_all_processes()


def generate_html(process_observatory: processMonitor):
    jinja = Environment(
        loader=PackageLoader("syscontrol", "templates"), autoescape=select_autoescape()
    )
    template = jinja.get_template("monitor_template.html")
    with open(get_html_file_path(), "w") as file:
        file.write(
            template.render(
                {
                    "trading_server_description": describe_trading_server_login_data(),
                    "dbase_description": str(process_observatory.data.mongo_db),
                    "process_info": process_observatory.process_dict_as_df(),
                    "log_messages": process_observatory.get_recent_log_messages()[
                        -MAX_LOG_LENGTH:
                    ],
                }
            )
        )


def get_html_file_path():
    path = get_production_config().get_element_or_missing_data("monitor_output_path")
    resolved_path = get_filename_for_package(path)
    return resolved_path


if __name__ == "__main__":
    monitor()
