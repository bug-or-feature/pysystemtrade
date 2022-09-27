from dataclasses import dataclass, field
from sysobjects.instruments import futuresInstrument


@dataclass
class IgInstrumentConfigData:
    epic: str
    currency: str
    multiplier: float
    bc_code: str
    periods: list = field(init=False, repr=False)
    inverse: bool = False
    period_str: str = "na"
    margin: float = 0.1

    def __post_init__(self):
        if self.period_str != "na":
            self.periods = self.period_str.split("|")
        else:
            self.periods = []

    def as_dict(self):
        return dict(
            epic=self.epic,
            currency=self.currency,
            multiplier=self.multiplier,
            bc_code=self.bc_code,
            inverse=self.inverse,
            period_str=self.period_str,
            margin=self.margin
        )

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
    def multiplier(self):
        return self.ig_data.multiplier

    @property
    def inverse(self):
        return self.ig_data.inverse

    @property
    def bc_code(self):
        return self.ig_data.bc_code

    @property
    ## FIXME make it look like a standard instrument, but we don't officially inherit... not sure why?
    def meta_data(self):
        return self.ig_data