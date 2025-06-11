# This is a submodule used to subselect attributes of a dataset.
class AttributeSelector:

    def __init__(self, datasets, mode=None):
        self._datasets = datasets
        self._dataAttributes = [
            "spot",
            "row",
            "col",
            "mean",
            "min",
            "max",
            "std_deviation",
            "normalized_mean",
            "mean_minus_min",
        ]
        self._dataCheckboxes = []

        self._dataStatisticsAttributes = [
            "row",
            "col",
            "adjusted_average",
            "adjusted_average_std_deviation",
            "relative_adjusted_average_std_deviation",
            "normalized_average",
            "normalized_average_std_deviation",
            "relative_normalized_average_std_deviation",
        ]
        self._dataStatisticsCheckboxes = []
        # br_diameter and br_shape are redundant values for vanilla MARTin
        self._parametersAttributes = [
            "invert_lut",
            "subract_background",
            "number_of_spotfields",
            "columns_per_spotfield",
            "spots_per_spotfield",
            "shape",
            "position",
            "diameter",
            "br_shape, br_position, br_diameter",
        ]
        self._parametersCheckboxes = []

        self._metadataAttributes[
            "version",
            "date_measured",
            "patId",
            "patName",
            "tags",
            "date_image_created",
            "imager",
            "pixel_binning",
            "exposure_time",
            "incubation_solution",
            "incubation_stock_concentration",
            "incubation_final_concentration",
            "incubation_time",
            "project_name",
            "project_description",
        ]
        self._metadataCheckboxes = []

        # Binary flag of availible attributes
        self._availibleAttributes = self.checkAvailibleAttributeGroups()
        self._enabledAttributes = self._availibleAttributes[:]  # copy not reference

        if mode:
            self.setAttributeCheckboxesMode(mode)

    # Checks which attribute groups are present in the datasets
    # data and metadata technically redundant, since both are required for loading a dataset.
    def checkAvailibleAttributeGroups(self):
        # [data, dataStatistics, parameters, metadata]
        flags = [False, False, False, False]

        for dataset in self._datasets:
            # Break loop if all flags are True
            if all(flags):
                return flags

            if dataset.spots:
                if dataset.spots[0].datapoint:
                    flags[0] = True
            if dataset.dataStatistics:
                flags[1] = True
            if dataset.spots:
                if dataset.spots[0].spotParameters:
                    flags[2] = True
            if dataset.metadata:
                flags[3] = True

        return flags

    def setEnabledAttributeGroups(self, attributeFlags):
        # Basically AND operator between Flags to be set and possibleFlags
        flags = [f1 and f2 for f1, f2 in zip(self._availibleAttributes, attributeFlags)]
        self._enabledAttributes = flags

    def getUiElements(self, hideGridIndices=False):
        checkboxBox = []
        gridIndices = ["spot", "row", "col"]

        if self._enabledAttributes[0]:
            for dAttr in self._dataAttributes:
                if hideGridIndices:
                    if dAttr in gridIndices:
                        continue
                checkbox = widgets.Checkbox(
                    value=True, description=dAttr, layout={"width": "max-content"}
                )
                self._dataCheckboxes.append(checkbox)
            if self._dataCheckboxes:
                dataTitle = widgets.HTML("<b style='font-size:15px;'>Data</b>")
                checkboxBox.append(widgets.VBox([dataTitle, self._dataCheckboxes]))

        if self._enabledAttributes[1]:
            for dStatAttr in self._dataStatisticsAttributes:
                if hideGridIndices:
                    if dStatAttr in gridIndices:
                        continue
                checkbox = widgets.Checkbox(
                    value=True, description=dStatAttr, layout={"width": "max-content"}
                )
                self._dataStatisticsCheckboxes.append(checkbox)
            if self._dataStatisticsCheckboxes:
                dataTitle = widgets.HTML(
                    "<b style='font-size:15px;'>Data Statistics</b>"
                )
                checkboxBox.append(
                    widgets.VBox([dataTitle, self._dataStatisticsCheckboxes])
                )

        if self._enabledAttributes[2]:
            for paramAttr in self._parametersAttributes:
                checkbox = widgets.Checkbox(
                    value=True, description=paramAttr, layout={"width": "max-content"}
                )
                self._parametersCheckboxes.append(checkbox)
            if self._parametersCheckboxes:
                dataTitle = widgets.HTML("<b style='font-size:15px;'>Parameters</b>")
                checkboxBox.append(
                    widgets.VBox([dataTitle, self._parametersCheckboxes])
                )

        if self._enabledAttributes[3]:
            for metaAttr in self._metadataAttributes:
                checkbox = widgets.Checkbox(
                    value=True, description=metaAttr, layout={"width": "max-content"}
                )
                self._metadataCheckboxes.append(checkbox)
            if self._metadataCheckboxes:
                dataTitle = widgets.HTML("<b style='font-size:15px;'>Metadata</b>")
                checkboxBox.append(widgets.VBox([dataTitle, self._metadataCheckboxes]))

        return widgets.HBox(checkboxBox)

    def setAttributeCheckboxesMode(self, mode):
        # Standard mode, boxes are initialized this way. This just removes any listeners.
        if mode == "ANY":
            boxes = (
                self._dataCheckboxes
                + self._dataStatisticsCheckboxes
                + self._parametersCheckboxes
                + self._metadataCheckboxes
            )
            for box in boxes:
                box.unobserve_all()

        if mode == "ONE":
            boxes = (
                self._dataCheckboxes
                + self._dataStatisticsCheckboxes
                + self._parametersCheckboxes
                + self._metadataCheckboxes
            )

            for box in boxes:
                box.value = False
                box.observe(
                    lambda b, checkbox=box, checkboxSet=boxes: self.optionSelected(
                        checkbox, checkboxSet
                    )
                )

        if mode == "ONE_PER_GROUP":
            boxSets = [
                self._dataCheckboxes,
                self._dataStatisticsCheckboxes,
                self._parametersCheckboxes,
                self._metadataCheckboxes,
            ]
            for boxes in boxSets:
                for box in boxes:
                    box.value = False
                    box.observe(
                        lambda b, checkbox=box, checkboxSet=boxes: self.optionSelected(
                            checkbox, checkboxSet
                        )
                    )

    def optionSelected(self, checkbox, checkboxSet):
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
        for box in checkboxSet:
            box.value = False

        checkbox.value = True
        self.setupValueSets(checkbox.description)

        self._checkboxObserveFlag = True
        self._createGraphButton.disabled = False
