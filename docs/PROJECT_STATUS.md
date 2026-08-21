# MBASIC-2025 Project Status

**Last Updated:** 2025-10-29
**Version:** 1.0.299
**Status:** ✅ Stable and Production-Ready

## Overview

MBASIC-2025 is a modern implementation of Microsoft MBASIC 5.21 with 100% backward compatibility and optional modern extensions. The project is actively maintained with continuous improvements to code quality, UX, and features.

## Project Health

| Metric | Status | Count |
|--------|--------|-------|
| **Completed Tasks** | ✅ | 68 in history/ |
| **Active TODOs** | 🔄 | 3 in dev/ |
| **Future/Deferred TODOs** | 📋 | 2 in future/ |
| **Test Coverage** | ✅ | All core features tested |
| **Documentation** | ✅ | Comprehensive |
| **Git Status** | ✅ | Clean, all committed |

## Recent Accomplishments (2025-10-29)

### Session Summary - 5 Major Improvements

1. **TODO Organization**
   - Cleaned up 5 completed TODOs
   - Moved to docs/history/ for reference
   - Deleted 1 irrelevant TODO

2. **DE_NONEIFY Code Quality Refactoring**
   - Added semantic helper methods to replace None checks
   - Improved code readability in runtime.py and parser.py
   - ~10 ambiguous checks replaced with clear intent methods
   - Example: `has_error_handler()` vs `error_handler is not None`

3. **Web UI Output Buffer Limiting**
   - Implemented line-based buffering (3,000 lines max)
   - Prevents browser memory issues
   - Changed from character-based to more predictable line-based

4. **Call Stack PC Enhancement**
   - Added statement-level precision to debugging displays
   - Format: "GOSUB from line 100.2" (line 100, statement 2)
   - Distinguishes multiple GOSUBs/FORs on same line
   - Improves debugging of complex multi-statement programs

5. **Documentation Updates**
   - All changes documented
   - WORK_IN_PROGRESS kept current
   - README and help system updated

## Core Features

