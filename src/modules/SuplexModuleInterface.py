from abc import ABC, abstractmethod


# This is an abstract base class (abc) which has to be implemented in all suplex-modules.
# It is used for both the detection and validation of said modules.
class SuplexModuleInterface(ABC):

    # Returns information such as module name and button-style.
    @abstractmethod
    def getModuleInfo(self):
        pass

    # Checks if the module is viable on the selected datasets.
    @abstractmethod
    def checkIfViable(self, datasets):
        pass

    # Returns description of module. May also be used to tell user why module is not viable for use.
    @abstractmethod
    def getModuleHoverText(self):
        pass

    # Returns an interface for the user to select options for data processing.
    @abstractmethod
    def getUI(self, datasets):
        pass

    # Processes datasets with a given set of options and returns them.
    @abstractmethod
    def processData(self, datasets, options):
        pass
