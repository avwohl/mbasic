# Enhanced Consistency Report (Code + Documentation)

Generated: 2025-11-06 02:53:58
Analyzed: Source code (.py, .json) and Documentation (.md)

## 🔧 Code vs Comment Conflicts


## 📋 General Inconsistencies

### 🔴 High Severity

#### documentation_inconsistency

**Description:** Contradictory documentation about ProgramManager file I/O methods and their relationship to FileIO abstraction

**Affected files:**
- `src/editing/manager.py`
- `src/file_io.py`

**Details:**
src/editing/manager.py docstring states:
"Note: ProgramManager.load_from_file() returns (success, lines) tuple for direct UI integration, while FileIO.load_file() returns raw file text. These serve different purposes: ProgramManager integrates with the editor, FileIO provides raw file content for the LOAD command to parse."

However, ProgramManager.load_from_file() actually returns (success, errors) where errors is List[Tuple[int, str]], NOT a lines tuple. The actual implementation:
"Returns:
    Tuple of (success, errors)
    success: True if at least one line loaded successfully
    errors: List of (line_number, error_message) for failed lines"

---

#### code_vs_comment

**Description:** Comment describes validation behavior that doesn't exist in the code

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Lines 157-165 comment states:
'# This feature requires the following UI integration:
# - interpreter.interactive_mode must reference the UI object (checked with hasattr)
# - UI.program must have add_line() and delete_line() methods (validated, errors if missing)
# - UI._refresh_editor() method to update the display (optional, checked with hasattr)
# - UI._highlight_current_statement() for restoring execution highlighting (optional, checked with hasattr)
# If interactive_mode doesn't exist, line editing silently continues without UI update.
# If interactive_mode exists but required program methods are missing, returns error message.'

However, the actual code (lines 175-182) validates UI.program and its methods:
'if not hasattr(ui, 'program') or not ui.program:
    return (False, "Cannot edit program lines: UI program manager not available\n")
if line_content and not hasattr(ui.program, 'add_line'):
    return (False, "Cannot edit program lines: add_line method not available\n")
if not line_content and not hasattr(ui.program, 'delete_line'):
    return (False, "Cannot edit program lines: delete_line method not available\n")'

The comment says 'If interactive_mode doesn't exist, line editing silently continues without UI update', but the code at line 219 returns an error: 'return (False, "Cannot edit program lines in this mode\n")' when interactive_mode doesn't exist.

---

#### code_vs_comment

**Description:** RENUM documentation claims conservative behavior for ERL expressions but implementation may incorrectly renumber arithmetic operations

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring at line ~862 states:
'Conservative behavior: ERL expressions with ANY binary operators (ERL+100, ERL*2, ERL=100)
have all right-hand numbers conservatively renumbered, even for arithmetic operations.
This is intentionally broader than the MBASIC manual (which only specifies comparison
operators) to avoid missing line references.'

But then at line ~952 the comment says:
'Known limitation: Arithmetic like "IF ERL+100 THEN..." will incorrectly renumber
the 100 if it happens to be an old line number. This is rare in practice.'

The docstring calls this 'conservative' and 'intentional', while the implementation comment calls it a 'known limitation' and 'incorrect'. These are contradictory characterizations of the same behavior.

---

#### code_vs_comment

**Description:** Comment about error_info being set before _invoke_error_handler contradicts the actual flow

**Affected files:**
- `src/interpreter.py`

**Details:**
In _invoke_error_handler, the comment says:
"Note: error_info is set by the exception handler in tick_pc() that caught
the error before calling this method. We're now ready to invoke the error handler."

But in tick_pc(), the code shows:
```python
except Exception as e:
    # Check if we're already in an error handler (prevent recursive errors)
    already_in_error_handler = (self.state.error_info is not None)

    # Set ErrorInfo for both handler and no-handler cases (needed by RESUME)
    error_code = self._map_exception_to_error_code(e)
    self.state.error_info = ErrorInfo(
        error_code=error_code,
        pc=pc,
        error_message=str(e)
    )

    # Check if we have an error handler and not already handling an error
    if self.runtime.has_error_handler() and not already_in_error_handler:
        self._invoke_error_handler(error_code, pc)
```

The comment in _invoke_error_handler is correct - error_info IS set before calling _invoke_error_handler. However, the comment could be clearer that error_info is set in the same exception handler block, not by a separate handler.

---

#### code_vs_comment

**Description:** Comment in execute_clear says 'bare except: pass below' but there is no bare except in the code - it uses 'except:' which catches all exceptions

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: 'Note: Errors during file close are silently ignored (bare except: pass below)'

Code shows:
try:
    file_obj = self.runtime.files[file_num]
    if hasattr(file_obj, 'close'):
        file_obj.close()
except:
    pass

The comment says 'bare except: pass below' suggesting the except block is elsewhere, but it's right there in the same code block. The comment is misleading about location.

---

#### code_vs_comment

**Description:** Comment in execute_cont describes behavior distinction but the actual check doesn't verify the distinction works as described

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: "Behavior distinction (MBASIC 5.21 compatibility):
- STOP statement: Sets both runtime.stopped=True AND runtime.halted=True
  The stopped flag allows CONT to resume from the saved position
- Break (Ctrl+C): Sets runtime.halted=True but NOT stopped=True, so CONT fails
This is intentional: CONT only works after STOP, not after Break interruption."

The code checks: if not self.runtime.stopped: raise RuntimeError("Can't continue - no program stopped")

However, there's no verification in this file that execute_stop actually sets both flags, or that Break only sets halted. The comment describes a contract but we can't verify it's implemented correctly from this file alone.

---

#### code_vs_comment

**Description:** Comment describes behavior that contradicts the actual implementation for INPUT semicolon handling

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() method:
Comment says: "INPUT "Name"; X  displays 'Name? ' (semicolon AFTER prompt shows '?')"
Comment says: "INPUT "Name", X  displays 'Name ' (comma AFTER prompt suppresses '?')"
Comment says: "INPUT; (semicolon IMMEDIATELY after INPUT keyword, no prompt) suppresses the default '?' prompt entirely (tracked by suppress_question flag above)."

However, the code only sets suppress_question when semicolon is IMMEDIATELY after INPUT:
if self.match(TokenType.SEMICOLON):
    suppress_question = True
    self.advance()

The code does NOT track whether semicolon or comma appears AFTER the prompt. It only consumes the separator:
if self.match(TokenType.SEMICOLON):
    self.advance()
elif self.match(TokenType.COMMA):
    self.advance()

The comment describes MBASIC 5.21 behavior where the separator after prompt affects '?' display, but the parser doesn't capture this information in the AST node.

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

**Description:** Comment about main widget storage contradicts between methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_help() at line ~850: 'Main widget retrieval: Use self.main_widget for consistency with _show_keymap and _show_settings (not self.loop.widget which might be a menu or other overlay at this moment)'

But in _activate_menu() at line ~920: 'Main widget storage: Extract base widget from current loop.widget. This unwraps any existing overlay to get the actual main UI. This is different from _show_keymap/_show_settings which use self.main_widget directly.'

These comments describe opposite approaches - _show_help says it uses self.main_widget like the others, but _activate_menu says it extracts from loop.widget which is different from the others.

---

#### code_vs_comment

**Description:** Comment about RUN behavior contradicts actual implementation regarding start_line parameter

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program() at line ~1075:
Comment says: "# Reset runtime with current program - RUN = CLEAR + GOTO first line (or start_line if specified)"

But later at line ~1100:
"# If start_line is specified (e.g., RUN 100), set PC to that line
# This must happen AFTER interpreter.start() because start() calls setup()
# which resets PC to the first line in the program. By setting PC here,
# we override that default and begin execution at the requested line."

The first comment suggests RUN with start_line is a simple operation, but the second comment reveals it's actually a workaround where we let the interpreter reset to the first line, then override it. This is a significant implementation detail that contradicts the simplified description.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate claims it syncs program to runtime but doesn't reset PC, yet the code shows _sync_program_to_runtime is called which may reset PC depending on implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says:
"# Sync program to runtime (but don't reset PC - keep current execution state)
# This allows LIST to work, but doesn't start execution
self._sync_program_to_runtime()"

The comment claims PC is not reset, but without seeing _sync_program_to_runtime implementation, we cannot verify this. The comment also contradicts itself by saying 'keep current execution state' while also noting that later code checks 'if self.runtime.npc is not None' and moves npc to pc, which IS modifying execution state.

---

#### code_vs_comment

**Description:** Comment claims interpreter.start() is not called to preserve PC, but then describes that immediate executor already called interpreter.start(start_line=120), which contradicts the preservation claim

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in _execute_immediate:
"# NOTE: Don't call interpreter.start() because it resets PC!
# If the immediate command was 'RUN 120', the immediate executor has already
# set PC to line 120 via interpreter.start(start_line=120), so we need to
# preserve that PC value and not reset it."

This is contradictory: it says don't call interpreter.start() because it resets PC, but then says the immediate executor already called interpreter.start(start_line=120). If interpreter.start() was already called, the PC was already set/reset. The logic is unclear about what state is being preserved.

---

#### code_vs_comment_conflict

**Description:** Comment claims help navigation keys are hardcoded and not loaded from keybindings, but HelpMacros class does load keybindings from JSON

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment in help_widget.py lines 66-70 states:
"Note: Help navigation keys are hardcoded here and in keypress() method.
While HelpMacros loads keybindings for {{kbd:action}} macro expansion in help content,
the help widget's own navigation keys (U for back, / for search, etc.) are hardcoded
separately and not loaded from keybindings. If these change, update here and keypress()."

However, HelpMacros.__init__() in help_macros.py line 24 calls self._load_keybindings() which loads from JSON:
"keybindings_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json""

The comment suggests HelpMacros only loads keybindings for macro expansion, but the class has full access to keybindings. The help widget navigation keys (U, /, ESC, Q, Tab, Enter) are indeed hardcoded in keypress() method rather than using the loaded keybindings.

---

#### code_vs_comment

**Description:** Variable window heading initialization doesn't match default sort column

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _create_variables_window() around line ~730:
tree.heading('#0', text='↓ Variable (Last Accessed)')

This sets the heading to show 'Last Accessed' with a down arrow, which should correspond to sort column 'accessed' with reverse=True.

However, the __init__ method sets:
self.variables_sort_column = 'accessed'
self.variables_sort_reverse = True

The heading text '↓ Variable (Last Accessed)' matches this default, but the comment at line ~728 says:
"# Set initial heading text with arrows (matches self.variables_sort_column default: 'accessed')"

This is actually consistent, not an inconsistency. However, there's a potential issue: if the default sort column or direction changes in __init__, the heading text in _create_variables_window() must be manually updated to match. This tight coupling could lead to inconsistencies.

---

#### code_vs_comment

**Description:** Comment about OPTION BASE behavior conflicts with code implementation for invalid values

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~380, comment states:
"# If no default subscripts, use first element based on array_base
# (OPTION BASE 0 uses zeros, OPTION BASE 1 uses ones, invalid values fallback to zeros)"

Then the code implements:
"if array_base == 0:
    # OPTION BASE 0: use all zeros
    default_subscripts = ','.join(['0'] * len(dimensions))
elif array_base == 1:
    # OPTION BASE 1: use all ones
    default_subscripts = ','.join(['1'] * len(dimensions))
else:
    # Invalid array_base (not 0 or 1) - fallback to 0
    default_subscripts = ','.join(['0'] * len(dimensions))"

This is correct, but the comment says "invalid values fallback to zeros" while BASIC standards typically only allow 0 or 1 for OPTION BASE. The code should validate array_base earlier or this comment should clarify that invalid values are a defensive programming measure, not an expected case.

---

#### code_vs_comment

**Description:** Comment in cmd_cont says stop_line and stop_stmt_index are optional extensions, but code uses them without checking if they exist

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1730 says:
# NOTE: This is a simplified implementation. The runtime.stop_line and
# runtime.stop_stmt_index attributes are optional extensions for better
# state restoration. If not present, execution continues from the current
# PC position maintained by the interpreter.

But code at line ~1750 uses:
if hasattr(self.runtime, 'stop_line') and hasattr(self.runtime, 'stop_stmt_index'):
    self.runtime.current_line = self.runtime.stop_line
    self.runtime.current_stmt_index = self.runtime.stop_stmt_index

The code correctly checks with hasattr(), but then assigns to current_line and current_stmt_index without checking if THOSE attributes exist. If stop_line/stop_stmt_index are optional, current_line/current_stmt_index might also not exist, causing AttributeError.

---

#### code_vs_comment

**Description:** Comment says 'Don't call interpreter.start()' but then manually replicates part of what start() would do

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment states: "NOTE: Don't call interpreter.start() because it resets PC! RUN 120 already set PC to line 120, so just clear halted flag"

But then the code does:
- self.runtime.halted = False
- self.interpreter.state.is_first_line = True

This is manually replicating initialization logic that might be in start(). If start() does more than just reset PC and set these flags, this could lead to incomplete initialization. The comment should clarify what other initialization start() does and why it's safe to skip it.

---

#### code_vs_comment

**Description:** serialize_statement() has a dangerous fallback that creates REM comments for unhandled statement types, with a warning that this could break RENUM

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Code:
else:
    # Fallback for unhandled statement types: return a placeholder REM comment.
    # WARNING: This could create invalid BASIC code during RENUM if new statement
    # types are added but not handled here. Ensure all statement types are supported.
    return f"REM {stmt_type}"

This is a code bug waiting to happen. If a new statement type is added to the parser but not to serialize_statement(), RENUM will silently corrupt the program by converting statements to comments. This should raise an exception instead.

---

#### code_vs_comment

**Description:** Comment about INPUT handling contradicts actual implementation location

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~1770, comment states:
"# INPUT handling: When INPUT statement executes, the immediate_entry input box
# is focused for user input (see _execute_tick() lines ~1886-1888)."

However, the actual INPUT handling in _execute_tick() is at lines ~1875-1890 and ~1906-1918, not at lines 1886-1888. The line numbers in the comment are incorrect.

---

#### code_vs_comment

**Description:** Comment claims _get_input provides input via TWO mechanisms, but the mechanisms may not both be active

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment in _handle_output_enter states: 'Provide input to interpreter via TWO mechanisms (both may be needed depending on code path): 1. interpreter.provide_input() - Used when interpreter is waiting synchronously... 2. input_future.set_result() - Used when async code is waiting via asyncio.Future... Only one path is active at a time, but we attempt both to ensure the waiting code receives input regardless of which path it used.'

