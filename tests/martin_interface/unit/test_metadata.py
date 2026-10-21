from dataclasses import is_dataclass
from datetime import datetime

import pytest

from suplex.martin_interface.metadata import (
    Concentration,
    Image,
    Incubation,
    Metadata,
    Patient,
)


class TestMetadataDataclasses:
    """Tests for all dataclasses in the metadata module (Patient, Image, Concentration, Incubation, Metadata) and their properties."""

    # -------------------------------------------------------------------------
    # Patient tests
    # -------------------------------------------------------------------------

    def test_patient_creation(self, sample_metadata_dict):
        """Creates a Patient dataclass from raw metadata and verifies all fields."""
        patient_data = sample_metadata_dict["patient"]
        patient = Patient(
            pat_id=patient_data["id"],
            name=patient_data["name"],
            tags=patient_data["tags"],
        )
        assert is_dataclass(patient)

        assert patient.pat_id == patient_data["id"]
        assert patient.name == patient_data["name"]
        assert patient.tags == patient_data["tags"]

    def test_patient_frozen(self, sample_metadata_dict):
        """Patient dataclass is frozen (immutable) and raises AttributeError on mutation."""
        patient_data = sample_metadata_dict["patient"]
        patient = Patient(
            pat_id=patient_data["id"],
            name=patient_data["name"],
            tags=patient_data["tags"],
        )

        with pytest.raises(AttributeError):
            patient.pat_id = "PAT002"

    # -------------------------------------------------------------------------
    # Image tests
    # -------------------------------------------------------------------------

    def test_image_creation(self, sample_metadata_dict):
        """Creates an Image dataclass from raw metadata and verifies all fields."""
        image_data = sample_metadata_dict["image"]

        image = Image(
            created=image_data["created"],
            imager=image_data["imager"],
            pixel_binning=image_data["pixel_binning"],
            exposure_time=image_data["exposure_time"],
        )
        assert is_dataclass(image)

        assert image.created == image_data["created"]
        assert image.imager == image_data["imager"]
        assert image.pixel_binning == image_data["pixel_binning"]
        assert image.exposure_time == image_data["exposure_time"]

    # -------------------------------------------------------------------------
    # Concentration tests
    # -------------------------------------------------------------------------

    def test_concentration_creation(self, sample_incubation_dict_raw):
        """Creates a Concentration dataclass from raw incubation data."""
        conc_data = sample_incubation_dict_raw["stock_concentration"]
        conc = Concentration(value=float(conc_data["value"]), unit=conc_data["unit"])

        assert is_dataclass(conc)

        assert conc.value == float(conc_data["value"])
        assert conc.unit == conc_data["unit"]

    # -------------------------------------------------------------------------
    # Incubation tests
    # -------------------------------------------------------------------------

    def test_incubation_creation(self, sample_metadata_dict):
        """Creates a full Incubation dataclass (including nested Concentration objects)."""
        incub_data = sample_metadata_dict["incubations"][0]
        stock = Concentration(
            incub_data["stock_concentration"]["value"],
            incub_data["stock_concentration"]["unit"],
        )
        final = Concentration(
            incub_data["final_concentration"]["value"],
            incub_data["final_concentration"]["unit"],
        )

        incubation = Incubation(
            solution=incub_data["solution"],
            stock_concentration=stock,
            final_concentration=final,
            incubation_time=incub_data["incubation_time"],
        )

        assert is_dataclass(incubation)

        assert incubation.solution == incub_data["solution"]
        assert incubation.stock_concentration.value == incub_data["stock_concentration"]["value"]
        assert incubation.final_concentration.value == incub_data["final_concentration"]["value"]
        assert incubation.incubation_time == incub_data["incubation_time"]

    # -------------------------------------------------------------------------
    # Metadata tests
    # -------------------------------------------------------------------------

    def test_metadata_creation_and_properties(self, sample_metadata_dict):
        """Creates a complete Metadata instance and verifies all top-level fields + delegated properties."""
        patient_data = sample_metadata_dict["patient"]
        image_data = sample_metadata_dict["image"]
        incub_data = sample_metadata_dict["incubations"][0]

        patient = Patient(patient_data["id"], patient_data["name"], patient_data["tags"])
        image = Image(
            image_data["created"],
            image_data["imager"],
            image_data["pixel_binning"],
            image_data["exposure_time"],
        )
        incubation = Incubation(
            incub_data["solution"],
            Concentration(
                incub_data["stock_concentration"]["value"],
                incub_data["stock_concentration"]["unit"],
            ),
            Concentration(
                incub_data["final_concentration"]["value"],
                incub_data["final_concentration"]["unit"],
            ),
            incub_data["incubation_time"],
        )

        metadata = Metadata(
            version=sample_metadata_dict["version"],
            datetime=sample_metadata_dict["datetime"],
            patient=patient,
            image=image,
            incubations=[incubation],
        )
        assert is_dataclass(metadata)

        assert metadata.version == sample_metadata_dict["version"]
        assert isinstance(metadata.datetime, datetime)

        assert metadata.pat_id == patient_data["id"]
        assert metadata.name == patient_data["name"]
        assert metadata.tags == patient_data["tags"]
        assert metadata.created == image_data["created"]
        assert metadata.imager == image_data["imager"]
        assert metadata.pixel_binning == image_data["pixel_binning"]
        assert metadata.exposure_time == image_data["exposure_time"]
