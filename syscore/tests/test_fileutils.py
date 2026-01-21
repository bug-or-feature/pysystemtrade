import pytest
import sys
from pathlib import Path
from syscore.fileutils import (
    resolve_path_and_filename_for_package,
    get_resolved_pathname,
)


@pytest.fixture()
def project_dir(request):
    module_path = Path(request.module.__file__)
    return str(module_path.parent.parent.parent.absolute())


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Only runs on unix")
class TestFileUtilsUnix:
    def test_resolve_path_absolute(self):
        actual = get_resolved_pathname("/home/rob")
        assert actual == "/home/rob"

    def test_resolve_path_absolute_trailing(self):
        actual = get_resolved_pathname("/home/rob/")
        assert actual == "/home/rob"

    def test_resolve_path_absolute_dotted(self):
        actual = get_resolved_pathname(".home.rob")
        assert actual == "/home/rob"

    def test_resolve_path_relative(self, project_dir):
        actual = get_resolved_pathname("syscore.tests")
        assert actual == f"{project_dir}/syscore/tests"

    def test_resolve_path_non_existent(self, project_dir):
        actual = get_resolved_pathname("syscore.testz")
        assert actual == f"{project_dir}/syscore/testz"

    def test_resolve_dotted_dir_name(self, tmp_path):
        directory = tmp_path / "dir.name.with.dots"
        directory.mkdir()
        file = directory / "hello.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = get_resolved_pathname(file)
        assert resolved_path == f"{tmp_path}/dir.name.with.dots/hello.txt"

    def test_resolve_dotted_file_name(self, tmp_path):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = get_resolved_pathname(file)
        assert resolved_path == f"{tmp_path}/dir_name/dotted.filename.txt"

    def test_resolve_package_separate(self):
        actual = resolve_path_and_filename_for_package("/home/rob/", "file.csv")
        assert actual == "/home/rob/file.csv"

    def test_resolve_package_combined(self):
        actual = resolve_path_and_filename_for_package("/home/rob/file.csv")
        assert actual == "/home/rob/file.csv"

    def test_resolve_package_combined_dotted(self):
        actual = resolve_path_and_filename_for_package(".home.rob.file.csv")
        assert actual == "/home/rob/file.csv"

    def test_resolve_package_module_separate(self, project_dir):
        actual = resolve_path_and_filename_for_package("syscore.tests", "file.csv")
        assert actual == f"{project_dir}/syscore/tests/file.csv"

    def test_resolve_package_module_instr_data_module(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "data.futures.csvconfig", "instrumentconfig.csv"
        )
        assert actual == f"{project_dir}/data/futures/csvconfig/instrumentconfig.csv"

    def test_resolve_package_module_combined(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscore.tests.pricetestdata.csv"
        )
        assert actual == f"{project_dir}/syscore/tests/pricetestdata.csv"

    @pytest.mark.xfail(reason="Cannot work with old or new implementation")
    def test_resolve_package_module_combined_dotted_filename(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscore.tests.price.test.data.csv"
        )
        assert actual == f"{project_dir}/syscore/tests/price.test.data.csv"

    def test_resolve_package_module_combined_dotted_filename_sep(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscore.tests", "price.test.data.csv"
        )
        assert actual == f"{project_dir}/syscore/tests/price.test.data.csv"

    @pytest.mark.xfail(reason="Cannot work with old or new implementation")
    def test_resolve_resolve_path_and_filename_for_package_with_dotted_dir_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir.name.with.dots"
        directory.mkdir()
        file = directory / "hello.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}/dir.name.with.dots", "hello.txt"
        )
        assert resolved_path == f"{tmp_path}/dir.name.with.dots/hello.txt"

    @pytest.mark.xfail(reason="Cannot work with old or new implementation")
    def test_resolve_resolve_path_and_filename_for_package_with_dotted_file_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}/dir_name/dotted.filename.txt"
        )
        assert resolved_path == f"{tmp_path}/dir_name/dotted.filename.txt"

    def test_resolve_resolve_path_and_filename_for_package_with_separate_dotted_file_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}/dir_name/", "dotted.filename.txt"
        )
        assert resolved_path == f"{tmp_path}/dir_name/dotted.filename.txt"

    # No Separate filename

    def test_csv_data(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "data.futures.csvconfig.instrumentconfig.csv"
        )
        assert actual == f"{project_dir}/data/futures/csvconfig/instrumentconfig.csv"

    def test_logging(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syslogging.logging_prod.yaml",
        )
        assert actual == f"{project_dir}/syslogging/logging_prod.yaml"

    def test_config_defaults(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysdata.config.defaults.yaml",
        )
        assert actual == f"{project_dir}/sysdata/config/defaults.yaml"

    def test_control_config_defaults(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscontrol.control_config.yaml",
        )
        assert actual == f"{project_dir}/syscontrol/control_config.yaml"

    def test_private_config_dots(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "private.private_config.yaml",
        )
        assert actual == f"{project_dir}/private/private_config.yaml"

    def test_private_config_slash(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "private/private_config.yaml",
        )
        assert actual == f"{project_dir}/private/private_config.yaml"

    def test_strategy_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "systems.provided.rob_system.config.yaml",
        )
        assert actual == f"{project_dir}/systems/provided/rob_system/config.yaml"

    def test_pickled_backtest(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "private/backtests/fut_strategy_v1_8/20260101_210632_backtest.pck",
        )
        assert (
            actual
            == f"{project_dir}/private/backtests/fut_strategy_v1_8/20260101_210632_backtest.pck"
        )

    def test_ib_instrument_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysbrokers.IB.config.ib_config_futures.csv",
        )
        assert actual == f"{project_dir}/sysbrokers/IB/config/ib_config_futures.csv"

    def test_ib_fx_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysbrokers.IB.config.ib_config_spot_FX.csv",
        )
        assert actual == f"{project_dir}/sysbrokers/IB/config/ib_config_spot_FX.csv"

    def test_ib_trading_hours_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysbrokers.IB.ib_config_trading_hours.yaml",
        )
        assert actual == f"{project_dir}/sysbrokers/IB/ib_config_trading_hours.yaml"

    def test_email_store_filename(self):
        actual = resolve_path_and_filename_for_package(
            "/home/rob/logs/email_store.log",
        )
        assert actual == "/home/rob/logs/email_store.log"


