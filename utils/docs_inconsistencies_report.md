# Documentation Inconsistencies Report

Generated: 2025-11-03 11:59:59

Found 552 inconsistencies:

## 🔴 High Severity

### date_inconsistency

**Description:** PROJECT_STATUS.md claims last update date of 2025-10-29, but this date is in the future (October 2025) and conflicts with the COMPILER_SEMANTIC_ANALYSIS_SESSION.md which only says '2025' without a specific date

**Affected files:**
- `PROJECT_STATUS.md`
- `design/future_compiler/COMPILER_SEMANTIC_ANALYSIS_SESSION.md`

**Details:**
PROJECT_STATUS.md: '**Last Updated:** 2025-10-29' vs COMPILER_SEMANTIC_ANALYSIS_SESSION.md: '**Session Date:** 2025'

---

### license_inconsistency

**Description:** License information is incomplete/placeholder in MBASIC_HISTORY.md

**Affected files:**
- `MBASIC_HISTORY.md`

**Details:**
MBASIC_HISTORY.md states: 'Is released under [appropriate open source license]' - this is a placeholder, not an actual license specification

---

### contradictory_information

**Description:** Contradictory recommendations for compilation strategy

**Affected files:**
- `design/future_compiler/DYNAMIC_TYPE_CHANGE_PROBLEM.md`
- `design/future_compiler/INTEGER_INFERENCE_STRATEGY.md`

**Details:**
DYNAMIC_TYPE_CHANGE_PROBLEM.md recommends 'Hybrid Strategy: Static Analysis + Tagged Storage' with tagged unions for type-unstable variables, while INTEGER_INFERENCE_STRATEGY.md recommends 'Use INTEGER Inference' with only two code paths (INTEGER and DOUBLE) and no tagged unions. The first document states 'Use tagged unions for type-unstable variables' but the second document's approach 'defaults to DOUBLE when uncertain' without mentioning tagged unions at all.

---

### contradictory_information

**Description:** Different handling of test_type_change.bas example

**Affected files:**
- `design/future_compiler/DYNAMIC_TYPE_CHANGE_PROBLEM.md`
- `design/future_compiler/INTEGER_INFERENCE_STRATEGY.md`

**Details:**
DYNAMIC_TYPE_CHANGE_PROBLEM.md states the hybrid approach should 'Preserves semantic compatibility' and handle the test case correctly with C changing types (INTEGER→SINGLE→DOUBLE). However, INTEGER_INFERENCE_STRATEGY.md explicitly states 'Result: Semantically different from interpreter!' and 'First PRINT: Shows 3.0 (or "3") instead of INTEGER 3' and 'Tradeoff: Accepts semantic difference for consistency and simplicity'.

---

### contradictory_status

**Description:** OPTIMIZATION_STATUS.md claims 27 optimizations are implemented and complete, while README.md explicitly states these are design documents only and NOT implemented

**Affected files:**
- `design/future_compiler/OPTIMIZATION_STATUS.md`
- `design/future_compiler/README.md`

**Details:**
OPTIMIZATION_STATUS.md: '**Summary: 27 optimizations implemented** (all in semantic analysis phase)' and '**Current Status: 26 optimizations implemented!**' and '**Semantic analysis phase:** ✅ COMPLETE'. README.md: '⚠️ **These are design documents only** - The current mbasic project is a **runtime interpreter**, not a compiler' and '**All documents in this directory**: Design/planning phase only' and '**Implementation status**: Not started (interpreter focus)'

---

### contradictory_status

**Description:** Internal inconsistency in optimization count - summary claims 27 implemented but conclusion says 26

**Affected files:**
- `design/future_compiler/OPTIMIZATION_STATUS.md`

**Details:**
Top of document: '**Summary: 27 optimizations implemented** (all in semantic analysis phase)'. Bottom of document: '**Current Status: 26 optimizations implemented!**'

---

### misleading_terminology

**Description:** Document uses 'implemented' and 'complete' terminology for features that are only designed/planned, not actually implemented in code

**Affected files:**
- `design/future_compiler/OPTIMIZATION_STATUS.md`

**Details:**
All 27 optimizations are marked with '**Status:** ✅ Complete' and '**Location:** `src/semantic_analyzer.py`' suggesting actual implementation, but README.md clarifies these are design documents only. The use of specific file paths like 'src/semantic_analyzer.py' implies real code exists.

---

### document_purpose_mismatch

**Description:** OPTIMIZATION_STATUS.md is written as a status/accomplishment document tracking completed work, but should be a design/planning document according to README.md

**Affected files:**
- `design/future_compiler/OPTIMIZATION_STATUS.md`

**Details:**
Document title 'Compiler Optimization Status' and language like 'tracks all optimizations implemented' suggests tracking actual implementation progress, but README.md clarifies all documents in this directory are 'Design/planning phase only'

---

### phase_numbering_conflict

**Description:** Conflicting definitions of what Phase 1 and Phase 2 accomplish

**Affected files:**
- `design/future_compiler/TYPE_REBINDING_PHASE2_DESIGN.md`
- `design/future_compiler/TYPE_REBINDING_STRATEGY.md`

**Details:**
TYPE_REBINDING_PHASE2_DESIGN.md states 'Phase 1 detects when variables can safely *change* types between program points' and 'Phase 2 extends Phase 1 by allowing variables to be **promoted**'. However, TYPE_REBINDING_STRATEGY.md describes a 'Phase 1: Basic Re-binding (Easy Wins)' and 'Phase 2: Promotion Analysis' with different scopes. The Phase 1 in STRATEGY.md includes FOR loop rebinding and sequential assignments, while PHASE2_DESIGN.md implies Phase 1 already handles type changes but is conservative about promotion.

---

### feature_scope_conflict

**Description:** Contradictory information about what Phase 1 can handle

**Affected files:**
- `design/future_compiler/TYPE_REBINDING_PHASE2_DESIGN.md`
- `design/future_compiler/TYPE_REBINDING_STRATEGY.md`

**Details:**
TYPE_REBINDING_PHASE2_DESIGN.md states 'Phase 1 behavior: Detects X changes from INTEGER → DOUBLE, Detects Y depends on X, **Conclusion**: Cannot optimize (Y depends on old X value)'. However, TYPE_REBINDING_STRATEGY.md's 'Phase 1: Basic Re-binding' explicitly includes 'FOR loop variable re-binding' and 'Sequential independent assignments' as working features, suggesting Phase 1 CAN handle these cases.

---

### terminology_inconsistency

**Description:** ACCOMPLISHMENTS.md describes the project as an 'interpreter' throughout, while ARRAY_INPUT_READ_FIX.md consistently refers to it as a 'compiler'

**Affected files:**
- `dev/ACCOMPLISHMENTS.md`
- `dev/ARRAY_INPUT_READ_FIX.md`

**Details:**
ACCOMPLISHMENTS.md: 'Successfully implemented a **complete, faithful interpreter**', 'Complete Runtime Interpreter', 'Interpreter vs Compiler - Decision: Implement as a **runtime interpreter**, not a compiler'. ARRAY_INPUT_READ_FIX.md: 'MBASIC 5.21 Compiler', 'The MBASIC 5.21 compiler now', 'pushing the compiler past the **10% milestone**'

---

### feature_status_conflict

**Description:** ACCOMPLISHMENTS.md claims 100% parser coverage and complete implementation, while ARRAY_INPUT_READ_FIX.md shows the parser was incomplete and being actively fixed

**Affected files:**
- `dev/ACCOMPLISHMENTS.md`
- `dev/ARRAY_INPUT_READ_FIX.md`

**Details:**
ACCOMPLISHMENTS.md: '**100% parser coverage** (121/121 test files parsing successfully)', 'Complete Parser Implementation ✅', 'All language features implemented'. ARRAY_INPUT_READ_FIX.md: 'The parser's READ and INPUT statements were only accepting simple variable names, not array elements', 'Success rate: 33 files (8.8%)', 'After Fix - Success rate: **41 files (11.0%)**'

---

### success_rate_conflict

**Description:** ACCOMPLISHMENTS.md reports 63% lexer success rate and 100% parser success, while ARRAY_INPUT_READ_FIX.md shows only 11% overall success rate

**Affected files:**
- `dev/ACCOMPLISHMENTS.md`
- `dev/ARRAY_INPUT_READ_FIX.md`

**Details:**
ACCOMPLISHMENTS.md: '63.0% success rate (includes non-MBASIC dialects)', '**100% parsing success** on valid MBASIC programs (121/121 test files)'. ARRAY_INPUT_READ_FIX.md: 'Success rate: **41 files (11.0%)**', 'Total parser failures: 194'

---

### implementation_status_conflict

**Description:** Conflicting information about Smart Insert Line implementation status

**Affected files:**
- `dev/AUTO_NUMBERING_VISUAL_UI_DESIGN.md`
- `dev/AUTO_NUMBERING_WEB_UI_FIX.md`

**Details:**
AUTO_NUMBERING_VISUAL_UI_DESIGN.md states '✅ **Smart Insert Line (Ctrl+I)**: IMPLEMENTED in Tk UI (src/ui/tk_ui.py:1469, bound at line 284)' but AUTO_NUMBERING_WEB_UI_FIX.md (dated 2025-10-31) describes implementing auto-numbering in Web UI as a new feature, with no mention of Ctrl+I functionality. The design doc claims Ctrl+I is implemented in Tk but not Web, yet the fix doc doesn't mention adding Ctrl+I to Web UI.

---

### feature_availability_conflict

**Description:** Web UI auto-numbering feature availability is inconsistent

**Affected files:**
- `dev/CODE_DUPLICATION_ANALYSIS.md`
- `dev/CODEMIRROR_INTEGRATION_PROGRESS.md`

**Details:**
CODE_DUPLICATION_ANALYSIS.md states 'Auto-numbering | ✓ | ✓ | ✓ | ✗' (Web UI does NOT have auto-numbering), but CODEMIRROR_INTEGRATION_PROGRESS.md at line 1161-1185 mentions 'Event handlers (keyup, click, blur, paste) are still attached using old pattern' which suggests the Web UI has event handlers that would support auto-numbering functionality.

---

### codemirror_status_conflict

**Description:** CodeMirror 6 integration status is contradictory

**Affected files:**
- `dev/CODEMIRROR6_INTEGRATION_ISSUES.md`
- `dev/CODEMIRROR_INTEGRATION_PROGRESS.md`

**Details:**
CODEMIRROR6_INTEGRATION_ISSUES.md states 'Reverted CodeMirror 6 integration. The code is still in the repository but disabled' and describes module loading failures. However, CODEMIRROR_INTEGRATION_PROGRESS.md (dated 2025-11-01, later than the issues doc) shows 'Status: IN PROGRESS' with version 1.0.354 marked as 'COMPLETED' for 'Replace Textarea with CodeMirror'. These documents present conflicting information about whether CodeMirror integration succeeded or failed.

---

### date_inconsistency

**Description:** Document date is set in the future (2025-10-28) which is impossible

**Affected files:**
- `dev/CURSES_VS_TK_GAP_ANALYSIS.md`

**Details:**
The document header states '**Date:** 2025-10-28' but the DATA_STATEMENT_FIX.md document shows implementation dates of '2025-10-22', suggesting the current year is 2025 but October 28 hasn't occurred yet, or this is a typo for 2024-10-28.

---

### directory_structure_inconsistency

**Description:** Conflicting directory structures for help system organization

**Affected files:**
- `dev/HELP_MIGRATION_PLAN.md`
- `dev/HELP_REORGANIZATION_EXAMPLE.md`
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_MIGRATION_PLAN.md proposes 'docs/help/common/language/' structure. HELP_REORGANIZATION_EXAMPLE.md shows migration from 'docs/help/common/language/' to 'docs/help/language/' (removing 'common'). HELP_SYSTEM_COMPLETION.md states final location is 'docs/help/common/language/' which contradicts the reorganization plan.

---

### file_location_inconsistency

**Description:** Inconsistent final location for language reference files

**Affected files:**
- `dev/HELP_REORGANIZATION_EXAMPLE.md`
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_REORGANIZATION_EXAMPLE.md states 'mv docs/help/common/language docs/help/language' and shows final structure as 'docs/help/language/'. HELP_SYSTEM_COMPLETION.md lists 'Location: docs/help/common/language/' for Tier 3 documentation, indicating the migration was not completed or documented incorrectly.

---

### directory_structure_inconsistency

**Description:** Conflicting directory structures for language reference documentation

**Affected files:**
- `dev/HELP_SYSTEM_DIAGRAM.md`
- `dev/HELP_SYSTEM_REORGANIZATION.md`

**Details:**
HELP_SYSTEM_DIAGRAM.md shows the final structure with 'docs/help/language/' as the location for language reference (Tier 1), while HELP_SYSTEM_REORGANIZATION.md describes the current problematic structure with both 'docs/help/common/language/' and an orphaned 'docs/help/language/' directory. The reorganization doc states 'Move language reference: mv docs/help/common/language docs/help/language' but DIAGRAM.md presents this as already completed.

---

### keybinding_conflict

**Description:** Ctrl+I keybinding is assigned to two different functions

**Affected files:**
- `dev/IMMEDIATE_MODE_DESIGN.md`
- `dev/INDENT_COMMAND_DESIGN.md`

**Details:**
IMMEDIATE_MODE_DESIGN.md assigns Ctrl+I to 'Focus immediate panel' (mentioned multiple times: 'Ctrl+I to focus', 'Press Ctrl+I - focus immediate panel', etc.). INDENT_COMMAND_DESIGN.md assigns Ctrl+I to 'auto-indent' in the Curses UI section: 'Curses: Ctrl+I for auto-indent'. Both documents propose using the same keyboard shortcut for completely different features.

---

### date_inconsistency

**Description:** Implementation date is listed as 2025-10-22, which is in the future

**Affected files:**
- `dev/INKEY_LPRINT_IMPLEMENTATION.md`

**Details:**
Document states 'Implementation Date: 2025-10-22' but this appears to be a typo - should likely be 2024-10-22 or the document is incorrectly dated

---

### date_inconsistency

**Description:** Implementation date is listed as 2025-10-22, which is in the future

**Affected files:**
- `dev/INPUT_HASH_FIX.md`

**Details:**
Document states 'Implementation Date: 2025-10-22' but this appears to be a typo - should likely be 2024-10-22 or the document is incorrectly dated

---

### contradictory_information

**Description:** Contradictory information about keyword-identifier splitting feature

**Affected files:**
- `dev/KEYWORD_IDENTIFIER_SPLITTING.md`
- `dev/LEXER_CLEANUP_COMPLETE.md`

**Details:**
KEYWORD_IDENTIFIER_SPLITTING.md (dated 2025-10-22) describes implementing keyword splitting where 'NEXTI' is parsed as 'NEXT I', claiming '+4 files successfully parsed' and 'zero regressions'. However, LEXER_CLEANUP_COMPLETE.md (dated 2025-10-29) states 'Removed STATEMENT_KEYWORDS processing that split NEXTI into NEXT I' and 'Now requires proper spacing: NextTime is an identifier, not NEXT Time'. The later document explicitly removes the feature the earlier document claims to have successfully implemented.

---

### contradictory_information

**Description:** Conflicting statements about MBASIC 5.21 syntax requirements

**Affected files:**
- `dev/KEYWORD_IDENTIFIER_SPLITTING.md`
- `dev/LEXER_CLEANUP_COMPLETE.md`

**Details:**
KEYWORD_IDENTIFIER_SPLITTING.md claims 'MBASIC and other period BASICs accepted both forms' (with and without spaces) and 'Our implementation now matches original behavior!'. However, LEXER_CLEANUP_COMPLETE.md states 'MBASIC 5.21 requires spaces' and 'Rationale: MBASIC 5.21 requires spaces. Old BASIC should use preprocessing scripts'. These are directly contradictory claims about what MBASIC 5.21 actually required.

---

### date_inconsistency

**Description:** Implementation date is listed as 2025-10-22, which is a future date and likely incorrect

**Affected files:**
- `dev/MID_STATEMENT_COMMENTS_FIX.md`

**Details:**
Document states 'Implementation Date: 2025-10-22' and '**Implementation Date**: 2025-10-22' multiple times. This appears to be a typo for 2024-10-22 or similar past date.

---

### date_inconsistency

**Description:** Implementation date is listed as 2025-10-22, which is a future date and likely incorrect

**Affected files:**
- `dev/MID_STATEMENT_FIX.md`

**Details:**
Document states '**Date**: 2025-10-22' at the top. This appears to be a typo for 2024-10-22 or similar past date.

---

### success_rate_inconsistency

**Description:** Conflicting success rates reported for the same corpus

**Affected files:**
- `dev/MID_STATEMENT_COMMENTS_FIX.md`
- `dev/MID_STATEMENT_FIX.md`

**Details:**
MID_STATEMENT_COMMENTS_FIX.md reports 'After Implementation: Successfully parsed: 53 files (22.6%)' and shows progression '20.9% → 22.6%'. However, MID_STATEMENT_FIX.md states 'Still 76 files parsing successfully (32.3%)' after its implementation. These cannot both be accurate for the same 235-file corpus.

---

### contradictory_status

**Description:** Conflicting completion status of PC refactoring

**Affected files:**
- `dev/PC_CLEANUP_REMAINING.md`
- `dev/PC_REFACTORING_COMPLETE.md`

**Details:**
PC_CLEANUP_REMAINING.md states 'Status: Mostly Complete (v1.0.293)' with '~95% complete' and lists remaining work including old execution methods and runtime fields. PC_REFACTORING_COMPLETE.md states 'Status: Fully complete including cleanup (v1.0.276 - v1.0.286)' and 'Phase 5: State Field Cleanup (v1.0.286) ✅' with 'Mission accomplished!' These directly contradict each other.

---

### contradictory_information

**Description:** Conflicting information about runtime field removal

**Affected files:**
- `dev/PC_CLEANUP_REMAINING.md`
- `dev/PC_REFACTORING_COMPLETE.md`

**Details:**
PC_CLEANUP_REMAINING.md states 'Runtime Fields Still Exist' and lists 'current_line', 'current_stmt_index', 'next_line', 'next_stmt_index' as 'Still used by old execution methods' with 'Should NOT remove yet'. PC_REFACTORING_COMPLETE.md Phase 5 states these fields were 'Converted to @property methods' and 'Removed all assignments to these cached fields' with 'Eliminated data duplication and sync issues'.

---

### date_inconsistency

**Description:** Last Updated date is impossible - document claims to be from the future

**Affected files:**
- `dev/README_TESTS_INVENTORY.md`

**Details:**
Document header states '> **Last Updated:** 2025-11-02' but the other documents are dated 2025-10-22 to 2025-10-26. November 2025 has not occurred yet relative to October 2025 dates in other files.

---

### feature_tracking_inconsistency

**Description:** Settings feature marked as complete in session summary but identified as missing/incomplete in gap analysis

**Affected files:**
- `dev/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md`
- `dev/SETTINGS_FEATURE_GAP_ANALYSIS.md`

**Details:**
SESSION_SUMMARY claims 'Settings system' is complete with 'SET, SHOW SETTINGS, HELP SET' CLI commands (v1.0.104), but SETTINGS_FEATURE_GAP_ANALYSIS states 'No SETSETTING command found, No SHOWSETTINGS command found, Settings system exists but no CLI interface!' The gap analysis explicitly searches for and cannot find these CLI commands that the session summary claims were implemented.

---

### ui_feature_parity_conflict

**Description:** Web UI feature completeness percentage contradicts between documents

**Affected files:**
- `dev/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md`
- `dev/SETTINGS_FEATURE_GAP_ANALYSIS.md`

**Details:**
SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md states Web UI is '95% feature complete' after keyboard shortcuts were added. However, SETTINGS_FEATURE_GAP_ANALYSIS.md reveals Web UI is missing the entire settings system (marked as '❌ MISSING'), which is a major feature category. The 95% figure appears to exclude settings entirely from the calculation.

---

### feature_implementation_conflict

**Description:** Curses UI command count conflicts between sessions

**Affected files:**
- `dev/SESSION_2025_10_26.md`
- `dev/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md`

**Details:**
SESSION_2025_10_26.md states 'Curses UI commands increased from 4 to 10 (150% increase)' with specific commands added including 'cmd_save', 'cmd_delete', 'cmd_renum', 'cmd_merge', 'cmd_files', 'cmd_cont'. However, SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md states 'Curses UI: Already had complete implementation!' for statement highlighting, suggesting it was already feature-complete before the October 26 session that supposedly added 6 new commands.

---

### feature_implementation_status

**Description:** STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md describes statement-level execution tracking as 'Already Implemented' with specific code locations, but STATUS.md makes no mention of this feature in any implementation status section

**Affected files:**
- `dev/STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md`
- `dev/STATUS.md`

**Details:**
STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md states: 'Statement-Level Execution Tracking ✓ - Location: src/interpreter.py:47, 257-310 - State variable: InterpreterState.current_statement_index - Runtime variable: runtime.current_stmt_index - Status: Already Implemented'. However, STATUS.md's comprehensive feature list under '✓ Fully Implemented' does not include statement-level highlighting or execution tracking anywhere.

---

### feature_implementation_status

**Description:** STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md describes Ctrl+C breakpoint and statement-level stepping as implemented, but STATUS.md does not list these debugging features

**Affected files:**
- `dev/STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md`
- `dev/STATUS.md`

**Details:**
STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md lists 'Ctrl+C Breakpoint ✓' and 'Statement-Level Stepping ✓' as already implemented features. STATUS.md mentions 'Break handling (Ctrl+C)' and 'STOP/CONT' under 'Program State Management' but does not mention statement-level stepping or the specific breakpoint implementation described.

---

### date_inconsistency

**Description:** Document claims creation date of 2025-10-28, which is in the future

**Affected files:**
- `dev/TEST_INVENTORY.md`

**Details:**
TEST_INVENTORY.md header states '**Created:** 2025-10-28' but this date has not occurred yet (appears to be a typo for 2024-10-28)

---

### keyword_policy_inconsistency

**Description:** Conflicting information about keyword case policies

**Affected files:**
- `dev/TEST_INVENTORY.md`
- `dev/TEST_RUN_RESULTS_2025-11-02.md`

**Details:**
TEST_INVENTORY.md describes test_keyword_case_policies.py as testing 'force_lower/upper/capitalize/first_wins/preserve' policies, but TEST_RUN_RESULTS_2025-11-02.md states 'Removed tests for deprecated keyword case policies' including 'error', 'first_wins', and 'preserve', leaving only 'force_lower', 'force_upper', 'force_capitalize'

---

### contradictory_information

**Description:** Enhancement plan states TK UI uses horizontal split layout that needs to be changed to vertical, but audit shows it already uses vertical layout

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN says: 'Horizontal split layout (needs to be changed to vertical like curses UI)' and 'WRONG - current implementation (to be changed): paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)'. AUDIT shows: 'paned (PanedWindow - vertical)' in widget hierarchy section 15, indicating vertical orientation is already implemented.

---

### feature_availability_conflict

**Description:** Enhancement plan lists many features as missing that audit shows are already implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN lists as missing: '❌ Line number column with status indicators (●, ?, space)', '❌ Tick-based interpreter integration', '❌ Breakpoint support (visual + functionality)', '❌ Debugger (Step/Continue/Stop)', '❌ Variables watch window (Ctrl+W)', '❌ Execution stack window (Ctrl+K)'. AUDIT shows all these are implemented: Section 3.2 'Status Column Indicators', Section 4.1 'Tick-Based Execution', Section 4.2 'Breakpoints', Section 4.3 'Stepping Modes', Section 5 'Variables Window', Section 6 'Execution Stack Window'.

---

### outdated_information

**Description:** Enhancement plan appears to be outdated as it describes features as missing that are already implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`

**Details:**
PLAN header says 'Status Assessment' and 'What's Missing' but describes the current state as having only 386 lines with basic features. AUDIT shows 3400+ lines with comprehensive implementation of all listed missing features. The plan appears to be from before the features were implemented.

---

### feature_status_conflict

**Description:** Conflicting information about Step Line implementation in Web UI

**Affected files:**
- `dev/UI_FEATURE_PARITY_CHECKLIST.md`
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
UI_FEATURE_PARITY_CHECKLIST.md states 'Step Line | ✅ | ✅ | ✅ | All have step line' under 'Debugging Features', but UI_FEATURE_PARITY_TRACKING.md (User-Facing Feature Comparison section) states 'Step Line | ❌ Missing' for Web UI and notes 'Missing Step Line entirely (no toolbar button or menu item for _menu_step_line)'

---

### feature_status_conflict

**Description:** Conflicting information about Stop/Interrupt in Curses UI

**Affected files:**
- `dev/UI_FEATURE_PARITY_CHECKLIST.md`
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
UI_FEATURE_PARITY_CHECKLIST.md states 'Stop execution | ✅ | ✅ | ✅ | Interrupt running program' for all UIs including Curses, but UI_FEATURE_PARITY_TRACKING.md states 'Stop | ❌ Missing' for Curses and notes 'Curses can't stop running programs' as a critical finding

---

### keyboard_shortcut_inconsistency

**Description:** Conflicting keyboard shortcuts for opening variables window across different UIs

**Affected files:**
- `dev/URWID_COMPLETION.md`
- `dev/VARIABLE_EDITING_STANDARDIZATION.md`
- `dev/VARIABLE_EDITING_STATUS.md`

**Details:**
URWID_COMPLETION.md does not mention Ctrl+W for variables window. VARIABLE_EDITING_STANDARDIZATION.md states 'Standard Keybinding: Ctrl+V (Variables)' for all UIs. However, VARIABLE_EDITING_STATUS.md states 'Open Variables window with Ctrl+W' for both Tk and Curses UIs, but 'Open Variables window (View menu or Ctrl+V)' for Web UI. This creates confusion about which shortcut is standard.

---

### method_naming_inconsistency

**Description:** Inconsistent naming of the debugger read method across documentation files

**Affected files:**
- `dev/VARIABLE_TRACKING.md`
- `dev/VARIABLE_TRACKING_CHANGES.md`

**Details:**
VARIABLE_TRACKING.md refers to the method as 'get_variable_debug()' in the testing section ('✅ `get_variable_debug()` doesn't update tracking'), while VARIABLE_TRACKING_CHANGES.md consistently uses 'get_variable_for_debugger()' throughout. The correct name appears to be 'get_variable_for_debugger()' based on the API reference sections in both documents.

---

### feature_implementation_conflict

**Description:** WEB_UI_EDITOR_ENHANCEMENTS.md describes Sort and Renumber features as implemented, but WEB_UI_FEATURE_PARITY.md (dated 2025-10-28, marked COMPLETE) makes no mention of these features in its comprehensive feature list

**Affected files:**
- `dev/WEB_UI_EDITOR_ENHANCEMENTS.md`
- `dev/WEB_UI_FEATURE_PARITY.md`

**Details:**
WEB_UI_EDITOR_ENHANCEMENTS.md states 'Implementation Status: ✅ Sort button added to toolbar, ✅ Sort functionality implemented, ✅ Renumber button added to toolbar' but WEB_UI_FEATURE_PARITY.md's complete feature list under 'Implemented Features' does not include Sort or Renumber under any section (Editor Features, File Operations, etc.)

---

### feature_implementation_conflict

**Description:** Editor enhancement features (Sort/Renumber) are documented as implemented but are not mentioned in the critical bug fixes document from the same timeframe

**Affected files:**
- `dev/WEB_UI_EDITOR_ENHANCEMENTS.md`
- `dev/WEB_UI_FIXES_2025_10_30.md`

**Details:**
WEB_UI_EDITOR_ENHANCEMENTS.md shows Sort/Renumber as implemented features, but WEB_UI_FIXES_2025_10_30.md (dated 2025-10-30) lists 7 critical bugs fixed without mentioning these features at all, suggesting they may not have been working or tested

---

### feature_status_conflict

**Description:** Document claims 'Full Feature Parity Achieved' but critical bugs document shows features were completely broken

**Affected files:**
- `dev/WEB_UI_FEATURE_PARITY.md`
- `dev/WEB_UI_FIXES_2025_10_30.md`

**Details:**
WEB_UI_FEATURE_PARITY.md (dated 2025-10-28) states 'Status: ✅ COMPLETE - Full Feature Parity Achieved' and 'The web UI is production-ready', but WEB_UI_FIXES_2025_10_30.md (dated 2025-10-30) states 'Fixed 7 out of 8 critical bugs in the Web UI that were making it completely unusable' including 'ALL Menus Requiring Double-Click (CRITICAL)' and 'STOP Button Doesn't Work (CRITICAL)'

---

### test_suite_conflict

**Description:** Test suite status conflicts with actual feature functionality

**Affected files:**
- `dev/WEB_UI_FIXES_2025_10_30.md`
- `dev/WEB_UI_FEATURE_PARITY.md`

**Details:**
WEB_UI_FIXES_2025_10_30.md lists '⏳ Test Suite Passing Despite Broken Features' as 'Problem: All tests pass but features were completely broken', but WEB_UI_FEATURE_PARITY.md references 'tests/playwright/test_web_ui.py - Browser-based tests' without mentioning this critical issue

---

### contradictory_information

**Description:** Fundamental contradiction about whether breakpoint pause functionality works or is fundamentally broken

**Affected files:**
- `dev/archive/BREAKPOINT_ISSUE_EXPLAINED.md`
- `dev/archive/BREAKPOINT_STATUS.md`
- `dev/archive/BREAKPOINT_SUMMARY.md`
- `dev/archive/CONTINUE_IMPLEMENTATION.md`

**Details:**
BREAKPOINT_ISSUE_EXPLAINED.md states 'The breakpoint system has a **fundamental architectural problem** with npyscreen' and 'The continue feature cannot work with npyscreen's architecture' and recommends removing the feature. However, BREAKPOINT_STATUS.md, BREAKPOINT_SUMMARY.md, and CONTINUE_IMPLEMENTATION.md all claim the feature is 'fully implemented' and 'working'. CONTINUE_IMPLEMENTATION.md explicitly states 'Status: ✅ FULLY IMPLEMENTED' and 'The continue functionality was **already implemented** in the codebase'.

---

### contradictory_information

**Description:** Conflicting information about screen display during breakpoints

**Affected files:**
- `dev/archive/BREAKPOINT_ISSUE_EXPLAINED.md`
- `dev/archive/BREAKPOINT_DISPLAY_FIX.md`
- `dev/archive/CONTINUE_FIX_SUMMARY.md`

**Details:**
BREAKPOINT_ISSUE_EXPLAINED.md states '❌ **Cannot display UI during breakpoint pause** - npyscreen doesn't support this' and claims the pause UI was disabled. However, BREAKPOINT_DISPLAY_FIX.md and CONTINUE_FIX_SUMMARY.md describe a fix that makes the screen visible during breakpoints, with CONTINUE_FIX_SUMMARY.md stating 'Expected Behavior Now: When a breakpoint hits, you should see: ✅ **Editor window** - Your BASIC program code'.

---

### broken_cross_reference

**Description:** ASCII codes document references CHR$ function with incorrect filename

**Affected files:**
- `help/common/language/appendices/ascii-codes.md`

**Details:**
Line references '../functions/crr_dollar.md' but the actual file is 'chr_dollar.md'. The link text says 'CHR$ Function' but points to wrong file.

---

### duplicate_function_documentation

**Description:** CHR$ function is documented twice with different filenames

**Affected files:**
- `help/common/language/functions/chr_dollar.md`
- `help/common/language/functions/crr_dollar.md`

**Details:**
chr_dollar.md documents CHR$ with syntax 'CHR$(I)' while crr_dollar.md also documents the same function with identical syntax. The title in crr_dollar.md is 'CRR$' but the content describes CHR$.

---

### typo_in_function_name

**Description:** ABS function syntax shows 'ASS' instead of 'ABS'

**Affected files:**
- `help/common/language/functions/abs.md`

**Details:**
In abs.md, the syntax section shows 'ASS (X)' but the title and description correctly refer to 'ABS'.

---

### broken_reference

**Description:** Index file references incorrect filenames for CHR$ and CDBL functions

**Affected files:**
- `help/common/language/functions/index.md`

**Details:**
Index lists '[CHR$](crr_dollar.md)' and '[CDBL](cobl.md)' but the actual files are 'chr_dollar.md' and 'cdbl.md'. Also references '[SPACE$](spaces.md)' but the actual file is 'space_dollar.md'.

---

### broken_reference

**Description:** MKI$/MKS$/MKD$ See Also section references incorrect filenames

**Affected files:**
- `help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md`

**Details:**
References '[COBL](cobl.md)' and '[CRR$](crr_dollar.md)' but the actual files should be 'cdbl.md' and 'chr_dollar.md'.

---

### broken_reference

**Description:** SPACES See Also section references incorrect filenames

**Affected files:**
- `help/common/language/functions/spaces.md`

**Details:**
References '[COBL](cobl.md)' and '[CRR$](crr_dollar.md)' but the actual files should be 'cdbl.md' and 'chr_dollar.md'.

---

### contradictory_information

**Description:** DEF FN documentation contradicts itself about function name length and spacing requirements

**Affected files:**
- `help/common/language/statements/def-fn.md`

**Details:**
The document states 'Function names can be multiple characters' and provides examples like FNABC, FNUCASE$, FNDIST, but also states 'Space after FN is optional' with examples showing 'DEF FN A(X)' vs 'DEF FNA(X)'. This creates confusion about whether 'FN A' (with space) creates a function named 'A' or 'FNA'. The syntax section shows 'DEF FN<name>' suggesting no space, but alternative forms show 'DEF FN<name>' with optional spaces, making it unclear if the space is part of the name or a separator.

---

### incomplete_documentation

**Description:** DEFINT/SNG/DBL/STR document contains unrelated DEF USR content

**Affected files:**
- `help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
The document includes a section '2.13 ~ USR' with 'Format: DEF USR[<digit>]=<integer expression>' which appears to be content from a different command (DEF USR) incorrectly included in the DEFINT/SNG/DBL/STR documentation. This is clearly misplaced content from a different section of the original manual.

---

### malformed_syntax_examples

**Description:** Syntax examples contain invalid BASIC code

**Affected files:**
- `help/common/language/statements/let.md`

**Details:**
let.md shows '110 LET 0=12' which is invalid (cannot assign to literal 0), and '120 LET E=12A2' which appears to be OCR errors or typos (should likely be '12^2' or similar).

---

### missing_ui_reference

**Description:** Web UI is mentioned in compatibility.md but not consistently listed in other documents describing available UIs

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/extensions.md`
- `help/mbasic/features.md`
- `help/mbasic/getting-started.md`

**Details:**
compatibility.md mentions 'CLI, Tk, and Curses UIs' for real filesystem and 'Web UI' for virtual filesystem. extensions.md lists '1. CLI, 2. Curses, 3. Tk, 4. Web' but getting-started.md only mentions 'Curses UI (Default), CLI Mode, Tkinter GUI' without Web UI. features.md does not mention Web UI at all in the 'User Interface Features' section.

---

### keyboard_shortcut_conflict

**Description:** Conflicting keyboard shortcuts for the same action - Ctrl+E mapped to two different functions

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+E' is listed as 'Move to end of line' under Editing Commands. In quick-reference.md: 'Ctrl+E' is listed as 'Renumber all lines (RENUM)' under Editing section. Also in keyboard-commands.md under Program Commands: 'Ctrl+E' is 'Renumber program lines (RENUM command)'.

---

### keyboard_shortcut_conflict

**Description:** Conflicting keyboard shortcuts for Ctrl+L - mapped to different functions in different contexts

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+L' is 'List program to output window' under Program Commands. In quick-reference.md: 'Ctrl+L' is 'List program (or Step Line when debugging)' under Program Management, and 'Step Line - execute all statements on current line' under Debugger section.

---

### keyboard_shortcut_conflict

**Description:** Different keys documented for stopping execution

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+Q' for Stop execution. In quick-reference.md: 'Ctrl+X' for Stop execution (eXit).

---

### keyboard_shortcut_inconsistency

**Description:** Inconsistent keyboard shortcuts for stopping program execution

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/tk/getting-started.md`
- `help/ui/tk/features.md`

