import pandas as pd
from pathlib import Path
from syscore.interactive.input import (
    get_input_from_user_and_convert_to_type,
)
from sysinit.futures.multiple_and_adjusted_from_csv_to_db import (
    init_db_with_csv_prices_for_code,
)
from sysinit.futures.multipleprices_from_db_prices_and_csv_calendars_to_db import (
    process_multiple_prices_single_instrument,
)
from sysinit.futures.rollcalendars_from_db_prices_to_csv import (
    build_and_write_roll_calendar,
)
from sysproduction.data.prices import get_valid_instrument_code_from_user

proj_dir = Path.cwd()
default_path_base = proj_dir / "data" / "futures"

path_base_str = get_input_from_user_and_convert_to_type(
    "Base dir for temp files?",
    type_expected=str,
    default_value=str(default_path_base),
)

path_base = Path(path_base_str)

roll_calendars_from_db = path_base / "roll_calendars_from_db"
multiple_prices_from_db = path_base / "multiple_from_db"
spliced_multiple_prices = path_base / "multiple_prices_csv_spliced"

if not roll_calendars_from_db.exists():
    roll_calendars_from_db.mkdir()

if not multiple_prices_from_db.exists():
    multiple_prices_from_db.mkdir()

if not spliced_multiple_prices.exists():
    spliced_multiple_prices.mkdir()

instrument_code = get_valid_instrument_code_from_user(source="multiple")
build_and_write_roll_calendar(
    instrument_code, output_datapath=str(roll_calendars_from_db)
)
input("Review roll calendar, press Enter to continue")

process_multiple_prices_single_instrument(
    instrument_code,
    csv_multiple_data_path=str(multiple_prices_from_db),
    csv_roll_data_path=str(roll_calendars_from_db),
    ADD_TO_DB=False,
    ADD_TO_CSV=True,
)
input("Review multiple prices, press Enter to continue")

supplied_file = path_base / "multiple_prices_csv" / f"{instrument_code}.csv"
generated_file = multiple_prices_from_db / f"{instrument_code}.csv"

supplied = pd.read_csv(supplied_file, index_col=0, parse_dates=True)
generated = pd.read_csv(generated_file, index_col=0, parse_dates=True)

# get final datetime of the supplied multiple_prices for this instrument
last_supplied = supplied.index[-1]

print(
    f"last datetime of supplied prices {last_supplied}, first datetime of updated "
    f"prices is {generated.index[0]}"
)

# assuming the latter is later than the former, truncate the generated data:
generated = generated.loc[last_supplied:]

# if first datetime in generated is the same as last datetime in repo, skip that row
first_generated = generated.index[0]
if first_generated == last_supplied:
    generated = generated.iloc[1:]

# check we're using the same price and forward contracts
# (i.e. no rolls missing, which there shouldn't be if there is date overlap)
try:
    assert (
        supplied.iloc[-1].PRICE_CONTRACT
        == generated.loc[last_supplied:].iloc[0].PRICE_CONTRACT
    )
    assert (
        supplied.iloc[-1].FORWARD_CONTRACT
        == generated.loc[last_supplied:].iloc[0].FORWARD_CONTRACT
    )
except AssertionError as e:
    print(supplied)
    print(generated)
    raise e
# nb we don't assert that the CARRY_CONTRACT is the same for supplied and generated,
# as some rolls implicit in the supplied multiple_prices don't match the pattern in
# the rollconfig.csv

spliced = pd.concat([supplied, generated])
spliced.to_csv(spliced_multiple_prices / f"{instrument_code}.csv")

init_db_with_csv_prices_for_code(
    instrument_code, multiple_price_datapath=str(spliced_multiple_prices)
)
