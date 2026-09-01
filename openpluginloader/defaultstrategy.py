"""The default strategy for loading plugins."""

import importlib
from importlib.abc import FileLoader
from importlib.machinery import ModuleSpec
import os
from pathlib import Path
import tarfile
import tomllib
from types import ModuleType
import typing

from openpluginloader.loader import PluginManager
from openpluginloader.metadata import (
    PluginLoadError,
    PluginMetadata,
    PluginMetadataLoader,
)
from openpluginloader.scanner import PluginScanner
from openpluginloader.utility import (
    DEFAULT_MODS,
    clear_module_caches,
    get_distribution_paths,
    get_recursive_includes,
    set_default_module_cache,
    set_meta_paths,
    sort_plugins,
)
from openpluginloader.versioning import ApiVersion, parse_api_version
import importlib._bootstrap
import importlib._bootstrap_external

# if not typing.TYPE_CHECKING:
# # Ensure GzipFile is included
# #   (stops things from breaking when we reset module cache)
from gzip import GzipFile

set_default_module_cache()  # (VERY IMPORTANT)


class DefaultMetadataLoader:
    """Load metadata from tar.gz archives as well as regular folders."""

    __slots__ = ()

    def __init__(self):
        pass

    def contains_meta(self, plugin_src: Path) -> bool:
        if plugin_src.is_file():
            with tarfile.open(plugin_src, "r:gz") as file:
                return "plugin.toml" in file.getnames()
        else:
            return (plugin_src / "plugin.toml").exists()

    def load_metadata(
        self, plugin_src: Path, api_version: ApiVersion
    ) -> PluginMetadata:
        # Load plugin pyproject config
        if os.path.exists(plugin_src / "pyproject.toml"):
            with open(plugin_src / "pyproject.toml", "r") as f:
                config = tomllib.loads(f.read())
                plugin_config = config.get("tool", {}).get("plugin", {})
                if (new_src := plugin_config.get("src")) is not None:
                    if Path(new_src).is_absolute():
                        plugin_src = new_src
                    else:
                        plugin_src = plugin_src / new_src

        data = ""
        if plugin_src.is_file():
            with tarfile.open(plugin_src, "r:gz") as file:
                dataio = file.extractfile("plugin.toml")
                if dataio is None:
                    raise PluginLoadError("Missing `plugin.toml` file")
                data = dataio.read().decode()
        else:
            with open(plugin_src / "plugin.toml", "r") as file:
                data = file.read()

        table = tomllib.loads(data)

        return PluginMetadata(
            author=table["author"],
            name=table["name"],
            entry=table["entry"],
            src_path=plugin_src,
            plugin_version=parse_api_version(table["version"]),
            min_api_version=parse_api_version(
                table.get("min_api_version", api_version)
            ),
            max_api_version=parse_api_version(
                table.get("max_api_version", api_version)
            ),
            dependencies=table.get("dependencies", []),
            aditional_meta=table,
        )


class DefaultPluginArchiver:
    """Archives plugins in a targz format"""

    __slots__ = ("extension", "enable_logging")

    extension: str
    """File extension used for file"""
    enable_logging: bool

    def __init__(self, *, extension: str = "tar.gz", enable_logging=True):
        self.extension = extension
        self.enable_logging = enable_logging

    def log(self, *args, **kwargs):
        if not self.enable_logging:
            return
        print(*args, **kwargs)

    def archive_plugin(
        self, meta: PluginMetadata, src: Path, destination: Path
    ) -> Path:
        includes = []
        exclude_paths = [".venv/*", ".env/*"]

        # if destination path exists inside of src path, we should
        #   exclude the destination path
        if destination.full_match(src):
            exclude_paths.append(str(destination.relative_to(src)))

        # Load plugin pyproject config
        if os.path.exists(src / "pyproject.toml"):
            with open(src / "pyproject.toml", "r") as f:
                config = tomllib.loads(f.read())
                plugin_config = config.get("tool", {}).get("plugin", {})
                includes = plugin_config.get("includes", includes)
                exclude_paths = plugin_config.get("exclude_paths", exclude_paths)
                if (new_src := plugin_config.get("src")) is not None:
                    if Path(new_src).is_absolute():
                        src = new_src
                    else:
                        src = src / new_src

        include_dists = get_recursive_includes(includes)

        final_path = destination / f"{meta.plugin_id}.{self.extension}"

        os.makedirs(destination, exist_ok=True)
        if os.path.exists(final_path):
            os.remove(final_path)

        with tarfile.open(final_path, "x:gz") as output_file:
            included_files = []
            self.log("Adding Include Packages:")
            # add files from includes
            for dist in include_dists:
                self.log(f"- {dist.name}=={dist.version}")
                # Add every file into tarfile's site-packages.
                for dist_file in get_distribution_paths(dist):
                    if dist_file in included_files:
                        continue
                    included_files.append(dist_file)
                    output_file.add(
                        dist_file.locate(), f"site-packages/{str(dist_file)}"
                    )

            self.log()
            self.log("Adding Project Files:")

            for root, _, files in src.walk():
                for proj_file in files:
                    full_path = root / proj_file
                    reparented = full_path.relative_to(src)
                    if any(reparented.full_match(item) for item in exclude_paths):
                        continue
                    self.log(f"- {reparented}")
                    output_file.add(full_path, str(reparented))

        return final_path

    def dearchive_plugin(self, src: Path, destination: Path) -> Path:
        with tarfile.open(src, "r:gz") as f:
            f.extractall(destination)
        return destination


