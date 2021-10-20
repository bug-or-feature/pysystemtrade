from syslogdiag.log_to_screen import logtoscreen
from sysbrokers.IG.client.ig_client import IgClient
from sysbrokers.IG.ig_connection import ConnectionIG
from sysbrokers.broker_static_data import brokerStaticData


class IgStaticData(brokerStaticData):

    def __init__(self, log=logtoscreen("IgStaticData")):
        self._igconnection = ConnectionIG()
        super().__init__(log=log)

    def __repr__(self):
        return "IG static data %s" % str(self.ig_client)

    @property
    def igconnection(self) -> ConnectionIG:
        return self._igconnection

    @property
    def ig_client(self) -> IgClient:
        client = getattr(self, "_ig_client", None)
        if client is None:
             client = self._ig_client = IgClient(igconnection=self.igconnection, log=self.log)
        return client

    def get_broker_account(self) -> str:
        return self._igconnection.get_account_number()

    def get_broker_name(self) -> str:
        return "IG"

    def get_broker_clientid(self) -> int:
        pass


