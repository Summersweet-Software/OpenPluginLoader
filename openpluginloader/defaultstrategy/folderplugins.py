import importlib
from importlib.abc import FileLoader
from importlib.machinery import ModuleSpec
import os
from pathlib import Path
import tomllib
from types import ModuleType

from openpluginloader.archiving import PluginArchiver
from openpluginloader.loader import PluginLoader
from openpluginloader.metadata import (
    PluginDependency,
    PluginLoadError,
    PluginMetadata,
    PluginMetadataLoader,
)
from openpluginloader.moduleprovider import PluginModuleProvider
from openpluginloader.scanner import Plugin, PluginScanner
from openpluginloader.versioning import ApiVersion, parse_api_version

import importlib._bootstrap
import importlib._bootstrap_external


class FolderPluginScanner(PluginScanner):
    """Finds and setups up TarGZPlugins.
    These are plugins in a targz file."""

    plugin_dir: Path

    loader: PluginLoader
    metaloader: PluginMetadataLoader
    archiver: PluginArchiver

    def __init__(
        self,
        plugin_dir: Path,
        loader: PluginLoader,
        archiver: PluginArchiver,
    ):
        self.plugin_dir = plugin_dir
        self.loader = loader
        self.metaloader = FolderPluginMetadataLoader()
        self.archiver = archiver

    def _is_folder_plugin(self, dir: Path) -> bool:
        return dir.is_dir() and self.metaloader.contains_meta(dir)

    def _create_plugin(self, src: Path, api_version: ApiVersion) -> Plugin:
        metadata = self.metaloader.load_metadata(src, api_version)

        return Plugin(
            metadata,
            self.metaloader,
            self.loader,
            self.archiver,
            FolderModuleProvider(),
            FolderLoadTimeModuleProvider(),
            self,
        )

    def get_plugin(self, src: Path, api_version: ApiVersion) -> Plugin | None:
        """Returns a plugin if available at this path"""
        if self._is_folder_plugin(src):
            return self._create_plugin(src, api_version)
        return None

    def get_available_plugins(self, api_version: ApiVersion) -> list[Plugin]:
        output: list[Plugin] = []
        for filename in os.listdir(self.plugin_dir):
            filepath = self.plugin_dir / filename
            if self._is_folder_plugin(filepath):
                output.append(self._create_plugin(filepath, api_version))
        return output


class FolderPluginMetadataLoader(PluginMetadataLoader):

    def _fix_plugin_src(self, plugin_src: Path):
        # Load plugin pyproject config
        if os.path.exists(plugin_src / "pyproject.toml"):
            with open(plugin_src / "pyproject.toml", "r") as f:
                config = tomllib.loads(f.read())
                plugin_config = config.get("tool", {}).get("plugin", {})
                if (new_src := plugin_config.get("src")) is not None:
                    if Path(new_src).is_absolute():
                        return new_src
                    else:
                        return plugin_src / new_src
        return plugin_src

    def contains_meta(self, plugin_src: Path) -> bool:
        plugin_src = self._fix_plugin_src(plugin_src)
        if not plugin_src.is_dir():
            return False
        return os.path.exists(plugin_src / "plugin.toml")

    def load_metadata(
        self, plugin_src: Path, api_version: ApiVersion
    ) -> PluginMetadata:
        plugin_src = self._fix_plugin_src(plugin_src)

        if plugin_src.is_file():
            raise PluginLoadError("Expected a folder when loading plugin metadata.")

        with open(plugin_src / "plugin.toml") as f:
            table = tomllib.loads(f.read())

        return PluginMetadata(
            author=table["author"],
            name=table["name"],
            entry=table["entry"],
            src_path=plugin_src,
            plugin_version=parse_api_version(table["version"]),
            min_api_version=parse_api_version(
                table.get("min_api_version", api_version)
            ),
            max_api_version=parse_api_version(
                table.get("max_api_version", api_version)
            ),
            dependencies=[
                PluginDependency(
                    dep["plugin_id"], dep["min_version"], dep["max_version"]
                )
                for dep in table.get("dependencies", [])
            ],
            aditional_meta=table,
        )


# ========= Providers ===========


class FolderModuleProvider(PluginModuleProvider):
    """Is able to search for modules inside of a folder containing a `site-packages` folder"""

    def setup_execution_environment(self, module: ModuleType):
        """Used when beginning to execute plugin modules."""
        return super().setup_execution_environment(module)

    def make_module_spec(
        self,
        plugin: Plugin,
        fullname: str,
        file_path: str,
        path: str | None,
        is_package: bool,
    ):
        """Creates a module given the provided information. Replace this function in order
        to change module creation details."""
        return ModuleSpec(
            fullname,
            FolderModuleLoader(
                fullname,
                file_path,
                plugin.metadata.src_path,
            ),
            origin=path,
            is_package=is_package,
        )

    def _find_spec_folder(
        self, plugin: Plugin, fullname: str, path: str | None, search_path: Path
    ) -> ModuleSpec | None:
        fullname_path = search_path / fullname.replace(".", "/")
        absolute_fullname_path = fullname_path.absolute()

        if absolute_fullname_path.exists() and absolute_fullname_path.is_dir():
            spec = self.make_module_spec(
                plugin, fullname, str(absolute_fullname_path), path, True
            )

            spec.has_location = True
        elif Path(str(absolute_fullname_path) + ".py").exists():
            spec = self.make_module_spec(
                plugin,
                fullname,
                str((str(absolute_fullname_path) + ".py")),
                path,
                False,
            )

            spec.has_location = True
        else:
            return None
        return spec

    def find_spec(
        self, plugin: Plugin, fullname: str, path: list[str] | None | str, target=None
    ) -> ModuleSpec | None:
        if isinstance(path, list):
            path = path[0] if len(path) > 0 else None

        return self._find_spec_folder(
            plugin, fullname, path, plugin.metadata.src_path
        ) or self._find_spec_folder(  # Find local modules
            plugin, fullname, path, plugin.metadata.src_path / "site-packages"
        )  # if not available, find site-packages


class FolderLoadTimeModuleProvider(FolderModuleProvider):
    """Actually in charge of loading individual files inside of a plugin.
    Only Active during plugin loading.

    Does nothing more than its parent.
    """

    pass


# ===== FileLoaders =====


class FolderModuleLoader(FileLoader):
    """Loads plugin modules from a folder plugin."""

    plugin_src: Path

    def __init__(self, fullname, path, plugin_src: Path):
        super().__init__(fullname, path)
        self.plugin_src = plugin_src

    def get_dunder_init_data(self, path: str) -> bytes:
        """Get __init__.py file to be run for packages."""
        file_path = path + "/__init__.py"
        if not os.path.exists(file_path) or not os.path.isdir(file_path):
            return b""

        with open(file_path, "rb") as f:
            return f.read()

    def get_data(self, path: str) -> bytes:
        if not path.endswith(".py"):
            return self.get_dunder_init_data(path)

        if not os.path.exists(path) or not os.path.isfile(path):
            raise ImportError(path)  # module file not found.

        with open(path, "rb") as f:
            return f.read()

    def get_source(self, fullname):
        return self.get_data(self.path).decode()

    def load_module(self, fullname: str | None = None) -> ModuleType:
        return importlib._bootstrap._load_module_shim(self, fullname)

    def exec_module(self, module: ModuleType):
        return importlib._bootstrap_external.SourceLoader.exec_module(self, module)
