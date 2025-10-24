# npyscreen Backend Removal

## Summary

The legacy `curses-npyscreen` backend has been completely removed from MBASIC. The project now uses only the modern urwid-based curses UI.

## Changes Made

### 1. Files Removed
- ✅ `src/ui/curses_npyscreen.py` - Legacy npyscreen backend implementation (~1200 lines)
- ✅ `src/ui/curses_ui_old.py.bak` - Old backup file

### 2. Code Updates

#### `mbasic.py`
- Removed `curses-npyscreen` from backend map
- Removed `curses-npyscreen` from argparse choices
- Updated help text examples
- Updated backend conditional logic

**Before:**
```python
backend_map = {
    'cli': ('ui.cli', 'CLIBackend'),
    'visual': ('ui.visual', 'VisualBackend'),
    'curses': ('ui.curses_ui', 'CursesBackend'),
    'curses-npyscreen': ('ui.curses_npyscreen', 'CursesBackend'),  # Removed
    'tk': ('ui.tk_ui', 'TkBackend'),
}
```

**After:**
```python
backend_map = {
    'cli': ('ui.cli', 'CLIBackend'),
    'visual': ('ui.visual', 'VisualBackend'),
    'curses': ('ui.curses_ui', 'CursesBackend'),
    'tk': ('ui.tk_ui', 'TkBackend'),
}
```

#### `src/ui/__init__.py`
- Removed import of `CursesNpyscreenBackend`
- Removed fallback logic to npyscreen
- Simplified curses backend import

**Before:**
```python
from .curses_npyscreen import CursesBackend as CursesNpyscreenBackend

try:
    from .curses_ui import CursesBackend
    _has_urwid = True
except ImportError:
    CursesBackend = CursesNpyscreenBackend
    _has_urwid = False
```

**After:**
```python
try:
    from .curses_ui import CursesBackend
    _has_curses = True
except ImportError:
    _has_curses = False
    CursesBackend = None
```

#### `requirements.txt`
- Removed `npyscreen>=1.0.0` dependency
- Updated comments

**Before:**
```txt
# Optional UI dependencies
npyscreen>=1.0.0    # For curses-npyscreen backend (legacy)
urwid>=2.0.0        # For curses backend (new, recommended)
```

**After:**
```txt
# Optional UI dependencies
urwid>=2.0.0        # For curses backend (full-screen terminal UI)
```

### 3. Documentation Updates

#### `docs/URWID_UI.md`
- Removed comparison table with npyscreen
- Removed references to `curses-npyscreen` backend
- Updated features section
- Removed migration instructions

#### `docs/dev/URWID_COMPLETION.md`
- Removed comparison table with npyscreen
- Updated feature status table
- Removed "Use npyscreen for" section
- Updated code statistics

## Rationale

### Why Remove npyscreen?

1. **Maintenance**: npyscreen has limited maintenance and few updates
2. **Code Quality**: urwid provides cleaner, more maintainable code
3. **Features**: urwid UI now has all essential features (INPUT, Save/Load)
4. **Simplicity**: One curses backend is easier to maintain than two
5. **Modern**: urwid is actively developed with comprehensive documentation

### Feature Parity

The urwid backend now provides all essential features:

| Feature | Status |
|---------|--------|
| Program execution | ✅ Complete |
| INPUT statements | ✅ Complete |
| File Save/Load | ✅ Complete |
| Help system | ✅ Complete |
| Output display | ✅ Complete |
| Error handling | ✅ Complete |

**Not Yet Implemented (Future):**
- Breakpoint debugging
- Step/Continue/End commands
- Menu system
- Mouse support

## Migration Guide

### For Users

**Old command:**
```bash
python3 mbasic.py --backend curses-npyscreen
```

**New command:**
```bash
python3 mbasic.py --backend curses
```

The urwid-based curses backend provides all the same basic functionality (program editing, execution, INPUT, file operations).

### For Developers

If you were extending or modifying the npyscreen backend:

1. The urwid backend is in `src/ui/curses_ui.py`
2. It's ~500 lines vs ~1200 lines (cleaner, simpler)
3. Uses standard urwid widgets (better documented)
4. Follow urwid conventions for extensions

## Verification

All functionality verified:
- ✅ Backend imports successfully
- ✅ No broken imports in codebase
- ✅ Help text updated
- ✅ Argparse choices updated
- ✅ Documentation updated
- ✅ Requirements updated

## What's Still Available

### Curses Backend (urwid)
```bash
python3 mbasic.py --backend curses
```
- Full-screen terminal UI
- Program editor
- Program execution
- INPUT statement support
- File Save/Load (Ctrl+S, Ctrl+O)
- Help system (Ctrl+H)

### CLI Backend
```bash
python3 mbasic.py --backend cli  # or just: python3 mbasic.py
```
- Command-line interface
- Interactive BASIC prompt
- Direct command execution
- Program loading from files

### Tkinter Backend
```bash
python3 mbasic.py --backend tk
```
- Graphical user interface
- Cross-platform GUI

## Testing

No dedicated npyscreen tests existed, so no test updates were required.

The existing test suite continues to work:
```bash
python3 test_variable_tracking.py  # ✅ Pass
```

## Future Plans

Advanced features will be added directly to the urwid backend:

1. **Breakpoint Support**
   - Visual breakpoint indicators
   - Toggle with 'b' key
   - Execution pause at breakpoints

2. **Step Debugging**
   - Step (s), Continue (c), End (e) commands
   - Variable inspection during execution
   - Call stack display

3. **Menu System**
   - File, Edit, Run, Help menus
   - Keyboard shortcuts
   - Mouse support

4. **Enhanced Features**
   - Syntax highlighting
   - Line numbers in gutter
   - Split-pane view
   - Watch window

## Conclusion

The npyscreen backend has been successfully removed. The project is now simpler with:
- ✅ One curses backend (urwid)
- ✅ Cleaner codebase (~700 fewer lines)
- ✅ No dependency on unmaintained library
- ✅ Better foundation for future features
- ✅ All essential functionality preserved

Users should use `--backend curses` for full-screen terminal UI.
