# Settings and Configuration

> **Status:** The settings system is implemented and available in all UIs. Core commands (SET, SHOW SETTINGS, HELP SET) work as documented. Settings files are automatically created in ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows). Note: Some individual settings are still planned (see status notes for each setting).

MBASIC includes a comprehensive settings system that allows you to customize its behavior. Settings can be configured globally, per-project, or per-file.

## Quick Start

### View All Settings
```basic
SHOW SETTINGS
```

### Change a Setting

**Using SET command (in BASIC):**
```basic
SET "variables.case_conflict" "error"
SET "editor.auto_number" true
```

**Using JSON file (in settings.json):**
```json
{
  "variables.case_conflict": "error",
  "editor.auto_number": true
}
```

Note: Both methods are equivalent. SET commands affect the current session; JSON files persist across sessions.

### Get Help on a Setting
```basic
HELP SET "variables.case_conflict"
```

## Settings Scope

Settings are applied in this order (most specific wins):

1. **File scope** - Per-file settings (future feature)
2. **Project scope** - `.mbasic/settings.json` in project directory
3. **Global scope** - `~/.mbasic/settings.json` in home directory
4. **Default** - Built-in defaults

### Global Settings File

**Location:**
- **Linux/Mac:** `~/.mbasic/settings.json`
- **Windows:** `%APPDATA%/mbasic/settings.json` (typically `C:\Users\YourName\AppData\Roaming\mbasic\settings.json`)

Example:
```json
{
  "variables.case_conflict": "first_wins",
  "editor.auto_number": true,
  "ui.theme": "dark"
}
```

### Project Settings File

Location: `.mbasic/settings.json` (in your project directory)

Use for project-specific preferences:
```json
{
  "variables.case_conflict": "error",
  "editor.auto_number_step": 5
}
```

---

## Variable Settings

### variables.case_conflict

**Controls:** How to handle variable name case variations

**Type:** Choice (enum)

**Default:** `"first_wins"`

**Options:**
- `"first_wins"` - First usage sets the case (silent)
- `"error"` - Flag conflicts as errors requiring user intervention
- `"prefer_upper"` - Choose version with most uppercase letters
- `"prefer_lower"` - Choose version with most lowercase letters
- `"prefer_mixed"` - Prefer mixed case (camelCase/PascalCase)

**Examples:**

#### first_wins (default)
```basic
10 TargetAngle = 45
20 targetangle = 90  ' Uses "TargetAngle" (first case)
30 PRINT TargetAngle  ' Displays as "TargetAngle" everywhere
```
Variable window shows: `TargetAngle = 90`

#### error
```basic
SET "variables.case_conflict" "error"
10 TargetAngle = 45
20 targetangle = 90  ' ERROR: Variable name case conflict
```
Program stops with error message showing line numbers.

#### prefer_upper
```basic
SET "variables.case_conflict" "prefer_upper"
10 TargetAngle = 45  ' 1 uppercase letter
20 targetangle = 90  ' 0 uppercase letters
30 TARGETANGLE = 100  ' 11 uppercase letters (wins)
```
Variable window shows: `TARGETANGLE = 100`

#### prefer_lower
```basic
SET "variables.case_conflict" "prefer_lower"
10 COUNTER = 10  ' 7 uppercase letters
20 counter = 20  ' 7 lowercase letters (wins)
30 Counter = 30  ' Mixed case
```
Variable window shows: `counter = 30`

#### prefer_mixed
```basic
SET "variables.case_conflict" "prefer_mixed"
10 myvar = 10      ' All lowercase
20 MYVAR = 20      ' All uppercase
30 MyVar = 30      ' Mixed case (wins)
```
Variable window shows: `MyVar = 30`

**Use Cases:**
- **first_wins**: Default, least surprising for most users
- **error**: Team projects requiring consistent naming
- **prefer_upper**: Classic BASIC style (all caps)
- **prefer_lower**: Modern Python/C style
- **prefer_mixed**: Modern camelCase/PascalCase style

### variables.show_types_in_window