This is contradictory: it says 'both may be needed' but then says 'only one path is active at a time'. If only one is active, attempting both could cause issues (e.g., setting a result on a Future that's not being awaited, or providing input when not in input_prompt state).

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

**Description:** Error code documentation mentions 'Input past end' error (code 62) but EOF function documentation uses different wording

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`
- `docs/help/common/language/functions/eof.md`

**Details:**
error-codes.md states:
"62 | Input past end | An INPUT statement is executed after all data in the file has been read, or for an empty file. Use EOF to detect end of file."

eof.md states:
"Use EOF to test for end-of-file while INPUTting, to avoid 'Input past end' errors."

The error message is quoted in eof.md but the actual error code table shows it without quotes. This is consistent, but the cross-reference could be clearer.

---

#### documentation_inconsistency

**Description:** CLOAD and CSAVE marked as 'NOT INCLUDED IN THE DEC VT180 VERSION' but version applicability unclear

**Affected files:**
- `docs/help/common/language/statements/cload.md`
- `docs/help/common/language/statements/csave.md`

**Details:**
Both CLOAD and CSAVE have titles stating 'THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION' but the documentation shows 'Versions: 8K (cassette), Extended (cassette)'. This creates confusion about whether these commands are available in the documented MBASIC 5.21 implementation. The documentation should clarify if these are implemented in this Python-based interpreter or not.

---

#### documentation_inconsistency

**Description:** Conflicting information about compiler implementation status

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/features.md`

**Details:**
architecture.md states: 'Current Implementation: ✅ Interpreter (fully functional)' and 'Semantic Analyzer: ✅ Complete (18 optimizations)' and 'Code Generation: ❌ Not implemented (future work)'

features.md states under 'Compiler Features > Semantic Analyzer': 'The interpreter includes an advanced semantic analyzer with 18 optimizations' and lists all 18 optimizations as if they are active features.

This creates confusion about whether the semantic analyzer is actually used during program execution or is just available for analysis. The architecture.md suggests it's for 'future compilation' while features.md presents it as an active interpreter feature.

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

But quick-reference.md shows: '**^V** | Save program (^S unavailable - terminal flow control)'

Both agree ^V is for save, but files.md also mentions in 'Loading from Command Line' section: 'python3 mbasic --ui curses myprogram.bas' while getting-started.md uses just 'mbasic --ui curses'. Inconsistent command format.

---

#### documentation_inconsistency

**Description:** Missing 'List program' keyboard shortcut in running.md

**Affected files:**
- `docs/help/ui/curses/running.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
running.md section 'Listing Programs' states: 'Access through the menu bar to list the program to the output window.'

But quick-reference.md shows: '**Menu only** | List program' under Program Management section.

running.md implies there's no keyboard shortcut, but doesn't explicitly state this, creating ambiguity.

---

#### documentation_inconsistency

**Description:** Feature availability discrepancy between UIs

**Affected files:**
- `docs/help/ui/curses/find-replace.md`
- `docs/help/ui/tk/features.md`

**Details:**
curses/find-replace.md explicitly states: 'The Curses UI currently **does not have** Find/Replace functionality for the editor. This feature is planned for future implementation.'

tk/features.md documents Find/Replace as a working feature: 'Find and Replace

Find text (Ctrl+F):
- Opens Find dialog with search options...'

This is correct behavior (different UIs have different features), but the curses documentation recommends: 'Use different UI:
- Tk UI has full Find/Replace' which is good cross-referencing.

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

**Description:** Tk UI documentation describes features as if implemented (Ctrl+I Smart Insert, Ctrl+W Variables window, Ctrl+K Stack, Ctrl+E Renumber) but settings.md says entire Tk GUI is 'planned/intended implementation and are not yet available'

**Affected files:**
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/settings.md`

**Details:**
tk/settings.md clearly states at the top:
'**Implementation Status:** The Tk (Tkinter) desktop GUI is planned to provide the most comprehensive settings dialog. **The features described in this document represent planned/intended implementation and are not yet available.** This is a design document for future development.'

But tk/tips.md and tk/workflows.md describe features as if they currently work:

tk/tips.md:
'Use **Ctrl+I** (Smart Insert) to insert blank lines under each section without calculating line numbers!'
'Press **Ctrl+W** (Toggle Stack) while stepping through nested loops'
'Press **Ctrl+E** (Renumber)'

tk/workflows.md:
'Press **Ctrl+I** (Smart Insert) to insert blank line'
'Press **Ctrl+W** to open Variables window'
'Press **Ctrl+E** (Renumber)'

These documents don't have disclaimers that features are planned, creating confusion about implementation status.

---

#### documentation_inconsistency

**Description:** Settings dialog shows tabs that may not exist or are incomplete

**Affected files:**
- `docs/help/ui/web/settings.md`

**Details:**
settings.md describes a 'Limits Tab':
"### Limits Tab

Shows resource limits (view-only in current version).

**Information displayed:**
- Maximum variables
- Maximum string length
- Maximum array dimensions

These limits are for information only and cannot be changed via the UI (they're set in the interpreter configuration)."

However, the ASCII diagram at the top only shows:
"│  📝 Editor    📊 Limits                 │"

This suggests the Limits tab exists but the documentation doesn't clarify if it's actually implemented or just planned. The phrase 'view-only in current version' suggests it exists but is incomplete.

---

#### documentation_inconsistency

**Description:** Contradictory information about Smart Insert availability

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
UI_FEATURE_COMPARISON.md states 'Smart Insert' is 'Tk exclusive feature' (only available in Tk UI). However, TK_UI_QUICK_START.md extensively documents Smart Insert (Ctrl+I) as a Tk feature with multiple examples. The inconsistency is that the feature comparison correctly identifies it as Tk-only, but there's no mention in the comparison about whether this is a planned feature for other UIs or permanently Tk-exclusive.

---

### 🟡 Medium Severity

#### code_vs_comment

**Description:** Fix script claims to modify src/runtime.py but the replacement pattern is incomplete/malformed

**Affected files:**
- `medium_severity_fixes.py`

**Details:**
Fix 6 in medium_severity_fixes.py:
count = fix_file('src/runtime.py', [
    ('_resolve_variable_name() docstring:',
     '_resolve_variable_name() is the standard method for variable resolution.'),
])

This replacement pattern is searching for '_resolve_variable_name() docstring:' which is unlikely to exist as literal text in the source. The pattern appears to be a placeholder or incomplete fix specification rather than actual text to replace.

---

#### code_vs_comment

**Description:** InputStatementNode docstring has confusing explanation of suppress_question field

**Affected files:**
- `src/ast_nodes.py`

**Details:**
The docstring states:
'Note: The suppress_question field indicates whether to suppress the question mark prompt:
- suppress_question=False (default): INPUT var or INPUT "prompt", var → shows "? " or "prompt? "
- suppress_question=True: INPUT; var → suppresses "?" completely (no prompt at all)

Semicolon usage:
- After prompt string: INPUT "prompt"; var → semicolon is just a separator (shows "prompt? ")
- Immediately after INPUT: INPUT; var → semicolon signals suppress_question=True'

This is internally contradictory: it says 'INPUT "prompt"; var' shows 'prompt? ' (with question mark) but also says the semicolon after INPUT signals suppress_question=True. The distinction between 'semicolon after prompt string' vs 'semicolon immediately after INPUT' needs clarification - both examples show semicolons after INPUT.

---

#### code_vs_comment

**Description:** VariableNode type_suffix documentation is complex and potentially confusing

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode has two fields for type handling:
- type_suffix: Optional[str] = None  # $, %, !, # - The actual suffix (see explicit_type_suffix for origin)
- explicit_type_suffix: bool = False  # True if type_suffix was in original source, False if inferred from DEF

The docstring states:
'Type suffix handling:
- type_suffix: The actual suffix character ($, %, !, #)
- explicit_type_suffix: True if suffix appeared in source code, False if inferred from DEF

Example: In "DEFINT A-Z: X=5", variable X has type_suffix="%" and explicit_type_suffix=False.
The suffix must be tracked but not regenerated in source code.'

This design requires careful handling: type_suffix is always set (even for DEF-inferred types) but explicit_type_suffix controls whether it should be displayed. This is correct but complex - code using VariableNode must check explicit_type_suffix before displaying type_suffix. The comment 'must be tracked but not regenerated' is the key insight but could be missed.

---

#### code_vs_comment

**Description:** Comment claims original_negative is captured at line 269, but that line number is incorrect in the actual code

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment at line 274 states:
# original_negative was captured before rounding (line 269 above)
But original_negative is actually captured at line 271, not 269. The comment references an incorrect line number.

---

#### code_vs_comment

**Description:** EOF function comment describes ^Z behavior but implementation details are unclear about when mode 'I' is set

**Affected files:**
- `src/basic_builtins.py`

**Details:**
The EOF function docstring states:
Note: For binary input files (mode 'I' from OPEN statement), respects ^Z (ASCII 26)
as EOF marker (CP/M style). Mode 'I' is set by the OPEN statement for binary input.

However, the code comment at line 738 states:
# Mode 'I' = binary input mode where ^Z checking is appropriate

But there's no code in this file showing how mode 'I' is actually set. The comment assumes the OPEN statement sets this mode, but this file doesn't implement OPEN, creating a documentation gap about the contract between modules.

---

#### code_vs_comment

**Description:** Long comment about identifier case handling contradicts the simple implementation

**Affected files:**
- `src/case_string_handler.py`

**Details:**
Lines 52-59 contain an extensive comment:
# Identifiers always preserve their original case in display.
# Unlike keywords, which can be forced to a specific case policy,
# identifiers (variable/function names) retain their case as typed.
# This matches MBASIC 5.21 behavior where identifiers are case-insensitive
# for matching but preserve display case.
# Note: We return original_text directly without using an identifier_table.
# A future enhancement could track identifiers for conflict detection.

But the code simply does 'return original_text'. The comment mentions 'A future enhancement could track identifiers' but then the code creates an identifier_table in get_identifier_table() that is never used. This suggests incomplete refactoring or the comment is outdated.

---

#### code_vs_comment

**Description:** INPUT function docstring describes # prefix stripping but doesn't show where this happens

**Affected files:**
- `src/basic_builtins.py`

**Details:**
INPUT function docstring states:
Note: The # prefix in BASIC syntax is stripped by the parser before calling this method.

This creates a contract with the parser that isn't documented in the parser file reference. It's unclear if this is actually implemented or just aspirational documentation.

---

#### code_vs_documentation

**Description:** SandboxedFileIO documentation claims it delegates to backend.sandboxed_fs but implementation shows incomplete integration

**Affected files:**
- `src/file_io.py`
- `src/filesystem/sandboxed_fs.py`

**Details:**
src/file_io.py SandboxedFileIO docstring states:
"Acts as an adapter to backend.sandboxed_fs (SandboxedFileSystemProvider from src/filesystem/sandboxed_fs.py), which provides an in-memory virtual filesystem."

But only list_files() is implemented with delegation:
"if hasattr(self.backend, 'sandboxed_fs'):
    pattern = filespec.strip().strip('"').strip("'") if filespec else None
    files = self.backend.sandboxed_fs.list_files(pattern)"

All other methods (load_file, save_file, delete_file, file_exists) raise IOError with "not yet implemented" messages, contradicting the claim that it "acts as an adapter" to the sandboxed filesystem.

---

#### documentation_inconsistency

**Description:** Inconsistent explanation of overlap between FileIO and FileSystemProvider abstractions

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
Both files claim there is "intentional overlap" for list_files() and delete() methods, but provide different justifications:

src/file_io.py states:
"Note: Both abstractions serve different purposes and are used at different times. There is intentional overlap: both provide list_files() and delete() methods. FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for runtime access (though not all BASIC dialects support runtime file listing/deletion)."

src/filesystem/base.py states:
"Note: There is intentional overlap between the two abstractions. Both provide list_files() and delete() methods, but serve different contexts: FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for runtime access (though not all BASIC dialects support runtime file operations)."

The explanations are nearly identical but use different wording ("different times" vs "different contexts", "runtime file listing/deletion" vs "runtime file operations"), suggesting copy-paste documentation that may not have been carefully reviewed for consistency.

---

#### code_vs_documentation

**Description:** ProgramManager.merge_from_file() return type documentation incomplete

**Affected files:**
- `src/editing/manager.py`

**Details:**
The docstring states:
"Returns:
    Tuple of (success, errors, lines_added, lines_replaced)
    success: True if at least one line loaded successfully
    errors: List of (line_number, error_message) for failed lines
    lines_added: Count of new lines added
    lines_replaced: Count of existing lines replaced"

But the implementation shows it returns a 4-tuple in success case and also a 4-tuple in failure case:
"if total_success > 0:
    return (True, errors, lines_added, lines_replaced)
else:
    return (False, errors, 0, 0)"

The documentation doesn't clarify that in the failure case (success=False), lines_added and lines_replaced will always be 0, which could be inferred but isn't explicitly stated.

---

#### code_vs_comment

**Description:** Comment claims INPUT statements are 'blocked when input() is called, not at parse time' but the help text says INPUT 'will fail at runtime'

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Line 154 comment: 'INPUT statement will fail at runtime in immediate mode (blocked when input() is called, not at parse time - use direct assignment instead)'

Help text (line 334): '• INPUT statement will fail at runtime in immediate mode (blocked when input() is called, not at parse time - use direct assignment instead)'

Both say the same thing, but the phrasing 'blocked when input() is called' vs 'will fail at runtime' could be clearer. The implementation in OutputCapturingIOHandler.input() raises RuntimeError, which is 'failing at runtime', not 'blocking'.

---

#### code_vs_comment

**Description:** Comment about PC save/restore contradicts actual behavior

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Line 249 comment states:
'# Note: We do not save/restore the PC before/after execution.
# This allows statements like RUN to change execution position.
# Normal statements (PRINT, LET, etc.) don't modify PC anyway.'

This comment suggests that NOT saving/restoring PC is intentional to allow RUN to work. However, there's no code that ever saved/restored PC in the first place, making this comment potentially misleading. It reads like a justification for removing code that was never there, or it's documenting a design decision that should be more clearly stated as 'We intentionally do not save/restore PC...' rather than 'We do not save/restore...' which implies it was considered and rejected.

---

#### code_vs_comment

**Description:** Docstring describes state checking logic that differs from implementation

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Docstring at lines 27-35 states:
'IMPORTANT: For tick-based execution (visual UIs), only execute immediate mode when the interpreter is in a safe state. The implementation checks:
- runtime.halted is True (program stopped)
- state.error_info is not None (program error)
- state.input_prompt is not None (waiting for INPUT)'

However, the actual implementation at lines 82-91 uses OR logic:
'return (self.runtime.halted or
        state.error_info is not None or
        state.input_prompt is not None)'

The docstring lists these as three separate checks but doesn't clearly indicate they are OR'd together (any one being true makes it safe). The docstring could be clearer: 'The implementation checks if ANY of the following are true:'

---

#### code_vs_comment

**Description:** Comment claims EDIT command 'count prefixes and search commands are not yet implemented' but doesn't clarify what happens when digits are entered

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~1050 says:
'Note: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K) are not yet implemented.
Digits fall through the command handling logic and produce no action (no output, no cursor movement).'

However, the actual edit command handler (cmd_edit) has no explicit handling for digit characters. The code will read the digit via _read_char() but then fall through all the if/elif branches without any action, which matches the comment. But this behavior is implicit rather than documented in code.

---

#### code_vs_documentation

**Description:** CHAIN command documentation incomplete regarding execution flow

**Affected files:**
- `src/interactive.py`

**Details:**
The cmd_chain docstring at line ~673 describes the CHAIN command parameters but doesn't mention that it raises ChainException to signal the interpreter to restart. The comment at line ~779 says:
'# Raise ChainException to signal run() loop to restart with new program
# This avoids recursive run() calls'

This is a critical implementation detail for understanding CHAIN behavior but is not documented in the main docstring.

---

#### code_vs_comment

**Description:** MERGE command comment about runtime update doesn't match actual implementation location

**Affected files:**
- `src/interactive.py`

**Details:**
The cmd_merge docstring at line ~598 says:
'- If program_runtime exists, updates runtime's statement_table (for CONT support)'

But the actual runtime update code at line ~635 is inside the 'if success:' block, meaning it only updates if the merge was successful. The docstring doesn't clarify this conditional behavior. Additionally, the update happens after the merge_from_file call, but the docstring makes it sound like it's part of the merge process itself.

---

#### code_vs_comment

**Description:** CONT command state management comment doesn't mention all cleared flags

**Affected files:**
- `src/interactive.py`

**Details:**
The cmd_cont docstring at line ~488 says:
'State management:
- Clears stopped/halted flags in runtime
- Restores PC from stop_pc (saved execution position)
- Resumes tick-based execution loop
- Handles input prompts and errors during execution'

But the actual implementation at lines ~497-499 shows:
self.program_runtime.stopped = False
self.program_runtime.halted = False

The docstring says 'Clears stopped/halted flags' but doesn't mention that both are explicitly set to False. More importantly, the code at line ~502 shows:
self.program_runtime.pc = self.program_runtime.stop_pc

This is described as 'Restores PC from stop_pc' but the actual operation is assignment, not restoration from a saved state. The comment could be clearer about what 'restore' means here.

---

#### code_vs_comment_conflict

**Description:** Comment claims GOTO/GOSUB in immediate mode are 'not recommended' and behavior 'may be confusing', but then describes that they actually work functionally. The comment is contradictory about whether these commands work properly.

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states: 'Note: GOTO/GOSUB in immediate mode are not recommended (see help text) because behavior may be confusing: they execute and jump during execute_statement(), but we restore the original PC afterward to preserve CONT functionality.'

Then explains: 'This means:
- The jump happens and target code runs during execute_statement()
- But the final PC change is reverted, preserving stopped position
- CONT will resume at the original stopped location, not the GOTO target
- So GOTO/GOSUB are functionally working but their PC effects are undone'

The comment describes working behavior but labels it as 'not recommended' and 'confusing' without clear justification.

---

#### code_vs_comment_conflict

**Description:** Comment describes PC restoration behavior that contradicts the stated purpose. The comment says PC is restored to 'preserve CONT functionality' but this would break GOTO/GOSUB semantics in a confusing way.

**Affected files:**
- `src/interactive.py`

**Details:**
Comment: 'Restore previous PC to maintain stopped program position'
Code: 'runtime.pc = old_pc'

The comment explains this preserves CONT but creates confusing behavior where GOTO/GOSUB execute their target code but then the PC jump is undone. This is a design decision that may be intentional but the comment presents it as if it's obviously correct rather than acknowledging the trade-off.

---

#### code_vs_comment

**Description:** InterpreterState docstring describes checking order for UI code examining completed state, but the actual execution order in tick_pc() is different and more complex

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring says:
"For UI/callers checking completed state:
- error_info: Non-None if an error occurred (highest priority for display)
- input_prompt: Non-None if waiting for input (set during statement execution)
- runtime.halted: True if stopped (paused/done/at breakpoint)"

But tick_pc() execution order is:
1. pause_requested check
2. halted check
3. break_requested check
4. breakpoints check
5. statement execution (where input_prompt is set)
6. error handling (where error_info is set)

The docstring's suggested checking order for UI is reasonable but doesn't match the internal execution flow, which could confuse developers trying to understand the state machine.

---

#### code_vs_comment

**Description:** Comment in current_statement_char_end property describes logic that doesn't fully match the implementation

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says:
"Uses max(char_end, next_char_start - 1) to handle string tokens correctly.
For the last statement on a line, uses line_text_map to get actual line length
(if available), otherwise falls back to stmt.char_end.
This works because:
- If there's a next statement, the colon is at next_char_start - 1
- If char_end is correct (most tokens), it will be >= next_char_start - 1
- If char_end is too short (string tokens), next_char_start - 1 is larger
- If no line_text_map entry exists, returns stmt.char_end as fallback"

But the code has three branches:
1. If next statement exists: return max(stmt_char_end, next_stmt.char_start - 1)
2. If no next statement AND line in line_text_map: return len(line_text)
3. If no next statement AND no line_text_map: return stmt_char_end

The comment doesn't clearly explain that branch 2 returns the full line length (not just char_end), which could be much larger than char_end if there are trailing spaces or comments.

---

#### code_vs_comment

**Description:** Comment about NEXT processing order conflicts with implementation details

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_next(), the docstring says:
"NEXT I, J, K processes variables left-to-right: I first, then J, then K.
For each variable, _execute_next_single() is called to increment it and check if
the loop should continue. If _execute_next_single() returns True (loop continues),
execution jumps back to the FOR body and remaining variables are not processed.
If it returns False (loop finished), that loop is popped and the next variable is processed."

But _execute_next_single() doesn't return True/False in the code shown. The code in execute_next() is:
```python
for var_node in var_list:
    var_name = var_node.name + (var_node.type_suffix or "")
    # Process this NEXT
    should_continue = self._execute_next_single(var_name, var_node=var_node)
    # If this loop continues (jumps back), don't process remaining variables
    if should_continue:
        return
```

The code expects a return value but _execute_next_single() signature shows:
"Returns:
    True if loop continues (jumped back), False if loop finished"

However, the implementation of _execute_next_single() is cut off in the provided code, so we can't verify if it actually returns these values. This is a potential inconsistency.

---

#### code_vs_comment

**Description:** Comment about return_stmt validation range is confusing

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_return(), the comment says:
"return_stmt is 0-indexed offset into statements array.
Valid range: 0 to len(statements) (inclusive).
- 0 to len(statements)-1: Normal statement positions
- len(statements): Special sentinel - GOSUB was last statement on line, so RETURN
  continues at next line. This value is valid because PC can point one past the
  last statement to indicate 'move to next line' (handled by statement_table.next_pc).
Values > len(statements) indicate the statement was deleted (validation error)."

But the validation code is:
```python
if return_stmt > len(line_statements):  # Check for strictly greater than (== len is OK)
    raise RuntimeError(f"RETURN error: statement {return_stmt} in line {return_line} no longer exists")
```

The comment correctly explains the logic, but the inline comment "Check for strictly greater than (== len is OK)" is redundant with the detailed comment above. The detailed comment is clear, but having both might confuse readers about which to trust.

---

#### code_vs_comment

**Description:** Comment describes WEND popping loop 'after setting npc above, before WHILE re-executes' but the actual pop happens after npc is set, which means the loop is popped before WHILE condition is re-evaluated, not 'before WHILE re-executes'

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: 'Pop the loop from the stack (after setting npc above, before WHILE re-executes). Timing: We pop NOW so the stack is clean before WHILE condition re-evaluation.'

Code shows:
self.runtime.npc = PC(loop_info['while_line'], loop_info['while_stmt'])
self.limits.pop_while_loop()
self.runtime.pop_while_loop()

The comment is internally contradictory - it says 'before WHILE re-executes' but then clarifies 'before WHILE condition re-evaluation', which are the same thing. The code pops after setting npc but before the next tick executes WHILE.

---

#### code_vs_comment

**Description:** Comment describes return_stmt validation logic incorrectly - says '> len(statements): Invalid' but the actual validation allows '== len' as valid sentinel

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says:
'Valid range:
  - 0 to len(statements)-1: Normal statement positions (existing statements)
  - len(statements): Special sentinel value - FOR was last statement on line,
                     continue execution at next line (no more statements to execute on current line)
  - > len(statements): Invalid - indicates the statement was deleted

Validation: Check for strictly greater than (== len is OK as sentinel)'

Code: if return_stmt > len(line_statements):

The comment correctly describes the logic, but the phrasing '> len(statements): Invalid' in the list could be misread as '>= len(statements)' being invalid. The clarification at the end is correct.

---

#### code_vs_comment

**Description:** Comment in execute_optionbase describes check 'len(self.runtime._arrays) > 0' but doesn't mention that this catches both explicit DIM and implicit array access

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: 'MBASIC 5.21 gives "Duplicate Definition" if:
1. OPTION BASE has already been executed, OR
2. Any arrays have been created (both explicitly via DIM and implicitly via first use like A(5)=10)
   This applies regardless of the current array base (0 or 1).
Note: The check len(self.runtime._arrays) > 0 catches all array creation because both
explicit DIM and implicit array access (via set_array_element) update runtime._arrays.'

The comment is actually accurate and complete. This is not an inconsistency.

---

#### code_vs_comment

**Description:** Comment in _read_line_from_file says 'Encoding: Uses latin-1' but doesn't mention that write operations may use different encoding

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment describes latin-1 encoding for reading:
'Encoding:
Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
Unicode U+0000-U+00FF, allowing round-trip byte preservation.'

However, in execute_open, mode 'O' and 'A' open with binary=False, which may use default system encoding (UTF-8), not latin-1. This creates an encoding mismatch between read and write operations.

---

#### code_vs_comment

**Description:** Comment in execute_reset says 'Unlike CLEAR (which silently ignores file close errors), RESET allows errors during file close to propagate' but CLEAR uses bare except which catches all errors

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_reset:
'Note: Unlike CLEAR (which silently ignores file close errors), RESET allows
errors during file close to propagate to the caller. This is intentional
different behavior between the two statements.'

Code in execute_clear:
try:
    file_obj = self.runtime.files[file_num]
    if hasattr(file_obj, 'close'):
        file_obj.close()
except:
    pass

Code in execute_reset:
for file_num in list(self.runtime.files.keys()):
    self.runtime.files[file_num]['handle'].close()
    del self.runtime.files[file_num]

The comment is accurate - CLEAR catches all exceptions with bare except, RESET doesn't catch any. However, the comment in execute_clear says 'bare except: pass below' which is misleading about location.

---

#### code_vs_comment

**Description:** Comment claims RSET truncates from left when value is too long, but code truncates from right

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: "Right-justify: pad on left if too short, truncate from left if too long"
But code does: value = value[-width:] which keeps rightmost characters (truncates from left is correct)
Actually, the code IS correct for right-justify (keeping rightmost chars), but the comment is ambiguous. For right-justify, you want to keep the rightmost characters when truncating, which value[-width:] does correctly.

---

#### code_vs_comment

**Description:** Comment claims string concatenation limit is 255 characters, but check uses len() which counts characters not bytes, inconsistent with field buffer encoding note

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_binaryop:
Comment: "Enforce 255 character string limit for concatenation (MBASIC 5.21 compatibility)
Note: This check only applies to concatenation via PLUS operator.
Other string operations (MID$, LSET, RSET, INPUT) do not enforce this limit.
Also note: len() counts characters, not bytes. For ASCII this is equivalent.
Field buffers (LSET/RSET) explicitly use latin-1 encoding where byte count matters."

The comment acknowledges len() counts characters not bytes, and mentions field buffers use latin-1 where bytes matter. However, for the 255 limit check on concatenation, it's unclear if MBASIC 5.21 enforced a 255-byte or 255-character limit. If latin-1 is used elsewhere, the limit might be bytes.

---

#### code_vs_comment

**Description:** Comment in execute_step says 'not yet functional - no actual stepping occurs' but doesn't explain what the current implementation does

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: "STEP is intended to execute one or more statements, then pause.
Current implementation: Placeholder (not yet functional - no actual stepping occurs).

Status: The tick_pc() method has infrastructure for step_statement and step_line
modes, but this immediate STEP command is not yet connected to that infrastructure."

Code: count = stmt.count if stmt.count else 1
self.io.output(f"STEP {count} - Debug stepping not fully implemented")

The comment says it's a placeholder and not functional, but the code does extract the count and output a message. It's unclear if this is 'not functional' or 'partially functional'.

---

#### documentation_inconsistency

**Description:** execute_list docstring claims line_text_map is kept in sync by ProgramManager but doesn't specify what happens if sync fails

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring: "Implementation note: Outputs from line_text_map (original source text), not regenerated from AST.
This preserves original formatting/spacing/case. The line_text_map is maintained by ProgramManager
and is kept in sync with the AST during program modifications (add_line, delete_line, RENUM, MERGE).
The sync is handled by ProgramManager methods and should remain consistent during normal operation."

The phrase 'should remain consistent during normal operation' implies it might not always be consistent, but there's no error handling in execute_list for missing line_text_map entries. The code checks 'if line_num in self.runtime.line_text_map' but doesn't document what happens if a line is missing.

---

#### Code vs Documentation inconsistency

**Description:** WebIOHandler has backward compatibility aliases print() and get_char() that are not documented in the base IOHandler interface or mentioned in the module-level documentation

**Affected files:**
- `src/iohandler/web_io.py`
- `src/iohandler/base.py`

**Details:**
web_io.py contains:
    def print(self, text="", end="\n"):
        """Deprecated: Use output() instead.

        This is a backward compatibility alias. New code should use output().
        """
        self.output(text, end)

    def get_char(self):
        """Deprecated: Use input_char() instead.

        This is a backward compatibility alias. New code should use input_char().
        """
        return self.input_char(blocking=False)

These methods are not part of the IOHandler base class interface and are not mentioned in any documentation about the iohandler module.

---

#### Code vs Documentation inconsistency

**Description:** Module docstring mentions SimpleKeywordCase and references src/simple_keyword_case.py, but this file is not included in the provided source code files, making it impossible to verify the relationship or consistency

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
keyword_case_manager.py docstring states:
Note: This class provides advanced case policies (first_wins, preserve, error) via
CaseKeeperTable and is used by parser.py and position_serializer.py. For simpler
force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py)
which only supports force_lower, force_upper, and force_capitalize.

The referenced file 'src/simple_keyword_case.py' is not provided in the source code files, so the relationship and consistency cannot be verified.

---

#### code_vs_comment

**Description:** Comment claims SimpleKeywordCase 'validates policy strings and defaults to force_lower for invalid values', but the actual SimpleKeywordCase class is not shown in the provided code, so this cannot be verified

**Affected files:**
- `src/lexer.py`

**Details:**
In create_keyword_case_manager() docstring:
"SimpleKeywordCase validates policy strings and defaults to force_lower for invalid values."

The SimpleKeywordCase class implementation is imported but not provided, so we cannot verify if it actually validates and defaults as claimed.

---

#### code_vs_comment

**Description:** Comment claims identifiers use 'original_case' field while keywords use 'original_case_keyword', but the code sets both fields inconsistently

**Affected files:**
- `src/lexer.py`

**Details:**
Comment in read_identifier() says:
"Preserve original case for display (identifiers always use original_case field,
unlike keywords which use original_case_keyword with policy-determined case)"

However, for keywords, the code sets:
token.original_case_keyword = display_case

But for identifiers, the code sets:
token.original_case = ident

This is consistent with the comment, but the Token class definition is not provided to verify these fields exist and are used correctly elsewhere.

---

#### code_vs_comment

**Description:** Comment claims 'MBASIC allows "PRINT#1" with no space' and describes special handling, but the implementation may not handle all file I/O keywords consistently

**Affected files:**
- `src/lexer.py`

**Details:**
Comment in read_identifier() says:
"Special case: File I/O keywords followed by # (e.g., PRINT#1)
MBASIC allows 'PRINT#1' with no space, which should tokenize as:
  PRINT (keyword) + # (operator) + 1 (number)"

The code checks:
if keyword_part in ['print', 'lprint', 'input', 'write', 'field', 'get', 'put', 'close']:

However, the comment earlier mentions 'PRINT# and INPUT#' specifically, but the list includes many more keywords. It's unclear if all these keywords actually support the # syntax in MBASIC 5.21.

---

#### code_vs_comment

**Description:** Comment claims RND and INKEY$ can be called without parentheses as MBASIC 5.21 behavior, but implementation only allows this for RND and INKEY$, not universally

**Affected files:**
- `src/parser.py`

**Details:**
Module docstring states:
"Exception: RND and INKEY$ can be called without parentheses (MBASIC 5.21 behavior)
Note: This is MBASIC-specific, not universal to all BASIC dialects"

However, the implementation in parse_builtin_function() only handles RND and INKEY specifically:
"# RND can be called without parentheses (RND returns random in [0,1))
# RND(n) where n>0 returns same sequence, n<0 reseeds, n=0 repeats last
if func_token.type == TokenType.RND and not self.match(TokenType.LPAREN):
    # RND without arguments
    return FunctionCallNode(...)

# INKEY$ can be called without parentheses (returns keyboard input or "")
if func_token.type == TokenType.INKEY and not self.match(TokenType.LPAREN):
    # INKEY$ without arguments
    return FunctionCallNode(...)

# Expect opening parenthesis for other functions or RND/INKEY$ with args
self.expect(TokenType.LPAREN)"

---

#### code_vs_comment

**Description:** Comment about MID$ statement detection describes complex lookahead but implementation may have issues with error recovery

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_statement() states:
"# MID$ statement (substring assignment)
# Detect MID$ used as statement: MID$(var, start, len) = value
...
# Complex lookahead: scan past parentheses (tracking depth) to find = sign"

The implementation uses try/except for lookahead:
"saved_pos = self.position
try:
    self.advance()  # Skip MID
    ...
except:
    pass
# Not a MID$ statement, restore and fall through to error
self.position = saved_pos"

The bare 'except:' clause catches all exceptions, which could hide legitimate parse errors. The comment doesn't mention this error handling strategy, and catching all exceptions may not be the intended behavior.

---

#### code_vs_comment

**Description:** Comment describes incorrect field name for ShowSettingsStatementNode

**Affected files:**
- `src/parser.py`

**Details:**
In parse_showsettings() method:
Comment says: "Field name: 'pattern' (optional filter string)"
But the code creates: ShowSettingsStatementNode(pattern=pattern_expr, ...)
The comment is correct, but it's placed in a way that suggests documentation of the field name, which matches the code. However, the comment format is inconsistent with other methods that don't document field names this way.

---

#### code_vs_comment

**Description:** Comment describes incorrect field name for SetSettingStatementNode

**Affected files:**
- `src/parser.py`

**Details:**
In parse_setsetting() method:
Comment says: "Field name: 'setting_name' (string identifying setting)"
Code creates: SetSettingStatementNode(setting_name=setting_name_expr, ...)
The comment format suggests this is documentation, but it's inconsistent with other parsing methods that don't include such field name documentation in comments.

---

#### code_vs_comment

**Description:** Comment about LINE keyword tokenization may be misleading

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() method:
Comment: "Note: The lexer tokenizes standalone LINE keyword as LINE_INPUT token."
This suggests LINE is always tokenized as LINE_INPUT, but the code checks:
if self.match(TokenType.LINE_INPUT):
This implies LINE_INPUT is a distinct token type, not just LINE. The comment should clarify that LINE in the context of INPUT is tokenized as LINE_INPUT, not that all LINE keywords become LINE_INPUT tokens.

---

#### code_vs_comment

**Description:** Comment about MID$ tokenization uses inconsistent terminology

**Affected files:**
- `src/parser.py`

**Details:**
In parse_mid_assignment() method:
Comment: "Note: The lexer tokenizes 'MID$' in source as a single MID token (the $ is part of the keyword, not a separate token)."
Code comment: "token = self.current()  # MID token (represents 'MID$' from source)"

This is consistent, but the phrasing 'the $ is part of the keyword' could be clearer. It should say 'the $ suffix is stripped by the lexer and the keyword is tokenized as MID' to match typical BASIC lexer behavior.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of type suffixes in DEF FN parsing

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deffn() method, there are two code paths:

Path 1 (with FN keyword):
type_suffix = self.get_type_suffix(raw_name)
if type_suffix:
    raw_name = raw_name[:-1]
function_name = 'fn' + raw_name

Path 2 (without space):
raw_name = fn_name_token.value
# No type suffix stripping here

Path 2 doesn't strip the type suffix from raw_name before creating function_name. This creates inconsistency where 'DEF FN test$' and 'DEF FNtest$' would create different function names ('fntest' vs 'fntest$').

---

#### code_vs_comment

**Description:** Comment claims COMMON statement stores variable names as strings, but code actually stores them as strings (consistent). However, the comment about array indicators is misleading.

**Affected files:**
- `src/parser.py`

**Details:**
In parse_common() method:
Comment says: "We consume the parentheses but don't need to store array dimension info (COMMON shares the entire array, not specific subscripts)"
Code does: variables.append(var_name) - stores just the name string

The comment is accurate about not storing dimension info, but the implementation doesn't distinguish between array and non-array variables in the stored list. The parentheses are consumed but the array nature is not preserved in the AST node.

---

#### code_vs_comment

**Description:** RESUME statement comment about RESUME 0 behavior may be misleading

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_resume() says:
"# Note: RESUME 0 means 'retry error statement' (interpreter treats 0 and None equivalently)
# We store the actual value (0 or other line number) for the AST"

This suggests 0 and None are equivalent, but the code stores them differently (0 as integer, None as None). The comment claims the interpreter treats them equivalently, but this is parser code, not interpreter code. The distinction between storing 0 vs None in the AST could matter to the interpreter.

---

#### code_vs_comment

**Description:** DATA statement comment about unquoted strings doesn't match the actual token types accepted

**Affected files:**
- `src/parser.py`

**Details:**
Comment says:
"Unquoted strings extend until comma, colon, end of line, or unrecognized token"

But the code accepts:
- IDENTIFIER tokens
- NUMBER tokens (converted to strings)
- LINE_NUMBER tokens
- MINUS/PLUS tokens
- Any token with a string value (keywords)

The comment says 'unrecognized token' stops parsing, but the code actually accepts many token types including keywords. The stopping condition is more like 'tokens without string values' rather than 'unrecognized tokens'.

---

#### code_vs_comment

**Description:** PC class docstring describes stmt_offset as '0-based index' but also calls it 'offset' which is confusing terminology

**Affected files:**
- `src/pc.py`

**Details:**
Docstring says: 'The stmt_offset is a 0-based index into the statements list for a line...Note: stmt_offset is the list index (position in the statements array). The term "offset" is used for historical reasons but it\'s simply the array index.'

This acknowledges the terminology is misleading but doesn't resolve it. The field is named 'stmt_offset' throughout the codebase but is actually an array index, not an offset in the traditional sense.

---

#### code_vs_documentation

**Description:** apply_keyword_case_policy docstring says 'Callers may pass keywords in any case' but implementation behavior varies by policy

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring states: 'Args:
    keyword: The keyword to transform (may be any case - function handles normalization internally)'

And: 'Note: The first_wins policy normalizes keywords to lowercase for lookup purposes. Other policies transform the keyword directly. Callers may pass keywords in any case.'

However, the 'first_wins' policy does normalize to lowercase for lookup (keyword_lower = keyword.lower()), while other policies like 'preserve' expect the caller to pass the correct case. The docstring claim that 'function handles normalization internally' is only partially true.

---

#### code_vs_comment

**Description:** emit_keyword docstring says 'Caller is responsible for normalizing keyword to lowercase' but apply_keyword_case_policy docstring says callers can pass any case

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword docstring: 'Note: Caller is responsible for normalizing keyword to lowercase before calling.'

apply_keyword_case_policy docstring: 'Args:
    keyword: The keyword to transform (may be any case - function handles normalization internally)'

These two functions have contradictory expectations about who normalizes keywords.

---

#### code_vs_comment

**Description:** PositionSerializer.__init__ docstring says keyword_case_manager is 'from parser' but doesn't specify which parser attribute

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring: 'keyword_case_manager: KeywordCaseManager instance (from parser) with keyword case table'

And comment in code: '# Store reference to keyword case manager from parser'

But there's no indication of how to get this from the parser or what parser class is expected. This makes the API unclear for users of this class.

---

#### code_vs_comment

**Description:** Comment in check_array_allocation() states 'This calculation matches the array creation logic in src/interpreter.py execute_dim()' but the actual calculation uses (dim_size + 1) which may or may not match interpreter.py without verification

**Affected files:**
- `src/resource_limits.py`

**Details:**
Comment at line ~180: '# This calculation matches the array creation logic in src/interpreter.py execute_dim()'
Code calculates: total_elements *= (dim_size + 1)  # +1 for 0-based indexing

The comment claims this matches interpreter.py but we cannot verify this claim from the provided code. If interpreter.py uses different logic, memory tracking will be incorrect.

---

#### code_vs_documentation

**Description:** File system limits (max_open_files, max_file_size, max_total_files) are defined and documented but no tracking or enforcement methods are implemented

**Affected files:**
- `src/resource_limits.py`

**Details:**
Documented parameters:
- max_open_files: Maximum number of simultaneously open files
- max_file_size: Maximum size for a single file (bytes)
- max_total_files: Maximum number of files that can be created

These are initialized in __init__ and included in preset configurations, but there are no methods like:
- open_file() / close_file() to track current_open_files
- check_file_size() to enforce max_file_size
- check_total_files() to enforce max_total_files

Only current_open_files is tracked as an instance variable (line ~82) but never incremented or checked. This suggests incomplete implementation or that file tracking happens elsewhere.

---

#### code_vs_comment

**Description:** Comment claims line=-1 in last_write distinguishes system variables from debugger sets, but both use line=-1

**Affected files:**
- `src/runtime.py`

**Details:**
In __init__ docstring for _variables:
"Note: line -1 in last_write indicates non-program execution sources:
       1. System/internal variables (ERR%, ERL%) via set_variable_raw() with FakeToken(line=-1)
       2. Debugger/interactive prompt via set_variable() with debugger_set=True and token.line=-1
       Both use line=-1, making them indistinguishable in last_write alone."

But in set_variable_raw() docstring:
"The line=-1 marker in last_write distinguishes system variables from:
- Normal program execution (line >= 0)
- Debugger sets (also use line=-1, but via debugger_set=True)"

The first comment correctly states they are indistinguishable, but the second claims they are distinguished.

---

#### code_vs_comment

**Description:** get_variable() docstring says token is REQUIRED but allows fallback for missing attributes

**Affected files:**
- `src/runtime.py`

**Details:**
get_variable() docstring states:
"Args:
    token: REQUIRED - Token object with line and position info for tracking.
           Must not be None (ValueError raised if None).

           The token is expected to have 'line' and 'position' attributes.
           If these attributes are missing, getattr() fallbacks are used:
           - 'line' falls back to self.pc.line_num (or None if PC is halted)
           - 'position' falls back to None"

This is contradictory - if token is REQUIRED and must not be None, why document fallback behavior for missing attributes? Either the token must have these attributes (making fallbacks unnecessary), or the token can be incomplete (making 'REQUIRED' misleading).

---

#### code_vs_comment

**Description:** Docstring for get_execution_stack() contains misleading documentation about 'from_line' field

**Affected files:**
- `src/runtime.py`

**Details:**
The docstring states:
"For GOSUB calls:
{
    'type': 'GOSUB',
    'from_line': 60,      # DEPRECATED: Same as return_line (kept for compatibility)
    'return_line': 60,    # Line to return to after RETURN
    'return_stmt': 0      # Statement offset to return to
}

Note: 'from_line' is misleading and redundant with 'return_line'.
       Both contain the line number to return to (not where GOSUB was called from)."

However, the actual implementation shows:
result.append({
    'type': 'GOSUB',
    'from_line': entry.get('return_line', 0),  # Line to return to
    'return_line': entry.get('return_line', 0),
    'return_stmt': entry.get('return_stmt', 0)
})

The comment '# Line to return to' confirms both fields contain the return line, but the docstring's explanation that 'from_line' is "DEPRECATED" and "kept for compatibility" suggests it should perhaps be removed or that there's confusion about its purpose.

---

#### code_vs_comment

**Description:** reset_for_run() docstring claims it's 'like CLEAR + reload program' but implementation shows it preserves common_vars

**Affected files:**
- `src/runtime.py`

**Details:**
The docstring states:
"Reset runtime for RUN command - like CLEAR + reload program.

