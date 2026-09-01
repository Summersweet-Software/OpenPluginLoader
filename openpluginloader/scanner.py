from typing import Protocol

from openpluginloader.metadata import PluginMetadata
from openpluginloader.versioning import ApiVersion


class PluginScanner(Protocol):
    """The plugin scanning strategy used"""

    def get_available_plugins(
        self, api_version: ApiVersion
    ) -> list[PluginMetadata]: ...


__all__ = ["PluginScanner"]
