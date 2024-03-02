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

    norgate_data = csvFuturesSimData(
        csv_data_paths=dict(
            csvFuturesMultiplePricesData="/Users/ageach/Documents/backup/pst_caleb/csv/backups_csv/multiple_prices",
            csvFuturesAdjustedPricesData="/Users/ageach/Documents/backup/pst_caleb/csv/backups_csv/adjusted_prices",
        )
    )
    import_config = build_import_config(instr)

    fsb_df = fsb_data.db_futures_adjusted_prices_data.get_adjusted_prices(instr)
    fut_code = remove_suffix(instr, "_fsb")
    fut_df = fut_data.db_futures_adjusted_prices_data.get_adjusted_prices(fut_code)
    nor_df = norgate_data.db_futures_adjusted_prices_data.get_adjusted_prices(fut_code)
    fsb_df = fsb_df.div(import_config.apply_multiplier)

    if draw:
        plt.title(f"FSB v Future adjusted prices for {instr}")
        plt.plot(fsb_df["2000-01-01":], label="FSB")
        plt.plot(fut_df["2000-01-01":], label="Future")
        plt.plot(nor_df["2000-01-01":], label="Norgate")
        plt.legend()
        show()


if __name__ == "__main__":
    compare_adjusted_prices("DOW_fsb", draw=True)
