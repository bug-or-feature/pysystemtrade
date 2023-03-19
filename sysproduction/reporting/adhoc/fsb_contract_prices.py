import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import show
from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData


def run_compare_fsb_contract_price_report(
    contract_obj_1,
    contract_obj_2,
    contract_obj_3,
    fsb_prices=None,
    draw=False,
):

    if fsb_prices is None:
        fsb_prices = ArcticFsbContractPriceData()

    adj_prices = arcticFuturesAdjustedPricesData()

    df_1 = fsb_prices.get_merged_prices_for_contract_object(contract_obj_1)
    df_2 = fsb_prices.get_merged_prices_for_contract_object(contract_obj_2)
    df_3 = fsb_prices.get_merged_prices_for_contract_object(contract_obj_3)
    adj = adj_prices.get_adjusted_prices(contract_obj_1)

    fsb_1 = df_1.return_final_prices().resample("1B").last()
    fsb_1.name = "1"

    fsb_2 = df_2.return_final_prices().resample("1B").last()
    fsb_2.name = "2"

    fsb_3 = df_3.return_final_prices().resample("1B").last()
    fsb_3.name = "3"

    prices = pd.concat([fsb_1, fsb_2, fsb_3], axis=1)
    # sliced_prices = prices[df_1.index[0]: df_2.index[-1]]

    if draw:
        do_plot(contract_obj_1, contract_obj_2, contract_obj_3, prices)
        # print(
        #     f"Correlations: price :\n {price_corr.iloc[0, 1]}, returns: {returns_corr.iloc[0, 1]}"
        # )

    results = dict(
        First=contract_obj_1.key,
        Second=contract_obj_2.key,
        Third=contract_obj_3.key,
    )

    return results


def do_plot(contract_obj_1, contract_obj_2, contract_obj_3, prices):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(211)
    ax.set_title(
        f"Comparing prices for {contract_obj_1.key}, {contract_obj_2.key}, {contract_obj_3.key}"
    )
    ax.plot(
        prices["1"],
        linestyle="-",
        label=contract_obj_1.key,
        color="black",
        linewidth=1.0,
    )
    ax.plot(
        prices["2"],
        linestyle="--",
        label=contract_obj_2.key,
        color="red",
        linewidth=2.0,
    )
    ax.plot(
        prices["3"],
        linestyle="--",
        label=contract_obj_3.key,
        color="green",
        linewidth=1.5,
    )
    # ax.plot(prices["IB"], linestyle=":", label="IB", color="green", linewidth=3.0)
    # ax.text(2, 6, f"Correlation: {price_corr.iloc[0,1]}", fontsize=15)
    ax.legend()
    ax.grid(True)

    show()
