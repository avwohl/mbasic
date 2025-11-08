# Documentation Changes Required (v14)

Generated from docs_inconsistencies_report-v14.md
Date: 2025-11-08

**These items require documentation updates only (comments, docstrings, markdown files).**
**No changes to code behavior.**

---

#### code_vs_comment

**Description:** Comment describes ERL renumbering behavior that contradicts MBASIC manual specification

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~570 states: 'MBASIC manual specifies: if ERL appears on left side of comparison operator (=, <>, <, >, <=, >=), the right-hand number is a line number reference.'

But then at line ~573: 'IMPORTANT: Current implementation renumbers for ANY binary operator with ERL on left, including arithmetic (ERL + 100, ERL * 2). This is broader than the manual specifies.'

The comment acknowledges the code intentionally deviates from the manual specification. The _renum_erl_comparison() method at line ~595 checks for 'BinaryOpNode' without filtering by operator type, confirming it handles ALL binary operators, not just comparisons. This is documented as intentional but creates a discrepancy between stated spec and implementation.

---

#### code_vs_comment

**Description:** Comment about CLEAR error handling contradicts actual behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1240 states:
"# Close all open files
# Note: Errors during file close are silently ignored (bare except: pass)"

The code shows:
try:
    file_obj = self.runtime.files[file_num]
    if hasattr(file_obj, 'close'):
        file_obj.close()
except:
    pass

This matches the comment. However, later at line ~1890 in execute_reset, there's a contrasting comment:
"# Close all open files (errors propagate to caller)"

And the code:
for file_num in list(self.runtime.files.keys()):
    self.runtime.files[file_num]['handle'].close()
    del self.runtime.files[file_num]

The comment in CLEAR says errors are silently ignored, and the comment in RESET says errors propagate. This is an intentional difference between the two statements, but the CLEAR comment should clarify this is different from RESET's behavior.

---

#### code_vs_comment

**Description:** serialize_let_statement docstring describes LET keyword handling but the implementation doesn't emit LET keyword at all

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring says: 'Serialize LET or assignment statement.

LetStatementNode represents both:
- Explicit LET statements: LET A=5
- Implicit assignments: A=5 (without LET keyword)'

But the implementation code:
```python
def serialize_let_statement(self, stmt: ast_nodes.LetStatementNode) -> str:
    result = ""
    # Variable
    var_text = self.serialize_expression(stmt.variable)
    result += var_text
    # Equals sign
    result += self.emit_token("=", None, "LetOperator")
```

There is NO code that emits the 'LET' keyword. The function always serializes as implicit assignment (A=5) regardless of whether the original had LET or not. This is a significant behavior mismatch.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime resets PC when paused_at_breakpoint=True, but explanation contradicts typical breakpoint resume behavior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sync_program_to_runtime method:
"# Restore PC only if execution is running AND not paused at breakpoint
# When paused_at_breakpoint=True, we reset PC to halted because the breakpoint PC
# is stored separately and will be restored when continuing from the breakpoint."

This comment suggests breakpoint PC is stored separately and will be restored later, but there's no visible code in this method or nearby that shows where this separate storage happens or how restoration works. This needs clarification about the breakpoint resume mechanism.

---

#### code_vs_comment_conflict

**Description:** Comment claims help navigation keys are hardcoded and not loaded from keybindings, but the code actually does load keybindings via HelpMacros

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~90 states:
"Note: Help navigation keys are hardcoded here and in keypress() method, not loaded from keybindings. The help widget uses fixed keys (U for back, / for search, ESC/Q to exit) to avoid dependency on keybinding configuration. HelpMacros does load the full keybindings from JSON (for {{kbd:action}} macro expansion in help content), but the help widget itself doesn't use those loaded keybindings."

However, HelpWidget.__init__ creates HelpMacros instance:
self.macros = HelpMacros('curses', help_root)

And HelpMacros._load_keybindings() does load keybindings from JSON:
keybindings_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"

The comment is technically correct that help_widget.py doesn't use the loaded keybindings for its own navigation (it uses hardcoded keys in keypress()), but the phrasing is confusing since HelpMacros is instantiated within HelpWidget.

---

#### code_vs_comment_conflict

**Description:** MAINTENANCE comment lists 3 places to update but implementation has more locations

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~90:
"MAINTENANCE: If help navigation keys change, update:
1. This footer text (line below)
2. The keypress() method (handle_key mapping around line 150+)
3. Help documentation that mentions these keys"

But the footer text appears in multiple places:
1. Line ~92: Initial footer in __init__
2. Line ~127: Footer in _cancel_search()
3. Line ~138: Footer in _execute_search() when no results
4. Line ~165: Footer in _execute_search() with results

The maintenance comment only mentions 'this footer text' but there are 4 different footer text assignments with hardcoded keys.

---

#### code_vs_comment

**Description:** Comment claims control characters modify text via deletion, but backspace/delete are not control characters in the traditional sense

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1048: 'Allow control characters (backspace, delete) - these modify text via deletion, not by inserting printable characters, so they pass validation'
Code: 'if char_code in (8, 127):  # Backspace (0x08) or Delete (0x7F)'
Backspace (0x08) and Delete (0x7F) are technically control characters, but the comment's phrasing 'Allow control characters' is misleading since the function blocks OTHER control characters later. The comment should say 'Allow backspace and delete' rather than generalizing to 'control characters'.

---

#### code_vs_comment

**Description:** Comment claims blank line won't be saved but contradicts earlier behavior where _save_editor_to_program is called on key release

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1245: 'DON'T save to program yet - the line is blank and would be filtered out by _save_editor_to_program() which skips blank lines. Just position the cursor on the new line so user can start typing. The line will be saved to program when: 1. User types content and triggers _on_key_release -> _save_editor_to_program()'
However, earlier in _on_key_press (line ~1047), there's: 'self.root.after(10, self._remove_blank_lines)' which would remove this blank line. The comment suggests the blank line persists until user types, but _remove_blank_lines would delete it almost immediately after insertion.

---

#### code_vs_comment

**Description:** Complex comment about avoiding interpreter.start() may indicate fragile code design

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method around line 1115:
"# Initialize interpreter state for execution
# NOTE: Don't call interpreter.start() because it calls runtime.setup()
# which resets PC to the first statement. The RUN command has already
# set PC to the correct line (e.g., RUN 120 sets PC to line 120).
# We only need to clear the halted flag and mark this as first line.
# This avoids the full initialization that start() does:
#   - runtime.setup() (rebuilds tables, resets PC)
#   - Creates new InterpreterState
#   - Sets up Ctrl+C handler
self.runtime.halted = False  # Clear halted flag to start execution
self.interpreter.state.is_first_line = True"

This comment describes working around the normal initialization flow, which suggests either:
1. The interpreter.start() API is not designed correctly for this use case
2. The code is bypassing proper initialization in a fragile way
3. There should be a separate API method for resuming vs starting

This needs architectural review.

---

#### code_vs_comment

**Description:** _parse_line_number() docstring and comment claim MBASIC 5.21 requires whitespace after line number, but regex allows end-of-string without whitespace

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment in _parse_line_number() says:
"# Match line number followed by whitespace OR end of string (both valid)
# Valid: "10 PRINT" (whitespace after), "10" (end after), "  10  REM" (leading whitespace ok)
# Invalid: "10REM" (no whitespace), "ABC10" (non-digit prefix), "" (empty after strip)
# MBASIC 5.21 requires whitespace (or end of line) between line number and statement"

The regex is: r'^(\d+)(?:\s|$)'

This matches either whitespace (\s) OR end-of-string ($). The comment says 'MBASIC 5.21 requires whitespace (or end of line)' which is consistent with the regex. However, the phrase 'or end of line' is ambiguous - does it mean end-of-string (which the regex checks) or a newline character? If MBASIC 5.21 truly requires whitespace between line number and statement, then a line like '10' with nothing after should be valid (just a line number, no statement), which the regex allows. This appears consistent, but needs verification that MBASIC 5.21 actually allows bare line numbers.

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

#### documentation_inconsistency

**Description:** Contradictory information about loop termination timing

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
The documentation states:
"Loop Termination:
The loop terminates when the variable passes the ending value, considering the STEP direction:
- Positive STEP (or no STEP): Loop terminates when variable > ending value
- Negative STEP: Loop terminates when variable < ending value

For example:
- FOR I = 1 TO 10 terminates when I > 10 (after I reaches 10 and increments to 11)
- FOR I = 10 TO 1 STEP -1 terminates when I < 1 (after I reaches 1 and decrements to 0)"

This is contradictory. The examples suggest the loop body executes when I=10 and I=1 respectively, THEN increments/decrements and tests. But standard BASIC behavior tests BEFORE executing the loop body. The loop should terminate when the test fails BEFORE execution, not after. This needs clarification about whether the test is before or after loop body execution.

---

#### documentation_inconsistency

**Description:** Tk UI documentation claims Find and Replace functionality, but extensions.md states Find is Tk-only with no mention of Replace

**Affected files:**
- `docs/help/common/ui/tk/index.md`
- `docs/help/mbasic/extensions.md`

**Details:**
tk/index.md states:
- **Find and Replace** - Search and replace text (Ctrl+F/Ctrl+H)

But extensions.md states:
- **Find** - ❌ | ✅ (Tk) | Extension

And in the feature comparison table, only 'Find' is mentioned for Tk, not 'Replace'.

---

#### documentation_inconsistency

**Description:** Variables Window shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md states Variables Window uses 'Ctrl+W', but quick-reference.md lists it as 'Menu only' under Global Commands.

---

#### documentation_inconsistency

**Description:** Settings Widget shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md and settings.md state Settings Widget uses 'Ctrl+,', but quick-reference.md lists it as 'Menu only' under Global Commands.

---

#### documentation_inconsistency

