from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData
from sysinit.futures.clone_data_for_instrument import *

fsb_prices = ArcticFsbContractPriceData()
csv_roll_calendar = csvRollCalendarData()


def clone_data_for_instrument(
    instrument_from: str,
    instrument_to: str,
    write_to_csv: bool = False,
    inverse: bool = False,
    offset: float = 0.0,
    ignore_duplication: bool = False,
):
    clone_prices_per_contract(
        instrument_from,
        instrument_to,
        offset=offset,
        inverse=inverse,
        ignore_duplication=ignore_duplication,
    )
    if write_to_csv:
        clone_roll_calendar(instrument_from, instrument_to)

    clone_prices_per_fsb_contract(
        f"{instrument_from}_fsb",
        f"{instrument_to}_fsb",
        ignore_duplication=ignore_duplication,
    )


def clone_prices_per_fsb_contract(
    instrument_from: str,
    instrument_to: str,
    list_of_contract_dates=None,
    ignore_duplication=False,
):
    if list_of_contract_dates is None:
        list_of_contract_dates = (
            fsb_prices.contract_dates_with_merged_price_data_for_instrument_code(
                instrument_from
            )
        )

    _ = [
        clone_single_fsb_contract(
            instrument_from,
            instrument_to,
            contract_date,
            ignore_duplication=ignore_duplication,
        )
        for contract_date in list_of_contract_dates
    ]


def clone_single_fsb_contract(
    instrument_from: str,
    instrument_to: str,
    contract_date: str,
    ignore_duplication=False,
):
    futures_contract_from = futuresContract(instrument_from, contract_date)
    futures_contract_to = futuresContract(instrument_to, contract_date)

    data_in = fsb_prices.get_merged_prices_for_contract_object(futures_contract_from)

    fsb_prices.write_merged_prices_for_contract_object(
        futures_contract_to,
        futures_price_data=data_in,
        ignore_duplication=ignore_duplication,
    )


def clone_roll_calendar(instrument_from: str, instrument_to: str):
    roll_calendar = csv_roll_calendar.get_roll_calendar(instrument_from)
    csv_roll_calendar.add_roll_calendar(instrument_to, roll_calendar=roll_calendar)
