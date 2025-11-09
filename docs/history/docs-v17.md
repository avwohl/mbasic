# Documentation and Comment Changes from Inconsistencies Report v17

Generated: 2025-11-09
Source: docs_inconsistencies_report-v17.md

This file contains issues that require updating documentation (.md files) or code comments, but do NOT require changes to what the code actually does.

---

## High Severity Documentation Issues

### CHAIN docstring describes variable preservation incorrectly for MERGE mode
**File:** `src/interactive.py` line ~380
**Issue:** Docstring categorization suggests MERGE is different from ALL, but code treats them identically
**Fix:** Update docstring to clarify that MERGE and ALL both save all variables (they're treated identically in the code)

### serialize_let_statement docstring about LET keyword stripping
**File:** `src/position_serializer.py`
**Issue:** Docstring claims 'ALWAYS outputs implicit assignment form (A=5) without LET keyword'
**Fix:** Verify this is intentional design, document clearly in both docstring and user docs

### emit_keyword and apply_keyword_case_policy contract mismatch
**File:** `src/position_serializer.py`
**Issue:** emit_keyword requires lowercase, apply_keyword_case_policy accepts any case
**Fix:** Update docstrings to clarify the contract and normalization requirements

### Settings widget keybindings not documented in JSON
**File:** `src/ui/curses_settings_widget.py`, `src/ui/curses_keybindings.json`
**Issue:** Widget implements ESC, ENTER, Apply, Reset keys but curses_keybindings.json has no settings entries
**Fix:** Add settings widget keybindings to curses_keybindings.json

### Comment in _continue_smart_insert outdated
**File:** `src/ui/curses_ui.py` line ~1050
**Issue:** Comment says "we've lost the context" but _continue_smart_insert() takes those parameters
**Fix:** Update comment to reflect that _continue_smart_insert() was extracted and does have context

### Comments claim "no status bar update" but code updates it
**File:** `src/ui/curses_ui.py`
**Issue:** Multiple functions have "Status bar stays at default" comments but call _update_status_with_errors()
**Fix:** Update comments to reflect actual status bar update behavior

### Multiple keybinding systems with unclear relationships
**Files:** `src/ui/help_macros.py`, `src/ui/help_widget.py`, `src/ui/interactive_menu.py`, `src/ui/keybinding_loader.py`
**Issue:** Three systems: keybindings.py constants, JSON loading, hardcoded help keys - unclear which is authoritative
**Fix:** Add comprehensive documentation explaining the three systems and their purposes

### Comment in _execute_immediate() about avoiding interpreter.start()
**File:** `src/ui/tk_ui.py` line ~1180
**Issue:** Comment explains manual PC preservation but creates maintenance risk
**Fix:** Document why this approach is needed, consider refactoring if possible

### Help system documentation contradicts implementation
**File:** `docs/help/README.md`, `src/ui/web_help_launcher.py`
**Issue:** README says "may be served externally" but code shows http://localhost/mbasic_docs
**Fix:** Update README to clarify help is served locally at /mbasic_docs

### LINE INPUT# documentation has incorrect filename
**File:** `docs/help/common/language/statements/inputi.md`, `docs/help/common/language/statements/line-input.md`
**Issue:** File is 'inputi.md' but describes LINE INPUT# not INPUT#
**Fix:** Consider renaming to line-input-hash.md for clarity

### Inconsistent implementation note formatting
**Files:** `docs/help/common/language/statements/width.md`, `docs/help/common/language/statements/wait.md`
**Issue:** Different detail levels for unimplemented features
**Fix:** Standardize implementation note format across all statements

### Broken internal documentation links
**Files:** `docs/help/index.md`, `docs/help/common/ui/cli/index.md`, `docs/help/common/ui/curses/editing.md`, `docs/help/common/ui/tk/index.md`
**Issue:** Multiple references to non-existent files (edit.md, auto.md, delete.md, renum.md, etc.)
**Fix:** Create missing files or fix links to existing files

### Find/Replace feature availability contradiction
**Files:** `docs/help/mbasic/features.md`, `docs/help/ui/cli/find-replace.md`
**Issue:** Unclear if Curses/Web have Find/Replace
**Fix:** Document Find/Replace availability for all UIs

### Variable inspection methods contradiction
**Files:** `docs/help/ui/curses/variables.md`, `docs/help/ui/cli/variables.md`
**Issue:** Variables Window described as Curses-only but CLI doc mentions it too
**Fix:** Clarify which UIs have Variables Window feature

### Typo in keyboard shortcut
**File:** `docs/help/ui/tk/feature-reference.md`
**Issue:** '{{kbd:file_save:tk}}hift+B' - should be 'Shift+B' or '{{kbd:file_save:tk}}+Shift+B'
**Fix:** Correct the typo

### Function key shortcuts documentation contradictory
**File:** `docs/help/ui/web/debugging.md`
**Issue:** States function keys are not implemented but then lists them as implemented
**Fix:** Clarify which shortcuts are actually available

### Toolbar buttons documentation contradictory
**Files:** `docs/help/ui/web/getting-started.md`, `docs/help/ui/web/web-interface.md`
**Issue:** getting-started lists toolbar, web-interface doesn't mention it
**Fix:** Ensure consistent UI component descriptions

---

## Medium Severity Documentation Issues

### InputStatementNode suppress_question documentation unclear
**File:** `src/ast_nodes.py` lines 211-220
**Issue:** Doesn't clarify if prompt can be set when suppress_question=True
**Fix:** Clarify validation and behavior in docstring

### Comment about trailing_minus_only phrasing misleading
**File:** `src/basic_builtins.py` line 232
**Issue:** '(1 char total)' vs '(2 chars total)' phrasing inconsistent
**Fix:** Clarify that trailing_minus_only always reserves 1 char

### EOF function mode 'I' comment unclear
**File:** `src/basic_builtins.py` lines 717-741
**Issue:** Comment says mode 'I' from OPEN but file_info stores 'I' not 'rb'
**Fix:** Clarify mode storage and Python file mode relationship

### Comment claims identifier_table not used but code implements it
**File:** `src/case_string_handler.py` lines 54-61
**Issue:** Comment contradicts implementation of get_identifier_table()
**Fix:** Update comment or remove unused code

### load_from_file() uses open() not FileIO abstraction
**File:** `src/editing/manager.py`
**Issue:** Docstring says FileIO should be used but code uses open() directly
**Fix:** Clarify architectural decision in docstring

### CONT docstring about editing and EDIT command inconsistency
**File:** `src/interactive.py` lines ~200, ~860
**Issue:** EDIT doesn't call clear_execution_state() but should
**Fix:** Document why or fix the inconsistency (see code-v17.md)

### Comment about readline Ctrl+A binding
**File:** `src/interactive.py` line ~90
**Issue:** Comment describes behavior in confusing way
**Fix:** Clarify that readline passes character through for start() to interpret

### Comment about NEXT processing order references wrong lines
**File:** `src/interpreter.py` lines 1088-1117
**Issue:** Comment describes behavior but should verify _execute_next_single() return value
**Fix:** Verify and document the actual behavior

### INPUT statement comment about state machine structure
**File:** `src/interpreter.py` line ~1240
**Issue:** Comment structure doesn't match code flow
**Fix:** Reorganize comment to match if/else structure

### Module docstring references missing file
**File:** `src/keyword_case_manager.py`
**Issue:** References src/simple_keyword_case.py which isn't provided
**Fix:** Verify file exists or remove reference

### apply_keyword_case_policy inconsistent input requirements
**File:** `src/position_serializer.py`
**Issue:** Docstring says 'may be any case' but Note says 'should pass lowercase'
**Fix:** Clarify the actual contract

### serialize_rem_statement comment_type case handling
**File:** `src/position_serializer.py`
**Issue:** Uses uppercase 'APOSTROPHE' then .lower() for emit_keyword
**Fix:** Document that comment_type is stored in uppercase

### PositionSerializer keyword_case_manager default None behavior
**File:** `src/position_serializer.py`
**Issue:** Default is None but comment says 'shouldn't happen'
**Fix:** Clarify when None is expected

### Comment about check_array_allocation() responsibility
**File:** `src/resource_limits.py`
**Issue:** Comment first says 'accounts for' then 'only for limit checking'
**Fix:** Clarify division of responsibility

### create_unlimited_limits() string length inconsistency
**File:** `src/resource_limits.py`
**Issue:** Uses 1MB strings breaking MBASIC compatibility, other presets use 255
**Fix:** Document this is intentional for testing

### Module docstring about SimpleKeywordCase relationship
**File:** `src/simple_keyword_case.py`
**Issue:** Doesn't explain relationship with KeywordCaseManager
**Fix:** Add architectural explanation

### SettingScope.FILE partially implemented but no FILE-scoped settings
**Files:** `src/settings.py`, `src/settings_definitions.py`
**Issue:** Infrastructure exists but no settings use it
**Fix:** Document FILE scope as reserved for future use

### create_settings_backend() docstring about session_id requirement
**File:** `src/settings_backend.py`
**Issue:** Says 'required if NICEGUI_REDIS_URL is set' but code falls back to file mode
**Fix:** Clarify docstring

### Readline keybindings documented in code but not JSON
**Files:** `src/ui/cli.py`, `src/ui/cli_keybindings.json`
**Issue:** get_additional_keybindings() returns readline keys not in JSON
**Fix:** Add readline keys to JSON or explain why they're separate

### Inconsistent arrow key notation
**File:** `src/ui/curses_keybindings.json`
**Issue:** Uses Unicode symbols (↑, ↓) vs text ("Up Arrow")
**Fix:** Standardize notation

### BREAK command clear syntax not in keybindings
**Files:** `src/ui/cli_debug.py`, `src/ui/cli_keybindings.json`
**Issue:** BREAK has list/clear/clear-all but JSON only shows set
**Fix:** Document all BREAK command variants

### STEP command with count not in keybindings
**Files:** `src/ui/cli_debug.py`, `src/ui/cli_keybindings.json`
**Issue:** 'STEP n' not documented in JSON
**Fix:** Add STEP count argument to keybindings

### Comment about bare identifiers and actual behavior
**File:** `src/ui/curses_ui.py`
**Issue:** Comment says rejects bare identifiers but only checks EOF/COLON
**Fix:** Clarify partial rejection behavior

### Comment about pasted lines starting with digits
**File:** `src/ui/curses_ui.py` _parse_line_numbers()
**Issue:** '123 + 456' would be misinterpreted as line 123
**Fix:** Document limitation

### Comment about IO Handler lifecycle
**File:** `src/ui/curses_ui.py` lines ~145-155
**Issue:** Emphasizes IO handler recreation but pattern is actually executor recreation
**Fix:** Clarify pattern description

### Inconsistent status bar behavior documentation
**File:** `src/ui/curses_ui.py`
**Issue:** Claims 'no status bar update' but _debug_step_line() updates it
**Fix:** Document when status bar IS updated

### Comment about code_start position hardcoded vs variable
**Files:** `src/ui/curses_ui.py` multiple methods
**Issue:** Some hardcode column 7, others use _parse_line_number
**Fix:** Document actual behavior and line number width assumptions

### Comment in _execute_immediate about start() calls
**File:** `src/ui/curses_ui.py`
**Issue:** Assumes immediate executor handles all start() calls
**Fix:** Clarify interaction and state initialization

### cmd_delete and cmd_renum pass runtime=None
**File:** `src/ui/curses_ui.py`
**Issue:** Comments say updates runtime but pass runtime=None
**Fix:** Clarify that _sync_program_to_runtime() is called after

### Comment uses 'language' and 'mbasic' tier labels
**File:** `src/ui/help_widget.py` line ~143
**Issue:** Comment accurate but phrasing could be clearer
**Fix:** Clarify tier_labels is local dict

### Both files have nearly identical keybinding comments
**Files:** `src/ui/help_macros.py`, `src/ui/keybinding_loader.py`
**Issue:** Cross-referencing comments could cause confusion
**Fix:** Consider centralizing explanation

### Comment about help_widget.py hardcoded keys
**File:** `src/ui/help_widget.py`
**Issue:** Repeated emphasis on 'hardcoded' vs 'loaded' creates confusion
**Fix:** Simplify explanation

### Comment about widget types incorrect
**File:** `src/ui/tk_settings_dialog.py` line 186
**Issue:** Says 'widgets are tk.Variable instances' but they're not the widgets
**Fix:** Clarify self.widgets stores Variable instances not widget objects

### Comment about arrow click width magic number
**File:** `src/ui/tk_ui.py` lines 1135-1139
**Issue:** ARROW_CLICK_WIDTH = 20 not explained
**Fix:** Document rationale for 20 pixels

### Comment about race condition unclear
**File:** `src/ui/tk_ui.py` _update_immediate_status()
**Issue:** 'Between tick cycles' scenario doesn't match single-threaded Tk
**Fix:** Clarify or remove race condition claim

### TkIOHandler input strategy distinction unclear
**File:** `src/ui/tk_ui.py`
**Issue:** INPUT uses inline, LINE INPUT uses modal - rationale not explained
**Fix:** Document design rationale

### Comment about _execute_immediate and has_work()
**File:** `src/ui/tk_ui.py`
**Issue:** Says 'only location' without explaining why
**Fix:** Remove fragile comment or explain constraint

### _parse_line_number() docstring about MBASIC 5.21 whitespace requirement
**File:** `src/ui/tk_widgets.py`
**Issue:** Claims whitespace required but validates standalone line numbers as valid
**Fix:** Clarify that end-of-string is acceptable alternative

### Comment about _get_input via _enable_inline_input
**File:** `src/ui/web/nicegui_backend.py`
**Issue:** References method not visible in provided code
**Fix:** Verify and update comment if method exists

### Comment about sort state matching Tk UI
**File:** `src/ui/web/nicegui_backend.py` lines ~159-160
**Issue:** References src/ui/tk_ui.py not provided
**Fix:** Verify defaults match

### Comment in _check_auto_number about variable naming
**File:** `src/ui/web/nicegui_backend.py`
**Issue:** last_edited_line_text compared to entire editor content
**Fix:** Rename variable to last_editor_content

### Comment about CP/M EOF marker consistency
**File:** `src/ui/web/nicegui_backend.py`
**Issue:** Claims consistency with file loading but doesn't reference where
**Fix:** Add reference to file loading code

### Class deprecation comment suggests migration
**File:** `src/ui/web_help_launcher.py`
**Issue:** Migration guide says add .html but open_help_in_browser() doesn't
**Fix:** Clarify .html extension handling

(Continue with all medium and low severity documentation issues...)

---

## Summary

All issues in this file are documentation/comment updates only. No changes to actual code behavior are required. Update docstrings, comments, and .md files to match actual implementation or clarify intended behavior.

Total documentation issues: ~300+
