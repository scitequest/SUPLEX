import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Any

from suplex.ui.ui_constants import SCHEME_FIELDS

logger = logging.getLogger(__name__)


def load_all_schemes(directory: Path) -> dict[str, Any]:
    """
    Scans the directory for Python files, validates them, and attempts to load
    scheme classes from each valid file. Returns a dictionary mapping scheme
    names to their corresponding scheme objects.

    Args:
        directory: Path to the directory containing scheme files

    Returns:
        Dictionary mapping scheme names to scheme objects
    """
    logger.debug("Loading schemes from directory: %s", directory)

    try:
        if not directory.exists():
            logger.warning("Schemes directory '%s' does not exist", directory)
            return {}

        if not directory.is_dir():
            logger.error("'%s' is not a directory", directory)
            return {}

        python_files = list(directory.glob("*.py"))

        if not python_files:
            logger.warning("No Python files found in schemes directory: %s", directory)
            return {}

        logger.debug("Found %d potential scheme files in directory", len(python_files))

        # Validate and filter files
        valid_files = validate_scheme_files(python_files)
        if not valid_files:
            logger.warning("No valid scheme files found after validation")
            return {}

        # Load schemes from valid files
        schemes = {}
        for file_path in valid_files:
            file_schemes = try_load_schemes_from_file(file_path)
            if not file_schemes:
                continue

            for scheme in file_schemes:
                if hasattr(scheme, "NAME"):
                    schemes[scheme.NAME] = scheme
                    logger.debug("Loaded scheme '%s' from file: %s", scheme.NAME, file_path.name)
                else:
                    logger.warning(
                        "Scheme class missing NAME attribute in file: %s",
                        file_path.name,
                    )

        logger.debug(
            "Successfully loaded %d schemes from %d files",
            len(schemes),
            len(valid_files),
        )
        return schemes

    except Exception as e:
        logger.error(
            "Failed to load schemes from directory '%s': %s",
            directory,
            e,
            exc_info=True,
        )
        return {}


def validate_scheme_files(python_files: list[Path]) -> list[Path]:
    """
    Validate that Python files meet requirements for being scheme files.
    Filters out system files, test files, and other non-scheme files based
    on naming conventions and file characteristics.

    Args:
        python_files: List of Python file paths to validate

    Returns:
        List of validated Python file paths that may contain schemes
    """
    logger.debug("Validating %d Python files for scheme loading", len(python_files))

    valid_files = []

    for file_path in python_files:
        try:
            if is_system_file(file_path):
                logger.debug("Skipping system/default file: %s", file_path.name)
                continue

            # Additional validation rules can be added here
            if not file_path.is_file():
                logger.debug("Skipping non-file path: %s", file_path)
                continue

            if file_path.stat().st_size == 0:
                logger.debug("Skipping empty file: %s", file_path.name)
                continue

            valid_files.append(file_path)
            logger.debug("Validated file for scheme loading: %s", file_path.name)

        except Exception as e:
            logger.error("Error validating file '%s': %s", file_path.name, e, exc_info=True)
            continue

    logger.debug("Validated %d files out of %d candidates", len(valid_files), len(python_files))
    return valid_files


def is_system_file(file_path: Path) -> bool:
    """
    Identifies files that should not be processed as scheme files based on
    naming conventions (e.g., __init__.py, test files, hidden files).

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file should be skipped, False otherwise
    """
    try:
        filename = file_path.name.lower()

        # Python system files (__init__.py, __main__.py, etc.)
        if filename.startswith("__") and filename.endswith("__.py"):
            return True

        # Common Python system/setup files
        system_files = {"setup.py", "conftest.py", "config.py"}
        if filename in system_files:
            return True

        # Test files
        if filename.startswith("test_") or filename.endswith("_test.py"):
            return True

        # Hidden files (Unix convention)
        if filename.startswith("."):
            return True

        # Backup and temporary files
        backup_extensions = {".tmp", ".bak", ".backup", ".old"}
        if any(filename.endswith(ext) for ext in backup_extensions):
            return True

        return False

    except Exception as e:
        logger.error(
            "Error checking if file is system file: %s - %s",
            file_path,
            e,
            exc_info=True,
        )
        return True  # Skip files that can't be checked safely