**Details:**
keyboard-shortcuts.md lists 'Ctrl+Q' for 'Stop execution' and 'Ctrl+C' for 'Interrupt running program', but getting-started.md and features.md reference '{{kbd:stop_program}}' without defining what that shortcut is. The actual key binding is unclear.

---

### keyboard_shortcut_inconsistency

**Description:** Different keyboard shortcuts documented for Variables Window

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/tk/features.md`

**Details:**
keyboard-shortcuts.md states 'Ctrl+V' for 'Show/hide Variables window', but features.md uses '{{kbd:toggle_variables}}' without defining it. Additionally, Ctrl+V typically means Paste in standard text editing.

---

### keyboard_shortcut_inconsistency

**Description:** Help system keyboard shortcuts conflict

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/tk/feature-reference.md`

**Details:**
keyboard-shortcuts.md states 'F1 or Ctrl+H' for 'Open help topics', but feature-reference.md lists 'Ctrl+H' for 'Find & Replace'. This is a direct conflict where the same shortcut is assigned to two different functions.

---

### keyboard_shortcut_inconsistency

**Description:** Settings dialog keyboard shortcut missing for Tk UI

**Affected files:**
- `help/ui/curses/settings.md`
- `help/ui/tk/settings.md`

**Details:**
curses/settings.md clearly states 'Ctrl+,' to open settings, but tk/settings.md only mentions 'Menu: File → Settings' and 'Keyboard shortcut: (check your system's menu)' without specifying the actual shortcut.

---

### feature_availability_conflict

**Description:** Contradictory information about debugger availability in Web UI

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/web-interface.md`

**Details:**
debugging.md provides comprehensive documentation of debugging features including 'Visual breakpoint management', 'Step-by-step execution', 'Real-time variable inspection', 'Call stack visualization', etc. However, web-interface.md explicitly states under Limitations: 'No debugger or breakpoint support (yet)'. These directly contradict each other.

---

### feature_availability_conflict

**Description:** Debugging features documented but not mentioned in getting started

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/getting-started.md`

**Details:**
debugging.md documents extensive debugging capabilities including breakpoints, variable inspection, and call stack. getting-started.md mentions 'Step Line' and 'Step Stmt' buttons in the toolbar and describes stepping through code, but doesn't mention breakpoints, variable inspection panels, or other debugging features described in debugging.md. This creates confusion about what's actually available.

---

### ui_component_inconsistency

**Description:** Inconsistent descriptions of UI layout and panels

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/features.md`
- `help/ui/web/debugging.md`

**Details:**
getting-started.md describes 'a simple, vertical layout' with numbered components 1-7 including Menu Bar, Toolbar, Program Editor, Output, Input Area, Command Area, and Status Bar. features.md mentions 'Resizable panels', 'Hide/show panels', 'Horizontal/vertical split' suggesting a more complex layout. debugging.md describes 'Variables Panel' in 'right sidebar' and 'Call Stack' panel, which aren't mentioned in getting-started.md's layout description.

---

### completion_status_inconsistency

**Description:** Document marked as COMPLETE but contains incomplete tasks

**Affected files:**
- `history/CALLSTACK_UI_PC_ENHANCEMENT_DONE.md`

**Details:**
Header shows 'Status: ✅ COMPLETE (v1.0.300)' but Phase 2 section shows 'Curses UI' with checkboxes marked complete for some items but unchecked items remain: '[ ] Locate FOR loop stack display code', '[ ] Change format to include statement positions', '[ ] Test with multi-statement line programs'. Phase 3 and Phase 4 also have all tasks unchecked. This contradicts the COMPLETE status.

---

### directory_path_inconsistency

**Description:** Conflicting documentation directory paths - one shows 'doc/' and the other shows 'doc/doc/'

**Affected files:**
- `history/DIRECTORY_STRUCTURE.md`
- `history/DOC_REORGANIZATION_COMPLETE.md`

**Details:**
DIRECTORY_STRUCTURE.md shows structure as 'doc/' (e.g., '├── doc/ # Documentation (*.md files)') while DOC_REORGANIZATION_COMPLETE.md consistently refers to 'doc/doc/' (e.g., 'doc/doc/', 'doc/doc/design/', 'doc/doc/history/'). This is a fundamental path inconsistency.

---

### directory_existence_inconsistency

**Description:** Conflicting information about bad_not521 vs bas_not51 directory

**Affected files:**
- `history/DIRECTORY_STRUCTURE.md`
- `history/DOC_REORGANIZATION_COMPLETE.md`

**Details:**
DIRECTORY_STRUCTURE.md refers to 'basic/bad_not521/ # Non-MBASIC 5.21 dialect files (20 files)' in the structure and later 'basic/bas_not51/ (20 files)' in the detailed section. These appear to be the same directory with inconsistent naming.

---

### contradictory_information

**Description:** Contradictory dates - both files claim to be from 2025-10-22 but show different test results and success rates

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md: 'Date: 2025-10-22, Context: After reaching 92/215 (42.8%) success rate'. FAILURE_CATEGORIZATION_CURRENT.md: 'Date: 2025-10-22 (Latest), Success Rate: 104/215 files (48.4%)'. Both claim same date but show progression from 92 to 104 files.

---

### contradictory_information

**Description:** Conflicting counts for EOF() function files

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md lists '5 Files' for EOF() function: 'direct.bas, genielst.bas, rbbent27.bas, sink.bas, timeout.bas'. FAILURE_CATEGORIZATION_CURRENT.md lists '7 files' for EOF() function: 'direct.bas, genielst.bas, rbbent27.bas, rbbmin27.bas, rbspurge.bas, rbsutl31.bas, simcvt.bas'.

---

### contradictory_information

**Description:** Completely different test corpus sizes and success metrics

**Affected files:**
- `history/FINAL_RESULTS.md`
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FINAL_RESULTS.md: '373 CP/M era BASIC programs, 221/373 (59.4%) success'. FAILURE_CATEGORIZATION.md: '215 files, 92/215 (42.8%)'. FAILURE_CATEGORIZATION_CURRENT.md: '215 files, 104/215 (48.4%)'. Different total file counts (373 vs 215) suggest different test corpora.

---

### contradictory_information

**Description:** Status contradicts implementation state

**Affected files:**
- `history/FILEIO_MODULE_ARCHITECTURE_DONE.md`

**Details:**
Header says 'Status: COMPLETED' but document clearly states 'Not Working: SandboxedFileIO is stub - returns empty results, FILES doesn't work in web UI, Web UI still has security issue (no sandboxing yet)'. This is not a completed feature.

---

### date_inconsistency

**Description:** Implementation date is listed as 2025-10-24, which is in the future relative to other documents dated 2025-10-22 and 2025-10-26

**Affected files:**
- `history/IMPLEMENTATION_COMPLETE.md`

**Details:**
IMPLEMENTATION_COMPLETE.md states 'Implementation Date: 2025-10-24' but INTERPRETER_IMPLEMENTATION_2025-10-22.md is dated '2025-10-22' and INPUT_SANITIZATION_DONE.md shows dates '2025-10-26'. The chronology suggests 2025-10-24 should be between these dates, but the content suggests it may be a typo for 2024-10-24.

---

### feature_status_conflict

**Description:** DEFINT/DEFSNG/DEFDBL/DEFSTR marked as both broken and implemented

**Affected files:**
- `history/LANGUAGE_TESTING_DONE.md`
- `history/LANGUAGE_CHANGES.md`

**Details:**
LANGUAGE_TESTING_DONE.md states: 'DEFINT/DEFSTR/DEFDBL/DEFSNG are marked as implemented in STATUS.md and have help documentation, but are actually broken' with example 'Syntax error in 70: Unknown DEF statement token type: TokenType.DEFINT'. However, the same document later shows 'Final Status (2025-10-31) - COMPLETE ✅' with '✅ **DEFINT issue FIXED** - Now parses and works correctly'. LANGUAGE_CHANGES.md discusses DEFINT as a feature to implement but doesn't mention it being broken or fixed.

---

### feature_status_conflict

**Description:** MISSING_OPERATORS_DONE shows RANDOMIZE as implemented and tested, but PARSER_TEST_RESULTS shows it as causing 3 parser failures (1.5%)

**Affected files:**
- `history/MISSING_OPERATORS_DONE_2025-10-31.md`
- `history/PARSER_TEST_RESULTS.md`

**Details:**
MISSING_OPERATORS_DONE_2025-10-31.md: 'RANDOMIZE Statement - Final Status: ✅ Interpreter implemented execute_randomize(), ✅ Test suite created and passing'. PARSER_TEST_RESULTS.md: 'RANDOMIZE statement | 3 | 1.5% | RNG initialization (not implemented)'

---

### feature_status_conflict

**Description:** PC_OLD_EXECUTION_METHODS document marked as COMPLETE but describes work as deferred

**Affected files:**
- `history/PC_OLD_EXECUTION_METHODS_DONE.md`
- `history/PHASE1_IO_ABSTRACTION_PROGRESS.md`

**Details:**
PC_OLD_EXECUTION_METHODS_DONE.md has 'Status: ✅ COMPLETE' in the header but the 'Decision' section states 'Defer this work until: 1. All tick-based UIs are stable and tested...' and 'This is technical debt, not a blocking issue.' A completed task should not have a decision to defer the work.

---

### status_contradiction

**Description:** File name indicates task is DONE but status field shows TODO

**Affected files:**
- `history/PRESERVE_ORIGINAL_SPACING_DONE.md`

**Details:**
Filename: 'PRESERVE_ORIGINAL_SPACING_DONE.md' but content shows '⏳ **Status:** TODO' at the top of the document. This is a direct contradiction between the filename and the documented status.

---

### project_scope_contradiction

**Description:** README describes project as compiler while REFACTORING_COMPLETE describes it as interpreter

**Affected files:**
- `history/README.md`
- `history/REFACTORING_COMPLETE.md`

**Details:**
README.md states 'The project started as a **compiler** effort but evolved into an **interpreter** implementation' and discusses compiler vs interpreter considerations. However, REFACTORING_COMPLETE.md consistently refers to 'MBASIC 5.21 interpreter' and 'The MBASIC 5.21 interpreter has been successfully refactored' without acknowledging any compiler aspects.

---

### date_inconsistency

**Description:** Impossible date: October 22, 2025 and October 28-29, 2025 are in the future, but documents are written as historical records

**Affected files:**
- `history/SEMANTIC_ANALYSIS_FOR_BASIC_2025-10-22.md`
- `history/SESSION_2025-10-29_IMPROVEMENTS.md`
- `history/SESSION_2025-10-29_PC_REFACTORING.md`
- `history/SESSION_2025_10_28_HELP_SEARCH_IMPROVEMENTS.md`
- `history/SESSION_2025_10_28_KEYWORD_CASE_INTEGRATION.md`

**Details:**
SEMANTIC_ANALYSIS_FOR_BASIC_2025-10-22.md has '**Date**: 2025-10-22', SESSION_2025-10-29_IMPROVEMENTS.md has '**Date:** October 29, 2025', SESSION_2025-10-29_PC_REFACTORING.md has '**Date:** October 29, 2025', SESSION_2025_10_28_HELP_SEARCH_IMPROVEMENTS.md has '**Date:** 2025-10-28', SESSION_2025_10_28_KEYWORD_CASE_INTEGRATION.md has '**Date:** 2025-10-28'. These dates are in the future but documents describe completed work.

---

### status_contradiction

**Description:** File name indicates DONE but status field shows TODO

**Affected files:**
- `history/SINGLE_SOURCE_OF_TRUTH_DONE.md`

**Details:**
Filename: 'SINGLE_SOURCE_OF_TRUTH_DONE.md' but content shows '⏳ **Status:** TODO' at the top. This is contradictory - either the file should be renamed to remove _DONE suffix, or the status should be updated to DONE/COMPLETE.

---

### status_contradiction

**Description:** File name indicates DONE but content appears to be a TODO request

**Affected files:**
- `history/STRING_GARBAGE_COLLECTION_DONE.md`

**Details:**
Filename: 'STRING_GARBAGE_COLLECTION_DONE.md' but content is a request to 'Write a document that details how string allocation and garbage collection worked'. This appears to be a TODO item, not a completed document.

---

### status_contradiction

**Description:** File name indicates DONE but status field shows TODO and action items are incomplete

**Affected files:**
- `history/TESTING_SYSTEM_ORGANIZATION_DONE.md`

**Details:**
Filename: 'TESTING_SYSTEM_ORGANIZATION_DONE.md' but content shows '## Status: ⏳ TODO' and Phase 1 is marked complete but Phases 2-5 are all marked with '[ ]' (incomplete). Only 1 of 5 phases is complete.

---

### date_inconsistency

**Description:** Document title claims to cover October 23-24, 2025, but actually documents October 23-25, 2025

**Affected files:**
- `history/TIMELINE_OCT_23-25.md`

**Details:**
Title says '# MBASIC Project Timeline: October 23-24, 2025' but the document includes extensive coverage of October 25, 2025 (Sessions 8-10) with 141 commits and ~15.25 hours of work. The Executive Summary also states 'October 23-24, 2025' but later sections clearly document October 25 work.

---

### statistics_inconsistency

**Description:** Total duration and commits mismatch between Executive Summary and actual content

**Affected files:**
- `history/TIMELINE_OCT_23-25.md`

**Details:**
Executive Summary states 'Total Duration: ~38 hours over 2 days' and 'Total Commits: 70 commits', but the Combined Statistics section shows 'Total: ~29.25 hours over 3 days' and 'Total: 211 commits'. The document clearly covers 3 days (Oct 23-25) not 2 days.

---

### version_number_mismatch

**Description:** Overlapping version numbers between timeline documents

**Affected files:**
- `history/TIMELINE_OCT_27-28.md`
- `history/TIMELINE_OCT_28-31.md`

**Details:**
TIMELINE_OCT_27-28.md ends at version 1.0.106 (Session 2 on Oct 28, 12:22 AM - 12:27 AM). TIMELINE_OCT_28-31.md starts at version 1.0.106 (12:30 PM on Oct 28). However, TIMELINE_OCT_28-31.md Session 1 claims to start at 12:30 PM but the first session in TIMELINE_OCT_27-28.md for Oct 28 ends at 12:27 AM (early morning). There's a time gap but the version numbers overlap exactly at 1.0.106.

---

### session_overlap

**Description:** Oct 28 sessions appear in both timeline documents with different content

**Affected files:**
- `history/TIMELINE_OCT_27-28.md`
- `history/TIMELINE_OCT_28-31.md`

**Details:**
TIMELINE_OCT_27-28.md covers Oct 28 12:01 AM - 12:27 AM (Architecture and Settings System). TIMELINE_OCT_28-31.md covers Oct 28 12:30 PM - 4:07 PM (Web UI fixes) and later sessions. Both documents claim to cover October 28, but with completely different work sessions and no acknowledgment of the other document's coverage.

---

### date_inconsistency

**Description:** Document dated 2025-10-22 which is a future date (impossible)

**Affected files:**
- `history/TOKEN_USAGE_SUMMARY_2025-10-22.md`

**Details:**
File header shows '**Date**: 2025-10-22' but this date is in the future. Should likely be 2024-10-22 or the document is misdated.

---

### feature_implementation_conflict

**Description:** Document claims Web UI lacks features that were later implemented

**Affected files:**
- `history/TRUE_100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`

**Details:**
TRUE_100_PERCENT document (dated 2025-10-29, version 1.0.301) states Web UI does NOT have: Current Line Highlight, Edit Variable Value, Variable Filtering, or Syntax Checking. However, VARIABLE_SORT_REFACTORING document shows Web UI has variable sorting implemented with Tk-style controls, suggesting more advanced variable features exist than the earlier document claims.

---

### date_inconsistency

**Description:** Document dates are inconsistent with timeline feasibility

**Affected files:**
- `history/VISUAL_BACKENDS_CURSES_TK.md`
- `history/VISUAL_UI_REFACTORING_PLAN.md`

**Details:**
VISUAL_BACKENDS_CURSES_TK.md is dated '2025-10-24' (future date from current perspective) while VISUAL_UI_REFACTORING_PLAN.md shows 'Last Updated: 2025-10-24'. Both documents reference the same future date, suggesting either incorrect dating or the documents are from a future context.

---

### file_path_inconsistency

**Description:** Web UI implementation file path inconsistency across documents

**Affected files:**
- `history/WEB_MULTI_USER_SESSION_ISOLATION_DONE.md`
- `history/WEB_UI_PARITY_DONE.md`
- `history/WEB_UI_MISSING_FEATURES_OLD.md`

**Details:**
WEB_MULTI_USER_SESSION_ISOLATION_DONE.md references 'src/ui/web/nicegui_backend.py' throughout. WEB_UI_PARITY_DONE.md references 'src/ui/web/web_ui.py' for implementations (e.g., 'Location: src/ui/web/web_ui.py:551-684'). WEB_UI_MISSING_FEATURES_OLD.md also references 'src/ui/web/nicegui_backend.py'. This suggests either: (1) the file was renamed from nicegui_backend.py to web_ui.py, or (2) there are two different web UI files, or (3) there's an error in one of the documents.

---

### keybinding_conflict

**Description:** Contradictory information about help keybinding in Curses UI

**Affected files:**
- `history/session_2025-10-25_help_system_keybindings.md`
- `history/session_keybinding_system_implementation.md`

**Details:**
In 'session_2025-10-25_help_system_keybindings.md', the help key was changed from Ctrl+M to Ctrl+A: 'Changed Ctrl+H → Ctrl+A for help (A for Assist/About)' and later states 'Ctrl+A → Opens table of contents (index.md)'. However, in 'session_keybinding_system_implementation.md', it states: 'Help key updated from Ctrl+A to Ctrl+H to match JSON' and 'Curses UI reads and uses JSON keybindings' with examples showing 'Ctrl+H' as the help key.

---

### date_inconsistency

**Description:** Web UI implementation document claims date of 2025-10-25, but all other session documents are dated 2025-10-22. The web UI session appears to be from a different date than the parser improvement sessions.

**Affected files:**
- `history/session_web_ui_implementation.md`
- `history/sessions/FINAL_SESSION_SUMMARY.md`
- `history/sessions/SESSION_2025-10-22_SUMMARY.md`
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`
- `history/snapshots/PARSER_STATUS_2025-10-22.md`

**Details:**
Web UI doc: '**Date**: 2025-10-25' vs Parser docs: '**Date**: 2025-10-22' or 'Date: 2025-10-22'

---

### success_rate_inconsistency

**Description:** Multiple conflicting success rates and file counts reported for the same date (2025-10-22). Different documents show different starting and ending points.

**Affected files:**
- `history/sessions/FINAL_SESSION_SUMMARY.md`
- `history/sessions/SESSION_2025-10-22_SUMMARY.md`
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`
- `history/snapshots/PARSER_STATUS_2025-10-22.md`

**Details:**
FINAL_SESSION_SUMMARY: '29 files (7.8%)' to '41 files (11.0%)' with 373 total files. SESSION_2025-10-22_SUMMARY: '69 files (29.4%)' to '74 files (31.5%)' with 235 files. SESSION_FINAL_SUMMARY: '113/163 files (69.3%)' to '120/161 files (74.5%)'. PARSER_STATUS: '119/193 (61.7%)'

---

### corpus_size_inconsistency

**Description:** Total corpus size varies dramatically across documents: 373 files, 235 files, 163 files, 161 files, 193 files, and 219 files are all mentioned.

**Affected files:**
- `history/sessions/FINAL_SESSION_SUMMARY.md`
- `history/sessions/SESSION_2025-10-22_SUMMARY.md`
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`
- `history/snapshots/PARSER_STATUS_2025-10-22.md`

**Details:**
FINAL_SESSION_SUMMARY: '373 files'. SESSION_2025-10-22_SUMMARY: '235 MBASIC-compatible files'. SESSION_FINAL_SUMMARY: '163 files' then '161 files'. PARSER_STATUS: '193 files'. SESSION_FINAL_SUMMARY also mentions '219 .bas files' total.

---

### session_overlap_conflict

**Description:** Three different 'final' or 'summary' documents all claim to be from 2025-10-22 but describe completely different work with different starting points, features, and results. They appear to be from different sessions or different projects entirely.

