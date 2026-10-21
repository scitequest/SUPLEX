# SUPLEX

**SUPLEX** is a modular analysis platform for data produced by **[MARTin](https://github.com/scitequest/martin)** (MicroArray Rastering Tool).  
It provides tools for data loading, validation, filtering, visualization (heatmaps, hitmaps, intensity overviews) and export — all accessible through a graphical interface that runs in your browser.

[![MARTin](https://img.shields.io/badge/Data%20from-MARTin-blue?style=flat-square)](https://github.com/scitequest/martin)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scitequest/SUPLEX/main?urlpath=voila/render/src/suplex/Suplex.ipynb)

### Features
- **Robust Data Ingestion** — Load and validate MARTin datasets with automatic fallback handling for missing files  
- **Modular Analysis** — Extensible module system for different visualization and analysis tasks  
- **Interactive UI** — Browser interface built with ipywidgets and served by Voilà  
- **Advanced Filtering** — Date range, tag-based, and statistical threshold filtering  
- **Multiple Visualization Types** — Heatmap collages, hitmaps, intensity overviews, boxplots, and more  
- **Export Capabilities** — Generate high-quality figures and Excel reports  
- **End-to-End Workflow** — Complete wizard from directory selection to module execution  

## Ways to Use SUPLEX

| Method | Best for | Data Saving/Loading | Requirements |
|--------|----------|---------------------|--------------|
| **Windows Installer** | Regular use | Full local access | None |
| **Standalone Executable** | Regular use | Full local access | None |
| **`uv tool install`** | Developers & power users | Full local access | [uv](https://docs.astral.sh/uv/) |
| **Online Demo** (Binder) | Quick testing | Disabled (demo mode) | Browser only |
| **From Source** | Development | Full local access | [uv](https://docs.astral.sh/uv/), Python ≥ 3.11 |

### 1. Windows Installer (Recommended for most users)
Download the latest `SUPLEX-Setup-*.exe` from the [Releases](https://github.com/scitequest/SUPLEX/releases) page.  
After installation, start SUPLEX from the Start Menu or Desktop icon. The application opens automatically in your default browser.  
No Python or Jupyter installation is required. All data stays on your computer.

### 2. Standalone Executable
Self-installing single-file executables for Windows, macOS and Linux are available in the [Releases](https://github.com/scitequest/SUPLEX/releases).  
The executable downloads Python and the dependencies on first start and reuses them afterwards.

### 3. Install as a command-line tool (uv)
Install [uv](https://docs.astral.sh/uv/) once, then:

```bash
uv tool install git+https://github.com/scitequest/SUPLEX
suplex
```

`suplex` starts a local server and opens SUPLEX in your browser.  
Options: `--port N`, `--no-browser`, `--debug`, `--demo`.  
Update later with `uv tool upgrade suplex`.

### 4. Online Demo (Binder)
Try SUPLEX directly in your browser:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scitequest/SUPLEX/main?urlpath=voila/render/src/suplex/Suplex.ipynb)

> **Note:** The demo runs in demo mode. Saving and loading of data is disabled. Use the bundled sample data to explore the modules.

### 5. From Source (Development)
```bash
git clone https://github.com/scitequest/SUPLEX.git
cd SUPLEX
uv sync --group dev
uv run suplex
```

### Usage
1. Launch the application  
2. Select a directory containing MARTin data, or load the sample data  
3. Choose datasets using date and tag filters  
4. Select an analysis module (e.g. Heatmap Collage, Hitmap)  
5. Configure and run the module  
6. Export results  

### Custom modules and colour schemes
SUPLEX loads additional modules and colour schemes from a per-user directory that it creates on first start (the path is printed when `suplex` starts):

| Platform | Modules | Colour schemes |
|----------|---------|----------------|
| Linux | `~/.local/share/suplex/modules/` | `~/.local/share/suplex/schemes/` |
| macOS | `~/Library/Application Support/suplex/modules/` | `~/Library/Application Support/suplex/schemes/` |
| Windows | `%LOCALAPPDATA%\scitequest\suplex\modules\` | `%LOCALAPPDATA%\scitequest\suplex\schemes\` |

See the [module development guide](docs/SUPLEX_Module_Development_Guide_en.md) ([German](docs/SUPLEX_Module_Development_Guide_ger.md)) for writing modules.

### Development
```bash
git clone https://github.com/scitequest/SUPLEX.git
cd SUPLEX
uv sync --group dev      # creates .venv with Python 3.14 and all dependencies
uv run suplex            # run the app from the checkout
uv run pytest            # run the test suite
uv run ruff check        # lint
uv run ruff format       # format
```

### Project structure
```
SUPLEX/
├── src/suplex/
│   ├── martin_interface/     # Data loading, validation & domain models
│   ├── suplex_modules/       # Analysis & visualization modules
│   ├── ui/                   # Graphical user interface
│   ├── sample_data/          # Bundled sample measurements (json/tsv)
│   ├── app.py                # Builds the GUI (called from the notebook)
│   ├── cli.py                # `suplex` command: starts Voilà and the browser
│   └── Suplex.ipynb          # Notebook rendered by Voilà
├── sample_data/              # Microscope images for the sample data (repository only)
├── tests/                    # Unit, integration and end-to-end tests
├── docs/                     # Module development guides
├── packaging/
│   ├── pyapp/                # Self-installing executable build
│   └── windows/              # Inno Setup installer wrapping the executable
├── start                     # Binder entry point (enables demo mode)
└── pyproject.toml
```

The code follows a multi-layer architecture:

- **`martin_interface`** — Handles directory scanning, file validation, and provides rich `Dataset` / `Project` objects  
- **`suplex_modules`** — Implements analysis logic through a common `SuplexModuleInterface`  
- **`ui`** — Provides the graphical wizard interface using Navigator + page components  

### Demo mode
Setting the environment variable `SUPLEX_DEMO=1` (or passing `--demo`) disables the buttons that write to the local disk. Binder sets it through the `start` script.

### Building the distributables
```bash
uv build                                       # sdist and wheel in dist/
uv run python packaging/pyapp/build.py         # executable in dist/pyapp/ (needs cargo)
```

On Windows the Inno Setup installer is compiled from `packaging/windows/suplex.iss` after the executable build. CI builds all of them on tags `v*`.

See [tests/README_tests.md](tests/README_tests.md) for testing guidelines and conventions.

### Requirements
- Python ≥ 3.11 (installed automatically by uv when using `uv tool install`)

### License
AGPL-3.0-only

### Author
Kai Oliver Kreissner
