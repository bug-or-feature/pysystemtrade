import pandas as pd
import datetime

from syscore.dateutils import n_days_ago
from syscore.exceptions import missingData


class spreadsForInstrument(pd.Series):
    def add_spread(self, spread: float, current_time=None):
        if current_time is None:
            current_time = datetime.datetime.now()
        new_row = pd.Series(spread, index=[current_time])

        # TODO fix FutureWarning: The behavior of array concatenation with empty entries
        #  is deprecated. In a future version, this will no longer exclude empty items
        #  when determining the result dtype. To retain the old behavior, exclude the
        #  empty entries before the concat operation
        return spreadsForInstrument(pd.concat([self, new_row], axis=0))

    def average_spread_last_n_days(self, n_days: int = 14):
        recent_data = self[n_days_ago(n_days)]
        if len(recent_data) == 0:
            raise missingData

        return recent_data.mean(skipna=True)
