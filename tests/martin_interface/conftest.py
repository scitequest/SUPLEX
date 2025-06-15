import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import isodate
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for test files.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_data_dict():
    """
    Sample data dictionary for testing.
    """
    return {
        "values": [
            {
                "mean_minus_min": 100.5,
                "normalized_mean": 0.5,
                "spot": 0,
                "row": 0,
                "col": 0,
                "min": 50.0,
                "max": 200.0,
                "mean": 150.5,
                "std_deviation": 25.3,
            },
            {
                "mean_minus_min": 50.25,
                "normalized_mean": 0.25,
                "spot": 0,
                "row": 0,
                "col": 1,
                "min": 25.0,
                "max": 100.0,
                "mean": 75.25,
                "std_deviation": 20.2,
            },
            {
                "mean_minus_min": 120.7,
                "normalized_mean": 0.6,
                "spot": 1,
                "row": 0,
                "col": 0,
                "min": 60.0,
                "max": 240.0,
                "mean": 180.7,
                "std_deviation": 30.2,
            },
            {
                "mean_minus_min": 60.35,
                "normalized_mean": 0.3,
                "spot": 1,
                "row": 0,
                "col": 1,
                "min": 30.0,
                "max": 120.0,
                "mean": 90.35,
                "std_deviation": 10.2,
            },
        ]
    }


@pytest.fixture
def sample_data_dict_raw():
    """
    Sample data dictionary for testing.
    """
    return {
        "values": [
            {
                "mean_minus_min": "100.5",
                "normalized_mean": "0.5",
                "spot": "0",
                "row": "0",
                "col": "0",
                "min": "50.0",
                "max": "200.0",
                "mean": "150.5",
                "std_deviation": "25.3",
            },
            {
                "mean_minus_min": "50.25",
                "normalized_mean": "0.25",
                "spot": "0",
                "row": "0",
                "col": "1",
                "min": "25.0",
                "max": "100.0",
                "mean": "75.25",
                "std_deviation": "20.2",
            },
            {
                "mean_minus_min": "120.7",
                "normalized_mean": "0.6",
                "spot": "1",
                "row": "0",
                "col": "0",
                "min": "60.0",
                "max": "240.0",
                "mean": "180.7",
                "std_deviation": "30.2",
            },
            {
                "mean_minus_min": "60.35",
                "normalized_mean": "0.3",
                "spot": "1",
                "row": "0",
                "col": "1",
                "min": "30.0",
                "max": "120.0",
                "mean": "90.35",
                "std_deviation": "10.2",
            },
        ]
    }


@pytest.fixture
def sample_data_tsv():
    """
    Sample data as TSV string containing string values.
    """
    lines = [
        "mean_minus_min\tnormalized_mean\tspot\trow\tcol\tmin\tmax\tmean\tstd_deviation",
        "100.5\t0.5\t0\t0\t0\t50.0\t200.0\t150.5\t25.3",
        "50.25\t0.25\t0\t0\t1\t25.0\t100.0\t75.25\t20.2",
        "120.7\t0.6\t1\t0\t0\t60.0\t240.0\t180.7\t30.2",
        "60.35\t0.3\t1\t0\t1\t30.0\t120.0\t90.35\t10.2",
    ]
    return "\n".join(lines)


@pytest.fixture
def sample_data_statistics_dict():
    """
    Sample data statistics dictionary for testing.
    The values of this dict have been derived from the sample data dictionary.
    """
    return {
        "values": [
            {
                "row": 0,
                "col": 0,
                "adjusted_average": 110.6,
                "adjusted_average_std_deviation": 14.28355698,
                "relative_adjusted_average_std_deviation": 12.9146085,
                "normalized_average": 0.55,
                "normalized_average_std_deviation": 0.070710678,
                "relative_normalized_average_std_deviation": 12.8564869,
            },
            {
                "row": 0,
                "col": 1,
                "adjusted_average": 55.3,
                "adjusted_average_std_deviation": 7.14177849,
                "relative_adjusted_average_std_deviation": 12.9146085,
                "normalized_average": 0.275,
                "normalized_average_std_deviation": 0.035355339,
                "relative_normalized_average_std_deviation": 12.8564869,
            },
        ]
    }


