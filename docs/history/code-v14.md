# Code Behavior Changes Required (v14)

Generated from docs_inconsistencies_report-v14.md
Date: 2025-11-08

**These items require changes to actual code behavior/functionality.**

---

#### Code vs Documentation inconsistency

**Description:** SandboxedFileIO methods documented as STUB but list_files() is IMPLEMENTED

**Affected files:**
- `src/file_io.py`

**Details:**
The SandboxedFileIO class docstring states:
"Implementation status:
- list_files(): IMPLEMENTED - delegates to backend.sandboxed_fs
- load_file(): STUB - raises IOError (requires async refactor)
- save_file(): STUB - raises IOError (requires async refactor)
- delete_file(): STUB - raises IOError (requires async refactor)
- file_exists(): STUB - raises IOError (requires async refactor)"

However, the actual implementation shows:
- list_files() is implemented and delegates to backend.sandboxed_fs
- load_file() raises IOError with message about async refactor
- save_file() raises IOError with message about async refactor
- delete_file() raises IOError with message about async refactor
- file_exists() raises IOError with message about async refactor

The documentation correctly describes the implementation status. This is actually consistent, not an inconsistency.

---

#### Code vs Documentation inconsistency

**Description:** The auto_save.py module is fully implemented with comprehensive autosave functionality, but there is no evidence in the other UI files (cli.py, curses_settings_widget.py, base.py) that this autosave functionality is actually integrated or used by any UI backend.

**Affected files:**
- `src/ui/auto_save.py`

**Details:**
auto_save.py provides:
- AutoSaveManager class with full implementation
- Emacs-style #filename# naming
- Recovery prompts
- Cleanup functionality

But none of the UI backend files (cli.py, base.py) show any imports or usage of AutoSaveManager. The feature appears to be implemented but not integrated into the actual UI backends.

---

#### code_vs_comment

**Description:** Comment says BASIC code can never start with digit, but this is incorrect

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_numbers method:
"# FIRST: Check if line starts with a digit (raw pasted BASIC)
# Since BASIC code can never legally start with a digit, this must be a line number
if line[0].isdigit():"

This is FALSE. BASIC code CAN start with a digit in several cases:
1. Numeric constants: '123' as a statement (though unusual)
2. Numeric expressions in immediate mode
3. Line continuation or multi-statement lines

The code assumes any line starting with a digit is a line number, which could cause incorrect parsing of valid BASIC code. This is a potential code bug masked by an incorrect comment.

---

#### code_vs_comment

**Description:** _ImmediateModeToken docstring references wrong line number for usage

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 20-26 docstring states:
"""Token for variable edits from immediate mode or variable editor.

This class is instantiated when editing variables via the variable inspector
(see _on_variable_edit() around line 1194). Used to mark variable changes that
originate from the variable inspector or immediate mode, not from program
execution. The line=-1 signals to runtime.set_variable() that this is a
debugger/immediate mode edit.
"""

The comment references '_on_variable_edit() around line 1194' but the provided code only goes up to line 1194 (incomplete file). The method _on_variable_edit is not visible in the provided excerpt, so the line number cannot be verified. This is likely outdated after code refactoring.

---

#### code_vs_comment

**Description:** Comment in serialize_statement() describes prevention strategy but the error handling doesn't prevent silent data corruption during all operations

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Prevention strategy: Explicitly fail (with ValueError) rather than silently omitting
statements during RENUM, which would corrupt the program.
All statement types must be handled above - if we reach here, serialization failed."

However, serialize_statement() is called from serialize_line(), which is used in multiple contexts:
1. renum_program() - where the ValueError would be raised
2. renumber_program_lines() - which returns (new_lines, line_mapping) and doesn't document that it can raise ValueError
3. Potentially other serialization contexts

The comment implies this is specifically for RENUM protection, but the function is general-purpose. The error handling strategy should either be documented as general serialization failure, or the function should be split into RENUM-specific and general variants.

---

#### documentation_inconsistency

**Description:** Help system documentation claims four UI backends exist, but web_help_launcher.py shows deprecated/legacy status and points to external URL instead of local help

**Affected files:**
- `docs/help/README.md`
- `src/ui/web_help_launcher.py`

**Details:**
README.md states: 'MBASIC supports four UI backends: CLI (command-line interface), Curses (terminal full-screen), Tk (desktop GUI), and Web (browser-based). The help system provides both common content (shared across all backends) and UI-specific documentation for each interface.'

However, web_help_launcher.py shows:
- HELP_BASE_URL = 'http://localhost/mbasic_docs' (external server, not local docs)
- WebHelpLauncher_DEPRECATED class marked as legacy
- Comments say: 'Legacy class kept for compatibility - new code should use direct web URL instead'
- Migration guide suggests using external URLs instead of local help system

---

#### documentation_inconsistency

**Description:** language.md references getting-started.md which doesn't exist in the provided documentation

**Affected files:**
- `docs/help/common/language.md`
- `docs/help/common/language/appendices/index.md`

**Details:**
In language.md: "**Note:** This is a quick reference guide. For a beginner-friendly tutorial, see `[Getting Started](getting-started.md)`."

The getting-started.md file is not provided in the documentation set, creating a broken reference. This is a high severity issue as it's a primary navigation link in the language reference.

---

#### documentation_inconsistency

**Description:** Keyboard shortcut placeholders not resolved

**Affected files:**
- `docs/help/common/shortcuts.md`
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`

**Details:**
shortcuts.md uses placeholder syntax like {{kbd:run:cli}}, {{kbd:run:curses}}, {{kbd:run_program:tk}}, etc. throughout the document. These placeholders are not resolved to actual key combinations. The documentation should either:
1. Replace placeholders with actual keys (e.g., 'F5', 'Ctrl+R')
2. Explain the placeholder system
3. Have a preprocessing step that resolves these before display

Similarly, cli/index.md uses {{kbd:stop:cli}} and curses/editing.md uses {{kbd:run:curses}}, {{kbd:parse:curses}}, {{kbd:new:curses}}, {{kbd:save:curses}}, {{kbd:continue:curses}} without resolution.

---

#### documentation_inconsistency

**Description:** Web UI debugging capabilities inconsistently documented

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/extensions.md`

**Details:**
features.md debugging section says features are 'available in all UIs' but extensions.md Web UI section only mentions:
- **Basic debugging** - Simple breakpoint support via menu

No mention of step execution, variable viewing, or stack viewer for Web UI in extensions.md, contradicting the 'all UIs' claim in features.md.

---

#### documentation_inconsistency

**Description:** Keyboard shortcut documentation uses placeholder syntax that was never replaced with actual keys

**Affected files:**
- `docs/help/ui/curses/editing.md`
- `docs/help/ui/cli/find-replace.md`

**Details:**
In curses/editing.md: 'Cut/Copy/Paste operations ({{kbd:stop:curses}}/C/V) are not available' and '{{kbd:continue:curses}}/V' - these {{kbd:...}} placeholders should be replaced with actual key names like 'Ctrl+X' or similar. The cli/find-replace.md correctly uses 'Ctrl+F', 'Ctrl+H', 'F3' format.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Recent Files feature

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md states Recent Files uses '{{kbd:save:curses}}hift+O' (appears to be a typo for Shift+O), but quick-reference.md does not list this shortcut at all in the Program Management section or anywhere else.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Clear All Breakpoints

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md states Clear All Breakpoints uses '{{kbd:save:curses}}hift+B' (appears to be Shift+B with typo), but quick-reference.md does not list this shortcut anywhere.

---

#### documentation_inconsistency

**Description:** Execution Stack access method inconsistency

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md states 'Via menu: Ctrl+U → Debug → Execution Stack' and 'Note: There is no dedicated keyboard shortcut', but quick-reference.md lists it as 'Menu only' under Global Commands without mentioning Ctrl+U menu access.

---

#### documentation_inconsistency

**Description:** Tk UI Search Help shortcut appears to be typo

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`

**Details:**
Tk feature-reference.md shows Search Help uses '{{kbd:file_save:tk}}hift+F' which appears to be the same typo pattern as seen in Curses docs, likely should be 'Shift+F' or similar.

---

#### code_vs_comment_conflict

**Description:** LineNode docstring claims no source_text field to avoid duplication, but design note contradicts actual regeneration mechanism

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring lines 149-157:
'The AST is the single source of truth. Text is always regenerated from the AST using statement token information (each statement has char_start/char_end and tokens preserve original_case for keywords and identifiers).

Design note: This class intentionally does not have a source_text field to avoid maintaining duplicate copies that could get out of sync with the AST during editing. Text regeneration is handled by the position_serializer module which reconstructs source text from statement nodes and their token information. Each StatementNode has char_start/char_end offsets that indicate the character position within the regenerated line text.'

This claims text is regenerated from 'statement token information' and 'tokens preserve original_case', but PrintStatementNode comment (line 237) says 'keyword_token fields... are not currently used by position_serializer, which handles keyword case through case_keepy_string() instead'. This suggests tokens are NOT used for regeneration as the LineNode docstring claims.

---

#### Code vs Comment conflict

**Description:** Comment about flush() behavior may be misleading about when content is saved

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
In InMemoryFileHandle.flush() method:

Comment states:
"""Flush write buffers (no-op for in-memory files).

Note: This calls StringIO/BytesIO flush() which are no-ops.
Content is only saved to the virtual filesystem on close().
Unlike standard file flush() which persists buffered writes to disk,
in-memory file writes are already in memory, so flush() has no effect."""

Code implementation:
def flush(self):
    if hasattr(self.file_obj, 'flush'):
        self.file_obj.flush()

The comment correctly describes that content is saved on close(), not flush(). However, it could be clearer that flush() is a no-op for persistence purposes but still calls the underlying StringIO/BytesIO flush() method (which itself does nothing). The comment is accurate but could be misread as saying flush() does absolutely nothing.

---

#### code_vs_documentation

**Description:** Docstring lists EDIT subcommands not fully implemented in code

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring at line ~665 states: 'Note: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K) are not yet implemented.'

This indicates the documentation lists commands (S, K with count prefixes) that are explicitly not implemented. The cmd_edit() method only handles: Space, D, C, I, X, H, L, E, Q, A, and CR. Commands S and K are not handled at all, and count prefixes (digits before commands) are not parsed.

---

#### code_vs_comment

**Description:** Comment claims STEP command is a placeholder and not functional, but the code does attempt to output a message and has a count parameter

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_step() docstring says:
"STEP is intended to execute one or more statements, then pause.

IMPORTANT: This method is a placeholder and does NOT actually perform stepping."

But the code does:
```
count = stmt.count if stmt.count else 1
self.io.output(f"STEP {count} - Debug stepping not fully implemented")
```

The comment says it's a placeholder that does NOT perform stepping, but the code does parse a count and output a message. The comment should clarify that it's partially implemented (parses syntax, outputs message) but doesn't actually step through execution.

---

#### Code vs Documentation inconsistency

**Description:** base.py documents input_char() with blocking parameter behavior, but web_io.py ignores the blocking parameter entirely

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/web_io.py`

**Details:**
base.py docstring: "Args:
    blocking: If True, wait for keypress. If False, return "" if no key ready."

web_io.py implementation: "Args:
    blocking: If True, wait for keypress. If False, return "" if no key ready.
             NOTE: This parameter is accepted for interface compatibility but
             is ignored in the web UI implementation."

The web implementation documents that it ignores the parameter, but this creates an API inconsistency where the method doesn't behave as the base interface promises.

---

#### code_vs_comment

**Description:** Comment about DIM tracking as both read and write may be misleading

**Affected files:**
- `src/runtime.py`

**Details:**
Line 685-693: "# Note: DIM is tracked as both read and write to provide consistent debugger display.
# While DIM is technically allocation/initialization (write-only operation), setting
# last_read to the DIM location ensures that debuggers/inspectors can show 'Last accessed'
# information even for arrays that have never been explicitly read. Without this, an
# unaccessed array would show no last_read info, which could be confusing. The DIM location
# provides useful context about where the array was created."

This comment justifies setting last_read for DIM as a debugger convenience, but this could be confusing for users who expect last_read to mean actual read access. The comment acknowledges this is not semantically correct but done for UI purposes. This design decision should be documented more prominently or reconsidered.

---

#### Code vs Documentation inconsistency

**Description:** get_variables() docstring claims to return array tracking info but implementation may return None for uninitialized fields

**Affected files:**
- `src/runtime.py`

