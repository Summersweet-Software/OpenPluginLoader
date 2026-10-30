from pathlib import Path
import sys

from openpluginloader.metadata import (
    PluginLoadError,
)
from openpluginloader.scanner import Plugin, PluginScanner
from openpluginloader.utility import sort_plugins
from openpluginloader.versioning import ApiVersion


class PluginOutOfDate(PluginLoadError):
    """Api version of the plugin is outdated"""


class PluginTooNew(PluginLoadError):
    """Api version of the plugin is too new"""


class PluginManager:
    """A configurable plugin manager class.
    Scans for, loads, and archives plugins using strategy pattern.
    """

    __slots__ = (
        "plugin_scanners",
        "api_version",
        "import_hooks",
        "known_plugins",
        "_hooks_are_initialized",
    )

    plugin_scanners: list[PluginScanner]
    """Determines how plugins are discovered/located.
    Also responsible for attributing loaders to plugins."""

    api_version: ApiVersion
    """The current api version of your plugin api."""
    import_hooks: list
    """List of import hooks that need to be installed before plugins can be
    loaded"""
    _hooks_are_initialized: bool

    known_plugins: list[Plugin]

    def __init__(
        self,
        *,
        plugin_scanners: list[PluginScanner],
        api_version: ApiVersion,
        import_hooks: list,
    ):
        self.plugin_scanners = plugin_scanners
        self.api_version = api_version
        self.import_hooks = import_hooks
        self._hooks_are_initialized = False

        self.known_plugins = []

    def initialize_hooks(self):
        """Initialize all import hooks and machinery"""
        for hook in self.import_hooks[::-1]:
            sys.meta_path.insert(0, hook)

        self._hooks_are_initialized = True

    @property
    def hooks_are_initialized(self) -> bool:
        """Whether or not hooks have been initialized.
        Deinitializing hooks resets this to `False`."""
        return self._hooks_are_initialized

    def deinitialize_hooks(self):
        """I would not personally recommend using this!
        This is only provided as a convenience and a way to standardize
        this sort of behavior. I doubt it should be used in most projects.

        Still- the option is provided
        """

        for hook in self.import_hooks:
            sys.meta_path.remove(hook)

        self._hooks_are_initialized = False

    def load_plugin(self, plugin: Plugin):
        """Dynamically load an individual plugin

        Important: Ensure you run `.initialize_hooks()` first
        """
        if plugin.metadata.min_api_version > self.api_version:
            raise PluginTooNew(
                plugin, self.api_version, plugin.metadata.min_api_version
            )
        if plugin.metadata.max_api_version < self.api_version:
            raise PluginOutOfDate(
                plugin, self.api_version, plugin.metadata.max_api_version
            )

        return plugin.loader.load_plugin(plugin)

    def load_all_plugins(self):
        """Load all plugins dynamically.

        Important: Ensure you run `.initialize_hooks()` first
        """
        for plugin in self.known_plugins:
            self.load_plugin(plugin)

    def discover_plugins(self) -> list[Plugin]:
        plugins = list(
            {
                plugin
                for scanner in self.plugin_scanners
                for plugin in scanner.get_available_plugins(self.api_version)
            }
        )
        self.known_plugins = sort_plugins(plugins)
        return self.known_plugins

    def _get_plugin(self, src: Path) -> Plugin | None:
        """Finds a single plugin without discovering all plugins"""
        for scanner in self.plugin_scanners:
            if (out := scanner.get_plugin(src, self.api_version)) is not None:
                return out
        return None

    def get_plugin_by_name(self, name: str) -> Plugin | None:
        for plugin in self.known_plugins:
            if plugin.metadata.name == name:
                return plugin
        return None

    def archive_plugin(self, src: Path, dest: Path) -> Path:
        plugin = self._get_plugin(src)
        if plugin is None:
            raise ValueError("Plugin could not be found at the specified source path.")
        return plugin.archiver.archive_plugin(plugin.metadata, src, dest)


__all__ = ["PluginManager", "PluginOutOfDate", "PluginTooNew"]
