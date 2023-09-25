import pickle

import pandas as pd

from syscore.fileutils import resolve_path_and_filename_for_package
from syscore.text import remove_suffix
from sysproduction.reporting.report_configs import reportConfig
from sysproduction.reporting.reporting_functions import (
    header,
    table,
    pandas_display_for_reports,
    parse_report_results,
    output_file_report,
)
from sysdata.data_blob import dataBlob


def instrument_risk_compare_report():

    report_config = reportConfig(
        title="Instrument Risk Compare Report", function="not_used", output="file"
    )

    data = dataBlob()

    manual_override = {
        "GAS_US_fsb": "GAS_US_mini",
        "GASOLINE_fsb": "GASOILINE",
        "GOLD_fsb": "GOLD_micro",
        "JGB_fsb": "JGB-SGX-mini",
        "NASDAQ_fsb": "NASDAQ_micro",
        # "SILVER_fsb": "SILVER-mini",
        "SP500_fsb": "SP500_micro",
    }

    # FSBs
    fsb_data = load_pickled_risk_data("fsb_instrument_risk.pickle")
    fut_data = load_pickled_risk_data("futures_instrument_risk.pickle")

    rows = []
    no_matches = []
    for key, value in fsb_data.items():

        if key in manual_override:
            fut_instr_code = manual_override[key]
        else:
            fut_instr_code = remove_suffix(key, "_fsb")

        if fut_instr_code in fut_data:

            fut_dict = fut_data[fut_instr_code]
            fsb_ann = round(value["annual_perc_stdev"], 2)
            fut_ann = round(fut_dict["annual_perc_stdev"], 2)
            diff = abs(100 - ((fsb_ann / fut_ann) * 100))
            rows.append(
                {
                    "Instr": key,
                    "FSB Daily %": round(value["daily_perc_stdev"], 3),
                    "Fut Daily %": round(fut_dict["daily_perc_stdev"], 2),
                    "FSB Annual %": round(value["annual_perc_stdev"], 2),
                    "Fut Annual %": round(fut_dict["annual_perc_stdev"], 2),
                    "Diff %": round(diff, 2),
                }
            )
        else:
            no_matches.append(f"{fut_instr_code}_fsb")

    results = pd.DataFrame(rows)
    results = results.sort_values(by="Diff %", ascending=False)

    report_results = [
        header("Instrument Risk Comparison"),
        table("Futures Spread Bets (FSB) v Futures (Fut)", results),
        table("FSBs with no matching Future", no_matches),
    ]

    pandas_display_for_reports()

    parsed_report_results = parse_report_results(data, report_results=report_results)

    output_file_report(
        parsed_report=parsed_report_results, data=data, report_config=report_config
    )


def load_pickled_risk_data(filename):
    path = resolve_path_and_filename_for_package("sysproduction.reporting", filename)
    full_path = resolve_path_and_filename_for_package(path)
    with open(full_path, "rb") as file:
        data = pickle.load(file)
        return data


if __name__ == "__main__":
    instrument_risk_compare_report()