### Language Implementation
- ✅ Full MBASIC 5.21 compatibility
- ✅ Statement-level execution with PC/NPC architecture
- ✅ Error handling (ON ERROR GOTO/GOSUB, RESUME)
- ✅ Control flow (GOTO, GOSUB, FOR, WHILE, IF)
- ✅ Arrays with OPTION BASE support
- ✅ DEF FN user-defined functions
- ✅ File I/O (OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT#)
- ✅ DATA/READ/RESTORE statements

### Modern Extensions
- ✅ BREAK, STEP, WATCH debugging commands
- ✅ STACK command for call stack inspection
- ✅ Multiple UI backends (CLI, Curses, TK, Web)
- ✅ Visual debugging with statement highlighting
- ✅ Auto-numbering for line entry
- ✅ Syntax highlighting
- ✅ Variable inspection and editing

### UI Backends

| Backend | Status | Features |
|---------|--------|----------|
| **CLI** | ✅ Stable | Basic terminal interface |
| **Curses** | ✅ Stable | Full-screen terminal UI |
| **TK** | ✅ Stable | Native GUI with debugging |
| **Web** | ✅ Stable | Browser-based with NiceGUI |

## Active Work (3 TODOs)

### High Priority
None currently - all high priority tasks complete

### Medium Priority

1. **PC_OLD_EXECUTION_METHODS_TODO.md**
   - Status: ⏳ TODO
   - Effort: ~8 hours
   - Description: Remove old execution methods, complete PC/NPC migration
   - Technical debt cleanup

### Low Priority

2. **INTERPRETER_REFACTOR_METHODS_NOT_VARIABLES_TODO.md**
   - Status: ⏸️ Deferred
   - Effort: ~4-5 hours
   - Description: Convert instance variables to overridable methods
   - Code quality improvement

3. **DE_NONEIFY_TODO.md**
   - Status: 🔄 Partially Complete (Phases 1-3 done)
   - Effort: ~2-3 hours remaining
   - Description: Continue replacing None checks in UI code
   - Code quality improvement

## Future/Deferred Work (2 TODOs)

1. **PRETTY_PRINTER_SPACING_TODO.md**
   - Nice-to-have formatting improvement
   - Low priority

2. **GTK_WARNING_SUPPRESSION_TODO.md**
   - Minor annoyance fix
   - Low priority

## Code Quality Metrics

### Recent Improvements
- ✅ Added semantic helper methods for clearer intent
- ✅ Reduced ambiguous None checks
- ✅ Improved parser token handling
- ✅ Enhanced runtime state management
- ✅ Better error handling clarity

### Test Status
- ✅ All core functionality tests passing
- ✅ UI backends tested (manual + automated where applicable)
- ✅ No known critical bugs
- ✅ Syntax validation clean

## Documentation

### User Documentation
- ✅ README.md - Project overview and quick start
- ✅ docs/user/ - User guides and tutorials
- ✅ docs/help/ - In-UI help system (searchable)

### Developer Documentation
- ✅ docs/dev/ - Implementation guides and status
- ✅ docs/history/ - Completed tasks archive (68 items)
- ✅ docs/design/ - Architecture decisions

### Help System
- ✅ Multi-backend support (CLI, Curses, TK, Web)
- ✅ Searchable help topics
- ✅ Context-sensitive help
- ✅ Comprehensive language reference

## Testing

### Test Coverage
- ✅ Basic language features
- ✅ Control flow (GOTO, GOSUB, FOR, WHILE)
- ✅ Error handling
- ✅ File I/O
- ✅ Arrays and variables
- ✅ User-defined functions

### Test Types
- ✅ Unit tests (Python)
- ✅ Integration tests (BASIC programs)
- ✅ UI tests (automated where possible)
- ✅ Comparison tests with real MBASIC 5.21 (run under a CP/M emulator — cpmemu is the
  preferred one; see `tests/HOW_TO_RUN_REAL_MBASIC.md`)
- ✅ Cross-toolchain tests: `utils/compare_toolchains.sh` builds the same BASIC program
  with uc80 and with z88dk and diffs what the two executables print

## Build & Deployment

### Requirements
- Python 3.8+ (3.9+ recommended)
- Optional: urwid (curses UI)
- Optional: tkinter (TK UI)
- Optional: NiceGUI (web UI)

Optional Z80/CP/M toolchain — only for building and running CP/M executables, never for
the interpreter itself:

	Role	Preferred	Supported alternate
	C compiler	uc80 (+ um80, ul80)	z88dk (zcc)
	CP/M emulator	cpmemu	tnylpo

See [Toolchain Policy](dev/TOOLCHAIN_POLICY.md) for what each alternate is still needed
for (MBF floats, true 8080 output, port I/O).

### Installation
```bash
git clone https://github.com/avwohl/mbasic.git
cd mbasic
pip install -r requirements.txt
python3 mbasic
```

### Distribution
- ✅ Git repository (GitHub)
- ✅ All Python (no compilation needed)
- ✅ Cross-platform (Linux, macOS, Windows)

## Performance

### Optimization Status
- ✅ Tick-based interpreter for responsive UI
- ✅ Statement table for fast PC navigation
- ✅ Efficient variable lookup
- ✅ Output buffer limiting (web UI)

### Known Limitations
- Line buffer limits for very long lines (MBASIC 5.21 compatible)
- Output buffer limited to 3,000 lines (web UI, configurable)

## Compatibility

### MBASIC 5.21 Compatibility
- ✅ 100% syntax compatibility
- ✅ Same error codes (where implemented)
- ✅ Same line number behavior
- ✅ Same variable scoping rules

### Extensions (Optional)
- Modern debugging commands (BREAK, STEP, WATCH, STACK)
- Multiple UI backends
- Visual debugging
- Enhanced error messages (optional)

## Community & Support

### Repository
- GitHub: https://github.com/avwohl/mbasic
- Issues: https://github.com/avwohl/mbasic/issues

### Development Activity
- ✅ Active development
- ✅ Regular commits
- ✅ Responsive to issues
- ✅ Well-documented changes

## Version History

### v1.0.299 (2025-10-29)
- ✅ DE_NONEIFY refactoring (code quality)
- ✅ Web UI output buffer limiting
- ✅ Call stack PC enhancement
- ✅ TODO cleanup and organization

### Recent Versions
- v1.0.298 - Lexer cleanup, MBASIC-2025 branding
- v1.0.287 - PC/NPC architecture improvements
- v1.0.276-278 - PC refactoring completion

## Conclusion

MBASIC-2025 is a **stable, well-maintained project** with:
- ✅ Strong foundation (100% MBASIC 5.21 compatibility)
- ✅ Modern enhancements (debugging, multiple UIs)
- ✅ Clean codebase (ongoing refactoring)
- ✅ Comprehensive documentation
- ✅ Active development

The project is ready for production use and continues to improve with regular updates.

---

*For detailed session logs, see docs/history/*
*For implementation guides, see docs/dev/*
*For user guides, see docs/user/*
