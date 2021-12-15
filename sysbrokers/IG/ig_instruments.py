from dataclasses import dataclass
from sysobjects.instruments import futuresInstrument


@dataclass
class IgInstrumentConfigData:
    epic: str
    currency: str
    ig_multiplier: float
    ig_inverse: bool = False


@dataclass
class FsbInstrumentWithIgConfigData(object):
    instrument: futuresInstrument
    ig_data: IgInstrumentConfigData

    @property
    def instrument_code(self):
        return self.instrument.instrument_code

    @property
    def epic(self):
        return self.ig_data.epic