**Description:** Tk UI Stop/Interrupt shortcut conflict

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`

**Details:**
Tk feature-reference.md states Stop/Interrupt uses '{{kbd:cut:tk}}' which is typically Ctrl+X, but this is also listed as the Cut operation shortcut in the Cut/Copy/Paste section. This creates a conflict where the same shortcut is documented for two different operations.

---

#### documentation_inconsistency

**Description:** Tk GUI features documented as implemented but settings.md indicates they are planned/not yet available

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/getting-started.md`
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`

**Details:**
Multiple Tk docs describe features like Smart Insert ({{kbd:smart_insert}}), Variables Window ({{kbd:toggle_variables}}), Execution Stack ({{kbd:toggle_stack}}), and Renumber ({{kbd:renumber}}) as if they are currently available. However, settings.md states: 'Implementation Status: The Tk (Tkinter) desktop GUI is planned to provide the most comprehensive settings dialog. The features described in this document represent planned/intended implementation and are not yet available.' This creates confusion about what is actually implemented vs planned.

---

#### documentation_inconsistency

**Description:** Contradictory information about localStorage usage in Web UI

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
Under 'Local Storage - Currently Implemented', features.md states:
'Programs stored in Python server memory (session-only, lost on page refresh)'
'Recent files list stored in browser localStorage'

But under 'Security Features - Data Protection - Currently Implemented', it states:
'Local storage only (browser localStorage)'

And under 'Session Management' it says:
'Programs are stored locally in browser storage only.'

These statements contradict each other - are programs stored in Python server memory OR in browser localStorage?

---

### 🟡 Medium Severity

#### documentation_inconsistency

**Description:** Version number inconsistency between setup.py and ast_nodes.py documentation

**Affected files:**
- `setup.py`
- `src/ast_nodes.py`

**Details:**
setup.py line 3: 'Setup script for MBASIC 5.21 Interpreter (version 0.99.0)'
setup.py line 5: 'Package version 0.99.0 reflects approximately 99% implementation status (core complete).'
setup.py line 16: 'version="0.99.0"'

ast_nodes.py line 3: 'Note: 5.21 refers to the Microsoft BASIC-80 language version, not this package version.'

The setup.py conflates MBASIC 5.21 (the language being interpreted) with package version 0.99.0 (the interpreter implementation). The ast_nodes.py correctly clarifies that 5.21 is the language version, not the package version. This creates confusion about what '5.21' means in different contexts.

---

#### code_vs_comment

**Description:** Comment in EOF() method describes mode 'I' as 'Input' but implementation comment says it's 'binary input mode'

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line ~570: Comment says "Mode 'I' means 'Input' in MBASIC syntax" but later says "Mode 'I' = binary input mode, where files are opened in binary mode ('rb')". The distinction between 'Input' (sequential text) vs 'binary input' is unclear. The code checks for ^Z (ASCII 26) which is CP/M binary EOF marker, suggesting 'I' is specifically binary mode, not general input.

---

#### code_vs_comment

**Description:** Comment about trailing_minus_only behavior is inconsistent with variable name and implementation

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line ~145: Comment says "trailing_minus_only: - at end, adds - for negative or space for non-negative (always 1 char)" but the spec parsing at line ~185 shows it's set when format_str[i] == '-'. The name 'trailing_minus_only' suggests it only adds minus, but comment says it adds space for non-negative. Implementation at line ~340 confirms it adds space for positive: "result_parts.append('-' if is_negative else ' ')". The 'only' in the name is misleading.

---

#### code_vs_comment

**Description:** EOF() docstring says it returns -1 for EOF but doesn't mention ^Z behavior for all file types

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line ~545: Docstring says "Returns -1 if at EOF, 0 otherwise" and mentions ^Z for mode 'I' files. However, the implementation only checks ^Z for mode 'I' (binary input). The docstring should clarify that ^Z is ONLY checked for mode 'I' files, not all files. Text mode files ignore ^Z.

---

#### code_vs_comment

**Description:** Comment about asterisk_fill counting as positions conflicts with padding logic

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line ~163: Comment says "spec['digit_count'] += 2  # Counts as 2 positions" for ** prefix. Line ~167 says "spec['digit_count'] += 2  # Counts as 2 positions" for $$ prefix. However, at line ~323 the code does "if spec['asterisk_fill']: result_parts.append('*' * max(0, padding_needed))" which fills with asterisks. The digit_count increment suggests ** reserves 2 positions, but the padding logic suggests it fills variable space. This is confusing about whether ** is fixed width or variable.

---

#### Documentation inconsistency

**Description:** Contradictory information about ProgramManager.load_from_file() return value

**Affected files:**
- `src/editing/manager.py`
- `src/file_io.py`

**Details:**
src/editing/manager.py docstring states:
"Note: ProgramManager.load_from_file() returns (success, errors) tuple where errors
is a list of (line_number, error_message) tuples for direct UI error reporting,
while FileIO.load_file() returns raw file text."

However, the actual implementation in manager.py shows:
def load_from_file(self, filename: str) -> Tuple[bool, List[Tuple[int, str]]]:
    """Load program from file.
    Returns:
        Tuple of (success, errors)
        success: True if at least one line loaded successfully
        errors: List of (line_number, error_message) for failed lines"""

The module docstring says errors is a list of tuples, but the function docstring says the same thing. Both are consistent with implementation. However, the module docstring creates confusion by contrasting with FileIO.load_file() which actually returns a string, not a tuple.

---

#### Documentation inconsistency

**Description:** Security warning about user_id validation appears in multiple places with slightly different wording

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
In SandboxedFileSystemProvider class docstring:
"Security:
- Per-user isolation via user_id keys in class-level storage
  IMPORTANT: Caller must ensure user_id is securely generated/validated
  to prevent cross-user access (e.g., use session IDs, not user-provided values)"

In __init__ docstring:
"Args:
    user_id: Unique identifier for this user/session
            SECURITY: Must be securely generated/validated (e.g., session IDs)
            to prevent cross-user access. Do NOT use user-provided values."

The warnings are consistent in meaning but use different phrasing ('ensure user_id is securely generated/validated' vs 'Must be securely generated/validated'). While not a major issue, standardizing the security warning language would improve clarity.

---

#### code_vs_comment

**Description:** Comment claims PC is not saved/restored, but this contradicts the documented behavior for control flow statements

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Comment at line ~200 states: 'Note: We do not save/restore the PC before/after execution. This allows statements like RUN to change execution position. Control flow statements (GOTO, GOSUB) can also modify PC but may produce unexpected results (see help text).'

However, the help text in _show_help() states: 'GOTO, GOSUB, and control flow statements are not recommended (they will execute but may produce unexpected results)'

The comment suggests this is intentional design to allow RUN to work, but doesn't explain why control flow produces 'unexpected results' or what those results are. The implementation executes statements at line 0, so GOTO/GOSUB would try to jump to other line numbers, which may not exist in the immediate context.

---

#### code_vs_comment

**Description:** Extensive documentation about numbered line editing feature requirements, but no validation that these requirements are actually enforced

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Lines ~100-110 contain detailed documentation:
'This feature requires the following UI integration:
- interpreter.interactive_mode must reference the UI object (checked with hasattr)
- UI.program must have add_line() and delete_line() methods (validated, errors if missing)
- UI._refresh_editor() method to update the display (optional, checked with hasattr)
- UI._highlight_current_statement() for restoring execution highlighting (optional, checked with hasattr)'

The code does check for these attributes with hasattr(), but the comment claims 'validated, errors if missing' for add_line/delete_line. However, the actual validation only happens AFTER checking if line_content exists (line ~125-130). If line_content is empty (delete case), it checks delete_line. If line_content exists (add case), it checks add_line. But it doesn't validate BOTH methods exist upfront as the documentation implies.

---

#### code_vs_comment

**Description:** Comment claims program line editing adds complete line with line number, but the code constructs it

**Affected files:**
- `src/immediate_executor.py`

**Details:**
At line ~130, comment states:
'# Add/update line - add_line expects complete line text with line number
complete_line = f"{line_num} {line_content}"
success, error = ui.program.add_line(line_num, complete_line)'

The comment says add_line 'expects complete line text with line number', but then the code passes BOTH line_num as first argument AND complete_line (which includes line_num) as second argument. This suggests either:
1. The comment is wrong about what add_line expects
2. The code is passing redundant information
3. add_line signature is: add_line(line_num, complete_line_text)

Without seeing the add_line implementation, it's unclear if passing line_num twice is intentional or if the comment is outdated.

---

#### code_vs_comment

**Description:** Comment claims EDIT command digits are 'silently ignored' but code doesn't implement this behavior

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~680 states: 'INTENTIONAL BEHAVIOR: When digits are entered, they are silently ignored (no output, no cursor movement, no error). This preserves MBASIC compatibility where digits are reserved for count prefixes in the full EDIT implementation.'

However, the cmd_edit() implementation has no code to handle digit input specially. The while loop at line ~720 only handles specific commands (Space, D, I, X, H, E, Q, L, A, C) and does not have any case for digit characters. Digits would fall through to no handler, which may cause unexpected behavior rather than being 'silently ignored'.

---

#### code_vs_comment

**Description:** Comment about CONT failure condition doesn't match actual implementation check

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~350 states: 'IMPORTANT: CONT will fail with "?Can't continue" if the program has been edited (lines added, deleted, or renumbered) because editing clears the GOSUB/RETURN and FOR/NEXT stacks'

However, cmd_cont() at line ~360 only checks: 'if not self.program_runtime or not self.program_runtime.stopped:'

The code does NOT check if stacks have been cleared. It only checks if runtime exists and if stopped flag is set. If clear_execution_state() clears the stacks but leaves stopped=True, CONT would attempt to continue with empty stacks, potentially causing crashes rather than showing "?Can't continue". The comment describes a safety mechanism that isn't actually implemented in the check.

---

#### code_vs_comment_conflict

**Description:** Comment claims GOTO/GOSUB in immediate mode are 'not recommended' but code fully supports them with documented special semantics

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~235 says: 'This is the intended behavior but may be unexpected, hence "not recommended".' However, the code implements full support for GOTO/GOSUB with well-defined behavior (execute and jump, then restore PC). The comment suggests discouragement but the implementation is complete and intentional.

---

#### code_vs_comment_conflict

**Description:** Comment describes PC restoration behavior but doesn't explain why GOTO/GOSUB execution during execute_statement is useful if immediately reverted

**Affected files:**
- `src/interactive.py`

**Details:**
Comments at lines ~230-237 explain: 'They execute and jump during execute_statement(), but we restore the\noriginal PC afterward to preserve CONT functionality.' This creates confusion: if the PC is restored, what was the point of executing the GOTO/GOSUB? The comment doesn't explain that side effects (like GOSUB pushing return address) may still occur.

---

#### code_vs_comment

**Description:** Comment describes skip_next_breakpoint_check behavior incorrectly - says it's set AFTER returning state, but code sets it BEFORE returning

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 62-65 says:
"Set to True AFTER halting at a breakpoint (set after returning state).
On next execution, if still True, allows stepping past the breakpoint once,
then clears itself to False. Prevents re-halting on same breakpoint."

But code at lines 449-452 shows:
if at_breakpoint:
    if not self.state.skip_next_breakpoint_check:
        self.runtime.halted = True
        self.state.skip_next_breakpoint_check = True
        return self.state

The flag is set to True BEFORE returning state (line 451), not after.

---

#### code_vs_comment

**Description:** Comment at line 1046 says 'return_stmt is 0-indexed offset' but then describes len(statements) as valid, which would be out of bounds for 0-indexed array

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 1046-1054 says:
"return_stmt is 0-indexed offset into statements array.
Valid range: 0 to len(statements) (inclusive).
- 0 to len(statements)-1: Normal statement positions
- len(statements): Special sentinel - GOSUB was last statement on line, so RETURN
  continues at next line. This value is valid because PC can point one past the
  last statement to indicate 'move to next line' (handled by statement_table.next_pc).
Values > len(statements) indicate the statement was deleted (validation error)."

This is internally consistent but confusing terminology. If it's '0-indexed offset', then len(statements) is not a valid index (it's one past the end). The comment should say 'position' or 'offset that can be one past the end' rather than '0-indexed offset' which implies array indexing semantics.

---

#### code_vs_comment

**Description:** Comment describes RESUME 0 as distinct from RESUME, but code treats them identically

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1090 states:
"# RESUME or RESUME 0 - retry the statement that caused the error
# Note: MBASIC allows both 'RESUME' and 'RESUME 0' as equivalent syntactic forms.
# Parser preserves the distinction (None vs 0) for source text regeneration,
# but runtime execution treats both identically."

The code checks:
if stmt.line_number is None or stmt.line_number == 0:

This is consistent with the comment, but the comment's phrasing "Parser preserves the distinction (None vs 0)" suggests there might be a distinction that matters elsewhere. The comment is accurate but could be clearer about why the distinction is preserved if execution is identical.

---

#### code_vs_comment

**Description:** Comment about NEXT validation describes sentinel value incorrectly

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~950 states:
"# return_stmt is 0-indexed offset into statements array.
# Valid range:
#   - 0 to len(statements)-1: Normal statement positions (existing statements)
#   - len(statements): Special sentinel value - FOR was last statement on line,
#                      continue execution at next line (no more statements to execute on current line)
#   - > len(statements): Invalid - indicates the statement was deleted
#
# Validation: Check for strictly greater than (== len is OK as sentinel)"

The code checks:
if return_stmt > len(line_statements):
    raise RuntimeError(...)

This allows return_stmt == len(line_statements) as valid (sentinel). However, the comment describes this as "FOR was last statement on line" but doesn't explain why this would be stored as len(statements) rather than len(statements)-1. The comment may be describing implementation details that aren't obvious from the code alone.

---

#### code_vs_comment

**Description:** Comment about OPTION BASE enforcement mentions 'strictly enforced' but doesn't explain all edge cases

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1310 states:
"MBASIC 5.21 restrictions (strictly enforced):
- OPTION BASE can only be executed once per program run
- Must be executed BEFORE any arrays are dimensioned (implicit or explicit)
- Violating either condition raises 'Duplicate Definition' error"

The code checks:
if self.runtime.option_base_executed:
    raise RuntimeError("Duplicate Definition")
if len(self.runtime._arrays) > 0:
    raise RuntimeError("Duplicate Definition")

The comment is accurate, but the later comment at line ~1320 adds important clarification:
"# Note: The check len(self.runtime._arrays) > 0 catches all array creation because both
# explicit DIM and implicit array access (via set_array_element) update runtime._arrays."

This additional detail should be in the main docstring for completeness.

---

#### code_vs_comment

**Description:** Comment about CP/M encoding is technically incorrect about character meaning preservation

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1570 states:
"Encoding:
Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
Unicode U+0000-U+00FF, allowing round-trip byte preservation.
Note: CP/M systems often used code pages like CP437 or CP850 for characters
128-255, which do NOT match latin-1. Latin-1 preserves the BYTE VALUES but
not necessarily the CHARACTER MEANING for non-ASCII CP/M text. Conversion
may be needed for accurate display of non-English CP/M files."

The comment correctly states that latin-1 preserves byte values but not character meaning. However, it says "Latin-1 preserves the BYTE VALUES but not necessarily the CHARACTER MEANING" which could be misread as "sometimes preserves meaning". It should say "Latin-1 preserves BYTE VALUES but NEVER preserves CHARACTER MEANING for CP437/CP850 encoded text" to be clearer.

---

#### code_vs_comment

**Description:** Comment in execute_cont() mentions BreakException handler behavior but this code doesn't show that handler

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_cont() docstring says:
"Note: execute_stop() moves NPC to PC for resume, while BreakException handler
does not update PC, which affects whether CONT can resume properly."

This comment references a BreakException handler that is not visible in this code file. The comment implies there's an inconsistency in how STOP vs Break (Ctrl+C) handle PC/NPC, but without seeing the BreakException handler code, we cannot verify if this is accurate or if it's outdated information from a refactoring.

---

#### code_vs_comment

**Description:** Comment in execute_list() warns about line_text_map sync issues but doesn't explain how to detect or handle them

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_list() docstring says:
"Implementation note: Outputs from line_text_map (original source text), not regenerated from AST.
This preserves original formatting/spacing/case. The line_text_map is maintained by ProgramManager
and should be kept in sync with the AST during program modifications (add_line, delete_line, RENUM, MERGE).
If ProgramManager fails to maintain this sync, LIST output may show stale or incorrect line text."

The comment warns about potential sync issues but the code has no validation or error handling for this case. If line_text_map can get out of sync (as the comment warns), the code should either: (1) validate sync and raise an error, (2) fall back to regenerating from AST, or (3) the comment should explain why this is acceptable. Currently it just silently outputs potentially incorrect data.

---

#### Code vs Documentation inconsistency

**Description:** ConsoleIOHandler.input_char() has complex fallback logic for Windows without msvcrt that calls input(), but this defeats the purpose of single-character input

**Affected files:**
- `src/iohandler/console.py`

**Details:**
Code has extensive fallback:
"# Fallback for Windows without msvcrt: use input() with severe limitations
# WARNING: This fallback calls input() which:
# - Waits for Enter key (defeats the purpose of single-char input)
# - Returns the entire line, not just one character"

This fallback behavior is so different from the documented interface that it essentially breaks the contract of input_char(). The method is supposed to return a single character, but the fallback returns an entire line. This is documented in comments but creates a severe API inconsistency.

---

#### Code vs Comment conflict

**Description:** Comment claims SimpleKeywordCase validates policy strings and auto-corrects invalid values to force_lower, but this validation behavior is not visible in the lexer code itself

**Affected files:**
- `src/lexer.py`

**Details:**
In create_keyword_case_manager() docstring:
"Note: SimpleKeywordCase validates policy strings in its __init__ method. Invalid
policy values (not in: force_lower, force_upper, force_capitalize) are automatically
corrected to force_lower. See src/simple_keyword_case.py for implementation."

However, the actual SimpleKeywordCase class is not shown in the provided code, so we cannot verify this claim. The comment references external behavior that may or may not exist.

---

#### Code vs Comment conflict

**Description:** Inconsistent handling of # character: comment says it's part of identifier type suffix, but code has special logic to split it back out for file I/O keywords

**Affected files:**
- `src/lexer.py`

**Details:**
In read_identifier() docstring:
"Identifiers can contain letters, digits, and end with type suffix $ % ! #
In MBASIC, $ % ! # are considered part of the identifier."

But later in the same function, there's special case handling:
"# Special case: File I/O keywords followed by # (e.g., PRINT#1)
# MBASIC allows 'PRINT#1' with no space, which should tokenize as:
#   PRINT (keyword) + # (operator) + 1 (number)
# The read_identifier() method treated # as a type suffix and consumed it,
# so we now have 'PRINT#' as ident. For file I/O keywords, we split it back out"

This shows # is NOT always part of the identifier as the docstring claims - it depends on context.

---

#### Code vs Comment conflict

**Description:** Comment claims REM/REMARK are keywords but APOSTROPHE is a distinct token type, but the actual distinction and reasoning is unclear

**Affected files:**
- `src/lexer.py`

**Details:**
Comment in tokenize():
"# Apostrophe comment - distinct token type (unlike REM/REMARK which are keywords)"

This implies a meaningful distinction, but the code shows both are handled specially:
- Apostrophe: creates APOSTROPHE token with comment text
- REM/REMARK: creates REM/REMARK token (keyword type) but replaces value with comment text

The functional difference is minimal - both end up as tokens containing comment text. The comment suggests a more significant architectural difference than actually exists.

---

#### code_vs_comment

**Description:** Comment claims RND and INKEY$ are the only functions that can be called without parentheses in MBASIC 5.21, but this is contradicted by the code implementation

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line 11-12 states:
"Exception: Only RND and INKEY$ can be called without parentheses in MBASIC 5.21
  (this is specific to these two functions, not a general MBASIC feature)"

However, the code at lines 1044-1055 shows RND can be called without parentheses:
"# RND can be called without parentheses - MBASIC 5.21 compatibility feature"

And at lines 1057-1063 shows INKEY$ can be called without parentheses:
"# INKEY$ can be called without parentheses - MBASIC 5.21 compatibility feature"

But the comment says this is 'specific to these two functions', while the implementation treats them as special cases with explicit checks. The comment implies this is a documented MBASIC 5.21 feature, but the code comments suggest it's a 'compatibility feature' which may indicate it's an interpreter-specific extension rather than a standard MBASIC 5.21 feature.

---

#### code_vs_comment

**Description:** Comment about semicolon handling contradicts MBASIC standard behavior

**Affected files:**
- `src/parser.py`

**Details:**
In parse_line() at lines 267-274, there's a comment:
"# Allow trailing semicolon at end of line only (treat as no-op).
# Context matters: Semicolons WITHIN PRINT/LPRINT are item separators (parsed there),
# but semicolons BETWEEN statements are NOT valid in MBASIC.
# MBASIC uses COLON (:) to separate statements, not semicolon (;)."

This comment states that semicolons between statements are NOT valid in MBASIC, but then the code at line 270 allows a trailing semicolon:
"self.advance()"

And at lines 271-274, it checks if there's more after the semicolon and raises an error if so. This suggests the parser is being lenient by allowing trailing semicolons, which may not match actual MBASIC 5.21 behavior. The comment should clarify whether this is a compatibility extension or if MBASIC 5.21 actually allows trailing semicolons.

---

#### code_vs_comment

**Description:** Comment about PRINT USING semicolon requirement contradicts flexible parsing in parse_print_using

**Affected files:**
- `src/parser.py`

**Details:**
In parse_print_using() at lines 1327-1328, the comment states:
"Note: Semicolon after format string is required (separates format from value list)."

And at lines 1336-1338, the code enforces this:
"if not self.match(TokenType.SEMICOLON):
    raise ParseError(f"Expected ';' after PRINT USING format string at line {self.current().line}")"

However, in the expression parsing loop at lines 1343-1357, the code allows semicolons as optional separators between expressions:
"# Check for separator first (skip it)
if self.match(TokenType.SEMICOLON):
    self.advance()"

This suggests semicolons are treated as optional separators in the value list, which may not match MBASIC 5.21 behavior. The comment should clarify whether semicolons are required or optional between values in the PRINT USING value list.

---

#### code_vs_comment

**Description:** Comment describes INPUT; syntax behavior incorrectly

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1050 states:
"Note: The semicolon immediately after INPUT keyword (INPUT;) suppresses
the default '?' prompt. The LINE modifier allows reading an entire line
including commas without treating them as delimiters."

However, the code at lines ~1060-1063 shows:
```
suppress_question = False
if self.match(TokenType.SEMICOLON):
    suppress_question = True
    self.advance()
