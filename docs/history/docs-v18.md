# Documentation Consistency Report (v18)

Generated: 2025-11-09 21:24:14
Category: Documentation, comments, and docstring issues only
Status: Issues that do NOT change code behavior

## 🔴 High Severity

#### code_vs_comment

**Description:** Comment about negative zero handling contradicts itself and may not match implementation intent

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment states:
"# Determine sign - preserve negative sign for values that round to zero.
# Use original_negative (captured above before rounding) to detect negative values that rounded to zero.
# This allows us to detect cases like -0.001 which round to 0 but should display as "-0" (not "0").
# This matches BASIC behavior. Positive values that round to zero display as "0"."

Code:
if rounded == 0 and original_negative:
    is_negative = True
else:
    is_negative = rounded < 0

The comment says this "matches BASIC behavior" but doesn't specify which BASIC version. MBASIC 5.21 behavior for negative values rounding to zero is not documented elsewhere in the file. This needs verification against actual MBASIC 5.21 behavior.

---
---

#### documentation_inconsistency

**Description:** create_unlimited_limits() breaks documented MBASIC 5.21 compatibility with warning, but other preset functions don't mention compatibility

**Affected files:**
- `src/resource_limits.py`

**Details:**
create_unlimited_limits() docstring explicitly warns:
"Note: This configuration intentionally breaks MBASIC 5.21 compatibility by setting
max_string_length to 1MB (instead of 255 bytes). This allows testing modern programs
without string length constraints, but may cause tests to pass with unlimited limits
that would fail with MBASIC-compatible limits. Use create_local_limits() or
create_web_limits() for MBASIC 5.21 compatible string handling."

However, create_web_limits() and create_local_limits() docstrings don't explicitly state they maintain MBASIC 5.21 compatibility. They just say 'restrictive' and 'generous' respectively. Given that the unlimited version explicitly calls out compatibility breaking, the other two should explicitly state they maintain compatibility.

---
---

#### code_vs_comment

**Description:** Comment in _on_paste claims 'Both cases use the same logic' for multi-line paste and single-line paste into blank line, but this is misleading - the code paths are different (inline paste vs auto-numbering)

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1237:
# Multi-line paste or single-line paste into blank line - use auto-numbering logic
# Both cases use the same logic (split by \n, process each line):
# 1. Multi-line paste: sanitized_text contains \n → multiple lines to process
# 2. Single-line paste into blank line: current_line_text empty → one line to process

But earlier code (line ~1220) shows single-line paste into existing line uses DIFFERENT logic:
if current_line_text:
    # Simple inline paste
    self.editor_text.text.insert(tk.INSERT, sanitized_text)
    return 'break'

The comment incorrectly suggests all cases use the same logic, when inline paste is handled separately.

---
---

#### code_vs_comment

**Description:** Comment in _highlight_current_statement claims 'Lines are displayed exactly as stored in program manager' but this contradicts the auto-numbering and formatting logic elsewhere in the code

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1590:
# Lines are displayed exactly as stored in program manager (see _refresh_editor),
# so char_start/char_end from runtime are directly usable as Tk text indices

But _refresh_editor() calls program.get_lines() which returns formatted lines, and the editor has auto-numbering logic that can modify line display. The comment oversimplifies the relationship between stored lines and displayed lines.

---
---

#### code_vs_comment

**Description:** Comment warns about maintenance risk due to code duplication

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method:
"MAINTENANCE RISK: This duplicates part of start()'s logic. If start() changes, this code may need to be updated to match. We only replicate the minimal setup needed (clearing halted flag, marking first line) while avoiding the full initialization that start() does:
  - runtime.setup() (rebuilds tables, resets PC) <- THIS is what we avoid
  - Creates new InterpreterState
  - Sets up Ctrl+C handler"

This indicates a design issue where logic is intentionally duplicated to avoid side effects, creating a fragile coupling between _execute_immediate() and the interpreter's start() method.

---
---

#### documentation_inconsistency

**Description:** DEF USR is listed in index but marked as not implemented, creating confusion about available features

**Affected files:**
- `docs/help/common/language/statements/def-usr.md`
- `docs/help/common/language/statements/index.md`

**Details:**
def-usr.md clearly states:
"⚠️ **Not Implemented**: This feature defines the starting address of assembly language subroutines and is not implemented in this Python-based interpreter."
"**Behavior**: Statement is parsed but no operation is performed"

However, index.md lists it under 'Functions' section without any indication it's not implemented:
"- [DEF USR](def-usr.md) - Define assembly language subroutine address"

The index should mark non-implemented features clearly, perhaps with a note or separate section.

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
CLI docs state 'The CLI includes a line editor accessed with the EDIT command' and references 'See: [EDIT Command](../../language/statements/edit.md)', but Curses docs make no mention of an EDIT command despite being a full-screen editor. The CLI description suggests EDIT is a command-mode feature, but it's unclear if this exists in CLI or if it's confused with the Curses full-screen editor.

---
---

#### documentation_inconsistency

**Description:** Find/Replace availability contradicts between feature list and UI-specific documentation

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/find-replace.md`

**Details:**
features.md under 'Tkinter GUI' states: 'Find and Replace - Search and replace text ({{kbd:find:tk}}/{{kbd:replace:tk}})'

But cli/find-replace.md states: 'The CLI backend does not have built-in Find/Replace commands' and recommends 'For built-in Find/Replace, use the Tk UI'

This is consistent. However, features.md under 'Web UI' states: 'Note: Find/Replace is not available in Web UI. Use the Tk UI for search/replace functionality.'

But features.md under 'Curses UI' also states: 'Note: Find/Replace is not available in Curses UI. Use the Tk UI for search/replace functionality.'

The inconsistency is that features.md doesn't mention CLI at all regarding Find/Replace availability, but documents it for Curses and Web. This creates an incomplete picture.

---
---

#### documentation_inconsistency

**Description:** Contradictory information about variable editing capability

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/variables.md`

**Details:**
docs/help/ui/curses/feature-reference.md states: 'Edit Variable Value (Not implemented)
⚠️ Variable editing is not available in Curses UI. You cannot directly edit values in the variables window. Use immediate mode commands to modify variable values instead.'

But docs/help/ui/curses/variables.md under 'Modifying Variables' states: '### Direct Editing Not Available
⚠️ **Not Implemented**: You cannot edit variable values directly in the variables window.'

Both agree it's not implemented, which is consistent. However, the variables.md document then provides extensive documentation about 'Window Controls' including 'Display Options' with keys like 'v: Toggle value truncation', 't: Toggle type display', etc., which suggests more functionality than just viewing.

---
---

#### documentation_inconsistency

**Description:** Save keyboard shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/files.md states: '1. Press **{{kbd:save:curses}}** to save (Ctrl+S unavailable - terminal flow control)'

But docs/help/ui/curses/quick-reference.md states: '**{{kbd:save:curses}}** | Save program (Ctrl+S unavailable - terminal flow control)'

Both mention Ctrl+S is unavailable, but use {{kbd:save:curses}} placeholder. The actual key should be documented explicitly (appears to be Ctrl+O based on context).

---
---

#### documentation_inconsistency

**Description:** Contradictory keyboard shortcuts for Find and Replace operations

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states:
- Find: {{kbd:find:tk}}
- Replace: {{kbd:replace:tk}}

But features.md states:
- Find text ({{kbd:find:tk}}): Opens Find dialog
- Replace text ({{kbd:replace:tk}}): Opens combined Find/Replace dialog
- Note: {{kbd:find:tk}} opens the Find dialog. {{kbd:replace:tk}} opens the Find/Replace dialog which includes both Find and Replace functionality.

This creates confusion about whether there are separate Find and Replace dialogs or a combined one.

---
---

#### documentation_inconsistency

**Description:** Contradictory information about program auto-save to localStorage

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/settings.md`

**Details:**
getting-started.md states in multiple places:
"**Note:** The Web UI uses browser downloads for saving program files to your computer. Auto-save of programs to browser localStorage is planned for a future release. (Settings ARE saved to localStorage - see [Settings](settings.md))"

And later:
"**Solution:** Auto-save of programs to localStorage is planned for a future release. Currently, you need to manually save your programs using File → Save."

But settings.md Settings Storage section describes localStorage as the DEFAULT storage method:
"### Local Storage (Default)

By default, settings are stored in your **browser's localStorage**."

The inconsistency is that getting-started.md says auto-save of PROGRAMS to localStorage is planned for the future, while settings.md talks about SETTINGS being stored in localStorage by default. However, the wording in getting-started.md could be clearer that it's specifically about programs, not settings.

---
---

## 🟡 Medium Severity

#### Documentation inconsistency

**Description:** Version number mismatch between setup.py and ast_nodes.py documentation

**Affected files:**
- `setup.py`
- `src/ast_nodes.py`

**Details:**
setup.py line 3: 'Setup script for MBASIC 5.21 Interpreter (version 0.99.0)'
setup.py line 5: 'Package version 0.99.0 reflects approximately 99% implementation status'
setup.py line 14: 'version="0.99.0"'

But ast_nodes.py line 3: 'Note: 5.21 refers to the Microsoft BASIC-80 language version, not this package version.'

The setup.py conflates MBASIC 5.21 (the language being interpreted) with package version 0.99.0, while ast_nodes.py correctly clarifies that 5.21 is the language version. This could confuse users about what version numbers mean.

---
---

#### code_vs_comment

**Description:** Comment in EOF() method describes ^Z handling for mode 'I' files but implementation checks file_info['mode'] == 'I' which may not align with how modes are stored

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment states: "Note: For binary input files (OPEN statement mode 'I'), respects ^Z (ASCII 26) as EOF marker (CP/M style). The 'I' mode from BASIC's OPEN statement is stored in file_info['mode']..."

Code checks: if file_info['mode'] == 'I':

The comment references execute_open() in interpreter.py which is not present in the provided files, making it impossible to verify if mode 'I' is actually stored in file_info['mode'] or if it's stored differently.

---
---

#### code_vs_comment

**Description:** Comment claims identifiers preserve original case but doesn't explain case-insensitive matching behavior

**Affected files:**
- `src/case_string_handler.py`

**Details:**
Comment in case_keepy_string method:
"# Identifiers always preserve their original case in display.
# Unlike keywords, which can be forced to a specific case policy,
# identifiers (variable/function names) retain their case as typed.
# This matches MBASIC 5.21 behavior where identifiers are case-insensitive
# for matching but preserve display case."

The comment describes case-insensitive matching but the code just returns original_text without any normalization or table lookup. The case-insensitive matching must happen elsewhere, but this isn't documented here, creating potential confusion about where case-insensitive comparison actually occurs.

---
---

#### Documentation inconsistency

**Description:** Contradictory information about storage location for SandboxedFileIO

**Affected files:**
- `src/file_io.py`

**Details:**
The FILE I/O ARCHITECTURE section says:
"Web UI uses SandboxedFileIO (server memory virtual filesystem)"

But the SandboxedFileIO class docstring says:
"Storage location: Python server memory (NOT browser localStorage)."

Then later in the same docstring:
"Acts as an adapter to backend.sandboxed_fs (SandboxedFileSystemProvider from src/filesystem/sandboxed_fs.py), which provides an in-memory virtual filesystem."

While these statements are consistent, the emphasis on "NOT browser localStorage" seems to contradict an unstated assumption. This may confuse readers who expect browser-side storage in a web UI.

---
---

#### Documentation inconsistency

**Description:** Duplicate two-letter error codes documented but potential ambiguity not fully explained

**Affected files:**
- `src/error_codes.py`

**Details:**
Module docstring says:
"Note: Some two-letter codes are duplicated (e.g., DD, CN, DF) across different numeric error codes. This matches the original MBASIC 5.21 specification where the two-letter codes alone are ambiguous - the numeric code is authoritative. All error handling in this implementation uses numeric codes for lookups, so the duplicate two-letter codes do not cause ambiguity in practice."

However, looking at ERROR_CODES dict:
10: ('DD', 'Duplicate definition')
61: ('DF', 'Disk full')
68: ('DD', 'Device unavailable')

The note mentions DD, CN, DF as duplicates, but:
- DD appears at codes 10 and 68 (confirmed)
- DF appears at codes 25 ('Device fault') and 61 ('Disk full') (confirmed)
- CN appears at codes 17 ('Can't continue') and 69 ('Communication buffer overflow') (confirmed)

The documentation is accurate but could be clearer about which specific codes are duplicated.

---
---

#### code_vs_comment

**Description:** Comment about numbered line editing says 'errors if missing' but code returns error tuples, not raising exceptions

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Comment says: "# If interactive_mode doesn't exist or is falsy, returns error: 'Cannot edit program lines in this mode'.
# If interactive_mode exists but required program methods are missing, returns error message."

But earlier comment says: "# - UI.program must have add_line() and delete_line() methods (validated, errors if missing)"

The phrase 'errors if missing' suggests exceptions, but the code returns (False, error_message) tuples. The later comment is more accurate. Minor terminology inconsistency.

---
---

#### code_vs_comment

**Description:** Comment claims EDIT command digits are 'silently ignored' but implementation doesn't handle digits at all

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~730 states:
'INTENTIONAL BEHAVIOR: When digits are entered, they are silently ignored (no output, no cursor movement, no error).'

However, the cmd_edit() implementation has no code to detect or handle digit input. Digits would fall through to the end of the if/elif chain and do nothing, but this is not 'intentional' handling - it's just absence of handling. The comment implies deliberate digit detection and suppression.

---
---

#### code_vs_comment

**Description:** Comment about ERL renumbering describes 'INTENTIONAL DEVIATION' but implementation may not match all cases

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~625 states:
'INTENTIONAL DEVIATION FROM MANUAL:
This implementation renumbers for ANY binary operator with ERL on left, including arithmetic operators (ERL + 100, ERL * 2, etc.), not just comparison operators.'

However, _renum_erl_comparison() only checks if expr is a BinaryOpNode with ERL on left and NumberNode on right. It doesn't verify the operator type at all. The comment claims it renumbers for 'ANY binary operator' but the code doesn't distinguish operators - it just checks structure. This is consistent with the comment's intent, but the comment could be clearer that no operator filtering happens.

---
---

#### code_vs_comment

**Description:** Comment in cmd_merge() says 'Error message from merge_from_file - format may vary' but then formats it with '?' prefix

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_merge() at line ~435:
Comment says: '# Error message from merge_from_file - format may vary'
Code does: 'print(f"?{error}")'

If the error format varies and might already include '?', adding another '?' could result in '??Error'. The comment acknowledges format variation but code doesn't handle it.

---
---

#### code_vs_comment

**Description:** Comment about return_stmt validation is incorrect - says values > len(statements) indicate deletion, but the actual check allows == len as valid

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 1027-1035 states:
"# return_stmt is 0-indexed offset into statements array.
# Valid range: 0 to len(statements) (inclusive).
# - 0 to len(statements)-1: Normal statement positions
# - len(statements): Special sentinel - GOSUB was last statement on line, so RETURN
#   continues at next line. This value is valid because PC can point one past the
#   last statement to indicate 'move to next line' (handled by statement_table.next_pc).
# Values > len(statements) indicate the statement was deleted (validation error).
if return_stmt > len(line_statements):  # Check for strictly greater than (== len is OK)"

The comment correctly describes the behavior, but then says 'Values > len(statements) indicate the statement was deleted'. This is accurate - the code checks 'return_stmt > len(line_statements)' which means values strictly greater than len indicate deletion. The comment is actually correct here.

---
---

#### code_vs_comment

**Description:** Comment describes RESUME 0 as distinct from RESUME, but code treats them identically

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1088 states:
"# RESUME or RESUME 0 - retry the statement that caused the error
# Note: MBASIC allows both 'RESUME' and 'RESUME 0' as equivalent syntactic forms.
# Parser preserves the distinction (None vs 0) for source text regeneration,
# but runtime execution treats both identically."

However, the code checks:
"if stmt.line_number is None or stmt.line_number == 0:"

This means the code correctly treats None and 0 identically, matching the comment. But the comment's phrasing "Parser preserves the distinction (None vs 0)" could be clearer about what distinction is preserved (syntactic only, not semantic).

---
---

#### code_vs_comment

**Description:** Comment about RUN without args says 'restart from beginning' but code sets halted=True

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1449 states:
"# RUN without arguments - CLEAR + restart from beginning
if hasattr(self, 'interactive_mode') and self.interactive_mode:
    self.interactive_mode.cmd_run()
else:
    # In non-interactive context, restart from beginning
    # Note: RUN without args sets halted=True to stop current execution.
    # The caller (e.g., UI tick loop) should detect halted=True and restart
    # execution from the beginning if desired. This is different from
    # RUN line_number which sets halted=False to continue execution inline.
    self.runtime.clear_variables()
    self.runtime.halted = True"

The comment says "restart from beginning" but the code sets halted=True, which stops execution. The nested comment clarifies that the CALLER should restart, but the top-level comment is misleading. The code is correct (halted=True signals the caller), but the comment should be clearer.

---
---

#### code_vs_comment

**Description:** Comment about INPUT state machine mentions input_file_number but doesn't explain its purpose clearly

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1625 states:
"State machine for keyboard input (file input is synchronous):
1. If state.input_buffer has data: Use buffered input (from provide_input())
2. Otherwise: Set state.input_prompt, input_variables, input_file_number and return (pauses execution)
3. UI calls provide_input() with user's input line
4. On next tick(), buffered input is used (step 1) and input_prompt/input_variables are cleared

File input bypasses the state machine and reads synchronously because file data is
immediately available (blocking I/O), unlike keyboard input which requires async
handling in the UI event loop."

The comment mentions setting input_file_number but doesn't explain what it's for. Looking at the code:
"self.state.input_file_number = None  # None indicates keyboard input (not file)"

This suggests input_file_number distinguishes keyboard vs file input, but the comment doesn't explain why this distinction is needed in the state. The code sets it but the comment doesn't document its purpose.

---
---

#### code_vs_comment

**Description:** Comment about DELETE vs NEW differs from actual behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1577 states:
"DELETE           - Delete all lines (same as NEW but keeps variables)"

However, looking at execute_new() at line ~1565:
"# Clear variables and arrays
self.runtime.clear_variables()
self.runtime.clear_arrays()"

And execute_delete() doesn't have special handling for 'delete all' that preserves variables. The comment suggests DELETE (no args) keeps variables while NEW doesn't, but both clear variables. This needs verification - either the comment is wrong or the code is missing the variable preservation for DELETE.

---
---

#### Code vs Documentation inconsistency

**Description:** Documentation claims Python's input() preserves leading/trailing spaces, but this is only partially accurate

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/console.py`

