# De-Noneify Codebase - Refactoring TODO

⏳ **Status**: PARTIALLY COMPLETE (Phase 1-3 done, Phase 4 deferred)

## Problem

The codebase has extensive use of `None` checks that obscure intent:
- 119 occurrences of `' is None'`
- 140 occurrences of `' is not None'`

While `is None` checks aren't inherently bad, many of them hide the actual semantic meaning:
- Does `next_line is None` mean "at end of program"?
- Does `current_token is None` mean "at end of expression"?
- Does `value is None` mean "uninitialized" or "optional not provided"?

## Goal

Replace semantic `None` checks with clearly-named predicates and state methods that express **intent**, not implementation.

## Examples of Good Replacements

### Control Flow State
```python
# BEFORE (obscure)
if self.runtime.next_line is not None:
    # Handle GOTO/GOSUB jump

# AFTER (clear intent)
if self.runtime.has_pending_jump():
    # Handle GOTO/GOSUB jump
```

### Parser/Lexer State
```python
# BEFORE (obscure)
if self.current_token is None:
    # End of expression

# AFTER (clear intent)
if self.at_end_of_expression():
    # End of expression
```

### Program Execution
```python
# BEFORE (obscure)
if self.interpreter is None:
    return False

# AFTER (clear intent)
if not self.has_active_interpreter():
    return False
```

### Optional Parameters
```python
# BEFORE (obscure)
def execute(self, limits=None):
    if limits is None:
        limits = create_default_limits()

# AFTER (still uses None, but more explicit)
def execute(self, limits: Optional[ResourceLimits] = None):
    if limits is None:  # OK: checking optional parameter
        limits = create_default_limits()
```

## When `is None` is OKAY

Some uses of `None` checks are perfectly fine and should **NOT** be changed:

1. **Checking optional function parameters** (with type hints)
   ```python
   def foo(bar: Optional[int] = None):
       if bar is None:  # OK: explicit optional param
           bar = 10
   ```

2. **Explicitly uninitialized state that needs lazy init**
   ```python
   self._cache = None  # Explicitly "not yet initialized"
   if self._cache is None:
       self._cache = self._build_cache()
   ```

3. **Protocol/interface methods that return None for "not found"**
   ```python
   def find_variable(name: str) -> Optional[Variable]:
       return self.vars.get(name)  # None = not found (OK)
   ```

## Progress Summary (v1.0.299)

### Completed ✅

**Phase 1: Analysis**
- Created `utils/analyze_none_checks.py` - categorization tool
- Found 326 total None checks (284 in semantic_analyzer.py are legitimate)
- Identified 42 actionable checks in core modules

**Phase 2: Helper Methods**
Added to `src/runtime.py`:
- `has_error_handler()` - Check if ON ERROR GOTO installed
- `has_active_loop(var_name=None)` - Check if FOR loop active

Added to `src/parser.py`:
- `has_more_tokens()` - Check if tokens remaining
- `at_end_of_tokens()` - Check if exhausted tokens

**Phase 3: Replacements**
- `src/interpreter.py`: 2 error handler checks replaced
- `src/parser.py`: 8 token None checks replaced with semantic methods

**Impact:**
- ~10 None checks replaced with clear semantic names
- Improved code readability in high-traffic paths
- All tests passing

### Deferred to Future

**Phase 4:** UI None checks (interpreter existence) - low priority, working fine
**Phase 5:** Optional parameters - already well-typed with type hints

## Implementation Strategy

### Phase 1: Identify Semantic Categories ✅ COMPLETE (1-2 hours)
Search codebase and categorize all `is None` / `is not None` uses:
- Control flow state (GOTO/GOSUB jumps)
- Parser/lexer position
- Interpreter state
- Optional parameters (leave as-is)
- Lazy initialization (leave as-is)
- Error/sentinel values

```bash
# Find all None checks
grep -rn ' is None' src/ --include="*.py" > /tmp/none_checks.txt
grep -rn ' is not None' src/ --include="*.py" >> /tmp/none_checks.txt

# Analyze by file/context
python3 utils/categorize_none_checks.py
```

### Phase 2: Create Helper Methods ✅ COMPLETE (2-3 hours)
Add clearly-named predicate methods to replace common None checks:

**Runtime state (src/runtime.py)**:
- `has_pending_jump()` → replaces `self.next_line is not None`
- `is_sequential_execution()` → replaces `self.next_line is None`
- `has_gosub_stack()` → replaces `len(self.gosub_stack) > 0`

**Parser state (src/parser.py)**:
- `at_end_of_tokens()` → replaces `self.current_token is None`
- `has_more_tokens()` → replaces `self.current_token is not None`
- `at_end_of_line()` → replaces token type checks

**Interpreter state (src/interpreter.py)**:
- `has_active_program()` → replaces checking if program exists
- `is_program_running()` → replaces state checks
- `can_execute_immediate()` → already exists, use it!

**UI state (src/ui/*.py)**:
- `has_active_interpreter()` → replaces `self.interpreter is not None`
- `has_loaded_program()` → replaces `self.program.lines`
- `is_runtime_initialized()` → replaces `self.runtime is not None`

### Phase 3: Replace Usage Sites ✅ PARTIALLY COMPLETE (2 hours done)
Systematically replace None checks with the new methods:
1. Start with highest-frequency patterns
2. Replace file-by-file
3. Run tests after each file
4. Commit incrementally

### Phase 4: Testing ✅ COMPLETE (1 hour)
- Run full test suite
- Test each UI backend (CLI, curses, TK, web)
- Verify immediate mode still works
- Check program execution

## Success Metrics

- Reduce `is None` occurrences from 119 to < 40 (optional params only)
- Reduce `is not None` occurrences from 140 to < 40
- Every remaining `is None` should be:
  - Optional parameter check, OR
  - Lazy initialization, OR
  - Documented with `# OK:` comment explaining why

## Priority

**MEDIUM** - This is a code quality improvement, not a bug fix. Good for:
- When between features
- Before major refactoring
- During code review/cleanup sessions

## Estimated Time

**6-10 hours total** (can be split across multiple sessions)

## References

Examples already in codebase:
- `has_pending_jump()` in src/runtime.py (recent addition)
- `is_sequential_execution()` in src/runtime.py (recent addition)
- `can_execute_immediate()` in src/immediate_executor.py

## Notes

- Don't rush this - take time to understand each None check's semantic meaning
- Consider adding type hints while refactoring (Optional[T])
- Look for patterns that appear multiple times (good candidates for helpers)
- This will make the code much more readable and maintainable
