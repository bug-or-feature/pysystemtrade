from syscore.constants import arg_not_supplied
from syslogdiag.log_to_screen import logtoscreen

from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_fx_handling import brokerFxHandlingData
from sysdata.data_blob import dataBlob


class IgFxHandlingData(brokerFxHandlingData):
    def __init__(
        self,
        data_blob: dataBlob,
        broker_conn: IGConnection,
        log=logtoscreen("IgFxHandlingData"),
    ):
        super().__init__(log=log)
        self._dataBlob = data_blob
        self._broker_conn = broker_conn

    def __repr__(self):
        return "IG FX handling data %s" % str(self.broker_conn)

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

    @property
    def data(self):
        return self._dataBlob

    def broker_fx_balances(self, account_id: str = arg_not_supplied) -> dict:
        # return self.broker_conn.broker_fx_balances(account_id)
        return {"USD": 0.0}

    def broker_fx_market_order(
        self,
        trade: float,
        ccy1: str,
        account_id: str = arg_not_supplied,
        ccy2: str = "USD",
    ):
        pass
