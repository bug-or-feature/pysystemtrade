from syslogdiag.log_to_screen import logtoscreen
from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_static_data import brokerStaticData


class IgStaticData(brokerStaticData):
    def __init__(self, broker_conn: IGConnection, log=logtoscreen("IgStaticData")):
        self._igconnection = broker_conn
        super().__init__(log=log)

    def __repr__(self):
        return "IG static data %s" % str(self.igconnection)

    @property
    def igconnection(self) -> IGConnection:
        return self._igconnection

    def get_broker_account(self) -> str:
        return self._igconnection.get_account_number()

    def get_broker_name(self) -> str:
        return "IG"

    def get_broker_clientid(self) -> int:
        pass
