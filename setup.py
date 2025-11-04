#!/usr/bin/env python3
"""
Setup script for MBASIC 5.21 Interpreter
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="mbasic-interpreter",
    version="0.99.0",  # Reflects ~99% implementation status (core complete)
    description="An interpreter for MBASIC 5.21 (BASIC-80 for CP/M) - Independent open-source implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aaron Wohl",
    author_email="mbasic@wohl.com",
    url="https://github.com/avwohl/mbasic",
    license="MIT",

    packages=find_packages(exclude=["tests", "basic", "doc", "utils", "bin"]),

    # Include the main script
    py_modules=["mbasic"],

    # Create a command-line script
    entry_points={
        "console_scripts": [
            "mbasic=mbasic:main",
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
        "License :: OSI Approved :: MIT License",
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
