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
import svgutils.transform as sg
import tempfile
import time
import pandas as pd
import warnings

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.viability_rules import (
    no_datasets_selected,
    sample_count_not_uniform,
    spot_count_is_not_uniform,
    has_insufficient_number_of_samples,
    has_negative_values,
)
from suplex_modules.submodules.value_extractor import (
    ValueExtractor,
    get_flat_value_list,
    flatten_list,
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
    SELECTION_MODE,
)
from suplex_modules.submodules.dataset_sorter import DatasetSorter
from suplex_modules.submodules.dataset_filters import DatasetFilter
from suplex_modules.submodules.sample_spot_filter import SampleSpotFilter
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
    ANNOTATION_COLOR,
    LINE_COLOR,
    CBAR_ORIENTATION,
    SEQUENTIAL_COLOR_SCHEME,
    GRID_STYLE,
    OPTION_WIDGETS_MAX_WIDTH,
    ASPECT_RATIO,
    CBAR_ORIENTATION,
    CBAR_TICK_MODE,
    get_aspect_ratio_value,
)

from suplex_modules.submodules.submodule_utils import number_to_letters

from suplex_modules.submodules.dynamic_threshold_filter import apply_dynamic_filtering

logger = logging.getLogger(__name__)

MAX_PIXELS_GRAPH = 2**20


