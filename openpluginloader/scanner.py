from typing import Protocol

from openpluginloader.metadata import PluginMetadata


class PluginScanner(Protocol):
    """The plugin scanning strategy used"""

    def get_available_plugins(self) -> list[PluginMetadata]: ...
