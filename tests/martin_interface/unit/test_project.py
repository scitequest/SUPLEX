from unittest.mock import Mock

from suplex.martin_interface.project import Project


class TestProject:
    """Tests for the Project class that acts as a container for related Datasets."""

    # -------------------------------------------------------------------------
    # Project creation and basic properties
    # -------------------------------------------------------------------------

    def test_project_creation(self, sample_project_dict_raw):
        """Creates a Project from raw dictionary data and verifies name, description, and empty datasets list."""
        project = Project(
            name=sample_project_dict_raw["name"],
            description=sample_project_dict_raw["description"],
        )

        assert project.name == sample_project_dict_raw["name"]
        assert project.description == sample_project_dict_raw["description"]
        assert project.datasets == []

    def test_properties_immutable(self, sample_project_dict_raw):
        """Verifies that the public properties return correct values and that datasets is a list."""
        project = Project(sample_project_dict_raw["name"], sample_project_dict_raw["description"])

        assert project.name == sample_project_dict_raw["name"]
        assert project.description == sample_project_dict_raw["description"]
        assert isinstance(project.datasets, list)

    # -------------------------------------------------------------------------
    # Dataset management
    # -------------------------------------------------------------------------

    def test_add_dataset(self, sample_project_dict_raw):
        """Adds a mock dataset to the project and confirms it appears in the datasets list."""
        project = Project(sample_project_dict_raw["name"], sample_project_dict_raw["description"])
        mock_dataset = Mock()

        project.add_dataset(mock_dataset)

        assert len(project.datasets) == 1
        assert project.datasets[0] == mock_dataset

    # -------------------------------------------------------------------------
    # Label and tag aggregation methods
    # -------------------------------------------------------------------------

    def test_get_measurement_labels(self, sample_project_dict_raw):
        """Collects measurement labels from all datasets in the project via get_name_label()."""
        project = Project(sample_project_dict_raw["name"], sample_project_dict_raw["description"])

        mock_dataset1 = Mock()
        mock_dataset1.get_name_label.return_value = "Label1"
        mock_dataset2 = Mock()
        mock_dataset2.get_name_label.return_value = "Label2"

        project.add_dataset(mock_dataset1)
        project.add_dataset(mock_dataset2)

        labels = project.get_measurement_labels()

        assert labels == ["Label1", "Label2"]

    def test_get_tags(self, sample_project_dict_raw):
        """Aggregates and deduplicates all tags from every dataset in the project."""
        project = Project(sample_project_dict_raw["name"], sample_project_dict_raw["description"])

        mock_dataset1 = Mock()
        mock_dataset1.tags = ["tag1", "tag2"]
        mock_dataset2 = Mock()
        mock_dataset2.tags = ["tag2", "tag3"]

        project.add_dataset(mock_dataset1)
        project.add_dataset(mock_dataset2)

        tags = project.get_tags()

        assert set(tags) == {"tag1", "tag2", "tag3"}

    def test_get_suplex_tags(self, sample_project_dict_raw, sample_suplex_dict):
        """Aggregates and deduplicates all suplex_tags from every dataset in the project."""
        project = Project(sample_project_dict_raw["name"], sample_project_dict_raw["description"])

        mock_dataset1 = Mock()
        mock_dataset1.suplex_tags = sample_suplex_dict["tags"][:1]
        mock_dataset2 = Mock()
        mock_dataset2.suplex_tags = sample_suplex_dict["tags"][1:]

        project.add_dataset(mock_dataset1)
        project.add_dataset(mock_dataset2)

        suplex_tags = project.get_suplex_tags()

        assert set(suplex_tags) == set(sample_suplex_dict["tags"])
