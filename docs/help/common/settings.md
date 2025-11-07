---
title: Settings System Overview
type: guide
description: Overview of MBASIC settings and configuration system
keywords: [settings, configuration, preferences, customization]
---

# Settings System Overview

**Note:** The settings system is a **MBASIC Extension** - not present in original MBASIC 5.21. See [MBASIC Extensions](../mbasic/extensions.md) for details.

MBASIC provides a comprehensive settings system that allows you to customize the behavior of the interpreter and editor across all user interfaces.

## What Are Settings?

Settings control various aspects of MBASIC including:

- **Editor behavior** - Auto-numbering, line number increments, tab size
- **Keyword display** - How keywords are capitalized (PRINT vs print vs Print)
- **Variable handling** - How variable name case conflicts are resolved
- **Interpreter behavior** - Strict mode, execution timeouts, debug mode
- **UI preferences** - Themes, font sizes, display options

## Settings Scope

Settings are stored at different scopes with this precedence order:

1. **File scope** (highest priority) - Per-file settings (future feature)
2. **Project scope** - Settings for a specific project directory
3. **Global scope** - User-wide settings
4. **Default values** (lowest priority) - Built-in defaults

## Settings Storage

Settings are stored in JSON format:

- **Linux/Mac**: `~/.mbasic/settings.json`
- **Windows**: `%APPDATA%\mbasic\settings.json`
- **Project**: `.mbasic/settings.json` in project directory

## Available Settings

### Editor Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `editor.auto_number` | boolean | `true` | Enable automatic line numbering |
| `editor.auto_number_step` | integer | `10` | Line number increment (1-1000) |
| `editor.tab_size` | integer | `4` | Tab width in spaces (1-16) |
| `editor.show_line_numbers` | boolean | `true` | Show line numbers in editor gutter |

### Keyword Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `keywords.case_style` | enum | `force_lower` | How to display keywords |

**Choices for `keywords.case_style`:**
- `force_lower` - Convert to lowercase (print, for, if)
- `force_upper` - Convert to UPPERCASE (PRINT, FOR, IF)
- `force_capitalize` - Capitalize (Print, For, If)

### Variable Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `variables.case_conflict` | enum | `first_wins` | How to handle variable name case conflicts |
| `variables.show_types_in_window` | boolean | `true` | Show type suffixes ($, %, !) in variable window |

**Choices for `variables.case_conflict`:**

BASIC is case-insensitive by default (Count = COUNT = count are the same variable). This setting controls which case version is displayed when the same variable is referenced with different cases:

- `first_wins` - First occurrence sets the case (silent) - e.g., if `Count` is used first, all references display as `Count`
- `error` - Flag conflicts as errors - raises error when same variable used with different cases
- `prefer_upper` - Choose most uppercase version - e.g., `COUNT` wins over `Count`
- `prefer_lower` - Choose most lowercase version - e.g., `count` wins over `Count`
- `prefer_mixed` - Prefer mixed case (camelCase) - e.g., `Count` wins over `COUNT`

### Interpreter Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `interpreter.strict_mode` | boolean | `false` | Enable strict error checking |
| `interpreter.max_execution_time` | integer | `30` | Max execution time in seconds (1-3600) |
| `interpreter.debug_mode` | boolean | `false` | Enable debug output |

### UI Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ui.theme` | enum | `default` | Color theme |
| `ui.font_size` | integer | `12` | Font size in points (8-32) |

**Choices for `ui.theme`:**
- `default` - Default color scheme
- `dark` - Dark mode
- `light` - Light mode
- `classic` - Classic BASIC green screen

## Accessing Settings by UI

Settings can be accessed differently depending on which UI you're using:

### CLI (Command Line)
```basic
SHOWSETTINGS                    ' Show all settings
SHOWSETTINGS editor             ' Show editor settings only
SETSETTING editor.auto_number_step 100   ' Change a setting
HELPSETTING editor.auto_number_step      ' Get help for a specific setting
```

**Available commands:**
- [SHOWSETTINGS](language/statements/showsettings.md) - Display current settings
- [SETSETTING](language/statements/setsetting.md) - Change a setting value
- [HELPSETTING](language/statements/helpsetting.md) - Get help for a setting

See: [CLI Settings Commands](../ui/cli/settings.md)

### Curses (Terminal UI)
- Press **Ctrl+,** to open settings widget
- Navigate with arrow keys
- Edit values and press Apply

See: [Curses Settings Widget](../ui/curses/settings.md)

### Tk (Desktop GUI)
- Click **File → Settings** menu
- Navigate tabs for different categories
- Modify values and click OK/Apply

See: [Tk Settings Dialog](../ui/tk/settings.md)

### Web UI
- Click settings icon in navigation
- Use tabbed dialog to modify settings
- Changes save to browser localStorage

See: [Web Settings Dialog](../ui/web/settings.md)

## Common Use Cases

### Change Auto-Numbering

**Problem:** Lines are numbered 10, 20, 30 but you want 100, 200, 300

**Solution:**
```basic
SETSETTING editor.auto_number_step 100
```

Or use Settings Dialog in GUI.

### Force Uppercase Keywords

**Problem:** You prefer classic BASIC style with UPPERCASE keywords

**Solution:**
```basic
SETSETTING keywords.case_style force_upper
```

After this, `print "hello"` displays as `PRINT "hello"` when listed.

### Catch Variable Name Typos

**Problem:** You keep mistyping `TotalCount` as `TotalCont`

**Solution:**
```basic
SETSETTING variables.case_conflict error
```

Now any case mismatch will trigger an error.

### Enable Strict Mode

**Problem:** Want more error checking

**Solution:**
```basic
SETSETTING interpreter.strict_mode true
```

## Settings Validation

All settings are validated when changed:

- **Type checking** - Booleans must be true/false, integers must be numbers
- **Range checking** - Integers have min/max values (e.g., auto_number_step: 1-1000)
- **Enum validation** - Enum settings only accept defined choices

Invalid settings are rejected with an error message.

## Resetting to Defaults

To reset all settings to defaults:

1. **CLI**: Delete `~/.mbasic/settings.json` and restart
2. **GUI**: Use "Reset to Defaults" button in Settings Dialog
3. **Programmatically**: Use SettingsManager.reset_to_defaults() in Python code

## See Also

- [SHOWSETTINGS Statement](language/statements/showsettings.md)
- [SETSETTING Statement](language/statements/setsetting.md)
- [CLI Settings](../ui/cli/settings.md)
- [Curses Settings](../ui/curses/settings.md)
- [Tk Settings](../ui/tk/settings.md)
- [Web Settings](../ui/web/settings.md)
