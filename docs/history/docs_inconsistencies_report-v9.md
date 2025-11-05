# Enhanced Consistency Report (Code + Documentation)

Generated: 2025-11-05 17:07:10
Analyzed: Source code (.py, .json) and Documentation (.md)

## 🔧 Code vs Comment Conflicts


## 📋 General Inconsistencies

### 🔴 High Severity

#### code_vs_comment

**Description:** INKEY() docstring says 'This is the MBASIC INKEY$ function' but the method is named INKEY (without $), which could confuse users expecting INKEY$ syntax

**Affected files:**
- `src/basic_builtins.py`

**Details:**
In INKEY() method around line 650:
Docstring: "Read keyboard without waiting (non-blocking input).

Returns a single character if a key is pressed, or empty string if not.
This is the MBASIC INKEY$ function."

The docstring correctly identifies this as INKEY$ in BASIC, but doesn't explain that Python method names can't include $ so it's named INKEY. Similar issue exists for INPUT() which is INPUT$ in BASIC - that method does document this (line 660: 'Method name is INPUT since Python doesn't allow $ in names'), but INKEY() should have the same clarification.

---

#### documentation_inconsistency

**Description:** Contradictory documentation about which component handles LOAD/SAVE commands

**Affected files:**
- `src/editing/manager.py`
- `src/file_io.py`

**Details:**
src/editing/manager.py docstring states:
"FILE I/O ARCHITECTURE:
This manager provides direct Python file I/O methods (load_from_file, save_to_file)
for local UIs (CLI, Curses, Tk) to load/save .BAS program files. This is separate
from the two filesystem abstractions:

1. FileIO (src/file_io.py) - For interactive LOAD/SAVE/MERGE/KILL commands
   - Interactive mode uses FileIO.load_file() for LOAD command
   - ProgramManager's load_from_file() is a convenience method for UI file dialogs"

But src/file_io.py docstring states:
"This module handles PROGRAM file operations (FILES, LOAD, SAVE, MERGE, KILL commands)."

The confusion: ProgramManager.load_from_file() is described as 'convenience for UI file dialogs' but also says 'Interactive mode uses FileIO.load_file() for LOAD command'. This creates ambiguity about which component actually handles the LOAD command in interactive mode.

---

#### code_vs_documentation

**Description:** SandboxedFileIO methods documented as STUB but list_files() is fully implemented

**Affected files:**
- `src/file_io.py`

**Details:**
SandboxedFileIO class docstring states:
"Implementation status:
- list_files(): IMPLEMENTED - delegates to backend.sandboxed_fs
- load_file(): STUB - raises IOError (requires async/await refactor)
- save_file(): STUB - raises IOError (requires async/await refactor)
- delete_file(): STUB - raises IOError (requires async/await refactor)
- file_exists(): STUB - returns False (requires async/await refactor)"

However, the actual implementation shows:
- list_files() is fully implemented and working
- load_file() raises IOError with message 'LOAD not yet implemented in web UI'
- save_file() raises IOError with message 'SAVE not yet implemented in web UI'
- delete_file() raises IOError with message 'DELETE not yet implemented in web UI'
- file_exists() returns False (stub)

The documentation correctly describes the implementation status.

---

#### code_vs_comment

**Description:** Numbered line editing feature has extensive requirements documented in comments but no validation that these requirements are met

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Lines ~110-130 document extensive requirements for numbered line editing:
'# This feature requires the following UI integration:
# - interpreter.interactive_mode must reference the UI object
# - UI must have a 'program' attribute with add_line() and delete_line() methods
# - UI must have _refresh_editor() method to update the display
# - UI must have _highlight_current_statement() for restoring execution highlighting
# If these requirements are not met, this will return an error message.'

However, the code only checks:
'if hasattr(self.interpreter, 'interactive_mode') and self.interpreter.interactive_mode:'

It then proceeds to call methods without checking if they exist:
'if hasattr(ui, 'program') and ui.program:' - checks program exists
'ui.program.add_line(line_num, complete_line)' - but doesn't check if add_line method exists
'if hasattr(ui, '_refresh_editor'):' - checks this one
'if hasattr(ui, '_highlight_current_statement') and hasattr(ui, 'runtime'):' - checks this one

The validation is inconsistent - some methods are checked with hasattr, others are not. The comment promises 'this will return an error message' if requirements aren't met, but the code will raise AttributeError instead.

---

#### code_vs_comment

**Description:** RENUM implementation comment describes AST-based approach but _renum_erl_comparison() has known limitation that contradicts the claimed precision

**Affected files:**
- `src/interactive.py`

**Details:**
Line 638-647 docstring claims:
"Delegates to renum_program() from ui_helpers.
The renum_program() implementation uses an AST-based approach (see ui_helpers.py):
1. Parse program to AST
2. Build line number mapping (old -> new)
3. Walk AST and update all line number references (via _renum_statement callback)
4. Serialize AST back to source"

But line 746-761 in _renum_erl_comparison() admits:
"IMPORTANT: Current implementation renumbers for ANY binary operator with ERL on left,
including arithmetic (ERL + 100, ERL * 2). This is broader than the manual specifies.

Rationale: Without semantic analysis, we cannot distinguish ERL=100 (comparison)
from ERL+100 (arithmetic) at parse time. We conservatively renumber all cases
to avoid missing valid line number references in comparisons.

Known limitation: Arithmetic like 'IF ERL+100 THEN...' will incorrectly renumber
the 100 if it happens to be an old line number. This is rare in practice."

The AST-based approach is claimed to update 'all line number references' correctly, but the implementation admits it cannot distinguish line numbers from arithmetic constants in ERL expressions, leading to incorrect renumbering. This is a significant limitation not mentioned in the high-level documentation.

---

#### code_vs_comment_conflict

**Description:** Comment claims GOTO/GOSUB should NOT be used in immediate mode and that PC changes would break CONT, but the code explicitly allows GOTO/GOSUB to execute and jump to program lines during statement execution

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states: "Immediate mode should NOT use GOTO/GOSUB (see help text) because PC changes would break CONT functionality for stopped programs."

But then comment continues: "IMPORTANT: GOTO/GOSUB WILL execute during the statement execution below (jumping to program lines and potentially executing code there)"

The code allows: interpreter.execute_statement(stmt) which executes GOTO/GOSUB, then restores PC with: runtime.pc = old_pc

This is contradictory - the comment says GOTO/GOSUB should NOT be used, but then explains they WILL execute.

---

#### code_vs_comment

**Description:** Comment about error_info being set before _invoke_error_handler is called contradicts the actual code flow

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~437 says: 'Note: error_info is set by the exception handler that caught the error. Multiple exception handlers in tick_pc() set error_info before calling this. We're now ready to invoke the error handler'

However, looking at the code at lines ~368-388, the error_info is set AFTER catching the exception but BEFORE calling _invoke_error_handler:

except Exception as e:
    already_in_error_handler = (self.state.error_info is not None)
    error_code = self._map_exception_to_error_code(e)
    self.state.error_info = ErrorInfo(
        error_code=error_code,
        pc=pc,
        error_message=str(e)
    )
    if self.runtime.has_error_handler() and not already_in_error_handler:
        self._invoke_error_handler(error_code, pc)

The comment is technically correct but misleading - it says 'Multiple exception handlers' but there's only ONE exception handler in tick_pc() that sets error_info. The comment implies there are multiple places setting error_info before calling _invoke_error_handler, but the code shows only one location.

---

#### code_vs_comment

**Description:** OPTION BASE comment claims 'Duplicate Definition' for any array existence, but code only checks _arrays dict

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_optionbase() says:
"MBASIC 5.21 gives 'Duplicate Definition' if:
1. OPTION BASE has already been executed, OR
2. Any arrays have been created (both explicitly via DIM and implicitly via first use like A(5)=10)
   This applies regardless of the current array base (0 or 1).
Note: The check len(self.runtime._arrays) > 0 catches all array creation because both
explicit DIM and implicit array access (via set_array_element) update runtime._arrays."

The code checks: if len(self.runtime._arrays) > 0:

This assumes _arrays is updated for implicit array creation. However, if set_array_element() auto-dimensions arrays without updating _arrays first, this check would fail. The comment's claim that "both explicit DIM and implicit array access update runtime._arrays" needs verification in the Runtime class.

---

#### code_vs_comment

**Description:** Comment in execute_list() warns about potential sync issues but provides no mechanism to detect or handle them

**Affected files:**
- `src/interpreter.py`

**Details:**
The comment states:
"Implementation note: Outputs from line_text_map (original source text), not regenerated from AST. This preserves original formatting/spacing/case. The line_text_map is maintained by ProgramManager and is kept in sync with the AST during program modifications (add_line, delete_line, RENUM, MERGE). If line_text_map becomes out of sync with AST (programming error), LIST output may be incorrect."

The comment acknowledges a potential critical bug (out-of-sync data structures) but the code has no validation, assertion, or error handling to detect this condition. If this is a real concern, the code should validate sync or the comment should be removed.

---

#### code_vs_comment

**Description:** Comment in execute_step() claims tick() supports step modes but doesn't verify this or explain the disconnect

**Affected files:**
- `src/interpreter.py`

**Details:**
The comment states:
"Status: The tick() method supports step_statement and step_line modes, but this immediate STEP command is not yet connected to that infrastructure."

This is a significant inconsistency: the comment claims tick() has functionality that this command should use, but provides no explanation of why they're disconnected or how to connect them. This suggests incomplete implementation or outdated comments.

---

#### Code vs Documentation inconsistency

**Description:** input_line() documentation promises space preservation but all implementations fail to deliver this

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/console.py`
- `src/iohandler/curses_io.py`
- `src/iohandler/web_io.py`

**Details:**
base.py documents: "Similar to input() but SHOULD preserve leading/trailing spaces and not interpret commas as field separators."

Then contradicts itself: "Note: This is the intended behavior for MBASIC LINE INPUT compatibility. Current implementations (console, curses, web) do NOT fully preserve leading/trailing spaces due to underlying platform limitations"

console.py: "Note: Current implementation does NOT preserve leading/trailing spaces as documented in base class. Python's input() automatically strips them."

curses_io.py: "Note: Current implementation does NOT preserve leading/trailing spaces as documented in base class. curses getstr() strips trailing spaces."

web_io.py: "Note: Current implementation does NOT preserve leading/trailing spaces as documented in base class. HTML input fields strip spaces."

This is a documented feature that is explicitly not implemented in any backend.

---

#### code_vs_comment

**Description:** Comment claims lexer tokenizes 'LINE INPUT' as LINE_INPUT but code checks for LINE_INPUT token in wrong context

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() method:
Comment says: "Note: The lexer tokenizes LINE INPUT as LINE_INPUT regardless of position"

But the code checks for LINE_INPUT token AFTER parsing the prompt:
```python
if self.match(TokenType.LINE_INPUT):
    line_mode = True
    self.advance()
```

This suggests the syntax is: INPUT \"prompt\";LINE var$ (LINE after prompt)
However, standard BASIC syntax is: LINE INPUT \"prompt\"; var$ (LINE before INPUT)

The comment and code suggest confusion about whether this is checking for LINE keyword in INPUT statement vs LINE INPUT as a separate statement type.

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

**Description:** Comment claims line numbers are variable width in both display AND editing, but code uses fixed 5-character width when reformatting pasted content

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring (lines 191-200) states:
"Note: This is NOT a true columnar layout with fixed column boundaries.
Line numbers have variable width in both display (_format_line returns variable-width
numbers) and editing (keypress method uses _parse_line_number to find code boundaries
dynamically). The layout is a formatted string with three fields, not three columns."

But _parse_line_numbers method (lines 991, 1024) uses fixed width:
"line_num_formatted = f\"{num_str:>5}\""

Additional comment at line 976 contradicts class docstring:
"Note: When reformatting pasted content, line numbers are right-justified to 5 characters
for consistent alignment. This differs from the variable-width formatting used in
_format_line() for display."

---

#### internal_inconsistency

**Description:** Inconsistent line number formatting: _format_line uses variable width, _parse_line_numbers uses fixed 5-character width

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_format_line (line 680):
"line_num_str = f\"{line_num}\"  # Variable width, no padding"

_parse_line_numbers (lines 991, 1024):
"line_num_formatted = f\"{num_str:>5}\"  # Fixed 5-character width with right justification"

This creates inconsistent display: lines created by _format_line have variable-width numbers (e.g., \" 10 PRINT\"), while pasted lines reformatted by _parse_line_numbers have fixed-width numbers (e.g., \"    10 PRINT\").

---

#### code_vs_comment

**Description:** Comment claims RUN = CLEAR + GOTO but implementation may differ

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program() method:

Comment says: "# Reset runtime with current program - RUN = CLEAR + GOTO first line (or start_line if specified)"

However, the subsequent code shows:
        # If start_line is specified (e.g., RUN 100), set PC to that line
        # This must happen AFTER interpreter.start() because start() calls setup()
        # which resets PC to the first line in the program. By setting PC here,
        # we override that default and begin execution at the requested line.
        if start_line is not None:
            from src.runtime import PC
            # Verify the line exists
            if start_line not in self.program.line_asts:
                self.output_buffer.append(f"?Undefined line {start_line}")
                self._update_output()
                self.status_bar.set_text("Error")
                self.running = False
                return False
            # Set PC to start at the specified line (after start() has built statement table)
            self.runtime.pc = PC.from_line(start_line)

The comment suggests RUN with a line number is equivalent to CLEAR + GOTO, but the implementation shows it's actually setting the PC after a full reset, which may have different semantics than a GOTO (e.g., GOTO doesn't clear variables, but this does).

---

#### code_inconsistency

**Description:** Duplicate code: CapturingIOHandler class is defined inline in _execute_immediate with comment about duplication

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method (line ~1080):
# Need to create the CapturingIOHandler class inline
# (duplicates definition in _run_program - consider extracting to shared location)
class CapturingIOHandler:
    def __init__(self):
        self.output_buffer = []
        self.debug_enabled = False
    ...

Comment explicitly acknowledges this is duplicate code that should be extracted, indicating a code smell/technical debt.

---

#### code_inconsistency

**Description:** interactive_menu.py imports keybindings module but keybinding_loader.py shows the proper way to load keybindings from JSON - inconsistent approaches

**Affected files:**
- `src/ui/interactive_menu.py`
- `src/ui/keybinding_loader.py`

**Details:**
interactive_menu.py uses:
from . import keybindings as kb

Then references kb.NEW_DISPLAY, kb.OPEN_DISPLAY, etc.

But keybinding_loader.py provides KeybindingLoader class that loads from JSON:
config_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"

This suggests two different keybinding systems exist: a Python module (keybindings.py) with constants, and a JSON-based system. The codebase should use one consistent approach.

---

#### code_vs_comment

**Description:** Variables window column heading text doesn't match sort behavior description

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _create_variables_window() at line ~1050:
"tree.heading('#0', text='↓ Variable (Last Accessed)')"

But the default sort is by 'accessed' timestamp in descending order (most recent first). The heading says 'Last Accessed' which is ambiguous - it could mean 'most recently accessed' or 'least recently accessed'. The arrow suggests descending order, but the text doesn't clarify the sort direction.

Additionally, the _on_variable_heading_click() docstring says:
"Arrow area (left ~20 pixels): Toggle sort direction
Rest of heading: Cycle sort column (for Variable) or set column (for Type/Value)"

But the comment at line ~1070 says Type and Value columns are 'not sortable', which conflicts with 'set column (for Type/Value)'.

---

#### code_vs_comment

**Description:** Comment in _sync_program_to_runtime claims PC is preserved 'only if execution is running' but code checks both self.running AND not self.paused_at_breakpoint

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines ~1593-1598:
If execution is currently running (self.running=True and not paused),
the PC is preserved. Otherwise, PC is set to halted state to prevent
accidental execution.

Code at line ~1619:
if self.running and not self.paused_at_breakpoint:

The comment says 'not paused' but the code specifically checks 'not self.paused_at_breakpoint'. These might be different states - there could be other pause conditions besides breakpoints. The comment oversimplifies the actual condition.

---

#### code_vs_comment

**Description:** Comment in _on_key_press says 'Clear yellow statement highlight when user starts editing' but this happens for ANY key press, not just editing keys

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment says: "# Clear yellow statement highlight when user starts editing
# This prevents visual artifact where statement highlight remains on part of a line
# after text is modified (occurs because highlight is tag-based and editing shifts positions)"

But the code clears highlight BEFORE checking if the key is valid:
if self.paused_at_breakpoint:
    self._clear_statement_highlight()

# Schedule blank line removal after key is processed
self.root.after(10, self._remove_blank_lines)

# Ignore special keys (arrows, function keys, modifiers, etc.)
if len(event.char) != 1:
    return None

This means arrow keys, function keys, etc. will also clear the highlight even though they don't edit the text. The comment should say 'when user presses any key' or the code should move the clear after validation.

---

#### code_vs_comment

**Description:** Contradictory documentation about input() vs input_line() behavior regarding inline input field usage

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In TkIOHandler.input() docstring:
"Input from user via inline input field (with fallback to modal dialog).
...
Prefers inline input field below output pane when backend is available,
but falls back to modal dialog if backend is not available."

In TkIOHandler.input_line() docstring:
"Input complete line from user via modal dialog.
...
Unlike input() which prefers inline input field, this ALWAYS uses
a modal dialog regardless of backend availability."

This creates an inconsistency: Why does LINE INPUT always use modal dialog while INPUT uses inline field? The docstrings don't explain the design rationale. This could confuse users expecting consistent input behavior.

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

**Description:** INPUT handling comment contradicts actual implementation location

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1730 comment:
  # INPUT handling: When INPUT statement executes, the immediate_entry input box
  # is focused for user input (see _execute_tick() lines ~1886-1888).
But _execute_tick starts at line ~1850, and the INPUT handling code is at lines ~1870-1890, not 1886-1888. Line numbers in comment are approximate but misleading.

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

**Description:** Help system URL mismatch - code points to localhost/mbasic_docs but documentation describes different structure

**Affected files:**
- `src/ui/web_help_launcher.py`
- `docs/help/README.md`

**Details:**
web_help_launcher.py defines:
HELP_BASE_URL = 'http://localhost/mbasic_docs'

But docs/help/README.md describes help structure as:
- /common - Shared content
- /ui/cli, /ui/curses, /ui/tk, /ui/web - UI-specific

The code constructs URLs like 'http://localhost/mbasic_docs/ui/tk/' but there's no documentation about how the docs/help directory structure maps to the web server's URL structure. Is docs/help/common served at /mbasic_docs/ or /mbasic_docs/common/?

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

**Description:** FOR-NEXT documentation contains contradictory information about loop execution. States 'Loop executes at least once if start equals end (regardless of STEP value)' but earlier states loop terminates if variable exceeds ending value considering STEP direction.

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
Operation section states:
'2. If variable exceeds ending value (y) considering STEP direction, loop terminates'

But Features section states:
'- Loop executes at least once if start equals end (regardless of STEP value)'

These contradict: if start=end and STEP is negative, the variable would immediately exceed the ending value (be less than it), so by rule 2 it should terminate without executing. But the feature says it executes at least once.

---

#### documentation_inconsistency

**Description:** WIDTH documentation contradicts itself about LPRINT support

**Affected files:**
- `docs/help/common/language/statements/width.md`

**Details:**
Implementation Note says 'The "WIDTH LPRINT" syntax is not supported (parse error)' but the Syntax section shows 'WIDTH LPRINT <integer expression>' as if it were valid. The Remarks section also discusses LPRINT option behavior.

---

#### documentation_inconsistency

**Description:** Broken reference to getting-started.md from index

**Affected files:**
- `docs/help/index.md`
- `docs/help/mbasic/getting-started.md`

**Details:**
index.md links to '[Getting Started](mbasic/getting-started.md)' but the actual file path based on other docs should be 'common/getting-started.md' or the link is correct but file is missing from provided docs.

---

#### documentation_inconsistency

**Description:** Contradictory information about PEEK/POKE memory state persistence

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states: 'PEEK does NOT return values written by POKE - no memory state is maintained'

compatibility.md states the same: 'PEEK does NOT return values written by POKE - no memory state is maintained'

However, both documents are internally consistent. The issue is that architecture.md describes PEEK as returning 'random integer 0-255' while compatibility.md also says 'Returns random integer 0-255 (for RNG seeding compatibility)'. This is consistent, not contradictory.

---

#### documentation_inconsistency

**Description:** Contradictory information about LPRINT support

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/features.md`

**Details:**
compatibility.md states under 'Terminal Differences': 'Width statement: WIDTH 80 - Accepted (no-op). Note: WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.'

features.md lists under 'Console I/O': 'LPRINT - Line printer output' as a supported feature.

This creates confusion: if LPRINT is supported as a feature, why does compatibility.md say 'WIDTH LPRINT syntax is not supported'? These may be different things (LPRINT command vs WIDTH LPRINT syntax), but the documentation doesn't clarify this distinction.

---

#### documentation_inconsistency

**Description:** Execution Stack access method inconsistency

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
feature-reference.md states 'Execution Stack (Menu only)' with instructions to use Ctrl+U menu, but cli/debugging.md describes 'STACK' command for viewing call stack. The curses UI appears to have menu-only access while CLI has a direct command, but this is not clearly explained in either document.

---

#### documentation_inconsistency

**Description:** Settings management not documented for Curses UI

