Utility
========

.. py:currentmodule:: openpluginloader.utility


This module contains useful context managers and utility functions for dealing
with plugin dependencies or the general import environment.

Globals
---------

.. py:data:: DEFAULT_MODS
    :type: dict[str, ModuleType]

    A dictionary representing the default module cache. Think of this as what
    modules will be available to plugins despite, generally, being inaccessible.

Functions
-----------

.. py:function:: set_default_module_cache() -> None

    Sets :py:data:`DEFAULT_MODS` to the current module cache in :py:data:`sys.modules`

.. py:function:: add_search_path(path: str) -> Generator[None, None, None]

    A **context manager** that temporarily adds single item to :py:data:`sys.path`

    (unused)

.. py:function:: set_search_path(new_paths: list[str]) -> Generator[None, None, None]

    A **context manager** that temporarily sets :py:data:`sys.path` to the provided list of new paths.


.. py:function:: set_meta_paths(hooks: list) -> Generator[None, None, None]

    A **context manager** that temporarily sets :py:data:`sys.meta_path` to the provided list of new import hooks.

.. py:function:: clear_module_caches(default: dict[str, ModuleType] | None = None) -> Generator[None, None, None]

    A **context manager** that temporarily clears the module cache (:py:data:`sys.modules`) and replaces it with :code:`default` if provided.

.. py:function:: get_recursive_includes(includes: list[str]) -> list[importlib.metadata.Distribution]

    Takes a list of includes and gets their importlib distributions (including those of indirect includes).
    List is deduplicated.

.. py:function:: get_distribution_paths(dist: importlib.metadata.Distribution) -> list[importlib.metadata.PackagePath]

    Gets the file paths included in a single distribution. Returns an empty list if :py:data:`dist.files` is None.

.. py:function:: find_plugin_from_list(id: str, plugins: list[PluginMetadata])

    Takes a plugin id and finds the corrosponding plugin metadata in a list of plugins.

.. py:function:: generate_dependency_list(plugin: PluginMetadata, plugins: list[PluginMetadata], seen: set[PluginMetadata] | None = None) -> set[PluginMetadata]

    Generates a recursive dependency list for a single plugin. Gets dependencies of dependencies.

    .. tip::

        Don't use the :py:data:`seen` argument. This is simply to avoid infinite recursion.

.. py:function:: generate_dependents_list(plugin: PluginMetadata, plugins: list[PluginMetadata]) -> set[PluginMetadata]

    Generates a list of a **dependents** for a single plugin. These are not the same as a dependency list. These are plugins that DEPEND ON the provided plugin.

.. py:function:: create_dependent_dict(plugins: list[PluginMetadata]) -> dict[str, set[PluginMetadata]]

    Generates a dictionary containing a mapping between plugin id's and their set of dependent plugins.

.. py:function:: sort_plugins(plugins: list[PluginMetadata]) -> list[PluginMetadata]

    Sorts plugins by load order. Ordering is not preserved for plugins with the same loading order.

    .. admonition:: Implementation Details

        Sorts plugins by gradually adding them to our output list.
        Plugins start by being loaded last, gradually we check if they can move
        further up in the load order to let them be loaded sooner. If a plugin is
        found to depend on a plugin that it is being compared against, then it will
        immediately be added after that dependency and the algorithm will move
        onto the next plugin in need of adding to our output.

Exceptions
------------

.. py:exception:: DependencyError(PluginLoadError)

    A generic error in loading dependencies

.. py:exception:: DependencyOutOfDate(DependencyError)

    A requested dependency is out of date

.. py:exception:: DependencyTooNew(DependencyError)

    A requested dependency is too new.

.. py:exception:: DependencyMissingError(DependencyError)

    A requested dependency was not found.

.. py:exception:: CircularDependencyError(DependencyError)

    A circular plugin dependency was detected. ex: :code:`A` requires :code:`B` but :code:`B` requires :code:`A`