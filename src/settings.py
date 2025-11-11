"""Settings manager for MBASIC interpreter.

Handles loading, saving, and accessing user settings with scope precedence.
Supports global settings and project settings:
- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)
- Project: .mbasic/settings.json in project directory
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .settings_definitions import (
    SETTING_DEFINITIONS,
    SettingDefinition,
    SettingScope,
    get_definition,
    validate_value,
)
from .settings_backend import SettingsBackend, FileSettingsBackend


class SettingsManager:
    """Manages user settings with scope precedence.

    Precedence: project > global > default

    Note: File-level settings (per-file settings) are FULLY IMPLEMENTED for in-memory use.
    The file_settings dict can be set/retrieved programmatically via set(key, value, scope=SettingScope.FILE)
    and get(key, scope=SettingScope.FILE). However, persistence is NOT implemented - load() doesn't populate
    it from disk and save() doesn't persist it to disk. No UI/command interface exists. When persistence is added,
    these in-memory operations will automatically work with the persisted data.
    """

    def __init__(self, project_dir: Optional[str] = None, backend: Optional[SettingsBackend] = None):
        """Initialize settings manager.

        Args:
            project_dir: Optional project directory for project-level settings
            backend: Optional settings backend (defaults to FileSettingsBackend)
        """
        self.project_dir = project_dir
        self.global_settings: Dict[str, Any] = {}
        self.project_settings: Dict[str, Any] = {}
        self.file_settings: Dict[str, Any] = {}  # RESERVED FOR FUTURE USE: per-file settings (not persisted)

        # Settings backend (file or Redis)
        if backend is None:
            backend = FileSettingsBackend(project_dir)
        self.backend = backend

        # Paths (for backward compatibility, may not be used with Redis backend)
        self.global_settings_path = getattr(backend, 'global_settings_path', None)
        self.project_settings_path = getattr(backend, 'project_settings_path', None)

        # Load settings from backend
        self.load()

    def _get_global_settings_path(self) -> Path:
        """Get path to global settings file.

        Note: This method is not called directly by SettingsManager. Instead, it is called by
        FileSettingsBackend.__init__() to compute paths. The __init__ method retrieves paths from
        backend.global_settings_path for backward compatibility. This method is kept separate for
        potential future use or manual path queries by external code.
        """
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            base_dir = Path(appdata) / 'mbasic'
        else:  # Linux/Mac
            base_dir = Path.home() / '.mbasic'

        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / 'settings.json'

    def _get_project_settings_path(self) -> Optional[Path]:
        """Get path to project settings file.

        Note: This method is not called directly by SettingsManager. Instead, it is called by
        FileSettingsBackend.__init__() to compute paths. The __init__ method retrieves paths from
        backend.project_settings_path for backward compatibility. This method is kept separate for
        potential future use or manual path queries by external code.
        """
        if not self.project_dir:
            return None

        project_dir = Path(self.project_dir)
        settings_dir = project_dir / '.mbasic'
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir / 'settings.json'

    def load(self):
        """Load settings from backend (file or Redis).

        This method delegates loading to the backend, which returns settings dicts.
        The backend determines the format (flat vs nested) based on what was saved.
        Internal representation is flexible: _get_from_dict() handles both flat keys like
        'auto_number' and nested dicts like {'editor': {'auto_number': True}}.
        Settings loaded from disk remain flat; settings modified via set() become nested; both work.
        """
        # Load settings from backend (backend handles format/storage details)
        self.global_settings = self.backend.load_global()
        self.project_settings = self.backend.load_project()

    def save(self, scope: SettingScope = SettingScope.GLOBAL):
        """Save settings to disk.

        Args:
            scope: Which scope to save (GLOBAL or PROJECT)
        """
        if scope == SettingScope.GLOBAL:
            self._save_global()
        elif scope == SettingScope.PROJECT:
            self._save_project()

    def _save_global(self):
        """Save global settings via backend"""
        flattened = self._flatten_settings(self.global_settings)
        self.backend.save_global(flattened)

    def _save_project(self):
        """Save project settings via backend"""
        flattened = self._flatten_settings(self.project_settings)
        self.backend.save_project(flattened)

    def _flatten_settings(self, settings_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested settings dict for JSON storage.

        Converts: {'editor': {'auto_number': True}}
        To: {'auto_number': True}
        """
        flat = {}
        for key, value in settings_dict.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    flat[f"{key}.{subkey}"] = subvalue
            else:
                flat[key] = value
        return flat

    def _unflatten_settings(self, flat_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Unflatten settings dict for internal storage.

        Converts: {'auto_number': True}
        To: {'editor': {'auto_number': True}}
        """
        nested = {}
        for key, value in flat_dict.items():
            if '.' in key:
                parts = key.split('.', 1)
                category = parts[0]
                subkey = parts[1]
                if category not in nested:
                    nested[category] = {}
                nested[category][subkey] = value
            else:
                nested[key] = value
        return nested

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get setting value with scope precedence.

        In normal usage (file settings not populated), precedence order is:
        project > global > definition default > provided default

        Note: The implementation also supports file-level settings (highest precedence: file > project > global...),
        but these are not populated in normal usage. File settings can be set programmatically via
        set(key, value, scope=SettingScope.FILE) but have no persistence layer. The file_settings dict
        is checked first in the precedence order for theoretical support of per-file overrides.

        Args:
            key: Setting key (e.g., 'case_conflict')
            default: Optional default value if setting not found

        Returns:
            Setting value
        """
        # Check file settings (not yet implemented)
        if key in self.file_settings:
            return self.file_settings[key]

        # Check project settings
        value = self._get_from_dict(key, self.project_settings)
        if value is not None:
            return value

        # Check global settings
        value = self._get_from_dict(key, self.global_settings)
        if value is not None:
            return value

        # Check definition default
        definition = get_definition(key)
        if definition:
            return definition.default

        # Use provided default
        return default

    def _get_from_dict(self, key: str, settings_dict: Dict[str, Any]) -> Optional[Any]:
        """Get value from nested settings dict.

        Args:
            key: Dotted key like 'auto_number'
            settings_dict: Nested dict like {'editor': {'auto_number': True}}

        Returns:
            Value or None if not found
        """
        if '.' in key:
            parts = key.split('.', 1)
            category = parts[0]
            subkey = parts[1]
            if category in settings_dict and isinstance(settings_dict[category], dict):
                return settings_dict[category].get(subkey)
        return settings_dict.get(key)

    def set(self, key: str, value: Any, scope: SettingScope = SettingScope.GLOBAL):
        """Set setting value.

        Args:
            key: Setting key (e.g., 'case_conflict')
            value: New value
            scope: Which scope to set (GLOBAL or PROJECT)

        Raises:
            ValueError: If value is invalid for this setting
        """
        # Validate value
        if not validate_value(key, value):
            definition = get_definition(key)
            if definition:
                raise ValueError(
                    f"Invalid value for '{key}': {value}\n"
                    f"Expected type: {definition.type.value}\n"
                    f"Choices: {definition.choices if definition.choices else 'N/A'}"
                )
            else:
                raise ValueError(f"Unknown setting: '{key}'")

        # Set value in appropriate scope
        if scope == SettingScope.GLOBAL:
            self._set_in_dict(key, value, self.global_settings)
        elif scope == SettingScope.PROJECT:
            self._set_in_dict(key, value, self.project_settings)
        elif scope == SettingScope.FILE:
            self.file_settings[key] = value

    def _set_in_dict(self, key: str, value: Any, settings_dict: Dict[str, Any]):
        """Set value in nested settings dict.

        Args:
            key: Dotted key like 'auto_number'
            value: Value to set
            settings_dict: Nested dict to modify
        """
        if '.' in key:
            parts = key.split('.', 1)
            category = parts[0]
            subkey = parts[1]
            if category not in settings_dict:
                settings_dict[category] = {}
            settings_dict[category][subkey] = value
        else:
            settings_dict[key] = value

    def get_definition(self, key: str) -> Optional[SettingDefinition]:
        """Get setting definition.

        Args:
            key: Setting key

        Returns:
            SettingDefinition or None if not found
        """
        return get_definition(key)

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings with values (merged across scopes).

        Returns:
            Dict of setting key -> current value
        """
        result = {}
        for key in SETTING_DEFINITIONS:
            result[key] = self.get(key)
        return result

    def reset_to_defaults(self, scope: SettingScope = SettingScope.GLOBAL):
        """Reset settings to defaults.

        Args:
            scope: Which scope to reset
        """
        if scope == SettingScope.GLOBAL:
            self.global_settings = {}
        elif scope == SettingScope.PROJECT:
            self.project_settings = {}
        elif scope == SettingScope.FILE:
            self.file_settings = {}


# Global settings manager instance (initialized when first needed)
_global_settings_manager: Optional[SettingsManager] = None


def get_settings_manager(project_dir: Optional[str] = None) -> SettingsManager:
    """Get global settings manager instance.

    Args:
        project_dir: Optional project directory for project-level settings

    Returns:
        SettingsManager instance
    """
    global _global_settings_manager
    if _global_settings_manager is None or project_dir is not None:
        _global_settings_manager = SettingsManager(project_dir=project_dir)
    return _global_settings_manager


# Convenience functions
def get(key: str, default: Optional[Any] = None) -> Any:
    """Get setting value (convenience function)."""
    return get_settings_manager().get(key, default)


def set(key: str, value: Any, scope: SettingScope = SettingScope.GLOBAL):
    """Set setting value (convenience function)."""
    get_settings_manager().set(key, value, scope)


def save(scope: SettingScope = SettingScope.GLOBAL):
    """Save settings (convenience function)."""
    get_settings_manager().save(scope)
