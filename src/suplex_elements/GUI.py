from martin_interface.martin_adapter import Adapter
from modules import ModuleLoader
from suplex_elements.ProjectCard import ProjectCard

import modules.submodules.File_Directory_Dialog as fdd
import sys
import os
import inspect
import importlib
import pkgutil
import ipywidgets as widgets
from tkinter import Tk, filedialog
from datetime import datetime, date
from IPython.display import display, clear_output
import numpy as np


class GUI:
    def __init__(self, modules, content, logView):
        self.modules = modules
        self.content = content
        self.data = None

        self.dirPath = ""

        # Elements not affected by reset
        self.header = self.getHeader()
        self.infoField = widgets.Box(
            [
                widgets.HTML(
                    value="<b>Info:</b> Welcome to SUPLEX! "
                    + str(len(modules))
                    + " Modules have been loaded."
                )
            ]
        )

        self.resetPage()

    def resetPage(self):
        self.projectAccordion = widgets.VBox()
        self.moduleSelector = widgets.VBox()
        self.activeModule = widgets.VBox()
        self.dirLoader = self.getDirLoader()

        self.content.children = [
            self.header,
            self.dirLoader,
            self.projectAccordion,
            self.moduleSelector,
            self.activeModule,
            self.infoField,
        ]

    def getHeader(self):
        return widgets.VBox()

    def getDirLoader(self):
        buttonDescription = "Open Directory"
        if self.dirPath:
            buttonDescription = "Change Directory"

        selectDirButton = widgets.Button(
            description=buttonDescription, button_style="info"
        )
        dirPathText = widgets.Text(
            value=self.dirPath,
            placeholder="...",
            description="Directory:",
            disabled=True,
        )
        selectDirButton.on_click(lambda b: self.loadDatasetsFromDir())

        return widgets.VBox([selectDirButton, dirPathText])

    def loadDatasetsFromDir(self):
        # Select directory
        self.dirPath = fdd.loadDirectoryDialog()
        if not self.dirPath:
            return

        # If successful reset application and load datasets
        self.resetPage()

        self.data = Adapter(self.dirPath)

        # Break if no data found
        if not self.data.datasets:
            self.infoField.children = [
                widgets.HTML(
                    value="<b>Info:</b> No datasets could be found in this directory."
                )
            ]
            return

        self.setupProjectAccordion()
        self.infoField.children = [
            widgets.HTML(
                value="<b>Info:</b> Loaded "
                + str(len(self.data.datasets))
                + " datasets from "
                + str(len(self.data.projects))
                + " projects."
            )
        ]

    def setupProjectAccordion(self):
        accordionTitle = widgets.HTML("<b style='font-size:30px;'>Projects</b>")
        accordion = widgets.Accordion()

        # Sets up project cards with their respective titles
        projectCards = [ProjectCard(project) for project in self.data.projects]
        accordion.children = [card.getCard() for card in projectCards]
        for i, card in enumerate(projectCards):
            accordion.set_title(i, card.getTitle())

        # Select Module
        selectDatasetsButton = widgets.Button(
            description="Suplex!",
            button_style="Success",
            layout=widgets.Layout(width="200px", height="60px"),
            style={"font_size": "20px"},
        )

        # Upon click collect all selected datasets into a singular list and open module selector.
        selectDatasetsButton.on_click(
            lambda b: self.datasetsSelected(
                [
                    dataset
                    for card in projectCards
                    for dataset in card.getSelectedDatasets()
                ]
            )
        )

        # Resets content of datasetCards
        self.projectAccordion.children = [
            accordionTitle,
            accordion,
            selectDatasetsButton,
        ]
        self.projectAccordion.layout.visible = True

    # Opens module selector and checks if modules may be used.
    def datasetsSelected(self, datasets):
        if not datasets:
            self.infoField.children = [
                widgets.HTML(value="<b>Info:</b> No datasets were selected.")
            ]
            return
        self.infoField.children = [
            widgets.HTML(
                value="<b>Info:</b> " + str(len(datasets)) + " datasets were selected."
            )
        ]

        # Do not reset selected datasets but make non-interactable.
        self.projectAccordion.layout.display = "none"
        self.getModuleSelector(datasets)

    def getModuleSelector(self, datasets):
        # Resets all modules
        self.modules = [module.resetModule() for module in self.modules]

        returnToSetSelectionButton = widgets.Button(
            description="Return",
            button_style="Danger",
            layout=widgets.Layout(width="500px", height="30px"),
            style={"font_size": "20px"},
        )
        returnToSetSelectionButton.on_click(lambda b: self.reselectDatasets())

        moduleButtons = []
        # Create buttons for each module
        for module in self.modules:
            module.loadAndCheckDatasets(datasets)
            moduleButton = widgets.Button(
                description=module.getModuleName(),
                button_style="",
                # style={'button_color': module.getModuleButtonColour()},
                layout=widgets.Layout(width="auto", margin="5px"),
                disabled=not module.moduleIsViable(),
            )

            # Trigger getUI when clicked
            moduleButton.on_click(lambda b, m=module: self.openModule(m))
            moduleButtons.append(moduleButton)

        moduleList = widgets.HBox(
            moduleButtons, layout=widgets.Layout(flex_flow="row wrap")
        )
        self.moduleSelector.children = [returnToSetSelectionButton, moduleList]

    def reselectDatasets(self):
        self.moduleSelector.children = []
        self.projectAccordion.layout.display = "block"

    def runModule(self, module, datasets):
        returnToModuleSelectionButton = widgets.Button(
            description="returnToModuleSelection",
            button_style="Danger",
            layout=widgets.Layout(width="200px", height="60px"),
            style={"font_size": "20px"},
        )
        returnToModuleSelectionButton.on_click(reselectModule)

        self.activeModule.children = [
            returnToModuleSelectionButton,
            module.getUI(datasets),
        ]

    def reselectModule(self, b):
        self.modules = [module.resetModule() for module in self.modules]
        self.moduleSelector.layout.display = "block"

    def openModule(self, module):
        self.moduleSelector.layout.display = "none"

        returnToModuleSelectionButton = widgets.Button(
            description="Return",
            button_style="Danger",
            layout=widgets.Layout(width="500px", height="30px"),
            style={"font_size": "20px"},
        )
        returnToModuleSelectionButton.on_click(lambda b: self.returnToModuleSelector())

        self.activeModule.children = [returnToModuleSelectionButton, module.getUI()]

    def returnToModuleSelector(self):
        self.moduleSelector.layout.display = "block"
        self.activeModule.children = []
