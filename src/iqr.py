import numpy as np

from .drops import Drops


class Iqr(Drops):
    def __init__(self, file_path: str, alpha: float = 1.5):
        super().__init__(file_path, alpha)

    def method(self):
        for placement in self.raw_placements:
            q1 = np.quantile(self.full_scores[placement["team"]], 0.25)
            q3 = np.quantile(self.full_scores[placement["team"]], 0.75)
            if (
                placement.get("place", len(self.teams)) > ((q3 - q1) * self.alpha + q3)
                and not placement["event"] in self.trial_events
            ):
                self.bombed_events[placement["team"]].append(placement["event"])

        super().method()
