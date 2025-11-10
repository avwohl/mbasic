"""
Auto-Save Manager for MBASIC IDE

Provides auto-save functionality with Emacs-inspired naming (#filename#):
- Saves to centralized temp directory (~/.mbasic/autosave/) automatically
- Uses Emacs-style #filename# naming convention
- Provides utilities to check if autosave is newer than saved file
- Cleans up old autosaves

This module provides building blocks for auto-save functionality, including
helper methods to format prompts. The UI layer is responsible for:
- Displaying prompts to user (this module provides format_recovery_prompt() helper)
- Deciding when to offer recovery on startup
- Deciding when to trigger auto-save operations
- Handling user responses to prompts

Usage:
    manager = AutoSaveManager(autosave_dir=Path.home() / '.mbasic' / 'autosave')
    manager.start_autosave('foo.bas', get_content_callback, interval=30)
    manager.stop_autosave()
    manager.cleanup_after_save('foo.bas')
"""

from pathlib import Path
from typing import Optional, Callable
from datetime import datetime, timedelta
import threading
import time


class AutoSaveManager:
    """Manages automatic saving of editor content to temp files."""

    def __init__(self, autosave_dir: Optional[Path] = None):
        """
        Initialize auto-save manager.

        Args:
            autosave_dir: Directory for autosave files (default: ~/.mbasic/autosave)
        """
        self.autosave_dir = autosave_dir or (Path.home() / '.mbasic' / 'autosave')
        self.autosave_dir.mkdir(parents=True, exist_ok=True)

        # Auto-save state
        self.timer = None
        self.current_file = None
        self.get_content = None
        self.last_content = None
        self.interval = 30  # seconds
        self.running = False

    def get_autosave_path(self, filepath: str) -> Path:
        """
        Get the autosave path for a given file.

        Args:
            filepath: Original file path (e.g., 'foo.bas' or '/path/to/foo.bas')

        Returns:
            Path to autosave file (e.g., ~/.mbasic/autosave/#foo.bas#)
        """
        # Get just the filename
        filename = Path(filepath).name if filepath else 'untitled.bas'

        # Emacs-inspired naming: #filename#
        autosave_name = f"#{filename}#"

        return self.autosave_dir / autosave_name

    def has_autosave(self, filepath: str) -> bool:
        """
        Check if an autosave exists for the given file.

        Args:
            filepath: Original file path

        Returns:
            True if autosave exists
        """
        autosave_path = self.get_autosave_path(filepath)
        return autosave_path.exists()

    def is_autosave_newer(self, filepath: str) -> bool:
        """
        Check if autosave is newer than the original file.

        Args:
            filepath: Original file path

        Returns:
            True if autosave exists and is newer than original file
        """
        if not filepath or not Path(filepath).exists():
            # If original doesn't exist, autosave is "newer"
            return self.has_autosave(filepath)

        autosave_path = self.get_autosave_path(filepath)
        if not autosave_path.exists():
            return False

        original_mtime = Path(filepath).stat().st_mtime
        autosave_mtime = autosave_path.stat().st_mtime

        return autosave_mtime > original_mtime

    def get_autosave_info(self, filepath: str) -> Optional[dict]:
        """
        Get information about an autosave file.

        Args:
            filepath: Original file path

        Returns:
            Dict with autosave info or None if no autosave exists
            {
                'path': Path,
                'size': int,
                'modified': datetime,
                'age_seconds': float
            }
        """
        autosave_path = self.get_autosave_path(filepath)
        if not autosave_path.exists():
            return None

        stat = autosave_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        age = (datetime.now() - mtime).total_seconds()

        return {
            'path': autosave_path,
            'size': stat.st_size,
            'modified': mtime,
            'age_seconds': age
        }

    def load_autosave(self, filepath: str) -> Optional[str]:
        """
        Load content from autosave file.

        Args:
            filepath: Original file path

        Returns:
            Autosave content or None if not found
        """
        autosave_path = self.get_autosave_path(filepath)
        if not autosave_path.exists():
            return None

        try:
            return autosave_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error loading autosave: {e}")
            return None

    def save_now(self, filepath: str, content: str) -> bool:
        """
        Immediately save content to autosave file.

        Args:
            filepath: Original file path (for naming autosave)
            content: Content to save

        Returns:
            True if save successful
        """
        try:
            autosave_path = self.get_autosave_path(filepath)
            autosave_path.write_text(content, encoding='utf-8')
            self.last_content = content
            return True
        except Exception as e:
            print(f"Error saving autosave: {e}")
            return False

    def _autosave_worker(self):
        """Background worker that periodically saves content."""
        while self.running:
            time.sleep(self.interval)

            if not self.running:
                break

            # Get current content
            if self.get_content:
                try:
                    content = self.get_content()

                    # Only save if content changed
                    if content != self.last_content:
                        self.save_now(self.current_file, content)

                except Exception as e:
                    print(f"Error in autosave worker: {e}")

    def start_autosave(
        self,
        filepath: str,
        get_content_callback: Callable[[], str],
        interval: int = 30
    ):
        """
        Start automatic saving.

        Args:
            filepath: File being edited (for naming autosave)
            get_content_callback: Function that returns current editor content
            interval: Save interval in seconds (default: 30)
        """
        # Stop any existing autosave
        self.stop_autosave()

        # Set up new autosave
        self.current_file = filepath
        self.get_content = get_content_callback
        self.interval = interval
        self.last_content = None
        self.running = True

        # Start background thread
        self.timer = threading.Thread(target=self._autosave_worker, daemon=True)
        self.timer.start()

    def stop_autosave(self):
        """Stop automatic saving."""
        self.running = False
        if self.timer:
            self.timer.join(timeout=1.0)
            self.timer = None

        self.current_file = None
        self.get_content = None
        self.last_content = None

    def cleanup_after_save(self, filepath: str):
        """
        Delete autosave file after user saves.

        Call this when the user successfully saves their file.

        Args:
            filepath: File that was saved
        """
        autosave_path = self.get_autosave_path(filepath)
        if autosave_path.exists():
            try:
                autosave_path.unlink()
            except Exception as e:
                print(f"Error deleting autosave: {e}")

    def cleanup_old_autosaves(self, max_age_days: int = 7):
        """
        Clean up old autosave files.

        Args:
            max_age_days: Delete autosaves older than this many days
        """
        cutoff = datetime.now() - timedelta(days=max_age_days)

        for autosave_file in self.autosave_dir.glob('#*#'):
            try:
                mtime = datetime.fromtimestamp(autosave_file.stat().st_mtime)
                if mtime < cutoff:
                    autosave_file.unlink()
            except Exception as e:
                print(f"Error cleaning up {autosave_file}: {e}")

    def format_recovery_prompt(self, filepath: str) -> Optional[str]:
        """
        Generate a recovery prompt message.

        Args:
            filepath: Original file path

        Returns:
            Formatted message or None if no recovery needed
        """
        if not self.is_autosave_newer(filepath):
            return None

        info = self.get_autosave_info(filepath)
        if not info:
            return None

        # Format timestamps
        modified_str = info['modified'].strftime('%Y-%m-%d %H:%M:%S')

        # Calculate age
        age = info['age_seconds']
        if age < 60:
            age_str = f"{int(age)} seconds ago"
        elif age < 3600:
            age_str = f"{int(age / 60)} minutes ago"
        else:
            age_str = f"{int(age / 3600)} hours ago"

        filename = Path(filepath).name if filepath else 'untitled.bas'

        return f"""Auto-save file found for: {filename}

The auto-saved version is newer than your last save.

Auto-save: {modified_str} ({age_str})
Size: {info['size']} bytes

Would you like to recover the auto-saved version?"""
