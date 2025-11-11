# Publishing MBASIC to PyPI - Step by Step Guide

## What is PyPI?

**PyPI** (Python Package Index) is the official repository for Python packages. When users run `pip install mbasic`, pip downloads from PyPI.

**Website**: https://pypi.org/

---

## Prerequisites

### 1. Create PyPI Account

**Live PyPI** (for real releases):
- Go to https://pypi.org/account/register/
- Create account with email verification
- Enable 2FA (Two-Factor Authentication) - **REQUIRED** for uploading

**Test PyPI** (for testing - use this first!):
- Go to https://test.pypi.org/account/register/
- Separate account from live PyPI
- Practice uploads without affecting real package

### 2. Install Build Tools

```bash
pip install --upgrade build twine
```

- `build` - Creates distribution packages
- `twine` - Uploads packages to PyPI securely

---

## Package Structure

Your package needs this structure:

```
mbasic/
├── LICENSE                  # 0BSD license (already have)
├── README.md               # Package description (already have)
├── pyproject.toml          # Package metadata (CREATE THIS)
├── src/                    # Source code (already have)
│   └── mbasic/
│       ├── __init__.py     # Makes it a package
│       ├── runtime.py
│       ├── interpreter.py
│       └── ...
├── mbasic               # Entry point script
└── requirements.txt        # Dependencies (already have)
```

---

## Step 1: Create pyproject.toml

This is the modern way to define Python packages (replaces old `setup.py`).

Create `pyproject.toml` in the root directory:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mbasic"
version = "1.0.115"
description = "MBASIC 5.21 compatible BASIC interpreter with modern enhancements"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "0BSD"}
authors = [
    {name = "Aaron Wohl", email = "your.email@example.com"}
]
keywords = [
    "basic",
    "interpreter",
    "vintage",
    "retro",
    "programming",
    "mbasic",
    "microsoft-basic"
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "License :: OSI Approved",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Interpreters",
    "Topic :: Software Development :: Compilers",
]

dependencies = []

[project.optional-dependencies]
curses = ["urwid>=2.0.0"]
dev = ["pytest>=7.0", "pexpect>=4.8.0"]
all = ["urwid>=2.0.0"]

[project.urls]
Homepage = "https://github.com/avwohl/mbasic"
Documentation = "https://github.com/avwohl/mbasic/tree/main/docs"
Repository = "https://github.com/avwohl/mbasic"
Issues = "https://github.com/avwohl/mbasic/issues"
Changelog = "https://github.com/avwohl/mbasic/blob/main/docs/dev/WORK_IN_PROGRESS.md"

[project.scripts]
mbasic = "mbasic:main"

[tool.setuptools]
packages = ["mbasic"]
package-dir = {"" = "src"}
```

**Important fields:**
- `version` - Update this for each release
- `authors.email` - Your real email
- `dependencies` - Currently empty (no required deps)
- `optional-dependencies` - Curses UI is optional
- `project.scripts` - Creates `mbasic` command

---

## Step 2: Update mbasic Entry Point

PyPI needs a `main()` function to call. Update `mbasic`:

```python
#!/usr/bin/env python3
"""
MBASIC - MBASIC 5.21 compatible interpreter
"""

def main():
    """Entry point for pip-installed mbasic command"""
    import sys
    import os

    # Add src to path if running from source
    if os.path.exists('src'):
        sys.path.insert(0, 'src')

    # Your existing code here (all the if __name__ == "__main__" stuff)
    # Just move it into this main() function

    # ... rest of your mbasic code ...

if __name__ == "__main__":
    main()
```

This allows both:
- `python mbasic` (current method)
- `mbasic` (after pip install)

---

## Step 3: Build the Package

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python -m build
```

**Output:**
```
dist/
├── mbasic-1.0.115-py3-none-any.whl  # Wheel (preferred)
└── mbasic-1.0.115.tar.gz             # Source distribution
```

**What these are:**
- `.whl` (wheel) - Fast, binary-compatible package
- `.tar.gz` (sdist) - Source distribution (backup)

---

## Step 4: Test Locally

Before uploading, test installation locally:

```bash
# Create test virtual environment
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Install from local wheel
pip install dist/mbasic-1.0.115-py3-none-any.whl

# Test it works
mbasic --version
mbasic

# Clean up
deactivate
rm -rf test_env
```

---

## Step 5: Upload to Test PyPI (Practice First!)

**ALWAYS test on Test PyPI before real PyPI!**

