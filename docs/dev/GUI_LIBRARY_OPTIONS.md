# GUI Library Options and Licensing

## Current Status: Tkinter (Included with Python)

**MBASIC currently uses Tkinter** - included with Python, no additional dependencies.

**License:** Python Software Foundation License (compatible with all licenses including 0BSD)

**Pros:**
- ✅ Included with Python (no installation needed)
- ✅ Cross-platform (Linux, Mac, Windows)
- ✅ Simple and lightweight
- ✅ No licensing concerns

**Cons:**
- ❌ Older look and feel
- ❌ Less modern widgets
- ❌ Not as feature-rich as Qt

---

## Future Options: Qt for Python

If we want to upgrade to a more modern GUI in the future, here are the options:

### Option 1: PySide6 ⭐ RECOMMENDED for Open Source

**License:** LGPL v3 / GPL v2 / GPL v3 (your choice)

**LGPL Compatibility:**
- ✅ Compatible with 0BSD license
- ✅ Users can link to PySide6 without viral effects
- ✅ LGPL only requires sharing PySide6 modifications, not your code
- ✅ Perfect for open source projects

**Installation:**
```bash
pip install PySide6
```

**Pros:**
- ✅ Official Qt binding (maintained by Qt Company)
- ✅ LGPL license - most permissive for Qt
- ✅ Modern, beautiful widgets
- ✅ Excellent documentation
- ✅ Long-term support

**Cons:**
- ❌ Large dependency (~200MB)
- ❌ Requires installation (not included with Python)

---

### Option 2: PyQt6

**License:** GPL v3 or Commercial

**GPL Implications:**
- ⚠️ GPL v3 is **viral** (copyleft)
- ⚠️ Requires MBASIC to be GPL v3 if distributed
- ⚠️ Incompatible with 0BSD's "do anything" philosophy
- ❌ Would force users to also use GPL

**NOT RECOMMENDED** unless you buy commercial license.

---

## License Compatibility Matrix

| Library | License | Compatible with 0BSD? | Notes |
|---------|---------|----------------------|-------|
| **Tkinter** | PSF License | ✅ Yes | Current, included with Python |
| **PySide6** | LGPL v3 | ✅ Yes | LGPL allows linking without copyleft |
| **PyQt6** | GPL v3 | ❌ No | GPL is viral, conflicts with "do anything" |
| **PyQt6** | Commercial | ✅ Yes | Must purchase license (~$550) |

---

## Recommendation

### For Current 0BSD License:

1. **Keep Tkinter** - works perfectly, no licensing issues
2. **If upgrading GUI**: Use **PySide6** with LGPL
3. **Avoid PyQt6** (GPL) unless buying commercial license

### LGPL Explained:

**LGPL allows:**
- ✅ Dynamic linking to LGPL libraries
- ✅ Your code stays 0BSD
- ✅ Users don't need to release source
- ✅ Only modifications to PySide6 itself must be shared

**Example:**
```
MBASIC (0BSD) → imports → PySide6 (LGPL)
```
This is perfectly legal! Users just need to:
- Include PySide6 license notice
- Allow relinking with different PySide6 version
- That's it! Your MBASIC code stays 0BSD

---

## Current Dependencies

### Core (No GUI):
- Python 3.8+ (PSF License - compatible)
- No external dependencies

### Optional (Curses UI):
- urwid 2.0+ (LGPL - compatible)

### Optional (TK UI):
- tkinter (included with Python - compatible)

### Optional (Future Qt UI):
- PySide6 (LGPL - compatible) ⭐ RECOMMENDED
- OR PyQt6 (GPL - incompatible) ❌

---

## Adding PySide6 (Future)

If we decide to add a Qt UI option:

### 1. Make it Optional

```python
# In requirements.txt
# Optional GUI dependencies
pyside6>=6.0.0  # Optional: Modern Qt6 GUI
```

### 2. Detect at Runtime

```python
# In mbasic
try:
    from PySide6 import QtWidgets
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

if args.ui == 'qt' and not QT_AVAILABLE:
    print("Qt UI requires: pip install PySide6")
    sys.exit(1)
```

### 3. Update Documentation

```markdown
## Installation Options

### Minimal (CLI only)
```bash
pip install mbasic
```

### With Curses UI
```bash
pip install mbasic[curses]
```

### With Qt GUI
```bash
pip install mbasic[qt]
```
```

---

## License Notices

### Current (0BSD + Tkinter)

No additional notices needed - both are permissive.

### If Adding PySide6

Must include in README:

```markdown
## License

MBASIC is licensed under 0BSD (Zero-Clause BSD).

### Dependencies

- PySide6 (optional): LGPL v3 / GPL v2 / GPL v3
  See https://doc.qt.io/qtforpython-6/licenses.html
```

---

## Summary

**Current Setup: ✅ Perfect**
- Tkinter (included)
- 0BSD license
- No licensing concerns

**Future Qt Option: Use PySide6**
- LGPL compatible with 0BSD
- Makes it optional dependency
- Clear documentation of licensing

**Never Use: PyQt6 with GPL**
- GPL conflicts with 0BSD philosophy
- Would force users into GPL
- Unless buying commercial license

---

## References

- **0BSD License**: https://opensource.org/license/0bsd
- **PySide6 Licensing**: https://doc.qt.io/qtforpython-6/licenses.html
- **LGPL Explained**: https://www.gnu.org/licenses/lgpl-3.0.html
- **License Compatibility**: https://www.gnu.org/licenses/gpl-faq.html#AllCompatibility
