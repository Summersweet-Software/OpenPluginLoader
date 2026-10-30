import importlib
from importlib.abc import FileLoader
from importlib.machinery import BuiltinImporter, ModuleSpec
from pathlib import Path
import sys
from types import ModuleType

from openpluginloader.manager import PluginManager
from openpluginloader.moduleprovider import PluginModuleProvider
from openpluginloader.scanner import Plugin
from openpluginloader.utility import (
    DEFAULT_MODS,
    clear_module_caches,
    set_meta_paths,
)


class PluginFolderLoader(FileLoader):
    """Import hook/file loader that does nothing.
    It represents the root of the `plugins` package
    """

    def get_data(self, path) -> bytes:
        return b""

    def get_source(self, fullname):
        return self.get_data(self.path).decode()


class PluginModuleLoaderShim(FileLoader):
    """Runs appropriate code to modify the execution environment when running
    exec_module.
    Provides passthrough for all other functions.
    """

    __slots__ = ("plugin", "loader", "module_provider", "changes_metapaths")

    plugin: Plugin
    module_provider: PluginModuleProvider
    loader: FileLoader
    changes_metapaths: bool
    """Changes if the DefaultPluginLoadTimeImportHook is added during."""

    def __init__(
        self,
        plugin: Plugin,
        module_provider: PluginModuleProvider,
        loader: FileLoader,
        changes_metapaths: bool,
    ):
        self.plugin = plugin
        self.module_provider = module_provider
        self.loader = loader
        self.changes_metapaths = changes_metapaths

    def get_data(self, path) -> bytes:
        return self.loader.get_data(path)

    def get_source(self, fullname) -> str | None:
        return self.loader.get_source(fullname)

    def load_module(self, fullname: str | None = None) -> ModuleType:
        return self.loader.load_module(fullname)

    def exec_module(self, module: ModuleType):
        importlib.invalidate_caches()

        with clear_module_caches(DEFAULT_MODS):
            if self.changes_metapaths:
                with set_meta_paths(
                    [
                        DefaultPluginLoadTimeImportHook(self.plugin),
                        *(
                            metapath
                            for metapath in sys.meta_path
                            if metapath
                            is BuiltinImporter  # add builtins importer (allows you to import things like "math")
                            or isinstance(
                                metapath, DefaultPluginLoadTimeImportHook
                            )  # ensure you can still do imports of local packages
                            or isinstance(
                                metapath, DefaultGlobalPluginImportHook
                            )  # ensure you can still do plugin imports.
                        ),
                    ]
                ):
                    with self.module_provider.setup_execution_environment(module):
                        return self.loader.exec_module(module)
            else:
                with self.module_provider.setup_execution_environment(module):
                    return self.loader.exec_module(module)


class DefaultPluginLoadTimeImportHook:
    """Import hook provided during plugin load time. Allows modules to be provided using the
    plugins module_loadtime_provider.

    This allows local modules/packages to be visible to plugins themselves.
    """

    __slots__ = ("plugin",)

    plugin: Plugin

    def __init__(self, plugin: Plugin):
        self.plugin = plugin

    def find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None:
        spec = self.plugin.module_loadtime_provider.find_spec(
            self.plugin, fullname, path, target
        )
        if (
            spec is not None
            and spec.loader is not None
            and isinstance(spec.loader, FileLoader)
        ):  # Insert Module Loader Shim to setup environment
            spec.loader = PluginModuleLoaderShim(
                self.plugin, self.plugin.module_loadtime_provider, spec.loader, False
            )
        return spec


class DefaultGlobalPluginImportHook:
    """An import hook that interprets any modules prefixed as `plugin.<plugin-name>` as
    a plugin within whatever plugin path is being used
    """

    plugin_path: Path
    manager: PluginManager
    plugin_module_cache: dict[str, ModuleSpec | None]
    plugins_module: ModuleSpec
    """The actual modulespec representing the fake "plugins" module"""

    def __init__(
        self,
        plugin_path: Path,
        manager: PluginManager,
    ):
        self.plugin_path = plugin_path

        self.manager = manager
        self.plugin_module_cache = {}

        self.plugins_module = ModuleSpec(
            "plugins",
            PluginFolderLoader("plugins", str(plugin_path)),
            origin=str(plugin_path),
            is_package=True,
        )

        if self.plugins_module.submodule_search_locations is not None:
            self.plugins_module.submodule_search_locations.append(
                str(plugin_path.absolute())
            )
        self.plugins_module.has_location = True

    def create_plugin_module(
        self, plugin: Plugin, fullname: str, path, target
    ) -> ModuleSpec | None:
        spec = plugin.module_provider.find_spec(plugin, fullname, path, target)
        if (
            spec is not None
            and spec.loader is not None
            and isinstance(spec.loader, FileLoader)
        ):  # Insert Module Loader Shim to setup environment
            spec.loader = PluginModuleLoaderShim(
                plugin, plugin.module_provider, spec.loader, True
            )
        return spec

    def find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None:
        if fullname == "plugins":
            return self.plugins_module

        if not fullname.startswith("plugins."):
            return None

        fullname_parts = fullname.split(".")
        plugin_name = fullname_parts[1]

        corrosponding_plugin = self.manager.get_plugin_by_name(plugin_name)

        if corrosponding_plugin is None:
            raise ImportError(f"Could not locate plugin: {plugin_name}.")

        # Use plugin entry when trying to import `__ENTRY__`
        if len(fullname_parts) >= 3 and fullname_parts[2] == "__ENTRY__":
            fullname_parts[2] = corrosponding_plugin.metadata.entry
            fullname = ".".join(fullname_parts)

        if fullname in self.plugin_module_cache.keys():
            return self.plugin_module_cache[fullname]

        if len(fullname_parts) >= 2:
            fake_fullname = ".".join(
                part for c, part in enumerate(fullname_parts) if c > 1
            )
        else:
            fake_fullname = fullname

        out = self.plugin_module_cache.setdefault(
            fullname,
            self.create_plugin_module(
                corrosponding_plugin, fake_fullname, path, target
            ),
        )
        if out is not None:
            out.name = fullname
        return out


__all__ = [
    "PluginFolderLoader",
    "PluginModuleLoaderShim",
    "DefaultPluginLoadTimeImportHook",
    "DefaultGlobalPluginImportHook",
]
