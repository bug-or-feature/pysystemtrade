import os

from syscore.dateutils import month_from_contract_letter
from syscore.fileutils import (
    files_with_extension_in_resolved_pathname,
    get_resolved_pathname,
)
from syscore.fileutils import get_filename_for_package
from sysdata.config.production_config import get_production_config
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData
from sysdata.csv.csv_roll_parameters import csvRollParametersData
from sysinit.futures.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices,
    init_arctic_with_csv_futures_contract_prices_for_code,
    init_arctic_with_csv_futures_contract_prices_for_contract,
)
from sysinit.futures_cj.barchart_futures_contract_prices_single import transfer_barchart_prices_to_arctic_single
from numpy import isnan

NORGATE_CONFIG = ConfigCsvFuturesPrices(
    input_date_index_name="Date",
    input_skiprows=0,
    input_skipfooter=0,
    input_date_format="%Y%m%d",
    input_column_mapping=dict(
        OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
    )
)

BARCHART_CONFIG = ConfigCsvFuturesPrices(
    input_date_index_name="Time",
    input_skiprows=0,
    input_skipfooter=0,
    input_date_format="%Y-%m-%dT%H:%M:%S%z",
    input_column_mapping=dict(
        OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
    )
)

def rename_files(pathname, norgate_instr_code=None, dry_run=True):

    """
    Renames Norgate price files into the format expected by pysystemtrdae. By default will move them into a directory
    named pathname + '_conv', which must exist. So

        /home/norgate/ES-2011U.csv

    would be moved to

        /home/norgate_conv/SP500_20110900.csv

    :param pathname: filesystem directory to the source files
    :type pathname: str
    :param norgate_instr_code: Norgate style instrument code. If omitted, will operate on all codes
    :type norgate_instr_code: str
    :param dry_run: flag to indicate whether to actually perform the rename/move
    :type dry_run: Bool

    """

    mapped = []
    unmapped = []
    misconfigured = []
    no_roll_config = []

    instr_config_src = csvFuturesInstrumentData()
    roll_config_src = csvRollParametersData()

    resolved_pathname = get_resolved_pathname(pathname)
    file_names = files_with_extension_in_resolved_pathname(resolved_pathname)
    for filename in file_names:
        splits = filename.split("-")
        identifier = splits[0]
        if norgate_instr_code is not None and norgate_instr_code != identifier:
            continue
        year = int(splits[1][:-1])
        monthcode = splits[1][4:]
        month = month_from_contract_letter(monthcode)

        if identifier in market_map:

            instrument = market_map[identifier]

            instr_config = instr_config_src._get_instrument_data_without_checking(instrument)
            if isnan(instr_config.meta_data.PerBlock) or isnan(instr_config.meta_data.Slippage):
                misconfigured.append(f"{identifier} ({instrument})")
                continue

            if not roll_config_src.is_code_in_data(instrument):
                no_roll_config.append(f"{identifier} ({instrument})")
                continue

            datecode = str(year) + "{0:02d}".format(month)
            new_file_name = f"{instrument}_{datecode}00.csv"
            new_full_name = os.path.join(resolved_pathname + "_conv", new_file_name)
            old_full_name = os.path.join(resolved_pathname, filename + ".csv")

            mapped.append(instrument)
            if dry_run:
                print(f"NOT renaming {old_full_name} to {new_full_name}, as dry_run")
            else:
                print(f"Renaming {old_full_name} to {new_full_name}")
                os.rename(old_full_name, new_full_name)

        else:
            unmapped.append(identifier)

    print(f"Successfully mapped: {dedupe_and_sort(mapped)}")
    print(f"Unmapped: {dedupe_and_sort(unmapped)}")
    print(f"Not properly configured in pysystemtrade: {dedupe_and_sort(misconfigured)}")
    print(f"No roll config in pysystemtrade: {dedupe_and_sort(no_roll_config)}")