**Affected files:**
- `docs/help/ui/cli/settings.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/settings.md provides detailed documentation for SHOWSETTINGS and SETSETTING commands in CLI mode. feature-reference.md lists 36 features for Curses UI but does not mention settings management at all. It's unclear if settings can be changed in Curses UI or if this is CLI-only.

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

**Description:** Conflicting information about variable sorting default

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
variables.md states under Sort Modes: '**Accessed**: Most recently accessed (read or written) - default, newest first'

quick-reference.md states: '**s** | Cycle sort mode (Accessed → Written → Read → Name)'

This confirms 'Accessed' is first in the cycle, but variables.md should clarify if this is the default when the window first opens, or just the first option when cycling.

---

#### documentation_inconsistency

**Description:** Settings shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/settings.md`
- `docs/help/ui/curses/index.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
settings.md states: '**Keyboard shortcut:** `Ctrl+,`'

quick-reference.md confirms: '**Ctrl+,** | Settings' under Global Commands

But index.md does not mention settings or Ctrl+, in its feature list or navigation guide. The settings feature should be documented in the main index.

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

**Description:** Contradictory information about boolean values in SET command

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states in the 'Type Conversion' section: 'Booleans: true or false (lowercase, no quotes in commands; use true/false in JSON files)'. However, the examples show: 'SET "editor.auto_number" true' without quotes. This is consistent. But the note says 'lowercase, no quotes in commands' which implies the command syntax uses lowercase true/false, while JSON also uses true/false. The phrasing 'use true/false in JSON files' is redundant since it's the same as commands.

---

### 🟡 Medium Severity

#### documentation_inconsistency

**Description:** Version mismatch between setup.py and documentation in ast_nodes.py

**Affected files:**
- `setup.py`
- `src/ast_nodes.py`

**Details:**
setup.py declares version="0.99.0" with comment "Reflects ~99% implementation status (core complete)", but ast_nodes.py header says "Abstract Syntax Tree (AST) node definitions for MBASIC 5.21" without version info. The setup.py suggests near-complete implementation while the code contains many statement nodes that may not be fully implemented.

---

#### code_comment_conflict

**Description:** InputStatementNode docstring contradicts field semantics for suppress_question

**Affected files:**
- `src/ast_nodes.py`

**Details:**
The docstring states:
"Note: The semicolon has different meanings depending on its position:
- After a prompt string: INPUT "prompt"; var  → shows "prompt? "
- Immediately after INPUT keyword: INPUT; var → suppresses "?" (no prompt)
The suppress_question field is True only for the second case (INPUT; without prompt)."

However, this creates ambiguity: if INPUT "prompt"; var shows "prompt? ", then the question mark is NOT suppressed. But the field name "suppress_question" suggests it controls whether the "?" appears. The docstring should clarify that suppress_question=True means INPUT; (no prompt at all), while a prompt string with semicolon still shows "?".

---

#### code_comment_conflict

**Description:** CallStatementNode has arguments field that parser doesn't support

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode docstring states:
"Note: The 'arguments' field exists for potential future compatibility with other BASIC dialects (e.g., CALL ROUTINE(args)), but extended syntax is not currently supported by the parser. Standard MBASIC 5.21 only accepts a single address expression."

The arguments field is defined as:
arguments: List['ExpressionNode']  # Reserved for future extended syntax (not currently parsed)

This creates confusion: the field exists in the AST node but is never populated by the parser. This could lead to bugs if code assumes the field is valid. Better design would be to add the field only when the feature is implemented.

---

#### code_comment_conflict

**Description:** PrintStatementNode has keyword_token field but other similar nodes don't consistently have this

**Affected files:**
- `src/ast_nodes.py`

**Details:**
PrintStatementNode has:
keyword_token: Optional[Token] = None  # Token for PRINT keyword (for case handling)

IfStatementNode has:
keyword_token: Optional[Token] = None  # Token for IF keyword
then_token: Optional[Token] = None     # Token for THEN keyword
else_token: Optional[Token] = None     # Token for ELSE keyword (if present)

ForStatementNode has:
keyword_token: Optional[Token] = None  # Token for FOR keyword
to_token: Optional[Token] = None       # Token for TO keyword
step_token: Optional[Token] = None     # Token for STEP keyword (if present)

But many other statement nodes (GotoStatementNode, GosubStatementNode, ReturnStatementNode, etc.) don't have keyword_token fields. This inconsistency suggests incomplete implementation of case-preserving functionality across all statement types.

---

#### code_vs_comment

**Description:** Comment in case_string_handler.py claims identifiers always preserve original case, but the code in basic_builtins.py INPUT() method has a comment describing file_info access pattern that references EOF() method, suggesting documentation of internal implementation details rather than user-facing behavior

**Affected files:**
- `src/basic_builtins.py`

**Details:**
In case_string_handler.py line ~60:
# Identifiers always preserve their original case in display.
# Unlike keywords, which can be forced to a specific case policy,
# identifiers (variable/function names) retain their case as typed.
# This matches MBASIC 5.21 behavior where identifiers are case-insensitive
# for matching but preserve display case.
# Note: We bypass the identifier_table here since identifiers always return
# original_text. The table could be used in future for conflict detection.

In basic_builtins.py INPUT() method line ~680:
# self.runtime.files[file_num] returns a dict with 'handle', 'mode', 'eof' keys
# Extract the file handle from the file_info dict to perform read operations
# (see EOF() method for the same access pattern)

This is not an inconsistency per se, but the INPUT() comment is overly detailed about internal implementation.

---

#### code_vs_comment

**Description:** UsingFormatter.format_numeric_field() has complex logic for handling negative zero that may not match the comment's explanation

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Around line 240 in format_numeric_field():
Comment: "# Determine sign - preserve negative sign for values that round to zero.
# This matches BASIC behavior where -0.001 formatted with no decimal places
# displays as \"-0\" (not \"0\"). Positive values that round to zero display as \"0\"."

Code:
if rounded == 0 and original_negative:
    is_negative = True
else:
    is_negative = rounded < 0

The logic seems correct, but the comment could be clearer that 'original_negative' is determined before rounding (line 235: original_negative = value < 0), which is the key to preserving the negative sign.

---

#### code_vs_comment

**Description:** Comment claims identifiers bypass the identifier_table and always return original_text, but the code still calls get_identifier_table() which creates the table even though it's not used

**Affected files:**
- `src/case_string_handler.py`

**Details:**
In case_keepy_string() method around line 60:
Comment: "# Note: We bypass the identifier_table here since identifiers always return
# original_text. The table could be used in future for conflict detection."

Code immediately before the return:
if setting_prefix == "idents":
    # [comment block]
    return original_text

However, the class method get_identifier_table() is defined and would create a table if called, but it's never actually called in the idents branch. This is not a bug, but the comment could be clearer that the table infrastructure exists but is intentionally unused for identifiers currently.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for filesystem abstraction purposes

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py states:
"1. FileIO (this file) - Program management operations (LOAD/SAVE/FILES/KILL)
   - Purpose: Load .BAS programs into memory, save from memory to disk"

But src/filesystem/base.py states:
"2. FileSystemProvider (this file) - Runtime file I/O
   - Purpose: File I/O from within running BASIC programs"

The inconsistency: FileIO says 'save from memory to disk' but SandboxedFileIO implementation uses 'Python server memory virtual filesystem', not disk. The documentation should clarify that 'disk' is implementation-dependent.

---

#### documentation_inconsistency

**Description:** ProgramManager docstring claims it's not suitable for Web UI but doesn't explain the architectural relationship

**Affected files:**
- `src/editing/manager.py`

**Details:**
ProgramManager docstring states:
"Note: Not suitable for Web UI due to direct filesystem access - Web UI uses
FileIO abstraction in interactive.py instead."

But later in the same docstring:
"Why ProgramManager has its own file I/O methods:
- Provides simpler API for local UIs that don't need FileIO abstraction
- Only used by local UIs (CLI, Curses, Tk) where filesystem access is safe
- Web UI uses FileIO abstraction in interactive.py instead"

The inconsistency: The first statement says ProgramManager is 'not suitable' for Web UI, but the explanation shows it's more about architectural choice (Web UI uses FileIO abstraction) rather than technical unsuitability. The ProgramManager could theoretically work with Web UI if given a sandboxed FileIO implementation.

---

#### code_vs_documentation

**Description:** ProgramManager.merge_from_file() return type documentation incomplete

**Affected files:**
- `src/editing/manager.py`

**Details:**
ProgramManager.merge_from_file() docstring states:
"Returns:
    Tuple of (success, errors, lines_added, lines_replaced)
    success: True if at least one line loaded successfully
    errors: List of (line_number, error_message) for failed lines
    lines_added: Count of new lines added
    lines_replaced: Count of existing lines replaced"

The code implementation:
```python
if total_success > 0:
    return (True, errors, lines_added, lines_replaced)
else:
    return (False, errors, 0, 0)
```

The documentation is accurate. However, it's worth noting that when success=False, lines_added and lines_replaced are always 0, which is implicit but not explicitly documented.

---

#### code_vs_comment

**Description:** Comment claims PC is not saved/restored but this contradicts the safety model described in docstrings

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Line ~200 comment states: 'Note: We do not save/restore the PC before/after execution. This allows statements like RUN to change execution position. Normal statements (PRINT, LET, etc.) don't modify PC anyway.'

However, the class docstring extensively documents that immediate mode should only execute when interpreter is in safe states (idle, paused, at_breakpoint, done, error, waiting_for_input) and NOT when running. The comment suggests RUN can be executed in immediate mode, but this would violate the safety constraints since RUN would start program execution.

The docstring states: 'DO NOT execute when status is: running - Program is executing (tick() is running) and not halted'

If RUN is allowed in immediate mode, it would transition from a safe state (paused/idle) to 'running', which then makes immediate mode unsafe. This creates a logical inconsistency.

---

#### code_vs_documentation

**Description:** Help text warns against GOTO/GOSUB but doesn't explain the actual behavior or safety implications

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The help text states:
'• GOTO, GOSUB, and control flow statements are not recommended (they will execute but may produce unexpected results)'

This is vague and potentially dangerous. The docstring emphasizes safety constraints about when immediate mode can execute, but doesn't explain what happens if someone executes 'GOTO 100' in immediate mode. Does it:
1. Jump to line 100 and continue execution (violating the safety model)?
2. Fail with an error?
3. Set PC but not start execution?

The comment at line ~200 says 'This allows statements like RUN to change execution position' which suggests control flow IS allowed, contradicting the 'not recommended' warning.

---

#### code_vs_documentation

**Description:** Help text claims INPUT is not allowed but OutputCapturingIOHandler.input() raises RuntimeError with different message

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The help text in _show_help() doesn't mention INPUT at all in the limitations section.

However, OutputCapturingIOHandler.input() method explicitly raises:
'raise RuntimeError("INPUT not allowed in immediate mode")'

This is a significant limitation that should be documented in the help text. Users might try to use INPUT in immediate mode and get a confusing error.

---

#### code_vs_comment

**Description:** Comment claims EDIT and AUTO are meta-commands that can't be parsed as BASIC statements, but AUTO is actually parsed and executed through execute_immediate() like other commands

**Affected files:**
- `src/interactive.py`

**Details:**
Line 186-189 comment states:
"# Meta-commands (editor commands that manipulate program source)
# AUTO and EDIT are meta-commands that require special handling - they can't be
# parsed as BASIC statements, so they're handled directly here."

But line 191-192 shows AUTO is handled specially:
"if command == "AUTO":
    self.cmd_auto(args)"

While line 197-202 shows everything else (not just EDIT) goes through parser:
"else:
    # Everything else (including LIST, DELETE, RENUM, FILES, RUN, LOAD, SAVE, MERGE, SYSTEM, NEW, PRINT, etc.)
    # goes through the real parser as immediate mode statements
    try:
        self.execute_immediate(cmd)"

The comment is inconsistent - it claims both AUTO and EDIT can't be parsed, but only EDIT is handled specially. AUTO goes through execute_immediate() path.

---

#### code_vs_comment

**Description:** EDIT command docstring claims count prefixes and search commands are 'not yet implemented' but provides no implementation for digit recognition at all

**Affected files:**
- `src/interactive.py`

**Details:**
Line 826-828 in cmd_edit() docstring:
"Note: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K) are not yet implemented.
Digits are not recognized as command prefixes and will be processed as individual
characters (e.g., '5D' processes '5' as unknown, then 'D' deletes one character)."

The implementation (lines 870-950) has no code path for handling digits at all - they fall through to no action. The comment says digits 'will be processed as individual characters' but there's no code showing what happens to unrecognized characters. The actual behavior is that digits are silently ignored (no output, no error), not 'processed as individual characters'.

---

#### code_vs_comment

**Description:** cmd_chain() docstring describes COMMON variable handling but implementation comment reveals variables may not be found due to type suffix ambiguity

**Affected files:**
- `src/interactive.py`

**Details:**
Line 545-551 docstring states:
"Runtime selection:

Save variables based on CHAIN options:
- MERGE (merge=True): overlay mode, preserves all variables
- ALL (all_flag=True): passes all variables to new program
- Neither: only pass COMMON variables (if defined)"

But lines 565-580 implementation reveals:
"# Note: common_vars stores base names (e.g., 'i'), but actual variables
# may have type suffixes (e.g., 'i%', 'i$') based on DEF statements
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

The docstring makes COMMON variable passing sound straightforward, but the implementation shows it's complex and may silently fail to pass variables if the type suffix doesn't match. This is a significant behavioral detail missing from the high-level documentation.

---

#### code_vs_comment_conflict

**Description:** Comment references help text about GOTO/GOSUB restrictions in immediate mode, but no verification that such help text exists or that the restriction is enforced

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states: "Immediate mode should NOT use GOTO/GOSUB (see help text)"

However, the code does not prevent GOTO/GOSUB from being used in immediate mode. It executes them and then restores the PC. There's no enforcement of the restriction mentioned in the comment, only a workaround for the side effects.

---

#### code_vs_comment

**Description:** InterpreterState docstring describes checking order for UI code examining completed state, but the actual checking order during execution (in tick_pc()) is different and more complex

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring says: 'Note: The suggested checking order below is for UI code that examines state AFTER execution completes. During execution (in tick_pc()), the actual checking order is: 1. pause_requested, 2. halted, 3. break_requested, 4. breakpoints, 5. input_prompt, 6. errors (handled via exceptions).'

However, the actual tick_pc() code checks in this order:
1. pause_requested (line ~300)
2. pc.halted() or runtime.halted (line ~307)
3. break_requested (line ~315)
4. breakpoints (line ~326)
5. input_prompt (line ~391)
6. step mode checks (lines ~408-415)

The docstring lists 'errors (handled via exceptions)' as step 6, but errors are actually handled via try/except blocks throughout the method, not as a sequential check. The step mode checks are not mentioned in the docstring at all.

---

#### code_vs_comment

**Description:** Comment about return_stmt validation in execute_return() has incorrect boundary description

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1009 says: 'return_stmt is 0-indexed offset into statements array. Valid range: 0 to len(statements) (inclusive). - 0 to len(statements)-1: Normal statement positions - len(statements): Special sentinel meaning "GOSUB was last statement, continue at next line" Values > len(statements) indicate the statement was deleted (validation error).'

But the validation code at line ~1014 is:
if return_stmt > len(line_statements):
    raise RuntimeError(...)

This checks for 'strictly greater than len(statements)', which means return_stmt == len(statements) is VALID (not an error). However, the comment says 'Values > len(statements) indicate the statement was deleted', which is ambiguous - does '>' mean 'greater than' or 'greater than or equal to'? The code clarifies this: only values STRICTLY greater than len(statements) are errors. The comment should say '>= len(statements) + 1' or 'strictly greater than len(statements)' to be precise.

---

#### code_vs_comment

**Description:** Comment about NEXT processing order conflicts with actual implementation behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1050 says: 'NEXT I, J, K processes variables left-to-right: I first, then J, then K. If any loop continues (not finished), execution jumps back to the loop body and remaining variables are not processed. This differs from separate statements (NEXT I: NEXT J: NEXT K) which would always execute sequentially.'

The code at lines ~1067-1077 implements this:
for var_node in var_list:
    var_name = var_node.name + (var_node.type_suffix or "")
    should_continue = self._execute_next_single(var_name, var_node=var_node)
    if should_continue:
        return

However, the comment is slightly misleading about 'separate statements'. The phrase 'NEXT I: NEXT J: NEXT K' suggests three separate NEXT statements on the same line (colon-separated), but those would NOT 'always execute sequentially' - if NEXT I loops back, the subsequent statements wouldn't execute either. The comment should clarify it means 'separate NEXT statements on different lines' or 'three separate NEXT statement nodes'.

---

#### code_vs_comment

**Description:** Comment claims WEND pops loop before WHILE re-evaluation, but code shows WHILE re-pushes if condition true

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at execute_wend() says:
"Pop the loop from the stack AFTER setting the jump target.
The WHILE will re-push if the condition is still true, or skip the
loop body if the condition is now false. This ensures clean stack state.
Note: We pop here (before execution reaches WHILE) so that if an error occurs during
WHILE condition evaluation, the loop is already popped (correct error handling behavior)."

But this creates a problem: if WHILE condition is true, it calls push_while_loop() again, meaning the loop is pushed twice (once by original WHILE, once by re-evaluation). The comment suggests this is intentional for "clean stack state" but doesn't explain why double-pushing is correct.

---

#### code_vs_comment

**Description:** Comment claims CLEAR preserves user_functions but code doesn't show this

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_clear() says:
"Note: Preserved state for CHAIN compatibility:
  - runtime.common_vars (list of COMMON variable names - the list itself, not variable values)
  - runtime.user_functions (DEF FN functions)
Note: Files and field_buffers are NOT preserved (cleared above)."

However, the code only calls:
- self.runtime.clear_variables()
- self.runtime.clear_arrays()
- Clears files and field_buffers

It does NOT explicitly preserve user_functions. The comment claims user_functions are preserved, but there's no code showing clear_variables() or clear_arrays() avoids touching user_functions. This needs verification in the Runtime class implementation.

---

#### code_vs_comment

**Description:** INPUT state machine comment doesn't mention input_file_number field

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_input() describes state machine:
"State machine for keyboard input (file input is synchronous):
1. If state.input_buffer has data: Use buffered input (from provide_input())
2. Otherwise: Set state.input_prompt, input_variables, and return (pauses execution)
3. UI calls provide_input() with user's input line
4. On next tick(), buffered input is used (step 1) and state vars are cleared"

But the code also sets: self.state.input_file_number = None

The comment doesn't mention input_file_number as part of the state machine, even though it's set alongside input_prompt and input_variables. This field is presumably used to distinguish keyboard vs file input during resumption.

---

#### code_vs_comment

**Description:** RESET comment claims it doesn't catch errors, but CLEAR comment says it does

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_reset():
"Note: Unlike CLEAR, RESET doesn't catch file close errors - they propagate to caller"

But in execute_clear():
"Note: Errors during file close are silently ignored (bare except: pass below)"

RESET code shows:
for file_num in list(self.runtime.files.keys()):
    self.runtime.files[file_num]['handle'].close()
    del self.runtime.files[file_num]

This has no try/except, so errors DO propagate. However, CLEAR has try/except with pass. The RESET comment correctly states the difference, but it's worth noting this behavioral difference is intentional.

---

#### code_vs_comment

**Description:** Comment claims LSET/RSET fallback is 'documented behavior' but no actual documentation exists in the codebase for this extension

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_lset() and execute_rset(), the comment states:
"Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field variables (used with FIELD statement for random file access). This fallback is a deliberate extension for compatibility with code that uses LSET for general string formatting. This is documented behavior, not a bug."

However, this extension behavior is not documented anywhere else in the provided code. The comment claims it's 'documented behavior' but provides no reference to where this documentation exists.

---

#### code_vs_comment

**Description:** Comment claims string concatenation limit applies only to PLUS operator, but doesn't clarify if other operations should enforce it

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_binaryop(), the comment states:
"# Enforce 255 character string limit for concatenation (MBASIC 5.21 compatibility)
# Note: This check only applies to concatenation via PLUS operator.
# Other string operations (MID$, LSET, RSET, INPUT) do not enforce this limit."

This creates an inconsistency: if MBASIC 5.21 has a 255 character string limit, why would only PLUS enforce it? The comment suggests other operations can create strings > 255 characters, which would be inconsistent with a global string length limit. This needs clarification about whether the limit is per-operation or global.

---

#### code_vs_comment

**Description:** Comment in execute_cont() describes behavior distinction but doesn't explain why this design choice was made

**Affected files:**
- `src/interpreter.py`

**Details:**
The comment states:
"Behavior distinction (MBASIC 5.21 compatibility):
- STOP statement: Sets runtime.stopped=True, allowing CONT to resume
- Break (Ctrl+C): Sets runtime.halted=True but NOT stopped=True, so CONT fails
This is intentional: CONT only works after STOP, not after Break interruption."

While the comment describes the behavior, it doesn't explain the rationale. Is this truly MBASIC 5.21 behavior, or is it an implementation choice? The comment claims compatibility but doesn't cite specific MBASIC behavior.

---

#### documentation_inconsistency

**Description:** Multiple comments reference 'MBASIC 5.21 compatibility' but no central documentation defines what this means

**Affected files:**
- `src/interpreter.py`

**Details:**
Throughout the file, comments reference 'MBASIC 5.21 compatibility' or 'MBASIC 5.21 behavior' in:
- execute_lset()
- execute_rset()
- execute_midassignment()
- execute_cont()
- evaluate_binaryop()

However, there's no central documentation defining what MBASIC 5.21 is, which behaviors are being emulated, or where to find the specification. This makes it impossible to verify if the implementation actually matches MBASIC 5.21.

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

The stub has no tkinter imports or dependencies.

---

#### Code vs Documentation inconsistency

**Description:** Console input_char() fallback behavior severely compromises functionality but is only mentioned in comments

**Affected files:**
- `src/iohandler/console.py`

**Details:**
console.py input_char() has a Windows fallback that completely breaks single-character input:

"# Fallback for Windows without msvcrt: use input() with severe limitations
# WARNING: This fallback calls input() which:
# - Waits for Enter key (defeats the purpose of single-char input)
# - Returns the entire line, not just one character
# This is a known limitation when msvcrt is unavailable.
# For proper single-character input on Windows, msvcrt is required.
line = input()
return line[:1] if line else ''"

This is a critical limitation that should be documented in the base.py interface documentation or the module docstring, not just buried in implementation comments. Users on Windows without msvcrt will get completely broken behavior for INKEY$ and INPUT$ functions.

---

#### code_vs_comment_conflict

**Description:** Comment claims lexer uses SimpleKeywordCase for 'force-based policies' only, but the code actually accepts any policy string from settings without validation

**Affected files:**
- `src/lexer.py`

**Details:**
Comment in create_keyword_case_manager() states:
"The lexer uses SimpleKeywordCase which supports force-based case policies:
- force_lower: Convert all keywords to lowercase
- force_upper: Convert all keywords to UPPERCASE
- force_capitalize: Convert all keywords to Capitalized form"

However, the code does:
policy = get("keywords.case_style", "force_lower")
return SimpleKeywordCase(policy=policy)

There is no validation that the policy is one of the three force-based policies mentioned. The code will pass any string from settings to SimpleKeywordCase constructor.

---

#### code_vs_comment_conflict

**Description:** Repeated claims that KeywordCaseManager is separate and used by parser/position_serializer, but no evidence of this separation or usage pattern in the provided code

**Affected files:**
- `src/lexer.py`

**Details:**
Multiple comments claim:
"Note: A separate KeywordCaseManager class exists (src/keyword_case_manager.py) that provides additional advanced policies (first_wins, preserve, error) using CaseKeeperTable for tracking case conflicts across the codebase. That class is used by the parser and position_serializer where conflict detection is needed."

However:
1. The file src/keyword_case_manager.py is not provided in the source code files
2. No evidence of how parser/position_serializer use this separate class
3. No evidence of CaseKeeperTable implementation
4. The distinction between 'simple force-based' and 'advanced policies' is not validated in code

---

#### code_vs_comment_conflict

**Description:** Comment claims 'properly-formed MBASIC 5.21 requires spaces between keywords' but code has special handling for PRINT# without spaces

**Affected files:**
- `src/lexer.py`

**Details:**
Comment in read_identifier():
"This lexer parses properly-formed MBASIC 5.21 which requires spaces between keywords and identifiers. Old BASIC with NEXTI instead of NEXT I should be preprocessed before parsing."

And later:
"NOTE: We do NOT handle old BASIC where keywords run together (NEXTI, FORI). This is properly-formed MBASIC 5.21 which requires spaces."

But the code explicitly handles PRINT#1 without spaces:
"MBASIC allows 'PRINT#1' with no space, which should tokenize as: PRINT (keyword) + # (operator) + 1 (number)"

This is contradictory - either MBASIC 5.21 requires spaces or it doesn't. The file I/O syntax appears to be an exception that should be documented.

---

#### code_vs_comment

**Description:** Comment claims RND and INKEY$ can be called without parentheses as 'standard BASIC', but this is actually MBASIC-specific behavior, not universal BASIC standard

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line 11-12 states:
"- Exception: RND and INKEY$ can be called without parentheses (standard BASIC)"

However, this is MBASIC 5.21 specific behavior. Many BASIC dialects (like QuickBASIC, BBC BASIC) require parentheses for all functions. The comment should clarify this is MBASIC behavior, not a universal BASIC standard.

---

#### code_vs_comment

**Description:** Comment in parse_print() claims comma after file number is 'technically optional', but code behavior and MBASIC 5.21 syntax may not match this claim

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~730-735:
"# Optionally consume comma after file number
# Note: MBASIC 5.21 typically uses comma (PRINT #1, "text"), but comma is
# technically optional. Our parser accepts comma or no separator.
# If semicolon appears instead, it will be treated as an item separator
# in the expression list below (not as a file number separator)."

This suggests the parser is more lenient than MBASIC 5.21 specification. The comment should clarify whether this is intentional compatibility extension or if MBASIC 5.21 actually requires the comma. The phrase 'technically optional' needs verification against actual MBASIC 5.21 behavior.

---

#### code_vs_comment

**Description:** Comment about MID$ statement detection describes complex lookahead logic that may not handle all edge cases correctly

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines ~490-495:
"# Detect MID$ used as statement: MID$(var, start, len) = value
# Look ahead to distinguish MID$ statement from MID$ function
# MID$ statement has pattern: MID$ ( ... ) =
# MID$ is tokenized as single MID token ($ is part of the keyword)
# Complex lookahead: scan past parentheses (tracking depth) to find = sign"

The implementation uses try/except to restore position on failure, but the comment doesn't mention this error handling approach. Additionally, the comment claims 'MID$ is tokenized as single MID token' but then the code checks for LPAREN separately, suggesting the tokenization detail may not be accurately described.

---

#### code_vs_comment

**Description:** Comment describes 'pattern' field but code uses 'pattern' parameter name inconsistently with docstring

**Affected files:**
- `src/parser.py`

**Details:**
In parse_showsettings() method:
- Docstring says: "Args:\n    pattern: Optional string expression to filter which settings to display"
- Comment in return statement says: "Field name: 'pattern' (optional filter string)"
- But the actual parameter in ShowSettingsStatementNode is named 'pattern'
This is actually consistent, but the inline comment is redundant and could cause confusion if the field name ever changes.

---

#### code_vs_comment

**Description:** Comment describes INPUT statement behavior with semicolon but implementation may not fully match MBASIC 5.21 semantics

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() method comment:
"Note: In MBASIC 5.21, the separator after the prompt string affects '?' display:\n- INPUT \"Name\"; X  displays \"Name? \" (semicolon shows '?')\n- INPUT \"Name\", X  displays \"Name \" (comma suppresses '?')"

However, the code only tracks suppress_question flag for INPUT; syntax (semicolon immediately after INPUT keyword), not for the separator after the prompt string. The separator after prompt is consumed but not used to modify suppress_question behavior. This suggests incomplete implementation of MBASIC 5.21 semantics.

---

#### code_vs_comment

**Description:** Comment in parse_for describes handling malformed FOR loops but warns about semantic changes without documenting impact

**Affected files:**
- `src/parser.py`

**Details:**
In parse_for() docstring:
"Note: Some files may have malformed FOR loops like \"FOR 1 TO 100\" (missing variable).\nWe handle this by creating a dummy variable 'I' to allow parsing to continue,\nthough this changes the semantics and may cause issues if variable I is referenced elsewhere."

This is a significant semantic change that could cause silent bugs. The comment acknowledges the problem but the code proceeds anyway. This should either:
1. Raise a parse error instead of silently changing semantics
2. Use a guaranteed-unique dummy variable name
3. Be documented as a known limitation in user-facing documentation

---

#### code_vs_comment

**Description:** Comment in parse_deftype describes batch vs interactive mode behavior but implementation always updates def_type_map

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deftype() docstring:
"Note: This method always updates def_type_map during parsing.\nIn batch mode (two-pass), first pass collects types, second pass uses them.\nIn interactive mode (single-pass), this immediately updates the type map."

The code unconditionally updates self.def_type_map regardless of mode. The comment suggests there should be different behavior for batch vs interactive mode, but the implementation doesn't distinguish between them. This could be:
1. Comment describing intended future behavior
2. Outdated comment from refactoring
3. Missing mode detection logic

---

#### code_vs_comment

**Description:** Comment in parse_deffn describes function name normalization but implementation details are unclear

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deffn() method:
Comment says: "# Use lowercase 'fn' to match function calls"

But earlier comment says: "# \"DEF FNR\" without space - identifier is \"fnr\" (lexer already normalized to lowercase)"

This suggests:
1. Lexer normalizes identifiers to lowercase
2. Parser explicitly uses lowercase 'fn' prefix

But it's unclear if this is redundant (lexer already did it) or necessary (lexer doesn't normalize keywords). The comment should clarify whether this normalization is defensive or required.

---

#### code_vs_comment

**Description:** CALL statement docstring claims both MBASIC 5.21 syntax and extended syntax are 'fully supported', but the comment contradicts this by saying extended syntax is for 'compatibility with other BASIC dialects'

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"MBASIC 5.21 syntax:
    CALL address           - Call machine code at numeric address

Extended syntax (also supported for compatibility with other BASIC dialects):
    CALL ROUTINE(X,Y)      - Call with arguments

Both forms are fully supported by this parser."

This is internally inconsistent - if CALL ROUTINE(X,Y) is 'extended syntax' for 'compatibility with other BASIC dialects', it implies it's NOT part of MBASIC 5.21 standard syntax, yet the docstring claims both are 'fully supported' as if they're equivalent.

---

#### documentation_inconsistency

**Description:** COMMON statement docstring says 'no subscripts are specified or stored' but the code does parse and consume parentheses for array indicators

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"The empty parentheses () indicate an array variable (all elements shared).
This is just a marker - no subscripts are specified or stored."

Code implementation:
"# Check for array indicator ()
# We consume the parentheses but don't need to store array dimension info
# (COMMON shares the entire array, not specific subscripts)"

While technically accurate that subscript VALUES aren't stored, the docstring could be clearer that the parentheses syntax IS parsed and consumed, just not stored in the AST. The phrase 'no subscripts are specified' is misleading since the () syntax must be specified in the source code.

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

**Description:** emit_keyword() docstring says keyword parameter should be 'normalized lowercase' but callers pass various cases

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword() docstring:
'Args:
    keyword: The keyword to emit (normalized lowercase)'

But in serialize_rem_statement():
'result = self.emit_keyword(stmt.comment_type.lower(), stmt.column, "RemKeyword")'

The caller explicitly calls .lower() on the keyword before passing it, suggesting the parameter is NOT already normalized. The docstring should say 'keyword to emit (will be looked up in case table)' rather than claiming it's already normalized.

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

#### Documentation inconsistency

**Description:** Global settings path documentation inconsistency between docstring and code

**Affected files:**
- `src/settings.py`

**Details:**
Module docstring says:
'- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)'

But _get_global_settings_path() implementation shows:
if os.name == 'nt':  # Windows
    appdata = os.getenv('APPDATA', os.path.expanduser('~'))
    base_dir = Path(appdata) / 'mbasic'
else:  # Linux/Mac
    base_dir = Path.home() / '.mbasic'

On Windows, if APPDATA is not set, it falls back to user home directory, creating ~/mbasic/settings.json (without the dot), not %APPDATA%/mbasic/settings.json as documented. The fallback behavior is not documented.

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

**Description:** Comment in _format_line says line numbers are variable width and not padded, but _parse_line_numbers uses fixed 5-character padding

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_format_line docstring (line 656) states:
"Returns:
    Formatted string or urwid markup: \"S<num> CODE\" where S is status (1 char),
    <num> is the line number (variable width, not padded)"

_format_line implementation (line 680) confirms:
"# Line number column (variable width)
line_num_str = f\"{line_num}\""

But _parse_line_numbers (lines 991, 1024) contradicts this:
"line_num_formatted = f\"{num_str:>5}\"
new_line = f\" {line_num_formatted} {rest}\""

---

#### code_vs_comment

**Description:** keypress method comment references column 7 as code area start, but with variable-width line numbers this position varies

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
keypress method comment (line 283) states:
"Format: \"S<linenum> CODE\" (where <linenum> is variable width)
- Column 0: Status (●, ?, space) - read-only
- Columns 1+: Line number (variable width) - editable
- After line number: Space
- After space: Code - editable"

But _sort_and_position_line (line 1088) uses fixed column 7:
"def _sort_and_position_line(self, lines, current_line_index, target_column=7):
    \"\"\"Sort lines by line number and position cursor at the moved line.

    Args:
        lines: List of text lines
        current_line_index: Index of line that triggered the sort
        target_column: Column to position cursor at (default: 7). This value is an
                      approximation for typical line numbers."

This contradicts the variable-width design since column 7 would only be correct for 5-digit line numbers.

---

#### code_vs_comment

**Description:** Comment at line 976 acknowledges the inconsistency but doesn't explain why different formatting is used

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment states:
"Note: When reformatting pasted content, line numbers are right-justified to 5 characters
for consistent alignment. This differs from the variable-width formatting used in
_format_line() for display. The fixed 5-char width (lines 991, 1024) helps maintain
alignment when pasting multiple lines with different line number lengths."

This comment acknowledges two different formatting approaches exist but doesn't explain:
1. Why consistency is needed for pasted content but not display
2. Why the class docstring claims variable width everywhere
3. Whether this is intentional design or a bug

---

#### code_vs_comment

**Description:** Comment states toolbar method is 'no longer used' but doesn't clarify if it should be removed

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _create_toolbar() method:
Comment says: "Note: This method is no longer used (toolbar removed from UI in favor of Ctrl+U menu for better keyboard navigation). The method is retained for reference and potential future re-enablement, but can be safely removed if the toolbar is not planned to return."

This creates ambiguity about whether the method should be kept or removed. The comment suggests it 'can be safely removed' but also says it's 'retained for reference'.

---

#### code_vs_comment

**Description:** IO Handler lifecycle comment describes two handlers but implementation details are unclear

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in __init__() says:
"# IO Handler Lifecycle:
# 1. self.io_handler (CapturingIOHandler) - Used for RUN program execution
#    Captures output to display in output window, defined inline above
# 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands
#    Created here and recreated in start() with fresh instance
#    OutputCapturingIOHandler is imported from immediate_executor module"

However, the code shows CapturingIOHandler is defined inline in __init__, while OutputCapturingIOHandler is imported but not shown in this file. The comment doesn't explain why two different handler types are needed or what the differences are between them.

---

#### code_vs_comment

**Description:** Comment about main widget storage is inconsistent across methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_help():
"# Main widget retrieval: Use self.main_widget for consistency with
# _show_keymap and _show_settings (not self.loop.widget which might be
# a menu or other overlay at this moment)"
But the code doesn't actually use self.main_widget - it just creates overlay without storing main widget.

In _show_keymap():
"Main widget storage: Uses self.main_widget (stored in __init__) rather than
self.loop.widget (which might be a menu or other overlay)."
Code: main_widget = self.main_widget

In _activate_menu():
"Main widget storage: Extracts base_widget from self.loop.widget to handle
cases where current widget might already be an overlay. This is different from
_show_keymap/_show_settings which use self.main_widget directly."
Code: main_widget = self.loop.widget.base_widget if hasattr(self.loop.widget, 'base_widget') else self.loop.widget

These three methods have different approaches to getting the main widget, and the comments acknowledge this but don't explain why the inconsistency exists or which approach is correct.

---

#### code_vs_comment

**Description:** Comment claims breakpoints are stored in editor (self.editor.breakpoints), but code accesses them differently

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program() method around line 1050:

Comment says: "Note: reset_for_run() clears variables and resets PC. Breakpoints are stored in the editor (self.editor.breakpoints), NOT in runtime, so they persist across runs and are re-applied below via interpreter.set_breakpoint() calls."

But the code that follows uses:
        # Re-apply breakpoints from editor
        # Breakpoints are stored in editor UI state and must be re-applied to interpreter
        # after reset_for_run (which clears them)
        for line_num in self.editor.breakpoints:
            self.interpreter.set_breakpoint(line_num)

This accesses self.editor.breakpoints directly, which matches the comment. However, the comment's claim that breakpoints are "NOT in runtime" conflicts with the fact that they need to be re-applied to the interpreter after reset_for_run clears them, suggesting they ARE stored in runtime/interpreter during execution.

---

#### code_vs_comment

**Description:** Comment about statement-level precision for GOSUB conflicts with default value handling

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_stack_window() method:

Comment says: "# Show statement-level precision for GOSUB return address
# Note: default of 0 if return_stmt is missing means first statement on line"

But the code uses:
                return_stmt = entry.get('return_stmt', 0)
                line = f"{indent}GOSUB from line {entry['from_line']}.{return_stmt}"

The comment claims default of 0 means "first statement on line", but this is misleading because statement numbering typically starts at 0, so 0 would indeed be the first statement. However, the comment's phrasing suggests this is a fallback behavior rather than the normal case, which may be incorrect.

---

#### code_vs_comment

**Description:** Comment about preserving PC conflicts with halted PC assignment

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sync_program_to_runtime() method:

Comment says: "# Restore PC only if execution is running AND not paused at breakpoint
# (paused programs need PC reset to current breakpoint location)
# Otherwise ensure halted (don't accidentally start execution)"

But the code shows:
        if self.running and not self.paused_at_breakpoint:
            # Execution is running - preserve execution state
            self.runtime.pc = old_pc
            self.runtime.halted = old_halted
        else:
            # No execution in progress - ensure halted
            self.runtime.pc = PC.halted_pc()
            self.runtime.halted = True

The comment claims paused programs need PC reset, but the code actually preserves old_pc when running and not paused. When paused at breakpoint, it sets PC to halted_pc(), which may not be the "current breakpoint location" as the comment suggests.

---

#### code_vs_comment

**Description:** Comment claims DELETE doesn't sync to runtime immediately, but code shows sync happens in _execute_immediate which is called for every immediate command

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_delete method:
Comment says: "Note: Doesn't sync to runtime immediately - sync happens when next immediate command is executed via _execute_immediate."

But in _execute_immediate method (line ~1050):
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

The sync happens immediately when DELETE is executed as an immediate command, not "when next immediate command is executed".

---

#### code_vs_comment

**Description:** Comment claims RENUM doesn't sync to runtime immediately, but same issue as DELETE - sync happens in _execute_immediate

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_renum method:
Comment says: "Note: Doesn't sync to runtime immediately - sync happens when next immediate command is executed via _execute_immediate."

But _execute_immediate calls _sync_program_to_runtime() for every immediate command execution, so RENUM syncs immediately when executed.

---

#### code_vs_comment

**Description:** Comment claims not to call interpreter.start() to preserve PC, but then creates InterpreterState conditionally which may have side effects

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method (line ~1145):
# NOTE: Don't call interpreter.start() because it resets PC!
# If the immediate command was 'RUN 120', the immediate executor has already
# set PC to line 120 via interpreter.start(start_line=120), so we need to
# preserve that PC value and not reset it.
# We only create InterpreterState if it doesn't exist (first run of session),
# which initializes tracking state but doesn't modify PC/runtime state.
from src.interpreter import InterpreterState
if not hasattr(self.interpreter, 'state') or self.interpreter.state is None:
    self.interpreter.state = InterpreterState(_interpreter=self.interpreter)

The comment claims InterpreterState initialization 'doesn't modify PC/runtime state' but this needs verification - creating state objects can have initialization side effects.

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

**Description:** HelpMacros docstring says {{kbd:help}} searches all sections for 'help' action, but help_widget.py hardcodes help navigation keys instead of using kbd macro

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/help_widget.py`

