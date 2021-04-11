"""Setup script for realpython-reader"""

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="flowi",
    version="0.2.0",
    description="ML lifecycle",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/psilva-leo/flowi",
    author="Leonardo Silva",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["flowi"],
    include_package_data=True,
    install_requires=[
        "dask[complete]",
        "dask-ml",
        "sklearn"
    ],
    entry_points={"console_scripts": ["flowi=flowi.__main__:main"]},
)
