# Open Plugin Loader

An MIT LICENSE library made to make packaging and loading of plugins easy for projects.

OPL is not going to help you make your plugin api itself, but it will make your experience loading plugins much easier. It also will make the experience of your users significantly easier as well by standardizing plugin packaging. Multiple of your projects can use the same plugin packaging strategy and thus users will not be required to relearn anything for each of your projects.

## Features

- Packaging plugins into a archive (targz) with their pypi dependencies pre-packaged
- Plugin sorting/dependency sorting. Ensures that plugins will be loaded in the "correct" order.
- Plugin import hook to allow plugins to depend on each other.
- Customization of plugin loading- choose to load them via dynamic import (default) or use a custom loading strategy (for example, a custom, sandboxed environment).
- Plugin api versioning. Ensure plugins follow versioning standards

#### Side Note:

My account (ArachnidAbby) has an old package called "OpenPluginApi". Although that project has inspired me to make this, I would NOT recommend using it. I wrote it when I was around 14. It is not very useful or good. It is not meant to be used with this project.
