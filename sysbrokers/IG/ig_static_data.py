from syslogdiag.log_to_screen import logtoscreen
from sysbrokers.IG.ig_connection import IGConnection
from sysbrokers.broker_static_data import brokerStaticData
from sysdata.data_blob import dataBlob


class IgStaticData(brokerStaticData):
    def __init__(
        self,
        broker_conn: IGConnection,
        data: dataBlob,
        log=logtoscreen("IgStaticData"),
    ):
        super().__init__(log=log, data=data)
        self._broker_conn = broker_conn

    def __repr__(self):
        return f"IG static data {self.broker_conn}"

    @property
    def broker_conn(self) -> IGConnection:
        return self._broker_conn

    def get_broker_account(self) -> str:
        return self.broker_conn.get_account_number()

    def get_broker_name(self) -> str:
        return "IG"

    def get_broker_clientid(self) -> int:
        pass
