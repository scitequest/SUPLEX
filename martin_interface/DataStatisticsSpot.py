class DataStatisticsSpot:
    def __init__(self, spotStats):
        self._row = int(spotStats["row"])
        self._col = int(spotStats["col"])
        self._adjusted_average = float(spotStats["adjusted_average"])
        self._adjusted_average_std_deviation = float(spotStats["adjusted_average_std_deviation"])
        self._relative_adjusted_average_std_deviation = float(spotStats["relative_adjusted_average_std_deviation"])
        self._normalized_average = float(spotStats["normalized_average"])
        self._normalized_average_std_deviation = float(spotStats["normalized_average_std_deviation"])
        self._relative_normalized_average_std_deviation = float(spotStats["relative_normalized_average_std_deviation"])
        
    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    @property
    def adjusted_average(self):
        return self._adjusted_average

    @property
    def adjusted_average_std_deviation(self):
        return self._adjusted_average_std_deviation

    @property
    def relative_adjusted_average_std_deviation(self):
        return self._relative_adjusted_average_std_deviation

    @property
    def normalized_average(self):
        return self._normalized_average

    @property
    def normalized_average_std_deviation(self):
        return self._normalized_average_std_deviation

    @property
    def relative_normalized_average_std_deviation(self):
        return self._relative_normalized_average_std_deviation