# 💡 IDEA: Refactor Interpreter to Use Methods Instead of Instance Variables

## Status
💡 IDEA - Not sure if this is a good approach yet

## Problem

The `Interpreter.__init__` has 8 instance variables, but most of them shouldn't be variables at all - they should be methods you can override.

**Current code smell:**
```python
def __init__(self, runtime, io_handler=None, breakpoint_callback=None,
             filesystem_provider=None, limits=None, settings_manager=None):
    self.runtime = runtime
    self.builtins = BuiltinFunctions(runtime)
    self.io = io_handler  # ← Variable for configuration
    self.fs = filesystem_provider  # ← Variable for configuration
    self.limits = limits  # ← Variable for configuration
    self.settings_manager = settings_manager  # ← Variable for configuration
    self.breakpoint_callback = breakpoint_callback  # ← Variable for configuration
    self.state = InterpreterState()
```

**Issues:**
1. **Unclear if modified** - When you see `self.io.output(text)`, you don't know if `self.io` is the default or if someone swapped it out
2. **Anti-subclassing** - Tries to prevent subclassing by using dependency injection for everything
3. **Complex initialization** - Need to construct and pass in 5+ objects just to customize one behavior
4. **Violates variable principle** - Variables are for things that CHANGE during execution, not configuration

## Principle

**Variables are for things that CHANGE during execution.**

**Methods are for things you might want to do DIFFERENTLY.**

## Which Are Legitimate Variables?

Going through the 8 instance variables:

1. `self.runtime` - **Valid variable** (holds execution state that changes)
2. `self.builtins` - **Should be a method** (builtin functions don't change)
3. `self.io` - **Should be a method** (I/O handler doesn't change)
4. `self.fs` - **Should be a method** (filesystem doesn't change)
5. `self.limits` - **Should be a method** (limits don't change)
6. `self.settings_manager` - **Should be a method** (settings don't change)
7. `self.breakpoint_callback` - **Should be a method** (callback doesn't change)
8. `self.state` - **Valid variable** (execution state that changes constantly)

Only `self.runtime` and `self.state` should be instance variables!

## Proposed Solution

### Simple `__init__`
```python
class Interpreter:
    def __init__(self, runtime):
        self.runtime = runtime
        self.state = InterpreterState()
```

### Override Methods for Customization
```python
    def do_output(self, text):
        """Override this to change output behavior"""
        print(text)

    def do_file_open(self, path, mode):
        """Override this to change filesystem behavior"""
        from filesystem import RealFileSystemProvider
        return RealFileSystemProvider().open(path, mode)

    def check_limit(self, resource, amount):
        """Override this to change resource limit behavior"""
        from resource_limits import create_local_limits
        return create_local_limits().check(resource, amount)

    def get_setting(self, key):
        """Override this to change settings behavior"""
        from src.settings import get_settings_manager
        return get_settings_manager().get(key)

    def on_breakpoint(self, line_number, stmt_index):
        """Override this to handle breakpoints differently"""
        return True  # Continue execution

    def get_builtin_function(self, name):
        """Override this to customize builtin functions"""
        from src.builtin_functions import BuiltinFunctions
        return BuiltinFunctions(self.runtime).get(name)
```

### Usage in Code
```python
# Instead of:
self.io.output(text)

# Use:
self.do_output(text)
```

### Customization via Subclassing
```python
class TestInterpreter(Interpreter):
    def do_output(self, text):
        # Capture output for testing
        self.captured_output.append(text)

    def do_file_open(self, path, mode):
        # Use mock filesystem
        return self.mock_fs.open(path, mode)
```

## Benefits

1. **Clear intent** - When you see `self.do_output()`, you know it's either the base implementation or overridden
2. **No hidden state** - Can't swap out variables in the middle of execution
3. **Simpler initialization** - Just pass `runtime`, nothing else
4. **Standard OOP** - Uses inheritance properly instead of dependency injection everywhere
5. **Easy to extend** - Override one method instead of constructing and passing 5 objects

## Implementation Plan

### Phase 1: Add Methods (Backward Compatible)
Add new methods alongside existing variables:
```python
def do_output(self, text):
    if hasattr(self, 'io'):
        self.io.output(text)  # Use old way if available
    else:
        print(text)  # New default
```

### Phase 2: Update Call Sites
Replace all uses throughout interpreter.py:
- `self.io.output()` → `self.do_output()`
- `self.fs.open()` → `self.do_file_open()`
- `self.limits.check()` → `self.check_limit()`
- `self.settings_manager.get()` → `self.get_setting()`
- `self.breakpoint_callback()` → `self.on_breakpoint()`
- `self.builtins.get()` → `self.get_builtin_function()`

### Phase 3: Deprecate Variables
Add deprecation warnings in `__init__` if anyone passes the old parameters.

### Phase 4: Remove Variables
Remove instance variables and old parameters completely.

## Files to Change

1. `src/interpreter.py` - Main refactoring
2. All UI backends that create Interpreter instances:
   - `src/ui/cli/cli.py`
   - `src/ui/curses/curses_ui.py`
   - `src/ui/web/nicegui_backend.py`
3. Test files that create Interpreter instances

## Estimate

- **Phase 1:** 1 hour (add methods)
- **Phase 2:** 2-3 hours (update ~100+ call sites)
- **Phase 3:** 30 minutes (deprecation warnings)
- **Phase 4:** 30 minutes (cleanup)

**Total:** ~4-5 hours

## Priority

LOW - Defer until web UI is working properly

## Related Issues

- Web UI spacing/layout issues need to be fixed first
- This is a code quality improvement, not a bug fix
