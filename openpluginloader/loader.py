from typing import Protocol
import typing

if typing.TYPE_CHECKING:
    from openpluginloader.scanner import Plugin


class PluginLoader(Protocol):
    """An individual strategy used to load a plugin.
    It acts as a collection of functions to control how
    plugins are imported
    """

    def load_plugin(self, plugin: "Plugin"):
        """Loads an individual plugin"""
        ...


__all__ = ["PluginLoader"]
