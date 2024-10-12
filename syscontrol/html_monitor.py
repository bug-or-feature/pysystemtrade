from sysdata.data_blob import dataBlob

from sysproduction.data.control_process import dataControlProcess
from syscontrol.monitor import processMonitor, check_if_pid_running_and_if_not_finish
from syscontrol.list_running_pids import describe_trading_server_login_data
from syscontrol.html_generation import (
    build_dashboard,
    build_report_files,
)


def html_monitor():
    with dataBlob(log_name="html-system-monitor") as data:
        data.log.debug("Starting HTML process monitor...")
        process_observatory = HTMLProcessMonitor(data)
        check_if_pid_running_and_if_not_finish(process_observatory)
        process_observatory.update_all_status_with_process_control()
        build_dashboard(data, create_monitor_context(process_observatory))
        build_report_files(data, {})
        data.log.debug("HTML process monitor done.")


class HTMLProcessMonitor(processMonitor):
    def __init__(self, data):
        super().__init__(data)
        self._data = data
        self.update_all_status_with_process_control()

    def process_dict_as_df(self):
        data_control = dataControlProcess(self.data)
        process_df = data_control.get_dict_of_control_processes().as_pd_df()
        return process_df

    def update_status(self, process_name, new_status):
        current_status = self.get_current_status(process_name)
        if current_status == new_status:
            pass
        else:
            self.change_status(process_name, new_status)


def create_monitor_context(process_observatory):
    return {
        "trading_server_description": describe_trading_server_login_data(),
        "dbase_description": str(process_observatory.data.mongo_db),
        "process_info": process_observatory.process_dict_as_df(),
    }


if __name__ == "__main__":
    html_monitor()