### Configure credentials:

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your PyPI token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your Test PyPI token
```

**Get tokens:**
- Test PyPI: https://test.pypi.org/manage/account/token/
- Real PyPI: https://pypi.org/manage/account/token/

**Security:**
```bash
chmod 600 ~/.pypirc
```

### Upload to Test PyPI:

```bash
twine upload --repository testpypi dist/*
```

**Output:**
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading mbasic-1.0.115-py3-none-any.whl
Uploading mbasic-1.0.115.tar.gz

View at:
https://test.pypi.org/project/mbasic/1.0.115/
```

### Test installation from Test PyPI:

```bash
# Create test environment
python -m venv test_env2
source test_env2/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ mbasic

# Test it
mbasic --version

# Clean up
deactivate
rm -rf test_env2
```

---

## Step 6: Upload to Real PyPI

**Only after Test PyPI works!**

```bash
twine upload dist/*
```

**Output:**
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading mbasic-1.0.115-py3-none-any.whl
Uploading mbasic-1.0.115.tar.gz

View at:
https://pypi.org/project/mbasic/1.0.115/
```

**DONE!** Your package is now live.

---

## Step 7: Update README.md

Add installation instructions:

```markdown
## Installation

### From PyPI (recommended)

```bash
pip install mbasic
```

### Optional dependencies

```bash
# With curses UI support
pip install mbasic[curses]

# Development tools
pip install mbasic[dev]

# Everything
pip install mbasic[all]
```

### From source

```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
pip install -e .  # Editable install
```
```

---

## Releasing New Versions

### 1. Update version

In `pyproject.toml`:
```toml
version = "1.0.116"  # Increment version
```

Also update in:
- `src/version.py` (if you have one)
- `README.md` (version badges)

### 2. Update changelog

In `docs/dev/WORK_IN_PROGRESS.md` or `CHANGELOG.md`:
```markdown
## Version 1.0.116 (2025-10-29)

### New Features
- Added keyword case handling

### Bug Fixes
- Fixed issue with...

### Breaking Changes
- None
```

### 3. Commit and tag

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.0.116"
git tag v1.0.116
git push
git push --tags
```

### 4. Build and upload

```bash
rm -rf dist/
python -m build
twine upload dist/*
```

---

## Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

**Setup:**
1. Get PyPI token from https://pypi.org/manage/account/token/
2. Add to GitHub: Settings → Secrets → New repository secret
3. Name: `PYPI_TOKEN`
4. Value: Your token

**Now:**
```bash
git tag v1.0.116
git push --tags
# GitHub automatically builds and publishes!
```

---

## Common Issues

### Issue: "File already exists"

**Cause:** You can't re-upload the same version.

**Solution:** Increment version in `pyproject.toml`

### Issue: "Invalid distribution"

**Cause:** Missing `__init__.py` or wrong structure

**Solution:** Ensure `src/mbasic/__init__.py` exists:
```python
"""MBASIC - MBASIC 5.21 interpreter"""
__version__ = "1.0.115"
```

### Issue: "Module not found" after install

**Cause:** Package directory not set correctly

**Solution:** Check `[tool.setuptools]` in `pyproject.toml`:
```toml
[tool.setuptools]
packages = ["mbasic"]
package-dir = {"" = "src"}
```

### Issue: "Entry point not working"

**Cause:** `main()` function not found

**Solution:** Ensure `mbasic` has `main()` and it's in correct location

---

## Best Practices

### 1. Use Semantic Versioning

- **Major** (1.x.x): Breaking changes
- **Minor** (x.1.x): New features, backward compatible
- **Patch** (x.x.1): Bug fixes

### 2. Test Before Publishing

Always test on Test PyPI first!

### 3. Keep README Updated

Users see this on PyPI - make it good:
- Installation instructions
- Quick start example
- Features list
- Links to docs

### 4. Add Badges

```markdown
[![PyPI version](https://badge.fury.io/py/mbasic.svg)](https://pypi.org/project/mbasic/)
[![Python versions](https://img.shields.io/pypi/pyversions/mbasic.svg)](https://pypi.org/project/mbasic/)
[![Downloads](https://pepy.tech/badge/mbasic)](https://pepy.tech/project/mbasic)
```

### 5. Don't Forget LICENSE

PyPI shows your license. You already have 0BSD - perfect!

---

## Quick Command Reference

```bash
# First time setup
pip install --upgrade build twine

# Build package
python -m build

# Test locally
pip install dist/mbasic-*.whl

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to real PyPI
twine upload dist/*

# New release workflow
git tag v1.0.116
git push --tags
rm -rf dist/
python -m build
twine upload dist/*
```

---

## Resources

- **Official Guide**: https://packaging.python.org/tutorials/packaging-projects/
- **PyPI Help**: https://pypi.org/help/
- **Twine Docs**: https://twine.readthedocs.io/
- **Build Docs**: https://pypa-build.readthedocs.io/
- **pyproject.toml spec**: https://peps.python.org/pep-0621/

---

## Security Notes

1. **Use tokens, not passwords** - More secure
2. **Enable 2FA** - Required by PyPI
3. **Protect ~/.pypirc** - `chmod 600`
4. **Use GitHub Secrets** - Never commit tokens
5. **Review before upload** - Can't delete published versions

---

## Summary for MBASIC

**What you need to do:**

1. ✅ Create `pyproject.toml` (template above)
2. ✅ Update `mbasic` with `main()` function
3. ✅ Create PyPI account
4. ✅ Install: `pip install build twine`
5. ✅ Build: `python -m build`
6. ✅ Test: Upload to Test PyPI first
7. ✅ Upload: `twine upload dist/*`

**Time estimate:** 30-60 minutes for first release

**Result:** Users can `pip install mbasic` worldwide!
