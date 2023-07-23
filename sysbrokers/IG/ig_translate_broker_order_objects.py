from sysbrokers.broker_trade import brokerTrade


class IgTradeWithContract(brokerTrade):
    def __init__(self, attrs: dict):
        self._attrs = attrs

    def __repr__(self):
        return f"IgTradeWithContract: {self._attrs}"

    def get_attr(self, name):
        return self._attrs[name]
