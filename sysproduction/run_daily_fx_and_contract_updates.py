from syscontrol.run_process import processToRun
from sysproduction.update_fx_prices import updateFxPrices
from sysproduction.update_epics import UpdateEpicHistory
from sysproduction.update_sampled_contracts import updateSampledContracts

from sysdata.data_blob import dataBlob


def run_daily_fx_and_contract_updates():
    process_name = "run_daily_fx_and_contract_updates"
    data = dataBlob(log_name=process_name)
    list_of_timer_names_and_functions = (
        get_list_of_timer_functions_for_fx_and_contract_update()
    )
    price_process = processToRun(process_name, data, list_of_timer_names_and_functions)
    price_process.run_process()


def get_list_of_timer_functions_for_fx_and_contract_update():
    data_fx = dataBlob(log_name="update_fx_prices")
    data_epics = dataBlob(log_name="update_epics")
    data_contracts = dataBlob(
        log_name="update_sampled_contracts",
        csv_data_paths=dict(
            csvFuturesInstrumentData="data.futures_spreadbet.csvconfig",
            csvRollParametersData="data.futures_spreadbet.csvconfig",
        ),
    )

    fx_update_object = updateFxPrices(data_fx)
    epic_update_object = UpdateEpicHistory(data_epics)
    contracts_update_object = updateSampledContracts(data_contracts)

    list_of_timer_names_and_functions = [
        ("update_fx_prices", fx_update_object),
        ("update_epic_history", epic_update_object),
        ("update_sampled_contracts", contracts_update_object),
    ]

    return list_of_timer_names_and_functions


if __name__ == "__main__":
    run_daily_fx_and_contract_updates()
