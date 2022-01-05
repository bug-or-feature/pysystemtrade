from dataclasses import dataclass
from sysobjects.instruments import futuresInstrument


@dataclass
class IgInstrumentConfigData:
    epic: str
    currency: str
    multiplier: float
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
