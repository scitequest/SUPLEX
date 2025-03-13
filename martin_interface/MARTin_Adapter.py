import json
import csv
import os
from .Dataset import Dataset
from .Project import Project

class Adapter:
    def __init__(self, path):
        self._datasets = []
        self._projects = []
        self.delveDirs(path)
        for proj in self._projects:
            proj.extractTags()
    
    def delveDirs(self, path, searchedFolders = None):
        readoutFiles = ["data.json", "data.tsv"]
        if searchedFolders is None:
            searchedFolders = set()

        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            if os.path.isdir(itempath):
                self.delveDirs(itempath, searchedFolders)
                
            elif item in readoutFiles:
                if path not in searchedFolders:
                    self.searchFolder(path)
                    searchedFolders.add(path)
    
    def searchFolder(self, folderpath):
        dataPath = None
        dataStatisticsPath = None
        metadataPath = None
        parametersPath = None
        imagePath = None
        annotatedImagePath = None
        
        
        for item in os.listdir(folderpath):
            if item == "data.json":
                dataPath = os.path.join(folderpath, item)
            elif item == "data.tsv" and dataPath is not None:
                dataPath = os.path.join(folderpath, item)
            elif item == "data_statistics.json":
                dataStatisticsPath = os.path.join(folderpath, item)
            elif item == "data_statistics.tsv" and dataStatisticsPath is not None:
                dataStatisticsPath = os.path.join(folderpath, item)
            elif item == "metadata.json":
                metadataPath = os.path.join(folderpath, item)
            elif item == "parameters.json":
                parametersPath = os.path.join(folderpath, item)
            elif os.path.splitext(item)[0] == "image":
                imagePath = os.path.join(folderpath, item)
            elif os.path.splitext(item)[0] == "annotated_image":
                annotatedImagePath = os.path.join(folderpath, item)
            
        self.addDataset(dataPath, dataStatisticsPath, metadataPath, parametersPath, imagePath, annotatedImagePath)
    
    def readJson(self, path):
        with open(path, 'r') as file:
            return json.load(file)

    def readTsv(self, path):
        with open(path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            return list(reader)

    def addDataset(self, dataPath, dataStatisticsPath, metadataPath, parametersPath, imagePath, annotatedImagePath):
        dataFile = None
        dataStatisticsFile = None
        metadataFile = None
        parametersFile = None
        
        projectName = "none" # The standard name for no project in MARTin is none.
        
        if dataPath.lower().endswith('.json'):
            dataFile = self.readJson(dataPath)
            dataFile = dataFile["values"]
        else:
            dataFile = self.readTsv(dataPath)

        
        if dataStatisticsPath.lower().endswith('.json'):
            dataStatisticsFile = self.readJson(dataStatisticsPath)
            dataStatisticsFile = dataStatisticsFile["values"]
        elif dataStatisticsPath.lower().endswith('.tsv'):
            dataStatisticsFile = self.readTsv(dataStatisticsPath)            
        
        if metadataPath is not None:
            metadataFile = self.readJson(metadataPath)
            if "project" in list(metadataFile.keys()):
                projectName = metadataFile["project"]["name"]
        
        if parametersPath is not None:
            parametersFile = self.readJson(parametersPath)
        
        # This adds datasets and new projects and establishes a bi-directional association between datasets and their projects.
        newProject = True
        for i, proj in enumerate (self._projects):
            if(proj.projectName == projectName):
                self._datasets.append(Dataset(dataFile, dataStatisticsFile, metadataFile, parametersFile, imagePath, annotatedImagePath, proj))
                proj.addDataset(self._datasets[-1])
                newProject = False
                break
            
        if(newProject):
            projectDescription = ""
            if projectName != "none":
                projectDescription = metadataFile["project"]["description"]
            self._projects.append(Project(projectName, projectDescription))
            self._datasets.append(Dataset(dataFile, dataStatisticsFile, metadataFile, parametersFile, imagePath, annotatedImagePath, self._projects[-1]))
            self._projects[-1].addDataset(self._datasets[-1])
    
    
    def getMeasurementsByProject(self):
        mList = []
        for proj in self.projects:
            dictionary = {
              "name": proj.projectName, 
              "measurementLabels": proj.getMeasurementLabels(),
              "measurementReference": proj.datasets, 
              "tags": proj.tags
            }
            mList.append(dictionary)
            
        return mList
    
    @property
    def datasets(self):
        return self._datasets
    
    @property
    def projects(self):
        return self._projects
        