**Details:**
base.py states: 'console: Python input() strips trailing newline only (preserves spaces)'
console.py states: 'Note: Python's input() strips only the trailing newline, preserving leading/trailing spaces.'

However, Python's input() does strip the trailing newline, and terminal behavior may strip other whitespace depending on the platform. The documentation oversimplifies this.

---
---

#### Code vs Documentation inconsistency

**Description:** input_char() documentation says blocking parameter is ignored, but method signature accepts it

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Method signature: 'def input_char(self, blocking=True):'
Docstring states: 'NOTE: This parameter is accepted for interface compatibility but is ignored in the web UI implementation.'

The docstring also states: 'The blocking parameter is ignored.' twice in different sections, which is redundant and suggests unclear documentation evolution.

---
---

#### Code vs Documentation inconsistency

**Description:** input_line() documentation acknowledges limitation but doesn't match implementation comment

**Affected files:**
- `src/iohandler/curses_io.py`

**Details:**
Docstring states: 'Note: Current implementation does NOT preserve trailing spaces as documented in base class. curses getstr() strips trailing whitespace (spaces, tabs, newlines). Leading spaces are preserved.'

However, the implementation just calls self.input(prompt) which uses getstr(), and there's no code attempting to preserve any spaces. The comment suggests awareness of the limitation but no attempt to work around it, yet base.py describes this as 'accepted limitation of underlying platform APIs'.

---
---

#### code_vs_comment

**Description:** Comment claims at_end_of_line() does NOT check for COLON or comment tokens, but the method description contradicts this and suggests using at_end_of_statement() instead

**Affected files:**
- `src/parser.py`

**Details:**
at_end_of_line() docstring says:
"Important: This does NOT check for COLON or comment tokens. For statement parsing,
use at_end_of_statement() instead to properly stop at colons and comments."

But at_end_of_statement() docstring says:
"A statement ends at:
- End of line (NEWLINE or EOF)
- Statement separator (COLON) - allows multiple statements per line
- Comment (REM, REMARK, or APOSTROPHE) - everything after is ignored"

The comment in at_end_of_line() warns about NOT checking COLON/comments, but then says to use at_end_of_statement() which DOES check them. This creates confusion about when to use which method.

---
---

#### code_vs_comment

**Description:** Comment about separator count vs expression count in parse_print() has confusing logic explanation

**Affected files:**
- `src/parser.py`

**Details:**
parse_print() has this comment:
"# Add newline if there's no trailing separator
# Separator count vs expression count:
# - If separators < expressions: no trailing separator, add newline
# - If separators >= expressions: has trailing separator, no newline added
# Examples: 'PRINT A;B;C' has 2 separators for 3 items (no trailing sep, adds \n)
#           'PRINT A;B;C;' has 3 separators for 3 items (trailing sep, no \n)"

Then the code does:
if len(separators) < len(expressions):
    separators.append('\n')

The logic is correct, but the comment explanation is backwards from typical thinking. Usually we think 'if there's a trailing separator, don't add newline' rather than 'if separators < expressions'. The comment tries to explain both perspectives but may confuse readers.

---
---

#### code_vs_comment

**Description:** Comment describes LINE_INPUT token behavior inconsistently with actual implementation

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() method around line 1050:

Comment states: "Note: The lexer tokenizes LINE keyword as LINE_INPUT token both when standalone (LINE INPUT statement) and when used as modifier (INPUT...LINE). The parser distinguishes these cases by context - LINE INPUT is a statement, INPUT...LINE uses LINE as a modifier within the INPUT statement."

However, the code checks for TokenType.LINE_INPUT in both contexts:
- line_mode = False
- if self.match(TokenType.LINE_INPUT):
    line_mode = True
    self.advance()

This suggests the lexer produces the same token type for both cases, which the comment confirms. The comment is accurate but could be clearer about why this design choice was made.

---
---

#### Documentation inconsistency

**Description:** base.py docstring lists 'BatchBackend' as a potential future backend type, but this contradicts the comment's own note that 'headless' execution seems contradictory to UIBackend purpose. The documentation is unclear about whether batch/non-interactive execution belongs in UIBackend abstraction.

**Affected files:**
- `src/ui/base.py`
- `src/ui/cli_keybindings.json`
- `src/ui/curses_keybindings.json`

**Details:**
base.py docstring says:
"Future/potential backend types (not yet implemented):
- WebBackend: Browser-based interface
- BatchBackend: Non-interactive execution mode for running programs from command line
           (Note: 'headless' typically means no UI, which seems contradictory to UIBackend purpose;
           batch/non-interactive execution may be better handled outside the UIBackend abstraction)"

This self-contradictory documentation suggests uncertainty about design direction.

---
---

#### Code vs Documentation inconsistency

**Description:** auto_save.py module docstring claims 'Never overwrites user-saved files without permission' and 'Offers recovery on startup if autosave is newer', but the code only provides checking functions (is_autosave_newer, format_recovery_prompt). The actual recovery UI/permission logic is not implemented in this module.

**Affected files:**
- `src/ui/auto_save.py`

**Details:**
Module docstring claims:
"Provides auto-save functionality with Emacs-inspired naming (#filename#):
- Saves to centralized temp directory (~/.mbasic/autosave/) automatically
- Uses Emacs-style #filename# naming convention
- Never overwrites user-saved files without permission
- Offers recovery on startup if autosave is newer
- Cleans up old autosaves"

But the code only provides:
- is_autosave_newer() - checking function
- format_recovery_prompt() - message generation
- load_autosave() - loading function

The actual 'never overwrites without permission' and 'offers recovery on startup' features require UI integration not present in this module. The module provides building blocks but doesn't implement the promised behavior.

---
---

#### Code vs Documentation inconsistency

**Description:** The footer displays keyboard shortcuts using constants from keybindings module, but the actual key handling in keypress() uses different constants (ESC_KEY, ENTER_KEY, SETTINGS_KEY, etc.) that are imported but not defined in the shown code. The relationship between these constants and the actual key strings is unclear.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Footer creation:
"footer_text = urwid.Text(
    f'↑↓ {key_to_display(ENTER_KEY)}=OK  '
    f'{key_to_display(ESC_KEY)}/{key_to_display(SETTINGS_KEY)}=Cancel  '
    f'{key_to_display(SETTINGS_APPLY_KEY)}=Apply  '
    f'{key_to_display(SETTINGS_RESET_KEY)}=Reset',
    align='center'
)"

keypress() method:
"if key == ESC_KEY or key == SETTINGS_KEY:
    self._on_cancel()
    return None
elif key == ENTER_KEY:
    self._on_ok()
    return None
elif key == SETTINGS_APPLY_KEY:
    self._on_apply()
    return None
elif key == SETTINGS_RESET_KEY:
    self._on_reset()
    return None"

The constants are imported from 'src.ui.keybindings' but that module is not shown, making it impossible to verify the key mappings are correct or consistent with the JSON keybinding files.

---
---

#### code_vs_comment

**Description:** Comment claims bare identifiers are rejected, but implementation only catches specific cases

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _check_line_syntax():
"# Reject bare identifiers (the parser treats them as implicit REMs for
# old BASIC compatibility, but in the editor we want to be stricter).
# Note: This only catches bare identifiers followed by EOF or COLON (e.g., 'foo' or 'foo:').
# Bare identifiers followed by other tokens (e.g., 'foo + bar') will be caught by the
# parser as syntax errors, so this check is sufficient for editor validation."

