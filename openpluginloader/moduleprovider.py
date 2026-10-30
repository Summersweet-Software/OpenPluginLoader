'''Contains the protocol for "module providers"'''

from contextlib import contextmanager
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Protocol
import typing

if typing.TYPE_CHECKING:
    from openpluginloader.scanner import Plugin


class PluginModuleProvider(Protocol):
    """Provides modules for a given plugin when being imported.
    Despite the common interface with import hooks- these should not be used
    as import hooks most of the time.

    These are used *inside of* a global import-hook that is *always loaded*.

    see: https://docs.python.org/3/glossary.html#term-finder
    """

    @contextmanager
    def setup_execution_environment(self, module: ModuleType):
        """Used when beginning to execute plugin modules."""
        try:
            yield
        finally:
            pass

    def find_spec(
        self, plugin: "Plugin", fullname: str, path, target=None
    ) -> ModuleSpec | None: ...