class HitmapModule(SuplexModuleInterface):

    def __init__(self) -> None:
        """
        Initialize the HitmapModule with default settings and UI elements.
        """
        logger.debug("Initializing HitmapModule")
        self._datasets = []
        self._color_scheme = None

        self._sorted_datasets = []
        self._included_datasets = []
        self._excluded_datasets = []

        self._static_hitmaps = {}
        # Stores objects of FilteredValue
        self._filtered_values_dynamic = {}
        # Stores Hit or no hit
        self._dynamic_hitmaps = {}
        self._aggregated_maps = {}
        self._compound_map = []
        self._filtered_values = {}

        self._DEFAULT_HOVER_TEXT = (
            "Generates heatmaps in reference to static and dynamic filtering methods."
        )
        self._module_hover_text = self._DEFAULT_HOVER_TEXT

        # UI Elements
        self._value_extractor = None
        self._tabs = None

        self._dataset_sorter = None
        self._dataset_filter = None
        self._sample_spot_filter = None
        # Dynamic filter is a set of functions and not an object.

        self._descriptor_radio = None
        self._dataset_descriptor = DATASET_LABEL.ID

        # Updatable boxes which contain our content
        self._collage_plot_box = WidgetFactory.vbox(
            children=[],
            width="100%",
            height="100%",
            layout=widgets.Layout(padding="10px"),
        )
        self._compound_plot_box = WidgetFactory.vbox(
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
            str: The module name "Hitmap".
        """
        return "Hitmap"

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
        Get the group name for the module.

        Returns:
            str: The group name "Vanilla".
        """

        return "Vanilla"

    @property
    def button_style(self) -> Dict[str, str]:
        """
        Get the button style configuration for the module.

        Returns:
            Dict[str, str]: Dictionary with font_color, button_color, and button_icon.
        """
        return {"font_color": "#FFFFFF", "button_color": "#ff3333", "button_icon": "🎯"}

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        """
        Check if the module is viable based on the provided datasets.
        Future iteration may reduce this list.

        Args:
            datasets (List[Dataset]): List of datasets to check.

        Returns:
            bool: True if viable, False otherwise.
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

        # In future iterations we may remove the uniformity rules.
        if sample_count_not_uniform(datasets):
            self._module_hover_text = (
                f"Cannot initiate {self.module_name}. Sample count is not uniform."
            )
            logger.info(
                "The module %s has been disabled. Sample count is not uniform.",
                self.module_name,
            )
            return False

        if spot_count_is_not_uniform(datasets):
            self._module_hover_text = (
                f"Cannot initiate {self.module_name}. Sample count is not uniform."
            )
            logger.info(
                "The module %s has been disabled. Spot count is not uniform.",
                self.module_name,
            )
            return False

        if has_insufficient_number_of_samples(datasets=datasets, min_count=3):
            self._module_hover_text = (
                f"Cannot initiate {self.module_name}. Sample count is below three."
            )
            logger.info(
                "The module %s has been disabled. Sample count is below three.",
                self.module_name,
            )
            return False

        if has_negative_values(datasets):
            self._module_hover_text = (
                f"Cannot initiate {self.module_name} since datasets contain a negative value."
            )
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
            str: The current hover text for the module.
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
            self._included_datasets = datasets.copy()
            self._color_scheme = color_scheme

            self._general_graph_settings = GeneralGraphSettings(
                swap_axes=False,
                invert_x_axis=False,
                invert_y_axis=False,
                show_grid=True,
                show_title=True,
                show_axis_ticks=True,
                sequential_color_scheme=SEQUENTIAL_COLOR_SCHEME.ROCKET,
                base_font_size=20,
                aspect_ratio=ASPECT_RATIO.AUTO,
                grid_style=GRID_STYLE.WHITEGRID,
                transparency=0.0,
                dpi=300,
            )

            self._heatmap_settings = HeatmapSettings(
                square=False,
                annot=False,
                annot_fontsize=1,
                annot_digits=0,
                annot_color=ANNOTATION_COLOR.AUTO,
                linewidths=0,
                cell_size=0.4,
                linecolor=LINE_COLOR.BLACK,
                robust=False,
                cbar_options=list(CBAR_ORIENTATION),
                cbar_tick_options=[CBAR_TICK_MODE.AUTO, CBAR_TICK_MODE.HIDE],
                start_at_index_0=True,
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
            self._dataset_sorter = DatasetSorter(tags=all_tags, num_levels=1, max_num_levels=10)
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
            self._dataset_filter.get_method_dropdown().observe(
                lambda b: self._dataset_filter.on_filter_changed(datasets=self._datasets),
                names="value",
            )
            self._dataset_filter.get_attribute_dropdown().observe(
                lambda b: self._dataset_filter.on_filter_changed(datasets=self._datasets),
                names="value",
            )

            self._sample_spot_filter = SampleSpotFilter(
                included_attributes=attributes,
                included_normalization_methods=NORMALIZATION_DEFAULT,
            )
            # Sets up slider dimensions
            self._sample_spot_filter.on_filter_params_changed(self._datasets)

            self._value_extractor = ValueExtractor(
                attributes=attributes,
                normalization_methods=NORMALIZATION_DEFAULT,
                custom_factor=2**16,
            )
            # We use a statistics value for initial depiction since we have to generate more graphs for spot values
            self._value_extractor.get_attribute_widget().value = (
                DATASET_ATTRIBUTE.ADJUSTED_AVERAGE.value
            )

            # Adjust dataset filter slider to selected attribute/normalization
            def on_values_extracted_changed():
                # Changing the slider will result in triggering its listener
                self._ignore_events = True
                self._sample_spot_filter.on_filter_params_changed(
                    datasets=self._datasets,
                    attribute=self._value_extractor.attribute,
                    normalization_method=self._value_extractor.normalization,
                    normalization_factor=self._value_extractor.custom_factor,
                )
                self._ignore_events = False
                self.auto_update(self.update_analysis)

            for widget in self._value_extractor.get_active_widgets():
                widget.observe(lambda b: on_values_extracted_changed(), names="value")

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
            collage_graph_tab = WidgetFactory.vbox(
                children=[self._collage_plot_box],
                layout=widgets.Layout(width="100%", height="auto", overflow="auto"),
            )
            compound_graph_tab = WidgetFactory.vbox(
                children=[self._compound_plot_box],
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
                    collage_graph_tab,
                    compound_graph_tab,
                    sort_filter_tab,
                    settings_tab,
                ],
                titles=[
                    "Overview",
                    "Dataset Statistics",
                    "Individual Maps",
                    "Compound Map",
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
                current_tab_index = change["new"]
                current_tab_title = self._tabs.titles[current_tab_index]

                # Don't auto update on tabs which don't depict any data
                ignore_tabs = ["Sorting & Filters", "Settings"]
                if not current_tab_title in ignore_tabs:
                    self.auto_update(self.update_analysis)

            self._tabs.observe(on_tab_change, names="selected_index")

            # Main layout: controls on left, tabs on right
            module_ui = WidgetFactory.hbox(
                [controls, self._tabs],
                layout=widgets.Layout(height="100%", width="100%", gap="0px", overflow="hidden"),
            )

            logger.debug("Module UI initialized successfully")
            self.update_analysis()
            return module_ui

        except Exception as e:
            logger.error("Failed to initiate module: %s", e, exc_info=True)
            raise

    def create_main_control_interface(self) -> widgets.Widget:
        """
        Create the main control interface for the module.

        Returns:
            widgets.Widget: The control interface widget.
        """

        logger.debug("Creating main control interface")
        try:
            title_html = WidgetFactory.html_widget(value="<h2>Overview Heatmap</h2>", width="auto")
            controls_box = WidgetFactory.vbox(
                children=[
                    self._value_extractor.get_ui(),
                    self.create_hitmap_filter_controls_section(),
                ],
                layout=widgets.Layout(
                    height="auto",
                    width="100%",
                ),
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
            logger.error("Failed to create main control interface: %s", e, exc_info=True)
            raise

    def create_hitmap_filter_controls_section(self) -> widgets.Widget:
        """
        Create the hitmap filter controls section.

        Returns:
            widgets.Widget: The filter controls widget.
        """
        hitmap_filter_content = []

        # Static Thresholding
        static_filter_label = WidgetFactory.label(value="Static Thresholding:")

        static_filter_slider = self._sample_spot_filter.get_threshold_range_slider()
        static_filter_slider.observe(lambda b: self.auto_update(self.update_analysis))

        static_filter_invert_checkbox = self._sample_spot_filter.get_invert_checkbox()
        static_filter_invert_checkbox.observe(lambda b: self.auto_update(self.update_analysis))

        self._apply_static_filter_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Apply Static Filtering",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="100%",
            on_change=lambda b: self.auto_update(self.update_analysis),
        )
        checkboxes_box = WidgetFactory.hbox(
            children=[static_filter_invert_checkbox, self._apply_static_filter_checkbox],
            gap="5px",
            overflow="visible",
            height="auto",
        )

        static_filter_widgets = WidgetFactory.vbox(
            children=[static_filter_slider, checkboxes_box],
            gap="5px",
            overflow="visible",
            height="auto",
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )
        hitmap_filter_content += [static_filter_label, static_filter_widgets]

        # Dynamic Thresholding
        dynamic_filter_label = WidgetFactory.label(value="Maximum Signal to Noise Ratio:")

        self._sparsity_sider = WidgetFactory.float_slider(
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            description="",
            readout=True,
            readout_format=".2f",
            layout=widgets.Layout(width="100%", padding="0px 10px"),
            continuous_update=False,
            on_change=lambda b: self.auto_update(self.update_analysis),
        )

        self._apply_dynamic_filter_checkbox = WidgetFactory.checkbox(
            value=True,
            description="Apply Dynamic Filtering",
            indent=False,
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="100%",
            on_change=lambda b: self.auto_update(self.update_analysis),
        )

        dynamic_filter_widgets = WidgetFactory.vbox(
            children=[self._sparsity_sider, self._apply_dynamic_filter_checkbox],
            gap="5px",
            overflow="visible",
            height="auto",
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )
        hitmap_filter_content += [dynamic_filter_label, dynamic_filter_widgets]

        # Propagation between both threshold modes
        filter_propagation_label = WidgetFactory.label(value="Filter Propagation:")
        c_mode_values = [mode.value for mode in list(SELECTION_MODE)]
        self._compound_mode_dropdown = WidgetFactory.dropdown(
            options=c_mode_values,
            value=SELECTION_MODE.ALL.value,
            description="",
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="100%",
            on_change=lambda b: self.auto_update(self.update_analysis),
        )
        filter_propagation_widgets = WidgetFactory.vbox(
            children=[self._compound_mode_dropdown],
            gap="5px",
            overflow="visible",
            height="auto",
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )

        hit_continuity_label = WidgetFactory.label(value="Required Hit Continuity:")
        n_samples = 1
        if self._datasets:
            n_samples = max(len(dataset.samples) for dataset in self._datasets)

        self._hit_continuity_number_input = WidgetFactory.int_number_input(
            value=1,
            min_value=1,
            max_value=n_samples,
            description="",
            layout=widgets.Layout(margin="0px", padding="0px"),
            width="100%",
            on_change=lambda b: self.auto_update(self.update_analysis),
        )
        hit_continuity_widgets = WidgetFactory.vbox(
            children=[self._hit_continuity_number_input],
            gap="5px",
            overflow="visible",
            height="auto",
            layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
        )

        propagation_widgets = WidgetFactory.vbox(
            children=[filter_propagation_label, filter_propagation_widgets],
            gap="5px",
            overflow="visible",
            height="auto",
            layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
        )
        continuity_widgets = WidgetFactory.vbox(
            children=[hit_continuity_label, hit_continuity_widgets],
            gap="5px",
            overflow="visible",
            height="auto",
            layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
        )
        hitmap_filter_content.append(
            WidgetFactory.hbox(
                children=[propagation_widgets, continuity_widgets],
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
            )
        )

        return WidgetFactory.vbox(
            children=hitmap_filter_content, layout=widgets.Layout(width="100%", height="auto")
        )

    def create_control_button_section(self):
        """
        Create the control button section with export and update buttons.

        Returns:
            widgets.Widget: The button section widget.
        """
        logger.debug("Creating control button section")
        try:
            export_overview_plot_button = WidgetFactory.button_emphasis(
                "Export Overview Plot",
                on_click=lambda b: self.on_export_overview_plot(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height="30px",
            )

            export_overview_csv_button = WidgetFactory.button_emphasis(
                "Export Overview CSV",
                on_click=lambda b: self.on_export_overview_csv(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height="30px",
            )

            export_compound_plot_button = WidgetFactory.button_emphasis(
                "Export Compound Plot",
                on_click=lambda b: self.on_export_compound_plot(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height="30px",
            )

            export_compound_csv_button = WidgetFactory.button_emphasis(
                "Export Compound CSV",
                on_click=lambda b: self.on_export_compound_csv(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height="30px",
            )

            update_button = WidgetFactory.button_success(
                "Apply Changes",
                on_click=lambda b: self.update_analysis(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height="30px",
            )

            self._auto_update_checkbox = WidgetFactory.checkbox(
                value=False,
                description="Auto",
                indent=False,
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
                height="30px",
            )
            self._auto_update_checkbox.observe(
                lambda b: self.auto_update(self.update_analysis), names="value"
            )

            first_col = WidgetFactory.vbox(
                children=[export_overview_plot_button, export_compound_plot_button, update_button],
                height="auto",
                width="100%",
                overflow_y="visible",
                gap="2px",
            )

            second_col = WidgetFactory.vbox(
                children=[
                    export_overview_csv_button,
                    export_compound_csv_button,
                    self._auto_update_checkbox,
                ],
                height="auto",
                width="100%",
                overflow_y="visible",
                gap="2px",
            )

            control_button_section = WidgetFactory.hbox(
                children=[first_col, second_col],
                height="auto",
                width="100%",
                overflow_y="visible",
                gap="2px",
            )

            logger.debug("Control button section created successfully")
            return control_button_section
        except Exception as e:
            logger.error("Failed to create control button section: %s", e, exc_info=True)
            raise

    def create_sort_filter_tab(self) -> widgets.Widget:
        """
        Create the sorting and filtering tab content.

        Returns:
            widgets.Widget: The tab content widget.
        """
        dataset_sorter_ui = self._dataset_sorter.get_ui()
        dataset_filter_ui = self._dataset_filter.get_ui()
        # This module uses a shortened version of sample spot filter which is displayed in controls.

        filter_tab = WidgetFactory.vbox(
            children=[dataset_sorter_ui, dataset_filter_ui],
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
        Create the settings tab content.

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

        self._descriptor_radio[0].on_click(lambda b: on_change_descriptor(DATASET_LABEL.ID))
        self._descriptor_radio[1].on_click(lambda b: on_change_descriptor(DATASET_LABEL.NAME))

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
                self.create_collage_controls_section(),
                self._collage.get_ui(),
                self._heatmap_settings.get_ui(),
                self._general_graph_settings.get_ui(),
            ],
            layout=widgets.Layout(padding="10px", max_width=OPTION_WIDGETS_MAX_WIDTH),
            gap="10px",
        )

        logger.debug("Settings tab created successfully")
        return settings_tab

    def create_collage_controls_section(self) -> widgets.Widget:
        """
        Create the collage controls section for content options.

        Returns:
            widgets.Widget: The controls section widget.
        """
        try:
            logger.debug("Creating collage controls section")

            # We use nested collages as such the term super_collage
            super_collage_settings_title = WidgetFactory.html_widget(
                value="<h3>Collage Content Options</h3>"
            )
            super_collage_widgets = [super_collage_settings_title]

            self._add_unsorted_barcharts_checkbox = WidgetFactory.checkbox(
                value=False,
                description="Add Positional Barcharts",
                indent=False,
                layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            )

            self._add_sorted_barcharts_checkbox = WidgetFactory.checkbox(
                value=False,
                description="Add Sorted Barcharts",
                indent=False,
                layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
            )

            self._add_delta_barcharts_checkbox = WidgetFactory.checkbox(
                value=False,
                description="Add Delta Barcharts",
                indent=False,
                layout=widgets.Layout(height="30px", width="auto", margin="0px", padding="0px"),
                names="value",
            )

            checkbox_container = WidgetFactory.vbox(
                children=[
                    self._add_unsorted_barcharts_checkbox,
                    self._add_sorted_barcharts_checkbox,
                    self._add_delta_barcharts_checkbox,
                ],
                gap="5px",
                overflow="visible",
                height="auto",
                layout=widgets.Layout(padding=OPTION_INSET.PRIMARY),
            )
            super_collage_widgets.append(checkbox_container)

            collage_cols_label = WidgetFactory.label("Cols in Collage:")
            collage_cols_number_input = self._collage.get_columns_input()

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

            heatmap_cols_label = WidgetFactory.label("Cols per Heatmap:")
            heatmap_cols_number_input = self._heatmap_settings.get_n_cols_widget()

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
                children=[heatmap_cols_container, collage_cols_container],
                gap="10px",
                overflow="visible",
                layout=widgets.Layout(padding=OPTION_INSET.BASELINE),
            )

            # Add containers to super_collage_widgets
            super_collage_widgets.append(top_row_hbox)

            # Create the main container
            collage_controls_section = WidgetFactory.vbox(
                children=super_collage_widgets, gap="5px", overflow="visible", height="auto"
            )

            logger.debug("Collage controls section created successfully")
            return collage_controls_section

        except Exception as e:
            logger.error("Failed to create collage controls section: %s", e, exc_info=True)
            raise

    def auto_update(self, method: Callable[[], None]) -> None:
        """
        Automatically update the analysis if auto-update is enabled.

        Args:
            method (Callable[[], None]): The method to call for update.
        """
        if self._auto_update_checkbox.value:
            method()

    def update_analysis(self):
        """
        Update the full analysis including filters, overview, statistics, and graphs.
        """
        logger.debug("Updating analysis")
        self.apply_all_filters()
        self.update_overview()
        self.update_dataset_statistics()
        self.update_compound_graph()
        self.update_collage_graph()

    def apply_all_filters(self):
        """
        Apply all filters: dataset sorting, filtering, static and dynamic thresholds.
        """
        logger.debug("Applying all filters")
        if self._ignore_events:
            return
        self._sorted_datasets = self._dataset_sorter.get_sorted_datasets(self._datasets)
        self.apply_dataset_filter()

        # Technically we could pass filter results to compound map instead of storing them.
        self.apply_static_threshold()
        self.apply_dynamic_threshold()
        self.generate_compound_map()
        # No display value normalization in this module

    def apply_dataset_filter(self):
        """
        Apply the dataset filter to sort and include/exclude datasets.
        """
        logger.debug("Applying dataset filter")
        self._included_datasets, self._excluded_datasets = (
            self._dataset_filter.get_filtered_datasets(datasets=self._sorted_datasets)
        )

    def apply_static_threshold(self):
        """
        Apply static thresholding to extract filtered values and create hitmaps.
        """
        # Static threshold does not require splitting of spotfields.
        logger.debug("Applying value filter")
        attribute = self._value_extractor.attribute
        normalization_method = self._value_extractor.normalization

        datasets = self._included_datasets

        sample_threshold_map, spot_threshold_map = self._sample_spot_filter.get_filter_maps(
            datasets=datasets,
            attribute=self._value_extractor.attribute,
            normalization_method=self._value_extractor.normalization,
            normalization_factor=self._value_extractor.custom_factor,
            spots_affect_sample=False,
            sample_affects_spots=False,
        )

        filtered_values_static = self._sample_spot_filter.extract_filtered_values_from_datasets(
            datasets=datasets,
            attribute=attribute,
            sample_threshold_map=sample_threshold_map,
            spot_threshold_map=spot_threshold_map,
            outside_replacement_value=float("nan"),
            above_replacement_value=float("nan"),
            below_replacement_value=float("nan"),
        )
        # Hitmap formatting using 0 = no hit and 1 = hit
        self._static_hitmaps = {}
        for key, value_list in filtered_values_static.items():
            self._static_hitmaps[key] = [0 if pd.isna(value) else 1 for value in value_list]

    def apply_dynamic_threshold(self):
        """
        Apply dynamic thresholding to extract filtered values and create hitmaps.
        """
        # Dynamic thresholding does not use normalization, but requires a splitting of spotfields
        attribute = self._value_extractor.attribute
        datasets = self._included_datasets

        self._filtered_values_dynamic = {}
        self._dynamic_hitmaps = {}

        for dataset in datasets:
            n_spotfields = dataset.general_parameters.number_of_spotfields
            if n_spotfields is None or attribute in DATA_STATISTICS_ATTRIBUTES:
                n_spotfields = 1

            # Extract flat map where the spots of each sample are placed next to one another
            value_map = get_flat_value_list(dataset=dataset, attribute=attribute)
            # Split flat map into spotfield maps
            spot_field_values_lists = [value_map[i::n_spotfields] for i in range(n_spotfields)]
            # Apply dynamic filtering for each set of spotfield values
            transformed_lists = [
                apply_dynamic_filtering(
                    value_list=spot_field_values_list,
                    max_relevant_fraction=self._sparsity_sider.value,
                )
                for spot_field_values_list in spot_field_values_lists
            ]
            # Re-create flat list for later to fit the format of static filtering and heatmap generation.
            restored_list_transformed = []
            # This requires all samples to have the same number of spots
            for i, value in enumerate(transformed_lists[0]):
                for transformed_list in transformed_lists:
                    restored_list_transformed.append(transformed_list[i])

            self._filtered_values_dynamic[dataset] = restored_list_transformed

        self._dynamic_hitmaps = {
            key: [1 if value.SIGNIFICANT else 0 for value in values]
            for key, values in self._filtered_values_dynamic.items()
        }

    def generate_compound_map(self):
        """
        Generate the compound map by aggregating static and dynamic hitmaps.
        """
        # Compound map is a list of dataset references
        # Len of compound map results in hitmap
        self._aggregated_maps = {}
        self._filtered_values = {}

        apply_static_filter = self._apply_static_filter_checkbox.value
        apply_dynamic_filter = self._apply_dynamic_filter_checkbox.value

        if not (apply_static_filter or apply_dynamic_filter):
            # Compound map and aggregated_maps are now empty
            return

        # If one option is set to false just work with a duplicate list (same result for both ALL and ANY).
        static_maps = self._static_hitmaps if apply_static_filter else self._dynamic_hitmaps
        dynamic_maps = self._dynamic_hitmaps if apply_dynamic_filter else self._static_hitmaps

        if len(static_maps) != len(dynamic_maps):
            # Should never be the case logically
            logger.critical(
                f"Variing length between static map lists ({len(static_maps)}) and dynamic map ({len(dynamic_maps)})"
            )
            return None

        filter_aggregation_mode = SELECTION_MODE(self._compound_mode_dropdown.value)
        min_hit_continuity = self._hit_continuity_number_input.value

        # Dynamically set compound maps dimensions
        max_length = max(len(static_map) for static_map in static_maps.values())
        self._compound_map = [[] for _ in range(max_length)]

        for key, static_map in static_maps.items():
            dynamic_map = dynamic_maps[key]
            if len(static_map) != len(dynamic_map):
                # Should never be the case logically
                logger.critical(
                    f"Variing length between static maps ({len(static_map)}) and dynamic map ({len(dynamic_map)})"
                )
                return None

            # Use AND or OR for hitmap overlaps.
            dataset_hitmap = []
            for i, static_value in enumerate(static_map):
                # 0 = False, 1 = True
                if filter_aggregation_mode == SELECTION_MODE.ALL:
                    dataset_hitmap.append(static_value and dynamic_map[i])
                elif filter_aggregation_mode == SELECTION_MODE.ANY:
                    dataset_hitmap.append(static_value or dynamic_map[i])
                else:
                    logger.warning(
                        f"Illegal selection mode used: {filter_aggregation_mode}. Will default to False."
                    )
                    dataset_hitmap.append(False)

            # Requirement of n hits in continuity for them to be counted as such.
            continual_hitmap = []
            cont_map = []
            for hit in dataset_hitmap:
                cont_map.append(hit)
                if not hit:
                    if sum(cont_map) < min_hit_continuity:
                        cont_map = [False] * len(cont_map)
                    continual_hitmap += cont_map
                    cont_map = []

            if cont_map and sum(cont_map) < min_hit_continuity:
                cont_map = [False] * len(cont_map)
            continual_hitmap += cont_map

            for j, hit in enumerate(continual_hitmap):
                if hit:
                    self._compound_map[j].append(key)

            # Store result of aggregation per dataset for later use
            self._aggregated_maps[key] = [
                int(x) for x in continual_hitmap
            ]  # use 0 and 1 instead of true/false to keep consistency
            self._filtered_values[key] = [
                value.VALUE if h >= 1 else np.nan
                for value, h in zip(self._filtered_values_dynamic[key], continual_hitmap)
            ]

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

            value_threshold_title = "Thresholding"
            apply_static_filter = self._apply_static_filter_checkbox.value
            apply_dynamic_filter = self._apply_dynamic_filter_checkbox.value

            if not self._included_datasets:
                html_content += f"<h3>{value_threshold_title}</h3>"
                html_content += (
                    "<ul><li><strong>No Values Left for Value Filtering</strong></li></ul>"
                )
                self._overview_box.children = [WidgetFactory.html_widget(html_content)]
                return

            if not apply_static_filter and not apply_dynamic_filter:
                html_content += f"<h3>{value_threshold_title}</h3>"
                html_content += "<ul><li><strong>No Filter active</strong></li></ul>"
                self._overview_box.children = [WidgetFactory.html_widget(html_content)]
                return

            threshold_min, threshold_max = (
                self._sample_spot_filter.get_threshold_range_slider().value
            )

            n_values = sum(len(values) for values in self._filtered_values.values())
            all_non_nan_values = [
                v for values in self._filtered_values.values() for v in values if not pd.isna(v)
            ]
            n_values_included = len(all_non_nan_values)
            filtered_values_mean = np.nanmean(all_non_nan_values) if all_non_nan_values else 0.0
            filtered_values_min = np.nanmin(all_non_nan_values) if all_non_nan_values else 0.0
            filtered_values_max = np.nanmax(all_non_nan_values) if all_non_nan_values else 0.0

            html_content += f"""
            <h3>{value_threshold_title}</h3>
            <ul>
                <li><strong>Static Filter Active:</strong> {apply_static_filter}</li>
                <li><strong>Static Filter Range:</strong> {threshold_min} - {threshold_max}</li>
                <li><strong>Static Filter Inverted:</strong> {self._sample_spot_filter.invert}</li>
                <li><strong>Dynamic Filter Active:</strong> {apply_dynamic_filter}</li>
                <li><strong>Dynamic Filter Sparsity:</strong> {self._sparsity_sider.value}</li>
                <li><strong>Filter Propagation Mode:</strong> {self._compound_mode_dropdown.value}</li>
                <li><strong>Values in Range:</strong> {n_values_included} / {n_values} ({n_values_included/n_values*100:.1f}%)</li>
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
            if (
                not self._apply_static_filter_checkbox.value
                and not self._apply_dynamic_filter_checkbox.value
            ):
                html_str = f"Please select a filter method to generate statistics."
                self._dataset_stats_box.children = [
                    WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
                ]
                return

            dataset_stats = []
            attribute = self._value_extractor.attribute
            normalization = self._value_extractor.normalization

            for dataset in self._included_datasets:
                values = self._filtered_values[dataset]
                static_hitmap = self._static_hitmaps[dataset]
                dynamic_hitmap = self._dynamic_hitmaps[dataset]

                n_values = len(static_hitmap)  # the same as values and dynamic hitmap

                n_hits_static = sum(static_hitmap)
                n_hits_static_perc = (n_hits_static / n_values) * 100 if n_values > 0 else 0

                n_hits_dynamic = sum(dynamic_hitmap)
                n_hits_dynamic_perc = (n_hits_dynamic / n_values) * 100 if n_values > 0 else 0

                overlap_count = sum(s and d for s, d in zip(static_hitmap, dynamic_hitmap))
                overlap_count_perc = (overlap_count / n_values) * 100 if n_values > 0 else 0

                if np.all(np.isnan(values)):
                    stat_mean = np.nan
                    stat_median = np.nan
                    stat_min = np.nan
                    stat_max = np.nan
                    stat_std = np.nan
                else:
                    stat_mean = np.nanmean(values)
                    stat_median = np.nanmedian(values)
                    stat_min = np.nanmin(values)
                    stat_max = np.nanmax(values)
                    stat_std = np.nanstd(values)

                name = dataset.id if self._dataset_descriptor == DATASET_LABEL.ID else dataset.name

                stat = {
                    "name": name,
                    "n_values": n_values,
                    "n_hits_static": n_hits_static,
                    "n_hits_static_perc": n_hits_static_perc,
                    "n_hits_dynamic": n_hits_dynamic,
                    "n_hits_dynamic_perc": n_hits_dynamic_perc,
                    "overlap_count": overlap_count,
                    "overlap_count_perc": overlap_count_perc,
                    "mean_filtered": stat_mean,
                    "median_filtered": stat_median,
                    "min_filtered": stat_min,
                    "max_filtered": stat_max,
                    "std_filtered": stat_std,
                }

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

            static_enabled = self._apply_static_filter_checkbox.value
            dynamic_enabled = self._apply_dynamic_filter_checkbox.value

            html_content = f"<h3>Dataset Statistics: {attribute.value} {norm_text}</h3>"

            html_content += f"""
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: {head_col}; color: {font_col_head};">
                    <th style="padding: 8px; text-align: left; border: 1px solid {line_col};">Dataset</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">n Values</th>
            """

            if static_enabled:
                html_content += f"""
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">n Included Static Filtering</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Percent Included Static Filtering</th>
            """

            if dynamic_enabled:
                html_content += f"""
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">n Included Dynamic Filtering</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Percent Included Dynamic Filtering</th>
            """

            if static_enabled and dynamic_enabled:
                html_content += f"""
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Overlap between Filters</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Percent Included Total</th>
            """

            html_content += f"""
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Mean Filtered</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Median Filtered</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Min Filtered</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Max Filtered</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid {line_col};">Std Dev Filtered</th>
                """
            html_content += "</tr>"
            for stat in dataset_stats:
                html_content += f"""
                <tr style="color: {font_col_body};">
                    <td style="padding: 8px; border: 1px solid {line_col};">{stat["name"]}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["n_values"]}</td>
                """

                if static_enabled:
                    html_content += f"""
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["n_hits_static"]}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["n_hits_static_perc"]:.2f}</td>
                    """

                if dynamic_enabled:
                    html_content += f"""
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["n_hits_dynamic"]}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["n_hits_dynamic_perc"]:.2f}</td>
                    """

                if static_enabled and dynamic_enabled:
                    html_content += f"""
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["overlap_count"]}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["overlap_count_perc"]:.2f}</td>
                    """

                html_content += f"""
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["mean_filtered"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["median_filtered"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["min_filtered"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["max_filtered"]:.4f}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid {line_col};">{stat["std_filtered"]:.4f}</td>
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

    def update_compound_graph(self) -> None:
        """
        Update the compound graph display.
        """
        logger.debug("Updating compound hitmap")
        try:
            # No filter method selected
            if (
                not self._apply_static_filter_checkbox.value
                and not self._apply_dynamic_filter_checkbox.value
            ):
                html_str = f"Please select a filter method to generate a hitmap."
                self._compound_plot_box.children = [
                    WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
                ]
                return

            if not self._compound_map:
                html_str = f"No datasets left after filtering."
                self._compound_plot_box.children = [
                    WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
                ]
                return

            svg_fig = self.get_compound_heatmap_collage()

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

            self._compound_plot_box.children = [html_widget]

        except Exception as e:
            html_str = f"Error generating plot: {str(e)}"
            if "Image size" in str(e) and "too large" in str(e):
                html_str = "Could not generate plot, please reduce dimensions."
                logger.warning("Failed to generate compound plot: %s", e, exc_info=True)
            else:
                logger.error("Failed to generate compound plot: %s", e, exc_info=True)

            self._compound_plot_box.children = [
                WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
            ]

    def on_export_compound_plot(self):
        """
        Handle export of the compound plot as SVG.
        """
        logger.debug("Exporting plot")
        try:
            if (
                not self._apply_static_filter_checkbox.value
                and not self._apply_dynamic_filter_checkbox.value
            ):
                logger.warning(
                    f"Could not export compound plots. Please select a filter method to generate a hitmap."
                )
                return

            if not self._compound_map:
                logger.warning(
                    f"Could not export compound plots. No datasets left after filtering."
                )
                return

            svg_fig = self.get_compound_heatmap_collage()
            default_filename = f"Compound_Hitmap_{self._value_extractor.attribute.value}_{self._value_extractor.normalization.value}.svg"

            root = Tk()
            root.withdraw()
            root.lift()
            root.attributes("-topmost", True)
            root.focus_force()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG files", "*.svg")],
                initialfile=default_filename,
                title="Save Plot As",
            )
            root.attributes("-topmost", False)
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

    def get_compound_heatmap_collage(self) -> sg.SVGFigure:
        """
        Generate the compound heatmap collage as SVG.

        Returns:
            sg.SVGFigure: The SVG figure for the compound heatmap collage.
        """
        # We use collage incase data option with multiple spotfields was selected.
        # This may result in a 1x1 collage.
        compound_count_map = [len(hits) for hits in self._compound_map]
        max_value = max(compound_count_map)

        n_spotfields = self._included_datasets[0].general_parameters.number_of_spotfields
        if n_spotfields is None or self._value_extractor.attribute in DATA_STATISTICS_ATTRIBUTES:
            n_spotfields = 1

        spotfield_compound_count_maps = [
            compound_count_map[i::n_spotfields] for i in range(n_spotfields)
        ]
        compound_heatmaps = []
        title = ""
        for i, spot_field_hit_list in enumerate(spotfield_compound_count_maps):
            if len(spotfield_compound_count_maps) > 1:
                title = f"Spotfield {i}"
            compound_heatmaps.append(
                self.generate_heatmap(
                    title=title,
                    dataset=None,
                    plot_values=spot_field_hit_list,
                    min_value=0,
                    max_value=max_value,
                )
            )

        columns = int(math.ceil(math.sqrt(len(compound_heatmaps))))

        # Collage without title or margins
        collage_image = self._collage.generate_collage(
            images=compound_heatmaps,
            columns=columns,
            dpi=self._general_graph_settings.dpi,
            title="",
            horizontal_margin=0,
            vertical_margin=0,
        )

        collage_image = self.add_global_colorbar(svg_image=collage_image, vmin=0, vmax=max_value)

        # Add title and margins after adding colorbar for proper positioning
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

        return collage_image

    def update_collage_graph(self) -> None:
        """
        Update the collage graph display.
        """
        logger.debug("Generating hitmap collage")
        try:
            if (
                not self._apply_static_filter_checkbox.value
                and not self._apply_dynamic_filter_checkbox.value
            ):
                html_str = f"Please select a filter method to generate hitmaps."
                self._collage_plot_box.children = [
                    WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
                ]
                return

            if not self._compound_map:
                html_str = f"No datasets left after filtering."
                self._collage_plot_box.children = [
                    WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
                ]
                return

            svg_fig = self.get_collage()

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

            self._collage_plot_box.children = [html_widget]

        except Exception as e:
            html_str = f"Error generating plot: {str(e)}"
            if "Image size" in str(e) and "too large" in str(e):
                html_str = "Could not generate plot, please reduce dimensions."
                logger.warning("Failed to generate plot: %s", e, exc_info=True)
            else:
                logger.error("Failed to generate plot: %s", e, exc_info=True)

            self._collage_plot_box.children = [
                WidgetFactory.info_field_error([WidgetFactory.html_widget(html_str)])
            ]

    def on_export_overview_plot(self):
        """
        Handle export of the overview plot as SVG.
        """
        logger.debug("Exporting plot")
        try:
            if (
                not self._apply_static_filter_checkbox.value
                and not self._apply_dynamic_filter_checkbox.value
            ):
                logger.warning(
                    f"Could not export compound plots. Please select a filter method to generate a hitmap."
                )
                return

            if not self._compound_map:
                logger.warning(
                    f"Could not export compound plots. No datasets left after filtering."
                )
                return

            svg_fig = self.get_collage()
            default_filename = f"Hitmap_Collage_{self._value_extractor.attribute.value}_{self._value_extractor.normalization.value}.svg"

            root = Tk()
            root.withdraw()
            root.lift()
            root.attributes("-topmost", True)
            root.focus_force()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG files", "*.svg")],
                initialfile=default_filename,
                title="Save Plot As",
            )
            root.attributes("-topmost", False)
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

    def get_collage(self) -> sg.SVGFigure:
        """
        Generate the collage from individual dataset heatmaps and barcharts.

        Returns:
            sg.SVGFigure: The SVG figure for the collage.
        """
        logger.debug("Generating collage from individual dataset heatmaps")
        threshold_lines = []

        # Depict threshold lines if they are used and if they are not in absolute positions
        if self._apply_static_filter_checkbox.value:
            min_threshold = self._sample_spot_filter.min_threshold
            abs_min_threshold = self._sample_spot_filter.get_threshold_range_slider().min
            if min_threshold > abs_min_threshold:
                threshold_lines.append(min_threshold)
            max_threshold = self._sample_spot_filter.max_threshold
            abs_max_threshold = self._sample_spot_filter.get_threshold_range_slider().max
            if max_threshold < abs_max_threshold:
                threshold_lines.append(max_threshold)

        # Flags
        dynamic_threshold_enabled = self._apply_dynamic_filter_checkbox.value
        add_unsorted_barcharts = self._add_unsorted_barcharts_checkbox.value
        add_sorted_barcharts = self._add_sorted_barcharts_checkbox.value
        add_delta_barcharts = self._add_delta_barcharts_checkbox.value

        # Scaling of non delta value barcharts is done globally
        abs_max_value = max(
            max(obj.VALUE for obj in values) for values in self._filtered_values_dynamic.values()
        )

        sub_collages = []
        for dataset, aggregated_values in self._aggregated_maps.items():
            n_spotfields = dataset.general_parameters.number_of_spotfields
            if (
                n_spotfields is None
                or self._value_extractor.attribute in DATA_STATISTICS_ATTRIBUTES
            ):
                n_spotfields = 1

            dataset_figures = []
            spot_field_hit_lists = [aggregated_values[i::n_spotfields] for i in range(n_spotfields)]
            # We use filtered values dynamic to be able to extract group indices
            spot_field_values_lists = [
                self._filtered_values_dynamic[dataset][i::n_spotfields] for i in range(n_spotfields)
            ]

            for i, spot_field_hit_list in enumerate(spot_field_hit_lists):
                title_str = "Hitmap"
                if len(spot_field_values_lists) > 1:
                    title_str += f" - Spotfield {i}"

                dataset_figures.append(
                    self.generate_heatmap(
                        title=title_str,
                        dataset=dataset,
                        plot_values=spot_field_hit_list,
                        min_value=0,
                        max_value=1,
                    )
                )

            plot_values_lists = []
            group_lists = []
            for spot_field_values_list in spot_field_values_lists:
                if add_unsorted_barcharts or add_sorted_barcharts:
                    plot_values = [value.VALUE for value in spot_field_values_list]
                    groups = [value.GROUP_NR for value in spot_field_values_list]
                    # Set all insignificant groups to the lowest insignificant group value
                    if dynamic_threshold_enabled:
                        min_insignificant_group = min(
                            (
                                value.GROUP_NR
                                for value in spot_field_values_list
                                if not value.SIGNIFICANT
                            ),
                            default=0,
                        )
                        groups = [
                            min_insignificant_group if group >= min_insignificant_group else group
                            for group in groups
                        ]
                    plot_values_lists.append(plot_values)
                    group_lists.append(groups)

            # We set the height of barcharts to the same as our heatmaps
            fig_height = dataset_figures[0].get_figheight()
            if add_unsorted_barcharts:
                for i, spot_field_values_list in enumerate(spot_field_values_lists):
                    title_str = "Values"
                    if len(spot_field_values_lists) > 1:
                        title_str += f" - Spotfield {i}"
                    dataset_figures.append(
                        self.generate_barchart(
                            title=title_str,
                            plot_values=plot_values_lists[i],
                            groups=group_lists[i],
                            threshold_lines=threshold_lines,
                            max_value=abs_max_value,
                        )
                    )

            if add_sorted_barcharts:
                for i, spot_field_values_list in enumerate(spot_field_values_lists):
                    title_str = "Sorted Values"
                    if len(spot_field_values_lists) > 1:
                        title_str += f" - Spotfield {i}"
                    # Sort both list by absolute value in ascending order
                    combined_data = list(zip(plot_values_lists[i], group_lists[i]))
                    sorted_combined = sorted(combined_data, key=lambda x: x[0])
                    # unzip sorted lists
                    sorted_plot_values = [item[0] for item in sorted_combined]
                    sorted_groups = [item[1] for item in sorted_combined]

                    dataset_figures.append(
                        self.generate_barchart(
                            title=title_str,
                            plot_values=sorted_plot_values,
                            groups=sorted_groups,
                            threshold_lines=threshold_lines,
                            max_value=abs_max_value,
                        )
                    )

            if add_delta_barcharts:
                for i, spot_field_values_list in enumerate(spot_field_values_lists):
                    title_str = "Delta Values"
                    if len(spot_field_values_lists) > 1:
                        title_str += f" - Spotfield {i}"

                    delta_values = [value.DELTA for value in spot_field_values_list]
                    dataset_figures.append(
                        self.generate_barchart(title=title_str, plot_values=delta_values, groups=[])
                    )

            title = ""
            if self._general_graph_settings.show_title:
                title = dataset.id if self._dataset_descriptor == DATASET_LABEL.ID else dataset.name

            # We use constant values for the sub-collages, maybe we'll make this interactive in a future version
            # Commented attributes default to the same setting as the overarching collage
            sub_title_size = max(1, int(self._collage.font_size * 0.618))  # Golden ratio

            dataset_cols = n_spotfields
            if (
                not (add_unsorted_barcharts or add_sorted_barcharts or add_delta_barcharts)
                or n_spotfields <= 1
            ):
                dataset_cols = int(math.ceil(math.sqrt(len(dataset_figures))))

            sub_collages.append(
                self._collage.generate_collage(
                    images=dataset_figures,
                    layout=COLLAGE_LAYOUT.GRID_EQUAL_ALL,
                    columns=dataset_cols,
                    scale_option=SCALE_OPTION.DOWNSCALE_TO_WIDTH,
                    padding_horizontal=10,
                    padding_vertical=10,
                    horizontal_margin=0,
                    vertical_margin=0,
                    title=title,
                    font_size=sub_title_size,
                    dpi=self._general_graph_settings.dpi,
                )
            )
            for fig in dataset_figures:
                plt.close(fig)

        # Collage without title or margins
        collage_image = self._collage.generate_collage(
            images=sub_collages,
            dpi=self._general_graph_settings.dpi,
            title="",
            horizontal_margin=0,
            vertical_margin=0,
        )

        collage_image = self.add_global_colorbar(svg_image=collage_image, vmin=0, vmax=1)

        # Add title and margins after adding colorbar for proper positioning
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

    def generate_barchart(
        self,
        title: str,
        plot_values: List[float],
        groups: List[int] = [],
        threshold_lines: List[float] = [],
        max_value: Optional[float] = None,
    ) -> plt.Figure:
        """
        Generate a barchart figure.

        Args:
            title (str): Title of the barchart.
            plot_values (List[float]): Values to plot.
            groups (List[int], optional): Group indices for coloring. Defaults to [].
            threshold_lines (List[float], optional): Threshold lines to draw. Defaults to [].
            max_value (Optional[float], optional): Maximum value for scaling. Defaults to None.

        Returns:
            plt.Figure: The matplotlib figure for the barchart.
        """
        if max_value is None:
            max_value = max(plot_values)

        sns.set_style(self._general_graph_settings.grid_style.value)
        base_font_size = self._general_graph_settings.base_font_size
        tick_font_size = base_font_size - 2
        plt.rcParams.update({"font.size": base_font_size})

        # Set bar to 1 in
        bar_width = 1
        fig_width = bar_width * len(plot_values)
        fig_height = fig_width
        ar_value = get_aspect_ratio_value(self._general_graph_settings.aspect_ratio)
        if ar_value is not None:
            fig_height = fig_width / ar_value

        # Add margin for labels
        tick_label_space = tick_font_size / 72.0
        if self._general_graph_settings.swap_axes:
            fig_height += tick_label_space
        else:
            char_width_factor = 0.6
            max_n_digits = len(str(max_value))
            tick_label_space = tick_label_space * char_width_factor * max_n_digits
            fig_width += tick_label_space

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        current_dpi = fig.dpi
        est_width_pixels = fig_width * current_dpi
        est_height_pixels = fig_height * current_dpi
        if (est_width_pixels > MAX_PIXELS_GRAPH) or (est_height_pixels > MAX_PIXELS_GRAPH):
            min_dpi_width = MAX_PIXELS_GRAPH / fig_width
            min_dpi_height = MAX_PIXELS_GRAPH / fig_height
            min_dpi = max(50, min(min_dpi_width, min_dpi_height))
            fig.set_dpi(min_dpi)
            logger.info(
                f"Proactively reduced DPI to {min_dpi} for bar chart (estimated pixels: {est_width_pixels:.0f}x{est_height_pixels:.0f})"
            )
        index_labels = range(len(plot_values))
        # Seaborn doesn't like pureley numerical labels and will try to typecast as such we make our labels strings
        index_labels = [f"i{label}" for label in index_labels]
        data = pd.DataFrame({"values": plot_values, "index": index_labels})
        # Forces to keep explicit order
        categories = data["index"].tolist()
        data["index"] = pd.Categorical(data["index"], categories=categories, ordered=True)

        # Set up color palette
        palette = plt.get_cmap(self._general_graph_settings.sequential_color_scheme.value)
        color_map = [palette(0.5)] * len(plot_values)
        if groups and len(groups) == len(plot_values):
            # Translate group list to color list for each bar
            max_group = max(groups) if groups else 1  # Avoid division by zero
            # Create a dictionary mapping each group in range(0, max_group + 1) to a color
            colors = {
                group: palette(1.0 - (group / max_group) if max_group > 0 else 0.5)
                for group in range(max_group + 1)
            }
            color_map = [colors[group] for group in groups]

        # Create the barplot with supressed warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            if self._general_graph_settings.swap_axes:
                sns.barplot(
                    data=data,
                    x="values",
                    y="index",
                    hue=None,
                    palette=None,
                    width=bar_width,
                    alpha=1.0 - self._general_graph_settings.transparency,
                    ax=ax,
                    legend=False,
                )
                ax.set_yticklabels([])
                ax.set_yticks([])
                ax.set_xlim(0, max_value)
            else:
                sns.barplot(
                    data=data,
                    x="index",
                    y="values",
                    hue="index",
                    width=bar_width,
                    palette=color_map,
                    alpha=1.0 - self._general_graph_settings.transparency,
                    ax=ax,
                    legend=False,
                )
                ax.set_xticklabels([])
                ax.set_xticks([])
                ax.set_ylim(0, max_value)

        if self._general_graph_settings.show_title:
            ax.set_title(title, fontsize=base_font_size, color=self._collage.title_color.value)

        # Remove axis labels
        ax.set_xlabel("", fontsize=base_font_size - 2)
        ax.set_ylabel("", fontsize=base_font_size - 2)

        # Adjust tick label sizes
        ax.tick_params(axis="both", which="major", labelsize=tick_font_size)

        # Grid and axes setup
        if self._general_graph_settings.show_grid:
            ax.grid(True, alpha=self._general_graph_settings.transparency)
        else:
            ax.grid(False)

        if not self._general_graph_settings.show_axis_ticks:
            ax.set_yticks([])
            ax.set_xticks([])

        # Invert axes if enabled
        if self._general_graph_settings.invert_x_axis:
            ax.invert_xaxis()
        if self._general_graph_settings.invert_y_axis:
            ax.invert_yaxis()

        # De-normalize threshold lines
        if self._value_extractor.normalization == NORMALIZATION.INTERNAL:
            threshold_lines = [line * max(plot_values) for line in threshold_lines]
        elif self._value_extractor.normalization == NORMALIZATION.GLOBAL:
            threshold_lines = [line * max_value for line in threshold_lines]
        elif self._value_extractor.normalization == NORMALIZATION.CUSTOM:
            custom_factor = self._value_extractor.custom_factor
            threshold_lines = [line * custom_factor for line in threshold_lines]

        # Add threshold lines if provided
        if threshold_lines:
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            # Lines are drawn if they fit in the barchart and always stretch the entire x or y axis
            if self._general_graph_settings.swap_axes:
                for line in threshold_lines:
                    if x_min < line < x_max:
                        ax.vlines(
                            line,
                            y_min,
                            y_max,
                            colors="red",
                            linestyles="--",
                            linewidth=1.5,
                            alpha=0.7,
                        )
            else:
                for line in threshold_lines:
                    if y_min < line < y_max:
                        ax.hlines(
                            line,
                            x_min,
                            x_max,
                            colors="red",
                            linestyles="--",
                            linewidth=1.5,
                            alpha=0.7,
                        )

        plt.tight_layout(pad=1.5)

        logger.debug(
            f"Bar chart generated successfully: {len(plot_values)} bars, {len(groups)} groups, swap_axes={self._general_graph_settings.swap_axes}"
        )
        return fig

    def generate_heatmap(
        self,
        title: str,
        dataset: Optional[Dataset],
        plot_values: List[float],
        min_value: float,
        max_value: float,
    ) -> plt.Figure:
        """
        Generate a heatmap figure.

        Args:
            title (str): Title of the heatmap.
            dataset (Optional[Dataset]): Dataset reference, if applicable.
            plot_values (List[float]): Values to plot in the heatmap.
            min_value (float): Minimum value for color scaling.
            max_value (float): Maximum value for color scaling.

        Returns:
            plt.Figure: The matplotlib figure for the heatmap.
        """

        dataset_descriptor = dataset.id if dataset else "compound"
        logger.debug(f"Generating heatmap for dataset: {dataset_descriptor}")

        try:
            # No truncation logic
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

            if (est_width_pixels > MAX_PIXELS_GRAPH) or (est_height_pixels > MAX_PIXELS_GRAPH):
                min_dpi_width = MAX_PIXELS_GRAPH / fig_width
                min_dpi_height = MAX_PIXELS_GRAPH / fig_height
                min_dpi = max(50, min(min_dpi_width, min_dpi_height))
                fig.set_dpi(min_dpi)
                logger.info(
                    f"Proactively reduced DPI to {min_dpi} (estimated pixels: {est_width_pixels:.0f}x{est_height_pixels:.0f}, figsize: {fig_width}x{fig_height}) to avoid size limit."
                )

            # Annotation kwargs
            annot_kws = {}
            if self._heatmap_settings.annot_fontsize:
                annot_kws["fontsize"] = self._heatmap_settings.annot_fontsize
            if self._heatmap_settings.annot_color != ANNOTATION_COLOR.AUTO:
                annot_kws["color"] = self._heatmap_settings.annot_color.value

            fmt = ""
            if self._heatmap_settings.annot:
                fmt = f".{self._heatmap_settings.annot_digits}f"
            # Generate heatmap with supressed warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                heatmap = sns.heatmap(
                    data_2d,
                    ax=ax,
                    vmin=min_value,
                    vmax=max_value,
                    cmap=self._general_graph_settings.sequential_color_scheme.value,
                    annot=self._heatmap_settings.annot,
                    fmt=fmt,
                    annot_kws=annot_kws or None,
                    cbar=False,
                    square=self._heatmap_settings.square,
                    linewidths=self._heatmap_settings.linewidths,
                    linecolor=self._heatmap_settings.linecolor,
                    robust=self._heatmap_settings.robust,
                )

            # Set labels to row and column indices
            col_labels = range(n_cols)
            row_labels = range(n_rows)
            start_index = 0 if self._heatmap_settings.start_at_index_0 else 1
            if self._heatmap_settings.use_letter_annotation_x:
                col_labels = [number_to_letters(i) for i in range(n_cols)]  # Always start from A
            else:
                col_labels = range(start_index, n_cols + start_index)

            if self._heatmap_settings.use_letter_annotation_y:
                row_labels = [number_to_letters(i) for i in range(n_rows)]  # Always start from A
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

            if self._general_graph_settings.show_title:
                ax.set_title(title, fontsize=base_font_size, color=self._collage.title_color.value)

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

            plt.tight_layout(pad=1.5)

            logger.debug(f"Heatmap generated successfully for dataset: {dataset_descriptor}")
            return fig

        except Exception as e:
            logger.error(
                f"Failed to generate heatmap for dataset %s: %s",
                dataset_descriptor,
                e,
                exc_info=True,
            )
            return None

    def add_global_colorbar(
        self,
        svg_image: sg.SVGFigure,
        vmin: float,
        vmax: float,
        bar_width=200,
    ) -> sg.SVGFigure:
        """
        Add a global colorbar to the SVG image.

        Args:
            svg_image (sg.SVGFigure): The SVG figure to add colorbar to.
            vmin (float): Minimum value for colorbar.
            vmax (float): Maximum value for colorbar.
            bar_width (int, optional): Width of the colorbar.

        Returns:
            sg.SVGFigure: The SVG figure with added colorbar.
        """
        logger.debug("Adding global colorbar to collage")
        # As values from single dataset hitmaps are either 0 or 1 this method is simplified

        orientation = self._heatmap_settings.cbar_orientation
        if orientation == CBAR_ORIENTATION.HIDE:
            return svg_image  # Return original if no cbar

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

        cmap = self._general_graph_settings.sequential_color_scheme.value

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
            ax, cmap=plt.get_cmap(cmap), norm=norm, orientation=orientation.value
        )

        tick_font_size = max(1, int(self._collage.font_size * 0.618))
        cb.ax.tick_params(labelsize=tick_font_size)
        if self._heatmap_settings.cbar_tick_mode == CBAR_TICK_MODE.HIDE:
            cb.set_ticks([])
        elif vmin == 0 and vmax == 1:  # non-compound hit-maps
            cb.set_ticks([vmin, vmax])

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
            combined_fig = sg.SVGFigure(width=f"{total_width}pt", height=f"{total_height}pt")
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
            combined_fig = sg.SVGFigure(width=f"{total_width}pt", height=f"{total_height}pt")
            collage_root = svg_image.getroot()
            collage_root.moveto(0, 0)
            combined_fig.append(collage_root)
            cbar_root = cbar_fig.getroot()
            cbar_root.moveto(0, collage_height + padding)
            combined_fig.append(cbar_root)
            combined_fig.set_size((f"{total_width}pt", f"{total_height}pt"))

        logger.debug("Global colorbar added successfully")
        return combined_fig

    def on_export_overview_csv(self):
        """
        Handle export of overview data as CSV.

        The CSV structure includes:
            - First row: A header with the attribute name, normalization method (if applicable), and column headers for samples/spots (e.g., "Sample_0_Spot_0" or "Sample_0") followed by a "Total Hits" column.
            - Subsequent rows: One row per dataset, with the dataset ID or name, followed by filtered values (padded with None for uniformity), and the total count of non-NaN values.
        """
        logger.debug("Exporting overview data as CSV")
        try:
            attribute = self._value_extractor.attribute
            normalization_method = self._value_extractor.normalization
            apply_static = self._apply_static_filter_checkbox.value
            apply_dynamic = self._apply_dynamic_filter_checkbox.value
            is_spot_level = attribute not in DATA_STATISTICS_ATTRIBUTES

            if not apply_static and not apply_dynamic:
                logger.info("Could not generate CSV. Please select a filter.")
                return

            if not self._filtered_values:
                logger.info("Could not generate CSV. No datasets left after filtering.")
                return

            # Mimic original spot sample format
            csv_dict = self._filtered_values.copy()
            if is_spot_level:
                for dataset in self._included_datasets:
                    spot_values = []
                    i = 0
                    for sample in dataset.samples:
                        spot_values.append([])
                        for spot in sample.spots:
                            spot_values[-1].append(self._filtered_values[dataset][i])
                            i += 1
                    csv_dict[dataset] = spot_values

            # Add none padding for sample entries
            max_samples = max(len(csv_value_list) for csv_value_list in csv_dict.values())
            padding_entry = [None] if is_spot_level else None
            for csv_value_list in csv_dict.values():
                csv_value_list.extend([padding_entry] * (max_samples - len(csv_value_list)))

            # Add none padding to spot entries
            if is_spot_level:
                for sample in range(max_samples):
                    max_spots = max(
                        len(csv_value_list[sample]) for csv_value_list in csv_dict.values()
                    )
                    for csv_value_list in csv_dict.values():
                        csv_value_list[sample].extend(
                            [None] * (max_spots - len(csv_value_list[sample]))
                        )

            # Add col headers for both spot and sample format
            col_headers = []
            if is_spot_level:
                for sample_idx in range(max_samples):
                    max_spots = max(
                        len(csv_value_list[sample_idx]) for csv_value_list in csv_dict.values()
                    )
                    col_headers.extend(
                        [f"Sample_{sample_idx}_Spot_{spot_idx}" for spot_idx in range(max_spots)]
                    )
            else:
                col_headers = [f"Sample_{i}" for i in range(max_samples)]

            # Add Total hits column header
            col_headers.append("Total Hits")

            # Create CSV title
            csv_title = attribute.value
            if normalization_method != NORMALIZATION.RAW:
                csv_title += f" - Normalized ({normalization_method.value})"
            filters = []
            if apply_static:
                filters.append("static")
            if apply_dynamic:
                filters.append("dynamic")
            if filters:
                csv_title += f" - {', '.join(filters)}"

            # Prepare header row
            header_row = [csv_title] + col_headers

            # Get file path
            root = Tk()
            root.withdraw()
            root.lift()
            root.attributes("-topmost", True)
            root.focus_force()
            default_filename = f"Hitmap_Overview_{csv_title}.csv"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename,
                title="Save Overview CSV As",
            )
            root.attributes("-topmost", False)
            root.destroy()

            if not file_path:
                logger.debug("Overview CSV export cancelled by user")
                return

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(header_row)

                # Write data rows
                for dataset in self._included_datasets:
                    # Get dataset label
                    if self._dataset_descriptor == DATASET_LABEL.ID:
                        dataset_label = dataset.id
                    else:
                        dataset_label = dataset.name

                    # Prepare data values
                    data_values = csv_dict[dataset]

                    if is_spot_level:
                        # Flatten spot-level data for CSV row
                        flattened_values = []
                        for sample_data in data_values:
                            flattened_values.extend(sample_data)
                    else:
                        flattened_values = data_values

                    # Count total hits (non-None, non-NaN values)
                    total_hits = pd.notna(flattened_values).sum()

                    # Create complete row
                    row = [dataset_label] + flattened_values + [total_hits]
                    writer.writerow(row)

            logger.info("Overview CSV exported successfully to %s", file_path)

        except Exception as e:
            logger.error("Failed to export overview CSV: %s", e, exc_info=True)

    def on_export_compound_csv(self):
        """
        Handle export of compound data as CSV.

        The CSV structure includes:
            - First row: A header with the attribute name, normalization method (if applicable), and column headers for samples/spots (e.g., "Sample_i_Spot_i" or "Sample_i").
            - Second row: Lists of dataset IDs or names (semicolon-separated) contributing to each position's compound map.
            - Third row: Counts of datasets contributing to each position in the compound map.
        """
        logger.debug("Exporting compound data as CSV")
        try:
            if not self._compound_map:
                logger.warning("No compound data available for export")
                return

            attribute = self._value_extractor.attribute
            normalization_method = self._value_extractor.normalization
            apply_static = self._apply_static_filter_checkbox.value
            apply_dynamic = self._apply_dynamic_filter_checkbox.value
            is_spot_level = attribute not in DATA_STATISTICS_ATTRIBUTES

            if not apply_static and not apply_dynamic:
                logger.info("Could not generate CSV. Please select a filter.")
                return

            # Reconstruct the compound map structure similar to overview CSV
            if is_spot_level:
                # Reconstruct spot-level structure from flat compound_map
                reconstructed_compound_map = []
                flat_index = 0

                # Calculate total samples across all datasets for proper reconstruction
                max_samples = (
                    max(len(dataset.samples) for dataset in self._included_datasets)
                    if self._included_datasets
                    else 0
                )

                for sample_idx in range(max_samples):
                    sample_spots = []
                    # Find maximum spots for this sample across all datasets
                    max_spots_for_sample = 0
                    for dataset in self._included_datasets:
                        if sample_idx < len(dataset.samples):
                            max_spots_for_sample = max(
                                max_spots_for_sample, len(dataset.samples[sample_idx].spots)
                            )

                    for spot_idx in range(max_spots_for_sample):
                        if flat_index < len(self._compound_map):
                            sample_spots.append(self._compound_map[flat_index])
                            flat_index += 1
                        else:
                            sample_spots.append([])  # Empty list for padding

                    reconstructed_compound_map.append(sample_spots)

                compound_data = reconstructed_compound_map
            else:
                compound_data = self._compound_map

            col_headers = []
            if is_spot_level:
                for sample_idx in range(len(compound_data)):
                    max_spots = len(compound_data[sample_idx]) if compound_data[sample_idx] else 0
                    col_headers.extend(
                        [f"Sample_{sample_idx}_Spot_{spot_idx}" for spot_idx in range(max_spots)]
                    )
            else:
                col_headers = [f"Sample_{i}" for i in range(len(compound_data))]

            # Create CSV title
            csv_title = f"Compound - {attribute.value}"
            if normalization_method != NORMALIZATION.RAW:
                csv_title += f" - Normalized ({normalization_method.value})"
            filters = []
            if apply_static:
                filters.append("static")
            if apply_dynamic:
                filters.append("dynamic")
            if filters:
                csv_title += f" - {', '.join(filters)}"

            header_row = [csv_title] + col_headers

            # Get file path
            root = Tk()
            root.withdraw()
            root.lift()
            root.attributes("-topmost", True)
            root.focus_force()
            default_filename = f"Hitmap_{csv_title}.csv"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename,
                title="Save Compound CSV As",
            )
            root.attributes("-topmost", False)
            root.destroy()
            if not file_path:
                logger.debug("Compound CSV export cancelled by user")
                return

            # Prepare data for CSV
            if is_spot_level:
                # Flatten spot-level data
                flattened_compound_data = []
                for sample_data in compound_data:
                    flattened_compound_data.extend(sample_data)
            else:
                flattened_compound_data = compound_data

            # Create dataset sets row (comma-separated dataset names/IDs)
            sets_row = ["Sets"]
            for position_hits in flattened_compound_data:
                if position_hits:
                    if self._dataset_descriptor == DATASET_LABEL.ID:
                        dataset_labels = [str(dataset.id) for dataset in position_hits]
                    else:
                        dataset_labels = [dataset.name for dataset in position_hits]
                    sets_row.append("; ".join(dataset_labels))
                else:
                    sets_row.append("")

            # Create count row
            count_row = ["Count"] + [
                len(position_hits) for position_hits in flattened_compound_data
            ]

            # Write CSV file
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header_row)
                writer.writerow(sets_row)
                writer.writerow(count_row)

            logger.info("Compound CSV exported successfully to %s", file_path)

        except Exception as e:
            logger.error("Failed to export compound CSV: %s", e, exc_info=True)

    def update_scheme(self, new_scheme: Any) -> None:
        """
        Update the color scheme and refresh analysis.

        Args:
            new_scheme (Any): The new color scheme.
        """
        self._color_scheme = new_scheme
        # Currently this only forces a re-color of our table
        self.update_analysis()

    def reset_module(self) -> Optional[Self]:
        """
        Reset the module to a new instance.

        Returns:
            Optional[Self]: A new instance of the module, or None on error.
        """
        logger.debug("Resetting module")
        try:
            new_module = HitmapModule()
            logger.debug("Module reset successfully")
            return new_module
        except Exception as e:
            logger.error("Failed to reset module: %s", e, exc_info=True)
            return None