The comment claims the check is 'sufficient' but then later in the code:
if isinstance(result, RemarkStatementNode):
    # Check if this was an actual REM keyword or implicit REM
    if tokens and tokens[0].type not in (TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
        return (False, f"Invalid statement: '{tokens[0].value}' is not a BASIC keyword")

This second check suggests the first check is NOT sufficient, contradicting the comment.

---
---

#### internal_inconsistency

**Description:** Inconsistent handling of line number width limits

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress() method for auto-numbering:
if next_num >= 99999 or attempts > 10:
    # Show error about no room

But in _format_line() and _parse_line_number(), there's no enforcement of 99999 as a maximum. The line_num_str = f"{line_num}" will format any integer, allowing line numbers > 99999. This creates an inconsistency where auto-numbering stops at 99999 but manual entry could exceed it.

---
---

#### code_vs_comment

**Description:** Comment claims Interpreter is created once and never recreated, but the lifecycle description is confusing about what gets recreated

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~189 says:
# Interpreter Lifecycle:
# Created ONCE here in __init__ and reused throughout the session.
# The interpreter object itself is NEVER recreated - the same instance is used
# for the lifetime of the UI session.
# Note: The immediate_io handler created here is temporary - ImmediateExecutor
# will be recreated in start() with a fresh OutputCapturingIOHandler, but that
# new executor will receive this same interpreter instance (not a new interpreter).

This is internally consistent, but the comment at line ~200 says:
# ImmediateExecutor Lifecycle:
# Created here with temporary IO handler (to ensure attribute exists),
# then recreated in start() with a fresh OutputCapturingIOHandler.
# Note: The interpreter (self.interpreter) is created once here and reused.
# Only the executor and its IO handler are recreated in start().

The confusion is that the Interpreter is created with immediate_io, but then ImmediateExecutor is recreated with a NEW immediate_io in start(). This means the Interpreter's IO handler becomes stale/unused after start() is called, which is not clearly explained.

---
---

#### code_vs_comment

**Description:** Comment in _update_stack_window describes statement offset as 0-based but doesn't clarify if this matches actual implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1070:
"# Show statement-level precision for GOSUB return address
# return_stmt is statement offset (0-based index): 0 = first statement, 1 = second, etc.
return_stmt = entry.get('return_stmt', 0)
line = f"{indent}GOSUB from line {entry['from_line']}.{return_stmt}""

The comment clearly states return_stmt is 0-based (0 = first statement), which matches the code using .get('return_stmt', 0). This is consistent.

---
---

#### code_vs_comment

**Description:** Comment in _run_program states 'Immediate mode status remains disabled during execution' but code calls _update_immediate_status() multiple times during execution

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1235:
"# Immediate mode status remains disabled during execution - program output shows in output window"

But throughout _execute_tick() method (lines 1240-1330), _update_immediate_status() is called:
- Line ~1260: after runtime error
- Line ~1270: after program completion
- Line ~1277: after paused/breakpoint
- Line ~1310: after user program error

The comment suggests immediate status is disabled, but code actively updates it during execution.

---
---

#### code_vs_comment

**Description:** Comment in _get_input_for_interpreter describes ESC behavior incorrectly

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says: 'Note: This sets stopped=True similar to a BASIC STOP statement, but the semantics differ - STOP is a deliberate program action, while ESC is user cancellation'

However, the code sets both stopped=True AND running=False:
self.runtime.stopped = True
self.running = False

The comment implies only stopped is set, but running is also cleared. This is important because it affects whether execution can be continued.

---
---

#### code_vs_comment

**Description:** Comment in _execute_immediate references duplicate code that should be extracted

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says:
'# Need to create the CapturingIOHandler class inline
# (duplicates definition in _run_program - consider extracting to shared location)'

But then the code does:
'# Import shared CapturingIOHandler
from .capturing_io_handler import CapturingIOHandler'

The comment suggests the class needs to be defined inline and duplicated, but the code actually imports it from a shared module. The comment is outdated.

---
---

#### code_vs_comment

**Description:** Comment in _execute_immediate about interpreter.start() contradicts typical execution flow

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says:
'# NOTE: Don't call interpreter.start() here - the immediate executor already called it if needed (e.g., 'RUN 120' called interpreter.start(start_line=120) to set PC to line 120). Calling it again would reset PC to the beginning.'

This suggests the immediate executor calls interpreter.start(), but then the code only initializes InterpreterState if it doesn't exist. The logic seems inconsistent - if immediate executor already called start(), why would we need to check if state exists and initialize it? This suggests either:
1. The comment is wrong about what immediate executor does
2. The code is missing proper initialization
3. The interaction between immediate executor and interpreter needs clarification

---
---

#### code_vs_comment_conflict

**Description:** Comments claim different purposes for loading same JSON files but both load for similar reasons

**Affected files:**
- `src/ui/keybinding_loader.py`
- `src/ui/help_macros.py`

**Details:**
keybinding_loader.py comment at line ~28 states:
"Note: This loads keybindings for runtime event handling (binding keys to actions). help_macros.py loads the same JSON files but for macro expansion in help content (e.g., {{kbd:run}} -> '^R'). Both read the same data but use it differently: KeybindingLoader for runtime key event handling, HelpMacros for documentation display."

help_macros.py comment at line ~28 states:
"Note: This loads the same keybinding JSON files as keybinding_loader.py, but for a different purpose: macro expansion in help content (e.g., {{kbd:run}} -> '^R') rather than runtime event handling. This is separate from help_widget.py which uses hardcoded keys for navigation within the help system itself."

Both comments correctly identify that they load the same JSON for different purposes, but the help_macros.py comment adds information about help_widget.py using hardcoded keys, which creates confusion when combined with the help_widget.py comment that claims HelpMacros doesn't affect help navigation. The relationship between these three components could be documented more clearly in one place.

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

However, tk_keybindings.json only documents Ctrl+F for inpage_search, missing Return (next match) and Escape (close search bar) which are implemented in lines 113-115.

---
---

#### code_vs_comment

**Description:** Comment at line 143 references 'see lines 293-297' but those lines are actually at different location in the code

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line 143: 'Note: immediate_history and immediate_status are always None in Tk UI (see lines 293-297)'
Actual location: The code setting immediate_history and immediate_status to None appears around lines 293-297 in the provided snippet, but this cross-reference may become incorrect if code is edited.

---
---

#### code_vs_comment

**Description:** Comment about Ctrl+I binding location conflicts with actual implementation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line 442: Comment in _create_menu() says '# Note: Ctrl+I is bound directly to editor text widget in start() (not root window)
        # to prevent tab key interference - see editor_text.text.bind('<Control-i>', ...)'
Line 207 in start(): 'self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)'
The comment is accurate, but it's placed in _create_menu() method far from where the binding actually occurs, making it easy to miss during maintenance.

---
---

#### code_vs_comment

**Description:** Comment claims _on_key_press allows backspace/delete because they 'modify text via deletion, not by inserting printable characters', but this is misleading - the real reason is they are control characters that need special handling for text editing

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1180:
# Allow backspace and delete - these modify text via deletion, not by inserting
# printable characters, so they pass validation. Note: These are control characters
# but we allow them specifically. Other control characters are blocked later.

The comment suggests backspace/delete 'pass validation' but the code explicitly allows them BEFORE validation (char_code in (8, 127)). The comment is confusing about the flow.

---
---

#### code_vs_comment

**Description:** Comment in _on_paste says 'Single line paste - check if we're in the middle of an existing line' but the code checks if current_line_text has content, not if cursor is 'in the middle'

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1220:
# Single line paste - check if we're in the middle of an existing line

But code checks:
if current_line_text:
    # If current line has content (not blank), do simple inline paste

The cursor could be at the start or end of the line, not necessarily 'in the middle'. Comment is imprecise.

---
---

#### code_vs_comment

**Description:** Comment in _smart_insert_line says 'DON'T save to program yet' because line has no statement, but this contradicts the general pattern where _save_editor_to_program is called after modifications

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1530:
# DON'T save to program yet - the line only has a line number with no statement,
# so _save_editor_to_program() will skip it (only saves lines with statements).
# Just position the cursor on the new line so user can start typing. The line
# will be saved to program when:
# 1. User types a statement and triggers _on_key_release -> _save_editor_to_program()
# 2. User switches focus or saves the file

This is inconsistent with other places where _save_editor_to_program() is called immediately after editor modifications (e.g., after _on_enter_key). The comment explains the reasoning but it's still an inconsistency in the pattern.

---
---

#### code_vs_comment

**Description:** Comment in _execute_tick says 'Output is routed to output pane via TkIOHandler' but this is obvious from the code and doesn't add value

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1620:
# Output is routed to output pane via TkIOHandler

This comment appears after the tick() call but doesn't explain anything about the tick() call itself. It's a statement of fact about the architecture that's already clear from cmd_run where TkIOHandler is set up.

---
---

#### code_vs_comment

**Description:** Comment in cmd_cont says 'The interpreter moves NPC to PC when STOP is executed' but this is implementation detail of interpreter.py, not tk_ui.py - comment is in wrong place

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1900:
# The interpreter moves NPC to PC when STOP is executed (see execute_stop()
# in interpreter.py). CONT simply clears the stopped/halted flags and resumes
# tick-based execution, which continues from the PC position.

This comment explains interpreter internals but is located in the UI layer. It would be better placed in interpreter.py near execute_stop().

---
---

#### documentation_inconsistency

**Description:** Inconsistent documentation about has_work() usage location

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _execute_immediate(): "Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command). This is the only location in tk_ui.py that calls has_work()."

This comment makes a strong claim about being the 'only location' but doesn't reference where else has_work() might be called or why this constraint exists. Without seeing the full file, this claim cannot be verified.

---
---

#### code_vs_comment

**Description:** Comment about PC restoration contradicts the need for manual state management

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _continue_execution() method:
"# The interpreter maintains the execution position in PC (moved by STOP).
# When CONT is executed, tick() will continue from runtime.pc, which was
# set by execute_stop() to point to the next statement after STOP.
# No additional position restoration is needed here."

But then in _execute_immediate(), there's complex manual PC management:
"# If statement set NPC (like RUN/GOTO), move it to PC
# This is what the tick loop does after executing a statement
if self.runtime.npc is not None:
    self.runtime.pc = self.runtime.npc
    self.runtime.npc = None"

These comments suggest inconsistent understanding of when PC management is automatic vs manual.

---
---

#### documentation_inconsistency

**Description:** The _redraw() docstring says 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas)' and references _parse_line_number() for 'regex-based extraction logic that validates line number format (requires whitespace or end-of-string after the number)', but this same information is repeated in multiple places with slightly different wording, creating potential for inconsistency.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_redraw() docstring: 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas). See _parse_line_number() for the regex-based extraction logic that validates line number format (requires whitespace or end-of-string after the number).'

_parse_line_number() has its own detailed comment: 'Match line number followed by whitespace OR end of string (both valid).'

Class docstring: 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas).'

The regex pattern requirement is documented in _parse_line_number() but also mentioned in _redraw()'s docstring. If the regex changes, both need updating.

---
---

#### code_vs_comment

**Description:** Comment about CodeMirror maintaining scroll position is not verifiable from code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~831:
# Note: CodeMirror maintains scroll position automatically when dialog closes

This claims CodeMirror has automatic behavior, but there's no code shown that configures or relies on this. The comment may be outdated if CodeMirror version or configuration changed.

---
---

#### documentation_inconsistency

**Description:** Help system documentation contradicts code implementation about how help is served

**Affected files:**
- `docs/help/README.md`
- `src/ui/web_help_launcher.py`

**Details:**
README.md states: "Help content is built using MkDocs and served locally at `http://localhost/mbasic_docs` for the Tk and Web UIs, while the CLI and Curses UIs use built-in markdown rendering."

However, web_help_launcher.py shows:
- HELP_BASE_URL = "http://localhost/mbasic_docs" (matches)
- But the deprecated WebHelpLauncher class uses port 8000: self.server_port = 8000 and constructs URLs like "http://localhost:8000"
- The code has conflicting approaches: one using a pre-existing web server at /mbasic_docs, another starting its own server on port 8000

The migration comment in web_help_launcher.py says "The help site is already built and served at http://localhost/mbasic_docs" but the deprecated class still has code to build and serve help on port 8000.

---
---

#### documentation_inconsistency

**Description:** Documentation references non-existent BASIC statements

**Affected files:**
- `docs/help/common/examples/loops.md`

**Details:**
The loops.md documentation states:
"**Note:** MBASIC 5.21 does not have EXIT FOR or EXIT WHILE statements (those were added in later BASIC versions). GOTO is the standard way to exit loops early in BASIC-80."

This is good clarification, but then the "Breaking Out of Loops" section title and content might mislead users into thinking there's a built-in break mechanism. The note clarifies this, but the section organization could be clearer that GOTO is the only option, not an alternative to other methods.

---
---

#### documentation_inconsistency

**Description:** Inconsistent Control-C behavior documentation

**Affected files:**
- `docs/help/common/language/functions/input_dollar.md`
- `docs/help/common/language/functions/inkey_dollar.md`

**Details:**
Both INPUT$ and INKEY$ document Control-C behavior, but with slightly different wording:

INKEY$: 'Note: Control-C behavior varied in original implementations. In MBASIC 5.21 interpreter mode, Control-C would terminate the program. This implementation passes Control-C through (CHR$(3)) for program detection and handling, allowing programs to detect and handle it explicitly.'

INPUT$: 'Note: Control-C behavior: This implementation passes Control-C through (CHR$(3)) for program detection and handling, allowing programs to detect and handle it explicitly.'

The INPUT$ version is shorter and doesn't mention the historical MBASIC 5.21 behavior. For consistency, both should provide the same level of detail about the implementation choice.

---
---

#### documentation_inconsistency

**Description:** DEF FN documentation claims multi-character function names are an extension over MBASIC 5.21, but DEFINT/SNG/DBL/STR documentation is from original MBASIC 5.21 and doesn't mention this is an extension

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
def-fn.md states:
"**Original MBASIC 5.21**: Function names were limited to a single character after FN"
"**This implementation (extension)**: Function names can be multiple characters"

However, defint-sng-dbl-str.md appears to be original MBASIC 5.21 documentation without noting whether the implementation differs. The DEF statements should have consistent documentation about what is original vs extended.

---
---

#### documentation_inconsistency

**Description:** END documentation states files remain closed after CONT, but FOR-NEXT loop termination test description may be confusing about when test occurs

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/for-next.md`

**Details:**
end.md clearly states:
"Can be continued with CONT (execution resumes at next statement after END)"
"Note: Files remain closed if CONT is used after END"

for-next.md states:
"The termination test happens AFTER each increment/decrement at the NEXT statement"
Then gives example: "FOR I = 1 TO 10 executes with I=1,2,3,...,10 (11 iterations)"

This is contradictory - if there are 11 iterations mentioned, but the loop executes with I=1 through 10, that's only 10 iterations. The documentation should clarify that the 11th iteration is when the test fails and loop exits.

---
---

#### documentation_inconsistency

**Description:** FIELD documentation warns against using FIELDed variables in INPUT/LET, but GET documentation doesn't mention this critical restriction

**Affected files:**
- `docs/help/common/language/statements/field.md`
- `docs/help/common/language/statements/get.md`

**Details:**
field.md states:
"**Note:** Do not use a FIELDed variable name in an INPUT or LET statement. Once a variable name is FIELDed, it points to the correct place in the random file buffer. If a subsequent INPUT or LET statement with that variable name is executed, the variable's pointer is moved to string space."

get.md shows example using FIELD variables but doesn't repeat this warning. Since GET and FIELD are commonly used together, both should mention this restriction.

---
---

#### documentation_inconsistency

**Description:** FOR-NEXT loop iteration count explanation is mathematically incorrect

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
for-next.md states:
"FOR I = 1 TO 10 executes with I=1,2,3,...,10 (11 iterations). After I=10 executes, NEXT increments to 11, test fails (11 > 10), loop exits."

This is incorrect. If the loop executes with I=1,2,3,...,10, that is exactly 10 iterations, not 11. The increment to 11 happens after the 10th iteration completes, but that's not an 11th iteration - it's the termination test. The documentation should say '(10 iterations)' not '(11 iterations)'.

---
---

#### documentation_inconsistency

**Description:** INPUT and INPUT# have different levels of detail about data parsing behavior

**Affected files:**
- `docs/help/common/language/statements/input.md`
- `docs/help/common/language/statements/input_hash.md`

**Details:**
input.md provides basic information about comma-separated values and quotes.

input_hash.md provides extensive detail:
"With numeric values, leading spaces, carriage returns and line feeds are ignored. The first character encountered that is not a space, carriage return or line feed is assumed to be the start of a number..."

INPUT (keyboard) should have similar detail about how it parses input, or both should reference a common parsing rules section.

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

**Description:** Inconsistent implementation notes for printer-related commands

**Affected files:**
- `docs/help/common/language/statements/llist.md`
- `docs/help/common/language/statements/lprint-lprint-using.md`

**Details:**
LLIST states: 'Not Implemented: This feature requires line printer hardware'
LPRINT states: 'Not Implemented: This feature requires line printer hardware'
Both have implementation notes, but the wording and detail level differ. LLIST provides more detailed alternatives.

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

**Description:** Inconsistent implementation note formatting and detail level

**Affected files:**
- `docs/help/common/language/statements/width.md`
- `docs/help/common/language/statements/wait.md`

**Details:**
WAIT.md has detailed implementation note with sections: 'Not Implemented', 'Behavior', 'Why', 'Limitations', 'Alternative', 'Historical Reference'

WIDTH.md has similar note but says 'Emulated as No-Op' instead of 'Not Implemented', and has slightly different structure.

Both should use consistent terminology and structure for implementation notes.

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

This seems to contradict itself - it says full names are used (COUNT vs COUNTER are different) but then says case doesn't matter (COUNT = Count). The distinction between 'name significance' and 'case sensitivity' needs clarification.

---
---

#### documentation_inconsistency

**Description:** RESUME documentation has inconsistent formatting in syntax section

**Affected files:**
- `docs/help/common/language/statements/resume.md`

**Details:**
The syntax section shows:

```basic
RESUME                  ' Retry the statement that caused the error
RESUME NEXT             ' Continue at the statement after the error
RESUME <line number>    ' Continue at a specific line number
```

But the main syntax at the top shows:

```
RESUME
RESUME NEXT
RESUME <line number>
```

The first has comments, the second doesn't. This is inconsistent with other documentation files which typically only show syntax without inline comments in the syntax block.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for stopping AUTO mode

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`

**Details:**
CLI docs say 'Press {{kbd:stop:cli}} to stop AUTO mode' while Curses docs say 'Exit AUTO mode with {{kbd:continue:curses}} or by typing a line number manually'. These appear to be different key bindings for the same action (stopping AUTO mode), but use different placeholder names (stop vs continue).

---
---

#### documentation_inconsistency

**Description:** Inconsistent Web UI file storage description

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
Compatibility guide provides detailed Web UI limitations: '50 file limit, 1MB per file' and 'Must be simple names (no slashes, no paths)' and 'Automatically uppercased by the virtual filesystem (CP/M style)'. Extensions guide only mentions: '50 file limit maximum, 1MB per file maximum, No path support (simple filenames only)' but omits the uppercasing behavior. The uppercasing is an important compatibility detail that should be in both docs or cross-referenced.

---
---

#### documentation_inconsistency

**Description:** Incomplete semantic analyzer optimization list

**Affected files:**
- `docs/help/mbasic/architecture.md`

**Details:**
Architecture doc lists '18 distinct optimizations' and provides detailed descriptions for optimizations 1-18. However, the numbering and grouping ('Core Optimizations (1-8)' and 'Advanced Optimizations (9-18)') suggests a specific structure, but optimization #18 'Uninitialized Variable Detection' is described as 'Warns about use-before-assignment' which is more of a static analysis feature than an optimization. This may be a categorization inconsistency.