This preserves breakpoints but resets everything else, equivalent to:
- CLEAR (clear variables, arrays, files, DATA pointer, etc.)"

However, at the end of the implementation, there's a comment:
"# NOTE: self.common_vars is NOT cleared - preserved for CHAIN compatibility"

This means reset_for_run() does NOT reset "everything else" as claimed. The common_vars are preserved, which is not mentioned in the main docstring description. This could be intentional for CHAIN compatibility, but the docstring should explicitly mention this exception.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about FILE scope settings availability

**Affected files:**
- `src/settings.py`
- `src/settings_definitions.py`

**Details:**
src/settings.py docstring says: 'Note: File-level settings infrastructure exists (file_settings dict, FILE scope), but there are currently no settings defined with FILE scope in settings_definitions.py, and there is no UI or command to manage per-file settings yet.'

However, src/settings.py get() method docstring says: 'Note: File-level settings infrastructure exists but is not yet fully implemented. The file_settings dict can be set programmatically and is checked first in precedence, but there is no UI or command to manage per-file settings. In normal usage, file_settings is empty and precedence falls through to project/global settings.'

The first says 'no settings defined with FILE scope', the second says 'can be set programmatically'. These statements are subtly different - one implies no definitions exist, the other implies programmatic use is possible.

---

#### code_vs_documentation_inconsistency

**Description:** Token.original_case_keyword field purpose conflicts with SimpleKeywordCase usage

**Affected files:**
- `src/tokens.py`
- `src/simple_keyword_case.py`

**Details:**
In src/tokens.py, Token dataclass has field 'original_case_keyword' documented as: 'Original case for keywords, determined by keyword case policy. Only set for keyword tokens (PRINT, IF, GOTO, etc.). Used by serializer to output keywords with consistent or preserved case style.'

However, src/simple_keyword_case.py docstring says: 'This is a simplified keyword case handler used by the lexer (src/lexer.py). It supports only three force-based policies: force_lower, force_upper, force_capitalize... For advanced policies (first_wins, preserve, error) via CaseKeeperTable, see KeywordCaseManager'

The Token field mentions 'preserved case style' but SimpleKeywordCase only supports force-based policies, not preservation. This suggests either:
1. The Token field documentation is too broad
2. SimpleKeywordCase should support preservation
3. KeywordCaseManager sets this field differently

---

#### Documentation inconsistency

**Description:** CLI STEP command documentation claims it implements statement-level stepping 'similar to the curses UI Step Statement command (Ctrl+T)', but the curses keybindings show Ctrl+K is for 'Step Line' and Ctrl+T is for 'Step statement'. The CLI documentation mentions 'Step Line' (Ctrl+K) is not available in CLI, but doesn't acknowledge that CLI STEP is supposed to match Ctrl+T behavior.

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/curses_keybindings.json`

**Details:**
cli_debug.py docstring says:
"This implements statement-level stepping similar to the curses UI 'Step Statement'
command (Ctrl+T). The curses UI also has a separate 'Step Line' command (Ctrl+K)
which is not available in the CLI."

curses_keybindings.json shows:
"step_line": { "keys": ["Ctrl+K"], "description": "Step Line (execute all statements on current line)" }
"step": { "keys": ["Ctrl+T"], "description": "Step statement (execute one statement)" }

The CLI doc correctly identifies Ctrl+T as statement-level and Ctrl+K as line-level, but the phrasing could be clearer.

---

#### Code vs Comment conflict

**Description:** The _execute_single_step() method's docstring claims it executes 'one statement at the current program counter position' and that tick()/execute_next() are 'expected to advance the program counter by one statement', but then contradicts itself by noting 'If the interpreter executes full lines instead, this method will behave as line-level stepping rather than statement-level.'

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
Docstring states:
"Execute a single statement (not a full line).

Uses the interpreter's tick() or execute_next() method to execute
one statement at the current program counter position.

Note: The actual statement-level granularity depends on the interpreter's
implementation of tick()/execute_next(). These methods are expected to
advance the program counter by one statement, handling colon-separated
statements separately. If the interpreter executes full lines instead,
this method will behave as line-level stepping rather than statement-level."

This is contradictory - it claims to execute one statement but admits it might execute a full line depending on implementation. The uncertainty suggests either the code doesn't guarantee statement-level stepping or the comment is outdated.

---

#### Code implementation issue

**Description:** The cmd_step() method displays current line number after each step with format '[{line_num}]', but the docstring says 'After each step, displays the current line number in format: [{line_num}]' without explaining what this format means or why brackets are used. This format is not documented elsewhere and may be confusing to users.

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
Docstring: "After each step, displays the current line number in format: [{line_num}]"

Code:
if self.interactive.program_runtime.current_line:
    line_num = self.interactive.program_runtime.current_line.line_number
    self.interactive.io_handler.output(f"[{line_num}]")

No explanation of why brackets are used or what they signify.

---

#### code_vs_comment

**Description:** Comment describes three-field format but implementation varies between methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring at line 143 describes format as: "S<linenum> CODE" with variable-width line numbers.

_format_line() at line 449 implements: prefix = f"{status}{line_num_str} " (variable width)

_parse_line_numbers() at lines 991, 1024 implements: new_line = f" {line_num_formatted} {rest}" where line_num_formatted = f"{num_str:>5}" (fixed 5-char width)

The format is inconsistent between display and paste reformatting.

---

#### code_vs_comment

**Description:** Comment claims _parse_line_number uses fixed width but it actually parses variable width

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line 148 states: "The keypress method uses _parse_line_number to find code boundaries dynamically."

_parse_line_number() at line 177 finds variable-width line numbers: space_idx = line.find(' ', 1) and line_num = int(line[1:space_idx])

This correctly handles variable width, contradicting the implication that fixed width is used.

---

#### code_vs_comment

**Description:** Variable width parsing contradicts fixed width formatting in same method

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_numbers() at line 1000:
linenum_int, code_start_col = self._parse_line_number(line)  # Comment says 'Variable width'

But at line 1024 in same method:
line_num_formatted = f"{num_str:>5}"  # Fixed 5-char width
new_line = f"{status}{line_num_formatted} {rest}"

The method parses variable width but formats to fixed width, creating potential misalignment.

---

#### code_vs_comment

**Description:** Comment claims ImmediateExecutor is recreated in start() but interpreter is reused, but code shows interpreter is also created once in __init__ and reused

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~180 says: 'ImmediateExecutor Lifecycle: Created here with temporary IO handler (to ensure attribute exists), then recreated in start() with a fresh OutputCapturingIOHandler. Note: The interpreter (self.interpreter) is created once here and reused. Only the executor and its IO handler are recreated in start().'

However, the code in start() method (line ~200) shows:
immediate_io = OutputCapturingIOHandler()
self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)

This confirms the comment is accurate - interpreter is reused, only executor is recreated. But earlier comment at line ~170 says 'Interpreter Lifecycle: Created ONCE here in __init__ and reused throughout the session. The interpreter is NOT recreated in start()' which is redundant with the later comment.

---

#### code_vs_comment

**Description:** Comment about IO handler lifecycle mentions two handlers but describes three

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~150 says: 'IO Handler Lifecycle: 1. self.io_handler (CapturingIOHandler) - Used for RUN program execution... 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands...'

But the code also uses self.io_handler (passed to __init__ from parent class) which is a third IO handler. The comment only describes the two created locally (CapturingIOHandler for runs and OutputCapturingIOHandler for immediate mode) but doesn't mention the original self.io_handler parameter from the constructor signature at line ~90: 'def __init__(self, io_handler: IOHandler, program_manager: ProgramManager)'

---

#### code_vs_comment

**Description:** Comment about help widget lifecycle contradicts implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in _show_help() at line ~845 says: 'Note: Unlike _show_keymap and _show_settings which support toggling, help doesn't store overlay state so it can't be toggled off. The help widget handles its own close behavior via ESC/Q keys.'

But _show_keymap() at line ~870 shows: 'This method supports toggling - calling it when keymap is already open will close it.' and checks 'if hasattr(self, '_keymap_overlay') and self._keymap_overlay:' to implement toggling.

The comment correctly describes that help doesn't support toggling, but the reason given ('help widget handles its own close behavior') doesn't explain why toggling couldn't also be implemented for help like it is for keymap.

---

#### code_vs_comment

**Description:** Comment claims breakpoints are stored in editor and NOT in runtime, but code shows breakpoints ARE cleared by reset_for_run() and must be re-applied

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1090 says:
"Note: reset_for_run() clears variables and resets PC. Breakpoints are stored in
the editor (self.editor.breakpoints), NOT in runtime, so they persist across runs
and are re-applied below via interpreter.set_breakpoint() calls."

But immediately after at line ~1110, code shows:
"# Re-apply breakpoints from editor
# Breakpoints are stored in editor UI state and must be re-applied to interpreter
# after reset_for_run (which clears them)
for line_num in self.editor.breakpoints:
    self.interpreter.set_breakpoint(line_num)"

The comment contradicts itself - it says breakpoints are NOT in runtime and persist, but then the code explicitly re-applies them BECAUSE reset_for_run() clears them from the interpreter/runtime.

---

#### code_vs_comment

**Description:** Comment about statement-level precision for GOSUB contradicts the default value handling

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_stack_window() at line ~1005:
Comment says: "# Show statement-level precision for GOSUB return address
# Note: default of 0 if return_stmt is missing means first statement on line"

But the code uses:
"return_stmt = entry.get('return_stmt', 0)"

This implies that if 'return_stmt' is missing, it defaults to 0 (first statement). However, the comment's phrasing "if return_stmt is missing" suggests this might be an error condition rather than normal behavior. The comment should clarify whether missing return_stmt is expected or indicates a bug.

---

#### code_vs_comment

**Description:** Comment about preserving PC state has unclear logic about paused_at_breakpoint

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sync_program_to_runtime() at line ~1260:
Comment says: "# Restore PC only if execution is running AND not paused at breakpoint
# (paused programs need PC reset to current breakpoint location)
# Otherwise ensure halted (don't accidentally start execution)"

But the code condition is:
"if self.running and not self.paused_at_breakpoint:"

The comment says "paused programs need PC reset to current breakpoint location" but the code in the else branch sets PC to halted_pc(), not to the breakpoint location. This suggests either the comment is wrong about what happens to paused programs, or the code is missing logic to handle the paused case properly.

---

#### code_vs_comment

**Description:** Comment claims DELETE and RENUM update self.program immediately and runtime sync occurs automatically via _execute_immediate, but the code shows runtime=None is passed to helper functions, meaning runtime is never synced at all during these operations

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_delete docstring:
"Note: Updates self.program immediately (source of truth). Runtime sync occurs
automatically via _execute_immediate which calls _sync_program_to_runtime before
executing any immediate command. This ensures runtime is always in sync when needed."

But the code calls:
deleted = delete_lines_from_program(self.program, args, runtime=None)

And in cmd_renum:
old_lines, line_map = renum_program(
    self.program,
    args,
    self.interpreter.interactive_mode._renum_statement,
    runtime=None
)

Passing runtime=None means the runtime is never updated by these helper functions. The comment suggests _execute_immediate will sync later, but these commands are called directly via cmd_delete/cmd_renum, not necessarily through _execute_immediate.

---

#### code_internal_inconsistency

**Description:** Duplicate CapturingIOHandler class definition in _execute_immediate with comment acknowledging duplication but not fixing it

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method:
"# Need to create the CapturingIOHandler class inline
# (duplicates definition in _run_program - consider extracting to shared location)
class CapturingIOHandler:"

The comment explicitly states this is a duplicate of code in _run_program and should be extracted, but the duplication remains. This violates DRY principle and creates maintenance burden.

---

#### code_internal_inconsistency

**Description:** Inconsistent output handling between _execute_immediate and cmd_* methods - immediate uses output_walker.append while cmd_* methods use _write_output

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate:
"self.output_walker.append(make_output_line(f'> {command}'))"
"self.output_walker.append(make_output_line(line))"

But in cmd_save, cmd_delete, cmd_renum, cmd_merge, cmd_files, cmd_cont:
"self._write_output(f'Saved to {filename}\n')"
"self._write_output(f'?Syntax error: filename required\n')"

This inconsistency suggests different output mechanisms are used depending on the code path, which could lead to output appearing in different places or with different formatting.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says command is logged to output pane 'not separate immediate history', but there's no context about what 'separate immediate history' refers to or why this distinction matters

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says:
"# Log the command to output pane (not separate immediate history)
self.output_walker.append(make_output_line(f'> {command}'))"

This comment references a 'separate immediate history' concept that doesn't appear to exist in the visible code, suggesting either removed functionality or incomplete refactoring.

---

#### code_vs_comment_conflict

**Description:** Docstring for _expand_kbd() describes searching across all sections, but implementation detail about 'action name' vs 'key name' terminology is inconsistent

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
The _expand_kbd() method docstring (lines 77-91) uses inconsistent terminology:
- Parameter name: "key_name: Name of key action (e.g., 'help', 'save', 'run')"
- Description: "This is searched across all keybinding sections"
- Example: "_expand_kbd('help') searches all sections for an action named 'help'"

The parameter is called 'key_name' but the docstring describes it as 'action name' or 'key action'. This is confusing - it should consistently use 'action' terminology since that's what the keybindings JSON structure uses (actions within sections).

---

#### code_vs_comment_conflict

**Description:** Comment in fmt_key() function claims limitation only handles Ctrl+ prefix, but this may be intentional design rather than limitation

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
The fmt_key() docstring (lines 33-46) states:
"Limitation: Only handles 'Ctrl+' prefix. Other formats like 'Alt+X',
'Shift+Ctrl+X', or 'F5' are returned unchanged. This is acceptable for
the curses menu which primarily uses Ctrl+ keybindings."

This is described as a 'Limitation' but the comment also says it's 'acceptable'. The function is working as designed for the curses menu's needs. The term 'limitation' suggests a deficiency, but the implementation is intentionally simple because the curses menu only uses Ctrl+ shortcuts. This should be clarified as intentional design rather than a limitation.

---

#### code_inconsistency

**Description:** HelpWidget hardcodes 'curses' UI name but HelpMacros is designed to be UI-agnostic

**Affected files:**
- `src/ui/help_widget.py`
- `src/ui/help_macros.py`

**Details:**
In help_widget.py line 48:
"# HelpWidget is curses-specific (uses urwid), so hardcode 'curses' UI name
self.macros = HelpMacros('curses', help_root)"

However, HelpMacros class in help_macros.py is designed to be UI-agnostic, accepting ui_name as a parameter (line 18). The HelpWidget could receive ui_name as a parameter instead of hardcoding it, making the code more flexible. While the comment explains why it's hardcoded (urwid is curses-specific), this creates tight coupling that could be avoided.

---

#### code_vs_comment

**Description:** Variable name LIST_KEY doesn't match its actual functionality

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment says: "Note: Variable named LIST_KEY for historical reasons (it was originally associated with BASIC's LIST command). This variable now implements step_line debugger functionality, which executes all statements on the current line before pausing again. The variable name doesn't match its current purpose but is retained for backward compatibility."

Code: LIST_KEY = _ctrl_key_to_urwid(_list_key)

The variable is loaded from 'step_line' action in JSON but named LIST_KEY, creating confusion.

---

#### code_vs_comment

**Description:** CONTINUE_KEY comment describes dual functionality but implementation doesn't show context-sensitivity

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment says: "Note: This key (typically Ctrl+G) is context-sensitive in the UI:
  - In debugger mode: Continue execution until next breakpoint or end
  - In editor mode: Go to line number (not yet implemented)
Loaded from 'goto_line' action in JSON since both uses share the same key."

Code: _continue_key = _get_key('editor', 'goto_line') or 'Ctrl+G'
CONTINUE_KEY = _ctrl_key_to_urwid(_continue_key)

The comment describes context-sensitive behavior, but the keybindings.py module only defines the key constant. The actual context-sensitive logic must be implemented elsewhere, but this isn't clear from the code.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of Stack window access method

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
In STACK_KEY definition:
"Note: No keyboard shortcut is assigned to avoid conflicts with editor typing.
The stack window is accessed via the menu system (Ctrl+U -> Debug -> Execution Stack)."
STACK_KEY = ''  # No keyboard shortcut
STACK_DISPLAY = 'Menu only'

But in KEYBINDINGS_BY_CATEGORY under 'Global Commands':
(STACK_DISPLAY, 'Toggle execution stack window')

The word 'Toggle' implies it can be toggled with a key, but STACK_DISPLAY is 'Menu only'. This is misleading.

---

#### Code vs Documentation inconsistency

**Description:** ESC key binding to close in-page search is implemented but not documented in keybindings

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
In tk_help_browser.py line 127-128:
# Note: ESC closes search bar - this is not documented in tk_keybindings.json
# as it's a local widget binding rather than a global application keybinding
self.inpage_search_entry.bind('<Escape>', lambda e: self._inpage_search_close())

The tk_keybindings.json file has a 'help_browser' section with 'search' and 'inpage_search' keys, but does not document the ESC key binding for closing the in-page search bar. While the comment explains this is intentional (local vs global binding), this creates an inconsistency where users looking at the keybindings file won't find this documented shortcut.

---

#### code_vs_comment

**Description:** Comment describes 4-pane layout but implementation has 3 panes plus conditional INPUT row

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring says:
"    - 4-pane vertical layout:
      * Editor with line numbers (top, ~50% - weight=3)
      * Output pane (middle, ~33% - weight=2)
      * INPUT row (shown only for INPUT statements, hidden otherwise)
      * Immediate mode input line (bottom, ~17% - weight=1)"

But code creates 3 PanedWindow panes:
1. editor_frame (weight=3)
2. output_frame (weight=2)
3. immediate_frame (weight=1)

The INPUT row is created inside output_frame and shown/hidden dynamically, not as a separate pane.

---

#### code_vs_comment

**Description:** Docstring describes syntax highlighting as 'optional' but no implementation or configuration for it exists

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring line ~50 says:
"    - Syntax highlighting (optional)"

But there is no code implementing syntax highlighting, no configuration option to enable/disable it, and no mention of it being a planned feature. This suggests either:
1. Feature was removed but docstring not updated
2. Feature is planned but not yet implemented
3. Feature exists elsewhere but not in this file

---

#### code_vs_comment

**Description:** Comment about toolbar simplification references removed features but doesn't explain why

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines ~465-469:
"# Note: Toolbar has been simplified to show only essential execution controls.
# Additional features are accessible via menus:
# - List Program → Run > List Program
# - New Program (clear) → File > New
# - Clear Output → Run > Clear Output"

This suggests the toolbar was previously more complex and was simplified, but:
1. No explanation of why it was simplified
2. No indication if this is temporary or permanent
3. The comment format suggests this is a recent change that might need review

This could indicate incomplete refactoring or a design decision that should be documented elsewhere.

---

#### code_vs_comment

**Description:** Comment claims auto-numbering is only called from _on_enter_key, but this contradicts the purpose of the method

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1180 states:
"Currently called only from _on_enter_key (after each Enter key press), not
after pasting or other modifications."

However, the method _remove_blank_lines() is designed to clean up blank lines in general. The comment suggests it's intentionally limited to Enter key presses, but this seems like an implementation limitation rather than a design choice. The method's docstring says it removes blank lines to "keep program clean" which suggests it should be called more broadly.

---

#### code_vs_comment

**Description:** Comment about validation timing contradicts implementation details

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~1140, comment states:
"# Note: This method is called with a delay (100ms) after cursor movement/clicks
# to avoid excessive validation during rapid editing"

But looking at _on_cursor_move() at line ~1175:
"self.root.after(100, self._validate_editor_syntax)"

And _on_mouse_click() at line ~1185:
"self.root.after(100, self._validate_editor_syntax)"

The 100ms delay is implemented in the callers, not in _validate_editor_syntax itself. The comment in _validate_editor_syntax makes it sound like the delay is part of that method's implementation, when it's actually the responsibility of the callers. This could be misleading for future maintainers.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of yellow statement highlight clearing

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~1183 in _on_mouse_click():
"# Clear yellow statement highlight when clicking (allows text selection to be visible)
if self.paused_at_breakpoint:
    self._clear_statement_highlight()"

But in _on_cursor_move() at line ~1177, there is no similar clearing of the yellow highlight. This means:
- Mouse click clears yellow highlight
- Arrow keys/cursor movement does NOT clear yellow highlight

This inconsistency in behavior could be confusing to users. Either both should clear it, or neither should (or there should be a comment explaining why the behavior differs).

---

#### code_vs_comment

**Description:** Comment claims clearing statement highlight on ANY key prevents visual artifacts, but code only clears when paused_at_breakpoint is True

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1180 says:
# Clear yellow statement highlight on any keypress when paused at breakpoint
# This prevents visual artifact where statement highlight remains on part of a line
# after text is modified (occurs because highlight is tag-based and editing shifts positions).
# Note: This clears on ANY key including arrows/function keys, not just editing keys.

But code implementation:
if self.paused_at_breakpoint:
    self._clear_statement_highlight()

The comment emphasizes 'ANY key' but the clearing only happens when paused_at_breakpoint is True, which is a specific state condition not mentioned in the comment's emphasis.

---

#### code_vs_comment

**Description:** Comment claims DON'T save to program yet because blank lines would be filtered, but this contradicts the auto-numbering behavior where numbered blank lines should be valid

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1490 in _smart_insert_line says:
# DON'T save to program yet - the line is blank and would be filtered out by
# _save_editor_to_program() which skips blank lines. Just position the cursor on
# the new line so user can start typing.

However, the inserted line has a line number (f'{insert_num} \n'), so it's not truly blank - it's a numbered line with no code. The comment suggests _save_editor_to_program() would filter it, but numbered lines (even without code) might be handled differently than truly blank lines. This creates ambiguity about what constitutes a 'blank line' for filtering purposes.

---

#### code_vs_comment

**Description:** Comment says 'Determine if program needs to be re-sorted' but lists conditions that include line number removal, which isn't about sorting but about validation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1360 says:
# Determine if program needs to be re-sorted:
# 1. Line number changed on existing line (both old and new are not None), OR
# 2. Line number was removed (old was not None, new is None and line has content)

Condition 2 (line number removed but content remains) isn't about re-sorting - it's about handling invalid lines (code without line numbers). The comment frames this as a sorting decision, but removing a line number creates an invalid state that needs different handling than just re-sorting.

---

#### code_vs_comment

**Description:** Comment in _update_immediate_status explains why 'not self.running' check is needed, but the logic combines it with can_execute_immediate() in a way that might not achieve the stated goal

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1785 says:
# Check if safe to execute - use both can_execute_immediate() AND self.running flag
# The 'not self.running' check prevents immediate mode execution when a program is running,
# even if the tick hasn't completed yet. This prevents race conditions where immediate
# mode could execute while the program is still running but between tick cycles.

Code:
can_exec_immediate = self.immediate_executor.can_execute_immediate()
can_execute = can_exec_immediate and not self.running

The comment suggests this prevents race conditions, but if can_execute_immediate() already checks runtime state properly, the additional 'not self.running' check might be redundant or indicate that can_execute_immediate() doesn't check what it should. This creates ambiguity about which component is responsible for the safety check.

---

#### code_vs_comment

**Description:** Comment claims immediate_history is always None but _setup_immediate_context_menu() and related methods reference it as if it could be a widget

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _add_immediate_output() docstring: "Note: self.immediate_history exists but is always None (see __init__) - it's a dummy attribute for compatibility with code that references it."

But _setup_immediate_context_menu() contains: "menu = tk.Menu(self.immediate_history, tearoff=0)" and "self.immediate_history.tag_ranges(tk.SEL)" which would fail if immediate_history is None.

Similarly, _copy_immediate_selection() and _select_all_immediate() call methods on self.immediate_history that would raise AttributeError if it's None.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about immediate mode output destination

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
_add_immediate_output() docstring says: "This method name is historical - it simply forwards to _add_output(). In the Tk UI, immediate mode output goes to the main output pane."

But _execute_immediate() comment says: "Execute without echoing (GUI design choice: command is visible in entry field, and 'Ok' prompt is unnecessary in GUI context - only results are shown)"

This creates confusion about whether immediate mode has its own output area or shares the main output pane. The docstring says it goes to main output, but the existence of _add_immediate_output() as a separate method and the 'historical' comment suggests there may have been a separate immediate output area previously.

---

#### code_vs_comment

**Description:** Comment about has_work() usage doesn't match actual usage pattern in codebase

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _execute_immediate() states: "Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command). This complements runtime flag checks (self.running, runtime.halted) used elsewhere."

However, the code immediately after checks has_work() and then checks 'if not self.running' to decide whether to start execution. This suggests has_work() is not complementing but rather preceding the runtime flag checks. The comment implies they work together, but the code shows has_work() is checked first, then runtime flags are used conditionally.

---

#### code_vs_comment

**Description:** Comment in _parse_line_number() states MBASIC 5.21 requires whitespace between line number and statement, but regex allows line number at end of string with no statement

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment says: "Note: '10REM' would not match (MBASIC 5.21 requires whitespace between line number and statement)"

But regex is: r'^(\d+)(?:\s|$)'

This regex matches '10' alone ($ = end of string) with no statement following, which contradicts the comment's implication that a statement must follow with whitespace. The comment suggests '10REM' is invalid due to missing whitespace, but doesn't clarify if '10' alone is valid.

---

#### code_vs_comment

**Description:** Comment in _delete_line() docstring describes parameter as 'Tkinter text widget line number (1-based sequential index)' but implementation uses it in f-string format that expects 1-based line numbers, while Tkinter text widget line numbers are actually 1-based

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring says: "line_num: Tkinter text widget line number (1-based sequential index), not BASIC line number (e.g., 10, 20, 30)"

Code uses: self.text.get(f'{line_num}.0', f'{line_num}.end') and self.text.delete(f'{line_num}.0', f'{line_num + 1}.0')

This is actually correct - Tkinter text widget lines ARE 1-based. However, the docstring's phrasing '(1-based sequential index)' in parentheses makes it seem like this is clarifying something unusual, when it's just the standard Tkinter behavior. The comment is technically correct but potentially confusing.

---

#### code_vs_comment

**Description:** Comment in _on_cursor_move() says 'Need to schedule this after current event processing to avoid issues' but doesn't specify what issues

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment: "# Need to schedule this after current event processing to avoid issues"

Code: self.text.after_idle(self._delete_line, self.current_line)

The comment doesn't explain what specific issues would occur without after_idle(). This could be: text widget modification during event handling, cursor position corruption, or undo stack issues. Without specifics, future maintainers might remove this thinking it's unnecessary.

---

#### code_vs_comment

**Description:** Comment in update_line_references() describes pattern as using non-greedy match for ON expressions, but warns about potential issues with expressions containing 'G'. However, the non-greedy match should handle this correctly.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Note: Pattern uses .+? (non-greedy) to match expression in ON statements,
which allows expressions containing any characters including 'G' (e.g., ON FLAG GOTO)"

The comment suggests this is a workaround, but non-greedy matching is the correct approach. The comment could be clearer about why this works rather than suggesting it's a potential issue.

---

#### code_vs_comment

**Description:** serialize_line() comment warns about fallback behavior causing inconsistent indentation, but doesn't explain when this occurs or how to prevent it

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states:
"# Note: If source_text doesn't match pattern, falls back to relative_indent=1
# This can cause inconsistent indentation for programmatically inserted lines"

This warning suggests a known issue but provides no guidance on how to handle programmatically inserted lines correctly. Should there be a way to set source_text for new lines?

---

#### code_vs_comment

**Description:** serialize_variable() comment about type suffix handling doesn't match the complexity of the actual logic

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Code:
if var.type_suffix and getattr(var, 'explicit_type_suffix', False):
    text += var.type_suffix

Comment:
"# Only add type suffix if it was explicit in the original source
# Don't add suffixes that were inferred from DEF statements
# Note: getattr defaults to False if explicit_type_suffix is missing, preventing suffix output"

The comment explains the intent but doesn't clarify what happens when explicit_type_suffix is missing vs False. The getattr default behavior is mentioned but the implications for backward compatibility aren't clear.

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

**Description:** Docstring claims breakpoint support is 'planned - not yet implemented' but doesn't clarify current state

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~826 in NiceGUIBackend docstring:
- Breakpoint support (planned - not yet implemented)

This is ambiguous - it's unclear if this is current documentation or outdated. If breakpoints are truly not implemented, the UI should not have any breakpoint-related buttons/menus, but this cannot be verified from the provided code.

---

#### code_vs_comment

**Description:** Comment claims RUN does NOT clear output, but code behavior and comment contradict each other

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~1806, comment states:
"# Don't clear output - continuous scrolling like ASR33 teletype
# Note: Step commands (Ctrl+T/Ctrl+K) DO clear output for clarity when debugging"

However, at line ~2027 in _menu_step_line and line ~2084 in _menu_step_stmt, the code calls:
"self._clear_output()"

This contradicts the comment's claim that step commands clear output. The comment says step commands DO clear output, and the code does clear output, so they agree. However, the comment about RUN not clearing output is inconsistent with the step behavior documentation.

---

#### code_vs_comment

**Description:** Comment claims breakpoints can be plain integers, but implementation uses PC objects exclusively

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~1438, comment states:
"# Note: self.runtime.breakpoints is a set that can contain:
#   - PC objects (statement-level breakpoints, created by _toggle_breakpoint)
#   - Plain integers (line-level breakpoints, legacy/compatibility)
# This implementation uses PC objects exclusively, but handles both for robustness."

The code then checks isinstance(item, PC) and handles plain integers in the else clause. However, all breakpoint creation code (_toggle_breakpoint at line ~1329, _do_toggle_breakpoint at line ~1463) only creates PC objects, never plain integers. The comment suggests legacy support that may not actually exist in practice.

---

#### code_vs_comment

**Description:** Comment about RUN behavior contradicts actual implementation regarding empty programs

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~1806, comment states:
"RUN on empty program is fine (just clears variables, no execution)."

But at line ~1843, the code checks:
"if not self.program.lines:
    self._set_status('Ready')
    self.running = False
    return"

This returns early without calling runtime.reset_for_run(), which means variables are NOT cleared for empty programs, contradicting the comment.

---

#### code_vs_comment

**Description:** Comment about state.current_line behavior when halted contradicts code usage

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~2169 in _handle_step_result, comment states:
"# Check PC directly - state.current_line returns None when halted"

But earlier in the same method at line ~2158, the code uses:
"self._set_status(f'Waiting for input at line {state.current_line}')"

This suggests state.current_line does NOT return None in all halted cases (specifically when waiting for input), contradicting the comment.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC only if exec_timer is active, but the logic description is confusing about 'preventing accidental starts'

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says: 'Preserves current PC/execution state only if exec_timer is active; otherwise resets PC to halted. This allows LIST and other commands to see the current program without starting execution.'

But inline comment says: '# This logic is about PRESERVING vs RESETTING state, not about preventing accidental starts'

The inline comment contradicts the docstring's claim about 'preventing accidental starts' (via LIST commands), suggesting the comment may have been added during refactoring to clarify intent.

---

#### code_vs_comment

**Description:** Comment describes double line number detection for paste, but the regex and logic may not match all cases

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment in _on_editor_change says: 'When pasting with auto-numbering enabled, the first line may have a double line number (e.g., "10 100 PRINT" where "10 " is the auto-number prompt and "100 PRINT" is pasted)'

But the regex check is: if lines and re.match(r'^\d+\s+\d+\s+', lines[0])

This requires whitespace after the second number, but the example '10 100 PRINT' would match. However, if user pastes '10 100PRINT' (no space after 100), it wouldn't match, creating inconsistent behavior.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'Don't create temporary ones!' but doesn't explain why this is critical

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment states: '# Use the session's single interpreter and runtime\n# Don't create temporary ones!'

The emphasis ('!') suggests this is critical, but there's no explanation of what would break if temporary instances were created. This makes it unclear whether this is a performance optimization or a correctness requirement.

---

#### code_vs_comment

**Description:** Architecture note claims 'we do NOT sync editor from AST' but then mentions RENUM updates editor text

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment in _execute_immediate states: 'Architecture note: We do NOT sync editor from AST after immediate commands. This preserves the one-way data flow: editor text → AST → execution. Syncing AST → editor would lose user's exact text, spacing, and comments. Some immediate commands (like RENUM) modify the AST directly, but we rely on those commands to update the editor text themselves, not via automatic sync.'

This is contradictory: if RENUM modifies the AST and updates the editor text, then there IS a sync from AST to editor, just done manually by the command. The 'one-way data flow' claim is misleading.

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
web_help_launcher.py function signature:
def open_help_in_browser(topic=None, ui_type='tk'):

Default is 'tk', but this file is named 'web_help_launcher.py' suggesting it's for web UI. Documentation shows help exists for cli, curses, tk, and web UIs equally, so defaulting to 'tk' seems arbitrary.

---

#### code_vs_documentation

**Description:** Settings dialog implementation doesn't match debugging documentation scope

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/debugging.md`

