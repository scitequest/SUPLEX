import pytest
from datetime import datetime, timedelta
import isodate
from unittest.mock import patch, Mock
from src.martin_interface.validation.metadata_validation import *


class TestMetadataValidation:
    @patch("src.martin_interface.validation.metadata_validation.try_get_valid_json")
    def test_try_get_validated_metadata_invalid_json(self, mock_json):
        mock_json.return_value = None

        result = try_get_validated_metadata("/test/path")
        assert result is None

    @patch(
        "src.martin_interface.validation.metadata_validation.try_typecast_metadata_file"
    )
    @patch(
        "src.martin_interface.validation.metadata_validation.is_Key_Structure_Identical"
    )
    @patch("src.martin_interface.validation.metadata_validation.try_get_valid_json")
    def test_try_get_validated_metadata_success_complete_values(
        self,
        mock_json,
        mock_key_structure,
        mock_typecast,
        sample_metadata_dict,
        sample_metadata_dict_raw,
        sample_incubation_dict_raw,
        sample_project_dict_raw,
    ):
        complete_metadata_raw = copy.deepcopy(sample_metadata_dict_raw)
        complete_metadata_raw["incubations"] = [sample_incubation_dict_raw]
        complete_metadata_raw["project"] = sample_project_dict_raw

        mock_json.return_value = complete_metadata_raw
        mock_key_structure.return_value = True
        mock_typecast.return_value = sample_metadata_dict

        result = try_get_validated_metadata("/test/path")

        assert result is not None

        # Explicit value comparisons with sample_metadata_dict
        assert result["version"] == sample_metadata_dict["version"]
        assert result["datetime"] == sample_metadata_dict["datetime"]
        assert result["patient"]["id"] == sample_metadata_dict["patient"]["id"]
        assert result["patient"]["name"] == sample_metadata_dict["patient"]["name"]
        assert result["patient"]["tags"] == sample_metadata_dict["patient"]["tags"]
        assert result["image"]["created"] == sample_metadata_dict["image"]["created"]
        assert result["image"]["imager"] == sample_metadata_dict["image"]["imager"]
        assert (
            result["image"]["pixel_binning"]
            == sample_metadata_dict["image"]["pixel_binning"]
        )
        assert (
            result["image"]["exposure_time"]
            == sample_metadata_dict["image"]["exposure_time"]
        )
        assert (
            result["incubations"][0]["solution"]
            == sample_metadata_dict["incubations"][0]["solution"]
        )
        assert (
            result["incubations"][0]["stock_concentration"]["value"]
            == sample_metadata_dict["incubations"][0]["stock_concentration"]["value"]
        )
        assert (
            result["incubations"][0]["stock_concentration"]["unit"]
            == sample_metadata_dict["incubations"][0]["stock_concentration"]["unit"]
        )
        assert (
            result["incubations"][0]["final_concentration"]["value"]
            == sample_metadata_dict["incubations"][0]["final_concentration"]["value"]
        )
        assert (
            result["incubations"][0]["final_concentration"]["unit"]
            == sample_metadata_dict["incubations"][0]["final_concentration"]["unit"]
        )
        assert (
            result["incubations"][0]["incubation_time"]
            == sample_metadata_dict["incubations"][0]["incubation_time"]
        )
        assert result["project"]["name"] == sample_metadata_dict["project"]["name"]
        assert (
            result["project"]["description"]
            == sample_metadata_dict["project"]["description"]
        )

    def test_try_typecast_metadata_file_complete_success(
        self,
        sample_metadata_dict,
        sample_metadata_dict_raw,
        sample_incubation_dict_raw,
        sample_project_dict_raw,
    ):
        sample_metadata_dict_raw["incubations"].append(sample_incubation_dict_raw)
        sample_metadata_dict_raw.update({"project": sample_project_dict_raw})

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)

        assert result is not None

        assert isinstance(result["version"], str)
        assert isinstance(result["datetime"], datetime)
        assert isinstance(result["patient"], dict)
        assert isinstance(result["patient"]["id"], str)
        assert isinstance(result["patient"]["name"], str)
        assert isinstance(result["patient"]["tags"], list)
        assert isinstance(result["patient"]["tags"][0], str)
        assert isinstance(result["image"], dict)
        assert isinstance(result["image"]["created"], datetime)
        assert isinstance(result["image"]["imager"], str)
        assert isinstance(result["image"]["pixel_binning"], int)
        assert isinstance(result["image"]["exposure_time"], timedelta)
        assert isinstance(result["incubations"], list)
        assert isinstance(result["incubations"][0]["solution"], str)
        assert isinstance(result["incubations"][0]["stock_concentration"], dict)
        assert isinstance(
            result["incubations"][0]["stock_concentration"]["value"], float
        )
        assert isinstance(result["incubations"][0]["stock_concentration"]["unit"], str)
        assert isinstance(result["incubations"][0]["final_concentration"], dict)
        assert isinstance(
            result["incubations"][0]["final_concentration"]["value"], float
        )
        assert isinstance(result["incubations"][0]["final_concentration"]["unit"], str)
        assert isinstance(result["incubations"][0]["incubation_time"], timedelta)
        assert isinstance(result["project"], dict)
        assert isinstance(result["project"]["name"], str)
        assert isinstance(result["project"]["description"], str)

        assert result["version"] == sample_metadata_dict["version"]
        assert result["datetime"] == sample_metadata_dict["datetime"]
        assert result["patient"] == sample_metadata_dict["patient"]
        assert result["image"] == sample_metadata_dict["image"]
        assert result["incubations"] == sample_metadata_dict["incubations"]
        assert result["project"] == sample_metadata_dict["project"]

    def test_try_get_validated_metadata_typecasted_complete_success(
        self,
        sample_metadata_dict,
        sample_metadata_dict_natural,
        sample_incubation_dict_raw,
    ):
        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_natural)

        assert result is not None

        assert isinstance(result["version"], str)
        assert isinstance(result["datetime"], datetime)
        assert isinstance(result["patient"], dict)
        assert isinstance(result["patient"]["id"], str)
        assert isinstance(result["patient"]["name"], str)
        assert isinstance(result["patient"]["tags"], list)
        assert isinstance(result["patient"]["tags"][0], str)
        assert isinstance(result["image"], dict)
        assert isinstance(result["image"]["created"], datetime)
        assert isinstance(result["image"]["imager"], str)
        assert isinstance(result["image"]["pixel_binning"], int)
        assert isinstance(result["image"]["exposure_time"], timedelta)
        assert isinstance(result["incubations"], list)
        assert isinstance(result["incubations"][0]["solution"], str)
        assert isinstance(result["incubations"][0]["stock_concentration"], dict)
        assert isinstance(
            result["incubations"][0]["stock_concentration"]["value"], float
        )
        assert isinstance(result["incubations"][0]["stock_concentration"]["unit"], str)
        assert isinstance(result["incubations"][0]["final_concentration"], dict)
        assert isinstance(
            result["incubations"][0]["final_concentration"]["value"], float
        )
        assert isinstance(result["incubations"][0]["final_concentration"]["unit"], str)
        assert isinstance(result["incubations"][0]["incubation_time"], timedelta)
        assert isinstance(result["project"], dict)
        assert isinstance(result["project"]["name"], str)
        assert isinstance(result["project"]["description"], str)

        assert result["version"] == sample_metadata_dict["version"]
        assert result["datetime"] == sample_metadata_dict["datetime"]
        assert result["patient"] == sample_metadata_dict["patient"]
        assert result["image"] == sample_metadata_dict["image"]
        assert result["incubations"] == sample_metadata_dict["incubations"]
        assert result["project"] == sample_metadata_dict["project"]

    def test_try_typecast_metadata_file_no_project_or_incubation_success(
        self, sample_metadata_dict_raw
    ):
        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)

        assert result is not None
        assert isinstance(result["version"], str)
        assert isinstance(result["datetime"], datetime)
        assert isinstance(result["patient"], dict)
        assert isinstance(result["image"], dict)
        assert result["incubations"] == []
        # Will be generated with standard values if there is none
        assert "project" in result.keys()
        assert result["project"]["name"] == "none"
        assert result["project"]["description"] == ""

    def test_try_typecast_metadata_file_no_incubations_success(
        self, sample_metadata_dict_raw, sample_project_dict_raw
    ):
        metadata = sample_metadata_dict_raw
        metadata.update({"project": sample_project_dict_raw})

        result = try_typecast_metadata_file("/test/path", metadata)

        assert result is not None
        assert isinstance(result["version"], str)
        assert isinstance(result["datetime"], datetime)
        assert isinstance(result["patient"], dict)
        assert isinstance(result["image"], dict)
        assert result["incubations"] == []  # sollte leer sein
        assert isinstance(result["project"], dict)  # sollte vorhanden sein
        assert isinstance(result["project"]["name"], str)
        assert isinstance(result["project"]["description"], str)
        assert result["project"] == sample_project_dict_raw

    def test_try_typecast_metadata_file_no_project_success(
        self, sample_metadata_dict_raw, sample_incubation_dict_raw
    ):
        metadata = sample_metadata_dict_raw
        metadata["incubations"].append(sample_incubation_dict_raw)

        result = try_typecast_metadata_file("/test/path", metadata)

        assert result is not None
        assert isinstance(result["version"], str)
        assert isinstance(result["datetime"], datetime)
        assert isinstance(result["patient"], dict)
        assert isinstance(result["image"], dict)
        assert isinstance(result["incubations"], list)
        assert len(result["incubations"]) == 1
        assert isinstance(result["incubations"][0]["solution"], str)
        assert isinstance(result["incubations"][0]["incubation_time"], timedelta)
        # Will be generated with standard values if there is none
        assert "project" in result.keys()
        assert result["project"]["name"] == "none"
        assert result["project"]["description"] == ""

    def test_typecast_invalid_datetime_format(self, sample_metadata_dict_raw):
        sample_metadata_dict_raw["datetime"] = "invalid-date-format"

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)
        assert result is None

    def test_typecast_invalid_image_created_datetime(self, sample_metadata_dict_raw):
        sample_metadata_dict_raw["image"]["created"] = "not-a-date"

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)
        assert result is None

    def test_typecast_invalid_pixel_binning_not_int(self, sample_metadata_dict_raw):
        sample_metadata_dict_raw["image"]["pixel_binning"] = "not-a-number"

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)
        assert result is None

    def test_typecast_invalid_exposure_time_duration(self, sample_metadata_dict_raw):
        sample_metadata_dict_raw["image"]["exposure_time"] = "invalid-duration"

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)
        assert result is None

    def test_typecast_invalid_concentration_values(
        self, sample_metadata_dict_raw, sample_incubation_dict_raw
    ):
        sample_incubation_dict_raw["stock_concentration"]["value"] = "not-a-float"
        sample_metadata_dict_raw["incubations"].append(sample_incubation_dict_raw)

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)
        assert result is None

    def test_typecast_invalid_incubation_time_duration(
        self, sample_metadata_dict_raw, sample_incubation_dict_raw
    ):
        sample_incubation_dict_raw["incubation_time"] = "invalid-duration"
        sample_metadata_dict_raw["incubations"].append(sample_incubation_dict_raw)

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)
        assert result is None

    def test_typecast_empty_patient_tags(self, sample_metadata_dict_raw):
        sample_metadata_dict_raw["patient"]["tags"] = []

        result = try_typecast_metadata_file("/test/path", sample_metadata_dict_raw)
        assert result is not None
        assert result["patient"]["tags"] == []