class DefaultPluginScanner:
    """The plugin scanning strategy used"""

    __slots__ = ("plugin_path", "meta_loader")

    def __init__(self, plugin_path: Path, meta_loader: PluginMetadataLoader):
        self.plugin_path = plugin_path
        self.meta_loader = meta_loader

    def _is_plugin_dir(self, dir: Path) -> bool:
        return dir.is_dir() and self.meta_loader.contains_meta(dir)

    def _is_plugin_archive(self, dir: Path) -> bool:
        return dir.is_file() and self.meta_loader.contains_meta(dir)

    def get_available_plugins(self, api_version: ApiVersion) -> list[PluginMetadata]:
        output: list[PluginMetadata] = []
        for file in os.listdir(self.plugin_path):
            plugin_src = self.plugin_path / file
            if not self.meta_loader.contains_meta(plugin_src):
                continue
            output.append(self.meta_loader.load_metadata(plugin_src, api_version))
        return output


class TarGzLoader(FileLoader):
    """Loads data from a targz"""

    tar_file_path: Path

    def __init__(self, fullname, path, tar_file_path: Path):
        super().__init__(fullname, path)
        self.tar_file_path = tar_file_path

    def get_dunder_init_data(self, path: str) -> bytes:
        """Get archive's `__init__.py` file's contents OR send blank data
        if that file does not exist.
        """
        with tarfile.open(self.tar_file_path, "r:gz") as f:
            if str(path) + "/__init__.py" not in f.getnames():
                return b""
            fileio = f.extractfile("__init__.py")
            if fileio is None:
                return b""
            return fileio.read()

    def get_data(self, path: str) -> bytes:
        if not str(path).endswith(".py"):
            return self.get_dunder_init_data(path)

        reparented = Path(path).relative_to(self.tar_file_path)
        with tarfile.open(self.tar_file_path, "r:gz") as f:
            if str(reparented).replace("\\", "/") not in f.getnames():
                raise ImportError(reparented)  # module not found.
            fileio = f.extractfile(str(reparented).replace("\\", "/"))
            if fileio is None:
                return b""
            return fileio.read()

    def get_source(self, fullname):
        return self.get_data(self.path).decode()


class TarGzPluginLoader(TarGzLoader):
    """Load targz plugins. Modifies exec_module in order to add site-packages"""

    def create_module(self, spec) -> None:
        return

    def load_module(self, fullname: str | None = None) -> ModuleType:
        return importlib._bootstrap._load_module_shim(self, fullname)

    def exec_module(self, module: ModuleType):
        importlib.invalidate_caches()

        with clear_module_caches(DEFAULT_MODS):
            with set_meta_paths(
                [
                    TarGzImportHook(self.tar_file_path, Path("site-packages")),
                    TarGzImportHook(self.tar_file_path, Path()),
                ]
            ):
                return importlib._bootstrap_external.SourceLoader.exec_module(
                    self, module
                )


class PluginFolderLoader(FileLoader):
    def get_data(self, path) -> bytes:
        return b""

    def get_source(self, fullname):
        return self.get_data(self.path).decode()