**Details:**
help_macros.py docstring:
"Example:
  {{kbd:help}} → looks up 'help' action in keybindings (searches all sections)
                  and returns the primary keybinding for that action"

But help_widget.py doesn't use {{kbd}} macros in its footer - it hardcodes the keys:
self.footer = urwid.Text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search U=Back ESC/Q=Exit ")

The help system should use {{kbd}} macros to display correct keybindings from JSON config.

---

#### code_vs_comment

**Description:** Comment says HelpWidget is curses-specific and hardcodes 'curses' UI name, but the class could be made UI-agnostic by accepting ui_name parameter

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~60:
"# HelpWidget is curses-specific (uses urwid), so hardcode 'curses' UI name
self.macros = HelpMacros('curses', help_root)"

While the comment explains the hardcoding, it's inconsistent with the design of HelpMacros which accepts ui_name as a parameter, suggesting it was designed to be UI-agnostic. HelpWidget could accept ui_name in __init__ instead of hardcoding.

---

#### code_vs_documentation

**Description:** HelpMacros._expand_kbd() docstring says it searches all sections for action name, but the implementation doesn't document what happens with duplicate action names across sections

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Docstring:
"Expand keyboard shortcut macro by searching for action name across all sections.

Args:
    key_name: Name of key action (e.g., 'help', 'save', 'run').
             This is searched across all keybinding sections (editor, help_browser, etc.)"

The code iterates through sections:
for section_name, section in self.keybindings.items():
    if key_name in section:
        return section[key_name]['primary']

If the same action name exists in multiple sections, it returns the first match. This behavior is not documented and could lead to unexpected results.

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

**Description:** Comment about Ctrl+I binding location conflicts with actual implementation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _create_menu() at line ~640:
"# Note: Ctrl+I is bound directly to editor text widget in start() (not root window)
# to prevent tab key interference - see editor_text.text.bind('<Control-i>', ...)"

But in start() method at line ~330, the binding is:
"# Bind Ctrl+I for smart insert line (must be on text widget to prevent tab)
self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)"

The comment in _create_menu() correctly describes the implementation, but the redundant comment in start() suggests this was a point of confusion during development.

---

#### code_inconsistency

**Description:** Inconsistent handling of region types in _on_variable_double_click

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_variable_double_click() at line ~1090:
"# Check if we clicked on a row (accept both 'tree' and 'cell' regions)
# 'tree' = first column area, 'cell' = other column areas
region = self.variables_tree.identify_region(event.x, event.y)
if region not in ('cell', 'tree'):
    return"

But in _on_variable_heading_click() at line ~1075:
"region = self.variables_tree.identify_region(event.x, event.y)
if region != 'heading':
    return  # Not a heading click, let normal handling continue"

The comment in double_click explains what 'tree' and 'cell' mean, but there's no explanation of what other region types exist or why 'heading' is the only valid one for heading clicks.

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

MBASIC 5.21 only allows OPTION BASE 0 or 1. The 'else' branch for invalid values suggests runtime allows other values, which would be non-standard behavior.

---

#### code_vs_comment

**Description:** Comment claims _remove_blank_lines is 'Currently called only from _on_enter_key' but doesn't document why it's not called after paste operations

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines ~1699-1704:
Currently called only from _on_enter_key (after each keypress), not
after pasting or other modifications. This provides continuous cleanup
as the user types.

This is inconsistent behavior - blank lines are removed during typing but not after paste. The comment acknowledges this but doesn't explain the design decision. Users might paste code with blank lines and expect them to be removed based on the typing behavior.

---

#### code_vs_comment

**Description:** Comment says 'clears red ? when line is fixed' but there's no evidence of red ? markers in the code

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1686:
# Also validate syntax after clicking (clears red ? when line is fixed)

The error marking system uses set_error() method but there's no code showing a red '?' character being displayed. The comment suggests a specific visual indicator that may not exist or may be implemented elsewhere.

---

#### internal_inconsistency

**Description:** Inconsistent handling of statement highlighting - cleared on mouse click but not on cursor movement

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_mouse_click (line ~1683):
# Clear yellow statement highlight when clicking (allows text selection to be visible)
if self.paused_at_breakpoint:
    self._clear_statement_highlight()

But in _on_cursor_move (line ~1677), there's no similar clearing of statement highlight. This creates inconsistent UX where clicking clears the highlight but arrow keys don't.

---

#### code_vs_comment

**Description:** Docstring for _validate_editor_syntax says 'Validates each line independently' but doesn't mention the 100ms delay mechanism

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring at lines ~1632-1634:
Validate syntax of all lines in editor and update error markers.

Validates each line independently as entered - immediate feedback.

But the method is called with 100ms delay (lines 1679, 1686), so feedback is not truly 'immediate'. The docstring should mention the debouncing behavior.

---

#### code_vs_comment

**Description:** Comment claims CONT is simplified and mentions optional runtime.stop_line/stop_stmt_index attributes, but the code actually uses these attributes without checking if they exist first

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment says: "NOTE: This is a simplified implementation. The runtime.stop_line and runtime.stop_stmt_index attributes are optional extensions for better state restoration. If not present, execution continues from the current PC position maintained by the interpreter."

But code does:
if hasattr(self.runtime, 'stop_line') and hasattr(self.runtime, 'stop_stmt_index'):
    self.runtime.current_line = self.runtime.stop_line
    self.runtime.current_stmt_index = self.runtime.stop_stmt_index

The code correctly checks for attribute existence with hasattr(), contradicting the comment's claim that it's a "simplified implementation" that doesn't handle the optional case properly.

---

#### code_vs_comment

**Description:** Comment in _check_line_change explains when NOT to trigger sort, but the logic description is incomplete regarding the actual conditions

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment says: "Don't trigger sort when:
- old_line_num is None: First time tracking this line (cursor just moved here, no editing yet)
- This prevents unnecessary re-sorting when user clicks around without making changes"

But the actual condition is more complex:
should_sort = False
if old_line_num != new_line_num:
    if old_line_num is not None and new_line_num is not None:
        should_sort = True
    elif old_line_num is not None and new_line_num is None and current_text.strip():
        should_sort = True

The comment only explains one case (old_line_num is None) but doesn't explain that we also DON'T sort when new_line_num is None and the line is empty (no content). This is an important case that's missing from the explanation.

---

#### code_vs_comment

**Description:** Comment in _execute_tick says 'brief flash effect' for highlighting during running, but there's no code that clears the highlight to create a flash

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment says: "# Running - highlight current statement (brief flash effect)"

But the code only sets the highlight:
if state.current_statement_char_start > 0 or state.current_statement_char_end > 0:
    self._highlight_current_statement(state.current_line, state.current_statement_char_start, state.current_statement_char_end)

There's no code that clears this highlight after a brief delay to create a 'flash effect'. The highlight persists until the next statement is highlighted or execution stops. The comment is misleading about the visual behavior.

---

#### code_vs_comment

**Description:** Comment claims immediate_history is always None (line ~291), but _setup_immediate_context_menu() and related methods (_copy_immediate_selection, _select_all_immediate) reference it as if it's a valid widget

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _add_immediate_output() states:
"Note: self.immediate_history exists but is always None (see line ~291) - it's a dummy attribute for compatibility with code that references it."

However, _setup_immediate_context_menu() docstring says:
"NOTE: This method is currently unused - immediate_history is always None in the Tk UI (see line ~291). This is dead code retained for potential future use if immediate mode gets its own output widget."

But the methods _copy_immediate_selection() and _select_all_immediate() call:
- self.immediate_history.get(tk.SEL_FIRST, tk.SEL_LAST)
- self.immediate_history.tag_add(tk.SEL, "1.0", tk.END)

These would fail with AttributeError if immediate_history is None.

---

#### code_vs_comment

**Description:** Comment about 'has_work()' usage doesn't match actual implementation pattern

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _execute_immediate() states:
"Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command).
This complements runtime flag checks (self.running, runtime.halted) used elsewhere."

However, the code immediately after checking has_work() also checks 'if not self.running' before starting execution. This suggests has_work() alone is NOT sufficient to determine if execution should start - it must be combined with the self.running flag check. The comment implies has_work() complements other checks, but doesn't clarify that both checks are required together.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about CLS command behavior

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler.clear_screen() docstring states:
"Clear screen - no-op for Tk UI.

Design decision: GUI output is persistent for review. Users can manually
clear output via Run > Clear Output menu if desired. CLS command is ignored
to preserve output history during program execution."

This documents that CLS is ignored, but doesn't clarify:
1. Whether this is documented in user-facing documentation
2. Whether programs expecting CLS to work will behave correctly
3. Whether there's a warning when CLS is used

This could lead to user confusion when CLS commands in their BASIC programs don't work as expected.

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
Comment says: "WARNING: This could create invalid BASIC code during RENUM if new statement types are added but not handled here. Ensure all statement types are supported."
Code does: return f"REM {stmt_type}"
The warning indicates this is a known bug/limitation, but the code doesn't raise an error or log a warning when this fallback is used. Silent data corruption during RENUM is a serious issue.

