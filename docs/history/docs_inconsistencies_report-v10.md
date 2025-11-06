# Enhanced Consistency Report (Code + Documentation)

Generated: 2025-11-05 22:59:03
Analyzed: Source code (.py, .json) and Documentation (.md)

## 🔧 Code vs Comment Conflicts


## 📋 General Inconsistencies

### 🔴 High Severity

#### documentation_inconsistency

**Description:** Contradictory documentation about FileIO delegation to ProgramManager

**Affected files:**
- `src/editing/manager.py`
- `src/file_io.py`

**Details:**
src/editing/manager.py states:
"FileIO.load_file() delegates to ProgramManager methods after path resolution"

But src/file_io.py shows FileIO.load_file() returns a string:
"Returns:
    File contents as string"

And ProgramManager.load_from_file() expects a filename path:
"def load_from_file(self, filename: str) -> Tuple[bool, List[Tuple[int, str]]]"

The FileIO.load_file() returns raw file content (string), not delegating to ProgramManager. The caller must pass that content to ProgramManager separately.

---

#### code_vs_documentation

**Description:** SandboxedFileIO methods documented as STUB but implementation status unclear

**Affected files:**
- `src/file_io.py`

**Details:**
Documentation states:
"Implementation status:
- list_files(): IMPLEMENTED - delegates to backend.sandboxed_fs
- load_file(): STUB - raises IOError (requires async/await refactor)
- save_file(): STUB - raises IOError (requires async/await refactor)
- delete_file(): STUB - raises IOError (requires async/await refactor)
- file_exists(): STUB - returns False (requires async/await refactor)"

But the code shows:
- list_files() is fully implemented
- load_file() raises IOError with message about async
- save_file() raises IOError with message about async
- delete_file() raises IOError with message about async
- file_exists() returns False (not raising error)

The inconsistency: file_exists() is documented as STUB but silently returns False instead of raising an error like the other stubs. This could cause silent failures.

---

#### code_vs_comment

**Description:** Line editing feature has extensive documentation about UI integration requirements, but no validation that these requirements are met before attempting to use them

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The numbered line editing section has detailed comments:
"# This feature requires the following UI integration:
# - interpreter.interactive_mode must reference the UI object
# - UI must have a 'program' attribute with add_line() and delete_line() methods
# - UI must have _refresh_editor() method to update the display (optional)
# - UI must have _highlight_current_statement() for restoring execution highlighting (optional)
# If core requirements are not met, this will return an error message."

However, the code only validates some requirements:
"if not hasattr(ui, 'program') or not ui.program:
    return (False, "Cannot edit program lines: UI program manager not available\n")"

But it doesn't validate that interpreter.interactive_mode exists before using it (only checks 'if hasattr(self.interpreter, 'interactive_mode') and self.interpreter.interactive_mode'). The code also uses hasattr() checks for optional methods (_refresh_editor, _highlight_current_statement) but doesn't validate the 'core requirements' mentioned in comments before attempting operations.

---

#### code_vs_comment

**Description:** RENUM docstring describes ERL limitation incorrectly - says 'cannot distinguish' but code actively renumbers ALL binary ops with ERL

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_renum() docstring (line ~550):
"Known limitation: ERL expressions with binary operators (ERL+100, ERL*2) cannot
distinguish line number references from arithmetic constants, so all numbers on
the right side are conservatively renumbered."

In _renum_erl_comparison() docstring (line ~650):
"IMPORTANT: Current implementation renumbers for ANY binary operator with ERL on left,
including arithmetic (ERL + 100, ERL * 2). This is broader than the manual specifies."

And implementation comment:
"# Check if this is a binary operation
if type(expr).__name__ != 'BinaryOpNode':
    return"

The cmd_renum docstring frames this as a limitation ("cannot distinguish"), but _renum_erl_comparison shows it's an intentional conservative choice. The docstrings contradict each other on whether this is a bug or a feature.

---

#### code_vs_comment

