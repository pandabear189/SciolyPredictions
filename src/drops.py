from __future__ import annotations

from textwrap import wrap
import numpy as np
import matplotlib.pyplot as plt

from utils.results import Results


class Drops(Results):
    def __init__(
        self,
        file_path: str,
        alpha: float = None,
    ):
        super().__init__(file_path)
        self.alpha = alpha or 2
        self.dropped_scores: dict[int, int] = {}
        self.bombed_events: dict[int, list[str]]
        self.averaged_bombed_events = sum(
            [len(self.bombed_events[t]) for t in self.bombed_events]
        ) / len(self.teams)
        self._teams_without_suffix: dict[int, str] = {}
        self._populate()
        self.non_trial_events: list = []
        self._ret_scores: dict[str, int] = {}
        self.to_drop = 0
        self._dropped = False

    def _populate(self) -> None:
        super()._populate()
        self.bombed_events = {t: [] for t in self.teams}
        self._teams_without_suffix = {
            team["number"]: team["school"] for team in self._teams_data
        }
        self._non_trials = [
            event for event in self.events if event not in self.trial_events
        ]

    def method(self):
        # to be implemented by subclasses
        pass

    def drop(self) -> None:
        """
        :return:  dict[str, int], sorted scores {name: sum(event placements), ...} after dropping
        """
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
        self._dropped = True
        # return sorted_scores

    def __handle_model(self) -> None:
        tnumber_sum_results = {t: np.sum(self.full_scores[t]) for t in self.teams}
        f_results = {
            t: len(self._non_trials) * len(self.teams) for t in self.team_names
        }
        for t in tnumber_sum_results:
            tname = self._teams_without_suffix[t]
            f_results[tname] = min(f_results[tname], tnumber_sum_results[t])

        self._ret_scores = f_results

    @property
    def ret_scores(self) -> dict[str, int]:
        self.__handle_model()
        return dict(sorted(self._ret_scores.items(), key=lambda item: item[1]))

    def visualize(self):
        if not self._dropped:
            raise ValueError(f"Must drop first {self.__repr__()}.drop()")
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
            xlim=(0, len(self.teams) + 4),
            xticks=np.arange(start=0, stop=len(self.teams) + 4, step=5),
            ylim=(0, max(self.score_sum.values()) + 200),
            yticks=np.arange(
                start=0, stop=max(self.score_sum.values()) + 200, step=100
            ),
        )
        plt.legend(loc="upper left")
        plt.show()
        super().visualize()
