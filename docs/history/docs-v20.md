# Documentation Issues - v20

Generated: 2025-11-10
Source: docs_inconsistencies_report-v20.md
Category: Documentation/comment fixes (no code behavior changes)

## Issues

#### 🔴 High Severity

---

#### code_vs_comment

**Description:** Comment claims identifiers preserve original case but implementation may not match runtime behavior

**Affected files:**
- `src/case_string_handler.py`

**Details:**
In case_keepy_string method for 'idents':
"# Identifiers (variable/function names) always preserve original case in display.
# Unlike keywords (which follow case_style policy), identifiers retain case as typed.
# This matches MBASIC 5.21: identifiers are case-insensitive for matching but
# preserve display case. Case-insensitive matching happens at runtime (runtime.py
# uses lowercase keys) and parsing (uses normalized forms), while this function
# only handles display formatting.
return original_text"

The comment claims runtime.py uses lowercase keys for case-insensitive matching, but this file doesn't show that implementation. This creates a dependency assumption that may not be verified. If runtime.py doesn't actually use lowercase keys, this comment is misleading.

---

---

#### Code vs Documentation inconsistency

**Description:** Numbered line editing feature has extensive validation requirements not mentioned in main docstring

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The execute() method has a large comment block describing numbered line editing:
"This feature requires the following UI integration:
- interpreter.interactive_mode must reference the UI object (checked with hasattr)
- UI.program must have add_line() and delete_line() methods (validated, returns error tuple if missing)
- UI._refresh_editor() method to update the display (optional, checked with hasattr)
- UI._highlight_current_statement() for restoring execution highlighting (optional, checked with hasattr)
If interactive_mode doesn't exist or is falsy, returns (False, error_message) tuple.
If interactive_mode exists but required program methods are missing, returns (False, error_message) tuple."

However, the class docstring and execute() method docstring make no mention of this numbered line editing feature at all. The Examples section in execute() docstring doesn't show numbered line examples. This is a significant feature that should be documented at the class/method level, not just in implementation comments.

---

---

#### Code vs Comment conflict

**Description:** The sanitize_input() docstring claims it 'Filters out: Extended ASCII (128-255)' but the function implementation only checks is_valid_input_char() which accepts codes 32-126, 9, 10, and 13. However, after parity clearing in the typical usage flow, characters 128-255 would be converted to 0-127 first. The docstring describes behavior that assumes parity bits are still set, but sanitize_input() is called AFTER clear_parity_all() in the main function.

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
sanitize_input() docstring:
"Filters out:
- Control characters (except tab, newline, CR)
- Extended ASCII (128-255)
- Non-ASCII Unicode"

But in sanitize_and_clear_parity():
"# First clear parity bits
cleared = clear_parity_all(text)
# Then sanitize control characters
sanitized = sanitize_input(cleared)"

By the time sanitize_input() is called, there are no characters in range 128-255 because they've been converted to 0-127. The docstring describes a capability that's never actually used in practice.

---

---

#### code_vs_comment

**Description:** Comment claims execute_command() handles commands directly, but code shows it calls execute_immediate() for most commands

**Affected files:**
- `src/interactive.py`

**Details:**
Module docstring (line ~10): 'Note: Line number detection happens first in process_line(), then non-numbered lines go to execute_command() where AUTO/EDIT/HELP are handled before attempting to parse as BASIC statements.'

Comment in execute_command() (line ~215): 'Everything else (including LIST, DELETE, RENUM, FILES, RUN, LOAD, SAVE, MERGE, SYSTEM, NEW, PRINT, etc.) goes through the real parser as immediate mode statements'

But the code in execute_command() (line ~200-220) shows that it only handles AUTO, EDIT, and HELP directly, then calls execute_immediate(cmd) for everything else. However, there's no execute_immediate() method defined in this file! This suggests the comment is wrong or the code is incomplete.

---

---

#### code_vs_comment

**Description:** current_statement_char_end docstring describes three cases but implementation logic doesn't clearly match case 2 description

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 99-111 says:
"2. Last statement on line AND line_text_map available: Returns len(line_text)
   - Returns the full line length including any trailing spaces/comments
   - This may be larger than char_end if trailing content exists"

But code at lines 119-127 shows:
"if pc.line_num in self._interpreter.runtime.line_text_map:
    line_text = self._interpreter.runtime.line_text_map[pc.line_num]
    # Return length of line (end of line)
    return len(line_text)
else:
    return stmt_char_end"

The comment "Return length of line (end of line)" doesn't mention "including trailing spaces/comments" as the docstring claims. The implementation returns len(line_text) which may or may not include trailing content depending on how line_text_map is populated. The docstring makes a claim about behavior that isn't verified by the code.

---

---

#### code_vs_comment

**Description:** execute_next comment describes validation logic that contradicts the actual validation code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says:
"# return_stmt is 0-indexed offset into statements array.
# Valid range:
#   - 0 to len(statements)-1: Normal statement positions (existing statements)
#   - len(statements): Special sentinel value - FOR was last statement on line,
#                      continue execution at next line (no more statements to execute on current line)
#   - > len(statements): Invalid - indicates the statement was deleted
#
# Validation: Check for strictly greater than (== len is OK as sentinel)
if return_stmt > len(line_statements):
    raise RuntimeError(f\"NEXT error: FOR statement in line {return_line} no longer exists\")"

This describes len(statements) as a valid sentinel value, but the validation code raises an error for return_stmt > len(line_statements), which would include len(statements)+1, len(statements)+2, etc. The comment should clarify that ONLY len(statements) is valid as sentinel, not any value > len(statements)-1.

---

---

#### code_vs_comment

**Description:** serialize_let_statement docstring claims LET is never output, but doesn't match actual AST design intent

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring says: 'Design decision: LetStatementNode represents both explicit LET statements and implicit assignments in the AST. This serializer intentionally ALWAYS outputs the implicit assignment form (A=5) without the LET keyword, regardless of the original source.'

However, the docstring also says: 'The AST intentionally does not distinguish between explicit LET and implicit assignment forms, as they are semantically equivalent (by design, not limitation)'

This creates ambiguity: if the AST doesn't distinguish by design, how can the serializer know whether to preserve the original LET keyword? The comment suggests this is a deliberate choice to normalize output, but it contradicts the claim that position preservation is a goal of the serializer.

---

---

#### code_vs_comment

**Description:** Comment says immediate mode status is updated after operations, but multiple code paths don't call _update_immediate_status()

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple methods have comments like:
'# Update immediate status (allows immediate mode again) - error message is in output'
'# Update immediate status (allows immediate mode again) - completion message is in output'

But several error paths don't call _update_immediate_status():
1. _debug_step() line ~730: 'except Exception' block doesn't call it (comment says 'Don't update immediate status on exception')
2. _debug_step_line() line ~810: 'except Exception' block doesn't call it
3. _debug_stop() line ~820: 'except Exception' block doesn't call it

This creates inconsistent behavior where immediate mode may remain disabled after errors.

---

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC when running and not paused, but implementation has contradictory logic

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Docstring at line ~1145 says:
PC handling:
- If running and not paused at breakpoint: Preserves PC and execution state
- If paused at breakpoint: Resets PC to halted (prevents accidental resumption)
- If not running: Resets PC to halted for safety

But code at line ~1175 does:
if self.running and not self.paused_at_breakpoint:
    # Execution is running - preserve execution state
    self.runtime.pc = old_pc
    self.runtime.halted = old_halted
else:
    # No execution in progress or paused at breakpoint - ensure halted
    self.runtime.pc = PC.halted_pc()
    self.runtime.halted = True

This appears consistent - the code matches the comment.

---

---

#### code_vs_comment

**Description:** Comment in _execute_immediate claims it doesn't call interpreter.start() to avoid resetting PC, but this contradicts expected behavior after RUN command

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1625 says:
# NOTE: Don't call interpreter.start() here. The immediate executor handles
# program start setup (e.g., RUN command sets PC appropriately via
# interpreter.start()). This function only ensures InterpreterState exists
# for tick-based execution tracking. If we called interpreter.start() here,
# it would reset PC to the beginning, overriding the PC set by RUN command.

But then code creates InterpreterState manually:
from src.interpreter import InterpreterState
if not hasattr(self.interpreter, 'state') or self.interpreter.state is None:
    self.interpreter.state = InterpreterState(_interpreter=self.interpreter)
self.runtime.halted = False
self.interpreter.state.is_first_line = True

This suggests the immediate executor's RUN command already called interpreter.start(), so this code is just ensuring state exists. The comment is explaining why NOT to call start() again.

---

---

#### code_vs_comment_conflict

**Description:** Comment claims help navigation keys are hardcoded and not loaded from keybindings JSON, but code actually does load keybindings via HelpMacros

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~73 states:
"Note: Help navigation keys are HARDCODED (not loaded from keybindings JSON) to avoid circular dependency issues. The help widget uses fixed keys (U for back, / for search, ESC/Q to exit) that work regardless of user keybinding customization.

Note: HelpMacros (instantiated below) DOES load keybindings from JSON, but only for macro expansion in help content ({{kbd:action}} substitution). The help widget's own navigation doesn't consult those loaded keybindings - it uses hardcoded keys."

However, the code at line ~48 shows:
self.macros = HelpMacros('curses', help_root)

And help_macros.py _load_keybindings() method (line ~28) loads keybindings JSON:
keybindings_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"

The comment is technically correct that help_widget.py's keypress() method uses hardcoded keys, but the phrasing "not loaded from keybindings JSON" is misleading since HelpMacros does load the JSON (just for different purpose).

---

---

#### documentation_inconsistency

**Description:** Multiple keybinding systems exist with unclear relationships: keybindings.py (constants), keybinding_loader.py (JSON), and hardcoded keys in help_widget.py

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/help_widget.py`
- `src/ui/interactive_menu.py`
- `src/ui/keybinding_loader.py`

**Details:**
Three different keybinding approaches are used:

1. keybinding_loader.py (lines ~1-200+): Loads from JSON files like 'curses_keybindings.json', provides get_primary(), get_all_keys() methods

2. interactive_menu.py (line ~4): Imports 'from . import keybindings as kb' and uses constants like kb.NEW_KEY, kb.OPEN_KEY

3. help_widget.py (line ~73): Uses hardcoded keys in keypress() method, with comment explaining they're intentionally not loaded from JSON

4. help_macros.py (line ~28): Loads JSON keybindings but only for macro expansion

The relationship between these systems is unclear:
- Is keybindings.py (with constants) deprecated in favor of keybinding_loader.py (JSON)?
- Why does interactive_menu.py use the old system while keybinding_loader.py exists?
- Are there two separate keybinding files: keybindings.py and curses_keybindings.json?

This needs architectural clarification.

---

---

#### code_vs_comment

**Description:** Comment claims lines match program manager's formatted output but char positions may not align

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1420 states: "Lines in the editor match the program manager's formatted output (see _refresh_editor). The char_start/char_end positions from runtime correspond to the displayed line text, so they are directly usable as Tk text indices."

This assumes perfect alignment between runtime's character positions and editor display positions. However, if the program manager adds any formatting (extra spaces, tabs, etc.) during _refresh_editor, the character positions would be offset. This needs verification that _refresh_editor preserves exact character positions.

---

---

#### code_vs_comment

**Description:** Method name _add_immediate_output() contradicts its documented and actual behavior

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method at line 1220 is named '_add_immediate_output' but docstring states:
"Add text to main output pane.

Note: This method name is historical/misleading - it actually adds to the main output pane, not a separate immediate output pane. It simply forwards to _add_output(). In the Tk UI, immediate mode output goes to the main output pane. self.immediate_history is always None (see __init__)."

The method name suggests it outputs to immediate mode area, but it actually outputs to main pane. This is a naming inconsistency that could confuse maintainers.

---

---

#### code_vs_comment

**Description:** Maintenance risk warning about duplicated logic that could become inconsistent

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method around line 1180, comment states:
"NOTE: Don't call interpreter.start() because it calls runtime.setup() which resets PC to the first statement. The RUN command has already set PC to the correct line (e.g., RUN 120 sets PC to line 120). Instead, we manually perform minimal initialization here.

MAINTENANCE RISK: This duplicates part of start()'s logic (see interpreter.start() in src/interpreter.py). If start() changes, this code may need to be updated to match."

This indicates code duplication between tk_ui.py and interpreter.py that could lead to inconsistencies if one is updated without the other.

---

---

#### code_vs_comment_conflict

**Description:** Comment in _on_status_click() claims it does NOT toggle breakpoints, but the docstring says it shows 'confirmation message for ●' which implies informational only. However, the method name and context suggest it should handle clicks, and the comment explicitly states toggling is handled elsewhere. The actual implementation only shows messages and never toggles breakpoints, so the code matches the comment, but the method binding and user expectation from clicking a status column would typically be to toggle.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring says: 'Handle click on status column (show error details for ?, confirmation message for ●).'

Comment says: 'Note: This displays information messages only. It does NOT toggle breakpoints - that's handled by the UI backend's breakpoint toggle command (e.g., TkBackend._toggle_breakpoint(), accessed via ^B in Tk UI or menu).'

Code implementation: Only calls messagebox.showerror() or messagebox.showinfo(), never toggles breakpoints.

The inconsistency is that users clicking on a breakpoint indicator (●) in a status column would typically expect to toggle it, but this implementation only shows an info message. This is a UX design issue where the comment clarifies the limitation but the design itself may be counterintuitive.

---

---

#### code_vs_comment

**Description:** Duplicate comment about INPUT prompt handling in _execute_tick - same note appears twice with identical wording, suggesting copy-paste error or refactoring artifact.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _execute_tick method, the following comment appears twice (around lines 1900 and 1930):
"# Note: We don't append the prompt to output here because the interpreter
# has already printed it via io.output() before setting input_prompt state.
# Verified: INPUT statement calls io.output(prompt) before awaiting user input."

This duplication suggests the code may have been refactored and the comment was not cleaned up properly.

---

---

#### documentation_inconsistency

**Description:** Self-contradictory information about DOUBLE precision in data-types.md

**Affected files:**
- `docs/help/common/language/data-types.md`

**Details:**
The DOUBLE Precision section contains contradictory statements:
1. 'Floating-point numbers with about 16 decimal digits of precision'
2. Later: 'approximately 16 digits'
The document uses both 'about' and 'approximately' to describe the same value, and the precision description is inconsistent within the same section.

---

---

#### documentation_inconsistency

**Description:** FOR-NEXT loop termination test description is contradictory within the same document

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
The document states:
"### Loop Termination:
The termination test happens AFTER each increment/decrement at the NEXT statement:
- **Positive STEP** (or no STEP): Loop continues while variable <= ending value
- **Negative STEP**: Loop continues while variable >= ending value"

But then the examples show:
"For example:
- `FOR I = 1 TO 10` executes with I=1,2,3,...,10 (10 iterations). After I=10 executes, NEXT increments to 11, test fails (11 > 10), loop exits."

This is internally consistent, but the phrasing 'Loop continues while variable <= ending value' followed by 'test fails (11 > 10)' could be clearer. The test that 'fails' is actually the continuation condition, which might confuse readers.

---

---

#### documentation_inconsistency

**Description:** SAVE documentation mentions MERGE requiring ASCII format, but MERGE is not in the related statements list

**Affected files:**
- `docs/help/common/language/statements/save.md`
- `docs/help/common/language/statements/run.md`

**Details:**
SAVE.md mentions: 'For instance, the MERGE command requires an ASCII format file'

But the 'See Also' section does not include MERGE, only: KILL, LOAD, MERGE (wait, it does say MERGE), NAME.

Actually, looking again, MERGE IS in the See Also. This may not be an issue. Let me re-examine...

Actually the See Also does include MERGE. This is not an inconsistency.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about EDIT command availability

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`

**Details:**
CLI docs state 'The CLI includes a line editor accessed with the EDIT command' and references 'See: [EDIT Command](../../language/statements/edit.md)', but Curses docs make no mention of an EDIT command despite being a full-screen editor. The CLI description suggests EDIT is a command-mode feature, but it's unclear if this command exists in the Curses UI or if line editing works differently there.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI file persistence

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
Compatibility.md states 'Note: Settings (not files) can persist via Redis if configured - see [Web UI Settings](../ui/web/settings.md)' suggesting some persistence mechanism exists. However, extensions.md clearly states 'Files persist during browser session only (lost on page refresh)' and 'No persistent storage across sessions'. The compatibility doc's mention of Redis persistence for settings creates confusion about what can and cannot persist.

---

---

#### documentation_inconsistency

**Description:** Broken or inconsistent internal documentation links

**Affected files:**
- `docs/help/index.md`
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
Multiple docs reference links that may not exist or use inconsistent paths:
- CLI: '[EDIT Command](../../language/statements/edit.md)'
- Curses: '[RENUM Command](../../language/statements/renum.md)', '[AUTO Command](../../language/statements/auto.md)', '[DELETE Command](../../language/statements/delete.md)'
- Tk: '[Examples](../../examples/hello-world.md)'
- Index: '[Hello World](common/examples/hello-world.md)', '[Loops and Control Flow](common/examples/loops.md)'
These links should be verified to ensure they point to existing files with correct relative paths.

---

---

#### documentation_inconsistency

**Description:** Missing keyboard shortcut for Clear All Breakpoints

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md states: "### Clear All Breakpoints (Shift+^B)
Remove all breakpoints from the program at once. Use Shift+Ctrl+B keyboard shortcut."

But quick-reference.md does not list this shortcut in any of its tables. This is a significant omission for a debugging feature.

---

---

#### documentation_inconsistency

**Description:** Conflicting information about Find/Replace keyboard shortcuts and functionality

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states:
"Find/Replace ({{kbd:find:tk}} / {{kbd:replace:tk}})
Powerful search and replace functionality:
- Find: {{kbd:find:tk}} - Opens Find-only dialog
- Replace: {{kbd:replace:tk}} - Opens combined Find/Replace dialog (includes both find and replace)"

But features.md states:
"Find and Replace
**Find text ({{kbd:find:tk}}):**
- Opens Find dialog with search options
**Replace text ({{kbd:replace:tk}}):**
- Opens combined Find/Replace dialog
**Note:** {{kbd:find:tk}} opens the Find dialog. {{kbd:replace:tk}} opens the Find/Replace dialog which includes both Find and Replace functionality."

The inconsistency is whether {{kbd:find:tk}} opens a "Find-only dialog" (feature-reference.md) or a "Find dialog with search options" (features.md). The note in features.md suggests they are different dialogs, but feature-reference.md says Replace dialog "includes both find and replace" implying Find is separate.

---

---

#### documentation_inconsistency

**Description:** Settings dialog implementation status unclear across documents

**Affected files:**
- `docs/help/ui/tk/settings.md`
- `docs/help/ui/tk/index.md`
- `docs/help/ui/tk/features.md`

**Details:**
settings.md clearly states at the top:
"**Implementation Status:** The Tk (Tkinter) desktop GUI is planned to provide a comprehensive settings dialog. **The settings dialog itself is not yet implemented**"

And later:
"**Current Status:** Many TK UI features work (auto-save, syntax checking, breakpoints, etc.) but the graphical settings dialog is not yet implemented."

However, index.md and features.md do not mention this limitation. They describe settings features as if they exist:
- index.md: "Settings & Configuration - Variable case, keyword case, and more"
- features.md does not mention settings at all

This creates confusion about what is actually available.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about program storage and auto-save functionality

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/settings.md`

**Details:**
features.md states under 'Local Storage > Currently Implemented': 'Program content stored in Python server memory (session-only, lost on page refresh)' and 'Recent files list (filenames only) stored in browser localStorage (persists across sessions)'. However, it also lists 'Automatic Saving (Planned)' as a future feature that 'Saves programs to browser localStorage for persistence'.

Meanwhile, getting-started.md says: 'Note: The Web UI uses browser downloads for saving program files to your computer. Auto-save of program code to browser localStorage is planned for a future release. (Note: Your editor settings ARE already saved to localStorage - see [Settings](settings.md))'

And settings.md under 'Settings Storage' describes two storage modes: 'Local Storage (Default)' where 'Settings persist across page reloads' and 'Redis Session Storage' for multi-user deployments.

The confusion is: Are programs currently stored in server memory OR localStorage? The docs say both. Are settings stored in localStorage (as getting-started.md and settings.md claim) or is this also planned? The 'Currently Implemented' vs 'Planned' markers are contradictory.

---

---

#### documentation_inconsistency

**Description:** QUICK_REFERENCE.md uses {{kbd:command}} notation but doesn't explain what it means or how to interpret it

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`

**Details:**
The document starts with:
'> **Note:** This reference uses `{{kbd:command}}` notation for keyboard shortcuts. Actual key mappings are configurable.'

But then uses shortcuts like:
'`{{kbd:new}}` | New | Clear program, start fresh'
'`{{kbd:open}}` | Load | Load program from file'

It's unclear what the actual default keys are. A user reading this doesn't know if {{kbd:new}} means 'N', 'Ctrl+N', 'F1', or something else. The reference to 'check ~/.mbasic/curses_keybindings.json' doesn't help a new user who hasn't run the program yet.

---

---

#### documentation_inconsistency

**Description:** Multiple settings marked as 'PLANNED' but status note at top says 'settings system is implemented and available in all UIs'

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
Top of document states:
'> **Status:** The settings system is implemented and available in all UIs. Core commands (SET, SHOW SETTINGS, HELP SET) work as documented.'

But then lists multiple settings as 'PLANNED':
- 'interpreter.strict_mode' - '**Status:** 🔧 PLANNED - Not yet implemented'
- 'interpreter.debug_mode' - '**Status:** 🔧 PLANNED - Not yet implemented'
- 'ui.theme' - '**Status:** 🔧 PLANNED - Not yet implemented'
- 'ui.font_size' - '**Status:** 🔧 PLANNED - Not yet implemented'

This is confusing - the settings *system* is implemented, but many individual *settings* are not. The distinction should be clearer upfront.

---

---

#### 🟡 Medium Severity

---

#### Documentation inconsistency

**Description:** Version number inconsistency between setup.py and ast_nodes.py module docstring

**Affected files:**
- `setup.py`
- `src/ast_nodes.py`

**Details:**
setup.py states 'Package version: 0.99.0 (reflects approximately 99% implementation status - core complete)' and 'Language version: MBASIC 5.21 (Microsoft BASIC-80 for CP/M)'. The ast_nodes.py module docstring only mentions '5.21 refers to the Microsoft BASIC-80 language version, not this package version' but doesn't mention the package version 0.99.0 anywhere. This creates potential confusion about versioning.

---

---

#### Code vs Comment conflict

**Description:** keyword_token fields documented as 'legacy, not currently used' but still present in multiple statement nodes

**Affected files:**
- `src/ast_nodes.py`

**Details:**
PrintStatementNode, IfStatementNode, and ForStatementNode all have keyword_token fields with comments stating '(legacy, not currently used)'. The PrintStatementNode docstring explains: 'Note: keyword_token fields are present in some statement nodes (PRINT, IF, FOR) but not others. These were intended for case-preserving keyword regeneration but are not currently used by position_serializer, which handles keyword case through apply_keyword_case_policy() and the KeywordCaseManager instead.' This suggests technical debt where unused fields remain in the codebase.

---

---

#### code_vs_comment

**Description:** Comment describes INPUT$ method receiving file number WITHOUT # prefix, but the actual BASIC syntax documentation shows #filenum with the # symbol

**Affected files:**
- `src/basic_builtins.py`

**Details:**
In INPUT method docstring:
"This method receives the file number WITHOUT the # prefix (parser strips it)."

