from utils.results import Results


class Predictions:
    def __init__(self, models: list[Results], data):
        self.models: list[Results] = models
        self.data = data
