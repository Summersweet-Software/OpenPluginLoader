from pathlib import Path
import sys

from openpluginloader.defaultstrategy import ImportPluginLoader
from openpluginloader.defaultstrategy.folderplugins import (
    FolderLoadTimeModuleProvider,
    FolderModuleProvider,
    FolderPluginMetadataLoader,
    FolderPluginScanner,
)
from openpluginloader.defaultstrategy.importmachinery import (
    DefaultGlobalPluginImportHook,
)
from openpluginloader.defaultstrategy.tarplugins import TargzPluginArchiver
from openpluginloader.manager import PluginManager
from openpluginloader.metadata import PluginDependency
from openpluginloader.utility import DEFAULT_MODS
from openpluginloader.versioning import parse_api_version


def cleansup(func):
    def wrapper(*args, **kwargs):
        default_mods = {**DEFAULT_MODS}
        previous = {**sys.modules}
        meta_paths = [*sys.meta_path]

        out = func(*args, **kwargs)

        sys.modules.clear()
        sys.modules.update(previous)
        sys.meta_path.clear()
        sys.meta_path.extend(meta_paths)
        DEFAULT_MODS.clear()
        DEFAULT_MODS.update(default_mods)
        return out

    return wrapper


API_VERSION = parse_api_version("0.1.0")
PLUGIN_PATH = Path("tests/test_plugins/")


def setup_manager():
    loader = ImportPluginLoader()
    archiver = TargzPluginArchiver(enable_logging=True)

    folder_scanner = FolderPluginScanner(PLUGIN_PATH, loader, archiver)

    manager = PluginManager(
        plugin_scanners=[folder_scanner],
        api_version=API_VERSION,
        import_hooks=[],
    )

    manager.import_hooks.append(
        DefaultGlobalPluginImportHook(PLUGIN_PATH, manager),
    )  # creates circular reference- not important since the manager has a lifetime as long as the program runtime.

    return manager


# ==== MetaLoader =====


def test_meta_loader_has_metadata_func():
    metaloader = FolderPluginMetadataLoader()

    assert metaloader.contains_meta(PLUGIN_PATH / "folder_plugin_1") == True
    assert metaloader.contains_meta(PLUGIN_PATH / "folder_plugin_2") == True
    assert metaloader.contains_meta(PLUGIN_PATH / "folder_plugin_3") == True
    assert metaloader.contains_meta(PLUGIN_PATH / "folder_plugin_broken") == False


def test_meta_loader_load_metadata_func():
    metaloader = FolderPluginMetadataLoader()

    metadata = metaloader.load_metadata(PLUGIN_PATH / "folder_plugin_2", API_VERSION)

    assert metadata.author == "Abby"
    assert metadata.name == "FolderPlugin2"
    assert metadata.entry == "main"
    assert metadata.src_path == PLUGIN_PATH / "folder_plugin_2"
    assert metadata.plugin_version == parse_api_version("1.0")
    assert metadata.min_api_version == parse_api_version("0.1.0")
    assert metadata.max_api_version == parse_api_version("1.1.10")
    assert metadata.dependencies == [
        PluginDependency(
            "Abby.FolderPlugin1",
            parse_api_version("0.0.0"),
            parse_api_version("99.0.0"),
        )
    ]
    assert metadata.aditional_meta == {
        "name": "FolderPlugin2",
        "author": "Abby",
        "entry": "main",
        "version": "1.0",
        "min_api_version": "0.1.0",
        "max_api_version": "1.1.10",
        "dependencies": [
            {
                "plugin_id": "Abby.FolderPlugin1",
                "min_version": "0.0.0",
                "max_version": "99.0.0",
            }
        ],
        "extra_data_thing": "WOAB",
    }


# ==== E2E =====


@cleansup
def test_scanner():
    manager = setup_manager()

    manager.initialize_hooks()
    plugins = manager.discover_plugins()

    assert len(plugins) == 3

    assert any(plugin.metadata.name == "FolderPlugin1" for plugin in plugins)
    assert any(plugin.metadata.name == "FolderPlugin2" for plugin in plugins)
    assert any(plugin.metadata.name == "FolderPlugin3" for plugin in plugins)

    assert all(
        isinstance(plugin.scanner_source, FolderPluginScanner) for plugin in plugins
    )
    assert all(
        isinstance(plugin.metaloader, FolderPluginMetadataLoader) for plugin in plugins
    )
    assert all(isinstance(plugin.archiver, TargzPluginArchiver) for plugin in plugins)
    assert all(isinstance(plugin.loader, ImportPluginLoader) for plugin in plugins)
    assert all(
        isinstance(plugin.module_provider, FolderModuleProvider) for plugin in plugins
    )
    assert all(
        isinstance(plugin.module_loadtime_provider, FolderLoadTimeModuleProvider)
        for plugin in plugins
    )


