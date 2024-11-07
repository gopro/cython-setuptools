from pathlib import Path

from cython_setuptools.pyproject import CythonSetuptoolsOptions, read_cython_setuptools_option

DATA_DIR = Path(__file__).parent / "data"


def test_basic():
    pyproject = DATA_DIR / "basic_pyproject.toml"
    extensions = read_cython_setuptools_option(pyproject)
    assert extensions["lol"].sources == ["a.pyx"]
    assert extensions["lol"].langage == "c"
    assert extensions["lol"].cpp_std == 17


def test_all_fields():
    pyproject = DATA_DIR / "all_fields_pyproject.toml"
    extensions = read_cython_setuptools_option(pyproject)
    expected = CythonSetuptoolsOptions(
        sources=["a.pyx"],
        libraries=["a", "b"],
        include_dirs=["toto/include"],
        library_dirs=["toto/lib", "/usr/lib"],
        extra_compile_args=["-g"],
        extra_link_args=["--strip-debug"],
        langage="c++",
        cpp_std=23,
        pkg_config_packages=["super_lib"],
        pkg_config_dirs=["toto/lib/pkgconfig"],
    )
    assert extensions["lol"] == expected


def test_multiples():
    pyproject = DATA_DIR / "multiple_extention_pyproject.toml"
    extensions = read_cython_setuptools_option(pyproject)
    assert extensions["reblochon"].sources == ["reblochon.pyx"]
    assert extensions["croissant"].sources == ["croissant.pyx"]
