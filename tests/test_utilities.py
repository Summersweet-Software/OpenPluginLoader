import importlib
import importlib.metadata
from pathlib import Path
import sys

from openpluginloader import utility
from openpluginloader.metadata import PluginDependency, PluginMetadata
from openpluginloader.versioning import parse_api_version


def test_set_default_module_cache():
    previous_mods = {**utility.DEFAULT_MODS}
    import pytest

    utility.set_default_module_cache()
    assert list(utility.DEFAULT_MODS.keys()) != list(previous_mods.keys())
    assert "pytest" in utility.DEFAULT_MODS.keys()


def test_add_search_path():
    previous_path = [*sys.path]
    new_path = "Example"

    with utility.add_search_path(new_path):
        assert len(previous_path) == len(sys.path) - 1
        assert new_path in sys.path

    assert sys.path == previous_path


def test_set_search_path():
    previous_path = [*sys.path]
    new_path = "Example"

    with utility.set_search_path([new_path]):
        assert len(sys.path) == 1
        assert [new_path] == sys.path

    assert sys.path == previous_path


def test_set_meta_paths():
    class Example:
        pass

    old_metas = [*sys.meta_path]

    with utility.set_meta_paths([Example]):
        assert sys.meta_path == [Example]

    assert sys.meta_path == old_metas


def test_clear_module_caches__no_defaults():
    old_modules = {**sys.modules}

    with utility.clear_module_caches():
        assert len(sys.modules) == 0

    assert sys.modules == old_modules


def test_clear_module_caches__with_defaults():
    old_modules = {**sys.modules}

    with utility.clear_module_caches(utility.DEFAULT_MODS):
        assert len(sys.modules) == len(utility.DEFAULT_MODS)
        assert sys.modules == utility.DEFAULT_MODS

    assert len(sys.modules) == len(old_modules)
    assert sys.modules == old_modules


def test_get_recursive_includes__mypy():
    includes = utility.get_recursive_includes(["mypy"])
    expected_names = {
        "mypy",
        "typing_extensions",
        "mypy_extensions",
        "pathspec",
        "librt",
        "ast_serialize",
    }

    assert set(include.name for include in includes) == expected_names


def test_get_recursive_includes__pytest():
    includes = utility.get_recursive_includes(["pytest"])
    expected_names = {
        "pytest",
        "colorama",
        "iniconfig",
        "packaging",
        "pluggy",
        "Pygments",
    }

    if sys.platform != "win32":
        expected_names.pop("colorama")

    assert set(include.name for include in includes) == expected_names


plugins = [
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
                "JoshKatz.B", parse_api_version("0.1.0"), parse_api_version("0.1.0")
            ),
            PluginDependency(
                "JoshKatz.C", parse_api_version("0.1.0"), parse_api_version("0.1.0")
            ),
        ],
        aditional_meta={},
    ),
    PluginMetadata(
        author="JoshKatz",
        name="B",
        entry="",
        src_path=Path(),
        plugin_version=parse_api_version("0.1.0"),
        min_api_version=parse_api_version("0.1.0"),
        max_api_version=parse_api_version("0.1.0"),
        dependencies=[
            PluginDependency(
                "JoshKatz.C", parse_api_version("0.1.0"), parse_api_version("0.1.0")
            ),
        ],
        aditional_meta={},
    ),
    PluginMetadata(
        author="JoshKatz",
        name="C",
        entry="",
        src_path=Path(),
        plugin_version=parse_api_version("0.1.0"),
        min_api_version=parse_api_version("0.1.0"),
        max_api_version=parse_api_version("0.1.0"),
        dependencies=[],
        aditional_meta={},
    ),
    PluginMetadata(
        author="JoshKatz",
        name="D",
        entry="",
        src_path=Path(),
        plugin_version=parse_api_version("0.1.0"),
        min_api_version=parse_api_version("0.1.0"),
        max_api_version=parse_api_version("0.1.0"),
        dependencies=[
            PluginDependency(
                "JoshKatz.A", parse_api_version("0.1.0"), parse_api_version("0.1.0")
            )
        ],
        aditional_meta={},
    ),
]


def test_get_distribution_paths__None():
    class ExampleDist(importlib.metadata.Distribution):
        def locate_file(self, path):
            raise

        def read_text(self, filename):
            raise

        @property
        def files(self):
            return None

    dist = ExampleDist()
    assert utility.get_distribution_paths(dist) == []


def test_get_distribution_paths__not_None():
    file_list = [
        importlib.metadata.PackagePath("A"),
        importlib.metadata.PackagePath("B"),
    ]

    class ExampleDist(importlib.metadata.Distribution):
        def locate_file(self, path):
            raise

        def read_text(self, filename):
            raise

        @property
        def files(self):
            return file_list

    dist = ExampleDist()
    assert utility.get_distribution_paths(dist) == file_list


def test_find_plugin_from_list__exists():
    assert plugins[0] == utility.find_plugin_from_list(plugins[0].plugin_id, plugins)


def test_find_plugin_from_list__not_exists():
    assert utility.find_plugin_from_list("WOAH", plugins) is None


def test_generate_dependency_list__non_recursive():
    expected = [plugins[2]]
    dependencies = utility.generate_dependency_list(plugins[1], plugins)

    assert expected == dependencies


def test_generate_dependency_list__recursive():
    expected = [plugins[0], plugins[1], plugins[2]]
    dependencies = utility.generate_dependency_list(plugins[3], plugins)

    assert expected == dependencies


def test_generate_dependents_list():
    expected = {plugins[0].plugin_id, plugins[1].plugin_id, plugins[3].plugin_id}
    dependencies = {
        plugin.plugin_id
        for plugin in utility.generate_dependents_list(plugins[2].plugin_id, plugins)
    }

    assert expected == dependencies


def test_create_dependent_dict():
    expected = {
        plugins[0].plugin_id: {
            plugins[3].plugin_id,
        },
        plugins[1].plugin_id: {
            plugins[0].plugin_id,
            plugins[3].plugin_id,
        },
        plugins[2].plugin_id: {
            plugins[0].plugin_id,
            plugins[1].plugin_id,
            plugins[3].plugin_id,
        },
        plugins[3].plugin_id: set(),
    }

    dependencies = {
        name: {depend.plugin_id for depend in depends}
        for name, depends in utility.create_dependent_dict(plugins).items()
    }

    assert expected == dependencies


def test_sort_plugins():
    expected = [plugins[2], plugins[1], plugins[0], plugins[3]]
    assert utility.sort_plugins(plugins) == expected
