"""Utility functions"""

from contextlib import contextmanager
import sys


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
