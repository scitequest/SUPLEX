from enum import Enum
import os
from collections import deque
import logging
from typing import List, Set
from .martin_interface_constants import SEARCH_MODE

logger = logging.getLogger(__name__)


def delve_dirs(path: str, target_files: List[str], detected_file_dirs: Set[str] = None) -> Set[str]:
    """
    Recursively search for directories containing target files and return them as a set.

    Args:
        path (str): Directory path to search.
        target_files (list): List of file names to in dir structure.
        detecte_file_dirs (set, optional): Set of parent directory paths containing target files, initialized if None.

    Returns:
        set: Set of unique parent directory paths containing target files
    """
    if detected_file_dirs is None:
        detected_file_dirs = set()
    try:
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            if os.path.isdir(itempath):
                delve_dirs(
                    path=itempath,
                    target_files=target_files,
                    detected_file_dirs=detected_file_dirs,
                )
            elif os.path.isfile(itempath) and item in target_files:
                detected_file_dirs.add(path)
    except PermissionError as e:
        logger.warning(f"Cannot access {path}: {e}")
        return detected_file_dirs
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return detected_file_dirs

    return detected_file_dirs


def sweep_dirs(
    root_path: str, target_files: List[str], mode: SEARCH_MODE, max_depth: int = 0
) -> Set[str]:
    """
    Iteratively search for parent directories containing target files based on mode.
    For description of search modes see documentation in constants.

    Args:
        rootPath (str): Starting directory path.
        target_files (list): List of file names to find.
        mode (SEARCH_MODE): Search mode from SEARCH_MODE enum.
        maxDepth (int, optional): Depth limit for bounded modes (0 = root only, etc.).

    Returns:
        set: Set of unique parent directory paths containing target files.
    """
    detected_file_dirs = set()
    # Stores tuples of (current_path, current_depth) starting at root_path.
    queue = deque([(root_path, 0)])

    while queue:
        current_dir, depth = queue.popleft()

        # Max depth limiter for bound search modes.
        if mode is not SEARCH_MODE.ITERATIVE_UNBOUND and depth > max_depth:
            continue

        try:
            # Get directory contents
            with os.scandir(current_dir) as entries:
                for item in entries:
                    if item.is_file() and item.name in target_files:
                        # Check limiters for each mode.
                        if (
                            mode is SEARCH_MODE.ITERATIVE_UNBOUND
                            or mode is SEARCH_MODE.ITERATIVE_BOUNDED_ALL
                            and depth <= max_depth
                            or mode is SEARCH_MODE.ITERATIVE_BOUNDED_BOTTOM
                            and depth == max_depth
                        ):

                            detected_file_dirs.add(current_dir)
                    elif item.is_dir():
                        if mode is SEARCH_MODE.ITERATIVE_UNBOUND or depth < max_depth:
                            queue.append((os.path.join(current_dir, item.name), depth + 1))

        except PermissionError as e:
            logger.warning(f"Cannot access {current_dir}: {e}")
            continue
        except Exception as e:
            logger.error(f"Exception occured: {e}")
            continue

    return detected_file_dirs
