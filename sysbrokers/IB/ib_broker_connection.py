from sysbrokers.broker_connection import brokerConnection
from sysbrokers.IB.ib_connection import connectionIB
from sysdata.mongodb.mongo_IB_client_id import mongoIbBrokerClientIdData


class ibBrokerConnection(brokerConnection):
    """
    Wraps connectionIB and its IB-specific lifecycle (client ID tracking)
    """

    def __init__(self, ib_conn: connectionIB, tracker: mongoIbBrokerClientIdData):
        self._ib_conn = ib_conn
        self._tracker = tracker

    def close_connection(self) -> None:
        self._ib_conn.close_connection()
        self._tracker.release_clientid(self._ib_conn.client_id())

    def connection_msg(self) -> str:
        cfg = self._ib_conn._ib_connection_config
        return f"{cfg['ipaddress']}:{cfg['port']}"

    def __getattr__(self, name: str):
        return getattr(self._ib_conn, name)

    def __repr__(self) -> str:
        return repr(self._ib_conn)
