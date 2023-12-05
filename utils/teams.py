from __future__ import annotations

from typing import overload, Any, TypeVar

T = TypeVar('T')
S = TypeVar('S')


@overload
def number_to_name(team_dict: dict[int, str], team_numbers: list[int]) -> list[str]:
    ...


@overload
def number_to_name(team_dict: dict[int, str], team_numbers: int) -> str:
    ...


def number_to_name(team_dict: dict[int, str], team_numbers: list[int] | int) -> list[str] | str:
    if isinstance(team_numbers, list):
        return [team_dict[t] for t in team_numbers]
    else:
        return team_dict[team_numbers]


def pretty_print(translation_dict: dict[Any, T], convert: dict[Any, S]) -> dict[T, S]:
    return {translation_dict[t]: s for t, s in convert.items()}