But then shows:
"BASIC syntax:
    INPUT$(n, #filenum) - read n characters from file"

The comment says the method receives WITHOUT #, but the BASIC syntax example shows WITH #. This is confusing - the comment should clarify that BASIC source uses # but the parser strips it before calling the method.

---

---

#### code_vs_comment

**Description:** format_numeric_field has confusing comment about sign behavior that contradicts itself

**Affected files:**
- `src/basic_builtins.py`

**Details:**
In format_numeric_field method:
"Determine sign BEFORE rounding (for negative zero handling)"
Then:
"original_negative = value < 0"
Then later:
"# Determine sign - preserve negative sign for values that round to zero.
# Use original_negative (captured above before rounding) to detect negative values that rounded to zero.
# This allows us to detect cases like -0.001 which round to 0 but should display as '-0' (not '0').
# This matches MBASIC 5.21 behavior: negative values that round to zero display as '-0',
# while positive values that round to zero display as '0'.
if rounded == 0 and original_negative:
    is_negative = True
else:
    # For non-zero values, use the rounded value's sign (normal case)
    is_negative = rounded < 0"

The comment is overly verbose and repeats the same concept multiple times. The logic is clear from the code itself.

---

---

#### code_vs_comment

**Description:** parse_numeric_field docstring describes sign behavior but has inconsistent terminology

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring says:
"Sign behavior:
- leading_sign: + at start, always adds + or - sign (reserves 1 char for sign)
- trailing_sign: + at end, always adds + or - sign (reserves 1 char for sign)
- trailing_minus_only: - at end, adds - for negative OR space for non-negative (reserves 1 char)"

But later in format_numeric_field code:
"# Note: trailing_minus_only adds - for negative OR space for non-negative (always reserves 1 char)"

The docstring says 'adds - for negative OR space' but doesn't emphasize 'always reserves 1 char' as strongly as the code comment does. The code comment is clearer about the space reservation.

---

---

#### code_vs_comment

**Description:** EOF function comment about ^Z detection references binary mode but doesn't explain text mode behavior clearly

**Affected files:**
- `src/basic_builtins.py`

**Details:**
EOF docstring says:
"Note: For binary input files (OPEN statement mode 'I'), respects ^Z (ASCII 26)
as EOF marker (CP/M style).

Implementation details:
- execute_open() in interpreter.py stores mode ('I', 'O', 'A', 'R') in file_info['mode']
- Mode 'I' files are opened in binary mode ('rb'), allowing ^Z detection
- Text mode files (output 'O', append 'A') use standard Python EOF detection without ^Z"

This implies mode 'O' and 'A' are text mode, but doesn't mention mode 'R' (random access). The comment lists 'R' as a mode but doesn't explain its EOF behavior.

---

---

#### code_vs_comment

**Description:** Comment claims GOSUB return mechanism uses return line numbers, but code uses return IDs

**Affected files:**
- `src/codegen_backend.py`

**Details:**
Line 142 comment: 'int gosub_stack[100];  /* Return line numbers */'
But _generate_gosub() (lines 329-337) pushes return_id (not line numbers) onto stack:
code.append(self.indent() + f'gosub_stack[gosub_sp++] = {return_id};  /* Push return address */')

The stack stores unique return IDs (0, 1, 2...) for each GOSUB, not the BASIC line numbers to return to.

---

---

#### code_vs_documentation

**Description:** Documentation claims z88dk path is hardcoded for snap installation, but doesn't mention configuration alternatives

**Affected files:**
- `src/codegen_backend.py`

**Details:**
Lines 113-118 docstring:
'Platform requirement: Assumes z88dk is installed via snap on Linux at /snap/bin/z88dk.zcc.
This path is hardcoded and will not work on other platforms or installation methods.
For non-snap installations, modify this path or make z88dk.zcc available in PATH.'

The documentation acknowledges the hardcoded path limitation but doesn't describe any configuration mechanism to override it. Users would need to modify source code to use different z88dk installations. This could be improved with an environment variable or config file option.

---

---

#### Documentation inconsistency

**Description:** Contradictory documentation about which abstraction provides list_files() and delete() methods

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py states: "There is intentional overlap: both provide list_files() and delete() methods. FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for runtime access (though not all BASIC dialects support runtime file listing/deletion)."

src/filesystem/base.py states: "Note: There is intentional overlap between the two abstractions. Both provide list_files() and delete() methods, but serve different contexts: FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for runtime access (though not all BASIC dialects support runtime file operations)."

However, FileIO.delete_file() is documented as the method name in src/file_io.py, while FileSystemProvider.delete() is the method name in src/filesystem/base.py. The documentation claims they both provide 'delete()' methods but they have different names.

---

---

#### Code vs Comment conflict

**Description:** InMemoryFileHandle.flush() docstring contradicts the actual behavior of flush in file I/O

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
Docstring states: "Flush write buffers (no-op for in-memory files).

Note: This calls StringIO/BytesIO flush() which are no-ops. Content is only saved to the virtual filesystem on close(). Unlike standard file flush() which persists buffered writes to disk, in-memory file writes are already in memory, so flush() has no effect."

This is misleading. The comment correctly states that StringIO/BytesIO flush() are no-ops, but the claim that "content is only saved to the virtual filesystem on close()" is incorrect for the actual behavior. In-memory writes to StringIO/BytesIO are immediately visible to subsequent reads on the same handle - they don't need close() to be "saved". The close() method does call _save_file_content() to persist to the virtual filesystem dict, but the content is already in the StringIO/BytesIO buffer before that.

---

---

#### Code vs Comment conflict

**Description:** Comment about PC save/restore contradicts the actual design decision

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Comment states: "Note: We do not save/restore the PC before/after execution by design. This allows statements like RUN to properly change execution position. Tradeoff: Control flow statements (GOTO, GOSUB) can also modify PC but are not recommended in immediate mode as they may produce unexpected results (see help text). This design prioritizes RUN functionality over preventing potentially confusing GOTO/GOSUB behavior. Normal statements (PRINT, LET) don't modify PC and work as expected."

However, the help text in _show_help() states: "GOTO, GOSUB, and control flow statements are not recommended (they will execute but may produce unexpected results)"

The comment explains a deliberate design tradeoff, but doesn't acknowledge that this same design allows RUN to work but also means the PC state after immediate execution may be unpredictable if control flow statements are used. The comment frames this as "prioritizing RUN" but doesn't mention that RUN itself is a control flow statement that changes PC.

---

---

#### Code vs Documentation inconsistency

**Description:** Documentation claims INPUT will fail but doesn't specify when or how

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Help text states: "INPUT statement will fail at runtime in immediate mode (use direct assignment instead)"

Docstring for OutputCapturingIOHandler.input() states: "Input not supported in immediate mode.

User-facing behavior: INPUT statement will fail at runtime in immediate mode. Implementation detail: INPUT statements parse successfully but execution fails when the interpreter calls this input() method."

However, the actual implementation raises RuntimeError with message "INPUT not allowed in immediate mode". The documentation doesn't specify:
1. What error message the user will see
2. Whether this is a RuntimeError or some other exception type
3. Whether the error is caught and formatted by _format_error() or propagates to the caller

The user-facing help should probably show an example of what error they'll see.

---

---

#### Code vs Comment conflict

**Description:** Module docstring claims the module 'clears parity bits from incoming characters' as one of its two main functions, but the main entry point function sanitize_and_clear_parity() performs parity clearing BEFORE sanitization, not as a separate filtering step. The order matters and the docstring oversimplifies the relationship.

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Module docstring says:
"This module provides functions to sanitize user input by:
1. Filtering out unwanted control characters
2. Clearing parity bits from incoming characters"

But sanitize_and_clear_parity() implementation shows:
"# First clear parity bits
cleared = clear_parity_all(text)
# Then sanitize control characters
sanitized = sanitize_input(cleared)"

The docstring presents these as parallel operations, but they're sequential with parity clearing happening first.

---

---

#### code_vs_comment

**Description:** Comment claims digits 'silently do nothing' in EDIT mode, but code has no explicit handling for digits

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~1050 says: 'INTENTIONAL MBASIC-COMPATIBLE BEHAVIOR: When digits are entered, they silently do nothing (no output, no cursor movement, no error)... Implementation: digits fall through the command checks without matching any elif branch.'

However, in the actual edit loop (lines ~1090-1180), there is no explicit handling or documentation of digit behavior. The code only handles specific commands (Space, D, I, X, H, E, Q, L, A, C). If a digit is entered, it would fall through all the elif branches and do nothing, but this is implicit behavior, not explicitly documented in the code flow.

---

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about which commands are parsed vs handled directly

**Affected files:**
- `src/interactive.py`

**Details:**
Module docstring (line ~7) says: 'Direct commands: AUTO, EDIT, HELP (special-cased before parser, see execute_command())'

But then says: 'Immediate mode statements: Most commands (RUN, LIST, SAVE, LOAD, NEW, MERGE, FILES, SYSTEM, DELETE, RENUM, CONT, CHAIN, etc.) are parsed as BASIC statements and executed via execute_immediate()'

However, in execute_command() (line ~200), the code shows that RUN, LIST, DELETE, RENUM, NEW, SAVE, LOAD, MERGE, CONT, CHAIN are all handled by calling cmd_* methods directly (cmd_run, cmd_list, etc.), NOT by parsing them as BASIC statements through execute_immediate(). The comment at line ~215 says 'Everything else goes through the parser as immediate mode statements' but this contradicts the module docstring which lists these commands as going through the parser.

---

---

#### code_vs_comment

**Description:** Docstring for cmd_merge says it updates runtime statement_table, but condition is unclear

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring for cmd_merge() (line ~410): 'If merge is successful AND program_runtime exists, updates runtime's statement_table (for CONT support). Runtime update only happens after successful merge.'

Code at line ~450: 'if success:
    # Update runtime if it exists (for CONT support)
    if self.program_runtime:
        for line_num in self.program.line_asts:
            line_ast = self.program.line_asts[line_num]
            self.program_runtime.statement_table.replace_line(line_num, line_ast)'

The code updates ALL lines in the program, not just the merged lines. The docstring says 'updates runtime's statement_table' but doesn't clarify that it rebuilds the entire statement table, not just the merged lines. This could be inefficient if only a few lines were merged.

---

---

#### code_vs_comment_conflict

**Description:** Comment claims 'second return value is bool indicating if parity bits were found; not needed here' but sanitize_and_clear_parity() is called with only one assignment target

**Affected files:**
- `src/interactive.py`

**Details:**
Line in cmd_auto():
# Comment: '(second return value is bool indicating if parity bits were found; not needed here)'
Code: 'line_text, _ = sanitize_and_clear_parity(line_text)'

The comment describes the second return value but the code uses '_' to discard it, which is correct. However, the comment's phrasing '(second return value is bool...; not needed here)' suggests this is explanatory documentation, but it's unclear if sanitize_and_clear_parity() actually returns a tuple or just a single value. If it returns only one value, the unpacking would fail.

---

---

#### code_vs_comment_conflict

**Description:** Docstring for cmd_files() mentions 'Future enhancement: Could add drive letter mapping' but provides no implementation path

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring states:
'Note: Drive letter syntax (e.g., "A:*.*") from CP/M and DOS is not supported.
This is a modern implementation running on Unix-like and Windows systems where
CP/M-style drive letter prefixes don't apply. Use standard path patterns instead
(e.g., "*.BAS", "../dir/*.BAS"). Future enhancement: Could add drive letter mapping.'

This 'Future enhancement' note in a docstring is unusual - such notes typically belong in TODO comments or issue trackers, not user-facing documentation. It's unclear if this is meant to inform users (confusing) or developers (wrong location).

---

---

#### code_vs_comment

**Description:** Comment describes skip_next_breakpoint_check behavior incorrectly regarding when it's set and cleared

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 56-59 says:
"Set to True AFTER halting at a breakpoint (set after returning state).
On next execution, if still True, allows stepping past the breakpoint once,
then is cleared to False. Prevents re-halting on same breakpoint."

But code at lines 398-404 shows:
- It's checked BEFORE halting: "if not self.state.skip_next_breakpoint_check:"
- It's set to True WHEN halting: "self.state.skip_next_breakpoint_check = True"
- It's cleared AFTER skipping: "else: self.state.skip_next_breakpoint_check = False"

The comment suggests it's set after returning state, but the code sets it during tick_pc() before returning.

---

---

#### code_vs_comment

**Description:** Comment about version removal is misleading about what was removed

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 677-682 says:
"# OLD EXECUTION METHODS REMOVED (version 1.0.299)
# Note: The project has an internal implementation version (tracked in src/version.py)
# which is separate from the MBASIC 5.21 language version being implemented.
# Old methods: run_from_current(), _run_loop(), step_once() (removed in v1.0.299)
# These used old current_line/next_line fields (also removed in v1.0.299)
# Replaced by tick_pc() and PC-based execution"

But the comment says "CONT command now uses tick() directly" which is incomplete - the run() method at lines 619-663 still exists and uses the tick-based API, it wasn't removed. The comment makes it sound like everything was removed, but only specific methods were removed.

---

---

#### code_vs_comment

**Description:** Comment claims DELETE preserves variables and ALL runtime state, but code shows NEW also preserves some runtime state (user_functions, common_vars)

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_delete comment says:
"Note: This implementation preserves variables and ALL runtime state when deleting lines.
NEW clears both lines and variables (execute_new calls clear_variables/clear_arrays),
while DELETE only removes lines from the program AST, leaving variables, open files,
error handlers, and loop stacks intact."

But execute_clear shows:
"State preservation for CHAIN compatibility:

PRESERVED by CLEAR (not cleared):
  - runtime.common_vars (list of COMMON variable names - the list itself, not values)
  - runtime.user_functions (DEF FN functions)"

And execute_new calls clear_variables/clear_arrays which are also called by CLEAR, suggesting NEW also preserves common_vars and user_functions like CLEAR does.

---

---

#### code_vs_comment

**Description:** execute_clear comment says it differs from RESET in error handling, but execute_reset comment doesn't mention this difference

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_clear has:
"# Note: Only OS-level file errors (OSError, IOError) are silently ignored to match
# MBASIC behavior. This differs from RESET which allows errors to propagate."

execute_reset has:
"Note: Unlike CLEAR (which silently ignores file close errors), RESET allows
errors during file close to propagate to the caller. This is intentional
different behavior between the two statements."

Both mention the difference but from opposite perspectives. The inconsistency is minor but could be unified.

---

---

#### code_vs_comment

**Description:** execute_wend comment describes timing of pop operation but the explanation is confusing

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says:
"# Pop the loop from the stack (after setting npc above, before WHILE re-executes).
# Timing: We pop NOW so the stack is clean before WHILE condition re-evaluation.
# The WHILE will re-push if its condition is still true, or skip the loop body
# if false. This ensures clean stack state and proper error handling if the
# WHILE condition evaluation fails (loop already popped, won't corrupt stack)."

The comment says 'after setting npc above' but the pop operations happen AFTER the npc assignment:
self.runtime.npc = PC(loop_info['while_line'], loop_info['while_stmt'])
self.limits.pop_while_loop()
self.runtime.pop_while_loop()

The comment is technically correct but could be clearer about the sequence: set npc, THEN pop.

---

---

#### code_vs_comment_conflict

**Description:** LSET/RSET fallback behavior comment contradicts itself about whether it's a bug or intentional

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_lset() (line ~2675), the comment states:
"Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field variables... This fallback is a deliberate extension that performs simple assignment without left-justification."

Then adds: "Note: This extension behavior allows LSET/RSET to work as simple assignment operators when not used with FIELD, which is intentional flexibility in this implementation, not a bug or incomplete feature."

In execute_rset() (line ~2715), similar comment says:
"This fallback is a deliberate extension that performs simple assignment without right-justification. The formatting only applies when used with FIELD variables. This is documented behavior, not a bug."

The repetitive defensive language ("not a bug", "intentional", "documented behavior") suggests uncertainty about whether this is correct behavior or a workaround.

---

---

#### code_vs_comment_conflict

**Description:** String length limit enforcement is inconsistent across operations

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_binaryop() (line ~3025), comment states:
"Enforce 255 character string limit for concatenation (MBASIC 5.21 compatibility)
Note: This check only applies to concatenation via PLUS operator.
Other string operations (MID$, INPUT) do not enforce this 255-char limit.
LSET/RSET have different limits: they enforce field width limits (defined by FIELD statement) rather than the 255-char concatenation limit."

This creates inconsistency: why would MBASIC 5.21 compatibility require 255-char limit for PLUS but not for INPUT or MID$? Either MBASIC 5.21 had a global string limit or it didn't. The selective enforcement suggests incomplete understanding of the original behavior.

---

---

#### code_vs_comment_conflict

**Description:** CONT command PC handling explanation contradicts itself

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_cont() docstring (line ~2870) states:
"PC handling difference:
- STOP: execute_stop() explicitly moves NPC to PC (line 2808), ensuring CONT resumes from the statement AFTER the STOP.
- Break (Ctrl+C): BreakException handler (line 376-381) does NOT update PC, leaving PC pointing to the statement that was interrupted. This means CONT will re-execute the interrupted statement (typically INPUT where Break occurred)."

But execute_stop() (line ~2795) shows:
"self.runtime.pc = self.runtime.npc"

The comment says "moves NPC to PC" but the code shows "moves PC to NPC" (opposite direction). This is a critical error in the documentation of control flow behavior.

---

---

#### code_vs_comment_conflict

**Description:** LIST command implementation note suggests fragile design

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_list() docstring (line ~2770) states:
"Implementation note: Outputs from line_text_map (original source text), not regenerated from AST. This preserves original formatting/spacing/case. The line_text_map is maintained by ProgramManager and should be kept in sync with the AST during program modifications (add_line, delete_line, RENUM, MERGE). If ProgramManager fails to maintain this sync, LIST output may show stale or incorrect line text."

This comment acknowledges a potential data consistency bug but doesn't explain why this design was chosen over a more robust approach (e.g., always regenerating from AST, or having a single source of truth). The phrase "If ProgramManager fails to maintain this sync" suggests this is a known fragility.

---

---

#### Code vs Documentation inconsistency

**Description:** web_io.py implements get_screen_size() method which is not part of IOHandler interface and not documented in base.py

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/web_io.py`

**Details:**
base.py IOHandler interface does not define get_screen_size() method.

web_io.py implements:
    def get_screen_size(self):
        '''Get terminal size.
        Returns:
            Tuple of (rows, cols) - returns reasonable defaults for web
        Note: This is a web_io-specific method, not part of the IOHandler base interface.'''
        return (24, 80)

The method's own docstring acknowledges it's not part of the base interface, but base.py's class docstring mentions: "Note: Implementations may provide additional methods beyond this interface for backend-specific functionality (e.g., web_io.get_screen_size())." This is documented in base.py but as an example of backend-specific extensions.

---

---

#### Code vs Documentation inconsistency

**Description:** input_char() blocking mode fallback on Windows without msvcrt has severe limitations not fully documented in base.py

**Affected files:**
- `src/iohandler/console.py`

**Details:**
console.py implements a fallback for Windows without msvcrt:
                    # Fallback for Windows without msvcrt: use input() with severe limitations
                    # WARNING: This fallback calls input() which:
                    # - Waits for Enter key (defeats the purpose of single-char input)
                    # - Reads the entire line but returns only the first character
                    # This is a known limitation when msvcrt is unavailable.
                    import warnings
                    warnings.warn(
                        "msvcrt not available on Windows - input_char() falling back to input() "
                        "(waits for Enter, not single character)",
                        RuntimeWarning
                    )
                    line = input()
                    return line[:1] if line else ""

base.py input_char() docstring only says:
        '''Input single character (INKEY$, INPUT$).
        Args:
            blocking: If True, wait for keypress. If False, return "" if no key ready.
        Returns:
            Single character string, or "" if non-blocking and no key available'''

The base documentation doesn't mention this severe Windows fallback limitation.

---

---

#### code_vs_comment

**Description:** Comment claims SimpleKeywordCase validates policy strings and auto-corrects invalid values, but this behavior is not verified in the provided code

**Affected files:**
- `src/lexer.py`

**Details:**
In create_keyword_case_manager() docstring:
"Note: SimpleKeywordCase validates policy strings in its __init__ method. Invalid
policy values (not in: force_lower, force_upper, force_capitalize) are automatically
corrected to force_lower. See src/simple_keyword_case.py for implementation."

However, SimpleKeywordCase implementation is not provided to verify this claim. The comment makes specific assertions about validation and auto-correction behavior that cannot be confirmed.

---

---

#### code_vs_comment

**Description:** Docstring for read_identifier() claims lexer requires spaces between keywords and identifiers, but implementation handles PRINT# without space

**Affected files:**
- `src/lexer.py`

**Details:**
read_identifier() docstring states:
"This lexer parses properly-formed MBASIC 5.21 which generally requires spaces
between keywords and identifiers. Exception: PRINT# and INPUT# where # is part
of the keyword."

The docstring says '# is part of the keyword' for PRINT# and INPUT#, but the implementation (lines ~250-265) actually treats # as NOT part of the keyword - it splits 'PRINT#' back into 'PRINT' keyword and rewinds to re-tokenize '#' separately. This contradicts the docstring's claim.

---

---

#### code_vs_comment

**Description:** Comment claims RND and INKEY$ are the only functions that can be called without parentheses in MBASIC 5.21, but this contradicts general MBASIC behavior

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line 18-19 states:
"Exception: Only RND and INKEY$ can be called without parentheses in MBASIC 5.21
  (this is specific to these two functions, not a general MBASIC feature)"

However, the code implementation at lines 1247-1260 shows:
- RND without parentheses is allowed (lines 1247-1254)
- INKEY$ without parentheses is allowed (lines 1256-1263)

This appears consistent, but the comment's claim that this is "specific to these two functions" may be misleading. In actual MBASIC implementations, other parameterless functions like TIMER, CSRLIN, etc. could also be called without parentheses. The comment should clarify whether this is a deliberate limitation or if other parameterless functions should also be supported.

---

---

#### code_vs_comment

**Description:** Comment claims semicolon between statements is not valid in MBASIC, but code allows trailing semicolons

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines 502-505 states:
"Semicolons WITHIN PRINT/LPRINT are item separators (parsed there),
but semicolons BETWEEN statements are NOT valid in MBASIC.
MBASIC uses COLON (:) to separate statements, not semicolon (;)."

However, the code at lines 500-509 explicitly allows trailing semicolons:
"# Allow trailing semicolon at end of line only (treat as no-op).
...
self.advance()
# Trailing semicolon is valid at actual end-of-line OR before a colon..."

This creates ambiguity: the comment says semicolons between statements are NOT valid, but the code allows them in specific contexts (trailing position). The comment should be updated to reflect that trailing semicolons are allowed as a special case.

---

---

#### code_vs_comment

**Description:** MID$ statement detection comment describes lookahead strategy but implementation may have edge cases

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines 826-838 describes:
"Lookahead strategy: scan past balanced parentheses, check for = sign"

The code at lines 839-862 implements this with try-catch for lookahead failures:
"except (IndexError, ParseError):
    # Catch lookahead failures during MID$ statement detection
    # IndexError: if we run past end of tokens
    # ParseError: if malformed syntax encountered during lookahead"

However, the comment at line 860 states "Position is restored below" but the actual restoration happens at line 863 ("self.position = saved_pos"). The error handling suggests that ParseError during lookahead is expected and handled, but this could mask actual syntax errors. The comment should clarify whether ParseError during lookahead is a normal case or indicates a problem.

---

---

#### code_vs_comment

**Description:** Comment describes LINE_INPUT token behavior inconsistently with actual implementation

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1150 states: 'Note: The lexer tokenizes LINE keyword as LINE_INPUT token both when standalone (LINE INPUT statement) and when used as modifier (INPUT...LINE). The parser distinguishes these cases by context - LINE INPUT is a statement, INPUT...LINE uses LINE as a modifier within the INPUT statement.'

However, the code at line ~1147 checks: 'if self.match(TokenType.LINE_INPUT):' which suggests the lexer produces LINE_INPUT token in both contexts. The comment implies the lexer doesn't distinguish between 'LINE INPUT' (statement) and 'INPUT...LINE' (modifier), but the parser code treats them the same way by checking for LINE_INPUT token type in both cases.

---

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about separator behavior in LPRINT vs PRINT statements

**Affected files:**
- `src/parser.py`

**Details:**
LPRINT parse_lprint() docstring (line ~1050) states: 'Separator count vs expression count:
- If separators < expressions: no trailing separator, add newline
- If separators >= expressions: has trailing separator, no newline added'

However, the PRINT statement parser (parse_print, not shown in this excerpt) may have different separator handling logic. The LPRINT implementation explicitly adds '\n' when len(separators) < len(expressions), but this behavior should be consistent across PRINT and LPRINT or the difference should be documented.

---

---

#### code_vs_comment

**Description:** Comment about DIM dimension expressions contradicts typical BASIC behavior

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1785 states: 'Dimension expressions: This implementation accepts any expression for array dimensions (e.g., DIM A(X*2, Y+1)), with dimensions evaluated at runtime. This behavior has been verified with MBASIC 5.21 (see tests/bas_tests/ for examples). Note: Some compiled BASICs (e.g., QuickBASIC) may require constants only.'

This comment claims the behavior 'has been verified with MBASIC 5.21' but doesn't provide specific test file references. The reference to 'tests/bas_tests/' is vague. If this is a significant deviation from other BASIC implementations, the specific test files should be named.

---

---

#### code_vs_comment

**Description:** Comment about DEFTYPE behavior describes implementation detail that may not match actual usage

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1920 states: 'Note: This method always updates def_type_map during parsing. The type map is shared across all statements (both in interactive mode where statements are parsed one at a time, and in batch mode where the entire program is parsed). The type map affects variable type inference throughout the program. The AST node is created for program serialization/documentation.'

This comment describes the def_type_map as 'shared across all statements' but doesn't clarify whether this map persists across multiple parse() calls or is reset. In interactive mode, if the parser is instantiated once and reused, the def_type_map would accumulate. If a new parser is created for each statement, the map would be lost. This ambiguity could lead to bugs.

---

---

#### code_vs_comment

**Description:** parse_width() docstring describes device parameter incorrectly

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states: "The parser accepts any expression; validation occurs at runtime."

However, the code only parses device when a COMMA is present:
```
device = None
if self.match(TokenType.COMMA):
    self.advance()
    device = self.parse_expression()
```

The docstring should clarify that device is optional and only parsed after a comma separator.

---

---

#### code_vs_comment

**Description:** parse_resume() docstring and implementation have inconsistent handling of RESUME 0

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"Note: RESUME with no argument retries the statement that caused the error.
RESUME 0 also retries the error statement (same as RESUME with no argument)."

And in AST representation:
"- RESUME (no arg) → line_number=None
- RESUME 0 → line_number=0 (interpreter handles 0 same as None)"

This creates ambiguity: the docstring says they're the same, but the AST stores different values (None vs 0). The comment "interpreter handles 0 same as None" suggests they should be equivalent, but storing different values could lead to confusion or bugs if the interpreter doesn't handle this correctly.

---

---

#### code_vs_comment

**Description:** parse_deffn() has complex function name normalization logic that may not match the docstring description

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states: "Function name normalization: All function names are normalized to lowercase with 'fn' prefix (e.g., \"FNR\" becomes \"fnr\", \"FNA$\" becomes \"fna$\") for consistent lookup."

The implementation has two branches:
1. When FN is separate token: strips type suffix, adds 'fn' prefix
2. When FN is part of identifier: expects 'fn' prefix already present from lexer, strips type suffix

The docstring example "FNA$" becomes "fna$" suggests the $ suffix is kept, but the code explicitly strips type suffixes:
```
type_suffix = self.get_type_suffix(raw_name)
if type_suffix:
    raw_name = raw_name[:-1]
```

This is inconsistent - either the suffix should be kept (as docstring suggests) or removed (as code does).

---

---

#### code_vs_comment

**Description:** PC class docstring claims stmt_offset is 0-based index but uses confusing terminology

**Affected files:**
- `src/pc.py`

**Details:**
Docstring says: 'The stmt_offset is a 0-based index into the statements list for a line.'
Then says: 'Note: Throughout the codebase, stmt_offset is consistently used as a list index (0, 1, 2, ...) not an offset in bytes. The parameter name uses "offset" for historical/semantic reasons (it offsets from the start of the line's statement list).'

This is internally consistent but the 'Note' section suggests there was confusion about whether it's an index vs offset, when the docstring already clearly states it's an index. The note is redundant and potentially confusing.

---

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about keyword case policy handling between apply_keyword_case_policy and emit_keyword

**Affected files:**
- `src/position_serializer.py`

**Details:**
apply_keyword_case_policy docstring lists policies: 'force_lower, force_upper, force_capitalize, first_wins, error, preserve'

But emit_keyword says: 'Architecture note: The parser stores keywords in uppercase (from TokenType enum names), so callers must convert to lowercase before calling this method.'

The 'preserve' policy documentation says: 'The "preserve" policy is typically handled at a higher level (keywords passed with original case preserved). If this function is called with "preserve" policy, we return the keyword as-is if already properly cased, or capitalize as a safe default.'

This is inconsistent: if keywords are stored uppercase in the parser, how can 'preserve' policy work? The original case would need to be stored separately in the AST, but there's no mention of this in the architecture notes.

---

---

#### Documentation inconsistency

**Description:** Inconsistent documentation about string length limits across different functions and presets

**Affected files:**
- `src/resource_limits.py`

**Details:**
The module docstring and create_web_limits()/create_local_limits() state that 255 bytes is for 'MBASIC 5.21 compatibility', but create_unlimited_limits() has a WARNING that says setting max_string_length to 1MB 'INTENTIONALLY BREAKS MBASIC 5.21 COMPATIBILITY' and that 'For MBASIC 5.21 spec compliance, use create_local_limits() or create_web_limits() which enforce the mandatory 255-byte string limit.'

However, the __init__ docstring for max_string_length parameter says: 'Maximum byte length for a string variable (UTF-8 encoded). MBASIC 5.21 limit is 255 bytes.' This suggests 255 is the MBASIC limit but doesn't explicitly state it's mandatory for compatibility.

The check_string_length() docstring says: 'String limits are measured in bytes (UTF-8 encoded), not character count. This matches MBASIC 5.21 behavior which limits string storage size.' This implies matching MBASIC behavior but doesn't say it's required.

The inconsistency is whether the 255-byte limit is:
1. A historical MBASIC limit that we optionally match for compatibility
2. A mandatory requirement for MBASIC 5.21 spec compliance

---

---

#### code_vs_comment

**Description:** Comment claims 'original_case' field stores original case as first typed, but code actually stores canonical case resolved by case_conflict policy

**Affected files:**
- `src/runtime.py`

**Details:**
Line 48-51 comment: "Note: The 'original_case' field stores the canonical case for display (determined by case_conflict policy).
       Despite its misleading name, this field contains the policy-resolved canonical case variant,
       not the original case as first typed. See _check_case_conflict() for resolution logic."

This comment acknowledges the field name is misleading. Multiple locations in code confirm this:
- Line 289: "# Note: Despite the field name, this stores canonical case not original (see module header)"
- Line 336: "'original_case': canonical_case  # Canonical case for display (field name is historical, see module header)"
- Line 348: "# Note: Despite the field name, this stores canonical case not original (see module header)"

The field name 'original_case' contradicts its actual purpose of storing the canonical/resolved case.

---

---

#### Code vs Documentation inconsistency

**Description:** get_variables() docstring claims to return array 'value' but implementation doesn't include it

**Affected files:**
- `src/runtime.py`

**Details:**
Docstring states each dict contains:
"- 'value': Current value (scalars only)"

But for arrays, the code returns:
- 'last_accessed_value': value of last accessed cell
- 'last_accessed_subscripts': subscripts of last accessed cell

The docstring doesn't mention 'last_accessed_value', 'last_accessed_subscripts', 'last_read_subscripts', or 'last_write_subscripts' fields that are actually returned for arrays. The example in the docstring also doesn't show these fields.

---

---

#### code_vs_comment

**Description:** SettingsManager.__init__ docstring claims paths are retrieved from backend for backward compatibility, but _get_global_settings_path() and _get_project_settings_path() helper methods have misleading comments

**Affected files:**
- `src/settings.py`

**Details:**
In SettingsManager.__init__:
        # Paths (for backward compatibility, may not be used with Redis backend)
        self.global_settings_path = getattr(backend, 'global_settings_path', None)
        self.project_settings_path = getattr(backend, 'project_settings_path', None)

But _get_global_settings_path() and _get_project_settings_path() have comments:
        """Get path to global settings file.

        Note: This method is not called internally by SettingsManager. Path resolution has been
        delegated to the backend (FileSettingsBackend or Redis backend). The __init__ method
        retrieves paths from backend.global_settings_path for backward compatibility.
        This helper method is kept for potential future use or manual path queries by external code.
        """

The comments claim these methods are "not called internally" and "kept for potential future use", but the code shows __init__ retrieves paths from backend attributes, not by calling these methods. The comments are accurate but could be clearer that these are duplicate/legacy implementations.

---

---

#### code_vs_comment

**Description:** RedisSettingsBackend.load_project() and save_project() docstrings claim different behaviors

**Affected files:**
- `src/settings_backend.py`

**Details:**
load_project() docstring:
        """Load project settings (returns empty dict in Redis mode).

        In Redis mode, all settings are session-scoped, not project-scoped.
        This method returns an empty dict rather than None for consistency.
        """

save_project() docstring:
        """Save project settings (no-op in Redis mode).

        In Redis mode, all settings are session-scoped, not project-scoped.
        This method does nothing (no write operation) for consistency.
        """

load_project() says it "returns empty dict" but save_project() says it "does nothing (no write operation)". The asymmetry is intentional but the phrasing could be clearer - load_project returns {} to indicate "no project settings available" while save_project silently ignores the request. Both are no-ops but with different return semantics.

---

---

#### code_vs_comment

**Description:** Module docstring claims both systems SHOULD read from same settings but implementation shows only KeywordCaseManager reads settings directly

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
Module docstring states:
"""Simple keyword case handling for MBASIC.

This is a simplified keyword case handler used by the lexer (src/lexer.py).
It supports only three force-based policies:
- force_lower: all lowercase (default, MBASIC 5.21 style)
- force_upper: all UPPERCASE (classic BASIC)
- force_capitalize: Capitalize first letter (modern style)

For advanced policies (first_wins, preserve, error) via CaseKeeperTable,
see KeywordCaseManager (src/keyword_case_manager.py) which is used by
src/parser.py and src/position_serializer.py.

ARCHITECTURE NOTE - Why Two Separate Case Handling Systems:

The lexer (src/lexer.py) uses SimpleKeywordCase because keywords only need
force-based policies in the tokenization phase. This lightweight handler applies
immediate transformations during tokenization without needing to track state.

The parser (src/parser.py) and serializer (src/position_serializer.py) use
KeywordCaseManager for advanced policies that require state tracking across the
entire program (first_wins, preserve, error). This separation allows:
1. Fast, stateless tokenization in the lexer
2. Complex, stateful case management in later phases
3. Settings changes between phases (though both should use consistent settings)

Note: Both systems SHOULD read from the same settings.get("keywords.case_style") setting
for consistency. SimpleKeywordCase receives policy via __init__ parameter (caller should
pass settings value), while KeywordCaseManager reads settings directly. Callers are responsible
for passing consistent policy values from settings to ensure matching behavior across phases.
"""

The comment says "Both systems SHOULD read from the same settings" and "Callers are responsible for passing consistent policy values", but SimpleKeywordCase.__init__ has no code to read from settings - it only accepts a policy parameter. The burden is entirely on the caller, which could lead to inconsistencies if callers don't properly read from settings. The comment acknowledges this but the phrasing "SHOULD read" implies both classes read settings when only KeywordCaseManager does.

---

---

#### Documentation inconsistency

**Description:** auto_save.py module is documented but not referenced in any UI backend implementation

**Affected files:**
- `src/ui/auto_save.py`
- `src/ui/curses_settings_widget.py`

**Details:**
auto_save.py provides AutoSaveManager class with comprehensive auto-save functionality including:
- Emacs-style #filename# naming
- Centralized temp directory (~/.mbasic/autosave/)
- Recovery prompts via format_recovery_prompt()
- Auto-save cleanup

However, this module is not imported or used in any of the UI backend files (cli.py, base.py, curses_settings_widget.py). The settings widget shows editor settings but no auto-save related settings are defined in the visible code.

---

---

#### Code vs Documentation inconsistency

**Description:** STEP command documentation claims statement-level stepping but implementation may not support it

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/cli_keybindings.json`

**Details:**
cli_keybindings.json states:
"description": "Execute next statement or n statements (STEP | STEP n) - attempts statement-level stepping"

cli_debug.py cmd_step() docstring states:
"Executes a single statement (not a full line). If a line contains multiple statements separated by colons, each statement is executed separately."

However, the _execute_single_step() method includes this note:
"Note: The actual statement-level granularity depends on the interpreter's implementation of tick()/execute_next(). These methods are expected to advance the program counter by one statement, handling colon-separated statements separately. If the interpreter executes full lines instead, this method will behave as line-level stepping rather than statement-level."

This suggests the feature may not actually work as documented if the interpreter doesn't support statement-level execution.

---

---

#### Code vs Documentation inconsistency

**Description:** BREAK command can set breakpoints on non-existent lines according to docstring but implementation prevents it

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/cli_keybindings.json`

**Details:**
cli_debug.py cmd_break() docstring states:
"Breakpoints can be set before or during execution, but only on existing program lines. If you try to set a breakpoint on a non-existent line, an error message will be displayed."

The implementation confirms this:
```python
if line_num in self.interactive.program.lines:
    self.breakpoints.add(line_num)
    self.interactive.io_handler.output(f"Breakpoint set at line {line_num}")
else:
    self.interactive.io_handler.output(f"Line {line_num} does not exist")
```

However, cli_keybindings.json description is ambiguous:
"description": "List breakpoints, set/clear breakpoint at line, or clear all (BREAK | BREAK line | BREAK line- | BREAK CLEAR)"

It doesn't mention the requirement that the line must exist, which could confuse users.

---

---

#### Code vs Documentation inconsistency

**Description:** Settings widget references SETTING_DEFINITIONS but the actual definitions are not visible in provided code

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
curses_settings_widget.py imports:
```python
from src.settings_definitions import SETTING_DEFINITIONS, SettingType, SettingScope
from src.settings import get, set as set_setting
```

The code uses SETTING_DEFINITIONS extensively but this file is not provided in the source code files. This makes it impossible to verify:
1. Whether auto-save settings exist
2. What the actual setting keys and types are
3. Whether the widget correctly handles all setting types
4. Whether the categories ('editor', 'keywords', 'variables') match the actual settings structure

---

---

#### code_vs_comment

**Description:** Comment describes default target_column as 7, but this assumes fixed-width line numbers which contradicts the variable-width design

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sort_and_position_line() docstring:
"target_column: Column to position cursor at (default: 7). Since line numbers have
                          variable width, this is approximate. The cursor will be positioned"

The comment says default is 7 and mentions it's approximate due to variable width, but earlier comments in the file state:
"Note: Methods like _sort_and_position_line use a default target_column of 7,
which assumes typical line numbers (status=1 char + number=5 digits + space=1 char).
This is an approximation since line numbers have variable width."

This 7-column assumption contradicts the core design principle stated in the class docstring:
"Line numbers use as many digits as needed (10, 100, 1000, 10000, etc.) rather
than fixed-width formatting. This maximizes screen space for code."

The default of 7 only works for 5-digit line numbers, but the system supports variable-width numbers.

---

---

#### code_vs_comment

**Description:** Comment about bare identifier handling doesn't match the two-stage checking implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _check_line_syntax() method:
"# Reject bare identifiers (the parser treats them as implicit REMs for
# old BASIC compatibility, but in the editor we want to be stricter).
# Note: This catches bare identifiers followed by EOF or COLON (e.g., 'foo' or 'foo:').
# Bare identifiers followed by other tokens (e.g., 'foo + bar') will be caught by the
# parser as syntax errors. A second check after parsing catches any remaining cases
# where the parser returned a RemarkStatementNode for an implicit REM."

The comment describes a two-stage process, but then the code has:
1. First check for IDENTIFIER followed by EOF/COLON
2. Second check after parsing for RemarkStatementNode

However, the comment says 'foo + bar' will be caught by parser as syntax errors, but this contradicts the claim that a second check is needed for 'any remaining cases'. If the parser catches them as errors, why is the second RemarkStatementNode check needed?

---

---

#### code_vs_comment

**Description:** Comment about FAST PATH contradicts the actual implementation of special key handling

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress() method:
"# FAST PATH: For normal printable characters, bypass editor-specific processing
# (syntax checking, column protection, etc.) for responsive typing
if len(key) == 1 and key >= ' ' and key <= '~':
    return super().keypress(size, key)

# For special keys (non-printable), we DO process them below to handle
# cursor navigation, protection of status column, etc."

But then later in the same method:
"# Prevent typing in status column (column 0)
if col_in_line == 0 and len(key) == 1 and key.isprintable():
    # Move cursor to line number column (column 1)
    new_cursor_pos = cursor_pos + 1
    self.edit_widget.set_edit_pos(new_cursor_pos)
    # Let key be processed at new position
    return super().keypress(size, key)"

This code for preventing typing in status column will NEVER execute because printable characters already returned in the FAST PATH above. The column protection is bypassed by the fast path optimization.

---

---

#### code_vs_comment

**Description:** Comment claims editor_lines stores execution state and is synced from editor, but code shows editor_lines is never actually populated from editor.lines

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~230 says:
# Note: self.editor_lines stores execution state (lines loaded from file for RUN)
# self.editor.lines (in ProgramEditorWidget) stores the actual editing state
# These serve different purposes and are synchronized as needed

However, searching the code shows:
1. editor_lines is initialized as empty dict: self.editor_lines = {}
2. It's only populated in _sync_program_to_editor() from self.program.lines
3. It's never populated FROM self.editor.lines
4. The synchronization described doesn't exist in the shown code

---

---

#### code_vs_comment

**Description:** Comment claims ImmediateExecutor is recreated in start() to ensure clean state, but Interpreter is reused - this creates potential state pollution

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~275 says:
# ImmediateExecutor Lifecycle:
# Created here with an OutputCapturingIOHandler, then recreated in start() with
# a fresh OutputCapturingIOHandler. Both instances are fully functional - the
# recreation in start() ensures a clean state for each UI session.
# Note: The interpreter (self.interpreter) is created once here and reused.
# Only the executor and its IO handler are recreated in start().

This is inconsistent because:
1. If the goal is 'clean state for each UI session', why reuse the Interpreter?
2. The Interpreter holds runtime state that could be polluted between sessions
3. Creating a new executor but reusing the interpreter doesn't achieve true clean state

---

---

#### code_vs_comment

**Description:** Comment claims _refresh_editor is called by immediate executor after adding/deleting lines, but no evidence of this connection in shown code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~180 says:
# Refresh the editor display from program manager.
#
# Called by immediate executor after adding/deleting lines via commands like '20 PRINT'.
# Syncs the editor widget's line storage with the program manager's lines.

However:
1. The immediate_executor is created but no code shows it calling _refresh_editor
2. No callback or reference to _refresh_editor is passed to immediate_executor
3. The connection described in the comment is not visible in the code

---

---

#### code_vs_comment

**Description:** Comment in _continue_smart_insert says context is lost and user must retry, but this creates poor UX

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1000 says:
# Note: Cannot continue the insert operation here because the context was lost
# when the dialog callback was invoked (lines, line_index, insert_num variables
# are no longer available). User will need to retry the insert operation manually.

This indicates a design flaw where:
1. User confirms renumber operation
2. Program renumbers successfully
3. But the original insert operation is abandoned
4. User must manually retry the insert

The comment acknowledges the problem but doesn't indicate if this is intentional or a known bug.

---

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of immediate mode status updates across different execution paths

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The code has inconsistent patterns for updating immediate mode status:

1. _debug_step() calls _update_immediate_status() on halt/error/completion
2. _debug_step_line() calls _update_immediate_status() on halt/error/completion
3. _debug_stop() calls _update_immediate_status() after stopping
4. But _debug_continue() does NOT call _update_immediate_status()
5. Exception handlers explicitly avoid calling it with comment 'Don't update immediate status on exception'

This creates unpredictable behavior where immediate mode availability depends on which code path was taken.

---

---

#### code_vs_comment

**Description:** Comment claims breakpoints are stored in editor as authoritative source and re-applied after reset, but code shows breakpoints are cleared during reset_for_run and then re-applied from editor.breakpoints

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1180 states:
"Note: reset_for_run() clears variables and resets PC. Breakpoints are STORED in
the editor (self.editor.breakpoints) as the authoritative source, not in runtime.
This allows them to persist across runs. After reset_for_run(), we re-apply them
to the interpreter below via set_breakpoint() calls so execution can check them."

This is accurate - the comment correctly describes the implementation where breakpoints persist in editor.breakpoints and are re-applied after reset. However, the phrasing could be clearer that reset_for_run() clears breakpoints from the interpreter/runtime, not from the editor.

---

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of loop.draw_screen() calls - some check loop_running, others don't

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Some methods check self.loop_running before calling draw_screen():
- _clear_all_breakpoints (line ~770): "if self.loop and self.loop_running: self.loop.draw_screen()"
- _toggle_variables_window (line ~1050): "if hasattr(self, 'loop') and self.loop and self.loop_running: self.loop.draw_screen()"
- _cycle_variables_sort_mode (line ~1120): "if hasattr(self, 'loop') and self.loop and self.loop_running: self.loop.draw_screen()"

Others don't check loop_running:
- _do_renumber (line ~650): "if self.loop and self.loop_running: self.loop.draw_screen()"
- _toggle_breakpoint_current_line (line ~730): "if self.loop and self.loop_running: self.loop.draw_screen()"

Actually, all the examples DO check loop_running. The inconsistency is in whether hasattr(self, 'loop') is checked first.

---

---

#### code_vs_comment

**Description:** Comment in _setup_program about PC override timing may be misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1195 states:
"If start_line is specified (e.g., RUN 100), set PC to that line
This must happen AFTER interpreter.start() because start() calls setup()
which resets PC to the first line in the program. By setting PC here,
we override that default and begin execution at the requested line."

This accurately describes the implementation, but the comment doesn't mention that this only works because the PC is set before any tick() calls. If tick() were called before setting PC, execution would start at the wrong line.

---

---

#### code_vs_comment

**Description:** Comment claims ESC during INPUT sets runtime.stopped=True and self.running=False, but code only sets self.running=False

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1047 says:
# Note: This sets runtime.stopped=True (like STOP) and self.running=False (stops UI tick).

But actual code at line ~1055 only does:
self.runtime.stopped = True
self.running = False

However, the comment describes the behavior correctly - both flags ARE set. This appears to be consistent.

---

---

#### code_vs_comment

**Description:** Comment in cmd_delete and cmd_renum says 'Updates self.program immediately (source of truth), then syncs to runtime' but the functions call helpers that may update runtime directly

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1710 (cmd_delete) and line ~1728 (cmd_renum) both say:
Note: Updates self.program immediately (source of truth), then syncs to runtime.

Both functions call:
self._sync_program_to_runtime()  # Sync runtime after program changes

But the helper functions (delete_lines_from_program, renum_program) are passed runtime=None, suggesting they don't update runtime. The comment appears accurate - helpers update self.program, then _sync_program_to_runtime syncs to runtime.

---

---

#### code_vs_comment

**Description:** Comment in _sync_program_to_runtime says it 'allows LIST and other commands to see the current program without accidentally triggering execution' but LIST doesn't call this function

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Docstring at line ~1145 says:
This allows LIST and other commands to see the current program without
accidentally triggering execution.

But cmd_list (line ~1698) just calls:
self._list_program()

Which uses self.editor_lines directly, not runtime's statement_table. The comment may be outdated or referring to immediate mode LIST command which goes through immediate_executor.

---

---

#### code_vs_comment_conflict

**Description:** Comment claims tier labels use 'language' and 'mbasic' from tier_labels dict, but code shows tier_labels only has these two entries and uses startswith('ui/') check separately

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~143 states:
"Note: Tier labels are determined from tier_labels dict ('language', 'mbasic'), startswith('ui/') check for UI tiers ('ui/curses', 'ui/tk'), or '📙 Other' fallback."

Code at lines ~145-148 shows:
tier_labels = {
    'language': '📕 Language',
    'mbasic': '📗 MBASIC',
}

Then at lines ~162-167:
tier_name = file_info.get('tier', '')
if tier_name.startswith('ui/'):
    tier_label = '📘 UI'
else:
    tier_label = tier_labels.get(tier_name, '📙 Other')

The comment accurately describes the logic, but the phrasing could be clearer that tier_labels is a local dict defined in the method, not a class attribute or external configuration.

---

---

#### documentation_inconsistency

**Description:** Both files have nearly identical comments about loading keybindings but for different purposes, creating potential confusion about their relationship

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/keybinding_loader.py`

**Details:**
help_macros.py line ~28 comment:
"Note: This loads the same keybinding JSON files as keybinding_loader.py, but for a different purpose: macro expansion in help content (e.g., {{kbd:run}} -> "^R") rather than runtime event handling. This is separate from help_widget.py which uses hardcoded keys for navigation within the help system itself."

keybinding_loader.py line ~28 comment:
"Note: This loads keybindings for runtime event handling (binding keys to actions). help_macros.py loads the same JSON files but for macro expansion in help content (e.g., {{kbd:run}} -> "^R"). Both read the same data but use it differently: KeybindingLoader for runtime key event handling, HelpMacros for documentation display."

These comments reference each other but could lead to circular confusion. The relationship is clear but the cross-referencing style is unusual.

---

---

#### code_vs_comment_conflict

**Description:** Comment claims help_widget.py uses hardcoded keys but doesn't mention that HelpMacros loads keybindings for macro expansion, creating confusion about what 'hardcoded' means

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Multiple comments in help_widget.py emphasize that navigation keys are hardcoded:

Line ~73: "Note: Help navigation keys are HARDCODED (not loaded from keybindings JSON)"

Line ~76: "Note: HelpMacros (instantiated below) DOES load keybindings from JSON, but only for macro expansion in help content ({{kbd:action}} substitution). The help widget's own navigation doesn't consult those loaded keybindings - it uses hardcoded keys."

Line ~79: "MAINTENANCE: If help navigation keys change, update:
1. All footer text assignments (search for 'self.footer' in this file - multiple locations)"

However, this creates confusion because:
1. HelpMacros IS instantiated and DOES load keybindings
2. The term 'hardcoded' is used to mean 'not dynamically loaded for navigation' but the keybindings ARE loaded (just for different purpose)
3. The maintenance note suggests manual updates to footer text, but doesn't clarify the relationship with the loaded keybindings

The comments are technically accurate but the repeated emphasis on 'hardcoded' vs 'loaded' creates unnecessary confusion about the architecture.

---

---

#### code_vs_comment_conflict

**Description:** Comment references keybindings module functions but code uses hardcoded keybinding references

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Comment at line ~23 states:
"# Use keybindings module to get actual shortcuts"

Code at lines ~24-44 shows menu definitions like:
(f'New            {key_to_display(kb.NEW_KEY)}', '_new_program'),
(f'Open...        {key_to_display(kb.OPEN_KEY)}', '_load_program'),

This imports from keybindings module (line ~4: from . import keybindings as kb) and uses constants like kb.NEW_KEY, kb.OPEN_KEY, etc.

However, this is inconsistent with the keybinding_loader.py approach which loads from JSON. The interactive_menu.py uses the old keybindings.py module with hardcoded constants, not the JSON-based keybinding_loader.py system.

This suggests there are two keybinding systems in use: the old keybindings.py with constants, and the new keybinding_loader.py with JSON configs.

---

---

#### Code vs Comment conflict

**Description:** Comment says QUIT_KEY has no dedicated keybinding and suggests using menu or Ctrl+C, but QUIT_ALT_KEY is defined and loaded from JSON config

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 127-133:
# Quit - No dedicated keybinding in QUIT_KEY (most Ctrl keys intercepted by terminal or already assigned)
# Primary method: Use menu (Ctrl+U -> File -> Quit)
# Alternative method: Ctrl+C (interrupt signal) - handled by QUIT_ALT_KEY below
QUIT_KEY = None  # No standard keybinding (use menu or Ctrl+C instead)

# Alternative quit via interrupt signal (Ctrl+C)
# Note: While not a "standard keybinding", Ctrl+C provides a keyboard shortcut to quit.
# It's handled as a signal rather than a regular key event, hence the separate constant.
_quit_alt_from_json = _get_key('editor', 'quit')
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

The comment implies Ctrl+C is a signal handler, but the code loads it from JSON as a regular keybinding.

---

---

#### Documentation inconsistency

**Description:** KEYBINDINGS_BY_CATEGORY comment lists keys not included in help, but doesn't mention QUIT_KEY (which is None) or explain why QUIT_ALT_KEY is shown instead

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 217-226:
# All keybindings organized by category for help display
# Note: This dictionary contains keybindings shown in the help system.
# Some defined constants are not included here:
# - CLEAR_BREAKPOINTS_KEY (Shift+Ctrl+B) - Available in menu under Edit > Clear All Breakpoints
# - STOP_KEY (Ctrl+X) - Shown in debugger context in the Debugger category
# - MAXIMIZE_OUTPUT_KEY (Shift+Ctrl+M) - Menu-only feature, not documented as keyboard shortcut
# - STACK_KEY (empty string) - No keyboard shortcut assigned, menu-only
# - Dialog-specific keys (DIALOG_YES_KEY, DIALOG_NO_KEY, SETTINGS_APPLY_KEY, SETTINGS_RESET_KEY) - Shown in dialog prompts
# - Context-specific keys (VARS_SORT_MODE_KEY, VARS_SORT_DIR_KEY, etc.) - Shown in Variables Window category

Comment doesn't explain that QUIT_KEY is None and QUIT_ALT_KEY is used instead. Also, STOP_KEY comment says it's shown in debugger context, but looking at line 245, STOP_KEY IS included in the Debugger category.

---

---

#### Code vs Documentation inconsistency

**Description:** In-page search keybindings documented in code comments but missing from tk_keybindings.json

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
tk_help_browser.py lines 113-116 document Return and Escape keys for in-page search:
# Return key in search box navigates to next match (local widget binding)
# Note: This binding is specific to the in-page search entry widget and is not
# documented in tk_keybindings.json, which only documents global application
# keybindings. Local widget bindings are documented in code comments only.
# ESC key closes search bar (local widget binding, not in tk_keybindings.json)

However, tk_keybindings.json only documents Ctrl+F for inpage_search, missing Return (next match) and Escape (close search bar) bindings. The comment explicitly states these are not in tk_keybindings.json, but this creates incomplete documentation of available keybindings.

---

---

#### Code duplication with inconsistency risk

**Description:** Path normalization logic duplicated between _follow_link() and _open_link_in_new_window() methods

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In _follow_link() (line 244):
# Note: Path normalization logic is duplicated in _open_link_in_new_window().
# Both methods use similar approach: resolve relative paths, normalize to help_root,
# handle path separators. If modification needed, update both methods consistently.

In _open_link_in_new_window() (line 638):
# Note: Path normalization logic is duplicated from _follow_link().
# Both methods resolve paths relative to help_root with similar logic.
# If modification needed, update both methods consistently.

Both methods implement similar path resolution logic (lines 247-272 and 645-665). This duplication creates maintenance risk where changes to one method may not be reflected in the other, leading to inconsistent behavior.

---

---

#### code_vs_comment

**Description:** Comment states immediate_history and immediate_status are 'always None' but code explicitly sets them to None with defensive programming justification

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~265 comment: 'Note: immediate_history and immediate_status are always None in Tk UI'
Line ~267 comment: '(Tk uses immediate_entry Entry widget directly instead of separate history/status widgets)'
Line ~273-276 code:
# Set immediate_history and immediate_status to None
# These attributes are not currently used but are set to None for defensive programming
# in case future code tries to access them (will get None instead of AttributeError)
self.immediate_history = None
self.immediate_status = None

---

---

#### code_vs_comment

**Description:** _ImmediateModeToken docstring references line 1194 for _on_variable_edit() but this is a forward reference that may be incorrect

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~18-23 docstring:
'''Token for variable edits from immediate mode or variable editor.

This class is instantiated when editing variables via the variable inspector
(see _on_variable_edit() around line 1194). Used to mark variable changes that
originate from the variable inspector or immediate mode, not from program
execution. The line=-1 signals to runtime.set_variable() that this is a
debugger/immediate mode edit.'''

The file is truncated at line ~1194 with _edit_simple_variable method, but _on_variable_edit() is not visible in the provided code. The line number reference may be outdated or incorrect.

---

---

#### code_vs_comment

**Description:** Variables window heading text shows 'Last Accessed' but comment says it matches 'accessed' column with descending sort

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines ~1063-1065:
# Set initial heading text with down arrow (matches self.variables_sort_column='accessed', descending)
tree.heading('#0', text='↓ Variable (Last Accessed)')

The comment correctly describes the initial state (sort_column='accessed', reverse=True from lines ~113-114), but the heading text 'Last Accessed' may not match the actual column name used in sorting logic. Need to verify if 'accessed' is the correct column identifier.

---

---

#### code_vs_comment

**Description:** Comment claims formatting may occur elsewhere, but code explicitly avoids formatting to preserve MBASIC compatibility

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _refresh_editor method around line 1150:
Comment says: '# (Note: "formatting may occur elsewhere" refers to the Variables and Stack windows,\n# which DO format data for display - not the editor/program text itself)'

This comment is confusing because it suggests formatting happens elsewhere, but the actual intent is to clarify that NO formatting happens to program text (only to Variables/Stack display data). The parenthetical note tries to clarify this but creates ambiguity about whether 'elsewhere' means 'in other parts of the code' or 'in other windows'.

---

---

#### code_vs_comment

**Description:** Comment about array_base validation contradicts defensive else clause

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _edit_array_element method around line 680:
Comment says: '# OPTION BASE only allows 0 or 1 (validated by OPTION statement parser).\n# The else clause is defensive programming for unexpected values.'

Then the code has:
if array_base == 0:
    default_subscripts = ','.join(['0'] * len(dimensions))
elif array_base == 1:
    default_subscripts = ','.join(['1'] * len(dimensions))
else:
    # Defensive fallback for invalid array_base (should not occur)
    default_subscripts = ','.join(['0'] * len(dimensions))

The comment claims OPTION BASE validation ensures only 0 or 1, making the else clause unreachable. However, if validation is truly complete, the else clause is dead code. If the else clause is needed for defensive programming, then validation might not be complete. This creates logical inconsistency about whether the else clause can ever execute.

---

---

#### internal_inconsistency

**Description:** Inconsistent handling of syntax validation output messages

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1250:
The code has logic: 'should_show_list = len(errors_found) > 1'
with comment: '# Only show full error list in output if there are multiple errors.\n# For single errors, the red ? icon in the editor is sufficient feedback.'

However, the status bar is ALWAYS updated with error count (lines 1260-1265), even for single errors. This creates inconsistency: single errors don't get output window messages (to avoid clutter) but DO get status bar messages. The comment explains the output window behavior but doesn't mention the status bar always shows errors.

---

---

#### code_vs_comment

**Description:** Comment claims _on_key_press clears highlight on ANY key, but code only clears on printable characters

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1050 states: "Clears on ANY key (even arrows/function keys)"

But code at line ~1060 returns None for non-printable keys BEFORE clearing highlight:

```
if len(event.char) != 1:
    return None
```

The highlight clearing happens at the top of the function, so it DOES clear on any key. However, the comment's justification about "editing shifts character positions" only applies to actual text modifications, not arrow keys.

---

---

#### code_vs_comment

**Description:** Comment about paste handling describes three cases but implementation has different logic flow

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1140 states: "The auto-numbering path handles:
1. Multi-line paste: sanitized_text contains \n → multiple lines to process
2. Single-line paste into blank line: current_line_text empty → one line to process"

However, the code checks for '\n' in sanitized_text first (line ~1125), then checks if current line has content. The logic is:
- If no newlines AND current line has content → inline paste
- Otherwise → auto-numbering path

This means single-line paste into non-blank line uses inline paste, not auto-numbering. The comment's case 2 is correct but incomplete.

---

---

#### code_vs_comment

**Description:** Comment about _smart_insert_line saving behavior contradicts when line is actually saved

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1330 states: "DON'T save to program yet - the line only has a line number with no statement, so _save_editor_to_program() will skip it (only saves lines with statements)."

This implies _save_editor_to_program() filters out lines with only line numbers. However, earlier in the file (around line ~900), _save_editor_to_program() is called after various edits, and there's no clear indication it filters blank numbered lines. The comment claims the line "won't be removed by _remove_blank_lines() because it contains the line number" but will be saved later when content is added. This needs verification of _save_editor_to_program()'s actual filtering behavior.

---

---

#### code_vs_comment

**Description:** Comment about CONT command validation incomplete compared to actual requirements

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1730 states: "Validation: Requires runtime exists and runtime.stopped is True."

However, the comment then describes that CONT works after STOP, Ctrl+C/Break, and END statements. The validation should also check that the program state allows continuation (PC is valid, statement table exists, etc.). The comment only mentions runtime.stopped but doesn't mention other state requirements.

---

---

#### code_vs_comment

**Description:** Comment claims GUI doesn't echo immediate mode commands, but this contradicts typical BASIC behavior documentation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method around line 1150:
Comment states: "Execute without echoing (GUI design choice that deviates from typical BASIC behavior: command is visible in entry field, and 'Ok' prompt is unnecessary in GUI context - only results are shown. Traditional BASIC echoes to output.)"

This comment acknowledges a deviation from documented BASIC behavior but doesn't clarify if this is intentional or a limitation.

---

---

#### code_vs_comment

**Description:** Dead code documented but method setup is never called

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method _setup_immediate_context_menu() at line 1290 has docstring:
"DEAD CODE: This method is never called because immediate_history is always None in the Tk UI (see __init__). Retained for potential future use if immediate mode gets its own output widget. Related dead code: _copy_immediate_selection() and _select_all_immediate()."

The methods _copy_immediate_selection() (line 1360) and _select_all_immediate() (line 1368) are also documented as related dead code. These methods exist but are never invoked, creating maintenance burden.

---

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about INPUT handling strategy

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler class docstring states:
"Input strategy rationale:
- INPUT statement: Uses inline input field when backend available (allowing the user to see program output context while typing input), otherwise uses modal dialog as fallback. This is availability-based, not a UI preference.
- LINE INPUT statement: Always uses modal dialog for consistent UX."

However, the input() method implementation (line 1440) shows fallback logic, while input_line() method (line 1475) always uses modal dialog. The distinction between 'availability-based' vs 'intentional UX choice' could be clearer about when each approach is used.

---

---

#### code_vs_comment

**Description:** Comment describes complex state management that may be fragile

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _update_immediate_status() method around line 1090:
"Check if safe to execute - use both can_execute_immediate() AND self.running flag. The 'not self.running' check prevents immediate mode execution when a program is running, even if the tick hasn't completed yet. This prevents race conditions where immediate mode could execute while the program is still running but between tick cycles."

This describes a race condition mitigation using multiple flags (can_execute_immediate() and self.running). The complexity suggests potential for state inconsistencies if these flags get out of sync.

---

---

#### code_vs_comment

**Description:** Comment indicates PC position handling differs from typical flow

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_continue() method around line 1050:
"The interpreter maintains the execution position in PC (moved by STOP). When CONT is executed, tick() will continue from runtime.pc, which was set by execute_stop() to point to the next statement after STOP. No additional position restoration is needed here."

This comment references execute_stop() behavior in another file, creating a dependency that could break if execute_stop() changes its PC handling without updating this code.

---

---

#### code_vs_comment_conflict

**Description:** The _delete_line() docstring describes line_num as 'Tkinter text widget line number (1-based sequential index), not BASIC line number' and mentions 'dual numbering', but the class docstring says 'BASIC line numbers are part of the text content (not drawn separately in the canvas)' without clearly explaining this dual numbering system upfront.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_delete_line() docstring: 'Args:
    line_num: Tkinter text widget line number (1-based sequential index),
             not BASIC line number (e.g., 10, 20, 30).
             Note: This class uses dual numbering - editor line numbers for
             text widget operations, BASIC line numbers for line_metadata lookups.'

Class docstring mentions: 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas).'

