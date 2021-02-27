from dataclasses import dataclass
from sysobjects.instruments import futuresInstrument

@dataclass
class barchartInstrumentConfigData:
    symbol: str
    currency: str = ""

@dataclass
class futuresInstrumentWithBarchartConfigData(object):
    instrument: futuresInstrument
    barchart_data: barchartInstrumentConfigData

    @property
    def instrument_code(self):
        return self.instrument.instrument_code

    @property
    def barchart_symbol(self):
        return self.barchart_data.symbol
