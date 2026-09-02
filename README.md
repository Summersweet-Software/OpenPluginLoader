# Open Plugin Loader

An MIT LICENSE library made to make packaging and loading of plugins easy for projects.

OPL is not going to help you make your plugin api itself, but it will make your experience loading plugins much easier. It also will make the experience of your users significantly easier as well by standardizing plugin packaging. Multiple of your projects can use the same plugin packaging strategy and thus users will not be required to relearn anything for each of your projects.

## Features

- Packaging plugins into an archive (targz) with their pypi dependencies pre-packaged
- Plugin sorting/dependency sorting. Ensures that plugins will be loaded in the correct order.
- Plugin import hook to allow plugins to depend on each other.
- Customization of plugin loading- choose to load them via dynamic import (default) or use a custom loading strategy (for example, a custom, sandboxed environment).
- Plugin api versioning. Ensure plugins follow versioning standards
- Plugin Manager using the strategy pattern. Change any individual component to suite your needs.

## Features Not Provided
- Sandboxed loading strategy. Sandbox security is not our expertise. I would rather we provide only what we can reasonable ensure the quality of.

## Planned Features
- [ ] Plugin Signing

# Getting Started: Making a Plugin (Default Strategy):

Making a plugin is fairly simple. A plugin has a few basic parts:
- A `pyproject.toml` (optional)
- A `plugin.toml`
- A plugin entry point (default `__init__.py`, can be modified in your `plugin.toml`)

## pyproject.toml configuration options

All configuration options are listed below.

```toml
# Your full pyproject
# ...
[tool.plugin]
includes = ["mypy"] # package includes. A list of strings. ONLY USE PACKAGE NAMES, NOT VERSIONS OR SPECIFIERS.
# It will use the version it finds first in your package search order.
# `includes` get added into a packaged plugin in a `site-packages` folder.

src="src/" # source directory (a string). Lets you have slightly more control over plugin packaging.

# More options can be added by custom plugin loaders (obviously), so keep that in mind.
```

## plugin.toml configuration options

Your `plugin.toml` contains plugin specific information and WILL be packaged in your final plugin.

```toml
# Can and will be changed by custom plugin loaders
name = "ExamplePlugin"
author = "Abby"
entry = "main" # Entry file
version = "1.0" # plugin version

min_api_version = "0.1.0"
max_api_version = "0.1.10"

# versions can be formated as follows:
# - string: "major.minor[.<patch>[-<tag>]]"
# - table: {major=1, minor=0, patch=0, tag="Beta"}
# - list/tuple: [1, 0, 0, "beta"], [1, 0], [1, 0, 0]


# (Optional from here on)
dependencies = [
    {plugin_id="author.name", min_version="0.1.0", max_version="0.1.0"},
    # ... more dependencies
]

# you can add as much additional data as you want.
# It will get saved under "aditional_meta" in `PluginMetadata`
```

## main.py (our entry in this example)
```
# Whatever you want here!

print("Holy moly, we loaded it!")
```


## Final structure

Here is the final file structure of our plugin

```
exampleplugin/
├── .venv/ # our virtual environment during development
│   └── ...
├── .git/
│   └── ...
├── src/
│   ├── main.py
│   └── plugin.toml
├── pyproject.toml
├── # misc
├── README.md
├── .gitignore
└── uv.lock
```


> [!TIP]
> When we lay it out like this, its easy to see why we should modify the `src` option
> in our `pyproject.toml`

## Packaging Our Plugin:
This heavily depends on your loading strategy, but there is a generic command provided.
It uses the default strategy.

```sh
uv run build-plugin ./ ./build
#                   ^     ^ 
#                   |     | - build/output directory
#                   |
#                   | - src directory (gets modified if a pyproject is present in that folder)
```

### Alternatively: We Can Make a Build Script.
This should mostly be provided by the plugin api you are using or create, but for testing we can also just build out our own.

```python
plugin_api_version = ApiVersion(1, 0, None, None)

src = Path("./")
dest = src / "build"

meta_loader = DefaultMetadataLoader() # loads the metadata for our plugin
archiver = DefaultPluginArchiver()

# load our metadata and archive our plugin
meta = meta_loader.load_metadata(src, plugin_api_version)
archiver.archive_plugin(meta, src, dest)
```

# Getting Started: Loading plugins (Default Strategy):

### Project structure
```
ourproject/
├── .venv/ # our virtual environment during development
│   └── ...
├── .git/
│   └── ...
├── plugins/
│   └── Abby.ExamplePlugin.tar.gz # our example plugin!
├── src/
│   ├── ourproject/ # plugin api
│   │   └── ...
│   └── main.py # Our application
├── pyproject.toml
├── README.md
├── .gitignore
└── uv.lock
```

## Loading plugins

Loading plugins is actually fairly easy (assuming you are okay with the defaults).

```python
from openpluginloader.defaultstrategy import create_default_manager
from openpluginloader.versioning import ApiVersion
from openpluginloader.utility import set_default_module_cache

from pathlib import Path

import ourproject # import our api. 

# makes our current imports available to plugins. VERY IMPORTANT
set_default_module_cache()
# You can also manually set `utility.DEFAULT_MODS` if you want more careful control
# ONLY MODIFY DEFAULT_MODS, DO NOT INSTANTIATE A NEW DICT! THIS WILL BREAK THINGS!

API_VERSION = ApiVersion(1, 0, 0, None)

manager = create_default_manager(API_VERSION, Path("plugins/"))
manager.initialize_hooks() # initialize very important import hooks

plugins = manager.discover_plugins() # discovers plugins and sorts them.
manager.load_all_plugins()
```

## Loading individual plugins:
```python
from openpluginloader.defaultstrategy import create_default_manager
from openpluginloader.versioning import ApiVersion
from openpluginloader.utility import set_default_module_cache

from pathlib import Path

import ourproject # import our api. 

# makes our current imports available to plugins. VERY IMPORTANT
set_default_module_cache()
# You can also manually set `utility.DEFAULT_MODS` if you want more careful control
# ONLY MODIFY DEFAULT_MODS, DO NOT INSTANTIATE A NEW DICT! THIS WILL BREAK THINGS!

API_VERSION = ApiVersion(1, 0, 0, None)

manager = create_default_manager(API_VERSION, Path("plugins/"))
manager.initialize_hooks() # initialize very important import hooks

plugins = manager.discover_plugins() # discovers plugins and sorts them.

import plugins.ExamplePlugin # imports `__init__.py` from our ExamplePlugin
# alternatively
import plugins.ExamplePlugin.__ENTRY__ # imports a plugin's entry point (defined in plugin.toml)
# alternatively again
import plugins.ExamplePlugin.main # import a specific module from ExamplePlugin
```

> [!IMPORTANT]
> Plugins can use these fancy plugin imports too! Keep that in mind!
> You can also make your LSP hate you less by adding a `plugins-stubs` and setting up
> mypy stubs in your `pyproject.toml`.

#### Side Note:

My account (ArachnidAbby) has an old package called "OpenPluginApi". Although that project has inspired me to make this, I would NOT recommend using it. I wrote it when I was around 14. It is not very useful or good. It is not meant to be used with this project.
