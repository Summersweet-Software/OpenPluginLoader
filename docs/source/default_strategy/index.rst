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


.. py:class:: ImportpluginLoader(PluginLoader)

    The default loading strategy for plugins.
    Uses dynamic imports and temporarily modifies python's path environment
    (from within import hooks local to Plugins themselves).

    .. py:method:: load_plugin(self, plugin: Plugin)

        Loads a plugin by importing :code:`f"plugins.{plugin.metadata.name}.__entry__"`


.. py:function:: create_default_manager(api_version: ApiVersion, plugin_path: Path, enable_archive_logging=True ) -> PluginManager

    :param bool enable_archive_logging: when enabled- archiving will print out added site-packages and files

    Creates the default plugin manager. This contains the :py:class:`TargzPluginScanner` and :py:class:`FolderPluginScanner`

    