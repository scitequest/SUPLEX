import csv
import io
import logging
import warnings
from tkinter import Tk, filedialog
from typing import Any, Self

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from suplex.config import DEMO
from suplex.martin_interface.dataset import Dataset
from suplex.suplex_modules.submodules.dataset_filters import DatasetFilter
from suplex.suplex_modules.submodules.dataset_sorter import DatasetSorter
from suplex.suplex_modules.submodules.sample_spot_filter import (
    SampleSpotFilter,
    get_normalization_factors,
)
from suplex.suplex_modules.submodules.settings.boxplot_settings import BoxplotSettings
from suplex.suplex_modules.submodules.settings.general_graph_settings import (
    GeneralGraphSettings,
)
from suplex.suplex_modules.submodules.settings.jitterplot_settings import JitterplotSettings
from suplex.suplex_modules.submodules.settings.submodule_settings_constants import (
    ASPECT_RATIO,
    GRID_STYLE,
    JITTER_TYPE,
    OPTION_INSET,
    OPTION_WIDGETS_MAX_WIDTH,
    SCALE_TYPE,
    SEQUENTIAL_COLOR_SCHEME,
    WHISKER_MODE,
    get_aspect_ratio_value,
)
from suplex.suplex_modules.submodules.submodule_constants import (
    DATA_ATTRIBUTES,
    DATA_STATISTICS_ATTRIBUTES,
    DATASET_ATTRIBUTE,
    DATASET_LABEL,
    NORMALIZATION,
    NORMALIZATION_DEFAULT,
)
from suplex.suplex_modules.submodules.submodule_utils import (
    apply_normalization,
    calculate_step_size,
)
from suplex.suplex_modules.submodules.value_extractor import (
    ValueExtractor,
    flatten_list,
    get_flat_value_list,
)
from suplex.suplex_modules.submodules.viability_rules import (
    has_negative_values,
    no_datasets_selected,
)
from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface
from suplex.ui.widget_factory import WidgetFactory

logger = logging.getLogger(__name__)
ABS_MAX_VALUE = 2**16 - 1
MAX_PIXELS_GRAPH = 2**20


