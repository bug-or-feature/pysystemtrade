import datetime

import pandas as pd

from sysobjects.contracts import futuresContract
from sysdata.arctic.arctic_fsb_per_contract_prices import (
    ArcticFsbContractPriceData,
    FsbContractPrices,
)
from sysdata.mongodb.mongo_futures_contracts import mongoFuturesContractData
from sysdata.futures.futures_per_contract_prices import futuresContractPriceData
from sysdata.data_blob import dataBlob
from sysproduction.data.generic_production_data import productionDataLayerGeneric


class UpdateFsbPrices(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:
        data.add_class_list(
            [
                ArcticFsbContractPriceData,
                mongoFuturesContractData,
                #arcticSpreadsForInstrumentData,
            ]
        )

        return data

    def update_prices_for_contract(
        self,
        contract_object: futuresContract,
        new_prices: pd.DataFrame,
        check_for_spike: bool = True,
    ) -> int:

        error_or_rows_added = (
            self.db_fsb_contract_price_data.update_prices_for_contract(
                contract_object, new_prices, check_for_spike=check_for_spike
            )
        )
        return error_or_rows_added

    # def add_spread_entry(self, instrument_code: str, spread: float):
    #     self.db_spreads_for_instrument_data.add_spread_entry(
    #         instrument_code, spread=spread
    #     )

    @property
    def db_futures_contract_price_data(self) -> futuresContractPriceData:
        return self.data.db_futures_contract_price

    @property
    def db_fsb_contract_price_data(self) -> futuresContractPriceData:
        return self.data.db_fsb_contract_price

    # @property
    # def db_spreads_for_instrument_data(self) -> spreadsForInstrumentData:
    #     return self.data.db_spreads_for_instrument
