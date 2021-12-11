import click
import pandas as pd
import datetime

from sysdata.data_blob import dataBlob
from sysproduction.data.broker import dataBroker
from sysdata.mongodb.mongo_futures_instruments import mongoFuturesInstrumentData
from sysdata.mongodb.mongo_futures_contracts import mongoFuturesContractData
from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysexecution.strategies.classic_buffered_positions import orderGeneratorForBufferedPositions

MIN_BET_DEMO_OVERRIDES = {
    'CARBON': 0.5,
    'CRUDE_W': 0.5,
    'EUROSTX': 0.5,
    'GOLD': 0.5,
    'HANG': 0.5
}


@click.command()
def hello():
    click.echo('Hello!')


@click.command()
def show_optimals():

    data = dataBlob()
    data.add_class_object(mongoFuturesInstrumentData)
    data.add_class_object(mongoFuturesContractData)
    data.add_class_object(arcticFuturesAdjustedPricesData)
    broker = dataBroker(data=data)
    pos = orderGeneratorForBufferedPositions(data=data, strategy_name='fsb_strategy_v1')
    now = datetime.datetime.now()

    optimals = pos.get_optimal_positions()
    upper_positions = optimals.upper_positions
    lower_positions = optimals.lower_positions
    ref_contracts = optimals.reference_contracts

    actuals_map = {}
    for contract_pos in broker.get_all_current_contract_positions():
        actual = {
            'pos': contract_pos.position,
            'date_str': contract_pos.date_str,
            'expiry': contract_pos.expiry_date,
            'contract': contract_pos.contract
        }
        actuals_map[contract_pos.instrument_code] = actual

    rows = []
    for instr_code in upper_positions.keys():
        if instr_code in actuals_map:
            pos_data = actuals_map[instr_code]
            expiry = pos_data['expiry']
            pos = round(pos_data['pos'], 2)
        else:
            expiry_key = ref_contracts[instr_code]
            contract = data.db_futures_contract.get_contract_object(instr_code, expiry_key)
            expiry = contract.expiry_date
            pos = 0.0

        lower = round(lower_positions[instr_code], 2)
        upper = round(upper_positions[instr_code], 2)
        instr_data = data.db_futures_instrument.get_instrument_data(instr_code)
        min_bet = instr_data.as_dict()['Pointsize']
        if instr_code in MIN_BET_DEMO_OVERRIDES:
            min_bet = MIN_BET_DEMO_OVERRIDES[instr_code]
        delta = expiry - now
        price = data.db_futures_adjusted_prices.get_adjusted_prices(instr_code).values[-1]
        fut_price = data.db_futures_adjusted_prices.get_adjusted_prices(instr_code[:-4]).values[-1]
        price_date = data.db_futures_adjusted_prices.get_adjusted_prices(instr_code).index[-1]

        if pos < lower:
            required_position = lower
        elif pos > upper:
            required_position = upper
        else:
            required_position = pos

        trade_required = required_position - pos
        # if required_trade is less than minimum bet, make it zero
        if abs(trade_required) < min_bet:
            trade_required = 0.0

        rows.append(
            {
                'Instr': instr_code,
                'Expiry': f"{expiry.strftime('%Y-%m-%d')}",
                'Days': f"{delta.days}",
                'FSB date': price_date.strftime('%Y-%m-%d %H:%M:%S'),
                'FSB price': round(price, 2),
                'Fut price': round(fut_price, 2),
                'Current': pos,
                'Lower': lower,
                'Upper': upper,
                'Min': min_bet,
                'Trade': trade_required,
            }
        )

    results = pd.DataFrame(rows)
    #results = results.sort_values(by='Days to expiry')

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.max_colwidth', None)

    click.echo(results)

    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.max_colwidth')


if __name__ == '__main__':
    show_optimals()
    #show_optimals(['--my_arg', '3'])