The class docstring should explain the dual numbering system more clearly upfront since it's a critical concept for understanding the widget's operation.

---

---

#### code_vs_comment_conflict

**Description:** The _on_cursor_move() method has a detailed comment explaining why after_idle() is used for deletion, but the comment in _delete_line() doesn't mention that it's always called via after_idle(), which is important context for understanding why the try/except for TclError is necessary.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_on_cursor_move() comment: '# Schedule deletion after current event processing to avoid interfering with ongoing key/mouse event handling (prevents cursor position issues, undo stack corruption, and widget state conflicts during event processing)'

_delete_line() has try/except: 'except tk.TclError:
    # Line no longer exists, ignore
    pass'

The _delete_line() method should mention in its docstring that it's called via after_idle() and that's why the line might not exist anymore (user could have edited between scheduling and execution).

---

---

#### code_vs_comment

**Description:** Comment in serialize_line() describes fallback behavior that doesn't match actual implementation logic

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Note: If source_text doesn't match pattern (or is unavailable), falls back to relative_indent=1.
When does this occur?
1. Programmatically inserted lines (no source_text attribute)
2. Lines where source_text doesn't start with line_number + spaces (edge case)"

However, the code only sets relative_indent=1 as initial default before checking source_text. If source_text exists but doesn't match the pattern, relative_indent remains 1 (the default), but this is not because of an explicit fallback - it's because the if match: block never executes. The comment implies a deliberate fallback mechanism, but the code just uses the initial default value.

---

---

#### Code vs Comment conflict

**Description:** Comment in cmd_run() claims 'Runtime accesses program.line_asts directly, no need for program_ast variable' but the code actually passes program.line_asts to Runtime constructor

**Affected files:**
- `src/ui/visual.py`

**Details:**
Comment says: '(Runtime accesses program.line_asts directly, no need for program_ast variable)'
Code shows: 'self.runtime = Runtime(self.program.line_asts, self.program.lines)'

The comment suggests Runtime accesses line_asts directly (implying it might have a reference to the program object), but the code explicitly passes line_asts as a constructor argument, which is a different pattern.

---

---

#### Code vs Documentation inconsistency

**Description:** get_cursor_position() docstring claims it returns placeholder values but doesn't document this limitation in the main class docstring features list

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Method docstring says:
        """Get current cursor position.

        Note: This is a placeholder implementation that always returns line 0, column 0.
        Full implementation would require async JavaScript communication support.

        Returns:
            Dict with 'line' and 'column' keys (placeholder: always {'line': 0, 'column': 0})
        """

But the class docstring lists features without mentioning this limitation:
    """CodeMirror 5 based code editor component.

    This component uses CodeMirror 5 (legacy version) which doesn't require
    ES6 module loading, making it compatible with NiceGUI's module system.

    Features:
    - Find highlighting (yellow background)
    - Breakpoint markers (red line background)
    - Current statement highlighting (green background)
    - Line numbers
    - Text editing
    """

The features list doesn't mention cursor position retrieval at all, and the method is non-functional.

---

---

#### code_vs_comment

**Description:** Comment claims input echoing happens naturally via editable textarea, but code shows input field is separate from output textarea

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~70 says:
# Note: Input echoing (displaying what user typed) happens naturally because
# the user types directly into the output textarea, which is made editable
# by _enable_inline_input() in the NiceGUIBackend class.

However, the UI structure shows separate elements:
- self.input_row (line ~1009)
- self.input_label (line ~1010)
- self.input_field (line ~1011)
- self.input_submit_btn (line ~1012)

These are separate UI elements for inline input, not making the output textarea editable.

---

---

#### code_vs_comment

**Description:** Docstring claims columns are not sortable, but code shows sortable: False explicitly set

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~213:
# Create table - columns not sortable (we handle sorting via buttons above)

Then at line ~216-219:
columns = [
    {'name': 'name', 'label': name_header, 'field': 'name', 'align': 'left', 'sortable': False},
    {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left', 'sortable': False},
    {'name': 'value', 'label': 'Value', 'field': 'value', 'align': 'left', 'sortable': False},
]

This is actually consistent - the comment explains WHY sortable is False. Not an inconsistency.

---

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

---

#### code_vs_comment

**Description:** Comment about INPUT handling references line 1932, but the actual _execute_tick method appears to be at a different location in the provided excerpt.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1730 states:
"# INPUT handling: When INPUT statement executes, the immediate_entry input box
# is focused for user input (see _execute_tick() at line 1932)."

The _execute_tick method in the provided code is around line 1880-1990, not line 1932. This line number reference may be outdated from code refactoring.

---

---

#### code_vs_comment

**Description:** Comment in _menu_run claims RUN does NOT clear output, but the comment references 'line ~1845 below' which is confusing given the actual line numbers in the code.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment in _menu_run (around line 1820) states:
"Note: This implementation does NOT clear output (see comment at line ~1845 below)."

The line reference '~1845 below' is vague and may be outdated. The actual comment about not clearing output appears to be at a different location.

---

---

#### code_vs_comment

**Description:** Comment in _handle_step_result claims to use 'microprocessor model' but the actual implementation checks multiple state properties in a specific order that may not align with a pure microprocessor model.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~2150 states:
"# Use microprocessor model: check error_info, input_prompt, and runtime.halted"

However, the implementation checks state.input_prompt first, then state.error_info, then runtime.halted, and finally has an else clause for 'still running'. This is more of a state machine pattern than a microprocessor model. The term 'microprocessor model' may be misleading or outdated terminology.

---

---

#### code_vs_comment

**Description:** Comment claims PC preservation logic prevents accidental execution starts, but code actually handles state preservation during statement table rebuilds

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _sync_program_to_runtime() method:

Comment says: "# This logic is about PRESERVING vs RESETTING state, not about preventing accidental starts"

But earlier comment says: "# Otherwise (no active execution): Resets PC to halted state, preventing
# unexpected execution when LIST/edit commands modify the program."

The word 'preventing' in the second comment contradicts the clarification that this is 'not about preventing accidental starts'. The logic resets PC when timer is inactive to maintain halted state after program modifications, which does prevent unexpected execution.

---

---

#### code_vs_comment

**Description:** Comment describes dual input mechanism but doesn't explain why both are needed or when each is used

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _handle_output_enter() method:

Comment says: "# Provide input to interpreter via TWO mechanisms (we check both in case either is active):
# 1. interpreter.provide_input() - Used when interpreter is waiting synchronously
#    (checked via interpreter.state.input_prompt). Stores input for retrieval.
# 2. input_future.set_result() - Used when async code is waiting via asyncio.Future
#    (see _get_input_async method). Only one path will be active at a time, but we
#    check both to handle whichever path the interpreter is currently using."

The comment says 'Only one path will be active at a time' but then says 'we check both in case either is active'. This is confusing - if only one is active, why check both? The comment should clarify that we don't know which path is active, so we try both.

---

---

#### code_vs_comment

**Description:** Comment claims 'errors are caught and logged, won't crash the UI' but the timer callback save_state_periodic() catches exceptions internally, so the comment is accurate for the timer but potentially misleading about general error handling

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~470: '# Save state periodically (errors are caught and logged, won't crash the UI)'
Code shows save_state_periodic() does catch exceptions:
    def save_state_periodic():
        try:
            app.storage.client['session_state'] = backend.serialize_state()
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to save session state: {e}\n")
            sys.stderr.flush()

The comment is accurate but could be clearer that it refers specifically to the timer callback's error handling.

---

---

#### code_vs_comment

**Description:** Comment says 'Save state on disconnect' but the callback save_on_disconnect() is registered with on_disconnect which may not fire reliably in all disconnect scenarios (browser crash, network loss, etc.)

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~474:
        # Save state on disconnect
        def save_on_disconnect():
            try:
                app.storage.client['session_state'] = backend.serialize_state()
            except Exception as e:
                sys.stderr.write(f"Warning: Failed to save final session state: {e}\n")
                sys.stderr.flush()

        ui.context.client.on_disconnect(save_on_disconnect)

