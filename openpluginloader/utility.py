"""Utility functions"""

from contextlib import contextmanager
import importlib.metadata
import sys
from types import ModuleType

from packaging.requirements import Requirement

from openpluginloader.metadata import PluginLoadError, PluginMetadata

# current module cache
DEFAULT_MODS = {**sys.modules}


def set_default_module_cache():
    """Sets the default module cache. Can help if you notice missing imports
    that are part of the import machinery your plugin managing strategy
    implements.

    These typically can't be easily reimported on the fly because every
    sys.meta_path entry is removed and replaced (at least temporarily)
    """
    global DEFAULT_MODS
    DEFAULT_MODS.clear()
    DEFAULT_MODS.update(sys.modules)


@contextmanager
def add_search_path(path: str):
    """Temporarily append an item to the search path, remove it when the
    context manager exits"""
    index = len(sys.path)
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path.pop(index)


@contextmanager
def set_search_path(new_path: list[str]):
    """Temporarily set the search path, reset it when the context manager exits"""
    old = [*sys.path]
    sys.path.clear()
    sys.path.extend(new_path)
    try:
        yield
    finally:
        sys.path.clear()
        sys.path.extend(old)


@contextmanager
def set_meta_paths(hooks: list):
    old = [*sys.meta_path]
    sys.meta_path.clear()
    sys.meta_path.extend(hooks)
    try:
        yield
    finally:
        sys.meta_path.clear()
        sys.meta_path.extend(old)


@contextmanager
def clear_module_caches(default: dict[str, ModuleType] | None = None):
    """Temporarily clear module caches and return them to their previous state
    after the context manager exits"""

    modules = {**sys.modules}

    sys.modules.clear()
    if default is not None:
        sys.modules.update(default)
    try:
        yield
    finally:
        sys.modules.clear()
        sys.modules.update(modules)


def get_recursive_includes(
    includes: list[str],
) -> list[importlib.metadata.Distribution]:
    """Takes the name of an include and gets a recursive list of
    dependency includes."""

    output: list[importlib.metadata.Distribution] = []
    to_search = [importlib.metadata.distribution(include) for include in includes]

    while len(to_search) > 0:
        current = to_search.pop(0)
        to_search.extend(
            importlib.metadata.distribution(parsed.name)
            for requirement in (current.requires or [])
            if (parsed := Requirement(requirement)).name
            not in (item.name for item in output)
            and (parsed.marker is None or parsed.marker.evaluate())
        )

        output.append(current)

    return output


def get_distribution_paths(
    dist: importlib.metadata.Distribution,
) -> list[importlib.metadata.PackagePath]:
    """Normalizes dist.files (used to do more. that is why this still exists)"""
    if dist.files is None:
        return []

    return dist.files


def find_plugin_from_list(
    id: str, plugins: list[PluginMetadata]
) -> PluginMetadata | None:
    for plugin in plugins:
        if id == plugin.plugin_id:
            return plugin
    return None


class DependencyError(PluginLoadError):
    pass


class DependencyOutOfDate(DependencyError):
    pass


class DependencyTooNew(DependencyError):
    pass


class DependencyMissingError(DependencyError):
    pass


class CircularDependencyError(DependencyError):
    pass


