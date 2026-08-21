# Developer Documentation

This section contains implementation notes, design decisions, and development history for the MBASIC project.

**Last Updated:** 2026-08-21
**Total Documents:** 52

## What's Here

This directory contains documentation for developers working on MBASIC:

- **Implementation Notes** - How features were implemented
- **Design Decisions** - Why things work the way they do
- **Testing Documentation** - Test coverage and methodologies
- **Work in Progress** - Current development tasks
- **Bug Fixes** - Historical fixes and their explanations

## Organization

Documents are organized chronologically as they were created during development. Use the search function or browse by topic below.

## For Contributors

If you're contributing to MBASIC:
1. Read `.claude/CLAUDE.md` for coding guidelines
2. Check `WORK_IN_PROGRESS.md` for current tasks
3. Review relevant implementation docs before making changes
4. Add new docs here when implementing significant features

## Z80/CP/M Toolchain

The compiler backend targets CP/M through a Z80 C toolchain and a CP/M emulator:

	Role	Preferred	Supported alternate
	C compiler	uc80 (+ um80, ul80)	z88dk (zcc)
	CP/M emulator	cpmemu	tnylpo

uc80 and cpmemu are the default pair. z88dk and tnylpo remain supported and are still
the route for Microsoft Binary Format floats, true Intel 8080 output, and `INP`/`OUT`/`WAIT`
port I/O — but they are not required. Read
[Toolchain Policy](TOOLCHAIN_POLICY.md) before editing any doc that names them, and
[Compiler Setup](COMPILER_SETUP.md) to install either pair.

## Browse by Category

### UI Implementation

- [Curses Program Keyboard](CURSES_PROGRAM_KEYBOARD.md)
- [Ios Ipad Web Ui Todo](IOS_IPAD_WEB_UI_TODO.md)
- [Tk Program Keyboard](TK_PROGRAM_KEYBOARD.md)
- [Web Error Logging](WEB_ERROR_LOGGING.md)
- [Web Multiuser Deployment](WEB_MULTIUSER_DEPLOYMENT.md)
- [Web Program Keyboard](WEB_PROGRAM_KEYBOARD.md)

### Language Features

- [Input Dollar Raw Read](INPUT_DOLLAR_RAW_READ.md)
- [Key Input Routing](KEY_INPUT_ROUTING.md)
- [Keybinding Systems](KEYBINDING_SYSTEMS.md)
- [Startrek And Gosub In Then](STARTREK_AND_GOSUB_IN_THEN.md)

### Testing & Quality

- [Tests Verified Against Binary](TESTS_VERIFIED_AGAINST_BINARY.md)

### File I/O

- [Backup Nonversioned Files](BACKUP_NONVERSIONED_FILES.md)
- [Checkpoint Validation](CHECKPOINT_VALIDATION.md)
- [Docs Url Configuration](DOCS_URL_CONFIGURATION.md)
- [Redis Per Session Settings](REDIS_PER_SESSION_SETTINGS.md)
- [Redis Session Storage Setup](REDIS_SESSION_STORAGE_SETUP.md)
- [Renum Serialization Fixes](RENUM_SERIALIZATION_FIXES.md)
- [Single Precision](SINGLE_PRECISION.md)
- [Usage Tracking Integration](USAGE_TRACKING_INTEGRATION.md)

### Debugging & Errors

- [Cli Input Handling Fixes](CLI_INPUT_HANDLING_FIXES.md)
- [Random Fixes Todo](RANDOM_FIXES_TODO.md)
- [Uc80 Bugs Todo](UC80_BUGS_TODO.md)
- [Usage Tracking Debug](USAGE_TRACKING_DEBUG.md)
- [Usage Tracking Enhanced Debug](USAGE_TRACKING_ENHANCED_DEBUG.md)

### Settings & Configuration

- [Compiler Memory Config](COMPILER_MEMORY_CONFIG.md)

### Refactoring & Cleanup

- [Architecture Cleanup Todo](ARCHITECTURE_CLEANUP_TODO.md)
- [Page Visits Cleanup](PAGE_VISITS_CLEANUP.md)

### Work in Progress

- [Mbasic 521 Divergences Todo](MBASIC_521_DIVERGENCES_TODO.md)

### Other

- [Compiler Cpu Targets](COMPILER_CPU_TARGETS.md)
- [Compiler Setup](COMPILER_SETUP.md)
- [Compiler Variable Types](COMPILER_VARIABLE_TYPES.md)
- [Compiler Z88Dk Path Change](COMPILER_Z88DK_PATH_CHANGE.md)
- [Edit Mode Typeahead](EDIT_MODE_TYPEAHEAD.md)
- [Kubernetes Deployment Plan](KUBERNETES_DEPLOYMENT_PLAN.md)
- [Kubernetes Deployment Setup](KUBERNETES_DEPLOYMENT_SETUP.md)
- [Kubernetes Deployment Summary](KUBERNETES_DEPLOYMENT_SUMMARY.md)
- [Linux Mint Developer Setup](LINUX_MINT_DEVELOPER_SETUP.md)
- [Macos Libedit Readline](MACOS_LIBEDIT_READLINE.md)
- [Mbasic 521 Sources](MBASIC_521_SOURCES.md)
- [No Memory Model](NO_MEMORY_MODEL.md)
- [Number Formatting](NUMBER_FORMATTING.md)
- [Path Based Tools](PATH_BASED_TOOLS.md)
- [Persistent Issues Analysis](PERSISTENT_ISSUES_ANALYSIS.md)
- [Persistent Issues Answer](PERSISTENT_ISSUES_ANSWER.md)
- [Persistent Issues Summary](PERSISTENT_ISSUES_SUMMARY.md)
- [Rnd Algorithm](RND_ALGORITHM.md)
- [Statement Attempt Undo](STATEMENT_ATTEMPT_UNDO.md)
- [String Pool Changes 2025 11 23](STRING_POOL_CHANGES_2025_11_23.md)
- [Tnylpo Setup](TNYLPO_SETUP.md)
- [Toolchain Policy](TOOLCHAIN_POLICY.md)
- [Windows Console Keys](WINDOWS_CONSOLE_KEYS.md)
- [Windows Import Compatibility](WINDOWS_IMPORT_COMPATIBILITY.md)

## See Also

- [MBASIC Help](../help/mbasic/index.md) - User-facing documentation
- Search function (top of page) - Find docs by keyword
