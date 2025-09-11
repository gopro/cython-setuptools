import hashlib
import os
from pathlib import Path
import re

import Cython
import Cython.Build
import Cython.Distutils
# Distutils is deprecated but for the moment this is the only way the default compiler is exposed when using setuptools
from setuptools._distutils.ccompiler import get_default_compiler

from .pyproject import CythonSetuptoolsOptions, read_cython_setuptools_option
from .pkgconfig_wrapper import get_flags
from .common import C_EXT, CPP_EXT, CYTHON_EXT, convert_to_bool, get_cpp_std_flag


def create_extensions(original_setup_file: str, cythonize: bool | None = None) -> list:
    """
    Create a list of extentions to be used as argument ``ext_modules`` of ``setuptools.setup()`` by reading the ``pyproject.toml``

    To force to compile pyx into .c/.cpp set ``CYTHONIZE`` env variable to True or if it is not set use the cythonize of this function
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
            If True ``Cython.Build.cythonize`` will always be called
            If False ``Cython.Build.cythonize`` will never be called
            If None ``Cython.Build.cythonize`` will be called if the generated .c/.cpp file does not match the .pyx
            Note that even if only 1 file does not match, it will be called for all extensions
            It is overrided by the env variable ``CYTHONIZE``

    Returns:
        A list Extentions, It can be safely used for ``ext_modules`` argument of ``setuptools.setup()``
    """
    extensions_options = read_cython_setuptools_option(Path(original_setup_file).parent / "pyproject.toml")
    extensions = []
    cythonize = _compute_cythonize(extensions_options, cythonize)
    profile_cython = convert_to_bool(os.environ.get("PROFILE_CYTHON", False))
    debug = convert_to_bool(os.environ.get("DEBUG", False))
    for name, options in extensions_options.items():
        _complete_cython_options(options, debug, cythonize)
        extensions.append(_create_extension(name, options, profile_cython))
    if cythonize:
        cythonized_extensions = Cython.Build.cythonize(extensions, force=True)
        for options in extensions_options.values():
            _add_pyx_file_hash_to_generated_files(options)
        return cythonized_extensions
    return extensions


def _compute_cythonize(extensions_options: dict[str, CythonSetuptoolsOptions], cythonize_arg: bool | None) -> bool:
    cythonize_env = os.environ.get("CYTHONIZE", None)
    if cythonize_env is not None:
        return convert_to_bool(cythonize_env)
    if cythonize_arg is not None:
        return cythonize_arg
    for options in extensions_options.values():
        new_ext = CPP_EXT if options.language == "c++" else C_EXT
        for source in options.sources:
            source_path = Path(source)
            if source_path.suffix == CYTHON_EXT:
                output_path = source_path.with_suffix(new_ext)
                if not _is_generated_file_up_to_date(source_path, output_path):
                    return True
    return False


def _read_pyx_file_hash_from_generated_files(generated_file_path: Path) -> str:
    if not generated_file_path.exists():
        return ""
    with open(generated_file_path, 'r', encoding='utf8') as f:
        content = f.read()
    match = re.search(r'^// input_hash: ([a-fA-F0-9]+)$', content, re.MULTILINE)
    return match.group(1) if match else ""


def _is_generated_file_up_to_date(pyx_file_path: Path, generated_file_path: Path) -> bool:
    return _sha256sum(pyx_file_path) == _read_pyx_file_hash_from_generated_files(generated_file_path)


def _add_pyx_file_hash_to_generated_files(options: CythonSetuptoolsOptions):
    new_ext = CPP_EXT if options.language == "c++" else C_EXT
    for source in options.sources:
        source_path = Path(source)
        if source_path.suffix == CYTHON_EXT:
            output_path = source_path.with_suffix(new_ext)
            pyx_hash = _sha256sum(source_path)
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"\n// input_hash: {pyx_hash}\n")


def _sha256sum(filename: Path) -> str:
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
        return file_hash.hexdigest()


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
