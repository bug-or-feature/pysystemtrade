from systems.futures_spreadbet.fsb_static_system import *
from syscore.pdutils import print_full
import matplotlib.pyplot as plt
from matplotlib.pyplot import show
import pandas as pd
from syscore.dateutils import ROOT_BDAYS_INYEAR
from syscore.dateutils import replace_midnight_with_notional_closing_time
from sysdata.csv.csv_futures_contract_prices import (
    csvFuturesContractPriceData,
    ConfigCsvFuturesPrices,
)
from sysobjects.futures_per_contract_prices import futuresContractPrices
from sysobjects.dict_of_futures_per_contract_prices import dictFuturesContractPrices
from sysdata.config.production_config import get_production_config
from syscore.fileutils import resolve_path_and_filename_for_package
from sysinit.futures_spreadbet.barchart_futures_contract_prices import BARCHART_CONFIG

DEPOSIT_FACTOR_MAP = {
    "Ags": 0.1,
    "Bond": 0.2,
    "Equity": 0.1,
    "FX": 0.05,
    "Metals": 0.1,
    "OilGas": 0.1,
    "Vol": 0.2,
}


def process_barchart_data(instrument):
    original_close = pd.DateOffset(hours=23, minutes=0, seconds=1)
    csv_time_offset = pd.DateOffset(hours=6)
    actual_close = pd.DateOffset(hours=0, minutes=0, seconds=0)
    datapath = resolve_path_and_filename_for_package(
        get_production_config().get_element_or_missing_data("barchart_path")
    )

    csv_futures_contract_prices = csvFuturesContractPriceData(
        datapath=datapath, config=BARCHART_CONFIG
    )
    all_barchart_data_original_ts = (
        csv_futures_contract_prices.get_all_prices_for_instrument(instrument)
    )
    all_barchart_data = dict(
        [
            (
                contractid,
                index_to_closing(data, csv_time_offset, original_close, actual_close),
            )
            for contractid, data in all_barchart_data_original_ts.items()
        ]
    )

    all_barchart_data = dictFuturesContractPrices(
        [(key, futuresContractPrices(x)) for key, x in all_barchart_data.items()]
    )

    return all_barchart_data


def index_to_closing(data_object, time_offset, original_close, actual_close):
    """
    Allows us to mix daily and intraday prices and seperate if required

    If index is daily, mark to actual_close
    If index is original_close, mark to actual_close
    If index is intraday, add time_offset

    :param data_object: pd.DataFrame or Series
    :return: data_object
    """
    new_index = []
    for index_entry in data_object.index:
        # Check for genuine daily data
        new_index_entry = replace_midnight_with_notional_closing_time(
            index_entry, actual_close
        )
        new_index.append(new_index_entry)

    new_data_object = pd.DataFrame(
        data_object.values, index=new_index, columns=data_object.columns
    )
    new_data_object = new_data_object.loc[
        ~new_data_object.index.duplicated(keep="first")
    ]

    return new_data_object


def check_csv_prices(instr_code):
    barchart_data = process_barchart_data(instr_code)
    barchart_prices_final = barchart_data.final_prices()
    barchart_prices_final_as_pd = pd.concat(barchart_prices_final, axis=1)
    barchart_prices_final_as_pd.plot()
    show()