---
---

#### documentation_inconsistency

**Description:** Inconsistent description of WIDTH statement support

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
Compatibility doc states 'WIDTH 80 ... Accepted (no-op)' and 'WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.' Extensions doc doesn't mention WIDTH at all. Since WIDTH is a compatibility feature (parsed but no-op), it should be mentioned in the extensions doc's compatibility section or feature comparison table.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation between documents

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/getting-started.md`

**Details:**
features.md uses template notation: '{{kbd:run:curses}}', '{{kbd:save:curses}}', '{{kbd:open:curses}}', '{{kbd:help:curses}}', '{{kbd:quit:curses}}'

getting-started.md uses the same template notation: '{{kbd:run:curses}}', '{{kbd:save:curses}}', '{{kbd:open:curses}}', '{{kbd:help:curses}}', '{{kbd:quit:curses}}'

However, features.md also references '{{kbd:step_line:curses}}' for Stack window which is inconsistent with the pattern (should likely be just a key name, not an action_ui pattern).

---
---

#### documentation_inconsistency

**Description:** User interface count mismatch

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/index.md`

**Details:**
features.md states under 'Choosing a User Interface': 'MBASIC supports four interfaces' and lists: Curses UI, CLI Mode, Tkinter GUI, Web UI

index.md states: 'Choice of user interfaces (CLI, Curses, Tkinter)' - only listing three interfaces and omitting Web UI.

This is an inconsistency in the feature count and list.

---
---

#### documentation_inconsistency

**Description:** Settings commands not listed in CLI features

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/settings.md`

**Details:**
cli/settings.md documents SHOWSETTINGS and SETSETTING commands as available in CLI mode.

However, features.md under 'Program Control' -> 'Direct Commands' does not list SHOWSETTINGS or SETSETTING among the available commands (RUN, LIST, NEW, SAVE, LOAD, DELETE, RENUM, AUTO).

This creates an incomplete picture of available CLI commands.

---
---

#### documentation_inconsistency

**Description:** String memory management implementation details not referenced in features

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`

**Details:**
features.md under 'Compiler Features' -> 'Semantic Analyzer' lists 18 optimizations but does not mention string memory management or garbage collection.

string-allocation-and-garbage-collection.md provides extensive documentation on 'CP/M Era MBASIC String Allocation and Garbage Collection' including memory architecture, allocation process, and garbage collection algorithm.

features.md should reference this implementation detail, especially since it affects performance and compatibility with original MBASIC behavior.

---
---

#### documentation_inconsistency

**Description:** Games library reference inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/index.md`

**Details:**
cli/index.md prominently features: '🎮 Games Library
Browse and run classic BASIC games:
- **[Games Library](../../../library/games/index.md)** - 113 classic CP/M era games ready to run!'

features.md makes no mention of the games library at all, despite it being a significant feature of the distribution.

This should be mentioned in features.md under a 'Included Content' or 'Examples' section.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Variables Window

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/quick-reference.md under 'Global Commands' states: '**Menu only** | Toggle variables window'

But docs/help/ui/curses/feature-reference.md under 'Variable Inspection' states: 'Variables Window (Menu only)' and 'Open/close the variables inspection window showing all program variables and their current values. **Note:** Access via menu only - no keyboard shortcut assigned.'

However, docs/help/ui/curses/variables.md shows: 'Press `{{kbd:toggle_variables:curses}}` to open the variables window.'

This is contradictory - either there is a keyboard shortcut or there isn't.

---
---

#### documentation_inconsistency

**Description:** Variable window sort modes inconsistency

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/variables.md states: 'Press `s` to cycle through sort orders:
- **Accessed**: Most recently accessed (read or written) - shown first
- **Written**: Most recently written to - shown first
- **Read**: Most recently read from - shown first
- **Name**: Alphabetical by variable name'

But docs/help/ui/curses/quick-reference.md states: '**s** | Cycle sort mode (Accessed → Written → Read → Name)'

And adds: '**Sort Modes:**
- **Accessed**: Most recently accessed (read or written) - default, newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name - A to Z'

The quick-reference adds 'default' and 'newest first' qualifiers that are missing from variables.md, and specifies 'A to Z' for Name sort which variables.md doesn't mention.

---
---

#### documentation_inconsistency

**Description:** Cut/Copy/Paste keyboard shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/feature-reference.md states: 'Cut/Copy/Paste (Not implemented)
Standard clipboard operations are not available in the Curses UI due to keyboard shortcut conflicts:
- **{{kbd:stop:curses}}** - Used for Stop/Interrupt (cannot be used for Cut)
- **{{kbd:continue:curses}}** - Terminal signal to exit program (cannot be used for Copy)
- **{{kbd:save:curses}}** - Used for Save File (cannot be used for Paste; {{kbd:save:curses}} is reserved by terminal for flow control)'

But docs/help/ui/curses/quick-reference.md states: '**Note:** Cut/Copy/Paste are not available - use your terminal's native clipboard (typically Shift+Ctrl+C/V or mouse selection).'

The feature-reference provides detailed explanation of WHY these aren't available (keyboard conflicts), while quick-reference just states they aren't available. The quick-reference should reference the feature-reference for details.

---
---

#### documentation_inconsistency

**Description:** Incomplete placeholder documentation vs detailed UI-specific documentation

**Affected files:**
- `docs/help/ui/common/running.md`
- `docs/help/ui/curses/running.md`

**Details:**
docs/help/ui/common/running.md is marked as 'PLACEHOLDER - Documentation in progress' and says 'For UI-specific instructions: - CLI: `docs/help/ui/cli/` - Curses: `docs/help/ui/curses/running.md`'

However, docs/help/ui/curses/running.md is a complete, detailed guide with sections on Running a Program, Output Window, Interactive Programs, Stopping a Program, etc.

The common/running.md placeholder should either be completed or removed, as it provides no value when UI-specific docs are complete.

---
---

#### documentation_inconsistency

**Description:** Window controls documented but implementation status unclear

**Affected files:**
- `docs/help/ui/curses/variables.md`

**Details:**
docs/help/ui/curses/variables.md under 'Window Controls' documents:
'### Resize and Position
- **Ctrl+Arrow**: Move window
- **Alt+Arrow**: Resize window
- **Ctrl+M**: Maximize/restore
- **{{kbd:stop:curses}}**: Close window'

And under 'Display Options':
'- **v**: Toggle value truncation
- **t**: Toggle type display
- **d**: Show decimal/hex toggle
- **w**: Word wrap long strings'

But there's no indication whether these features are implemented or planned. Given that variable editing is explicitly marked 'Not Implemented', these should also be marked if they're not available.

---
---

#### documentation_inconsistency

**Description:** Conflicting information about Save keyboard shortcut

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/feature-reference.md under 'File Operations' states:
'### Save File ({{kbd:save:curses}})
Save the current program to disk. If no filename is set, prompts for one.
Note: Uses {{kbd:save:curses}} because {{kbd:save:curses}} is reserved for terminal flow control.'

This note is confusing - it says 'Uses {{kbd:save:curses}} because {{kbd:save:curses}} is reserved', which appears to be a copy-paste error. It should probably say 'Uses {{kbd:save:curses}} because Ctrl+S is reserved for terminal flow control.'

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Cut operation

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md lists:
- Cut/Copy/Paste ({{kbd:cut:tk}}/C/V)
- Cut: {{kbd:cut:tk}}

This appears to be incomplete notation. Should be {{kbd:cut:tk}}/{{kbd:copy:tk}}/{{kbd:paste:tk}} for consistency.

---
---

#### documentation_inconsistency

**Description:** Conflicting information about Search Help keyboard shortcut

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md lists under Help System:
- Search Help ({{kbd:file_save:tk}}hift+F)

This appears to be a typo/error. The shortcut notation '{{kbd:file_save:tk}}hift+F' is malformed and doesn't match any standard pattern. Should likely be a dedicated search shortcut or removed.

---
---

#### documentation_inconsistency

**Description:** Missing keyboard shortcuts for several documented features

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md documents these features as '(menu only)' or '(toolbar)' with no keyboard shortcuts:
- Stop/Interrupt: No keyboard shortcut (menu only)
- Continue: No keyboard shortcut (toolbar: 'Cont' button)
- Step Statement: No keyboard shortcut (toolbar: 'Stmt' button)
- Clear All Breakpoints: No keyboard shortcut (menu only)

But features.md shows:
- {{kbd:step_statement}} - Execute next statement
- {{kbd:step_line}} - Execute next line
- {{kbd:continue_execution}} - Continue to next breakpoint

This is contradictory about whether these shortcuts exist.

---
---

#### documentation_inconsistency

**Description:** Contradictory information about program storage persistence

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
features.md Local Storage section states:
- Currently Implemented:
  - Programs stored in Python server memory (session-only, lost on page refresh)
  - Recent files list stored in browser localStorage

But later under Session Management it states:
- Note: Collaboration features (sharing, collaborative editing, version control) are not currently implemented. Programs are stored locally in browser storage only.

This is contradictory - first it says programs are in server memory (lost on refresh), then it says programs are in browser storage (persistent).

---
---

#### documentation_inconsistency

**Description:** Inconsistent implementation status warnings across Tk UI documents

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/tips.md`

**Details:**
features.md has a note at the top:
- Note: Some features described below (Smart Insert, Variables Window, Execution Stack) are documented here based on the Tk UI design specifications. Check [Settings](settings.md) for current implementation status...

workflows.md has:
- Note: Some features described below (Smart Insert, Variables Window, Execution Stack, Renumber dialog) are documented here based on the Tk UI design specifications...

tips.md has:
- Note: Some features described below (Smart Insert, Variables Window, Execution Stack) are documented here based on the Tk UI design specifications...

These notes are inconsistent about which features are potentially unimplemented (workflows.md adds 'Renumber dialog').

---
---

#### documentation_inconsistency

**Description:** Inconsistent information about File menu operations between getting-started.md and web-interface.md

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md states:
"File operations (New, Open, Save, Save As) are available through the File menu."

But web-interface.md File Menu section lists:
"- **New** - Clear the editor and start a new program
- **Open** - Open a .bas file from your computer (via browser file picker)
- **Clear Output** - Clear the output area"

The File menu in web-interface.md is missing Save and Save As, which are mentioned in getting-started.md. Also, getting-started.md mentions these operations in the Toolbar section but then says they're in the File menu, while web-interface.md says file operations are available through the File menu but doesn't list Save/Save As there.

---
---

#### documentation_inconsistency

**Description:** Contradictory information about 'Open Example' feature availability

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md File Operations section states:
"File → Recent Files shows recently opened files (saved in localStorage, persists across browser sessions)."

But web-interface.md File Menu section states:
"**Note:** An 'Open Example' feature to choose from sample BASIC programs is planned for a future release."

The getting-started.md mentions Recent Files as an existing feature, while web-interface.md mentions Open Example as a future feature. These are different features, but the inconsistency is that getting-started.md doesn't mention Open Example at all, and web-interface.md doesn't mention Recent Files.

---
---

#### documentation_inconsistency

**Description:** Inconsistent menu structure documentation

**Affected files:**
- `docs/help/ui/web/index.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
index.md states:
"### Menu Bar

Located at the top with File, Edit, Run, View, and Help menus."

But getting-started.md states:
"### 1. Menu Bar

At the very top, three menus:

- **File** - New, Open, Save, Save As, Recent Files, Exit
- **Run** - Run Program, Stop, Step, Continue, List Program, Show Variables, Show Stack, Clear Output
- **Help** - Help Topics, About"

The index.md lists 5 menus (File, Edit, Run, View, Help) while getting-started.md lists only 3 menus (File, Run, Help). The Edit and View menus are missing from getting-started.md's description.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`

**Details:**
The document uses two different notations for keyboard shortcuts:
1. Template syntax: '{{kbd:new}}', '{{kbd:open}}', '{{kbd:save}}', '{{kbd:quit}}', '{{kbd:help}}', '{{kbd:run}}'
2. Plain text: 'ESC', 'Arrow Keys', 'b', 'F9', 'c', 'C', 's', 'S', 'e', 'E'

The {{kbd:...}} syntax appears to be a template placeholder that should be replaced with actual key names, but it's mixed with plain text key names in the same document.

---
---

#### documentation_inconsistency

**Description:** Empty program descriptions and tags

**Affected files:**
- `docs/library/telecommunications/index.md`

**Details:**
All telecommunications programs have empty descriptions and tags:
- Bmodem: no description, no tags
- Bmodem1: no description, no tags
- Command: no description, no tags
- Exitbbs1: no description, no tags
- Xtel: no description, no tags

This is inconsistent with other category index files (utilities, etc.) which have detailed descriptions and tags for each program.

---
---

#### documentation_inconsistency

**Description:** README.md describes keyboard-shortcuts.md as 'Keyboard shortcuts reference (Curses UI specific)' but the file title says 'MBASIC Curses UI Keyboard Shortcuts', confirming it's Curses-only. However, UI_FEATURE_COMPARISON.md shows keyboard shortcuts exist for all UIs (CLI, Curses, Tk, Web) with a comparison table.