**Details:**
web_settings_dialog.py implements:
- Editor settings (auto-numbering)
- Limits settings (read-only)

But debugging.md extensively documents debugging features (breakpoints, stepping, variables window, stack window) with no mention of a settings dialog. The settings dialog doesn't expose any debugging-related settings.

---

#### documentation_inconsistency

**Description:** Compiler documentation describes features as implemented but code generation is marked 'In Progress'

**Affected files:**
- `docs/help/common/compiler/index.md`
- `docs/help/common/compiler/optimizations.md`

**Details:**
optimizations.md states:
'27 optimizations implemented in the semantic analysis phase.'
'All optimizations preserve the original program behavior while improving performance or reducing resource usage.'

But index.md states:
'Code Generation
Status: In Progress
Documentation for the code generation phase will be added as the compiler backend is developed.'

This creates confusion about whether the compiler is functional or not. The optimizations are described as 'implemented' but code generation is 'in progress', suggesting the compiler cannot actually generate executable code yet.

---

#### documentation_inconsistency

**Description:** ASCII codes documentation shows control character DEL at position 127, but error codes documentation references error code 127 which doesn't exist in the error table

**Affected files:**
- `docs/help/common/language/appendices/ascii-codes.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
ascii-codes.md shows:
| Dec | Hex | Name | Description |
|-----|-----|------|-------------|
| 127 | 7F | DEL | Delete/Rubout |

But error-codes.md only defines errors up to 67, with reserved ranges. No error 127 is documented.

---

#### documentation_inconsistency

**Description:** Inconsistent precision specifications for floating-point types

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/cdbl.md`
- `docs/help/common/language/functions/csng.md`

**Details:**
data-types.md states:
- SINGLE: "approximately 7 digits"
- DOUBLE: "approximately 16 digits"

cdbl.md states:
- DOUBLE: "approximately 16 digits of precision"

csng.md states:
- SINGLE: "approximately 7 digits of precision"

The word 'approximately' is used inconsistently - sometimes 'about', sometimes 'approximately'. While not technically wrong, standardization would improve clarity.

---

#### documentation_inconsistency

**Description:** Index describes math-functions.md as containing 'Derived mathematical functions' but the actual file also documents built-in functions

**Affected files:**
- `docs/help/common/language/appendices/index.md`
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
index.md states:
"### [Mathematical Functions](math-functions.md)
Derived mathematical functions using BASIC-80's intrinsic functions.

**Includes:**
- Trigonometric functions (secant, cosecant, cotangent)
- Inverse trigonometric functions
- Hyperbolic functions
- Inverse hyperbolic functions
- Mathematical constants and examples"

But math-functions.md actually has two sections:
1. "## Built-In Mathematical Functions" - listing SIN, COS, TAN, etc.
2. "## Derived Mathematical Functions" - showing how to compute SEC, CSC, etc.

The index description is incomplete.

---

#### documentation_inconsistency

**Description:** Data types documentation mentions 'Overflow' error but doesn't link to error codes appendix

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
data-types.md shows:
"**INTEGER Overflow:**
```basic
10 X% = 32767
20 X% = X% + 1     ' ERROR: Overflow
```

**Solution:** Use SINGLE or DOUBLE for larger numbers.

**Floating-Point Overflow:**
```basic
10 X# = 1D+308
20 X# = X# * 10    ' ERROR: Overflow
```"

error-codes.md defines:
"| **OV** | 6 | Overflow | The result of a calculation is too large to be represented in BASIC-80's number format. (Underflow results in zero with no error.) |"

The data-types.md should reference the error codes appendix for the Overflow error.

---

#### documentation_inconsistency

**Description:** PEEK documentation states it does NOT work with POKE, but doesn't clarify if POKE documentation exists or is consistent

**Affected files:**
- `docs/help/common/language/functions/peek.md`

**Details:**
PEEK.md states:
"Important Limitations:
- **PEEK does NOT return values written by POKE** (POKE is a no-op that does nothing)"

This indicates POKE exists as a statement but is non-functional. However, POKE is referenced in the 'See Also' section as '../statements/poke.md', but that file is not provided in the documentation set. Need to verify if POKE documentation exists and if it consistently describes the same non-functional behavior.

---

#### documentation_inconsistency

**Description:** LOC and LOF have identical 'See Also' sections despite different purposes

**Affected files:**
- `docs/help/common/language/functions/loc.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
Both LOC.md and LOF.md have exactly the same 'See Also' section with 14 identical references. While they are related file I/O functions, having identical cross-references suggests the lists may not be optimally curated for each function's specific use case.

---

#### documentation_inconsistency

**Description:** VAL function documentation lists incorrect 'See Also' references

**Affected files:**
- `docs/help/common/language/functions/val.md`
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
VAL function's 'See Also' section includes 'MID$ Assignment' which links to '../statements/mid-assignment.md', but the actual file shown in the documentation set is 'mid-assignment.md' without the hyphen. This creates a broken reference. Additionally, VAL lists many string manipulation functions in 'See Also' but doesn't list type conversion functions like CINT, CSNG, CDBL which are more directly related to VAL's purpose of converting strings to numbers.

---

#### documentation_inconsistency

**Description:** Index claims 45 intrinsic functions but actual count may differ

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/functions/val.md`
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
The language index states 'Functions - 45 intrinsic functions' but doesn't provide a complete list to verify this count. Given that some functions like VARPTR and USR are marked as not implemented, the actual count of working functions may be different. The index should clarify whether this count includes unimplemented functions.

---

#### documentation_inconsistency

**Description:** DEF FN documentation describes extension not in original MBASIC 5.21

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
The DEF FN documentation states that 'This implementation (extension): Function names can be multiple characters' but also claims to document MBASIC 5.21. The documentation should clearly indicate this is an extension beyond the original MBASIC 5.21 specification, not part of the original. The 'Syntax Notes' section mixes original behavior with extensions without clear separation.

---

#### documentation_inconsistency

**Description:** Operators documentation references non-existent data-types.md file

**Affected files:**
- `docs/help/common/language/operators.md`
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
The operators.md 'See Also' section includes a link to 'Data Types - Variable types and declarations' with path 'data-types.md', but this file is not included in the provided documentation set. The DEFINT/SNG/DBL/STR documentation also references '../data-types.md' and '../variables.md' which are not present.

---

#### documentation_inconsistency

**Description:** Index claims 77 commands and statements but doesn't provide verification

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/statements/auto.md`
- `docs/help/common/language/statements/chain.md`
- `docs/help/common/language/statements/close.md`

**Details:**
The language index states 'Statements - 77 commands and statements' but doesn't provide a complete list to verify this count. Given that some statements like CALL, CLOAD, CSAVE are marked as not implemented or version-specific, the actual count of available statements may differ.

---

#### documentation_inconsistency

**Description:** END documentation claims CONT can resume execution after END, but this contradicts typical BASIC behavior where END terminates the program completely

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/stop.md`

**Details:**
end.md states: 'Can be continued with CONT (execution resumes at next statement after END)'

This is inconsistent with standard BASIC behavior where END terminates the program and CONT should not work. The documentation should clarify whether this implementation allows CONT after END, and if so, explain this non-standard behavior.

---

#### documentation_inconsistency

**Description:** GET documentation mentions INPUT# and LINE INPUT# can read from random file buffer, but this is not mentioned in FIELD or other random file documentation

**Affected files:**
- `docs/help/common/language/statements/field.md`
- `docs/help/common/language/statements/get.md`

**Details:**
get.md states: '**Note:** After a GET statement, INPUT# and LINE INPUT# may be used to read characters from the random file buffer.'

This capability is not mentioned in field.md or other random file documentation. This seems like an important feature that should be cross-referenced and explained more thoroughly.

---

#### documentation_inconsistency

**Description:** HELPSETTING is listed in index.md under Modern Extensions but SETSETTING is referenced as SET in the See Also

**Affected files:**
- `docs/help/common/language/statements/helpsetting.md`
- `docs/help/common/language/statements/index.md`

**Details:**
helpsetting.md references 'SETSETTING' in See Also:
'- [SETSETTING](setsetting.md) - Configure interpreter settings'

But index.md lists it as:
'- [SET](setsetting.md) - Configure interpreter settings'

The command name should be consistent - either SETSETTING or SET.

---

#### documentation_inconsistency

**Description:** LOAD documentation mentions CP/M .BAS extension behavior without clarifying implementation

**Affected files:**
- `docs/help/common/language/statements/load.md`

**Details:**
load.md states:
'(With CP/M, the default extension .BAS is supplied.)'

This should clarify whether this Python implementation follows the same convention or not.

---

#### documentation_inconsistency

**Description:** OPEN documentation mentions mode 'A' for append is not documented, but PRINT# documentation references 'mode "A"' for append

**Affected files:**
- `docs/help/common/language/statements/open.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
OPEN.md syntax shows: '<mode> is a string expression whose first character is one of the following:
- "O" - specifies sequential output mode
- "I" - specifies sequential input mode
- "R" - specifies random input/output mode'
(No "A" mode listed)

PRINTI-PRINTI-USING.md: 'PRINT# writes data to a sequential file opened for output (mode "O") or append (mode "A")'

The OPEN documentation is missing the append mode.

---

#### documentation_inconsistency

**Description:** MERGE states it 'does NOT close open files' while RUN states it 'closes all files', but both return to command level - inconsistent behavior description

**Affected files:**
- `docs/help/common/language/statements/merge.md`
- `docs/help/common/language/statements/run.md`

**Details:**
MERGE.md: 'Open files: Unlike LOAD, MERGE does NOT close open files. Files that are open before MERGE remain open after MERGE completes.'

RUN.md: 'When RUN is executed:
- All variables are reset to zero or empty strings
- All open files are closed'

This is actually consistent behavior (MERGE keeps files open, RUN closes them), but the documentation could be clearer about why they differ.

---

#### documentation_inconsistency

**Description:** PUT documentation mentions using PRINT# and WRITE# with random files, but this is unusual and potentially confusing

**Affected files:**
- `docs/help/common/language/statements/put.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
PUT.md: '**Note:** PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer before a PUT statement.'

This is an advanced technique that mixes sequential and random file operations. The PRINT# documentation doesn't mention this capability. This cross-reference should be bidirectional or the PUT note should be expanded with warnings about when this is appropriate.

---

#### documentation_inconsistency

**Description:** SETSETTING and SHOWSETTINGS documentation missing HELPSETTING cross-reference

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/language/statements/showsettings.md`

**Details:**
Both setsetting.md and showsettings.md list HELPSETTING in their 'related' frontmatter and 'See Also' sections, but helpsetting.md file is not provided in the documentation set. The statements reference a command that appears to be missing from the documentation.

---

#### documentation_inconsistency

**Description:** WIDTH statement vs settings system overlap not explained

**Affected files:**
- `docs/help/common/language/statements/width.md`
- `docs/help/common/settings.md`

**Details:**
width.md states: 'WIDTH <integer expression>' is emulated as no-op and settings are 'silently ignored'
settings.md documents 'editor.tab_size' and other width-related settings that CAN be changed
The relationship between WIDTH statement (which does nothing) and actual width settings is not clarified. Users might be confused about how to actually control width.

---

#### documentation_inconsistency

**Description:** Variable case sensitivity documentation incomplete

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md states: 'Variable names are not case-sensitive by default (Count = COUNT = count), but the behavior when using different cases can be configured via the `variables.case_conflict` setting'
settings.md documents variables.case_conflict with choices: first_wins, error, prefer_upper, prefer_lower, prefer_mixed
However, variables.md doesn't explain what 'not case-sensitive by default' means in relation to these settings. Does 'first_wins' make them case-insensitive? The interaction is unclear.

---

#### documentation_inconsistency

**Description:** Settings storage location incomplete for project scope

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
settings.md states:
'Project scope - Settings for a specific project directory'
and
'Project: .mbasic/settings.json in project directory'
But it doesn't explain what defines a 'project directory' or how the system determines which directory is the project root. This is important for users to understand where their settings will be stored.

---

#### documentation_inconsistency

**Description:** Implementation note contradicts statement purpose

**Affected files:**
- `docs/help/common/language/statements/wait.md`

**Details:**
wait.md has an 'Implementation Note' stating:
'⚠️ **Not Implemented**: This feature requires direct hardware I/O port access and is not implemented'
'**Behavior**: Statement is parsed but no operation is performed'
But the 'Purpose' section still describes it as if it works: 'To suspend program execution while monitoring the status of a machine input port.'
The documentation should clarify upfront that this is a historical reference only and the statement doesn't function.

---

#### documentation_inconsistency

**Description:** Inconsistent description of PEEK behavior between architecture.md and compatibility.md

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states: 'PEEK: Returns random integer 0-255 (for RNG seeding compatibility)'

compatibility.md states: 'PEEK: Returns random integer 0-255 (for RNG seeding compatibility)'

Both documents agree on the behavior, but architecture.md includes this in 'Hardware Compatibility Notes' section while compatibility.md includes it under 'Intentional Differences > Hardware-Specific Features'. The placement and context differ slightly, which could cause confusion about whether this is a compatibility note or an intentional difference.

---

#### documentation_inconsistency

**Description:** Web UI file persistence description inconsistency

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md states: 'Files stored in Python-side memory (not browser localStorage)' and 'Files persist only during browser session - lost on page refresh'

extensions.md does not mention the Web UI's file handling limitations at all in its 'Multiple User Interfaces' section, only listing it as 'Web - Browser-based IDE (⚠️ Extension)'

The compatibility.md provides detailed information about Web UI file limitations that should be cross-referenced or summarized in extensions.md for completeness.

---

#### documentation_inconsistency

**Description:** Debugging features availability inconsistency

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/features.md`

**Details:**
extensions.md states: 'BREAK - Breakpoint Management' with 'Availability: CLI (command form), Curses (Ctrl+B), Tk (UI controls)'

features.md under 'Debugging' lists: 'Breakpoints - Set/clear breakpoints (UI-dependent)' and 'Step execution - Execute one line at a time (UI-dependent)' and 'Variable watch - Monitor variables (UI-dependent)' and 'Stack viewer - View call stack (UI-dependent)'

The features.md uses vague '(UI-dependent)' notation while extensions.md provides specific UI availability. These should be consistent, with features.md either providing the same detail or referencing extensions.md.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for project name

**Affected files:**
- `docs/help/mbasic/architecture.md`

**Details:**
architecture.md uses 'MBASIC' throughout the document as the project name.

extensions.md states: 'This is MBASIC-2025, a modern implementation of Microsoft BASIC-80 5.21' and lists 'Project Names Under Consideration: MBASIC-2025, Visual MBASIC 5.21, MBASIC++, MBASIC-X'

The architecture.md should clarify which name is being used or reference the naming discussion in extensions.md.

---

#### documentation_inconsistency

**Description:** Unclear relationship between semantic analyzer and interpreter execution

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/architecture.md`

**Details:**
features.md states: 'The interpreter includes an advanced semantic analyzer with 18 optimizations' suggesting these optimizations are applied during interpretation.

architecture.md states: 'The semantic analyzer is production-ready and can be used for: Program analysis and optimization reports, Bug detection, Understanding program behavior, Future compilation when code generator is added'

This suggests the semantic analyzer is a separate analysis tool, not part of the runtime interpreter. The relationship between the analyzer and the interpreter's execution needs clarification.

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

**Description:** Inconsistent keyboard shortcut notation format

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md uses: '**^R**', '**^Q**', '**^F**' (caret notation)

index.md uses: 'Ctrl+F', 'Ctrl+A' (Ctrl+ notation)

Both formats refer to the same keys but use different notation styles throughout the curses documentation.

---

#### documentation_inconsistency

**Description:** Conflicting information about variable sort modes and their defaults

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/variables.md`

**Details:**
quick-reference.md states: 'Sort Modes:
- **Accessed**: Most recently accessed (read or written) - default, newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name - A to Z'

variables.md states: 'Press `s` to cycle through sort orders:
- **Accessed**: Most recently accessed (read or written) - shown first
- **Written**: Most recently written to - shown first
- **Read**: Most recently read from - shown first
- **Name**: Alphabetical by variable name'

The descriptions differ slightly ('default, newest first' vs 'shown first', 'A to Z' vs no direction specified).

---

#### documentation_inconsistency

**Description:** Inconsistent menu access shortcut documentation

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md shows: '**^U** | Show menu' under Global Commands

index.md doesn't mention ^U or Ctrl+U for menu access at all in the navigation keys table or tips section.

---

#### documentation_inconsistency

**Description:** Inconsistent command format for starting MBASIC

**Affected files:**
- `docs/help/ui/tk/index.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
index.md shows: 'mbasic --ui tk [filename.bas]'

getting-started.md shows: 'mbasic --ui tk [filename.bas]' but also 'mbasic [filename.bas]' with note 'Or to use the default curses UI'

This creates confusion about what the default UI actually is, since the tk/index.md is specifically for TK documentation.

---

#### documentation_inconsistency

**Description:** Incomplete variable window keyboard shortcuts documentation

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
variables.md shows extensive keyboard reference table with keys like 's', 'd', 'f', '/', 'r', 'u', 'e', 'h', 'v', 't', 'w', 'p', 'q'

quick-reference.md only documents: 's' (sort), 'd' (direction), 'f' (filter), '/' (search)

Many documented shortcuts in variables.md are missing from the quick-reference, making it incomplete.

---

#### documentation_inconsistency

**Description:** Inconsistent feature count claims

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md title states: 'This document covers all 37 features available in the Tkinter (Tk) UI.'

Counting the documented features:
- File Operations: 8
- Execution & Control: 6
- Debugging: 6
- Variable Inspection: 6
- Editor Features: 7
- Help System: 4
Total: 37 features

However, features.md doesn't claim a specific number and presents a subset of 'Essential' features, which could cause confusion about completeness.

---

#### documentation_inconsistency

**Description:** Referenced file does not exist

**Affected files:**
- `docs/help/ui/tk/index.md`
- `docs/help/ui/tk/tips.md`

**Details:**
tk/index.md references: '[Tips & Tricks](tips.md) - Best practices and productivity tips'

The file tips.md is not provided in the documentation set, suggesting either missing documentation or an incorrect reference.

---

#### documentation_inconsistency

**Description:** Keyboard shortcut notation inconsistency

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
feature-reference.md uses placeholder notation: '{{kbd:run_program}}', '{{kbd:save_file}}', '{{kbd:smart_insert}}'

getting-started.md also uses: '{{kbd:run_program}}', '{{kbd:save_file}}', '{{kbd:smart_insert}}'

But feature-reference.md also uses explicit shortcuts: 'Ctrl+N', 'Ctrl+O', 'Ctrl+S', 'F5', 'F10'

Mixing placeholder notation with explicit shortcuts in the same document creates inconsistency.

---

#### documentation_inconsistency

**Description:** Contradictory information about auto-save functionality between getting-started.md and features.md

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/features.md`

**Details:**
getting-started.md states:
'**Note:** The Web UI uses browser downloads for saving files to your computer. Auto-save to browser localStorage is planned for a future release.'
'**Solution:** Auto-save to localStorage is planned for a future release. Currently, you need to manually save your programs using File → Save.'

But features.md under 'Local Storage' section states:
'**Currently Implemented:**
- Programs stored in Python server memory (session-only, lost on page refresh)
- Recent files list stored in browser localStorage'

And under 'Automatic Saving (Planned):' it says:
'- Saves programs to browser localStorage for persistence'

This creates confusion about whether localStorage is used at all currently, and what exactly is stored there.

---

#### documentation_inconsistency

**Description:** Inconsistent information about breakpoint functionality - debugging.md says 'currently implemented' but describes features as 'planned'

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
debugging.md states under 'Setting Breakpoints':
'### Currently Implemented
1. Use **Run → Toggle Breakpoint** menu option
2. Enter the line number when prompted
3. A visual indicator appears in the editor
4. Use **Run → Clear All Breakpoints** to remove all'

But then immediately says:
'**Note:** Advanced features like clicking line numbers to set breakpoints, conditional breakpoints, and a dedicated breakpoint panel are planned for future releases but not yet implemented.'

And later under 'Variable Inspector':
'**Implementation Status:** Basic variable viewing via Debug menu is currently available. The detailed variable inspector panels, watch expressions, and interactive editing features described below are **planned for future releases** and not yet implemented.'

This mixing of 'currently implemented' with extensive 'planned' sections makes it unclear what actually works.

---

#### documentation_inconsistency

**Description:** Self-contradictory statements about collaboration features in features.md

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
features.md under 'Session Management' section states:
'**Note:** Collaboration features (sharing, collaborative editing, version control) are not currently implemented. Programs are stored locally in browser storage only.'

But earlier in the same document under 'Local Storage' it says:
'**Currently Implemented:**
- Programs stored in Python server memory (session-only, lost on page refresh)'

These two statements contradict each other - one says 'browser storage', the other says 'Python server memory'. They describe different storage mechanisms.

---

#### documentation_inconsistency

**Description:** Debugging.md describes extensive planned features without clear separation from implemented features

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md has many sections marked '(Planned)' but the document structure makes it hard to distinguish what works now vs. what's planned:

- 'Variables Panel (Planned)' with detailed UI mockup
- 'Features (Planned)' with extensive feature lists
- 'Call Stack' section says 'not yet implemented' but then describes 'Stack Panel (Planned)' in detail
- 'Advanced Debugging (Planned Features)' section with conditional breakpoints, logpoints, data breakpoints, debug console, performance profiling
- 'Debug Settings' says 'planned for future releases' but then shows detailed 'Options Menu (Planned)'

The document would benefit from clearer separation between 'Currently Available' and 'Planned' sections at the top level.

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

But web-interface.md under Edit Menu states:
"- **Settings** - Configure auto-numbering, case handling, and other interpreter options"

This implies Settings is in the Edit menu, not a separate navigation bar icon. The two documents describe different UI locations for accessing Settings.

---

#### documentation_inconsistency

**Description:** Inconsistent instructions for loading files across library documentation

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/library/games/index.md`
- `docs/library/utilities/index.md`
- `docs/library/education/index.md`
- `docs/library/business/index.md`
- `docs/library/electronics/index.md`
- `docs/library/ham_radio/index.md`
- `docs/library/data_management/index.md`
- `docs/library/telecommunications/index.md`
- `docs/library/demos/index.md`

**Details:**
settings.md and web-interface.md use:
"**Load the file:**
   - **Web/Tkinter UI:** Click File → Open, select the downloaded file
   - **CLI:** Type `LOAD "filename.bas"`"

But most library index files (games, utilities, education, etc.) use:
"**Load the file:**
   - **Web/Tkinter UI:** Click File → Open, select the downloaded file
   - **CLI:** Type `LOAD "filename.bas"`"

However, some library files use 'Open the file' instead of 'Load the file' (business, electronics, ham_radio, data_management, telecommunications, demos). This creates inconsistent terminology across the documentation.

---

#### documentation_inconsistency

**Description:** Conflicting information about File menu Open Example feature

**Affected files:**
- `docs/help/ui/web/web-interface.md`

**Details:**
web-interface.md states under File Menu:
"- **Open** - Open a .bas file from your computer (via browser file picker)"

But then immediately after says:
"**Note:** An 'Open Example' feature to choose from sample BASIC programs is planned for a future release."

This suggests 'Open Example' is not yet implemented, but the extensive library documentation (docs/library/*) with 202 programs suggests example programs do exist. The inconsistency is whether these examples are accessible via the UI or only via manual download.

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

The guide then documents both systems extensively. However, the guide doesn't mention if there are any other case-sensitive elements in MBASIC (like file names, function names, etc.) that might have their own handling. This is complete as stated but could clarify if these are the ONLY two case handling systems.

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

**Description:** Inconsistent documentation about Step/Continue/Stop shortcuts

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md states 'Note: Step, Continue, and Stop are available via toolbar buttons or the Run menu (no keyboard shortcuts).' However, SETTINGS_AND_CONFIGURATION.md does not mention this limitation and the UI_FEATURE_COMPARISON.md shows 'Menu/Toolbar' for Tk debugging shortcuts, which is consistent with TK_UI_QUICK_START.md but the lack of keyboard shortcuts is not clearly documented in the comparison table.

---

#### documentation_inconsistency

**Description:** Inconsistent boolean value format in SET command examples

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md shows inconsistent boolean formats. In 'Quick Start' section: 'SET "editor.auto_number" true' (lowercase, no quotes). In 'SET Command' section: 'SET "editor.show_line_numbers" true' (lowercase, no quotes). But in 'Type Conversion' it says 'Booleans: true or false (lowercase, no quotes in commands; use true/false in JSON files)' which is consistent. However, the JSON examples show 'true' and 'false' without quotes, which is correct JSON but the note about 'use true/false in JSON files' is redundant since JSON booleans are always unquoted.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut for Save between UIs

**Affected files:**
- `docs/user/keyboard-shortcuts.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
keyboard-shortcuts.md (Curses UI) shows 'Ctrl+V' for 'Save program' and 'Shift+Ctrl+V' for 'Save As'. However, UI_FEATURE_COMPARISON.md shows 'Ctrl+S' for Save across all UIs in the 'Common Shortcuts' table. This is a significant inconsistency - Curses uses Ctrl+V while other UIs use Ctrl+S.

