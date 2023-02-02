import pandas as pd
from dataclasses import dataclass, field, InitVar
from datetime import datetime, timedelta
from syscore.dateutils import contract_month_from_number


class FsbEpicsHistory(pd.DataFrame):
    def __init__(self, data):
        super().__init__(data)
        data.index.name = "index"

    @classmethod
    def create_empty(cls):
        return FsbEpicsHistory(pd.DataFrame())

    def roll_chain(self):
        datetime_now = datetime.now() - timedelta(100)
        raw = self._extract_raw_roll_chain()

        return [item.pst_date_key for item in raw if item.epic_key_date >= datetime_now]

    def _extract_raw_roll_chain(self):
        results = []
        for row in self.to_dict(orient="records"):
            for value in row.values():
                try:
                    results.append(BetExpiry(value))
                except:
                    # print("unmapped, ignoring")
                    pass

        my_set = set(results)
        try:
            sorted_set = sorted(my_set)
            return sorted_set
        except Exception as exc:
            print(exc)


@dataclass(order=True)
class BetExpiry:
    str_val: InitVar[str]
    sort_index: int = field(init=False, repr=False)
    epic_key: str = field(init=False)
    epic_key_date: datetime = field(init=False)
    expiry_date: datetime = field(init=False)
    month_key: str = field(init=False)
    # status: str = field(init=False)
    pst_date_key: str = field(init=False)

    def __post_init__(self, str_val):

        if str_val != "unmapped":
            self.epic_key = str_val[:6]
            self.expiry_date = datetime.strptime(str_val[8:27], "%Y-%m-%d %H:%M:%S")
            self.epic_key_date = datetime.strptime(self.epic_key, "%b-%y")
            self.month_key = contract_month_from_number(self.epic_key_date.month)
            self.pst_date_key = self.epic_key_date.strftime("%Y%m00")
            self.sort_index = self.epic_key_date
        else:
            raise Exception("Bad row")

    def __eq__(self, other):
        if not isinstance(other, BetExpiry):
            return NotImplemented
        return self.epic_key == other.epic_key

    def __hash__(self) -> int:
        return hash(self.epic_key)

    def __repr__(self):
        return f"{self.epic_key} {self.month_key} {self.expiry_date}"
