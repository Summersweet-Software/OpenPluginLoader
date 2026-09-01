from pathlib import Path
from typing import Any, NamedTuple, Protocol

from openpluginloader.versioning import ApiVersion


class PluginDependency(NamedTuple):
    """A dependency for a plugin"""

    plugin_id: str
    """format: `<author>.<name>`"""

    min_version: ApiVersion
    """minimum plugin version required."""
    max_version: ApiVersion
    """maximum plugin version required."""


class PluginMetadata(NamedTuple):
    """The metadata contained typically within the 'plugin.toml'
    file inside of each plugin"""

    author: str
    name: str
    entry: str

    src_path: Path
    """Where the plugin is on disk"""

    plugin_version: ApiVersion

    min_api_version: ApiVersion
    """minimum plugin api version required."""
    max_api_version: ApiVersion
    """maximum plugin api version required."""

    dependencies: list[PluginDependency]

    aditional_meta: dict[str, Any]

    @property
    def plugin_id(self) -> str:
        return f"{self.author}.{self.name}"

    def __str__(self) -> str:
        return f"PluginMetadata(\n\t{(
            "\n\t".join(f"{name}={val}" for name, val in self._asdict().items())
        )}\n)"

    def __repr__(self) -> str:
        return f"PluginMetadata(id={self.plugin_id})"


class PluginMetadataLoader(Protocol):
    def contains_meta(self, plugin_src: Path) -> bool: ...

    def load_metadata(
        self, plugin_src: Path, api_version: ApiVersion
    ) -> PluginMetadata: ...


class PluginLoadError(Exception):
    pass


__all__ = ["PluginMetadata", "PluginMetadataLoader", "PluginLoadError"]
