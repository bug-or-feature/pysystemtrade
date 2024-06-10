from syscontrol.run_process import processToRun

from sysdata.data_blob import dataBlob

from syscontrol.html_generation import build_report_files
from sysproduction.data.reports import dataReports

# JUST A COPY AND PASTE JOB RIGHT NOW


def run_reports():
    process_name = "run_reports"
    data = dataBlob(
        log_name=process_name,
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
        ),
    )
    list_of_timer_names_and_functions = get_list_of_timer_functions_for_reports(data)
    report_process = processToRun(process_name, data, list_of_timer_names_and_functions)
    report_process.run_process()


def get_list_of_timer_functions_for_reports(data):
    list_of_timer_names_and_functions = []
    data_reports = dataReports(data)
    all_configs = data_reports.get_report_configs_to_run()

    for report_name, report_config in all_configs.items():
        data_for_report = dataBlob(
            log_name=report_name, csv_data_paths=data.csv_data_paths
        )
        report_object = runReport(data_for_report, report_config, report_name)
        report_tuple = (report_name, report_object)
        list_of_timer_names_and_functions.append(report_tuple)

    data_for_gen = dataBlob(log_name="generate_html")
    gen_obj = generateWrappers(data_for_gen, "generate_html")
    report_tuple = ("generate_html", gen_obj)
    list_of_timer_names_and_functions.append(report_tuple)

    return list_of_timer_names_and_functions


from sysproduction.reporting.reporting_functions import run_report


class runReport(object):
    def __init__(self, data, config, report_function):
        self.data = data
        self.config = config

        # run process expects a method with same name as log name
        setattr(self, report_function, self.run_generic_report)

    def run_generic_report(self):
        ## Will be renamed
        run_report(self.config, data=self.data)


class generateWrappers(object):
    def __init__(self, data, function):
        self.data = data

        # run process expects a method with same name as log name
        setattr(self, function, self.run_function)

    def run_function(self):
        ## Will be renamed
        build_report_files(self.data, {})


if __name__ == "__main__":
    run_reports()
