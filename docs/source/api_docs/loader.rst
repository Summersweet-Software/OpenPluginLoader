Plugin Loader
==============

.. py:currentmodule:: openpluginloader.loader


.. py:class:: PluginLoader(Protocol)

    An individual strategy used to load a plugin.
    It acts as a collection of functions to control how
    plugins are imported and sorted.


    .. py:method:: load_plugin(self, plugin: Plugin)

        Loads the specified plugin given its metadata.

