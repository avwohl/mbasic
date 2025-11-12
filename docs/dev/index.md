# Developer Documentation

This section contains implementation notes, design decisions, and development history for the MBASIC project.

**Last Updated:** 2025-11-12
**Total Documents:** 202

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

## Browse by Category

### UI Implementation

- [Web Error Logging](WEB_ERROR_LOGGING.md)
- [Web Multiuser Deployment](WEB_MULTIUSER_DEPLOYMENT.md)

### Language Features

- [Keybinding Systems](KEYBINDING_SYSTEMS.md)
- [Mb25 Runtime Library Plan](MB25_RUNTIME_LIBRARY_PLAN.md)

### File I/O

- [Backup Nonversioned Files](BACKUP_NONVERSIONED_FILES.md)
- [Docs Url Configuration](DOCS_URL_CONFIGURATION.md)
- [Keybinding Macros Migration](KEYBINDING_MACROS_MIGRATION.md)
- [Medium Severity Session Report](MEDIUM_SEVERITY_SESSION_REPORT.md)
- [Pip Install Resource Location Plan](PIP_INSTALL_RESOURCE_LOCATION_PLAN.md)
- [Printf Elimination Todo](PRINTF_ELIMINATION_TODO.md)
- [Redis Per Session Settings](REDIS_PER_SESSION_SETTINGS.md)
- [Redis Session Storage Setup](REDIS_SESSION_STORAGE_SETUP.md)

### Debugging & Errors

- [Import Consistency Fix](IMPORT_CONSISTENCY_FIX.md)
- [Low Severity Fix Report](LOW_SEVERITY_FIX_REPORT.md)
- [Random Fixes Todo](RANDOM_FIXES_TODO.md)
- [Redis Storage Bug Fix](REDIS_STORAGE_BUG_FIX.md)

### Settings & Configuration

- [Compiler Memory Config](COMPILER_MEMORY_CONFIG.md)

### Refactoring & Cleanup

- [Architecture Cleanup Todo](ARCHITECTURE_CLEANUP_TODO.md)

### Work in Progress

- [Work In Progress Final Summary](WORK_IN_PROGRESS_FINAL_SUMMARY.md)
- [Work In Progress](WORK_IN_PROGRESS.md)

### Other

- [Compiler Cpu Targets](COMPILER_CPU_TARGETS.md)
- [Compiler Missing Features](COMPILER_MISSING_FEATURES.md)
- [Compiler Remaining Work](COMPILER_REMAINING_WORK.md)
- [Compiler Setup](COMPILER_SETUP.md)
- [Compiler Status Summary](COMPILER_STATUS_SUMMARY.md)
- [Compiler Z88Dk Path Change](COMPILER_Z88DK_PATH_CHANGE.md)
- [Consistency Checker Convergence Proposal](CONSISTENCY_CHECKER_CONVERGENCE_PROPOSAL.md)
- [Kubernetes Deployment Plan](KUBERNETES_DEPLOYMENT_PLAN.md)
- [Kubernetes Deployment Setup](KUBERNETES_DEPLOYMENT_SETUP.md)
- [Kubernetes Deployment Summary](KUBERNETES_DEPLOYMENT_SUMMARY.md)
- [Linux Mint Developer Setup](LINUX_MINT_DEVELOPER_SETUP.md)
- [Path Based Tools](PATH_BASED_TOOLS.md)
- [Persistent Issues Analysis](PERSISTENT_ISSUES_ANALYSIS.md)
- [Persistent Issues Answer](PERSISTENT_ISSUES_ANSWER.md)
- [Persistent Issues Summary](PERSISTENT_ISSUES_SUMMARY.md)
- [Tnylpo Setup](TNYLPO_SETUP.md)

## Subdirectories

### old_dev_docs/