```

Then at lines ~1078-1086, the comment contradicts itself:
"# Note: In MBASIC 5.21, the separator after prompt affects '?' display:
# - INPUT "Name"; X  displays "Name? " (semicolon AFTER prompt shows '?')
# - INPUT "Name", X  displays "Name " (comma AFTER prompt suppresses '?')
# Different behavior: INPUT; (semicolon IMMEDIATELY after INPUT keyword, no prompt)
# suppresses the default '?' prompt entirely (tracked by suppress_question flag above)."

The second comment clarifies that INPUT; suppresses the '?' prompt entirely, but the first comment says it "suppresses the default '?' prompt" without explaining the distinction between INPUT; (no prompt at all) vs INPUT "prompt"; (prompt with '?').

---

#### code_vs_comment

**Description:** MID$ assignment comment incorrectly describes lexer tokenization

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1820-1826 states:
"Note: The lexer tokenizes 'MID$' in source as a single MID token (the $ is part
of the keyword, not a separate token)."

Then the code at line ~1828 shows:
```
token = self.current()  # MID token (represents 'MID$' from source)
```

This comment claims the lexer tokenizes 'MID$' as a MID token, but without seeing the lexer code, we cannot verify this. In many BASIC implementations, MID$ is tokenized as MID with $ as part of the keyword name. The comment should clarify whether the token type is literally 'MID' or 'MID$' or something else.

---

#### code_vs_comment

**Description:** IF statement ELSE clause parsing has complex lookahead logic that may not match all documented cases

**Affected files:**
- `src/parser.py`

**Details:**
The parse_if method has extensive lookahead logic for distinguishing :ELSE from statement separator colons (lines ~1530-1600). The comment at line ~1515 lists syntax variations:
"- IF condition THEN line_number ELSE line_number (or :ELSE with lookahead)"

However, the code shows multiple places where ELSE is checked:
1. After THEN line_number (lines ~1535-1560)
2. During statement parsing loop (lines ~1570-1595)
3. After GOTO line_number (lines ~1610-1625)

The complexity suggests the comment's simple list may not capture all the edge cases the code handles, particularly around when colons are required vs optional before ELSE.

---

#### code_vs_comment

**Description:** Comment claims CALL statement primarily uses numeric address form in MBASIC 5.21, but code fully implements extended syntax with arguments

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_call() states:
"Note: MBASIC 5.21 primarily uses the simple numeric address form, but this
parser fully supports both forms for broader compatibility."

However, the implementation fully parses both forms:
- Simple numeric address: CALL 16384
- Extended with arguments: CALL ROUTINE(X,Y)

The code handles both equally, converting FunctionCallNode and VariableNode with subscripts into CallStatementNode with arguments. The comment suggests the extended form is for compatibility, but the code treats both as first-class features.

---

#### code_vs_comment

**Description:** PC class docstring describes stmt_offset as '0-based index' but also calls it 'offset' which is confusing terminology

**Affected files:**
- `src/pc.py`

**Details:**
Docstring says: 'The stmt_offset is a 0-based index into the statements list for a line...Note: stmt_offset is the list index (position in the statements array). The term "offset" is used for historical reasons but it\'s simply the array index.'

This acknowledges the terminology is misleading but doesn't fix it. Throughout the codebase it's consistently used as an index (0, 1, 2...) not an offset in the traditional sense.

---

#### code_vs_comment

**Description:** apply_keyword_case_policy implementation doesn't match its docstring regarding first_wins normalization

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring says: 'Note: The first_wins policy normalizes keywords to lowercase for lookup purposes. Other policies transform the keyword directly without normalization.'

But the code shows ALL policies receive the keyword as-is and transform it. The 'first_wins' policy does normalize to lowercase for lookup (keyword_lower = keyword.lower()) but this is an implementation detail, not a caller requirement. The docstring implies callers need to know about this normalization.

---

#### code_vs_comment

**Description:** emit_keyword caller responsibility comment contradicts apply_keyword_case_policy docstring about input case requirements

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword says: 'Caller responsibility: The caller must pass the keyword in lowercase (e.g., "print", "for").'

apply_keyword_case_policy says: 'Args:
    keyword: The keyword to transform (may be any case)'

If emit_keyword requires lowercase input, but it calls apply_keyword_case_policy which accepts any case, there's a mismatch in the contract.

---

#### code_vs_comment_conflict

**Description:** Comment about MBASIC array sizing convention may not match actual implementation location

**Affected files:**
- `src/resource_limits.py`

**Details:**
In check_array_allocation() method, line ~165:

Comment states: '# Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21'
Followed by: '# This implements the MBASIC array sizing convention (called by execute_dim() in interpreter.py)'

The code then does: 'total_elements *= (dim_size + 1)  # +1 for 0-based indexing (0 to N)'

The comment claims 'This implements the MBASIC array sizing convention' but the actual implementation is just calculating the size for limit checking. The actual array creation/initialization would be in interpreter.py's execute_dim(). The comment may be misleading about where the convention is 'implemented' vs where it's 'accounted for in size calculation'.

---

#### code_vs_comment

**Description:** Comment claims 'original_case' stores the original case, but code actually stores the canonical/resolved case

**Affected files:**
- `src/runtime.py`

**Details:**
Line 48-51 comment: "'original_case' stores the canonical case for display (determined by case_conflict policy).
Despite the name 'original_case', this field stores the resolved canonical case variant,
not necessarily the first case seen."

Line 265: "self._variables[full_name]['original_case'] = canonical_case  # Store canonical case for display (see _check_case_conflict)"

Line 283: "# Always update original_case to canonical (for prefer_upper/prefer_lower/prefer_mixed policies)
# Note: 'original_case' field name is misleading - it stores the canonical case, not the original"

Line 368: "self._variables[full_name]['original_case'] = canonical_case  # Store canonical case for display (see _check_case_conflict)"

Line 373: "# Always update original_case to canonical (for prefer_upper/prefer_lower/prefer_mixed policies)
# Note: 'original_case' field name is misleading - it stores the canonical case, not the original"

The field name 'original_case' is misleading throughout the codebase. It should be renamed to 'canonical_case' or 'display_case' to match its actual purpose.

---

#### code_vs_comment

**Description:** SettingsManager class has unused _get_global_settings_path and _get_project_settings_path methods

**Affected files:**
- `src/settings.py`

**Details:**
The SettingsManager class defines:
- _get_global_settings_path()
- _get_project_settings_path()

But these methods are never called in the class. The __init__ method comment says:
"# Paths (for backward compatibility, may not be used with Redis backend)
self.global_settings_path = getattr(backend, 'global_settings_path', None)
self.project_settings_path = getattr(backend, 'project_settings_path', None)"

The paths are retrieved from the backend, not from these methods. These methods appear to be dead code left over from refactoring.

---

#### code_vs_comment

**Description:** Token dataclass comment claims fields are mutually exclusive but implementation doesn't enforce it

**Affected files:**
- `src/tokens.py`

**Details:**
Token dataclass docstring states:
"Note: These fields serve different purposes and should be mutually exclusive
(identifiers use original_case, keywords use original_case_keyword):
- original_case: For identifiers (user variables) - preserves what user typed
- original_case_keyword: For keywords - stores policy-determined display case

The dataclass doesn't enforce exclusivity (both can be set) for implementation flexibility,
but the lexer/parser maintain this convention: only one field is populated per token."

This is a design decision documented in comments, but the comment acknowledges the code doesn't enforce what it describes. The comment says 'should be mutually exclusive' but then says 'both can be set'. This is internally contradictory documentation.

---

#### code_vs_comment

**Description:** get() method docstring describes precedence including file settings but implementation shows file_settings is always empty in normal usage

**Affected files:**
- `src/settings.py`

**Details:**
get() method docstring:
"Precedence: file > project > global > definition default > provided default

Note: File-level settings infrastructure is fully implemented and functional.
The file_settings dict can be set programmatically and is checked first in precedence.
However, no UI or command exists to manage per-file settings. In normal usage,
file_settings is empty and precedence falls through to project/global settings."

The docstring correctly describes the precedence order and notes file_settings is empty in normal usage. However, it's misleading to list 'file' first in the precedence when it's never populated. The precedence in practice is: project > global > definition default > provided default.

---

#### JSON configuration inconsistency

**Description:** The 'continue' command has different key bindings between CLI and curses: CLI uses 'CONT' command while curses uses 'Ctrl+C'. Additionally, curses uses 'Ctrl+C' for continue but 'Ctrl+X' for stop, which is inconsistent with typical terminal conventions where Ctrl+C stops execution.

**Affected files:**
- `src/ui/cli_keybindings.json`
- `src/ui/curses_keybindings.json`

**Details:**
cli_keybindings.json:
"continue": {"keys": ["CONT"], "primary": "CONT", "description": "Continue execution"}
"stop": {"keys": ["Ctrl+C"], "primary": "Ctrl+C", "description": "Stop program execution"}

curses_keybindings.json:
"continue": {"keys": ["Ctrl+C"], "primary": "Ctrl+C", "description": "Continue execution"}
"stop": {"keys": ["Ctrl+X"], "primary": "Ctrl+X", "description": "Stop program execution"}

This creates a confusing user experience where Ctrl+C has opposite meanings in different UIs.

---

#### Code vs Comment conflict

**Description:** The _create_body() method's footer comment claims 'All shortcuts use constants from keybindings module to ensure footer display matches actual key handling in keypress() method', but the footer only shows 4 shortcuts while keypress() handles 4 different actions. The comment implies complete coverage but implementation may be incomplete.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment in _create_body():
"# Create footer with keyboard shortcuts (instead of button widgets)
# Note: All shortcuts use constants from keybindings module to ensure
# footer display matches actual key handling in keypress() method"

Footer shows: ENTER_KEY, ESC_KEY, SETTINGS_KEY, SETTINGS_APPLY_KEY, SETTINGS_RESET_KEY
keypress() handles: ESC_KEY, SETTINGS_KEY, ENTER_KEY, SETTINGS_APPLY_KEY, SETTINGS_RESET_KEY

The comment's claim of ensuring display matches handling is accurate, but the phrasing 'All shortcuts' could be misleading if there are other possible actions not shown.

---

#### Code vs Documentation inconsistency

**Description:** The base.py UIBackend class defines execute_immediate() as an optional method with a docstring showing examples, but cli.py's CLIBackend implements it by delegating to interactive.execute_statement() without any validation or error handling, and there's no documentation about whether execute_statement() actually exists or what it does.

**Affected files:**
- `src/ui/cli.py`
- `src/ui/base.py`

**Details:**
base.py defines:
"def execute_immediate(self, statement: str) -> None:
    '''Execute immediate mode statement.
    
    Args:
        statement: BASIC statement to execute immediately
    
    Examples:
        PRINT 2+2
        A=5: PRINT A
        FOR I=1 TO 10: PRINT I: NEXT I
    '''
    pass"

cli.py implements:
"def execute_immediate(self, statement: str) -> None:
    '''Execute immediate mode statement.'''
    self.interactive.execute_statement(statement)"

No documentation confirms execute_statement() exists on InteractiveMode or what it does.

---

#### code_vs_comment

**Description:** Comment claims line numbers use 1-5 digits, but code supports variable width up to 99999

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring says:
"Display format: 'S<linenum> CODE' where:
- Field 2 (variable width): Line number (1-5 digits, no padding)"

But code in _on_auto_number_renumber_response and elsewhere uses 99999 as max:
"if next_num >= 99999 or attempts > 10:"

This is 5 digits max, but the comment '1-5 digits' suggests it could be 1, 2, 3, 4, OR 5 digits, which is correct. However, the implementation actually enforces a hard limit of 99999 (exactly 5 digits max), not a variable 1-5 digit range.

---

#### code_vs_comment

**Description:** Comment claims empty lines are valid but code has special handling that contradicts this

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_syntax_errors method:
"# Clear error status for empty lines, but preserve breakpoints
# Note: line_number > 0 check handles edge case of line 0 (if present)
# Consistent with _check_line_syntax which treats all empty lines as valid"

But in _check_line_syntax:
"if not code_text or not code_text.strip():
    # Empty lines are valid
    return (True, None)"

The inconsistency: _update_syntax_errors has 'line_number > 0' check, suggesting line 0 is treated differently, but _check_line_syntax treats ALL empty lines as valid regardless of line number. The comment claims consistency but the implementations differ in their handling of line 0.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of line number changes between keypress and _on_enter_idle

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress method, line number changes trigger immediate sorting:
"if current_line_num != self._saved_line_num:
    # Line number changed - sort lines
    self._sort_and_position_line(lines, line_num, target_column=col_in_line)"

But in _on_enter_idle, sorting is deferred and only happens if cursor is in line number area:
"if line_num_parsed is not None and 1 <= col_in_line < code_start:
    self._sort_and_position_line(lines, line_num, target_column=col_in_line)"

This creates two different code paths for sorting with different conditions, which could lead to inconsistent behavior.

---

#### code_vs_comment

**Description:** Comment claims editor_lines stores execution state while editor.lines stores editing state, but code shows they are synchronized and serve overlapping purposes

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~130 says:
# Note: self.editor_lines stores execution state (lines loaded from file for RUN)
# self.editor.lines (in ProgramEditorWidget) stores the actual editing state
# These serve different purposes and are synchronized as needed

However, _save_editor_to_program() (line ~230) syncs editor.lines -> program, and _refresh_editor() (line ~290) syncs program -> editor.lines. The _sync_program_to_editor() method would sync program -> editor_lines. This suggests they are redundant storage rather than serving truly different purposes.

---

#### code_vs_comment

**Description:** Comment about IO Handler lifecycle claims io_handler is created once and reused, but immediate_io is recreated in start()

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~165 says:
# IO Handler Lifecycle:
# 1. self.io_handler (CapturingIOHandler) - Used for RUN program execution
#    Created ONCE here, reused throughout session (NOT recreated in start())
# 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands
#    Created here temporarily, then RECREATED in start() with fresh instance each time

However, at line ~200, the code creates immediate_io temporarily in __init__, then the comment says it will be recreated in start(). This is confusing because it suggests the temporary creation in __init__ serves no purpose except to initialize the attribute.

---

#### code_vs_comment

**Description:** Comment in _on_insert_line_renumber_response says context is lost, but this could be preserved

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
At line ~1180, comment says:
# Note: We can't continue the insert here because we've lost the context
# (lines, line_index, insert_num variables). User will need to retry insert.

This suggests a design limitation, but the context could be preserved by storing it as instance variables or in a closure. The comment makes it sound like a technical impossibility when it's actually a design choice.

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

This comment is accurate and matches the code implementation where breakpoints are re-applied after reset_for_run(). However, the phrasing could be clearer that breakpoints ARE cleared from the interpreter during reset but preserved in editor state.

---

#### code_vs_comment

**Description:** Comment about PC setting timing may be misleading about when start() resets PC

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1200 states:
"# If start_line is specified (e.g., RUN 100), set PC to that line
# This must happen AFTER interpreter.start() because start() calls setup()
# which resets PC to the first line in the program. By setting PC here,
# we override that default and begin execution at the requested line."

This comment accurately describes the behavior but could be clearer that the PC override happens after the interpreter is fully initialized, not just after start() is called.

---

#### code_vs_comment

**Description:** Comment claims ESC sets stopped=True similar to BASIC STOP, but code behavior differs from STOP semantics

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _get_input_for_interpreter method:
Comment says: "# Note: This sets stopped=True similar to a BASIC STOP statement, but the semantics
# differ - STOP is a deliberate program action, while ESC is user cancellation"

However, the code sets self.runtime.stopped = True and self.running = False, which prevents CONT from working (CONT checks self.runtime.stopped). But the comment acknowledges semantic differences without clarifying if CONT should work after ESC cancellation.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says immediate executor already called interpreter.start(), but this may not always be true

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method:
"# NOTE: Don't call interpreter.start() here - the immediate executor already
# called it if needed (e.g., 'RUN 120' called interpreter.start(start_line=120)
# to set PC to line 120). Calling it again would reset PC to the beginning."

This assumes the immediate executor always calls start() when needed, but the code then checks if InterpreterState exists and creates it if not. This suggests there are cases where start() wasn't called. The comment may be outdated or incomplete.

---

#### internal_inconsistency

**Description:** Inconsistent handling of program source of truth between methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
cmd_delete and cmd_renum comments say "Updates self.program immediately (source of truth), then syncs to runtime" and call _sync_program_to_runtime().

However, _execute_immediate updates self.program from editor_lines, then syncs to runtime.

But _list_program reads from self.editor_lines directly, not self.program.

This suggests confusion about whether self.program or self.editor_lines is the source of truth for the current program state.

---

#### code_vs_comment_conflict

**Description:** Comments in both files claim they serve different purposes, but they load identical JSON files for overlapping use cases

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/keybinding_loader.py`

**Details:**
help_macros.py comment at line ~35:
"Note: This is generic keybinding loading for macro expansion in help content (e.g., {{kbd:run}} -> '^R'). This is different from help_widget.py which uses hardcoded keys for its own navigation. HelpMacros needs full keybindings to expand {{kbd:action}} macros in documentation, not for actual event handling."

keybinding_loader.py comment at line ~30:
"Note: This loads keybindings for UI event handling (binding keys to actions). This is different from help_macros.py which loads the same JSON for macro expansion in help content (e.g., {{kbd:run}} -> '^R'). These serve different purposes: KeybindingLoader for runtime event handling, HelpMacros for documentation generation."

Both load from: Path(__file__).parent / f"{self.ui_name}_keybindings.json"

The distinction is valid but the comments overemphasize the difference when both are reading the same data structure for related purposes (one for display, one for binding).

---

#### documentation_inconsistency

**Description:** Docstring describes {{kbd:help}} format but implementation uses different search logic

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Module docstring states:
"{{kbd:help}} → looks up 'help' action in keybindings (searches all sections) and returns the primary keybinding for that action"

But _expand_kbd() implementation supports additional format:
"Formats:
- 'action' - searches current UI (e.g., 'help', 'save', 'run')
- 'action:ui' - searches specific UI (e.g., 'save:curses', 'run:tk')"

The module docstring doesn't mention the 'action:ui' format capability.

---

#### code_vs_comment_conflict

**Description:** Comment claims tier detection uses startswith('ui/') but code shows more complex tier mapping

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~145:
"Note: UI tier (e.g., 'ui/curses', 'ui/tk') is detected via startswith('ui/') check below and gets '📘 UI' label. Other unrecognized tiers get '📙 Other'."

But the code shows a tier_labels dict with explicit mappings:
tier_labels = {
    'language': '📕 Language',
    'mbasic': '📗 MBASIC',
}

Then uses:
if tier_name.startswith('ui/'):
    tier_label = '📘 UI'
else:
    tier_label = tier_labels.get(tier_name, '📙 Other')

The comment is incomplete - it doesn't mention the 'language' and 'mbasic' tier mappings.

---

#### code_vs_comment_conflict

**Description:** Comment describes link format but doesn't match actual regex pattern

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment in _create_text_markup_with_links() at line ~230:
"Links are marked with [text] in the rendered output. This method finds ALL [text] patterns for display/navigation, but uses the renderer's links for target mapping when following links."

But the actual regex pattern is:
link_pattern = r'\[([^\]]+)\](?:\([^)]+\))?'

This matches both `[text]` AND `[text](url)` formats, not just `[text]`. The comment is incomplete.

---

#### Code vs Comment conflict

**Description:** Comment claims QUIT_KEY has no keyboard shortcut, but QUIT_ALT_KEY (Ctrl+C) is documented as an alternative quit method. The comment is misleading about quit functionality.

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 138-145:
# Quit - No dedicated keyboard shortcut (most Ctrl keys intercepted by terminal or already assigned)
# Primary method: Use menu (Ctrl+U -> File -> Quit)
# Alternative: Ctrl+C (interrupt signal) will also quit - see QUIT_ALT_KEY below
QUIT_KEY = None  # No keyboard shortcut

# Alternative quit via interrupt signal (Ctrl+C)
# Note: This is not a standard keybinding but a signal handler, hence "alternative"
_quit_alt_from_json = _get_key('editor', 'quit')
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

The comment says there's no keyboard shortcut, but then immediately defines QUIT_ALT_KEY as Ctrl+C. This is contradictory - either Ctrl+C is a quit shortcut or it isn't.

---

#### code_vs_comment

**Description:** Comment states immediate_history and immediate_status are 'always None' but provides incorrect reasoning

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 293-297 comment states:
# Set immediate_history and immediate_status to None
# These attributes are not currently used but are set to None for defensive programming
# in case future code tries to access them (will get None instead of AttributeError)

However, lines 141-143 in __init__ already set these to None with comment:
# Immediate mode widgets and executor
# Note: immediate_history and immediate_status are always None in Tk UI (see lines 293-297)

The comment at lines 141-143 references lines 293-297 as explanation, but lines 293-297 don't explain WHY they're always None in Tk UI - they just say it's for defensive programming. The real reason appears to be architectural: Tk UI uses immediate_entry (Entry widget) instead of history/status widgets.

---

#### code_vs_comment_conflict

**Description:** Comment claims formatting may occur elsewhere, but code explicitly avoids formatting to preserve MBASIC compatibility

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _refresh_editor method around line 1150:
Comment says: "(Note: 'formatting may occur elsewhere' refers to the Variables and Stack windows, which DO format data for display - not the editor/program text itself)"

This parenthetical note appears to be defending against a concern that doesn't exist - the code already preserves text exactly as stored. The comment creates confusion by mentioning formatting that occurs in other windows, which is irrelevant to this method's purpose.

---

#### code_vs_comment_conflict

**Description:** Comment about when _validate_editor_syntax is called doesn't match actual call sites

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1230:
Comment says: "Note: This method is called:
- With 100ms delay after cursor movement/clicks (to avoid excessive validation during rapid editing)
- Immediately when focus leaves editor (to ensure validation before switching windows)"

However, looking at actual call sites:
- _on_cursor_move: calls with 100ms delay (matches comment)
- _on_mouse_click: calls with 100ms delay (matches comment)
- _on_focus_out: calls immediately (matches comment)
- _on_enter_key: NOT mentioned in comment but calls immediately at line 1380

The comment is incomplete - it doesn't mention the call from _on_enter_key which validates syntax after Enter key press.

---

#### code_vs_comment_conflict

**Description:** Comment about when _remove_blank_lines is called contradicts potential future usage

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines method around line 1330:
Comment says: "Currently called only from _on_enter_key (after each Enter key press), not after pasting or other modifications. This provides cleanup when the user presses Enter to move to a new line."

The word 'Currently' suggests this may change in the future, but the method implementation doesn't have any guards or parameters to handle being called from different contexts. If it were called after pasting, the cursor position restoration logic might not work correctly. Either: (1) the comment should be more definitive about the single call site, or (2) the method should be made more robust for multiple call contexts.

---

#### code_vs_comment

**Description:** Comment claims blank lines are removed after key press, but code only schedules removal without guaranteeing execution

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1050: '# Schedule blank line removal after key is processed'
Code: 'self.root.after(10, self._remove_blank_lines)'
The comment implies blank lines WILL be removed, but after() only schedules it - if user types rapidly or other events occur, the removal may be delayed or skipped. The comment should clarify this is scheduled/asynchronous.

---

#### code_vs_comment

**Description:** Comment about cursor movement clearing highlight conflicts with actual trigger condition

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1042: 'Clear yellow statement highlight on any keypress when paused at breakpoint - Clears on ANY key (even arrows/function keys)'
Code at line ~1044: 'if self.paused_at_breakpoint: self._clear_statement_highlight()'
The comment emphasizes clearing on 'ANY key (even arrows/function keys)' but the actual condition only checks paused_at_breakpoint flag, not whether the key is an arrow or function key. The emphasis on 'ANY key' seems to suggest this was a design decision, but the code doesn't distinguish between key types.

---

#### code_vs_comment

**Description:** Comment about line change detection logic doesn't match actual implementation conditions

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1120: 'Determine if program needs to be re-sorted: 1. Line number changed on existing line (both old and new are not None), OR 2. Line number was removed (old was not None, new is None and line has content)'
Followed by: 'Don't trigger sort when: - old_line_num is None: First time tracking this line (cursor just moved here, no editing yet)'
However, the code at line ~1127 checks 'if old_line_num != new_line_num:' BEFORE checking if old_line_num is None. This means the condition structure doesn't exactly match the comment's description. The logic is correct but the comment could be clearer about the order of checks.

---

#### code_vs_comment

**Description:** Comment about paste behavior describes two cases but implementation treats them differently than described

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~920: 'Multi-line paste or single-line paste into blank line - use auto-numbering logic. Both cases use the same logic (split by \n, process each line): 1. Multi-line paste: sanitized_text contains \n → multiple lines to process 2. Single-line paste into blank line: current_line_text empty → one line to process'
However, the code at line ~905 already handled single-line paste into existing line with a return 'break', so case 2 (single-line paste into blank line) is actually a subset of the multi-line logic, not a separate case. The comment makes it sound like both cases are equivalent, but they're handled by different code paths.

---

#### code_vs_comment

**Description:** Comment claims immediate mode execution doesn't echo commands, but this contradicts typical BASIC behavior documentation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method around line 1090:
Comment states: "Execute without echoing (GUI design choice that deviates from typical BASIC behavior: command is visible in entry field, and 'Ok' prompt is unnecessary in GUI context - only results are shown. Traditional BASIC echoes to output.)"

This comment acknowledges a deviation from documented BASIC behavior but doesn't clarify if this is intentional or if documentation should be updated to reflect GUI-specific behavior.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about INPUT vs LINE INPUT behavior strategy

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler class docstring states:
"Input strategy:
- INPUT statement: Uses inline input field when backend available,
  otherwise uses modal dialog (not a preference, but availability-based)
- LINE INPUT statement: Always uses modal dialog for consistent UX"

