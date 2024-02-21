from syscore.constants import arg_not_supplied
from sysdata.data_blob import dataBlob
from sysproduction.reporting.api import reportingApi
from sysproduction.reporting.reporting_functions import (
    body_text,
)
from sysquant.estimators.correlation_estimator import correlationEstimate
from systems.basesystem import System
from systems.futures_spreadbet.fsb_system import fsb_system
from systems.provided.static_small_system_optimise.optimise_small_system import (
    find_best_ordered_set_of_instruments,
    get_correlation_matrix,
)


def static_fsb_instrument_selection_report(
    data: dataBlob = arg_not_supplied, selection_config=None
):
    if selection_config is None:
        selection_config = [
            [2000, 1],
            [5000, 3],
            [10000, 5],
            [15000, 8],
            [20000, 10],
            [25000, 15],
            [30000, 20],
            [35000, 23],
            [40000, 25],
            [35000, 28],
            [50000, 30],
        ]

    formatted_output = []
    reporting_api = reportingApi(
        data,
    )

    system = fsb_system()
    corr_matrix = get_correlation_matrix(system)  ## capital irrelevant

    formatted_output.append(
        reporting_api.terse_header(
            "Static instrument selection for different levels of capital"
        )
    )
    for (
        capital,
        est_number_of_instruments,
    ) in selection_config:
        system = fsb_system()
        instrument_list = static_system_results_for_capital(
            system,
            corr_matrix=corr_matrix,
            est_number_of_instruments=est_number_of_instruments,
            capital=capital,
        )

        text_to_output = body_text(
            f"For capital of {capital}, {len(instrument_list)} instruments, "
            f"selected order: {str(instrument_list)}"
        )
        formatted_output.append(text_to_output)

    formatted_output.append(reporting_api.footer())

    return formatted_output


def static_system_results_for_capital(
    system: System,
    corr_matrix: correlationEstimate,
    est_number_of_instruments: int,
    capital: float,
):
    notional_starting_IDM = est_number_of_instruments**0.25
    max_instrument_weight = 1.0 / est_number_of_instruments

    return find_best_ordered_set_of_instruments(
        system=system,
        corr_matrix=corr_matrix,
        capital=capital,
        max_instrument_weight=max_instrument_weight,
        notional_starting_IDM=notional_starting_IDM,
    )


if __name__ == "__main__":
    static_fsb_instrument_selection_report(selection_config=[[10000, 3]])
