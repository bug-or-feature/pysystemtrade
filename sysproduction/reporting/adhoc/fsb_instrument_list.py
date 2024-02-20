import pandas as pd

from syscore.constants import arg_not_supplied
from syscore.interactive.progress_bar import progressBar
from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from sysproduction.data.instruments import diagInstruments
from sysproduction.data.prices import diagPrices
from sysproduction.reporting.api import reportingApi
from sysproduction.reporting.reporting_functions import (
    table,
    pandas_display_for_reports,
)


def instrument_list_report(data: dataBlob = arg_not_supplied):
    formatted_output = []

    diag_instruments = diagInstruments(data)
    diag_prices = diagPrices(data)
    data_broker = dataBroker(data)
    reporting_api = reportingApi(
        data,
    )

    list_of_instruments = diag_instruments.get_list_of_instruments()

    p = progressBar(len(list_of_instruments))
    list_of_results = []
    for instrument_code in list_of_instruments:
        meta_data = diag_instruments.get_meta_data(instrument_code)
        row_for_instrument = instrument_results_as_pd_df_row(
            meta_data,
            instrument_code=instrument_code,
            data_broker=data_broker,
            diag_prices=diag_prices,
        )
        list_of_results.append(row_for_instrument)
        p.iterate()

    pandas_display_for_reports()
    results_as_df = pd.concat(list_of_results, axis=0)

    formatted_output.append(
        reporting_api.terse_header("List of instruments with configuration")
    )
    formatted_output.append(
        table("Combined instrument and broker config", results_as_df)
    )

    formatted_output.append(reporting_api.footer())

    return formatted_output


def instrument_results_as_pd_df_row(
    meta_data,
    instrument_code: str,
    data_broker: dataBroker,
    diag_prices: diagPrices,
):
    instrument_broker_data = data_broker.get_brokers_instrument_with_metadata(
        instrument_code
    )

    prices = diag_prices.get_adjusted_prices(instrument_code)
    if len(prices) > 0:
        raw = prices.index[0]
        first_date = raw.strftime("%Y-%m-%d")
    else:
        first_date = "n/a"

    meta_data_as_dict = meta_data.as_dict()
    broker_data_as_dict = instrument_broker_data.meta_data.as_dict()
    relabelled_broker_data_as_dict = dict(
        [(key, value) for key, value in broker_data_as_dict.items()]
    )

    merged_data = {
        **meta_data_as_dict,
        **relabelled_broker_data_as_dict,
        "from": first_date,
    }
    merged_data_as_pd = pd.DataFrame(merged_data, index=[instrument_code])
    del merged_data_as_pd["PerBlock"]
    del merged_data_as_pd["PerTrade"]
    del merged_data_as_pd["Percentage"]
    del merged_data_as_pd["currency"]

    return merged_data_as_pd


if __name__ == "__main__":
    instrument_list_report()