But the input() method docstring states:
"Prefers inline input field below output pane when backend is available,
but falls back to modal dialog if backend is not available."

While the input_line() method docstring states:
"Unlike input() which prefers inline input field, this ALWAYS uses
a modal dialog regardless of backend availability."

The word 'prefers' vs 'uses when available' creates ambiguity about whether this is a preference or a hard requirement based on availability.

---

#### code_vs_comment

**Description:** Comment claims has_work() is only called in one location, but this is a maintenance assertion that could become outdated

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method around line 1125:
"# Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command).
# This is the only location in tk_ui.py that calls has_work()."

This type of comment creates a maintenance burden - if has_work() is called elsewhere in the future, this comment becomes incorrect. Such assertions should be verified by tooling, not comments.

---

#### code_vs_comment

**Description:** Comment about race condition prevention uses redundant checks that may indicate unclear state management

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _update_immediate_status() method around line 1020:
"# Check if safe to execute - use both can_execute_immediate() AND self.running flag
# The 'not self.running' check prevents immediate mode execution when a program is running,
# even if the tick hasn't completed yet. This prevents race conditions where immediate
# mode could execute while the program is still running but between tick cycles.
can_exec_immediate = self.immediate_executor.can_execute_immediate()
can_execute = can_exec_immediate and not self.running"

The comment suggests that can_execute_immediate() alone is insufficient and requires an additional self.running check. This indicates either:
1. can_execute_immediate() is not correctly checking all necessary conditions
2. There's unclear ownership of execution state between components
3. The state management design has race conditions that require defensive checks

---

#### code_vs_comment

**Description:** Docstring claims error takes priority and breakpoint becomes visible after fixing error, but _on_status_click() shows both error and breakpoint messages, suggesting they can coexist visually

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring says:
"Status priority (when both error and breakpoint):
- ? takes priority (error shown)
- After fixing error, ● becomes visible (automatically handled by set_error() method
  which checks has_breakpoint flag when clearing errors)"

But _on_status_click() docstring says:
"Displays informational messages about line status:
- For error markers (?): Shows error message in a message box
- For breakpoint markers (●): Shows confirmation message that breakpoint is set"

The code in _on_status_click() checks error_msg first, then checks has_breakpoint in else clause, confirming only one symbol shows at a time. However, the phrasing "automatically handled" is misleading - it's just standard if/elif logic in set_error(), not special automatic handling.

---

#### code_vs_comment

**Description:** _delete_line() docstring has confusing dual numbering explanation that may mislead developers

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring says:
"Args:
    line_num: Tkinter text widget line number (1-based sequential index),
             not BASIC line number (e.g., 10, 20, 30).
             Note: This class uses dual numbering - editor line numbers for
             text widget operations, BASIC line numbers for line_metadata lookups."

This is accurate but the note about 'dual numbering' appears in _delete_line() which only uses editor line numbers. The note would be more appropriate in the class docstring or in methods that convert between the two (like _redraw() or _on_status_click()).

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

However, the code only sets relative_indent=1 as initial default before checking source_text. If source_text exists but doesn't match the pattern, relative_indent remains 1 (the default), but the comment implies this is a deliberate fallback case. The code doesn't explicitly handle the 'doesn't match pattern' case separately from the 'no source_text' case.

---

#### code_vs_comment

**Description:** Comment in update_line_references() describes pattern behavior that may not match actual regex behavior for edge cases

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Note: Pattern uses .+? (non-greedy) to match expression in ON statements,
which correctly handles edge cases like 'ON FLAG GOTO' (variable starting with 'G'),
'ON X+Y GOTO' (expressions), and 'ON A$ GOTO' (string variables)"

The pattern is: r'\b(GOTO|GOSUB|THEN|ELSE|ON\s+.+?\s+GOTO|ON\s+.+?\s+GOSUB)\s+(\d+)'

The .+? pattern will match any characters non-greedily, but the comment claims it 'correctly handles' these cases without explaining what 'correctly' means. For 'ON FLAG GOTO 10', the pattern would match 'ON FLAG GOTO' as the keyword group, which is correct. However, for nested expressions like 'ON X GOTO 10 : ON Y GOTO 20', the non-greedy match might not behave as expected if there are multiple GOTO keywords on the same line.

---

#### code_vs_documentation

**Description:** serialize_expression() docstring describes ERR/ERL special handling but doesn't explain why this is necessary or what the alternative would be

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring states: "Note:
ERR and ERL are special system variables that are serialized without
parentheses (e.g., 'ERR' not 'ERR()') when they appear as FunctionCallNode
with no arguments, matching MBASIC 5.21 syntax."

This note explains WHAT the code does but not WHY. The implementation shows:
if expr.name in ('ERR', 'ERL') and len(expr.arguments) == 0:
    return expr.name

The docstring should explain:
1. Why ERR/ERL are represented as FunctionCallNode instead of VariableNode in the AST
2. What would happen if they were serialized with parentheses
3. Whether this is a parser quirk or a BASIC language requirement

Without this context, maintainers might not understand why this special case exists.

---

#### Code vs Documentation inconsistency

**Description:** Comment in cmd_run() claims 'Runtime accesses program.line_asts directly, no need for program_ast variable' but this is misleading - the code does pass program.line_asts to Runtime constructor, so there IS a need to access it, just not to store it in a separate variable first.

**Affected files:**
- `src/ui/visual.py`

**Details:**
Comment says: '(Runtime accesses program.line_asts directly, no need for program_ast variable)'
Code shows: 'self.runtime = Runtime(self.program.line_asts, self.program.lines)'
The comment suggests Runtime accesses it directly without passing, but the code explicitly passes it as a constructor argument.

---

#### Code vs Comment conflict

**Description:** The value property getter has a comment 'Sometimes event args are dict - return empty string' suggesting defensive programming, but there's no explanation of why event args would be a dict when the setter and internal handler treat it as a string.

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Property getter:
        if isinstance(self._value, dict):
            # Sometimes event args are dict - return empty string
            return ''
        return self._value or ''

This suggests a known issue where _value can become a dict, but the setter and change handler both treat it as a string. This inconsistency is not explained.

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

#### code_vs_comment

**Description:** VariablesDialog sort defaults claim to match Tk UI but may differ

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~127:
# Sort state (matches Tk UI defaults: see sort_mode and sort_reverse in src/ui/tk_ui.py)
self.sort_mode = 'accessed'  # Current sort mode
self.sort_reverse = True  # Sort direction

This references tk_ui.py for verification, but without seeing that file, cannot confirm if defaults actually match. The comment suggests they should be identical.

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

#### code_vs_comment

**Description:** Comment in _menu_run claims RUN does NOT clear output, but the comment references 'line ~1845 below' which is confusing given the actual line numbers in the code.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment in _menu_run (around line 1820) states:
"Note: This implementation does NOT clear output (see comment at line ~1845 below)."

The line reference '~1845 below' is vague and may be outdated. The actual comment about not clearing output appears to be at a different location.

---

#### code_vs_comment

**Description:** Comment in _handle_step_result claims to use 'microprocessor model' but the actual implementation checks multiple state properties in a specific order that may not align with a pure microprocessor model.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~2150 states:
"# Use microprocessor model: check error_info, input_prompt, and runtime.halted"

However, the implementation checks state.input_prompt first, then state.error_info, then runtime.halted. A true microprocessor model would typically check error conditions first. This may be intentional design, but the comment could be misleading about the actual priority order.

---

#### code_vs_comment

**Description:** Comment claims PC is conditionally preserved based on exec_timer state, but code logic doesn't match the described behavior

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _sync_program_to_runtime() method:

Comment says:
"PC handling (conditional preservation):
- If exec_timer is active (execution in progress): Preserves PC and halted state,
  allowing program to resume from current position after rebuild.
- Otherwise (no active execution): Resets PC to halted state, preventing
  unexpected execution when LIST/edit commands modify the program."

But the code checks:
if self.exec_timer and self.exec_timer.active:
    # Preserve PC
else:
    # Reset to halted

The comment describes this as preventing "unexpected execution" but the actual purpose appears to be about state consistency during rebuilds. The comment's explanation about "preventing unexpected execution when LIST/edit commands run" is misleading because LIST/edit commands don't trigger execution - they just rebuild the statement table.

---

#### code_vs_comment

**Description:** Comment about paste detection threshold is arbitrary and may not match actual behavior

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _on_editor_change() method:

Comment says:
"Detect paste: large content change (threshold: >5 chars)
This heuristic helps clear auto-number prompts before paste content merges with them.
The 5-char threshold is arbitrary - balances detecting small pastes while avoiding
false positives from rapid typing (e.g., typing 'PRINT' quickly = 5 chars but not a paste)."

The comment admits the threshold is arbitrary and gives an example where typing 'PRINT' (5 chars) would NOT trigger paste detection, but the code uses >5 (greater than 5), meaning 'PRINT' (exactly 5 chars) wouldn't trigger it anyway. The comment's example doesn't match the actual threshold logic.

---

#### code_vs_comment

**Description:** Comment about architecture decision contradicts actual code behavior

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _execute_immediate() method:

Comment says:
"Architecture: We do NOT auto-sync editor from AST after immediate commands.
This preserves one-way data flow (editor → AST → execution) and prevents
losing user's formatting/comments. Commands that modify code (like RENUM)
update the editor text directly."

However, the code calls:
self._save_editor_to_program()
self._sync_program_to_runtime()

This IS syncing from editor to program/runtime, which contradicts the claim about "one-way data flow". The comment seems to be describing a different sync direction (AST → editor) than what the code does (editor → AST).

---

#### code_vs_comment

**Description:** Comment claims 'errors are caught and logged, won't crash the UI' but the timer callback save_state_periodic() could still raise exceptions that propagate

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~470: '# Save state periodically (errors are caught and logged, won't crash the UI)'

But the timer is set up as:
ui.timer(5.0, save_state_periodic)

The save_state_periodic function has try/except, but if ui.timer itself or the serialization in backend.serialize_state() raises an exception outside the try block, it could still crash. The comment overstates the error handling robustness.

---

#### documentation_inconsistency

**Description:** Compiler documentation describes 27 optimizations as 'implemented' but index.md says code generation is 'In Progress'

**Affected files:**
- `docs/help/common/compiler/optimizations.md`
- `docs/help/common/compiler/index.md`

**Details:**
optimizations.md states: '27 optimizations implemented in the semantic analysis phase. All optimizations preserve the original program behavior while improving performance or reducing resource usage.'

But index.md states: 'Code Generation - Status: In Progress - Documentation for the code generation phase will be added as the compiler backend is developed.'

This creates confusion about whether the compiler is functional or still under development. The optimizations are described as 'implemented' but code generation is 'in progress', suggesting the optimizations exist but can't generate actual code yet.

---

#### documentation_inconsistency

**Description:** index.md references shortcuts.md and examples.md which are not provided in the documentation set

**Affected files:**
- `docs/help/common/index.md`

**Details:**
In index.md under 'Topics' section:
`[Keyboard Shortcuts](shortcuts.md)`
`[Examples](examples.md)`

These files are not included in the provided documentation, creating broken links.

---

#### documentation_inconsistency

**Description:** Contradictory information about Control-C behavior

**Affected files:**
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/input_dollar.md`

**Details:**
INKEY$.md states: 'Note: Control-C behavior varied in original implementations. In MBASIC 5.21 interpreter, Control-C would terminate the program. In the BASIC Compiler, Control-C was passed through. This implementation follows compiler behavior and passes Control-C through (CHR$(3)) for program detection and handling.'

INPUT$.md states: 'Note: In MBASIC 5.21 interpreter, Control-C would interrupt INPUT$ and terminate the wait. This implementation passes Control-C through (CHR$(3)) for program detection and handling, matching compiler behavior.'

Both claim to match compiler behavior but describe different original MBASIC 5.21 behaviors (terminate program vs interrupt/terminate wait).

---

#### documentation_inconsistency

**Description:** Example code shows conflicting behavior for type precedence

**Affected files:**
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
Line 60 shows: NAME1$ = "TEST"  ' String (starts with N, but $ suffix overrides DEFINT)
Line 70 shows: AMOUNT = "100"   ' String (starts with A, DEFSTR applies)

The comment on line 60 correctly states that $ suffix overrides DEFINT N-Z, making NAME1$ a string.
However, line 70 assigns a string literal "100" to AMOUNT, which would be a string regardless of DEFSTR A. The example should show AMOUNT without quotes to demonstrate DEFSTR behavior, or the comment should clarify that the literal is a string, not the variable type.

---

#### documentation_inconsistency

**Description:** Contradictory information about CONT behavior after END

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/error.md`

**Details:**
end.md states: "Can be continued with CONT (execution resumes at next statement after END)"

However, this contradicts typical BASIC behavior where END closes files and terminates the program. If CONT can resume after END, it's unclear what state the program is in (are files still closed? does execution truly resume at the next statement?). This needs clarification or correction, as END is typically a terminal statement.

---

#### documentation_inconsistency

**Description:** Different terminology for string modification operations

**Affected files:**
- `docs/help/common/language/statements/lset.md`
- `docs/help/common/language/statements/mid-assignment.md`

**Details:**
lset.md describes: "To left-justify a string in a field for random file I/O operations" and explains it "assigns the string expression to the string variable, left-justified in the field."

mid-assignment.md describes: "To replace characters within a string variable without creating a new string" and explains "The MID$ assignment statement modifies a portion of an existing string variable by replacing characters"

Both modify strings in place, but LSET is described as "assigning" while MID$ is described as "replacing" or "modifying". The conceptual difference (LSET for file fields vs MID$ for general strings) is clear, but the terminology inconsistency could confuse users about whether these are fundamentally different operations.

---

#### documentation_inconsistency

**Description:** Settings documentation references non-existent HELPSETTING command

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
settings.md lists HELPSETTING as an available command under 'CLI (Command Line)' section: 'HELPSETTING editor.auto_number_step      ' Get help for a specific setting'. However, there is no helpsetting.md documentation file in the statements directory, and it's unclear if this command is actually implemented.

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI file persistence and settings storage

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md states:
- Files stored in server-side memory (sandboxed filesystem per session)
- Files persist during browser session but are lost on page refresh
- Note: Settings (not files) can persist via Redis if configured - see `[Web UI Settings](../ui/web/settings.md)`

But extensions.md states:
- **Session-based storage** - Files persist during browser session only (lost on page refresh)

The compatibility.md mentions Redis for settings persistence, but extensions.md makes no mention of any persistence mechanism. This creates confusion about what actually persists.

---

#### documentation_inconsistency

**Description:** Auto-save behavior documentation differs between documents

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/extensions.md`

**Details:**
features.md states:
- Auto-save behavior varies by UI:
  - **CLI, Tk, Curses:** Save to local filesystem (persistent)
  - **Web UI:** Files stored in server-side session memory only (not persistent across page refreshes)

But extensions.md states:
- **Auto-save** - ❌ | ✅ (Tk) | Extension

This suggests only Tk has auto-save, contradicting features.md which mentions CLI and Curses also save to local filesystem.

---

#### documentation_inconsistency

**Description:** Inconsistent UI count - getting-started mentions 4 UIs but index mentions 3

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/mbasic/index.md`

**Details:**
getting-started.md states 'MBASIC supports four interfaces' and lists CLI, Curses, Tkinter, and Web UI. However, index.md under 'Key Features' only mentions 'Choice of user interfaces (CLI, Curses, Tkinter)' - omitting Web UI from the list.

---

#### documentation_inconsistency

**Description:** Renumber feature has inconsistent shortcut documentation

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
feature-reference.md states Renumber uses 'Ctrl+E', but quick-reference.md states it is 'Menu only' with no keyboard shortcut listed.

---

#### documentation_inconsistency

**Description:** Inconsistent feature count claims

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
Curses feature-reference.md claims '7 features' for File Operations but only lists 6 features (New, Open, Save, Save As, Recent Files, Auto-Save, Merge Files = 7, correct). Tk feature-reference.md claims '8 features' for File Operations and lists 8 (New, Open, Save, Save As, Recent Files, Auto-Save, Delete Lines, Merge Files). Delete Lines appears in Tk but not in Curses File Operations section.

---

#### documentation_inconsistency

**Description:** Variable window filter options inconsistency

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/variables.md`

**Details:**
quick-reference.md states filter cycles through 'All → Scalars → Arrays → Modified', but variables.md only mentions 'All', 'Scalars', 'Arrays', 'Modified' without specifying the cycle order or if they match.

---

#### documentation_inconsistency

**Description:** Clear All Breakpoints shortcut inconsistency between UIs

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
Curses feature-reference.md shows '{{kbd:save:curses}}hift+B' (likely Shift+B with typo), while Tk feature-reference.md shows '{{kbd:file_save:tk}}hift+B' (likely Shift+B with typo). Both appear to have the same typo pattern but use different kbd template variables.

---

#### documentation_inconsistency

**Description:** Cut/Copy/Paste explanation has circular reference

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
Feature-reference.md states: '{{kbd:save:curses}} - Used for Save File (cannot be used for Paste; {{kbd:save:curses}} is reserved by terminal for flow control)' - this mentions {{kbd:save:curses}} twice with conflicting purposes (Save File vs terminal flow control).

---

#### documentation_inconsistency

**Description:** Delete Lines operation inconsistency

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
quick-reference.md states 'Delete/Backspace - Delete current line' under Editing section, but feature-reference.md lists 'Delete Lines (Ctrl+D)' as a separate feature. Unclear if these are the same feature or different operations.

---

#### documentation_inconsistency

**Description:** Inconsistent information about auto-save functionality for programs

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/settings.md`

**Details:**
getting-started.md states: "Auto-save of programs to browser localStorage is planned for a future release" (appears twice)

But settings.md describes auto-save as already implemented: "Settings ARE saved to localStorage" and provides detailed documentation about localStorage storage being the default method.

The distinction between program auto-save vs settings auto-save is unclear and potentially confusing to users.

---

#### documentation_inconsistency

**Description:** Contradictory information about settings persistence in Redis mode

**Affected files:**
- `docs/help/ui/web/settings.md`

**Details:**
settings.md states about Redis storage: "Settings persist across browser tabs" and "Shared state in multi-instance deployments"

But then states: "Settings are session-based (cleared when session expires)"

This creates confusion - do settings persist or are they session-based? The document suggests both persistence and session-based clearing, which are contradictory concepts.

---

#### documentation_inconsistency

**Description:** Conflicting information about Calendar program location

**Affected files:**
- `docs/library/index.md`
- `docs/library/utilities/index.md`

**Details:**
docs/library/index.md lists 'Calendar' under Utilities featured programs: 'Featured programs: Calendar, Unit Converter, Sort, Search, Day of Week Calculator'

However, docs/library/utilities/index.md for the Calendar entry states: 'Note: A different calendar program is also available in the `[Games Library](../games/index.md#calendar)`'

This suggests there are TWO calendar programs - one in Utilities and one in Games. But the main index.md only mentions Calendar under Utilities, not Games. The Games section featured programs list is: 'Blackjack, Spacewar, Star Trek, Hangman, Roulette' - no Calendar mentioned.

---

#### documentation_inconsistency

**Description:** README.md lists CASE_HANDLING_GUIDE.md as a configuration document, but this file is not referenced or described in SETTINGS_AND_CONFIGURATION.md

**Affected files:**
- `docs/user/README.md`
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
README.md shows:
- **`[CASE_HANDLING_GUIDE.md](CASE_HANDLING_GUIDE.md)`** - Variable and keyword case handling

