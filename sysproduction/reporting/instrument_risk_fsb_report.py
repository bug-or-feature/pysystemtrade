from sysdata.data_blob import dataBlob

from syscore.objects import header, table, arg_not_supplied, body_text
from sysproduction.reporting.api_fsb import ReportingApiFsb

HEADER_TEXT = body_text(
    "Risk calculation for different FSB instruments, columns as follows:\n"
    + "A - daily_price_stdev: Standard deviation, price points, per day\n"
    + "B - annual_price_stdev: Standard deviation, price points, per year = A * 16       \n"
    + "C - price: Price  \n"
    + "D - daily_perc_stdev: Standard deviation, percentage (1=1%), per day = A * C \n"
    + "E - annual_perc_stdev: Standard deviation, percentage (1=1%), per year = B * C = D * 16  \n"
    + "F - min_bet: Minimum bet in base (account) currency  \n"
    + "G - exposure: Notional exposure for minimum bet = F * C  \n"
    + "H - annual_risk_min_bet: Standard deviation, base currency, per year = B * F = E * G"
)


def instrument_risk_fsb_report(data: dataBlob = arg_not_supplied):

    if data is arg_not_supplied:
        data = dataBlob()

    reporting_api = ReportingApiFsb(data)

    formatted_output = []
    formatted_output.append(reporting_api.terse_header("Instrument Risk FSB report"))
    formatted_output.append(HEADER_TEXT)

    formatted_output.append(
        reporting_api.table_of_risk_all_fsb_instruments(
            sort_by="annual_perc_stdev",
            table_header="Risk of all FSB instruments with data - sorted by annualised % standard deviation",
        )
    )

    formatted_output.append(
        reporting_api.table_of_risk_all_fsb_instruments(
            sort_by="annual_risk_min_bet",
            table_header="Risk of all FSB instruments with data - "
            "sorted by annualised currency risk for the minimum bet",
        )
    )

    formatted_output.append(
        reporting_api.table_of_risk_all_fsb_instruments(
            sort_by="exposure",
            table_header="Risk of all FSB instruments with data - sorted by notional exposure per minimum bet",
        )
    )

    formatted_output.append(reporting_api.footer())

    return formatted_output
