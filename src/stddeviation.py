import numpy as np

from .drops import Drops


class StdDeviation(Drops):
    def __init__(self, file_path: str, alpha: float = 2):
        super().__init__(file_path, alpha)
        self.method()

    def method(self) -> None:
        for placement in self.raw_placements:
            mean = np.mean(self.full_scores[placement["team"]])
            std = np.std(self.full_scores[placement["team"]])
            if (
                placement.get("place", len(self.teams))
                > (mean + self.alpha * std)  # upper fence/bound
                and not placement["event"] in self.trial_events
            ):
                self.bombed_events[placement["team"]].append(placement["event"])
        super().method()
