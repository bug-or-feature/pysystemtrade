import datetime

import click
import pandas as pd

from sysdata.arctic.arctic_adjusted_prices import arcticFuturesAdjustedPricesData
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysdata.data_blob import dataBlob
from sysdata.mongodb.mongo_futures_contracts import mongoFuturesContractData
from sysexecution.strategies.classic_buffered_positions import (
    orderGeneratorForBufferedPositions,
)
from sysinit.futures_spreadbet.fsb_multipleprices import (
    process_multiple_prices_single_instrument,
)
from sysinit.futures_spreadbet.fsb_rollcalendars_to_csv import (
    build_and_write_roll_calendar,
)
from sysobjects.contracts import futuresContract as fc
from sysproduction.data.broker import dataBroker
from sysproduction.data.contracts import dataContracts, get_dates_to_choose_from
from sysproduction.data.prices import (
    get_valid_instrument_code_from_user,
)
from sysexecution.strategies.fsb_buffered_positions import MIN_BET_DEMO_OVERRIDES


@click.command(name="fh")
def hello():
    """FSB hello test"""
    click.echo("Hello!")


@click.command(name="fo")
def show_optimals():
    """FSB show optimal positions (deprecated)"""
    data = dataBlob()
    data.add_class_object(csvFuturesInstrumentData)
    data.add_class_object(mongoFuturesContractData)
    data.add_class_object(arcticFuturesAdjustedPricesData)
    broker = dataBroker(data=data)
    pos = orderGeneratorForBufferedPositions(data=data, strategy_name="fsb_strategy_v3")
    now = datetime.datetime.now()

    optimals = pos.get_optimal_positions()
    upper_positions = optimals.upper_positions
    lower_positions = optimals.lower_positions
    ref_contracts = optimals.reference_contracts

    actuals_map = {}
    for contract_pos in broker.get_all_current_contract_positions():
        actual = {
            "pos": contract_pos.position,
            "date_str": contract_pos.date_str,
            "expiry": contract_pos.expiry_date,
            "contract": contract_pos.contract,
        }
        actuals_map[contract_pos.instrument_code] = actual

    rows = []
    for instr_code in upper_positions.keys():
        if instr_code in actuals_map:
            pos_data = actuals_map[instr_code]
            expiry = pos_data["expiry"]
            pos = round(pos_data["pos"], 2)
        else:
            expiry_key = ref_contracts[instr_code]
            contract = data.db_futures_contract.get_contract_object(
                instr_code, expiry_key
            )
            expiry = contract.expiry_date
            pos = 0.0

        lower = round(lower_positions[instr_code], 2)
        upper = round(upper_positions[instr_code], 2)
        instr_data = data.db_futures_instrument.get_instrument_data(instr_code)
        min_bet = instr_data.as_dict()["Pointsize"]
        if instr_code in MIN_BET_DEMO_OVERRIDES:
            min_bet = MIN_BET_DEMO_OVERRIDES[instr_code]
        delta = expiry - now
        price = data.db_futures_adjusted_prices.get_adjusted_prices(instr_code).values[
            -1
        ]
        price_date = data.db_futures_adjusted_prices.get_adjusted_prices(
            instr_code
        ).index[-1]

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
                "Instr": instr_code,
                "Expiry": f"{expiry.strftime('%Y-%m-%d')}",
                "Days": f"{delta.days}",
                "FSB date": price_date.strftime("%Y-%m-%d %H:%M:%S"),
                "FSB price": round(price, 2),
                "Current": pos,
                "Lower": lower,
                "Upper": upper,
                "Min": min_bet,
                "Trade": trade_required,
            }
        )

    results = pd.DataFrame(rows)
    # results = results.sort_values(by='Days to expiry')

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 2000)
    pd.set_option("display.max_colwidth", None)

    click.echo(results)

    pd.reset_option("display.max_columns")
    pd.reset_option("display.width")
    pd.reset_option("display.max_colwidth")


@click.command(name="fm")
def adjust_forward():
    """FSB interactively adjust multiple prices with an alternative fwd"""
    with dataBlob(
        log_name="Adjust-Forward-For-Multiple",
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
        ),
    ) as data:
        diag_contracts = dataContracts(data)
        data.add_class_list([arcticFuturesContractPriceData])
        do_another = True
        while do_another:
            EXIT_STR = "Finished: Exit"
            instr_code = get_valid_instrument_code_from_user(
                data, source="single", allow_exit=True, exit_code=EXIT_STR
            )
            if instr_code is EXIT_STR:
                do_another = False
            else:
                roll_cal = build_and_write_roll_calendar(
                    instrument_code=instr_code,
                    output_datapath="fsb.roll_calendars_csv",
                    input_prices=data.db_futures_contract_price,
                    check_before_writing=False,
                    input_config=csvRollParametersData(datapath="fsb.csvconfig"),
                    write=False,
                )

                last = roll_cal.iloc[-1]
                priced = last["current_contract"]
                fwd = last["next_contract"]
                carry = last["carry_contract"]
                click.echo(
                    f"Current multiple price setup: priced={priced}, "
                    f"forward={fwd}, carry={carry}"
                )
                invalid_input = True
                while invalid_input:
                    dates_to_choose_from = get_dates_to_choose_from(
                        data=data,
                        instrument_code=instr_code,
                        only_sampled_contracts=True,
                    )

                    dates_to_display = diag_contracts.get_labelled_list_of_contracts_from_contract_date_list(
                        instr_code, dates_to_choose_from
                    )

                    click.echo("Available contract dates %s" % str(dates_to_display))
                    new_fwd = input("New contract for forward and carry? [yyyymmdd]")
                    if new_fwd in dates_to_choose_from:
                        break
                    else:
                        click.echo(f"{new_fwd} is not in list {dates_to_choose_from}")
                        continue  # not required

                # check there are enough prices in new proposed forward
                new_fwd_prices = data.db_futures_contract_price.get_merged_prices_for_contract_object(
                    fc.from_two_strings(instr_code, new_fwd)
                )

                ans = input(
                    f"Price lines for proposed new fwd: {len(new_fwd_prices)}. "
                    f"Are you sure? (y/other)"
                )
                if ans == "y":

                    click.echo(
                        f"OK. Adjusting multiple prices for {instr_code} with "
                        f"{new_fwd} as forward and carry, instead of {fwd}"
                        f"NOTE: debug mode, will only write to CSV currently"  # TODO
                    )

                    roll_cal.iloc[
                        -1, roll_cal.columns.get_loc("next_contract")
                    ] = new_fwd
                    roll_cal.iloc[
                        -1, roll_cal.columns.get_loc("carry_contract")
                    ] = new_fwd

                    adj_mult_prices = process_multiple_prices_single_instrument(
                        instrument_code=instr_code,
                        adjust_calendar_to_prices=False,
                        csv_multiple_data_path="fsb.multiple_prices_csv",
                        csv_roll_data_path="fsb.csvconfig",
                        ADD_TO_ARCTIC=False,  # TODO
                        ADD_TO_CSV=True,  # TODO
                        roll_calendar=roll_cal,
                    )

                    click.echo(f"Adjusted multiple prices: {adj_mult_prices}")


if __name__ == "__main__":
    # show_optimals()
    adjust_forward()
