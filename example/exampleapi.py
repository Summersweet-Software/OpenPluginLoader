from typing import Callable

from openpluginloader.versioning import ApiVersion

API_VERSION = ApiVersion(1, 0, 0, "release")


def attempt_causing_an_error():
    """Should only work if a plugin packages mypy"""
    import mypy  # not a dependency we own!


EXAMPLE_THINGS = []


class SomeThing:
    def __init__(self, foo: Callable):
        self.foo = foo

        EXAMPLE_THINGS.append(self)
