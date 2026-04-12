import ipywidgets as widgets
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from typing import Dict, List, Optional, Union, Any, Callable
from typing_extensions import Self
import io
import os
from tkinter import filedialog, Tk
import numpy as np
import logging
import csv
import math
from PIL import Image
import svgutils.transform as sg
import tempfile
import time
import warnings

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.viability_rules import no_datasets_selected, has_negative_values
from suplex_modules.submodules.value_extractor import (
    ValueExtractor,
    extract_value_list_from_dataset,
    get_flat_value_list,
    flatten_list,
    get_reference_statistics,
)
from suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
    NORMALIZATION,
    DATASET_LABEL,
    NORMALIZATION_DEFAULT,
    NORMALIZATION_REFERENCE_POINT,
    COLLAGE_LAYOUT,
    SCALE_OPTION,
    COLOR,
    TITLE_POSITION,
    READING_ORDER,
)
from suplex_modules.submodules.dataset_sorter import DatasetSorter
from suplex_modules.submodules.dataset_filters import DatasetFilter
from suplex_modules.submodules.sample_spot_filter import (
    SampleSpotFilter,
    get_normalization_factors,
)
from suplex_modules.submodules.collage import (
    Collage,
    add_title_to_svg,
    add_padding_to_svgs,
)

from suplex_modules.submodules.settings.general_graph_settings import (
    GeneralGraphSettings,
)

from suplex_modules.submodules.settings.heatmap_settings import HeatmapSettings
from suplex_modules.submodules.settings.submodule_settings_constants import (
    OPTION_INSET,
    DIVERGENT_COLOR_SCHEME,
    ANNOTATION_COLOR,
    LINE_COLOR,
    CBAR_ORIENTATION,
)

from suplex_modules.submodules.settings.submodule_settings_constants import (
    SEQUENTIAL_COLOR_SCHEME,
    SCALE_TYPE,
    GRID_STYLE,
    JITTER_TYPE,
    WHISKER_MODE,
    OPTION_INSET,
    OPTION_WIDGETS_MAX_WIDTH,
    ASPECT_RATIO,
    CBAR_ORIENTATION,
    CBAR_TICK_MODE,
    get_aspect_ratio_value,
)

from suplex_modules.submodules.submodule_utils import (
    number_to_letters,
    calculate_step_size,
)

logger = logging.getLogger(__name__)

MAX_PIXELS_GRAPH = 2**20


