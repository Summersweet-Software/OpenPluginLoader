Import Machinery
==================

These are all of the import hooks and what they do.
These are integral for the inner workings of this plugin loader.

.. py:currentmodule:: openpluginloader.defaultstrategy.importmachinery

Python Import-Hooks and FileLoaders
-------------------------------------

.. py:class:: PluginFolderLoader()

    A file loader for the fake "plugins" package.
    This returns empty data to python during module import.


.. py:class:: PluginModuleLoaderShim(plugin: Plugin, module_provider: PluginModuleProvider, loader: FileLoader, changes_metapaths: bool)

    A file loader that acts as shim around file loaders provided by :py:class:`PluginModuleProviders <openpluginloader.moduleprovider.PluginModuleProvider>`

    .. py:method:: get_data(self, path) -> bytes

        A transparent shim around :py:func:`loader.get_data`

    .. py:method:: get_source(self, fullname) -> str | None

        A transparent shim around :py:func:`loader.get_source`

    .. py:method:: load_module(self, fullname: str | None = None) -> ModuleType

        A transparent shim around :py:func:`loader.load_module`

    .. py:method:: exec_module(self, module: ModuleType) -> None:

        Changes the execution environment by:

        - invalidating module caches
        - using :py:const:`DEFAULT_MODS` to set the :py:data:`sys.modules`
        - resetting metapaths to only include :py:class:`DefaultPluginLoadTimeImportHook`, :py:class:`BuiltinImporter`, :py:class:`DefaultGlobalPluginImportHook`
        - running :py:func:`module_provider.setup_execution_environment`

        Then it runs :py:func:`loader.exec_module`


.. py:class:: DefaultPluginLoadTimeImportHook(plugin: Plugin)

    An import hook added during plugin loadtime.

    .. py:method:: find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None

        Uses plugin's :py:attr:`module_loadtime_provider` and runs :py:func:`find_spec`
        If a loader is provided, it creates a shim around it. This shim has :py:data:`changes_metapaths` set to :py:const:`False`


.. py:class:: DefaultGlobalPluginImportHook(plugin_path: Path, manager: PluginManager)

    An always-active import hook providing the :code:`plugins` package for import in your codebase.

    .. py:method:: create_plugin_module(self, plugin: Plugin, fullname: str, path, target) -> ModuleSpec | None

        uses plugin's :py:attr:`module_provider` to find the plugin module being referenced.
        If a module with a loader is provided then a shim will be wrapped around it.
        This shim has :py:data:`changes_metapaths` set to :py:const:`True`

    .. py:method:: find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None

        provides plugin modules, keeps a cache seperate from :py:data:`sys.modules`.

