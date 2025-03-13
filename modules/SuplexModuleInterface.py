from abc import ABC, abstractmethod

# This is an abstract base class (abc) which has to be implemented in all suplex-modules.
# It is used for both the detection and validation of said modules.
class SuplexModuleInterface(ABC):
    
    # Returns Module Name
    @abstractmethod
    def getModuleName(self):
        pass
    
    # Returns Module Group Name. This is later used to order all modules.
    @abstractmethod
    def getModuleGroupName(self):
        pass
    
    # Checks if the module can be used and stores datasets if valid.
    @abstractmethod
    def loadAndCheckDatasets(self, datasets):
        pass
    
    # Returns an interface for the user to select options for data processing.
    # Can in some cases be empty.
    @abstractmethod
    def getUI(self):
        pass
    
    # Returns the processed data.
    @abstractmethod
    def processData(self):
        pass

    # Returns the processed data.
    @abstractmethod
    def moduleIsViable(self):
        pass

    # Returns the module to its initial state
    def resetModule(self):
        pass