#!/usr/bin/env python3
"""
Setup script for MBASIC 5.21 Interpreter

Package version: 0.99.0 (reflects approximately 99% implementation status - core complete)
Language version: MBASIC 5.21 (Microsoft BASIC-80 for CP/M)

Note: 5.21 refers to the Microsoft BASIC-80 language version being interpreted,
not this package's version number. This is an independent open-source implementation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="mbasic-interpreter",
    version="0.99.0",  # Package version (99% implementation status). Note: 5.21 is the BASIC language version.
    description="An interpreter for MBASIC 5.21 (BASIC-80 for CP/M) - Independent open-source implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aaron Wohl",
    author_email="mbasic@wohl.com",
    url="https://github.com/avwohl/mbasic",
    license="GPL-3.0-or-later",

    packages=find_packages(exclude=["tests", "basic", "doc", "utils", "bin"]),

    # Include the main script
    py_modules=["mbasic"],

    # Create a command-line script and register mkdocs plugins
    entry_points={
        "console_scripts": [
            "mbasic=mbasic:main",
        ],
        "mkdocs.plugins": [
            "macro_expander = utils.mkdocs_plugins.macro_expander:MacroExpanderPlugin",
        ],
    },

    # Python version requirement
    python_requires=">=3.8",

    # No external dependencies required (only standard library)
    install_requires=[],

    # Optional development dependencies
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },

    # Package metadata
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Other",
        "Topic :: Software Development :: Interpreters",
        "Topic :: System :: Emulators",
        "Operating System :: OS Independent",
    ],

    keywords="basic interpreter mbasic basic-80 cpm retro-computing vintage",

    # Include additional files specified in MANIFEST.in
    include_package_data=True,

    # Zip safe
    zip_safe=False,

    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/avwohl/mbasic/issues",
        "Source": "https://github.com/avwohl/mbasic",
        "Documentation": "https://github.com/avwohl/mbasic/blob/main/README.md",
    },
)
