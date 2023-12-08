from __future__ import annotations

from typing import Literal, Callable

import yaml
import numpy as np

import utils


class Drops:
    def __init__(
            self,
            file_path: str,
            method: Literal["std_deviation", "mean", "iqr"],
            alpha: float = None
    ):
        self.method: Callable = {"std_deviation": self.std_deviation, "mean": self.mean, "iqr": self.iqr}[method]
        self.alpha = alpha or 2
        self.data: dict = {}
        self.team_list: list[dict[str, str | int]] = []
        self.teams: dict[int, str] = {}
        self.full_scores: dict[int, list[int]] = {}
        self.events: list[str] = []
        self.trial_events: list[str] = []
        self.total_scores: dict[str, int] = {}
        self.averages: dict[int, float] = {}
        self.bombed_events: dict[int, list[str]] = {}

        self.path: str = file_path

        self.setup()

    def setup(self):
        with open(self.path, 'r') as file:
            self.data = yaml.safe_load(file)

        self.team_list = sorted(self.data.get("Teams"), key=lambda x: x['number'])
        self.teams = {team['number']: (team['school'] + " " + team.get('suffix', "")) for team in
                      self.team_list}  # team number : team name
        self.events = [event['name'] for event in self.data.get('Events')]
        self.trial_events = [d['name'] for d in self.data.get('Events') if d.get('trial', False)]
        self.total_scores = {t: 0 for t in self.teams}  # team number : total score (sum)
        self.full_scores = {t: [] for t in self.teams}  # full array of scores for each team

        for placement in self.data.get('Placings'):
            self.total_scores[placement['team']] += placement.get(
                'place', len(self.teams)
            ) if not placement['event'] in self.trial_events else 0

            self.full_scores[placement['team']].append(
                placement.get('place', len(self.teams))
            ) if not placement['event'] in self.trial_events else 0

        self.averages = {
            t: self.total_scores[t] / (len(self.data.get('Events')) - len(self.trial_events)) for t in self.teams
        }
        self.bombed_events = {t: [] for t in self.teams}

    def iqr(self):
        for placement in self.data.get('Placings'):
            q1 = np.quantile(self.full_scores[placement['team']], 0.25)
            q3 = np.quantile(self.full_scores[placement['team']], 0.75)
            if (placement.get('place', len(self.teams)) > ((q3 - q1) * self.alpha + q3)
                    and not placement['event'] in self.trial_events):
                self.bombed_events[placement['team']].append(placement['event'])

        print("\"Bombed\" events by school:", utils.pretty_print(self.teams, self.bombed_events), "\n")
        print(
            "Average \"bombed events\": ",
            sum([len(self.bombed_events[t]) for t in self.bombed_events]) / len(self.teams)
        )

    def mean(self):
        for placement in self.data.get('Placings'):
            if (placement.get('place', len(self.teams)) > self.averages[placement['team']] * self.alpha
                    and not placement['event'] in self.trial_events):
                self.bombed_events[placement['team']].append(placement['event'])

        print("\"Bombed\" events by school:", utils.pretty_print(self.teams, self.bombed_events), "\n")
        print(
            "Average \"bombed events\": ",
            sum([len(self.bombed_events[t]) for t in self.bombed_events]) / len(self.teams)
        )

    def std_deviation(self):
        for placement in self.data.get('Placings'):
            mean = np.mean(self.full_scores[placement['team']])
            std = np.std(self.full_scores[placement['team']])
            if (placement.get('place', len(self.teams)) > (mean + self.alpha * std)
                    and not placement['event'] in self.trial_events):
                self.bombed_events[placement['team']].append(placement['event'])

        print("\"Bombed\" events by school:", utils.pretty_print(self.teams, self.bombed_events), "\n")
        print(
            "Average \"bombed events\": ",
            sum([len(self.bombed_events[t]) for t in self.bombed_events]) / len(self.teams)
        )

    def drop(self) -> dict[str, int]:
        """

        :return:  dict[str, int], sorted scores {name: sum(event placements), ...} after dropping
        """
        self.method()
        score_copy = self.full_scores.copy()
        drops = round(sum([len(self.bombed_events[t]) for t in self.bombed_events]) / len(self.teams))

        for _ in range(drops):
            for team in score_copy:
                score_copy[team].remove(max(score_copy[team]))

        score_with_drops = {t: sum(score_copy[t]) for t in score_copy}

        sorted_scores = dict(sorted(score_with_drops.items(), key=lambda item: item[1]))
        print(f"After dropping {drops} events: \n")
        print(utils.pretty_print(self.teams, sorted_scores))

        return sorted_scores


if __name__ == '__main__':
    """
    Example usage:
    """
    drops = Drops("../data/2023-05-20_nationals_c.yaml", "std_deviation", alpha=1.25)
    drops.drop()