class TarGzImportHook:
    """Is able to search for inside of a targz containing a `site-packages` folder"""

    tar_file_path: Path

    sub_path: Path
    """A path inside of the targz to begin searching"""

    def __init__(self, tar_file_path: Path, sub_path: Path):
        self.tar_file_path = tar_file_path
        self.sub_path = sub_path

    def find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None:
        fullname_path = self.sub_path / "/".join(fullname.split("."))
        if isinstance(path, list):
            path = path[0] if len(path) > 0 else None

        with tarfile.open(self.tar_file_path, "r:gz") as f:
            names = f.getnames()
            if any(Path(name).is_relative_to(fullname_path) for name in names):
                spec = ModuleSpec(
                    fullname,
                    TarGzLoader(
                        fullname,
                        str(self.tar_file_path / fullname_path),
                        self.tar_file_path,
                    ),
                    origin=path,
                    is_package=True,
                )

                spec.has_location = True
            elif (str(fullname_path).replace("\\", "/") + ".py") in names:
                spec = ModuleSpec(
                    fullname,
                    TarGzLoader(
                        fullname,
                        str(self.tar_file_path / (str(fullname_path) + ".py")),
                        self.tar_file_path,
                    ),
                    origin=path,
                    is_package=False,
                )

                spec.has_location = True
            else:
                return None
            return spec


class TarGzPluginImportHook:
    """An import hook that interprets any modules prefixed as `plugin.<plugin-name>` as
    a plugin within whatever plugin path is being used
    """

    plugin_path: Path
    known_plugins: list[PluginMetadata]
    plugin_module_cache: dict[str, ModuleSpec]
    plugins_module: ModuleSpec

    def __init__(
        self,
        plugin_path: Path,
        known_plugins: list[PluginMetadata],
    ):
        self.plugin_path = plugin_path

        self.known_plugins = known_plugins
        self.plugin_module_cache: dict[str, ModuleSpec] = {}

        self.plugins_module = ModuleSpec(
            "plugins",
            PluginFolderLoader("plugins", str(plugin_path)),
            origin=str(plugin_path),
            is_package=True,
        )

        if self.plugins_module.submodule_search_locations is not None:
            self.plugins_module.submodule_search_locations.append(
                str(plugin_path.absolute())
            )
        self.plugins_module.has_location = True

    def find_module(
        self,
        fullname,
        path,
    ): ...

    def create_plugin_module(
        self, plugin_meta: PluginMetadata, fullname: str
    ) -> ModuleSpec:
        path_parts = fullname.split(".")
        if len(path_parts) == 2:
            path = str(plugin_meta.src_path)
        else:
            path = (
                "/".join([str(plugin_meta.src_path), *fullname.split(".")[2:]]) + ".py"
            )
        spec = ModuleSpec(
            fullname,
            TarGzPluginLoader(
                fullname,
                path,
                plugin_meta.src_path,
            ),
            origin=path,
            is_package=True,
        )

        spec.has_location = True

        return spec

    def find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None:
        if fullname == "plugins":
            return self.plugins_module

        if not fullname.startswith("plugins."):
            return

        fullname_parts = fullname.split(".")
        plugin_name = fullname_parts[1]

        corrosponding_plugin = None

        for plugin in self.known_plugins:
            if plugin.name != plugin_name:
                continue
            corrosponding_plugin = plugin

        if corrosponding_plugin is None:
            return

        # Use plugin entry when trying to import `__ENTRY__`
        if len(fullname_parts) >= 3 and fullname_parts[2] == "__ENTRY__":
            fullname_parts[2] = corrosponding_plugin.entry
            fullname = ".".join(fullname_parts)

        if fullname in self.plugin_module_cache.keys():
            return self.plugin_module_cache[fullname]

        return self.plugin_module_cache.setdefault(
            fullname, self.create_plugin_module(corrosponding_plugin, fullname)
        )


class ImportLoader:
    """The default loading strategy for plugins.
    Uses dynamic imports and temporarily modifies python's path environment.
    """

    def __init__(self):
        pass

    def load_plugin(self, plugin: PluginMetadata):
        """Loads an individual plugin"""
        importlib.import_module(f"plugins.{plugin.name}.__ENTRY__")

    def sort_plugins_by_load_order(
        self, plugins: list[PluginMetadata]
    ) -> list[PluginMetadata]:
        """Determines the load order of plugins"""
        return sort_plugins(plugins)


def create_default_manager(
    api_version: ApiVersion, plugin_path: Path, enable_archive_logging=True
) -> PluginManager:
    """Creates the default plugin manager

    enable_archive_logging - when enabled- archiving will print out added
      site-packages and files
    """

    meta_loader = DefaultMetadataLoader()
    scanner = DefaultPluginScanner(plugin_path, meta_loader)

    return PluginManager(
        metadata_loader=meta_loader,
        loading_strategy=ImportLoader(),
        archiver=DefaultPluginArchiver(enable_logging=enable_archive_logging),
        plugin_scanner=scanner,
        api_version=api_version,
        import_hooks=[
            TarGzPluginImportHook(
                plugin_path, scanner.get_available_plugins(api_version)
            ),
        ],
    )
