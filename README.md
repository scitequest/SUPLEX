# SUPLEX

**SUPLEX** is a modular analysis platform for **MARTin** microarray data. It provides tools for data loading, validation, filtering, visualization (heatmaps, hitmaps, intensity overviews) and export, all accessible through a graphical interface that runs in your browser.

## Features

- **Robust Data Ingestion** — Load and validate MARTin datasets with automatic fallback handling for missing files
- **Modular Analysis** — Extensible module system for different visualization and analysis tasks
- **Interactive UI** — Browser interface built with ipywidgets and served by Voilà
- **Advanced Filtering** — Date range, tag-based, and statistical threshold filtering
- **Multiple Visualization Types** — Heatmap collages, hitmaps, intensity overviews, boxplots, and more
- **Export Capabilities** — Generate high-quality figures and Excel reports
- **End-to-End Workflow** — Complete wizard from directory selection to module execution

## Installation

### As a command line tool (recommended)

Install [uv](https://docs.astral.sh/uv/) once, then install SUPLEX as a tool. uv manages a private Python for it, so no system Python is required.

```bash
uv tool install git+https://github.com/scitequest/SUPLEX
suplex
```

`suplex` starts a local server and opens SUPLEX in your default browser. Options: `--port N`, `--no-browser`, `--debug` (show kernel tracebacks), `--demo` (disable saving to disk). Update with `uv tool upgrade suplex`.

### Standalone executables and Windows installer

Releases ship self-installing single-file executables for Windows, macOS and Linux built with [PyApp](https://ofek.dev/pyapp/), plus a Windows installer (`SUPLEX-Setup-<version>.exe`) that adds Start menu and desktop entries. The executable downloads Python and the locked dependencies on first start and reuses them afterwards.

### Online demo

Try SUPLEX in your browser without installing anything:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scitequest/SUPLEX/main?urlpath=voila/render/src/suplex/Suplex.ipynb)

> **Note:** The demo runs on a shared server. Exporting results and saving logs to disk is disabled there (demo mode); use the bundled sample data to explore the modules.

## Usage

1. Launch the application
2. Select a directory containing MARTin data, or load the sample data
3. Choose datasets using date and tag filters
4. Select an analysis module (e.g. Heatmap Collage, Hitmap)
5. Configure and run the module
6. Export results

### Custom modules and colour schemes

SUPLEX loads additional modules and colour schemes from a per-user directory that it creates on first start (the path is printed when `suplex` starts):

| Platform | Modules | Colour schemes |
|---|---|---|
| Linux | `~/.local/share/suplex/modules/` | `~/.local/share/suplex/schemes/` |
| macOS | `~/Library/Application Support/suplex/modules/` | `~/Library/Application Support/suplex/schemes/` |
| Windows | `%LOCALAPPDATA%\scitequest\suplex\modules\` | `%LOCALAPPDATA%\scitequest\suplex\schemes\` |

See the [module development guide](docs/SUPLEX_Module_Development_Guide_en.md) ([German](docs/SUPLEX_Module_Development_Guide_ger.md)) for writing modules.

## Development

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

## Requirements

- Python ≥ 3.11 (installed automatically by uv when using `uv tool install`)

## License

AGPL-3.0-only

## Author

Kai Oliver Kreissner
