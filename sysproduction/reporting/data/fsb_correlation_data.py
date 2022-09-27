import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import show

from syscore.pdutils import print_full
from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysdata.arctic.arctic_futures_per_contract_prices import arcticFuturesContractPriceData
from sysdata.data_blob import dataBlob
from sysobjects.contracts import futuresContract as fc
from sysobjects.contracts import get_code_and_id_from_contract_key as from_key
from sysproduction.data.contracts import dataContracts
from sysproduction.data.prices import diagPrices


def fsb_correlation_data(
        contract_obj,
        futures_prices=None,
        fsb_prices=None,
        draw=False):

    if futures_prices is None:
        futures_prices = arcticFuturesContractPriceData()

    if fsb_prices is None:
        fsb_prices = ArcticFsbContractPriceData()

    futures_df = futures_prices.get_merged_prices_for_contract_object(contract_obj)
    fsb_df = fsb_prices.get_merged_prices_for_contract_object(contract_obj)

    fut = futures_df.return_final_prices().resample("1B").last()
    fsb = fsb_df.return_final_prices().resample("1B").last()

    prices = pd.concat([fut, fsb], axis=1)
    prices.rename(
        columns={
            prices.columns[0]: "Future",
            prices.columns[1]: "FSB",
        }, inplace=True)
    sliced_prices = prices[fsb_df.index[0]:fsb_df.index[-1]]

    returns = pd.concat([fut.diff(), fsb.diff()], axis=1)
    returns.rename(
        columns={
            returns.columns[0]: "Future",
            returns.columns[1]: "FSB",
        }, inplace=True)
    sliced_returns = returns[fsb_df.index[0]:fsb_df.index[-1]]

    price_corr = sliced_prices.corr()
    returns_corr = sliced_returns.corr()

    if draw:
        do_plot(contract_obj, sliced_prices, sliced_returns, price_corr, returns_corr)
        print(f"Correlations: price :\n {price_corr.iloc[0, 1]}, returns: {returns_corr.iloc[0, 1]}")

    results = dict(
        Contract=contract_obj.key,
        Price=price_corr.iloc[0,1],
        Returns=returns_corr.iloc[0,1]
    )

    return results


def do_plot(contract_obj, prices, returns, price_corr, returns_corr):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(211)
    ax.set_title(f"Prices for {contract_obj.key}")
    ax.plot(prices["Future"], linestyle="-", label="Future", color='black', linewidth=2.0)
    ax.plot(prices["FSB"], linestyle="--", label="FSB", color='red', linewidth=2.0)
    #ax.text(2, 6, f"Correlation: {price_corr.iloc[0,1]}", fontsize=15)
    ax.legend()
    ax.grid(True)

    ax = fig.add_subplot(212)
    ax.set_title(f"Returns for {contract_obj.key}")
    ax.plot(returns["Future"], linestyle="-", label="Future", color='black', linewidth=2.0)
    ax.plot(returns["FSB"], linestyle="--", label="FSB", color='red', linewidth=2.0)
    #ax.text(2, 6, f"Correlation: {returns_corr.iloc[0,1]}", fontsize=15)
    #ax.figtext(0.5, 0.5, "Correlation: wank")
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
            all_contracts_list = diag_contracts.get_all_contract_objects_for_instrument_code(
                instr_code
            )
            for contract in all_contracts_list.currently_sampling():
                if futures_prices.has_merged_price_data_for_contract(contract) and \
                        fsb_prices.has_merged_price_data_for_contract(contract):
                    rows.append(fsb_correlation_data(contract, futures_prices, fsb_prices))

    results = pd.DataFrame(rows)
    results = results.sort_values(by="Price")

    print(f"\n{print_full(results)}\n")


def contract_key(key):
    return fc.from_two_strings(from_key(key)[0], from_key(key)[1])


if __name__ == "__main__":

    #run_fsb_report(fc.from_two_strings("V2X_fsb", "20210500"), plot=True)
    #run_fsb_report(fc.from_key("BTP_fsb/20210300"), plot=True)
    #run_fsb_report(fc("CRUDE_W_fsb", "20210700"), draw=True) # CRUDE_W_fsb/20220400
    #run_fsb_report(fc("ASX_fsb", "20211200"), draw=True) # ASX_fsb/20211200
    fsb_correlation_data(contract_key("CAC_fsb/20220900"), draw=True)

    # all correlations
    #currently_sampling_report()

    # view contract mappings and expiries
    #mappings_and_expiries()
