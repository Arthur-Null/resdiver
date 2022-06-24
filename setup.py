from pathlib import Path

from setuptools import find_packages, setup

init_file_path = "resdiver/__init__.py"


def read(rel_path):
    with open(Path(__file__).parent / rel_path, "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="resdiver",
    version=get_version(init_file_path),
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.4",
        "Click",
        "pyyaml",
    ],
    entry_points={"console_scripts": ["gather_results = resdiver.gather_results:gather_results"]},
)
