"""
Encapsulate the retrieval of information from the pyproject.toml
"""

import os
from typing import Any

from serde import field, serde
from serde.toml import from_toml


@serde
class CythonSetuptoolsOptions:
    """
    All cython setuptools option that can be in the pyproject.toml

    Attributes:
        sources: The list of Cython and C/C++ source files that are compiled to build the module.
        libraries: A list of libraries to link with the module.
        include_dirs: A list of directories to find include files.
        library_dirs: A list of directories to find libraries.
        extra_compile_args: Extra arguments passed to the compiler.
        extra_link_args: Extra arguments passed to the linker.
        language: Typically "c" or "c++".
        cpp_std: Typically "11", "14", "17" or "20".
        pkg_config_packages: A list of `pkg-config` package names to link with the module.
        pkg_config_dirs:
            A list of directories to add to the pkg-config search paths
            (extends the `PKG_CONFIG_PATH` environment variable).
    """
    sources: list[str]
    libraries: list[str] = field(default_factory=list)
    include_dirs: list[str] = field(default_factory=list)
    library_dirs: list[str] = field(default_factory=list)
    extra_compile_args: list[str] = field(default_factory=list)
    extra_link_args: list[str] = field(default_factory=list)
    langage: str = "c"
    cpp_std: int = 17
    pkg_config_packages: list[str] = field(default_factory=list)
    pkg_config_dirs: list[str] = field(default_factory=list)

    def to_extension_kwargs(self) -> dict[str, Any]:
        """
        Helper function to return a dict that can be used to create an Extension
        Note that before using this function, fields like ``cpp_std`` or ``pkg_config_packages``
        should be used to fill extra elements in ``extra_compile_args`` and ``extra_link_args``

        Returns:
            A dict with the fields ``sources``, ``libraries``, ``include_dirs``, ``extra_compile_args``, ``extra_link_args``
        """
        return {
            "sources": self.sources,
            "libraries": self.libraries,
            "include_dirs": self.include_dirs,
            "extra_compile_args": self.extra_compile_args,
            "extra_link_args": self.extra_link_args,
        }


@serde
class _PyProject:
    cython_extensions: dict[str, CythonSetuptoolsOptions]


def _read_cython_setuptools_option_from_string(pyproject_content: str) -> dict[str, CythonSetuptoolsOptions]:
    return from_toml(_PyProject, pyproject_content).cython_extensions


def read_cython_setuptools_option(pyproject_path: os.PathLike) -> dict[str, CythonSetuptoolsOptions]:
    """
    Read the pyproject.toml and return cython setup tools options

    Args:
        pyproject_path: path to the pyproject.toml eg: 'toto/pyproject.toml'

    Returns:
        A dict where they key is the name of the extension and the value is the options
    """
    with open(pyproject_path, encoding="utf-8") as f:
        toml = f.read()
    return _read_cython_setuptools_option_from_string(toml)