# TODO: Implement caching
def generate_dependency_list(
    plugin: PluginMetadata, plugins: list[PluginMetadata], seen: list[str] | None = None
) -> list[PluginMetadata]:
    """Generates a recursive dependency list. Gets dependencies of dependencies
    etc. etc."""

    if seen is None:
        seen = [plugin.plugin_id]
    elif plugin.plugin_id in seen:
        raise CircularDependencyError(
            f"Circular dependency found while generating dependencies for: {plugin.plugin_id}"
        )
    else:
        # needs to make a new "seen list" (otherwise bad times will occur)
        seen = [*seen, plugin.plugin_id]

    dependencies = []

    for dep in plugin.dependencies:
        dep_plugin = find_plugin_from_list(dep.plugin_id, plugins)
        if dep_plugin is None:
            raise DependencyMissingError(f"Could not find plugin: {dep.plugin_id}")
        # check if plugin was already added
        if any(
            dep_plugin.plugin_id == dependency.plugin_id for dependency in dependencies
        ):
            continue
        if dep_plugin.plugin_version < dep.min_version:
            raise DependencyOutOfDate(
                f"{plugin.plugin_id} requires {dep.plugin_id}"
                f" {dep.min_version} or higher. {dep.plugin_id} is "
                f"only version {dep_plugin.plugin_version}"
            )
        if dep_plugin.plugin_version > dep.max_version:
            raise DependencyTooNew(
                f"{plugin.plugin_id} requires {dep.plugin_id}"
                f" {dep.max_version} or lower. {dep.plugin_id} is "
                f"only version {dep_plugin.plugin_version}"
            )
        dependencies.append(dep_plugin)
        sub_dependencies = generate_dependency_list(dep_plugin, plugins, seen)
        dependencies.extend(
            sub_depend
            for sub_depend in sub_dependencies
            if not any(
                sub_depend.plugin_id == dependency.plugin_id
                for dependency in dependencies
            )  # ensure no duplicates
        )

    return dependencies


def generate_dependents_list(plugin_id: str, plugins: list[PluginMetadata]):
    """Generates a list of dependents"""

    output = []

    for plugin in plugins:
        dependencies = generate_dependency_list(plugin, plugins)
        if any(dep.plugin_id == plugin_id for dep in dependencies):
            output.append(plugin)

    return output


def create_dependent_dict(
    plugins: list[PluginMetadata],
) -> dict[str, list[PluginMetadata]]:
    return {
        plugin.plugin_id: generate_dependents_list(plugin.plugin_id, plugins)
        for plugin in plugins
    }


def sort_plugins(plugins: list[PluginMetadata]) -> list[PluginMetadata]:
    """Sorts plugins by gradually adding them to our output list.
    Plugins start by being loaded last, gradually we check if they can move
    further up in the load order to let them be loaded sooner. If a plugin is
    found to depend on a plugin that it is being compared against, then it will
    immediately be added after that dependency and the algorithm will move
    onto the next plugin in need of adding to our output.

    What is this algorithm called? Idk, I didn't go to college. I just
    came up with it on the fly. My best guess after trying to find a name is
    a "topological sort" but I think that a class of sorting algorithms rather
    than a specific algorithm. Idk.
    """
    output: list[PluginMetadata] = []
    dependents = create_dependent_dict(plugins)

    for plugin in plugins:
        # iterate through output list in reverse order
        #   (starting with plugins that load last)
        for c, out_plugin in enumerate(reversed(output)):
            out_dependents = dependents[out_plugin.plugin_id]
            # check if our output plugin dependency on the current plugin to
            #   be added- if so, we must place our current plugin AFTER the
            #   one already within the output list
            if any(plugin.plugin_id == dep.plugin_id for dep in out_dependents):
                output.insert(len(output) - c, plugin)  # place plugin after current one
                break
        else:
            output.insert(0, plugin)  # add plugin to the beginning

    return output


__all__ = [
    # Module caching
    "DEFAULT_MODS",
    "set_default_module_cache",
    # context managers
    "add_search_path",
    "set_search_path",
    "set_meta_paths",
    "clear_module_caches",
    # archiver utilities
    "get_recursive_includes",
    "get_distribution_paths",
    # random utils
    "find_plugin_from_list",
    # dependency sorting
    "generate_dependency_list",
    "generate_dependents_list",
    "create_dependent_dict",
    "sort_plugins",
    # Exceptions
    "DependencyError",
    "DependencyOutOfDate",
    "DependencyTooNew",
    "DependencyMissingError",
    "CircularDependencyError",
]
