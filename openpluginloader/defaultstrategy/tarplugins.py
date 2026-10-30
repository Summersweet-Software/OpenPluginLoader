import importlib
from importlib.abc import FileLoader
from importlib.machinery import ModuleSpec
import os
from pathlib import Path
import tarfile
import tomllib
from types import ModuleType

from openpluginloader.archiving import PluginArchiver
from openpluginloader.loader import PluginLoader
from openpluginloader.metadata import (
    PluginDependency,
    PluginLoadError,
    PluginMetadata,
    PluginMetadataLoader,
)
from openpluginloader.moduleprovider import PluginModuleProvider
from openpluginloader.scanner import Plugin, PluginScanner
from openpluginloader.utility import (
    get_distribution_paths,
    get_recursive_includes,
    set_default_module_cache,
)
from openpluginloader.versioning import ApiVersion, parse_api_version

import importlib._bootstrap
import importlib._bootstrap_external

# Ensure GzipFile is included
#   (stops things from breaking when we reset module cache)
from gzip import GzipFile

set_default_module_cache()  # (VERY IMPORTANT)


class TarGZPluginScanner(PluginScanner):
    """Finds and setups up TarGZPlugins.
    These are plugins in a targz file."""

    plugin_dir: Path

    loader: PluginLoader
    metaloader: PluginMetadataLoader
    archiver: PluginArchiver

    def __init__(
        self,
        plugin_dir: Path,
        loader: PluginLoader,
        archiver: PluginArchiver,
    ):
        self.plugin_dir = plugin_dir
        self.loader = loader
        self.metaloader = ArchivePluginMetadataLoader()
        self.archiver = archiver

    def _is_archive_plugin(self, dir: Path) -> bool:
        return dir.is_file() and self.metaloader.contains_meta(dir)

    def _create_plugin(self, src: Path, api_version: ApiVersion) -> Plugin:
        metadata = self.metaloader.load_metadata(src, api_version)

        return Plugin(
            metadata,
            self.metaloader,
            self.loader,
            self.archiver,
            TarGzModuleProvider(Path("")),
            TarGZLoadTimeModuleProvider(Path("")),
            self,
        )

    def get_plugin(self, src: Path, api_version: ApiVersion) -> Plugin | None:
        """Returns a plugin if available at this path"""
        if self._is_archive_plugin(src):
            return self._create_plugin(src, api_version)
        return None

    def get_available_plugins(self, api_version: ApiVersion) -> list[Plugin]:
        output: list[Plugin] = []
        for filename in os.listdir(self.plugin_dir):
            filepath = self.plugin_dir / filename
            if self._is_archive_plugin(filepath):
                output.append(self._create_plugin(filepath, api_version))
        return output


class ArchivePluginMetadataLoader(PluginMetadataLoader):
    """Loads the metadata of targz plugins"""

    def __init__(self):
        pass

    def contains_meta(self, plugin_src: Path) -> bool:
        if not plugin_src.is_file() or not tarfile.is_tarfile(plugin_src):
            return False
        with tarfile.open(plugin_src, "r:gz") as file:
            return "plugin.toml" in file.getnames()

    def load_metadata(
        self, plugin_src: Path, api_version: ApiVersion
    ) -> PluginMetadata:
        data = ""
        if not plugin_src.is_file():
            raise PluginLoadError(
                "Expected a targz plugin archive when loading plugin metadata."
            )

        with tarfile.open(plugin_src, "r:gz") as file:
            dataio = file.extractfile("plugin.toml")
            if dataio is None:
                raise PluginLoadError("Missing `plugin.toml` file")
            data = dataio.read().decode()

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
            dependencies=[
                PluginDependency(
                    dep["plugin_id"], dep["min_version"], dep["max_version"]
                )
                for dep in table.get("dependencies", [])
            ],
            aditional_meta=table,
        )


class TargzPluginArchiver:
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
        includes: list[str] = []
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

        include_dists = []
        seen_dist_names = set()
        for include in get_recursive_includes(includes):
            if include.name in include_dists:
                continue
            seen_dist_names.add(include.name)
            include_dists.append(include)

        final_path = destination / f"{meta.plugin_id}.{self.extension}"

        os.makedirs(destination, exist_ok=True)
        if os.path.exists(final_path):
            os.remove(final_path)

        with tarfile.open(final_path, "x:gz") as output_file:
            self.log("Adding Include Packages:")
            # add files from includes
            for dist in include_dists:
                self.log(f"- {dist.name}=={dist.version}")
                # Add every file into tarfile's site-packages.
                for dist_file in get_distribution_paths(dist):
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


