# Package Plugins as TarGZ

import os
from pathlib import Path

from openpluginloader.defaultstrategy import create_default_manager
from openpluginloader.defaultstrategy.tarplugins import TargzPluginArchiver
from openpluginloader.versioning import parse_api_version

PLUGIN_FOLDER = Path("tests/test_plugins/")
for file in os.listdir(PLUGIN_FOLDER):
    if file.endswith(".tar.gz"):
        os.remove(PLUGIN_FOLDER / file)

manager = create_default_manager(parse_api_version("0.1.0"), PLUGIN_FOLDER, True)


print("=" * 57)
print("Archiving Plugins For Testing Purposes")
print("=" * 57)
print()

for file in os.listdir(PLUGIN_FOLDER):
    if os.path.isdir(PLUGIN_FOLDER / file) and file != "folder_plugin_broken":
        manager.archive_plugin(PLUGIN_FOLDER / file, PLUGIN_FOLDER)

print()
print("=" * 57)
print("Finished Archiving Plugins. Running Tests")
print("=" * 57)
print()