- [Accomplishments](old_dev_docs/ACCOMPLISHMENTS.md)
- [Array Input Read Fix](old_dev_docs/ARRAY_INPUT_READ_FIX.md)
- [Ast Serialization](old_dev_docs/AST_SERIALIZATION.md)
- [Auto Command Implementation](old_dev_docs/AUTO_COMMAND_IMPLEMENTATION.md)
- [Auto Numbering Implementation](old_dev_docs/AUTO_NUMBERING_IMPLEMENTATION.md)
- [Auto Numbering Visual Ui Design](old_dev_docs/AUTO_NUMBERING_VISUAL_UI_DESIGN.md)
- [Auto Numbering Web Ui Fix](old_dev_docs/AUTO_NUMBERING_WEB_UI_FIX.md)
- [Bad Syntax Analysis](old_dev_docs/BAD_SYNTAX_ANALYSIS.md)
- [Breakpoints](old_dev_docs/BREAKPOINTS.md)
- [Breakpoint Display Fix](old_dev_docs/BREAKPOINT_DISPLAY_FIX.md)
- [Breakpoint Issue Explained](old_dev_docs/BREAKPOINT_ISSUE_EXPLAINED.md)
- [Breakpoint Not Stopping Debug](old_dev_docs/BREAKPOINT_NOT_STOPPING_DEBUG.md)
- [Breakpoint Status](old_dev_docs/BREAKPOINT_STATUS.md)
- [Breakpoint Summary](old_dev_docs/BREAKPOINT_SUMMARY.md)
- [Broken Links Analysis](old_dev_docs/BROKEN_LINKS_ANALYSIS.md)
- [Browser Opening Fix](old_dev_docs/BROWSER_OPENING_FIX.md)
- [Call Implementation](old_dev_docs/CALL_IMPLEMENTATION.md)
- [Case Conflict With Chain Merge Common](old_dev_docs/CASE_CONFLICT_WITH_CHAIN_MERGE_COMMON.md)
- [Check Status](old_dev_docs/CHECK_STATUS.md)
- [Cleanup Summary](old_dev_docs/CLEANUP_SUMMARY.md)
- [Clean Install Test Results](old_dev_docs/CLEAN_INSTALL_TEST_RESULTS.md)
- [Codemirror6 Integration Issues](old_dev_docs/CODEMIRROR6_INTEGRATION_ISSUES.md)
- [Codemirror Integration Progress](old_dev_docs/CODEMIRROR_INTEGRATION_PROGRESS.md)
- [Code Comment Fixes Applied](old_dev_docs/CODE_COMMENT_FIXES_APPLIED.md)
- [Code Comment Fixes Remaining](old_dev_docs/CODE_COMMENT_FIXES_REMAINING.md)
- [Code Comment Fixes Summary](old_dev_docs/CODE_COMMENT_FIXES_SUMMARY.md)
- [Code Duplication Analysis](old_dev_docs/CODE_DUPLICATION_ANALYSIS.md)
- [Compiler Memory Optimization](old_dev_docs/COMPILER_MEMORY_OPTIMIZATION.md)
- [Continue Feature](old_dev_docs/CONTINUE_FEATURE.md)
- [Continue Fix Summary](old_dev_docs/CONTINUE_FIX_SUMMARY.md)
- [Continue Implementation](old_dev_docs/CONTINUE_IMPLEMENTATION.md)
- [Cr Line Ending Fix](old_dev_docs/CR_LINE_ENDING_FIX.md)
- [Ctrl C Input Handling](old_dev_docs/CTRL_C_INPUT_HANDLING.md)
- [Curses Feature Parity Complete](old_dev_docs/CURSES_FEATURE_PARITY_COMPLETE.md)
- [Curses Menu White Background Todo](old_dev_docs/CURSES_MENU_WHITE_BACKGROUND_TODO.md)
- [Curses Mouse Support Todo](old_dev_docs/CURSES_MOUSE_SUPPORT_TODO.md)
- [Curses Ui Feature Parity](old_dev_docs/CURSES_UI_FEATURE_PARITY.md)
- [Curses Ui File Loading Fix](old_dev_docs/CURSES_UI_FILE_LOADING_FIX.md)
- [Curses Ui Testing](old_dev_docs/CURSES_UI_TESTING.md)
- [Curses Vs Tk Gap Analysis](old_dev_docs/CURSES_VS_TK_GAP_ANALYSIS.md)
- [Cursor Fix](old_dev_docs/CURSOR_FIX.md)
- [Data Statement Fix](old_dev_docs/DATA_STATEMENT_FIX.md)
- [Debugger Commands](old_dev_docs/DEBUGGER_COMMANDS.md)
- [Debugger Ui Research](old_dev_docs/DEBUGGER_UI_RESEARCH.md)
- [Debug Mode](old_dev_docs/DEBUG_MODE.md)
- [Def Fn Implementation](old_dev_docs/DEF_FN_IMPLEMENTATION.md)
- [Def Fn Syntax Rules](old_dev_docs/DEF_FN_SYNTAX_RULES.md)
- [Detokenizer Fixes](old_dev_docs/DETOKENIZER_FIXES.md)
- [Developer Guide Index](old_dev_docs/DEVELOPER_GUIDE_INDEX.md)
- [Documentation Coverage](old_dev_docs/DOCUMENTATION_COVERAGE.md)
- [Documentation Fixes Summary](old_dev_docs/DOCUMENTATION_FIXES_SUMMARY.md)
- [Documentation Fixes Tracker](old_dev_docs/DOCUMENTATION_FIXES_TRACKER.md)
- [Editor Fixes 2025 10 30](old_dev_docs/EDITOR_FIXES_2025_10_30.md)
- [Else Keyword Fix](old_dev_docs/ELSE_KEYWORD_FIX.md)
- [Explicit Type Suffix With Defsng Issue](old_dev_docs/EXPLICIT_TYPE_SUFFIX_WITH_DEFSNG_ISSUE.md)
- [Feature Completion Requirements](old_dev_docs/FEATURE_COMPLETION_REQUIREMENTS.md)
- [Filesystem Security](old_dev_docs/FILESYSTEM_SECURITY.md)
- [File Io Implementation](old_dev_docs/FILE_IO_IMPLEMENTATION.md)
- [Functional Testing Methodology](old_dev_docs/FUNCTIONAL_TESTING_METHODOLOGY.md)
- [Function Key Removal](old_dev_docs/FUNCTION_KEY_REMOVAL.md)
- [Github Docs Workflow Explained](old_dev_docs/GITHUB_DOCS_WORKFLOW_EXPLAINED.md)
- [Gosub Stack Test Results](old_dev_docs/GOSUB_STACK_TEST_RESULTS.md)
- [Gui Library Options](old_dev_docs/GUI_LIBRARY_OPTIONS.md)
- [Hash File Io Fix](old_dev_docs/HASH_FILE_IO_FIX.md)
- [Help Build Time Indexes](old_dev_docs/HELP_BUILD_TIME_INDEXES.md)
- [Help Indexing Options](old_dev_docs/HELP_INDEXING_OPTIONS.md)
- [Help Indexing Specification](old_dev_docs/HELP_INDEXING_SPECIFICATION.md)
- [Help Integration Per Client](old_dev_docs/HELP_INTEGRATION_PER_CLIENT.md)
- [Help Menu Status](old_dev_docs/HELP_MENU_STATUS.md)
- [Help Migration Plan](old_dev_docs/HELP_MIGRATION_PLAN.md)
- [Help Migration Status](old_dev_docs/HELP_MIGRATION_STATUS.md)
- [Help Reorganization Example](old_dev_docs/HELP_REORGANIZATION_EXAMPLE.md)
- [Help System Completion](old_dev_docs/HELP_SYSTEM_COMPLETION.md)
- [Help System Diagram](old_dev_docs/HELP_SYSTEM_DIAGRAM.md)
- [Help System Reorganization](old_dev_docs/HELP_SYSTEM_REORGANIZATION.md)
- [Help System Summary](old_dev_docs/HELP_SYSTEM_SUMMARY.md)
- [Help System Web Deployment](old_dev_docs/HELP_SYSTEM_WEB_DEPLOYMENT.md)
- [Immediate Mode Design](old_dev_docs/IMMEDIATE_MODE_DESIGN.md)
- [Immediate Mode Safety](old_dev_docs/IMMEDIATE_MODE_SAFETY.md)
- [Implementation Summary](old_dev_docs/IMPLEMENTATION_SUMMARY.md)
- [Indent Command Design](old_dev_docs/INDENT_COMMAND_DESIGN.md)
- [Inkey Lprint Implementation](old_dev_docs/INKEY_LPRINT_IMPLEMENTATION.md)
- [Input Hash Fix](old_dev_docs/INPUT_HASH_FIX.md)
- [Installation For Developers](old_dev_docs/INSTALLATION_FOR_DEVELOPERS.md)
- [Installation Testing Todo](old_dev_docs/INSTALLATION_TESTING_TODO.md)
- [Interactive Command Test Coverage](old_dev_docs/INTERACTIVE_COMMAND_TEST_COVERAGE.md)
- [Interpreter Refactor Methods Not Variables Idea](old_dev_docs/INTERPRETER_REFACTOR_METHODS_NOT_VARIABLES_IDEA.md)
- [Keyword Case Scope Analysis](old_dev_docs/KEYWORD_CASE_SCOPE_ANALYSIS.md)
- [Keyword Identifier Splitting](old_dev_docs/KEYWORD_IDENTIFIER_SPLITTING.md)
- [Language Features Test Coverage](old_dev_docs/LANGUAGE_FEATURES_TEST_COVERAGE.md)
- [Language Testing Progress 2025 10 30](old_dev_docs/LANGUAGE_TESTING_PROGRESS_2025_10_30.md)
- [Lexer Cleanup Complete](old_dev_docs/LEXER_CLEANUP_COMPLETE.md)
- [Library Test Results](old_dev_docs/LIBRARY_TEST_RESULTS.md)
- [Menu Changes](old_dev_docs/MENU_CHANGES.md)
- [Mid Statement Comments Fix](old_dev_docs/MID_STATEMENT_COMMENTS_FIX.md)
- [Mid Statement Fix](old_dev_docs/MID_STATEMENT_FIX.md)
- [Mouse Breakpoint Implementation](old_dev_docs/MOUSE_BREAKPOINT_IMPLEMENTATION.md)
- [Nicegui Testing Guide](old_dev_docs/NICEGUI_TESTING_GUIDE.md)
- [Not Implemented](old_dev_docs/NOT_IMPLEMENTED.md)
- [Optional Dependencies Strategy](old_dev_docs/OPTIONAL_DEPENDENCIES_STRATEGY.md)
- [Package Dependencies](old_dev_docs/PACKAGE_DEPENDENCIES.md)
- [Parsed Inconsistencies Readme](old_dev_docs/PARSED_INCONSISTENCIES_README.md)
- [Pc Cleanup Remaining](old_dev_docs/PC_CLEANUP_REMAINING.md)
- [Pc Implementation Status](old_dev_docs/PC_IMPLEMENTATION_STATUS.md)
- [Pc Refactoring Complete](old_dev_docs/PC_REFACTORING_COMPLETE.md)
- [Popup Dialog Refactor Todo](old_dev_docs/POPUP_DIALOG_REFACTOR_TODO.md)
- [Publishing To Pypi Guide](old_dev_docs/PUBLISHING_TO_PYPI_GUIDE.md)
- [Pypi Publishing Checklist](old_dev_docs/PYPI_PUBLISHING_CHECKLIST.md)
- [Randomize Implementation](old_dev_docs/RANDOMIZE_IMPLEMENTATION.md)
- [Readme](old_dev_docs/README.md)
- [Readme Continue](old_dev_docs/README_CONTINUE.md)
- [Readme Tests Inventory](old_dev_docs/README_TESTS_INVENTORY.md)
- [Resource Limits Design](old_dev_docs/RESOURCE_LIMITS_DESIGN.md)
- [Runtime Interpreter Split Todo](old_dev_docs/RUNTIME_INTERPRETER_SPLIT_TODO.md)
- [Run Statement Implementation](old_dev_docs/RUN_STATEMENT_IMPLEMENTATION.md)
- [Session 2025 10 26](old_dev_docs/SESSION_2025_10_26.md)
- [Session 2025 10 28 Summary](old_dev_docs/SESSION_2025_10_28_SUMMARY.md)
- [Session Storage Audit](old_dev_docs/SESSION_STORAGE_AUDIT.md)
- [Session Summary 2025 Web Ui And Highlighting](old_dev_docs/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md)
- [Settings Feature Gap Analysis](old_dev_docs/SETTINGS_FEATURE_GAP_ANALYSIS.md)
- [Simple Test](old_dev_docs/SIMPLE_TEST.md)
- [Statement Highlighting Implementation](old_dev_docs/STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md)
- [Status](old_dev_docs/STATUS.md)
- [Status Bar Updates Review](old_dev_docs/STATUS_BAR_UPDATES_REVIEW.md)
- [Storage Abstraction Design](old_dev_docs/STORAGE_ABSTRACTION_DESIGN.md)
- [System Statement Fix](old_dev_docs/SYSTEM_STATEMENT_FIX.md)
- [Testing Checklist](old_dev_docs/TESTING_CHECKLIST.md)
- [Testing Guide](old_dev_docs/TESTING_GUIDE.md)
- [Testing Web Ui Fileio](old_dev_docs/TESTING_WEB_UI_FILEIO.md)
- [Test Coverage Matrix](old_dev_docs/TEST_COVERAGE_MATRIX.md)
- [Test Inventory](old_dev_docs/TEST_INVENTORY.md)
- [Test Run Results 2025-11-02](old_dev_docs/TEST_RUN_RESULTS_2025-11-02.md)
- [Tk Editor Completion Summary](old_dev_docs/TK_EDITOR_COMPLETION_SUMMARY.md)
- [Tk Editor Current State](old_dev_docs/TK_EDITOR_CURRENT_STATE.md)
- [Tk Ui Changes For Other Uis](old_dev_docs/TK_UI_CHANGES_FOR_OTHER_UIS.md)
- [Tk Ui Enhancement Plan](old_dev_docs/TK_UI_ENHANCEMENT_PLAN.md)
- [Tk Ui Feature Audit](old_dev_docs/TK_UI_FEATURE_AUDIT.md)
- [Ui Consolidation Status](old_dev_docs/UI_CONSOLIDATION_STATUS.md)
- [Ui Development Guide](old_dev_docs/UI_DEVELOPMENT_GUIDE.md)
- [Ui Feature Parity](old_dev_docs/UI_FEATURE_PARITY.md)
- [Ui Feature Parity Checklist](old_dev_docs/UI_FEATURE_PARITY_CHECKLIST.md)
- [Ui Feature Parity Tracking](old_dev_docs/UI_FEATURE_PARITY_TRACKING.md)
- [Ui Helpers Guide](old_dev_docs/UI_HELPERS_GUIDE.md)
- [Urwid Completion](old_dev_docs/URWID_COMPLETION.md)
- [Variable Editing Feature](old_dev_docs/VARIABLE_EDITING_FEATURE.md)
- [Variable Editing Standardization](old_dev_docs/VARIABLE_EDITING_STANDARDIZATION.md)
- [Variable Editing Status](old_dev_docs/VARIABLE_EDITING_STATUS.md)
- [Variable Tracking](old_dev_docs/VARIABLE_TRACKING.md)
- [Variable Tracking Changes](old_dev_docs/VARIABLE_TRACKING_CHANGES.md)
- [Variable Type Suffix Behavior](old_dev_docs/VARIABLE_TYPE_SUFFIX_BEHAVIOR.md)
- [Visual Ui Editor Enhancement](old_dev_docs/VISUAL_UI_EDITOR_ENHANCEMENT.md)
- [Web Architecture Refactor Todo](old_dev_docs/WEB_ARCHITECTURE_REFACTOR_TODO.md)
- [Web Ui Dialog Pattern](old_dev_docs/WEB_UI_DIALOG_PATTERN.md)
- [Web Ui Editor Enhancements](old_dev_docs/WEB_UI_EDITOR_ENHANCEMENTS.md)
- [Web Ui Feature Parity](old_dev_docs/WEB_UI_FEATURE_PARITY.md)
- [Web Ui Fixes 2025 10 30](old_dev_docs/WEB_UI_FIXES_2025_10_30.md)
- [Web Ui Fixes 2025 10 30 Part2](old_dev_docs/WEB_UI_FIXES_2025_10_30_PART2.md)
- [Web Ui Implementation](old_dev_docs/WEB_UI_IMPLEMENTATION.md)
- [Web Ui Options](old_dev_docs/WEB_UI_OPTIONS.md)
- [Web Ui Real Options](old_dev_docs/WEB_UI_REAL_OPTIONS.md)
- [Web Ui Testing Checklist](old_dev_docs/WEB_UI_TESTING_CHECKLIST.md)
- [Web Ui Verification Results](old_dev_docs/WEB_UI_VERIFICATION_RESULTS.md)
- [While Loop Stack Behavior](old_dev_docs/WHILE_LOOP_STACK_BEHAVIOR.md)
- [Work In Progress](old_dev_docs/WORK_IN_PROGRESS.md)
- [Work In Progress Template](old_dev_docs/WORK_IN_PROGRESS_TEMPLATE.md)
- [Test Bp Ui Debug](old_dev_docs/test_bp_ui_debug.md)

## See Also

- [MBASIC Help](../help/mbasic/index.md) - User-facing documentation
- Search function (top of page) - Find docs by keyword
