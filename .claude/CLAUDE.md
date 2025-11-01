# Notes for Claude

## Workflow Triggers
- **On EVERY startup**: Check if `docs/dev/WORK_IN_PROGRESS.md` exists → Read it and ask user to continue or start new
- **After ANY UI changes**: Update `docs/dev/UI_FEATURE_PARITY_TRACKING.md`
- **When adding a feature**: Read `docs/dev/FEATURE_COMPLETION_REQUIREMENTS.md` for 5 requirements checklist
- **Before committing**: Use `./utils/checkpoint.sh "message"` - auto-increments version, rebuilds indexes, commits, pushes

## Utility Scripts
- **Before writing a utility script**: Check `utils/UTILITY_SCRIPTS_INDEX.md` - one may already exist
- **When importing old BASIC**: Read `utils/UTILITY_SCRIPTS_INDEX.md` for processing pipeline

## 🚨 CRITICAL: Comparing with Real MBASIC
**When user asks to compare with real MBASIC 5.21**: Read `tests/HOW_TO_RUN_REAL_MBASIC.md` and follow instructions EXACTLY
- Why: "every day when i ask you to compare... it takes you like 10 tries to get it work"
- Key: Must cd to tests/, pipe content, end with SYSTEM not END

## Work-in-Progress Tracking
- **Before starting multi-step work**: Create `docs/dev/WORK_IN_PROGRESS.md` with task/status/files/next steps
- **When completing work**: Delete `WORK_IN_PROGRESS.md`
- **Format details**: See existing WORK_IN_PROGRESS.md examples in docs/history/

## TODO Tracking
- **When user requests future feature**: Create `docs/dev/*_TODO.md` (user searches for "TODO" in filenames)
- **When complete**: Move to `docs/history/` and rename TODO → DONE
- **Don't create for**: Tasks being done immediately, simple bug fixes
- **Format/examples**: See existing TODO files in docs/dev/ or DONE files in docs/history/

## Debugging
- **MBASIC_DEBUG=1 always enabled in .bashrc** - sends unexpected errors to stderr/debug link
- **When debugging**: Check debug link for stderr output (user may say "check your debug link")
- **Debug mode details**: Read `docs/dev/DEBUG_MODE.md` for levels and usage
- **In code**: Use `from src.debug_logger import debug_log` not print statements
- **NEVER write to /tmp/debug.log** - this file is reserved for user's error reports to Claude

## Developer Setup
- **For setup instructions**: Read `docs/dev/INSTALLATION_FOR_DEVELOPERS.md`
- **Dependencies**: `pip install -r requirements.txt` (standard library + optional urwid, pexpect, frontmatter, mkdocs)

# File Organization

## Directory Structure
- **Utility scripts**: `utils/` - NEVER create in root directory
- **BASIC programs**: `basic/` (working), `basic/bad_syntax/` (broken), `basic/bas_tests/` (tests)
- **Source code**: `mbasic` and core files in root (parser.py, lexer.py, etc.)
- **Documentation**: `docs/` - NEVER create .md files in root (except README.md)
  - `docs/dev/` - Current work, implementation notes, fixes, work-in-progress
  - `docs/help/` - In-UI help system (common/ for language, ui/{backend}/ for UI-specific)
  - `docs/user/` - External user guides, tutorials, quick references
  - `docs/history/` - Archived/completed work (move from dev/ when done)
  - `docs/future/` - Deferred/someday projects (move to dev/ when active)
  - `docs/design/` - Architecture and design documents
  - `docs/external/` - External references (PDFs, specs)

## Code & UI Rules
- **Code style**: Python 3, type hints, pathlib, docstrings, comments for complex logic
- **UI/UX**: NO FUNCTION KEYS (F1-F12) - user cannot use them. Use Ctrl+letter instead (Ctrl+G, Ctrl+T, etc.)

## Testing
- **Test files**: `basic/bas_tests/` - MBASIC 5.21 syntax only
- **Run tests**: `python3 mbasic <program.bas>`
- **Testing with real MBASIC**: See `tests/HOW_TO_RUN_REAL_MBASIC.md`
- **Testing curses UI**: `python3 utils/test_curses_comprehensive.py` (see `docs/dev/CURSES_UI_TESTING.md` for details)
