import os
from setuptools import find_packages
from distutils.core import setup

# Setting the version
version = "0.0.1"
# Determining the root dir.
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(ROOT_DIR, "README.md"), "r", encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except IOError:
    LONG_DESCRIPTION = ""
setup(
    name="PYSE lab tasks",
    version=version,
    description="PYSE",
    long_description=LONG_DESCRIPTION,
    author="S&S",
    author_email="simen.myrrusten@gmail.com",
    url="https://github.com/nemisis84/PYSE",
    package_dir={"": "src"},
    include_package_data=False,
    packages=find_packages("src"),
    install_requires=['sympy', 'numpy'],
    python_requires=">=3.10"
)