The comment doesn't mention that this is best-effort and may not fire in all disconnect scenarios. The periodic save (every 5 seconds) provides backup, but the comment could be clearer about reliability.

---

---

#### documentation_inconsistency

**Description:** Help URL inconsistency - documentation mentions legacy localhost:8000 but code uses /mbasic_docs path

**Affected files:**
- `docs/help/README.md`
- `src/ui/web_help_launcher.py`

**Details:**
README.md states: '(Legacy code may reference `http://localhost:8000`, which is deprecated in favor of the `/mbasic_docs` path.)'

But web_help_launcher.py HELP_BASE_URL = 'http://localhost/mbasic_docs' and the WebHelpLauncher_DEPRECATED class uses self.server_port = 8000 with localhost:8000 URLs.

The deprecated class comment says 'NEW: In NiceGUI backend, use: ui.navigate.to('/mbasic_docs/statements/print/', new_tab=True)' but this path format is inconsistent with HELP_BASE_URL which includes the full http://localhost prefix.

---

---

#### code_documentation_mismatch

**Description:** Keybinding JSON structure doesn't match documentation placeholder format

**Affected files:**
- `src/ui/web_keybindings.json`
- `docs/help/common/debugging.md`

**Details:**
JSON has structure like:
{
  'editor': {
    'step': { 'keys': ['F10'], 'primary': 'F10', 'description': 'Step to next line' },
    'continue': { 'keys': ['F5'], 'primary': 'F5', 'description': 'Continue execution' }
  }
}

But debugging.md uses placeholders like {{kbd:step:curses}} and {{kbd:continue:curses}} which suggest a different structure (action:ui_type) rather than the JSON's (category.action) structure.

Also, JSON only has 'editor' category, no UI-specific variants (no 'curses', 'tk', 'web' distinctions in the JSON).

---

---

#### documentation_inconsistency

**Description:** Documentation claims 27 optimizations but Type Rebinding Analysis description suggests it's not fully implemented

**Affected files:**
- `docs/help/common/compiler/optimizations.md`

**Details:**
optimizations.md states at the top: '27 optimizations analyzed in the semantic analysis phase.'

But the 'Code Generation' section at the bottom says:
'Status: In Progress

Additional optimizations will be added during code generation:'

This suggests some optimizations are only 'analyzed' (detected) but not yet 'applied' (implemented in code generation). The documentation should clarify which of the 27 are fully implemented vs. only detected.

---

---

#### documentation_inconsistency

**Description:** Inconsistent cross-references between getting-started.md and language.md

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/language.md`

**Details:**
getting-started.md says 'For detailed reference documentation, see [BASIC Language Reference](language.md)' but language.md says 'For a beginner-friendly tutorial, see [Getting Started](getting-started.md)'. However, getting-started.md also links to [BASIC Language Reference](language/statements/index.md) in the 'Next Steps' section, creating confusion about whether language.md or language/statements/index.md is the main reference.

---

---

#### documentation_inconsistency

**Description:** Inconsistent precision information for SINGLE type

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/atn.md`

**Details:**
data-types.md states SINGLE has '~7 significant digits' of precision, while atn.md states 'the evaluation of ATN is always performed in single precision (~7 significant digits)'. The tilde (~) suggests approximation, but the exact precision should be consistent. Additionally, data-types.md says 'approximately 16 digits' for DOUBLE but uses 'about 16 decimal digits' elsewhere in the same document.

---

---

#### documentation_inconsistency

**Description:** Inconsistent error code reference format

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
data-types.md references 'Error 6 - OV' and links to error-codes.md, but error-codes.md lists the error as 'Code: OV, Number: 6'. The format and order differ between the reference and the actual error codes document.

---

---

#### documentation_inconsistency

**Description:** Incomplete cross-reference between character set and ASCII codes

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
character-set.md has a 'See Also' section linking to ascii-codes.md, but ascii-codes.md does not link back to character-set.md in its 'See Also' section. The relationship should be bidirectional for better navigation.

---

---

#### documentation_inconsistency

**Description:** Inconsistent precision information for PI calculation

**Affected files:**
- `docs/help/common/language/appendices/math-functions.md`
- `docs/help/common/language/functions/atn.md`

**Details:**
math-functions.md states 'Note: ATN(1) * 4 gives single precision (~7 digits)' and 'For double precision, use ATN(CDBL(1)) * 4', while atn.md states '**Note:** When computing PI with `ATN(1) * 4`, the result is limited to single precision (~7 digits). For higher precision, use `ATN(CDBL(1)) * 4` to get double precision.' The information is consistent but the note in atn.md is more detailed and should be the canonical reference.

---

---

#### documentation_inconsistency

**Description:** Inconsistent error number formatting in error codes table

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
The error codes table uses different formatting for reserved errors:
- Errors 24-25: '*24-25* | *(Reserved)*'
- Errors 27-28: '*27-28* | *(Reserved)*'
- Errors 31-49: '*31-49* | *(Reserved)*'
- Error 56: '*56* | *(Reserved)*'
- Errors 59-60: '*59-60* | *(Reserved)*'
- Error 65: '*65* | *(Reserved)*'

Single reserved errors use single asterisks while ranges use asterisks around the range. This formatting inconsistency makes the table harder to parse.

---

---

#### documentation_inconsistency

**Description:** LOF function is documented in detail but missing from the index categorization

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
The index.md file lists LOF under 'File I/O Functions' in the alphabetical quick reference, but LOF is not listed in the 'By Category' section under 'File I/O Functions'. The category section lists: EOF, INPUT$, LOC, LOF (missing), LPOS, but LOF has a complete documentation file at lof.md.

---

---

#### documentation_inconsistency

**Description:** Inconsistent Control-C behavior documentation

**Affected files:**
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/input_dollar.md`

**Details:**
Both INKEY$ and INPUT$ document Control-C behavior with identical notes: 'Note: Control-C behavior varied in original implementations. In MBASIC 5.21 interpreter mode, Control-C would terminate the program. This implementation passes Control-C through (CHR$(3)) for program detection and handling, allowing programs to detect and handle it explicitly.' However, this note appears to be implementation-specific and may not belong in both places, or should be consistently applied to all input functions.

---

---

#### documentation_inconsistency

**Description:** LPOS 'See Also' section references functions not in its category

**Affected files:**
- `docs/help/common/language/functions/lpos.md`

**Details:**
LPOS is categorized as a 'file-io' function but its 'See Also' section references POS, LPRINT, LPRINT USING, WIDTH LPRINT, PRINT, and PRINT# - mixing console, printer, and file I/O functions. The original documentation had a different 'See Also' list that was replaced with implementation-specific alternatives.

---

---

#### documentation_inconsistency

**Description:** CLEAR documentation has conflicting information about parameter meanings between MBASIC 5.21 and earlier versions

**Affected files:**
- `docs/help/common/language/statements/clear.md`

**Details:**
The documentation states:
"In MBASIC 5.21 (BASIC-80 release 5.0 and later):
- expression1: If specified, sets the highest memory location available for BASIC to use
- expression2: Sets the stack space reserved for BASIC"

But then notes:
"Historical note: In earlier versions of BASIC-80 (before release 5.0), the parameters had different meanings:
- expression1 set the amount of string space
- expression2 set the end of memory"

This is confusing because the documentation is for MBASIC 5.21 but includes historical information that contradicts the current behavior. The syntax section shows 'CLEAR [,[<expression1>] [,<expression2>]]' but doesn't clearly indicate which version's semantics apply.

---

---

#### documentation_inconsistency

**Description:** Index page claims 45 intrinsic functions and 77 statements but doesn't provide verification

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/operators.md`

**Details:**
The index.md states:
'- [Functions](functions/index.md) - 45 intrinsic functions
- [Statements](statements/index.md) - 77 commands and statements'

These specific counts should be verifiable by counting the actual documented functions and statements, but no such verification is provided. If these numbers are from the original manual, they may not match the current implementation.

---

---

#### documentation_inconsistency

**Description:** DEF FN documentation claims multi-character function names are an extension over MBASIC 5.21, but DEFINT/SNG/DBL/STR documentation doesn't mention this is also an extension

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
def-fn.md states:
"**Original MBASIC 5.21**: Function names were limited to a single character after FN:
- ✓ `FNA` - single character
- ✓ `FNB$` - single character with type suffix

**This implementation (extension)**: Function names can be multiple characters"

However, defint-sng-dbl-str.md doesn't clarify whether the DEF<type> statements themselves have any extensions or differences from original MBASIC 5.21. The documentation should be consistent about noting extensions.

---

---

#### documentation_inconsistency

**Description:** END documentation states files remain closed after CONT, but this behavior is not mentioned in STOP documentation

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/stop.md`

**Details:**
end.md states:
"Both END and STOP allow continuation with CONT. The key difference is that END closes all files before returning to command level, and these files remain closed even if execution is continued with CONT."

This important detail about file state after CONT is only in END.md. The STOP.md file should also mention that files remain open after STOP+CONT for consistency.

---

---

#### documentation_inconsistency

**Description:** FIELD documentation warns against using FIELDed variables in INPUT/LET, but GET documentation doesn't mention this critical restriction

**Affected files:**
- `docs/help/common/language/statements/field.md`
- `docs/help/common/language/statements/get.md`

**Details:**
field.md contains important warning:
"**Note:** Do not use a FIELDed variable name in an INPUT or LET statement. Once a variable name is FIELDed, it points to the correct place in the random file buffer. If a subsequent INPUT or LET statement with that variable name is executed, the variable's pointer is moved to string space."

get.md shows example using FIELDed variables but doesn't repeat this warning. Users reading GET documentation might not see the FIELD warning.

---

---

#### documentation_inconsistency

**Description:** INPUT and INPUT# have different descriptions of how strings are parsed, particularly regarding quotes

**Affected files:**
- `docs/help/common/language/statements/input.md`
- `docs/help/common/language/statements/input_hash.md`

**Details:**
input.md states:
"String values may be entered with or without quotes (quotes are required if the string contains commas)"

input_hash.md provides much more detail:
"If this first character is a quotation mark ("), the string item will consist of all characters read between the first quotation mark and the second. Thus, a quoted string may not contain a quotation mark as a character. If the first character of the string is not a quotation mark, the string is an unquoted string, and will terminate on a comma, carriage or line feed (or after 255 characters have been read)."

The INPUT documentation should be more detailed about quote handling to match INPUT#.

---

---

#### documentation_inconsistency

**Description:** ERR/ERL documentation states ERR is reset to 0 after RESUME, but ERROR documentation doesn't mention this

**Affected files:**
- `docs/help/common/language/statements/err-erl-variables.md`
- `docs/help/common/language/statements/error.md`

**Details:**
err-erl-variables.md states:
"ERR is reset to 0 when:
  - RESUME statement is executed
  - A new RUN command is issued
  - An error handling routine ends normally (without error)"

error.md doesn't mention what happens to ERR after the simulated error is handled. For consistency, it should note that ERR will be reset after RESUME just like with real errors.

---

---

#### documentation_inconsistency

**Description:** Inconsistent maximum line length specification between LINE INPUT# and LINE INPUT

**Affected files:**
- `docs/help/common/language/statements/inputi.md`
- `docs/help/common/language/statements/line-input.md`

**Details:**
LINE INPUT# documentation states: 'To read an entire line (up to 254 characters)'
LINE INPUT documentation states: 'To input an entire line (up to 254 characters)'
Both claim 254 character limit, but this should be verified as consistent across both file and console input operations.

---

---

#### documentation_inconsistency

**Description:** Carriage return/line feed sequence handling ambiguity

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
Documentation states: 'LINE INPUT# reads all characters in the sequential file up to a carriage return. It then skips over the carriage return/line feed sequence'
But also states: '(If a line feed/carriage return sequence is encountered, it is preserved.)'
This is contradictory - does it skip CR/LF or preserve LF/CR? The order matters and behavior is unclear.

---

---

#### documentation_inconsistency

**Description:** MID$ assignment behavior description could be ambiguous

**Affected files:**
- `docs/help/common/language/statements/mid-assignment.md`

**Details:**
Documentation states: 'If the replacement string is shorter than length, only the available characters are replaced'
This could be interpreted two ways:
1. Only as many characters as are in the replacement string are replaced
2. The replacement string is used and remaining positions are unchanged
The examples suggest interpretation 1, but explicit clarification would help.

---

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note detail

**Affected files:**
- `docs/help/common/language/statements/out.md`
- `docs/help/common/language/statements/poke.md`

**Details:**
OUT states: 'Emulated as No-Op: This feature requires direct hardware I/O port access'
POKE states: 'Emulated as No-Op: This feature requires direct memory access'
Both are no-ops but POKE provides more detail: 'Programs using POKE will run without errors, but the memory writes are silently ignored.'
OUT should have similar detail about behavior.

---

---

#### documentation_inconsistency

**Description:** Maximum line number inconsistency

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
RENUM documentation states: 'Cannot create line numbers > 65529'
This specific limit should be verified as consistent across all line number operations (AUTO, GOTO, GOSUB, etc.) and documented in a central location.

---

---

#### documentation_inconsistency

**Description:** Cross-reference inconsistency: RESET warns not to confuse with RSET, but RSET warns not to confuse with RESET. Both should use consistent wording.

**Affected files:**
- `docs/help/common/language/statements/reset.md`
- `docs/help/common/language/statements/rset.md`

**Details:**
RESET.md says: 'Do not confuse RESET with [RSET](rset.md), which right-justifies strings in random file fields.'

RSET.md says: 'Do not confuse RSET with [RESET](reset.md), which closes all open files.'

Both warnings are correct but could be more consistently worded.

---

---

#### documentation_inconsistency

**Description:** Inconsistent description of file closing behavior across RUN, STOP, and SYSTEM

**Affected files:**
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
RUN.md: 'All open files are closed (unlike STOP, which keeps files open)'

STOP.md: 'Unlike the END statement, the STOP statement does not close files.'

SYSTEM.md: 'When SYSTEM is executed: All open files are closed'

This creates confusion about which statements close files. RUN says STOP keeps files open, but doesn't mention END. The relationship between all three needs clarification.

---

---

#### documentation_inconsistency

**Description:** Variable name significance documentation conflicts with settings documentation

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md says: 'Note on Variable Name Significance: In the original MBASIC 5.21, only the first 2 characters of variable names were significant (AB, ABC, and ABCDEF would be the same variable). This Python implementation uses the full variable name for identification, allowing distinct variables like COUNT and COUNTER.'

But then it says: 'Case Sensitivity: Variable names are not case-sensitive by default (Count = COUNT = count), but the behavior when using different cases can be configured via the variables.case_conflict setting'

This seems contradictory - if full names are used, why would Count and COUNT be the same? The explanation should clarify that case-insensitivity is separate from the 2-character limitation.

---

---

#### documentation_inconsistency

**Description:** Shortcuts documentation uses {{kbd:...}} syntax but doesn't explain what it means

**Affected files:**
- `docs/help/common/shortcuts.md`
- `docs/help/common/settings.md`

**Details:**
shortcuts.md uses syntax like: '{{kbd:run:cli}}', '{{kbd:run:curses}}', '{{kbd:run_program:tk}}'

This appears to be a template syntax for keyboard shortcuts, but there's no explanation of what these placeholders represent or how they're rendered. Users seeing the raw markdown would be confused.

---

---

#### documentation_inconsistency

**Description:** RESUME documentation has inconsistent example numbering

**Affected files:**
- `docs/help/common/language/statements/resume.md`

**Details:**
The examples are numbered 'Example 1', 'Example 2', 'Example 3', 'Example 4', 'Example 5', but most other documentation files use '## Example' without numbering, or use a single example section. This inconsistency makes the documentation feel less uniform.

---

---

#### documentation_inconsistency

**Description:** Settings documentation shows conflicting information about settings storage location

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
settings.md says:
'Settings are stored in JSON format:
- Linux/Mac: ~/.mbasic/settings.json
- Windows: %APPDATA%\mbasic\settings.json
- Project: .mbasic/settings.json in project directory'

But earlier it says 'Settings are stored at different scopes' with precedence order including 'File scope (highest priority) - Per-file settings (future feature)'

If file scope is a 'future feature', it shouldn't be in the storage locations list, or should be marked as such.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for stopping AUTO mode

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`

**Details:**
CLI docs say 'Press {{kbd:stop:cli}} to stop AUTO mode' while Curses docs say 'Exit AUTO mode with {{kbd:continue:curses}} or by typing a line number manually'. These appear to be different key combinations for the same action (stopping AUTO mode), but use different placeholder names (stop vs continue).

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about Find and Replace availability

**Affected files:**
- `docs/help/common/ui/tk/index.md`
- `docs/help/mbasic/extensions.md`

**Details:**
Tk docs state 'Find and replace' as an editor feature and list 'Find' ({{kbd:find:tk}}) in the Edit Menu, but extensions.md says 'Find and Replace (Tk only)' in the comparison table. However, the Tk docs only show a 'Find' menu item, not 'Replace', creating ambiguity about whether Replace is actually implemented.

---

---

#### documentation_inconsistency

**Description:** Inconsistent description of Web UI filename handling

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
Compatibility.md states 'Automatically uppercased by the virtual filesystem (CP/M style)' and 'The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage'. However, extensions.md only mentions 'Simple filenames only' without mentioning the uppercasing behavior. This is an important detail that should be consistent across both documents.

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about STEP command variants

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
Extensions.md shows 'STEP INTO' and 'STEP OVER' as '(planned)' features, but compatibility.md makes no mention of these variants when discussing debugging commands. The status of these features should be consistent across documentation.

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about WIDTH statement behavior

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
Compatibility.md states 'WIDTH is parsed for compatibility but performs no operation' and 'The "WIDTH LPRINT" syntax is not supported.' However, architecture.md makes no mention of WIDTH statement at all when discussing compatibility features. This omission could confuse users about whether WIDTH is implemented.

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about syntax highlighting availability

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
Extensions.md states 'Syntax highlighting (Tk, Web)' in the Editor Enhancements section, but Tk docs say 'Syntax highlighting (optional)' in the Editor Pane features. The word 'optional' suggests it may not always be available, but extensions.md implies it's a standard feature of Tk UI.

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about auto-save behavior

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
Extensions.md states 'Auto-save behavior varies by UI' and lists different behaviors for CLI/Tk/Curses vs Web UI. However, compatibility.md doesn't mention auto-save at all when discussing file operations. Users need to understand auto-save behavior for each UI to avoid data loss.

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about Find/Replace availability across UIs

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/find-replace.md`
- `docs/help/ui/cli/index.md`

**Details:**
features.md states 'Find/Replace is not available in Curses UI. Use the Tk UI for search/replace functionality' and 'Find/Replace is not available in CLI. Use the Tk UI for search/replace functionality' and 'Find/Replace is not available in Web UI. Use the Tk UI for search/replace functionality'. However, find-replace.md for CLI provides detailed workarounds and alternative methods, suggesting the feature gap is documented but the messaging is inconsistent about whether it's a limitation or just requires different approaches.

---

---

#### documentation_inconsistency

**Description:** Inconsistent UI listing - Web UI missing from getting-started.md

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/getting-started.md`

**Details:**
features.md lists four UIs: 'MBASIC supports four interfaces: Curses UI (Default), CLI Mode, Tkinter GUI, Web UI'. However, getting-started.md under 'Choosing a User Interface' only lists three: 'MBASIC supports four interfaces:' but then only documents Curses UI, CLI Mode, and Tkinter GUI. The Web UI section is present but the intro says 'four interfaces' when only three are shown in getting-started initially.

---

---

#### documentation_inconsistency

**Description:** Inconsistent count of functions between documents

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/index.md`

**Details:**
features.md states 'Functions (45+)' in the Functions section header. However, index.md states 'Functions - All 40 functions' in the BASIC-80 Language Reference section. This is a discrepancy of 5+ functions.

---

---

#### documentation_inconsistency

**Description:** Inconsistent count of statements and error codes

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/index.md`

**Details:**
features.md does not specify the total number of statements or error codes. However, cli/index.md states 'Statements - All 63 statements' and 'Error Codes - All 68 error codes'. These specific counts should be consistent across documentation or explained if they differ.

---

---

#### documentation_inconsistency

**Description:** Incomplete documentation about Web UI file storage limitations

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md states under Web UI: 'Session-based storage - Files persist during browser session only (lost on page refresh)' and 'In-memory filesystem - Virtual filesystem with limitations: 50 file limit maximum, 1MB per file maximum, No path support (simple filenames only), No persistent storage across sessions'. However, it then says 'See [Compatibility Guide](compatibility.md) for complete Web UI file storage details.' This suggests the Compatibility Guide should have more details, but we don't have that file to verify if the information is complete and consistent.

---

---

#### documentation_inconsistency

**Description:** Settings system not mentioned in main features document

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/settings.md`

**Details:**
settings.md provides extensive documentation about SHOWSETTINGS and SETSETTING commands, including categories like editor, keywords, variables, interpreter, and ui settings. However, features.md does not mention the settings system at all under any section (Program Control, Direct Commands, etc.). This is a significant feature omission from the main features list.

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about Execution Stack access method

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md states: "**Access methods:**
- Via menu: Ctrl+U → Debug → Execution Stack
- Via command: Type `STACK` in immediate mode (same as CLI)"

But quick-reference.md under "Global Commands" shows:
"| **Menu only** | Toggle execution stack window |"

This suggests menu-only access, contradicting the feature-reference.md claim that you can also use the STACK command in immediate mode.

---

---

#### documentation_inconsistency

**Description:** Different default sort orders documented for variables window

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/cli/variables.md`

**Details:**
curses/variables.md states: "**Note**: The default sort order is 'Accessed' with newest first."

But cli/variables.md doesn't mention any sorting capability at all, which is correct since CLI uses PRINT for variable inspection. However, the curses documentation should clarify this is a Curses-specific feature not available in CLI.

---

---

#### documentation_inconsistency

**Description:** Conflicting information about variable sorting options

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
variables.md states: "Press `s` to cycle through sort orders:
- **Accessed**: Most recently accessed (read or written) - shown first (default)
- **Written**: Most recently written to - shown first
- **Read**: Most recently read from - shown first
- **Name**: Alphabetical by variable name"

But feature-reference.md states: "### Variable Sorting (s key in variables window)
Cycle through different sort orders:
- **Accessed**: Most recently accessed (read or written) - newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name

Press 'd' to toggle sort direction (ascending/descending)."

The wording differs slightly ("shown first" vs "newest first") which could cause confusion about whether these are the same or different behaviors.

---

---

#### documentation_inconsistency

**Description:** Missing cross-reference to error handling in CLI variables documentation

**Affected files:**
- `docs/help/ui/common/errors.md`
- `docs/help/ui/cli/variables.md`

**Details:**
cli/variables.md shows examples of checking variables during debugging but doesn't mention how to handle errors that might occur. The errors.md document exists and covers error handling comprehensively, but there's no link from the CLI variables page to error handling documentation, even though debugging often involves handling errors.

---

---

#### documentation_inconsistency

**Description:** Placeholder documentation conflicts with detailed UI-specific documentation

**Affected files:**
- `docs/help/ui/common/running.md`
- `docs/help/ui/curses/running.md`

**Details:**
common/running.md states: "**Status:** PLACEHOLDER - Documentation in progress

This page will cover:
- How to run BASIC programs
- RUN command
- Program execution
- Stopping programs
- Continuing after STOP"

But curses/running.md provides complete, detailed documentation for running programs in the Curses UI. The common/running.md placeholder should either be removed or updated to reference the UI-specific documentation.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Step Statement

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states:
"Step Statement
Execute one BASIC statement at a time.
- Menu: Run → Step Statement
- Toolbar: 'Stmt' button
- No keyboard shortcut"

But features.md states:
"Debug with:
- {{kbd:step_statement:tk}} - Execute next statement"

One document says there is no keyboard shortcut, the other references {{kbd:step_statement:tk}}.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Continue

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states:
"Continue
Resume execution after pausing at a breakpoint.
- Menu: Run → Continue
- Toolbar: 'Cont' button
- No keyboard shortcut"

But features.md states:
"Debug with:
- {{kbd:continue_execution:tk}} - Continue to next breakpoint"

One document says there is no keyboard shortcut, the other references {{kbd:continue_execution:tk}}.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Step Line

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states:
"Step Line (F10)
Execute one line at a time.
- Menu: Run → Step Line
- Shortcut: F10"

But features.md states:
"Debug with:
- {{kbd:step_line:tk}} - Execute next line"

feature-reference.md says F10, features.md uses {{kbd:step_line:tk}} placeholder. These should be consistent.

---

---

#### documentation_inconsistency

**Description:** Missing Search Help keyboard shortcut in feature-reference.md

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states:
"Search Help
Search across all help documentation:
**Note:** Search function is available via the help browser's search box (no dedicated keyboard shortcut)."

But features.md does not mention Search Help at all in its features list. This could mean:
1. features.md is incomplete (missing Search Help)
2. Search Help is not actually a key feature worth highlighting
3. The note about 'no dedicated keyboard shortcut' might be outdated

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut references for Variables Window

**Affected files:**
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/tips.md`

**Details:**
workflows.md states:
"2. Press **{{kbd:toggle_variables:tk}}** to open Variables window"

But tips.md states:
"Keep Variables window open (**{{kbd:toggle_variables:tk}}**):"

Both use the same placeholder, which is good, but the feature-reference.md shows this as a real shortcut. The inconsistency is minor but worth noting for completeness.

---

---

#### documentation_inconsistency

**Description:** Inconsistent implementation status within debugging.md

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md has conflicting statements about variable inspector:

At the top of Variable Inspector section:
"**Implementation Status:** Basic variable viewing via Debug menu is currently available. The detailed variable inspector panels, watch expressions, and interactive editing features described below are **planned for future releases** and not yet implemented."

But earlier in the document under "Starting Debug Session":
"**Currently implemented:**
- **Run ({{kbd:run:web}})** - Start program from beginning
- **Continue ({{kbd:continue:web}})** - Run to next breakpoint
- **Step ({{kbd:step:web}})** - Step to next line
- **Stop ({{kbd:stop:web}})** - End execution"

No mention of variable viewing being "currently available" in the implemented list, creating confusion about what actually works.

---

---

#### documentation_inconsistency

**Description:** Inconsistent Run Program keyboard shortcuts

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
feature-reference.md states:
"Run Program ({{kbd:run_program:tk}} or F5)
Execute the current program from the beginning.
- Shortcuts: {{kbd:run_program:tk}} or F5"

But getting-started.md states:
"| {{kbd:run_program}} | Run program |"

Note the difference: feature-reference.md uses {{kbd:run_program:tk}} (with :tk suffix), getting-started.md uses {{kbd:run_program}} (without suffix). This could cause template expansion issues.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut format in tables

**Affected files:**
- `docs/help/ui/tk/getting-started.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
getting-started.md uses:
"| {{kbd:save_file}} | Save file |"

But feature-reference.md uses:
"| {{kbd:file_save:tk}} | Save File |"

The action names are different: 'save_file' vs 'file_save'. This suggests either:
1. Different keyboard shortcut systems
2. Outdated documentation
3. Copy-paste errors

---

---

#### documentation_inconsistency

**Description:** Conflicting information about toggle_breakpoint keyboard shortcut

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md states at the end:
"**Note:** {{kbd:toggle_breakpoint:web}} is implemented but currently available via menu only (not yet bound to keyboard)."

But earlier in "Keyboard Shortcuts" section it lists:
"**Planned for Future Releases:**
- Statement-level stepping (execute one statement at a time)
- Navigation shortcuts for debugger panels
- Variable inspector shortcuts"

No mention of toggle_breakpoint being implemented. The note at the end contradicts the earlier section by saying it IS implemented (just not bound to keyboard yet).

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about file operations and 'Open Example' feature

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
features.md under 'File Operations > Currently Implemented' lists: 'Load .BAS files from local filesystem' and 'Save/download programs as .BAS files'.

However, web-interface.md under 'File Menu' states: 'Note: An "Open Example" feature to choose from sample BASIC programs is planned for a future release.'

