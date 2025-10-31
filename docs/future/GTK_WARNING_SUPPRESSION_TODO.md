# GTK Warning Suppression

## Status: ⏸️ DEFERRED

## Issue

When starting the web backend on some Linux systems, a harmless GTK warning appears:

```
Gtk-Message: 11:06:24.119: Not loading module "atk-bridge": The functionality is provided by GTK natively. Please try to not load it.
```

## Impact

- **Severity:** LOW - Cosmetic only
- **Functionality:** Does not affect operation of web UI
- **User experience:** Slightly unprofessional to see warning on startup

## What Was Tried

Multiple approaches were attempted (versions 1.0.189-1.0.192):

1. **Setting `NO_AT_BRIDGE=1` environment variable**
   - At top of mbasic before imports
   - Before dynamic backend loading
   - At top of nicegui_backend.py before NiceGUI import
   - Result: No effect

2. **Python stderr filtering**
   - Wrapping sys.stderr with filter class
   - Result: Message comes from C library, bypasses Python stderr

3. **OS-level file descriptor filtering**
   - Using os.dup2() to redirect fd 2 through pipe
   - Background thread filtering lines
   - Result: Complex, unreliable

## Why It's Hard

The GTK message comes from:
- C libraries loaded by NiceGUI dependencies
- Printed directly to file descriptor 2 (stderr)
- Happens before Python code can intercept it
- May come from subprocess or shared library init

## Possible Future Solutions

### Option 1: Wrapper Script (Simplest)
Create `mbasic-web` wrapper script:
```bash
#!/bin/bash
NO_AT_BRIDGE=1 exec python3 /path/to/mbasic --backend web "$@" 2>&1 | \
  grep -v "Gtk-Message" | grep -v "atk-bridge"
```

**Pros:** Simple, works
**Cons:** Extra file, platform-specific

### Option 2: User Configuration
Document in README that users should set:
```bash
export NO_AT_BRIDGE=1
```
in their shell profile.

**Pros:** Simple documentation
**Cons:** Requires user action

### Option 3: Accept It
Just accept the warning message - it's harmless and many GTK apps show it.

**Pros:** No work needed
**Cons:** Slightly unprofessional appearance

### Option 4: NiceGUI Fix
Report to NiceGUI project - they might be able to suppress it internally.

**Pros:** Fixes it for all NiceGUI users
**Cons:** Not under our control

## Recommendation

**Accept it for now (Option 3).** The warning is harmless and doesn't affect functionality. If it becomes a user complaint, implement Option 1 (wrapper script).

## Related Files

- `mbasic` - Main entry point
- `src/ui/web/nicegui_backend.py` - Web UI implementation

## Notes

- This is a common issue with GTK applications on Linux
- The warning appears on some distributions but not others
- Users can suppress it themselves with `NO_AT_BRIDGE=1` if desired
