0.2.3 (unreleased)
==================

0.2.2 (2022-09-06)
==================

- The plugin is now aware of the ``run_slow`` and ``run_hugemem`` options
  introduced in ``pytest-astropy`` version 0.10.0. [#48]

0.2.1 (2022-03-09)
==================

- Fixed compatibility with ``astropy``. [#43]

0.2.0 (2021-12-27)
==================

- Suppressed ``PytestAssertRewriteWarning``. [#4]

- Do not show astropy-helpers version in packages that don't use it. [#16]

- Removed compatibility code for ``astropy`` < 4.0, and for ``astropy-helpers``. [#32]

- Removed ``astropy`` dependency. [#19, #34]

- Bumped minimum supported Python version to 3.7 and various infrastructure updates. [#23, #39]

0.1.2 (2019-12-18)
==================

- Handle the case where the astropy version is 'unknown'. [#11]

- Fix declaration of test dependencies. [#9]

0.1.1 (2019-10-25)
==================

- Make plugin not crash if astropy is not installed. [#1]

0.1 (2019-10-25)
================

- Initial release.
