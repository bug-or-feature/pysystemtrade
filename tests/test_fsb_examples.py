import pytest

from syscore.constants import arg_not_supplied
from sysdata.config.configdata import Config
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from systems.accounts.accounts_stage import Account
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.forecasting import Rules
from systems.portfolio import Portfolios
from systems.positionsizing import PositionSizing
from systems.provided.rules.ewmac import ewmac_forecast_with_defaults as ewmac
from systems.rawdata import RawData
from systems.trading_rules import TradingRule


@pytest.fixture()
def data():
    data = csvFuturesSimData(
        csv_data_paths=dict(
            csvFuturesInstrumentData="data.futures_spreadbet.csvconfig",
            csvRollParametersData="data.futures_spreadbet.csvconfig",
            csvFxPricesData="data.futures.fx_prices_csv",
            csvFuturesMultiplePricesData="data.futures_spreadbet.multiple_prices_csv",
            csvFuturesAdjustedPricesData="data.futures_spreadbet.adjusted_prices_csv",
        )
    )
    return data


@pytest.fixture()
def raw_data():
    return RawData()


@pytest.fixture()
def ewmac_8():
    return TradingRule((ewmac, [], dict(Lfast=8, Lslow=32)))


@pytest.fixture()
def ewmac_32():
    return TradingRule(dict(function=ewmac, other_args=dict(Lfast=32, Lslow=128)))


@pytest.fixture()
def my_rules(ewmac_8, ewmac_32):
    return Rules(dict(ewmac8=ewmac_8, ewmac32=ewmac_32))


@pytest.fixture()
def my_config(ewmac_8, ewmac_32):
    my_config = Config()
    my_config.trading_rules = dict(ewmac8=ewmac_8, ewmac32=ewmac_32)
    my_config.instruments = ["US10_fsb", "BUXL_fsb", "GOLD_fsb", "NASDAQ_fsb"]
    my_config.risk_overlay = arg_not_supplied
    my_config.exclude_instrument_lists = dict(
        ignore_instruments=["MILK"],
        trading_restrictions=["BUTTER"],
        bad_markets=["CHEESE"],
    )

    return my_config


@pytest.fixture()
def fcs():
    return ForecastScaleCap()


@pytest.fixture()
def combiner():
    return ForecastCombine()


@pytest.fixture()
def possizer():
    return PositionSizing()


@pytest.fixture()
def account():
    return Account()


@pytest.fixture()
def portfolio():
    return Portfolios()