**Controls:** Show type suffixes ($, %, !, #) in variable window

**Type:** Boolean

**Default:** `true`

**Example:**
```basic
' With show_types_in_window = true
Variable window shows: Counter%, Message$, Value!

' With show_types_in_window = false
Variable window shows: Counter, Message, Value
```

---

## Editor Settings

### editor.auto_number

**Controls:** Automatically number typed lines

**Type:** Boolean

**Default:** `true`

**When enabled:**
```basic
' You type (without line number):
PRINT "Hello"

' MBASIC adds:
10 PRINT "Hello"
```

### editor.auto_number_step

**Controls:** Line number increment for auto-numbering

**Type:** Integer (1-1000)

**Default:** `10`

**Example:**
```basic
SET "editor.auto_number_step" 5

' Lines numbered: 5, 10, 15, 20, ...
```

### editor.tab_size

**Controls:** Tab width in spaces

**Type:** Integer (1-16)

**Default:** `4`

### editor.show_line_numbers

**Controls:** Display line numbers in editor

**Type:** Boolean

**Default:** `true`

---

## Interpreter Settings

### interpreter.strict_mode

**Status:** 🔧 PLANNED - Not yet implemented

**Controls:** Enable strict error checking

**Type:** Boolean

**Default:** `false`

**When enabled (future):**
- Additional error checks
- Undefined variable warnings
- Type mismatch warnings

### interpreter.max_execution_time

**Controls:** Maximum program execution time in seconds

**Type:** Integer (1-3600)

**Default:** `30`

**Example:**
```basic
SET "interpreter.max_execution_time" 60
' Program will stop after 60 seconds
```

Set to `0` for unlimited execution time (use with caution).

### interpreter.debug_mode

**Status:** 🔧 PLANNED - Not yet implemented

**Controls:** Enable debug output

**Type:** Boolean

**Default:** `false`

**When enabled (future):**
- Detailed execution traces
- Variable access tracking
- Performance metrics

---

## UI Settings

### ui.theme

**Status:** 🔧 PLANNED - Not yet implemented

**Controls:** Color theme for UI

**Type:** Choice (enum)

**Default:** `"default"`

**Options (future):**
- `"default"` - Standard theme
- `"dark"` - Dark background
- `"light"` - Light background
- `"classic"` - Retro BASIC terminal style

### ui.font_size

**Status:** 🔧 PLANNED - Not yet implemented

**Controls:** UI font size in points

**Type:** Integer (8-32)

**Default:** `12`

**Example (when implemented):**
```basic
SET "ui.font_size" 14
' Increases font size for better readability
```

---

## Command Reference

### SET Command

**Syntax:**
```basic
SET "setting.name" value
```

**Examples:**
```basic
SET "variables.case_conflict" "error"
SET "editor.auto_number_step" 5
SET "ui.theme" "dark"
SET "editor.show_line_numbers" true
```

**Type Conversion:**
- Strings: `"value"` (with quotes)
- Numbers: `5` (without quotes)
- Booleans: `true` or `false` (lowercase, no quotes in both commands and JSON files)

### SHOW SETTINGS Command

**Syntax:**
```basic
SHOW SETTINGS               ' Show all settings
SHOW SETTINGS "pattern"     ' Show matching settings
```

**Examples:**
```basic
SHOW SETTINGS
' Displays all settings with current values

SHOW SETTINGS "editor"
' Shows only editor.* settings

SHOW SETTINGS "case"
' Shows settings containing "case" in name
```

**Output Format:**
```
Category: Variables
  variables.case_conflict = first_wins (default)
  variables.show_types_in_window = true

Category: Editor
  editor.auto_number = true
  ...
```

### HELP SET Command

**Syntax:**
```basic
HELP SET "setting.name"
```

**Example:**
```basic
HELP SET "variables.case_conflict"

' Output:
' Setting: variables.case_conflict
' Type: enum
' Default: first_wins
' Choices: first_wins, error, prefer_upper, prefer_lower, prefer_mixed
'
' Description:
' Controls what happens when the same variable appears with different cases.
' ...
```

---

## Common Workflows

### Team Project with Consistent Naming
```basic
' In project .mbasic/settings.json:
{
  "variables.case_conflict": "error",
  "editor.auto_number_step": 5
}

' Now all team members must use consistent case
```

### Classic BASIC Style (All Caps)
```basic
SET "variables.case_conflict" "prefer_upper"
SET "ui.theme" "classic"

' Variables display in uppercase like vintage BASIC
```

### Modern Python-like Style
```basic
SET "variables.case_conflict" "prefer_lower"
SET "ui.theme" "dark"

' Variables display in lowercase like modern languages
```

### Debugging Session
```basic
SET "interpreter.debug_mode" true
SET "interpreter.max_execution_time" 300
RUN

' See detailed execution traces
```

---

## Case Conflict Scenarios

### Scenario 1: Accidental Typos

**Without error checking:**
```basic
' Default: first_wins
10 TotalCount = 0
20 FOR I = 1 TO 10
30   TotalCont = TotalCont + I  ' Typo! Different variable
40 NEXT I
50 PRINT TotalCount  ' Prints 0 (bug!)
```

**With error checking:**
```basic
SET "variables.case_conflict" "error"
10 TotalCount = 0
20 FOR I = 1 TO 10
30   TotalCont = TotalCont + I
40 NEXT I

' ERROR at line 30: Variable name case conflict:
' "TotalCont" vs "TotalCount" at line 10
' Bug caught immediately!
```

### Scenario 2: Merging Code

**Problem:**
```basic
' Program 1 uses:
PlayerScore = 100

' Program 2 uses:
playerscore = 200

' After MERGE:
10 PlayerScore = 100
20 playerscore = 200  ' Same variable, different case
```

**Solution:**
```basic
SET "variables.case_conflict" "first_wins"
' Uses "PlayerScore" everywhere

' OR
SET "variables.case_conflict" "error"
' Forces you to fix the conflict
```

### Scenario 3: Code Style Enforcement

**Team wants camelCase:**
```basic
SET "variables.case_conflict" "prefer_mixed"

' Team members use different cases:
10 targetangle = 45   ' All lowercase
20 TARGETANGLE = 90   ' All uppercase
30 TargetAngle = 100  ' Mixed case (camelCase)

' Variable window shows: TargetAngle
' Enforces team's camelCase style
```

---

## Tips and Best Practices

### 1. Use error Mode for Team Projects
Prevents accidental case variations across team members.

```basic
' In project .mbasic/settings.json:
{
  "variables.case_conflict": "error"
}
```

### 2. Use first_wins for Personal Projects
Least surprising behavior, lets you code freely.

### 3. Check Variable Window
The Variables & Resources window ({{kbd:toggle_variables}} in TK UI) shows the canonical case being used.

### 4. Document Your Choice
Add a comment at the top of programs:
```basic
10 REM Case policy: first_wins
20 REM Use consistent case for readability
```

### 5. Test After Changing Policies
```basic
SET "variables.case_conflict" "error"
RUN

' Fix any conflicts found
' Then set back to first_wins if desired
```

---

## Troubleshooting

### "Case conflict error" - What to do?

**Error message:**
```
Variable name case conflict: 'TargetAngle' at line 10 vs 'targetangle' at line 20
```

**Solutions:**
1. Fix the code to use consistent case
2. Change policy: `SET "variables.case_conflict" "first_wins"`
3. Choose a policy that picks one: `"prefer_upper"`, `"prefer_lower"`, etc.

### Settings not persisting?

Check that you're editing the right file:
- **Global (Linux/Mac):** `~/.mbasic/settings.json`
- **Global (Windows):** `%APPDATA%/mbasic/settings.json`
- **Project:** `.mbasic/settings.json` (create directory if needed)

Settings in files persist across sessions. Settings via `SET` command only affect current session.

### Which setting is being used?

```basic
SHOW SETTINGS "variables.case_conflict"

' Output shows:
' variables.case_conflict = error (project)
'                          ^^^^^^^ shows scope
```

Possible scopes: `(default)`, `(global)`, `(project)`, `(file)`

---

## Advanced Usage

### Create Project Settings Directory
```bash
mkdir -p .mbasic
cat > .mbasic/settings.json << 'EOF'
{
  "variables.case_conflict": "error",
  "editor.auto_number_step": 5,
  "ui.theme": "dark"
}
EOF
```

### Backup Global Settings
```bash
cp ~/.mbasic/settings.json ~/.mbasic/settings.json.backup
```

### Reset to Defaults
Delete settings files and MBASIC will use built-in defaults:
```bash
rm ~/.mbasic/settings.json
rm .mbasic/settings.json
```

---

## Related Documentation

- **Quick Reference**: `docs/user/QUICK_REFERENCE.md`
- **TK UI Guide**: `docs/user/TK_UI_QUICK_START.md`
- **Developer Notes**: `docs/dev/WORK_IN_PROGRESS.md`

---

## Future Settings (Planned)

The following settings are designed but not yet implemented:

- `keywords.case_style` - Keyword case handling (PRINT vs print)
- `spacing.operator_style` - Spacing around operators
- `spacing.comma_style` - Spacing after commas
- `merge.case_conflict_behavior` - How MERGE handles conflicts

See `docs/dev/KEYWORD_CASE_HANDLING_TODO.md` for details on upcoming features.
