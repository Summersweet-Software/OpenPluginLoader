from typing import NamedTuple


class ApiVersion(NamedTuple):
    """The API version of a specific plugin api or plugin."""

    major: int
    minor: int
    patch: int | None
    """Patch versioning not required to allow for plugins to support versioning like this: `1.3.*` (written as `1.3`)"""
    tag: str | None
    """Extra data attached to the version."""

    def __gt__(self, other: "ApiVersion | tuple[int | str | None, ...]") -> bool:
        if not isinstance(other, ApiVersion):
            return False

        for c, (self_part, other_part) in enumerate(zip(self, other)):
            if self_part is None or other_part is None:
                continue

            if (
                isinstance(self_part, int)
                and isinstance(other_part, int)  # type checking fuckery.
                and self_part < other_part
            ):
                return False
            if (
                isinstance(self_part, str)
                and isinstance(other_part, str)
                and self_part < other_part
            ):
                return False

            if c == len(self) - 1 and self_part == other_part:
                return False

        return True

    def __ge__(self, other: "ApiVersion | tuple[int | str | None, ...]") -> bool:
        if not isinstance(other, ApiVersion):
            return False

        for self_part, other_part in zip(self, other):
            if self_part is None or other_part is None:
                continue

            if (
                isinstance(self_part, int)
                and isinstance(other_part, int)  # type checking fuckery.
                and self_part < other_part
            ):
                return False
            if (
                isinstance(self_part, str)
                and isinstance(other_part, str)
                and self_part < other_part
            ):
                return False

        return True

    def __lt__(self, other: "ApiVersion | tuple[int | str | None, ...]") -> bool:
        if not isinstance(other, ApiVersion):
            return False

        for c, (self_part, other_part) in enumerate(zip(self, other)):
            if self_part is None or other_part is None:
                continue

            if (
                isinstance(self_part, int)
                and isinstance(other_part, int)  # type checking fuckery.
                and self_part > other_part
            ):
                return False
            if (
                isinstance(self_part, str)
                and isinstance(other_part, str)
                and self_part > other_part
            ):
                return False

            if c == len(self) - 1 and self_part == other_part:
                return False

        return True

    def __le__(self, other: "ApiVersion | tuple[int | str | None, ...]") -> bool:
        if not isinstance(other, ApiVersion):
            return False

        for self_part, other_part in zip(self, other):
            if self_part is None or other_part is None:
                continue

            if (
                isinstance(self_part, int)
                and isinstance(other_part, int)  # type checking fuckery.
                and self_part > other_part
            ):
                return False
            if (
                isinstance(self_part, str)
                and isinstance(other_part, str)
                and self_part > other_part
            ):
                return False

        return True


class VersionFormatError(ValueError): ...


class VersionStringFormatError(VersionFormatError):
    """A version string was improperly formatted"""


class VersionTableFormatError(VersionFormatError):
    """A version table was improperly formatted"""


class VersionTupleFormatError(VersionFormatError):
    """A version tuple was improperly formatted"""


type VersionDict = dict[str, float | int | str]
type VersionTuple = tuple[int, int] | tuple[int, int, int | None] | tuple[
    int, int, int | None, str | None
] | tuple


def parse_string_api_version(version: str) -> ApiVersion:
    """Parses a string formatted in this way: `<major>.<minor>[.patch][.tag]`
    major, minor, and patch version must be numeric characters only ([0-9]).
    version `tag` can be anything.
    """

    parts = version.split(".")

    # Ensure api string has a valid number of parts
    if len(parts) < 2:
        raise VersionStringFormatError(
            f"Version string: `{version}` did not contain enough parts (min 2, major + minor version)."
        )
    if len(parts) > 4:
        raise VersionStringFormatError(
            f"Version string: `{version}` contains too many parts (max 4, major + minor + patch + tag)."
        )

    # validate and get the major version
    if not parts[0].isnumeric():
        raise VersionStringFormatError(
            f"Version string: `{version}` contains an invalid major version (must only contain characters: [0-9])"
        )

    major = int(parts[0])

    # validate and get the minor version
    if not parts[1].isnumeric():
        raise VersionStringFormatError(
            f"Version string: `{version}` contains an invalid minor version (must only contain characters: [0-9])"
        )

    minor = int(parts[1])

    # early return if version string only contains major and minor version
    if len(parts) == 2:
        return ApiVersion(major, minor, None, None)

    if not parts[2].isnumeric():
        raise VersionStringFormatError(
            f"Version string: `{version}` contains an invalid patch version (must only contain characters: [0-9])"
        )

    patch = int(parts[2])

    if len(parts) == 3:
        return ApiVersion(major, minor, patch, None)

    return ApiVersion(major, minor, patch, parts[3])


