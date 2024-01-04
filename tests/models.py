from src import *

test_files = [
    "../data/2023-02-18_penn_invitational_c.yaml",
    # "../data/2023-01-21_mit_invitational_c.yaml",
]


def stdev():
    for f in test_files:
        model = StdDeviation(f)
        model.drop()
        assert model._dropped is True  # will raise AssertionError if not true
        # model.visualize()

        print("alpha (should be default 2 ", model.alpha)
        print("amt dropped", model.to_drop)
        for i, team in enumerate(dict(sorted(model.ret_scores.items(), key=lambda x: x[1]))):
            print(i + 1, team, model.ret_scores[team])


if __name__ == '__main__':
    stdev()
