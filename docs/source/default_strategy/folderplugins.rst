Folder Plugins
================

.. py:currentmodule:: openpluginloader.defaultstrategy.folderplugins


OPL Machinery
---------------

.. py:class:: FolderPluginScanner(PluginScanner)

    Finds and setups up folder-plugins
    These are plugins in a basic folder.


.. py:class:: FolderPluginMetadataLoader(PluginMetadataLoader)

    Loads metadata from folder plugins.


.. py:class:: FolderModuleProvider(PluginModuleProvider)

    Basic module provider for finding modules inside of folder plugins.


.. py:class:: FolderLoadTimeModuleProvider(FolderModuleProvider)

    Does the same thing as :py:class:`FolderModuleProvider <openpluginloader.defaultstrategy.folderplugins.FolderModuleProvider>`.
    Seperated for future differentiation if at all necessary.

Import Machinery
------------------

.. py:class:: FolderModuleLoader(FileLoader)

    Loads file contents from a folder-plugin's module(s)

    see: https://docs.python.org/3/library/importlib.html#importlib.abc.Loader

