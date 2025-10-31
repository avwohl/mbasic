# Migration to Urwid-based Curses UI

## Overview

The curses UI backend has been migrated from npyscreen to urwid. The old npyscreen implementation remains available as `curses-npyscreen` for backward compatibility.

## Changes Made

### File Renaming

- `src/ui/curses_ui.py` → `src/ui/curses_npyscreen.py`
- New `src/ui/curses_ui.py` created using urwid

### Backend Selection

- **`--backend curses`** - New urwid-based UI (recommended)
- **`--backend curses-npyscreen`** - Legacy npyscreen UI (for compatibility)

### Command Line Usage

```bash
# New urwid UI (requires: pip install urwid)
python3 mbasic --backend curses

# Legacy npyscreen UI (requires: pip install npyscreen)
python3 mbasic --backend curses-npyscreen
```

### Graceful Fallback

If urwid is not installed, the `curses` backend automatically falls back to `curses-npyscreen`. This ensures backward compatibility without requiring users to install urwid.

## Dependencies

Updated `requirements.txt`:

```
# Optional UI dependencies
npyscreen>=1.0.0    # For curses-npyscreen backend (legacy)
urwid>=2.0.0        # For curses backend (new, recommended)
```

Both are optional - the interpreter works fine with just the CLI backend (no dependencies).

## Why Urwid?

### Advantages over npyscreen

1. **Better maintained** - More active development and community support
2. **Cleaner API** - More pythonic and easier to work with
3. **Better performance** - More efficient screen updates
4. **Better documentation** - Comprehensive docs and examples
5. **More flexible** - Easier to customize layouts and widgets

### npyscreen Issues

1. **Cursor positioning bugs** - Had issues with cursor jumping and display glitches (see `docs/dev/CURSOR_FIX.md`)
2. **Complex event loop** - The `keypress_timeout` and `while_waiting` mechanism was fragile
3. **Limited maintenance** - Less active development
4. **Harder to debug** - Complex internal state management

## Urwid UI Features

The new urwid-based UI provides:

### Current Implementation

- Multi-line editor for BASIC programs
- Output window for program results
- Status bar for messages
- Basic keyboard shortcuts:
  - `Ctrl+Q` - Quit
  - `Ctrl+R` - Run program
  - `Ctrl+L` - List program
  - `Ctrl+N` - New program
  - `Ctrl+A` - Help

### Planned Features

- Menu system (File, Edit, Run, Debug, Help)
- Breakpoint support with visual indicators
- Interactive debugger (Step, Continue, End)
- Syntax highlighting
- Line numbering
- Better error display
- Mouse support
- Split panes and resizable windows

## Implementation Details

### File Structure

```
src/ui/
  ├── base.py                # Abstract UIBackend interface
  ├── curses_ui.py          # New urwid-based implementation
  ├── curses_npyscreen.py   # Legacy npyscreen implementation
  ├── cli.py                # CLI backend
  └── tk_ui.py              # Tkinter GUI backend
```

### Key Classes

#### CursesBackend (urwid)

```python
class CursesBackend(UIBackend):
    """Urwid-based curses UI backend."""

    def __init__(self, io_handler, program_manager):
        # Initialize UI widgets
        self.editor = EditorWidget()
        self.output = urwid.Text("")
        self.status_bar = urwid.Text("...")

    def start(self):
        # Create UI layout
        self._create_ui()
        # Run urwid main loop
        self.loop.run()
```

#### Layout Structure

```
┌─────────────────────────────────────┐
│ Editor (70%)                        │
│ ┌─────────────────────────────────┐ │
│ │ 10 PRINT "Hello"                │ │
│ │ 20 END                          │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Output (30%)                        │
│ ┌─────────────────────────────────┐ │
│ │ Hello                           │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Status: Ready - Press Ctrl+A for help  │
└─────────────────────────────────────┘
```

## Testing

### Automated Tests

Breakpoint tests updated to use `curses-npyscreen` explicitly:

```bash
python3 tests/test_breakpoints_final.py
```

All tests pass with the npyscreen backend.

### Manual Testing

1. **Test urwid UI** (requires urwid):
   ```bash
   pip install urwid
   python3 mbasic --backend curses
   ```

2. **Test npyscreen UI**:
   ```bash
   python3 mbasic --backend curses-npyscreen
   ```

3. **Test fallback** (without urwid):
   ```bash
   pip uninstall urwid
   python3 mbasic --backend curses
   # Should fall back to npyscreen
   ```

## Migration Path

### For Users

No action required - the system automatically uses the best available backend:

1. If urwid is installed: Uses new urwid UI when `--backend curses` is specified
2. If urwid is not installed: Falls back to npyscreen UI
3. Can explicitly use `--backend curses-npyscreen` for legacy UI

### For Developers

1. **New features**: Implement in `src/ui/curses_ui.py` (urwid)
2. **Bug fixes**: Fix in both implementations if critical
3. **Tests**: Update to specify `curses-npyscreen` for breakpoint tests
4. **Future**: Plan to deprecate npyscreen backend once urwid UI is feature-complete

## Future Work

### Short Term

- [ ] Implement program execution in urwid UI
- [ ] Add breakpoint support
- [ ] Add debugging commands (Step, Continue, End)
- [ ] Port features from npyscreen implementation

### Medium Term

- [ ] Add syntax highlighting
- [ ] Implement menu system
- [ ] Add mouse support
- [ ] Improve help system

### Long Term

- [ ] Deprecate npyscreen backend
- [ ] Remove npyscreen dependency
- [ ] Make urwid the default (once feature-complete)

## References

- Urwid documentation: http://urwid.org/
- npyscreen documentation: https://npyscreen.readthedocs.io/
- MBASIC UI architecture: `src/ui/base.py`
- Cursor positioning fix (npyscreen): `docs/dev/CURSOR_FIX.md`
- Breakpoint implementation (npyscreen): `docs/dev/BREAKPOINTS.md`
