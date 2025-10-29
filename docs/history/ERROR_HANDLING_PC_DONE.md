# Error Handling PC Enhancement

**Status:** ⏳ TODO
**Priority:** MEDIUM
**Created:** 2025-10-28 (v1.0.289)

## Problem

Error handling still uses line numbers extracted from PC instead of using PC objects directly. This causes several issues:

1. **Loss of statement precision**: `pc.line_num` throws away statement offset information
2. **No ERS# variable**: Users can't determine which statement on a line caused an error
3. **Scattered pc.line_num usage**: ~50+ places extracting line_num instead of using PC
4. **ErrorInfo uses int not PC**: Stores `error_line: int` instead of `error_pc: PC`

### Current Behavior

```basic
10 A=1:B=2:C=1/0:D=4
20 ON ERROR GOTO 100
100 PRINT "Error at line"; ERL
110 RESUME NEXT
```

**Output:**
```
Error at line 10
```

**Problem:** Can't tell which statement (the `C=1/0`) caused the error!

### Desired Behavior

```basic
10 A=1:B=2:C=1/0:D=4
20 ON ERROR GOTO 100
100 PRINT "Error at line"; ERL; "statement"; ERS
110 RESUME NEXT
```

**Output:**
```
Error at line 10 statement 2
```

## Proposed Changes

### 1. Add ERS# System Variable

**New variable:** `ERS#` (Error Statement) - 0-based statement offset within error line

**Behavior:**
- Set when error occurs: `ERS# = error_pc.stmt_offset`
- Works with existing `ERL#` (Error Line)
- 0-based to match PC.stmt_offset (first statement = 0)
- Valid only after error, undefined otherwise

**Example usage:**
```basic
10 ON ERROR GOTO 1000
20 A=5:B=10:C=1/0:D=20
...
1000 PRINT "Error at line"; ERL; "statement"; ERS
1010 RESUME NEXT
```

