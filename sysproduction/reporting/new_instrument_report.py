from systems.provided.futures_chapter15.basesystem import *
from systems.futures_spreadbet.fsb_static_system import *
from syscore.pdutils import print_full
from sysdata.sim.db_futures_sim_data import dbFuturesSimData
import matplotlib
from matplotlib.pyplot import show
import pandas as pd

DEPOSIT_FACTOR_MAP = {
    "Equity": 0.1,
    "Bond": 0.2,
    "FX": 0.05,
    "Metals": 0.1,
    "OilGas": 0.1,
    "Ags": 0.1,
}


def run_new_instrument_report(instr_code, print=True):

    system = fsb_static_system()
    #system = fsb_static_system(data=dbFuturesSimData())
    #system.config.instrument_weights=dict(instr_code=1.0)
    system.config.risk_overlay=arg_not_supplied
    system.config.instrument_weights=dict()
    system.config.instrument_weights[instr_code] = 1.0
    #system.config.instrument_div_multiplier = 1.0
    metadata = system.data.get_instrument_meta_data(instr_code)
    raw_price = system.data.get_raw_price(instr_code)
    raw_carry = system.data.get_instrument_raw_carry_data(instr_code)
    raw_cost = system.data.get_raw_cost_data(instr_code)
    spread = raw_cost.price_slippage * 2
    min_bet = metadata.meta_data.Pointsize
    asset_class = metadata.meta_data.AssetClass
    deposit_factor = DEPOSIT_FACTOR_MAP[asset_class]
    min_capital = min_bet * raw_price * deposit_factor

    #system.rules.get_raw_forecast("DOW_fsb", "ewmac64_256").plot()
    #system.rules.get_raw_forecast("DOW_fsb", "carry").plot()
    #system.combForecast.get_combined_forecast("DOW_fsb").plot()
    #system.positionSize.get_subsystem_position("DOW_fsb").plot()

    vol_scalar = system.positionSize.get_volatility_scalar(instr_code)

    cost_per_trade = system.accounts.get_SR_cost_per_trade_for_instrument(instr_code)
    #system.accounts.pandl_for_instrument(instr_code).curve().plot()

    turnover = system.accounts.subsystem_turnover(instr_code)
    sr_cost = system.accounts.get_SR_cost_given_turnover(instr_code, turnover)
    pandl = system.accounts.pandl_for_subsystem(instr_code)
    #system.accounts.pandl_for_subsystem(instr_code).plot()
    # sharpe
    sharpe = system.accounts.portfolio().sharpe()
    costs_as_percent = (sr_cost / sharpe) * 100
    below_speed_limit = sr_cost < sharpe * 0.3333

    results = dict(
        Instrument=instr_code,
        Asset_class=asset_class,
        Price=round(raw_price.iloc[-1], 2),
        Spread=spread,
        Min_bet=min_bet,
        Deposit_factor=deposit_factor,
        Capital_required=round(min_capital.iloc[-1], 2),
        Volatility_scalar=round(vol_scalar.iloc[-1], 2),
        Cost_per_trade=round(cost_per_trade, 4),
        Turnover=round(turnover, 2),
        Sharpe=round(sharpe, 2),
        SR_cost=round(sr_cost, 3),
        Costs_percent=round(costs_as_percent, 2),
        Below_speed_limit=below_speed_limit,
    )

    if print:
        print(f"New instrument report for {instr_code}\n\n")
        for key, value in results.items():
            print(f"{key}: {value}")

    return results


def multi_instrument_report():
    rows = []
    instr_list = ["BUXL_fsb","CAD_fsb","CRUDE_W_fsb","EUROSTX_fsb","GOLD_fsb","NASDAQ_fsb","NZD_fsb","US10_fsb",
                  "BTP_fsb","DOW_fsb","COFFEE_fsb","EUR_fsb","GILT_fsb","JPY_fsb","NIKKEI_fsb","SOYOIL_fsb"]

    for instr in instr_list:
        rows.append(run_new_instrument_report(instr, print=False))

    results = pd.DataFrame(rows)
    results = results.sort_values(by="Costs_percent")  # Ctotal, NMinCap

    print(f"\n{print_full(results)}\n")


if __name__ == "__main__":
    #run_new_instrument_report("JPY_fsb")

    multi_instrument_report()