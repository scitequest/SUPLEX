import ipywidgets as widgets


class ModulePage:
    def __init__(self, modules, moduleView):
        self._modules = modules
        self._pageName = modules[0].getModuleGroupName()
        self._moduleView = moduleView
        self._moduleButtons = []
        self.initializeModuleButtons()

    def initializeModuleButtons(self):
        for module in self._modules:
            self._moduleButtons.append(
                widgets.Button(description=module.getModuleName(), button_style="")
            )
            self._moduleButtons[-1].on_click(lambda b: self.activateModule(module))

    def activateModule(self, module):
        self._moduleView.children = module.getUserInterface()

    def getModuleButtons(self):
        return widgets.VBox(self._moduleButtons)

    @property
    def modules(self):
        return self._modules

    @property
    def pageName(self):
        return self._pageName

    @property
    def moduleButtons(self):
        return self._moduleButtons
