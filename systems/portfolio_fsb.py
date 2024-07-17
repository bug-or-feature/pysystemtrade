from sysquant.optimisation.weights import portfolioWeights
from systems.portfolio import Portfolios


"""
Stage for portfolios, with some FSB specific methods

Gets the position, accounts for instrument weights and diversification
multiplier
"""


class FsbPortfolios(Portfolios):
    def get_min_bet_for_instrument(self, instrument_code: str) -> float:
        min_bet = self.get_contract_multiplier(instrument_code)
        return min_bet

    def get_minimum_bets(self) -> portfolioWeights:
        instrument_list = self.get_instrument_list()
        values_as_dict = dict(
            [
                (
                    instrument_code,
                    self.get_min_bet_for_instrument(instrument_code),
                )
                for instrument_code in instrument_list
            ]
        )

        return portfolioWeights(values_as_dict)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
