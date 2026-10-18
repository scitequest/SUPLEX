# SUPLEX

**SUPLEX** is a modular analysis platform for **MARTin** microarray data. It provides powerful tools for data loading, validation, filtering, visualization (heatmaps, hitmaps, intensity overviews), and export — all accessible through an intuitive graphical interface.

## Features

- **Robust Data Ingestion** — Load and validate MARTin datasets with automatic fallback handling for missing files
- **Modular Analysis** — Extensible module system for different visualization and analysis tasks
- **Interactive UI** — Modern interface built with PySide6 and ipywidgets
- **Advanced Filtering** — Date range, tag-based, and statistical threshold filtering
- **Multiple Visualization Types** — Heatmap collages, hitmaps, intensity overviews, boxplots, and more
- **Export Capabilities** — Generate high-quality figures and Excel reports
- **End-to-End Workflow** — Complete wizard from directory selection to module execution

## Project Structure

```
suplex/
├── src/
│   ├── martin_interface/     # Data loading, validation & domain models
│   ├── suplex_modules/       # Analysis & visualization modules
│   └── ui/                   # Graphical user interface
├── tests/
│   ├── martin_interface/     # Tests for data layer
│   ├── suplex_modules/       # Tests for analysis modules
│   ├── ui/                   # Tests for the user interface
│   └── end_to_end/           # Full workflow integration tests
├── pyproject.toml
└── README.md
```

## Installation

### From Source (Recommended for Development)

```bash
git clone https://github.com/your-org/suplex.git
cd suplex
pip install -e ".[dev]"
```

### Install Only for Testing

```bash
pip install -e ".[test]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific layers
pytest tests/martin_interface/      # Data loading & validation
pytest tests/suplex_modules/        # Analysis modules
pytest tests/ui/                    # User interface
pytest tests/end_to_end/            # Full workflow tests

# With coverage
pytest --cov=src --cov-report=html
```

See [tests/README_tests.md](tests/README_tests.md) for detailed testing guidelines and conventions.

## Usage

1. Launch the application
2. Select a directory containing MARTin data
3. Choose datasets using date and tag filters
4. Select an analysis module (e.g. Heatmap Collage, Hitmap)
5. Configure and run the module
6. Export results

## Development

This project follows a clean multi-layer architecture:

- **`martin_interface`** — Handles directory scanning, file validation, and provides rich `Dataset` / `Project` objects
- **`suplex_modules`** — Implements analysis logic through a common `SuplexModuleInterface`
- **`ui`** — Provides the graphical wizard interface using Navigator + page components

We maintain a comprehensive test suite with:
- Unit tests for individual components
- Integration tests between layers
- End-to-end workflow tests

## Requirements

- Python ≥ 3.9
- ipywidgets / Jupyter
- matplotlib, numpy, pandas, seaborn
- Pillow, svgutils, openpyxl
- typing_extensions

## License

AGPL License

## Author

Kai Oliver Kreissner

---

*For detailed information about the test suite and development practices, see [tests/README_tests.md](tests/README_tests.md).*