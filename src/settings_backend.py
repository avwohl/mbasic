"""Settings storage backends for MBASIC.

Provides pluggable storage backends for settings:
- FileSettingsBackend: Local filesystem storage (default, single-user)
- RedisSettingsBackend: Per-session Redis storage (multi-user web deployments)
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class SettingsBackend(ABC):
    """Abstract base class for settings storage backends."""

    @abstractmethod
    def load_global(self) -> Dict[str, Any]:
        """Load global settings.

        Returns:
            Dict of setting_key -> value
        """
        pass

    @abstractmethod
    def save_global(self, settings: Dict[str, Any]) -> None:
        """Save global settings.

        Args:
            settings: Dict of setting_key -> value
        """
        pass

    @abstractmethod
    def load_project(self) -> Dict[str, Any]:
        """Load project settings.

        Returns:
            Dict of setting_key -> value
        """
        pass

    @abstractmethod
    def save_project(self, settings: Dict[str, Any]) -> None:
        """Save project settings.

        Args:
            settings: Dict of setting_key -> value
        """
        pass


class FileSettingsBackend(SettingsBackend):
    """File-based settings storage (original behavior).

    Stores settings in JSON files:
    - Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)
    - Project: .mbasic/settings.json in project directory
    """

    def __init__(self, project_dir: Optional[str] = None):
        """Initialize file backend.

        Args:
            project_dir: Optional project directory for project-level settings
        """
        self.project_dir = project_dir
        self.global_settings_path = self._get_global_settings_path()
        self.project_settings_path = self._get_project_settings_path()

    def _get_global_settings_path(self) -> Path:
        """Get path to global settings file."""
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            base_dir = Path(appdata) / 'mbasic'
        else:  # Linux/Mac
            base_dir = Path.home() / '.mbasic'

        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / 'settings.json'

    def _get_project_settings_path(self) -> Optional[Path]:
        """Get path to project settings file."""
        if not self.project_dir:
            return None

        project_dir = Path(self.project_dir)
        settings_dir = project_dir / '.mbasic'
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir / 'settings.json'

    def load_global(self) -> Dict[str, Any]:
        """Load global settings from file."""
        try:
            if self.global_settings_path.exists():
                with open(self.global_settings_path, 'r') as f:
                    data = json.load(f)
                    return data.get('settings', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load global settings: {e}")
        return {}

    def save_global(self, settings: Dict[str, Any]) -> None:
        """Save global settings to file."""
        data = {
            'version': '1.0',
            'settings': settings
        }
        try:
            with open(self.global_settings_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save global settings: {e}")

    def load_project(self) -> Dict[str, Any]:
        """Load project settings from file."""
        if not self.project_settings_path:
            return {}

        try:
            if self.project_settings_path.exists():
                with open(self.project_settings_path, 'r') as f:
                    data = json.load(f)
                    return data.get('settings', {})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load project settings: {e}")
        return {}

    def save_project(self, settings: Dict[str, Any]) -> None:
        """Save project settings to file."""
        if not self.project_settings_path:
            print("Warning: No project directory set, cannot save project settings")
            return

        data = {
            'version': '1.0',
            'settings': settings
        }
        try:
            with open(self.project_settings_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save project settings: {e}")


class RedisSettingsBackend(SettingsBackend):
    """Redis-based per-session settings storage.

    Stores settings in Redis with per-session isolation:
    - Key format: nicegui:settings:{session_id}
    - Each session has independent settings
    - Optionally initialized from default file-based settings (if provided and not already in Redis)
    - No disk writes in this mode (Redis is the only storage)
    """

    def __init__(self, redis_client, session_id: str, default_settings: Optional[Dict[str, Any]] = None):
        """Initialize Redis backend.

        Args:
            redis_client: Redis client instance (from nicegui or redis-py)
            session_id: Unique session identifier
            default_settings: Default settings loaded from disk (optional)
        """
        self.redis = redis_client
        self.session_id = session_id
        self.redis_key = f"nicegui:settings:{session_id}"

        # Initialize with defaults if not already in Redis
        if default_settings and not self._exists():
            self.save_global(default_settings)

    def _exists(self) -> bool:
        """Check if settings exist in Redis for this session."""
        try:
            return self.redis.exists(self.redis_key)
        except Exception:
            return False

    def _get_data(self) -> Dict[str, Any]:
        """Get settings data from Redis."""
        try:
            data = self.redis.get(self.redis_key)
            if data:
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)
        except Exception as e:
            print(f"Warning: Could not load settings from Redis: {e}")
        return {}

    def _set_data(self, settings: Dict[str, Any]) -> None:
        """Set settings data in Redis."""
        try:
            data = json.dumps(settings)
            # Set with TTL of 24 hours (matches NiceGUI session expiry)
            self.redis.setex(self.redis_key, 86400, data)
        except Exception as e:
            print(f"Error: Could not save settings to Redis: {e}")

    def load_global(self) -> Dict[str, Any]:
        """Load settings from Redis for this session.

        Note: In Redis mode, 'global' and 'project' are the same -
        all settings are per-session.
        """
        return self._get_data()

    def save_global(self, settings: Dict[str, Any]) -> None:
        """Save settings to Redis for this session."""
        self._set_data(settings)

    def load_project(self) -> Dict[str, Any]:
        """Load project settings (returns empty in Redis mode).

        In Redis mode, all settings are session-scoped, not project-scoped.
        """
        return {}

    def save_project(self, settings: Dict[str, Any]) -> None:
        """Save project settings (no-op in Redis mode).

        In Redis mode, all settings are session-scoped, not project-scoped.
        """
        pass  # Project settings not supported in Redis mode


def create_settings_backend(session_id: Optional[str] = None,
                           project_dir: Optional[str] = None) -> SettingsBackend:
    """Factory function to create appropriate settings backend.

    Args:
        session_id: Session ID for Redis mode (required if NICEGUI_REDIS_URL is set)
        project_dir: Project directory for file mode

    Returns:
        SettingsBackend instance (File or Redis based on environment)
    """
    import os

    redis_url = os.environ.get('NICEGUI_REDIS_URL')

    if redis_url and session_id:
        # Redis mode: per-session settings
        try:
            import redis

            # Create Redis client
            redis_client = redis.from_url(redis_url, decode_responses=True)

            # Load default settings from disk
            file_backend = FileSettingsBackend(project_dir)
            default_settings = file_backend.load_global()

            # Create Redis backend with defaults
            return RedisSettingsBackend(redis_client, session_id, default_settings)

        except ImportError:
            print("Warning: redis package not installed, falling back to file backend")
            return FileSettingsBackend(project_dir)
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}, falling back to file backend")
            return FileSettingsBackend(project_dir)
    else:
        # File mode: traditional filesystem storage
        return FileSettingsBackend(project_dir)
