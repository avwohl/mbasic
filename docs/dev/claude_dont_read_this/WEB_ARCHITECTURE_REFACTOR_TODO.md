# Web UI Architecture Refactor - TODO

## Current (Broken) Architecture

```
mbasic (line 286):
    backend = NiceGUIBackend(io, program_mgr)  # ONE instance
    backend.start()                            # Calls ui.run()

NiceGUIBackend.build_ui():
    @ui.page('/')
    def main_page():
        self.editor = ui.textarea(...)    # Overwrites for each client!
        self.output = ui.textarea(...)    # Overwrites for each client!
```

**Problem:** ONE backend instance shared by ALL clients.
- When Tab B loads, it overwrites `self.editor`, `self.output`, etc.
- When Tab A's program outputs, it goes to Tab B's UI!

## Correct Architecture

```
mbasic:
    # DON'T create backend here for web!
    if backend_name == 'web':
        # Just start NiceGUI with a page factory function
        start_web_ui()

def start_web_ui():
    @ui.page('/')
    def main_page():
        # Create NEW backend instance for THIS client
        io_handler = ...
        program_mgr = ProgramManager()
        backend = NiceGUIBackend(io_handler, program_mgr)
        backend.build_ui()  # Builds UI for THIS client only

    ui.run()
```

**Key Changes:**
1. Backend instance created INSIDE `@ui.page('/')` function
2. Each client gets their OWN backend instance
3. No sharing, no session storage needed
4. Clean, simple architecture

## Implementation Plan

### Phase 1: Refactor Web UI Entry Point

**File:** `mbasic`

Change web backend initialization:

```python
def main():
    ...
    elif args.backend == 'web':
        # Web backend is special - don't create backend instance here
        from src.ui.web.nicegui_backend import start_web_ui
        start_web_ui()
        return
    else:
        backend = load_backend(args.backend, io_handler, program_manager)
```

### Phase 2: Create start_web_ui() Function

**File:** `src/ui/web/nicegui_backend.py`

Add module-level function:

```python
def start_web_ui():
    """Start the NiceGUI web server with per-client backend instances."""

    @ui.page('/')
    def main_page():
        # Create backend instance for THIS client
        from src.iohandler.base import IOHandler
        from src.editing.manager import ProgramManager

        # Create web-specific IO handler
        io_handler = ...  # TODO: Need to create this per-client
        program_manager = ProgramManager()

        # Create backend for this client
        backend = NiceGUIBackend(io_handler, program_manager)
        backend.build_ui()  # Build UI for this specific client

    # Start NiceGUI server
    ui.run(
        title='MBASIC 5.21 - Web IDE',
        port=8080,
        reload=False,
        show=False
    )
```

### Phase 3: Remove Session Storage Code

Since each client has their own backend instance, remove:

1. `_get_session_state()` method
2. All `@property` decorators for session state
3. `app.storage.client` usage

Everything can be normal instance variables:
- `self.runtime`
- `self.interpreter`
- `self.running`
- `self.output`
- `self.editor`
- etc.

### Phase 4: Simplify IOHandler

The IO handler needs to be created per-client too. Currently it's created once and shared.

**File:** `src/iohandler/web_io.py`

The `SimpleWebIOHandler` takes callbacks, so it should work fine per-instance:

```python
def main_page():
    backend = NiceGUIBackend(None, ProgramManager())
    backend.build_ui()

    # Create IO handler AFTER UI is built, passing backend's methods
    io_handler = SimpleWebIOHandler(
        backend._append_output,
        backend._get_input
    )
    backend.io = io_handler
```

## Benefits of Refactor

1. **✓ No session storage complexity** - Everything is instance variables
2. **✓ No timer context issues** - Timers belong to specific backend instance
3. **✓ No UI element sharing** - Each client has their own UI elements
4. **✓ Matches desktop UI architecture** - Web works same as TK/Curses
5. **✓ Clean, simple code** - No per-client dictionaries or context management

## Testing After Refactor

1. Open two browser tabs
2. Load different programs in each
3. Run both programs
4. Verify each tab shows its own output
5. Verify no cross-contamination

## Files to Modify

1. `mbasic` - Change web backend initialization
2. `src/ui/web/nicegui_backend.py` - Add `start_web_ui()`, remove session storage
3. Update tests to work with new architecture

## Priority

**HIGH** - Current architecture is fundamentally broken for multi-user

## Status

TODO - Needs implementation

## Related Files

- `docs/dev/WEB_SESSION_TIMER_CONTEXT_TODO.md` - Documents the symptom (wrong fix)
- `docs/history/WEB_MULTI_USER_SESSION_ISOLATION_DONE.md` - First attempt (wrong approach)
- `docs/dev/WEB_UI_TESTING_CHECKLIST.md` - Testing checklist

## Notes

The `app.storage.client` approach was a band-aid that partially worked for runtime state but left UI elements broken. The proper fix is to match the architecture of other backends (CLI, TK, Curses) where each "session" gets its own backend instance.

For web, "session" = browser tab/window, so each page load should create a new backend instance.
