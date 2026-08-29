from pathlib import Path
import sys
from typing import Protocol

from openpluginloader.archiving import PluginArchiver
from openpluginloader.metadata import PluginMetadata, PluginMetadataLoader
from openpluginloader.scanner import PluginScanner
from openpluginloader.versioning import ApiVersion


class PluginLoader(Protocol):
    """An individual strategy used to load a plugin.
    It acts as a collection of functions to control how
    plugins are imported
    """

    def load_plugin(self, plugin):
        """Loads an individual plugin"""
        ...

    def sort_plugins_by_load_order(
        self, plugins: list[PluginMetadata]
    ) -> list[PluginMetadata]:
        """Determines the load order of plugins"""
        ...


class PluginManager:
    """A configurable plugin manager class.
    Scans for and loads plugins using configured loader classes."""

    __slots__ = (
        "metadata_loader",
        "loading_strategy",
        "archiver",
        "plugin_scanner",
        "api_version",
        "import_hooks",
    )

    metadata_loader: PluginMetadataLoader
    """Controls how metadata is loaded"""

    loading_strategy: PluginLoader
    """Determines what happens when a plugin actually gets loaded."""

    archiver: PluginArchiver
    """Determines how plugins get archived."""

    plugin_scanner: PluginScanner
    """Determines how plugins are discovered/located."""

    api_version: ApiVersion
    """The current api version of your plugin api."""

    import_hooks: list
    """List of import hooks that need to be installed before plugins can be loaded"""

    def __init__(
        self,
        *,
        metadata_loader: PluginMetadataLoader,
        loading_strategy: PluginLoader,
        archiver: PluginArchiver,
        plugin_scanner: PluginScanner,
        api_version: ApiVersion,
        import_hooks: list,
    ):
        self.metadata_loader = metadata_loader
        self.loading_strategy = loading_strategy
        self.archiver = archiver
        self.plugin_scanner = plugin_scanner
        self.api_version = api_version
        self.import_hooks = import_hooks

    def initialize_hooks(self):
        """Initialize all import hooks and machinery"""
        for hook in self.import_hooks[::-1]:
            sys.meta_path.insert(0, hook)

    def deinitialize_hooks(self):
        """I would not personally recommend using this!
        This is only provided as a convience and a way to standardize
        this sort of behavior. I doubt it should be used in most projects...
        well... unless you want to... ah nvm
        """
        sys.path_hooks

        for hook in self.import_hooks:
            sys.meta_path.remove(hook)

    def archive_plugin(self, src: Path, dest: Path) -> Path:
        meta = self.metadata_loader.load_metadata(src, self.api_version)
        return self.archiver.archive_plugin(meta, src, dest)


__all__ = ["PluginManager", "PluginLoader"]
