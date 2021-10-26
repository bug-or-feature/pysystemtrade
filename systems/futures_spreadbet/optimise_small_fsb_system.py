from copy import copy
import yaml
import os
import os.path
from sysquant.estimators.correlations import correlationEstimate
from sysquant.optimisation.optimisers.handcraft import *
from sysquant.estimators.estimates import Estimates, meanEstimates, stdevEstimates
from sysquant.optimisation.shared import neg_SR
from syscore.dateutils import WEEKS_IN_YEAR
from systems.futures_spreadbet.fsb_system import fsb_system
from systems.futures_spreadbet.run_system import calc_forecasts
from syscore.fileutils import get_filename_for_package
from sysdata.config.production_config import Config

## THIS MIGHT NEED TWEAKING, DEPENDING ON CAPITAL
max_instrument_weight = 0.33

notional_starting_IDM = 1.0
minimum_instrument_weight_idm = max_instrument_weight * notional_starting_IDM


def optimise():
    ignore = config_from_file("systems.futures_spreadbet.ignore.yaml")
    rules = config_from_file("systems.futures_spreadbet.rules2.yaml")
    capital = config_from_file("systems.futures_spreadbet.capital.yaml")
    config = Config([rules, capital, ignore])
    system = fsb_system(config=config)
    system.set_logging_level("on")

    find_best_ordered_set_of_instruments(system, 50000)
    #do_simple_iter(system, capital=50000)


def do_simple_iter(system, capital=500000):

    system.config.notional_trading_capital = capital
    system.config.forecast_post_ceiling_cost_SR = 1.0
    system.config.instrument_correlation_estimate['floor_at_zero'] = False

    results = []
    for instr in system.portfolio.get_instrument_list():
        avg_pos = system.positionSize.get_volatility_scalar(instr).iloc[-1]
        max_pos = calculate_maximum_position(system, instr, 0.1)
        cost = calculate_trading_cost(system, instr)
        net_sr = net_SR_for_instrument(instr, max_pos, cost, notional_SR=0.5)
        results.append((instr, avg_pos, max_pos, cost, net_sr))

    results = sorted(results, key=lambda tup: tup[4], reverse=True)
    #results.sort(key=operator.itemgetter(1, 2))
    for tup2 in results:
        print(f"{tup2[0]}: "
              f"avg_pos: {round(tup2[1],3)}, "
              f"max_pos: {round(tup2[2],3)}, "
              f"cost: {round(tup2[3],3)}, "
              f"net_sr: {round(tup2[4],3)}")


def find_best_ordered_set_of_instruments(system, capital=500000) -> list:

    # TODO figure out how to do this
    # 'system' can be precalculated up to the combined forecast stage to save time

    system.config.notional_trading_capital = capital
    system.config.forecast_post_ceiling_cost_SR = 1.0
    system.config.instrument_correlation_estimate['floor_at_zero'] = False

    list_of_instruments = system.portfolio.get_instrument_list(for_instrument_weights=True)

    calc_forecasts(system)

    list_of_correlations = system.portfolio.get_instrument_correlation_matrix()
    corr_matrix = list_of_correlations.corr_list[-1]

    best_market = find_best_market(system=system)
    set_of_instruments_used = [best_market]

    unused_list_of_instruments = copy(list_of_instruments)
    unused_list_of_instruments.remove(best_market)

    portfolio_sizes_dict = {}
    max_SR = 0.0
    while len(unused_list_of_instruments) > 0:
        new_SR, selected_market, sizes_dict = find_next_instrument(
            system,
            unused_list_of_instruments = unused_list_of_instruments,
            set_of_instruments_used=set_of_instruments_used,
            corr_matrix=corr_matrix,
            sizes_dict=portfolio_sizes_dict)

        if (new_SR) < (max_SR * 0.9):
            print("PORTFOLIO TOO BIG! SR falling")
            break
        portfolio_size_with_market = portfolio_sizes_dict[selected_market]
        print("Portfolio %s SR %.2f" % (str(set_of_instruments_used), new_SR))
        print(str(portfolio_size_with_market))

        set_of_instruments_used.append(selected_market)
        unused_list_of_instruments.remove(selected_market)
        if new_SR > max_SR:
            max_SR = new_SR

    return set_of_instruments_used


def find_best_market(system) -> str:

    list_of_instruments = system.get_instrument_list()

    all_results = []
    for instrument_code in list_of_instruments:
        all_results.append((
            instrument_code,
            net_SR_for_instrument_in_system(
                system,
                instrument_code,
                instrument_weight_idm=minimum_instrument_weight_idm)))

    all_results = sorted(all_results, key=lambda tup: tup[1])

    best_market = all_results[-1][0]

    #return best_market
    return 'GOLD'


def find_next_instrument(system,
    unused_list_of_instruments: list,
    set_of_instruments_used: list,
    corr_matrix: correlationEstimate,
        sizes_dict: dict):

    SR_list = []

    for instrument_code in unused_list_of_instruments:
        instrument_list = set_of_instruments_used + [instrument_code]

        portfolio_sizes, SR_this_instrument = SR_for_instrument_list(
            system,
            corr_matrix=corr_matrix,
            instrument_list=instrument_list)
        SR_list.append((instrument_code, SR_this_instrument))
        sizes_dict[instrument_code] = portfolio_sizes

    SR_list = sorted(SR_list, key=lambda tup: tup[1])
    selected_market = SR_list[-1][0]
    new_SR = SR_list[-1][1]

    return new_SR, selected_market, sizes_dict

