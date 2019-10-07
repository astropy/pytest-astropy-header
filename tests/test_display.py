import pytest

import numpy
import pandas
import skimage

NUMPY_VERSION = numpy.__version__
PANDAS_VERSION = pandas.__version__
SKIMAGE_VERSION = skimage.__version__

pytest_plugins = ['pytester']


def extract_package_version_lines(output):
    lines = []
    in_section = False
    for line in output.splitlines():
        if line.strip() == 'Package versions:':
            in_section = True
        elif in_section:
            if line.strip() == "":
                break
            else:
                lines.append(line)
    return lines


def test_default(testdir, capsys):
    testdir.makeini("""
                    [pytest]
                    """)
    testdir.inline_run("--astropy-header")
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 6
    assert lines[0].startswith('numpy: ')
    assert lines[1].startswith('scipy: ')
    assert lines[2].startswith('matplotlib: ')
    assert lines[3].startswith('h5py: ')
    assert lines[4].startswith('pandas: ')
    assert lines[5].startswith('astropy: ')


def test_single(testdir, capsys):
    testdir.makeini("""
                    [pytest]
                    astropy_header_packages = numpy
                    """)
    testdir.inline_run("--astropy-header")
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 2
    assert lines[0] == f'numpy: {NUMPY_VERSION}'
    assert lines[1].startswith('astropy: ')


def test_single_item_list(testdir, capsys):
    testdir.makeini("""
                    [pytest]
                    astropy_header_packages =
                        numpy
                    """)
    testdir.inline_run("--astropy-header")
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 2
    assert lines[0] == f'numpy: {NUMPY_VERSION}'
    assert lines[1].startswith('astropy: ')


def test_multiple_comma(testdir, capsys):
    testdir.makeini("""
                    [pytest]
                    astropy_header_packages = numpy, pandas
                    """)
    testdir.inline_run("--astropy-header")
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 3
    assert lines[0] == f'numpy: {NUMPY_VERSION}'
    assert lines[1] == f'pandas: {PANDAS_VERSION}'
    assert lines[2].startswith('astropy: ')


def test_multiple_list(testdir, capsys):
    testdir.makeini("""
                    [pytest]
                    astropy_header_packages =
                        numpy
                        pandas
                    """)
    testdir.inline_run("--astropy-header")
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 3
    assert lines[0] == f'numpy: {NUMPY_VERSION}'
    assert lines[1] == f'pandas: {PANDAS_VERSION}'
    assert lines[2].startswith('astropy: ')


def test_nonexistent(testdir, capsys):
    testdir.makeini("""
                    [pytest]
                    astropy_header_packages = apackagethatdoesnotexist
                    """)
    testdir.inline_run("--astropy-header")
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 2
    assert lines[0] == f'apackagethatdoesnotexist: not available'
    assert lines[1].startswith('astropy: ')


def test_hyphen(testdir, capsys):
    # This is to check that what needs to be passed are package names,
    # not module names.
    testdir.makeini("""
                    [pytest]
                    astropy_header_packages = scikit-image
                    """)
    testdir.inline_run("--astropy-header")
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 2
    assert lines[0] == f'scikit-image: {SKIMAGE_VERSION}'
    assert lines[1].startswith('astropy: ')
