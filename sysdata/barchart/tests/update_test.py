from sysdata.barchart.bc_connection import bcConnection
from sysdata.barchart.bc_instruments_data import BarchartFuturesInstrumentData
from sysdata.barchart.bc_futures_contracts_data import BarchartFuturesContractData
from sysdata.barchart.bc_futures_contract_price_data import (
    BarchartFuturesContractPriceData,
)

from sysobjects.contracts import futuresContract as fc
from syscore.dateutils import Frequency

import pandas as pd
import pytest
import datetime


def check_current_contracts():
    bc = bcConnection()

    print("Checking timestamp of latest prices available from Barchart...")

    for contract in [
        ("BUND", "20210900"),
        ("GOLD", "20210800"),
        ("NZD", "20210900"),
        ("SP500", "20210900"),
    ]:
        # for contract in [('GOLD','20210600'), ('GOLD','20210800'), ('GOLD','20211000'), ('GOLD','20211200')]:
        # for contract in [('AEX','20210900')]:
        df = bc.get_historical_futures_data_for_contract(fc(contract[0], contract[1]))
        print(df.tail(10))


if __name__ == "__main__":

    check_current_contracts()
