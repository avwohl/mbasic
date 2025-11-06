# Statement-Level Highlighting Implementation Plan

## Overview
Implement visual highlighting of the current statement being executed within a line, supporting multi-statement lines (separated by `:`).

## Current State (Already Implemented)

### Ctrl+C Breakpoint ✓
- **Location**: `src/interpreter.py:126-132`, `214-223`
- **How it works**: Signal handler sets `runtime.break_requested = True`, interpreter checks and pauses
- **Status**: 'paused'

### Statement-Level Execution Tracking ✓
- **Location**: `src/interpreter.py:47`, `257-310`
- **State variable**: `InterpreterState.current_statement_index`
- **Runtime variable**: `runtime.current_stmt_index`

### Statement-Level Stepping ✓
- **Location**: `src/interpreter.py:307-309`
- **Mode**: `tick(mode='step_statement')`
- **Behavior**: Pauses after executing each statement

### Multi-Statement Parsing ✓
- **Location**: `src/parser.py:274-323`
- **Format**: Statements separated by COLON (`:`), stored in `LineNode.statements` list

## What Needs to Be Added

### 1. Character Position Tracking
**File**: `src/ast_nodes.py`

Add to each StatementNode:
```python
@dataclass
class StatementNode:
    line_num: int = 0
    column: int = 0
    char_start: int = 0  # NEW: Character offset from start of line
    char_end: int = 0    # NEW: Character offset end position
```

**Implementation**: Modify parser to track and store character positions as it parses statements.

### 2. Source Line Storage
**File**: `src/ast_nodes.py`

Add to LineNode:
```python
@dataclass
class LineNode:
    line_number: int
    statements: List['StatementNode']
    source_text: str = ""  # NEW: Original source line for highlighting
    line_num: int = 0
    column: int = 0
```

**Implementation**: Store original source text when parsing

### 3. Execution State Enhancement
**File**: `src/interpreter.py`

Add to InterpreterState:
```python
@dataclass
class InterpreterState:
    # ... existing fields ...
    current_statement_char_start: int = 0  # NEW
    current_statement_char_end: int = 0    # NEW
```

**Implementation**: Update these fields when executing statements in `tick()`

### 4. UI Highlighting

#### Tk UI (Primary Focus)
**File**: `src/ui/tk_ui.py`

Add methods:
```python
def _highlight_current_statement(self, line_number, char_start, char_end):
    """Highlight specific character range within a line in the editor"""
    # Use Text widget tags to highlight the range
    # Tag name: 'current_statement'
    # Visual: yellow background or similar

def _clear_statement_highlight(self):
    """Remove statement highlighting"""
```

Update in `_on_tick()`:
- Check if state has statement position info
- Call `_highlight_current_statement()` with position
- Clear highlight when execution completes

#### Curses UI
**File**: `src/ui/curses_ui.py`

Add indicator:
```python
def _show_current_statement(self, line_number, stmt_index, total_stmts):
    """Show which statement is executing in status line"""
    # Display: "Line 100 [stmt 2/3]" in status bar
```

#### CLI UI
**File**: `src/ui/cli.py`

Add output:
```python
# When paused/stepping, show:
# Paused at line 100, statement 2 of 3
```

#### Web UI
**File**: `src/ui/web/web_ui.py`

Add highlighting similar to Tk UI using CodeMirror/Monaco markers

### 5. Testing

Create test file: `tests/test_statement_stepping.bas`
```basic
10 REM Test statement stepping
20 FOR I=1 TO 1000000: PRINT I: NEXT I
30 A=1: B=2: C=3: D=4: E=5
40 IF A>0 THEN X=1: Y=2: Z=3
50 PRINT "Done"
```

Test cases:
1. Load program, press Ctrl+S to step statement-by-statement
2. Verify highlighting moves through each statement in line 20
3. Press Ctrl+C during loop, verify it pauses correctly
4. Press Ctrl+G to continue, Ctrl+C again
5. Use Ctrl+S to step individual statements in line 30

## Implementation Order

1. **Phase 1: Position Tracking** (Foundation)
   - Add `char_start`/`char_end` to StatementNode
   - Add `source_text` to LineNode
   - Modify parser to capture positions
   - Update interpreter state to track statement positions

2. **Phase 2: Tk UI Highlighting** (Primary UI)
   - Implement `_highlight_current_statement()`
   - Implement `_clear_statement_highlight()`
   - Update `_on_tick()` to use highlighting
   - Test with multi-statement lines

3. **Phase 3: Other UIs** (Consistency)
   - Update curses UI with statement indicator
   - Update CLI UI with statement info
   - Update web UI with highlighting

4. **Phase 4: Testing & Documentation**
   - Create comprehensive test programs
   - Test Ctrl+C in single-line loops
   - Document keybindings and features
   - Update help system

## Implementation Notes

### Parser Changes
The parser already iterates through tokens when building statements. We need to:
1. Record the position of the first token of each statement
2. Record the position after the last token (or before the COLON)
3. Store these in the statement node

### Lexer Token Information
Tokens already have `line` and `column` fields. We can use these to calculate character positions.

### Highlighting in Tk Text Widget
```python
# Create tag for highlighting
editor_text.tag_config('current_statement', background='yellow', foreground='black')

# Apply highlighting
editor_text.tag_remove('current_statement', '1.0', 'end')
start_idx = f"{line_number}.{char_start}"
end_idx = f"{line_number}.{char_end}"
editor_text.tag_add('current_statement', start_idx, end_idx)
editor_text.see(start_idx)
```

### Single-Line Loop Considerations
For a line like `100 FOR I=0 TO 10000: GOTO 100`:
- Each iteration executes 2 statements (FOR body, GOTO)
- Ctrl+C should pause between statements
- Highlighting should show which statement is active
- This tests the core functionality perfectly

## Testing Strategy

1. **Unit tests**: Test parser position tracking
2. **Integration tests**: Test interpreter state updates
3. **UI tests**: Visual verification of highlighting
4. **Performance tests**: Ensure no slowdown with highlighting

## Dependencies

- Existing: Parser, Interpreter, all UIs
- New: None (all Python stdlib)

## Backwards Compatibility

- All changes are additive
- Old code continues to work
- New features are opt-in through UI

## Future Enhancements

- Breakpoints at statement level (not just line level)
- Step over/into for statement-level debugging
- Conditional breakpoints on specific statements
- Statement execution time profiling