---

#### documentation_inconsistency

**Description:** Unclear scope precedence for settings

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states 'Settings are applied in this order (most specific wins): 1. File scope - Per-file settings (future feature) 2. Project scope 3. Global scope 4. Default'. However, it also states 'Note: Both methods are equivalent. SET commands affect the current session; JSON files persist across sessions.' This creates confusion about whether SET commands create a 5th scope level (session scope) that would override file/project/global, or if SET commands modify one of the existing scopes.

---

#### documentation_inconsistency

**Description:** Inconsistent line ending compatibility claims

**Affected files:**
- `docs/user/sequential-files.md`

**Details:**
sequential-files.md states 'This MBASIC implementation supports all three line ending formats for maximum cross-platform compatibility' and shows CRLF, LF, and CR all with '✅ Yes'. However, it also states 'MBASIC 5.21 line ending compatibility: ⚠️ More permissive (MBASIC only accepts CRLF)'. This creates confusion about whether the implementation is compatible with MBASIC 5.21 or intentionally different. The summary table shows this as a warning but doesn't clarify if this is a bug or intentional enhancement.

---

### 🟢 Low Severity

#### documentation_inconsistency

**Description:** Version number appears in setup.py but not consistently referenced in fix script

**Affected files:**
- `setup.py`
- `medium_severity_fixes.py`

**Details:**
setup.py declares version='0.99.0' with comment '# Reflects ~99% implementation status (core complete)'

The medium_severity_fixes.py script references 'MBASIC 5.21' throughout but doesn't reference the package version 0.99.0. While not strictly an inconsistency, the fix script's header could mention the package version for clarity.

---

#### code_vs_comment

**Description:** LineNode docstring claims 'intentionally does not have a source_text field' but design note seems defensive

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring states:
'Design note: This class intentionally does not have a source_text field to avoid maintaining duplicate copies that could get out of sync with the AST during editing. Text regeneration is handled by the position_serializer module which reconstructs source text from statement nodes and their token information.'

The phrase 'intentionally does not have' followed by a justification suggests this might have been a point of contention or confusion. The comment is clear but the defensive tone suggests there may have been alternative designs considered. Not a true inconsistency but worth noting for context.

---

#### code_vs_comment

**Description:** CallStatementNode has 'arguments' field that parser never populates

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode docstring states:
'Note: The "arguments" field is reserved for potential future compatibility with other BASIC dialects (e.g., CALL ROUTINE(args)). The parser does not currently populate this field (always empty list). Standard MBASIC 5.21 only accepts a single address expression in the "target" field.'

This is a code smell rather than an inconsistency - having a field that is documented as 'always empty list' suggests the data structure may be over-engineered. However, the documentation is honest about this, so it's more of a design question than an inconsistency.

---

#### documentation_inconsistency

**Description:** TypeInfo class docstring describes it as both a 'facade' and having 'backward compatibility' purpose

**Affected files:**
- `src/ast_nodes.py`

**Details:**
TypeInfo docstring states:
'This class provides a facade over VarType with two purposes:
1. Static helper methods for type conversions
2. Class attributes (INTEGER, SINGLE, etc.) that expose VarType enum values for backward compatibility with code that uses TypeInfo.INTEGER instead of VarType.INTEGER'

The term 'facade' typically means providing a simplified interface, but here TypeInfo is mainly providing backward compatibility aliases. The class attributes (INTEGER = VarType.INTEGER, etc.) are simple pass-throughs, not a facade. The static methods (from_suffix, from_def_statement) are the actual utility functions. The description could be clearer about the primary purpose being backward compatibility rather than abstraction.

---

#### code_vs_comment

**Description:** VarType docstring shows SINGLE as default but doesn't explain when default applies

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VarType enum docstring states:
'Types are specified by suffix characters or DEF statements:
- INTEGER: % suffix (e.g., COUNT%) or DEFINT A-Z
- SINGLE: ! suffix (e.g., VALUE!) or DEFSNG A-Z (default type)
- DOUBLE: # suffix (e.g., TOTAL#) or DEFDBL A-Z
- STRING: $ suffix (e.g., NAME$) or DEFSTR A-Z'

It says SINGLE is the 'default type' but doesn't explain when this default applies. The default is used when a variable has no suffix and no DEF statement applies to its first letter. This context would be helpful in the docstring.

---

#### code_vs_comment

**Description:** Comment about trailing_minus_only behavior is redundant and potentially confusing

**Affected files:**
- `src/basic_builtins.py`

**Details:**
At line 237, the comment states:
# trailing_minus_only: - at end only (always adds 1 char: - or space)
This same information is repeated in the docstring at lines 227-229. The inline comment adds '(always 1 char)' which could be clearer as 'always adds exactly 1 character position'.

---

#### code_vs_comment

**Description:** Comment about file handle access pattern is verbose and could be in docstring

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Lines 819-822 contain a detailed comment:
# self.runtime.files[file_num] returns a dict with 'handle', 'mode', 'eof' keys
# Extract the file handle from the file_info dict to perform read operations
# (this pattern is used by EOF(), LOC(), LOF(), and other file functions)

This implementation detail comment appears in the INPUT function but describes a pattern used throughout the class. It would be better as a class-level docstring or module documentation rather than buried in one function.

---

#### documentation_inconsistency

**Description:** Module docstring claims to document TAB, SPC, USING but doesn't mention other formatting functions

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Module docstring states:
Built-in functions for MBASIC 5.21.

BASIC built-in functions (SIN, CHR$, INT, etc.) and formatting utilities (TAB, SPC, USING).

But the module also implements STR$, SPACE$, STRING$ which are formatting utilities not mentioned in the docstring.

---

#### code_vs_comment

**Description:** Comment about file mode 'I' and binary read contradicts actual read operation

**Affected files:**
- `src/basic_builtins.py`

**Details:**
At line 743, comment states:
# File opened in binary mode ('rb') per mode 'I' check above
# read(1) returns bytes object; next_byte[0] accesses the first byte value as integer

This comment assumes the file was opened in binary mode 'rb', but this function doesn't open the file - it only checks if mode == 'I'. The actual file opening happens elsewhere (presumably in OPEN statement handler). The comment makes an assumption about implementation details not visible in this code.

---

#### code_vs_comment

**Description:** InMemoryFileHandle.flush() comment describes behavior that differs from typical file semantics

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The flush() method comment states:
"Note: This calls StringIO/BytesIO flush() which are no-ops. Content is only saved to the virtual filesystem on close(). This differs from file flush() semantics where flush() typically persists buffered writes. For in-memory files, all writes are already in memory, so flush() has no meaningful effect."

This is accurate documentation of the implementation, but creates an inconsistency with the FileHandle abstract interface which doesn't document this limitation. Code calling flush() on a FileHandle would expect standard flush semantics (immediate persistence), but InMemoryFileHandle silently defers until close(). This could cause data loss if the program crashes between flush() and close().

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for ProgramManager's relationship to Web UI

**Affected files:**
- `src/editing/manager.py`

**Details:**
The module docstring states:
"Note: Not suitable for Web UI due to direct filesystem access - Web UI uses FileIO abstraction in interactive.py instead."

But later in the same docstring:
"Why ProgramManager has its own file I/O methods:
...
- Web UI uses FileIO abstraction exclusively (no direct ProgramManager file access)"

The first statement says Web UI uses FileIO "in interactive.py" (specific file), while the second says Web UI uses FileIO "exclusively" (broader claim). The reference to "interactive.py" is also potentially confusing as that file is not included in the provided source files.

---

#### documentation_inconsistency

**Description:** Error code documentation mentions ambiguity but doesn't provide resolution guidance

**Affected files:**
- `src/error_codes.py`

**Details:**
The module docstring states:
"Note: Some two-letter codes are duplicated (e.g., DD, CN, DF) across different numeric error codes. This matches the original MBASIC 5.21 specification where the two-letter codes alone are ambiguous - the numeric code is authoritative."

Looking at ERROR_CODES dictionary:
- DD appears at codes 10 ("Duplicate definition"), 61 ("Disk full"), and 68 ("Device unavailable")
- CN appears at codes 17 ("Can't continue") and 69 ("Communication buffer overflow")
- DF appears at codes 25 ("Device fault") and 61 ("Disk full")

The documentation correctly identifies the ambiguity but doesn't explain how the system handles this in practice (e.g., does format_error() always use numeric codes to avoid ambiguity?).

---

#### documentation_inconsistency

**Description:** Help text formatting inconsistency in LIMITATIONS section

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The LIMITATIONS section has inconsistent bullet point formatting:
- First bullet: '• INPUT statement will fail...'
- Second bullet: '• Multi-statement lines...'
- Third bullet: '• GOTO, GOSUB...'
- Fourth bullet: '• DEF FN works...'
- Fifth bullet: '• Cannot execute...'

All use bullet points consistently, but the descriptions vary in style (some are warnings, some are capabilities). This is minor but could be more uniform.

---

#### documentation_inconsistency

**Description:** Module docstring claims Python 3.9+ syntax but uses standard typing

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Module docstring states:
'Note: This module uses Python 3.9+ type hint syntax (tuple[str, bool] instead of Tuple[str, bool]).'

However, the actual function signature at line 125 uses:
'def sanitize_and_clear_parity(text: str) -> tuple[str, bool]:'

This is indeed Python 3.9+ syntax (lowercase tuple), so the documentation is accurate. However, the note seems unnecessary since the code itself demonstrates this. This is a very minor documentation style issue.

---

#### code_vs_comment

**Description:** Help text describes INPUT behavior inconsistently with implementation details

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Help text line 334 states:
'• INPUT statement will fail at runtime in immediate mode (blocked when input() is called, not at parse time - use direct assignment instead)'

The OutputCapturingIOHandler.input() method at line 377 raises:
'raise RuntimeError("INPUT not allowed in immediate mode")'

The help text says 'blocked when input() is called' but the implementation 'raises RuntimeError'. The term 'blocked' suggests waiting or suspension, while 'raises RuntimeError' is an exception. The help text should say 'raises an error' or 'throws an exception' instead of 'blocked'.

---

#### code_vs_comment

**Description:** Comment about readline Ctrl+A binding may be misleading

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~127 says:
'# Bind Ctrl+A to insert the character instead of moving cursor to beginning-of-line
# This overrides default Ctrl+A (beginning-of-line) behavior.
# When user presses Ctrl+A, the terminal sends ASCII 0x01, and 'self-insert'
# tells readline to insert it as-is instead of interpreting it as a command.
# The \x01 character in the input string triggers edit mode (see start() method)'

However, this binding makes Ctrl+A insert a literal 0x01 character which is then checked in the start() method. This is unusual - most implementations would use a custom readline command or key binding callback. The comment is accurate but the approach is unconventional and could confuse maintainers.

---

#### code_vs_comment

**Description:** DELETE command docstring lists error handling that may not match implementation

**Affected files:**
- `src/interactive.py`

**Details:**
The cmd_delete docstring at line ~817 says:
'Error handling: ValueError is caught and displayed with "?" prefix,
all other exceptions are converted to "?Syntax error".'

But the actual exception handling at lines ~835-839 shows:
try:
    delete_lines_from_program(...)
except ValueError as e:
    print(f"?{e}")
except Exception as e:
    print(f"?Syntax error")

The second except block prints "?Syntax error" without including the exception message, which loses information. The docstring says 'converted to' which implies the error is transformed, but actually the original error is discarded.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of EDIT command escape character

**Affected files:**
- `src/interactive.py`

**Details:**
The cmd_edit docstring at line ~1042 shows:
'- I<text>$: Insert text ($ = Escape)'

But the _read_until_escape implementation at line ~1195 checks for both ESC and $:
if ch is None or ch == '\x1b' or ch == '$':  # ESC or $

The docstring only mentions $ as the escape character, not the actual ESC key (\x1b). This could confuse users who try to use the ESC key.

---

#### code_vs_comment_conflict

**Description:** Comment references 'see help text' for GOTO/GOSUB recommendation, but no help text is visible in the provided code to verify this claim.

**Affected files:**
- `src/interactive.py`

**Details:**
Comment line: 'Note: GOTO/GOSUB in immediate mode are not recommended (see help text)'

No help text is provided in the code snippet to verify what the help text actually says about GOTO/GOSUB in immediate mode.

---

#### code_vs_comment

**Description:** Comment about skip_next_breakpoint_check timing is unclear about when it's set vs when it's checked

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: "Set to True AFTER halting at a breakpoint (set after returning state)."

But the code in tick_pc() sets it to True when halting:
```python
if at_breakpoint:
    if not self.state.skip_next_breakpoint_check:
        self.runtime.halted = True
        self.state.skip_next_breakpoint_check = True
        return self.state
```

The comment suggests it's set "after returning state" but it's actually set before returning. The parenthetical "(set after returning state)" is misleading.

---

#### code_vs_comment

**Description:** Comment about string variables in FOR loops is misleading

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_for(), the docstring says:
"The loop variable typically has numeric type suffixes (%, !, #). The variable
type determines how values are stored. String variables ($) in FOR loops
would cause a type error when set_variable() attempts to store the numeric
loop value, so they are effectively not supported despite being parsed."

This comment suggests string variables are parsed but will fail at runtime. However, it's unclear if the parser actually allows string variables in FOR statements. The comment says "despite being parsed" but doesn't clarify if this is a parser bug or intentional behavior. This needs clarification about whether the parser should reject string variables in FOR loops or if the runtime error is the intended behavior.

---

#### documentation_inconsistency

**Description:** Comment mentions 'internal implementation version' tracked in src/version.py but this file is not shown in the provided code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in interpreter.py says:
"# OLD EXECUTION METHODS REMOVED
# Note: The project has an internal implementation version (tracked in src/version.py)
# which is separate from the MBASIC 5.21 language version being implemented."

This references src/version.py which is not provided in the source files. Cannot verify if this file exists or what version information it contains.

---

#### code_vs_comment

**Description:** InterpreterState docstring mentions checking order but doesn't explain why input_prompt is checked during execution while error_info is set via exceptions

**Affected files:**
- `src/interpreter.py`

**Details:**
The docstring says:
"Note: The suggested checking order below is for UI code that examines state AFTER
execution completes. During execution (in tick_pc()), checks occur in this order:
1. pause_requested, 2. halted, 3. break_requested, 4. breakpoints,
5. statement execution (input_prompt set DURING execution, errors via exceptions)."

This mentions that input_prompt is set DURING execution and errors are via exceptions, but doesn't explain why this architectural difference exists. The comment could be clearer about the fact that input_prompt is set synchronously during statement execution (blocking the tick), while errors are caught and converted to error_info asynchronously.

---

#### code_vs_comment

**Description:** Comment in execute_resume says 'Parser preserves the distinction (None vs 0)' but this is implementation detail that may not be accurate without seeing parser code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: 'RESUME or RESUME 0 - retry the statement that caused the error
Note: Parser preserves the distinction (None vs 0) for accurate source text regeneration, but the interpreter treats both identically at runtime.'

Code: if stmt.line_number is None or stmt.line_number == 0:

Without seeing the parser code, we cannot verify if the parser actually preserves this distinction or if the comment is outdated.

---

#### code_vs_comment

**Description:** Comment in execute_input describes state machine steps but step numbering doesn't match actual flow

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says:
'State machine for keyboard input (file input is synchronous):
1. If state.input_buffer has data: Use buffered input (from provide_input())
2. Otherwise: Set state.input_prompt, input_variables, input_file_number and return (pauses execution)
3. UI calls provide_input() with user's input line
4. On next tick(), buffered input is used (step 1) and state vars are cleared'

Step 4 says 'state vars are cleared' but the clearing happens at the end of execute_input after processing, not 'on next tick()'. The state vars are cleared in the same execution that processes the input, not on a subsequent tick.

---

#### code_vs_comment

**Description:** Comment in execute_run says 'RUN without args sets halted=True to stop current execution' but doesn't explain why this is different from RUN line_number

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: 'Note: RUN without args sets halted=True to stop current execution.
The caller (e.g., UI tick loop) should detect halted=True and restart
execution from the beginning if desired. This is different from
RUN line_number which sets halted=False to continue execution inline.'

The comment explains the difference but doesn't explain WHY they behave differently. RUN without args delegates to interactive_mode.cmd_run() which presumably handles the restart, while RUN line_number does inline restart. The asymmetry is documented but not justified.

---

#### code_vs_comment

**Description:** Comment in execute_field describes LSET/RSET usage but these statements are not shown in the provided code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: 'After FIELD, use GET/PUT to read/write records, and LSET/RSET to
modify field variable values before PUT.'

The code shows execute_get and execute_put but no execute_lset or execute_rset methods are visible in the provided code. This may be because the code is truncated (part 2 of interpreter.py), but the comment references functionality not shown.

---

#### code_vs_comment

**Description:** Comment in execute_midassignment says 'start_idx == len(current_value) is considered out of bounds' but this is standard behavior, not a special case

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: "Note: start_idx == len(current_value) is considered out of bounds (can't start replacement past end)"
This is just explaining that you can't start at position beyond the string length, which is obvious from the condition start_idx >= len(current_value). The comment is redundant but not incorrect.

---

#### code_vs_comment

**Description:** Comment in evaluate_functioncall explains debugger_set=True usage but the reasoning is verbose and could be clearer

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment: "Note: get_variable_for_debugger() and debugger_set=True are used to avoid
triggering variable access tracking. This save/restore is internal function
call machinery, not user-visible variable access. The tracking system
(if enabled) distinguishes between:
- User code variable access (tracked for debugging/variables window)
- Internal implementation details (not tracked)"

This is accurate but overly detailed. The key point is 'debugger_set=True avoids tracking internal function parameter save/restore'. The rest is explanation that could be in separate documentation.

---

#### code_vs_comment

**Description:** execute_lset and execute_rset have identical fallback comments but don't explain why fallback is needed

**Affected files:**
- `src/interpreter.py`

**Details:**
Both functions have: "Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field
variables (used with FIELD statement for random file access). This fallback
is a deliberate extension for compatibility with code that uses LSET for
general string formatting. This is documented behavior, not a bug."

The comment says 'for compatibility with code that uses LSET for general string formatting' but doesn't specify which BASIC dialect or programs need this. It's unclear what 'compatibility' means here if MBASIC 5.21 doesn't support it.

---

#### Documentation inconsistency

**Description:** Module docstring mentions CursesIOHandler but the actual class name in curses_io.py is CursesIOHandler (correct), however the import statement uses 'from .curses_io import CursesIOHandler' which is correct. No actual inconsistency, but worth noting the module is named curses_io.py not cursesio.py.

**Affected files:**
- `src/iohandler/__init__.py`

**Details:**
The __init__.py correctly imports:
from .curses_io import CursesIOHandler

This is consistent with the actual file name 'curses_io.py' and class name 'CursesIOHandler'.

---

#### Code vs Comment conflict

**Description:** The input_char() method's fallback for Windows without msvcrt has a comment describing severe limitations, but the implementation doesn't fully match the warning

**Affected files:**
- `src/iohandler/console.py`

**Details:**
Comment says:
                    # Fallback for Windows without msvcrt: use input() with severe limitations
                    # WARNING: This fallback calls input() which:
                    # - Waits for Enter key (defeats the purpose of single-char input)
                    # - Returns the entire line, not just one character
                    # This is a known limitation when msvcrt is unavailable.
                    # For proper single-character input on Windows, msvcrt is required.
                    line = input()
                    return line[:1] if line else ""

The comment says it 'Returns the entire line, not just one character' but the code actually does 'return line[:1]' which returns only the first character. The comment is misleading about what the code does, though the limitation about waiting for Enter is accurate.

---

#### Documentation inconsistency

