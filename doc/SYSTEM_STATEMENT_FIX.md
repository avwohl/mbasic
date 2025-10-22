# SYSTEM Statement Implementation

**Date**: 2025-10-22
**Context**: Continuing parse error fixes in MBASIC 5.21 compiler

## Problem

SYSTEM is a statement in MBASIC that exits the program and returns control to the operating system (similar to END, but specifically for OS return). The parser did not recognize SYSTEM as a keyword, treating it as an identifier instead, which caused it to attempt parsing SYSTEM as an assignment statement.

### Error Pattern
```
Parse error: Expected EQUAL, got NEWLINE
```

This occurred when SYSTEM appeared without an `=` sign, as the parser expected:
```basic
SYSTEM = value    ' Parser expected this
```

But the actual code was:
```basic
SYSTEM            ' Actual usage (statement, not assignment)
```

### Affected Files
Initially affected 16 files with "Expected EQUAL, got NEWLINE" errors. After the fix, this was reduced to 6 files (62.5% reduction), with the remaining 10 files having SYSTEM as the cause.

### Example from MENU.bas
```basic
160 IF A$=CHR$(13) THEN PRINT E1$Y1$"You are in HDOS"Y5$;:SYSTEM
```

This exits the program and returns to the OS when Enter (CHR$(13)) is pressed.

## Solution

Added SYSTEM as a keyword and implemented it as a statement (similar to END and STOP).

### 1. Added SYSTEM Token (tokens.py)

Added token type around line 58:

```python
RESUME = auto()
RETURN = auto()
STEP = auto()
STOP = auto()
SYSTEM = auto()      # NEW
THEN = auto()
TO = auto()
WHILE = auto()
WEND = auto()
```

Added to KEYWORDS dictionary around line 236:

```python
'RESUME': TokenType.RESUME,
'RETURN': TokenType.RETURN,
'STEP': TokenType.STEP,
'STOP': TokenType.STOP,
'SYSTEM': TokenType.SYSTEM,      # NEW
'THEN': TokenType.THEN,
'TO': TokenType.TO,
'WHILE': TokenType.WHILE,
'WEND': TokenType.WEND,
```

### 2. Created SystemStatementNode (ast_nodes.py)

Added around line 309:

```python
@dataclass
class SystemStatementNode:
    """SYSTEM statement - return control to operating system

    Syntax:
        SYSTEM    - Exit BASIC and return to OS

    Similar to END but specifically returns to the operating system
    (commonly used in CP/M and MS-DOS BASIC variants)
    """
    line_num: int = 0
    column: int = 0
```

### 3. Implemented parse_system() (parser.py)

Added around line 1195:

```python
def parse_system(self) -> SystemStatementNode:
    """Parse SYSTEM statement"""
    token = self.advance()

    return SystemStatementNode(
        line_num=token.line,
        column=token.column
    )
```

### 4. Added to Statement Dispatcher (parser.py)

Added around line 411:

```python
elif token.type == TokenType.END:
    return self.parse_end()
elif token.type == TokenType.STOP:
    return self.parse_stop()
elif token.type == TokenType.SYSTEM:      # NEW
    return self.parse_system()
elif token.type == TokenType.RUN:
    return self.parse_run()
```

## Testing

### Isolated Test
```python
source = '160 IF A$=CHR$(13) THEN PRINT E1$Y1$"You are in HDOS"Y5$;:SYSTEM'
# Result: SUCCESS
# Line 160: 2 statements
#   - IfStatementNode
#   - SystemStatementNode
```

### Comprehensive Test Results

**Before Implementation:**
- Successfully parsed: 76 files (32.3%)
- "Expected EQUAL, got NEWLINE" errors: 16 files

**After Implementation:**
- Successfully parsed: **84 files (35.7%)** ✓ +8 files
- "Expected EQUAL, got NEWLINE" errors: 6 files (-62.5%)

**Impact:**
- **+8 files** now parsing successfully (+10.5% increase)
- **-10 files** with "Expected EQUAL, got NEWLINE" caused by SYSTEM
- Overall error count reduced

### Newly Parsing Files

At least these files now parse successfully (examples with SYSTEM):
- MENU.bas
- menu.bas
- asciiart.bas
- buildsub.bas
- calendr5.bas
- kpro2-sw.bas
- roulette.bas
- spacewar.bas

## Background: SYSTEM in MBASIC

### Purpose
SYSTEM exits the BASIC interpreter and returns control to the operating system. This is commonly used in:
- Menu programs that launch other programs
- Utilities that need to exit cleanly to the OS
- Programs that provide a "quit to DOS/CP/M" option

### Historical Context
- **CP/M MBASIC**: SYSTEM returns to CP/M prompt
- **MS-DOS GW-BASIC/BASICA**: SYSTEM returns to DOS prompt
- **Different from END**: END stops program execution but may keep interpreter loaded

### Usage Pattern
```basic
' Exit program and return to OS
SYSTEM

' Common in menu systems
IF choice$ = "Q" THEN SYSTEM

' After displaying message
PRINT "Goodbye!": SYSTEM
```

## Technical Notes

### Design Decision: Statement vs Function

SYSTEM is a **statement** (like END, STOP), not a function:
- Takes no parameters
- No return value
- Cannot be used in expressions
- Terminates program execution immediately

### Similar Statements
- **END**: Terminates program (may keep interpreter)
- **STOP**: Pauses execution (for debugging)
- **SYSTEM**: Exits to operating system
- **RUN**: Restarts program or loads new program

### Implementation Pattern

The implementation follows the same pattern as END and STOP:
1. Simple token recognition
2. No parameter parsing
3. Creates basic AST node with just line/column info
4. One-line parser function

## Files Modified

1. **tokens.py**:
   - Added SYSTEM token type (line ~58)
   - Added to KEYWORDS dictionary (line ~236)

2. **ast_nodes.py**:
   - Added SystemStatementNode (lines 309-320)

3. **parser.py**:
   - Added parse_system() (lines 1195-1202)
   - Added to statement dispatcher (line ~411)

## Code References

- SYSTEM token definition: tokens.py:58
- SYSTEM keyword mapping: tokens.py:236
- SystemStatementNode: ast_nodes.py:309-320
- parse_system(): parser.py:1195-1202
- Statement dispatcher: parser.py:411

## Impact Summary

- **Files fixed**: +8 files now parsing (76 → 84)
- **Success rate**: 32.3% → 35.7% (+3.4 percentage points)
- **Error reduction**: "Expected EQUAL, got NEWLINE" reduced by 62.5% (16 → 6)
- **Semantic support**: Proper handling of OS-exit statement
- **Code quality**: Follows established pattern for simple statements
