from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType

from openpluginloader.archiving import PluginArchiver
from openpluginloader.loader import PluginLoader
from openpluginloader.metadata import (
    PluginDependency,
    PluginMetadata,
    PluginMetadataLoader,
)
from openpluginloader.moduleprovider import PluginModuleProvider
from openpluginloader.scanner import Plugin, PluginScanner
from openpluginloader.versioning import ApiVersion, parse_api_version


class FakeMetaLoader(PluginMetadataLoader):
    def contains_meta(self, plugin_src: Path) -> bool:
        return True

    def load_metadata(
        self, plugin_src: Path, api_version: ApiVersion
    ) -> PluginMetadata:
        return PluginMetadata(
            author="JoshKatz",
            name="A",
            entry="",
            src_path=Path(),
            plugin_version=parse_api_version("0.1.0"),
            min_api_version=parse_api_version("0.1.0"),
            max_api_version=parse_api_version("0.1.0"),
            dependencies=[
                PluginDependency(
                    "JoshKatz.B",
                    parse_api_version("0.1.0"),
                    parse_api_version("0.1.0"),
                ),
                PluginDependency(
                    "JoshKatz.C",
                    parse_api_version("0.1.0"),
                    parse_api_version("0.1.0"),
                ),
            ],
            aditional_meta={},
        )


class FakeLoader(PluginLoader):
    def load_plugin(self, plugin: Plugin):
        """Loads an individual plugin"""
        pass


class FakeArchiver(PluginArchiver):
    def archive_plugin(
        self, meta: PluginMetadata, src: Path, destination: Path
    ) -> Path:
        return destination

    def dearchive_plugin(self, src: Path, destination: Path) -> Path:
        return destination


class FakeModuleProvider(PluginModuleProvider):
    def setup_execution_environment(self, module: ModuleType):
        return super().setup_execution_environment(module)

    def find_spec(
        self, plugin: "Plugin", fullname: str, path, target=None
    ) -> ModuleSpec | None:
        return None


class FakeScanner(PluginScanner):
    def get_plugin(self, src: Path, api_version: ApiVersion) -> Plugin | None:
        """Returns a plugin if available at this path"""
        return None

    def get_available_plugins(self, api_version: ApiVersion) -> list[Plugin]:
        return [
            Plugin(
                PluginMetadata(
                    author="JoshKatz",
                    name="A",
                    entry="",
                    src_path=Path(),
                    plugin_version=parse_api_version("0.1.0"),
                    min_api_version=parse_api_version("0.1.0"),
                    max_api_version=parse_api_version("0.1.0"),
                    dependencies=[
                        PluginDependency(
                            "JoshKatz.B",
                            parse_api_version("0.1.0"),
                            parse_api_version("0.1.0"),
                        ),
                        PluginDependency(
                            "JoshKatz.C",
                            parse_api_version("0.1.0"),
                            parse_api_version("0.1.0"),
                        ),
                    ],
                    aditional_meta={},
                ),
                FakeMetaLoader(),
                FakeLoader(),
                FakeArchiver(),
                FakeModuleProvider(),
                FakeModuleProvider(),
                FakeScanner(),
            )
        ]
