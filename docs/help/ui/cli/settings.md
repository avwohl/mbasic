---
title: CLI Settings Commands
type: guide
ui: cli
description: How to view and modify settings in CLI mode
keywords: [settings, showsettings, setsetting, configuration, cli]
---

# CLI Settings Commands

In CLI mode, settings are managed through two commands: `SHOWSETTINGS` and `SETSETTING`.

## SHOWSETTINGS Command

Display current settings and their values.

### Syntax

```basic
SHOWSETTINGS [filter]
```

### Parameters

- **filter** (optional) - String to filter settings by category or name

### Examples

```basic
Ok
SHOWSETTINGS
```
Displays all settings:
```
variables.case_conflict = first_wins
variables.show_types_in_window = True
keywords.case_style = force_lower
editor.auto_number = True
editor.auto_number_step = 10
editor.tab_size = 4
editor.show_line_numbers = True
interpreter.strict_mode = False
interpreter.max_execution_time = 30
interpreter.debug_mode = False
ui.theme = default
ui.font_size = 12
```

```basic
Ok
SHOWSETTINGS editor
```
Displays only editor settings:
```
editor.auto_number = True
editor.auto_number_step = 10
editor.tab_size = 4
editor.show_line_numbers = True
```

```basic
Ok
SHOWSETTINGS editor.auto_number_step
```
Displays single setting:
```
editor.auto_number_step = 10
```

## SETSETTING Command

Change a setting value.

### Syntax

```basic
SETSETTING key value
```

### Parameters

- **key** - Setting name (dotted notation, e.g., `editor.auto_number_step`)
- **value** - New value (type must match setting type)

### Examples

#### Change Auto-Number Step

```basic
Ok
SETSETTING editor.auto_number_step 100
Setting 'editor.auto_number_step' = 100
```

Now when you type lines without numbers, they'll increment by 100:
```basic
Ok
PRINT "Hello"
 100  PRINT "Hello"
Ok
PRINT "World"
 200  PRINT "World"
```

#### Enable/Disable Auto-Numbering

```basic
Ok
SETSETTING editor.auto_number false
Setting 'editor.auto_number' = False
```

#### Change Keyword Case Style

```basic
Ok
SETSETTING keywords.case_style force_upper
Setting 'keywords.case_style' = force_upper
Ok
LIST
 100  PRINT "Hello"
 200  PRINT "World"
```

Keywords now display in UPPERCASE.

#### Enable Strict Mode

```basic
Ok
SETSETTING interpreter.strict_mode true
Setting 'interpreter.strict_mode' = True
```

#### Change Variable Case Conflict Policy

```basic
Ok
SETSETTING variables.case_conflict error
Setting 'variables.case_conflict' = error
```

Now variable name case mismatches will trigger errors:
```basic
Ok
10 TotalCount = 0
Ok
20 TotalCont = 1
?Error: Variable case conflict - 'TotalCont' vs 'TotalCount'
```

## Error Handling

### Unknown Setting

```basic
Ok
SETSETTING invalid.key value
?Error: Unknown setting 'invalid.key'
```

### Invalid Value Type

```basic
Ok
SETSETTING editor.auto_number maybe
?Error: Invalid value for 'editor.auto_number': maybe
Expected type: boolean
```

### Out of Range

```basic
Ok
SETSETTING editor.auto_number_step 9999
?Error: Invalid value for 'editor.auto_number_step': 9999
Valid range: 1-1000
```

### Invalid Enum Choice

```basic
Ok
SETSETTING keywords.case_style rainbow
?Error: Invalid value for 'keywords.case_style': rainbow
Choices: force_lower, force_upper, force_capitalize
```

## Settings Persistence

Settings changed with `SETSETTING` are automatically saved to disk and persist across CLI sessions.

**Settings file location:**
- Linux/Mac: `~/.mbasic/settings.json`
- Windows: `%APPDATA%\mbasic\settings.json`

## Available Settings

For a complete list of available settings, see [Settings System Overview](../../common/settings.md).

### Quick Reference

| Category | Settings |
|----------|----------|
| **editor** | auto_number, auto_number_step, tab_size, show_line_numbers |
| **keywords** | case_style |
| **variables** | case_conflict, show_types_in_window |
| **interpreter** | strict_mode, max_execution_time, debug_mode |
| **ui** | theme, font_size |

## Common Workflows

### Customize Auto-Numbering

```basic
' Start at line 1000, increment by 10
SETSETTING editor.auto_number_step 10
SETSETTING editor.auto_number true

' Or start at 100, increment by 100
SETSETTING editor.auto_number_step 100
```

### Configure for Classic BASIC Style

```basic
' Uppercase keywords, start at 10
SETSETTING keywords.case_style force_upper
SETSETTING editor.auto_number_step 10
```

### Enable All Error Checking

```basic
SETSETTING interpreter.strict_mode true
SETSETTING variables.case_conflict error
```

### Quick Settings Check

```basic
' Before starting work, check your settings
SHOWSETTINGS editor
SHOWSETTINGS keywords
```

## Tips

1. **Use tab completion** - In some terminal environments, setting names can be tab-completed

2. **Check before changing** - Use `SHOWSETTINGS <key>` to see current value before changing

3. **Filter by category** - Use `SHOWSETTINGS editor` to see only related settings

4. **Test settings** - After changing, type a few lines to verify the behavior

5. **Document your preferences** - Keep a small .bas file with your preferred SETSETTING commands

Example preferences file:
```basic
' my-preferences.bas
10 REM My preferred MBASIC settings
20 REM
30 SETSETTING editor.auto_number_step 100
40 SETSETTING keywords.case_style force_upper
50 SETSETTING variables.case_conflict error
60 PRINT "Settings applied!"
```

Load with: `RUN "my-preferences.bas"`

## See Also

- [Settings System Overview](../../common/settings.md)
- [SHOWSETTINGS Statement Reference](../../common/language/statements/showsettings.md)
- [SETSETTING Statement Reference](../../common/language/statements/setsetting.md)
- [CLI Index](index.md)

[← Back to CLI Help](index.md)