**Affected files:**
- `docs/user/README.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
README.md line: '- **[keyboard-shortcuts.md](keyboard-shortcuts.md)** - Keyboard shortcuts reference (Curses UI specific)'

keyboard-shortcuts.md title: '# MBASIC Curses UI Keyboard Shortcuts'

UI_FEATURE_COMPARISON.md has section '## Keyboard Shortcuts Comparison' with tables showing shortcuts for CLI, Curses, Tk, and Web UIs.

The README suggests keyboard-shortcuts.md covers all UIs or is mislabeled, but the file itself is Curses-only. The comparison doc shows shortcuts exist for all UIs but aren't documented in a single reference.

---
---

#### documentation_inconsistency

**Description:** Auto-save feature status inconsistently described for Tk UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'File Operations' table:

Row 'Auto-save' shows:
- Tk: ⚠️
- Web: ✅
- Notes: 'Tk: planned/optional, Web: automatic'

The ⚠️ symbol means 'Partially implemented' according to legend, but the Notes say 'planned/optional' which suggests it's NOT implemented yet (planned = future). This is contradictory.

If it's planned but not implemented, it should be 📋 (Planned for future implementation).
If it's partially implemented, the Notes should explain what part works.

---
---

#### documentation_inconsistency

**Description:** Document references non-existent help files

**Affected files:**
- `docs/user/sequential-files.md`

**Details:**
At the end of sequential-files.md under 'See Also' section:

- [OPEN Statement](../help/common/language/statements/open.md)
- [INPUT# Statement](../help/common/language/statements/input_hash.md)
- [LINE INPUT# Statement](../help/common/language/statements/inputi.md)
- [EOF Function](../help/common/language/functions/eof.md)
- [File Format Compatibility](FILE_FORMAT_COMPATIBILITY.md)

These file paths are referenced but we don't have access to verify if they exist. The document also references:

'For general sequential file operations, see the [OPEN](../help/common/language/statements/open.md), [INPUT#](../help/common/language/statements/input_hash.md), [LINE INPUT#](../help/common/language/statements/inputi.md), and [PRINT#](../help/common/language/statements/printi-printi-using.md) statement documentation.'

Without access to these files, we cannot verify if they exist or if the paths are correct.

---
---

#### documentation_inconsistency

**Description:** Conflicting information about boolean value format in SET command vs JSON

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
Under 'SET Command' section, 'Type Conversion' subsection states:

'Booleans: `true` or `false` (lowercase, no quotes in commands; use true/false in JSON files)'

This is confusing because:
1. It says 'no quotes in commands' but then says 'use true/false in JSON files' - JSON also doesn't use quotes for booleans
2. The phrasing 'no quotes in commands; use true/false in JSON files' implies JSON might be different, but JSON boolean syntax is also true/false without quotes

The intended meaning seems to be that both use unquoted true/false, but the phrasing with semicolon suggests a contrast that doesn't exist.

---

---

## 🟢 Low Severity

#### Documentation inconsistency

**Description:** LineNode docstring mentions source_text field that doesn't exist

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring lines 152-161:
'Design note: This class intentionally does not have a source_text field to avoid
maintaining duplicate copies that could get out of sync with the AST during editing.
Text regeneration is handled by the position_serializer module which reconstructs
source text from statement nodes and their token information. Each StatementNode
has char_start/char_end offsets that indicate the character position within the
regenerated line text.'

The docstring explicitly documents the absence of a source_text field and explains why. However, this is unusual documentation style - typically you document what IS present, not what ISN'T. This could be confusing if readers don't know why this is mentioned.

---
---

#### Documentation inconsistency

**Description:** ChainStatementNode.delete_range type annotation inconsistency

**Affected files:**
- `src/ast_nodes.py`

**Details:**
ChainStatementNode line 598:
'delete_range: Optional[Tuple[int, int]] = None  # (start_line_number, end_line_number) for DELETE option - tuple of int line numbers'

The comment redundantly specifies 'tuple of int line numbers' when the type annotation 'Tuple[int, int]' already makes this clear. While not technically an inconsistency, the redundant comment could become outdated if the type changes.

---
---

#### code_vs_comment

**Description:** Comment in EOF() describes binary mode file handling but doesn't clarify relationship between BASIC mode 'I' and Python mode 'rb'

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment states: "These files are opened in binary mode ('rb') which allows ^Z checking for CP/M-style EOF detection"

This assumes mode 'I' files are opened with Python mode 'rb', but without seeing the execute_open() implementation referenced in the comment, this cannot be verified. The comment creates an expectation about implementation details in another file.

---
---

#### documentation_inconsistency

**Description:** Module docstring references tokens.py for MBASIC 5.21 specification but tokens.py is not provided

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring states: "Note: Version 5.21 refers to BASIC-80 Reference Manual Version 5.21. See tokens.py for complete MBASIC 5.21 specification reference."

The file tokens.py is not included in the provided source files, making this reference unverifiable.

---
---

#### Documentation inconsistency

**Description:** Comment about GOSUB return mechanism may be outdated

**Affected files:**
- `src/codegen_backend.py`

**Details:**
In _generate_return() method, there's a comment:
"# Generate case statements for ALL GOSUB return points in the program
# (we know the total from the first pass)"

But the code generates cases for range(self.total_gosubs), which is the count of GOSUB statements, not return points. Each GOSUB creates one return point, so this is technically correct, but the comment could be clearer that it's iterating over GOSUB count, not a separate list of return points.

---
---

#### Code vs Documentation inconsistency

**Description:** Docstring says manager is 'Not suitable for Web UI' but implementation doesn't prevent web UI usage

**Affected files:**
- `src/editing/manager.py`

**Details:**
Module docstring says:
"Extracted from InteractiveMode to enable reuse across local UIs (CLI, Curses, Tk).
Note: Not suitable for Web UI due to direct filesystem access - Web UI uses FileIO abstraction in interactive.py instead."

However, the ProgramManager class itself doesn't have any checks or restrictions preventing web UI usage. The load_from_file() and save_to_file() methods use standard Python file I/O which would work in any environment. The 'not suitable' claim appears to be a design recommendation rather than a technical limitation.

---
---

#### documentation_inconsistency

**Description:** Module docstring mentions 'TWO SEPARATE FILESYSTEM ABSTRACTIONS' but then describes intentional overlap, which could be clearer about the relationship

**Affected files:**
- `src/filesystem/base.py`

**Details:**
Docstring says:
"TWO SEPARATE FILESYSTEM ABSTRACTIONS:
1. FileIO (src/file_io.py) - Program management operations
...
2. FileSystemProvider (this file) - Runtime file I/O
...
Note: There is intentional overlap between the two abstractions.
Both provide list_files() and delete() methods, but serve different contexts"

The heading 'TWO SEPARATE' followed by 'intentional overlap' is slightly contradictory. They are separate abstractions with overlapping functionality, but the phrasing could be clearer.

---
---

#### code_vs_comment

**Description:** Comment says 'Note: We do not save/restore the PC before/after execution' but doesn't explain why this design choice was made

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Comment in execute() method:
"# Note: We do not save/restore the PC before/after execution.
# This allows statements like RUN to change execution position.
# Control flow statements (GOTO, GOSUB) can also modify PC but may produce
# unexpected results (see help text). Normal statements (PRINT, LET) don't modify PC."

The comment explains the consequence but not the rationale. It's unclear if this is intentional design or a limitation. The help text mentions control flow statements 'are not recommended' which suggests this might be a known limitation rather than intended behavior.

---
---

#### documentation_inconsistency

**Description:** Module docstring lists commands in two categories but categorization is inconsistent with implementation

**Affected files:**
- `src/interactive.py`

**Details:**
Module docstring at top states:
'- Direct commands: AUTO, EDIT, HELP (handled specially, not parsed as BASIC statements)
- Immediate mode statements: RUN, LIST, SAVE, LOAD, NEW, MERGE, FILES, SYSTEM, DELETE, RENUM, etc.
  (parsed as BASIC statements and executed in immediate mode)'

However, in execute_command() at line ~180, the code shows:
- AUTO, EDIT, HELP are handled directly (matches docstring)
- But then it says 'Everything else... goes through the parser as immediate mode statements'

The implementation for LIST, DELETE, RENUM, etc. actually calls cmd_list(), cmd_delete(), cmd_renum() methods directly in execute_immediate(), not through parser. The docstring's categorization is misleading about which commands are 'parsed as BASIC statements'.

---
---

#### code_vs_comment

**Description:** Comment says 'OLD EXECUTION METHODS REMOVED (version 1.0.299)' but this version number is not defined or tracked anywhere visible in the provided code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 677 states:
"# OLD EXECUTION METHODS REMOVED (version 1.0.299)
# Note: The project has an internal implementation version (tracked in src/version.py)
# which is separate from the MBASIC 5.21 language version being implemented."

The comment references src/version.py for tracking internal version, but this file is not provided in the source code files. Cannot verify if version 1.0.299 is accurate or if version tracking exists.

---
---

#### documentation_inconsistency

**Description:** InterpreterState docstring describes execution order but doesn't mention error_info can be set during statement execution (not just in error handlers)

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 44-51 describes execution order:
"Internal execution order in tick_pc() (for developers understanding control flow):
1. pause_requested check - pauses if pause() was called
2. halted check - stops if already halted
3. break_requested check - handles Ctrl+C breaks
4. breakpoints check - pauses at breakpoints
5. trace output - displays [line] or [line.stmt] if TRON is active
6. statement execution - where input_prompt may be set
7. error handling - where error_info is set via exception handlers"

However, code at lines 424-437 shows error_info is set DURING statement execution (step 6), not just in error handlers (step 7):
try:
    self.execute_statement(stmt)
    ...
except Exception as e:
    # Set ErrorInfo for both handler and no-handler cases
    self.state.error_info = ErrorInfo(...)

The docstring should clarify that error_info can be set during step 6 (statement execution) when exceptions occur.

---
---

#### code_vs_comment

**Description:** Comment about CLEAR state preservation mentions user_functions but doesn't mention other preserved state

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1283 states:
"# State preservation for CHAIN compatibility:
#
# PRESERVED by CLEAR (not cleared):
#   - runtime.common_vars (list of COMMON variable names - the list itself, not values)
#   - runtime.user_functions (DEF FN functions)
#
# NOT PRESERVED (cleared above):
#   - All variables and arrays
#   - All open files (closed and cleared)
#   - Field buffers"

However, the code doesn't explicitly preserve user_functions - it only clears variables, arrays, and files. The comment implies user_functions are intentionally preserved, but there's no code showing they survive CLEAR. This could be correct if user_functions are stored separately and not touched by clear_variables/clear_arrays, but the comment should clarify this is implicit preservation rather than explicit.

---
---

#### code_vs_comment

**Description:** Comment about OPTION BASE enforcement mentions 'Duplicate Definition' error but doesn't explain why that specific error

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1360 states:
"MBASIC 5.21 restrictions (strictly enforced):
- OPTION BASE can only be executed once per program run
- Must be executed BEFORE any arrays are dimensioned (implicit or explicit)
- Violating either condition raises 'Duplicate Definition' error"

The code correctly raises 'Duplicate Definition' but the comment doesn't explain why MBASIC chose this error message (which seems semantically odd for 'already executed' vs 'arrays exist'). This is historical MBASIC behavior being replicated, but the comment could note this is MBASIC's choice, not a logical error message.

---
---

#### Documentation inconsistency

**Description:** Module docstring mentions CursesIOHandler but the actual class name in curses_io.py is CursesIOHandler (correct), however the docstring example shows inconsistent capitalization

**Affected files:**
- `src/iohandler/__init__.py`

**Details:**
The __init__.py correctly exports 'CursesIOHandler' but the module docstring doesn't provide usage examples for consistency with the GUI/Web handlers mentioned.

---
---

#### Code vs Documentation inconsistency

**Description:** get_screen_size() method exists but is not part of IOHandler interface

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py implements get_screen_size() with note: 'Note: This is a web_io-specific method, not part of the IOHandler base interface. Other implementations (console, curses, gui) do not provide this method.'

This creates an inconsistent interface where code using WebIOHandler might call methods not available in other handlers, breaking polymorphism.

---
---

#### Documentation inconsistency

**Description:** Inconsistent warning message formatting in fallback code

**Affected files:**
- `src/iohandler/console.py`

**Details:**
First warning: 'warnings.warn("msvcrt not available on Windows - non-blocking input_char() not supported", RuntimeWarning)'

Second warning: 'warnings.warn("msvcrt not available on Windows - input_char() falling back to input() (waits for Enter, not single character)", RuntimeWarning)'

The warnings have different levels of detail and formatting style, suggesting they were written at different times.

---
---

#### Documentation inconsistency

**Description:** Module docstring references SimpleKeywordCase but doesn't provide import path

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
Docstring states: 'For simpler force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py)'

This references a file that is not included in the provided source code files, making it impossible to verify the relationship or whether SimpleKeywordCase actually exists.

---
---

#### Code vs Comment conflict

**Description:** Comment about platform-specific behavior is vague and potentially misleading

**Affected files:**
- `src/iohandler/console.py`

**Details:**
In input_line() method: 'Note: Python's input() strips only the trailing newline, preserving leading/trailing spaces. However, terminal input behavior may vary across platforms.'

This comment hedges by saying 'may vary' but doesn't specify what variations exist or when they occur, making it less useful for developers trying to understand actual behavior.

---
---

#### code_vs_comment

**Description:** Comment in parse_print() mentions optional comma after file number, but doesn't explain semicolon handling clearly

**Affected files:**
- `src/parser.py`

**Details:**
parse_print() comment says:
"# Optionally consume comma after file number
# Note: MBASIC 5.21 typically uses comma (PRINT #1, 'text').
# Our parser makes the comma optional for flexibility.
# If semicolon appears instead of comma, it will be treated as an item
# separator in the expression list below (not as a file number separator)."

The code then does:
if self.match(TokenType.COMMA):
    self.advance()

This comment suggests semicolon is NOT consumed after file number, which could lead to ambiguity. The comment is trying to explain behavior but may be confusing about what happens when semicolon follows file number.

---
---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'end of line' vs 'end of statement' in various docstrings

**Affected files:**
- `src/parser.py`

**Details:**
Multiple methods use different terminology:
- at_end_of_line() checks for NEWLINE or EOF
- at_end_of_statement() checks for NEWLINE, EOF, COLON, or comments
- at_end() checks for EOF or position >= len(tokens)
- at_end_of_tokens() checks if current() is None

The naming suggests 'line' means physical line and 'statement' means logical statement, but the documentation doesn't consistently explain this distinction. Some comments use 'end of line' when they mean 'end of statement'.

---
---

#### code_vs_comment

**Description:** Comment in parse_variable_or_function() about stripping type suffix from original_case may not match actual behavior

**Affected files:**
- `src/parser.py`

**Details:**
The code says:
if type_suffix:
    name = name[:-1]  # Remove the suffix character from the name
    # Also strip from original case
    if original_case and len(original_case) > 0:
        original_case = original_case[:-1]
    explicit_type_suffix = True

The comment 'Also strip from original case' suggests we're modifying original_case, but this only happens if type_suffix exists. The comment doesn't clarify what happens to original_case when there's no explicit suffix but a DEF-inferred type.

---
---

#### code_vs_comment

**Description:** Comment about MID$ tokenization may be misleading

**Affected files:**
- `src/parser.py`

**Details:**
In parse_mid_assignment() method around line 1850:

Comment states: "Note: The lexer tokenizes 'MID$' in source as a single MID token (the $ is part of the keyword, not a separate token)."

Then code shows:
token = self.current()  # MID token (represents 'MID$' from source)

This is consistent, but the comment could be clearer about whether the token type is actually called 'MID' or 'MID$' in the TokenType enum. The comment suggests the $ is stripped during lexing, but doesn't explicitly state what the token type name is.

---
---

#### code_vs_comment

**Description:** Comment about dimension expressions in DIM statement may not match all BASIC dialects

**Affected files:**
- `src/parser.py`

**Details:**
In parse_dim() method around line 1750:

Comment states: "Dimension expressions: This implementation accepts any expression for array dimensions (e.g., DIM A(X*2, Y+1)), with dimensions evaluated at runtime. This matches MBASIC 5.21 behavior. Note: Some compiled BASICs (e.g., QuickBASIC) may require constants only."

The code implements: dim_expr = self.parse_expression()

This is consistent with the comment, but the comment makes a claim about "MBASIC 5.21 behavior" without providing a reference or verification. This could be misleading if MBASIC 5.21 actually has different behavior.

---
---

#### code_vs_comment

**Description:** Comment about LPRINT separator behavior uses ambiguous examples

**Affected files:**
- `src/parser.py`

**Details:**
In parse_lprint() method around line 1000:

Comment states: "Separator count vs expression count:
- If separators < expressions: no trailing separator, add newline
- If separators >= expressions: has trailing separator, no newline added
Examples: 'LPRINT A;B;C' has 2 separators for 3 items (no trailing sep, adds \n)
          'LPRINT A;B;C;' has 3 separators for 3 items (trailing sep, no \n)
          'LPRINT ;' has 1 separator for 0 items (trailing sep, no \n)"

The code implements:
if len(separators) < len(expressions):
    separators.append('\n')

The logic is correct, but the third example 'LPRINT ;' is confusing because it suggests a separator with no expressions, which would result in separators=1, expressions=0, and len(separators) >= len(expressions), so no newline is added. However, this edge case behavior isn't clearly explained in the comment.

---
---

#### documentation_inconsistency

**Description:** PC class examples show notation like 'PC(10, 0)' and 'PC(10, 2)' but __repr__ outputs 'PC(10.0)' and 'PC(10.2)' with dot notation. The examples don't match the actual string representation.

**Affected files:**
- `src/pc.py`

**Details:**
Examples in docstring:
    'PC(10, 0)  - First statement on line 10 (stmt_offset=0)'
    'PC(10, 2)  - Third statement on line 10 (stmt_offset=2)'

__repr__ implementation:
    'return f"PC({self.line_num}.{self.stmt_offset})"'

Actual output would be 'PC(10.0)' not 'PC(10, 0)'. The examples should use dot notation to match the implementation.

---
---

#### documentation_inconsistency

**Description:** Module docstrings have inconsistent cross-references to each other

**Affected files:**
- `src/resource_limits.py`
- `src/resource_locator.py`

**Details:**
resource_limits.py says: "Note: This is distinct from resource_locator.py which finds package data files."

resource_locator.py says: "Note: This is distinct from resource_limits.py which enforces runtime execution limits."

Both modules correctly distinguish themselves from each other, but the phrasing is slightly different. resource_limits.py describes resource_locator as finding 'package data files' while resource_locator describes resource_limits as enforcing 'runtime execution limits'. Both are accurate but could be more consistent.

---
---

#### code_vs_documentation_inconsistency

**Description:** Docstring parameter descriptions use inconsistent units for memory values

**Affected files:**
- `src/resource_limits.py`

**Details:**
In ResourceLimits.__init__() docstring:
- max_total_memory described as: "Maximum total memory for all variables/arrays (bytes)"
- max_array_size described as: "Maximum size for a single array (bytes)"
- max_file_size described as: "Maximum size for a single file (bytes)"

All correctly specify '(bytes)' unit. However:
- max_string_length described as: "Maximum byte length for a string variable (UTF-8 encoded). MBASIC 5.21 limit is 255 bytes."

This one says 'byte length' in the description text and then adds '255 bytes' at the end, making it redundant. The others just say the parameter name and '(bytes)'. Minor inconsistency in documentation style.

---
---

#### code_vs_comment

**Description:** Comment in _get_global_settings_path() and _get_project_settings_path() says methods are 'not currently used' but they are used in __init__

**Affected files:**
- `src/settings.py`

**Details:**
Comment says: 'Note: This method is not currently used. Path resolution has been delegated to the backend'

But __init__ code shows:
self.global_settings_path = getattr(backend, 'global_settings_path', None)
self.project_settings_path = getattr(backend, 'project_settings_path', None)

The methods themselves are indeed unused (backend handles paths), but the comment is misleading about why they're kept. They're kept for 'potential future use or manual path queries', not because they're used via getattr (which gets backend attributes, not calls these methods).

---
---

#### documentation_inconsistency

**Description:** Module docstrings describe different storage paths for global settings

**Affected files:**
- `src/settings.py`
- `src/settings_backend.py`

**Details:**
src/settings.py docstring says:
'- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)'

src/settings_backend.py FileSettingsBackend docstring says:
'- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)'

Both are consistent, but the implementation in _get_global_settings_path() uses:
appdata = os.getenv('APPDATA', os.path.expanduser('~'))

This means if APPDATA is not set on Windows, it falls back to home directory, which would be ~\mbasic\settings.json, not %APPDATA%\mbasic\settings.json. The documentation should note this fallback behavior.

---
---

#### documentation_inconsistency

**Description:** Comments mention settings not included but don't explain why they're documented as excluded

**Affected files:**
- `src/settings_definitions.py`

**Details:**
Comments say:
'# Note: editor.tab_size setting not included - BASIC uses line numbers for program structure, not indentation, so tab size is not a meaningful setting for BASIC source code'

'# Note: Line numbers are always shown - they\'re fundamental to BASIC! editor.show_line_numbers setting not included - makes no sense for BASIC'

These are design decisions documented in comments, but there's no corresponding documentation explaining these exclusions to users. If a user expects these settings (common in modern editors), they won't find documentation explaining why they're absent.

---
---

#### Documentation inconsistency

**Description:** get_additional_keybindings() function has extensive documentation explaining why readline keybindings are NOT in cli_keybindings.json, but this meta-documentation about what's intentionally excluded seems misplaced in code rather than in a separate documentation file.

**Affected files:**
- `src/ui/cli.py`

**Details:**
get_additional_keybindings() docstring:
"Return additional keybindings for CLI that aren't in the JSON file.

These are readline keybindings that are handled by Python's readline module,
not by the keybinding system. They're documented here for completeness.

NOTE: These keybindings are intentionally NOT in cli_keybindings.json because:
1. They're provided by readline, not the MBASIC keybinding system
2. They're only available when readline is installed (platform-dependent)
3. Users can't customize them through MBASIC settings
4. They follow standard readline/Emacs conventions (Ctrl+E, Ctrl+K, etc.)

This separation keeps cli_keybindings.json focused on MBASIC-specific keybindings
that users can customize, while this function documents readline's built-in keybindings
for reference in help systems."

This architectural explanation belongs in design documentation, not in a function docstring.

---
---

#### Code vs Comment conflict

**Description:** Comment in _create_setting_widget() says 'Strip force_ prefix from beginning for cleaner display' but uses removeprefix() with a fallback that checks startswith(). The comment doesn't explain why this prefix stripping is needed or what 'force_' means in this context.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Code in _create_setting_widget():
"# Strip 'force_' prefix from beginning for cleaner display
display_label = choice.removeprefix('force_') if hasattr(str, 'removeprefix') else (choice[6:] if choice.startswith('force_') else choice)"

The comment explains WHAT is done but not WHY. Later code shows the actual value is stored separately:
"# Store the actual value as user_data for later retrieval
rb._actual_value = choice"

And in _on_reset():
"# Note: Compares actual value (stored in _actual_value) not display label
# since display labels have 'force_' prefix stripped"

This suggests 'force_' is a meaningful prefix in enum values, but there's no documentation explaining its purpose or which settings use it.

---
---

#### Documentation inconsistency

**Description:** The 'show_settings' command description says 'View all settings or filter by pattern (e.g., SHOW SETTINGS "auto")' but the 'keys' field only shows 'SHOW SETTINGS' without the pattern syntax.

**Affected files:**
- `src/ui/cli_keybindings.json`

**Details:**
cli_keybindings.json:
"show_settings": {
  "keys": ["SHOW SETTINGS"],
  "primary": "SHOW SETTINGS",
  "description": "View all settings or filter by pattern (e.g., SHOW SETTINGS \"auto\")"
}

The keys field should probably be ["SHOW SETTINGS", "SHOW SETTINGS \"pattern\""] to match the description, or the description should clarify that the pattern is optional.

---
---

#### code_vs_comment

**Description:** Comment about default target_column=7 is misleading given variable-width line numbers

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress() method:
"Note: Methods like _sort_and_position_line use a default target_column of 7,
which assumes typical line numbers (status=1 char + number=5 digits + space=1 char).
This is an approximation since line numbers have variable width."

But with variable-width line numbers, the calculation '1 + 5 + 1 = 7' is only valid for 5-digit line numbers. For line 10, the actual column would be 1 + 2 + 1 = 4. The comment acknowledges this is an approximation but the default value of 7 may not be appropriate for most cases.

---
---

#### code_vs_comment

**Description:** Comment about line_number > 0 check is unclear about its purpose

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_syntax_errors():
"# Clear error status for empty lines, but preserve breakpoints
# Note: line_number > 0 check handles edge case of line 0 (if present)
# Consistent with _check_line_syntax which treats all empty lines as valid"

The comment mentions 'line 0' as an edge case, but BASIC programs typically don't use line 0. The purpose of this check is unclear - is line 0 invalid? Should it be skipped? The comment doesn't clarify the intended behavior.

---
---

#### code_vs_comment

**Description:** Comment about pasted lines starting with digits assumes they are line numbers, but this may not always be true

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_numbers():
"# FIRST: Check if line starts with a digit (raw pasted BASIC with line numbers)
# In this context, we assume lines starting with digits are numbered program lines (e.g., '10 PRINT').
# Note: While BASIC statements can start with digits (numeric expressions), when pasting
# program code, lines starting with digits are conventionally numbered program lines."

The comment acknowledges that BASIC statements can start with digits but assumes pasted content starting with digits is always a line number. This could cause issues if someone pastes a numeric expression like '123 + 456' without a line number.

---
---

#### code_vs_comment

**Description:** Comment about 'use None instead of not' is overly specific and potentially confusing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _display_syntax_errors():
"# Check if output walker is available (use 'is None' instead of 'not' to avoid false positive on empty walker)
if self._output_walker is None:"

The comment suggests 'not self._output_walker' would give a false positive on an empty walker, but an empty walker would still be truthy (it's an object, not None). The comment seems to confuse 'empty' with 'None'. Using 'is None' is correct, but the justification is misleading.

---
---

#### code_vs_comment

**Description:** Comment says immediate_io is created temporarily and recreated in start(), but the code shows it's created twice in __init__ and once in start()

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~175 says:
# IO Handler Lifecycle:
# 1. self.io_handler (CapturingIOHandler) - Used for RUN program execution
#    Created ONCE here, reused throughout session (NOT recreated in start())
# 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands
#    Created here temporarily, then RECREATED in start() with fresh instance each time

But in __init__, immediate_io is created at line ~186 for Interpreter, then again at line ~197 for ImmediateExecutor. Then in start() at line ~234, it's created a third time. The comment suggests only 2 creations (once in __init__ temporarily, once in start()), but code shows 3 total.

---
---

#### code_vs_comment

**Description:** Comment says 'Toolbar removed from UI layout' but there's no evidence of a toolbar ever existing in the visible code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~267 says:
# Toolbar removed from UI layout - use Ctrl+U interactive menu bar instead for keyboard navigation

This suggests a toolbar was previously in the code and removed, but without seeing the git history or previous versions, this comment may be outdated or referring to code not shown in this snippet.

---
---

#### code_vs_comment

**Description:** Comment about _continue_smart_insert losing context is misleading - the method receives all needed parameters

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1363 says:
# Note: Cannot continue the insert operation here because the context was lost
# when the dialog callback was invoked (lines, line_index, insert_num variables
# are no longer available). User will need to retry the insert operation manually.

But _continue_smart_insert() at line ~1368 receives insert_num, line_index, and lines as parameters, so the context is NOT lost. The comment suggests a limitation that doesn't exist in the code.

---
---

#### code_vs_comment

**Description:** Comment about main widget storage approach differs between methods but describes same underlying pattern

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_help/_show_keymap/_show_settings (around lines 700-900), comments state:
"Main widget retrieval: Use self.base_widget (stored at UI creation time in __init__)
rather than self.loop.widget (which reflects the current widget and might be a menu
or other overlay)."

In _activate_menu (around line 950), comment states:
"Main widget storage: Unlike _show_help/_show_keymap/_show_settings which close
existing overlays first (and thus can use self.base_widget directly), this method
extracts base_widget from self.loop.widget to unwrap any existing overlay."

These comments describe different approaches for different use cases, which is intentional design. Not an inconsistency.

---
---

#### code_vs_comment

**Description:** Comment in _execute_immediate about immediate mode status is misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says:
'# Immediate mode status remains disabled during execution - program output shows in output window'

But this is just a comment with no corresponding code. The actual status update happens in _update_immediate_status() which is called elsewhere. The comment placement suggests it's explaining code that should be here but isn't.

---
---

#### code_vs_comment

**Description:** Comment in _sync_program_to_runtime about LIST command is confusing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says:
'# Sync program to runtime (updates statement table and line text map).
# If execution is running, _sync_program_to_runtime preserves current PC.
# If not running, it sets PC to halted. Either way, this doesn't start execution,
# but allows commands like LIST to see the current program.'

The comment about LIST is misleading because LIST doesn't need runtime sync to see the program - it reads from self.program directly (see _list_program method). The sync is for execution, not for LIST. This suggests the comment writer misunderstood the purpose of the sync.

---
---

#### documentation_inconsistency

**Description:** Version macro comment mentions separate implementation version but doesn't explain relationship

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Comment at line ~77 states:
"# Hardcoded MBASIC version for documentation
# Note: Project has internal implementation version (src/version.py) separate from this
return "5.21"  # MBASIC 5.21 language version"

This mentions two different versions (documentation version 5.21 and implementation version in src/version.py) but doesn't explain why they're different or how they relate. This could confuse developers about which version to use where.

---
---

#### Code vs Comment conflict

**Description:** Comment claims context menu dismissal is automatic, but code explicitly releases grab

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Lines 598-602 comment states:
# Note: tk_popup() handles menu dismissal automatically (ESC key,
# clicks outside menu, selecting items). Explicit bindings for
# FocusOut/Escape are not needed and may not fire reliably since
# Menu widgets have their own event handling for dismissal.

But lines 603-607 explicitly release grab:
try:
    menu.tk_popup(event.x_root, event.y_root)
finally:
    # Release grab after menu is shown. Note: tk_popup handles menu interaction,
    # but we explicitly release the grab to ensure clean state.
    menu.grab_release()

The comment says explicit handling is not needed, but code does explicit grab_release() with justification.

---
---

#### Code vs Comment conflict

**Description:** Comment about link tag prefixes may be incomplete

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Lines 575-579 comment states:
Note: Both "link_" (from _render_line_with_links) and "result_link_"
(from _execute_search) prefixes are checked. Both types are stored
identically in self.link_urls, but the prefixes distinguish their origin.

However, _render_line_with_links() at line 227 creates tags with prefix "link_" (not "link_" and "result_link_"), while _execute_search() at line 437 creates "result_link_" prefix. The comment correctly describes the two prefixes, but the code at line 580-582 checks for both:
for tag in tags:
    if tag.startswith("link_") or tag.startswith("result_link_"):
        link_tag = tag

This is consistent, not a conflict.

---
---

#### Code vs Comment conflict

**Description:** Comment describes widget storage incorrectly

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Lines 189-192 comment in _get_current_widget_values():
# All entries in self.widgets dict are tk.Variable instances (BooleanVar, StringVar, IntVar),
# not the actual widget objects (Checkbutton, Spinbox, Entry, Combobox).
# The variables are associated with widgets via textvariable/variable parameters.

This is accurate based on _create_setting_widget() lines 139-161 which stores variables (var) not widgets in self.widgets[key]. Not a conflict, comment is correct.

---
---

#### Documentation inconsistency

**Description:** Docstring describes modal behavior incompletely

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 36 comment states:
# Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())

This clarifies that grab_set() is used without wait_window(), making it modal for interaction but not blocking. However, the class docstring at line 15 just says 'Dialog for modifying MBASIC settings' without mentioning modal behavior. Minor documentation gap.

---
---

#### Code vs Documentation inconsistency

**Description:** Help display mechanism described as tooltip in comment but implemented as label

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 172 comment states:
# Show short help as inline label (not a hover tooltip, just a gray label)

This clarifies the implementation is a static label, not a tooltip. The comment is accurate and matches the code at lines 173-175 which creates a ttk.Label. Not an inconsistency, just explicit clarification.

---
---

#### code_vs_comment

**Description:** Comment describes _ImmediateModeToken usage at line 1194 but that line number is not visible in provided code

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 18-25: '_ImmediateModeToken docstring says: "This class is instantiated when editing variables via the variable inspector (see _on_variable_edit() around line 1194)."'
The provided code ends before line 1194, making this reference unverifiable. The method _on_variable_edit() is not present in the provided snippet.

---
---

#### documentation_inconsistency

**Description:** Docstring example shows TkIOHandler created without backend parameter, but later code shows backend parameter being used

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring lines 56-62: 'io = TkIOHandler()  # TkIOHandler created without backend reference initially'
Line 323: 'tk_io = TkIOHandler(self._add_output, self.root, backend=self)'
The example in the docstring doesn't match the actual instantiation pattern used in the code.

---
---

#### code_vs_comment_conflict

**Description:** Comment about showing error list contradicts the actual condition logic

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1870:
Comment: "# Only show full error list in output if there are multiple errors.\n# For single errors, the red ? icon in the editor is sufficient feedback.\n# This avoids cluttering the output pane with repetitive messages during editing."

Code:
should_show_list = len(errors_found) > 1
if should_show_list:
    self._add_output("\n=== Syntax Errors ===\n")

The comment says 'multiple errors' but the code checks for '> 1' which means 2 or more. This is technically correct, but the comment could be clearer. More importantly, the comment explains the rationale (avoiding clutter) but doesn't explain why exactly 1 error is the threshold - why not show errors for 2-3 errors but hide for 1? The logic seems arbitrary without more context.

---
---

#### code_vs_comment

**Description:** Comment in _check_line_change says 'Don't trigger sort when old_line_num is None' to prevent sorting when 'user clicks around without making changes', but this is implementation detail that could be in the code logic itself

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1360:
# Determine if program needs to be re-sorted:
# 1. Line number changed on existing line (both old and new are not None), OR
# 2. Line number was removed (old was not None, new is None and line has content)
#
# Don't trigger sort when:
# - old_line_num is None: First time tracking this line (cursor just moved here, no editing yet)
# - This prevents unnecessary re-sorting when user clicks around without making changes

The comment is verbose and explains the logic that's already clear from the code structure. Could be simplified.

---
---

#### code_vs_comment

**Description:** Comment in _on_enter_key says 'At this point, the editor contains only the numbered lines (no blank lines)' but this is an assumption that may not always hold

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1070:
# At this point, the editor contains only the numbered lines (no blank lines)
# because _refresh_editor loads from the program, which filters out blank lines

This assumes _refresh_editor() was just called and succeeded, but if there were parse errors, _refresh_editor() is NOT called (line ~1063: 'if not success: return'). So the comment's assumption may be false.

---
---

#### code_vs_comment_conflict

**Description:** The _on_cursor_move() method has a comment explaining why after_idle() is used: 'Schedule deletion after current event processing to avoid interfering with ongoing key/mouse event handling (prevents cursor position issues, undo stack corruption, and widget state conflicts during event processing)', but this detailed explanation is not mentioned in the method's docstring or the class docstring's 'Automatic blank line removal' section.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Inline comment: '# Schedule deletion after current event processing to avoid interfering with ongoing key/mouse event handling (prevents cursor position issues, undo stack corruption, and widget state conflicts during event processing)'

Class docstring only says: 'When cursor moves away from a blank line, that line is automatically deleted'

The technical reason for using after_idle() is important for maintainers but not documented in the docstring.

---
---

#### Code vs Comment conflict

**Description:** Comment in _internal_change_handler says 'CodeMirror sends new value in e.args attribute' but this is implementation detail that may not always be true

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Comment: '# CodeMirror sends new value in e.args attribute'
Code: 'self._value = e.args'

This comment describes the current behavior but doesn't explain why or acknowledge this is a NiceGUI event convention, not necessarily a CodeMirror convention. The comment could be misleading if the event structure changes.

---
---

#### Documentation inconsistency

**Description:** value property docstring says 'Always returns a string, even if internal value is dict or None' but doesn't explain why internal value would ever be a dict

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Property docstring:
    @property
    def value(self) -> str:
        """Get current editor content.

        Always returns a string, even if internal value is dict or None.
        """
        if isinstance(self._value, dict):
            # Sometimes event args are dict - return empty string
            return ''
        return self._value or ''

The docstring mentions dict handling but doesn't explain the circumstances. The inline comment 'Sometimes event args are dict' suggests this is a workaround for an event handling quirk, but this isn't documented in the property docstring.

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

**Description:** Multiple references to MBASIC version '5.21' as language version, but inconsistent labeling

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~598: # Note: '5.21' is the MBASIC language version (intentionally hardcoded)
Line ~599: ui.label('MBASIC 5.21 Web IDE').classes('text-lg')
Line ~1063: ui.page_title('MBASIC 5.21 - Web IDE')
Line ~1117: self.output_text = f'MBASIC 5.21 Web IDE - {VERSION}\n'

The comment clarifies 5.21 is the language version, but this distinction is not consistently documented throughout the file.

---
---

#### code_vs_comment

**Description:** Comment about columns not being sortable contradicts the presence of sort controls

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~177:
# Create table - columns not sortable (we handle sorting via buttons above)

This comment is accurate for the table itself, but could be clearer that sorting IS available via the button controls above the table, not via column headers. The phrasing 'columns not sortable' might mislead readers into thinking no sorting exists.

---
---

#### code_vs_comment

**Description:** Comment about event args structure shows uncertainty about implementation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Lines ~221-229:
# e.args is the event arguments from NiceGUI table
# For rowClick, the clicked row data is in e.args (which is a dict-like object)
try:
    # Get the row data from the event
    if hasattr(e.args, 'get'):
        # e.args is a dict-like object
        var_name = e.args.get('name')
    elif isinstance(e.args, list) and len(e.args) > 0:
        # e.args might be a list with row data

The multiple conditional checks and comments like 'might be' suggest uncertainty about the actual event structure. This indicates either incomplete documentation or unstable API.

---
---

#### code_vs_comment

**Description:** Comment about natural number formatting doesn't explain the logic clearly

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~343:
# Format numbers naturally - show integers without decimals

The code checks if a float equals its integer conversion, but the comment doesn't explain why this is 'natural' or what the alternative would be. This is a minor clarity issue.

---
---

#### code_vs_comment

**Description:** Comment about NiceGUI best practice for dialog creation may be outdated

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1055:
# Create reusable dialog instances (NiceGUI best practice: create once, reuse)

This claims to be a NiceGUI best practice, but without seeing NiceGUI documentation, cannot verify if this is current guidance or outdated advice.

---
---

#### documentation_inconsistency

**Description:** Compiler documentation describes features as in-progress but presents them as complete

**Affected files:**
- `docs/help/common/compiler/index.md`
- `docs/help/common/compiler/optimizations.md`

**Details:**
index.md states: "**Status:** In Progress" for Code Generation and "Documentation for the code generation phase will be added as the compiler backend is developed."

However, optimizations.md presents 27 optimizations in detail with full descriptions, examples, and benefits as if they are fully implemented. The page only mentions at the end: "**Status:** In Progress" and "Additional optimizations will be added during code generation".

This creates confusion about whether these 27 optimizations are:
1. Already implemented in semantic analysis (as the text suggests)
2. Planned but not yet implemented
3. Partially implemented

The documentation should clearly state the implementation status of each optimization.

---
---

#### documentation_inconsistency

**Description:** Inconsistent cross-reference descriptions between LOC and LOF

**Affected files:**
- `docs/help/common/language/functions/loc.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
In loc.md, the 'See Also' section references LOF as: 'Returns the total file SIZE in bytes (LOC returns current POSITION/record number)'

