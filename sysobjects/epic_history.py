import pandas as pd


class FsbEpicsHistory(pd.DataFrame):
    def __init__(self, data):
        super().__init__(data)
        data.index.name = "index"

    @classmethod
    def create_empty(cls):
        return FsbEpicsHistory(pd.DataFrame())
