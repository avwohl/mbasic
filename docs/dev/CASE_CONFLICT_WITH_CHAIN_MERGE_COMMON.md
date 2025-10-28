# Case Conflict Interactions with CHAIN, MERGE, and COMMON

⏳ **Status**: Analysis for Future Implementation

## Overview

This document analyzes how the variable case conflict system interacts with MBASIC's program chaining features: CHAIN, MERGE, and COMMON.

## Current Implementation Status

### ✅ Implemented Features

1. **COMMON Statement** (`execute_common()`)
   - Declares variables to be shared across CHAIN operations
   - Stores variable names in `runtime.common_vars` list
   - Order matters (MBASIC 5.21 behavior)
   - Currently stores variable base names (without type suffixes)

2. **CHAIN Statement** (`cmd_chain()`)
   - Loads and executes another BASIC program
   - Options:
     - `MERGE`: Overlay instead of replace
     - `ALL`: Pass all variables
     - Line number: Start execution point
     - `DELETE range`: Delete lines after merge

3. **MERGE Statement** (`cmd_merge()`)
   - Merges program from disk into current program
   - Preserves all existing variables

4. **Variable Preservation Logic** (`cmd_chain()`, line 579-600):
   ```python
   if all_flag or merge:
       # Save all variables
       saved_variables = self.program_runtime.get_all_variables()
   elif self.program_runtime.common_vars:
       # Save only COMMON variables (in order)
       # Tries all type suffixes: %, $, !, #
   ```

### ✅ Variable Case Conflict System (v1.0.106-109)

- Tracks all case variants per variable
- 5 policies: first_wins, error, prefer_upper, prefer_lower, prefer_mixed
- Stores `original_case` in variable metadata
- Works with `get_all_variables()` and `set_variable()`

## Potential Issues with Current Implementation

### Issue 1: COMMON Variable Case Preservation

**Scenario:**
```basic
' PROGRAM1.BAS
10 COMMON TargetAngle
20 TargetAngle = 45
30 CHAIN "PROGRAM2.BAS"
```

```basic
' PROGRAM2.BAS
10 COMMON targetangle
20 PRINT targetangle  ' Should be 45
```

**Question:** When PROGRAM2 loads, should `targetangle` match `TargetAngle` from PROGRAM1?

**Current Behavior:**
- COMMON stores base names: `['targetangle']` (normalized to lowercase)
- Case variants tracked separately in `_variable_case_variants`
- When restoring, uses `variable_exists()` to find variable with any suffix
- **BUT**: Case matching may not work correctly across programs

**Problem:**
1. PROGRAM1 stores variable as `targetangle!` with `original_case='TargetAngle'`
2. PROGRAM2 declares `COMMON targetangle`
3. Case conflict system may:
   - With `first_wins`: Use PROGRAM1's `TargetAngle` (correct!)
   - With `error`: Raise error because cases differ (too strict!)
   - With `prefer_upper`: Choose `TargetAngle` (correct!)

### Issue 2: MERGE Case Conflicts

**Scenario:**
```basic
' Current program
10 TargetAngle = 45
```

```basic
' File to merge: OVERLAY.BAS
20 targetangle = 90  ' Same variable, different case
30 PRINT targetangle
```

**After MERGE "OVERLAY.BAS":**
```basic
10 TargetAngle = 45
20 targetangle = 90
30 PRINT targetangle
```

**Question:** Should line 20 trigger a case conflict?

**Current Behavior:**
- MERGE preserves all existing variables
- New code is parsed and may reference same variables with different case
- Case conflict policy applies during execution

**With Different Policies:**
- `first_wins`: Line 10's `TargetAngle` wins, line 20 updates same variable
- `error`: Would raise error when line 20 executes
- `prefer_upper`: Both use `TargetAngle`
- `prefer_lower`: Both use `targetangle`

### Issue 3: CHAIN ALL - Full Variable Transfer

**Scenario:**
```basic
' PROGRAM1.BAS with 100 variables
10 DIM Matrix(10,10)
20 FOR I = 1 TO 100
30   TargetAngle = I
40   Counter = I * 2
50 NEXT I
60 CHAIN "PROGRAM2.BAS",,ALL  ' Pass ALL variables
```

```basic
' PROGRAM2.BAS
10 PRINT Counter  ' Access variable from PROGRAM1
```

**Question:** How are case variants transferred?

**Current Behavior:**
- `get_all_variables()` returns dict with `original_case` field
- `update_variables()` bulk restores variables
- **BUT**: `update_variables()` uses `set_variable_raw()` which bypasses case conflict checking!

**Potential Problem:**
```python
def update_variables(self, variables):
    """Bulk update variables from get_all_variables()"""
    for var_info in variables:
        # ...
        if not var_info['is_array']:
            self.set_variable_raw(full_name, var_info['value'])
```

This bypasses `_check_case_conflict()` and doesn't restore `original_case`!

### Issue 4: Case Variant History Across Programs

**Question:** Should case variant tracking persist across CHAIN?

**Example:**
```basic
' PROGRAM1.BAS
10 TargetAngle = 45
20 targetangle = 90  ' Conflict detected
30 CHAIN "PROGRAM2.BAS",,ALL
```

```basic
' PROGRAM2.BAS
10 PRINT targetangle  ' Fresh start, or remember conflict?
```

**Current State:**
- `_variable_case_variants` is in runtime
- Runtime is replaced during CHAIN (unless ALL or COMMON)
- Variant history is lost

