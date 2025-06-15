from modules.SuplexModuleInterface import SuplexModuleInterface
from modules.submodules import AttributeSelector
from modules.submodules import File_Directory_Dialog as fdc

import ipywidgets as widgets
import math
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display
import tkinter as tk
from tkinter import filedialog
import os


# Generates a scatterplot overlaid by a boxplot for each dataset.
# This is used to get a view of the intensity profile of a given Dataset.
# It also allows the user to experiment with static thresholds via widget input.
class Intensity_Overview:
    MODULE_NAME = "Intensity Overview"
    MODULE_GROUP = "Analysis"

    def __init__(self):
        self._datasets = []
        self._plotDisplay = widgets.Output()
        self._figure = None

        self._minorIssues = []
        self._majorIssue = ""

        self._options = [
            [
                "mean",
                "min",
                "max",
                "std_deviation",
                "normalized_mean",
                "mean_minus_min",
            ],
            [
                "adjusted_average",
                "adjusted_average_std_deviation",
                "relative_adjusted_average_std_deviation",
                "normalized_average",
                "normalized_average_std_deviation",
                "relative_normalized_average_std_deviation",
            ],
        ]
        self._valueSets = []

        self._dataCheckboxes = []
        for option in self._options[0]:
            checkbox = widgets.Checkbox(
                value=False, description=option, layout={"width": "max-content"}
            )
            self._dataCheckboxes.append(checkbox)
            checkbox.observe(lambda b, checkbox=checkbox: self.optionSelected(checkbox))

        self._dataStatisticsCheckboxes = []
        for option in self._options[1]:
            checkbox = widgets.Checkbox(
                value=False, description=option, layout={"width": "max-content"}
            )
            self._dataStatisticsCheckboxes.append(checkbox)
            checkbox.observe(lambda b, checkbox=checkbox: self.optionSelected(checkbox))

        self._checkboxObserveFlag = True
        self._thresholdSlider = widgets.FloatRangeSlider(
            value=[0, 100],
            min=0,
            max=100,
            step=1,
            description="Threshold:",
            disabled=False,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format=".1f",
            layout=widgets.Layout(width="600px"),
        )

        self._createGraphButton = widgets.Button(
            description="Generate Graph", button_style="success"
        )
        self._createGraphButton.on_click(lambda b: self.processData())

        self._downloadButton = widgets.Button(
            description="Save Graph", button_style="success"
        )
        self._downloadButton.disabled = True
        self._downloadButton.on_click(lambda b: self.downloadGraph())

    def getUI(self):
        # Sets a standard value and calls for the initialization of the threshold slider
        self._dataCheckboxes[0].value = True

        title = widgets.HTML("<b style='font-size:20px;'>Intensity Overview</b>")
        description = widgets.HTML(
            "<b style='font-size:10px;'>Here be long form description</b>"
        )

        dataDescription = widgets.HTML("<b style='font-size:15px;'>Data</b>")
        dataCheckboxes = widgets.VBox([dataDescription] + self._dataCheckboxes)

        dataStatisticsDescription = widgets.HTML(
            "<b style='font-size:15px;'>Data Statistics</b>"
        )
        dataStatisticsCheckboxes = widgets.VBox(
            [dataStatisticsDescription] + self._dataStatisticsCheckboxes
        )

        checkboxesBox = widgets.HBox([dataCheckboxes, dataStatisticsCheckboxes])

        ui = widgets.VBox(
            [
                title,
                description,
                checkboxesBox,
                self._thresholdSlider,
                self._createGraphButton,
                self._plotDisplay,
                self._downloadButton,
            ]
        )

        return [ui]

    def processData(self):
        minVal = self._thresholdSlider.value[0]
        maxVal = self._thresholdSlider.value[1]
        valSets = self._valueSets

        # If no value restriction was set just use all values.
        if not (
            minVal == self._thresholdSlider.min and maxVal == self._thresholdSlider.max
        ):
            for vSet in self._valueSets:
                vSet["values"] = [
                    value for value in vSet["values"] if minVal <= value <= maxVal
                ]
            valSets = [vSet for vSet in valSets if vSet["values"]]

        self.generatePlot(valSets)
        self._downloadButton.disabled = False

    def generatePlot(self, valSets):
        absMinVal = self._thresholdSlider.min
        absMaxVal = self._thresholdSlider.max
        minVal = self._thresholdSlider.value[0]
        maxVal = self._thresholdSlider.value[1]

        setLabels = [valSet["name"] for valSet in valSets]
        vSets = [valSet["values"] for valSet in valSets]

        fig, ax = plt.subplots()
        if absMinVal != minVal and absMaxVal != maxVal:
            plt.axvline(x=minVal, linewidth=2, color="r")
            plt.axvline(x=maxVal, linewidth=2, color="r")
        ax = sns.boxplot(data=vSets, orient="h", ax=ax)
        ax = sns.stripplot(data=vSets, orient="h", s=3, linewidth=1, ax=ax)
        ax.set_yticklabels(setLabels)

        if absMinVal > 0:
            absMinVal = 0
        ax.set_xlim(absMinVal, absMaxVal)

        self._plotDisplay.clear_output(wait=True)
        with self._plotDisplay:
            display(fig)

        self._figure = fig

    def downloadGraph(self):
        root = tk.Tk()
        root.withdraw()
        folderSelected = filedialog.askdirectory()
        if not folderSelected:
            return

        dpi = 10
        self._figure.savefig(folderSelected + "/image.png", dpi=dpi)

    def optionSelected(self, checkbox):
        # Prevents an infinite loop
        if not self._checkboxObserveFlag:
            return

        # Checkbox was deselected, logically no checkbox is selected anymore
        if not checkbox.value:
            self._createGraphButton.disabled = True
            self._thresholdSlider.disabled = True
            return

        self._checkboxObserveFlag = False

        # Mimics the behaviour of radio buttons for multiple sets of checkboxes.
        # Additionally allows to select no checkbox.
        for dataCheckbox in self._dataCheckboxes:
            dataCheckbox.value = False

        for dataStatisticsCheckbox in self._dataStatisticsCheckboxes:
            dataStatisticsCheckbox.value = False

        checkbox.value = True
        self.setupValueSets(checkbox.description)

        self._checkboxObserveFlag = True
        self._createGraphButton.disabled = False

    def setupValueSets(self, attribute):

        self._valueSets = []

        minVal = None
        maxVal = None

        for dataset in self._datasets:
            values = []

            if attribute in self._options[0]:
                # Flatten spot list, since it's two dimensional.
                valueCollection = [
                    item for sublist in dataset.spots for item in sublist
                ]
            else:
                valueCollection = dataset.dataStatistics

            for valueSet in valueCollection:
                val = self.valueDemux(valueSet, attribute)
                values.append(val)
                if minVal is None or maxVal is None:
                    minVal = val
                    maxVal = val
                if val < minVal:
                    minVal = val
                if val > maxVal:
                    maxVal = val

            self._valueSets.append({"name": dataset.getNameLabel(), "values": values})

        # Calculates the order of magnitude between the max/min delta
        stepsize = math.floor(math.log10(abs(maxVal - minVal))) - 2
        stepsizeFormat = "0"
        if stepsize < 0:
            stepsizeFormat = str(-1 * stepsize)
        stepsize = 10**stepsize

        self._thresholdSlider.disabled = False
        self._thresholdSlider.min = minVal
        self._thresholdSlider.max = maxVal
        self._thresholdSlider.step = stepsize
        self._thresholdSlider.readout_format = "." + stepsizeFormat + "f"
        self._thresholdSlider.value = [minVal, maxVal]

    # Basically a switch-case for all possible radio-button selections
    def valueDemux(self, valueSet, attribute):
        # data
        if attribute == "mean":
            return valueSet.datapoint.mean_val
        if attribute == "min":
            return valueSet.datapoint.min_val
        if attribute == "max":
            return valueSet.datapoint.max_val
        if attribute == "std_deviation":
            return valueSet.datapoint.std_deviation
        if attribute == "normalized_mean":
            return valueSet.datapoint.normalized_mean
        if attribute == "mean_minus_min":
            return valueSet.datapoint.mean_minus_min
        # data statistics
        if attribute == "adjusted_average":
            return valueSet.adjusted_average
        if attribute == "adjusted_average_std_deviation":
            return valueSet.adjusted_average_std_deviation
        if attribute == "relative_adjusted_average_std_deviation":
            return valueSet.relative_adjusted_average_std_deviation
        if attribute == "normalized_average":
            return valueSet.normalized_average
        if attribute == "normalized_average_std_deviation":
            return valueSet.normalized_average_std_deviation
        if attribute == "relative_normalized_average_std_deviation":
            return valueSet.relative_normalized_average_std_deviation

    def getModuleName(self):
        return Intensity_Overview.MODULE_NAME

    def getModuleGroupName(self):
        return Intensity_Overview.MODULE_GROUP

    def moduleIsViable(self):
        return False

    def loadAndCheckDatasets(self, datasets):
        for dataset in datasets:
            if dataset.nSpots > 0:
                self._datasets.append(dataset)
            else:
                issueText = (
                    "Couldn't load "
                    + dataset.metadata.patName
                    + " - "
                    + dataset.metadata.patId
                    + ". Dataset without any datapoints."
                )
                self._minorIssues.append(issueText)

    def resetModule(self):
        return type(self)()