def try_load_schemes_from_file(file_path: Path) -> list[Any]:
    """
    Dynamically imports the specified file and extracts all classes that
    match the required scheme schema. Handles import errors gracefully.

    Args:
        file_path: Path to the Python file to load schemes from

    Returns:
        List of scheme class objects that passed validation
    """
    logger.debug("Attempting to load schemes from file: %s", file_path)

    module_name = file_path.stem
    scheme_classes = []

    try:
        # Create module spec from file
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            logger.warning("Could not create module spec for file: %s", file_path)
            return scheme_classes

        # Load and execute module
        module = importlib.util.module_from_spec(spec)

        # Add to sys.modules to handle potential circular imports
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error("Failed to execute module '%s': %s", file_path, e, exc_info=True)
            return scheme_classes
        finally:
            # Clean up sys.modules to avoid pollution
            if module_name in sys.modules:
                del sys.modules[module_name]

        # Extract and validate scheme classes
        classes_found = 0
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip imported classes (only load classes defined in this module)
            if obj.__module__ != module_name:
                continue

            classes_found += 1
            logger.debug("Found class '%s' in module '%s'", name, module_name)

            if validate_against_schema(SCHEME_FIELDS, obj):
                scheme_classes.append(obj)
                logger.debug("Successfully validated scheme class: %s", name)
            else:
                logger.debug("Class '%s' did not pass scheme validation", name)

        logger.debug(
            "Found %d classes, validated %d schemes from file: %s",
            classes_found,
            len(scheme_classes),
            file_path.name,
        )

    except ImportError as e:
        logger.error("Import error loading schemes from '%s': %s", file_path, e)
    except SyntaxError as e:
        logger.error("Syntax error in scheme file '%s': %s", file_path, e)
    except Exception as e:
        logger.error(
            "Unexpected error loading schemes from '%s': %s",
            file_path,
            e,
            exc_info=True,
        )

    return scheme_classes


def validate_against_schema(schema: dict[str, Any], test_obj: Any, path: str = "") -> bool:
    """
    Recursively checks that the object has all required attributes and that
    nested objects (classes) also match their expected structure. This ensures
    that scheme objects conform to the expected interface.

    Args:
        schema: Dictionary defining the expected structure and types
        test_obj: Object to validate against the schema
        path: Current path in the validation (for error reporting)

    Returns:
        True if the object matches the schema, False otherwise

    """
    logger.debug(
        "Validating object against schema: %s",
        getattr(test_obj, "__name__", str(test_obj)),
    )

    try:
        for field_name, expected_type in schema.items():
            current_path = f"{path}.{field_name}" if path else field_name

            # Check if required attribute exists
            if not hasattr(test_obj, field_name):
                logger.debug(
                    "Missing required attribute '%s' in %s",
                    current_path,
                    getattr(test_obj, "__qualname__", str(test_obj)),
                )
                return False

            attribute_value = getattr(test_obj, field_name)

            # Handle nested class structure validation
            if isinstance(expected_type, dict):
                if not inspect.isclass(attribute_value):
                    logger.debug(
                        "Expected class at '%s', got %s",
                        current_path,
                        type(attribute_value),
                    )
                    return False

                # Recursively validate nested class structure
                if not validate_against_schema(expected_type, attribute_value, current_path):
                    logger.debug("Nested validation failed for '%s'", current_path)
                    return False

            # Handle type validation for simple types
            elif isinstance(expected_type, type):
                if not isinstance(attribute_value, expected_type):
                    logger.debug(
                        "Type mismatch at '%s': expected %s, got %s",
                        current_path,
                        expected_type.__name__,
                        type(attribute_value).__name__,
                    )
                    return False

            # Handle callable validation
            elif callable(expected_type):
                try:
                    if not expected_type(attribute_value):
                        logger.debug("Validation function failed for '%s'", current_path)
                        return False
                except Exception as e:
                    logger.debug("Error in validation function for '%s': %s", current_path, e)
                    return False
            else:
                logger.warning("Unknown expected type for '%s': %s", current_path, expected_type)

        logger.debug(
            "Schema validation passed for object: %s",
            getattr(test_obj, "__name__", str(test_obj)),
        )
        return True

    except Exception as e:
        logger.error(
            "Error during schema validation for %s: %s",
            getattr(test_obj, "__name__", str(test_obj)),
            e,
            exc_info=True,
        )
        return False


def get_schemes(schemes_directory: str = "schemes") -> dict[str, Any]:
    """
    Convenience function that constructs the full path to the schemes directory
    and loads all valid schemes found within it.

    Args:
        schemes_directory: Name of the schemes directory relative to this module

    Returns:
        Dictionary mapping scheme names to scheme objects

    """
    logger.debug("Loading schemes from directory: %s", schemes_directory)

    try:
        # Construct path relative to this module
        current_file = Path(__file__)
        schemes_path = current_file.parent / schemes_directory

        logger.debug("Resolved schemes path: %s", schemes_path.absolute())

        schemes = load_all_schemes(schemes_path)

        if not schemes:
            logger.warning("No schemes loaded from directory: %s", schemes_directory)
        else:
            logger.debug("Successfully loaded %d schemes", len(schemes))

        return schemes

    except Exception as e:
        logger.error(
            "Failed to get schemes from directory '%s': %s",
            schemes_directory,
            e,
            exc_info=True,
        )
        return {}
