# UI Helpers Guide

## Overview

The `src/ui/ui_helpers.py` module provides portable utilities that all UIs (CLI, Tk, Web, Curses) can use. These functions have **no UI-specific dependencies** and handle common tasks like error formatting, line numbering, and position calculations.

## Categories

### 1. Line Number Utilities
### 2. RENUM/DELETE Utilities
### 3. Error Formatting (NEW!)
### 4. Position Calculations (NEW!)

---

## 1. Line Number Utilities

### Constants

```python
MIN_LINE_NUMBER = 0
MAX_LINE_NUMBER = 65529
DEFAULT_START = 10
DEFAULT_INCREMENT = 10
```

### `validate_line_number(line_num: int) -> bool`

Check if line number is in valid MBASIC range.

```python
>>> validate_line_number(100)
True
>>> validate_line_number(70000)
False
```

### `parse_line_number(line_text: str) -> Optional[int]`

Extract line number from BASIC code line.

```python
>>> parse_line_number("10 PRINT 'HELLO'")
10
>>> parse_line_number("  20 FOR I=1 TO 10")
20
>>> parse_line_number("REM no line number")
None
```

### `calculate_midpoint(line_before: int, line_after: int) -> Optional[int]`

Find line number between two lines for smart insert.

```python
>>> calculate_midpoint(10, 30)
20
>>> calculate_midpoint(10, 11)
None  # No room
```

### `find_insert_line_number(line_before: int, line_after: Optional[int], increment: int) -> int`

Calculate appropriate line number for new line insertion.

```python
>>> find_insert_line_number(10, 30, 10)
20
>>> find_insert_line_number(10, 11, 10)
11  # Will need renumber
>>> find_insert_line_number(30, None, 10)
40  # At end of program
```

---

## 2. RENUM/DELETE Utilities

### `build_line_mapping(old_lines: List[int], new_start: int, old_start: int, increment: int) -> Dict[int, int]`

Build renumbering map for RENUM command.

```python
>>> old_lines = [10, 20, 30, 40]
>>> mapping = build_line_mapping(old_lines, 100, 20, 10)
>>> mapping
{10: 10, 20: 100, 30: 110, 40: 120}
# Lines before old_start stay same, rest renumbered
```

### `update_line_references(code: str, line_mapping: Dict[int, int]) -> str`

Update GOTO/GOSUB/THEN/ELSE line number references.

```python
>>> mapping = {10: 100, 20: 200}
>>> update_line_references("GOTO 10", mapping)
'GOTO 100'
>>> update_line_references("ON X GOTO 10,20", mapping)
'ON X GOTO 100,200'
```

### `parse_delete_args(args: str, all_line_numbers: List[int]) -> Tuple[int, int]`

Parse DELETE command arguments.

```python
>>> parse_delete_args("40", [10, 20, 30, 40, 50])
(40, 40)  # Single line
>>> parse_delete_args("40-100", [10, 20, 30, 40, 50])
(40, 100)  # Range
>>> parse_delete_args("-40", [10, 20, 30, 40, 50])
(10, 40)  # From start
>>> parse_delete_args("40-", [10, 20, 30, 40, 50])
(40, 50)  # To end
```

---

## 3. Error Formatting (NEW!)

### `format_error_message(message: str, line_number: Optional[int], line_text: Optional[str], column: Optional[int], mbasic_style: bool) -> str`

**General-purpose error formatter with MBASIC styling.**

**Parameters:**
- `message` - Error message text
- `line_number` - BASIC line number (optional)
- `line_text` - Full line text for context (optional)
- `column` - Column position (1-indexed, absolute) (optional)
- `mbasic_style` - Add "?" prefix (default: True)

**Examples:**

