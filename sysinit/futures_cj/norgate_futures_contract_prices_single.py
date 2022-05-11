import os

from syscore.dateutils import month_from_contract_letter
from syscore.fileutils import (
    files_with_extension_in_resolved_pathname,
    get_resolved_pathname,
)
from syscore.fileutils import get_filename_for_package
from sysdata.config.production_config import get_production_config
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices_for_code,
    init_arctic_with_csv_futures_contract_prices_for_contract,
)


NORGATE_CONFIG = ConfigCsvFuturesPrices(
    input_date_index_name="Date",
    input_skiprows=0,
    input_skipfooter=0,
    input_date_format="%Y%m%d",
    input_column_mapping=dict(
        OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Close"
    )
)


def rename_files(pathname, norgate_instr_code=None):

    unmapped = []
    resolved_pathname = get_resolved_pathname(pathname)
    file_names = files_with_extension_in_resolved_pathname(resolved_pathname)
    for filename in file_names:
        splits = filename.split("-")
        identifier = splits[0]
        if norgate_instr_code != identifier:
            print(f"Ignoring {os.path.join(resolved_pathname, filename + '.csv')}")
            continue
        year = int(splits[1][:-1])
        monthcode = splits[1][4:]
        month = month_from_contract_letter(monthcode)

        if identifier in market_map:
            instrument = market_map[identifier]
            datecode = str(year) + "{0:02d}".format(month)
            new_file_name = f"{instrument}_{datecode}00.csv"
            new_full_name = os.path.join(resolved_pathname + "_conv", new_file_name)
            old_full_name = os.path.join(resolved_pathname, filename + ".csv")
            print(f"Renaming {old_full_name} to {new_full_name}")
            os.rename(old_full_name, new_full_name)

        else:
            unmapped.append(identifier)

    mylist = list(dict.fromkeys(unmapped))
    print(f"Unmapped: {sorted(mylist)}")
    return None


