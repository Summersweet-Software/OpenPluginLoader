Tar Plugins
=============

.. py:currentmodule:: openpluginloader.defaultstrategy.tarplugins


OPL Machinery
---------------

.. py:class:: TargzPluginScanner(PluginScanner)

    Finds and setups up TarGZPlugins.
    These are plugins in a targz file.


.. py:class:: TargzPluginMetadataLoader(PluginMetadataLoader)

    Loads metadata from targz plugins.


.. py:class:: TargzPluginArchiver(PluginArchiver)

    Archives plugins in a targz format


.. py:class:: TargzModuleProvider(sub_path: Path)

    :param Path sub_path: a path inside of the targz file-structure to begin searching for modules.

    Basic module provider for finding modules inside of targz plugins.


.. py:class:: TargzLoadTimeModuleProvider(sub_path: Path)

    Does the same thing as :py:class:`TargzModuleProvider <openpluginloader.defaultstrategy.tarplugins.TargzModuleProvider>`.
    Seperated for future differentiation if at all necessary.

Import Machinery
------------------

.. py:class:: TargzModuleLoader(FileLoader)

    Loads file contents from a Targz-plugin's module(s)

    see: https://docs.python.org/3/library/importlib.html#importlib.abc.Loader

