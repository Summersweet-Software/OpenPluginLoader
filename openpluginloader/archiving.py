"""Packages/Archives plugins into a zip-like format"""

from pathlib import Path
from typing import Protocol

from openpluginloader.metadata import PluginMetadata


class PluginArchiver(Protocol):
    """The archiving strategy for a plugin"""

    def archive_plugin(
        self, meta: PluginMetadata, src: Path, destination: Path
    ) -> Path: ...

    def dearchive_plugin(self, src: Path, destination: Path) -> Path: ...
