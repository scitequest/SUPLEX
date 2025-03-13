from modules.SuplexModuleInterface import SuplexModuleInterface
import ipywidgets as widgets

class Main_Test(SuplexModuleInterface):
    MODULE_NAME = "Test"
    MODULE_GROUP = "Test-Group"
    
    def __init__(self):
        self._datasets = None
        self._ui = widgets.VBox()
    
    def getModuleName(self):
        return Main_Test.MODULE_NAME
    
    def getModuleGroupName(self):
        return Main_Test.MODULE_GROUP
    
    def loadAndCheckDatasets(self, datasets):
        self._datasets = datasets
    
    def getUI(self):
        button = widgets.Button(
            description= "Show Selected Datasets",
            button_style='',
            layout=widgets.Layout(width='auto', margin='5px')
        )
        
        button.on_click(lambda b: self.processData())

        self._ui.children = [button]
        
        return self._ui
    
    def processData(self):
        multi_row_text = [  ]
        text = ""
        for dataset in self._datasets:
            text += dataset.getNameLabel() + "<br>"
        textbox = widgets.HTML(
            value=text,
            layout={'height': '200px', 'overflow_y': 'auto', 'border': '1px solid black'}
        )

        self._ui.children = self._ui.children + (textbox,)

    def moduleIsViable(self):
        return bool(self._datasets)

    def resetModule(self):
        return type(self)()