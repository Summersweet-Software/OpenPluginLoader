Module Providers
==================

Plugin module providers allow you to set the method for finding modules inside of plugins.
Scanners set the provider for each plugin they find. Each plugin gets 2 providers.

One is used during regular imports from outside of the plugin itself.

The other is used during the loading of the given plugin.
This is useful for relative module imports inside of plugins.

.. py:currentmodule:: openpluginloader.moduleprovider


.. py:class:: PluginModuleProvider

    Provides modules for a given plugin when being imported.
    Despite the common interface with import hooks- these should not be used
    as import hooks most of the time.

    These are used *inside of* a global import-hook that is *always loaded*.

    see: https://docs.python.org/3/glossary.html#term-finder

    .. py:method:: setup_execution_environment(self, module: ModuleType) -> Generator[None, Any, None]

        A context manager used to setup the module execution environment. Can be used to setup fake modules, change path variables, etc.

    .. py:method:: find_spec(self, plugin: Plugin, fullname: str, path: str | list[str], target=None) -> ModuleSpec | None

        Acts similarly to :py:func:`find_spec` inside of regular python import-hooks. The difference being that a plugin is provided.