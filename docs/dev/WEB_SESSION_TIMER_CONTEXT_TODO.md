# Web UI Session Timer Context Issue - TODO

## Problem

Multi-session isolation works for most operations, but execution timers don't work correctly across sessions:

**Observed Behavior:**
1. Tab A: Paste program, Tab B: Paste different program
2. Tab B: Run program → Works correctly ✓
3. Tab A: Run program → Nothing happens (no error, no output) ✗

**Root Cause:**
The `exec_timer` (created with `ui.timer()`) runs in a global NiceGUI context, but when it fires the `_execute_tick()` callback, it may not have access to the correct `app.storage.client` context for that specific session.

## Current Implementation

**File:** `src/ui/web/nicegui_backend.py`

**Line 872:** Timer creation
```python
self.exec_timer = ui.timer(0.01, self._execute_tick, once=False)
```

**Line 880-887:** Timer callback
```python
def _execute_tick(self):
    """Execute one tick of the interpreter."""
    if not self.interpreter:  # This accesses app.storage.client
        return
```

**The Issue:**
- `self.interpreter` is a @property that calls `self._get_session_state()['interpreter']`
- `_get_session_state()` accesses `app.storage.client['mbasic_state']`
- When `ui.timer()` fires the callback, `app.storage.client` might not be bound to the correct client

## Potential Solutions

### Option 1: Store Client ID with Timer (Recommended)
Store the client ID when creating the timer, then restore the context in the callback:

```python
# At timer creation (line 872):
from nicegui import context
self.exec_timer = ui.timer(0.01, lambda: self._execute_tick_with_context(context.client.id), once=False)

# New method:
def _execute_tick_with_context(self, client_id):
    """Execute tick with explicit client context."""
    # Need to restore client context here
    # Research: How to set app.storage.client context from client_id?
    self._execute_tick()
```

### Option 2: Use ui.run Method
NiceGUI provides `ui.run` for executing code in the correct client context:

```python
# At timer creation:
from nicegui import context
client = context.client
self.exec_timer = ui.timer(0.01, lambda: client.run(self._execute_tick), once=False)
```

### Option 3: Store Session State in Timer Closure
Capture the session state reference when creating the timer:

```python
# At timer creation:
session_state = self._get_session_state()  # Capture reference
self.exec_timer = ui.timer(0.01, lambda: self._execute_tick_with_state(session_state), once=False)

def _execute_tick_with_state(self, state):
    """Execute tick with explicit state reference."""
    if not state['interpreter']:
        return
    # ... use state dict directly instead of self. properties
```

### Option 4: Store interpreter/runtime in Timer (Simplest)
Instead of storing exec_timer in session, store interpreter/runtime directly in the timer closure:

```python
# At timer creation (line 845-872):
interpreter = self.interpreter  # Capture at creation time
runtime = self.runtime
exec_io = self.exec_io

def tick_callback():
    if not interpreter:
        return
    state = interpreter.tick(mode='run', max_statements=1000)
    # Handle state...

self.exec_timer = ui.timer(0.01, tick_callback, once=False)
```

## Investigation Needed

1. **Test app.storage.client in timer callbacks**
   - Add debug logging to see if `app.storage.client` exists in `_execute_tick()`
   - Check if it's None or has wrong session data

2. **Research NiceGUI client context management**
   - How does `ui.timer()` bind to client context?
   - Can we explicitly set client context in callback?
   - Look at nicegui.context module

3. **Check if nicegui.client.run() solves this**
   - NiceGUI documentation suggests using `client.run()` for callbacks
   - Test if this preserves `app.storage.client` correctly

## Testing

After implementing fix:

1. Open two browser tabs (A and B)
2. Tab A: Paste program `10 PRINT "A" \n 20 END`
3. Tab B: Paste program `10 PRINT "B" \n 20 END`
4. Tab B: Click Run → Should print "B" ✓
5. Tab A: Click Run → Should print "A" ✓ (currently fails)
6. Verify both tabs can run simultaneously without interference

## Priority

**MEDIUM-HIGH** - Affects multi-user functionality but has workaround (only one user runs at a time)

## Status

TODO - Debug logging added, need to investigate timer context binding

## Debug Logging Added

Added debug logging at lines 885-891 in `src/ui/web/nicegui_backend.py`:
- Logs when no interpreter found
- Logs execution state before each tick

Check server console output or debug logs when testing.

## Related Files

- `src/ui/web/nicegui_backend.py` - Lines 822-927 (run/execution code)
- `docs/dev/WEB_UI_TESTING_CHECKLIST.md` - Multi-user testing checklist
- `docs/history/WEB_MULTI_USER_SESSION_ISOLATION_DONE.md` - Initial session isolation implementation
