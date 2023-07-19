from trading_ig.lightstreamer import Subscription
from syslogging.logger import *


class IgTicker:

    _instances = {}

    @classmethod
    def get_instance(cls, connection, epic):
        if epic not in cls._instances:
            print(f"Creating new ticker for {epic}")
            ticker = super(IgTicker, cls).__new__(cls)
            ticker._connection = connection
            ticker._log = get_logger("igTicker")
            ticker._bid = 0.0
            ticker._ask = 0.0
            ticker._bid_size = 0
            ticker._ask_size = 0
            ticker._key = None
            ticker._epic = epic
            ticker._subscribe()
            cls._instances[epic] = ticker

        return cls._instances.get(epic)

    # def __init__(self, connection, epic):
    #     self._connection = connection
    #     self._log = get_logger("igTicker")
    #     self._bid = 0.0
    #     self._ask = 0.0
    #     self._bid_size = 0
    #     self._ask_size = 0
    #     self._key = None
    #     self._epic = epic
    #     self._subscribe()

    def __repr__(self) -> str:
        return (
            f"IgTicker for '{self._epic}', bid {self._bid}, ask {self._ask}, "
            f"bid_size {self._bid_size}, ask_size {self._ask_size}"
        )

    @property
    def bid(self):
        return self._bid

    @property
    def ask(self):
        return self._ask

    @property
    def bidSize(self):
        return self._ask_size

    @property
    def askSize(self):
        return self._bid_size

    def _subscribe(self):
        subscription = Subscription(
            mode="DISTINCT",
            items=[f"CHART:{self._epic}:TICK"],
            fields=["UTM", "BID", "OFR", "LTV"],
        )
        subscription.addlistener(self._on_update)
        self._key = self._connection.stream_service.ls_client.subscribe(subscription)
        self._log.debug(f"subscription key: {self._key}")

    def _unsubscribe(self):
        self._connection.stream_service.ls_client.unsubscribe(self._key)

    def set_bid(self, value):
        try:
            self._bid = float(value)
        except TypeError:
            # ignore, there will be plenty of dud values
            pass

    def set_ask(self, value):
        try:
            self._ask = float(value)
        except TypeError:
            # ignore, there will be plenty of dud values
            pass

    def set_sizes(self, value):
        try:
            new_size = int(value)
            self._bid_size = new_size
            self._ask_size = new_size
        except TypeError:
            # ignore, there will be plenty of dud values
            pass

    def _on_update(self, item_update):
        # self._log.debug(f"item_update: {item_update}")
        update_values = item_update["values"]
        self.set_bid(update_values["BID"])
        self.set_ask(update_values["OFR"])
        self.set_sizes(update_values["LTV"])
        self._log.info(self)
