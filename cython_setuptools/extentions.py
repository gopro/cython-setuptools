import os
from pathlib import Path

import Cython
import Cython.Build
import Cython.Distutils
# Distutils is deprecated but for the moment this is the only way the default compiler is exposed when using setuptools
from setuptools._distutils.ccompiler import get_default_compiler

from .pyproject import CythonSetuptoolsOptions, read_cython_setuptools_option
from .pkgconfig_wrapper import get_flags
from .common import C_EXT, CPP_EXT, CYTHON_EXT, convert_to_bool, get_cpp_std_flag


def create_extensions(original_setup_file: str, cythonize: bool = True) -> list:
    """
    Create a list of extentions to be used as argument ``ext_modules`` of ``setuptools.setup()`` by reading the ``pyproject.toml``

    To compile pyx into .c/.cpp set ``CYTHONIZE`` env variable to True or if it is not set use the cythonize of this function
    To get debug symboles ``DEBUG`` env variable (does not work with msvc)
    To enable profiling use ``PROFILE_CYTHON`` env variable

    Example of a what can be added to a ``pyproject.toml`` to have an extension named ``lol``:
    ```
        [cython_extensions.lol]
        # The list of Cython and C/C++ source files that are compiled to build the module.
        sources = ["a.pyx"]
        # A list of libraries to link with the module.
        libraries = ["a", "b"]
        # A list of directories to find include files.
        include_dirs = ["toto/include"]
        # A list of directories to find libraries.
        library_dirs = ["toto/lib", "/usr/lib"]
        # Extra arguments passed to the compiler.
        extra_compile_args = ["-g"]
        # Extra arguments passed to the linker.
        extra_link_args = ["--strip-debug"]
        # Typically "c" or "c++".
        language = "c++"
        # Typically "11", "14", "17" or "20".
        cpp_std = 23
        # A list of `pkg-config` package names to link with the module.
        pkg_config_packages = ["super_lib"]
        # A list of directories to add to the pkg-config search paths (extends the `PKG_CONFIG_PATH` environment variable).
        pkg_config_dirs = ["toto/lib/pkgconfig"]
    ```

    Args:
        original_setup_file:
            Location of the ``setup.py`` calling this file.
            It is used to retrieve the location of the ``pyproject.toml`` (that should be in the same directory)
            It is recommanded to just use ``__file__``
        cythonize:
            If True ``Cython.Build.cythonize`` will be called
            It is overrided by the env variable ``CYTHONIZE``

    Returns:
        A list Extentions, It can be safely used for ``ext_modules`` argument of ``setuptools.setup()``
    """
    extensions_options = read_cython_setuptools_option(Path(original_setup_file).parent / "pyproject.toml")
    extensions = []
    cythonize = convert_to_bool(os.environ.get("CYTHONIZE", cythonize))
    profile_cython = convert_to_bool(os.environ.get("PROFILE_CYTHON", False))
    debug = convert_to_bool(os.environ.get("DEBUG", False))
    for name, options in extensions_options.items():
        _complete_cython_options(options, debug, cythonize)
        extensions.append(_create_extension(name, options, profile_cython))
    if cythonize:
        extensions = Cython.Build.cythonize(extensions, force=True)
    return extensions


def _complete_cython_options(options: CythonSetuptoolsOptions, debug: bool, cythonize: bool):
    if debug and get_default_compiler() != "msvc":
        options.extra_compile_args.append("-g")
    if options.language == "c++":
        options.extra_compile_args.append(get_cpp_std_flag(options.cpp_std))

    # Get flags from pkg-config dependencies
    build_flags = get_flags(options.pkg_config_packages, options.pkg_config_dirs)
    options.extra_compile_args += build_flags.compile_flags
    options.extra_link_args += build_flags.link_flags

    # Force to use already generated .c/.cpp files if cythonize is False
    if not cythonize:
        new_ext = CPP_EXT if options.language == "c++" else C_EXT
        new_sources = []
        for source in options.sources:
            source_path = Path(source)
            if source_path.suffix == CYTHON_EXT:
                source = str(source_path.with_suffix(new_ext))
            new_sources.append(source)
        options.sources = new_sources


def _create_extension(name: str, options: CythonSetuptoolsOptions, profile_cython: bool) -> Cython.Distutils.Extension:
    cython_directives = {"profile": True} if profile_cython else {}
    return Cython.Distutils.Extension(name=name, cython_directives=cython_directives, **options.to_extension_kwargs())
