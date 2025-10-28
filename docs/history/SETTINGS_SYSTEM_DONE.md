# Settings System for MBASIC Interpreter

✅ **Status:** COMPLETED (v1.0.104-105)

**Priority:** HIGH - Required for case-preserving variables and other configurable behaviors

## Problem

The MBASIC interpreter currently has no settings/configuration system. As features are added that benefit from user configuration (like case-preserving variables), we need a unified way to manage user preferences.

## Immediate Need: Variable Case Conflict Handling

The case-preserving variables feature needs a setting to control how conflicts are handled when the same variable appears with different cases.

**Example conflict:**
```basic
10 TargetAngle = 45
20 targetangle = 50
30 TARGETANGLE = 55
```

### Proposed Setting: `variable_case_conflict`

**Option 1: `first_wins` (DEFAULT)**
- First occurrence sets canonical case: `TargetAngle`
- All subsequent uses (regardless of case) update same variable
- When saved from AST, all variables use first case
- Silent behavior - no errors or warnings

**Option 2: `error`**
- First occurrence sets canonical case: `TargetAngle`
- Subsequent different case triggers error
- User must fix inconsistency or decide to change setting
- Error message: `"Variable 'targetangle' conflicts with existing 'TargetAngle' at line 10"`

**Option 3: `prefer_upper`**
- Track all case variations used
- On conflict, prefer uppercase characters
- `TargetAngle` + `targetangle` + `TARGETANGLE` → `TARGETANGLE`
- When saved from AST, uses uppercase-preferred version

**Option 4: `prefer_lower`**
- Track all case variations used
- On conflict, prefer lowercase characters
- `TargetAngle` + `targetangle` + `TARGETANGLE` → `targetangle`
- When saved from AST, uses lowercase-preferred version

**Option 5: `prefer_mixed`**
- Track all case variations used
- On conflict, prefer mixed case (camelCase/PascalCase)
- `TargetAngle` + `targetangle` + `TARGETANGLE` → `TargetAngle`
- Heuristic: prefer version with both upper and lower case

## Settings System Requirements

### Core Features

1. **Persistent storage** - Settings saved between sessions
2. **Multiple scopes** - Global, per-project, per-file
3. **Type safety** - Validate setting values
4. **Documentation** - Help text for each setting
5. **UI integration** - Easy to view/change in all UIs
6. **Defaults** - Sensible defaults that work out-of-box

### Setting Types

```python
class SettingType:
    BOOLEAN = "boolean"      # True/False
    INTEGER = "integer"      # Numeric value
    STRING = "string"        # Text value
    ENUM = "enum"           # Choice from list
    COLOR = "color"         # Color value
    PATH = "path"           # File/directory path
```

### Setting Scopes

```python
class SettingScope:
    GLOBAL = "global"       # ~/.mbasic/settings.json
    PROJECT = "project"     # .mbasic/settings.json in project dir
    FILE = "file"          # Per-file metadata
```

## Proposed Settings Structure

### Configuration File Format

**JSON format (simple, widely supported):**

```json
{
  "version": "1.0",
  "settings": {
    "editor": {
      "auto_number": true,
      "auto_number_step": 10,
      "tab_size": 4,
      "show_line_numbers": true
    },
    "interpreter": {
      "strict_mode": false,
      "max_execution_time": 30,
      "debug_mode": false
    },
    "variables": {
      "case_conflict": "first_wins",
      "show_types_in_window": true,
      "preserve_def_types": true
    },
    "ui": {
      "theme": "default",
      "font_size": 12,
      "color_scheme": "classic"
    }
  }
}
```

### Setting Definitions

