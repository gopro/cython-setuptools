# FIXME
# distutils is deprecated starting from python3.10
# but the migration to setuptools is not completed
# this import will change in the future
from setuptools._distutils.ccompiler import get_default_compiler

CYTHON_EXT = ".pyx"
C_EXT = ".c"
CPP_EXT = ".cpp"


def get_cpp_std_flag(version: int | str) -> str:
    """
    Get the compiler flag for the corresponding version for the default compiler

    Args:
        version: C++ standard version (eg: 98, 11, 14, 17, 20, 23, 26)

    Returns:
        The compiler flag
    """
    return f"/std:c++{version}" if get_default_compiler() == "msvc" else f"-std=c++{version}"


def convert_to_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    value = value.lower()
    if value in ("1", "on", "true", "yes"):
        return True
    elif value in ("0", "off", "false", "no"):
        return False
    raise ValueError(f"invalid boolean string {value}")