In lof.md, the 'See Also' section references LOC as: 'Returns current file POSITION/record number (LOF returns total SIZE in bytes)'

These are mirror descriptions but use slightly different capitalization patterns (SIZE vs size, POSITION vs position). While functionally equivalent, consistency would be better.

---
---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' sections for system functions

**Affected files:**
- `docs/help/common/language/functions/fre.md`
- `docs/help/common/language/functions/hex_dollar.md`
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/inp.md`
- `docs/help/common/language/functions/peek.md`

**Details:**
The system functions (FRE, INKEY$, INP, PEEK) all have nearly identical 'See Also' sections listing each other, but HEX$ does not include these system functions in its 'See Also' section even though it's used in examples with INP and PEEK. The grouping appears arbitrary - either all system functions should cross-reference each other consistently, or the cross-references should be more selective based on actual functional relationships.

---
---

#### documentation_inconsistency

**Description:** Inconsistent error condition documentation format

**Affected files:**
- `docs/help/common/language/functions/instr.md`
- `docs/help/common/language/functions/mid_dollar.md`

**Details:**
In instr.md: 'Note: If I=0 is specified, an "Illegal function call" error will occur.'

In mid_dollar.md: 'Note: If I=0 is specified, an "Illegal function call" error will occur.'

Both functions document the same error condition in the same way, but other functions with similar constraints (like LEFT$, RIGHT$) don't document what happens with invalid arguments. This inconsistency in documentation completeness could confuse users about whether other functions validate their inputs.

---
---

#### documentation_inconsistency

**Description:** SPACE$ documentation doesn't mention relationship to STRING$

**Affected files:**
- `docs/help/common/language/functions/space_dollar.md`
- `docs/help/common/language/functions/string_dollar.md`

**Details:**
space_dollar.md states: 'This is equivalent to STRING$(I, 32) since 32 is the ASCII code for a space character.'

However, string_dollar.md doesn't mention that SPACE$ is a convenience function for STRING$(I, 32). The cross-reference is one-directional. For completeness, STRING$ documentation should note that SPACE$ provides a shorthand for creating space strings.

---
---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in mathematical functions

**Affected files:**
- `docs/help/common/language/functions/int.md`
- `docs/help/common/language/functions/sgn.md`
- `docs/help/common/language/functions/sin.md`
- `docs/help/common/language/functions/sqr.md`

**Details:**
Some mathematical function examples show the 'Ok' prompt after output (int.md, sin.md), while others don't (sgn.md shows only the ON GOTO statement without RUN output, sqr.md shows full RUN session with Ok). This inconsistency in example presentation style makes the documentation less uniform.

---
---

#### documentation_inconsistency

**Description:** Inconsistent formatting of 'See Also' sections between related DEF statements

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
def-fn.md uses:
- [DEF USR](def-usr.md) - Define assembly subroutine address
- [USR](../functions/usr.md) - Call assembly language subroutine

def-usr.md uses:
- [USR](../functions/usr.md) - Call assembly language subroutine
- [DEF FN](def-fn.md) - Define user-defined function

Both should cross-reference each other consistently, but def-usr.md doesn't mention it's not implemented while def-fn.md doesn't warn about this.

---
---

#### documentation_inconsistency

**Description:** DELETE and EDIT have different levels of implementation detail about modern vs historical behavior

**Affected files:**
- `docs/help/common/language/statements/delete.md`
- `docs/help/common/language/statements/edit.md`

**Details:**
delete.md provides minimal information and doesn't mention modern implementation differences.

edit.md explicitly states:
"**Modern MBASIC Implementation:** This implementation provides full-screen editing capabilities through the integrated editor (Tk, Curses, or Web UI). The EDIT command is recognized for compatibility, but line editing is performed directly in the full-screen editor rather than entering a special edit mode."

DELETE should similarly clarify if its behavior differs from original MBASIC 5.21.

---
---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of 'BASIC' vs 'BASIC-80' across documentation

**Affected files:**
- `docs/help/common/language/statements/files.md`
- `docs/help/common/language/statements/input.md`

**Details:**
files.md uses: "CP/M automatically adds .BAS extension if none is specified for BASIC program files."

input.md and other files use: "BASIC-80" when referring to the interpreter.

Documentation should consistently use either 'BASIC', 'BASIC-80', or 'MBASIC' when referring to the interpreter.

---
---

#### documentation_inconsistency

**Description:** GOSUB documentation mentions BASIC-80 by name, GOTO documentation doesn't, inconsistent naming

**Affected files:**
- `docs/help/common/language/statements/gosub-return.md`
- `docs/help/common/language/statements/goto.md`

**Details:**
gosub-return.md: "The RETURN statement(s) in a subroutine cause BASIC-80 to branch back to the statement following the most recent GOSUB statement."

goto.md: Uses generic language without mentioning BASIC-80 or MBASIC.

Documentation should be consistent about whether to use 'BASIC-80', 'MBASIC', or generic 'the interpreter'.

---
---

#### documentation_inconsistency

**Description:** Index lists HELPSETTING, LIMITS, SET, and SHOW SETTINGS as modern extensions but uses inconsistent command names

**Affected files:**
- `docs/help/common/language/statements/index.md`

**Details:**
Index lists:
"- [HELPSETTING](helpsetting.md) - Display help for settings"
"- [SET](setsetting.md) - Configure interpreter settings"
"- [SHOW SETTINGS](showsettings.md) - Display current settings"

The link text 'SET' points to 'setsetting.md', suggesting the actual command might be SETSETTING not SET. The index should use the actual command name consistently.

---
---

#### documentation_inconsistency

**Description:** ERR/ERL documentation says they are 'read-only' but doesn't clarify if ERROR statement can set them

**Affected files:**
- `docs/help/common/language/statements/err-erl-variables.md`
- `docs/help/common/language/statements/error.md`

**Details:**
err-erl-variables.md states:
"- ERR and ERL are read-only variables"
"- ERROR statement sets both ERR (to the specified code) and ERL (to the line where ERROR was executed)"

This seems contradictory - if they're read-only, how does ERROR set them? The documentation should clarify that they're read-only to user code but can be set by the interpreter/ERROR statement.

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

**Description:** Maximum line number inconsistency

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
Documentation states: 'Cannot create line numbers > 65529'
Other BASIC documentation typically uses 65535 as the maximum line number. The value 65529 seems unusual and should be verified.

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

However, the individual setting descriptions in settings.md don't consistently remind readers these are extensions. This is minor but could be clearer.

---
---

#### documentation_inconsistency

**Description:** Shortcuts documentation uses placeholder syntax {{kbd:...}} that may not render correctly

**Affected files:**
- `docs/help/common/shortcuts.md`

**Details:**
The shortcuts.md file uses syntax like {{kbd:run:cli}}, {{kbd:step:curses}}, etc. throughout.

This appears to be a template syntax for a documentation system that would replace these with actual key combinations. However, if this documentation is viewed raw (e.g., in a text editor or basic markdown viewer), these placeholders would be confusing.

The documentation should either:
1. Include actual key combinations in addition to placeholders
2. Have a note explaining the placeholder syntax
3. Be processed by a system that replaces these before display

---
---

#### documentation_inconsistency

**Description:** Inconsistent file naming: write.md vs writei.md for WRITE vs WRITE#

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md documents WRITE (screen output)
writei.md documents WRITE# (file output)

The 'i' suffix in 'writei.md' is not intuitive. Other file I/O statements use different conventions:
- printi-printi-using.md for PRINT#
- input_hash.md for INPUT#

The naming convention is inconsistent across similar file I/O statements.

---
---

#### documentation_inconsistency

**Description:** Inconsistent 'Versions' field formatting

**Affected files:**
- `docs/help/common/language/statements/swap.md`
- `docs/help/common/language/statements/while-wend.md`

**Details:**
SWAP.md: 'Versions: Extended, Disk'
WHILE-WEND.md: No 'Versions' field at all

Most other statements include a Versions field. WHILE-WEND should probably have one for consistency.

---
---

#### documentation_inconsistency

**Description:** Settings documentation mentions 'File scope' as future feature but doesn't clearly mark it

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
In the 'Settings Scope' section:

'1. File scope (highest priority) - Per-file settings (future feature)'

This mentions it's a future feature inline, but the table format makes it look like it's currently available. Should be more clearly marked as not yet implemented, similar to how WAIT and WIDTH have implementation notes.

---
---

#### documentation_inconsistency

**Description:** Incomplete feature availability matrix

**Affected files:**
- `docs/help/common/ui/tk/index.md`
- `docs/help/mbasic/extensions.md`

**Details:**
Tk docs mention 'Some Tk configurations include an immediate mode panel' but Extensions guide doesn't mention this variability. Extensions guide states 'Find and Replace (Tk only)' but Tk docs only mention 'Find' in the menu ({{kbd:find:tk}}), not Replace. This suggests either the feature matrix is incomplete or the Tk docs are missing Replace documentation.

---
---

#### documentation_inconsistency

**Description:** Typo example creates confusion

**Affected files:**
- `docs/help/common/ui/curses/editing.md`

**Details:**
Curses editing doc includes example: 'Typos in line numbers: 10 PRINT "Test"\n1O PRINT "Oops"   ← Letter O instead of zero\nThis is a syntax error! The parser will reject "1O" as an invalid line number.' This is correct, but the formatting with '\n' in the description makes it unclear if this is showing actual newlines or if it's a formatting error in the documentation itself.

---
---

#### documentation_inconsistency

**Description:** Inconsistent documentation of LINE statement

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md lists under 'Input/Output' -> 'Console I/O': 'LINE INPUT - Full line input'

not-implemented.md states: 'LINE - Draw line (GW-BASIC graphics version - not the LINE INPUT statement which IS implemented)'

While technically not contradictory, the capitalization and emphasis in not-implemented.md suggests potential confusion. The features.md should clarify that LINE INPUT is the statement, not LINE alone.

---
---

#### documentation_inconsistency

**Description:** Installation instructions reference different documentation files

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/mbasic/index.md`

