Plugin Scanners
=================

Plugin scanners are what actually search for your plugins. They tell you what plugins you actually *can* load in.

.. py:currentmodule:: openpluginloader.scanner


.. py:class:: PluginScanner(Protocol)

    An individual strategy used to scan for available plugins

    .. py:method:: get_available_plugins(self, api_version: ApiVersion) -> list[PluginMetadata]

        Gets all available plugins to be loaded