---

#### code_vs_documentation

**Description:** renum_program() docstring says callback is 'responsible for identifying and updating statements with line number references' but doesn't specify which statement types need updating

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says: "Called for ALL statements; callback is responsible for identifying and updating statements with line number references (GOTO, GOSUB, ON GOTO, ON GOSUB, IF THEN/ELSE line numbers)"
This lists some statement types but doesn't clarify if this is exhaustive. The function doesn't validate that the callback handles all necessary types, so incorrect callbacks could silently fail to update some references.

---

#### code_vs_documentation

**Description:** Docstring claims Runtime accesses program.line_asts directly, but code shows Runtime is initialized with program.line_asts and program.lines as separate parameters

**Affected files:**
- `src/ui/visual.py`

**Details:**
Comment in cmd_run() says:
"# (Runtime accesses program.line_asts directly, no need for program_ast variable)"

But the actual code shows:
"self.runtime = Runtime(self.program.line_asts, self.program.lines)"

This suggests Runtime receives these as constructor parameters rather than accessing them directly from a program object.

---

#### code_internal

**Description:** Sort state initialization comment claims to match Tk UI defaults but references non-existent line numbers

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~119-120 comment in VariablesDialog.__init__:
"# Sort state (matches Tk UI defaults: see src/ui/tk_ui.py lines 91-92)
self.sort_mode = 'accessed'  # Current sort mode
self.sort_reverse = True  # Sort direction"

The comment references src/ui/tk_ui.py lines 91-92 for verification, but this file is not provided in the source code files. Cannot verify if the defaults actually match.

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

**Description:** Inconsistent handling of empty programs between RUN and step commands

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
_menu_run (line ~1799):
  # If empty program, just show Ready (variables cleared, nothing to execute)
  if not self.program.lines:
      self._set_status('Ready')
      self.running = False
      return

_menu_step_line (line ~2050) and _menu_step_stmt (line ~2100):
  # If empty program, just show Ready (matches RUN behavior - silent success)
  if not self.program.lines:
      self._set_status('Ready')
      self.running = False
      return

Both handle empty programs the same way, but RUN comment says 'variables cleared' while step comments say 'matches RUN behavior'. However, step methods don't actually clear variables before this check - they only clear if program is non-empty.

---

#### code_vs_comment

**Description:** Comment about breakpoint types doesn't match actual implementation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1560 in _update_breakpoint_display:
  # Note: self.runtime.breakpoints is a set that can contain:
  #   - PC objects (statement-level breakpoints, created by _toggle_breakpoint)
  #   - Plain integers (line-level breakpoints, legacy/compatibility)
  # This implementation uses PC objects exclusively, but handles both for robustness.

But _toggle_breakpoint (line ~1450) and _do_toggle_breakpoint (line ~1620) ONLY create PC objects, never plain integers. The 'legacy/compatibility' claim is not supported by any code that creates integer breakpoints.

---

#### code_internal_inconsistency

**Description:** Inconsistent runtime initialization between RUN and step commands

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
_menu_run (line ~1820):
  # Reset runtime with current program - RUN = CLEAR + GOTO first line
  # This preserves breakpoints but clears variables
  self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

_menu_step_line (line ~2060):
  if self.runtime is None:
      self.runtime = Runtime(self.program.line_asts, self.program.lines)
      self.runtime.setup()
  else:
      # Reset runtime for fresh execution (clears variables but preserves breakpoints)
      self.runtime.reset_for_run(self.program.line_asts, self.program.lines)

RUN assumes runtime exists and calls reset_for_run directly. Step checks if runtime is None and creates it. This could cause AttributeError if RUN is called before runtime is created.

---

#### code_vs_comment

**Description:** Inconsistent state management comments - 'running' flag purpose unclear

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Multiple comments describe self.running differently:

Line ~1800: "self.running = False  # Mark as not running (updates UI spinner/status)"
Line ~1850: "# Mark as running (for display and state tracking - spinner, status, continue/step logic)"
Line ~1870: "# Note: self.running is also set/cleared elsewhere but may not persist reliably in async callbacks"

The last comment suggests self.running is unreliable, but the code depends on it for Continue logic. This is confusing.

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

**Description:** Comment in _save_editor_to_program mentions CP/M EOF marker but this seems irrelevant for web editor

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# Normalize line endings and remove CP/M EOF markers\n# \r\n -> \n (Windows line endings, may appear if user pastes text)\n# \r -> \n (old Mac line endings, may appear if user pastes text)\n# \x1a (Ctrl+Z, CP/M EOF marker - included for consistency with file loading)'

The CP/M EOF marker (\x1a) is unlikely to appear in a web editor context. This comment suggests code was copied from file loading logic without adaptation, or the comment is outdated.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcuts for toggling breakpoints between documentation files

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md states:
- Curses UI: 'b' key
- Tk UI: 'Ctrl+B'

But editor-commands.md states:
'b | Ctrl+B | Toggle breakpoint (Curses: b, Tk: Ctrl+B)'

The table format in editor-commands.md suggests 'b' works in both UIs as an alternative, which contradicts the UI-specific assignments in debugging.md.

---

#### code_vs_documentation

**Description:** Help launcher references MkDocs but compiler documentation uses MkDocs-specific frontmatter

**Affected files:**
- `src/ui/web_help_launcher.py`
- `docs/help/common/compiler/index.md`

**Details:**
web_help_launcher.py has deprecated class WebHelpLauncher_DEPRECATED that references MkDocs:
'Check if mkdocs is available'
'subprocess.run(["mkdocs", "build"])'

The compiler documentation files (optimizations.md, index.md) use MkDocs frontmatter:
'---\ndescription: ...\nkeywords: ...\ntitle: ...\ntype: reference\n---'

But the main open_help_in_browser() function just points to a static URL 'http://localhost/mbasic_docs' with no mention of whether MkDocs is required or if it's pre-built. The comment says 'Local web server serving the built MkDocs site' but doesn't explain the build process.

---

#### documentation_inconsistency

**Description:** Conflicting information about Load program shortcut

**Affected files:**
- `docs/help/common/editor-commands.md`
- `docs/help/common/debugging.md`

**Details:**
editor-commands.md 'Program Commands' table:
'b | Ctrl+O | Load program'

This conflicts with the breakpoint toggle command also using 'b'. The same key 'b' is listed for two different functions:
1. Toggle breakpoint (in Debugging Commands)
2. Load program (in Program Commands)

debugging.md doesn't mention 'b' for loading programs, only for breakpoints in Curses UI.

---

#### code_vs_documentation

**Description:** Version information in code not reflected in documentation

**Affected files:**
- `src/version.py`
- `docs/help/common/getting-started.md`

**Details:**
version.py defines:
VERSION = '1.0.657'
PROJECT_NAME = 'MBASIC-2025'
MBASIC_VERSION = '5.21'
COMPATIBILITY = '100% MBASIC 5.21 compatible with optional extensions'

But getting-started.md only mentions:
'MBASIC 5.21 is compatible with MBASIC from the 1980s'

No mention of MBASIC-2025 project name, version 1.0.657, or the 'optional extensions' part of compatibility. Users might not know they're using a modern reimplementation.

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

**Description:** CLEAR documentation has confusing historical note about parameter meanings that changed between BASIC-80 versions

**Affected files:**
- `docs/help/common/language/statements/clear.md`

**Details:**
The CLEAR documentation states: 'In MBASIC 5.21 (BASIC-80 release 5.0 and later): expression1: If specified, sets the highest memory location available for BASIC to use' but then says 'Historical note: In earlier versions of BASIC-80 (before release 5.0), the parameters had different meanings: expression1 set the amount of string space'. This is confusing because the doc is for MBASIC 5.21 but spends significant space on obsolete behavior. The string space note contradicts the current behavior description.

---

#### documentation_inconsistency

**Description:** CLOAD and CSAVE have identical 'See Also' sections with unrelated functions

**Affected files:**
- `docs/help/common/language/statements/cload.md`
- `docs/help/common/language/statements/csave.md`

**Details:**
Both CLOAD and CSAVE list the same 8 'See Also' items: CVI/CVS/CVD, DEFINT/SNG/DBL/STR, ERR AND ERL VARIABLES, INPUT#, LINE INPUT, LPRINT, MKI$/MKS$/MKD$, SPACE$, TAB. These are mostly unrelated to cassette operations. They should reference each other and possibly LOAD/SAVE for disk operations instead.

---

#### documentation_inconsistency

**Description:** Operators doc says division by zero 'returns machine infinity, execution continues' but TAN doc says 'Overflow error message is displayed'

**Affected files:**
- `docs/help/common/language/operators.md`
- `docs/help/common/language/functions/tan.md`

**Details:**
In operators.md: 'Division by zero: Returns machine infinity, execution continues' with example showing no error. But tan.md states: 'If TAN overflows, the "Overflow" error message is displayed, machine infinity with the appropriate sign is supplied as the result, and execution continues.' This is inconsistent - does an error message display or not?

---

#### documentation_inconsistency

**Description:** DIM documentation states minimum subscript is 0 unless OPTION BASE is used, but doesn't mention that arrays can be redimensioned after ERASE. ERASE doc mentions redimensioning but DIM doesn't cross-reference this capability.

**Affected files:**
- `docs/help/common/language/statements/dim.md`
- `docs/help/common/language/statements/erase.md`

**Details:**
DIM.md: 'If an array variable name is used without a DIM statement, the maximum value of its subscript(s) is assumed to be 10. If a subscript is used that is greater than the maximum specified, a "Subscript out of range" error occurs. The minimum value for a subscript is always 0, unless otherwise specified with the OPTION BASE statement'

ERASE.md: 'Arrays may be redimensioned after they are ERASEd, or the previously allocated array space in memory may be used for other purposes. If an attempt is made to redimension an array without first ERASEing it, a "Redimensioned array" error occurs.'

---

#### documentation_inconsistency

**Description:** ERR/ERL documentation states ERR is reset to 0 when RESUME is executed, but ERROR documentation doesn't mention this reset behavior when discussing how ERROR sets ERR.

**Affected files:**
- `docs/help/common/language/statements/err-erl-variables.md`
- `docs/help/common/language/statements/error.md`

**Details:**
err-erl-variables.md: 'ERR is reset to 0 when:
  - RESUME statement is executed
  - A new RUN command is issued
  - An error handling routine ends normally (without error)'

error.md only states: 'ERR variable will contain the error code' without mentioning the reset conditions.

---

#### documentation_inconsistency

**Description:** INPUT documentation states 'If too many values are entered, the extras are ignored with a ?Redo from start message' but LINE INPUT doesn't mention any error handling for input that's too long (>254 characters).

**Affected files:**
- `docs/help/common/language/statements/input.md`
- `docs/help/common/language/statements/line-input.md`

**Details:**
input.md: 'If too many values are entered, the extras are ignored with a ?Redo from start message'

line-input.md: 'To input an entire line (up to 254 characters) to a string variable, without the use of delimiters.' - no mention of what happens if input exceeds 254 characters.

---

#### documentation_inconsistency

**Description:** Documentation inconsistently mentions CP/M .BAS extension behavior. KILL and LOAD mention it, but FILES doesn't clearly state whether it applies to FILES command.

**Affected files:**
- `docs/help/common/language/statements/kill.md`
- `docs/help/common/language/statements/files.md`
- `docs/help/common/language/statements/load.md`

**Details:**
kill.md: 'Note: CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files.'

load.md: '(With CP/M, the default extension .BAS is supplied.)'

files.md: 'Note: CP/M automatically adds .BAS extension if none is specified for BASIC program files.' - but this is in a general note, not specifically about FILES command behavior.

---

#### documentation_inconsistency

**Description:** Index lists FILES under 'File Management' category but the FILES.md document itself categorizes it as 'file-io'.

**Affected files:**
- `docs/help/common/language/statements/index.md`
- `docs/help/common/language/statements/files.md`

**Details:**
index.md: 'File Management' section includes FILES

files.md frontmatter: 'category: file-io'

---

#### documentation_inconsistency

**Description:** EDIT documentation describes traditional single-character edit mode commands but then states they are not implemented, creating confusion about what EDIT actually does.

**Affected files:**
- `docs/help/common/language/statements/edit.md`

**Details:**
edit.md lists:
'Edit Mode Commands:
In traditional MBASIC, EDIT mode provided special single-character commands:
- I - Insert mode
- D - Delete characters
- C - Change characters
- L - List the line
- Q - Quit edit mode
- Space - Move cursor forward
- Enter - Accept changes'

Then states:
'Implementation Note:
This implementation provides full-screen editing capabilities through the integrated editor (when using the Tk, Curses, or Web UI). The traditional single-character edit mode commands are not implemented.'

---

#### documentation_inconsistency

**Description:** INPUT# and LINE INPUT# have inconsistent file naming - input_hash.md vs inputi.md - and different title formats.

**Affected files:**
- `docs/help/common/language/statements/input_hash.md`
- `docs/help/common/language/statements/inputi.md`

**Details:**
input_hash.md:
- filename: input_hash.md
- title: 'INPUT# (File)'

inputi.md:
- filename: inputi.md  
- title: 'LINE INPUT# (File)'

The filename convention is inconsistent (hash vs i suffix).

---

#### documentation_inconsistency

**Description:** NULL statement documentation has unclear and potentially outdated remarks about hardware timing

**Affected files:**
- `docs/help/common/language/statements/null.md`

**Details:**
The Remarks section states:
'For 10-character-per-second tape punches, <integer expression> should be >=3. When tapes are not being punched, <integer expression> should be 0 or 1 for Teletypes and Teletype-compatible CRTs. <integer expression> should be 2 or 3 for 30 cps hard copy printers. The default value is O.'

This refers to obsolete hardware (tape punches, Teletypes) and the last sentence has a typo: 'O' instead of '0'. This documentation appears to be from the original MBASIC manual without updates for modern context.

---

#### documentation_inconsistency

**Description:** OPTION BASE documentation states 'Only one OPTION BASE statement is allowed per program' but doesn't explain what happens if multiple are used

**Affected files:**
- `docs/help/common/language/statements/option-base.md`

**Details:**
The Remarks section states:
'The OPTION BASE statement must appear before any DIM statements or array references in the program. Only one OPTION BASE statement is allowed per program.'

But it doesn't specify:
- What error occurs if multiple OPTION BASE statements are used?
- What happens if OPTION BASE appears after DIM?
- Is this a compile-time or runtime check?

Other statement docs typically explain error conditions more clearly.

---

#### documentation_inconsistency

**Description:** PRINT# USING documentation references format string syntax but doesn't fully document it

**Affected files:**
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
The documentation states:
'PRINT# USING formats output using a format string, just like PRINT USING:
- # for digit positions
- . for decimal point
- $$ for floating dollar sign
- ** for asterisk fill
- , for thousands separator'

But this is incomplete compared to full PRINT USING syntax. It should either:
1. Reference the full PRINT USING documentation
2. Provide complete format string documentation
3. State explicitly that it's a partial list

The 'See Also' section references 'PRINT USING' but links to print.md which doesn't contain USING documentation.

---

#### documentation_inconsistency

**Description:** RENUM documentation has duplicate line numbers in Example 6

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
Example 6 shows the result after RENUM 1000,100,100:
'1000 PRINT "OPTION 1"
1100 END
1100 PRINT "OPTION 2"
1200 END
1200 PRINT "OPTION 3"
1300 END'

Lines 1100 and 1200 appear twice each. This is clearly an error in the documentation. The correct output should have unique line numbers:
1000, 1100, 1200, 1300, 1400, 1500

---

#### documentation_inconsistency

**Description:** SAVE documentation mentions 'Disk' version but SYSTEM documentation also mentions 'Disk' version, creating ambiguity about version requirements

**Affected files:**
- `docs/help/common/language/statements/save.md`
- `docs/help/common/language/statements/system.md`

**Details:**
save.md states '**Versions:** Disk' while system.md also states '**Versions:** Disk'. The documentation doesn't clarify if these are the same 'Disk' version or different versions.

---

#### documentation_inconsistency

**Description:** SETSETTING syntax differs between statement documentation and settings guide

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/settings.md`

**Details:**
setsetting.md shows 'SETSETTING setting.name value' but settings.md example shows 'SETSETTING editor.auto_number_step 100' - unclear if value needs quotes for strings or how different types are handled.

---

#### documentation_inconsistency

**Description:** File closing behavior inconsistency between STOP and SYSTEM

**Affected files:**
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
stop.md states 'Unlike the END statement, the STOP statement does not close files' but system.md states 'When SYSTEM is executed: All open files are closed'. This creates confusion about which statements close files.

---

#### documentation_inconsistency

**Description:** Variable case sensitivity documentation incomplete regarding settings

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md mentions 'the behavior when using different cases can be configured via the `variables.case_conflict` setting' but doesn't fully explain the interaction. settings.md lists the options but variables.md should reference the specific setting values.

---

#### documentation_inconsistency

**Description:** AUTO command behavior not consistently documented across UIs

**Affected files:**
- `docs/help/common/ui/tk/index.md`
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/ui/cli/index.md`

**Details:**
curses/editing.md and cli/index.md both mention AUTO command with 'Exit AUTO mode with Ctrl+C', but tk/index.md doesn't mention AUTO at all. Unclear if AUTO is available in Tk UI.

---

#### documentation_inconsistency

**Description:** Settings storage location documentation incomplete for project scope

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
settings.md states 'Project scope - Settings for a specific project directory' and shows '.mbasic/settings.json in project directory' but doesn't explain how a 'project directory' is determined or how to initialize project settings.

---

#### documentation_inconsistency

**Description:** WAIT statement marked as not implemented but includes full documentation

**Affected files:**
- `docs/help/common/language/statements/wait.md`

**Details:**
wait.md has Implementation Note stating 'Not Implemented' and 'Statement is parsed but no operation is performed', yet includes complete Syntax, Purpose, Remarks, and Example sections. Should clarify if documentation is for reference only.

---

#### documentation_inconsistency

**Description:** Extension version labeling inconsistent

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/language/statements/showsettings.md`

**Details:**
Both setsetting.md and showsettings.md state '**Versions:** MBASIC Extension' but other docs use 'Disk' or 'EXtended'. Unclear if 'MBASIC Extension' is a formal version designation or just descriptive text.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for project name

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md uses 'MBASIC-2025' and 'This implementation' interchangeably.

extensions.md explicitly states: 'This is MBASIC-2025, a modern implementation of Microsoft BASIC-80 5.21' and lists alternative names under consideration:
- MBASIC-2025 (emphasizes the modern update)
- Visual MBASIC 5.21 (emphasizes the multiple UIs)
- MBASIC++ (emphasizes extensions)
- MBASIC-X (extended MBASIC)

architecture.md doesn't use any specific project name, just refers to 'MBASIC'.

This creates confusion about the official project name.

---

#### documentation_inconsistency

**Description:** Inconsistent information about WIDTH statement support

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/features.md`

**Details:**
compatibility.md states: 'WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.'

features.md does not mention WIDTH statement at all in its comprehensive feature list, neither in the 'Input/Output' section nor in any other section.

This is an inconsistency - if WIDTH is parsed and accepted (even as no-op), it should be documented in the features list.

---

#### documentation_inconsistency

**Description:** Inconsistent description of Web UI file storage mechanism

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md states about Web UI: 'Files stored in Python-side memory (not browser localStorage)' and 'Automatically uppercased by the virtual filesystem (CP/M style)' with note 'The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage'

extensions.md does not provide details about Web UI file storage implementation, only mentioning 'Browser-based IDE' and 'Auto-save - Automatic saving to browser storage'

The phrase 'saving to browser storage' in extensions.md contradicts compatibility.md's statement that files are 'stored in Python-side memory (not browser localStorage)'.

---

#### documentation_inconsistency

**Description:** Missing Web UI from getting-started guide

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/mbasic/extensions.md`

**Details:**
getting-started.md describes three interfaces under 'Choosing a User Interface':
1. Curses UI (Default)
2. CLI Mode
3. Tkinter GUI

extensions.md lists four UIs under 'Multiple User Interfaces':
1. CLI - Classic command line
2. Curses - Full-screen terminal UI
3. Tk - Desktop GUI with menus
4. Web - Browser-based IDE

The getting-started.md guide is missing the Web UI option entirely, which is a significant omission for new users.

---

#### documentation_inconsistency

**Description:** Self-contradictory statement about file handling differences

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
compatibility.md has a section 'File System Differences' that states:

'IMPORTANT: File handling differs between UIs:'

Then describes CLI, Tk, and Curses UIs as having 'Real filesystem access' with examples showing modern paths.

Then describes Web UI as having 'In-memory virtual filesystem'.

However, earlier in the same document under 'Fully Compatible Features' > 'File I/O', it states: 'Sequential files: Fully compatible' and 'Random access files: Fully compatible'.

This creates confusion: if file handling 'differs between UIs' and Web UI uses 'in-memory virtual filesystem', how can file I/O be 'fully compatible' across all UIs?

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
The index.md lists 'String Allocation and Garbage Collection' under Implementation Details, but this is a very detailed technical document about CP/M MBASIC internals. The index doesn't clarify that this is historical/reference material about the original MBASIC, not necessarily the current implementation's behavior.

---

#### documentation_inconsistency

**Description:** Variable inspection capabilities differ between UIs but not clearly documented

**Affected files:**
- `docs/help/ui/cli/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/variables.md states 'The CLI does not have a Variables Window feature' and recommends using PRINT for inspection. feature-reference.md describes 'Variables Window (Ctrl+W)' with filtering and sorting. The fundamental difference in variable inspection between UIs is mentioned but not prominently highlighted in a comparison document.

---

#### documentation_inconsistency

**Description:** Cut/Copy/Paste documentation contradicts standard expectations

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
feature-reference.md states 'Cut/Copy/Paste (Not implemented)' and explains 'Ctrl+X is used for Stop/Interrupt, Ctrl+C exits the program, and Ctrl+V is used for Save'. However, it then says 'Use your terminal's native copy/paste functions instead (typically Shift+Ctrl+C/V or mouse selection)'. This creates confusion about whether clipboard operations work at all.

---

#### documentation_inconsistency

**Description:** Placeholder documentation not completed

**Affected files:**
- `docs/help/ui/common/running.md`

**Details:**
running.md is marked as 'PLACEHOLDER - Documentation in progress' with minimal content. This is referenced from multiple other documents but provides no useful information. Status: incomplete documentation.

---

#### documentation_inconsistency

**Description:** Feature count claim not verifiable

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
feature-reference.md title claims 'all 36 features available in the Curses UI' but the document lists: 8 File Operations + 6 Execution & Control + 6 Debugging + 6 Variable Inspection + 6 Editor Features + 4 Help System = 36 features. However, several are marked 'Not implemented' or 'Not yet implemented', so the count of 'available' features is misleading.

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

**Description:** Inconsistent menu access shortcut

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md states: '**Ctrl+U** | Show menu' under Global Commands

But index.md does not mention Ctrl+U or any menu access shortcut in its navigation table or tips section.

The getting-started.md also doesn't mention how to access the menu system.

---

#### documentation_inconsistency

**Description:** Execution stack window shortcut inconsistency

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md states: '**Menu only** | Toggle execution stack window' under both Global Commands and Debugger sections

But index.md doesn't mention the execution stack window at all in its feature list or navigation guide.

This suggests the feature exists but is incompletely documented.

---

#### documentation_inconsistency

**Description:** Contradictory information about Find/Replace shortcuts

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

But feature-reference.md states:
'### Find/Replace (Ctrl+F / Ctrl+H)'
'- Find: Ctrl+F'
'- Replace: Ctrl+H'