**Affected files:**
- `history/sessions/FINAL_SESSION_SUMMARY.md`
- `history/sessions/SESSION_2025-10-22_SUMMARY.md`
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`

**Details:**
All three documents are dated 2025-10-22 and claim to be session summaries, but describe mutually exclusive work: one focuses on file I/O and arrays (373 file corpus), another on ELSE and keyword splitting (235 file corpus), and a third on RESET and REM handling (161-163 file corpus).

---

### contradictory_statistics

**Description:** Test corpus size mismatch - one document reports 373 files tested, another reports 163 files

**Affected files:**
- `history/snapshots/PARSER_TEST_REPORT_2025-10-22.md`
- `history/snapshots/PARSE_ERROR_CATEGORIES_2025-10-22.md`

**Details:**
PARSER_TEST_REPORT_2025-10-22.md states 'Comprehensive testing of the MBASIC 5.21 lexer and parser against **373 CP/M-era BASIC programs**' and 'Total files tested: 373'. However, PARSE_ERROR_CATEGORIES_2025-10-22.md states 'Total Failures: 50 files (30.7% of 163 file corpus)' and 'Successfully Parsing: 113 files (69.3%)', indicating a corpus of only 163 files.

---

### contradictory_statistics

**Description:** Success rate mismatch - different success rates reported for parser

**Affected files:**
- `history/snapshots/PARSER_TEST_REPORT_2025-10-22.md`
- `history/snapshots/PARSE_ERROR_CATEGORIES_2025-10-22.md`

**Details:**
PARSER_TEST_REPORT_2025-10-22.md reports '**Successfully parsed** | **29** | **7.8%**' with 'End-to-End Success Rate: 7.8%'. However, PARSE_ERROR_CATEGORIES_2025-10-22.md reports 'Successfully Parsing: 113 files (69.3%)', which is dramatically different.

---

### contradictory_statistics

**Description:** Parser failure count mismatch

**Affected files:**
- `history/snapshots/PARSER_TEST_REPORT_2025-10-22.md`
- `history/snapshots/PARSE_ERROR_CATEGORIES_2025-10-22.md`

**Details:**
PARSER_TEST_REPORT_2025-10-22.md states '**Parser failures** | **206** | **55.2%**' out of 373 files. PARSE_ERROR_CATEGORIES_2025-10-22.md states 'Total Failures: 50 files (30.7% of 163 file corpus)', which is a completely different number.

---

### keyboard_shortcut_inconsistency

**Description:** Inconsistent keyboard shortcuts for Variables window across different UI documentation

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md mentions 'Ctrl+W in TK UI' for Variables & Resources window. TK_UI_QUICK_START.md lists both 'Ctrl+V' for Variables window and 'Ctrl+W' for Variables & Resources window. keyboard-shortcuts.md (Curses UI) uses 'Ctrl+W' for toggle variables watch window. This creates confusion about which shortcut does what in which UI.

---

## 🟡 Medium Severity

### project_name_inconsistency

**Description:** Project name inconsistency - MBASIC_HISTORY.md refers to project as 'mbasic' while PROJECT_STATUS.md calls it 'MBASIC-2025'

**Affected files:**
- `MBASIC_HISTORY.md`
- `PROJECT_STATUS.md`

**Details:**
MBASIC_HISTORY.md: 'This project (`mbasic`) is:' vs PROJECT_STATUS.md: '# MBASIC-2025 Project Status' and 'MBASIC-2025 is a modern implementation'

---

### ui_backend_inconsistency

**Description:** UI backend naming inconsistency - PROJECT_STATUS.md lists 'TK' while README.md lists 'tk' (lowercase) and also mentions 'visual' backend not in PROJECT_STATUS table

**Affected files:**
- `PROJECT_STATUS.md`
- `README.md`

**Details:**
PROJECT_STATUS.md lists: 'CLI, Curses, TK, Web' while README.md lists: 'cli, curses, tk, visual' with different capitalization and an additional 'visual' backend

---

### version_inconsistency

**Description:** Version history shows v1.0.299 as current but also mentions v1.0.298 and v1.0.287, v1.0.276-278 without clear indication if these are all real versions or examples

**Affected files:**
- `PROJECT_STATUS.md`

**Details:**
PROJECT_STATUS.md: '**Version:** 1.0.299' and '### v1.0.299 (2025-10-29)' but the date 2025-10-29 is in the future

---

### feature_scope_inconsistency

**Description:** PROJECT_STATUS.md describes current production features while COMPILER_SEMANTIC_ANALYSIS_SESSION.md describes future compiler work as complete, creating confusion about what's actually implemented

**Affected files:**
- `PROJECT_STATUS.md`
- `design/future_compiler/COMPILER_SEMANTIC_ANALYSIS_SESSION.md`

**Details:**
PROJECT_STATUS.md describes interpreter as 'Production-Ready' with current features, while COMPILER_SEMANTIC_ANALYSIS_SESSION.md states 'SEMANTIC ANALYSIS PHASE: COMPLETE AND PRODUCTION-READY' for a compiler that appears to be future work based on the directory name 'future_compiler'

---

### contradictory_information

**Description:** Inconsistent type system complexity

**Affected files:**
- `design/future_compiler/DYNAMIC_TYPE_CHANGE_PROBLEM.md`
- `design/future_compiler/INTEGER_INFERENCE_STRATEGY.md`

**Details:**
DYNAMIC_TYPE_CHANGE_PROBLEM.md discusses a type system with INTEGER, SINGLE, and DOUBLE types throughout (e.g., 'INTEGER < SINGLE < DOUBLE' hierarchy, SINGLE operations with ADDSS/SUBSS). INTEGER_INFERENCE_STRATEGY.md simplifies to only INTEGER and DOUBLE, stating 'Only two code paths (INTEGER and DOUBLE)' and never mentions SINGLE type handling in its approach.

---

### contradictory_information

**Description:** Different conclusions about semantic correctness tradeoff

**Affected files:**
- `design/future_compiler/DYNAMIC_TYPE_CHANGE_PROBLEM.md`
- `design/future_compiler/INTEGER_INFERENCE_STRATEGY.md`

**Details:**
DYNAMIC_TYPE_CHANGE_PROBLEM.md concludes 'The recommended hybrid approach: ✅ Preserves semantic compatibility' as a key benefit. INTEGER_INFERENCE_STRATEGY.md's comparison table shows 'Semantic Correctness' as ⭐⭐ (2 stars) for INTEGER Inference, same as DEFDBL A-Z, indicating it does NOT preserve semantic compatibility, contradicting the first document's recommendation.

---

### implementation_status_conflict

**Description:** Integer size inference status unclear in iterative optimization implementation

**Affected files:**
- `design/future_compiler/INTEGER_SIZE_INFERENCE.md`
- `design/future_compiler/ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md`

**Details:**
INTEGER_SIZE_INFERENCE.md states 'Status: Design complete, ready for implementation' and lists it as not yet implemented. However, ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md (dated 2025-10-24, marked COMPLETE) does not mention integer size inference in its list of iterative optimizations in Phase 2, nor in the _count_optimizations() method, suggesting it may not be integrated yet despite the iterative framework being complete.

---

### optimization_list_inconsistency

**Description:** Different lists of optimizations in iterative loop

**Affected files:**
- `design/future_compiler/ITERATIVE_OPTIMIZATION_STRATEGY.md`
- `design/future_compiler/ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md`

**Details:**
ITERATIVE_OPTIMIZATION_STRATEGY.md lists 'Category B: Iterative' optimizations including 'Constant folding & propagation', 'Boolean simplification', 'Copy propagation', 'Dead code elimination', and 'Strength reduction'. However, ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md's actual implementation in Phase 2 only lists: 'Loop-invariant detection, Reachability analysis, Forward substitution, Live variable analysis, Available expressions, Type rebinding' - missing several optimizations mentioned in the strategy document.

---

### missing_optimization_integration

**Description:** Integer size inference not mentioned in iterative optimization clearing logic

**Affected files:**
- `design/future_compiler/INTEGER_SIZE_INFERENCE.md`
- `design/future_compiler/ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md`

**Details:**
INTEGER_SIZE_INFERENCE.md describes integer size inference as part of the optimization framework and mentions it should be 'integrated into analyze() method' and 'Add to iterative optimization loop'. However, ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md's _clear_iterative_state() method does not mention integer_size or range_info in the 'MUST RECALCULATE' section, though it does preserve range_info in the 'NEVER STALE' section, creating ambiguity about whether integer size inference is part of the iterative loop.

---

### internal_contradiction

**Description:** Loop Analysis is categorized as 'NEVER STALE' but has an exception that contradicts this classification

**Affected files:**
- `design/future_compiler/OPTIMIZATION_DATA_STALENESS_ANALYSIS.md`

**Details:**
In Category 1 (STRUCTURAL - Never Stale), Loop Analysis is marked as '✅ Keep - Never stale' but immediately followed by '⚠️ Exception: iteration_count might benefit from constants'. This suggests it's not truly 'never stale' if iteration_count can change based on constant propagation. However, in the 'NEVER STALE' classification section, self.loops is listed without qualification.

---

### inconsistent_categorization

**Description:** self.alias_info appears in RECALCULATE ONCE AT END section but is not analyzed in Category 3 (REPORTING ONLY)

**Affected files:**
- `design/future_compiler/OPTIMIZATION_DATA_STALENESS_ANALYSIS.md`

**Details:**
self.alias_info is listed under 'RECALCULATE ONCE AT END (Reporting)' but is not discussed in the 'Category 3: REPORTING ONLY' section where other reporting-only analyses like string_pool, builtin_function_calls, array_bounds_violations, and string_concat_in_loops are detailed.

---

### file_reference_inconsistency

**Description:** README.md references ACCOMPLISHMENTS.md as former name of SEMANTIC_ANALYSIS_DESIGN.md, but OPTIMIZATION_STATUS.md doesn't mention this renaming

**Affected files:**
- `design/future_compiler/README.md`

**Details:**
README.md: '**SEMANTIC_ANALYSIS_DESIGN.md** (formerly ACCOMPLISHMENTS.md)' but OPTIMIZATION_STATUS.md doesn't acknowledge it was ever called ACCOMPLISHMENTS.md or reference SEMANTIC_ANALYSIS_DESIGN.md

---

### file_reference_inconsistency

**Description:** README.md references COMPILER_SEMANTIC_ANALYSIS_SESSION.md as formerly SESSION_SUMMARY.md, creating potential confusion about file naming

**Affected files:**
- `design/future_compiler/README.md`

**Details:**
README.md: '**COMPILER_SEMANTIC_ANALYSIS_SESSION.md** (formerly SESSION_SUMMARY.md)' - this renaming history is not mentioned in OPTIMIZATION_STATUS.md

---

### scope_inconsistency

**Description:** OPTIMIZATION_STATUS.md describes optimizations as if they're part of a working compiler with actual code locations, while README.md clarifies the project is an interpreter without these features

**Affected files:**
- `design/future_compiler/OPTIMIZATION_STATUS.md`
- `design/future_compiler/README.md`

**Details:**
OPTIMIZATION_STATUS.md provides detailed implementation locations like '**Location:** `src/semantic_analyzer.py` - `ConstantEvaluator` class' suggesting working code, but README.md states 'The current mbasic project is a **faithful interpreter** for MBASIC 5.21' and 'These compiler optimizations would require: Static analysis at "compile time"'

---

### file_structure_inconsistency

**Description:** Inconsistent documentation file naming and location

**Affected files:**
- `design/future_compiler/README_OPTIMIZATIONS.md`
- `design/future_compiler/SEMANTIC_ANALYSIS_DESIGN.md`

**Details:**
README_OPTIMIZATIONS.md lists 'ACCOMPLISHMENTS.md' as a top-level file in the mbasic/ directory, but SEMANTIC_ANALYSIS_DESIGN.md refers to itself as 'ACCOMPLISHMENTS.md' in multiple places (e.g., 'ACCOMPLISHMENTS.md - This file'). The actual filename is SEMANTIC_ANALYSIS_DESIGN.md, not ACCOMPLISHMENTS.md.

---

### documentation_reference_inconsistency

**Description:** Inconsistent self-reference in documentation files

**Affected files:**
- `design/future_compiler/README_OPTIMIZATIONS.md`
- `design/future_compiler/SEMANTIC_ANALYSIS_DESIGN.md`

**Details:**
README_OPTIMIZATIONS.md footer states 'For detailed technical information, see: - `ACCOMPLISHMENTS.md` - Full project summary' but the actual file providing the full project summary is SEMANTIC_ANALYSIS_DESIGN.md, which internally refers to itself as 'ACCOMPLISHMENTS.md - This file' in its own documentation section.

---

### duplicate_content

**Description:** Section '5. Constant Folding Optimization' appears twice in the document with identical content

**Affected files:**
- `design/future_compiler/SEMANTIC_ANALYZER.md`

**Details:**
The section appears first after 'Line Number Validation' (section 7) and then again after 'Usage' section. Both instances describe the same feature with identical examples and explanations. The second instance should likely be removed or the numbering is incorrect (section 5 appears after section 7).

---

### content_organization

**Description:** Advanced Optimizations section appears after Examples but contains core features already discussed

**Affected files:**
- `design/future_compiler/SEMANTIC_ANALYZER.md`

**Details:**
The 'Advanced Optimizations' section at the end discusses 'Loop Analysis' and 'Subroutine Side-Effect Analysis', but 'GOSUB/Subroutine Analysis' was already covered in detail in section 7 of Key Features. This creates confusion about whether these are separate features or the same feature described twice.

---

### feature_status_mismatch

**Description:** Type checking listed as future enhancement but type rebinding analysis already implemented

**Affected files:**
- `design/future_compiler/SEMANTIC_ANALYZER.md`
- `design/future_compiler/TYPE_REBINDING_IMPLEMENTATION_SUMMARY.md`

**Details:**
SEMANTIC_ANALYZER.md lists 'Type checking: Detect type mismatches at compile time' as a future enhancement, but TYPE_REBINDING_IMPLEMENTATION_SUMMARY.md shows that type analysis is already implemented with TypeBinding dataclass and _analyze_variable_type_bindings() method integrated as pass 15.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for the same concept: 'Type Re-binding' vs 'Type Rebinding'

**Affected files:**
- `design/future_compiler/TYPE_REBINDING_PHASE2_DESIGN.md`
- `design/future_compiler/TYPE_REBINDING_STRATEGY.md`

**Details:**
TYPE_REBINDING_STRATEGY.md uses 'Type Re-binding' (with hyphen) in title and throughout, while TYPE_REBINDING_PHASE2_DESIGN.md uses 'Type Rebinding' (no hyphen). Both refer to the same concept of variables changing types at compile time.

---

### conceptual_overlap

**Description:** Unclear distinction between type rebinding and type promotion

**Affected files:**
- `design/future_compiler/TYPE_REBINDING_PHASE2_DESIGN.md`
- `design/future_compiler/TYPE_REBINDING_STRATEGY.md`

**Details:**
TYPE_REBINDING_PHASE2_DESIGN.md defines 'Type Rebinding (Phase 1): Variable completely changes type at a program point, Old value is NOT carried forward' vs 'Type Promotion (Phase 2): Variable is widened (INT→DOUBLE) while keeping value, Old value IS carried forward'. However, TYPE_REBINDING_STRATEGY.md's example 'X = 10 (INTEGER), Y = X + 1 (INTEGER), X = 10.5 (DOUBLE), Z = Y + X (Promote Y to DOUBLE)' shows promotion happening within what it calls the rebinding strategy, blurring the distinction.

---

### implementation_status_conflict

**Description:** Conflicting status indicators for implementation phases

**Affected files:**
- `design/future_compiler/TYPE_REBINDING_PHASE2_DESIGN.md`
- `design/future_compiler/TYPE_REBINDING_STRATEGY.md`

**Details:**
TYPE_REBINDING_PHASE2_DESIGN.md ends with 'Status: Design phase, Priority: High, Dependency: Phase 1 complete ✅', suggesting Phase 1 is complete. However, TYPE_REBINDING_STRATEGY.md ends with 'Should we proceed with Phase 1 implementation?' suggesting Phase 1 is not yet implemented.

---

### implementation_date_conflict

**Description:** Both documents claim implementation on the same date (2025-10-22) but describe different features

**Affected files:**
- `dev/ARRAY_INPUT_READ_FIX.md`
- `dev/AUTO_COMMAND_IMPLEMENTATION.md`

**Details:**
ARRAY_INPUT_READ_FIX.md: 'Implementation Date: 2025-10-22' (array subscript fix). AUTO_COMMAND_IMPLEMENTATION.md: '**Date**: 2025-10-22' (AUTO command implementation)

---

### scope_inconsistency

**Description:** ACCOMPLISHMENTS.md describes a complete, production-ready system while ARRAY_INPUT_READ_FIX.md describes active development with significant parsing failures

**Affected files:**
- `dev/ACCOMPLISHMENTS.md`
- `dev/ARRAY_INPUT_READ_FIX.md`

**Details:**
ACCOMPLISHMENTS.md: 'complete, production-ready implementation', 'All core features are implemented, tested, and documented'. ARRAY_INPUT_READ_FIX.md: 'Total parser failures: 194', 'Remaining "Expected : or newline" Errors', describes ongoing fixes and improvements

---

### date_inconsistency

**Description:** Document header shows future date

**Affected files:**
- `dev/AUTO_NUMBERING_VISUAL_UI_DESIGN.md`

**Details:**
Document header states 'Date: 2025-10-26' but other documents show dates like '2025-10-30' and '2025-10-31', suggesting this is either a typo (should be 2024-10-26) or the dates are inconsistent across documents.

---

### feature_scope_inconsistency

**Description:** Different auto-numbering trigger mechanisms described

**Affected files:**
- `dev/AUTO_NUMBERING_VISUAL_UI_DESIGN.md`
- `dev/AUTO_NUMBERING_WEB_UI_FIX.md`

**Details:**
AUTO_NUMBERING_VISUAL_UI_DESIGN.md describes auto-numbering as 'Basic auto-numbering on Enter: IMPLEMENTED in Tk and Curses UIs (src/ui/tk_ui.py:1305, src/ui/curses_ui.py:479)'. However, AUTO_NUMBERING_WEB_UI_FIX.md (Implementation 2025-10-31 section) states 'Auto-numbering now triggers when **leaving a line**, not just on Enter' with triggers including 'Arrow keys (up/down)', 'Mouse click', and 'Blur (focus out)'. This represents a significant behavioral difference not mentioned in the design doc.

---

### file_reference_inconsistency

**Description:** Different file locations referenced for same functionality

**Affected files:**
- `dev/AUTO_NUMBERING_VISUAL_UI_DESIGN.md`
- `dev/AUTO_NUMBERING_WEB_UI_FIX.md`

**Details:**
AUTO_NUMBERING_VISUAL_UI_DESIGN.md states 'Renumber command with dialog: IMPLEMENTED in Tk, Curses, and Web UIs (src/ui/web/web_ui.py:476)' but AUTO_NUMBERING_WEB_UI_FIX.md consistently references 'src/ui/web/nicegui_backend.py' for Web UI implementation. It's unclear if web_ui.py and nicegui_backend.py are the same file or different files.

---

### version_mismatch

**Description:** Version numbers are inconsistent across documentation files

**Affected files:**
- `dev/CODEMIRROR_INTEGRATION_PROGRESS.md`
- `dev/CLEAN_INSTALL_TEST_RESULTS.md`

**Details:**
CODEMIRROR_INTEGRATION_PROGRESS.md mentions versions 1.0.349-1.0.354, while CLEAN_INSTALL_TEST_RESULTS.md doesn't specify any version numbers. The version progression suggests these documents may be from different time periods.

---

### file_location_inconsistency

**Description:** Documentation file locations don't match the cleanup summary

**Affected files:**
- `dev/CLEANUP_SUMMARY.md`
- `dev/CODEMIRROR_INTEGRATION_PROGRESS.md`

**Details:**
CLEANUP_SUMMARY.md shows final structure with docs in 'docs/dev/' (e.g., 'docs/dev/NPYSCREEN_REMOVAL.md'), but the current files being analyzed are in 'dev/' directory (e.g., 'dev/CODEMIRROR_INTEGRATION_PROGRESS.md'), suggesting the cleanup may not have been completed or these are different directories.

---

### date_inconsistency

**Description:** Analysis dates suggest temporal inconsistency

**Affected files:**
- `dev/CODE_DUPLICATION_ANALYSIS.md`
- `dev/CODEMIRROR_INTEGRATION_PROGRESS.md`

**Details:**
CODE_DUPLICATION_ANALYSIS.md is dated '2025-10-26' and mentions consolidation completed on '2025-10-26'. CODEMIRROR_INTEGRATION_PROGRESS.md is dated '2025-11-01' (6 days later). However, the version numbers in CODEMIRROR_INTEGRATION_PROGRESS.md (1.0.349-1.0.354) seem to span a longer development period than 6 days would suggest.

---

### version_number_mismatch

**Description:** Version numbers mentioned don't align with typical semantic versioning progression

**Affected files:**
- `dev/CURSES_FEATURE_PARITY_COMPLETE.md`

**Details:**
Document mentions versions 1.0.206-1.0.209 which suggests 4 versions, but only describes changes in 4 distinct versions (1.0.206, 1.0.207, 1.0.208, 1.0.209). The version jump from 1.0.206 to 1.0.209 is only 3 increments but covers 4 features.

---

### contradictory_information

**Description:** Contradictory information about ProgramManager.lines structure

**Affected files:**
- `dev/CURSES_UI_FEATURE_PARITY.md`
- `dev/CURSES_UI_FILE_LOADING_FIX.md`

**Details:**
CURSES_UI_FEATURE_PARITY.md states in the 'Known Issues to Check' section: 'Correct approach: Store lines exactly as entered: "20 PRINT I" (no leading spaces)' and 'char_start/char_end from parser are relative to the stored text'. However, CURSES_UI_FILE_LOADING_FIX.md describes the current architecture as 'ProgramManager.lines is Dict[int, str] mapping line_number → complete line text' and shows code that uses regex to 'Extract code part (without line number)' with pattern r'^\d+\s+(.*)'. This implies lines ARE stored WITH line numbers, contradicting the feature parity doc's statement about storing lines 'exactly as entered' without formatting.

---

### outdated_information

**Description:** Task tracking shows completed items but 'Known Issues to Check' section not updated

**Affected files:**
- `dev/CURSES_UI_FEATURE_PARITY.md`

**Details:**
The 'Task Tracking' section shows Phase 1 and Phase 2 tasks as '✅ Completed', including '1.10 Update window header to show sort mode/direction' and '2.3 Update menu/help display to show both'. However, the 'Known Issues to Check' section still has '⬜ NOT CHECKED YET' with unchecked items like '[ ] Verify curses UI doesn't add leading spaces to line numbers' and '[ ] Check if statement highlighting works correctly'. If Phase 1 and 2 are complete, these checks should have been performed.

---

### feature_implementation_conflict

**Description:** Conflicting information about Step Line implementation status

**Affected files:**
- `dev/CURSES_VS_TK_GAP_ANALYSIS.md`
- `dev/DEBUGGER_UI_RESEARCH.md`

**Details:**
CURSES_VS_TK_GAP_ANALYSIS.md states 'Step Line (full line) | ✅ | ✅ | ✅ SAME' indicating Step Line is implemented in both UIs. However, DEBUGGER_UI_RESEARCH.md states 'Missing: Step Line Mode' and 'tick(mode='step_line', max_statements=1) # Step Line (NEW - not yet implemented)' indicating it's not implemented.

---

### keyboard_shortcut_conflict

**Description:** Different keyboard shortcuts proposed for Step Line

**Affected files:**
- `dev/CURSES_VS_TK_GAP_ANALYSIS.md`
- `dev/DEBUGGER_UI_RESEARCH.md`

**Details:**
CURSES_VS_TK_GAP_ANALYSIS.md shows 'Step Line | Present | Ctrl+L' while DEBUGGER_UI_RESEARCH.md proposes 'F10: Step Line'. These are different key bindings for the same function.

---

### keyboard_shortcut_conflict

**Description:** Different keyboard shortcuts proposed for Step Statement

**Affected files:**
- `dev/CURSES_VS_TK_GAP_ANALYSIS.md`
- `dev/DEBUGGER_UI_RESEARCH.md`

**Details:**
CURSES_VS_TK_GAP_ANALYSIS.md shows 'Step Statement | Present | Ctrl+T' while DEBUGGER_UI_RESEARCH.md proposes 'F11: Step Statement'. These are different key bindings for the same function.

---

### feature_implementation_conflict

**Description:** Conflicting information about Pause functionality

**Affected files:**
- `dev/CURSES_VS_TK_GAP_ANALYSIS.md`
- `dev/DEBUGGER_UI_RESEARCH.md`

**Details:**
DEBUGGER_UI_RESEARCH.md lists 'Pause/Break (Ctrl+Break)' and 'F8: Pause' as standard debugger controls. However, CURSES_VS_TK_GAP_ANALYSIS.md does not mention a Pause command in the Run Menu comparison, only showing Run, Step Line, Step Statement, Continue, and Stop.

---

### version_inconsistency

**Description:** Inconsistent MBASIC version references

**Affected files:**
- `dev/DEF_FN_IMPLEMENTATION.md`
- `dev/DEF_FN_SYNTAX_RULES.md`

**Details:**
DEF_FN_IMPLEMENTATION.md title says 'MBASIC 5.21 Compiler' but DEF_FN_SYNTAX_RULES.md says 'Verified with MBASIC 5.21'. The first implies it's a compiler for 5.21, the second implies testing against 5.21 interpreter.

---

### contradictory_information

**Description:** Timeline shows impossible date progression

**Affected files:**
- `dev/ELSE_KEYWORD_FIX.md`

**Details:**
ELSE_KEYWORD_FIX.md shows 'Implementation Date: 2025-10-22' but the document describes events and testing that would have occurred after implementation. The dates 2025-10-22 and 2025-10-27 are in the future relative to typical documentation practices, suggesting either placeholder dates or a date format issue.

---

### date_inconsistency

**Description:** Multiple documents reference dates in 2025 (October 2025, January 2025) which appear to be future dates, suggesting either incorrect year or the documents are templates

**Affected files:**
- `dev/GITHUB_DOCS_WORKFLOW_EXPLAINED.md`
- `dev/FUNCTIONAL_TESTING_METHODOLOGY.md`

**Details:**
GITHUB_DOCS_WORKFLOW_EXPLAINED.md: 'Fixed in v1.0.103 (October 28, 2025)', FUNCTIONAL_TESTING_METHODOLOGY.md: 'Created: 2025-10-29', 'Test Executed: 2025-10-29', FEATURE_COMPLETION_REQUIREMENTS.md: 'Auto-numbering Bug (2025-01)', 'Settings Feature Gap (2025-01)'

---

### ui_list_inconsistency

**Description:** FEATURE_COMPLETION_REQUIREMENTS.md lists 5 UIs (CLI, Curses, TK, Web, Visual) while FUNCTION_KEY_REMOVAL.md only discusses 2 curses UIs (Urwid and Legacy Curses), with no mention of Visual UI

**Affected files:**
- `dev/FEATURE_COMPLETION_REQUIREMENTS.md`
- `dev/FUNCTION_KEY_REMOVAL.md`

**Details:**
FEATURE_COMPLETION_REQUIREMENTS.md: 'Document status for EACH UI: CLI, Curses, TK, Web, Visual'. FUNCTION_KEY_REMOVAL.md only covers 'Urwid UI' and 'Legacy Curses UI' with no discussion of Visual UI or whether it uses function keys

---

### implementation_status_conflict

**Description:** Conflicting information about help indexing implementation status

**Affected files:**
- `dev/HELP_INDEXING_OPTIONS.md`
- `dev/HELP_BUILD_TIME_INDEXES.md`

**Details:**
HELP_INDEXING_OPTIONS.md discusses help indexing as a future feature with recommendations ('For immediate use: Implement grep-based search', 'For future enhancement: Add front matter + build index'), while HELP_BUILD_TIME_INDEXES.md shows 'Status: ✅ IMPLEMENTED' with a date of 2025-10-27, indicating the front matter + build index approach has been completed. These documents appear to represent different stages but could confuse readers about current state.

---

### path_inconsistency

**Description:** Inconsistent help root path construction

**Affected files:**
- `dev/HELP_INDEXING_SPECIFICATION.md`
- `dev/HELP_INTEGRATION_PER_CLIENT.md`

**Details:**
HELP_INDEXING_SPECIFICATION.md shows 'help_root = Path(__file__).parent.parent / "docs" / "help"' in Phase 2, but HELP_INTEGRATION_PER_CLIENT.md shows 'help_root = Path(__file__).parent.parent.parent / "docs" / "help"' (three .parent calls) in multiple places. The correct number of parent directory traversals is inconsistent.

---

### tier_naming_inconsistency

**Description:** Tier numbering reversed between documents

**Affected files:**
- `dev/HELP_REORGANIZATION_EXAMPLE.md`
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_REORGANIZATION_EXAMPLE.md defines: 'TIER 1: Language Reference', 'TIER 2: MBASIC Implementation', 'TIER 3: UI-Specific'. HELP_SYSTEM_COMPLETION.md reverses this: 'Tier 1: UI-Specific Documentation (📘)', 'Tier 2: MBASIC Implementation (📗)', 'Tier 3: BASIC-80 Language Reference (📕)'.

---

### status_inconsistency

**Description:** Migration status conflicts with reorganization plan

**Affected files:**
- `dev/HELP_MIGRATION_STATUS.md`
- `dev/HELP_REORGANIZATION_EXAMPLE.md`

**Details:**
HELP_MIGRATION_STATUS.md (dated 2025-10-25) states 'Status: Core migration complete, ready for use' and marks content as production-ready. HELP_REORGANIZATION_EXAMPLE.md describes a major reorganization that needs to happen, including moving files and deleting duplicates, suggesting the migration is not actually complete.

---

### file_deletion_inconsistency

**Description:** Files marked for deletion may still exist in final structure

**Affected files:**
- `dev/HELP_REORGANIZATION_EXAMPLE.md`
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_REORGANIZATION_EXAMPLE.md lists files to delete: 'docs/help/common/editor-commands.md', 'docs/help/common/shortcuts.md', 'docs/help/common/language.md', 'docs/help/common/index.md'. HELP_SYSTEM_COMPLETION.md doesn't mention these deletions and shows 'docs/help/common/language/' still exists, suggesting deletions weren't completed.

---

### search_index_location_inconsistency

**Description:** Search index file locations don't match directory structure

**Affected files:**
- `dev/HELP_REORGANIZATION_EXAMPLE.md`
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_SYSTEM_COMPLETION.md lists 'Language Index (docs/help/common/language/search_index.json)' but HELP_REORGANIZATION_EXAMPLE.md shows language files should be at 'docs/help/language/' (without 'common'), which would make the index path 'docs/help/language/search_index.json'.

---

### ui_backend_naming_inconsistency

**Description:** Inconsistent naming and listing of UI backends

**Affected files:**
- `dev/HELP_SYSTEM_DIAGRAM.md`
- `dev/HELP_SYSTEM_REORGANIZATION.md`
- `dev/HELP_SYSTEM_WEB_DEPLOYMENT.md`

**Details:**
HELP_SYSTEM_DIAGRAM.md shows three UIs in the architecture diagram: 'CLI UI', 'Curses UI', and 'Tk UI'. HELP_SYSTEM_REORGANIZATION.md mentions four backends: 'cli, curses, tk, visual' in the directory structure section ('docs/help/ui/{backend}/') and includes 'docs/help/ui/visual/' in the Tier 3 structure. HELP_SYSTEM_WEB_DEPLOYMENT.md's MkDocs configuration only lists three: 'CLI Interface', 'Curses (Terminal)', and 'Tkinter (GUI)', with no mention of 'visual'.

---

### implementation_status_inconsistency

**Description:** Conflicting representation of implementation status

**Affected files:**
- `dev/HELP_SYSTEM_DIAGRAM.md`
- `dev/HELP_SYSTEM_REORGANIZATION.md`

**Details:**
HELP_SYSTEM_DIAGRAM.md presents the three-tier structure as implemented and operational, with detailed pseudocode showing 'class HelpWidget' with multi-context support already in place. HELP_SYSTEM_REORGANIZATION.md treats this as a future proposal, stating 'Current: help_widget = HelpWidget(str(help_root), "ui/curses/index.md")' vs 'Proposed: help_widget = HelpWidget(ui_docs=..., mbasic_docs=..., language_docs=...)' and includes a 'Migration Plan' with phases, suggesting this is not yet implemented.

---

### content_location_inconsistency

**Description:** Conflicting information about NOT_IMPLEMENTED.md location

**Affected files:**
- `dev/HELP_SYSTEM_REORGANIZATION.md`
- `dev/HELP_SYSTEM_WEB_DEPLOYMENT.md`

**Details:**
HELP_SYSTEM_REORGANIZATION.md states in Phase 4: 'Move NOT_IMPLEMENTED.md to mbasic/not-implemented.md', suggesting it currently exists elsewhere. However, the Tier 2 structure shows 'not-implemented.md' as a file to be created ('touch docs/help/mbasic/not-implemented.md'). HELP_SYSTEM_WEB_DEPLOYMENT.md's MkDocs nav includes 'Not Implemented: docs/help/mbasic/not-implemented.md' as if it already exists in that location.

---

### feature_scope_ambiguity

**Description:** Unclear whether INDENT command should be available in immediate mode

**Affected files:**
- `dev/IMMEDIATE_MODE_DESIGN.md`
- `dev/INDENT_COMMAND_DESIGN.md`

**Details:**
IMMEDIATE_MODE_DESIGN.md states that immediate mode can execute 'any statement' including 'LIST' command, and mentions 'Immediate LIST Command' as an edge case. INDENT_COMMAND_DESIGN.md describes INDENT as a command that modifies program structure. It's unclear whether INDENT should be executable from immediate mode, and if so, whether it would be safe given the state restrictions outlined in IMMEDIATE_MODE_SAFETY.md.

---

### date_inconsistency

**Description:** Created date is listed as 2025-10-30, which is in the future

**Affected files:**
- `dev/INSTALLATION_TESTING_TODO.md`

**Details:**
Document states 'Created: 2025-10-30' but this appears to be a typo - should likely be 2024-10-30

---

### date_inconsistency

**Description:** Last Updated date is listed as 2025-10-31, which is in the future

**Affected files:**
- `dev/INTERACTIVE_COMMAND_TEST_COVERAGE.md`

**Details:**
Document states 'Last Updated: 2025-10-31' but this appears to be a typo - should likely be 2024-10-31

---

### contradictory_information

**Description:** Conflicting information about DEFINT/DEFSTR/DEFDBL implementation status

**Affected files:**
- `dev/LIBRARY_TEST_RESULTS.md`
- `dev/LANGUAGE_TESTING_PROGRESS_2025_10_30.md`

**Details:**
LIBRARY_TEST_RESULTS.md (dated 2025-10-30) states 'DEFINT/DEFSTR/DEFDBL Not Implemented' as a 'Critical Finding' affecting 23 programs. However, LANGUAGE_TESTING_PROGRESS_2025_10_30.md (same date) lists 'DEFINT/DEFSNG/DEFDBL/DEFSTR' under 'Now Tested (after today)' with '✅' and includes 'test_deftypes.bas' that tests these features. The document also states 'Initial TODO said DEFINT was broken' but 'Tests show it works'.

---

### date_inconsistency

**Description:** Feature implementation and removal within 7 days

**Affected files:**
- `dev/KEYWORD_IDENTIFIER_SPLITTING.md`
- `dev/LEXER_CLEANUP_COMPLETE.md`

**Details:**
KEYWORD_IDENTIFIER_SPLITTING.md is dated 2025-10-22 and describes a successful implementation. LEXER_CLEANUP_COMPLETE.md is dated 2025-10-29 (7 days later) and removes the same feature. This rapid reversal suggests either the feature was problematic or the initial assessment was incorrect, but no explanation for the reversal is provided in the cleanup document.

---

### contradictory_information

**Description:** Conflicting information about fixed BASIC programs

**Affected files:**
- `dev/LEXER_CLEANUP_COMPLETE.md`
- `dev/KEYWORD_IDENTIFIER_SPLITTING.md`

**Details:**
LEXER_CLEANUP_COMPLETE.md states it 'Fixed manually' issues in 'finance.bas' and 'lifscore.bas' by adding spaces (e.g., 'IFP=0' → 'IF P=0'). However, KEYWORD_IDENTIFIER_SPLITTING.md lists these same files as 'New Successfully Parsed Files' that work because of the keyword splitting feature, implying they didn't need manual fixes.

---

### feature_naming_inconsistency

**Description:** Two different features both use 'MID' in their titles, potentially causing confusion

**Affected files:**
- `dev/MID_STATEMENT_COMMENTS_FIX.md`
- `dev/MID_STATEMENT_FIX.md`

**Details:**
MID_STATEMENT_COMMENTS_FIX.md discusses mid-statement comments (apostrophe comments after statements), while MID_STATEMENT_FIX.md discusses MID$ statement (substring assignment). These are completely different features but have similar file names.

---

### implementation_order_inconsistency

**Description:** Unclear which feature was implemented first, but success rates suggest conflicting timelines

**Affected files:**
- `dev/MID_STATEMENT_COMMENTS_FIX.md`
- `dev/MID_STATEMENT_FIX.md`

**Details:**
Both documents claim implementation on 2025-10-22 (likely 2024-10-22). MID_STATEMENT_COMMENTS_FIX.md shows progression from 20.9% to 22.6%, while MID_STATEMENT_FIX.md reports 32.3% success rate. If both were implemented on the same date, the timeline and cumulative effects are unclear.

---

### missing_ui_backend

**Description:** NiceGUI web UI mentioned in one document but not in dependency strategy

**Affected files:**
- `dev/OPTIONAL_DEPENDENCIES_STRATEGY.md`
- `dev/PACKAGE_DEPENDENCIES.md`

**Details:**
PACKAGE_DEPENDENCIES.md lists 'nicegui (Web)' as an optional UI, but OPTIONAL_DEPENDENCIES_STRATEGY.md only discusses cli, curses, and tk backends. The pyproject.toml example in OPTIONAL_DEPENDENCIES_STRATEGY.md doesn't include nicegui as an optional dependency.

---

### version_mismatch

**Description:** Inconsistent version numbers for PC implementation completion

**Affected files:**
- `dev/PC_CLEANUP_REMAINING.md`
- `dev/PC_IMPLEMENTATION_STATUS.md`
- `dev/PC_REFACTORING_COMPLETE.md`

**Details:**
PC_CLEANUP_REMAINING.md states 'Status: Mostly Complete (v1.0.293)' and lists work completed in v1.0.291-293. PC_IMPLEMENTATION_STATUS.md shows phases completed in v1.0.276-278 with Phase 5 pending. PC_REFACTORING_COMPLETE.md states 'Fully complete including cleanup (v1.0.276 - v1.0.286)' and shows Phase 5 completed in v1.0.286. These version ranges don't align.

---

### version_mismatch

**Description:** Different example version numbers used

**Affected files:**
- `dev/PUBLISHING_TO_PYPI_GUIDE.md`
- `dev/PYPI_PUBLISHING_CHECKLIST.md`

**Details:**
PUBLISHING_TO_PYPI_GUIDE.md uses version '1.0.115' throughout examples. PYPI_PUBLISHING_CHECKLIST.md uses '1.0.119' in Step 1 checks and '1.0.120' in the 'Updating for New Release' section. While these are just examples, the inconsistency could cause confusion.

---

### contradictory_information

**Description:** Phase 5 status conflict

**Affected files:**
- `dev/PC_IMPLEMENTATION_STATUS.md`
- `dev/PC_REFACTORING_COMPLETE.md`

**Details:**
PC_IMPLEMENTATION_STATUS.md shows 'Phase 5: Cleanup (PENDING)' with unchecked items. PC_REFACTORING_COMPLETE.md shows 'Phase 5: State Field Cleanup (v1.0.286) ✅' as completed with all items checked.

---

### outdated_information

**Description:** Document appears outdated compared to completion document

**Affected files:**
- `dev/PC_IMPLEMENTATION_STATUS.md`

**Details:**
PC_IMPLEMENTATION_STATUS.md ends with 'Next Steps: 1. Start Phase 2: Refactor tick() loop to use PC' but PC_REFACTORING_COMPLETE.md shows all phases including Phase 5 are complete. The status document appears to be from an earlier point in development and hasn't been updated.

---

### test_count_inconsistency

**Description:** Inconsistent test counts in summary statistics

**Affected files:**
- `dev/README_TESTS_INVENTORY.md`

**Details:**
The document states '**Total: 27 automated regression tests**' in one section, but the summary table shows '**27**' Python tests and '**102**' BASIC tests for a total of '**129**'. However, the breakdown shows 38 self-checking BASIC tests + 64 BASIC test programs = 102 BASIC tests, which is correct. But earlier it says 'Total: 38 self-checking BASIC tests' separately from the 64 programs, suggesting these should be counted distinctly.

---

### date_inconsistency

**Description:** Two different sessions claim the same date with different work

**Affected files:**
- `dev/SESSION_2025_10_26.md`
- `dev/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md`

**Details:**
SESSION_2025_10_26.md is dated 'October 26, 2025' and focuses on 'Command Consolidation' and 'Parser Improvement'. SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md is dated '2025-10-26' and focuses on 'Web UI Feature Parity & Statement Highlighting'. These appear to be completely different sessions with different accomplishments but claim the same date.

---

### test_coverage_inconsistency

**Description:** Test file counts don't align between sessions on same date

**Affected files:**
- `dev/SESSION_2025_10_26.md`
- `dev/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md`

**Details:**
SESSION_2025_10_26.md states 'Test Files with Results' increased from 3 to 7 (+133%) with 4 new tests added. SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md (same date) mentions creating 4 test programs in 'basic/bas_tests/' directory but doesn't reference the earlier test count or acknowledge the previous session's test additions.

---

### settings_command_naming_inconsistency

**Description:** Settings CLI command names differ between implementation and gap analysis

**Affected files:**
- `dev/SESSION_2025_10_28_SUMMARY.md`
- `dev/SETTINGS_FEATURE_GAP_ANALYSIS.md`

**Details:**
SESSION_2025_10_28_SUMMARY.md documents CLI commands as 'SET "setting.name" value' and 'SHOW SETTINGS ["pattern"]'. SETTINGS_FEATURE_GAP_ANALYSIS.md searches for 'SETSETTING' and 'SHOWSETTINGS' commands (single words) and proposes CLI commands as 'SETSETTING key value' and 'SHOWSETTINGS [filter]'. The command naming convention is inconsistent.

---

### missing_cross_reference

**Description:** STATUS.md references LANGUAGE_TESTING_TODO.md but TEST_COVERAGE_MATRIX.md references LANGUAGE_TESTING_DONE.md - unclear which document is current

**Affected files:**
- `dev/STATUS.md`
- `dev/TEST_COVERAGE_MATRIX.md`

**Details:**
STATUS.md under 'Placeholder' section states: 'See: docs/dev/LANGUAGE_TESTING_TODO.md - Current testing TODO items'. However, TEST_COVERAGE_MATRIX.md under 'See Also' references: 'Testing completion: docs/history/LANGUAGE_TESTING_DONE.md'. This suggests testing may be complete, contradicting the TODO reference.

---

### feature_implementation_status

**Description:** Conflicting information about RANDOMIZE implementation status

**Affected files:**
- `dev/STATUS.md`
- `dev/TEST_COVERAGE_MATRIX.md`

**Details:**
STATUS.md does not list RANDOMIZE anywhere in implemented or unimplemented sections. TEST_COVERAGE_MATRIX.md lists 'RANDOMIZE - RNG seeding statement (parsed, not executed - may not be in MBASIC 5.21, use PEEK(0) instead)' under 'Features Not Yet Implemented'. This creates ambiguity about whether RANDOMIZE is parsed at all.

---

### feature_implementation_status

**Description:** EQV and IMP operators listed differently across documents

**Affected files:**
- `dev/STATUS.md`
- `dev/TEST_COVERAGE_MATRIX.md`

**Details:**
STATUS.md does not mention EQV or IMP operators anywhere. TEST_COVERAGE_MATRIX.md lists them under 'Features Not Yet Implemented' with note '(parsed, not executed - may not be in MBASIC 5.21)'. This inconsistency leaves unclear whether these operators are part of the MBASIC 5.21 specification being implemented.

---

### test_count_mismatch

**Description:** Total test count differs between inventory and test run results

**Affected files:**
- `dev/TEST_INVENTORY.md`
- `dev/TEST_RUN_RESULTS_2025-11-02.md`

**Details:**
TEST_INVENTORY.md claims '**Total:** 35 test files identified' but TEST_RUN_RESULTS_2025-11-02.md shows '**Total Tests:** 27 regression tests'. The inventory lists 36 numbered items (not 35), and the test runner only found 27.

---

### file_location_inconsistency

**Description:** Test file locations don't match between inventory plan and actual test results

**Affected files:**
- `dev/TEST_INVENTORY.md`
- `dev/TEST_RUN_RESULTS_2025-11-02.md`

**Details:**
TEST_INVENTORY.md proposes moving tests to 'tests/regression/' subdirectories, but TEST_RUN_RESULTS_2025-11-02.md shows tests already in 'regression/' subdirectories (e.g., 'regression/help/test_help_search_ranking.py' not 'tests/regression/help/test_help_search_ranking.py')

---

### test_categorization_mismatch

**Description:** Categorization summary counts don't match detailed listings

**Affected files:**
- `dev/TEST_INVENTORY.md`

**Details:**
Categorization Summary claims '**Definitely Keep as Regression Tests (25)**' but detailed listings show different numbers: 10 root Python tests + 22 utils tests = 32 potential regression tests, not 25

---

### missing_test_file

**Description:** Test file mentioned in inventory but not in test run results

**Affected files:**
- `dev/TEST_INVENTORY.md`
- `dev/TEST_RUN_RESULTS_2025-11-02.md`

**Details:**
TEST_INVENTORY.md lists 'utils/test_curses_comprehensive.py' as 'IMPORTANT - Main curses test runner' but it does not appear in the 27 tests run in TEST_RUN_RESULTS_2025-11-02.md

---

### feature_availability_conflict

**Description:** Enhancement plan lists keyboard shortcuts as missing that audit shows are implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN says 'Missing: Ctrl+R, Ctrl+T, Ctrl+G, Ctrl+X, Ctrl+B, Ctrl+W, Ctrl+K, Ctrl+D, Ctrl+E, Ctrl+A, Ctrl+U'. AUDIT section 12 shows implemented: Ctrl+R (Run Program), Ctrl+X (Cut), Ctrl+B (Toggle Breakpoint), Ctrl+W (Variables Window), Ctrl+K (Execution Stack), Ctrl+I (Insert Line).

---

### feature_availability_conflict

**Description:** Enhancement plan lists statement highlighting as missing but audit shows it's implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN lists '❌ Statement highlighting (cyan background for active statement)' as missing. AUDIT section 4.4 'Statement Highlighting' describes full implementation with yellow background (#ffeb3b) for active statements.

---

### feature_availability_conflict

**Description:** Enhancement plan lists automatic line sorting as missing but audit shows it's implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN lists '❌ Automatic line sorting' as missing. AUDIT section 3.5 'Auto-Sort on Navigation' describes full implementation with triggers on arrow keys, page up/down, mouse click, and focus out.

---

### feature_availability_conflict

**Description:** Enhancement plan lists auto-numbering as missing but audit shows it's implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN lists '❌ Auto-numbering with calculator-style digit entry' as missing. AUDIT section 3.3 'Auto-Numbering System' describes full implementation with configurable start/increment and intelligent line number calculation.

---

### feature_availability_conflict

**Description:** Enhancement plan lists syntax error detection as missing but audit shows it's implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN lists '❌ Syntax error detection with ? markers' as missing. AUDIT section 3.6 'Syntax Validation' describes real-time validation with red ? indicators on error lines.

---

### feature_availability_conflict

**Description:** Enhancement plan lists help dialog as missing but audit shows it's implemented

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN lists '❌ Help dialog (Ctrl+A)' as missing. AUDIT section 11 'Help System' describes comprehensive help browser with search, navigation, and in-page search (Ctrl+F). Section 12.1 shows Ctrl+H (not Ctrl+A) is the default for Help Topics.

---

### completion_percentage_conflict

**Description:** Different completion percentages for Web UI

**Affected files:**
- `dev/UI_FEATURE_PARITY_CHECKLIST.md`
- `dev/UI_FEATURE_PARITY.md`

**Details:**
UI_FEATURE_PARITY_CHECKLIST.md states 'Web UI: 98% Feature Complete ⬆️ (was 97%)', but UI_FEATURE_PARITY.md does not provide a percentage and the feature table shows several missing features (Save As, Recent Files, Auto-Save, etc.)

---

### feature_status_conflict

**Description:** Conflicting information about Recent Files in Web UI

**Affected files:**
- `dev/UI_FEATURE_PARITY_CHECKLIST.md`
- `dev/UI_FEATURE_PARITY.md`

**Details:**
UI_FEATURE_PARITY_CHECKLIST.md states 'Recent files | ✅ | ✅ | ✅ | COMPLETE 2025-10-27 - Shared recent_files.py, shows last 10 files' for all UIs, but UI_FEATURE_PARITY.md shows 'Recent Files | ❌ | ❌ | ✅ File menu | ⚠️ Browser storage | ❌' indicating CLI and Curses don't have it

---

### feature_status_conflict

**Description:** Conflicting information about Variable Search/Filter

**Affected files:**
- `dev/UI_FEATURE_PARITY_CHECKLIST.md`
- `dev/UI_FEATURE_PARITY.md`

**Details:**
UI_FEATURE_PARITY_CHECKLIST.md states 'Search/filter variables | ✅ | ✅ | ✅ | COMPLETE 2025-10-27 - Real-time filter on name, value, type' for all UIs, but UI_FEATURE_PARITY.md shows 'Variable Filtering | ❌ | ✅ Ctrl+F in vars | ✅ Search box | ✅ Search | ❌' indicating CLI and Visual don't have it

---

### feature_status_conflict

**Description:** Conflicting information about Save functionality in CLI

**Affected files:**
- `dev/UI_FEATURE_PARITY.md`
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
UI_FEATURE_PARITY.md shows 'Save File | ✅ SAVE' for CLI, but UI_FEATURE_PARITY_TRACKING.md shows 'Save File | [❌|❓|⚡]' for CLI with note 'CLI missing (only has Save As)' and later states 'Save (without prompt) | CLI only | File management (has Save As only)'

---

### feature_status_conflict

**Description:** Conflicting information about Smart Insert Line in Web UI

**Affected files:**
- `dev/UI_FEATURE_PARITY_CHECKLIST.md`
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
UI_FEATURE_PARITY_CHECKLIST.md states 'Smart Insert Line (Ctrl+I) | ✅ | ✅ | Menu | COMPLETE 2025-10-26 - Tk/Curses use Ctrl+I, Web uses Edit menu', but UI_FEATURE_PARITY_TRACKING.md shows 'Smart Insert | [❌|❓|⚡]' for Web UI

---

### test_coverage_conflict

**Description:** Contradictory test coverage information for CLI

**Affected files:**
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
The 'Testing Infrastructure Status' table shows 'CLI | Subprocess + test suite | test_all_ui_features.py | 100% | [✅|📝|🧪] Full coverage 2025-10-29', but the 'Testing Priorities' table shows 'CLI | 80% | 90% | Already well-tested, add UI-specific tests', and later notes 'CLI actually well-tested ~80%'

---

### feature_status_inconsistency

**Description:** Contradictory implementation status for Curses UI variable editing

**Affected files:**
- `dev/VARIABLE_EDITING_FEATURE.md`
- `dev/VARIABLE_EDITING_STATUS.md`

**Details:**
VARIABLE_EDITING_FEATURE.md states '✅ Curses UI: Key binding (Enter/'e') (commit fcedd97)' and '✅ Curses UI: Edit prompt (commit fcedd97)' marking it as complete. However, VARIABLE_EDITING_STATUS.md describes it as '✅ COMPLETE' with full implementation details at 'src/ui/curses_ui.py:2520-2647'. Meanwhile, VARIABLE_EDITING_STANDARDIZATION.md lists Curses as '⚠️ Partial implementation' under 'Current Implementation Status'.

---

### feature_status_inconsistency

**Description:** Contradictory status information about implementation completion

**Affected files:**
- `dev/VISUAL_UI_EDITOR_ENHANCEMENT.md`

**Details:**
The document header states 'Status: PARTIAL IMPLEMENTATION' and lists '✅ Auto-numbering on Enter (src/ui/tk_ui.py:1305)' as done, but later in 'Current Issues' section #5 states 'Auto-Numbering Not Working (Tk/Web)' with 'Tk/Web behavior: Not implemented or broken'. This creates confusion about whether auto-numbering is actually implemented or not.

---

### task_tracking_inconsistency

**Description:** Task completion status conflicts with implementation status

**Affected files:**
- `dev/VISUAL_UI_EDITOR_ENHANCEMENT.md`

**Details:**
The 'What's Been Done' section marks several features as complete (✅), but the 'Task Tracking' section under 'Implementation Plan' marks all Phase 1 and Phase 2 tasks as '⬜ Not Started'. For example, 'Auto-numbering on Enter' is marked done at the top but task '1.3 Implement auto-numbering on Enter key' is marked not started.

---

### version_number_mismatch

**Description:** Version numbers are inconsistent across documents from similar timeframes

**Affected files:**
- `dev/WEB_UI_FEATURE_PARITY.md`
- `dev/WEB_UI_FIXES_2025_10_30.md`

**Details:**
WEB_UI_FEATURE_PARITY.md states 'Version: 1.0.203' and mentions features implemented across 'versions 1.0.194-1.0.202', but WEB_UI_FIXES_2025_10_30.md (dated same day) makes no mention of version numbers for the fixes

---

### auto_numbering_implementation_conflict

**Description:** Auto-numbering is listed as complete feature but also listed as having critical bugs that needed fixing

**Affected files:**
- `dev/WEB_UI_FEATURE_PARITY.md`
- `dev/WEB_UI_FIXES_2025_10_30.md`

**Details:**
WEB_UI_FEATURE_PARITY.md lists 'Auto-numbering (v1.0.199)' as '✅ COMPLETE' under Editor Features, but WEB_UI_FIXES_2025_10_30.md lists '✅ Auto-Numbering JavaScript Timeout (HIGH)' as a bug that was fixed, indicating the feature was broken

---

### timeline_inconsistency

**Description:** Implementation timeline estimates conflict with actual implementation dates

**Affected files:**
- `dev/WEB_UI_IMPLEMENTATION.md`
- `dev/WEB_UI_FEATURE_PARITY.md`

**Details:**
WEB_UI_IMPLEMENTATION.md (dated 2025-10-25) estimates 'Total: 3 days to working IDE' with 'Day 1: Basic UI + I/O (✅ Done)' and 'Current Status: Day 1 complete', but WEB_UI_FEATURE_PARITY.md (dated 2025-10-28) shows features implemented across multiple versions (1.0.194-1.0.202) suggesting a longer timeline

---

### editor_implementation_conflict

**Description:** Different descriptions of editor implementation approach

**Affected files:**
- `dev/WEB_UI_EDITOR_ENHANCEMENTS.md`
- `dev/WEB_UI_IMPLEMENTATION.md`

**Details:**
WEB_UI_EDITOR_ENHANCEMENTS.md states 'The Web UI uses NiceGUI's textarea (Quasar q-textarea)' and discusses limitations, while WEB_UI_IMPLEMENTATION.md states 'Textarea for BASIC code (will upgrade to Monaco/CodeMirror)' and later 'Upgrade editor to Monaco or nicegui-codemirror' as a Phase 1 task

---

### implementation_status_conflict

**Description:** WEB_UI_REAL_OPTIONS.md describes web UI as future work with 3-5 day estimates, but WORK_IN_PROGRESS.md shows web UI already implemented with specific version numbers and bug fixes

**Affected files:**
- `dev/WEB_UI_REAL_OPTIONS.md`
- `dev/WORK_IN_PROGRESS.md`

**Details:**
WEB_UI_REAL_OPTIONS.md: 'Total: 3 days to working IDE' and 'Timeline: Prototype: 1 day, MVP: 3 days' vs WORK_IN_PROGRESS.md: 'src/ui/web/nicegui_backend.py' already exists with version 1.0.385-1.0.392 fixes

---

### feature_availability_conflict

**Description:** WEB_UI_REAL_OPTIONS.md describes web UI features as planned/proposed, but WEB_UI_TESTING_CHECKLIST.md indicates features are implemented but need testing

**Affected files:**
- `dev/WEB_UI_REAL_OPTIONS.md`
- `dev/WEB_UI_TESTING_CHECKLIST.md`

**Details:**
WEB_UI_REAL_OPTIONS.md: 'Phase 1: Basic IDE (Day 1)' with example code vs WEB_UI_TESTING_CHECKLIST.md: '**Implemented:** Version 1.0.300' and 'Web UI menus are currently in development'

---

### completion_status_conflict

**Description:** Document shows both 'Status: COMPLETE ✅' and 'Next Steps' section with remaining work

**Affected files:**
- `dev/WORK_IN_PROGRESS.md`

**Details:**
WORK_IN_PROGRESS.md: '## Status: COMPLETE ✅' but also '## Next Steps: Remove remaining interactive_mode references (LOAD, SAVE, RUN filename, CHAIN, SYSTEM, MERGE, CONT)'

---

### contradictory_information

**Description:** Conflicting recommendations about breakpoint feature status

**Affected files:**
- `dev/archive/BREAKPOINT_ISSUE_EXPLAINED.md`
- `dev/archive/CONTINUE_IMPLEMENTATION.md`

**Details:**
BREAKPOINT_ISSUE_EXPLAINED.md recommends 'For a working debugger, I suggest: 1. **Remove breakpoint UI from curses IDE** - it's fundamentally broken' and apologizes for 'wasting your time debugging something that was fundamentally flawed'. However, CONTINUE_IMPLEMENTATION.md concludes 'The continue feature is **complete and functional**' and provides comprehensive documentation as if it's a finished, working feature.

---

### contradictory_information

**Description:** Conflicting testing status claims

**Affected files:**
- `dev/archive/BREAKPOINT_STATUS.md`
- `dev/archive/BREAKPOINT_ISSUE_EXPLAINED.md`

**Details:**
BREAKPOINT_STATUS.md states under 'What I've Tested': '✅ **Interpreter step execution** - Fully tested with `test_breakpoint_final.py`' and claims the implementation is 'Code Complete'. However, BREAKPOINT_ISSUE_EXPLAINED.md states 'I've **disabled the broken breakpoint pause UI**' and 'The program will run without crashing, but breakpoints won't actually pause execution'.

---

### outdated_information

**Description:** Debug documentation references features that may have been removed or changed

**Affected files:**
- `dev/archive/BREAKPOINT_NOT_STOPPING_DEBUG.md`
- `dev/archive/CONTINUE_IMPLEMENTATION.md`

**Details:**
BREAKPOINT_NOT_STOPPING_DEBUG.md provides extensive debugging steps for 'Breakpoints are not stopping program execution', but if BREAKPOINT_ISSUE_EXPLAINED.md is correct that the feature was disabled, this debug guide would be obsolete. Conversely, if CONTINUE_IMPLEMENTATION.md is correct that it's working, the debug guide is unnecessary.

---

### version_mismatch

**Description:** Version number inconsistency within the same document

**Affected files:**
- `future/DISTRIBUTION_TESTING.md`

**Details:**
The document header states 'Version: 1.0.147' but later in the Version Management section shows 'Current: 1.0.147' with description 'Patch: 147 (development increments)'. However, the version numbering scheme explanation suggests this should be a more stable release number for PyPI publication, not a development increment.

---

### feature_status

**Description:** Conflicting information about curses UI implementation

**Affected files:**
- `dev/archive/IMPLEMENTATION_SUMMARY.md`
- `dev/archive/MENU_CHANGES.md`

**Details:**
IMPLEMENTATION_SUMMARY.md (appears to be about urwid migration) states many features 'Not Yet Implemented' in urwid UI, while MENU_CHANGES.md discusses menu structure changes in 'src/ui/curses_ui.py' as if fully implemented. Unclear if MENU_CHANGES refers to npyscreen or urwid implementation.

---

### version_mismatch

**Description:** Different version numbers mentioned for the package

**Affected files:**
- `future/PYPI_DISTRIBUTION.md`
- `future/SIMPLE_DISTRIBUTION_APPROACH.md`

**Details:**
PYPI_DISTRIBUTION.md states 'Version: 1.0.151' and 'Version Ready: 1.0.151', while SIMPLE_DISTRIBUTION_APPROACH.md mentions 'version = "1.0.112"' in the pyproject.toml example. These should be consistent or the discrepancy should be explained.

---

### feature_availability

**Description:** Debugging features documented but not mentioned in basic editor commands

**Affected files:**
- `help/common/debugging.md`
- `help/common/editor-commands.md`

**Details:**
debugging.md extensively documents breakpoints, stepping, and debug windows with shortcuts like 'Ctrl+B', 'Ctrl+V', 'Ctrl+K', but editor-commands.md doesn't mention any debugging commands in its 'Program Commands' or 'Editing Commands' sections. This omission may confuse users about available features.

---

### inconsistent_function_naming

**Description:** Double precision conversion function has two different names

**Affected files:**
- `help/common/language/functions/cobl.md`
- `help/common/language/functions/cdbl.md`

**Details:**
cobl.md documents 'COBL(X)' as converting to double precision, while cdbl.md documents 'CDBL(X)' for the same purpose. Both claim to be in Extended and Disk versions.

---

### broken_cross_reference

**Description:** CINT See Also section references non-existent CSNG function

**Affected files:**
- `help/common/language/functions/cint.md`

**Details:**
cint.md references 'CSNG' in See Also but links to 'csng.md', which exists. However, the link format appears correct.

---

### inconsistent_cross_references

**Description:** Related functions reference each other inconsistently

**Affected files:**
- `help/common/language/functions/cobl.md`
- `help/common/language/functions/crr_dollar.md`
- `help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
cobl.md, crr_dollar.md, and cvi-cvs-cvd.md all have identical 'See Also' sections referencing the same set of functions, but this set includes 'COBL' and 'CRR$' which appear to be duplicates of 'CDBL' and 'CHR$'.