**Details:**
getting-started.md references: 'Installation Guide: docs/dev/INSTALLATION_FOR_DEVELOPERS.md - Developer setup'

index.md under 'For Developers' references: 'Installation Guide: docs/dev/INSTALLATION_FOR_DEVELOPERS.md - Developer setup'

Both reference the same file, but getting-started.md is meant for end users while the developer installation guide is specifically for developers. getting-started.md should have end-user installation instructions, not reference developer docs.

---
---

#### documentation_inconsistency

**Description:** CLS statement documentation inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md does not explicitly list CLS in the 'Input/Output' or 'Program Control' sections.

not-implemented.md states: 'Note: Basic CLS (clear screen) IS implemented in MBASIC - see [CLS](../common/language/statements/cls.md). The GW-BASIC extended CLS with optional parameters is not implemented.'

This suggests CLS is implemented but not documented in the features list, creating an incomplete feature inventory.

---
---

#### documentation_inconsistency

**Description:** Inconsistent command examples for CLI mode

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/getting-started.md`
- `docs/help/ui/cli/index.md`

**Details:**
getting-started.md shows CLI prompt as 'Ok':
'10 PRINT "Hello, World!"
20 END
RUN'

cli/index.md also shows 'Ok' prompt:
'Ok
LOAD "MYPROGRAM.BAS"
RUN'

cli/settings.md shows 'Ok' prompt:
'Ok
SHOWSETTINGS'

However, features.md under 'Program Control' -> 'Execution Control' shows 'STOP - Halt execution (resumable)' without any prompt context.

While minor, consistent prompt notation would improve clarity.

---
---

#### documentation_inconsistency

**Description:** Different command syntax examples for same operations

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/ui/cli/index.md`