## Recommended Solutions

### Solution 1: Enhance Variable Transfer Methods

**Update `update_variables()` to preserve case:**

```python
def update_variables(self, variables):
    """
    Bulk update variables.

    Args:
        variables: list of variable dicts (from get_all_variables())
                  Each dict contains: name, type_suffix, original_case, value, ...
    """
    for var_info in variables:
        # Reconstruct full name
        full_name = var_info['name'] + var_info['type_suffix']

        if not var_info['is_array']:
            # IMPORTANT: Restore original_case metadata
            if full_name not in self._variables:
                self._variables[full_name] = {
                    'value': var_info['value'],
                    'last_read': None,
                    'last_write': None,
                    'original_case': var_info.get('original_case', var_info['name'])
                }
            else:
                self._variables[full_name]['value'] = var_info['value']
                # Preserve or update original_case based on policy?
                # For CHAIN ALL, probably want to preserve source program's case
                if 'original_case' in var_info:
                    self._variables[full_name]['original_case'] = var_info['original_case']
```

### Solution 2: COMMON Variable Case Matching

**Two Approaches:**

**A. Strict Matching (Recommended for `error` policy):**
- COMMON variables must match case exactly
- Enforces consistency across program boundaries
- Error if PROGRAM1 has `COMMON TargetAngle` and PROGRAM2 has `COMMON targetangle`

**B. Loose Matching (Recommended for other policies):**
- Match COMMON variables case-insensitively
- Apply case conflict policy across programs
- Store canonical case from first program

**Implementation:**
```python
def execute_common(self, stmt):
    """Execute COMMON statement"""
    for var_name in stmt.variables:
        # Extract base name and type suffix
        base_name, type_suffix = split_variable_name_and_suffix(var_name)

        # Store with original_case if provided
        original_case = getattr(stmt, 'original_case_for_vars', {}).get(var_name, var_name)

        # Check if already in common_vars (case-insensitive)
        normalized_name = base_name.lower()
        existing = [v for v in self.runtime.common_vars if v['name'].lower() == normalized_name]

        if existing and self.settings_manager:
            policy = self.settings_manager.get("variables.case_conflict", "first_wins")
            if policy == "error" and existing[0]['original_case'] != original_case:
                raise RuntimeError(f"COMMON case conflict: '{existing[0]['original_case']}' vs '{original_case}'")

        if not existing:
            self.runtime.common_vars.append({
                'name': base_name,
                'type_suffix': type_suffix,
                'original_case': original_case
            })
```

### Solution 3: MERGE Case Policy Options

**Add setting:** `merge.case_conflict_behavior`

Options:
- `inherit`: Merged code inherits existing variable cases (default)
- `error`: Raise error on case conflicts between existing and merged code
- `prefer_existing`: Always use existing program's case
- `prefer_merged`: Use merged code's case

**Use Case:**
- Team merging code from different sources
- Enforcing consistent style
- Debugging case conflicts in complex programs

### Solution 4: Case Variant History Transfer

**Option A: Don't Transfer (Recommended)**
- Fresh start for case variants in new program
- Simpler implementation
- Matches MBASIC 5.21 behavior (no case tracking)

**Option B: Transfer Variants (Advanced)**
- Include `case_variants` in serialization
- Transfer `_variable_case_variants` during CHAIN ALL
- Preserves conflict detection across programs
- More complex, probably unnecessary

## Test Scenarios

### Test 1: COMMON Variable Transfer with Case
```python
def test_common_case_transfer():
    # PROGRAM1 with COMMON TargetAngle
    # PROGRAM2 with COMMON targetangle
    # Verify variable value transfers correctly
    # Verify case policy applies
```

### Test 2: MERGE with Case Conflicts
```python
def test_merge_case_conflict():
    # Create program with TargetAngle = 45
    # MERGE overlay with targetangle = 90
    # Verify behavior with different policies
```

### Test 3: CHAIN ALL with Case Preservation
```python
def test_chain_all_case_preservation():
    # PROGRAM1 sets MyVar = 100 (mixed case)
    # CHAIN "PROGRAM2.BAS",,ALL
    # Verify MyVar accessible in PROGRAM2
    # Verify original_case preserved
```

## Priority and Impact

**Priority:** Medium

**Impact:**
- **High** for `error` policy - could break valid programs
- **Medium** for `first_wins` - mostly works but may surprise users
- **Low** for other policies - primarily cosmetic

**Recommendation:**
1. Fix `update_variables()` to preserve `original_case` (HIGH priority)
2. Document current behavior in user manual
3. Implement strict matching for `error` policy if needed
4. Consider `merge.case_conflict_behavior` setting (LOW priority)

## Related Features

- Variable case conflict system (v1.0.106-109) - ✅ COMPLETED
- CHAIN/MERGE/COMMON implementation - ✅ IMPLEMENTED
- Settings system - ✅ COMPLETED

## Notes

- MBASIC 5.21 had no case tracking, so this is uncharted territory
- Most programs use consistent casing, so conflicts rare
- Error policy is most affected - need clear documentation
- CHAIN ALL is advanced feature, users probably understand implications

## References

- `src/runtime.py` - Variable storage and COMMON tracking
- `src/interpreter.py` - execute_common(), execute_chain(), execute_merge()
- `src/interactive.py` - cmd_chain() with variable preservation
- Variable case conflict design (v1.0.106-109)
