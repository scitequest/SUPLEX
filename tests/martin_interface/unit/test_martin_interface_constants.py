import pytest
from enum import Enum
from src.martin_interface.martin_interface_constants import (
    MARTIN_MEASURE_DIR_DEPTH,
    STANDARD_READOUT_FILES,
    TOLERANCE,
    SEARCH_MODE,
    IMAGE_EXTENSIONS,
    DATA_FIELDS,
    DATA_STATISTICS_FIELDS,
    PARAMETERS_FIELDS_POLYGON,
    PARAMETERS_FIELDS_CIRCLE,
    METADATA_FIELDS_REQUIRED,
    PROJECT_FIELDS,
    INCUBATION_FIELDS,
    SUPLEX_FIELDS,
)


class TestMartinInterfaceConstants:
    """Tests for all constants and data structures defined in martin_interface_constants.py."""

    # -------------------------------------------------------------------------
    # Basic constants
    # -------------------------------------------------------------------------

    def test_martin_measure_dir_depth(self):
        """MARTIN_MEASURE_DIR_DEPTH is set to the expected integer value (3)."""
        assert MARTIN_MEASURE_DIR_DEPTH == 3
        assert isinstance(MARTIN_MEASURE_DIR_DEPTH, int)

    def test_standard_readout_files(self):
        """STANDARD_READOUT_FILES contains the two minimum required MARTin readout files."""
        assert "data.json" in STANDARD_READOUT_FILES
        assert "data.tsv" in STANDARD_READOUT_FILES
        assert len(STANDARD_READOUT_FILES) == 2

    def test_tolerance(self):
        """TOLERANCE is set to the expected floating-point precision value."""
        assert TOLERANCE == 1e-6
        assert isinstance(TOLERANCE, float)

    # -------------------------------------------------------------------------
    # SEARCH_MODE enum
    # -------------------------------------------------------------------------

    def test_search_mode_enum(self):
        """SEARCH_MODE is a proper Enum with all four expected members and correct string values."""
        assert issubclass(SEARCH_MODE, Enum)

        assert hasattr(SEARCH_MODE, "RECURSIVE")
        assert hasattr(SEARCH_MODE, "ITERATIVE_BOUNDED_BOTTOM")
        assert hasattr(SEARCH_MODE, "ITERATIVE_BOUNDED_ALL")
        assert hasattr(SEARCH_MODE, "ITERATIVE_UNBOUND")

        assert SEARCH_MODE.RECURSIVE.value == "recursive"
        assert SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM.value == "iterative_bounded_bottom"
        assert SEARCH_MODE.ITERATIVE_BOUNDED_ALL.value == "iterative_bounded_all"
        assert SEARCH_MODE.ITERATIVE_UNBOUND.value == "iterative_unbound"

        assert len(SEARCH_MODE) == 4

    # -------------------------------------------------------------------------
    # Image extensions
    # -------------------------------------------------------------------------

    def test_image_extensions(self):
        """IMAGE_EXTENSIONS contains all supported image file extensions as a set."""
        assert ".jpg" in IMAGE_EXTENSIONS
        assert ".jpeg" in IMAGE_EXTENSIONS
        assert ".png" in IMAGE_EXTENSIONS
        assert ".tif" in IMAGE_EXTENSIONS
        assert ".tiff" in IMAGE_EXTENSIONS

        assert isinstance(IMAGE_EXTENSIONS, set)

    # -------------------------------------------------------------------------
    # Data fields structures
    # -------------------------------------------------------------------------

    def test_data_fields_structure(self):
        """DATA_FIELDS has the correct nested structure and type annotations for MARTin data files."""
        assert isinstance(DATA_FIELDS, dict)
        assert "values" in DATA_FIELDS
        assert isinstance(DATA_FIELDS["values"], list)
        assert len(DATA_FIELDS["values"]) == 1

        fields = DATA_FIELDS["values"][0]
        assert "mean_minus_min" in fields
        assert fields["mean_minus_min"] == float
        assert "normalized_mean" in fields
        assert fields["normalized_mean"] == float
        assert "spot" in fields
        assert fields["spot"] == int
        assert "row" in fields
        assert fields["row"] == int
        assert "col" in fields
        assert fields["col"] == int
        assert "min" in fields
        assert fields["min"] == float
        assert "max" in fields
        assert fields["max"] == float
        assert "mean" in fields
        assert fields["mean"] == float
        assert "std_deviation" in fields
        assert fields["std_deviation"] == float

    def test_data_statistics_fields_structure(self):
        """DATA_STATISTICS_FIELDS has the correct nested structure and type annotations."""
        assert isinstance(DATA_STATISTICS_FIELDS, dict)
        assert "values" in DATA_STATISTICS_FIELDS
        assert isinstance(DATA_STATISTICS_FIELDS["values"], list)
        fields = DATA_STATISTICS_FIELDS["values"][0]
        assert "row" in fields
        assert fields["row"] == int
        assert "col" in fields
        assert fields["col"] == int
        assert "adjusted_average" in fields
        assert fields["adjusted_average"] == float
        assert "adjusted_average_std_deviation" in fields
        assert fields["adjusted_average_std_deviation"] == float
        assert "relative_adjusted_average_std_deviation" in fields
        assert fields["relative_adjusted_average_std_deviation"] == float
        assert "normalized_average" in fields
        assert fields["normalized_average"] == float
        assert "normalized_average_std_deviation" in fields
        assert fields["normalized_average_std_deviation"] == float
        assert "relative_normalized_average_std_deviation" in fields
        assert fields["relative_normalized_average_std_deviation"] == float

    # -------------------------------------------------------------------------
    # Parameters fields structures
    # -------------------------------------------------------------------------

    def test_parameters_fields_polygon_structure(self):
        """PARAMETERS_FIELDS_POLYGON matches the expected structure for polygonal spot definitions."""
        assert isinstance(PARAMETERS_FIELDS_POLYGON, dict)
        assert "invert_lut" in PARAMETERS_FIELDS_POLYGON
        assert PARAMETERS_FIELDS_POLYGON["invert_lut"] == bool
        assert "subtract_background" in PARAMETERS_FIELDS_POLYGON
        assert PARAMETERS_FIELDS_POLYGON["subtract_background"] == bool
        assert "number_of_spotfields" in PARAMETERS_FIELDS_POLYGON
        assert PARAMETERS_FIELDS_POLYGON["number_of_spotfields"] == int
        assert "columns_per_spotfield" in PARAMETERS_FIELDS_POLYGON
        assert PARAMETERS_FIELDS_POLYGON["columns_per_spotfield"] == int
        assert "spots_per_spotfield" in PARAMETERS_FIELDS_POLYGON
        assert PARAMETERS_FIELDS_POLYGON["spots_per_spotfield"] == int
        assert "spots" in PARAMETERS_FIELDS_POLYGON
        assert isinstance(PARAMETERS_FIELDS_POLYGON["spots"], list)
        spots = PARAMETERS_FIELDS_POLYGON["spots"][0]
        assert "type" in spots
        assert spots["type"] == str
        assert "coordinates" in spots
        assert spots["coordinates"] == [[float]]
        assert "background_rectangles" in PARAMETERS_FIELDS_POLYGON
        assert isinstance(PARAMETERS_FIELDS_POLYGON["background_rectangles"], list)
        bg_rect = PARAMETERS_FIELDS_POLYGON["background_rectangles"][0]
        assert "type" in bg_rect
        assert bg_rect["type"] == str
        assert "coordinates" in bg_rect
        assert bg_rect["coordinates"] == [[float]]

    def test_parameters_fields_circle_structure(self):
        """PARAMETERS_FIELDS_CIRCLE matches the expected structure for circular spot definitions."""
        assert isinstance(PARAMETERS_FIELDS_CIRCLE, dict)
        assert "invert_lut" in PARAMETERS_FIELDS_CIRCLE
        assert PARAMETERS_FIELDS_CIRCLE["invert_lut"] == bool
        assert "subtract_background" in PARAMETERS_FIELDS_CIRCLE
        assert PARAMETERS_FIELDS_CIRCLE["subtract_background"] == bool
        assert "number_of_spotfields" in PARAMETERS_FIELDS_CIRCLE
        assert PARAMETERS_FIELDS_CIRCLE["number_of_spotfields"] == int
        assert "columns_per_spotfield" in PARAMETERS_FIELDS_CIRCLE
        assert PARAMETERS_FIELDS_CIRCLE["columns_per_spotfield"] == int
        assert "spots_per_spotfield" in PARAMETERS_FIELDS_CIRCLE
        assert PARAMETERS_FIELDS_CIRCLE["spots_per_spotfield"] == int
        assert "spots" in PARAMETERS_FIELDS_CIRCLE
        assert isinstance(PARAMETERS_FIELDS_CIRCLE["spots"], list)
        spots = PARAMETERS_FIELDS_CIRCLE["spots"][0]
        assert "type" in spots
        assert spots["type"] == str
        assert "position" in spots
        assert spots["position"] == [[float]]
        assert "diameter" in spots
        assert spots["diameter"] == float
        assert "background_rectangles" in PARAMETERS_FIELDS_CIRCLE
        assert isinstance(PARAMETERS_FIELDS_CIRCLE["background_rectangles"], list)
        bg_rect = PARAMETERS_FIELDS_CIRCLE["background_rectangles"][0]
        assert "type" in bg_rect
        assert bg_rect["type"] == str
        assert "coordinates" in bg_rect
        assert bg_rect["coordinates"] == [[float]]

    # -------------------------------------------------------------------------
    # Metadata & related fields
    # -------------------------------------------------------------------------

    def test_metadata_fields_required_structure(self):
        """METADATA_FIELDS_REQUIRED defines the mandatory fields and their expected types."""
        assert isinstance(METADATA_FIELDS_REQUIRED, dict)
        assert "version" in METADATA_FIELDS_REQUIRED
        assert METADATA_FIELDS_REQUIRED["version"] == str
        assert "datetime" in METADATA_FIELDS_REQUIRED
        assert METADATA_FIELDS_REQUIRED["datetime"] == str
        assert "patient" in METADATA_FIELDS_REQUIRED
        assert isinstance(METADATA_FIELDS_REQUIRED["patient"], dict)
        patient = METADATA_FIELDS_REQUIRED["patient"]
        assert "id" in patient
        assert patient["id"] == str
        assert "name" in patient
        assert patient["name"] == str
        assert "tags" in patient
        assert isinstance(patient["tags"], list)
        assert patient["tags"][0] == str
        assert "image" in METADATA_FIELDS_REQUIRED
        assert isinstance(METADATA_FIELDS_REQUIRED["image"], dict)
        image = METADATA_FIELDS_REQUIRED["image"]
        assert "created" in image
        assert image["created"] == str
        assert "imager" in image
        assert image["imager"] == str
        assert "pixel_binning" in image
        assert image["pixel_binning"] == int
        assert "exposure_time" in image
        assert image["exposure_time"] == str
        assert "incubations" in METADATA_FIELDS_REQUIRED
        assert isinstance(METADATA_FIELDS_REQUIRED["incubations"], list)

    def test_project_fields_structure(self):
        """PROJECT_FIELDS defines the optional project section of metadata."""
        assert isinstance(PROJECT_FIELDS, dict)
        assert "project" in PROJECT_FIELDS
        assert isinstance(PROJECT_FIELDS["project"], dict)
        project = PROJECT_FIELDS["project"]
        assert "name" in project
        assert project["name"] == str
        assert "description" in project
        assert project["description"] == str

    def test_incubation_fields_structure(self):
        """INCUBATION_FIELDS defines the structure of individual incubation entries."""
        assert isinstance(INCUBATION_FIELDS, dict)
        assert "solution" in INCUBATION_FIELDS
        assert INCUBATION_FIELDS["solution"] == str
        assert "stock_concentration" in INCUBATION_FIELDS
        assert isinstance(INCUBATION_FIELDS["stock_concentration"], dict)
        stock = INCUBATION_FIELDS["stock_concentration"]
        assert "value" in stock
        assert stock["value"] == float
        assert "unit" in stock
        assert stock["unit"] == str
        assert "final_concentration" in INCUBATION_FIELDS
        assert isinstance(INCUBATION_FIELDS["final_concentration"], dict)
        final = INCUBATION_FIELDS["final_concentration"]
        assert "value" in final
        assert final["value"] == float
        assert "unit" in final
        assert final["unit"] == str
        assert "incubation_time" in INCUBATION_FIELDS
        assert INCUBATION_FIELDS["incubation_time"] == str

    def test_suplex_fields_structure(self):
        """SUPLEX_FIELDS defines the internal suplex.json structure used by Suplex modules."""
        assert isinstance(SUPLEX_FIELDS, dict)
        assert "tags" in SUPLEX_FIELDS
        assert isinstance(SUPLEX_FIELDS["tags"], list)
        assert SUPLEX_FIELDS["tags"][0] == str
        assert "row_labels" in SUPLEX_FIELDS
        assert isinstance(SUPLEX_FIELDS["row_labels"], list)
        assert SUPLEX_FIELDS["row_labels"][0] == str
        assert "col_labels" in SUPLEX_FIELDS
        assert isinstance(SUPLEX_FIELDS["col_labels"], list)
        assert SUPLEX_FIELDS["col_labels"][0] == str
