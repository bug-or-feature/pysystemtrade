from sysbrokers.broker_activity_data import BrokerActivityData
from sysbrokers.IG.ig_connection import ConnectionIG
from sysbrokers.IG.ig_instruments_data import IgFsbInstrumentData
from syslogdiag.logger import logger
from syslogdiag.log_to_screen import logtoscreen


class IgActivityData(BrokerActivityData):

    def __init__(self, log: logger = logtoscreen("IgActivityData")):
        super().__init__(log=log)
        self._igconnection = ConnectionIG()

    @property
    def igconnection(self) -> ConnectionIG:
        return self._igconnection

    @property
    def futures_instrument_data(self) -> IgFsbInstrumentData:
        return IgFsbInstrumentData(log=self.log)

    def get_recent(self):
        return self.igconnection.get_activity()
