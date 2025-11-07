"""Resource locator for finding package data files (docs, basic programs, etc.)

This module provides functions to locate package resources (data files, docs,
examples) that work both in development (running from source) and in installed
environments (pip install).

Note: This is distinct from resource_limits.py which enforces runtime execution limits.

When installed via pip, data files are typically installed to:
- Site-packages: /usr/local/lib/python3.x/site-packages/mbasic/docs/
- User install: ~/.local/lib/python3.x/site-packages/mbasic/docs/
- System install: /usr/lib/python3.x/site-packages/mbasic/docs/

This module tries multiple strategies:
1. Development: Look relative to source files (../../docs from src/)
2. Python 3.9+: Use importlib.resources.files()
3. Fallback: Use pkg_resources (setuptools)
4. Last resort: Check sys.prefix locations
"""

import sys
from pathlib import Path
from typing import Optional


def find_docs_dir() -> Path:
    """Find the docs directory in development or installed environment.

    Returns:
        Path to docs directory

    Raises:
        FileNotFoundError: If docs directory cannot be found
    """
    # Strategy 1: Development mode - look relative to this file
    # This file is in src/, so docs is at ../docs
    dev_docs = Path(__file__).parent.parent / "docs"
    if dev_docs.is_dir() and (dev_docs / "help" / "index.md").exists():
        return dev_docs

    # Strategy 2: Python 3.9+ importlib.resources
    if sys.version_info >= (3, 9):
        try:
            from importlib.resources import files
            # Try to find docs as package data
            docs_path = files('mbasic').joinpath('docs')
            if docs_path.is_dir():
                return Path(str(docs_path))
        except (ImportError, AttributeError, TypeError):
            pass

    # Strategy 3: pkg_resources (older method, requires setuptools)
    try:
        import pkg_resources
        docs_path = Path(pkg_resources.resource_filename('mbasic', 'docs'))
        if docs_path.is_dir():
            return docs_path
    except (ImportError, KeyError):
        pass

    # Strategy 4: Check common installation locations
    # Look in site-packages next to where our source module is
    src_module_path = Path(__file__).parent
    possible_locations = [
        src_module_path.parent / "docs",  # mbasic/docs (if src is mbasic/src)
        src_module_path / "docs",          # src/docs
        Path(sys.prefix) / "share" / "mbasic" / "docs",  # /usr/share/mbasic/docs
        Path(sys.prefix) / "local" / "share" / "mbasic" / "docs",  # /usr/local/share/mbasic/docs
    ]

    for location in possible_locations:
        if location.is_dir() and (location / "help" / "index.md").exists():
            return location

    # Give up
    raise FileNotFoundError(
        "Cannot find docs directory. Searched:\n" +
        f"  Development: {dev_docs}\n" +
        "  Installed package data\n" +
        "  System locations: /usr/share/mbasic/docs, etc.\n\n" +
        "If you installed via pip, the package may be misconfigured.\n" +
        "If running from source, ensure docs/help/index.md exists."
    )


def find_help_dir() -> Path:
    """Find the help documentation directory.

    Returns:
        Path to docs/help directory

    Raises:
        FileNotFoundError: If help directory cannot be found
    """
    return find_docs_dir() / "help"


def find_library_dir() -> Path:
    """Find the library (games, demos) directory.

    Returns:
        Path to docs/library directory

    Raises:
        FileNotFoundError: If library directory cannot be found
    """
    return find_docs_dir() / "library"


def find_basic_dir() -> Optional[Path]:
    """Find the basic programs directory (development only).

    Returns:
        Path to basic/ directory, or None if not in development mode
    """
    # basic/ directory is development-only, not distributed
    dev_basic = Path(__file__).parent.parent / "basic"
    if dev_basic.is_dir():
        return dev_basic
    return None