But features.md does not mention 'Open Example' at all in either the 'Currently Implemented' or 'Planned' sections under File Operations. This omission creates inconsistency about whether this feature exists, is planned, or was forgotten in the documentation.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about settings storage implementation

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/settings.md`

**Details:**
features.md under 'Local Storage > Currently Implemented' states: 'Editor settings stored in browser localStorage (persists across sessions)'

However, settings.md provides much more detailed information about two storage modes: localStorage (default) and Redis session storage (for multi-user deployments). It describes Redis storage as: 'If the web server is configured with `NICEGUI_REDIS_URL`, settings are stored in Redis with per-session isolation'.

The question is: Is Redis storage currently implemented or planned? features.md doesn't mention Redis at all, suggesting it might be a planned feature that was documented prematurely in settings.md, or features.md is outdated.

---

---

#### documentation_inconsistency

**Description:** Calendar program appears in both Games and Utilities libraries with different descriptions and different actual programs

**Affected files:**
- `docs/library/games/index.md`
- `docs/library/utilities/index.md`

**Details:**
Games library describes calendar.bas as 'Full-year calendar display program - shows entire year's calendar at once (Creative Computing, 1979)' with a note pointing to Utilities.

Utilities library describes calendar.bas as 'Month/year calendar generator - prompts for specific month and year (1900-2099), prints formatted calendar (Dr Dobbs, 1982)' with a note pointing to Games.

These are clearly two different programs (1979 vs 1982, different sources, different functionality) but both are named 'calendar.bas'. The cross-references suggest they are alternatives, but they have the same filename which would cause a conflict.

---

---

#### documentation_inconsistency

**Description:** Most game entries are missing descriptions, authors, and tags

**Affected files:**
- `docs/library/games/index.md`

**Details:**
Out of approximately 130 games listed, only 3 have complete metadata (Calendar, Survival, and a few others). The vast majority show:

**Year:** 1980s
**Tags:** 

with empty descriptions and tags. This is inconsistent with other library categories (Electronics, Ham Radio, Utilities) where most entries have detailed descriptions.

---

---

#### documentation_inconsistency

**Description:** Timer555.bas appears to be duplicate of 555-ic.bas

**Affected files:**
- `docs/library/electronics/index.md`

**Details:**
Two entries with very similar descriptions:

555-Ic: '555 Timer calculator - calculates resistance and capacitance values for proper operation of the 555 timer-oscillator at desired frequency'

Timer555: '555 Timer circuit calculator - calculates component values for 555 timer circuits (similar to 555-ic.bas)'

The Timer555 description explicitly notes it's 'similar to 555-ic.bas', suggesting these may be duplicate or very similar programs. This should be clarified - are they different implementations, or is one redundant?

---

---

#### documentation_inconsistency

**Description:** CHOOSING_YOUR_UI.md claims CLI has 'full debugging capabilities through text commands' but QUICK_REFERENCE.md only documents Curses UI debugging features

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states:
'**Unique advantages:**
- Command-line debugging (BREAK, STEP, STACK commands)'

and

'**Limitations:**
- No visual debugging interface (debugging via text commands only)'

But QUICK_REFERENCE.md is titled 'MBASIC Curses IDE - Quick Reference Card' and only documents Curses UI debugging with keyboard shortcuts like 'b' or 'F9' for breakpoints, and 'c', 's', 'e' for continue/step/end. No documentation found for CLI text commands like BREAK, STEP, STACK.

---

---

#### documentation_inconsistency

**Description:** CHOOSING_YOUR_UI.md mentions 'Conditional breakpoints' as unique to Web UI, but SETTINGS_AND_CONFIGURATION.md doesn't document this feature

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
CHOOSING_YOUR_UI.md lists under Web UI unique advantages:
'- Conditional breakpoints'

However, SETTINGS_AND_CONFIGURATION.md has no mention of conditional breakpoints, how to set them, or any settings related to them. This feature is not documented anywhere in the settings system.

---

---

#### documentation_inconsistency

**Description:** INSTALL.md says 'All core language features and statements are implemented' but CHOOSING_YOUR_UI.md implies some debugging features vary by UI

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
INSTALL.md states:
'This is a comprehensive implementation of MBASIC 5.21. All core language features and statements are implemented and tested'

But CHOOSING_YOUR_UI.md shows debugging capabilities differ:
- CLI: 'Command-line debugging (BREAK, STEP, STACK commands)' but 'No visual debugging interface'
- Curses/Tk/Web: Have visual debugging features

This suggests debugging features are UI-dependent, not core language features, but the distinction isn't clearly explained.

---

---

#### documentation_inconsistency

**Description:** Settings documentation shows boolean values as 'true/false' in examples but doesn't clarify if they're case-sensitive

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
Examples show:
'SET "editor.auto_number" true'
'SET "editor.show_line_numbers" true'

And in JSON:
'"editor.auto_number": true'

The note says 'Booleans: true or false (lowercase, no quotes in both commands and JSON files)' but this appears only once in the Type Conversion section. It should be more prominent since case-sensitivity in boolean values is a common source of errors.

---

---

#### documentation_inconsistency

**Description:** Installation guide lists 'urwid' for Curses but CHOOSING_YOUR_UI.md doesn't mention this dependency in its Curses section

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
INSTALL.md clearly states:
'| **Curses** | `urwid` (install via pip) |'

But CHOOSING_YOUR_UI.md's Curses section under 'Unique advantages' says:
'- No GUI dependencies'

This is misleading - Curses does have a dependency (urwid), it just doesn't require GUI/X11 dependencies. The distinction should be clearer.

---

---

#### documentation_inconsistency

**Description:** Decision matrix shows conflicting information about Curses mouse support

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
In the detailed Curses section:
'**Limitations:**
- Limited mouse support'

But in the Decision Matrix at the bottom:
'| **Mouse support** | ❌ | ⚠️ Limited | ✅ | ✅ |'

The CLI column shows ❌ (no mouse support) which is correct, but the inconsistency is that 'Limited mouse support' is listed as both a limitation and a feature. It's unclear what 'limited' means - does it work for some things but not others? Which features support mouse and which don't?

---

---

#### documentation_inconsistency

**Description:** Web UI startup time includes 'browser launch time' but this varies dramatically by browser and whether it's already running

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
Performance Comparison shows:
'4. **Web**: ~2s (includes browser launch time)'

Browser launch time can vary from 0s (if browser already open) to 10+ seconds (cold start of Chrome/Firefox). This measurement is not meaningful without more context. Should specify if this is with browser already running or cold start.

---

---

#### documentation_inconsistency

**Description:** TK_UI_QUICK_START.md references keyboard shortcuts for Tk UI but keyboard-shortcuts.md only documents Curses UI shortcuts

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md uses placeholders like {{kbd:run_program}}, {{kbd:file_save}}, {{kbd:smart_insert}}, {{kbd:renumber}}, {{kbd:toggle_variables}}, {{kbd:toggle_stack}}, {{kbd:toggle_breakpoint}}, {{kbd:replace}}, {{kbd:file_open}}, {{kbd:file_new}}, {{kbd:help_topics}}, {{kbd:file_quit}} for Tk UI.

However, keyboard-shortcuts.md is titled 'MBASIC Curses UI Keyboard Shortcuts' and only documents Curses shortcuts like Ctrl+R (Run), Ctrl+V (Save), Ctrl+N (New), Ctrl+O (Open), Ctrl+H (Help), Ctrl+Q (Quit), Ctrl+E (Renumber), Ctrl+W (Toggle variables), Ctrl+B (Toggle breakpoint), etc.

There is no corresponding keyboard-shortcuts document for Tk UI, leaving the {{kbd:*:tk}} placeholders unresolved.

---

---

#### documentation_inconsistency

**Description:** UI_FEATURE_COMPARISON.md uses template notation for keyboard shortcuts but references keyboard-shortcuts.md which uses literal key combinations

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
UI_FEATURE_COMPARISON.md states at the top:
'> **Note:** This guide uses `{{kbd:action:ui}}` notation for keyboard shortcuts. These are template variables that represent actual key combinations. For specific key mappings, see the Help menu in each UI or the individual UI quick reference guides.'

It then uses placeholders like {{kbd:run:cli}}, {{kbd:run:curses}}, {{kbd:run_program:tk}}, {{kbd:run:web}} throughout.

However, keyboard-shortcuts.md (the only keyboard shortcuts doc provided) uses literal key combinations like 'Ctrl+R', 'Ctrl+V', etc., not template notation. There's a mismatch in documentation approach.

---

---

#### 🟢 Low Severity

---

#### Code vs Comment conflict

**Description:** CallStatementNode.arguments field documented as unused but still present in dataclass

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode docstring states: 'Implementation Note: The \'arguments\' field is currently unused (always empty list). It exists for potential future support of BASIC dialects that allow CALL with arguments (e.g., CALL ROUTINE(args)). Standard MBASIC 5.21 only accepts a single address expression in the \'target\' field. Code traversing the AST can safely ignore the \'arguments\' field for MBASIC 5.21 programs.' This is a design decision for future compatibility, but creates confusion about whether the field should be checked.

---

---

#### Documentation inconsistency

**Description:** LineNode docstring mentions 'src.position_serializer module' but file path not verified in provided code

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring states: 'Text regeneration is handled by the src.position_serializer module which reconstructs source text from statement nodes and their token information. The serializer\'s serialize_line() method uses each statement\'s tokens and char_start/char_end offsets to regenerate the exact source text with preserved formatting and keyword casing.' However, no src/position_serializer.py file was provided in the source code files to verify this reference is correct.

---

---

#### Documentation inconsistency

**Description:** StatementNode docstring references tk_ui module that is not provided

**Affected files:**
- `src/ast_nodes.py`

**Details:**
StatementNode docstring states: 'Note: char_start/char_end are populated by the parser and used by: - UI highlighting: tk_ui._highlight_current_statement() highlights the currently executing statement by underlining the text from char_start to char_end'. The tk_ui module is not included in the provided source files, making this reference unverifiable.

---

---

#### Documentation inconsistency

**Description:** RemarkStatementNode comment_type default value explanation may be incomplete

**Affected files:**
- `src/ast_nodes.py`

**Details:**
RemarkStatementNode docstring states: 'Default value "REM" is used only when creating nodes programmatically (not from parsed source).' However, it's unclear what happens if a node is created programmatically with comment_type="APOSTROPHE" - will it regenerate as an apostrophe comment or REM? The relationship between comment_type and source regeneration needs clarification.

---

---

#### code_vs_comment

**Description:** EOF function docstring references execute_open() in interpreter.py but provides incomplete search guidance

**Affected files:**
- `src/basic_builtins.py`

**Details:**
The EOF docstring says:
"See execute_open() in interpreter.py for file opening implementation (search for 'execute_open')"

This is redundant - saying 'search for execute_open' when already naming the function. The comment could be clearer about what specific aspect of execute_open is relevant (the mode setting and binary file handling).

---

---

#### documentation_inconsistency

**Description:** Module docstring references 'MBASIC 5.21 (CP/M era MBASIC-80)' but doesn't explain relationship between version numbers

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring says:
"Built-in functions for MBASIC 5.21 (CP/M era MBASIC-80).

Note: Version 5.21 refers to BASIC-80 Reference Manual Version 5.21, which documents
Microsoft BASIC-80 as implemented for CP/M systems."

This is slightly confusing - it says 'MBASIC 5.21' then clarifies it's the manual version, not necessarily the BASIC version. Could be clearer about whether MBASIC itself has a version number distinct from the manual.

---

---

#### code_vs_comment

**Description:** Comment says 'Error: invalid return address' but this is not really an error condition in correct programs

**Affected files:**
- `src/codegen_backend.py`

**Details:**
Line 357: 'default: break;  /* Error: invalid return address */'

The comment suggests this is an error, but the code just breaks (does nothing). In a correctly structured BASIC program with matching GOSUB/RETURN pairs, this case should never execute. The comment could be clearer that this is a safety fallback for malformed programs, not a runtime error handler.

---

---

#### code_vs_comment

**Description:** Comment about negative step handling is incomplete/misleading

**Affected files:**
- `src/codegen_backend.py`

**Details:**
Lines 254-257:
'# Determine comparison operator based on step
if stmt.step_expr:
    # If step is negative, use >= instead of <=
    # For now, assume positive step (TODO: handle negative steps)
    comp = \'<=\''

The comment says 'If step is negative, use >= instead of <=' but the code always uses '<=' regardless of step value. The TODO indicates this is unimplemented, but the comment structure suggests conditional logic that doesn't exist.

---

---

#### documentation_inconsistency

**Description:** Duplicate two-letter error codes documented but potential ambiguity not fully explained

**Affected files:**
- `src/error_codes.py`

**Details:**
Lines 7-18 explain duplicate two-letter codes:
'Note: Some two-letter codes are duplicated across different numeric error codes.
This matches the original MBASIC 5.21 specification where the two-letter codes
alone are ambiguous - the numeric code is authoritative.

Specific duplicates (from MBASIC 5.21 specification):
- DD: code 10 ("Duplicate definition") and code 68 ("Device unavailable")
- DF: code 25 ("Device fault") and code 61 ("Disk full")
- CN: code 17 ("Can't continue") and code 69 ("Communication buffer overflow")'

However, the format_error() function (line 77) only uses two-letter codes in output: f'?{two_letter} Error in {line_number}'. This means error messages displayed to users would be ambiguous (e.g., '?DD Error in 100' could mean either error 10 or 68). The documentation doesn't explain how this ambiguity is resolved in user-facing error messages.

---

---

#### code_vs_comment

**Description:** Comment says 'Error: invalid return address' uses break, but doesn't explain what happens after break

**Affected files:**
- `src/codegen_backend.py`

**Details:**
Lines 356-357:
'default: break;  /* Error: invalid return address */'

After the break, execution continues past the switch statement and the if block, effectively doing nothing. The comment doesn't clarify that this silently ignores invalid returns rather than reporting an error or halting execution.

---

---

#### Code vs Documentation inconsistency

**Description:** Documentation uses state name strings that don't exist in actual implementation

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Documentation states: "State names used in documentation (not actual enum values): 'idle', 'paused', 'at_breakpoint', 'done', 'error', 'waiting_for_input', 'running'"

Then later: "Note: The actual implementation checks boolean flags (halted, error_info, input_prompt), not string state values."

This is confusing because the documentation introduces state names that are never used anywhere in the codebase. While the note clarifies this, it would be clearer to document the actual boolean flags directly rather than inventing conceptual state names.

---

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for storage location in SandboxedFileIO documentation

**Affected files:**
- `src/file_io.py`

**Details:**
The documentation uses multiple terms for the same concept:
1. "Python server memory (NOT browser localStorage or disk files)"
2. "Storage location: Python server memory"
3. "server memory virtual filesystem"
4. "in-memory virtual filesystem"

While these all refer to the same thing, the repeated clarification and varied terminology suggests uncertainty about whether readers will understand. The documentation would be clearer with consistent terminology.

---

---

#### Code vs Documentation inconsistency

**Description:** The is_valid_input_char() docstring states it 'Rejects: Extended ASCII (128-255)' but the function actually accepts any character in range 32-126, which means it would accept character code 126 but the rejection description suggests 127+ are rejected. The DEL character (127) is not explicitly mentioned in the 'Allows' section but is implicitly rejected.

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Docstring says:
"Allows:
- Printable ASCII (32-126): space through tilde"
"Rejects:
- Extended ASCII (128-255)"

Code implementation:
"if 32 <= code <= 126:
    return True"

The DEL character (127) falls between printable ASCII and extended ASCII but isn't explicitly documented in either category. The example shows it's rejected, but the main documentation doesn't clearly state this.

---

---

#### Documentation inconsistency

**Description:** The clear_parity() function docstring example shows 'chr(193)' as 'A with bit 7 set' and claims it returns 'A', but 193 & 0x7F = 65 which is indeed 'A'. However, the clear_parity_all() example shows 'chr(193) + chr(194)' returning 'AB', but 194 & 0x7F = 66 which is 'B'. The documentation is technically correct but could be clearer that these are the ASCII values with bit 7 set (193='A'+128, 194='B'+128).

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
clear_parity() docstring:
">>> clear_parity(chr(193))  # 'A' with bit 7 set
'A'"

clear_parity_all() docstring:
">>> clear_parity_all(chr(193) + chr(194))  # Characters with bit 7 set
'AB'"

The comment 'Characters with bit 7 set' doesn't specify which characters, making it less clear than the clear_parity() example.

---

---

#### code_vs_comment

**Description:** Comment about MERGE passing all variables contradicts MBASIC spec

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in cmd_chain() (line ~470): 'Save variables based on CHAIN options:
- ALL: passes all variables to the chained program
- MERGE: merges program lines (overlays code) - NOTE: Currently also passes all vars
- Neither: passes only COMMON variables (resolves type suffixes if needed)

MBASIC 5.21 behavior: MERGE and ALL are orthogonal options.
Current implementation: Both MERGE and ALL result in passing all variables.
TODO: Separate line merging (MERGE) from variable passing (ALL).'

The code at line ~480 shows: 'if all_flag or merge: # Save all variables'

This is documented as a known deviation with a TODO, but it's still an inconsistency between the MBASIC spec and implementation.

---

---

#### code_vs_comment

**Description:** Comment says readline enhances input() with Ctrl+A rebinding, but implementation details unclear

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~30: 'Try to import readline for better line editing
This enhances input() with:
- Backspace/Delete working properly
- Arrow keys for navigation
- Command history (up/down arrows)
- Ctrl+E (end of line)
- Other Emacs keybindings (Ctrl+K, Ctrl+U, etc.)
Note: Ctrl+A is rebound for EDIT mode to insert ASCII 0x01 (see _setup_readline)'

The _setup_readline() method (line ~165) does bind Ctrl+A: 'readline.parse_and_bind("Control-a: self-insert")'

However, the comment says Ctrl+A 'inserts ASCII 0x01' but the code comment at line ~170 says 'Bind Ctrl+A to insert the character (ASCII 0x01) into the input line, overriding the default Ctrl+A (beginning-of-line) behavior.' This is consistent, but the mechanism is unclear - does 'self-insert' automatically insert 0x01, or does the terminal send 0x01 when Ctrl+A is pressed? The comment doesn't explain this clearly.

---

---

#### code_vs_comment_conflict

**Description:** Comment in execute_immediate() describes complex GOTO/GOSUB behavior that may not match user expectations

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states:
'Note: GOTO/GOSUB in immediate mode work but PC restoration affects CONT behavior:
They execute and jump during execute_statement(), but we restore the
original PC afterward to preserve CONT functionality. This means:
- The jump happens and target code runs during execute_statement()
- The final PC change is then reverted, preserving the stopped position
- CONT will resume at the original stopped location, not the GOTO target'

This describes a complex behavior where GOTO/GOSUB execute but their PC changes are reverted. The comment says 'marked "not recommended" in help text' but the cmd_help() method shows no such warning about GOTO/GOSUB in immediate mode. This is a documentation inconsistency.

---

---

#### documentation_inconsistency

**Description:** cmd_help() does not document GOTO/GOSUB warnings mentioned in execute_immediate() comments

**Affected files:**
- `src/interactive.py`

**Details:**
The execute_immediate() method has extensive comments about GOTO/GOSUB behavior being 'not recommended' in immediate mode, stating 'hence marked "not recommended" in help text'. However, cmd_help() does not mention GOTO, GOSUB, or any warnings about their use in immediate mode. The help text only shows:
'Program Management:', 'Debugging:', 'Settings:', 'File System:' sections with no mention of statement-level commands or their limitations.

---

---

#### code_vs_comment_conflict

**Description:** Comment in execute_immediate() about line_text_map design decision may be outdated

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states:
'Pass empty line_text_map since immediate mode uses temporary line 0.
Design note: Could pass {0: statement} to improve error reporting, but immediate
mode errors typically reference the statement the user just typed (visible on screen),
so line_text_map provides minimal benefit. Future enhancement if needed.'

This is a design rationale comment that describes passing an empty dict for line_text_map. However, the code actually builds 'program_text = "0 " + statement' which creates a line 0. The comment suggests this is intentional but describes it as providing 'minimal benefit' for error reporting. This may be outdated if error reporting has changed or if the benefit assessment is no longer accurate.

---

---

#### code_vs_comment_conflict

**Description:** Comment about bare except being 'acceptable' may not align with modern Python best practices

**Affected files:**
- `src/interactive.py`

**Details:**
In _read_char() method:
'# Fallback for non-TTY/piped input or any terminal errors.
# Bare except is acceptable here because we're degrading gracefully to basic read()
# on any error (AttributeError, termios.error, ImportError on Windows, etc.)'

The comment justifies using bare 'except:' but modern Python style guides (PEP 8) recommend against bare except clauses. While the rationale is provided, the comment doesn't acknowledge this is a style deviation or explain why catching BaseException (including KeyboardInterrupt, SystemExit) is safe here.

---

---

#### code_vs_comment

**Description:** InterpreterState docstring execution order doesn't match actual tick_pc() implementation order

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 44-51 lists execution order:
"1. pause_requested check - pauses if pause() was called
2. halted check - stops if already halted
3. break_requested check - handles Ctrl+C breaks
4. breakpoints check - pauses at breakpoints
5. trace output - displays [line] or [line.stmt] if TRON is active
6. statement execution - where input_prompt may be set
7. error handling - where error_info is set via exception handlers"

But tick_pc() implementation (lines 355-450) shows:
1. pause_requested check (line 358)
2. halted check (line 364)
3. break_requested check (line 373)
4. breakpoints check (line 385) - BUT this happens BEFORE trace output
5. trace output (line 407) - happens AFTER breakpoint check

The order of steps 4 and 5 is swapped in the implementation vs documentation.

---

---

#### documentation_inconsistency

**Description:** InterpreterState docstring has inconsistent formatting for property descriptions

**Affected files:**
- `src/interpreter.py`

**Details:**
The docstring at lines 30-53 uses different formatting styles:
- Lines 33-36 use bullet points with colons: "- error_info: Non-None if..."
- Lines 38-51 use numbered list with dashes: "1. pause_requested check - pauses if..."

Inconsistent punctuation and formatting makes the documentation harder to read.

---

---

#### code_vs_comment

**Description:** Comment about return_stmt validation uses confusing terminology

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 1001-1010 says:
"# return_stmt is 0-indexed offset into statements array.
# Valid range: 0 to len(statements) (inclusive).
# - 0 to len(statements)-1: Normal statement positions
# - len(statements): Special sentinel - GOSUB was last statement on line, so RETURN
#   continues at next line. This value is valid because PC can point one past the
#   last statement to indicate 'move to next line' (handled by statement_table.next_pc).
# Values > len(statements) indicate the statement was deleted (validation error).
# Validation: return_stmt > len(line_statements) means the statement was deleted
# (Note: return_stmt == len(line_statements) is valid as a sentinel value)"

The comment switches between "len(statements)" and "len(line_statements)" without clarifying they're the same thing. Also, the phrase "Special sentinel" is used but the code at line 1018 just treats it as a normal PC value without special handling.

---

---

#### code_vs_comment

**Description:** Comment in execute_resume says 'RESUME 0' is equivalent to 'RESUME', but the distinction is preserved in the AST

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says:
"# RESUME or RESUME 0 - retry the statement that caused the error
# Note: MBASIC allows both 'RESUME' and 'RESUME 0' as equivalent syntactic forms.
# Parser preserves the distinction (None vs 0) for source text regeneration,
# but runtime execution treats both identically."

Code checks:
if stmt.line_number is None or stmt.line_number == 0:

This is consistent, but the comment could be clearer that the check handles both None (RESUME) and 0 (RESUME 0) as the same case.

---

---

#### code_vs_comment_conflict

**Description:** Comment about debugger_set parameter is overly defensive and suggests uncertainty

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_functioncall() (line ~3095), comment states:
"Note: get_variable_for_debugger() and debugger_set=True are used to avoid triggering variable access tracking... Maintainer warning: Ensure all internal variable operations use debugger_set=True"

The "Maintainer warning" suggests this is a fragile pattern that could easily be broken, but doesn't explain why this approach was chosen over a more robust design. This defensive comment pattern appears throughout the codebase.

---

---

#### code_vs_comment_conflict

**Description:** Character vs byte count comment is overly detailed for ASCII assumption

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_binaryop() (line ~3030), comment states:
"Also note: len() counts characters. For ASCII and latin-1 (both single-byte encodings), character count equals byte count. Field buffers (LSET/RSET) use latin-1 encoding. This implementation assumes strings are ASCII/latin-1; Unicode strings with multi-byte characters may have len() < 255 but exceed 255 bytes. MBASIC 5.21 used single-byte encodings only."

This level of detail about encoding suggests either: (1) there was a bug related to this that required extensive documentation, or (2) the implementation doesn't actually handle this correctly and the comment is defensive. For a BASIC interpreter targeting MBASIC 5.21 compatibility, this should be a non-issue.

---

---

#### Documentation inconsistency

**Description:** Module docstring states GUIIOHandler is not exported due to dependencies, but gui.py shows it's a stub with no actual dependencies

**Affected files:**
- `src/iohandler/__init__.py`
- `src/iohandler/gui.py`

**Details:**
__init__.py says: "GUIIOHandler and WebIOHandler are not exported here because they have dependencies on their respective UI frameworks (tkinter, nicegui)."

But gui.py shows GUIIOHandler is actually a stub implementation with no external dependencies:
"class GUIIOHandler(IOHandler):
    '''GUI-based I/O handler stub.
    This is a minimal stub implementation showing how to create a custom I/O handler for GUI applications.'''

The stub only uses internal buffers and has no tkinter dependency.

---

---

#### Code vs Comment conflict

**Description:** Backward compatibility comment for print() method says it was renamed to avoid conflicts with Python's built-in, but both methods coexist

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment states:
    # Backward compatibility alias
    # This method was renamed from print() to output() to avoid conflicts with Python's
    # built-in print function. The print() alias is maintained for backward compatibility
    # with older code that may still call io_handler.print().
    def print(self, text="", end="\n"):

However, having a method named print() doesn't actually conflict with the built-in print() function in Python - they exist in different namespaces (instance method vs built-in function). The comment's reasoning is technically incorrect.

---

---

#### Documentation inconsistency

**Description:** Inconsistent documentation about input() behavior regarding whitespace preservation

**Affected files:**
- `src/iohandler/console.py`

**Details:**
console.py input_line() docstring says:
        '''Input a complete line from console.
        For console, this delegates to self.input() (same behavior).
        Note: Python's input() strips only the trailing newline. Leading/trailing
        spaces are generally preserved, but terminal input behavior may vary across
        platforms. See input_line() documentation in base.py for details.'''

This states "Leading/trailing spaces are generally preserved" but then adds "terminal input behavior may vary across platforms" which creates uncertainty. The base.py documentation is clearer about this being a platform limitation.

---

---

#### Code inconsistency

**Description:** curses_io.py input_line() docstring says it does NOT preserve trailing spaces, but this contradicts the stated goal in base.py

**Affected files:**
- `src/iohandler/curses_io.py`

**Details:**
curses_io.py input_line() says:
        '''Input a full line (LINE INPUT statement).
        Args:
            prompt: Prompt to display
        Returns:
            User input as string
        Note: Current implementation does NOT preserve trailing spaces as documented
        in base class. curses getstr() strips trailing whitespace (spaces, tabs, newlines).
        Leading spaces are preserved. This is a known limitation - see input_line()
        documentation in base.py.'''

base.py input_line() says:
        '''Input a complete line from user (LINE INPUT statement).
        Design goal: Preserve leading/trailing spaces and not interpret commas as
        field separators (for MBASIC LINE INPUT compatibility).'''

The "design goal" language in base.py is appropriate, and the curses implementation correctly documents its limitation. This is consistent documentation of a known platform limitation.

---

---

#### Documentation inconsistency

**Description:** Module docstring references SimpleKeywordCase but doesn't provide import path

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
Module docstring says:
"Note: This class provides advanced case policies (first_wins, preserve, error) via
CaseKeeperTable and is used by parser.py and position_serializer.py. For simpler
force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py)
which only supports force_lower, force_upper, and force_capitalize."

The reference to SimpleKeywordCase provides the file path but not the import statement. For consistency with other documentation, it could specify: "from src.simple_keyword_case import SimpleKeywordCase"

---

---

#### code_vs_comment

**Description:** Comment about identifier case handling mentions two different fields but explanation could be clearer

**Affected files:**
- `src/lexer.py`

**Details:**
In read_identifier() method around line 280:
"# Preserve original case for display. Identifiers use the original_case field
# to store the exact case as typed. Keywords use original_case_keyword to store
# the case determined by the keyword case policy (see Token class in tokens.py)."

This comment is placed in the identifier section but discusses both identifiers and keywords. The Token class definition is not provided to verify these field names exist and are used as described.

---

---

#### code_vs_comment

**Description:** Comment about old BASIC preprocessing contradicts the actual implementation which does handle PRINT# special case

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line ~270 states:
"# NOTE: We do NOT handle old BASIC where keywords run together (NEXTI, FORI).
# This is properly-formed MBASIC 5.21 which requires spaces.
# Exception: PRINT# and similar file I/O keywords (handled above) support # without space.
# Other old BASIC syntax should be preprocessed with conversion scripts."

However, the code immediately above (lines ~250-265) DOES implement special handling for keywords ending with # (PRINT#, INPUT#, etc.), splitting them back out. This is a form of handling 'run together' syntax, contradicting the claim that such syntax is not handled.

---

---

#### documentation_inconsistency

**Description:** Module docstring claims implementation enables Extended BASIC features but doesn't specify which features beyond periods in identifiers

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring states:
"MBASIC 5.21 Extended BASIC features: This implementation enables Extended BASIC
features (e.g., periods in identifiers like 'RECORD.FIELD') as they are part of MBASIC 5.21."

Only one example (periods in identifiers) is given. It's unclear what other Extended BASIC features are enabled or if this is the only one.

---

---

#### code_vs_comment

**Description:** Comment about type suffix behavior may not match implementation for all cases

**Affected files:**
- `src/lexer.py`

**Details:**
In read_identifier() at line ~220:
"# Type suffix - terminates identifier (e.g., A$ reads as A$, not A$B)"

This comment suggests type suffixes always terminate identifiers. However, the special case handling for file I/O keywords with # (lines ~250-265) shows that # can be treated differently depending on context. The comment doesn't acknowledge this complexity.

---

---

#### code_vs_comment

**Description:** at_end_of_line() docstring warns against using it for statement parsing, but the method is used in multiple statement parsing contexts

**Affected files:**
- `src/parser.py`

**Details:**
Docstring at lines 176-189 states:
"Note: Most statement parsing should use at_end_of_statement(), not this method.
Using at_end_of_line() in statement parsing can cause bugs where comments are
parsed as part of the statement instead of ending it."

However, at_end_of_line() is used in statement parsing contexts:
- Line 1449: parse_print() uses "while not self.at_end_of_line()"
- Line 1495: parse_print_using() uses "while not self.at_end_of_line()"
- Line 330: collect_def_types() uses "while not self.at_end_of_line()"
- Line 357: parse_def_type_declaration() uses "while not self.at_end_of_line()"

The code does check for REM/REMARK/APOSTROPHE tokens separately in parse_print() (line 1449), which mitigates the issue, but the usage pattern contradicts the docstring's warning.

---

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'end of statement' checking across docstrings

**Affected files:**
- `src/parser.py`

**Details:**
at_end_of_line() docstring (lines 176-189) describes use cases including:
"Line-level parsing in parse_program() where COLON separates statements on same line"

at_end_of_statement() docstring (lines 191-208) states:
"A statement ends at:
- End of line (NEWLINE or EOF)
- Statement separator (COLON) - allows multiple statements per line
- Comment (REM, REMARK, or APOSTROPHE) - everything after is ignored"

The first docstring suggests COLON is relevant to line-level parsing, while the second correctly identifies COLON as a statement separator. This could confuse developers about when to use each method. The at_end_of_line() docstring should clarify that it does NOT check for COLON.

---

---

#### code_vs_comment

**Description:** Comment about comma being optional after file number contradicts MBASIC 5.21 standard

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines 1430-1437 states:
"Note: MBASIC 5.21 typically requires comma (PRINT #1, 'text').
Our parser makes the comma optional for compatibility with BASIC variants
that allow PRINT #1; 'text' or PRINT #1 'text'."

This explicitly documents a deviation from MBASIC 5.21 behavior. However, the file header (line 2) claims this is a "Parser for MBASIC 5.21". If the parser intentionally deviates from MBASIC 5.21 for compatibility reasons, this should be documented more prominently (e.g., in the module docstring) rather than buried in a function comment.

---

---

#### code_vs_comment

**Description:** Comment about MID$ tokenization uses inconsistent terminology

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1893 states: 'Note: The lexer tokenizes 'MID$' in source as TokenType.MID (the $ is part of the keyword, not a separate token). The token type name is 'MID', not 'MID$'.'

This comment is technically correct but potentially confusing because it emphasizes that the token type is 'MID' not 'MID$', yet the actual source keyword is 'MID$'. The comment could be clearer about whether the dollar sign is stripped during lexing or if TokenType.MID represents the full 'MID$' keyword.

---

---

#### code_vs_comment

**Description:** Comment about INPUT semicolon behavior is verbose and potentially confusing

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1115-1122 explains: 'Note: In MBASIC 5.21, the separator after prompt affects "?" display:
- INPUT "Name"; X  displays "Name? " (semicolon AFTER prompt shows '?')
- INPUT "Name", X  displays "Name " (comma AFTER prompt suppresses '?')
Different behavior: INPUT; (semicolon IMMEDIATELY after INPUT keyword, no prompt) suppresses the default '?' prompt entirely (tracked by suppress_question flag above).'

This comment describes two different semicolon behaviors (after prompt vs after INPUT keyword) which could be confusing. The distinction between 'semicolon after prompt' and 'semicolon after INPUT keyword' is important but the comment structure makes it easy to conflate the two cases.

---

---

#### documentation_inconsistency

**Description:** Inconsistent documentation style for statement syntax

**Affected files:**
- `src/parser.py`

**Details:**
Some statement parsers have detailed syntax documentation in docstrings (e.g., parse_input at line ~1095 has extensive syntax examples), while others have minimal documentation (e.g., parse_let at line ~1195 just says 'Parse LET statement'). The parse_showsettings (line ~1365) includes Args: section in docstring, but most other parsers don't follow this pattern. Documentation style should be consistent across all statement parsers.

---

---

#### code_vs_comment

**Description:** parse_call() docstring claims full support for extended syntax but implementation may not handle all cases

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states: "Note: MBASIC 5.21 primarily uses the simple numeric address form, but this parser fully supports both forms for broader compatibility."

The implementation attempts to handle both forms by checking if target is VariableNode with subscripts or FunctionCallNode, but the comment claims "full support" which may be overstated. The parser converts these to CallStatementNode but doesn't validate that the extended syntax is semantically correct for MBASIC 5.21.

---

---

#### code_vs_comment

**Description:** parse_data() docstring mentions line numbers but implementation treats them as unquoted strings

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states: "Line numbers (e.g., DATA 100 200) are treated as part of unquoted strings."

Implementation has:
```
elif tok.type == TokenType.LINE_NUMBER:
    string_parts.append(str(tok.value))
    self.advance()
```

This is consistent, but the docstring could be clearer that LINE_NUMBER tokens are converted to strings and included in the unquoted string value, not treated as numeric data items.

---

---

#### code_vs_comment

**Description:** parse_common() docstring says 'just a marker' but doesn't explain what happens to array indicator

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states: "The empty parentheses () indicate an array variable (all elements shared). This is just a marker - no subscripts are specified or stored."

The implementation consumes the parentheses but stores only the variable name as a string:
```
if self.match(TokenType.LPAREN):
    self.advance()
    if not self.match(TokenType.RPAREN):
        raise ParseError(...)
    self.advance()
