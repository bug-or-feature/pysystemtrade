from sysbrokers.IG.ig_capital_data import IgCapitalData
from sysdata.alphavantage.av_spot_FX_data import AvFxPricesData
from sysbrokers.IG.ig_futures_contract_price_data import IgFuturesContractPriceData
from sysbrokers.IG.ig_futures_contract_data import IgFuturesContractData
from sysbrokers.IG.ig_instruments_data import IgFuturesInstrumentData
from sysbrokers.IG.ig_contract_position_data import IgContractPositionData
from sysbrokers.IG.ig_orders import IgExecutionStackData
from sysbrokers.IG.ig_static_data import IgStaticData
from sysbrokers.IG.ig_fx_handling import IgFxHandlingData
from sysdata.mongodb.mongo_market_info import mongoMarketInfoData
from sysdata.arctic.arctic_fsb_epics_history import ArcticFsbEpicHistoryData
from sysdata.arctic.arctic_fsb_per_contract_prices import ArcticFsbContractPriceData


def get_class_list():
    return [
        AvFxPricesData,
        IgFuturesContractPriceData,
        IgFuturesContractData,
        IgContractPositionData,
        IgExecutionStackData,
        IgStaticData,
        IgCapitalData,
        IgFuturesInstrumentData,
        IgFxHandlingData,
        mongoMarketInfoData,
        ArcticFsbEpicHistoryData,
        ArcticFsbContractPriceData,
    ]
