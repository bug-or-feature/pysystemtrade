import datetime
from sysdata.config.configdata import Config
from sysdata.config.control_config import get_control_config
from sysdata.config.private_config import PRIVATE_CONFIG_DIR_ENV_VAR
from sysbrokers.IB.ib_trading_hours import get_saved_trading_hours


class TestConfig:
    def test_init_dict(self, monkeypatch):
        monkeypatch.delenv(PRIVATE_CONFIG_DIR_ENV_VAR, raising=False)
        config = Config(dict(parameters=dict(p1=3, p2=4.6), another_thing="foo"))
        assert config.as_dict()["parameters"]["p2"] == 4.6
        assert config.as_dict()["another_thing"] == "foo"

    def test_init_str(self, monkeypatch):
        monkeypatch.delenv(PRIVATE_CONFIG_DIR_ENV_VAR, raising=False)
        config = Config("systems.provided.example.exampleconfig.yaml")
        assert config.as_dict()["forecast_cap"] == 21.0

    def test_init_list(self, monkeypatch):
        monkeypatch.delenv(PRIVATE_CONFIG_DIR_ENV_VAR, raising=False)
        config = Config(
            [
                "systems.provided.example.exampleconfig.yaml",
                dict(parameters=dict(p1=3, p2=4.6), another_thing="foo"),
            ]
        )
        assert config.as_dict()["forecast_cap"] == 21.0
        assert config.as_dict()["parameters"]["p2"] == 4.6
        assert config.as_dict()["another_thing"] == "foo"

    def test_default(self, monkeypatch):
        monkeypatch.delenv(PRIVATE_CONFIG_DIR_ENV_VAR, raising=False)
        Config.reset()
        config = Config.default_config()
        assert config.get_element("ib_idoffset") == 100

    def test_custom_dir(self, monkeypatch):
        monkeypatch.setenv(
            PRIVATE_CONFIG_DIR_ENV_VAR, "sysdata.tests.custom_private_config"
        )

        Config.reset()
        config = Config.default_config()
        assert config.get_element("ib_idoffset") == 1000

    def test_bad_custom_dir(self, monkeypatch):
        monkeypatch.setenv(PRIVATE_CONFIG_DIR_ENV_VAR, "sysdata.tests")

        Config.reset()
        config = Config.default_config()
        assert config.get_element("ib_idoffset") == 100

    def test_default_control(self, monkeypatch):
        monkeypatch.delenv(PRIVATE_CONFIG_DIR_ENV_VAR, raising=False)
        Config.reset()
        config = get_control_config()
        assert (
            config.as_dict()["process_configuration_start_time"]["run_stack_handler"]
            == "00:01"
        )

    def test_control_custom_dir(self, monkeypatch):
        monkeypatch.setenv(
            PRIVATE_CONFIG_DIR_ENV_VAR, "sysdata.tests.custom_private_config"
        )

        config = get_control_config()
        assert (
            config.as_dict()["process_configuration_start_time"]["run_stack_handler"]
            == "01:00"
        )

    def test_control_bad_custom_dir(self, monkeypatch):
        monkeypatch.setenv(PRIVATE_CONFIG_DIR_ENV_VAR, "sysdata.tests")

        config = get_control_config()
        assert (
            config.as_dict()["process_configuration_start_time"]["run_stack_handler"]
            == "00:01"
        )

    def test_trading_hours_default(self, monkeypatch):
        monkeypatch.delenv(PRIVATE_CONFIG_DIR_ENV_VAR, raising=False)
        config = get_saved_trading_hours()
        assert config["MET"]["Monday"][0].closing_time == datetime.time(15)

    def test_trading_hours_custom(self, monkeypatch):
        monkeypatch.setenv(
            PRIVATE_CONFIG_DIR_ENV_VAR, "sysdata.tests.custom_private_config"
        )
        config = get_saved_trading_hours()
        assert config["MET"]["Monday"][0].opening_time == datetime.time(9)
        assert config["MET"]["Monday"][0].closing_time == datetime.time(14)

    def test_trading_hours_bad_custom_dir(self, monkeypatch):
        monkeypatch.setenv(PRIVATE_CONFIG_DIR_ENV_VAR, "sysdata.tests")
        config = get_saved_trading_hours()
        assert config["MET"]["Monday"][0].closing_time == datetime.time(15)
