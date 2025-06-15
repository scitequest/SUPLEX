import pytest
import json
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


class TestNotebooks:
    """Test suite for Jupyter notebooks."""

    def test_suplex_notebook_structure(self):
        """Test Suplex notebook structure and imports."""
        # Read the notebook
        with open("Suplex.ipynb", "r") as f:
            nb = nbformat.read(f, as_version=4)

        # Check notebook metadata
        assert nb.metadata.kernelspec.language == "python"

        # Check for required imports in code cells
        code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
        assert len(code_cells) >= 2

        # Check first cell imports
        first_cell = code_cells[0].source
        assert "from suplex_elements.GUI import GUI" in first_cell
        assert "import ipywidgets as widgets" in first_cell
        assert "import logging" in first_cell

    @pytest.mark.skip(reason="Requires running Jupyter kernel")
    def test_suplex_notebook_execution(self):
        """Test Suplex notebook execution."""
        # This test would require a running Jupyter kernel
        # Skipped in CI but can be run locally
        pass
