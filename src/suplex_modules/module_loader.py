import os
import sys
import importlib.util
import inspect
import ast
import logging
from collections import deque
from enum import Enum
from typing import Any, Type, List, Set, Tuple, Optional

from .suplex_module_interface import SuplexModuleInterface
from .module_constants import (
    DEFAULT_MODULE_DIRECTORY,
    DEFAULT_SEARCH_DEPTH,
    STANDARD_READOUT_FILE_TYPE,
    SEARCH_MODE,
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_FILES,
    DEFAULT_IGNORE_EXTENSIONS,
)

logger = logging.getLogger(__name__)


def load_modules(
    dir_path: str = DEFAULT_MODULE_DIRECTORY,
    max_depth: int = DEFAULT_SEARCH_DEPTH,
    filetype: str = STANDARD_READOUT_FILE_TYPE,
    mode: SEARCH_MODE = SEARCH_MODE.RECURSIVE,
    ignore_dirs: Set[str] = DEFAULT_IGNORE_DIRS,
    ignore_files: Set[str] = DEFAULT_IGNORE_FILES,
    ignore_extensions: Set[str] = DEFAULT_IGNORE_EXTENSIONS,
) -> List[SuplexModuleInterface]:
    """
    Load suplex modules from a given directory.
    This is supposed to be used upon startup of the software to scan the modules directory.

    In principle it should also be possible to load additional modules from a second source using this code.
    However this is not implemented, but might be of interest in later versions.

    Args:
        max_depth (int): Maximum depth to search (only relevant for bounded modes). Defaults to DEFAULT_SEARCH_DEPTH.
        filetype (str): Filetype of suplex modules. Defaults to STANDARD_READOUT_FILE_TYPE.
        mode (SEARCH_MODE): Search mode from SEARCH_MODE enum. Defaults to SEARCH_MODE.RECURSIVE.
        ignore_dirs (Set[str]): Set of directory names to ignore. Defaults to DEFAULT_IGNORE_DIRS.
        ignore_files (Set[str]): Set of file names to ignore. Defaults to DEFAULT_IGNORE_FILES.
        ignore_extensions (Set[str]): Set of file extensions to ignore. Defaults to DEFAULT_IGNORE_EXTENSIONS.

    Returns:
        List of Modules derived from SuplexModuleInterface
    """
    if mode == SEARCH_MODE.RECURSIVE:
        files = set()
        delve_dirs(
            search_dir=dir_path,
            filetype=filetype,
            files=files,
            ignore_dirs=ignore_dirs,
            ignore_files=ignore_files,
            ignore_extensions=ignore_extensions,
        )
    else:
        files = sweep_dirs(
            root_path=dir_path,
            filetype=filetype,
            mode=mode,
            max_depth=max_depth,
            ignore_dirs=ignore_dirs,
            ignore_files=ignore_files,
            ignore_extensions=ignore_extensions,
        )

    logger.debug(f"Collected a total of {len(files)} files")
    modules = []
    for file_path in files:
        # The method try_get_module returns an empty list if file is invalid.
        modules += try_get_module(file_path)

    return modules


def delve_dirs(
    search_dir: str,
    filetype: str,
    files: Set[str],
    ignore_dirs: Set[str] = DEFAULT_IGNORE_DIRS,
    ignore_files: Set[str] = DEFAULT_IGNORE_FILES,
    ignore_extensions: Set[str] = DEFAULT_IGNORE_EXTENSIONS,
) -> None:
    """
    Recursively search directories for potentially compatible modules.

    Args:
        search_dir (str): Directory path to search
        filetype (str): Filetype of suplex modules.
        modules (List[str]): List to append found file directories.
        ignore_dirs (Set[str]): Set of directory names to ignore.
        ignore_files (Set[str]): Set of file names to ignore.
        ignore_extensions (Set[str]): Set of file extensions to ignore.
    """
    try:
        with os.scandir(search_dir) as entries:
            for entry in entries:
                if entry.is_dir():
                    if should_ignore_directory(entry.name, ignore_dirs):
                        logger.debug(f"Ignoring directory: {entry.path}")
                        continue
                    delve_dirs(
                        search_dir=entry.path,
                        filetype=filetype,
                        files=files,
                        ignore_dirs=ignore_dirs,
                        ignore_files=ignore_files,
                        ignore_extensions=ignore_extensions,
                    )

                elif entry.is_file():
                    if should_ignore_file(entry.name, ignore_files, ignore_extensions):
                        logger.debug(f"Ignoring file: {entry.path}")
                        continue

                    if entry.name.endswith(filetype):
                        logger.debug(f"Found file: {entry.path}")
                        files.add(entry.path)

    except PermissionError as e:
        logger.warning(f"Cannot access {search_dir}: {e}")
    except Exception as e:
        logger.error(f"Exception occurred while scanning {search_dir}: {e}")


