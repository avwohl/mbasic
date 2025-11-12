# Simple Distribution Approach for MBASIC (Pure Python)

## Reality Check ✅

**MBASIC is pure Python** - no compilation needed!
- All source code interpreted
- Dependencies: Python 3.8+, optional urwid for curses UI, optional tkinter
- No C extensions, no build step
- Runs fine as regular user (non-root)

**Build farms are OVERKILL** - they're for:
- Compiled binaries (C, Rust, Go, etc.)
- Multi-arch native code
- Complex dependencies

## Recommended Simple Approach

### Option 1: PyPI (pip install) ⭐ BEST FOR PYTHON

**Simplest distribution:**
```bash
pip install mbasic
```

**Setup:**
1. Create `setup.py` or `pyproject.toml` (modern)
2. Register on PyPI: https://pypi.org/
3. Build: `python -m build`
4. Upload: `twine upload dist/*`

**That's it!** Users get:
- `pip install mbasic` anywhere
- Auto-installs dependencies
- Works on any OS (Linux, Mac, Windows)
- Any architecture (x86, ARM, whatever)

**User Experience:**
```bash
# Install
pip install mbasic

# Run
mbasic

# Or with python -m
python -m mbasic
```

---

### Option 2: Git Clone (Current Method) ✅ WORKS FINE

**What we have now:**
```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
pip install -r requirements.txt
python mbasic
```

**Pros:**
- ✅ Already works
- ✅ Latest code always
- ✅ Easy for developers
- ✅ No packaging needed

**Cons:**
- ❌ Less convenient for end users
- ❌ Requires git knowledge
- ❌ No version management

---

### Option 3: Single File Distribution (zipapp)

**Python has built-in single-file support:**
```bash
python -m zipapp mbasic -o mbasicz -p "/usr/bin/env python3"
```

Creates `mbasicz` - entire app in one executable file!

**Users run:**
```bash
./mbasicz
# or
python mbasicz
```

**Pros:**
- ✅ Single file
- ✅ No installation
- ✅ Portable
- ✅ Built-in to Python

**Cons:**
- ❌ Still needs Python installed
- ❌ Dependencies separate

---

### Option 4: GitHub Releases (Simple Download)

**Just zip the source:**
```bash
git archive --format=zip --output=mbasic-v1.0.112.zip HEAD
```

**Release on GitHub:**
- Tag version: `git tag v1.0.112`
- Push: `git push --tags`
- GitHub auto-creates release
- Attach zip file

**Users:**
```bash
wget https://github.com/avwohl/mbasic/releases/download/v1.0.112/mbasic-v1.0.112.zip
unzip mbasic-v1.0.112.zip
cd mbasic
pip install -r requirements.txt
python mbasic
```

---

## What About System Packages (.deb, .snap)?

### When You DON'T Need Them:

**You don't need .deb/.snap if:**
- ✅ Your users know how to `pip install` (most Python users do)
- ✅ Running as regular user is fine (MBASIC doesn't need root)
- ✅ No system integration needed (no system services, no file associations)
- ✅ Pure Python with standard dependencies

**MBASIC checks all these boxes!**

### When You MIGHT Want Them:

**Consider .deb/.snap only if you want:**
- Desktop integration (`.desktop` files, app menu entries)
- File association (`.bas` files open with MBASIC)
- System-wide installation
- Non-technical users (grandma can install from "Software Center")
- Sandbox security (snap confinement)

**But even then:**
- PyPI is simpler and works everywhere
- `pip install --user mbasic` installs for current user
- Create desktop launcher manually if needed

---

## Recommended Implementation: PyPI Package

### Step 1: Create `pyproject.toml` (Modern Python)

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mbasic"
version = "1.0.112"
description = "MBASIC 5.21 compatible BASIC interpreter"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "GPL-3.0-or-later"}
authors = [
    {name = "Aaron Wohl", email = "mbasic@wohl.com"}
]
keywords = ["basic", "interpreter", "vintage", "retro", "programming"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Interpreters",
]

dependencies = []

[project.optional-dependencies]
curses = ["urwid>=2.0.0"]
dev = ["pytest", "pexpect"]

[project.urls]
Homepage = "https://github.com/avwohl/mbasic"
Documentation = "https://github.com/avwohl/mbasic/tree/main/docs"
Repository = "https://github.com/avwohl/mbasic"
Issues = "https://github.com/avwohl/mbasic/issues"

[project.scripts]
mbasic = "mbasic:main"
```

### Step 2: Create Entry Point in `mbasic`

```python
def main():
    """Entry point for pip-installed mbasic"""
    import sys
    # Your existing main code here

if __name__ == "__main__":
    main()
```

### Step 3: Build and Upload

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

### Step 4: Users Install

```bash
# Basic installation
pip install mbasic

# With curses UI support
pip install mbasic[curses]

# Development installation
pip install mbasic[dev]

# Run
mbasic
```

**Done!** Works on:
- ✅ Linux (all distros)
- ✅ macOS
- ✅ Windows
- ✅ All architectures (x86, ARM, RISC-V, etc.)

---

## Summary: What You Actually Need

### Minimal (Works Now) ✅
```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
pip install -r requirements.txt
python mbasic
```

### Better (PyPI Package) ⭐ RECOMMENDED
```bash
pip install mbasic
mbasic
```

### Overkill (Build Farms) ❌ NOT NEEDED
- .deb packages with Launchpad
- .snap with multi-arch builds
- Complex CI/CD pipelines

**Bottom Line:**
- Pure Python = Simple distribution
- PyPI is the Python standard
- Everything else is complexity without benefit
- Save build farms for when you add native extensions (if ever)

---

## Implementation Checklist

### For PyPI Distribution (30 minutes of work)

- [ ] Create `pyproject.toml`
- [ ] Add `main()` entry point to `mbasic`
- [ ] Register PyPI account
- [ ] Install: `pip install build twine`
- [ ] Build: `python -m build`
- [ ] Upload: `twine upload dist/*`
- [ ] Test: `pip install mbasic`
- [ ] Update README with installation instructions

### Optional Extras

- [ ] Add GitHub Action to auto-publish on tag
  ```yaml
  - name: Publish to PyPI
    env:
      TWINE_USERNAME: __token__
      TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
    run: |
      python -m build
      twine upload dist/*
  ```

- [ ] Add version badge to README
- [ ] Add PyPI download stats badge

---

## Cost Analysis

| Method | Setup Time | Maintenance | Cost |
|--------|------------|-------------|------|
| **Git Clone** | 0 min | None | FREE |
| **PyPI** | 30 min | Minimal | FREE |
| **Build Farms** | 1-2 weeks | High | FREE but WHY? |

**Verdict:** Use PyPI, skip build farms entirely.

---

## When to Reconsider Build Farms

**Only if you:**
1. Add native C/Rust extensions for speed
2. Bundle Python interpreter (PyInstaller/Nuitka)
3. Need sandboxed desktop app
4. Target non-technical users who can't pip install

**Until then:** Keep it simple. Python is already cross-platform and portable.

---

## References

- **Python Packaging Guide**: https://packaging.python.org/
- **PyPI**: https://pypi.org/
- **pyproject.toml spec**: https://peps.python.org/pep-0621/
- **zipapp**: https://docs.python.org/3/library/zipapp.html