This suggests Ctrl+F and Ctrl+H open separate dialogs, but features.md says Ctrl+H opens a 'combined Find/Replace dialog'. The documentation should clarify if these are separate dialogs or one combined dialog.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation using template syntax

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
features.md uses template syntax like:
'{{kbd:smart_insert}}'
'{{kbd:toggle_breakpoint}}'
'{{kbd:step_statement}}'

But feature-reference.md uses plain text:
'Ctrl+N'
'Ctrl+O'
'Ctrl+S'

The template syntax {{kbd:...}} suggests these are placeholders that should be replaced with actual key combinations, but it's unclear what system is being used. All documentation should use consistent notation.

---

#### documentation_inconsistency

**Description:** Missing documentation for variable window search shortcut

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
quick-reference.md states: '**/** | Search for variable' under Variables Window section

variables.md mentions search but with different details:
'### Search Function
1. In variables window, press `/` to search
2. Type variable name or partial match
3. Press Enter to find
4. Press `n` for next match
5. Press `N` for previous match'

The quick-reference.md should include the full search workflow (n/N for next/previous) for completeness.

---

#### documentation_inconsistency

**Description:** Conflicting information about default UI

**Affected files:**
- `docs/help/ui/index.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
index.md under Curses UI states:
'**Start with:**
```bash
mbasic                # Default UI
mbasic --ui curses
```'

But getting-started.md under tk/getting-started.md states:
'Or to use the default curses UI:
```bash
mbasic [filename.bas]
```'

Both documents claim curses is the default, which is consistent. However, the comparison table in index.md should explicitly state which UI is the default in a prominent location.

---

#### documentation_inconsistency

**Description:** Context Help shortcut inconsistency

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states:
'### Context Help (Shift+F1)
Get help for the BASIC keyword at the cursor:
- Place cursor on keyword
- Press Shift+F1
- Opens relevant help page'

features.md states:
'## Context Help (Shift+F1)
Get instant help for any BASIC keyword:
- Place cursor on a keyword (like PRINT, FOR, GOTO)
- Press Shift+F1
- Help page for that keyword opens automatically
- Quick way to look up syntax and examples'

Both documents agree on Shift+F1, but the curses documentation mentions Ctrl+A for context help in index.md:
'- **Context-sensitive help**: Press Ctrl+A with cursor on a BASIC keyword for direct help'

This suggests different UIs use different shortcuts for the same feature, which should be clearly documented.

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

'### Variable Inspector

**Currently Implemented:**
- Basic variable viewing via Debug menu

**Display Features (Planned):**
- Tree view
- Type indicators
- Array expansion
- Search/filter'

But then immediately after, it describes a 'Variables Panel (Planned)' with detailed features. The section title 'Variable Inspector' doesn't clearly indicate whether this is the currently implemented feature or a planned enhancement. The structure suggests the entire Variable Inspector is planned, contradicting the 'Currently Implemented' note at the top.

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

**Description:** Conflicting information about Step/Continue/Stop keyboard shortcuts

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md states: 'Note: Step, Continue, and Stop are available via toolbar buttons or the Run menu (no keyboard shortcuts).' However, UI_FEATURE_COMPARISON.md in the 'Debugging Shortcuts' table shows 'Menu/Toolbar' for Tk's Step and Continue actions, which is consistent. But the note in TK_UI_QUICK_START.md could be clearer that these are intentionally toolbar-only.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about settings persistence

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states: 'Settings in files persist across sessions. Settings via SET command only affect current session.' However, TK_UI_QUICK_START.md doesn't mention this distinction when discussing the SET command examples. Users might not realize SET commands don't persist.

---

#### documentation_inconsistency

**Description:** Inconsistent menu access documentation

**Affected files:**
- `docs/user/keyboard-shortcuts.md`

**Details:**
keyboard-shortcuts.md shows 'Menu only' for 'Toggle execution stack window' under Global Commands, but also shows 'Menu only' for 'Show/hide execution stack window' under Debugger section. This is redundant and could be consolidated. Also, 'Ctrl+U' is listed as 'Activate menu bar' but it's unclear if this applies to all sections or just global.

---

#### documentation_inconsistency

**Description:** Inconsistent date format in 'Recently Added' section

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md shows 'Recently Added (2025-10-29)' but the current date context suggests this might be 2024-10-29 or the documentation is from the future. This appears to be a typo in the year.

---

#### documentation_inconsistency

**Description:** Inconsistent Quit keyboard shortcut documentation

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md doesn't explicitly list a Quit shortcut in the shortcuts table. keyboard-shortcuts.md (Curses) lists both 'Ctrl+Q' and 'Ctrl+C' for Quit. UI_FEATURE_COMPARISON.md shows 'Ctrl+Q' for Tk. The TK_UI_QUICK_START.md should include this information.

---

### 🟢 Low Severity

#### code_comment_conflict

**Description:** LineNode docstring contradicts its own structure regarding source_text field

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring states:
"The AST is the single source of truth. Text is always regenerated from the AST using token positions and formatting information.

Note: Do not add a source_text field - it would create a duplicate copy that gets out of sync with the AST."

However, the LineNode class definition does not have a source_text field, so the warning appears to be preemptive documentation rather than describing actual code. This is confusing because it warns against something that doesn't exist in the code.

---

#### code_comment_conflict

**Description:** DimStatementNode has unused token field with misleading comment

**Affected files:**
- `src/ast_nodes.py`

**Details:**
DimStatementNode has field:
token: Optional[Any] = None  # Reserved for future use (currently unused)

This comment suggests the field is intentionally unused and reserved, but it's unclear why it exists at all if unused. Other statement nodes don't have similar placeholder fields. This could be leftover from refactoring.

---

#### documentation_inconsistency

**Description:** VariableNode documentation uses inconsistent terminology for type_suffix

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode docstring says:
"Type suffix handling:
- type_suffix: The actual suffix ($, %, !, #) - may be explicit or inferred
- explicit_type_suffix: Whether type_suffix came from source code (True) or was inferred from a DEF statement (False)"

But the field definition says:
type_suffix: Optional[str] = None  # $, %, !, # (explicit from source OR inferred from DEF)

The comment "explicit from source OR inferred from DEF" contradicts the docstring which says explicit_type_suffix tracks whether it's explicit or inferred. The field comment should just say "$, %, !, #" without the parenthetical.

---

#### code_comment_conflict

**Description:** TypeInfo class docstring describes it as backwards compatibility wrapper but doesn't explain what it's compatible with

**Affected files:**
- `src/ast_nodes.py`

**Details:**
TypeInfo docstring states:
"This class wraps VarType with static helper methods. New code may use VarType directly, but TypeInfo provides backwards compatibility and convenient conversion utilities."

However, there's no explanation of what older code or API it's maintaining compatibility with. If this is truly for backwards compatibility, there should be a deprecation notice or explanation of the migration path.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation style for statement nodes

**Affected files:**
- `src/ast_nodes.py`

**Details:**
Some statement nodes have detailed docstrings with syntax examples (e.g., InputStatementNode, ChainStatementNode, RenumStatementNode), while others have minimal or no docstrings (e.g., EndStatementNode, TronStatementNode, TroffStatementNode). This inconsistency makes the codebase harder to understand and maintain.

---

#### documentation_inconsistency

**Description:** Comment placement inconsistency for SetSettingStatementNode and ShowSettingsStatementNode

**Affected files:**
- `src/ast_nodes.py`

**Details:**
Near line 700, there's a comment:
"# NOTE: SetSettingStatementNode and ShowSettingsStatementNode are defined
# in the "Settings Commands" section below (see line ~980+)."

This forward reference is unusual and suggests the file organization could be improved. The nodes are defined much later in the file, breaking the logical grouping of statement nodes.

---

#### code_vs_comment

**Description:** EOF() method comment describes ^Z handling for mode 'I' but the implementation checks file_info['mode'] == 'I' which may not be fully documented what 'I' represents

**Affected files:**
- `src/basic_builtins.py`

**Details:**
In EOF() method around line 590:
Comment: "Note: For binary input files (mode 'I'), respects ^Z (ASCII 26) as EOF marker (CP/M style)."
Comment: "# Mode 'I' = binary input mode where ^Z checking is appropriate"

The comment explains mode 'I' is binary input, but there's no documentation in the file header or class docstring explaining the file mode conventions ('I', 'O', 'A', 'R', etc.) used by the runtime.

---

#### documentation_inconsistency

**Description:** Module docstring claims 'All BASIC built-in functions' but TabMarker, SpcMarker, and UsingFormatter are not functions, they are classes

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Module docstring at top of basic_builtins.py:
"""
Built-in functions for MBASIC 5.21.

All BASIC built-in functions (SIN, CHR$, INT, etc.)
"""

However, the file contains:
- class TabMarker
- class SpcMarker
- class UsingFormatter
- class BuiltinFunctions

The docstring should say 'Built-in functions and formatting utilities' or similar.

---

#### code_vs_comment

**Description:** Comment in format_numeric_field() mentions 'trailing_minus_only ALWAYS adds a char' but this is implementation detail not clearly stated in parse_numeric_field() spec

**Affected files:**
- `src/basic_builtins.py`

**Details:**
In format_numeric_field() around line 290:
Comment: "# Add sign to content width (trailing_minus_only ALWAYS adds a char, - or space)"

This behavior is implemented correctly (line 340: result_parts.append('-' if is_negative else ' ')), but the parse_numeric_field() method's spec dictionary doesn't document that trailing_minus_only reserves space for both negative and positive numbers (space for positive).

---

#### documentation_inconsistency

**Description:** CaseKeeperTable docstring example shows 'Print' with capital P, but the default policy is 'first_wins' which would preserve whatever case was first set, not necessarily 'Print'

**Affected files:**
- `src/case_keeper.py`

**Details:**
In CaseKeeperTable class docstring:
Example:
    table = CaseKeeperTable()
    table.set("PRINT", "Print")  # Key: "print", Display: "Print"
    table.get("print")  # Returns: "Print"

The example is correct for the specific set() call shown, but could be misleading since it doesn't show what happens if you set("PRINT", "PRINT") first - with first_wins policy, subsequent set("print", "Print") would be ignored and "PRINT" would be retained.

---

#### code_vs_comment

**Description:** Module docstring mentions 'UI' but the code only outputs to stderr, not to any UI component

**Affected files:**
- `src/debug_logger.py`

**Details:**
Module docstring line 3:
"When enabled, errors and debug info are output to both the UI and stderr for
easy visibility when debugging with Claude Code or other tools."

However, debug_log_error() only outputs to stderr (line 80: print(debug_output, file=sys.stderr)) and returns a string. The function doesn't directly output to any UI - it's up to the caller to display the returned string in the UI. The docstring should say 'returns formatted message for UI display' rather than 'output to both the UI and stderr'.

---

#### code_vs_comment

**Description:** Comment about flush() semantics may be misleading

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
InMemoryFileHandle.flush() method has this comment:
"Note: This calls StringIO/BytesIO flush() which are no-ops.
Content is only saved to the virtual filesystem on close().
This differs from file flush() semantics where flush() typically
persists buffered writes. For in-memory files, all writes are
already in memory, so flush() has no meaningful effect."

The code implementation:
```python
def flush(self):
    if hasattr(self.file_obj, 'flush'):
        self.file_obj.flush()
```

The comment is accurate - StringIO/BytesIO flush() are indeed no-ops, and content is saved on close(). However, the comment could be clearer that this is intentional behavior, not a limitation.

---

#### code_vs_documentation

**Description:** Security warning about user_id validation is in docstring but not enforced in code

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
SandboxedFileSystemProvider.__init__() docstring states:
"Security:
- No access to real filesystem
- No path traversal (../ etc.)
- Resource limits enforced
- Per-user isolation via user_id keys in class-level storage
  IMPORTANT: Caller must ensure user_id is securely generated/validated
  to prevent cross-user access (e.g., use session IDs, not user-provided values)"

The code implementation:
```python
def __init__(self, user_id: str, max_files: int = 50, max_file_size: int = 1024 * 1024):
    self.user_id = user_id
    # ... no validation of user_id
```

The code accepts any user_id without validation. The docstring correctly warns that validation is the caller's responsibility, but this could be made more explicit or the class could provide validation helpers.

---

#### documentation_inconsistency

**Description:** Inconsistent description of SandboxedFileIO storage location

**Affected files:**
- `src/file_io.py`

**Details:**
SandboxedFileIO class docstring states:
"Acts as an adapter to backend.sandboxed_fs (SandboxedFileSystemProvider from
src/filesystem/sandboxed_fs.py), which provides an in-memory virtual filesystem.

Storage location: Python server memory (NOT browser localStorage)."

But earlier in the file, the module docstring states:
"* SandboxedFileIO: Python server memory virtual filesystem (Web UI)"

And later:
"* SandboxedFileSystemProvider: Python server memory (Web UI)"

The inconsistency: The documentation is actually consistent - all references say 'Python server memory'. However, the emphasis on 'NOT browser localStorage' in SandboxedFileIO docstring suggests there may have been confusion about this in the past. This is more of a documentation redundancy than an inconsistency.

---

#### documentation_inconsistency

**Description:** FileHandle.flush() method missing from abstract base class but implemented in RealFileHandle

**Affected files:**
- `src/filesystem/base.py`
- `src/filesystem/real_fs.py`

**Details:**
FileHandle abstract base class defines these methods:
- read()
- readline()
- write()
- close()
- seek()
- tell()
- is_eof()

But RealFileHandle implements an additional method:
```python
def flush(self):
    """Flush write buffers."""
    if not self.closed:
        self.file_obj.flush()
```

InMemoryFileHandle also implements flush():
```python
def flush(self):
    """Flush write buffers..."""
    if hasattr(self.file_obj, 'flush'):
        self.file_obj.flush()