def sweep_dirs(
    root_path: str,
    filetype: str,
    mode: SEARCH_MODE,
    max_depth: int,
    ignore_dirs: Set[str],
    ignore_files: Set[str],
    ignore_extensions: Set[str],
) -> Set[str]:
    """
    Iteratively search directories for potentially compatible modules.

    This method allows for three modes:
    - ITERATIVE_BOUNDED_BOTTOM: Traverse a directory to a defined depth and search for files at the bottom.
    - ITERATIVE_BOUNDED_ALL: Traverse a directory to a defined depth and search for files at every subdirectory.
    - ITERATIVE_UNBOUND: Search an entire directory for files iterativeley.

    Args:
        root_path: Starting directory path
        mode: Search mode from SEARCH_MODE enum
        max_depth: Depth limit for bounded modes (0 = root only)
        ignore_dirs: Set of directory names to ignore
        ignore_files: Set of file names to ignore
        ignore_extensions: Set of file extensions to ignore

    Returns:
        A set of file paths
    """
    files = set()
    # Queue stores tuples of (current_path, current_depth)
    queue = deque([(root_path, 0)])

    while queue:
        current_dir, depth = queue.popleft()
        if mode != SEARCH_MODE.ITERATIVE_UNBOUND and depth > max_depth:
            continue

        try:
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    if entry.is_dir():
                        if should_ignore_directory(entry.name, ignore_dirs):
                            logger.debug(f"Ignoring directory: {entry.path}")
                            continue
                        # Add subdirectory to queue if we have not exceeded depth limit
                        if mode == SEARCH_MODE.ITERATIVE_UNBOUND or depth < max_depth:
                            queue.append((entry.path, depth + 1))

                    elif entry.is_file():
                        if should_ignore_file(
                            entry.name, ignore_files, ignore_extensions
                        ):
                            logger.debug(f"Ignoring file: {entry.path}")
                            continue
                        if entry.name.endswith(filetype):
                            if should_collect_at_depth(mode, depth, max_depth):
                                files.add(entry.path)
                                logger.debug(f"Added Python file: {entry.path}")

        except PermissionError as e:
            logger.warning(f"Cannot access {current_dir}: {e}")
            continue
        except Exception as e:
            logger.error(f"Exception occurred while scanning {current_dir}: {e}")
            continue

    return files


def should_ignore_directory(dir_name: str, ignore_dirs: Set[str]) -> bool:
    """
    Check if a directory should be ignored based on ignore patterns.

    Args:
        dir_name (str): Name of the directory
        ignore_dirs (Set[str]): Set of directory names to ignore

    Returns:
        True if directory should be ignored, else False
    """
    if dir_name in ignore_dirs:
        return True

    # Hidden directories (starting with .)
    if dir_name.startswith("."):
        return True

    # Check for common patterns
    if any(pattern in dir_name.lower() for pattern in ["cache", "temp", "tmp"]):
        return True

    return False


def should_ignore_file(
    file_name: str, ignore_files: Set[str], ignore_extensions: Set[str]
) -> bool:
    """
    Check if a file should be ignored based on ignore patterns.
    As we only search for very specific file types this method is a bit redundant.
    However we consider it to be good practice and it also may provide some use in future versions of suplex.

    Args:
        file_name (str): Name of the file
        ignore_files (Set[str]): Set of file names to ignore
        ignore_extensions (Set[str]): Set of file extensions to ignore

    Returns:
        True if file should be ignored, False otherwise
    """
    if file_name in ignore_files:
        return True

    # Hidden files (starting with .)
    if file_name.startswith("."):
        return True

    for ext in ignore_extensions:
        if file_name.endswith(ext):
            return True

    # Check for temporary/backup files
    if file_name.endswith((".tmp", ".bak", ".swp", "~")):
        return True

    # Check for test files
    if file_name.startswith("test_"):
        return True

    return False


def should_collect_at_depth(
    mode: SEARCH_MODE, current_depth: int, max_depth: int
) -> bool:
    """
    Determine if files should be collected at the current depth based on search mode.

    Args:
        mode: Search mode
        current_depth: Current traversal depth
        max_depth: Maximum allowed depth

    Returns:
        True if files should be collected at this depth
    """
    if mode == SEARCH_MODE.ITERATIVE_UNBOUND:
        return True
    elif mode == SEARCH_MODE.ITERATIVE_BOUNDED_ALL:
        return current_depth <= max_depth
    elif mode == SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM:
        return current_depth == max_depth
    return False


