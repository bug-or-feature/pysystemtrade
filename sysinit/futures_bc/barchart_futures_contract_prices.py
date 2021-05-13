from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures.contract_prices_from_csv_to_arctic import init_arctic_with_csv_futures_contract_prices
from sysinit.futures_bc.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices_for_code,
    init_arctic_with_csv_futures_contract_prices_for_contract
)

market_map = dict(AE='AEX',
                  A6='AUD',
                  HR='BOBL',
                  II='BTP',
                  MX='CAC',
                  GG='BUND',
                  HG='COPPER',
                  ZC='CORN',
                  CL='CRUDE_W',
                  GE='EDOLLAR',
                  E6='EUR',
                  NG='GAS_US',
                  B6='GBP',
                  GC='GOLD',
                  J6='JPY',
                  HE='LEANHOG',
                  LE='LIVECOW',
                  M6='MXP',
                  NQ='NASDAQ',
                  N6='NZD',
                  FN='OAT',
                  PA='PALLAD',
                  HF='SHATZ',
                  PL='PLAT',
                  SZ='SMI',
                  ZS='SOYBEAN',
                  ES='SP500',
                  ZT='US2',
                  ZF='US5',
                  ZN='US10',
                  ZB='US20',
                  VI='VIX',
                  ZW='WHEAT',
                  DV='V2X',
                  UD='US30')

barchart_csv_config = ConfigCsvFuturesPrices(input_date_index_name="Time",
                                input_skiprows=0, input_skipfooter=0,
                                input_date_format='%Y-%m-%dT%H:%M:%S%z',
                                input_column_mapping=dict(OPEN='Open',
                                                          HIGH='High',
                                                          LOW='Low',
                                                          FINAL='Close',
                                                          VOLUME='Volume'
                                                          ))

def transfer_barchart_prices_to_arctic(datapath):
    init_arctic_with_csv_futures_contract_prices(datapath, csv_config= barchart_csv_config)

def transfer_barchart_prices_to_arctic_single(instr, datapath):
    init_arctic_with_csv_futures_contract_prices_for_code(instr, datapath, csv_config= barchart_csv_config)

def transfer_barchart_prices_to_arctic_single_contract(instr, contract, datapath):
    init_arctic_with_csv_futures_contract_prices_for_contract(instr, contract, datapath, csv_config=barchart_csv_config)

if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    datapath = "/Users/ageach/Dev/work/pyhistprice/data/barchart_tz"
    #transfer_barchart_prices_to_arctic(datapath)
    transfer_barchart_prices_to_arctic_single('GOLD', datapath)
    #transfer_barchart_prices_to_arctic_single_contract('SP500', '20210600', datapath)

