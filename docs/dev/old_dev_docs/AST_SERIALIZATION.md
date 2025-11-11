# AST Serialization Architecture

## Overview

The MBASIC interpreter uses Abstract Syntax Tree (AST) serialization as the **single source of truth** for program representation. This means:

1. Programs are parsed into AST nodes
2. AST nodes can be serialized back to BASIC source code
3. All UIs (CLI, Tk, Web, Curses) use the same serialization
4. Operations like RENUM, DELETE, MERGE work on the AST
5. Saved programs match loaded programs exactly

## Key Components

### 1. AST Nodes (`src/ast_nodes.py`)

All AST nodes include position tracking:
- `line_num` - Source line number (1-indexed)
- `column` - Column position in source (1-indexed, absolute)
- `char_start` - Character offset for highlighting (statements only)
- `char_end` - Character end position for highlighting (statements only)

**Special case: Comments**
```python
@dataclass
class RemarkStatementNode:
    """REM/REMARK statement - comment"""
    text: str
    comment_type: str = "REM"  # "REM", "REMARK", or "APOSTROPHE"
    line_num: int = 0
    column: int = 0
```

The `comment_type` field preserves the original syntax:
- `"REM"` - for `REM` keyword
- `"REMARK"` - for `REMARK` keyword (normalized to REM on output)
- `"APOSTROPHE"` - for `'` apostrophe syntax

### 2. Serialization (`src/interactive.py`)

The `InteractiveMode` class provides serialization methods:

```python
def _serialize_line(self, line_node):
    """Serialize a LineNode back to source text, preserving indentation"""
    # Returns: "10 PRINT 'Hello'    ' This is a comment"

def _serialize_statement(self, stmt):
    """Serialize a statement node back to source text"""
    # Handles all statement types

def _serialize_expression(self, expr):
    """Serialize an expression node to source text"""
    # Handles numbers, strings, variables, operators, functions

def _serialize_variable(self, var):
    """Serialize a variable reference"""
    # Handles names, type suffixes, array subscripts
```

### 3. Formatting Preservation

The serializer preserves:

✅ **Comment syntax** - `'` vs `REM`
```basic
10 PRINT "TEST"    ' This is preserved as apostrophe
20 REM This is preserved as REM
```

✅ **Line indentation** - Uses `column` from first statement
```basic
10     PRINT "TEST"    # Spaces after line number preserved
```

✅ **Uppercase keywords** - PRINT, FOR, TO, NEXT, END, REM, GOTO, etc.
```basic
10 FOR i = 1 TO 10    # Becomes: 10 FOR I = 1 TO 10
```

✅ **Integer representation** - No decimal for whole numbers
```basic
10 X = 100    # Not 100.0
```

✅ **Inline comment spacing** - Comments use spacing not colon
```basic
10 PRINT X    ' Comment here    # Not: PRINT X : ' Comment
```

❌ **Variable case** - Normalized to lowercase (acceptable for case-insensitive BASIC)
```basic
10 X = 5    # Becomes: 10 x = 5
```

## Usage Examples

### Example 1: RENUM Command

The RENUM command uses AST serialization:

```python
# In interactive.py cmd_renum()
def cmd_renum(self, args):
    # 1. Build line number mapping
    line_mapping = build_line_mapping(old_lines, new_start, old_start, increment)

    # 2. Update GOTO/GOSUB references in AST
    for line_num, line_node in self.program.line_asts.items():
        for stmt in line_node.statements:
            update_goto_references(stmt, line_mapping)

    # 3. Serialize AST back to text
    new_lines = {}
    for old_num, line_node in self.program.line_asts.items():
        new_num = line_mapping[old_num]
        line_node.line_number = new_num
        new_lines[new_num] = self._serialize_line(line_node)

    # 4. Update program
    self.program.lines = new_lines
```

### Example 2: DELETE Command

The DELETE command modifies the AST:

```python
def cmd_delete(self, args):
    start, end = parse_delete_args(args, list(self.program.lines.keys()))

    # Delete from both lines and AST
    for line_num in list(self.program.lines.keys()):
        if start <= line_num <= end:
            del self.program.lines[line_num]
            del self.program.line_asts[line_num]
```

### Example 3: SAVE/LOAD

Programs are saved/loaded via serialized text:

```python
def cmd_save(self, args):
    # Serialize all lines from AST
    with open(filename, 'w') as f:
        for line_num in sorted(self.program.line_asts.keys()):
            line_node = self.program.line_asts[line_num]
            line_text = self._serialize_line(line_node)
            f.write(line_text + '\n')
```

When loading, lines are parsed back into AST, completing the round-trip.

## Position Tracking Details

### Absolute Positions

The `column` field stores absolute column position (includes line number):

```basic
10 PRINT "TEST"
^  ^     ^
1  4     10
```

- Line number `10` starts at column 1
- Space after `10` is at column 3
- `PRINT` starts at column 4
- String starts at column 10

### Indentation Preservation

The serializer uses `column` to preserve indentation:

```python
# In _serialize_line()
first_stmt = line_node.statements[0]
if hasattr(first_stmt, 'column') and first_stmt.column > 0:
    current_pos = len(line_num_str) + 1  # +1 for 1-indexed
    desired_col = first_stmt.column
    spaces_needed = max(1, desired_col - current_pos)
    parts.append(' ' * spaces_needed)
```

