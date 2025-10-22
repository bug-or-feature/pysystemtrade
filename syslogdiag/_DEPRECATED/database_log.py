from sysdata.base_data import baseData
from syslogdiag.pst_logger import pst_logger
from syslogdiag.log_to_screen import logtoscreen


LOG_COLLECTION_NAME = "Logs"
EMAIL_ON_LOG_LEVEL = [4]


class logData(baseData):
    def __init__(self, log: pst_logger = logtoscreen("logData")):
        super().__init__(log=log)

    def delete_log_items_from_before_n_days(self, lookback_days: int = 365):
        # need something to delete old log records, eg more than x months ago

        raise NotImplementedError
