"""
Constants and enumerations for SUPLEX submodule components.

This module defines the core enumerations used throughout the SUPLEX submodule
system for dataset selection, labeling, and tag filtering operations.
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DATASET_LABEL(Enum):
    """
    Enumeration for dataset labeling options.

    Defines the different types of information that can be displayed
    in dataset labels within the user interface:
    - Name: Informal name of dataset.
    - ID: Formal identifier of dataset.
    - CREATED_DATE: Date the image was generated (typically the same day the assay was conducted).
    - MEASURE_DATE: Date the measurement was taken via MARTin.
    """

    NAME = "name"
    ID = "id"
    CREATED_DATE = "Image created"
    MEASURE_DATE = "Measured"


class DATASET_SELECTOR_MODE(Enum):
    """
    Enumeration for dataset selection modes.

    Defines how many datasets can be selected and the behavior
    when selection limits are reached:
    - SINGLE: Only one dataset can be selected
    - MULTIPLE_UNBOUND: Unlimited multiple selection
    - MULTIPLE_BOUND: Limited multiple selection with queue
    """

    SINGLE = "single"
    MULTIPLE_UNBOUND = "multiple_unbound"
    MULTIPLE_BOUND = "multiple_bound"


class TAG_SELECTION_MODE(Enum):
    """
    Enumeration for tag-based dataset filtering modes.

    Defines the logical relationship between selected tags when
    filtering datasets:
    - ANY: Match datasets with any of the selected tags (OR logic)
    - ALL: Match datasets with all of the selected tags (AND logic)
    """

    ANY = "any"
    ALL = "all"