def parse_table_api_version(version: VersionDict) -> ApiVersion:
    """Parses a table containing a version (containing major and minor version. Optionally containing patch and tag)"""
    major = version.get("major")
    minor = version.get("minor")
    patch = version.get("patch")
    tag = version.get("tag")

    # valid major version and ensure it exists
    if (
        major is None
        or (isinstance(major, str) and not major.isnumeric())
        or isinstance(major, float)
    ):
        raise VersionTableFormatError(
            f"Version table: `{version}` does not contain or contains an invalid major version (must only contain characters: [0-9])"
        )

    # valid minor version and ensure it exists
    if (
        minor is None
        or (isinstance(minor, str) and not minor.isnumeric())
        or isinstance(minor, float)
    ):
        raise VersionTableFormatError(
            f"Version table: `{version}` does not contain or contains an invalid minor version (must only contain characters: [0-9])"
        )

    # validate patch version if exists
    if patch is not None and (
        (isinstance(patch, str) and not patch.isnumeric()) or isinstance(patch, float)
    ):
        raise VersionTableFormatError(
            f"Version table: `{version}` contains an invalid patch version (must only contain characters: [0-9])"
        )

    # valid tag if it exists (ensure its not a float. That would lead to invalid tag string)
    if tag is not None and isinstance(tag, float):
        raise VersionTableFormatError(
            f"Version table: `{version}` contains an invalid tag version (must not be a float)"
        )

    # cast patch version
    if patch is not None:
        patch = int(patch)

    # cast tag version
    if tag is not None:
        tag = str(tag)

    return ApiVersion(int(major), int(minor), patch, tag)


def parse_tuple_api_version(version: VersionTuple) -> ApiVersion:
    """Parses a tuple containing a version (containing major and minor version. Optionally containing patch and tag)"""

    # Ensure api string has a valid number of parts
    if len(version) < 2:
        raise VersionTupleFormatError(
            f"Version tuple: `{version}` did not contain enough parts (min 2, major + minor version)."
        )
    if len(version) > 4:
        raise VersionTupleFormatError(
            f"Version tuple: `{version}` contains too many parts (max 4, major + minor + patch + tag)."
        )

    # valid major and minor version types
    if not isinstance(version[0], int):
        raise VersionTupleFormatError(
            f"Version tuple: `{version}` must contain an integer major version."
        )

    if not isinstance(version[1], int):
        raise VersionTupleFormatError(
            f"Version tuple: `{version}` must contain an integer minor version."
        )

    # early return if there are only 2 version parts
    if len(version) == 2:
        return ApiVersion(version[0], version[1], None, None)

    # ensure patch is an integer if it isn't None
    if version[2] is not None and not isinstance(version[2], int):
        raise VersionTupleFormatError(
            f"Version tuple: `{version}` must contain an integer patch version."
        )

    # early return if there is no tag
    if len(version) == 3:
        return ApiVersion(version[0], version[1], version[2], None)

    # validate tag
    if version[3] is not None and not isinstance(version[3], str):
        raise VersionTupleFormatError(
            f"Version tuple: `{version}` must contain a string tag."
        )

    return ApiVersion(version[0], version[1], version[2], version[3])


def parse_api_version(version: str | VersionDict | VersionTuple):
    """Parses an arbitrary api version (str, dict, or tuple)"""
    match version:
        case str():
            return parse_string_api_version(version)
        case dict():
            return parse_table_api_version(version)
        case tuple():
            return parse_tuple_api_version(version)
        case _:
            raise VersionFormatError("Expected a table, tuple, or string version")