**Description:** Comment says 'Clear execution state when program is cleared' but clear_execution_state() is not called in cmd_new()

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_new() at line ~350:
"def cmd_new(self):
    \"\"\"NEW - Clear program\"\"\"
    self.program.clear()
    self.current_file = None
    # Clear execution state when program is cleared
    self.clear_execution_state()
    print(\"Ready\")"

The comment says execution state is cleared, and the code does call clear_execution_state(). However, looking at the implementation of clear_execution_state() (line ~140), it only clears state if self.program_runtime exists:
"if self.program_runtime:
    self.program_runtime.gosub_stack.clear()
    ..."

But cmd_new() doesn't set self.program_runtime = None, so the runtime object persists with cleared stacks but still exists. The comment implies complete clearing but the implementation is partial.

---

#### code_vs_comment

**Description:** execute_for docstring claims string variables in FOR loops are 'technically allowed' but the implementation doesn't show any special handling for string type suffix

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring says: 'The loop variable can have any type suffix (%, $, !, #) and the variable type determines how values are stored, but the loop arithmetic always uses the evaluated numeric values. String variables in FOR loops are uncommon but technically allowed (though not meaningful).'

However, the code does: 'start = self.evaluate_expression(stmt.start_expr); end = self.evaluate_expression(stmt.end_expr); step = self.evaluate_expression(stmt.step_expr) if stmt.step_expr else 1'

Then: 'self.runtime.set_variable(stmt.variable.name, stmt.variable.type_suffix, start, ...)'

If stmt.variable.type_suffix is '$' (string), and start is a number, set_variable would likely fail or coerce incorrectly. The claim that string variables are 'technically allowed' is not supported by any visible error handling or type coercion logic in execute_for. This needs clarification on whether this is actually supported or if the comment is incorrect.

---

#### code_vs_comment

**Description:** WEND execution comment contradicts actual implementation regarding when loop is popped

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1069 states:
"# Pop the loop from the stack AFTER setting the jump target.
# The WHILE will re-push if the condition is still true, or skip the
# loop body if the condition is now false. This ensures clean stack state.
# Note: We pop here (before execution reaches WHILE) so that if an error occurs during
# WHILE condition evaluation, the loop is already popped (correct error handling behavior)."

The comment says "Pop the loop from the stack AFTER setting the jump target" but then immediately contradicts itself by saying "We pop here (before execution reaches WHILE)". The code pops AFTER setting npc but BEFORE the WHILE re-executes. The comment should be clarified to avoid this apparent contradiction.

---

#### code_vs_comment

**Description:** execute_cont() docstring claims Break sets halted=True but NOT stopped=True, but execute_stop() sets BOTH flags

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_cont() docstring states:
'Behavior distinction (MBASIC 5.21 compatibility):
- STOP statement: Sets runtime.stopped=True, allowing CONT to resume
- Break (Ctrl+C): Sets runtime.halted=True but NOT stopped=True, so CONT fails'

However, execute_stop() implementation shows:
self.runtime.stopped = True
self.runtime.stop_pc = self.runtime.npc
...
self.runtime.halted = True

This sets BOTH stopped=True AND halted=True, contradicting the docstring's claim that only stopped is set. Either the code is wrong (should not set halted), or the docstring is wrong (should say STOP sets both flags).

---

#### Code vs Comment conflict

**Description:** Comment claims file I/O keywords can be followed by # without space, but the code logic may not handle all cases correctly

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line 293-302:
"# Special case: File I/O keywords followed by # (e.g., PRINT#1)
# The # is NOT a type suffix here - it's part of the file I/O syntax.
# MBASIC allows 'PRINT#1' with no space, which should tokenize as:
#   PRINT (keyword) + # (operator) + 1 (number)
# Since we read 'PRINT#' as one identifier, we need to split it."

However, the code at line 303-314 only handles this case when ident_lower.endswith('#'). This means the identifier reading logic must have consumed the # character. But looking at read_identifier() at line 270-275, the # character is only consumed if it's at the end AND treated as a type suffix:
"elif char in ['$', '%', '!', '#']:
    # Type suffix - only allowed at end of identifier
    ident += self.advance()
    break"

This creates a contradiction: the comment says # is NOT a type suffix for file I/O keywords, but the code treats it as one during identifier reading, then tries to split it back out. The logic may work but is confusing.

---

#### code_vs_comment

**Description:** Comment about MBASIC 5.21 prompt behavior contradicts itself regarding semicolon behavior

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() method, there are two comments about semicolon behavior that appear contradictory:

Comment 1 (lines after prompt parsing):
"# Note: In MBASIC 5.21, the separator after the prompt string affects '?' display:
# - INPUT "Name"; X  displays "Name? " (semicolon shows '?')
# - INPUT "Name", X  displays "Name " (comma suppresses '?')"

Comment 2 (immediately after):
"# Additionally, INPUT; (semicolon immediately after INPUT keyword) can also
# suppress the '?' prompt, which is tracked by the suppress_question flag above."

These comments contradict each other:
- Comment 1 says semicolon after prompt SHOWS '?'
- Comment 2 says semicolon after INPUT keyword SUPPRESSES '?'

While these refer to different positions (after prompt vs after INPUT keyword), the contradiction in behavior (semicolon shows vs suppresses) without clear explanation of why the same punctuation has opposite effects in different positions could confuse readers.

---

#### Documentation inconsistency

**Description:** CLI STEP command documentation claims it implements statement-level stepping 'similar to the curses UI Step Statement command (Ctrl+T)', but the curses keybindings show Ctrl+K is for 'Step Line' and Ctrl+T is for 'Step statement'. The CLI documentation also states 'The curses UI also has a separate Step Line command (Ctrl+K) which is not available in the CLI', but this contradicts the claim that CLI STEP is similar to Ctrl+T (statement stepping).

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/curses_keybindings.json`

**Details:**
cli_debug.py docstring says:
"This implements statement-level stepping similar to the curses UI 'Step Statement'
command (Ctrl+T). The curses UI also has a separate 'Step Line' command (Ctrl+K)
which is not available in the CLI."

But curses_keybindings.json shows:
"step_line": {
  "keys": ["Ctrl+K"],
  "description": "Step Line (execute all statements on current line)"
}
"step": {
  "keys": ["Ctrl+T"],
  "description": "Step statement (execute one statement)"
}

The CLI STEP command claims to be like Ctrl+T (statement-level), which is correct, but the explanation about Ctrl+K being unavailable is confusing since Ctrl+K is the line-level stepping, not statement-level.

---

#### code_vs_comment

**Description:** Comment claims line numbers use fixed 5-character width, but code uses variable width

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring at line 149 states: "Note: This is NOT a true columnar layout with fixed column boundaries.
Line numbers use variable width for display (_format_line returns variable-width numbers).
However, when reformatting pasted content, _parse_line_numbers uses fixed 5-character width
for alignment consistency."

But _format_line() at line 449 uses: line_num_str = f"{line_num}" (variable width, no padding)

And _parse_line_numbers() at lines 991 and 1024 uses: line_num_formatted = f"{num_str:>5}" (fixed 5-char width)

This creates inconsistent formatting between display and paste handling.

---

#### code_vs_comment

**Description:** Comment claims variable width but code at line 1024 uses fixed 5-char padding

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring at line 149 claims: "Line numbers use variable width for display (_format_line returns variable-width numbers)."

But _parse_line_numbers() at line 1024 uses: line_num_formatted = f"{num_str:>5}"
new_line = f"{status}{line_num_formatted} {rest}"

This creates lines with fixed 5-character line number fields, contradicting the variable-width claim.

---

#### code_vs_comment

**Description:** Comment about statement-level precision for GOSUB contradicts default value handling

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_stack_window(), comment states:
"# Show statement-level precision for GOSUB return address
# Note: default of 0 if return_stmt is missing means first statement on line
return_stmt = entry.get('return_stmt', 0)
line = f"{indent}GOSUB from line {entry['from_line']}.{return_stmt}"

The comment says 'default of 0 if return_stmt is missing means first statement on line', but this is ambiguous. In many BASIC implementations, statement numbering starts at 0 (first statement), but the comment could be interpreted as 'line.0' being a special notation. The code doesn't validate whether return_stmt=0 is semantically correct or just a placeholder. This could lead to confusion about whether '.0' in the display means 'first statement' or 'unknown statement'.

---

#### code_inconsistency

**Description:** Duplicate CapturingIOHandler class definition in _execute_immediate() with comment acknowledging duplication but not fixing it

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate() around line ~1180:
# Need to create the CapturingIOHandler class inline
# (duplicates definition in _run_program - consider extracting to shared location)
class CapturingIOHandler:
    def __init__(self):
        self.output_buffer = []
        self.debug_enabled = False
    def output(self, text, end='\n'):
        ...

Comment explicitly states this duplicates definition in _run_program and should be extracted to shared location, but duplication remains.

---

#### code_vs_comment

**Description:** Comment claims tier detection logic for UI tier, but the actual implementation differs from description

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~110 states:
"# Map tier to labels for search result display
# Note: UI tier (e.g., 'ui/curses', 'ui/tk') is detected via startswith('ui/')
# check below and gets '📘 UI' label. Other unrecognized tiers get '📙 Other'."

The tier_labels dict only defines 'language' and 'mbasic' tiers. The code then checks:
if tier_name.startswith('ui/'):
    tier_label = '📘 UI'
else:
    tier_label = tier_labels.get(tier_name, '📙 Other')

This means 'language' and 'mbasic' get their specific labels, UI tiers get '📘 UI', but the comment suggests only unrecognized tiers get '📙 Other'. Actually, any tier not in tier_labels and not starting with 'ui/' gets '📙 Other'.

---

#### code_vs_comment

**Description:** Comment claims _on_enter_key is called 'after each keypress' but it's only called when Enter key is pressed

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1779:
Currently called only from _on_enter_key (after each keypress), not
after pasting or other modifications.

This is incorrect. _on_enter_key is only called when the Enter key is pressed, not after every keypress. The comment should say 'after each Enter keypress' or 'when Enter is pressed'.

---

#### code_vs_comment

**Description:** Comment in _update_immediate_status explains checking self.running to prevent race conditions, but the actual condition uses 'and not self.running' which would allow execution when running=False (opposite of prevention)

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1730 says:
'# We check self.running to prevent immediate mode execution during program execution,
# even if the tick hasn\'t completed yet. This prevents race conditions where immediate
# mode could execute while the program is still running but between tick cycles.'

Code at line ~1733:
can_execute = can_exec_immediate and not self.running

The logic is correct (prevents execution when running=True), but the comment's phrasing 'to prevent immediate mode execution during program execution' could be clearer. The comment describes the goal but doesn't clearly state that 'not self.running' achieves this by requiring running to be False.

---

#### code_vs_comment

**Description:** TkIOHandler.input() docstring claims it 'Prefers inline input field below output pane when backend is available, but falls back to modal dialog' - however LINE INPUT always uses modal dialog, creating inconsistent user experience not documented in class docstring

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler.input() docstring:
"Input from user via inline input field (with fallback to modal dialog).

Used by INPUT statement to read user input.

Returns the raw string entered by user. The interpreter handles parsing
of comma-separated values for INPUT statements with multiple variables.
Prefers inline input field below output pane when backend is available,
but falls back to modal dialog if backend is not available."

But TkIOHandler.input_line() docstring:
"Input complete line from user via modal dialog.

Used by LINE INPUT statement for reading entire line as string.
Unlike input() which prefers inline input field, this ALWAYS uses
a modal dialog regardless of backend availability."

The class-level docstring only mentions:
"IOHandler that routes output to Tk output pane.

This handler captures program output and sends it to the Tk UI's
output text widget via a callback function."

It doesn't explain the dual input strategy (inline vs modal) which is a significant design decision.

---

#### code_vs_comment

**Description:** _on_status_click() docstring says it shows 'breakpoint info for ●' but the actual behavior only shows a generic message, not actual breakpoint information

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring: 'Handle click on status column (show error for ?, breakpoint info for ●).'

Actual code for breakpoint:
messagebox.showinfo(
    f"Breakpoint on Line {line_num}",
    f"Line {line_num} has a breakpoint set.\n\nUse the debugger menu or commands to manage breakpoints."
)

This is just a confirmation message, not 'breakpoint info'. True breakpoint info would include details like condition, hit count, enabled/disabled state, etc.

---

#### code_vs_comment

**Description:** Step methods clear output but RUN doesn't - inconsistent initialization behavior

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
_menu_step_line (line ~2050) and _menu_step_stmt (line ~2100) both call:
  self._clear_output()
But _menu_run (line ~1799) has comment:
  # Don't clear output - continuous scrolling like ASR33 teletype
This creates inconsistent user experience: stepping clears output, but running doesn't.

---

#### code_vs_comment

**Description:** Comment says RUN clears variables 'like CLEAR statement' but doesn't reference what CLEAR does or if it exists

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1799 in _menu_run():
  "RUN clears variables (like CLEAR statement) and starts execution from first line."
But there's no CLEAR command implementation visible in this file, and no reference to where CLEAR is documented. The runtime.reset_for_run() call presumably does this, but the relationship to a CLEAR statement is unclear.

---

#### code_vs_comment

**Description:** Comment claims TWO mechanisms are needed for input, but explanation suggests redundancy or architectural confusion

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment in _handle_output_enter says: 'Provide input to interpreter via TWO mechanisms (both are needed): 1. interpreter.provide_input() - Primary path for synchronous interpreter (see _get_input method which returns empty and relies on state transitions) 2. input_future.set_result() - Secondary path for async compatibility (see _get_input_async method which uses asyncio.Future) This ensures both synchronous and async code paths work correctly.'

This suggests the architecture has both sync and async input paths that must be manually coordinated. If both are truly needed, it indicates a design issue. If only one is needed, the comment is misleading.

---

#### code_vs_documentation

**Description:** Help system URL mismatch - code points to http://localhost/mbasic_docs but documentation structure suggests docs/help/ directory

**Affected files:**
- `src/ui/web_help_launcher.py`
- `docs/help/README.md`
- `docs/help/common/index.md`

**Details:**
web_help_launcher.py defines:
HELP_BASE_URL = 'http://localhost/mbasic_docs'

But README.md describes help structure as:
- /common - Shared Help Content
- /ui/cli, /ui/curses, /ui/tk, /ui/web

The code assumes a web server at localhost serving mbasic_docs, but the documentation is in docs/help/ with no mention of how it gets served at that URL or how the web server is configured.

---

#### documentation_inconsistency

**Description:** Missing MKI$/MKS$/MKD$ functions in appendices index but referenced in CVI/CVS/CVD

**Affected files:**
- `docs/help/common/language/functions/cvi-cvs-cvd.md`
- `docs/help/common/language/appendices/index.md`

**Details:**
In cvi-cvs-cvd.md 'See Also' section:
'- [MKI$, MKS$, MKD$](mki_dollar-mks_dollar-mkd_dollar.md) - Convert numeric values to string values'

These functions are referenced but not listed in the appendices/index.md or functions overview. The inverse functions (MKI$/MKS$/MKD$) should be documented if CVI/CVS/CVD are documented.

---

#### documentation_inconsistency

**Description:** FIELD documentation warns against using FIELDed variables in INPUT/LET, but GET documentation suggests using INPUT# with random files after GET, which could conflict with FIELD variables.

**Affected files:**
- `docs/help/common/language/statements/field.md`
- `docs/help/common/language/statements/get.md`

**Details:**
FIELD.md: 'Do not use a FIELDed variable name in an INPUT or LET statement. Once a variable name is FIELDed, it points to the correct place in the random file buffer. If a subsequent INPUT or LET statement with that variable name is executed, the variable's pointer is moved to string space.'

GET.md: 'After a GET statement, INPUT# and LINE INPUT# may be used to read characters from the random file buffer.'

This could be confusing - using INPUT# after GET might interact with FIELDed variables in unexpected ways.

---

#### documentation_inconsistency

**Description:** LLIST documentation contains implementation note stating feature is not implemented, but still provides full documentation as if it works, creating confusion.

**Affected files:**
- `docs/help/common/language/statements/llist.md`

**Details:**
LLIST.md starts with:
'⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.\n\n**Behavior**: Statement is parsed but no listing is sent to a printer'

But then provides full syntax, purpose, remarks, and examples as if the feature works. This is inconsistent with how other unimplemented features might be documented.

---

#### documentation_inconsistency

**Description:** WIDTH documentation has conflicting implementation notes. It says 'Emulated as No-Op' and 'performs no operation' but also says 'Statement executes successfully without errors'. Then contradicts by saying 'WIDTH LPRINT syntax is not supported (parse error)'.

**Affected files:**
- `docs/help/common/language/statements/width.md`

**Details:**
width.md states:
'⚠️ **Emulated as No-Op**: This statement is parsed for compatibility but performs no operation.'
'**Behavior**: Statement executes successfully without errors'
But then:
'**Limitations**: The "WIDTH LPRINT" syntax is not supported (parse error).'
If it's a no-op that executes successfully, why would WIDTH LPRINT cause a parse error?

---

#### documentation_inconsistency

**Description:** SWAP documentation shows 'Versions: EXtended, Disk' with inconsistent capitalization of 'EXtended' (capital X in middle).

**Affected files:**
- `docs/help/common/language/statements/swap.md`

**Details:**
swap.md: '**Versions:** EXtended, Disk'
This appears to be a typo - should be 'Extended' not 'EXtended'.

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI filesystem persistence

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md states about Web UI: 'Files stored in Python-side memory (not browser localStorage)' and 'Files persist only during browser session - lost on page refresh'

However, extensions.md states about Web UI: 'Auto-save - Automatic saving to browser storage'

These statements contradict each other. If files are stored in Python-side memory and lost on page refresh, then 'automatic saving to browser storage' cannot be accurate. Either the Web UI saves to browser storage (localStorage/IndexedDB) or it doesn't.

---

#### documentation_inconsistency

**Description:** Conflicting information about STEP command variants

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
cli/debugging.md documents 'STEP INTO' and 'STEP OVER' commands with syntax examples:
```
STEP [n]               - Execute n statements (default: 1)
STEP INTO             - Step into subroutines
STEP OVER             - Step over subroutine calls
```
But then states 'STEP INTO/OVER not yet implemented (use STEP)' under Limitations.

Meanwhile, curses/feature-reference.md documents:
- 'Step Statement (Ctrl+T)' - Execute one BASIC statement
- 'Step Line (Ctrl+K)' - Execute the next line

These appear to be different stepping mechanisms with no clear relationship documented.

---

#### documentation_inconsistency

**Description:** Execution Stack access method unclear and potentially incorrect

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
The feature-reference.md states:
'Execution Stack (Menu only)
View the call stack showing:
- Active GOSUB calls
- FOR/NEXT loops
- WHILE loops

How to access:
1. Press Ctrl+U to open the menu bar
2. Navigate to the Debug menu
3. Select "Execution Stack" option

Note: There is no dedicated keyboard shortcut to avoid conflicts with editor typing.'

However, cli/debugging.md documents a 'STACK' command that does the same thing. It's unclear if Curses UI has both menu access AND a STACK command, or if this is a UI-specific difference that should be clarified.

---

#### documentation_inconsistency

**Description:** Contradictory information about save keyboard shortcut

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
files.md states: 'Press **^V** to save (Note: ^S unavailable due to terminal flow control)'

But quick-reference.md shows: '**^V** (Ctrl+V) | Save program (Ctrl+S unavailable - terminal flow control)'

However, the quick-reference also lists under 'Program Management': '**Ctrl+N** | New program' and '**^V** (Ctrl+V) | Save program'

This is inconsistent because ^V is typically Ctrl+V which is paste in most systems. The documentation should clarify if this is really Ctrl+V or if it's a different key combination.

---

#### documentation_inconsistency

**Description:** Execution stack window feature documentation mismatch

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md lists under 'Global Commands': '**Menu only** | Toggle execution stack window'

And under 'Debugger': '**Menu only** | Show/hide execution stack window'

But index.md does not mention an execution stack window feature at all in the Curses UI Guide section.

This feature appears to be documented in quick-reference but not in the main index or other guide pages.

---

#### documentation_inconsistency

**Description:** Feature comparison table in index.md is incomplete

**Affected files:**
- `docs/help/ui/index.md`
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
index.md comparison table shows:
'| Variables Window | ✓ | ✗ | ✓ | ✓ |'

But this doesn't capture the important distinction that:
- Curses: Variables window exists but cannot edit values (per curses/variables.md)
- Tk: Variables window exists and CAN edit values (per tk/feature-reference.md)

The comparison table should have a separate row for 'Edit Variables' or add a note about this limitation.

---

#### documentation_inconsistency

**Description:** Tk settings.md describes comprehensive settings dialog as 'planned/intended implementation and are not yet available', but web/settings.md is referenced multiple times without existing in the provided files

**Affected files:**
- `docs/help/ui/tk/settings.md`
- `docs/help/ui/web/settings.md`

**Details:**
tk/settings.md states: '**Implementation Status:** The Tk (Tkinter) desktop GUI is planned to provide the most comprehensive settings dialog. **The features described in this document represent planned/intended implementation and are not yet available.**'

Multiple files reference 'docs/help/ui/web/settings.md':
- web/getting-started.md: 'See [Settings](settings.md) for currently available settings'
- web/features.md: 'See [Settings](settings.md) for currently available settings'
- web/debugging.md: 'See [Settings](settings.md) for currently available settings'
- web/index.md: '[Settings & Configuration](settings.md) - Customize your experience'

But web/settings.md is not provided in the documentation files.

---

#### documentation_inconsistency

**Description:** Contradictory status of settings system implementation

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md header states: 'Status: The settings system is FULLY IMPLEMENTED and available in all UIs. All commands (SET, SHOW SETTINGS, HELP SET) work as documented.' However, the same document marks several settings as 'Status: 🔧 PLANNED - Not yet implemented' including interpreter.strict_mode, interpreter.debug_mode, ui.theme, and ui.font_size. This is contradictory - the system cannot be 'FULLY IMPLEMENTED' if multiple settings are 'Not yet implemented'.

---

### 🟡 Medium Severity

#### documentation_inconsistency

**Description:** Version mismatch between setup.py and documentation comments

**Affected files:**
- `setup.py`
- `src/ast_nodes.py`

**Details:**
setup.py declares version="0.99.0" with comment "Reflects ~99% implementation status (core complete)", but ast_nodes.py header says "Abstract Syntax Tree (AST) node definitions for MBASIC 5.21" without version info. The setup.py also says "MBASIC 5.21 Interpreter" in the docstring but uses version 0.99.0 for the package.

---

#### code_vs_comment_conflict

**Description:** LineNode docstring claims no source_text field but doesn't explain how text regeneration works

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring states:
"The AST is the single source of truth. Text is always regenerated from
the AST using token positions and formatting information.

Design note: This class intentionally does not have a source_text field to avoid
maintaining duplicate copies that could get out of sync with the AST during editing."

However, LineNode has no fields for "token positions and formatting information" - it only has line_number, statements, line_num, and column. The docstring describes a design that isn't reflected in the actual fields.

---

#### code_vs_comment_conflict

**Description:** TypeInfo class docstring describes it as wrapper but implementation suggests it's more than that

**Affected files:**
- `src/ast_nodes.py`

**Details:**
TypeInfo docstring states:
"This class wraps VarType with static helper methods. New code may use
VarType directly, but TypeInfo provides backwards compatibility and
convenient conversion utilities."

However, TypeInfo exposes VarType enum values as class attributes (INTEGER = VarType.INTEGER, etc.) which is more than just "wrapping" - it's creating an alternative interface. The comment about "backwards compatibility" suggests this is legacy code, but there's no indication of deprecation or migration path.

---

#### code_vs_comment

**Description:** Comment claims original_negative was captured before rounding at line 263, but that line is actually the rounding operation itself, not the capture

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 260: original_negative = value < 0
Line 263: rounded = round(value, precision)
Comment at line 267-270 says: "original_negative was captured before rounding (line 263)" but line 263 is the rounding operation. The capture happens at line 260.

---

#### code_vs_comment

**Description:** Comment claims identifiers bypass the identifier_table, but the table is still retrieved and could be used

**Affected files:**
- `src/case_string_handler.py`

**Details:**
Lines 51-57 comment: "# Identifiers always preserve their original case in display.
# Unlike keywords, which can be forced to a specific case policy,
# identifiers (variable/function names) retain their case as typed.
# This matches MBASIC 5.21 behavior where identifiers are case-insensitive
# for matching but preserve display case.
# Note: We bypass the identifier_table here since identifiers always return
# original_text. The table could be used in future for conflict detection."
However, line 58 returns original_text directly without using the table at all. The comment says 'bypass' but the code doesn't even retrieve the table for identifiers, making the 'could be used in future' note misleading about current implementation.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for filesystem abstractions

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py describes two abstractions:
"1. FileIO (this file) - Program management operations (LOAD/SAVE/FILES/KILL)"
"2. FileSystemProvider (src/filesystem/base.py) - Runtime file I/O (OPEN/CLOSE/INPUT#/PRINT#)"

But src/filesystem/base.py header says:
"This module handles RUNTIME file I/O (OPEN, CLOSE, INPUT#, PRINT# statements).
For PROGRAM file operations (FILES, LOAD, SAVE, MERGE commands), see src/file_io.py."

However, FileSystemProvider.list_files() and FileSystemProvider.delete() overlap with FileIO operations (FILES and KILL commands). The separation is not clean.

---

#### documentation_inconsistency

**Description:** Contradictory information about SandboxedFileIO storage location

**Affected files:**
- `src/file_io.py`

**Details:**
The docstring states:
"Storage location: Python server memory (NOT browser localStorage)."

But also states:
"Acts as an adapter to backend.sandboxed_fs (SandboxedFileSystemProvider from
src/filesystem/sandboxed_fs.py), which provides an in-memory virtual filesystem."

And the comment says:
"The stubs exist because ui.run_javascript() cannot be called from synchronous code."

This implies browser JavaScript interaction, which contradicts "NOT browser localStorage". If it's purely Python server memory via sandboxed_fs, why would ui.run_javascript() be needed?

---

#### documentation_inconsistency

**Description:** Unclear relationship between ProgramManager file methods and FileIO abstraction

**Affected files:**
- `src/editing/manager.py`

**Details:**
The documentation states:
"Why ProgramManager has its own file I/O methods:
- Provides simpler API for local UI menu operations (File > Open/Save dialogs)
- Only used by local UIs (CLI, Curses, Tk) where filesystem access is safe
- Separate from BASIC command flow: UI menus call ProgramManager directly,
  BASIC commands (LOAD/SAVE) go through FileIO abstraction first"

But ProgramManager.load_from_file() and FileIO.load_file() have different signatures:
- ProgramManager.load_from_file(filename: str) -> Tuple[bool, List[Tuple[int, str]]]
- FileIO.load_file(filename: str) -> str

How does FileIO delegate to ProgramManager if the return types are incompatible? The architecture description is unclear about the actual call flow.

---

#### code_vs_comment

**Description:** Comment claims INPUT is not allowed in immediate mode, but code only raises error when input() is called, not when INPUT statement is parsed

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In ImmediateExecutor._show_help(), the help text states:
"• INPUT statement is not allowed in immediate mode (use direct assignment instead)"

However, in OutputCapturingIOHandler.input():
"def input(self, prompt=""):
    '''Input not supported in immediate mode.'''
    raise RuntimeError("INPUT not allowed in immediate mode")"

The INPUT statement would be parsed and executed normally - it only fails when the interpreter tries to call io_handler.input(). The documentation implies INPUT statements are blocked at parse/execute time, but they're only blocked when the input() method is invoked.

---

#### code_vs_comment

**Description:** Comment describes saving/restoring PC, but code explicitly does NOT do this

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In execute() method, comment states:
"# Note: We do not save/restore the PC before/after execution.
# This allows statements like RUN to change execution position.
# Normal statements (PRINT, LET, etc.) don't modify PC anyway."

This comment is accurate and matches the code behavior. However, earlier versions may have saved/restored PC, and this comment serves as documentation of a deliberate design choice. This is actually consistent - marking as informational only.

---

#### code_vs_comment

**Description:** Help text claims multi-statement lines work but are not recommended, but no code prevents or warns about them

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Help text in _show_help() states:
"• Multi-statement lines (: separator) work but are not recommended"

The execute() method parses and executes all statements on line 0:
"for stmt in line_node.statements:
    interpreter.execute_statement(stmt)"

The code fully supports multi-statement lines with no warnings or restrictions. The 'not recommended' guidance is only in help text, but there's no technical reason given why they shouldn't be used. This may confuse users about whether the feature is supported or discouraged.

---

#### code_vs_comment

**Description:** Comment claims digits are silently ignored in EDIT mode, but code doesn't handle digits at all

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_edit() docstring:
"Note: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K) are not yet implemented.
Digits are silently ignored (not recognized as command prefixes or processed as commands)."

But in the actual edit loop (lines ~800-900), there is no code handling digit characters. If a user types a digit, it will fall through all the if/elif branches and do nothing (no output, no cursor movement). The comment suggests intentional handling, but the code just ignores them by omission.

---

#### code_vs_comment

**Description:** Comment says 'Error already contains line number' but the error format doesn't guarantee this

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_merge() at line ~420:
"# Error already contains line number (e.g., \"Syntax error in 2020: ...\"), don't duplicate
print(f\"?{error}\")"

But the error comes from program.merge_from_file() which returns errors from parse_single_line(). Looking at parse_single_line() (line ~120), it formats errors as:
"print(error)
if basic_line_num is not None:
    print(f\"  {line_text}\")"

The error format depends on how ProgramManager.merge_from_file formats errors. The comment assumes a specific format but doesn't verify it.

---

#### code_vs_comment

**Description:** CHAIN docstring says 'only pass COMMON variables (if defined)' but implementation has complex fallback logic

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_chain() docstring (line ~450):
"- Neither: only pass COMMON variables (if defined)"

But implementation (lines ~470-490) shows:
"elif self.program_runtime.common_vars:
    # Save only COMMON variables (in order)
    # Note: common_vars stores base names (e.g., \"i\"), but actual variables
    # may have type suffixes (e.g., \"i%\", \"i$\") based on DEF statements
    saved_variables = {}
    for var_name in self.program_runtime.common_vars:
        # Try to find the variable with type suffix
        # Check all possible type suffixes: %, $, !, #
        found = False
        for suffix in ['%', '$', '!', '#', '']:
            full_name = var_name + suffix
            if self.program_runtime.variable_exists(full_name):
                saved_variables[full_name] = self.program_runtime.get_variable_raw(full_name)
                found = True
                break
        # If not found with any suffix, the variable might not have been initialized
        # That's okay - we just skip it"

The docstring oversimplifies the complex type suffix resolution logic.

---

#### code_vs_comment_conflict

**Description:** Comment claims GOTO/GOSUB in immediate mode will have PC changes reverted, but the code shows the jump executes and runs code during execute_statement(), which contradicts the claim that they are 'discouraged' if they actually work fully

**Affected files:**
- `src/interactive.py`

**Details:**
Comment says: 'Note: GOTO/GOSUB in immediate mode are discouraged (see help text) because they can be confusing, but if used, they execute and jump to program lines during statement execution. However, we restore the original PC afterward to preserve CONT functionality for stopped programs.'

The comment explains that GOTO/GOSUB DO execute and jump during execute_statement(), but then the PC is restored. This means the jump happens and code runs, making them functionally work, which contradicts calling them 'discouraged' - they're not broken, just the final PC position is reverted.

---

#### code_vs_comment

**Description:** InterpreterState docstring describes checking order for UI code examining completed state, but the actual tick_pc() implementation uses a different checking order during execution

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring says: 'Note: The suggested checking order below is for UI code that examines state AFTER execution completes. During execution (in tick_pc()), the actual checking order is: 1. pause_requested, 2. halted, 3. break_requested, 4. breakpoints, 5. input_prompt, 6. errors (handled via exceptions). For UI/callers checking completed state: - error_info: Non-None if an error occurred (highest priority for display) - input_prompt: Non-None if waiting for input (blocks until user provides input) - runtime.halted: True if stopped (paused/done/at breakpoint)'

But tick_pc() code checks in order: 1. pause_requested, 2. halted (pc.halted() or runtime.halted), 3. break_requested, 4. breakpoints, 5. trace output, 6. statement execution (errors via exceptions), 7. input_prompt check AFTER execution.

The docstring suggests input_prompt is checked during execution flow, but the code only checks it AFTER statement execution completes.

---

#### code_vs_comment

**Description:** Comment in execute_return describes return_stmt validation logic that contradicts the actual validation check

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: 'return_stmt is 0-indexed offset into statements array. Valid range: 0 to len(statements) (inclusive). - 0 to len(statements)-1: Normal statement positions - len(statements): Special sentinel meaning "GOSUB was last statement, continue at next line" Values > len(statements) indicate the statement was deleted (validation error).'

But the validation code checks: 'if return_stmt > len(line_statements):' with comment 'Check for strictly greater than (== len is OK)'

This means return_stmt == len(statements) is considered VALID (the special sentinel case), but return_stmt > len(statements) is invalid. However, the comment description doesn't clearly explain why len(statements) is a valid sentinel value or what it means in practice. The code is correct but the comment could be clearer about this edge case.

---

#### code_vs_comment

**Description:** execute_next docstring describes left-to-right processing behavior but doesn't mention the early return optimization that skips remaining variables

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring says: 'NEXT I, J, K processes variables left-to-right: I first, then J, then K. If any loop continues (not finished), execution jumps back to the loop body and remaining variables are not processed. This differs from separate statements (NEXT I: NEXT J: NEXT K) which would always execute sequentially.'

The code implements this with: 'should_continue = self._execute_next_single(var_name, var_node=var_node); if should_continue: return'

However, the docstring doesn't clearly explain what 'should_continue' means or that _execute_next_single returns True when jumping back to FOR. The relationship between 'loop continues' and 'should_continue' return value is not documented in the docstring.

---

#### code_vs_comment

**Description:** Comment claims RESUME 0 and RESUME (None) are treated identically, but parser creates different AST representations

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1090 states:
"# RESUME or RESUME 0 - retry the statement that caused the error
# Note: Parser creates different AST representations (None vs 0) to preserve
# the original source syntax for round-trip serialization, but the interpreter
# treats both identically at runtime (both retry the error statement)."

Code at line ~1091:
if stmt.line_number is None or stmt.line_number == 0:

This is consistent, but the comment's claim about "round-trip serialization" suggests the parser preserves the distinction for a reason beyond what the interpreter needs. The comment should clarify whether this distinction matters for any other component.

---

#### code_vs_comment

**Description:** CLEAR statement comment claims files are preserved for CHAIN but code explicitly clears them

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1234 states:
"# Note: Preserved state for CHAIN compatibility:
#   - runtime.common_vars (list of COMMON variable names - the list itself, not variable values)
#   - runtime.user_functions (DEF FN functions)
# Note: Files and field_buffers are NOT preserved (cleared above)."

However, the preceding code at lines ~1224-1232 explicitly closes and clears all files:
for file_num in list(self.runtime.files.keys()):
    try:
        file_obj = self.runtime.files[file_num]
        if hasattr(file_obj, 'close'):
            file_obj.close()
    except:
        pass
self.runtime.files.clear()
self.runtime.field_buffers.clear()

The comment correctly states files are NOT preserved, but the phrasing "Preserved state for CHAIN compatibility" followed by "Files and field_buffers are NOT preserved" is confusing. It should clearly separate what IS preserved from what is NOT preserved.

---

#### code_vs_comment

**Description:** File encoding comment claims latin-1 for round-trip preservation but doesn't mention actual CP/M code page issues

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1378 states:
"Encoding:
Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
Unicode U+0000-U+00FF, allowing round-trip byte preservation.
Note: Files using non-English code pages (other than standard ASCII/latin-1)
may require conversion before reading for accurate character display."

The comment acknowledges code page issues but doesn't explain that CP/M systems often used different code pages (like CP437, CP850) for characters 128-255, which would NOT match latin-1. The comment should clarify that latin-1 preserves BYTES but not necessarily CHARACTER MEANING for non-ASCII text from CP/M systems.

---

#### code_vs_comment

**Description:** RUN statement comment claims inline execution for non-interactive context but doesn't handle halted state correctly

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1545 states:
"# In non-interactive context (running program), do inline
self.runtime.clear_variables()
# Set NPC to target line (like GOTO)
# On next tick(), NPC will be moved to PC
self.runtime.npc = PC.from_line(line_num)
self.runtime.halted = False"

However, for RUN without arguments (line ~1554), the code sets:
self.runtime.halted = True

This is inconsistent - RUN with a line number sets halted=False (to continue execution), but RUN without arguments sets halted=True (to stop execution). The comment should explain this difference, as it's not obvious why restarting from the beginning would halt execution.

---

#### code_vs_comment

**Description:** RESET statement comment contradicts CLEAR statement regarding error handling during file close

**Affected files:**
- `src/interpreter.py`

**Details:**
CLEAR statement at line ~1224 has:
try:
    file_obj = self.runtime.files[file_num]
    if hasattr(file_obj, 'close'):
        file_obj.close()
except:
    pass

With comment at line ~1230: "# Note: Errors during file close are silently ignored (bare except: pass below)"

But RESET statement at line ~1757 has:
for file_num in list(self.runtime.files.keys()):
    self.runtime.files[file_num]['handle'].close()
    del self.runtime.files[file_num]

With comment at line ~1754: "# Note: Unlike CLEAR, RESET doesn't catch file close errors - they propagate to caller"

This is intentional different behavior, but it's not documented in the docstrings. Users might expect consistent error handling between CLEAR and RESET.

---

#### code_vs_comment

**Description:** Comment claims RSET truncates from the left when value is longer than width, but code truncates from the right

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_rset(), comment says 'Right-justify and pad/truncate to width' but the code does:
value = value[:width]
This truncates from the LEFT (keeps first 'width' characters), not from the right. For right-justification, when truncating a too-long string, it should keep the rightmost characters: value = value[-width:] or value = value[len(value)-width:]

---

#### code_vs_comment

**Description:** execute_step() docstring claims tick() supports step modes, but implementation shows stepping is not functional

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring states:
'Status: The tick() method supports step_statement and step_line modes, but this immediate STEP command is not yet connected to that infrastructure.'

However, the actual implementation is:
self.io.output(f"STEP {count} - Debug stepping not fully implemented")

This creates confusion about whether tick() actually has working step support or not. If tick() has the infrastructure, the comment should clarify what's missing. If tick() doesn't have it, the comment is misleading.

---

#### Code vs Documentation inconsistency

**Description:** input_line() documented to preserve leading/trailing spaces but implementations explicitly state they cannot

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/console.py`
- `src/iohandler/curses_io.py`
- `src/iohandler/web_io.py`

**Details:**
base.py docstring: "Intended behavior: Preserve leading/trailing spaces and not interpret commas as field separators (for MBASIC LINE INPUT compatibility)."

But then states: "Known limitation: Current implementations (console, curses, web) do NOT fully preserve leading/trailing spaces due to underlying platform limitations"

All three implementations (console.py, curses_io.py, web_io.py) include notes confirming they cannot preserve spaces. This creates confusion about whether this is a bug or accepted limitation.

---

#### Code vs Documentation inconsistency

**Description:** get_char() backward compatibility alias always uses non-blocking mode but comment doesn't explain why

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py get_char() method:
"def get_char(self):
    '''Deprecated: Use input_char() instead.
    
    This is a backward compatibility alias. New code should use input_char().
    Note: Always calls input_char(blocking=False) for non-blocking behavior.
    '''
    return self.input_char(blocking=False)"

The comment states it "Always calls input_char(blocking=False)" but doesn't explain:
1. Why it forces non-blocking when input_char() supports both modes
2. Whether old code using get_char() expected blocking or non-blocking behavior
3. If this could break backward compatibility for code expecting blocking behavior

---

#### Code vs Comment conflict

**Description:** Comment claims lexer uses SimpleKeywordCase for 'force-based policies' only, but the code actually accepts any policy string from settings without validation

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line 13-27 states:
"The lexer uses SimpleKeywordCase which supports force-based case policies:
- force_lower: Convert all keywords to lowercase
- force_upper: Convert all keywords to UPPERCASE
- force_capitalize: Convert all keywords to Capitalized form"

However, create_keyword_case_manager() at line 36 passes any policy from settings directly:
policy = get("keywords.case_style", "force_lower")
return SimpleKeywordCase(policy=policy)

No validation ensures only force_lower/force_upper/force_capitalize are used. If settings contains 'first_wins', 'preserve', or 'error', it would be passed to SimpleKeywordCase without error.

---

#### Documentation inconsistency

**Description:** Inconsistent documentation about which class handles which keyword case policies across multiple comments

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line 13-27 in create_keyword_case_manager():
"The lexer uses SimpleKeywordCase which supports force-based case policies:
- force_lower: Convert all keywords to lowercase
- force_upper: Convert all keywords to UPPERCASE
- force_capitalize: Convert all keywords to Capitalized form

Note: A separate KeywordCaseManager class exists (src/keyword_case_manager.py)
that provides additional advanced policies (first_wins, preserve, error) using
CaseKeeperTable for tracking case conflicts across the codebase."

Comment at line 96-103 in __init__():
"# Keyword case handler - uses SimpleKeywordCase for force-based policies:
# force_lower, force_upper, force_capitalize (simple case conversion)
#
# Note: The separate KeywordCaseManager class (src/keyword_case_manager.py) is used by
# parser/position_serializer for advanced policies (first_wins, preserve, error) that
# require tracking case conflicts via CaseKeeperTable."

These comments repeat the same information, creating maintenance burden. If the policy list changes, both locations need updating.

---

#### Code vs Comment conflict

**Description:** Comment about handling old BASIC contradicts implementation approach

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line 316-318:
"# NOTE: We do NOT handle old BASIC where keywords run together (NEXTI, FORI).
# This is properly-formed MBASIC 5.21 which requires spaces.
# Old BASIC files should be preprocessed with conversion scripts."

However, the code at line 303-314 DOES handle a special case of keywords running together (PRINT# without space). This is inconsistent with the claim that old BASIC syntax should be preprocessed. Either the lexer handles some old syntax or it doesn't.

---

#### Code vs Comment conflict

**Description:** Comment about identifier normalization contradicts token handling

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line 320-322:
"# Otherwise it's an identifier
# Normalize to lowercase (BASIC is case-insensitive) but preserve original case
token = Token(TokenType.IDENTIFIER, ident.lower(), start_line, start_column)"

The comment says 'Normalize to lowercase' and the code does ident.lower(), but then at line 323:
"token.original_case = ident  # Preserve original case for display"

For keywords, the code uses a different approach at line 287-289:
"display_case = self.keyword_case_manager.register_keyword(ident_lower, ident, start_line, start_column)
token.original_case_keyword = display_case  # Use policy-determined case"

The inconsistency is that identifiers preserve the original case in original_case, but keywords use policy-determined case in original_case_keyword. The comment doesn't explain why these are handled differently.

---

#### code_vs_comment

**Description:** Comment claims RND and INKEY$ can be called without parentheses as 'standard BASIC', but this is actually MBASIC-specific behavior, not universal BASIC standard

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line 11-12 states:
"- Exception: RND and INKEY$ can be called without parentheses (standard BASIC)"

However, this is MBASIC 5.21 specific behavior. Many BASIC dialects (like BBC BASIC, True BASIC) require parentheses for all functions. The comment should clarify this is MBASIC behavior, not a universal BASIC standard.

---

#### code_vs_comment

**Description:** parse_print() comment claims comma after file number is 'technically optional', but code behavior doesn't match this description

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1009-1013:
"# Optionally consume comma after file number
# Note: MBASIC 5.21 typically uses comma (PRINT #1, "text"), but comma is
# technically optional. Our parser accepts comma or no separator.
# If semicolon appears instead, it will be treated as an item separator
# in the expression list below (not as a file number separator)."

The code does consume comma if present, but the comment's claim that 'comma is technically optional' and 'semicolon will be treated as item separator' suggests ambiguous parsing. If PRINT #1;"text" is valid, the semicolon would be consumed as an item separator in the expressions list, which could lead to confusion. The comment should clarify whether MBASIC 5.21 actually allows this syntax or if this is a parser extension.

---

#### code_vs_comment

**Description:** Comment about MID$ statement detection describes complex lookahead logic that may not handle all edge cases correctly

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~560-565:
"# MID$ statement (substring assignment)
# Detect MID$ used as statement: MID$(var, start, len) = value
...
# Complex lookahead: scan past parentheses (tracking depth) to find = sign"

The lookahead logic tries to distinguish MID$ statement from MID$ function by scanning for '=' after matching parentheses. However, this could fail for nested function calls like:
MID$(A$, FN(X), 2) = "Y"

The comment acknowledges this is 'complex' but doesn't mention potential failure cases or limitations.

---

#### code_vs_comment

**Description:** Comment describes 'pattern' field but code uses 'pattern' parameter name inconsistently with docstring

**Affected files:**
- `src/parser.py`

**Details:**
In parse_showsettings() method:

Docstring says:
"Args:
    pattern: Optional string expression to filter which settings to display"

Comment in return statement says:
"pattern=pattern_expr,  # Field name: 'pattern' (optional filter string)"

But the actual parameter in the docstring is named 'pattern' while the variable is 'pattern_expr'. The comment clarifies the field name is 'pattern', which matches the AST node field, but the docstring Args section should document the AST node field name, not a local variable name.

---

#### code_vs_comment

**Description:** Comment describes MID$ tokenization but doesn't match the token name used

**Affected files:**
- `src/parser.py`

**Details:**
In parse_mid_assignment() method:

Comment says:
"Note: The lexer tokenizes 'MID$' in source as a single MID token (the $ is part
of the keyword, not a separate token)."

And in the code:
"token = self.current()  # MID token (represents 'MID$' from source)"

However, the method is called parse_mid_assignment() and the comment emphasizes that the lexer creates a 'MID token' (not MID$ token). This is correct behavior, but the emphasis on '$ is part of the keyword' might be misleading since the token itself is just 'MID'. The comment should clarify that the $ is consumed during lexing and the resulting token is TokenType.MID.

---

#### code_vs_comment

**Description:** Incomplete docstring in parse_deffn() - cut off mid-sentence

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deffn() method, the code ends abruptly:

"type_suffix = self.get_type_suffix(raw_name)
if type_suffix:"

The method implementation is incomplete - there's no code after the 'if type_suffix:' line, and the docstring example shows the function should handle type suffixes (e.g., 'FNA$'). This appears to be truncated source code rather than a documentation inconsistency, but it means the documented behavior (handling functions with type suffixes like FNA$) is not fully implemented in the visible code.

---

#### code_vs_comment

**Description:** CALL statement docstring claims MBASIC 5.21 only supports numeric address syntax, but code fully implements extended syntax with arguments

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"MBASIC 5.21 syntax:
    CALL address           - Call machine code at numeric address

Extended syntax (also supported for compatibility with other BASIC dialects):
    CALL ROUTINE(X,Y)      - Call with arguments

Both forms are fully supported by this parser."

This is contradictory - it first claims MBASIC 5.21 only supports 'CALL address', then says extended syntax is for 'other BASIC dialects', but then says 'Both forms are fully supported'. The implementation fully supports both forms without any dialect distinction.

---

#### code_vs_comment

**Description:** COMMON statement comment says 'no subscripts are specified or stored' but code checks for and consumes parentheses

**Affected files:**
- `src/parser.py`

**Details:**
Comment says:
"The empty parentheses () indicate an array variable (all elements shared).
This is just a marker - no subscripts are specified or stored."

Code does:
if self.match(TokenType.LPAREN):
    self.advance()
    if not self.match(TokenType.RPAREN):
        raise ParseError("Expected ) after ( in COMMON array", self.current())
    self.advance()

The error message 'Expected ) after ( in COMMON array' suggests it expects empty parens only, which matches the comment. However, the comment could be clearer that non-empty parens are an error.

---

#### code_vs_comment

**Description:** PC class docstring describes stmt_offset as both 'offset' and 'index' interchangeably, but the implementation and usage throughout the code treats it strictly as a 0-based index into a list

**Affected files:**
- `src/pc.py`

**Details:**
Docstring says: 'The stmt_offset is a 0-based index into the statements list for a line... Note: stmt_offset is both an "offset from beginning" and an "index position". These terms are equivalent for 0-based indexing (offset=0 is index=0).'

However, in position_serializer.py renumber_with_spacing_preservation(), the code uses enumerate() which produces indices: 'for stmt_offset, stmt in enumerate(line_node.statements)'

The term 'offset' typically implies a distance/displacement, while 'index' implies a position in a sequence. The code consistently uses it as an index.

---

#### documentation_inconsistency

**Description:** PC module describes statement identification as (line_number, statement_offset) but position_serializer uses different terminology when building PCs

**Affected files:**
- `src/pc.py`
- `src/position_serializer.py`

**Details:**
In pc.py PC class:
'PC identifies a statement by (line_number, statement_offset)'
'PC(10, 2)  - Third statement on line 10 (stmt_offset=2)'

In position_serializer.py replace_line():
'for stmt_offset, stmt in enumerate(line_node.statements):'
'    pc = PC(line_num, stmt_offset)'

The terminology is consistent (stmt_offset), but the PC module emphasizes it as an 'offset' while the implementation treats it as an enumeration index. The documentation could be clearer that stmt_offset is simply the list index.

---

#### code_vs_comment

**Description:** renumber_with_spacing_preservation() docstring says 'caller must call position_serializer separately' but doesn't explain what the caller should do with the returned AST

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring: 'Text can then be regenerated from updated AST using position_serializer (caller must call position_serializer separately)'

The function returns 'Dict of new_line_number -> LineNode (with updated positions)' but doesn't document that the caller needs to:
1. Call serialize_line() on each LineNode to get text
2. Handle the returned PositionConflict list

This is incomplete documentation rather than a conflict, but could lead to incorrect usage.

---

#### code_vs_comment

**Description:** Comment describes DIM A(N) creating N+1 elements but this is implementation detail not verified in this module

**Affected files:**
- `src/resource_limits.py`

**Details:**
Line 169 comment:
    total_elements *= (dim_size + 1)  # +1 because DIM A(N) creates N+1 elements (0 to N)

This module calculates array sizes based on this assumption, but the actual array creation logic is elsewhere. If the interpreter doesn't actually create N+1 elements, the memory calculations would be wrong.

---

#### code_vs_comment

**Description:** Comment in _variables documentation states line -1 indicates 'non-program execution sources' with two categories, but the implementation and set_variable_raw() docstring show three distinct sources using line=-1

**Affected files:**
- `src/runtime.py`

**Details:**
Comment in __init__ says:
'Note: line -1 in last_write indicates non-program execution sources:
       1. System/internal variables (ERR%, ERL%) via set_variable_raw() with FakeToken(line=-1)
       2. Debugger/interactive prompt via set_variable() with debugger_set=True and token.line=-1'

But set_variable_raw() docstring says:
'The line=-1 marker in last_write distinguishes system variables from:
- Normal program execution (line >= 0)
- Debugger sets (also use line=-1, but via debugger_set=True)'

This implies both system/internal variables AND debugger sets use line=-1, making them indistinguishable in last_write tracking. The comment lists them as separate categories but they share the same marker.

---

#### code_vs_comment

**Description:** The _resolve_variable_name() docstring says it's 'the standard method' but then set_variable_raw() docstring says 'For special cases like system variables' suggesting _resolve_variable_name shouldn't be used for system variables, creating confusion about when to use which method

**Affected files:**
- `src/runtime.py`

**Details:**
_resolve_variable_name() docstring:
'This is the standard method for determining the storage key for a variable,
applying BASIC type resolution rules (explicit suffix > DEF type > default).
For special cases like system variables (ERR%, ERL%), see set_variable_raw().'

set_variable_raw() docstring:
'Set variable by full name (e.g., 'err%', 'erl%').
Convenience wrapper for system/internal variable updates (ERR%, ERL%, etc.).
Internally calls set_variable() with a FakeToken(line=-1)...'

The guidance is unclear: _resolve_variable_name says 'see set_variable_raw for system variables' but set_variable_raw internally uses set_variable which would call _resolve_variable_name. The distinction between 'standard' and 'special case' paths is muddled.

---

#### code_vs_comment

**Description:** The _check_case_conflict() method's handling of debugger_set in set_variable() is inconsistent - the method is called with token parameter but debugger_set=True means token can be None, yet _check_case_conflict expects a token

**Affected files:**
- `src/runtime.py`

**Details:**
In set_variable():
if not debugger_set:
    if original_case is None:
        original_case = name
    canonical_case = self._check_case_conflict(name, original_case, token, settings_manager)
else:
    canonical_case = original_case or name

The code skips _check_case_conflict when debugger_set=True, but the ValueError check earlier says 'token is None and not debugger_set' is an error. This means when debugger_set=True, token CAN be None, but _check_case_conflict requires a token. The code correctly avoids calling _check_case_conflict when debugger_set=True, but there's no comment explaining why case conflict checking is skipped for debugger sets.

---

#### code_vs_comment

**Description:** Docstring for get_execution_stack() contains misleading documentation about 'from_line' field

**Affected files:**
- `src/runtime.py`

**Details:**
Docstring states:
"'from_line': 60,      # DEPRECATED: Same as return_line (kept for compatibility)"
and
"Note: 'from_line' is misleading and redundant with 'return_line'.
       Both contain the line number to return to (not where GOSUB was called from)."

However, the implementation shows:
'from_line': entry.get('return_line', 0),  # Line to return to

The comment says 'Line to return to' which is correct, but the docstring's extensive explanation about it being 'misleading' creates confusion. The field name 'from_line' naturally suggests 'where we came from' but actually stores 'where to return to', making the docstring's warning valid but potentially confusing.

---

#### code_vs_comment

**Description:** Comment in get_variables_and_arrays() about parse_name() behavior doesn't match typical BASIC convention

**Affected files:**
- `src/runtime.py`

**Details:**
The parse_name() function has this code:
else:
    # No suffix - assume single precision
    return full_name, '!'

The comment says 'assume single precision' and returns '!' for variables without a type suffix. However, in many BASIC dialects, variables without a suffix are actually treated as having their type determined by DEFINT/DEFSNG/DEFDBL statements, not always defaulting to single precision. The comment may be oversimplifying the actual behavior, though without seeing the full variable handling code, it's unclear if this is truly incorrect or just a simplified explanation.

---

#### Documentation inconsistency

**Description:** Inconsistent documentation about file-level settings implementation status

**Affected files:**
- `src/settings.py`
- `src/settings_definitions.py`

**Details:**
src/settings.py docstring says: 'Note: File-level settings (per-file overrides) are defined in the data structures but not yet fully implemented. The file_settings dict exists and can be set/queried, but there is no UI or command to manage per-file settings yet.'

However, src/settings_definitions.py defines SettingScope.FILE = 'file' with comment '# Per-file metadata' but provides no settings that actually use FILE scope. All defined settings use GLOBAL or PROJECT scope only.

The get() method in settings.py checks file_settings first in precedence, and set() method accepts SettingScope.FILE, but there are no actual file-scoped settings defined in SETTING_DEFINITIONS.

---

#### Code vs Comment conflict

**Description:** Token class docstring describes mutually exclusive fields but implementation allows both to be set

**Affected files:**
- `src/tokens.py`

**Details:**
Token class docstring states:
'original_case: Original case for user-defined identifiers (variable names) before normalization. Only set for IDENTIFIER tokens. Example: "myVar" stored here, "myvar" in value.
original_case_keyword: Original case for keywords, determined by keyword case policy. Only set for keyword tokens (PRINT, IF, GOTO, etc.). Used by serializer to output keywords with consistent or preserved case style.

Note: These fields serve different purposes and are mutually exclusive'

However, the Token dataclass definition allows both fields to be set simultaneously with no enforcement:
@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    original_case: Any = None
    original_case_keyword: str = None

There is no validation to ensure mutual exclusivity. The __repr__ method even handles displaying both if both are set.

---

#### Code vs Documentation inconsistency

**Description:** CLIBackend imports and uses modules not provided in source listing

**Affected files:**
- `src/ui/cli.py`

**Details:**
src/ui/cli.py imports:
from interactive import InteractiveMode
from .cli_debug import add_debug_commands

Neither 'interactive.py' nor 'cli_debug.py' are provided in the source code listing. The CLIBackend class depends on these modules but they are not documented or included, making it impossible to verify the implementation is consistent with the interface.

---

#### Code vs Comment conflict

**Description:** The _execute_single_step() method's docstring claims it executes 'a single statement' and that the interpreter's tick()/execute_next() methods are 'expected to advance the program counter by one statement', but then contradicts itself by noting 'If the interpreter executes full lines instead, this method will behave as line-level stepping rather than statement-level.' This uncertainty undermines the confident claims made in cmd_step() docstring.

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
_execute_single_step() docstring:
"Execute a single statement (not a full line).

Uses the interpreter's tick() or execute_next() method to execute
one statement at the current program counter position.

Note: The actual statement-level granularity depends on the interpreter's
implementation of tick()/execute_next(). These methods are expected to
advance the program counter by one statement, handling colon-separated
statements separately. If the interpreter executes full lines instead,
this method will behave as line-level stepping rather than statement-level."

This contradicts cmd_step() which confidently states:
"Executes a single statement (not a full line). If a line contains multiple
statements separated by colons, each statement is executed separately."

---

#### Code vs Documentation inconsistency

**Description:** The SettingsWidget footer displays keyboard shortcuts including 'ESC/^P=Cancel', but the keypress() handler treats 'ctrl p' as cancel. However, curses_keybindings.json shows Ctrl+P is bound to 'Parse program' in the editor context, creating a potential conflict.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
curses_settings_widget.py footer text:
"Enter=OK  ESC/^P=Cancel  ^A=Apply  ^R=Reset"

keypress() handler:
elif key == 'esc' or key == 'ctrl p':
    self._on_cancel()
    return None

curses_keybindings.json editor context:
"parse": {
  "keys": ["Ctrl+P"],
  "primary": "Ctrl+P",
  "description": "Parse program"
}

This creates ambiguity about what Ctrl+P should do when the settings widget is open.

---

#### Code inconsistency

**Description:** The _create_setting_widget() method for ENUM type creates radio buttons with display labels that strip 'force_' prefix for cleaner display, but stores the actual value with the prefix. However, the code comment says 'strip force_ prefix' but the implementation uses replace() which would strip it from anywhere in the string, not just as a prefix.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Code in _create_setting_widget():
# Create display label (strip force_ prefix for cleaner display)
display_label = choice.replace('force_', '')

The replace() method removes 'force_' from anywhere in the string, not just the prefix. Should use:
display_label = choice[6:] if choice.startswith('force_') else choice

Or:
display_label = choice.removeprefix('force_')  # Python 3.9+

---

#### code_vs_comment

**Description:** Comment describes three-field format but implementation varies between methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring at line 143 describes format as: "S<linenum> CODE" with variable-width line numbers.

_format_line() at line 449 implements: prefix = f"{status}{line_num_str} " (variable width)

_parse_line_numbers() at lines 991, 1024 implements: new_line = f" {line_num_formatted} {rest}" where line_num_formatted = f"{num_str:>5}" (fixed 5-char width)

The format string differs: variable width in display vs fixed width in paste handling.

---

#### code_vs_comment

**Description:** Docstring describes format as 'S<linenum> CODE' but actual format includes extra space

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple docstrings describe format as: "S<linenum> CODE"

But actual implementation at line 456 is: prefix = f"{status}{line_num_str} " (includes trailing space)

And at line 1024: new_line = f"{status}{line_num_formatted} {rest}" (space before rest)

The format should be documented as "S<linenum> CODE" with explicit space separator.

---

#### code_vs_comment

**Description:** Variable width vs fixed width inconsistency in _parse_line_number usage

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_parse_line_number() at line 197 extracts variable-width line numbers from display.

But _parse_line_numbers() at lines 991, 1024 reformats with fixed 5-char width: f"{num_str:>5}"

This means pasted content gets reformatted to fixed width, but then _parse_line_number reads it as variable width. The round-trip conversion is inconsistent.

---

#### code_vs_comment

**Description:** Comment claims ImmediateExecutor is recreated in start() with fresh OutputCapturingIOHandler, but the interpreter is reused. However, the code shows interpreter is created once in __init__ and the comment correctly states it's NOT recreated in start().

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~150: "# ImmediateExecutor Lifecycle:
# Created here with temporary IO handler (to ensure attribute exists),
# then recreated in start() with a fresh OutputCapturingIOHandler.
# The new executor in start() will reuse this same self.interpreter instance."

This is actually consistent - the comment correctly describes that interpreter is reused while executor is recreated. However, the phrasing could be clearer about what 'this same self.interpreter instance' refers to.

---

#### code_vs_comment

**Description:** Comment about main widget storage in _activate_menu differs from _show_keymap/_show_settings approach

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _activate_menu (~1050): "# Main widget storage: Extract base widget from current loop.widget
# This unwraps any existing overlay to get the actual main UI"

In _show_keymap (~1010): "# Main widget storage: Use self.main_widget (stored at UI creation)
# not self.loop.widget (current widget which might be a menu or overlay)"

The comments explicitly note different approaches: _activate_menu extracts base_widget from loop.widget, while _show_keymap uses self.main_widget directly. The comment in _activate_menu says 'This is different from _show_keymap/_show_settings which use self.main_widget directly.' This inconsistency in approach may indicate a design issue or refactoring opportunity.

---

#### internal_inconsistency

**Description:** Inconsistent main widget storage strategy across overlay methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_show_keymap and _show_settings use: self.main_widget (stored at UI creation)
_activate_menu uses: self.loop.widget.base_widget (extracted at runtime)
_show_help uses: self.main_widget (but doesn't store overlay state)

These three different approaches to accessing the main widget for overlays suggest inconsistent design patterns. The comments explicitly acknowledge these differences but don't explain why different methods are needed.

---

#### code_vs_comment

**Description:** Comment claims main_widget is stored in __init__, but code actually stores it in _show_settings method

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in _show_settings() says:
"Main widget storage: Uses self.main_widget (stored in __init__) rather than
self.loop.widget (which might be a menu or other overlay)."

But the code shows:
main_widget = self.main_widget
self._settings_main_widget = main_widget

The comment implies self.main_widget was set in __init__, but we don't see __init__ in this file fragment. The code then stores it in self._settings_main_widget for the settings overlay session. This suggests either:
1. The comment is outdated and self.main_widget is set elsewhere
2. The initialization is missing from the provided code
3. The comment should say 'stored at UI creation' not 'stored in __init__'

---

#### code_vs_comment

**Description:** Comment about PC override timing may be misleading about when start() resets PC

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program(), comment states:
"If start_line is specified (e.g., RUN 100), set PC to that line
This must happen AFTER interpreter.start() because start() calls setup()
which resets PC to the first line in the program. By setting PC here,
we override that default and begin execution at the requested line."

This comment assumes interpreter.start() always resets PC to first line, but the actual behavior depends on the implementation of start()/setup() which we don't see here. The comment makes a strong claim about internal behavior that may not be guaranteed by the API contract.

---

#### code_vs_comment

**Description:** Comment about PC preservation logic contradicts the actual condition check

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sync_program_to_runtime(), comment states:
"# Restore PC only if execution is running AND not paused at breakpoint
# (paused programs need PC reset to current breakpoint location)
# Otherwise ensure halted (don't accidentally start execution)
if self.running and not self.paused_at_breakpoint:
    # Execution is running - preserve execution state
    self.runtime.pc = old_pc
    self.runtime.halted = old_halted
else:
    # No execution in progress - ensure halted
    self.runtime.pc = PC.halted_pc()
    self.runtime.halted = True

The comment says 'paused programs need PC reset to current breakpoint location', but the else branch sets PC to halted_pc(), not to any breakpoint location. This suggests either:
1. The comment is wrong about what happens to paused programs
2. The code should have special handling for self.paused_at_breakpoint that preserves PC
3. halted_pc() somehow represents the breakpoint location (unlikely)

---

#### code_vs_comment

**Description:** Comment claims DELETE doesn't sync to runtime immediately, but _execute_immediate() calls _sync_program_to_runtime() before executing any immediate command

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_delete() docstring:
"Note: Doesn't sync to runtime immediately - sync happens when next immediate
command is executed via _execute_immediate."

But in _execute_immediate() method (line ~1150):
# Parse editor content into program (in case user typed lines directly)
# This updates self.program but doesn't affect runtime yet
self._parse_editor_content()

# Load program lines into program manager
self.program.clear()
for line_num in sorted(self.editor_lines.keys()):
    line_text = f"{line_num} {self.editor_lines[line_num]}"
    self.program.add_line(line_num, line_text)

# Sync program to runtime (but don't reset PC - keep current execution state)
# This allows LIST to work, but doesn't start execution
self._sync_program_to_runtime()

The sync happens BEFORE executing the command, so DELETE does sync to runtime immediately when executed.

---

#### code_vs_comment

**Description:** Comment claims RENUM doesn't sync to runtime immediately, but _execute_immediate() calls _sync_program_to_runtime() before executing any immediate command

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_renum() docstring:
"Note: Doesn't sync to runtime immediately - sync happens when next immediate
command is executed via _execute_immediate."

But _execute_immediate() syncs to runtime before executing any command, including RENUM. Same issue as with DELETE command.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate() says 'Don't call interpreter.start() because it resets PC!' but then explains that immediate executor already called start() with start_line parameter

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment around line ~1200:
# Initialize interpreter state for execution
# NOTE: Don't call interpreter.start() because it resets PC!
# If the immediate command was 'RUN 120', the immediate executor has already
# set PC to line 120 via interpreter.start(start_line=120), so we need to
# preserve that PC value and not reset it.

This is confusing - it says don't call start() because it resets PC, but then says the immediate executor already called start(start_line=120) which would have set PC. The logic seems contradictory about whether start() was called and whether PC needs preservation.

---

#### code_inconsistency

**Description:** Inconsistent state checking logic in _execute_immediate() - comment says 'No state checking - just ask the interpreter' but code checks has_work() which is a form of state checking

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Around line ~1220:
# Check if interpreter has work to do (after RUN statement)
# No state checking - just ask the interpreter
has_work = self.interpreter.has_work() if self.interpreter else False

The comment claims 'No state checking' but calling has_work() is checking interpreter state. The comment may be trying to distinguish from checking self.running or other UI state, but it's misleading.

---

#### code_vs_comment

**Description:** Comment claims help navigation keys are hardcoded and different from main editor, but the code actually loads keybindings from JSON file via HelpMacros class

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~70 states:
"# Footer shows navigation keys for the help system specifically
# Note: These are hardcoded help navigation keys, not loaded from keybindings.py
# (help navigation uses different keys than the main editor - e.g., 'U' for back,
# '/' for search). If these change, they must be updated here and in keypress()."

However, the code initializes HelpMacros which loads keybindings from JSON:
self.macros = HelpMacros('curses', help_root)

And HelpMacros._load_keybindings() loads from:
keybindings_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"

---

#### code_vs_documentation

**Description:** HelpMacros class loads keybindings but only uses them for {{kbd:action}} macro expansion, not for help navigation keys

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/help_widget.py`

**Details:**
help_macros.py docstring states:
"{{kbd:help}} → looks up 'help' action in keybindings (searches all sections)
                  and returns the primary keybinding for that action"

The _expand_kbd() method searches all sections for an action and returns its primary keybinding.

However, help_widget.py hardcodes navigation keys in keypress() method (lines with 'q', 'Q', 'esc', '/', 'enter', 'u', 'U', 'tab', 'shift tab') and in the footer text. These hardcoded keys don't use the loaded keybindings from HelpMacros.

---

#### code_internal_inconsistency

**Description:** HelpWidget hardcodes 'curses' UI name in constructor comment and initialization, but this widget is urwid-based and could theoretically be used by other urwid-based UIs

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Line ~60 comment:
"# HelpWidget is curses-specific (uses urwid), so hardcode 'curses' UI name"

Line ~61:
self.macros = HelpMacros('curses', help_root)

This hardcoding means if another UI backend also uses urwid, it would still load 'curses' keybindings. The ui_name parameter should potentially be passed to HelpWidget constructor instead of hardcoded.

---

#### code_internal_inconsistency

**Description:** KeybindingLoader loads from same JSON file as HelpMacros but provides different interface and conversion utilities

**Affected files:**
- `src/ui/keybinding_loader.py`

**Details:**
Both classes load from:
Path(__file__).parent / f"{self.ui_name}_keybindings.json"

HelpMacros provides:
- _expand_kbd(key_name) - searches all sections for action
- get_all_keys(section) - gets all keys for a section

KeybindingLoader provides:
- get_primary(section, action) - requires section parameter
- get_all_keys(section, action) - different signature than HelpMacros
- Tkinter conversion utilities

These two classes duplicate the JSON loading logic and provide overlapping but incompatible interfaces. This suggests a design inconsistency where keybinding access should be unified.

---

#### code_vs_comment

**Description:** Variable name LIST_KEY conflicts with its actual functionality

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment says: "Note: Variable named LIST_KEY for historical compatibility (originally BASIC's LIST command), but now implements step_line functionality in the debugger."

The variable is named LIST_KEY but:
1. It's loaded from 'step_line' action in JSON: _list_key = _get_key('editor', 'step_line')
2. The comment admits it's for "historical compatibility" but implements step_line
3. This creates confusion - the variable name doesn't match its purpose

---

#### code_vs_comment

**Description:** Comment describes Ctrl+L as context-sensitive but code doesn't show this implementation

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment at line ~200 says:
"# Note: Ctrl+L is context-sensitive in curses UI:
# - When debugging: Step Line (execute all statements on current line)
# - When editing: List program (same as LIST_KEY)"

However, the code only defines LIST_KEY once with a single binding from 'step_line'. There's no code showing context-sensitive behavior or dual functionality. The comment describes a feature that isn't visible in this module.

---

#### code_vs_comment

**Description:** Stack window documentation conflicts with implementation

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Two different comments describe the stack window:

1. At STACK_KEY definition:
"# Execution stack window (menu only - no dedicated key)
# Note: No keyboard shortcut is assigned to avoid conflicts with editor typing.
# The stack window is accessed via the menu system (Ctrl+U -> Debug -> Execution Stack)."

2. In KEYBINDINGS_BY_CATEGORY:
(STACK_DISPLAY, 'Toggle execution stack window')

where STACK_DISPLAY = 'Menu only'

The first comment says it's accessed via menu to avoid conflicts, but the second says 'Toggle' which implies a keyboard shortcut. The STACK_KEY is set to empty string '', confirming no keyboard shortcut exists, but the word 'Toggle' in the help text is misleading.

---

#### Code vs Documentation inconsistency

**Description:** ESC key binding to close in-page search is implemented but not documented in keybindings

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
In tk_help_browser.py line 127-129:
# Note: ESC closes search bar - this is not documented in tk_keybindings.json
# as it's a local widget binding rather than a global application keybinding
self.inpage_search_entry.bind('<Escape>', lambda e: self._inpage_search_close())

The code explicitly notes that ESC is not documented in tk_keybindings.json. However, the help_browser section in tk_keybindings.json documents other help browser keybindings like Ctrl+F and Return. For consistency, ESC should either be documented or the comment should explain why it's intentionally excluded.

---

#### code_vs_comment

**Description:** Comment describes 3-pane layout but implementation has 4 panes

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring says:
"    - 3-pane vertical layout:
      * Editor with line numbers (top, ~50% - weight=3)
      * Output pane (middle, ~33% - weight=2)
      * Immediate mode input line (bottom, ~17% - weight=1)"

But code creates 4 panes:
1. Editor frame (weight=3)
2. Output frame (weight=2) 
3. INPUT row (hidden by default, shown for INPUT statements)
4. Immediate mode frame (weight=1)

The INPUT row is a separate pane between output and immediate mode.

---

#### code_vs_comment

**Description:** Ctrl+I keybinding comment inconsistency between menu creation and actual binding

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _create_menu() at line ~495, comment says:
"# Note: Ctrl+I is bound directly to editor text widget in start() (not root window)
# to prevent tab key interference - see editor_text.text.bind('<Control-i>', ...)"

But in start() method at line ~235, the actual binding is:
"# Bind Ctrl+I for smart insert line (must be on text widget to prevent tab)
self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)"

The comment in _create_menu() references a different location than where the binding actually occurs. The comment says 'see editor_text.text.bind' but doesn't specify the line number, making it hard to verify the cross-reference.

---

#### code_vs_comment

**Description:** Variables window heading text inconsistency with sort functionality

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~1009, the initial heading is set:
"tree.heading('#0', text='↓ Variable (Last Accessed)')"

This hardcodes 'Last Accessed' as the sort mode, but the actual default sort mode is set at line ~127:
"self.variables_sort_column = 'accessed'  # Current sort column: 'accessed', 'written', 'read', 'name', 'type', or 'value'"

While 'accessed' corresponds to 'Last Accessed', the heading text should be dynamically generated based on the sort column variable, not hardcoded. If the default sort column changes, the heading won't match.

---

#### code_vs_comment

**Description:** Comment claims default subscripts use array_base for OPTION BASE 0/1, but code has fallback for 'invalid' array_base values that isn't mentioned in BASIC-80 spec

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1090:
# If no default subscripts, use first element based on array_base
# (OPTION BASE 0 uses zeros, OPTION BASE 1 uses ones, invalid values fallback to zeros)

Code at lines ~1095-1103:
if array_base == 0:
    # OPTION BASE 0: use all zeros
    default_subscripts = ','.join(['0'] * len(dimensions))
elif array_base == 1:
    # OPTION BASE 1: use all ones
    default_subscripts = ','.join(['1'] * len(dimensions))
else:
    # Invalid array_base (not 0 or 1) - fallback to 0
    default_subscripts = ','.join(['0'] * len(dimensions))

MBASIC 5.21 only allows OPTION BASE 0 or 1. The 'else' case for invalid array_base values suggests the runtime might allow other values, which would be non-standard behavior.

---

#### code_vs_comment

**Description:** Comment claims _remove_blank_lines is only called from _on_enter_key, but this limits its usefulness for paste operations

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1779:
Currently called only from _on_enter_key (after each keypress), not
after pasting or other modifications. This provides continuous cleanup
as the user types.

This is a design limitation rather than a bug, but the comment acknowledges that blank lines won't be removed after paste operations. This could lead to inconsistent behavior where typing removes blanks but pasting doesn't. The comment documents this but doesn't explain why this design choice was made.

---

#### code_vs_comment

**Description:** Docstring for _edit_array_element claims to pre-fill subscripts from value_display, but also has fallback logic based on array_base

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring at line ~1062:
The dialog pre-fills with the last accessed subscripts and value if available,
extracted from value_display (e.g., "[5,3]=42" portion).

But code at lines ~1088-1103 has extensive fallback logic:
# If no default subscripts, use first element based on array_base
if not default_subscripts and dimensions:
    array_base = self.runtime.array_base
    if array_base == 0:
        default_subscripts = ','.join(['0'] * len(dimensions))
    elif array_base == 1:
        default_subscripts = ','.join(['1'] * len(dimensions))
    else:
        default_subscripts = ','.join(['0'] * len(dimensions))

The docstring doesn't mention this fallback behavior when no last accessed subscripts are available.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of statement highlighting on mouse click vs other events

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_mouse_click (line ~1763):
# Clear yellow statement highlight when clicking (allows text selection to be visible)
if self.paused_at_breakpoint:
    self._clear_statement_highlight()

But _on_cursor_move and _on_focus_out don't clear the statement highlight. This means the yellow highlight is only cleared on mouse clicks, not when using keyboard navigation. This creates inconsistent UX where keyboard users see the highlight but mouse users don't.

---

#### code_vs_comment

**Description:** Comment claims _on_key_press clears highlight on ANY key including arrows/function keys, but code only clears on keypress when paused_at_breakpoint is True

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment says: 'Note: This clears on ANY key including arrows/function keys, not just editing keys.'

But code shows:
if self.paused_at_breakpoint:
    self._clear_statement_highlight()

The clearing only happens when paused_at_breakpoint is True, not on ANY keypress unconditionally.

---

#### code_vs_comment

**Description:** Docstring for cmd_cont says 'Invalid if program was edited after stopping' but no validation code checks for program edits

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring states:
'Invalid if program was edited after stopping.'

But the implementation in cmd_cont() does not check if the program was edited. It only checks:
if not self.runtime or not self.runtime.stopped:
    self._write_output('?Can\'t continue')
    return

There is no validation that the program hasn't been modified since stopping.

---

#### code_vs_comment

**Description:** Comment in _check_line_change says 'old_line_num is None: First time tracking this line' but this contradicts the logic that old_line_num comes from last_edited_line_text which was already set

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1260 says:
'# Don\'t trigger sort when:
# - old_line_num is None: First time tracking this line (cursor just moved here, no editing yet)
# - This prevents unnecessary re-sorting when user clicks around without making changes'

But old_line_num is parsed from self.last_edited_line_text, which was set when the cursor was last on that line. If old_line_num is None, it means the previous line had no line number, not that we're tracking it for the first time. The 'first time tracking' case is actually handled earlier when self.last_edited_line_index is None.

---

#### code_vs_comment

**Description:** Comment claims immediate_history is always None (line ~291), but _setup_immediate_context_menu() and related methods (_copy_immediate_selection, _select_all_immediate) reference self.immediate_history as if it's a valid widget

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _add_immediate_output() states:
"Note: self.immediate_history exists but is always None (see line ~291) - it's a dummy attribute for compatibility with code that references it."

But _setup_immediate_context_menu() docstring says:
"NOTE: This method is currently unused - immediate_history is always None in the Tk UI (see line ~291). This is dead code retained for potential future use if immediate mode gets its own output widget."

However, methods like _copy_immediate_selection() and _select_all_immediate() directly call methods on self.immediate_history:
"selected_text = self.immediate_history.get(tk.SEL_FIRST, tk.SEL_LAST)"
"self.immediate_history.tag_add(tk.SEL, '1.0', tk.END)"

These would fail with AttributeError if immediate_history is None.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate() says 'Execute without echoing' but the code does echo output via _add_immediate_output()

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment states:
"# Execute without echoing (GUI design choice: command is visible in entry field,
# and 'Ok' prompt is unnecessary in GUI context - only results are shown)
success, output = self.immediate_executor.execute(command)

# Show output if any
if output:
    self._add_immediate_output(output)"

The comment says 'without echoing' but then immediately shows output. The comment seems to mean 'without echoing the command itself or Ok prompt', but the phrasing is confusing since output IS echoed.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate() says 'Use has_work() to check if the interpreter is ready to execute' but the actual check is 'has_work = self.interpreter.has_work()' followed by 'if has_work:' which doesn't verify readiness, just whether work exists

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment states:
"# Check if interpreter has work to do (after RUN statement)
# Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command).
# This complements runtime flag checks (self.running, runtime.halted) used elsewhere.
has_work = self.interpreter.has_work()"

The comment conflates 'has work to do' with 'ready to execute'. These are different concepts - has_work() likely checks if there's a program loaded, not if the interpreter is in a ready state.

---

#### code_vs_comment

**Description:** Comment says blank line removal is 'Implemented via _on_cursor_move()' but the actual implementation uses both _on_cursor_move() and _delete_line()

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring states: 'Implemented via _on_cursor_move() tracking cursor movement'

Actual implementation: _on_cursor_move() detects blank lines and schedules deletion, but _delete_line() performs the actual deletion. The comment oversimplifies the implementation.

---

#### code_vs_comment

**Description:** _parse_line_number() regex comment says 'no match - invalid' for '10REM' but this is actually valid BASIC syntax in some dialects

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment in _parse_line_number(): '# Examples: "10 PRINT" (whitespace after), "10" (end after), "10REM" (no match - invalid)'

The regex r'^(\d+)(?:\s|$)' requires whitespace or end-of-string after the line number, so '10REM' would not match. However, the comment labels this as 'invalid' which may be incorrect - some BASIC dialects allow commands immediately after line numbers without whitespace (e.g., '10REM comment').

---

#### code_vs_comment

**Description:** _delete_line() docstring parameter description is inconsistent with how the method is actually called

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring says: 'line_num: Tkinter text widget line number (1-based sequential index), not BASIC line number (e.g., 10, 20, 30)'

Calling code in _on_cursor_move():
self.current_line = new_line
self.text.after_idle(self._delete_line, self.current_line)

where new_line = int(cursor_pos.split('.')[0])

The docstring correctly describes what the parameter should be, and the code appears to pass the correct value. However, the distinction between 'Tkinter line number' and 'BASIC line number' could be clearer throughout the codebase to avoid confusion.

---

#### code_vs_comment

**Description:** _redraw() docstring says 'BASIC line numbers are parsed from text content (not drawn in canvas)' but this is already stated in the class docstring, creating redundancy and potential for inconsistency

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring: 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas).'

_redraw() docstring: 'Note: BASIC line numbers are parsed from text content (not drawn in canvas).'

While not technically inconsistent, having the same information in multiple places increases maintenance burden and risk of future inconsistency if one is updated but not the other.

---

#### code_vs_comment

**Description:** Comment in serialize_variable() claims type suffixes are only added if explicit, but code doesn't check explicit_type_suffix attribute consistently

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment says: "Only add type suffix if it was explicit in the original source"
Code checks: if var.type_suffix and getattr(var, 'explicit_type_suffix', False)
However, getattr with False default means if explicit_type_suffix is missing, it defaults to False and suffix won't be added even if type_suffix exists. This may be intentional but the comment doesn't clarify the fallback behavior.

---

#### code_vs_comment

**Description:** serialize_statement() fallback for unhandled statement types creates REM comment but warning says this could create invalid BASIC code

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Code:
else:
    # Fallback for unhandled statement types: return a placeholder REM comment.
    # WARNING: This could create invalid BASIC code during RENUM if new statement
    # types are added but not handled here. Ensure all statement types are supported.
    return f"REM {stmt_type}"

The warning indicates this is a dangerous fallback that could corrupt programs during RENUM, but the code still uses it. This suggests either: (1) the fallback should raise an error instead, or (2) the warning is overstated.

---

#### code_vs_comment

**Description:** update_line_references() regex pattern comment claims to match 'ON <expr> GOTO/GOSUB' but pattern may not correctly handle all expressions

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment says: "Keywords: GOTO, GOSUB, THEN, ELSE, or 'ON <expr> GOTO/GOSUB'"

Pattern: r'\b(GOTO|GOSUB|THEN|ELSE|ON\s+[^G]+\s+GOTO|ON\s+[^G]+\s+GOSUB)\s+(\d+)'

The [^G]+ pattern means "any characters except G". This would fail for expressions containing the letter G, such as:
- ON G GOTO 100
- ON FLAG GOTO 100
- ON GETVAL() GOTO 100

This is a potential bug where the regex doesn't match the documented behavior.

---

#### code_vs_documentation

**Description:** Docstring claims Runtime accesses program.line_asts directly, but code shows Runtime is initialized with program.line_asts and program.lines as separate parameters

**Affected files:**
- `src/ui/visual.py`

**Details:**
Comment in cmd_run() says:
"# (Runtime accesses program.line_asts directly, no need for program_ast variable)"

But the actual code is:
"self.runtime = Runtime(self.program.line_asts, self.program.lines)"

This suggests Runtime receives line_asts and lines as constructor parameters, not accessing them directly from program object.

---

#### code_vs_comment

**Description:** Missing assignment of program_manager to self.program in __init__ method

**Affected files:**
- `src/ui/visual.py`

**Details:**
The __init__ docstring and class docstring reference 'self.program' throughout:
"Args:
    program_manager: ProgramManager instance"

And usage examples show:
"self.program.add_line(line_num, text)"
"self.program.get_lines()"
"self.program.clear()"

But the __init__ method only shows:
"super().__init__(io_handler, program_manager)"
"self.runtime = None"
"self.interpreter = None"

There's no visible 'self.program = program_manager' assignment, suggesting it might be done in the parent UIBackend class, but this is not documented.

---

#### code_vs_comment

**Description:** Comment claims sort defaults match Tk UI but references lines that are not visible

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~127-128 comment in VariablesDialog.__init__ states:
"# Sort state (matches Tk UI defaults: see src/ui/tk_ui.py lines 91-92)
self.sort_mode = 'accessed'  # Current sort mode
self.sort_reverse = True  # Sort direction"

The comment references specific lines in tk_ui.py (91-92) to justify the default values, but those lines are not provided in the source code files, making it impossible to verify the claim that these defaults match the Tk UI.

---

#### code_vs_comment

**Description:** Comment claims RUN does NOT clear output, but code behavior and teletype analogy suggest continuous scrolling is intentional

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1799 comment: "Note: This implementation does NOT clear output (see line 1799 comment below)."
But the _menu_run method doesn't call _clear_output(), and another comment says "Don't clear output - continuous scrolling like ASR33 teletype"
This is consistent behavior, not an inconsistency - the comment is accurate.

---

#### code_vs_comment

**Description:** Comment about Ctrl+C handling is misleading - describes external behavior not implemented in this method

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1850 in _execute_tick():
  "Note on Ctrl+C handling (external to this method):
  Ctrl+C interrupts are handled at the top level (in mbasic main, which wraps
  start_web_ui() in a try/except). During long-running programs, Ctrl+C can be
  unresponsive because Python signal handlers only run between bytecode instructions.
  This method does not implement any Ctrl+C handling directly."
This comment describes a limitation but doesn't indicate if there's a Stop button or other mechanism. The code shows _menu_stop exists but the comment doesn't reference it.

---

#### code_vs_comment

**Description:** Breakpoint implementation comment describes both PC objects and plain integers, but toggle_breakpoint only creates PC objects

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1990 in _update_breakpoint_display():
  # Note: self.runtime.breakpoints is a set that can contain:
  #   - PC objects (statement-level breakpoints, created by _toggle_breakpoint)
  #   - Plain integers (line-level breakpoints, legacy/compatibility)
  # This implementation uses PC objects exclusively, but handles both for robustness.
But _toggle_breakpoint (line ~1920) and _do_toggle_breakpoint (line ~2030) only create PC objects:
  pc = PC(line_num, stmt_offset)
  pc = PC(line_num, 0)
No code path creates plain integer breakpoints, making the 'legacy/compatibility' comment misleading.

---

#### code_vs_comment

**Description:** Comment about RUN with line number shows feature exists but implementation details are unclear

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1830 in _menu_run():
  # Check if RUN was called with a line number (e.g., RUN 120)
  # This is set by immediate_executor when user types "RUN 120"
  if hasattr(self, '_run_start_line') and self._run_start_line:
This references immediate_executor setting _run_start_line, but immediate_executor is not shown in this file. The mechanism for how 'RUN 120' gets parsed and sets this attribute is not documented.

---

#### code_vs_comment

**Description:** Help menu comment says 'URL is constructed by web_help_launcher' but then references undefined 'url' variable

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2280 in _menu_help():
  # Note: URL is constructed by web_help_launcher based on topic parameter
  success = open_help_in_browser(topic="help/ui/web/", ui_type="web")
  ...
  else:
    msg = f'Could not open browser automatically.\n\nPlease open this URL manually:\n{url}'
The variable 'url' is never defined in this method, causing a NameError if the else branch executes. Same issue in _menu_games_library() at line ~2300.

---

#### code_vs_comment

**Description:** Comment says 'state properties return 0 when halted' but doesn't document which properties or why

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2200 in _handle_step_result():
  # Get char positions directly from statement_table (state properties return 0 when halted)
  char_start = None
  char_end = None
  stmt = self.runtime.statement_table.get(pc)
This implies state.current_statement_char_start and state.current_statement_char_end return 0 when halted, but this behavior isn't documented in the state object definition.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC only if exec_timer is active, but the logic description is confusing about 'preventing accidental starts'

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says: 'Preserves current PC/execution state only if exec_timer is active; otherwise resets PC to halted. This allows LIST and other commands to see the current program without starting execution.'

But inline comment says: '# This logic is about PRESERVING vs RESETTING state, not about preventing accidental starts'

The comment contradicts the docstring's claim about 'preventing accidental starts' (via LIST commands), creating confusion about the actual purpose.

---

#### code_vs_comment

**Description:** Comment describes double line number detection for paste, but the regex and logic may not match all cases

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says: 'When pasting with auto-numbering enabled, the first line may have a double line number (e.g., "10 100 PRINT" where "10 " is the auto-number prompt and "100 PRINT" is pasted)'

Code checks: if lines and re.match(r'^\d+\s+\d+\s+', lines[0])

But then extracts with: match = re.match(r'^(\d+)\s+(.*)$', lines[0])

The second regex doesn't verify the double number pattern - it just captures first number and rest, which could incorrectly trigger on single-numbered lines with content.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate claims not to sync editor from AST, but doesn't explain how RENUM updates editor

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says: 'Architecture note: We do NOT sync editor from AST after immediate commands. This preserves the one-way data flow: editor text → AST → execution. Syncing AST → editor would lose user's exact text, spacing, and comments. Some immediate commands (like RENUM) modify the AST directly, but we rely on those commands to update the editor text themselves, not via automatic sync.'

This claims RENUM updates editor text directly, but there's no visible code in this method that does so, and no clear indication of where that happens. This could be outdated or incomplete documentation.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says to query interpreter via has_work() instead of runtime flags, but doesn't explain why or what the difference is

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# Check if interpreter has work to do (after RUN statement) # Query interpreter directly via has_work() instead of checking runtime flags'

This suggests there are multiple ways to check for work (interpreter.has_work() vs runtime flags), but doesn't explain why one is preferred or what the semantic difference is. This could indicate architectural confusion or incomplete refactoring.

---

#### documentation_inconsistency

**Description:** README.md mentions a 'visual backend' as part of web UI, but this is not documented anywhere else and no visual backend exists in the codebase

**Affected files:**
- `docs/help/README.md`
- `docs/help/common/index.md`

**Details:**
README.md states: 'Note: The visual backend is part of the web UI implementation.'

This appears to be outdated or incorrect - there is no separate 'visual backend' mentioned in any other documentation or visible in the code files provided.

---

#### code_vs_documentation

**Description:** Help launcher default UI type inconsistency

**Affected files:**
- `src/ui/web_help_launcher.py`
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
web_help_launcher.py open_help_in_browser() has default parameter:
ui_type='tk'

But this is in a file called 'web_help_launcher.py' and the function is used for web-based help. The default should likely be 'web' not 'tk', or the parameter should be required.

---

#### code_vs_documentation

**Description:** Settings dialog documented features not visible in code

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/debugging.md`

**Details:**
debugging.md extensively documents Variables Window and Execution Stack Window with keyboard shortcuts:
'Tk UI: Debug → Variables or Ctrl+V'
'Tk UI: Debug → Execution Stack or Ctrl+K'

But web_settings_dialog.py only implements settings for auto-numbering and limits. There's no Variables Window or Stack Window implementation visible in the WebSettingsDialog class. Either the documentation is for a different UI (Tk/Curses) and shouldn't be in 'common', or the web UI is missing these features.

---

#### documentation_inconsistency

**Description:** Compiler documentation exists but no compiler code provided

**Affected files:**
- `docs/help/common/compiler/index.md`
- `docs/help/common/compiler/optimizations.md`

**Details:**
Extensive compiler optimization documentation exists describing 27 optimizations in detail, but no compiler implementation code is provided in the source files. The documentation states:
'Status: In Progress'
'Documentation for the code generation phase will be added as the compiler backend is developed.'

This suggests the compiler is not yet implemented, making the detailed optimization documentation premature or the code is missing from the provided files.

---

#### documentation_inconsistency

**Description:** ASCII codes table shows DEL at position 127 in both the printable characters table and special character section, creating ambiguity about whether it's printable or special

**Affected files:**
- `docs/help/common/language/appendices/ascii-codes.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
In ascii-codes.md:
- Printable Characters table (32-126) shows: '| 127 | 7F | DEL |'
- Special Character section shows: '| 127 | 7F | DEL | Delete/Rubout |'

DEL (127) is traditionally a control character, not a printable character. The table header says 'Printable Characters (32-126)' but includes 127.

---

#### documentation_inconsistency

**Description:** Inconsistent precision specifications for floating-point types

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/cdbl.md`
- `docs/help/common/language/functions/csng.md`

**Details:**
In data-types.md:
- SINGLE: '~7 digits'
- DOUBLE: '~16 digits'

In cdbl.md:
'Double-precision numbers have approximately 16 digits of precision'

In csng.md:
'Single-precision numbers have approximately 7 digits of precision'

The use of '~' vs 'approximately' is inconsistent. Should standardize terminology.

---

#### documentation_inconsistency

**Description:** Different line terminator information between character-set.md and ascii-codes.md

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
In character-set.md:
'| 10 | LF | Line feed (Unix newline) |'
'| 13 | CR | Carriage return (Mac/DOS newline) |'

In ascii-codes.md:
'| 10 | 0A | LF | Line Feed | New line |'
'| 13 | 0D | CR | Carriage Return | Return to line start |'

character-set.md provides OS-specific context (Unix/Mac/DOS) while ascii-codes.md uses generic descriptions. Should be consistent.

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' references in CVI/CVS/CVD - includes unrelated functions

**Affected files:**
- `docs/help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
In cvi-cvs-cvd.md 'See Also' section includes:
'- [CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/cload.md)'
'- [CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/csave.md)'
'- [LPRINT AND LPRINT USING](../statements/lprint-lprint-using.md)'

These cassette tape and printer functions are not directly related to binary string conversion. The 'See Also' section appears to be copied from another document without curation.

---

#### documentation_inconsistency

**Description:** Inconsistent range specifications for floating-point types

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/cdbl.md`
- `docs/help/common/language/functions/csng.md`

**Details:**
In data-types.md:
- SINGLE: '±2.938736×10^-39 to ±1.701412×10^38'
- DOUBLE: '±2.938736×10^-39 to ±1.701412×10^38 (same numerical range as single-precision, but with greater precision)'

In cdbl.md:
'range from 2.938735877055719 x 10^-39 to 1.701411834604692 x 10^38'

In csng.md:
'range from 2.938736 x 10^-39 to 1.701412 x 10^38'

The ranges have different precision in their specification (more digits in cdbl.md), and data-types.md explicitly notes same range for both types while individual function docs don't clarify this.

---

#### documentation_inconsistency

**Description:** Inconsistent Control-C behavior documentation between INKEY$ and INPUT$

**Affected files:**
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/input_dollar.md`

**Details:**
inkey_dollar.md states: 'Note: In original MBASIC, Control-C would terminate the program. In the BASIC Compiler, Control-C was passed through. This implementation passes Control-C through to the program (it can be detected and handled).'

input_dollar.md states: 'Note: In original MBASIC, Control-C would interrupt the INPUT$ function. This implementation passes Control-C through to the program (it can be detected and handled).'

The notes describe different original behaviors ('terminate the program' vs 'interrupt the INPUT$ function') but both claim this implementation passes Control-C through. This should be clarified for consistency.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation status descriptions for machine code features

**Affected files:**
- `docs/help/common/language/functions/usr.md`
- `docs/help/common/language/functions/varptr.md`
- `docs/help/common/language/statements/call.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
USR function says 'Always returns 0', VARPTR says 'Function is not available', CALL says 'Statement is parsed but no operation is performed', and DEF USR says 'Statement is parsed but no operation is performed'. These should have consistent behavior descriptions - either all return/do nothing, all are unavailable, or all are parsed but ignored.

---

#### documentation_inconsistency

**Description:** CLEAR documentation has confusing historical note about parameter meanings

**Affected files:**
- `docs/help/common/language/statements/clear.md`

**Details:**
The CLEAR documentation states: 'In MBASIC 5.21 (BASIC-80 release 5.0 and later): expression1: If specified, sets the highest memory location available for BASIC to use' but then says 'Historical note: In earlier versions of BASIC-80 (before release 5.0), the parameters had different meanings: expression1 set the amount of string space'. This is confusing because MBASIC 5.21 IS BASIC-80 release 5.21, which is after 5.0. The documentation should clarify that MBASIC 5.21 uses the newer parameter meanings.

---

#### documentation_inconsistency

**Description:** CHAIN and COMMON documentation have circular references without clear explanation

**Affected files:**
- `docs/help/common/language/statements/chain.md`
- `docs/help/common/language/statements/common.md`

**Details:**
CHAIN says 'Variables are only passed to the chained program if they are declared in a COMMON statement' and COMMON says 'The COMMON statement is used in conjunction with the CHAIN statement'. However, neither clearly explains the relationship or provides a complete example showing both statements working together. The CHAIN example shows COMMON in PROG1.BAS and PROG2.BAS but doesn't show the actual CHAIN statement with COMMON variables.

---

#### documentation_inconsistency

**Description:** Operators documentation exists but not linked from main language index

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/operators.md`

**Details:**
The file docs/help/common/language/operators.md provides comprehensive operator documentation, but the main language index (docs/help/common/language/index.md) does not link to it in the 'Language Components' or 'Language Features' sections. The index mentions operators briefly under 'Language Features' but doesn't provide a link to the detailed operators guide.

---

#### documentation_inconsistency

**Description:** DIM documentation states minimum subscript is 0 unless OPTION BASE is used, but doesn't mention that arrays can be redimensioned after ERASE. ERASE doc mentions redimensioning but DIM doesn't cross-reference this capability.

**Affected files:**
- `docs/help/common/language/statements/dim.md`
- `docs/help/common/language/statements/erase.md`

**Details:**
DIM.md: 'If an array variable name is used without a DIM statement, the maximum value of its subscript(s) is assumed to be 10.'

ERASE.md: 'Arrays may be redimensioned after they are ERASEd, or the previously allocated array space in memory may be used for other purposes. If an attempt is made to redimension an array without first ERASEing it, a "Redimensioned array" error occurs.'

---

#### documentation_inconsistency

**Description:** FOR-NEXT documentation contains contradictory information about loop execution. States 'Loop body executes at least once' but also describes termination check that could prevent execution.

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
FOR-NEXT.md states:
'Loop body executes at least once regardless of start/end relationship'
But also:
'If variable exceeds ending value (y) considering STEP direction, loop terminates'

These statements conflict - if the initial value already exceeds the end value, the loop should not execute at all in standard BASIC behavior.

---

#### documentation_inconsistency

**Description:** FILES documentation mentions CP/M automatically adding .BAS extension but doesn't clarify if this applies to FILES command or only to other commands like LOAD/SAVE.

**Affected files:**
- `docs/help/common/language/statements/files.md`

**Details:**
FILES.md: 'Note: CP/M automatically adds .BAS extension if none is specified for BASIC program files.'

This note appears in FILES.md but it's unclear if FILES command itself adds .BAS or if this is just general CP/M behavior. Other docs (KILL.md) have similar notes but are more specific about which commands this applies to.

---

#### documentation_inconsistency

**Description:** INPUT and LINE INPUT both describe semicolon behavior for suppressing carriage return, but the syntax descriptions differ in how they show the semicolon placement.

**Affected files:**
- `docs/help/common/language/statements/input.md`
- `docs/help/common/language/statements/line-input.md`

**Details:**
INPUT.md syntax: 'INPUT[:] [<"prompt string">:]<list of variables>'
INPUT.md remarks: 'A semicolon immediately after INPUT suppresses the carriage return/line feed'

LINE-INPUT.md syntax: 'LINE INPUT [;"prompt string";]<string variable>'
LINE-INPUT.md remarks: 'If LINE INPUT is immediately followed by a semicolon (before the prompt string)...'

The syntax notation is inconsistent - INPUT uses [:] while LINE INPUT uses [;"...";]

---

#### documentation_inconsistency

**Description:** FOR-NEXT documentation states 'Termination check occurs at NEXT, not FOR (after loop body has executed)' which contradicts standard BASIC behavior where the check can occur before first iteration.

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
FOR-NEXT.md: 'Termination check occurs at NEXT, not FOR (after loop body has executed)'

This implies the loop always executes at least once, but earlier in the same doc it says:
'If variable exceeds ending value (y) considering STEP direction, loop terminates'

Standard BASIC checks the condition before the first iteration in some implementations.

---

#### documentation_inconsistency

**Description:** GOSUB documentation states nesting is limited only by available memory, but FOR-NEXT doesn't mention any nesting limits, creating inconsistency in how limits are documented.

**Affected files:**
- `docs/help/common/language/statements/gosub-return.md`
- `docs/help/common/language/statements/for-next.md`

**Details:**
GOSUB-RETURN.md: 'Such nesting of subroutines is limited only by available memory.'

FOR-NEXT.md doesn't mention any limits on nested loops, but presumably the same memory limitation applies. Inconsistent documentation of limits across similar features.

---

#### documentation_inconsistency

**Description:** LPRINT documentation references PRINT USING but PRINT documentation does not document PRINT USING syntax

**Affected files:**
- `docs/help/common/language/statements/lprint-lprint-using.md`
- `docs/help/common/language/statements/print.md`

**Details:**
lprint-lprint-using.md states 'LPRINT USING works exactly like PRINT USING' and has 'See Also' link to print.md for 'PRINT USING', but print.md only documents basic PRINT statement without USING clause. The syntax section in print.md shows 'PRINT [<list of expressions>]' with no USING variant documented.

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' sections between LSET and RSET

**Affected files:**
- `docs/help/common/language/statements/lset.md`
- `docs/help/common/language/statements/rset.md`

**Details:**
lset.md includes CLOSE in 'See Also' but rset.md does not. Both documents are nearly identical in structure and purpose, so they should have identical 'See Also' sections. lset.md: 'CLOSE - Close file when done'. rset.md omits CLOSE.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-referencing between error handling statements

**Affected files:**
- `docs/help/common/language/statements/on-error-goto.md`
- `docs/help/common/language/statements/resume.md`

**Details:**
on-error-goto.md 'See Also' includes: ERROR, RESUME, ERR/ERL. resume.md 'See Also' includes: ERROR, ON ERROR GOTO, ERR/ERL Variables. Both reference each other but use slightly different naming: 'ERR/ERL' vs 'ERR/ERL Variables'.

---

#### documentation_inconsistency

**Description:** PUT documentation mentions PRINT# and WRITE# can be used with random files but PRINT# documentation only mentions sequential files

**Affected files:**
- `docs/help/common/language/statements/put.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
put.md states: 'PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer before a PUT statement.' However, printi-printi-using.md only states: 'PRINT# writes data to a sequential file opened for output (mode "O") or append (mode "A")' with no mention of random file usage.

---

#### documentation_inconsistency

**Description:** RESUME documentation claims verification against MBASIC 5.21 but no other docs make this claim

**Affected files:**
- `docs/help/common/language/statements/resume.md`

**Details:**
resume.md includes section 'Testing RESUME' with 'Verified behavior against real MBASIC 5.21' and checkmarks. No other documentation files include verification claims. This is inconsistent with documentation style across other files.

---

#### documentation_inconsistency

**Description:** RUN statement documentation mentions file extension defaults to .BAS, but SAVE documentation says CP/M default extension is .BAS. This creates ambiguity about whether .BAS is added automatically or is just a convention.

**Affected files:**
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/save.md`

**Details:**
run.md: 'File extension defaults to .BAS if not specified'
save.md: 'With CP/M, the default extension .BAS is supplied'

---

#### documentation_inconsistency

**Description:** Variables documentation mentions 'variables.case_conflict' setting but doesn't fully explain it. Settings documentation provides complete details. Cross-reference is missing.

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md mentions: 'Case Sensitivity: Variable names are not case-sensitive by default (Count = COUNT = count), but the behavior when using different cases can be configured via the `variables.case_conflict` setting'
But doesn't link to settings.md which has full details of the choices (first_wins, error, prefer_upper, etc.)

---

#### documentation_inconsistency

**Description:** SETSETTING and SHOWSETTINGS are documented as 'MBASIC Extension' but settings.md doesn't clarify if these commands are available in all UIs or only specific ones.

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
setsetting.md and showsettings.md both say:
'**Versions:** MBASIC Extension'
But settings.md section 'Accessing Settings by UI' shows CLI commands work, but doesn't clarify if these work in all UIs or are CLI-only.

---

#### documentation_inconsistency

**Description:** Variables documentation states 'only the first 2 characters of variable names were significant' in original MBASIC but doesn't clarify if this limitation applies to array names, function names, or DEF FN names.

**Affected files:**
- `docs/help/common/language/variables.md`

**Details:**
variables.md: '**Note on Variable Name Significance:** In the original MBASIC 5.21, only the first 2 characters of variable names were significant (AB, ABC, and ABCDEF would be the same variable). This Python implementation uses the full variable name for identification'
Doesn't specify if this applies to: array names (DIM ARRAY1(10) vs ARRAY2(10)), DEF FN names, or other identifiers.

---

#### documentation_inconsistency

**Description:** Curses editing documentation says 'Lines are automatically sorted by number' but doesn't mention if this is true for all UIs. Tk documentation also mentions this but CLI documentation doesn't clarify.

**Affected files:**
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
curses/editing.md: 'Lines are automatically sorted by number'
tk/index.md: 'Lines automatically sort by number'
But cli/index.md doesn't mention automatic sorting behavior.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'command level' vs 'Ok prompt' vs 'BASIC prompt'. Different docs use different terms for the same concept.

**Affected files:**
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
run.md: 'return to command level'
stop.md: 'return to command level'
system.md: 'returns to the BASIC "Ok" prompt' vs 'return to the operating system command level'
These terms are used interchangeably without clear definition.

---

#### documentation_inconsistency

**Description:** TRON-TROFF documentation example shows output with inconsistent spacing and formatting that may not match actual implementation output.

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
tron-troff.md example shows:
'[10] [20] [30] [40] 1   10   20'
with specific spacing, but doesn't clarify if this exact formatting is guaranteed or implementation-dependent.

---

#### documentation_inconsistency

**Description:** Inconsistent description of PEEK behavior between architecture.md and compatibility.md

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states: 'PEEK: Returns random integer 0-255 (for RNG seeding compatibility)'

compatibility.md states: 'PEEK: Returns random integer 0-255 (for RNG seeding compatibility)'

Both documents agree on the behavior, but architecture.md emphasizes 'PEEK does NOT return values written by POKE' while compatibility.md also states this. However, the architecture.md section is under 'Hardware Compatibility Notes' while compatibility.md places it under 'Hardware-Specific Features'. The placement and context differ slightly.

---

#### documentation_inconsistency

**Description:** Inconsistent naming of the project/implementation

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/features.md`

**Details:**
extensions.md states: 'This is **MBASIC-2025**, a modern implementation of Microsoft BASIC-80 5.21 (CP/M era)' and lists multiple project names under consideration: 'MBASIC-2025 (emphasizes the modern update)', 'Visual MBASIC 5.21 (emphasizes the multiple UIs)', 'MBASIC++ (emphasizes extensions)', 'MBASIC-X (extended MBASIC)'

However, other documents consistently refer to it as 'MBASIC' or 'this MBASIC interpreter' without the '-2025' suffix. features.md title is 'MBASIC Features', compatibility.md refers to 'MBASIC-2025' in one place but 'this implementation' elsewhere.

The project naming appears undecided, creating inconsistency across documentation.

---

#### documentation_inconsistency

**Description:** Confusing explanation of Web UI filename uppercasing

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
compatibility.md states: 'Automatically uppercased by the virtual filesystem (CP/M style)' followed by 'The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage'

The second statement seems to be defending against a misinterpretation, but it's unclear why uppercasing would be confused with persistent storage. This appears to be addressing a concern that isn't obvious from the context, making the documentation confusing.

---

#### documentation_inconsistency

**Description:** Inconsistent availability information for debugging commands

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/features.md`

**Details:**
extensions.md provides detailed availability for debugging commands:
'BREAK: CLI (command form), Curses (Ctrl+B), Tk (UI controls)'
'STEP: CLI (command form), Curses (Ctrl+T/Ctrl+K), Tk (UI controls)'
'STACK: CLI (command form), Curses (menu access), Tk (stack window)'

features.md only states:
'Breakpoints - Set/clear breakpoints (UI-dependent)'
'Step execution - Execute one line at a time (UI-dependent)'
'Stack viewer - View execution stack (UI-dependent)'

features.md lacks the specific UI availability details that extensions.md provides.

---

#### documentation_inconsistency

**Description:** Inconsistent file handling description between CLI/Tk/Curses and Web UI

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
compatibility.md states: 'IMPORTANT: File handling differs between UIs:' and then describes 'CLI, Tk, and Curses UIs - Real filesystem access' vs 'Web UI - In-memory virtual filesystem'

However, the Web UI section states files are 'stored in Python-side memory (not browser localStorage)' which implies server-side storage, not client-side. This contradicts the typical understanding of 'in-memory virtual filesystem' in a web context, which would usually mean client-side browser memory.

The architecture needs clarification: Is the Web UI using server-side Python memory (requiring a persistent server connection) or client-side browser memory?

---

#### documentation_inconsistency

**Description:** Unclear status of 'compile-then-execute' architecture claim

**Affected files:**
- `docs/help/mbasic/architecture.md`

**Details:**
architecture.md states in Overview: 'Unlike traditional BASIC interpreters that re-parse code on each execution, MBASIC uses a modern **compile-then-execute** architecture for better performance.'

However, the document then describes 'Interpreter Mode (Current Implementation)' which 'Executes AST directly' with 'Runtime Execution'. The term 'compile-then-execute' typically implies ahead-of-time compilation to bytecode or native code, but the document describes parse-once-execute-many, which is still interpretation.

The 'Compiler Backend (Semantic Analyzer)' section clarifies that actual compilation is 'Not implemented (future work)', making the initial 'compile-then-execute' claim potentially misleading. It should say 'parse-then-execute' or 'parse-once-execute-many' to be more accurate.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut for deleting lines

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/editing.md`

**Details:**
feature-reference.md states 'Delete Lines (Ctrl+D)' under File Operations, but editing.md shows 'Quick Delete (Ctrl+D)' under Deleting Lines section. Both describe the same feature but categorize it differently - one as a file operation, one as an editing operation.

---

#### documentation_inconsistency

**Description:** Missing cross-reference to string allocation documentation

**Affected files:**
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`
- `docs/help/mbasic/index.md`

**Details:**
The index.md lists 'String Allocation and Garbage Collection' under Implementation Details, but this is a deep technical document about CP/M MBASIC internals. The index doesn't clarify that this is historical/reference material about the original MBASIC, not necessarily the current implementation's behavior.

---

#### documentation_inconsistency

**Description:** Settings commands not listed in CLI index

**Affected files:**
- `docs/help/ui/cli/settings.md`
- `docs/help/ui/cli/index.md`

**Details:**
cli/settings.md documents SHOWSETTINGS and SETSETTING commands in detail, but cli/index.md does not list these under 'Common Commands' or anywhere else. Users may not discover these features.

---

#### documentation_inconsistency

**Description:** Placeholder documentation not completed

**Affected files:**
- `docs/help/ui/common/running.md`

**Details:**
running.md is marked as 'PLACEHOLDER - Documentation in progress' but is referenced from multiple other documents including cli/index.md and curses/editing.md. This creates broken documentation flow.

---

#### documentation_inconsistency

**Description:** Conflicting information about Find/Replace availability

**Affected files:**
- `docs/help/ui/cli/find-replace.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/find-replace.md states 'The CLI backend does not have built-in Find/Replace commands' and recommends using Tk UI for this feature.

curses/feature-reference.md states 'Find/Replace (Not yet implemented)' and references a find-replace.md file that should exist at docs/help/ui/curses/find-replace.md.

This suggests:
1. CLI intentionally doesn't have Find/Replace (design decision)
2. Curses plans to have it but doesn't yet (implementation gap)
3. The referenced curses find-replace.md file may not exist

---

#### documentation_inconsistency

**Description:** Unclear applicability of historical implementation details

**Affected files:**
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`

**Details:**
The string-allocation-and-garbage-collection.md document provides extensive detail about CP/M era MBASIC's implementation, including:
- 'O(n²) Time Complexity'
- Specific 8080 assembly code
- Performance tables for 2 MHz 8080
- 'Implementation for Modern Emulation' section

However, it's unclear whether:
1. This Python implementation replicates the O(n²) algorithm for compatibility
2. This is purely historical reference material
3. The modern implementation uses different algorithms

The document states 'Understanding this system is crucial for: Accurate emulation of period systems' but doesn't clarify if THIS implementation is such an emulation or a modern reimplementation.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/files.md`

**Details:**
quick-reference.md uses mixed notation:
- Sometimes: '**^F** (Ctrl+F)' with explanation
- Sometimes: '**Ctrl+R**' without caret notation
- Sometimes: '**Menu only**' for features without shortcuts

files.md consistently uses: '**^V**', '**^O**', '**^N**'

The documentation should use consistent notation throughout (either always show both ^X and Ctrl+X, or pick one standard).

---

#### documentation_inconsistency

**Description:** Conflicting information about List Program feature

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md states under 'Program Management': '**Menu only** | List program'

But index.md does not mention this feature at all in its list of available features.

running.md mentions: 'Access through the menu bar to list the program to the output window.'

This suggests the feature exists but is inconsistently documented across pages.

---

#### documentation_inconsistency

**Description:** Variables window keyboard shortcuts inconsistency

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
variables.md documents these keys in the Variables Window:
- 's' - Cycle sort mode
- 'd' - Toggle sort direction
- 'f' - Cycle filter mode
- '/' - Search for variable

But quick-reference.md shows the same keys with different capitalization and no mention of whether they work only in the variables window or globally:
'| Key | Action |
| **s** | Cycle sort mode (Accessed → Written → Read → Name) |'

The context (whether these are global or window-specific) should be clarified in quick-reference.md.

---

#### documentation_inconsistency

**Description:** Find and Replace keyboard shortcut documentation conflict

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
features.md states:
'**Find text (Ctrl+F):**
- Opens Find dialog with search options'
'**Replace text (Ctrl+H):**
- Opens combined Find/Replace dialog'
'**Note:** Ctrl+F opens the Find dialog. Ctrl+H opens the Find/Replace dialog which includes both Find and Replace functionality.'

But feature-reference.md shows:
'### Find/Replace (Ctrl+F / Ctrl+H)'
And lists both as separate features with the same shortcuts.

The note in features.md suggests Ctrl+H opens a combined dialog, but the heading suggests they are separate. This needs clarification.

---

#### documentation_inconsistency

**Description:** Variable editing capability differs between UIs but not clearly stated

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
curses/variables.md states:
'### Current Status
⚠️ **Partial Implementation**: Variable editing in Curses UI is limited.'
'### What Doesn't Work Yet
- Cannot edit values directly in window
- No inline editing
- Must use immediate mode to modify'

tk/feature-reference.md states:
'### Edit Variable Value
Double-click a variable in the Variables window to edit its value during debugging.'

This is a significant feature difference between UIs that should be highlighted in the comparison tables in docs/help/ui/index.md.

---

#### documentation_inconsistency

**Description:** Placeholder syntax inconsistency for keyboard shortcuts

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/index.md`

**Details:**
features.md uses placeholder syntax like:
'Press {{kbd:smart_insert}}'
'Or press {{kbd:toggle_breakpoint}}'
'Shows all variables with:'

index.md uses the same syntax:
'**Smart Insert ({{kbd:smart_insert}})**'
'**Variables Window ({{kbd:toggle_variables}})**'

But getting-started.md shows:
'| {{kbd:run_program}} | Run program |'

These placeholders suggest there's a template system that should replace them with actual key names, but it's unclear if this is working correctly or if the documentation is showing raw template syntax. This needs verification.

---

#### documentation_inconsistency

**Description:** Settings documentation exists for Curses but referenced for Tk

**Affected files:**
- `docs/help/ui/curses/settings.md`
- `docs/help/ui/tk/settings.md`

**Details:**
curses/settings.md provides detailed documentation about the settings widget with keyboard shortcut 'Ctrl+,'.

tk/settings.md is referenced in tk/index.md: '[Settings & Configuration](settings.md)'

But there is no tk/settings.md file in the provided documentation. Either:
1. The file is missing
2. The link should point to curses/settings.md
3. Tk uses a different settings interface that needs documentation

---

#### documentation_inconsistency

**Description:** Contradictory information about auto-save functionality in Web UI

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/features.md`

**Details:**
web/getting-started.md states:
'**Note:** The Web UI uses browser downloads for saving files to your computer. Auto-save to browser localStorage is planned for a future release.'

And later: '**Solution:** Auto-save to localStorage is planned for a future release. Currently, you need to manually save your programs using File → Save.'

But web/features.md under 'Local Storage' section states:
'**Currently Implemented:**
- Programs stored in browser localStorage

**Automatic Saving (Planned):**
- Saves to browser storage
- Every 30 seconds'

This creates confusion: are programs currently stored in localStorage or not? The 'Automatic Saving' being planned suggests manual localStorage storage exists, but getting-started.md says localStorage auto-save is planned.

---

#### documentation_inconsistency

**Description:** Inconsistent information about breakpoint setting methods

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
web/debugging.md states:
'### Currently Implemented

1. Use **Run → Toggle Breakpoint** menu option
2. Enter the line number when prompted
3. A visual indicator appears in the editor
4. Use **Run → Clear All Breakpoints** to remove all'

web/getting-started.md states:
'### Breakpoints

Set breakpoints to pause execution at specific lines:
1. Use **Run → Toggle Breakpoint** menu option
2. Enter the line number
3. Program will pause when reaching that line
4. Use **Run → Clear All Breakpoints** to remove all'

Both describe the same feature, but debugging.md mentions 'A visual indicator appears in the editor' while getting-started.md does not mention this visual feedback. This should be consistent.

---

#### documentation_inconsistency

**Description:** Tk documentation describes features as available but settings.md says they are planned

**Affected files:**
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/settings.md`

**Details:**
tk/settings.md clearly states at the top:
'**Implementation Status:** The Tk (Tkinter) desktop GUI is planned to provide the most comprehensive settings dialog. **The features described in this document represent planned/intended implementation and are not yet available.**'

However, tk/tips.md and tk/workflows.md describe features as if they are currently available:

tk/tips.md:
'Use **Ctrl+I** (Smart Insert) to insert blank lines under each section without calculating line numbers!'
'Press **Ctrl+K** (Toggle Stack) while stepping through nested loops'
'Press **Ctrl+E** (Renumber)'

tk/workflows.md:
'Press **Ctrl+N** (New)'
'Press **Ctrl+I** (Smart Insert) to insert blank line'
'Press **Ctrl+R** (Run) to test'
'Press **Ctrl+S** (Save)'
'Press **Ctrl+W** to open Variables window'
'Press **Ctrl+E** (Renumber)'

These documents should clarify whether these features are currently implemented or planned.

---

#### documentation_inconsistency

**Description:** Variable Inspector section contradicts itself about implementation status

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
web/debugging.md states:
'## Variable Inspector

**Implementation Status:** Basic variable viewing via Debug menu is currently available. The detailed variable inspector panels, watch expressions, and interactive editing features described below are **planned for future releases** and not yet implemented.'

But then immediately describes 'Variables Panel (Planned)' with detailed features. The section title 'Variable Inspector' suggests it exists, but the content says it's planned. This is confusing - it should either be titled 'Variable Inspector (Planned)' or the implementation status note should be more prominent.

---

#### documentation_inconsistency

**Description:** Inconsistent methods for opening Settings dialog

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
settings.md states:
"**Methods:**
1. Click the **⚙️ Settings** icon in the navigation bar
2. Click menu → Settings"

But web-interface.md only mentions:
"### Edit Menu
- **Settings** - Configure auto-numbering, case handling, and other interpreter options"

No mention of a ⚙️ Settings icon in the navigation bar in web-interface.md. The two documents describe different UI access patterns.

---

#### documentation_inconsistency

**Description:** Conflicting information about calendar programs

**Affected files:**
- `docs/library/games/index.md`
- `docs/library/utilities/index.md`

**Details:**
games/index.md states:
"### Calendar
Year-long calendar display program from Creative Computing
**Source:** Creative Computing, Morristown, NJ
**Year:** 1979
**Tags:** calendar, display
**Note:** A simpler calendar utility is also available in the [Utilities Library](../utilities/index.md#calendar)"

But utilities/index.md states:
"### Calendar
Simple calendar generator - prints a formatted calendar for any month/year (1900-2099)
**Source:** Dr Dobbs Nov 1981
**Year:** 1982
**Tags:** date, calendar, utility
**Note:** A different calendar program is also available in the [Games Library](../games/index.md#calendar)"

The games version claims the utilities version is "simpler", but the utilities version claims it's just "different". Also, different sources (Creative Computing vs Dr Dobbs) and years (1979 vs 1982) are listed.

---

#### documentation_inconsistency

**Description:** QUICK_REFERENCE.md is described as Curses UI specific but doesn't clearly state this in its title or opening

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`
- `docs/user/README.md`

**Details:**
QUICK_REFERENCE.md title is 'MBASIC Curses IDE - Quick Reference Card' which is clear, but README.md lists it under 'Reference Documentation' without the UI-specific qualifier in the description. The description says 'Quick command reference (Curses UI specific)' but this creates ambiguity about whether there are quick references for other UIs.

---

#### documentation_inconsistency

**Description:** Missing cross-reference between case handling guide and settings documentation

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
CASE_HANDLING_GUIDE.md mentions 'SETTINGS_AND_CONFIGURATION.md - Complete settings reference' in its 'See Also' section, but SETTINGS_AND_CONFIGURATION.md is not present in the provided documentation files. This creates a broken reference that users cannot follow.

---

#### documentation_inconsistency

**Description:** Duplicate installation documentation with redirect pattern

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/INSTALLATION.md`

**Details:**
INSTALLATION.md exists as a redirect file pointing to INSTALL.md:
'> **Note:** This is a redirect file. For complete installation instructions, see [INSTALL.md](INSTALL.md).'

While this is intentional for compatibility, it creates potential confusion. The README.md lists both files separately under 'Getting Started' without explaining the relationship:
- **[INSTALL.md](INSTALL.md)** - Installation guide
- **[INSTALLATION.md](INSTALLATION.md)** - Alternative installation instructions

The description 'Alternative installation instructions' is misleading since it's actually a redirect.

---

#### documentation_inconsistency

**Description:** keyboard-shortcuts.md listed but not provided

**Affected files:**
- `docs/user/README.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
README.md lists 'keyboard-shortcuts.md' under Reference Documentation:
- **[keyboard-shortcuts.md](keyboard-shortcuts.md)** - Keyboard shortcuts reference (Curses UI specific)

However, this file was not provided in the documentation set. This could indicate either a missing file or an outdated README entry.

---

#### documentation_inconsistency

**Description:** sequential-files.md listed but not provided

**Affected files:**
- `docs/user/README.md`
- `docs/user/sequential-files.md`

**Details:**
README.md lists 'sequential-files.md' under File Operations:
- **[sequential-files.md](sequential-files.md)** - Sequential file I/O guide

However, this file was not provided in the documentation set. This could indicate either a missing file or an outdated README entry.

---

#### documentation_inconsistency

**Description:** Case handling guide claims to document two systems but only documents one

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`

**Details:**
CASE_HANDLING_GUIDE.md states:
'MBASIC gives you **two separate case handling systems**:
1. **Variable Case Handling** - Controls how variable names are displayed
2. **Keyword Case Handling** - Controls how keywords like PRINT, FOR, IF are displayed'

The guide then documents both systems extensively. However, the guide doesn't mention if there are any other case-sensitive elements in MBASIC (like file names, string literals, etc.) that might confuse users about what 'case handling' covers.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Variables window

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states 'The Variables & Resources window (Ctrl+W in TK UI)' but TK_UI_QUICK_START.md lists 'Ctrl+W' as 'Show/hide Variables window' without mentioning 'Resources'. The window name is inconsistent - one doc calls it 'Variables & Resources window' while the other calls it 'Variables window'.

---

#### documentation_inconsistency

**Description:** Conflicting information about Find/Replace availability in Web UI

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md states Find/Replace is 'Tk UI only' in the keyboard shortcuts table. However, UI_FEATURE_COMPARISON.md shows Find/Replace for Web UI as '⚠️' (partially implemented or planned) with note 'Tk: implemented, Web: planned'. This is inconsistent - one says Tk only, the other says Web is planned.

---

#### documentation_inconsistency

**Description:** Inconsistent boolean value format in SET command examples

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md shows inconsistent boolean formats:
- In 'Quick Start' section: 'SET "editor.auto_number" true' (no quotes)
- In 'Type Conversion' section: 'Booleans: true or false (lowercase, no quotes in commands; use true/false in JSON files)'
- In 'SET Command' examples: 'SET "editor.show_line_numbers" true' (no quotes)
But then states 'use true/false in JSON files' implying commands are different, yet all examples show no quotes. The distinction between command and JSON format for booleans is unclear.

---

#### documentation_inconsistency

**Description:** Contradictory information about CLI save functionality

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md shows 'Save (interactive)' as '❌' for CLI with note 'Ctrl+S prompts for filename', but then in the 'Limitations' section for CLI states 'No interactive save prompt (must use SAVE "filename" command)'. These statements contradict each other - one implies Ctrl+S works, the other says there's no interactive save prompt.

---

#### documentation_inconsistency

**Description:** Incomplete cross-reference to non-existent documentation

**Affected files:**
- `docs/user/sequential-files.md`

**Details:**
sequential-files.md 'See Also' section references '[File Format Compatibility](FILE_FORMAT_COMPATIBILITY.md)' but this file is not included in the provided documentation set. This creates a broken reference.

---

### 🟢 Low Severity

#### code_vs_comment_conflict

**Description:** InputStatementNode docstring has confusing/contradictory explanation of semicolon behavior

**Affected files:**
- `src/ast_nodes.py`

**Details:**
The docstring states:
"Note: The semicolon has different meanings depending on its position:
- After a prompt string: INPUT "prompt"; var  → shows "prompt? " (question mark still appears)
- Immediately after INPUT keyword: INPUT; var → suppresses "?" completely (no prompt at all)
The suppress_question field is True only for the second case (INPUT; without prompt),
not for the first case (prompt with semicolon still shows "?")."

This is internally contradictory - it says "prompt with semicolon still shows '?'" but also says the semicolon after prompt shows "prompt? ". The explanation conflates two different uses of semicolon but the field suppress_question only tracks one case.

---

#### code_vs_comment_conflict

**Description:** CallStatementNode has arguments field but docstring says it's not parsed

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode docstring states:
"Note: The 'arguments' field exists for potential future compatibility with
other BASIC dialects (e.g., CALL ROUTINE(args)), but extended syntax is
not currently supported by the parser. Standard MBASIC 5.21 only accepts
a single address expression."

This creates confusion - the field exists in the dataclass but is documented as unused. If it's not parsed, it should either be removed or the comment should clarify what value it will have (empty list?).

---

#### code_vs_comment_conflict

**Description:** VariableNode docstring explanation of type_suffix fields is confusing

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode has this comment:
"Type suffix handling:
- type_suffix: The actual suffix ($, %, !, #) - may be explicit or inferred
- explicit_type_suffix: Whether type_suffix came from source code (True) or
  was inferred from a DEF statement (False)

Both fields work together: type_suffix stores the value, explicit_type_suffix
tracks its origin. This is needed to regenerate source code accurately."

The explanation is circular and redundant. It says type_suffix "may be explicit or inferred" then immediately explains explicit_type_suffix tracks whether it's explicit or inferred. The comment could be simplified.

---

#### documentation_inconsistency

**Description:** Inconsistent comment style for statement nodes

**Affected files:**
- `src/ast_nodes.py`

**Details:**
Most statement nodes have docstrings with "Syntax:" and "Example:" sections (e.g., EraseStatementNode, MidAssignmentStatementNode, ChainStatementNode), but many others don't (e.g., PrintStatementNode, LetStatementNode, ForStatementNode). This creates inconsistent documentation quality across the codebase.

---

#### documentation_inconsistency

**Description:** Comment references line numbers that may not be accurate

**Affected files:**
- `src/ast_nodes.py`

**Details:**
Near SetSettingStatementNode definition, there's a comment:
"# NOTE: SetSettingStatementNode and ShowSettingsStatementNode are defined
# in the "Settings Commands" section below (see line ~980+)."

This appears before the actual definitions, but the line reference (~980+) may become inaccurate as the file is edited. Line number references in comments are fragile.

---

#### code_vs_comment_conflict

**Description:** RenumStatementNode docstring shows parameter omission syntax but doesn't explain defaults clearly

**Affected files:**
- `src/ast_nodes.py`

**Details:**
RenumStatementNode docstring shows:
"Parameters can be omitted using commas:
    RENUM 100,,20  - new_start=100, old_start=0 (default), increment=20
    RENUM ,50,20   - new_start=10 (default), old_start=50, increment=20"

But the field definitions show:
"new_start: 'ExpressionNode' = None  # New starting line number (default 10)
old_start: 'ExpressionNode' = None  # First old line to renumber (default 0)
increment: 'ExpressionNode' = None  # Increment (default 10)"

The defaults are documented in two places with the same values, but it's unclear whether None means "use default" or whether the parser/interpreter handles the defaults. This could lead to confusion.

---

#### code_vs_comment

**Description:** Comment about EOF() checking ^Z says 'read(1) returns bytes in binary mode, so next_byte[0] gives the byte value' but this is implementation detail that could be clearer

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 729-730 comment: "# Peek at next byte to check for ^Z or EOF
# read(1) returns bytes in binary mode, so next_byte[0] gives the byte value"
The comment explains the indexing but doesn't clarify that this only works because the file was opened in binary mode ('rb'). The mode check at line 726 (if file_info['mode'] == 'I') ensures this, but the connection isn't explicit.

---

#### documentation_inconsistency

**Description:** Docstring for INPUT() method describes BASIC syntax with # prefix but Python call syntax without it, potentially confusing

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Lines 869-877:
"INPUT$ - Read num characters from keyboard or file.
(Method name is INPUT since Python doesn't allow $ in names)

BASIC syntax:
    INPUT$(n) - read n characters from keyboard
    INPUT$(n, #filenum) - read n characters from file

Python call syntax (from interpreter):
    INPUT(n) - read n characters from keyboard
    INPUT(n, filenum) - read n characters from file (no # prefix)"
The distinction between BASIC syntax and Python call syntax is documented, but it's unclear whether the # is stripped by the parser or if this is just documentation. Similar functions like EOF() use file_num parameter without mentioning # prefix removal.

---

#### code_vs_comment

**Description:** Comment about trailing_minus_only says it 'ALWAYS adds a char' but this is implementation detail not clearly stated in the field spec parsing

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 343 comment: "# Add sign to content width (trailing_minus_only ALWAYS adds a char, - or space)"
This behavior is implemented correctly at lines 371-373, but the parse_numeric_field() method doesn't document this distinction between trailing_sign (which adds + or -) and trailing_minus_only (which adds - or space). The comment assumes knowledge not present in the spec structure.

---

#### code_vs_documentation

**Description:** EOF() docstring mentions 'binary input files (mode I)' but doesn't explain what mode 'I' represents or how it differs from other modes

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Lines 714-719:
"Test for end of file.

Returns -1 if at EOF, 0 otherwise
Note: For binary input files (mode 'I'), respects ^Z (ASCII 26) as EOF marker (CP/M style).
Text mode files and output files use standard Python EOF detection."
The docstring uses 'mode I' without explaining it's a BASIC file mode designation. Other file operations in the codebase would need to set this mode, but there's no cross-reference to where modes are defined or set.

---

#### code_vs_comment

**Description:** Comment about file_info access pattern references EOF() method but the pattern is used in multiple methods

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Lines 895-897:
"# self.runtime.files[file_num] returns a dict with 'handle', 'mode', 'eof' keys
# Extract the file handle from the file_info dict to perform read operations
# (see EOF() method for the same access pattern)"
This comment in INPUT() references EOF() as an example, but LOC(), LOF(), and other methods use the same pattern. The comment could be more general or the pattern could be extracted to a helper method.

---

#### code_vs_documentation

**Description:** ProgramManager.merge_from_file() not mentioned in FILE I/O ARCHITECTURE section

**Affected files:**
- `src/editing/manager.py`

**Details:**
The FILE I/O ARCHITECTURE section lists:
"1. FileIO (src/file_io.py) - For interactive BASIC commands (LOAD/SAVE/MERGE/KILL)"

But ProgramManager has merge_from_file() method which is a direct file operation like load_from_file() and save_to_file(). The architecture documentation doesn't explain how MERGE command relates to ProgramManager.merge_from_file() vs FileIO abstraction.

---

#### code_vs_comment

**Description:** InMemoryFileHandle.flush() comment describes different semantics than typical file flush

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The flush() method comment states:
"Note: This calls StringIO/BytesIO flush() which are no-ops.
Content is only saved to the virtual filesystem on close().
This differs from file flush() semantics where flush() typically
persists buffered writes. For in-memory files, all writes are
already in memory, so flush() has no meaningful effect."

This is accurate but could be misleading. The comment correctly describes the behavior, but users expecting standard file flush() semantics (persist to storage) won't get that. This is a design choice, not a bug, but worth noting for API compatibility.

---

#### code_vs_documentation

**Description:** SandboxedFileSystemProvider security note about user_id validation

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The docstring states:
"Per-user isolation via user_id keys in class-level storage
IMPORTANT: Caller must ensure user_id is securely generated/validated
to prevent cross-user access (e.g., use session IDs, not user-provided values)"

This is a security warning in the documentation, but there's no code enforcement. The class accepts any user_id string without validation. This is a documentation-only warning, which could be missed. Consider adding a code comment at __init__ or a validation method.

---

#### documentation_inconsistency

**Description:** Inconsistent description of which UI uses which filesystem abstraction

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py states:
"Implementations:
  * RealFileIO: Direct filesystem access to disk (TK, Curses, CLI)
  * SandboxedFileIO: Python server memory virtual filesystem (Web UI)"

And:
"Implementations:
  * LocalFileSystemProvider: Direct filesystem access (TK, Curses, CLI)
  * SandboxedFileSystemProvider: Python server memory (Web UI)"

But src/filesystem/base.py states:
"Different UIs can provide different implementations:
- RealFileSystemProvider: Direct filesystem access (CLI, Tk, Curses)
- SandboxedFileSystemProvider: In-memory or restricted access (Web)"

The naming is inconsistent: RealFileIO vs LocalFileSystemProvider. Also, one says "TK" and another says "Tk" (capitalization).

---

#### code_vs_comment

**Description:** Docstring says 'waiting_for_input' state allows immediate mode, but implementation checks input_prompt attribute instead of state name

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Class docstring states:
"CAN execute when waiting for input:
- 'waiting_for_input' - Program is waiting for INPUT."

But can_execute_immediate() implementation checks:
"return (self.runtime.halted or
        state.error_info is not None or
        state.input_prompt is not None)"

The code checks 'state.input_prompt is not None' rather than checking for a 'waiting_for_input' status value. The docstring implies there's a status enum value called 'waiting_for_input', but the code uses a different mechanism (checking if input_prompt attribute exists).

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for interpreter states between docstring and implementation

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Class docstring lists states as strings:
"- 'idle' - No program loaded
- 'paused' - User hit Ctrl+Q (stop)
- 'at_breakpoint' - Hit breakpoint
- 'done' - Program finished
- 'error' - Program encountered error
- 'running' - Program is executing
- 'waiting_for_input' - Program is waiting for INPUT"

But can_execute_immediate() doesn't check these state strings. Instead it checks:
"return (self.runtime.halted or
        state.error_info is not None or
        state.input_prompt is not None)"

The docstring implies a state machine with named states, but the implementation uses boolean flags and attribute presence checks. The state names in the docstring may not correspond to actual state values in the interpreter.

---

#### code_vs_comment

**Description:** Function return type annotation uses tuple[str, bool] which requires Python 3.9+, but no version requirement documented

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
In sanitize_and_clear_parity():
"def sanitize_and_clear_parity(text: str) -> tuple[str, bool]:"

This uses the built-in tuple type for type hints, which requires Python 3.9+. Earlier versions require 'from typing import Tuple' and 'Tuple[str, bool]'. No Python version requirement is documented in the module docstring or comments.

---

#### code_vs_comment

**Description:** Docstring example shows clearing parity from chr(193) results in 'A', but chr(194) should result in 'B' not 'AB'

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
In clear_parity_all() docstring:
">>> clear_parity_all(chr(193) + chr(194))  # Characters with bit 7 set
'AB'"

This is actually correct: chr(193) & 0x7F = 65 ('A'), chr(194) & 0x7F = 66 ('B'). The example is accurate. This is not an inconsistency.

---

#### code_vs_comment

**Description:** Comment says 'bare except' but exception handling is actually specific

**Affected files:**
- `src/interactive.py`

**Details:**
Line ~870 in _read_char():
Comment: "# Fallback for non-TTY/piped input or any terminal errors (bare except)"
Code: "except:"

The comment acknowledges it's a bare except, but describes it as intentional for terminal errors. This is technically consistent but the comment could be clearer that it's catching all exceptions intentionally.

---

#### code_vs_comment

**Description:** Docstring says 'Delegates to ui_helpers.delete_lines_from_program()' but doesn't mention it returns deleted line numbers

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_delete() docstring (line ~490):
"Delegates to ui_helpers.delete_lines_from_program() which handles:
- Parsing the delete range syntax
- Removing lines from program manager
- Updating runtime statement table if program is loaded"

But in the code (line ~510):
"# delete_lines_from_program returns list of deleted line numbers (not used here)
delete_lines_from_program(self, args, self.program_runtime)"

The docstring doesn't mention the return value, but the code comment does. Minor documentation incompleteness.

---

#### documentation_inconsistency

**Description:** Module docstring says 'MBASIC 5.21' but startup message says 'MBASIC-2025'

**Affected files:**
- `src/interactive.py`

**Details:**
Module docstring (line 2):
"MBASIC 5.21 Interactive Command Mode"

But in start() method (line ~180):
print("MBASIC-2025 - Modern MBASIC 5.21 Interpreter")

Inconsistent branding between internal documentation and user-facing messages.

---

#### code_vs_comment_conflict

**Description:** Comment references 'help text' about GOTO/GOSUB being discouraged, but no help text is visible in this code section

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states: 'GOTO/GOSUB in immediate mode are discouraged (see help text)'

The help text being referenced is not present in the provided code, making it impossible to verify if the help text exists or what it actually says about this behavior.

---

#### code_vs_comment_conflict

**Description:** Docstring says 'examine/modify program variables' works for 'stopped OR finished programs', but doesn't clarify if finished programs retain their runtime

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring states: 'If program_runtime exists (from RUN), use it so immediate mode can examine/modify program variables (works for stopped OR finished programs)'

The code checks 'if self.program_runtime is not None' but doesn't show whether program_runtime is cleared when a program finishes normally (vs being stopped). The comment implies it persists for finished programs, but this behavior isn't evident in the code shown.

---

#### code_vs_comment

**Description:** Comment on skip_next_breakpoint_check field describes behavior that doesn't match the actual implementation timing

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: 'Set to True WHEN halting at a breakpoint (set during the halt). On next execution, if still True, allows stepping past the breakpoint once, then clears itself to False.'

But the code in tick_pc() sets skip_next_breakpoint_check = True AFTER halting (after 'return self.state'), not 'during the halt'. The flag is set, then execution returns, then on next tick it's checked and cleared. The comment's phrasing 'set during the halt' is slightly misleading about the exact timing.

---

#### code_vs_comment

**Description:** Comment in current_statement_char_end property describes fallback behavior that may not match actual line_text_map usage

**Affected files:**
- `src/interpreter.py`

**Details:**
Property docstring says: 'For the last statement on a line, uses line_text_map to get actual line length (if available), otherwise falls back to stmt.char_end.'

The code does: 'if pc.line_num in self._interpreter.runtime.line_text_map: line_text = self._interpreter.runtime.line_text_map[pc.line_num]; return len(line_text)'

But there's no explicit check that this is 'the last statement on a line' before using line_text_map. The code uses line_text_map whenever there's no next statement AND line_text_map has an entry, but doesn't verify this is actually the last statement. The comment implies a more specific condition than the code implements.

---

#### documentation_inconsistency

**Description:** Comment mentions 'OLD EXECUTION METHODS REMOVED' and references src/version.py for internal version tracking, but this file is not shown in the provided code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment block says: 'Note: The project has an internal implementation version (tracked in src/version.py) which is separate from the MBASIC 5.21 language version being implemented. Old methods: run_from_current(), _run_loop(), step_once() (removed)'

This references src/version.py which is not included in the provided source files, making it impossible to verify the version tracking claim or understand the versioning scheme.

---

#### code_vs_comment

**Description:** Comment in _execute_next_single describes validation logic but uses slightly different wording than the actual error messages

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: 'Validate that this FOR loop is on top of the stack (innermost control structure). This prevents errors like: FOR X / FOR Y / NEXT X (skipping Y)'

But the error messages generated are more specific: 'NEXT {var_name} without FOR - found FOR {top_var} loop instead (improper nesting)' or 'NEXT {var_name} without FOR - found WHILE loop instead (improper nesting)'

The comment's example 'FOR X / FOR Y / NEXT X (skipping Y)' doesn't match the actual error message format, which would say 'NEXT X without FOR - found FOR Y loop instead (improper nesting)'. Minor wording inconsistency.

---

#### code_vs_comment

**Description:** INPUT statement comment describes state machine variables but doesn't mention input_file_number

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1343 states:
"# Set input prompt - execution will pause
# Sets: input_prompt (prompt text), input_variables (var list),
#       input_file_number (None for keyboard input, file # for file input)"

This comment correctly documents input_file_number, but the earlier state machine description at line ~1310 only mentions:
"2. Otherwise: Set state.input_prompt, input_variables, input_file_number and return (pauses execution)"

The documentation is consistent, but the initial state machine description could be more explicit about what input_file_number represents.

---

#### code_vs_comment

**Description:** OPTION BASE comment claims strict enforcement but doesn't mention what happens with implicit arrays created before OPTION BASE

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1267 states:
"MBASIC 5.21 restrictions (strictly enforced):
- OPTION BASE can only be executed once per program run
- Must be executed BEFORE any arrays are dimensioned (implicit or explicit)
- Violating either condition raises 'Duplicate Definition' error"

Code at line ~1283 checks:
if len(self.runtime._arrays) > 0:
    raise RuntimeError("Duplicate Definition")

The comment correctly states the restriction, but doesn't clarify the implementation detail that implicit array creation (like A(5)=10 without prior DIM) also populates runtime._arrays and would trigger this error. The note at line ~1287 does mention this, but it's buried in implementation details rather than the main restriction list.

---

#### code_vs_comment

**Description:** CLOSE statement comment claims silent ignore of unopened files but doesn't document this is MBASIC-compatible behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1747 states:
"# Silently ignore closing unopened files (like MBASIC)"

This is good documentation, but it's only mentioned in a code comment, not in the docstring. The docstring should mention this behavior since it's a deliberate compatibility choice that differs from typical error handling.

---

#### code_vs_comment

**Description:** Comment in evaluate_binaryop mentions 'extended characters could differ if using latin-1 encoding' but LSET/RSET explicitly use latin-1 encoding

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_binaryop() for PLUS operator, comment states:
'Also note: len() counts characters, not bytes. For ASCII this is equivalent, but extended characters could differ if using latin-1 encoding.'

However, in execute_lset() and execute_rset(), the code explicitly uses:
buffer_info['buffer'][offset:offset+width] = value.encode('latin-1')

This suggests the system IS using latin-1 encoding for field buffers, making the comment's hypothetical scenario actually real. The comment should acknowledge that latin-1 IS being used in field operations.

---

#### code_vs_comment

**Description:** Comment about debugger_set parameter mentions 'variables window' but no such feature is visible in the code

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_functioncall(), comment states:
'Note: get_variable_for_debugger() and debugger_set=True are used to avoid triggering variable access tracking. This save/restore is internal function call machinery, not user-visible variable access. The tracking system (if enabled) distinguishes between:
- User code variable access (tracked for debugging/variables window)
- Internal implementation details (not tracked)'

The mention of 'variables window' suggests a GUI debugger feature, but this file shows no evidence of such a feature. This may be documentation for a planned feature or from a different codebase.

---

#### Documentation inconsistency

**Description:** Module docstring states GUIIOHandler and WebIOHandler are not exported to avoid dependencies, but gui.py contains a stub implementation with no external dependencies

**Affected files:**
- `src/iohandler/__init__.py`
- `src/iohandler/gui.py`
- `src/iohandler/web_io.py`

**Details:**
__init__.py says: "GUIIOHandler and WebIOHandler are not exported here because they have dependencies on their respective UI frameworks (tkinter, nicegui)."

However, gui.py (GUIIOHandler) is actually a stub with NO external dependencies - it only uses internal buffers and queues. Only web_io.py (WebIOHandler) actually imports nicegui.

---

#### Code vs Comment conflict

**Description:** Backward compatibility comments reference old method names but don't explain migration path

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py has two backward compatibility aliases:
1. print() -> output(): "This method was renamed from print() to output() to avoid conflicts with Python's built-in print function."
2. get_char() -> input_char(): "This method was renamed from get_char() to input_char() for consistency with the IOHandler base class interface."

However, base.py (IOHandler) never had print() or get_char() methods - they were always output() and input_char(). This suggests web_io.py had a different API history than the base class, but the comment implies it's for base class consistency.

---

#### Code vs Documentation inconsistency

**Description:** input_char() fallback behavior on Windows without msvcrt is severely limited but not documented in base class

**Affected files:**
- `src/iohandler/console.py`

**Details:**
console.py input_char() has a fallback for Windows without msvcrt:
"# WARNING: This fallback calls input() which:
# - Waits for Enter key (defeats the purpose of single-char input)
# - Returns the entire line, not just one character
# This is a known limitation when msvcrt is unavailable."

This severe limitation (requiring Enter key for "single character" input) is not mentioned in base.py's input_char() documentation, which simply says it should "Input single character".

---

#### Documentation inconsistency

**Description:** Module docstring references SimpleKeywordCase but doesn't provide import path or explain when to use which

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
keyword_case_manager.py docstring: "Note: This class provides advanced case policies (first_wins, preserve, error) via CaseKeeperTable and is used by parser.py and position_serializer.py. For simpler force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py) which only supports force_lower, force_upper, and force_capitalize."

This mentions SimpleKeywordCase but:
1. Doesn't explain why there are two separate classes for keyword case
2. Doesn't clarify when to use KeywordCaseManager vs SimpleKeywordCase
3. SimpleKeywordCase file is not included in the provided source files, so we cannot verify if it exists or if the reference is outdated

---

#### Code vs Comment conflict

**Description:** input_char() docstring says 'Character input not supported' but implementation returns empty string without explaining if this is temporary or permanent

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py input_char():
"def input_char(self, blocking=True):
    '''Get single character input (for INKEY$, INPUT$).
    ...
    Note: Character input not supported in web UI (always returns empty string).
    '''
    return ''"

The note says it's "not supported" but doesn't clarify:
1. Is this a temporary limitation or architectural decision?
2. Should callers expect this to work in future versions?
3. How should BASIC programs using INKEY$ behave in web UI?

---

#### Documentation inconsistency

**Description:** get_cursor_position() default implementation and console implementation both return (1,1) but console comment suggests it's difficult to implement

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/console.py`

**Details:**
base.py: "Default implementation returns (1, 1). Override for cursor tracking."

console.py: "def get_cursor_position(self) -> tuple[int, int]:
    '''Get current cursor position.
    
    Note: This is difficult to implement portably in console.
    Returns (1, 1) by default.
    '''
    # Getting cursor position in console is complex and platform-specific
    # Return default position
    return (1, 1)"

The console implementation adds a note about difficulty but then does exactly what the base class default does. This suggests either:
1. Console should override but doesn't (implementation gap)
2. The comment is unnecessary (comment outdated)
3. There's a reason console explicitly implements the default (unclear)

---

#### Code vs Comment conflict

**Description:** Docstring claims lexer is for 'MBASIC 5.21 (CP/M era MBASIC-80)' but implementation handles features beyond strict MBASIC 5.21

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring at line 2-6:
"Lexer for MBASIC 5.21 (CP/M era MBASIC-80)
Based on BASIC-80 Reference Manual Version 5.21

Note: MBASIC 5.21 includes Extended BASIC features (e.g., periods in identifiers)."

However, read_identifier() at line 267 includes comment:
"# Subsequent characters can be letters, digits, or periods (in Extended BASIC)"

This suggests periods in identifiers are an 'Extended BASIC' feature, but the docstring claims MBASIC 5.21 already includes Extended BASIC features. The relationship between MBASIC 5.21 and Extended BASIC is unclear.

---

#### Code vs Comment conflict

**Description:** Comment in read_identifier() docstring contradicts the NOTE comment about preprocessing

**Affected files:**
- `src/lexer.py`

**Details:**
Docstring at line 253-260:
"Read an identifier or keyword.
Identifiers can contain letters, digits, and end with type suffix $ % ! #
In MBASIC, $ % ! # are considered part of the identifier.

This lexer parses properly-formed MBASIC 5.21 which requires spaces
between keywords and identifiers. Old BASIC with NEXTI instead of NEXT I
should be preprocessed before parsing."

But then at line 303-314, the code handles PRINT# (keyword without space before #), which contradicts the claim that 'properly-formed MBASIC 5.21 requires spaces'. If PRINT#1 is valid MBASIC 5.21, then the docstring is incorrect about space requirements.

---

#### code_vs_comment

**Description:** Inconsistent terminology: 'at_end_of_line' method comment doesn't mention it checks for comment tokens, but parse_line comment says comments are handled separately

**Affected files:**
- `src/parser.py`

**Details:**
at_end_of_line() docstring (line ~130):
"Check if at end of logical line (NEWLINE or EOF)

Note: This method does NOT check for comment tokens (REM, REMARK, APOSTROPHE).
Comments are handled separately in parse_line() where they are parsed as
statements and can be followed by more statements when separated by COLON."

But at_end_of_statement() (line ~145) DOES check for comment tokens:
"A statement ends at:
- End of line (NEWLINE or EOF)
- Statement separator (COLON)
- Comment (REM, REMARK, or APOSTROPHE)"

The distinction between 'end of line' vs 'end of statement' is correct in code, but the comment in parse_line about comments being 'followed by more statements when separated by COLON' is misleading - comments consume the rest of the line.

---

#### code_vs_comment

**Description:** Comment about trailing separator logic is confusing and potentially incorrect

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~1044-1046:
"# Add newline if there's no trailing separator
# Trailing separator means len(separators) == len(expressions)
# (each expression has a separator except the last, which has a trailing separator)"

This comment is confusing. If there are N expressions:
- No trailing separator: N-1 separators (between expressions)
- Trailing separator: N separators (between expressions + one at end)

The condition 'len(separators) < len(expressions)' would be true when separators < expressions, which happens when there's no trailing separator. But the comment's explanation '(each expression has a separator except the last, which has a trailing separator)' is circular and unclear.

---

#### code_vs_comment

**Description:** Incomplete comment in parse_lprint() - comment is cut off mid-sentence

**Affected files:**
- `src/parser.py`

**Details:**
At line ~1118, the comment reads:
"# Add newline if there's no trailing separator
# Trailing separator means len(separators) == len(expressions)"

But the code snippet ends here without showing the rest of the implementation. This appears to be a truncated file, but if this is the actual code, the comment is incomplete and the implementation is missing.

---

#### documentation_inconsistency

**Description:** Docstring claims 'Array dimensions must be constant expressions' but this constraint is not enforced in parse_dim or array subscript parsing

**Affected files:**
- `src/parser.py`

**Details:**
Module docstring (line 10):
"- Array dimensions must be constant expressions"

However, in parse_variable_or_function() (lines ~700+), array subscripts are parsed as general expressions:
"args.append(self.parse_expression())"

There's no validation that these are constant expressions. Either the docstring is incorrect, or the implementation is missing this validation. In actual MBASIC 5.21, DIM statements do require constant dimensions, but array access can use variable subscripts.

---

#### code_vs_comment

**Description:** Comment claims 'name[0] is already lowercase from lexer normalization' but this assumption is not validated

**Affected files:**
- `src/parser.py`

**Details:**
In get_variable_type() method (line ~780):
"# Check DEF type mapping
# name[0] is already lowercase from lexer normalization
first_letter = name[0]"

This assumes the lexer always normalizes to lowercase, but there's no assertion or validation. If the lexer behavior changes or if names come from other sources, this could break. The code should either validate this assumption or document it as a contract with the lexer.

---

#### code_vs_comment

**Description:** Comment about lexer tokenization behavior may be misleading

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() method, comment states:
"# Note: The lexer tokenizes standalone LINE keyword as LINE_INPUT token."

This comment appears in the context of checking for LINE modifier in INPUT statement (e.g., INPUT "prompt";LINE var$). However, it's unclear if this refers to:
1. The LINE keyword when used as a modifier in INPUT statements
2. The separate LINE INPUT statement

The comment says 'standalone LINE keyword' but the code is checking for LINE as a modifier within an INPUT statement, which is not standalone. This could confuse readers about when LINE vs LINE_INPUT tokens are generated.

---

#### code_vs_comment

**Description:** Comment about malformed FOR loops describes behavior that changes semantics

**Affected files:**
- `src/parser.py`

**Details:**
In parse_for() method:

Comment says:
"Note: Some files may have malformed FOR loops like 'FOR 1 TO 100' (missing variable).
We handle this by creating a dummy variable 'I' to allow parsing to continue,
though this changes the semantics and may cause issues if variable I is referenced elsewhere."

This comment acknowledges that the parser changes program semantics to handle malformed input. This is a significant behavior that could lead to silent bugs. The comment correctly warns about this, but it's unclear if this is intentional error recovery or a workaround. The severity is low because the comment does document the issue, but the approach itself (silently changing semantics) is questionable.

---

#### code_vs_comment

**Description:** RESUME statement comment mentions 'RESUME 0' behavior but doesn't explain it's equivalent to plain RESUME

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_resume says:
"# Note: RESUME 0 means 'retry error statement' (interpreter treats 0 and None equivalently)"

This suggests RESUME 0 and RESUME (None) are equivalent, but the comment doesn't clarify if this is standard BASIC behavior or an implementation detail. The code stores the actual value without special handling for 0.

---

#### code_vs_comment

**Description:** WIDTH statement docstring has inconsistent parameter description format

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"Syntax: WIDTH width [, device]

Parses a WIDTH statement that specifies output width for a device.
Both the width and optional device parameters are parsed as expressions.

Args:
    width: Column width expression (typically 40 or 80)
    device: Optional device expression (typically screen or printer)"

The 'Args:' section uses function parameter documentation style, but this is a method that doesn't take these as parameters - they're parsed from tokens. This is misleading documentation format.

---

#### code_vs_comment

**Description:** DATA statement comment describes unquoted string handling but implementation details differ slightly

**Affected files:**
- `src/parser.py`

**Details:**
Comment says:
"Unquoted strings extend until comma, colon, or end of line"

But the code also stops on unknown token types:
else:
    # Unknown token type without string value - stop here
    break

This means unquoted strings can also be terminated by tokens that aren't comma/colon/EOL, which isn't mentioned in the comment.

---

#### internal_inconsistency

**Description:** Inconsistent handling of type suffix extraction across different parse methods

**Affected files:**
- `src/parser.py`

**Details:**
In parse_def_fn:
param_type_suffix = self.get_type_suffix(param_name)
if param_type_suffix:
    param_name = param_name[:-1]  # Remove suffix from name

In parse_line_input:
var_name, type_suffix = self.split_name_and_suffix(var_token.value)

In parse_read:
var_name, type_suffix = self.split_name_and_suffix(var_token.value)

Some methods use get_type_suffix() and manually strip, others use split_name_and_suffix(). This inconsistency suggests one approach may be preferred but not uniformly applied.

---

#### code_vs_comment

**Description:** Comment in _adjust_statement_positions() references 'AssignmentStatementNode' but code uses 'LetStatementNode'

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_let_statement() docstring:
'Note: LetStatementNode represents both explicit LET statements (LET A=5)
and implicit assignments (A=5) in MBASIC. The node name \'LetStatementNode\'
is used consistently throughout the codebase.

In _adjust_statement_positions(), \'AssignmentStatementNode\' was used historically
but has been replaced by \'LetStatementNode\' for consistency.'

The comment acknowledges historical naming but the actual code in _adjust_statement_positions() checks: 'if stmt_type == \'LetStatementNode\''

This is informational rather than a conflict, but the historical reference might confuse readers.

---

#### code_vs_documentation

**Description:** apply_keyword_case_policy() docstring says 'keyword argument is normalized to lowercase internally when needed' but only first_wins policy actually normalizes it

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring: 'Note: The keyword argument is normalized to lowercase internally when needed (e.g., for first_wins policy lookup). Callers may pass keywords in any case.'

Code implementation:
- force_lower: returns keyword.lower()
- force_upper: returns keyword.upper()
- force_capitalize: returns keyword.capitalize()
- first_wins: keyword_lower = keyword.lower() (only policy that creates lowercase version)
- error/preserve: returns keyword.capitalize()

Most policies transform the keyword directly without normalizing to lowercase first. Only first_wins creates a lowercase version for lookup. The docstring overstates the normalization behavior.

---

#### code_vs_comment

**Description:** emit_keyword() docstring says 'keyword: The keyword to emit (normalized lowercase)' but the function doesn't enforce or verify this

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword() docstring:
'Args:
    keyword: The keyword to emit (normalized lowercase)'

But the function implementation:
'def emit_keyword(self, keyword: str, expected_column: Optional[int], node_type: str = "Keyword") -> str:'
    # Get display case from keyword case manager table
    if self.keyword_case_manager:
        keyword_with_case = self.keyword_case_manager.get_display_case(keyword)

The function calls get_display_case(keyword) which presumably expects lowercase, but there's no validation or normalization. If a caller passes uppercase, behavior is undefined.

---

#### code_vs_documentation

**Description:** StatementTable.next_pc() docstring describes sequential execution but doesn't mention that it returns halted PC for invalid input

**Affected files:**
- `src/pc.py`

**Details:**
Docstring: 'Get next PC after given PC (sequential execution)... Returns: Next PC in sequence, or halted PC if at end'

Code implementation:
'try:
    idx = self._keys_cache.index(pc)
    if idx + 1 < len(self._keys_cache):
        return self._keys_cache[idx + 1]
except ValueError:
    # PC not found in table
    pass
return PC.halted_pc()'

The function returns halted PC both when at end AND when PC is not found in table (ValueError). The docstring only mentions the 'at end' case.

---

#### code_vs_comment

**Description:** Comment says '255 bytes (MBASIC 5.21 compatibility - can be overridden)' but there's no override mechanism in the code

**Affected files:**
- `src/resource_limits.py`

**Details:**
In __init__ docstring line 42:
    max_string_length: int = 255,            # 255 bytes (MBASIC 5.21 compatibility - can be overridden)

The comment suggests this can be overridden, but there's no special override mechanism - it's just a regular parameter like all others. The comment is misleading or outdated.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for string length limit across comments

**Affected files:**
- `src/resource_limits.py`

**Details:**
Line 42 comment: '255 bytes (MBASIC 5.21 compatibility - can be overridden)'
Line 242 comment: '255 bytes (MBASIC 5.21 compatibility)'
Line 264 comment: '255 bytes (MBASIC 5.21 compatibility)'
Line 286 comment: '1MB strings (for testing/development - not MBASIC compatible)'

The first comment mentions 'can be overridden' but subsequent comments don't mention this capability, creating inconsistency.

---

#### documentation_inconsistency

**Description:** Module docstring mentions 'runtime' parameter but code examples show 'runtime' without defining what it is

**Affected files:**
- `src/resource_limits.py`

**Details:**
Module docstring lines 8-10:
    # Web UI
    limits = create_web_limits()
    interpreter = Interpreter(runtime, io, limits=limits)

The 'runtime' and 'io' parameters are used in examples but never explained. This could confuse users about what these parameters should be.

---

#### code_vs_comment

**Description:** estimate_size method has fallback for unknown types but comment says 'Default to double'

**Affected files:**
- `src/resource_limits.py`

**Details:**
Lines 138-140:
    else:
        return 8  # Default to double

The comment says 'Default to double' but the method doesn't verify that 8 bytes is actually the size of a double in all contexts. The DOUBLE type is explicitly 8 bytes (line 136), so this is consistent, but the comment could be clearer that this is a fallback for unknown types.

---

#### code_vs_comment

**Description:** Comment in dimension_array() says 'DIM is tracked as both read and write for debugger display purposes' but the rationale is inconsistent with typical read/write semantics

**Affected files:**
- `src/runtime.py`

**Details:**
Comment states:
'Note: DIM is tracked as both read and write for debugger display purposes.
Technically DIM is an allocation/initialization (write-only), but tracking it
as both allows debuggers to show "last accessed" info for unaccessed arrays.'

This is semantically odd - DIM creates/allocates an array (write operation), but doesn't 'read' anything. Tracking it as a read operation just for debugger convenience conflates allocation with access. The comment acknowledges this is 'technically' wrong but justifies it for UI purposes.

---

#### documentation_inconsistency

**Description:** Docstring for get_variable() has inconsistent formatting and unclear fallback behavior description

**Affected files:**
- `src/runtime.py`

**Details:**
The docstring states:
'The token is expected to have 'line' and 'position' attributes.
If these attributes are missing, getattr() fallbacks are used:
- 'line' falls back to self.pc.line_num (or None if PC is halted)
- 'position' falls back to None'

But the actual code uses:
getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None)

The docstring says 'self.pc.line_num (or None if PC is halted)' but doesn't mention the 'if self.pc' check. If self.pc is None, this would fail before checking halted(). The docstring oversimplifies the fallback logic.

---

#### code_vs_comment

**Description:** Comment in push_for_loop() mentions 'Verbose debug logging (only if MBASIC_DEBUG_LEVEL=2)' but the actual debug_log calls use level=2 and level=1, with level=1 described as 'Always log errors' which contradicts 'only if level=2'

**Affected files:**
- `src/runtime.py`

**Details:**
Comment says:
'# Verbose debug logging (only if MBASIC_DEBUG_LEVEL=2)'

But then code has:
debug_log(..., level=2)  # for normal logging
debug_log(..., level=1)  # with comment 'Always log errors'

If level=1 'always logs', it's not 'only if MBASIC_DEBUG_LEVEL=2'. The comment is misleading about when logging occurs.

---

#### documentation_inconsistency

**Description:** Incomplete docstring for get_all_variables() - the example shows 'last_read' and 'last_write' with timestamp fields, but the Returns section doesn't document the timestamp field

**Affected files:**
- `src/runtime.py`

**Details:**
Returns section says:
'- 'last_read': {'line': int, 'position': int, 'timestamp': float} or None
- 'last_write': {'line': int, 'position': int, 'timestamp': float} or None'

But the example shows:
'last_read': {'line': 20, 'position': 5, 'timestamp': 1234.567}

The timestamp field IS documented in the Returns section, so this is actually consistent. However, the docstring is incomplete - it doesn't explain what the timestamp represents (perf_counter value) or its purpose.

---

#### code_vs_comment

**Description:** Inconsistent terminology for statement offset indexing in comments

**Affected files:**
- `src/runtime.py`

**Details:**
In set_breakpoint() docstring:
"Note: offset 0 = 1st statement, offset 1 = 2nd statement, offset 2 = 3rd statement, etc."

In get_gosub_stack() docstring:
"Note: stmt_offset is a 0-based index where 0 = 1st statement, 1 = 2nd statement, etc."

In get_execution_stack() example:
"FOR I at line 100, statement 0 (1st statement)"

All describe the same concept (0-based indexing) but use slightly different phrasing. While not technically incorrect, the variation in explanation style could cause confusion. The phrase '0-based index' is clearer than listing examples.

---

#### documentation_inconsistency

**Description:** get_execution_stack() docstring has redundant explanation about nesting order

**Affected files:**
- `src/runtime.py`

**Details:**
The docstring states twice that entries are in nesting order:
1. "Returns information about all active control flow structures, interleaved in the order they were entered."
2. "The first entry is the outermost (entered first), and the last entry is the innermost (entered most recently)."
3. "Note: The order reflects nesting level based on execution order (when each structure was entered), not source line order."

All three statements convey the same information with slightly different wording, making the documentation unnecessarily verbose.

---

#### code_vs_comment

**Description:** Inconsistent comment style for statement offset documentation

**Affected files:**
- `src/runtime.py`

**Details:**
Throughout the file, statement offset is documented with different comment styles:
1. 'stmt_offset=None'  with comment 'Optional statement offset (0-based index)'
2. 'return_stmt': 0      # Statement offset
3. 'stmt': 0             # Statement offset

Some comments explain it's 0-based, others just say 'Statement offset'. For consistency and clarity, all should mention it's 0-based or reference the convention established elsewhere.

---

#### Code vs Comment conflict

**Description:** load() method comment describes behavior that doesn't match implementation intent

**Affected files:**
- `src/settings.py`

**Details:**
The load() method has this comment:
'Implementation note: Settings are stored in flattened format on disk (e.g., {'editor.auto_number': True}) and save() uses _flatten_settings() to write them. However, load() intentionally does NOT call _unflatten_settings() - it keeps settings in flattened format after loading. This is by design because _get_from_dict() can handle both flattened ('editor.auto_number': True) and nested ({'editor': {'auto_number': True}}) formats. Settings modified via set() will be in nested format, while loaded settings remain flat, but both works correctly in lookups.'

This creates an inconsistent internal state where some settings are flat and some are nested. The comment says this is 'by design' but it's unclear why this mixed state is preferable to consistently unflattening on load.

---

#### Code vs Documentation inconsistency

**Description:** Comments removed for settings that were never added

**Affected files:**
- `src/settings_definitions.py`

**Details:**
src/settings_definitions.py has comments at the end:
'# Note: Tab key is used for window switching in curses UI, not indentation
# Removed editor.tab_size setting as it's not relevant for BASIC

# Note: Line numbers are always shown - they're fundamental to BASIC!
# Removed editor.show_line_numbers setting as it makes no sense for BASIC'

These comments reference removed settings, but there's no evidence in the code that these settings ever existed. The comments suggest they were removed, but they may never have been implemented. This is confusing documentation.

---

#### Documentation inconsistency

**Description:** Module docstring references files that may not exist or have different purposes

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
src/simple_keyword_case.py docstring says:
'For advanced policies (first_wins, preserve, error) via CaseKeeperTable, see KeywordCaseManager (src/keyword_case_manager.py) which is used by parser.py and position_serializer.py.'

However, none of these files (keyword_case_manager.py, parser.py, position_serializer.py) are provided in the source code listing. This creates a documentation reference to non-existent (or at least not-provided) files.

---

#### Code vs Documentation inconsistency

**Description:** Import error handling suggests CursesBackend is optional but doesn't document why or when it's unavailable

**Affected files:**
- `src/ui/__init__.py`

**Details:**
src/ui/__init__.py has:
try:
    from .curses_ui import CursesBackend
    _has_curses = True
except ImportError:
    # Curses UI not available
    _has_curses = False
    CursesBackend = None

The code sets _has_curses flag but never exports it or documents when/why curses might be unavailable. The __all__ list includes 'CursesBackend' unconditionally, which could cause issues if it's None.

---

#### Code vs Comment conflict

**Description:** Comment says 'Emacs-style' but implementation differs from Emacs behavior

**Affected files:**
- `src/ui/auto_save.py`

**Details:**
Module docstring says:
'Provides Emacs-style auto-save functionality:
- Saves to temp files (#filename#) automatically'

The get_autosave_path() method comment also says '# Emacs-style: #filename#'

However, Emacs saves autosave files in the same directory as the original file, while this implementation saves them to a centralized ~/.mbasic/autosave directory. This is not actually Emacs-style behavior.

---

#### Documentation inconsistency

**Description:** UIBackend docstring lists backend types that aren't implemented

**Affected files:**
- `src/ui/base.py`

**Details:**
UIBackend class docstring says:
'Different UIs can implement this interface:
- CLIBackend: Terminal-based REPL (current InteractiveMode)
- GUIBackend: Desktop GUI with visual editor
- MobileBackend: Touch-based mobile UI
- WebBackend: Browser-based interface
- HeadlessBackend: No UI, for batch processing'

However, only CLIBackend is actually implemented in the provided code. The others (GUIBackend, MobileBackend, WebBackend, HeadlessBackend) are mentioned as examples but don't exist. The __init__.py only imports CLIBackend, VisualBackend, TkBackend, and optionally CursesBackend - none of which match the names in the docstring except CLIBackend.

---

#### Code vs Comment conflict

**Description:** _get_from_dict() docstring example doesn't match actual usage pattern

**Affected files:**
- `src/settings.py`

**Details:**
_get_from_dict() docstring says:
'Args:
    key: Dotted key like 'editor.auto_number'
    settings_dict: Nested dict like {'editor': {'auto_number': True}}'

But the load() method comment explicitly states that loaded settings remain in flattened format, not nested format. So settings_dict would actually be {'editor.auto_number': True} for loaded settings, not the nested format shown in the docstring example.

---

#### Code vs Documentation inconsistency

**Description:** The SettingsWidget footer shows '^R=Reset' for resetting to defaults, but curses_keybindings.json shows Ctrl+R is bound to 'Run program' in the editor context, creating a potential keybinding conflict.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
curses_settings_widget.py footer:
"Enter=OK  ESC/^P=Cancel  ^A=Apply  ^R=Reset"

keypress() handler:
elif key == 'ctrl r':
    self._on_reset()
    return None

curses_keybindings.json editor context:
"run": {
  "keys": ["Ctrl+R"],
  "primary": "Ctrl+R",
  "description": "Run program"
}

When settings widget is open, Ctrl+R should reset settings, but in editor context it runs the program.

---

#### Code vs Comment conflict

**Description:** The cmd_break() docstring states 'Breakpoints are only activated when the RUN command is executed', but the implementation in _install_breakpoint_handler() checks breakpoints during execute_next() which could be called in contexts other than RUN (e.g., during STEP operations).

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
cmd_break() docstring:
"Breakpoints are only activated when the RUN command is executed.
After setting breakpoints, use RUN to start/restart the program
for them to take effect."

But _install_breakpoint_handler() is called from enhance_run_command() and modifies execute_next() to check breakpoints:
def breakpoint_execute():
    """Execute with breakpoint checking"""
    # Check current line for breakpoint
    if interpreter.runtime.current_line:
        line_num = interpreter.runtime.current_line.line_number
        if line_num in self.breakpoints:
            ...

This means breakpoints would be checked during any execute_next() call, not just during RUN.

---

#### Code vs Comment conflict

**Description:** The _add_debug_help() method has a TODO comment saying 'Integrate debug commands with help system', but the method is called during initialization, suggesting it should be doing something now rather than being a placeholder.

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
def _add_debug_help(self):
    """Add debug commands to help system (not yet implemented)"""
    # TODO: Integrate debug commands with help system
    pass

This method is called from _register_commands() during __init__, but does nothing. Either it should be removed from the call chain or implemented.

---

#### code_vs_comment

**Description:** Comment at line 147 mentions 'fixed 5-character width' but this contradicts variable-width design

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment states: "The keypress method uses _parse_line_number to find code boundaries
dynamically. The layout is a formatted string with three fields, not three columns."

But then at line 991 note says: "Note: When reformatting pasted content, line numbers are right-justified to 5 characters
for consistent alignment. This differs from the variable-width formatting used in
_format_line() for display. The fixed 5-char width (lines 991, 1024) helps maintain
alignment when pasting multiple lines with different line number lengths."

This creates confusion about whether the design is variable-width or fixed-width.

---

#### code_vs_comment

**Description:** Comment at line 991 references 'lines 991, 1024' but this is self-referential

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line 991 states: "The fixed 5-char width (lines 991, 1024) helps maintain
alignment when pasting multiple lines with different line number lengths."

This comment is ON line 991, making the reference confusing. Should reference the actual code lines or be more descriptive.

---

#### code_vs_comment

**Description:** Comment says toolbar method is 'no longer used' and 'retained for reference', but doesn't specify if it's deprecated or planned for removal

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at _create_toolbar method (~240): "Note: This method is no longer used (toolbar removed from UI in favor of Ctrl+U menu
for better keyboard navigation). The method is retained for reference and potential
future re-enablement, but can be safely removed if the toolbar is not planned to return."

The comment is self-contradictory: it says the method 'can be safely removed' but also says it's 'retained for reference and potential future re-enablement'. This creates ambiguity about whether the code should be kept or removed.

---

#### code_vs_comment

**Description:** Comment about help widget lifecycle differs from keymap/settings pattern

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_help (~990): "Note: Unlike _show_keymap and _show_settings which support toggling,
help doesn't store overlay state so it can't be toggled off. The help
widget handles its own close behavior via ESC/Q keys."

This comment correctly describes the difference, but the inconsistency in behavior between similar UI overlay methods (_show_help vs _show_keymap/_show_settings) may indicate incomplete refactoring or design inconsistency. All three show overlays but have different lifecycle management.

---

#### code_vs_comment

**Description:** Comment describes editor.lines vs editor_lines distinction but the relationship is unclear

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~40: "# Note: self.editor_lines is the CursesBackend's storage dict
# self.editor.lines is the ProgramEditorWidget's storage dict (different object)"

Then at line ~45: "self.editor_lines = {}  # line_num -> text for editing"

However, throughout the code (e.g., _delete_current_line, _smart_insert_line, _renumber_lines), only self.editor.lines is used, not self.editor_lines. The self.editor_lines dict is initialized but never appears to be used in the visible code, suggesting either dead code or missing synchronization logic.

---

#### code_vs_comment

**Description:** Comment about STACK_KEY conditional check is redundant

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
At line ~470: "elif STACK_KEY and key == STACK_KEY:
    # Toggle execution stack window (only if STACK_KEY is defined)"

The comment says 'only if STACK_KEY is defined' but the code already has 'STACK_KEY and' which handles undefined/None/False cases. The comment is technically correct but the conditional pattern 'STACK_KEY and key == STACK_KEY' is unusual - typically you'd check 'if STACK_KEY is not None and key == STACK_KEY' or just 'if key == STACK_KEY' if STACK_KEY is always defined.

---

#### code_vs_comment

**Description:** Comment about breakpoint persistence contradicts implementation details

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program(), comment states:
"Note: reset_for_run() clears variables and resets PC. Breakpoints are stored in
the editor (self.editor.breakpoints), NOT in runtime, so they persist across runs
and are re-applied below via interpreter.set_breakpoint() calls."

However, the code shows breakpoints are re-applied AFTER calling interpreter.start():
# Re-apply breakpoints from editor
# Breakpoints are stored in editor UI state and must be re-applied to interpreter
# after reset_for_run (which clears them)
for line_num in self.editor.breakpoints:
    self.interpreter.set_breakpoint(line_num)

The first comment says they're re-applied 'below' but doesn't mention they must be re-applied AFTER interpreter.start(). The second comment is more accurate. This could confuse someone trying to understand the initialization order.

---

#### internal_inconsistency

**Description:** Inconsistent error handling between user errors and internal errors in _execute_tick

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_tick(), the exception handler has logic to distinguish user errors from internal errors:

is_user_error = state and state.error_info is not None

if is_user_error:
    # User program error (like FOR/NEXT nesting) - don't spam stderr
    # Format nicely for the user
    ...
else:
    # Internal/unexpected error - log it to stderr
    error_msg = debug_log_error(...)

However, earlier in the same method, when state.error_info is set, it's handled directly without going through the exception handler. This means there are two different code paths for user errors:
1. Direct handling when state.error_info is set (lines ~1150-1175)
2. Exception handler when is_user_error is True (lines ~1200-1220)

Both format the error similarly but the duplication suggests potential for inconsistency.

---

#### code_vs_comment

**Description:** Comment about default type suffix mapping may be incorrect

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_variables_window(), the type_map includes:
type_map = {
    '$': 'string',
    '%': 'integer',
    '!': 'single',
    '#': 'double',
    '': 'single'  # default
}

The comment says "# default" for empty string mapping to 'single', but in many BASIC dialects, the default numeric type varies (could be single, double, or integer depending on the implementation). Without seeing the actual type system implementation, this assumption may be incorrect. The code uses this for filtering, so an incorrect default could cause variables to not match type-based filters.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate() says 'This updates self.program but doesn't affect runtime yet' but immediately after it calls _sync_program_to_runtime()

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1145:
# Parse editor content into program (in case user typed lines directly)
# This updates self.program but doesn't affect runtime yet
self._parse_editor_content()

# Load program lines into program manager
self.program.clear()
for line_num in sorted(self.editor_lines.keys()):
    line_text = f"{line_num} {self.editor_lines[line_num]}"
    self.program.add_line(line_num, line_text)

# Sync program to runtime (but don't reset PC - keep current execution state)
# This allows LIST to work, but doesn't start execution
self._sync_program_to_runtime()

The comment 'doesn't affect runtime yet' is misleading since _sync_program_to_runtime() is called immediately after.

---

#### code_inconsistency

**Description:** Both _save_program() and _save_as_program() have identical implementations except for the initial filename prompt logic

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_save_program() checks if self.current_filename exists and uses it, otherwise prompts.
_save_as_program() always prompts for filename.

Both methods then have identical code for:
- Parsing editor content
- Creating program content
- Writing to file
- Adding to recent files
- Storing current filename
- Cleaning up autosave
- Restarting autosave

This is significant code duplication (~40 lines) that could be refactored.

---

#### code_vs_comment

**Description:** cmd_delete() and cmd_renum() docstrings mention 'runtime=None' parameter but don't explain why it's None or what the implications are

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_delete():
"Note: Doesn't sync to runtime immediately - sync happens when next immediate
command is executed via _execute_immediate. This is acceptable because DELETE
modifies self.program which is the source of truth, and runtime is only updated
when needed for execution."

The docstring mentions runtime=None in the context of calling delete_lines_from_program(), but doesn't explain that passing None means the helper function won't sync to runtime, which contradicts the actual behavior where _execute_immediate() syncs before executing.

---

#### code_vs_comment

**Description:** Comment in fmt_key() function acknowledges limitation but doesn't match actual usage pattern

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Comment states:
"Limitation: Only handles 'Ctrl+' prefix. Other formats like 'Alt+X',
'Shift+Ctrl+X', or 'F5' are returned unchanged. This is acceptable for
the curses menu which primarily uses Ctrl+ keybindings."

However, the menu structure uses keybindings module (kb.NEW_DISPLAY, kb.OPEN_DISPLAY, etc.) which could return any format. The comment suggests this is intentional and acceptable, but there's no validation that the keybindings module actually only returns Ctrl+ formats for curses.

---

#### code_vs_documentation

**Description:** TODO comment indicates version should be imported from src.version module, but it's hardcoded

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Line ~73:
# TODO: Import version from src.version module instead of hardcoding
return "5.21"  # MBASIC version (hardcoded)

This is a known issue documented in code, but represents an inconsistency between intended design (dynamic version import) and current implementation (hardcoded).

---

#### code_vs_comment

**Description:** Comment describes link format as [text] but doesn't specify this is the rendered output format from MarkdownRenderer

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment in _create_text_markup_with_links() at line ~180:
"Links are marked with [text] in the rendered output. This method
converts them to use the 'link' attribute for highlighting"

This comment could be clearer that [text] is the format produced by MarkdownRenderer.render(), not a markdown syntax. The relationship between MarkdownRenderer output and this method's input isn't explicitly documented.

---

#### documentation_inconsistency

**Description:** Inconsistent notation for keyboard shortcuts in different contexts

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
The code uses multiple notations for the same keys:
1. STATUS_BAR_SHORTCUTS uses ^X notation: "^F help  ^U menu  ^W vars  ^K step line"
2. KEYBINDINGS_BY_CATEGORY uses Ctrl+ notation: "Ctrl+F", "Ctrl+U", "Ctrl+W"
3. The keymap_widget.py has a _format_key_display() function to convert between them

This inconsistency means documentation shows keys differently in different places, which could confuse users.

---

#### code_vs_comment

**Description:** Comment says Ctrl+G is context-sensitive but code doesn't implement this

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment for CONTINUE_KEY says:
"# Note: This key (typically Ctrl+G) is context-sensitive in the UI:
#   - In debugger mode: Continue execution until next breakpoint or end
#   - In editor mode: Go to line number (not yet implemented)"

The code loads from 'goto_line' action but the comment says editor mode is "not yet implemented". This creates ambiguity about what the key actually does and whether the JSON config or the comment is authoritative.

---

#### documentation_inconsistency

**Description:** KEYBINDINGS_BY_CATEGORY includes undocumented shortcuts

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
KEYBINDINGS_BY_CATEGORY includes these shortcuts that aren't defined as constants in the code:
- 'Shift+Ctrl+V' for 'Save As'
- 'Shift+Ctrl+O' for 'Recent files'

These appear in the help documentation but have no corresponding constant definitions (like SAVE_AS_KEY, RECENT_FILES_KEY, etc.) in the keybindings module. This suggests either:
1. The documentation is ahead of implementation
2. These are implemented elsewhere without being defined here
3. The documentation is incorrect

---

#### code_vs_comment

**Description:** Inconsistent terminology for 'Step Line' functionality

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
The code uses multiple descriptions for the same functionality:
1. LIST_KEY comment: "Step Line - execute all statements on current line"
2. STATUS_BAR_SHORTCUTS: "^K step line"
3. KEYBINDINGS_BY_CATEGORY: "Step Line - execute all statements on current line"
4. JSON action name: 'step_line'

While mostly consistent, the variable name LIST_KEY doesn't match any of these descriptions, creating potential confusion.

---

#### documentation_inconsistency

**Description:** Help key description inconsistency

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
HELP_KEY is defined with comment "# Help system - use Ctrl+F (F for help/Find help)"

The mnemonic explanation says "F for help/Find help" but F doesn't stand for 'help' - it stands for 'Find'. This is a minor inconsistency in the mnemonic explanation.

---

#### documentation_inconsistency

**Description:** Variables window appears in two different categories with same key

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
VARIABLES_DISPLAY appears in two categories:
1. 'Global Commands': (VARIABLES_DISPLAY, 'Toggle variables watch window')
2. 'Debugger (when program running)': (VARIABLES_DISPLAY, 'Show/hide variables window')

Both refer to the same key (Ctrl+W) but use slightly different descriptions ('Toggle' vs 'Show/hide'). This duplication could confuse users about when the key is available.

---

#### documentation_inconsistency

**Description:** Stack window appears in two different categories with same key

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
STACK_DISPLAY appears in two categories:
1. 'Global Commands': (STACK_DISPLAY, 'Toggle execution stack window')
2. 'Debugger (when program running)': (STACK_DISPLAY, 'Show/hide execution stack window')

Both refer to 'Menu only' but appear in different contexts, suggesting different availability. This duplication is confusing.

---

#### code_vs_comment

**Description:** Comment says 'title=None creates border without title text (still has top border line)' but this is standard urwid behavior

**Affected files:**
- `src/ui/keymap_widget.py`

**Details:**
In KeymapWidget.__init__():
"# title=None creates border without title text (still has top border line)
linebox = urwid.LineBox(
    urwid.AttrMap(self.listbox, 'body'),
    title=None
)"

The comment explains standard urwid.LineBox behavior as if it's special. This isn't wrong, but it's documenting library behavior rather than application logic, which could be misleading.

---

#### documentation_inconsistency

**Description:** Module docstring says 'Not thread-safe (no locking mechanism)' but doesn't explain implications

**Affected files:**
- `src/ui/recent_files.py`

**Details:**
The module docstring states:
"- Note: Not thread-safe (no locking mechanism)"

However, it doesn't explain:
1. Whether MBASIC uses multiple threads
2. What could go wrong if used from multiple threads
3. Whether this is a limitation or intentional design

This creates uncertainty about whether thread-safety is needed.

---

#### Code vs Documentation inconsistency

**Description:** Return key in search box is documented but Enter key in in-page search is not

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
tk_keybindings.json documents:
"search": {
  "keys": ["Return"],
  "primary": "Return",
  "description": "Execute search (when in search box)"
}

But tk_help_browser.py line 126 also binds Return for in-page search:
self.inpage_search_entry.bind('<Return>', lambda e: self._inpage_find_next())

The keybindings file only documents Return for the main search box, not for the in-page search box where it triggers find next.

---

#### Code duplication inconsistency

**Description:** Table formatting code is duplicated with a note about extraction

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/markdown_renderer.py`

**Details:**
In tk_help_browser.py line 663-667:
def _format_table_row(self, line: str) -> str:
    """Format a markdown table row for display.

    Note: This implementation is duplicated in src/ui/markdown_renderer.py.
    Consider extracting to a shared utility module if additional changes are needed.
    """

The code explicitly notes duplication with markdown_renderer.py and suggests extraction to a shared utility. This is a maintenance concern rather than an inconsistency, but indicates technical debt.

---

#### Code vs Comment conflict

**Description:** Comment says 'non-blocking' but grab_set() makes dialog modal

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 48:
# Make modal (grab input focus, but non-blocking - no wait_window())
self.transient(parent)
self.grab_set()

The comment claims the dialog is 'non-blocking' because it doesn't call wait_window(). However, grab_set() makes the dialog modal by preventing interaction with other windows. The dialog IS blocking user interaction with the parent window, even if it doesn't block code execution. The comment is misleading about what 'non-blocking' means in this context.

---

#### Code vs Comment conflict

**Description:** Help display mechanism differs from comment description

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 152-159:
# Help button
if defn.help_text and len(defn.help_text) > 50:
    help_btn = ttk.Button(frame, text="?", width=3,
                         command=lambda k=key, d=defn: self._show_help(k, d))
    help_btn.pack(side=tk.LEFT, padx=(5, 0))
else:
    # Show short help as inline label (not a hover tooltip, just a gray label)
    if defn.help_text:

The comment says 'not a hover tooltip, just a gray label' but this seems to be clarifying what it ISN'T rather than what was previously there. The comment suggests there might have been confusion about implementation, but the current code is clear. This is a defensive comment that may be unnecessary.

---

#### Code internal inconsistency

**Description:** Context menu dismiss mechanism has redundant cleanup

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In tk_help_browser.py line 619-631:
def dismiss_menu():
    try:
        menu.unpost()
    except:
        pass

try:
    menu.tk_popup(event.x_root, event.y_root)
finally:
    # Release grab after menu is shown. Note: tk_popup handles menu interaction,
    # but we explicitly release the grab to ensure clean state.
    menu.grab_release()

The comment says 'tk_popup handles menu interaction' but then explicitly calls grab_release(). The comment also defines dismiss_menu() but the finally block doesn't call it. The cleanup logic is split between the finally block and the dismiss_menu function in a potentially confusing way.

---

#### code_vs_comment

**Description:** Comment says immediate mode has no header or history, but attributes are set to None

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~280 says:
"# Immediate mode input (just the prompt and entry, no header or history)"

But then at lines ~330-333:
"# Set immediate_history and immediate_status to None
# These attributes are not currently used but are set to None for defensive programming
# in case future code tries to access them (will get None instead of AttributeError)
self.immediate_history = None
self.immediate_status = None"

The comment suggests these were removed, but the code explicitly sets them to None with a different explanation (defensive programming). This creates confusion about whether they were intentionally removed or are placeholders.

---

#### code_vs_comment

**Description:** Toolbar comment says features are accessible via menus, but lists incorrect menu paths

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~520 says:
"# Note: Toolbar has been simplified to show only essential execution controls.
# Additional features are accessible via menus:
# - List Program → Run > List Program
# - New Program (clear) → File > New
# - Clear Output → Run > Clear Output"

However, looking at the menu creation code:
- 'List Program' is correctly at Run > List Program (line ~506)
- 'New Program' is correctly at File > New (line ~442)
- 'Clear Output' is correctly at Run > Clear Output (line ~509)

But the comment format uses '→' which might be confusing. Also, the comment mentions these as 'removed from toolbar' but doesn't clarify what was actually removed or when.

---

#### documentation_inconsistency

**Description:** Docstring example code references non-existent 'editing' module

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Class docstring shows usage example:
"from editing import ProgramManager"

But based on the actual imports at the top of the file, there is no 'editing' module imported. The actual import structure is not shown, making the example potentially misleading for users trying to use this class.

---

#### code_vs_comment

**Description:** Comment about entry widget configuration is redundant and potentially confusing

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At lines ~287-290:
"# Use tk.Entry instead of ttk.Entry for better input reliability
# Explicitly set state, takefocus, and exportselection to ensure entry accepts input
self.immediate_entry = tk.Entry(input_frame, font=('Courier', 10),
                                state='normal', takefocus=True,
                                exportselection=False)"

Then at line ~333:
"# Initialize immediate mode entry to be enabled and focused
# (it will be enabled/disabled later based on program state via _update_immediate_status)
self.immediate_entry.config(state=tk.NORMAL)"

The entry is already created with state='normal', so the later config(state=tk.NORMAL) is redundant. The comment suggests this is intentional initialization, but it's unclear why it needs to be set twice.

---

#### code_vs_comment

**Description:** Comment about Type and Value columns not being sortable contradicts heading setup

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~1084:
"# Type and Value columns are not sortable"

But the columns are set up with headings that could be clicked:
"tree.heading('Value', text='  Value')
tree.heading('Type', text='  Type')"

The comment suggests these columns shouldn't be sortable, but there's no visual indication (like disabled state or different styling) to show users they can't sort by these columns. Users might click and expect sorting to work.

---

#### code_vs_comment

**Description:** Comment says validation is called with 100ms delay after cursor movement/clicks, but actual delay varies by event type

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1683:
# Note: This method is called with a delay (100ms) after cursor movement/clicks
# to avoid excessive validation during rapid editing

But in code:
_on_cursor_move: self.root.after(100, self._validate_editor_syntax)
_on_mouse_click: self.root.after(100, self._validate_editor_syntax)
_on_focus_out: self._validate_editor_syntax()  # No delay!

The _on_focus_out handler calls validation immediately without any delay, contradicting the comment.

---

#### code_vs_comment

**Description:** Comment about preserving final blank line conflicts with actual Tk Text widget behavior

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1774:
Removes blank lines to keep program clean, but preserves the final
line which is always blank in Tk Text widget (internal Tk behavior).

This comment suggests the final blank line is intentionally preserved, but the code at line ~1795 explicitly keeps it:
if line.strip() or i == len(lines) - 1:
    filtered_lines.append(line)

The comment makes it sound like this is unavoidable Tk behavior, but the code is actively choosing to keep it. This is misleading about whether it's a Tk limitation or a design choice.

---

#### code_vs_comment

**Description:** Comment about error display behavior doesn't match actual implementation logic

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1710:
# Only show error list in output if there are multiple errors or this is the first time
# Don't spam output on every keystroke
should_show_list = len(errors_found) > 1

The comment mentions 'or this is the first time' but the code only checks if there are multiple errors. There's no tracking of whether this is the first time errors are shown. The comment suggests more sophisticated logic than actually exists.

---

#### code_vs_comment

**Description:** Comment in _on_paste says 'Single-line paste into blank line (current_line_text is empty) - auto-number if needed' but the code path for blank lines falls through to multi-line logic

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1090 says:
'# Multi-line paste or single-line paste into blank line - use auto-numbering logic
# This handles two cases:
# 1. Multi-line paste (sanitized_text contains \n) - auto-number if needed
# 2. Single-line paste into blank line (current_line_text is empty) - auto-number if needed'

However, the code before this comment explicitly handles single-line paste into existing lines and returns 'break'. The remaining code only processes multi-line pastes (lines with \n). Single-line paste into blank line would have been caught by the earlier 'if current_line_text:' check and would not reach this comment's code section.

---

#### code_vs_comment

**Description:** Comment in _smart_insert_line says 'DON'T save to program yet' but the function already called _save_editor_to_program() earlier

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1450 says:
'# DON\'T save to program yet - the line is blank and would be filtered out by
# _save_editor_to_program() which skips blank lines.'

However, earlier in the same function (line ~1380), the code explicitly calls:
self._save_editor_to_program()
self._refresh_editor()

So the program has already been saved before the comment claims not to save it.

---

#### code_vs_comment

**Description:** Comment in _on_enter_key says 'Tk uses 1-based indexing' but this is about line numbers in the text widget, not general Tk indexing

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~950:
current_line_text_index = idx + 1  # Tk uses 1-based indexing

This is misleading. The +1 is because idx is from enumerate() which is 0-based, and Tk text widget line numbers start at 1. It's not about 'Tk uses 1-based indexing' in general, but specifically about text widget line numbering.

---

#### code_vs_comment

**Description:** Docstring for _add_immediate_output() says it 'forwards to _add_output()' but the actual implementation directly calls self._add_output(text) without any forwarding logic

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring states:
"Add text to main output pane.

This method name is historical - it simply forwards to _add_output().
In the Tk UI, immediate mode output goes to the main output pane."

Implementation:
"def _add_immediate_output(self, text):
    self._add_output(text)"

This is technically correct but the term 'forwards' is misleading - it's a simple wrapper/alias, not a forwarding pattern.

---

#### documentation_inconsistency

**Description:** Inconsistent reference to line numbers - comments reference 'line ~291' but this is vague and may become outdated as code changes

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Multiple comments reference:
"Note: self.immediate_history exists but is always None (see line ~291)"
"NOTE: This method is currently unused - immediate_history is always None in the Tk UI (see line ~291)."

Line number references in comments are fragile and will become incorrect as code is modified. Should reference method names or use relative references instead.

---

#### code_vs_comment

**Description:** Canvas width comment says '20 (pixels in Tkinter)' but doesn't clarify this is a fixed width that may not scale with font size

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment: '# Width: 20 (pixels in Tkinter) for one status character (●, ?, or space)'

Code: self.canvas = tk.Canvas(self, width=20, ...)

The width is hardcoded to 20 pixels, but the font size is configurable (default 10). If font size changes, the status symbols might not fit properly in the 20-pixel canvas.

---

#### internal_inconsistency

**Description:** Inconsistent regex patterns for parsing line numbers between _parse_line_number() and _on_status_click()

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_parse_line_number() uses: r'^(\d+)(?:\s|$)'

_on_status_click() uses: r'^\s*(\d+)'

The second pattern allows leading whitespace (\s*) while the first doesn't. The second pattern also doesn't enforce whitespace or end-of-string after the number. This could lead to different parsing behavior in different parts of the code.

---

#### code_vs_comment

**Description:** Class docstring says 'automatic blank line removal' happens 'When cursor moves away' but doesn't mention it's scheduled with after_idle

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring: 'When cursor moves away from a blank line, that line is automatically deleted'

Actual implementation:
self.text.after_idle(self._delete_line, self.current_line)

The deletion is scheduled asynchronously using after_idle, not immediate. This is an important implementation detail that affects timing and could matter for understanding race conditions or event ordering.

---

#### code_vs_comment

**Description:** serialize_line() comment mentions fallback behavior for missing source_text but doesn't explain potential inconsistency issue

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment in serialize_line() says:
"# Note: If source_text doesn't match pattern, falls back to relative_indent=1
# This can cause inconsistent indentation for programmatically inserted lines"

This is a warning about a known issue, but the function doesn't provide any way to handle or detect this inconsistency. The comment acknowledges the problem but the code doesn't mitigate it.

---

#### documentation_inconsistency

**Description:** update_line_references() docstring claims 'fast, good for most cases' but doesn't explain limitations or edge cases

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says: "Uses regex-based approach (fast, good for most cases)."

The phrase "good for most cases" implies there are cases where it's NOT good, but the docstring doesn't document what those cases are or when to use an alternative approach. No alternative approach is mentioned in the module.

---

#### code_vs_comment

**Description:** renum_program() docstring says callback is 'responsible for identifying and updating statements with line number references' but doesn't specify which statement types need updating

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says:
"renum_callback: Function that takes (stmt, line_map) to update statement references.
                Called for ALL statements; callback is responsible for identifying and
                updating statements with line number references (GOTO, GOSUB, ON GOTO,
                ON GOSUB, IF THEN/ELSE line numbers)"

The list in parentheses appears to be examples, but it's unclear if this is exhaustive. The docstring doesn't clarify whether other statement types (like RESTORE, RESUME, etc.) might also have line number references that need updating.

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No UI-framework dependencies' but doesn't clarify if runtime/parser dependencies are allowed

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Module docstring says:
"This module contains UI-agnostic helper functions that can be used by
any UI (CLI, Tk, Web, Curses). No UI-framework dependencies (Tk, curses, web)
are allowed, though standard library modules (os, glob, re) are permitted."

However, several functions (renum_program, delete_lines_from_program) take runtime and program_manager objects as parameters, which are not standard library modules. The docstring should clarify that core interpreter dependencies are allowed, only UI framework dependencies are prohibited.

---

#### code_vs_comment

**Description:** serialize_expression() docstring note about ERR/ERL mentions 'MBASIC 5.21 syntax' but module header doesn't specify MBASIC version compatibility

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
serialize_expression() docstring says:
"Note:
    ERR and ERL are special system variables that are serialized without
    parentheses (e.g., 'ERR' not 'ERR()') when they appear as FunctionCallNode
    with no arguments, matching MBASIC 5.21 syntax."

The module header and other functions don't mention MBASIC 5.21 compatibility as a design goal. This creates ambiguity about whether the entire module targets MBASIC 5.21 compatibility or just this specific function.

---

#### code_vs_comment

**Description:** cycle_sort_mode() comment says 'This matches the Tk UI implementation' but module is supposed to be UI-agnostic

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Comment in cycle_sort_mode():
"The cycle order is: accessed -> written -> read -> name -> (back to accessed)
This matches the Tk UI implementation."

The module docstring says it provides 'consistent variable sorting behavior across all UI backends', implying it's the canonical implementation. Saying it 'matches the Tk UI' suggests Tk UI is the source of truth, which contradicts the module's purpose of being the shared implementation.

---

#### code_vs_comment

**Description:** get_sort_key_function() comment mentions 'old type/value modes' but these modes are not documented anywhere in the module

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Comment in get_sort_key_function():
"# Default to name sorting (unknown modes fall back to this, e.g., old 'type'/'value')"

The module's get_variable_sort_modes() only returns 4 modes: accessed, written, read, name. There's no documentation about deprecated 'type' or 'value' modes, when they were removed, or why they're mentioned in this comment.

---

#### code_vs_documentation

**Description:** cmd_run() docstring says 'Override or use this implementation' but the method creates Runtime and Interpreter which requires knowledge of internal structure

**Affected files:**
- `src/ui/visual.py`

**Details:**
The docstring suggests this is a usable base implementation:
"Override or use this implementation:
1. Create Runtime and Interpreter from ProgramManager
2. Run the program
3. Handle errors and display output"

However, the implementation imports 'create_local_limits' from 'resource_limits' module without showing the import at the top of the file, and uses internal attributes like 'self.program.line_asts' and 'self.program.lines' which may not be part of ProgramManager's public API. This makes it unclear if subclasses can actually 'use this implementation' as-is.

---

#### documentation_inconsistency

**Description:** Class docstring mentions 'Use self.program for program management' but doesn't document what self.program is or its type

**Affected files:**
- `src/ui/visual.py`

**Details:**
The docstring says:
"6. Use self.program for program management"

But there's no documentation of what self.program is, its type (presumably ProgramManager based on __init__ parameter), or what methods are available. The __init__ method receives 'program_manager' parameter but doesn't show it being assigned to self.program.

---

#### code_vs_documentation

**Description:** get_cursor_position() docstring says it returns placeholder but doesn't document that it's not actually functional

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
The method docstring says:
"Get current cursor position (placeholder implementation).

Returns:
    Dict with 'line' and 'column' keys (always returns {0, 0} - not implemented)"

While it does mention 'not implemented' in parentheses, the docstring format suggests this is a working method. The comment inside says:
"# This would need async support, for now return placeholder"

This is inconsistent - a placeholder/unimplemented method should probably raise NotImplementedError or be more clearly marked as non-functional in the docstring.

---

#### code_vs_comment

**Description:** Comment about event args being dict conflicts with type hints suggesting string value

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
In the value property getter:
"if isinstance(self._value, dict):
    # Sometimes event args are dict - return empty string
    return ''"

But the __init__ method shows:
"def _internal_change_handler(e):
    self._value = e.args  # CodeMirror sends new value as args"

The comment says 'CodeMirror sends new value as args' suggesting it should be a string, but then the property getter handles the case where it's a dict. This suggests either:
1. The event handling is buggy and sometimes receives unexpected dict values
2. The comment is wrong about what CodeMirror sends
3. There's an undocumented edge case

---

#### code_vs_comment

**Description:** Comment claims input echoing is handled by NiceGUIBackend class, but the actual echoing mechanism is not visible in the provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~67 comment states:
"# Note: The input echoing (displaying what user typed) is handled by the
# inline input handler in the NiceGUIBackend class, not here."

However, the NiceGUIBackend class code shown does not include the _enable_inline_input() method or any visible input echoing implementation. The comment references a method that may exist but is not shown in the provided code excerpt.

---

#### code_vs_comment

**Description:** Comment references _get_input method but the actual callback mechanism is unclear

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~56-58 comment states:
"The input_callback handles asyncio.Future coordination between synchronous
interpreter and async web UI. The input field appears below the output pane,
allowing users to see all previous output while typing."

The comment mentions _get_input as the callback (line ~60: "# prompt display via _enable_inline_input() method in the NiceGUIBackend class"), but the actual _get_input implementation is not shown in the provided code, making it impossible to verify the described behavior.

---

#### code_vs_comment

**Description:** Comment references line number that doesn't match the actual location

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1027 comment states:
"# The _on_editor_change method (defined at line ~2609) handles:"

This comment references line ~2609 for the _on_editor_change method definition, but the provided code excerpt ends before that line. The comment may be outdated if the code has been refactored or the line numbers have changed.

---

#### code_internal_inconsistency

**Description:** Inconsistent comment style for tracking state variables

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1018-1021 uses detailed inline comments:
"self.last_edited_line_index = None
self.last_edited_line_text = None
self.last_line_count = 0  # Track number of lines to detect Enter
self.auto_numbering_in_progress = False  # Prevent recursive calls
self.editor_has_been_used = False  # Track if user has typed anything"

Some variables have inline comments explaining their purpose, while others (last_edited_line_index, last_edited_line_text) do not. This inconsistency makes the code harder to understand.

---

#### code_vs_comment

**Description:** Comment says 'INPUT statement executes, the immediate_entry input box is focused' but code shows output textarea has keydown handler

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1770 comment:
  # INPUT handling: When INPUT statement executes, the immediate_entry input box
  # is focused for user input (see _execute_tick() lines ~1886-1888).
  # The output textarea remains readonly.
But line ~1780:
  # Set up Enter key handler for output textarea (for future inline input feature)
  self.output.on('keydown.enter', self._handle_output_enter)
The comment says 'future inline input feature' but earlier comment says immediate_entry is used. Unclear which is current vs planned.

---

#### code_vs_comment

**Description:** Comment says 'interpreter/runtime reused to preserve session state' but runtime is reset

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2110 in _menu_step_stmt():
  # Create new IO handler for execution (interpreter/runtime reused to preserve session state)
But the code immediately calls:
  self.runtime.reset_for_run(self.program.line_asts, self.program.lines)
Which resets the runtime. The comment about 'preserving session state' is misleading - only breakpoints are preserved, variables are cleared.

---

#### code_vs_comment

**Description:** Comment about 'defensive programming - prevents multiple timers' but no explanation of why multiple timers would occur

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2240 in _menu_continue():
  # Cancel any existing timer first (defensive programming - prevents multiple timers)
  if self.exec_timer:
    self.exec_timer.cancel()
This is good practice but the comment doesn't explain the scenario where multiple timers could be created. Is this a known bug being worked around?

---

#### code_vs_comment

**Description:** Comment in _remove_blank_lines assumes cursor is at end, but acknowledges this may not be true

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment states: 'The last line is preserved even if blank, since it's likely where the cursor is after pressing Enter. This prevents removing the blank line user just created. Note: This assumes cursor is at the end, which may not always be true if user clicks elsewhere.'

The code preserves the last line unconditionally, but the comment admits the assumption may be wrong, suggesting the implementation might not handle all cases correctly.

---

#### code_vs_comment

**Description:** Comment in _check_auto_number says 'Only auto-numbers a line once' but the logic checks old snapshot existence, not a 'numbered once' flag

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: 'Only auto-numbers a line once - tracks the last snapshot to avoid re-numbering lines while user is still typing on them.'

Code checks: if stripped and (i < len(old_lines) or len(lines) > len(old_lines))

The logic doesn't truly prevent numbering 'once' - it prevents numbering lines that didn't exist in the old snapshot. A line could theoretically be numbered multiple times if snapshots change in certain ways.

---

#### documentation_inconsistency

**Description:** Docstring for start() says 'Not implemented - raises NotImplementedError' but this is redundant with the implementation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring: 'Not implemented - raises NotImplementedError. Use start_web_ui() module function instead for web backend.'

The docstring just repeats what the code does (raise NotImplementedError). It would be more useful to explain WHY this method isn't implemented (architectural decision for multi-user web apps).

---

#### code_vs_comment

**Description:** Comment about CP/M EOF marker in _save_editor_to_program seems out of place for web editor

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# Normalize line endings and remove CP/M EOF markers # \r\n -> \n (Windows line endings, may appear if user pastes text) # \r -> \n (old Mac line endings, may appear if user pastes text) # \x1a (Ctrl+Z, CP/M EOF marker - included for consistency with file loading)'

The CP/M EOF marker (\x1a) handling is described as 'for consistency with file loading', but in a web editor context where users type or paste text, this marker is extremely unlikely to appear. This suggests copy-pasted code from file loading logic.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for breakpoints

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md states:
'Curses UI: Position cursor on the line and press b'
'Tk UI: Click the line number gutter next to the line Or position cursor on the line and press Ctrl+B'

editor-commands.md states:
'b | Ctrl+B | Toggle breakpoint (Curses: b, Tk: Ctrl+B)'

The first doc says Tk can use 'b' OR 'Ctrl+B', the second says only 'Ctrl+B' for Tk. This is contradictory.

---

#### code_vs_comment

**Description:** Deprecated class comment suggests using 'direct web URL' but no alternative implementation shown

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Comment states:
'# Legacy class kept for compatibility - new code should use direct web URL instead'
'# The help site is already built and served at http://localhost/mbasic_docs'

But there's no documentation or code showing how the help site is 'already built and served' or what mechanism serves it. The WebHelpLauncher_DEPRECATED class has logic to build and serve help, but if it's deprecated, what replaced it?

---

#### documentation_inconsistency

**Description:** Help opening shortcuts inconsistent

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
editor-commands.md states:
'F1 or H | | Open help'

debugging.md doesn't mention 'H' key for help, only references F1 in context help:
'Press F1 with cursor on a BASIC keyword for context help'

It's unclear if 'H' opens general help or if this is UI-specific.

---

#### code_vs_comment

**Description:** Comment claims MkDocs is needed but code has fallback logic

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
The _use_fallback_viewer() method prints:
'Help system: Please install MkDocs for best experience'
'Run: pip install mkdocs mkdocs-material'

But the comment says:
'# Could implement a simple markdown viewer here'
'# or open the raw markdown files'

This suggests the fallback isn't implemented, but the code structure implies it should handle the case when MkDocs isn't available. The actual behavior is unclear.

---

#### code_vs_documentation

**Description:** Version information mismatch in documentation

**Affected files:**
- `src/version.py`
- `docs/help/common/getting-started.md`

**Details:**
version.py states:
VERSION = '1.0.667'
MBASIC_VERSION = '5.21'

getting-started.md states:
'MBASIC 5.21 is compatible with MBASIC from the 1980s'

The documentation should reference the actual project version (1.0.667) somewhere, not just the compatibility version (5.21). Users need to know what version of MBASIC-2025 they're running.

---

#### documentation_inconsistency

**Description:** Inconsistent reference to UI-specific help location

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/getting-started.md`

**Details:**
getting-started.md says:
'See your UI-specific help for how to type programs:
- [Curses UI](../ui/curses/editing.md)'

But debugging.md references:
'[Keyboard Shortcuts](shortcuts.md)'

The path structure is inconsistent - some use relative paths like '../ui/curses/', others use same-directory paths like 'shortcuts.md'. The actual file structure from README.md shows /ui/curses/index.md exists, but getting-started.md references /ui/curses/editing.md which may not exist.

---

#### documentation_inconsistency

**Description:** Inconsistent precision information for ATN function evaluation

**Affected files:**
- `docs/help/common/language/appendices/math-functions.md`
- `docs/help/common/language/functions/atn.md`

**Details:**
In math-functions.md:
'PI = ATN(1) * 4
' (Note: ATN is evaluated in single precision, ~7 digits)'

In atn.md:
'The expression X may be any numeric type, but the evaluation of ATN is always performed in single precision.'

Both mention single precision, but math-functions.md adds the ~7 digits detail which should be consistent across both documents.

---

#### documentation_inconsistency

**Description:** Inconsistent formatting of reserved error code ranges

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
In error-codes.md, reserved error codes are formatted inconsistently:
- '| | *24-25* | *(Reserved)* |'
- '| | *27-28* | *(Reserved)* |'
- '| | *31-49* | *(Reserved)* |'
- '| | *56* | *(Reserved)* |'
- '| | *59-60* | *(Reserved)* |'
- '| | *65* | *(Reserved)* |'

Single codes (56, 65) use same formatting as ranges, which is inconsistent. Should distinguish single reserved codes from ranges.

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' sections across mathematical functions

**Affected files:**
- `docs/help/common/language/functions/abs.md`
- `docs/help/common/language/functions/atn.md`
- `docs/help/common/language/functions/cos.md`
- `docs/help/common/language/functions/exp.md`
- `docs/help/common/language/functions/fix.md`

**Details:**
Mathematical functions (abs.md, atn.md, cos.md, exp.md, fix.md) all have identical 'See Also' sections listing the same 10 functions:
- ABS, ATN, COS, EXP, FIX, INT, LOG, RND, SGN, SIN, SQR, TAN

This creates circular references and doesn't provide useful differentiation. Each function should have a curated 'See Also' list of related functions, not the complete list.

---

#### documentation_inconsistency

**Description:** Mathematical constants section uses inconsistent notation for precision

**Affected files:**
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
In math-functions.md:
'PI = 3.1415927          ' Single-precision approximation
PI# = 3.141592653589793 ' Double-precision value

E = 2.7182818           ' Single-precision approximation
E# = 2.718281828459045  ' Double-precision value'

The comment says 'approximation' for single and 'value' for double, implying double is exact. Both are approximations of irrational numbers. Should use consistent terminology like 'Single-precision value' and 'Double-precision value'.

---

#### documentation_inconsistency

**Description:** INPUT$ function categorization mismatch in index

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/input_dollar.md`

**Details:**
In index.md, INPUT$ is listed under 'File I/O Functions' category.
In input_dollar.md, the frontmatter shows 'category: file-io'.
However, INPUT$ can read from both terminal and files, so it could also be considered a string function or have dual categorization. The current categorization is consistent but potentially incomplete.

---

#### documentation_inconsistency

**Description:** TAB function categorization mismatch in index

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/tab.md`

**Details:**
In index.md, TAB is listed under 'String Functions' category.
In tab.md, the frontmatter shows 'category: output-formatting'.
These categories don't match - TAB should either be in 'String Functions' or a separate 'Output Formatting' category should exist in the index.

---

#### documentation_inconsistency

**Description:** SPC function categorization mismatch in index

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/spc.md`

**Details:**
In index.md, SPC is listed under 'String Functions' category.
In spc.md, the frontmatter shows 'category: string'.
However, SPC is described as 'Prints I blanks on the terminal' and 'may only be used with PRINT and LPRINT statements', making it more of an output formatting function like TAB, not a string manipulation function.

---

#### documentation_inconsistency

**Description:** SPACE$ description could reference STRING$ equivalence

**Affected files:**
- `docs/help/common/language/functions/space_dollar.md`
- `docs/help/common/language/functions/string_dollar.md`

**Details:**
space_dollar.md states: 'This is equivalent to STRING$(I, 32) since 32 is the ASCII code for a space character.'

This cross-reference is good, but string_dollar.md doesn't mention that STRING$(I, 32) is equivalent to SPACE$(I). The relationship should be bidirectional for better documentation.

---

#### documentation_inconsistency

**Description:** INT function has inconsistent 'related' field in frontmatter

**Affected files:**
- `docs/help/common/language/functions/int.md`

**Details:**
int.md frontmatter includes:
related: ['fix', 'cint', 'csng', 'cdbl']

But the 'See Also' section at the bottom includes many more functions (ABS, ATN, COS, EXP, FIX, LOG, RND, SGN, SIN, SQR, TAN). The 'related' field should either match the 'See Also' section or have a clear distinction in purpose.

---

#### documentation_inconsistency

**Description:** Inconsistent 'related' field usage in string function frontmatter

**Affected files:**
- `docs/help/common/language/functions/left_dollar.md`
- `docs/help/common/language/functions/right_dollar.md`
- `docs/help/common/language/functions/mid_dollar.md`

**Details:**
left_dollar.md has:
related: ['right_dollar', 'mid_dollar', 'len']

right_dollar.md has:
related: ['left_dollar', 'mid_dollar', 'len']

mid_dollar.md has:
related: ['left_dollar', 'right_dollar', 'len', 'instr']

The 'related' fields are similar but not identical (MID$ includes INSTR while others don't). This should be consistent across related functions.

---

#### documentation_inconsistency

**Description:** LOG function missing 'related' field in frontmatter while INT has it

**Affected files:**
- `docs/help/common/language/functions/log.md`
- `docs/help/common/language/functions/int.md`

**Details:**
log.md frontmatter has:
keywords: ['function', 'log', 'print', 'return']
syntax: LOG (X)
title: LOG
type: function

But int.md has an additional 'related' field:
related: ['fix', 'cint', 'csng', 'cdbl']

Some function docs have 'related' fields while others don't. This should be consistent - either all should have it or none should (with 'See Also' being the canonical reference list).

---

#### documentation_inconsistency

**Description:** LOF function has 'related' field but most other file I/O functions don't

**Affected files:**
- `docs/help/common/language/functions/lof.md`

**Details:**
lof.md frontmatter includes:
related: ['eof', 'loc', 'open']

But other file I/O functions like loc.md, eof.md, input_dollar.md don't have 'related' fields in their frontmatter. This inconsistency in frontmatter structure should be resolved.

---

#### documentation_inconsistency

**Description:** INSTR example shows 'Illegal function call' error for I=0, but doesn't specify valid range clearly

**Affected files:**
- `docs/help/common/language/functions/instr.md`
- `docs/help/common/language/functions/left_dollar.md`

**Details:**
instr.md states: 'Optional offset I sets the position for starting the search. I must be in the range 1 to 255.'
Then notes: 'If I=0 is specified, an "Illegal function call" error will occur.'

This is clear, but left_dollar.md states: 'I must be in the range 0 to 255. If I=0, the null string (length zero) is returned.'

So LEFT$ allows I=0 but INSTR doesn't. This difference should be more prominently documented as it's a common source of confusion.

---

#### documentation_inconsistency

**Description:** MID$ example note about I=0 error but doesn't specify in main description

**Affected files:**
- `docs/help/common/language/functions/mid_dollar.md`

**Details:**
mid_dollar.md description states: 'I and J must be in the range 1 to 255.'
But then notes: 'If I=0 is specified, an "Illegal function call" error will occur.'

The note is redundant if the range is already specified as '1 to 255'. Either remove the note or clarify that the range specification already excludes 0.

---

#### documentation_inconsistency

**Description:** TAN function documentation has inconsistent 'See Also' section - includes functions not directly related to trigonometry

**Affected files:**
- `docs/help/common/language/functions/tan.md`

**Details:**
The 'See Also' section for TAN includes functions like ABS, FIX, INT, RND, SGN which are not trigonometric functions. Other trig functions (SIN, COS, ATN) have similar comprehensive lists, but it's inconsistent with the focused nature of other function documentation. Compare to VAL function which has a more focused 'See Also' list of related string functions.

---

#### documentation_inconsistency

**Description:** VARPTR and DEF USR have different 'See Also' lists despite being related features

**Affected files:**
- `docs/help/common/language/functions/varptr.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
VARPTR includes comprehensive system function references (FRE, INKEY$, INP, LIMITS, NULL, PEEK, etc.) while DEF USR only references USR, DEF FN, POKE, and PEEK. Since both are system/memory-related features that are not implemented, they should have similar 'See Also' sections.

---

#### documentation_inconsistency

**Description:** DEF FN documentation describes extension not mentioned in other docs

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
DEF FN documentation extensively describes multi-character function names as an extension: 'Original MBASIC 5.21: Function names were limited to a single character after FN' vs 'This implementation (extension): Function names can be multiple characters'. However, the main language index (docs/help/common/language/index.md) does not mention this extension in its overview of functions or language features. Extensions should be documented consistently across all relevant files.

---

#### documentation_inconsistency

**Description:** Inconsistent formatting of example sections

**Affected files:**
- `docs/help/common/language/statements/auto.md`
- `docs/help/common/language/statements/delete.md`

**Details:**
AUTO uses '# Generates line numbers...' style comments in examples, while DELETE uses plain text descriptions without code block formatting. Example formatting should be consistent across all statement documentation.

---

#### documentation_inconsistency

**Description:** CLOAD and CSAVE marked as 'not included in DEC VT180 version' but version tags say '8K, Extended'

**Affected files:**
- `docs/help/common/language/statements/cload.md`
- `docs/help/common/language/statements/csave.md`

**Details:**
Both CLOAD and CSAVE have titles stating 'THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION' but the version tags say '8K (cassette), Extended (cassette)'. This is confusing - it should either be in the version tag or the title, not both, and the information should be consistent.

---

#### documentation_inconsistency

**Description:** DATA statement example output formatting inconsistent with description

**Affected files:**
- `docs/help/common/language/statements/data.md`

**Details:**
The example shows 'PRINT A; B; C$; D$' which would print with spaces between values due to semicolons, but the output shown is ' 12  3.14159 Hello WORLD' with varying spacing. The example should clarify the spacing behavior or use consistent formatting.

---

#### documentation_inconsistency

**Description:** END documentation states 'Can be continued with CONT (execution resumes at next statement after END)' but GOTO example shows program terminating with 'Out of data' error, not demonstrating END behavior.

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/goto.md`

**Details:**
END.md claims CONT can resume after END, but the GOTO.md example shows:
'?Out of data in 10\nOk'
This doesn't demonstrate END's continuation behavior, only error handling.

---

#### documentation_inconsistency

**Description:** ERR/ERL documentation states ERR is reset to 0 when RESUME is executed, but ERROR documentation doesn't mention this reset behavior when discussing error simulation.

**Affected files:**
- `docs/help/common/language/statements/err-erl-variables.md`
- `docs/help/common/language/statements/error.md`

**Details:**
ERR-ERL-VARIABLES.md: 'ERR is reset to 0 when: RESUME statement is executed'

ERROR.md discusses simulating errors and setting ERR but doesn't mention the reset behavior on RESUME, which is important for error handling flow.

---

#### documentation_inconsistency

**Description:** EDIT documentation describes traditional single-character edit mode commands but then states they are not implemented, creating confusion about what EDIT actually does.

**Affected files:**
- `docs/help/common/language/statements/edit.md`

**Details:**
EDIT.md lists edit mode commands:
'I - Insert mode\nD - Delete characters\nC - Change characters\nL - List the line\nQ - Quit edit mode'

Then states:
'This implementation provides full-screen editing capabilities through the integrated editor (when using the Tk, Curses, or Web UI). The traditional single-character edit mode commands are not implemented.'

This is confusing - why document commands that don't work?

---

#### documentation_inconsistency

**Description:** Index page does not list FILES command in alphabetical listing under 'F' section, but FILES.md exists as a documented statement.

**Affected files:**
- `docs/help/common/language/statements/index.md`
- `docs/help/common/language/statements/files.md`

**Details:**
index.md 'F' section lists:
- FIELD
- FOR...NEXT

But FILES.md exists and should be listed between FIELD and FOR...NEXT alphabetically.

---

#### documentation_inconsistency

**Description:** INPUT documentation describes error message '?Redo from start' for too many values, but doesn't describe what happens with type mismatches (string vs numeric).

**Affected files:**
- `docs/help/common/language/statements/input.md`

**Details:**
INPUT.md: 'If too many values are entered, the extras are ignored with a ?Redo from start message'

But doesn't mention what happens if user enters 'ABC' when a numeric variable is expected, which is a common INPUT error scenario.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation completeness for USING clause between LPRINT and PRINT#

**Affected files:**
- `docs/help/common/language/statements/lprint-lprint-using.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
lprint-lprint-using.md provides minimal detail about USING: 'LPRINT USING works exactly like PRINT USING except output goes to the line printer' with no format string details. printi-printi-using.md provides more detail: '# for digit positions
. for decimal point
$$ for floating dollar sign
** for asterisk fill
, for thousands separator'. Both reference PRINT USING but neither fully documents the format string syntax.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-referencing of file management commands

**Affected files:**
- `docs/help/common/language/statements/merge.md`
- `docs/help/common/language/statements/new.md`

**Details:**
merge.md 'See Also' includes: KILL, LOAD, NAME, SAVE. new.md 'See Also' includes: CHAIN, CLEAR, COMMON, CONT, END, RUN, STOP, SYSTEM. Neither references the other, despite both affecting program state in memory. MERGE could reasonably reference NEW as a related command.

---

#### documentation_inconsistency

**Description:** MID$ assignment documentation has extensive 'See Also' list that includes unrelated functions

**Affected files:**
- `docs/help/common/language/statements/mid-assignment.md`

**Details:**
mid-assignment.md 'See Also' includes: ASC, CHR$, HEX$, INSTR, LEFT$, LEN, MID$, OCT$, RIGHT$, SPACE$, SPC, STR$, STRING$, VAL. Many of these (HEX$, OCT$, SPACE$, SPC, STR$, STRING$, VAL) are not directly related to string replacement operations. Other string manipulation docs (LSET, RSET) have more focused 'See Also' sections.

---

#### documentation_inconsistency

**Description:** NULL documentation references obsolete hardware without implementation note

**Affected files:**
- `docs/help/common/language/statements/null.md`

**Details:**
null.md discusses '10-character-per-second tape punches' and 'Teletypes' without an implementation note explaining these are obsolete. Compare to lprint-lprint-using.md, out.md, and poke.md which all have '⚠️ **Not Implemented**' or '⚠️ **Emulated as No-Op**' sections. NULL appears to be a no-op for modern systems but lacks this clarification.

---

#### documentation_inconsistency

**Description:** OPEN documentation does not mention append mode but PRINT# does

**Affected files:**
- `docs/help/common/language/statements/open.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
open.md lists modes as: 'O' (output), 'I' (input), 'R' (random). printi-printi-using.md states: 'PRINT# writes data to a sequential file opened for output (mode "O") or append (mode "A")'. Append mode 'A' is not documented in OPEN.

---

#### documentation_inconsistency

**Description:** OPTION BASE 'See Also' section incomplete

**Affected files:**
- `docs/help/common/language/statements/option-base.md`

**Details:**
option-base.md 'See Also' only includes: DIM, ERASE. Missing references to array-related functions like LBOUND, UBOUND which would be affected by OPTION BASE setting.

---

#### documentation_inconsistency

**Description:** PRINT documentation has inconsistent alias documentation

**Affected files:**
- `docs/help/common/language/statements/print.md`

**Details:**
print.md front matter includes 'aliases: ["?"]' but the Remarks section says '**?** - Shorthand for PRINT' without explaining this is an alias. The term 'alias' vs 'shorthand' is inconsistent.

---

#### documentation_inconsistency

**Description:** RANDOMIZE example formatting inconsistency

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
randomize.md example has inconsistent indentation and formatting. Lines like '10 RANDOMIZE' have no leading spaces, but output lines like ' .88598 .484668...' have leading spaces. The 'Ok' prompts are sometimes indented. This makes the example harder to read compared to other documentation examples.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-referencing between READ and RESTORE

**Affected files:**
- `docs/help/common/language/statements/read.md`
- `docs/help/common/language/statements/restore.md`

**Details:**
read.md 'See Also' includes: DATA, RESTORE. restore.md 'See Also' includes: DATA, READ. Both correctly reference each other, but the order is different (alphabetical vs logical).

---

#### documentation_inconsistency

**Description:** REM example has inconsistent formatting and incomplete code

**Affected files:**
- `docs/help/common/language/statements/rem.md`

**Details:**
rem.md example shows: '120 REM CALCULATE AVERAGE VELOCITY
130 FOR I=1 TO 20
140 SUM=SUM + V(I)' but then shows alternative: '120 FOR I=1 TO 20     'CALCULATE AVERAGE VELOCITY
130 SUM=SUM+V(I)
140 NEXT I'. The first example is missing NEXT I and has different line numbers for equivalent code.

---

#### documentation_inconsistency

**Description:** RENUM documentation has duplicate line numbers in example output

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
renum.md Example 6 shows output with duplicate line numbers: '1000 PRINT "OPTION 1"
1100 END
1100 PRINT "OPTION 2"
1200 END
1200 PRINT "OPTION 3"'. Lines 1100 and 1200 appear twice, which is impossible in BASIC. This appears to be a documentation error.

---

#### documentation_inconsistency

**Description:** RESET 'See Also' does not include FILES but mentions it would be useful

**Affected files:**
- `docs/help/common/language/statements/reset.md`
- `docs/help/common/language/statements/open.md`

**Details:**
reset.md 'See Also' includes: CLOSE, OPEN. It mentions 'Display directory of files' for FILES but does not link to it. open.md does not reference RESET at all.

---

#### documentation_inconsistency

**Description:** SYSTEM documentation says 'All open files are closed' but STOP documentation says 'Unlike the END statement, the STOP statement does not close files.' This creates confusion about file handling behavior.

**Affected files:**
- `docs/help/common/language/statements/system.md`
- `docs/help/common/language/statements/stop.md`

**Details:**
system.md: 'When SYSTEM is executed:
- All open files are closed'
stop.md: 'Unlike the END statement, the STOP statement does not close files.'

---

#### documentation_inconsistency

**Description:** WRITE and WRITE# documentation have inconsistent titles. WRITE is titled 'WRITE (Screen)' and WRITE# is titled 'WRITE# (File)' but the pattern isn't consistent with other statement pairs.

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md: 'title: "WRITE (Screen)"'
writei.md: 'title: "WRITE# (File)"'
This naming pattern with parenthetical clarification isn't used consistently elsewhere (e.g., PRINT vs PRINT# don't have this).

---

#### documentation_inconsistency

**Description:** Keyboard shortcuts documentation shows different shortcuts for the same actions. shortcuts.md shows ^R for Run, but tk/index.md shows Ctrl+R.

**Affected files:**
- `docs/help/common/shortcuts.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
shortcuts.md uses caret notation: '**^R** - Run program'
tk/index.md uses Ctrl notation: '**Ctrl+R** - Execute program'
While these are equivalent, inconsistent notation may confuse users.

---

#### documentation_inconsistency

**Description:** Settings documentation lists 'ui.theme' choices including 'classic' described as 'Classic BASIC green screen' but doesn't clarify if this is actually implemented or aspirational.

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
settings.md shows:
'**Choices for `ui.theme`:**
- `default` - Default color scheme
- `dark` - Dark mode
- `light` - Light mode
- `classic` - Classic BASIC green screen'
No indication if all themes are implemented or if some are planned features.

---

#### documentation_inconsistency

**Description:** Main help index references 'Ctrl+F to search within the current page' but doesn't clarify if this is browser functionality or built-in help browser functionality.

**Affected files:**
- `docs/help/index.md`

**Details:**
index.md: 'Press **Ctrl+F** to search within the current page'
This could be confusing in different UIs - is this the browser's find function or a help system feature?

---

#### documentation_inconsistency

**Description:** CLI documentation shows 'python3 mbasic' as the command but Tk documentation shows 'python3 mbasic --ui tk'. No clarification on default UI or how to specify it.

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
cli/index.md: 'python3 mbasic'
tk/index.md: 'python3 mbasic --ui tk'
Doesn't explain what happens with just 'python3 mbasic' - which UI is default?

---

#### documentation_inconsistency

**Description:** WIDTH LPRINT syntax support inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
features.md states: 'LPRINT - Line printer output (Note: LPRINT statement is supported, but WIDTH LPRINT syntax is not)'

compatibility.md states under 'Width statement': 'Note: WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.'

Both agree WIDTH LPRINT is not supported, but features.md only mentions it in a note while compatibility.md provides more context about WIDTH being a no-op.

---

#### documentation_inconsistency

**Description:** Inconsistent count of optimizations in semantic analyzer

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/features.md`

**Details:**
architecture.md states: 'The semantic analyzer implements **18 distinct optimizations**' and lists them as 'Core Optimizations (1-8)' and 'Advanced Optimizations (9-18)'

features.md states: 'The interpreter includes an advanced semantic analyzer with 18 optimizations:' and lists all 18.

Both documents agree on 18 optimizations and list the same ones, so this is consistent. However, the grouping differs slightly in presentation.

---

#### documentation_inconsistency

**Description:** Missing Web UI from getting-started.md interface options

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/mbasic/features.md`

**Details:**
getting-started.md lists three interfaces under 'Choosing a User Interface': Curses UI, CLI Mode, and Tkinter GUI. It does not mention the Web UI.

However, features.md lists 'Web - Browser-based IDE' as one of the four user interfaces, and extensions.md describes Web UI features in detail.

The getting-started.md guide should include the Web UI as an option for new users.

---

#### documentation_inconsistency

**Description:** Inconsistent description of Find and Replace availability

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/extensions.md`

**Details:**
features.md states under 'Tkinter GUI': 'Find and Replace - Search and replace text (Ctrl+F/Ctrl+H)'

extensions.md states under 'Editor Enhancements': 'Find and Replace (Tk only)'

Both agree it's Tk-only, but features.md provides keyboard shortcuts while extensions.md doesn't. This is minor but could be more consistent.

---

#### documentation_inconsistency

**Description:** Installation instructions reference non-existent requirements.txt

**Affected files:**
- `docs/help/mbasic/getting-started.md`

**Details:**
getting-started.md states: '# Install optional dependencies\npip install -r requirements.txt'

However, no requirements.txt file is shown in the documentation files provided. The documentation should either include the requirements.txt file content or specify the exact packages to install (e.g., 'pip install urwid python-frontmatter').

---

#### documentation_inconsistency

**Description:** Inconsistent command for running MBASIC

**Affected files:**
- `docs/help/mbasic/getting-started.md`

**Details:**
getting-started.md shows: '# Run MBASIC\nmbasic'

But earlier examples and other documentation consistently use 'python3 mbasic' or 'mbasic --ui cli'. The bare 'mbasic' command would only work if the script is installed in PATH or made executable. The documentation should clarify whether users need to run 'python3 mbasic.py' or if there's an installation step that creates a 'mbasic' command.

---

#### documentation_inconsistency

**Description:** Inconsistent command naming for help system

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/cli/index.md`

**Details:**
feature-reference.md refers to 'Help Command (?)' while cli/index.md uses 'HELP <topic>' and 'HELP SEARCH <keyword>'. The curses UI uses '?' while CLI uses 'HELP' command, but this distinction is not clearly documented.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for variable inspection

**Affected files:**
- `docs/help/ui/cli/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/variables.md uses 'Variable Inspection with PRINT' and 'Variables Window (GUI UIs Only)', while curses/feature-reference.md uses 'Variables Window (Ctrl+W)' and 'Variable Inspection'. The CLI doc suggests Variables Window is only for GUI, but Curses (a TUI) has it.

---

#### documentation_inconsistency

**Description:** Inconsistent feature availability documentation

**Affected files:**
- `docs/help/mbasic/not-implemented.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
not-implemented.md lists features 'not in MBASIC 5.21' (like SCREEN, PSET, etc.) but curses/feature-reference.md lists 'Not implemented' features (like Cut/Copy/Paste, Find/Replace) without clarifying whether these are:
1. Not in MBASIC 5.21 spec (so correctly not implemented)
2. In MBASIC 5.21 spec but not yet implemented in this interpreter
3. Modern UI features not part of MBASIC 5.21 at all

---

#### documentation_inconsistency

**Description:** Keyboard shortcut conflict not fully explained

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
feature-reference.md states 'Note: Uses Ctrl+V because Ctrl+S is reserved for terminal flow control' for Save File, and 'Note: Ctrl+X is used for Stop/Interrupt, Ctrl+C exits the program, and Ctrl+V is used for Save' for Cut/Copy/Paste.

This explains why standard shortcuts aren't used, but doesn't explain why Ctrl+V was chosen for Save when it's traditionally Paste. The conflict between 'Ctrl+V for Save' and 'Ctrl+V traditionally for Paste' is mentioned but not fully justified.

---

#### documentation_inconsistency

**Description:** Inconsistent command examples for starting MBASIC

**Affected files:**
- `docs/help/ui/curses/getting-started.md`
- `docs/help/ui/curses/index.md`

**Details:**
getting-started.md shows: 'mbasic --ui curses'

index.md shows: 'python3 mbasic --ui curses myprogram.bas'

files.md shows: 'python3 mbasic --ui curses myprogram.bas'

The documentation should be consistent about whether to use 'mbasic' or 'python3 mbasic' as the command.

---

#### documentation_inconsistency

**Description:** Inconsistent command for starting Tk UI

**Affected files:**
- `docs/help/ui/tk/getting-started.md`
- `docs/help/ui/tk/index.md`

**Details:**
getting-started.md shows:
'```bash
mbasic --ui tk [filename.bas]
```

Or to use the default curses UI:
```bash
mbasic [filename.bas]
```'

index.md shows:
'```bash
mbasic --ui tk [filename.bas]
```'

The getting-started page suggests curses is the default UI, but this should be verified and made consistent across all UI documentation.

---

#### documentation_inconsistency

**Description:** Help navigation instructions differ between UIs

**Affected files:**
- `docs/help/ui/curses/help-navigation.md`
- `docs/help/ui/tk/index.md`

**Details:**
curses/help-navigation.md provides detailed keyboard navigation:
'| **/** | Open search prompt |'
'| **U** | Go back to previous topic |'
'| **ESC** or **Q** | Exit help, return to editor |'

tk/index.md states:
'Use the help browser to navigate:
- **Links** - Click any blue link to navigate
- **Back button** - Return to previous page
- **Home button** - Return to this page
- **Search** - Find help topics by keyword'

These are different navigation paradigms (keyboard vs GUI) but both pages should clarify which UI they apply to more prominently.

---

#### documentation_inconsistency

**Description:** Duplicate entry in keyboard shortcuts table

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`

**Details:**
quick-reference.md lists under 'Debugger (when program running)':
'| **Ctrl+W** | Show/hide variables window |'

But also lists under 'Global Commands':
'| **Ctrl+W** | Toggle variables watch window |'

These appear to be the same feature listed twice with slightly different descriptions. Should be consolidated.

---

#### documentation_inconsistency

**Description:** Referenced file does not exist

**Affected files:**
- `docs/help/ui/tk/tips.md`

**Details:**
tk/index.md references: '[Tips & Tricks](tips.md)'

But no tips.md file was provided in the tk directory. This link will be broken.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for debug controls

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/debugging.md`

**Details:**
web/features.md lists under 'Execution Control':
'**Currently Implemented:**
- Run (Ctrl+R)
- Continue (Ctrl+G)
- Step statement (Ctrl+T)
- Step line (Ctrl+K)
- Stop (Ctrl+Q)'

web/debugging.md lists:
'**Currently Implemented:**
- `Ctrl+R` - Run program
- `Ctrl+G` - Continue (run to next breakpoint)
- `Ctrl+T` - Step statement
- `Ctrl+K` - Step line
- `Ctrl+Q` - Stop execution'

The descriptions differ slightly (e.g., 'Continue' vs 'Continue (run to next breakpoint)'). While not contradictory, consistency in descriptions would be better.

---

#### documentation_inconsistency

**Description:** Different descriptions of how to access the Web IDE

**Affected files:**
- `docs/help/ui/web/index.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
web/index.md states:
'**Access the Web IDE:**
```
https://your-server/mbasic
```'

web/getting-started.md states:
'From the command line:

```bash
mbasic --ui web
```

Then open your browser to: **http://localhost:8080**'

These describe two different access methods without clarifying their relationship. Is 'https://your-server/mbasic' a deployed version while 'localhost:8080' is local development? This should be clarified.

---

#### documentation_inconsistency

**Description:** Contradictory information about file format support

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
web/features.md lists under 'Format Support':

'**Input Formats (Currently Implemented):**
- .BAS files
- .TXT files
- ASCII text

**Output Formats (Currently Implemented):**
- Standard .BAS'

But earlier under 'File Operations' it states:
'**Currently Implemented:**
- Load .BAS files from local filesystem
- Save/download programs as .BAS files'

The first section mentions .TXT and ASCII text support, but the second only mentions .BAS files. This should be consistent.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for execution controls

**Affected files:**
- `docs/help/ui/web/getting-started.md`

**Details:**
web/getting-started.md uses different terms for the same buttons:

In toolbar section:
'**Step Line** - Execute all statements on current line, then pause (⏭️ button, Ctrl+K)'
'**Step Stmt** - Execute one statement, then pause (↻ button, Ctrl+T)'

But in the 'Step Execution' section:
'**Step Statement** - Execute one statement at a time:'
'**Step Line** - Execute all statements on one line, then pause:'

The toolbar uses 'Step Stmt' (abbreviated) while the section uses 'Step Statement' (full). Should be consistent throughout.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for file operations

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
settings.md uses:
"Click File → Save to download it to your computer"

But web-interface.md File Menu section lists:
"- **New** - Clear the editor and start a new program
- **Open** - Open a .bas file from your computer (via browser file picker)
- **Clear Output** - Clear the output area"

No **Save** option is documented in web-interface.md's File Menu, yet settings.md references it.

---

#### documentation_inconsistency

**Description:** Inconsistent instructions for loading files across library index pages

**Affected files:**
- `docs/library/business/index.md`
- `docs/library/data_management/index.md`
- `docs/library/demos/index.md`
- `docs/library/education/index.md`
- `docs/library/electronics/index.md`
- `docs/library/games/index.md`
- `docs/library/ham_radio/index.md`
- `docs/library/telecommunications/index.md`
- `docs/library/utilities/index.md`

**Details:**
Most library index pages say:
"3. **Load the file:**
   - **Web/Tkinter UI:** Click File → Open, select the downloaded file
   - **CLI:** Type `LOAD "filename.bas"`"

But some say:
"3. **Open the file:**
   - **Web/Tkinter UI:** Click File → Open, select the downloaded file
   - **CLI:** Type `LOAD "filename.bas"`"

Inconsistent use of "Load" vs "Open" terminology. Files affected:
- business/index.md: "Open the file"
- demos/index.md: "Open the file"
- education/index.md: "Open the file"
- electronics/index.md: "Open the file"
- telecommunications/index.md: "Open the file"
- data_management/index.md: "Load the file"
- games/index.md: "Load the file"
- ham_radio/index.md: "Load the file"
- utilities/index.md: "Load the file"

---

#### documentation_inconsistency

**Description:** Settings dialog validation range inconsistency

**Affected files:**
- `docs/help/ui/web/settings.md`

**Details:**
In the "Editor Tab" section, the document states:
"- **Line number increment** (number input)
  - Range: 1-1000"

But in the "Validation" section, it states:
"- **Line number increment** must be 1-1000"

And in the "Change Line Number Increment" section:
"3. Click on "Line number increment" field
4. Type new value (1-1000)"

While these are consistent with each other, the example error message shows:
"**Example error:**
```
⚠️ Error: Line number increment must be between 1 and 1000
```"

The phrasing "between 1 and 1000" could be interpreted as exclusive (2-999) rather than inclusive (1-1000). Should be "from 1 to 1000" or "between 1 and 1000 inclusive".

---

#### documentation_inconsistency

**Description:** CLI debugging capabilities described inconsistently

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states: 'CLI has full debugging capabilities through commands (BREAK, STEP, WATCH, STACK), but lacks the visual debugging interface (Variables Window, clickable breakpoints, etc.) found in Curses, Tk, and Web UIs.'

However, QUICK_REFERENCE.md only documents Curses UI debugging with breakpoints and doesn't mention CLI's text-based debugging commands. This could confuse users about CLI's actual debugging capabilities.

---

#### documentation_inconsistency

**Description:** Case handling guide references TK_UI_QUICK_START.md but quick reference is for Curses

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CASE_HANDLING_GUIDE.md 'See Also' section lists:
- `TK_UI_QUICK_START.md` - Using the graphical interface
- `QUICK_REFERENCE.md` - All MBASIC commands

But QUICK_REFERENCE.md is actually 'MBASIC Curses IDE - Quick Reference Card', not a general command reference. The description 'All MBASIC commands' is misleading.

---

#### documentation_inconsistency

**Description:** Inconsistent dependency information presentation

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/INSTALL.md`

**Details:**
CHOOSING_YOUR_UI.md states: 'CLI: Just Python 3.8+' and 'No dependencies'

INSTALL.md states: 'CLI mode: No dependencies needed (Python standard library only)'

While both are correct, the phrasing differs. CHOOSING_YOUR_UI.md could be clearer that Python 3.8+ itself is a prerequisite, not a dependency in the pip sense.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of UI names

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
Throughout CHOOSING_YOUR_UI.md, UI names are capitalized inconsistently:
- Sometimes: 'CLI', 'Curses', 'Tk', 'Web' (title case)
- Sometimes: 'CLI', 'CURSES', 'TK', 'WEB' (all caps in table headers)
- Command examples use: '--ui curses', '--ui tk', '--ui web' (lowercase)

While this doesn't create functional issues, it could be standardized for consistency.

---

#### documentation_inconsistency

**Description:** Different command examples for running MBASIC

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
INSTALL.md consistently uses: 'python3 mbasic'
CHOOSING_YOUR_UI.md uses both:
- 'python3 mbasic --ui curses'
- 'python3 mbasic --ui tk'

While both are correct, INSTALL.md could mention the --ui flag earlier to avoid confusion when users see it in other documentation.

---

#### documentation_inconsistency

**Description:** CP/M conversion instructions reference non-existent utility

**Affected files:**
- `docs/user/FILE_FORMAT_COMPATIBILITY.md`

**Details:**
FILE_FORMAT_COMPATIBILITY.md states:
'MBASIC includes a utility script for CP/M conversion:
```bash
# Convert a file to CP/M format (CRLF line endings)
python3 utils/convert_to_cpm.py yourfile.bas
```'

This utility script is mentioned but not provided in the documentation set. Users cannot verify if this utility exists or what its actual interface is.

---

#### documentation_inconsistency

**Description:** Performance numbers lack context or measurement methodology

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
CHOOSING_YOUR_UI.md provides specific performance numbers:
'Startup Time
1. **CLI**: ~0.1s (fastest)
2. **Curses**: ~0.3s
3. **Tk**: ~0.8s
4. **Web**: ~2s (browser launch)'

These numbers lack context: What hardware? What Python version? Are these averages? This could mislead users about expected performance on their systems.

---

#### documentation_inconsistency

**Description:** Help key inconsistency in quick reference

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`

**Details:**
QUICK_REFERENCE.md lists two different keys for Help:
- In 'Editor Commands' table: 'Ctrl+P | Help | Open help browser'
- In 'Help System' table: 'Ctrl+P | Anywhere | Open help browser'
- But also mentions: 'Press Ctrl+P (or ^F) within the Curses UI'

This suggests ^F (Ctrl+F) is an alternative, but it's not listed in the main command tables, creating potential confusion.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of Step/Continue/Stop availability

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md states: 'Note: Step, Continue, and Stop are available via toolbar buttons or the Run menu (no keyboard shortcuts).' However, keyboard-shortcuts.md (for Curses UI) shows keyboard shortcuts for these actions: 'Ctrl+G' for Continue, 'Ctrl+K' for Step Line, 'Ctrl+T' for Step Statement, 'Ctrl+X' for Stop. This creates confusion about whether these shortcuts exist in Tk UI or only in Curses UI.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut for Help

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md does not list a keyboard shortcut for Help in the Essential Keyboard Shortcuts table, but mentions 'Press Ctrl+? or use Help menu' in the Getting Help section. keyboard-shortcuts.md (Curses UI) shows '^F' for help and 'Ctrl+H' for help. UI_FEATURE_COMPARISON.md shows 'Ctrl+?' for Tk and 'Ctrl+H/F1' for Curses. The Tk UI help shortcut is inconsistently documented.

---

#### documentation_inconsistency

**Description:** Inconsistent Save keyboard shortcut documentation

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+S' as 'Save file' in Essential Keyboard Shortcuts. keyboard-shortcuts.md (Curses UI) lists 'Ctrl+V' as 'Save program' and 'Shift+Ctrl+V' as 'Save As'. This creates confusion about whether Tk uses Ctrl+S or Ctrl+V for save. UI_FEATURE_COMPARISON.md confirms Ctrl+S for all UIs except CLI.

---

#### documentation_inconsistency

**Description:** Ambiguous menu-only features in keyboard shortcuts

**Affected files:**
- `docs/user/keyboard-shortcuts.md`

**Details:**
keyboard-shortcuts.md lists 'Menu only' for 'Toggle execution stack window' in two places (Global Commands and Debugger sections). This is unclear - does 'Menu only' mean there's no keyboard shortcut, or that the feature is only available via menu and not via command? The documentation should clarify this.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of toolbar button names

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md uses inconsistent capitalization for toolbar buttons:
- 'Click "Step" or "Stmt" toolbar button' (quoted, capitalized)
- 'Click the **Stmt** toolbar button' (bold, capitalized)
- 'Click the **Step** toolbar button' (bold, capitalized)
- 'Click "Cont" toolbar button' (quoted, capitalized)
Sometimes quoted, sometimes bold, but always capitalized. Should standardize formatting.

---

#### documentation_inconsistency

**Description:** Inconsistent path separator in settings file location examples

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md uses forward slashes for all paths including Windows: '%APPDATA%/mbasic/settings.json'. Windows typically uses backslashes. While forward slashes work in many contexts, the documentation should clarify this or use platform-appropriate separators.

---


## Summary

- Total issues found: 677
- Code/Comment conflicts: 235
- Other inconsistencies: 442
