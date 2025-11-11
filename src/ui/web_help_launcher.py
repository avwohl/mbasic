"""Web browser help launcher for MBASIC.

Opens help documentation in the system's default web browser.
Points to GitHub Pages by default, with optional override via MBASIC_DOCS_URL environment variable.
"""

import webbrowser
import subprocess
import socket
import time
from pathlib import Path
from typing import Optional
from ..docs_config import get_docs_url, DOCS_BASE_URL


def open_help_in_browser(topic=None, ui_type="tk"):
    """Open help documentation in web browser.

    Uses GitHub Pages by default (https://avwohl.github.io/mbasic/help/).
    Override with MBASIC_DOCS_URL environment variable for local development.

    Args:
        topic: Specific help topic (e.g., "statements/print", "ui/tk/index")
        ui_type: UI type for UI-specific help ("tk", "curses", "web", "cli")

    Returns:
        bool: True if browser opened successfully, False otherwise
    """
    # Get URL using centralized configuration
    url = get_docs_url(topic, ui_type)

    # Check if a browser is available
    try:
        browser = webbrowser.get()
    except webbrowser.Error as e:
        import sys
        sys.stderr.write(f"BROWSER ERROR: No browser available - {e}\n")
        sys.stderr.write(f"URL was: {url}\n")
        sys.stderr.flush()
        return False

    # Open in browser
    try:
        result = webbrowser.open(url)
        import sys
        sys.stderr.write(f"webbrowser.open() returned: {result}\n")
        sys.stderr.flush()
        return result
    except Exception as e:
        import sys
        sys.stderr.write(f"Error opening browser: {e}\n")
        sys.stderr.flush()
        return False


# Simple convenience function
def open_help():
    """Open help documentation in browser (default page)."""
    return open_help_in_browser()


# Legacy class kept for compatibility - new code should use direct web URL instead
# The help site is built and served at GitHub Pages (https://avwohl.github.io/mbasic/help/)
#
# Migration guide for code using this class:
# OLD: launcher = WebHelpLauncher(); launcher.open_help("statements/print")
# NEW: open_help_in_browser("statements/print")  # Uses directory-style URLs: /statements/print/
# NEW: In NiceGUI backend, use: ui.navigate.to('/mbasic_docs/statements/print/', new_tab=True)
# Note: MkDocs uses directory-style URLs by default (/path/ not /path.html)

class WebHelpLauncher_DEPRECATED:
    """Legacy class wrapper for compatibility."""

    def __init__(self, help_root: str = "docs/help"):
        """Initialize help launcher (legacy compatibility)."""
        self.help_root = Path(help_root)
        self.server_process = None
        self.server_port = 8000

    def open_help(self, topic: Optional[str] = None, ui_type: str = "tk"):
        """Open help documentation in web browser.

        Args:
            topic: Specific help topic (e.g., "statements/print")
            ui_type: UI type for UI-specific help ("tk", "curses", "web", "cli")
        """
        # Check if we need to build help first
        if not self._is_help_built():
            self._build_help()

        # Start local server if needed
        if not self._is_server_running():
            self._start_help_server()

        # Construct URL
        base_url = f"http://localhost:{self.server_port}"

        if topic:
            # Convert topic to URL path
            # e.g., "statements/print" -> "/statements/print/"
            if not topic.endswith('/'):
                topic += '/'
            if not topic.startswith('/'):
                topic = '/' + topic
            url = base_url + topic
        else:
            # Default to UI-specific index
            url = f"{base_url}/ui/{ui_type}/"

        # Open in browser
        webbrowser.open(url)

    def _is_help_built(self) -> bool:
        """Check if help has been built to HTML."""
        site_dir = self.help_root / "site"
        index_file = site_dir / "index.html"
        return site_dir.exists() and index_file.exists()

    def _build_help(self):
        """Build help documentation to HTML using MkDocs."""
        print("Building help documentation...")

        # Check if mkdocs is available
        try:
            subprocess.run(
                ["mkdocs", "--version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("MkDocs not installed. Using fallback markdown viewer.")
            self._use_fallback_viewer()
            return

        # Build help
        try:
            subprocess.run(
                ["mkdocs", "build"],
                cwd=self.help_root,
                capture_output=True,
                check=True
            )
            print("Help documentation built successfully")
        except subprocess.CalledProcessError as e:
            print(f"Failed to build help: {e}")
            self._use_fallback_viewer()

    def _is_server_running(self) -> bool:
        """Check if help server is already running."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', self.server_port))
            sock.close()
            return result == 0
        except:
            return False

    def _start_help_server(self):
        """Start a simple HTTP server for help files."""
        site_dir = self.help_root / "site"

        if not site_dir.exists():
            print("Help not built, using fallback")
            self._use_fallback_viewer()
            return

        print(f"Starting help server on port {self.server_port}...")

        # Use Python's built-in HTTP server
        self.server_process = subprocess.Popen(
            ["python3", "-m", "http.server", str(self.server_port)],
            cwd=site_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for server to start
        for _ in range(10):
            if self._is_server_running():
                print("Help server started")
                break
            time.sleep(0.5)
        else:
            print("Failed to start help server")
            self._use_fallback_viewer()

    def _use_fallback_viewer(self):
        """Fallback: Open markdown files directly or use simple viewer."""
        # For now, just inform user
        print("Help system: Please install MkDocs for best experience")
        print("Run: pip install mkdocs mkdocs-material")

        # Could implement a simple markdown viewer here
        # or open the raw markdown files

    def stop_server(self):
        """Stop the help server if running."""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None


# Alias for backwards compatibility
def open_online_help(topic: Optional[str] = None, ui_type: str = "cli"):
    """Open online help documentation.

    Opens the hosted documentation on GitHub Pages.
    This is now an alias for open_help_in_browser() since it uses GitHub Pages by default.
    """
    return open_help_in_browser(topic, ui_type)