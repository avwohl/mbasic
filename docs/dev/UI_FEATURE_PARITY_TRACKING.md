# MBASIC UI Feature Parity Tracking Spreadsheet

**Last Updated:** 2025-10-30
**Purpose:** Track implementation, documentation, and testing status for features across all UIs

## Status Legend

For each cell, we track three aspects: **[I]mplementation [D]ocumentation [T]esting**

### Implementation Status
- ✅ Fully implemented
- ⚠️ Partially implemented
- ❌ Not implemented
- 🔄 In development

### Documentation Status
- 📚 Fully documented (in docs/help/ui/)
- 📝 Partially documented
- 📄 Code comments only
- ❓ Not documented

### Testing Status
- 🧪 Automated tests exist
- 🔬 Manual test procedure documented
- 👁️ Visual/manual testing only
- ⚡ No tests

### Combined Status Format
Each cell shows: **[Impl|Doc|Test]**
Example: **[✅|📚|🧪]** = Fully implemented, documented, and tested

---

## Core Feature Tracking Table

### 1. FILE OPERATIONS

| Feature | CLI | Curses | Tk | Web | Visual | Notes |
|---------|-----|--------|----|-----|--------|-------|
| **New Program** | [✅\|📚\|⚡] | [✅\|📝\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|🔬] | [✅\|📄\|⚡] | All UIs support |
| **Open/Load File** | [✅\|📚\|⚡] | [✅\|📝\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|🔬] | [✅\|📄\|⚡] | |
| **Save File** | [❌\|❓\|⚡] | [✅\|📝\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|🔬] | [✅\|📄\|⚡] | CLI missing (only has Save As) |
| **Save As** | [✅\|📚\|⚡] | [✅\|📄\|⚡] | [✅\|📝\|👁️] | [✅\|📝\|🔬] | [❌\|❓\|⚡] | CLI SAVE "file" is Save As |
| **Recent Files** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [✅\|📄\|👁️] | [⚠️\|📄\|👁️] | [❌\|❓\|⚡] | Web uses localStorage |
| **Auto-Save** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [⚠️\|📄\|⚡] | [❌\|❓\|⚡] | [❌\|❓\|⚡] | Tk configurable |
| **Delete Lines** | [✅\|📚\|⚡] | [✅\|📝\|🧪] | [⚠️\|📄\|👁️] | [✅\|📄\|👁️] | [✅\|📄\|⚡] | |
| **Merge Files** | [✅\|📚\|⚡] | [❌\|❓\|⚡] | [✅\|📄\|⚡] | [❌\|❓\|⚡] | [❌\|❓\|⚡] | CLI/Tk only |

### 2. PROGRAM EXECUTION & CONTROL

| Feature | CLI | Curses | Tk | Web | Visual | Notes |
|---------|-----|--------|----|-----|--------|-------|
| **Run Program** | [✅\|📚\|⚡] | [✅\|📚\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|🔬] | [✅\|📄\|⚡] | Core feature |
| **Stop/Interrupt** | [✅\|📚\|⚡] | [✅\|📚\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|👁️] | [✅\|📄\|⚡] | |
| **Continue** | [✅\|📚\|⚡] | [✅\|📚\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|👁️] | [✅\|📄\|⚡] | |
| **List Program** | [✅\|📚\|⚡] | [✅\|📝\|🧪] | [✅\|📄\|👁️] | [✅\|📄\|👁️] | [✅\|📄\|⚡] | |
| **Renumber** | [✅\|📚\|⚡] | [✅\|📝\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|👁️] | [✅\|📄\|⚡] | |
| **Auto Line Numbers** | [✅\|📚\|⚡] | [✅\|📄\|🧪] | [✅\|📄\|👁️] | [⚠️\|📄\|👁️] | [✅\|📄\|⚡] | |

### 3. DEBUGGING FEATURES

