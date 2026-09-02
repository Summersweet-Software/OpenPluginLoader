from openpluginloader.versioning import (
    ApiVersion,
    VersionStringFormatError,
    VersionTableFormatError,
    VersionTupleFormatError,
    parse_string_api_version,
    parse_table_api_version,
    parse_tuple_api_version,
)


def test_parse_api_string__not_enough_parts():
    try:
        parse_string_api_version("10")
        assert False
    except VersionStringFormatError:
        assert True


def test_parse_api_string__too_many_parts():
    try:
        parse_string_api_version("1.0.2.3")
        assert False
    except VersionStringFormatError:
        assert True


def test_parse_api_string__2_parts():
    ver = parse_string_api_version("1.0")
    assert ver == ApiVersion(1, 0, None, None)


def test_parse_api_string__non_numeric_major_ver():
    try:
        parse_string_api_version("1a.0")
        assert False
    except VersionStringFormatError:
        assert True


def test_parse_api_string__non_numeric_minor_ver():
    try:
        parse_string_api_version("1.0a")
        assert False
    except VersionStringFormatError:
        assert True


def test_parse_api_string__3_parts():
    ver = parse_string_api_version("1.0.5")
    assert ver == ApiVersion(1, 0, 5, None)


def test_parse_api_string__non_numeric_patch_ver():
    try:
        parse_string_api_version("1.0.3e")
        assert False
    except VersionStringFormatError:
        assert True


def test_parse_api_string__4_parts():
    ver = parse_string_api_version("1.0.5-burger")
    assert ver == ApiVersion(1, 0, 5, "burger")


# * Table version


def test_parse_api_table__2_parts():
    ver = parse_table_api_version({"major": 1, "minor": 0})
    assert ver == ApiVersion(1, 0, None, None)


def test_parse_api_table__missing_major():
    try:
        parse_table_api_version({"minor": 0})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__missing_minor():
    try:
        parse_table_api_version({"major": 0})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__float_major():
    try:
        parse_table_api_version({"major": 0.2})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__non_numeric_major():
    try:
        parse_table_api_version({"major": "asf34"})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__float_minor():
    try:
        parse_table_api_version({"major": 1, "minor": 0.2})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__non_numeric_minor():
    try:
        parse_table_api_version({"major": 1, "minor": "asf34"})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__3_parts():
    ver = parse_table_api_version({"major": 1, "minor": 0, "patch": 12})
    assert ver == ApiVersion(1, 0, 12, None)


def test_parse_api_table__float_patch():
    try:
        parse_table_api_version({"major": 23, "minor": 0, "patch": 0.2})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__non_numeric_match():
    try:
        parse_table_api_version({"major": 23, "minor": 0, "patch": "asdf"})
        assert False
    except VersionTableFormatError:
        assert True


def test_parse_api_table__4_parts():
    ver = parse_table_api_version({"major": 1, "minor": 0, "patch": 12, "tag": "alpha"})
    assert ver == ApiVersion(1, 0, 12, "alpha")


def test_parse_api_table__float_tag():
    try:
        parse_table_api_version({"major": 23, "minor": 0, "patch": 0, "tag": 0.2})
        assert False
    except VersionTableFormatError:
        assert True


# * tuple api version
def test_parse_api_tuple__not_enough_parts():
    try:
        parse_tuple_api_version((10,))
        assert False
    except VersionTupleFormatError:
        assert True


def test_parse_api_tuple__too_many_parts():
    try:
        parse_tuple_api_version((1, 2, 5, 7, 9))
        assert False
    except VersionTupleFormatError:
        assert True


def test_parse_api_tuple__2_parts():
    ver = parse_tuple_api_version((1, 0))
    assert ver == ApiVersion(1, 0, None, None)


def test_parse_api_tuple__non_int_major_version():
    try:
        parse_tuple_api_version((0.2, 0))
        assert False
    except VersionTupleFormatError:
        assert True


def test_parse_api_tuple__non_int_minor_version():
    try:
        parse_tuple_api_version((1, 0.5))
        assert False
    except VersionTupleFormatError:
        assert True


def test_parse_api_tuple__3_parts():
    ver = parse_tuple_api_version((1, 0, 5))
    assert ver == ApiVersion(1, 0, 5, None)


