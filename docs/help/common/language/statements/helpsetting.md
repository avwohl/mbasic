---
category: system
description: Display help for a specific setting
keywords:
- help
- setting
- documentation
- describe
syntax: "HELP SET \"setting.name\""
title: HELP SET
type: statement
related: [setsetting, showsettings]
---

# HELP SET

## Syntax

```basic
HELP SET "setting.name"
```

**Versions:** MBASIC Extension

## Purpose

To display detailed help information for a specific interpreter setting.

## Remarks

HELP SET displays comprehensive documentation for a named setting, including:
- Full setting name
- Description of what the setting controls
- Valid values and data type
- Default value
- Scope (session, user, system)
- Related settings
- Usage examples

This is useful for understanding what a setting does before changing it, or for discovering the valid values for a setting.

## Example

```basic
HELP SET "display.width"
HELP SET "editor.tabsize"

10 INPUT "Setting name"; S$
20 HELP SET S$
30 INPUT "New value"; V
40 SET S$ V
```

## Notes

- This is a modern extension not present in original MBASIC 5.21
- Setting names are case-insensitive
- Unknown setting names produce an error message
- Use SHOW SETTINGS to discover available setting names

## See Also

- [SET](setsetting.md) - Modify a setting
- [SHOW SETTINGS](showsettings.md) - List all settings
