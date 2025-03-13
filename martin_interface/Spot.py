from .Datapoint import Datapoint
from .Parameters import Parameters

class Spot:
    def __init__(self, datapoint, spotParameters):
        self._datapoint = Datapoint(datapoint)
        self._spotParameters = Parameters(spotParameters)
    
    @property
    def datapoint(self):
        return self._datapoint
    
    @property
    def spotParameters(self):
        return self._spotParameters