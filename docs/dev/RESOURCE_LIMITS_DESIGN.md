# Resource Limits Design

**Date**: 2025-10-25
**Status**: ✅ IMPLEMENTED (2025-10-26)

## TL;DR

Create a centralized `ResourceLimits` object that the UI passes to the interpreter to track and enforce resource usage limits (memory, stack depth, string lengths, etc.).

## Problem

Currently, resource limits are either:
- Hardcoded in various places (stack depth, string length)
- Per-UI implementation (file system limits in web UI only)
- Not tracked at all (memory usage for arrays/strings)

This makes it hard to:
- Apply consistent limits across all UIs
- Track actual resource usage
- Provide useful error messages when limits are exceeded
- Adjust limits for different environments (web vs local)

## Proposed Solution

### 1. ResourceLimits Class

Create a `ResourceLimits` class that tracks and enforces all resource constraints:

```python
class ResourceLimits:
    """Track and enforce resource limits for BASIC program execution.

    This class is passed from the UI to the interpreter to provide
    environment-specific resource constraints (web = tight limits,
    local = generous limits).
    """

    def __init__(self,
                 # Stack limits
                 max_gosub_depth=100,
                 max_for_depth=50,
                 max_while_depth=50,

                 # Memory limits
                 max_total_memory=10*1024*1024,  # 10MB default
                 max_array_size=1*1024*1024,      # 1MB per array
                 max_string_length=32767,          # 32KB (MBASIC limit)

                 # File system limits
                 max_open_files=10,
                 max_file_size=512*1024,          # 512KB per file
                 max_total_files=20,

                 # Execution limits
                 max_execution_time=60.0,         # 60 seconds
                 max_statements_per_tick=1000,    # For tick-based execution
                ):
        # Store limits
        self.max_gosub_depth = max_gosub_depth
        self.max_for_depth = max_for_depth
        self.max_while_depth = max_while_depth
        self.max_total_memory = max_total_memory
        self.max_array_size = max_array_size
        self.max_string_length = max_string_length
        self.max_open_files = max_open_files
        self.max_file_size = max_file_size
        self.max_total_files = max_total_files
        self.max_execution_time = max_execution_time
        self.max_statements_per_tick = max_statements_per_tick

        # Track current usage
        self.current_memory_usage = 0
        self.current_gosub_depth = 0
        self.current_for_depth = 0
        self.current_while_depth = 0
        self.current_open_files = 0
        self.execution_start_time = None

        # Track individual allocations for detailed reporting
        self.allocations = {}  # name -> size in bytes

    # Stack depth tracking

    def push_gosub(self, line_num):
        """Track GOSUB call. Raises RuntimeError if limit exceeded."""
        self.current_gosub_depth += 1
        if self.current_gosub_depth > self.max_gosub_depth:
            raise RuntimeError(f"GOSUB stack overflow (limit: {self.max_gosub_depth})")

    def pop_gosub(self):
        """Track RETURN from GOSUB."""
        self.current_gosub_depth = max(0, self.current_gosub_depth - 1)

    def push_for_loop(self, var_name):
        """Track FOR loop entry. Raises RuntimeError if limit exceeded."""
        self.current_for_depth += 1
        if self.current_for_depth > self.max_for_depth:
            raise RuntimeError(f"FOR loop nesting too deep (limit: {self.max_for_depth})")

    def pop_for_loop(self):
        """Track NEXT (loop exit)."""
        self.current_for_depth = max(0, self.current_for_depth - 1)

    def push_while_loop(self):
        """Track WHILE loop entry. Raises RuntimeError if limit exceeded."""
        self.current_while_depth += 1
        if self.current_while_depth > self.max_while_depth:
            raise RuntimeError(f"WHILE loop nesting too deep (limit: {self.max_while_depth})")

    def pop_while_loop(self):
        """Track WEND (loop exit)."""
        self.current_while_depth = max(0, self.current_while_depth - 1)

    # Memory tracking

    def estimate_size(self, value, var_type):
        """Estimate memory size of a value in bytes.

        Args:
            value: The actual value (number, string, array)
            var_type: TypeInfo (INTEGER, SINGLE, DOUBLE, STRING)

        Returns:
            int: Estimated size in bytes
        """
        from parser import TypeInfo

        if var_type == TypeInfo.INTEGER:
            return 2  # 2 bytes for 16-bit integer
        elif var_type == TypeInfo.SINGLE:
            return 4  # 4 bytes for single-precision float
        elif var_type == TypeInfo.DOUBLE:
            return 8  # 8 bytes for double-precision float
        elif var_type == TypeInfo.STRING:
            # String: length + overhead
            if isinstance(value, str):
                return len(value.encode('utf-8')) + 4  # +4 for length prefix
            return 4  # Empty string
        else:
            return 8  # Default to double

    def check_array_allocation(self, var_name, dimensions, element_type):
        """Check if array allocation would exceed limits.

        Args:
            var_name: Variable name
            dimensions: List of dimension sizes [10, 20] for DIM A(10, 20)
            element_type: TypeInfo for array elements

        Raises:
            RuntimeError: If allocation would exceed limits

        Returns:
            int: Estimated size in bytes
        """
        # Calculate total elements (all dimensions multiplied)
        total_elements = 1
        for dim_size in dimensions:
            total_elements *= (dim_size + 1)  # +1 because BASIC is 0-indexed

        # Estimate element size
        element_size = self.estimate_size(None, element_type)

        # Total array size
        array_size = total_elements * element_size

        # Check against per-array limit
        if array_size > self.max_array_size:
            raise RuntimeError(
                f"Array {var_name} too large: {array_size} bytes "
                f"(limit: {self.max_array_size} bytes, "
                f"{total_elements} elements × {element_size} bytes/element)"
            )

        # Check against total memory limit
        new_total = self.current_memory_usage + array_size
        if new_total > self.max_total_memory:
            raise RuntimeError(
                f"Out of memory: would use {new_total} bytes "
                f"(limit: {self.max_total_memory} bytes, "
                f"current: {self.current_memory_usage} bytes)"
            )

        return array_size

    def allocate_array(self, var_name, dimensions, element_type):
        """Allocate memory for an array.

        Args:
            var_name: Variable name
            dimensions: List of dimension sizes
            element_type: TypeInfo for array elements

        Raises:
            RuntimeError: If allocation would exceed limits
        """
        # Check if allocation is allowed
        array_size = self.check_array_allocation(var_name, dimensions, element_type)

        # Free old allocation if re-dimensioning
        if var_name in self.allocations:
            old_size = self.allocations[var_name]
            self.current_memory_usage -= old_size

        # Record new allocation
        self.allocations[var_name] = array_size
        self.current_memory_usage += array_size

    def allocate_variable(self, var_name, value, var_type):
        """Track variable assignment.

        Args:
            var_name: Variable name
            value: The value being assigned
            var_type: TypeInfo
        """
        var_size = self.estimate_size(value, var_type)

        # Free old allocation
        if var_name in self.allocations:
            old_size = self.allocations[var_name]
            self.current_memory_usage -= old_size

        # Record new allocation
        self.allocations[var_name] = var_size
        self.current_memory_usage += var_size

    def free_variable(self, var_name):
        """Free memory for a variable (e.g., when CLEAR or NEW is called)."""
        if var_name in self.allocations:
            size = self.allocations[var_name]
            self.current_memory_usage -= size
            del self.allocations[var_name]

    def clear_all(self):
        """Free all memory (NEW command)."""
        self.allocations.clear()
        self.current_memory_usage = 0
        self.current_gosub_depth = 0
        self.current_for_depth = 0
        self.current_while_depth = 0

    def check_string_length(self, string_value):
        """Check if string exceeds maximum length.

        Args:
            string_value: The string to check

        Raises:
            RuntimeError: If string exceeds limit
        """
        if isinstance(string_value, str):
            byte_length = len(string_value.encode('utf-8'))
            if byte_length > self.max_string_length:
                raise RuntimeError(
                    f"String too long: {byte_length} bytes "
                    f"(limit: {self.max_string_length} bytes)"
                )

    # Execution time tracking

    def start_execution(self):
        """Mark start of program execution."""
        import time
        self.execution_start_time = time.time()

    def check_execution_time(self):
        """Check if execution time limit exceeded.

        Raises:
            RuntimeError: If time limit exceeded
        """
        if self.execution_start_time is None:
            return

        import time
        elapsed = time.time() - self.execution_start_time
        if elapsed > self.max_execution_time:
            raise RuntimeError(
                f"Execution time limit exceeded: {elapsed:.1f}s "
                f"(limit: {self.max_execution_time}s)"
            )

    # Reporting

    def get_usage_report(self):
        """Get a human-readable usage report.

        Returns:
            str: Multi-line report of current resource usage
        """
        lines = []
        lines.append("Resource Usage:")
        lines.append(f"  Memory: {self.current_memory_usage:,} / {self.max_total_memory:,} bytes ({self.current_memory_usage / self.max_total_memory * 100:.1f}%)")
        lines.append(f"  GOSUB depth: {self.current_gosub_depth} / {self.max_gosub_depth}")
        lines.append(f"  FOR depth: {self.current_for_depth} / {self.max_for_depth}")
        lines.append(f"  WHILE depth: {self.current_while_depth} / {self.max_while_depth}")

        if self.execution_start_time:
            import time
            elapsed = time.time() - self.execution_start_time
            lines.append(f"  Execution time: {elapsed:.1f}s / {self.max_execution_time}s")

        if self.allocations:
            lines.append("  Top allocations:")
            top = sorted(self.allocations.items(), key=lambda x: x[1], reverse=True)[:5]
            for name, size in top:
                lines.append(f"    {name}: {size:,} bytes")

        return "\n".join(lines)
```

