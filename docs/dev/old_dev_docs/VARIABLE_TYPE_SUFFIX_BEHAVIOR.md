# Variable Type Suffix Behavior in MBASIC

## Question

What happens with `K`, `K!`, `K%` - are they the same variable or different variables?

## Answer from Real MBASIC 5.21

Testing with real MBASIC 5.21:

```basic
10 K = 100
20 K! = 3.14
30 K% = 42
40 PRINT "K ="; K
50 PRINT "K! ="; K!
60 PRINT "K% ="; K%
70 SYSTEM
```

**Output:**
```
K = 3.14
K! = 3.14
K% = 42
```

## Key Finding: K and K! are THE SAME VARIABLE!

**Rules:**
1. `K` without suffix defaults to single-precision float (same as `K!`)
2. `K!` explicitly specifies single-precision float
3. **Therefore `K` and `K!` are the SAME variable** - they share the same storage
4. `K%` (integer) is a **DIFFERENT variable** - separate storage
5. `K$` (string) would be a **DIFFERENT variable** - separate storage
6. `K#` (double) would be a **DIFFERENT variable** - separate storage

## General Rule

**Type suffixes create different variables EXCEPT when the suffix matches the default type.**

### Default Types (without DEFINT/DEFSNG/etc.)
- No suffix → Single precision float (`!`)
- `!` → Single precision float
- `%` → Integer (16-bit)
- `#` → Double precision float
- `$` → String

So:
- `X` and `X!` → **SAME variable** (both single precision)
- `X` and `X%` → **DIFFERENT variables**
- `X` and `X#` → **DIFFERENT variables**
- `X` and `X$` → **DIFFERENT variables**
- `X!` and `X%` → **DIFFERENT variables**
- `X!` and `X#` → **DIFFERENT variables**
- etc.

### With DEFINT A-Z

```basic
10 DEFINT A-Z
20 K = 100
30 K% = 42
40 PRINT K, K%
```

Now `K` defaults to integer:
- `K` and `K%` → **SAME variable** (both integer)
- `K` and `K!` → **DIFFERENT variables**

## Our Implementation

Looking at `/home/wohl/cl/mbasic/src/runtime.py`, the `_resolve_variable_name()` method handles this:

```python
def _resolve_variable_name(name, type_suffix, def_type_map=None):
    """
    Resolve the full variable name with type suffix.

    Args:
        name: Variable base name (e.g., 'x', 'foo')
        type_suffix: Explicit type suffix ($, %, !, #) or None/empty string
        def_type_map: Optional dict mapping first letter to default TypeInfo

    Returns:
        tuple: (full_name, type_suffix) where full_name is lowercase name with suffix
    """
    name = name.lower()

    # If explicit suffix provided, use it
    if type_suffix:
        return (name + type_suffix, type_suffix)

    # No explicit suffix - check DEF type map
    if def_type_map:
        first_letter = name[0]
        if first_letter in def_type_map:
            var_type = def_type_map[first_letter]
            # Convert DEF type to suffix
            if var_type == TypeInfo.STRING:
                type_suffix = '$'
            elif var_type == TypeInfo.INTEGER:
                type_suffix = '%'
            elif var_type == TypeInfo.DOUBLE:
                type_suffix = '#'
            elif var_type == TypeInfo.SINGLE:
                type_suffix = '!'
            return (name + type_suffix, type_suffix)

    # Default to single precision
    return (name + '!', '!')
```

**This is CORRECT!**

When you write `K`:
1. No explicit suffix
2. Checks def_type_map - if `DEFINT A-Z` was used, returns `k%`
3. Otherwise defaults to single precision: `k!`

When you write `K!`:
1. Explicit suffix provided: `!`
2. Returns `k!`

**Both resolve to the same key: `k!`** (assuming no DEFINT)

## Storage Keys

