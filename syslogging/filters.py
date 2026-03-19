import logging


class IBFilter(logging.Filter):
    """
    Custom log filter for 'ib-insync'. Should be added at handler level
    """

    def __init__(self):
        super().__init__("ib_async")

    def filter(self, record):
        # for all records with name starting 'ib_insync'
        if record.name.startswith(self.name):
            # if msg starts with 'Warning', then set the level to WARNING and allow
            if record.msg.startswith("Warning"):
                record.levelname = "WARNING"
                record.levelno = 30
                return True
            # don't allow INFO or lower
            if record.levelno < 25:
                return False
        # otherwise allow
        return True
