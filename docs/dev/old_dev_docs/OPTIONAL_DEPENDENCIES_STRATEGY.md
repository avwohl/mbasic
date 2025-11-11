# Optional Dependencies Strategy for MBASIC

## Problem Statement

User question: "If someone only has command line or curses does our tk dependency suck in all of x11 on a headless machine?"

**Answer: NO - tkinter is already handled correctly!**

But we need a proper packaging strategy for PyPI to make this explicit.

---

## Current Status ✅

### Good News: Lazy Loading Already Implemented

MBASIC already uses **lazy imports** for tkinter:

```python
# In src/ui/tk_ui.py - imports are INSIDE methods, not at module level
def start(self):
    import tkinter as tk  # ← Only imported when TkBackend.start() is called
    from tkinter import ttk, scrolledtext
```

**This means:**
- ✅ Importing mbasic does NOT import tkinter
- ✅ Using CLI backend does NOT import tkinter
- ✅ Using curses backend does NOT import tkinter
- ✅ Only using `--ui tk` imports tkinter
- ✅ If tkinter isn't available, other backends still work

### Backend Loading is Dynamic

```python
# mbasic uses importlib.import_module()
def load_backend(backend_name, io_handler, program_manager):
    backend_module = importlib.import_module(module_name)  # Dynamic!
```

**This means:**
- Only the requested backend module is loaded
- If tk_ui.py is never imported, tkinter is never imported

---

## Testing Current Behavior

### Test 1: CLI Backend (No Tkinter Needed)

```bash
python3 -c "
import sys
# Remove tkinter if it exists (simulate headless)
sys.modules['tkinter'] = None

# Now try to use CLI backend
import mbasic
# This should work fine
print('CLI backend works without tkinter!')
"
```

### Test 2: Verify Lazy Loading

```python
import sys
print('tkinter' in sys.modules)  # Should be False

from src.ui import tk_ui  # Import the module
print('tkinter' in sys.modules)  # Still False! (lazy load)

backend = tk_ui.TkBackend(io, program)
backend.start()  # NOW tkinter gets imported
print('tkinter' in sys.modules)  # Now True
```

---

## PyPI Packaging Strategy

### Recommended: Optional Dependencies (Extras)

In `pyproject.toml`, define optional dependency groups:

```toml
[project]
name = "mbasic"
version = "1.0.116"
# ... other metadata ...

# Core has NO dependencies (Python stdlib only)
dependencies = []

[project.optional-dependencies]
# Curses UI (urwid)
curses = [
    "urwid>=2.0.0"
]

# Tkinter UI (nothing needed - included with Python)
# But we document it for clarity
tk = []

# GUI alias for tk
gui = []

# All UIs
all = [
    "urwid>=2.0.0"
]

# Development tools
dev = [
    "pytest>=7.0",
    "pexpect>=4.8.0",
    "python-frontmatter>=1.0.0"
]

# Documentation tools
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.4.0",
    "mkdocs-awesome-pages-plugin>=2.9.0"
]
```

### Installation Examples

```bash
# Minimal install - CLI only (no dependencies)
pip install mbasic

# With curses UI
pip install mbasic[curses]

# With TK UI (no extra deps, but explicit)
pip install mbasic[tk]

# All UIs
pip install mbasic[all]

# Development setup
pip install mbasic[all,dev,docs]
```

---

## Backend Availability Detection

### Current Behavior

The code already handles missing backends gracefully via try/except in `load_backend()`:

```python
try:
    backend_module = importlib.import_module(module_name)
except ImportError as e:
    raise ImportError(f"Failed to load backend '{backend_name}': {e}")
```

### Improvement: Friendly Error Messages

We should enhance error messages to guide users to install the right dependencies:

