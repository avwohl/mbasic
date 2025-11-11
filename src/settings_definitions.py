"""Settings definitions for MBASIC interpreter.

This module defines all available settings, their types, defaults, and validation rules.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class SettingType(Enum):
    """Types of settings supported"""
    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"
    ENUM = "enum"
    COLOR = "color"
    PATH = "path"


class SettingScope(Enum):
    """Scope/precedence of settings"""
    GLOBAL = "global"      # ~/.mbasic/settings.json
    PROJECT = "project"    # .mbasic/settings.json in project dir
    FILE = "file"          # Per-file metadata (RESERVED FOR FUTURE USE - not currently implemented)


class SettingDefinition:
    """Definition of a single setting"""

    def __init__(self,
                 key: str,
                 type: SettingType,
                 default: Any,
                 description: str,
                 help_text: str = "",
                 scope: SettingScope = SettingScope.GLOBAL,
                 choices: Optional[List[Any]] = None,
                 min_value: Optional[int] = None,
                 max_value: Optional[int] = None):
        self.key = key
        self.type = type
        self.default = default
        self.description = description
        self.help_text = help_text
        self.scope = scope
        self.choices = choices or []
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> bool:
        """Validate a value against this setting's constraints"""
        if self.type == SettingType.BOOLEAN:
            return isinstance(value, bool)

        elif self.type == SettingType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            return True

        elif self.type == SettingType.STRING:
            return isinstance(value, str)

        elif self.type == SettingType.ENUM:
            return value in self.choices

        elif self.type == SettingType.COLOR:
            # Simple validation - hex color or named color
            if isinstance(value, str):
                return value.startswith('#') or value.isalpha()
            return False

        elif self.type == SettingType.PATH:
            return isinstance(value, str)

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert definition to dictionary for serialization"""
        return {
            'type': self.type.value,
            'default': self.default,
            'description': self.description,
            'help': self.help_text,
            'scope': self.scope.value,
            'choices': self.choices,
            'min': self.min_value,
            'max': self.max_value,
        }


# All available settings
# Note: Setting keys no longer use category prefixes (editor., keywords., variables.)
# The old format is maintained for backward compatibility in loading
SETTING_DEFINITIONS: Dict[str, SettingDefinition] = {
    # Variable settings
    "case_conflict": SettingDefinition(
        key="case_conflict",
        type=SettingType.ENUM,
        default="first_wins",
        choices=["first_wins", "error", "upper", "lower"],
        description="How to handle variable name case conflicts",
        help_text="When same var has different cases: first_wins (order), error (flag), upper/lower (style)",
        scope=SettingScope.GLOBAL,
    ),

    "show_types_in_window": SettingDefinition(
        key="show_types_in_window",
        type=SettingType.BOOLEAN,
        default=True,
        description="Show type suffixes ($, %, !, #) in variable window",
        help_text="When enabled, variable window shows types like X%, Y$, Z#",
        scope=SettingScope.GLOBAL,
    ),

    # Keyword settings
    "case_style": SettingDefinition(
        key="case_style",
        type=SettingType.ENUM,
        default="force_lower",
        choices=["force_lower", "force_upper", "force_capitalize"],
        description="How to handle keyword case in source code",
        help_text="lowercase (MBASIC 5.21), UPPERCASE (classic), or Capitalize (modern)",
        scope=SettingScope.PROJECT,
    ),

    # Editor settings
    "auto_number": SettingDefinition(
        key="auto_number",
        type=SettingType.BOOLEAN,
        default=True,
        description="Automatically number typed lines",
        help_text="When enabled, lines typed without numbers get auto-numbered",
        scope=SettingScope.PROJECT,
    ),

    "auto_number_start": SettingDefinition(
        key="auto_number_start",
        type=SettingType.INTEGER,
        default=10,
        min_value=1,
        max_value=65529,
        description="Starting line number for auto-numbering",
        help_text="First line number when auto-numbering (10, 100, 1000, etc.)",
        scope=SettingScope.PROJECT,
    ),

    "auto_number_step": SettingDefinition(
        key="auto_number_step",
        type=SettingType.INTEGER,
        default=10,
        min_value=1,
        max_value=1000,
        description="Line number increment for auto-numbering",
        help_text="Step size between auto-numbered lines (default: 10)",
        scope=SettingScope.PROJECT,
    ),

    # Note: editor.tab_size setting not included - BASIC uses line numbers for program structure,
    # not indentation, so tab size is not a meaningful setting for BASIC source code

    # Note: Line numbers are always shown - they're fundamental to BASIC!
    # editor.show_line_numbers setting not included - makes no sense for BASIC

    # Note: Additional settings may be added in future versions
}


def get_definition(key: str) -> Optional[SettingDefinition]:
    """Get definition for a setting by key"""
    return SETTING_DEFINITIONS.get(key)


def get_all_definitions() -> Dict[str, SettingDefinition]:
    """Get all setting definitions"""
    return SETTING_DEFINITIONS.copy()


def get_default_value(key: str) -> Any:
    """Get default value for a setting"""
    definition = get_definition(key)
    return definition.default if definition else None


def validate_value(key: str, value: Any) -> bool:
    """Validate a value for a setting"""
    definition = get_definition(key)
    if not definition:
        return False
    return definition.validate(value)
