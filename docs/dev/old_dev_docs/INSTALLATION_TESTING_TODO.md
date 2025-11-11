# Installation Testing TODO

**Status:** TODO
**Priority:** MEDIUM
**Created:** 2025-10-30

## Goal

Test MBASIC installation on clean systems to ensure it works correctly for new users.

## Platforms to Test

### Linux
- ✅ Ubuntu (current development platform)
- ⬜ Ubuntu (clean install)
- ⬜ Fedora (different package manager - dnf/rpm)
- ⬜ Debian
- ⬜ Arch Linux

### macOS
- ⬜ macOS with Homebrew
- ⬜ macOS with MacPorts

### Windows
- ⬜ Windows 10/11
- ⬜ Windows with WSL

## Test Cases

### 1. Minimal Install (CLI only)
```bash
pip install mbasic-interpreter
mbasic
```
Expected: CLI works, no errors

### 2. Full Install (all UIs)
```bash
pip install mbasic-interpreter
pip install urwid nicegui  # Optional UIs
mbasic --ui curses
mbasic --ui tk
mbasic --ui web
```
Expected: All UIs work

### 3. Development Install
```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
pip install -r requirements.txt
python3 mbasic
```
Expected: Can run from source, tests work

## What to Check

- [ ] Python version compatibility (3.8+)
- [ ] Dependencies install correctly
- [ ] No missing system libraries
- [ ] All UIs launch without errors
- [ ] Help system works
- [ ] Sample programs run
- [ ] File I/O works
- [ ] Settings persist correctly

## Related

- `docs/dev/INSTALLATION_FOR_DEVELOPERS.md` - Current install guide
- `setup.py` - Package configuration
- `requirements.txt` - Dependencies

This is a future task - all development has been on Linux so far.