```

The inconsistency: flush() is implemented in both concrete classes but not declared as an abstract method in the base class. This means code using FileHandle cannot rely on flush() being available.

---

#### code_vs_documentation

**Description:** Help text claims multi-statement lines work but are not recommended, but no implementation details or limitations are documented

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The _show_help() method states:
'• Multi-statement lines (: separator) work but are not recommended'

However, there is no code in the execute() method that specifically handles or validates multi-statement lines. The code builds 'program_text = "0 " + statement' and parses it, then iterates through 'line_node.statements', which suggests multi-statement support exists through the parser.

The limitation is mentioned but not explained (why not recommended? what are the risks?). This is a minor documentation gap.

---

#### documentation_inconsistency

**Description:** Docstring example shows tuple return format inconsistently

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The execute() method docstring shows examples:
'>>> if executor.can_execute_immediate():
...     success, output = executor.execute("PRINT 2 + 2")
(True, " 4\\n")'

This shows the tuple being printed directly, but the example code shows it being unpacked into variables. The example should either show:
'>>> success, output = executor.execute("PRINT 2 + 2")'
without the tuple display, or:
'>>> executor.execute("PRINT 2 + 2")
(True, " 4\\n")'
without the unpacking. Mixing both is confusing.

---

#### code_vs_comment

**Description:** Comment about waiting_for_input state is contradictory

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The docstring states:
'CAN execute when waiting for input:
- 'waiting_for_input' - Program is waiting for INPUT. Immediate mode is allowed to inspect/modify variables while paused for input. This state is detected by checking if state.input_prompt is not None. However, the user should respond to the input prompt via normal input, not via immediate commands.'

This is contradictory: it says immediate mode IS allowed ('CAN execute') but then says users should NOT use immediate commands ('should respond to the input prompt via normal input, not via immediate commands').

The can_execute_immediate() method returns True when 'state.input_prompt is not None', confirming immediate mode is allowed. But the guidance is unclear about what users should actually do.

---

#### code_vs_documentation

**Description:** Module docstring claims to filter extended ASCII but implementation details differ from description

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Module docstring states:
'1. Filtering out unwanted control characters
2. Clearing parity bits from incoming characters'

And lists issues prevented:
'- Extended ASCII (128-255) causing character mismatches'

However, the is_valid_input_char() function rejects extended ASCII (128-255) entirely, while clear_parity() converts them to standard ASCII (0-127) by clearing bit 7.

These are two different approaches:
1. sanitize_input() REJECTS extended ASCII
2. clear_parity() CONVERTS extended ASCII to standard ASCII

The module docstring doesn't clearly explain that there are two different strategies being used, and sanitize_and_clear_parity() applies BOTH (first convert, then filter), which means the conversion step is partially redundant since filtering happens after.

---

#### code_vs_comment

**Description:** Docstring for cmd_cont() says 'stop_pc itself is NOT cleared' but this is misleading - stop_pc is never explicitly cleared anywhere in the codebase

**Affected files:**
- `src/interactive.py`

**Details:**
Line 336-337 in cmd_cont() docstring:
"- Note: stop_pc itself is NOT cleared (remains for potential debugging)"

This implies there's a design decision to preserve stop_pc, but there's no code anywhere that would clear it. The comment makes it sound like an intentional preservation when it's just never modified. The state management section accurately describes what IS cleared (stopped/halted flags) but the 'NOT cleared' note is unnecessary and potentially confusing.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'immediate mode' vs 'direct command' throughout the file

**Affected files:**
- `src/interactive.py`

**Details:**
Line 6 module docstring uses 'Direct commands':
"- Direct commands (RUN, LIST, SAVE, LOAD, NEW, etc.)"

Line 7 uses 'Immediate mode execution':
"- Immediate mode execution"

Line 176 method name uses 'execute_command':
"def execute_command(self, cmd):"

Line 177 docstring uses both terms:
"Execute a direct command or immediate mode statement"

Line 1009 method name uses 'execute_immediate':
"def execute_immediate(self, statement):"

Line 1010 docstring uses 'immediate mode':
"Execute a statement in immediate mode (no line number)"

The file inconsistently uses 'direct command' and 'immediate mode' to describe the same concept (executing statements without line numbers). This could confuse readers about whether these are different features.

---

#### code_vs_comment

**Description:** Comment about readline Ctrl+A binding is misleading about what 'self-insert' does

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 119-123 comment:
"# Bind Ctrl+A to insert the character instead of moving cursor to beginning-of-line
# This overrides default Ctrl+A (beginning-of-line) behavior.
# When user presses Ctrl+A, the terminal sends ASCII 0x01, and 'self-insert'
# tells readline to insert it as-is instead of interpreting it as a command.
# The \x01 character in the input string triggers edit mode (see start() method)"

The comment says 'self-insert' tells readline to 'insert it as-is', but 'self-insert' in readline actually means 'insert the character into the input buffer'. The comment makes it sound like the character is inserted into the program or output, when it's actually just inserted into the current input line being edited. The phrase 'insert it as-is instead of interpreting it as a command' is technically correct but could be clearer that it's inserting into the input buffer.

---

#### code_vs_comment_conflict

**Description:** Comment about restoring PC is redundant and potentially confusing given the earlier IMPORTANT comment already explained this behavior

**Affected files:**
- `src/interactive.py`

**Details:**
Two comments describe the same PC restoration behavior:

1. "IMPORTANT: GOTO/GOSUB WILL execute during the statement execution below (jumping to program lines and potentially executing code there), but we restore the original PC afterward."

2. Later: "# Restore previous PC to maintain stopped program position\n# This reverts any GOTO/GOSUB PC changes from above execution\nruntime.pc = old_pc"

The second comment is redundant given the detailed IMPORTANT comment above.

---

#### code_vs_comment

**Description:** Comment about skip_next_breakpoint_check timing is ambiguous about when the flag is set vs when it takes effect

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: 'Set to True WHEN halting at a breakpoint (set during the halt). On next execution, if still True, allows stepping past the breakpoint once, then clears itself to False.'

The code at line ~332 shows:
if at_breakpoint:
    if not self.state.skip_next_breakpoint_check:
        self.runtime.halted = True
        self.state.skip_next_breakpoint_check = True
        return self.state
    else:
        self.state.skip_next_breakpoint_check = False

The comment says 'set during the halt' but the flag is actually set BEFORE returning (which causes the halt). The flag is set in the same tick that detects the breakpoint, not 'during' the halt state. This is a minor timing ambiguity.

---

#### documentation_inconsistency

**Description:** Docstring for current_statement_char_end property has overly detailed implementation explanation that may become outdated

**Affected files:**
- `src/interpreter.py`

**Details:**
The docstring at line ~91 provides extensive implementation details:
'Uses max(char_end, next_char_start - 1) to handle string tokens correctly. For the last statement on a line, uses line_text_map to get actual line length (if available), otherwise falls back to stmt.char_end. This works because: - If there's a next statement, the colon is at next_char_start - 1 - If char_end is correct (most tokens), it will be >= next_char_start - 1 - If char_end is too short (string tokens), next_char_start - 1 is larger - If no line_text_map entry exists, returns stmt.char_end as fallback'

This level of implementation detail in a property docstring is unusual and creates maintenance burden - if the implementation changes, the docstring must be updated. A simpler docstring like 'Get current statement char_end, adjusted for token boundaries' would be more maintainable.

---

#### code_vs_comment

**Description:** Docstring for execute_for says string variables in FOR loops are 'uncommon but technically allowed (though not meaningful)' but doesn't explain what happens

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at line ~1027 says: 'The loop variable can have any type suffix (%, $, !, #) and the variable type determines how values are stored, but the loop arithmetic always uses the evaluated numeric values. String variables in FOR loops are uncommon but technically allowed (though not meaningful).'

This raises questions: What happens if you do 'FOR A$ = 1 TO 10'? Does it convert 1 to "1" and store as string? Does the loop arithmetic work? The comment says 'loop arithmetic always uses the evaluated numeric values' but doesn't explain how string variables interact with this. The implementation at lines ~1037-1046 shows it just calls set_variable() with the start value, which would handle type conversion, but the docstring doesn't clarify the behavior.

---

#### code_vs_comment

**Description:** Comment about RESUME 0 vs RESUME None is misleading about runtime behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_resume() says:
"Note: Parser creates different AST representations (None vs 0) to preserve
the original source syntax for round-trip serialization, but the interpreter
treats both identically at runtime (both retry the error statement)."

The code checks: if stmt.line_number is None or stmt.line_number == 0:

This is correct, but the comment could be clearer that the distinction matters for serialization only, not semantics.

---

#### code_vs_comment

**Description:** Comment about NEXT validation uses confusing terminology for sentinel value

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_next() says:
"return_stmt is 0-indexed offset into statements array.
Valid range: 0 to len(statements)-1 for existing statements.
return_stmt == len(statements) is a special sentinel: FOR was last statement, continue at next line.
Values > len(statements) indicate the statement was deleted (validation error)."

The code checks: if return_stmt > len(line_statements):

This is correct, but the comment's explanation of "sentinel value" for return_stmt == len(statements) is confusing. It's not really a sentinel - it's just the natural result of FOR being the last statement (next statement offset would be len(statements)). The comment makes it sound like a special magic value.

---

#### code_vs_comment

**Description:** Comment claims CLEAR silently ignores file close errors, but code shows bare except

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_clear() says:
"Note: Errors during file close are silently ignored (bare except: pass below)"

The code shows:
try:
    file_obj = self.runtime.files[file_num]
    if hasattr(file_obj, 'close'):
        file_obj.close()
except:
    pass

This is correct - bare except with pass does silently ignore errors. However, the comment's phrasing "(bare except: pass below)" suggests the bare except is directly below, but it's actually inside the try block. Minor clarity issue.

---

#### code_vs_comment

**Description:** Comment about latin-1 encoding mentions code pages but doesn't explain conversion process

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in _read_line_from_file() says:
"Encoding:
Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
Unicode U+0000-U+00FF, allowing round-trip byte preservation.
Note: Files using non-English code pages (other than standard ASCII/latin-1)
may require conversion before reading for accurate character display."

The note mentions "conversion before reading" but doesn't explain how users should do this conversion, or whether the interpreter provides any facilities for it. This is more of a documentation gap than an inconsistency.

---

#### code_vs_comment

**Description:** Comment in execute_midassignment() has inconsistent validation description

**Affected files:**
- `src/interpreter.py`

**Details:**
The comment states:
"# Validate start position (must be within string: 0 <= start_idx < len)
# Note: start_idx == len(current_value) is considered out of bounds (can't start replacement past end)
if start_idx < 0 or start_idx >= len(current_value):
    # Start position is out of bounds - no replacement (MBASIC 5.21 behavior)
    return"

The comment says 'must be within string: 0 <= start_idx < len' but then the note redundantly explains the same upper bound condition. The note doesn't add new information beyond what the first line already states.

---

#### code_vs_comment

**Description:** Comment about debugger_set parameter uses inconsistent terminology

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_functioncall(), the comment states:
"# Note: get_variable_for_debugger() and debugger_set=True are used to avoid triggering variable access tracking."

Then later:
"# Restore parameter values (use debugger_set=True to avoid tracking)"

The first comment mentions 'get_variable_for_debugger()' but the code actually calls it without explaining what it does. The second comment is clearer. The terminology 'debugger_set' vs 'avoid tracking' could be more consistent.

---

#### code_vs_comment

**Description:** Comment about latin-1 encoding in LSET/RSET doesn't explain why this encoding was chosen

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_lset() and execute_rset(), the code uses:
buffer_info['buffer'][offset:offset+width] = value.encode('latin-1')

But there's no comment explaining why latin-1 encoding is used instead of ASCII or UTF-8. This is important for understanding character handling in file buffers.

---

#### Code vs Comment conflict

**Description:** Backward compatibility comments reference old method names but don't explain why aliases exist

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py has two backward compatibility aliases:

1. "def print(self, text='', end='\n'):
    '''Deprecated: Use output() instead.
    This is a backward compatibility alias. New code should use output().'''"

2. "def get_char(self):
    '''Deprecated: Use input_char() instead.
    This is a backward compatibility alias. New code should use input_char().
    Note: Always calls input_char(blocking=False) for non-blocking behavior.'''"

However, the module-level comment says: "This method was renamed from print() to output() to avoid conflicts with Python's built-in print function."

This explains print() but doesn't explain why get_char() was renamed to input_char(). The other IOHandler implementations don't have these aliases, suggesting web_io.py had a different evolution path that isn't documented.

---

#### Documentation inconsistency

**Description:** Module docstring references another module (simple_keyword_case.py) that is not present in the provided files

**Affected files:**
- `src/keyword_case_manager.py`
- `src/iohandler/__init__.py`

**Details:**
keyword_case_manager.py docstring states:

"Note: This class provides advanced case policies (first_wins, preserve, error) via CaseKeeperTable and is used by parser.py and position_serializer.py. For simpler force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py) which only supports force_lower, force_upper, and force_capitalize."

However, src/simple_keyword_case.py is not included in the provided source files. This creates a documentation reference to a non-existent (or at least not provided) module.

---

#### Code vs Documentation inconsistency

**Description:** get_char() alias always uses non-blocking mode but original method supports both blocking and non-blocking

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
The get_char() backward compatibility alias documentation says:

"def get_char(self):
    '''Deprecated: Use input_char() instead.
    This is a backward compatibility alias. New code should use input_char().
    Note: Always calls input_char(blocking=False) for non-blocking behavior.'''
    return self.input_char(blocking=False)"

This means old code calling get_char() will always get non-blocking behavior, even if the original implementation supported blocking. This could break backward compatibility if get_char() was previously used in blocking mode. The comment acknowledges this but doesn't explain if this is intentional or a limitation.

---

#### Code vs Comment conflict

**Description:** Comment describes get_cursor_position() as 'difficult' but doesn't explain why or what the challenges are

**Affected files:**
- `src/iohandler/console.py`

**Details:**
console.py get_cursor_position() has this comment:

"def get_cursor_position(self) -> tuple[int, int]:
    '''Get current cursor position.
    Note: This is difficult to implement portably in console.
    Returns (1, 1) by default.'''
    # Getting cursor position in console is complex and platform-specific
    # Return default position
    return (1, 1)"

The comment says it's 'difficult' and 'complex and platform-specific' but doesn't explain what the actual challenges are (ANSI escape sequence queries? Terminal capability detection? Async response handling?). This makes it unclear whether this is a fundamental limitation or just not implemented yet.

---

#### Documentation inconsistency

**Description:** web_io.py has get_screen_size() method not defined in base IOHandler interface

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py implements:

"def get_screen_size(self):
    '''Get terminal size.
    Returns:
        Tuple of (rows, cols) - returns reasonable defaults for web'''
    return (24, 80)"

This method is not defined in the IOHandler base class (base.py), and no other IOHandler implementation (console, curses, gui) implements it. This suggests either:
1. It's a web-specific extension that should be documented as such
2. It should be added to the base interface
3. It's legacy code that should be removed

---

#### documentation_inconsistency

**Description:** Docstring claims lexer is for 'MBASIC 5.21 (CP/M era MBASIC-80)' but also mentions 'Extended BASIC' features without clarification

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring:
"Lexer for MBASIC 5.21 (CP/M era MBASIC-80)
Based on BASIC-80 Reference Manual Version 5.21"

But in read_identifier() comment:
"Subsequent characters can be letters, digits, or periods (in Extended BASIC)"

No clarification whether Extended BASIC features are part of MBASIC 5.21 or if this is supporting multiple BASIC variants.

---

#### code_vs_comment_conflict

**Description:** Comment about file I/O keywords followed by # mentions specific keywords but code checks for a different set

**Affected files:**
- `src/lexer.py`

**Details:**
Comment states:
"Special case: File I/O keywords followed by # (e.g., PRINT#1)
The # is NOT a type suffix here - it's part of the file I/O syntax.
MBASIC allows 'PRINT#1' with no space"

Code checks:
if keyword_part in ['print', 'lprint', 'input', 'write', 'field', 'get', 'put', 'close']:

The comment only mentions PRINT as an example, but doesn't document that this special handling applies to all 8 keywords listed in the code. The comment should list all affected keywords or state 'file I/O keywords such as PRINT, INPUT, etc.'

---

#### code_vs_comment_conflict

**Description:** Comment about REM/REMARK handling describes reading comment text, but implementation details differ from description

**Affected files:**
- `src/lexer.py`

**Details:**
In tokenize() method, comment says:
"# Special handling for REM/REMARK - read comment text"

The code then replaces the token value with comment text:
token = Token(token.type, comment_text, token.line, token.column)

However, for APOSTROPHE comments, the comment text is stored directly in the token value during creation:
self.tokens.append(Token(TokenType.APOSTROPHE, comment_text, start_line, start_column))

The inconsistency is that REM tokens are created with 'rem' as value then replaced, while APOSTROPHE tokens are created directly with comment text. This asymmetry is not explained in comments.

---

#### code_vs_comment

**Description:** at_end_of_line() docstring claims it does NOT check for comments, but at_end_of_statement() does check for comments - inconsistent terminology

**Affected files:**
- `src/parser.py`

**Details:**
at_end_of_line() docstring (line ~130):
"Note: This method does NOT check for comment tokens (REM, REMARK, APOSTROPHE).
Comments are handled separately in parse_line() where they are parsed as
statements and can be followed by more statements when separated by COLON."

at_end_of_statement() docstring (line ~145):
"A statement ends at:
- End of line (NEWLINE or EOF)
- Statement separator (COLON)
- Comment (REM, REMARK, or APOSTROPHE)"

The note in at_end_of_line() suggests comments can be followed by more statements after COLON, but this contradicts the typical behavior where comments consume the rest of the line. The parse_remark() implementation and parse_line() logic show comments DO end the line.

---

#### code_vs_comment

**Description:** Incomplete comment in parse_lprint() - comment ends mid-sentence

**Affected files:**
- `src/parser.py`

**Details:**
At line ~810, the comment reads:
"# Add newline if there's no trailing separator
# Trailing separator means len(separators) == len(expressions)"

This comment appears to be cut off and doesn't complete the explanation. The parse_print() method has a more complete version of this comment that explains the logic fully. This suggests the comment was copied but not completed during implementation.

---

#### documentation_inconsistency

**Description:** Docstring claims 'Array dimensions must be constant expressions' but code doesn't enforce this constraint

**Affected files:**
- `src/parser.py`

**Details:**
Module docstring (line 10):
"- Array dimensions must be constant expressions"

However, the parse_dim() method is not shown in this code snippet, and there's no visible validation in parse_expression() or parse_variable_or_function() that enforces constant expressions for array subscripts. This claim may be aspirational rather than implemented, or the enforcement may be in a different part of the codebase not shown here.

---

#### code_vs_comment

**Description:** Comment about ERR and ERL being 'system variables' conflicts with their placement in expression parsing as special cases

**Affected files:**
- `src/parser.py`

**Details:**
In parse_primary() at lines ~660-670:
"# ERR and ERL are system variables (integer type)
elif token.type in (TokenType.ERR, TokenType.ERL):
    self.advance()
    return VariableNode(
        name=token.type.name,  # 'ERR' or 'ERL'
        type_suffix='%',       # Integer type
        subscripts=[],
        line_num=token.line,
        column=token.column
    )"

The comment says they are 'system variables' but they are handled as special token types (TokenType.ERR, TokenType.ERL) rather than as regular identifiers. This suggests they are keywords/reserved words, not variables. The terminology 'system variables' is misleading.

---

#### code_vs_comment

**Description:** Redundant inline comment in parse_setsetting that duplicates docstring information

**Affected files:**
- `src/parser.py`

**Details:**
In parse_setsetting() method:
- Docstring already documents: "Args:\n    setting_name: String expression identifying the setting"
- Inline comment repeats: "Field name: 'setting_name' (string identifying setting)"
The inline comment adds no new information and could become outdated if refactored.

---

#### code_vs_comment

**Description:** Comment in parse_mid_assignment mentions lexer behavior that may be inconsistent with actual token type

**Affected files:**
- `src/parser.py`

**Details:**
In parse_mid_assignment() docstring:
"Note: The lexer tokenizes 'MID$' in source as a single MID token (the $ is part\nof the keyword, not a separate token)."

Then in the code:
```python
token = self.current()  # MID token (represents 'MID$' from source)
```

This comment describes lexer behavior but doesn't verify it. If the lexer actually produces separate MID and $ tokens, this parser code would fail. The comment should either be verified against lexer implementation or removed.

---

#### code_vs_comment

**Description:** Inconsistent comment style for field name documentation in return statements

**Affected files:**
- `src/parser.py`

**Details:**
Some methods include inline comments documenting field names in return statements:
- parse_showsettings: "pattern=pattern_expr,  # Field name: 'pattern' (optional filter string)"
- parse_setsetting: "setting_name=setting_name_expr,  # Field name: 'setting_name' (string identifying setting)"

But most other methods (parse_goto, parse_gosub, parse_return, etc.) don't include these inline comments. This inconsistency makes the codebase harder to maintain. Either all methods should document field names inline, or none should (relying on docstrings instead).

---

#### code_vs_comment

**Description:** RESUME statement comment mentions 'RESUME 0' behavior but doesn't explain it's equivalent to plain RESUME

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_resume says:
"# Note: RESUME 0 means 'retry error statement' (interpreter treats 0 and None equivalently)"

This note suggests RESUME 0 and RESUME (None) are equivalent, but the docstring only documents 'RESUME [NEXT | line_number]' without mentioning that RESUME 0 is a special case equivalent to plain RESUME. This could confuse users about whether 0 is a valid line number or a special sentinel.

---

#### code_vs_comment

**Description:** WIDTH statement docstring describes 'device' parameter but doesn't clarify what valid device values are

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"Args:
    width: Column width expression (typically 40 or 80)
    device: Optional device expression (typically screen or printer)"

The comment says device is 'typically screen or printer' but doesn't specify if these are string literals, numeric codes, or identifiers. The implementation just parses it as a generic expression without validation or documentation of valid values.

---

#### code_vs_comment

**Description:** DATA statement docstring lists unquoted string examples but doesn't mention that keywords can be part of unquoted strings

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"DATA items can be:
- Numbers: DATA 1, 2, 3
- Quoted strings: DATA 'HELLO', 'WORLD'
- Unquoted strings: DATA HELLO WORLD, FOO BAR

Unquoted strings extend until comma, colon, or end of line"

But the code implementation includes:
"elif tok.value is not None and isinstance(tok.value, str):
    # Any keyword with a string value - treat as part of unquoted string
    # This handles keywords like TO, FOR, IF, etc. in DATA statements"

The docstring doesn't mention that BASIC keywords (TO, FOR, IF, etc.) can be part of unquoted strings in DATA statements, which is a significant parsing behavior.

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

#### code_vs_documentation

**Description:** renumber_with_spacing_preservation() docstring says 'caller must call position_serializer separately' but doesn't explain why or how

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring: 'Text can then be regenerated from updated AST using position_serializer (caller must call position_serializer separately)'

This is vague about:
1. Why the caller needs to call it separately (function doesn't return text)
2. Which position_serializer function to call (serialize_line_with_positions?)
3. Whether the returned LineNodes can be directly serialized

The documentation should be more explicit about the two-step process.

---

#### code_vs_comment

**Description:** serialize_expression() handles VariableNode with 'explicit_type_suffix' attribute but no documentation explains when this attribute is set

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_expression() for VariableNode:
'# Only add type suffix if explicit
if expr.type_suffix and getattr(expr, \'explicit_type_suffix\', False):
    text += expr.type_suffix'

The code checks for an 'explicit_type_suffix' attribute but:
1. No comment explains what makes a type suffix 'explicit' vs implicit
2. No documentation of when this attribute is set during parsing
3. The getattr() with False default suggests it's optional, but why?

This appears to distinguish between 'A$' (explicit) and 'A' (implicit string type), but needs documentation.

---

#### documentation_inconsistency

**Description:** StatementTable.next_pc() docstring describes sequential execution but doesn't mention what happens with GOTO/GOSUB

**Affected files:**
- `src/pc.py`

**Details:**
Docstring: 'Get next PC after given PC (sequential execution).

Sequential execution means:
- Next statement on same line (increment stmt_offset), OR
- First statement of next line (if at end of current line)'

This describes the default sequential flow but doesn't clarify that control flow statements (GOTO, GOSUB, IF THEN line_number) bypass this sequential mechanism. The PC module's top-level docstring mentions 'GOTO just sets npc' but next_pc() doesn't reference this distinction.

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

**Description:** Conditional import handling doesn't match __all__ export

**Affected files:**
- `src/ui/__init__.py`

**Details:**
src/ui/__init__.py conditionally imports CursesBackend:
try:
    from .curses_ui import CursesBackend
    _has_curses = True
except ImportError:
    _has_curses = False
    CursesBackend = None

Then unconditionally exports it in __all__:
__all__ = ['UIBackend', 'CLIBackend', 'VisualBackend', 'CursesBackend', 'TkBackend']

This means CursesBackend will be None if import fails, but it's still exported. Code importing 'from src.ui import CursesBackend' will get None instead of an ImportError, which could cause confusing errors later.

---

#### Code vs Comment conflict

**Description:** Module docstring shows incorrect usage example

**Affected files:**
- `src/ui/auto_save.py`

**Details:**
Module docstring shows:
'Usage:
    manager = AutoSaveManager(autosave_dir=Path.home() / '.mbasic' / 'autosave')
    manager.start_autosave('foo.bas', get_content_callback, interval=30)
    manager.stop_autosave()
    manager.cleanup_after_save('foo.bas')'

However, the __init__ method signature is:
def __init__(self, autosave_dir: Optional[Path] = None):

The example passes a Path object, which is correct, but the docstring doesn't import Path. A complete usage example should show: 'from pathlib import Path' first.

---

#### Code vs Documentation inconsistency

**Description:** UIBackend docstring lists backend types that aren't implemented

**Affected files:**
- `src/ui/base.py`

**Details:**
UIBackend docstring says:
'Different UIs can implement this interface:
- CLIBackend: Terminal-based REPL (current InteractiveMode)
- GUIBackend: Desktop GUI with visual editor
- MobileBackend: Touch-based mobile UI
- WebBackend: Browser-based interface
- HeadlessBackend: No UI, for batch processing'

But only CLIBackend is actually implemented in the provided code. The __init__.py shows: VisualBackend, TkBackend, and optionally CursesBackend exist, but GUIBackend, MobileBackend, WebBackend, and HeadlessBackend are not implemented. The docstring should either list only implemented backends or clarify these are planned/example backends.

---

#### Code vs Comment conflict

**Description:** CLIBackend docstring shows incorrect import path

**Affected files:**
- `src/ui/cli.py`

**Details:**
CLIBackend docstring shows usage:
'from src.iohandler.console import ConsoleIOHandler
from editing import ProgramManager
from src.ui.cli import CLIBackend'

The import 'from editing import ProgramManager' uses a relative module name 'editing' without 'src.' prefix, while the other imports use 'src.' prefix. This inconsistency suggests either the import example is wrong or the actual module structure is different than shown.

---

#### Code vs Documentation inconsistency

**Description:** CLIBackend references non-existent cli_debug module

**Affected files:**
- `src/ui/cli.py`

**Details:**
In CLIBackend.__init__:
# Add debugging capabilities
from .cli_debug import add_debug_commands
self.debugger = add_debug_commands(self.interactive)

However, cli_debug.py is not provided in the source code listing. This import will fail at runtime. Either the file is missing from the listing or this is dead code that should be removed.

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

**Description:** Comment says cursor positioned at column 7 but code calculates position dynamically based on line content

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress method around line 400, comment implies fixed column positioning:
"# Position cursor after first line number and space"

But implementation uses dynamic calculation:
"pos = 1  # Skip status char
while pos < len(first_line) and first_line[pos].isdigit():
    pos += 1
if pos < len(first_line) and first_line[pos] == ' ':
    pos += 1  # Skip space after line number
self.edit_widget.set_edit_pos(pos)"

This is actually correct for variable-width, but the earlier references to column 7 create confusion.

---

#### code_vs_comment

**Description:** Comment about toolbar removal references method that still exists in code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _create_ui() method:
Comment says: "# Toolbar removed from UI layout - use Ctrl+U menu instead for keyboard navigation
# (_create_toolbar method still exists but is not called)"

This is consistent with the code (method exists but isn't called), but the dual comments about the same unused method in two places could lead to maintenance issues if one is updated and the other isn't.

---

#### code_vs_comment

**Description:** Interpreter lifecycle comment contradicts itself about recreation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in __init__() says:
"# Interpreter Lifecycle:
# Created ONCE here in __init__ and reused throughout the session.
# The interpreter is NOT recreated in start() - only ImmediateExecutor is.
# Note: The immediate_io handler created here is temporary - ImmediateExecutor
# will be recreated in start() with a fresh OutputCapturingIOHandler, but
# this same interpreter instance will be reused with the new executor."

Then in start() method, the code creates a NEW ImmediateExecutor:
"immediate_io = OutputCapturingIOHandler()
self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)"

The comment says the interpreter is reused with the new executor, but it's unclear if the new ImmediateExecutor actually reuses the same interpreter instance or creates a new one. The comment implies reuse but doesn't match the constructor call pattern.

---

#### code_vs_comment

**Description:** Comment about help widget lifecycle contradicts toggle support claim

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_help() docstring:
"Note: Unlike _show_keymap and _show_settings which support toggling,
help doesn't store overlay state so it can't be toggled off. The help
widget handles its own close behavior via ESC/Q keys."

Then in the method body:
"# Help widget manages its own lifecycle - it doesn't support toggling
# like _show_keymap and _show_settings do, so we don't store the overlay
# or main widget. Help closes via ESC/Q handled internally by HelpWidget."

This is internally consistent, but the comment in _show_keymap() says:
"This method supports toggling - calling it when keymap is already open will close it."

The inconsistency is that help could theoretically support toggling like keymap does, but chooses not to. The comments don't explain why this design decision was made.

---

#### documentation_inconsistency

**Description:** Variable naming inconsistency in comments vs code for editor lines storage

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in __init__() says:
"# Editor state
# Note: self.editor_lines is the CursesBackend's storage dict
# self.editor.lines is the ProgramEditorWidget's storage dict (different object)
self.editor_lines = {}  # line_num -> text for editing"

But throughout the code, self.editor_lines is used inconsistently:
- In _smart_insert_line(): self.editor.lines[insert_num] = ""
- In _renumber_lines(): self.editor.lines[new_line_num] = code
- In _delete_current_line(): del self.editor.lines[line_number]

The comment suggests two separate storage dicts exist, but the code primarily uses self.editor.lines, not self.editor_lines. This suggests either the comment is outdated or the implementation doesn't match the design.

---

#### code_vs_comment

**Description:** Comment describes layout positions that may not match actual implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _toggle_variables_window() method:

Comment says: "# Layout: menu (0), editor (1), variables (2), output (3), status (4)"

But in _toggle_stack_window() method:

Comment says: "# Layout: menu (0), editor (1), [variables (2)], [stack (2 or 3)], output, status"

These two comments describe different layouts. The second comment shows variables and stack as optional (in brackets) and doesn't number output and status, while the first shows a fixed layout with all positions numbered. This suggests the layout is dynamic but the comments don't consistently reflect this.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of main widget storage approach

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _toggle_settings() method docstring:

"Main widget storage: Uses self.main_widget (stored in __init__) rather than self.loop.widget (which might be a menu or other overlay)."

And in the method body:

"# Main widget storage: Use self.main_widget (stored at UI creation)
# not self.loop.widget (current widget which might be a menu or overlay)"

These two comments say essentially the same thing but use different terminology: "stored in __init__" vs "stored at UI creation". While not contradictory, this inconsistency could cause confusion about when/where main_widget is initialized.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'No state checking - just ask the interpreter' but code doesn't actually check interpreter state

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line ~1130:
# Check if interpreter has work to do (after RUN statement)
# No state checking - just ask the interpreter
has_work = self.interpreter.has_work() if self.interpreter else False

The comment 'No state checking' is ambiguous - it's unclear what state checking is being avoided or why this is significant.

---

#### code_inconsistency

**Description:** Inconsistent error message format between cmd_save and cmd_merge

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
cmd_save uses:
self._write_output(f"?Error saving file: {e}\n")

cmd_merge uses:
self._write_output(f"?{e}\n")

Both handle exceptions but format error messages differently - one includes context ('Error saving file:'), the other doesn't.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'Parse editor content into program' but then immediately clears and rebuilds program

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line ~1050:
# Parse editor content into program (in case user typed lines directly)
# This updates self.program but doesn't affect runtime yet
self._parse_editor_content()

# Load program lines into program manager
self.program.clear()
for line_num in sorted(self.editor_lines.keys()):
    line_text = f"{line_num} {self.editor_lines[line_num]}"
    self.program.add_line(line_num, line_text)

The comment says 'This updates self.program' but the very next line clears self.program, suggesting the parse is actually updating editor_lines, not self.program directly.

---

#### code_vs_comment

**Description:** Footer text in HelpWidget shows hardcoded keys that may not match actual keybindings configuration

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Footer text hardcoded as:
self.footer = urwid.Text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search U=Back ESC/Q=Exit ")

These keys (U, /, ESC, Q) are hardcoded in the footer display and in keypress() method, but HelpMacros loads keybindings from JSON. If keybindings change in JSON, footer won't reflect actual bindings.

---

#### code_vs_comment

**Description:** Comment in fmt_key() function acknowledges limitation but doesn't explain why it's acceptable

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Comment states:
"Limitation: Only handles 'Ctrl+' prefix. Other formats like 'Alt+X',
'Shift+Ctrl+X', or 'F5' are returned unchanged. This is acceptable for
the curses menu which primarily uses Ctrl+ keybindings."

However, the menu structure shows items like 'Keyboard Shortcuts' and 'Settings' which may have non-Ctrl keybindings (F1, F12, etc.). The comment assumes all menu items use Ctrl+ but doesn't verify this assumption.

---

#### documentation_inconsistency

**Description:** TODO comment indicates version should be imported from src.version module but is hardcoded

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
In _expand_macro method:
# TODO: Import version from src.version module instead of hardcoding
return "5.21"  # MBASIC version (hardcoded)

This TODO indicates the implementation is incomplete and inconsistent with intended design.

---

#### code_vs_comment

**Description:** Comment describes tier label mapping but implementation has inconsistency in how 'Other' tier is determined

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment states:
"# Map tier to labels for search result display
# Note: UI tier (e.g., 'ui/curses', 'ui/tk') is detected via startswith('ui/')
# check below and gets '📘 UI' label. Other unrecognized tiers get '📙 Other'."

But the code shows:
tier_labels = {
    'language': '📕 Language',
    'mbasic': '📗 MBASIC',
}

The comment mentions UI tier detection but tier_labels dict doesn't include 'ui' key. The logic relies on startswith('ui/') check later, which is inconsistent with the dict-based approach for other tiers.

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

**Description:** Variables window appears in two different categories with different descriptions

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
VARIABLES_DISPLAY appears twice in KEYBINDINGS_BY_CATEGORY:

1. In 'Global Commands': (VARIABLES_DISPLAY, 'Toggle variables watch window')
2. In 'Debugger (when program running)': (VARIABLES_DISPLAY, 'Show/hide variables window')

These describe the same key with slightly different wording ('Toggle' vs 'Show/hide' and 'watch window' vs 'window'). While semantically similar, this duplication and inconsistent wording could confuse users.

---

#### code_vs_comment

**Description:** Comment about Ctrl+S being unavailable is incomplete

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment says:
"# Save program (Ctrl+S unavailable - terminal flow control)
# Use Ctrl+V instead (V for saVe)"

The comment explains Ctrl+S is unavailable due to terminal flow control (XON/XOFF), but doesn't explain that Ctrl+Q is also affected by this same issue. Since QUIT_KEY uses Ctrl+Q, this creates an inconsistency - if Ctrl+S is avoided for flow control, why is Ctrl+Q used for quit when it's also a flow control character (XON)?

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization in help text

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
KEYBINDINGS_BY_CATEGORY has inconsistent capitalization:
- Some entries: 'Quit', 'Run program', 'New program'
- Other entries: 'This help' (lowercase 'help')
- Mixed: 'Continue execution (Go)' vs 'Stop execution (eXit)' - 'Go' is capitalized but 'eXit' has unusual capitalization

While minor, this inconsistency affects the professional appearance of the help system.

---

#### Code duplication with inconsistency risk

**Description:** Table formatting code is duplicated between files with warning comment

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

The code itself acknowledges duplication exists. While not strictly an inconsistency yet, this is a maintenance risk where the two implementations could diverge.

---

#### Documentation inconsistency

**Description:** Comment describes tooltip behavior but implementation uses inline label

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 177-181:
else:
    # Show short help as inline label (not a hover tooltip, just a gray label)
    if defn.help_text:
        help_label = ttk.Label(frame, text=defn.help_text,
                              foreground='gray', font=('TkDefaultFont', 9))

The comment explicitly clarifies 'not a hover tooltip, just a gray label', suggesting there may have been confusion or a previous implementation that used tooltips. The comment is accurate but indicates potential past inconsistency.

---

#### Code vs Comment conflict

**Description:** Modal dialog comment says 'non-blocking' but uses grab_set() which blocks input to other windows

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 48-49:
# Make modal (grab input focus, but non-blocking - no wait_window())
self.transient(parent)
self.grab_set()

The comment says 'non-blocking' but grab_set() makes the dialog modal by preventing interaction with other windows. The comment likely means 'non-blocking to code execution' (no wait_window() call), but the phrasing is confusing since the dialog does block user interaction with the parent window.

---

#### Code vs Documentation inconsistency

**Description:** Docstring lists features but omits context menu functionality

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Module docstring (lines 1-9) lists:
- Scrollable help content display
- Clickable links
- Search across multi-tier help system with ranking and fuzzy matching
- In-page search (Ctrl+F) with match highlighting
- Navigation history (back button)

However, the code implements a right-click context menu (line 598-643) with 'Copy', 'Select All', and 'Open in New Window' features that are not mentioned in the module docstring.

---

#### code_vs_comment

**Description:** Comment says immediate_history and immediate_status are set to None but explains they are 'not currently used'

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~450:
"# Set immediate_history and immediate_status to None
# These attributes are not currently used but are set to None for defensive programming
# in case future code tries to access them (will get None instead of AttributeError)
self.immediate_history = None
self.immediate_status = None"

This suggests these were previously used features that were removed. The comment is accurate but indicates potential technical debt or incomplete refactoring.

---

#### code_vs_comment

**Description:** Toolbar comment says features are accessible via menus but doesn't mention all removed features

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~650:
"# Note: Toolbar has been simplified to show only essential execution controls.
# Additional features are accessible via menus:
# - List Program → Run > List Program
# - New Program (clear) → File > New
# - Clear Output → Run > Clear Output"

This implies these specific features were removed from toolbar, but doesn't explain what other features might have been removed or why these three are specifically mentioned.

---

#### documentation_inconsistency

**Description:** Docstring mentions 'Syntax highlighting (optional)' but no implementation or configuration is shown

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Class docstring lists:
"    Provides a graphical UI with:
    - Menu bar (File, Edit, Run, Help)
    - Toolbar with common actions
    - 3-pane vertical layout:
      ...
    - Syntax highlighting (optional)
    - File dialogs for Open/Save"

No syntax highlighting code is present in the visible portion of the file, and no configuration option for enabling/disabling it is shown. This may be implemented elsewhere or may be a planned feature.

---

#### code_vs_comment

**Description:** Comment says validation happens 'after cursor movement/clicks' but implementation uses 100ms delay which could miss rapid movements

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1625:
# Note: This method is called with a delay (100ms) after cursor movement/clicks
# to avoid excessive validation during rapid editing

Code at lines ~1677-1679:
def _on_cursor_move(self, event):
    self._check_line_change()
    # Also validate syntax after movement
    self.root.after(100, self._validate_editor_syntax)

The 100ms delay means if user moves cursor multiple times within 100ms, only the last movement triggers validation. Comment implies validation happens 'after' movements but doesn't clarify the debouncing behavior.

---

#### code_vs_comment

**Description:** Docstring for _edit_array_element says it 'pre-fills with the last accessed subscripts' but code has complex fallback logic not mentioned

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring at lines ~1055-1062:
The dialog pre-fills with the last accessed subscripts and value if available,
extracted from value_display (e.g., "[5,3]=42" portion).

Code at lines ~1088-1103 has additional logic:
# If no default subscripts, use first element based on array_base
if not default_subscripts and dimensions:
    array_base = self.runtime.array_base
    if array_base == 0:
        default_subscripts = ','.join(['0'] * len(dimensions))
    elif array_base == 1:
        default_subscripts = ','.join(['1'] * len(dimensions))
    else:
        default_subscripts = ','.join(['0'] * len(dimensions))

Docstring doesn't mention the fallback to first element when no last accessed subscripts exist.

---

#### code_vs_comment

**Description:** Comment says 'No formatting is applied' but then mentions 'Some formatting may occur elsewhere'

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines ~1547-1551:
Line numbers are part of the text content as entered by user.
No formatting is applied to preserve compatibility with real MBASIC.
...
# Note: Some formatting may occur elsewhere (e.g., variable display, stack display)
# This preserves compatibility with real MBASIC for program text

The comment contradicts itself - first says no formatting, then says some formatting may occur. This is confusing about what the actual behavior is.

---

#### code_vs_comment

**Description:** Comment in _on_paste says 'Single line paste' but the condition checks for both no newlines AND existing content, making it more specific than described

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment says: "# Single line paste - check if we're in the middle of an existing line"

But the actual logic is:
if '\n' not in sanitized_text:
    # ... check current_line_text ...
    if current_line_text:
        # Simple inline paste

This is not just "single line paste" - it's specifically "single line paste into a non-empty line". The comment should clarify this distinction since empty lines are handled differently (they go through auto-numbering logic).

---

#### code_vs_comment

**Description:** Comment in _smart_insert_line says it inserts 'blank line' but the implementation actually inserts a numbered line with a space, not truly blank

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment says: "Smart insert - insert blank line between current and next line."

But code does:
new_line_text = f'{insert_num} \n'
self.editor_text.text.insert(f'{insert_index}.0', new_line_text)

This creates a line like '10 \n' which has a line number and space, not a truly blank line. The comment later clarifies this won't be saved until user types content, but the initial description is misleading.

---

#### code_vs_comment

**Description:** Inconsistent terminology: 'immediate mode' vs 'immediate mode panel' vs 'immediate mode area' used interchangeably

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Multiple references:
- "_focus_immediate_entry" docstring: "Focus the immediate mode entry widget when clicking in immediate mode area."
- "_update_immediate_status" docstring: "Update immediate mode panel status based on interpreter state."
- Method names use "immediate" without qualifier

While not technically wrong, consistent terminology would improve code clarity. Should standardize on one term (e.g., 'immediate mode panel' or 'immediate mode area').

---

#### code_vs_comment

**Description:** Misleading method name _add_immediate_output() that doesn't actually add to immediate output

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method _add_immediate_output() has docstring:
"Add text to main output pane.

This method name is historical - it simply forwards to _add_output().
In the Tk UI, immediate mode output goes to the main output pane."

The method name suggests it adds to immediate output, but it actually adds to main output. While the docstring explains this is historical, the name is misleading and could be refactored to _add_output() directly or renamed to clarify its actual behavior.

---

#### code_vs_comment

**Description:** Comment about 'execute without echoing' contradicts typical BASIC immediate mode behavior

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _execute_immediate() states:
"Execute without echoing (GUI design choice: command is visible in entry field,
and 'Ok' prompt is unnecessary in GUI context - only results are shown)"

While this is a valid design choice, it contradicts traditional BASIC immediate mode where commands are echoed to output. The comment justifies this but doesn't acknowledge it's a deviation from standard BASIC behavior. This could be documented more clearly as a deliberate design decision that differs from traditional BASIC interpreters.

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
Comment says: "Note: If source_text doesn't match pattern, falls back to relative_indent=1
This can cause inconsistent indentation for programmatically inserted lines"
This is a warning about a known issue, but the function doesn't provide any way to handle or detect this inconsistency. The comment acknowledges the problem but the code doesn't offer a solution or flag.

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No UI-framework dependencies' but doesn't mention the glob and os imports which are standard library

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says: "No UI-framework dependencies (Tk, curses, web) are allowed, though standard library modules (os, glob, re) are permitted."
This is consistent with the imports, but the phrasing could be clearer. It says 'no UI-framework dependencies are allowed' then says 'though standard library modules are permitted' - the 'though' suggests a contradiction when there isn't one.

---

#### code_vs_documentation

**Description:** update_line_references() docstring says it uses 'regex-based approach (fast, good for most cases)' but doesn't document limitations

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says: "Uses regex-based approach (fast, good for most cases)."
This implies there are cases where it's NOT good, but the docstring doesn't explain what those cases are or what the limitations are. The comment about 'Two-pass approach' in the code suggests complexity but no documentation of edge cases.

---

#### code_vs_comment

**Description:** update_line_references() regex pattern comment says 'ON <expr> GOTO/GOSUB' but pattern uses [^G]+ which is 'not G' not 'expression'

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment says: "Keywords: GOTO, GOSUB, THEN, ELSE, or 'ON <expr> GOTO/GOSUB'"
Pattern is: r'\b(GOTO|GOSUB|THEN|ELSE|ON\s+[^G]+\s+GOTO|ON\s+[^G]+\s+GOSUB)\s+(\d+)'
The [^G]+ means 'one or more characters that are not G', which is a hack to match the expression between ON and GOTO/GOSUB. This works but is fragile and the comment doesn't explain why this approach was chosen.

---

#### code_vs_comment

**Description:** serialize_expression() docstring mentions ERR and ERL special handling but doesn't explain why they're special

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says: "ERR and ERL are special system variables that are serialized without parentheses (e.g., 'ERR' not 'ERR()') when they appear as FunctionCallNode with no arguments, matching MBASIC 5.21 syntax."
This explains WHAT but not WHY. The code checks if expr.name in ('ERR', 'ERL') and len(expr.arguments) == 0, but doesn't explain why these are parsed as FunctionCallNode if they're variables. This suggests a parser quirk that should be documented.

---

#### code_vs_documentation

**Description:** cycle_sort_mode() docstring says it 'matches the Tk UI implementation' but this is supposed to be UI-agnostic

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Docstring says: "The cycle order is: accessed -> written -> read -> name -> (back to accessed)
This matches the Tk UI implementation."
The module is supposed to provide 'consistent variable sorting behavior across all UI backends', so referencing a specific UI implementation suggests this was copied from Tk rather than being truly UI-agnostic. The comment should explain the rationale for this cycle order, not just say it matches Tk.

---

#### code_vs_documentation

**Description:** get_sort_key_function() has fallback comment mentioning 'old type/value modes' but these aren't documented anywhere

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Comment says: "Default to name sorting (unknown modes fall back to this, e.g., old 'type'/'value')"
This suggests there were previously 'type' and 'value' sort modes that have been removed, but there's no documentation of this change or why they were removed. The comment is likely outdated.

---

#### code_vs_documentation

**Description:** get_default_reverse_for_mode() docstring mentions 'Name/type/value sorts' but only 'name' is a valid mode

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Docstring says: "Name/type/value sorts default to reverse=False (ascending)."
But get_variable_sort_modes() only returns 'accessed', 'written', 'read', 'name'. There are no 'type' or 'value' modes. This is inconsistent with the available modes.

---

#### code_vs_comment

**Description:** get_cursor_position() docstring says it returns a dict but implementation comment says it's not implemented and returns placeholder

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Docstring:
"Get current cursor position (placeholder implementation).

Returns:
    Dict with 'line' and 'column' keys (always returns {0, 0} - not implemented)"

The docstring acknowledges it's not implemented but describes it as if it works. The comment inside says:
"# This would need async support, for now return placeholder"

This is confusing - the method appears functional but always returns {0, 0}.

---

#### documentation_inconsistency

**Description:** Incomplete stub implementations for cmd_delete, cmd_renum, and cmd_cont have only comments but no actual code or error messages

**Affected files:**
- `src/ui/visual.py`

**Details:**
Methods cmd_delete(), cmd_renum(), and cmd_cont() contain only comments like:
"# Parse args (e.g., '10-50' or '100')
# Call self.program.delete_line() or delete_range()"

But cmd_list(), cmd_new(), cmd_save(), and cmd_load() have actual implementations. This inconsistency in the stub template may confuse developers about which methods need implementation vs which are provided.

---

#### code_vs_documentation

**Description:** add_breakpoint() and set_current_statement() docstrings describe BASIC line numbers but implementation details unclear about conversion

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Docstrings say:
"Add breakpoint marker (red background) to BASIC line number.

Args:
    line_num: BASIC line number (e.g., 10, 20, 30)"

and

"Highlight current executing statement (green background).

Args:
    line_num: BASIC line number, or None to clear highlighting"

But the JavaScript method calls don't show any conversion from BASIC line numbers (10, 20, 30) to editor line indices (0, 1, 2). It's unclear if the JavaScript side handles this conversion or if the Python side should.

---

#### code_vs_comment

**Description:** add_find_highlight() docstring says line parameter is 0-based but add_breakpoint() says line_num is BASIC line number

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
add_find_highlight() docstring:
"Args:
    line: 0-based line number"

add_breakpoint() docstring:
"Args:
    line_num: BASIC line number (e.g., 10, 20, 30)"

This inconsistency in parameter semantics (0-based editor lines vs BASIC line numbers) could lead to confusion about which methods expect which type of line reference.

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

The comment references _get_input as the input_callback, but the coordination mechanism and Future handling is not visible in the provided code. This may be implemented elsewhere but the comment suggests it should be in the shown code.

---

#### code_vs_comment

**Description:** Comment at line ~2609 references _on_editor_change method but method implementation is not shown

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2609 comment states:
"# The _on_editor_change method (defined at line ~2609) handles:
# - Removing blank lines
# - Auto-numbering
# - Placeholder clearing"

This is a self-referential comment claiming the method is defined at that line, but the actual method implementation is not included in the provided code excerpt. The comment appears to be a placeholder or the code is truncated.

---

#### code_vs_comment

**Description:** Comment claims prompt display is handled by _enable_inline_input() but method is not shown

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~60-62 comment in SimpleWebIOHandler.input():
"# Don't print prompt here - the input_callback (backend._get_input) handles
# prompt display via _enable_inline_input() method in the NiceGUIBackend class"

The comment references _enable_inline_input() method that should exist in NiceGUIBackend class, but this method is not visible in the provided code excerpt.

---

#### documentation

**Description:** Docstring references feature audit document that may be outdated

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2543 in NiceGUIBackend class docstring:
"Based on TK UI feature set (see docs/dev/TK_UI_FEATURE_AUDIT.md)."

This references an external documentation file that is not provided. Cannot verify if the implementation actually matches the audit or if the audit is up to date.

---

#### code_internal

**Description:** Incomplete code excerpt with placeholder comment about method location

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
The code ends abruptly at line ~2609 with a comment:
"# Content change handlers via CodeMirror's on_change callback
# The _on_editor_change method (defined at line ~2609) handles:"

This suggests the code excerpt is incomplete and the actual implementation continues beyond what is shown. The comment with '~2609' indicates approximate line numbers, suggesting this is a partial view.

---

#### code_vs_comment

**Description:** Comment says 'interpreter/runtime reused to preserve session state' but code creates new IO handler

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2110 in _menu_step_stmt:
  # Create new IO handler for execution (interpreter/runtime reused to preserve session state)
  self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)
  self.interpreter.io = self.exec_io
The comment suggests reuse but the code creates a NEW IO handler. This is likely intentional (new handler for new execution context) but the comment is confusing.

---

#### code_vs_comment

**Description:** Comment about readonly output textarea contradicts INPUT handling implementation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1730:
  # INPUT handling: When INPUT statement executes, the immediate_entry input box
  # is focused for user input (see _execute_tick() lines ~1886-1888).
  # The output textarea remains readonly.

But line ~1740:
  # Set up Enter key handler for output textarea (for future inline input feature)
  self.output.on('keydown.enter', self._handle_output_enter)

The comment says output remains readonly, but there's a keydown handler suggesting future inline input. Also, _menu_stop (line ~1980) has code to make output readonly again, implying it might not always be readonly.

---

#### code_vs_comment

**Description:** Comment about RUN with line number references non-existent attribute

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1835 in _menu_run:
  # Check if RUN was called with a line number (e.g., RUN 120)
  # This is set by immediate_executor when user types "RUN 120"
  if hasattr(self, '_run_start_line') and self._run_start_line:
      # Set PC to start at the specified line
      from src.pc import PC
      self.runtime.npc = PC.from_line(self._run_start_line)
      # Clear the temporary attribute
      self._run_start_line = None

This references immediate_executor setting _run_start_line, but immediate_executor is not shown in this file. The comment describes cross-module behavior without showing the other side.

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

The logic doesn't truly prevent numbering 'once' - it prevents numbering lines that didn't exist in the old snapshot OR when line count increased. A line could theoretically be numbered multiple times if it meets the conditions repeatedly.

---

#### documentation_inconsistency

**Description:** Docstring for start() says 'Not implemented' but then says to use start_web_ui() function, which is confusing

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring: 'Not implemented - raises NotImplementedError. Use start_web_ui() module function instead for web backend.'

This is technically correct but confusing - it's not 'not implemented', it's 'intentionally raises error to redirect to correct function'. The phrasing suggests incomplete code rather than intentional design.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Variables window

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md states Variables window shortcut is 'Ctrl+V' for all UIs.

editor-commands.md also lists 'Ctrl+V' for Variables window.

However, debugging.md says 'Tk UI: Debug → Variables or Ctrl+V' but editor-commands.md doesn't mention the menu alternative. Minor documentation completeness issue.

---

#### code_vs_comment

**Description:** Comment says 'Legacy class kept for compatibility' but class is marked DEPRECATED in name

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Line comment: '# Legacy class kept for compatibility - new code should use direct web URL instead'

Class name: 'WebHelpLauncher_DEPRECATED'

The comment suggests it's kept for compatibility (implying it still works and is used), but the _DEPRECATED suffix and the comment 'new code should use direct web URL' suggests it shouldn't be used. The docstring also says 'Legacy class wrapper for compatibility' but doesn't specify what code depends on it.

---

#### documentation_inconsistency

**Description:** Inconsistent command listing - debugging.md has more complete shortcuts than editor-commands.md

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md lists:
- Ctrl+R: Run program
- Ctrl+T: Step
- Ctrl+G: Continue
- Ctrl+Q: Stop
- Ctrl+V: Variables window
- Ctrl+K: Stack window
- Ctrl+B (Tk) / b (Curses): Toggle breakpoint

editor-commands.md 'Debugging Commands' section lists the same shortcuts but doesn't mention that 'b' is Curses-specific for breakpoints in the main table (only in the note).

---

#### code_vs_documentation

**Description:** Settings dialog exists in code but not documented in help system

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/debugging.md`