---

### broken_cross_reference

**Description:** Error codes document references non-existent ERR and ERL page

**Affected files:**
- `help/common/language/appendices/error-codes.md`

**Details:**
References '[ERR and ERL](../statements/err-erl-variables.md)' but the actual file referenced in other documents is 'err-erl-variables.md' which may not exist or be named differently.

---

### inconsistent_naming

**Description:** Two different files exist for SPACE$ function with different filenames

**Affected files:**
- `help/common/language/functions/index.md`
- `help/common/language/functions/space_dollar.md`
- `help/common/language/functions/spaces.md`

**Details:**
Both 'space_dollar.md' and 'spaces.md' document the SPACE$ function. The index.md references 'spaces.md' but most other files reference 'space_dollar.md'. This creates ambiguity about which is the canonical file.

---

### inconsistent_cross_references

**Description:** String function See Also sections inconsistently reference SPACE$ vs SPACES

**Affected files:**
- `help/common/language/functions/hex_dollar.md`
- `help/common/language/functions/instr.md`
- `help/common/language/functions/left_dollar.md`
- `help/common/language/functions/len.md`
- `help/common/language/functions/mid_dollar.md`
- `help/common/language/functions/oct_dollar.md`
- `help/common/language/functions/right_dollar.md`
- `help/common/language/functions/space_dollar.md`

**Details:**
Most string functions reference '[SPACE$](space_dollar.md)' but the index references '[SPACE$](spaces.md)'. This creates inconsistent navigation paths.

---

### missing_syntax_section

**Description:** STRING$ function documentation is missing a Syntax section that other function documents have

**Affected files:**
- `help/common/language/functions/string_dollar.md`

**Details:**
Most function docs (spc.md, sqr.md, str_dollar.md, tab.md, tan.md, usr.md, val.md, varptr.md) include a '## Syntax' section with code block showing the function signature. string_dollar.md jumps directly from title to Description without a Syntax section.

---

### missing_description

**Description:** SGN function referenced in 'See Also' has placeholder description

**Affected files:**
- `help/common/language/functions/sqr.md`

**Details:**
In sqr.md 'See Also' section: '- [SGN](sgn.md) - NEEDS_DESCRIPTION' indicates incomplete documentation for the SGN function.

---

### missing_categorization

**Description:** TAB function has placeholder category

**Affected files:**
- `help/common/language/functions/tab.md`

**Details:**
tab.md frontmatter shows 'category: NEEDS_CATEGORIZATION' while other functions have proper categories like 'string', 'mathematical', 'system'.

---

### inconsistent_see_also_references

**Description:** TAB function 'See Also' section references unrelated commands instead of similar functions

**Affected files:**
- `help/common/language/functions/tab.md`

**Details:**
tab.md 'See Also' section lists CLOAD, COBL, CRR$, CSAVE, CVI/CVS/CVD, DEFINT/SNG/DBL/STR, ERR AND ERL, INPUT#, LINE INPUT, LPRINT, MKI$/MKS$/MKD$, SPACES - these appear to be from a different context (possibly file I/O or type conversion) rather than output formatting functions like PRINT, SPC, POS which would be more relevant.

---

### missing_syntax_section

**Description:** CLOAD and CSAVE statements missing Syntax sections

**Affected files:**
- `help/common/language/statements/cload.md`
- `help/common/language/statements/csave.md`

**Details:**
Both cload.md and csave.md jump directly to Purpose without a Syntax section, while other statement documents (auto.md, call.md, chain.md, clear.md, close.md, cls.md, common.md, cont.md, data.md) include explicit Syntax sections.

---

### missing_cross_references

**Description:** DEF FN does not reference DEFINT/SNG/DBL/STR in 'See Also' section despite discussing type suffixes

**Affected files:**
- `help/common/language/statements/def-fn.md`
- `help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
DEF FN extensively discusses type suffixes (%, $, etc.) and type specification in function names, but does not link to DEFINT/SNG/DBL/STR which defines default variable types. DEFINT/SNG/DBL/STR also does not reference DEF FN despite both dealing with variable typing.

---

### version_information_inconsistency

**Description:** Inconsistent version notation format

**Affected files:**
- `help/common/language/statements/def-fn.md`
- `help/common/language/statements/end.md`
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/goto.md`

**Details:**
def-fn.md has no version information in the document body. end.md shows 'Versions: SK, Extended, Disk' in the body. for-next.md shows 'Versions: SK, Extended, Disk' in body. goto.md shows 'Versions: SK, Extended, Disk' in body. The frontmatter 'type: statement' is consistent, but version information placement is inconsistent.

---

### missing_information

**Description:** DIM and ERASE lack comprehensive examples compared to DEF FN

**Affected files:**
- `help/common/language/statements/dim.md`
- `help/common/language/statements/erase.md`

**Details:**
def-fn.md provides 8 detailed examples with explanations and output. dim.md provides only a minimal 4-line example fragment. erase.md provides only a 3-line example fragment. The level of documentation detail is inconsistent across similar statement types.

---

### contradictory_information

**Description:** END statement description conflicts with typical BASIC behavior

**Affected files:**
- `help/common/language/statements/end.md`

**Details:**
Document states 'BASIC-aO·always returns to command level after an END is executed' but also says 'An END statement at the end of a program is optional.' If END always returns to command level, it should not be optional - the program would need some way to terminate. This suggests either the 'always' statement is incorrect or the 'optional' statement needs clarification.

---

### inconsistent_syntax_format

**Description:** Inconsistent formatting in syntax sections - some use plain text descriptions within code blocks, others use proper markdown formatting

**Affected files:**
- `help/common/language/statements/let.md`
- `help/common/language/statements/line-input.md`
- `help/common/language/statements/lprint-lprint-using.md`
- `help/common/language/statements/mid_dollar.md`
- `help/common/language/statements/open.md`
- `help/common/language/statements/option-base.md`
- `help/common/language/statements/out.md`
- `help/common/language/statements/poke.md`
- `help/common/language/statements/printi-printi-using.md`

**Details:**
let.md shows '110 LET 0=12' with malformed examples. line-input.md uses '[i]' notation inconsistently. mid_dollar.md has '_where nand m are integer expressions' as plain text in code block. option-base.md has 'where n is 1 or 0' outside syntax block. out.md and poke.md have 'where I and J are...' descriptions in code blocks.

---

### missing_purpose_content

**Description:** OPTION BASE documentation has empty Purpose section

**Affected files:**
- `help/common/language/statements/option-base.md`

**Details:**
The Purpose section contains only '## See Also' with no actual purpose description, while all other files have descriptive purpose text.

---

### missing_remarks_content

**Description:** Several files have empty or incomplete Remarks sections

**Affected files:**
- `help/common/language/statements/list.md`
- `help/common/language/statements/new.md`
- `help/common/language/statements/print.md`
- `help/common/language/statements/printi-printi-using.md`

**Details:**
list.md, new.md, print.md, and printi-printi-using.md have '## Remarks' headers with no content or only partial content before jumping to examples.

---

### duplicate_content

**Description:** Two separate files document MID$ with overlapping but different content

**Affected files:**
- `help/common/language/statements/mid-assignment.md`
- `help/common/language/statements/mid_dollar.md`

**Details:**
mid-assignment.md is a modern, well-formatted document about MID$ assignment. mid_dollar.md appears to be legacy documentation for the same feature with different formatting and less detail. Both reference each other in See Also sections.

---

### inconsistent_see_also_references

**Description:** The 'See Also' sections for file I/O statements (PUT, RESET, RSET) all reference 'PRINTi AND PRINTi USING' with inconsistent formatting and link targets

**Affected files:**
- `help/common/language/statements/put.md`
- `help/common/language/statements/reset.md`
- `help/common/language/statements/rset.md`

**Details:**
All three files link to 'printi-printi-using.md' but use inconsistent display text: 'PRINTi AND PRINTi USING' vs the actual title format. The link format suggests 'PRINTi' but standard BASIC uses 'PRINT#' notation.

---

### inconsistent_see_also_references

**Description:** File I/O statements reference '~ INPUTi' with tilde prefix in See Also sections

**Affected files:**
- `help/common/language/statements/put.md`
- `help/common/language/statements/reset.md`
- `help/common/language/statements/rset.md`

**Details:**
The link text '~ INPUTi' appears with a tilde prefix and links to 'inputi.md', which is inconsistent with standard BASIC notation 'INPUT#'. The tilde appears to be a formatting artifact.

---

### missing_reference

**Description:** WIDTH statement documentation references WRITE statement in See Also section, but links to write.md which documents terminal output WRITE, not the file I/O WRITE # statement

**Affected files:**
- `help/common/language/statements/width.md`
- `help/common/language/statements/write.md`