def dedupe_and_sort(my_list):
    deduped = list(dict.fromkeys(my_list))
    return sorted(deduped)

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
    #'AFB': 'Eastern Australia Feed Barley',
    #'AWM': 'Eastern Australia Wheat',
    'BAX': 'CADSTIR',
    'BRN': 'BRENT',
    'BTC': 'BITCOIN',
    'CC': 'COCOA',
    'CGB': 'CAD10',
    'CL': 'CRUDE_W',
    'CT': 'COTTON2',
    'DC': 'MILK',
    'DV': 'V2X',
    'DX': 'DX',
    'EH': 'ETHANOL',
    'EMD': 'SP400',
    'ES': 'SP500',
    'ET': 'SP500_micro',
    'EUA': 'EUA',
    'FBTP': 'BTP',
    #'FBTP9': 'XXX',
    'FCE': 'CAC',
    'FDAX': 'DAX',
    #'FDAX9': 'XXX',
    'FESX': 'EUROSTX',
    #'FESX9': 'XXX',
    'FGBL': 'BUND',
    #'FGBL9': 'XXX',
    'FGBM': 'BOBL',
    #'FGBM9': 'XXX',
    'FGBS': 'SHATZ',
    #'FGBS9': 'XXX',
    'FGBX': 'BUXL',
    'FOAT': 'OAT',
    #'FOAT9': 'XXX',
    'FSMI': 'SMI',
    #'FTDX': 'TecDAX',
    'GAS': 'GASOIL',
    'GC': 'GOLD',
    'GD': 'GICS',
    'GE': 'EDOLLAR',
    'GF': 'FEEDCOW',
    'GWM': 'GAS_UK',
    'HE': 'LEANHOG',
    'HG': 'COPPER',
    'HO': 'HEATOIL',
    #'HTW': 'MSCI Taiwan Index',
    #'HTW4': 'XXX',
    'HSI': 'HANG',
    'KC': 'COFFEE',
    'KE': 'REDWHEAT',
    'KOS': 'KOSPI',
    'LBS': 'LUMBER',
    'LCC': 'COCOA_LDN',
    'LE': 'LIVECOW',
    'LES': 'EURCHF',
    'LEU': 'EURIBOR',
    #'LEU9': 'XXX',
    'LFT': 'FTSE100',
    #'LFT9': 'XXX',
    'LLG': 'GILT',
    'LRC': 'ROBUSTA',
    'LSS': 'STERLING3',
    'LSU': 'SUGAR',
    #'LWB': 'Feed wheat',
    #'MHI': 'Hang Seng Index - Mini',
    #'MWE': 'Hard Red Spring Wheat',
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
    #'SO3': '3-Month SONIA',
    #'SP': 'XXXX',
    #'SP1': 'XXXX',
    #'SR3': '3-Month SOFR',
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
    'YG': 'GOLD_micro',
    'YI': 'SILVER-mini',
    #'YIB': 'ASX 30 Day Interbank Cash Rate',
    #'YIB4': 'XXXX',
    #'YIR': 'ASX 90 Day Bank Accepted Bills',
    #'YIR4': 'XXXX',
    'YM': 'DOW',
    'YXT': 'AUS10',
    #'YXT4': 'XXXX',
    'YYT': 'AUS3',
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


norgate_multiplier_map = {
    'COFFEE': 0.01,
    'COPPER': 0.01,
    'COTTON2': 0.01,
    'JPY': 0.01,
    'OJ': 0.01,
    'RICE': 0.01,
    'SUGAR11': 0.01,
}


def transfer_norgate_prices_to_arctic_single_contract(instr, contract, datapath):
    init_arctic_with_csv_futures_contract_prices_for_contract(
        instr, contract, datapath, csv_config=NORGATE_CONFIG
    )


def transfer_norgate_prices_to_arctic_single(instr, datapath):
    init_arctic_with_csv_futures_contract_prices_for_code(
        instr,
        datapath,
        csv_config=build_import_config(instr)
    )


def transfer_norgate_prices_to_arctic(datapath):
    init_arctic_with_csv_futures_contract_prices(
        datapath, csv_config=NORGATE_CONFIG
    )


