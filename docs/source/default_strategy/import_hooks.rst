Import Hooks
==============

These are all of the import hooks and what they do.
These are integral for the inner workings of this plugin loader.

.. py:currentmodule:: openpluginloader.defaultstrategy


.. py:class:: DefaultPluginImportHook(plugin_path: Path, known_plugins: list[PluginMetadata])

    An import hook that creates a :py:mod:`plugins` package to allow plugins to be imported as if they were regular modules/packages.
    This import hook also acts as if it "owns" the :py:mod:`plugins` namespace, not allowing other import hooks to take over
    if a specified sub-package/module was not located.

    .. important::

        Plugins are provided via their name, not their file/folder names.

    .. note::

        A magic :py:mod:`__ENTRY__` sub-module is also provided which points to a plugin's
        entry module.

    .. py:attribute:: plugin_path
        :type: Path

        path to where plugins are located. Necessary to determine module paths.

    .. py:attribute:: known_plugins
        :type: list[PluginMetadata]

        A list of available plugins for this hook to use.

    .. py:attribute:: plugin_module_cache
        :type: dict[str, ModuleSpec]

        An internal cache mapping full module names to their specific spec.

    .. py:attribute:: plugins_module
        :type: ModuleSpec

        The parent module for all plugin modules. (The :py:mod:`plugins` namespace/packge)

    .. py:method:: find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None

        Returns a module specification for a module if it is a plugin, if not None is returned.

        :raises ImportError: when importing a non-existent plugin from the :py:mod:`plugins` namespace

.. warning::

    This is not a complete list. Since these are going to be reworked, it felt unncessary to fully document these hooks for the short amount of time
    between versions.