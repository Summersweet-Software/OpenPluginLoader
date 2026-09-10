Default Strategy
==================

The purpose of the default strategy is to provide a baseline for plugin loading.

Supported plugin types/formats include:
- Folder Plugin's (a folder with a :code:`plugin.toml`)
- Archive Plugins (a targz containing a :code:`plugin.toml`)

Each part/strategy included in this module is reusable. Each part will be documented in depth to ensure
writers of bispoke plugin loaders do not have to create duplicates of functionality already provided to them.