### 2. Preset Configurations

Provide preset limit configurations for different environments:

```python
# src/resource_limits.py

def create_web_limits():
    """Create resource limits suitable for web environment (restrictive)."""
    return ResourceLimits(
        max_gosub_depth=50,
        max_for_depth=25,
        max_while_depth=25,
        max_total_memory=5*1024*1024,      # 5MB
        max_array_size=512*1024,            # 512KB per array
        max_string_length=32767,            # 32KB (MBASIC standard)
        max_open_files=5,
        max_file_size=256*1024,             # 256KB per file
        max_total_files=10,
        max_execution_time=30.0,            # 30 seconds
        max_statements_per_tick=500,
    )

def create_local_limits():
    """Create resource limits suitable for local CLI (generous)."""
    return ResourceLimits(
        max_gosub_depth=500,
        max_for_depth=100,
        max_while_depth=100,
        max_total_memory=100*1024*1024,     # 100MB
        max_array_size=10*1024*1024,        # 10MB per array
        max_string_length=32767,            # 32KB (MBASIC standard)
        max_open_files=20,
        max_file_size=10*1024*1024,         # 10MB per file
        max_total_files=100,
        max_execution_time=300.0,           # 5 minutes
        max_statements_per_tick=10000,
    )

def create_unlimited_limits():
    """Create effectively unlimited limits (for testing)."""
    return ResourceLimits(
        max_gosub_depth=10000,
        max_for_depth=1000,
        max_while_depth=1000,
        max_total_memory=1024*1024*1024,    # 1GB
        max_array_size=100*1024*1024,       # 100MB per array
        max_string_length=1024*1024,        # 1MB strings
        max_open_files=100,
        max_file_size=100*1024*1024,        # 100MB per file
        max_total_files=1000,
        max_execution_time=3600.0,          # 1 hour
        max_statements_per_tick=100000,
    )
```

