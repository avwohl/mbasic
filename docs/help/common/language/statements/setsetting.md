---
category: system
description: Configure interpreter settings at runtime
keywords: ['set', 'setting', 'configure', 'option', 'preference', 'runtime']
syntax: SETSETTING setting.name value
title: SETSETTING
type: statement
related: ['showsettings', 'helpsetting']
---

# SETSETTING

## Syntax

```basic
SETSETTING setting.name value
```

**Versions:** MBASIC Extension

## Purpose

To configure interpreter settings and options at runtime.

## Remarks

SETSETTING allows programs to dynamically configure interpreter behavior by modifying settings. The setting name uses dotted notation (e.g., display.width, editor.tab_size) without quotes.

Settings can control:
- Display and output formatting
- Editor behavior
- Runtime options
- UI preferences

Settings persist for the current session or can be saved to configuration files depending on the setting scope.

## Example

```basic
SETSETTING display.width 80
SETSETTING editor.tab_size 4

10 SETSETTING interpreter.strict_mode 1
20 PRINT "Strict mode enabled"

100 INPUT "Tab size"; T
110 SETSETTING editor.tab_size T
```

## Notes

- This is a modern extension not present in original MBASIC 5.21
- Available settings are implementation-specific
- Use SHOWSETTINGS to list all available settings
- Use HELPSETTING "name" to get help on a specific setting
- Invalid setting names produce an error

## See Also
- [SHOWSETTINGS](showsettings.md) - Display current interpreter settings
- [HELPSETTING](helpsetting.md) - Display help for a specific setting
- [LIMITS](limits.md) - Display resource usage and interpreter limits
- [WIDTH](width.md) - To set the printed line width in number of characters for the terminal or line printer
