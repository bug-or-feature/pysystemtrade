import datetime
import yaml
from matplotlib.pyplot import show
from syscore.fileutils import resolve_path_and_filename_for_package
from systems.diagoutput import systemDiag
from systems.futures_spreadbet.fsb_static_system import fsb_static_system
from syslogging.logger import get_logger
from sysdata.config.configdata import Config
from syscore.pdutils import print_full

SAVED_SYSTEM = "systems.futures_spreadbet.saved-system.pck"
# CONFIG = "systems.futures_spreadbet.config.fsb_static_system_v5_6.yaml"
# CONFIG = "systems.futures_spreadbet.config.fsb_static_minimal.yaml"
# CONFIG = "systems.futures_spreadbet.config.fsb_static_system_full_hier.yaml"
CONFIG = "systems.futures_spreadbet.config.fsb_static_system_full_est.yaml"

log = get_logger("backtest")


def run_system(
    load_pickle=False, write_pickle=False, do_estimate=False, write_config=False
):
    if load_pickle:
        log.info(f"Loading system from {SAVED_SYSTEM}")
        system = fsb_static_system()
        system.cache.get_items_with_data()
        system.cache.unpickle(SAVED_SYSTEM)
        system.cache.get_items_with_data()
        write_pickle = False
    else:
        log.info(f"Building system from {CONFIG}")
        config = Config(CONFIG)
        if do_estimate:
            config.use_forecast_div_mult_estimates = True
            config.use_instrument_div_mult_estimates = True
            config.use_forecast_weight_estimates = True
            config.use_instrument_weight_estimates = True
            config.use_forecast_scale_estimates = True
        system = fsb_static_system(config=config)

    # acc_portfolio = system.accounts.portfolio()
    acc_portfolio = system.accounts.portfolio(roundpositions=False)
    # acc_portfolio_percent = system.accounts.portfolio().percent
    acc_portfolio_percent = system.accounts.portfolio(roundpositions=False).percent

    # weights_df = system.portfolio.get_instrument_weights()
    # weights = weights_df.iloc[-1]
    # print_full(weights_df)

    # for instr in system.get_instrument_list():
    #     cf = round(system.combForecast.get_combined_forecast(instr)[-1], 2)
    #     sub_pos = round(system.positionSize.get_subsystem_position(instr)[-1], 2)
    #     not_pos = round(system.portfolio.get_notional_position(instr)[-1], 2)
    #     act_pos = round(system.portfolio.get_actual_position(instr)[-1], 2)
    #     buffer = round(system.portfolio.get_buffers(instr).iloc[-1], 3)
    #     pos_buffers = system.portfolio.get_buffers_for_position(instr).iloc[-1]
    #     top = round(pos_buffers["top_pos"], 2)
    #     bot = round(pos_buffers["bot_pos"], 2)
    #     print(
    #         f"{instr=}: {cf=}, {sub_pos=}, {not_pos=}, {act_pos=}, {buffer=}, {bot=}, {top=}"
    #     )

    # pos = system.portfolio.get_notional_position("DOW_fsb")
    # system.accounts.pandl_for_instrument("DOW_fsb").curve().plot(legend=True)
    # show()
    # system.accounts.pandl_for_instrument("HANG_fsb").curve().plot(legend=True)
    # show()
    # system.accounts.pandl_for_instrument("LEANHOG_fsb").curve().plot(legend=True)
    # show()
    # system.accounts.pandl_for_instrument("US30_fsb").curve().plot(legend=True)
    # show()
    # log.info(f"pos: {pos}")

    # forecast_sc = system.forecastScaleCap
    # comb_forecast = system.combForecast
    # positions = system.positionSize
    # portfolio = system.portfolio
    # accounts = system.accounts

    log.info(f"Stats: {acc_portfolio_percent.stats()}")
    log.info(f"Stats as %: {acc_portfolio_percent.stats()}\n")

    # acc_portfolio.curve().plot(legend=True)
    # show()
    # acc_pf_nr.curve().plot()
    acc_portfolio_percent.curve().plot(legend=True)
    show()

    # for instr in system.portfolio.get_instrument_list(
    #     for_instrument_weights=True, auto_remove_bad_instruments=True
    # ):
    # for instr in [
    #     "BTP_fsb",
    #     "DOW_fsb",
    #     "EUA_fsb",
    #     "EUR_fsb",
    #     "GOLD_fsb",
    #     "LEANHOG_fsb",
    #     "ROBUSTA_fsb",
    # ]:
    # instr_pnl = system.accounts.pandl_for_instrument(instr, roundpositions=False)
    # instr_pnl = system.accounts.pandl_for_instrument(instr)
    # system.accounts.pandl_across_subsystems(instr, roundpositions=False).plot(
    # system.accounts.pandl_for_subsystem(instr, roundpositions=False).plot(
    #     title=instr
    # )
    # show()
    # system.accounts.pandl_for_instrument(instr, roundpositions=False)
    # ss_pnl = system.accounts.pandl_for_subsystem(instr)
    # print(f"{instr}: {instr_pnl.stats()}")
    # print(f"{instr}: {instr_pnl.sharpe()}")

    if write_pickle:
        write_pickle_file(system)
    if do_estimate:
        write_estimate_file(system)
    if write_config:
        write_full_config_file(system)

    return system


def write_pickle_file(system):
    # now = datetime.datetime.now()
    # #f = open("/home/rob/temp.pck", "wb")
    # pickle_file = open(f"systems.futures_spreadbet.system-{now.strftime('%Y-%m-%d_%H%M%S')}.pck", "wb")
    # pickle.dump(all_pandl, pickle_file)
    # pickle_file.close()
    log.info(f"Writing pickled system to {SAVED_SYSTEM}")
    system.cache.pickle(SAVED_SYSTEM)


def write_estimate_file(system):
    now = datetime.datetime.now()
    sysdiag = systemDiag(system)
    output_file = resolve_path_and_filename_for_package(
        f"systems.futures_spreadbet.estimate-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    print(f"writing estimate params to: {output_file}")
    estimates_needed = [
        "instrument_div_multiplier",
        "forecast_div_multiplier",
        "forecast_scalars",
        "instrument_weights",
        "forecast_weights",
        # "forecast_mapping",
    ]

    sysdiag.yaml_config_with_estimated_parameters(output_file, estimates_needed)


def write_full_config_file(system):
    now = datetime.datetime.now()
    output_file = resolve_path_and_filename_for_package(
        f"systems.futures_spreadbet.full_config-{now.strftime('%Y-%m-%d_%H%M%S')}.yaml"
    )
    print(f"writing config to: {output_file}")
    system.config.save(output_file)


def config_from_file(path_string):
    path = resolve_path_and_filename_for_package(path_string)
    with open(path) as file_to_parse:
        config_dict = yaml.load(file_to_parse, Loader=yaml.CLoader)
    return config_dict


if __name__ == "__main__":
    # run_system(load_pickle=True)
    # run_system()
    # run_system(do_estimate=True)
    run_system(
        load_pickle=False, write_pickle=False, do_estimate=False, write_config=False
    )
