from dataclasses import dataclass
from sysobjects.instruments import futuresInstrument


@dataclass
class BcInstrumentConfigData:
    symbol: str
    currency: str = ""


@dataclass
class BcFuturesInstrument(object):
    instrument: futuresInstrument
    bc_data: BcInstrumentConfigData

    @property
    def instrument_code(self):
        return self.instrument.instrument_code

    @property
    def bc_symbol(self):
        return self.bc_data.symbol
