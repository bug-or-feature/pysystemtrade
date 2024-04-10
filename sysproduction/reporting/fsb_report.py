from sysdata.data_blob import dataBlob
from syscore.constants import arg_not_supplied
from syscore.interactive.display import set_pd_print_options
from sysproduction.reporting.reporting_functions import body_text
from sysproduction.reporting.api_fsb import ReportingApiFsb
from sysbrokers.IG.ig_instruments_data import IgFuturesInstrumentData
from sysproduction.data.production_data_objects import (
    get_class_for_data_type,
    MARKET_INFO_DATA,
    FSB_EPIC_HISTORY_DATA,
    EPIC_PERIODS_DATA,
)

MISSING_EPIC_HEADER_TEXT = body_text(
    "Instruments where the epic for a given contract is yet to be defined.\n"
    "This can happen for forward contracts where there are only two epics, but should "
    "never happen for priced. Missing forwards will normally resolve just after a "
    "roll, but if IG skip a contract will need manual action. "
)

MISCONFIGURED_MINIMUM_BET_HEADER_TEXT = body_text(
    "Instruments where the minimum bet is misconfigured, or recently changed by IG"
)

LATE_MARKET_INFO_HEADER_TEXT = body_text(
    "Instruments where the market info has not been recently updated"
)

PROBLEM_ROLL_HEADER_TEXT = body_text(
    "Possible unexpected IG roll schedule, or roll config\n"
)

EPIC_VARIATION_HEADER_TEXT = body_text(
    "Instruments where there is a mismatch between "
    "the configured epic periods and those calculated by our regular scans. \n"
    "This happens occasionally for commodities and STIRs"
)

ALL_CORR_HEADER_TEXT = body_text(
    "Price: correlation between spread bet price and the underlying future, per contract\n"
    + "Returns: correlation between spread bet returns and the underlying future, per contract\n"
    + "Sorted by contract"
)

BELOW_MIN_CORR_HEADER_TEXT = body_text(
    "Possible problem correlations. The contracts below have possible data or config issues\n"
    + "Price: correlation between spread bet price and the underlying future, per contract\n"
    + "Returns: correlation between spread bet returns and the underlying future, per contract\n"
    + "Showing only those with Price < 0.8 or Returns < 0.6, sorted by Returns"
)

BELOW_MIN_CORR_PR_HEADER_TEXT = body_text(
    "Possible problem correlations. The priced contracts below have possible data or config issues\n"
    + "Price: correlation between spread bet price and the underlying future, per contract\n"
    + "Returns: correlation between spread bet returns and the underlying future, per contract\n"
    + "Showing only those with Price < 0.8 or Returns < 0.6, sorted by Returns"
)

BELOW_MIN_CORR_FWD_HEADER_TEXT = body_text(
    "Possible problem correlations. The forward contracts below have possible data or config issues\n"
    + "Price: correlation between spread bet price and the underlying future, per contract\n"
    + "Returns: correlation between spread bet returns and the underlying future, per contract\n"
    + "Showing only those with Price < 0.8 or Returns < 0.6, sorted by Returns"
)


def do_fsb_report(
    data: dataBlob = arg_not_supplied,
):
    if data is arg_not_supplied:
        data = dataBlob()

    data.add_class_list(
        [
            IgFuturesInstrumentData,
            get_class_for_data_type(FSB_EPIC_HISTORY_DATA),
            get_class_for_data_type(MARKET_INFO_DATA),
            get_class_for_data_type(EPIC_PERIODS_DATA),
        ]
    )
    reporting_api_fsb = ReportingApiFsb(data)
    formatted_output = []

    formatted_output.append(reporting_api_fsb.terse_header("FSB report"))

    # instruments where epic is yet to be defined
    formatted_output.append(MISSING_EPIC_HEADER_TEXT)
    formatted_output.append(reporting_api_fsb.table_of_missing_epics())
    formatted_output.append(
        reporting_api_fsb.table_of_missing_epics(
            table_header="Missing priced epic", style="priced"
        )
    )

    # misconfigured minimum bets
    formatted_output.append(MISCONFIGURED_MINIMUM_BET_HEADER_TEXT)
    formatted_output.append(reporting_api_fsb.table_of_wrong_min_bet_size())

    # delayed market info
    formatted_output.append(LATE_MARKET_INFO_HEADER_TEXT)
    formatted_output.append(reporting_api_fsb.table_of_delayed_market_info())

    # epic period mismatches
    formatted_output.append(EPIC_VARIATION_HEADER_TEXT)
    set_pd_print_options(extra_wide=True)
    formatted_output.append(reporting_api_fsb.table_of_epic_period_mismatches())
    set_pd_print_options()

    # roll calendar mismatches
    formatted_output.append(PROBLEM_ROLL_HEADER_TEXT)
    formatted_output.append(reporting_api_fsb.table_of_problem_fsb_rolls())

    # problem correlations for priced contracts
    formatted_output.append(BELOW_MIN_CORR_PR_HEADER_TEXT)
    formatted_output.append(
        reporting_api_fsb.table_of_problem_priced_fsb_correlations()
    )

    # problem correlations for forward contracts
    formatted_output.append(BELOW_MIN_CORR_FWD_HEADER_TEXT)
    formatted_output.append(
        reporting_api_fsb.table_of_problem_forward_fsb_correlations()
    )

    # price and returns correlation for currently sampled contracts
    # formatted_output.append(ALL_CORR_HEADER_TEXT)
    # formatted_output.append(reporting_api_fsb.table_of_fsb_correlations())

    # fsb mappings and expiries
    formatted_output.append(reporting_api_fsb.fsb_mappings_and_expiries())

    formatted_output.append(reporting_api_fsb.footer())

    return formatted_output


if __name__ == "__main__":
    do_fsb_report()