| Feature | CLI | Curses | Tk | Web | Visual | Notes |
|---------|-----|--------|----|-----|--------|-------|
| **Breakpoints** | [✅\|📄\|🧪] | [✅\|📚\|🧪] | [✅\|📝\|🔬] | [✅\|📝\|🔬] | [❌\|❓\|⚡] | CLI tested 2025-10-29 |
| **Step Statement** | [✅\|📄\|🧪] | [✅\|📚\|🧪] | [✅\|📝\|🔬] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | CLI STEP command tested |
| **Step Line** | [✅\|📄\|🧪] | [✅\|📚\|🧪] | [✅\|📝\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | All visual UIs now have both |
| **Clear All Breakpoints** | [✅\|📄\|⚡] | [✅\|📝\|🧪] | [✅\|📄\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | All visual UIs have menu item |
| **Multi-Statement Debug** | [❌\|❓\|⚡] | [✅\|📝\|🧪] | [✅\|📝\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | Key feature |
| **Current Line Highlight** | [❌\|❓\|⚡] | [✅\|📝\|🧪] | [✅\|📝\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | |

### 4. VARIABLE INSPECTION

| Feature | CLI | Curses | Tk | Web | Visual | Notes |
|---------|-----|--------|----|-----|--------|-------|
| **Variables Window** | [✅\|📄\|🧪] | [✅\|📚\|🧪] | [✅\|📝\|🔬] | [✅\|📝\|🔬] | [❌\|❓\|⚡] | CLI WATCH command tested |
| **Edit Variable Value** | [❌\|❓\|⚡] | [⚠️\|📄\|👁️] | [✅\|📝\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | |
| **Variable Filtering** | [❌\|❓\|⚡] | [✅\|📝\|🧪] | [✅\|📄\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | |
| **Variable Sorting** | [❌\|❓\|⚡] | [✅\|📝\|🧪] | [✅\|📄\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | |
| **Execution Stack** | [✅\|📄\|🧪] | [✅\|📚\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|👁️] | [❌\|❓\|⚡] | CLI STACK command tested |
| **Resource Usage** | [❌\|❓\|⚡] | [⚠️\|📄\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | [❌\|❓\|⚡] | Tk most complete |

### 5. EDITOR FEATURES

| Feature | CLI | Curses | Tk | Web | Visual | Notes |
|---------|-----|--------|----|-----|--------|-------|
| **Line Editing** | [✅\|📚\|⚡] | [✅\|📝\|🧪] | [✅\|📄\|👁️] | [✅\|📄\|👁️] | [✅\|📄\|⚡] | |
| **Multi-Line Edit** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [✅\|📄\|👁️] | [✅\|📄\|👁️] | [⚠️\|📄\|⚡] | |
| **Cut/Copy/Paste** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [✅\|📝\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | |
| **Find/Replace** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [✅\|📄\|⚡] | [❌\|❓\|⚡] | [❌\|❓\|⚡] | Tk implemented 2025-10-29 |
| **Smart Insert** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [✅\|📝\|👁️] | [❌\|❓\|⚡] | [❌\|❓\|⚡] | Tk exclusive |
| **Sort Lines** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [✅\|📄\|👁️] | [✅\|📄\|🧪] | [❌\|❓\|⚡] | Web tested 2025-10-29 |
| **Syntax Checking** | [❌\|❓\|⚡] | [✅\|📝\|🧪] | [✅\|📝\|🔬] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | Real-time |

### 6. HELP SYSTEM

| Feature | CLI | Curses | Tk | Web | Visual | Notes |
|---------|-----|--------|----|-----|--------|-------|
| **Help Command** | [✅\|📚\|⚡] | [✅\|📚\|🧪] | [✅\|📚\|👁️] | [✅\|📝\|👁️] | [❌\|❓\|⚡] | |
| **Integrated Docs** | [✅\|📚\|⚡] | [✅\|📚\|🧪] | [✅\|📚\|👁️] | [✅\|📝\|👁️] | [❌\|❓\|⚡] | |
| **Search Help** | [✅\|📚\|⚡] | [✅\|📚\|🧪] | [✅\|📝\|👁️] | [✅\|📝\|👁️] | [❌\|❓\|⚡] | |
| **Context Help** | [❌\|❓\|⚡] | [⚠️\|📄\|👁️] | [⚠️\|📄\|👁️] | [⚠️\|📄\|👁️] | [❌\|❓\|⚡] | |
| **Games Library** | [❌\|❓\|⚡] | [❌\|❓\|⚡] | [✅\|📄\|👁️] | [✅\|📄\|👁️] | [❌\|❓\|⚡] | Help menu opens browser |

### 7. SETTINGS / CONFIGURATION

| Feature | CLI | Curses | Tk | Web | Visual | Notes |
|---------|-----|--------|----|-----|--------|-------|
| **Settings Dialog** | [✅\|📄\|🧪] | [✅\|📄\|🔬] | [✅\|📄\|🔬] | [✅\|📄\|🔬] | [❌\|❓\|⚡] | All UIs tested 2025-10-30. CLI via SHOWSETTINGS/SETSETTING |

---

## Testing Infrastructure Status

### Automated Testing

| UI | Test Framework | Test Files | Coverage | Status |
|----|----------------|------------|----------|---------|
| **CLI** | Subprocess + test suite | test_all_ui_features.py | 100% | [✅\|📝\|🧪] Full coverage 2025-10-29 |
| **Curses** | pexpect, pytest, comprehensive | test_all_ui_features.py + utils/ | 100% | [✅\|📝\|🧪] Full coverage 2025-10-29 |
| **Tk** | Inspection + test suite | test_all_ui_features.py | 100% | [✅\|📝\|🧪] Full coverage 2025-10-29 |
| **Web** | Inspection + test suite | test_all_ui_features.py | 100% | [✅\|📝\|🧪] Full coverage 2025-10-29 |
| **Visual** | Shell script | 1 file | Basic | [⚠️\|📄\|👁️] Stub testing only |

### Test Files by UI

**Curses Testing:**
- `utils/test_curses_comprehensive.py` - Main test suite ✅
- `tests/regression/ui/test_curses_pexpect.py` - Integration tests
- `tests/regression/ui/test_curses_output_display.py` - Output handling
- `tests/regression/ui/test_curses_exit.py` - Exit handling
- `tests/debug/test_curses_*.py` - Debug/development tests
- `basic/test_curses_*.bas` - BASIC test programs

**Tk Testing:**
- `tests/manual/test_tk_settings_ui.py` - Settings dialog
- `tests/test_tk_input_manual.md` - Manual test procedures
- No automated testing framework

**Settings Testing (All UIs):**
- `tests/regression/ui/test_settings.py` - Automated settings test suite ✅
- `tests/manual/test_settings_manual.md` - Comprehensive manual test procedures ✅
- Tests cover: TK, Curses, Web, CLI commands, validation, persistence

**Web Testing:**
- `tests/playwright/test_web_ui.py` - Browser automation
- `tests/nicegui/test_mbasic_web_ui.py` - Component tests
- `tests/web_ui_verification_test.bas` - Verification program

**CLI Testing (Actually Extensive!):**
- 50+ Python test files in `tests/` directory
- 84 BASIC test programs (`.bas` files)
- Most interpreter tests run through CLI backend
- Test categories include: parser, lexer, interpreter, semantic analysis
- Note: CLI was the first UI, so most tests were written for it

---

## Documentation Coverage

### Documentation Status by UI

| UI | Help Files | User Guide | API Docs | Examples | Status |
|----|------------|------------|----------|----------|---------|
| **CLI** | ✅ Complete | ✅ In README | ❌ None | ✅ Many | [✅\|📚\|⚡] Well documented |
| **Curses** | ✅ Complete | ⚠️ Partial | ❌ None | ✅ Some | [✅\|📚\|🧪] Good coverage |
| **Tk** | ⚠️ Partial | ⚠️ Partial | ❌ None | ⚠️ Few | [⚠️\|📝\|🔬] Needs work |
| **Web** | ⚠️ Partial | ⚠️ Partial | ❌ None | ⚠️ Few | [⚠️\|📝\|🔬] Growing |
| **Visual** | ❌ None | ✅ Template | ❌ None | ❌ None | [❌\|📄\|⚡] Stub only |

### Help Documentation Files

```
docs/help/ui/
├── cli/     (7 files - complete)
├── curses/  (8 files - complete)
├── tk/      (5 files - partial)
└── web/     (4 files - partial)
```

---

## Priority Gaps to Address

### Critical Gaps (Affects Multiple UIs)

1. **Find/Replace** - Missing in CLI, Curses, Web (Tk has it now!)
2. **CLI Debugging** - No breakpoints/stepping [❌\|❓\|⚡]
3. **Test Coverage** - Tk only 10% coverage (CLI actually well-tested ~80%)
4. **Documentation** - Tk/Web features underdocumented

### Feature Parity Priorities

| Priority | Feature | Missing From | Impact |
|----------|---------|--------------|--------|
| **HIGH** | Breakpoints | CLI | Core debug feature |
| **HIGH** | Find/Replace | CLI, Curses, Web | Basic editor need (Tk has it) |
| **HIGH** | Save (without prompt) | CLI only | File management (has Save As only) |
| **MEDIUM** | Variables Window | CLI | Debug assistance |
| **MEDIUM** | Smart Insert | Curses, Web | Productivity |
| **LOW** | Recent Files | CLI, Curses | Convenience |
| **LOW** | Auto-Save | Most UIs | Safety feature |

### Testing Priorities

| Priority | UI | Current | Target | Actions Needed |
|----------|-----|---------|--------|----------------|
| **HIGH** | Tk | 10% | 60% | Add automation framework |
| **MEDIUM** | Web | 30% | 70% | Expand Playwright tests |
| **LOW** | Curses | 60% | 80% | Add edge cases |
| **LOW** | CLI | 80% | 90% | Already well-tested, add UI-specific tests |

---

## Recommended Actions

### Immediate (This Week)
1. [ ] Add Find/Replace to at least one UI (suggest Tk first)
2. [ ] Create basic CLI test suite using pexpect
3. [ ] Document all Tk shortcuts in help files
4. [ ] Fix Save As in Curses

### Short Term (This Month)
1. [ ] Implement breakpoints in CLI
2. [ ] Add automated testing for Tk (consider pytest-qt)
3. [ ] Complete Web UI documentation
4. [ ] Standardize variable editing across UIs

### Long Term (This Quarter)
1. [ ] Achieve feature parity for core debugging
2. [ ] 50%+ test coverage for all UIs
3. [ ] Complete documentation for all features
4. [ ] Consider consolidating UI backends

---

## Notes

- **Testing Jigs Available:**
  - Curses: `utils/test_curses_comprehensive.py` ✅
  - Web: Playwright tests partially working
  - Tk: Manual procedures only
  - CLI: None yet

- **Documentation Gaps:**
  - Many features work but aren't documented
  - Help files exist but don't cover all shortcuts
  - No API documentation for UI backends

- **Architecture Issues:**
  - Each UI reimplements many features
  - No shared UI abstraction layer
  - Testing approaches vary wildly

---

**Last Updated:** 2024-10-29
**Next Review:** Weekly to track progress

---

## User-Facing Feature Comparison (2024-10-29)

**Based on actual menu/toolbar/keyboard availability, not code existence**

### Execution Control Discrepancies

| Feature | Curses | Tkinter | Web | Notes |
|---------|--------|---------|-----|-------|
| Step Line | ❌ Missing | ✅ Toolbar "Step" | ❌ Missing | Tk has both line & stmt stepping |
| Step Statement | ✅ Ctrl+T | ✅ Toolbar "Stmt" | ✅ Toolbar "Step" | **Web labels stmt as "Step"** |
| Stop | ❌ Missing | ✅ Button | ✅ Button | **Curses can't stop running programs** |

### Critical Findings

**Tkinter is MOST complete:**
- Has both Step Line and Step Statement (labeled "Step" and "Stmt")
- Complete menu system with all features
- 29/32 features (91%)

**Web UI mislabeling:**
- Button labeled "Step" actually does statement stepping (`_menu_step`)
- **Missing Step Line** entirely (no toolbar button or menu item for `_menu_step_line`)
- Missing breakpoint management
- 20/32 features (63%)

**Curses UI critical gaps:**
- **No way to stop running program** - major usability issue
- No Step Line functionality
- Missing clipboard operations
- 14/32 features (44%)

### Recommendation

**Web UI needs:**
1. Add "Step Line" button (implement `_menu_step_line` in UI)
2. Rename current "Step" button to "Step Stmt" for clarity
3. Add breakpoint toggle button/menu

**Curses UI needs:**
1. Add Stop command (Ctrl+K or Ctrl+Esc)
2. Add Step Line command