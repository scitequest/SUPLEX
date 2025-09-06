import ipywidgets as widgets
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Union, Any
from typing_extensions import Self
import io
from tkinter import filedialog, Tk
import numpy as np
import pandas as pd
import logging
import csv

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.viability_rules import no_datasets_selected
from suplex_modules.submodules.value_extractor import (
    ValueExtractor,
    extract_value_list_from_dataset,
    get_flat_value_list,
    flatten_list,
    get_reference_statistics
)
from suplex_modules.submodules.submodule_constants import (
    DATASET_ATTRIBUTE,
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
    NORMALIZATION,
    DATASET_LABEL,
    NORMALIZATION_DEFAULT,
    NORMALIZATION_REFERENCE_POINT
)
from suplex_modules.submodules.dataset_sorter import DatasetSorter
from suplex_modules.submodules.dataset_filters import DatasetFilter
from suplex_modules.submodules.sample_spot_filter import (
    SampleSpotFilter,
    get_normalization_factors,
)
from suplex_modules.submodules.settings.general_graph_settings import (
    GeneralGraphSettings,
)

from suplex_modules.submodules.settings.heatmap_settings import HeatmapSettings
from suplex_modules.submodules.settings.submodule_settings_constants import OPTION_INSET, DIVERGENT_COLOR_SCHEME, ANNOTATION_COLOR, LINE_COLOR, CBAR_ORIENTATION, ANNOTATION_COLOR

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
    get_aspect_ratio_value
)
from suplex_modules.submodules.submodule_utils import get_shortened_label

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

        self._DEFAULT_HOVER_TEXT = "Generates an overview heatmap of all dataset values."
        self._module_hover_text = self._DEFAULT_HOVER_TEXT

        # UI Elements
        self._value_extractor = None
        self._dataset_filter_checkbox = None
        self._use_displayed_dataset_filter_checkbox = None
        self._use_displayed_value_filter_checkbox = None

        self._tabs = None

        self._dataset_sorter = None
        self._dataset_filter = None
        self._sample_spot_filter = None

        self._general_graph_settings = GeneralGraphSettings(
            swap_axes=False,
            invert_x_axis=False,
            invert_y_axis=False,
            show_grid=True,
            show_title=True,
            show_axis_labels=True,
            show_axis_ticks=True,
            include_empty_datasets=False,
            sequential_color_scheme=SEQUENTIAL_COLOR_SCHEME.GREYS,
            divergent_color_scheme=DIVERGENT_COLOR_SCHEME.COOLWARM,
            title="",
            x_label="Positions",
            y_label="Datasets",
            max_label_length=20,
            base_font_size=12,
            aspect_ratio=ASPECT_RATIO.AUTO,
            grid_style=GRID_STYLE.TICKS,
            transparency=0.0,
        )

        highlight_colors = list(ANNOTATION_COLOR)
        highlight_colors.remove(ANNOTATION_COLOR.AUTO)
        highlight_colors.remove(ANNOTATION_COLOR.BLACK)
        highlight_colors.remove(ANNOTATION_COLOR.WHITE)
        
        self._heatmap_settings = HeatmapSettings(
            square = False,
            symmetric_scaling = True,
            annot = False,
            annot_fontsize = 1,
            annot_digits = 0,
            annot_color = ANNOTATION_COLOR.AUTO,
            linewidths = 0,
            cell_size = 0.01,
            linecolor= LINE_COLOR.BLACK,
            robust = False,
            cbar_options = list(CBAR_ORIENTATION),
            start_at_index_0 = True,
            highlight_reference_points = True,
            highlight_colors = highlight_colors
        )
        
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
        logger.debug("OverviewHeatmapModule initialized successfully")

    @property
    def module_name(self) -> str:
        """
        Get the name of the module.

        Returns:
            str: The module name.
        """
        return "Overview Heatmap"

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
        return {"font_color": "#FFFFFF", "button_color": "#87CEEB", "button_icon": "🌡️"}

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

            all_tags = set()
            for dataset in self._datasets:
                all_tags.update(dataset.tags + dataset.suplex_tags)
            all_tags = sorted(list(all_tags))

            # Initialize DatasetSorter with all options and collected tags
            self._dataset_sorter = DatasetSorter(
                tags=all_tags, num_levels=1, max_num_levels=10
            )
            attributes = DATA_ATTRIBUTES + DATA_STATISTICS_ATTRIBUTES + [DATASET_ATTRIBUTE.SPOT_COORDINATES_X, DATASET_ATTRIBUTE.SPOT_COORDINATES_Y]
            
            self._dataset_filter = DatasetFilter(
                included_attributes=attributes
            )
            self._sample_spot_filter = SampleSpotFilter(
                included_attributes=attributes,
                included_normalization_methods = NORMALIZATION_DEFAULT
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
            max_index = max(sum(len(sample.spots) for sample in dataset.samples) for dataset in self._datasets)
            self._value_extractor = ValueExtractor(
                attributes = attributes,
                normalization_methods = normalization_methods,
                max_reference_index = max_index
            )
            
            def on_values_extracted_changed():
                self._ignore_events = True
                attribute = None
                if self._use_displayed_dataset_filter_checkbox.value:
                    attribute = self._value_extractor.attribute
                
                self._dataset_filter.on_filter_changed(
                    datasets=self._datasets, attribute=attribute
                )
                self._ignore_events = False
                self.update_analysis()
            
                
            for widget in self._value_extractor.get_active_widgets():
                widget.observe(lambda b: on_values_extracted_changed(), names="value")
            
            self._value_extractor.get_reference_selector().get_ref_container().observe(
                lambda b: self.update_analysis(),
                names="children"
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
                    self.update_analysis()


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
                value="<h2>Overview Heatmap</h2>", width="auto"
            )
            controls_box = WidgetFactory.vbox(
                children=[
                    self._value_extractor.get_ui(),
                    self.create_dataset_filter_section(),
                ],
                layout=widgets.Layout(
                    height="100%",
                    width="100%",
                ),
                gap = "20px"
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

    def create_dataset_filter_section(self) -> widgets.Widget:
        """
        Create dataset filter configuration section.

        Returns:
            widgets.Widget: The dataset filter section widget.
        """
        logger.debug("Creating dataset filter section")
        try:
            dataset_filter_label = WidgetFactory.label("Dataset Filter:")

            slider = self._dataset_filter.get_threshold_slider()
            slider.observe(
                lambda b: self.update_analysis(), names="value"
            )

            def on_use_displayed_dataset_filter_checkbox_changed():
                self._dataset_filter.get_attribute_dropdown().disabled = (
                    self._use_displayed_dataset_filter_checkbox.value
                )
                self.update_analysis()

            self._use_displayed_dataset_filter_checkbox = WidgetFactory.checkbox(
                description="Use Same Attribute as Displayed",
                value=True,
                indent=False,
                on_change=lambda b: on_use_displayed_dataset_filter_checkbox_changed(),
                layout=widgets.Layout(margin="0px", padding="0px"),
            )

            self._dataset_filter_checkbox = WidgetFactory.checkbox(
                description="Apply Dataset Filter",
                value=False,
                indent=False,
                on_change=lambda b: self.update_analysis(),
                layout=widgets.Layout(margin="0px", padding="0px"),
            )

            dataset_filter_section = WidgetFactory.vbox(
                children=[
                    dataset_filter_label,
                    slider,
                    self._use_displayed_dataset_filter_checkbox,
                    self._dataset_filter_checkbox,
                ]
            )
            logger.debug("Dataset filter section created successfully")
            return dataset_filter_section
        except Exception as e:
            logger.error(
                "Failed to create dataset filter section: %s", e, exc_info=True
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
                layout=widgets.Layout(padding="0px"),
                width="100%",
            )

            export_as_tsv_button = WidgetFactory.button_emphasis(
                "Export CSV",
                on_click=lambda b: self.on_export_csv(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
            )

            control_button_section = WidgetFactory.hbox(
                children=[export_plot_button, export_as_tsv_button],
                height ="40px",
                overflow_y = "visible"
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
            lambda b: self._sample_spot_filter.on_filter_params_changed(datasets=self._datasets), names="value"
        )
        self._sample_spot_filter.get_normalization_dropdown().observe(
            lambda b: self._sample_spot_filter.on_filter_params_changed(datasets=self._datasets), names="value"
        )
        self._sample_spot_filter.get_normalization_factor_input().observe(
            lambda b: self._sample_spot_filter.on_filter_params_changed(datasets=self._datasets), names="value"
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
            self.update_analysis()

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
                self._heatmap_settings.get_ui(),
                self._general_graph_settings.get_ui()
            ],
            layout=widgets.Layout(padding="10px", max_width=OPTION_WIDGETS_MAX_WIDTH),
            gap="10px",
        )

        logger.debug("Settings tab created successfully")
        return settings_tab

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
        attribute = self._value_extractor.attribute
        dataset_filter_attribute = (
            attribute if self._use_displayed_dataset_filter_checkbox.value else None
        )

        self._included_datasets, self._excluded_datasets = (
            self._dataset_filter.get_filtered_datasets(
                datasets=self._sorted_datasets, attribute=dataset_filter_attribute
            )
        )

    def apply_value_filter(self):
        """
        Apply value filter to datasets.
        """
        logger.debug("Applying value filter")
        attribute = self._value_extractor.attribute
        normalization_method = self._value_extractor.normalization

        datasets = self._sorted_datasets
        if self._dataset_filter_checkbox.value:
            datasets = self._included_datasets

        self._sample_threshold_map, self._spot_threshold_map = (
            self._sample_spot_filter.get_filter_maps(
                datasets=datasets
            )
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
                datasets=datasets, attribute=attribute,
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
            if not self._dataset_filter_checkbox.value:
                dataset_filter_title += " (Not Applied) "
            dataset_filter_title += f": {dataset_filter_method.value}"

            dataset_filter_attribute_text = f"Same as Displayed ({attribute.value})"
            if not self._use_displayed_dataset_filter_checkbox.value:
                dataset_filter_attribute_text = (
                    self._dataset_filter.attribute
                )

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
            if self._dataset_filter_checkbox.value and not self._included_datasets:
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
            is_reference_norm = normalization in NORMALIZATION_REFERENCE_POINT and len(self._value_extractor.references) > 0

            for dataset in self._sorted_datasets:
                values = self._filtered_values.get(dataset, [])
                unfiltered_values = self._unfiltered_values.get(dataset, [])  # For reference stats

                if not values:
                    continue

                n_values = len(values)
                n_values_total = sum(len(sample.spots) for sample in dataset.samples)
                perc_excluded = (
                    (1 - n_values / n_values_total) * 100 if n_values_total > 0 else 0
                )

                stat_mean = np.nanmean(values)
                stat_median = np.nanmedian(values)
                stat_min = np.nanmin(values)
                stat_max = np.nanmax(values)
                stat_std = np.nanstd(values)

                stat = {
                    "name": dataset.id if self._dataset_descriptor == DATASET_LABEL.ID else dataset.name,
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
                    ref_stats = get_reference_statistics(unfiltered_values, self._value_extractor.references)
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
        logger.debug("Generating overview heatmap")

        # Catches edge case: no references selected in reference point method
        if self._value_extractor.normalization in NORMALIZATION_REFERENCE_POINT and len(self._value_extractor.references) == 0:
            html_str = f"Please select reference indices to generate a plot."
            self._plot_box.children = [
                WidgetFactory.info_field_error(
                    [WidgetFactory.html_widget(html_str)]
                )
            ]
            return
        
        try:
            value_lists = self._filtered_values

            if not self._general_graph_settings.include_empty_datasets:
                value_lists = {
                    key: value_list for key, value_list in value_lists.items() 
                    if value_list and not all(val is None or (val is not None and np.isnan(val)) for val in value_list)
                }

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

            fig = self.generate_heatmap(plot_data=value_lists)

            # Preview as png
            buffer = io.BytesIO()
            fig.savefig(
                buffer, 
                format="png", 
                bbox_inches="tight", 
                dpi=fig.dpi)
            buffer.seek(0)
            img_bytes = buffer.getvalue()
            plt.close(fig)  # Close the figure to free memory
            logger.debug("Plot generated successfully as PNG")
    
            image_widget = widgets.Image(
                value=img_bytes, format="png", width="100%", height="auto"
            )
    
            self._plot_box.children = [image_widget]

        except Exception as e:
            html_str = f"Error generating plot: {str(e)}"
            if "Image size" in str(e) and "too large" in str(e):
                html_str = "Could not generate plot, please reduce dimensions."
                logger.warning("Failed to generate plot: %s", e, exc_info=True)
            else:
                logger.error("Failed to generate plot: %s", e, exc_info=True)
                
            self._plot_box.children = [
                WidgetFactory.info_field_error(
                    [WidgetFactory.html_widget(html_str)]
                )
            ]

    def on_export_plot(self):
        """
        Export the current plot using Tkinter save dialog.
        """
        if self._value_extractor.normalization in NORMALIZATION_REFERENCE_POINT and len(self._value_extractor.references) == 0:
            logger.info("Could not export plot since no indices for export were selected.")
            return
            
        logger.debug("Exporting plot")
        try:
            value_lists = self._filtered_values

            if not self._general_graph_settings.include_empty_datasets:
                value_lists = {
                    key: value_list for key, value_list in value_lists.items() if value_list
                }

            if not value_lists:
                logger.warning("No data available for export")
                return

            fig = self.generate_heatmap(
                plot_data=value_lists
            )

            # Export as SVG
            buffer = io.BytesIO()
            fig.savefig(
                buffer,
                format="svg",
                bbox_inches="tight",
                dpi = fig.dpi
            )
            buffer.seek(0)
            plt.close(fig)

            # Tkinter Save-File-Dialog
            root = Tk()
            root.withdraw()
            default_filename = f"intensity_overview_{self._value_extractor.attribute.value}_{self._value_extractor.normalization.value}.svg"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG files", "*.svg")],
                initialfile=default_filename,
                title="Save Plot As",
            )

            if file_path:
                with open(file_path, "wb") as f:
                    f.write(buffer.getvalue())
                logger.info("Plot exported successfully to %s", file_path)
            else:
                logger.debug("Plot export cancelled by user")
        except Exception as e:
            if "Image size" in str(e) and "too large" in str(e):
                logger.warning("Failed to generate plot: %s", e, exc_info=True)   
            logger.error("Failed to export plot: %s", e, exc_info=True)

    def get_data_matrix(self, value_lists: Dict[Dataset, List[float]]):
        if not value_lists:
            raise ValueError("No data provided for heatmap generation")
   
        # Prepare data: Find max length and create 2D array with NaN padding
        max_len = max(len(values) for values in value_lists.values())
        data_matrix = np.full((len(value_lists), max_len), np.nan)

        return data_matrix

    def generate_heatmap(self, plot_data: Dict[Dataset, List[float]]) -> plt.Figure:
        """
        Generates a heatmap where each row corresponds to a dataset's value list.
        
        Args:
            plot_data (Dict[Dataset, List[float]]): Dictionary with datasets as keys and flattened value lists as values.
        
        Returns:
            plt.Figure: The generated matplotlib figure.
        """
        logger.debug("Generating heatmap")
        
        data_matrix = self.get_data_matrix(value_lists = plot_data)
        
        datasets = list(plot_data.keys())
        for i, dataset in enumerate(datasets):
            values = plot_data[dataset]
            data_matrix[i, :len(values)] = values
        
        # Create DataFrame for seaborn
        df = pd.DataFrame(data_matrix)
        
        # Dataset labels (y-axis by default)
        max_label_length = self._general_graph_settings.max_label_length
        y_labels = [
            get_shortened_label(
                dataset.id if self._dataset_descriptor == DATASET_LABEL.ID else dataset.name,
                max_label_length
            ) for dataset in datasets
        ]
        
        # Position labels (x-axis by default)
        max_len = data_matrix.shape[1]
        start_index = 0 if self._heatmap_settings.start_at_index_0 else 1
        x_labels = list(range(start_index, max_len + start_index))
        
        # Assign labels to DataFrame
        df.index = y_labels
        df.columns = x_labels
        
        # Handle swap axes
        if self._general_graph_settings.swap_axes:
            df = df.T
            # Swap labels
            temp = x_labels
            x_labels = y_labels
            y_labels = temp
        
        # Create figure
        ar_value = get_aspect_ratio_value(self._general_graph_settings.aspect_ratio)
        
        # Estimate figsize based on data dimensions
        n_rows, n_cols = df.shape
        base_size = self._heatmap_settings.cell_size
        fig_width = max(5, n_cols * base_size)
        fig_height = max(5, n_rows * base_size)
        
        if ar_value is not None:
            fig_height = fig_width / ar_value  # Adjust height to match aspect ratio
        
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
            logger.info(f"Proactively reduced DPI to {min_dpi} (estimated pixels: {est_width_pixels:.0f}x{est_height_pixels:.0f}, figsize: {fig_width}x{fig_height}) to avoid size limit.")
        
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
                # This effectiveley neutralizes center
                finite_data = data_matrix[~np.isnan(data_matrix)]
                if len(finite_data) > 0:
                    delta_min = abs(np.min(finite_data) - center)
                    delta_max = abs(np.max(finite_data) - center)
                    max_delta = max(delta_min, delta_max)
                    
                    vmin = center - max_delta
                    vmax = center + max_delta

        show_cbar = self._heatmap_settings.cbar_orientation in [CBAR_ORIENTATION.VERTICAL, CBAR_ORIENTATION.HORIZONTAL]
        cbar_kws = None
        if show_cbar:
            cbar_kws = {"orientation": self._heatmap_settings.cbar_orientation.value}
        
        sns_heatmap_kwargs = {
        "ax": ax,
        "cmap": cmap,
        "vmin": vmin,
        "vmax": vmax,
        "center": center,
        "square": self._heatmap_settings.square,
        "annot": self._heatmap_settings.annot,
        "fmt": f".{self._heatmap_settings.annot_digits}f" if self._heatmap_settings.annot else "",
        "annot_kws": {"fontsize": self._heatmap_settings.annot_fontsize} if self._heatmap_settings.annot else None,
        "linewidths": self._heatmap_settings.linewidths,
        "linecolor": self._heatmap_settings.linecolor,
        "robust": self._heatmap_settings.robust,
        "cbar": show_cbar,
        "cbar_kws": cbar_kws,
        }

        # Heatmaps resolve auto internally
        annot_color = self._heatmap_settings.annot_color
        if self._heatmap_settings.annot and annot_color != ANNOTATION_COLOR.AUTO:
            sns_heatmap_kwargs["annot_kws"] = {"color": annot_color.value}
        
        heatmap = sns.heatmap(df, **sns_heatmap_kwargs)

        # Changes labels to σ notation if gaussian option was used
        if show_cbar and self._value_extractor.normalization in [NORMALIZATION.BY_POSITION_GAUSSIAN_ABSOLUTE, NORMALIZATION.BY_POSITION_GAUSSIAN_PARTIAL]:
            cbar = heatmap.collections[0].colorbar
            
            current_ticks = cbar.get_ticks()
            # Only depict whole numbers
            allowed_ticks = [-3,-2,-1,0,1,2,3]
            # Prevents overflowing ticks
            vmin, vmax = cbar.mappable.get_clim()
            integer_ticks = [t for t in current_ticks if t in allowed_ticks and vmin <= t <= vmax]

            # Change to σ notation
            labels = [f"−σ{int(-t)}" if t < 0 else f"σ{int(t)}" if t > 0 else "0" for t in integer_ticks]
            
            cbar.set_ticks(integer_ticks)
            cbar.set_ticklabels(labels)
        
        # Apply general settings
        if self._general_graph_settings.show_title:
            ax.set_title(self._general_graph_settings.title or "Overview Heatmap")
        
        if self._general_graph_settings.show_axis_labels:
            ax.set_xlabel(self._general_graph_settings.x_label or "Positions")
            ax.set_ylabel(self._general_graph_settings.y_label or "Datasets")
        else:
            ax.set_xlabel("")
            ax.set_ylabel("")
        
        if not self._general_graph_settings.show_axis_ticks:
            ax.set_xticks([])
            ax.set_yticks([])
        
        if self._general_graph_settings.invert_x_axis:
            ax.invert_xaxis()
        
        if self._general_graph_settings.invert_y_axis:
            ax.invert_yaxis()
        
        # Transparency: Apply alpha to the heatmap patches
        alpha = 1.0 - self._general_graph_settings.transparency
        for patch in ax.patches:
            r, g, b, a = patch.get_facecolor()
            patch.set_facecolor((r, g, b, alpha))
        
        # Font sizes
        base_font_size = self._general_graph_settings.base_font_size
        plt.rcParams.update({"font.size": base_font_size})
        ax.title.set_fontsize(base_font_size + 2)  # Title slightly larger
        ax.xaxis.label.set_fontsize(base_font_size)
        ax.yaxis.label.set_fontsize(base_font_size)
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontsize(base_font_size - 2)
        
        # Grid style: But heatmap already has lines, perhaps adjust
        sns.set_style(self._general_graph_settings.grid_style.value)
        
        fig.tight_layout()
        
        # Colors reference point ticks red
        if self._heatmap_settings.highlight_reference_points:
            reference_points = self._value_extractor.references
            if not self._heatmap_settings.start_at_index_0:
                reference_points = [reference + 1 for reference in reference_points]
            ticks = ax.get_xticklabels()
            if self._general_graph_settings.swap_axes:
                ticks = ax.get_yticklabels()
            for tick in ticks:
                try:
                    tick_value = int(tick.get_text())
                    if tick_value in reference_points:
                        tick.set_color(self._heatmap_settings.highlight_color.value)
                except ValueError:
                    pass
                    
        logger.debug(f"Heatmap generated successfully, figsize: {fig_width}x{fig_height}, dpi: {fig.dpi})")
        return fig

    def on_export_csv(self):
        """
        Export data as CSV using Tkinter save dialog.
        """
        if self._value_extractor.normalization in NORMALIZATION_REFERENCE_POINT and len(self._value_extractor.references) == 0:
            logger.info("Could not export csv since no indices for export were selected.")
            return
            
        logger.debug("Exporting data as CSV")
        try:
            value_lists = self._filtered_values
    
            if not self._general_graph_settings.include_empty_datasets:
                value_lists = {
                    key: value_list for key, value_list in value_lists.items() if value_list
                }
    
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
                data_matrix[i, :len(values)] = values
    
            # Indices for columns (analogous to heatmap x_labels)
            max_len = data_matrix.shape[1]
            start_index = 0 if self._heatmap_settings.start_at_index_0 else 1
            indices = list(range(start_index, max_len + start_index))
    
            # Header row
            header = [csv_title] + indices
    
            # Tkinter Save-File-Dialog
            root = Tk()
            root.withdraw()
            default_filename = f"overview_heatmap_{attribute.value}_{normalization.value}.csv"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename,
                title="Save CSV As",
            )
    
            if not file_path:
                logger.debug("CSV export cancelled by user")
                return
    
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
    
                for i, dataset in enumerate(datasets):
                    descriptor = (
                        dataset.id if self._dataset_descriptor == DATASET_LABEL.ID else dataset.name
                    )
                    row = [descriptor] + ['' if np.isnan(val) else val for val in data_matrix[i]]
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