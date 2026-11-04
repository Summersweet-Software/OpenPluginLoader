from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from openpluginloader.archiving import PluginArchiver
from openpluginloader.loader import PluginLoader
from openpluginloader.metadata import PluginMetadata, PluginMetadataLoader
from openpluginloader.moduleprovider import PluginModuleProvider
from openpluginloader.versioning import ApiVersion


@dataclass(slots=True)
class Plugin:
    """The metadata of a plugin, as well as all of its necessary
    loading and archiving components."""

    metadata: PluginMetadata

    # load strategies
    metaloader: PluginMetadataLoader
    loader: PluginLoader
    archiver: PluginArchiver

    module_provider: PluginModuleProvider
    """The module provider during regular imports of plugins.
    Finds the plugins and their submodules"""
    module_loadtime_provider: PluginModuleProvider
    """A module provider used during the loading of plugins. Is toggled on/off.
    Finds modules local to plugins themselves.
    """

    scanner_source: "PluginScanner"
    """Which scanner found this plugin"""

    def __eq__(self, other) -> bool:
        return isinstance(other, Plugin) and self.metadata == other.metadata

    def __hash__(self) -> int:
        return hash(self.metadata)


class PluginScanner(Protocol):
    """The plugin scanning strategy used"""

    def get_plugin(self, src: Path, api_version: ApiVersion) -> Plugin | None:
        """Returns a plugin if available at this path"""
        ...

    def get_available_plugins(self, api_version: ApiVersion) -> list[Plugin]: ...


__all__ = ["Plugin", "PluginScanner"]
