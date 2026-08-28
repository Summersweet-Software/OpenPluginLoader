"""Packages/Archives plugins into a zip-like format"""

import os
from pathlib import Path
import sys
import tarfile
import tomllib
from typing import Protocol

from openpluginloader.metadata import PluginMetadata
from openpluginloader.utility import get_distribution_paths, get_recursive_includes


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

    def __init__(self, *, extension: str = "tar.gz"):
        self.extension = extension

    def archive_plugin(
        self, meta: PluginMetadata, src: Path, destination: Path
    ) -> Path:
        includes = []
        exclude_paths = [".venv/*", ".env/*"]

        # if destination path exists inside of src path, we should
        #   exclude the destination path
        if destination.full_match(src):
            exclude_paths.append(str(destination.relative_to(src)))

        # Load plugin pyproject config
        if os.path.exists(src / "pyproject.toml"):
            with open(src / "pyproject.toml", "r") as f:
                config = tomllib.loads(f.read())
                plugin_config = config.get("tool", {}).get("plugin", {})
                includes = plugin_config.get("includes", includes)
                exclude_paths = plugin_config.get("exclude_paths", exclude_paths)
                if (new_src := plugin_config.get("src")) is not None:
                    if Path(new_src).is_absolute():
                        src = new_src
                    else:
                        src = src / new_src

        include_dists = get_recursive_includes(includes)

        final_path = destination / f"{meta.plugin_id}.{self.extension}"
        os.makedirs(destination, exist_ok=True)
        if os.path.exists(final_path):
            os.remove(final_path)
        with tarfile.open(final_path, "x:gz") as output_file:
            included_files = []
            print("Adding Include Packages:")
            # add files from includes
            for dist in include_dists:
                print(f"- {dist.name}=={dist.version}")
                # Add every file into tarfile's site-packages.
                for dist_file in get_distribution_paths(dist):
                    if dist_file in included_files:
                        continue
                    included_files.append(dist_file)
                    output_file.add(
                        dist_file.locate(), f"site-packages/{str(dist_file)}"
                    )

            print()
            print("Adding Project Files:")

            for root, _, files in src.walk():
                for proj_file in files:
                    full_path = root / proj_file
                    reparented = full_path.relative_to(src)
                    print(f"- {reparented}")
                    if any(reparented.full_match(item) for item in exclude_paths):
                        continue
                    output_file.add(full_path, str(reparented))

        return final_path
