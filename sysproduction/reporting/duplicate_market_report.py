from sysdata.data_blob import dataBlob

from syscore.constants import arg_not_supplied
from sysproduction.reporting.reporting_functions import body_text
from sysproduction.reporting.api import reportingApi

HEADER_TEXT = body_text(
    "List of duplicate markets eg mini and micro, or dual listing; recommendations as to which to trade"
)


def duplicate_market_report(
    data: dataBlob = arg_not_supplied,
    min_correlation: float = 0.95,
):
    if data is arg_not_supplied:
        data = dataBlob()

    reporting_api = reportingApi(
        data,
        min_correlation=min_correlation,
    )

    formatted_output = []
    formatted_output.append(reporting_api.terse_header("Duplicate markets report"))
    formatted_output.append(HEADER_TEXT)

    list_of_duplicate_market_tables = reporting_api.list_of_duplicate_market_tables()

    formatted_output.append(
        reporting_api.body_text_suggest_changes_to_duplicate_markets()
    )
    formatted_output = formatted_output + list_of_duplicate_market_tables

    formatted_output.append(reporting_api.get_correlations_for_configured_duplicates())

    formatted_output.append(reporting_api.get_potential_unconfigured_duplicates())

    formatted_output.append(reporting_api.footer())

    return formatted_output


if __name__ == "__main__":
    duplicate_market_report()