@pytest.mark.skipif(sys.platform in ["linux", "darwin"], reason="Only runs on windows")
class TestFileUtilsWindoze:
    def test_resolve_path_absolute(self):
        actual = get_resolved_pathname("C:\\home\\rob\\")
        assert actual == "C:\\home\\rob"

    def test_resolve_path_absolute_lower_case(self):
        actual = get_resolved_pathname("c:\\home\\rob\\")
        assert actual == "c:\\home\\rob"

    def test_resolve_path_absolute_trailing(self):
        actual = get_resolved_pathname("C:\\home\\rob\\")
        assert actual == "C:\\home\\rob"

    @pytest.mark.xfail(reason="A Windows absolute path needs a root AND a drive")
    def test_resolve_path_absolute_dotted(self):
        actual = get_resolved_pathname(".home.rob")
        assert actual == "\\home\\rob"

    def test_resolve_path_relative(self, project_dir):
        actual = get_resolved_pathname("syscore.tests")
        assert actual == f"{project_dir}\\syscore\\tests"

    def test_resolve_path_non_existent(self, project_dir):
        actual = get_resolved_pathname("syscore.testz")
        assert actual == f"{project_dir}\\syscore\\testz"

    def test_resolve_dotted_dir_name(self, tmp_path):
        directory = tmp_path / "dir.name.with.dots"
        directory.mkdir()
        file = directory / "hello.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = get_resolved_pathname(file)
        assert resolved_path == f"{tmp_path}\\dir.name.with.dots\\hello.txt"

    def test_resolve_dotted_file_name(self, tmp_path):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = get_resolved_pathname(file)
        assert resolved_path == f"{tmp_path}\\dir_name\\dotted.filename.txt"

    def test_resolve_package_separate(self):
        actual = resolve_path_and_filename_for_package("C:\\home\\rob\\", "file.csv")
        assert actual == "C:\\home\\rob\\file.csv"

    def test_resolve_package_combined(self):
        actual = resolve_path_and_filename_for_package("C:\\home\\rob\\file.csv")
        assert actual == "C:\\home\\rob\\file.csv"

    @pytest.mark.xfail(reason="A Windows absolute path needs a root AND a drive")
    def test_resolve_package_combined_dotted(self):
        actual = resolve_path_and_filename_for_package(".home.rob.file.csv")
        assert actual == "\\home\\rob\\file.csv"

    def test_resolve_package_module_separate(self, project_dir):
        actual = resolve_path_and_filename_for_package("syscore.tests", "file.csv")
        assert actual == f"{project_dir}\\syscore\\tests\\file.csv"

    def test_resolve_package_module_combined(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscore.tests.pricetestdata.csv"
        )
        assert actual == f"{project_dir}\\syscore\\tests\\pricetestdata.csv"

    @pytest.mark.xfail(reason="Cannot work with old or new implementation")
    def test_resolve_package_module_combined_dotted_filename(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscore.tests.price.test.data.csv"
        )
        assert actual == f"{project_dir}\\syscore\\tests\\price.test.data.csv"

    def test_resolve_package_module_combined_dotted_filename_sep(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscore.tests", "price.test.data.csv"
        )
        assert actual == f"{project_dir}\\syscore\\tests\\price.test.data.csv"

    @pytest.mark.xfail(reason="Cannot work with old or new implementation")
    def test_resolve_resolve_path_and_filename_for_package_with_dotted_dir_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir.name.with.dots"
        directory.mkdir()
        file = directory / "hello.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}\\dir.name.with.dots", "hello.txt"
        )
        assert resolved_path == f"{tmp_path}\\dir.name.with.dots\\hello.txt"

    @pytest.mark.xfail(reason="Cannot work with old or new implementation")
    def test_resolve_resolve_path_and_filename_for_package_with_dotted_file_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}\\dir_name\\dotted.filename.txt"
        )
        assert resolved_path == f"{tmp_path}\\dir_name\\dotted.filename.txt"

    def test_resolve_resolve_path_and_filename_for_package_with_separate_dotted_file_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}\\dir_name\\", "dotted.filename.txt"
        )
        assert resolved_path == f"{tmp_path}\\dir_name\\dotted.filename.txt"

    # No Separate filename

    def test_csv_data(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "data.futures.csvconfig.instrumentconfig.csv"
        )
        assert (
            actual == f"{project_dir}\\data\\futures\\csvconfig\\instrumentconfig.csv"
        )

    def test_logging(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syslogging.logging_prod.yaml",
        )
        assert actual == f"{project_dir}\\syslogging\\logging_prod.yaml"

    def test_config_defaults(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysdata.config.defaults.yaml",
        )
        assert actual == f"{project_dir}\\sysdata\\config\\defaults.yaml"

    def test_control_config_defaults(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "syscontrol.control_config.yaml",
        )
        assert actual == f"{project_dir}\\syscontrol\\control_config.yaml"

    def test_private_config_dots(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "private.private_config.yaml",
        )
        assert actual == f"{project_dir}\\private\\private_config.yaml"

    def test_private_config_slash(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "private/private_config.yaml",
        )
        assert actual == f"{project_dir}\\private\\private_config.yaml"

    def test_strategy_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "systems.provided.rob_system.config.yaml",
        )
        assert actual == f"{project_dir}\\systems\\provided\\rob_system\\config.yaml"

    def test_pickled_backtest(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "private/backtests/fut_strategy_v1_8/20260101_210632_backtest.pck",
        )
        assert (
            actual
            == f"{project_dir}\\private\\backtests\\fut_strategy_v1_8\\20260101_210632_backtest.pck"
        )

    def test_ib_instrument_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysbrokers.IB.config.ib_config_futures.csv",
        )
        assert actual == f"{project_dir}\\sysbrokers\\IB\\config\\ib_config_futures.csv"

    def test_ib_fx_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysbrokers.IB.config.ib_config_spot_FX.csv",
        )
        assert actual == f"{project_dir}\\sysbrokers\\IB\\config\\ib_config_spot_FX.csv"

    def test_ib_trading_hours_config(self, project_dir):
        actual = resolve_path_and_filename_for_package(
            "sysbrokers.IB.ib_config_trading_hours.yaml",
        )
        assert actual == f"{project_dir}\\sysbrokers\\IB\\ib_config_trading_hours.yaml"

    def test_email_store_filename(self):
        actual = resolve_path_and_filename_for_package(
            "C:\\home\\rob\\logs\\email_store.log",
        )
        assert actual == "C:\\home\\rob\\logs\\email_store.log"