class TestFsbExamples:
    def test_fsb_system_rules(self, data, raw_data):
        """
        TODO
        """

        my_rules = Rules(ewmac)
        print(my_rules.trading_rules())

        my_rules = Rules(dict(ewmac=ewmac))
        print(my_rules.trading_rules())

        my_system = System([my_rules, raw_data], data)
        print(my_system)
        print(my_system.rules.get_raw_forecast("BUXL_fsb", "ewmac").tail(5))

    def test_fsb_system_trading_rule(self, data, raw_data, ewmac_8, ewmac_32):

        ewmac_rule = TradingRule(ewmac)
        my_rules = Rules(dict(ewmac=ewmac_rule))
        print(ewmac_rule)

        my_rules = Rules(dict(ewmac8=ewmac_8, ewmac32=ewmac_32))
        print(my_rules.trading_rules()["ewmac32"])

        my_system = System([my_rules, raw_data], data)
        my_system.rules.get_raw_forecast("BUXL_fsb", "ewmac32").tail(5)

    def test_fsb_system_trading_rules_estimated(
        self, data, raw_data, ewmac_8, ewmac_32, fcs
    ):

        my_rules = Rules(dict(ewmac8=ewmac_8, ewmac32=ewmac_32))
        my_config = Config()
        print(my_config)

        empty_rules = Rules()
        my_config.trading_rules = dict(ewmac8=ewmac_8, ewmac32=ewmac_32)
        my_system = System([empty_rules, raw_data], data, my_config)
        my_system.rules.get_raw_forecast("BUXL_fsb", "ewmac32").tail(5)

        # we can estimate these ourselves
        my_config.instruments = ["US10_fsb", "BUXL_fsb", "GOLD_fsb", "NASDAQ_fsb"]
        my_config.use_forecast_scale_estimates = True

        fcs = ForecastScaleCap()
        my_system = System([fcs, my_rules, raw_data], data, my_config)
        my_config.forecast_scalar_estimate["pool_instruments"] = False
        print(
            my_system.forecastScaleCap.get_forecast_scalar("BUXL_fsb", "ewmac32").tail(
                5
            )
        )

    def test_fsb_system_trading_rules_fixed(self, data, my_rules, fcs):

        # or we can use the values from the book
        my_config = Config()
        my_config.trading_rules = dict(ewmac8=ewmac_8, ewmac32=ewmac_32)
        my_config.instruments = ["US10_fsb", "BUXL_fsb", "GOLD_fsb", "NASDAQ_fsb"]
        my_config.forecast_scalars = dict(ewmac8=5.3, ewmac32=2.65)
        my_config.use_forecast_scale_estimates = False

        my_system = System([fcs, my_rules], data, my_config)
        print(
            my_system.forecastScaleCap.get_capped_forecast("BUXL_fsb", "ewmac32").tail(
                5
            )
        )

    def test_fsb_system_combing_rules(self, data, raw_data, my_rules, my_config, fcs):

        # defaults
        combiner = ForecastCombine()
        my_system = System([fcs, my_rules, combiner, raw_data], data, my_config)
        print(my_system.combForecast.get_forecast_weights("BUXL_fsb").tail(5))
        print(
            my_system.combForecast.get_forecast_diversification_multiplier(
                "BUXL_fsb"
            ).tail(5)
        )

    @pytest.mark.slow  # will be skipped unless run with 'pytest --runslow'
    def test_fsb_system_combining_and_estimating(
        self, data, raw_data, my_rules, my_config, fcs, combiner, possizer, account
    ):

        # estimates:
        my_config.forecast_weight_estimate = dict(method="one_period")
        my_config.use_forecast_weight_estimates = True
        my_config.use_forecast_div_mult_estimates = True

        my_system = System(
            [account, fcs, my_rules, combiner, raw_data, possizer], data, my_config
        )

        # this is a bit slow, better to know what's going on
        my_system.set_logging_level("on")

        print(my_system.combForecast.get_forecast_weights("US10_fsb").tail(5))
        print(
            my_system.combForecast.get_forecast_diversification_multiplier(
                "US10_fsb"
            ).tail(5)
        )

    def test_fsb_system_combining_fixed(self, data, raw_data, my_config, fcs):

        # fixed:
        my_config.forecast_weights = dict(ewmac8=0.5, ewmac32=0.5)
        my_config.forecast_div_multiplier = 1.1
        my_config.use_forecast_weight_estimates = False
        my_config.use_forecast_div_mult_estimates = False

        empty_rules = Rules()
        combiner = ForecastCombine()
        my_system = System(
            [fcs, empty_rules, combiner, raw_data], data, my_config
        )  # no need for accounts if no estimation done
        my_system.combForecast.get_combined_forecast("BUXL_fsb").tail(5)

    def test_fsb_system_position_sizing(
        self, data, raw_data, my_rules, my_config, fcs, combiner, possizer
    ):

        # size positions
        my_config.percentage_vol_target = 25
        my_config.notional_trading_capital = 500000
        my_config.base_currency = "GBP"

        my_system = System(
            [fcs, my_rules, combiner, possizer, raw_data], data, my_config
        )

        print(my_system.positionSize.get_price_volatility("BUXL_fsb").tail(5))
        print(my_system.positionSize.get_block_value("BUXL_fsb").tail(5))
        print(my_system.positionSize.get_underlying_price("BUXL_fsb"))
        print(my_system.positionSize.get_instrument_value_vol("BUXL_fsb").tail(5))
        print(my_system.positionSize.get_volatility_scalar("BUXL_fsb").tail(5))
        print(my_system.positionSize.get_vol_target_dict())
        print(my_system.positionSize.get_subsystem_position("BUXL_fsb").tail(5))

    @pytest.mark.slow  # will be skipped unless run with 'pytest --runslow'
    def test_fsb_system_portfolio_estimated(
        self, data, raw_data, my_rules, my_config, fcs, combiner, possizer, account
    ):

        # portfolio - estimated
        portfolio = Portfolios()

        my_config.use_instrument_weight_estimates = True
        my_config.use_instrument_div_mult_estimates = True
        my_config.instrument_weight_estimate = dict(
            method="shrinkage", date_method="in_sample"
        )

        my_system = System(
            [account, fcs, my_rules, combiner, possizer, portfolio, raw_data],
            data,
            my_config,
        )

        my_system.set_logging_level("on")

        print(my_system.portfolio.get_instrument_weights().tail(5))
        print(my_system.portfolio.get_instrument_diversification_multiplier().tail(5))

    def test_fsb_system_portfolio_fixed(
        self, data, raw_data, my_rules, my_config, fcs, combiner, possizer, portfolio
    ):

        # or fixed
        my_config.use_instrument_weight_estimates = False
        my_config.use_instrument_div_mult_estimates = False
        my_config.instrument_weights = dict(
            US10_fsb=0.1, BUXL_fsb=0.4, GOLD_fsb=0.3, NASDAQ_fsb=0.2
        )
        my_config.instrument_div_multiplier = 1.5
        my_config.forecast_weights = dict(ewmac8=0.5, ewmac32=0.5)
        my_config.use_forecast_weight_estimates = False

        my_system = System(
            [fcs, my_rules, combiner, possizer, portfolio, raw_data], data, my_config
        )

        print(my_system.portfolio.get_notional_position("BUXL_fsb").tail(5))

    def test_fsb_system_costs(
        self,
        data,
        raw_data,
        my_rules,
        my_config,
        fcs,
        combiner,
        possizer,
        portfolio,
        account,
    ):

        my_config.forecast_weights = dict(ewmac8=0.5, ewmac32=0.5)
        my_config.instrument_weights = dict(
            US10_fsb=0.1, BUXL_fsb=0.4, GOLD_fsb=0.3, NASDAQ_fsb=0.2
        )

        my_system = System(
            [fcs, my_rules, combiner, possizer, portfolio, account, raw_data],
            data,
            my_config,
        )
        profits = my_system.accounts.portfolio()
        print(profits.percent.stats())

        # have costs data now
        print(profits.gross.percent.stats())
        print(profits.net.percent.stats())

    def test_fsb_system_config_object(self, data, ewmac_8, ewmac_32):

        my_config = Config(
            dict(
                trading_rules=dict(ewmac8=ewmac_8, ewmac32=ewmac_32),
                instrument_weights=dict(
                    US10_fsb=0.1, BUXL_fsb=0.4, GOLD_fsb=0.3, NASDAQ_fsb=0.2
                ),
                instrument_div_multiplier=1.5,
                forecast_scalars=dict(ewmac8=5.3, ewmac32=2.65),
                forecast_weights=dict(ewmac8=0.5, ewmac32=0.5),
                forecast_div_multiplier=1.1,
                percentage_vol_target=25.00,
                notional_trading_capital=500000,
                base_currency="GBP",
                risk_overlay=arg_not_supplied,
                exclude_instrument_lists=dict(
                    ignore_instruments=["MILK"],
                    trading_restrictions=["BUTTER"],
                    bad_markets=["CHEESE"],
                ),
            )
        )
        print(my_config)
        my_system = System(
            [
                Account(),
                Portfolios(),
                PositionSizing(),
                ForecastCombine(),
                ForecastScaleCap(),
                Rules(),
                RawData(),
            ],
            data,
            my_config,
        )
        print(my_system.portfolio.get_notional_position("BUXL_fsb").tail(5))

    def test_fsb_system_config_import(self, data):

        my_config = Config("systems.futures_spreadbet.simple_fsb_system_config.yaml")
        my_config.risk_overlay = arg_not_supplied
        my_config.exclude_instrument_lists = dict(
            ignore_instruments=["MILK"],
            trading_restrictions=["BUTTER"],
            bad_markets=["CHEESE"],
        )
        print(my_config)
        my_system = System(
            [
                Account(),
                Portfolios(),
                PositionSizing(),
                ForecastCombine(),
                ForecastScaleCap(),
                Rules(),
                RawData(),
            ],
            data,
            my_config,
        )
        print(my_system.rules.get_raw_forecast("BUXL_fsb", "ewmac32").tail(5))
        print(my_system.rules.get_raw_forecast("BUXL_fsb", "ewmac8").tail(5))
        print(
            my_system.forecastScaleCap.get_capped_forecast("BUXL_fsb", "ewmac32").tail(
                5
            )
        )
        print(my_system.forecastScaleCap.get_forecast_scalar("BUXL_fsb", "ewmac32"))
        print(my_system.combForecast.get_combined_forecast("BUXL_fsb").tail(5))
        print(my_system.combForecast.get_forecast_weights("BUXL_fsb").tail(5))

        print(my_system.positionSize.get_subsystem_position("BUXL_fsb").tail(5))

        print(my_system.portfolio.get_notional_position("BUXL_fsb").tail(5))
