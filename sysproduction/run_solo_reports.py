from sysdata.data_blob import dataBlob
from sysproduction.reporting.reporting_functions import run_report_with_data_blob
from sysproduction.reporting.roll_report import ALL_ROLL_INSTRUMENTS
from sysproduction.reporting.report_configs import reportConfig

def run_solo_roll_report():
    config = reportConfig(
        title="Roll report",
        function="sysproduction.reporting.roll_report.roll_info",
        instrument_code=ALL_ROLL_INSTRUMENTS,
        output="email"
    )
    with dataBlob(log_name="Email-Roll-Report") as data:
        run_report_with_data_blob(config, data)


if __name__ == "__main__":
    run_solo_roll_report()