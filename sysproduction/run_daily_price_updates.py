from syscontrol.run_process import processToRun
from sysproduction.update_historical_prices import updateHistoricalPrices
from sysproduction.generate_fsb_updates import GenerateFsbUpdates
from sysproduction.interactive_controls import auto_update_spread_costs
from sysdata.data_blob import dataBlob


def run_daily_price_updates():
    process_name = "run_daily_prices_updates"
    data = dataBlob(log_name=process_name)
    list_of_timer_names_and_functions = get_list_of_timer_functions_for_price_update()
    price_process = processToRun(process_name, data, list_of_timer_names_and_functions)
    price_process.run_process()


def get_list_of_timer_functions_for_price_update():
    data = dataBlob(
        log_name="prices_updates",
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
        ),
    )
    historical_update_object = updateHistoricalPrices(data)
    generate_fsb_object = GenerateFsbUpdates(data)
    update_slippage = auto_update_spread_costs(data, filter_on=5.0)

    list_of_timer_names_and_functions = [
        ("update_historical_prices", historical_update_object),
        ("generate_fsb_updates", generate_fsb_object),
        ("auto_update_slippage", update_slippage),
    ]

    return list_of_timer_names_and_functions


if __name__ == "__main__":
    run_daily_price_updates()
