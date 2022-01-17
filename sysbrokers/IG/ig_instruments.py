from dataclasses import dataclass
from sysobjects.instruments import futuresInstrument


@dataclass
class IgInstrumentConfigData:
    epic: str
    currency: str
    multiplier: float
    source: str
    bc_code: str
    inverse: bool = False
    period_str: str = ""
    margin: float = 0.1

    def epic_periods(self) -> []:
        if self.period_str == "na":
            return []
        else:
            return self.period_str.split("|")


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

    @property
    def source(self):
        return self.ig_data.source

    @property
    def multiplier(self):
        return self.ig_data.multiplier

    @property
    def inverse(self):
        return self.ig_data.inverse

    @property
    def bc_code(self):
        return self.ig_data.bc_code