def SR_for_instrument_list(system, corr_matrix, instrument_list):

    estimates = build_estimates(instrument_list=instrument_list, corr_matrix=corr_matrix)

    handcraft_portfolio = handcraftPortfolio(estimates)
    risk_weights = handcraft_portfolio.risk_weights()

    SR = estimate_SR_given_weights(system=system,
                                   risk_weights=risk_weights,
                                   handcraft_portfolio=handcraft_portfolio)

    portfolio_sizes = estimate_portfolio_sizes_given_weights(system,
                                                      risk_weights=risk_weights,
                                                      handcraft_portfolio=handcraft_portfolio)

    return portfolio_sizes, SR


def build_estimates(instrument_list, corr_matrix, notional_years_data=30):

    ## We don't take SR into account
    mean_estimates = meanEstimates(dict([
        (instrument_code, 1.0)
        for instrument_code in instrument_list
    ]))

    stdev_estimates = stdevEstimates(dict([
        (instrument_code, 1.0) for instrument_code in instrument_list
    ]))

    estimates = Estimates(correlation=corr_matrix.subset(instrument_list),
                          mean=mean_estimates,
                          stdev=stdev_estimates,
                          frequency="W",
                          data_length=notional_years_data * WEEKS_IN_YEAR)

    return estimates


def estimate_SR_given_weights(system, risk_weights, handcraft_portfolio: handcraftPortfolio):
    instrument_list = list(risk_weights.keys())

    mean_estimates = mean_estimates_from_SR_function_actual_weights(system,
                                                                    risk_weights=risk_weights,
                                                                    handcraft_portfolio=handcraft_portfolio)

    wt = np.array(risk_weights.as_list_given_keys(instrument_list))
    mu = np.array(mean_estimates.list_in_key_order(instrument_list))
    cm = handcraft_portfolio.estimates.correlation_matrix

    SR = -neg_SR(wt, cm, mu)

    return SR


def mean_estimates_from_SR_function_actual_weights(system, risk_weights, handcraft_portfolio: handcraftPortfolio):
    instrument_list = list(risk_weights.keys())
    actual_idm = min(2.5, handcraft_portfolio.div_mult(risk_weights))
    mean_estimates = meanEstimates(dict([
        (instrument_code, net_SR_for_instrument_in_system(system, instrument_code,
                                                          instrument_weight_idm=actual_idm * risk_weights[instrument_code]))
        for instrument_code in instrument_list
    ]))

    return mean_estimates


def estimate_portfolio_sizes_given_weights(system, risk_weights, handcraft_portfolio: handcraftPortfolio):
    instrument_list = list(risk_weights.keys())
    idm = handcraft_portfolio.div_mult(risk_weights)

    portfolio_sizes = dict([
        (instrument_code,
         round(calculate_maximum_position(system,
                                          instrument_code,
                                          instrument_weight_idm=risk_weights[instrument_code] * idm), 1))
        for instrument_code in instrument_list
    ])

    return portfolio_sizes


def net_SR_for_instrument_in_system(system, instrument_code, instrument_weight_idm=0.25):

    if instrument_weight_idm == 0:
        return 0.0

    if instrument_weight_idm > minimum_instrument_weight_idm:
        instrument_weight_idm = copy(minimum_instrument_weight_idm)

    maximum_pos_final = calculate_maximum_position(system, instrument_code, instrument_weight_idm=instrument_weight_idm)
    trading_cost = calculate_trading_cost(system, instrument_code)

    return net_SR_for_instrument(instrument_code, maximum_position=maximum_pos_final, trading_cost=trading_cost)


def calculate_maximum_position(system, instrument_code, instrument_weight_idm=0.25):
    pos_at_average = system.positionSize.get_volatility_scalar(instrument_code)
    pos_at_average_in_system = pos_at_average * instrument_weight_idm
    forecast_multiplier = system.combForecast.get_forecast_cap() / system.positionSize.avg_abs_forecast()

    maximum_pos_final = pos_at_average_in_system.iloc[-1] * forecast_multiplier

    return maximum_pos_final


def calculate_trading_cost(system, instrument_code):
    turnover = system.accounts.subsystem_turnover(instrument_code)
    #SR_cost_per_trade = system.accounts.get_SR_cost_per_trade_for_instrument(instrument_code)
    #trading_cost = turnover * SR_cost_per_trade
    total_cost = system.accounts.get_SR_cost_given_turnover(instrument_code, turnover)
    return total_cost


def net_SR_for_instrument(instr_code, maximum_position, trading_cost, notional_SR=0.5, cost_multiplier=1.0):
    return notional_SR - (trading_cost * cost_multiplier) - size_penalty(instr_code, maximum_position)
    #return notional_SR - (trading_cost * cost_multiplier)


def size_penalty(instr_code, maximum_position):
    if maximum_position < 0.5:
        print(f"{instr_code} size penalty awarded")
        return 9999

    return 0.125 / maximum_position ** 2
    #return 0.25 / maximum_position ** 2


def cost_penalty(instr_code, trading_cost):
    if trading_cost > 0.08:
        print(f"{instr_code} cost penalty awarded")
        return 9999
    return trading_cost

def config_from_file(path_string):
    path = get_filename_for_package(path_string)
    with open(path) as file_to_parse:
        config_dict = yaml.load(file_to_parse, Loader=yaml.CLoader)
    return config_dict

if __name__ == "__main__":
    optimise()