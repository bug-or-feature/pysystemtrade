from sysdata.data_blob import dataBlob
from syscore.objects import arg_not_supplied, body_text
from sysproduction.reporting.api_fsb import ReportingApiFsb

ALL_CORR_HEADER_TEXT = body_text(
    "Price: correlation between spread bet price and the underlying future, per contract\n" +
    "Returns: correlation between spread bet returns and the underlying future, per contract\n" +
    "Sorted by contract"
)

BELOW_MIN_CORR_HEADER_TEXT = body_text(
    "Possible problem correlations. The contracts below have possible data or config issues\n" +
    "Price: correlation between spread bet price and the underlying future, per contract\n" +
    "Returns: correlation between spread bet returns and the underlying future, per contract\n" +
    "Showing only those with Price < 0.8 or Returns < 0.6, sorted by Returns"
)


def do_fsb_report(
    data: dataBlob = arg_not_supplied,
):

    if data is arg_not_supplied:
        data = dataBlob()
    reporting_api_fsb = ReportingApiFsb(
        data
    )
    formatted_output = []

    formatted_output.append(reporting_api_fsb.std_header("FSB report"))

    # problem correlations for currently sampled contracts
    formatted_output.append(BELOW_MIN_CORR_HEADER_TEXT)
    formatted_output.append(reporting_api_fsb.table_of_problem_fsb_correlations())

    # price and returns correlation for currently sampled contracts
    formatted_output.append(ALL_CORR_HEADER_TEXT)
    formatted_output.append(reporting_api_fsb.table_of_fsb_correlations())

    # fsb mappings and expiries
    formatted_output.append(
        reporting_api_fsb.fsb_mappings_and_expiries()
    )

    formatted_output.append(reporting_api_fsb.footer())

    return formatted_output


if __name__ == "__main__":

    do_fsb_report()
