Plugin Metadata
=================

.. py:currentmodule:: openpluginloader.metadata


.. py:class:: PluginDependency(plugin_id: str, min_version: ApiVersion, max_version: ApiVersion)

    A :py:class:`NamedTuple` representing a plugin's dependencies inside of a plugin metadata file.

    .. py:attribute:: plugin_id
        :type: str

        The id of the plugin, formatted, :code:`<Author>.<Name>`

    .. py:attribute:: min_version
        :type: ApiVersion

        minimum version this plugin must be in order to satisfy the dependency

    .. py:attribute:: max_version
        :type: ApiVersion

        maximum version this plugin must be in order to satisfy the dependency


.. py:class:: PluginMetadata(author: str, name: str, entry: str, src_path: Path, plugin_version: ApiVersion, min_api_version: ApiVersion, max_api_version: ApiVersion, dependencies: list[PluginDependency], aditional_meta: dict[str, Any])

    A :py:class:`NamedTuple` representing a plugins metadata.

    .. py:attribute:: author
        :type: str

    .. py:attribute:: name
        :type: str

    .. py:attribute:: entry
        :type: str

        The entry point for the plugin's code. Without this we don't know specifically which plugin
        file to import to begin running the plugin's code. Takes the form of a fully-qualified python module name
        :code:`module` or :code:`package.module` or :code:`package.subpkg.module`

    .. py:attribute:: src_path
        :type: Path

        Where the plugin is on disk

    .. py:attribute:: plugin_version
        :type: ApiVersion

    .. py:attribute:: min_api_version
        :type: ApiVersion

        The minimum required plugin api version to allow this plugin to be loaded

    .. py:attribute:: max_api_version
        :type: ApiVersion

        The maximum allowed plugin api version to allow this plugin to be loaded

    .. py:attribute:: dependencies
        :type: list[PluginDependency]

    .. py:attribute:: additional_meta
        :type: dict[str, Any]

        Any additional metadata fields. Populated with current metadata as well in the case of the default
        metadata loader.


    .. py:property:: plugin_id

        The plugins author and name as a string with a dot seperator.

    .. py:method:: __str__(self) -> str

    .. py:method:: __repr__(self) -> str

    .. py:method:: __hash__(self) -> int

        hashes the plugin by using its id. Does not take into account any other metadata.

.. py:exception:: PluginLoadError(Exception)

    A generic error class representing a loading errors.