@pytest.fixture
def sample_data_statistics_dict_raw():
    """
    Variant of sample_data_statistics_dict.
    All values are stored as strings.
    """
    return {
        "values": [
            {
                "row": "0",
                "col": "0",
                "adjusted_average": "110.6",
                "adjusted_average_std_deviation": "14.28355698",
                "relative_adjusted_average_std_deviation": "12.9146085",
                "normalized_average": "0.55",
                "normalized_average_std_deviation": "0.070710678",
                "relative_normalized_average_std_deviation": "12.8564869",
            },
            {
                "row": "0",
                "col": "1",
                "adjusted_average": "55.3",
                "adjusted_average_std_deviation": "7.14177849",
                "relative_adjusted_average_std_deviation": "12.9146085",
                "normalized_average": "0.275",
                "normalized_average_std_deviation": "0.035355339",
                "relative_normalized_average_std_deviation": "12.8564869",
            },
        ]
    }


@pytest.fixture
def sample_data_statistics_tsv():
    """
    Sample data_statistics as TSV string containing string values.
    """
    lines = [
        "row\tcol\tadjusted_average\tadjusted_average_std_deviation\trelative_adjusted_average_std_deviation\tnormalized_average\tnormalized_average_std_deviation\trelative_normalized_average_std_deviation",
        "0\t0\t110.6\t14.28355698\t12.9146085\t0.55\t0.070710678\t12.8564869",
        "0\t1\t55.3\t7.14177849\t12.9146085\t0.275\t0.035355339\t12.8564869",
    ]
    return "\n".join(lines)


@pytest.fixture
def sample_metadata_dict():
    """
    Complete metadata with parsed datetime and duration.
    """
    return {
        "version": "1.0",
        "datetime": datetime.fromisoformat("1998-07-13T10:30:00"),
        "patient": {"id": "PAT001", "name": "Test Patient", "tags": ["tag1", "tag2"]},
        "image": {
            "created": datetime.fromisoformat("1997-07-13T10:00:00"),
            "imager": "Test imager",
            "pixel_binning": 1,
            "exposure_time": isodate.parse_duration("PT0.5S"),
        },
        "incubations": [
            {
                "solution": "Antibody Solution",
                "stock_concentration": {"value": 1000.0, "unit": "µg/mL"},
                "final_concentration": {"value": 10.0, "unit": "µg/mL"},
                "incubation_time": isodate.parse_duration("PT30M"),
            }
        ],
        "project": {"name": "TestProject", "description": "Test project description"},
    }


@pytest.fixture
def sample_metadata_dict_natural():
    """
    A Metadata dict without any objects.
    Datetime and duration are not parsed and kept as strings.
    This is the state metadata.json files should be in.
    """
    return {
        "version": "1.0",
        "datetime": "1998-07-13T10:30:00",
        "patient": {"id": "PAT001", "name": "Test Patient", "tags": ["tag1", "tag2"]},
        "image": {
            "created": "1997-07-13T10:00:00",
            "imager": "Test imager",
            "pixel_binning": 1,
            "exposure_time": "PT0.5S",
        },
        "incubations": [
            {
                "solution": "Antibody Solution",
                "stock_concentration": {"value": 1000.0, "unit": "µg/mL"},
                "final_concentration": {"value": 10.0, "unit": "µg/mL"},
                "incubation_time": "PT30M",
            }
        ],
        "project": {"name": "TestProject", "description": "Test project description"},
    }


@pytest.fixture
def sample_metadata_dict_raw():
    """
    Variant of sample_data_statistics_dict.
    All values are stored as strings.
    No incubations and no project field - this is the minimal state of a metadata file.
    """
    return {
        "version": "1.0",
        "datetime": "1998-07-13T10:30:00",
        "patient": {"id": "PAT001", "name": "Test Patient", "tags": ["tag1", "tag2"]},
        "image": {
            "created": "1997-07-13T10:00:00",
            "imager": "Test imager",
            "pixel_binning": "1",
            "exposure_time": "PT0.5S",
        },
        "incubations": [],
    }