**Details:**
web_settings_dialog.py implements a full settings dialog with:
- Editor settings (auto-numbering, line number increment)
- Limits settings (read-only)
- Save/Cancel functionality

But none of the help documentation (debugging.md, editor-commands.md, getting-started.md, etc.) mentions how to access settings or what settings are available. The Web UI help index (docs/help/ui/web/index.md) is not provided but likely should document this.

---

#### documentation_inconsistency

**Description:** README mentions visual backend but index.md doesn't

**Affected files:**
- `docs/help/README.md`
- `docs/help/common/index.md`

**Details:**
README.md states:
'**Note:** The visual backend is part of the web UI implementation.'

But common/index.md and other help files don't explain what the 'visual backend' is or how it relates to the web UI. This could confuse users looking for a 'visual' UI option.

---

#### documentation_inconsistency

**Description:** Inconsistent END statement usage in examples

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/examples/hello-world.md`

**Details:**
debugging.md test program:
'60 END'

hello-world.md states:
'Line 20: END
- Tells BASIC to stop running the program
- Always good practice to end programs with END'

But some examples in loops.md and other files don't consistently use END (some do, some don't). This might confuse beginners about whether END is required.

---

#### code_vs_comment

**Description:** Function open_help() docstring incomplete

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Function definition:
def open_help():
    """Open help documentation in browser (default page)."""
    return open_help_in_browser()

The docstring says 'default page' but doesn't specify what the default is. Looking at open_help_in_browser(), the default is f'{HELP_BASE_URL}/ui/{ui_type}/' where ui_type defaults to 'tk'. The simple wrapper doesn't pass ui_type, so it uses 'tk' by default, which might not be correct for all callers.

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

**Description:** VARPTR and DEF USR have identical 'See Also' sections but different implementation notes

**Affected files:**
- `docs/help/common/language/functions/varptr.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
Both VARPTR and DEF USR have the exact same 'See Also' list (FRE, HELP SET, INKEY$, INP, LIMITS, NULL, PEEK, RANDOMIZE, REM, SET, SHOW SETTINGS, TRON/TROFF, USR/VARPTR, WIDTH). However, VARPTR says 'Function is not available' while DEF USR says 'Statement is parsed but no operation is performed'. If they're related enough to share See Also lists, their implementation status should be consistent.

