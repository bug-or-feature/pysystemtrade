"""
IB connection using ib-insync https://ib-insync.readthedocs.io/api.html
"""

import time

from ib_insync import IB

from sysbrokers.IB.ib_connection_defaults import ib_defaults
from sysbrokers.IB.ib_contracts import ibContract
from syscore.exceptions import missingData
from syscore.constants import arg_not_supplied

from syslogging.logger import *

from sysdata.config.production_config import get_production_config

IB_ERROR_TYPES = {
    100: "Max messages exceeded",
    102: "Duplicate ticker",
    103: "Duplicate orderid",
    104: "can't modify filled order",
    105: "trying to modify different order",
    106: "can't transmit orderid",
    107: "can't transmit incomplete order",
    109: "price out of range",
    110: "tick size wrong for price",
    122: "No request tag has been found for order",
    123: "invalid conid",
    133: "submit order failed",
    134: "modify order failed",
    135: "cant find order",
    136: "order cant be cancelled",
    140: "size should be an integer",
    141: "price should be a double",
    200: "ambiguous contract",
    201: "order rejected",
    202: "order cancelled",
    501: "already connected",
    502: "can't connect",
    503: "TWS need upgrading",
}

IB_IS_ERROR = list(IB_ERROR_TYPES.keys())


class connectionIB(object):
    """
    Connection object for connecting IB
    (A database plug in will need to be added for streaming prices)
    """

    def __init__(
        self,
        client_id: int,
        ib_ipaddress: str = arg_not_supplied,
        ib_port: int = arg_not_supplied,
        account: str = arg_not_supplied,
        log_name: str = "connectionIB",
    ):
        """
        :param client_id: client id
        :param ib_ipaddress: IP address of machine running IB Gateway or TWS. If not
          passed then will get from private config file, or defaults
        :param ib_port: Port listened to by IB Gateway or TWS
        :param log_name: calling log name

        """

        # resolve defaults
        ipaddress, port, __ = ib_defaults(ib_ipaddress=ib_ipaddress, ib_port=ib_port)
        self._ib_connection_config = dict(
            ipaddress=ipaddress, port=port, client=client_id
        )

        # The client id is pulled from a mongo database
        # If for example you want to use a different database you could do something like:
        # connectionIB(mongo_ib_tracker =
        # mongoIBclientIDtracker(database_name="another")

        # If you copy for another broker include these lines
        self._log = get_logger(
            "connectionIB",
            {
                TYPE_LOG_LABEL: log_name,
                BROKER_LOG_LABEL: "IB",
                CLIENTID_LOG_LABEL: client_id,
            },
        )

        # You can pass a client id yourself, or let IB find one

        try:
            self._init_connection(
                ipaddress=ipaddress, port=port, client_id=client_id, account=account
            )
        except Exception as e:
            # Log all exceptions generated during connection as critical error.
            # Under the default production setup this should send an email.
            # Error is reraised as we can't really continue and user intervention is required
            self.log.critical(
                f"IB connection failed with exception - {e}, connection aborted."
            )
            raise

    def _init_connection(
        self, ipaddress: str, port: int, client_id: int, account=arg_not_supplied
    ):
        ib = IB()

        try:
            if account is arg_not_supplied:
                ## not passed get from config
                account = get_broker_account()
        except missingData:
            self.log.error(
                "Broker account ID not found in private config - may cause issues"
            )
            ib.connect(ipaddress, port, clientId=client_id)
        else:
            ## connect using account
            ib.connect(ipaddress, port, clientId=client_id, account=account)

        # Sometimes takes a few seconds to resolve... only have to do this once per process so no biggie
        time.sleep(5)

        # Add error handler
        ib.errorEvent += self.error_handler

        self._ib = ib
        self._account = account

    @property
    def ib(self):
        return self._ib

    @property
    def log(self):
        return self._log

    def __repr__(self):
        return "IB broker connection" + str(self._ib_connection_config)

    def client_id(self):
        return self._ib_connection_config["client"]

    @property
    def account(self):
        return self._account

    def error_handler(
        self, reqid: int, error_code: int, error_string: str, ib_contract: ibContract
    ):
        """
        Error handler called from server

        :param reqid: IB reqid
        :param error_code: IB error code
        :param error_string: IB error string
        :param ib_contract: IB contract or None
        :return: success
        """

        contract = f"{str(ib_contract)}" if ib_contract else ""
        if error_code in IB_IS_ERROR:
            # Serious requires some action
            myerror_type = IB_ERROR_TYPES.get(error_code, "generic")
            self.log.warning(
                f"Reqid {reqid}: {error_code} ({myerror_type}) {error_string} {contract}"
            )
        else:
            self.log.info(f"Reqid {reqid}: {error_code} {error_string} {contract}")

    def close_connection(self):
        self.log.debug("Terminating %s" % str(self._ib_connection_config))
        try:
            # Try and disconnect IB client
            self.ib.disconnect()
        except BaseException:
            self.log.warning(
                "Trying to disconnect IB client failed... ensure process is killed"
            )


def get_broker_account() -> str:
    production_config = get_production_config()
    account_id = production_config.get_element("broker_account")
    return account_id
