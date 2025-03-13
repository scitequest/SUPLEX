class Project:
    def __init__(self, projectName, projectDescription):
        self._projectName = projectName
        self._projectDescription = projectDescription
        self._datasets = []
        self._tags = []
        
    def addDataset(self, dataset):
        self._datasets.append(dataset)
        
    def getMeasurementLabels(self):
        ret = []
        for dataset in self._datasets:
            ret.append(dataset.getLabel())
            
        return ret
    
    def extractTags(self):
        for dataset in self._datasets:
            tags = dataset.getTags()
            for tag in tags:
                if tag not in self._tags:
                    self._tags += tag
        
    @property
    def projectName(self):
        return self._projectName
    
    @property
    def projectDescription(self):
        return self._projectDescription
    
    @property
    def datasets(self):
        return self._datasets
    
    @property
    def tags(self):
        return self._tags