But SETTINGS_AND_CONFIGURATION.md only covers variables.case_conflict setting and mentions 'See docs/dev/KEYWORD_CASE_HANDLING_TODO.md for details on upcoming features' without referencing CASE_HANDLING_GUIDE.md

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation between documents

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md uses:
'({{kbd:toggle_variables}} in TK UI)'

TK_UI_QUICK_START.md uses:
'**{{kbd:run_program}}**' and '**{{kbd:file_save}}**'

Inconsistent use of bold formatting and parentheses for kbd placeholders

---

#### documentation_inconsistency

**Description:** Inconsistent boolean value notation in SET command examples

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md shows:
'SET "editor.auto_number" true'
and
'SET "editor.show_line_numbers" true'

But also states:
'- Booleans: `true` or `false` (lowercase, no quotes in commands; use true/false in JSON files)'

The phrase 'use true/false in JSON files' is confusing since it's already stated they should be lowercase without quotes in commands

---

#### documentation_inconsistency

**Description:** Conflicting information about Find/Replace availability in Web UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
The Feature Availability Matrix shows:
| **Find/Replace** | ❌ | ❌ | ✅ | ⚠️ | Tk: implemented, Web: planned |

But the Recently Added section states:
'### Recently Added (2025-10-29)
- ✅ Tk: Find/Replace functionality'

And Coming Soon section states:
'### Coming Soon
- ⏳ Find/Replace in Web UI'

The date '2025-10-29' appears to be in the future (assuming current date is before that), which is inconsistent

---

### 🟢 Low Severity

#### code_vs_comment_conflict

**Description:** Comment claims keyword_token fields are not used, but they exist in multiple statement nodes

**Affected files:**
- `src/ast_nodes.py`

**Details:**
PrintStatementNode line 237: 'keyword_token: Optional[Token] = None  # Token for PRINT keyword (legacy, not currently used)'

IfStatementNode lines 295-297:
'keyword_token: Optional[Token] = None  # Token for IF keyword
then_token: Optional[Token] = None     # Token for THEN keyword
else_token: Optional[Token] = None     # Token for ELSE keyword (if present)'

ForStatementNode lines 311-313:
'keyword_token: Optional[Token] = None  # Token for FOR keyword
to_token: Optional[Token] = None       # Token for TO keyword
step_token: Optional[Token] = None     # Token for STEP keyword (if present)'

The PrintStatementNode comment says these fields are 'legacy, not currently used' and explains they were 'intended for case-preserving keyword regeneration but are not currently used by position_serializer'. However, IfStatementNode and ForStatementNode have similar fields without the 'legacy' or 'not used' disclaimer, creating inconsistency about whether these fields are actually used.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of INPUT statement semicolon behavior

**Affected files:**
- `src/ast_nodes.py`

**Details:**
InputStatementNode docstring lines 260-271:
'Note: The suppress_question field controls "?" display:
- suppress_question=False (default): Adds "?" after prompt
  Examples: INPUT var → "? ", INPUT "Name", var → "Name? "
- suppress_question=True: No "?" added (but custom prompt string still displays if present)
  Examples: INPUT; var → "" (no prompt), INPUT "Name"; var → "Name" (prompt without "?")

Semicolon position determines suppress_question value:
- INPUT "prompt"; var → semicolon after prompt is just separator (suppress_question=False, shows "?")
- INPUT; var → semicolon immediately after INPUT (suppress_question=True, no "?")'

The explanation is confusing: it says 'INPUT "prompt"; var' has 'suppress_question=False' and 'shows "?"', but earlier it says 'INPUT "Name"; var → "Name" (prompt without "?")'. These statements contradict each other about whether INPUT "prompt"; var shows the question mark.

---

#### code_vs_comment_conflict

**Description:** CallStatementNode has unused arguments field with conflicting documentation

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode docstring lines 826-841:
'Implementation Note: The \'arguments\' field is currently unused (always empty list). It exists for potential future support of BASIC dialects that allow CALL with arguments (e.g., CALL ROUTINE(args)). Standard MBASIC 5.21 only accepts a single address expression in the \'target\' field. Code traversing the AST can safely ignore the \'arguments\' field for MBASIC 5.21 programs.'

