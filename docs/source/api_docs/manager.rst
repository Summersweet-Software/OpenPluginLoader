Plugin Manager
================

.. py:currentmodule:: openpluginloader.manager


.. py:class:: PluginManager(self, *, metadata_loader: PluginMetadataLoader, loading_strategy: PluginLoader, archiver: PluginArchiver, plugin_scanner: PluginScanner, api_version: ApiVersion, import_hooks: list,)

    .. py:attribute:: metadata_loader
        :type: PluginMetadataLoader

    .. py:attribute:: loading_strategy
        :type: PluginLoader

    .. py:attribute:: archiver
        :type: PluginArchiver

    .. py:attribute:: plugin_scanner
        :type: PluginScanner

    .. py:attribute:: api_version
        :type: ApiVersion

    .. py:attribute:: import_hooks
        :type: list

    .. py:attribute:: known_plugins
        :type: list[PluginMetadata]

        This is where plugins are stored after discovery.
        By default, they will be sorted. Manually running plugin discovery
        (via :py:attr:`plugin_scanner.get_available_plugins <openpluginloader.scanner.PluginScanner.get_available_plugins>`) will not, by default,
        be sorted.

    .. py:method:: initialize_hooks(self) -> None

        Initializes all import hooks passed into the constructor.
        This sets up important import machinery necessary to make many
        plugin loading strategies work.

    .. py:method:: deinitialize_hooks(self) -> None

        Removes added import hooks from the :py:const:`sys.meta_path` variable.

        .. warning::

            This is not recommended to be used. This is only provided as a convenience
            and to standardize the functionality

    .. py:method:: load_plugin(self, plugin: PluginMetadata) -> None

            Does api version checking before loading a plugin using the
            loading strategy specified in :py:attr:`loading_strategy`

            .. important::

                Returns whatever :py:attr:`loading_strategy.load_plugin <openpluginloader.loader.PluginLoader.load_plugin>` returns. This *should* be None
                according to the :py:class:`~openpluginloader.loader.PluginLoader` Protocol definition, but implementors may explicitly
                choose to not follow this protocol.

                You should also run :py:func:`initialize_hooks()` first!

    .. py:method:: load_all_plugins(self)

        Loads all plugins found in :py:attr:`known_plugins`.

        .. important::

            ensure you first run :py:func:`initialize_hooks()`

        :raises PluginOutOfDate: When the manager's api version is greater than the plugins maximum version.
        :raises PluginTooNew: When the manager's api version is less than than the plugins minimum version.

    .. py:method:: discover_plugins(self) -> list[PluginMetadata]

        Discovers and sorts all plugins. Stores them in :py:attr:`known_plugins`

    .. py:property:: hooks_are_initialized
        :type: bool

        A boolean telling you if all the hooks have been initialized.

----

.. py:class:: PluginMetadataLoader(Protocol)

    A strategy to load metadata from a plugin.

    .. py:function:: contains_meta(self, plugin_src: Path) -> bool

        A function to determine if a specific plugin file/path includes a metadata file

    .. py:function:: load_metadata(self, plugin_src: Path, api_version: ApiVersion) -> bool

        Loads the metadata from a plugin file/path. Api version of the plugin manager/api is provided for any validation.

        