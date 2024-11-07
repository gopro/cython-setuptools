"""
Module to wrap calls to pkg-config
"""
from dataclasses import dataclass, field
import os
import shlex
import subprocess


@dataclass
class BuildFlags:
    """
    Build flags that can be returned by pkg-config
    """
    compile_flags: list[str] = field(default_factory=list)  # eg: -I -DMY_MACRO
    link_flags: list[str] = field(default_factory=list)  # eg: -L -l


def get_flags(pkg_config_packages: list[str], pkg_config_dirs: list[str] | None = None) -> BuildFlags:
    """
    Get build flags from dependencies using pkg-config.
    It uses pkg-config options --cflags for compilation flags and --libs for link flags

    Args:
        pkg_config_packages: list of packages to send to pkg config
        pkg_config_dirs: extend the `PKG_CONFIG_PATH` env variable

    Returns:
        A BuildFlags dataclass
    """
    if not pkg_config_packages:
        return BuildFlags()

    compile_flags = _run_pkg_config(pkg_config_packages, "--cflags", pkg_config_dirs)
    link_flags = _run_pkg_config(pkg_config_packages, "--libs", pkg_config_dirs)

    return BuildFlags(shlex.split(compile_flags), shlex.split(link_flags))


def _run_pkg_config(pkg_names: list[str], option: str, pkg_config_dirs: list[str] | None = None) -> str:
    env = os.environ.copy()
    if pkg_config_dirs:
        _extend_pkg_config_path(pkg_config_dirs, env)
    cmd = ["pkg-config", option, *pkg_names]
    return subprocess.check_output(cmd, env=env).decode("utf8")


def _extend_pkg_config_path(pkg_config_dirs: list[str], env_to_update: dict[str, str]):
    original = env_to_update.get("PKG_CONFIG_PATH", "")
    if original != "" and not original.endswith(":"):
        original += ":"
    env_to_update["PKG_CONFIG_PATH"] = original + ":".join(pkg_config_dirs)
