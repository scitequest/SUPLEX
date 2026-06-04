from pathlib import Path
import logging
import ipywidgets as widgets
from typing import Dict, List, Optional, Any
from typing_extensions import Self
import statistics
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import ColorScaleRule
import io
from tkinter import Tk, filedialog

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory

from suplex_modules.submodules.submodule_constants import (
    DATASET_SELECTOR_MODE,
    DATASET_LABEL,
    DATASET_ATTRIBUTE,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
)
from suplex_modules.submodules.viability_rules import no_datasets_selected
from suplex_modules.submodules.value_extractor import (
    ValueExtractor,
    extract_value_list_from_dataset,
    get_flat_value_list,
)
from suplex_modules.submodules.submodule_utils import get_shortened_label


logger = logging.getLogger(__name__)


class ExcelAdapter(SuplexModuleInterface):

    def __init__(self):
        """
        Initialize the OverviewHeatmapModule with default settings and UI elements.
        """
        logger.debug("Initializing OverviewHeatmapModule")
        self._datasets = []

        self._DEFAULT_HOVER_TEXT = "Formats MARTin Data into a Microsoft Excel Sheet."
        self._module_hover_text = self._DEFAULT_HOVER_TEXT

        self._value_extractor = None

        logger.debug("OverviewHeatmapModule initialized successfully")

    @property
    def module_name(self) -> str:
        """
        Get the name of the module.

        Returns:
            str: The module name.
        """
        return "MS Excel"

    @property
    def module_version(self) -> str:
        """
        Get the version of the module.

        Returns:
            str: The module version.
        """
        return "0.1.0"

    @property
    def group_name(self) -> str:
        """
        Get the group name of the module.

        Returns:
            str: The group name.
        """
        return "Adapters"

    @property
    def button_style(self) -> Dict[str, str]:
        """
        Get the style configuration for the module button.

        Returns:
            Dict[str, str]: Dictionary containing button style properties.
        """
        icon_path = Path(__file__).parent / "icons" / "excel_adapter_icon.png"

        return {"font_color": "#FFFFFF", "button_color": "#107C41", "button_icon": str(icon_path)}

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        """
        Activates or deactivates the module by a set of rules.
        Currently we only disallow module use if no datasets were selected.

        Returns:
            bool: True if module can be used with datasets loaded.
        """
        logger.debug("Checking viability of module: %s", self.module_name)

        if no_datasets_selected(datasets):
            self._module_hover_text = (
                f"Cannot initiate {self.module_name} since no datasets have been selected."
            )
            logger.info(
                "The module %s has been disabled, since no datasets have been selected.",
                self.module_name,
            )
            return False

        self._module_hover_text = self._DEFAULT_HOVER_TEXT
        logger.debug("%s is viable.", self.module_name)
        return True

    def get_module_hover_text(self) -> str:
        """
        Get the hover text for the module.

        Returns:
            str: The hover text.
        """
        return self._module_hover_text

    def initiate_module(self, datasets: List[Dataset], color_scheme: Any) -> widgets.Box:
        """
        Initialize module with datasets.

        Args:
            datasets (List[Dataset]): List of datasets to initialize with.
            color_scheme (Any): Color scheme to use.

        Returns:
            widgets.Box: The module UI widget.
        """
        logger.debug("Initiating module %s with %d datasets", self.module_name, len(datasets))
        try:
            self._datasets = datasets

            attributes = (
                DATA_ATTRIBUTES
                + DATA_STATISTICS_ATTRIBUTES
                + [DATASET_ATTRIBUTE.SPOT_COORDINATES_X, DATASET_ATTRIBUTE.SPOT_COORDINATES_Y]
            )
            self._value_extractor = ValueExtractor(
                attributes=attributes,
            )

            module_title = WidgetFactory.html_widget(value="<h2>Excel Adapter</h2>", width="auto")
            overview_sheet_box = self.get_overview_sheet_ui()
            individual_sheet_box = self.get_individual_sheet_ui()

            # Main layout: controls on left, tabs on right
            module_ui = WidgetFactory.vbox(
                [module_title, overview_sheet_box, individual_sheet_box],
                layout=widgets.Layout(
                    height="100%", width="100%", overflow="hidden", padding="10px"
                ),
                gap="5px",
            )

            logger.debug("Module UI initialized successfully")
            return module_ui

        except Exception as e:
            logger.error("Failed to initiate module: %s", e, exc_info=True)
            raise

    def get_overview_sheet_ui(self) -> widgets.Widget:
        """
        Create the UI for the overview sheet export section.

        Returns:
            widgets.Widget: The UI widget for the overview sheet export section.
        """
        overview_sheet_title = WidgetFactory.html_widget(
            value="<h3>Overview Sheet</h3>", width="auto"
        )
        value_extractor_ui = self._value_extractor.get_attribute_widget()

        export_overview_button = WidgetFactory.button_success(
            "Export Oveview",
            on_click=lambda b: self.export_overview_sheet(
                attribute=self._value_extractor.attribute
            ),
            layout=widgets.Layout(width="120px", margin="0px", padding="0px"),
            width="auto",
        )

        self._conditional_formatting_overview_sheet = WidgetFactory.checkbox(
            value=True,
            description="Add conditional formatting for each dataset",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        interactive_elements_box = WidgetFactory.hbox(
            children=[
                value_extractor_ui,
                export_overview_button,
                self._conditional_formatting_overview_sheet,
            ],
            layout=widgets.Layout(width="100%", height="auto"),
            gap="10px",
        )

        return WidgetFactory.vbox(
            children=[overview_sheet_title, interactive_elements_box],
            width="100%",
            height="100px",
            gap="5px",
        )

    def get_individual_sheet_ui(self) -> widgets.Widget:
        """
        Create the UI for the individual sheets export section.

        Returns:
            widgets.Widget: The UI widget for the individual sheets export section.
        """
        individual_sheet_title = WidgetFactory.html_widget(
            value="<h3>Individual Sheets</h3>", width="auto"
        )

        metadata_box_label = WidgetFactory.label(value="Header")

        self._id_checkbox = WidgetFactory.checkbox(
            value=True,
            description="ID",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        self._name_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Name",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        self._project_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Project",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        dataset_title_box = WidgetFactory.hbox(
            children=[self._id_checkbox, self._name_checkbox, self._project_checkbox],
            layout=widgets.Layout(width="100%", min_height="30px"),
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        self._timestamp_measured_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Timestamp Measured",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        self._image_generated_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Timestamp Generated",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        timestamps_box = WidgetFactory.hbox(
            children=[self._timestamp_measured_checkbox, self._image_generated_checkbox],
            layout=widgets.Layout(width="100%", min_height="30px"),
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        self._tags_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Tags",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        self._general_parameters_checkbox = WidgetFactory.checkbox(
            value=True,
            description="General parameters",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        self._imager_info_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Imager Info",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )

        self._incubations_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Incubations",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
        )
        metadata_checkboxes_box = WidgetFactory.vbox(
            children=[
                dataset_title_box,
                timestamps_box,
                self._tags_checkbox,
                self._general_parameters_checkbox,
                self._imager_info_checkbox,
                self._incubations_checkbox,
            ],
            width="100%",
            height="auto",
            gap="0px",
            overflow_y="auto",
            overflow_x="visible",
        )

        metadata_box = interactive_elements_box = WidgetFactory.vbox(
            children=[metadata_box_label, metadata_checkboxes_box],
            width="100%",
            height="250px",
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        data_box_label = WidgetFactory.label(value="Individual Spot Values")
        self._data_checkboxes = []
        # One checkbox per value of this enum list
        data_attributes_ext = DATA_ATTRIBUTES + [
            DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
            DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
        ]
        for attribute in data_attributes_ext:
            self._data_checkboxes.append(
                WidgetFactory.checkbox(
                    value=True,
                    description=attribute.value,
                    indent=False,
                    layout=widgets.Layout(margin="0px", padding="0px"),
                    width="auto",
                )
            )
        data_checkboxes_box = WidgetFactory.vbox(
            children=self._data_checkboxes,
            width="100%",
            height="auto",
            gap="0px",
            overflow_y="auto",
            overflow_x="visible",
        )

        data_box = WidgetFactory.vbox(
            children=[data_box_label, data_checkboxes_box],
            width="100%",
            height="100%",
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        data_stats_box_label = WidgetFactory.label(value="Data Statistics")
        self._data_statistics_checkboxes = []
        for attribute in DATA_STATISTICS_ATTRIBUTES:
            self._data_statistics_checkboxes.append(
                WidgetFactory.checkbox(
                    value=True,
                    description=attribute.value,
                    indent=False,
                    layout=widgets.Layout(margin="0px", padding="0px"),
                    width="auto",
                )
            )
        data_statistics_checkboxes_box = WidgetFactory.vbox(
            children=self._data_statistics_checkboxes,
            overflow_y="auto",
            overflow_x="visible",
        )
        data_statistics_box = WidgetFactory.vbox(
            children=[data_stats_box_label, data_statistics_checkboxes_box],
            width="100%",
            height="100%",
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        values_box = WidgetFactory.hbox(
            children=[data_box, data_statistics_box],
            width="100%",
            height="320px",
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        export_individual_button = WidgetFactory.button_success(
            "Export Datasets",
            on_click=lambda b: self.export_individual_sheets(),
            layout=widgets.Layout(width="120px", margin="0px", padding="0px"),
            width="auto",
        )

        self._conditional_formatting_individual_sheet = WidgetFactory.checkbox(
            value=True,
            description="Add conditional formatting for each value col.",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="auto",
            on_click=lambda b: self._export_individual_sheets(),
        )

        bottom_row_controls_box = WidgetFactory.hbox(
            children=[export_individual_button, self._conditional_formatting_individual_sheet],
            width="100%",
            height="auto",
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        disclaimer_html = WidgetFactory.label(
            "Disclaimer: Microsoft Excel is a registered trademark of Microsoft Corporation. This module is not affiliated with or endorsed by Microsoft."
        )
        disclaimer_box = WidgetFactory.hbox(
            children=[disclaimer_html],
            layout=widgets.Layout(width="100%", height="auto", justify_content="flex-end"),
            overflow_y="visible",
            overflow_x="visible",
        )

        bottom_row_box = WidgetFactory.hbox(
            children=[bottom_row_controls_box, disclaimer_box],
            width="100%",
            height="80px",
            gap="5px",
            overflow_y="visible",
            overflow_x="visible",
        )

        return WidgetFactory.vbox(
            children=[individual_sheet_title, metadata_box, values_box, bottom_row_box],
            layout=widgets.Layout(width="100%", height="100%", justify_content="space-between"),
            gap="5px",
        )

    def export_overview_sheet(self, attribute: DATASET_ATTRIBUTE):
        """
        This method generates an Excel workbook with a single sheet that organizes data for a selected attribute from all provided datasets.
        The sheet includes a header row with dataset IDs and a position column indicating sample and spot indices (or samples for statistical attributes).

        The data is structured as a matrix where each column represents a dataset and each row corresponds to a sample or spot position.
        If conditional formatting is enabled, a green color scale is applied to each dataset column individually to highlight value ranges.

        Args:
            attribute (DATASET_ATTRIBUTE): The dataset attribute to export.
        """
        logger.debug("Exporting file")
        apply_conditional_formatting = self._conditional_formatting_overview_sheet.value
        spot_coordinates = [
            DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
            DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
        ]

        sheet_head = [f"Overview - {attribute.value}"]

        max_samples = 0
        max_spots_per_sample = 0

        for dataset in self._datasets:
            spot_value_list = extract_value_list_from_dataset(dataset, attribute=attribute)
            n_samples = len(spot_value_list)
            max_samples = max(max_samples, n_samples)

            value_list = get_flat_value_list(dataset, attribute=attribute)
            n_spots = int(len(value_list) / n_samples) if n_samples > 0 else 0
            max_spots_per_sample = max(max_spots_per_sample, n_spots)

        if attribute in DATA_STATISTICS_ATTRIBUTES:
            position_col = [f"Sample_{i}" for i in range(max_samples)]
        else:
            position_col = [
                f"Sample_{i}_Spot_{j}"
                for i in range(max_samples)
                for j in range(max_spots_per_sample)
            ]

        sheet_content = []

        for dataset in self._datasets:
            sheet_head.append(dataset.id)
            if attribute in DATA_STATISTICS_ATTRIBUTES:
                value_list = get_flat_value_list(dataset, attribute=attribute)

                # Pad to max_samples
                while len(value_list) < max_samples:
                    value_list.append(None)

                sheet_content.append(value_list)

            else:
                spot_value_list = extract_value_list_from_dataset(dataset, attribute=attribute)
                # Calculate Average coordinates
                if attribute in spot_coordinates:
                    spot_value_list = [
                        [
                            statistics.mean(spot_coords) if spot_coords else 0.0
                            for spot_coords in sample_spots
                        ]
                        for sample_spots in spot_value_list
                    ]

                # Create padded flattened list
                value_list = []
                for i in range(max_samples):
                    if i < len(spot_value_list):
                        sample_spots = spot_value_list[i]
                        # Add existing spots
                        for j in range(max_spots_per_sample):
                            if j < len(sample_spots):
                                value_list.append(sample_spots[j])
                            else:
                                # Pad missing spots in existing sample
                                value_list.append(None)
                    else:
                        # Pad entire missing sample
                        value_list.extend([None] * max_spots_per_sample)

                sheet_content.append(value_list)

        # Create Excel workbook with openpyxl
        wb = Workbook()
        ws = wb.active
        ws.title = get_shortened_label(f"{attribute.value}", 31)

        # Write header row
        for col, header in enumerate(sheet_head, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        # Write position column
        for row, position in enumerate(position_col, 2):
            cell = ws.cell(row=row, column=1, value=position)
            cell.font = Font(bold=True)

        # Write data
        for col, dataset_values in enumerate(sheet_content, 2):
            for row, value in enumerate(dataset_values, 2):
                ws.cell(row=row, column=col, value=value)

        # Apply conditional formatting if enabled - per dataset (column)
        if apply_conditional_formatting and sheet_content:
            start_row = 2  # First data row
            end_row = len(position_col) + 1  # Last data row

            # Apply color scale to each dataset column individually
            for col_idx in range(len(sheet_content)):
                # Dataset columns start at column 2
                data_col = col_idx + 2
                column_range = f"{ws.cell(start_row, data_col).coordinate}:{ws.cell(end_row, data_col).coordinate}"

                # Apply color scale for this column
                color_scale = ColorScaleRule(
                    start_type="min",
                    start_color="FFFFFF",  # White
                    end_type="max",
                    end_color="008000",  # Dark Green
                )
                ws.conditional_formatting.add(column_range, color_scale)

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            ws.column_dimensions[column_letter].width = adjusted_width

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # File dialog for export
        root = Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        root.focus_force()

        default_filename = f"{attribute.value}.xlsx"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=default_filename,
            title="Export Overview Sheet",
        )
        root.attributes("-topmost", False)
        root.destroy()

        if file_path:
            with open(file_path, "wb") as f:
                f.write(buffer.getvalue())
            logger.info("Overview sheet exported successfully to %s", file_path)
        else:
            logger.debug("File export cancelled by user")

    def export_individual_sheets(self):
        """
        This method creates an Excel workbook with one sheet per dataset.

        Each sheet contains a header section with metadata based on user-selected options.
        Below the header, two tables are generated for data statistics and data values.

        Conditional formatting (green color scale) is applied to attribute columns if enabled.

        """
        logger.debug("Exporting individual sheets")

        # Collect selected attributes based on checkboxes
        data_attributes_ext = DATA_ATTRIBUTES + [
            DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
            DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
        ]
        data_attributes = [
            attr for attr, cb in zip(data_attributes_ext, self._data_checkboxes) if cb.value
        ]

        data_statistics_attributes = [
            attr
            for attr, cb in zip(DATA_STATISTICS_ATTRIBUTES, self._data_statistics_checkboxes)
            if cb.value
        ]

        apply_conditional_formatting = self._conditional_formatting_individual_sheet.value

        if not data_attributes and not data_statistics_attributes:
            logger.warning("No attributes selected for export")
            return

        # Create Excel workbook with openpyxl
        wb = Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # Create a new sheet for each dataset
        for dataset in self._datasets:
            # Truncate title if too long for Excel
            ws = wb.create_sheet(title=get_shortened_label(dataset.id, 31))

            # Build Header
            header_row = 1
            col = 1

            # Row 1: Project, ID, Name (direct values, larger font) with column gaps
            if self._id_checkbox.value or self._name_checkbox.value or self._project_checkbox.value:
                if self._project_checkbox.value:
                    project_name = dataset.project.name if dataset.project else "N/A"
                    ws.cell(row=header_row, column=col, value=project_name).font = Font(
                        bold=True, size=16
                    )
                    col += 2  # One column gap after Project
                if self._id_checkbox.value:
                    ws.cell(row=header_row, column=col, value=dataset.id).font = Font(
                        bold=True, size=16
                    )
                    col += 1
                if self._name_checkbox.value:
                    ws.cell(row=header_row, column=col, value=dataset.name).font = Font(
                        bold=True, size=16
                    )
                header_row += 1
                header_row += 2  # Two empty lines after this row
                col = 1  # Reset col for next row

            # Timestamps row
            if self._timestamp_measured_checkbox.value or self._image_generated_checkbox.value:
                if self._timestamp_measured_checkbox.value:
                    measure_date = (
                        dataset.measure_date.strftime("%Y-%m-%d %H:%M:%S")
                        if dataset.measure_date
                        else "N/A"
                    )
                    ws.cell(
                        row=header_row, column=col, value=f"Timestamp Measured: {measure_date}"
                    ).font = Font(bold=True)
                    col += 2
                if self._image_generated_checkbox.value:
                    creation_date = (
                        dataset.image_creation_date.strftime("%Y-%m-%d %H:%M:%S")
                        if dataset.image_creation_date
                        else "N/A"
                    )
                    ws.cell(
                        row=header_row, column=col, value=f"Timestamp Generated: {creation_date}"
                    ).font = Font(bold=True)
                header_row += 1
                col = 1

            # Tags row
            if self._tags_checkbox.value:
                tags_str = ", ".join(dataset.tags) if dataset.tags else "N/A"
                ws.cell(row=header_row, column=col, value=f"Tags: {tags_str}").font = Font(
                    bold=True
                )
                header_row += 1
                col = 1

            # General Parameters row
            if self._general_parameters_checkbox.value and dataset.general_parameters:
                gp = dataset.general_parameters
                params = [
                    f"Invert LUT: {gp.invert_lut}",
                    f"Subtract Background: {gp.subtract_background}",
                    f"Number of Spotfields: {gp.number_of_spotfields}",
                    f"Columns per Spotfield: {gp.columns_per_spotfield}",
                    f"Spots per Spotfield: {gp.spots_per_spotfield}",
                ]
                for param in params:
                    ws.cell(row=header_row, column=col, value=param).font = Font(bold=True)
                    col += 1  # No gap between these categories
                header_row += 1
                col = 1

            # Imager Info row
            if self._imager_info_checkbox.value and dataset.metadata:
                img = dataset.metadata.image
                info = [
                    f"Imager: {img.imager}",
                    f"Pixel Binning: {img.pixel_binning}",
                    f"Exposure Time: {str(img.exposure_time)}",
                ]
                for item in info:
                    ws.cell(row=header_row, column=col, value=item).font = Font(bold=True)
                    col += 2
                header_row += 1
                col = 1

            # One empty line before Incubations
            if (
                self._incubations_checkbox.value
                and dataset.metadata
                and dataset.metadata.incubations
            ):
                header_row += 1  # One line space before incubations

                for i, inc in enumerate(dataset.metadata.incubations):
                    inc_row = header_row
                    # First line: Incubation i in col1, Solution: x in col2
                    ws.cell(row=inc_row, column=col, value=f"Incubation {i}").font = Font(bold=True)
                    ws.cell(row=inc_row, column=col + 1, value=f"Solution: {inc.solution}").font = (
                        Font(bold=True)
                    )
                    inc_row += 1

                    # Subsequent lines: Label in col1, Value in col2
                    stock_unit = (
                        "%"
                        if inc.stock_concentration.unit == "percent"
                        else inc.stock_concentration.unit
                    )
                    final_unit = (
                        "%"
                        if inc.final_concentration.unit == "percent"
                        else inc.final_concentration.unit
                    )

                    # Stock Conc
                    ws.cell(row=inc_row, column=col, value="Stock Conc:").font = Font(bold=True)
                    ws.cell(
                        row=inc_row,
                        column=col + 1,
                        value=f"{inc.stock_concentration.value} {stock_unit}",
                    ).font = Font(bold=True)
                    inc_row += 1

                    # Final Conc
                    ws.cell(row=inc_row, column=col, value="Final Conc:").font = Font(bold=True)
                    ws.cell(
                        row=inc_row,
                        column=col + 1,
                        value=f"{inc.final_concentration.value} {final_unit}",
                    ).font = Font(bold=True)
                    inc_row += 1

                    # Incubation Time
                    ws.cell(row=inc_row, column=col, value="Incubation Time:").font = Font(
                        bold=True
                    )
                    ws.cell(row=inc_row, column=col + 1, value=str(inc.incubation_time)).font = (
                        Font(bold=True)
                    )

                    col += 3  # Two columns for block + one gap to next block

                # Advance header_row by the max block height (4 lines: title + 3 details)
                header_row += 4
                col = 1

            # Add some space after header
            table_title_row = header_row + 1
            headers_row = table_title_row + 2
            data_start_row = headers_row + 1

            # Spot Values Table (left side)
            if data_attributes:
                # Table title
                ws.cell(row=table_title_row, column=1, value="Spot Values").font = Font(
                    bold=True, size=14
                )

                # Headers: Sample, Spot, then each attribute
                headers = ["Sample", "Spot"] + [attr.value for attr in data_attributes]
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=headers_row, column=col, value=header)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(
                        start_color="CCCCCC", end_color="CCCCCC", fill_type="solid"
                    )
                    cell.alignment = Alignment(horizontal="center")

                # Data rows
                row_idx = data_start_row
                for sample_idx, sample_spots in enumerate(
                    extract_value_list_from_dataset(dataset, attribute=data_attributes[0])
                ):  # Use first attr to get structure
                    for spot_idx in range(len(sample_spots)):
                        # Write Sample and Spot indices (0-based)
                        ws.cell(row=row_idx, column=1, value=sample_idx)
                        ws.cell(row=row_idx, column=2, value=spot_idx)

                        # Write values for each attribute
                        for attr_col, attr in enumerate(data_attributes, 3):
                            spot_value_list = extract_value_list_from_dataset(
                                dataset, attribute=attr
                            )
                            if sample_idx < len(spot_value_list) and spot_idx < len(
                                spot_value_list[sample_idx]
                            ):
                                value = spot_value_list[sample_idx][spot_idx]
                                # For coordinates, take mean if list
                                if attr in [
                                    DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
                                    DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
                                ]:
                                    value = statistics.mean(value) if value else 0.0
                                ws.cell(row=row_idx, column=attr_col, value=value)
                            else:
                                ws.cell(row=row_idx, column=attr_col, value=None)

                        row_idx += 1

                # Apply conditional formatting per attribute column if enabled
                if apply_conditional_formatting:
                    start_row = data_start_row
                    end_row = row_idx - 1
                    num_attrs = len(data_attributes)
                    if end_row >= start_row:
                        for attr_col in range(3, 3 + num_attrs):  # Attribute columns start at 3
                            column_range = f"{ws.cell(start_row, attr_col).coordinate}:{ws.cell(end_row, attr_col).coordinate}"
                            color_scale = ColorScaleRule(
                                start_type="min",
                                start_color="FFFFFF",  # White
                                end_type="max",
                                end_color="008000",  # Dark Green
                            )
                            ws.conditional_formatting.add(column_range, color_scale)

            # Sample Values Table (right side, with 2 columns gap)
            if data_statistics_attributes:
                # Determine starting column: after spot table + 2 gap columns
                sample_table_start_col = (
                    (2 + len(data_attributes) + 3) if data_attributes else 1
                )  # +3: spot cols + 2 gap

                # Table title
                ws.cell(
                    row=table_title_row, column=sample_table_start_col, value="Sample Values"
                ).font = Font(bold=True, size=14)

                # Headers: Sample, then each statistic attribute
                headers = ["Sample"] + [attr.value for attr in data_statistics_attributes]
                for col_offset, header in enumerate(headers):
                    cell = ws.cell(
                        row=headers_row, column=sample_table_start_col + col_offset, value=header
                    )
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(
                        start_color="CCCCCC", end_color="CCCCCC", fill_type="solid"
                    )
                    cell.alignment = Alignment(horizontal="center")

                # Data rows
                row_idx = data_start_row
                for sample_idx in range(
                    len(get_flat_value_list(dataset, attribute=data_statistics_attributes[0]))
                ):  # Use first stat to get num samples
                    # Write Sample index
                    ws.cell(row=row_idx, column=sample_table_start_col, value=sample_idx)

                    # Write values for each statistic attribute
                    for attr_col, attr in enumerate(data_statistics_attributes, 1):
                        value_list = get_flat_value_list(dataset, attribute=attr)
                        if sample_idx < len(value_list):
                            ws.cell(
                                row=row_idx,
                                column=sample_table_start_col + attr_col,
                                value=value_list[sample_idx],
                            )
                        else:
                            ws.cell(
                                row=row_idx, column=sample_table_start_col + attr_col, value=None
                            )

                    row_idx += 1

                # Apply conditional formatting per attribute column if enabled
                if apply_conditional_formatting:
                    start_row = data_start_row
                    end_row = row_idx - 1
                    num_attrs = len(data_statistics_attributes)
                    if end_row >= start_row:
                        for attr_col in range(
                            1, 1 + num_attrs
                        ):  # Relative to sample_table_start_col
                            column_range = f"{ws.cell(start_row, sample_table_start_col + attr_col).coordinate}:{ws.cell(end_row, sample_table_start_col + attr_col).coordinate}"
                            color_scale = ColorScaleRule(
                                start_type="min",
                                start_color="FFFFFF",  # White
                                end_type="max",
                                end_color="008000",  # Dark Green
                            )
                            ws.conditional_formatting.add(column_range, color_scale)

            # Auto-adjust column widths for the entire sheet
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                ws.column_dimensions[column_letter].width = adjusted_width

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # File dialog for export
        root = Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        root.focus_force()

        # Collect project names for default filename
        project_str = (
            "-".join(set(ds.project.name for ds in self._datasets if ds.project)) or "datasets"
        )
        default_filename = f"{project_str}.xlsx"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=default_filename,
            title="Export Individual Sheets",
        )
        root.attributes("-topmost", False)
        root.destroy()

        if file_path:
            with open(file_path, "wb") as f:
                f.write(buffer.getvalue())
            logger.info("Individual sheets exported successfully to %s", file_path)
        else:
            logger.debug("File export cancelled by user")

    def update_scheme(self, new_scheme) -> None:
        """
        Update the color scheme and refresh analysis.
        Excel Adapter does not have any special elements, so this method does nothing

        Args:
            new_scheme: New color scheme to apply.
        """
        pass

    def reset_module(self) -> Optional[Self]:
        """
        Reset module to initial state.

        Returns:
            Optional[Self]: New instance of the module or None if reset failed.
        """
        logger.debug("Resetting module")
        try:
            new_module = ExcelAdapter()
            logger.debug("Module reset successfully")
            return new_module
        except Exception as e:
            logger.error("Failed to reset module: %s", e, exc_info=True)
            return None
