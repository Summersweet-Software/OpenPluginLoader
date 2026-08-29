"""Utility functions"""

from contextlib import contextmanager
import importlib.metadata
import sys
from types import ModuleType

from packaging.requirements import Requirement


@contextmanager
def add_search_path(path: str):
    """Temporarily append an item to the search path, remove it when the
    context manager exits"""
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


@contextmanager
def set_meta_paths(hooks: list):
    old = [*sys.meta_path]
    sys.meta_path.clear()
    sys.meta_path.extend(hooks)
    try:
        yield
    finally:
        sys.meta_path.clear()
        sys.meta_path.extend(old)


@contextmanager
def clear_module_caches(default: dict[str, ModuleType] | None = None):
    """Temporarily clear module caches and return them to their previous state
    after the context manager exits"""

    modules = {**sys.modules}

    sys.modules.clear()
    if default is not None:
        sys.modules.update(default)
    try:
        yield
    finally:
        sys.modules.clear()
        sys.modules.update(modules)


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