```python
def load_backend(backend_name, io_handler, program_manager):
    try:
        # ... existing code ...
        backend_module = importlib.import_module(module_name)
        return backend_class(io_handler, program_manager)

    except ImportError as e:
        # Provide helpful installation instructions
        install_help = {
            'tk': "Tkinter is included with Python. If missing, reinstall Python with tkinter support.",
            'curses': "Install with: pip install mbasic[curses]",
        }

        help_msg = install_help.get(backend_name, "")
        error_msg = f"Failed to load backend '{backend_name}': {e}"

        if help_msg:
            error_msg += f"\n\n{help_msg}"

        raise ImportError(error_msg)
```

---

## Tkinter Availability on Different Systems

### Linux (apt/yum/dnf)

**Problem:** Some minimal Linux installs don't include tkinter.

**Debian/Ubuntu:**
```bash
sudo apt-get install python3-tk
```

**RHEL/CentOS/Fedora:**
```bash
sudo dnf install python3-tkinter
```

**Detection:**
```python
try:
    import tkinter
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False
```

### macOS

**Status:** Tkinter included with Python (via python.org installer)

### Windows

**Status:** Tkinter included with Python (official installer)

### Headless Servers

**Problem:** X11 not available

**Solutions:**
1. Use CLI backend: `python3 mbasic --ui cli`
2. Use curses backend: `python3 mbasic --ui curses`
3. Virtual X server (Xvfb) if TK needed:
   ```bash
   sudo apt-get install xvfb
   xvfb-run python3 mbasic --ui tk
   ```

---

## Recommended Changes

### 1. Update mbasic with Better Error Messages

```python
def load_backend(backend_name, io_handler, program_manager):
    """Load a UI backend dynamically using importlib

    Raises helpful error messages if dependencies are missing.
    """
    try:
        # ... existing code ...
        backend_module = importlib.import_module(module_name)
        backend_class = getattr(backend_module, class_name)
        return backend_class(io_handler, program_manager)

    except ImportError as e:
        # Backend-specific help messages
        help_messages = {
            'tk': (
                "Tkinter backend requires tkinter (usually included with Python).\n"
                "If missing:\n"
                "  - Debian/Ubuntu: sudo apt-get install python3-tk\n"
                "  - RHEL/Fedora: sudo dnf install python3-tkinter\n"
                "  - macOS/Windows: Reinstall Python from python.org\n"
                "\n"
                "Alternative: Use --ui cli or --ui curses"
            ),
            'curses': (
                "Curses backend requires urwid library.\n"
                "Install with: pip install mbasic[curses]\n"
                "             or pip install urwid>=2.0.0\n"
                "\n"
                "Alternative: Use --ui cli or --ui tk"
            ),
        }

        error_msg = f"Failed to load backend '{backend_name}': {e}"
        if backend_name in help_messages:
            error_msg += f"\n\n{help_messages[backend_name]}"

        raise ImportError(error_msg)
```

### 2. Add --list-backends Command

```python
def list_backends():
    """Check which backends are available and print status"""
    backends = {
        'cli': ('Built-in', None),
        'curses': ('urwid', 'urwid>=2.0.0'),
        'tk': ('tkinter', None),
    }

    print("Available backends:\n")
    for name, (module, install) in backends.items():
        try:
            if name == 'cli':
                status = "✓ Available"
            elif name == 'tk':
                import tkinter
                status = "✓ Available"
            elif name == 'curses':
                import urwid
                status = "✓ Available"
        except ImportError:
            status = "✗ Not available"
            if install:
                status += f" (install: pip install {install})"

        print(f"  {name:10} {status}")

# In main():
parser.add_argument('--list-backends', action='store_true',
                    help='List available backends and exit')

if args.list_backends:
    list_backends()
    sys.exit(0)
```

### 3. Create pyproject.toml (for PyPI)

See `PUBLISHING_TO_PYPI_GUIDE.md` for full `pyproject.toml` example with optional-dependencies.

### 4. Update README.md