```python
# Basic error
>>> format_error_message("Division by zero", 100)
'?Division by zero in 100'

# Error with visual indicator
>>> format_error_message("Syntax error", 20, "20 PRINT X Y", 12)
'''?Syntax error in 20
20 PRINT X Y
           ^'''

# Non-MBASIC style (for internal errors)
>>> format_error_message("Internal error", mbasic_style=False)
'Internal error'
```

**Use Cases:**
- Runtime errors
- Parse errors
- Interactive mode errors
- Any error that needs consistent formatting

---

### `format_syntax_error(line_number: int, line_text: str, column: Optional[int], specific_message: Optional[str]) -> str`

**Format syntax/parse errors with line context.**

**Parameters:**
- `line_number` - BASIC line number
- `line_text` - Full line text
- `column` - Error column (optional)
- `specific_message` - Detailed error info (optional)

**Examples:**

```python
>>> format_syntax_error(100, "100 PRINT X Y", 13, "Expected :")
'''?Syntax error: Expected : in 100
100 PRINT X Y
            ^'''

>>> format_syntax_error(50, "50 NEXT", None, "NEXT without FOR")
'?Syntax error: NEXT without FOR in 50'
```

**Use Cases:**
- Parser errors
- Line entry validation
- Interactive mode syntax checking

---

### `format_runtime_error(error_code: int, error_message: str, line_number: Optional[int]) -> str`

**Format runtime errors with MBASIC error codes.**

**Parameters:**
- `error_code` - Numeric error code (e.g., 11 = division by zero)
- `error_message` - Human-readable description
- `line_number` - Line where error occurred (optional)

**Examples:**

```python
>>> format_runtime_error(11, "Division by zero", 250)
'?11 Error in 250: Division by zero'

>>> format_runtime_error(6, "Overflow")
'?6 Error: Overflow'
```

**Common Error Codes:**
- 2 - Syntax error
- 6 - Overflow
- 11 - Division by zero
- 13 - Type mismatch
- 14 - Out of string space
- 16 - String formula too complex

**Use Cases:**
- Interpreter runtime errors
- Math operation errors
- Type checking errors

---

### `format_parse_error_with_context(line_text: str, error_message: str, column: Optional[int], token_length: Optional[int]) -> str`

**Format parse errors with full context and multi-character indicators.**

**Parameters:**
- `line_text` - Line being parsed
- `error_message` - Error description
- `column` - Error position (optional)
- `token_length` - Length of problematic token for ^^ underline (optional)

**Examples:**

```python
>>> format_parse_error_with_context(
...     "100 PRINT X Y",
...     "Expected : or newline",
...     13
... )
'''Parse error: Expected : or newline
100 PRINT X Y
            ^'''

# Multi-character indicator
>>> format_parse_error_with_context(
...     "10 PRINT HELLO WORLD",
...     "Unknown identifier",
...     10,
...     5
... )
'''Parse error: Unknown identifier
10 PRINT HELLO WORLD
         ^^^^^'''
```

**Use Cases:**
- Parser diagnostics
- Token-level error reporting
- Developer debugging

---

### `standardize_error_format(error_str: str) -> str`

**Convert various error formats to consistent MBASIC style.**

**Transformations:**
- Adds "?" prefix if missing
- Removes "Parse error at line X, column Y:" prefix
- Normalizes to MBASIC format

**Examples:**

```python
>>> standardize_error_format("Syntax error")
'?Syntax error'

>>> standardize_error_format("Parse error at line 1, column 5: Expected :")
'?Expected :'

>>> standardize_error_format("?Already formatted")
'?Already formatted'
```

**Use Cases:**
- Converting parser exceptions to MBASIC format
- Normalizing errors from different sources
- UI error display

---

### `extract_error_location(error_str: str) -> Tuple[Optional[int], Optional[int]]`

**Extract line and column numbers from error messages.**

**Returns:**
- Tuple of `(line_number, column_number)`
- `(None, None)` if no location found

**Examples:**

