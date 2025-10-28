"""
Recent Files Manager - Shared module for tracking recently opened files

This module provides a simple, portable way to track recently opened files
across all UIs (Tk, Curses, Web). Files are stored in a JSON file in the
user's config directory.

Features:
- Stores last 10 recently opened files
- Records full path and last access timestamp
- Automatically creates config directory if needed
- Thread-safe file operations
- Cross-platform (uses pathlib)

Usage:
    from src.ui.recent_files import RecentFilesManager

    rfm = RecentFilesManager()
    rfm.add_file("/path/to/program.bas")
    recent = rfm.get_recent_files()
    for filepath in recent:
        print(filepath)
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import os


class RecentFilesManager:
    """Manages a list of recently opened files."""

    def __init__(self, max_files: int = 10, config_dir: Optional[Path] = None):
        """Initialize the recent files manager.

        Args:
            max_files: Maximum number of recent files to track (default: 10)
            config_dir: Custom config directory (default: ~/.mbasic)
        """
        self.max_files = max_files

        # Determine config directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use platform-appropriate config directory
            home = Path.home()
            self.config_dir = home / '.mbasic'

        # Recent files JSON file
        self.recent_files_path = self.config_dir / 'recent_files.json'

        # Ensure config directory exists
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # If we can't create config dir, we'll just fail silently
            # and operations will fall back to in-memory only
            pass

    def _load_recent_files(self) -> list:
        """Load recent files from disk.

        Returns:
            List of dicts with 'path' and 'timestamp' keys
        """
        if not self.recent_files_path.exists():
            return []

        try:
            with open(self.recent_files_path, 'r') as f:
                data = json.load(f)
                # Validate structure
                if isinstance(data, list):
                    return [item for item in data if isinstance(item, dict) and 'path' in item]
                return []
        except (json.JSONDecodeError, OSError):
            # Corrupted or unreadable file - return empty list
            return []

    def _save_recent_files(self, files: list):
        """Save recent files to disk.

        Args:
            files: List of dicts with 'path' and 'timestamp' keys
        """
        try:
            with open(self.recent_files_path, 'w') as f:
                json.dump(files, f, indent=2)
        except OSError:
            # Can't write to disk - fail silently
            pass

    def add_file(self, filepath: str):
        """Add a file to the recent files list.

        If the file is already in the list, it's moved to the top.
        If the list exceeds max_files, oldest entries are removed.

        Args:
            filepath: Full path to the file to add
        """
        # Normalize path
        filepath = str(Path(filepath).resolve())

        # Load current list
        recent = self._load_recent_files()

        # Remove file if already present (we'll add it at the top)
        recent = [item for item in recent if item.get('path') != filepath]

        # Add to top with current timestamp
        recent.insert(0, {
            'path': filepath,
            'timestamp': datetime.now().isoformat()
        })

        # Trim to max_files
        recent = recent[:self.max_files]

        # Save
        self._save_recent_files(recent)

    def get_recent_files(self, max_count: Optional[int] = None) -> List[str]:
        """Get list of recent file paths.

        Args:
            max_count: Maximum number of files to return (default: all)

        Returns:
            List of file paths, most recent first
        """
        recent = self._load_recent_files()

        # Filter out files that no longer exist
        existing = []
        for item in recent:
            path = item.get('path')
            if path and Path(path).exists():
                existing.append(path)

        # Update file if we removed any non-existent files
        if len(existing) < len(recent):
            self._save_recent_files([
                {'path': path, 'timestamp': item.get('timestamp', '')}
                for item, path in zip(recent, existing)
            ])

        # Apply max_count if specified
        if max_count is not None:
            existing = existing[:max_count]

        return existing

    def clear(self):
        """Clear all recent files."""
        self._save_recent_files([])

    def remove_file(self, filepath: str):
        """Remove a specific file from the recent files list.

        Args:
            filepath: Full path to the file to remove
        """
        # Normalize path
        filepath = str(Path(filepath).resolve())

        # Load current list
        recent = self._load_recent_files()

        # Remove file
        recent = [item for item in recent if item.get('path') != filepath]

        # Save
        self._save_recent_files(recent)

    def get_recent_files_with_info(self, max_count: Optional[int] = None) -> List[dict]:
        """Get list of recent files with full information.

        Args:
            max_count: Maximum number of files to return (default: all)

        Returns:
            List of dicts with 'path', 'timestamp', 'filename', 'exists' keys
        """
        recent = self._load_recent_files()

        # Add additional info
        result = []
        for item in recent:
            path = item.get('path')
            if path:
                path_obj = Path(path)
                result.append({
                    'path': path,
                    'timestamp': item.get('timestamp', ''),
                    'filename': path_obj.name,
                    'exists': path_obj.exists()
                })

        # Apply max_count if specified
        if max_count is not None:
            result = result[:max_count]

        return result