@pytest.fixture
def sample_incubation_dict_raw():
    """
    Variant of the incubations field of sample_data_statistics_dict.
    All values are stored as strings.
    """
    return {
        "solution": "Antibody Solution",
        "stock_concentration": {"value": "1000.0", "unit": "µg/mL"},
        "final_concentration": {"value": "10.0", "unit": "µg/mL"},
        "incubation_time": "PT30M",
    }


@pytest.fixture
def sample_project_dict_raw():
    """
    Variant of the project field of sample_data_statistics_dict.
    All values are stored as strings.
    """
    return {"name": "TestProject", "description": "Test project description"}


@pytest.fixture
def sample_parameters_dict_polygon():
    """
    Sample parameters dictionary with polygonal spots.
    """
    return {
        "invert_lut": False,
        "subtract_background": True,
        "number_of_spotfields": 2,
        "columns_per_spotfield": 2,
        "spots_per_spotfield": 2,
        "spots": [
            {
                "type": "POLYGON",
                "coordinates": [[10.0, 10.0], [20.0, 10.0], [20.0, 20.0], [10.0, 20.0]],
            },
            {
                "type": "POLYGON",
                "coordinates": [[30.0, 10.0], [40.0, 10.0], [40.0, 20.0], [30.0, 20.0]],
            },
            {
                "type": "POLYGON",
                "coordinates": [
                    [110.0, 10.0],
                    [120.0, 10.0],
                    [120.0, 20.0],
                    [110.0, 20.0],
                ],
            },
            {
                "type": "POLYGON",
                "coordinates": [
                    [130.0, 10.0],
                    [140.0, 10.0],
                    [140.0, 20.0],
                    [130.0, 20.0],
                ],
            },
        ],
        "background_rectangles": [
            {
                "type": "POLYGON",
                "coordinates": [[0.0, 0.0], [5.0, 0.0], [5.0, 5.0], [0.0, 5.0]],
            }
        ],
    }


@pytest.fixture
def sample_parameters_dict_polygon_raw():
    """
    Sample parameters dictionary with polygonal spots.
    """
    return {
        "invert_lut": "False",
        "subtract_background": "True",
        "number_of_spotfields": "2",
        "columns_per_spotfield": "2",
        "spots_per_spotfield": "2",
        "spots": [
            {
                "type": "POLYGON",
                "coordinates": [
                    ["10.0", "10.0"],
                    ["20.0", "10.0"],
                    ["20.0", "20.0"],
                    ["10.0", "20.0"],
                ],
            },
            {
                "type": "POLYGON",
                "coordinates": [
                    ["30.0", "10.0"],
                    ["40.0", "10.0"],
                    ["40.0", "20.0"],
                    ["30.0", "20.0"],
                ],
            },
            {
                "type": "POLYGON",
                "coordinates": [
                    ["110.0", "10.0"],
                    ["120.0", "10.0"],
                    ["120.0", "20.0"],
                    ["110.0", "20.0"],
                ],
            },
            {
                "type": "POLYGON",
                "coordinates": [
                    ["130.0", "10.0"],
                    ["140.0", "10.0"],
                    ["140.0", "20.0"],
                    ["130.0", "20.0"],
                ],
            },
        ],
        "background_rectangles": [
            {
                "type": "POLYGON",
                "coordinates": [
                    ["0.0", "0.0"],
                    ["5.0", "0.0"],
                    ["5.0", "5.0"],
                    ["0.0", "5.0"],
                ],
            }
        ],
    }


@pytest.fixture
def sample_parameters_dict_circle():
    """
    Sample parameters dictionary with circular spots.
    Added typo `subract` for compatibility testing of MARTin v1.0.
    """
    return {
        "invert_lut": True,
        "subtract_background": False,
        "number_of_spotfields": 2,
        "columns_per_spotfield": 2,
        "spots_per_spotfield": 2,
        "spots": [
            {"type": "CIRCLE", "position": [15.0, 15.0], "diameter": 10.0},
            {"type": "CIRCLE", "position": [35.0, 15.0], "diameter": 10.0},
            {"type": "CIRCLE", "position": [115.0, 15.0], "diameter": 10.0},
            {"type": "CIRCLE", "position": [135.0, 15.0], "diameter": 10.0},
        ],
        "background_rectangles": [
            {
                "type": "POLYGON",
                "coordinates": [[0.0, 0.0], [5.0, 0.0], [5.0, 5.0], [0.0, 5.0]],
            }
        ],
    }


