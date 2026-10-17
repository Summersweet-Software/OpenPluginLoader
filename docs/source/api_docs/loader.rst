Plugin Loader
==============

.. py:currentmodule:: openpluginloader.loader


.. py:class:: PluginLoader(Protocol)

    An individual strategy used to load a plugin.
    It acts as a collection of functions to control how
    plugins are imported and sorted.


    .. py:method:: load_plugin(self, plugin: PluginMetadata)

        Loads the specified plugin given its metadata.

    .. py:method:: sort_plugin_by_load_order(self, plugin: list[PluginMetadata]) -> list[PluginMetadata]

        Sorts a list of plugins by its load order. Returns a sorted list of plugins.

