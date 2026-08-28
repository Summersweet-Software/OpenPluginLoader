from pathlib import Path
import tarfile
import tomllib
from typing import Any, NamedTuple, Protocol

from openpluginloader.versioning import ApiVersion, parse_api_version


class PluginDependency(NamedTuple):
    """A dependency for a plugin"""

    plugin_id: str
    """format: `<author>.<name>`"""

    min_version: ApiVersion
    """minimum plugin version required."""
    max_version: ApiVersion
    """maximum plugin version required."""


class PluginMetadata(NamedTuple):
    """The metadata contained typically within the 'plugin.toml' file inside of each plugin"""

    author: str
    name: str

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


class PluginMetadataLoader(Protocol):
    def load_metadata(self, plugin_src: Path) -> PluginMetadata: ...


class PluginLoadError(Exception):
    pass


class DefaultMetadataLoader:
    __slots__ = ()

    def __init__(self):
        pass

    def load_metadata(
        self, plugin_src: Path, api_version: ApiVersion
    ) -> PluginMetadata:
        data = ""
        if plugin_src.is_file():
            with tarfile.open(plugin_src, "r:gz") as file:
                dataio = file.extractfile("plugin.toml")
                if dataio is None:
                    raise PluginLoadError("Missing `plugin.toml` file")
                data = dataio.read().decode()
        else:
            with open(plugin_src / "plugin.toml", "r") as file:
                data = file.read()

        table = tomllib.loads(data)

        return PluginMetadata(
            table["author"],
            table["name"],
            plugin_src,
            parse_api_version(table["version"]),
            parse_api_version(table.get("min_api_version", api_version)),
            parse_api_version(table.get("max_api_version", api_version)),
            table.get("dependencies", []),
            {},
        )