def run_new_instrument_report(instr_code, do_print=True):

    system = fsb_static_system()
    # system = fsb_static_system(data=dbFuturesSimData())
    # system.config.instrument_weights=dict(instr_code=1.0)
    system.config.risk_overlay = arg_not_supplied
    system.config.instrument_weights = dict()
    system.config.instrument_weights[instr_code] = 1.0
    # system.config.instrument_div_multiplier = 1.0
    metadata = system.data.get_instrument_meta_data(instr_code)
    raw_price = system.data.get_raw_price(instr_code)
    raw_carry = system.data.get_instrument_raw_carry_data(instr_code)
    raw_cost = system.data.get_raw_cost_data(instr_code)
    spread = raw_cost.price_slippage * 2
    min_bet = metadata.meta_data.Pointsize
    asset_class = metadata.meta_data.AssetClass
    deposit_factor = DEPOSIT_FACTOR_MAP[asset_class]

    daily_vol = system.rawdata.get_daily_percentage_volatility(instr_code).iloc[-1]
    ann_std_dev = daily_vol * ROOT_BDAYS_INYEAR

    min_exposure = min_bet * raw_price.iloc[-1]
    min_capital = min_exposure * (ann_std_dev / 100)

    # stddev = system.rawdata.get_annual_percentage_volatility(instr_code)

    vol_scalar = system.positionSize.get_volatility_scalar(instr_code)

    cost_per_trade = system.accounts.get_SR_cost_per_trade_for_instrument(instr_code)
    # system.accounts.pandl_for_instrument(instr_code).curve().plot()

    turnover = system.accounts.subsystem_turnover(instr_code)
    sr_cost = system.accounts.get_SR_cost_given_turnover(instr_code, turnover)
    pandl = system.accounts.pandl_for_subsystem(instr_code)
    # system.accounts.pandl_for_subsystem(instr_code).plot()
    # sharpe
    sharpe = system.accounts.portfolio().sharpe()
    costs_as_percent = (sr_cost / sharpe) * 100
    below_speed_limit = sr_cost < sharpe * 0.3333

    results = dict(
        Instrument=instr_code,
        Asset_class=asset_class,
        Price=round(raw_price.iloc[-1], 2),
        AnnStdDev=round(ann_std_dev, 2),
        Spread=spread,
        Min_bet=min_bet,
        Deposit_factor=deposit_factor,
        MinExposure=round(min_exposure, 2),
        Capital_required=round(min_capital, 2),
        Volatility_scalar=round(vol_scalar.iloc[-1], 2),
        Cost_per_trade=round(cost_per_trade, 4),
        Turnover=round(turnover, 2),
        Sharpe=round(sharpe, 2),
        SR_cost=round(sr_cost, 3),
        Costs_percent=round(costs_as_percent, 2),
        Below_speed_limit=below_speed_limit,
    )

    if do_print:
        print(f"New instrument report for {instr_code}\n\n")
        for key, value in results.items():
            print(f"{key}: {value}")

        do_plots(system, instr_code)

    return results


def do_plots(system, instr_code):
    fig = plt.figure(figsize=(10, 20))
    ax = fig.add_subplot(711)
    ax.set_title(f"Adjusted prices for {instr_code}")
    ax.plot(system.data.get_raw_price(instr_code))
    ax.grid(True)

    ax = fig.add_subplot(712)
    ax.set_title(f"ewmac64_256 for {instr_code}")
    ax.plot(system.rules.get_raw_forecast(instr_code, "ewmac64_256"))
    ax.grid(True)

    ax = fig.add_subplot(713)
    ax.set_title(f"carry for {instr_code}")
    ax.plot(system.rules.get_raw_forecast(instr_code, "carry"))
    ax.grid(True)

    ax = fig.add_subplot(714)
    ax.set_title(f"Combined forecast for {instr_code}")
    ax.plot(system.combForecast.get_combined_forecast(instr_code))
    ax.grid(True)

    ax = fig.add_subplot(715)
    ax.set_title(f"Subsystem position for {instr_code}")
    ax.plot(system.positionSize.get_subsystem_position(instr_code))
    ax.grid(True)

    ax = fig.add_subplot(716)
    ax.set_title(f"PnL for {instr_code}")
    ax.plot(system.accounts.pandl_for_instrument(instr_code).curve())
    ax.grid(True)

    ax = fig.add_subplot(717)
    ax.set_title(f"Subsystem PnL for {instr_code}")
    ax.plot(system.accounts.pandl_for_subsystem(instr_code))
    ax.grid(True)

    show()


def multi_instrument_report():
    rows = []
    instr_list = [
        "ASX_fsb",
        "BTP_fsb",
        "CAD_fsb",
        "COFFEE_fsb",
        "COPPER_fsb",
        "CRUDE_W_fsb",
        "DOW_fsb",
        "DX_fsb",
        "EUA_fsb",
        "EUROSTX_fsb",
        "EUR_fsb",
        "GAS_US_fsb",
        "GBP_fsb",
        "GILT_fsb",
        "HANG_fsb",
        "JGB_fsb",
        "JPY_fsb",
        "NIKKEI_fsb",
        "SILVER_fsb",
        "SOYBEAN_fsb",
        "SOYOIL_fsb",
        "US2_fsb",
        "V2X_fsb",
        "WHEAT_fsb",
    ]

    for instr in instr_list:
        rows.append(run_new_instrument_report(instr, do_print=False))

    results = pd.DataFrame(rows)
    # results = results.sort_values(by="Capital_required")
    # results = results.sort_values(by="Cost_per_trade")
    results = results.sort_values(by="Costs_percent")

    print(f"\n{print_full(results)}\n")


if __name__ == "__main__":
    # run_new_instrument_report("WHEAT_fsb")
    # multi_instrument_report()
    check_csv_prices("AEX")
