from __future__ import annotations

from typing import Literal, Callable

import numpy as np
import matplotlib.pyplot as plt

import utils
from utils.results import Results


class Drops(Results):
    def __init__(
            self,
            file_path: str,
            method: Literal["std_deviation", "mean", "iqr"],
            alpha: float = None
    ):
        super().__init__(file_path)
        self._method: Callable = {"std_deviation": self.std_deviation, "mean": self.mean, "iqr": self.iqr}[method]
        self.alpha = alpha or 2
        self.dropped_scores: dict[int, int] = {}
        self.bombed_events: dict[int, list[str]]
        self.averaged_bombed_events = sum([len(self.bombed_events[t]) for t in self.bombed_events]) / len(self.teams)

    def _populate(self) -> None:
        super()._populate()
        self.bombed_events = {t: [] for t in self.teams}

    def iqr(self):
        for placement in self.raw_placements:
            q1 = np.quantile(self.full_scores[placement['team']], 0.25)
            q3 = np.quantile(self.full_scores[placement['team']], 0.75)
            if (placement.get('place', len(self.teams)) > ((q3 - q1) * self.alpha + q3)
                    and not placement['event'] in self.trial_events):
                self.bombed_events[placement['team']].append(placement['event'])

    def mean(self):
        for placement in self.raw_placements:
            if (placement.get('place', len(self.teams)) > self.averages[placement['team']] * self.alpha
                    and not placement['event'] in self.trial_events):
                self.bombed_events[placement['team']].append(placement['event'])

    def std_deviation(self) -> None:
        for placement in self.raw_placements:
            mean = np.mean(self.full_scores[placement['team']])
            std = np.std(self.full_scores[placement['team']])
            if (placement.get('place', len(self.teams)) > (mean + self.alpha * std)
                    and not placement['event'] in self.trial_events):
                self.bombed_events[placement['team']].append(placement['event'])

    def drop(self) -> None:
        """

        :return:  dict[str, int], sorted scores {name: sum(event placements), ...} after dropping
        """
        self._method()
        score_copy = self.full_scores
        drop = round(sum([len(self.bombed_events[t]) for t in self.bombed_events]) / len(self.teams))

        for _ in range(drop):
            for team in score_copy:
                score_copy[team].remove(max(score_copy[team]))

        score_with_drops = {t: sum(score_copy[t]) for t in score_copy}

        sorted_scores = dict(sorted(score_with_drops.items(), key=lambda item: item[1]))
        # print(f"After dropping {drop} events: \n")
        # print(utils.pretty_print(self.teams, sorted_scores))
        self.dropped_scores = sorted_scores
        # return sorted_scores

    def visualize(self):
        fig, ax = plt.subplots()
        ax.set_title("Distribution of scores")
        ax.set_xlabel("Team Placement")
        ax.set_ylabel("Score")

        non_drop_rankings = sorted(self.score_sum, key=self.score_sum.get)
        drop_rankings = sorted(self.dropped_scores, key=self.dropped_scores.get)

        colors = {k: (np.random.random(), np.random.random(), np.random.random()) for k in self.teams}
        ndrop_data = [(non_drop_rankings.index(i) + 1, self.score_sum[i], colors[i]) for i in self.teams]
        drop_data = [(drop_rankings.index(i) + 1, self.dropped_scores[i], colors[i]) for i in self.teams]

        ndrop_x, ndrop_y, ndrop_color = zip(*ndrop_data)
        drop_x, drop_y, drop_color = zip(*drop_data)

        ax.scatter(x=ndrop_x, y=ndrop_y, color=ndrop_color, label="Before dropping", marker="o")
        ax.scatter(x=drop_x, y=drop_y, color=drop_color, label="After dropping", marker="*")

        ax.set(xlim=(0, 61), xticks=np.arange(start=0, stop=61, step=5),
               ylim=(0, 1000), yticks=np.arange(start=0, stop=max(self.score_sum.values()) + 200, step=100))
        plt.legend(loc="upper left")
        plt.show()


if __name__ == '__main__':
    """
    Example usage:
    """
    drops = Drops("../data/2023-02-18_penn_invitational_c.yaml", "std_deviation", alpha=1.25)
    drops.drop()
    drops.visualize()