@pytest.fixture
def sample_parameters_dict_circle_raw():
    """
    Sample parameters dictionary with circular spots.
    Added typo `subract` for compatibility testing of MARTin v1.0.
    """
    return {
        "invert_lut": "True",
        "subtract_background": "False",
        "number_of_spotfields": "2",
        "columns_per_spotfield": "2",
        "spots_per_spotfield": "2",
        "spots": [
            {"type": "CIRCLE", "position": ["15.0", "15.0"], "diameter": "10.0"},
            {"type": "CIRCLE", "position": ["35.0", "15.0"], "diameter": "10.0"},
            {"type": "CIRCLE", "position": ["115.0", "15.0"], "diameter": "10.0"},
            {"type": "CIRCLE", "position": ["135.0", "15.0"], "diameter": "10.0"},
        ],
        "background_rectangles": [
            {
                "type": "POLYGON",
                "coordinates": [
                    ["0.0", "0.0"],
                    ["5.0", "0.0"],
                    ["5.0", "5.0"],
                    ["0.0", "5.0"],
                ],
            }
        ],
    }


@pytest.fixture
def sample_suplex_dict():
    """
    Sample suplex dictionary for testing.
    """
    return {
        "tags": ["analysis1", "validated"],
        "row_labels": ["A", "B"],
        "col_labels": ["1", "2"],
    }


@pytest.fixture
def mock_path_holder():
    """
    Mock PathHolder object.
    """
    from src.martin_interface.holder import PathHolder

    return PathHolder(
        dataset_path="/test/dataset",
        data_path="/test/dataset/data.json",
        data_statistics_path="/test/dataset/data_statistics.json",
        metadata_path="/test/dataset/metadata.json",
        parameters_path="/test/dataset/parameters.json",
        image_path="/test/dataset/image.tif",
        annotated_image_path="/test/dataset/annotated_image.tif",
        suplex_path="/test/dataset/suplex.json",
    )


@pytest.fixture
def mock_file_holder(
    sample_data_dict,
    sample_data_statistics_dict,
    sample_metadata_dict,
    sample_parameters_dict_polygon,
    sample_suplex_dict,
):
    """
    Mock FileHolder object.
    """
    from src.martin_interface.holder import FileHolder

    return FileHolder(
        data_file=sample_data_dict,
        data_statistics_file=sample_data_statistics_dict,
        metadata_file=sample_metadata_dict,
        parameters_file=sample_parameters_dict_polygon,
        suplex_file=sample_suplex_dict,
    )


@pytest.fixture
def create_sample_files(
    temp_dir,
    sample_data_dict,
    sample_data_statistics_dict,
    sample_metadata_dict_natural,
    sample_parameters_dict_polygon,
    sample_suplex_dict,
):
    """
    Generates testfiles in a temporary directory
    """
    # Create data.json
    data_path = os.path.join(temp_dir, "data.json")
    with open(data_path, "w") as f:
        json.dump(sample_data_dict, f)

    # Create data_statistics.json
    data_statistics_path = os.path.join(temp_dir, "data_statistics.json")
    with open(data_statistics_path, "w") as f:
        json.dump(sample_data_statistics_dict, f)

    # Create metadata.json
    metadata_path = os.path.join(temp_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(sample_metadata_dict_natural, f)

    # Create parameters.json
    parameters_path = os.path.join(temp_dir, "parameters.json")
    with open(parameters_path, "w") as f:
        json.dump(sample_parameters_dict_polygon, f)

    # Create suplex.json
    suplex_path = os.path.join(temp_dir, "suplex.json")
    with open(suplex_path, "w") as f:
        json.dump(sample_suplex_dict, f)

    return temp_dir
