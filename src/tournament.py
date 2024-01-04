from __future__ import annotations

import datetime

import yaml

from src.drops import Drops
from src.iqr import Iqr
from src.mean import Mean
from src.stddeviation import StdDeviation
from src.superscore import SuperScoreModel

TESTING = False


class Tournament:
    def __init__(
            self,
            path: str,
            models_to_use: list[
                tuple[float, type[Iqr | StdDeviation | Mean | SuperScoreModel]]
            ],
    ):
        self._ranks: tuple[str] | None = None
        self._path = path
        self._data = {}
        self._models: dict[float, Iqr | StdDeviation | Mean | SuperScoreModel] = {}
        self._competitiveness: float = (
            0  # [0, 1] 0 being least competitive, 1 being most competitive
        )
        self._recentness: float = 0  # [0, 1] 0 being least recent, 1 being most recent
        self._raw_models = models_to_use
        self._prelim: dict[str, float] = {}
        if sum([k for k, _ in self._raw_models]) != 1:
            raise ValueError("Sum of weights must equal 1")
        self.setup()

    def setup(self):
        with open(self._path, "r") as f:
            self._data = yaml.safe_load(f)

        for weight, model in self._raw_models:
            self.__self(model, weight)

        d = self._data["Tournament"].get(
            "date", self._data["Tournament"].get("start date")
        )
        date: datetime.datetime = d
        year, month, day = date.year, date.month, date.day
        season_start = datetime.date(
            year=(year - 1 if month < 5 else year), month=8, day=1
        )
        season_end = datetime.date(
            year=(year if month < 5 else year + 1), month=5, day=1
        )
        self._recentness = (date - season_start) / (season_end - season_start)
        self.set_comp()

    def __self(
            self, model: type[Iqr | StdDeviation | Mean | SuperScoreModel], weight: float
    ) -> None:
        _model = model(self._path, weight)
        self._models[_model.weight] = _model

    def set_comp(self) -> float:
        """
        Sets the competitiveness of the tournament
        :return: float, [0, 1] 0 being least competitive, 1 being most competitive
        measured by the number of teams that competed at nationals at the tournament/total number of teams
        """
        with open("../data/2023-05-20_nationals_c.yaml", "r") as f:
            h = yaml.safe_load(f)
        national_tlist = [t["school"] for t in h["Teams"]]
        comped_tlist = [t["school"] for t in self._data["Teams"]]
        self._competitiveness = len(
            set(comped_tlist).intersection(set(national_tlist))
        ) / len(
            comped_tlist
        )  # [0, 1]
        return self._competitiveness

    def aggregate(self) -> tuple[str]:
        _prelim: dict[str, float] = {}
        for j, (rel_model_weight, model) in enumerate(self._models.items()):
            assert isinstance(model, (Drops, SuperScoreModel))
            if j == 0:  # populate dictionary
                if isinstance(model, Drops):
                    _prelim = {team: 0 for team in model.ret_scores}
                else:
                    _prelim = {team: 0 for team in model.super_scores}

            if isinstance(model, Drops):
                rankings = [team for team in model.ret_scores]
                for i, team in enumerate(rankings):
                    _prelim[team] += (i + 1) * rel_model_weight
            else:
                rankings = [team for team in model.super_scores]
                for i, team in enumerate(rankings):
                    _prelim[team] += (i + 1) * rel_model_weight
        self._prelim = _prelim
        self._ranks = tuple(
            [t for t in dict(sorted(_prelim.items(), key=lambda x: x[1]))]
        )
        return self._ranks

    @property
    def model_list(self) -> list[Iqr | StdDeviation | Mean | SuperScoreModel]:
        return list(self._models.values())

    @property
    def prelim(self) -> dict[str, float]:
        return self._prelim

    @property
    def models(self) -> dict[float, Iqr | StdDeviation | Mean | SuperScoreModel]:
        """
        :return: dict of models {weight: model, ...}
        """
        return self._models

    @property
    def ranks(self) -> tuple[str] | None:
        """
        :return: list of team names in order of rank
        """
        return self._ranks

    @property
    def tourney_weight(self) -> float:
        return self._competitiveness * self._recentness


if __name__ == '__main__':
    TESTING = False
    if TESTING:
        t = Tournament(
            "../data/2023-01-21_mit_invitational_c.yaml",
            [(0.1, Iqr), (0.6, StdDeviation), (0.1, Mean), (0.2, SuperScoreModel)],
        )

        print(t.aggregate())
        print(t.prelim)
        print(t._competitiveness, t._recentness)
        print(t.tourney_weight)
