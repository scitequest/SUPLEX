from datetime import datetime
from dateutil import parser

class Metadata:
    def __init__(self, metadata):
        self._version = metadata["version"]
        self._datetime = metadata["datetime"]
        
        # Content of patient
        self._patId = metadata["patient"]["id"]
        self._patName = metadata["patient"]["name"]
        self._tags = metadata["patient"]["tags"]
        
        # Content of image
        self._imageCreated = metadata["image"]["created"]
        self._imager = metadata["image"]["imager"]
        self._binning = metadata["image"]["pixel_binning"]
        self._exposureTime = metadata["image"]["exposure_time"]
        
        self._incubations = self.getIncubations(metadata["incubations"])
    
    def getIncubations(self, incubations):
        ret = []
        for incub in incubations:
            stock = Concentration(incub["stock_concentration"]["value"], incub["stock_concentration"]["unit"])
            final = Concentration(incub["final_concentration"]["value"], incub["final_concentration"]["unit"])
            ret.append(Incubation(incub["solution"], stock, final, incub["incubation_time"]))
        return ret
    
    def getCreationDate(self):
        dt = datetime.fromisoformat(self._imageCreated)
        dt = datetime.fromisoformat(str(dt))
        return dt.date()
    
    def getMeasureDate(self):
        dt = parser.parse(self._datetime)
        dt = datetime.fromisoformat(str(dt))
        return dt.date()
    
    @property
    def version(self):
        return self._version

    @property
    def datetime(self):
        return self._datetime

    @property
    def patId(self):
        return self._patId

    @property
    def patName(self):
        return self._patName

    @property
    def tags(self):
        return self._tags

    @property
    def imageCreated(self):
        return self._imageCreated

    @property
    def imager(self):
        return self._imager

    @property
    def binning(self):
        return self._binning

    @property
    def exposureTime(self):
        return self._exposureTime

    @property
    def incubations(self):
        return self._incubations

class Incubation:
    def __init__(self, solution, stock_concentration, final_concentration, incubation_time):
        self._solution = solution
        self._stock_concentration = stock_concentration
        self._final_concentration = final_concentration
        self._incubation_time = incubation_time

    @property
    def solution(self):
        return self._solution

    @property
    def stock_concentration(self):
        return self._stock_concentration

    @property
    def final_concentration(self):
        return self._final_concentration

    @property
    def incubation_time(self):
        return self._incubation_time
    
class Concentration:
    def __init__(self, value, unit):
        self._value = value
        self._unit = unit
        
    @property
    def value(self):
        return self._value

    @property
    def unit(self):
        return self._unit