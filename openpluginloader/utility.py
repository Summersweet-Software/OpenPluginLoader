"""Utility functions"""

from contextlib import contextmanager
import importlib.metadata
from pathlib import Path
import sys

import packaging
from packaging.requirements import Requirement


@contextmanager
def add_search_path(path: str):
    """Temporarily append an item to the search path, remove it when the context manager exits"""
    index = len(sys.path)
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path.pop(index)


@contextmanager
def set_search_path(new_path: list[str]):
    """Temporarily set the search path, reset it when the context manager exits"""
    old = [*sys.path]
    sys.path.clear()
    sys.path.extend(new_path)
    try:
        yield
    finally:
        sys.path.clear()
        sys.path.extend(old)


def get_recursive_includes(
    includes: list[str],
) -> list[importlib.metadata.Distribution]:
    """Takes the name of an include and gets a recursive list of
    dependency includes."""

    output: list[importlib.metadata.Distribution] = []
    to_search = [importlib.metadata.distribution(include) for include in includes]

    while len(to_search) > 0:
        current = to_search.pop(0)
        to_search.extend(
            importlib.metadata.distribution(parsed.name)
            for requirement in (current.requires or [])
            if (parsed := Requirement(requirement)).name
            not in (item.name for item in output)
            and (parsed.marker is None or parsed.marker.evaluate())
        )

        output.append(current)

    return output


def get_distribution_paths(
    dist: importlib.metadata.Distribution,
) -> list[importlib.metadata.PackagePath]:
    """Normalizes dist.files (used to do more. that is why this still exists)"""
    if dist.files is None:
        return []

    return dist.files