```markdown
## Installation

### Minimal (CLI only, no dependencies)
```bash
pip install mbasic
python3 -m mbasic --ui cli
```

### With Curses UI (full-screen terminal)
```bash
pip install mbasic[curses]
python3 -m mbasic  # curses is default
```

### With Tkinter GUI (if tkinter available)
```bash
pip install mbasic
python3 -m mbasic --ui tk
```

**Note:** Tkinter is included with most Python installations. If missing:
- Debian/Ubuntu: `sudo apt-get install python3-tk`
- RHEL/Fedora: `sudo dnf install python3-tkinter`

### Check Available Backends
```bash
python3 -m mbasic --list-backends
```

### Headless Servers
For servers without X11, use CLI or curses backends:
```bash
pip install mbasic[curses]
python3 -m mbasic --ui curses
# or
python3 -m mbasic --ui cli
```
```

---

## Summary

### Current Status: ✅ Already Good!

1. **Tkinter is lazy-loaded** - only imported when TkBackend.start() is called
2. **Dynamic backend loading** - unused backends never imported
3. **No hard dependencies** - core MBASIC has zero PyPI dependencies
4. **Backend isolation** - each backend in separate module

### What We Need to Do:

1. ✅ **Create pyproject.toml** with optional-dependencies (see PUBLISHING_TO_PYPI_GUIDE.md)
2. ⏳ **Add --list-backends** command to help users see what's available
3. ⏳ **Improve error messages** when backend dependencies missing
4. ⏳ **Update README.md** with installation examples for different use cases

### Key Insight:

**Pure Python packages don't need build farms** - the packaging is simple:
- Core: Zero dependencies ✅
- Curses: Optional urwid dependency (declared as extra)
- TK: System package (python3-tk), not PyPI
- CLI: Always available

Users on headless machines can:
```bash
pip install mbasic           # CLI only
pip install mbasic[curses]   # Add full-screen terminal UI
```

No X11 gets pulled in unless the user explicitly runs `--ui tk` (which will fail gracefully with helpful error).

---

## Testing Checklist

Before publishing to PyPI, test these scenarios:

### 1. Clean Virtual Environment - Minimal Install
```bash
python3 -m venv /tmp/test_minimal
source /tmp/test_minimal/bin/activate
pip install dist/mbasic-*.whl
python3 -m mbasic --ui cli  # Should work
python3 -m mbasic --ui tk   # Should work if tkinter available
python3 -m mbasic --ui curses  # Should fail with helpful message
deactivate
```

### 2. Clean Virtual Environment - Curses Install
```bash
python3 -m venv /tmp/test_curses
source /tmp/test_curses/bin/activate
pip install dist/mbasic-*.whl[curses]
python3 -m mbasic --ui curses  # Should work
deactivate
```

### 3. Headless Simulation
```bash
# Simulate headless by blocking tkinter
python3 -c "import sys; sys.modules['tkinter'] = None; exec(open('mbasic').read())" --ui cli
```

### 4. Backend Detection
```bash
python3 -m mbasic --list-backends
# Should show status of all backends
```

---

## Related Documentation

- `PUBLISHING_TO_PYPI_GUIDE.md` - Complete PyPI publishing guide with pyproject.toml
- `SIMPLE_DISTRIBUTION_APPROACH.md` - Why PyPI is better than build farms
- `GUI_LIBRARY_OPTIONS.md` - Qt/tkinter licensing analysis

---

## Conclusion

**Short answer to user's question:**

> No, tkinter does NOT get imported on headless machines unless you explicitly use `--ui tk`. The code already uses lazy loading and dynamic imports. We just need to document this properly and create the right PyPI package with optional dependencies.

**What to do next:**

1. Create `pyproject.toml` with optional-dependencies
2. Add `--list-backends` command
3. Improve error messages for missing backends
4. Test in clean virtual environments
5. Publish to PyPI with clear installation docs

The architecture is already correct - we just need to package it properly!