```python
>>> extract_error_location("Parse error at line 5, column 10: message")
(5, 10)

>>> extract_error_location("?Syntax error in 100")
(100, None)

>>> extract_error_location("Generic error")
(None, None)
```

**Use Cases:**
- Parsing error messages from exceptions
- Jumping to error location in editor
- Error log analysis

---

## 4. Position Calculations (NEW!)

### `get_relative_column(line_text: str, absolute_column: int) -> int`

**Convert absolute column to relative (spaces after line number).**

**Why:** After RENUM, absolute positions shift but relative positions stay same.

**Examples:**

```python
>>> get_relative_column("10 PRINT X", 4)
1  # First character after "10 "

>>> get_relative_column("100 PRINT X", 5)
1  # First character after "100 "

>>> get_relative_column("10   PRINT X", 6)
3  # Third space after "10"
```

**Math:**
```
relative = absolute - len(line_number) - 1
```

**Use Cases:**
- Preserving indentation after RENUM
- Error position tracking
- Cursor position calculations

---

### `get_absolute_column(line_text: str, relative_column: int) -> int`

**Convert relative column to absolute (full line position).**

**Examples:**

```python
>>> get_absolute_column("10 PRINT X", 1)
4  # "10 " = 3 chars, +1 = 4

>>> get_absolute_column("100 PRINT X", 1)
5  # "100 " = 4 chars, +1 = 5

>>> get_absolute_column("10   PRINT X", 3)
6  # "10" + 3 spaces
```

**Math:**
```
absolute = len(line_number) + relative + 1
```

**Use Cases:**
- Error position display
- Cursor positioning in editors
- Syntax highlighting

---

### `create_error_indicator(line_text: str, column: int, length: int, indicator_char: str) -> str`

**Create visual error indicator line (^^^).**

**Parameters:**
- `line_text` - Line with error
- `column` - Error position (1-indexed)
- `length` - Number of characters to underline (default: 1)
- `indicator_char` - Character to use (default: '^')

**Examples:**

```python
>>> line = "10 PRINT X"
>>> create_error_indicator(line, 10, 1)
'         ^'

>>> line = "10 PRINT HELLO WORLD"
>>> create_error_indicator(line, 10, 5, '~')
'         ~~~~~'

>>> line = "100 FOR I=1TO10"
>>> create_error_indicator(line, 12, 2)
'           ^^'
```

**Use Cases:**
- Visual error messages
- Syntax error display
- Token highlighting in errors

---

## Usage Patterns

### Pattern 1: Formatting Parser Errors

```python
from ui.ui_helpers import format_syntax_error

def handle_parse_error(line_num, line_text, error):
    # Extract column from exception if available
    column = error.token.column if hasattr(error, 'token') else None

    # Format for display
    formatted = format_syntax_error(
        line_num,
        line_text,
        column,
        str(error)
    )

    print(formatted)
```

**Output:**
```
?Syntax error: Expected : in 100
100 PRINT X Y
            ^
```

---

### Pattern 2: Converting Positions for Error Display

```python
from ui.ui_helpers import get_relative_column, create_error_indicator

def show_error_in_editor(line_text, absolute_col):
    # Convert to relative for stability across RENUM
    relative_col = get_relative_column(line_text, absolute_col)

    # Store relative position (survives RENUM)
    store_error_position(relative_col)

    # Create visual indicator
    indicator = create_error_indicator(line_text, absolute_col, 1)

    print(line_text)
    print(indicator)
```

---

### Pattern 3: Standardizing Errors from Multiple Sources

```python
from ui.ui_helpers import standardize_error_format

def display_error(error_msg):
    # Normalize format regardless of source
    standardized = standardize_error_format(error_msg)

    # Now always in MBASIC format with ? prefix
    print(standardized)
```

**Input variations:**
```
"Syntax error"
"Parse error at line 1, column 5: Expected :"
"?Already formatted"
```

**Output:**
```
?Syntax error
?Expected :
?Already formatted
```

---

