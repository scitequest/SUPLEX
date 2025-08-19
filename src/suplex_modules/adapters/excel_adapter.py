import ipywidgets as widgets
from typing import Dict, List, Optional, Any
from typing_extensions import Self
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
import os

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.dataset_selector import DatasetSelector
from suplex_modules.submodules.submodule_constants import DATASET_SELECTOR_MODE, DATASET_LABEL


class ExcelExportModule(SuplexModuleInterface):
    """
    Module for exporting SUPLEX datasets to Excel files with extensive configuration options.
    """

    def __init__(self):
        self._datasets = []
        self._dataset_selector = None
        self._export_config = {
            "sheet_mode": "multiple",  # "single" or "multiple"
            "data_types": {
                "spots": True,
                "statistics": True,
                "parameters": False
            },
            "spot_fields": {
                "mean_val": True,
                "normalized_mean": True,
                "mean_minus_min": False,
                "min_val": False,
                "max_val": False,
                "std_deviation": True,
                "row": True,
                "col": True,
                "spot": True
            },
            "statistics_fields": {
                "adjusted_average": True,
                "average": True,
                "confidence_interval": True,
                "coefficient_of_variation": True,
                "median": True,
                "row": True,
                "col": True
            },
            "parameter_fields": {
                "exposure_time": True,
                "imager": True,
                "pixel_binning": True,
                "wavelength": True,
                "aperture": True
            },
            "header_config": {
                "enabled": True,
                "name": True,
                "pat_id": True,
                "measure_date": True,
                "tags": True,
                "incubations": True
            },
            "formatting": {
                "enabled": True,
                "type": "color_scale",  # "color_scale", "data_bars", "icon_sets", "custom"
                "color_scale": {
                    "min_color": "FF0000",  # Red
                    "mid_color": "FFFF00",  # Yellow
                    "max_color": "00FF00"   # Green
                }
            }
        }
        self._ui_elements = {}

    @property
    def module_name(self) -> str:
        return "Excel Export"

    @property
    def module_version(self) -> str:
        return "1.0.0"

    @property
    def group_name(self) -> str:
        return "Adapters"

    @property
    def button_style(self) -> Dict[str, str]:
        return {
            "font_color": "#FFFFFF",
            "button_color": "#107C10",  # Excel green
            "button_icon": "E"
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        return "Export datasets to Excel with configurable formatting and structure. Requires at least one dataset."

    def initiate_module(self, datasets: List[Dataset]) -> widgets.Box:
        self._datasets = datasets
        
        # Header
        header = WidgetFactory.html_widget(
            value="<h2 style='color: #107C10; margin-bottom: 20px;'>📊 Excel Export Module</h2>",
            width="100%"
        )
        
        # Dataset selector
        self._dataset_selector = DatasetSelector(
            datasets=datasets,
            mode=DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND,
            label_parts=[DATASET_LABEL.NAME, DATASET_LABEL.MEASURE_DATE, DATASET_LABEL.ID]
        )
        
        # Create tabs
        tabs = WidgetFactory.tab(
            children=[
                self._create_export_tab(),
                self._create_data_selection_tab(),
                self._create_formatting_tab(),
                self._create_header_config_tab()
            ],
            titles=["Export", "Data Selection", "Formatting", "Header Config"]
        )
        
        return WidgetFactory.vbox([header, tabs])

    def _create_export_tab(self) -> widgets.Widget:
        """Creates the main export tab"""
        
        # Sheet mode selection
        sheet_mode_label = WidgetFactory.html_widget("<h4>Sheet Organization:</h4>")
        self._ui_elements["sheet_mode"] = WidgetFactory.custom_radio_buttons(
            number=2,
            description=["Single Sheet (All datasets)", "Multiple Sheets (One per dataset)"],
            i_toggled=1
        )
        
        # File name input
        self._ui_elements["filename"] = WidgetFactory.text_input(
            value="suplex_export",
            placeholder="Enter filename (without .xlsx)",
            description="Filename:"
        )
        
        # Export button
        export_btn = WidgetFactory.button_emphasis(
            "Export to Excel",
            icon="💾",
            on_click=self._on_export_click
        )
        
        # Progress and status
        self._ui_elements["progress"] = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description="Progress:",
            bar_style="success",
            style={"bar_color": "#107C10"},
            orientation="horizontal"
        )
        self._ui_elements["progress"].layout.display = "none"
        
        self._ui_elements["status"] = WidgetFactory.vbox([])
        
        # Dataset selector and export controls
        export_controls = WidgetFactory.vbox([
            sheet_mode_label,
            WidgetFactory.hbox(self._ui_elements["sheet_mode"], gap="10px"),
            self._ui_elements["filename"],
            export_btn,
            self._ui_elements["progress"],
            self._ui_elements["status"]
        ], gap="15px")
        
        return WidgetFactory.hbox([
            self._dataset_selector.get_ui_element(),
            export_controls
        ], gap="20px")

    def _create_data_selection_tab(self) -> widgets.Widget:
        """Creates the data selection configuration tab"""
        
        # Data type selection
        data_type_label = WidgetFactory.html_widget("<h4>Data Types to Export:</h4>")
        self._ui_elements["export_spots"] = WidgetFactory.checkbox(
            value=True,
            description="Spot Data (Raw measurements)",
            on_change=self._on_data_type_change
        )
        self._ui_elements["export_statistics"] = WidgetFactory.checkbox(
            value=True,
            description="Data Statistics (Aggregated values)",
            on_change=self._on_data_type_change
        )
        self._ui_elements["export_parameters"] = WidgetFactory.checkbox(
            value=False,
            description="General Parameters",
            on_change=self._on_data_type_change
        )
        
        # Field selection for spots
        spot_fields_label = WidgetFactory.html_widget("<h4>Spot Data Fields:</h4>")
        spot_fields = []
        for field, enabled in self._export_config["spot_fields"].items():
            cb = WidgetFactory.checkbox(
                value=enabled,
                description=self._format_field_name(field)
            )
            self._ui_elements[f"spot_{field}"] = cb
            spot_fields.append(cb)
        
        # Field selection for statistics
        stats_fields_label = WidgetFactory.html_widget("<h4>Statistics Fields:</h4>")
        stats_fields = []
        for field, enabled in self._export_config["statistics_fields"].items():
            cb = WidgetFactory.checkbox(
                value=enabled,
                description=self._format_field_name(field)
            )
            self._ui_elements[f"stats_{field}"] = cb
            stats_fields.append(cb)
        
        # Field selection for parameters
        param_fields_label = WidgetFactory.html_widget("<h4>Parameter Fields:</h4>")
        param_fields = []
        for field, enabled in self._export_config["parameter_fields"].items():
            cb = WidgetFactory.checkbox(
                value=enabled,
                description=self._format_field_name(field)
            )
            self._ui_elements[f"param_{field}"] = cb
            param_fields.append(cb)
        
        # Layout with columns
        left_column = WidgetFactory.vbox([
            data_type_label,
            self._ui_elements["export_spots"],
            self._ui_elements["export_statistics"],
            self._ui_elements["export_parameters"],
            spot_fields_label,
            *spot_fields[:5]
        ], gap="5px")
        
        right_column = WidgetFactory.vbox([
            WidgetFactory.html_widget("<div style='height: 20px;'></div>"),  # Spacer
            *spot_fields[5:],
            stats_fields_label,
            *stats_fields,
            param_fields_label,
            *param_fields
        ], gap="5px")
        
        return WidgetFactory.hbox([left_column, right_column], gap="40px")

    def _create_formatting_tab(self) -> widgets.Widget:
        """Creates the formatting configuration tab"""
        
        # Enable formatting
        self._ui_elements["formatting_enabled"] = WidgetFactory.checkbox(
            value=True,
            description="Enable Conditional Formatting",
            on_change=self._on_formatting_change
        )
        
        # Formatting type
        formatting_type_label = WidgetFactory.html_widget("<h4>Formatting Type:</h4>")
        self._ui_elements["formatting_type"] = WidgetFactory.dropdown(
            options=["Color Scale", "Data Bars", "Icon Sets", "Custom Rules"],
            value="Color Scale",
            description="Type:"
        )
        
        # Color scale configuration
        color_scale_label = WidgetFactory.html_widget("<h4>Color Scale Configuration:</h4>")
        
        # Color pickers (simplified as text inputs for hex colors)
        self._ui_elements["min_color"] = WidgetFactory.text_input(
            value="#FF0000",
            placeholder="#FF0000",
            description="Minimum Color (Hex):"
        )
        self._ui_elements["mid_color"] = WidgetFactory.text_input(
            value="#FFFF00",
            placeholder="#FFFF00",
            description="Middle Color (Hex):"
        )
        self._ui_elements["max_color"] = WidgetFactory.text_input(
            value="#00FF00",
            placeholder="#00FF00",
            description="Maximum Color (Hex):"
        )
        
        # Preview
        preview_html = """
        <h4>Preview:</h4>
        <div style='display: flex; gap: 10px; align-items: center;'>
            <div style='width: 60px; height: 30px; background: #FF0000; border: 1px solid #ccc;'></div>
            <span>Low Values</span>
            <div style='width: 60px; height: 30px; background: #FFFF00; border: 1px solid #ccc;'></div>
            <span>Mid Values</span>
            <div style='width: 60px; height: 30px; background: #00FF00; border: 1px solid #ccc;'></div>
            <span>High Values</span>
        </div>
        """
        preview = WidgetFactory.html_widget(preview_html)
        
        # Additional formatting options
        additional_label = WidgetFactory.html_widget("<h4>Additional Options:</h4>")
        self._ui_elements["bold_headers"] = WidgetFactory.checkbox(
            value=True,
            description="Bold Headers"
        )
        self._ui_elements["autofit_columns"] = WidgetFactory.checkbox(
            value=True,
            description="Auto-fit Column Width"
        )
        self._ui_elements["freeze_headers"] = WidgetFactory.checkbox(
            value=True,
            description="Freeze Header Row"
        )
        
        return WidgetFactory.vbox([
            self._ui_elements["formatting_enabled"],
            formatting_type_label,
            self._ui_elements["formatting_type"],
            color_scale_label,
            self._ui_elements["min_color"],
            self._ui_elements["mid_color"],
            self._ui_elements["max_color"],
            preview,
            additional_label,
            self._ui_elements["bold_headers"],
            self._ui_elements["autofit_columns"],
            self._ui_elements["freeze_headers"]
        ], gap="10px")

    def _create_header_config_tab(self) -> widgets.Widget:
        """Creates the header configuration tab"""
        
        # Enable headers
        self._ui_elements["header_enabled"] = WidgetFactory.checkbox(
            value=True,
            description="Include Dataset Headers",
            on_change=self._on_header_change
        )
        
        # Header fields
        header_fields_label = WidgetFactory.html_widget("<h4>Header Information to Include:</h4>")
        
        header_fields = []
        for field, enabled in self._export_config["header_config"].items():
            if field != "enabled":
                cb = WidgetFactory.checkbox(
                    value=enabled,
                    description=self._format_field_name(field)
                )
                self._ui_elements[f"header_{field}"] = cb
                header_fields.append(cb)
        
        # Header preview
        preview_label = WidgetFactory.html_widget("<h4>Header Preview:</h4>")
        self._ui_elements["header_preview"] = WidgetFactory.info_field_default([
            WidgetFactory.html_widget(self._generate_header_preview())
        ])
        
        # Update preview button
        update_preview_btn = WidgetFactory.button_default(
            "Update Preview",
            on_click=self._update_header_preview
        )
        
        return WidgetFactory.vbox([
            self._ui_elements["header_enabled"],
            header_fields_label,
            *header_fields,
            preview_label,
            update_preview_btn,
            self._ui_elements["header_preview"]
        ], gap="10px")

    def _on_export_click(self, button):
        """Handles the export button click"""
        selected_datasets = self._dataset_selector.get_selected_datasets()
        
        if not selected_datasets:
            self._show_status("error", "⚠️ Please select at least one dataset to export.")
            return
        
        # Update configuration from UI
        self._update_config_from_ui()
        
        # Show progress
        self._ui_elements["progress"].layout.display = "block"
        self._ui_elements["progress"].value = 0
        
        try:
            # Perform export
            filename = self._export_to_excel(selected_datasets)
            self._show_status("success", f"✅ Successfully exported to: {filename}")
        except Exception as e:
            self._show_status("error", f"❌ Export failed: {str(e)}")
        finally:
            self._ui_elements["progress"].layout.display = "none"

    def _export_to_excel(self, datasets: List[Dataset]) -> str:
        """Performs the actual Excel export"""
        filename = f"{self._ui_elements["filename"].value}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            
            if self._export_config["sheet_mode"] == "single":
                # Single sheet mode
                self._export_single_sheet(writer, datasets)
            else:
                # Multiple sheets mode
                total_datasets = len(datasets)
                for i, dataset in enumerate(datasets):
                    # Update progress
                    self._ui_elements["progress"].value = int((i / total_datasets) * 100)
                    
                    sheet_name = self._get_sheet_name(dataset, i)
                    self._export_dataset_to_sheet(writer, dataset, sheet_name)
            
            # Apply formatting if enabled
            if self._export_config["formatting"]["enabled"]:
                self._apply_formatting(writer.book)
        
        self._ui_elements["progress"].value = 100
        return filename

    def _export_single_sheet(self, writer, datasets: List[Dataset]):
        """Exports all datasets to a single sheet"""
        all_data = []
        current_row = 0
        
        worksheet = writer.book.create_sheet("All Datasets")
        
        for dataset in datasets:
            # Add header if enabled
            if self._export_config["header_config"]["enabled"]:
                header_df = self._create_header_dataframe(dataset)
                header_df.to_excel(writer, sheet_name="All Datasets", 
                                 startrow=current_row, index=False, header=False)
                current_row += len(header_df) + 1
            
            # Add data
            if self._export_config["data_types"]["spots"]:
                spots_df = self._create_spots_dataframe(dataset)
                if not spots_df.empty:
                    spots_df.to_excel(writer, sheet_name="All Datasets", 
                                    startrow=current_row, index=False)
                    current_row += len(spots_df) + 2
            
            if self._export_config["data_types"]["statistics"]:
                stats_df = self._create_statistics_dataframe(dataset)
                if not stats_df.empty:
                    stats_df.to_excel(writer, sheet_name="All Datasets", 
                                    startrow=current_row, index=False)
                    current_row += len(stats_df) + 2
            
            # Add separator
            current_row += 2

    def _export_dataset_to_sheet(self, writer, dataset: Dataset, sheet_name: str):
        """Exports a single dataset to a sheet"""
        current_row = 0
        
        # Create sheet
        worksheet = writer.book.create_sheet(sheet_name)
        
        # Add header if enabled
        if self._export_config["header_config"]["enabled"]:
            header_df = self._create_header_dataframe(dataset)
            header_df.to_excel(writer, sheet_name=sheet_name, 
                             startrow=current_row, index=False, header=False)
            current_row += len(header_df) + 1
        
        # Add data sections
        if self._export_config["data_types"]["spots"]:
            # Section header
            section_df = pd.DataFrame([["SPOT DATA"]])
            section_df.to_excel(writer, sheet_name=sheet_name, 
                              startrow=current_row, index=False, header=False)
            current_row += 1
            
            spots_df = self._create_spots_dataframe(dataset)
            if not spots_df.empty:
                spots_df.to_excel(writer, sheet_name=sheet_name, 
                                startrow=current_row, index=False)
                current_row += len(spots_df) + 2
        
        if self._export_config["data_types"]["statistics"]:
            # Section header
            section_df = pd.DataFrame([["DATA STATISTICS"]])
            section_df.to_excel(writer, sheet_name=sheet_name, 
                              startrow=current_row, index=False, header=False)
            current_row += 1
            
            stats_df = self._create_statistics_dataframe(dataset)
            if not stats_df.empty:
                stats_df.to_excel(writer, sheet_name=sheet_name, 
                                startrow=current_row, index=False)
                current_row += len(stats_df) + 2
        
        if self._export_config["data_types"]["parameters"]:
            # Section header
            section_df = pd.DataFrame([["GENERAL PARAMETERS"]])
            section_df.to_excel(writer, sheet_name=sheet_name, 
                              startrow=current_row, index=False, header=False)
            current_row += 1
            
            params_df = self._create_parameters_dataframe(dataset)
            if not params_df.empty:
                params_df.to_excel(writer, sheet_name=sheet_name, 
                                 startrow=current_row, index=False)

    def _create_header_dataframe(self, dataset: Dataset) -> pd.DataFrame:
        """Creates a header dataframe from dataset metadata"""
        header_data = []
        
        if dataset.metadata:
            if self._export_config["header_config"]["name"]:
                header_data.append(["Dataset Name:", dataset.metadata.name])
            
            if self._export_config["header_config"]["pat_id"]:
                header_data.append(["Patient ID:", dataset.metadata.pat_id])
            
            if self._export_config["header_config"]["measure_date"] and dataset.measure_date:
                header_data.append(["Measurement Date:", 
                                  dataset.measure_date.strftime("%Y-%m-%d %H:%M:%S")])
            
            if self._export_config["header_config"]["tags"]:
                all_tags = dataset.tags + dataset.suplex_tags
                if all_tags:
                    header_data.append(["Tags:", ", ".join(all_tags)])
            
            if self._export_config["header_config"]["incubations"] and dataset.metadata.incubations:
                incubation_str = "; ".join([
                    f"{inc.solution} ({inc.final_concentration.value}{inc.final_concentration.unit})"
                    for inc in dataset.metadata.incubations
                ])
                header_data.append(["Incubations:", incubation_str])
        
        return pd.DataFrame(header_data, columns=["Field", "Value"])

    def _create_spots_dataframe(self, dataset: Dataset) -> pd.DataFrame:
        """Creates a dataframe from spot data"""
        data = []
        
        for sample_idx, sample in enumerate(dataset.samples):
            for spot_idx, spot in enumerate(sample.spots):
                row_data = {"sample_id": sample_idx, "spot_id": spot_idx}
                
                # Add selected fields
                for field, include in self._export_config["spot_fields"].items():
                    if include and hasattr(spot, field):
                        row_data[field] = getattr(spot, field)
                
                data.append(row_data)
        
        return pd.DataFrame(data)

    def _create_statistics_dataframe(self, dataset: Dataset) -> pd.DataFrame:
        """Creates a dataframe from statistics data"""
        data = []
        
        for sample_idx, sample in enumerate(dataset.samples):
            if sample.data_statistics:
                stats = sample.data_statistics
                row_data = {"sample_id": sample_idx}
                
                # Add selected fields
                for field, include in self._export_config["statistics_fields"].items():
                    if include and hasattr(stats, field):
                        value = getattr(stats, field)
                        # Handle confidence interval tuple
                        if field == "confidence_interval" and value:
                            row_data["ci_lower"] = value[0]
                            row_data["ci_upper"] = value[1]
                        else:
                            row_data[field] = value
                
                data.append(row_data)
        
        return pd.DataFrame(data)

    def _create_parameters_dataframe(self, dataset: Dataset) -> pd.DataFrame:
        """Creates a dataframe from general parameters"""
        if not dataset.general_parameters:
            return pd.DataFrame()
        
        params = dataset.general_parameters
        data = []
        
        for field, include in self._export_config["parameter_fields"].items():
            if include and hasattr(params, field):
                value = getattr(params, field)
                # Format timedelta
                if field == "exposure_time" and value:
                    value = str(value)
                data.append({"Parameter": self._format_field_name(field), "Value": value})
        
        return pd.DataFrame(data)

    def _apply_formatting(self, workbook):
        """Applies formatting to the Excel workbook"""
        for sheet in workbook.worksheets:
            # Apply conditional formatting to numerical columns
            if self._export_config["formatting"]["type"] == "color_scale":
                self._apply_color_scale(sheet)
            
            # Bold headers
            if self._ui_elements["bold_headers"].value:
                self._bold_headers(sheet)
            
            # Auto-fit columns
            if self._ui_elements["autofit_columns"].value:
                self._autofit_columns(sheet)
            
            # Freeze panes
            if self._ui_elements["freeze_headers"].value:
                sheet.freeze_panes = "A2"

    def _apply_color_scale(self, sheet):
        """Applies color scale conditional formatting"""
        # Find numerical columns
        for col in sheet.columns:
            col_letter = col[0].column_letter
            is_numeric = True
            
            # Check if column contains numbers (skip header)
            for cell in col[1:]:
                if cell.value is not None and not isinstance(cell.value, (int, float)):
                    is_numeric = False
                    break
            
            if is_numeric and len(col) > 1:
                # Apply color scale
                color_scale_rule = ColorScaleRule(
                    start_type="min",
                    start_color=self._ui_elements["min_color"].value.replace("#", ""),
                    mid_type="percentile",
                    mid_value=50,
                    mid_color=self._ui_elements["mid_color"].value.replace("#", ""),
                    end_type="max",
                    end_color=self._ui_elements["max_color"].value.replace("#", "")
                )
                
                # Apply to column range
                sheet.conditional_formatting.add(
                    f"{col_letter}2:{col_letter}{len(col)}",
                    color_scale_rule
                )

    def _bold_headers(self, sheet):
        """Makes header rows bold"""
        for row in sheet.iter_rows(min_row=1, max_row=1):
            for cell in row:
                if cell.value:
                    cell.font = Font(bold=True)
        
        # Also bold section headers
        for row in sheet.iter_rows():
            if row[0].value in ["SPOT DATA", "DATA STATISTICS", "GENERAL PARAMETERS"]:
                for cell in row:
                    cell.font = Font(bold=True, size=12)

    def _autofit_columns(self, sheet):
        """Auto-fits column widths"""
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width

    def _get_sheet_name(self, dataset: Dataset, index: int) -> str:
        """Generates a valid sheet name for a dataset"""
        if dataset.metadata and dataset.metadata.name:
            name = dataset.metadata.name
        else:
            name = f"Dataset_{index + 1}"
        
        # Excel sheet name limitations
        invalid_chars = ["\\", "/", "*", "[", "]", ":", "?"]
        for char in invalid_chars:
            name = name.replace(char, "_")
        
        # Limit length to 31 characters
        if len(name) > 31:
            name = name[:28] + "..."
        
        return name

    def _format_field_name(self, field: str) -> str:
        """Formats field names for display"""
        return field.replace("_", " ").title()

    def _update_config_from_ui(self):
        """Updates the configuration from UI elements"""
        # Sheet mode
        self._export_config["sheet_mode"] = "single" if self._ui_elements["sheet_mode"][0].value else "multiple"
        
        # Data types
        self._export_config["data_types"]["spots"] = self._ui_elements["export_spots"].value
        self._export_config["data_types"]["statistics"] = self._ui_elements["export_statistics"].value
        self._export_config["data_types"]["parameters"] = self._ui_elements["export_parameters"].value
        
        # Field selections
        for field in self._export_config["spot_fields"]:
            self._export_config["spot_fields"][field] = self._ui_elements[f"spot_{field}"].value
        
        for field in self._export_config["statistics_fields"]:
            self._export_config["statistics_fields"][field] = self._ui_elements[f"stats_{field}"].value
        
        for field in self._export_config["parameter_fields"]:
            self._export_config["parameter_fields"][field] = self._ui_elements[f"param_{field}"].value
        
        # Header config
        self._export_config["header_config"]["enabled"] = self._ui_elements["header_enabled"].value
        for field in self._export_config["header_config"]:
            if field != "enabled":
                self._export_config["header_config"][field] = self._ui_elements[f"header_{field}"].value
        
        # Formatting
        self._export_config["formatting"]["enabled"] = self._ui_elements["formatting_enabled"].value
        self._export_config["formatting"]["type"] = self._ui_elements["formatting_type"].value.lower().replace(" ", "_")

    def _generate_header_preview(self) -> str:
        """Generates a preview of the header"""
        preview = "<pre style="font-family: monospace; background: #f0f0f0; padding: 10px;">"
        preview += "Dataset Name: Example Dataset\n"
        preview += "Patient ID: PAT001\n"
        preview += "Measurement Date: 2025-01-15 14:30:00\n"
        preview += "Tags: control, baseline, study_A\n"
        preview += "Incubations: Antibody (1:1000); Buffer (1x)\n"
        preview += "</pre>"
        return preview

    def _update_header_preview(self, button):
        """Updates the header preview based on current settings"""
        self._update_config_from_ui()
        
        preview = "<pre style="font-family: monospace; background: #f0f0f0; padding: 10px;">"
        if self._export_config["header_config"]["enabled"]:
            if self._export_config["header_config"]["name"]:
                preview += "Dataset Name: Example Dataset\n"
            if self._export_config["header_config"]["pat_id"]:
                preview += "Patient ID: PAT001\n"
            if self._export_config["header_config"]["measure_date"]:
                preview += "Measurement Date: 2025-01-15 14:30:00\n"
            if self._export_config["header_config"]["tags"]:
                preview += "Tags: control, baseline, study_A\n"
            if self._export_config["header_config"]["incubations"]:
                preview += "Incubations: Antibody (1:1000); Buffer (1x)\n"
        else:
            preview += "Headers disabled"
        preview += "</pre>"
        
        self._ui_elements["header_preview"].children = [
            WidgetFactory.html_widget(preview)
        ]

    def _show_status(self, status_type: str, message: str):
        """Shows a status message"""
        if status_type == "success":
            status_widget = WidgetFactory.info_field_success([
                WidgetFactory.html_widget(message)
            ])
        elif status_type == "error":
            status_widget = WidgetFactory.info_field_error([
                WidgetFactory.html_widget(message)
            ])
        elif status_type == "warning":
            status_widget = WidgetFactory.info_field_warning([
                WidgetFactory.html_widget(message)
            ])
        else:
            status_widget = WidgetFactory.info_field_default([
                WidgetFactory.html_widget(message)
            ])
        
        self._ui_elements["status"].children = [status_widget]

    def _on_data_type_change(self, change):
        """Handles changes to data type checkboxes"""
        # Enable/disable corresponding field selections
        if change["owner"] == self._ui_elements["export_spots"]:
            enabled = change["new"]
            for field in self._export_config["spot_fields"]:
                self._ui_elements[f"spot_{field}"].disabled = not enabled
        
        elif change["owner"] == self._ui_elements["export_statistics"]:
            enabled = change["new"]
            for field in self._export_config["statistics_fields"]:
                self._ui_elements[f"stats_{field}"].disabled = not enabled
        
        elif change["owner"] == self._ui_elements["export_parameters"]:
            enabled = change["new"]
            for field in self._export_config["parameter_fields"]:
                self._ui_elements[f"param_{field}"].disabled = not enabled

    def _on_formatting_change(self, change):
        """Handles changes to formatting enabled checkbox"""
        enabled = change["new"]
        self._ui_elements["formatting_type"].disabled = not enabled
        self._ui_elements["min_color"].disabled = not enabled
        self._ui_elements["mid_color"].disabled = not enabled
        self._ui_elements["max_color"].disabled = not enabled
        self._ui_elements["bold_headers"].disabled = not enabled
        self._ui_elements["autofit_columns"].disabled = not enabled
        self._ui_elements["freeze_headers"].disabled = not enabled

    def _on_header_change(self, change):
        """Handles changes to header enabled checkbox"""
        enabled = change["new"]
        for field in self._export_config["header_config"]:
            if field != "enabled":
                self._ui_elements[f"header_{field}"].disabled = not enabled

    def update_scheme(self, new_scheme) -> Optional[Self]:
        """Theme update (not implemented)"""
        return None

    def reset_module(self) -> Optional[Self]:
        """Reset module"""
        return ExcelExportModule()