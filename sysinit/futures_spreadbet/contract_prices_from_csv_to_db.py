from syscore.constants import arg_not_supplied

from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData
from sysproduction.data.prices import diagPrices
from sysobjects.contracts import futuresContract
from syscore.dateutils import Frequency, MIXED_FREQ
from syscore.text import remove_suffix

diag_prices = diagPrices()


def init_db_with_csv_futures_contract_prices(
    datapath: str, csv_config=arg_not_supplied
):
    csv_prices = csvFuturesContractPriceData(datapath)
    input(
        "WARNING THIS WILL ERASE ANY EXISTING DATABASE PRICES WITH DATA FROM %s ARE YOU SURE?! (CTRL-C TO STOP)"
        % csv_prices.datapath
    )

    instrument_codes = csv_prices.get_list_of_instrument_codes_with_merged_price_data()
    instrument_codes.sort()
    for instrument_code in instrument_codes:
        init_db_with_csv_futures_prices_for_code(
            instrument_code, datapath, csv_config=csv_config
        )


def init_db_with_csv_futures_prices_for_code(
    instrument_code: str,
    datapath: str,
    csv_config=arg_not_supplied,
    freq=MIXED_FREQ,
):
    print(f"Importing csv prices ({freq.name}) for {instrument_code}")
    csv_prices = csvFuturesContractPriceData(datapath, config=csv_config)
    db_prices = diag_prices.db_futures_contract_price_data

    print(f"Getting .csv prices ({freq.name}) may take some time")
    csv_price_dict = csv_prices.get_prices_at_frequency_for_instrument(
        instrument_code, frequency=freq
    )

    print(f"Have .csv prices ({freq.name}) for the following contracts:")
    print(str(csv_price_dict.keys()))

    for contract_date_str, prices_for_contract in csv_price_dict.items():
        print(f"Processing {contract_date_str}")
        print(f".csv prices are\n{str(prices_for_contract)}")
        contract = futuresContract.from_two_strings(instrument_code, contract_date_str)
        print(f"Contract object is {str(contract)}")
        print("Writing to db")
        db_prices.write_prices_at_frequency_for_contract_object(
            contract, prices_for_contract, frequency=freq, ignore_duplication=True
        )
        print("Reading back prices from db to check")
        written_prices = db_prices.get_prices_at_frequency_for_contract_object(
            contract, frequency=freq
        )
        print(f"Read back prices ({freq.name}) are \n{str(written_prices)}")


def init_db_with_csv_futures_prices_for_contract(
    instr_code: str,
    date_str: str,
    datapath: str,
    csv_config=arg_not_supplied,
    freq: Frequency = MIXED_FREQ,
):
    csv_prices = csvFuturesContractPriceData(datapath, config=csv_config)
    db_prices = diag_prices.db_futures_contract_price_data

    print(f"Getting .csv prices for {instr_code} ({freq.name}) - may take some time")
    csv_price_dict = csv_prices.get_prices_at_frequency_for_instrument(instr_code, freq)
    print(f"Have .csv prices ({freq.name}) for the following contracts:")
    print(str(csv_price_dict.keys()))

    if date_str in csv_price_dict:
        prices_for_contract = csv_price_dict[date_str]
        print(f"Processing {date_str}")
        print(f".csv prices ({freq.name}) are \n{str(prices_for_contract)}")
        contract = futuresContract.from_two_strings(instr_code, date_str)
        print(f"Contract object is {str(contract)}")
        print("Writing to arctic")
        db_prices.write_prices_at_frequency_for_contract_object(
            contract, prices_for_contract, frequency=freq, ignore_duplication=True
        )
        print("Reading back prices from arctic to check")
        written_prices = db_prices.get_prices_at_frequency_for_contract_object(
            contract, frequency=freq
        )
        print(f"Read back prices ({freq.name}) are\n{str(written_prices)}")
    else:
        print(f"Can't find {freq.name} csv price data for {instr_code}/{date_str}")


# def init_db_with_csv_fsb_contract_prices(datapath: str, csv_config=arg_not_supplied):
#     csv_prices = CsvFsbContractPriceData(datapath)
#     input(
#         "WARNING THIS WILL ERASE ANY EXISTING FSB ARCTIC PRICES WITH DATA FROM %s ARE YOU SURE?! (CTRL-C TO STOP)"
#         % csv_prices.datapath
#     )
#
#     instrument_codes = csv_prices.get_list_of_instrument_codes_with_merged_price_data()
#     instrument_codes.sort()
#     for instrument_code in instrument_codes:
#         init_arctic_with_csv_fsb_contract_prices_for_code(
#             instrument_code, datapath, csv_config=csv_config
#         )


# def init_arctic_with_csv_fsb_contract_prices_for_code(
#     instrument_code: str, datapath: str, csv_config=arg_not_supplied
# ):
#     csv_prices = CsvFsbContractPriceData(datapath, config=csv_config)
#     arctic_prices = ArcticFsbContractPriceData()
#
#     print("Getting FSB .csv prices may take some time")
#     csv_price_dict = csv_prices.get_merged_prices_for_instrument(instrument_code)
#
#     print("Have FSB .csv prices for the following contracts:")
#     print(str(csv_price_dict.keys()))
#
#     for contract_date_str, prices_for_contract in csv_price_dict.items():
#         print(f"Processing {instrument_code}/{contract_date_str}")
#         print(".csv prices are \n %s" % str(prices_for_contract))
#         contract = futuresContract.from_two_strings(instrument_code, contract_date_str)
#         print("Contract object is %s" % str(contract))
#         print("Writing to arctic")
#         arctic_prices.write_merged_prices_for_contract_object(
#             contract, prices_for_contract, ignore_duplication=True
#         )
#         print("Reading back prices from arctic to check")
#         written_prices = arctic_prices.get_merged_prices_for_contract_object(contract)
#         print("Read back prices are \n %s" % str(written_prices))


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    # modify flags as required
    datapath = "*** NEED TO DEFINE A DATAPATH***"
    init_db_with_csv_futures_contract_prices(datapath)
