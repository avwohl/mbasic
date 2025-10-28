# Case-Preserving Variable Names

⏳ **Status:** TODO

**Priority:** MEDIUM - Usability improvement for variable display

## Problem

Currently, the variable table stores all variable names in lowercase. This causes two issues:

### Issue 1: Variable Display
If a user names a variable `TargetAngle`, it displays as `targetangle` in the variable window. This looks wrong and makes the variable list harder to read.

### Issue 2: Lost Original Formatting
The original case formatting from the user's code is lost, even though BASIC is case-insensitive for variable names.

## Current Implementation

**Variable table structure:**
- Dictionary keyed on lowercase variable name: `{"targetangle": value}`
- Lookup is simple: `var_table[name.lower()]`
- Display shows lowercase: `"targetangle = 45"`

**Example:**
```basic
10 TargetAngle = 45
20 PRINT TargetAngle
```

**Current behavior:**
- Variable table: `{"targetangle": 45}`
- Variable window shows: `targetangle = 45` ❌

## Proposed Solution

### Case-Insensitive Lookup with Case Preservation

**Change variable table to preserve original case:**
- Store original case as typed by user
- Lookup using case-insensitive comparison
- Display using preserved case

**New structure:**
```python
# Option A: Store both original and normalized
var_table = {
    "targetangle": {  # lowercase key for lookup
        "name": "TargetAngle",  # preserved original case
        "value": 45,
        "type": "single"
    }
}

# Option B: Custom dict class with case-insensitive lookup
class CaseInsensitiveVarTable:
    def __init__(self):
        self._data = {}  # normalized_key -> (original_name, value, type)

    def __setitem__(self, name, value):
        # Store with normalized key, but preserve original name
        normalized = name.lower()
        if normalized not in self._data:
            self._data[normalized] = {"name": name, "value": value}
        else:
            # Keep original name, update value
            self._data[normalized]["value"] = value

    def __getitem__(self, name):
        # Lookup using normalized key
        return self._data[name.lower()]["value"]

    def get_original_name(self, name):
        # Get preserved case
        return self._data[name.lower()]["name"]
```

**Desired behavior:**
```basic
10 TargetAngle = 45
20 PRINT TargetAngle
```

- Variable table stores: `{"targetangle": {"name": "TargetAngle", "value": 45}}`
- Variable window shows: `TargetAngle = 45` ✅
- Lookup `targetangle`, `TARGETANGLE`, `TargetAngle` all work ✅

## Handling Conflicts

**Case where same variable appears with different cases:**

```basic
10 TargetAngle = 45
20 targetangle = 50
30 TARGETANGLE = 55
```

**⚠️ IMPORTANT:** Conflict handling should be **user-configurable** via settings system.

See: `SETTINGS_SYSTEM_TODO.md` for full settings implementation plan.

**Setting:** `variable_case_conflict`

### Option 1: `first_wins` (DEFAULT)
- First occurrence defines the canonical case: `TargetAngle`
- All subsequent uses update the same variable
- When saved from AST, all variables use first case: `TargetAngle = 55`
- **Silent behavior** - no errors or warnings

**Pros:**
- Simple and predictable
- Matches typical programming behavior
- Encourages consistent naming
- Works perfectly for programs with consistent case

**Cons:**
- If first use is all-lowercase, that becomes canonical
- User might want to change canonical case later

### Option 2: `error`
- First occurrence defines the canonical case: `TargetAngle`
- Subsequent different case triggers error
- User must fix inconsistency or change setting
- Error message: `"Variable 'targetangle' conflicts with existing 'TargetAngle' at line 10"`

**Pros:**
- Enforces consistency
- Makes conflicts immediately visible
- User maintains full control

**Cons:**
- May be too strict for casual users
- Requires user intervention

### Option 3: `prefer_upper`
- Track all case variations used
- On conflict, prefer characters that are uppercase
- `TargetAngle` + `targetangle` + `TARGETANGLE` → `TARGETANGLE`
- When saved from AST, uses uppercase-preferred version

**Pros:**
- Automatic resolution
- Matches classic BASIC convention (uppercase keywords)
- Consistent across conflicts

**Cons:**
- May not match user's preferred style
- ALL UPPERCASE can be less readable

### Option 4: `prefer_lower`
- Track all case variations used
- On conflict, prefer characters that are lowercase
- `TargetAngle` + `targetangle` + `TARGETANGLE` → `targetangle`
- When saved from AST, uses lowercase-preferred version

**Pros:**
- Automatic resolution
- Matches modern convention (lowercase identifiers)
- Consistent across conflicts

**Cons:**
- May not match user's preferred style
- all lowercase can be less readable for long names

### Option 5: `prefer_mixed`
- Track all case variations used
- On conflict, prefer mixed case (camelCase/PascalCase)
- `TargetAngle` + `targetangle` + `TARGETANGLE` → `TargetAngle`
- Heuristic: prefer version with both upper and lower case