**Description:** The input_line() documentation in base.py describes a 'KNOWN LIMITATION' about not preserving leading/trailing spaces, and this is repeated in console.py, curses_io.py, and web_io.py. However, the specific platform limitations differ slightly between implementations but all reference the same base.py documentation.

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/console.py`
- `src/iohandler/curses_io.py`
- `src/iohandler/web_io.py`

**Details:**
base.py states:
        KNOWN LIMITATION (not a bug - platform limitation):
        Current implementations (console, curses, web) CANNOT fully preserve
        leading/trailing spaces due to underlying platform API constraints:
        - console: Python input() strips trailing newline/spaces
        - curses: getstr() strips trailing spaces
        - web: HTML input fields strip spaces

Each implementation file repeats:
        Note: Current implementation does NOT preserve leading/trailing spaces
        as documented in base class. [specific reason]. This is a known limitation - see input_line() documentation in base.py.

This is consistent documentation, not an inconsistency. Marking as low severity for completeness.

---

#### Code vs Documentation inconsistency

**Description:** KeywordCaseManager docstring mentions it is used by parser.py and position_serializer.py, but these files are not provided to verify this claim

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
Module docstring states:
Note: This class provides advanced case policies (first_wins, preserve, error) via
CaseKeeperTable and is used by parser.py and position_serializer.py.

Neither parser.py nor position_serializer.py are included in the provided files, so this cannot be verified.

---

#### Code vs Documentation inconsistency

**Description:** KeywordCaseManager uses CaseKeeperTable but this class is imported from src.case_keeper which is not provided in the source files

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
keyword_case_manager.py imports:
from src.case_keeper import CaseKeeperTable

The file src/case_keeper.py (or src/case_keeper/__init__.py) is not provided, so the CaseKeeperTable implementation and its policy handling cannot be verified for consistency.

---

#### Code vs Comment conflict

**Description:** The get_char() backward compatibility alias comment states it preserves non-blocking behavior, but the original implementation's blocking behavior is not documented or verifiable

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment in web_io.py states:
        """Deprecated: Use input_char() instead.

        This is a backward compatibility alias. New code should use input_char().
        Note: Always calls input_char(blocking=False) for non-blocking behavior.
        The original get_char() implementation was non-blocking, so this preserves
        that behavior for backward compatibility.
        """

The claim about 'The original get_char() implementation was non-blocking' cannot be verified from the provided code, as no previous version is shown. This is a historical claim that may or may not be accurate.

---

#### code_vs_comment

**Description:** Comment in read_identifier() says 'Identifiers can contain letters, digits, and end with type suffix $ % ! #' but the code also allows periods in identifiers

**Affected files:**
- `src/lexer.py`

**Details:**
Comment says:
"Identifiers can contain letters, digits, and end with type suffix $ % ! #"

But code implementation allows periods:
while self.current_char() is not None:
    char = self.current_char()
    if char.isalnum() or char == '.':
        ident += self.advance()

The comment should mention that periods are also allowed (for Extended BASIC).

---

#### documentation_inconsistency

**Description:** Module docstring mentions 'MBASIC 5.21 (CP/M era MBASIC-80)' and 'Extended BASIC features' but doesn't clarify if Extended BASIC is the same as MBASIC 5.21 or a separate feature set

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring:
"Lexer for MBASIC 5.21 (CP/M era MBASIC-80)
Based on BASIC-80 Reference Manual Version 5.21

Note: MBASIC 5.21 includes Extended BASIC features (e.g., periods in identifiers)."

It's unclear if 'Extended BASIC' is a formal name for features in MBASIC 5.21 or if it refers to optional extensions.

---

#### code_vs_comment

**Description:** Comment in read_identifier() says 'Type suffix - only allowed at end of identifier' but the code breaks immediately after consuming the suffix, which is correct behavior but the comment could be clearer

**Affected files:**
- `src/lexer.py`

**Details:**
Comment says:
"# Type suffix - only allowed at end of identifier"

The code correctly breaks after consuming one suffix character:
elif char in ['$', '%', '!', '#']:
    ident += self.advance()
    break

The comment is accurate but could be more explicit that the break enforces this rule.

---

#### code_vs_comment

**Description:** Comment in tokenize() says 'Skip control characters gracefully' but the code raises an error for unexpected characters after skipping control characters

**Affected files:**
- `src/lexer.py`

**Details:**
Comment says:
"# Skip control characters gracefully"

But the code structure is:
if ord(char) < 32 and char not in ['\t', '\n', '\r']:
    self.advance()
    continue
raise LexerError(f"Unexpected character: '{char}' (0x{ord(char):02x})", start_line, start_column)

The comment is accurate - control characters are skipped. The error is raised for non-control unexpected characters. The comment placement might be confusing.

---

#### code_vs_comment

**Description:** Comment in parse_print() mentions optional comma after file number, but implementation behavior differs from comment description

**Affected files:**
- `src/parser.py`

**Details:**
Comment states:
"# Optionally consume comma after file number
# Note: MBASIC 5.21 typically uses comma (PRINT #1, "text").
# Our parser makes the comma optional for flexibility.
# If semicolon appears instead of comma, it will be treated as an item
# separator in the expression list below (not as a file number separator)."

However, the code only checks for comma:
"if self.match(TokenType.COMMA):
    self.advance()"

The comment suggests semicolon handling but the code doesn't explicitly handle semicolon after file number - it would fall through to the expression parsing loop where semicolon is treated as a separator. This is correct behavior but the comment could be clearer.

---

#### code_vs_comment

**Description:** Inconsistent comment about trailing separator behavior in parse_print()

**Affected files:**
- `src/parser.py`

**Details:**
Comment states:
"# Add newline if there's no trailing separator
# For N expressions: N-1 separators (between items) = no trailing separator
#                    N separators (between items + at end) = has trailing separator
if len(separators) < len(expressions):
    separators.append('\n')"

This logic adds a newline when separators < expressions, which means when there are N expressions and N-1 separators. However, the comment description is slightly confusing because it doesn't account for the case where there are 0 expressions (empty PRINT statement), which would result in len(separators) < len(expressions) being False (0 < 0 = False), so no newline would be added. This edge case behavior may not match the comment's intent.

---

#### documentation_inconsistency

**Description:** Incomplete parse_lprint() implementation with truncated code

**Affected files:**
- `src/parser.py`

**Details:**
The parse_lprint() function ends abruptly with:
"# Add newline if there's no trailing separator"

But the actual implementation code for adding the newline is missing (cut off). The function should have similar logic to parse_print() for handling trailing separators, but the code is incomplete in the provided file.

---

#### code_vs_comment

**Description:** Comment about ERR and ERL as system variables conflicts with their placement in expression parsing

**Affected files:**
- `src/parser.py`

**Details:**
In parse_primary(), the comment states:
"# ERR and ERL are system variables (integer type)
elif token.type in (TokenType.ERR, TokenType.ERL):
    self.advance()
    return VariableNode(
        name=token.type.name,  # 'ERR' or 'ERL'
        type_suffix='%',       # Integer type
        subscripts=[],
        ...
    )"

However, earlier in is_builtin_function(), there's a comment:
"# Note: ERR and ERL are not functions, they are system variables"

This is consistent, but the implementation creates a VariableNode with subscripts=[] (empty list) rather than subscripts=None. This differs from how simple variables are created in parse_variable_or_function() where subscripts=None is used for non-array variables. This inconsistency could cause issues in code that checks for array vs scalar variables.

---

#### code_vs_comment

**Description:** Inconsistent comment style for documenting AST node fields

**Affected files:**
- `src/parser.py`

**Details:**
Most parse methods (parse_print, parse_input, parse_goto, etc.) don't document field names in comments.
Only parse_showsettings() and parse_setsetting() have comments like "Field name: 'pattern'"
This creates inconsistency in documentation style across the parser.

---

#### code_vs_comment

**Description:** Comment about DEF FN function name normalization is unclear

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deffn() method:
Comment: "'DEF FNR' without space - identifier is 'fnr' (lexer already normalized to lowercase)"
Code: "function_name = 'fn' + raw_name  # Use lowercase 'fn' to match function calls"

If the lexer already normalized to lowercase, why does the code use lowercase 'fn' explicitly? This suggests either:
1. The comment is wrong and lexer doesn't normalize
2. The code is redundant
3. The normalization happens at different stages

---

#### code_vs_comment

**Description:** Comment about LPRINT separators is potentially misleading

**Affected files:**
- `src/parser.py`

**Details:**
In parse_lprint() method:
Comment: "# For N expressions: N-1 separators (between items) = no trailing separator
#                    N separators (between items + at end) = has trailing separator"

Then code: "if len(separators) < len(expressions):
    separators.append('\n')"

The comment explains the relationship but doesn't clarify that the code is normalizing the case where there's no trailing separator by adding a newline. This could be clearer.

---

#### code_vs_comment

**Description:** CALL statement docstring claims MBASIC 5.21 primarily uses simple numeric address form, but implementation fully supports extended syntax without any version-specific handling

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"MBASIC 5.21 syntax:
    CALL address           - Call machine code at numeric address

Extended syntax (for compatibility with other BASIC dialects):
    CALL ROUTINE(X,Y)      - Call with arguments

Note: MBASIC 5.21 primarily uses the simple numeric address form, but this parser fully supports both forms for broader compatibility."

However, the implementation treats both forms equally without any version checks or warnings. The comment suggests a distinction that doesn't exist in the code.

---

#### code_vs_comment

**Description:** WIDTH statement docstring describes device parameter but doesn't clarify what expressions are valid

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"Syntax: WIDTH width [, device]

Parses a WIDTH statement that specifies output width for a device.
Both the width and optional device parameters are parsed as expressions.

The parsed statement contains:
- width: Column width expression (typically 40 or 80)
- device: Optional device expression (typically screen or printer)"

The comment mentions 'typically screen or printer' but doesn't specify if these are string literals, identifiers, or numeric codes. The implementation just calls parse_expression() without validation.

---

#### code_vs_comment

**Description:** DEF FN comment about lexer normalization may be outdated or incorrect

**Affected files:**
- `src/parser.py`

**Details:**
In parse_def_fn() method, comment states:
"# raw_name already starts with lowercase 'fn' from lexer normalization"

However, earlier in the same method, there's code that strips type suffixes:
"type_suffix = self.get_type_suffix(raw_name)
if type_suffix:
    raw_name = raw_name[:-1]"

The comment about lexer normalization doesn't explain whether the lexer also handles type suffixes, or if this is purely parser responsibility. The relationship between lexer and parser responsibilities is unclear.

---

#### documentation_inconsistency

**Description:** OPEN statement docstring lists syntax variations but doesn't document which is preferred or canonical

**Affected files:**
- `src/parser.py`

**Details:**
The parse_open() docstring shows multiple syntax variations:
"Syntax variations:
- OPEN "R", #1, "FILENAME"
- OPEN "I", #1, "FILENAME"
- OPEN "O", #1, "FILENAME"
- OPEN "R", #1, "FILENAME", record_length
- OPEN filename$ FOR INPUT AS #1
- OPEN filename$ FOR OUTPUT AS #1
- OPEN filename$ FOR APPEND AS #1"

But doesn't indicate which syntax is 'classic' vs 'modern' (though the code comments do). The docstring should match the inline comments about syntax styles.

---

#### code_vs_comment

**Description:** Comment in serialize_let_statement mentions 'AssignmentStatementNode' as historical name but this creates confusion

**Affected files:**
- `src/position_serializer.py`

**Details:**
Comment states: 'In _adjust_statement_positions(), \'AssignmentStatementNode\' was used historically but has been replaced by \'LetStatementNode\' for consistency.'

However, _adjust_statement_positions() code only checks for 'LetStatementNode', not 'AssignmentStatementNode'. The comment references historical usage that may confuse readers looking at current code.

---

#### code_vs_comment

**Description:** Comment about operator positions says 'not tracked' but code uses None which could mean tracked-as-None vs not-tracked

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_let_statement: '# Equals sign (operator position not tracked - using None for column)'

The comment says 'not tracked' but the code explicitly passes None. This is ambiguous - does None mean 'no position info available' or 'position was never stored'? The emit_token function treats None as 'use pretty printing' which suggests it means 'no position info', but the comment phrasing is unclear.

---

#### documentation_inconsistency

**Description:** renumber_with_spacing_preservation docstring has redundant instruction about serialization

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring says: 'Text can then be regenerated from updated AST using serialize_line() (caller should call serialize_line() on each returned LineNode to regenerate text)'

And in Returns section: 'Dict of new_line_number -> LineNode (with updated positions)
Caller should serialize these LineNodes using serialize_line() to get text'

The same instruction is given twice in slightly different wording, which is redundant.

---

#### code_vs_comment

**Description:** Comment in serialize_expression says 'Only add type suffix if explicit' but doesn't explain what makes it explicit

**Affected files:**
- `src/position_serializer.py`

**Details:**
Code: '# Only add type suffix if explicit
if expr.type_suffix and getattr(expr, \'explicit_type_suffix\', False):'

The comment mentions 'explicit' but doesn't define what makes a type suffix explicit vs implicit. The code checks for an 'explicit_type_suffix' attribute but there's no documentation about when this is set or what it means.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology: 'MBASIC 5.21 compatibility' mentioned for max_string_length but no other MBASIC version references or compatibility notes elsewhere

**Affected files:**
- `src/resource_limits.py`

**Details:**
Lines with 'MBASIC 5.21 compatibility':
- Line ~35: max_string_length: int = 255,            # 255 bytes (MBASIC 5.21 compatibility)
- Line ~67: max_string_length: Maximum length for a string variable (bytes)
- Line ~330: max_string_length=255,              # 255 bytes (MBASIC 5.21 compatibility)
- Line ~349: max_string_length=255,              # 255 bytes (MBASIC 5.21 compatibility)
- Line ~368: max_string_length=1024*1024,        # 1MB strings (for testing/development - not MBASIC compatible)

The module documentation doesn't mention MBASIC compatibility as a design goal, and only string length has this specific version reference. This creates ambiguity about whether other limits are also meant to match MBASIC 5.21.

---

#### code_vs_comment

**Description:** Comment says 'DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21' but this is implementation detail that should be in interpreter.py, not resource_limits.py

**Affected files:**
- `src/resource_limits.py`

**Details:**
Comment at line ~177-178:
'# Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21
# This calculation matches the array creation logic in src/interpreter.py execute_dim()'

This comment describes interpreter behavior, not resource limit behavior. The resource_limits module should not need to know or document how DIM works - it should only calculate memory based on what the interpreter tells it. This suggests tight coupling or that the calculation logic might belong in interpreter.py instead.

---

#### code_vs_comment

**Description:** Docstring for estimate_size() says it handles 'VarType enum' but code only checks TypeInfo

**Affected files:**
- `src/resource_limits.py`

**Details:**
Docstring at line ~154:
'Args:
    value: The actual value (number, string, array)
    var_type: TypeInfo (INTEGER, SINGLE, DOUBLE, STRING) or VarType enum'

Code at lines ~159-169 only compares against TypeInfo:
'if var_type == TypeInfo.INTEGER:
    return 2
elif var_type == TypeInfo.SINGLE:
    return 4
...

No handling of VarType enum is present. Either the docstring is outdated or the implementation is incomplete.

---

#### code_vs_comment

**Description:** Comment says 'Import here to avoid circular dependency' but doesn't explain what the circular dependency is or why it exists

**Affected files:**
- `src/resource_limits.py`

**Details:**
Comment at line ~157:
'# Import here to avoid circular dependency
from src.ast_nodes import TypeInfo'

This suggests a design issue where resource_limits.py and ast_nodes.py depend on each other. The comment doesn't explain why this circular dependency exists or whether it should be refactored. This could indicate a code smell where TypeInfo should be in a separate module or the dependency structure needs review.

---

#### code_vs_comment

**Description:** Comment in dimension_array() says DIM is tracked as both read and write, but explanation is misleading

**Affected files:**
- `src/runtime.py`

**Details:**
In dimension_array():
"# Note: DIM is tracked as both read and write for debugger display purposes.
# Technically DIM is an allocation/initialization (write-only), but tracking it
# as both allows debuggers to show 'last accessed' info for unaccessed arrays."

The code sets both last_read and last_write to the same tracking_info, but the comment suggests this is for showing 'last accessed' info. However, if an array is never accessed after DIM, showing DIM as the 'last read' is misleading since DIM doesn't read the array.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'canonical case' vs 'original case'

**Affected files:**
- `src/runtime.py`

**Details:**
In _check_case_conflict() method, the return value is described as 'canonical case':
"Returns:
    str: The canonical case to use for this variable (might differ from original_case)"

But in get_variable() and set_variable(), the stored value is called 'original_case':
"self._variables[full_name]['original_case'] = canonical_case  # Store canonical case"

The field name 'original_case' suggests it stores the original case from source, but it actually stores the canonical case determined by the case conflict policy. This is confusing.

---

#### code_vs_comment

**Description:** Comment about error_handler tracking conflicts with actual usage

**Affected files:**
- `src/runtime.py`

**Details:**
In __init__:
"# Error handling registration (ON ERROR GOTO/GOSUB)
self.error_handler = None     # Line number for registered error handler
self.error_handler_is_gosub = False  # True if ON ERROR GOSUB, False if ON ERROR GOTO
# Note: Actual error state (occurred/active) is tracked in state.error_info, not here
# Runtime only stores the registered handler location, not whether an error occurred
# Error PC and details are stored in ErrorInfo (interpreter.py state)
# ERL%, ERS%, and ERR% system variables are set from ErrorInfo"

But then immediately after:
"# Initialize system variables ERR% and ERL% to 0
# These are integer type variables set by error handling code
self.set_variable_raw('err%', 0)
self.set_variable_raw('erl%', 0)"

The comment says ERR% and ERL% are set from ErrorInfo (in interpreter.py), but the code sets them in Runtime.__init__(). This suggests Runtime does track some error state, contradicting the comment.

---

#### documentation_inconsistency

**Description:** Incomplete docstring in get_all_variables() - example is cut off

**Affected files:**
- `src/runtime.py`

**Details:**
The get_all_variables() docstring has an incomplete example:
"Example:
    [
        {'name': 'counter', 'type_suffix': '%', 'is_array': False, 'value': 42,
         'original_case': 'Counter',
         'last_read': {'line': 20, 'position': 5, 'timestamp': 1234.567},
         'last_write': {'line': 10, 'position': 4, 'timestamp': 1234.500}},
        {'name': 'msg', 'type_suffix': '$', 'is_array': False, 'value': 'hello',
         'original_case': 'msg',"

The example is incomplete - the second dictionary entry is not closed, and the array is not closed.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for statement offset indexing in different docstrings

**Affected files:**
- `src/runtime.py`

**Details:**
In set_breakpoint() docstring:
"stmt_offset: Optional statement offset (0-based index). If None, breaks on entire line.
                        Ignored if line_or_pc is a PC object.
                        Note: offset 0 = 1st statement, offset 1 = 2nd statement, offset 2 = 3rd statement, etc."

In get_gosub_stack() docstring:
"Note: stmt_offset is a 0-based index where 0 = 1st statement, 1 = 2nd statement, etc."

Both describe the same concept (0-based indexing) but use slightly different phrasing. The first is more explicit with examples, while the second uses 'etc.' The terminology should be consistent across all methods dealing with statement offsets.

---

#### code_vs_comment

**Description:** Comment in parse_name() helper function describes behavior that may not match all cases

**Affected files:**
- `src/runtime.py`

**Details:**
The comment states:
"# No explicit suffix - default to single precision (!)
# Note: In _variables, all names should already have resolved type suffixes
# from _resolve_variable_name() which applies DEF type rules. This fallback
# handles edge cases where a variable was stored without a type suffix."

However, the function is used to parse names from both self._variables and self._arrays. The comment only discusses _variables behavior and doesn't mention whether arrays follow the same rules or if this fallback is actually needed for arrays. This could lead to confusion about whether arrays can be stored without type suffixes.

---

#### documentation_inconsistency

**Description:** get_loop_stack() marked as deprecated but no deprecation timeline or removal plan mentioned

**Affected files:**
- `src/runtime.py`

**Details:**
The method get_loop_stack() has a docstring:
"""Deprecated: Use get_execution_stack() instead."""

However, there's no information about:
- When it was deprecated
- When it might be removed
- Whether it's still safe to use
- What version introduced get_execution_stack() as replacement

This makes it unclear for users whether they need to urgently migrate or if this is a soft deprecation.

---

#### code_vs_comment_conflict

**Description:** Comment about load() behavior contradicts typical expectations but is intentional

**Affected files:**
- `src/settings.py`

**Details:**
In load() method, comment states: 'Implementation note: Settings are stored in flattened format on disk (e.g., {'editor.auto_number': True}) and save() uses _flatten_settings() to write them. However, load() intentionally does NOT call _unflatten_settings() - it keeps settings in flattened format after loading.'

This is unusual because there are both _flatten_settings() and _unflatten_settings() methods defined, but _unflatten_settings() is never called. The comment explains this is intentional because _get_from_dict() handles both formats, but having an unused method is confusing.

---

#### code_inconsistency

**Description:** Unused method _unflatten_settings() defined but never called

**Affected files:**
- `src/settings.py`

**Details:**
The method _unflatten_settings() is defined in SettingsManager class but is never called anywhere in the codebase. The load() method explicitly avoids calling it according to comments. This suggests either:
1. The method should be removed as dead code
2. The method is intended for future use
3. The load() implementation should use it

The comment in load() explains why it's not used, but having unused code is a maintenance burden.

---

#### documentation_inconsistency

**Description:** Comments about settings that don't exist are inconsistent with module purpose

**Affected files:**
- `src/settings_definitions.py`

**Details:**
At the end of SETTING_DEFINITIONS, there are comments:
'# Note: Tab key is used for window switching in curses UI, not indentation
# editor.tab_size setting not included - not relevant for BASIC

# Note: Line numbers are always shown - they're fundamental to BASIC!
# editor.show_line_numbers setting not included - makes no sense for BASIC'

These comments explain why certain settings DON'T exist. While informative, they're unusual in a definitions file - typically you document what IS there, not what ISN'T. This could confuse developers looking for these settings.

---

#### documentation_inconsistency

**Description:** Token dataclass note about field exclusivity is not enforced

**Affected files:**
- `src/tokens.py`

**Details:**
Token dataclass docstring says: 'Note: These fields serve different purposes and should be mutually exclusive (identifiers use original_case, keywords use original_case_keyword): - original_case: For identifiers (user variables) - preserves what user typed - original_case_keyword: For keywords - stores policy-determined display case. The dataclass doesn't enforce this exclusivity, but code should maintain it.'

This is a soft constraint documented but not enforced. If it's important enough to document, it might be worth enforcing with validation or a factory method. The current approach relies on developer discipline.

---

#### code_vs_documentation_inconsistency

**Description:** UIBackend subclasses listed in __init__.py don't match base.py documentation

**Affected files:**
- `src/ui/__init__.py`
- `src/ui/base.py`

**Details:**
src/ui/__init__.py lists: 'UIBackend', 'CLIBackend', 'VisualBackend', 'CursesBackend', 'TkBackend'

src/ui/base.py docstring lists: 'CLIBackend: Terminal-based REPL (interactive command mode), CursesBackend: Full-screen terminal UI with visual editor, TkBackend: Desktop GUI using Tkinter' and mentions 'Future/potential backend types (not yet implemented): WebBackend, HeadlessBackend'

The __init__.py includes 'VisualBackend' which is not mentioned in base.py's documentation. This could be an oversight or VisualBackend might be an alias/base class for visual UIs.

---

#### code_inconsistency

**Description:** CLIBackend replaces interactive's program manager but doesn't document why

**Affected files:**
- `src/ui/cli.py`

**Details:**
In CLIBackend.__init__():
'# Replace interactive's program manager with ours (for external control)
# This allows programmatic loading before start()
self.interactive.program = program_manager'

This replacement happens after InteractiveMode is created with io_handler. The comment says 'for external control' and 'allows programmatic loading before start()', but it's unclear why InteractiveMode can't just be initialized with the correct program_manager in the first place. This suggests either:
1. InteractiveMode constructor doesn't accept program_manager (API limitation)
2. There's a specific initialization order requirement
3. This is a workaround for a design issue

---

#### documentation_inconsistency

**Description:** Global settings path documentation has platform-specific inconsistency

**Affected files:**
- `src/settings.py`

**Details:**
Module docstring says: 'Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)'

But _get_global_settings_path() implementation shows:
'if os.name == 'nt':  # Windows
    appdata = os.getenv('APPDATA', os.path.expanduser('~'))
    base_dir = Path(appdata) / 'mbasic'
else:  # Linux/Mac
    base_dir = Path.home() / '.mbasic''

On Windows, if APPDATA is not set, it falls back to home directory, which would be ~/mbasic (not %APPDATA%/mbasic). The documentation doesn't mention this fallback behavior.

---

#### code_vs_comment_conflict

**Description:** Defensive programming comment suggests invalid policy values are possible

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
In SimpleKeywordCase.__init__():
'if policy not in ["force_lower", "force_upper", "force_capitalize"]:
    # Fallback for invalid/unknown policy values (defensive programming)
    policy = "force_lower"'

The comment says 'defensive programming' but there's no documentation about where invalid values could come from. If this is reading from user settings (settings.py), the settings validation should prevent invalid values. This suggests either:
1. Settings validation is insufficient
2. This class is used in contexts without validation
3. This is overly defensive code that could be an assertion instead

---

#### Code vs Documentation inconsistency

**Description:** The settings widget keypress handler comment states 'Ctrl+P is used for Cancel in the settings widget context (overrides editor's Parse Program binding)' but the curses_keybindings.json shows Ctrl+P is for 'Parse program' in the editor context. The comment correctly notes the override behavior, but there's no documentation of this modal override pattern elsewhere.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
curses_settings_widget.py comment:
"# Note: Ctrl+P is used for Cancel in the settings widget context (overrides
# editor's Parse Program binding). When the settings widget is open, Ctrl+P
# closes the settings dialog. This is intentional - modal dialogs can override
# editor keybindings while they have focus."

curses_keybindings.json:
"parse": { "keys": ["Ctrl+P"], "primary": "Ctrl+P", "description": "Parse program" }

The keybindings JSON doesn't document context-specific overrides or modal behavior.

---

#### Code vs Documentation inconsistency

**Description:** Settings widget footer shows 'ESC/^P=Cancel' suggesting both ESC and Ctrl+P cancel, but the keypress handler treats them identically without documenting why Ctrl+P is included as a cancel option when it conflicts with the editor's Parse command.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Footer text: "Enter=OK  ESC/^P=Cancel  ^A=Apply  ^R=Reset"

Keypress handler:
if key == 'esc' or key == 'ctrl p':
    self._on_cancel()
    return None

The dual binding is explained in a comment but not in user-facing documentation.

---

#### Code vs Comment conflict

**Description:** The _create_body() method comment says 'Create footer with keyboard shortcuts (instead of button widgets)' implying buttons were previously used, but there's no context for why this design choice was made or what changed.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment: "# Create footer with keyboard shortcuts (instead of button widgets)"

This suggests a refactoring occurred but the comment doesn't explain the rationale or previous implementation.

---

#### Code vs Documentation inconsistency

**Description:** The cmd_break() docstring states 'Breakpoints are only activated when the RUN command is executed' and 'After setting breakpoints, use RUN to start/restart the program for them to take effect', but doesn't explain what happens if breakpoints are set while a program is already running.

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
Docstring:
"Breakpoints are only activated when the RUN command is executed.
After setting breakpoints, use RUN to start/restart the program
for them to take effect."

The enhance_run_command() method installs breakpoint handlers, but there's no documentation of whether breakpoints can be added/removed during execution or only before RUN.

---

#### Code implementation issue

**Description:** The _create_setting_widget() method has a comment about using removeprefix() with a fallback for compatibility, but uses hasattr(str, 'removeprefix') which checks if the method exists on the str class, not if it's available in the current Python version. This is correct but the inline comment is verbose and could be clearer.

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Code:
# Use removeprefix to only strip from the beginning, not anywhere in the string
display_label = choice.removeprefix('force_') if hasattr(str, 'removeprefix') else (choice[6:] if choice.startswith('force_') else choice)

The comment explains the logic but the code is complex. The hasattr check is for Python 3.9+ compatibility.

---

#### code_vs_comment

**Description:** Comment at line 147 mentions 'fixed 5-character width' but this contradicts variable-width claim

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line 147 comment: "However, when reformatting pasted content, _parse_line_numbers uses fixed 5-character width
for alignment consistency. The keypress method uses _parse_line_number to find code boundaries
dynamically. The layout is a formatted string with three fields, not three columns."

This acknowledges the inconsistency but doesn't explain why both approaches exist or which is correct.

---

#### code_vs_comment

**Description:** Comment at line 964 mentions fixed 5-char width but actual behavior differs

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line 964 comment in _parse_line_numbers(): "Note: When reformatting pasted content, line numbers are right-justified to 5 characters
for consistent alignment. This differs from the variable-width formatting used in
_format_line() for display. The fixed 5-char width (lines 991, 1024) helps maintain
alignment when pasting multiple lines with different line number lengths."

This explicitly documents the inconsistency but doesn't explain if this is intentional design or a bug.

---

#### code_vs_comment

**Description:** Comment at line 1107 describes target_column as approximation but doesn't explain variable width handling

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line 1107 docstring: "target_column: Column to position cursor at (default: 7). This value is an
approximation for typical line numbers. Since line numbers have
variable width, the actual code area start position varies.
The cursor will be positioned at this column or adjusted based
on actual line content."

However, the code at line 1133 uses: new_cursor_pos = line_start + target_column without any adjustment logic for variable width.

---

#### code_vs_comment

**Description:** Comment about toolbar being removed conflicts with method still existing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in _create_ui() at line ~280 says: 'Toolbar removed from UI layout - use Ctrl+U menu instead for keyboard navigation (_create_toolbar method still exists but is not called)'

But the _create_toolbar() method at line ~240 has its own docstring saying: 'Note: This method is no longer used (toolbar removed from UI in favor of Ctrl+U menu for better keyboard navigation). The method is retained for reference and potential future re-enablement, but can be safely removed if the toolbar is not planned to return.'

Both comments say the same thing, which is consistent, but having the method present with a deprecation note while also having comments elsewhere about it being removed creates mild confusion.

---

#### code_vs_comment

**Description:** Comment says editor.lines is different object from editor_lines but both are dicts with same purpose

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~110 says: 'Note: self.editor_lines is the CursesBackend's storage dict self.editor.lines is the ProgramEditorWidget's storage dict (different object)'

Both are described as storage dicts for line_num -> text, suggesting they serve the same purpose but are separate objects. This creates confusion about why two separate storage mechanisms exist and which one is authoritative.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for step debugging commands

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The code uses multiple terms for the same stepping operations:
- Method names: _debug_step() and _debug_step_line()
- Menu handlers: _menu_step() and _menu_step_line()
- Comments: 'Step Statement' vs 'Stmt' (in toolbar comment)
- Status messages: 'Stepping...' vs 'Stepping line...'
- Key bindings: STEP_KEY and LIST_KEY (where LIST_KEY triggers step line)

The use of 'LIST_KEY' for step line operation is particularly confusing since LIST typically means listing program code, not stepping through it.

---

#### code_vs_comment

**Description:** Comment describes layout positions that may not match actual implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _toggle_variables_window() at line ~880:
Comment says: "# Layout: menu (0), editor (1), variables (2), output (3), status (4)"

In _toggle_stack_window() at line ~1020:
Comment says: "# Layout: menu (0), editor (1), [variables (2)], [stack (2 or 3)], output, status"

These comments describe the pile layout but don't account for dynamic insertion/removal. The second comment is more accurate with brackets indicating optional elements, but the first comment is misleading as it shows a static layout when variables/stack windows can be toggled.

---

#### code_vs_comment

**Description:** Comment about main widget storage is verbose and potentially confusing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_settings() at line ~820:
Comment says: "Main widget storage: Uses self.main_widget (stored in __init__) rather than
self.loop.widget (which might be a menu or other overlay)."

And again at line ~840:
"# Main widget storage: Use self.main_widget (stored at UI creation)
# not self.loop.widget (current widget which might be a menu or overlay)"

The same concept is explained twice in slightly different ways within the same method. This redundancy suggests the comment may have been added during debugging or refactoring and not cleaned up.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'variables window' vs 'watch window'

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The method _toggle_variables_window() uses the attribute self.watch_window_visible:
"self.watch_window_visible = not self.watch_window_visible"

But the method name and most references call it 'variables window'. The attribute name suggests it might have been called 'watch window' in an earlier version. This naming inconsistency could cause confusion.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'No state checking - just ask the interpreter' but this is misleading since has_work() likely checks internal state

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says:
"# Check if interpreter has work to do (after RUN statement)
# No state checking - just ask the interpreter
has_work = self.interpreter.has_work() if self.interpreter else False"

The comment 'No state checking' is misleading because calling has_work() IS checking state - it's just delegating the state check to the interpreter object rather than checking runtime.halted or similar flags directly.

---

#### code_internal_inconsistency

**Description:** Both _save_program and _save_as_program have identical implementations except for the initial filename prompt logic

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The two methods have nearly identical code blocks for:
- Parsing editor content
- Creating program content
- Writing to file
- Adding to recent files
- Storing current filename
- Cleaning up autosave
- Restarting autosave

The only difference is _save_program checks if self.current_filename exists before prompting, while _save_as_program always prompts. This duplication violates DRY principle.

---

#### documentation_inconsistency

**Description:** Comment about version macro references non-existent src/version.py file

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
In help_macros.py line 73, the comment states:
"# Hardcoded MBASIC version for documentation
# Note: Project has internal implementation version (src/version.py) separate from this"

This references 'src/version.py' but no such file is provided in the source code files. This could be outdated documentation if the file was removed, or the comment may be incorrect about where version information is stored.

---

#### code_vs_comment_conflict

**Description:** Comment about tier labels in search results doesn't match actual tier detection logic

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment in help_widget.py lines 127-129 states:
"# Map tier to labels for search result display
# Note: UI tier (e.g., 'ui/curses', 'ui/tk') is detected via startswith('ui/')
# check below and gets '📘 UI' label. Other unrecognized tiers get '📙 Other'."

However, the actual tier_labels dict (lines 130-133) only defines 'language' and 'mbasic' tiers. The comment mentions UI tier detection happens 'below', but the code at lines 148-151 shows:
"if tier_name.startswith('ui/'):
    tier_label = '📘 UI'
else:
    tier_label = tier_labels.get(tier_name, '📙 Other')"

The comment is accurate but could be clearer that the tier_labels dict is incomplete by design, with UI tiers handled separately via startswith() check.

---

#### code_inconsistency

**Description:** Inconsistent path separator handling in _load_topic() method

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
In help_widget.py _load_topic() method (lines 334-365), there are multiple path normalization steps:
- Line 348: "new_topic = target.replace('\\', '/')"
- Line 363: "new_topic = new_topic.replace('\\', '/')"

The code normalizes path separators to forward slashes twice in different branches. While this works, it suggests inconsistent handling. The first normalization (line 348) handles absolute paths from search results, while the second (line 363) handles relative paths. This duplication could be consolidated.

---

#### code_vs_comment_conflict

**Description:** Comment about 'absolute path' detection logic is misleading

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
In help_widget.py lines 339-341:
"# Check if target is already an absolute path (from search results)
# Absolute paths don't start with . or .., or start with common/
if not target.startswith('.') or target.startswith('common/'):"

The comment says 'absolute paths' but the logic actually detects 'help-root-relative paths'. True absolute paths would start with '/' or 'C:\'. The paths being detected here are relative to help_root (like 'common/file.md'), not absolute filesystem paths. The comment should say 'help-root-relative paths' instead of 'absolute paths'.

---

#### documentation_inconsistency

**Description:** Inconsistent key notation formats in documentation

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
STATUS_BAR_SHORTCUTS uses ^X notation: "MBASIC - ^F help  ^U menu  ^W vars  ^K step line  Tab cycle  ^Q quit"

But KEYBINDINGS_BY_CATEGORY uses Ctrl+ notation in QUIT_DISPLAY, MENU_DISPLAY, etc.

The keymap_widget.py has a _format_key_display() function to convert Ctrl+ to ^, but this conversion happens at display time, creating inconsistency in the source data.

---

#### documentation_inconsistency

**Description:** KEYBINDINGS_BY_CATEGORY includes keys not defined as constants in the module

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
KEYBINDINGS_BY_CATEGORY includes:
- 'Shift+Ctrl+V' for 'Save As'
- 'Shift+Ctrl+O' for 'Recent files'
- 's' and 'd' for Variables Window

But these keys are not defined as module-level constants like other keys (e.g., no SAVE_AS_KEY, RECENT_FILES_KEY, etc.). This creates inconsistency in how keys are documented vs. how they're defined in code.

---

#### code_vs_comment

**Description:** Comment about Ctrl+L being context-sensitive lacks corresponding code

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment at end of debugger section: "Note: Ctrl+L is context-sensitive in curses UI:
- When debugging: Step Line (execute all statements on current line)
- When editing: List program (same as LIST_KEY)"

However, there's no CTRL_L_KEY constant defined, and the comment references LIST_KEY which is actually bound to Ctrl+K (from 'step_line' action), not Ctrl+L. This appears to be outdated or incorrect documentation.

---

#### code_vs_comment

**Description:** HELP_KEY comment says 'mnemonic: F for Find help' but F typically means File or Forward

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment: "# Help system - use Ctrl+F (mnemonic: F for Find help)"

Ctrl+F is more commonly associated with 'Find' or 'Search' in most applications, not 'Find help'. The mnemonic explanation is weak and potentially confusing. A better mnemonic might be needed or the comment should acknowledge this is non-standard.

---

#### documentation_inconsistency

**Description:** MAXIMIZE_OUTPUT_KEY comment mentions change from Ctrl+O but doesn't explain why Ctrl+Shift+M was chosen

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Comment: "# Maximize output (for games/full-screen programs)
# Note: Changed from Ctrl+O to Ctrl+Shift+M to avoid conflict with Open (Ctrl+O)"

The comment explains why it was changed FROM Ctrl+O, but doesn't explain why Ctrl+Shift+M was chosen. M for Maximize is reasonable, but this isn't stated. Minor documentation gap.

---

#### code_vs_comment

**Description:** QUIT_ALT_KEY loaded from 'continue' action but used for quit functionality

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Code: _quit_alt_key = _get_key('editor', 'continue') or 'Ctrl+C'

Comment: # Alternative quit (Ctrl+C)

The key is loaded from the 'continue' action in the JSON config, but it's used as an alternative quit key. This naming mismatch between the JSON action name ('continue') and its actual use ('quit') is confusing.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for step operations in documentation

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
In KEYBINDINGS_BY_CATEGORY:
- LIST_DISPLAY is documented as 'Step Line - execute all statements on current line'
- STEP_DISPLAY is documented as 'Step Statement - execute one statement at a time'

But in STATUS_BAR_SHORTCUTS:
- Uses '^K step line' (lowercase, no hyphen)

The terminology should be consistent across all documentation strings.

---

#### Code vs Documentation inconsistency

**Description:** Return key binding for in-page search navigation not documented

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
In tk_help_browser.py line 126:
self.inpage_search_entry.bind('<Return>', lambda e: self._inpage_find_next())

The tk_keybindings.json documents Return key for 'Execute search (when in search box)' but does not document that Return also advances to the next match when in the in-page search box. This is a different behavior from the main search box.

---

#### Code duplication inconsistency

**Description:** Table formatting code is duplicated across files

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/markdown_renderer.py`

