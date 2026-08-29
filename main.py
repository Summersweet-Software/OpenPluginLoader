from pathlib import Path

from openpluginloader.defaultstrategy import create_default_manager
from openpluginloader.versioning import ApiVersion

API_VERSION = ApiVersion(1, 0, 0, None)


if __name__ == "__main__":
    manager = create_default_manager(API_VERSION, Path("example/exampleplugin/build/"))
    manager.initialize_hooks()

    plugin_src = Path("example/exampleplugin")
    plugin_dest = plugin_src / "build"
    manager.archive_plugin(plugin_src, plugin_dest)

    print()
    print()

    print("Plugin import result")

    import plugins.ExamplePlugin.__ENTRY__
