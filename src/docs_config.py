"""
Documentation URL configuration for MBASIC UIs.

Provides centralized configuration for documentation URLs, supporting both
local development and production deployment.

Environment Variables:
    MBASIC_DOCS_URL: Override the documentation base URL
                     Default: https://avwohl.github.io/mbasic/help/
                     For local development: http://localhost:8000/help/
"""

import os
from pathlib import Path


# Default production documentation URL (GitHub Pages)
DEFAULT_DOCS_URL = "https://avwohl.github.io/mbasic/help/"

# Get documentation URL from environment or use default
DOCS_BASE_URL = os.environ.get('MBASIC_DOCS_URL', DEFAULT_DOCS_URL)


def get_docs_url(topic: str = None, ui_type: str = "cli") -> str:
    """
    Get the documentation URL for a specific topic.

    Args:
        topic: Specific help topic (e.g., "common/statements/print")
        ui_type: UI type for UI-specific help ("tk", "curses", "web", "cli")

    Returns:
        Full URL to the documentation page
    """
    base = DOCS_BASE_URL.rstrip('/')

    if topic:
        # Ensure topic has proper path format
        topic = topic.lstrip('/')
        if not topic.endswith('/') and '.' not in topic:
            topic += '/'
        return f"{base}/{topic}"
    else:
        # Default to UI-specific index
        return f"{base}/ui/{ui_type}/"


def get_local_docs_path() -> Path:
    """
    Get the path to local documentation files.

    Returns:
        Path to docs/help directory (relative to project root)

    Note: Local docs are used by UIs that render markdown directly (curses, tk).
    Web-based UIs should use get_docs_url() instead.
    """
    # Get path to this module (src/docs_config.py)
    src_dir = Path(__file__).parent

    # Project root is parent of src
    project_root = src_dir.parent

    # docs/help is the help documentation root
    return project_root / "docs" / "help"


def is_using_remote_docs() -> bool:
    """
    Check if documentation is configured to use remote URL.

    Returns:
        True if using remote (web-based) documentation, False if localhost
    """
    return not DOCS_BASE_URL.startswith('http://localhost')


# For backwards compatibility and convenience
HELP_BASE_URL = DOCS_BASE_URL
