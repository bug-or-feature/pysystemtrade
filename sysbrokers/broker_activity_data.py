from syslogdiag.logger import logger
from syslogdiag.log_to_screen import logtoscreen

class BrokerActivityData:

    def __init__(self,  log: logger=logtoscreen("BrokerActivityData")):
        pass

    def get_recent(self):
        raise NotImplementedError
