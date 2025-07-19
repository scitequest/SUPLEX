import ipywidgets as widgets
from typing import Dict, List, Optional
from typing_extensions import Self
from suplex_modules.suplex_module_interface import SuplexModuleInterface
from martin_interface.dataset import Dataset
import os

class DatasetViewerModule(SuplexModuleInterface):
    """
    Testmodul das die Namen und Informationen der selektierten Datensätze anzeigt.
    """

    def __init__(self):
        self._datasets = []

    @property
    def module_name(self) -> str:
        return "Dataset Viewer"

    @property
    def module_version(self) -> str:
        return "1.0.0"

    @property
    def group_name(self) -> str:
        return "Vanilla"

    @property
    def button_style(self) -> Dict[str, str]:
        return {
            'font_color': '#FFFFFF',
            'button_color': '#2E86AB',
            'button_icon': "📊"
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        # Dieses Modul funktioniert mit allen Datensätzen
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        return "Zeigt Informationen über die ausgewählten Datensätze an."

    def initiate_module(self, datasets: List[Dataset]) -> widgets.Box:
        self._datasets = datasets
        
        # Header
        header = widgets.HTML(
            value="<h2 style='color: #2E86AB; margin-bottom: 20px;'>Ausgewählte Datensätze</h2>"
        )
        
        # Dataset-Informationen
        dataset_info = []
        for i, dataset in enumerate(datasets, 1):
            info_html = f"""
            <div style='border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;'>
                <h3 style='margin-top: 0; color: #333;'>Dataset {i}</h3>
                <p><strong>Name:</strong> {getattr(dataset, 'name', 'Unbekannt')}</p>
                <p><strong>Typ:</strong> {type(dataset).__name__}</p>
                <p><strong>Pfad:</strong> {getattr(dataset, 'path', 'Nicht verfügbar')}</p>
            </div>
            """
            dataset_info.append(widgets.HTML(value=info_html))
        
        # Scrollbarer Container für die Datensätze
        content = widgets.VBox([header] + dataset_info)
        
        return widgets.Box([content], layout=widgets.Layout(
            width='100%',
            height='100%',
            overflow='auto',
            padding='20px'
        ))

    def update_scheme(self, new_scheme):
        return None

    def reset_module(self) -> Optional[Self]:
        return DatasetViewerModule()


class HelloWorldModule(SuplexModuleInterface):
    """
    Einfaches Hello World Testmodul.
    """

    def __init__(self):
        self._click_count = 0

    @property
    def module_name(self) -> str:
        return "Hello World"

    @property
    def module_version(self) -> str:
        return "1.0.0"

    @property
    def group_name(self) -> str:
        return "Demo"

    @property
    def button_style(self) -> Dict[str, str]:
        return {
            'font_color': '#FFFFFF',
            'button_color': '#A23B72'
            # no icon field
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        # Dieses Demo-Modul funktioniert immer
        return True

    def get_module_hover_text(self) -> str:
        return "Ein einfaches Demo-Modul zum Testen der GUI-Funktionalität."

    def initiate_module(self, datasets: List[Dataset]) -> widgets.Box:
        # Titel
        title = widgets.HTML(
            value="<h1 style='text-align: center; color: #A23B72;'>Hello World Module</h1>"
        )
        
        # Begrüßungstext
        greeting = widgets.HTML(
            value=f"<p style='text-align: center; font-size: 18px;'>Willkommen! Du hast {len(datasets)} Dataset(s) ausgewählt.</p>"
        )
        
        # Interaktiver Button
        self._click_counter = widgets.HTML(
            value=f"<p style='text-align: center;'>Button wurde {self._click_count} mal geklickt</p>"
        )
        
        click_button = widgets.Button(
            description='Klick mich!',
            button_style='success',
            layout=widgets.Layout(width='200px', margin='20px auto')
        )
        
        def on_button_click(b):
            self._click_count += 1
            self._click_counter.value = f"<p style='text-align: center;'>Button wurde {self._click_count} mal geklickt</p>"
        
        click_button.on_click(on_button_click)
        
        return widgets.VBox([
            title,
            greeting,
            click_button,
            self._click_counter
        ], layout=widgets.Layout(
            width='100%',
            height='100%',
            align_items='center',
            justify_content='center',
            padding='50px'
        ))

    def update_scheme(self, new_scheme):
        return None

    def reset_module(self) -> Optional[Self]:
        return HelloWorldModule()

class HelloWorldModule_Copy(SuplexModuleInterface):
    """
    Einfaches Hello World Testmodul.
    """

    def __init__(self):
        self._click_count = 0

    @property
    def module_name(self) -> str:
        return "Hello World_copy"

    @property
    def module_version(self) -> str:
        return "1.0.0"

    @property
    def group_name(self) -> str:
        return "Demo"

    @property
    def button_style(self) -> Dict[str, str]:
        return {
            'font_color': '#FFFFFF',
            'button_color': '#A23B72',
            'button_icon': "" # empty icon field
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        # Dieses Demo-Modul funktioniert immer
        return True

    def get_module_hover_text(self) -> str:
        return "Ein einfaches Demo-Modul zum Testen der GUI-Funktionalität."

    def initiate_module(self, datasets: List[Dataset]) -> widgets.Box:
        # Titel
        title = widgets.HTML(
            value="<h1 style='text-align: center; color: #A23B72;'>Hello World Module</h1>"
        )
        
        # Begrüßungstext
        greeting = widgets.HTML(
            value=f"<p style='text-align: center; font-size: 18px;'>Willkommen! Du hast {len(datasets)} Dataset(s) ausgewählt.</p>"
        )
        
        # Interaktiver Button
        self._click_counter = widgets.HTML(
            value=f"<p style='text-align: center;'>Button wurde {self._click_count} mal geklickt</p>"
        )
        
        click_button = widgets.Button(
            description='Klick mich!',
            button_style='success',
            layout=widgets.Layout(width='200px', margin='20px auto')
        )
        
        def on_button_click(b):
            self._click_count += 1
            self._click_counter.value = f"<p style='text-align: center;'>Button wurde {self._click_count} mal geklickt</p>"
        
        click_button.on_click(on_button_click)
        
        return widgets.VBox([
            title,
            greeting,
            click_button,
            self._click_counter
        ], layout=widgets.Layout(
            width='100%',
            height='100%',
            align_items='center',
            justify_content='center',
            padding='50px'
        ))

    def update_scheme(self, new_scheme):
        return None

    def reset_module(self) -> Optional[Self]:
        return HelloWorldModule()


class DataStatsModule(SuplexModuleInterface):
    """
    Modul zur Anzeige von Datenstatistiken mit etwas Interaktivität.
    """

    def __init__(self):
        self._datasets = []

    @property
    def module_name(self) -> str:
        return "Data Statistics"

    @property
    def module_version(self) -> str:
        return "1.2.0"

    @property
    def group_name(self) -> str:
        return "Vanilla"

    @property
    def button_style(self) -> Dict[str, str]:
        icon_path = os.path.join(os.path.dirname(__file__), "gif_icon.gif")
        
        return {
            'font_color': '#FFFFFF',
            'button_color': '#F18F01',
            'button_icon': icon_path
        }

    def check_if_viable(self, datasets: List[Dataset]) -> bool:
        # Nur verfügbar wenn mindestens ein Dataset ausgewählt ist
        return len(datasets) > 0

    def get_module_hover_text(self) -> str:
        return "Zeigt Statistiken und Metadaten der ausgewählten Datensätze an."

    def initiate_module(self, datasets: List[Dataset]) -> widgets.Box:
        self._datasets = datasets
        
        # Header
        header = widgets.HTML(
            value="<h2 style='color: #F18F01; margin-bottom: 20px;'>Dataset Statistiken</h2>"
        )
        
        # Dropdown zur Dataset-Auswahl
        dataset_names = [f"Dataset {i+1}: {getattr(ds, 'name', 'Unbekannt')}" for i, ds in enumerate(datasets)]
        dataset_dropdown = widgets.Dropdown(
            options=dataset_names,
            description='Dataset:',
            layout=widgets.Layout(width='400px')
        )
        
        # Statistik-Anzeige
        stats_display = widgets.HTML(value="<p>Wähle ein Dataset aus dem Dropdown-Menü aus.</p>")
        
        def update_stats(change):
            selected_index = dataset_dropdown.index
            if selected_index is not None and selected_index < len(datasets):
                dataset = datasets[selected_index]
                stats_html = f"""
                <div style='border: 2px solid #F18F01; border-radius: 10px; padding: 20px; background-color: #fff5e6;'>
                    <h3 style='color: #F18F01; margin-top: 0;'>Statistiken für {getattr(dataset, 'name', 'Unbekannt')}</h3>
                    <ul style='list-style-type: none; padding-left: 0;'>
                        <li>📂 <strong>Typ:</strong> {type(dataset).__name__}</li>
                        <li>📍 <strong>Pfad:</strong> {getattr(dataset, 'path', 'Nicht verfügbar')}</li>
                        <li>🔢 <strong>Größe:</strong> {getattr(dataset, 'size', 'Unbekannt')} Einträge</li>
                        <li>📅 <strong>Erstellt:</strong> {getattr(dataset, 'created', 'Unbekannt')}</li>
                        <li>🏷️ <strong>Format:</strong> {getattr(dataset, 'format', 'Unbekannt')}</li>
                    </ul>
                </div>
                """
                stats_display.value = stats_html
        
        dataset_dropdown.observe(update_stats, names='value')
        
        # Refresh Button
        refresh_btn = widgets.Button(
            description='🔄 Aktualisieren',
            button_style='info',
            layout=widgets.Layout(width='150px', margin='10px 0')
        )
        
        def refresh_stats(b):
            if dataset_dropdown.index is not None:
                update_stats({'new': dataset_dropdown.value})
        
        refresh_btn.on_click(refresh_stats)
        
        # Summary Info
        summary = widgets.HTML(
            value=f"""
            <div style='background-color: #f0f8ff; border-left: 4px solid #F18F01; padding: 15px; margin: 20px 0;'>
                <h4 style='margin: 0 0 10px 0;'>Zusammenfassung</h4>
                <p><strong>Gesamtanzahl Datasets:</strong> {len(datasets)}</p>
                <p><strong>Modul Version:</strong> {self.module_version}</p>
            </div>
            """
        )
        
        return widgets.VBox([
            header,
            dataset_dropdown,
            refresh_btn,
            stats_display,
            summary
        ], layout=widgets.Layout(
            width='100%',
            height='100%',
            padding='20px',
            overflow='auto'
        ))
        
    def update_scheme(self, new_scheme):
        return None
        
    def reset_module(self) -> Optional[Self]:
        return DataStatsModule()