def try_get_module(file_path: str) -> List[SuplexModuleInterface]:
    """
    Attempts to load SUPLEX compatible modules from a given file.
    Returns a list as a file may contain multiple modules.
    Safely load compatible modules from a Python file with proper error handling.

    Args:
        file_path: Path to a file potentially containing modules.

    Returns:
        List of instantiated SUPLEX modules derived from SuplexModuleInterface
        or an empty list if file was invalid or does not contain a SUPLEX module.
    """
    module_objects = []
    try:
        if not has_suplex_interface_classes(file_path):
            return []

        python_module_name = os.path.splitext(os.path.basename(file_path))[0]
        # Dynamically load the module - spec contains name, dir and blueprint of module.
        spec = importlib.util.spec_from_file_location(python_module_name, file_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not create module spec for {file_path}")
            return []

        # Generate empty module container.
        module = importlib.util.module_from_spec(spec)
        # Fill container with explicit module information.
        spec.loader.exec_module(module)

        # Find SuplexModuleInterface implementations.
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if is_valid_suplex_module_class(
                obj, python_module_name, SuplexModuleInterface
            ):
                try:
                    instance = obj()
                    module_objects.append(instance)
                    logger.debug(f"Successfully loaded {name} from {file_path}")
                except Exception as e:
                    logger.warning(
                        f"Failed to instantiate {name} from {file_path}: {e}"
                    )

    # Do not load from erroneus files
    except (OSError, SyntaxError, ImportError) as e:
        logger.error(f"Error loading module from {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading module from {file_path}: {e}")
        return []

    return module_objects


def has_suplex_interface_classes(file_path: str) -> bool:
    """
    Check if a Python file contains classes that might implement SuplexModuleInterface.
    This is done without executing any code (via AST parsing) in said file.

    Args:
        file_path: Path to the Python file

    Returns:
        True if file likely contains SuplexModuleInterface implementations, False if otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        node = ast.parse(content, filename=file_path)

        aliases = set()  # collect aliases for later on class inheritance check

        # Check for SuplexModuleInterface imports
        has_interface_import = False
        for item in node.body:
            if isinstance(item, ast.ImportFrom):
                # Check if importing `from` SuplexModuleInterface module
                if item.module and (
                    item.module == "SuplexModuleInterface"
                    or item.module.endswith(".SuplexModuleInterface")
                ):
                    has_interface_import = True
                    aliases.update(alias.asname for alias in item.names if alias.asname)
                    break
                # Check if SuplexModuleInterface is among the imported names
                if item.names and any(
                    alias.name == "SuplexModuleInterface" for alias in item.names
                ):
                    has_interface_import = True
                    aliases.update(
                        alias.asname
                        for alias in item.names
                        if alias.asname and alias.name == "SuplexModuleInterface"
                    )
                    break
            # For direct `import` statements.
            elif isinstance(item, ast.Import):
                if item.names and any(
                    alias.name == "SuplexModuleInterface" for alias in item.names
                ):
                    has_interface_import = True
                    aliases.update(
                        alias.asname
                        for alias in item.names
                        if alias.asname
                        and (
                            alias.name == "SuplexModuleInterface"
                            or alias.name.endswith(".SuplexModuleInterface")
                        )
                    )
                    break
        if not has_interface_import:
            return False

        # Look for class definitions with base classes recursively within the whole AST (`walk`).
        for item in ast.walk(node):
            # item is class and has a base class.
            if isinstance(item, ast.ClassDef) and item.bases:
                # Might have multiple base classes, check if any references SuplexModuleInterface
                for base in item.bases:
                    # Check for simple import of interface
                    if (
                        isinstance(base, ast.Name)
                        and "SuplexModuleInterface" in base.id
                    ):
                        return True
                    if isinstance(base, ast.Name) and base.id in aliases:
                        return True
                    elif isinstance(base, ast.Attribute):
                        attr_name = ""
                        current = base
                        # Decode AST structure into usable string
                        while isinstance(current, ast.Attribute):
                            attr_name = current.attr + (
                                "." + attr_name if attr_name else ""
                            )
                            current = current.value
                        if isinstance(current, ast.Name):
                            attr_name = current.id + (
                                "." + attr_name if attr_name else ""
                            )
                        if "SuplexModuleInterface" in attr_name:
                            return True

        return False

    except (OSError, SyntaxError, UnicodeDecodeError) as e:
        logger.warning(f"Could not parse {file_path}: {e}")
        return False


def is_valid_suplex_module_class(
    obj: Any, module_name: str, interface_class: Type
) -> bool:
    """
    Checks if an object is a valid SUPLEX plugin class.

    Validates that the object is a class that inherits from SuplexModuleInterface,
    is defined in the current module (not imported), and is not the interface itself.

    Args:
        obj: Object to validate (typically from inspect.getmembers)
        module_name: Name of the Python module being inspected
        interface_class: SuplexModuleInterface class that plugins must inherit from

    Returns:
        bool: True if obj is a valid SUPLEX plugin class, False otherwise
    """
    if not hasattr(obj, "__module__"):
        return False
    if obj.__module__ != module_name:
        return False
    try:
        if not issubclass(obj, interface_class):
            return False
    except TypeError:
        # issubclass() fails if obj is not a class
        return False
    if obj is interface_class:
        return False
    return True
