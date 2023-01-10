import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import show

from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData


def correlation_data(instr, db_data=None, csv_data=None, draw=False):

    if db_data is None:
        db_data = arcticFuturesAdjustedPricesData()

    if csv_data is None:
        csv_data = csvFuturesSimData()

    db_series = db_data.get_adjusted_prices(instr)
    csv_series = csv_data.get_backadjusted_futures_price(instr)

    db = db_series.resample("1B").last()
    csv = csv_series.resample("1B").last()

    prices = pd.concat({"DB": db, "CSV": csv}, axis=1)
    sliced_prices = prices[
        max(db_series.index[0], csv_series.index[0]) : min(
            db_series.index[-1], csv_series.index[-1]
        )
    ]

    returns = pd.concat({"DB": db.diff(), "CSV": csv.diff()}, axis=1)
    sliced_returns = returns[
        max(db_series.index[0], csv_series.index[0]) : min(
            db_series.index[-1], csv_series.index[-1]
        )
    ]

    price_corr = sliced_prices.corr()
    returns_corr = sliced_returns.corr()

    if draw:
        do_plot(instr, sliced_prices, sliced_returns)

    results = dict(
        Instrument=instr,
        PriceCorr=price_corr.iloc[0, 1],
        ReturnsCorr=returns_corr.iloc[0, 1],
        StartDB=prices["DB"].first_valid_index(),
        StartCSV=prices["CSV"].first_valid_index(),
    )

    print(f"Results: {results}")
    return results


def do_plot(instr, prices, returns):
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(211)
    ax.set_title(f"Prices for {instr}")
    ax.plot(prices["DB"], linestyle="-", label="DB", color="orange", linewidth=2.0)
    ax.plot(prices["CSV"], linestyle="--", label="CSV", color="blue", linewidth=2.0)
    ax.legend()
    ax.grid(True)

    ax = fig.add_subplot(212)
    ax.set_title(f"Returns for {instr}")
    ax.plot(returns["DB"], linestyle="-", label="DB", color="orange", linewidth=1.0)
    ax.plot(returns["CSV"], linestyle="--", label="CSV", color="blue", linewidth=0.5)
    ax.legend()
    ax.grid(True)
    show()


def all_report():

    db_data = arcticFuturesAdjustedPricesData()
    csv_data = csvFuturesSimData()

    rows = []
    for instr in db_data.get_list_of_instruments():
        if instr in csv_data.get_instrument_list():
            rows.append(correlation_data(instr, db_data, csv_data))
        else:
            print(f"No CSV data for {instr}")

    results = pd.DataFrame(rows)
    results["Diff"] = abs(results["StartCSV"] - results["StartDB"])
    results = results.sort_values(
        by="ReturnsCorr"
    )  # PriceCorr, ReturnsCorr, StartDB, Diff

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 2000)
    pd.set_option("display.max_colwidth", None)
    print(f"\n{results}\n")


if __name__ == "__main__":

    # correlation_data("MXP", draw=True)
    # correlation_data("CAD", draw=True)
    # correlation_data("CHF", draw=True)
    # correlation_data("RUSSELL", draw=True)
    # correlation_data("US30", draw=True)
    # correlation_data("NIKKEI", draw=True)
    # correlation_data("SP400", draw=True)
    # correlation_data("LEANHOG", draw=True)
    # correlation_data("EUR", draw=True)
    # correlation_data("LIVECOW", draw=True)
    # correlation_data("OATIES", draw=True)
    # correlation_data("US10", draw=True)
    # correlation_data("CAC", draw=True)
    # correlation_data("DAX", draw=True)
    # correlation_data("DOW", draw=True)
    # correlation_data("BITCOIN", draw=True)
    # correlation_data("AUD", draw=True)
    # correlation_data("RICE", draw=True)
    # correlation_data("GOLD_micro", draw=True)
    # correlation_data("GASOILINE", draw=True)
    # correlation_data("US10U", draw=True)
    correlation_data("EURIBOR", draw=True)
    # all_report()

    # defo needs re-importing
    # 'MXP', 'CHF', 'CAD', 'LEANHOG', 'EUR', 'AUD'

    # maybe, try
    # LIVECOW, GASOILINE
