from typing import Protocol

from openpluginloader.metadata import PluginMetadata
from openpluginloader.versioning import ApiVersion


class PluginLoader(Protocol):
    """An individual strategy used to load a plugin.
    It acts as a collection of functions to control how
    plugins are imported
    """

    def load_config(self) -> PluginMetadata:
        """Loads a plugins config"""
        ...

    def load_plugin(self, plugin):
        """Loads an individual plugin"""
        ...

    def sort_plugins_by_load_order(
        self, plugins: list[PluginMetadata]
    ) -> list[PluginMetadata]:
        """"""
        ...


class ImportLoader:
    """The default loading strategy for plugins.
    Uses dynamic imports and temporarily modifies python's path environment.
    """

    # TODO: look into path hooks, info is a little lacking on them


class PluginManager:
    """A configurable plugin manager class.
    Scans for and loads plugins using configured loader classes."""

    __slots__ = ()

    loading_stategy: PluginLoader
    """Determines what happens when a plugin actually gets loaded."""

    api_version: ApiVersion
    """The current api version of your plugin api."""
