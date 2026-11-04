import importlib
from pathlib import Path

from openpluginloader.defaultstrategy.folderplugins import FolderPluginScanner
from openpluginloader.defaultstrategy.importmachinery import (
    DefaultGlobalPluginImportHook,
)
from openpluginloader.defaultstrategy.tarplugins import (
    TargzPluginScanner,
    TargzPluginArchiver,
)
from openpluginloader.loader import PluginLoader
from openpluginloader.manager import PluginManager
from openpluginloader.scanner import Plugin
from openpluginloader.versioning import ApiVersion


class ImportPluginLoader(PluginLoader):
    """The default loading strategy for plugins.
    Uses dynamic imports and temporarily modifies python's path environment
    (from within import hooks local to Plugins themselves).
    """

    def __init__(self):
        pass

    def load_plugin(self, plugin: Plugin):
        """Loads an individual plugin"""
        importlib.import_module(f"plugins.{plugin.metadata.name}.__ENTRY__")


def create_default_manager(
    api_version: ApiVersion, plugin_path: Path, enable_archive_logging=True
) -> PluginManager:
    """Creates the default plugin manager

    enable_archive_logging - when enabled- archiving will print out added
      site-packages and files
    """
    loader = ImportPluginLoader()
    archiver = TargzPluginArchiver(enable_logging=enable_archive_logging)

    Targz_scanner = TargzPluginScanner(plugin_path, loader, archiver)
    folder_scanner = FolderPluginScanner(plugin_path, loader, archiver)

    manager = PluginManager(
        plugin_scanners=[Targz_scanner, folder_scanner],
        api_version=api_version,
        import_hooks=[],
    )

    manager.import_hooks.append(
        DefaultGlobalPluginImportHook(plugin_path, manager),
    )  # creates circular reference- not important since the manager has a lifetime as long as the program runtime.

    return manager


__all__ = ["ImportPluginLoader", "create_default_manager"]