@cleansup
def test_plugin_load_order():
    manager = setup_manager()

    manager.initialize_hooks()
    plugins = manager.discover_plugins()

    plugin_1_idx = plugins.index(
        next(plugin for plugin in plugins if plugin.metadata.name == "FolderPlugin1")
    )

    plugin_2_idx = plugins.index(
        next(plugin for plugin in plugins if plugin.metadata.name == "FolderPlugin2")
    )  # depends on plugin 1

    assert plugin_2_idx > plugin_1_idx


@cleansup
def test_plugin_load_plugin_2_via_manager():
    class FakeModule(type(sys)):
        def __init__(self, name):
            super().__init__(name)
            self.counter = 0

    DEFAULT_MODS["FakeModule"] = FakeModule("FakeModule")

    manager = setup_manager()

    manager.initialize_hooks()
    plugins = manager.discover_plugins()

    plugin_2 = next(
        plugin for plugin in plugins if plugin.metadata.name == "FolderPlugin2"
    )

    manager.load_plugin(plugin_2)
    assert DEFAULT_MODS["FakeModule"].counter == 1


@cleansup
def test_plugin_load_plugin_2_via_import():

    class FakeModule(type(sys)):
        def __init__(self, name):
            super().__init__(name)
            self.counter = 0

    DEFAULT_MODS["FakeModule"] = FakeModule("FakeModule")

    manager = setup_manager()

    manager.initialize_hooks()
    manager.discover_plugins()

    import plugins.FolderPlugin2.__ENTRY__

    assert DEFAULT_MODS["FakeModule"].counter == 1


@cleansup
def test_plugin_load_plugin_2_sub_file():

    class FakeModule(type(sys)):
        def __init__(self, name):
            super().__init__(name)
            self.counter = 0

    DEFAULT_MODS["FakeModule"] = FakeModule("FakeModule")

    manager = setup_manager()

    manager.initialize_hooks()
    manager.discover_plugins()

    import plugins.FolderPlugin2.extra_file

    assert DEFAULT_MODS["FakeModule"].counter == 1000


@cleansup
def test_plugin_load_plugin_1_and_2_via_manager_persist():

    class FakeModule(type(sys)):
        def __init__(self, name):
            super().__init__(name)
            self.counter = 0

    DEFAULT_MODS["FakeModule"] = FakeModule("FakeModule")

    manager = setup_manager()

    manager.initialize_hooks()
    plugins = manager.discover_plugins()

    plugin_1 = next(
        plugin for plugin in plugins if plugin.metadata.name == "FolderPlugin1"
    )
    plugin_2 = next(
        plugin for plugin in plugins if plugin.metadata.name == "FolderPlugin2"
    )

    manager.load_plugin(plugin_1)
    manager.load_plugin(plugin_2)
    assert DEFAULT_MODS["FakeModule"].counter == 2


@cleansup
def test_plugin_load_plugin_1_and_2_via_import_persist():

    class FakeModule(type(sys)):
        def __init__(self, name):
            super().__init__(name)
            self.counter = 0

    DEFAULT_MODS["FakeModule"] = FakeModule("FakeModule")

    manager = setup_manager()

    manager.initialize_hooks()
    manager.discover_plugins()

    import plugins.FolderPlugin1.__ENTRY__
    import plugins.FolderPlugin2.__ENTRY__

    assert DEFAULT_MODS["FakeModule"].counter == 2


@cleansup
def test_plugin_load_plugin_2_fake_sitepackage():
    class FakeModule(type(sys)):
        def __init__(self, name):
            super().__init__(name)
            self.counter = 0

    DEFAULT_MODS["FakeModule"] = FakeModule("FakeModule")

    manager = setup_manager()

    manager.initialize_hooks()
    manager.discover_plugins()

    import plugins.FolderPlugin2.sitepackages_testing

    assert DEFAULT_MODS["FakeModule"].counter == -15


@cleansup
def test_plugin_load_plugin_3_via_manager_disallow_outside_imports():

    manager = setup_manager()

    manager.initialize_hooks()
    plugins = manager.discover_plugins()

    plugin_3 = next(
        plugin for plugin in plugins if plugin.metadata.name == "FolderPlugin3"
    )

    try:
        manager.load_plugin(plugin_3)
        assert False  # The above should always error. If not, we fail the test
    except ModuleNotFoundError:
        assert True  # Test is successful if we can't access the out-of-scope module.


@cleansup
def test_plugin_load_ensure_cant_import_plugin_locals_outside_plugins():

    manager = setup_manager()

    manager.initialize_hooks()
    plugins = manager.discover_plugins()

    try:
        import fake_mypy

        assert False  # The above should always error. If not, we fail the test
    except ModuleNotFoundError:
        assert True  # Test is successful if we can't access the out-of-scope module.