### Pattern 4: Runtime Error with Code

```python
from ui.ui_helpers import format_runtime_error

def divide(a, b, line_num):
    if b == 0:
        error_msg = format_runtime_error(11, "Division by zero", line_num)
        raise RuntimeError(error_msg)
    return a / b
```

---

## Integration with UIs

### CLI UI

```python
from ui.ui_helpers import format_syntax_error

# In interactive.py
try:
    parse_line(line_text)
except ParseError as e:
    print(format_syntax_error(line_num, line_text, e.column, str(e)))
```

### Tk UI

```python
from ui.ui_helpers import format_syntax_error, create_error_indicator

# In tk_ui.py
def show_error_dialog(line_num, line_text, column):
    error_msg = format_syntax_error(line_num, line_text, column)
    messagebox.showerror("Syntax Error", error_msg)
```

### Web UI

```python
from ui.ui_helpers import format_parse_error_with_context

# In web_ui.py
def format_error_for_json(line_text, error, column):
    formatted = format_parse_error_with_context(
        line_text,
        str(error),
        column
    )
    return {"error": formatted, "line": line_text, "column": column}
```

### Curses UI

```python
from ui.ui_helpers import create_error_indicator

# In curses_ui.py
def display_error_inline(stdscr, y, line_text, column):
    stdscr.addstr(y, 0, line_text)
    indicator = create_error_indicator(line_text, column, 1)
    stdscr.addstr(y+1, 0, indicator, curses.color_pair(ERROR_COLOR))
```

---

## Best Practices

### 1. **Always Use Relative Positions for Storage**

```python
# GOOD - Survives RENUM
relative_col = get_relative_column(line_text, absolute_col)
store_position(relative_col)

# BAD - Breaks after RENUM
store_position(absolute_col)
```

### 2. **Convert to Absolute for Display**

```python
# GOOD - Display uses absolute
absolute_col = get_absolute_column(line_text, stored_relative_col)
show_indicator(absolute_col)

# BAD - Display with relative looks wrong
show_indicator(stored_relative_col)
```

### 3. **Use Standardize for External Errors**

```python
# GOOD - Consistent format
try:
    operation()
except Exception as e:
    print(standardize_error_format(str(e)))

# BAD - Inconsistent format
try:
    operation()
except Exception as e:
    print(str(e))  # May not have ? prefix
```

### 4. **Provide Context When Available**

```python
# GOOD - Rich error info
format_syntax_error(line_num, line_text, column, specific_msg)

# ACCEPTABLE - Minimal info
format_syntax_error(line_num, line_text, None, None)

# AVOID - No context at all
print("Syntax error")
```

---

## Testing

All UI helper functions include doctests. Run tests:

```bash
python3 -m doctest src/ui/ui_helpers.py -v
```

Or test specific function:

```python
import doctest
from ui.ui_helpers import format_error_message
doctest.run_docstring_examples(format_error_message, globals(), verbose=True)
```

---

## Future Enhancements

### Ideas for Additional Utilities

1. **Error History**
   - `add_error_to_history(error, line_num, column)`
   - `get_recent_errors(count=10)`
   - Track errors for analysis

2. **Multi-line Error Spans**
   - `format_multi_line_error(start_line, end_line, message)`
   - Useful for GOSUB/RETURN mismatches

3. **Error Severity Levels**
   - `format_warning()`, `format_info()`, `format_critical()`
   - Different prefixes (?, !, *)

4. **Context Window**
   - `show_error_with_context(line_num, context_lines=2)`
   - Show surrounding lines for context

5. **Diff-style Indicators**
   - Show what was expected vs what was found
   - Useful for parse errors

---

## See Also

- `AST_SERIALIZATION.md` - AST structure and serialization
- `INDENT_COMMAND_DESIGN.md` - Future INDENT command
- `src/parser.py` - ParseError exception class
- `src/interactive.py` - Error handling in CLI
