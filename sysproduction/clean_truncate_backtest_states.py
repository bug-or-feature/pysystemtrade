from syscore.fileutils import delete_old_files_with_extension_in_pathname
from sysproduction.data.backtest import get_directory_store_backtests
from sysdata.config.production_config import get_production_config
from sysdata.data_blob import dataBlob


def clean_truncate_backtest_states():
    data = dataBlob()
    cleaner = cleanTruncateBacktestStates(data)
    cleaner.clean_backtest_states()

    return None


class cleanTruncateBacktestStates:
    def __init__(self, data: dataBlob):
        self.data = data

    def clean_backtest_states(self):
        directory_to_use = get_directory_store_backtests()
        max_age = get_production_config().get_element("backtest_max_age")

        self.data.log.debug(
            "Deleting old .pck and .yaml backtest state files in directory %s"
            % directory_to_use
        )
        delete_old_files_with_extension_in_pathname(
            directory_to_use, days_old=max_age, extension=".pck"
        )
        delete_old_files_with_extension_in_pathname(
            directory_to_use, days_old=max_age, extension=".pckz"
        )
        delete_old_files_with_extension_in_pathname(
            directory_to_use, days_old=max_age, extension=".yaml"
        )


if __name__ == "__main__":
    clean_truncate_backtest_states()
