# Documentation Organization

## Overview

The documentation has been cleaned and organized into a clear, maintainable structure.

## Directory Structure

```
docs/
├── QUICK_REFERENCE.md          # User: Quick reference guide
├── URWID_UI.md                 # User: Curses UI documentation
│
├── help/                        # User-facing help system
│   ├── index.md                 # Help index
│   ├── getting-started.md       # Getting started guide
│   ├── editor-commands.md       # Editor commands reference
│   ├── shortcuts.md             # Keyboard shortcuts
│   ├── examples.md              # Usage examples
│   ├── language.md              # Language overview
│   │
│   ├── language/                # Language reference
│   │   └── statements/
│   │       ├── index.md
│   │       ├── print.md
│   │       └── for-next.md
│   │
│   └── ui/                      # UI-specific help
│       └── curses/
│           ├── index.md
│           ├── getting-started.md
│           ├── keyboard-commands.md
│           ├── editing.md
│           ├── running.md
│           ├── files.md
│           └── help-navigation.md
│
└── dev/                         # Development documentation
    ├── CLEANUP_SUMMARY.md       # Directory cleanup documentation
    ├── FUNCTION_KEY_REMOVAL.md  # Function key removal details
    ├── NPYSCREEN_REMOVAL.md     # npyscreen backend removal
    ├── URWID_COMPLETION.md      # urwid UI implementation
    ├── URWID_MIGRATION.md       # Migration to urwid
    ├── VARIABLE_TRACKING.md     # Variable tracking system
    ├── VARIABLE_TRACKING_CHANGES.md  # API changes
    │
    └── archive/                 # Obsolete documentation (npyscreen-related)
        ├── BREAKPOINT*.md       # 6 files - npyscreen breakpoint docs
        ├── CONTINUE*.md         # 3 files - npyscreen continue feature
        ├── CURSOR_FIX.md        # npyscreen cursor fix
        ├── DEBUGGER_COMMANDS.md # npyscreen debugger
        ├── HELP_*.md            # 2 files - npyscreen help system
        ├── IMPLEMENTATION_SUMMARY.md
        ├── MENU_CHANGES.md
        ├── MOUSE_BREAKPOINT_IMPLEMENTATION.md
        ├── TESTING_CHECKLIST.md
        ├── CHECK_STATUS.md
        ├── README_CONTINUE.md
        ├── SIMPLE_TEST.md
        └── test_bp_ui_debug.md
```

## Organization Principles

### User-Facing Documentation (`docs/`)

Located at the root of `docs/` directory:
- **Purpose**: Documentation for end users
- **Audience**: BASIC programmers using MBASIC
- **Contents**: Quick references, UI guides, tutorials

**Files:**
- `QUICK_REFERENCE.md` - Quick command reference
- `URWID_UI.md` - Curses UI user guide

### Help System (`docs/help/`)

Organized help content accessed from within MBASIC:
- **Purpose**: Interactive help system
- **Audience**: Users learning MBASIC
- **Contents**: Getting started, language reference, examples

**Structure:**
- Root: General help topics
- `language/` - BASIC language reference
- `ui/curses/` - Curses UI-specific help

### Development Documentation (`docs/dev/`)

Technical documentation for developers:
- **Purpose**: Implementation details, design decisions
- **Audience**: MBASIC developers and contributors
- **Contents**: Architecture, changes, migrations

**Current Files (7):**
1. `CLEANUP_SUMMARY.md` - Directory cleanup
2. `FUNCTION_KEY_REMOVAL.md` - Function key removal
3. `NPYSCREEN_REMOVAL.md` - npyscreen backend removal
4. `URWID_COMPLETION.md` - urwid implementation completion
5. `URWID_MIGRATION.md` - Migration from npyscreen to urwid
6. `VARIABLE_TRACKING.md` - Variable tracking implementation
7. `VARIABLE_TRACKING_CHANGES.md` - Variable tracking API changes

### Archive (`docs/dev/archive/`)

