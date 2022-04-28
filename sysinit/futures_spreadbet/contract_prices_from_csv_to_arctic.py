import re
from syscore.objects import arg_not_supplied

from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData
from sysdata.csv.csv_fsb_contract_prices import CsvFsbContractPriceData
from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.arctic.arctic_fsb_per_contract_prices import (
    ArcticFsbContractPriceData,
)
from sysobjects.contracts import futuresContract


def init_arctic_with_csv_futures_contract_prices(
    datapath: str, csv_config=arg_not_supplied
):
    csv_prices = csvFuturesContractPriceData(datapath)
    input(
        "WARNING THIS WILL ERASE ANY EXISTING ARCTIC PRICES WITH DATA FROM %s ARE YOU SURE?! (CTRL-C TO STOP)"
        % csv_prices.datapath
    )

    instrument_codes = csv_prices.get_list_of_instrument_codes_with_price_data()
    instrument_codes.sort()
    for instrument_code in instrument_codes:
        init_arctic_with_csv_futures_contract_prices_for_code(
            instrument_code, datapath, csv_config=csv_config
        )

def init_arctic_with_csv_fsb_contract_prices(
    datapath: str, csv_config=arg_not_supplied
):
    csv_prices = CsvFsbContractPriceData(datapath)
    input(
        "WARNING THIS WILL ERASE ANY EXISTING FSB ARCTIC PRICES WITH DATA FROM %s ARE YOU SURE?! (CTRL-C TO STOP)"
        % csv_prices.datapath
    )

    instrument_codes = csv_prices.get_list_of_instrument_codes_with_price_data()
    instrument_codes.sort()
    for instrument_code in instrument_codes:
        init_arctic_with_csv_fsb_contract_prices_for_code(
            instrument_code, datapath, csv_config=csv_config
        )


def init_arctic_with_csv_futures_contract_prices_for_code(
    instrument_code: str, datapath: str, csv_config=arg_not_supplied
):
    fut_instr_code = instrument_code.removesuffix("_fsb")
    print(f"Futures: {fut_instr_code}, fsb: {instrument_code}")
    csv_prices = csvFuturesContractPriceData(datapath, config=csv_config)
    arctic_prices = arcticFuturesContractPriceData()

    print("Getting .csv prices may take some time")
    csv_price_dict = csv_prices.get_all_prices_for_instrument(fut_instr_code)

    print("Have .csv prices for the following contracts:")
    print(str(csv_price_dict.keys()))

    for contract_date_str, prices_for_contract in csv_price_dict.items():
        print("Processing %s" % contract_date_str)
        print(".csv prices are \n %s" % str(prices_for_contract))
        contract = futuresContract.from_two_strings(instrument_code, contract_date_str)
        print("Contract object is %s" % str(contract))
        print("Writing to arctic")
        arctic_prices.write_prices_for_contract_object(
            contract, prices_for_contract, ignore_duplication=True
        )
        print("Reading back prices from arctic to check")
        written_prices = arctic_prices.get_prices_for_contract_object(contract)
        print("Read back prices are \n %s" % str(written_prices))

def init_arctic_with_csv_fsb_contract_prices_for_code(
    instrument_code: str, datapath: str, csv_config=arg_not_supplied
):
    csv_prices = CsvFsbContractPriceData(datapath, config=csv_config)
    arctic_prices = ArcticFsbContractPriceData()

    print("Getting FSB .csv prices may take some time")
    csv_price_dict = csv_prices.get_all_prices_for_instrument(instrument_code)

    print("Have FSB .csv prices for the following contracts:")
    print(str(csv_price_dict.keys()))

    for contract_date_str, prices_for_contract in csv_price_dict.items():
        print(f"Processing {instrument_code}/{contract_date_str}")
        print(".csv prices are \n %s" % str(prices_for_contract))
        contract = futuresContract.from_two_strings(instrument_code, contract_date_str)
        print("Contract object is %s" % str(contract))
        print("Writing to arctic")
        arctic_prices.write_prices_for_contract_object(
            contract, prices_for_contract, ignore_duplication=True
        )
        print("Reading back prices from arctic to check")
        written_prices = arctic_prices.get_prices_for_contract_object(contract)
        print("Read back prices are \n %s" % str(written_prices))



def remove_suffix(input_str: str, suffix: str):
    if input_str.endswith(suffix):
        return re.sub(f"{suffix}$", '', input_str)
    return input_str


def init_arctic_with_csv_futures_contract_prices_for_contract(
    instrument_code: str, date_str: str, datapath: str, csv_config=arg_not_supplied
):
    fut_instr_code = instrument_code.removesuffix("_fsb")
    print(f"Futures: {fut_instr_code}, fsb: {instrument_code}")
    csv_prices = csvFuturesContractPriceData(datapath, config=csv_config)
    arctic_prices = arcticFuturesContractPriceData()

    print("Getting .csv prices may take some time")
    csv_price_dict = csv_prices.get_all_prices_for_instrument(fut_instr_code)

    print("Have .csv prices for the following contracts:")
    print(str(csv_price_dict.keys()))

    for contract_date_str, prices_for_contract in csv_price_dict.items():
        if contract_date_str == date_str:
            print("Processing %s" % contract_date_str)
            print(".csv prices are \n %s" % str(prices_for_contract))
            contract = futuresContract.from_two_strings(instrument_code, contract_date_str)
            print("Contract object is %s" % str(contract))
            print("Writing to arctic")
            arctic_prices.write_prices_for_contract_object(
                contract, prices_for_contract, ignore_duplication=True
            )
            print("Reading back prices from arctic to check")
            written_prices = arctic_prices.get_prices_for_contract_object(contract)
            print("Read back prices are \n %s" % str(written_prices))


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    # modify flags as required
    datapath = "*** NEED TO DEFINE A DATAPATH***"
    init_arctic_with_csv_futures_contract_prices(datapath)