### 3. Integration with Interpreter

Modify `Interpreter.__init__()` to accept limits:

```python
class Interpreter:
    def __init__(self, runtime, io_handler, filesystem_provider=None, limits=None):
        self.runtime = runtime
        self.io = io_handler
        self.filesystem = filesystem_provider or DefaultFileSystemProvider()
        self.limits = limits or create_local_limits()  # Default to local limits

        # ... rest of initialization
```

### 4. UI Integration

Each UI creates and passes appropriate limits:

**Web UI**:
```python
from resource_limits import create_web_limits

# In menu_run():
limits = create_web_limits()
self.interpreter = Interpreter(self.runtime, self.io_handler, filesystem, limits=limits)
```

**Tk/Curses UI**:
```python
from resource_limits import create_local_limits

# In cmd_run():
limits = create_local_limits()
self.interpreter = Interpreter(self.runtime, self.io_handler, limits=limits)
```

**CLI UI**:
```python
from resource_limits import create_unlimited_limits

# For testing/development
limits = create_unlimited_limits()
interpreter = Interpreter(runtime, io_handler, limits=limits)
```

### 5. Interpreter Changes

Modify interpreter to call limits at key points:

**DIM statement**:
```python
def execute_dim(self, stmt):
    var_name = stmt.var_name
    dimensions = [self.evaluate_expression(dim_expr) for dim_expr in stmt.dimensions]
    var_type = self.runtime.get_variable_type(var_name)

    # Check if allocation is allowed
    self.limits.allocate_array(var_name, dimensions, var_type)

    # Proceed with actual allocation
    # ... existing DIM logic
```

