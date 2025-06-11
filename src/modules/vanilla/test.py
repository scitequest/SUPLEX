from modules.SuplexModuleInterface import SuplexModuleInterface
import ipywidgets as widgets


class Main_Test(SuplexModuleInterface):
    MODULE_NAME = "Test"
    MODULE_DESCRIPTION = "A module used for testing."

    def __init__(self):
        self._datasets = None
        self._hoverText = Main_Test.MODULE_DESCRIPTION
        self._ui = widgets.VBox()

    def getModuleInfo(self):
        return Main_Test.MODULE_NAME

    def checkIfViable(self, datasets):
        if True:
            self._hoverText = Main_Test.MODULE_DESCRIPTION
            return True
        self._hoverText = "Module not viable"
        return False

    def getModuleHoverText(self):
        return self._hoverText

    def getUI(self, datasets):
        button = widgets.Button(
            description="Show Selected Datasets",
            button_style="",
            layout=widgets.Layout(width="auto", margin="5px"),
        )

        button.on_click(lambda b: self.processData())

        self._ui.children = [button]

        return self._ui

    def processData(self, datasets, options):
        multi_row_text = []
        text = ""
        for dataset in datasets:
            text += dataset.getNameLabel() + "<br>"
        textbox = widgets.HTML(
            value=text,
            layout={
                "height": "200px",
                "overflow_y": "auto",
                "border": "1px solid black",
            },
        )

        self._ui.children = self._ui.children + (textbox,)
