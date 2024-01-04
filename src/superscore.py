from textwrap import wrap

import numpy as np
from matplotlib import pyplot as plt

from utils.results import Results


class SuperScoreModel(Results):
    def __init__(self, results_path: str, weight: float):
        super().__init__(results_path)
        self._super_scores: dict[str, int] = {}
        self._super_placements: dict[int, list[int]] = {}
        self._super_averages: dict[int, float] = {}
        self._pre_aggregate_scores: dict[str, list[int]] = {}
        self._teams_without_suffix: dict[int, str] = {}
        self._full_res_wo_suffix: dict[int, list[int]] = {}
        self.weight = weight
        self._populate()
        self._non_trials: list[str] = []

    def _populate(self) -> None:
        super()._populate()
        self._non_trials = [
            event for event in self.events if event not in self.trial_events
        ]
        self._teams_without_suffix = {
            team["number"]: team["school"] for team in self._teams_data
        }
        self._aggregate_scores()
        self._calculate_super_scores()

    @property
    def teams_without_suffix(self) -> dict[int, str]:
        """
        :return: Dictionary of team numbers and names WITHOUT SUFFIX
        Helper attr for superscoring
        """
        return self._teams_without_suffix

    @property
    def super_scores(self) -> dict[str, int]:
        """
        :return: Dictionary of team names and super scores
        Sorted In Ascending Order
        """
        return dict(sorted(self._super_scores.items(), key=lambda x: x[1]))

    def _aggregate_scores(self) -> None:
        data = {
            t: [
                len(self.teams) + 1
                for _ in range(len(self.events) - len(self.trial_events))
            ]
            for t in self.team_names
        }
        for placement in self.raw_placements:
            team_number = placement["team"]
            t_name = self.teams_without_suffix[team_number]
            if placement["event"] not in self.trial_events:
                data[t_name][self._non_trials.index(placement["event"])] = min(
                    data[t_name][self._non_trials.index(placement["event"])],
                    placement.get("place", len(self.teams) + 1),
                )
            self._pre_aggregate_scores = data

    def _calculate_super_scores(self) -> None:
        self._super_scores = {
            t: np.sum(self._pre_aggregate_scores[t]) for t in self.team_names
        }

    def visualize(self) -> None:
        """
        :return: None
        Prints out the super scores in a nice format
        """
        fig, ax = plt.subplots()
        ax.set_title(
            "\n".join(
                wrap(
                    f"Super Score vs. Original Results ({self.tournament.get('name', self.tournament['location'])}"
                )
            )
        )
        ax.set_xlabel("Team Placement")
        ax.set_ylabel("Score")

        colors = {
            t: (np.random.random(), np.random.random(), np.random.random())
            for t in self.team_names
        }
        super_data = [
            (i + 1, score, colors[team])
            for i, (team, score) in enumerate(self.super_scores.items())
        ]
        supX, supY, supC = zip(*super_data)

        before_data = [
            (i + 1, np.sum(score), colors[self.teams_without_suffix[team]])
            for i, (team, score) in enumerate(
                sorted(self.full_scores.items(), key=lambda x: np.sum(x[1]))
            )
        ]
        befX, befY, befC = zip(*before_data)
        ax.scatter(supX, supY, color=supC, label="Super Scores", marker="*", s=16)
        ax.scatter(befX, befY, color=befC, label="Original Results", marker=0, s=15)
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

    # Demo


if __name__ == "__main__":
    model = SuperScoreModel("../data/2023-02-18_penn_invitational_c.yaml")
    print(model.super_scores)
    model.visualize()
