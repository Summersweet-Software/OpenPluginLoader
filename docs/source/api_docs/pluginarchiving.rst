Plugin Archivers
=================

Plugin Archivers determine how archives are created and unpacked. These are useful for bundling dependencies within plugins themselves.
They are also useful for things like `plugin signing <https://en.wikipedia.org/wiki/Code_signing>`_.

.. py:currentmodule:: openpluginloader.archiving


.. py:class:: PluginArchiver(Protocol)

    An individual strategy used to archive and dearchive plugins.

    .. py:method:: archive_plugin(self,  meta: PluginMetadata, src: Path, destination: Path) -> Path

        Takes a plugin (:code:`meta`) and looks at the source and destination paths provided to create an archived plugin

        :returns: The final path to the archive file

    .. py:method:: dearchive_plugin(self, src: Path, destination: Path) -> Path

        Takes an archived plugin at a specific source path and dumps the contents in a
        destination path provided.

        :returns: The final path to the archived file/folder