from .drops import Drops


class Mean(Drops):
    def __init__(self, file_path: str, alpha: float = 2):
        super().__init__(file_path, alpha)

    def method(self):
        for placement in self.raw_placements:
            if (
                placement.get("place", len(self.teams))
                > self.averages[placement["team"]] * self.alpha
                and not placement["event"] in self.trial_events
            ):
                self.bombed_events[placement["team"]].append(placement["event"])

        super().method()