def transfer_barchart_prices_to_arctic_single_contract(instr, contract, datapath):
    init_arctic_with_csv_futures_contract_prices_for_contract(
        instr, contract, datapath, csv_config=BARCHART_CONFIG
    )


def build_import_config(instr):
    if instr in norgate_multiplier_map:
        multiplier = norgate_multiplier_map[instr]
    else:
        multiplier = 1.0

    return ConfigCsvFuturesPrices(
        input_date_index_name="Date",
        input_skiprows=0,
        input_skipfooter=0,
        input_date_format="%Y%m%d",
        input_column_mapping=dict(
            OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
        ),
        apply_multiplier=multiplier,

    )

if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    #datapath = "/home/caleb/pysystemtrade/data/Norgate/Futures"
    #datapath = "/home/caleb/pysystemtrade/data/Norgate/Future_conv"
    datapath = get_filename_for_package(
        get_production_config().get_element_or_missing_data("norgate_path")
        #get_production_config().get_element_or_missing_data("barchart_path")
    )

    # rename/move files, just for one (Norgate style) instrument code. Operates in 'dry_run' mode by default
    # to actually do the rename, set dry_run=False
    # rename_files(datapath, "NKD")
    # rename_files(datapath, "NKD", dry_run=False)

    # rename/move all files. Operates in 'dry_run' mode by default
    # to actually do the rename, set dry_run=False
    #rename_files(datapath)
    #rename_files(datapath, dry_run=False)

    # import just one contract file
    # transfer_norgate_prices_to_arctic_single_contract("GOLD", "20211200", datapath=datapath)

    # import all contract files for one instrument
    #transfer_norgate_prices_to_arctic_single(instrument_code, datapath=datapath)

    # import all contract files for more than one instrument
    # for instr in ["GOLD", "SP500"]:

    #for instr in ['STERLING3']:
    #for instr in ['BOBL', 'BTP', 'BUND', 'BUXL', 'EDOLLAR', 'EURIBOR', 'OAT', 'SHATZ', 'US10', 'US10U', 'US2', 'US20', 'US30', 'US5']:
    #for instr in # ['CAC', 'DAX', 'DOW', 'EUROSTX', 'FTSE100', 'NASDAQ', 'NIKKEI', 'RUSSELL', 'SMI', 'SP400', 'VIX']:
    #for instr in ['AUD', 'BITCOIN', 'CAD', 'CHF', 'JPY', 'MXP']:
    #for instr in ['JPY', 'OJ', 'COFFEE', 'SUGAR11', 'COPPER', 'RICE']:
    #for instr in ['JPY', 'OJ', 'COFFEE', 'SUGAR11', 'COPPER', 'RICE']:
    #for instr in ["BOBL", "BTP", "BUND", "BUXL", "CAC", "CANOLA", "COTTON", "EURIBOR", "EUROSTX", "DAX", "FTSE100", "GASOIL", "NIKKEI", "OAT", "ROBUSTA", "SHATZ", "SMI", "VIX"]:
    #for instr in ["BOBL", "BTP", "BUND", "BUXL", "OAT", "SHATZ"]:
    #for instr in ['COTTON2']:
    #for instr in ['EURIBOR']:
    #for instr in ['NIKKEI']:
    for instr in ['COTTON2','FTSE100','VIX']:
         transfer_norgate_prices_to_arctic_single(instr, datapath=datapath)
         #transfer_barchart_prices_to_arctic_single(instr, datapath=datapath)

    # import all contract files for all instruments
    # transfer_norgate_prices_to_arctic(datapath=datapath)

    # for instr in ["NZD"]:
    #     for contract_date in ['20130900']:
    #         transfer_barchart_prices_to_arctic_single_contract(instr, contract_date, datapath)

    # bash rename COTTON_YYYYMMDD.csv to COTTON2_YYYYMMDD.csv
    # for i in *-doc-*.txt; do mv "$i" "${i/*-doc-/doc-}"; done
    # for i in COTTON_*.csv; do mv "$i" "${i/COTTON_/COTTON2_}"; done

