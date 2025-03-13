from .Parameters import Parameters
from .DataStatisticsSpot import DataStatisticsSpot
from .Spot import Spot
from .Metadata import Metadata
from datetime import datetime

class Dataset:
    def __init__(self, measureData, dataStatistics, metadata, parameters, imagePath, annotatedImagePath, project):
        
        # measureData cannot be None, but everything else can.
        self._spots = self.initSpots(measureData, parameters)
        self._dataStatistics = None
        self._backgroundRectangles = None
        self._metadata = None
        self._invertLut = None
        self._subtractBackground = None
        self._nSpotfields = None
        self._nCols = None
        self._nSpots = None
        self._nRows = None
        
        if dataStatistics is not None:
            self._dataStatistics = self.initDataStatistics(dataStatistics)            
        
        # TODO: metadata can never be none, change this later.
        if metadata is not None:
            self._metadata = Metadata(metadata)
        
        self._project = project
        
        # Split-off general parameters from spot-specific parameters
        if parameters is not None:
            self._backgroundRectangles = self.initBackgroundRectangles(parameters["background_rectangles"])
            self._invertLut = bool(parameters["invert_lut"])
            self._subtractBackground = bool(parameters["subract_background"])
            self._nSpotfields = int(parameters["number_of_spotfields"])
            self._nCols = int(parameters["columns_per_spotfield"])
            self._nSpots = int(parameters["spots_per_spotfield"])
            self._nRows = int(self._nSpots / self._nCols)
        else:
            self.setGridDimensions()
            
        self._imagePath = imagePath
        self._annotatedImagePath = annotatedImagePath
    
    def initSpots(self, measureData, parameters):
        if parameters is not None:
            params = parameters["spots"]
        else:
            params = [None] * len(measureData)
            
        nSpotfields = int(measureData[-1]["spot"]) + 1
        ret = [[] for _ in range(nSpotfields)]
        
        for i, mDatapoint in enumerate(measureData):
            ret[int(mDatapoint["spot"])].append(Spot(mDatapoint, params[i]))
            
        return ret
            
    def initDataStatistics(self, dataStatistics):
        return [DataStatisticsSpot(dStat) for dStat in dataStatistics]
    
    def initBackgroundRectangles(self, bRectParams):
        return [Parameters(bRect) for bRect in bRectParams]
    
    # This method is only called if there is no parameters file.
    # In this case the dimensions and number of Spot Fields is extracted from the measurements.
    def setGridDimensions(self):
        self._nSpotfields = self._spots[-1].datapoint.spot + 1
        self._nCols = self._spots[-1].datapoint.col + 1
        self._nRows = self._spots[-1].datapoint.row + 1
        self._nSpots = self._nSpotfields * self._nCols * self._nRows
    
    def getCreationDate(self):
        return self._metadata.getCreationDate()
    
    def getNameLabel(self):
        return str(self._metadata.patId + " - " + self._metadata.patName)
    
    def getCreationLabel(self):
        dt = datetime.fromisoformat(self._metadata.imageCreated)
        return str(dt.date()) + ": " + self._metadata.patId + " - " + self._metadata.patName
    
    def getMeasureDateLabel(self):
        dt = datetime.fromisoformat(self._metadata.datetime)
        return str(dt.date()) + ": " + self._metadata.patId + " - " + self._metadata.patName
    
    def getTags(self):
        return self._metadata.tags
    
    def hasSomeTags(self, compTags):
        return any(tag in self._metadata.tags for tag in compTags)
    
    def hasAllTags(self, compTags):
        if not compTags:
            return False
        return set(compTags).issubset(set(self._metadata.tags))
    
    def isInTimeframe(self, startDate, endDate):
        cDate = self._metadata.getCreationDate()
        return startDate <= cDate <= endDate

    @property
    def spots(self):
        return self._spots

    @property
    def dataStatistics(self):
        return self._dataStatistics

    @property
    def backgroundRectangles(self):
        return self._backgroundRectangles

    @property
    def metadata(self):
        return self._metadata

    @property
    def invertLut(self):
        return self._invertLut

    @property
    def subtractBackground(self):
        return self._subtractBackground

    @property
    def nSpotfields(self):
        return self._nSpotfields

    @property
    def nCols(self):
        return self._nCols

    @property
    def nSpots(self):
        return self._nSpots

    @property
    def nRows(self):
        return self._nRows

    @property
    def imagePath(self):
        return self._imagePath

    @property
    def annotatedImagePath(self):
        return self._annotatedImagePath

    @property
    def project(self):
        return self._project