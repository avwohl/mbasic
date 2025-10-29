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
    FILE = "file"          # Per-file metadata


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
SETTING_DEFINITIONS: Dict[str, SettingDefinition] = {
    # Variable settings
    "variables.case_conflict": SettingDefinition(
        key="variables.case_conflict",
        type=SettingType.ENUM,
        default="first_wins",
        choices=["first_wins", "error", "prefer_upper", "prefer_lower", "prefer_mixed"],
        description="How to handle variable name case conflicts",
        help_text="""Controls what happens when the same variable appears with different cases.

- first_wins: First occurrence sets case (default, silent)
- error: Flag conflicts as errors requiring user intervention
- prefer_upper: Choose version with most uppercase letters
- prefer_lower: Choose version with most lowercase letters
- prefer_mixed: Prefer mixed case (camelCase/PascalCase)

Example:
  10 TargetAngle = 45
  20 targetangle = 50  <- Conflict!

With first_wins: Uses 'TargetAngle' throughout
With error: Shows error, user must fix or change setting
With prefer_upper: Would use 'TARGETANGLE' if used later
""",
        scope=SettingScope.GLOBAL,
    ),

    "variables.show_types_in_window": SettingDefinition(
        key="variables.show_types_in_window",
        type=SettingType.BOOLEAN,
        default=True,
        description="Show type suffixes ($, %, !, #) in variable window",
        help_text="When enabled, variable window shows types like X%, Y$, Z#",
        scope=SettingScope.GLOBAL,
    ),

    # Keyword settings
    "keywords.case_style": SettingDefinition(
        key="keywords.case_style",
        type=SettingType.ENUM,
        default="force_lower",
        choices=["force_lower", "force_upper", "force_capitalize"],
        description="How to handle keyword case in source code",
        help_text="""Controls how keywords are displayed.

- force_lower: Convert all keywords to lowercase (default, MBASIC 5.21 style)
- force_upper: Convert all keywords to UPPERCASE (classic BASIC style)
- force_capitalize: Capitalize keywords (Print, For, If - modern readable style)

Example with force_upper:
  10 print "hello"  -> 10 PRINT "hello"
  20 Print "world"  -> 20 PRINT "world"

Example with force_capitalize:
  10 PRINT "hello"  -> 10 Print "hello"
  20 print "world"  -> 20 Print "world"

Example with first_wins:
  10 Print "hello"  -> 10 Print "hello"
  20 PRINT "world"  -> 20 Print "world"  (uses first case)

Example with error:
  10 Print "hello"
  20 PRINT "world"  -> ERROR: Keyword case conflict!
""",
        scope=SettingScope.PROJECT,
    ),

    # Editor settings
    "editor.auto_number": SettingDefinition(
        key="editor.auto_number",
        type=SettingType.BOOLEAN,
        default=True,
        description="Automatically number typed lines",
        help_text="When enabled, lines typed without numbers get auto-numbered",
        scope=SettingScope.PROJECT,
    ),

    "editor.auto_number_step": SettingDefinition(
        key="editor.auto_number_step",
        type=SettingType.INTEGER,
        default=10,
        min_value=1,
        max_value=1000,
        description="Line number increment for auto-numbering",
        help_text="Step size between auto-numbered lines (default: 10)",
        scope=SettingScope.PROJECT,
    ),

    "editor.tab_size": SettingDefinition(
        key="editor.tab_size",
        type=SettingType.INTEGER,
        default=4,
        min_value=1,
        max_value=16,
        description="Tab width in spaces",
        help_text="Number of spaces to use for tab indentation",
        scope=SettingScope.GLOBAL,
    ),

    "editor.show_line_numbers": SettingDefinition(
        key="editor.show_line_numbers",
        type=SettingType.BOOLEAN,
        default=True,
        description="Show line numbers in editor",
        help_text="Display line numbers in the editor gutter",
        scope=SettingScope.GLOBAL,
    ),

    # Interpreter settings
    "interpreter.strict_mode": SettingDefinition(
        key="interpreter.strict_mode",
        type=SettingType.BOOLEAN,
        default=False,
        description="Enable strict error checking",
        help_text="When enabled, additional errors are flagged (undefined variables, etc.)",
        scope=SettingScope.GLOBAL,
    ),

    "interpreter.max_execution_time": SettingDefinition(
        key="interpreter.max_execution_time",
        type=SettingType.INTEGER,
        default=30,
        min_value=1,
        max_value=3600,
        description="Maximum program execution time in seconds",
        help_text="Program will be stopped if it runs longer than this (0 = unlimited)",
        scope=SettingScope.GLOBAL,
    ),

    "interpreter.debug_mode": SettingDefinition(
        key="interpreter.debug_mode",
        type=SettingType.BOOLEAN,
        default=False,
        description="Enable debug output",
        help_text="Show detailed debug information during execution",
        scope=SettingScope.GLOBAL,
    ),

    # UI settings
    "ui.theme": SettingDefinition(
        key="ui.theme",
        type=SettingType.ENUM,
        default="default",
        choices=["default", "dark", "light", "classic"],
        description="Color theme for UI",
        help_text="Choose visual appearance (default, dark, light, classic)",
        scope=SettingScope.GLOBAL,
    ),

    "ui.font_size": SettingDefinition(
        key="ui.font_size",
        type=SettingType.INTEGER,
        default=12,
        min_value=8,
        max_value=32,
        description="UI font size in points",
        help_text="Font size for editor and UI elements",
        scope=SettingScope.GLOBAL,
    ),
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