class IntensityOverviewModule(SuplexModuleInterface):
    """
    Generates scatterplot overlaid by boxplot for each dataset to analyze intensity profiles.
    Allows experimentation with static thresholds via interactive controls.
    Uses AttributeSelector for flexible attribute selection and supports different normalization modes.
    """

    def __init__(self):
        """
        Initialize the IntensityOverviewModule with default settings and UI elements.
        """
        logger.debug("Initializing IntensityOverviewModule")
        self._datasets = []
        self._color_scheme = None

        self._sorted_datasets = []
        self._included_datasets = []
        self._excluded_datasets = []
        self._sample_threshold_map = {}
        self._spot_threshold_map = {}
        self._filtered_values = {}
        self._unfiltered_values = {}

        self._DEFAULT_HOVER_TEXT = "Visualizes intensity distributions across datasets using an overlay of boxplots and jitterplots."
        self._module_hover_text = self._DEFAULT_HOVER_TEXT

        # UI Elements
        self._value_extractor = None

        self._dataset_filter_checkbox = None
        self._use_displayed_dataset_filter_checkbox = None
        self._apply_threshold_checkbox = None
        self._show_threshold_checkbox = None
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
            sequential_color_scheme=SEQUENTIAL_COLOR_SCHEME.VIRIDIS,
            title="",
            x_label="Values",
            y_label="Datasets",
            max_label_length=20,
            base_font_size=12,
            aspect_ratio=ASPECT_RATIO.AUTO,
            x_scale=SCALE_TYPE.LINEAR,
            x_range=(0, ABS_MAX_VALUE),
            grid_style=GRID_STYLE.TICKS,
            transparency=0.0,
        )

        self._boxplot_settings = BoxplotSettings(show_outliers=False, show_all_options=True)
        self._jitterplot_settings = JitterplotSettings(show_all_options=True)

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
        logger.debug("IntensityOverviewModule initialized successfully")

    def _create_checkbox(self, description: str = "", value: bool = False, indent: bool = False):
        cb = WidgetFactory.checkbox(value=value, description=description, indent=indent)
        cb.layout.width = "auto"
        cb.layout.margin = "0px"
        cb.layout.padding = "0px"
        return cb

    @property
    def module_name(self) -> str:
        """
        Get the name of the module.

        Returns:
            str: The module name.
        """
        return "Intensity Overview"

    @property
    def module_version(self) -> str:
        """
        Get the version of the module.

        Returns:
            str: The module version.
        """
        return "0.6.0"

    @property
    def group_name(self) -> str:
        """
        Get the group name of the module.

        Returns:
            str: The group name.
        """
        return "Vanilla"

    @property
    def button_style(self) -> dict[str, str]:
        """
        Get the style configuration for the module button.

        Returns:
            Dict[str, str]: Dictionary containing button style properties.
        """
        return {"font_color": "#FFFFFF", "button_color": "#28A745", "button_icon": "📊"}

    def check_if_viable(self, datasets: list[Dataset]) -> bool:
        """
        Check if module can work with provided datasets.

        Args:
            datasets (List[Dataset]): List of datasets to check viability against.

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
            str: The hover text.
        """
        return self._module_hover_text

    def initiate_module(self, datasets: list[Dataset], color_scheme: Any) -> widgets.Box:
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

            all_tags = set()
            for dataset in self._datasets:
                all_tags.update(dataset.tags + dataset.suplex_tags)
            all_tags = sorted(list(all_tags))

            # Initialize DatasetSorter with all options and collected tags
            self._dataset_sorter = DatasetSorter(tags=all_tags, num_levels=1, max_num_levels=10)
            included_attributes = (
                DATA_ATTRIBUTES
                + DATA_STATISTICS_ATTRIBUTES
                + [
                    DATASET_ATTRIBUTE.SPOT_COORDINATES_X,
                    DATASET_ATTRIBUTE.SPOT_COORDINATES_Y,
                ]
            )
            self._value_extractor = ValueExtractor(
                attributes=included_attributes,
                normalization_methods=NORMALIZATION_DEFAULT,
                max_reference_index=ABS_MAX_VALUE,
            )

            self._dataset_filter = DatasetFilter(included_attributes=included_attributes)
            self._sample_spot_filter = SampleSpotFilter(
                included_attributes=included_attributes,
                included_normalization_methods=NORMALIZATION_DEFAULT,
            )
            self._sample_threshold_map = self._sample_spot_filter.get_default_sample_map(
                self._included_datasets
            )
            self._spot_threshold_map = self._sample_spot_filter.get_default_spot_map(
                self._included_datasets
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

                if current_tab_title in ["Graph", "Dataset Statistics"]:
                    self.apply_all_filters()

            self._tabs.observe(on_tab_change, names="selected_index")

            # Main layout: controls on left, tabs on right
            module_ui = WidgetFactory.hbox(
                [controls, self._tabs],
                layout=widgets.Layout(height="100%", width="100%", gap="0px", overflow="hidden"),
            )

            logger.debug("Module UI initialized successfully")
            # Initial updates
            self.on_selected_attribute_changed()
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
                value="<h2>Intensity Overview</h2>", width="auto"
            )
            controls_content = WidgetFactory.vbox(
                children=[
                    self._value_extractor.get_ui(),
                    self.create_dataset_filter_section(),
                    self.create_value_filter_section(),
                    self.create_control_button_section(),
                ],
                layout=widgets.Layout(
                    height="100%",
                    width="100%",
                    justify_content="space-between",
                    padding="0px 10px",
                ),
            )
            for widget in self._value_extractor.get_active_widgets():
                widget.observe(lambda b: self.on_selected_attribute_changed(), names="value")

            control_interface = WidgetFactory.vbox(
                children=[title_html, controls_content],
                layout=widgets.Layout(width="400px", height="100%", padding="5px"),
            )
            logger.debug("Main control interface created successfully")
            return control_interface
        except Exception as e:
            logger.error("Failed to create main control interface: %s", e, exc_info=True)
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
            slider.observe(lambda b: self.on_selected_attribute_changed(), names="value")

            def on_use_displayed_dataset_filter_checkbox_changed():
                self._dataset_filter.get_attribute_dropdown().disabled = (
                    self._use_displayed_dataset_filter_checkbox.value
                )
                self.on_selected_attribute_changed()

            self._use_displayed_dataset_filter_checkbox = self._create_checkbox(
                description="Use Same Attribute as Displayed",
                value=True,
            )
            self._use_displayed_dataset_filter_checkbox.observe(
                lambda b: on_use_displayed_dataset_filter_checkbox_changed(), names="value"
            )

            self._dataset_filter_checkbox = self._create_checkbox(
                description="Apply Dataset Filter",
                value=False,
            )
            self._dataset_filter_checkbox.observe(
                lambda b: self.on_selected_attribute_changed(), names="value"
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
            logger.error("Failed to create dataset filter section: %s", e, exc_info=True)
            raise

    def create_value_filter_section(self):
        """
        Create the value filter section UI.

        Returns:
            widgets.Widget: The value filter section widget.
        """
        logger.debug("Creating value filter section")
        try:
            value_threshold_label = WidgetFactory.label("Value Threshold")

            slider = self._sample_spot_filter.get_threshold_range_slider()
            slider.observe(lambda b: self.apply_all_filters(), names="value")

            # Default state
            self._sample_spot_filter.get_attribute_dropdown().disabled = True
            self._sample_spot_filter.get_normalization_dropdown().disabled = True
            self._sample_spot_filter.get_normalization_factor_input().disabled = True

            def on_use_displayed_value_filter_checkbox_changed():
                disabled = self._use_displayed_value_filter_checkbox.value
                self._sample_spot_filter.get_attribute_dropdown().disabled = disabled
                self._sample_spot_filter.get_normalization_dropdown().disabled = disabled
                self._sample_spot_filter.get_normalization_factor_input().disabled = disabled

                # Adjust range since content of slider may change (new attribute or normalization).
                self.on_selected_attribute_changed()

            self._use_displayed_value_filter_checkbox = self._create_checkbox(
                description="Use Same Attribute as Displayed",
                value=True,
            )
            self._use_displayed_value_filter_checkbox.observe(
                lambda b: on_use_displayed_value_filter_checkbox_changed(), names="value"
            )

            # Decides if we use self._filtered_values or self._unfiltered_values for statistics and graph depiction.
            self._apply_threshold_checkbox = self._create_checkbox(
                description="Apply Value Threshold",
                value=False,
            )
            self._apply_threshold_checkbox.observe(lambda b: self.update_analysis(), names="value")

            # Decides if we depict threshold lines. This only affects the graph.
            self._show_threshold_checkbox = self._create_checkbox(
                description="Depict Value Threshold",
                value=True,
            )
            self._show_threshold_checkbox.observe(lambda b: self.update_graph(), names="value")

            spot_threshold_section = WidgetFactory.vbox(
                children=[
                    value_threshold_label,
                    slider,
                    self._use_displayed_value_filter_checkbox,
                    self._apply_threshold_checkbox,
                    self._show_threshold_checkbox,
                ],
                layout=widgets.Layout(gap="5px"),
            )
            logger.debug("Value threshold section created successfully")

            return spot_threshold_section
        except Exception as e:
            logger.error("Failed to create spot threshold section: %s", e, exc_info=True)
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
                disabled=DEMO,
                on_click=lambda b: self.on_export_plot(),
                layout=widgets.Layout(padding="0px"),
                width="100%",
            )

            export_as_tsv_button = WidgetFactory.button_emphasis(
                "Export CSV",
                disabled=DEMO,
                on_click=lambda b: self.on_export_csv(),
                layout=widgets.Layout(margin="0px", padding="0px"),
                width="100%",
            )

            control_button_section = WidgetFactory.hbox(
                children=[export_plot_button, export_as_tsv_button]
            )
            logger.debug("Control button section created successfully")
            return control_button_section
        except Exception as e:
            logger.error("Failed to create control button section: %s", e, exc_info=True)
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

        self._dataset_filter.get_method_dropdown().observe(
            lambda b: self.on_selected_attribute_changed(), names="value"
        )
        self._dataset_filter.get_attribute_dropdown().observe(
            lambda b: self.on_selected_attribute_changed(), names="value"
        )
        self._dataset_filter.get_invert_checkbox().observe(
            lambda b: self.on_selected_attribute_changed(), names="value"
        )

        sample_spot_filter_ui = self._sample_spot_filter.get_ui()

        self._sample_spot_filter.get_attribute_dropdown().observe(
            lambda b: self.on_selected_attribute_changed(), names="value"
        )
        self._sample_spot_filter.get_normalization_dropdown().observe(
            lambda b: self.on_selected_attribute_changed(), names="value"
        )
        self._sample_spot_filter.get_normalization_factor_input().observe(
            lambda b: self.on_selected_attribute_changed(), names="value"
        )

        self._sample_spot_filter.get_invert_checkbox().observe(
            lambda b: self.apply_all_filters(), names="value"
        )
        self._sample_spot_filter.get_sample_affects_spots_checkbox().observe(
            lambda b: self.apply_all_filters(), names="value"
        )
        self._sample_spot_filter.get_spots_affect_sample_checkbox().observe(
            lambda b: self.apply_all_filters(), names="value"
        )
        self._sample_spot_filter.get_sample_filter_mode_dropdown().observe(
            lambda b: self.apply_all_filters(), names="value"
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
                self._boxplot_settings.get_ui(),
                self._jitterplot_settings.get_ui(),
                self._general_graph_settings.get_ui(),
            ],
            layout=widgets.Layout(padding="10px", max_width=OPTION_WIDGETS_MAX_WIDTH),
            gap="10px",
        )

        active_widgets = (
            self._boxplot_settings.get_active_widgets()
            + self._jitterplot_settings.get_active_widgets()
            + self._general_graph_settings.get_active_widgets()
        )

        for widget in active_widgets:
            widget.observe(
                lambda change: setattr(self, "_graph_update_pending", True),
                names="value",
            )

        logger.debug("Settings tab created successfully")
        return settings_tab

    def on_selected_attribute_changed(self):
        """
        Handle changes to selected attribute or normalization.
        """
        logger.debug("Attribute or normalization changed")
        if self._ignore_events:
            return
        self._ignore_events = True

        self._sorted_datasets = self._dataset_sorter.get_sorted_datasets(self._datasets)

        # Visualized
        attribute = self._value_extractor.attribute
        normalization_method = self._value_extractor.normalization

        # Dataset Filter
        dataset_filter_attribute = (
            attribute if self._use_displayed_dataset_filter_checkbox.value else None
        )
        datasets = self._sorted_datasets

        self._dataset_filter.on_filter_changed(
            datasets=datasets, attribute=dataset_filter_attribute
        )
        self.apply_dataset_filter()

        # Value Filter
        value_filter_attribute = (
            attribute if self._use_displayed_value_filter_checkbox.value else None
        )
        value_filter_normalization_method = (
            normalization_method if self._use_displayed_value_filter_checkbox.value else None
        )
        value_filter_normalization_factor = (
            self._value_extractor.custom_factor
            if self._use_displayed_value_filter_checkbox.value
            else None
        )
        if self._dataset_filter_checkbox.value:
            datasets = self._included_datasets

        self._sample_spot_filter.on_filter_params_changed(
            datasets=datasets,
            attribute=value_filter_attribute,
            normalization_method=value_filter_normalization_method,
            normalization_factor=value_filter_normalization_factor,
        )

        if datasets:
            # Axis scaling should always be done in reference to depicted values
            displayed_norm_factors = get_normalization_factors(
                datasets=datasets,
                attribute=attribute,
                normalization_method=normalization_method,
                normalization_factor=self._value_extractor.custom_factor,
            )

            all_values_flat_normalized = []
            for i, dataset in enumerate(datasets):
                values = get_flat_value_list(dataset=dataset, attribute=attribute)
                all_values_flat_normalized += [
                    value / displayed_norm_factors[i] for value in values
                ]

            max_value = np.nanmax(all_values_flat_normalized)
            min_value = np.nanmin(all_values_flat_normalized)
            step_size, decimals = calculate_step_size(min_value=min_value, max_value=max_value)
            readout_format = f".{decimals}f"

            min_range = self._general_graph_settings.get_x_range_min_widget()
            min_range.max = min_value
            min_range.value = min_range.min
            min_range.step = step_size
            min_range.readout_format = readout_format

            max_range = self._general_graph_settings.get_x_range_max_widget()
            max_range.min = max_value
            max_range.value = max_value
            max_range.step = step_size
            max_range.readout_format = readout_format

        self.apply_value_filter()
        self.normalize_values()
        self.update_analysis()

        self._ignore_events = False

    def apply_all_filters(self):
        """
        Apply all filters and update analysis.
        """
        logger.debug("Applying all filters")
        self._sorted_datasets = self._dataset_sorter.get_sorted_datasets(self._datasets)

        self.apply_dataset_filter()
        self.apply_value_filter()
        # We normalize after we filter!
        self.normalize_values()

        self.update_analysis()

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

        spot_filter_attribute = (
            attribute if self._use_displayed_value_filter_checkbox.value else None
        )

        spot_filter_normalization_method = (
            normalization_method if self._use_displayed_value_filter_checkbox.value else None
        )
        spot_filter_normalization_factor = (
            self._value_extractor.custom_factor
            if self._use_displayed_value_filter_checkbox.value
            else None
        )

        datasets = self._sorted_datasets
        if self._dataset_filter_checkbox.value:
            datasets = self._included_datasets

        self._sample_threshold_map, self._spot_threshold_map = (
            self._sample_spot_filter.get_filter_maps(
                datasets=datasets,
                attribute=spot_filter_attribute,
                normalization_method=spot_filter_normalization_method,
                normalization_factor=spot_filter_normalization_factor,
            )
        )

        self._filtered_values = self._sample_spot_filter.extract_filtered_values_from_datasets(
            datasets=datasets,
            attribute=attribute,
            sample_threshold_map=self._sample_threshold_map,
            spot_threshold_map=self._spot_threshold_map,
        )

        self._unfiltered_values = self._sample_spot_filter.extract_filtered_values_from_datasets(
            datasets=datasets, attribute=attribute
        )

    def normalize_values(self):
        """
        Normalize filtered and unfiltered values.
        """
        logger.debug("Normalizing values")
        normalization_method = self._value_extractor.normalization
        normalization_factor = self._value_extractor.custom_factor

        self._filtered_values = apply_normalization(
            value_sets=self._filtered_values,
            normalization_method=normalization_method,
            normalization_factor=normalization_factor,
        )

        self._unfiltered_values = apply_normalization(
            value_sets=self._unfiltered_values,
            normalization_method=normalization_method,
            normalization_factor=normalization_factor,
        )

    def update_analysis(self):
        """
        Update overview, statistics, and graph.
        """
        logger.debug("Updating analysis")
        self.update_overview()
        self.update_dataset_statistics()
        self.update_graph()

    def update_overview(self) -> None:
        """
        Update overview analysis content.
        """
        logger.debug("Updating overview analysis")
        try:
            attribute = self._value_extractor.attribute
            normalization = self._value_extractor.normalization
            norm_factor = self._value_extractor.custom_factor

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
                dataset_filter_attribute_text = self._dataset_filter.get_attribute_dropdown().value

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
                <li><strong>Threshold:</strong> {self._dataset_filter.get_threshold_slider().value}</li>
                <li><strong>Inverted Selection:</strong> {self._dataset_filter.invert}</li>
                <li><strong>Number of Excluded  Sets:</strong> {len(self._excluded_datasets)} / {len(self._datasets)} ({len(self._excluded_datasets) / len(self._datasets) * 100:.1f}%)</li>
                <li><strong>Excluded Sets:</strong> {excluded_set_identifiers}</li>
            </ul>
            """

            value_threshold_title = "Value Threshold"
            if self._dataset_filter_checkbox.value and not self._included_datasets:
                html_content += f"<h3>{value_threshold_title}</h3>"
                html_content += (
                    "<ul><li><strong>No Values Left for Value Filtering</strong></li></ul>"
                )
                self._overview_box.children = [WidgetFactory.html_widget(html_content)]
                return

            if not self._apply_threshold_checkbox.value:
                value_threshold_title += " (Not Applied)"

            value_filter_attribute_text = f"Same as Displayed ({attribute.value})"
            if not self._use_displayed_value_filter_checkbox.value:
                value_filter_attribute_text = (
                    self._sample_spot_filter.get_attribute_dropdown().value
                )

            value_filter_normalization_text = f"Same as Displayed {norm_text}"
            if not self._use_displayed_value_filter_checkbox.value:
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
            filtered_values_mean = np.nanmean(filtered_values_flat) if filtered_values_flat else 0.0
            filtered_values_min = np.nanmin(filtered_values_flat) if filtered_values_flat else 0.0
            filtered_values_max = np.nanmax(filtered_values_flat) if filtered_values_flat else 0.0

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
                <li><strong>Values in Range:</strong> {n_values_included} / {len(flat_flag_list)} ({n_values_included / len(flat_flag_list) * 100:.1f}%)</li>
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
        Update dataset statistics content.
        """
        logger.debug("Updating dataset statistics")
        try:
            # If no filter applied unfiltered = filtered
            value_sets_unfiltered = self._unfiltered_values
            value_sets_used = self._unfiltered_values
            if self._apply_threshold_checkbox.value:
                value_sets_used = self._filtered_values

            dataset_stats = []

            for key in value_sets_used:
                descriptor = key.id if self._dataset_descriptor == DATASET_LABEL.ID else key.name
                n_values = len(value_sets_used[key])
                n_values_total = len(value_sets_unfiltered[key])

                perc_excluded = 0.0
                if n_values_total > 0:
                    n_excluded = n_values_total - n_values
                    perc_excluded = (n_excluded / n_values_total) * 100

                if value_sets_used[key] and not np.all(np.isnan(value_sets_used[key])):
                    stat_mean = np.nanmean(value_sets_used[key])
                    stat_median = np.nanmedian(value_sets_used[key])
                    stat_min = np.nanmin(value_sets_used[key])
                    stat_max = np.nanmax(value_sets_used[key])
                    stat_std = np.nanstd(value_sets_used[key])
                else:
                    stat_mean = np.nan
                    stat_median = np.nan
                    stat_min = np.nan
                    stat_max = np.nan
                    stat_std = np.nan

                dataset_stats.append(
                    {
                        "name": descriptor,
                        "n_values": n_values,
                        "n_values_total": n_values_total,
                        "perc_excluded": perc_excluded,
                        "mean": stat_mean,
                        "median": stat_median,
                        "min": stat_min,
                        "max": stat_max,
                        "std": stat_std,
                    }
                )

            if not dataset_stats:
                logger.debug("No data available for dataset statistics")
                self._dataset_stats_box.children = [
                    WidgetFactory.info_field_error(
                        [WidgetFactory.html_widget("No datasets available.")]
                    )
                ]
                return

            attribute = self._value_extractor.attribute
            normalization = self._value_extractor.normalization
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
                </tr>
            """

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
                </tr>
                """
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
        logger.debug("Generating intensity overview plot")

        # We might want to add a custom progress widget like this later on
        # loading_widget = WidgetFactory.custom_progress(width = 100%, height = 100%)
        # self._plot_box.children = [loading_widget]

        try:
            value_sets = self._unfiltered_values
            if self._apply_threshold_checkbox.value:
                value_sets = self.filter_empty_datasets(self._filtered_values)

            if not value_sets:
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

            fig = self.generate_box_jitter_plot(plot_data=value_sets)

            buffer = io.BytesIO()
            fig.savefig(buffer, format="svg", bbox_inches="tight", transparent=True)
            plt.close(fig)
            buffer.seek(0)
            svg_bytes = buffer.getvalue()
            svg_string = svg_bytes.decode("utf-8")
            # This adjusts svg size to use 100% of the provided width
            svg_string = svg_string.replace(
                "<svg", "<svg style='width: 100%; height: auto; display: block;'", 1
            )
            logger.debug("Plot generated successfully as SVG")

            html_content = f"""
            <div style="width: 100%; height: auto; background: white; box-sizing: border-box;">
                    {svg_string}
            </div>
            """

            html_widget = WidgetFactory.html_widget(
                value=html_content, layout=widgets.Layout(width="100%", height="auto")
            )

            self._plot_box.children = [html_widget]

        except Exception as e:
            logger.error("Failed to generate plot: %s", e, exc_info=True)
            self._plot_box.children = [
                WidgetFactory.info_field_error(
                    [WidgetFactory.html_widget(f"Error generating plot: {str(e)}")]
                )
            ]

    def on_export_plot(self):
        """
        Export the current plot using Tkinter save dialog.
        """
        logger.debug("Exporting plot")
        try:
            value_sets = self._unfiltered_values
            if self._apply_threshold_checkbox.value:
                value_sets = self.filter_empty_datasets(self._filtered_values)

            if not value_sets:
                logger.warning("No data available for export")
                return

            fig = self.generate_box_jitter_plot(plot_data=value_sets)

            buffer = io.BytesIO()
            fig.savefig(
                buffer,
                format="svg",
                dpi=fig.dpi,
                bbox_inches="tight",
            )
            buffer.seek(0)
            plt.close(fig)

            # Tkinter Save-File-Dialog
            root = Tk()
            root.withdraw()
            root.lift()
            root.attributes("-topmost", True)
            root.focus_force()
            default_filename = f"Intensity_Overview_{self._value_extractor.attribute.value}_{self._value_extractor.normalization.value}.svg"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG files", "*.svg")],
                initialfile=default_filename,
                title="Save Plot As",
            )
            root.attributes("-topmost", False)
            root.destroy()
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(buffer.getvalue())
                logger.info("Plot exported successfully to %s", file_path)
            else:
                logger.debug("Plot export cancelled by user")
        except Exception as e:
            logger.error("Failed to export plot: %s", e, exc_info=True)

    def filter_empty_datasets(
        self, value_lists: dict[Dataset, list[float]]
    ) -> dict[Dataset, list[float]]:
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
            and not all(val is None or (val is not None and np.isnan(val)) for val in value_list)
        }

    def get_shortened_label(self, label: str, max_length: int) -> str:
        """
        Shorten a label if it exceeds the maximum length.

        Args:
            label (str): The label to shorten.
            max_length (int): Maximum allowed length.

        Returns:
            str: Shortened label if necessary.
        """
        if len(label) <= max_length:
            return label

        if max_length < 5:
            return label[:max_length]

        side_len = (max_length - 3) // 2
        return f"{label[:side_len]}...{label[-(max_length - 3 - side_len) :]}"

    def generate_box_jitter_plot(self, plot_data: dict[str, list[float]]) -> plt.Figure:
        """
        Generate the actual intensity plot.

        Args:
            plot_data (Dict[str, List[float]]): Data to plot, keyed by dataset.

        Returns:
            plt.Figure: The generated figure.
        """
        logger.debug("Generating box scatter plot with %d datasets", len(plot_data))
        try:
            sns.set_style(self._general_graph_settings.grid_style.value)
            plt.rcParams.update(
                {
                    "font.size": self._general_graph_settings.base_font_size,
                    "axes.titlesize": self._general_graph_settings.title_font_size,
                    "axes.labelsize": self._general_graph_settings.label_font_size,
                    "xtick.labelsize": self._general_graph_settings.tick_font_size,
                    "ytick.labelsize": self._general_graph_settings.tick_font_size,
                }
            )
            n_datasets = len(plot_data)
            if n_datasets == 0:
                n_datasets = 1

            # Inches per dataset
            width_per_dataset = 0.4
            height_per_dataset = 0.3
            left_margin = right_margin = bottom_margin = top_margin = 0.5

            if self._general_graph_settings.swap_axes:
                fig_width = left_margin + right_margin + n_datasets * width_per_dataset
                fig_height = 4 + top_margin + bottom_margin
            else:
                fig_width = 6 + left_margin + right_margin
                fig_height = bottom_margin + top_margin + n_datasets * height_per_dataset

            ar_value = get_aspect_ratio_value(self._general_graph_settings.aspect_ratio)

            if ar_value is not None:
                if self._general_graph_settings.swap_axes:
                    fig_height = fig_width / ar_value
                else:
                    fig_width = fig_height * ar_value

            figsize = (fig_width, fig_height)

            fig, ax = plt.subplots(figsize=figsize)

            # DPI-Downscaling-Logik (analog zu overview_heatmap.py)
            current_dpi = fig.dpi  # Standard-DPI von matplotlib (normalerweise 100)
            est_width_pixels = fig_width * current_dpi
            est_height_pixels = fig_height * current_dpi

            if (est_width_pixels > MAX_PIXELS_GRAPH) or (est_height_pixels > MAX_PIXELS_GRAPH):
                min_dpi_width = MAX_PIXELS_GRAPH / fig_width
                min_dpi_height = MAX_PIXELS_GRAPH / fig_height
                min_dpi = max(
                    50, min(min_dpi_width, min_dpi_height)
                )  # Mindestens 50 DPI, um Qualität zu wahren
                fig.set_dpi(min_dpi)
                logger.info(
                    f"Proactively reduced DPI to {min_dpi} (estimated pixels: {est_width_pixels:.0f}x{est_height_pixels:.0f}, figsize: {fig_width}x{fig_height}) to avoid size limit."
                )

            color_scheme = self._general_graph_settings.sequential_color_scheme.value
            try:
                cmap = plt.colormaps.get_cmap(color_scheme)
            except ValueError:
                logger.warning("Invalid color scheme: %s, falling back to viridis", color_scheme)
                cmap = plt.colormaps.get_cmap("viridis")
            colors = cmap(np.linspace(0, 1, len(plot_data)))

            dataset_labels = [key.id for key in plot_data.keys()]
            if self._dataset_descriptor == DATASET_LABEL.NAME:
                dataset_labels = [key.name for key in plot_data.keys()]

            if self._general_graph_settings.max_label_length:
                max_label_length = self._general_graph_settings.max_label_length
                axis_labels = []
                for label in dataset_labels:
                    axis_labels.append(
                        self.get_shortened_label(label=label, max_length=max_label_length)
                    )

            if self._boxplot_settings.show_boxplot:
                self.create_boxplot(ax, plot_data, colors, axis_labels)

            if self._jitterplot_settings.show_jitterplot:
                self.create_jitterplot(ax, plot_data, colors)

            if self._show_threshold_checkbox.value:
                self.add_thresholds(ax)

            # Setup axes, labels, scales, etc.
            self.setup_axes(ax, plot_data, colors, axis_labels)
            plt.tight_layout(pad=1.5)

            logger.debug("Box scatter plot generated successfully")
            return fig
        except Exception as e:
            logger.error("Failed to generate box scatter plot: %s", e, exc_info=True)
            return None

    def create_boxplot(self, ax, plot_data, colors, axis_labels: list[str] = []):
        """
        Create boxplot on the given axis.

        Args:
            ax: Matplotlib axis to plot on.
            plot_data (Dict[str, List[float]]): Data to plot.
            colors (list): Colors for the boxes.
            axis_labels (list[str]): Labels for the axes. Optional.
        """
        if not axis_labels or len(axis_labels) != len(plot_data):
            axis_labels = plot_data.keys()

        whisker_mode = self._boxplot_settings.whisker_mode
        if whisker_mode == WHISKER_MODE.NONE:
            whis = 0
        elif whisker_mode == WHISKER_MODE.IQR:
            whis = self._boxplot_settings.iqr_factor
        elif whisker_mode == WHISKER_MODE.PERCENTILES:
            whis = [
                self._boxplot_settings.percentile_min,
                self._boxplot_settings.percentile_max,
            ]
        elif whisker_mode == WHISKER_MODE.MIN_MAX:
            whis = [0, 100]

        processed_data = []
        for data in plot_data.values():
            if not data:
                processed_data.append([np.nan])
            else:
                processed_data.append(data)

        # Ignore warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            box_plot = ax.boxplot(
                processed_data,
                patch_artist=True,
                tick_labels=axis_labels,
                widths=self._boxplot_settings.box_width,
                whis=whis,
                showfliers=self._boxplot_settings.show_outliers,
                orientation="vertical" if self._general_graph_settings.swap_axes else "horizontal",
            )
            for patch, color in zip(box_plot["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(self._boxplot_settings.box_alpha)

    def create_jitterplot(self, ax, plot_data, colors):
        """
        Create jitterplot on the given axis.

        Args:
            ax: Matplotlib axis to plot on.
            plot_data (Dict[str, List[float]]): Data to plot.
            colors (list): Colors for the points.
        """
        point_size = self._jitterplot_settings.point_size
        jitter_type = self._jitterplot_settings.jitter_type
        jitter_strength = self._jitterplot_settings.jitter_strength
        point_alpha = self._jitterplot_settings.point_alpha

        for i, values in enumerate(plot_data.values()):
            pos = [i + 1] * len(values)

            if self._general_graph_settings.swap_axes:
                x_axis = pos.copy()
                y_axis = values
                jitter_axis = x_axis
            else:
                x_axis = values
                y_axis = pos.copy()
                jitter_axis = y_axis

            if self._jitterplot_settings.apply_jitter:
                if jitter_type == JITTER_TYPE.UNIFORM:
                    jitter = np.random.uniform(-jitter_strength, jitter_strength, len(values))
                elif jitter_type == JITTER_TYPE.GAUSSIAN:
                    jitter = np.random.normal(0, jitter_strength, len(values))
                else:
                    jitter = np.zeros(len(values))

                jitter_axis = [p + j for p, j in zip(jitter_axis, jitter)]

            if self._general_graph_settings.swap_axes:
                x_axis = jitter_axis
            else:
                y_axis = jitter_axis

            # Supress warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                ax.scatter(
                    x_axis,
                    y_axis,
                    alpha=point_alpha,
                    s=point_size,
                    color=colors[i],
                    edgecolors="black",
                    linewidth=0.5,
                )

    def add_thresholds(self, ax):
        """
        Add threshold lines to the plot if applicable.

        Args:
            ax: Matplotlib axis to add thresholds to.
        """
        if self._general_graph_settings.x_scale != SCALE_TYPE.LINEAR:
            return

        threshold_min, threshold_max = self._sample_spot_filter.get_threshold_range_slider().value
        slider_min = self._sample_spot_filter.get_threshold_range_slider().min
        slider_max = self._sample_spot_filter.get_threshold_range_slider().max

        if self._general_graph_settings.swap_axes:
            if threshold_min > slider_min:
                ax.axhline(y=threshold_min, color="red", linestyle="--", linewidth=2)
            if threshold_max < slider_max:
                ax.axhline(y=threshold_max, color="red", linestyle="--", linewidth=2)
        else:
            if threshold_min > slider_min:
                ax.axvline(x=threshold_min, color="red", linestyle="--", linewidth=2)
            if threshold_max < slider_max:
                ax.axvline(x=threshold_max, color="red", linestyle="--", linewidth=2)

    def setup_axes(self, ax, plot_data, colors, axis_labels: list[str] = []):
        """
        Setup axes, labels, scales, and other plot elements.

        Args:
            ax: Matplotlib axis to setup.
            plot_data (Dict[str, List[float]]): Data used for plotting.
            colors (list): Colors used in the plot.
            axis_labels (list[str]): Labels for the axes. Optional.
        """
        if not axis_labels or len(axis_labels) != len(plot_data):
            axis_labels = plot_data.keys()

        n_datasets = len(plot_data)
        attribute = self._value_extractor.attribute
        normalization = self._value_extractor.normalization

        attribute_display = attribute.value.replace("_", " ").title()
        normalization_suffix = f" ({normalization.value})" if normalization != "raw" else ""

        value_label = self._general_graph_settings.x_label
        dataset_label = self._general_graph_settings.y_label

        positions = list(range(1, n_datasets + 1))

        if self._general_graph_settings.swap_axes:
            ax.set_xscale(SCALE_TYPE.LINEAR.value)
            ax.set_yscale(self._general_graph_settings.x_scale.value)
            ax.set_xlim([0.5, n_datasets + 0.5])
            ax.set_ylim(self._general_graph_settings.x_range)
            ax.set_xticks(positions)
            ax.set_xticklabels(axis_labels, rotation=90 if n_datasets > 10 else 0)
        else:
            ax.set_xscale(self._general_graph_settings.x_scale.value)
            ax.set_yscale(SCALE_TYPE.LINEAR.value)
            ax.set_xlim(self._general_graph_settings.x_range)
            ax.set_ylim([0.5, n_datasets + 0.5])
            ax.set_yticks(positions)
            ax.set_yticklabels(axis_labels, rotation=0)

        show_axis_labels = self._general_graph_settings.show_axis_labels
        ax.set_xlabel(value_label if show_axis_labels else "")
        ax.set_ylabel(dataset_label if show_axis_labels else "")

        if self._general_graph_settings.show_title:
            plot_title = (
                self._general_graph_settings.title
                or f"Intensity Overview: {attribute_display}{normalization_suffix}"
            )
            ax.set_title(plot_title)

        if not self._general_graph_settings.show_axis_ticks:
            ax.set_xticks([])
            ax.set_yticks([])

        if self._general_graph_settings.invert_x_axis:
            ax.invert_xaxis()

        if self._general_graph_settings.invert_y_axis:
            ax.invert_yaxis()

        ax.grid(
            self._general_graph_settings.show_grid,
            alpha=self._general_graph_settings.transparency,
        )

    def on_export_csv(self):
        """
        Export data as CSV using Tkinter save dialog.
        """
        logger.debug("Exporting data as CSV")

        attribute = self._value_extractor.attribute
        normalization_method = self._value_extractor.normalization

        sample_threshold_map = spot_threshold_map = None
        if self._apply_threshold_checkbox.value:
            sample_threshold_map, spot_threshold_map = (
                self._sample_threshold_map,
                self._spot_threshold_map,
            )

        datasets = self._included_datasets
        if not datasets:
            logger.warning("No datasets available for export")
            return

        # Extract filtered values with NaN placeholders from datasets
        csv_valuesets = self._sample_spot_filter.extract_filtered_values_from_datasets(
            datasets=datasets,
            attribute=attribute,
            sample_threshold_map=sample_threshold_map,
            spot_threshold_map=spot_threshold_map,
            outside_replacement_value=float("nan"),
        )

        normalization_factor = self._value_extractor.custom_factor
        csv_valuesets = apply_normalization(
            value_sets=csv_valuesets,
            normalization_method=normalization_method,
            normalization_factor=normalization_factor,
        )

        csv_title = f"{attribute.value}"
        if normalization_method != NORMALIZATION.RAW:
            csv_title += " - Normalized"
        csv_title += f" ({normalization_method.value})"

        root = Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        root.focus_force()
        default_filename = f"Intensity_Data_{attribute.value}_{normalization_method.value}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default_filename,
            title="Save CSV As",
        )

        root.attributes("-topmost", False)
        root.destroy()

        if not file_path:
            logger.debug("CSV export cancelled by user")
            return

        # Write CSV based on attribute type
        if attribute in DATA_STATISTICS_ATTRIBUTES:
            max_len = np.nanmax((len(lst) for lst in csv_valuesets.values()), default=0)
            indices = list(range(max_len))
            head_row = [csv_title] + indices

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(head_row)
                for key, values in csv_valuesets.items():
                    descriptor = (
                        key.id if self._dataset_descriptor == DATASET_LABEL.ID else key.name
                    )
                    row = [descriptor] + list(values)
                    writer.writerow(row)
        else:
            max_samples = 0
            # sample_index -> max_spots
            max_spots_per_sample = {}

            for threshold_map in self._spot_threshold_map.values():
                max_samples = np.nanmax([max_samples, len(threshold_map)])

                for sample_idx, spots in enumerate(threshold_map):
                    current_spots = len(spots)
                    if sample_idx not in max_spots_per_sample:
                        max_spots_per_sample[sample_idx] = current_spots
                    else:
                        max_spots_per_sample[sample_idx] = np.nanmax(
                            [max_spots_per_sample[sample_idx], current_spots]
                        )

            # Generate header with Sample_i_Spot_j format
            header = [csv_title]
            for sample_idx in range(max_samples):
                max_spots = max_spots_per_sample.get(sample_idx, 0)
                for spot_idx in range(max_spots):
                    header.append(f"Sample_{sample_idx}_Spot_{spot_idx}")

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)

                for dataset in csv_valuesets.keys():
                    if dataset not in self._spot_threshold_map:
                        continue

                    descriptor = (
                        dataset.id if self._dataset_descriptor == DATASET_LABEL.ID else dataset.name
                    )
                    row = [descriptor]

                    flattened_values = csv_valuesets[dataset]

                    value_index = 0
                    threshold_map = self._spot_threshold_map[dataset]

                    for sample_idx in range(max_samples):
                        max_spots = max_spots_per_sample.get(sample_idx, 0)

                        if sample_idx < len(threshold_map):
                            sample_spots = len(threshold_map[sample_idx])
                        else:
                            sample_spots = 0

                        for spot_idx in range(max_spots):
                            if spot_idx < sample_spots:
                                if value_index < len(flattened_values):
                                    row.append(flattened_values[value_index])
                                    value_index += 1
                                else:
                                    row.append("")
                            else:
                                row.append("")
                    writer.writerow(row)

        logger.info("CSV exported successfully to %s", file_path)

    def update_scheme(self, new_scheme) -> None:
        """
        Update the color scheme and refresh analysis.

        Args:
            new_scheme: New color scheme to apply.
        """
        self._color_scheme = new_scheme
        # Currently this only forces a re-color of our table
        self.update_analysis()

    def reset_module(self) -> Self | None:
        """
        Reset module to initial state.

        Returns:
            Optional[Self]: New instance of the module or None if reset failed.
        """
        logger.debug("Resetting module")
        try:
            new_module = IntensityOverviewModule()
            logger.debug("Module reset successfully")
            return new_module
        except Exception as e:
            logger.error("Failed to reset module: %s", e, exc_info=True)
            return None
