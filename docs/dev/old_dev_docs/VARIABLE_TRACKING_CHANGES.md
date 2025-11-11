# Variable Tracking API Changes

## Summary

The variable access tracking system has been updated to make token parameters **mandatory** for all program execution calls, ensuring consistent tracking of all variable accesses.

## Breaking Changes

### 1. `get_variable()` - Token Now Required

**Before:**
```python
value = runtime.get_variable('x', '!')  # Optional token
```

**After:**
```python
# REQUIRED: Must pass token for program execution
token = self._make_token_info(expr)
value = runtime.get_variable('x', '!', token=token)

# Raises ValueError if token is None
```

### 2. `set_variable()` - Token Now Required

**Before:**
```python
runtime.set_variable('x', '!', 10)  # Optional token
```

**After:**
```python
# REQUIRED: Must pass token for program execution
token = self._make_token_info(stmt.variable)
runtime.set_variable('x', '!', 10, token=token)

# Exception: debugger_set=True allows token to be None
runtime.set_variable('x', '!', 999, debugger_set=True)
```

### 3. New Method: `get_variable_for_debugger()`

**Purpose:** Read variables for debugging/inspection **without** updating tracking metadata.

**Before:**
```python
value = runtime.get_variable('x', '!')  # Would update tracking
```

**After:**
```python
# Use this in debuggers/inspectors to avoid polluting tracking
value = runtime.get_variable_for_debugger('x', '!')
```

## Migration Guide

### For Interpreter Code

All interpreter code has been updated automatically. No action needed.

### For Debugger/Inspector Code

**Old pattern:**
```python
# Reading variable in debugger
value = runtime.get_variable(var_name, type_suffix)
```

**New pattern:**
```python
# Use dedicated debugger method
value = runtime.get_variable_for_debugger(var_name, type_suffix)
```

### For Test Code

**Old pattern:**
```python
runtime.set_variable('test', '%', 100)
value = runtime.get_variable('test', '%')
```

**New pattern:**
```python
# Use debugger_set for test setup
runtime.set_variable('test', '%', 100, debugger_set=True)

# Use debugger method for reading
value = runtime.get_variable_for_debugger('test', '%')

# OR create a dummy token
class TokenInfo:
    def __init__(self, line, position):
        self.line = line
        self.position = position

token = TokenInfo(0, 0)
runtime.set_variable('test', '%', 100, token=token)
value = runtime.get_variable('test', '%', token=token)
```

## Rationale

### Why Make Token Mandatory?

1. **Consistency**: Ensures all variable accesses during program execution are tracked
2. **Clarity**: Explicit distinction between program execution and debugging
3. **Data Quality**: Prevents incomplete tracking data
4. **Intent**: Forces developers to think about whether they're executing or inspecting

### Separate Read/Write Timestamps

- `last_read`: Tracks GET operations (variable is read)
- `last_write`: Tracks SET operations (variable is written)
- Timestamps use `time.perf_counter()` for nanosecond precision

### Debugger Flag

- `debugger_set`: Marks variables modified by debugger, not by program
- Useful for distinguishing program state from debugging artifacts

## API Reference

### `get_variable(name, type_suffix=None, def_type_map=None, token=None)`

- **Purpose**: Get variable value during program execution
- **Token**: **REQUIRED** - Raises ValueError if None
- **Tracking**: Updates `last_read` with timestamp and location
- **Use**: All normal variable reads in interpreter

### `set_variable(name, type_suffix, value, def_type_map=None, token=None, debugger_set=False)`

- **Purpose**: Set variable value during program execution or debugging
- **Token**: **REQUIRED** unless `debugger_set=True` - Raises ValueError if None and not debugger_set
- **Tracking**: Updates `last_write` with timestamp and location (if token provided)
- **Debugger Flag**: Set `debugger_set=True` for debugger modifications
- **Use**: All assignments in interpreter

### `get_variable_for_debugger(name, type_suffix=None, def_type_map=None)`

- **Purpose**: Get variable value for debugging/inspection
- **Token**: Not accepted (would defeat purpose)
- **Tracking**: **Does NOT update** any tracking metadata
- **Use**: Debuggers, inspectors, watch windows, variable displays

### `get_variables_by_recent_access(include_metadata=False)`

- **Purpose**: Get all variables sorted by most recent access
- **Sorting**: Uses max of read/write timestamps
- **Metadata**: Optionally include full tracking metadata
- **Use**: Debugger variable displays, analysis tools

## Implementation Details

### Token Info Structure

```python
class TokenInfo:
    def __init__(self, line, position):
        self.line = line      # Line number in source
        self.position = position  # Column position in line
```

### Metadata Structure

```python
{
    'x!': {
        'last_read': {
            'line': 100,
            'position': 5,
            'timestamp': 1234.567890  # perf_counter()
        },
        'last_write': {
            'line': 95,
            'position': 10,
            'timestamp': 1234.500000
        },
        'debugger_set': False
    }
}
```

## Testing

All tests have been updated and pass:

```bash
python3 test_variable_tracking.py
```

**Test Coverage:**
- ✅ Token mandatory for get_variable
- ✅ Token mandatory for set_variable
- ✅ debugger_set=True allows token=None for set_variable
- ✅ get_variable_for_debugger doesn't update tracking
- ✅ Separate read/write timestamps
- ✅ High-precision timestamps (perf_counter)
- ✅ Sorting by recent access

## Error Messages

### ValueError on Missing Token

```python
>>> runtime.get_variable('x', '!')
ValueError: get_variable() requires token parameter. Use get_variable_for_debugger() for debugging.

>>> runtime.set_variable('x', '!', 10)
ValueError: set_variable() requires token parameter. Use debugger_set=True for debugger writes.
```

## Benefits

1. **Explicit Intent**: Clear separation between execution and inspection
2. **Complete Tracking**: All program variable accesses are tracked
3. **Debugger Safety**: Debugger operations don't pollute tracking data
4. **Better Analysis**: Accurate access patterns for optimization
5. **Type Safety**: Errors at call site instead of silent incorrect behavior

## Backward Compatibility

**Breaking Change**: This is intentionally a breaking change to ensure correct usage.

- Old code calling `get_variable()` without token will raise ValueError
- Old code calling `set_variable()` without token will raise ValueError
- Migration is straightforward: use `get_variable_for_debugger()` or provide token

## Future Enhancements

1. **Array Element Tracking**: Track array[subscript] accesses individually
2. **Access History**: Keep full history instead of just last access
3. **Access Counts**: Track total read/write counts per variable
4. **Hot Variable Detection**: Identify most frequently accessed variables
5. **Access Pattern Analysis**: Detect sequential/random access patterns

## Conclusion

These changes enforce best practices by making token tracking mandatory for program execution while providing a clear, separate API for debugging/inspection that doesn't affect tracking data. This results in higher quality tracking information and more explicit code.