Variables are stored in `runtime._variables` dict with keys like:
- `k!` - K or K! (single precision)
- `k%` - K% (integer)
- `k#` - K# (double precision)
- `k$` - K$ (string)

All variable names are lowercase in storage.

## Implications for Case-Preserving Variables TODO

When implementing case-preserving variables, we need to handle:

1. **Variable key:** Still `k!` (lowercase with suffix)
2. **Display name:** Preserve case: `TargetAngle!` or `TargetAngle` (depending on explicit_type_suffix)
3. **Conflict detection:** Must consider that `K` and `K!` are the same variable

**Example:**
```basic
10 TargetAngle = 45      ' Stored as targetangle! (default single)
20 targetangle! = 50     ' SAME variable as line 10
30 TargetAngle% = 100    ' DIFFERENT variable (targetangle%)
```

**Case preservation should track:**
- `targetangle!` → display as `TargetAngle` (first occurrence)
- `targetangle%` → display as `TargetAngle%` (first occurrence)

## Implications for Spacing Preservation TODO

When preserving token positions, remember:
- `K` (no suffix) still needs to track default type
- `K!` (with suffix) tracks explicit suffix
- These resolve to same storage key but may have different tokens

## Test Cases

### Test 1: Same variable (default type)
```basic
10 X = 100
20 X! = 200
30 PRINT X, X!
' Output: 200, 200 (same variable)
```

### Test 2: Different variables
```basic
10 X = 100
20 X% = 200
30 PRINT X, X%
' Output: 100, 200 (different variables)
```

### Test 3: With DEFINT
```basic
10 DEFINT A-Z
20 X = 100
30 X% = 200
40 PRINT X, X%
' Output: 200, 200 (same variable, both integer)
```

### Test 4: DEFINT doesn't affect explicit suffixes
```basic
10 DEFINT A-Z
20 X = 100
30 X! = 200
40 PRINT X, X!
' Output: 100, 200 (different variables: X is integer, X! is single)
```

## Summary

✅ **Our implementation is CORRECT**

- Variables with different type suffixes are different variables
- EXCEPT when suffix matches the default type (then they're the same)
- Default type is single-precision (`!`) unless changed by DEFINT/DEFSNG/etc.
- All variables stored lowercase with suffix as key
- `_resolve_variable_name()` correctly handles type resolution

## Related Issues

- **Type suffix serialization (v1.0.85):** Don't output inferred suffixes
- **Case-preserving variables (TODO):** Must handle that K and K! are same variable
- **Spacing preservation (TODO):** K vs K! have different tokens but same storage

## Historical Note

This behavior is standard across all MBASICs:
- BASIC-80 (MBASIC 5.21) - 1981
- GW-BASIC - 1983
- QuickBASIC - 1985
- QBasic - 1991

The rule has always been: **type suffix creates storage key**, default types fill in missing suffixes.

## Testing Our Implementation

### Test Results: ✅ CORRECT!

Tested our implementation with the following code:

```python
runtime.set_variable('K', None, 100, def_type_map=None, token=token)   # K = 100
runtime.set_variable('K', '!', 3.14, def_type_map=None, token=token)   # K! = 3.14
runtime.set_variable('K', '%', 42, def_type_map=None, token=token)     # K% = 42
```

**Our storage:**
- `k!` = 3.14
- `k%` = 42

**Reading back:**
- `K` → 3.14
- `K!` → 3.14
- `K%` → 42

**Real MBASIC 5.21:**
- `K` → 3.14
- `K!` → 3.14
- `K%` → 42

**✅ Perfect match!** Our implementation correctly handles type suffixes exactly like real MBASIC.

## Verification with Real MBASIC

Testing with real MBASIC 5.21:

```bash
cd tests
(cat type_suffix_test.bas && echo "RUN") | timeout 10 tnylpo ../com/mbasic
```

Output from real MBASIC:
```
K = 3.14
K! = 3.14
K% = 42
```

**✅ Our implementation is CORRECT!**