### RENUM Position Adjustment

After RENUM, column positions may shift:
- `10 PRINT` → `100 PRINT` (shift right by 2 columns)
- `1000 PRINT` → `10 PRINT` (shift left by 2 columns)

The serializer handles this by:
1. Using new line number length for `current_pos`
2. Maintaining `desired_col` from original AST
3. Adding appropriate spacing to reach desired column

**Limitation**: If new line number is longer than space available, statement may shift.

## Comment Handling

### Apostrophe vs REM

The lexer distinguishes comment types:

```python
# In lexer.py
if char == "'":
    comment_text = self.read_comment()
    self.tokens.append(Token(TokenType.APOSTROPHE, comment_text, ...))

if token.type == TokenType.REM:
    comment_text = self.read_comment()
    token = Token(TokenType.REM, comment_text, ...)
```

The parser stores this in AST:

```python
# In parser.py parse_remark_statement()
comment_type = token.type.name  # "REM", "REMARK", or "APOSTROPHE"
return RemarkStatementNode(
    text=comment_text,
    comment_type=comment_type,
    ...
)
```

The serializer outputs correctly:

```python
# In interactive.py _serialize_statement()
if stmt.comment_type == "APOSTROPHE":
    return f"' {stmt.text}"
else:  # REM, REMARK, or default
    return f"REM {stmt.text}"
```

### Inline Comments

Comments after statements use spacing not colon separator:

```python
# In _serialize_line()
for i, stmt in enumerate(line_node.statements):
    stmt_text = self._serialize_statement(stmt)
    if i == 0:
        parts.append(stmt_text)
    else:
        # Check if this is an inline comment
        if type(stmt).__name__ == 'RemarkStatementNode':
            # Inline comment - preserve spacing, no colon
            parts.append('    ' + stmt_text)
        else:
            parts.append(' : ' + stmt_text)
```

Result:
```basic
10 PRINT X    ' This is a comment
```
Not:
```basic
10 PRINT X : ' This is a comment
```

## UI Integration

### All UIs Use Same Serialization

Each UI can access serialization via `InteractiveMode`:

**CLI** - Direct access
```python
mode = InteractiveMode()
line_text = mode._serialize_line(line_node)
```

**Tk UI** - Via interpreter reference
```python
serialized = self.interpreter.interactive_mode._serialize_line(line_node)
```

**Web UI** - Same as Tk

**Curses UI** - Same as Tk

### Benefits of Single Source

1. **Consistency** - All UIs show same formatting
2. **Testing** - Test once, works everywhere
3. **Debugging** - AST issues visible immediately
4. **Maintainability** - One implementation to fix/enhance

## Testing

### Manual Testing

```python
from parser import Parser
from lexer import Lexer
from interactive import InteractiveMode

line = '10 PRINT "TEST"    \' This is a comment'
lexer = Lexer(line)
tokens = lexer.tokenize()
parser = Parser(tokens, {})
ast = parser.parse_line()

mode = InteractiveMode()
serialized = mode._serialize_line(ast)
print(f"Original:    {line}")
print(f"Serialized:  {serialized}")
print(f"Match: {line == serialized}")
```

### Expected Results

✅ Exact match for:
- Comments (`'` and `REM`)
- Strings (with apostrophes inside)
- Indentation
- Line structure

❌ Acceptable differences:
- Variable case (X → x)
- Blank numbered lines (not preserved in AST)

## Future Enhancements

### 1. Relative Position Tracking

Add position relative to first statement (excludes line number width):

```python
@dataclass
class StatementNode:
    column: int = 0           # Absolute position (current)
    column_relative: int = 0  # Relative to first non-whitespace after line num
```

Benefits:
- Survives RENUM digit count changes
- More stable for error messages

### 2. UI Helper Functions

Create `src/ui/ui_helpers.py` functions for:
- `format_error_position(line_num, column)` - Adjust column for line number width
- `serialize_program(program)` - High-level program serialization
- `validate_ast_roundtrip(source)` - Test parse→serialize→parse equivalence

### 3. Expression Serialization Enhancement

Currently simple string concatenation. Could enhance to:
- Preserve parentheses from original source
- Smart spacing around operators
- Handle operator precedence for minimal parentheses

## Implementation Status

**Completed** (commits 58a58f9, 57b102c):
- ✅ Comment type preservation (`comment_type` field)
- ✅ Apostrophe vs REM distinction
- ✅ Indentation preservation
- ✅ Inline comment spacing
- ✅ All statement types
- ✅ All expression types
- ✅ Tk UI integration
- ✅ Round-trip testing

**Working Well**:
- RENUM with AST serialization
- DELETE with AST modification
- SAVE/LOAD consistency
- Multi-UI compatibility

**Known Limitations**:
- Variable case normalized to lowercase
- Blank numbered lines not in AST
- Absolute column positions shift after RENUM
- No original source preservation for error recovery

## References

- `src/ast_nodes.py` - AST node definitions
- `src/interactive.py` - Serialization implementation (lines 893-1129)
- `src/parser.py` - AST construction from tokens
- `src/lexer.py` - Tokenization with position tracking
- `src/ui/ui_helpers.py` - Shared UI utilities
- `src/editing/manager.py` - Program storage and management
