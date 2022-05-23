from syscore.objects import arg_not_supplied
from sysdata.data_blob import dataBlob
from sysproduction.reporting.api_fsb import ReportingApiFsb


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
    #formatted_output.append(HEADER_TEXT)

    formatted_output.append(reporting_api_fsb.table_of_fsb_correlations())

    formatted_output.append(
        reporting_api_fsb.fsb_mappings_and_expiries()
    )

    formatted_output.append(reporting_api_fsb.footer())

    return formatted_output


if __name__ == "__main__":

    do_fsb_report()
