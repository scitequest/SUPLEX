# SUPLEX Module Development Guide

**SUPLEX** is a modular Python application for analyzing MARTin microarray data. Modules extend SUPLEX with custom analysis, visualization, and export functionality.

This guide explains how to develop new modules that integrate seamlessly into the SUPLEX ecosystem.

## Table of Contents

1. [Module Interface](#module-interface)
2. [Data Structure](#data-structure)
3. [UI Components (WidgetFactory)](#ui-components-widgetfactory)
4. [Submodules](#submodules)
5. [Complete Module Example](#complete-module-example)
6. [Common Patterns](#common-patterns)
7. [Debugging Tips](#debugging-tips)
8. [Best Practices](#best-practices)
9. [Deployment](#deployment)

---

## Module Interface

All modules must inherit from `SuplexModuleInterface`.

```python
from typing import List, Optional, Any
from typing_extensions import Self

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
import ipywidgets as widgets
```

### Required Properties and Methods

```python
class YourModule(SuplexModuleInterface):

    @property
    def module_name(self) -> str:
        """Unique name shown in the module selection UI."""
        return "Your Module Name"

    @property
    def module_version(self) -> str:
        """Semantic version of the module."""
        return "1.0.0"

    @property
    def group_name(self) -> str:
        """Category for grouping in the UI (e.g. 'Analysis', 'Visualization', 'Export')."""
        return "Analysis"

    @property
    def button_style(self) -> dict:
        """Styling information for the module button."""
        return {
            "font_color": "#FFFFFF",
            "button_color": "#2E86AB",
            "button_icon": "📊"   # Emoji or icon path
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        """Return True if this module can work with the given datasets."""
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        """Tooltip text shown when hovering over the module button."""
        return "Description of what this module does."

    def initiate_module(self, datasets: List[Dataset], color_scheme) -> Any:
        """
        Main entry point. Creates and returns the module's UI.
        
        Args:
            datasets: List of selected Dataset objects
            color_scheme: Current color scheme for theming
        """
        # Build and return your UI here
        pass

    def update_scheme(self, new_scheme) -> Optional[Self]:
        """Called when the user changes the color scheme. Usually can be left empty."""
        return None

    def reset_module(self) -> Optional[Self]:
        """Return a fresh instance of this module. Used when re-launching."""
        return YourModule()
```

### Important Notes

- `initiate_module` now receives a `color_scheme` parameter. Use it for consistent theming.
- `reset_module()` should return a **new instance** of your module (not `self`).
- `check_if_viable()` is called before showing the module to the user.

---

## Data Structure

### Dataset Hierarchy

```
Project
└── Dataset
    ├── metadata: Metadata | None
    ├── general_parameters: GeneralParameters | None
    ├── samples: List[Sample]
    │   ├── spots: List[Spot]
    │   └── data_statistics: DataStatistics | None
    └── suplex_file: dict
```

### Commonly Used Dataset Attributes

```python
dataset.measure_date            # datetime | None
dataset.image_creation_date     # datetime | None
dataset.tags                    # List[str]
dataset.suplex_tags             # List[str]
dataset.samples                 # List[Sample]
dataset.metadata                # Metadata | None
dataset.general_parameters      # GeneralParameters | None
```

### Working with Samples and Spots

```python
for sample in dataset.samples:
    print(f"Sample has {len(sample.spots)} spots")
    
    if sample.data_statistics:
        print(f"Adjusted average: {sample.data_statistics.adjusted_average}")

    for spot in sample.spots:
        print(f"Mean: {spot.mean_val}, Row: {spot.row}, Col: {spot.col}")
```

### Metadata Access

```python
if dataset.metadata:
    print(dataset.metadata.pat_id)
    print(dataset.metadata.name)
    print(dataset.metadata.tags)
    
    for incubation in dataset.metadata.incubations:
        print(incubation.solution)
```

---

## UI Components (WidgetFactory)

Import the factory:

```python
from ui.widget_factory import WidgetFactory
```

### Common Widgets

```python
# Buttons
button = WidgetFactory.button_default("Click me", on_click=callback)
button = WidgetFactory.button_emphasis("Important", icon="🔥")
button = WidgetFactory.button_success("Save")
button = WidgetFactory.button_danger("Delete")

# Inputs
text = WidgetFactory.text_input(value="", description="Name:", on_change=callback)
number = WidgetFactory.number_input(value=10, min_value=0, max_value=100)
dropdown = WidgetFactory.dropdown(options=["A", "B", "C"], value="A")
checkbox = WidgetFactory.checkbox(value=False, description="Enable")
slider = WidgetFactory.slider(value=50, min_value=0, max_value=100)

# Containers
vbox = WidgetFactory.vbox(children=[widget1, widget2], gap="10px")
hbox = WidgetFactory.hbox(children=[widget1, widget2], gap="15px")
tabs = WidgetFactory.tab(children=[tab1, tab2], titles=["Tab 1", "Tab 2"])

# Info messages
info = WidgetFactory.info_field_success([WidgetFactory.html_widget("Success!")])
warning = WidgetFactory.info_field_warning([WidgetFactory.html_widget("Warning")])
```

---

## Submodules

SUPLEX provides reusable UI components for dataset and tag selection.

### DatasetSelector

```python
from suplex_modules.submodules.dataset_selector import DatasetSelector
from suplex_modules.submodules.submodule_constants import DATASET_SELECTOR_MODE, DATASET_LABEL

selector = DatasetSelector(
    datasets=datasets,
    mode=DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND,
    label_parts=[DATASET_LABEL.NAME, DATASET_LABEL.MEASURE_DATE]
)

ui_element = selector.get_ui_element()
selected_datasets = selector.get_selected_datasets()
```

### TagSelector

```python
from suplex_modules.submodules.tag_selector import TagSelector

tag_selector = TagSelector(datasets)
ui = tag_selector.get_ui_element()

tagged_datasets = tag_selector.get_tagged_datasets_any()
```

---

## Complete Module Example

Below is a complete, working example of a simple analysis module.

```python
import ipywidgets as widgets
from typing import List, Optional, Any
from typing_extensions import Self

from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
from ui.widget_factory import WidgetFactory
from suplex_modules.submodules.dataset_selector import DatasetSelector
from suplex_modules.submodules.submodule_constants import DATASET_SELECTOR_MODE, DATASET_LABEL


class SimpleAnalysisModule(SuplexModuleInterface):
    """Example module that performs basic statistics on selected datasets."""

    def __init__(self):
        self._datasets: List[Dataset] = []
        self._dataset_selector: Optional[DatasetSelector] = None
        self._results_container: Optional[widgets.Widget] = None

    @property
    def module_name(self) -> str:
        return "Simple Analysis"

    @property
    def module_version(self) -> str:
        return "1.0.0"

    @property
    def group_name(self) -> str:
        return "Analysis"

    @property
    def button_style(self) -> dict:
        return {
            "font_color": "#FFFFFF",
            "button_color": "#2E86AB",
            "button_icon": "📊"
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        return len(datasets) > 0 and any(d.metadata is not None for d in datasets)

    def get_module_hover_text(self) -> str:
        return "Performs basic statistical analysis on selected datasets."

    def initiate_module(self, datasets: List[Dataset], color_scheme) -> widgets.Widget:
        self._datasets = datasets

        header = WidgetFactory.html_widget(
            "<h2 style='color: #2E86AB;'>Simple Analysis Module</h2>"
        )

        self._dataset_selector = DatasetSelector(
            datasets=datasets,
            mode=DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND,
            label_parts=[DATASET_LABEL.NAME, DATASET_LABEL.MEASURE_DATE]
        )

        analyze_btn = WidgetFactory.button_emphasis(
            "Analyze", icon="🔍", on_click=self._on_analyze
        )

        self._results_container = WidgetFactory.vbox(
            children=[WidgetFactory.html_widget("<p>Select datasets and click Analyze.</p>")],
            height="300px"
        )

        controls = WidgetFactory.vbox([analyze_btn], gap="10px")

        content = WidgetFactory.hbox([
            self._dataset_selector.get_ui_element(),
            WidgetFactory.vbox([controls, self._results_container])
        ])

        return WidgetFactory.vbox([header, content], gap="20px")

    def _on_analyze(self, button):
        selected = self._dataset_selector.get_selected_datasets()

        if not selected:
            self._results_container.children = [
                WidgetFactory.info_field_warning([
                    WidgetFactory.html_widget("Please select at least one dataset.")
                ])
            ]
            return

        # Perform simple analysis
        html = "<h3>Results</h3>"
        for ds in selected:
            total_spots = sum(len(s.spots) for s in ds.samples)
            html += f"<p><b>{ds.metadata.name if ds.metadata else 'Unknown'}</b>: {total_spots} spots</p>"

        self._results_container.children = [
            WidgetFactory.info_field_success([WidgetFactory.html_widget(html)])
        ]

    def update_scheme(self, new_scheme) -> Optional[Self]:
        return None

    def reset_module(self) -> Optional[Self]:
        return SimpleAnalysisModule()
```

---

## Common Patterns

### Aggregating Data Across Datasets

```python
all_spots = []
for dataset in datasets:
    for sample in dataset.samples:
        all_spots.extend(sample.spots)

mean_values = [spot.mean_val for spot in all_spots]
average = sum(mean_values) / len(mean_values) if mean_values else 0
```

### Filtering Datasets

```python
from datetime import datetime, timedelta

# Filter by recent date
recent = [d for d in datasets if d.measure_date and d.measure_date > datetime.now() - timedelta(days=30)]

# Filter by tag
control_datasets = [d for d in datasets if "control" in d.tags]
```

### Exporting Data

```python
import pandas as pd

def export_spots_to_csv(datasets, filename="results.csv"):
    records = []
    for ds in datasets:
        for sample in ds.samples:
            for spot in sample.spots:
                records.append({
                    "dataset": ds.metadata.name if ds.metadata else "Unknown",
                    "row": spot.row,
                    "col": spot.col,
                    "mean": spot.mean_val,
                    "normalized": spot.normalized_mean
                })
    pd.DataFrame(records).to_csv(filename, index=False)
```

---

## Debugging Tips

```python
def inspect_dataset(dataset):
    print(f"Name: {dataset.metadata.name if dataset.metadata else 'Unknown'}")
    print(f"Samples: {len(dataset.samples)}")
    print(f"Total spots: {sum(len(s.spots) for s in dataset.samples)}")
    print(f"Tags: {dataset.tags}")
```

---

## Best Practices

- Always check if `dataset.metadata` or `dataset.general_parameters` is `None`.
- Use `WidgetFactory` for consistent styling.
- Keep `initiate_module()` reasonably fast — heavy computation should happen on button click.
- Return a **new instance** from `reset_module()`.
- Use the `color_scheme` parameter passed to `initiate_module()` for theming when possible.
- Prefer `DatasetSelector` and `TagSelector` over building custom selection UIs.

---

## Deployment

1. Save your module as a `.py` file.
2. Place it in one of these locations:
   - `src/suplex_modules/vanilla/` — for standard modules
   - `src/suplex_modules/custom/` — for user-created modules (create the folder if needed)
3. Modules are automatically discovered at startup via `module_loader.py`.

### Quick Test

```python
from your_module import YourModule

module = YourModule()
print(module.module_name)
print(module.check_if_viable(your_test_datasets))
```

---

This guide reflects the current architecture of SUPLEX. When in doubt, refer to existing modules in `src/suplex_modules/` as reference implementations.