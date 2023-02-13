from sysdata.data_blob import dataBlob

from syscore.constants import arg_not_supplied
from sysproduction.reporting.reporting_functions import body_text
from sysproduction.reporting.api_fsb import ReportingApiFsb


HEADER_TEXT = body_text(
    "The following report calculates minimum capital as follows:\n"
    + "A - min_bet: Minimum bet in account currency \n"
    + "B - price: Price\n"
    + "C - ann_perc_stdev: Annual standard deviation in percentage terms (20 = 20%) \n"
    + "D - risk_target: Risk target in percentage terms (20 = 20%) \n"
    + "E - min_cap_min_bet: Minimum capital for minimum bet = A * B * C / D \n"
    + "F - min_pos_avg_fc: Minimum position multiplier for average forecast \n"
    + "G - min_cap_avg_fc: Minimum capital for average forecast = E * F \n"
    + "H - instr_weight: Proportion of capital allocated to instrument \n"
    + "I - IDM: Instrument diversification multiplier \n"
    + "J - min_cap_portfolio: Minimum capital within a portfolio, allowing for minimum position = G / ( H * I) \n"
)


def minimum_capital_fsb_report(
    data: dataBlob = arg_not_supplied,
):

    if data is arg_not_supplied:
        data = dataBlob()

    reporting_api = ReportingApiFsb(data)

    formatted_output = []
    formatted_output.append(reporting_api.terse_header("Minimum capital FSB report"))
    formatted_output.append(HEADER_TEXT)

    formatted_output.append(reporting_api.table_of_minimum_capital_fsb())

    formatted_output.append(reporting_api.footer())

    return formatted_output
