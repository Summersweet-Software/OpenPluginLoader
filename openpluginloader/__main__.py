import os
from pathlib import Path
import sys

from openpluginloader.archiving import DefaultPluginArchiver
from openpluginloader.metadata import DefaultMetadataLoader
from openpluginloader.versioning import ApiVersion

CWD = Path(os.getcwd())
DEFAULT_DEST = Path(os.getcwd()) / "build"


def archive_plugin():
    src = CWD if len(sys.argv) < 1 else Path(sys.argv[0])
    dest = DEFAULT_DEST if len(sys.argv) < 2 else Path(sys.argv[1])

    meta_loader = DefaultMetadataLoader()
    archiver = DefaultPluginArchiver()

    meta = meta_loader.load_metadata(src, ApiVersion(1, 0, None, None))

    archiver.archive_plugin(meta, src, dest)
