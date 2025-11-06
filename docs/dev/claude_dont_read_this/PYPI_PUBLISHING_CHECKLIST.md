# PyPI Publishing Checklist

## Status: Ready to Publish ✅

All packaging files are complete and tested. Follow these steps when ready to publish.

---

## Prerequisites (One-Time Setup)

### 1. Create PyPI Accounts

**Test PyPI** (practice first!):
- https://test.pypi.org/account/register/
- Enable 2FA

**Production PyPI**:
- https://pypi.org/account/register/
- Enable 2FA

### 2. Install Build Tools

```bash
pip install --upgrade build twine
```

### 3. Create API Tokens

**Test PyPI:**
- Go to: https://test.pypi.org/manage/account/token/
- Create token with scope: "Entire account"
- Save as `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEI... (your Test PyPI token)

[pypi]
username = __token__
password = pypi-AgEI... (your PyPI token)
```

**Protect the file:**
```bash
chmod 600 ~/.pypirc
```

---

## Publishing Workflow

### Step 1: Pre-Flight Checks

```bash
# Verify version number is updated
cat src/version.py
# Should show latest version (e.g., 1.0.119)

# Verify pyproject.toml version matches
grep "version =" pyproject.toml
# Should match src/version.py

# Verify all tests pass
python3 mbasic --list-backends
# Should show all backends available

# Check imports work
python3 -c "import sys; sys.path.insert(0, 'src'); from runtime import Runtime; print('✓ Imports OK')"
```

### Step 2: Clean and Build

```bash
# Remove old builds
rm -rf dist/ build/ *.egg-info

# Build the package
python3 -m build

# Verify output
ls -lh dist/
# Should show:
#   mbasic-1.0.119-py3-none-any.whl
#   mbasic-1.0.119.tar.gz
```

### Step 3: Test Locally

```bash
# Create clean test environment
python3 -m venv /tmp/test_mbasic
source /tmp/test_mbasic/bin/activate

# Install from local wheel
pip install dist/mbasic-*.whl

# Test it works
mbasic --list-backends
mbasic --ui cli
# Type: PRINT "Hello, World!"
# Type: RUN

# Clean up
deactivate
rm -rf /tmp/test_mbasic
```

### Step 4: Upload to Test PyPI

**ALWAYS test on Test PyPI before production!**

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Wait a moment for processing, then view:
# https://test.pypi.org/project/mbasic/
```

### Step 5: Test Installation from Test PyPI

```bash
# Create clean test environment
python3 -m venv /tmp/test_from_testpypi
source /tmp/test_from_testpypi/bin/activate

# Install from Test PyPI (minimal)
pip install --index-url https://test.pypi.org/simple/ mbasic

# Test CLI backend
python3 -c "import mbasic; mbasic.main()" --ui cli --help

# Clean up
deactivate

# Test with curses
python3 -m venv /tmp/test_curses
source /tmp/test_curses/bin/activate
pip install --index-url https://test.pypi.org/simple/ mbasic[curses]
python3 -m mbasic --list-backends
deactivate

rm -rf /tmp/test_from_testpypi /tmp/test_curses
```

### Step 6: Upload to Production PyPI

**Only after Test PyPI works perfectly!**

```bash
# Final check: version not already published
# Visit: https://pypi.org/project/mbasic/
# Verify this version doesn't exist yet