**Details:**
width.md does not link to writei.md (WRITE # for file I/O), only to write.md (terminal WRITE). The See Also section should likely reference writei.md since WIDTH LPRINT relates to printer/file output width.

---

### path_inconsistency

**Description:** Inconsistent relative path references to common documentation

**Affected files:**
- `help/common/ui/curses/editing.md`
- `help/common/ui/tk/index.md`

**Details:**
curses/editing.md uses paths like '../../language/statements/renum.md' while tk/index.md uses 'common/language/statements/index.md' and 'common/examples/hello-world.md'. The path structure suggests tk/index.md paths are incorrect (missing '../..' prefix).

---

### inconsistent_information

**Description:** WIDTH statement documentation has conflicting implementation status

**Affected files:**
- `help/common/language/statements/width.md`

**Details:**
The Implementation Note says 'Limitations: The "WIDTH LPRINT" syntax is not supported (parse error)' but the Syntax section shows 'WIDTH LPRINT <integer expression>' as part of the original syntax. It's unclear if this is parsed and ignored or causes a parse error.

---

### missing_reference

**Description:** WIDTH statement See Also section includes unrelated functions

**Affected files:**
- `help/common/language/statements/width.md`

**Details:**
width.md See Also includes FRE, INKEY$, INP, PEEK, USR, VARPTR which have no apparent relationship to setting line width. These appear to be copied from another statement's documentation.

---

### contradictory_information

**Description:** Conflicting information about which debugging commands are available in which UI

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/extensions.md`

**Details:**
compatibility.md states 'BREAK, STEP, WATCH, STACK (CLI only)' under Modern Extensions. extensions.md also states 'IMPORTANT: These commands are exclusive to the CLI backend' for debugging commands. However, features.md under 'Debugging' lists these as 'UI-dependent' without specifying CLI-only.

---

### contradictory_information

**Description:** Conflicting information about WIDTH statement support

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/features.md`

**Details:**
compatibility.md states 'WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.' However, features.md does not mention WIDTH at all in the 'Input/Output' section or anywhere else, creating ambiguity about whether it's supported.

---

### missing_information

**Description:** Web UI installation and usage instructions missing

**Affected files:**
- `help/mbasic/getting-started.md`
- `help/mbasic/features.md`

**Details:**
getting-started.md provides installation and usage instructions for CLI, Curses, and Tk UIs, but does not mention how to start or use the Web UI that is referenced in compatibility.md and extensions.md.

---

### feature_availability_conflict

**Description:** STEP INTO/OVER commands documented differently across UIs

**Affected files:**
- `help/ui/cli/debugging.md`
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In cli/debugging.md: 'STEP INTO' and 'STEP OVER' are listed in syntax but marked as 'not yet implemented' in Limitations section. In curses docs, only 'Step Statement' (Ctrl+T) and 'Step Line' (Ctrl+L) are mentioned, with no reference to STEP INTO/OVER.

---

### keyboard_shortcut_conflict

**Description:** Different key bindings documented for Save command

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+S' or 'F5' for Save program. In quick-reference.md: Only 'Ctrl+S' (shown as {{kbd:save}}) is listed, no mention of F5.

---

### keyboard_shortcut_conflict

**Description:** Different key bindings documented for Run command

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+R' for Run program. In running.md: 'F2 or Ctrl+R' for running. In quick-reference.md: Only 'Ctrl+R' (shown as {{kbd:run}}) is listed.

---

### keyboard_shortcut_conflict

**Description:** Different key bindings documented for List command

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+L' for List program. In running.md: 'F3 or Ctrl+L' for listing. In quick-reference.md: Only 'Ctrl+L' is mentioned.

---

### keyboard_shortcut_conflict

**Description:** Different key bindings documented for Load/Open command

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+O' for Load program. In files.md: 'b or Ctrl+O' for loading. In quick-reference.md: Only 'Ctrl+O' is listed.

---

### feature_availability_conflict

**Description:** Conflicting information about stopping program execution

**Affected files:**
- `help/ui/curses/running.md`
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In running.md: 'Currently no way to interrupt running programs (use Ctrl+C to exit entirely)'. In keyboard-commands.md: 'Ctrl+Q' is listed as 'Stop execution'. In quick-reference.md: 'Ctrl+X' is listed as 'Stop execution (eXit)'.

---

### feature_availability_conflict

**Description:** Variables window key binding conflict

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/keyboard-commands.md`

**Details:**
In feature-reference.md: 'Ctrl+W' to open/close variables window. In keyboard-commands.md: 'Ctrl+V' for 'Open variables window (during execution)'. In quick-reference.md: 'Ctrl+W' for 'Toggle variables watch window'.

---

### feature_availability_conflict

**Description:** Step Line feature described differently

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/tk/feature-reference.md`

**Details:**
keyboard-shortcuts.md mentions 'Step Line: Would execute the entire line - Currently same as Step Statement (may change in future)', but feature-reference.md lists 'Step Line (F10)' as a separate feature with shortcut F10, while keyboard-shortcuts.md doesn't mention F10 for stepping.

---

### ui_comparison_inconsistency

**Description:** Variables window feature availability inconsistent

**Affected files:**
- `help/ui/index.md`
- `help/ui/curses/variables.md`

**Details:**
index.md comparison table shows Curses has Variables Window (✓), but curses/variables.md states 'Variable Editing (Limited)' with 'Cannot edit values directly in window' and lists it as 'Partial Implementation'. The comparison should reflect this limitation.

---

### settings_category_inconsistency

**Description:** Different settings categories between UIs

**Affected files:**
- `help/ui/curses/settings.md`
- `help/ui/tk/settings.md`

**Details:**
curses/settings.md lists categories: EDITOR, KEYWORDS, VARIABLES, INTERPRETER, UI. tk/settings.md lists tabs: Editor, Interpreter, Keywords, Variables, UI. While similar, the curses version uses all caps and different ordering, which may confuse users switching between UIs.

---

### feature_availability_conflict

**Description:** Find/Replace keyboard shortcuts inconsistency

**Affected files:**
- `help/ui/tk/feature-reference.md`
- `help/ui/tk/keyboard-shortcuts.md`

**Details:**
feature-reference.md lists 'Find/Replace (Ctrl+F / Ctrl+H)' but keyboard-shortcuts.md shows 'Ctrl+H' conflicts with Help system ('F1 or Ctrl+H' for help). This creates ambiguity about what Ctrl+H actually does.

---

### keyboard_shortcut_inconsistency

**Description:** Different keyboard shortcuts documented for same actions

**Affected files:**
- `help/ui/web/keyboard-shortcuts.md`
- `help/ui/web/debugging.md`

**Details:**
keyboard-shortcuts.md lists 'Ctrl+R' for Run, 'Ctrl+Q' for Stop, 'Ctrl+T' for Step, 'Ctrl+G' for Continue. debugging.md lists 'F5' for Continue, 'Shift+F5' for Stop, 'F10' for Step Over, 'F11' for Step Into, 'Shift+F11' for Step Out. These are completely different shortcut schemes for similar actions.

---

### feature_documentation_mismatch

**Description:** Advanced debugging features documented without corresponding shortcuts

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/keyboard-shortcuts.md`

**Details:**
debugging.md documents 'Conditional Breakpoints', 'Logpoints', 'Data Breakpoints', 'Debug Console', and 'Performance Profiling'. keyboard-shortcuts.md only mentions basic breakpoint toggle (Ctrl+B) and doesn't document shortcuts for these advanced features, suggesting they may not be implemented.

---

### file_operation_inconsistency

**Description:** Inconsistent file operation descriptions

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/keyboard-shortcuts.md`

**Details:**
getting-started.md describes Save as 'Download current program (triggers Save As if not yet named)' and 'Browser download dialog appears'. keyboard-shortcuts.md describes 'Ctrl+S' as 'Save current program (download)' but doesn't mention the Save As behavior or dialog. The actual behavior is unclear.

---

### ui_component_inconsistency

**Description:** Menu structure inconsistency

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/keyboard-shortcuts.md`

**Details:**
getting-started.md describes menu bar with 'File', 'Run', 'Help' menus. keyboard-shortcuts.md describes 'File Menu (Folder Icon)', 'Run Menu (Play Icon)', 'Debug Menu (Bug Icon)', 'Help Menu (Question Mark Icon)' - adding a Debug menu not mentioned in getting-started.md.

---

### version_number_inconsistency

**Description:** Both documents claim to be version 1.0.300 but describe different features

**Affected files:**
- `history/100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`
- `history/CALLSTACK_UI_PC_ENHANCEMENT_DONE.md`

**Details:**
100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md states 'Version: 1.0.300' and describes UI test coverage achievement. CALLSTACK_UI_PC_ENHANCEMENT_DONE.md states 'Completed: 2025-10-29 (v1.0.300)' and describes call stack UI enhancements. Both cannot be the same version if they represent different milestones.

---

### ui_backend_count_inconsistency

**Description:** Different counts and names for UI backends across documents

**Affected files:**
- `history/100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`
- `history/CALLSTACK_UI_PC_ENHANCEMENT_DONE.md`

**Details:**
100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md lists '4 major UI backends: CLI, Curses, Tkinter, Web'. CALLSTACK_UI_PC_ENHANCEMENT_DONE.md references 'curses, tk, visual' and separately mentions 'Visual/Web UI (src/ui/visual/, src/ui/web/)' suggesting 'visual' and 'web' might be different backends, which would make 5 total backends, not 4.

---

### feature_implementation_inconsistency

**Description:** Contradictory statements about STEP command implementation

**Affected files:**
- `history/100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`

**Details:**
Document states 'STEP Command Implementation - Status: Minimal implementation' and 'Implementation: Acknowledges command with message' suggesting basic functionality. However, it also states 'Full debugging functionality is deferred to future work' and under 'STEP Command Disambiguation' explains it serves dual purposes including 'Debug Command: STEP at statement start (new functionality)'. The extent of actual implementation is unclear.

---

### feature_availability_conflict

**Description:** Conflicting information about COMMON statement support

**Affected files:**
- `history/COMPILER_DESIGN.md`
- `history/COMPILER_VS_INTERPRETER_DIFFERENCES.md`

**Details:**
COMPILER_DESIGN.md states 'COMMON - May not be supported or works differently for linking' (suggesting partial support), while COMPILER_VS_INTERPRETER_DIFFERENCES.md explicitly states 'COMMON - NOT implemented - generates fatal error. Future versions will implement it similar to FORTRAN's COMMON statement.' The second document is more definitive that it's completely unsupported.

---

### feature_availability_conflict

**Description:** Conflicting information about ERASE statement support

**Affected files:**
- `history/COMPILER_DESIGN.md`
- `history/COMPILER_VS_INTERPRETER_DIFFERENCES.md`

**Details:**
COMPILER_DESIGN.md states 'ERASE - Not supported in static array mode' (implying it works in dynamic mode), while COMPILER_VS_INTERPRETER_DIFFERENCES.md states 'ERASE statement NOT implemented - generates fatal error' (implying complete lack of support). The first document suggests conditional support based on $DYNAMIC mode.

---

### feature_implementation_conflict

**Description:** Conflicting information about EOF() function implementation status

**Affected files:**
- `history/CURRENT_FAILURE_ANALYSIS.md`
- `history/CURSES_UI_INPUT_CHECK_DONE.md`

**Details:**
CURRENT_FAILURE_ANALYSIS.md lists 'EOF() Function - 7 files ⭐ HIGH PRIORITY' as a missing feature to implement with status 'Current Error: Unexpected token in expression: EOF_FUNC'. However, this contradicts the general implementation completeness suggested in other documents. The status of EOF() function implementation is unclear.

---

### file_count_mismatch

**Description:** Different total markdown file counts reported

**Affected files:**
- `history/DIRECTORY_STRUCTURE.md`
- `history/DOC_REORGANIZATION_COMPLETE.md`

**Details:**
DOC_REORGANIZATION_COMPLETE.md states 'Successfully reorganized all 94 markdown files' and later '71 total .md files' after cleanup. DOC_REORGANIZATION_PLAN.md also mentions '94 markdown files'. However, DIRECTORY_STRUCTURE.md does not provide a total count of markdown files, making it unclear if it reflects the pre-cleanup (94) or post-cleanup (71) state.

---

### test_corpus_count_inconsistency

**Description:** Different test corpus file counts for bas_tests1/

**Affected files:**
- `history/DIRECTORY_STRUCTURE.md`
- `history/ERROR_ANALYSIS.md`

**Details:**
DIRECTORY_STRUCTURE.md states 'basic/bas_tests1/ (215 files)' and 'Clean MBASIC 5.21 test corpus. Files verified to be MBASIC 5.21 dialect.' However, ERROR_ANALYSIS.md states '**Test Corpus**: 373 files in `bas_tests1/`'. This is a significant discrepancy (215 vs 373 files).

---

### success_rate_inconsistency

**Description:** Different parsing success rates reported

**Affected files:**
- `history/DIRECTORY_STRUCTURE.md`
- `history/ERROR_ANALYSIS.md`

**Details:**
DIRECTORY_STRUCTURE.md states '**Current Status**: 104/215 files (48.4%) parsing successfully' for bas_tests1/. ERROR_ANALYSIS.md states '**Successfully parsed**: 163 files (43.7%)' out of 373 files. These represent different test corpus sizes and success rates.

---

### status_inconsistency

**Description:** Conflicting completion status between plan and completion documents

**Affected files:**
- `history/DOC_REORGANIZATION_PLAN.md`
- `history/DOC_REORGANIZATION_COMPLETE.md`

**Details:**
DOC_REORGANIZATION_PLAN.md shows 'Status: IN PROGRESS' at the top, but DOC_REORGANIZATION_COMPLETE.md states '**Status**: ✅ COMPLETE (2025-10-24)'. The plan document appears to be outdated and should either be marked complete or archived.

---

### contradictory_information

**Description:** Conflicting file counts for multiline IF/THEN

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md: '7 Files' for multiline IF/THEN. FAILURE_CATEGORIZATION_CURRENT.md: '7 files' but different list includes 'mfil.bas, timeout.bas, un-prot.bas' which weren't in original list.

---

### contradictory_information

**Description:** Conflicting file counts for decimal line numbers

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md: '5 Files' (cbasedit.bas, cmprbib.bas, commo1.bas, fxparms.bas, journal.bas). FAILURE_CATEGORIZATION_CURRENT.md: '6 files' (adds airmiles.bas and voclst.bas, removes fxparms.bas).

---

### contradictory_information

**Description:** Conflicting file counts for Atari OPEN syntax

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md: '3 Files' (aut850.bas, auto850.bas, pckexe.bas). FAILURE_CATEGORIZATION_CURRENT.md: '4 files' (adds gammonb.bas).

---

### version_mismatch

**Description:** Version numbers mentioned don't align with completion status

**Affected files:**
- `history/FILEIO_MODULE_ARCHITECTURE_DONE.md`

**Details:**
Document title says 'DONE' and 'Status: COMPLETED (v1.0.370-1.0.400+)' but then lists items as 'Not Working (v1.0.373)' with SandboxedFileIO as stub. Contradicts completion claim.

---

### contradictory_information

**Description:** PRINT# statement status unclear

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md lists 'PRINT# Statement - 11 Files' as high priority to implement. FAILURE_CATEGORIZATION_CURRENT.md doesn't mention PRINT# at all in features to implement, suggesting it may have been implemented but this isn't stated.

---

### contradictory_information

**Description:** NAME statement file count discrepancy

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md: 'NAME Statement - 6 Files' (mxref.bas, othello.bas, simcvt2.bas, tabzilog.bas, trade.bas, tvigammo.bas). FAILURE_CATEGORIZATION_CURRENT.md: 'NAME Statement - 1 file' (pckget.bas only).

---

### optimization_count_inconsistency

**Description:** Conflicting statements about total number of optimizations

**Affected files:**
- `history/IMPLEMENTATION_COMPLETE.md`

**Details:**
IMPLEMENTATION_COMPLETE.md states both 'Total Optimizations: 27 (was 26)' in the summary section and 'doc/OPTIMIZATION_STATUS.md - Updated to 27 optimizations' in the documentation section, but also says 'Successfully implemented Phase 1 of Type Rebinding Analysis' as if it's a single new optimization. The increment from 26 to 27 is consistent, but unclear if this represents one optimization or multiple.

---

### status_inconsistency

**Description:** AUTO command listed as both implemented and not implemented

**Affected files:**
- `history/INTERACTIVE_MODE_2025-10-22.md`

**Details:**
INTERACTIVE_MODE_2025-10-22.md lists 'AUTO [start][,increment]' under 'Interactive Commands' with full documentation of its usage, but also lists '✓ AUTO - Auto line numbering mode' under 'Supported Commands' and later states 'Future Enhancements: 1. AUTO command - Auto line numbering'. This suggests the document was updated to add AUTO but the future enhancements section was not cleaned up.

---

### scope_inconsistency

**Description:** Conflicting information about 8K BASIC support and keyword spacing

**Affected files:**
- `history/LANGUAGE_CHANGES.md`
- `history/LEXER_FAILURE_ANALYSIS.md`

**Details:**
LANGUAGE_CHANGES.md discusses 8K BASIC as a variant to potentially support, mentioning 'keywords without spaces' as a feature. However, LEXER_FAILURE_ANALYSIS.md definitively concludes: 'Are lexer failures due to 8K BASIC (keywords without spaces)?' Answer: NO' and '~0% appear to be 8K BASIC'. The analysis recommends NOT supporting 8K BASIC, but LANGUAGE_CHANGES.md doesn't reflect this decision.

---

### documentation_status_conflict

**Description:** Inconsistent completion status between documentation and testing

**Affected files:**
- `history/LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md`
- `history/LANGUAGE_TESTING_DONE.md`

**Details:**
LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md shows 'Status: ✅ DONE (2025-10-29)' but lists many unchecked tasks in Phase 2 and Phase 3 (17 functions and 22 statements with '[ ]' checkboxes). LANGUAGE_TESTING_DONE.md shows 'Status: ✅ COMPLETE' dated '2025-10-31' with all major tasks completed. The documentation completion appears to be marked done before the actual work was finished.

---

### test_coverage_conflict

**Description:** Test count and coverage claims differ from documentation completion status

**Affected files:**
- `history/LANGUAGE_TESTING_DONE.md`
- `history/LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md`

**Details:**
LANGUAGE_TESTING_DONE.md claims '✅ **Test suite EXPANDED from 7 to 33 tests** - All passing!' and lists 33 specific test files. However, LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md's Phase 4 states 'Once documentation is complete' for test coverage, implying tests should come after documentation. The timeline suggests tests were completed (2025-10-31) before documentation was marked done (2025-10-29), which is chronologically impossible.

---

### parser_implementation_conflict

**Description:** Conflicting approaches to handling old BASIC syntax

**Affected files:**
- `history/LANGUAGE_CHANGES.md`
- `history/LEXER_CLEANUP_DONE.md`

**Details:**
LANGUAGE_CHANGES.md discusses supporting 8K BASIC with 'keywords without spaces' as a potential feature. LEXER_CLEANUP_DONE.md explicitly states this should NOT be supported: 'The keyword detection in STATEMENT_KEYWORDS attempts to handle old BASIC that allowed: fori=0to10. This is now handled by scripts to fix old BASIC. The lexer should parse the real language.' and recommends 'Remove the special handling for keywords running together with identifiers.'

---

### feature_status_conflict

**Description:** LEXER_ISSUES.md lists RANDOMIZE as needing implementation, but MISSING_OPERATORS_DONE_2025-10-31.md shows it was completed on 2025-10-31

**Affected files:**
- `history/LEXER_ISSUES.md`
- `history/MISSING_OPERATORS_DONE_2025-10-31.md`

**Details:**
LEXER_ISSUES.md (created earlier) states 'RANDOMIZE statement (not implemented)' in the RUN statement error section, while MISSING_OPERATORS_DONE_2025-10-31.md shows 'RANDOMIZE Statement' with 'Final Status: ✅ Lexer recognizes keyword, ✅ Parser creates RandomizeStatementNode, ✅ Interpreter implemented execute_randomize(), ✅ Test suite created and passing'

---

### feature_status_conflict

**Description:** Random access file operations marked as complete in one doc but file I/O marked as not implemented in another

**Affected files:**
- `history/MISSING_OPERATORS_DONE_2025-10-31.md`
- `history/PARSER_TEST_RESULTS.md`

**Details:**
MISSING_OPERATORS_DONE_2025-10-31.md: '4. Random Access File Operations ✅ IMPLEMENTED AND TESTED - Random access files are fully implemented! Implemented Statements: ✅ FIELD, ✅ GET, ✅ PUT, ✅ LSET, ✅ RSET'. PARSER_TEST_RESULTS.md: 'OPEN, CLOSE, LINE INPUT, WRITE - File I/O (not implemented)'

---

### parser_coverage_conflict

**Description:** Parser completion percentage conflicts between documents

**Affected files:**
- `history/PARSER_SUMMARY.md`
- `history/PARSER_TEST_RESULTS.md`

**Details:**
PARSER_SUMMARY.md states 'Parser: 100% ✓ (for core MBASIC)' and 'The parser is complete for core MBASIC functionality'. PARSER_TEST_RESULTS.md shows only 7.8% of files successfully parse and lists many missing features needed to reach 50% or 80% success rate

---

### date_inconsistency

**Description:** Document shows impossible future dates for creation and completion

**Affected files:**
- `history/PC_OLD_EXECUTION_METHODS_DONE.md`

**Details:**
Document header shows 'Created: 2025-10-28 (v1.0.287)' and 'Completed: 2025-10-29 (v1.0.300)' which are dates in October 2025, but all other Phase documents are dated 2025-10-24. This appears to be a typo where October was written instead of a different month.

---

### file_path_inconsistency

**Description:** Phase 1 documents creating files in src/io/ but then renames to src/iohandler/

**Affected files:**
- `history/PHASE1_IO_ABSTRACTION_PROGRESS.md`

**Details:**
Document shows 'Created three modules' under 'src/io/' (base.py, console.py, gui.py) but later states 'Renamed src/io/ → src/iohandler/' in commit 8c2c076. The initial file creation section should reference the final directory name or clarify these were renamed.

---

### feature_status_inconsistency

**Description:** Parser completion status inconsistent

**Affected files:**
- `history/README.md`
- `history/PRESERVE_ORIGINAL_SPACING_DONE.md`

**Details:**
README.md states 'Parser: Complete ✓' and lists it as 'Fully Implemented' with comprehensive features. However, PRESERVE_ORIGINAL_SPACING_DONE.md discusses parser modifications needed in 'Phase 2: Store Token Sequences in AST Nodes' suggesting the parser is not complete for spacing preservation features.

---

### module_structure_inconsistency

**Description:** Different module structure and file locations described

**Affected files:**
- `history/REFACTORING_COMPLETE.md`
- `history/PRESERVE_ORIGINAL_SPACING_DONE.md`

**Details:**
REFACTORING_COMPLETE.md shows structure with 'src/iohandler/', 'src/editing/', 'src/ui/' modules. PRESERVE_ORIGINAL_SPACING_DONE.md references 'src/ui/ui_helpers.py', 'src/ast_nodes.py', 'src/parser.py' without the modular structure, suggesting different architectural states.

---

### file_reference_inconsistency

**Description:** References to TODO files that may not exist or be documented

**Affected files:**
- `history/PRESERVE_ORIGINAL_SPACING_DONE.md`

**Details:**
PRESERVE_ORIGINAL_SPACING_DONE.md references 'PRETTY_PRINTER_SPACING_TODO.md' and 'CASE_PRESERVING_VARIABLES_TODO.md' in the 'Related TODOs' section, but these files are not listed in the provided documentation set, creating broken references.

---

### version_sequence_inconsistency

**Description:** Version numbers don't follow chronological order with dates

**Affected files:**
- `history/SESSION_2025_10_28_HELP_SEARCH_IMPROVEMENTS.md`
- `history/SESSION_2025_10_28_KEYWORD_CASE_INTEGRATION.md`
- `history/SESSION_2025-10-29_IMPROVEMENTS.md`
- `history/SESSION_2025-10-29_PC_REFACTORING.md`

**Details:**
Oct 28 sessions show v1.0.151 and v1.0.153, while Oct 29 sessions (later date) show v1.0.298→v1.0.299 and v1.0.299→v1.0.300. This suggests either the dates are wrong or there's a massive version jump (v1.0.153 to v1.0.298) between consecutive days.

---

### feature_status_inconsistency

**Description:** Conflicting information about execution architecture

**Affected files:**
- `history/SEMANTIC_ANALYSIS_FOR_BASIC_2025-10-22.md`
- `history/SESSION_2025-10-29_PC_REFACTORING.md`

**Details:**
SEMANTIC_ANALYSIS (dated Oct 22) discusses 'Runtime Setup Phase' and building line tables as future work with architecture diagrams showing 'Runtime Setup' as a separate phase. However, PC_REFACTORING (dated Oct 29) describes removing old execution methods and completing PC-based execution, suggesting the architecture has fundamentally changed. The SEMANTIC_ANALYSIS document doesn't mention PC-based execution at all.

---

### command_naming_inconsistency

**Description:** Inconsistent command names for settings commands between documents

**Affected files:**
- `history/SESSION_2025_10_28_SETTINGS_AND_CASE_HANDLING.md`
- `history/SETTINGS_SYSTEM_DONE.md`

**Details:**
SESSION_2025_10_28 mentions 'SET "setting.name" value', 'SHOW SETTINGS ["pattern"]', and 'HELP SET "setting.name"' commands. SETTINGS_SYSTEM_DONE mentions 'SET <setting> <value>', 'SHOW SETTINGS', and 'HELP SET' commands. The quote marks and parameter format differ.

---

### architectural_contradiction

**Description:** Single source of truth document recommends Program Object as truth, but timeline shows Runtime duplicates program data

**Affected files:**
- `history/SINGLE_SOURCE_OF_TRUTH_DONE.md`
- `history/TIMELINE_NOV_01.md`

**Details:**
SINGLE_SOURCE_OF_TRUTH_DONE.md recommends 'Option A (Program Object as Truth)' and states 'No duplication: Only program object stores the truth'. However, TIMELINE_NOV_01.md (Version 1.0.364) documents: 'Data Duplication Issue: - Discovered: ProgramManager stores lines/ASTs, Runtime copies them - Violates "no copy" principle'. This indicates the recommended architecture was not implemented and data duplication exists.

---

### implementation_status_mismatch

**Description:** Single source of truth marked as DONE but timeline shows it's still a TODO

**Affected files:**
- `history/SINGLE_SOURCE_OF_TRUTH_DONE.md`
- `history/TIMELINE_NOV_01.md`

**Details:**
SINGLE_SOURCE_OF_TRUTH_DONE.md filename suggests completion, but TIMELINE_NOV_01.md (Version 1.0.364) states: 'Created RUNTIME_PROGRAM_DATA_DUPLICATION_TODO.md documenting: - Problem and current workaround - Proper solution (Runtime references ProgramManager directly)'. This indicates the issue is documented as a TODO, not resolved.

---

### documentation_count_inconsistency

**Description:** Inconsistent count of documentation files

**Affected files:**
- `history/TIMELINE_OCT_23-25.md`

**Details:**
Session 7 states 'Total Documentation: 71 markdown files organized into logical categories' but Session 9 mentions '98 help files' with YAML front matter. The Combined Statistics mentions '100+ markdown files' but earlier sections cite different numbers (71 files in one place, 75 help files in another).

---

### help_file_count_inconsistency

**Description:** Inconsistent count of help system files

**Affected files:**
- `history/TIMELINE_OCT_23-25.md`

**Details:**
Session 9 states 'Extracted 38 BASIC-80 functions' and '37 BASIC-80 statements' (total 75), and later mentions 'Auto-enhanced metadata for 98 help files'. The Combined Statistics section states '75 individual help files (38 functions, 37 statements)' but Session 9 clearly mentions 98 files total.

---

### time_calculation_inconsistency

**Description:** Session time ranges don't add up correctly

**Affected files:**
- `history/TIMELINE_OCT_23-25.md`

**Details:**
Session 8 claims '6:00 AM - 4:00 PM' which is 10 hours, but the subsections show '6:00 AM - 8:00 AM' (2h), '8:00 AM - 10:00 AM' (2h), '10:00 AM - 12:00 PM' (2h), '12:00 PM - 2:00 PM' (2h), '2:00 PM - 4:00 PM' (2h) = 10 hours total. This is actually consistent, but the breakdown suggests continuous work which may not account for breaks.

---

### commit_count_inconsistency

**Description:** Inconsistent commit counts for October 28

**Affected files:**
- `history/TIMELINE_OCT_27-28.md`
- `history/TIMELINE_OCT_28-31.md`

**Details:**
TIMELINE_OCT_27-28.md states 'October 28: 31 commits' in Combined Statistics. TIMELINE_OCT_28-31.md states 'October 28: ~28 commits' in Combined Statistics. These should match if they're covering the same day.

---

### version_range_inconsistency

**Description:** Version jump inconsistency in Session 1

**Affected files:**
- `history/TIMELINE_OCT_28-31.md`

**Details:**
TIMELINE_OCT_28-31.md Oct 28 Session 1 states 'Versions: 1.0.106 → 1.0.124' (19 version increments) but also states '19 commits'. However, Session 2 on same day states 'Versions: 1.0.125 → 1.0.133' which correctly follows, but the version count (1.0.124 - 1.0.106 = 18 versions, not 19).

---

### total_statistics_mismatch

**Description:** Total commits don't match sum of daily commits

**Affected files:**
- `history/TIMELINE_OCT_27-28.md`

**Details:**
TIMELINE_OCT_27-28.md Combined Statistics states 'Total: 155 commits' and breaks down as 'October 27: 124 commits' and 'October 28: 31 commits'. However, 124 + 31 = 155, which is correct. But the document also states 'Total Commits: 155 commits' in Executive Summary while listing 'Versions: 1.0.0 → 1.0.106 (106 version increments)', suggesting potential mismatch between commits and version increments.

---

### version_number_inconsistency

**Description:** Version numbers are inconsistent and out of sequence across documents

**Affected files:**
- `history/TRUE_100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`
- `history/UI_STATUS_FIELD_REMOVAL_DONE.md`
- `history/VARIABLE_SORT_REFACTORING_DONE.md`

**Details:**
TRUE_100_PERCENT document shows 'Version: 1.0.301', UI_STATUS document references 'v1.0.458-461', and VARIABLE_SORT document doesn't specify a version but references Web/Tk/Curses UIs. The version jump from 1.0.301 to 1.0.458+ is unexplained.

---

### completion_status_inconsistency

**Description:** Document title says 'DONE' but content shows incomplete work

**Affected files:**
- `history/UI_STATUS_FIELD_REMOVAL_DONE.md`

**Details:**
Title: 'UI Status Field Removal - DONE' but document shows '## Completed' section with only Curses UI done, and '## Pending Updates' section listing TK UI, Web UI, and CLI UI as incomplete. The document should either be titled 'TODO' or 'IN_PROGRESS' rather than 'DONE'.

---

### phase_status_inconsistency

**Description:** Phase 5 status conflicts between documents

**Affected files:**
- `history/VISUAL_BACKENDS_CURSES_TK.md`
- `history/VISUAL_UI_REFACTORING_PLAN.md`

**Details:**
VISUAL_UI_REFACTORING_PLAN.md states 'Phase 5: Mobile/Visual UI (DEFERRED)' and describes it as 'intentionally deferred until after Phases 1-4 are complete'. However, VISUAL_BACKENDS_CURSES_TK.md shows Phase 5 as implemented with complete Curses and Tkinter backends, contradicting the deferred status. The plan document says Phase 5 is about 'Mobile/Visual UI Framework Evaluation' while the implementation document shows Phase 5 as already having production-ready visual backends.

---

### directory_structure_inconsistency

**Description:** Conflicting information about directory naming

**Affected files:**
- `history/VISUAL_BACKENDS_CURSES_TK.md`
- `history/VISUAL_UI_REFACTORING_PLAN.md`

**Details:**
VISUAL_UI_REFACTORING_PLAN.md Phase 1 checklist shows 'Create src/iohandler/ directory structure (renamed from io/)' and notes 'src/iohandler/' was used instead of 'src/io/'. However, the proposed architecture section still shows 'src/io/' in the directory structure diagram. VISUAL_BACKENDS_CURSES_TK.md doesn't clarify which naming convention is actually used.

---

### feature_scope_inconsistency

**Description:** Debugging features implementation status unclear

**Affected files:**
- `history/VISUAL_BACKENDS_CURSES_TK.md`
- `history/VISUAL_UI_REFACTORING_PLAN.md`

**Details:**
VISUAL_UI_REFACTORING_PLAN.md Phase 1 notes state 'ExecutionState, stepping, and breakpoints deferred (not needed for initial visual UI)'. However, the plan document extensively describes debugging features like get_execution_state(), step_line(), set_breakpoint() as part of Phase 1 goals. VISUAL_BACKENDS_CURSES_TK.md doesn't mention whether these debugging features are implemented in the Curses/Tk backends, creating ambiguity about their actual status.

---

### version_number_mismatch

**Description:** Different version numbers mentioned for the same feature implementation

**Affected files:**
- `history/WEB_UI_INPUT_UX_DONE.md`
- `history/WEB_UI_MISSING_FEATURES_OLD.md`

**Details:**
WEB_UI_INPUT_UX_DONE.md states INPUT was implemented in 'Version: 1.0.174', while WEB_UI_MISSING_FEATURES_OLD.md states 'Current Version: 1.0.176' and mentions INPUT as 'Status: ✅ IMPLEMENTED' with note 'Web Has: Inline input field below output (v1.0.174)'. The discrepancy is minor but the 'Current Version' in the OLD doc suggests it may be outdated.

---

### feature_status_conflict

**Description:** Smart Insert Line feature shows conflicting implementation status

**Affected files:**
- `history/WEB_UI_MISSING_FEATURES_OLD.md`
- `history/WEB_UI_PARITY_DONE.md`

**Details:**
WEB_UI_MISSING_FEATURES_OLD.md (dated 2025-10-28) lists 'Auto-Numbering' as 'Status: ❌ NOT IMPLEMENTED' under CRITICAL MISSING FEATURES. However, WEB_UI_PARITY_DONE.md (dated 2025-10-26, earlier) shows 'Smart Insert Line' as '✅ COMPLETE' with implementation at 'web_ui.py:551-684'. The OLD doc may be referring to a different auto-numbering feature, but the terminology and priority suggest they may be related features with conflicting status.

---

### contradictory_information

**Description:** Variables Window column order shows conflicting status

**Affected files:**
- `history/WEB_UI_MISSING_FEATURES_OLD.md`
- `history/WEB_UI_PARITY_DONE.md`

**Details:**
WEB_UI_MISSING_FEATURES_OLD.md (dated 2025-10-28) does not mention Variables Window column order as a known issue. However, WEB_UI_PARITY_DONE.md (dated 2025-10-26) lists 'Variables Window Column Order - Fixed to match Tk UI' as a recent completion, changing from 'Name | Type | Value' to 'Name | Value | Type' at 'Location: src/ui/web/web_ui.py:886-890'. The OLD doc should reflect this fix if it's truly current as of 2025-10-28.

---

### date_inconsistency

**Description:** Document dates suggest temporal inconsistency

**Affected files:**
- `history/WEB_UI_PARITY_DONE.md`
- `history/WEB_UI_MISSING_FEATURES_OLD.md`

**Details:**
WEB_UI_PARITY_DONE.md is dated '2025-10-26' and shows Smart Insert Line as complete. WEB_UI_MISSING_FEATURES_OLD.md is dated '2025-10-28' (2 days later) but lists Auto-Numbering as NOT IMPLEMENTED. If these are the same feature or related features, the later document should reflect the earlier completion. The filename 'OLD.md' suggests it may be an archived version, but the date is later than the DONE document.

---

### version_mismatch

**Description:** Different version numbers mentioned in documentation

**Affected files:**
- `history/session_2025-10-27_error_handling_continue_button.md`
- `history/session_keybinding_system_implementation.md`

**Details:**
In 'session_2025-10-27_error_handling_continue_button.md', the final version is stated as '1.0.5'. However, in 'session_keybinding_system_implementation.md', the macro expansion example shows '{{version}} → "5.21"', which appears to be the MBASIC language version rather than the interpreter version.

---

### keybinding_conflict

**Description:** Different help keybindings for Tk UI

**Affected files:**
- `history/session_2025-10-25_help_system_keybindings.md`
- `history/session_keybinding_system_implementation.md`

**Details:**
In 'session_2025-10-25_help_system_keybindings.md', there's no mention of Tk UI help keybinding. In 'session_keybinding_system_implementation.md', it states 'Keyboard shortcuts: Ctrl+? or Ctrl+/ to open' for Tk GUI help, but the JSON keybinding example shows 'Ctrl+H' as the help key.

---

### feature_implementation_conflict

**Description:** Different documents claim different features were implemented in the same session. FINAL_SESSION_SUMMARY lists File I/O, DEF FN, RANDOMIZE, CALL, and Array Fix. SESSION_2025-10-22_SUMMARY lists ELSE, keyword splitting, INPUT #filenum, and ERASE. SESSION_FINAL_SUMMARY lists RESET, INPUT ;LINE, REM handling, and WRITE#.

**Affected files:**
- `history/sessions/FINAL_SESSION_SUMMARY.md`
- `history/sessions/SESSION_2025-10-22_SUMMARY.md`
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`

**Details:**
FINAL_SESSION_SUMMARY: 'File I/O Support', 'DEF FN', 'RANDOMIZE', 'CALL', 'Array Subscript Fix'. SESSION_2025-10-22_SUMMARY: 'ELSE Keyword Support', 'Keyword-Identifier Splitting', 'INPUT #filenum Support', 'ERASE Statement'. SESSION_FINAL_SUMMARY: 'RESET Statement', 'INPUT ;LINE Syntax', 'REM and Statement Continuation', 'WRITE# Statement Fix'.

---

### lines_of_code_inconsistency

**Description:** Different line counts for successfully parsed code on the same date.

**Affected files:**
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`
- `history/snapshots/PARSER_STATUS_2025-10-22.md`

**Details:**
SESSION_FINAL_SUMMARY: 'Lines of code: 14,586'. PARSER_STATUS: 'Lines of Code: 14,445'. Both claim to be current status for 2025-10-22.

---

### statement_count_inconsistency

**Description:** Different statement counts for successfully parsed code on the same date.

**Affected files:**
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`
- `history/snapshots/PARSER_STATUS_2025-10-22.md`

**Details:**
SESSION_FINAL_SUMMARY: 'Statements: 17,614'. PARSER_STATUS: 'Statements: 17,698'. Both claim to be current status for 2025-10-22.

---

### token_count_inconsistency

**Description:** Different token counts for successfully parsed code on the same date.

**Affected files:**
- `history/sessions/SESSION_FINAL_SUMMARY_2025-10-22.md`
- `history/snapshots/PARSER_STATUS_2025-10-22.md`

**Details:**
SESSION_FINAL_SUMMARY: 'Tokens: 149,841'. PARSER_STATUS: 'Tokens: 146,134'. Both claim to be current status for 2025-10-22.

---

### contradictory_statistics

**Description:** Game count mismatch in library statistics

**Affected files:**
- `library/index.md`
- `library/games/index.md`

**Details:**
library/index.md states 'Total Programs: 114+' at the bottom. However, counting the games in library/games/index.md shows 113 games listed, which would make the total library count inconsistent if other categories are added.

---

### contradictory_information

**Description:** Expected success rate calculation error

**Affected files:**
- `history/snapshots/PARSE_ERROR_CATEGORIES_2025-10-22.md`

**Details:**
PARSE_ERROR_CATEGORIES_2025-10-22.md shows 'Phase 3 | Edge cases | +14 | 97.5% | +8.7%' but 113 + 19 + 14 + 14 = 160 files out of 163 would be 98.2%, not 97.5%. The math doesn't add up correctly.

---

### missing_reference

**Description:** CHOOSING_YOUR_UI.md describes four UIs (CLI, Curses, Tk, Web) but QUICK_REFERENCE.md only documents the Curses UI without mentioning the existence of other UIs

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`
- `user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states 'MBASIC gives you **two separate case handling systems**' and describes CLI, Curses, Tk, and Web UIs. QUICK_REFERENCE.md is titled 'MBASIC Curses IDE - Quick Reference Card' and only covers Curses UI commands without acknowledging other UI options.

---

### inconsistent_information

**Description:** Two different installation guides exist with conflicting information - one is complete, one is a placeholder

**Affected files:**
- `user/INSTALL.md`
- `user/INSTALLATION.md`

**Details:**
INSTALL.md provides detailed installation instructions including virtual environment setup and troubleshooting. INSTALLATION.md is marked as 'PLACEHOLDER - Documentation in progress' with minimal quick install instructions. This creates confusion about which guide to follow.

---

### missing_reference

**Description:** CHOOSING_YOUR_UI.md references UI_FEATURE_COMPARISON.md which is not provided in the documentation set

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`

**Details:**
At the end of CHOOSING_YOUR_UI.md: '## More Information - [UI Feature Comparison](UI_FEATURE_COMPARISON.md) - Detailed feature matrix' but this file is not included.

---

### missing_reference

**Description:** QUICK_REFERENCE.md references multiple documentation files that are not provided

**Affected files:**
- `user/QUICK_REFERENCE.md`

**Details:**
References: 'DEBUGGER_COMMANDS.md', 'CONTINUE_FEATURE.md', 'BREAKPOINT_SUMMARY.md', 'HELP_SYSTEM_SUMMARY.md' - none of these files are included in the documentation set.

---

### feature_availability_conflict

**Description:** Find and Replace availability inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md states 'Press Ctrl+H (Find and Replace)' as an available feature. However, UI_FEATURE_COMPARISON.md shows 'Find/Replace' with 'Ctrl+H' shortcut but also lists under 'Recently Added (2025-10-29): ✅ Tk: Find/Replace functionality', suggesting it's newly added. The keyboard shortcuts table in UI_FEATURE_COMPARISON.md shows 'Ctrl+H/F1' for Help in Curses, creating potential confusion with Tk's Ctrl+H for Find/Replace.

---

### command_inconsistency

**Description:** Inconsistent command for renumbering programs

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/keyboard-shortcuts.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md uses 'Ctrl+E' for renumber throughout. keyboard-shortcuts.md (Curses UI) states 'Ctrl+E | Renumber all lines (RENUM)', using the command name 'RENUM'. However, SETTINGS_AND_CONFIGURATION.md never mentions the 'RENUM' command name, only referring to the renumber dialog.

---

### keyboard_shortcut_inconsistency

**Description:** Step execution keyboard shortcuts differ between UIs

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+T' for 'Step through code (next statement)' and 'Ctrl+L' for 'Step through code (next line)'. keyboard-shortcuts.md (Curses UI) lists 'Ctrl+K' for 'Step Line' and 'Ctrl+T' for 'Step Statement'. The Ctrl+K shortcut has different meanings: in Tk it's 'Show/hide Execution Stack window', in Curses it's 'Step Line'.

---

### save_command_inconsistency

**Description:** Save keyboard shortcut inconsistency in Curses UI

**Affected files:**
- `user/keyboard-shortcuts.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
keyboard-shortcuts.md (Curses UI) lists 'Ctrl+V' for 'Save program' and 'Shift+Ctrl+V' for 'Save As'. However, UI_FEATURE_COMPARISON.md shows 'Ctrl+S' for Save across all UIs including Curses. This is a significant inconsistency as Ctrl+V is also mentioned for Variables window in other contexts.

---

## 🟢 Low Severity

### author_credit_inconsistency

**Description:** Author credit differs between documents - one mentions 'Andrew Wohl' specifically, the other uses 'avwohl' GitHub username

**Affected files:**
- `MBASIC_HISTORY.md`
- `PROJECT_STATUS.md`

**Details:**
MBASIC_HISTORY.md: 'Written from scratch in Python by Andrew Wohl' vs PROJECT_STATUS.md: 'GitHub: https://github.com/avwohl/mbasic'

---

### repository_path_inconsistency

**Description:** Documentation references different relative paths - README.md uses '../mkdocs.yml' while COMPILATION_STRATEGIES_COMPARISON.md uses 'doc/' prefix

**Affected files:**
- `README.md`
- `design/future_compiler/COMPILATION_STRATEGIES_COMPARISON.md`

**Details:**
README.md: '**Configuration:** `../mkdocs.yml`' vs COMPILATION_STRATEGIES_COMPARISON.md: '**Related Files**: - `doc/DYNAMIC_TYPE_CHANGE_PROBLEM.md`'

---

### documentation_structure_inconsistency

**Description:** README.md describes docs directory structure but PROJECT_STATUS.md references 'docs/history/', 'docs/dev/', 'docs/user/' while README.md shows '/history', '/dev', '/user' without 'docs/' prefix

**Affected files:**
- `README.md`
- `PROJECT_STATUS.md`

**Details:**
README.md: '### `/help` - In-UI Help System' vs PROJECT_STATUS.md: '*For detailed session logs, see docs/history/*'

---

### inconsistent_terminology

**Description:** Inconsistent naming of BASIC dialect

**Affected files:**
- `design/future_compiler/DYNAMIC_TYPE_CHANGE_PROBLEM.md`
- `design/future_compiler/INTEGER_INFERENCE_STRATEGY.md`

**Details:**
DYNAMIC_TYPE_CHANGE_PROBLEM.md uses 'MBASIC (MBASIC)' in the first line and 'interpreted MBASIC' later. INTEGER_INFERENCE_STRATEGY.md doesn't specify which BASIC dialect it's targeting, though it references test_type_change.bas which is from the MBASIC context.

---

### missing_reference

**Description:** References non-existent documentation file

**Affected files:**
- `design/future_compiler/INTEGER_INFERENCE_STRATEGY.md`

**Details:**
INTEGER_INFERENCE_STRATEGY.md lists 'doc/COMPILATION_STRATEGIES_COMPARISON.md' in Related Files section, but this file is not provided in the documentation set and is not mentioned in DYNAMIC_TYPE_CHANGE_PROBLEM.md.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for Common Subexpression Elimination

**Affected files:**
- `design/future_compiler/INTEGER_SIZE_INFERENCE.md`
- `design/future_compiler/ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md`

**Details:**
INTEGER_SIZE_INFERENCE.md uses 'CSE (Common Subexpression Elimination)' while ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md uses 'CSE' without expansion in some places and 'common_subexpressions' in code. Both refer to the same optimization but terminology varies.

---

### data_structure_inconsistency

**Description:** Inconsistent state tracking attributes

**Affected files:**
- `design/future_compiler/ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md`
- `design/future_compiler/ITERATIVE_OPTIMIZATION_STRATEGY.md`

**Details:**
ITERATIVE_OPTIMIZATION_STRATEGY.md's _get_optimization_state() includes 'self.folded_expressions' for constant folding state. However, ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md's _count_optimizations() method does not include folded_expressions in its count, and the _clear_iterative_state() method does not mention clearing or preserving folded_expressions.

---

### convergence_iteration_count_inconsistency

**Description:** Different max_iterations defaults

**Affected files:**
- `design/future_compiler/ITERATIVE_OPTIMIZATION_STRATEGY.md`
- `design/future_compiler/ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md`

**Details:**
ITERATIVE_OPTIMIZATION_STRATEGY.md proposes 'MAX_ITERATIONS = 10' as safety limit and recommends 'Default: max_iterations=5'. ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md implements 'max_iterations: int = 5' as the default, which matches the recommendation but differs from the initial proposal of 10 in the strategy document.

---

### date_inconsistency

**Description:** Impossible implementation date

**Affected files:**
- `design/future_compiler/ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md`

**Details:**
ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md states 'Implementation Date: 2025-10-24' which is a future date (document appears to be from 2024 or earlier based on context). This is likely a typo and should probably be 2024-10-24.

---

### incomplete_categorization

**Description:** Several data structures mentioned in 'MUST RECALCULATE' section are not analyzed in the detailed Category sections

**Affected files:**
- `design/future_compiler/OPTIMIZATION_DATA_STALENESS_ANALYSIS.md`

**Details:**
The following items appear in the 'MUST RECALCULATE' list but are not discussed in Categories 1-3: self.strength_reductions, self.expression_reassociations, self.copy_propagations, self.active_copies, self.branch_optimizations, self.uninitialized_warnings, self.initialized_variables, self.induction_variables, self.active_ivs, self.range_info, self.active_ranges, self.available_expr_analysis. These are listed as needing recalculation but lack the detailed analysis provided for other optimizations.

---

### missing_data_structure

**Description:** self.array_base and self.flags are listed in NEVER STALE section but not analyzed in any category

**Affected files:**
- `design/future_compiler/OPTIMIZATION_DATA_STALENESS_ANALYSIS.md`

**Details:**
In the 'NEVER STALE (Keep Forever)' section, self.array_base and self.flags are listed but these data structures are not mentioned or analyzed in any of the three main categories (STRUCTURAL, INCREMENTAL, REPORTING ONLY).

---

### file_structure_inconsistency

**Description:** Documentation file location inconsistency

**Affected files:**
- `design/future_compiler/README_OPTIMIZATIONS.md`
- `design/future_compiler/SEMANTIC_ANALYSIS_DESIGN.md`

**Details:**
README_OPTIMIZATIONS.md shows 'doc/OPTIMIZATION_STATUS.md' in the file structure, while SEMANTIC_ANALYSIS_DESIGN.md references it as 'doc/OPTIMIZATION_STATUS.md' in documentation section. Both agree on location, but README shows it under 'doc/' while listing other docs at root level.

---

### line_count_inconsistency

**Description:** Different line counts reported for semantic_analyzer.py

**Affected files:**
- `design/future_compiler/README_OPTIMIZATIONS.md`
- `design/future_compiler/SEMANTIC_ANALYSIS_DESIGN.md`

**Details:**
README_OPTIMIZATIONS.md states 'semantic_analyzer.py # Main implementation (3,545 lines)' while SEMANTIC_ANALYSIS_DESIGN.md states 'src/semantic_analyzer.py - Main implementation (3545 lines)'. The comma placement differs (3,545 vs 3545), though this may be formatting rather than actual inconsistency.

---

### test_count_inconsistency

**Description:** Inconsistent test case count description

**Affected files:**
- `design/future_compiler/README_OPTIMIZATIONS.md`
- `design/future_compiler/SEMANTIC_ANALYSIS_DESIGN.md`

**Details:**
README_OPTIMIZATIONS.md states '200+ individual test cases' while SEMANTIC_ANALYSIS_DESIGN.md also states 'Total Test Cases: 200+'. Both use '200+' but this is vague and could indicate the exact count is unknown or differs between documents.

---

### section_numbering

**Description:** Inconsistent section numbering in Key Features

**Affected files:**
- `design/future_compiler/SEMANTIC_ANALYZER.md`

**Details:**
The document has: '1. Runtime Constant Evaluation', '2. Constant Expression Evaluator', '3. Compile-Time IF/THEN/ELSE Evaluation', '4. Symbol Tables', '5. Compiler-Specific Validations', '6. Compilation Switch Detection', '7. Line Number Validation', then '5. Constant Folding Optimization' (duplicate 5), '6. Common Subexpression Elimination' (duplicate 6), '7. GOSUB/Subroutine Analysis' (duplicate 7). Sections 5-7 are numbered twice.

---

### missing_cross_reference

**Description:** TYPE_REBINDING_IMPLEMENTATION_SUMMARY.md is not mentioned in SEMANTIC_ANALYZER.md's Future Enhancements or References

**Affected files:**
- `design/future_compiler/SEMANTIC_ANALYZER.md`
- `design/future_compiler/TYPE_REBINDING_IMPLEMENTATION_SUMMARY.md`

**Details:**
SEMANTIC_ANALYZER.md lists 'Future Enhancements' including type checking, but doesn't reference the already-implemented Type Rebinding Analysis documented in TYPE_REBINDING_IMPLEMENTATION_SUMMARY.md. The implementation summary shows this is integrated into semantic_analyzer.py as the 15th pass.

---

### inconsistent_terminology

**Description:** Inconsistent use of 'compile-time' vs 'compile time'

**Affected files:**
- `design/future_compiler/SEMANTIC_ANALYZER.md`

**Details:**
The document uses both 'compile-time' (hyphenated) in section titles like 'Compile-Time IF/THEN/ELSE Evaluation' and 'compile time' (two words) in body text like 'evaluated at compile time'. Should be consistent throughout.

---

### missing_cross_reference

**Description:** optimization_guide.md references files that don't exist in the provided documentation

**Affected files:**
- `design/future_compiler/optimization_guide.md`

**Details:**
The guide references 'ACCOMPLISHMENTS.md', 'OPTIMIZATION_STATUS.md', 'analyze_program.py', and 'demo_all_optimizations.bas' but these files are not included in the documentation set provided for analysis. Cannot verify if these references are accurate or if the files exist.

---

### example_inconsistency

**Description:** Same example code produces different analysis conclusions

**Affected files:**
- `design/future_compiler/TYPE_REBINDING_PHASE2_DESIGN.md`
- `design/future_compiler/TYPE_REBINDING_STRATEGY.md`

**Details:**
Both documents use the example 'X = 10, Y = X + 1, X = 10.5, Z = Y + X' but with different conclusions. PHASE2_DESIGN.md says 'Phase 1 behavior: Cannot optimize (Y depends on old X value)' while STRATEGY.md says 'Can handle this: Promote Y to DOUBLE for line 130' and marks it with '✅'.

---

### ui_reference_inconsistency

**Description:** AST_SERIALIZATION.md lists four UIs (CLI, Tk, Web, Curses) while AUTO_NUMBERING_IMPLEMENTATION.md only discusses TK UI implementation

**Affected files:**
- `dev/AST_SERIALIZATION.md`
- `dev/AUTO_NUMBERING_IMPLEMENTATION.md`

**Details:**
AST_SERIALIZATION.md: 'All UIs (CLI, Tk, Web, Curses) use the same serialization'. AUTO_NUMBERING_IMPLEMENTATION.md only mentions 'TK UI' and 'src/ui/tk_ui.py' with no mention of other UIs having auto-numbering

---

### version_number_inconsistency

**Description:** Version history shows gaps and inconsistent versioning scheme

**Affected files:**
- `dev/AUTO_NUMBERING_IMPLEMENTATION.md`

**Details:**
Version History lists: 1.0.58, 1.0.59, 1.0.61, 1.0.62, 1.0.63-1.66 (range), 1.0.67, 1.0.70, 1.0.71, 1.0.72. Missing versions 1.0.60, 1.0.68, 1.0.69 without explanation

---

### version_number_inconsistency

**Description:** Multiple version numbers for same feature

**Affected files:**
- `dev/AUTO_NUMBERING_WEB_UI_FIX.md`

**Details:**
AUTO_NUMBERING_WEB_UI_FIX.md mentions 'Version: 1.0.318 (completed 2025-10-31)' for the main fix, then later mentions 'Version: 1.0.323 (completed 2025-11-01)' for the Enter key fix. The document doesn't clearly indicate these are sequential versions or explain the version jump.

---

### terminology_inconsistency

**Description:** Inconsistent naming of UI components

**Affected files:**
- `dev/AUTO_NUMBERING_VISUAL_UI_DESIGN.md`
- `dev/AUTO_NUMBERING_WEB_UI_FIX.md`

**Details:**
AUTO_NUMBERING_VISUAL_UI_DESIGN.md refers to 'Web UI' throughout, while AUTO_NUMBERING_WEB_UI_FIX.md uses both 'Web UI' and references 'nicegui_backend.py', but the design doc doesn't mention NiceGUI as the Web UI implementation framework.

---

### success_rate_calculation_inconsistency

**Description:** Different success rate calculations for similar metrics

**Affected files:**
- `dev/BAD_SYNTAX_ANALYSIS.md`
- `dev/CALL_IMPLEMENTATION.md`

**Details:**
BAD_SYNTAX_ANALYSIS.md calculates 'Parser success rate: 35%' as '115 working programs' out of total programs. CALL_IMPLEMENTATION.md shows 'Success rate: 33 files (8.8%)' which appears to be 33 out of 375 total files. The denominators and what constitutes 'success' appear different between documents.

---

### date_format_inconsistency

**Description:** Inconsistent date formats across documents

**Affected files:**
- `dev/AUTO_NUMBERING_WEB_UI_FIX.md`
- `dev/BAD_SYNTAX_ANALYSIS.md`
- `dev/BROKEN_LINKS_ANALYSIS.md`
- `dev/BROWSER_OPENING_FIX.md`
- `dev/CALL_IMPLEMENTATION.md`

**Details:**
Documents use different date formats: 'Date: 2025-10-30, Updated: 2025-10-31' (AUTO_NUMBERING_WEB_UI_FIX.md), 'Analysis Date: 2025-10-26' (BAD_SYNTAX_ANALYSIS.md), 'Date: 2025-10-26' (BROKEN_LINKS_ANALYSIS.md), '2025-10-30' (BROWSER_OPENING_FIX.md), and '2025-10-22' (CALL_IMPLEMENTATION.md). Some use 'Date:' prefix, others don't.

---

### command_count_inconsistency

**Description:** Curses UI command count inconsistency within same document

**Affected files:**
- `dev/CODE_DUPLICATION_ANALYSIS.md`

**Details:**
CODE_DUPLICATION_ANALYSIS.md states 'Curses UI: 4 commands' in the 'Commands Per UI' section, but later in 'Consolidation Results' it states 'Curses UI: 4 commands → 10 commands (150% increase)' and 'Curses UI: Added 134 LOC for 6 new commands'. The math doesn't align: 4 + 6 = 10 is correct, but the document initially lists only 4 commands.

---

### web_ui_file_naming_inconsistency

**Description:** Web UI backend file naming is inconsistent

**Affected files:**
- `dev/CODE_DUPLICATION_ANALYSIS.md`
- `dev/CODEMIRROR_INTEGRATION_PROGRESS.md`
- `dev/CODEMIRROR6_INTEGRATION_ISSUES.md`

**Details:**
CODE_DUPLICATION_ANALYSIS.md refers to 'web_ui.py', CODEMIRROR_INTEGRATION_PROGRESS.md refers to 'nicegui_backend.py', and CODEMIRROR6_INTEGRATION_ISSUES.md also refers to 'nicegui_backend.py'. These appear to be the same file with different names, or the file was renamed.

---

### missing_web_ui_in_cleanup

**Description:** Web UI directory not mentioned in cleanup summary

**Affected files:**
- `dev/CLEANUP_SUMMARY.md`

**Details:**
CLEANUP_SUMMARY.md shows directory structure with 'src/' but doesn't detail the 'src/ui/web/' subdirectory that is extensively referenced in other documents (CODEMIRROR_INTEGRATION_PROGRESS.md, CODEMIRROR6_INTEGRATION_ISSUES.md). The cleanup summary may be incomplete or the web UI was added after the cleanup.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for carriage return character

**Affected files:**
- `dev/COMPILER_MEMORY_OPTIMIZATION.md`
- `dev/CR_LINE_ENDING_FIX.md`

**Details:**
COMPILER_MEMORY_OPTIMIZATION.md uses 'Control-M' while CR_LINE_ENDING_FIX.md uses both 'Control-M' and '^M' interchangeably. The hex value 0x0d is also written as '0x0d' in one place and '0x0D' (uppercase) in another within CR_LINE_ENDING_FIX.md.

---

### date_format_inconsistency

**Description:** Inconsistent date formats used across documents

**Affected files:**
- `dev/CR_LINE_ENDING_FIX.md`
- `dev/CURSES_FEATURE_PARITY_COMPLETE.md`

**Details:**
CR_LINE_ENDING_FIX.md uses '2025-10-22' format while CURSES_FEATURE_PARITY_COMPLETE.md uses '2025-10-28' format. Both use YYYY-MM-DD but the dates suggest October 2025 which may be a typo (should likely be 2024).

---

### file_reference_inconsistency

**Description:** References removed file that may still exist

**Affected files:**
- `dev/CURSES_FEATURE_PARITY_COMPLETE.md`

**Details:**
Document states 'docs/dev/WORK_IN_PROGRESS.md - Removed (task complete)' under 'Files Modified' but this contradicts the statement that files were 'Modified' rather than 'Deleted'.

---

### status_inconsistency

**Description:** Conflicting status indicators for implementation phases

**Affected files:**
- `dev/COMPILER_MEMORY_OPTIMIZATION.md`

**Details:**
Document header states 'Status: Future Work - Design complete, implementation pending' but Phase 1 shows '[x] Separate array and string spaces' and other completed items, suggesting some implementation has been done.

---

### path_inconsistency

**Description:** Inconsistent path format for related documents

**Affected files:**
- `dev/CURSES_FEATURE_PARITY_COMPLETE.md`

**Details:**
Under 'Related Documents', paths are listed as 'docs/dev/CURSES_VS_TK_GAP_ANALYSIS.md' and 'docs/dev/WEB_UI_FEATURE_PARITY.md' but under 'Files Modified' paths are listed as 'src/ui/curses_ui.py' without the 'docs/' prefix, suggesting inconsistent path notation.

---

### inconsistent_terminology

**Description:** Inconsistent terminology for line storage format

**Affected files:**
- `dev/CURSES_UI_FEATURE_PARITY.md`
- `dev/CURSES_UI_FILE_LOADING_FIX.md`

**Details:**
CURSES_UI_FEATURE_PARITY.md uses 'stored text' and 'stored lines' to refer to how lines are kept, while CURSES_UI_FILE_LOADING_FIX.md uses 'complete line text' and 'full line text'. The feature parity doc suggests lines are stored as '20 PRINT I' (with line number), but the file loading fix doc's regex pattern suggests the same, yet the feature parity doc's 'Known Issues' section warns against adding 'leading spaces to line numbers' as if this is a formatting concern separate from storage.

---

### missing_reference

**Description:** Feature parity doc doesn't reference the file loading fix

**Affected files:**
- `dev/CURSES_UI_FEATURE_PARITY.md`
- `dev/CURSES_UI_FILE_LOADING_FIX.md`

**Details:**
CURSES_UI_FEATURE_PARITY.md has a 'Known Issues to Check' section that mentions checking curses UI line formatting and statement highlighting, but doesn't reference the CURSES_UI_FILE_LOADING_FIX.md which documents a major fix to how lines are synced from ProgramManager to the editor. The file loading fix is directly relevant to the 'Line Number Formatting and Statement Highlighting' issue described.

---

### inconsistent_status

**Description:** Phase 2 marked complete but Phase 3 testing not started

**Affected files:**
- `dev/CURSES_UI_FEATURE_PARITY.md`

**Details:**
Phase 2 tasks (2.1-2.3) are marked '✅ Completed', but Phase 3 task '2.4 Test both step modes' is marked '⬜ Not Started'. Additionally, all Phase 3 testing tasks (3.1-3.6) are marked '⬜ Not Started', which suggests the features may not have been fully tested despite being marked as implemented.

---

### terminology_inconsistency

**Description:** Inconsistent naming for stepping commands

**Affected files:**
- `dev/CURSES_VS_TK_GAP_ANALYSIS.md`
- `dev/DEBUGGER_UI_RESEARCH.md`

**Details:**
CURSES_VS_TK_GAP_ANALYSIS.md uses 'Step Line' and 'Step Statement' consistently. DEBUGGER_UI_RESEARCH.md uses 'Step Line', 'Step Stmt', 'Step Statement', and 'Stmt' interchangeably without clear standardization.

---

### success_rate_inconsistency

**Description:** Minor inconsistency in success rate improvement calculation

**Affected files:**
- `dev/DATA_STATEMENT_FIX.md`

**Details:**
The document states 'Total improvement on cleaned corpus: 17.4% → 22.6% (+5.2%)' but the actual difference is 5.2 percentage points, which is correctly stated. However, earlier it shows the baseline as 17.4% with 41 files, but the table shows 'Corpus cleaned | 17.4% | 41 | baseline' without clarifying what 'cleaned' means in relation to the 235 file corpus.

---

### date_inconsistency

**Description:** Implementation date mismatch for DEF FN feature

**Affected files:**
- `dev/DEF_FN_IMPLEMENTATION.md`
- `dev/DEF_FN_SYNTAX_RULES.md`

**Details:**
DEF_FN_IMPLEMENTATION.md states 'Implementation Date: 2025-10-22' while DEF_FN_SYNTAX_RULES.md states 'Date: 2025-10-27'. These appear to be related to the same feature but have different dates.

---

### terminology_inconsistency

**Description:** Inconsistent capitalization of 'Claude Code'

**Affected files:**
- `dev/DEVELOPER_GUIDE_INDEX.md`
- `dev/DEBUG_MODE.md`

**Details:**
DEBUG_MODE.md uses 'Claude Code' (capitalized) throughout, while this is a general debugging feature not specific to any particular tool. The terminology suggests it's a specific product when it's actually a general debug mode.

---

### missing_reference

**Description:** References non-existent file

**Affected files:**
- `dev/DEVELOPER_GUIDE_INDEX.md`

**Details:**
DEVELOPER_GUIDE_INDEX.md references 'WORK_IN_PROGRESS.md' with note '(if exists)', suggesting uncertainty about whether this file exists. This creates ambiguity in the documentation structure.

---

### date_format_inconsistency

**Description:** Inconsistent date formats used across documentation

**Affected files:**
- `dev/DEVELOPER_GUIDE_INDEX.md`
- `dev/EDITOR_FIXES_2025_10_30.md`
- `dev/ELSE_KEYWORD_FIX.md`

**Details:**
DEVELOPER_GUIDE_INDEX.md uses 'Last Updated: 2025-10-30', EDITOR_FIXES_2025_10_30.md uses '2025-10-30' in title, ELSE_KEYWORD_FIX.md uses 'Implementation Date: 2025-10-22'. Multiple date formats (YYYY-MM-DD vs spelled out) are used inconsistently.

---

### path_inconsistency

**Description:** Inconsistent path references for utility scripts

**Affected files:**
- `dev/DEVELOPER_GUIDE_INDEX.md`
- `dev/DETOKENIZER_FIXES.md`

**Details:**
DEVELOPER_GUIDE_INDEX.md states 'See `utils/UTILITY_SCRIPTS_INDEX.md` in the repository' but DETOKENIZER_FIXES.md references 'utils/detokenizer.py' without mentioning the index file. The existence and location of UTILITY_SCRIPTS_INDEX.md is unclear.

---

### version_number_mismatch

**Description:** Document references version v1.0.135 as 'Current Status' but also states the fix was in v1.0.103 (October 28, 2025), creating a temporal inconsistency with the date being in the future

**Affected files:**
- `dev/GITHUB_DOCS_WORKFLOW_EXPLAINED.md`

**Details:**
Document states 'Current Status (v1.0.135)' and 'Fixed in v1.0.103 (October 28, 2025)' - the date October 28, 2025 is in the future, likely meant to be 2024

---

### implementation_date_inconsistency

**Description:** FILE_IO_IMPLEMENTATION.md states implementation date as 2025-10-22, while FILESYSTEM_SECURITY.md states 2025-10-25, but both appear to be future dates

**Affected files:**
- `dev/FILE_IO_IMPLEMENTATION.md`
- `dev/FILESYSTEM_SECURITY.md`

**Details:**
FILE_IO_IMPLEMENTATION.md: 'Implementation Date: 2025-10-22', FILESYSTEM_SECURITY.md: 'Date: 2025-10-25'

---

### feature_tracking_reference

**Description:** Document references 'docs/dev/UI_FEATURE_PARITY_TRACKING.md' multiple times but this file is not included in the provided documentation set for verification

**Affected files:**
- `dev/FEATURE_COMPLETION_REQUIREMENTS.md`

**Details:**
Multiple references to 'docs/dev/UI_FEATURE_PARITY_TRACKING.md' throughout FEATURE_COMPLETION_REQUIREMENTS.md, including: 'Added to docs/dev/UI_FEATURE_PARITY_TRACKING.md with status for ALL UIs', 'Add to feature tracking (docs/dev/UI_FEATURE_PARITY_TRACKING.md)'

---

### file_reference_inconsistency

**Description:** Document references 'docs/dev/ALL_FEATURES_CANONICAL_NAMES.txt' but this file is not included in the provided documentation set for verification

**Affected files:**
- `dev/FEATURE_COMPLETION_REQUIREMENTS.md`

**Details:**
Multiple references including: 'Added to docs/dev/ALL_FEATURES_CANONICAL_NAMES.txt', 'Add to canonical list (docs/dev/ALL_FEATURES_CANONICAL_NAMES.txt)'

---

### terminology_inconsistency

**Description:** Inconsistent naming of Tkinter UI - referred to as both 'TK' and 'Tkinter' across documents

**Affected files:**
- `dev/FEATURE_COMPLETION_REQUIREMENTS.md`
- `dev/FUNCTION_KEY_REMOVAL.md`

**Details:**
FEATURE_COMPLETION_REQUIREMENTS.md uses 'TK', FUNCTIONAL_TESTING_METHODOLOGY.md uses 'Tkinter' in test plans

---

### date_inconsistency

**Description:** Test date is in the future

**Affected files:**
- `dev/GOSUB_STACK_TEST_RESULTS.md`

**Details:**
GOSUB_STACK_TEST_RESULTS.md shows 'Test Date: 2025-10-25' which is a future date, likely should be 2024-10-25

---

### date_inconsistency

**Description:** Implementation date is in the future

**Affected files:**
- `dev/HELP_BUILD_TIME_INDEXES.md`

**Details:**
HELP_BUILD_TIME_INDEXES.md shows 'Date: 2025-10-27' which is a future date, likely should be 2024-10-27

---

### date_inconsistency

**Description:** Implementation date is in the future

**Affected files:**
- `dev/HASH_FILE_IO_FIX.md`

**Details:**
HASH_FILE_IO_FIX.md shows 'Implementation Date: 2025-10-22' which is a future date, likely should be 2024-10-22

---

### missing_cross_reference

**Description:** Missing backward reference to options document

**Affected files:**
- `dev/HELP_BUILD_TIME_INDEXES.md`
- `dev/HELP_INDEXING_OPTIONS.md`

**Details:**
HELP_BUILD_TIME_INDEXES.md references HELP_INDEXING_SPECIFICATION.md and other docs in 'See Also' section, but does not reference HELP_INDEXING_OPTIONS.md which discusses the decision-making process that led to the implemented solution. This would provide useful context for understanding why the front matter approach was chosen.

---

### date_inconsistency

**Description:** Impossible future date in document header

**Affected files:**
- `dev/HELP_INDEXING_SPECIFICATION.md`

**Details:**
HELP_INDEXING_SPECIFICATION.md has 'Date: 2025-10-25' which is in the future. This appears to be a typo (should likely be 2024-10-25 or 2023-10-25).

---

### missing_reference

**Description:** Visual UI mentioned in specification but not in integration document

**Affected files:**
- `dev/HELP_INDEXING_SPECIFICATION.md`
- `dev/HELP_INTEGRATION_PER_CLIENT.md`

**Details:**
HELP_INDEXING_SPECIFICATION.md mentions 'ui: String # cli|curses|tk|visual' in the front matter schema, but HELP_INTEGRATION_PER_CLIENT.md only covers CLI, Curses, and Tkinter clients. The 'visual' UI is not documented in the integration guide.

---

### inconsistent_terminology

**Description:** Inconsistent naming for Tkinter UI

**Affected files:**
- `dev/HELP_INDEXING_SPECIFICATION.md`
- `dev/HELP_INTEGRATION_PER_CLIENT.md`

**Details:**
HELP_INDEXING_SPECIFICATION.md uses 'tk' in the ui field example, while HELP_INTEGRATION_PER_CLIENT.md uses both 'tk' (in paths like 'ui/tk/index.md') and 'Tkinter' (in headings like '### Tkinter Client Integration'). The front matter schema should clarify if 'tk' or 'tkinter' is the canonical value.

---

### feature_availability_conflict

**Description:** Explicit context syntax mentioned but not fully implemented

**Affected files:**
- `dev/HELP_INDEXING_SPECIFICATION.md`
- `dev/HELP_INTEGRATION_PER_CLIENT.md`

**Details:**
HELP_INTEGRATION_PER_CLIENT.md mentions 'Explicit context syntax: "language:statements/print.md"' with a '(future)' note in the navigate_to() method, but this feature is not mentioned in HELP_INDEXING_SPECIFICATION.md's implementation plan or front matter schema.

---

### inconsistent_count

**Description:** Different statement and function counts in different contexts

**Affected files:**
- `dev/HELP_INDEXING_SPECIFICATION.md`
- `dev/HELP_INTEGRATION_PER_CLIENT.md`

**Details:**
Both documents consistently mention '63 statements' and '40 functions', but HELP_INDEXING_SPECIFICATION.md's categorization guide lists specific categories without confirming the total count matches 63 statements. This is a minor consistency check issue rather than a direct contradiction.

---

### file_count_inconsistency

**Description:** Different total file counts reported

**Affected files:**
- `dev/HELP_MIGRATION_STATUS.md`
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_MIGRATION_STATUS.md states 'Total help files: 110+' (40 functions + 63 statements + 3 appendices + 2 conceptual + indices). HELP_SYSTEM_COMPLETION.md states 'Total files: 125 documentation files' without clear breakdown matching the 110+ count.

---

### keyword_count_inconsistency

**Description:** Inconsistent keyword counts within same document

**Affected files:**
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_SYSTEM_COMPLETION.md states 'Searchable keywords: Comprehensive keyword indexing across all tiers' and later '177 keywords' for Language Index, '28 keywords' for MBASIC Index, '37 keywords' for UI Index (total 242). However, 'Quality Metrics' section shows 'Total keywords: 78' before enhancement and '242' after, but doesn't clarify if 78 was the sum across all indexes or just one.

---

### file_count_detail_inconsistency

**Description:** Search index file counts don't sum to total documentation files

**Affected files:**
- `dev/HELP_SYSTEM_COMPLETION.md`

**Details:**
HELP_SYSTEM_COMPLETION.md states '108 files indexed' (Language) + '4 files indexed' (MBASIC) + '7 files indexed' (UI) = 119 files, but earlier states 'Total files: 125 documentation files', leaving 6 files unaccounted for in search indexes.

---

### file_count_inconsistency

**Description:** Discrepancy in language reference file counts

**Affected files:**
- `dev/HELP_SYSTEM_DIAGRAM.md`
- `dev/HELP_SYSTEM_REORGANIZATION.md`

**Details:**
HELP_SYSTEM_DIAGRAM.md states '40 functions' and '63 statements' in multiple places. HELP_SYSTEM_REORGANIZATION.md also mentions '40 function references' and '63 statement references' in the Tier 1 structure, but later states 'common/language/functions/ # 40 files' and 'common/language/statements/ # 63 files' in the current structure problems section, and then shows 'language/functions/ # 2 files (duplicates?)' in the orphaned directory, suggesting inconsistent file counts.

---

### link_syntax_inconsistency

**Description:** Inconsistent recommendations for cross-tier link syntax

**Affected files:**
- `dev/HELP_SYSTEM_DIAGRAM.md`
- `dev/HELP_SYSTEM_REORGANIZATION.md`
- `dev/HELP_SYSTEM_WEB_DEPLOYMENT.md`

**Details:**
HELP_SYSTEM_DIAGRAM.md shows explicit context syntax in examples: 'language:statements/print.md' and 'mbasic:getting-started.md'. HELP_SYSTEM_REORGANIZATION.md presents this as an open question: 'Should we use explicit context syntax (language:functions/print.md) or relative paths (../../language/functions/print.md)?' with pros/cons listed. HELP_SYSTEM_WEB_DEPLOYMENT.md recommends 'Keep using relative paths for now (works everywhere)' and marks explicit context as 'future', contradicting the DIAGRAM.md examples.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for BASIC language version

**Affected files:**
- `dev/HELP_SYSTEM_DIAGRAM.md`
- `dev/HELP_SYSTEM_REORGANIZATION.md`

**Details:**
HELP_SYSTEM_DIAGRAM.md consistently uses 'BASIC-80' when referring to the language reference (e.g., 'BASIC-80 Language Reference', 'BASIC-80 language documentation'). HELP_SYSTEM_REORGANIZATION.md uses both 'BASIC-80' and 'MBASIC 5.21' interchangeably when describing the same content, such as 'Pure BASIC-80 specification' and 'MBASIC 5.21 manual content' in the same section, creating potential confusion about whether these are the same or different.

---

### terminology_inconsistency

**Description:** Inconsistent capitalization of state names

**Affected files:**
- `dev/IMMEDIATE_MODE_DESIGN.md`
- `dev/IMMEDIATE_MODE_SAFETY.md`

**Details:**
IMMEDIATE_MODE_DESIGN.md uses lowercase state names in quotes: 'idle', 'paused', 'at_breakpoint', 'done', 'error', 'running', 'waiting_for_input'. IMMEDIATE_MODE_SAFETY.md uses the same lowercase format consistently. However, the formatting in tables varies slightly - this is minor but worth noting for consistency.

---

### ui_integration_inconsistency

**Description:** Different UI integration approaches for similar features

**Affected files:**
- `dev/IMMEDIATE_MODE_DESIGN.md`
- `dev/INDENT_COMMAND_DESIGN.md`

**Details:**
IMMEDIATE_MODE_DESIGN.md proposes keyboard shortcuts for Curses UI (Ctrl+I, Ctrl+L) and always-visible panels for Tk/Web UIs. INDENT_COMMAND_DESIGN.md proposes menu items for Tk/Web ('Edit menu → Auto-Indent') but keyboard shortcut for Curses (Ctrl+I). The design philosophy differs - immediate mode emphasizes always-visible UI elements while INDENT uses menu-based access for graphical UIs.

---

### missing_reference

**Description:** INSTALLATION_TESTING_TODO.md references setup.py but INSTALLATION_FOR_DEVELOPERS.md doesn't mention it

**Affected files:**
- `dev/INSTALLATION_FOR_DEVELOPERS.md`
- `dev/INSTALLATION_TESTING_TODO.md`

**Details:**
INSTALLATION_TESTING_TODO.md lists 'setup.py - Package configuration' under Related section, but INSTALLATION_FOR_DEVELOPERS.md doesn't document setup.py or mention package installation via pip

---

### inconsistent_terminology

**Description:** Inconsistent formatting of success rate improvements

**Affected files:**
- `dev/INKEY_LPRINT_IMPLEMENTATION.md`
- `dev/INPUT_HASH_FIX.md`

**Details:**
INKEY_LPRINT_IMPLEMENTATION.md uses '+3.5%' while INPUT_HASH_FIX.md uses '+0.4%' - both are correct but formatting style differs slightly in presentation

---

### version_reference

**Description:** Python version requirements mentioned twice with slightly different wording

**Affected files:**
- `dev/INSTALLATION_FOR_DEVELOPERS.md`

**Details:**
System Requirements states 'Python: 3.8 or later (3.9+ recommended)' while Install System Dependencies section just shows 'python3' without version specification

---

### version_mismatch

**Description:** Unusual version number format

**Affected files:**
- `dev/KEYWORD_CASE_SCOPE_ANALYSIS.md`

**Details:**
KEYWORD_CASE_SCOPE_ANALYSIS.md lists 'Version: 1.0.153' which is an unusually high patch number. This may indicate a different versioning scheme or could be an error.

---

### terminology_inconsistency

**Description:** Different terminology used for the same UI backends

**Affected files:**
- `dev/OPTIONAL_DEPENDENCIES_STRATEGY.md`
- `dev/PACKAGE_DEPENDENCIES.md`

**Details:**
OPTIONAL_DEPENDENCIES_STRATEGY.md refers to 'curses backend' and 'tk backend', while PACKAGE_DEPENDENCIES.md mentions 'Curses' and 'Web' (nicegui) but doesn't mention tk explicitly in the placeholder list.

---

### version_number_inconsistency

**Description:** Version number in example may not match actual project version

**Affected files:**
- `dev/OPTIONAL_DEPENDENCIES_STRATEGY.md`

**Details:**
Document shows 'version = "1.0.116"' in pyproject.toml example, but this specific version number is not validated against other documentation.

---

### missing_reference

**Description:** Reference to non-existent document

**Affected files:**
- `dev/PC_CLEANUP_REMAINING.md`

**Details:**
PC_CLEANUP_REMAINING.md mentions 'see CALLSTACK_UI_PC_ENHANCEMENT_TODO.md' under 'UI Integration' section, but this file is not included in the provided documentation set.

---

### implementation_status_inconsistency

**Description:** Implementation phases marked complete but document shows mixed status

**Affected files:**
- `dev/RESOURCE_LIMITS_DESIGN.md`

**Details:**
Document header shows 'Status: ✅ IMPLEMENTED (2025-10-26)' and all phases are marked with checkmarks (✅), but the document is titled as a 'DESIGN' document rather than an implementation report. The checkmarks suggest completion but the document structure is forward-looking ('Proposed Solution', 'Implementation Plan').

---

### terminology_inconsistency

**Description:** Command name inconsistency in reporting feature

**Affected files:**
- `dev/RESOURCE_LIMITS_DESIGN.md`

**Details:**
Phase 4 mentions 'Add `LIMITS` command to show resource usage (renamed from SYSTEM to avoid conflict)' but earlier in the document under 'Benefits' section it refers to 'Users can see `SYSTEM` report of usage'. This suggests the command was renamed but the document wasn't fully updated.

---

### missing_cross_reference

**Description:** Resource limits testing not mentioned in test inventory

**Affected files:**
- `dev/README_TESTS_INVENTORY.md`
- `dev/RESOURCE_LIMITS_DESIGN.md`

**Details:**
RESOURCE_LIMITS_DESIGN.md mentions '11 tests in tests/test_resource_limits.py' and '8 tests in tests/test_interpreter_limits.py' (total 19 tests), but these are not listed in the comprehensive test inventory in README_TESTS_INVENTORY.md which claims to provide a 'comprehensive inventory of the actual test suite'.

---

### file_count_inconsistency

**Description:** Incomplete enumeration of BASIC test programs

**Affected files:**
- `dev/README_TESTS_INVENTORY.md`

**Details:**
Under 'BASIC Test Programs (basic/dev/bas_tests/)' section, items 20-26 are listed as '_(Additional GOSUB stack tests)_' and items 38-64 are listed as '_(Various other BASIC programs for comprehensive testing)_' without actual file names, despite claiming to be a comprehensive inventory. The document states 'Total: 64 BASIC test programs' but only explicitly lists 37 files.

---

### version_number_gap

**Description:** Version numbering sequence has unexplained gap

**Affected files:**
- `dev/SESSION_2025_10_28_SUMMARY.md`
- `dev/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md`

**Details:**
SESSION_2025_10_28_SUMMARY.md shows versions v1.0.103 through v1.0.114 (October 28, 2025). SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md (October 26, 2025) does not mention any version numbers. Given October 26 is before October 28, there should be version numbers before v1.0.103, but they are not documented in the October 26 session.

---

### commit_count_mismatch

**Description:** Different commit counts for same date

**Affected files:**
- `dev/SESSION_2025_10_26.md`
- `dev/SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md`

**Details:**
SESSION_2025_10_26.md lists '4 Git Commits' with specific commit hashes (8bdb23e, 7c143f9, c0bb98e, 5c84ae3). SESSION_SUMMARY_2025_WEB_UI_AND_HIGHLIGHTING.md lists '17 commits' for the same date (2025-10-26). These cannot both be accurate for the same date.

---

### path_inconsistency

**Description:** Inconsistent path references to testing documentation location

**Affected files:**
- `dev/TESTING_GUIDE.md`
- `dev/TEST_COVERAGE_MATRIX.md`

**Details:**
TESTING_GUIDE.md references 'docs/dev/LANGUAGE_TESTING_TODO.md' while TEST_COVERAGE_MATRIX.md references both 'docs/dev/INTERACTIVE_COMMAND_TEST_COVERAGE.md' and 'docs/history/LANGUAGE_TESTING_DONE.md'. The 'docs/' prefix is inconsistent with the file location 'dev/' shown in the file headers.

---

### documentation_completeness

**Description:** TESTING_GUIDE.md is marked as placeholder but other testing documentation exists

**Affected files:**
- `dev/TESTING_GUIDE.md`

**Details:**
TESTING_GUIDE.md states 'Status: PLACEHOLDER - Documentation in progress' and 'This documentation is planned but not yet written', but comprehensive testing documentation already exists in TEST_COVERAGE_MATRIX.md and is referenced in STATUS.md. The placeholder status appears outdated.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for program execution control features

**Affected files:**
- `dev/STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md`
- `dev/STATUS.md`

**Details:**
STATEMENT_HIGHLIGHTING_IMPLEMENTATION.md uses terms like 'Ctrl+C Breakpoint', 'Statement-Level Stepping', and 'tick(mode='step_statement')'. STATUS.md uses 'Break handling (Ctrl+C)', 'STOP/CONT', but doesn't mention 'stepping' or 'tick modes'. The terminology for similar debugging features differs between documents.

---

### feature_status_conflict

**Description:** Document shows all features complete but uses future-tense language in some sections

**Affected files:**
- `dev/TK_UI_CHANGES_FOR_OTHER_UIS.md`

**Details:**
Status Summary table shows all features as '✅ Implemented and working' with '100% Complete', but earlier sections use language like 'What Other UIs Need to Implement' and 'What Other UIs Need to Verify' suggesting work is still pending

---

### path_inconsistency

**Description:** Inconsistent path format for BASIC test files

**Affected files:**
- `dev/TEST_INVENTORY.md`

**Details:**
TEST_INVENTORY.md proposes moving BASIC files to 'basic/bas_tests/' but earlier mentions 'basic/dev/bas_tests/' in the test run results context

---

### feature_availability_conflict

**Description:** Enhancement plan lists delete line and renumber commands as missing but audit shows they exist

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN lists '❌ Delete line command (Ctrl+D)' and '❌ Renumber command (Ctrl+E)' as missing. AUDIT section 13.1 shows 'cmd_delete(args)' and 'cmd_renum(args)' are implemented command methods.

---

### inconsistent_terminology

**Description:** Different color specifications for statement highlighting

**Affected files:**
- `dev/TK_UI_ENHANCEMENT_PLAN.md`
- `dev/TK_UI_FEATURE_AUDIT.md`

**Details:**
PLAN specifies 'cyan background for active statement'. AUDIT section 4.4 specifies 'Yellow background (#ffeb3b)' for statement highlighting.

---

### feature_status_conflict

**Description:** Conflicting information about Find/Replace in Tk UI

**Affected files:**
- `dev/UI_FEATURE_PARITY.md`
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
UI_FEATURE_PARITY.md shows 'Find & Replace | ❌ | ❌ | ⚠️ Not documented | ❌ | ❌' for Tk, but UI_FEATURE_PARITY_TRACKING.md shows 'Find/Replace | [❌|❓|⚡] | [❌|❓|⚡] | [✅|📄|⚡] | [❌|❓|⚡]' indicating Tk has it, and notes 'Tk implemented 2025-10-29'

---

### date_inconsistency

**Description:** Inconsistent last updated dates within same document

**Affected files:**
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
Document header shows 'Last Updated: 2025-10-30' but footer shows 'Last Updated: 2024-10-29' and 'User-Facing Feature Comparison (2024-10-29)' section header

---

### feature_status_conflict

**Description:** Conflicting information about Settings Dialog in CLI

**Affected files:**
- `dev/UI_FEATURE_PARITY_CHECKLIST.md`
- `dev/UI_FEATURE_PARITY_TRACKING.md`

**Details:**
UI_FEATURE_PARITY_CHECKLIST.md does not list Settings Dialog for CLI, but UI_FEATURE_PARITY_TRACKING.md shows 'Settings Dialog | [✅|📄|🧪]' for CLI with note 'All UIs tested 2025-10-30. CLI via SHOWSETTINGS/SETSETTING'

---

### ui_name_inconsistency

**Description:** Inconsistent naming of the curses-based UI

**Affected files:**
- `dev/URWID_COMPLETION.md`
- `dev/VARIABLE_EDITING_STANDARDIZATION.md`
- `dev/VARIABLE_EDITING_STATUS.md`

**Details:**
URWID_COMPLETION.md refers to 'urwid-based curses UI' and 'urwid UI' throughout. VARIABLE_EDITING_STANDARDIZATION.md and VARIABLE_EDITING_STATUS.md consistently refer to it as 'Curses' or 'Curses UI' without mentioning urwid. This could cause confusion about whether these are the same UI or different implementations.

---

### error_formatting_reference_inconsistency

**Description:** Missing cross-references to error handling in other UI documentation

**Affected files:**
- `dev/UI_HELPERS_GUIDE.md`

**Details:**
UI_HELPERS_GUIDE.md extensively documents error formatting functions (format_error_message, format_syntax_error, etc.) and shows integration examples for CLI, Tk, Web, and Curses UIs. However, none of the other documentation files (URWID_COMPLETION.md, VARIABLE_EDITING_*.md) reference these standardized error formatting utilities when discussing error handling, suggesting potential inconsistency in error display across UIs.

---

### column_position_terminology

**Description:** Inconsistent column indexing documentation

**Affected files:**
- `dev/UI_HELPERS_GUIDE.md`

**Details:**
UI_HELPERS_GUIDE.md states 'column - Column position (1-indexed, absolute) (optional)' for format_error_message, but the get_relative_column and get_absolute_column functions don't explicitly state whether their parameters are 0-indexed or 1-indexed, though examples suggest 1-indexed. This could lead to off-by-one errors in implementation.

---

### terminology_inconsistency

**Description:** Inconsistent capitalization of 'debugger' in compound terms

**Affected files:**
- `dev/VARIABLE_TRACKING.md`
- `dev/VARIABLE_TRACKING_CHANGES.md`

**Details:**
VARIABLE_TRACKING.md uses 'debugger-initiated', 'debugger-modified', and 'debugger-set' (with hyphens), while VARIABLE_TRACKING_CHANGES.md uses 'debugger_set' (with underscore) when referring to the parameter name. Both are technically correct in their contexts, but the mixed usage could cause confusion.

---

### reference_inconsistency

**Description:** Reference to non-existent documentation file

**Affected files:**
- `dev/VISUAL_UI_EDITOR_ENHANCEMENT.md`

**Details:**
The document references 'CURSES_UI_FEATURE_PARITY.md' multiple times ('See also: CURSES_UI_FEATURE_PARITY.md'), but this file is not included in the provided documentation set, making it impossible to verify cross-references.

---

### reference_inconsistency

**Description:** Reference to non-existent documentation file

**Affected files:**
- `dev/VISUAL_UI_EDITOR_ENHANCEMENT.md`

**Details:**
The document references 'TK_UI_ENHANCEMENT_PLAN.md' in the status section ('see TK_UI_ENHANCEMENT_PLAN.md'), but this file is not included in the provided documentation set.

---

### file_path_inconsistency

**Description:** Different file paths referenced for the same web UI implementation

**Affected files:**
- `dev/WEB_UI_EDITOR_ENHANCEMENTS.md`
- `dev/WEB_UI_IMPLEMENTATION.md`
- `dev/WEB_UI_FEATURE_PARITY.md`

**Details:**
WEB_UI_EDITOR_ENHANCEMENTS.md references 'src/ui/web/web_ui.py', WEB_UI_IMPLEMENTATION.md also references 'src/ui/web/web_ui.py', but WEB_UI_FEATURE_PARITY.md references 'src/ui/web/nicegui_backend.py' and WEB_UI_FIXES documents reference 'src/ui/web/nicegui_backend.py'. Unclear if these are the same file renamed or different files.

---

### date_inconsistency

**Description:** Document dates suggest impossible timeline

**Affected files:**
- `dev/WEB_UI_FEATURE_PARITY.md`
- `dev/WEB_UI_FIXES_2025_10_30.md`

**Details:**
WEB_UI_FEATURE_PARITY.md is dated '2025-10-28' and WEB_UI_FIXES_2025_10_30.md is dated '2025-10-30', but both dates are in the future (documents appear to be from 2024 based on context)

---

### version_mismatch

**Description:** WEB_UI_REAL_OPTIONS.md has a future date (2025-10-25) while WORK_IN_PROGRESS.md references version 1.0.376+ with date 2025-11-01

**Affected files:**
- `dev/WEB_UI_REAL_OPTIONS.md`
- `dev/WORK_IN_PROGRESS.md`

**Details:**
WEB_UI_REAL_OPTIONS.md: '**Date**: 2025-10-25' vs WORK_IN_PROGRESS.md: '**Last Updated:** 2025-11-01 v1.0.376'

---

### architectural_inconsistency

**Description:** WEB_UI_REAL_OPTIONS.md proposes WebIOHandler class, but WORK_IN_PROGRESS.md shows different architecture with program_manager and AST-based approach

**Affected files:**
- `dev/WEB_UI_REAL_OPTIONS.md`
- `dev/WORK_IN_PROGRESS.md`

**Details:**
WEB_UI_REAL_OPTIONS.md: 'class WebIOHandler(IOHandler)' vs WORK_IN_PROGRESS.md: 'Interpreter has self.program_manager reference' and 'AST is source of truth, text is just a view/cache'

---

### file_path_inconsistency

**Description:** Different file paths referenced for web UI implementation

**Affected files:**
- `dev/WEB_UI_REAL_OPTIONS.md`
- `dev/WORK_IN_PROGRESS.md`

**Details:**
WEB_UI_REAL_OPTIONS.md: 'src/ui/web/web_ui.py' vs WORK_IN_PROGRESS.md: 'src/ui/web/nicegui_backend.py'

---

### testing_status_conflict

**Description:** WEB_UI_TESTING_CHECKLIST.md says testing is TODO pending stable UI, but WEB_UI_VERIFICATION_RESULTS.md shows detailed verification already performed

**Affected files:**
- `dev/WEB_UI_TESTING_CHECKLIST.md`
- `dev/WEB_UI_VERIFICATION_RESULTS.md`

**Details:**
WEB_UI_TESTING_CHECKLIST.md: '**Status** **TODO** - Test when web UI menus and features are stable' vs WEB_UI_VERIFICATION_RESULTS.md: '## Date: 2025-10-26' with detailed test results and fixes

---

### inconsistent_terminology

**Description:** Inconsistent key command descriptions

**Affected files:**
- `dev/archive/DEBUGGER_COMMANDS.md`
- `dev/archive/CONTINUE_FEATURE.md`
- `dev/archive/BREAKPOINT_DISPLAY_FIX.md`

**Details:**
DEBUGGER_COMMANDS.md and CONTINUE_FEATURE.md list 'e' as 'End' command, but BREAKPOINT_DISPLAY_FIX.md uses 'end' in lowercase in status messages. Also, some docs say 'Press c' while others say 'Press 'c'' with quotes.

---

### missing_reference

**Description:** Conflicting information about Ctrl+P shortcut functionality

**Affected files:**
- `dev/archive/HELP_SYSTEM_SUMMARY.md`
- `dev/archive/HELP_MENU_STATUS.md`

**Details:**
HELP_SYSTEM_SUMMARY.md lists '**^P** (Ctrl+P) - Open help from anywhere in the editor' as a working feature and states 'Automated tests confirm: ✓ Help opens with ^P'. However, HELP_MENU_STATUS.md notes 'The ^P shortcut mentioned in the help message doesn't work because npyscreen doesn't route Ctrl+P to the help handler when in the main editor widget. Only menu-based help access works.'

---

### inconsistent_file_references

**Description:** Different line number references for same code

**Affected files:**
- `dev/archive/CONTINUE_IMPLEMENTATION.md`
- `dev/archive/BREAKPOINT_DISPLAY_FIX.md`

**Details:**
CONTINUE_IMPLEMENTATION.md references 'src/ui/curses_ui.py (lines 443-504)' for _breakpoint_hit() method, while BREAKPOINT_DISPLAY_FIX.md references both 'src/ui/curses_ui.py:443-504' (Before) and 'src/ui/curses_ui.py:443-529' (After), suggesting the code changed but CONTINUE_IMPLEMENTATION.md wasn't updated.

---

### file_reference

**Description:** References to test files that may not exist

**Affected files:**
- `dev/archive/IMPLEMENTATION_SUMMARY.md`

**Details:**
Document mentions 'tests/test_urwid_ui.py' and 'tests/hello_test.bas' as new files created, but these are not confirmed to exist in the file structure shown.

---

### ui_backend_naming

**Description:** Inconsistent UI backend naming convention

**Affected files:**
- `dev/archive/IMPLEMENTATION_SUMMARY.md`

**Details:**
Document uses both '--ui curses' and '--ui=curses' (with equals sign) interchangeably. In DISTRIBUTION_TESTING.md, the format '--ui=cli' is consistently used with equals sign.

---

### documentation_location

**Description:** Referenced documentation files not listed in index

**Affected files:**
- `dev/archive/IMPLEMENTATION_SUMMARY.md`
- `dev/index.md`

**Details:**
IMPLEMENTATION_SUMMARY.md references 'docs/URWID_UI.md' and 'docs/dev/URWID_MIGRATION.md' but these are not listed in the dev/index.md comprehensive file listing.

---

### command_inconsistency

**Description:** Inconsistent command format for running mbasic

**Affected files:**
- `dev/archive/IMPLEMENTATION_SUMMARY.md`
- `future/DISTRIBUTION_TESTING.md`

**Details:**
IMPLEMENTATION_SUMMARY.md shows 'python3 mbasic' while DISTRIBUTION_TESTING.md shows 'mbasic' (as installed command). Both are valid but context differs - one is running from source, other from installed package.

---

### file_path

**Description:** Both documents reference modifying src/ui/curses_ui.py but for different purposes

**Affected files:**
- `dev/archive/MOUSE_BREAKPOINT_IMPLEMENTATION.md`
- `dev/archive/MENU_CHANGES.md`

**Details:**
MOUSE_BREAKPOINT_IMPLEMENTATION.md adds mouse support to curses_ui.py, while MENU_CHANGES.md modifies menu structure in curses_ui.py. If IMPLEMENTATION_SUMMARY.md is correct that curses_ui.py was renamed to curses_npyscreen.py and a new urwid-based curses_ui.py was created, these documents may be referring to different files or different points in time.

---

### keyboard_shortcut

**Description:** Keyboard shortcut conflict noted but not resolved

**Affected files:**
- `dev/archive/MENU_CHANGES.md`

**Details:**
Document states 'Ctrl+L - Load (note: conflicts with List, but Load dialog appears first)' indicating an unresolved keyboard shortcut conflict between Load and List commands.

---

### test_file_reference

**Description:** References to test_continue.bas file without confirmation of existence

**Affected files:**
- `dev/archive/SIMPLE_TEST.md`
- `dev/archive/test_bp_ui_debug.md`

**Details:**
Multiple archive documents reference 'test_continue.bas' and 'demo_continue.bas' as test files, but these are not confirmed to exist in the documented file structure.

---

### documentation_organization

**Description:** Archive documents not properly categorized in index

**Affected files:**
- `dev/index.md`

**Details:**
The dev/index.md lists archive/ subdirectory documents at the end but doesn't explain that these are archived/historical documents, which could cause confusion about current vs. historical implementation status.

---

### missing_ui_reference

**Description:** Web UI documentation structure mentioned but not consistently referenced

**Affected files:**
- `help/README.md`
- `help/common/getting-started.md`
- `future/GTK_WARNING_SUPPRESSION_TODO.md`

**Details:**
help/README.md lists '/ui/visual - Visual Backend Help' but getting-started.md doesn't mention visual UI in the 'See your UI-specific help' section, only listing 'Curses UI', 'Tkinter UI', and 'CLI'. GTK_WARNING_SUPPRESSION_TODO.md mentions 'web backend' and 'web UI' but help/README.md doesn't have a '/ui/web' section listed, only '/ui/visual'.

---

### terminology_inconsistency

**Description:** Inconsistent naming for web-based UI

**Affected files:**
- `help/README.md`
- `future/GTK_WARNING_SUPPRESSION_TODO.md`

**Details:**
GTK_WARNING_SUPPRESSION_TODO.md refers to 'web backend', 'web UI', and 'nicegui_backend.py', while help/README.md refers to it as 'Visual Backend'. The terminology should be consistent - either 'web', 'visual', or 'NiceGUI'.

---

### missing_reference

**Description:** Getting started references UI help that may not exist

**Affected files:**
- `help/common/getting-started.md`
- `help/README.md`

**Details:**
getting-started.md says 'See your UI-specific help for how to type programs' and lists links to '[Tkinter UI](ui/tk/index.md)' and '[CLI](ui/cli/index.md)', but help/README.md shows these paths as '/ui/tk' and '/ui/cli' without confirming index.md files exist at those locations.

---

### command_inconsistency

**Description:** Different keyboard shortcuts listed for help

**Affected files:**
- `help/common/editor-commands.md`
- `help/common/index.md`

**Details:**
editor-commands.md states 'F1 or H - Open help', while index.md states '^P - Show this help'. These appear to be different commands for the same function, which may be UI-specific but isn't clarified.

---

### path_inconsistency

**Description:** Inconsistent documentation path references

**Affected files:**
- `future/PYPI_DISTRIBUTION.md`
- `future/SIMPLE_DISTRIBUTION_APPROACH.md`

**Details:**
PYPI_DISTRIBUTION.md refers to 'docs/future/DISTRIBUTION_TESTING.md' and 'docs/future/SIMPLE_DISTRIBUTION_APPROACH.md', but the actual files are in 'future/' directory, not 'docs/future/'. This suggests either the files moved or the documentation references are outdated.

---

### inconsistent_syntax_formatting

**Description:** Inconsistent spacing in syntax declarations

**Affected files:**
- `help/common/language/functions/abs.md`
- `help/common/language/functions/asc.md`
- `help/common/language/functions/cos.md`

**Details:**
abs.md uses 'ASS (X)' with space before parenthesis, asc.md uses 'ASC (X$)' with space, while cos.md uses 'COS (X)' with space. Some other functions use no space.

---

### inconsistent_version_information

**Description:** Duplicate version listing in COS function

**Affected files:**
- `help/common/language/functions/atn.md`
- `help/common/language/functions/cos.md`

**Details:**
cos.md shows 'Versions: SK, Extended, Disk Extended, Disk' with 'Extended, Disk' appearing twice, while atn.md shows 'Versions: SK, Extended, Disk' without duplication.

---

### missing_cross_reference

**Description:** RIGHT$ See Also section references non-existent MID$ statement file

**Affected files:**
- `help/common/language/functions/right_dollar.md`

**Details:**
RIGHT$ includes '[MID$](../statements/mid_dollar.md)' in See Also, but MID$ is a function, not a statement. The correct reference should be to the function file or to the MID$ Assignment statement.

---

### inconsistent_syntax_format

**Description:** INT function has inconsistent syntax format in header

**Affected files:**
- `help/common/language/functions/int.md`

**Details:**
INT shows 'INT (X) Versions,: 8K, Extended, Disk' with unusual comma placement and spacing, unlike other functions which use consistent 'Versions:' or 'Versionsr' format.

---

### typo_in_version_label

**Description:** HEX$ has typo in version label

**Affected files:**
- `help/common/language/functions/hex_dollar.md`

**Details:**
Shows 'Versionsr Extended, Disk' instead of 'Versions: Extended, Disk' - appears to be a typo with 'r' instead of ':'.

---

### inconsistent_see_also_lists

**Description:** String function 'See Also' sections have identical lists but are not consistently ordered

**Affected files:**
- `help/common/language/functions/spc.md`
- `help/common/language/functions/str_dollar.md`
- `help/common/language/functions/string_dollar.md`
- `help/common/language/functions/val.md`

**Details:**
Files spc.md, str_dollar.md, string_dollar.md, and val.md all reference the same set of string functions in their 'See Also' sections (ASC, CHR$, HEX$, INSTR, LEFT$, LEN, MID$, MID$ Assignment, OCT$, RIGHT$, SPACE$, SPC, STR$, STRING$, VAL), but the order varies slightly between documents.

---

### example_formatting_inconsistency

**Description:** SPC example output appears malformed with '~ERE' instead of 'THERE'

**Affected files:**
- `help/common/language/functions/spc.md`

**Details:**
In spc.md Example section: 'PRINT "OVER" SPC(15) "THERE"
 OVER ~ERE' - the output shows '~ERE' instead of expected 'THERE', suggesting a typo or encoding issue.

---

### inconsistent_example_formatting

**Description:** STR$ example has malformed syntax with double closing parentheses

**Affected files:**
- `help/common/language/functions/str_dollar.md`

**Details:**
In str_dollar.md Example: '20 ON LEN(STR$(N» GOSUB 30,100,200,300,400,500' - uses '»' instead of proper closing parenthesis ')'

---

### incomplete_example

**Description:** STR$ example is incomplete and lacks explanation

**Affected files:**
- `help/common/language/functions/str_dollar.md`

**Details:**
The example in str_dollar.md shows lines 5-20 but doesn't include the subroutines at lines 30, 100, 200, 300, 400, 500 that are referenced, making it incomplete. Also includes 'Also see the VAL function.' as part of the example code block instead of in See Also section.

---

### metadata_inconsistency

**Description:** STR$ has 'related' field in frontmatter while other functions use 'See Also' section

**Affected files:**
- `help/common/language/functions/str_dollar.md`

**Details:**
str_dollar.md frontmatter includes 'related: ['val', 'print-using', 'left_dollar', 'right_dollar']' field, which is not present in other function documentation files that use the 'See Also' section instead.

---

### version_information_inconsistency

**Description:** CLOAD and CSAVE have inconsistent version information

**Affected files:**
- `help/common/language/statements/cload.md`
- `help/common/language/statements/csave.md`

**Details:**
cload.md has no version information in frontmatter, while csave.md specifies '**Versions:** 8K (cassette), Extended (cassette)'. Both should have consistent version documentation.

---

### inconsistent_see_also_lists

**Description:** CLOAD and CSAVE have identical but differently ordered 'See Also' sections

**Affected files:**
- `help/common/language/statements/cload.md`
- `help/common/language/statements/csave.md`

**Details:**
Both files reference the same set of functions/statements (COBL, CRR$, CSAVE/CLOAD, CVI/CVS/CVD, DEFINT/SNG/DBL/STR, ERR AND ERL, INPUT#, LINE INPUT, LPRINT, MKI$/MKS$/MKD$, SPACES, TAB) but in different orders.

---

### missing_example

**Description:** CLOSE statement example references external documentation

**Affected files:**
- `help/common/language/statements/close.md`

**Details:**
close.md Example section states 'See PART II, Chapter 3, MBASIC Disk I/O, of the MBASIC User's Guide.' instead of providing an inline example like other statements.

---

### inconsistent_terminology

**Description:** Inconsistent capitalization of 'BASIC' vs 'BASIC-80' vs 'BASIC-SO'

**Affected files:**
- `help/common/language/statements/def-fn.md`
- `help/common/language/statements/dim.md`
- `help/common/language/statements/erase.md`

**Details:**
def-fn.md uses 'BASIC-80' consistently. dim.md uses 'BASIC-SO' in example. defint-sng-dbl-str.md uses 'BASIC-SO'. inputi.md uses 'BASIC-SO' and 'BASIC-aO'. This appears to be OCR errors ('SO' and 'aO' instead of '80').

---

### formatting_inconsistency

**Description:** Inconsistent example formatting and indentation

**Affected files:**
- `help/common/language/statements/defint-sng-dbl-str.md`
- `help/common/language/statements/delete.md`
- `help/common/language/statements/erase.md`

**Details:**
defint-sng-dbl-str.md has poorly formatted examples with inconsistent indentation and mixed inline comments. delete.md has clean examples with consistent formatting. erase.md has clean examples. The quality of example formatting varies significantly across documents.

---

### inconsistent_see_also_sections

**Description:** See Also sections have inconsistent relevance and completeness

**Affected files:**
- `help/common/language/statements/def-fn.md`
- `help/common/language/statements/dim.md`
- `help/common/language/statements/erase.md`
- `help/common/language/statements/end.md`

**Details:**
def-fn.md has no 'See Also' section despite discussing related concepts like variable types and functions. dim.md has 2 relevant related commands. erase.md has 2 relevant related commands. end.md has 8 related commands including some tangentially related ones like CLEAR and SYSTEM. The criteria for inclusion in 'See Also' appears inconsistent.

---

### metadata_inconsistency

**Description:** Some documents have category 'NEEDS_CATEGORIZATION' while others are properly categorized

**Affected files:**
- `help/common/language/statements/defint-sng-dbl-str.md`
- `help/common/language/statements/err-erl-variables.md`

**Details:**
defint-sng-dbl-str.md has 'category: NEEDS_CATEGORIZATION'. err-erl-variables.md has 'category: NEEDS_CATEGORIZATION' and 'description: NEEDS_DESCRIPTION'. Other documents like def-fn.md have proper categories like 'functions', 'arrays', 'editing', etc.

---

### inconsistent_example_formatting

**Description:** Inconsistent formatting and spacing in example code blocks

**Affected files:**
- `help/common/language/statements/kill.md`
- `help/common/language/statements/let.md`
- `help/common/language/statements/list.md`
- `help/common/language/statements/print.md`

**Details:**
kill.md shows '200 KILL RDATA1R' with 'See also Appendix B.' on same line. let.md has inconsistent spacing ('110 LET 0=12' vs '110   D=12'). list.md mixes format descriptions with examples. print.md has extensive unformatted example content.

---

### inconsistent_version_notation

**Description:** Inconsistent notation for version information

**Affected files:**
- `help/common/language/statements/list.md`
- `help/common/language/statements/on-gosub-on-goto.md`

**Details:**
list.md uses 'Format 2: LIST [<line number>[-[<line number>]]] Extended, Disk' mixing format and version info. on-gosub-on-goto.md uses '**Versions:** SK, Extended, Disk' in proper format.

---

### inconsistent_see_also_references

**Description:** Some files have extensive See Also sections while related files have minimal references

**Affected files:**
- `help/common/language/statements/limits.md`
- `help/common/language/statements/line-input.md`
- `help/common/language/statements/lprint-lprint-using.md`

**Details:**
limits.md has 12 See Also references, line-input.md has 10, lprint-lprint-using.md has 10, while simpler commands like kill.md only have 4. The selection criteria appears inconsistent.

---

### inconsistent_metadata

**Description:** Inconsistent use of 'related' vs 'See Also' in frontmatter

**Affected files:**
- `help/common/language/statements/mid-assignment.md`
- `help/common/language/statements/lset.md`

**Details:**
mid-assignment.md uses 'related: [...]' in YAML frontmatter, while lset.md and most others only use 'See Also' sections in the body. This creates inconsistent cross-referencing.

---

### reference_format_inconsistency

**Description:** Inconsistent formatting of cross-references in example sections

**Affected files:**
- `help/common/language/statements/kill.md`
- `help/common/language/statements/line-input.md`

**Details:**
kill.md shows 'See also Appendix B.' inline with code. line-input.md shows 'See Example, Section 2.32, LINE INPUT#.' These reference formats don't match the markdown link style used in See Also sections.

---

### missing_cross_references

**Description:** RENUM documentation states it updates RESTORE statements, but RESTORE documentation doesn't mention RENUM

**Affected files:**
- `help/common/language/statements/renum.md`
- `help/common/language/statements/restore.md`

**Details:**
RENUM.md: 'RENUM automatically updates line number references in: ... RESTORE line_number'. However, RESTORE.md's 'See Also' section only lists DATA and READ, not RENUM.

---

### inconsistent_version_information

**Description:** Inconsistent version notation format

**Affected files:**
- `help/common/language/statements/restore.md`
- `help/common/language/statements/swap.md`

**Details:**
RESTORE.md uses 'SK, Extended, Disk' while SWAP.md uses 'EXtended, Disk' (with capital X in middle of word). Should be consistent capitalization.

---

### incomplete_cross_references

**Description:** RESUME documentation mentions ON ERROR GOTO but RUN doesn't mention error handling reset behavior

**Affected files:**
- `help/common/language/statements/resume.md`
- `help/common/language/statements/run.md`

**Details:**
RESUME.md extensively documents error handling with ON ERROR GOTO. RUN.md states 'All open files are closed' and clears various states, but doesn't explicitly mention that error handlers are also cleared/reset when RUN executes.

---

### inconsistent_terminology

**Description:** Inconsistent description of PUT statement purpose

**Affected files:**
- `help/common/language/statements/put.md`
- `help/common/language/statements/rset.md`

**Details:**
PUT.md description: 'To write a record from   a   random   buffer   to   a random. disk file.' (has extra spaces and incomplete sentence ending with 'random.'). RSET.md correctly describes it as 'random file I/O operations' without the formatting issues.

---

### documentation_quality

**Description:** Example output formatting inconsistency

**Affected files:**
- `help/common/language/statements/randomize.md`

**Details:**
The RANDOMIZE example shows user input inline with prompt like 'Random Number Seed (-32768    to 32767)? 3     (user types 3)' with excessive spacing and parenthetical notes that are inconsistent with other examples in the documentation set.

---

### missing_related_links

**Description:** RESUME references error codes appendix that isn't linked in See Also

**Affected files:**
- `help/common/language/statements/resume.md`

**Details:**
RESUME.md states 'See [Error Codes](../appendices/error-codes.md) for complete list' in the body text, but this link doesn't appear in the 'See Also' section where it would be more discoverable.

---

### inconsistent_terminology

**Description:** Inconsistent syntax notation for optional parameters

**Affected files:**
- `help/common/language/statements/write.md`
- `help/common/language/statements/writei.md`

**Details:**
write.md uses 'WRITE[<list of expressions»' with closing bracket notation, while writei.md uses 'WRITE #<file number>, <list of expressions>' with standard angle brackets. The syntax notation style should be consistent.

---

### missing_reference

**Description:** WRITE # documentation references WRITE statement but doesn't link to it

**Affected files:**
- `help/common/language/statements/writei.md`

**Details:**
writei.md mentions 'Unlike PRINT #, WRITE # formats the data' but doesn't include write.md in the See Also section, only printi-printi-using.md and print.md

---

### missing_reference

**Description:** Main index doesn't reference settings system

**Affected files:**
- `help/index.md`
- `help/common/settings.md`

**Details:**
help/index.md provides comprehensive navigation but doesn't mention the settings system documented in help/common/settings.md, which is a major feature with SHOWSETTINGS and SETSETTING commands.

---

### missing_reference

**Description:** Shortcuts documentation doesn't specify which UI it applies to

**Affected files:**
- `help/common/shortcuts.md`

**Details:**
help/common/shortcuts.md describes keyboard shortcuts but doesn't clarify if these apply to all UIs or just specific ones (appears to be Curses-specific based on content like 'Mouse click' for breakpoints and menu navigation).

---

### inconsistent_terminology

**Description:** Inconsistent capitalization of 'Ok' prompt

**Affected files:**
- `help/common/ui/cli/index.md`
- `help/common/ui/tk/index.md`
- `help/common/ui/curses/editing.md`

**Details:**
cli/index.md consistently uses 'Ok' while other documentation sometimes uses 'OK'. The prompt should be consistently capitalized.

---

### outdated_information

**Description:** Architecture document references future compilation as 'planned' but doesn't clarify current status

**Affected files:**
- `help/mbasic/architecture.md`

**Details:**
The document says 'Status: Current Implementation: ✅ Interpreter (fully functional), Semantic Analyzer: ✅ Complete (18 optimizations), Code Generation: ❌ Not implemented (future work)' but uses language like 'Planned Pipeline' and 'Potential Targets' without clarifying if this is actively being developed or just theoretical.

---

### inconsistent_terminology

**Description:** Inconsistent naming of the project/implementation

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/extensions.md`
- `help/mbasic/index.md`

**Details:**
compatibility.md uses 'MBASIC-2025' and states 'This interpreter provides **100% compatibility**'. extensions.md says 'This is **MBASIC-2025**' and lists 'Project Names Under Consideration: MBASIC-2025, Visual MBASIC 5.21, MBASIC++, MBASIC-X'. index.md refers to it as 'MBASIC 5.21 interpreter implementation' and 'MBASIC-80 (MBASIC) version 5.21 for CP/M'. The project name appears to be undecided.

---

### missing_reference

**Description:** compatibility.md references extensions.md for modern extensions, but not-implemented.md is not cross-referenced

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/not-implemented.md`

**Details:**
compatibility.md states 'See [Extensions Guide](extensions.md) for complete details' about modern extensions, but does not reference not-implemented.md which covers features not in MBASIC 5.21. These two documents are complementary but not cross-linked.

---

### inconsistent_feature_list

**Description:** Debugging features listed differently in features.md vs extensions.md

**Affected files:**
- `help/mbasic/features.md`
- `help/mbasic/extensions.md`

**Details:**
features.md lists debugging features as 'TRON/TROFF, Breakpoints (UI-dependent), Step execution (UI-dependent), Variable watch (UI-dependent), Stack viewer (UI-dependent)'. extensions.md lists 'BREAK, STEP, WATCH, STACK' as CLI-only commands. The relationship between these two lists is unclear.

---

### contradictory_information

**Description:** Inconsistent description of PEEK behavior

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/features.md`

**Details:**
compatibility.md states 'PEEK: Returns random integer 0-255 (for RNG seeding compatibility)' and 'PEEK does NOT return values written by POKE'. features.md lists 'PEEK, POKE - Memory access (emulated)' without clarifying the random return behavior or the lack of POKE/PEEK interaction.

---

### feature_documentation_conflict

**Description:** Function key usage inconsistency

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/keyboard-commands.md`

**Details:**
In feature-reference.md and other docs, function keys (F2, F3, F5) are mentioned for various commands. In keyboard-commands.md, there's a note: 'No function keys required! All commands use Ctrl or regular keys.' This creates confusion about whether function keys are supported.

---

### keyboard_shortcut_missing

**Description:** Help key binding inconsistency

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In keyboard-commands.md: 'Ctrl+P' for Open help system. In quick-reference.md: '{{kbd:help}}' (template variable) for Help. In help-navigation.md: '{{kbd:help}}' is used. The actual key binding is unclear.

---

### terminology_inconsistency

**Description:** Inconsistent prompt terminology

**Affected files:**
- `help/ui/cli/debugging.md`
- `help/ui/cli/variables.md`

**Details:**
In cli/debugging.md, the prompt is shown as 'Ready' in examples. In cli/variables.md, it's also 'Ready'. However, in cli/index.md, it's shown as 'Ok'. This creates confusion about the actual CLI prompt.

---

### feature_availability_conflict

**Description:** WATCH command mentioned but not documented

**Affected files:**
- `help/ui/cli/debugging.md`
- `help/ui/cli/variables.md`

**Details:**
In cli/index.md under 'Debugging Commands', 'WATCH - Inspect variables' is listed. However, in cli/debugging.md, there is no WATCH command documented. In cli/variables.md, only PRINT is documented for variable inspection.

---

### cross_reference_inconsistency

**Description:** Inconsistent UI naming in cross-references

**Affected files:**
- `help/ui/cli/find-replace.md`
- `help/ui/curses/find-replace.md`

**Details:**
In cli/find-replace.md: References 'Tk UI' and 'Web UIs'. In curses/find-replace.md: References 'Tk UI' only. The Web UI is not consistently mentioned across find-replace documentation.

---

### feature_count_mismatch

**Description:** Feature count doesn't match listed features

**Affected files:**
- `help/ui/tk/feature-reference.md`

**Details:**
feature-reference.md claims '37 features' in the title, but counting the listed features: File Operations (8) + Execution & Control (6) + Debugging (6) + Variable Inspection (6) + Editor Features (7) = 33 features, not 37. The Help System section lists 4 more features, totaling 37, but this should be clarified in the document structure.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for execution control

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/tk/feature-reference.md`

**Details:**
keyboard-shortcuts.md uses 'Continue (run to next breakpoint or end)' while feature-reference.md uses 'Continue (Ctrl+G): Resume execution after pausing at a breakpoint'. The descriptions differ slightly in scope.

---

### feature_availability_conflict

**Description:** File system capabilities inconsistency

**Affected files:**
- `help/ui/web/features.md`
- `help/ui/web/web-interface.md`

**Details:**
features.md under 'File Operations' mentions 'Open Files: Click to browse, Drag and drop, Recent files list' and 'Save Options: Save to browser, Download as file, Export to GitHub, Share via link'. web-interface.md describes only in-memory filesystem with no mention of GitHub export, sharing via link, or drag-and-drop.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for stepping operations

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/keyboard-shortcuts.md`

**Details:**
getting-started.md uses 'Step Line' and 'Step Stmt' for stepping operations. keyboard-shortcuts.md uses 'Step' for 'execute one statement'. debugging.md uses 'Step Over', 'Step Into', 'Step Out'. Multiple different terms for similar operations creates confusion.

---

### feature_documentation_mismatch

**Description:** Settings dialog features mismatch

**Affected files:**
- `help/ui/web/features.md`
- `help/ui/web/settings.md`

**Details:**
features.md under 'Customization' lists 'Editor Settings: Font size, Font family, Tab size, Line wrapping' and 'Behavior Settings: Auto-save interval, Syntax check delay, Execution speed, Debug options'. settings.md only documents 'Enable auto-numbering' and 'Line number increment' settings, with no mention of font, tab size, auto-save, or other settings.

---

### date_format_inconsistency

**Description:** Inconsistent date formats used across documentation files

**Affected files:**
- `history/100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`
- `history/CALLSTACK_UI_PC_ENHANCEMENT_DONE.md`

**Details:**
File '100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md' uses format '2025-10-29' while 'CALLSTACK_UI_PC_ENHANCEMENT_DONE.md' uses '2025-10-28' and '2025-10-29'. Both are valid ISO 8601 formats, but the year 2025 appears to be a typo as these are historical documents that should be dated 2024 based on the BROKEN_LINKS_REPORT filename showing '2024-10-26'.

---

### file_path_inconsistency

**Description:** Inconsistent references to web UI file paths

**Affected files:**
- `history/100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`
- `history/CALLSTACK_UI_PC_ENHANCEMENT_DONE.md`

**Details:**
100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md references 'src/ui/web/nicegui_backend.py' for Web UI implementation. CALLSTACK_UI_PC_ENHANCEMENT_DONE.md lists both 'src/ui/visual/' and 'src/ui/web/nicegui_backend.py' as separate paths, suggesting potential confusion between 'visual' and 'web' UI backends.

---

### test_count_inconsistency

**Description:** Discrepancy in initial test counts

**Affected files:**
- `history/100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`

**Details:**
Under 'Journey to 100%' section, 'Starting Point' shows 'Initial Coverage: 76.5% (39/51 tests passing)' and 'Initial Failures: 12 tests failing'. However, 39 + 12 = 51, but the final count shows 49 total tests, not 51. The document later states 'After Curses Fix: 91.8% (45/49 passing)' confirming 49 total tests.

---

### terminology_inconsistency

**Description:** Inconsistent naming of Tkinter UI

**Affected files:**
- `history/CALLSTACK_UI_PC_ENHANCEMENT_DONE.md`

**Details:**
Document uses both 'TK UI' and 'Tkinter UI' interchangeably. In Phase 2 it says 'TK UI (src/ui/tk_ui.py)' but in Phase 3 it says 'TK UI' again. The file path suggests 'tk_ui' is the canonical name, but 'Tkinter' is the actual Python library name.

---

### terminology_inconsistency

**Description:** Inconsistent naming of MBASIC compiler product

**Affected files:**
- `history/COMPILER_DESIGN.md`
- `history/COMPILER_VS_INTERPRETER_DIFFERENCES.md`

**Details:**
COMPILER_DESIGN.md refers to 'MBASIC Compiler (BASCOM)' and 'BASCOM/Compiled BASIC' throughout, while COMPILER_VS_INTERPRETER_DIFFERENCES.md consistently uses 'MBASIC Compiler (BASCOM)' in the title but then refers to just 'Compiler' in section headings. Both documents are about the same product but use slightly different naming conventions.

---

### missing_reference

**Description:** References non-existent bad_not521/ directory without context

**Affected files:**
- `history/CURRENT_FAILURE_ANALYSIS.md`

**Details:**
CURRENT_FAILURE_ANALYSIS.md repeatedly mentions moving files to 'bad_not521/' directory (e.g., 'Action: MOVE to bad_not521/'), but this directory structure is not explained or referenced in any other documentation file. The purpose and organization of this directory is unclear.

---

### version_reference_inconsistency

**Description:** Inconsistent version references for MBASIC

**Affected files:**
- `history/COMPILER_DESIGN.md`
- `history/COMPILER_VS_INTERPRETER_DIFFERENCES.md`

**Details:**
COMPILER_DESIGN.md references 'BASIC-80 (MBASIC) Reference Manual Version 5.21' and mentions 'MBASIC 5.21 syntax' in lexer notes, while COMPILER_VS_INTERPRETER_DIFFERENCES.md refers to 'MBASIC-80 5.x Interpreter' (using 5.x instead of specific 5.21). Both should consistently reference the same version.

---

### date_inconsistency

**Description:** Inconsistent date format usage

**Affected files:**
- `history/CURRENT_FAILURE_ANALYSIS.md`
- `history/CURSES_BACKEND_COMPLETE.md`

**Details:**
CURRENT_FAILURE_ANALYSIS.md uses date '2025-10-22' while CURSES_BACKEND_COMPLETE.md uses '2025-10-24'. While these are different dates (which is fine), the year 2025 appears to be incorrect as these are historical documents, suggesting a typo that should be 2024.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for compilation directives

**Affected files:**
- `history/COMPILER_DESIGN.md`
- `history/COMPILER_VS_INTERPRETER_DIFFERENCES.md`

**Details:**
COMPILER_DESIGN.md uses 'Metacommands (Compiler Directives)' as section heading and refers to them as 'metacommands' throughout (e.g., 'REM $STATIC', 'REM $DYNAMIC'). COMPILER_VS_INTERPRETER_DIFFERENCES.md uses 'COMPILATION SWITCHES' and refers to command-line switches (e.g., '/E', '/X', '/D'). While these are different concepts, the relationship between metacommands and switches is not clearly explained.

---

### missing_cross_reference

**Description:** References non-existent documentation files

**Affected files:**
- `history/CURSES_UI_INPUT_CHECK_DONE.md`

**Details:**
CURSES_UI_INPUT_CHECK_DONE.md references 'docs/dev/TK_UI_INPUT_DIALOG_TODO.md' and 'docs/dev/WEB_UI_INPUT_UX_TODO.md' in the Related section, but these files are not included in the provided documentation set. Cannot verify if these files exist or if the references are correct.

---

### status_inconsistency

**Description:** Conflicting completion status claims

**Affected files:**
- `history/DE_NONEIFY_DONE.md`

**Details:**
DE_NONEIFY_DONE.md has title ending in '_DONE' and states '✅ Status: SUBSTANTIALLY COMPLETE (Phases 1-4 done)', but then lists 'Phase 5' and 'Remaining None checks' as 'Deferred to Future', and estimates '6-10 hours total' work remaining. The 'DONE' in filename conflicts with incomplete status.

---

### documentation_location_inconsistency

**Description:** Unclear whether documentation reorganization is reflected in DIRECTORY_STRUCTURE.md

**Affected files:**
- `history/DIRECTORY_STRUCTURE.md`
- `history/DOC_REORGANIZATION_COMPLETE.md`

**Details:**
DOC_REORGANIZATION_COMPLETE.md describes a major reorganization completed on 2025-10-24 with subdirectories (design/, history/, implementation/). DIRECTORY_STRUCTURE.md shows 'doc/' with flat structure listing '*.md files' but doesn't show the subdirectory organization described in the reorganization document.

---

### file_count_progression_inconsistency

**Description:** File count progression doesn't match between plan and completion

**Affected files:**
- `history/DOC_REORGANIZATION_PLAN.md`
- `history/DOC_REORGANIZATION_COMPLETE.md`

**Details:**
DOC_REORGANIZATION_PLAN.md states 'After step 2 (delete redundant): 71 files' and 'After full reorganization (planned): ~50 files in doc/, ~14 in future_compiler/, ~10 in history/'. DOC_REORGANIZATION_COMPLETE.md shows final count as '71 total .md files' with breakdown '26 files (main), 16 files (future_compiler), 10 files (history), 19 files (implementation)' = 71 total, not the ~74 suggested by the plan.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for non-MBASIC files directory

**Affected files:**
- `history/DIRECTORY_STRUCTURE.md`
- `history/DOC_REORGANIZATION_COMPLETE.md`

**Details:**
The directory containing non-MBASIC 5.21 files is referred to as both 'bad_not521' and 'bas_not51' in DIRECTORY_STRUCTURE.md, while DOC_REORGANIZATION_COMPLETE.md doesn't mention this directory at all.

---

### inconsistent_terminology

**Description:** Inconsistent naming of ELSE feature

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`
- `history/FAILURE_CATEGORIZATION_CURRENT.md`

**Details:**
FAILURE_CATEGORIZATION.md: 'ELSE Statement Edge Cases - 11 Files'. FAILURE_CATEGORIZATION_CURRENT.md: 'ELSE Edge Cases - 3 files'. Same feature but different file counts and slightly different naming.

---

### missing_reference

**Description:** Document title says DONE but status says TODO

**Affected files:**
- `history/FIX_MKDOCS_STRICT_MODE_DONE.md`

**Details:**
Filename is 'FIX_MKDOCS_STRICT_MODE_DONE.md' but document header says '⏳ Status: TODO - HIGH PRIORITY'. Inconsistent completion status.

---

### outdated_information

**Description:** Document appears to be superseded by CURRENT version

**Affected files:**
- `history/FAILURE_CATEGORIZATION.md`

**Details:**
FAILURE_CATEGORIZATION.md and FAILURE_CATEGORIZATION_CURRENT.md both claim date 2025-10-22, but CURRENT version has higher success rate (104 vs 92 files) and different file lists, suggesting the non-CURRENT version is outdated despite same date.

---

### version_number_inconsistency

**Description:** Version numbers mentioned don't align with a clear versioning scheme

**Affected files:**
- `history/KEYWORD_CASE_HANDLING_DONE.md`

**Details:**
KEYWORD_CASE_HANDLING_DONE.md mentions versions 'v1.0.122-128', 'v1.0.122', 'v1.0.126-127', 'v1.0.104-105', 'v1.0.106-109', and 'v1.0.89'. These appear to be build/commit numbers rather than semantic versions, but this is inconsistent with the lack of version numbers in other history documents.

---

### file_reference_inconsistency

**Description:** Different file naming conventions for built-in functions module

**Affected files:**
- `history/INTERPRETER_IMPLEMENTATION_2025-10-22.md`
- `history/IMPLEMENTATION_COMPLETE.md`

**Details:**
INTERPRETER_IMPLEMENTATION_2025-10-22.md mentions renaming 'builtins.py' to 'basic_builtins.py' to avoid conflicts, and lists 'src/basic_builtins.py' in the code statistics. However, IMPLEMENTATION_COMPLETE.md's proposed architecture shows 'src/builtins.py' in the file structure, suggesting inconsistent documentation of the actual vs. proposed file names.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for compilation phases

**Affected files:**
- `history/IMPLEMENTATION_COMPLETE.md`
- `history/INTERPRETER_COMPILER_ARCHITECTURE_2025-10-22.md`

**Details:**
IMPLEMENTATION_COMPLETE.md uses 'Phase 1', 'Phase 2', 'Phase 3' to describe Type Rebinding Analysis stages. INTERPRETER_COMPILER_ARCHITECTURE_2025-10-22.md uses 'Phase 1', 'Phase 2', 'Phase 3' to describe Interpreter, Compiler, and Additional Targets development stages. The same phase numbering is used for completely different concepts.

---

### terminology_inconsistency

**Description:** Inconsistent naming convention for string functions with $ suffix

**Affected files:**
- `history/LANGUAGE_CHANGES.md`
- `history/LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md`

**Details:**
LANGUAGE_CHANGES.md discusses the inconsistency: 'Implementation uses `CHR`, docs use `CHR$` (or vice versa)' and asks 'Should we use `STR` or `STR$` in docs?' with recommendation 'Use `STR$` in docs (user-visible), `STR` in implementation'. However, LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md lists functions both ways: 'chr.md' and also mentions 'may exist as `left_dollar.md`', 'right_dollar.md', etc., showing the inconsistency persists in documentation filenames.

---

### feature_list_inconsistency

**Description:** Different categorization of language features between documents

**Affected files:**
- `history/LANGUAGE_CHANGES.md`
- `history/LANGUAGE_TESTING_DONE.md`

**Details:**
LANGUAGE_CHANGES.md lists features in categories like 'Must Implement', 'Should Implement', 'Could Implement' with items like 'Global DEF type statements', 'Static array dimensions', etc. LANGUAGE_TESTING_DONE.md categorizes the same features differently under 'Arithmetic & Math', 'String Operations', 'Variables & Types', etc. Some features appear in one document but not the other, making it unclear which is the authoritative feature list.

---

### timeline_inconsistency

**Description:** Inconsistent date formats and completion markers

**Affected files:**
- `history/LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md`
- `history/LANGUAGE_TESTING_DONE.md`
- `history/LEXER_CLEANUP_DONE.md`

**Details:**
LANGUAGE_DOCUMENTATION_COMPLETION_DONE.md uses 'Status: ✅ DONE (2025-10-29)', LANGUAGE_TESTING_DONE.md uses 'Status: ✅ COMPLETE' with 'Created: 2025-10-30' and 'Completed: 2025-10-31', while LEXER_CLEANUP_DONE.md uses 'Status: ⏳ TODO' with 'Created: 2025-10-29 (v1.0.295)'. The version number is only mentioned in one document, and the status markers are inconsistent (DONE vs COMPLETE vs TODO).

---

### terminology_inconsistency

**Description:** Inconsistent terminology for comment statements: 'REMARK' vs 'REM'

**Affected files:**
- `history/LEXER_ISSUES.md`
- `history/PARSER_SUMMARY.md`

**Details:**
LEXER_ISSUES.md uses 'REMARK' as a separate keyword needing recognition: 'Recognize REMARK as synonym for REM'. PARSER_SUMMARY.md lists 'Comments: REM, REMARK, ')' suggesting both are already implemented

---

### date_inconsistency

**Description:** Document shows completion date as 2025-10-30 but last updated as 2025-10-29

**Affected files:**
- `history/LIBRARY_BROWSER_DONE.md`

**Details:**
Header shows '✅ Status: COMPLETE - Games library fully implemented and integrated (2025-10-30)' but footer shows 'Created: 2025-10-29, Last Updated: 2025-10-29'

---

### feature_list_inconsistency

**Description:** Statement count discrepancy in parser implementation

**Affected files:**
- `history/PARSER_SUMMARY.md`
- `history/PARSER_TEST_RESULTS.md`

**Details:**
PARSER_SUMMARY.md: 'Statement Parsers (17 types)' then lists more than 17 items. PARSER_TEST_RESULTS.md: 'Handles 16 different statement types in real programs'

---

### test_file_reference_inconsistency

**Description:** Test file paths inconsistent within same document

**Affected files:**
- `history/MISSING_OPERATORS_DONE_2025-10-31.md`

**Details:**
Document references both 'basic/dev/tests_with_results/test_eqv_imp.bas' and 'basic/dev/tests_with_results/test_randomize.bas' but also mentions 'tests/mathcomp.bas' and 'basic/mathtest.bas' without the dev/tests_with_results path structure

---

### module_naming_inconsistency

**Description:** Inconsistent references to I/O module naming after rename

**Affected files:**
- `history/PHASE1_IO_ABSTRACTION_PROGRESS.md`
- `history/PHASE4_DYNAMIC_LOADING_PROGRESS.md`

**Details:**
PHASE1 document mentions the module was renamed from 'src/io/' to 'src/iohandler/' (commit 8c2c076), but PHASE4 document references 'ConsoleIOHandler' without clarifying the module path. The rename is documented in Phase 1 but Phase 4 code examples don't consistently show 'from iohandler.console import ConsoleIOHandler'.

---

### phase_numbering_inconsistency

**Description:** Phase 1 mentions deferred stepping/breakpoint support but this feature is never addressed in subsequent phases

**Affected files:**
- `history/PHASE1_IO_ABSTRACTION_PROGRESS.md`
- `history/PHASE2_PROGRAM_MANAGEMENT_PROGRESS.md`
- `history/PHASE3_UI_ABSTRACTION_PROGRESS.md`
- `history/PHASE4_DYNAMIC_LOADING_PROGRESS.md`

**Details:**
PHASE1 document states under 'Deferred to Future Phases': 'Stepping and Breakpoint Support - Add to Interpreter class... Deferred to Phase 2 or 3'. However, Phases 2, 3, and 4 documents never mention implementing this feature, and Phase 4 conclusion states 'All 4 core phases complete' without addressing this deferred item.

---

### terminology_inconsistency

**Description:** Inconsistent capitalization of backend class names in documentation

**Affected files:**
- `history/PHASE3_UI_ABSTRACTION_PROGRESS.md`
- `history/PHASE4_DYNAMIC_LOADING_PROGRESS.md`

**Details:**
PHASE3 uses 'CLIBackend' and 'VisualBackend' consistently, but PHASE4's load_backend() code shows conditional logic: 'backend_class_name = f'{backend_name.upper()}Backend' if backend_name == 'cli' else f'{backend_name.capitalize()}Backend'' which would produce 'CLIBackend' vs 'VisualBackend', suggesting inconsistent naming convention.

---

### version_reference_missing

**Description:** Only PC_OLD_EXECUTION_METHODS document includes version numbers

**Affected files:**
- `history/PC_OLD_EXECUTION_METHODS_DONE.md`
- `history/PHASE1_IO_ABSTRACTION_PROGRESS.md`
- `history/PHASE2_PROGRAM_MANAGEMENT_PROGRESS.md`
- `history/PHASE3_UI_ABSTRACTION_PROGRESS.md`
- `history/PHASE4_DYNAMIC_LOADING_PROGRESS.md`

**Details:**
PC_OLD_EXECUTION_METHODS_DONE.md references 'v1.0.287' and 'v1.0.300' but all Phase documents (1-4) dated 2025-10-24 do not include any version numbers, making it unclear what version the Phase work was completed in.

---

### terminology_inconsistency

**Description:** Inconsistent reference to comment syntax

**Affected files:**
- `history/README.md`
- `history/PRESERVE_ORIGINAL_SPACING_DONE.md`

**Details:**
README.md states 'Comments: REM, REMARK' while PRESERVE_ORIGINAL_SPACING_DONE.md mentions 'Comments: REM keyword or ' apostrophe'. The apostrophe comment syntax is not mentioned in README's feature list.

---

### version_reference_inconsistency

**Description:** Version number mentioned without context in other documents

**Affected files:**
- `history/PRESERVE_ORIGINAL_SPACING_DONE.md`

**Details:**
PRESERVE_ORIGINAL_SPACING_DONE.md mentions 'completed v1.0.85' for TYPE_SUFFIX_SERIALIZATION, but no version numbers are mentioned in README.md or REFACTORING_COMPLETE.md, creating inconsistency in versioning documentation.

---

### date_inconsistency

**Description:** Impossible date in documentation

**Affected files:**
- `history/REFACTORING_COMPLETE.md`

**Details:**
REFACTORING_COMPLETE.md shows '**Date**: 2025-10-24' which is a future date (document appears to be from 2024 or earlier based on context). This is likely a typo for 2024-10-24.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for execution position tracking

**Affected files:**
- `history/SEMANTIC_ANALYSIS_FOR_BASIC_2025-10-22.md`
- `history/SESSION_2025-10-29_PC_REFACTORING.md`

**Details:**
SEMANTIC_ANALYSIS document uses 'line_table' and 'line number table' interchangeably. PC_REFACTORING document refers to 'PC/NPC' (Program Counter/Next Program Counter) but SEMANTIC_ANALYSIS doesn't mention this terminology at all, despite discussing execution flow.

---

### code_reference_inconsistency

**Description:** Inconsistent line count for removed code

**Affected files:**
- `history/SESSION_2025-10-29_IMPROVEMENTS.md`
- `history/SESSION_2025-10-29_PC_REFACTORING.md`

**Details:**
SESSION_2025-10-29_IMPROVEMENTS.md states 'Lines added: ~500+' for improvements. SESSION_2025-10-29_PC_REFACTORING.md states '~308 lines removed' total. Both are from the same date but describe different work, yet the version progression (v1.0.298→v1.0.299→v1.0.300) suggests they're sequential sessions on the same day.

---

### missing_cross_reference

**Description:** Related sessions don't reference each other

**Affected files:**
- `history/SESSION_2025-10-29_IMPROVEMENTS.md`
- `history/SESSION_2025-10-29_PC_REFACTORING.md`

**Details:**
Both documents are dated October 29, 2025 and show sequential version numbers (v1.0.298→v1.0.299 and v1.0.299→v1.0.300), suggesting they're part of the same day's work. However, neither document references the other, and IMPROVEMENTS.md's 'Next Session Recommendations' includes 'PC_OLD_EXECUTION_METHODS_TODO.md' which was actually completed in the PC_REFACTORING session.

---

### feature_status_inconsistency

**Description:** CLI settings commands status unclear

**Affected files:**
- `history/SETTINGS_IMPLEMENTATION_PLAN_DONE.md`
- `history/SESSION_2025_10_28_SETTINGS_AND_CASE_HANDLING.md`

**Details:**
SETTINGS_IMPLEMENTATION_PLAN_DONE states 'CLI has no SETSETTING/SHOWSETTINGS commands' as current status (marked with ❌), but SESSION_2025_10_28 documents that CLI commands were completed in v1.0.104 with 'Added SET "setting.name" value command' and 'Added SHOW SETTINGS ["pattern"]' command.

---

### terminology_inconsistency

**Description:** Inconsistent command naming: SETSETTING vs SET

**Affected files:**
- `history/SETTINGS_IMPLEMENTATION_PLAN_DONE.md`
- `history/SETTINGS_SYSTEM_DONE.md`

**Details:**
SETTINGS_IMPLEMENTATION_PLAN_DONE uses 'SETSETTING' and 'SHOWSETTINGS' as command names in Phase 2 description, while SETTINGS_SYSTEM_DONE uses 'SET' and 'SHOW SETTINGS' in CLI UI examples.

---

### version_reference_inconsistency

**Description:** Version numbers don't align with completion status

**Affected files:**
- `history/SESSION_2025_10_28_SETTINGS_AND_CASE_HANDLING.md`
- `history/SETTINGS_IMPLEMENTATION_PLAN_DONE.md`

**Details:**
SESSION_2025_10_28 shows settings system completed in v1.0.104-105, but SETTINGS_IMPLEMENTATION_PLAN_DONE was marked completed on 2025-10-30 without specific version numbers, creating ambiguity about when features were actually implemented.

---

### scope_inconsistency

**Description:** Setting scope precedence order differs

**Affected files:**
- `history/SESSION_2025_10_28_SETTINGS_AND_CASE_HANDLING.md`
- `history/SETTINGS_SYSTEM_DONE.md`

**Details:**
SESSION_2025_10_28 states 'Scope precedence: file > project > global > default' while SETTINGS_SYSTEM_DONE in SettingsManager.get() comment states 'Check: file -> project -> global -> default'. Both describe the same order but use different notation (> vs ->).

---

### terminology_inconsistency

**Description:** Inconsistent naming for program storage component

**Affected files:**
- `history/SINGLE_SOURCE_OF_TRUTH_DONE.md`
- `history/TIMELINE_NOV_01.md`

**Details:**
SINGLE_SOURCE_OF_TRUTH_DONE.md refers to 'Program Object (self.program)' throughout. TIMELINE_NOV_01.md refers to 'ProgramManager stores lines/ASTs'. It's unclear if these are the same component or different components.

---

### commit_count_inconsistency

**Description:** Session 9 commit count doesn't match stated range

**Affected files:**
- `history/TIMELINE_OCT_23-25.md`

**Details:**
Session 9 header states '43 commits' but the commit range 'c0e9fb8a through ac6d957' would need verification. This is a minor inconsistency as the exact count may vary based on how commits are counted.

---

### feature_status_inconsistency

**Description:** TK UI INPUT dialog feature not mentioned in timeline

**Affected files:**
- `history/TK_UI_INPUT_DIALOG_DONE.md`
- `history/TIMELINE_OCT_28-31.md`

**Details:**
TK_UI_INPUT_DIALOG_DONE.md shows implementation completed in v1.0.173, but TIMELINE_OCT_28-31.md which covers versions up to 1.0.315 does not mention this feature implementation at all. The timeline should include this significant UI change.

---

### documentation_reference_inconsistency

**Description:** Inconsistent documentation file references

**Affected files:**
- `history/TIMELINE_OCT_27-28.md`
- `history/TIMELINE_OCT_28-31.md`

**Details:**
TIMELINE_OCT_27-28.md mentions 'docs/dev/PRETTY_PRINTER_SPACING_TODO.md (NEW - pending)' and 'docs/dev/SINGLE_SOURCE_OF_TRUTH_TODO.md (NEW)'. TIMELINE_OCT_28-31.md mentions 'docs/dev/VARIABLE_SORT_REFACTORING_TODO.md (moved to history)' but doesn't reference the status of the previously mentioned TODO files.

---

### test_results_inconsistency

**Description:** Conflicting test results for case preservation

**Affected files:**
- `history/TIMELINE_OCT_27-28.md`

**Details:**
TIMELINE_OCT_27-28.md Session 2 Part 2 states 'Test results: 9/10 tests passing' for case preservation, but Combined Statistics states 'Case Preservation: ✅ 9/10 unit tests passing' without explaining what the 1 failing test is or if it was later fixed.

---

### ui_count_inconsistency

**Description:** Different number of UIs referenced across documents

**Affected files:**
- `history/TRUE_100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`
- `history/UI_STATUS_FIELD_REMOVAL_DONE.md`

**Details:**
TRUE_100_PERCENT document tests 4 UIs (CLI, Curses, Tkinter, Web) with specific test counts. UI_STATUS_FIELD_REMOVAL document mentions 'other UIs' and lists TK UI, Web UI, and CLI UI as pending, but doesn't mention if Curses changes apply to all 4 UIs or just 3.

---

### terminology_inconsistency

**Description:** Inconsistent naming of Tk/Tkinter UI

**Affected files:**
- `history/TRUE_100_PERCENT_UI_TEST_COVERAGE_ACHIEVED.md`
- `history/VARIABLE_SORT_REFACTORING_DONE.md`

**Details:**
TRUE_100_PERCENT document uses 'Tkinter' (e.g., 'Tkinter (21/21 - 100%)'), while VARIABLE_SORT document uses 'Tk UI' (e.g., 'Refactored Tk UI to Use Common Helper'). Should standardize on one naming convention.

---

### file_path_inconsistency

**Description:** Inconsistent file path references for Web UI

**Affected files:**
- `history/UI_STATUS_FIELD_REMOVAL_DONE.md`
- `history/VARIABLE_SORT_REFACTORING_DONE.md`

**Details:**
UI_STATUS document references 'src/ui/web_ui.py' while VARIABLE_SORT document references 'src/ui/web/nicegui_backend.py'. These appear to be different files or the path structure changed between documents.

---

### completion_date_missing

**Description:** Document marked as DONE but has no completion date

**Affected files:**
- `history/UI_STATUS_FIELD_REMOVAL_DONE.md`

**Details:**
UI_STATUS_FIELD_REMOVAL_DONE.md has no completion date field, unlike VARIABLE_SORT_REFACTORING_DONE.md which has '## Completion Date: 2025-10-31'. If work is complete, should have completion date.

---

### backend_count_inconsistency

**Description:** Inconsistent backend count within same document

**Affected files:**
- `history/VISUAL_BACKENDS_CURSES_TK.md`

**Details:**
VISUAL_BACKENDS_CURSES_TK.md states 'The MBASIC interpreter now supports **4 different UI backends**' in the Available Backends section, listing cli, curses, tk, and visual. However, the Conclusion section also states 'The MBASIC interpreter now supports **4 UI backends**' with the same list. While consistent in count, the document earlier mentions these are 'production-ready' but the 'visual' backend is described as a 'Template for custom backends' and 'Generic stub', which contradicts the production-ready claim.

---

### reference_inconsistency

**Description:** Missing reference document

**Affected files:**
- `history/VISUAL_BACKENDS_CURSES_TK.md`

**Details:**
VISUAL_BACKENDS_CURSES_TK.md References section lists '[REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) - Phases 1-4 completion summary' but this document is not provided in the analysis set. The document is referenced but its existence and content cannot be verified.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for UI components

**Affected files:**
- `history/VISUAL_BACKENDS_CURSES_TK.md`
- `history/VISUAL_UI_REFACTORING_PLAN.md`

**Details:**
VISUAL_UI_REFACTORING_PLAN.md uses 'backends/' directory and refers to 'backend modules', while also using 'src/ui/' for UI implementations. VISUAL_BACKENDS_CURSES_TK.md Phase 4 notes state 'No backends/ directory created - backends live in src/ui/', contradicting the plan's proposed structure that shows both 'src/ui/' and 'backends/' directories.

---

### outdated_information

**Description:** Output buffer limiting shows different version numbers for completion

**Affected files:**
- `history/WEB_UI_MISSING_FEATURES_OLD.md`
- `history/WEB_UI_OUTPUT_IMPROVEMENTS_DONE.md`

**Details:**
WEB_UI_OUTPUT_IMPROVEMENTS_DONE.md states output buffer limiting was completed in 'v1.0.300', but WEB_UI_MISSING_FEATURES_OLD.md is dated '2025-10-28' with 'Current Version: 1.0.176', which predates v1.0.300. This suggests the OLD doc is indeed outdated and doesn't reflect the v1.0.300 improvements.

---

### test_status_inconsistency

**Description:** INPUT statement test status shows different information

**Affected files:**
- `history/WEB_UI_INPUT_UX_DONE.md`
- `history/WEB_UI_MISSING_FEATURES_OLD.md`

**Details:**
WEB_UI_INPUT_UX_DONE.md states 'Test is skipped due to async deadlock issue' and 'Manual testing works'. WEB_UI_MISSING_FEATURES_OLD.md under test results shows '1 test skipped: ⏭️ INPUT statement (async deadlock in test env, works manually)' which is consistent, but also lists under feature #33 'Status: ✅ IMPLEMENTED' with 'Note: Has async deadlock in pytest, but works in manual testing'. The information is consistent but the presentation suggests the OLD doc may have been updated after the INPUT implementation.

---

### date_inconsistency

**Description:** All parser improvement phases dated 2025-10-22, but sessions from 2025-10-25 and 2025-10-27 exist

**Affected files:**
- `history/planning/PHASE1_IMPROVEMENTS_2025-10-22.md`
- `history/planning/PHASE2_IMPROVEMENTS_2025-10-22.md`
- `history/planning/PHASE3_IMPROVEMENTS_2025-10-22.md`
- `history/planning/PHASE4_IMPROVEMENTS_2025-10-22.md`

**Details:**
The four parser improvement phase documents are all dated '2025-10-22', but later session documents are dated '2025-10-25' and '2025-10-27'. This suggests either the parser improvement dates are incorrect, or there's a gap in documentation between 2025-10-22 and 2025-10-25.

---

### feature_status_conflict

**Description:** Conflicting information about search implementation in Curses UI

**Affected files:**
- `history/session_2025-10-25_help_system_keybindings.md`
- `history/session_keybinding_system_implementation.md`

**Details:**
In 'session_2025-10-25_help_system_keybindings.md', the help system features list does not mention search functionality for Curses UI. However, in 'session_keybinding_system_implementation.md', it states: 'Curses UI: Search already implemented from previous session'.

---

### commit_reference_inconsistency

**Description:** Web UI document references specific commit hashes (289682c, 2d3868e) but these cannot be verified against other documents and may be from a different repository or timeline.

**Affected files:**
- `history/session_web_ui_implementation.md`

**Details:**
Web UI doc mentions: 'Commit: 289682c - Add NiceGUI web UI for MBASIC' and 'Commit: 2d3868e - Complete web UI with full debugger'. No other documents reference commits.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for the same concept: 'success rate' vs 'parser success rate' vs 'files parsing'.

**Affected files:**
- `history/sessions/FINAL_SESSION_SUMMARY.md`
- `history/sessions/SESSION_2025-10-22_SUMMARY.md`

**Details:**
Documents use 'success rate', 'parser success rate', 'successfully parsed', and 'files parsing' interchangeably without clear definition of what metric is being measured.

---

### missing_reference

**Description:** Missing bug report link

**Affected files:**
- `library/index.md`

**Details:**
library/index.md states '⚠️ **Important:** These programs have had minimal testing by humans. If you encounter issues, please submit a bug report (link coming soon).' The link is marked as 'coming soon' but should be updated with actual GitHub issues link.

---

### inconsistent_date

**Description:** Incomplete test date in report

**Affected files:**
- `history/snapshots/PARSER_TEST_REPORT_2025-10-22.md`

**Details:**
PARSER_TEST_REPORT_2025-10-22.md footer states '**Test Date**: 2025' without specifying the month/day, while the filename indicates '2025-10-22'.

---

### inconsistent_terminology

**Description:** Inconsistent UI naming conventions

**Affected files:**
- `index.md`
- `library/index.md`

**Details:**
index.md uses 'Curses (terminal), CLI (command-line), Tkinter (GUI), or Web (browser)' while library/index.md uses 'Web/Tkinter UI' and 'CLI' without mentioning Curses UI in the usage instructions.

---

### inconsistent_terminology

**Description:** Inconsistent naming of the Curses UI - referred to as both 'Curses IDE' and 'Urwid/curses UI'

**Affected files:**
- `user/QUICK_REFERENCE.md`
- `user/README.md`

**Details:**
QUICK_REFERENCE.md uses 'MBASIC Curses IDE' while README.md references 'URWID_UI.md' and describes it as 'Urwid/curses UI guide'. The underlying library (urwid) vs the UI name (Curses) creates confusion.

---

### missing_reference

**Description:** README.md lists URWID_UI.md as a content file but this file is not provided in the documentation set

**Affected files:**
- `user/README.md`

**Details:**
README.md states '- **[URWID_UI.md](URWID_UI.md)** - Urwid/curses UI guide' but URWID_UI.md is not included in the provided files.

---

### inconsistent_information

**Description:** Conflicting information about dependencies - INSTALL.md says 'no external dependencies' while CHOOSING_YOUR_UI.md implies urwid is required for Curses UI

**Affected files:**
- `user/INSTALL.md`
- `user/CHOOSING_YOUR_UI.md`

**Details:**
INSTALL.md states 'Since this project has no external dependencies, this step mainly verifies your Python environment is working correctly.' However, CHOOSING_YOUR_UI.md shows 'pip install urwid' as required for Curses UI, and INSTALLATION.md lists 'Optional: urwid (for Curses UI)' and 'Optional: nicegui (for Web UI)'.

---

### missing_reference

**Description:** CASE_HANDLING_GUIDE.md references SETTINGS_AND_CONFIGURATION.md which is not provided

**Affected files:**
- `user/CASE_HANDLING_GUIDE.md`

**Details:**
Under 'See Also' section: '- `SETTINGS_AND_CONFIGURATION.md` - Complete settings reference' but this file is not included in the documentation set.

---

### missing_reference

**Description:** CASE_HANDLING_GUIDE.md references TK_UI_QUICK_START.md which is not provided

**Affected files:**
- `user/CASE_HANDLING_GUIDE.md`

**Details:**
Under 'See Also' section: '- `TK_UI_QUICK_START.md` - Using the graphical interface' but this file is not included in the documentation set.

---

### inconsistent_information

**Description:** Different repository URLs or installation methods suggested

**Affected files:**
- `user/INSTALL.md`
- `user/INSTALLATION.md`

**Details:**
INSTALL.md uses 'git clone https://github.com/avwohl/mbasic.git' while INSTALLATION.md also uses the same URL but presents different installation methods (pip vs from source) as primary options.

---

### feature_description_conflict

**Description:** Smart Insert feature availability unclear

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md extensively documents Smart Insert (Ctrl+I) as a Tk feature. UI_FEATURE_COMPARISON.md lists 'Smart Insert' as 'Tk exclusive feature' with checkmark only for Tk. However, the feature matrix shows it as '❌' for all other UIs without explicitly stating it's Tk-only in the matrix itself, which could be clearer.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for Variables window

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md refers to 'Variables & Resources window (Ctrl+W in TK UI)'. TK_UI_QUICK_START.md uses both 'Variables window' and 'Variables & Resources window' seemingly interchangeably, with different shortcuts (Ctrl+V and Ctrl+W). It's unclear if these are the same window or different windows.

---

### feature_availability_conflict

**Description:** Execution Stack window availability unclear

**Affected files:**
- `user/UI_FEATURE_COMPARISON.md`
- `user/keyboard-shortcuts.md`

**Details:**
keyboard-shortcuts.md (Curses UI) lists 'Menu only' for 'Toggle execution stack window' under both Global Commands and Debugger sections. UI_FEATURE_COMPARISON.md doesn't clearly indicate whether Execution Stack is available in Curses UI, though it shows it's available in CLI, Tk, and Web.

---

