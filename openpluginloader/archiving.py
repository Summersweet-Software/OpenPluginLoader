"""Packages/Archives plugins into a zip-like format"""

import os
from pathlib import Path
import sys
import tarfile
import tomllib
from typing import Protocol

from openpluginloader.metadata import PluginMetadata


class PluginArchiver(Protocol):
    """The archiving strategy for a plugin"""

    def archive_plugin(
        self, meta: PluginMetadata, src: Path, destination: Path
    ) -> Path: ...

    def dearchive_plugin(self, src: Path, destination: Path) -> Path: ...


class DefaultPluginArchiver:
    """Archives plugins in a targz format"""

    __slots__ = ("extension",)

    extension: str
    """File extension used for file"""

    def __init__(self, *, extension: str = "targz"):
        self.extension = extension

    # def archive_plugin(
    #     self, meta: PluginMetadata, src: Path, destination: Path
    # ) -> Path:
    #     dependencies = []
    #     if os.path.exists(src / "pyproject.toml"):
    #         with open(src / "pyproject.toml", "r") as f:
    #             config = tomllib.loads(f.read())
    #             dependencies = config["dependencies"]

    #     search_paths = sys.path
    #     dep_include_paths: list[Path] = []

    #     for dependency in dependencies:
    #         for search_path in search_paths:
    #             if (
    #                 not os.path.exists(f"{search_path}/{dependency}")
    #                 and not os.path.exists(f"{search_path}/{dependency}.py")
    #                 and not os.path.exists(f"{search_path}/{dependency}.pyd")
    #             ):  # dependency is not found here!
    #                 continue

    #             # get all related children for this
    #             children = [
    #                 child
    #                 for child in os.listdir(search_path)
    #                 if child.startswith(f"{dependency}")
    #             ]

    #             for child in children:
    #                 if not child.startswith(f"{dependency}-") or not child.startswith(
    #                     f".dist-info"
    #                 ):
    #                     continue
    #                 if not os.path.exists(f"{child}/top_level.txt"):
    #                     dep_include_paths.append(dependency)
    #                     continue

    #                 with open(f"{child}/top_level.txt") as f:
    #                     top_levels = f.read().split("\n")
    #                     dep_include_paths.extend(
    #                         Path(top_level) for top_level in top_levels
    #                     )

    #     final_path = src / f"{meta.plugin_id}.{self.extension}"
    #     with tarfile.open(final_path) as file:
    #         # add deps
    #         file.add("", "site-packages/{}")

    #     return final_path

    def archive_plugin(
        self, meta: PluginMetadata, src: Path, destination: Path
    ) -> Path: ...
