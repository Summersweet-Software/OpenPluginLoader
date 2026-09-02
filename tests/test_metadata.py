from pathlib import Path

from openpluginloader.metadata import PluginDependency, PluginMetadata
from openpluginloader.versioning import parse_api_version

example_meta = (
    PluginMetadata(
        author="JoshKatz",
        name="D",
        entry="",
        src_path=Path(),
        plugin_version=parse_api_version("0.1.0"),
        min_api_version=parse_api_version("0.1.0"),
        max_api_version=parse_api_version("0.1.0"),
        dependencies=[
            PluginDependency(
                "JoshKatz.A", parse_api_version("0.1.0"), parse_api_version("0.1.0")
            )
        ],
        aditional_meta={},
    ),
)


def test_metadata__repr__():
    """Ensure __repr__ doesn't error"""

    output = example_meta.__repr__()
    assert output != ""
    assert isinstance(output, str)


def test_metadata__str__():
    """Ensure __str__ doesn't error"""

    output = example_meta.__str__()
    assert output != ""
    assert isinstance(output, str)
