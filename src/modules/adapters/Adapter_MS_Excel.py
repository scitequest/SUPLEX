from modules.SuplexModuleInterface import SuplexModuleInterface
import modules.submodules.File_Directory_Dialog as fdd
import xlsxwriter as excel
import os


class Adapter_MS_Excel():
    MODULE_NAME = "Export to Excel"
    MODULE_GROUP = "Format and Export"

    def __init__(self):
        self._datasets = []
        self._attributeSelector = None
        self._splitByProject = False

    def getModuleName(self):
        return Adapter_MS_Excel.MODULE_NAME

    def getModuleGroupName(self):
        return Adapter_MS_Excel.MODULE_GROUP

    def loadAndCheckDatasets(self, datasets):
        self._datasets = datasets

    def moduleIsViable(self):
        return False

    def getUI(self):
        self._attributeSelector = AttributeSelector(self._datasets, "ANY")
        checkboxes = self._attributeSelector.getUiElements(hideGridIndices=False)

        formatDataButton = widgets.Button(
            description="Format to Excel", button_style="success"
        )
        formatDataButton.on_click(lambda b: self.processData())

        ui = widgets.VBox([checkboxes, formatDataButton])

        return ui

    def processData(self):
        filetypes = [
            ("Excel Workbook", "*.xlsx"),
            ("Excel Macro-Enabled Workbook", "*.xlsm"),
            ("Excel Binary Workbook", "*.xlsb"),
            ("Excel 97-2003 Workbook", "*.xls"),
            ("All files", "*.*"),
        ]

        path = fdd.saveFileDialog(filetypes)

        if not path:
            return
        # TODO: finish this
        if self._splitByProject:
            directory = os.path.dirname(path)
            name, extension = os.path.splitext(os.path.basename(path))

            for projSet in datasets.projects:
                file = name + " - " + proj.name + extension
                filepath = os.path.join(directory, file)
                self.generateWorkbook(projSet, filepath)
            return

        self.generateWorkbook(self._datasets, path)

    def generateWorkbook(data, path):
        workbook = excel.Workbook(path)
        worksheets = []
        for dataset in data:
            worksheets.append(workbook.add_worksheet())

            lines = self.getSheetHeader(dataset)
            for i in range(dataset.nSpots):
                lines = [
                    ["Name", "Age", "City"],
                    ["Alice", 24, "New York"],
                    ["Bob", 27, "Los Angeles"],
                    ["Charlie", 22, "Chicago"],
                    ["David", 32, "Houston"],
                ]

            # Write data to the worksheet
            for row_num, row_data in enumerate(data):
                worksheets[-1].write_row(row_num, 0, row_data)

            # Add a conditional formatting rule to the 'Age' column (Column B)
            worksheets[-1].conditional_format(
                "B2:B5",
                {
                    "type": "cell",
                    "criteria": ">",
                    "value": 25,
                    "format": workbook.add_format({"bg_color": "#00FF00"}),
                },
            )

        workbook.close()

    def getSheetHeader(dataset):
        title = [dataset.metadata.patName]
        subtitle = ["ID:", dataset.metadata.patId]

        header = [title, subtitle, []]  # empty [] are row skips

        if self._attributeSelector.useMetadata():  # method not existent
            return
            [
                "version",
                "date_measured",
                "date_image_created",
                "tags",
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

        header.append(self._attributeSelector.getSelected())

        return header

    def resetModule(self):
        return type(self)()
