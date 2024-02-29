# History

## 0.3.3
- bump integration test to using Python3 instead Python2

- bump base tox python to 3.10

- bump gitactions checkout and setup-python versions

- fix warning: 'cpp_std', 'tags' warnings.warn(msg)

## 0.3.2
- github-action: rename cicd_test.yml to tests.yml

## 0.3.1
- github-action: fix test branch to main


## 0.3.0

- Update README.md.
- Honor black.
- Refactored tests.
- Added new cpp_std flag to specify the c++ standard version.
- Refactored python package architecture to use a single version of
  vendor.py as setup for the the required modules to build the bindings.
- Removed CLI commands.
- Added the original setup __file__ argument to setup to pass the current
  working directory.
- Resolve config parser deprecations.
- Migration from setup.py to pyproject.toml.
- Added automatic git versioning system
- Enhance tox.ini tests.
- Added git-actions on pull request and push on master
  - Platform: [Unix, Darwin, Windows]
  - Python versions: [3.7, 3.8, 3.9, 3.10, 3.11]
- Removed Makefile.
- Removed travis.yml.

## 0.2.3

- extract_args() handles missing args.

## 0.2.2

- pkg-config -L, -l and -I flags are extracted and put in modules'
  library_dirs, libraries and include_dirs respectively.

## 0.2.1

- Use Cython's cythonize() instead of deprecated build_ext.
- Python 3 unicode fix.
- Defaults section extra fields are now merged in module dicts.

## 0.2

- Unrecognized fields are also included in `parse_setup_cfg()`'s module dicts.

## 0.1

- First public release.