def test_parse_api_tuple__non_int_patch_version():
    try:
        parse_tuple_api_version((1, 0, "23"))
        assert False
    except VersionTupleFormatError:
        assert True


def test_parse_api_tuple__4_parts():
    ver = parse_tuple_api_version((1, 0, 5, "burger"))
    assert ver == ApiVersion(1, 0, 5, "burger")


def comparing_api_version_less_than():
    # major and minor only
    assert ApiVersion(1, 0, None, None) < ApiVersion(1, 1, None, None)
    assert not (ApiVersion(1, 0, None, None) < ApiVersion(0, 1, None, None))

    # major, minor, patch
    assert ApiVersion(1, 0, 0, None) < ApiVersion(1, 0, 1, None)
    assert not ApiVersion(1, 0, 3, None) < ApiVersion(1, 0, 1, None)

    # major, minor, patch, tag
    assert ApiVersion(1, 0, 0, "alpha") < ApiVersion(1, 0, 0, "beta")
    assert not ApiVersion(1, 0, 2, "release") < ApiVersion(1, 0, 0, "beta")

    # major and minor only (tag in only one version) (this just needs to not error.)
    assert ApiVersion(1, 0, None, None) < ApiVersion(1, 0, None, "alpha")


def comparing_api_version_less_than_or_equal():
    # major and minor only
    assert ApiVersion(1, 0, None, None) <= ApiVersion(1, 1, None, None)
    assert ApiVersion(1, 0, None, None) <= ApiVersion(1, 0, None, None)
    assert not ApiVersion(1, 3, None, None) <= ApiVersion(1, 0, None, None)

    # major, minor, patch
    assert ApiVersion(1, 0, 0, None) <= ApiVersion(1, 0, 1, None)
    assert ApiVersion(1, 0, 0, None) <= ApiVersion(1, 0, 0, None)
    assert not ApiVersion(1, 0, 5, None) <= ApiVersion(1, 0, 1, None)

    # major, minor, patch, tag
    assert ApiVersion(1, 0, 0, "alpha") <= ApiVersion(1, 0, 0, "beta")
    assert ApiVersion(1, 0, 0, "beta") <= ApiVersion(1, 0, 0, "beta")
    assert not ApiVersion(1, 0, 0, "release") <= ApiVersion(1, 0, 0, "beta")


def comparing_api_version_greater_than():
    # major and minor only
    assert ApiVersion(1, 2, None, None) > ApiVersion(1, 1, None, None)
    assert not (ApiVersion(1, 0, None, None) > ApiVersion(1, 1, None, None))

    # major, minor, patch
    assert ApiVersion(1, 0, 1, None) > ApiVersion(1, 0, 0, None)
    assert not ApiVersion(1, 0, 3, None) > ApiVersion(1, 0, 12, None)

    # major, minor, patch, tag
    assert ApiVersion(1, 0, 1, "alpha") > ApiVersion(1, 0, 0, "beta")
    assert not ApiVersion(1, 0, 0, "release") > ApiVersion(1, 0, 2, "beta")


def comparing_api_version_greater_than_or_equal():
    # major and minor only
    assert ApiVersion(1, 2, None, None) >= ApiVersion(1, 1, None, None)
    assert ApiVersion(1, 0, None, None) >= ApiVersion(1, 0, None, None)
    assert not ApiVersion(0, 1, None, None) >= ApiVersion(1, 0, None, None)

    # major, minor, patch
    assert ApiVersion(1, 0, 2, None) >= ApiVersion(1, 0, 0, None)
    assert ApiVersion(1, 0, 0, None) >= ApiVersion(1, 0, 0, None)
    assert not ApiVersion(1, 0, 5, None) >= ApiVersion(1, 0, 12, None)

    # major, minor, patch, tag
    assert ApiVersion(1, 0, 0, "beta") >= ApiVersion(1, 0, 0, "alpha")
    assert ApiVersion(1, 0, 0, "beta") >= ApiVersion(1, 0, 0, "beta")
    assert not ApiVersion(1, 0, 0, "alpha") >= ApiVersion(1, 0, 0, "beta")
