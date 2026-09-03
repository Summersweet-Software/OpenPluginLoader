"""Our example project"""

from pathlib import Path
import sys

EXTRA = (Path(__file__).parent / "../").absolute().__str__()
print(EXTRA)
sys.path.append(EXTRA)
import exampleapi
from openpluginloader.utility import set_default_module_cache

# needs to occur early. If this isn't possible then we should manually cull modules.
set_default_module_cache()

from openpluginloader.defaultstrategy import create_default_manager

try:
    exampleapi.attempt_causing_an_error()
    assert False
except ImportError:
    assert True

plugin_manager = create_default_manager(
    exampleapi.API_VERSION, plugin_path=Path("plugins")
)

plugin_manager.initialize_hooks()
plugin_manager.discover_plugins()
plugin_manager.load_all_plugins()


for obj in exampleapi.EXAMPLE_THINGS:
    obj.foo()
