Versions
==========

This module contains all files related to versioning. This is mostly the actual :py:class:`ApiVersion`
class itself as well as several utility functions for loading versions.

.. py:currentmodule:: openpluginloader.versioning


.. py:class:: ApiVersion(major: int, minor: int, patch: int | None, tag: str | None)

    A :py:class:`NamedTuple` representing a version. Formatted using `Semantic Versioning <https://semver.org/>`_.

    .. py:attribute:: major
        :type: int

    .. py:attribute:: minor
        :type: int

    .. py:attribute:: patch
        :type: int | None

        Optional patch version.

    .. py:attribute:: tag
        :type: str | None

        Optional tag version. Things like :code:`-alpha` or :code:`-rc1`

    .. py:method:: __gt__(self, other: ApiVersion | tuple[int | str | None, ...]) -> bool:

        Checks if our own version is greater than another version

    .. py:method:: __lt__(self, other: ApiVersion | tuple[int | str | None, ...]) -> bool:

        Checks if our own version is less than another version

    .. py:method:: __ge__(self, other: ApiVersion | tuple[int | str | None, ...]) -> bool:

        Checks if our own version is greater than or equal to another version

    .. py:method:: __le__(self, other: ApiVersion | tuple[int | str | None, ...]) -> bool:

        Checks if our own version is less than or equal to another version

    .. py:method:: __repr__(self) -> str:

        Prints a version in its shortest form in general semantic versioning style.
        ex:

        - :code:`v1.0`
        - :code:`v1.0.2`
        - :code:`v1.0-alpha`
        - :code:`v1.0.2-alpha`



----


.. py:function:: parse_string_api_version(version: str) -> ApiVersion

    Parses a string formatted in this way: `<major>.<minor>[.<patch>][-<tag>]`
    major, minor, and patch version must be numeric characters only ([0-9]).
    version `tag` can be anything.

    Returns a validated api version

    :raises VersionStringFormatError: When the formatting is incorrect

.. py:function:: parse_table_api_version(version: VersionDict) -> ApiVersion

    Parses a table containing a version (containing major and minor version. Optionally containing patch and tag)

    Returns a validated api version

    :raises VersionTableFormatError: When the formatting is incorrect

.. py:function:: parse_tuple_api_version(version: VersionDict) -> ApiVersion

    Parses a tuple containing a version (containing major and minor version. Optionally containing patch and tag)

    Returns a validated api version

    :raises VersionTupleFormatError: When the formatting is incorrect

----


.. py:type:: VersionDict
    :canonical: dict[str, float | int | str]

.. py:type:: VersionTuple
    :canonical: tuple[int, int] | tuple[int, int, int | None] | tuple[int, int, int | None, str | None] | tuple

----


.. py:exception:: VersionFormatError(ValueError)

    Represents a generic formatting error in a version

.. py:exception:: VersionStringFormatError(VersionFormatError)

    A version string was improperly formatted

.. py:exception:: VersionTableFormatError(VersionFormatError)

    A version table was improperly formatted

.. py:exception:: VersionTupleFormatError(VersionFormatError)

    A version tuple was improperly formatted