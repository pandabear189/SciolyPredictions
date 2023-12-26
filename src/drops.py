from __future__ import annotations

from textwrap import wrap
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
        alpha: float = None,
    ):
        super().__init__(file_path)
        self._method: Callable = {
            "std_deviation": self.std_deviation,
            "mean": self.mean,
            "iqr": self.iqr,
        }[method]
        self.alpha = alpha or 2
        self.dropped_scores: dict[int, int] = {}
        self.bombed_events: dict[int, list[str]]
        self.averaged_bombed_events = sum(
            [len(self.bombed_events[t]) for t in self.bombed_events]
        ) / len(self.teams)
        self._teams_without_suffix: dict[int, str] = {}
        self._populate()
        self.__dropped: bool = False
        self.non_trial_events: list = []
        self._ret_scores: dict[str, int] = {}
        self.to_drop = 0

    def _populate(self) -> None:
        super()._populate()
        self.bombed_events = {t: [] for t in self.teams}
        self._teams_without_suffix = {
            team["number"]: team["school"] for team in self._teams_data
        }
        self._non_trials = [
            event for event in self.events if event not in self.trial_events
        ]

    def iqr(self):
        for placement in self.raw_placements:
            q1 = np.quantile(self.full_scores[placement["team"]], 0.25)
            q3 = np.quantile(self.full_scores[placement["team"]], 0.75)
            if (
                placement.get("place", len(self.teams)) > ((q3 - q1) * self.alpha + q3)
                and not placement["event"] in self.trial_events
            ):
                self.bombed_events[placement["team"]].append(placement["event"])

    def mean(self):
        for placement in self.raw_placements:
            if (
                placement.get("place", len(self.teams))
                > self.averages[placement["team"]] * self.alpha
                and not placement["event"] in self.trial_events
            ):
                self.bombed_events[placement["team"]].append(placement["event"])

    def std_deviation(self) -> None:
        for placement in self.raw_placements:
            mean = np.mean(self.full_scores[placement["team"]])
            std = np.std(self.full_scores[placement["team"]])
            if (
                placement.get("place", len(self.teams)) > (mean + self.alpha * std)
                and not placement["event"] in self.trial_events
            ):
                self.bombed_events[placement["team"]].append(placement["event"])

    def drop(self) -> None:
        """
        :return:  dict[str, int], sorted scores {name: sum(event placements), ...} after dropping
        """
        self._method()
        score_copy = self.full_scores
        drop = round(
            sum([len(self.bombed_events[t]) for t in self.bombed_events])
            / len(self.teams)
        )
        self.to_drop = drop

        for _ in range(drop):
            for team in score_copy:
                score_copy[team].remove(max(score_copy[team]))

        score_with_drops = {t: sum(score_copy[t]) for t in score_copy}

        sorted_scores = dict(sorted(score_with_drops.items(), key=lambda item: item[1]))
        self.dropped_scores = sorted_scores
        self.__dropped = True
        # return sorted_scores

    def __handle_model(self) -> None:
        tnumber_sum_results = {t: np.sum(self.full_scores[t]) for t in self.teams}
        print(len(self.non_trial_events), len(self.teams)   )
        f_results = {t: len(self._non_trials)*len(self.teams) for t in self.team_names}
        for t in tnumber_sum_results:
            tname = self._teams_without_suffix[t]
            f_results[tname] = min(f_results[tname], tnumber_sum_results[t])

        self._ret_scores = f_results

    @property
    def ret_scores(self) -> dict[str, int]:
        self.__handle_model()
        if not self.__dropped:
            raise NotImplementedError("You must drop scores before returning")
        return dict(sorted(self._ret_scores.items(), key=lambda item: item[1]))

    def visualize(self):
        if not self.__dropped:
            raise NotImplementedError("You must drop scores before visualizing")
        fig, ax = plt.subplots()
        ax.set_title(
            "\n".join(
                wrap(
                    f"Drop vs Original Results ({self.tournament.get('name', self.tournament['location'])})"
                )
            )
        )
        ax.set_xlabel("Team Placement")
        ax.set_ylabel("Score")

        non_drop_rankings = sorted(self.score_sum, key=self.score_sum.get)
        drop_rankings = sorted(self.dropped_scores, key=self.dropped_scores.get)

        colors = {
            k: (np.random.random(), np.random.random(), np.random.random())
            for k in self.teams
        }
        ndrop_data = [
            (non_drop_rankings.index(i) + 1, self.score_sum[i], colors[i])
            for i in self.teams
        ]
        drop_data = [
            (drop_rankings.index(i) + 1, self.dropped_scores[i], colors[i])
            for i in self.teams
        ]

        ndrop_x, ndrop_y, ndrop_color = zip(*ndrop_data)
        drop_x, drop_y, drop_color = zip(*drop_data)

        ax.scatter(
            x=ndrop_x, y=ndrop_y, color=ndrop_color, label="Before dropping", marker="o"
        )
        ax.scatter(
            x=drop_x, y=drop_y, color=drop_color, label="After dropping", marker="*"
        )

        ax.set(
            xlim=(0, len(self.teams)),
            xticks=np.arange(start=0, stop=len(self.teams) + 4, step=5),
            ylim=(0, 1000),
            yticks=np.arange(
                start=0, stop=max(self.score_sum.values()) + 200, step=100
            ),
        )
        plt.legend(loc="upper left")
        plt.show()
        super().visualize()


if __name__ == "__main__":
    """
    Example usage:
    """
    drops = Drops(
        "../data/2023-02-18_penn_invitational_c.yaml", "std_deviation", alpha=1.25
    )
    drops.drop()
    utils.pretty_print(drops.teams, drops.dropped_scores)
    print(drops.ret_scores)
    drops.visualize()
