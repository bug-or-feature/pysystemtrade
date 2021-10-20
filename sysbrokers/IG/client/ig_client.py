from sysbrokers.IG.ig_connection import ConnectionIG
from trading_ig import IGService
from syslogdiag.logger import logger
from syslogdiag.log_to_screen import logtoscreen


class IgClient(object):
    """
    Client specific to IG
    """

    def __init__(self, igconnection: ConnectionIG, log: logger = logtoscreen("IgClient")):
        self._ig_connnection = igconnection
        self._log = log

    @property
    def ig_connection(self) -> ConnectionIG:
        return self._ig_connnection

    @property
    def ig(self) -> IGService:
        return self.ig_connection.service

    @property
    def log(self):
        return self._log
