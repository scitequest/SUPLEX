import ipywidgets as widgets

# This class is used for graphic representation of the project-measurement structure.
# It allows the subselection of specific datasets via date, tag and manual input.
class ProjectCard:
    def __init__(self, project):
        self._project = project
        
        # Left Column Elements
        self._datasetLabelSelection = self.generateDatasetLabelSelector()
        self._datasetCheckboxes = self.generateCheckboxes(self.getDatasetLabels())
        
        # Right Column Elements
        self._selectAllButton = widgets.Button(description="Select All", button_style="success")
        self._selectAllButton.on_click(lambda b: self.setAllDatasetCheckboxes(True))
        self._deselectAllButton = widgets.Button(description="Deselect All", button_style="danger")
        self._deselectAllButton.on_click(lambda b: self.setAllDatasetCheckboxes(False))
        
        self._startDatePicker = widgets.DatePicker(description='Start Date')
        self._endDatePicker = widgets.DatePicker(description='End Date')
        
        self.setupDateSelectors()
        self._startDatePicker.observe(lambda b: self.dateRangeChanged())
        self._endDatePicker.observe(lambda b: self.dateRangeChanged())

        self._tagCheckboxes = self.generateCheckboxes(self._project.tags)
        self._tagSelectionButton_AND = widgets.Button(description="Select If All Apply", button_style="success")
        self._tagSelectionButton_AND.on_click(lambda b: self.tagSelectDatasets(value = True, requireAll = True))
        self._tagSelectionButton_OR = widgets.Button(description="Select If Any Apply", button_style="success")
        self._tagSelectionButton_OR.on_click(lambda b: self.tagSelectDatasets(value = True, requireAll = False))
        self._tagDeselectionButton_AND = widgets.Button(description="Deselect If All Apply", button_style="danger")
        self._tagDeselectionButton_AND.on_click(lambda b: self.tagSelectDatasets(value = False, requireAll = True))
        self._tagDeselectionButton_OR = widgets.Button(description="Deselect If Any Apply", button_style="danger")
        self._tagDeselectionButton_OR.on_click(lambda b: self.tagSelectDatasets(value = False, requireAll = False))
        
    def generateCheckboxes(self, names):
        dCheckbox = []
        for name in names:
            dCheckbox.append(widgets.Checkbox(value=False, 
                                              description= name, 
                                              layout=widgets.Layout(width='auto', overflow='visible', white_space='normal')))
        return dCheckbox
    
    def getDatasetLabels(self):
        labels = []
        lsv = self._datasetLabelSelection.value
        
        for dataset in self._project.datasets:
            if lsv == "Date Image Taken":
                labels.append(dataset.getCreationLabel())
            elif lsv == "Date Image Measured":
                labels.append(dataset.getMeasureDateLabel())
            else:
                labels.append(dataset.getNameLabel())
        
        return labels
    
    def generateDatasetLabelSelector(self):
        noDateInfo = "Depict datasets without any date. This will disable the date-range selector."
        imageTakenInfo = "Depict datasets by the date the measured image was created."
        measuredInfo = "Depict datasets by the date the image was measured."
        
        tButtons = widgets.ToggleButtons(
            options=["Disable", "Date Image Taken", "Date Image Measured"],
            disabled=False,
            button_style='info', 
            tooltips=[noDateInfo, imageTakenInfo, measuredInfo],
            value="Disable")
        
        tButtons.observe(lambda b: self.changeDatasetLabelFormat())
        
        return tButtons
    
    def changeDatasetLabelFormat(self):
        dSetLabels = self.getDatasetLabels()
        
        for i, dSetLabel in enumerate(dSetLabels):
            self._datasetCheckboxes[i].enabled = True
            self._datasetCheckboxes[i].description = dSetLabel
        
        self.setupDateSelectors()
        
    def setAllDatasetCheckboxes(self, value):
        for checkbox in self._datasetCheckboxes:
            if not checkbox.disabled:
                checkbox.value = value
    
    def dateRangeChanged(self):
        value = self._datasetLabelSelection.value
        if value == "Disable":
            return
        for i, dataset in enumerate(self._project.datasets):
            if value == "Date Image Taken":
                date = dataset.metadata.getCreationDate()
            else:
                date = dataset.metadata.getMeasureDate()
            
            if self._startDatePicker.value <= date and date <= self._endDatePicker.value:
                self._datasetCheckboxes[i].disabled = False
            else:
                self._datasetCheckboxes[i].value = False
                self._datasetCheckboxes[i].disabled = True
        
    def setupDateSelectors(self):
        value = self._datasetLabelSelection.value
        
        if value == "Disable":
            self._startDatePicker.disabled  = True
            self._endDatePicker.disabled  = True
            self._startDatePicker.value = None
            self._endDatePicker.value = None
        else:
            self._startDatePicker.disabled  = False
            self._endDatePicker.disabled  = False
        
        earliestDate = None
        latestDate = None
        
        for dataset in self._project.datasets:
            if value == "Date Image Taken":
                cDate = dataset.metadata.getCreationDate()
            else:
                cDate = dataset.metadata.getMeasureDate()
            
            if(earliestDate is None or cDate < earliestDate):
                earliestDate = cDate
            
            if(latestDate is None or cDate > latestDate):
                latestDate = cDate
                
        self._startDatePicker.value = earliestDate
        self._endDatePicker.value = latestDate
  
        
    def tagSelectDatasets(self, value, requireAll):
        activeTags = []
        for tagCheckbox in self._tagCheckboxes:
            if tagCheckbox.value:
                activeTags.append(tagCheckbox.description)
        
        # Do nothing if there aren't any tags selected.
        if not activeTags:
            return
        
        for i, dataset in enumerate(self._project.datasets):
            if requireAll:
                applies = dataset.hasAllTags(activeTags)
            else:
                applies = dataset.hasSomeTags(activeTags)
            
            if applies:
                self._datasetCheckboxes[i].value = value

    def getCard(self):
        # Left Column Elements
        leftColTitle = widgets.HTML("<b style='font-size:20px;'>Datasets</b>")
        mCheckboxBox = widgets.VBox(self._datasetCheckboxes)
        leftCol = widgets.VBox([leftColTitle, mCheckboxBox])
        
        # Right Column Elements
        rightColTitle = widgets.HTML("<b style='font-size:20px;'>Filters</b>")
        rightColGeneralSubitle = widgets.HTML("<b style='font-size:10px;'>General</b>")
        toggleAllButtonBox = widgets.HBox([self._selectAllButton, self._deselectAllButton])
        rightColDateSubitle = widgets.HTML("<b style='font-size:10px;'>Date</b>")
        datePickerBox = widgets.HBox([self._startDatePicker, self._endDatePicker])
        
        rightColTagSubitle = widgets.HTML("<b style='font-size:10px;'>Tags</b>")
        tagSelectionButtonBox = widgets.GridBox(
            children=[self._tagSelectionButton_AND, self._tagSelectionButton_OR, 
                      self._tagDeselectionButton_AND, self._tagDeselectionButton_OR],
            layout=widgets.Layout(
                grid_template_columns="repeat(2, 150px)",
                grid_gap="5px"
            )
        )
        tagCheckboxesBox = widgets.GridBox(
            children= self._tagCheckboxes,
            layout=widgets.Layout(
                grid_template_columns="repeat(3, 150px)",
                grid_gap="5px"
            )
        )
        
        rightCol = widgets.VBox([rightColTitle, rightColGeneralSubitle, toggleAllButtonBox, rightColDateSubitle, datePickerBox, self._datasetLabelSelection, rightColTagSubitle, tagSelectionButtonBox, tagCheckboxesBox])
        
        content = widgets.GridBox(
        children=[leftCol, rightCol],
        layout=widgets.Layout(
            grid_template_columns="1fr 1fr",
            grid_template_rows="auto auto",
            grid_gap="3px 3px",
            align_items="stretch"
            )
        )
        return content
    
    def getTitle(self):
        return self._project.projectName
    
    def getSelectedDatasets(self):
        dSet = []
        for i, dCheckbox in enumerate(self._datasetCheckboxes):
            if dCheckbox.value:
                dSet.append(self._project.datasets[i])
            
        return dSet