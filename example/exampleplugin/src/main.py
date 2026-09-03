"""Our plugin entry point."""

from other import example

print("Balls")

example()

# Use import from package that does no exist in our `example` app
import mypy.api

print(mypy.api.__doc__)

import exampleapi

exampleapi.attempt_causing_an_error()
exampleapi.SomeThing(lambda: print("it worked"))
