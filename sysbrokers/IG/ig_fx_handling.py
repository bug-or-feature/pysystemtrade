from syscore.objects import arg_not_supplied
from syslogdiag.log_to_screen import logtoscreen

from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_fx_handling import brokerFxHandlingData


class IgFxHandlingData(brokerFxHandlingData):

    def __init__(self, broker_conn: IGConnection, log=logtoscreen("IgFxHandlingData")):
        self._igconnection = broker_conn
        super().__init__(log=log)

    def __repr__(self):
        return "IG FX handling data %s" % str(self.igconnection)

    @property
    def igconnection(self) -> IGConnection:
        return self._igconnection

    def broker_fx_balances(self, account_id: str = arg_not_supplied) -> dict:
        #return self.igconnection.broker_fx_balances(account_id)
        return {"USD": 0.0}

    def broker_fx_market_order(
        self,
        trade: float,
        ccy1: str,
        account_id: str = arg_not_supplied,
        ccy2: str = "USD",
    ):
        pass
