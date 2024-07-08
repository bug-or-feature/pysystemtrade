from matplotlib.pyplot import show
import pandas as pd
from syscore.interactive.input import (
    true_if_answer_is_yes,
)
from sysdata.data_blob import dataBlob
from sysinit.futures.rollcalendars_from_arcticprices_to_csv import (
    build_and_write_roll_calendar,
)
from sysinit.futures.multipleprices_from_db_prices_and_csv_calendars_to_db import (
    process_multiple_prices_single_instrument,
)
from sysinit.futures.adjustedprices_from_db_multiple_to_db import (
    process_adjusted_prices_single_instrument,
)
from sysobjects.rolls import rollParameters
from sysproduction.data.prices import (
    get_valid_instrument_code_from_user,
    INSTRUMENT_CODE_SOURCE_CONFIG,
    diagPrices,
    updatePrices,
)
from sysproduction.data.fsb_contracts import DataFsbContracts
from sysdata.csv.csv_roll_calendars import csvRollCalendarData

from sysproduction.data.contracts import dataContracts, get_dates_to_choose_from
from sysobjects.contracts import futuresContract as fc


def safely_modify_fsb_roll_parameters(data: dataBlob):
    print("Strongly suggest you backup and/or do this on a test machine first")
    print("Enter instrument code: Must be defined in CSV config")
    instr_code = get_valid_instrument_code_from_user(
        data, source=INSTRUMENT_CODE_SOURCE_CONFIG
    )
    roll_parameters = get_roll_parameters(data, instrument_code=instr_code)

    roll_calendars = csvRollCalendarData("fsb.roll_calendars_csv")
    current = roll_calendars.get_roll_calendar(instr_code)

    rebuild = true_if_answer_is_yes(
        "Rebuild entire calendar? The alternative is a one off change, ie skipping one "
        "contract. In this scenario we would add any new rows, and then "
        "tweak the last one (y/n) "
    )
    if rebuild:
        build_and_write_roll_calendar(
            instr_code,
            output_datapath=roll_calendars.datapath,
            input_prices=data.db_futures_contract_price,
            roll_parameters=roll_parameters,
        )
    else:
        diag_contracts = dataContracts(data)

        # get existing roll cal, add any new rows to it
        print("Last few rows of existing calendar: ")
        print(current.tail(20))

        first = input("First contract to consider for additional rows? (eg 20240300) ")

        new_rows = build_and_write_roll_calendar(
            instr_code,
            output_datapath=roll_calendars.datapath,
            input_prices=data.db_futures_contract_price,
            roll_parameters=roll_parameters,
            first_contract=first,
            check_before_writing=False,
            write=False,
        )

        roll_cal = pd.concat([current, new_rows])

        last = roll_cal.iloc[-1]
        priced = last["current_contract"]
        fwd = last["next_contract"]
        carry = last["carry_contract"]
        print(
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

            dates_to_display = (
                diag_contracts.get_labelled_list_of_contracts_from_contract_date_list(
                    instr_code, dates_to_choose_from
                )
            )

            print("Available contract dates %s" % str(dates_to_display))
            new_fwd = input("New contract for forward? [yyyymmdd]")
            if new_fwd in dates_to_choose_from:
                break
            else:
                print(f"{new_fwd} is not in list {dates_to_choose_from}")
                continue  # not required

        # check there are enough prices in new proposed forward
        new_fwd_prices = (
            data.db_futures_contract_price.get_merged_prices_for_contract_object(
                fc.from_two_strings(instr_code, new_fwd)
            )
        )

        ans = input(
            f"Price lines for proposed new fwd: {len(new_fwd_prices)}. "
            f"Are you sure? (y/other) "
        )
        if ans == "y":
            print(
                f"OK. Writing roll calendar for {instr_code} with "
                f"{new_fwd} as forward, instead of {fwd}"
            )

            roll_cal.iloc[-1, roll_cal.columns.get_loc("next_contract")] = new_fwd

            roll_calendars.add_roll_calendar(
                instr_code, roll_cal, ignore_duplication=True
            )
        else:
            print("OK, exiting. Goodbye")
            return None

    ans = true_if_answer_is_yes(
        "Inspect roll calendar, and if required manually hack or "
        "change roll parameters. Happy to continue? (y/other) "
    )
    if not ans:
        print("Doing nothing. Goodbye")
        return None

    updated_roll_cal = roll_calendars.get_roll_calendar(instr_code)
    new_multiple_prices = process_multiple_prices_single_instrument(
        instr_code,
        csv_roll_data_path="fsb.csvconfig",
        csv_multiple_data_path="fsb.multiple_prices_csv",
        adjust_calendar_to_prices=False,
        ADD_TO_DB=False,
        ADD_TO_CSV=False,
        roll_calendar=updated_roll_cal,
        roll_parameters=roll_parameters,
    )

    new_adjusted_prices = process_adjusted_prices_single_instrument(
        instr_code,
        multiple_prices=new_multiple_prices,
        ADD_TO_DB=False,
        ADD_TO_CSV=False,
    )

    diag_prices = diagPrices(data)
    existing_multiple_prices = diag_prices.get_multiple_prices(instr_code)
    existing_adj_prices = diag_prices.get_adjusted_prices(instr_code)

    do_the_plots = true_if_answer_is_yes(
        "Display diagnostic plots? Answer NO on headless server (y/other) "
    )

    if do_the_plots:
        prices = pd.concat(
            [new_multiple_prices.PRICE, existing_multiple_prices.PRICE], axis=1
        )
        prices.columns = ["New", "Existing"]

        prices.plot(title="Prices of current contract")

        carry_price = pd.concat(
            [new_multiple_prices.CARRY, existing_multiple_prices.CARRY], axis=1
        )
        carry_price.columns = ["New", "Existing"]
        carry_price.plot(title="Price of carry contract")

        net_carry_existing = carry_price.Existing - prices.Existing
        net_carry_new = carry_price.New - prices.New
        net_carry_compare = pd.concat([net_carry_new, net_carry_existing], axis=1)
        net_carry_compare.columns = ["New", "Existing"]
        net_carry_compare.plot(title="Raw carry difference")

        adj_compare = pd.concat([existing_adj_prices, new_adjusted_prices], axis=1)
        adj_compare.columns = ["Existing", "New"]
        adj_compare.plot(title="Adjusted prices")
        input("Press return to see plots")
        show()

    sure = true_if_answer_is_yes(
        "Happy to continue? Will overwrite existing data! (y/other) "
    )
    if not sure:
        print("No changes made. Goodbye")
        return None

    update_prices = updatePrices(data)
    update_prices.add_multiple_prices(
        instrument_code=instr_code,
        updated_multiple_prices=new_multiple_prices,
        ignore_duplication=True,
    )
    print("Updated multiple prices in database: copy backup files for .csv")

    # Overwrite adjusted prices
    update_prices.add_adjusted_prices(
        instrument_code=instr_code,
        updated_adjusted_prices=new_adjusted_prices,
        ignore_duplication=True,
    )
    print("Updated adjusted prices in database: copy backup files for .csv")

    print("All done!")
    print(
        "Run update_sampled_contracts and interactive_update_roll_status to "
        "make sure no issues"
    )


def get_roll_parameters(data: dataBlob, instrument_code) -> rollParameters:
    print("Existing roll parameters: Must be defined in CSV config")
    data_contracts = DataFsbContracts(data)
    roll_parameters = data_contracts.get_roll_parameters(instrument_code)
    print(str(roll_parameters))

    return roll_parameters


if __name__ == "__main__":
    data = dataBlob(
        csv_data_paths=dict(
            csvFuturesInstrumentData="fsb.csvconfig",
            csvRollParametersData="fsb.csvconfig",
        ),
    )
    safely_modify_fsb_roll_parameters(data)
