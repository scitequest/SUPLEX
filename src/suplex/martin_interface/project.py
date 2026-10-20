class Project:
    """
    A Project serves as a container for datasets, allowing users to organize related
    datasets together using a shared pool of tags.

    Instances of this class allow for a project oriented method to access datasets.
    At the same time instances of `Dataset` also store a reference to their corresponding project.

    Attributes:
        _name (str): The name of the project.
        _description (str): A description of the project.
        _datasets (List): List of datasets contained in this project.
    """

    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
        self._datasets = []

    def add_dataset(self, dataset) -> None:
        """
        Add a dataset to this project.

        Args:
            dataset: The dataset object to be added to the project.
        """
        self._datasets.append(dataset)

    def get_measurement_labels(self) -> list[str]:
        """
        Retrieve measurement labels from all datasets in the project.

        Collects the name labels from each dataset contained in this project
        by calling their get_name_label() method.

        Returns:
            List[str]: A list of measurement label strings, one from each dataset
        """
        ret = []
        for dataset in self._datasets:
            ret.append(dataset.get_name_label())
        return ret

    def get_tags(self) -> list[str]:
        """
        Retrieve all tags from all datasets in the project.

        Aggregates the tags attribute from each dataset in the project,
        combining them into a single flat list.

        Returns:
            List[str]: A list of all tags from every dataset associated with this project.
        """
        tags = []
        for dataset in self._datasets:
            tags += dataset.tags
        return list(set(tags))

    def get_suplex_tags(self) -> list[str]:
        """
        Retrieve all suplex tags from all datasets in the project.

        Aggregates the suplex_tags attribute from each dataset in the project,
        combining them into a single flat list.

        Returns:
            List[str]: A list of all suplex_tags from every dataset associated with this project.
        """
        tags = []
        for dataset in self._datasets:
            tags += dataset.suplex_tags
        return list(set(tags))

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def datasets(self):
        return self._datasets