**Details:**
getting-started.md shows file operations without quotes:
'mbasic program.bas    # Run a file'

cli/index.md shows file operations with quotes:
'LOAD "file.bas" - Load program
SAVE "file.bas" - Save program'

While both may be valid, consistent examples would reduce confusion. The CLI commands require quotes, but the shell command doesn't.

---
---

#### documentation_inconsistency

**Description:** Inconsistent delete line keyboard shortcut documentation

**Affected files:**
- `docs/help/ui/curses/editing.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/editing.md under 'Deleting Lines > Quick Delete (^D)' states: '1. Navigate to the line
2. Press **^D**
3. Line is deleted immediately'

But docs/help/ui/curses/quick-reference.md under 'Editing' states: '**Delete/Backspace** | Delete current line'

This suggests two different methods (^D vs Delete/Backspace) for deleting lines, which may be correct but should be clarified.

---
---

#### documentation_inconsistency

**Description:** Settings keyboard shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/settings.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/settings.md states: '**Keyboard shortcut:** `Ctrl+,`'

But docs/help/ui/curses/quick-reference.md under 'Global Commands' states: '**Menu only** | Settings'

This is contradictory - either there is a Ctrl+, shortcut or it's menu-only.

---
---

#### documentation_inconsistency

**Description:** Keyboard reference table includes unimplemented features

**Affected files:**
- `docs/help/ui/curses/variables.md`

**Details:**
docs/help/ui/curses/variables.md includes a 'Keyboard Reference' table with keys like:
'`u` | Toggle auto-update'
'`e` | Export to file'
'`h` | Help'

However, earlier in the same document under 'Modifying Variables', it states that direct editing is 'Not Implemented'. The keyboard reference should clarify which features are implemented vs planned.

---
---

#### documentation_inconsistency

**Description:** Integration features documented without implementation status

**Affected files:**
- `docs/help/ui/curses/variables.md`

**Details:**
docs/help/ui/curses/variables.md under 'Integration with Editor' documents:
'### Synchronized Display
- Variables window tracks cursor position
- Shows variables referenced on current line
- Highlights undefined variables'

And:
'### Quick Navigation
- Double-click variable name (if mouse enabled)
- Jumps to first usage in code
- Shows all references'

These advanced features are documented as if they exist, but there's no indication of implementation status. Given that simpler features like variable editing are marked 'Not Implemented', these should also be marked if unavailable.

---
---

#### documentation_inconsistency

**Description:** Help keyboard shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/help-navigation.md`
- `docs/help/ui/curses/index.md`

**Details:**
docs/help/ui/curses/help-navigation.md states: 'Press **{{kbd:help:curses}}** anytime to open help.'

But docs/help/ui/curses/index.md states: 'Press **{{kbd:home:curses}}** with cursor on a BASIC keyword for direct help'

This suggests two different shortcuts ({{kbd:help:curses}} for general help, {{kbd:home:curses}} for context-sensitive help), but this distinction should be clarified.

---
---

#### documentation_inconsistency

**Description:** Inconsistent shortcut notation in Quick Reference table

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
feature-reference.md Quick Reference table shows:
- {{kbd:run_program:tk}} / F5 | Run Program
- (menu only) | Stop Program
- (toolbar) | Step Statement
- (toolbar) | Continue

But getting-started.md Essential Shortcuts table shows:
- {{kbd:run_program}} | Run program
- {{kbd:save_file}} | Save file
- {{kbd:smart_insert}} | Insert line between existing lines
- {{kbd:toggle_breakpoint}} | Toggle breakpoint
- {{kbd:toggle_variables}} | Show/hide variables window

The notation is inconsistent - sometimes using :tk suffix, sometimes not.

---
---

#### documentation_inconsistency

**Description:** Document describes itself as design document but uses present tense

**Affected files:**
- `docs/help/ui/tk/settings.md`

**Details:**
settings.md states at the top:
- Implementation Status: The Tk (Tkinter) desktop GUI is planned to provide the most comprehensive settings dialog. **The features described in this document represent planned/intended implementation and are not yet available.** This is a design document for future development.

But then uses present tense throughout:
- 'The settings dialog is designed to be a multi-tabbed window'
- 'Settings are saved to disk automatically when you click OK or Apply'

Should consistently use future tense or conditional language for planned features.

---
---

#### documentation_inconsistency

**Description:** Inconsistent command line examples for starting the GUI

**Affected files:**
- `docs/help/ui/tk/index.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
index.md shows:
- mbasic --ui tk [filename.bas]

getting-started.md shows:
- mbasic --ui tk [filename.bas]
- Or to use the default curses UI:
  mbasic [filename.bas]

The second example in getting-started.md about 'default curses UI' is confusing in a Tk GUI help document and suggests the default is curses, not tk.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation format

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/settings.md`

**Details:**
getting-started.md uses placeholder notation:
"{{kbd:run:web}}", "{{kbd:stop:web}}", "{{kbd:step_line:web}}", "{{kbd:step:web}}", "{{kbd:continue:web}}", "{{kbd:paste:web}}", "{{kbd:select_all:web}}", "{{kbd:copy:web}}", "{{kbd:help:web}}"

But settings.md uses the same placeholder in a different context:
"{{kbd:help:web}}2" (appears to be F12 for developer tools)

The notation is inconsistent - sometimes it's just the placeholder, sometimes it has a number appended. This suggests either incomplete template replacement or inconsistent usage of the kbd placeholder system.

---
---

#### documentation_inconsistency

**Description:** Inconsistent description of Command area behavior

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md states:
"**Important:** The Command area does **NOT** auto-number. It executes immediately."

web-interface.md states:
"- **No automatic line numbering** - commands run immediately"

Both say the same thing, but getting-started.md also includes examples showing pressing Enter to execute, while web-interface.md shows 'Press Enter' in examples but the main description says 'Click Execute'. There's a minor inconsistency about whether you press Enter or click Execute button.

---
---

#### documentation_inconsistency

**Description:** Inconsistent game count in library documentation

**Affected files:**
- `docs/library/games/index.md`
- `docs/library/business/index.md`
- `docs/library/data_management/index.md`
- `docs/library/demos/index.md`
- `docs/library/education/index.md`
- `docs/library/electronics/index.md`
- `docs/library/ham_radio/index.md`

**Details:**
docs/help/ui/web/index.md states:
"- **[Games Library](../../../library/games/index.md)** - 113 classic CP/M era games to download and load!"

But counting the games listed in docs/library/games/index.md, there are exactly 113 games listed (from 23Matches to Word). However, the other library index files (business, data_management, demos, education, electronics, ham_radio) don't provide counts in their descriptions. This is not an inconsistency per se, but worth noting for completeness.

---
---

#### documentation_inconsistency

**Description:** Featured programs list doesn't match actual utilities

**Affected files:**
- `docs/library/index.md`
- `docs/library/utilities/index.md`

**Details:**
docs/library/index.md lists featured utilities: 'Calendar, Unit Converter, Sort, Search, Day of Week Calculator'

But docs/library/utilities/index.md shows:
- Calendar (calendr5.bas) - exists
- 'Unit Converter' - no program with this exact name exists
- Sort (sort.bas) - exists but described as 'BASICODE 2 utility routines collection', not a sort utility
- Search (search.bas) - exists
- 'Day of Week Calculator' - exists as 'dow.bas' but not with that exact name

The featured list uses marketing names that don't match actual program names/descriptions.

---
---

#### documentation_inconsistency

**Description:** Million.bas categorized as utility but described as game

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
In docs/library/utilities/index.md, million.bas is listed as a utility with description:
'Millionaire life simulation game - make financial decisions to accumulate wealth'
Tags: 'simulation, financial, game'

This is clearly described as a game, not a utility. It should likely be in the Games category instead.

---
---

#### documentation_inconsistency

**Description:** Rotate.bas categorized as utility but described as game

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
In docs/library/utilities/index.md, rotate.bas is listed as a utility with description:
'Letter rotation puzzle game - order letters A-P by rotating groups clockwise'
Tags: 'puzzle, game, logic'

This is clearly described as a game, not a utility. It should likely be in the Games category instead.

---
---

#### documentation_inconsistency

**Description:** Inconsistent command syntax examples

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`

**Details:**
The guide shows SET command examples in two different formats:
1. With quotes: SET "variables.case_conflict" "first_wins"
2. Without quotes in some contexts: 'variables.case_conflict'

While both may be valid, the inconsistency could confuse users about whether quotes are required.

---
---

#### documentation_inconsistency

**Description:** Duplicate installation documentation

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/INSTALLATION.md`

**Details:**
Two installation files exist:
1. docs/user/INSTALL.md - Full installation guide
2. docs/user/INSTALLATION.md - Redirect file pointing to INSTALL.md

The INSTALLATION.md file states: 'This file exists for compatibility with different documentation linking conventions. All installation documentation has been consolidated in [INSTALL.md](INSTALL.md).'

While this is intentional for compatibility, it creates potential maintenance burden if links need updating.

---
---

#### documentation_inconsistency

**Description:** Library statistics may be outdated

**Affected files:**
- `docs/library/index.md`

**Details:**
The main library index states:
'Library Statistics:
- 202 programs from the 1970s-1980s'

This is a hard-coded number that will become outdated as programs are added or removed. The actual count should be verified against the program files, or the documentation should note this is approximate.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut placeholder format between documents

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md uses: '{{kbd:toggle_variables}}' format throughout

TK_UI_QUICK_START.md uses both:
- '**{{kbd:run_program}}**' (with bold)
- '{{kbd:toggle_variables}}' (without bold)
- '{{kbd:file_save}}' (without bold)

Inconsistent styling of the same placeholder type across documents.

---
---

#### documentation_inconsistency

**Description:** Mouse support status for Curses UI unclear

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'User Interface' table:

Row 'Mouse support' shows:
- Curses: ⚠️
- Notes: 'Curses: limited, terminal-dependent'

This correctly uses ⚠️ with explanation. However, in 'Detailed UI Descriptions' under Curses Limitations: 'Limited mouse support' is mentioned without explaining what works vs what doesn't.

The documentation should clarify what mouse operations ARE supported in Curses (e.g., clicking line numbers for breakpoints?) vs what isn't.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation in table vs text

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
In the 'Essential Keyboard Shortcuts' table, shortcuts are shown as:
'**{{kbd:run_program}}**' (with bold and placeholder)

But in the text below, they're referenced as:
'Press **{{kbd:run_program}}** to run' (bold around entire phrase including 'Press')
'Use Smart Insert ({{kbd:smart_insert}})' (no bold on placeholder)
'Press **{{kbd:toggle_variables}}**' (bold around Press and placeholder)

The styling is inconsistent - sometimes the placeholder is bolded, sometimes the entire instruction is bolded, sometimes neither.

---
---

#### documentation_inconsistency

**Description:** Duplicate installation documentation files listed

**Affected files:**
- `docs/user/README.md`

**Details:**
Under 'Getting Started' section:

- **[INSTALL.md](INSTALL.md)** - Installation guide
- **[INSTALLATION.md](INSTALLATION.md)** - Alternative installation instructions

Two separate installation files are listed with slightly different descriptions ('guide' vs 'alternative instructions'). This suggests either:
1. Redundant documentation that should be merged
2. Different installation methods that should be clearly distinguished
3. One file is outdated

The README doesn't explain why there are two installation documents or when to use which one.

---


## Summary

- Total issues found: 573
- Code/Comment conflicts: 225
- Other inconsistencies: 348
- Ignored (already reviewed): 99
---

## Summary

- Total documentation issues: 228
- High severity: 13
- Medium severity: 91
- Low severity: 124
