from pathlib import Path

from openpluginloader.defaultstrategy import create_default_manager
from openpluginloader.metadata import PluginDependency, PluginMetadata
from openpluginloader.utility import (
    create_dependent_dict,
    generate_dependency_list,
    sort_plugins,
)
from openpluginloader.versioning import ApiVersion, parse_api_version

API_VERSION = ApiVersion(1, 0, 0, None)

# plugins = [
#     PluginMetadata(
#         author="JoshKatz",
#         name="A",
#         entry="",
#         src_path=Path(),
#         plugin_version=parse_api_version("0.1.0"),
#         min_api_version=parse_api_version("0.1.0"),
#         max_api_version=parse_api_version("0.1.0"),
#         dependencies=[
#             PluginDependency(
#                 "JoshKatz.B", parse_api_version("0.1.0"), parse_api_version("0.1.0")
#             ),
#             PluginDependency(
#                 "JoshKatz.C", parse_api_version("0.1.0"), parse_api_version("0.1.0")
#             ),
#         ],
#         aditional_meta={},
#     ),
#     PluginMetadata(
#         author="JoshKatz",
#         name="B",
#         entry="",
#         src_path=Path(),
#         plugin_version=parse_api_version("0.1.0"),
#         min_api_version=parse_api_version("0.1.0"),
#         max_api_version=parse_api_version("0.1.0"),
#         dependencies=[
#             PluginDependency(
#                 "JoshKatz.C", parse_api_version("0.1.0"), parse_api_version("0.1.0")
#             ),
#         ],
#         aditional_meta={},
#     ),
#     PluginMetadata(
#         author="JoshKatz",
#         name="C",
#         entry="",
#         src_path=Path(),
#         plugin_version=parse_api_version("0.1.0"),
#         min_api_version=parse_api_version("0.1.0"),
#         max_api_version=parse_api_version("0.1.0"),
#         dependencies=[],
#         aditional_meta={},
#     ),
#     PluginMetadata(
#         author="JoshKatz",
#         name="D",
#         entry="",
#         src_path=Path(),
#         plugin_version=parse_api_version("0.1.0"),
#         min_api_version=parse_api_version("0.1.0"),
#         max_api_version=parse_api_version("0.1.0"),
#         dependencies=[
#             PluginDependency(
#                 "JoshKatz.A", parse_api_version("0.1.0"), parse_api_version("0.1.0")
#             )
#         ],
#         aditional_meta={},
#     ),
# ]


if __name__ == "__main__":
    manager = create_default_manager(API_VERSION, Path("example/exampleplugin/build/"))
    manager.initialize_hooks()

    plugin_src = Path("example/exampleplugin")
    plugin_dest = plugin_src / "build"
    manager.archive_plugin(plugin_src, plugin_dest)

    print()

    plugins = manager.discover_plugins()

    print(
        {
            plugin.plugin_id: [
                dep.plugin_id for dep in generate_dependency_list(plugin, plugins)
            ]
            for plugin in plugins
        }
    )

    print(
        {
            name: [dep.plugin_id for dep in deps]
            for name, deps in create_dependent_dict(plugins).items()
        }
    )

    print()
    print(sort_plugins(plugins))
    print()

    manager.load_all_plugins()
