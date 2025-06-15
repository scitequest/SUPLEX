import pytest
from datetime import datetime, timedelta
from src.martin_interface.metadata import (
    Patient,
    Image,
    Concentration,
    Incubation,
    Metadata,
)
from dataclasses import is_dataclass


class TestMetadataDataclasses:
    def test_patient_creation(self, sample_metadata_dict):
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
        patient_data = sample_metadata_dict["patient"]
        patient = Patient(
            pat_id=patient_data["id"],
            name=patient_data["name"],
            tags=patient_data["tags"],
        )

        with pytest.raises(AttributeError):
            patient.pat_id = "PAT002"

    def test_image_creation(self, sample_metadata_dict):
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

    def test_concentration_creation(self, sample_incubation_dict_raw):
        conc_data = sample_incubation_dict_raw["stock_concentration"]
        conc = Concentration(value=float(conc_data["value"]), unit=conc_data["unit"])

        assert is_dataclass(conc)

        assert conc.value == float(conc_data["value"])
        assert conc.unit == conc_data["unit"]

    def test_incubation_creation(self, sample_metadata_dict):
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
        assert (
            incubation.stock_concentration.value
            == incub_data["stock_concentration"]["value"]
        )
        assert (
            incubation.final_concentration.value
            == incub_data["final_concentration"]["value"]
        )
        assert incubation.incubation_time == incub_data["incubation_time"]

    def test_metadata_creation_and_properties(self, sample_metadata_dict):
        patient_data = sample_metadata_dict["patient"]
        image_data = sample_metadata_dict["image"]
        incub_data = sample_metadata_dict["incubations"][0]

        patient = Patient(
            patient_data["id"], patient_data["name"], patient_data["tags"]
        )
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