```python
SETTING_DEFINITIONS = {
    "variables.case_conflict": {
        "type": SettingType.ENUM,
        "default": "first_wins",
        "choices": ["first_wins", "error", "prefer_upper", "prefer_lower", "prefer_mixed"],
        "description": "How to handle variable name case conflicts",
        "help": """
Controls what happens when the same variable appears with different cases.

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
        "scope": SettingScope.GLOBAL,
    },

    "editor.auto_number": {
        "type": SettingType.BOOLEAN,
        "default": True,
        "description": "Automatically number typed lines",
        "help": "When enabled, lines typed without numbers get auto-numbered",
        "scope": SettingScope.PROJECT,
    },

    "editor.auto_number_step": {
        "type": SettingType.INTEGER,
        "default": 10,
        "min": 1,
        "max": 1000,
        "description": "Line number increment for auto-numbering",
        "help": "Step size between auto-numbered lines (default: 10)",
        "scope": SettingScope.PROJECT,
    },
}
```

## Implementation Plan

### Phase 1: Core Settings Infrastructure

**Files to create:**
- `src/settings.py` - Settings manager
- `src/settings_definitions.py` - Setting definitions and defaults
- `~/.mbasic/settings.json` - User's global settings

**Core classes:**
```python
class SettingsManager:
    def __init__(self):
        self.global_settings = {}
        self.project_settings = {}
        self.load()

    def get(self, key: str, default=None):
        """Get setting value with scope precedence"""
        # Check: file -> project -> global -> default
        pass

    def set(self, key: str, value, scope=SettingScope.GLOBAL):
        """Set setting value"""
        pass

    def load(self):
        """Load settings from disk"""
        pass

    def save(self):
        """Save settings to disk"""
        pass

    def validate(self, key: str, value) -> bool:
        """Validate setting value against definition"""
        pass

    def get_definition(self, key: str) -> dict:
        """Get setting definition"""
        pass
```

### Phase 2: UI Integration

**Add settings UI to each backend:**

**CLI UI:**
- `SET <setting> <value>` - Set a setting
- `SHOW SETTINGS` - List all settings
- `HELP SET` - Show setting help

**Curses UI:**
- `Ctrl+,` - Open settings panel
- Navigate with arrow keys
- Edit with Enter

**TK UI:**
- Menu: `Edit > Settings...`
- Dialog with tabs for categories
- Search/filter settings

### Phase 3: Variable Case Conflict Implementation

**Update case-preserving variables to use setting:**

```python
def _set_variable(self, name: str, value):
    """Set variable with case conflict handling"""
    normalized = name.lower()
    conflict_mode = settings.get("variables.case_conflict")

    if normalized in self.variables:
        existing_name = self.variables[normalized]["name"]

        if existing_name != name:
            # Case conflict detected
            if conflict_mode == "first_wins":
                # Keep existing case, update value
                name = existing_name

            elif conflict_mode == "error":
                raise VariableCaseConflictError(
                    f"Variable '{name}' conflicts with existing '{existing_name}'"
                )

            elif conflict_mode == "prefer_upper":
                # Choose version with more uppercase
                name = _prefer_uppercase(existing_name, name)

            elif conflict_mode == "prefer_lower":
                # Choose version with more lowercase
                name = _prefer_lowercase(existing_name, name)

            elif conflict_mode == "prefer_mixed":
                # Choose mixed case version
                name = _prefer_mixed_case(existing_name, name)

    self.variables[normalized] = {"name": name, "value": value}
```

### Phase 4: Additional Settings

**Editor settings:**
- `editor.auto_number` - Enable/disable auto-numbering
- `editor.auto_number_step` - Line number increment
- `editor.tab_size` - Tab width
- `editor.show_line_numbers` - Show line numbers in editor

**Interpreter settings:**
- `interpreter.strict_mode` - Strict error checking
- `interpreter.max_execution_time` - Timeout for programs
- `interpreter.debug_mode` - Enable debug output

**UI settings:**
- `ui.theme` - Color theme
- `ui.font_size` - UI font size
- `ui.show_variable_types` - Show type suffixes in variable window

## File Locations

### Global Settings
- **Linux/Mac:** `~/.mbasic/settings.json`
- **Windows:** `%APPDATA%\mbasic\settings.json`

### Project Settings
- `.mbasic/settings.json` in project root

### Per-File Settings
- Stored in program file comments or separate metadata file

## Settings UI Mockup

