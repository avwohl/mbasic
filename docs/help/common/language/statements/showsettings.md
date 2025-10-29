---
category: system
description: Display current interpreter settings
keywords:
- show
- settings
- display
- list
- configuration
- options
syntax: "SHOW SETTINGS [\"pattern\"]"
title: SHOW SETTINGS
type: statement
related: [setsetting, helpsetting]
---

# SHOW SETTINGS

## Syntax

```basic
SHOW SETTINGS ["pattern"]
```

**Versions:** MBASIC Extension

## Purpose

To display current interpreter settings and their values.

## Remarks

SHOW SETTINGS lists all interpreter settings and their current values. An optional pattern string can filter the display to show only matching settings.

The display typically includes:
- Setting name (in dotted notation)
- Current value
- Setting scope (session, user, system)
- Brief description (if available)

If a pattern is provided, only settings whose names contain the pattern string are shown.

## Example

```basic
SHOW SETTINGS
' Lists all settings

SHOW SETTINGS "display"
' Shows only display-related settings

10 SHOW SETTINGS "editor"
20 INPUT "Change a setting (Y/N)"; A$
```

## Notes

- This is a modern extension not present in original MBASIC 5.21
- Pattern matching is case-insensitive
- Settings are organized by category (display, editor, runtime, etc.)
- Some settings may be read-only

## See Also

- [SET](setsetting.md) - Modify a setting
- [HELP SET](helpsetting.md) - Get help on a specific setting