CallStatementNode definition lines 842-845:
'target: \'ExpressionNode\'  # Memory address expression
arguments: List[\'ExpressionNode\']  # Reserved for future (parser always sets to empty list)'

The field exists but is documented as always empty and unused. This creates maintenance burden and potential confusion. The comment says 'parser always sets to empty list' but doesn't explain why the field exists at all if it's never used.

---

#### documentation_inconsistency

**Description:** ChainStatementNode delete_range type annotation inconsistency

**Affected files:**
- `src/ast_nodes.py`

**Details:**
ChainStatementNode definition line 545:
'delete_range: Optional[Tuple[int, int]] = None  # (start_line_number, end_line_number) for DELETE option - tuple of int line numbers'

The comment redundantly specifies 'tuple of int line numbers' when the type annotation 'Tuple[int, int]' already makes this clear. More importantly, the comment format '(start_line_number, end_line_number)' uses underscores while other similar comments use spaces (e.g., 'line_number' vs 'line number'), creating minor inconsistency in documentation style.

---

#### code_vs_comment_conflict

**Description:** VariableNode type_suffix documentation is verbose and potentially confusing

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode docstring lines 1027-1038:
'Type suffix handling:
- type_suffix: The actual suffix character ($, %, !, #) - always set to indicate variable type
- explicit_type_suffix: Boolean indicating the origin of type_suffix:
    * True: suffix appeared in source code (e.g., "X%" in "X% = 5")
    * False: suffix inferred from DEFINT/DEFSNG/DEFDBL/DEFSTR (e.g., "X" with DEFINT A-Z)

Example: In "DEFINT A-Z: X=5", variable X has type_suffix=\'%\' and explicit_type_suffix=False.
The suffix must be tracked for type checking but not regenerated in source code.
Both fields must always be examined together to correctly handle variable typing.'

VariableNode definition lines 1040-1044:
'name: str  # Normalized lowercase name for lookups
type_suffix: Optional[str] = None  # $, %, !, # - The actual suffix (see explicit_type_suffix for origin)
subscripts: Optional[List[\'ExpressionNode\']] = None  # For array access
original_case: Optional[str] = None  # Original case as typed by user (for display)
explicit_type_suffix: bool = False  # True if type_suffix was in original source, False if inferred from DEF'

The docstring says 'type_suffix... always set to indicate variable type' but the field definition has 'Optional[str] = None', meaning it can be None. This is contradictory.

---

#### documentation_inconsistency

**Description:** Inconsistent comment style for statement nodes with keyword tokens

**Affected files:**
- `src/ast_nodes.py`

**Details:**
PrintStatementNode line 237: 'keyword_token: Optional[Token] = None  # Token for PRINT keyword (legacy, not currently used)'

IfStatementNode lines 295-297:
'keyword_token: Optional[Token] = None  # Token for IF keyword
then_token: Optional[Token] = None     # Token for THEN keyword
else_token: Optional[Token] = None     # Token for ELSE keyword (if present)'

ForStatementNode lines 311-313:
'keyword_token: Optional[Token] = None  # Token for FOR keyword
to_token: Optional[Token] = None       # Token for TO keyword
step_token: Optional[Token] = None     # Token for STEP keyword (if present)'

PrintStatementNode includes detailed explanation about legacy status and position_serializer, while IfStatementNode and ForStatementNode have minimal comments. This inconsistency makes it unclear whether the keyword_token fields in IF and FOR statements are also legacy/unused.

---

#### code_vs_comment

**Description:** Comment says identifier_table exists but is not used for identifiers

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line ~100 in case_string_handler.py: Comment states "An identifier_table infrastructure exists (see get_identifier_table) but is not currently used for identifiers". This suggests dead code or incomplete implementation. The get_identifier_table() method exists but serves no purpose if identifiers always return original_text.

---

#### documentation_inconsistency

**Description:** Module docstring references tokens.py for MBASIC 5.21 specification but tokens.py is not included in provided files

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 6: "See tokens.py for complete MBASIC 5.21 specification reference." - tokens.py is not in the provided source files, making this reference unverifiable.

---

#### code_vs_comment

**Description:** Comment about leading sign not adding to digit_count contradicts implementation

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line ~172: Comment says "Note: leading sign doesn't add to digit_count, it's a format modifier" but at line ~313 the code adds 1 to field_width for leading_sign: "if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']: field_width += 1". This suggests leading sign DOES consume a position in the field width calculation.

---

#### code_vs_comment

**Description:** Comment says identifiers preserve original case but implementation returns original_text without using table

**Affected files:**
- `src/case_string_handler.py`

**Details:**
Lines ~47-55: Long comment explains that identifiers preserve original case and mentions identifier_table exists but is not used. The code then returns original_text directly. This suggests the identifier_table infrastructure (get_identifier_table method) is dead code that should be removed or the comment should explain why it exists.

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for filesystem abstraction purposes

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py states:
"1. FileIO (this file) - Program management operations
   - Purpose: Load .BAS programs into memory, save from memory to storage"

src/filesystem/base.py states:
"1. FileIO (src/file_io.py) - Program management operations
   - Purpose: Load .BAS programs into memory, save from memory to disk"

One says 'storage', the other says 'disk'. While semantically similar, the inconsistency could confuse readers, especially since the web UI uses memory-based storage, not disk.

---

#### Documentation inconsistency

**Description:** Module docstring has redundant explanation about ProgramManager file I/O methods

**Affected files:**
- `src/editing/manager.py`

**Details:**
The module docstring contains a long section titled 'Why ProgramManager has its own file I/O methods:' that explains the separation between ProgramManager's direct file I/O and the FileIO abstraction. However, this explanation is somewhat redundant with the earlier 'FILE I/O ARCHITECTURE:' section which already explains the separation. The two sections could be consolidated for clarity.

---

#### Code vs Documentation inconsistency

**Description:** RealFileSystemProvider.__init__ docstring mentions base_path restriction but implementation allows None for unrestricted access

**Affected files:**
- `src/filesystem/real_fs.py`

**Details:**
The __init__ docstring states:
"Args:
    base_path: Optional base directory to restrict access.
              If None, allows access to entire filesystem."

The implementation correctly handles both cases:
- When base_path is set, _resolve_path() restricts access
- When base_path is None, _resolve_path() returns filename as-is

This is consistent. However, the security implications of allowing None (unrestricted filesystem access) could be more prominently documented, especially since this is used by local UIs where users have legitimate filesystem access.

---

#### code_vs_comment

**Description:** Docstring example shows escaped backslash in output but actual output would have single backslash

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In execute() method docstring:
'Examples:
>>> executor.execute("PRINT 2 + 2")
(True, " 4\\n")'

The double backslash (\\n) is correct for showing the literal string representation in Python docstring, but might be confusing. The actual return value would be the string ' 4\n' (with actual newline character), and repr() would show it as ' 4\\n'. This is technically correct but could be clearer.

---

#### code_vs_comment

**Description:** Comment says 'bare except' but code uses specific exception handling

**Affected files:**
- `src/interactive.py`

**Details:**
At line ~800, comment states: '# Fallback for non-TTY/piped input or any terminal errors (bare except)'

But the code uses 'except:' which is indeed a bare except. However, the comment's phrasing suggests this might be unintentional or a code smell that should be documented as intentional. The comment acknowledges it but doesn't explain why bare except is acceptable here.

---

#### code_vs_comment

**Description:** Comment about readline Ctrl+A binding may be misleading

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at lines ~90-95 states: 'Bind Ctrl+A to insert the character instead of moving cursor to beginning-of-line. This overrides default Ctrl+A (beginning-of-line) behavior. When user presses Ctrl+A, the terminal sends ASCII 0x01, and 'self-insert' tells readline to insert it as-is instead of interpreting it as a command.'

However, this conflicts with the typical readline behavior where 'self-insert' would insert a visible character. The code at line ~135 checks for '\x01' (Ctrl+A) to trigger edit mode, which suggests Ctrl+A should NOT be inserted as a character but should be intercepted. The readline binding may not work as described since the input() call would receive the character before the start() method can check for it.

---

#### documentation_inconsistency

**Description:** Module docstring lists commands that are not directly handled in execute_command()

**Affected files:**
- `src/interactive.py`

**Details:**
Module docstring at line ~7 lists: 'Direct commands (RUN, LIST, SAVE, LOAD, NEW, MERGE, FILES, SYSTEM, DELETE, RENUM, AUTO, EDIT, etc.)'

However, execute_command() at line ~220 only directly handles AUTO, EDIT, and HELP. The comment at line ~227 states: 'Everything else (including LIST, DELETE, RENUM, FILES, RUN, LOAD, SAVE, MERGE, SYSTEM, NEW, PRINT, etc.) goes through the real parser as immediate mode statements'

This means commands like RUN, LIST, SAVE, LOAD, NEW, MERGE, FILES, SYSTEM, DELETE, RENUM are NOT handled as 'direct commands' but as parsed immediate mode statements. The module docstring is misleading about the architecture.

---

#### code_vs_comment

**Description:** Comment says 'Note: program_runtime object persists' but clear_execution_state() doesn't verify this

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~440 in cmd_new() states: 'Note: program_runtime object persists, only its stacks are cleared'

However, clear_execution_state() at line ~185 only operates on self.program_runtime if it exists, and cmd_new() doesn't ensure program_runtime persists. If program_runtime is None, clear_execution_state() does nothing. The comment implies program_runtime always exists after NEW, but the code doesn't guarantee this.

---

#### code_vs_comment_conflict

**Description:** Comment about empty line_text_map is overly detailed and potentially misleading

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~220 states: 'Pass empty line_text_map since immediate mode uses temporary line 0\n(no source line text available for error reporting, but this is fine\nfor immediate mode where the user just typed the statement)'. However, the statement WAS just typed and IS available in the 'statement' parameter. The comment implies source text is unavailable when it actually is available, just not being passed.

---

#### code_vs_comment_conflict

**Description:** Comment about Runtime initialization mentions 'no source line text available' but doesn't explain why this is acceptable

**Affected files:**
- `src/interactive.py`

**Details:**
Comment says 'no source line text available for error reporting, but this is fine\nfor immediate mode where the user just typed the statement'. The justification is weak - if the user just typed it, we DO have the text (in 'statement' variable) and could pass it. The comment doesn't explain why we choose not to.

---

#### code_vs_comment

**Description:** Comment says 'clears itself to False' but code shows it's cleared by the else branch, not by itself

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 64-65 says:
"then clears itself to False. Prevents re-halting on same breakpoint."

But code at lines 454-455 shows:
else:
    self.state.skip_next_breakpoint_check = False

The flag doesn't clear 'itself' - it's explicitly cleared by the else branch when the breakpoint is skipped.

---

#### code_vs_comment

**Description:** Comment says NEXT I, J, K differs from separate statements, but the described behavior is actually the same for loop completion

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 1113-1119 says:
"NEXT I, J, K processes variables left-to-right: I first, then J, then K.
For each variable, _execute_next_single() is called to increment it and check if
the loop should continue. If _execute_next_single() returns True (loop continues),
execution jumps back to the FOR body and remaining variables are not processed.
If it returns False (loop finished), that loop is popped and the next variable is processed.

This differs from separate statements (NEXT I: NEXT J: NEXT K) which would
always execute sequentially, processing all three NEXT statements."

The claim about 'differs from separate statements' is misleading. If NEXT I loops back, control returns to FOR I body, so NEXT J and NEXT K wouldn't execute anyway (they're after NEXT I). The behavior is the same whether combined or separate, except for the case where I's loop completes - then J is processed immediately in combined form, vs requiring another iteration in separate form.

---

#### code_vs_comment

**Description:** Comment about WEND timing is verbose and potentially confusing about when pop occurs

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1050 states:
"# Pop the loop from the stack (after setting npc above, before WHILE re-executes).
# Timing: We pop NOW so the stack is clean before WHILE condition re-evaluation.
# The WHILE will re-push if its condition is still true, or skip the loop body
# if false. This ensures clean stack state and proper error handling if the
# WHILE condition evaluation fails (loop already popped, won't corrupt stack)."

The code pops AFTER setting npc, which is correct. However, the comment's emphasis on "before WHILE re-executes" could be misread as "before the jump" when it actually means "before the WHILE statement executes on the next tick". The comment is technically correct but could be clearer.

---

#### code_vs_comment

**Description:** Comment about RUN behavior describes halted flag inconsistently

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1470 states:
"# Note: RUN without args sets halted=True to stop current execution.
# The caller (e.g., UI tick loop) should detect halted=True and restart
# execution from the beginning if desired. This is different from
# RUN line_number which sets halted=False to continue execution inline."

The code shows:
if stmt.target:
    # RUN line_number path
    self.runtime.npc = PC.from_line(line_num)
    self.runtime.halted = False
else:
    # RUN without args path
    self.runtime.clear_variables()
    self.runtime.halted = True

The comment is accurate, but it's unusual that RUN without args sets halted=True (stopping execution) while RUN line_number sets halted=False (continuing execution). This asymmetry should be explained more clearly in the comment - why does RUN without args halt instead of jumping to the first line?

---

#### code_vs_comment

**Description:** Comment about INPUT state machine mentions input_file_number but doesn't explain its purpose clearly

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1640 states:
"# Set input prompt - execution will pause
# Sets: input_prompt (prompt text), input_variables (var list),
#       input_file_number (None for keyboard input, file # for file input)"

The code sets:
self.state.input_file_number = None  # None indicates keyboard input (not file)

However, the comment doesn't explain WHY input_file_number is needed when file input is synchronous (as stated in the docstring: "File input bypasses the state machine and reads synchronously"). If file input is synchronous, why store input_file_number at all? This suggests either the comment is outdated or there's a use case not explained.

---

#### Code vs Comment conflict

**Description:** Backward compatibility comment for print() method says it was renamed to avoid conflicts with Python's built-in, but output() is the standard IOHandler method name

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment says: "This method was renamed from print() to output() to avoid conflicts with Python's built-in print function."

However, output() is the standard method name defined in IOHandler base class (base.py). The comment implies print() was the original name, but base.py has always defined output() as the interface method. The comment is misleading about the reason for the naming.

---

#### Code vs Comment conflict

**Description:** get_char() backward compatibility comment claims it preserves non-blocking behavior, but always calls input_char(blocking=False) which is ignored anyway

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment says: "Note: Always calls input_char(blocking=False) for non-blocking behavior. The original get_char() implementation was non-blocking, so this preserves that behavior for backward compatibility."

But input_char() in web_io.py ignores the blocking parameter entirely and always returns "" immediately. The comment suggests the blocking parameter matters, but it doesn't in this implementation.

---

#### Documentation inconsistency

**Description:** get_screen_size() method exists in web_io.py but is not part of IOHandler base interface, creating API inconsistency

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py has get_screen_size() method with note: "Note: This is a web_io-specific method, not part of the IOHandler base interface. Other implementations (console, curses, gui) do not provide this method."

This creates an inconsistent API where code using WebIOHandler can call get_screen_size() but code using other IOHandler implementations cannot. This violates the abstraction principle of the IOHandler interface.

---

#### Documentation inconsistency

**Description:** Module docstring references SimpleKeywordCase in src/simple_keyword_case.py but this file is not provided in the source code listing

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
Docstring says: "For simpler force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py) which only supports force_lower, force_upper, and force_capitalize."

The file src/simple_keyword_case.py is not included in the provided source code files, making this reference unverifiable and potentially incorrect.

---

#### Code vs Documentation inconsistency

**Description:** ConsoleIOHandler.input_char() non-blocking mode uses select on Unix but warns about msvcrt unavailability on Windows, creating asymmetric error handling

**Affected files:**
- `src/iohandler/console.py`

**Details:**
Unix path: "if select.select([sys.stdin], [], [], 0.0)[0]: return sys.stdin.read(1) else: return """

Windows path: "except ImportError: import warnings; warnings.warn("msvcrt not available on Windows - non-blocking input_char() not supported", RuntimeWarning); return """

The Unix implementation silently returns "" when no input is available (expected behavior), but Windows warns when msvcrt is unavailable even though it also returns "" (same result). This creates inconsistent user experience across platforms.

---

#### Documentation inconsistency

**Description:** Module docstring claims 'Extended BASIC features' are always enabled with no option to disable, but no configuration or toggle mechanism is shown anywhere

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring states:
"MBASIC 5.21 Extended BASIC features: This implementation always enables Extended BASIC
features (e.g., periods in identifiers like 'RECORD.FIELD') as they are part of MBASIC 5.21.
There is no option to disable them."

This statement about 'no option to disable' is unnecessary if there's no configuration system shown. It implies there might have been or could be such an option, creating confusion.

---

#### Code internal inconsistency

**Description:** Inconsistent handling of original case: identifiers use 'original_case' field, keywords use 'original_case_keyword' field, but this distinction is only explained in one comment

**Affected files:**
- `src/lexer.py`

**Details:**
In read_identifier() for identifiers:
"token.original_case = ident"

In read_identifier() for keywords:
"token.original_case_keyword = display_case"

Comment explains:
"# Preserve original case for display. Identifiers use the original_case field
# to store the exact case as typed. Keywords use original_case_keyword to store
# the case determined by the keyword case policy (see Token class in tokens.py)."

This distinction is only documented in this one location and references an external file (tokens.py) not provided for verification.

---

#### code_vs_comment

**Description:** Comment about MID$ lookahead strategy may not match actual implementation complexity

**Affected files:**
- `src/parser.py`

**Details:**
At lines 527-548, there's a detailed comment about MID$ statement detection:
"# Detect MID$ used as statement: MID$(var, start, len) = value
# Look ahead to distinguish MID$ statement from MID$ function call
# MID$ statement has pattern: MID$ ( ... ) =
# MID$ function has pattern: MID$ ( ... ) in expression context
# Note: The lexer tokenizes 'MID$' (including the $) as a single token with type TokenType.MID
# Lookahead strategy: scan past balanced parentheses, check for = sign"

The implementation uses a try-except block with 'bare except' at line 543:
"except:
    # Bare except intentionally catches all exceptions during lookahead"

The comment at lines 544-547 justifies this:
"# (IndexError if we run past end, any parsing errors from malformed syntax)
# This is safe because position is restored below and proper error reported later"

However, using bare except is generally considered bad practice in Python, and the comment's justification that 'proper error reported later' may not be accurate if the lookahead fails for reasons other than 'not a MID$ statement'. This could mask genuine parsing errors.

---

#### code_vs_comment

**Description:** Comment about LINE modifier tokenization may be misleading

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1090-1092 states:
"# Check for LINE modifier (e.g., INPUT "prompt";LINE var$)
# LINE allows input of entire line including commas
# Note: The lexer tokenizes standalone LINE keyword as LINE_INPUT token.
# This is distinct from the LINE INPUT statement which is parsed separately."

The comment says "standalone LINE keyword as LINE_INPUT token" but in the context of INPUT statement, LINE is not standalone - it's part of the INPUT syntax. The comment could be clearer about when LINE is tokenized as LINE_INPUT vs when it's part of INPUT...LINE syntax.

---

#### code_vs_comment

**Description:** LPRINT comment about trailing separator logic is confusing

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1010-1015 states:
"# Add newline if there's no trailing separator
# For N expressions: N-1 separators (between items) = no trailing separator
#                    N separators (between items + at end) = has trailing separator
# Note: If len(separators) > len(expressions) (e.g., "LPRINT ;"), the trailing
# separator is already in the list and will suppress the newline."

The logic described is correct but the phrasing "N-1 separators (between items)" could be clearer. The comment mixes the concept of separators "between items" with trailing separators, which might confuse readers about whether the trailing separator is counted in the N-1 or N case.

---

#### code_vs_comment

**Description:** DEFTYPE comment about mode behavior is incomplete

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1850-1856 states:
"Note: This method always updates def_type_map during parsing, regardless of mode.
The type map is shared between parsing passes in batch mode and affects variable
type inference throughout the program. The AST node is created for program
serialization/documentation."

The comment mentions "regardless of mode" and "batch mode" but doesn't explain what modes exist or what the alternative behavior would be. This suggests there might be an interactive mode vs batch mode distinction that isn't fully documented in this comment.

---

#### code_vs_comment

**Description:** DIM statement comment about dimension expressions contradicts typical BASIC behavior

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1730-1734 states:
"Dimension expressions: This implementation matches MBASIC 5.21 behavior by accepting
any expression for array dimensions (e.g., DIM A(X*2, Y+1)). Dimensions are evaluated
at runtime. Note: Some compiled BASICs (GW-BASIC, QuickBASIC) require constants only."

This comment claims the implementation matches MBASIC 5.21 by accepting expressions, but then notes that GW-BASIC and QuickBASIC require constants. However, GW-BASIC is often considered very similar to MBASIC. This suggests either:
1. The comment is incorrect about GW-BASIC requiring constants
2. The comment is incorrect about matching MBASIC 5.21 behavior
3. There's a version difference not explained

Without access to MBASIC 5.21 documentation, this cannot be verified.

---

#### code_vs_comment

**Description:** DEF FN comment about function name normalization placement

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1895-1901 states:
"Function name normalization: All function names are normalized to lowercase with
'fn' prefix (e.g., "FNR" becomes "fnr", "FNA$" becomes "fna$") for consistent
lookup. This matches the lexer's identifier normalization and ensures function
calls match their definitions regardless of case."

This detailed normalization comment appears in the DEF FN parser but doesn't show the actual normalization code in the visible portion. The comment should either be moved to where normalization occurs or reference where it happens.

---

#### code_vs_comment

**Description:** Comment in parse_resume() says RESUME and RESUME 0 both retry error statement, but implementation stores actual value

**Affected files:**
- `src/parser.py`

**Details:**
Comment states:
"Note: RESUME and RESUME 0 both retry the statement that caused the error."

Code implementation:
```python
line_number = int(self.advance().value)
```

The comment suggests RESUME 0 has special meaning (retry error statement), and notes that interpreter treats 0 and None equivalently. However, the parser stores the actual value (0 or other line number) without special handling. This creates ambiguity about whether 0 is a sentinel value or an actual line number 0.

---

#### code_vs_comment

**Description:** parse_width() docstring describes device parameter as 'implementation-specific' but provides no guidance on what values are valid

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"device: Optional device expression (implementation-specific; may support
file numbers, device codes, or other values depending on the interpreter)"

The code simply parses any expression:
```python
device = self.parse_expression()
```

The comment acknowledges the parameter is implementation-specific but provides no examples or constraints. This makes it unclear what valid device values are (file numbers like #1, device names like "LPT1:", numeric codes, etc.).

---

#### documentation_inconsistency

**Description:** parse_common() docstring says 'Non-empty parentheses are an error' but doesn't show error handling code

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"The empty parentheses () indicate an array variable (all elements shared).
This is just a marker - no subscripts are specified or stored. Non-empty
parentheses are an error (parser enforces empty parens only)."

Code implementation:
```python
if self.match(TokenType.LPAREN):
    self.advance()
    if not self.match(TokenType.RPAREN):
        raise ParseError("Expected ) after ( in COMMON array", self.current())
    self.advance()
```

The error message "Expected ) after ( in COMMON array" doesn't clearly communicate that subscripts are not allowed. A user might interpret this as a syntax error rather than understanding that COMMON arrays cannot have subscripts specified.

---

#### code_vs_comment

**Description:** parse_def_fn() comment about function name normalization is inconsistent with actual behavior

**Affected files:**
- `src/parser.py`

**Details:**
Comment states:
"function_name = 'fn' + raw_name  # Use lowercase 'fn' to match function calls"

And later:
"# raw_name already starts with lowercase 'fn' from lexer normalization
function_name = raw_name"

The first comment suggests adding 'fn' prefix, while the second suggests it's already there. The code handles two cases:
1. DEF FN R (space): adds 'fn' prefix
2. DEF FNR (no space): already has 'fn' from lexer

The comments don't clearly explain why these two paths exist or that they're handling different tokenization scenarios.

---

#### code_vs_comment

**Description:** apply_keyword_case_policy docstring says 'Callers may pass keywords in any case' but emit_keyword docstring says 'keyword MUST be normalized lowercase by caller'

**Affected files:**
- `src/position_serializer.py`

**Details:**
apply_keyword_case_policy docstring: 'Callers may pass keywords in any case.'

emit_keyword docstring: 'Args:
    keyword: The keyword to emit (MUST be normalized lowercase by caller)'

These are contradictory requirements for the same parameter type.

---

#### code_vs_comment

**Description:** preserve policy docstring describes defensive fallback but doesn't explain when this incorrect usage would occur

**Affected files:**
- `src/position_serializer.py`

**Details:**
In apply_keyword_case_policy for 'preserve' policy:

'# The "preserve" policy means callers should pass keywords already in the correct case
# and this function returns them as-is. However, since we can\'t know the original case
# here, we provide a defensive fallback (capitalize) for robustness in case this
# function is called incorrectly with "preserve" policy.'

This suggests the function might be called incorrectly but doesn't explain the scenario. If callers should never call this with 'preserve', why have the fallback?

---

#### documentation_inconsistency

**Description:** Module docstrings have asymmetric cross-references

**Affected files:**
- `src/resource_limits.py`
- `src/resource_locator.py`

**Details:**
resource_limits.py states: 'Note: This is distinct from resource_locator.py which finds package data files.'

resource_locator.py states: 'Note: This is distinct from resource_limits.py which enforces runtime execution limits.'

Both files correctly distinguish themselves from each other, but the phrasing is slightly different. resource_limits.py says resource_locator 'finds package data files' while resource_locator.py says resource_limits 'enforces runtime execution limits'. This is consistent in meaning but could be more parallel in structure.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for string length limits

**Affected files:**
- `src/resource_limits.py`

**Details:**
The parameter is named 'max_string_length' and documented as 'Maximum length for a string variable (bytes)' in multiple places.

However, in check_string_length() method, the error message says: 'String too long: {byte_length} bytes (limit: {self.max_string_length} bytes)'

While in estimate_size() method, the comment says: 'String: UTF-8 byte length + 4-byte length prefix'

The term 'length' is used but it's actually measuring 'byte length' or 'size'. This could be confusing since string 'length' often refers to character count, not byte count. The code is consistent in using bytes, but the terminology could be clearer.

---

#### code_vs_comment_conflict

**Description:** Comment about MBASIC 5.21 compatibility in unlimited limits may be misleading

**Affected files:**
- `src/resource_limits.py`

**Details:**
In create_unlimited_limits() function:

The code sets: 'max_string_length=1024*1024'  # 1MB strings (for testing/development - not MBASIC compatible)

However, the other two preset functions (create_web_limits and create_local_limits) both set max_string_length=255 with comment '# 255 bytes (MBASIC 5.21 compatibility)'

The comment in create_unlimited_limits() correctly notes it's 'not MBASIC compatible', but this creates an inconsistency where the 'unlimited' preset actually breaks MBASIC compatibility. This may be intentional for testing, but could cause confusion if someone uses unlimited limits expecting MBASIC-compatible behavior.

---

#### documentation_inconsistency

**Description:** Incomplete docstring for get_all_variables() method

**Affected files:**
- `src/runtime.py`

**Details:**
Line 1009-1023: The docstring for get_all_variables() is incomplete:

"""Export all variables with structured type information.

Returns detailed information about each variable including:
- Base name (without type suffix)
- Type suffix character
- For scalars: current value
- For arrays: dimensions and base
- Access tracking: last_read and last_write info

Returns:
    list: List of dictionaries with variable information
          Each dict contains:
"""

The docstring ends abruptly with "Each dict contains:" without listing what the dict actually contains. The implementation is present but the documentation is incomplete.

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

While all are technically correct, the varying levels of detail (some show 2 examples, some show 3) and placement (some in Notes, some inline) create minor inconsistency in documentation style.

---

#### documentation_inconsistency

**Description:** Duplicate documentation of settings file paths in two files

**Affected files:**
- `src/settings.py`
- `src/settings_backend.py`

**Details:**
Both settings.py and settings_backend.py document the same file paths:

settings.py docstring:
"- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)
- Project: .mbasic/settings.json in project directory"

settings_backend.py FileSettingsBackend docstring:
"Stores settings in JSON files:
- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)
- Project: .mbasic/settings.json in project directory"

This duplication could lead to maintenance issues if paths change.

---

#### code_vs_comment

**Description:** Comment about file-level settings infrastructure being 'fully implemented' is misleading

**Affected files:**
- `src/settings.py`

**Details:**
Multiple comments state file-level settings are 'fully implemented':

In SettingsManager docstring:
"Note: File-level settings infrastructure is fully implemented (file_settings dict,
FILE scope support in get/set/reset methods), but currently unused."

In get() method:
"Note: File-level settings infrastructure is fully implemented and functional.
The file_settings dict can be set programmatically and is checked first in precedence."

However, the infrastructure is only partially implemented:
- file_settings dict exists
- get() checks it
- set() can write to it
- reset_to_defaults() can clear it
- BUT: load() never populates it from any source
- BUT: save() never persists it anywhere

So it's not 'fully implemented' - it's a runtime-only dict with no persistence.

---

#### code_vs_documentation

**Description:** Comments mention settings not included but don't explain why

**Affected files:**
- `src/settings_definitions.py`

**Details:**
Two comments mention excluded settings:

"# Note: editor.tab_size setting not included - BASIC uses line numbers for program structure,
# not indentation, so tab size is not a meaningful setting for BASIC source code"

"# Note: Line numbers are always shown - they're fundamental to BASIC!
# editor.show_line_numbers setting not included - makes no sense for BASIC"

These are good explanatory comments, but they reference settings that don't exist anywhere in the codebase. This could confuse developers looking for these settings. The comments are defensive documentation against expected but non-existent features.

---

#### documentation_inconsistency

**Description:** RedisSettingsBackend comment mentions 'nicegui or redis-py' but only redis-py is imported

**Affected files:**
- `src/settings_backend.py`

**Details:**
RedisSettingsBackend.__init__ docstring says:
"Args:
    redis_client: Redis client instance (from nicegui or redis-py)"

But in create_settings_backend(), only redis-py is used:
"import redis
redis_client = redis.from_url(redis_url, decode_responses=True)"

No nicegui Redis client is ever used. The comment suggests two possible sources but only one is implemented.

---

#### code_vs_comment

**Description:** RedisSettingsBackend TTL comment says '24 hours (matches NiceGUI session expiry)' but this is hardcoded assumption

**Affected files:**
- `src/settings_backend.py`

**Details:**
In RedisSettingsBackend._set_data():
"# Set with TTL of 24 hours (matches NiceGUI session expiry)
self.redis.setex(self.redis_key, 86400, data)"

The comment assumes NiceGUI session expiry is 24 hours, but this is not verified anywhere in the code. If NiceGUI's session expiry changes or is configurable, this hardcoded value would be incorrect. The comment makes an assertion about external behavior without verification.

---

#### Code vs Comment conflict

**Description:** Comment in _create_setting_widget() claims both removeprefix() and fallback [6:] 'only strip from the beginning', but this is redundant since slicing [6:] by definition only operates on the beginning of the string. The comment seems to over-explain obvious behavior.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment in _create_setting_widget():
"# Create display label (strip 'force_' prefix from beginning for cleaner display)
# Note: Both removeprefix() and the fallback [6:] only strip from the beginning,
# ensuring we don't modify 'force_' appearing elsewhere in the string"

The note about [6:] 'only strip from the beginning' is redundant - string slicing from the start always operates on the beginning.

---

#### Code vs Comment conflict

**Description:** Comment in _on_reset() states it compares 'actual value' not 'display label' and mentions 'force_' prefix stripping, but this explanation is overly detailed for what is simply setting a radio button state to match the default value.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment in _on_reset():
"# Set radio button to default value
# Note: Compares actual value (stored in _actual_value) not display label
# since display labels have 'force_' prefix stripped (see _create_setting_widget)"

The code simply does: rb.set_state(rb._actual_value == defn.default)

The comment over-explains the comparison when the code is self-evident.

---

#### Documentation inconsistency

**Description:** The cmd_break() docstring states 'Breakpoints can be set at any time (before or during execution)' and 'Use RUN to start the program', but there's no clear documentation about what happens if you set breakpoints during execution or how the breakpoint system integrates with the running program.

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
cmd_break() docstring:
"Breakpoints can be set at any time (before or during execution).
They are checked during program execution at each statement.
Use RUN to start the program, and it will pause when reaching breakpoints."

The enhance_run_command() method modifies RUN behavior, but there's no documentation about how breakpoints set during execution (after RUN) are handled.

---

#### code_vs_comment

**Description:** Comment about syntax error priority is redundant with code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _get_status_char method:
"Get the status character for a line based on priority.

Priority order (highest to lowest):
1. Syntax error (?) - highest priority
2. Breakpoint (●) - medium priority
3. Normal ( ) - default"

The code implementation is:
"if has_syntax_error:
    return '?'
elif line_number in self.breakpoints:
    return '●'
else:
    return ' '"

The comment exactly mirrors the code structure with no additional information. This is not an inconsistency per se, but the comment adds no value and could become outdated if priorities change.

---

#### code_vs_comment

**Description:** Comment about fast path optimization is misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress method:
"# FAST PATH: For normal printable characters, bypass all processing
# This is critical for responsive typing
if len(key) == 1 and key >= ' ' and key <= '~':
    return super().keypress(size, key)"

Comment claims this bypasses 'all processing', but super().keypress() still does significant processing (urwid's Edit widget processing, cursor movement, text insertion, etc.). The comment should say 'bypass editor-specific processing' or 'bypass syntax checking and column protection'.

---

#### code_vs_comment

**Description:** Comment says _create_toolbar is 'UNUSED' but provides detailed explanation that could be misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
At line ~420, comment states:
STATUS: UNUSED - not called anywhere in current implementation.

The toolbar was removed from the UI in favor of Ctrl+U menu for better keyboard navigation. This fully-implemented method is retained for reference in case toolbar functionality is desired in the future. Can be safely removed if no plans to restore.

This is accurate documentation of unused code, but the phrase 'Can be safely removed' conflicts with 'retained for reference'. Should clarify intent.

---

#### code_vs_comment

**Description:** Comment about Interpreter lifecycle says it's never recreated, but this seems to conflict with the need to reset state between runs

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~180 says:
# Interpreter Lifecycle:
# Created ONCE here in __init__ and reused throughout the session.
# The interpreter object itself is NEVER recreated - the same instance is used
# for the lifetime of the UI session.

This raises the question of how state is reset between program runs. The comment doesn't explain how the interpreter is cleaned/reset, which could be important for understanding the architecture.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'statement' vs 'stmt' in variable names and UI text

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The code uses both 'stmt' and 'statement' inconsistently:
- highlight_stmt parameter (line ~870)
- 'step_statement' mode string (line ~860)
- STEP_KEY for 'Step Statement' (line ~750)
- stmt_offset in PC (line ~880)

While 'stmt' is a common abbreviation, mixing both forms in user-facing text and internal APIs could cause confusion.

---

#### code_vs_comment

**Description:** Comment about column positioning in _smart_insert_line is inconsistent with actual column numbers

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
At line ~1195, comment says:
# Position cursor on the new line, at the code area (column 7)

But the actual position calculation uses column 7 for a line number that could be variable width. The comment assumes fixed-width line numbers, but the code uses variable-width parsing elsewhere (e.g., _parse_line_number). This could be incorrect for line numbers with different digit counts.

---

#### code_vs_comment

**Description:** Comment about main widget storage strategy differs between methods but implementation is consistent

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple comments explain main widget storage:

1. _show_help (line ~520): "Main widget retrieval: Use self.base_widget (stored at UI creation time in __init__) rather than self.loop.widget (which reflects the current widget and might be a menu or other overlay)."

2. _activate_menu (line ~620): "Extract base widget from current loop.widget to unwrap any existing overlay. This differs from _show_help/_show_keymap/_show_settings which use self.base_widget directly, since menu needs to work even when other overlays are already present."

These comments accurately describe different strategies for different use cases, but the distinction could be confusing without understanding the full context.

---

#### code_vs_comment

**Description:** Comment about status bar behavior during errors is inconsistent across methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple locations have comments about status bar behavior:

1. Line ~1165: "# Status bar stays at default - error is displayed in output"
2. Line ~1220: "# Status bar stays at default (STATUS_BAR_SHORTCUTS) - error is in output"
3. Line ~1240: "# Status bar stays at default (STATUS_BAR_SHORTCUTS) - error is in output"
4. Line ~1260: "# Status bar stays at default - error is displayed in output"
5. Line ~1280: "# No status bar update - program output will show in output window"

Some comments specify STATUS_BAR_SHORTCUTS constant while others just say 'default'. The implementation appears consistent but comment wording varies.

---

#### code_internal_inconsistency

**Description:** Inconsistent error message formatting - some use box drawing characters, some don't specify format in comments

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Error formatting varies:

1. Parse errors (line ~1160): Use box with ┌─ Parse Error ────┐
2. Startup errors (line ~1230): Use box with ┌─ Startup Error ──┐
3. Runtime errors (line ~1320): Use box with ┌─ Runtime Error ──┐
4. Unexpected errors (line ~1270): Use box with ┌─ Unexpected Error ─┐

All use similar box formatting but the box widths and dash counts differ slightly. This is a minor visual inconsistency.

---

#### code_vs_comment

**Description:** Comment about statement-level precision for GOSUB uses 0-based indexing but may be confusing without context

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1090 states:
"# Show statement-level precision for GOSUB return address
# return_stmt is statement offset (0-based index): 0 = first statement, 1 = second, etc."

The comment is accurate but the display format 'line {entry['from_line']}.{return_stmt}' uses 0-based statement numbers which might be confusing to users expecting 1-based numbering.

---

#### code_vs_comment

**Description:** Comment says _sync_program_to_runtime doesn't start execution, but doesn't mention it can preserve running execution state

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sync_program_to_runtime method docstring:
"Sync program to runtime without resetting PC.

Updates runtime's statement_table and line_text_map from self.program,
but preserves current PC/execution state. This allows LIST and other
commands to see the current program without starting execution."

The comment focuses on "without starting execution" but the implementation has complex logic to preserve PC when self.running=True and not paused_at_breakpoint. The docstring could be clearer about when PC is preserved vs reset.

---

#### code_vs_comment_conflict

**Description:** Comment about version.py conflicts with hardcoded version implementation

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Comment at line ~82:
"# Hardcoded MBASIC version for documentation
# Note: Project has internal implementation version (src/version.py) separate from this
return '5.21'  # MBASIC 5.21 language version"

The comment suggests there's a src/version.py file with a different version, but this file is not provided in the source code listing. The comment implies a separation between 'documentation version' and 'implementation version' but doesn't explain why they should differ or how to keep them in sync.

---

#### documentation_inconsistency

**Description:** Docstring says 'ESC/Q to exit' but implementation also accepts lowercase 'q'

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Module docstring states:
"Provides:
- Up/Down scrolling through help content
- Enter to follow links
- ESC/Q to exit"

But keypress() method handles:
if key in ('q', 'Q', 'esc'):

So both uppercase Q and lowercase q work, but docstring only mentions uppercase Q.

---

#### code_vs_comment_conflict

**Description:** Comment says 'QUIT_KEY is None (menu-only)' but keybindings module is not shown

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Comment at line ~37:
"('Quit', 'quit'),  # QUIT_KEY is None (menu-only)"

This references a QUIT_KEY constant from the keybindings module (kb), but we cannot verify this claim since the keybindings module source is not provided. The comment implies there's no keyboard shortcut for quit outside the menu.

---

#### code_vs_comment_conflict

**Description:** Comment says 'STACK_KEY is '' (menu-only)' but keybindings module is not shown

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Comment at line ~52:
"('Execution Stack', '_toggle_stack_window'),  # STACK_KEY is '' (menu-only)"

This references a STACK_KEY constant from the keybindings module (kb), but we cannot verify this claim since the keybindings module source is not provided. The comment implies there's no keyboard shortcut for stack window outside the menu.

---

#### documentation_inconsistency

**Description:** Search result path format inconsistency in comments

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~370:
"# Check if target is already an absolute path (from search results)
# Absolute paths start with common/ or ui/"

But earlier in _search_indexes() at line ~165, search results store paths as:
results.append((
    tier_label,
    file_info.get('path', ''),
    ...
))

The comment describes these as 'absolute paths' but they're actually help-root-relative paths. The term 'absolute' is misleading since they're relative to help_root, not filesystem absolute.

---

#### Code vs Comment conflict

**Description:** Comment claims MAXIMIZE_OUTPUT_KEY is 'menu-only feature, not documented as keyboard shortcut', but the constant is defined with a keyboard shortcut value.

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line 191: MAXIMIZE_OUTPUT_KEY = 'ctrl shift m'

Comment in KEYBINDINGS_BY_CATEGORY (lines 217-222) says:
# - MAXIMIZE_OUTPUT_KEY (Shift+Ctrl+M) - Menu-only feature, not documented as keyboard shortcut

If it's truly menu-only, why define it with a keyboard shortcut value? This suggests either the comment is outdated or the implementation doesn't match the intent.

---

#### Code vs Documentation inconsistency

**Description:** Inconsistent key display format between keybindings.py and keymap_widget.py for Shift+Ctrl combinations.

**Affected files:**
- `src/ui/keybindings.py`
- `src/ui/keymap_widget.py`

**Details:**
In keybindings.py, key_to_display() returns:
'shift ctrl b' -> '^Shift+B'

In keymap_widget.py, _format_key_display() converts:
'Shift+Ctrl+V' -> 'Shift+^V'

These two functions produce different formats for the same type of key combination. The keybindings.py version puts the caret before 'Shift', while keymap_widget.py puts it after.

---

#### Code vs Comment conflict

**Description:** Comment describes path normalization duplication but implementation details differ slightly

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Line 267 comment states:
Note: Path normalization logic is duplicated in _open_link_in_new_window().
Both methods use similar approach: resolve relative paths, normalize to help_root,
handle path separators. If modification needed, update both methods consistently.

However, comparing _follow_link() (lines 267-298) and _open_link_in_new_window() (lines 682-710), the implementations have subtle differences:
- _follow_link checks for absolute paths with: if target.startswith('/') or target.startswith('common/') or ':/' in target or ':\\' in target
- _open_link_in_new_window checks: if not url.startswith('.')

These are different conditions that may not handle all cases identically. The comment suggests they use 'similar approach' but the actual logic differs in how absolute vs relative paths are detected.

---

#### Code vs Comment conflict

**Description:** Comment about table formatting duplication references non-existent file

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Line 714 comment in _format_table_row() states:
Note: This implementation may be duplicated in src/ui/markdown_renderer.py.
If both implementations exist and changes are needed to table formatting logic,
consider extracting to a shared utility module to maintain consistency.

However, src/ui/markdown_renderer.py is not provided in the source files, so we cannot verify if this duplication actually exists. The comment suggests uncertainty ('may be duplicated') but provides no way to verify this claim.

---

#### Code vs Documentation inconsistency

**Description:** Comment about modal behavior is misleading

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 48 comment states:
# Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())

This comment is technically correct but potentially misleading. The dialog uses transient() and grab_set() which do make it modal in the UI sense (blocking parent interaction), but the comment's emphasis on 'doesn't block code execution' might confuse readers about what 'modal' means in this context. The comment seems to be clarifying that it's not using wait_window() for synchronous blocking, but this level of detail might not be necessary or could be clearer.

---

#### Code vs Comment conflict

**Description:** Comment about help display mechanism is imprecise

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 147 comment states:
# Show short help as inline label (not a hover tooltip, just a gray label)

The comment clarifies it's 'not a hover tooltip' but this seems defensive - there's no code that would suggest it's a tooltip. The comment may be outdated from a previous implementation or design discussion where tooltips were considered. The parenthetical clarification adds no value to understanding the current code.

---

#### code_vs_comment

**Description:** Comment describes 3-pane layout with specific weights but implementation may differ

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring lines 48-54 states:
- 3-pane vertical layout (weights: 3:2:1 = total 6 units):
  * Editor with line numbers (top, ~50% = 3/6 - weight=3)
  * Output pane (middle, ~33% = 2/6 - weight=2)
    - Contains INPUT row (shown/hidden dynamically for INPUT statements)
  * Immediate mode input line (bottom, ~17% = 1/6 - weight=1)

Code at lines 218-220, 227-228, 234-235 shows:
paned.add(editor_frame, weight=3)
paned.add(output_frame, weight=2)
paned.add(immediate_frame, weight=1)

Weights match documentation. However, immediate_frame has height=40 forced (line 237: input_frame.pack_propagate(False)) which may override the weight-based sizing, making it not truly ~17% but a fixed 40 pixels.

---

#### code_vs_comment

**Description:** Variables window heading text comment doesn't match actual implementation detail

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 1089-1090 comment states:
# Set initial heading text with down arrow (matches self.variables_sort_column='accessed', descending)
tree.heading('#0', text='↓ Variable (Last Accessed)')

The comment says 'descending' but the actual sort direction is controlled by self.variables_sort_reverse=True (line 127). While True typically means descending, the comment should reference the actual variable name for clarity.

---

#### documentation_inconsistency

**Description:** Docstring usage example references TkIOHandler but doesn't show its import or initialization details

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 56-66 show usage example:
Usage:
    from src.ui.tk_ui import TkBackend, TkIOHandler
    from src.editing.manager import ProgramManager

    io = TkIOHandler()  # TkIOHandler created without backend reference initially
    def_type_map = {}  # Type suffix defaults for variables (DEFINT, DEFSNG, etc.)
    program = ProgramManager(def_type_map)
    backend = TkBackend(io, program)
    backend.start()  # Runs Tk mainloop until window closed

The comment says 'TkIOHandler created without backend reference initially' but doesn't explain that the backend reference is set later. Looking at line 318, the actual initialization is:
tk_io = TkIOHandler(self._add_output, self.root, backend=self)

The usage example is misleading - it shows TkIOHandler() with no arguments, but the actual code passes three arguments.

---

#### code_vs_comment_conflict

**Description:** Comment about OPTION BASE validation contradicts defensive else clause

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _edit_array_element method around line 680:
Comment says: "OPTION BASE only allows 0 or 1 (validated by OPTION statement parser). The else clause is defensive programming for unexpected values."

Code has:
if array_base == 0:
    default_subscripts = ','.join(['0'] * len(dimensions))
elif array_base == 1:
    default_subscripts = ','.join(['1'] * len(dimensions))
else:
    # Defensive fallback for invalid array_base (should not occur)
    default_subscripts = ','.join(['0'] * len(dimensions))

If OPTION BASE truly only allows 0 or 1 and this is validated, the else clause should never execute. The comment acknowledges this but the defensive code remains, suggesting either: (1) validation isn't complete, (2) array_base could be modified elsewhere, or (3) the else clause is unnecessary.

---

#### code_vs_comment_conflict

**Description:** Comment about clearing yellow highlight contradicts when highlight is actually restored

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_mouse_click method around line 1310:
Comment says: "Clear yellow statement highlight when clicking (allows text selection to be visible). The highlight is restored when execution resumes or when stepping to the next statement."

This comment describes when the highlight is restored, but there's no code visible in this file that shows the restoration logic. The comment makes a claim about behavior that isn't implemented in the visible code, suggesting either: (1) the restoration happens elsewhere and should be referenced, or (2) the comment is describing intended behavior that isn't fully implemented.

---

#### code_vs_comment_conflict

**Description:** Comment about showing error list contradicts simplicity claim

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1260:
Comment says: "Only show full error list in output if there are multiple errors. For single errors, the red ? icon in the editor is sufficient feedback. This avoids cluttering the output pane with repetitive messages during editing. Note: We don't track 'first time' - this is intentionally simple."

The comment claims the approach is 'intentionally simple' and doesn't track 'first time', but then immediately implements conditional logic based on error count (len(errors_found) > 1). This is not particularly simple - it's a specific UX decision. The comment seems to be defending against a criticism that wasn't made, suggesting it may be outdated from a code review discussion.

---

#### code_vs_comment

**Description:** Comment describes keyboard shortcut behavior but doesn't mention all modifier key handling

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1055: 'Allow keyboard shortcuts with modifier keys (Control, Alt, etc.) to propagate'
Code checks: 'if event.state & 0x000C:  # Control or Alt pressed'
Comment says 'etc.' but code only checks Control (0x0004) and Alt (0x0008), not other modifiers like Command/Meta. Comment should be more precise about which modifiers are handled.

---

#### code_vs_comment

**Description:** Comment about CONT command validation doesn't mention all actual validation checks

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1550: 'Validation: Requires runtime exists and runtime.stopped is True. Invalid if program was edited after stopping.'
Code at line ~1558: 'if not self.runtime or not self.runtime.stopped:'
The comment mentions 'Invalid if program was edited after stopping' but there's no code checking for program edits. Either the validation is incomplete or the comment is outdated.

---

#### code_vs_comment

**Description:** Method name _add_immediate_output() is misleading - docstring admits it's historical and just forwards to _add_output()

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method at line 1145:
def _add_immediate_output(self, text):
    """Add text to main output pane.

    This method name is historical - it simply forwards to _add_output().
    In the Tk UI, immediate mode output goes to the main output pane.
    Note: self.immediate_history exists but is always None (see __init__). Code
    that references it (e.g., _setup_immediate_context_menu) guards against None.
    """
    self._add_output(text)

The method name suggests it adds to immediate output, but it actually adds to main output. This is a naming inconsistency that could confuse maintainers.

---

#### code_vs_comment

**Description:** Dead code retained with comment explaining it's unused, creating maintenance burden

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method _setup_immediate_context_menu() at line 1213:
"""Setup right-click context menu for immediate history widget.

NOTE: This method is currently unused - immediate_history is always None
in the Tk UI (see __init__). This is dead code retained for potential
future use if immediate mode gets its own output widget.
"""

Also references dead code in _copy_immediate_selection() and _select_all_immediate() methods. The comment acknowledges these are unused but they remain in the codebase.

---

#### code_vs_comment

**Description:** Comment in _on_cursor_move says 'Schedule deletion after current event processing' but doesn't explain the specific technical reasons

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment says:
"# Schedule deletion after current event processing to avoid interfering
# with ongoing key/mouse event handling (prevents cursor position issues,
# undo stack corruption, and widget state conflicts during event processing)"

This is actually accurate and well-documented. The after_idle() call does prevent these issues. This is NOT an inconsistency - the comment correctly explains the implementation.

---

#### documentation_inconsistency

**Description:** Class docstring says 'BASIC line numbers are part of the text content (not drawn separately in the canvas)' but _redraw() docstring repeats this with slightly different wording

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring: "Note: BASIC line numbers are part of the text content (not drawn separately in the canvas)."

_redraw() docstring: "Note: BASIC line numbers are parsed from text content (not drawn in canvas)."

Both say the same thing but with different phrasing ('separately in the canvas' vs 'in canvas'). Minor inconsistency in documentation style.

---

#### code_vs_comment

**Description:** _redraw() docstring references _parse_line_number() validation but doesn't mention the specific regex pattern

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_redraw() docstring says:
"Note: BASIC line numbers are parsed from text content (not drawn in canvas).
See _parse_line_number() for the regex-based extraction logic that validates
line number format (requires whitespace or end-of-line after the number)."

This correctly describes what _parse_line_number() does, but the phrase 'end-of-line' is ambiguous (could mean newline character or end-of-string). The actual regex uses $ which is end-of-string, not \n which would be a newline character.

---

#### code_vs_documentation

**Description:** update_line_references() docstring describes 'Two-pass approach' but implementation uses single regex substitution pass

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring states: "Two-pass approach using different regex patterns:
Pattern 1: Match keyword + first line number (GOTO/GOSUB/THEN/ELSE/ON...GOTO/ON...GOSUB)
Pattern 2: Match comma-separated line numbers (for ON...GOTO/GOSUB lists)"

The implementation does use two regex patterns (pattern and comma_pattern), but they're applied sequentially in a single pass through the code, not in two separate passes. The term 'two-pass' typically implies processing the entire input twice. This is more accurately a 'two-pattern single-pass approach'.

---

#### code_vs_documentation

**Description:** renum_program() docstring describes callback responsibility but doesn't specify what 'in-place' means for immutable AST nodes

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring states: "renum_callback: Function(stmt: StatementNode, line_map: Dict[int, int]) -> None
that updates statement line number references in-place."

The term 'in-place' typically means modifying the object directly. However, if StatementNode objects have immutable line number fields, 'in-place' would mean modifying attributes of the node object, not replacing the node itself. The docstring should clarify whether the callback should:
1. Modify attributes of the stmt object (true in-place)
2. Return a new statement object (not in-place)
3. Modify child nodes of stmt (partially in-place)

The example reference to curses_ui.py suggests it's true in-place modification, but this should be explicit.

---

#### Code vs Comment conflict

**Description:** The get_cursor_position() method docstring says it 'always returns line 0, column 0' and is a 'placeholder implementation', but the actual return statement uses dict keys as integers {0, 0} instead of the documented string keys 'line' and 'column'.

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Docstring says: 'Returns:\n            Dict with \'line\' and \'column\' keys (placeholder: always {0, 0})'
Comment in method says: '# This would need async support, for now return placeholder\n        return {\'line\': 0, \'column\': 0}'
The docstring describes the return format correctly, but uses confusing notation '{0, 0}' which looks like a set literal rather than a dict with string keys.

---

#### Documentation inconsistency

**Description:** The cmd_delete() and cmd_renum() docstrings reference 'curses_ui.py or tk_ui.py' as example implementations, but these files are not present in the provided source code, making the references unhelpful.

**Affected files:**
- `src/ui/visual.py`

**Details:**
cmd_delete() docstring: 'See curses_ui.py or tk_ui.py for example implementations.'
cmd_renum() docstring: 'See ui_helpers.renum_program() for the shared implementation logic.'
These references assume files exist that are not in the provided codebase.

---

#### Code vs Documentation inconsistency

**Description:** The cmd_cont() docstring references 'tk_ui.cmd_cont()' as an example implementation, but tk_ui.py is not in the provided source code.

**Affected files:**
- `src/ui/visual.py`

**Details:**
Docstring says: 'See tk_ui.cmd_cont() for example implementation.'
This reference cannot be followed as the file is not provided.

---

#### Code vs Comment conflict

**Description:** The _internal_change_handler comment says 'CodeMirror sends new value as args' but this is ambiguous - it's unclear if 'args' means e.args specifically or a general term for arguments.

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Comment: '# CodeMirror sends new value as args'
Code: 'self._value = e.args'
The comment could be clearer that it means the e.args attribute specifically, not just 'as arguments'.

---

#### code_vs_comment

**Description:** Comment references _enable_inline_input() method that is not visible in the provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~70 references:
# by _enable_inline_input() in the NiceGUIBackend class.

This method is not shown in the provided code snippet (part 1), suggesting either:
1. The method exists in part 2 (not shown)
2. The comment is outdated and references a removed method
3. The method was renamed

---

#### code_vs_comment

**Description:** Comment says prompt display is handled by _get_input via _enable_inline_input, but implementation details not visible

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~62-64:
# Don't print prompt here - the input_callback (backend._get_input) handles
# prompt display via _enable_inline_input() method in the NiceGUIBackend class

The _get_input method is not shown in the provided code, so cannot verify if this is accurate.

---

#### documentation_inconsistency

**Description:** Inconsistent version number references - hardcoded '5.21' vs imported VERSION

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Multiple locations reference version numbers:
1. Line ~558: # Note: '5.21' is the MBASIC language version (intentionally hardcoded)
2. Line ~560: ui.label('MBASIC 5.21 Web IDE').classes('text-lg')
3. Line ~561: ui.label(f'{VERSION}').classes('text-md text-gray-600 mb-4')
4. Line ~1000: self.output_text = f'MBASIC 5.21 Web IDE - {VERSION}\n'
5. Line ~1063: ui.page_title('MBASIC 5.21 - Web IDE')

The comment clarifies '5.21' is the language version and VERSION is the implementation version, but this distinction is not consistently documented throughout the file.

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

#### documentation_inconsistency

**Description:** Multiple comments reference 'ASR33 teletype' behavior for continuous scrolling output, but this historical context may not be clear to modern developers and could benefit from additional explanation.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comments at multiple locations reference 'ASR33 teletype' behavior:
- Line ~1845: "# Don't clear output - continuous scrolling like ASR33 teletype"
- Line ~2050: "# Note: Output is NOT cleared - continuous scrolling like ASR33 teletype"

While technically not an inconsistency, this historical reference may be unclear without additional context about why this design choice was made.

---

#### code_vs_comment

**Description:** Comment describes dual input mechanism but doesn't explain why both are needed or when each is used

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _handle_output_enter() method:

Comment says:
"Provide input to interpreter via TWO mechanisms (both may be needed depending on code path):
1. interpreter.provide_input() - Used when interpreter is waiting synchronously
   (checked via interpreter.state.input_prompt). Stores input for retrieval.
2. input_future.set_result() - Used when async code is waiting via asyncio.Future
   (see _get_input_async method). Only one path is active at a time, but we
   attempt both to ensure the waiting code receives input regardless of which path it used."

The comment claims "only one path is active at a time" but then says "we attempt both" - this is contradictory. If only one is active, why attempt both? The comment should clarify the actual execution flow or race condition being handled.

---

#### code_vs_comment

**Description:** Comment describes auto-numbering behavior that may not match implementation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _check_auto_number() method:

Comment says:
"Auto-numbers a line at most once per content state - tracks last snapshot to avoid
re-numbering lines while user is typing. However, if content changes significantly
(e.g., line edited after numbering, then un-numbered again), the line could be
re-numbered by this logic."

The comment describes a complex state tracking mechanism, but the actual code only checks:
- if i < len(old_lines) or len(lines) > len(old_lines)
- if not re.match(r'^\s*\d+', old_line)

This doesn't implement the "at most once per content state" guarantee described. The comment may be describing intended behavior rather than actual implementation.

---

#### code_vs_comment

**Description:** Comment about blank line preservation heuristic may not accurately describe behavior

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _remove_blank_lines() method:

Comment says:
"Remove blank lines from editor except the last line.

The last line is preserved even if blank to avoid removing it while the user
is actively typing on it. This is a heuristic that works well in practice but
may preserve some blank lines if the user edits earlier in the document."

The code preserves the last line unconditionally (if line.strip() or i == len(lines) - 1), but the comment's claim about "may preserve some blank lines if the user edits earlier" doesn't match the implementation - only the LAST line is preserved, not lines "earlier in the document".

---

#### code_vs_comment

**Description:** Comment describes _get_input behavior that relies on interpreter state transitions not shown in code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _get_input() method:

Comment says:
"Return empty string - signals interpreter to transition to 'waiting_for_input'
state (state transition happens in interpreter when it receives empty string
from input()). Execution pauses until _submit_input() calls provide_input()."

The comment references _submit_input() method which doesn't exist in this file - the actual method is _handle_output_enter(). Also, the comment describes interpreter state transitions that aren't visible in this code, making it unclear if the described behavior is actually implemented.

---

#### code_vs_comment

**Description:** Comment about sys.stderr.write usage doesn't match actual error handling pattern

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _sync_program_from_editor() method:

Comment says:
"Using sys.stderr.write directly (not log_web_error) to avoid dependency on logging
infrastructure during critical serialization path."

However, throughout the rest of the file, log_web_error is used extensively in exception handlers, including in other serialization-related methods like _serialize_runtime(). The comment suggests a special case for this method, but it's unclear why this particular error path needs to avoid the logging infrastructure when others don't.

---

#### code_vs_comment

**Description:** Docstring for stop() method says 'disconnecting all clients' but app.shutdown() behavior is not verified in code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring: 'Stop the web UI server and shut down NiceGUI app.

Calls app.shutdown() to terminate the NiceGUI application,
disconnecting all clients and stopping the web server.'

Code: app.shutdown()

The docstring makes specific claims about disconnecting clients, but there's no verification that app.shutdown() actually does this. This could be accurate or could be an assumption.

---

#### documentation_inconsistency

**Description:** Comment about Redis storage mentions 'load-balanced instances' but no documentation about actual load balancing setup

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Lines ~481-488 mention:
'Session state will be shared across load-balanced instances'
and
'Set NICEGUI_REDIS_URL to enable Redis storage for load balancing'

But there's no documentation about:
- How to actually set up load balancing
- What load balancer to use
- Whether NiceGUI supports this natively
- Any caveats or requirements

This could mislead users into thinking Redis alone enables load balancing.

---

#### code_vs_comment

**Description:** Comment says 'Create default DEF type map (all SINGLE precision)' but this is creating a new map each time, not using a default

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~447: '# Create default DEF type map (all SINGLE precision)'

Code creates a new dict:
def_type_map = {}
for letter in 'abcdefghijklmnopqrstuvwxyz':
    def_type_map[letter] = TypeInfo.SINGLE

The word 'default' is misleading - this is creating a fresh type map, not using a pre-existing default. Better wording would be 'Create DEF type map with all letters as SINGLE precision' or 'Initialize DEF type map'.

---

#### documentation_inconsistency

**Description:** FRE documentation has inconsistent 'See Also' references mixing statements and functions

**Affected files:**
- `docs/help/common/language/functions/fre.md`

**Details:**
In fre.md 'See Also' section includes:
- `[HELP SET](../statements/helpsetting.md)`
- `[LIMITS](../statements/limits.md)`
- `[NULL](../statements/null.md)`
- `[RANDOMIZE](../statements/randomize.md)`
- `[REM](../statements/rem.md)`
- `[SET (setting)](../statements/setsetting.md)`
- `[SHOW SETTINGS](../statements/showsettings.md)`
- `[TRON/TROFF](../statements/tron-troff.md)`
- `[WIDTH](../statements/width.md)`

Mixed with functions like INP, PEEK, INKEY$, USR, VARPTR. The grouping seems arbitrary and some references (like HELP SET, SET, SHOW SETTINGS) may not be standard MBASIC-80 commands.

---

#### documentation_inconsistency

**Description:** HEX$ function description mismatch between index and detail page

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/hex_dollar.md`

**Details:**
Index page says 'Number to hexadecimal' but detail page says 'Returns a string which represents the hexadecimal value of the decimal argument'. Both are correct but inconsistent in style - index uses brief descriptions while detail uses full sentences.

---

#### documentation_inconsistency

**Description:** OCT$ function description mismatch between index and detail page

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/oct_dollar.md`

**Details:**
Index page says 'Number to octal' but detail page says 'Returns a string which represents the octal value of the decimal argument'. Both are correct but inconsistent in style.

---

#### documentation_inconsistency

**Description:** Cross-reference descriptions are inconsistent

**Affected files:**
- `docs/help/common/language/functions/lof.md`
- `docs/help/common/language/functions/loc.md`

**Details:**
In LOF.md See Also section: 'LOC - Returns current file POSITION/record number (LOF returns total SIZE in bytes)'
In LOC.md See Also section: 'LOF - Returns the total file SIZE in bytes (LOC returns current POSITION/record number)'
Both say the same thing but with different emphasis/capitalization.

---

#### documentation_inconsistency

**Description:** Inconsistent error message formatting

**Affected files:**
- `docs/help/common/language/functions/instr.md`

**Details:**
INSTR.md note says: 'Note: If I=0 is specified, an "Illegal function call" error will occur.'
MID$.md note says: 'Note: If I=0 is specified, an "Illegal function call" error will occur.'
Both use quotes around the error message, but other documentation files may format error messages differently.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-reference formatting in See Also sections

**Affected files:**
- `docs/help/common/language/statements/delete.md`
- `docs/help/common/language/statements/edit.md`
- `docs/help/common/language/statements/list.md`

**Details:**
delete.md uses: `[RENUM](renum.md)` - Renumber program lines and update line references
edit.md uses: `[RENUM](renum.md)` - Renumber program lines and update line references
list.md uses: `[RENUM](renum.md)` - Renumber program lines and update line references

All three files reference RENUM consistently, but the formatting style varies across other statements. Some use full descriptions, others use brief ones.

---

#### documentation_inconsistency

**Description:** Inconsistent example output formatting

**Affected files:**
- `docs/help/common/language/statements/randomize.md`
- `docs/help/common/language/statements/read.md`

**Details:**
randomize.md shows example output with "Ok" prompt:
"RUN
Random Number Seed (-32768 to 32767)? 3
.88598 .484668 .586328 .119426 .709225
Ok"

read.md shows example output without "Ok" prompt:
"Output:
Student 100 John scored 85.5
Student 200 Mary scored 92.3"

Inconsistent formatting of example outputs across documentation makes it harder to understand what is actual program output vs interpreter prompts.

---

#### documentation_inconsistency

**Description:** Similar command names (RESTORE vs RESUME) with different purposes not cross-referenced

**Affected files:**
- `docs/help/common/language/statements/restore.md`
- `docs/help/common/language/statements/resume.md`

**Details:**
restore.md is about resetting DATA pointers for READ statements.
resume.md is about continuing execution after error handling.

These commands have similar names but completely different purposes. Neither document cross-references the other or includes a note warning about the name similarity, which could help prevent user confusion.

While not strictly required, a note like "Note: Do not confuse RESTORE with RESUME (error handling)" would be helpful.

---

#### documentation_inconsistency

**Description:** Different levels of detail in error handling documentation

**Affected files:**
- `docs/help/common/language/statements/resume.md`
- `docs/help/common/language/statements/on-error-goto.md`

**Details:**
resume.md provides extensive examples with 5 detailed scenarios, error code reference table, and testing notes: "Verified behavior against real MBASIC 5.21"

on-error-goto.md provides minimal example with basic error handling.

While RESUME is more complex and warrants more examples, the disparity in documentation depth is notable. The error code table in RESUME would be useful in ON ERROR GOTO as well.

---

#### documentation_inconsistency

**Description:** Inconsistent 'Versions' field values

**Affected files:**
- `docs/help/common/language/statements/rset.md`
- `docs/help/common/language/statements/swap.md`

**Details:**
rset.md shows 'Versions: Disk' while swap.md shows 'Versions: Extended, Disk'. Need to verify if RSET is available in Extended BASIC or only Disk BASIC.

---

#### documentation_inconsistency

**Description:** Menu item documentation contains unrendered template variable

**Affected files:**
- `docs/help/common/ui/tk/index.md`

**Details:**
In the Edit Menu section:
- **Select All** (Ctrl+A) - Select all text

This is the only shortcut with an actual key combination shown, while all others use template variables like {{kbd:cut:tk}}. This inconsistency suggests incomplete template rendering or documentation.

---

#### documentation_inconsistency

**Description:** Save shortcut explanation inconsistency

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
files.md states 'Press {{kbd:save:curses}} to save (Ctrl+S unavailable - terminal flow control)' suggesting {{kbd:save:curses}} is NOT Ctrl+S. However, feature-reference.md states 'Note: Uses {{kbd:save:curses}} because {{kbd:save:curses}} is reserved for terminal flow control' which is circular and confusing. The actual shortcut key is unclear.

---

#### documentation_inconsistency

**Description:** Inconsistent auto-numbering increment default values

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/settings.md`

**Details:**
getting-started.md states: "First line: Starts at 10 (configurable in Settings)"

settings.md states: "Line number increment (number input)
  - Range: 1-1000
  - Default: 10"

While both mention 10, getting-started.md refers to the 'starting line number' while settings.md refers to the 'increment'. These are different concepts - starting line vs increment between lines. The documentation conflates these two separate settings.

---

#### documentation_inconsistency

**Description:** Inconsistent game count in library

**Affected files:**
- `docs/help/ui/web/index.md`
- `docs/library/games/index.md`

**Details:**
index.md states: "Games Library - 113 classic CP/M era games to download and load!"

However, counting the games listed in docs/library/games/index.md shows exactly 113 games, which matches. But other library index files (business, data_management, demos, education, electronics, ham_radio) don't provide counts in their parent references.

This is actually consistent, but worth noting for completeness verification.

---

#### documentation_inconsistency

**Description:** Inconsistent Settings dialog access instructions

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/settings.md`

**Details:**
getting-started.md mentions: "Use the Settings dialog (⚙️ icon) to change the increment or disable auto-numbering entirely"

settings.md states: "Methods:
1. Click the ⚙️ Settings icon in the navigation bar
2. Click menu → Settings"

The first document only mentions the icon, while the second mentions both icon and menu. This is minor but creates incomplete information in getting-started.md.

---

#### documentation_inconsistency

**Description:** Duplicate calendar program references

**Affected files:**
- `docs/library/games/index.md`

**Details:**
The calendar.bas entry in games/index.md includes a note: "Note: A simpler calendar utility is also available in the `[Utilities Library](../utilities/index.md#calendar)`"

However, no utilities/index.md file is provided in the documentation files list, so this cross-reference cannot be verified. This may be a broken link or reference to non-existent documentation.

---

#### documentation_inconsistency

**Description:** Program categorization inconsistency - games in utilities

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
The utilities/index.md file includes two programs that appear to be games rather than utilities:

1. 'Million' - 'Millionaire life simulation game - make financial decisions to accumulate wealth' with tags 'simulation, financial, game'

2. 'Rotate' - 'Letter rotation puzzle game - order letters A-P by rotating groups clockwise' with tags 'puzzle, game, logic'

These are explicitly described as games but are listed in the Utilities category rather than the Games category.

---

#### documentation_inconsistency

**Description:** Placeholder syntax in documentation not explained

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`

**Details:**
The QUICK_REFERENCE.md uses placeholder syntax like {{kbd:new}}, {{kbd:open}}, {{kbd:save}}, {{kbd:run}}, {{kbd:help}}, {{kbd:quit}} throughout the document.

These appear to be template placeholders for actual keyboard shortcuts, but:
1. No explanation is provided for what these placeholders represent
2. The actual key bindings are not specified
3. Users cannot determine what keys to actually press

For example: '| {{kbd:new}} | New | Clear program, start fresh |'

This makes the quick reference unusable without knowing the actual key mappings.

---

#### documentation_inconsistency

**Description:** Duplicate installation documentation with redirect

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/INSTALLATION.md`

**Details:**
There are two installation documentation files:

1. docs/user/INSTALL.md - Contains the full installation guide
2. docs/user/INSTALLATION.md - A redirect file that says 'This is a redirect file. For complete installation instructions, see INSTALL.md'

While the redirect explains itself, having two files with similar names (INSTALL vs INSTALLATION) could cause confusion. The redirect file exists 'for compatibility with different documentation linking conventions' but this creates maintenance burden and potential for outdated links.

---

#### documentation_inconsistency

**Description:** Unclear program descriptions for xextract and xscan

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
Two utility programs have cryptic descriptions that don't explain their purpose:

1. Xextract: '0 -->END PAGE / 1-20 -->EXTRACT ITEM / 21 -->RESTART' with empty tags
2. Xscan: '0 -->END PAGE / 1-20 -->DELETE ITEM / 21 -->RESTART' with empty tags

These appear to be menu options or command descriptions rather than program descriptions. Users cannot determine what these programs actually do from these descriptions.

---

#### documentation_inconsistency

**Description:** TK_UI_QUICK_START.md references keyboard-shortcuts.md but that file only documents Curses UI shortcuts, not Tk shortcuts

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md states:
'### Learn More About...
- **Keyboard Shortcuts**: See `[Tk Keyboard Shortcuts](keyboard-shortcuts.md)`'

But keyboard-shortcuts.md title is '# MBASIC Curses UI Keyboard Shortcuts' and only documents Curses shortcuts

---

#### documentation_inconsistency

**Description:** UI_FEATURE_COMPARISON.md shows conflicting information about Save functionality

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
The table shows:
| **Save (interactive)** | ❌ | ✅ | ✅ | ✅ | Keyboard shortcut prompts for filename |
| **Save (command)** | ✅ | ✅ | ✅ | ✅ | SAVE "filename" command |

But later states:
'### Known Gaps
- CLI: No interactive save prompt (use SAVE "filename" command instead)'

This is redundant - the table already shows CLI has no interactive save

---

#### documentation_inconsistency

**Description:** Inconsistent reference to LINE INPUT# statement documentation

**Affected files:**
- `docs/user/sequential-files.md`

**Details:**
sequential-files.md references:
'`[LINE INPUT#](../help/common/language/statements/inputi.md)`'

The filename 'inputi.md' seems unusual - typically would expect 'line-input-hash.md' or similar. This may be correct but appears inconsistent with other statement naming like 'input_hash.md'

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut placeholder format

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md uses multiple formats:
- '**{{kbd:run_program}}**'
- '{{kbd:smart_insert}}'
- '**{{kbd:file_save}}**'

Some are bold, some are not, creating visual inconsistency

---

#### documentation_inconsistency

**Description:** Inconsistent status emoji usage

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md uses:
'**Status:** 🔧 PLANNED - Not yet implemented'

But the top-level status note uses:
'> **Status:** The settings system is implemented...'

without an emoji. Inconsistent formatting for status indicators

---

## Summary

- Total issues found: 682
- Code/Comment conflicts: 243
- Other inconsistencies: 439

---