class OverviewHeatmapModule(SuplexModuleInterface):

    def __init__(self):
        """
        Initialize the OverviewHeatmapModule with default settings and UI elements.
        """
        logger.debug("Initializing OverviewHeatmapModule")
        self._datasets = []
        self._color_scheme = None

        self._sorted_datasets = []
        self._included_datasets = []
        self._excluded_datasets = []
        self._sample_threshold_map = {}
        self._spot_threshold_map = {}
        self._filtered_values = {}
        self._unfiltered_values = {}

        self._DEFAULT_HOVER_TEXT = (
            "Generates an overview heatmap of all dataset values."
        )
        self._module_hover_text = self._DEFAULT_HOVER_TEXT

        # UI Elements
        self._value_extractor = None
        self._tabs = None

        self._dataset_sorter = None
        self._dataset_filter = None
        self._sample_spot_filter = None

        self._descriptor_radio = None
        self._dataset_descriptor = DATASET_LABEL.ID

        # Updatable boxes which contain our content
        self._plot_box = WidgetFactory.vbox(
            children=[],
            width="100%",
            height="100%",
            layout=widgets.Layout(padding="10px"),
        )
        self._overview_box = WidgetFactory.vbox(
            children=[],
            width="100%",
            height="100%",
            layout=widgets.Layout(padding="10px"),
        )
        self._dataset_stats_box = WidgetFactory.vbox(
            children=[],
            width="100%",
            height="100%",
            layout=widgets.Layout(padding="10px"),
        )

        # Flag which allows to change widgets programmatically
        self._ignore_events = False
        self._scale_col_bar_globally = False
        logger.debug("OverviewHeatmapModule initialized successfully")

    @property
    def module_name(self) -> str:
        """
        Get the name of the module.

        Returns:
            str: The module name.
        """
        return "Heatmap Collage"

    @property
    def module_version(self) -> str:
        """
        Get the version of the module.

        Returns:
            str: The module version.
        """
        return "0.2.0"

    @property
    def group_name(self) -> str:
        """
        Get the group name of the module.

        Returns:
            str: The group name.
        """
        return "Vanilla"

    @property
    def button_style(self) -> Dict[str, str]:
        """
        Get the style configuration for the module button.

        Returns:
            Dict[str, str]: Dictionary containing button style properties.
        """
        return {"font_color": "#FFFFFF", "button_color": "#ED9121", "button_icon": "🗺️"}

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        """
        Check if module can work with provided datasets.

        Args:
            datasets (List[Dataset]): List of datasets to check viability against.

        Returns:
            bool: True if viable, False otherwise.
        """
        logger.debug("Checking viability of module: %s", self.module_name)

        if no_datasets_selected(datasets):
            self._module_hover_text = f"Cannot initiate {self.module_name} since no datasets have been selected."
            logger.info(
                "The module %s has been disabled, since no datasets have been selected.",
                self.module_name,
            )
            return False

        if has_negative_values(datasets):
            self._module_hover_text = f"Cannot initiate {self.module_name} since datasets contain a negative value."
            logger.info(
                "The module %s has been disabled, since datasets contain a negative value.",
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

    def initiate_module(
        self, datasets: List[Dataset], color_scheme: Any
    ) -> widgets.Box:
        """
        Initialize module with datasets.

        Args:
            datasets (List[Dataset]): List of datasets to initialize with.
            color_scheme (Any): Color scheme to use.

        Returns:
            widgets.Box: The module UI widget.
        """
        logger.debug(
            "Initiating module %s with %d datasets", self.module_name, len(datasets)
        )
        try:

            self._datasets = datasets
            self._included_datasets = datasets.copy()
            self._color_scheme = color_scheme

            max_samples_per_dataset = 1  # Default
            # Max samples since we generate split heatmaps per spotfield instead of combined ones
            if self._datasets:
                max_samples_per_dataset = max(
                    len(dataset.samples) for dataset in self._datasets
                )

            self._general_graph_settings = GeneralGraphSettings(
                swap_axes=False,
                invert_x_axis=False,
                invert_y_axis=False,
                show_grid=True,
                show_title=True,
                show_axis_ticks=True,
                include_empty_datasets=False,
                sequential_color_scheme=SEQUENTIAL_COLOR_SCHEME.GREYS,
                divergent_color_scheme=DIVERGENT_COLOR_SCHEME.COOLWARM,
                base_font_size=20,
                aspect_ratio=ASPECT_RATIO.AUTO,
                grid_style=GRID_STYLE.TICKS,
                transparency=0.0,
                dpi=300,
                min_index=0,
                max_index=max_samples_per_dataset,
            )

            highlight_colors = list(ANNOTATION_COLOR)
            highlight_colors.remove(ANNOTATION_COLOR.AUTO)
            highlight_colors.remove(ANNOTATION_COLOR.BLACK)
            highlight_colors.remove(ANNOTATION_COLOR.WHITE)

            self._heatmap_settings = HeatmapSettings(
                square=False,
                symmetric_scaling=True,
                annot=False,
                annot_fontsize=1,
                annot_digits=0,
                annot_color=ANNOTATION_COLOR.AUTO,
                linewidths=0,
                cell_size=0.4,
                linecolor=LINE_COLOR.BLACK,
                robust=False,
                cbar_options=list(CBAR_ORIENTATION),
                cbar_tick_options=list(CBAR_TICK_MODE),
                start_at_index_0=True,
                highlight_reference_points=True,
                highlight_colors=highlight_colors,
                use_letter_annotation_x=False,
                use_letter_annotation_y=False,
                col_labels="",
                row_labels="",
                use_custom_col_labels=False,
                use_custom_row_labels=False,
                n_cols=10,
            )

            # Automatically set to the highest number of cols across all datasets
            max_columns = max(
                dataset.general_parameters.columns_per_spotfield
                for dataset in self._datasets
                if dataset.general_parameters.columns_per_spotfield is not None
            )
            self._heatmap_settings.get_n_cols_widget().value = max_columns

            # Uses golden ratio for pretty init grid
            dataset_cols_init_val = int((len(self._datasets) * 1.618) ** 0.5)

            title_colors = list(COLOR)
            title_colors.remove(COLOR.NONE)
            # initialize collage with all options set to true
            self._collage = Collage(
                layouts=list(COLLAGE_LAYOUT),
                columns=dataset_cols_init_val,
                max_columns=len(self._datasets),
                scaling=list(SCALE_OPTION),
                padding_horizontal=10,
                max_padding_horizontal=100,
                padding_vertical=10,
                max_padding_vertical=100,
                margin_vertical=10,
                max_margin_vertical=100,
                margin_horizontal=10,
                max_margin_horizontal=100,
                title="",
                title_positions=list(TITLE_POSITION),
                title_colors=title_colors,
                font_size=50,
                max_font_size=200,
                reading_orders=list(READING_ORDER),
                show_all_options=True,
            )

            all_tags = set()
            for dataset in self._datasets:
                all_tags.update(dataset.tags + dataset.suplex_tags)
            all_tags = sorted(list(all_tags))

            # Initialize DatasetSorter with all options and collected tags
            self._dataset_sorter = DatasetSorter(
                tags=all_tags, num_levels=1, max_num_levels=10
            )
            attributes = (
                DATA_ATTRIBUTES
                + DATA_STATISTICS_ATTRIBUTES
                + [
                    DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
                    DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
                ]
            )

            self._dataset_filter = DatasetFilter(
                included_attributes=attributes,
                default_threshold=1.0,  # per default nothing will be filtered
            )
            self._sample_spot_filter = SampleSpotFilter(
                included_attributes=attributes,
                included_normalization_methods=NORMALIZATION_DEFAULT,
            )
            # Sets up slider dimensions
            self._sample_spot_filter.on_filter_params_changed(self._datasets)

            self._sample_threshold_map = (
                self._sample_spot_filter.get_default_sample_map(self._included_datasets)
            )
            self._spot_threshold_map = self._sample_spot_filter.get_default_spot_map(
                self._included_datasets
            )

            normalization_methods = list(NORMALIZATION)
            normalization_methods.remove(NORMALIZATION.CUSTOM)
            max_index = max(
                sum(len(sample.spots) for sample in dataset.samples)
                for dataset in self._datasets
            )
            self._value_extractor = ValueExtractor(
                attributes=attributes,
                normalization_methods=normalization_methods,
                max_reference_index=max_index,
            )
            self._value_extractor.get_attribute_widget().value = DATASET_ATTRIBUTE.ADJUSTED_AVERAGE.value

            def on_values_extracted_changed():
                self._ignore_events = True
                self._dataset_filter.on_filter_changed(datasets=self._datasets)
                self._ignore_events = False
                self.auto_update(self.update_analysis)

            for widget in self._value_extractor.get_active_widgets():
                widget.observe(lambda b: on_values_extracted_changed(), names="value")

            self._value_extractor.get_reference_selector().get_ref_container().observe(
                lambda b: self.auto_update(self.update_analysis), names="children"
            )

            controls = self.create_main_control_interface()
            sort_filter_content = self.create_sort_filter_tab()
            settings_content = self.create_settings_tab()

            # Generate content for each tab
            # Initial content will be set via update methods
            overview_tab = WidgetFactory.vbox(
                children=[self._overview_box],
                layout=widgets.Layout(width="100%", height="auto", overflow="auto"),
            )
            dataset_stats_tab = WidgetFactory.vbox(
                children=[self._dataset_stats_box],
                layout=widgets.Layout(width="100%", height="auto", overflow="auto"),
            )
            graph_tab = WidgetFactory.vbox(
                children=[self._plot_box],
                layout=widgets.Layout(width="100%", height="auto", overflow="auto"),
            )
            sort_filter_tab = WidgetFactory.vbox(
                children=[sort_filter_content],
                layout=widgets.Layout(width="100%", height="auto", overflow="auto"),
            )
            settings_tab = WidgetFactory.vbox(
                children=[settings_content],
                layout=widgets.Layout(width="100%", height="auto", overflow="auto"),
            )

            self._tabs = WidgetFactory.tab(
                children=[
                    overview_tab,
                    dataset_stats_tab,
                    graph_tab,
                    sort_filter_tab,
                    settings_tab,
                ],
                titles=[
                    "Overview",
                    "Dataset Statistics",
                    "Graph",
                    "Sorting & Filters",
                    "Settings",
                ],
                layout=widgets.Layout(
                    width="100%",
                    height="100%",
                    overflow="auto",
                    padding="5px",
                    margin="0px",
                ),
            )

            def on_tab_change(change):
                """
                Update graph only when changing to Graph tab
                """
                current_tab_index = change["new"]
                current_tab_title = self._tabs.titles[current_tab_index]

                ignore_tabs = ["Sorting & Filters", "Settings"]
                if not current_tab_title in ignore_tabs:
                    self.auto_update(self.update_analysis)

            self._tabs.observe(on_tab_change, names="selected_index")

            # Main layout: controls on left, tabs on right
            module_ui = WidgetFactory.hbox(
                [controls, self._tabs],
                layout=widgets.Layout(
                    height="100%", width="100%", gap="0px", overflow="hidden"
                ),
            )

            logger.debug("Module UI initialized successfully")
            self.update_analysis()
            return module_ui

        except Exception as e:
            logger.error("Failed to initiate module: %s", e, exc_info=True)
            raise

    def create_main_control_interface(self) -> widgets.Widget:
        """
        Create the main control panel.

        Returns:
            widgets.Widget: The main control interface widget.
        """
        logger.debug("Creating main control interface")
        try:
            title_html = WidgetFactory.html_widget(
                value="<h2>Heatmap Collage</h2>", width="auto"
            )
            controls_box = WidgetFactory.vbox(
                children=[
                    self._value_extractor.get_ui(),
                    self.create_collage_controls_section(),
                ],
                layout=widgets.Layout(
                    height="100%",
                    width="100%",
                )
            )

            controls_content = WidgetFactory.vbox(
                children=[
                    controls_box,
                    self.create_control_button_section(),
                ],
                layout=widgets.Layout(
                    height="100%",
                    width="100%",
                    justify_content="space-between",
                    padding="0px 10px",
                ),
            )

            control_interface = WidgetFactory.vbox(
                children=[title_html, controls_content],
                layout=widgets.Layout(width="400px", height="100%", padding="5px"),
            )
            logger.debug("Main control interface created successfully")
            return control_interface
        except Exception as e:
            logger.error(
                "Failed to create main control interface: %s", e, exc_info=True
            )
            raise

    def create_collage_controls_section(self) -> widgets.Widget:
        """
        Create the collage controls section widget with nested layout.

        Returns:
            widgets.Widget: The VBox widget containing all collage control options.
        """
        try:
            logger.debug("Creating collage controls section")

            # List to collect all top-level widgets
            collage_widgets = []

            self._add_heatmaps_checkbox = WidgetFactory.checkbox(
                value=True,
                description="Add Heatmaps",
                indent=False,
                layout=widgets.Layout(
                    height="30px", width="auto", margin="0px", padding="0px"
                ),
            )
            self._add_heatmaps_checkbox.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )

            self._add_annotated_images_checkbox = WidgetFactory.checkbox(
                value=False,
                description="Add Annotated Images",
                indent=False,
                layout=widgets.Layout(
                    height="30px", width="auto", margin="0px", padding="0px"
                ),
                on_change=lambda b: self.auto_update(self.update_analysis),
                names="value",
            )
            self._add_annotated_images_checkbox.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )

            self._add_full_images_checkbox = WidgetFactory.checkbox(
                value=False,
                description="Add Full Images",
                indent=False,
                layout=widgets.Layout(
                    height="30px", width="auto", margin="0px", padding="0px"
                ),
            )
            self._add_full_images_checkbox.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )
            h_checkbox_container = WidgetFactory.hbox(
                children=[
                    self._add_heatmaps_checkbox,
                    self._add_full_images_checkbox,
                ],
                overflow="visible",
                height="auto"
            )
            
            checkbox_container = WidgetFactory.vbox(
                children=[
                    h_checkbox_container,
                    self._add_annotated_images_checkbox
                ],
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            collage_widgets.append(checkbox_container)

            max_dataset_cols = max_columns = max(
                dataset.general_parameters.number_of_spotfields
                for dataset in self._datasets
                if dataset.general_parameters.number_of_spotfields is not None
            )

            # Plus two since we allow users to add annotated and full images
            dataset_cols_init_val = int(
                math.ceil(math.sqrt(max_columns))
            )  # try to make a square
            max_dataset_cols += 2

            heatmap_cols_label = WidgetFactory.label("Cols per Heatmap:")
            heatmap_cols_number_input = self._heatmap_settings.get_n_cols_widget()
            heatmap_cols_number_input.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )

            dataset_cols_label = WidgetFactory.label("Cols per Dataset:")
            self._dataset_cols_number_input = WidgetFactory.int_number_input(
                value=dataset_cols_init_val,
                min_value=1,
                max_value=max_dataset_cols,
                description="",
                layout=widgets.Layout(
                    height="30px", width="100%", margin="0px", padding="0px"
                ),
            )
            self._dataset_cols_number_input.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )

            collage_cols_label = WidgetFactory.label("Cols in Collage:")
            collage_cols_number_input = self._collage.get_columns_input()
            collage_cols_number_input.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )

            # Create individual containers
            collage_cols_container = WidgetFactory.vbox(
                children=[
                    collage_cols_label,
                    WidgetFactory.vbox(
                        children=[collage_cols_number_input],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )

            dataset_cols_container = WidgetFactory.vbox(
                children=[
                    dataset_cols_label,
                    WidgetFactory.vbox(
                        children=[self._dataset_cols_number_input],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )

            heatmap_cols_container = WidgetFactory.vbox(
                children=[
                    heatmap_cols_label,
                    WidgetFactory.vbox(
                        children=[heatmap_cols_number_input],
                        gap="5px",
                        overflow="visible",
                        height="auto",
                        layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
                    ),
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )

            # Create HBox with collage and dataset columns side by side
            top_row_hbox = WidgetFactory.hbox(
                children=[collage_cols_container, dataset_cols_container],
                gap="10px",
                overflow="visible",
                layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
            )

            # Add containers to collage_widgets
            collage_widgets.append(top_row_hbox)
            collage_widgets.append(heatmap_cols_container)

            # Create the main container
            collage_controls_section = WidgetFactory.vbox(
                children=collage_widgets, gap="5px", overflow="visible", height="auto"
            )

            logger.debug("Collage controls section created successfully")
            return collage_controls_section

        except Exception as e:
            logger.error(
                "Failed to create collage controls section: %s", e, exc_info=True
            )
            raise

    def create_control_button_section(self):
        """
        Create the control buttons section UI.

        Returns:
            widgets.Widget: The control button section widget.
        """
        logger.debug("Creating control button section")
        try:
            export_plot_button = WidgetFactory.button_emphasis(
                "Export Plot",
                on_click=lambda b: self.on_export_plot(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height = "30px"
            )

            export_as_tsv_button = WidgetFactory.button_emphasis(
                "Export CSV",
                on_click=lambda b: self.on_export_csv(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height = "30px"
            )

            update_button = WidgetFactory.button_success(
                "Apply Changes",
                on_click=lambda b: self.update_analysis(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height = "30px"
            )

            self._auto_update_checkbox = WidgetFactory.checkbox(
                value=False,
                description="Auto",
                indent=False,
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height = "30px"
            )
            self._auto_update_checkbox.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )

            first_col = WidgetFactory.vbox(
                children=[export_plot_button, update_button],
                height="100%",
                width="100%",
                overflow_y="visible",
                gap="5px",
            )

            second_col = WidgetFactory.vbox(
                children=[export_as_tsv_button, self._auto_update_checkbox],
                height="100%",
                width="100%",
                overflow_y="visible",
                gap="5px",
            )

            control_button_section = WidgetFactory.hbox(
                children=[first_col, second_col],
                height="80px",
                width="100%",
                overflow_y="visible",
                gap="5px",
            )

            logger.debug("Control button section created successfully")
            return control_button_section
        except Exception as e:
            logger.error(
                "Failed to create control button section: %s", e, exc_info=True
            )
            raise

    def create_sort_filter_tab(self) -> widgets.Widget:
        """
        Create filter tab with widgets to alter modes for dataset filter and threshold filter.
        As we place the sliders in controls we cannot use get_ui for either the dataset_filter nor the spot_filter.

        Returns:
            widgets.Widget: The sort and filter tab widget.
        """

        dataset_sorter_ui = self._dataset_sorter.get_ui()
        dataset_filter_ui = self._dataset_filter.get_ui()
        sample_spot_filter_ui = self._sample_spot_filter.get_ui()

        self._sample_spot_filter.get_attribute_dropdown().observe(
            lambda b: self._sample_spot_filter.on_filter_params_changed(
                datasets=self._datasets
            ),
            names="value",
        )
        self._sample_spot_filter.get_normalization_dropdown().observe(
            lambda b: self._sample_spot_filter.on_filter_params_changed(
                datasets=self._datasets
            ),
            names="value",
        )
        self._sample_spot_filter.get_normalization_factor_input().observe(
            lambda b: self._sample_spot_filter.on_filter_params_changed(
                datasets=self._datasets
            ),
            names="value",
        )

        filter_tab = WidgetFactory.vbox(
            children=[dataset_sorter_ui, dataset_filter_ui, sample_spot_filter_ui],
            layout=widgets.Layout(
                padding="10px",
                height="100%",
                width="100%",
                max_width=OPTION_WIDGETS_MAX_WIDTH,
            ),
            gap="50px",
        )
        return filter_tab

    def create_settings_tab(self) -> widgets.Widget:
        """
        Create the settings tab with plot options and graph settings.

        Returns:
            widgets.Widget: The settings tab widget.
        """
        logger.debug("Initiating creation of settings tab")

        dataset_box_title = WidgetFactory.html_widget(value="<h3>Dataset Options</h3>")
        radio_label = WidgetFactory.label(value="Descriptor")

        self._descriptor_radio = WidgetFactory.custom_radio_buttons(
            number=2,
            description=[DATASET_LABEL.ID.value, DATASET_LABEL.NAME.value],
            i_toggled=0,
            width="100%",
            height="30px",
        )

        def on_change_descriptor(new_descriptor: DATASET_LABEL):
            self._dataset_descriptor = new_descriptor
            self.auto_update(self.update_analysis)

        self._descriptor_radio[0].on_click(
            lambda b: on_change_descriptor(DATASET_LABEL.ID)
        )
        self._descriptor_radio[1].on_click(
            lambda b: on_change_descriptor(DATASET_LABEL.NAME)
        )

        radio_button_box = WidgetFactory.hbox(
            children=self._descriptor_radio,
            width="300px",
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )
        radio_box = WidgetFactory.vbox(
            children=[radio_label, radio_button_box],
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )

        dataset_names_box = WidgetFactory.vbox(
            children=[dataset_box_title, radio_box], layout=widgets.Layout(gap="10px")
        )

        settings_tab = WidgetFactory.vbox(
            children=[
                dataset_names_box,
                self._collage.get_ui(),
                self._heatmap_settings.get_ui(),
                self._general_graph_settings.get_ui(),
            ],
            layout=widgets.Layout(padding="10px", max_width=OPTION_WIDGETS_MAX_WIDTH),
            gap="10px",
        )

        logger.debug("Settings tab created successfully")
        return settings_tab

    def auto_update(self, method: Callable[[], None]) -> None:
        """
        Automatically update the analysis if auto-update is enabled.

        Args:
            method: The method to call for updating.
        """
        if self._auto_update_checkbox.value:
            method()

    def update_analysis(self):
        """
        Update overview, statistics, and graph.
        """
        logger.debug("Updating analysis")
        self.apply_all_filters()
        self.update_overview()
        self.update_dataset_statistics()
        self.update_graph()

    def apply_all_filters(self):
        """
        Apply all filters and update analysis.
        """
        logger.debug("Applying all filters")
        if self._ignore_events:
            return
        self._sorted_datasets = self._dataset_sorter.get_sorted_datasets(self._datasets)
        self.apply_dataset_filter()

        self.apply_value_filter()
        # We normalize after we filter!
        self.normalize_values()

    def apply_dataset_filter(self):
        """
        Apply dataset filter to sorted datasets.
        """
        logger.debug("Applying dataset filter")
        self._included_datasets, self._excluded_datasets = (
            self._dataset_filter.get_filtered_datasets(datasets=self._sorted_datasets)
        )

    def apply_value_filter(self):
        """
        Apply value filter to datasets.
        """
        logger.debug("Applying value filter")
        attribute = self._value_extractor.attribute
        normalization_method = self._value_extractor.normalization

        datasets = self._included_datasets

        self._sample_threshold_map, self._spot_threshold_map = (
            self._sample_spot_filter.get_filter_maps(datasets=datasets)
        )

        self._filtered_values = (
            self._sample_spot_filter.extract_filtered_values_from_datasets(
                datasets=datasets,
                attribute=attribute,
                sample_threshold_map=self._sample_threshold_map,
                spot_threshold_map=self._spot_threshold_map,
                outside_replacement_value=float("nan"),
            )
        )

        self._unfiltered_values = (
            self._sample_spot_filter.extract_filtered_values_from_datasets(
                datasets=datasets,
                attribute=attribute,
                outside_replacement_value=float("nan"),
            )
        )

    def normalize_values(self):
        """
        Normalize filtered and unfiltered values.
        """
        logger.debug("Normalizing values")

        self._filtered_values = self._value_extractor.normalize_values(
            value_lists=self._filtered_values
        )

        self._unfiltered_values = self._value_extractor.normalize_values(
            value_lists=self._unfiltered_values
        )

    def update_overview(self) -> None:
        """
        Update overview analysis content.
        """
        logger.debug("Updating overview analysis")
        try:
            attribute = self._value_extractor.attribute
            normalization = self._value_extractor.normalization

            norm_text = f"({normalization.value})"
            if normalization != NORMALIZATION.RAW:
                norm_text = "Normalized " + norm_text

            base_dataset_values = [
                get_flat_value_list(dataset=dataset, attribute=attribute)
                for dataset in self._datasets
            ]
            base_dataset_values_flat = flatten_list(nested_list=base_dataset_values)
            base_mean = np.nanmean(base_dataset_values_flat)
            base_min = np.nanmin(base_dataset_values_flat)
            base_max = np.nanmax(base_dataset_values_flat)

            html_content = f"""
            <h2>Overview: {attribute.value} {norm_text}</h2>
        
            <h3>Overall Statistics</h3>
            <ul>
                <li><strong>nSets:</strong> {len(self._datasets)}</li>
                <li><strong>Total Number of Values:</strong> {len(base_dataset_values_flat)}</li>
                <li><strong>Global Mean:</strong> {base_mean:.4f}</li>
                <li><strong>Global Min:</strong> {base_min:.4f}</li>
                <li><strong>Global Max:</strong> {base_max:.4f}</li>
            </ul>
            """

            dataset_filter_method = self._dataset_filter.method

            dataset_filter_title = "Dataset Filter"
            dataset_filter_title += f": {dataset_filter_method.value}"

            dataset_filter_attribute_text = self._dataset_filter.attribute.value

            excluded_set_identifiers = (
                ", ".join(
                    [
                        (
                            dataset.id
                            if self._dataset_descriptor == DATASET_LABEL.ID
                            else dataset.name
                        )
                        for dataset in self._excluded_datasets
                    ]
                )
                if self._excluded_datasets
                else "None"
            )

            html_content += f"""
            <h3>{dataset_filter_title}</h3>
            <ul>
                <li><strong>Attribute:</strong> {dataset_filter_attribute_text}</li>
                <li><strong>Threshold:</strong> {self._dataset_filter.threshold}</li>
                <li><strong>Inverted Selection:</strong> {self._dataset_filter.invert}</li>
                <li><strong>Number of Excluded  Sets:</strong> {len(self._excluded_datasets)} / {len(self._datasets)} ({len(self._excluded_datasets)/len(self._datasets)*100:.1f}%)</li>
                <li><strong>Excluded Sets:</strong> {excluded_set_identifiers}</li>
            </ul>
            """

            value_threshold_title = "Value Threshold"
            if not self._included_datasets:
                html_content += f"<h3>{value_threshold_title}</h3>"
                html_content += "<ul><li><strong>No Values Left for Value Filtering</strong></li></ul>"
                self._overview_box.children = [WidgetFactory.html_widget(html_content)]
                return

            value_filter_attribute_text = (
                self._sample_spot_filter.get_attribute_dropdown().value
            )

            value_filter_normalization_text = (
                self._sample_spot_filter.get_normalization_dropdown().value
            )

            threshold_min, threshold_max = (
                self._sample_spot_filter.get_threshold_range_slider().value
            )

            flat_flag_list = []
            if attribute in DATA_STATISTICS_ATTRIBUTES:
                flat_flag_list = [
                    self._sample_spot_filter.is_flag_in_selected_range(item)
                    for sublist in self._sample_threshold_map.values()
                    for item in sublist
                ]
            else:
                flat_flag_list = [
                    self._sample_spot_filter.is_flag_in_selected_range(item)
                    for outer_list in self._spot_threshold_map.values()
                    for sublist in outer_list
                    for item in sublist
                ]

            n_values_included = np.nansum(flat_flag_list)

            filtered_values_flat = [
                item for sublist in self._filtered_values.values() for item in sublist
            ]
            filtered_values_mean = (
                np.nanmean(filtered_values_flat) if filtered_values_flat else 0.0
            )
            filtered_values_min = (
                np.nanmin(filtered_values_flat) if filtered_values_flat else 0.0
            )
            filtered_values_max = (
                np.nanmax(filtered_values_flat) if filtered_values_flat else 0.0
            )

            html_content += f"""
            <h3>{value_threshold_title}</h3>
            <ul>
                <li><strong>Attribute:</strong> {value_filter_attribute_text}</li>
                <li><strong>Normalization:</strong> {value_filter_normalization_text}</li>
                <li><strong>Range:</strong> {threshold_min} - {threshold_max}</li>
                <li><strong>Inverted Selection:</strong> {self._sample_spot_filter.invert}</li>
                <li><strong>Sample Filtering Affects Spots:</strong> {self._sample_spot_filter.sample_affects_spots}</li>
                <li><strong>Spot Filtering Affects Samples:</strong> {self._sample_spot_filter.spots_affect_sample}</li>
                <li><strong>Propagation Mode:</strong> {self._sample_spot_filter.sample_filter_mode.value}</li>
                <li><strong>Values in Range:</strong> {n_values_included} / {len(flat_flag_list)} ({n_values_included/len(flat_flag_list)*100:.1f}%)</li>
                <li><strong>Filtered Global Mean:</strong> {filtered_values_mean:.4f}</li>
                <li><strong>Filtered Global Min:</strong> {filtered_values_min:.4f}</li>
                <li><strong>Filtered Global Max:</strong> {filtered_values_max:.4f}</li>
            </ul>
            """

            logger.debug("Overview analysis updated successfully")
            self._overview_box.children = [WidgetFactory.html_widget(html_content)]
        except Exception as e:
            logger.error("Failed to update overview analysis: %s", e, exc_info=True)
            self._overview_box.children = [
                WidgetFactory.info_field_error(
                    [WidgetFactory.html_widget(f"Error generating overview: {str(e)}")]
                )
            ]

    def update_dataset_statistics(self) -> None:
        """
        Update the dataset statistics display based on current filtered values.
        """
        logger.debug("Updating dataset statistics")
        try:
            dataset_stats = []
            attribute = self._value_extractor.attribute
            normalization = self._value_extractor.normalization
            is_reference_norm = (
                normalization in NORMALIZATION_REFERENCE_POINT
                and len(self._value_extractor.references) > 0
            )

            for dataset in self._sorted_datasets:
                values = self._filtered_values.get(dataset, [])
                unfiltered_values = self._unfiltered_values.get(
                    dataset, []
                )  # For reference stats

                if not values:
                    continue

                n_values = len(values) - np.sum(np.isnan(values)) # no filtered values

                if attribute in DATA_STATISTICS_ATTRIBUTES:
                    n_values_total = len(dataset.samples)
                else:
                    n_values_total = sum(len(sample.spots) for sample in dataset.samples)
                
                perc_excluded = (
                    (1 - n_values / n_values_total) * 100 if n_values_total > 0 else 0
                )

                
                if values and not np.all(np.isnan(values)):
                    stat_mean = np.nanmean(values)
                    stat_median = np.nanmedian(values)
                    stat_min = np.nanmin(values)
                    stat_max = np.nanmax(values)
                    stat_std = np.nanstd(values)
                else:
                    stat_mean = np.nan
                    stat_median = np.nan
                    stat_min = np.nan
                    stat_max = np.nan
                    stat_std = np.nan

                name = (
                    dataset.id
                    if self._dataset_descriptor == DATASET_LABEL.ID
                    else dataset.name
                )

                stat = {
                    "name": name,
                    "n_values": n_values,
                    "n_values_total": n_values_total,
                    "perc_excluded": perc_excluded,
                    "mean": stat_mean,
                    "median": stat_median,
                    "min": stat_min,
                    "max": stat_max,
                    "std": stat_std,
                }

                # Add reference statistics if applicable
                if is_reference_norm:
                    ref_stats = get_reference_statistics(
                        unfiltered_values, self._value_extractor.references
                    )
                    stat["ref_n"] = ref_stats["n_reference_points"]
                    stat["ref_avg"] = ref_stats["avg"]
                    stat["ref_stdev"] = ref_stats["stdev"]
                    stat["ref_median"] = ref_stats["median"]
                    stat["ref_stdev_percent"] = ref_stats["stdev_percent"]

                dataset_stats.append(stat)

            if not dataset_stats:
                logger.debug("No data available for dataset statistics")
                self._dataset_stats_box.children = [
                    WidgetFactory.info_field_error(
                        [WidgetFactory.html_widget("No datasets available.")]
                    )
                ]
                return

            norm_text = f"({normalization.value})"
            if normalization != NORMALIZATION.RAW:
                norm_text = "Normalized " + norm_text

            head_col = self._color_scheme.LAYOUT_COLOR.TABLE.HEAD
            line_col = self._color_scheme.LAYOUT_COLOR.TABLE.LINES
            font_col_head = self._color_scheme.TEXT.COLOR.TABLE.HEAD
            font_col_body = self._color_scheme.TEXT.COLOR.TABLE.BODY

            html_content = f"<h3>Dataset Statistics: {attribute.value} {norm_text}</h3>"

            html_content += f"""
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: {head_col}; color: {font_col_head};">
                    <th style="padding: 8px; text-align: left; border: 1px solid {line_col};">Dataset</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">n Values</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Percent Excluded</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Mean</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Median</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Min</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Max</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Std Dev</th>
            """

            # Add reference headers only if reference normalization is active
            if is_reference_norm:
                html_content += f"""
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Ref n</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Ref Mean</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Ref Median</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Ref Std Dev</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Ref %Std Dev</th>
                """

            html_content += "</tr>"

            for stat in dataset_stats:
                html_content += f"""
                <tr style="color: {font_col_body};">
                    <td style="padding: 8px; border: 1px solid {line_col};">{stat["name"]}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["n_values"]} / {stat["n_values_total"]}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["perc_excluded"]:.2f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["mean"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["median"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["min"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["max"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["std"]:.4f}</td>
                """

                # Add reference cells only if reference normalization is active
                if is_reference_norm:
                    html_content += f"""
                        <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["ref_n"]}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["ref_avg"]:.4f}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["ref_median"]:.4f}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["ref_stdev"]:.4f}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["ref_stdev_percent"]:.2f}</td>
                    """

                html_content += "</tr>"

            html_content += "</table>"

            logger.debug("Dataset statistics updated successfully")
            self._dataset_stats_box.children = [WidgetFactory.html_widget(html_content)]
        except Exception as e:
            logger.error("Failed to update dataset statistics: %s", e, exc_info=True)
            self._dataset_stats_box.children = [
                WidgetFactory.info_field_error(
                    [WidgetFactory.html_widget("Error generating dataset statistics.")]
                )
            ]

    def update_graph(self) -> None:
        """
        Generate the intensity overview plot.
        """
        logger.debug("Generating heatmap collage")

        # Catches edge case: no references selected in reference point method
        if (
            self._value_extractor.normalization in NORMALIZATION_REFERENCE_POINT
            and len(self._value_extractor.references) == 0
        ):
            html_str = f"Please select reference indices to generate a plot."
            self._plot_box.children = [
                WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
            ]
            return

        try:
            value_lists = self.filter_empty_datasets(self._filtered_values)

            if not value_lists:
                logger.warning("No data available for plotting after filtering")
                self._plot_box.children = [
                    WidgetFactory.info_field_error(
                        [
                            WidgetFactory.html_widget(
                                "No data available for plotting after filtering."
                            )
                        ]
                    )
                ]
                return

            if (
                not self._add_heatmaps_checkbox.value
                and not self._add_annotated_images_checkbox.value
                and not self._add_full_images_checkbox.value
            ):
                self._plot_box.children = [
                    WidgetFactory.info_field_error(
                        [WidgetFactory.html_widget("No elements for collage selected.")]
                    )
                ]
                return

            svg_fig = self.get_collage(plot_data=value_lists)

            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_svg:
                svg_fig.save(tmp_svg.name)
                with open(tmp_svg.name, "r", encoding="utf-8") as f:
                    svg_string = f.read()

                # Extremely ugly solution for the way windows handles tempfiles
                for attempt in range(3):
                    try:
                        os.remove(tmp_svg.name)
                        break
                    except PermissionError:
                        if attempt < 2:
                            time.sleep(0.1)
                        else:
                            logger.debug(f"Could not remove temp file {tmp_svg.name}")

            html_content = f"""
            <div style="width: 100%; height: auto; overflow: visible; position: relative;">
                <div style="width: 100%; height: 0; padding-bottom: 75%; position: relative; overflow: visible;">
                    <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                         preserveAspectRatio="xMidYMid meet">
                        {svg_string}
                    </svg>
                </div>
            </div>
            """

            svg_width = float(svg_fig.width.rstrip("ptpx"))
            svg_height = float(svg_fig.height.rstrip("ptpx"))
            html_content = f"""
            <svg style="width: 100%; height: auto;" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
                {svg_string}
            </svg>
            """
            html_widget = WidgetFactory.html_widget(
                value=html_content, layout=widgets.Layout(width="100%", height="auto")
            )

            self._plot_box.children = [html_widget]

        except Exception as e:
            html_str = f"Error generating plot: {str(e)}"
            if "Image size" in str(e) and "too large" in str(e):
                html_str = "Could not generate plot, please reduce dimensions."
                logger.warning("Failed to generate plot: %s", e, exc_info=True)
            else:
                logger.error("Failed to generate plot: %s", e, exc_info=True)

            self._plot_box.children = [
                WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
            ]

    def on_export_plot(self):
        """
        Export the current plot using Tkinter save dialog.
        """
        if (
            self._value_extractor.normalization in NORMALIZATION_REFERENCE_POINT
            and len(self._value_extractor.references) == 0
        ):
            logger.info(
                "Could not export plot since no indices for export were selected."
            )
            return

        logger.debug("Exporting plot")
        try:
            value_lists = self.filter_empty_datasets(self._filtered_values)

            if not value_lists:
                logger.warning("No data available for export")
                return

            if (
                not self._add_heatmaps_checkbox.value
                and not self._add_annotated_images_checkbox.value
                and not self._add_full_images_checkbox.value
            ):
                # No collage elements -> no export
                return

            svg_fig = self.get_collage(plot_data=value_lists)
            default_filename = f"Heatmap_Collage_{self._value_extractor.attribute.value}_{self._value_extractor.normalization.value}.svg"

            root = Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            root.focus_force()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG files", "*.svg")],
                initialfile=default_filename,
                title="Save Plot As",
            )
            
            root.attributes('-topmost', False)
            root.destroy()
            
            if file_path:
                svg_fig.save(file_path)
                logger.info("Plot exported successfully to %s", file_path)
            else:
                logger.debug("Plot export cancelled by user")
        except Exception as e:
            if "Image size" in str(e) and "too large" in str(e):
                logger.warning("Failed to generate plot: %s", e, exc_info=True)
            logger.error("Failed to export plot: %s", e, exc_info=True)

    def filter_empty_datasets(self, value_lists: Dict[Dataset, List[float]]) -> Dict[Dataset, List[float]]:
        """
        Remove datasets that contain only NaN/None values when the user has disabled the inclusion of empty datasets.

        Args:
            value_lists (Dict[Dataset, List[float]]): Dictionary with datasets as keys
                and their (filtered) value lists as values.

        Returns:
            Dict[Dataset, List[float]]: The same dictionary with empty (all-NaN) datasets
                removed if include_empty_datasets is False.
        """
        if self._general_graph_settings.include_empty_datasets:
            return value_lists

        return {
            key: value_list
            for key, value_list in value_lists.items()
            if value_list
            and not all(
                val is None or (val is not None and np.isnan(val))
                for val in value_list
            )
        }

    def get_collage(self, plot_data: Dict[Dataset, List[float]]) -> sg.SVGFigure:
        """
        Generate a collage from individual dataset heatmaps and images.

        Args:
            plot_data (Dict[Dataset, List[float]]): Data for plotting.

        Returns:
            sg.SVGFigure: The generated collage SVG.
        """
        logger.debug("Generating collage from individual dataset heatmaps")

        # self._dataset_cols_number_input
        sub_collages = []
        for dataset, plot_values in plot_data.items():
            dataset_figures = []
            dataset_images = []

            if self._add_heatmaps_checkbox.value:
                dataset_figures += self.get_heatmaps(
                    dataset=dataset, plot_values=plot_values
                )

            annotated_image_path = dataset.path_holder.annotated_image_path
            if self._add_annotated_images_checkbox.value and annotated_image_path:
                try:
                    img = Image.open(annotated_image_path).convert("RGBA")
                    dataset_images.append(img)
                except Exception as e:
                    logger.warning(
                        f"Failed to load image from {annotated_image_path}: %s", e
                    )

            full_image_path = dataset.path_holder.image_path
            if self._add_full_images_checkbox.value and full_image_path:
                try:
                    img = Image.open(full_image_path)
                    # Convert I;16B to 8-bit grayscale before RGBA to ensure compatibility with collage.py's RGB/RGBA processing.
                    if img.mode == "I;16B":
                        img_array = np.array(img, dtype=np.uint16)
                        img_array = (img_array / 256).astype(np.uint8)
                        img = Image.fromarray(img_array, mode="L")
                    img = img.convert("RGBA")
                    dataset_images.append(img)
                except Exception as e:
                    logger.warning(
                        f"Failed to load image from {full_image_path}: %s", e
                    )

            title = ""
            if self._general_graph_settings.show_title:
                title = (
                    dataset.id
                    if self._dataset_descriptor == DATASET_LABEL.ID
                    else dataset.name
                )

            # We use constant values for the sub-collages, maybe we'll make this interactive in a future version
            # Commented attributes default to the same setting as the overarching collage
            sub_title_size = max(
                1, int(self._collage.font_size * 0.618)
            )  # Golden ratio

            sub_collages.append(
                self._collage.generate_collage(
                    images=dataset_figures + dataset_images,
                    layout=COLLAGE_LAYOUT.GRID_EQUAL_ALL,
                    columns=self._dataset_cols_number_input.value,
                    scale_option=SCALE_OPTION.DOWNSCALE_TO_WIDTH,
                    padding_horizontal=10,
                    padding_vertical=10,
                    horizontal_margin=0,
                    vertical_margin=0,
                    title=title,
                    # title_position,
                    # title_color,
                    font_size=sub_title_size,
                    # reading_order,
                    dpi=self._general_graph_settings.dpi,
                )
            )
            for fig in dataset_figures:
                plt.close(fig)

        show_global_cbar = self._heatmap_settings.cbar_orientation in [
            CBAR_ORIENTATION.VERTICAL,
            CBAR_ORIENTATION.HORIZONTAL,
        ]
        show_global_cbar = (
            show_global_cbar
            and self._value_extractor.normalization
            not in [
                NORMALIZATION.RAW,
                NORMALIZATION.CUSTOM,
                NORMALIZATION.BY_POSITION,
                NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL,
            ]
        )

        title = ""  # remove title to allow centering with separatly added colbar
        vertical_margin = 0
        horizontal_margin = 0
        if not show_global_cbar:
            title = self._collage.title
            horizontal_margin = self._collage.horizontal_margin
            vertical_margin = self._collage.vertical_margin

        collage_image = self._collage.generate_collage(
            images=sub_collages,
            dpi=self._general_graph_settings.dpi,
            title=title,
            horizontal_margin=horizontal_margin,
            vertical_margin=vertical_margin,
        )

        if show_global_cbar:
            collage_image = self.add_global_colorbar(
                svg_image=collage_image, plot_data=plot_data
            )
            collage_image = add_title_to_svg(
                svg=collage_image,
                title=self._collage.title,
                title_position=self._collage.title_position,
                title_color=self._collage.title_color,
                font_size=self._collage.font_size,
            )
            collage_image = add_padding_to_svgs(
                [collage_image],
                horizontal_padding=self._collage.horizontal_margin,
                vertical_padding=self._collage.vertical_margin,
            )[0]

        logger.debug("Collage generated successfully")
        return collage_image

    def get_heatmaps(
        self, dataset: Dataset, plot_values: List[float]
    ) -> List[plt.Figure]:
        """
        Generate heatmaps for the dataset, splitting by spotfields if applicable.

        Args:
            dataset (Dataset): The dataset to generate heatmaps for.
            plot_values (List[float]): The values to plot.

        Returns:
            List[plt.Figure]: List of heatmap figures.
        """
        n_spotfields = dataset.general_parameters.number_of_spotfields
        if (
            n_spotfields <= 1
            or n_spotfields is None
            or self._value_extractor.attribute in DATA_STATISTICS_ATTRIBUTES
        ):
            return [self.generate_heatmap(dataset=dataset, plot_values=plot_values)]

        # Use extended slicing to extract spots in format [start:stop:step]
        spot_field_values_list = [
            plot_values[i::n_spotfields] for i in range(n_spotfields)
        ]
        return [
            self.generate_heatmap(dataset=dataset, plot_values=spot_field_values)
            for spot_field_values in spot_field_values_list
        ]

    def generate_heatmap(
        self, dataset: Dataset, plot_values: List[float]
    ) -> plt.Figure:
        """
        Generate a single heatmap for the given dataset and values.

        Args:
            dataset (Dataset): The dataset.
            plot_values (List[float]): The values to plot in the heatmap.

        Returns:
            plt.Figure: The generated heatmap figure.
        """
        logger.debug(f"Generating heatmap for dataset: %s", dataset.id)
        try:
            # Edge case where there is only one non NaN value
            if sum(~np.isnan(plot_values)) <= 1:
                #changes NaN to zero to allow scaling of heatmap
                plot_values = [0.0 if np.isnan(x) else x for x in plot_values]
                
            min_index = self._general_graph_settings.min_index
            max_index = self._general_graph_settings.max_index
            if min_index > max_index or min_index >= len(plot_values):
                logger.warning(
                    f"Could not apply index truncation to {dataset.id}. Number of values {len(plot_values)}, min_index {min_index}, max_index {max_index}."
                )
            else:
                max_index = min(max_index, len(plot_values) - 1)
                plot_values = plot_values[min_index : max_index + 1]
            
            # Structure into 2D array based on n_cols
            n_cols = self._heatmap_settings.n_cols
            n_values = len(plot_values)
            n_rows = (n_values + n_cols - 1) // n_cols
            # Pad with NaN to fill the grid
            padded_values = plot_values + [np.nan] * (n_rows * n_cols - n_values)
            data_2d = np.array(padded_values).reshape(n_rows, n_cols)

            # Handle swap axes
            if self._general_graph_settings.swap_axes:
                data_2d = data_2d.T
                # Swap n_rows and n_cols for further calculations
                n_rows, n_cols = n_cols, n_rows

            # Set up style and font sizes based on general settings
            sns.set_style(self._general_graph_settings.grid_style.value)
            base_font_size = self._general_graph_settings.base_font_size
            plt.rcParams.update(
                {
                    "font.size": base_font_size,
                }
            )

            # Calculate figure size
            width_per_col = self._heatmap_settings.cell_size
            height_per_row = self._heatmap_settings.cell_size
            left_margin = right_margin = bottom_margin = top_margin = 0.5
            fig_width = left_margin + right_margin + n_cols * width_per_col
            fig_height = bottom_margin + top_margin + n_rows * height_per_row

            ar_value = get_aspect_ratio_value(self._general_graph_settings.aspect_ratio)
            if ar_value is not None:
                fig_width = fig_height * ar_value  # Adjust width to match aspect ratio

            fig, ax = plt.subplots(figsize=(fig_width, fig_height))

            # Estimating size for dynamic downscaling
            current_dpi = fig.dpi
            est_width_pixels = fig_width * current_dpi
            est_height_pixels = fig_height * current_dpi

            if (est_width_pixels > MAX_PIXELS_GRAPH) or (
                est_height_pixels > MAX_PIXELS_GRAPH
            ):
                min_dpi_width = MAX_PIXELS_GRAPH / fig_width
                min_dpi_height = MAX_PIXELS_GRAPH / fig_height
                min_dpi = max(50, min(min_dpi_width, min_dpi_height))
                fig.set_dpi(min_dpi)
                logger.info(
                    f"Proactively reduced DPI to {min_dpi} (estimated pixels: {est_width_pixels:.0f}x{est_height_pixels:.0f}, figsize: {fig_width}x{fig_height}) to avoid size limit."
                )

            # Colorbar scaling and cmap setup
            vmin = None
            vmax = None
            center = None
            cmap = self._general_graph_settings.sequential_color_scheme.value

            normalization = self._value_extractor.normalization
            if normalization in NORMALIZATION_REFERENCE_POINT:
                cmap = self._general_graph_settings.divergent_color_scheme.value
                center = 0
                if normalization == NORMALIZATION.BY_POSITION:
                    center = 1
                if self._heatmap_settings.symmetric_scaling:
                    # Symmetric scaling around center
                    finite_data = data_2d[~np.isnan(data_2d)]
                    if len(finite_data) > 0:
                        delta_min = abs(np.min(finite_data) - center)
                        delta_max = abs(np.max(finite_data) - center)
                        max_delta = max(delta_min, delta_max)

                        vmin = center - max_delta
                        vmax = center + max_delta

            # Annotation kwargs
            annot_kws = {}
            if self._heatmap_settings.annot_fontsize:
                annot_kws["fontsize"] = self._heatmap_settings.annot_fontsize
            if self._heatmap_settings.annot_color != ANNOTATION_COLOR.AUTO:
                annot_kws["color"] = self._heatmap_settings.annot_color.value

            show_cbar = self._heatmap_settings.cbar_orientation in [
                CBAR_ORIENTATION.VERTICAL,
                CBAR_ORIENTATION.HORIZONTAL,
            ]
            show_cbar = show_cbar and normalization in [
                NORMALIZATION.RAW,
                NORMALIZATION.CUSTOM,
                NORMALIZATION.BY_POSITION,
                NORMALIZATION.BY_POSITION,
                NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL,
            ]
            cbar_kws = None
            if show_cbar:
                cbar_kws = {
                    "orientation": self._heatmap_settings.cbar_orientation.value
                }

            # Generate the heatmap and supress warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                heatmap = sns.heatmap(
                    data_2d,
                    ax=ax,
                    cmap=cmap,
                    annot=self._heatmap_settings.annot,
                    fmt=(
                        f".{self._heatmap_settings.annot_digits}f"
                        if self._heatmap_settings.annot
                        else ""
                    ),
                    annot_kws=annot_kws if annot_kws else None,
                    cbar=show_cbar,
                    square=self._heatmap_settings.square,
                    vmin=vmin,
                    vmax=vmax,
                    center=center,
                    linewidths=self._heatmap_settings.linewidths,
                    linecolor=self._heatmap_settings.linecolor,
                    robust=self._heatmap_settings.robust,
                    cbar_kws=cbar_kws,
                )

            # Changes labels to σ notation if gaussian option was used

            if show_cbar and normalization in [
                NORMALIZATION.BY_POSITION_GAUSSIAN_ABSOLUTE,
                NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL,
            ]:
                cbar = heatmap.collections[0].colorbar

                current_ticks = cbar.get_ticks()
                # Only depict whole numbers
                allowed_ticks = [-3, -2, -1, 0, 1, 2, 3]
                # Prevents overflowing ticks
                vmin_cbar, vmax_cbar = cbar.mappable.get_clim()
                integer_ticks = [
                    t
                    for t in current_ticks
                    if t in allowed_ticks and vmin_cbar <= t <= vmax_cbar
                ]

                # Change to σ notation
                labels = [
                    f"−σ{int(-t)}" if t < 0 else f"σ{int(t)}" if t > 0 else "0"
                    for t in integer_ticks
                ]

                cbar.set_ticks(integer_ticks)
                cbar.set_ticklabels(labels)
            elif show_cbar:
                cbar = heatmap.collections[0].colorbar
                vmin_cbar, vmax_cbar = cbar.mappable.get_clim()
                tick_mode = self._heatmap_settings.cbar_tick_mode
                if tick_mode == CBAR_TICK_MODE.HIDE:
                    cbar.set_ticks([])
                elif tick_mode == CBAR_TICK_MODE.START_END:
                    vmin_cbar, vmax_cbar = cbar.mappable.get_clim()
                    cbar.set_ticks([vmin_cbar, vmax_cbar])
                elif tick_mode == CBAR_TICK_MODE.START_MIDDLE_END:
                    vmin_cbar, vmax_cbar = cbar.mappable.get_clim()
                    middle = (vmax_cbar + vmin_cbar) / 2
                    cbar.set_ticks([vmin_cbar, middle, vmax_cbar])
                elif tick_mode == CBAR_TICK_MODE.FOUR_TICKS:
                    vmin_cbar, vmax_cbar = cbar.mappable.get_clim()
                    cbar.set_ticks(np.linspace(vmin_cbar, vmax_cbar, 4))
                elif tick_mode == CBAR_TICK_MODE.FIVE_TICKS:
                    vmin_cbar, vmax_cbar = cbar.mappable.get_clim()
                    cbar.set_ticks(np.linspace(vmin_cbar, vmax_cbar, 5))
                elif tick_mode == CBAR_TICK_MODE.TEN_TICKS:
                    vmin_cbar, vmax_cbar = cbar.mappable.get_clim()
                    cbar.set_ticks(np.linspace(vmin_cbar, vmax_cbar, 10))

                if tick_mode not in [CBAR_TICK_MODE.HIDE, CBAR_TICK_MODE.AUTO]:
                    _, decimals = calculate_step_size(vmin_cbar, vmax_cbar)
                    current_ticks = cbar.get_ticks()
                    labels = [f"{t:.{decimals}f}" for t in current_ticks]

            # Set labels to row and column indices
            col_labels = range(n_cols)
            row_labels = range(n_rows)
            start_index = 0 if self._heatmap_settings.start_at_index_0 else 1
            if self._heatmap_settings.use_letter_annotation_x:
                col_labels = [
                    number_to_letters(i) for i in range(n_cols)
                ]  # Always start from A
            else:
                col_labels = range(start_index, n_cols + start_index)

            if self._heatmap_settings.use_letter_annotation_y:
                row_labels = [
                    number_to_letters(i) for i in range(n_rows)
                ]  # Always start from A
            else:
                row_labels = range(start_index, n_rows + start_index)

            if self._heatmap_settings.use_custom_col_labels:
                col_label_str = self._heatmap_settings.col_labels
                custom_col_labels = [
                    label.strip() for label in col_label_str.split(",") if label.strip()
                ]
                if len(custom_col_labels) == n_cols:
                    col_labels = custom_col_labels
                else:
                    logger.warning(
                        f"Custom column labels length mismatch: expected {n_cols}, got {len(custom_col_labels)}. "
                        "Falling back to default labels."
                    )

            if self._heatmap_settings.use_custom_row_labels:
                row_label_str = self._heatmap_settings.row_labels
                custom_row_labels = [
                    label.strip() for label in row_label_str.split(",") if label.strip()
                ]
                if len(custom_row_labels) == n_rows:
                    row_labels = custom_row_labels
                else:
                    logger.warning(
                        f"Custom row labels length mismatch: expected {n_rows}, got {len(custom_row_labels)}. "
                        "Falling back to default labels."
                    )

            # centered ticks
            x_ticks = np.arange(0.5, n_cols, 1)
            y_ticks = np.arange(0.5, n_rows, 1)

            ax.set_xticks(x_ticks)
            ax.set_yticks(y_ticks)
            ax.set_xticklabels(col_labels, rotation=0)
            ax.set_yticklabels(row_labels, rotation=0)

            ax.set_xlabel("")
            ax.set_ylabel("")

            # Differentiated font sizes for ticks
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(base_font_size - 2)

            # Grid and axes setup
            if not self._general_graph_settings.show_axis_ticks:
                ax.set_xticks([])
                ax.set_yticks([])

            if self._general_graph_settings.show_grid:
                ax.grid(True, alpha=self._general_graph_settings.transparency)
            else:
                ax.grid(False)

            if self._general_graph_settings.invert_x_axis:
                ax.invert_xaxis()
            if self._general_graph_settings.invert_y_axis:
                ax.invert_yaxis()

            # Transparency: Apply alpha to the heatmap patches
            alpha = 1.0 - self._general_graph_settings.transparency
            for patch in ax.patches:
                r, g, b, a = patch.get_facecolor()
                patch.set_facecolor((r, g, b, alpha))

            if self._heatmap_settings.highlight_reference_points:
                for ref_idx in self._value_extractor.references:
                    if self._general_graph_settings.swap_axes:
                        # Adjust for swapped axes: original rows become columns
                        ref_col = ref_idx // self._heatmap_settings.n_cols
                        ref_row = ref_idx % self._heatmap_settings.n_cols
                    else:
                        ref_row = ref_idx // n_cols
                        ref_col = ref_idx % n_cols
                    # Draw a rectangle around the cell
                    rect = plt.Rectangle(
                        (ref_col, ref_row),
                        1,
                        1,
                        fill=False,
                        edgecolor=self._heatmap_settings.highlight_color.value,
                        lw=2,
                    )
                    ax.add_patch(rect)

            plt.tight_layout(pad=1.5)

            logger.debug(f"Heatmap generated successfully for dataset: %s", dataset.id)
            return fig

        except Exception as e:
            logger.error(
                f"Failed to generate heatmap for dataset %s: %s",
                dataset.id,
                e,
                exc_info=True,
            )
            return None

    def add_global_colorbar(
        self,
        svg_image: sg.SVGFigure,
        plot_data: Dict[Dataset, List[float]],
        bar_width=200,
    ) -> sg.SVGFigure:
        """
        Add a global colorbar to the collage SVG.

        Args:
            svg_image (sg.SVGFigure): The original SVG image.
            plot_data (Dict[Dataset, List[float]]): Data for colorbar scaling.
            bar_width (int, optional): Width of the colorbar. Defaults to 200.

        Returns:
            sg.SVGFigure: The SVG with added colorbar.
        """
        logger.debug("Adding global colorbar to collage")

        # This is written to work generally even though we don't use all options

        all_values = [
            val for values in plot_data.values() for val in values if not np.isnan(val)
        ]
        if not all_values:
            logger.warning("No valid data for colorbar generation")
            return svg_image

        orientation = self._heatmap_settings.cbar_orientation
        if orientation == CBAR_ORIENTATION.HIDE:
            return svg_image  # Return original if no cbar

        vmin = min(all_values)
        vmax = max(all_values)
        center = None

        normalization = self._value_extractor.normalization
        if normalization in NORMALIZATION_REFERENCE_POINT:
            center = 0
            if normalization == NORMALIZATION.BY_POSITION:
                center = 1
            if self._heatmap_settings.symmetric_scaling:
                delta_min = abs(vmin - center)
                delta_max = abs(vmax - center)
                max_delta = max(delta_min, delta_max)
                vmin = center - max_delta
                vmax = center + max_delta

        # Colormap setup
        cmap = self._general_graph_settings.sequential_color_scheme.value
        if center is not None:
            cmap = self._general_graph_settings.divergent_color_scheme.value

        # Ticks and labels
        ticks = None
        ticklabels = None
        if normalization in [
            NORMALIZATION.BY_POSITION_GAUSSIAN_ABSOLUTE,
            NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL,
        ]:
            ticks = [-3, -2, -1, 0, 1, 2, 3]
            ticklabels = [
                f"−σ{int(-t)}" if t < 0 else f"σ{int(t)}" if t > 0 else "0"
                for t in ticks
            ]

        collage_width = float(svg_image.width.rstrip("pt"))
        collage_height = float(svg_image.height.rstrip("pt"))

        if orientation == CBAR_ORIENTATION.VERTICAL:
            width = bar_width
            height = collage_height
        else:  # horizontal
            width = collage_width
            height = bar_width

        # Figure size in inches (approx 72 pt per inch)
        fig_width = width / 72.0
        fig_height = height / 72.0

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Norm and colorbar
        norm = (
            mpl.colors.TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)
            if center is not None
            else mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        )
        cb = mpl.colorbar.ColorbarBase(
            ax,
            cmap=plt.get_cmap(cmap),
            norm=norm,
            orientation=orientation.value,
            ticks=ticks if ticks else None,
        )

        tick_font_size = max(1, int(self._collage.font_size * 0.618))
        cb.ax.tick_params(labelsize=tick_font_size)

        # Apply CBAR_TICK_MODE logic
        if normalization in [
            NORMALIZATION.BY_POSITION_GAUSSIAN_ABSOLUTE,
            NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL,
        ]:
            if ticks and ticklabels:
                cb.set_ticks(ticks)
                cb.set_ticklabels(ticklabels)
        else:
            tick_mode = self._heatmap_settings.cbar_tick_mode
            logger.debug(
                f"Setting global colorbar ticks with mode: %s", tick_mode.value
            )

            if tick_mode == CBAR_TICK_MODE.HIDE:
                cb.set_ticks([])
            elif tick_mode == CBAR_TICK_MODE.START_END:
                cb.set_ticks([vmin, vmax])
            elif tick_mode == CBAR_TICK_MODE.START_MIDDLE_END:
                middle = (vmax + vmin) / 2
                cb.set_ticks([vmin, middle, vmax])
            elif tick_mode == CBAR_TICK_MODE.FOUR_TICKS:
                cb.set_ticks(np.linspace(vmin, vmax, 4))
            elif tick_mode == CBAR_TICK_MODE.FIVE_TICKS:
                cb.set_ticks(np.linspace(vmin, vmax, 5))
            elif tick_mode == CBAR_TICK_MODE.TEN_TICKS:
                cb.set_ticks(np.linspace(vmin, vmax, 10))

            if tick_mode not in [CBAR_TICK_MODE.HIDE, CBAR_TICK_MODE.AUTO]:
                vmin_cbar, vmax_cbar = cb.mappable.get_clim()
                _, decimals = calculate_step_size(vmin_cbar, vmax_cbar)
                current_ticks = cb.get_ticks()
                labels = [f"{t:.{decimals}f}" for t in current_ticks]

        # Export to SVG
        with io.BytesIO() as buf:
            fig.savefig(buf, format="svg", pad_inches=5)
            buf.seek(0)
            svg_str = buf.read().decode("utf-8")

        plt.close(fig)

        cbar_svg = sg.fromstring(svg_str)
        root = cbar_svg.getroot()
        root.moveto(0, 0)

        cbar_fig = sg.SVGFigure(width=f"{width}pt", height=f"{height}pt")

        cbar_fig.append(root)

        # Combine with svg_image padding is used twice, between heatmap and bar and between bar and edge
        padding = tick_font_size * 2
        if orientation == CBAR_ORIENTATION.VERTICAL:
            total_width = collage_width + width + padding + padding
            total_height = max(collage_height, height)
            combined_fig = sg.SVGFigure(
                width=f"{total_width}pt", height=f"{total_height}pt"
            )
            collage_root = svg_image.getroot()
            collage_root.moveto(0, 0)
            combined_fig.append(collage_root)
            cbar_root = cbar_fig.getroot()
            cbar_root.moveto(collage_width + padding, 0)
            combined_fig.append(cbar_root)
            combined_fig.set_size((f"{total_width}pt", f"{total_height}pt"))
        else:  # horizontal
            total_width = max(collage_width, width)
            total_height = collage_height + height + padding + padding
            combined_fig = sg.SVGFigure(
                width=f"{total_width}pt", height=f"{total_height}pt"
            )
            collage_root = svg_image.getroot()
            collage_root.moveto(0, 0)
            combined_fig.append(collage_root)
            cbar_root = cbar_fig.getroot()
            cbar_root.moveto(0, collage_height + padding)
            combined_fig.append(cbar_root)
            combined_fig.set_size((f"{total_width}pt", f"{total_height}pt"))

        logger.debug("Global colorbar added successfully")
        return combined_fig

    def get_data_matrix(self, value_lists: Dict[Dataset, List[float]]):
        """
        Prepare a data matrix for CSV export.

        Args:
            value_lists (Dict[Dataset, List[float]]): The value lists.

        Returns:
            np.ndarray: The data matrix.
        """
        if not value_lists:
            raise ValueError("No data provided for heatmap generation")

        # Prepare data: Find max length and create 2D array with NaN padding
        max_len = max(len(values) for values in value_lists.values())
        data_matrix = np.full((len(value_lists), max_len), np.nan)

        return data_matrix

    def on_export_csv(self):
        """
        Export data as CSV using Tkinter save dialog.
        """
        if (
            self._value_extractor.normalization in NORMALIZATION_REFERENCE_POINT
            and len(self._value_extractor.references) == 0
        ):
            logger.info(
                "Could not export csv since no indices for export were selected."
            )
            return

        logger.debug("Exporting data as CSV")
        try:
            value_lists = self.filter_empty_datasets(self._filtered_values)

            if not value_lists:
                logger.warning("No data available for export")
                return

            attribute = self._value_extractor.attribute
            normalization = self._value_extractor.normalization

            csv_title = f"{attribute.value}"
            if normalization != NORMALIZATION.RAW:
                csv_title += f" - Normalized ({normalization.value})"

            # Generate the data matrix analogous to the graph
            data_matrix = self.get_data_matrix(value_lists=value_lists)

            # Datasets for rows
            datasets = list(value_lists.keys())

            for i, dataset in enumerate(datasets):
                values = value_lists[dataset]
                data_matrix[i, : len(values)] = values

            # Indices for columns (analogous to heatmap x_labels)
            max_len = data_matrix.shape[1]
            start_index = 0 if self._heatmap_settings.start_at_index_0 else 1
            indices = list(range(start_index, max_len + start_index))

            # Header row
            header = [csv_title] + indices

            # Tkinter Save-File-Dialog
            root = Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            root.focus_force()
            default_filename = (
                f"Heatmap_Collage_{attribute.value}_{normalization.value}.csv"
            )
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename,
                title="Save CSV As",
            )
            
            root.attributes('-topmost', False)
            root.destroy()
            
            if not file_path:
                logger.debug("CSV export cancelled by user")
                return

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)

                for i, dataset in enumerate(datasets):
                    descriptor = (
                        dataset.id
                        if self._dataset_descriptor == DATASET_LABEL.ID
                        else dataset.name
                    )
                    row = [descriptor] + [
                        "" if np.isnan(val) else val for val in data_matrix[i]
                    ]
                    writer.writerow(row)

            logger.info("CSV exported successfully to %s", file_path)
        except Exception as e:
            logger.error("Failed to export CSV: %s", e, exc_info=True)

    def update_scheme(self, new_scheme) -> None:
        """
        Update the color scheme and refresh analysis.

        Args:
            new_scheme: New color scheme to apply.
        """
        self._color_scheme = new_scheme
        # Currently this only forces a re-color of our table
        self.update_analysis()

    def reset_module(self) -> Optional[Self]:
        """
        Reset module to initial state.

        Returns:
            Optional[Self]: New instance of the module or None if reset failed.
        """
        logger.debug("Resetting module")
        try:
            new_module = OverviewHeatmapModule()
            logger.debug("Module reset successfully")
            return new_module
        except Exception as e:
            logger.error("Failed to reset module: %s", e, exc_info=True)
            return None
