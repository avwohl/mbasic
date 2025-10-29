"""Web browser help launcher for MBASIC.

Opens help documentation in the system's default web browser instead of
using custom help windows. This leverages the fact that help is already
built for web viewing.
"""

import webbrowser
import os
import subprocess
import time
import socket
from pathlib import Path
from typing import Optional


class WebHelpLauncher:
    """Launches help documentation in web browser."""

    def __init__(self, help_root: str = "docs/help"):
        """Initialize help launcher.

        Args:
            help_root: Path to help documentation root
        """
        self.help_root = Path(help_root)
        self.server_process = None
        self.server_port = 8081  # Different from main web UI (8080)

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


def open_help_in_browser(topic: Optional[str] = None, ui_type: str = "tk"):
    """Convenience function to open help in browser.

    Args:
        topic: Specific help topic
        ui_type: UI type for UI-specific help
    """
    launcher = WebHelpLauncher()
    launcher.open_help(topic, ui_type)


# Alternative: Use GitHub Pages or other hosted documentation
def open_online_help(topic: Optional[str] = None):
    """Open online help documentation.

    Opens the hosted documentation on GitHub Pages or other hosting service.
    """
    base_url = "https://yourusername.github.io/mbasic-docs"

    if topic:
        url = f"{base_url}/{topic}"
    else:
        url = base_url

    webbrowser.open(url)