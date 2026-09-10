.. OpenPluginLoader documentation master file, created by
   sphinx-quickstart on Wed Sep  9 21:27:34 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OpenPluginLoader
=================

OpenPluginLoader is a general purpose plugin loading library for applications built in python.
It's default plugin loader provides complex dependency management which many application plugin loaders
might not include on their own. It also provides a level of isolation from project files that can be helpful in ensuring
your api is the only thing getting exposed to plugins.

The purpose of OpenPluginLoader is to provide a simple, open standard for loading plugins
to create a community around plugin archiving and loading. This makes plugin loaders
able to be more wide-spread and to be of higher qualities for project maintainers as well as
plugin developers. This is why its called *Open* PluginLoader. Its also why **the library is fully MIT licensed.**


Modularity
************

OpenPluginLoader is built using the *strategy pattern*. This allows each part to be interchangable/modular.
This makes it extremely easy to pick and chose how you want to load plugins while still not rewriting the entire
library yourself.

For example:
#############

You can switch out the default MetadataLoader without breaking the rest of the plugin loading.
(For example if you wanted to use a :code:`plugin.json` file instead of a :code:`plugin.toml`)


Pypi Dependency Management
****************************

OPL allows plugins to include their own copies of their pypi/package dependencies. Sub-dependencies will also be found
via the use of the `Packaging library <https://pypi.org/project/packaging/>`_. This is extremely helpful and makes plugins
more useful in most applications.

For Example
#############

Lets say you have a business management application with a plugin system (using OPL).
If someone wants to add a plugin to take pictures of reciepts to scan into the app then they might need OpenCV.
This dependency include could be very messy to include because most plugin loaders don't have a good mechanism for
*packaging* plugins. OPL includes a plugin packaging system that allows you to include pypi dependencies in the final
:code:`plugin.tar.gz` file. They can easily be added to the :code:`tool.plugin.include` list in a plugin's :code:`pyproject.toml` file.

Plugin Dependency Management
******************************

Plugins can also declare a list of plugin dependencies. These each have a minimum and maximum versions. Modifying the MetadataLoader will give you
the ability to set defaults or to only require one instead of both of these options.

Dependencies are used during load order sorting (via a topological sort) to ensure plugins are loaded in the correct order.

Features Not Provided Out-Of-The-Box
**************************************

Out of the box, **OPL Does Not Provide Sandboxing**. This is important to note. Sandboxing is difficult and
`Summersweet-Software <https://summersweet.software>`_ does not want to be responsible for ensuring this level of security. If our team ever gets a security expert,
then we will be sure to include it.

Documentation Quality
***********************

All documentation is hand-written. This means there are more useful tips within the docs themselves,
but it does also mean to possibility for more spelling errors or small typos in api functions/classes/modules/etc.


Summersweet Software
**********************

Summersweet software is a workers cooperative built on the idea of bringing power back to the people.
We want software to be something that doesn't exploit but rather empowers developers and users alike.
This is why this library is released for free.

That being said, we would appreciate your support by `following us on github <https://github.com/Summersweet-Software>`_
or `starring this repository <https://github.com/Summersweet-Software/OpenPluginLoader>`_. And, if you have the cash to spare
and want to support us, you can use github sponsors to give us money.

Regardless, we will keep pushing out open-source libraries and software. We will release components for our closed-source
products too. Thats actually why OPL exists today!

.. Hidden TOCs

.. toctree::
    :glob:
    :caption: OpenPluginLoader
    :hidden:

    self

.. toctree::
    :glob:
    :maxdepth: 2
    :caption: api-reference
    :hidden:


    api_docs/utility.rst
    api_docs/pluginmetadata.rst
    api_docs/apiversion.rst
    api_docs/manager.rst
    api_docs/loader.rst
    api_docs/pluginscanner.rst
    api_docs/pluginarchiving.rst


.. toctree::
    :glob:
    :maxdepth: 2
    :caption: default-strategy
    :hidden:

    default_strategy/index.rst
    default_strategy/basics.rst
    default_strategy/import_hooks.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`