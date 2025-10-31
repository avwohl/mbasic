# MBASIC PyPI Distribution Testing Guide

**Status**: Package prepared, ready for building and testing
**Version**: 1.0.147

## Overview

This document explains how to build, test, and publish MBASIC to PyPI.

**IMPORTANT**: Do NOT publish to PyPI without explicit approval!

## Prerequisites

### Required Tools

```bash
# Install build tools in a virtual environment
python3 -m venv venv-build
source venv-build/bin/activate
pip install build twine
```

### PyPI Account Setup

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Generate API token**: https://pypi.org/manage/account/token/
   - Scope: "Entire account" (for first upload) or "Project: mbasic" (for updates)
   - Save token securely - you'll need it for uploads
3. **Configure token** in `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-AgEIcHlwaS5vcmcC...  # Your token here
   ```

### Test PyPI (Optional but Recommended)

For testing uploads without affecting production PyPI:

1. **Create TestPyPI account**: https://test.pypi.org/account/register/
2. **Generate TestPyPI token**
3. **Add to** `~/.pypirc`:
   ```ini
   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-AgENdGVzdC5weXBpLm9yZwI...  # Your test token
   ```

## Package Structure

Files configured for distribution:

```
mbasic/
├── pyproject.toml      # ✓ Package metadata and dependencies
├── MANIFEST.in         # ✓ Non-Python files to include
├── mbasic           # ✓ Entry point with main() function
├── src/                # ✓ All source packages
│   ├── *.py
│   ├── ui/
│   ├── iohandler/
│   ├── editing/
│   └── filesystem/
├── docs/               # ✓ Documentation
│   └── help/          # ✓ In-UI help system
├── basic/              # ✓ Example BASIC programs
└── README.md           # ✓ Package description
```

## Building the Package

### Step 1: Update Version

Version is managed in `src/version.py` and `pyproject.toml`:

```bash
# Version is auto-incremented by checkpoint.sh
./checkpoint.sh "message"

# Or manually update both files:
# - src/version.py: VERSION = "1.0.147"
# - pyproject.toml: version = "1.0.147"
```

### Step 2: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info
```

### Step 3: Build Package

```bash
# Build source distribution (.tar.gz) and wheel (.whl)
python3 -m build

# Output will be in dist/:
# - mbasic-1.0.147.tar.gz (source distribution)
# - mbasic-1.0.147-py3-none-any.whl (wheel)
```

### Step 4: Verify Build

```bash
# Check package contents
tar -tzf dist/mbasic-1.0.147.tar.gz | head -20

# Verify wheel
unzip -l dist/mbasic-1.0.147-py3-none-any.whl | head -20

# Check package metadata
python3 -m twine check dist/*
```

Expected output:
```
Checking dist/mbasic-1.0.147.tar.gz: PASSED
Checking dist/mbasic-1.0.147-py3-none-any.whl: PASSED
```

## Testing the Package

### Test 1: Local Installation

```bash
# Create clean test environment
python3 -m venv venv-test
source venv-test/bin/activate

# Install from built package
pip install dist/mbasic-1.0.147-py3-none-any.whl

# Test basic functionality
mbasic --version
mbasic --backend=cli --help

# Test with a simple program
cat > /tmp/test.bas << 'EOF'
10 PRINT "Hello from packaged MBASIC!"
20 FOR I = 1 TO 5
30   PRINT "Count:"; I
40 NEXT I
50 END
EOF

mbasic --backend=cli /tmp/test.bas

# Clean up
deactivate
rm -rf venv-test
```

### Test 2: Verify Entry Point

```bash
# The 'mbasic' command should be available
which mbasic

# Should show: /path/to/venv-test/bin/mbasic

# Test that it works
mbasic --list-backends
```

### Test 3: Check Package Contents

```bash
# Install and check installed files
python3 -m venv venv-check
source venv-check/bin/activate
pip install dist/mbasic-1.0.147-py3-none-any.whl

# List installed files
pip show -f mbasic | head -50

# Verify critical files are included:
# - mbasic (entry point)
# - src/*.py (interpreter core)
# - src/ui/*.py (UI backends)
# - docs/help/**/*.md (help system)

deactivate
rm -rf venv-check
```

### Test 4: Upload to TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
python3 -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
python3 -m venv venv-testpypi
source venv-testpypi/bin/activate
pip install --index-url https://test.pypi.org/simple/ mbasic

# Test functionality
mbasic --version
mbasic --backend=cli /tmp/test.bas

deactivate
rm -rf venv-testpypi
```