# ==== FileLoaders =====


class TarGzModuleLoader(FileLoader):
    """Loads data from a targz-plugin's module(s)

    see: https://docs.python.org/3/library/importlib.html#importlib.abc.Loader
    """

    tar_file_path: Path
    """Path to the targz file to be opened"""

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

    def load_module(self, fullname: str | None = None) -> ModuleType:
        return importlib._bootstrap._load_module_shim(self, fullname)

    def exec_module(self, module: ModuleType):
        return importlib._bootstrap_external.SourceLoader.exec_module(self, module)


# ===== ModuleProviders ====


class TarGzModuleProvider(PluginModuleProvider):
    """Is able to search for modules inside of a targz containing a `site-packages` folder"""

    sub_path: Path
    """A path inside of the targz to begin searching"""

    def __init__(self, sub_path: Path):
        self.sub_path = sub_path

    def setup_execution_environment(self, module: ModuleType):
        """Used when beginning to execute plugin modules."""
        return super().setup_execution_environment(module)

    def make_module_spec(
        self,
        plugin: Plugin,
        fullname: str,
        file_path: str,
        path: str | None,
        is_package: bool,
    ):
        """Creates a module given the provided information. Replace this function in order
        to change module creation details."""
        return ModuleSpec(
            fullname,
            TarGzModuleLoader(
                fullname,
                file_path,
                plugin.metadata.src_path,
            ),
            origin=path,
            is_package=is_package,
        )

    def find_spec(
        self, plugin: Plugin, fullname: str, path: list[str] | None | str, target=None
    ) -> ModuleSpec | None:
        if isinstance(path, list):
            path = path[0] if len(path) > 0 else None

        return self._find_spec_targz(
            plugin, fullname, path, self.sub_path, target
        ) or self._find_spec_targz(  # Find local modules
            plugin, fullname, path, self.sub_path / "site-packages", target
        )  # if not available, find site-packages

    def _find_spec_targz(
        self,
        plugin: Plugin,
        fullname: str,
        path: str | None,
        sub_path: Path,
        target=None,
    ) -> ModuleSpec | None:
        fullname_path = sub_path / fullname.replace(".", "/")
        text_fullname_path = str(fullname_path).replace("\\", "/")

        if fullname == "":
            spec = self.make_module_spec(
                plugin,
                fullname,
                str(plugin.metadata.src_path / fullname_path),
                path,
                True,
            )

            spec.has_location = True
            return spec

        with tarfile.open(plugin.metadata.src_path, "r:gz") as f:
            names = f.getnames()
            if any(
                Path(name).is_relative_to(fullname_path) for name in names
            ):  # folder found directly

                spec = self.make_module_spec(
                    plugin,
                    fullname,
                    str(plugin.metadata.src_path / fullname_path),
                    path,
                    True,
                )

                spec.has_location = True
            # TODO: Verify correctness
            elif (
                text_fullname_path + ".py"
            ) in names:  # a python file was instead found.
                spec = self.make_module_spec(
                    plugin,
                    fullname,
                    str(plugin.metadata.src_path / (str(fullname_path) + ".py")),
                    path,
                    False,
                )

                spec.has_location = True
            else:
                return None
            return spec


class TarGZLoadTimeModuleProvider(TarGzModuleProvider):
    """Actually in charge of loading individual files inside of a plugin.
    Only Active during plugin loading.
    """

    def make_module_spec(
        self,
        plugin: Plugin,
        fullname: str,
        file_path: str,
        path: str | None,
        is_package: bool,
    ):
        return ModuleSpec(
            fullname,
            TarGzModuleLoader(
                fullname,
                file_path,
                plugin.metadata.src_path,
            ),
            origin=path,
            is_package=is_package,
        )


__all__ = [
    "TarGZPluginScanner",
    "ArchivePluginMetadataLoader",
    "TargzPluginArchiver",
    "TarGzModuleLoader",
    "TarGzModuleProvider",
    "TarGZLoadTimeModuleProvider",
]
