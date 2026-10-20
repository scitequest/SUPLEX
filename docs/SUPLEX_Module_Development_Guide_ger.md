# SUPLEX Modulentwicklungsleitfaden

**SUPLEX** ist eine modulare Python-Anwendung zur Analyse von MARTin-Mikroarray-Daten. Module erweitern SUPLEX um eigene Analyse-, Visualisierungs- und Exportfunktionen.

Dieser Leitfaden erklärt, wie Sie neue Module entwickeln, die sich nahtlos in das SUPLEX-System integrieren.

## Inhaltsverzeichnis

1. [Modul-Schnittstelle](#modul-schnittstelle)
2. [Datenstruktur](#datenstruktur)
3. [UI-Komponenten (WidgetFactory)](#ui-komponenten-widgetfactory)
4. [Submodule](#submodule)
5. [Vollständiges Modul-Beispiel](#vollständiges-modul-beispiel)
6. [Häufige Muster](#häufige-muster)
7. [Debugging-Tipps](#debugging-tipps)
8. [Best Practices](#best-practices)
9. [Bereitstellung](#bereitstellung)

---

## Modul-Schnittstelle

Alle Module müssen von `SuplexModuleInterface` erben.

```python
from typing import List, Optional, Any
from typing_extensions import Self

from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface
from suplex.martin_interface.dataset import Dataset
import ipywidgets as widgets
```

### Erforderliche Eigenschaften und Methoden

```python
class IhrModul(SuplexModuleInterface):

    @property
    def module_name(self) -> str:
        """Eindeutiger Name, der in der Modulauswahl angezeigt wird."""
        return "Ihr Modulname"

    @property
    def module_version(self) -> str:
        """Semantische Version des Moduls."""
        return "1.0.0"

    @property
    def group_name(self) -> str:
        """Kategorie zur Gruppierung in der Oberfläche (z. B. 'Analysis', 'Visualization', 'Export')."""
        return "Analysis"

    @property
    def button_style(self) -> dict:
        """Styling-Informationen für den Modul-Button."""
        return {
            "font_color": "#FFFFFF",
            "button_color": "#2E86AB",
            "button_icon": "📊"   # Emoji oder Pfad zu einer Icon-Datei
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        """Gibt True zurück, wenn das Modul mit den übergebenen Datensätzen arbeiten kann."""
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        """Tooltip-Text, der beim Hovern über den Modul-Button angezeigt wird."""
        return "Beschreibung, was dieses Modul macht."

    def initiate_module(self, datasets: List[Dataset], color_scheme) -> Any:
        """
        Haupt-Einstiegspunkt. Erzeugt und gibt die Benutzeroberfläche des Moduls zurück.
        
        Args:
            datasets: Liste der ausgewählten Dataset-Objekte
            color_scheme: Aktuelles Farbschema für das Thema
        """
        # Hier Ihre UI aufbauen
        pass

    def update_scheme(self, new_scheme) -> Optional[Self]:
        """Wird aufgerufen, wenn der Benutzer das Farbschema ändert. Kann meist leer bleiben."""
        return None

    def reset_module(self) -> Optional[Self]:
        """Gibt eine frische Instanz dieses Moduls zurück. Wird beim erneuten Start verwendet."""
        return IhrModul()
```

### Wichtige Hinweise

- `initiate_module` erhält jetzt zusätzlich den Parameter `color_scheme`. Nutzen Sie ihn für ein konsistentes Design.
- `reset_module()` sollte eine **neue Instanz** Ihres Moduls zurückgeben (nicht `self`).
- `check_if_viable()` wird aufgerufen, bevor das Modul dem Benutzer angezeigt wird.

---

## Datenstruktur

### Dataset-Hierarchie

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

### Häufig verwendete Dataset-Attribute

```python
dataset.measure_date            # datetime | None
dataset.image_creation_date     # datetime | None
dataset.tags                    # List[str]
dataset.suplex_tags             # List[str]
dataset.samples                 # List[Sample]
dataset.metadata                # Metadata | None
dataset.general_parameters      # GeneralParameters | None
```

### Arbeiten mit Samples und Spots

```python
for sample in dataset.samples:
    print(f"Sample hat {len(sample.spots)} Spots")
    
    if sample.data_statistics:
        print(f"Adjusted Average: {sample.data_statistics.adjusted_average}")

    for spot in sample.spots:
        print(f"Mean: {spot.mean_val}, Row: {spot.row}, Col: {spot.col}")
```

### Zugriff auf Metadaten

```python
if dataset.metadata:
    print(dataset.metadata.pat_id)
    print(dataset.metadata.name)
    print(dataset.metadata.tags)
    
    for incubation in dataset.metadata.incubations:
        print(incubation.solution)
```

---

## UI-Komponenten (WidgetFactory)

Importieren Sie die Factory:

```python
from suplex.ui.widget_factory import WidgetFactory
```

### Häufig verwendete Widgets

```python
# Buttons
button = WidgetFactory.button_default("Klicken", on_click=callback)
button = WidgetFactory.button_emphasis("Wichtig", icon="🔥")
button = WidgetFactory.button_success("Speichern")
button = WidgetFactory.button_danger("Löschen")

# Eingabefelder
text = WidgetFactory.text_input(value="", description="Name:", on_change=callback)
number = WidgetFactory.number_input(value=10, min_value=0, max_value=100)
dropdown = WidgetFactory.dropdown(options=["A", "B", "C"], value="A")
checkbox = WidgetFactory.checkbox(value=False, description="Aktivieren")
slider = WidgetFactory.slider(value=50, min_value=0, max_value=100)

# Container
vbox = WidgetFactory.vbox(children=[widget1, widget2], gap="10px")
hbox = WidgetFactory.hbox(children=[widget1, widget2], gap="15px")
tabs = WidgetFactory.tab(children=[tab1, tab2], titles=["Tab 1", "Tab 2"])

# Info-Meldungen
info = WidgetFactory.info_field_success([WidgetFactory.html_widget("Erfolg!")])
warning = WidgetFactory.info_field_warning([WidgetFactory.html_widget("Warnung")])
```

---

## Submodule

SUPLEX stellt wiederverwendbare UI-Komponenten für die Datensatz- und Tag-Auswahl bereit.

### DatasetSelector

```python
from suplex.suplex_modules.submodules.dataset_selector import DatasetSelector
from suplex.suplex_modules.submodules.submodule_constants import DATASET_SELECTOR_MODE, DATASET_LABEL

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
from suplex.suplex_modules.submodules.tag_selector import TagSelector

tag_selector = TagSelector(datasets)
ui = tag_selector.get_ui_element()

tagged_datasets = tag_selector.get_tagged_datasets_any()
```

---

## Vollständiges Modul-Beispiel

Hier ist ein vollständiges, funktionierendes Beispiel eines einfachen Analyse-Moduls.

```python
import ipywidgets as widgets
from typing import List, Optional, Any
from typing_extensions import Self

from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface
from suplex.martin_interface.dataset import Dataset
from suplex.ui.widget_factory import WidgetFactory
from suplex.suplex_modules.submodules.dataset_selector import DatasetSelector
from suplex.suplex_modules.submodules.submodule_constants import DATASET_SELECTOR_MODE, DATASET_LABEL


class SimpleAnalysisModule(SuplexModuleInterface):
    """Beispielmodul, das grundlegende Statistiken für ausgewählte Datensätze berechnet."""

    def __init__(self):
        self._datasets: List[Dataset] = []
        self._dataset_selector: Optional[DatasetSelector] = None
        self._results_container: Optional[widgets.Widget] = None

    @property
    def module_name(self) -> str:
        return "Einfache Analyse"

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
        return "Führt eine einfache statistische Analyse der ausgewählten Datensätze durch."

    def initiate_module(self, datasets: List[Dataset], color_scheme) -> widgets.Widget:
        self._datasets = datasets

        header = WidgetFactory.html_widget(
            "<h2 style='color: #2E86AB;'>Einfaches Analyse-Modul</h2>"
        )

        self._dataset_selector = DatasetSelector(
            datasets=datasets,
            mode=DATASET_SELECTOR_MODE.MULTIPLE_UNBOUND,
            label_parts=[DATASET_LABEL.NAME, DATASET_LABEL.MEASURE_DATE]
        )

        analyze_btn = WidgetFactory.button_emphasis(
            "Analysieren", icon="🔍", on_click=self._on_analyze
        )

        self._results_container = WidgetFactory.vbox(
            children=[WidgetFactory.html_widget("<p>Datensätze auswählen und auf Analysieren klicken.</p>")],
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
                    WidgetFactory.html_widget("Bitte mindestens einen Datensatz auswählen.")
                ])
            ]
            return

        # Einfache Analyse durchführen
        html = "<h3>Ergebnisse</h3>"
        for ds in selected:
            total_spots = sum(len(s.spots) for s in ds.samples)
            html += f"<p><b>{ds.metadata.name if ds.metadata else 'Unbekannt'}</b>: {total_spots} Spots</p>"

        self._results_container.children = [
            WidgetFactory.info_field_success([WidgetFactory.html_widget(html)])
        ]

    def update_scheme(self, new_scheme) -> Optional[Self]:
        return None

    def reset_module(self) -> Optional[Self]:
        return SimpleAnalysisModule()
```

---

## Häufige Muster

### Daten über mehrere Datensätze aggregieren

```python
all_spots = []
for dataset in datasets:
    for sample in dataset.samples:
        all_spots.extend(sample.spots)

mean_values = [spot.mean_val for spot in all_spots]
average = sum(mean_values) / len(mean_values) if mean_values else 0
```

### Datensätze filtern

```python
from datetime import datetime, timedelta

# Nach Datum filtern
recent = [d for d in datasets if d.measure_date and d.measure_date > datetime.now() - timedelta(days=30)]

# Nach Tag filtern
control_datasets = [d for d in datasets if "control" in d.tags]
```

### Daten exportieren

```python
import pandas as pd

def export_spots_to_csv(datasets, filename="ergebnisse.csv"):
    records = []
    for ds in datasets:
        for sample in ds.samples:
            for spot in sample.spots:
                records.append({
                    "dataset": ds.metadata.name if ds.metadata else "Unbekannt",
                    "row": spot.row,
                    "col": spot.col,
                    "mean": spot.mean_val,
                    "normalized": spot.normalized_mean
                })
    pd.DataFrame(records).to_csv(filename, index=False)
```

---

## Debugging-Tipps

```python
def inspect_dataset(dataset):
    print(f"Name: {dataset.metadata.name if dataset.metadata else 'Unbekannt'}")
    print(f"Samples: {len(dataset.samples)}")
    print(f"Gesamte Spots: {sum(len(s.spots) for s in dataset.samples)}")
    print(f"Tags: {dataset.tags}")
```

---

## Best Practices

- Prüfen Sie immer, ob `dataset.metadata` oder `dataset.general_parameters` `None` ist.
- Verwenden Sie `WidgetFactory` für ein konsistentes Design.
- Halten Sie `initiate_module()` möglichst schnell — aufwändige Berechnungen sollten erst beim Klick auf einen Button ausgeführt werden.
- Geben Sie aus `reset_module()` eine **neue Instanz** zurück.
- Nutzen Sie den `color_scheme`-Parameter, der an `initiate_module()` übergeben wird.
- Bevorzugen Sie `DatasetSelector` und `TagSelector` vor selbst gebauten Auswahl-UI-Elementen.

---

## Bereitstellung

1. Speichern Sie Ihr Modul als `.py`-Datei.
2. Legen Sie es in einem der folgenden Ordner ab:
   - `src/suplex_modules/vanilla/` — für Standard-Module
   - `src/suplex_modules/custom/` — für benutzerdefinierte Module (Ordner bei Bedarf anlegen)
3. Module werden beim Start automatisch über `module_loader.py` erkannt.

### Schnelltest

```python
from ihr_modul import IhrModul

module = IhrModul()
print(module.module_name)
print(module.check_if_viable(ihre_test_datensätze))
```

---

Dieser Leitfaden entspricht dem aktuellen Stand der SUPLEX-Architektur. Im Zweifelsfall dienen die bestehenden Module in `src/suplex_modules/` als Referenzimplementierungen.