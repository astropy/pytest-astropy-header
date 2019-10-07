# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This plugin provides customization of the header displayed by pytest for
reporting purposes.
"""

import os
import sys
import datetime
import locale
from pkg_resources import working_set
from setuptools.config import read_configuration

DEFAULT_PACKAGES = ['numpy', 'scipy', 'matplotlib', 'h5py', 'pandas']


def pytest_addoption(parser):
    group = parser.getgroup("astropy header options")
    group.addoption('--astropy-header', action='store_true',
                    help="Show the pytest-astropy header")
    parser.addini('astropy_header', default=False,
                  help="whether to show the pytest-astropy header")
    parser.addini('astropy_header_packages', type='linelist',
                  help="comma-separated list of packages to include in the header")


def pytest_report_header(config):

    if not config.getoption('--astropy-header') and not config.getini("astropy_header"):
        return

    # Determine package name
    package_name = None
    if os.path.exists('setup.cfg'):
        setup_cfg = read_configuration('setup.cfg')
        if 'metadata' in setup_cfg and 'name' in setup_cfg['metadata']:
            package_name = setup_cfg['metadata']['name']

    packages = config.getini("astropy_header_packages")

    if len(packages) == 0:
        packages = DEFAULT_PACKAGES
    elif len(packages) == 1 and ',' in packages[0]:
        packages = [pkg.strip() for pkg in packages[0].split(',')]

    if package_name is not None and package_name not in packages:
        packages.append(package_name)

    if 'astropy' not in packages:
        packages.append('astropy')

    try:
        stdoutencoding = sys.stdout.encoding or 'ascii'
    except AttributeError:
        stdoutencoding = 'ascii'

    args = config.args

    # Per https://github.com/astropy/astropy/pull/4204, strip the rootdir from
    # each directory argument
    if hasattr(config, 'rootdir'):
        rootdir = str(config.rootdir)
        if not rootdir.endswith(os.sep):
            rootdir += os.sep

        dirs = [arg[len(rootdir):] if arg.startswith(rootdir) else arg
                for arg in args]
    else:
        dirs = args

    s = "Running tests in {}.\n\n".format(" ".join(dirs))

    s += "Date: {}\n\n".format(datetime.datetime.now().isoformat()[:19])

    from platform import platform
    plat = platform()
    if isinstance(plat, bytes):
        plat = plat.decode(stdoutencoding, 'replace')
    s += f"Platform: {plat}\n\n"
    s += f"Executable: {sys.executable}\n\n"
    s += f"Full Python Version: \n{sys.version}\n\n"

    s += "encodings: sys: {}, locale: {}, filesystem: {}".format(
        sys.getdefaultencoding(),
        locale.getpreferredencoding(),
        sys.getfilesystemencoding())
    s += '\n'

    s += f"byteorder: {sys.byteorder}\n"
    s += "float info: dig: {0.dig}, mant_dig: {0.dig}\n\n".format(
        sys.float_info)

    s += f"Package versions: \n"

    for package_name in packages:
        if package_name in working_set.by_key:
            req_pkg = working_set.by_key[package_name]
            version = req_pkg.version
        else:
            version = 'not available'
        s += f"{package_name}: {version}\n"

    s += f"\n"

    special_opts = ["remote_data", "pep8"]
    opts = []
    for op in special_opts:
        op_value = getattr(config.option, op, None)
        if op_value:
            if isinstance(op_value, str):
                op = ': '.join((op, op_value))
            opts.append(op)
    if opts:
        s += "Using Astropy options: {}.\n".format(", ".join(opts))

    return s


def pytest_terminal_summary(terminalreporter):
    """Output a warning to IPython users in case any tests failed."""

    try:
        get_ipython()
    except NameError:
        return

    if not terminalreporter.stats.get('failed'):
        # Only issue the warning when there are actually failures
        return

    terminalreporter.ensure_newline()
    terminalreporter.write_line(
        'Some tests are known to fail when run from the IPython prompt; '
        'especially, but not limited to tests involving logging and warning '
        'handling.  Unless you are certain as to the cause of the failure, '
        'please check that the failure occurs outside IPython as well.  See '
        'http://docs.astropy.org/en/stable/known_issues.html#failing-logging-'
        'tests-when-running-the-tests-in-ipython for more information.',
        yellow=True, bold=True)