variables.append(var_name)
```

The docstring could be clearer that the array indicator is completely discarded and not represented in the AST - there's no way to distinguish between 'COMMON A' and 'COMMON A()' in the resulting CommonStatementNode.

---

---

#### code_vs_comment

**Description:** apply_keyword_case_policy docstring has contradictory guidance about input normalization

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring says: 'Args:
    keyword: The keyword to transform (should be normalized lowercase for consistency, but first_wins policy can handle mixed case by normalizing internally)'

Then says: 'Note: While this function can handle mixed-case input (first_wins policy normalizes to lowercase internally for lookup), callers should normalize to lowercase before calling to ensure consistent behavior with emit_keyword() and avoid case-sensitivity issues in non-first_wins policies.'

This is confusing: it says the keyword 'should be normalized lowercase' but then explains it can handle mixed case. The note clarifies callers should normalize, but the initial 'should be' is weaker than the note's recommendation. Should be consistent about whether normalization is required or optional.

---

---

#### code_vs_comment

**Description:** serialize_expression comment about explicit_type_suffix attribute existence is unclear

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_expression for VariableNode:
'# Only add type suffix if explicitly present in source code (not inferred from DEFINT/DEFSNG/etc)
# Note: explicit_type_suffix attribute may not exist on all VariableNode instances (defaults to False via getattr)'

The comment says the attribute 'may not exist' but the code uses getattr with default False. This is correct code but the comment could be clearer that this is intentional defensive programming, not a bug or inconsistency in the AST design.

---

---

#### documentation_inconsistency

**Description:** Module docstring claims AST is single source of truth but serialize_line implementation suggests token positions are also authoritative

**Affected files:**
- `src/position_serializer.py`

**Details:**
Module docstring says: 'Key principle: AST is the single source of truth for CONTENT (what tokens exist and their values). Original token positions are HINTS for formatting (where to place tokens). When positions conflict with content, content wins and a PositionConflict is recorded.'

But serialize_line comment says: 'AST is the source of truth for content (what tokens exist) - serialize from AST while attempting to preserve original token positions/spacing as formatting hints'

And emit_token implementation shows: 'if expected_column < self.current_column: # CONFLICT: Token expects to be earlier than current position'

This is consistent, but the module docstring could be clearer that position conflicts are tracked but don't prevent serialization - the AST content always wins and positions are adjusted as needed.

---

---

#### Code vs Comment conflict

**Description:** Comment about array indexing convention may be misleading about what it's documenting

**Affected files:**
- `src/resource_limits.py`

**Details:**
In check_array_allocation(), there's a comment:
'# Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21
# We replicate this convention here for accurate size calculation (limit checking must match
# the actual allocation size). The execute_dim() method in interpreter.py uses the same
# convention when creating arrays, ensuring consistency between limit checks and allocation.'

The comment says 'We replicate this convention here' but the code that follows is just calculating size for limit checking, not actually creating the array. The comment might be clearer if it said 'We account for this convention here' or 'We use this convention in our size calculation'. The phrase 'replicate this convention' suggests the code is implementing the indexing behavior, when it's actually just calculating the memory impact of that behavior.

---

---

#### Documentation inconsistency

**Description:** Module docstrings have reciprocal references but use slightly different wording

**Affected files:**
- `src/resource_limits.py`
- `src/resource_locator.py`

**Details:**
resource_limits.py says: 'Note: This is distinct from resource_locator.py which finds package data files.'

resource_locator.py says: 'Note: This is distinct from resource_limits.py which enforces runtime execution limits.'

The first uses 'finds package data files' while the second uses 'enforces runtime execution limits'. For consistency, they should use parallel phrasing, such as:
- resource_limits.py: 'enforces runtime execution limits'
- resource_locator.py: 'locates package data files'

Or both could use 'provides' or 'handles'. The current wording is not wrong but lacks parallelism.

---

---

#### Code vs Documentation inconsistency

**Description:** Docstring says 'Different UIs can create appropriate limit configurations' but only shows three preset functions

**Affected files:**
- `src/resource_limits.py`

**Details:**
The module docstring states: 'Different UIs can create appropriate limit configurations (web UI uses tight limits, local UIs use generous limits).'

The usage examples show:
- create_web_limits() for Web UI
- create_local_limits() for Local UI
- create_unlimited_limits() for Testing/Development

However, the module only provides these three preset functions. If 'different UIs' need to create 'appropriate limit configurations', the documentation should either:
1. Clarify that UIs should use one of these three presets
2. Show how UIs can create custom ResourceLimits instances with custom parameters
3. Explain when/why a UI would need something other than these three presets

The current wording suggests more flexibility than is demonstrated.

---

---

#### code_vs_comment

**Description:** Comment about line=-1 usage is incomplete - doesn't mention debugger sets also use line=-1

**Affected files:**
- `src/runtime.py`

**Details:**
Line 52-56 comment: "Note: line -1 in last_write indicates non-program execution sources:
       1. System/internal variables (ERR%, ERL%) via set_variable_raw() with FakeToken(line=-1)
       2. Debugger/interactive prompt via set_variable() with debugger_set=True and token.line=-1
       Both use line=-1, making them indistinguishable from each other in last_write alone.
       However, line=-1 distinguishes these special sources from normal program execution (line >= 0)."

But the set_variable_raw() docstring (lines 437-451) says:
"The line=-1 marker in last_write indicates system/internal variables.
However, debugger sets also use line=-1 (via debugger_set=True),
making them indistinguishable from system variables in last_write alone."

This is consistent, but the module-level comment could be clearer that both paths are indistinguishable.

---

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for case resolution - 'canonical case' vs 'original case'

**Affected files:**
- `src/runtime.py`

**Details:**
The code uses both terms inconsistently:
- Line 48: "'original_case' field stores the canonical case for display"
- Line 289: "Always update to canonical case"
- Line 336: "canonical_case  # Canonical case for display (field name is historical)"

The field is named 'original_case' but stores 'canonical case'. While comments acknowledge this is historical/misleading, it creates confusion. The term 'canonical case' is used in code/comments but 'original_case' is the field name.

---

---

#### code_vs_comment

**Description:** Comment about DIM tracking rationale may not match actual debugger behavior expectations

**Affected files:**
- `src/runtime.py`

**Details:**
Lines 711-719 comment: "# Note: DIM is tracked as both read and write to provide consistent debugger display.
# While DIM is technically allocation/initialization (write-only operation), setting
# last_read to the DIM location ensures that debuggers/inspectors can show 'Last accessed'
# information even for arrays that have never been explicitly read. Without this, an
# unaccessed array would show no last_read info, which could be confusing. The DIM location
# provides useful context about where the array was created."

This justification assumes debuggers would be confused by null last_read, but it's debatable whether DIM should count as a 'read' operation. This creates semantic confusion - DIM is not actually reading the array, it's allocating it. A debugger could show 'Never read' or 'Allocated at line X' instead.

---

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

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for statement offset indexing explanation

**Affected files:**
- `src/runtime.py`

**Details:**
Multiple docstrings explain 0-based indexing differently:

get_gosub_stack(): "Note: stmt_offset uses 0-based indexing (offset 0 = 1st statement, offset 1 = 2nd statement, etc.)"

set_breakpoint(): "Note: Uses 0-based indexing (offset 0 = 1st statement, offset 1 = 2nd statement, offset 2 = 3rd statement, etc.)"

get_execution_stack() example: "This shows: FOR I at line 100, statement offset 0 (1st statement)..."

While all are technically correct, the varying levels of detail (some show 2 examples, some show 3) create minor inconsistency in documentation style.

---

---

#### Documentation inconsistency

**Description:** Deprecation notice format inconsistency

**Affected files:**
- `src/runtime.py`

**Details:**
get_loop_stack() has structured deprecation info:
"Deprecated since: 2025-10-25 (commit cda25c84)
Will be removed: No earlier than 2026-01-01"

But the 'from_line' field redundancy note in get_execution_stack() mentions backward compatibility without any deprecation timeline or removal plan, despite being redundant.

---

---

#### code_vs_comment

**Description:** SettingsManager.load() docstring mentions format flexibility but implementation details are unclear

**Affected files:**
- `src/settings.py`

**Details:**
load() docstring states:
        """Load settings from backend (file or Redis).

        This method delegates loading to the backend, which returns settings dicts.
        The backend determines the format (flat vs nested) based on what was saved.
        Internal representation is flexible: _get_from_dict() handles both flat keys like
        'editor.auto_number' and nested dicts like {'editor': {'auto_number': True}}.
        Settings loaded from disk remain flat; settings modified via set() become nested; both work.
        """

However, the actual load() implementation just calls:
        self.global_settings = self.backend.load_global()
        self.project_settings = self.backend.load_project()

The comment claims "Settings loaded from disk remain flat; settings modified via set() become nested" but FileSettingsBackend.load_global() returns data.get('settings', {}) which could be either flat or nested depending on what was saved. The comment implies a specific behavior that isn't enforced by the code.

---

---

#### documentation_inconsistency

**Description:** Module docstring lists only two scopes (global and project) but code supports three scopes including FILE

**Affected files:**
- `src/settings.py`

**Details:**
Module docstring at top of settings.py:
"""Settings manager for MBASIC interpreter.

Handles loading, saving, and accessing user settings with scope precedence.
Supports global settings and project settings:
- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)
- Project: .mbasic/settings.json in project directory
"""

But SettingScope enum in settings_definitions.py defines:
    GLOBAL = "global"      # ~/.mbasic/settings.json
    PROJECT = "project"    # .mbasic/settings.json in project dir
    FILE = "file"          # Per-file metadata (RESERVED FOR FUTURE USE - not currently implemented)

The module docstring should mention FILE scope even if it notes it's reserved for future use.

---

---

#### code_vs_comment

**Description:** create_settings_backend() docstring claims fallback behavior without logging/warning is expected, but this may be surprising

**Affected files:**
- `src/settings_backend.py`

**Details:**
create_settings_backend() docstring:
    """Factory function to create appropriate settings backend.

    Args:
        session_id: Session ID for Redis mode (required for Redis backend, but falls back
            to file backend if not provided even when NICEGUI_REDIS_URL is set)
        project_dir: Project directory for file mode

    Returns:
        SettingsBackend instance (Redis if redis_url and session_id both provided, otherwise File)

    Note:
        If NICEGUI_REDIS_URL is set but session_id is None, falls back to FileSettingsBackend
        (this is expected behavior - Redis requires both URL and session_id, so incomplete config
        defaults to file mode without logging/warning).
        If Redis package is not installed or connection fails, falls back to FileSettingsBackend with warning.
    """

The note explicitly states "without logging/warning" for the NICEGUI_REDIS_URL-set-but-no-session_id case, but this silent fallback could be confusing. The code does print warnings for ImportError and connection failures, but not for incomplete config. This inconsistency in warning behavior may be intentional but could surprise users.

---

---

#### documentation_inconsistency

**Description:** SettingScope.FILE comment says 'not currently implemented' but settings.py shows it IS implemented for runtime use

**Affected files:**
- `src/settings_definitions.py`

**Details:**
In settings_definitions.py SettingScope enum:
    FILE = "file"          # Per-file metadata (RESERVED FOR FUTURE USE - not currently implemented)

But in settings.py SettingsManager class:
    def __init__(self, ...):
        ...
        self.file_settings: Dict[str, Any] = {}  # RESERVED FOR FUTURE USE: per-file settings (not persisted)

    def set(self, key: str, value: Any, scope: SettingScope = SettingScope.GLOBAL):
        ...
        elif scope == SettingScope.FILE:
            self.file_settings[key] = value

    def reset_to_defaults(self, scope: SettingScope = SettingScope.GLOBAL):
        ...
        elif scope == SettingScope.FILE:
            self.file_settings = {}

The comment in settings_definitions.py says "not currently implemented" but settings.py shows FILE scope IS implemented for runtime manipulation (just not persisted). The comments should be consistent - either both say "implemented for runtime but not persisted" or both say "reserved for future use".

---

---

#### code_vs_comment

**Description:** Comment says 'tab size is not a meaningful setting for BASIC' but this is debatable for modern editors

**Affected files:**
- `src/settings_definitions.py`

**Details:**
In SETTING_DEFINITIONS dict after editor.auto_number_step:
    # Note: editor.tab_size setting not included - BASIC uses line numbers for program structure,
    # not indentation, so tab size is not a meaningful setting for BASIC source code

    # Note: Line numbers are always shown - they're fundamental to BASIC!
    # editor.show_line_numbers setting not included - makes no sense for BASIC

The comment claims "tab size is not a meaningful setting for BASIC source code" because "BASIC uses line numbers for program structure, not indentation". However, modern BASIC editors often support indentation for readability (even if not semantically meaningful), and users may want to control tab display width. This is a design decision rather than a technical fact, and the comment presents it as absolute truth.

---

---

#### Documentation inconsistency

**Description:** Curses UI has separate Step Line and Step Statement commands, CLI only has STEP

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/curses_keybindings.json`

**Details:**
curses_keybindings.json defines two separate stepping commands:
- "step_line" (Ctrl+K): "Step Line (execute all statements on current line)"
- "step" (Ctrl+T): "Step statement (execute one statement)"

cli_debug.py cmd_step() docstring acknowledges this:
"This implements statement-level stepping similar to the curses UI 'Step Statement' command (Ctrl+T). The curses UI also has a separate 'Step Line' command (Ctrl+K) which is not available in the CLI."

This is documented but represents a feature disparity between UIs that users should be aware of.

---

---

#### Code vs Comment conflict

**Description:** get_additional_keybindings() comment says Ctrl+A is overridden but doesn't explain the override behavior

**Affected files:**
- `src/ui/cli.py`

**Details:**
Comment in get_additional_keybindings() states:
"# Note: Ctrl+A is overridden by MBASIC to trigger edit mode"

However, cli_keybindings.json shows:
"edit": {
  "keys": ["Ctrl+A"],
  "primary": "Ctrl+A",
  "description": "Edit line (last line or Ctrl+A followed by line number)"
}

The comment suggests Ctrl+A is completely overridden, but the keybinding description shows it has MBASIC-specific behavior (edit mode) rather than readline's default (move to start of line). The comment could be clearer about what 'overridden' means in this context.

---

---

#### Documentation inconsistency

**Description:** Readline keybindings documentation split between code comment and JSON file

**Affected files:**
- `src/ui/cli.py`
- `src/ui/cli_keybindings.json`

**Details:**
get_additional_keybindings() function in cli.py documents readline keybindings (Ctrl+E, Ctrl+K, etc.) with explanation:
"NOTE: These keybindings are intentionally NOT in cli_keybindings.json because:
1. They're provided by readline, not the MBASIC keybinding system
2. They're only available when readline is installed (platform-dependent)
3. Users can't customize them through MBASIC settings
4. They follow standard readline/Emacs conventions"

However, this creates a documentation split where some keybindings are in JSON and others are in Python code. Users looking at cli_keybindings.json won't see the full picture of available keybindings.

---

---

#### Code vs Comment conflict

**Description:** Comment claims all shortcuts use constants but footer text is hardcoded

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment in _create_body() states:
"# Note: All shortcuts use constants from keybindings module to ensure
# footer display matches actual key handling in keypress() method"

However, the footer text construction uses key_to_display() function calls but the actual text labels are hardcoded strings:
```python
footer_text = urwid.Text(
    f"↑↓ {key_to_display(ENTER_KEY)}=OK  "
    f"{key_to_display(ESC_KEY)}/{key_to_display(SETTINGS_KEY)}=Cancel  "
    f"{key_to_display(SETTINGS_APPLY_KEY)}=Apply  "
    f"{key_to_display(SETTINGS_RESET_KEY)}=Reset",
    align='center'
)
```

The labels ("OK", "Cancel", "Apply", "Reset") are hardcoded, not from constants. The comment is misleading about the extent of constant usage.

---

---

#### Code vs Comment conflict

**Description:** Comment about stripping 'force_' prefix uses hasattr check for removeprefix but doesn't handle False case

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
In _create_setting_widget() method:
```python
# Strip 'force_' prefix from beginning for cleaner display
display_label = choice.removeprefix('force_') if hasattr(str, 'removeprefix') else (choice[6:] if choice.startswith('force_') else choice)
```

The comment says it strips the prefix, but the code has a complex fallback for Python versions without removeprefix(). The fallback uses choice[6:] which assumes 'force_' is exactly 6 characters, but only applies it if choice.startswith('force_'). This is correct but the comment doesn't explain the version compatibility handling.

---

---

#### Code vs Comment conflict

**Description:** Comment about comparing actual values vs display labels is verbose and could be clearer

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
In _on_reset() method:
```python
# Note: Compares actual value (stored in _actual_value) not display label
# since display labels have 'force_' prefix stripped (see _create_setting_widget)
for rb in widget:
    rb.set_state(rb._actual_value == defn.default)
```

This comment explains the implementation detail but is placed in the reset method rather than where _actual_value is set (_create_setting_widget). The comment would be more useful near the line:
```python
rb._actual_value = choice
```
where the actual value is stored.

---

---

#### code_vs_comment

**Description:** Comment about auto-numbering limit contradicts actual behavior for manual entry

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress() method around line 500:
"# Note: Auto-numbering stops at 99999 for display consistency, but manual
# entry of higher line numbers is not prevented by _parse_line_number().
# This is intentional - auto-numbering uses conservative limits while
# manual entry allows flexibility."

However, the code checks:
"if next_num >= 99999 or attempts > 10:"

This suggests auto-numbering stops at 99999, but the comment claims manual entry isn't prevented. The _parse_line_number() method has no such limit check visible in the provided code, so the comment appears accurate but could be clearer about where this distinction is enforced.

---

---

#### code_vs_comment

**Description:** Comment about line 0 handling is unclear about intentionality

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_syntax_errors() method:
"# Note: line_number > 0 check silently skips line 0 if present (not a valid
# BASIC line number). This avoids setting status for malformed lines.
# Consistent with _check_line_syntax which treats all empty lines as valid"

The comment says this is 'consistent with _check_line_syntax', but _check_line_syntax() doesn't have any line_number > 0 check - it only checks if code_text is empty. The consistency claim appears incorrect.

---

---

#### documentation_inconsistency

**Description:** Incomplete docstring for _sort_and_position_line truncated mid-sentence

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The docstring for _sort_and_position_line() is incomplete:
"target_column: Column to position cursor at (default: 7). Since line numbers have
                          variable width, this is approximate. The cursor will be positioned"

The sentence ends abruptly without explaining where the cursor will be positioned.

---

---

#### code_vs_comment

**Description:** Comment says immediate_io is recreated in start() but the code shows it's created in both __init__ and start()

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~260 says:
# 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands
#    Created here temporarily, then RECREATED in start() with fresh instance each time

But the code shows:
1. In __init__ (line ~262): immediate_io = OutputCapturingIOHandler()
2. In start() (line ~340): immediate_io = OutputCapturingIOHandler()

The comment implies the first creation is temporary/throwaway, but doesn't explain why it's created twice or what happens to the first instance.

---

---

#### code_vs_comment

**Description:** Comment says 'Toolbar removed from UI layout' but there's no evidence a toolbar ever existed in this code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~390 says:
# Toolbar removed from UI layout - use Ctrl+U interactive menu bar instead for keyboard navigation

This suggests a toolbar was previously in the code and removed, but:
1. No commented-out toolbar code is visible
2. No self.toolbar variable exists
3. The comment may be outdated or referring to a different version

---

---

#### code_vs_comment

**Description:** Comment says immediate mode status 'remains disabled' during execution, but doesn't explain when/how it gets re-enabled

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple comments say:
'(Immediate mode status remains disabled during execution - output shows in output window)'

Appears at lines ~680, ~740, ~780. However:
1. The mechanism for disabling immediate mode is not shown
2. The mechanism for re-enabling it is not clear
3. The relationship between execution state and immediate mode availability is not documented
4. _update_immediate_status() is called but its implementation is not shown

---

---

#### code_vs_comment

**Description:** Comment about main widget storage strategy differs between methods but implementation is consistent

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_help/_show_keymap/_show_settings (around lines 800-900), comments state:
"Main widget retrieval: Use self.base_widget (stored at UI creation time in __init__)
rather than self.loop.widget (which reflects the current widget and might be a menu
or other overlay)."

In _activate_menu (around line 950), comment states:
"Main widget storage: Unlike _show_help/_show_keymap/_show_settings which close
existing overlays first (and thus can use self.base_widget directly), this method
extracts base_widget from self.loop.widget to unwrap any existing overlay."

The comments accurately describe different strategies for different use cases, but the distinction could be confusing without understanding the full context.

---

---

#### code_vs_comment

**Description:** Comment about immediate mode status updates is inconsistent across error handling paths

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple locations have comments about when immediate status is updated:

Line ~1170: "Don't update immediate status here - error is displayed in output"
Line ~1200: "Don't update immediate status on exception - error is in output"
Line ~1230: "Immediate mode status remains disabled during execution - program output shows in output window"
Line ~1280: "Update immediate status after error so user can continue"
Line ~1310: "Update immediate status after error so user can continue"

The pattern shows immediate status is NOT updated during setup/parse errors, but IS updated after runtime errors. Comments are consistent with implementation but the reasoning could be clearer.

---

---

#### code_vs_comment

**Description:** Comment about statement-level precision for GOSUB uses confusing terminology

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_stack_window (line ~1460):
"# Show statement-level precision for GOSUB return address
# return_stmt is statement offset (0-based index): 0 = first statement, 1 = second, etc."

The comment correctly describes the implementation, but the term 'statement offset' might be confused with byte offset. The code correctly formats it as 'line.statement' notation.

---

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'Immediate mode status remains disabled during execution' but there's no code setting status to disabled

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1633 says:
# Immediate mode status remains disabled during execution - program output shows in output window

But the code just sets:
self.running = True

There's no explicit call to disable immediate mode status. However, _update_immediate_status() checks can_execute_immediate() which likely returns False when running=True, so the status is implicitly disabled. The comment is describing the effect, not a direct action.

---

---

#### code_vs_comment

**Description:** Comment in _get_input_for_interpreter describes behavior 'similar to STOP' but STOP is a program statement, not a UI action

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1050 says:
# The behavior is similar to STOP: user can examine variables and continue with CONT.

This is describing ESC during INPUT. The comparison to STOP statement is accurate - both set runtime.stopped=True and allow CONT to resume. This is not an inconsistency.

---

---

#### code_vs_comment_conflict

**Description:** Comment describes _expand_kbd parameter format but doesn't mention the actual implementation handles both formats in the same parameter

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at lines ~107-115 states:
"Args:
    key_name: Name of key action, optionally with UI specifier.
             Formats:
             - 'action' - searches current UI (e.g., 'help', 'save', 'run')
             - 'action:ui' - searches specific UI (e.g., 'save:curses', 'run:tk')"

But the docstring example at lines ~117-119 shows:
"Example:
    _expand_kbd('help') searches current UI for action 'help'
    _expand_kbd('save:curses') searches Curses UI for action 'save'"

The format description uses 'action:ui' but the example shows 'save:curses' which reverses the order. The code at line ~126 shows:
if ':' in key_name:
    action, ui = key_name.split(':', 1)

So the format is actually 'action:ui' as stated, but the example 'save:curses' makes it look like 'action:ui_name' where 'save' is the action and 'curses' is the UI, which is correct. This is actually consistent, just potentially confusing.

---

---

#### documentation_inconsistency

**Description:** Docstring example format inconsistency in macro syntax

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Module docstring at lines ~7-11 shows:
"Examples:
  {{kbd:help}} → looks up 'help' action in current UI's keybindings and returns
                  the primary keybinding for that action
  {{kbd:save:curses}} → looks up 'save' action in Curses UI specifically
  {{version}} → MBASIC version string"

The example {{kbd:save:curses}} suggests a three-part format (macro:action:ui), but the actual implementation and _expand_kbd docstring show the format is {{kbd:action}} or {{kbd:action:ui}} where the macro name is 'kbd' and the argument is 'action' or 'action:ui'.

The example should be {{kbd:save:curses}} which is parsed as macro='kbd', arg='save:curses', then arg is split into action='save', ui='curses'. The example is correct but could be clearer about the parsing.

---

---

#### code_vs_comment_conflict

**Description:** Comment describes link format matching but implementation uses different regex pattern than described

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at lines ~234-240 states:
"Links are marked with [text] or [text](url) in the rendered output. This method finds ALL such patterns for display/navigation using regex r'\\[([^\\]]+)\\](?:\\([^)]+\\))?', which matches both formats. The renderer's links list is used for target mapping when following links."

