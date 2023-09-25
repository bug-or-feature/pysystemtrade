from matplotlib.pyplot import show
import matplotlib.pyplot as plt

from syscore.text import remove_suffix
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysinit.futures_spreadbet.fsb_contract_prices import (
    build_import_config,
)


def compare_adjusted_prices(instr, draw=False):
    fsb_data = csvFuturesSimData(
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
            csvFxPricesData="data.futures.fx_prices_csv",
            csvFuturesMultiplePricesData="fsb.multiple_prices_csv",
            csvFuturesAdjustedPricesData="fsb.adjusted_prices_csv",
        )
    )

    fut_data = csvFuturesSimData()
    fut_code = remove_suffix(instr, "_fsb")
    import_config = build_import_config(instr)

    fsb_df = fsb_data.db_futures_adjusted_prices_data.get_adjusted_prices(instr)
    fut_df = fut_data.db_futures_adjusted_prices_data.get_adjusted_prices(fut_code)
    fsb_df = fsb_df.div(import_config.apply_multiplier)

    if draw:
        plt.title(f"FSB v Future adjusted prices for {instr}")
        plt.plot(fsb_df, label="FSB")
        plt.plot(fut_df, label="Future")
        plt.legend()
        show()


if __name__ == "__main__":
    compare_adjusted_prices("CRUDE_W_fsb", draw=True)