**Pros:**
- Automatic resolution
- Matches modern coding style
- Most readable for multi-word identifiers

**Cons:**
- Heuristic may pick "wrong" version
- More complex to implement

## Recommended Approach

**Default to `first_wins` (Option 1)** because:
1. Simple to implement
2. Predictable behavior
3. Works perfectly for programs with consistent case (the common case)
4. BASIC is already case-insensitive, so conflicts are rare
5. Silent - doesn't interrupt workflow

**But make it configurable** so users can choose:
- `error` - Strict mode, enforce consistency
- `prefer_upper` - Classic BASIC style
- `prefer_lower` - Modern style
- `prefer_mixed` - Readability preference

**For programs with inconsistent case:**
- Variable still works correctly (same value)
- Display depends on conflict mode setting
- User can change setting or fix code

## Implementation Plan

### Phase 1: Update Variable Table Structure
- Change from `str -> value` to `str -> {name, value, type}`
- Update all variable storage code
- Keep lookup case-insensitive

### Phase 2: Preserve First Case
- When variable first created, store original case
- When variable updated, keep original case
- Update variable display to show preserved case

### Phase 3: Update Parser/Interpreter
- Modify `VariableNode` to preserve original case
- Update variable assignment to use new structure
- Update variable lookup to use case-insensitive key

### Phase 4: Update UI
- Variable window displays preserved case
- Variable tooltips show preserved case
- Ensure all UIs (CLI, curses, TK) updated

### Phase 5: Testing
- Test with mixed-case variable names
- Test with all-lowercase (should still work)
- Test with all-uppercase (should still work)
- Test with inconsistent case (verify first-wins)

## Files to Modify

### Core Implementation
- `src/interpreter.py` - Variable table structure and storage
- `src/ast_nodes.py` - VariableNode case preservation
- `src/parser.py` - Store original case in VariableNode

### UI Updates
- `src/ui/tk_ui.py` - Variable window display
- `src/ui/curses_ui.py` - Variable panel display
- `src/ui/cli_ui.py` - Variable listing

### Testing
- `tests/test_variables.py` - Test case preservation
- `tests/test_case_insensitive.py` - Test lookup behavior

## Edge Cases

### Case 1: DEFINT with mixed case
```basic
10 DEFINT T
20 TargetAngle = 45
```
- Type inference works on normalized name: `targetangle`
- Display preserves case: `TargetAngle`

### Case 2: Array names
```basic
10 DIM Values(10)
20 Values(1) = 100
30 values(2) = 200
```
- Array name preserved: `Values`
- Display: `Values(1) = 100`, `Values(2) = 200`

### Case 3: Function names
```basic
10 DEF FNSquare(X) = X * X
20 PRINT FNSquare(5)
30 PRINT fnsquare(3)
```
- Function name preserved: `FNSquare`
- Both calls work (case-insensitive)

## Benefits

1. **Readability:** Variable window shows names as user typed them
2. **Professional:** Matches modern programming expectations
3. **Backward compatible:** Doesn't break case-insensitive lookup
4. **Minimal complexity:** First-wins strategy is simple

## Testing Plan

### Test Cases
1. **Single case style:**
   - All lowercase: `targetangle`
   - All uppercase: `TARGETANGLE`
   - Mixed case: `TargetAngle`

2. **Inconsistent case:**
   - First lowercase, then mixed
   - First mixed, then uppercase
   - Multiple different cases

3. **Special cases:**
   - Arrays with mixed case
   - Functions with mixed case
   - Type suffixes: `Value!` vs `VALUE!`

4. **UI verification:**
   - Variable window shows preserved case
   - Tooltips show preserved case
   - LIST command shows preserved case (if applicable)

## Success Criteria

- ✅ Variables display in original case
- ✅ Lookup remains case-insensitive
- ✅ First occurrence defines canonical case
- ✅ All UIs show preserved case
- ✅ No breaking changes to existing programs
- ✅ Performance not impacted

## Related Issues

This is related to the type suffix serialization fix (completed in v1.0.85):
- Both preserve user's original input
- Both distinguish between "what the user typed" vs "what the interpreter inferred"
- Both are about maintaining fidelity to source code

## Notes

- Classic BASIC interpreters typically converted everything to uppercase
- Modern convention is to preserve case for display
- This brings MBASIC interpreter closer to modern IDE behavior
- Similar to how Python preserves case but does case-insensitive imports (on Windows)

### Historical Note

This approach to case handling (case-insensitive lookup while preserving original case for display) was proposed by **William Wulf**, a professor at Carnegie Mellon University, around 1984. This design elegantly balances the user-friendliness of case-insensitive identifiers with the readability benefits of preserving the programmer's original formatting intent.
