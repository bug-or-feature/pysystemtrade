from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysinit.futures.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices,
)
from sysinit.futures_spreadbet.contract_prices_from_csv_to_arctic import (
    init_arctic_with_csv_futures_contract_prices_for_code,
    init_arctic_with_csv_futures_contract_prices_for_contract,
)

market_map = dict(
    AE="AEX",
    AP="ASX",
    A6="AUD",
    BA="BITCOIN",
    HR="BOBL",
    CB="BRENT_W",
    II="BTP",
    GG="BUND",
    GX="BUXL",
    MX="CAC",
    D6="CAD",
    CK="CARBON",
    S6="CHF",
    CA="COCOA_LDN",
    CC="COCOA_NY",
    KC="COFFEE",
    RM="COFFEE_LDN",
    HG="COPPER",
    ZC="CORN",
    CT="COTTON",
    CL="CRUDE_W",
    DY="DAX",
    DX="DOLLAR",
    YM="DOW",
    GE="EDOLLAR",
    E6="EUR",
    RP="EURGBP",
    IM="EURIBOR",
    FX="EUROSTX",
    X="FTSE",
    LF="GASOIL_LDN",
    RB="GASOLINE",
    NG="GAS_US",
    B6="GBP",
    G="GILT",
    GC="GOLD",
    HS="HANG",
    HO="HEATOIL",
    JX="JGB",
    J6="JPY",
    HE="LEANHOG",
    LE="LIVECOW",
    LB="LUMBER",
    M6="MXP",
    NQ="NASDAQ",
    NY="NIKKEI",
    N6="NZD",
    FN="OAT",
    ZO="OATIES",
    OJ="OJ",
    PA="PALLAD",
    PL="PLAT",
    ZR="RICE",
    QR="RUSSELL",
    HF="SHATZ",
    SI="SILVER",
    SZ="SMI",
    ZS="SOYBEAN",
    ZM="SOYMEAL",
    ZL="SOYOIL",
    ES="SP500",
    L="STERLING3",
    SB="SUGAR",
    SW="SUGAR_LDN",
    ZN="US10",
    ZT="US2",
    UD="US30",
    ZF="US5",
    ZB="USTB",
    DV="V2X",
    VI="VIX",
    ZW="WHEAT",
    XX="WHEAT_LDN",
)

ig_csv_config = ConfigCsvFuturesPrices(
    input_date_index_name="Date",
    input_skiprows=0,
    input_skipfooter=0,
    input_date_format="%Y-%m-%dT%H:%M:%S%z",
    input_column_mapping=dict(
        OPEN="Open", HIGH="High", LOW="Low", FINAL="Close", VOLUME="Volume"
    ),
)


def transfer_barchart_prices_to_arctic(datapath):
    init_arctic_with_csv_futures_contract_prices(datapath, csv_config=ig_csv_config)


def transfer_barchart_prices_to_arctic_single(instr, datapath):
    init_arctic_with_csv_futures_contract_prices_for_code(
        instr, datapath, csv_config=ig_csv_config
    )


def transfer_barchart_prices_to_arctic_single_contract(instr, contract, datapath):
    init_arctic_with_csv_futures_contract_prices_for_contract(
        instr, contract, datapath, csv_config=ig_csv_config
    )


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    datapath = "/Users/ageach/Dev/work/pyhistprice/data/ig/live5"
    # transfer_barchart_prices_to_arctic(datapath)

    # transfer_barchart_prices_to_arctic_single('NASDAQ_fsb', datapath)

    # for instr in ["LIVECOW_fsb"]:
    # for instr in ["BUXL_fsb", "CAD_fsb", "CARBON_fsb", "CRUDE_W_fsb", "DAX_fsb", "EUROSTX_fsb", "GILT_fsb", "HANG_fsb", "NIKKEI_fsb", "NZD_fsb", "SOYOIL_fsb", "US30_fsb"]:
    # for instr in ['COFFEE_fsb','US10_fsb', 'ASX_fsb','EUR_fsb','COPPER_fsb','HEATOIL_fsb','LIVECOW_fsb','US5_fsb','AEX_fsb','DOLLAR_fsb','PALLAD_fsb','GASOLINE_fsb']:
    #    transfer_barchart_prices_to_arctic_single(instr, datapath)

    # for instr in ["US30", "USTB", "EURIBOR", "STERLING3", "EURGBP", "JGB", "CAD", "CHF", "DOLLAR", "BRENT_W", "GASOLINE", "HEATOIL", "GASOIL_LDN"]:
    #    for contract_date in ['20200300', '20200600', '20200900', '20201200', '20210300', '20210600', '20210900', '20211200']:
    #        transfer_barchart_prices_to_arctic_single_contract(instr, contract_date, datapath)

    # for contract_date in ['DAX.20201200', 'DAX.20210300', 'DAX.20210600', 'DAX.20210900', 'DAX.20211200']:
    # for contract_date in ['20200100', '20200200', '20200300', '20200400','20200500', '20200600', '20200700', '20200800','20200900', '20201000', '20201100', '20201200','20210100', '20210200', '20210300', '20210400','20210500', '20210600', '20210700', '20210800','20210900', '20211000', '20211100', '20211200']:
    # for contract in ['DAX.20210600', 'DAX.20210900', 'DAX.20211200']:
    # instr = "SUGAR_LDN"
    # years = ["2020","2021","2022"]
    # months = ["01","03","05","07","08","09","10","12"]
    # for contract_date in ['20200900','20201200','20210300','20210500','20210700','20210900','20211200','20220300','20220500','20220700','20220900','20221200']:
    # for contract_date in ['20210300', '20210500', '20210700', '20210900', '20211100',   '20210300', '20210500', '20210700', '20210900', '20211100',]:
    # for contract_date in ['19950800']:
    #    transfer_barchart_prices_to_arctic_single_contract(instr, contract_date, datapath)
    # for year in years:
    #     for month in months:
    #         contract_date = f"{year}{month}00"
    #         print(f"code: {contract_date}")

    # instr = 'BUXL_fsb'
    # for contract_date in ['20210900']:
    # for contract_date in ['20110600', '20220200','20220400','20220600', ]:
    #    transfer_barchart_prices_to_arctic_single_contract(instr, contract_date, datapath)

    transfer_barchart_prices_to_arctic_single_contract(
        "COPPER_fsb", "20210700", datapath
    )
