"""
Update historical data per contract from interactive brokers data, dump into mongodb

Apply a check to each price series
"""

from syscore.constants import success

from sysdata.data_blob import dataBlob
from sysproduction.data.prices import (
    diagPrices,
    get_valid_instrument_code_from_user,
)
from sysdata.tools.cleaner import interactively_get_config_overrides_for_cleaning
from sysproduction.update_historical_prices import (
    update_historical_prices_for_instrument,
)
from sysproduction.update_multiple_adjusted_prices import (
    update_multiple_adjusted_prices,
)
from sysproduction.generate_fsb_updates import GenerateFsbUpdates


def interactive_manual_check_historical_prices():
    """
    Do a daily update for futures contract prices, using IB historical data

    If any 'spikes' are found, run manual checks

    :return: Nothing
    """
    with dataBlob(
        log_name="Update-Historical-prices-manually",
        csv_data_paths=dict(
            csvFuturesInstrumentData="data.futures_spreadbet.csvconfig",
            csvRollParametersData="data.futures_spreadbet.csvconfig",
        ),
    ) as data:
        instr_list = []
        cleaning_config = interactively_get_config_overrides_for_cleaning(data=data)

        do_another = True
        while do_another:
            EXIT_STR = "Finished: Exit"
            instrument_code = get_valid_instrument_code_from_user(
                data, source="single", allow_exit=True, exit_code=EXIT_STR
            )
            if instrument_code is EXIT_STR:
                do_another = False
            else:
                check_instrument_ok_for_broker(data, instrument_code)
                data.log.label(instrument_code=instrument_code)
                update_historical_prices_for_instrument(
                    instrument_code=instrument_code,
                    cleaning_config=cleaning_config,
                    data=data,
                    interactive_mode=True,
                )
                instr_list.append(instrument_code)

        if instr_list:
            print(f"Now generating FSB prices from: {instr_list}")
            fsb_updater = GenerateFsbUpdates(data)
            for instr in instr_list:
                fsb_updater.update(instr + "_fsb")

            print(f"Now updating multiple and adjusted prices for: {instr_list}")
            update_multiple_adjusted_prices(instr_list)
    return success


def check_instrument_ok_for_broker(data: dataBlob, instrument_code: str):
    diag_prices = diagPrices(data)
    list_of_codes_all = diag_prices.get_list_of_instruments_with_contract_prices()
    if instrument_code not in list_of_codes_all:
        print("\n\n\ %s is not an instrument with price data \n\n" % instrument_code)
        raise Exception()


if __name__ == "__main__":
    interactive_manual_check_historical_prices()
