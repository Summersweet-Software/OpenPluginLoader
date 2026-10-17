Default Strategy
==================

The purpose of the default strategy is to provide a baseline for plugin loading.

Supported plugin types/formats include:

- Folder Plugin's (a folder with a :code:`plugin.toml`)
- Archive Plugins (a targz containing a :code:`plugin.toml`)

Each part/strategy included in this module is reusable. Each part will be documented in depth to ensure
writers of bispoke plugin loaders do not have to create duplicates of functionality already provided to them.

.. important::

    Importing this module, :py:mod:`defaultstrategy <openpluginloader.defaultstrategy>`, will cause
    :py:func:`set_default_module_cache() <openpluginloader.utility.set_default_module_cache>` to be called.


Api Reference
---------------

.. py:currentmodule:: openpluginloader.defaultstrategy


.. py:class:: DefaultMetadataLoader

    Load metadata from tar.gz archives as well as regular folders.
    Implements the :py:class:`PluginMetadataLoader <openpluginloader.metadata.PluginMetadataLoader>` protocol

    .. note::

        Will be split into two classes in the next major version. Many big changes will be made in that version

.. py:class:: DefaultPluginArchiver(*, extension: str = "tar.gz", enable_logging: bool = True)

    :param str extension: The file extension that emitted plugins should have.
    :param bool enable_logging: If true (default) then running :code:`archive_plugin` will output logs to the console/terminal

    Archives plugins in a targz format. Implements the :py:class:`PluginArchiver <openpluginloader.archiving.PluginArchiver>` protocol.


.. py:class:: DefaultPluginScanner

    Finds plugins either in folders or in archive files (targz).

    Implements :py:class:`PluginScanner <openpluginloader.scanner.PluginScanner>` protocol.


.. py:function:: create_default_manager(api_version: ApiVersion, plugin_path: Path, enable_archive_logging: bool = True) -> PluginManager

    Creates the default plugin manager. It does not initialize the hooks inside the plugin manager, you must call that method yourself.

    :param bool enable_archive_logging: Defaults to :code:`True` and changes whether or not `enable_logging` is true for the plugin archiver.