## Publishing to PyPI

**IMPORTANT**: Only perform these steps after receiving explicit approval!

### Pre-Publication Checklist

- [ ] Version updated in `src/version.py` and `pyproject.toml`
- [ ] `README.md` is up to date with installation instructions
- [ ] All tests passing (`python3 tests/run_regression.py`)
- [ ] Package built successfully (`python3 -m build`)
- [ ] Package verified (`python3 -m twine check dist/*`)
- [ ] Tested in clean environment (local wheel install works)
- [ ] (Optional) Tested on TestPyPI
- [ ] **Got explicit approval to publish**

### Upload to PyPI

```bash
# Upload to production PyPI
python3 -m twine upload dist/*

# You'll see:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading mbasic-1.0.147-py3-none-any.whl
# Uploading mbasic-1.0.147.tar.gz
# View at:
# https://pypi.org/project/mbasic/1.0.147/
```

### Verify Publication

```bash
# Wait a minute for PyPI to process

# Check package page
xdg-open https://pypi.org/project/mbasic/

# Test installation from PyPI
python3 -m venv venv-pypi-test
source venv-pypi-test/bin/activate
pip install mbasic

# Verify installation
mbasic --version
mbasic --list-backends
mbasic --backend=cli /tmp/test.bas

deactivate
rm -rf venv-pypi-test
```

## Post-Publication Tasks

After successful publication:

1. **Create Git tag**:
   ```bash
   git tag v1.0.147
   git push origin v1.0.147
   ```

2. **Create GitHub Release**:
   - Go to https://github.com/avwohl/mbasic/releases/new
   - Select tag `v1.0.147`
   - Title: "MBASIC v1.0.147"
   - Description: Brief changelog
   - Attach built files from `dist/`

3. **Update README badge** (optional):
   ```markdown
   ![PyPI version](https://img.shields.io/pypi/v/mbasic.svg)
   ![Python versions](https://img.shields.io/pypi/pyversions/mbasic.svg)
   ```

4. **Announce**:
   - Update main README with PyPI installation instructions
   - Post to relevant forums/communities if desired

## Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError: No module named 'build'`

**Solution**: Install build tools:
```bash
pip install build twine
```

### Upload Fails

**Error**: `Invalid or non-existent authentication information`

**Solution**: Check `~/.pypirc` configuration, regenerate API token if needed.

### Package Too Large

**Error**: `File too large`

**Solution**: Check MANIFEST.in excludes test files and large assets:
```bash
# MANIFEST.in should exclude:
recursive-exclude tests *
recursive-exclude utils *
```

### Import Errors After Installation

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Check `pyproject.toml` package configuration:
```toml
[tool.setuptools]
packages = ["src", "src.ui", "src.iohandler", ...]
```

## Version Management

### Incrementing Version

Use the checkpoint script (auto-increments):
```bash
./checkpoint.sh "Add new feature"
```

Or manually update:
1. `src/version.py`: `VERSION = "1.0.148"`
2. `pyproject.toml`: `version = "1.0.148"`
3. Rebuild package

### Version Numbering Scheme

- **Major** (1.x.x): Breaking changes, major features
- **Minor** (x.1.x): New features, enhancements
- **Patch** (x.x.1): Bug fixes, documentation

Current: 1.0.147
- Major: 1 (full MBASIC 5.21 implementation)
- Minor: 0 (first stable release)
- Patch: 147 (development increments)

## Emergency: Yanking a Release

If a critical bug is discovered after publishing:

```bash
# Yank the release (makes it unavailable for new installs)
# Users who already installed can still use it
pip install twine
twine upload --skip-existing --repository pypi dist/*

# Or use PyPI web interface:
# https://pypi.org/manage/project/mbasic/releases/
```

**Note**: Yanking doesn't delete the release, just marks it as problematic.
Fix the bug, increment version, and publish a new release.

## Support

- **PyPI Documentation**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Build Documentation**: https://pypa-build.readthedocs.io/

## Summary: Quick Command Reference

```bash
# Build
rm -rf dist/
python3 -m build

# Check
python3 -m twine check dist/*

# Test locally
pip install dist/mbasic-*.whl

# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Upload to PyPI (NEEDS APPROVAL!)
python3 -m twine upload dist/*
```
