=====================
pytest-astropy-header
=====================

This plugin package provides a way to include information about the system,
Python installation, and select dependencies in the header of the output when
running pytest. It can be used with packages that are not affiliated with the
Astropy project, but is optimized for use with astropy-related projects.

Installation
------------

The ``pytest-astropy-header`` plugin can be installed using ``pip``::

    $ pip install pytest-astropy-header

It is also possible to install the latest development version from the source
repository::

    $ git clone https://github.com/astropy/pytest-astropy-header
    $ cd pytest-astropy-header
    $ pip install .

In either case, the plugin will automatically be registered for use with
``pytest``.

User guide
----------

The plugin provided by this package makes it easy to include a header
with diagnostic information before running the tests, e.g.::

    Running tests in astropy.

    Date: 2019-09-02T23:33:43

    Platform: Darwin-18.7.0-x86_64-i386-64bit

    Executable: /Users/tom/python/dev/bin/python3.7

    Full Python Version:
    3.7.4 (v3.7.4:e09359112e, Jul  8 2019, 14:54:52)
    [Clang 6.0 (clang-600.0.57)]

    encodings: sys: utf-8, locale: UTF-8, filesystem: utf-8
    byteorder: little
    float info: dig: 15, mant_dig: 15

    Package versions:
    numpy: 1.16.4
    scipy: 1.3.0
    matplotlib: 3.1.1
    h5py: 2.9.0
    pandas: 0.24.2
    astropy: 4.0.dev25634

    Using Astropy options: remote_data: none.

The most robust way to enable the plugin in a way that will work regardless of
how the tests are run (e.g. via ``python setup.py test``, ``pytest``, or
``package.test()``) is to add the following to a ``conftest.py`` file that is
inside your package::

    def pytest_configure(config):
        config.option.astropy_header = True


By default, a few packages will be shown, but you may want to customize how the
packages appear. As for enabling the plugin, the most robust way to do this to
be compatible with different astropy versions is via the ``conftest.py`` file::

    from pytest_astropy_header.display import PYTEST_HEADER_MODULES, TESTED_VERSIONS

    def pytest_configure(config):
        config.option.astropy_header = True
        PYTEST_HEADER_MODULES.pop('Pandas')
        PYTEST_HEADER_MODULES['scikit-image'] = 'skimage'

The key to ``PYTEST_HEADER_MODULES`` should be the name that will be displayed
in the header, and the value should be the name of the Python module.

Migrating from the astropy header plugin to pytest-astropy
----------------------------------------------------------

Before the v4.0 release of the core astropy package, the plugin that handles the
header of the testing output described above lived in
``astropy.tests.plugins.display``. A few steps are now needed to update packages
to make sure that only the pytest-astropy version is used instead. These should
be done in addition to the configuration mentioned in the previous section.

First, you should be able to significantly simplify the ``conftest.py`` file by
replacing e.g.::

    from astropy.version import version as astropy_version
    if astropy_version < '3.0':
        # With older versions of Astropy, we actually need to import the pytest
        # plugins themselves in order to make them discoverable by pytest.
        from astropy.tests.pytest_plugins import *
    else:
        # As of Astropy 3.0, the pytest plugins provided by Astropy are
        # automatically made available when Astropy is installed. This means it's
        # not necessary to import them here, but we still need to import global
        # variables that are used for configuration.
        from astropy.tests.plugins.display import (pytest_report_header,
                                                   PYTEST_HEADER_MODULES,
                                                   TESTED_VERSIONS)

    # Customize the following lines to add/remove entries from
    # the list of packages for which version numbers are displayed when running
    # the tests. Making it pass for KeyError is essential in some cases when
    # the package uses other astropy affiliated packages.
    try:
        PYTEST_HEADER_MODULES['Astropy'] = 'astropy'
        del PYTEST_HEADER_MODULES['h5py']
    except KeyError:
        pass

    # This is to figure out the package version, rather than
    # using Astropy's
    from .version import version, astropy_helpers_version

    packagename = os.path.basename(os.path.dirname(__file__))
    TESTED_VERSIONS[packagename] = version
    TESTED_VERSIONS['astropy_helpers'] = astropy_helpers_version

with e.g.::

    import os

    from astropy.version import version as astropy_version
    if astropy_version < '3.0':
        from astropy.tests.pytest_plugins import *
        del pytest_report_header
    else:
        from pytest_astropy_header.display import PYTEST_HEADER_MODULES, TESTED_VERSIONS


    def pytest_configure(config):

        config.option.astropy_header = True

        PYTEST_HEADER_MODULES.pop('Pandas', None)
        PYTEST_HEADER_MODULES['scikit-image'] = 'skimage'

        from .version import version, astropy_helpers_version
        packagename = os.path.basename(os.path.dirname(__file__))
        TESTED_VERSIONS[packagename] = version
        TESTED_VERSIONS['astropy_helpers'] = astropy_helpers_version

Note that while you will need to use a recent version of pytest-astropy for this
to work, it should work with Astropy 2.0 onwards without requiring all the
``try...except`` for imports.

Next check all of your ``conftest.py`` files and be sure to remove the old
plugin from lists such as::

    pytest_plugins = [
      'astropy.tests.plugins.display',
    ]

Development Status
------------------

Questions, bug reports, and feature requests can be submitted on `github`_.

.. _github: https://github.com/astropy/pytest-astropy

License
-------

This package is licensed under a 3-clause BSD style license - see the
``LICENSE.rst`` file.
