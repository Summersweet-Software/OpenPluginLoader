Plugin Scanners
=================

Plugin scanners are what actually search for your plugins. They tell you what plugins you actually *can* load in.

.. py:currentmodule:: openpluginloader.scanner

Dataclasses
-------------

.. py:class:: Plugin(metadata: PluginMetadata, metaloader: PluginMetadataLoader, loader: PluginLoader, archiver: PluginArchiver, module_provider: PluginModuleProvider, module_loadtime_provider: PluginModuleProvider, scanner_source: PluginScanner)

    A :py:class:`Dataclass` representing a plugin via its metadata and loading strategies.

    .. py:attribute:: metadata
        :type: PluginMetadata

    .. py:attribute:: metaloader
        :type: PluginMetadataLoader

        Defines the metadataload used when loading the plugin metadata.
        This makes it possible to reload metadata if necessary.

    .. py:attribute:: loader
        :type: PluginLoader

        The loader used to load the plugin when the manager object calls :py:func:`load_plugin <openpluginloader.manager.PluginManager.load_plugin>`

    .. py:attribute:: archiver
        :type: Archiver

    .. py:attribute:: module_provider
        :type: PluginModuleProvider

        Provides what sub-modules are available (and also what happens when you import the plugin-base) when doing imports of plugin modules.

    .. py:attribute:: module_loadtime_provider
        :type: PluginModuleProvider

        Provides what modules are available during the time a plugin is being loaded in.
        This allows plugins themselves to find specific modules only available inside themselves.

    .. py:attribute:: scanner_source
        :type: PluginScanner

        The scanner that produced this :py:class:`Plugin` object.

Protocols
-----------

.. py:class:: PluginScanner(Protocol)

    An individual strategy used to scan for available plugins

    .. py:method:: get_available_plugins(self, api_version: ApiVersion) -> list[Plugin]

        Gets all available plugins to be loaded
