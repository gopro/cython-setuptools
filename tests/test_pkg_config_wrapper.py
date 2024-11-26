from pathlib import Path
import platform

import pytest

from cython_setuptools.pkgconfig_wrapper import _extend_pkg_config_path, get_flags

DATA_DIR = Path(__file__).parent / "data"


def test_extend_pkg_config_path():
    dirs = ["toto", "foo"]
    expected = "toto:foo"
    empty_path = {"PKG_CONFIG_PATH": ""}
    _extend_pkg_config_path(dirs, empty_path)
    assert empty_path["PKG_CONFIG_PATH"] == expected

    path_not_defined = {}
    _extend_pkg_config_path(dirs, path_not_defined)
    assert path_not_defined["PKG_CONFIG_PATH"] == expected

    expected = "/lol/toto:toto:foo"
    path_not_terminator = {"PKG_CONFIG_PATH": "/lol/toto"}
    _extend_pkg_config_path(dirs, path_not_terminator)
    assert path_not_terminator["PKG_CONFIG_PATH"] == expected

    path_with_terminator = {"PKG_CONFIG_PATH": "/lol/toto:"}
    _extend_pkg_config_path(dirs, path_with_terminator)
    assert path_with_terminator["PKG_CONFIG_PATH"] == expected


@pytest.mark.skipif(platform.system() == 'Windows', reason='Having pkg-config on windows is not trivial')
def test_get_flags():
    build_flags = get_flags(["my_fake_lib"], [str(DATA_DIR)])
    assert build_flags.link_flags == ["-L/tmp/lib", "-lmy_fake_lib"]
    assert build_flags.compile_flags == ["-I/tmp/include"]