**Details:**
In tk_help_browser.py line 673-675:
def _format_table_row(self, line: str) -> str:
    """Format a markdown table row for display.

    Note: This implementation is duplicated in src/ui/markdown_renderer.py.
    Consider extracting to a shared utility module if additional changes are needed.
    """

The comment explicitly acknowledges code duplication with markdown_renderer.py. This creates a maintenance burden where changes to table formatting logic must be synchronized across multiple files.

---

#### Code vs Comment conflict

**Description:** Comment about modal behavior is misleading

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 48-49:
# Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())
self.transient(parent)
self.grab_set()

The comment states 'prevents interaction with parent, but doesn't block code execution - no wait_window()'. However, this is describing expected behavior rather than explaining why wait_window() is NOT called. The comment could be clearer about whether this is intentional design (non-blocking modal) or a potential issue.

---

#### Code vs Comment conflict

**Description:** Comment about tooltip is inaccurate

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 145-147:
else:
    # Show short help as inline label (not a hover tooltip, just a gray label)
    if defn.help_text:

The comment says 'not a hover tooltip, just a gray label' but this clarification seems unnecessary unless there was previous confusion or a tooltip implementation was considered. The comment may be outdated from a refactoring.

---

#### Documentation inconsistency

**Description:** Inconsistent documentation of link path resolution behavior

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In tk_help_browser.py line 289-292:
# Check if target is an absolute path (starts with / or contains :/)
# OR starts with common/ (common help paths should always be absolute)
# Absolute paths are relative to help root
if target.startswith('/') or target.startswith('common/') or ':/' in target or ':\\' in target:

The comment states 'common help paths should always be absolute' but then treats paths starting with 'common/' as absolute (relative to help root). This is confusing terminology - they are 'absolute' in the sense of being relative to help_root, not relative to current topic, but not absolute filesystem paths.

---

#### Code vs Comment conflict

**Description:** Comment about dismiss_menu helper placement is confusing

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In tk_help_browser.py line 621-623:
# Define dismiss_menu helper for ESC/FocusOut bindings (below)
def dismiss_menu():
    try:

The comment says 'for ESC/FocusOut bindings (below)' but the function is defined before it's used, not after. The comment should say '(used below)' or similar to match the actual code structure.

---

#### Code vs Comment conflict

**Description:** Comment about grab_release is misleading

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In tk_help_browser.py line 630-632:
# Release grab after menu is shown. Note: tk_popup handles menu interaction,
# but we explicitly release the grab to ensure clean state.
menu.grab_release()

The comment says 'Release grab after menu is shown' but tk_popup() is called in a try block and grab_release() is in the finally block. The grab_release() happens after the menu is dismissed, not just after it's shown. The comment is technically incorrect about timing.

---

#### code_vs_comment

**Description:** Comment says immediate_history and immediate_status are set to None but explains they are 'not currently used'

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines ~280-283:
"# Set immediate_history and immediate_status to None
# These attributes are not currently used but are set to None for defensive programming
# in case future code tries to access them (will get None instead of AttributeError)"

This suggests these attributes were planned or previously used but removed. The comment is defensive but could indicate incomplete refactoring or planned features.

---

#### code_vs_comment

**Description:** Comment about Ctrl+I binding location conflicts with actual implementation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _create_menu() at line ~447 says:
"# Note: Ctrl+I is bound directly to editor text widget in start() (not root window)
# to prevent tab key interference - see editor_text.text.bind('<Control-i>', ...)"

But in start() method around line ~200, the binding is:
self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)

The comment is accurate about the binding location, but the phrasing 'see editor_text.text.bind' suggests looking at a specific line that may not be obvious. This is minor but could be clearer.

---

#### documentation_inconsistency

**Description:** Docstring example shows ConsoleIOHandler but TkIOHandler is actually used

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring usage example at lines ~54-62:
"Usage:
    from src.iohandler.console import ConsoleIOHandler
    from src.editing.manager import ProgramManager
    from src.ui.tk_ui import TkBackend

    io = ConsoleIOHandler()
    def_type_map = {}
    program = ProgramManager(def_type_map)
    backend = TkBackend(io, program)
    backend.start()"

But in start() method around line ~300:
tk_io = TkIOHandler(self._add_output, self.root, backend=self)
self.interpreter = Interpreter(self.runtime, tk_io, limits=create_unlimited_limits())

The example shows ConsoleIOHandler being passed to TkBackend, but the actual implementation creates and uses TkIOHandler internally. The example is misleading about how the IO handler is used.

---

#### code_vs_comment

**Description:** Comment about click region handling is incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_variable_double_click() at line ~806:
"# Check if we clicked on a row (accept both 'tree' and 'cell' regions)
# 'tree' = first column area, 'cell' = other column areas
region = self.variables_tree.identify_region(event.x, event.y)
if region not in ('cell', 'tree'):
    return"

The comment explains 'tree' and 'cell' but doesn't mention what other regions exist or why they're rejected. This could be clearer about what regions are possible (e.g., 'heading', 'separator', 'nothing').

---

#### code_vs_comment

**Description:** Comment about formatting contradicts actual behavior in code

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~1050, comment states:
"# Insert line exactly as stored from program manager - no formatting applied here
# Note: Some formatting may occur elsewhere (e.g., variable display, stack display)
# This preserves compatibility with real MBASIC for program text"

However, throughout the file there are multiple places where formatting IS applied:
- Line ~450: Integer formatting without decimals for array subscripts
- Line ~520: Natural number formatting for FOR loop values
- Line ~850: Value formatting for variables display

The comment suggests no formatting occurs in the editor, but the note acknowledges formatting happens elsewhere. This is slightly contradictory - the comment should be clearer about what "no formatting applied here" means.

---

#### code_vs_comment

**Description:** Comment about type suffix extraction doesn't match all code paths

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~240, comment states:
"# Parse variable name (remove type suffix for runtime call)"

Then code does:
"if variable_name[-1] in '$%!#':
    base_name = variable_name[:-1]
    suffix = variable_name[-1]
else:
    base_name = variable_name
    suffix = None"

However, at line ~360 in _edit_array_element(), similar logic is used:
"base_name = variable_name[:-1] if variable_name[-1] in '$%!#' else variable_name
suffix = variable_name[-1] if variable_name[-1] in '$%!#' else None"

The logic is the same but written differently (ternary vs if/else). This inconsistency in style within the same file could indicate copy-paste without refactoring. Consider extracting to a helper method.

---

#### code_vs_comment

**Description:** Comment describes two cases for multi-line paste logic but the actual branching logic differs from description

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1230 says:
# Multi-line paste or single-line paste into blank line - use auto-numbering logic
# This handles two cases:
# 1. Multi-line paste (sanitized_text contains \n) - auto-number if needed
# 2. Single-line paste into blank line (current_line_text is empty) - auto-number if needed

However, the code flow doesn't explicitly check for case 2 (single-line paste into blank line). The code falls through to the multi-line logic after the inline paste check, but doesn't verify current_line_text is empty as the comment suggests. The comment implies a specific check for blank lines that isn't present.

---

#### code_vs_comment

**Description:** Comment says 'Schedule blank line removal after key is processed' but the scheduled function name is _remove_blank_lines which isn't defined in this file

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1195 says:
# Schedule blank line removal after key is processed
self.root.after(10, self._remove_blank_lines)

The method _remove_blank_lines is called but not defined in the visible portion of tk_ui.py. This could be defined elsewhere in the file, but the comment doesn't clarify this is a deferred call to a method that may or may not exist, creating uncertainty about whether this is dead code or a missing implementation.

---

#### code_vs_comment

**Description:** Docstring says _setup_immediate_context_menu is 'currently unused' but doesn't explain if it's ever called

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring states: "NOTE: This method is currently unused - immediate_history is always None in the Tk UI (see __init__). This is dead code retained for potential future use if immediate mode gets its own output widget."

However, the code doesn't show whether this method is called during initialization or not. If it's truly dead code, it should either be removed or the comment should clarify that it's never invoked.

---

#### documentation_inconsistency

**Description:** TkIOHandler docstring describes input strategy but implementation details don't fully match description

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Class docstring states: "Input strategy:
- INPUT statement: Prefers inline input field (when backend available), falls back to modal dialog
- LINE INPUT statement: Always uses modal dialog for consistent UX"

However, input_line() docstring says: "Unlike input() which prefers inline input field, this ALWAYS uses a modal dialog regardless of backend availability."

The second docstring adds 'regardless of backend availability' which is implied but not explicitly stated in the class docstring. While not contradictory, the class docstring could be clearer about the 'always' nature of LINE INPUT's modal dialog usage.

---

#### code_vs_comment

**Description:** Docstring for _on_status_click() says it shows 'breakpoint confirmation' but implementation shows 'breakpoint info' message

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring: "Handle click on status column (show error details for ?, breakpoint confirmation for ●)."

Implementation shows: messagebox.showinfo(f"Breakpoint on Line {line_num}", f"Line {line_num} has a breakpoint set.\n\nUse the debugger menu or commands to manage breakpoints.")

This is informational, not a confirmation dialog. The term 'confirmation' typically implies a yes/no dialog, but showinfo() only displays information.

---

#### documentation_inconsistency

**Description:** Class docstring describes 'automatic blank line removal' feature but doesn't mention it only triggers on cursor movement away from blank lines

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring states: "Automatic blank line removal:
- When cursor moves away from a blank line, that line is automatically deleted"

However, it doesn't clarify that this only happens when moving to a DIFFERENT line (checked by: if self.current_line is not None and self.current_line != new_line). Moving within the same line doesn't trigger removal. This is a minor omission but could be clearer.

---

#### code_vs_comment

**Description:** Comment in canvas creation says 'Width: 20 (pixels in Tkinter)' but doesn't clarify this is for the status column width, not per-character width

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment: "# Width: 20 (pixels in Tkinter) for one status character (●, ?, or space)"

Code: self.canvas = tk.Canvas(self, width=20, bg='#e0e0e0', highlightthickness=0)

The comment says '20 pixels for one status character' but this is the total canvas width, not a per-character calculation. The phrasing 'for one status character' could be misread as '20 pixels per character' when it means 'wide enough for one character'.

---

#### code_vs_comment

**Description:** Regex comment in _on_status_click() uses different pattern than _parse_line_number() without explanation

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_parse_line_number() uses: r'^(\d+)(?:\s|$)' with comment about requiring whitespace

_on_status_click() uses: r'^\s*(\d+)' which allows leading whitespace and doesn't check for trailing whitespace/end

The _on_status_click() regex is more permissive (allows leading whitespace, doesn't enforce trailing whitespace/end). No comment explains why different parsing rules are used in these two locations.

---

#### code_vs_comment

**Description:** Docstring for serialize_variable() shows example output 'x$' (lowercase) but doesn't explain case preservation logic

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring example:
>>> serialize_variable(var_node)
'x$'

But the code uses: text = getattr(var, 'original_case', var.name) or var.name

The example shows lowercase output, but the actual behavior depends on whether original_case is preserved. The docstring should clarify this behavior.

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No UI-framework dependencies' but doesn't mention the dependency on AST node types from parser module

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Module docstring states:
"No UI-framework dependencies (Tk, curses, web)
are allowed. Standard library modules (os, glob, re) and core interpreter
modules (runtime, parser, AST nodes) are permitted."

While it mentions 'AST nodes' are permitted, the extensive use of specific node types (LineNode, PrintStatementNode, GotoStatementNode, etc.) in serialize_statement() creates a tight coupling to the parser's AST structure. This should be more explicitly documented as a dependency.

---

#### code_vs_comment

**Description:** serialize_expression() docstring note about ERR/ERL doesn't explain why they're special or reference the relevant BASIC specification

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring note:
"Note:
    ERR and ERL are special system variables that are serialized without
    parentheses (e.g., 'ERR' not 'ERR()') when they appear as FunctionCallNode
    with no arguments, matching MBASIC 5.21 syntax."

This explains the behavior but not the reason. Are ERR/ERL parsed as function calls but should be serialized as variables? This seems like a parser/serializer mismatch that should be explained.

---

#### documentation_inconsistency

**Description:** renum_program() docstring describes renum_callback as being called for 'ALL statements' but doesn't explain why or what the callback should do for non-branching statements

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring states:
"renum_callback: Function that takes (stmt, line_map) to update statement references.
                Called for ALL statements; callback is responsible for identifying and
                updating statements with line number references (GOTO, GOSUB, ON GOTO,
                ON GOSUB, IF THEN/ELSE line numbers)"

Why is it called for ALL statements if only some have line references? This seems inefficient. Should the function filter first, or is there a reason to call it for every statement?

---

#### code_vs_comment

**Description:** serialize_statement() handles RemarkStatementNode with comment about REMARK conversion, but the conversion location isn't specified

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Code comment:
"# Preserve comments using original syntax (REM or ')
# Note: REMARK is converted to REM during parsing, not here"

This note suggests REMARK is converted during parsing, but doesn't reference where in the parser this happens. This makes it hard to verify the claim or understand the full comment handling flow.

---

#### documentation_inconsistency

**Description:** cycle_sort_mode() comment mentions 'Tk UI implementation' but this is supposed to be UI-agnostic code

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Comment states:
"The cycle order is: accessed -> written -> read -> name -> (back to accessed)
This matches the Tk UI implementation."

If this module provides 'consistent variable sorting behavior across all UI backends', it shouldn't reference a specific UI implementation. Either the comment should be removed or it should explain why Tk's order was chosen as the standard.

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
Line ~67-68 comment states:
# Note: The input echoing (displaying what user typed) is handled by the
# inline input handler in the NiceGUIBackend class, not here.

However, the NiceGUIBackend class code shown does not include the _enable_inline_input() method or any visible input echoing implementation that this comment references.

---

#### code_vs_comment

**Description:** Comment references method that doesn't appear in provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~60 comment states:
# prompt display via _enable_inline_input() method in the NiceGUIBackend class

The _enable_inline_input() method is not shown in the provided code excerpt of NiceGUIBackend class, making it unclear if this method exists or if the comment is outdated.

---

#### code_vs_comment

**Description:** Comment references line number that may be incorrect due to code truncation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1009 comment states:
# The _on_editor_change method (defined at line ~2609) handles:

This line number reference appears to be from a different version or complete file, as the provided code excerpt ends before line 2609. This suggests either the comment is outdated or the code is incomplete.

---

#### documentation_inconsistency

**Description:** Incomplete code excerpt makes verification of documented features impossible

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
The file header indicates this is 'part 1' of nicegui_backend.py, but critical methods referenced in comments are not included:
- _on_editor_change (referenced at line ~1009)
- _enable_inline_input (referenced at line ~60)
- Various menu handlers (_menu_run, _menu_stop, etc.)

This makes it impossible to verify consistency between the class docstring's feature list and actual implementation.

---

#### code_vs_comment

**Description:** Comment about Ctrl+C handling is misleading about where handling occurs

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~1858, comment states:
"Note on Ctrl+C handling (external to this method):
Ctrl+C interrupts are handled at the top level (in mbasic main, which wraps
start_web_ui() in a try/except)."

This comment suggests Ctrl+C is handled elsewhere, but provides no information about whether the web UI actually supports Ctrl+C interruption during program execution, or if this is a limitation of the web environment.

---

#### code_vs_comment

**Description:** Comment about interpreter/runtime reuse is unclear about when reuse occurs

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~2084 in _menu_step_stmt, comment states:
"# Create new IO handler for execution (interpreter/runtime reused to preserve session state)"

However, the code shows that runtime is conditionally created or reset:
"if self.runtime is None:
    self.runtime = Runtime(...)
else:
    self.runtime.reset_for_run(...)"

The comment suggests reuse always happens, but the code shows it's conditional. The comment is misleading about the actual behavior.

---

#### code_vs_comment

**Description:** Comment about char position retrieval contradicts actual code behavior

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line ~2180 in _handle_step_result, comment states:
"# Get char positions directly from statement_table (state properties return 0 when halted)"

However, earlier in the same method at lines ~2160-2161, the code successfully uses:
"char_start = state.current_statement_char_start if state.current_statement_char_start > 0 else None
char_end = state.current_statement_char_end if state.current_statement_char_end > 0 else None"

This suggests state properties do NOT always return 0 when halted, contradicting the comment's claim.

---

#### code_vs_comment

**Description:** Comment in _remove_blank_lines assumes cursor is at end, but acknowledges this may not be true

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment states: 'The last line is preserved even if blank, since it's likely where the cursor is after pressing Enter. This prevents removing the blank line user just created. Note: This assumes cursor is at the end, which may not always be true if user clicks elsewhere.'

The code preserves the last line unconditionally, but the comment admits the assumption may be wrong. This creates uncertainty about whether the behavior is correct.

---

#### code_vs_comment

**Description:** Comment in _save_editor_to_program mentions CP/M EOF marker but this seems unlikely in web context

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment states: '# Normalize line endings and remove CP/M EOF markers\n# \r\n -> \n (Windows line endings, may appear if user pastes text)\n# \r -> \n (old Mac line endings, may appear if user pastes text)\n# \x1a (Ctrl+Z, CP/M EOF marker - included for consistency with file loading)'

The \x1a (CP/M EOF) handling seems unnecessary in a web editor context where users are typing/pasting modern text. The comment says 'included for consistency with file loading' but doesn't explain why web editor needs this.

---

#### code_vs_comment

**Description:** Comment in _check_auto_number says 'Only auto-numbers a line once' but the logic checks if line existed in previous snapshot

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring states: 'Only auto-numbers a line once - tracks the last snapshot to avoid re-numbering lines while user is still typing on them.'

But the code checks: 'if stripped and (i < len(old_lines) or len(lines) > len(old_lines))'

This doesn't prevent numbering a line 'once' - it prevents numbering lines that are being actively typed. A line could be numbered multiple times if it's edited and then completed again. The comment is misleading about what 'once' means.

---

#### documentation_inconsistency

**Description:** Version number hardcoded in start_web_ui may not match actual version

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Code logs: sys.stderr.write(f"MBASIC Web UI Starting - Version {VERSION}\n")

But VERSION is imported from elsewhere. If VERSION is not kept in sync with actual releases, this could show incorrect version information to users.

---

#### documentation_inconsistency

**Description:** Inconsistent breakpoint toggle shortcuts between documents

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md states:
'Curses UI: Position cursor on the line and press b'
'Tk UI: Click the line number gutter next to the line Or position cursor on the line and press Ctrl+B'

editor-commands.md states:
'b | Ctrl+B | Toggle breakpoint (Curses: b, Tk: Ctrl+B)'

Both documents agree on the shortcuts, but editor-commands.md also lists 'b' as a top-level command for 'Load program' which conflicts with using 'b' for breakpoints in Curses UI.

---

#### code_vs_comment

**Description:** Deprecated class comment suggests using 'direct web URL' but no alternative implementation shown

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Comment states:
'# Legacy class kept for compatibility - new code should use direct web URL instead'
'# The help site is already built and served at http://localhost/mbasic_docs'

But there's no documentation or code showing how the help site is built, deployed, or served at that URL. The WebHelpLauncher_DEPRECATED class has methods for building with MkDocs and starting a server, but if it's deprecated, what's the replacement?

---

#### documentation_inconsistency

**Description:** Keyboard shortcut documentation inconsistency for opening help

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
editor-commands.md states:
'F1 or H | | Open help'

debugging.md does not mention H as a help shortcut, only references F1 in tips section:
'Press F1 with cursor on a BASIC keyword for context help'

Inconsistent whether H is a valid help shortcut across all UIs.

---

#### documentation_inconsistency

**Description:** Navigation instructions differ between help index pages

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/index.md`

**Details:**
index.md shows navigation:
'↑/↓ - Scroll up/down
Space - Page down
B - Page up
Enter - Follow link
U - Go back/up
Q or ESC - Exit help'

getting-started.md doesn't include navigation instructions, only references 'See your UI-specific help' without providing the same navigation guide.

---

#### code_vs_comment

**Description:** Function docstring describes behavior not implemented in function body

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
open_help_in_browser() docstring states:
'Check if a browser is available'
'Open in browser'

The function does check for browser availability and attempts to open, but it also writes debug output to stderr which is not mentioned in the docstring:
sys.stderr.write(f'BROWSER ERROR: No browser available - {e}\n')
sys.stderr.write(f'URL was: {url}\n')
sys.stderr.write(f'webbrowser.open() returned: {result}\n')

---

#### documentation_inconsistency

**Description:** Math functions appendix states ATN is evaluated in single precision, but ATN function doc doesn't mention precision limitations

**Affected files:**
- `docs/help/common/language/appendices/math-functions.md`
- `docs/help/common/language/functions/atn.md`

**Details:**
math-functions.md states: "(Note: ATN is evaluated in single precision, ~7 digits)"

atn.md states: "The expression X may be any numeric type, but the evaluation of ATN is always performed in single precision."

Both mention single precision, but the appendix adds a note about ~7 digits that could be confusing since it's in a comment about computing PI.

---

#### documentation_inconsistency

**Description:** Character set documentation lists control characters with different detail level than ASCII codes appendix

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
character-set.md shows abbreviated control character table:
| Code | Character | Usage |
|------|-----------|-------|
| 7 | BEL | Bell/beep: `PRINT CHR$(7)` |
| 8 | BS | Backspace |
...

ascii-codes.md shows complete table with abbreviations and full names:
| Dec | Hex | Abbr | Name | Description |
|-----|-----|------|------|-------------|
| 7 | 07 | BEL | Bell | Beep/alert sound |
| 8 | 08 | BS | Backspace | Move cursor left |

The character-set.md should reference the complete table in ascii-codes.md for consistency.

---

#### documentation_inconsistency

**Description:** Function index lists CVD, CVI, CVS and MKD$, MKI$, MKS$ separately but they are documented in combined files

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/cvi-cvs-cvd.md`
- `docs/help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md`

**Details:**
index.md shows:
"- [CVD, CVI, CVS](cvi-cvs-cvd.md) - String to number
- [MKD$, MKI$, MKS$](mki_dollar-mks_dollar-mkd_dollar.md) - Number to string"

And in alphabetical list:
"[CVD/CVI/CVS](cvi-cvs-cvd.md) | ... | [MKD$/MKI$/MKS$](mki_dollar-mks_dollar-mkd_dollar.md)"

The notation is inconsistent - sometimes comma-separated, sometimes slash-separated.

---

#### documentation_inconsistency

**Description:** FIX documentation states it's equivalent to SGN(X)*INT(ABS(X)) but doesn't show the difference clearly in examples

**Affected files:**
- `docs/help/common/language/functions/fix.md`
- `docs/help/common/language/functions/int.md`

**Details:**
fix.md states:
"FIX(X) is equivalent to SGN(X)*INT(ABS(X)). The major difference between FIX and INT is that FIX does not return the next lower number for negative X."

Example shows:
"PRINT FIX(58.75)
58
Ok
PRINT FIX(-58.75)
-58
Ok"

But int.md doesn't show a corresponding example with negative numbers to illustrate the difference. The cross-reference exists but the contrast isn't clear.

---

#### documentation_inconsistency

**Description:** Character set mentions underscore in variable names with qualifier 'some versions' but data-types doesn't mention this limitation

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/data-types.md`

**Details:**
character-set.md states:
"| **_** | Underscore | Allowed in variable names (some versions) |"

data-types.md states:
"Valid variable names:
- Start with a letter (A-Z)
- Can contain letters and digits
- Can end with type suffix ($, %, !, #)
- Maximum length varies by implementation"

No mention of underscore support or version-specific behavior in data-types.md.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of Control-C behavior between INKEY$ and INPUT$

**Affected files:**
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/input_dollar.md`

**Details:**
INKEY$ states: "Note: Control-C behavior varied in original implementations. In MBASIC 5.21 interpreter, Control-C would terminate the program. In the BASIC Compiler, Control-C was passed through. This implementation follows compiler behavior and passes Control-C through (CHR$(3)) for program detection and handling."

INPUT$ states: "Note: In MBASIC 5.21 interpreter, Control-C would interrupt INPUT$ and terminate the wait. This implementation passes Control-C through (CHR$(3)) for program detection and handling, matching compiler behavior."

Both describe the same behavior but with slightly different wording. INKEY$ mentions "terminate the program" while INPUT$ mentions "terminate the wait". The implementation behavior is the same (passing through), but the description of original behavior differs.

---

#### documentation_inconsistency

**Description:** INT function 'related' field references non-existent 'fix' function

**Affected files:**
- `docs/help/common/language/functions/int.md`

**Details:**
INT.md has:
related: ['fix', 'cint', 'csng', 'cdbl']

But the 'See Also' section correctly references FIX (uppercase). The 'related' field uses lowercase 'fix' which may not match the actual file naming convention if files are case-sensitive.

---

#### documentation_inconsistency

**Description:** Inconsistent 'related' field naming conventions across string functions

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

The 'related' fields use lowercase with underscores (e.g., 'right_dollar'), but the actual file names and references in 'See Also' sections use uppercase without underscores (e.g., 'RIGHT$'). This inconsistency in naming convention could cause broken links if the system is case-sensitive.

---

#### documentation_inconsistency

**Description:** Inconsistent formatting and detail level in 'Implementation Note' sections for non-implemented features

**Affected files:**
- `docs/help/common/language/functions/lpos.md`
- `docs/help/common/language/functions/inp.md`
- `docs/help/common/language/functions/usr.md`
- `docs/help/common/language/functions/peek.md`

**Details:**
Four functions have implementation notes for non-implemented features, but with varying levels of detail and formatting:

INP: Uses ⚠️ emoji, has 'Not Implemented' label, explains behavior and why
LPOS: Uses ⚠️ emoji, has 'Not Implemented' label, provides alternatives
USR: Uses ⚠️ emoji, has 'Not Implemented' label, minimal explanation
PEEK: Uses ℹ️ emoji (different!), has 'Emulated with Random Values' label (different status!), extensive explanation with limitations

PEEK is actually partially implemented (returns random values) rather than fully non-implemented like the others, but the inconsistent emoji usage (ℹ️ vs ⚠️) and section structure makes this distinction unclear.

---

#### documentation_inconsistency

**Description:** SPACE$ documentation references STRING$ equivalence but doesn't explain the relationship clearly

**Affected files:**
- `docs/help/common/language/functions/space_dollar.md`

**Details:**
SPACE$.md states:
"This is equivalent to STRING$(I, 32) since 32 is the ASCII code for a space character."

However, STRING$.md doesn't mention SPACE$ as a special case or provide a reciprocal reference. The relationship is one-way documented.

---

#### documentation_inconsistency

**Description:** INSTR documentation has inconsistent capitalization in error description

**Affected files:**
- `docs/help/common/language/functions/instr.md`

**Details:**
INSTR.md states:
"Note: If I=0 is specified, an 'Illegal function call' error will occur."

The error message is quoted as 'Illegal function call' but it's unclear if this is the exact error message (case-sensitive) that the interpreter produces. Other documentation doesn't consistently quote error messages, making it unclear if this is the exact string or a paraphrase.

---

#### documentation_inconsistency

**Description:** MID$ documentation has inconsistent error description compared to INSTR

**Affected files:**
- `docs/help/common/language/functions/mid_dollar.md`

**Details:**
MID$.md states:
"Note: If I=0 is specified, an 'Illegal function call' error will occur."

INSTR.md has the same note. However, MID$ allows J to be omitted but doesn't specify what happens if J=0. The documentation is incomplete about all error conditions.

---

#### documentation_inconsistency

**Description:** TAN documentation mentions overflow behavior but other trig functions don't

**Affected files:**
- `docs/help/common/language/functions/tan.md`

**Details:**
TAN.md states:
"If TAN overflows, the 'Overflow' error message is displayed, machine infinity with the appropriate sign is supplied as the result, and execution continues."

SIN.md and COS.md don't mention overflow behavior at all. This is inconsistent - either all trig functions should document their overflow behavior, or none should (if it's standard behavior).

