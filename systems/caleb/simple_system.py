from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from systems.provided.futures_chapter15.basesystem import futures_system
from sysdata.config.production_config import Config
from matplotlib.pyplot import show

system = futures_system(
    data=csvFuturesSimData(
        csv_data_paths=dict(
            csvFxPricesData="data.futures_cj.fx_prices_csv",
            csvFuturesMultiplePricesData="data.futures_cj.multiple_prices_csv",
            csvFuturesAdjustedPricesData="data.futures_cj.adjusted_prices_csv",
        )
    ),
    config=Config("systems.caleb.simple_strategy.yaml")
)

print(system)



def pandl_for_instrument_rules():

    system.config.start_date = "2010-01-01"

    # how all trading rules have done for a particular instrument (returns accountCurveGroup)
    acc_curve_group = system.accounts.pandl_for_instrument_rules("SP500")
    print(f"percentage stats: {acc_curve_group.percent.stats()}")
    print(f"Get a list of methods. equivalent to acc_curve.gross.stats(): {acc_curve_group.gross.daily.stats()}")
    print(f"Sharpe ratio based on annual: {acc_curve_group.annual.sharpe()}")
    print(f"standard deviation of weekly returns: {acc_curve_group.gross.weekly.std()}")
    print(f"annualised std. deviation of daily (net) returns: {acc_curve_group.daily.ann_std()}")
    print(f"median of annual costs: {acc_curve_group.costs.annual.median()}")

    print(f"asset columns: {acc_curve_group.asset_columns}")
    print(f"list of methods: {acc_curve_group['momentum16'].gross.daily.stats()}")
    print(f"Sharpe ratio based on annual: {acc_curve_group['accel32'].annual.sharpe()}")
    print(f"standard deviation of weekly returns: {acc_curve_group['assettrend8'].gross.weekly.std()}")
    print(f"annualised std. deviation of daily (net) returns: {acc_curve_group['carry30'].daily.ann_std()}")
    print(f"median of annual costs: {acc_curve_group['mrinasset160'].costs.annual.median()}")


if __name__ == "__main__":
    pandl_for_instrument_rules()