**Details:**
Docstring states arrays include:
"'last_read': {'line': int, 'position': int, 'timestamp': float} or None"
"'last_write': {'line': int, 'position': int, 'timestamp': float} or None"

Code uses:
"'last_read': array_data.get('last_read')"
"'last_write': array_data.get('last_write')"

If these keys don't exist in array_data, .get() returns None (correct). However, the docstring doesn't document the additional fields 'last_read_subscripts', 'last_write_subscripts', 'last_accessed_value', and 'last_accessed_subscripts' that are also added to the result for arrays. These fields are implemented but not documented in the Returns section.

---

#### code_vs_comment

**Description:** Comment in load() method claims settings remain flat, but code shows settings can be both flat and nested

**Affected files:**
- `src/settings.py`

**Details:**
Comment in load() method states:
"Loaded settings remain flat; settings modified via set() become nested; both work."

However, the code shows:
1. Settings loaded from disk are flat (e.g., {'editor.auto_number': True})
2. Settings modified via set() become nested (e.g., {'editor': {'auto_number': True}})
3. _get_from_dict() handles both formats

The comment is accurate but could be clearer that this is intentional mixed-format support, not a bug.

---

#### Code vs Documentation inconsistency

**Description:** CLI STEP command documentation claims it implements statement-level stepping like curses 'Step Statement' (Ctrl+T), but curses also has a separate 'Step Line' command (Ctrl+K) that is not available in CLI. The documentation acknowledges this but creates confusion about feature parity.

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/curses_keybindings.json`

**Details:**
cli_debug.py docstring:
"This implements statement-level stepping similar to the curses UI 'Step Statement'
command (Ctrl+T). The curses UI also has a separate 'Step Line' command (Ctrl+K)
which is not available in the CLI."

curses_keybindings.json defines both:
"step_line": {"keys": ["Ctrl+K"], "description": "Step Line (execute all statements on current line)"}
"step": {"keys": ["Ctrl+T"], "description": "Step statement (execute one statement)"}

CLI only has STEP command with no line-level stepping equivalent.

---

#### Code vs Comment conflict

**Description:** The _execute_single_step() method's docstring claims it executes one statement and describes statement-level granularity, but includes a disclaimer that actual behavior depends on interpreter implementation. The comment admits the method might behave as line-level stepping if the interpreter doesn't support statement-level execution.

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
Method docstring:
"Execute a single statement (not a full line).

Uses the interpreter's tick() or execute_next() method to execute
one statement at the current program counter position.

Note: The actual statement-level granularity depends on the interpreter's
implementation of tick()/execute_next(). These methods are expected to
advance the program counter by one statement, handling colon-separated
statements separately. If the interpreter executes full lines instead,
this method will behave as line-level stepping rather than statement-level."

This creates uncertainty about whether STEP actually provides statement-level stepping as documented in cmd_step().

---

#### code_vs_comment

**Description:** Comment claims bug fix but code behavior doesn't match the described bug

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_display method:
"# DON'T increment counter here - that happens only on Enter
# Bug fix: Incrementing here caused next_auto_line_num to advance prematurely,
# displaying the wrong line number before the user typed anything"

However, the code never increments next_auto_line_num in _update_display at all - there's no code being prevented. The comment describes a bug that was fixed by removing code, but there's no evidence of that code ever being there (no commented-out increment). This suggests the comment is describing a historical bug fix but doesn't match current code structure.

---

#### Documentation inconsistency

**Description:** CONTINUE_KEY is documented with dual purpose (Go to line / Continue execution) but the JSON key name 'goto_line' only reflects one purpose, creating confusion.

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 180-185:
# Go to line (also used for Continue execution in debugger context)
# Note: This key serves dual purpose - "Go to line" in editor mode and
# "Continue execution (Go)" in debugger mode. The JSON key is 'goto_line'
# to reflect its primary function, but CONTINUE_KEY name reflects debugger usage.
_continue_from_json = _get_key('editor', 'goto_line')
CONTINUE_KEY = _ctrl_key_to_urwid(_continue_from_json) if _continue_from_json else 'ctrl g'

The variable name CONTINUE_KEY suggests debugger functionality, but the JSON key 'goto_line' suggests editor functionality. This naming mismatch makes the code harder to understand and maintain.

---

#### Code vs Documentation inconsistency

**Description:** In-page search keybindings documented in code comments but missing from tk_keybindings.json

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
tk_help_browser.py lines 113-117 document local widget bindings:
# Return key in search box navigates to next match (local widget binding)
# Note: This binding is specific to the in-page search entry widget and is not
# documented in tk_keybindings.json, which only documents global application
# keybindings. Local widget bindings are documented in code comments only.
self.inpage_search_entry.bind('<Return>', lambda e: self._inpage_find_next())
# ESC key closes search bar (local widget binding, not in tk_keybindings.json)
self.inpage_search_entry.bind('<Escape>', lambda e: self._inpage_search_close())

However, tk_keybindings.json only documents the global Ctrl+F binding under help_browser.inpage_search, but does not document the Return and Escape bindings that work within the in-page search bar. The comment explicitly states these are intentionally excluded, but this creates incomplete documentation of the help browser's keybindings.

---

#### Code vs Comment conflict

**Description:** Comment about failed restore tracking contradicts error handling approach

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 207 comment states:
# Track failed restores - user should know if settings couldn't be restored

However, the actual error handling (lines 207-220) only shows a warning if restores fail, but doesn't prevent the dialog from closing. This means the user is warned but the dialog still closes, potentially leaving the application in an inconsistent state. The comment suggests this is intentional ('user should know') but doesn't explain why closing the dialog is still the right action when restores fail.

---

#### code_vs_comment

**Description:** Comment about Ctrl+I binding location contradicts actual binding location

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line 455 comment states:
# Note: Ctrl+I is bound directly to editor text widget in start() (not root window)
# to prevent tab key interference - see editor_text.text.bind('<Control-i>', ...)

However, the actual binding at line 237 is:
self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)

This is correct and matches the comment. But then line 455 says 'see editor_text.text.bind' as if pointing to a specific line, when it should reference line 237. The comment is technically correct but the cross-reference is vague.

---

#### code_vs_comment

**Description:** Comment about toolbar simplification references removed features but doesn't explain why

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 571-576 comment states:
# Note: Toolbar has been simplified to show only essential execution controls.
# Additional features are accessible via menus:
# - List Program → Run > List Program
# - New Program (clear) → File > New
# - Clear Output → Run > Clear Output

This suggests the toolbar was previously more complex and was simplified, but doesn't explain the rationale. The comment lists where to find the removed features but doesn't document why they were removed from the toolbar. This is informational but incomplete historical context.

---

#### code_vs_comment

**Description:** Comment about INPUT row visibility control is incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 267-269 comment states:
# INPUT row (hidden by default, shown when INPUT statement needs input)
# Visibility controlled via pack() when showing, pack_forget() when hiding
# Don't pack yet - will be packed when needed

This explains the visibility mechanism but doesn't reference where the show/hide logic is implemented. The comment should point to the methods that control this (likely _show_input_row() and _hide_input_row() or similar, but these aren't visible in the provided code).

---

#### code_vs_comment

**Description:** Comment about variable window heading click behavior doesn't match implementation complexity

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 1113-1119 comment states:
Handle clicks on variable list column headings.

Only the Variable column (column #0) is sortable - clicking it cycles through
different sort modes (see _cycle_variable_sort() for the cycle order).
Type and Value columns are not sortable.

However, lines 1135-1152 show more complex logic:
- Left 20 pixels (arrow area) = toggle sort direction
- Rest of header = cycle/set sort column

The docstring doesn't mention the arrow click behavior at all, only mentioning cycling through sort modes. This is a significant omission of functionality.

---

#### code_vs_comment

**Description:** _on_status_click() uses different regex pattern than _parse_line_number() for extracting BASIC line numbers

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_parse_line_number() uses: r'^(\d+)(?:\s|$)'
This requires whitespace OR end-of-string after the line number.

_on_status_click() uses: r'^\s*(\d+)'
This only requires digits, with optional leading whitespace, but doesn't verify anything comes after.

This means _on_status_click() would match '10REM' and extract '10', while _parse_line_number() would reject it. This inconsistency could cause the status click handler to show info for lines that _parse_line_number() considers invalid.

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No UI-framework dependencies' but doesn't mention the runtime/parser/AST dependencies that are allowed

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Module docstring states: "No UI-framework dependencies (Tk, curses, web)
are allowed. Standard library modules (os, glob, re) and core interpreter
modules (runtime, parser, AST nodes) are permitted."

However, the actual imports only show: from typing import Dict, List, Tuple, Optional, Set
import re

The module doesn't import runtime, parser, or AST nodes directly. These are passed as parameters or accessed via attributes. The docstring should clarify that these are 'accepted as parameters' rather than 'imported', or the docstring is outdated from a refactoring.

---

#### code_vs_comment

**Description:** Comment claims output is NOT cleared on RUN, but Step commands DO clear output. However, examining the step command implementations (_menu_step_line and _menu_step_stmt), there is no code that clears output.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1845 states:
"# Note: Output is NOT cleared - continuous scrolling like ASR33 teletype"
and
"# Note: Step commands (Ctrl+T/Ctrl+K) DO clear output for clarity when debugging"

However, in _menu_step_line (around line 2050) and _menu_step_stmt (around line 2100), the code contains:
"# Note: Output is NOT cleared - continuous scrolling like ASR33 teletype"

There is no code in either step method that calls any clear/reset function on self.output or self._append_output. The comment claims step commands clear output, but the implementation does not.

---

#### code_internal_inconsistency

**Description:** Inconsistent error handling between save_state_periodic and save_on_disconnect callbacks

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Both callbacks have identical try/except blocks:

try:
    app.storage.client['session_state'] = backend.serialize_state()
except Exception as e:
    sys.stderr.write(f'Warning: Failed to save session state: {e}\n')
    sys.stderr.flush()

However, save_on_disconnect has a different error message: 'Failed to save final session state'

This is minor but shows slight inconsistency in error messaging approach. Both should probably use the same message or the distinction should be more meaningful.

---

#### code_vs_documentation

**Description:** Debugging documentation references keyboard shortcuts that vary by UI, but web_settings_dialog.py doesn't show any keyboard shortcut configuration

**Affected files:**
- `docs/help/common/debugging.md`
- `src/ui/web/web_settings_dialog.py`

**Details:**
debugging.md states: 'Debugging keyboard shortcuts vary by UI. See your UI-specific help for complete keyboard shortcut reference' and lists shortcuts like 'Ctrl+T' for Step.

However, web_settings_dialog.py only shows settings for:
- editor.auto_number (checkbox)
- editor.auto_number_step (number input)
- limits.* (read-only display)

No keyboard shortcut configuration is present in the settings dialog, despite web_keybindings.json defining shortcuts like F1, F5, F9, F10, Ctrl+R, etc.

---

#### code_vs_documentation

**Description:** Debugging documentation describes Variables Window and Execution Stack features, but session_state.py doesn't track this UI state

**Affected files:**
- `docs/help/common/debugging.md`
- `src/ui/web/session_state.py`

**Details:**
debugging.md describes:
- Variables Window with sorting, editing, array tracking
- Execution Stack Window showing FOR loops and GOSUB calls
- Statement highlighting with current statement index

But SessionState dataclass only tracks:
- running, paused, output_text (basic execution state)
- editor_content, editor_cursor (editor state)
- last_find_text, last_find_position (find/replace state)
- No variables_window_open, stack_window_open, or current_statement_index fields

This suggests either:
1. These windows are not persisted in session state (inconsistent with Redis-backed sessions)
2. Documentation describes features not yet implemented in web UI

---

#### code_vs_documentation

**Description:** SessionState tracks auto_save_enabled and auto_save_interval but these settings are not mentioned in web_settings_dialog.py or debugging documentation

**Affected files:**
- `src/ui/web/session_state.py`
- `docs/help/common/debugging.md`

**Details:**
SessionState defines:
auto_save_enabled: bool = True
auto_save_interval: int = 30

But web_settings_dialog.py only shows:
- editor.auto_number
- editor.auto_number_step
- limits.* (read-only)

No auto-save settings are exposed in the UI, despite being tracked in session state. This suggests either:
1. Auto-save is implemented but not configurable
2. These fields are planned but not yet used
3. Settings dialog is incomplete

---

#### documentation_inconsistency

**Description:** ATN function documentation mentions precision limitation when computing PI, but the appendices/math-functions.md doesn't mention this important caveat when showing PI calculation examples

**Affected files:**
- `docs/help/common/language/functions/atn.md`
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
In atn.md: "**Note:** When computing PI with `ATN(1) * 4`, the result is limited to single precision (~7 digits). For higher precision, use `ATN(CDBL(1)) * 4` to get double precision."

In math-functions.md under 'Computing Pi' section, it shows both methods but doesn't explain the precision difference or why you'd use CDBL.

---

#### documentation_inconsistency

**Description:** FIX documentation references INT but INT documentation is incomplete in the provided files

**Affected files:**
- `docs/help/common/language/functions/fix.md`
- `docs/help/common/language/functions/int.md`

**Details:**
In fix.md: "FIX(X) is equivalent to SGN(X)*INT(ABS(X)). The major difference between FIX and INT is that FIX does not return the next lower number for negative X."

The INT function documentation is referenced in 'See Also' sections but the actual int.md file content is not fully shown in the provided documentation. The relationship between FIX and INT is explained in FIX but may not be reciprocally explained in INT.

---

#### documentation_inconsistency

**Description:** data-types.md references getting-started.md in 'See Also' section but file doesn't exist

**Affected files:**
- `docs/help/common/language/data-types.md`

**Details:**
In data-types.md 'See Also' section: "- `[Variables](../getting-started.md#variables)` - Using variables"

This creates a broken link as getting-started.md is not in the provided documentation.

---

#### documentation_inconsistency

**Description:** EOF documentation references LINE INPUT# with incorrect link path

**Affected files:**
- `docs/help/common/language/functions/eof.md`

**Details:**
In eof.md 'See Also' section:
- `[LINE INPUT#](../statements/inputi.md)` - Read entire line from file

The link path is 'inputi.md' but based on naming conventions in other files, it should likely be 'line-input-hash.md' or 'line-input_hash.md'. The inconsistent naming makes this unclear.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting and terminology

**Affected files:**
- `docs/help/common/language/functions/inp.md`
- `docs/help/common/language/functions/peek.md`
- `docs/help/common/language/functions/lpos.md`

**Details:**
INP.md uses: '⚠️ **Not Implemented**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter. **Behavior**: Always returns 0'

PEEK.md uses: 'ℹ️ **Emulated with Random Values**: PEEK does NOT read actual memory. Instead, it returns a random value between 0-255 (inclusive). **Behavior**: Each call to PEEK returns a new random integer...'

LPOS.md uses: '⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter. **Behavior**: Function always returns 0 (because there is no printer to track position for)'

These implementation notes use different emoji (⚠️ vs ℹ️), different header styles, and different levels of detail. They should follow a consistent template.

---

#### documentation_inconsistency

**Description:** CLEAR documentation contains conflicting information about parameter meanings between MBASIC 5.21 and earlier versions

**Affected files:**
- `docs/help/common/language/statements/clear.md`

**Details:**
The CLEAR.md documentation states:

"**In MBASIC 5.21 (BASIC-80 release 5.0 and later):**
- **expression1**: If specified, sets the highest memory location available for BASIC to use
- **expression2**: Sets the stack space reserved for BASIC (default: 256 bytes or 1/8 of available memory, whichever is smaller)"

But then contradicts itself:

"**Historical note:** In earlier versions of BASIC-80 (before release 5.0), the parameters had different meanings:
- expression1 set the amount of string space
- expression2 set the end of memory

This behavior changed in release 5.0 to support dynamic string allocation."

The documentation should clarify which version's behavior is actually implemented in this interpreter.

---

#### documentation_inconsistency

**Description:** CLS is documented as 'Extended, Disk' version but index.md doesn't clarify version availability for statements

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/statements/cls.md`

**Details:**
CLS.md states:
"**Versions:** Extended, Disk

**Note:** CLS is implemented in MBASIC and works in all UI backends."

However, the language index.md doesn't provide any guidance on version markers or what they mean in the context of this implementation. Users might be confused about whether 'Extended, Disk' means the feature is limited or fully available.

---

#### documentation_inconsistency

**Description:** Vague and potentially incorrect remark about CP/M behavior

**Affected files:**
- `docs/help/common/language/statements/files.md`

**Details:**
files.md states: "Note: CP/M automatically adds .BAS extension if none is specified for BASIC program files."

This is misleading. CP/M itself does not add extensions - this would be MBASIC's behavior when interpreting filenames. The note should clarify that MBASIC (not CP/M) may add .BAS extension in certain contexts, and specify which contexts (LOAD, SAVE, FILES, etc.).

---

#### documentation_inconsistency

**Description:** Incomplete description of semicolon behavior

**Affected files:**
- `docs/help/common/language/statements/input.md`

**Details:**
input.md states two different semicolon behaviors:
1. "A semicolon immediately after INPUT suppresses the carriage return/line feed after the user presses Enter"
2. "A semicolon after the prompt string causes the prompt to be displayed without a question mark"

These are two different positions for the semicolon (INPUT; vs "prompt";) but the documentation doesn't clearly distinguish between INPUT; "prompt" and INPUT "prompt"; and what happens with INPUT; "prompt";. The syntax line shows [;] only once, which is ambiguous.

---

#### documentation_inconsistency

**Description:** Incomplete information about overlapping range behavior

**Affected files:**
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
The documentation states: "Note: When ranges overlap, the last declaration takes precedence. For example, if you declare both DEFDBL L-P and DEFINT I-N, variables starting with L, M, and N would be affected by both declarations, with the later declaration taking effect."

This note is helpful but incomplete. It doesn't specify:
1. Whether "last" means last in the program text or last executed at runtime
2. What happens if DEF statements are in different parts of the program
3. Whether the scope is global or can be changed mid-program

Typically in BASIC, DEF statements are global and order in source matters, but this should be explicit.

---

#### documentation_inconsistency

**Description:** Contradictory information about file closing behavior between LOAD and MERGE

**Affected files:**
- `docs/help/common/language/statements/load.md`
- `docs/help/common/language/statements/merge.md`

**Details:**
load.md states: "LOAD (without ,R): Closes all open files and deletes all variables and program lines currently in memory before loading" and "LOAD with ,R option: Program is RUN after loading, and all open data files are kept open for program chaining"

merge.md states: "File handling: Unlike LOAD (without ,R), MERGE does NOT close open files. Files that are open before MERGE remain open after MERGE completes. (Compare with LOAD which closes files except when using the ,R option.)"

The contradiction: load.md says LOAD without ,R closes files, but merge.md's comparison statement "Compare with LOAD which closes files except when using the ,R option" implies LOAD always closes files except with ,R, which matches load.md. However, the phrasing "Unlike LOAD (without ,R)" is confusing because it suggests LOAD without ,R has different behavior than what's being compared.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of file modes

**Affected files:**
- `docs/help/common/language/statements/open.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
open.md documents three modes:
- "O" - specifies sequential output mode
- "I" - specifies sequential input mode
- "R" - specifies random input/output mode

printi-printi-using.md mentions: "PRINT# writes data to a sequential file opened for output (mode "O") or append (mode "A")."

The OPEN documentation doesn't mention mode "A" for append, but PRINT# documentation references it. This is an incomplete mode list in the OPEN documentation.

---

#### documentation_inconsistency

**Description:** RESET not mentioned in OPEN's See Also section

**Affected files:**
- `docs/help/common/language/statements/reset.md`
- `docs/help/common/language/statements/open.md`

**Details:**
reset.md states: "The RESET statement closes all files that have been opened with OPEN statements. It performs the same function as executing CLOSE without any file numbers"

open.md See Also section includes CLOSE but not RESET, even though RESET is directly related to file operations initiated by OPEN.

This is a missing cross-reference that would help users discover the RESET command.

---

#### documentation_inconsistency

**Description:** Inconsistent 'Versions' field format across documentation files

**Affected files:**
- `docs/help/common/language/statements/rset.md`
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/save.md`

**Details:**
Some files use 'Versions: Disk' (rset.md, run.md has '8K, Extended, Disk', save.md), while others use 'Versions: MBASIC Extension' (setsetting.md, showsettings.md). The format should be consistent across all documentation files.

---

#### documentation_inconsistency

**Description:** WIDTH documentation describes unsupported LPRINT syntax but doesn't clearly mark it in syntax section

**Affected files:**
- `docs/help/common/language/statements/width.md`

**Details:**
The Implementation Note says 'WIDTH LPRINT <integer expression>' is NOT SUPPORTED and will cause parse error, but the original Syntax section under 'Historical Reference' shows this syntax without clear warning. The unsupported syntax should be more prominently marked in the syntax section itself.

---

#### documentation_inconsistency

**Description:** Variable name significance documentation contradicts itself

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md states: 'In the original MBASIC 5.21, only the first 2 characters of variable names were significant (AB, ABC, and ABCDEF would be the same variable). This Python implementation uses the full variable name for identification, allowing distinct variables like COUNT and COUNTER.' However, it also states 'Variable names are not case-sensitive by default (Count = COUNT = count)', which seems to contradict the full name usage. The settings.md clarifies this is about case sensitivity, not character significance, but variables.md should be clearer.

---

#### documentation_inconsistency

**Description:** WAIT statement documentation formatting issue

**Affected files:**
- `docs/help/common/language/statements/wait.md`

**Details:**
The Remarks section contains malformed text: 'The data read at the port is exclusive OR~ed with the integer expression J, and then AND~ed with 1.' The tilde characters (~) appear to be formatting artifacts. Should be 'XORed' and 'ANDed' or 'exclusive-ORed' and 'ANDed'.

---

#### documentation_inconsistency

**Description:** RSET documentation references non-existent RESET statement

**Affected files:**
- `docs/help/common/language/statements/rset.md`

**Details:**
rset.md ends with: '**Note:** Do not confuse RSET with `[RESET](reset.md)`, which closes all open files.' However, there is no reset.md file in the documentation. Either the RESET documentation is missing or this note is incorrect.

---

#### documentation_inconsistency

**Description:** WIDTH implementation note contradicts itself about supported syntax

**Affected files:**
- `docs/help/common/language/statements/width.md`

**Details:**
The Implementation Note states: 'The simple "WIDTH <number>" statement parses and executes successfully without errors' but also says 'The "WIDTH LPRINT" syntax is NOT supported and will cause a parse error.' However, under 'UNSUPPORTED SYNTAX' it shows the original MBASIC 5.21 also supported 'WIDTH LPRINT <integer expression>'. The note should clarify that the base WIDTH command existed in original MBASIC, but this implementation only accepts the simple form as a no-op.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Stop/Break functionality in Tk UI

**Affected files:**
- `docs/help/common/ui/tk/index.md`
- `docs/help/mbasic/features.md`

**Details:**
tk/index.md states:
- **Stop** ({{kbd:toggle_breakpoint:tk}}reak) - Interrupt execution

This appears to be a template variable that wasn't properly rendered, suggesting 'toggle_breakpoint' key is used for 'Stop/Break'. However, features.md doesn't clarify this mapping.

---

#### documentation_inconsistency

**Description:** Debugging features availability description differs between documents

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/extensions.md`

**Details:**
features.md states:
- **Breakpoints** - Set/clear breakpoints (available in all UIs; access method varies)
- **Step execution** - Execute one line at a time (available in all UIs; access method varies)
- **Variable viewing** - Monitor variables (available in all UIs; access method varies)
- **Stack viewer** - View call stack (available in all UIs; access method varies)

But extensions.md states:
**Availability:** CLI (command form), Curses (Ctrl+B), Tk (UI controls)

This suggests these features are NOT available in Web UI, contradicting features.md claim of 'available in all UIs'.

---

#### documentation_inconsistency

**Description:** PEEK/POKE behavior described differently in architecture vs compatibility docs

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states:
- PEEK: Returns random integer 0-255 (for RNG seeding compatibility)
- POKE: Parsed and executes successfully, but performs no operation (no-op)
- **PEEK does NOT return values written by POKE** - no memory state is maintained

compatibility.md states the same but adds:
- No access to actual system memory

The architecture.md should mention this security/design rationale as well for consistency.

---

#### documentation_inconsistency

**Description:** Missing Web UI settings documentation referenced in compatibility guide

**Affected files:**
- `docs/help/index.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
compatibility.md references:
- see `[Web UI Settings](../ui/web/settings.md)`

But index.md lists UI-specific help as:
- `[Tk (Desktop GUI)](ui/tk/index.md)`
- `[Curses (Terminal)](ui/curses/index.md)`
- `[Web Browser](ui/web/index.md)`
- `[CLI (Command Line)](ui/cli/index.md)`

The path '../ui/web/settings.md' is referenced but not listed in the main index, suggesting missing documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent prompt format in code examples

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
getting-started.md uses bare prompt without 'Ready':
```
10 PRINT "Hello, World!"
20 END
RUN
```

But debugging.md consistently uses 'Ready' prompt:
```
Ready
BREAK 100
Breakpoint set at line 100
Ready
```

The actual MBASIC prompt behavior should be documented consistently.

---

#### documentation_inconsistency

**Description:** SHOWSETTINGS and SETSETTING commands not listed in CLI index

**Affected files:**
- `docs/help/ui/cli/settings.md`
- `docs/help/ui/cli/index.md`

**Details:**
cli/settings.md documents SHOWSETTINGS and SETSETTING as CLI commands with full syntax and examples. However, cli/index.md's 'Common Commands' section does not list these commands:
- LIST - Show program
- RUN - Execute program
- LOAD "file.bas" - Load program
- SAVE "file.bas" - Save program
- NEW - Clear program
- AUTO - Auto line numbering
- RENUM - Renumber lines
- SYSTEM - Exit MBASIC

The settings commands should be included in the common commands list or have a dedicated section.

---

#### documentation_inconsistency

**Description:** Variables inspection documentation exists but not linked from CLI index

**Affected files:**
- `docs/help/ui/cli/variables.md`
- `docs/help/ui/cli/index.md`

**Details:**
cli/variables.md provides comprehensive documentation on variable inspection in CLI mode, but cli/index.md does not link to it. The index shows:

**Debugging Commands:**
- `[Debugging Guide](debugging.md)` - Complete debugging reference
- BREAK - Set/clear breakpoints
- STEP - Single-step execution
- STACK - View call stack

Variable inspection is a debugging feature and should be linked here.

---

#### documentation_inconsistency

**Description:** Broken internal link to keyboard shortcuts

**Affected files:**
- `docs/help/ui/curses/editing.md`

**Details:**
curses/editing.md contains: 'See Also: `[Keyboard Shortcuts](../../../user/keyboard-shortcuts.md)`'

This path '../../../user/keyboard-shortcuts.md' would resolve to 'docs/user/keyboard-shortcuts.md' which is not in the provided documentation structure. The correct path is likely different or the file doesn't exist.

---

#### documentation_inconsistency

**Description:** Variable sorting modes inconsistency

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
variables.md states sort modes are 'Accessed → Written → Read → Name', but feature-reference.md describes them as:
- Accessed: Most recently accessed (read or written) - newest first
- Written: Most recently written to - newest first
- Read: Most recently read from - newest first
- Name: Alphabetically by variable name
Both agree on the modes but variables.md doesn't explain what each mode means.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation between Tk and Web UI docs

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/web/features.md`

**Details:**
Tk features.md uses notation like {{kbd:smart_insert}}, {{kbd:toggle_breakpoint}}, {{kbd:find:tk}}, {{kbd:replace:tk}} without the :tk suffix in most places, but then uses :tk suffix for find/replace. Web features.md consistently uses {{kbd:run:web}}, {{kbd:continue:web}}, {{kbd:step:web}}, {{kbd:find:web}}, {{kbd:replace:web}} with the :web suffix. The Tk docs should be consistent - either always use :tk suffix or never use it.

---

#### documentation_inconsistency

**Description:** Different keyboard shortcuts documented for same operations across UIs

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/web/debugging.md`

**Details:**
Tk features.md documents:
- {{kbd:step_statement}} - Execute next statement
- {{kbd:step_line}} - Execute next line
- {{kbd:continue_execution}} - Continue to next breakpoint

Web debugging.md documents:
- {{kbd:step:web}} - Step statement
- Ctrl+K - Step line
- {{kbd:continue:web}} - Continue

The naming is inconsistent (step_statement vs step, continue_execution vs continue) and it's unclear if these are meant to be the same operations with different shortcuts per UI, or if the documentation is using inconsistent terminology.

---

#### documentation_inconsistency

**Description:** Contradictory information about function key shortcuts in Web UI

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md states: 'Note: Function key shortcuts ({{kbd:continue:web}}, {{kbd:step:web}}, {{kbd:help:web}}1, etc.) are not implemented in the Web UI.'

However, features.md lists under 'Execution Control - Currently Implemented':
- Run ({{kbd:run:web}})
- Continue ({{kbd:continue:web}})
- Step statement ({{kbd:step:web}})
- Stop ({{kbd:stop:web}})

This is contradictory - either these shortcuts work or they don't.

---

#### documentation_inconsistency

**Description:** Contradictory information about settings storage implementation

**Affected files:**
- `docs/help/ui/tk/settings.md`
- `docs/help/ui/web/features.md`

**Details:**
tk/settings.md states at the end: 'Note: Settings storage is implemented, but the settings dialog itself is not yet available in the Tk UI.'

However, the entire document is marked as 'Implementation Status: ... The features described in this document represent planned/intended implementation and are not yet available.'

This is contradictory - if settings storage is implemented, that should be clearly separated from the planned dialog features.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation status for breakpoint features

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/debugging.md`

**Details:**
features.md under 'Breakpoints - Currently Implemented' states:
- Line breakpoints (toggle via Run menu)
- Clear all breakpoints
- Visual indicators in editor

debugging.md under 'Setting Breakpoints - Currently Implemented' states:
1. Use Run → Toggle Breakpoint menu option
2. Enter the line number when prompted

But then debugging.md also says: 'Note: Advanced features like clicking line numbers to set breakpoints and a dedicated breakpoint panel are planned for future releases but not yet implemented.'

This suggests clicking line numbers doesn't work, but features.md doesn't mention this limitation.

---

#### documentation_inconsistency

**Description:** Missing 'Open Example' feature documentation inconsistency

**Affected files:**
- `docs/help/ui/web/web-interface.md`
- `docs/help/ui/web/index.md`

**Details:**
web-interface.md states: "Note: An 'Open Example' feature to choose from sample BASIC programs is planned for a future release."

However, index.md states: "Example programs - Load samples to learn" and "Load Examples - File → Load Example to see sample programs" suggesting the feature already exists.

This creates confusion about whether the feature is implemented or planned.

---

#### documentation_inconsistency

**Description:** Missing cross-reference to case handling in quick reference

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
The CASE_HANDLING_GUIDE.md is a comprehensive 500+ line guide about an important feature (case handling for variables and keywords).

However, QUICK_REFERENCE.md makes no mention of:
- Case handling settings
- SET command for configuring case behavior
- SHOW SETTINGS command
- The existence of case conflict detection

The quick reference should at least mention these features exist and point to the detailed guide, as case handling affects how code appears in the editor.

---

#### documentation_inconsistency

**Description:** Keyboard shortcuts table references shortcuts that may not exist

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
The Common Shortcuts table shows:
| **Run** | {{kbd:run:cli}} | {{kbd:run:curses}} | {{kbd:run_program:tk}} | {{kbd:run:web}} |

But keyboard-shortcuts.md (Curses UI) shows the actual shortcut is '^R' not a placeholder. The table uses placeholder notation that suggests these will be replaced, but it's unclear if this is correct or if actual key combinations should be shown

---

#### documentation_inconsistency

**Description:** INPUT() docstring shows conflicting syntax examples

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line ~710: Docstring shows "INPUT$(n, #filenum)" in BASIC syntax but then says "INPUT(n, filenum)" in Python call syntax and "Note: The # prefix in BASIC syntax is stripped by the parser". This is confusing because it suggests # is part of BASIC syntax but then says it's stripped. Should clarify that # is a BASIC file number prefix, not part of INPUT$ syntax itself.

---

#### Code vs Documentation inconsistency

**Description:** Documentation mentions duplicate two-letter codes but doesn't list which codes are duplicated

**Affected files:**
- `src/error_codes.py`

**Details:**
The module docstring states:
"Note: Some two-letter codes are duplicated (e.g., DD, CN, DF) across different
numeric error codes. This matches the original MBASIC 5.21 specification where
the two-letter codes alone are ambiguous - the numeric code is authoritative."

Looking at ERROR_CODES dictionary:
- DD appears at codes 10 and 68
- CN appears at codes 17 and 69
- DF appears at codes 25 and 61

The documentation correctly identifies the duplicate codes. However, it says '(e.g., DD, CN, DF)' which implies there might be more duplicates. A complete list or clarification that these are the only duplicates would be helpful.

---

#### documentation_inconsistency

**Description:** Help text mentions 'Ctrl+H (UI help)' but this is UI-specific and may not be available in all contexts

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In _show_help() method:
'Press Ctrl+H (UI help) for keyboard shortcuts and UI features.'

This assumes a specific UI implementation with Ctrl+H bound to help, but ImmediateExecutor is designed to be UI-agnostic. The help text should either be generic or note that this is specific to certain UIs.

---

#### code_vs_comment

**Description:** Comment about INPUT statement behavior is split between two locations with slightly different wording

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In execute() method docstring (line ~80):
'Examples:
>>> executor.execute("PRINT 2 + 2")
(True, " 4\\n")'

But in help text LIMITATIONS section:
'• INPUT statement will fail at runtime in immediate mode (use direct assignment instead)'

And in OutputCapturingIOHandler.input() method:
'"""Input not supported in immediate mode.

Note: INPUT statements are parsed and executed normally, but fail
at runtime when the interpreter calls this input() method."""'

The wording is inconsistent - 'will fail at runtime' vs 'not supported' vs 'not allowed'. All mean the same thing but should use consistent terminology.

---

#### documentation_inconsistency

**Description:** Module docstring mentions Python version requirement but doesn't specify minimum version consistently

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Module docstring states:
'Implementation note: Uses standard Python type hints (e.g., tuple[str, bool])
which require Python 3.9+. For earlier Python versions, use Tuple[str, bool] from typing.'

This is informational but doesn't indicate whether the code actually supports Python <3.9 or if it's a hard requirement. The code uses tuple[str, bool] syntax, which means it REQUIRES Python 3.9+, but the note suggests there's a workaround for earlier versions (which isn't implemented).

---

#### documentation_inconsistency

**Description:** cmd_help docstring says 'HELP - Show help information about commands' but implementation shows 'Debugging Commands' which is narrower scope

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring: 'HELP - Show help information about commands'
Implementation prints: 'MBASIC-2025 Debugging Commands:'
The help output focuses on debugging commands but also includes general commands like LOAD, SAVE, NEW, etc. The title is misleading.

---

#### documentation_inconsistency

**Description:** InterpreterState docstring lists execution order but doesn't mention error_info can be set during statement execution (step 6), only in error handling (step 7)

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 44-52 lists:
"Internal execution order in tick_pc() (for developers understanding control flow):
1. pause_requested check - pauses if pause() was called
2. halted check - stops if already halted
3. break_requested check - handles Ctrl+C breaks
4. breakpoints check - pauses at breakpoints
5. trace output - displays [line] or [line.stmt] if TRON is active
6. statement execution - where input_prompt may be set
7. error handling - where error_info is set via exception handlers"

But code at lines 476-490 shows error_info is set DURING statement execution (step 6) in the except block, before invoking the error handler. The docstring implies it's only set in step 7 (error handling).

---

#### code_vs_comment

**Description:** Comment about string length limit mentions len() counts characters and discusses encoding, but doesn't clarify behavior for multi-byte characters

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_binaryop(), the comment states:
"Also note: len() counts characters. For ASCII and latin-1 (both single-byte encodings),
character count equals byte count. Field buffers (LSET/RSET) use latin-1 encoding."

This comment is technically correct but potentially misleading. Python's len() on strings always counts Unicode code points (characters), not bytes. The comment seems to imply this is specific to ASCII/latin-1, but it's true for all Python strings. The relevant point is that field buffers use latin-1 encoding when converting to bytes, which means each character becomes one byte. The comment could be clearer about this distinction.

---

#### code_vs_comment

**Description:** Comment about LSET/RSET fallback behavior claims it's for compatibility but may be misleading

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_lset() and execute_rset(), the comments state:
"Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field
variables (used with FIELD statement for random file access). This fallback
is a deliberate extension for compatibility with code that uses LSET for
general string formatting. This is documented behavior, not a bug."

The comment says the fallback is for "compatibility with code that uses LSET for general string formatting" but then also says "In strict MBASIC 5.21, LSET/RSET are only for field variables." This is contradictory - if MBASIC 5.21 doesn't support LSET for general strings, then supporting it isn't "compatibility" with MBASIC 5.21, it's an extension beyond MBASIC 5.21. The comment should clarify this is compatibility with other BASIC dialects or user expectations, not MBASIC 5.21.

---

#### code_vs_comment

**Description:** Comment about debugger_set parameter usage is inconsistent with actual parameter name

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_functioncall(), the comment says:
"Note: get_variable_for_debugger() and debugger_set=True are used to avoid
triggering variable access tracking."

But the actual code uses:
```
self.runtime.set_variable(base_name, type_suffix, saved_value, debugger_set=True)
```

The comment correctly describes the parameter name (debugger_set=True), so this is actually consistent. However, the comment could be clearer about why this specific mechanism exists and what would happen if debugger_set=False was used instead.

---

#### Documentation inconsistency

**Description:** Module docstring states WebIOHandler is not exported due to nicegui dependency, but web_io.py imports nicegui at module level, making it fail on import if nicegui is not installed

**Affected files:**
- `src/iohandler/__init__.py`
- `src/iohandler/web_io.py`

**Details:**
__init__.py says: "WebIOHandler are not exported here because they have dependencies on their respective UI frameworks (tkinter, nicegui). They should be imported directly from their modules when needed"

But web_io.py has: "from nicegui import ui" at the top level, which will fail immediately on import if nicegui is not installed, defeating the purpose of not exporting it.

---

#### Code vs Comment conflict

**Description:** Comment in read_identifier() claims 'Old BASIC with NEXTI instead of NEXT I should be preprocessed' but no preprocessing mechanism is shown or referenced

**Affected files:**
- `src/lexer.py`

**Details:**
Comment states:
"This lexer parses properly-formed MBASIC 5.21 which generally requires spaces
between keywords and identifiers. Exception: PRINT# and INPUT# where # is part
of the keyword. Old BASIC with NEXTI instead of NEXT I should be preprocessed."

And later:
"NOTE: We do NOT handle old BASIC where keywords run together (NEXTI, FORI).
This is properly-formed MBASIC 5.21 which requires spaces.
Exception: PRINT# and similar file I/O keywords (handled above) support # without space.
Other old BASIC syntax should be preprocessed with conversion scripts."

No preprocessing scripts or mechanisms are referenced elsewhere in the code, making this claim unverifiable.

---

#### Code vs Comment conflict

**Description:** Comment in tokenize() method mentions 'CP/M BASIC' but module docstring specifies 'MBASIC 5.21 (CP/M era MBASIC-80)' - inconsistent terminology

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring: "Lexer for MBASIC 5.21 (CP/M era MBASIC-80)"

Comment in tokenize(): "# In CP/M BASIC, \r (carriage return) can be used as statement separator"

While these refer to the same thing, the terminology is inconsistent. Should use 'MBASIC 5.21' or 'MBASIC-80' consistently.

---

#### code_vs_comment

**Description:** Inconsistent terminology for 'end of line' vs 'end of statement' in method documentation

**Affected files:**
- `src/parser.py`

**Details:**
The method at_end_of_line() at line 163 has documentation:
"Check if at end of logical line (NEWLINE or EOF)

Note: This method does NOT check for comment tokens (REM, REMARK, APOSTROPHE)
or statement separators (COLON). Use at_end_of_statement() when parsing statements
that should stop at comments/colons. Use at_end_of_line() for line-level parsing
where colons separate multiple statements on the same line."

However, the implementation at line 172 checks:
"return token.type in (TokenType.NEWLINE, TokenType.EOF)"

The method at_end_of_statement() at line 174 checks:
"return token.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.COLON,
                      TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE)"

The documentation is clear and correct, but the usage throughout the code may be inconsistent. For example, in parse_print() at line 1296, it checks 'not self.at_end_of_line()' but also checks for COLON, ELSE, and REM tokens separately, which suggests at_end_of_statement() might be more appropriate.

---

#### documentation_inconsistency

**Description:** Incomplete documentation of expression parsing precedence levels

**Affected files:**
- `src/parser.py`

**Details:**
The parse_expression() method documentation at lines 598-611 lists precedence levels:
"Precedence (lowest to highest):
1. Logical: IMP
2. Logical: EQV
3. Logical: XOR
4. Logical: OR
5. Logical: AND
6. Logical: NOT
7. Relational: =, <>, <, >, <=, >=
8. Additive: +, -
9. Multiplicative: *, /, \\, MOD
10. Unary: -, +
11. Power: ^
12. Primary: numbers, strings, variables, functions, parentheses"

However, this list shows 'Unary: -, +' at level 10 and 'Power: ^' at level 11, but in standard mathematical precedence, unary operators typically have higher precedence than binary operators. The implementation at parse_unary() (line 779) calls parse_power() (line 791), which means unary operators are parsed BEFORE power operators, giving them HIGHER precedence. This contradicts the documentation which lists unary at level 10 and power at level 11 (where higher numbers should mean higher precedence).

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No need to track current_line/current_stmt/next_line/next_stmt separately' but doesn't explain what system it replaced

**Affected files:**
- `src/pc.py`

**Details:**
The module docstring lists benefits of the PC design including 'No need to track current_line/current_stmt/next_line/next_stmt separately' but there's no context about what the previous system was or why this is better. This makes the claim hard to verify.

---

#### code_vs_comment

**Description:** Comment about line=-1 usage is inconsistent between different locations

**Affected files:**
- `src/runtime.py`

**Details:**
Line 47-53 in __init__ comment: "Note: line -1 in last_write indicates non-program execution sources:
1. System/internal variables (ERR%, ERL%) via set_variable_raw() with FakeToken(line=-1)
2. Debugger/interactive prompt via set_variable() with debugger_set=True and token.line=-1
Both use line=-1, making them indistinguishable from each other in last_write alone.
However, line=-1 distinguishes these special sources from normal program execution (line >= 0)."

Line 430-437 in set_variable_raw() comment: "The line=-1 marker in last_write indicates system/internal variables.
However, debugger sets also use line=-1 (via debugger_set=True),
making them indistinguishable from system variables in last_write alone.
Both are distinguished from normal program execution (line >= 0)."

These comments are consistent, but the explanation is repeated in multiple places. Consider consolidating into a single authoritative comment location.

---

#### code_vs_comment

**Description:** Comment about token.line fallback behavior is inconsistent with ValueError check

**Affected files:**
- `src/runtime.py`

**Details:**
Line 234-243 in get_variable() docstring: "token: REQUIRED - Token object for tracking (ValueError raised if None).

Token object is required but its attributes are optional:
- token.line: Preferred for tracking, falls back to self.pc.line_num if missing
- token.position: Preferred for tracking, falls back to None if missing

This allows robust handling of tokens from various sources (lexer, parser,
fake tokens) while enforcing that some token object must be provided.
For debugging without token requirements, use get_variable_for_debugger()."

Line 248-249: "if token is None:
    raise ValueError('get_variable() requires token parameter. Use get_variable_for_debugger() instead.')"

The comment describes fallback behavior for missing token.line attribute, but the code raises ValueError if token itself is None. The comment should clarify that token object is required (not None) but its attributes can be missing.

---

#### Code vs Comment conflict

**Description:** Comment claims default type suffix fallback should not occur in practice, but code implements it as defensive programming

**Affected files:**
- `src/runtime.py`

**Details:**
In parse_name() helper function within get_variables():

Comment says: "Note: In normal operation, all names in _variables have resolved type suffixes from _resolve_variable_name() which applies DEF type rules. This fallback is defensive programming for robustness - it should not occur in practice, but protects against potential edge cases in legacy code or future changes."

Code implements: "return full_name, '!'" as fallback when no type suffix present.

The comment suggests this is purely defensive and shouldn't happen, but doesn't explain if this is truly unreachable or if there are legitimate edge cases.

---

#### Documentation inconsistency

**Description:** Redundant field documentation acknowledges redundancy but doesn't explain why it exists

**Affected files:**
- `src/runtime.py`

**Details:**
In get_execution_stack() docstring for GOSUB calls:

"Note: 'from_line' is redundant with 'return_line' - both contain the same value (the line number to return to after RETURN). The 'from_line' field exists for backward compatibility with code that expects it. Use 'return_line' for new code as it more clearly indicates the field's purpose."

This documents the redundancy but doesn't specify what code depends on 'from_line' or when it might be safe to remove. The deprecation policy is unclear compared to get_loop_stack() which has explicit deprecation dates.

---

#### Documentation inconsistency

**Description:** Deprecation notice uses inconsistent date format

**Affected files:**
- `src/runtime.py`

**Details:**
In get_loop_stack() deprecation notice:
"Deprecated since: 2025-10-25 (commit cda25c84)"

This date (October 25, 2025) is in the future relative to typical development timelines, suggesting either:
1. The date format is incorrect (should be 2024-10-25)
2. This is placeholder documentation
3. The year is a typo

The removal date "No earlier than 2026-01-01" would only give 2 months notice if the deprecation date is correct, which seems short for a compatibility feature.

---

#### code_vs_comment

**Description:** Module docstring references src/lexer.py but doesn't verify the relationship

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
Module docstring states:
"This is a simplified keyword case handler used by the lexer (src/lexer.py)."

And later:
"The lexer (src/lexer.py) uses SimpleKeywordCase because keywords only need
force-based policies in the tokenization phase."

However, src/lexer.py is not provided in the source files, so this relationship cannot be verified. The comment makes claims about how another module uses this code, but that module isn't available for verification.

---

#### Documentation inconsistency

**Description:** The UIBackend docstring mentions 'BatchBackend' as a potential future backend type but then includes a confusing note about 'headless' being contradictory. The comment seems to conflate batch/non-interactive execution with headless operation.

**Affected files:**
- `src/ui/base.py`

**Details:**
From base.py docstring:
"Future/potential backend types (not yet implemented):
- WebBackend: Browser-based interface
- BatchBackend: Non-interactive execution mode for running programs from command line
               (Note: 'headless' typically means no UI, which seems contradictory to UIBackend purpose;
               batch/non-interactive execution may be better handled outside the UIBackend abstraction)"

The parenthetical note creates confusion about whether batch execution should be a UIBackend or not.

---

#### code_vs_comment

**Description:** Comment about target_column default value is misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sort_and_position_line docstring:
"target_column: Column to position cursor at (default: 7). This value is an approximation for typical line numbers."

And in keypress method:
"Note: Methods like _sort_and_position_line use a default target_column of 7, which assumes typical line numbers (status=1 char + number=5 digits + space=1 char)."

But the math is wrong: 1 + 5 + 1 = 7 assumes ALL line numbers are exactly 5 digits (like 10000-99999). For typical line numbers like 10, 100, 1000, the code area starts at column 3, 4, or 5, not 7. The comment should say 'assumes 5-digit line numbers' not 'typical line numbers'.

---

#### code_vs_comment

**Description:** Comment about 'use is None instead of not' is overly defensive

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _display_syntax_errors method:
"# Check if output walker is available (use 'is None' instead of 'not' to avoid false positive on empty walker)
if self._output_walker is None:"

This comment suggests that 'not self._output_walker' would give false positive on empty walker. However, an empty walker (ListWalker with no items) is still truthy in Python - only None is falsy. The comment implies a bug that doesn't exist. Using 'is None' is correct, but the justification is wrong.

---

#### code_vs_comment

**Description:** Status bar update inconsistency in debug methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _debug_step() (line ~850) and _debug_step_line() (line ~920), comments say '(No status bar update - output will show in output window)' but later in the same methods, there ARE status bar updates:

Line ~880: self.status_bar.set_text(f"Paused at {pc_display} - ...")
Line ~950: self.status_bar.set_text(f"Paused at {pc_display} - ...")

The comment is misleading - it should say 'No initial status bar update' or remove the comment entirely.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate mentions syncing allows LIST to see current program, but LIST command implementation calls _list_program which doesn't use runtime

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method:
"# Sync program to runtime (updates statement table and line text map).
# If execution is running, _sync_program_to_runtime preserves current PC.
# If not running, it sets PC to halted. Either way, this doesn't start execution,
# but allows commands like LIST to see the current program."

However, _list_program (called by cmd_list) uses self.editor_lines directly, not runtime's statement_table. The comment may be outdated or referring to a different LIST implementation.

---

#### code_vs_comment

**Description:** Comment in cmd_delete and cmd_renum says runtime=None but doesn't explain why

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_delete:
"delete_lines_from_program(self.program, args, runtime=None)"

In cmd_renum:
"renum_program(self.program, args, self.interpreter.interactive_mode._renum_statement, runtime=None)"

Both pass runtime=None to helper functions, then call _sync_program_to_runtime() afterward. The comment doesn't explain this pattern - it appears the helpers don't need runtime because sync happens separately, but this isn't documented.

---

#### Code vs Comment conflict

**Description:** Comment says STACK_KEY has no keyboard shortcut and is menu-only, but this contradicts the pattern of other constants that have actual key values.

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line 156: STACK_KEY = ''  # No keyboard shortcut

Comment in KEYBINDINGS_BY_CATEGORY (lines 217-222) says:
# - STACK_KEY (empty string) - No keyboard shortcut assigned, menu-only

While technically consistent, using an empty string for 'no shortcut' is inconsistent with QUIT_KEY which uses None for the same purpose. This inconsistency could cause bugs.

---

#### Code vs Comment conflict

**Description:** Comment claims certain keys are not included in KEYBINDINGS_BY_CATEGORY, but doesn't explain why MENU_KEY is also excluded despite being a global command.

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 217-222:
# Note: This dictionary contains keybindings shown in the help system.
# Some defined constants are not included here:
# - CLEAR_BREAKPOINTS_KEY (Shift+Ctrl+B) - Available in menu under Edit > Clear All Breakpoints
# - STOP_KEY (Ctrl+X) - Shown in debugger context in the Debugger category
# - MAXIMIZE_OUTPUT_KEY (Shift+Ctrl+M) - Menu-only feature, not documented as keyboard shortcut
# - STACK_KEY (empty string) - No keyboard shortcut assigned, menu-only
# - Dialog-specific keys (DIALOG_YES_KEY, DIALOG_NO_KEY, SETTINGS_APPLY_KEY, SETTINGS_RESET_KEY) - Shown in dialog prompts
# - Context-specific keys (VARS_SORT_MODE_KEY, VARS_SORT_DIR_KEY, etc.) - Shown in Variables Window category

However, STOP_KEY (Ctrl+X) IS included in the 'Debugger (when program running)' category (line 253), contradicting the comment. Also, MENU_KEY is defined (line 135) but not listed in the exclusions comment, yet it IS included in KEYBINDINGS_BY_CATEGORY (line 230).

---

#### Code inconsistency

**Description:** Inconsistent handling of missing JSON keys - some use if/else with defaults, others just use defaults in the else clause.

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Some keys use this pattern:
_run_from_json = _get_key('editor', 'run')
RUN_KEY = _ctrl_key_to_urwid(_run_from_json) if _run_from_json else 'ctrl r'

But QUIT_ALT_KEY uses the same pattern even though the comment suggests Ctrl+C is always the fallback:
_quit_alt_from_json = _get_key('editor', 'quit')
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

This inconsistency suggests uncertainty about whether these defaults should ever be used or if they're just safety fallbacks.

---

#### Documentation inconsistency

**Description:** Module docstring claims 'Not thread-safe (no locking mechanism)' but doesn't explain why this matters or what the consequences are.

**Affected files:**
- `src/ui/recent_files.py`

**Details:**
Lines 1-22 (module docstring):
"""Recent Files Manager - Shared module for tracking recently opened files
...
Features:
- Stores last 10 recently opened files
- Records full path and last access timestamp
- Automatically creates config directory if needed
- Cross-platform (uses pathlib)
- Note: Not thread-safe (no locking mechanism)
"""

This warning about thread-safety is mentioned but not explained. Given that the module is used across multiple UIs (Tk, Curses, Web), it's unclear if this is a real concern or just a theoretical limitation.

---

#### Code vs Comment conflict

**Description:** Comment about link tag prefixes is incomplete

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Line 632 comment states:
Note: Both 'link_' (from _render_line_with_links) and 'result_link_'
(from _execute_search) prefixes are checked. Both types are stored
identically in self.link_urls, but the prefixes distinguish their origin.

However, the code also creates tags with prefix 'result_link_' in _execute_search (line 449), but the actual tag binding in _render_line_with_links uses 'link_{counter}' format (line 234). The comment correctly identifies both prefixes but doesn't mention that there's also a plain 'link' tag used for styling (line 161) which is different from the clickable link tags.

---

#### Documentation inconsistency

**Description:** Module docstring lists features not fully explained in implementation comments

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Module docstring (lines 1-10) lists:
- Table formatting for markdown tables

But the _format_table_row() method (lines 714-732) has minimal documentation about how table formatting works. The docstring promises 'table formatting' as a feature but doesn't explain that separator rows are skipped, columns are padded to 15 chars, or that markdown formatting in cells is cleaned up.

---

#### Code vs Comment conflict

**Description:** Comment about menu dismissal is overly detailed

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Line 649 comment states:
# Define dismiss_menu helper for ESC/FocusOut bindings (below)

Followed by line 658 comment:
# Release grab after menu is shown. Note: tk_popup handles menu interaction,
# but we explicitly release the grab to ensure clean state.

These comments provide implementation details about menu handling that are standard Tkinter patterns. The level of detail suggests these were added during debugging or as learning notes, but may not be necessary for maintenance. The second comment's note about tk_popup handling interaction is particularly verbose.

---

#### code_vs_comment

**Description:** Comment about immediate entry focus handling is overly detailed for implementation detail

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 299-303 have extensive comments about focus handling:
# Initialize immediate mode entry to be enabled and focused
# (it will be enabled/disabled later based on program state via _update_immediate_status)
self.immediate_entry.config(state=tk.NORMAL)

# Ensure entry is above other widgets
self.immediate_entry.lift()

# Give initial focus to immediate entry for convenience
def set_initial_focus():
    # Ensure all widgets are fully laid out
    self.root.update_idletasks()
    # Set focus to immediate entry
    self.immediate_entry.focus_force()

# Try setting focus after a delay to ensure window is fully realized
self.root.after(500, set_initial_focus)

The comments explain every step but don't explain WHY the 500ms delay is needed or what problem it solves. This level of detail suggests a workaround for a Tk timing issue but doesn't document the root cause.

---

#### code_vs_comment

**Description:** CLS behavior documented as design decision but may conflict with user expectations

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In TkIOHandler.clear_screen() method:
"""Clear screen - no-op for Tk UI.

Design decision: GUI output is persistent for review. Users can manually
clear output via Run > Clear Output menu if desired. CLS command is ignored
to preserve output history during program execution.
"""

This documents that CLS is intentionally ignored, but this may conflict with BASIC program expectations. Programs that use CLS for screen management will not work as expected. This should be documented in user-facing documentation, not just code comments.

---

#### code_vs_comment

**Description:** Comment in serialize_variable() mentions explicit_type_suffix attribute behavior but implementation uses getattr with default

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Note: explicit_type_suffix is not always set (depends on parser implementation),
so getattr defaults to False if missing, preventing incorrect suffix output"

This comment is accurate and matches the code: getattr(var, 'explicit_type_suffix', False). However, it's placed after the conditional check, making it read like an explanation of potential issues rather than documenting the defensive programming pattern. The comment is correct but could be clearer about being documentation of the getattr pattern.

---

#### code_vs_documentation

**Description:** cycle_sort_mode() docstring mentions 'Tk UI implementation' but this is supposed to be UI-agnostic code

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Docstring states: "The cycle order is: accessed -> written -> read -> name -> (back to accessed)
This matches the Tk UI implementation."

The module docstring claims this is 'Common variable sorting logic for all UIs (Tk, Curses, Web)' and should be UI-agnostic. Referencing a specific UI implementation (Tk) in the docstring suggests this might be copied code or that the Tk UI is considered the canonical implementation. The docstring should either:
1. Remove the Tk reference and just document the cycle order
2. Explain that this cycle order was chosen to match existing Tk behavior for consistency

The current phrasing makes it unclear whether this is a design decision or an implementation detail.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of editor placeholder clearing

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In OpenFileDialog._open_file() at line ~467:
# Clear placeholder once content is loaded
if content:
    self.backend.editor_has_been_used = True
    self.backend.editor.props('placeholder=""')

However, editor_has_been_used is set but never initialized in __init__ (line ~976-1024). This suggests either:
1. Missing initialization
2. Attribute is set elsewhere
3. Code relies on Python's dynamic attribute creation

---

#### documentation_inconsistency

**Description:** Debugging documentation mentions Ctrl+T for Step but web_keybindings.json doesn't define this shortcut

**Affected files:**
- `docs/help/common/debugging.md`
- `src/ui/web_keybindings.json`

**Details:**
debugging.md states: 'Shortcuts: Tk/Curses/Web: Ctrl+T or Step button'

But web_keybindings.json defines:
- 'step': {'keys': ['F10'], 'primary': 'F10', 'description': 'Step to next line'}
- No Ctrl+T binding is present

Also, web_keybindings.json shows 'continue' uses F5, but 'run' also uses F5, which could be confusing.

---

#### documentation_inconsistency

**Description:** editor-commands.md says shortcuts vary by UI and refers to UI-specific help, but debugging.md gives specific shortcuts like Ctrl+T, Ctrl+G, Ctrl+Q

**Affected files:**
- `docs/help/common/editor-commands.md`
- `docs/help/common/debugging.md`

**Details:**
editor-commands.md states: 'Important: Keyboard shortcuts vary by UI. See your UI-specific help for the exact keybindings' and 'Each UI uses different keys due to platform constraints (e.g., Curses can't use Ctrl+S for save as it's used for terminal flow control).'

But debugging.md gives specific shortcuts:
- 'Press Ctrl+T or click Step to advance one statement'
- 'Press Ctrl+G or click Continue to run to next breakpoint'
- 'Press Ctrl+Q or click Stop to halt execution'

This creates confusion about whether these shortcuts are universal or UI-specific.

---

#### code_comment_conflict

**Description:** Comment says 'Legacy class kept for compatibility' but the class is marked _DEPRECATED in the name, suggesting it should not be used at all

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Class definition: 'class WebHelpLauncher_DEPRECATED:'
Docstring: 'Legacy class wrapper for compatibility.'
Comment above class: 'Legacy class kept for compatibility - new code should use direct web URL instead'

The _DEPRECATED suffix suggests the class should not be used, but 'kept for compatibility' suggests it's still supported. The migration guide implies all code should migrate away from it.

---

#### code_vs_documentation

**Description:** Version documentation says MBASIC 5.21 but version.py shows VERSION = '1.0.772' which is the project version, not the MBASIC version

**Affected files:**
- `src/version.py`
- `docs/help/common/getting-started.md`

**Details:**
version.py defines:
VERSION = '1.0.772'  # Project version
MBASIC_VERSION = '5.21'  # The MBASIC version we implement

getting-started.md states: 'MBASIC 5.21 is compatible with MBASIC from the 1980s.'

This is technically correct but could be clearer. The project version (1.0.772) vs MBASIC compatibility version (5.21) distinction should be documented.

---

#### documentation_inconsistency

**Description:** loops.md uses WEND statement but getting-started.md doesn't mention WHILE-WEND loops in basic concepts

**Affected files:**
- `docs/help/common/examples/loops.md`
- `docs/help/common/getting-started.md`

**Details:**
loops.md has extensive WHILE-WEND examples:
'10 WHILE SUM < 100
40   SUM = SUM + COUNT
60 WEND'

But getting-started.md only shows FOR-NEXT loops in the 'Program Flow' section:
'10 FOR I = 1 TO 10
20   PRINT I
30 NEXT I'

WHILE-WEND is a fundamental loop construct and should be mentioned in getting-started.md alongside FOR-NEXT.

---

#### documentation_inconsistency

**Description:** Inconsistent notation for mathematical constants between data-types.md and math-functions.md

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
In data-types.md under 'Exponent Notation':
- Uses 'D notation (e.g., 1.5D+10)' and 'E notation (e.g., 1.5E+10)'

In math-functions.md under 'Constants':
- Shows PI# = 3.141592653589793 and E# = 2.718281828459045
- But doesn't show examples using D or E notation for these constants

The math-functions.md should demonstrate D/E notation usage for consistency with data-types.md teaching.

---

#### documentation_inconsistency

**Description:** Error code reference inconsistency - CVI/CVS/CVD mentions error code 'FC' but error-codes.md uses code '5' for Illegal function call

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`
- `docs/help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
In cvi-cvs-cvd.md: "**Error:** Raises 'Illegal function call' (error code FC)"

In error-codes.md: "| **FC** | 5 | Illegal function call | ..."

Both 'FC' and '5' are shown in error-codes.md, but the cvi-cvs-cvd.md only mentions 'FC' without the numeric code. For consistency, both should be mentioned or a standard format should be used.

---

#### documentation_inconsistency

**Description:** character-set.md references character-set.md in its own 'See Also' section

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
In character-set.md 'See Also' section:
- `[Character Set](../character-set.md)` - BASIC-80 character set overview

This is a self-reference that should probably point to ascii-codes.md or be removed.

---

#### documentation_inconsistency

**Description:** ascii-codes.md 'See Also' section has circular reference to character-set.md

**Affected files:**
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
In ascii-codes.md 'See Also':
- `[Character Set](../character-set.md)` - BASIC-80 character set overview

And in character-set.md 'See Also':
- `[ASCII Codes](appendices/ascii-codes.md)` - Complete ASCII table

While cross-references are useful, the relationship should be clarified (one is overview, one is detailed reference).

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting

**Affected files:**
- `docs/help/common/language/functions/hex_dollar.md`
- `docs/help/common/language/functions/oct_dollar.md`

**Details:**
HEX$.md shows two separate examples with 'RUN' commands:
'10 INPUT X
20 A$ = HEX$(X)
30 PRINT X; "DECIMAL IS "; A$; " HEXADECIMAL"
RUN
? 32
32 DECIMAL IS 20 HEXADECIMAL
Ok

10 PRINT HEX$(255)
RUN
FF
Ok'

OCT$.md shows similar examples but with slightly different formatting and comments. Both should follow the same style.

---

#### documentation_inconsistency

**Description:** SPACE$ description mentions STRING$ equivalence but STRING$ doesn't mention SPACE$

**Affected files:**
- `docs/help/common/language/functions/space_dollar.md`
- `docs/help/common/language/functions/string_dollar.md`

**Details:**
SPACE$.md says: 'This is equivalent to STRING$(I, 32) since 32 is the ASCII code for a space character.'
But STRING$.md doesn't mention that SPACE$ is a special case. Cross-references should be bidirectional.

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' section ordering

**Affected files:**
- `docs/help/common/language/functions/int.md`
- `docs/help/common/language/functions/sin.md`

**Details:**
INT.md lists functions in one order (ABS, ATN, CDBL, CINT, COS, CSNG, EXP, FIX, LOG, RND, SGN, SIN, SQR, TAN) while SIN.md lists them in a different order (ABS, ATN, COS, EXP, FIX, INT, LOG, RND, SGN, SQR, TAN). The 'See Also' sections should follow a consistent ordering (alphabetical or by category).

---

#### documentation_inconsistency

**Description:** PEEK documentation has conflicting statements about POKE relationship

**Affected files:**
- `docs/help/common/language/functions/peek.md`

**Details:**
PEEK.md states in the implementation note: 'Important Limitations: **PEEK does NOT return values written by POKE** (POKE is a no-op that does nothing)'

But later in the Description section it says: 'PEEK is traditionally the complementary function to the POKE statement. However, in this implementation, PEEK returns random values and POKE is a no-op, so they are not functionally related.'

The second statement is more accurate and complete. The implementation note should be consistent with the description.

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' references - TAB references READ and DATA, VAL does not reference TAB despite using it in example

**Affected files:**
- `docs/help/common/language/functions/tab.md`
- `docs/help/common/language/functions/val.md`

**Details:**
TAB.md example uses READ/DATA and lists them in 'See Also':
```basic
10 PRINT "NAME" TAB(25) "AMOUNT": PRINT
20 READ A$, B$
30 PRINT A$ TAB(25) B$
40 DATA "G. T. JONES", "$25.00"
```

VAL.md example uses TAB but doesn't reference it:
```basic
10 READ NAME$, CITY$, STATE$, ZIP$
20 IF VAL(ZIP$) < 90000 OR VAL(ZIP$) > 96699 THEN PRINT NAME$; TAB(25); "OUT OF STATE"
30 IF VAL(ZIP$) >= 90801 AND VAL(ZIP$) <= 90815 THEN PRINT NAME$; TAB(25); "LONG BEACH"
```
VAL.md 'See Also' includes SPC but not TAB, despite TAB being used in the example.

---

#### documentation_inconsistency

**Description:** DEF FN documentation describes extended multi-character function names as an extension but doesn't clearly mark compatibility implications

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
DEF FN.md states:

"**Original MBASIC 5.21**: Function names were limited to a single character after FN:
- ✓ `FNA` - single character
- ✓ `FNB$` - single character with type suffix

**This implementation (extension)**: Function names can be multiple characters:
- ✓ `FNA` - single character (compatible with original)
- ✓ `FNABC` - multiple characters"

This is an extension beyond original MBASIC 5.21 behavior, but the documentation doesn't clearly indicate this could cause compatibility issues with original MBASIC programs that might have used 'FNABC' as separate tokens.

---

#### documentation_inconsistency

**Description:** CHAIN and COMMON documentation have slightly different descriptions of variable passing behavior

**Affected files:**
- `docs/help/common/language/statements/chain.md`
- `docs/help/common/language/statements/common.md`

**Details:**
CHAIN.md states:
"Variables are only passed to the chained program if they are declared in a COMMON statement. Without ALL, only COMMON variables are passed. With ALL, all variables are passed."

COMMON.md states:
"If all variables are to be passed, use CHAIN with the ALL option and omit the COMMON statement."

This creates ambiguity: Does CHAIN...ALL require COMMON statements or not? CHAIN.md says "With ALL, all variables are passed" (implying COMMON not needed), while COMMON.md says "omit the COMMON statement" (confirming COMMON not needed with ALL). The wording should be consistent.

---

#### documentation_inconsistency

**Description:** CONT documentation references non-existent example in Section 2.61

**Affected files:**
- `docs/help/common/language/statements/cont.md`

**Details:**
CONT.md Example section states:
```basic
See example Section 2.61, STOP.
```

This appears to be a reference to the original MBASIC manual's section numbering, which doesn't exist in this documentation structure. The reference should either be updated to point to the actual STOP.md file or the example should be included directly.

---

#### documentation_inconsistency

**Description:** DEF USR documentation references non-existent Appendix C

**Affected files:**
- `docs/help/common/language/statements/def-usr.md`

**Details:**
DEF USR.md states:
"See Appendix C, Assembly Language Subroutines, in the original MBASIC documentation for details on writing assembly language routines."

This appendix doesn't exist in the current documentation structure. Since DEF USR is not implemented, this reference should either be removed or updated to indicate it's from the original manual.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation status descriptions for machine code features

**Affected files:**
- `docs/help/common/language/functions/usr.md`
- `docs/help/common/language/functions/varptr.md`
- `docs/help/common/language/statements/call.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
Different wording is used across files for similar 'not implemented' features:

USR.md: "**Behavior**: Always returns 0"
VARPTR.md: "**Behavior**: Function is not available (runtime error when called)"
CALL.md: "**Behavior**: Statement is parsed but no operation is performed"
DEF USR.md: "**Behavior**: Statement is parsed but no operation is performed"

These should use consistent language to describe what happens when these features are used.

---

#### documentation_inconsistency

**Description:** DATA documentation example output doesn't match the code

**Affected files:**
- `docs/help/common/language/statements/data.md`

**Details:**
DATA.md shows this example:
```basic
10 DATA 12, 3.14159, "Hello", WORLD
20 DATA "Smith, John", 100, -5.5
30 READ A, B, C$, D$
40 PRINT A; B; C$; D$
50 READ NAME$, SCORE, ADJUSTMENT
60 PRINT NAME$, SCORE, ADJUSTMENT
```

Output:
```
 12  3.14159 Hello WORLD
Smith, John    100  -5.5
```

The output format suggests PRINT with semicolons produces spaces between values, and PRINT with commas produces tab-separated values. However, the spacing in the output doesn't clearly show this distinction, particularly the second line which should show tab-separated output but appears to have irregular spacing.

---

#### documentation_inconsistency

**Description:** Incomplete cross-reference list

**Affected files:**
- `docs/help/common/language/statements/field.md`

**Details:**
field.md See Also section lists:
- OPEN, LSET, RSET, GET, PUT, MKI$/MKS$/MKD$, CVI/CVS/CVD, CLOSE

But does not reference LOC or LOF functions which are commonly used with random files and are referenced in get.md's See Also section. This creates an inconsistent cross-reference network.

---

#### documentation_inconsistency

**Description:** Incomplete syntax description

**Affected files:**
- `docs/help/common/language/statements/get.md`

**Details:**
get.md syntax shows: GET [#]<file number>[,<record number>]

But the remarks state: "If <record number> is omitted, the next record (after the last GET) is read into the buffer."

The syntax should clarify that record number is optional by showing it in square brackets, which it does. However, the example only shows GET with a record number. An example showing GET without a record number (sequential reading) would be helpful for completeness.

---

#### documentation_inconsistency

**Description:** Duplicate note about CP/M extension behavior

**Affected files:**
- `docs/help/common/language/statements/kill.md`

**Details:**
kill.md contains the same note as files.md: "Note: CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files."

This creates maintenance burden and potential for inconsistency. The note appears in multiple files (files.md, kill.md) and should either be centralized in a common reference or consistently applied across all file-related commands (LOAD, SAVE, MERGE, etc.).

---

#### documentation_inconsistency

**Description:** Incomplete Remarks section

**Affected files:**
- `docs/help/common/language/statements/list.md`

**Details:**
list.md has an empty Remarks section:
"## Remarks


## Example"

This should either contain remarks about LIST behavior (like LLIST does) or be removed if there are no special remarks to make.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-reference lists in See Also sections

**Affected files:**
- `docs/help/common/language/statements/llist.md`
- `docs/help/common/language/statements/renum.md`

**Details:**
llist.md See Also includes: AUTO, DELETE, EDIT, LIST, RENUM
renum.md See Also includes: AUTO, DELETE, EDIT, LIST, LLIST

Both documents reference each other and share the same category (editing), but the cross-reference is symmetric. This is actually consistent, but worth noting that LLIST is marked as not implemented while still being cross-referenced.

---

#### documentation_inconsistency

**Description:** LPRINT documentation references PRINT USING but PRINT documentation doesn't fully document PRINT USING

**Affected files:**
- `docs/help/common/language/statements/lprint-lprint-using.md`
- `docs/help/common/language/statements/print.md`

**Details:**
lprint-lprint-using.md states: "LPRINT USING works exactly like PRINT USING except output goes to the line printer."

However, print.md only briefly mentions PRINT USING in the See Also section as "PRINT USING - Formatted output to the screen" but doesn't provide full documentation of the USING syntax in the main PRINT document. The LPRINT doc shows example syntax like "LPRINT USING "##: $$###.##"; ITEM, PRICE" but this format string syntax is not explained in the PRINT documentation.

---

#### documentation_inconsistency

**Description:** NEW documentation lacks detail compared to similar commands

**Affected files:**
- `docs/help/common/language/statements/new.md`
- `docs/help/common/language/statements/load.md`

**Details:**
new.md has an empty Remarks section and minimal documentation: "To delete the program currently in memory and clear all variables."

load.md provides detailed remarks about file handling: "LOAD (without ,R): Closes all open files and deletes all variables and program lines currently in memory before loading"

NEW performs similar operations (deleting program and clearing variables) but doesn't document whether it closes open files. Given that LOAD closes files, it's likely NEW does too, but this is not documented.

---

#### documentation_inconsistency

**Description:** NULL references obsolete hardware but LPRINT also references obsolete hardware with different implementation notes

**Affected files:**
- `docs/help/common/language/statements/null.md`
- `docs/help/common/language/statements/lprint-lprint-using.md`

**Details:**
null.md describes NULL for tape punches and teletypes without an implementation warning.

lprint-lprint-using.md has a prominent implementation note: "⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter."

Both reference obsolete hardware (tape punches/teletypes vs line printers), but only LPRINT has the implementation warning. NULL should probably also have a similar warning since tape punches and 10-character-per-second devices are equally obsolete.

---

#### documentation_inconsistency

**Description:** Array documentation doesn't cross-reference OPTION BASE

**Affected files:**
- `docs/help/common/language/statements/option-base.md`
- `docs/help/common/language/statements/read.md`

**Details:**
read.md states: "Variables in the list may be subscripted. Array elements must be dimensioned before being referenced in a READ statement."

However, it doesn't mention OPTION BASE in the See Also section, even though OPTION BASE affects array subscripting. option-base.md only references DIM and ERASE in its See Also section.

While not strictly an error, array-related documentation could benefit from consistent cross-referencing of OPTION BASE.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting

**Affected files:**
- `docs/help/common/language/statements/out.md`
- `docs/help/common/language/statements/poke.md`

**Details:**
out.md states: "⚠️ **Emulated as No-Op**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter."

poke.md states: "⚠️ **Emulated as No-Op**: This feature requires direct memory access and cannot be implemented in a Python-based interpreter."

The wording differs slightly: "is not implemented" vs "cannot be implemented". While both convey similar meaning, consistency in implementation notes would be better.

---

#### documentation_inconsistency

**Description:** Print zone width inconsistency

**Affected files:**
- `docs/help/common/language/statements/print.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
print.md states: "When items are separated by commas, values are printed in zones of 14 columns each: Columns 1-14 (first zone), Columns 15-28 (second zone)..."

printi-printi-using.md states: "Items separated by commas are printed in print zones" but doesn't specify the zone width.

While PRINT# likely uses the same 14-column zones as PRINT, this is not explicitly documented, creating potential ambiguity.

---

#### documentation_inconsistency

**Description:** PUT documentation mentions PRINT# for random files but LSET doesn't

**Affected files:**
- `docs/help/common/language/statements/put.md`
- `docs/help/common/language/statements/lset.md`

**Details:**
put.md Note section states: "PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer before a PUT statement."

lset.md states: "LSET is used with random access files to prepare data for writing with PUT" but doesn't mention that PRINT# can also be used.

This creates an incomplete picture in LSET documentation about alternative ways to prepare random file data.

---

#### documentation_inconsistency

**Description:** Inconsistent file extension documentation

**Affected files:**
- `docs/help/common/language/statements/save.md`
- `docs/help/common/language/statements/run.md`

**Details:**
save.md states '(With CP/M, the default extension .BAS is supplied.)' while run.md states 'File extension defaults to .BAS if not specified'. The phrasing should be consistent - either both mention CP/M or both use generic language.

---

#### documentation_inconsistency

**Description:** Inconsistent description of file closing behavior

**Affected files:**
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
stop.md states 'Unlike the END statement, the STOP statement does not close files.' system.md states 'When SYSTEM is executed: All open files are closed'. However, the 'See Also' sections are inconsistent - stop.md references CHAIN, CLEAR, COMMON which are not directly related to file closing, while system.md has the same references. The relationship between these commands and file handling should be clarified consistently.

---

#### documentation_inconsistency

**Description:** Missing version information

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
tron-troff.md does not include a 'Versions:' field in the frontmatter, unlike most other statement documentation files. Should specify which BASIC versions support TRON/TROFF.

---

#### documentation_inconsistency

**Description:** Inconsistent title formatting for WRITE statements

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md uses title 'WRITE (Screen)' while writei.md uses title 'WRITE# (File)'. The parenthetical descriptions are helpful but the formatting should be consistent. Consider using 'WRITE (Screen)' and 'WRITE# (File)' or 'WRITE - Screen' and 'WRITE# - File'.

---

#### documentation_inconsistency

**Description:** SETSETTING and SHOWSETTINGS reference HELPSETTING but no such doc exists

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/language/statements/showsettings.md`

**Details:**
Both setsetting.md and showsettings.md list 'helpsetting' in their 'related' frontmatter field and reference it in 'See Also' sections. However, there is no helpsetting.md file in the documentation. Either the file is missing or the references should be removed.

---

#### documentation_inconsistency

**Description:** RUN documentation has inconsistent syntax description

**Affected files:**
- `docs/help/common/language/statements/run.md`

**Details:**
The Syntax section shows:
```basic
RUN [line number]
RUN "filename"
```
But the Remarks section describes three forms:
- RUN (no arguments)
- RUN line-number
- RUN "filename"

The syntax section should include all three forms explicitly:
```basic
RUN
RUN [line number]
RUN "filename"
```

---

#### documentation_inconsistency

**Description:** Curses editing documentation references undefined keyboard shortcuts

**Affected files:**
- `docs/help/common/ui/curses/editing.md`

**Details:**
The document uses placeholders like {{kbd:run:curses}}, {{kbd:parse:curses}}, {{kbd:new:curses}}, {{kbd:save:curses}}, {{kbd:continue:curses}} but states 'See your UI's keyboard shortcuts documentation for the complete list.' without providing a specific link. Should link to the actual curses keyboard shortcuts documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent description of Web UI file uppercasing behavior

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md states:
- Automatically uppercased by the virtual filesystem (CP/M style)
- The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage

This detailed explanation is missing from extensions.md, which only mentions 'simple filenames only' without explaining the uppercasing behavior.

---

#### documentation_inconsistency

**Description:** Incomplete keyboard shortcut table with template variables not rendered

**Affected files:**
- `docs/help/common/ui/tk/index.md`

**Details:**
The keyboard shortcuts table contains unrendered template variables:
| **{{kbd:file_new:tk}}** | New program |
| **{{kbd:file_open:tk}}** | Open file |
| **{{kbd:file_save:tk}}** | Save file |
| **{{kbd:run_program:tk}}** | Run program |
| **{{kbd:find:tk}}** | Find |

These should be replaced with actual keyboard shortcuts (e.g., Ctrl+N, Ctrl+O, etc.) or the template system should be documented.

---

#### documentation_inconsistency

**Description:** LPRINT statement behavior unclear in features list

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md states:
- **LPRINT** - Line printer output (Note: Statement is parsed but produces no output - see `[LPRINT](../common/language/statements/lprint-lprint-using.md)` for details)

This note suggests LPRINT is a no-op, but it's listed under 'Console I/O' features as if it's functional. This should be clarified or moved to a 'Compatibility Stubs' section.

---

#### documentation_inconsistency

**Description:** Inconsistent command prompt representation

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/ui/cli/index.md`

**Details:**
getting-started.md shows the MBASIC prompt as 'Ok' in examples:
```
10 PRINT "Hello, World!"
20 END
RUN
```

But cli/index.md shows it as 'Ok' with different formatting:
```
Ok
LOAD "MYPROGRAM.BAS"
RUN
```

The actual prompt format should be consistent across documentation.

---

#### documentation_inconsistency

**Description:** Self-contradictory statement about LINE command

**Affected files:**
- `docs/help/mbasic/not-implemented.md`

**Details:**
The document states: 'LINE - Draw line (GW-BASIC graphics version - not the LINE INPUT statement which IS implemented)'

This is confusing because it says LINE is not implemented, but then clarifies that LINE INPUT is implemented. The phrasing could be clearer that there are two different commands: LINE (graphics, not implemented) and LINE INPUT (file I/O, implemented).

---

#### documentation_inconsistency

**Description:** Document describes CP/M MBASIC implementation but unclear if this applies to the Python implementation

**Affected files:**
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`

**Details:**
The string-allocation-and-garbage-collection.md document provides extensive detail about 'CP/M era Microsoft BASIC-80 (MBASIC)' and 'Intel 8080 assembly implementation'. However, the getting-started.md describes this project as 'a complete Python implementation of MBASIC-80'.

It's unclear whether:
1. The Python implementation replicates the exact O(n²) garbage collection algorithm
2. This is historical documentation only
3. The Python implementation uses modern garbage collection

The document should clarify its relevance to the current Python implementation.

---

#### documentation_inconsistency

**Description:** Placeholder documentation file that should be completed or removed

**Affected files:**
- `docs/help/ui/common/running.md`

**Details:**
running.md is marked as 'PLACEHOLDER - Documentation in progress' and contains minimal information. It references UI-specific docs but those paths may not all exist:
- CLI: `docs/help/ui/cli/` (exists)
- Curses: `docs/help/ui/curses/running.md` (referenced in other docs)
- TK: `docs/help/ui/tk/` (not seen in provided files)
- Web: `docs/help/ui/web/` (not seen in provided files)

Either complete this common documentation or remove it and ensure all UI-specific running docs exist.

---

#### documentation_inconsistency

**Description:** Installation instructions reference files that may not exist

**Affected files:**
- `docs/help/mbasic/getting-started.md`

**Details:**
getting-started.md installation section references:
- 'pip install -r requirements.txt' - but no requirements.txt file is shown in docs
- 'mbasic' command without .py extension - unclear if this is a shell script or Python module

Should clarify:
1. Whether requirements.txt exists and what it contains
2. How the 'mbasic' command is installed/configured
3. Whether it's 'python mbasic.py' or an installed command

---

#### documentation_inconsistency

**Description:** Typo in keyboard shortcut placeholder

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
Multiple instances of '{{kbd:save:curses}}hift+O' and '{{kbd:save:curses}}hift+B' appear to be typos where 'S' from 'Shift' got concatenated with the kbd template. Should likely be 'Shift+{{kbd:open:curses}}' and 'Shift+{{kbd:toggle_breakpoint:curses}}' or similar.

---

#### documentation_inconsistency

**Description:** UI comparison table shows conflicting debugger support

**Affected files:**
- `docs/help/ui/index.md`

**Details:**
The comparison table shows Web UI has 'Limited' debugger support, but doesn't specify what limitations exist compared to Curses and Tk which show full support (✓).

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut references for file operations

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
getting-started.md uses {{kbd:save_file}} in the shortcuts table, but features.md uses {{kbd:file_save}} in the Tips section. These should be consistent - likely {{kbd:file_save}} is correct based on the pattern of file_new, file_save, etc.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut references within same document

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md uses both {{kbd:help:web}}1 and {{kbd:help:web}}2 for browser DevTools shortcuts, but earlier in the same document states that function key shortcuts are not implemented. This is internally inconsistent.

---

#### documentation_inconsistency

**Description:** Context Help shortcut not using template notation

**Affected files:**
- `docs/help/ui/tk/features.md`

**Details:**
features.md documents 'Context Help (Shift+F1)' with a hardcoded shortcut instead of using the {{kbd:...}} template notation. This should be {{kbd:context_help}} or similar for consistency with other shortcuts in the document.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation format

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md uses placeholder notation: {{kbd:run:web}}, {{kbd:stop:web}}, {{kbd:step:web}}, {{kbd:continue:web}}, {{kbd:help:web}}

web-interface.md uses actual keyboard shortcuts: Ctrl+V, Ctrl+A, Ctrl+C, Ctrl+K

The {{kbd:...}} placeholders appear to be template variables that should be replaced with actual shortcuts, but they're left unreplaced in the published documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent description of Step Line keyboard shortcut

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md states: "Step Line - Execute all statements on current line, then pause (⏭️ button, Ctrl+K)"

web-interface.md does not mention Ctrl+K for Step Line in its keyboard shortcuts section, only listing Ctrl+V, Ctrl+A, Ctrl+C.

This creates ambiguity about whether Ctrl+K is actually implemented for Step Line.

---

#### documentation_inconsistency

**Description:** Inconsistent program count in library statistics

**Affected files:**
- `docs/library/index.md`

**Details:**
The main library index states: 'Library Statistics: 202 programs from the 1970s-1980s'

However, counting the documented programs across all category index files would be needed to verify this number is accurate. The telecommunications category alone shows only 5 programs (Bmodem, Bmodem1, Command, Exitbbs1, Xtel), and utilities shows 18 programs. Without seeing all category files, this count cannot be verified but should be checked for accuracy.

---

#### documentation_inconsistency

**Description:** Contradictory information about CLI debugging capabilities

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
The CHOOSING_YOUR_UI.md document contains contradictory statements about CLI debugging:

In the CLI section 'Limitations': 'No visual debugging (text commands only)'

But then in 'Unique advantages': 'Command-line debugging (BREAK, STEP, STACK commands)'

And later a note clarifies: 'Note: CLI has full debugging capabilities through commands (BREAK, STEP, STACK), but lacks the visual debugging interface (Variables Window, clickable breakpoints, etc.) found in Curses, Tk, and Web UIs.'

The initial 'Limitations' statement is misleading - it should clarify that CLI has debugging commands but lacks visual debugging UI, not imply it has no debugging at all.

---

#### documentation_inconsistency

**Description:** Missing program descriptions in telecommunications category

**Affected files:**
- `docs/library/telecommunications/index.md`

**Details:**
The telecommunications/index.md file lists 5 programs but provides no descriptions for any of them:

- Bmodem: No description, empty tags
- Bmodem1: No description, empty tags
- Command: No description, empty tags
- Exitbbs1: No description, empty tags
- Xtel: No description, empty tags

All other category index files (utilities, etc.) provide descriptions and tags for their programs. This category appears incomplete compared to the documentation standard established elsewhere.

---