---

#### documentation_inconsistency

**Description:** STR$ example code is incomplete with ellipsis comment

**Affected files:**
- `docs/help/common/language/functions/str_dollar.md`

**Details:**
STR$.md example has:
"100 PRINT 'Two digits'
110 RETURN
' ... (additional subroutines at 200, 300, 400, 500)"

This incomplete example with ellipsis is inconsistent with other documentation which provides complete, runnable examples.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting for unimplemented features

**Affected files:**
- `docs/help/common/language/functions/varptr.md`
- `docs/help/common/language/statements/call.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
VARPTR uses '⚠️ **Not Implemented**:' at the top with detailed explanation, while CALL and DEF USR place the implementation note after the syntax/purpose sections. CALL uses '⚠️ **Not Implemented**:' while DEF USR uses '## Implementation Note' as a separate section. The placement and formatting should be consistent across all unimplemented features.

---

#### documentation_inconsistency

**Description:** CLEAR documentation has confusing version-specific parameter explanations

**Affected files:**
- `docs/help/common/language/statements/clear.md`

**Details:**
The CLEAR documentation explains that 'In MBASIC 5.21 (BASIC-80 release 5.0 and later)' the parameters work one way, then provides a 'Historical note' about earlier versions. However, since this is documentation for MBASIC 5.21 specifically, the historical note creates confusion about which behavior is actually implemented. The current implementation behavior should be stated clearly first, with historical notes clearly marked as not applicable to this version.

---

#### documentation_inconsistency

**Description:** EDIT documentation describes traditional edit mode commands but states they're not implemented

**Affected files:**
- `docs/help/common/language/statements/edit.md`

**Details:**
The EDIT documentation lists traditional edit mode commands (I, D, C, L, Q, Space, Enter) but then states in the Implementation Note that 'The traditional single-character edit mode commands are not implemented.' This creates confusion about what EDIT actually does. The documentation should focus on what IS implemented rather than extensively documenting what is NOT implemented.

---

#### documentation_inconsistency

**Description:** DIM documentation has incomplete 'See Also' section

**Affected files:**
- `docs/help/common/language/statements/dim.md`

**Details:**
The DIM documentation's 'See Also' section only lists ERASE and OPTION BASE, but should also reference array-related topics like READ/DATA (which it mentions in the example), and possibly the data types documentation for understanding array element types.

---

#### documentation_inconsistency

**Description:** ERASE documentation has redundant implementation note

**Affected files:**
- `docs/help/common/language/statements/erase.md`

**Details:**
The ERASE documentation includes: '**Implementation Note:** This Python implementation of MBASIC fully supports the ERASE statement.'

This note is unnecessary as it doesn't indicate any deviation from standard behavior. If the statement is fully supported as documented, no implementation note is needed.

---

#### documentation_inconsistency

**Description:** ERR/ERL documentation has conflicting information about when ERR is reset

**Affected files:**
- `docs/help/common/language/statements/err-erl-variables.md`

**Details:**
The documentation states:
'- ERR is reset to 0 when:
  - RESUME statement is executed
  - A new RUN command is issued
  - An error handling routine ends normally (without error)'

But also states:
'- Both ERR and ERL persist after an error handler completes, until the next error or RESUME'

These two statements contradict each other regarding whether ERR persists after an error handler completes.

---

#### documentation_inconsistency

**Description:** FILES documentation mentions CP/M behavior but doesn't clarify if this applies to the Python implementation

**Affected files:**
- `docs/help/common/language/statements/files.md`

**Details:**
files.md states: '**Note**: CP/M automatically adds .BAS extension if none is specified for BASIC program files.'

The documentation should clarify whether this Python implementation mimics this CP/M behavior or not.

---

#### documentation_inconsistency

**Description:** FOR...NEXT documentation has unclear loop termination explanation

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
The documentation states:
'4. If variable exceeds ending value (y) considering STEP direction, loop terminates'

Then separately states:
'- Negative STEP counts backward (loop terminates when variable < end after increment)'
'- Positive STEP counts forward (loop terminates when variable > end after increment)'

The phrase 'after increment' is confusing - it should clarify whether the test happens before or after the increment on each iteration.

---

#### documentation_inconsistency

**Description:** GOSUB documentation example output formatting is inconsistent

**Affected files:**
- `docs/help/common/language/statements/gosub-return.md`

**Details:**
The example shows:
'Output:
```
SUBROUTINE IN PROGRESS
BACK FROM SUBROUTINE
```'

But the program has three separate PRINT statements in the subroutine (lines 40, 50, 60) that would produce 'SUBROUTINE  IN PROGRESS' with extra spaces, not 'SUBROUTINE IN PROGRESS'.

---

#### documentation_inconsistency

**Description:** GOTO example shows output with unusual formatting that doesn't match the code

**Affected files:**
- `docs/help/common/language/statements/goto.md`

**Details:**
The example shows:
'R = 5                AREA = 78.5'

But line 20 has 'PRINT "R =" :R,' which would produce 'R =5' (no space after =) and line 40 has 'PRINT "AREA =" :A' which would produce 'AREA =78.5'. The output shown has extra spaces that don't match the code.

---

#### documentation_inconsistency

**Description:** IF...THEN...ELSE documentation has unclear statement about GOTO between THEN and ELSE

**Affected files:**
- `docs/help/common/language/statements/if-then-else-if-goto.md`

**Details:**
The documentation states:
'- Cannot use GOTO between THEN and ELSE'

This is unclear. Does it mean you cannot have 'IF x THEN GOTO 100 ELSE ...'? Or does it mean something else? The restriction needs clarification.

---

#### documentation_inconsistency

**Description:** INPUT documentation mentions ?Redo from start message but doesn't explain when it occurs

**Affected files:**
- `docs/help/common/language/statements/input.md`

**Details:**
input.md states:
'- If too many values are entered, the extras are ignored with a ?Redo from start message'

This contradicts the statement that 'extras are ignored' - if they're ignored, why would there be a 'Redo from start' message? This needs clarification about the actual behavior.

---

#### documentation_inconsistency

**Description:** KILL documentation mentions CP/M behavior without clarifying if it applies to this implementation

**Affected files:**
- `docs/help/common/language/statements/kill.md`

**Details:**
kill.md states:
'**Note**: CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files.'

This should clarify whether the Python implementation mimics this behavior or not.

---

#### documentation_inconsistency

**Description:** LIST documentation has incomplete Remarks section

**Affected files:**
- `docs/help/common/language/statements/list.md`

**Details:**
The LIST documentation has an empty Remarks section:
'## Remarks


## Example'

This should either be removed or filled in with relevant information about LIST behavior.

---

#### documentation_inconsistency

**Description:** LSET example shows incorrect field positions in comment

**Affected files:**
- `docs/help/common/language/statements/lset.md`

**Details:**
The example comment states:
'30 LSET N$ = "JOHN DOE"'
'40 LSET A$ = "25"'

But then shows:
'N$ will contain "JOHN DOE            " (padded with spaces)'
'A$ will contain "25        " (padded with spaces)'

The field was defined as 20 characters for N$ and 10 for A$. 'JOHN DOE' is 8 characters, so it should be padded with 12 spaces, not the number shown. 'A$' should have 8 spaces, not 9.

---

#### documentation_inconsistency

**Description:** MERGE documentation states 'The file must have been SAVEd in ASCII format' but SAVE documentation uses 'SAVE' inconsistently - sometimes as 'SAVEd' (past tense with capital letters) and sometimes as 'saved' (lowercase)

**Affected files:**
- `docs/help/common/language/statements/merge.md`
- `docs/help/common/language/statements/save.md`

**Details:**
MERGE.md: 'The file must have been SAVEd in ASCII format'
SAVE.md: 'Otherwise, BASIC saves the file' (lowercase)
This is a minor stylistic inconsistency in terminology.

---

#### documentation_inconsistency

**Description:** PRINT documentation describes print zones as 14 columns, but PRINT# documentation states 'Items separated by commas are printed in print zones' without specifying the zone width

**Affected files:**
- `docs/help/common/language/statements/print.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
PRINT.md: 'When items are separated by commas, values are printed in zones of 14 columns each'
PRINTI-PRINTI-USING.md: 'Items separated by commas are printed in print zones' (no width specified)
The PRINT# documentation should clarify that zones are also 14 columns for consistency.

---

#### documentation_inconsistency

**Description:** MID$ Assignment documentation has inconsistent capitalization in the 'See Also' section

**Affected files:**
- `docs/help/common/language/statements/mid-assignment.md`

**Details:**
The 'See Also' section lists:
- 'ASC' - Returns a numerical value...
- 'CHR$' - Returns a one-character string...

But the descriptions use inconsistent capitalization:
- Some start with 'Returns' (capital R)
- Some start with 'Return' (capital R)
- Some start with 'Extract' (capital E)
- Some start with 'Convert' (capital C)

This is minor but shows inconsistent formatting in cross-references.

---

#### documentation_inconsistency

**Description:** NEW and RUN both claim to 'clear all variables' but use slightly different wording for what happens to files

**Affected files:**
- `docs/help/common/language/statements/new.md`
- `docs/help/common/language/statements/run.md`

**Details:**
NEW.md: 'To delete the program currently in memory and clear all variables' (no mention of files)

RUN.md: 'All variables are cleared and files are closed before execution begins'

NEW should clarify whether it closes files or not. Based on MERGE documentation stating 'Unlike LOAD, MERGE does NOT close open files', it's likely NEW does close files, but this should be explicit.

---

#### documentation_inconsistency

**Description:** ON...GOSUB/ON...GOTO documentation has inconsistent spacing in syntax examples

**Affected files:**
- `docs/help/common/language/statements/on-gosub-on-goto.md`

**Details:**
Syntax section shows:
'ON <expression> GOTO <list of line numbers>'
'ON <expression> GOSUB <list of line numbers>'

But example shows:
'100 ON L-1 GOTO 150,300,320,390'

The syntax uses spaces around angle brackets but the example has no spaces around the expression. This is minor but could be more consistent.

---

#### documentation_inconsistency

**Description:** NULL documentation has inconsistent spacing in example code

**Affected files:**
- `docs/help/common/language/statements/null.md`

**Details:**
Example shows:
'NULL 2
100 INPUT X
200 IF X<50 GOTO 800'

The NULL statement has no line number, but the following statements do. This might confuse readers about whether NULL is a direct command or can be used in programs. The documentation should clarify this is showing both direct mode and program usage.

---

#### documentation_inconsistency

**Description:** OPTION BASE documentation states 'Only one OPTION BASE statement is allowed per program' but doesn't specify what error occurs if multiple are used

**Affected files:**
- `docs/help/common/language/statements/option-base.md`

**Details:**
OPTION BASE.md: 'The OPTION BASE statement must appear before any DIM statements or array references in the program. Only one OPTION BASE statement is allowed per program.'

The documentation doesn't specify what error message appears if a second OPTION BASE is encountered. This would be helpful for users.

---

#### documentation_inconsistency

**Description:** POKE and OUT both have 'Implementation Note' sections with similar warnings, but use slightly different wording

**Affected files:**
- `docs/help/common/language/statements/poke.md`
- `docs/help/common/language/statements/out.md`

**Details:**
POKE.md: '⚠️ **Emulated as No-Op**: This feature requires direct memory access and cannot be implemented in a Python-based interpreter.'

OUT.md: '⚠️ **Emulated as No-Op**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.'

The wording differs slightly ('cannot be implemented' vs 'is not implemented'). These should use consistent language for similar situations.

---

#### documentation_inconsistency

**Description:** PRINT documentation shows '?' as an alias but doesn't fully explain its usage in the Remarks section

**Affected files:**
- `docs/help/common/language/statements/print.md`

**Details:**
PRINT.md shows in metadata: 'aliases: ['?']'

And mentions in Special Forms: '**?** - Shorthand for PRINT'

But the Remarks section doesn't explain that ? can be used anywhere PRINT is used. The example shows it, but explicit documentation would be clearer.

---

#### documentation_inconsistency

**Description:** RANDOMIZE documentation example shows inconsistent spacing in output

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
The example output shows:
'Random Number Seed (-32768 to 32767)? 3     (user types 3)'

The spacing before '(user types 3)' is inconsistent with typical documentation formatting. This is very minor but could be cleaned up.

---

#### documentation_inconsistency

**Description:** RENUM documentation has a duplicate line number in Example 6

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
Example 6 shows:
'1000 PRINT "OPTION 1"
1100 END
1100 PRINT "OPTION 2"
1200 END
1200 PRINT "OPTION 3"
1300 END'

Lines 1100 and 1200 appear twice each. This appears to be a typo in the example - the middle section should probably be:
'1000 PRINT "OPTION 1"
1100 END
1200 PRINT "OPTION 2"
1300 END
1400 PRINT "OPTION 3"
1500 END'

---

#### documentation_inconsistency

**Description:** RESUME documentation uses inconsistent formatting for error codes in the table

**Affected files:**
- `docs/help/common/language/statements/resume.md`

**Details:**
The 'Error Codes Reference' table shows:
'| ERR | Error |
|-----|-------|
| 2 | Syntax error |'

But earlier in examples, error codes are referenced as 'ERR = 11' or 'ERR = 8'. The table could include more context about when these errors occur to match the detail level of the examples.

---

#### documentation_inconsistency

**Description:** RUN documentation states 'File extension defaults to .BAS if not specified' but SAVE documentation says 'With CP/M, the default extension .BAS is supplied'

**Affected files:**
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/save.md`

**Details:**
RUN.md: 'File extension defaults to .BAS if not specified'

SAVE.md: '(With CP/M, the default extension .BAS is supplied.)'

The RUN documentation doesn't specify this is CP/M-specific, while SAVE does. They should be consistent about whether .BAS extension defaulting is universal or CP/M-specific.

---

#### documentation_inconsistency

**Description:** Inconsistent setting name format in examples

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/settings.md`

**Details:**
setsetting.md shows: 'SETSETTING display.width 80' and 'SETSETTING editor.tab_size 4'
settings.md shows the same settings but doesn't demonstrate the SETSETTING command syntax consistently. The settings.md file uses different formatting in its examples section.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-reference lists

**Affected files:**
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
stop.md 'See Also' includes: CONT, END, CHAIN, CLEAR, RUN, SYSTEM
system.md 'See Also' includes: CHAIN, CLEAR, COMMON, CONT, END, NEW, RUN, STOP
system.md includes COMMON and NEW which stop.md doesn't, creating asymmetric cross-references for related commands.

---

#### documentation_inconsistency

**Description:** Inconsistent file naming and cross-references

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md has title 'WRITE (Screen)' and references writei.md as 'WRITE#'
writei.md has title 'WRITE# (File)' and references write.md as 'WRITE'
The file naming convention (writei.md for WRITE#) is inconsistent with the statement name and could cause confusion.

---

#### documentation_inconsistency

**Description:** Example output formatting inconsistency

**Affected files:**
- `docs/help/common/language/statements/swap.md`

**Details:**
The SWAP example shows:
'LIST
              10 A$=" ONE " : B$=" ALL " : C$="FOR"
              20 PRINT A$ C$ B$'
with excessive leading whitespace that doesn't match the formatting style of other statement examples in the documentation set.

---

#### documentation_inconsistency

**Description:** Keyboard shortcuts documented in multiple places with potential conflicts

**Affected files:**
- `docs/help/common/shortcuts.md`
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
shortcuts.md shows: '^R - Run program', '^P - Show help', '^Q - Quit IDE'
curses/editing.md shows: 'Ctrl+R - Run program', 'Ctrl+N - New program', 'Ctrl+S - Save program', 'Ctrl+L - Load program', 'Ctrl+P - Help'
tk/index.md shows: 'Ctrl+N - New program', 'Ctrl+O - Open file', 'Ctrl+S - Save file', 'Ctrl+R - Run program', 'Ctrl+F - Find', 'F1 - Help'
The shortcuts are inconsistent across UIs (^P vs F1 for help, ^Q vs not mentioned for quit). This may be intentional UI differences but should be clarified.

---

#### documentation_inconsistency

**Description:** Example output formatting uses inconsistent spacing

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
The TRON-TROFF example shows:
'TRON
             Ok
             LIST
             10 K=lO'
with excessive leading whitespace (13 spaces) that doesn't match other examples in the documentation which typically use 0-4 spaces for indentation.

---

#### documentation_inconsistency

**Description:** Broken link reference in main index

**Affected files:**
- `docs/help/index.md`
- `docs/help/mbasic/index.md`

**Details:**
index.md references: '[Getting Started](mbasic/getting-started.md)'
But the actual path structure shows it should be under common: 'common/getting-started.md' based on other references in the documentation, or the file is missing from the provided documentation set.

---

#### documentation_inconsistency

**Description:** WIDTH implementation note has conflicting information

**Affected files:**
- `docs/help/common/language/statements/width.md`

**Details:**
width.md states:
'⚠️ **Emulated as No-Op**: This statement is parsed for compatibility but performs no operation.'
'**Behavior**: The simple "WIDTH <number>" statement parses and executes successfully without errors, but does not affect output width (settings are silently ignored).'
But then in 'See Also' it references SETSETTING which CAN change settings. The relationship between WIDTH (no-op) and actual width settings needs clarification.

---

#### documentation_inconsistency

**Description:** LPRINT statement support inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
features.md states: 'LPRINT - Line printer output (Note: LPRINT statement is supported, but WIDTH LPRINT syntax is not)'

compatibility.md states under 'Terminal Differences': 'Width statement: 10 WIDTH 80 // Accepted (no-op). Note: WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.'

The features.md note about WIDTH LPRINT is embedded in the LPRINT description, while compatibility.md discusses it under WIDTH. This could be clearer if both documents consistently explained that LPRINT works but WIDTH LPRINT does not.

---

#### documentation_inconsistency

**Description:** Confusing statement about Web UI uppercasing

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
compatibility.md states: 'Automatically uppercased by the virtual filesystem (CP/M style)' followed by 'The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage'

The second statement seems to be defending against a misinterpretation that wasn't clearly set up. The phrase 'not evidence of persistent storage' is confusing because uppercasing has nothing to do with persistence. This appears to be addressing a concern that wasn't clearly articulated.

---

#### documentation_inconsistency

**Description:** Missing Web UI in getting-started.md interface list

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/mbasic/features.md`

**Details:**
getting-started.md lists three interfaces under 'Choosing a User Interface': Curses UI, CLI Mode, and Tkinter GUI. It does not mention the Web UI.

features.md under 'User Interface Features' lists four interfaces: Curses UI, CLI Mode, Tkinter GUI, and Web UI.

The getting-started.md should include the Web UI option for completeness.

---

#### documentation_inconsistency

**Description:** Redundant information about line ending support

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
compatibility.md describes line ending support in two places:

1. Under 'Fully Compatible Features > File I/O': 'Line ending support: More permissive than MBASIC 5.21...'
2. Under 'Intentional Differences > Enhanced File Handling': 'Accepts LF, CR, or CRLF line endings (original only CRLF)'

The same information is presented twice with slightly different wording, which could be consolidated or cross-referenced.

---

#### documentation_inconsistency

**Description:** Installation instructions reference non-existent requirements.txt

**Affected files:**
- `docs/help/mbasic/getting-started.md`

**Details:**
getting-started.md states: '# Install optional dependencies
pip install -r requirements.txt'

However, no requirements.txt file is shown in the documentation files provided. This instruction may be incorrect or the file may be missing from the documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of 'MBASIC' vs 'mbasic'

**Affected files:**
- `docs/help/mbasic/architecture.md`

**Details:**
architecture.md uses both 'MBASIC' (capitalized) throughout most of the document and 'mbasic' (lowercase) in command examples like 'python3 mbasic --ui cli'.

While this may be intentional (uppercase for the product name, lowercase for the command), it should be explicitly clarified to avoid confusion.

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

**Description:** Different levels of detail for Find/Replace feature

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
features.md states: 'Find text (Ctrl+F):
- Opens Find dialog with search options
...
Replace text (Ctrl+H):
- Opens combined Find/Replace dialog
...
Note: Ctrl+F opens the Find dialog. Ctrl+H opens the Find/Replace dialog which includes both Find and Replace functionality.'

feature-reference.md states: 'Find/Replace (Ctrl+F / Ctrl+H)
Powerful search and replace functionality:
- Find: Ctrl+F
- Replace: Ctrl+H
- Find Next: F3
- Options: Case-sensitive, whole word, regex
- Replace single or all occurrences
- Search wraps around'

The note in features.md about Ctrl+H including Find functionality is not mentioned in feature-reference.md, creating potential confusion about whether there are separate dialogs.

---

#### documentation_inconsistency

**Description:** Settings documentation exists for curses but referenced for tk

**Affected files:**
- `docs/help/ui/curses/settings.md`
- `docs/help/ui/tk/settings.md`

**Details:**
curses/settings.md provides detailed documentation about the Settings Widget with keyboard shortcut Ctrl+,

tk/settings.md is referenced in tk/index.md ('Settings & Configuration') but the file doesn't exist in the provided documentation.

This suggests either missing tk settings documentation or incorrect reference.

---

#### documentation_inconsistency

**Description:** Inconsistent search key documentation

**Affected files:**
- `docs/help/ui/curses/help-navigation.md`
- `docs/help/ui/curses/index.md`

**Details:**
help-navigation.md states: 'Searching

| Key | Action |
|-----|--------|
| **/** | Open search prompt |'

index.md states: 'Press **/** to search across all help content.'

Both agree on the key, but help-navigation.md provides more detail about the search process (Type query, Enter, ESC to cancel) that index.md lacks.

---

#### documentation_inconsistency

**Description:** Inconsistent command format examples

**Affected files:**
- `docs/help/ui/curses/getting-started.md`
- `docs/help/ui/curses/files.md`

**Details:**
getting-started.md uses: 'mbasic --ui curses'

files.md uses: 'python3 mbasic --ui curses myprogram.bas'

The python3 prefix is inconsistent across documentation. Some examples use it, others don't, which could confuse users about the correct invocation method.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Step operations

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
features.md under 'Execution Control' lists:
'**Currently Implemented:**
- Run (Ctrl+R)
- Continue (Ctrl+G)
- Step statement (Ctrl+T)
- Step line (Ctrl+K)
- Stop (Ctrl+Q)'

getting-started.md describes the toolbar buttons:
'- **Step Line** - Execute all statements on current line, then pause (⏭️ button, Ctrl+K)
- **Step Stmt** - Execute one statement, then pause (↻ button, Ctrl+T)'

Both agree on the shortcuts, but features.md uses lowercase 'statement' and 'line' while getting-started.md capitalizes them as 'Step Line' and 'Step Stmt'. Minor inconsistency in terminology.

---

#### documentation_inconsistency

**Description:** Different URL formats shown for accessing Web IDE

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/index.md`

**Details:**
getting-started.md shows:
'Then open your browser to: **http://localhost:8080**'

index.md shows:
'**Access the Web IDE:**
```
https://your-server/mbasic
```'

These are different URL patterns - one uses localhost:8080, the other uses https with a path. Should clarify which is correct or if both are valid deployment options.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for file operations

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
settings.md uses:
"- **Open** - Open a .bas file from your computer (via browser file picker)"

web-interface.md uses:
"**Load the file:**
   - **Web/Tkinter UI:** Click File → Open, select the downloaded file"

Both use 'Open' but settings.md says 'Open a .bas file' while web-interface.md says 'Load the file' in the instructions, creating minor terminology inconsistency.

---

#### documentation_inconsistency

**Description:** Duplicate calendar programs with conflicting descriptions

**Affected files:**
- `docs/library/games/index.md`
- `docs/library/utilities/index.md`

**Details:**
games/index.md has:
"### Calendar

Year-long calendar display program from Creative Computing

**Source:** Creative Computing, Morristown, NJ
**Year:** 1979
**Tags:** calendar, display

**[Download calendar.bas](calendar.bas)**

**Note:** A simpler calendar utility is also available in the [Utilities Library](../utilities/index.md#calendar)"

utilities/index.md has:
"### Calendar

Simple calendar generator - prints a formatted calendar for any month/year (1900-2099)

**Source:** Dr Dobbs Nov 1981
**Year:** 1982
**Tags:** date, calendar, utility

**[Download calendar.bas](calendar.bas)**

**Note:** A different calendar program is also available in the [Games Library](../games/index.md#calendar)"

The games version says utilities has a 'simpler' version, but utilities says it's a 'different' version. Also, games version is from 1979 Creative Computing, utilities is from 1982 Dr Dobbs - these appear to be different programs but both are named calendar.bas which would cause a file conflict.

---

#### documentation_inconsistency

**Description:** Library statistics count may be inaccurate

**Affected files:**
- `docs/library/index.md`

**Details:**
index.md states:
"**Library Statistics:**
- 202 programs from the 1970s-1980s
- Sources: OAK, Simtel, CP/M CD-ROMs, and other historical archives"

This is a static count that would need manual updating whenever programs are added or removed. Without seeing the actual file counts in each category, this number cannot be verified and may become outdated.

---

#### documentation_inconsistency

**Description:** Future features section lists items that may already be implemented

**Affected files:**
- `docs/help/ui/web/settings.md`

**Details:**
settings.md lists under 'Future Features':
"- [ ] More settings (keywords, variables, interpreter)"

But web-interface.md under Edit Menu states:
"- **Settings** - Configure auto-numbering, case handling, and other interpreter options"

And settings.md itself mentions:
"You can configure interpreter behavior using BASIC commands in your program or the Command area:

```basic
REM Configure case handling for variables
SET "variables.case_conflict" "error"

REM Configure keyword capitalization
SET "keywords.case_style" "force_capitalize"
```"

This suggests some interpreter settings ARE available, contradicting the future features list.

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

**Description:** Inconsistent Python command naming

**Affected files:**
- `docs/user/INSTALL.md`

**Details:**
INSTALL.md uses 'python3' throughout most examples but then states:
'On some systems, Python 3 is available as `python` instead of `python3`'

It would be clearer to establish a convention early (e.g., 'This guide uses python3, but you may need to use python on some systems') rather than switching between them.

---

#### documentation_inconsistency

**Description:** Different keyboard shortcut documentation for help

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md states 'In-app help: Press Ctrl+?' for Tk UI, but keyboard-shortcuts.md (for Curses UI) shows '^F' for help and 'Ctrl+H/F1' for help. The Tk UI help shortcut is not documented in the keyboard-shortcuts.md file which is titled for Curses UI.

---

#### documentation_inconsistency

**Description:** Inconsistent Find/Replace keyboard shortcut documentation

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+H' as 'Find and replace (Tk UI only)' in the shortcuts table, but later in the 'Advanced Editing - Find and Replace' section it says 'Press Ctrl+H (Find and Replace)'. UI_FEATURE_COMPARISON.md shows Find/Replace as implemented for Tk but doesn't specify the shortcut. The keyboard shortcuts comparison table at the bottom doesn't include Find/Replace at all.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of toolbar button names

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md uses inconsistent capitalization for toolbar buttons: 'Click "Step" or "Stmt" toolbar button' (quoted, capitalized) vs 'Click "Cont" toolbar button' (quoted, capitalized) vs 'Click the Step toolbar button' (unquoted, capitalized). The style should be consistent throughout.

---

#### documentation_inconsistency

**Description:** Inconsistent status indicators in feature matrix

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md uses '⚠️' to indicate 'Partially implemented or planned' but doesn't consistently explain which features are partial vs planned. For example, 'Auto-save' shows '⚠️' for Tk with note 'Tk: planned/optional' but 'Find/Replace' shows '⚠️' for Web with note 'Tk: implemented, Web: planned'. The matrix should clearly distinguish between 'partially implemented' and 'planned'.

---

#### documentation_inconsistency

**Description:** Inconsistent line number examples in Smart Insert section

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md 'Example 2: No Gap - Auto Renumber' shows lines '10, 11, 12' but then after renumbering shows '10, 15, 1000, 1010'. The example states 'Lines 11 onwards are renumbered to 1000, 1010, 1020...' but line 10 gets a line 15 inserted, which doesn't match the description of '11 onwards'. The example should clarify that line 10 stays, line 15 is inserted, and line 11 becomes 1000.

---

#### documentation_inconsistency

**Description:** Missing CLI debugging commands in feature comparison

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md states under CLI 'Unique Features: Direct command-line debugging' and mentions 'NEW debugging commands (BREAK, STEP, WATCH, STACK)' in the CLI description. However, the 'Debugging Features' table shows CLI with '✅' for breakpoints, step execution, variable inspector, and call stack view, but doesn't mention these are command-based (BREAK, STEP, WATCH, STACK commands) vs visual in other UIs. The 'Notes' column for CLI debugging features should clarify 'CLI: BREAK command', 'CLI: STEP command', etc.

---


## Summary

- Total issues found: 666
- Code/Comment conflicts: 224
- Other inconsistencies: 442