# Upload to production PyPI
twine upload dist/*

# View your package
# https://pypi.org/project/mbasic/
```

### Step 7: Test Production Installation

```bash
# Create clean environment
python3 -m venv /tmp/test_prod
source /tmp/test_prod/bin/activate

# Install from production PyPI
pip install mbasic

# Test it
mbasic --list-backends
mbasic --ui cli

# Test with optional dependencies
pip install mbasic[curses]
mbasic --ui curses

deactivate
rm -rf /tmp/test_prod
```

### Step 8: Create GitHub Release

```bash
# Tag the release
git tag v1.0.119
git push origin v1.0.119

# Create release on GitHub:
# https://github.com/avwohl/mbasic/releases/new
# - Tag: v1.0.119
# - Title: MBASIC 1.0.119
# - Description: Copy from WORK_IN_PROGRESS.md
# - Attach: dist/*.whl and dist/*.tar.gz
```

### Step 9: Make Repository Public and Enable GitHub Pages

**After publishing to PyPI, make the repository public:**

```bash
# 1. Go to repository settings:
#    https://github.com/avwohl/mbasic/settings

# 2. Scroll to "Danger Zone" section

# 3. Click "Change visibility" → "Make public"

# 4. Enable GitHub Pages:
#    https://github.com/avwohl/mbasic/settings/pages
#    - Under "Source", select "GitHub Actions"
#    - This deploys docs to: https://avwohl.github.io/mbasic

# 5. Verify docs deploy successfully:
#    - Check workflow: https://github.com/avwohl/mbasic/actions
#    - Visit site: https://avwohl.github.io/mbasic
```

**Note:** GitHub Pages requires a public repository. The documentation build workflow is already configured and will automatically deploy once the repository is public and Pages is enabled.

---

## Updating for New Release

### 1. Update Version Numbers

```bash
# src/version.py
VERSION = "1.0.120"

# pyproject.toml
version = "1.0.120"
```

### 2. Update Changelog

In `docs/dev/WORK_IN_PROGRESS.md`, document changes for this version.

### 3. Commit Version Bump

```bash
./checkpoint.sh "Bump version to 1.0.120"
```

### 4. Repeat Publishing Workflow

Follow Steps 2-8 above.

---

## Troubleshooting

### Error: "File already exists"

**Cause:** Can't re-upload same version to PyPI.

**Solution:** Increment version number in `src/version.py` and `pyproject.toml`.

### Error: "Invalid distribution"

**Cause:** Missing files or incorrect package structure.

**Solution:**
1. Check `python3 -m build` output for warnings
2. Verify all __init__.py files exist:
   ```bash
   find src -name "__init__.py"
   # Should show: src/ui, src/editing, src/filesystem, src/iohandler, src/ui/web
   ```

### Error: "Module not found" after install

**Cause:** Package structure incorrect in pyproject.toml.

**Solution:** Verify packages list includes all subdirectories:
```toml
packages = ["src", "src.ui", "src.ui.web", "src.editing", "src.filesystem", "src.iohandler"]
```

### Error: Backend not loading

**Cause:** Missing dependencies or import errors.

**Solution:**
1. Check `--list-backends` shows correct status
2. Test import: `python3 -c "import sys; sys.path.insert(0, 'src'); from ui.tk_ui import TkBackend"`
3. Verify MANIFEST.in includes all necessary files

---

## Automation with GitHub Actions

**Future enhancement:** Set up GitHub Actions to automatically publish on tagged releases.

See `docs/dev/PUBLISHING_TO_PYPI_GUIDE.md` section "Automation with GitHub Actions" for workflow file.

---

## Important Notes

1. **Can't delete published versions** - Be sure before publishing!
2. **Test PyPI is separate** - Must test before production
3. **Version numbers are permanent** - Can't reuse a version
4. **Tokens are secrets** - Never commit ~/.pypirc to git
5. **License is 0BSD** - Most permissive, no attribution required

---

## Quick Commands Reference

```bash
# Build
rm -rf dist/ build/ *.egg-info && python3 -m build

# Test locally
pip install dist/mbasic-*.whl

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to production
twine upload dist/*

# Verify version
cat src/version.py
grep version pyproject.toml

# Test imports
python3 -c "import sys; sys.path.insert(0, 'src'); from runtime import Runtime"
```

---

## Current Status

- ✅ `pyproject.toml` - Complete with optional dependencies
- ✅ `MANIFEST.in` - Updated to include all necessary files
- ✅ `src/ui/web/__init__.py` - Created
- ✅ `README.md` - Updated with PyPI installation instructions
- ✅ `--list-backends` command - Implemented
- ✅ Error messages - Improved with installation help
- ✅ Documentation - Complete in `docs/dev/`

**Next step:** Follow this checklist when ready to publish!

---

## Resources

- PyPI Homepage: https://pypi.org/
- Test PyPI: https://test.pypi.org/
- Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/
- Build Docs: https://pypa-build.readthedocs.io/
