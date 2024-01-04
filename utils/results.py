from __future__ import annotations

from typing import Generator
import numpy as np
import yaml


class Results:
    def __init__(self, results_path) -> None:
        self.results_path = results_path
        self._data: dict = {}
        self._populate()
        self._teams_data: list[dict[str, str | int]]
        self._teams: dict[int, str]
        self._events: list[str]
        self._trial_events: list[str]
        self._full_scores: dict[int, list[int]]
        self._score_sum: dict[int, int]
        self._averages: dict[int, float]
        self._raw_placements: list[dict[str, str | int]]
        self._team_names: set[str]
        self._weight: float = 0

    def __lt__(self, other) -> bool:
        return self.weight < other.weight

    def __gt__(self, other) -> bool:
        return self.weight > other.weight

    def __eq__(self, other) -> bool:
        return self.weight == other.weight

    def __float__(self) -> float:
        return self.weight

    def _populate(self) -> None:
        self._load_data()
        self._teams_data = sorted(self._data.get("Teams"), key=lambda x: x["number"])
        self._teams = {
            team["number"]: (team["school"] + " " + team.get("suffix", ""))
            for team in self._teams_data
        }
        self._events = [event["name"] for event in self._data.get("Events")]
        self._trial_events = [
            event["name"]
            for event in self._data.get("Events")
            if event.get("trial", False)
        ]
        full_scores = {t: [] for t in self.teams}
        for placement in self._data.get("Placings"):
            team_number = placement["team"]
            full_scores[team_number].append(
                placement.get("place", len(self.teams))
            ) if placement["event"] not in self.trial_events else 0
        self._full_scores = full_scores
        self._score_sum = {t: np.sum(self.full_scores[t]) for t in self.teams}
        self._averages = {
            t: self.score_sum[t] / (len(self.events) - len(self.trial_events))
            for t in self.teams
        }
        self._raw_placements = self._data.get("Placings")
        self._team_names = set([g["school"] for g in self.teams_data])

    def _load_data(self) -> None:
        with open(self.results_path, "r") as file:
            self._data = yaml.safe_load(file)

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        self._weight = value

    @property
    def teams_data(self) -> list[dict[str, str | int]]:
        """
        :return: List of dictionaries containing team data
        :exe: [{'number': 1, 'school': 'School Name', 'suffix': 'A'}, ...]
        """

        return self._teams_data

    @property
    def teams(self) -> dict[int, str]:
        """
        :return: Dictionary of team numbers and names
        :exe: {1: 'School Name A', 2: 'School Name B', ...}
        """

        return self._teams

    @property
    def events(self) -> list[str]:
        """
        :return: List of event names
        :exe: ['Event 1', 'Event 2', ...]
        """

        return self._events

    @property
    def walk_events(self) -> Generator[str]:
        """
        :return: Generator of event names
        :exe: 'Event 1', 'Event 2', ...
        """

        yield from (event for event in self.events if event not in self.trial_events)

    @property
    def trial_events(self) -> list[str]:
        """
        :return: List of trial event names
        :exe: ['Event 1', 'Event 2', ...]
        """

        return self._trial_events

    @property
    def full_scores(self) -> dict[int, list[int]]:
        """
        :return: Dictionary of team numbers and full array of scores
        :exe: {1: [1, 2, 3], 2: [1, 2, 3], ...}
        """
        return self._full_scores

    @property
    def score_sum(self) -> dict[int, int]:
        """
        :return: Dictionary of team numbers and total score
        :exe: {1: 100, 2: 200, ...}
        """

        return self._score_sum

    @property
    def averages(self) -> dict[int, float]:
        """
        :return: Dictionary of team numbers and average score
        :exe: {1: 100.0, 2: 200.0, ...}
        """

        return self._averages

    @property
    def raw_placements(self) -> list[dict[str, str | int]]:
        return self._raw_placements

    @property
    def team_names(self) -> set[str]:
        return self._team_names

    @property
    def tournament(self) -> dict[str, str]:
        return self._data["Tournament"]

    def visualize(self) -> None:
        """
        :return: None
        To be overridden by subclasses
        """
        pass
