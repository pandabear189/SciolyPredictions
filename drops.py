from __future__ import annotations

import typing

import yaml
import numpy as np


def main(file_path: str, call: typing.Literal['std_deviation', 'iqr', 'mean'] = 'std_deviation', alpha: float = 1.5):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    # Team List in order index of team number - 1 (0-indexed)
    teams = [team['school'] for team in data.get('Teams')]

    # Event Order (0-indexed)
    events = [event['name'] for event in data.get('Events')]

    # %%
    trial_events = [d['name'] for d in data.get('Events') if d.get('trial', False)]
    total_scores: dict[str, int] = {t: 0 for t in teams}  # team number : total score (sum)
    full_scores: dict[str, list[int]] = {t: [] for t in teams}  # full array of scores for each team

    for placement in data.get('Placings'):
        total_scores[teams[placement['team'] - 1]] += placement.get('place', len(teams)) if not placement[
                                                                                                    'event'] in trial_events else 0
        full_scores[teams[placement['team'] - 1]].append(placement.get('place', len(teams))) if not placement[
                                                                                                        'event'] in trial_events else 0

    # print(total_scores)
    # print(full_scores)

    averages = {t: total_scores[t] / (len(data.get('Events')) - len(trial_events)) for t in teams}
    # print(averages)

    bombed_events = {t: [] for t in teams}
    def mean(alpha: float = 2):
        for placement in data.get('Placings'):
            if placement.get('place', len(teams)) > averages[teams[placement['team'] - 1]] * alpha and not placement[
                                                                                                               'event'] in trial_events:
                bombed_events[teams[placement['team'] - 1]].append(placement['event'])

        print("\"Bombed\" events by school:", bombed_events, "\n")
        print("Average \"bombed events\": ", sum([len(bombed_events[t]) for t in bombed_events]) / len(teams))

    def iqr(alpha: float = 1.5):
        for placement in data.get('Placings'):
            q1 = np.quantile(full_scores[teams[placement['team'] - 1]], 0.25)
            q3 = np.quantile(full_scores[teams[placement['team'] - 1]], 0.75)
            if placement.get('place', len(teams)) > ((q3 - q1) * alpha + q3) and not placement['event'] in trial_events:
                bombed_events[teams[placement['team'] - 1]].append(placement['event'])

        print("\"Bombed\" events by school:", bombed_events, "\n")
        print("Average \"bombed events\": ", sum([len(bombed_events[t]) for t in bombed_events]) / len(teams))

    def std_deviation(alpha: float = 1.5):
        for placement in data.get('Placings'):
            mean = np.mean(full_scores[teams[placement['team'] - 1]])
            std = np.std(full_scores[teams[placement['team'] - 1]])
            if placement.get('place', len(teams)) > (mean + alpha * std) and not placement['event'] in trial_events:
                bombed_events[teams[placement['team'] - 1]].append(placement['event'])

        print("\"Bombed\" events by school:", bombed_events, "\n")
        print("Average \"bombed events\": ", sum([len(bombed_events[t]) for t in bombed_events]) / len(teams))

    """
    :return: dict of scores after dropping events
    """
    if call == 'std_deviation':
        method = std_deviation
    elif call == 'iqr':
        method = iqr
    else:
        method = mean

    # run method
    method(alpha)

    score_copy = full_scores.copy()
    drops = round(sum([len(bombed_events[t]) for t in bombed_events]) / len(teams))

    for _ in range(drops):
        for team in score_copy:
            score_copy[team].remove(max(score_copy[team]))

    score_with_drops = {t: sum(score_copy[t]) for t in score_copy}

    print(dict(sorted(score_with_drops.items(), key=lambda item: item[1])))
    return score_copy




