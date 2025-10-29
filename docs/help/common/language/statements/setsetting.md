---
category: system
description: Configure interpreter settings at runtime
keywords:
- set
- setting
- configure
- option
- preference
- runtime
syntax: "SET \"setting.name\" value"
title: SET (setting)
type: statement
related: [showsettings, helpsetting]
---

# SET (setting)

## Syntax

```basic
SET "setting.name" value
```

**Versions:** MBASIC Extension

## Purpose

To configure interpreter settings and options at runtime.

## Remarks

SET allows programs to dynamically configure interpreter behavior by modifying settings. The setting name is a string in dotted notation (e.g., "display.width", "editor.tabsize").

Settings can control:
- Display and output formatting
- Editor behavior
- Runtime options
- UI preferences

Settings persist for the current session or can be saved to configuration files depending on the setting scope.

## Example

```basic
SET "display.width" 80
SET "editor.tabsize" 4

10 SET "runtime.strict_mode" 1
20 PRINT "Strict mode enabled"

100 INPUT "Tab size"; T
110 SET "editor.tabsize" T
```

## Notes

- This is a modern extension not present in original MBASIC 5.21
- Available settings are implementation-specific
- Use SHOW SETTINGS to list all available settings
- Use HELP SET "name" to get help on a specific setting
- Invalid setting names produce an error

## See Also

- [SHOW SETTINGS](showsettings.md) - Display current settings
- [HELP SET](helpsetting.md) - Get help on a setting