Obsolete development documentation:
- **Purpose**: Historical reference
- **Audience**: Developers investigating history
- **Contents**: npyscreen-related implementation docs

**Archived (21 files):**
- All npyscreen breakpoint implementation docs
- All npyscreen continue/step debugging docs
- npyscreen-specific cursor, menu, help system docs
- npyscreen testing and debugging notes

## Changes Made

### Moved to Archive

**npyscreen Backend Documentation (obsolete):**
- `BREAKPOINT*.md` (6 files) - Breakpoint system for npyscreen
- `CONTINUE*.md` (3 files) - Continue feature for npyscreen
- `CURSOR_FIX.md` - Cursor positioning fix for npyscreen
- `DEBUGGER_COMMANDS.md` - Debugger commands for npyscreen
- `HELP_MENU_STATUS.md` - Help menu for npyscreen
- `HELP_SYSTEM_SUMMARY.md` - Help system for npyscreen
- `IMPLEMENTATION_SUMMARY.md` - npyscreen implementation
- `MENU_CHANGES.md` - Menu system for npyscreen
- `MOUSE_BREAKPOINT_IMPLEMENTATION.md` - Mouse support for npyscreen
- `TESTING_CHECKLIST.md` - npyscreen testing
- `CHECK_STATUS.md` - npyscreen status checks
- `README_CONTINUE.md` - Continue feature README
- `SIMPLE_TEST.md` - Simple test for npyscreen
- `test_bp_ui_debug.md` - Breakpoint debugging notes

### Retained in docs/dev/

**Current Implementation Documentation:**
- `CLEANUP_SUMMARY.md` - Recent directory cleanup
- `FUNCTION_KEY_REMOVAL.md` - Current: removed function keys
- `NPYSCREEN_REMOVAL.md` - Recent: npyscreen removal
- `URWID_COMPLETION.md` - Current: urwid UI is complete
- `URWID_MIGRATION.md` - Current: migration guide
- `VARIABLE_TRACKING.md` - Current: active feature
- `VARIABLE_TRACKING_CHANGES.md` - Current: recent API changes

## Benefits

### 1. Clear Separation
- **User docs** in `docs/` root - easy to find
- **Help system** in `docs/help/` - organized by topic
- **Dev docs** in `docs/dev/` - implementation details
- **Archive** in `docs/dev/archive/` - historical reference

### 2. Reduced Clutter
- **Before**: 29 files in docs/dev/
- **After**: 7 current files + archive
- **Improvement**: 76% reduction in active dev docs

### 3. Focused Content
- Only current, relevant documentation in main areas
- Obsolete npyscreen docs archived but preserved
- Easy to find what matters for current codebase

### 4. Maintainability
- Clear what's current vs historical
- Easy to add new documentation
- Obvious where each type of doc belongs

## Usage Guidelines

### Adding New Documentation

**User Documentation:**
```bash
# User guides, tutorials, reference
docs/NEW_USER_GUIDE.md
```

**Help Content:**
```bash
# Interactive help topics
docs/help/new-topic.md
docs/help/language/statements/new-statement.md
docs/help/ui/curses/new-feature.md
```

**Development Documentation:**
```bash
# Implementation details, design decisions
docs/dev/NEW_FEATURE_IMPLEMENTATION.md
```

### When to Archive

Archive documentation when:
1. Feature has been completely removed (e.g., npyscreen)
2. Implementation has been completely replaced
3. Document is no longer relevant to current codebase
4. Keeping for historical reference only

**How to archive:**
```bash
mv docs/dev/OBSOLETE_DOC.md docs/dev/archive/
```

## Summary

The documentation is now clean, organized, and maintainable:

✅ **7 current dev docs** - All relevant to current codebase
✅ **2 user docs** - Quick reference and UI guide
✅ **15 help docs** - Complete help system
✅ **21 archived docs** - Preserved npyscreen history

Total active documentation: **24 files** (down from 45)
Reduction: **47% fewer active docs** while preserving history