**MBASIC 5.21 compatibility note:**
- ERS# is a new extension, not in original MBASIC 5.21
- Does not break existing programs (new variable)
- Follows MBASIC naming convention (# suffix for numeric variable)

### 2. Update ErrorInfo to Use PC

**Current structure:**
```python
@dataclass
class ErrorInfo:
    error_code: int
    error_line: int  # Only stores line number!
    error_message: str
```

**New structure:**
```python
@dataclass
class ErrorInfo:
    error_code: int
    error_pc: PC  # Full position with statement offset
    error_message: str

    @property
    def error_line(self) -> int:
        """Backwards compatibility: extract line from PC"""
        return self.error_pc.line_num if self.error_pc else None

    @property
    def error_stmt(self) -> int:
        """New: statement offset within line"""
        return self.error_pc.stmt_offset if self.error_pc else 0
```

**Benefits:**
- Preserves statement-level error information
- Backwards compatible via `error_line` property
- Enables precise error reporting in UIs

### 3. Review All pc.line_num Usage

**Search for:** All places using `pc.line_num` or `runtime.pc.line_num`

**Categories:**

#### Category A: Should Use Full PC
These should store/pass PC object, not just line number:

```python
# BAD: Loses statement info
self._invoke_error_handler(error_code, pc.line_num, pc.stmt_offset)

# GOOD: Keeps PC together
self._invoke_error_handler(error_code, pc)
```

**Examples:**
- Error handler invocation
- ErrorInfo creation
- Error reporting/logging
- Debug output that shows position

#### Category B: Line Number Is Correct
These legitimately need just the line number:

```python
# OK: User-visible line number for display
self.io.output(f"Error at line {pc.line_num}")

# OK: GOTO target (statement offset always 0)
if target_line == pc.line_num:
    ...

# OK: Setting ERL# system variable (separate from ERS#)
self.runtime.set_variable("ERL", pc.line_num)
```

**Examples:**
- User-facing error messages
- GOTO/GOSUB line number matching
- ERL# system variable (pairs with new ERS#)
- Trace output showing line numbers

#### Category C: Should Use Property/Method
These should call a helper method instead of direct access:

```python
# BAD: Direct field access scattered everywhere
if pc.line_num in breakpoints:
    ...

# GOOD: Use helper method
if pc.matches_line(line_num):
    ...
```

## Implementation Plan

### Phase 1: Add ERS# Variable

1. **Add to Runtime** (`src/runtime.py`):
   ```python
   # In Runtime.__init__():
   self.error_stmt_offset = 0  # Set when error occurs
   ```

2. **Set on error** (`src/interpreter.py`):
   ```python
   # In exception handlers:
   self.runtime.error_line = pc.line_num
   self.runtime.error_stmt_offset = pc.stmt_offset  # NEW
   ```

3. **Expose as ERS** (`src/basic_builtins.py` or variable handler):
   ```python
   # When user accesses ERS:
   if var_name == "ERS":
       return self.runtime.error_stmt_offset
   ```

4. **Test with error handlers**:
   ```basic
   10 ON ERROR GOTO 1000
   20 A=1:B=2:C=1/0:D=4
   30 PRINT "After error"
   1000 PRINT "Error at"; ERL; "stmt"; ERS
   1010 RESUME NEXT
   ```

### Phase 2: Update ErrorInfo Structure

1. **Update dataclass** (`src/interpreter.py`):
   ```python
   @dataclass
   class ErrorInfo:
       error_code: int
       error_pc: PC  # Changed from error_line: int
       error_message: str

       @property
       def error_line(self) -> int:
           return self.error_pc.line_num if self.error_pc else None

       @property
       def error_stmt(self) -> int:
           return self.error_pc.stmt_offset if self.error_pc else 0
   ```

2. **Update ErrorInfo creation** (all places creating ErrorInfo):
   ```python
   # Before:
   ErrorInfo(error_code=code, error_line=pc.line_num, error_message=msg)

   # After:
   ErrorInfo(error_code=code, error_pc=pc, error_message=msg)
   ```

3. **Update all error_info readers**:
   - UIs displaying errors can still use `error_info.error_line`
   - Add display of `error_info.error_stmt` where helpful
   - Update error highlight to use both line and statement

### Phase 3: Audit pc.line_num Usage

1. **Find all usages**:
   ```bash
   grep -rn "\.line_num" src/ --include="*.py"
   ```

2. **Categorize each usage** (A, B, or C from above)

3. **Refactor Category A** (should use full PC):
   ```python
   # Example: Error handler invocation
   # Before:
   def _invoke_error_handler(self, error_code, error_line, error_stmt):
       ...

   # After:
   def _invoke_error_handler(self, error_code, error_pc: PC):
       ...
   ```

4. **Keep Category B** (line number is correct):
   - Add comments explaining why line_num is used
   - Document that statement info not needed here

5. **Refactor Category C** (add helper methods):
   ```python
   # Add to PC class:
   def matches_line(self, line_num: int) -> bool:
       """Check if PC is on the given line"""
       return self.line_num == line_num

   def display_position(self, show_stmt: bool = True) -> str:
       """Format position for user display"""
       if show_stmt and self.stmt_offset > 0:
           return f"{self.line_num}.{self.stmt_offset}"
       return str(self.line_num)
   ```

### Phase 4: Update Error Messages

1. **Statement-aware error messages**:
   ```python
   # Before:
   f"Error at line {pc.line_num}"

   # After (when helpful):
   f"Error at {pc.display_position()}"  # Shows "10.2" for multi-statement lines
   ```

2. **UI error highlighting**:
   - Use `error_info.error_pc` to highlight exact statement
   - Show statement offset in error display
   - Jump to exact statement location

## Testing Strategy

### Test 1: ERS# with Multi-Statement Errors
```basic
10 ON ERROR GOTO 1000
20 PRINT "Start"
30 A=1:B=2:C=1/0:D=4
40 PRINT "After (shouldn't see)"
1000 PRINT "Error at line"; ERL; "statement"; ERS
1010 PRINT "Expected: line 30 statement 2"
1020 RESUME NEXT
```

**Expected output:**
```
Start
Error at line 30 statement 2
Expected: line 30 statement 2
```

### Test 2: ERS# with Single Statement
```basic
10 ON ERROR GOTO 1000
20 X = 1/0
1000 PRINT "Error at line"; ERL; "statement"; ERS
1010 PRINT "Expected: line 20 statement 0"
```

**Expected output:**
```
Error at line 20 statement 0
Expected: line 20 statement 0
```

### Test 3: ErrorInfo PC Preservation
```python
# Unit test
try:
    # Execute: 10 A=1:B=2:C=1/0
    interp.tick()
except:
    assert interp.state.error_info.error_pc == PC(10, 2)
    assert interp.state.error_info.error_line == 10
    assert interp.state.error_info.error_stmt == 2
```

### Test 4: UI Error Highlighting
- Set error at line 100, statement 2
- Verify UI highlights exact statement (3rd statement on line)
- Verify error message shows statement position

## Benefits

1. **Precise error location**: Know exactly which statement failed
2. **Better debugging**: Users can identify problem in multi-statement lines
3. **Consistent with PC design**: Error handling uses PC throughout
4. **UI enhancement**: Debuggers can highlight exact failing statement
5. **Backwards compatible**: ERL# still works, new ERS# is optional

## Backwards Compatibility

- **ERL#** continues to work as before (line number only)
- **ERS#** is a new variable, doesn't break existing code
- **ErrorInfo.error_line** property maintains old behavior
- Old code using `error_info.error_line` continues to work

## Estimated Effort

- **Phase 1** (ERS# variable): 2 hours
- **Phase 2** (ErrorInfo PC): 2 hours
- **Phase 3** (Audit pc.line_num): 3 hours
- **Phase 4** (Error messages): 2 hours
- **Testing**: 2 hours

**Total**: ~11 hours

## Examples of pc.line_num Categories

### Category A: Should Use Full PC

```python
# src/interpreter.py line ~355
self.state.error_info = ErrorInfo(
    error_code=self._map_exception_to_error_code(e),
    error_line=pc.line_num,  # BAD: Loses stmt_offset
    error_message=str(e)
)
# Should be: error_pc=pc

# src/interpreter.py line ~843
self._invoke_error_handler(error_code, line_node.line_number, self.runtime.current_stmt_index)
# Should be: self._invoke_error_handler(error_code, runtime.pc)
```

### Category B: Line Number Is Correct

```python
# src/interpreter.py line ~280 (user-facing message)
self.io.output(f"Break in {pc}")  # OK: Shows PC string "PC(10.2)"
# Could also be: f"Break in line {pc.line_num}"

# src/interpreter.py line ~1184 (GOTO target)
if stmt.line_number == pc.line_num:  # OK: Checking if we're at target line
    ...

# Runtime variable setting
self.runtime.set_variable("ERL", pc.line_num)  # OK: ERL is defined as line number
```

### Category C: Could Use Helper Method

```python
# Breakpoint checking
if pc.line_num in self.state.breakpoints:  # Could be: pc.matches_line_breakpoint(breakpoints)
    ...

# Display formatting
f"Paused at line {pc.line_num}"  # Could be: f"Paused at {pc.display_position()}"
```

## Related Documentation

- `docs/dev/PC_REFACTORING_COMPLETE.md` - PC architecture overview
- `docs/dev/PC_OLD_EXECUTION_METHODS_TODO.md` - Complete PC migration
- MBASIC 5.21 manual - Error handling (ERR, ERL, ON ERROR)

## Notes

- ERS# follows MBASIC naming: # suffix for numeric variable
- 0-based to match PC.stmt_offset and Python conventions
- Statement 0 = first statement on line (consistent with PC design)
- Could also add ERR$ (error message string) for completeness
