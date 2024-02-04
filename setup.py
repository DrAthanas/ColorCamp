#!/usr/bin/env python3

from pathlib import Path
from setuptools import setup

# get key package details from py_pkg/__version__.py
about = {}  # type: ignore
here = Path(__file__).parent
package_name = "colorcamp"
with open(here / package_name / "__version__.py", "r") as f:
    exec(f.read(), about)

# load the README file and use it as the long_description for PyPI
with open("README.md", "r") as f:
    readme = f.read()

# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    name=about["__title__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    version=about["__version__"],
    author=about["__author__"],
    url=about["__url__"],
    packages=[package_name],
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[],
    license=about["__license__"],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="colors",
)
