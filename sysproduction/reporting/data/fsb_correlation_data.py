import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import show
from syscore.text import remove_suffix
from syscore.fileutils import resolve_path_and_filename_for_package
from syscore.pdutils import print_full
from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.config.production_config import get_production_config
from sysdata.csv.csv_futures_contract_prices import (
    csvFuturesContractPriceData,
    ConfigCsvFuturesPrices,
)
from sysdata.data_blob import dataBlob
from sysobjects.contracts import futuresContract as fc
from sysobjects.contracts import get_code_and_id_from_contract_key as from_key
from sysproduction.data.contracts import dataContracts
from sysproduction.data.prices import diagPrices
from sysinit.futures_spreadbet.fsb_contract_prices import (
    build_import_config,
)


def fsb_correlation_data(
    contract_obj,
    futures_prices=None,
    fsb_prices=None,
    is_priced=False,
    is_fwd=False,
    draw=False,
):

    if futures_prices is None:
        futures_prices = arcticFuturesContractPriceData()

    if fsb_prices is None:
        fsb_prices = ArcticFsbContractPriceData()

    bc_datapath = (
        resolve_path_and_filename_for_package(
            get_production_config().get_element_or_missing_data("barchart_path")
            # get_production_config().get_element_or_missing_data("norgate_path")
        ),
    )

    import_config = build_import_config(contract_obj.instrument_code)

    # ib_prices = csvFuturesContractPriceData(
    #     #datapath=bc_datapath,
    #     datapath="/Users/ageach/Dev/work/pyhistprice/data/barchart/",
    #     #datapath="/Users/ageach/Documents/backup/pst_caleb/csv/backups_csv/contract_prices/",
    #     config=import_config,
    #     # #config=ConfigCsvFuturesPrices(
    #     #     #input_date_index_name="DATETIME",
    #     #     input_date_index_name="Time",
    #     #     #input_skiprows=0,
    #     #     #input_skipfooter=0,
    #     #     input_date_format="%Y-%m-%d",  # 19810507
    #     #     input_date_format="%Y-%m-%dT%H:%M:%S",  # 2022-01-18T00:00:00+0000
    #     #     #input_column_mapping=dict(
    #     #     #    OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
    #     #     #),  # Date,Symbol,Security Name,Open,High,Low,Close,Volume
    #     #     apply_multiplier=100.0,
    #     #     apply_inverse=False,
    #     # )
    # )

    futures_df = futures_prices.get_merged_prices_for_contract_object(contract_obj)
    fsb_df = fsb_prices.get_merged_prices_for_contract_object(contract_obj)

    remove_suffix(contract_obj.instrument_code, "_fsb")
    ib_contract = fc.from_two_strings(
        remove_suffix(contract_obj.instrument_code, "_fsb"), contract_obj.date_str
    )
    # ib_df = ib_prices.get_merged_prices_for_contract_object(ib_contract)

    fut = futures_df.return_final_prices().resample("1B").last()
    fut.name = "Barchart"

    fsb = fsb_df.return_final_prices().resample("1B").last()
    fsb.name = "IG"

    # ib = ib_df.return_final_prices().resample("1B").last()
    # ib.name = "IB"

    prices = pd.concat([fut, fsb], axis=1)
    # prices = pd.concat([fut, fsb, ib], axis=1)

    sliced_prices = prices[fsb_df.index[0] : fsb_df.index[-1]]

    returns = pd.concat([fut.diff(), fsb.diff()], axis=1)
    returns.rename(
        columns={
            returns.columns[0]: "Future",
            returns.columns[1]: "FSB",
        },
        inplace=True,
    )
    sliced_returns = returns[fsb_df.index[0] : fsb_df.index[-1]]

    price_corr = sliced_prices.corr()
    returns_corr = sliced_returns.corr()

    if draw:
        do_plot(contract_obj, sliced_prices, sliced_returns, price_corr, returns_corr)
        print(
            f"Correlations: price :\n {price_corr.iloc[0, 1]}, returns: {returns_corr.iloc[0, 1]}"
        )

    results = dict(
        Contract=contract_obj.key,
        Price=price_corr.iloc[0, 1],
        Returns=returns_corr.iloc[0, 1],
        IsPriced=is_priced,
        IsFwd=is_fwd,
    )

    return results


def do_plot(contract_obj, prices, returns, price_corr, returns_corr):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(211)
    ax.set_title(f"Prices for {contract_obj.key}")
    ax.plot(
        prices["Barchart"],
        linestyle="-",
        label="Barchart",
        color="black",
        linewidth=2.0,
    )
    ax.plot(prices["IG"], linestyle="--", label="IG", color="red", linewidth=2.0)
    # ax.plot(prices["IB"], linestyle=":", label="IB", color="green", linewidth=3.0)
    # ax.text(2, 6, f"Correlation: {price_corr.iloc[0,1]}", fontsize=15)
    ax.legend()
    ax.grid(True)

    ax = fig.add_subplot(212)
    ax.set_title(f"Returns for {contract_obj.key}")
    ax.plot(
        returns["Future"], linestyle="-", label="Future", color="black", linewidth=2.0
    )
    ax.plot(returns["FSB"], linestyle="--", label="FSB", color="red", linewidth=2.0)
    # ax.text(2, 6, f"Correlation: {returns_corr.iloc[0,1]}", fontsize=15)
    # ax.figtext(0.5, 0.5, "Correlation: wank")
    ax.legend()
    ax.grid(True)
    show()


def currently_sampling_report():

    futures_prices = arcticFuturesContractPriceData()
    fsb_prices = ArcticFsbContractPriceData()

    # futures_instr_list = futures_prices.get_list_of_instrument_codes_with_price_data()

    rows = []
    with dataBlob(log_name="FSB-Report") as data:
        price_data = diagPrices(data)
        diag_contracts = dataContracts(data)

        for instr_code in price_data.get_list_of_instruments_in_multiple_prices():
            all_contracts_list = (
                diag_contracts.get_all_contract_objects_for_instrument_code(instr_code)
            )
            for contract in all_contracts_list.currently_sampling():
                if futures_prices.has_merged_price_data_for_contract(
                    contract
                ) and fsb_prices.has_merged_price_data_for_contract(contract):
                    rows.append(
                        fsb_correlation_data(
                            contract,
                            futures_prices=futures_prices,
                            fsb_prices=fsb_prices,
                        )
                    )

    results = pd.DataFrame(rows)
    results = results.sort_values(by="Price")

    print(f"\n{print_full(results)}\n")


def contract_key(key):
    return fc.from_two_strings(from_key(key)[0], from_key(key)[1])


if __name__ == "__main__":

    # run_fsb_report(fc.from_two_strings("V2X_fsb", "20210500"), plot=True)
    # run_fsb_report(fc.from_key("BTP_fsb/20210300"), plot=True)
    # run_fsb_report(fc("CRUDE_W_fsb", "20210700"), draw=True) # CRUDE_W_fsb/20220400
    # run_fsb_report(fc("ASX_fsb", "20211200"), draw=True) # ASX_fsb/20211200
    fsb_correlation_data(contract_key("CAC_fsb/20220900"), draw=True)

    # all correlations
    # currently_sampling_report()

    # view contract mappings and expiries
    # mappings_and_expiries()
