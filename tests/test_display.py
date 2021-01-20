import pytest
import numpy

NUMPY_VERSION = numpy.__version__

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
    testdir.inline_run()
    out, err = capsys.readouterr()
    assert 'Package versions:' not in out


@pytest.mark.parametrize('method', ['cli', 'ini', 'conftest'])
def test_enabled(testdir, capsys, method):
    if method == 'cli':
        testdir.inline_run("--astropy-header")
    elif method == 'ini':
        testdir.makeini("""
            [pytest]
            astropy_header = yes
        """)
        testdir.inline_run()
    elif method == 'conftest':
        testdir.makeconftest("""
            def pytest_configure(config):
                config.option.astropy_header = True
        """)
        testdir.inline_run()
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 5
    assert lines[0].startswith('Numpy: ')
    assert lines[1].startswith('Scipy: ')
    assert lines[2].startswith('Matplotlib: ')
    assert lines[3].startswith('h5py: ')
    assert lines[4].startswith('Pandas: ')


@pytest.mark.parametrize('method', ['ini', 'conftest'])
def test_explicit_disable(testdir, capsys, method):
    if method == 'ini':
        testdir.makeini("""
            [pytest]
            astropy_header = no
        """)
        testdir.inline_run()
    elif method == 'conftest':
        testdir.makeconftest("""
            def pytest_configure(config):
                config.option.astropy_header = False
        """)
    testdir.inline_run()
    out, err = capsys.readouterr()
    assert 'Package versions:' not in out


@pytest.mark.parametrize('method', ['cli', 'ini', 'ini_list', 'conftest'])
def test_override_package_single(testdir, capsys, method):
    if method == 'cli':
        testdir.inline_run("--astropy-header", "--astropy-header-packages=numpy")
    elif method == 'ini':
        testdir.makeini("""
            [pytest]
            astropy_header = yes
            astropy_header_packages = numpy
        """)
        testdir.inline_run()
    elif method == 'ini_list':
        testdir.makeini("""
            [pytest]
            astropy_header = yes
            astropy_header_packages =
                numpy
        """)
        testdir.inline_run()
    elif method == 'conftest':
        testdir.makeconftest("""
            def pytest_configure(config):
                config.option.astropy_header = True
                config.option.astropy_header_packages = ['numpy']
        """)
        testdir.inline_run()
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 1
    assert lines[0] == f'numpy: {NUMPY_VERSION}'


@pytest.mark.parametrize('method', ['cli', 'ini', 'ini_list', 'conftest'])
def test_override_package_multiple(testdir, capsys, method):
    if method == 'cli':
        testdir.inline_run("--astropy-header", "--astropy-header-packages=numpy,pandas")
    elif method == 'ini':
        testdir.makeini("""
            [pytest]
            astropy_header = yes
            astropy_header_packages = numpy, pandas
        """)
        testdir.inline_run()
    elif method == 'ini_list':
        testdir.makeini("""
            [pytest]
            astropy_header = yes
            astropy_header_packages =
                numpy
                pandas
        """)
        testdir.inline_run()
    elif method == 'conftest':
        testdir.makeconftest("""
            def pytest_configure(config):
                config.option.astropy_header = True
                config.option.astropy_header_packages = ['numpy', 'pandas']
        """)
        testdir.inline_run()
    out, err = capsys.readouterr()
    print(out)
    lines = extract_package_version_lines(out)
    assert len(lines) == 2
    assert lines[0] == f'numpy: {NUMPY_VERSION}'
    assert lines[1].startswith('pandas')


@pytest.mark.parametrize('method', ['cli', 'ini', 'ini_list', 'conftest'])
def test_nonexistent(testdir, capsys, method):
    if method == 'cli':
        testdir.inline_run("--astropy-header", "--astropy-header-packages=apackagethatdoesnotexist")
    elif method == 'ini':
        testdir.makeini("""
            [pytest]
            astropy_header = yes
            astropy_header_packages = apackagethatdoesnotexist
        """)
        testdir.inline_run()
    elif method == 'ini_list':
        testdir.makeini("""
            [pytest]
            astropy_header = yes
            astropy_header_packages =
                apackagethatdoesnotexist
        """)
        testdir.inline_run()
    elif method == 'conftest':
        testdir.makeconftest("""
            def pytest_configure(config):
                config.option.astropy_header = True
                config.option.astropy_header_packages = ['apackagethatdoesnotexist']
        """)
        testdir.inline_run()
    out, err = capsys.readouterr()
    lines = extract_package_version_lines(out)
    assert len(lines) == 1
    assert lines[0] == 'apackagethatdoesnotexist: not available'


def test_modify_in_conftest(testdir, capsys):
    testdir.makeconftest("""
    from pytest_astropy_header.display import PYTEST_HEADER_MODULES, TESTED_VERSIONS

    def pytest_configure(config):
        config.option.astropy_header = True
        PYTEST_HEADER_MODULES.pop('Pandas')
        PYTEST_HEADER_MODULES['scikit-image'] = 'skimage'
        TESTED_VERSIONS['fakepackage'] = '1.0.2'
    """)
    testdir.inline_run()
    out, err = capsys.readouterr()
    assert err == ''
    lines = extract_package_version_lines(out)
    assert len(lines) == 5
    assert lines[0].startswith('Numpy: ')
    assert lines[1].startswith('Scipy: ')
    assert lines[2].startswith('Matplotlib: ')
    assert lines[3].startswith('h5py: ')
    assert lines[4].startswith('scikit-image: ')
    assert 'Running tests with fakepackage version 1.0.2' in out
