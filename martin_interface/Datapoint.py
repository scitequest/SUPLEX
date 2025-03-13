class Datapoint:
    def __init__(self, datapoint):
        self._mean_minus_min = float(datapoint["mean_minus_min"])
        self._normalized_mean = float(datapoint["normalized_mean"])
        self._spot = int(datapoint["spot"])
        self._row = int(datapoint["row"])
        self._col = int(datapoint["col"])
        self._min_val = float(datapoint["min"])
        self._max_val = float(datapoint["max"])
        self._mean_val = float(datapoint["mean"])
        self._std_deviation = float(datapoint["std_deviation"])
        
    @property
    def mean_minus_min(self):
        return self._mean_minus_min

    @property
    def normalized_mean(self):
        return self._normalized_mean

    @property
    def spot(self):
        return self._spot

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    @property
    def min_val(self):
        return self._min_val

    @property
    def max_val(self):
        return self._max_val

    @property
    def mean_val(self):
        return self._mean_val

    @property
    def std_deviation(self):
        return self._std_deviation