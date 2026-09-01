from typing import Protocol

from openpluginloader.metadata import PluginMetadata


class PluginLoader(Protocol):
    """An individual strategy used to load a plugin.
    It acts as a collection of functions to control how
    plugins are imported
    """

    def load_plugin(self, plugin: PluginMetadata):
        """Loads an individual plugin"""
        ...

    def sort_plugins_by_load_order(
        self, plugins: list[PluginMetadata]
    ) -> list[PluginMetadata]:
        """Determines the load order of plugins"""
        ...


__all__ = ["PluginLoader"]
