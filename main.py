import os
from pathlib import Path
import sys

from openpluginloader.archiving import DefaultPluginArchiver
from openpluginloader.metadata import PluginMetadata
from openpluginloader.versioning import parse_api_version

if __name__ == "__main__":
    archiver = DefaultPluginArchiver()

    meta = PluginMetadata(
        "abby",
        "example",
        Path(),
        parse_api_version("1.0.0"),
        parse_api_version("1.0.0"),
        parse_api_version("1.0.0"),
        [],
        {},
    )

    archiver.archive_plugin(
        meta, Path("example/exampleplugin/"), Path("example/exampleplugin/build")
    )