The regex pattern in the comment is escaped for docstring (\\[ becomes \[), but the actual pattern at line ~253 is:
link_pattern = r'\[([^\]]+)\](?:\([^)]+\))?'

The comment's regex representation is correct for a docstring but could be confusing. The actual pattern is correct and matches the description.

---

---

#### Code vs Comment conflict

**Description:** Comment says CONTINUE_KEY is for 'Go to line' in editor and 'Continue execution (Go)' in debugger, but JSON key is 'goto_line' which doesn't clearly indicate dual purpose

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

The comment explains dual purpose but this may not be documented in the JSON schema or help text.

---

---

#### Code vs Comment conflict

**Description:** Comment says STOP_KEY is 'Shown in debugger context in the Debugger category' implying it's NOT in KEYBINDINGS_BY_CATEGORY, but it IS present in the 'Debugger (when program running)' category

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line 221 comment:
# - STOP_KEY (Ctrl+X) - Shown in debugger context in the Debugger category

But line 245 in KEYBINDINGS_BY_CATEGORY:
'Debugger (when program running)': [
    ...
    (key_to_display(STOP_KEY), 'Stop execution (eXit)'),
    ...
]

The comment is misleading - STOP_KEY IS included in KEYBINDINGS_BY_CATEGORY.

---

---

#### Code inconsistency

**Description:** Inconsistent handling of JSON fallbacks - some keys have fallback values, others don't

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Most keys have fallback values:
RUN_KEY = _ctrl_key_to_urwid(_run_from_json) if _run_from_json else 'ctrl r'

But some don't:
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

This is inconsistent - either all should have fallbacks or none should. The pattern suggests all keys should have sensible defaults if JSON is missing.

---

---

#### Code vs Documentation inconsistency

**Description:** keymap_widget.py converts 'Ctrl+' to '^' notation but keybindings.py key_to_display() already does this conversion, creating redundant logic

**Affected files:**
- `src/ui/keybindings.py`
- `src/ui/keymap_widget.py`

**Details:**
In keybindings.py lines 107-123, key_to_display() converts:
'ctrl a' -> '^A'
'shift ctrl b' -> '^Shift+B'

In keymap_widget.py lines 10-23, _format_key_display() converts:
'Ctrl+F' -> '^F'
'Shift+Ctrl+V' -> 'Shift+^V'

These functions handle different input formats (urwid keys vs Ctrl+ notation) but the keymap_widget function seems unnecessary since key_to_display() is already called in KEYBINDINGS_BY_CATEGORY construction.

---

---

#### Documentation inconsistency

**Description:** Module docstring says keybindings are loaded from curses_keybindings.json but doesn't mention validation rules or fallback behavior

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 1-11:
"""
Keyboard binding definitions for MBASIC Curses UI.

This module loads keybindings from curses_keybindings.json and provides them
in the format expected by the Curses UI (urwid key names, character codes, display names).

This ensures consistency between the JSON config, the UI behavior, and the documentation.

File location: curses_keybindings.json is located in the src/ui/ directory (same directory as this module).
If you need to modify keybindings, edit that JSON file rather than changing constants here.
"""

Docstring doesn't mention:
1. Validation rules (Ctrl+A through Ctrl+Z only)
2. Duplicate key detection
3. Fallback values when JSON keys are missing
4. That validation happens at module load time

---

---

#### Code inconsistency

**Description:** Hardcoded keys (MENU_KEY, CLEAR_BREAKPOINTS_KEY, DELETE_LINE_KEY, etc.) are not loaded from JSON despite module claiming all keybindings come from JSON

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line 124:
MENU_KEY = 'ctrl u'

Line 169:
CLEAR_BREAKPOINTS_KEY = 'ctrl shift b'

Line 172:
DELETE_LINE_KEY = 'ctrl d'

Line 175:
RENUMBER_KEY = 'ctrl e'

Line 178:
INSERT_LINE_KEY = 'ctrl y'

Line 193:
STOP_KEY = 'ctrl x'

Line 196:
SETTINGS_KEY = 'ctrl p'

Line 199:
MAXIMIZE_OUTPUT_KEY = 'ctrl shift m'

These are hardcoded but module docstring says 'If you need to modify keybindings, edit that JSON file rather than changing constants here.'

---

---

#### Code duplication with inconsistency risk

**Description:** Table formatting logic may be duplicated in markdown_renderer.py

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/markdown_renderer.py`

**Details:**
In _format_table_row() method (line 677):
# Note: This implementation may be duplicated in src/ui/markdown_renderer.py.
# If both implementations exist and changes are needed to table formatting logic,
# consider extracting to a shared utility module to maintain consistency.

The comment suggests potential duplication but cannot be verified without seeing markdown_renderer.py. If duplication exists, changes to table formatting in one location may not be reflected in the other.

---

---

#### Code vs Comment conflict

**Description:** Comment about link tag prefixes may be incomplete or misleading

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In _create_context_menu() method (line 598):
# Note: Both "link_" (from _render_line_with_links) and "result_link_"
# (from _execute_search) prefixes are checked. Both types are stored
# identically in self.link_urls, but the prefixes distinguish their origin.

However, in _render_line_with_links() (line 211), links are tagged with "link_{counter}" format, and in _execute_search() (line 437), links are tagged with "result_link_{counter}" format. The comment correctly identifies both prefixes, but the actual code in _render_line_with_links() creates tags like "link_1", "link_2", etc., while the comment at line 598 suggests checking for "link_" prefix. The implementation is correct, but the comment could be clearer about the full tag format including the counter suffix.

---

---

#### Code vs Comment conflict

**Description:** Comment about tk_popup() dismissal behavior may be misleading about explicit bindings

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In _create_context_menu() method (line 612):
# Note: tk_popup() handles menu dismissal automatically (ESC key,
# clicks outside menu, selecting items). Explicit bindings for
# FocusOut/Escape are not needed and may not fire reliably since
# Menu widgets have their own event handling for dismissal.

This comment explains why explicit dismissal bindings are not needed, but it's placed after the menu.tk_popup() call and before menu.grab_release(). The comment is informative but could be misinterpreted as explaining why grab_release() is needed, when it's actually explaining why other bindings are NOT needed. The placement and wording could be clearer.

---

---

#### Code vs Comment conflict

**Description:** Comment about widget storage contradicts actual implementation

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In _get_current_widget_values() method (line 207):
# All entries in self.widgets dict are tk.Variable instances (BooleanVar, StringVar, IntVar),
# not the actual widget objects (Checkbutton, Spinbox, Entry, Combobox).
# The variables are associated with widgets via textvariable/variable parameters.

This comment is accurate and matches the implementation in _create_setting_widget() (lines 157-181) where tk.Variable instances are stored in self.widgets, not the widget objects themselves. However, the method name '_get_current_widget_values' is slightly misleading since it's getting values from variables, not widgets. This is a minor naming inconsistency rather than a code/comment conflict.

---

---

#### Code vs Comment conflict

**Description:** Comment about modal behavior may be misleading about blocking

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In __init__() method (line 44):
# Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())

The comment clarifies that grab_set() makes the dialog modal but doesn't block code execution because wait_window() is not called. This is accurate, but the phrasing 'prevents interaction with parent' might be misunderstood as blocking, when it only prevents UI interaction while allowing code to continue. The comment is technically correct but could be clearer about the distinction between UI modality and code blocking.

---

---

#### Code vs Comment conflict

**Description:** Comment about help display mechanism is misleading

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In _create_setting_widget() method (line 186):
# Show short help as inline label (not a hover tooltip, just a gray label)

The comment clarifies that short help text is displayed as a static label, not a tooltip. However, the comment seems defensive, suggesting there might have been confusion or a previous implementation using tooltips. The comment is accurate but its tone suggests potential past inconsistency or confusion about the intended behavior.

---

---

#### code_vs_comment

**Description:** Docstring describes 3-pane layout with specific weights (3:2:1) but implementation uses ttk.PanedWindow which doesn't use those exact weight values

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring lines ~48-52:
'- 3-pane vertical layout (weights: 3:2:1 = total 6 units):
  * Editor with line numbers (top, ~50% = 3/6 - weight=3)
  * Output pane (middle, ~33% = 2/6 - weight=2)
    - Contains INPUT row (shown/hidden dynamically for INPUT statements)
  * Immediate mode input line (bottom, ~17% = 1/6 - weight=1)'

Implementation lines ~177-195:
paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
paned.add(editor_frame, weight=3)
paned.add(output_frame, weight=2)
paned.add(immediate_frame, weight=1)

The weights are correct, but the description is overly specific about percentages which may not match actual rendering.

---

---

#### documentation_inconsistency

**Description:** Docstring example shows TkIOHandler created without backend reference, but actual initialization pattern may differ

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines ~56-63 in class docstring:
Usage:
    from src.ui.tk_ui import TkBackend, TkIOHandler
    from src.editing.manager import ProgramManager

    io = TkIOHandler()  # TkIOHandler created without backend reference initially
    def_type_map = {}  # Type suffix defaults for variables (DEFINT, DEFSNG, etc.)
    program = ProgramManager(def_type_map)
    backend = TkBackend(io, program)
    backend.start()  # Runs Tk mainloop until window closed

The comment 'TkIOHandler created without backend reference initially' suggests a two-phase initialization, but the actual TkIOHandler class is not shown in the provided code to verify this pattern.

---

---

#### code_vs_comment

**Description:** Comment about toolbar simplification references features in menus, but the comment placement suggests removed buttons

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines ~509-514:
# Note: Toolbar has been simplified to show only essential execution controls.
# Additional features are accessible via menus:
# - List Program → Run > List Program
# - New Program (clear) → File > New
# - Clear Output → Run > Clear Output

This comment appears after toolbar creation but doesn't clearly indicate what was removed or when. It reads like a historical note that may be outdated.

---

---

#### code_vs_comment

**Description:** Comment describes ARROW_CLICK_WIDTH as 'typical arrow icon width for standard Tkinter theme' but value is hardcoded

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1107:
ARROW_CLICK_WIDTH = 20  # Width of clickable arrow area in pixels (typical arrow icon width for standard Tkinter theme)

The comment suggests this is based on theme standards, but the hardcoded value may not work correctly across different themes or platforms. This could be a design issue rather than just a comment issue.

---

---

#### code_vs_comment

**Description:** Comment about validation timing is incomplete regarding when validation occurs

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1230:
Comment says: '# Note: This method is called:\n# - With 100ms delay after cursor movement/clicks (to avoid excessive validation during rapid editing)\n# - Immediately when focus leaves editor (to ensure validation before switching windows)'

However, looking at the code, validation is also called:
- In _on_enter_key after Enter is pressed (line ~1380: 'self.root.after(100, self._validate_editor_syntax)')
- After mouse clicks (line ~1360: 'self.root.after(100, self._validate_editor_syntax)')

The comment should mention all trigger points or be more general.

---

---

#### code_vs_comment

**Description:** Comment about when _remove_blank_lines is called is incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines method around line 1310:
Comment says: 'Currently called only from _on_enter_key (after each Enter key press), not\nafter pasting or other modifications.'

This comment describes current behavior but doesn't explain WHY it's only called from _on_enter_key. Is this intentional design (blank lines should only be removed on Enter) or a limitation (should be called after paste but isn't yet)? The comment leaves this ambiguous.

---

---

#### code_vs_comment

**Description:** Comment about clearing yellow highlight doesn't explain restoration timing

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_mouse_click method around line 1355:
Comment says: '# Clear yellow statement highlight when clicking (allows text selection to be visible).\n# The highlight is restored when execution resumes or when stepping to the next statement.'

The comment mentions restoration happens 'when execution resumes or when stepping', but doesn't clarify what happens if the user clicks while paused and then continues without stepping. The restoration timing could be more precisely documented.

---

---

#### code_vs_comment

**Description:** Comment about Tk Text widget design is overly detailed for context

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines method around line 1305:
Comment says: 'Removes blank lines to keep program clean, but preserves the final\nline. Tk Text widgets always end with a newline character (Tk design -\ntext content ends at last newline, so there\'s always an empty final line).'

The detailed explanation about Tk Text widget design (text content ending at last newline) is more implementation detail than necessary for understanding the method's purpose. This could be simplified to just state that the final line is preserved.

---

---

#### code_vs_comment

**Description:** Comment describes backspace/delete as control characters but code treats them specially

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1068 states: "Note: These are control characters (ASCII 8 and 127) but we need them for text editing. Other control characters are blocked by validation later."

This is accurate but potentially confusing because the code explicitly allows these before the control character validation, making them exceptions rather than control characters that pass validation.

---

---

#### code_vs_comment

**Description:** Comment about cursor positioning after smart insert may be incorrect

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1335 states: "Position cursor at the end of the line number (ready to type code)"

Code sets cursor to: f'{insert_index}.{col_pos}' where col_pos = len(f'{insert_num} ')

This positions cursor AFTER the space following the line number, which is correct for typing code. However, the comment says "at the end of the line number" which technically would be before the space. Minor wording issue.

---

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for execution state

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
The code uses multiple terms for similar states:
- 'running' (boolean flag)
- 'halted' (runtime.halted)
- 'stopped' (runtime.stopped)
- 'paused_at_breakpoint' (boolean flag)

These states overlap and their exact relationships aren't clearly documented. For example, can something be both 'halted' and 'stopped'? When is 'paused_at_breakpoint' true vs 'halted' true?

---

---

#### code_vs_comment

**Description:** Comment about CLS behavior may not match user expectations

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In clear_screen() method at line 1520:
"Design decision: GUI output is persistent for review. Users can manually clear output via Run > Clear Output menu if desired. CLS command is ignored to preserve output history during program execution."

This documents that CLS is intentionally ignored, but users familiar with BASIC may expect CLS to clear the screen. This design decision contradicts traditional BASIC behavior and may surprise users.

---

---

#### code_vs_comment_conflict

**Description:** The _parse_line_number() docstring and inline comments provide extensive explanation of valid/invalid line number formats, but the class docstring's 'Automatic blank line removal' section doesn't mention that blank lines with valid BASIC line numbers (e.g., '10' alone) are NOT removed, only completely blank lines.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_parse_line_number() comment: 'Valid examples:
  "10 PRINT" - line number 10 followed by whitespace, then statement
  "10" - standalone line number (no statement, just the line number)'

_on_cursor_move() code: 'if line_text.strip() == '': # Delete the blank line'

A line containing only '10' would have line_text.strip() == '10', not '', so it would NOT be deleted. However, the class docstring says 'When cursor moves away from a blank line, that line is automatically deleted' without clarifying that lines with only a BASIC line number are preserved.

---

---

#### code_vs_comment_conflict

**Description:** The _redraw() docstring says 'See _parse_line_number() for the regex-based extraction logic that validates line number format (requires whitespace or end-of-string after the number)' but this validation detail is more of an implementation note than a description of what _redraw() does.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_redraw() docstring: 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas). See _parse_line_number() for the regex-based extraction logic that validates line number format (requires whitespace or end-of-string after the number).'

This note about regex validation requirements belongs in _parse_line_number()'s docstring (where it already exists in detail), not in _redraw()'s docstring. The _redraw() docstring should focus on what _redraw() does.

---

---

#### code_vs_comment_conflict

**Description:** The _on_status_click() method uses the same regex pattern as _parse_line_number() (as noted in its comment 'Use same pattern as _parse_line_number() for consistency') but duplicates the regex instead of calling _parse_line_number(). This creates maintenance risk if the pattern changes.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_on_status_click() code:
'line_text = line_text.strip()
match = re.match(r'^(\d+)(?:\s|$)', line_text)
if match:
    line_num = int(match.group(1))'

_parse_line_number() code:
'line_text = line_text.strip()
match = re.match(r'^(\d+)(?:\s|$)', line_text)
if match:
    return int(match.group(1))'

The comment acknowledges using 'same pattern' but the code duplicates it instead of calling the existing method. Should call: 'line_num = self._parse_line_number(line_text)'

---

---

#### code_vs_comment

**Description:** Comment in serialize_variable() mentions explicit_type_suffix attribute behavior that may not be consistently set

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Note: explicit_type_suffix is not always set (depends on parser implementation),
so getattr defaults to False if missing, preventing incorrect suffix output"

This comment acknowledges parser implementation dependency but doesn't clarify when explicit_type_suffix IS set vs when it's missing. The code uses getattr(var, 'explicit_type_suffix', False) to handle missing attribute, but the comment suggests this is a workaround for inconsistent parser behavior rather than intentional design.

---

---

#### documentation_inconsistency

**Description:** Module docstring claims no UI-framework dependencies but doesn't mention AST node dependencies

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Module docstring states: "No UI-framework dependencies (Tk, curses, web)
are allowed. Standard library modules (os, glob, re) and core interpreter
modules (runtime, parser, AST nodes) are permitted."

The docstring explicitly permits "AST nodes" but many functions (serialize_line, serialize_statement, serialize_expression, etc.) have tight coupling to specific AST node types and their attributes. This creates an implicit dependency on AST node structure that isn't clearly documented as a constraint.

---

---

#### code_vs_documentation

**Description:** update_line_references() docstring describes two-pattern approach but implementation details differ from description

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring states: "Two-pattern approach (applied sequentially in a single pass):
Pattern 1: Match keyword + first line number (GOTO/GOSUB/THEN/ELSE/ON...GOTO/ON...GOSUB)
Pattern 2: Match comma-separated line numbers (for ON...GOTO/GOSUB lists)"

The description says "single pass" but the code actually applies two separate regex substitutions sequentially (pattern.sub() then comma_pattern.sub()), which is technically two passes over the string. The docstring's "single pass" claim is misleading.

---

---

#### code_vs_comment

**Description:** Comment in serialize_statement() for RemarkStatementNode mentions REMARK conversion but doesn't explain when it occurs

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Note: REMARK is converted to REM during parsing, not here"

This comment references a parsing behavior (REMARK -> REM conversion) but doesn't clarify whether the AST will ever contain comment_type='REMARK' or if it's always normalized to 'REM' by the parser. The code only checks for 'APOSTROPHE' vs else (defaulting to REM), suggesting REMARK is already converted, but the comment doesn't make this clear.

---

---

#### code_vs_documentation

**Description:** cycle_sort_mode() docstring claims to match Tk UI implementation but no verification of actual Tk UI behavior

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Docstring states: "The cycle order is: accessed -> written -> read -> name -> (back to accessed)
This matches the Tk UI implementation."

The comment claims this matches Tk UI but there's no reference to where in the Tk UI this is verified, and no mechanism to ensure they stay in sync if one changes. This creates a potential for drift between implementations.

---

---

#### code_vs_comment

**Description:** serialize_expression() docstring describes ERR/ERL special handling but doesn't explain why they're special

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring states: "Note:
    ERR and ERL are special system variables that are serialized without
    parentheses (e.g., 'ERR' not 'ERR()') when they appear as FunctionCallNode
    with no arguments, matching MBASIC 5.21 syntax."

The note explains WHAT is done (no parentheses) and WHY (matching MBASIC 5.21), but doesn't explain WHY ERR/ERL appear as FunctionCallNode in the AST if they're actually system variables. This suggests a parser design decision that isn't documented here.

---

---

#### Documentation inconsistency

**Description:** Docstring example in cmd_list() shows implementation pattern but the actual implementation is already complete, not a stub

**Affected files:**
- `src/ui/visual.py`

**Details:**
Docstring says:
        """Execute LIST command - list program lines.

        Example:
            lines = self.program.get_lines()
            for line_num, line_text in lines:
                self.io.output(line_text)
        """

But the method body already contains this exact implementation:
        lines = self.program.get_lines()
        for line_num, line_text in lines:
            self.io.output(line_text)

The docstring presents it as an 'Example' to implement, but it's already implemented.

---

---

#### Code vs Comment conflict

**Description:** Comment in _internal_change_handler says 'CodeMirror sends new value in e.args attribute' but this is implementation detail that may not be accurate

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Comment in __init__ method:
        def _internal_change_handler(e):
            self._value = e.args  # CodeMirror sends new value in e.args attribute
            if on_change:
                on_change(e)

The comment claims CodeMirror sends the value in e.args, but this is actually a NiceGUI event handling detail, not a CodeMirror behavior. The comment could be misleading about where this behavior originates.

---

---

#### Code vs Documentation inconsistency

**Description:** value property getter has defensive code for dict/None cases but this behavior is not documented in the property docstring

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Property implementation:
    @property
    def value(self) -> str:
        """Get current editor content.

        Always returns a string, even if internal value is dict or None.
        """
        if isinstance(self._value, dict):
            # Sometimes event args are dict - return empty string
            return ''
        return self._value or ''

The docstring mentions it 'Always returns a string, even if internal value is dict or None' but doesn't explain WHY the internal value might be a dict (event args issue) or when this would occur. The inline comment provides more context than the docstring.

---

---

#### code_vs_comment

**Description:** Comment references _enable_inline_input() method that is not visible in the provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~70 references:
# by _enable_inline_input() in the NiceGUIBackend class.

This method is not shown in the provided code snippet (part 1 of nicegui_backend.py). Either the method exists in part 2 (not shown), or the comment is outdated.

---

---

#### code_vs_comment

**Description:** Comment says prompt display is handled by _get_input via _enable_inline_input, but implementation details not visible

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~60-62:
# Don't print prompt here - the input_callback (backend._get_input) handles
# prompt display via _enable_inline_input() method in the NiceGUIBackend class

The _get_input method is not shown in the provided code, so cannot verify if this is accurate or outdated.

---

---

#### documentation_inconsistency

**Description:** Multiple references to MBASIC version '5.21' as language version vs implementation version

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
The code has multiple comments clarifying version numbers:
- Line ~438: # Note: '5.21' is the MBASIC language version (intentionally hardcoded)
- Line ~896: # Use CodeMirror 5 (legacy) - simple script tags, no ES6 modules
- Line ~920: ui.page_title('MBASIC 5.21 - Web IDE')
- Line ~1000: self.output_text = f'MBASIC 5.21 Web IDE - {VERSION}\n'

This is actually consistent, but the repeated clarifications suggest past confusion. The pattern is correct: '5.21' is the BASIC language version, VERSION is the implementation version.

---

---

#### code_vs_comment

**Description:** Comment about sort state matching Tk UI defaults references external file

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~159-160:
# Sort state (matches Tk UI defaults: see sort_mode and sort_reverse in src/ui/tk_ui.py)
self.sort_mode = 'accessed'  # Current sort mode
self.sort_reverse = True  # Sort direction

This references src/ui/tk_ui.py which is not provided. Cannot verify if the defaults actually match.

---

---

#### code_vs_comment

**Description:** Comment claims _on_editor_change method is 'defined later in this class', but the actual location is not visible in the provided code excerpt.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1680 states:
"# The _on_editor_change method handles:
# - Removing blank lines
# - Auto-numbering
# - Placeholder clearing
# (Note: Method defined later in this class - search for 'def _on_editor_change')"

This is informational and not necessarily an inconsistency, but if the method is not actually defined in the class, this would be misleading.

---

---

#### code_vs_comment

**Description:** Comment claims breakpoints are stored in runtime.breakpoints and can be 'plain integers' for legacy compatibility, but the implementation exclusively uses PC objects in _toggle_breakpoint.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment in _update_breakpoint_display (around line 1570) states:
"# Note: self.runtime.breakpoints is a set that can contain:
#   - PC objects (statement-level breakpoints, created by _toggle_breakpoint)
#   - Plain integers (line-level breakpoints, legacy/compatibility)
# This implementation uses PC objects exclusively, but handles both for robustness."

However, examining _toggle_breakpoint and _do_toggle_breakpoint, all breakpoints are created as PC objects with stmt_offset. The code does handle both types in _update_breakpoint_display, but the comment suggests plain integers might be added elsewhere, which is not evident in the provided code.

---

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for step commands - comments reference 'Ctrl+T/Ctrl+K' but menu items are 'Step Line' and 'Step Statement' without keyboard shortcuts shown.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1845 mentions:
"# Note: Step commands (Ctrl+T/Ctrl+K) DO clear output for clarity when debugging"

But in _create_menu (around line 1780), the Debug menu shows:
"ui.menu_item('Step Line', on_click=self._menu_step_line)
ui.menu_item('Step Statement', on_click=self._menu_step_stmt)"

No keyboard shortcuts are registered or displayed in the UI for these commands, making the Ctrl+T/Ctrl+K reference potentially confusing or outdated.

---

---

#### code_vs_comment

**Description:** Docstring for _sync_program_to_runtime describes PC handling as 'conditional preservation' but implementation is actually 'conditional reset'

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says:
"PC handling (conditional preservation):
- If exec_timer is active (execution in progress): Preserves PC and halted state,
  allowing program to resume from current position after rebuild.
- Otherwise (no active execution): Resets PC to halted state, preventing
  unexpected execution when LIST/edit commands modify the program."

The framing as 'conditional preservation' is misleading - it's actually 'conditional reset'. When timer is active, PC is preserved (no action). When timer is inactive, PC is reset. The primary action is resetting, not preserving.

---

---

#### code_vs_comment

**Description:** Comment about paste detection threshold claims it's arbitrary but provides specific reasoning

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _on_editor_change() method:

Comment says: "# The 5-char threshold is arbitrary - balances detecting small pastes while avoiding
# false positives from rapid typing (e.g., typing 'PRINT' quickly = 5 chars but not a paste)."

The comment claims the threshold is 'arbitrary' but then provides specific reasoning about balancing paste detection vs rapid typing. If there's reasoning, it's not arbitrary - it's a heuristic with justification.

---

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'Don't create temporary ones!' but doesn't explain why or what the alternative was

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _execute_immediate() method:

Comment says: "# Use the session's single interpreter and runtime
# Don't create temporary ones!"

The emphatic 'Don't create temporary ones!' suggests this was a previous bug or design issue, but there's no context about why temporary instances would be problematic or what issues they caused. This makes the comment less useful for future maintainers.

---

---

#### documentation_inconsistency

**Description:** Architecture comment about not auto-syncing editor from AST appears in _execute_immediate but doesn't explain what triggers the sync or when it's appropriate

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says: "# Architecture: We do NOT auto-sync editor from AST after immediate commands.
# This preserves one-way data flow (editor → AST → execution) and prevents
# losing user's formatting/comments. Commands that modify code (like RENUM)
# update the editor text directly."

This architectural decision is documented inline but not in a centralized architecture document. The comment also mentions RENUM as an example but doesn't list other commands that modify editor text directly, making it incomplete.

---

---

#### code_vs_comment

**Description:** Comment in _check_auto_number says 'Don't auto-number if content hasn't changed' but code checks exact equality which may miss semantic equivalence

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _check_auto_number() method:

Comment says: "# Don't auto-number if content hasn't changed
if current_text == self.last_edited_line_text:
    return"

The comment describes intent (content hasn't changed) but the code checks exact string equality. This could miss cases where content is semantically unchanged but has different whitespace or formatting. The comment should be more precise about checking exact text equality.

---

---

#### code_vs_comment

**Description:** Comment in _sync_program_from_editor uses sys.stderr.write but doesn't import sys at function level

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _sync_program_from_editor() method:

Comment says: "# Using sys.stderr.write directly to ensure output even if logging fails.
sys.stderr.write(f'Warning: Failed to sync program from editor: {e}\n')
sys.stderr.flush()"

The code uses sys.stderr but doesn't show an import statement. While sys may be imported at module level, the comment's emphasis on 'directly' suggests this is critical error handling, so the import should be visible or documented.

---

---

#### documentation_inconsistency

**Description:** Comment about Redis configuration mentions 'load-balanced instances' but there's no documentation about load balancing setup or requirements

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~478:
    if redis_url:
        sys.stderr.write(f"Redis storage enabled: {redis_url}\n")
        sys.stderr.write("Session state will be shared across load-balanced instances\n\n")

This implies load balancing is a supported configuration, but there's no documentation about:
- How to set up load balancing
- What load balancer to use
- Any special configuration needed
- Whether sticky sessions are required or not

---

---

#### code_inconsistency

**Description:** Default storage secret 'dev-default-change-in-production' is used when MBASIC_STORAGE_SECRET is not set, but there's no warning logged about using an insecure default in production

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~489:
    ui.run(
        title='MBASIC 5.21 - Web IDE',
        port=port,
        storage_secret=os.environ.get('MBASIC_STORAGE_SECRET', 'dev-default-change-in-production'),
        reload=False,
        show=True
    )

The default value name suggests it should be changed in production, but there's no runtime warning if the default is being used. This could be a security issue.

---

---

#### documentation_inconsistency

**Description:** Keyboard shortcut placeholder inconsistency in documentation

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md uses placeholders like '{{kbd:step:curses}}' and '{{kbd:continue:curses}}' and '{{kbd:quit:curses}}' and '{{kbd:toggle_stack:tk}}' and '{{kbd:step_line:curses}}'

But editor-commands.md just says 'See your UI-specific help for the exact keybindings' without using the placeholder format.

The placeholder format suggests these should be replaced with actual keybindings from web_keybindings.json, but the JSON file shows 'F10' for step, 'F5' for continue, 'Esc' for stop, etc. The placeholders don't match the JSON structure (e.g., {{kbd:step:curses}} but JSON has 'editor.step' not 'step').

---

---

#### documentation_inconsistency

**Description:** Documentation references non-existent shortcuts.md file

**Affected files:**
- `docs/help/common/debugging.md`

**Details:**
debugging.md 'See Also' section includes:
- [Keyboard Shortcuts](shortcuts.md) - Complete shortcut reference

But no shortcuts.md file is provided in the source files. This is a broken documentation link.

---

---

#### code_documentation_mismatch

**Description:** SessionState has auto_save fields but WebSettingsDialog doesn't expose them

**Affected files:**
- `src/ui/web/session_state.py`
- `src/ui/web/web_settings_dialog.py`

**Details:**
SessionState has:
- auto_save_enabled: bool = True
- auto_save_interval: int = 30

But WebSettingsDialog._create_editor_settings() only shows:
- editor.auto_number (checkbox)
- editor.auto_number_step (number input)

The auto-save settings are stored in session state but not exposed in the settings dialog UI.

---

---

#### documentation_inconsistency

**Description:** Loop examples documentation has inconsistent BASIC code formatting

**Affected files:**
- `docs/help/common/examples/loops.md`

**Details:**
Most examples use proper line numbers (10, 20, 30...) but some comments are inconsistent:

Example: 'Fill array' section has:
'30 ' Fill array'
'70 ' Calculate sum'

These comments after line numbers should be 'REM' statements in proper BASIC-80:
'30 REM Fill array'
'70 REM Calculate sum'

The apostrophe (') comment syntax was added in later BASIC versions, not in MBASIC 5.21.

---

---

#### code_documentation_mismatch

**Description:** Settings dialog shows 'Limits' tab as read-only but documentation doesn't mention settings dialog at all

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/debugging.md`

**Details:**
web_settings_dialog.py _create_limits_settings() shows:
ui.label('(View only - modify in code for now)').classes('text-sm text-gray-600 mb-4')

This indicates limits are not editable in the UI, but the debugging.md and other help docs don't mention the settings dialog or explain which settings can be changed vs. which are read-only.

---

---

#### code_comment_conflict

**Description:** Comment says VERSION is auto-incremented but doesn't explain the checkpoint.sh mechanism

**Affected files:**
- `src/version.py`

**Details:**
version.py comment:
'VERSION is automatically incremented by utils/checkpoint.sh after each commit.
Manual edits to VERSION will be overwritten by the next checkpoint.'

But utils/checkpoint.sh is not provided in the source files, so this comment references external tooling that isn't documented. Users might manually edit VERSION not knowing about the checkpoint system.

---

---

#### documentation_inconsistency

**Description:** Documentation uses inconsistent terminology for 'Step' command

**Affected files:**
- `docs/help/common/debugging.md`

**Details:**
debugging.md uses multiple terms:
- 'Step Line' - Execute one entire line
- 'Step Statement' - Execute one statement
- 'Step' button (in UI descriptions)
- '{{kbd:step:curses}}' (placeholder)

But web_keybindings.json just has 'step' with description 'Step to next line' (no mention of statement-level stepping).

The documentation should clarify if 'Step' means line-level or statement-level, or if there are separate commands for each.

---

---

#### documentation_inconsistency

**Description:** Inconsistent statement about line number range

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/language.md`

**Details:**
getting-started.md states 'Numbers can be 1-65535' but language.md does not specify the valid range for line numbers. This creates an incomplete reference.

---

---

#### documentation_inconsistency

**Description:** Error code reference uses different terminology

**Affected files:**
- `docs/help/common/language/functions/cvi-cvs-cvd.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
cvi-cvs-cvd.md states 'Raises "Illegal function call" (error code FC)' but error-codes.md lists it as 'Code: FC, Number: 5, Message: Illegal function call'. The term 'error code FC' vs 'Code: FC' is inconsistent terminology.

---

---

#### documentation_inconsistency

**Description:** Missing INT function documentation prevents verification of FIX comparison

**Affected files:**
- `docs/help/common/language/functions/fix.md`
- `docs/help/common/language/functions/int.md`

**Details:**
fix.md states 'FIX(X) is equivalent to SGN(X)*INT(ABS(X))' and 'The major difference between FIX and INT is that FIX does not return the next lower number for negative X', but int.md is not provided in the documentation set to verify this claim or provide the contrasting behavior.

---

---

#### documentation_inconsistency

**Description:** Inconsistent notation explanation for exponents

**Affected files:**
- `docs/help/common/language/data-types.md`

**Details:**
The DOUBLE Precision section states:
'**Exponent Notation:**
- D notation (e.g., 1.5D+10) forces double-precision, required for exponents beyond single-precision range
- E notation (e.g., 1.5E+10) uses single-precision by default, converts to double if assigned to # variable
- For values within single-precision range, D and E are interchangeable when assigned to # variables'

This creates confusion: if E notation 'converts to double if assigned to # variable', then how is it different from D notation for values within single-precision range? The third bullet contradicts the distinction made in the first two bullets.

---

---

#### documentation_inconsistency

**Description:** Cross-reference inconsistency between LOC and LOF

**Affected files:**
- `docs/help/common/language/functions/loc.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
LOC.md 'See Also' section does not reference LOF, but LOF.md 'See Also' section references LOC with description 'Returns current file position/record number (LOF returns total size in bytes)'. This creates an asymmetric cross-reference relationship.

---

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' sections across system functions

**Affected files:**
- `docs/help/common/language/functions/fre.md`
- `docs/help/common/language/functions/hex_dollar.md`
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/inp.md`

**Details:**
FRE, INKEY$, INP, and PEEK all have nearly identical 'See Also' sections listing the same functions, but HEX$ (a string function) has a completely different set of 'See Also' references. The system functions appear to share a template 'See Also' list that may not be contextually relevant for each function.

---

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' ordering in mathematical functions

**Affected files:**
- `docs/help/common/language/functions/int.md`
- `docs/help/common/language/functions/sgn.md`
- `docs/help/common/language/functions/sin.md`
- `docs/help/common/language/functions/sqr.md`

**Details:**
Mathematical functions have 'See Also' sections with the same functions but in different orders. For example, INT lists them as: ABS, ATN, CDBL, CINT, COS, CSNG, EXP, FIX, LOG, RND, SGN, SIN, SQR, TAN. SGN lists them as: ABS, ATN, COS, EXP, FIX, INT, LOG, RND, SIN, SQR, TAN (missing CDBL, CINT, CSNG). This inconsistency makes navigation less predictable.

---

---

#### documentation_inconsistency

**Description:** PEEK documentation states POKE is complementary but implementation note contradicts this

**Affected files:**
- `docs/help/common/language/functions/peek.md`

**Details:**
The Description section states: 'PEEK is traditionally the complementary function to the POKE statement. However, in this implementation, PEEK returns random values and POKE is a no-op, so they are not functionally related.' This creates confusion as the traditional relationship is mentioned but then immediately contradicted. The documentation should be clearer about the non-functional relationship upfront.

---

---

#### documentation_inconsistency

**Description:** SPACE$ and SPC have overlapping functionality but inconsistent cross-references

**Affected files:**
- `docs/help/common/language/functions/space_dollar.md`
- `docs/help/common/language/functions/spc.md`

**Details:**
SPACE$ documentation says 'For variable spacing in PRINT statements, see SPC() and TAB()' and lists SPC in 'See Also'. However, SPC documentation does not mention SPACE$ in its 'See Also' section, only listing TAB, PRINT, LPRINT, POS. This creates an asymmetric relationship.

---

---

#### documentation_inconsistency

**Description:** MKI$/MKS$/MKD$ 'See Also' section includes unrelated functions

**Affected files:**
- `docs/help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md`

**Details:**
The 'See Also' section includes CLOAD and CSAVE with notes 'THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION', which are cassette tape commands unrelated to the core functionality of converting numbers to strings for random file operations. Also includes LPRINT which is not directly related to file buffer operations.

---

---

#### documentation_inconsistency

**Description:** Index categorization may be incomplete or inconsistent

**Affected files:**
- `docs/help/common/language/functions/index.md`

**Details:**
The index shows 'System Functions' category includes: FRE, INKEY$, INP, PEEK, USR, VARPTR. However, LPOS is categorized as 'file-io' in its frontmatter but could arguably be a system function since it deals with hardware (line printer). The categorization scheme may need review for consistency.

---

---

#### documentation_inconsistency

**Description:** Inconsistent 'related' field in frontmatter - str_dollar.md lists 'left_dollar' and 'right_dollar' but string_dollar.md does not include these in its See Also section

**Affected files:**
- `docs/help/common/language/functions/str_dollar.md`
- `docs/help/common/language/functions/string_dollar.md`

**Details:**
str_dollar.md frontmatter:
related: ['val', 'print-using', 'left_dollar', 'right_dollar']

string_dollar.md See Also section does not include left_dollar or right_dollar references, though both documents have similar See Also lists for other string functions.

---

---

#### documentation_inconsistency

**Description:** TAB function documentation includes READ and DATA in See Also section, but these are not directly related to TAB functionality

**Affected files:**
- `docs/help/common/language/functions/tab.md`

**Details:**
TAB See Also includes:
- [READ](../statements/read.md) - Read data from DATA statements (used in example above)
- [DATA](../statements/data.md) - Store data for READ statements (used in example above)

These are only tangentially related because they appear in the example code, not because they're functionally related to TAB. Other function docs don't include every statement used in their examples.

---

---

#### documentation_inconsistency

**Description:** Inconsistent formatting of version information in frontmatter

**Affected files:**
- `docs/help/common/language/statements/auto.md`
- `docs/help/common/language/statements/chain.md`

**Details:**
auto.md does not have a 'Versions:' field in its content, while chain.md explicitly states '**Versions:** Disk' in the content body. Other documents like string_dollar.md show versions in a consistent format. The version information should be consistently placed either in frontmatter or in a standard location in the content.

---

---

#### documentation_inconsistency

**Description:** CONT documentation references non-existent example

**Affected files:**
- `docs/help/common/language/statements/cont.md`

**Details:**
The Example section states:
'See example Section 2.61, STOP.'

However, this is a reference to a section number from the original manual that doesn't exist in the current documentation structure. The reference should either point to the actual STOP.md file or include an inline example.

---

---

#### documentation_inconsistency

**Description:** CLOAD and CSAVE documentation state they are not included in DEC VT180 version but don't clarify modern implementation status

**Affected files:**
- `docs/help/common/language/statements/cload.md`
- `docs/help/common/language/statements/csave.md`

**Details:**
Both documents state:
'**Note:** This command is not included in the DEC VT180 version or modern disk-based systems.'

However, they don't have an 'Implementation Note' section like USR, VARPTR, and CALL do to clearly indicate whether these are implemented in the current Python interpreter. Given they're cassette-specific commands, they likely aren't implemented but this should be explicitly stated.

---

---

#### documentation_inconsistency

**Description:** CLS documentation states it works in all UI backends but doesn't mention which backends exist

**Affected files:**
- `docs/help/common/language/statements/cls.md`

**Details:**
The documentation states:
'**Note:** CLS is implemented in MBASIC and works in all UI backends.'

This implies multiple UI backends exist but doesn't reference where to find information about them. Other system-level commands don't mention UI backends at all.

---

---

#### documentation_inconsistency

**Description:** COMMON documentation has incomplete example with ellipsis

**Affected files:**
- `docs/help/common/language/statements/common.md`

**Details:**
The example shows:
'100 COMMON A,B,C,D(),G$
               110 CHAIN "PROG3",10
                    •'

The bullet point (•) and unusual indentation suggest this is a fragment from the original manual that wasn't fully adapted. The example should be complete and properly formatted.

---

---

#### documentation_inconsistency

**Description:** Inconsistent formatting of 'See Also' sections between related DEF statements

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
def-fn.md 'See Also' section:
- [DEF USR](def-usr.md) - Define assembly subroutine address
- [USR](../functions/usr.md) - Call assembly language subroutine
- [GOSUB-RETURN](gosub-return.md) - Branch to and return from a subroutine

def-usr.md 'See Also' section:
- [USR](../functions/usr.md) - Call assembly language subroutine
- [DEF FN](def-fn.md) - Define user-defined function
- [POKE](poke.md) - Write byte to memory location
- [PEEK](../functions/peek.md) - Read byte from memory location

The descriptions are inconsistent (e.g., 'Define assembly subroutine address' vs 'Define user-defined function' - one has 'assembly' detail, other doesn't).

---

---

#### documentation_inconsistency

**Description:** DELETE and EDIT have different error descriptions for non-existent line numbers

**Affected files:**
- `docs/help/common/language/statements/delete.md`
- `docs/help/common/language/statements/edit.md`

**Details:**
delete.md states:
"If <line number> does not exist, an 'Illegal function call' error occurs."

edit.md states:
"If the line doesn't exist, an error is generated."

The error type should be consistent - either both specify 'Illegal function call' or both use generic 'error'.

---

---

#### documentation_inconsistency

**Description:** GOSUB documentation mentions STOP, END, or GOTO to prevent inadvertent entry, but GOTO documentation doesn't mention this pattern

**Affected files:**
- `docs/help/common/language/statements/gosub-return.md`
- `docs/help/common/language/statements/goto.md`

**Details:**
gosub-return.md states:
"To prevent inadvertent entry into the subroutine, it may be preceded by a STOP, END, or GOTO statement that directs program control around the subroutine."

This is a common programming pattern that could be mentioned in GOTO documentation as a use case.

---

---

#### documentation_inconsistency

**Description:** HELPSETTING is listed in index.md under 'Modern Extensions' but the command name in the index is inconsistent

**Affected files:**
- `docs/help/common/language/statements/helpsetting.md`
- `docs/help/common/language/statements/index.md`

**Details:**
In index.md, the Modern Extensions section lists:
"- [HELPSETTING](helpsetting.md) - Display help for settings
- [LIMITS](limits.md) - Show interpreter limits
- [SET](setsetting.md) - Configure interpreter settings
- [SHOW SETTINGS](showsettings.md) - Display current settings"

The link text '[SET](setsetting.md)' doesn't match - it should be '[SETSETTING](setsetting.md)' to match the actual command name and filename.

---

---

#### documentation_inconsistency

**Description:** DIM states initial array values are zero, but ERASE doesn't mention what happens to array values after ERASE

**Affected files:**
- `docs/help/common/language/statements/dim.md`
- `docs/help/common/language/statements/erase.md`

**Details:**
dim.md states:
"The DIM statement sets all the elements of the specified arrays to an initial value of zero."

erase.md states:
"Arrays may be redimensioned after they are ERASEd, or the previously allocated array space in memory may be used for other purposes."

It's unclear whether ERASEd arrays are zeroed or if the memory is left in an undefined state. The documentation should clarify this.

---

---

#### documentation_inconsistency

**Description:** DEF FN Example 4 uses hexadecimal notation but the explanation could be clearer about the bit operation

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
Example 4 states:
"- `&H5F` is hexadecimal notation (hex 5F = decimal 95 = binary 01011111)
- `AND &H5F` clears bit 5 (the lowercase bit in ASCII), converting lowercase to uppercase"

This is technically incorrect - AND &H5F clears bit 5 (the 0x20 bit), but &H5F = 01011111 means bit 5 is SET in the mask. The operation clears bit 5 in the CHARACTER by ANDing with a mask that has bit 5 clear. The explanation should say 'AND &H5F clears bit 5 of the character' or 'AND with a mask that has bit 5 clear'.

---

---

#### documentation_inconsistency

**Description:** Filename inconsistency in title vs syntax

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
Title: 'LINE INPUT# (File)'
Syntax: 'LINE INPUT#<file number>,<string variable>'
The title adds '(File)' for disambiguation but this is not part of the actual statement name.

---

---

#### documentation_inconsistency

**Description:** CP/M-specific behavior may not apply to Python implementation

**Affected files:**
- `docs/help/common/language/statements/kill.md`

**Details:**
Documentation states: 'CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files.'
This is OS-specific behavior that may not be relevant to a Python-based interpreter running on modern systems.

---

---

#### documentation_inconsistency

**Description:** Inconsistent formatting in example section

**Affected files:**
- `docs/help/common/language/statements/list.md`

**Details:**
Example section mixes 'Format 1:' and 'Format 2:' labels with indentation that makes it unclear which examples belong to which format. The layout could be clearer.

---

---

#### documentation_inconsistency

**Description:** File closing behavior documentation could be clearer

**Affected files:**
- `docs/help/common/language/statements/load.md`
- `docs/help/common/language/statements/merge.md`

**Details:**
LOAD doc: 'LOAD (without ,R): Closes all open files... LOAD with ,R option: all open data files are kept open'
MERGE doc: 'Unlike LOAD (without ,R), MERGE does NOT close open files'
The relationship between these three behaviors (LOAD, LOAD,R, MERGE) could be presented more clearly in a comparison table.

---

---

#### documentation_inconsistency

**Description:** Missing version information

**Affected files:**
- `docs/help/common/language/statements/lset.md`

**Details:**
LSET documentation shows 'Versions: Disk' but other similar file I/O commands like GET, PUT, FIELD also show 'Versions: Disk'. This is consistent, but LSET's related command RSET should also be checked for version consistency.

---

---

#### documentation_inconsistency

**Description:** Outdated hardware-specific documentation

**Affected files:**
- `docs/help/common/language/statements/null.md`

**Details:**
Documentation references '10-character-per-second tape punches' and 'Teletypes' which are obsolete hardware. This command may not be relevant to modern Python-based implementation.

---

---

#### documentation_inconsistency

**Description:** Error handling within error handler behavior unclear

**Affected files:**
- `docs/help/common/language/statements/on-error-goto.md`

**Details:**
Documentation states: 'If an error occurs during execution of an error handling subroutine, the BASIC error message is printed and execution terminates. Error trapping does not occur within the error handling subroutine.'
But earlier it says: 'It is recommended that all error trapping subroutines execute an ON ERROR GOTO 0 if an error is encountered for which there is no recovery action.'
These statements seem contradictory - if error trapping doesn't occur in the handler, why would ON ERROR GOTO 0 be needed there?

---

---

#### documentation_inconsistency

**Description:** File opening restrictions unclear

**Affected files:**
- `docs/help/common/language/statements/open.md`

**Details:**
Documentation states: 'A file can be OPENed for sequential input or random access on more than one file number at a time. A file may be OPENed for output, however, on only one file number at a time.'
It's unclear if this means:
1. The same physical file can be opened multiple times for input but only once for output
2. Only one file total can be open for output at a time
The wording suggests interpretation 1, but clarification would help.

---

---

#### documentation_inconsistency

**Description:** Print zone width inconsistency potential

**Affected files:**
- `docs/help/common/language/statements/print.md`

**Details:**
Documentation states print zones are 14 columns each, listing zones at columns 1-14, 15-28, 29-42, 43-56, 57-70.
This should be verified against WIDTH statement behavior and actual implementation, as some BASIC variants use different zone widths.

---

---

#### documentation_inconsistency

**Description:** Incomplete PRINT# USING format string documentation

**Affected files:**
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
Documentation mentions format string characters (# . $$ ** ,) but doesn't provide complete details. It should reference the full PRINT USING documentation or provide complete format string syntax.

---

---

#### documentation_inconsistency

**Description:** Confusing note about PRINT# with random files

**Affected files:**
- `docs/help/common/language/statements/put.md`

**Details:**
Documentation states: 'PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer before a PUT statement.'
This is an advanced technique that seems inconsistent with the typical FIELD/LSET/RSET workflow. The relationship and use case should be clarified.

---

---

#### documentation_inconsistency

**Description:** Seed range documentation

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
Documentation shows prompt: 'Random Number Seed (-32768 to 32767)?'
This is a 16-bit signed integer range. Should verify this matches the actual implementation and whether larger seeds are supported in the Python version.

---

---

#### documentation_inconsistency

**Description:** See Also section references non-existent file

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
See Also section references: '[LINE INPUT](line-input.md)'
But the actual file is 'line-input.md' which exists. However, the link format should be verified for consistency across all documentation files.

---

---

#### documentation_inconsistency

**Description:** Similar command names (RESTORE vs RESET) could cause confusion but are not cross-referenced

**Affected files:**
- `docs/help/common/language/statements/restore.md`
- `docs/help/common/language/statements/reset.md`

**Details:**
RESTORE resets DATA pointer, RESET closes all files. These are completely different operations with similar names. Neither document cross-references the other to prevent confusion, unlike RESET/RSET which do warn about confusion.

---

---

#### documentation_inconsistency

**Description:** Similar command names (RESUME vs RESTORE) could cause confusion but are not cross-referenced

**Affected files:**
- `docs/help/common/language/statements/resume.md`
- `docs/help/common/language/statements/restore.md`

**Details:**
RESUME continues after error, RESTORE resets DATA pointer. These are completely different operations with similar names starting with 'RES'. No cross-reference warning exists.

---

---

#### documentation_inconsistency

**Description:** SETSETTING and SHOWSETTINGS marked as 'MBASIC Extension' but settings.md doesn't consistently emphasize this

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
SETSETTING.md and SHOWSETTINGS.md both say: 'Versions: MBASIC Extension'

settings.md says at top: 'Note: The settings system is a MBASIC Extension - not present in original MBASIC 5.21.'

But the individual setting descriptions in settings.md don't consistently remind readers these are extensions. This is minor but could be clearer.

---

---

#### documentation_inconsistency

**Description:** WRITE and WRITE# have inconsistent title formatting

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md has title: 'WRITE (Screen)'
writei.md has title: 'WRITE# (File)'

The hash symbol placement is inconsistent. Should be 'WRITE (Screen)' and 'WRITE# (File)' or 'WRITE' and 'WRITE #' with space.

---

---

#### documentation_inconsistency

**Description:** SWAP example output formatting is inconsistent with other examples

**Affected files:**
- `docs/help/common/language/statements/swap.md`

**Details:**
SWAP.md shows:
'LIST\n10 A$="ONE" : B$="ALL" : C$="FOR"\n20 PRINT A$; " "; C$; " "; B$\n30 SWAP A$, B$\n40 PRINT A$; " "; C$; " "; B$\n\nRUN\nONE FOR ALL\nALL FOR ONE\nOk'

Most other examples separate the LIST output from RUN output more clearly, or don't show LIST at all. This format is harder to read.

---

---

#### documentation_inconsistency

**Description:** TRON-TROFF uses hyphenated title but other paired commands don't

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
Title is 'TRON-TROFF' with hyphen, but the syntax shows them as separate commands: 'TRON' and 'TROFF'.

Other paired commands like WHILE...WEND use ellipsis in title. Should be consistent: either 'TRON/TROFF' or 'TRON...TROFF' or separate pages.

---

---

#### documentation_inconsistency

**Description:** WHILE...WEND uses ellipsis in title but hyphen would be more consistent with syntax

**Affected files:**
- `docs/help/common/language/statements/while-wend.md`

**Details:**
Title: 'WHILE...WEND'
Syntax shows: 'WHILE <expression>' and 'WEND' as separate statements

The ellipsis suggests they're part of one statement, but they're actually two separate statements that work together. Other documentation uses ellipsis for this pattern (like FOR...NEXT), so this is consistent with that convention, but could be clearer.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for exiting

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
CLI docs show 'Ctrl+D - Exit MBASIC (Unix/Linux)' and 'Ctrl+Z - Exit MBASIC (Windows)' as keyboard shortcuts, but Tk docs only show 'Exit' in the File Menu with no keyboard shortcut listed. It's unclear if Ctrl+D/Ctrl+Z work in Tk UI or if only the menu option is available.

---

---

#### documentation_inconsistency

**Description:** Inconsistent description of direct mode behavior

**Affected files:**
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
Curses docs state 'Lines without numbers execute immediately: PRINT 2 + 2\n 4\nThis is useful for testing expressions.' Tk docs mention an 'Immediate mode panel' that 'Some Tk configurations include' but don't clearly explain if this is the same as direct mode or a separate feature. The relationship between these concepts needs clarification.

---

---

#### documentation_inconsistency

**Description:** Inconsistent information about command history availability

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/mbasic/extensions.md`

**Details:**
CLI docs show 'Up/Down - Command history (if available)' suggesting it's conditional, but extensions.md doesn't mention command history at all in the CLI features. The conditions under which command history is available should be clarified.

---

---

#### documentation_inconsistency

**Description:** Debugging features described differently in different locations

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
features.md states under Debugging: 'Breakpoints - Set/clear breakpoints (available in all UIs; access method varies)' and 'Step execution - Execute one line at a time (available in all UIs; access method varies)'. However, debugging.md for CLI shows 'STEP INTO/OVER not yet implemented (use STEP)' under Planned features, suggesting step execution has limitations not mentioned in the features overview.

---

---

#### documentation_inconsistency

**Description:** Inconsistent description of Web UI availability

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/ui/cli/index.md`

**Details:**
getting-started.md includes Web UI as one of four interfaces with full documentation. However, cli/index.md states 'Note: MBASIC supports multiple interfaces (CLI, Curses, Tk, Web)' but the main help index in cli/index.md does not provide a direct link to Web UI documentation, only mentioning it in a note.

---

---

#### documentation_inconsistency

**Description:** Planned features listed without clear implementation status

**Affected files:**
- `docs/help/ui/cli/debugging.md`

**Details:**
debugging.md lists 'Planned (not yet implemented):' features like 'STEP INTO - Step into subroutines (planned)' and 'STEP OVER - Step over subroutine calls (planned)'. Later under Limitations it states 'STEP INTO/OVER not yet implemented (use STEP)'. This redundancy could be consolidated, and it's unclear if these are on a roadmap or just wishlist items.

---

---

#### documentation_inconsistency

**Description:** Settings file location may be inconsistent with actual implementation

**Affected files:**
- `docs/help/ui/cli/settings.md`

**Details:**
settings.md states: 'Settings file location: Linux/Mac: ~/.mbasic/settings.json, Windows: %APPDATA%\mbasic\settings.json'. However, without seeing the actual code implementation, we cannot verify if these paths are correct or if there are other possible locations (e.g., XDG_CONFIG_HOME on Linux).

---

---

#### documentation_inconsistency

**Description:** Games library link inconsistency

**Affected files:**
- `docs/help/mbasic/index.md`
- `docs/help/ui/cli/index.md`

**Details:**
cli/index.md includes a prominent '🎮 Games Library' section at the top with a link to '../../../library/games/index.md' stating '113 classic CP/M era games ready to run!'. However, mbasic/index.md does not mention the games library at all. This seems like an important feature that should be consistently referenced.

---

---

#### documentation_inconsistency

**Description:** Keyboard shortcut notation inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md uses template notation like '{{kbd:run:curses}}' and '{{kbd:save:curses}}' for keyboard shortcuts, but these are not expanded in the markdown. This suggests either: 1) A template system should process these before display, 2) The actual shortcuts should be documented inline, or 3) There's a missing preprocessing step. Without seeing how these are rendered, it's unclear if users will see the actual shortcuts.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for delete operation

**Affected files:**
- `docs/help/ui/curses/editing.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
editing.md states: "### Quick Delete (^D)
1. Navigate to the line
2. Press **^D**
3. Line is deleted immediately"

But feature-reference.md states: "### Delete Lines ({{kbd:delete:curses}})
Delete the current line in the editor."

The ^D notation vs {{kbd:delete:curses}} template suggests different shortcuts, though they may resolve to the same key.

---

---

#### documentation_inconsistency

**Description:** Incomplete keyboard reference for variables window

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/variables.md`

**Details:**
quick-reference.md shows: "| **s** | Cycle sort mode (Accessed → Written → Read → Name) |
| **d** | Toggle sort direction (ascending ↑ / descending ↓) |
| **f** | Cycle filter mode (All → Scalars → Arrays → Modified) |
| **/** | Search for variable |
| **n** | Next search match |
| **N** | Previous search match |"

But variables.md shows additional keys: "| `r` | Refresh |
| `u` | Toggle auto-update |
| `e` | Export to file |
| `h` | Help |"

These additional keys are not documented in the quick reference.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for settings

**Affected files:**
- `docs/help/ui/curses/settings.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
settings.md states: "**Keyboard shortcut:** `Ctrl+,`"

But feature-reference.md states: "### Settings Widget ({{kbd:settings:curses}})"

The Ctrl+, notation vs {{kbd:settings:curses}} template suggests different documentation styles that should be unified.

---

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for variable access tracking

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
variables.md uses: "Most recently accessed (read or written)"

feature-reference.md uses: "Most recently accessed (read or written) - newest first"

The addition of "newest first" in one document but not the other creates ambiguity about the sort order direction.

---

---

#### documentation_inconsistency

**Description:** Inconsistent count of features in Tk UI

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/index.md`

**Details:**
feature-reference.md title says "Complete Feature Reference" and lists features in categories:
- File Operations (8 features)
- Execution & Control (6 features)
- Debugging (6 features)
- Variable Inspection (6 features)
- Editor Features (7 features)
- Help System (4 features)
Total: 37 features

But index.md comparison table lists only generic categories without counts. This is not necessarily an inconsistency but the feature-reference.md could be outdated if features were added/removed.

---

---

#### documentation_inconsistency

**Description:** Inconsistent UI naming: 'Curses UI' vs 'Curses'

**Affected files:**
- `docs/help/ui/index.md`

**Details:**
index.md uses both:
- Header: "### 📟 [Curses UI](curses/index.md)"
- Table: "| Feature | Curses | CLI | Tkinter | Web |"

Should be consistent throughout. Either always "Curses UI" or always "Curses".

---

---

#### documentation_inconsistency

**Description:** Inconsistent UI naming: 'Tkinter GUI' vs 'Tkinter' vs 'Tk'

**Affected files:**
- `docs/help/ui/index.md`

**Details:**
index.md uses multiple names:
- Header: "### 🖼️ [Tkinter GUI](tk/index.md)"
- Table: "| Feature | Curses | CLI | Tkinter | Web |"
- Command: "mbasic --ui tk"

The command uses 'tk' but the documentation uses 'Tkinter' and 'Tkinter GUI'. Should be consistent.

---

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md uses two different formats:

1. With backticks: "`{{kbd:run:web}}`"
2. Without backticks: "{{kbd:continue:web}}"

Example:
"Press `F12` to open browser tools (standard browser shortcut)"
vs
"**Run ({{kbd:run:web}})** - Start program from beginning"

Should be consistent throughout the document.

---

---

#### documentation_inconsistency

**Description:** Missing View menu documentation in features.md

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
web-interface.md documents a 'View Menu' with 'Show Variables' option: 'View Menu
- **Show Variables** - Open the Variables Window to view and monitor program variables in real-time'

However, features.md does not mention the View menu at all in its 'User Interface' section or anywhere else. This is an omission that creates incomplete documentation.

---

---

#### documentation_inconsistency

**Description:** Inconsistent menu structure documentation

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md states: 'At the very top, three menus: **File** - New, Open, Save, Save As, Recent Files, Exit; **Run** - Run Program, Stop, Step, Continue, List Program, Show Variables, Show Stack, Clear Output; **Help** - Help Topics, About'

However, web-interface.md documents: 'File Menu', 'Edit Menu', 'Run Menu', 'View Menu', 'Help Menu' - that's FIVE menus, not three.

Additionally, getting-started.md lists 'Show Variables' and 'Show Stack' under the Run menu, but web-interface.md shows 'Show Variables' under the View menu. The menu structure is inconsistently documented.

---

---

#### documentation_inconsistency

**Description:** Broken or inconsistent library documentation structure

**Affected files:**
- `docs/help/ui/web/index.md`
- `docs/library/business/index.md`
- `docs/library/data_management/index.md`
- `docs/library/demos/index.md`
- `docs/library/education/index.md`

**Details:**
index.md under 'Games Library' links to '../../../library/games/index.md' and states '113 classic CP/M era games to download and load!'.

However, the provided library documentation only includes: business/index.md, data_management/index.md, demos/index.md, and education/index.md. The games/index.md file is missing from the provided documentation, yet it's prominently featured in the main index.

Additionally, all library index files (business, data_management, demos, education) have identical 'How to Use' and 'About' sections with the text 'These programs are from the CP/M and early PC era (1970s-1980s), preserved from historical archives including OAK, Simtel, and CP/M CD-ROMs.' This suggests copy-paste documentation that may not be accurate for all categories (e.g., demos/index.md includes 'Modern' test programs, not just CP/M era programs).

---

---

#### documentation_inconsistency

**Description:** Inconsistent toolbar button descriptions

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md describes toolbar buttons as: 'Run - Parse and execute the program (▶️ green button, {{kbd:run:web}})', 'Stop - Stop running program (⏹️ red button, {{kbd:stop:web}})', 'Step - Execute all statements on current line, then pause (⏭️ button, {{kbd:step_line:web}})', 'Stmt - Execute one statement, then pause (↻ button, {{kbd:step:web}})', 'Cont - Resume normal execution after stepping (▶️⏸️ button, {{kbd:continue:web}})'.

However, web-interface.md describes them as: 'Run (▶️ green) - Start program execution', 'Stop (⏹️ red) - Stop running program', 'Step (⏭️) - Execute all statements on current line', 'Stmt (↻) - Execute one statement', 'Cont (▶️⏸️) - Continue execution after pause'.

The descriptions are similar but not identical. getting-started.md includes keyboard shortcuts and more detailed descriptions ('Parse and execute' vs 'Start program execution'), while web-interface.md is more concise. This inconsistency could confuse users.

---

---

#### documentation_inconsistency

**Description:** Category name mismatch in header and footer

**Affected files:**
- `docs/library/electronics/index.md`

**Details:**
Header says '# MBASIC Electronics Programs' but the footer section says '## About These Electronics' (missing 'Programs'). Other library docs consistently use the full category name in the footer (e.g., 'About These Games', 'About These Ham Radio', 'About These Telecommunications').

---

---

#### documentation_inconsistency

**Description:** Inconsistent footer section naming pattern

**Affected files:**
- `docs/library/ham_radio/index.md`
- `docs/library/telecommunications/index.md`

**Details:**
Ham Radio footer says '## About These Ham Radio' and Telecommunications says '## About These Telecommunications', but these should probably be '## About These Ham Radio Programs' and '## About These Telecommunications Programs' to match the pattern in other libraries (Games, Utilities, etc.).

---

---

#### documentation_inconsistency

**Description:** Library statistics may be outdated

**Affected files:**
- `docs/library/index.md`

**Details:**
The index.md states '**Library Statistics:**
- 177 programs from the 1970s-1980s'

Counting the programs listed in the provided documentation:
- Games: ~130 programs
- Utilities: 19 programs
- Electronics: 13 programs
- Ham Radio: 7 programs
- Telecommunications: 5 programs

This totals approximately 174 programs visible in the provided docs, which is close to 177 but may not include Education, Business, Data Management, and Demos categories that are mentioned but not provided. The count should be verified against actual program files.

---

---

#### documentation_inconsistency

**Description:** Million.bas categorization inconsistency

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
Million.bas is described as 'Millionaire life simulation game - make financial decisions to accumulate wealth' with tags 'simulation, financial, game', but it's placed in the Utilities library rather than the Games library where it would seem to belong based on its description.

---

---

#### documentation_inconsistency

**Description:** Rotate.bas categorization inconsistency

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
Rotate.bas is described as 'Letter rotation puzzle game - order letters A-P by rotating groups clockwise' with tags 'puzzle, game, logic', but it's placed in the Utilities library rather than the Games library where games typically belong.

---

---

#### documentation_inconsistency

**Description:** Bearing.bas categorization inconsistency

**Affected files:**
- `docs/library/electronics/index.md`

**Details:**
Bearing.bas is described as 'Compute bearings between geographic coordinates - calculates distance and bearing between two latitude/longitude positions' with tags 'geography, navigation, coordinates, bearing'. This appears to be a navigation/geography utility rather than an electronics program. It might be better suited for a different category or the Utilities library.

---

---

#### documentation_inconsistency

**Description:** Reference to non-existent bug report link

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`

**Details:**
The CASE_HANDLING_GUIDE.md is in docs/user/ but references features that aren't mentioned in the library documentation. More importantly, the library index.md states '⚠️ **Important:** These programs have had minimal testing by humans. If you encounter issues, please submit a bug report (link coming soon).' - the bug report link is marked as 'coming soon' but no actual link or instructions are provided.

---

---

#### documentation_inconsistency

**Description:** Performance measurements disclaimer is vague about what 'typical development hardware' means

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
The note states: 'These measurements are approximate, taken on typical development hardware (modern CPU, 8GB+ RAM, Python 3.9+)'

This is imprecise - 'modern CPU' could mean anything from 2015-2024. More specific hardware specs would be helpful for users to calibrate expectations.

---

---

#### documentation_inconsistency

**Description:** Document mentions 'utils/convert_to_cpm.py' script but doesn't indicate if this script actually exists in the project

**Affected files:**
- `docs/user/FILE_FORMAT_COMPATIBILITY.md`

**Details:**
The document states:
'MBASIC includes a utility script for CP/M conversion:
```bash
# Convert a file to CP/M format (CRLF line endings)
python3 utils/convert_to_cpm.py yourfile.bas
```'

No indication is given whether this script is implemented, planned, or just an example. Users might try to use it and find it doesn't exist.

---

---

#### documentation_inconsistency

**Description:** Settings file locations use different path separators inconsistently

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
The document shows:
'~/.mbasic/settings.json' (Unix-style with forward slash)
'%APPDATA%/mbasic/settings.json' (Windows environment variable but Unix-style forward slash)

Windows paths should use backslashes: '%APPDATA%\mbasic\settings.json' or clarify that forward slashes work on Windows too.

---

---

#### documentation_inconsistency

**Description:** README.md mentions 'keyboard-shortcuts.md' is 'Curses UI specific' but also says 'Tk shortcuts in TK_UI_QUICK_START.md'

**Affected files:**
- `docs/user/README.md`

**Details:**
Under Reference Documentation:
'- **[keyboard-shortcuts.md](keyboard-shortcuts.md)** - Keyboard shortcuts reference (Curses UI specific; Tk shortcuts in TK_UI_QUICK_START.md)'

This implies there are two separate keyboard shortcut documents, but it's unclear if there's overlap, if they're comprehensive, or if Web UI shortcuts are documented anywhere.

---

---

#### documentation_inconsistency

**Description:** Installation guide shows 'python3 mbasic' but doesn't clarify if 'mbasic' is a script, module, or directory

**Affected files:**
- `docs/user/INSTALL.md`

**Details:**
Throughout INSTALL.md, commands like:
'python3 mbasic'
'python3 mbasic --ui curses'

It's not immediately clear to a new user what 'mbasic' refers to. Is it a Python script named 'mbasic' (no .py extension)? A package? A directory with __main__.py? This should be clarified early in the installation guide.

---

---

#### documentation_inconsistency

**Description:** TK_UI_QUICK_START.md references a non-existent keyboard shortcuts document for Tk UI

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
In the 'Learn More About...' section, TK_UI_QUICK_START.md states:
'- **Keyboard Shortcuts**: See [Tk Keyboard Shortcuts](keyboard-shortcuts.md)'

However, keyboard-shortcuts.md documents Curses UI shortcuts, not Tk UI shortcuts. The link is misleading.

---

---

#### documentation_inconsistency

**Description:** Inconsistent reference to settings documentation filename

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md states:
'**Learn more:** See `docs/user/SETTINGS_AND_CONFIGURATION.md` for complete settings guide.'

This filename uses SCREAMING_SNAKE_CASE, but other documentation files in the same directory use different naming conventions (TK_UI_QUICK_START.md, UI_FEATURE_COMPARISON.md use SCREAMING_SNAKE_CASE, while keyboard-shortcuts.md and sequential-files.md use kebab-case). The referenced file is not provided in the documentation set, so we cannot verify if it exists or what its actual name is.

---

---

#### documentation_inconsistency

**Description:** Reference to non-existent FILE_FORMAT_COMPATIBILITY.md document

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
In sequential-files.md, the 'See Also' section includes:
'- [File Format Compatibility](FILE_FORMAT_COMPATIBILITY.md) - Line endings and file format compatibility'

This document is not provided in the documentation set. It's unclear if this is a separate document or if sequential-files.md itself is meant to be the file format compatibility documentation.

---

---

#### documentation_inconsistency

**Description:** CLI save feature marked as not available despite SAVE command being documented

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In the 'File Operations' section:
| **Save (interactive)** | ❌ | ✅ | ✅ | ✅ | Keyboard shortcut prompts for filename |

CLI is marked as ❌ (not available) for 'Save (interactive)', but later in 'Known Gaps' section it states:
'- CLI: No interactive save prompt (use SAVE "filename" command instead)'

This suggests CLI does have save functionality via command, just not interactive. The feature name 'Save (interactive)' vs the note clarification creates confusion about whether CLI can save at all.

---

---

#### documentation_inconsistency

**Description:** Inconsistent toolbar button naming conventions

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md uses different naming conventions for toolbar buttons:
- 'Step toolbar button' (lowercase 'toolbar button')
- 'Stmt toolbar button' (lowercase 'toolbar button')
- 'Click "Step" toolbar button' (quoted button name)
- 'Click "Cont" toolbar button' (quoted button name)
- 'Click "Stmt" toolbar button' (quoted button name)

Sometimes buttons are quoted, sometimes not. Sometimes 'toolbar button' is capitalized in context, sometimes not. This inconsistency makes the documentation less clear.

---

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of 'Variables Window' and 'Execution Stack Window'

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
Throughout TK_UI_QUICK_START.md, window names are capitalized inconsistently:
- 'Variables Window' (title case)
- 'Variables window' (sentence case)
- 'Execution Stack Window' (title case)
- 'variables window' (lowercase)

Example quotes:
'Press **{{kbd:toggle_variables}}** to open Variables Window'
'Check variable values in Variables Window'
'keep Variables Window open'
'you'll see each array element as it's filled!' (no window name given)

Standardizing on either title case or sentence case would improve consistency.

---


## Summary

- Total issues found: 702
- Code/Comment conflicts: 232
- Other inconsistencies: 470

---

