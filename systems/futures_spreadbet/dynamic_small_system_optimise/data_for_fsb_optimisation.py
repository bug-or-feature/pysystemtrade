import numpy as np

from systems.provided.dynamic_small_system_optimise.data_for_optimisation import (
    dataForOptimisation,
)


class dataForFsbOptimisation(dataForOptimisation):
    def __init__(self, obj_instance: "objectiveFsbFunctionForGreedy"):
        super().__init__(obj_instance)
        self.min_bets = obj_instance.min_bets

    @property
    def min_bets_as_np(self) -> np.array:
        return self.get_key("min_bets_as_np")

    @property
    def labels_as_np(self) -> np.array:
        return self.get_key("labels_as_np")

    @property
    def _min_bets_as_np(self) -> np.array:
        min_bets_as_np = np.array(
            self.min_bets.as_list_given_keys(self.keys_with_valid_data)
        )

        return min_bets_as_np

    @property
    def _labels_as_np(self) -> np.array:
        # labels_as_np = np.array(list(self.min_bets.keys()))
        labels_as_np = np.array(self.keys_with_valid_data)
        return labels_as_np

    def min_bet_for_code(self, instrument_code: str) -> float:
        min_bets = self.min_bets
        return min_bets.get(instrument_code, np.isnan)
