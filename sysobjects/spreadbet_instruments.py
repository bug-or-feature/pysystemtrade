from sysobjects.instruments import futuresInstrument, instrumentCosts, EMPTY_INSTRUMENT
from dataclasses import dataclass


class FuturesSpreadbet(futuresInstrument):

    def __init__(self, instrument_code: str):
        super().__init__(instrument_code)

    def __eq__(self, other):
        if isinstance(other, FuturesSpreadbet):
            if self.instrument_code == other.instrument_code:
                return True
        return False


@dataclass
class FuturesSpreadbetMetaData(object):

    Description: str = ""

    # point size in price units (futures spreadbet)
    Pointsize: float = 0.0
    Currency: str = ""
    AssetClass: str = ""
    AssetSubclass: str = ""
    Spread: float = 0.0

    # minimum bet per point
    # used by spread bets and CFDs (per point)
    MinBetPerPoint: float = 0.0

    # spreadbet prices (CFDs too?) are often a multiple of the underlying futures price, this is that value
    Multiplier: float = 1.0

    # some FX spread bets are priced as the inverse of the future they're based on, eg USDCAD -> CADUSD
    Inverse: bool = False

    # size of contract (value of a 1 point move in price)
    # used by CFDs (contracts)
    # ContractSize: float = 0.0

    # minimum number of contracts
    # used by CFDs (contracts)
    # MinContracts: float = 0.0

    # Slippage: float = 0.0
    # PerBlock: float = 0.0
    # Percentage: float = 0.0
    # PerTrade: float = 0.0
    # SpreadBetMultiplier: float = 1.0
    # BetPointSize: float = 0.0
    # RollsPerYear: int = 4

    def as_dict(self) -> dict:
        keys = self.__dataclass_fields__.keys()
        self_as_dict = dict([(key, getattr(self, key)) for key in keys])

        return self_as_dict

    @classmethod
    def from_dict(cls, input_dict):
        keys = cls.__dataclass_fields__.keys()
        args_list = [input_dict[key] for key in keys]

        return cls(*args_list)


@dataclass
class FuturesSpreadbetWithMetaData:
    instrument: FuturesSpreadbet
    meta_data: FuturesSpreadbetMetaData

    @property
    def instrument_code(self) -> str:
        return self.instrument.instrument_code

    @property
    def key(self) -> str:
        return self.instrument_code

    def as_dict(self) -> dict:
        meta_data_dict = self.meta_data.as_dict()
        meta_data_dict['instrument_code'] = self.instrument_code

        return meta_data_dict

    @classmethod
    def from_dict(cls, input_dict):
        instrument_code = input_dict.pop('instrument_code')
        instrument = FuturesSpreadbet(instrument_code)
        meta_data = FuturesSpreadbetMetaData.from_dict(input_dict)

        return FuturesSpreadbetWithMetaData(instrument, meta_data)

    @classmethod
    def create_empty(cls):
        instrument = FuturesSpreadbet(EMPTY_INSTRUMENT)
        meta_data = FuturesSpreadbetMetaData()

        instrument_with_metadata = FuturesSpreadbetWithMetaData(instrument, meta_data)

        return instrument_with_metadata

    def empty(self):
        return self.instrument.empty()


class FuturesSpreadbetCosts(instrumentCosts):

    def __init__(self, spread: float = 0.0, pointsize: float = 0.0, min_bet: float = 0.0,
                 multiplier: float = 0.0):

        self._spread = spread
        self._pointsize = pointsize
        self._min_bet = min_bet
        self._multiplier = multiplier

    def __repr__(self):
        return f"FuturesSpreadbetCosts spread {self.spread}, pointsize {self.pointsize}, min bet {self.min_bet}, " \
               f"multiplier {self.multiplier}"

    @property
    def spread(self):
        return self._spread

    @property
    def pointsize(self):
        return self._pointsize

    @property
    def min_bet(self):
        return self._min_bet

    @property
    def multiplier(self):
        return self._multiplier

    def get_sr_cost_per_trade_for_instrument(self, instr, block_price_multiplier, average_price,
            avg_annual_vol_perc) -> float:

        cost_in_percentage_terms = self.get_sr_cost_per_trade_for_instrument_percentage(instr)

        # cost per round trip
        SR_cost = cost_in_percentage_terms / avg_annual_vol_perc

        return SR_cost

    def get_sr_cost_per_trade_for_instrument_percentage(self, block_price_multiplier, average_price) -> float:

        cost_in_percentage_terms = self.calculate_cost_percentage_terms(
            blocks_traded=1,
            block_price_multiplier=block_price_multiplier,
            price=average_price
        )

        return cost_in_percentage_terms

    def calculate_total_commission(self, blocks_traded: float, value_per_block: float):
        return 0.0

    def get_holding_costs_per_instrument(self, instrument_code: str) -> float:
        pass

    def calculate_cost_instrument_currency(self, blocks_traded: float, block_price_multiplier: float, price: float):
        """
        Calculates Transaction cost per trade in instrument currency.

        This is TCccy as described in 'Leveraged Trading' p.294

        :param price: instrument price
        :type price: float
        :return: cost per trade in currency
        :rtype: float
        """

        # No commission with spread bets
        commission = 0.0
        tc_ccy = commission + ((self.spread * self.min_bet) / 2)

        print(f"SR TCccy: £{tc_ccy}")

        return tc_ccy

    def calculate_cost_percentage_terms(self, blocks_traded: float, block_price_multiplier: float,
            price: float) -> float:
        """
        This is TCratio, Leveraged Trading p.294

        :param blocks_traded:
        :type blocks_traded:
        :param block_price_multiplier:
        :type block_price_multiplier:
        :param price:
        :type price:
        :return:
        :rtype:
        """

        cost_in_currency_terms = self.calculate_cost_instrument_currency(
            blocks_traded,
            block_price_multiplier=block_price_multiplier,
            price=price)

        cost_in_percentage_terms = cost_in_currency_terms / ((self.min_bet * price) / self.pointsize)

        return cost_in_percentage_terms