market_map = {
    '6A': 'AUD',
    '6B': 'GBP',
    '6C': 'CAD',
    '6E': 'EUR',
    '6J': 'JPY',
    '6M': 'MXP',
    '6N': 'NZD',
    '6S': 'CHF',
    'AE': 'AEX',
    #'AFB': "Eastern Australia Feed Barley",
    #'AWM': "Eastern Australia Wheat",
    'BAX': "CADSTIR",
    'BRN': 'BRENT',
    'BTC': 'BITCOIN',
    'CC': 'COCOA',
    'CGB': "CAD10",
    'CL': 'CRUDE_W',
    'CT': 'COTTON',
    'DC': 'MILK',
    'DV': 'V2X',
    'DX': 'DX',
    'EH': 'ETHANOL',
    'EMD': 'SP400',
    'ES': 'SP500',
    'ET': 'SP500_micro',
    'EUA': 'EUA',
    'FBTP': "BTP",
    #'FBTP9': "XXX",
    'FCE': 'CAC',
    'FDAX': 'DAX',
    #'FDAX9': "XXX",
    'FESX': 'EUROSTX',
    #'FESX9': "XXX",
    'FGBL': 'BUND',
    #'FGBL9': "XXX",
    'FGBM': 'BOBL',
    #'FGBM9': "XXX",
    'FGBS': 'SHATZ',
    #'FGBS9': "XXX",
    'FGBX': 'BUXL',
    'FOAT': 'OAT',
    #'FOAT9': "XXX",
    'FSMI': 'SMI',
    #'FTDX': 'TecDAX',
    'GAS': 'GASOIL',
    'GC': 'GOLD',
    'GD': "GICS",
    'GE': 'EDOLLAR',
    'GF': 'FEEDCOW',
    'GWM': 'GAS_UK',
    'HE': 'LEANHOG',
    'HG': 'COPPER',
    'HO': 'HEATOIL',
    #'HTW': "MSCI Taiwan Index",
    #'HTW4': "XXX",
    'HSI': 'HANG',
    'KC': 'COFFEE',
    'KE': 'REDWHEAT',
    'KOS': 'KOSPI',
    'LBS': 'LUMBER',
    'LCC': "COCOA_LDN",
    'LE': 'LIVECOW',
    'LES': 'EURCHF',
    'LEU': 'EURIBOR',
    #'LEU9': "XXX",
    'LFT': 'FTSE100',
    #'LFT9': "XXX",
    'LLG': 'GILT',
    'LRC': 'ROBUSTA',
    'LSS': 'STERLING3',
    #'LSU': "white sugar",
    #'LWB': "Feed wheat",
    #'MHI': "Hang Seng Index - Mini",
    #'MWE': "Hard Red Spring Wheat",
    'NG': 'GAS_US',
    'NIY': 'NIKKEI-JPY',
    'NKD': 'NIKKEI',
    'NM': 'NASDAQ_micro',
    'NQ': 'NASDAQ',
    'OJ': 'OJ',
    'PA': 'PALLAD',
    'PL': 'PLAT',
    'QG': 'GAS_US_mini',
    'QM': 'CRUDE_W_mini',
    'RB': 'GASOILINE',
    'RS': 'CANOLA',
    'RTY': 'RUSSELL',
    'SB': 'SUGAR11',
    'SCN': 'FTSECHINAA',
    #'SCN4': 'XXXX',
    'SI': 'SILVER',
    #'SIN': 'SGX Nifty 50 Index',
    'SJB': 'JGB-mini',
    #'SNK': 'Nikkei 225 (SGX)',
    #'SNK4': 'XXXX',
    #'SP': 'XXXX',
    #'SP1': 'XXXX',
    'SSG': 'MSCISING',
    #'SSG4': 'XXXX',
    #'SXF': 'S&P/TSX 60 Index',
    'TN': 'US10U',
    'UB': 'US30',
    'VX': 'VIX',
    #'WBS': 'WTI Crude Oil',
    'YAP': 'ASX',
    #'YAP10': 'XXXX',
    #'YAP4': 'XXXX',
    'YG': 'Gold_micro',
    'YI': 'Mini-Silver',
    #'YIB': "ASX 30 Day Interbank Cash Rate",
    #'YIB4': 'XXXX',
    #'YIR': "ASX 90 Day Bank Accepted Bills",
    #'YIR4': 'XXXX',
    'YM': 'DOW',
    'YXT': "AUS10",
    #'YXT4': 'XXXX',
    'YYT': 'ZQ',
    #'YYT4': 'XXXX',
    'ZB': 'US20',
    'ZC': 'CORN',
    'ZF': 'US5',
    'ZL': 'SOYOIL',
    'ZM': 'SOYMEAL',
    'ZN': 'US10',
    'ZO': 'OATIES',
    #'ZQ': '30 Day Federal Funds',
    'ZR': 'RICE',
    'ZS': 'SOYBEAN',
    'ZT': 'US2',
    'ZW': 'WHEAT'
}


def transfer_norgate_prices_to_arctic_single(instr, datapath):
    init_arctic_with_csv_futures_contract_prices_for_code(
        instr,
        datapath,
        csv_config=NORGATE_CONFIG
    )

def transfer_barchart_prices_to_arctic_single_contract(instr, contract, datapath):
    init_arctic_with_csv_futures_contract_prices_for_contract(
        instr, contract, datapath, csv_config=NORGATE_CONFIG
    )

def transfer_norgate_prices_to_arctic_single_contract(instr, datapath):
    init_arctic_with_csv_futures_contract_prices_for_code(
        instr,
        datapath,
        csv_config=NORGATE_CONFIG
    )

# init_arctic_with_csv_futures_contract_prices_for_contract


def sort_map():
    sort = dict(sorted(market_map.items()))
    print(sort)

def find_map_dupes():
    # finding duplicate values
    # from dictionary
    # using a naive approach
    rev_dict = {}

    for key, value in market_map.items():
        rev_dict.setdefault(value, set()).add(key)

    result = [key for key, values in rev_dict.items()
              if len(values) > 1]

    # printing result
    print("duplicate values", str(result))


if __name__ == "__main__":
    # input("Will overwrite existing prices are you sure?! CTL-C to abort")
    # datapath = get_filename_for_package(
    #     get_production_config().get_element_or_missing_data("norgate_path")
    # )
    datapath = "/Users/ageach/Dev/work/pyhistprice/data/norgate_conv"

    transfer_barchart_prices_to_arctic_single_contract("GOLD", "20211200", datapath=datapath)

    #transfer_norgate_prices_to_arctic_single("GOLD", datapath=datapath)
    #for instr in ["SP500"]:
        #transfer_norgate_prices_to_arctic_single(instr, datapath=datapath)


    #sort_map()

    #find_map_dupes()

    #rename_files(datapath, "GC")