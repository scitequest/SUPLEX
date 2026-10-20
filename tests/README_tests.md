# SUPLEX Test Suite

This directory contains the comprehensive test suite for the SUPLEX project, which consists of three main layers:

- **martin_interface** — Data loading, validation, and the `Dataset` / `Project` domain model
- **suplex_modules** — Analysis modules (heatmaps, hitmaps, value extraction, filtering, etc.)
- **ui** — Graphical user interface (PySide6 + ipywidgets)

In addition, there is a dedicated `end_to_end/` folder for workflow-level tests that span multiple layers.

## Directory Structure

```
tests/
├── conftest.py                          # Global fixtures (used across 3+ packages)
├── martin_interface/
│   ├── conftest.py                      # Local fixtures for martin_interface
│   ├── unit/
│   └── integration/
├── suplex_modules/
│   ├── conftest.py                      # Local fixtures for suplex_modules
│   ├── submodules/
│   │   └── conftest.py
│   ├── unit/
│   ├── integration/
│   └── vanilla/
├── ui/
│   ├── conftest.py                      # Local fixtures for UI
│   ├── unit/
│   └── integration/
├── end_to_end/                          # End-to-end workflow tests
│   ├── conftest.py
│   └── test_*.py
├── test_data/
└── README_tests.md
```

## Testing Strategy

### Conftest Hierarchy

We follow a clear separation of concerns for fixtures:

| Level | File | Purpose | Scope |
|-------|------|---------|-------|
| **Global** | `tests/conftest.py` | Fixtures used by **3 or more** different packages | Available everywhere |
| **Package-local** | `martin_interface/conftest.py`, `suplex_modules/conftest.py`, `ui/conftest.py` | Fixtures used only within that package | Package + subfolders |
| **Test-specific** | Inside individual test files | Rarely used or very specific fixtures | Single test file |

**Rule**: Move a fixture to the highest appropriate level only when it is genuinely reused.

### Standardized Test Format

All test files should follow this consistent structure:

```python
import pytest
# Explicit imports only (no wildcard imports)


class TestClassName:
    """Clear, descriptive English docstring describing what this test class covers."""

    # -------------------------------------------------------------------------
    # Section Name
    # -------------------------------------------------------------------------

    def test_something(self, fixture_name):
        """Clear, descriptive English docstring."""
        # Arrange
        ...

        # Act
        ...

        # Assert
        ...
```

**Guidelines:**
- Use **class-based** tests
- All docstrings and comments must be in **English**
- Group related tests using `# -------------------------------------------------------------------------` section comments
- Prefer fixtures from the appropriate `conftest.py`
- Cover both the **happy path** and important **edge cases**
- Keep test logic and assertions 100% intact when refactoring existing tests

## Running Tests

All commands below assume the development environment created with `uv sync --group dev`;
prefix them with `uv run` (or activate `.venv`).

### Run All Tests

```bash
uv run pytest
```

### Run Specific Layers

```bash
# martin_interface layer
pytest tests/martin_interface/

# suplex_modules layer
pytest tests/suplex_modules/

# UI layer
pytest tests/ui/

# End-to-end tests only
pytest tests/end_to_end/
```

### Useful pytest Flags

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run with pdb on failure
pytest --pdb

# Run only tests matching a keyword
pytest -k "heatmap"

# Run with coverage
pytest --cov=suplex --cov-report=term-missing
```

### Coverage Reports

```bash
# Terminal report
pytest --cov=suplex --cov-report=term-missing

# HTML report (recommended)
pytest --cov=suplex --cov-report=html
# Then open htmlcov/index.html

# XML report (for CI)
pytest --cov=suplex --cov-report=xml
```

## Writing New Tests

### When Adding a New Test File

1. Place it in the correct folder:
   - `tests/martin_interface/unit/` or `integration/`
   - `tests/suplex_modules/unit/` or `integration/`
   - `tests/ui/unit/` or `integration/`
   - `tests/end_to_end/`

2. Use the appropriate local `conftest.py` for shared fixtures.

3. Follow the standardized class-based format shown above.

4. Include both happy path and relevant edge cases.

### Fixture Best Practices

- Keep fixtures focused and well-documented with English docstrings.
- Use `scope="session"` only for expensive operations (e.g. loading all modules).
- Prefer real objects over heavy mocking when feasible (especially in integration and end-to-end tests).
- For end-to-end tests, use realistic temporary MARTin datasets via the `end_to_end/conftest.py` fixtures.

## Continuous Integration

The test suite is designed to work well in CI/CD pipelines. Example GitHub Actions step:

```yaml
- name: Run tests
  run: |
    uv sync --locked --group dev
    uv run pytest --cov=suplex --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Debugging Tests

| Goal | Command |
|------|---------|
| See which tests are running | `pytest -v` |
| See print statements | `pytest -s` |
| Full traceback on failure | `pytest --tb=long` |
| Drop into debugger on failure | `pytest --pdb` |
| Run only one test file | `pytest tests/end_to_end/test_full_wizard_workflow.py` |
| Run only one test method | `pytest tests/end_to_end/test_full_wizard_workflow.py::TestFullWizardWorkflow::test_full_wizard_flow_end_to_end` |

## Best Practices

- **Isolation**: Every test should be independent and not rely on state from other tests.
- **Clarity**: Test names and docstrings should clearly describe what is being tested.
- **Speed**: Keep unit tests fast. Use mocks for expensive operations.
- **Realism**: Integration and end-to-end tests should use real `Adapter`, `Dataset`, and module objects whenever practical.
- **Maintenance**: Update tests when production code changes. Do not let tests become outdated.
- **Documentation**: Keep this README up to date when the test architecture changes.

---

This test suite aims to provide confidence when modifying any of the three layers (`martin_interface`, `suplex_modules`, or `ui`) while maintaining a clean and consistent testing experience.