from pathlib import Path

from cython_setuptools.extentions import create_extensions
from cython_setuptools.pyproject import CythonSetuptoolsOptions, read_cython_setuptools_option

DATA_DIR = Path(__file__).parent / "data"


def test_library_dirs_reach_extension(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[cython_extensions.example]\n'
        'sources = ["example.c"]\n'
        'libraries = ["custom"]\n'
        'library_dirs = ["vendor/lib", "other/lib"]\n'
    )
    extensions = create_extensions(str(tmp_path / "setup.py"), cythonize=False)
    assert len(extensions) == 1
    assert extensions[0].library_dirs == ["vendor/lib", "other/lib"]
    assert extensions[0].libraries == ["custom"]


def test_basic():
    pyproject = DATA_DIR / "basic_pyproject.toml"
    extensions = read_cython_setuptools_option(pyproject)
    assert extensions["lol"].sources == ["a.pyx"]
    assert extensions["lol"].language == "c"
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
        language="c++",
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