**GOSUB/RETURN**:
```python
def execute_gosub(self, stmt):
    self.limits.push_gosub(stmt.target_line)
    # ... existing GOSUB logic

def execute_return(self, stmt):
    self.limits.pop_gosub()
    # ... existing RETURN logic
```

**FOR/NEXT**:
```python
def execute_for(self, stmt):
    self.limits.push_for_loop(stmt.var_name)
    # ... existing FOR logic

def execute_next(self, stmt):
    self.limits.pop_for_loop()
    # ... existing NEXT logic
```

**String operations**:
```python
def string_concat(self, left, right):
    result = str(left) + str(right)
    self.limits.check_string_length(result)
    return result
```

**Variable assignment**:
```python
def set_variable(self, var_name, value, var_type):
    self.limits.allocate_variable(var_name, value, var_type)
    # ... existing assignment logic
```

## String Tracking Question

### Option A: Track Every String Operation (Accurate but Slow)

```python
def string_concat(self, left, right):
    result = str(left) + str(right)
    # Check length limit
    self.limits.check_string_length(result)
    # Track memory usage
    self.limits.allocate_variable("_temp_string", result, TypeInfo.STRING)
    return result
```

**Pros**: Accurate memory tracking
**Cons**: Performance overhead on every string operation

### Option B: Track Only Variable Assignments (Fast but Approximate)

```python
def set_variable(self, var_name, value, var_type):
    if var_type == TypeInfo.STRING:
        # Check length on assignment
        self.limits.check_string_length(value)
        # Track only named variables
        self.limits.allocate_variable(var_name, value, var_type)
    # ... rest of assignment
```

**Pros**: Fast, minimal overhead
**Cons**: Doesn't track temporary strings

### Recommendation: **Option B** (Track Only Variables)

- More realistic: MBASIC only limits string **variables** to 255 bytes
- Better performance: No overhead on intermediate string operations
- Still catches the important cases: Assignment to variables
- Simpler implementation: One check point (assignment)

For string length, enforce MBASIC's 255-byte limit for string variables:

```python
max_string_length=255  # MBASIC limit for string variables
```

Temporary string expressions can be longer, but can't be assigned to variables.

## Implementation Plan

### Phase 1: Create ResourceLimits Class ✅
- [x] Create `src/resource_limits.py` with `ResourceLimits` class
- [x] Add preset configurations (web, local, unlimited)
- [x] Add unit tests for limit checking (11 tests in `tests/test_resource_limits.py`)

### Phase 2: Integrate with Interpreter ✅
- [x] Modify `Interpreter.__init__()` to accept limits parameter
- [x] Add limit checks to DIM statement
- [x] Add limit checks to GOSUB/RETURN
- [x] Add limit checks to FOR/NEXT, WHILE/WEND
- [x] Add limit checks to string variable assignment (8 tests in `tests/test_interpreter_limits.py`)

### Phase 3: Update UIs ✅
- [x] Web UI: Use `create_web_limits()`
- [x] Tk UI: Use `create_local_limits()`
- [x] Curses UI: Use `create_local_limits()`
- [x] CLI UI: Use `create_unlimited_limits()`

### Phase 4: Add Reporting ✅
- [x] Add `LIMITS` command to show resource usage (renamed from SYSTEM to avoid conflict)
- [x] Add resource usage to error messages (already excellent)
- [x] Add usage display to debug/watch windows (Tk and Curses UIs)

## Benefits

1. **Centralized Control**: All limits in one place
2. **Environment-Specific**: Web gets tight limits, local gets generous limits
3. **Better Errors**: "Array too large: 2MB (limit: 512KB)" instead of generic errors
4. **Resource Visibility**: Users can see `SYSTEM` report of usage
5. **Safety**: Prevents runaway programs from consuming resources
6. **Flexibility**: Easy to adjust limits per environment

## Example Error Messages

**Before**:
```
Out of memory
```

**After**:
```
Array A too large: 2,097,152 bytes (limit: 524,288 bytes, 262,144 elements × 8 bytes/element)
Current memory usage: 3,145,728 / 5,242,880 bytes

Top allocations:
  B(): 1,048,576 bytes
  C(): 524,288 bytes
  A(): 262,144 bytes
```

Much more actionable!

## Notes

- String length limit: Use 255 bytes (MBASIC standard for string variables)
- Track only string **variables**, not intermediate expressions
- Memory tracking is approximate (good enough for limits)
- File system limits already implemented in `SandboxedFileSystemProvider`
- Consider integrating file limits into `ResourceLimits` for consistency
