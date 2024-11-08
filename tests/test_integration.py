import os
from pathlib import Path
import shutil

import cython_setuptools


this_dir = Path(__file__).parent
cython_setuptools_path = Path(cython_setuptools.__file__, "..", "..").absolute()


def _setup_source(setup_name: str, tmp_path: Path):
    pypkg_dir = tmp_path / 'pypkg'
    src_dir = tmp_path / 'src'
    setup_path = pypkg_dir / 'setup.py'
    shutil.copytree(this_dir / 'pypkg', pypkg_dir)
    shutil.copytree(this_dir / 'src', src_dir)
    os.symlink(pypkg_dir / setup_name, setup_path)
    return setup_path, pypkg_dir


def test_compile_and_run_no_cythonize_mode(virtualenv, tmp_path: Path):
    setup_path, pypkg_dir = _setup_source("setup-no-cythonize.py", tmp_path)
    virtualenv.run(f"pip install {cython_setuptools_path}")
    virtualenv.env.update({'CYTHONIZE': "1"})
    virtualenv.run(f"pip install -e {pypkg_dir}")
    assert int(virtualenv.run("python -m bar", capture=True)) == 2


def test_compile_and_run_cythonize_mode(virtualenv, tmp_path: Path):
    setup_path, pypkg_dir = _setup_source("setup-cythonize.py", tmp_path)
    virtualenv.run(f"pip install {cython_setuptools_path}")
    virtualenv.run(f"pip install -e {pypkg_dir}")
    assert int(virtualenv.run("python -m bar", capture=True)) == 2