### CLI UI
```
MBASIC> SHOW SETTINGS
Global Settings:
  variables.case_conflict = first_wins
  editor.auto_number = true
  editor.auto_number_step = 10
  ui.theme = default

MBASIC> SET variables.case_conflict error
Setting 'variables.case_conflict' = error

MBASIC> HELP SET variables.case_conflict
variables.case_conflict (enum)
  Default: first_wins
  Choices: first_wins, error, prefer_upper, prefer_lower, prefer_mixed

  Controls what happens when the same variable appears with different cases.

  - first_wins: First occurrence sets case (default, silent)
  - error: Flag conflicts as errors requiring user intervention
  - prefer_upper: Choose version with most uppercase letters
  - prefer_lower: Choose version with most lowercase letters
  - prefer_mixed: Prefer mixed case (camelCase/PascalCase)
```

### TK UI
```
┌─ Settings ─────────────────────────────┐
│ Search: [____________]                  │
├─────────────────────────────────────────┤
│ ┌──── Categories ────┐ ┌─── Values ───┐│
│ │ • Editor           │ │              ││
│ │   Variables        │ │ Variable     ││
│ │   Interpreter      │ │ Case         ││
│ │   UI               │ │ Conflicts:   ││
│ └────────────────────┘ │              ││
│                        │ ○ First Wins ││
│                        │ ○ Error      ││
│                        │ ○ Upper      ││
│                        │ ○ Lower      ││
│                        │ ○ Mixed      ││
│                        │              ││
│                        │ [?] Help     ││
│                        └──────────────┘│
├─────────────────────────────────────────┤
│              [OK]  [Cancel]  [Apply]    │
└─────────────────────────────────────────┘
```

## Testing Plan

### Unit Tests
- Test setting validation
- Test scope precedence (file > project > global)
- Test load/save round-trip
- Test default values

### Integration Tests
- Test settings UI in each backend
- Test variable case conflict modes
- Test settings persistence
- Test invalid setting values

### User Testing
- Test discoverability (can users find settings?)
- Test usability (can users change settings easily?)
- Test help text clarity

## Migration Plan

**Step 1: Create settings infrastructure**
- Implement SettingsManager class
- Define core settings
- Add global settings file

**Step 2: Add CLI UI**
- `SET` command
- `SHOW SETTINGS` command
- `HELP SET` command

**Step 3: Add variable case conflict setting**
- Implement conflict modes
- Update variable storage
- Add tests

**Step 4: Add other UI backends**
- Curses settings panel
- TK settings dialog
- Visual settings (future)

**Step 5: Add more settings**
- Editor settings
- Interpreter settings
- UI settings

## Benefits

1. **User control** - Users can customize behavior
2. **Consistency** - Single source of truth for configuration
3. **Discoverability** - Settings UI makes features visible
4. **Documentation** - Help text explains each setting
5. **Extensibility** - Easy to add new settings

## Related Features

- **Case-preserving variables** - Needs `variable_case_conflict` setting
- **Auto-numbering** - Could use `editor.auto_number` setting
- **Pretty printer** - Could use spacing/formatting settings
- **Debug mode** - Could use `interpreter.debug_mode` setting

## Success Criteria

- ✅ Settings persist between sessions
- ✅ Settings UI works in all backends (CLI, curses, TK)
- ✅ Variable case conflict modes work correctly
- ✅ Help text is clear and useful
- ✅ Default settings work out-of-box
- ✅ Settings validate on set (catch invalid values)

## Notes

- Settings system should be simple and lightweight
- Avoid over-engineering - start with JSON files
- Can migrate to more sophisticated system later if needed
- Settings should be backward compatible (old programs still work)
- Consider environment variable overrides for testing

## Historical Context

Configuration systems have evolved:
- **1980s:** Hard-coded defaults, maybe a .rc file
- **1990s:** .ini files, registry (Windows)
- **2000s:** XML configuration files
- **2010s:** JSON, YAML, TOML
- **2020s:** JSON/TOML with schema validation

We choose JSON for:
- Wide support in Python (standard library)
- Human-readable and editable
- Schema validation available
- IDE support (autocomplete, validation)