---

#### documentation_inconsistency

**Description:** DEF FN documentation describes extension (multi-character function names) but doesn't clearly mark it as non-standard

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
The DEF FN documentation extensively describes multi-character function names as 'This implementation (extension)' but the main syntax section doesn't have a clear warning that this differs from original MBASIC 5.21. The syntax shows both forms as equally valid without indicating one is an extension. Compare to USR/VARPTR/CALL which have prominent '⚠️ **Not Implemented**' warnings.

---

#### documentation_inconsistency

**Description:** Inconsistent formatting of 'See Also' sections

**Affected files:**
- `docs/help/common/language/statements/data.md`
- `docs/help/common/language/statements/def-fn.md`

**Details:**
DATA statement has a 'See Also' section with only 2 items (READ, RESTORE), while DEF FN has 3 items (DEF USR, USR, GOSUB-RETURN). Most other docs have much longer See Also lists (10+ items). This suggests incomplete cross-referencing or inconsistent standards for what should be included.

---

#### documentation_inconsistency

**Description:** CLOSE documentation has minimal 'See Also' section compared to similar I/O commands

**Affected files:**
- `docs/help/common/language/statements/close.md`

**Details:**
CLOSE only lists 5 related items (OPEN, RESET, END, STOP, EOF) while other I/O commands like CLOAD/CSAVE list 8+ items. Missing obvious related commands like INPUT#, PRINT#, GET, PUT, etc.

---

#### documentation_inconsistency

**Description:** CLS documentation has no 'See Also' section

**Affected files:**
- `docs/help/common/language/statements/cls.md`

**Details:**
CLS is the only statement in the provided docs with no 'See Also' section at all. It should at least reference other display-related commands or formatting functions.

---

#### documentation_inconsistency

**Description:** Index claims 45 intrinsic functions but DEF FN is user-defined, not intrinsic

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/statements/def-fn.md`

**Details:**
The language index states 'Functions - 45 intrinsic functions' but DEF FN defines user-defined functions, not intrinsic ones. The count may be incorrect or the categorization is unclear.

---

#### documentation_inconsistency

**Description:** AUTO example uses # for comments which is not standard BASIC syntax

**Affected files:**
- `docs/help/common/language/statements/auto.md`

**Details:**
AUTO example shows: 'AUTO 100,50    # Generates line numbers 100, 150, 200 •••'. The # symbol is not documented as a comment character in BASIC-80. Standard comment is REM statement. This should use REM or be marked as explanatory text outside the code.

---

#### documentation_inconsistency

**Description:** END documentation contains contradictory information about continuation with CONT. First states 'Can be continued with CONT (execution resumes at next statement after END)' but later states 'Both END and STOP allow continuation with CONT, but END closes files first.'

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/end.md`

**Details:**
Section 'Difference from STOP' lists:
'END:
- Can be continued with CONT (execution resumes at next statement after END)'

But then states:
'Both END and STOP allow continuation with CONT, but END closes files first.'

This is contradictory because if END closes files, continuing execution after END would leave those files closed, which may not be the intended behavior.

---

#### documentation_inconsistency

**Description:** FIELD documentation warns not to use FIELDed variables in INPUT or LET statements, but GET documentation doesn't mention this important restriction when discussing reading data.

**Affected files:**
- `docs/help/common/language/statements/field.md`
- `docs/help/common/language/statements/get.md`

**Details:**
field.md: 'Note: Do not use a FIELDed variable name in an INPUT or LET statement. Once a variable name is FIELDed, it points to the correct place in the random file buffer. If a subsequent INPUT or LET statement with that variable name is executed, the variable's pointer is moved to string space.'

get.md has no mention of this restriction in its remarks or notes.

---

#### documentation_inconsistency

**Description:** Both INPUT and LINE INPUT mention semicolon behavior for suppressing carriage return, but the syntax descriptions differ slightly in how this is presented.

**Affected files:**
- `docs/help/common/language/statements/input.md`
- `docs/help/common/language/statements/line-input.md`

**Details:**
input.md syntax: 'INPUT[:] [<"prompt string">:]<list of variables>'
input.md remarks: 'A semicolon immediately after INPUT suppresses the carriage return/line feed after the user presses Enter'

line-input.md syntax: 'LINE INPUT [;"prompt string";]<string variable>'
line-input.md remarks: 'If LINE INPUT is immediately followed by a semicolon (before the prompt string), then the carriage return typed by the user to end the input line does not echo a carriage return/line feed sequence'

The syntax uses [:] vs [;] notation inconsistently.

---

#### documentation_inconsistency

**Description:** LIST documentation has incomplete remarks section - it's empty between Purpose and Example.

**Affected files:**
- `docs/help/common/language/statements/list.md`

**Details:**
list.md shows:
'## Remarks


## Example'

The Remarks section is completely empty, which is unusual for a command documentation.

---

#### documentation_inconsistency

**Description:** Index.md lists 'Modern Extensions (MBASIC only)' but includes LIMITS which is also listed separately in the alphabetical listing without the MBASIC extension note.

**Affected files:**
- `docs/help/common/language/statements/index.md`

**Details:**
Index shows LIMITS in both:
1. Alphabetical listing under 'L' without extension note
2. 'Modern Extensions (MBASIC only)' category

This dual listing could be confusing about whether LIMITS is a standard or extension feature.

---

#### documentation_inconsistency

**Description:** Both LLIST and LPRINT have implementation notes stating they're not implemented, but the notes have slightly different wording and alternative suggestions.

**Affected files:**
- `docs/help/common/language/statements/llist.md`
- `docs/help/common/language/statements/lprint-lprint-using.md`

**Details:**
llist.md: 'Alternative: Use LIST to display program to console or redirect console output to a file for printing'

lprint-lprint-using.md: 'Alternative: Use PRINT to output to console or PRINT# to output to a file, then print the file using your operating system's print facilities.'

Both should probably mention the same alternatives consistently.

---

#### documentation_inconsistency

**Description:** GOSUB-RETURN uses 'aliases' field in frontmatter while IF-THEN-ELSE uses it too, but other similar multi-name commands don't use this field consistently.

**Affected files:**
- `docs/help/common/language/statements/gosub-return.md`
- `docs/help/common/language/statements/if-then-else-if-goto.md`

**Details:**
gosub-return.md: 'aliases: ['gosub-return']'
if-then-else-if-goto.md: 'aliases: ['if-then', 'if-goto', 'if-then-else']'

But for-next.md doesn't have aliases field even though it's also a multi-keyword statement.

---

#### documentation_inconsistency

**Description:** LSET and RSET documentation have inconsistent 'Notes' sections with different wording for essentially the same information

**Affected files:**
- `docs/help/common/language/statements/lset.md`
- `docs/help/common/language/statements/rset.md`

**Details:**
LSET Notes:
- LSET does not write to the file - use PUT to write the record
- The string variable should be a field variable defined with FIELD
- Trailing spaces are added for padding, leading spaces are not

RSET Notes:
- RSET does not write to the file - use PUT to write the record
- The string variable should be a field variable defined with FIELD
- Leading spaces are added for padding, trailing spaces are not

The third bullet point describes opposite behavior (which is correct), but the first two bullets are identical. For consistency, both should have parallel structure.

---

#### documentation_inconsistency

**Description:** Inconsistent formatting in 'See Also' sections - some use full descriptions, others don't

**Affected files:**
- `docs/help/common/language/statements/merge.md`
- `docs/help/common/language/statements/name.md`
- `docs/help/common/language/statements/new.md`

**Details:**
merge.md See Also entries include full descriptions:
- [KILL](kill.md) - To delete a file from disk
- [LOAD](load.md) - To load a file from disk into memory

name.md See Also entries include full descriptions:
- [KILL](kill.md) - To delete a file from disk

new.md See Also entries include full descriptions:
- [CHAIN](chain.md) - To call a program and pass variables to it from the current program

But other files like mid-assignment.md use different format:
- [ASC](../functions/asc.md) - Returns a numerical value that is the ASCII code...

Inconsistent style across documentation files.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of 'BASIC-80' vs 'BASIC' in documentation

**Affected files:**
- `docs/help/common/language/statements/on-error-goto.md`

**Details:**
The on-error-goto.md file uses both 'BASIC-80' and 'BASIC' to refer to the same system:
- 'all errors detected, including direct mode errors (e.g., Syntax errors), will cause a jump to the specified error handling subroutine'
- 'An ON ERROR GOTO 0 statement that appears in an error trapping subroutine causes BASIC-80 to stop'
- 'the BASIC error message is printed'

Some files consistently use 'BASIC-80' while others use 'BASIC'. Should be standardized.

---

#### documentation_inconsistency

**Description:** OPEN documentation has incomplete mode descriptions in Remarks

**Affected files:**
- `docs/help/common/language/statements/open.md`

**Details:**
The Remarks section lists three modes:
- 'O' - specifies sequential output mode
- 'I' - specifies sequential input mode
- 'R' - specifies random input/output mode

However, the text later mentions 'append (mode "A")' in the PRINT# documentation (printi-printi-using.md), but mode 'A' is not documented in the OPEN statement's mode list. This is an incomplete reference.

---

#### documentation_inconsistency

**Description:** OUT and POKE have different implementation note formats despite both being unimplemented hardware features

**Affected files:**
- `docs/help/common/language/statements/out.md`
- `docs/help/common/language/statements/poke.md`

**Details:**
OUT uses:
'⚠️ **Not Implemented**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.
**Behavior**: Statement is parsed but no operation is performed'

POKE uses:
'⚠️ **Emulated as No-Op**: This feature requires direct memory access and cannot be implemented in a Python-based interpreter.
**Behavior**: Statement is parsed and executes successfully, but performs no operation'

Both describe essentially the same behavior (parsed but no-op) but use different terminology ('Not Implemented' vs 'Emulated as No-Op'). Should be consistent.

---

#### documentation_inconsistency

**Description:** PRINT documentation has formatting inconsistency in example output

**Affected files:**
- `docs/help/common/language/statements/print.md`

**Details:**
The example shows:
```basic
10 PRINT "Hello, World!"
20 PRINT "The answer is"; 42
...
```

Output:
```
Hello, World!
The answer is 42
```

But earlier in Remarks it states 'Numbers are printed with: A leading space for positive numbers (where minus sign would go)... A trailing space'

So the output should actually be:
'The answer is 42 ' (with leading and trailing spaces around 42)

The example output doesn't match the documented behavior.

---

#### documentation_inconsistency

**Description:** RANDOMIZE example has inconsistent spacing in output

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
The example output shows:
'Random Number Seed (-32768 to 32767)? 3     (user types 3)'

The spacing and formatting is inconsistent with other documentation examples. Most examples don't include '(user types X)' annotations inline with the output. This should either:
1. Use consistent comment style: '? 3  REM user types 3'
2. Or separate user input from output more clearly

---

#### documentation_inconsistency

**Description:** READ documentation states 'Variables in the list may be subscripted' but doesn't show an example

**Affected files:**
- `docs/help/common/language/statements/read.md`

**Details:**
The Remarks section mentions:
'Variables in the list may be subscripted. Array elements must be dimensioned before being referenced in a READ statement.'

But the Example section only shows simple variables (ID, NAME$, SCORE). An example with array subscripts would be helpful:
'30 READ A(1), A(2), A(3)'

Other documentation files typically provide examples for all mentioned features.

---

#### documentation_inconsistency

**Description:** REM documentation example has inconsistent line numbering

**Affected files:**
- `docs/help/common/language/statements/rem.md`

**Details:**
The example shows:
'120 REM CALCULATE AVERAGE VELOCITY
130 FOR I=1 TO 20
140 SUM=SUM + V(I)'

Then shows an alternative:
'120 FOR I=1 TO 20     'CALCULATE AVERAGE VELOCITY
130 SUM=SUM+V(I)
140 NEXT I'

The second version has different line numbers (130 vs 140 for SUM=SUM+V(I)) and adds 'NEXT I' which wasn't in the first version. This makes it confusing as they're supposed to be equivalent examples.

---

#### documentation_inconsistency

**Description:** RESUME documentation includes 'Testing RESUME' section that references 'real MBASIC 5.21' which is meta-documentation

**Affected files:**
- `docs/help/common/language/statements/resume.md`

**Details:**
The documentation includes:
'## Testing RESUME

Verified behavior against real MBASIC 5.21:
- ✅ RESUME retries error line
- ✅ RESUME NEXT skips to next statement
...'

This is meta-documentation about testing the implementation, not user-facing documentation. It should either be:
1. Removed from user documentation
2. Moved to a developer/implementation notes section
3. Reworded to be user-facing ('RESUME behavior:')

---

#### documentation_inconsistency

**Description:** RUN documentation has inconsistent hyphenation of 'line number' vs 'line-number'

**Affected files:**
- `docs/help/common/language/statements/run.md`

**Details:**
The documentation uses both forms:
- 'RUN [line number]' (in syntax)
- 'RUN line-number' (in remarks: 'Executes the current program starting at the specified line number')

Should be consistent throughout. Most other documentation uses 'line number' (two words) in prose and '<line number>' in syntax.

---

#### documentation_inconsistency

**Description:** SHOWSETTINGS syntax inconsistency - optional pattern parameter formatting differs

**Affected files:**
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
showsettings.md shows syntax as 'SHOWSETTINGS ["pattern"]' with brackets indicating optional, but settings.md examples show 'SHOWSETTINGS' and 'SHOWSETTINGS "display"' without explaining the bracket notation.

---

#### documentation_inconsistency

**Description:** WRITE vs WRITE# documentation has inconsistent cross-references

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md (screen) has 'See Also' pointing to writei.md (file) with description 'Write data to a sequential file (file output variant)', but writei.md points back with 'Write data to terminal (terminal output variant)' - the relationship could be clearer.

---

#### documentation_inconsistency

**Description:** Keyboard shortcuts documentation duplicated with potential inconsistencies

**Affected files:**
- `docs/help/common/shortcuts.md`
- `docs/help/common/ui/curses/editing.md`

**Details:**
shortcuts.md lists '^R - Run program' and curses/editing.md also mentions 'Ctrl+R - Run program'. If these are UI-specific, the common shortcuts.md should clarify which UI it applies to.

---

#### documentation_inconsistency

**Description:** SWAP version information unclear

**Affected files:**
- `docs/help/common/language/statements/swap.md`

**Details:**
swap.md states '**Versions:** EXtended, Disk' - unclear what 'EXtended' means and how it differs from 'Disk'. Other docs use 'Disk' or 'MBASIC Extension' but not 'EXtended'.

---

#### documentation_inconsistency

**Description:** TRON-TROFF example formatting inconsistent

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
The example shows 'TRON\n             Ok\n             LIST' with unusual spacing/indentation that doesn't match other examples in the documentation. Unclear if this is intentional or a formatting error.

---

#### documentation_inconsistency

**Description:** SAVE example comment syntax inconsistent

**Affected files:**
- `docs/help/common/language/statements/save.md`

**Details:**
save.md example shows 'SAVE "MYPROGRAM.BAS", A  ' Save in ASCII format' with inline comment using apostrophe, but BASIC typically requires REM or ' at start of comment, not inline after code.

---

#### documentation_inconsistency

**Description:** Different counts of optimizations in semantic analyzer

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/features.md`

**Details:**
architecture.md states: 'The semantic analyzer implements 18 distinct optimizations' and lists all 18 numbered optimizations (1-18).

features.md states: 'The interpreter includes an advanced semantic analyzer with 18 optimizations' and also lists 18 numbered items (1-18).

Both documents agree on 18 optimizations and list the same ones. This is actually consistent, not an inconsistency.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for interpreter mode

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/features.md`

**Details:**
architecture.md uses the heading 'Interpreter Mode (Current Implementation)' and describes it as the current implementation.

features.md uses the heading 'Compiler Features' with subheading 'Semantic Analyzer' and states 'The interpreter includes an advanced semantic analyzer'.

This mixing of 'interpreter' and 'compiler' terminology when describing the same system could be confusing. The architecture.md makes it clear that semantic analyzer is for future compilation, but features.md presents it as part of 'Compiler Features' while also saying 'the interpreter includes' it.

---

#### documentation_inconsistency

**Description:** Installation instructions reference non-existent script name

**Affected files:**
- `docs/help/mbasic/getting-started.md`

**Details:**
getting-started.md shows installation with:

'# Run MBASIC
mbasic'

But earlier shows cloning from 'https://github.com/avwohl/mbasic.git' and doesn't explain how 'mbasic' command becomes available. The instructions don't mention installing the package or creating a symlink, yet show running 'mbasic' directly.

Later examples show 'mbasic --ui cli' and 'mbasic --ui tk' but never explain how to make the 'mbasic' command available in PATH.

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

**Description:** Find/Replace availability inconsistency

**Affected files:**
- `docs/help/ui/cli/find-replace.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/find-replace.md states 'The CLI backend does not have built-in Find/Replace commands' and recommends Tk UI. feature-reference.md states 'Find/Replace (Not yet implemented)' for Curses UI. Both lack the feature but use different terminology ('does not have' vs 'not yet implemented'), suggesting different future plans.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for unimplemented features

**Affected files:**
- `docs/help/mbasic/not-implemented.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
not-implemented.md uses 'Not in MBASIC 5.21' and 'Why not implemented' sections to explain missing features from other BASIC dialects. feature-reference.md uses '(Not implemented)' and '(Not yet implemented)' for UI features. The distinction between 'not implemented' (never will be) vs 'not yet implemented' (planned) is inconsistent.

---

#### documentation_inconsistency

**Description:** Inconsistent navigation structure between index pages

**Affected files:**
- `docs/help/mbasic/index.md`
- `docs/help/ui/cli/index.md`

**Details:**
mbasic/index.md uses emoji icons (📗📕📘) to categorize documentation tiers, while cli/index.md uses the same emojis but in a different organizational structure. The emoji usage is inconsistent - mbasic uses them for implementation/language/UI distinction, cli uses them for CLI/MBASIC/Language distinction.

---

#### documentation_inconsistency

**Description:** Debugging command availability differs between UIs

**Affected files:**
- `docs/help/ui/cli/debugging.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/debugging.md documents BREAK, STEP, and STACK as text commands. feature-reference.md shows Ctrl+B for breakpoints, Ctrl+T for step statement, Ctrl+K for step line, and menu-only for execution stack. The fundamental difference in debugging interfaces (command-based vs keyboard-based) is not explained in a comparison document.

---

#### documentation_inconsistency

**Description:** Missing documentation for List program feature

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/running.md`

**Details:**
quick-reference.md shows: '**Menu only** | List program' under Program Management

running.md mentions: 'Access through the menu bar to list the program to the output window.'

But neither document explains what 'List program' does in detail, or provides the menu path to access it. The feature is mentioned but not fully documented.

---

#### documentation_inconsistency

**Description:** Inconsistent command line syntax for starting GUI

**Affected files:**
- `docs/help/ui/tk/index.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
index.md shows: 'mbasic --ui tk [filename.bas]'

getting-started.md shows:
'```bash
mbasic --ui tk [filename.bas]
```
Or to use the default curses UI:
```bash
mbasic [filename.bas]
```'

But the index.md for curses (docs/help/ui/curses/index.md) doesn't mention that curses is the default UI. This should be clarified consistently across all UI documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent information about command line loading behavior

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
files.md states:
'You can also load a program when starting:
```bash
python3 mbasic --ui curses myprogram.bas
```
The program will:
- Load into the editor
- Automatically run
- Then enter interactive mode'

But getting-started.md shows:
'```bash
mbasic --ui curses
```'

The files.md suggests programs auto-run when loaded from command line, but this behavior is not mentioned in getting-started.md or confirmed elsewhere. This needs verification.

---

#### documentation_inconsistency

**Description:** Inconsistent help search documentation

**Affected files:**
- `docs/help/ui/curses/help-navigation.md`
- `docs/help/ui/curses/index.md`

**Details:**
help-navigation.md states:
'| **/** | Open search prompt |'

index.md states:
'Press **/** to search across all help content.'

But help-navigation.md provides more detail:
'**Search tips:**
- Search across all three documentation tiers
- Try keywords like "loop", "array", "file"
- Try statement names like "print", "for", "if"
- Try function names like "left$", "abs", "int"
- Results show tier markers: 📕 Language, 📗 MBASIC, 📘 UI'

The index.md should mention the three-tier search capability for completeness.

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

The first section mentions .TXT and ASCII text as input formats, but the second section only mentions .BAS files. This should be consistent.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of menu items

**Affected files:**
- `docs/help/ui/web/getting-started.md`

**Details:**
web/getting-started.md uses inconsistent capitalization for menu items:

'File → Recent Files' (capital F in Files)
'Run → Run Program' (capital P in Program)
'Run → Show Variables' (capital V in Variables)
'Run → Show Stack' (capital S in Stack)
'Run → Clear Output' (capital O in Output)
'Run → List Program' (capital P in Program)

But also:
'File → Open' (lowercase 'pen' implied)
'File → Save' (lowercase 'ave' implied)

Menu item names should have consistent capitalization throughout the documentation.

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

**Description:** Inconsistent keyboard shortcut for Help

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+?' for help in Tk UI, but keyboard-shortcuts.md (for Curses UI) lists '^F' for help. The UI_FEATURE_COMPARISON.md shows 'Ctrl+H/F1' for Curses and 'Ctrl+?' for Tk. There's inconsistency in whether Tk supports F1 or only Ctrl+?.

---

#### documentation_inconsistency

**Description:** Inconsistent Save keyboard shortcut documentation

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+S' for Save in Tk UI. keyboard-shortcuts.md (Curses UI) lists 'Ctrl+V' for Save program and 'Shift+Ctrl+V' for Save As. This is a UI difference, but could be confusing since Ctrl+V is typically Paste in most applications.

---

#### documentation_inconsistency

**Description:** Inconsistent feature status for Find/Replace

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md shows Find/Replace as '✅' (fully implemented) for Tk but '⚠️' (planned) for Web. However, in the 'Recently Added (2025-10-29)' section, it lists '✅ Tk: Find/Replace functionality' as recently added, which is consistent. But the Web status shows '⚠️ Tk: planned/optional, Web: automatic' for Auto-save, not Find/Replace. The table entry for Find/Replace Web shows '⚠️' with note 'Tk: implemented, Web: planned' which is consistent.

---

#### documentation_inconsistency

**Description:** Inconsistent line number increment documentation

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md in the 'Smart Insert Workflow' section shows an example where 'A blank line 15 is automatically inserted!' between lines 10 and 20. However, in 'Example 3: At End of Program', it states 'A blank line 40 is inserted (using standard increment of 10)' after line 30. The increment logic isn't clearly explained - is it midpoint calculation or standard increment?

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for line endings

**Affected files:**
- `docs/user/sequential-files.md`

**Details:**
sequential-files.md uses both 'line ending' and 'line endings' inconsistently. Also uses 'ending' vs 'endings' in different contexts. While not technically wrong, consistency would improve readability.

---

#### documentation_inconsistency

**Description:** Inconsistent status emoji usage

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md uses '🔧 PLANNED' for some features but the status line at the top uses text 'Status: The settings system is FULLY IMPLEMENTED'. The emoji usage is inconsistent - some sections use emoji (🔧) while the header uses text only.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in case conflict scenarios

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md shows examples with different comment styles. Some use 'REM' statements, others use apostrophe comments. While both are valid, consistency within the same document section would be clearer.

---


## Summary

- Total issues found: 658
- Code/Comment conflicts: 208
- Other inconsistencies: 450
