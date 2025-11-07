# Enhanced Consistency Report (Code + Documentation)

Generated: 2025-11-07 14:55:57
Analyzed: Source code (.py, .json) and Documentation (.md)

## 🔧 Code vs Comment Conflicts


## 📋 General Inconsistencies

### 🔴 High Severity

#### Documentation inconsistency

**Description:** Contradictory documentation about ProgramManager.load_from_file() return value

**Affected files:**
- `src/editing/manager.py`
- `src/file_io.py`

**Details:**
src/editing/manager.py docstring states:
"Note: ProgramManager.load_from_file() returns (success, errors) tuple where errors
is a list of (line_number, error_message) tuples for direct UI error reporting,
while FileIO.load_file() returns raw file text."

But the actual method signature in manager.py shows:
def load_from_file(self, filename: str) -> Tuple[bool, List[Tuple[int, str]]]:
    """Load program from file.
    ...
    Returns:
        Tuple of (success, errors)
        success: True if at least one line loaded successfully
        errors: List of (line_number, error_message) for failed lines

This is consistent internally, but the module docstring emphasizes a distinction that may be confusing since both descriptions match the implementation.

---

#### code_vs_comment

**Description:** Extensive comment block describes UI integration requirements that cannot be validated from provided code

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Lines 103-113 contain detailed documentation about UI integration:
"# This feature requires the following UI integration:
# - interpreter.interactive_mode must reference the UI object (checked with hasattr)
# - UI.program must have add_line() and delete_line() methods (validated, errors if missing)
# - UI._refresh_editor() method to update the display (optional, checked with hasattr)
# - UI._highlight_current_statement() for restoring execution highlighting (optional, checked with hasattr)
# If interactive_mode doesn't exist or is falsy, returns error: "Cannot edit program lines in this mode".
# If interactive_mode exists but required program methods are missing, returns error message."

The code does implement these checks (lines 119-169), but without the UI code files, we cannot verify:
1. Whether the UI actually provides these methods
2. Whether the method signatures match expectations
3. Whether the error messages match what's documented

This is a potential integration contract that may be violated.

---

#### code_vs_comment

**Description:** CONT docstring says editing clears execution state, but clear_execution_state() is never called when lines are modified

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 289-299 CONT docstring: 'IMPORTANT: CONT will fail with "?Can't continue" if the program has been edited (lines added, deleted, or renumbered) because editing clears the GOSUB/RETURN and FOR/NEXT stacks to prevent crashes from invalidated return addresses and loop contexts. See clear_execution_state() for details.'

However, process_line() (lines 186-207) adds/deletes lines WITHOUT calling clear_execution_state():
- Line 195: del self.lines[line_num] (no clear_execution_state)
- Line 203: self.line_asts[line_num] = line_ast (no clear_execution_state)

Only cmd_new() (line 398) and cmd_renum() (line 862) call clear_execution_state(). This means CONT could crash after line edits.

---

#### code_vs_comment

**Description:** DELETE command docstring says it returns deleted line numbers, but cmd_delete ignores the return value

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 759-761 docstring: 'Delegates to ui_helpers.delete_lines_from_program() which handles:
...
- Returns list of deleted line numbers (not used by this command)'

Line 777: 'delete_lines_from_program(self, args, self.program_runtime)' - return value is ignored.

If the return value is intentionally unused, why does the function return it? This suggests either:
1. The return value should be used (e.g., for confirmation message)
2. The function signature is wrong
3. The comment is documenting unused functionality

---

#### code_vs_comment

**Description:** FOR loop validation comment contradicts actual validation logic

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1005 states:
"# return_stmt is 0-indexed offset into statements array.
# Valid range:
#   - 0 to len(statements)-1: Normal statement positions (existing statements)
#   - len(statements): Special sentinel value - FOR was last statement on line,
#                      continue execution at next line (no more statements to execute on current line)
#   - > len(statements): Invalid - indicates the statement was deleted
#
# Validation: Check for strictly greater than (== len is OK as sentinel)"

But the actual validation code is:
'if return_stmt > len(line_statements):'

This means return_stmt == len(line_statements) is VALID (sentinel), and only return_stmt > len(line_statements) is invalid. The comment correctly describes this, so there's no inconsistency here. Retracting this item.

---

#### code_vs_comment_conflict

**Description:** execute_step() docstring claims infrastructure exists in tick_pc() but marks implementation as placeholder/not functional

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring states: 'Status: The tick_pc() method has infrastructure for step_statement and step_line modes, but this immediate STEP command is not yet connected to that infrastructure.'

This claims tick_pc() has step infrastructure, but without seeing tick_pc() code, we cannot verify this. The actual execute_step() implementation is:
```
count = stmt.count if stmt.count else 1
self.io.output(f"STEP {count} - Debug stepping not fully implemented")
```

This is a complete no-op that just prints a message. The docstring describes planned functionality rather than actual functionality, which is misleading for API documentation.

---

#### code_vs_comment

**Description:** FOR loop malformed handling comment describes semantic change but doesn't warn about side effects

**Affected files:**
- `src/parser.py`

**Details:**
In parse_for() docstring:

"Note: Some files may have malformed FOR loops like "FOR 1 TO 100" (missing variable).
We handle this by creating a dummy variable 'I' to allow parsing to continue,
though this changes the semantics and may cause issues if variable I is referenced elsewhere."

The code creates a dummy variable 'I' for malformed FOR loops, but the comment acknowledges this "may cause issues if variable I is referenced elsewhere" without providing any warning mechanism or error reporting. This is a significant semantic change that could silently break programs. The comment describes the problem but the code doesn't implement any safeguards or warnings, creating a dangerous situation where malformed code is silently "fixed" in a way that could corrupt program behavior.

---

#### code_vs_documentation

**Description:** Step command behavior inconsistency: auto_save.py documents statement-level stepping, cli_debug.py implements it but notes it depends on interpreter implementation, and curses_keybindings.json shows both 'step' (Ctrl+T) and 'step_line' (Ctrl+K) commands suggesting two different granularities

**Affected files:**
- `src/ui/auto_save.py`
- `src/ui/cli_debug.py`
- `src/ui/curses_keybindings.json`

**Details:**
auto_save.py line 1: 'Provides auto-save functionality with Emacs-inspired naming (#filename#)'
cli_debug.py cmd_step docstring: 'Executes a single statement (not a full line). If a line contains multiple statements separated by colons, each statement is executed separately.'
cli_debug.py _execute_single_step comment: 'Note: The actual statement-level granularity depends on the interpreter\'s implementation of tick()/execute_next(). These methods are expected to advance the program counter by one statement, handling colon-separated statements separately. If the interpreter executes full lines instead, this method will behave as line-level stepping rather than statement-level.'
curses_keybindings.json: 'step': 'Step statement (execute one statement)' and 'step_line': 'Step Line (execute all statements on current line)'

---

#### code_vs_comment

**Description:** Comment claims status bar is not updated but code shows status bar updates in multiple places

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _debug_step() method around line ~1450, comment says:
"# (No status bar update - output will show in output window)"

But later in the same method around line ~1490, the code explicitly updates the status bar:
"self.status_bar.set_text(f'Paused at {pc_display} - {key_to_display(STEP_KEY)}=Step, {key_to_display(CONTINUE_KEY)}=Continue, {key_to_display(STOP_KEY)}=Stop')"

Similar contradictions appear in _debug_step_line() and _debug_stop() methods where comments claim no status bar updates but code shows status bar.set_text() calls.

---

#### code_vs_comment

**Description:** Comment in cmd_delete and cmd_renum claims runtime sync occurs automatically via _execute_immediate, but this creates a timing issue

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comments in cmd_delete (line ~1280) and cmd_renum (line ~1300): "Note: Updates self.program immediately (source of truth). Runtime sync occurs\nautomatically via _execute_immediate which calls _sync_program_to_runtime before\nexecuting any immediate command."

However, _execute_immediate code (line ~1020) shows: "# Parse editor content into program (in case user typed lines directly)\n# This updates self.program, then syncs to runtime below\nself._parse_editor_content()\n\n# Load program lines into program manager\nself.program.clear()\nfor line_num in sorted(self.editor_lines.keys()):\n    line_text = f\"{line_num} {self.editor_lines[line_num]}\"\n    self.program.add_line(line_num, line_text)\n\n# Sync program to runtime\nself._sync_program_to_runtime()"

The sync happens BEFORE the immediate command executes, but cmd_delete/cmd_renum modify self.program DURING execution. The comment claims sync happens before the command, but the modifications happen after the sync, meaning runtime is out of sync until next immediate command.

---

#### internal_inconsistency

**Description:** cmd_delete and cmd_renum pass runtime=None to helper functions but don't call _sync_program_to_runtime after modifying program

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
cmd_delete (line ~1280): "deleted = delete_lines_from_program(self.program, args, runtime=None)\nself._refresh_editor()"

cmd_renum (line ~1300): "old_lines, line_map = renum_program(\n    self.program,\n    args,\n    self.interpreter.interactive_mode._renum_statement,\n    runtime=None\n)\nself._refresh_editor()"

Both functions modify self.program but only call _refresh_editor(), not _sync_program_to_runtime(). The comments claim sync happens automatically via _execute_immediate, but as noted in another issue, the sync happens BEFORE the command executes, not after. This means runtime is out of sync after these commands complete.

---

#### code_vs_comment_conflict

**Description:** Comment claims help navigation keys are hardcoded and not loaded from keybindings, but HelpMacros does load keybindings from JSON for macro expansion. The comment is misleading about the relationship between help widget navigation and keybinding configuration.

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~95 states:
"Note: Help navigation keys are hardcoded here and in keypress() method, not loaded from
keybindings. The help widget uses fixed keys (U for back, / for search, ESC/Q to exit)
to avoid dependency on keybinding configuration. HelpMacros does load the full keybindings
from JSON (for {{kbd:action}} macro expansion in help content), but the help widget itself
doesn't use those loaded keybindings."

However, the code shows:
1. HelpMacros IS initialized with keybindings: self.macros = HelpMacros('curses', help_root)
2. HelpMacros._load_keybindings() DOES load from JSON: keybindings_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"
3. The comment correctly notes help widget navigation is hardcoded, but the explanation about HelpMacros is accurate - it's not a conflict, just verbose documentation.

---

#### Code inconsistency

**Description:** QUIT_ALT_KEY is loaded from 'editor.continue' JSON key, which is semantically wrong - it should load from a quit-related key, not continue

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line ~99:
_quit_alt_from_json = _get_key('editor', 'continue')
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

This loads the quit alternative key from the 'continue' action in JSON, which is clearly incorrect. The 'continue' action should be for continuing execution, not quitting.

---

#### code_vs_comment

**Description:** Docstring claims variables window sorts by 'accessed' (last-accessed timestamp) by default with descending order, but the tree heading shows 'Last Accessed' which may not match the actual sort implementation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 103-104 state:
        self.variables_sort_column = 'accessed'  # Current sort column (default: 'accessed' for last-accessed timestamp)
        self.variables_sort_reverse = True  # Sort direction: False=ascending, True=descending (default descending for timestamps)

Line 673 shows:
        tree.heading('#0', text='↓ Variable (Last Accessed)')

However, the comment at line 673 states 'matches self.variables_sort_column='accessed', descending' but there's no visible code in this file that implements the actual sorting by 'accessed' timestamp. The sort_variables function is imported from src.ui.variable_sorting but not shown, creating uncertainty about whether the default sort is actually implemented.

---

#### code_vs_comment

**Description:** Comment claims 'not self.running' check prevents race conditions, but this check is redundant with can_execute_immediate() logic

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1729 says:
# Check if safe to execute - use both can_execute_immediate() AND self.running flag
# The 'not self.running' check prevents immediate mode execution when a program is running,
# even if the tick hasn't completed yet. This prevents race conditions where immediate
# mode could execute while the program is still running but between tick cycles.

The comment suggests 'not self.running' is needed to prevent race conditions. However, if can_execute_immediate() is properly implemented, it should already handle this case. The comment implies a design flaw where can_execute_immediate() alone is insufficient, which needs clarification.

---

#### code_vs_comment

**Description:** Docstring for TkIOHandler.input() says it handles comma-separated values but implementation returns raw string

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring states: "Returns the raw string entered by user. The interpreter handles parsing of comma-separated values for INPUT statements with multiple variables."

This is internally contradictory - it says it returns raw string AND that the interpreter handles parsing. The comment should clarify that this method returns raw string and does NOT parse comma-separated values itself.

---

#### code_vs_comment

**Description:** serialize_statement() raises ValueError for unhandled statement types to prevent 'silent data corruption during RENUM', but renum_program() uses a callback for updating references instead of calling serialize_statement(). The error handling strategy is inconsistent.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
In serialize_statement():
"# For other statement types, raise an error - this indicates a missing serialization handler\n# All statement types must be explicitly handled to prevent silent data corruption during RENUM\nelse:\n    from src.debug_logger import debug_log\n    error_msg = f\"Unhandled statement type '{stmt_type}' in serialize_statement() - cannot serialize during RENUM\"\n    debug_log(f\"ERROR: {error_msg}\")\n    raise ValueError(error_msg)"

But renum_program() uses a callback (renum_callback) to update line references, not serialize_statement(). If the callback doesn't handle a statement type, there's no error raised. This creates an inconsistency: serialize_statement() prevents silent corruption, but renum_program() could silently fail to update references if the callback is incomplete.

---

#### code_vs_comment

**Description:** Inconsistent documentation about breakpoint types - code handles both PC objects and plain integers, but comments suggest PC-only

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1754 comment in _update_breakpoint_display: "# Note: self.runtime.breakpoints is a set that can contain:
#   - PC objects (statement-level breakpoints, created by _toggle_breakpoint)
#   - Plain integers (line-level breakpoints, legacy/compatibility)
# This implementation uses PC objects exclusively, but handles both for robustness."

However, _do_toggle_breakpoint (line ~1798) creates PC objects with stmt_offset=0, and the comment at line ~1756 says "This implementation uses PC objects exclusively" which contradicts the "legacy/compatibility" plain integer support mentioned just above.

---

#### code_vs_comment

**Description:** Comment claims RUN clears variables but preserves breakpoints, but reset_for_run behavior is not verified in this file

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1795 comment: "# Reset runtime with current program - RUN = CLEAR + GOTO first line
# This preserves breakpoints but clears variables"

And line ~2041 comment: "# Create or reset runtime - preserves breakpoints"

These comments make assertions about reset_for_run() behavior, but the actual implementation of reset_for_run() is not shown in this file. If reset_for_run() doesn't actually preserve breakpoints, these comments would be incorrect.

---

#### code_vs_comment

**Description:** Dual input mechanism comment in _handle_output_enter suggests both paths may be needed, but this indicates unclear control flow

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment states: 'Provide input to interpreter via TWO mechanisms (both may be needed depending on code path): 1. interpreter.provide_input() - Used when interpreter is waiting synchronously... 2. input_future.set_result() - Used when async code is waiting via asyncio.Future... Only one path is active at a time, but we attempt both to ensure the waiting code receives input regardless of which path it used.'

This suggests the code doesn't know which mechanism is active and tries both, which could indicate a design issue or race condition.

---

#### code_vs_comment

**Description:** start() method docstring says to use start_web_ui() instead, but then raises NotImplementedError. The stop() method has similar docstring but actually works. Inconsistent pattern.

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
start() docstring: 'Not implemented - raises NotImplementedError.\n\nUse start_web_ui() module function instead for web backend.'
start() code: 'raise NotImplementedError("Web backend uses start_web_ui() function, not backend.start()")'

stop() docstring: 'Not implemented - raises NotImplementedError.\n\nUse start_web_ui() module function instead for web backend.'
stop() code: 'app.shutdown()' (does NOT raise NotImplementedError)

The docstrings are identical but the implementations differ - one raises exception, one doesn't.

---

#### code_documentation_mismatch

**Description:** Redis-backed session storage implemented and tested but not documented for users

**Affected files:**
- `test_redis_settings.py`
- `docs/help/common/debugging.md`
- `docs/help/README.md`

**Details:**
test_redis_settings.py demonstrates:
- Per-session settings isolation in Redis
- Settings persistence across page refreshes
- Independent settings for different sessions
- Fallback to file backend when Redis unavailable

The test file header states:
'This verifies that:
1. Different sessions have independent settings
2. Settings persist across SettingsManager instances with same session_id
3. Default settings are loaded from disk on first access
4. Changes don't affect other sessions'

But no user-facing documentation explains:
- That web UI uses Redis for session storage
- That settings are per-session, not global
- How to configure Redis URL
- What happens when Redis is unavailable
- That different browser tabs/windows have independent settings

This is a significant architectural feature that users should understand.

---

#### documentation_inconsistency

**Description:** EXP function overflow limit contradicts the documented SINGLE/DOUBLE range limits

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/exp.md`

**Details:**
exp.md states: "X must be <=87.3365. If EXP overflows, the 'Overflow' error message is displayed"

However, data-types.md states SINGLE range as: "±2.938736×10^-39 to ±1.701412×10^38"

The maximum value e^87.3365 ≈ 6.8×10^37, which is within the stated SINGLE range. But the documentation suggests this is the overflow limit. This implies either:
1. The SINGLE range documentation is incorrect
2. The EXP limit is more conservative than the actual range
3. There's a different internal representation issue

This needs clarification as it affects how programmers understand numeric limits.

---

#### documentation_inconsistency

**Description:** Settings documentation describes features as 'MBASIC Extension' but settings.md treats them as standard features

**Affected files:**
- `docs/help/common/settings.md`
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/language/statements/setsetting.md`

**Details:**
showsettings.md and setsetting.md both say:
'**Versions:** MBASIC Extension'
'This is a modern extension not present in original MBASIC 5.21'

But settings.md presents the entire settings system as a standard feature without any indication it's an extension. The main settings.md document should have a prominent note that the entire settings system is a modern extension not present in original MBASIC 5.21.

---

#### documentation_inconsistency

**Description:** Contradictory information about PEEK/POKE implementation between index and architecture docs

**Affected files:**
- `docs/help/index.md`
- `docs/help/mbasic/architecture.md`

**Details:**
index.md states: 'PEEK does NOT return values written by POKE - no memory state is maintained'

architecture.md states: 'PEEK/POKE - Emulated for compatibility:
- POKE: Parsed and executes successfully, but performs no operation (no-op)
- PEEK: Returns random integer 0-255 (for RNG seeding compatibility)
- **PEEK does NOT return values written by POKE** - no memory state is maintained'

Both say the same thing but index.md appears in a 'Most Commonly Searched' section without the full context that architecture.md provides, which could confuse users.

---

#### documentation_inconsistency

**Description:** Contradictory information about file persistence in Web UI

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md states: 'Files persist only during browser session - lost on page refresh' and 'No persistent storage across sessions'

extensions.md mentions 'Auto-save - Automatic saving to browser storage' for the Web UI.

These statements appear contradictory. If files are lost on page refresh, how does auto-save to browser storage work? This needs clarification about what exactly is saved and when.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of STACK command availability

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
cli/debugging.md documents 'STACK - Call Stack Inspection' as a CLI command with syntax 'STACK', 'STACK GOSUB', 'STACK FOR'. However, feature-reference.md states 'Execution Stack (Menu only)' for Curses UI with note 'There is no dedicated keyboard shortcut'. It's unclear if the STACK command works in Curses UI or if it's menu-only.

---

#### documentation_inconsistency

**Description:** Self-contradictory statement about Find/Replace in Curses UI

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
feature-reference.md contains contradictory information: Under 'Editor Features' it states 'Find/Replace (Not yet implemented)' but then says 'See [Find/Replace](find-replace.md) (available via menu)'. These two statements directly contradict each other - it cannot be both 'not yet implemented' and 'available via menu'.

---

#### documentation_inconsistency

**Description:** Contradictory information about save keyboard shortcut

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
files.md states: 'Press **^V** to save (Note: ^S unavailable due to terminal flow control)'

But quick-reference.md states: '**^V** | Save program (^S unavailable - terminal flow control)'

However, the note about ^S being unavailable is inconsistent with the actual shortcut listed. The documentation should clarify if ^V is the save shortcut or if there's another shortcut.

---

#### documentation_inconsistency

**Description:** Contradictory information about command-line loading behavior

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
files.md states: 'The program will:
- Load into the editor
- Automatically run
- Then enter interactive mode'

But getting-started.md shows: 'mbasic --ui curses' with no mention of auto-run behavior when loading a file.

This is contradictory - does loading from command line auto-run or not? The behavior should be clearly documented.

---

#### documentation_inconsistency

**Description:** Contradictory information about variable window search key

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/variables.md`

**Details:**
quick-reference.md states: '**/** | Search for variable' under Variables Window section

variables.md states: '### Search Function
1. In variables window, press `/` to search'

Both agree on `/` key, but variables.md also mentions: 'Press `n` for next match
Press `N` for previous match'

These navigation keys (n/N) are not documented in quick-reference.md, creating an incomplete reference.

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

But web/settings.md file is not provided in the documentation set.

---

#### documentation_inconsistency

**Description:** Major contradiction about Variable Inspector implementation status

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/debugging.md`

**Details:**
features.md states:
'### Variable Inspector

**Currently Implemented:**
- Basic variable viewing via Debug menu'

But debugging.md states:
'## Variable Inspector

**Implementation Status:** Basic variable viewing via Debug menu is currently available. The detailed variable inspector panels, watch expressions, and interactive editing features described below are **planned for future releases** and not yet implemented.'

Then debugging.md shows extensive planned features under '### Variables Panel (Planned)' with detailed tree view structure.

However, getting-started.md states:
'### Show Variables

While program is paused or after it runs:
- Click Run → Show Variables
- A popup shows all defined variables and their values'

This suggests a working feature, contradicting the 'planned' status in debugging.md.

---

#### documentation_inconsistency

**Description:** Unrelated documentation in sequential-files.md

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/sequential-files.md`

**Details:**
sequential-files.md contains extensive documentation about line endings and ^Z EOF markers, which has no connection to the settings and configuration system. This appears to be a documentation organization issue where file I/O documentation is mixed with settings documentation.

---

### 🟡 Medium Severity

#### Documentation inconsistency

**Description:** Version number mismatch between setup.py and ast_nodes.py module docstring

**Affected files:**
- `setup.py`
- `src/ast_nodes.py`

**Details:**
setup.py declares version="0.99.0" with comment "Reflects ~99% implementation status (core complete)", but ast_nodes.py docstring says "Abstract Syntax Tree (AST) node definitions for MBASIC 5.21" without mentioning the interpreter version 0.99.0. This creates ambiguity about whether 5.21 refers to the target MBASIC version being emulated or the interpreter version.

---

#### Code vs Comment conflict

**Description:** LineNode docstring claims no source_text field but doesn't explain how char_start/char_end in StatementNode relate to line boundaries

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring states: "Design note: This class intentionally does not have a source_text field to avoid maintaining duplicate copies that could get out of sync with the AST during editing. Text regeneration is handled by the position_serializer module..."

However, StatementNode has char_start and char_end fields described as "Character offset from start of line". If LineNode has no source_text, it's unclear what "start of line" means or how these offsets are used during regeneration. The relationship between LineNode, StatementNode offsets, and the position_serializer module needs clarification.

---

#### Code vs Comment conflict

**Description:** VariableNode has conflicting documentation about type_suffix vs explicit_type_suffix

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode docstring states:
"Type suffix handling:
- type_suffix: The actual suffix character ($, %, !, #)
- explicit_type_suffix: True if suffix appeared in source code, False if inferred from DEF

Example: In "DEFINT A-Z: X=5", variable X has type_suffix='%' and explicit_type_suffix=False. The suffix must be tracked but not regenerated in source code."

This creates confusion: if type_suffix contains the actual suffix character, why does explicit_type_suffix exist? The comment says "must be tracked but not regenerated" - but how does code know whether to regenerate it? The relationship between these two fields and their usage in serialization needs clarification.

---

#### Code vs Comment conflict

**Description:** PrintStatementNode has keyword_token field but other similar statements don't consistently have token fields

**Affected files:**
- `src/ast_nodes.py`

**Details:**
PrintStatementNode has: "keyword_token: Optional[Token] = None  # Token for PRINT keyword (for case handling)"

IfStatementNode has: "keyword_token, then_token, else_token" fields
ForStatementNode has: "keyword_token, to_token, step_token" fields

But many other statement nodes (GotoStatementNode, GosubStatementNode, WhileStatementNode, etc.) don't have keyword_token fields. It's unclear why some statements preserve token information for case handling and others don't. This inconsistency suggests either incomplete implementation or unclear design intent.

---

#### code_vs_comment

**Description:** Comment claims original_negative is captured at line 269, but that line is actually inside format_numeric_field method at a different location

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment at line 272 states:
# original_negative was captured before rounding (line 269 above: original_negative = value < 0)
But line 269 is actually:
        original_negative = value < 0
The comment reference is correct in content but the line number reference in the comment itself is self-referential and confusing. The comment appears to be explaining the code immediately above it, not referencing a different line 269.

---

#### code_vs_comment

**Description:** Comment claims identifier_table infrastructure exists but is not used, yet get_identifier_table() method is implemented and functional

**Affected files:**
- `src/case_string_handler.py`

**Details:**
Comment at lines 54-60 states:
# Note: We return original_text directly. An identifier_table infrastructure
# exists (see get_identifier_table) but is not currently used for identifiers,
# as they always preserve their original case without policy enforcement.

However, the get_identifier_table() method is fully implemented (lines 23-27) and functional. The comment suggests it's unused infrastructure, but the code shows it's a working method that could be called. This creates confusion about whether the infrastructure is vestigial or intentionally available for future use.

---

#### code_vs_comment

**Description:** EOF() implementation comment about binary mode and ^Z checking contradicts the actual file mode checking logic

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment at lines 779-782 states:
# For input files opened in binary mode, check for EOF or ^Z
# Mode 'I' = binary input mode, where files are opened in binary mode ('rb')
# and ^Z checking is appropriate for CP/M-style EOF detection

But the code checks file_info['mode'] == 'I' without verifying the file was actually opened in binary mode ('rb'). The comment assumes mode 'I' means binary mode, but this is not validated in the visible code. The file could theoretically be opened in text mode with mode='I' set, which would break the ^Z detection logic.

---

#### Code vs Documentation inconsistency

**Description:** SandboxedFileIO methods documented as STUB but implementation status unclear

**Affected files:**
- `src/file_io.py`

**Details:**
SandboxedFileIO class docstring states:
"Implementation status:
- list_files(): IMPLEMENTED - delegates to backend.sandboxed_fs
- load_file(): STUB - raises IOError (requires async/await refactor)
- save_file(): STUB - raises IOError (requires async/await refactor)
- delete_file(): STUB - raises IOError (requires async/await refactor)
- file_exists(): STUB - raises IOError (requires async/await refactor)"

However, the actual implementations show:
- load_file() raises: "LOAD not yet implemented in web UI - requires async refactor"
- save_file() raises: "SAVE not yet implemented in web UI - requires async refactor"
- delete_file() raises: "DELETE not yet implemented in web UI - requires async refactor"
- file_exists() raises: "File existence check not yet implemented in web UI - requires async refactor"

The error messages say "not yet implemented" but don't mention "requires async/await refactor" consistently (file_exists says "requires async refactor" not "async/await refactor").

---

#### Code vs Documentation inconsistency

**Description:** FileSystemProvider.list_files() return type documentation mismatch

**Affected files:**
- `src/filesystem/base.py`
- `src/filesystem/sandboxed_fs.py`

**Details:**
src/filesystem/base.py documents:
@abstractmethod
def list_files(self, pattern: Optional[str] = None) -> list:
    """List files matching pattern.
    ...
    Returns:
        List of filenames
    """

But src/file_io.py FileIO.list_files() returns:
"Returns:
    List of (filename, size_bytes, is_dir) tuples"

The FileSystemProvider.list_files() returns simple filenames (list of strings), while FileIO.list_files() returns tuples with metadata. This is intentional separation but could cause confusion since both have similar method names.

---

#### Documentation inconsistency

**Description:** Module docstring claims Web UI uses FileIO abstraction exclusively but doesn't explain the relationship

**Affected files:**
- `src/editing/manager.py`

**Details:**
The module docstring states:
"Why ProgramManager has its own file I/O methods:
...
- Web UI uses FileIO abstraction exclusively (no direct ProgramManager file access)"

But earlier it says:
"Note: Not suitable for Web UI due to direct filesystem access - Web UI uses
FileIO abstraction in interactive.py instead."

This creates confusion: if Web UI uses FileIO exclusively, why does ProgramManager have load_from_file/save_to_file methods at all? The explanation says these are for "local UI menu operations" but doesn't clearly state that Web UI never calls these ProgramManager methods directly.

---

#### code_vs_comment

**Description:** Comment claims INPUT statements are blocked at parse time, but code shows they are blocked at runtime

**Affected files:**
- `src/immediate_executor.py`

**Details:**
LIMITATIONS section in _show_help() docstring states:
"• INPUT statement will fail at runtime in immediate mode (blocked when input() is called, not at parse time - use direct assignment instead)"

This correctly describes the implementation in OutputCapturingIOHandler.input():
"def input(self, prompt=""):
    """Input not supported in immediate mode.

    Note: INPUT statements are parsed and executed normally, but fail
    at runtime when the interpreter calls this input() method."""
    raise RuntimeError("INPUT not allowed in immediate mode")"

However, the help text is inconsistent with itself - it says "will fail at runtime" but then adds "(blocked when input() is called, not at parse time - use direct assignment instead)" which is redundant and confusing phrasing.

---

#### code_vs_comment

**Description:** Comment describes microprocessor model but code checks boolean flags

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In can_execute_immediate(), the comment states:
"# Check interpreter state using microprocessor model"

But the actual implementation checks boolean flags and object attributes:
"return (self.runtime.halted or
        state.error_info is not None or
        state.input_prompt is not None)"

The term 'microprocessor model' suggests a specific architectural pattern, but the code is simply checking boolean conditions. This terminology mismatch could mislead developers about the actual implementation approach.

---

#### code_vs_comment

**Description:** Comment claims EDIT command is not yet implemented, but code shows full implementation

**Affected files:**
- `src/interactive.py`

**Details:**
Line 1046 comment says: 'Note: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K) are not yet implemented.'

However, the cmd_edit method (lines 1046-1200) has a complete implementation with:
- Space, D, C, I, X, H, L, E, Q, A commands
- Full cursor management
- Character-by-character editing
- Save/abort functionality

The comment is partially correct (count prefixes and search ARE missing), but misleading about overall implementation status.

---

#### code_vs_comment

**Description:** RENUM docstring claims broader ERL renumbering than MBASIC manual, but doesn't explain if this matches actual MBASIC 5.21 behavior

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 826-838 docstring: 'ERL handling: ERL expressions with ANY binary operators (ERL+100, ERL*2, ERL=100) have all right-hand numbers renumbered, even for arithmetic operations. This is intentionally broader than the MBASIC manual (which only specifies comparison operators) to avoid missing line references.'

The comment claims this is '100% compatible with MBASIC 5.21' (line 7), but then admits deviating from the MBASIC manual. Need clarification:
1. Does actual MBASIC 5.21 renumber arithmetic operators?
2. Is the manual incomplete/wrong?
3. Is this a known incompatibility?

---

#### code_vs_comment

**Description:** Comment says readline Ctrl+A binding inserts character, but actual behavior depends on terminal/readline version

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 145-150: 'Bind Ctrl+A to insert the character instead of moving cursor to beginning-of-line. This overrides default Ctrl+A (beginning-of-line) behavior. When user presses Ctrl+A, the terminal sends ASCII 0x01, and "self-insert" tells readline to insert it as-is instead of interpreting it as a command.'

This comment assumes:
1. Terminal sends 0x01 for Ctrl+A (not always true)
2. readline 'self-insert' works as described (version-dependent)
3. The binding successfully overrides default (may fail on some systems)

The code at lines 163-177 handles 0x01 for edit mode, but the readline binding may not reliably produce 0x01 input.

---

#### code_vs_comment

**Description:** Comment says MERGE updates runtime statement_table 'only after successful merge', but code updates during merge

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 543-547 docstring: 'If merge is successful AND program_runtime exists, updates runtime's statement_table (for CONT support). Runtime update only happens after successful merge.'

But lines 577-582 show update happens INSIDE the merge loop:
'if self.program_runtime:
    for line_num in self.program.line_asts:
        line_ast = self.program.line_asts[line_num]
        self.program_runtime.statement_table.replace_line(line_num, line_ast)'

This updates ALL lines (not just merged ones) and happens after merge completes, but the comment implies it's conditional on success in a way that's misleading.

---

#### code_vs_comment

**Description:** CHAIN docstring describes ChainException behavior but doesn't explain when it's raised vs when program runs directly

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 593-598: 'Raises ChainException when called during program execution to signal the interpreter's run() loop to restart with the new program. This avoids recursive run() calls. When called from command line (not during execution), runs the program directly.'

But the code at lines 688-720 shows:
- Lines 688-707: Always raises ChainException if runtime exists
- Lines 708-720: Only runs directly if no runtime exists

The docstring implies ChainException is raised 'during program execution', but code shows it's raised whenever runtime exists (even if not currently executing). This is confusing.

---

#### code_vs_comment_conflict

**Description:** Comment claims GOTO/GOSUB in immediate mode 'work but have special semantics' and describes execution behavior, but the actual behavior may be confusing or incorrect

**Affected files:**
- `src/interactive.py`

**Details:**
Comment says: 'GOTO/GOSUB in immediate mode work but have special semantics: They execute and jump during execute_statement(), but we restore the original PC afterward to preserve CONT functionality.'

Code does:
```
old_pc = runtime.pc
for stmt in line_node.statements:
    interpreter.execute_statement(stmt)
runtime.pc = old_pc
```

The comment describes that GOTO/GOSUB will execute and jump, then the PC is restored. However, this means if a GOTO is executed in immediate mode, it would jump to that line, execute it, but then restore the PC. This behavior is confusing - if the GOTO target line modifies variables or has side effects, those persist, but the PC position is reverted. The comment acknowledges this is 'not recommended' but the implementation allows it with potentially confusing semantics.

---

#### code_vs_comment

**Description:** Comment describes skip_next_breakpoint_check behavior incorrectly regarding when it's set and cleared

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 56-59 says:
"Set to True AFTER halting at a breakpoint (set after returning state).
On next execution, if still True, allows stepping past the breakpoint once,
then clears itself to False. Prevents re-halting on same breakpoint."

But code at lines 367-373 shows:
```
if at_breakpoint:
    if not self.state.skip_next_breakpoint_check:
        self.runtime.halted = True
        self.state.skip_next_breakpoint_check = True
        return self.state
    else:
        self.state.skip_next_breakpoint_check = False
```

The comment says it's "set after returning state" but the code sets it to True BEFORE returning (line 369), then clears it to False on the next execution when the breakpoint is encountered again (line 373). The comment's description of the timing is misleading.

---

#### code_vs_comment

**Description:** Comment about return_stmt validation contradicts the actual validation logic

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 1009-1017 says:
"return_stmt is 0-indexed offset into statements array.
Valid range: 0 to len(statements) (inclusive).
- 0 to len(statements)-1: Normal statement positions
- len(statements): Special sentinel - GOSUB was last statement on line, so RETURN
  continues at next line. This value is valid because PC can point one past the
  last statement to indicate 'move to next line' (handled by statement_table.next_pc).
Values > len(statements) indicate the statement was deleted (validation error)."

But the validation code at line 1018 checks:
```
if return_stmt > len(line_statements):  # Check for strictly greater than (== len is OK)
```

The comment says "Values > len(statements) indicate the statement was deleted" and the code checks "return_stmt > len(line_statements)", which means return_stmt == len(line_statements) is considered valid. However, the comment also says this is a "Special sentinel" case, but there's no code that actually handles this special case differently - it just passes through to create PC(return_line, return_stmt). This suggests either the comment is over-explaining or the validation is incomplete.

---

#### code_vs_comment

**Description:** execute_next docstring describes behavior that differs from what the code comment suggests about separate statements

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 1082-1092 says:
"NEXT I, J, K processes variables left-to-right: I first, then J, then K.
For each variable, _execute_next_single() is called to increment it and check if
the loop should continue. If _execute_next_single() returns True (loop continues),
execution jumps back to the FOR body and remaining variables are not processed.
If it returns False (loop finished), that loop is popped and the next variable is processed.

This differs from separate statements (NEXT I: NEXT J: NEXT K) which would
always execute sequentially, processing all three NEXT statements."

However, the code at lines 1104-1113 shows:
```
for var_node in var_list:
    var_name = var_node.name + (var_node.type_suffix or "")
    should_continue = self._execute_next_single(var_name, var_node=var_node)
    if should_continue:
        return
```

The comment says separate statements 'NEXT I: NEXT J: NEXT K' would behave differently, but if NEXT I causes a jump back to FOR I, execution would never reach 'NEXT J' anyway. The distinction being made is unclear - both cases would stop processing subsequent NEXT statements if a loop continues.

---

#### code_vs_comment

**Description:** Comment describes WEND popping loop 'after setting npc' but code pops before potential WHILE re-push

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1090 says:
"# Pop the loop from the stack (after setting npc above, before WHILE re-executes).
# Timing: We pop NOW so the stack is clean before WHILE condition re-evaluation."

This suggests popping happens AFTER npc is set but BEFORE WHILE re-executes. However, the actual sequence is:
1. Set npc to WHILE position
2. Pop loop from stack
3. WHILE re-executes on next tick

The comment is accurate about timing but the phrase 'after setting npc above' could be clearer that both operations happen in sequence before returning.

---

#### code_vs_comment

**Description:** CLEAR documentation says 'bare except: pass' but code structure unclear

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1260 states:
"# Close all open files
# Note: Errors during file close are silently ignored (bare except: pass)"

The actual code is:
'try:
    file_obj = self.runtime.files[file_num]
    if hasattr(file_obj, "close"):
        file_obj.close()
except:
    pass'

The comment accurately describes the behavior. However, this is contrasted with RESET statement which 'allows errors during file close to propagate to the caller' (line ~1680). This is intentional different behavior and is documented, so no inconsistency.

---

#### code_vs_comment

**Description:** RUN statement comment describes behavior that differs from implementation

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1420 states:
"# In non-interactive context, restart from beginning
# Note: RUN without args sets halted=True to stop current execution.
# The caller (e.g., UI tick loop) should detect halted=True and restart
# execution from the beginning if desired. This is different from
# RUN line_number which sets halted=False to continue execution inline."

However, the code for RUN without args is:
'self.runtime.clear_variables()
self.runtime.halted = True'

This sets halted=True but does NOT set any PC to restart from beginning. The comment says 'caller should detect halted=True and restart' but this is ambiguous - does halted=True mean 'program ended' or 'restart requested'? The distinction between RUN (halted=True) and RUN line_number (halted=False, sets npc) suggests different semantics that may not be clear to callers.

---

#### code_vs_comment_conflict

**Description:** Comment in execute_cont() describes different behavior for STOP vs Break regarding PC update, but execute_stop() code shows it DOES update PC

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: 'Note: execute_stop() moves NPC to PC for resume, while BreakException handler does not update PC, which affects whether CONT can resume properly.'

But execute_stop() code shows:
```
self.runtime.pc = self.runtime.npc
```

This indicates execute_stop() DOES update PC (sets it to NPC), contradicting the implication that there's a difference in PC handling. The comment suggests BreakException handler doesn't update PC while STOP does, but the phrasing is confusing about what actually happens.

---

#### code_vs_comment_conflict

**Description:** Comment in evaluate_functioncall() explains debugger_set=True usage but the actual restore code doesn't use it

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says: '# Restore parameter values (use debugger_set=True to avoid tracking)'

But the actual restore code is:
```
self.runtime.set_variable(base_name, type_suffix, saved_value, debugger_set=True)
```

The comment is correct - the code DOES use debugger_set=True. However, earlier in the same function, the save operation uses:
```
saved_vars[param_name] = self.runtime.get_variable_for_debugger(param.name, param.type_suffix)
```

And the parameter setting uses:
```
self.runtime.set_variable(param.name, param.type_suffix, args[i], token=call_token, limits=self.limits)
```

This is inconsistent - the save uses get_variable_for_debugger (untracked), the set uses normal set_variable (tracked), but the restore uses debugger_set=True (untracked). The asymmetry suggests potential tracking issues.

---

#### Code vs Documentation inconsistency

**Description:** The base.py IOHandler.input_line() docstring states it should 'Preserve leading/trailing spaces and not interpret commas' but then documents a KNOWN LIMITATION that implementations CANNOT preserve spaces. However, the docstring examples and 'Design goal' suggest this should work, creating confusion about whether this is a bug or accepted limitation.

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/console.py`
- `src/iohandler/curses_io.py`
- `src/iohandler/web_io.py`

**Details:**
base.py docstring says:
'Design goal: Preserve leading/trailing spaces and not interpret commas as field separators (for MBASIC LINE INPUT compatibility).'

But then says:
'KNOWN LIMITATION (not a bug - platform limitation):
Current implementations (console, curses, web) CANNOT fully preserve leading/trailing spaces due to underlying platform API constraints'

This creates ambiguity: is preserving spaces the intended behavior (design goal) or an accepted limitation? The 'design goal' language suggests it should work but doesn't.

---

#### code_vs_comment

**Description:** Comment claims SimpleKeywordCase validates policy strings in __init__ and defaults to force_lower for invalid values, but this behavior is not verifiable from the provided code

**Affected files:**
- `src/lexer.py`

**Details:**
In create_keyword_case_manager() docstring:
"Note: SimpleKeywordCase is implemented in src/simple_keyword_case.py. It validates
policy strings in its __init__ method and defaults to force_lower for invalid values."

However, SimpleKeywordCase implementation is not provided in the source files, so we cannot verify if this validation behavior actually exists. The comment makes specific claims about implementation details that cannot be confirmed.

---

#### code_vs_comment

**Description:** Comment claims identifiers can contain periods in Extended BASIC, but implementation details are unclear

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring states:
"Note: MBASIC 5.21 includes Extended BASIC features (e.g., periods in identifiers)."

And in read_identifier() around line 240:
"# Subsequent characters can be letters, digits, or periods (in Extended BASIC)
while self.current_char() is not None:
    char = self.current_char()
    if char.isalnum() or char == '.':
        ident += self.advance()"

The code does allow periods in identifiers, but there's no conditional logic checking if Extended BASIC mode is enabled. The comment suggests this is a mode-specific feature, but the implementation always allows it. This could be intentional (always supporting Extended BASIC) or an inconsistency.

---

#### code_vs_comment

**Description:** Comment claims RND and INKEY$ can be called without parentheses as a general MBASIC 5.21 feature, but code only implements this for these two specific functions

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line 11-12 states:
"Exception: Only RND and INKEY$ can be called without parentheses in MBASIC 5.21
  (this is specific to these two functions, not a general MBASIC feature)"

However, the code at lines 1088-1102 implements this behavior:
```
if func_token.type == TokenType.RND and not self.match(TokenType.LPAREN):
    # RND without arguments
    return FunctionCallNode(...)

if func_token.type == TokenType.INKEY and not self.match(TokenType.LPAREN):
    # INKEY$ without arguments
    return FunctionCallNode(...)
```

The comment correctly describes the implementation, so this is actually consistent. However, the phrasing could be clearer.

---

#### code_vs_comment

**Description:** Comment about MID$ statement detection describes lookahead strategy but implementation may have issues

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines 625-633 describes:
"Look ahead to distinguish MID$ statement from MID$ function call
MID$ statement has pattern: MID$ ( ... ) =
MID$ function has pattern: MID$ ( ... ) in expression context"

The code implements lookahead (lines 634-655), but the error handling at line 657 catches all exceptions with bare 'except:', which could hide bugs. The comment says 'either not a statement or error in lookahead' but doesn't specify what errors are expected.

---

#### code_vs_comment

**Description:** Comment describes MID$ assignment syntax incorrectly regarding token representation

**Affected files:**
- `src/parser.py`

**Details:**
In parse_mid_assignment() method:

Comment states: "Note: The lexer tokenizes 'MID$' in source as a single MID token (the $ is part of the keyword, not a separate token)."

However, the comment in the method body states: "token = self.current()  # MID token (represents 'MID$' from source)"

This suggests the token is MID, but the docstring example shows "MID$(string_var, start, length) = value" which implies the $ is part of the syntax. The comment claims the lexer creates a single MID token for 'MID$', but this conflicts with standard BASIC tokenization where MID$ would typically be a separate token type or the $ would be handled differently.

---

#### code_vs_comment

**Description:** SETSETTING docstring field name comment conflicts with actual parameter name

**Affected files:**
- `src/parser.py`

**Details:**
In parse_setsetting() method:

Docstring states:
"Args:
    setting_name: String expression identifying the setting (e.g., "editor.auto_number")
    value: Expression to evaluate and assign to the setting"

But in the return statement comment:
"return SetSettingStatementNode(
    setting_name=setting_name_expr,  # Field name: 'setting_name' (string identifying setting)
    value=value_expr,
    ..."

The inline comment redundantly restates that the field is called 'setting_name', which is already clear from the code. This suggests the comment may have been added during refactoring and is now unnecessary, or there was confusion about parameter naming.

---

#### code_vs_comment

**Description:** DIM statement comment about MBASIC 5.21 behavior conflicts with implementation flexibility

**Affected files:**
- `src/parser.py`

**Details:**
In parse_dim() docstring:

"Note: MBASIC 5.21 allows any expression for dimensions (evaluated at runtime).
Some compiled BASICs require constant expressions, but we accept any expression."

This comment suggests the parser is being permissive by accepting "any expression" for array dimensions, implying this is a design choice. However, the code simply calls parse_expression() without any validation or restriction. The comment implies there was a decision to be more flexible than "some compiled BASICs", but doesn't document whether this matches MBASIC 5.21 behavior exactly or if there are any limitations that should be enforced.

---

#### code_vs_comment

**Description:** DEF FN comment describes stripping type suffix but doesn't explain lowercase 'fn' prefix handling clearly

**Affected files:**
- `src/parser.py`

**Details:**
In parse_def_fn, the comment says:
"# Use lowercase 'fn' to match function calls"
and
"# raw_name already starts with lowercase 'fn' from lexer normalization"

But the docstring at the top doesn't explain that function names are normalized to lowercase with 'fn' prefix. The docstring shows examples like 'DEF FNR(X) = X * 2' but doesn't clarify that internally this becomes 'fnr'. This could confuse someone reading just the docstring without seeing the implementation details.

---

#### code_vs_comment

**Description:** PC class docstring describes stmt_offset as 'offset' but clarifies it's actually an array index, creating terminology confusion

**Affected files:**
- `src/pc.py`

**Details:**
Docstring says: "The stmt_offset is a 0-based index into the statements list for a line."
Then: "Note: stmt_offset is the list index (position in the statements array). The term 'offset' is used for historical reasons but it's simply the array index."

This acknowledges the terminology is misleading but doesn't fix it. The parameter and attribute are named 'stmt_offset' throughout but represent an index, not an offset.

---

#### code_vs_comment

**Description:** emit_keyword docstring says 'Caller is responsible for normalizing keyword to lowercase' but serialize_rem_statement passes stmt.comment_type.lower() which already normalizes

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword docstring:
"Note: Caller is responsible for normalizing keyword to lowercase before calling."

But in serialize_rem_statement:
result = self.emit_keyword(stmt.comment_type.lower(), stmt.column, "RemKeyword")

The caller is doing the normalization (.lower()) before calling emit_keyword, which contradicts the stated responsibility. If the caller must normalize, why does emit_keyword also call get_display_case which expects normalized input?

---

#### code_vs_comment

**Description:** serialize_let_statement docstring discusses 'AssignmentStatementNode' terminology but function only handles 'LetStatementNode'

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring:
"Note: LetStatementNode represents both explicit LET statements (LET A=5)
and implicit assignments (A=5) in MBASIC. The node name 'LetStatementNode'
is used consistently throughout the codebase.

In _adjust_statement_positions(), 'AssignmentStatementNode' was used historically
but has been replaced by 'LetStatementNode' for consistency."

This note about historical naming appears in serialize_let_statement but would be more appropriate in _adjust_statement_positions where the historical usage allegedly occurred. The placement suggests documentation was copied without proper context.

---

#### naming_confusion

**Description:** Two different modules with very similar names (resource_limits vs resource_locator) that serve completely different purposes, which could cause confusion

**Affected files:**
- `src/resource_limits.py`
- `src/resource_locator.py`

**Details:**
resource_limits.py: Handles runtime resource constraints (memory, stack depth, execution time)
resource_locator.py: Handles finding package data files (docs, help files)

These are completely unrelated functionalities but the similar naming pattern 'resource_*' suggests they might be related. Consider renaming one (e.g., 'package_locator.py' or 'execution_limits.py') to avoid confusion.

---

#### code_vs_comment

**Description:** Comment claims line=-1 distinguishes system/internal variables from debugger sets, but both use line=-1 making them indistinguishable

**Affected files:**
- `src/runtime.py`

**Details:**
In __init__ docstring for self._variables:
"Note: line -1 in last_write indicates non-program execution sources:
       1. System/internal variables (ERR%, ERL%) via set_variable_raw() with FakeToken(line=-1)
       2. Debugger/interactive prompt via set_variable() with debugger_set=True and token.line=-1
       Both use line=-1, making them indistinguishable from each other in last_write alone."

But in set_variable_raw() docstring:
"The line=-1 marker in last_write indicates system/internal variables.
However, debugger sets also use line=-1 (via debugger_set=True),
making them indistinguishable from system variables in last_write alone."

The __init__ comment correctly states they are indistinguishable, but the set_variable_raw() comment says "line=-1 marker indicates system/internal variables" which is misleading since debugger sets also use -1.

---

#### code_vs_comment

**Description:** get_variable() docstring says token is REQUIRED but allows fallback for missing line/position attributes

**Affected files:**
- `src/runtime.py`

**Details:**
get_variable() docstring states:
"Args:
    token: REQUIRED - Token object for tracking. Must not be None (ValueError raised if None).

           The token should have 'line' and 'position' attributes for tracking.
           If token is missing these attributes, fallback values are used:
           - Missing 'line' falls back to self.pc.line_num (or None if PC is halted)
           - Missing 'position' falls back to None"

This creates ambiguity: if token is REQUIRED but can have missing attributes with fallbacks, what is the actual contract? The implementation uses getattr() with fallbacks, suggesting tokens without line/position are acceptable. But the docstring emphasizes REQUIRED in caps, implying strict validation. The actual validation only checks 'if token is None', not attribute presence.

---

#### code_vs_comment

**Description:** Comment claims 'from_line' is redundant with 'return_line' and kept for backward compatibility, but the code sets 'from_line' to the same value as 'return_line', making them truly identical rather than just redundant

**Affected files:**
- `src/runtime.py`

**Details:**
In get_execution_stack() method:

Comment says:
"Note: 'from_line' is redundant with 'return_line' - both contain the same value
(the line number to return to after RETURN). The 'from_line' field exists
for backward compatibility with code that expects it. Use 'return_line'
for new code as it more clearly indicates the field's purpose."

Code implementation:
result.append({
    'type': 'GOSUB',
    'from_line': entry.get('return_line', 0),  # Line to return to
    'return_line': entry.get('return_line', 0),
    'return_stmt': entry.get('return_stmt', 0)  # Statement offset
})

The comment suggests 'from_line' might have had a different historical meaning, but the code shows they are literally the same value from the same source.

---

#### code_vs_comment

**Description:** Comment in load() method claims settings are NOT unflattened after loading, but this contradicts the actual storage format and usage pattern

**Affected files:**
- `src/settings.py`

**Details:**
In settings.py load() method:
Comment says: "However, load() intentionally does NOT call _unflatten_settings() - it keeps settings in flattened format after loading. This is by design because _get_from_dict() can handle both flattened ('editor.auto_number': True) and nested ({'editor': {'auto_number': True}}) formats."

But _get_from_dict() implementation shows:
```
if '.' in key:
    parts = key.split('.', 1)
    category = parts[0]
    subkey = parts[1]
    if category in settings_dict and isinstance(settings_dict[category], dict):
        return settings_dict[category].get(subkey)
return settings_dict.get(key)
```

This code expects nested format for dotted keys (checks isinstance(settings_dict[category], dict)). If settings remain flattened as {'editor.auto_number': True}, the nested lookup path would fail and fall through to direct key lookup. The comment claims both formats work, but the code structure suggests nested format is expected for proper category-based organization.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about global settings path between SettingsManager and FileSettingsBackend

**Affected files:**
- `src/settings.py`
- `src/settings_backend.py`

**Details:**
src/settings.py module docstring:
"- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)"

src/settings_backend.py FileSettingsBackend docstring:
"Stores settings in JSON files:
- Global: ~/.mbasic/settings.json"

The FileSettingsBackend docstring omits Windows path information, while SettingsManager includes it. Both classes implement the same logic for Windows (%APPDATA%/mbasic), so documentation should be consistent.

---

#### code_vs_comment

**Description:** RedisSettingsBackend docstring claims settings are initialized from default file-based settings, but constructor makes this optional

**Affected files:**
- `src/settings_backend.py`

**Details:**
RedisSettingsBackend class docstring:
"Stores settings in Redis with per-session isolation:
- Key format: nicegui:settings:{session_id}
- Each session has independent settings
- Initialized from default file-based settings
- No disk writes in this mode (read-only from disk)"

But __init__ signature:
```
def __init__(self, redis_client, session_id: str, default_settings: Optional[Dict[str, Any]] = None):
    ...
    # Initialize with defaults if not already in Redis
    if default_settings and not self._exists():
        self.save_global(default_settings)
```

The default_settings parameter is Optional and only used if provided AND settings don't exist. The docstring claims settings are "Initialized from default file-based settings" but this is conditional, not guaranteed. If default_settings=None, no initialization occurs.

---

#### documentation_inconsistency

**Description:** BREAK command documentation states 'Breakpoints are only activated when the RUN command is executed' but the implementation shows breakpoints are checked during execution, not just at RUN time

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
cmd_break docstring: 'Breakpoints are only activated when the RUN command is executed. After setting breakpoints, use RUN to start/restart the program for them to take effect.'
However, _install_breakpoint_handler shows: 'def breakpoint_execute():\n    """Execute with breakpoint checking"""\n    # Check current line for breakpoint\n    if interpreter.runtime.current_line:\n        line_num = interpreter.runtime.current_line.line_number\n        if line_num in self.breakpoints:'
This suggests breakpoints are checked during execution, not just at RUN initialization.

---

#### code_vs_comment

**Description:** Comment says 'Create footer with keyboard shortcuts (instead of button widgets)' but the implementation creates Text widget, not actual keyboard shortcuts

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment at line in _create_body: '# Create footer with keyboard shortcuts (instead of button widgets)'
Followed by: 'footer_text = urwid.Text(f"↑↓ {key_to_display(ENTER_KEY)}=OK  ...", align=\'center\')'
The comment suggests this is an alternative to button widgets, but doesn't clarify why buttons aren't used or what the previous implementation was.

---

#### code_vs_documentation

**Description:** UIBackend base class documents optional command methods but CLIBackend implements them by delegating to InteractiveMode, creating unclear contract about which methods are required vs optional

**Affected files:**
- `src/ui/base.py`
- `src/ui/cli.py`

**Details:**
base.py docstring: '# Optional: Standard commands that backends may implement\n# (CLI implements these, GUI may have different UX)'
Followed by method definitions: 'def cmd_run(self) -> None: pass'
But cli.py implements all these methods: 'def cmd_run(self) -> None: """Execute RUN command.""" self.interactive.cmd_run()'
The base class says these are optional but provides no guidance on what a minimal implementation requires, and the CLI implementation suggests they might be expected.

---

#### code_vs_documentation

**Description:** SettingsWidget._on_apply method emits 'applied' signal but there's no signal handling mechanism visible in the code, only a stored attribute

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
_on_apply method: 'if self._apply_settings():\n    # Update original values so Cancel won\'t revert\n    self._load_current_values()\n    # Signal success (parent will show message)\n    self._emit(\'applied\')'
_emit implementation: 'def _emit(self, signal: str):\n    """Emit a signal to parent.\n\n    Args:\n        signal: Signal name (\'close\', \'applied\')\n    """\n    # Store signal for parent to check\n    self.signal = signal'
The comment says 'Emit a signal to parent' but the implementation just stores it in an attribute. There's no actual signal emission mechanism or parent notification.

---

#### code_vs_comment

**Description:** Comment describes line number format as fixed 5 characters, but code implements variable width line numbers

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring says:
"Display format: 'S<linenum> CODE' where:
- Field 1 (1 char): Status (●=breakpoint, ?=error, space=normal)
- Field 2 (variable width): Line number (no padding for display)
- Field 3 (rest of line): Program text (BASIC code)

Note: Line numbers use variable width (not fixed 5 chars) for flexibility with large programs."

But _format_line method comment says:
"Format a single program line with status, line number, and code.

Returns:
    Formatted string or urwid markup: 'S<num> CODE' where S is status (1 char),
    <num> is the line number (variable width, no padding), and CODE is the program text."

The code consistently implements variable width throughout, but the class docstring has a confusing note that mentions 'not fixed 5 chars' suggesting there was a previous fixed-width implementation.

---

#### code_vs_comment

**Description:** Comment describes handling multiple line numbers but implementation behavior is unclear

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_number method:
"Extract line number from display line.

Format: 'SNN CODE' where S=status, NN=line number (variable width)

Handles multiple line numbers by keeping the last one found.
Example: '?10 100 for...' returns 100, since 'for' stops the search."

However, the example is confusing - if 'for' stops the search, why would it find 100? The code loops through numbers and keeps the last valid one before hitting a non-digit that's not followed by space. The comment example doesn't clearly illustrate this behavior.

---

#### code_vs_comment

**Description:** Inconsistent documentation about when syntax errors are displayed

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The _update_syntax_errors method docstring says:
"Update status indicators for lines with syntax errors.

Args:
    text: Current editor text

Returns:
    Updated text with '?' status for lines with parse errors"

But the method also calls _display_syntax_errors() which shows errors in the output window. The docstring only mentions updating status indicators, not displaying errors in output.

---

#### code_vs_comment

**Description:** Comment about FAST PATH optimization contradicts actual implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress method:
"# FAST PATH: For normal printable characters, bypass all processing
# This is critical for responsive typing
if len(key) == 1 and key >= ' ' and key <= '~':
    return super().keypress(size, key)

# No expensive processing here - just set flags and let enter_idle callback handle it"

But immediately after the fast path, there IS expensive processing for special keys: parsing line numbers, checking syntax errors, sorting lines. The comment 'No expensive processing here' is misleading - it should say 'No expensive processing for normal characters' or be placed differently.

---

#### code_vs_comment

**Description:** Comment claims toolbar was removed but method still exists and is fully implemented

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1050 says:
"Note: This method is no longer used (toolbar removed from UI in favor of Ctrl+U menu
for better keyboard navigation). The method is retained for reference and potential
future re-enablement, but can be safely removed if the toolbar is not planned to return."

However, the _create_toolbar() method contains a complete, working implementation with buttons for New, Open, Save, Run, Stop, Step, Stmt, and Cont. The method creates urwid.Button widgets with proper callbacks and styling.

---

#### code_vs_comment

**Description:** Inconsistent documentation about IO handler lifecycle and recreation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment block around line ~900 states:
"# IO Handler Lifecycle:
# 1. self.io_handler (CapturingIOHandler) - Used for RUN program execution
#    Captures output to display in output window, defined inline above
# 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands
#    Created here and recreated in start() with fresh instance"

However, in __init__, self.io_handler is created once as CapturingIOHandler and never recreated. The immediate_io is created in __init__ and then recreated in start(). The comment suggests both are recreated, but only immediate_io is.

---

#### code_vs_comment

**Description:** Inconsistent comments about status bar updates across debug methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple debug methods have comments saying 'Status bar stays at default' or 'No status bar update', but then the code updates the status bar:

_debug_step() line ~1450: '# (No status bar update - output will show in output window)' but then line ~1490 calls self.status_bar.set_text()

_debug_step_line() line ~1540: '# (No status bar update - output will show in output window)' but then line ~1580 calls self.status_bar.set_text()

_debug_stop() line ~1620: '# Status bar stays at default - stop message is in output' but this one actually doesn't update status bar, making it inconsistent with the others.

---

#### code_vs_comment

**Description:** Comment claims breakpoints are stored in editor and NOT in runtime, but code shows breakpoints ARE cleared by reset_for_run() and must be re-applied

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1050 says:
"Note: reset_for_run() clears variables and resets PC. Breakpoints are stored in
the editor (self.editor.breakpoints), NOT in runtime, so they persist across runs
and are re-applied below via interpreter.set_breakpoint() calls."

But immediately after, code shows:
"# Re-apply breakpoints from editor
# Breakpoints are stored in editor UI state and must be re-applied to interpreter
# after reset_for_run (which clears them)
for line_num in self.editor.breakpoints:
    self.interpreter.set_breakpoint(line_num)"

The comment says breakpoints are NOT in runtime and persist, but the code explicitly re-applies them because reset_for_run() clears them from the interpreter/runtime.

---

#### code_vs_comment

**Description:** Comment about statement-level precision for GOSUB contradicts default value handling

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_stack_window() at line ~950:
"# Show statement-level precision for GOSUB return address
# Note: default of 0 if return_stmt is missing means first statement on line
return_stmt = entry.get('return_stmt', 0)
line = f"{indent}GOSUB from line {entry['from_line']}.{return_stmt}"

The comment says 'default of 0 if return_stmt is missing means first statement on line', but this is misleading. If return_stmt is missing, it defaults to 0, which would display as 'line X.0'. However, the comment implies this is semantically meaningful (first statement), when it might just be a missing value. The display format 'line.statement' suggests statement numbering starts at 0, but this is not clarified.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC during execution, but code resets PC to halted when not running or paused at breakpoint

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in _execute_immediate (line ~1050): "Sync program to runtime (updates statement table and line text map).\nIf execution is running, _sync_program_to_runtime preserves current PC.\nIf not running, it sets PC to halted."

But _sync_program_to_runtime code (line ~450): "if self.running and not self.paused_at_breakpoint:\n    # Execution is running - preserve execution state\n    self.runtime.pc = old_pc\n    self.runtime.halted = old_halted\nelse:\n    # No execution in progress - ensure halted\n    self.runtime.pc = PC.halted_pc()\n    self.runtime.halted = True"

The comment says PC is preserved when running, but code shows PC is reset to halted when paused_at_breakpoint is True, even if running is True.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says interpreter.start() shouldn't be called because immediate executor already called it, but this assumption may not hold for all commands

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1120: "# NOTE: Don't call interpreter.start() here - the immediate executor already\n# called it if needed (e.g., 'RUN 120' called interpreter.start(start_line=120)\n# to set PC to line 120). Calling it again would reset PC to the beginning.\n# We only initialize InterpreterState if it doesn't exist (first run of session),\n# which sets up tracking state without modifying PC/runtime state."

This assumes immediate executor always calls start() when needed, but there's no verification that this contract is maintained. If immediate executor changes or new commands are added, this could break.

---

#### code_vs_comment

**Description:** Duplicate CapturingIOHandler class definition with comment suggesting it should be extracted to shared location

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1090: "# Need to create the CapturingIOHandler class inline\n# (duplicates definition in _run_program - consider extracting to shared location)"

The CapturingIOHandler class is defined inline in _execute_immediate, and the comment acknowledges it duplicates the definition in _run_program. This is a code smell indicating the classes should be unified, but the comment only suggests consideration rather than documenting why it hasn't been done.

---

#### code_vs_comment_conflict

**Description:** Comment describes tier label mapping but code has incomplete mapping that results in '📙 Other' for unrecognized tiers, while comment doesn't mention this fallback behavior clearly.

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~145 states:
"Note: UI tier (e.g., 'ui/curses', 'ui/tk') is detected via startswith('ui/')
check below and gets '📘 UI' label. Other unrecognized tiers get '📙 Other'."

Code at line ~158:
tier_labels = {
    'language': '📕 Language',
    'mbasic': '📗 MBASIC',
}

Then at line ~175:
if tier_name.startswith('ui/'):
    tier_label = '📘 UI'
else:
    tier_label = tier_labels.get(tier_name, '📙 Other')

The comment accurately describes the behavior. This is actually consistent.

---

#### code_vs_documentation_inconsistency

**Description:** help_macros.py docstring says HelpMacros searches all sections for kbd actions, but help_widget.py hardcodes 'curses' as ui_name when initializing HelpMacros, creating a mismatch between the generic documentation and specific implementation.

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/help_widget.py`

**Details:**
help_macros.py docstring:
"{{kbd:help}} → looks up 'help' action in keybindings (searches all sections)
                  and returns the primary keybinding for that action"

help_widget.py line ~48:
"# HelpWidget is curses-specific (uses urwid), so hardcode 'curses' UI name
self.macros = HelpMacros('curses', help_root)"

The docstring implies generic behavior across UIs, but the implementation is hardcoded to 'curses'. This is a documentation clarity issue - the docstring should note that the UI name determines which keybindings file is loaded.

---

#### code_vs_comment_conflict

**Description:** Comment describes _expand_kbd searching all sections, but the actual search behavior and the relationship to help widget's hardcoded navigation keys creates confusion about keybinding architecture.

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
help_macros.py _expand_kbd docstring:
"Expand keyboard shortcut macro by searching for action name across all sections.

Args:
    key_name: Name of key action (e.g., 'help', 'save', 'run').
             This is searched across all keybinding sections (editor, help_browser, etc.)

Returns:
    Primary key combination or original macro if not found

Example:
    _expand_kbd('help') searches all sections for an action named 'help'
    and returns its primary keybinding (e.g., '^H')"

But help_widget.py comment says help navigation keys are hardcoded and don't use keybindings. This creates architectural confusion - are help keys configurable via keybindings or not? The {{kbd:help}} macro would expand to the configured key, but the help widget itself uses hardcoded keys.

---

#### code_vs_comment_conflict

**Description:** Comment says 'If help navigation keys change, update here and keypress()' but doesn't mention updating the footer text which also displays the keys, creating incomplete maintenance instructions.

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~95:
"Note: Help navigation keys are hardcoded here and in keypress() method, not loaded from
keybindings. The help widget uses fixed keys (U for back, / for search, ESC/Q to exit)
to avoid dependency on keybinding configuration. HelpMacros does load the full keybindings
from JSON (for {{kbd:action}} macro expansion in help content), but the help widget itself
doesn't use those loaded keybindings. If help navigation keys change, update here and keypress()."

But the footer text at line ~92 also hardcodes the keys:
"self.footer = urwid.Text(" ↑/↓=Scroll →/←=Next/Prev Link Enter=Follow /=Search U=Back ESC/Q=Exit ")"

If keys change, the footer text must also be updated, but the comment doesn't mention this.

---

#### code_inconsistency

**Description:** Both HelpMacros and KeybindingLoader load keybindings from JSON files using similar patterns, but they don't share code. This duplication could lead to inconsistencies if the loading logic needs to change.

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/keybinding_loader.py`

**Details:**
help_macros.py _load_keybindings():
"keybindings_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"
if keybindings_path.exists():
    try:
        with open(keybindings_path, 'r') as f:
            return json.load(f)
    except Exception:
        pass
return {}"

keybinding_loader.py _load_config():
"config_path = Path(__file__).parent / f"{self.ui_name}_keybindings.json"
if config_path.exists():
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        pass
return {}"

These are nearly identical. They should share a common loading function to avoid divergence.

---

#### Code vs Comment conflict

**Description:** Comment says 'Step Line - execute all statements on current line' but variable is named LIST_KEY, which is confusing and doesn't match the action name

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line ~115:
# Step Line - execute all statements on current line (debugger command)
_list_from_json = _get_key('editor', 'step_line')
LIST_KEY = _ctrl_key_to_urwid(_list_from_json) if _list_from_json else 'ctrl k'

The variable name LIST_KEY doesn't match the action 'step_line' or the description 'Step Line'. This appears to be a naming inconsistency where the variable should be STEP_LINE_KEY.

---

#### Documentation inconsistency

**Description:** KEYBINDINGS_BY_CATEGORY shows 'Step Line' and 'Step Statement' as separate actions, but the code only defines LIST_KEY (step_line) and STEP_KEY (step), creating confusion about terminology

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
In KEYBINDINGS_BY_CATEGORY:
(key_to_display(LIST_KEY), 'Step Line - execute all statements on current line'),
(key_to_display(STEP_KEY), 'Step Statement - execute one statement at a time'),

But in code:
LIST_KEY is loaded from 'step_line'
STEP_KEY is loaded from 'step'

The terminology 'Step Statement' is not used anywhere else in the code, only in the documentation string.

---

#### Code vs Comment conflict

**Description:** STATUS_BAR_SHORTCUTS references LIST_KEY with description 'step line' but this key's purpose is unclear given the variable naming confusion

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line ~235:
STATUS_BAR_SHORTCUTS = f"MBASIC - {key_to_display(HELP_KEY)} help  {key_to_display(MENU_KEY)} menu  {key_to_display(VARIABLES_KEY)} vars  {key_to_display(LIST_KEY)} step line  {key_to_display(TAB_KEY)} cycle  ↑↓ scroll"

This uses LIST_KEY but describes it as 'step line', which is inconsistent with the variable name.

---

#### Code vs Documentation inconsistency

**Description:** ESC key binding to close in-page search is implemented but not documented in keybindings

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
In tk_help_browser.py line 142-144:
# Note: ESC closes search bar - this is not documented in tk_keybindings.json
# as it's a local widget binding rather than a global application keybinding
self.inpage_search_entry.bind('<Escape>', lambda e: self._inpage_search_close())

The comment explicitly states this is not documented in tk_keybindings.json. However, tk_keybindings.json has a 'help_browser' section that documents other help browser keybindings like Ctrl+F. The ESC binding should be documented there for completeness, even if it's a local binding.

---

#### code_vs_comment

**Description:** Comment describes 3-pane layout with specific weight ratios, but code implements 3 panes with different weights than documented

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line 58-62 states:
    - Editor with line numbers (top, ~50% - weight=3)
    - Output pane (middle, ~33% - weight=2)
    - Immediate mode input line (bottom, ~17% - weight=1)

However, the code at lines 158-176 creates:
    - editor_frame with weight=3
    - output_frame with weight=2
    - immediate_frame with weight=1

The percentages don't match the weights: weight=3 is 50%, weight=2 is 33%, weight=1 is 17%, totaling 100%. But with weights 3:2:1, the actual distribution is 50%:33.3%:16.7%, which matches. The comment is correct but could be clearer that these are approximate percentages.

---

#### code_vs_comment

**Description:** Comment describes INPUT row as 'shown/hidden dynamically for INPUT statements' but implementation details suggest it's always created but not packed

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line 61 in docstring states:
        - Contains INPUT row (shown/hidden dynamically for INPUT statements)

Lines 189-191 show:
        # INPUT row (hidden by default, shown when INPUT statement needs input)
        self.input_row = ttk.Frame(output_frame, height=40)
        # Don't pack yet - will be packed when needed

The comment is accurate but the docstring could be clearer that 'shown/hidden' is implemented via pack/pack_forget rather than show/hide visibility.

---

#### code_vs_comment

**Description:** Comment describes _ImmediateModeToken as marking edits from 'variable inspector or immediate mode' but the token is only used for line=-1 signaling

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 20-27 state:
    """Token for variable edits from immediate mode or variable editor.

    Used to mark variable changes that originate from the variable inspector
    or immediate mode, not from program execution. The line=-1 signals to
    runtime.set_variable() that this is a debugger/immediate mode edit.
    """

The class only has line=-1 and position=None attributes. The docstring suggests it's used to 'mark variable changes' but the implementation is just a simple token with line=-1. It's unclear if this token is actually passed to runtime.set_variable() or if it's just a placeholder.

---

#### code_vs_comment

**Description:** Comment at line 697 describes heading click behavior but the actual implementation in _on_variable_heading_click may not match all described behaviors

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 697-702:
        """Handle clicks on variable list column headings.

        Only the Variable column (column #0) is sortable - clicking it cycles through
        different sort modes (accessed, written, read, name, type, value).
        Type and Value columns are not sortable.
        """

The implementation at lines 704-732 shows logic for determining click position (arrow vs text) and calling _toggle_variable_sort_direction() or _cycle_variable_sort(), but the actual cycling through 'accessed, written, read, name, type, value' modes is not visible in this code snippet. The methods _toggle_variable_sort_direction() and _cycle_variable_sort() are called but not defined in the shown code.

---

#### code_vs_comment

**Description:** Comment claims OPTION BASE only allows 0 or 1, but code has defensive else clause for other values

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1090-1100:
Comment: "OPTION BASE only allows 0 or 1. The else clause is defensive programming to handle any unexpected values (should not occur in correct implementations)."

Code:
if array_base == 0:
    default_subscripts = ','.join(['0'] * len(dimensions))
elif array_base == 1:
    default_subscripts = ','.join(['1'] * len(dimensions))
else:
    # Defensive fallback for invalid array_base (should not occur)
    default_subscripts = ','.join(['0'] * len(dimensions))

The comment states OPTION BASE only allows 0 or 1, making the else clause unnecessary if this is enforced elsewhere. Either the validation is missing (making the else clause necessary), or the comment is outdated.

---

#### code_vs_comment

**Description:** Comment about preserving final blank line contradicts Tk Text widget behavior claim

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1895-1900 in _remove_blank_lines:
Comment: "Removes blank lines to keep program clean, but preserves the final line which is always blank in Tk Text widget (internal Tk behavior)."

Code at line ~1915:
for i, line in enumerate(lines):
    if line.strip() or i == len(lines) - 1:
        filtered_lines.append(line)

The comment claims the final line is 'always blank' due to Tk behavior, but the code explicitly preserves it with 'i == len(lines) - 1'. If it's always blank due to Tk, why does the code need to preserve it? This suggests either the comment is wrong about Tk behavior, or the code is doing unnecessary work.

---

#### code_vs_comment

**Description:** Comment claims clearing statement highlight prevents visual artifact when text is modified, but code clears highlight on ANY keypress including non-editing keys

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1180 says:
# Clear yellow statement highlight on any keypress when paused at breakpoint
# This prevents visual artifact where statement highlight remains on part of a line
# after text is modified (occurs because highlight is tag-based and editing shifts positions).
# Note: This clears on ANY key including arrows/function keys, not just editing keys.

The comment acknowledges clearing on ANY key but justifies it by preventing artifacts 'after text is modified'. However, arrow keys and function keys don't modify text, so the justification doesn't match the behavior. The code clears highlight even when no modification occurs.

---

#### code_vs_comment

**Description:** Comment describes two cases for multi-line paste logic but the code structure doesn't clearly separate these cases

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1127 says:
# Multi-line paste or single-line paste into blank line - use auto-numbering logic
# This handles two cases:
# 1. Multi-line paste (sanitized_text contains \n) - auto-number if needed
# 2. Single-line paste into blank line (current_line_text is empty) - auto-number if needed

However, the code that follows doesn't have separate branches for these two cases. Both cases flow through the same logic path. The comment suggests two distinct scenarios but the implementation treats them identically.

---

#### code_vs_comment

**Description:** Comment says 'Lines are displayed exactly as stored' but this contradicts the auto-numbering and sanitization logic that modifies lines before display

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1656 says:
# Lines are displayed exactly as stored, so char_start/char_end
# are relative to the line as displayed

This comment appears in _highlight_current_statement(). However, throughout the file there is extensive logic for auto-numbering, paste sanitization, blank line removal, and line sorting that modifies lines before display. The statement 'exactly as stored' is misleading.

---

#### code_vs_comment

**Description:** Comment describes CONT behavior but doesn't mention that it checks runtime.stopped flag, which is critical to understanding when CONT is valid

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring at line ~1688 says:
"""Execute CONT command - continue after STOP.

Resumes execution after:
- STOP statement
- Ctrl+C/Break
- END statement (in some cases)

Invalid if program was edited after stopping.

The interpreter moves NPC to PC when STOP is executed (see execute_stop()
in interpreter.py). CONT simply clears the stopped/halted flags and resumes
tick-based execution, which continues from the PC position.
"""

The docstring says 'Invalid if program was edited after stopping' but doesn't explain that this is enforced by checking runtime.stopped flag. The code at line ~1695 checks 'if not self.runtime or not self.runtime.stopped' but this critical validation isn't mentioned in the docstring.

---

#### code_vs_comment

**Description:** Comment claims immediate_history is always None but _setup_immediate_context_menu() references it as if it exists

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _add_immediate_output() docstring: "Note: self.immediate_history exists but is always None (see __init__) - it's a dummy attribute for compatibility with code that references it."

But _setup_immediate_context_menu() contains:
  def show_context_menu(event):
    menu = tk.Menu(self.immediate_history, tearoff=0)
    ...
    if self.immediate_history.tag_ranges(tk.SEL):

This would fail with AttributeError if immediate_history is None.

---

#### code_vs_comment

**Description:** Comment says has_work() complements runtime flag checks but code only uses it in one specific case

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _execute_immediate() states: "Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command). This complements runtime flag checks (self.running, runtime.halted) used elsewhere."

However, has_work() is only called once in this specific location after immediate command execution. The comment implies it's used as a general complement to runtime flags throughout the codebase, but this appears to be the only usage shown.

---

#### code_vs_comment

**Description:** Comment about execute() not echoing conflicts with typical immediate mode behavior expectations

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _execute_immediate() states: "Execute without echoing (GUI design choice: command is visible in entry field, and 'Ok' prompt is unnecessary in GUI context - only results are shown)"

This design choice is documented but may be inconsistent with user expectations from traditional BASIC interpreters where commands are echoed to output. The comment justifies it but doesn't note this deviation from typical BASIC behavior.

---

#### code_vs_comment

**Description:** Comment about input_line() ALWAYS using modal dialog conflicts with input() fallback behavior

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler.input_line() docstring: "Unlike input() which prefers inline input field, this ALWAYS uses a modal dialog regardless of backend availability."

But input() also uses modal dialog as fallback when backend is unavailable. The distinction is that input_line() NEVER tries inline input, while input() prefers it. The comment could be clearer about this being a preference vs. absolute difference.

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

**Description:** Comment in _delete_line() docstring describes line_num parameter incorrectly regarding what it represents

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring says: "line_num: Tkinter text widget line number (1-based sequential index), not BASIC line number (e.g., 10, 20, 30)"

This is correct, but the implementation in _on_cursor_move() uses self.current_line which is set from cursor_pos.split('.')[0], and this value is used directly in _delete_line(). The clarification is good, but there's potential confusion because line_metadata uses BASIC line numbers while _delete_line uses editor line numbers. The distinction is documented but the dual numbering system throughout the class could lead to bugs.

---

#### code_vs_comment

**Description:** Docstring for _on_status_click() states it does NOT toggle breakpoints, but there's no clear documentation of how breakpoints ARE toggled

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring: "Note: This displays information/confirmation messages only. It does NOT toggle breakpoints or show detailed breakpoint info - that must be done through the UI's breakpoint commands and debugger windows."

This explicitly states what the method doesn't do, but there's no reference to what methods or UI components DO handle breakpoint toggling. The set_breakpoint() method exists but there's no documentation of what calls it or how users interact with it.

---

#### code_vs_comment

**Description:** Comment in update_line_references() describes pattern as using non-greedy match for ON expressions, but warns about potential issues with expressions containing 'G'. However, the pattern should handle this correctly.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment says: "Note: Pattern uses .+? (non-greedy) to match expression in ON statements,\n# which allows expressions containing any characters including 'G' (e.g., ON FLAG GOTO)"

The non-greedy match .+? followed by \s+GOTO should correctly handle expressions like 'FLAG' that contain 'G', as the non-greedy quantifier will stop at the first match of '\s+GOTO'. The comment seems to suggest this might be problematic, but the regex should work correctly.

---

#### code_vs_comment

**Description:** Comment in serialize_variable() says 'Don't add suffixes that were inferred from DEF statements' but the code checks explicit_type_suffix attribute which may not exist on all VariableNode instances.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment: "# Only add type suffix if it was explicit in the original source\n# Don't add suffixes that were inferred from DEF statements\n# Note: getattr defaults to False if explicit_type_suffix is missing, preventing suffix output"

Code: "if var.type_suffix and getattr(var, 'explicit_type_suffix', False):"

The comment explains the intent, but it's unclear if all VariableNode instances are guaranteed to have the explicit_type_suffix attribute set correctly. If some nodes don't have this attribute, they'll default to False and lose their type suffix during serialization, which could be a bug.

---

#### code_vs_documentation

**Description:** renum_program() docstring says callback is 'responsible for identifying and updating statements with line number references' but doesn't specify which statement types need updating or provide examples.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says: "renum_callback: Function that takes (stmt, line_map) to update statement references.\n                        Called for ALL statements; callback is responsible for identifying and\n                        updating statements with line number references (GOTO, GOSUB, ON GOTO,\n                        ON GOSUB, IF THEN/ELSE line numbers)"

The documentation lists some statement types but doesn't provide:
1. A complete list of all statement types that contain line number references
2. Example callback implementation
3. What attributes of each statement type need updating
4. Whether the callback should modify statements in-place or return new ones

---

#### Documentation inconsistency

**Description:** Docstring example shows 'self.cmd_save("program.bas")' but actual method signature requires filename parameter

**Affected files:**
- `src/ui/visual.py`

**Details:**
Docstring example in start() method:
'self.window.save_button.connect(lambda: self.cmd_save("program.bas"))'

Actual method signature:
'def cmd_save(self, filename: str) -> None:'

The example is correct, but it's inconsistent with how other examples show method calls without parameters. This could confuse developers about whether filename is required.

---

#### Code vs Documentation inconsistency

**Description:** cmd_delete and cmd_renum methods are documented but not implemented (only pass statements)

**Affected files:**
- `src/ui/visual.py`

**Details:**
Both methods have docstrings describing functionality:

'def cmd_delete(self, args: str) -> None:
    """Execute DELETE command - delete line range."""
    # Parse args (e.g., "10-50" or "100")
    # Call self.program.delete_line() or delete_range()
    pass'

'def cmd_renum(self, args: str) -> None:
    """Execute RENUM command - renumber lines."""
    # Parse args for new_start and increment
    # Call self.program.renumber()
    pass'

These are stub implementations but the docstrings suggest they should work.

---

#### Code vs Documentation inconsistency

**Description:** cmd_cont method is documented but not implemented (only pass statement)

**Affected files:**
- `src/ui/visual.py`

**Details:**
'def cmd_cont(self) -> None:
    """Execute CONT command - continue after STOP."""
    # Resume execution if runtime is in stopped state
    pass'

The docstring describes functionality but the method does nothing. This is a stub class, but it's unclear if this is intentional or incomplete.

---

#### code_vs_comment

**Description:** Docstring claims breakpoint support is 'planned - not yet implemented' but doesn't indicate if this is accurate

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1009-1010 in NiceGUIBackend docstring:
- Breakpoint support (planned - not yet implemented)

This is a status comment in documentation that may be outdated. Without seeing the full implementation, it's unclear if breakpoints have been implemented since this comment was written.

---

#### code_vs_comment

**Description:** Comment claims RUN does NOT clear output, but this contradicts the documented behavior and user expectations

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1806 comment: "# Don't clear output - continuous scrolling like ASR33 teletype
# Note: Step commands (Ctrl+T/Ctrl+K) DO clear output for clarity when debugging"

However, the _menu_run method does not call _clear_output(), while _menu_step_line and _menu_step_stmt both call _clear_output() at lines ~2050 and ~2109. This creates inconsistent behavior where stepping clears output but running doesn't.

---

#### code_vs_comment

**Description:** Comment about INPUT handling references lines that don't match the actual implementation location

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1603 comment: "# INPUT handling: When INPUT statement executes, the immediate_entry input box
# is focused for user input (see _execute_tick() lines ~1886-1888)."

The _execute_tick method is defined around line ~1851, and the input handling logic spans multiple locations (lines ~1862-1870, ~1886-1896). The comment's line reference is imprecise.

---

#### internal_code_inconsistency

**Description:** Inconsistent handling of empty programs between RUN and STEP commands

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _menu_run (line ~1800): "# If empty program, just show Ready (variables cleared, nothing to execute)
if not self.program.lines:
    self._set_status('Ready')
    self.running = False
    return"

In _menu_step_line (line ~2044) and _menu_step_stmt (line ~2103): "# If empty program, just show Ready (matches RUN behavior - silent success)
if not self.program.lines:
    self._set_status('Ready')
    self.running = False
    return"

Both handle empty programs identically, but RUN doesn't clear output while STEP commands do (via _clear_output() calls at lines ~2050 and ~2109). This creates an inconsistency in user experience.

---

#### code_vs_comment

**Description:** Comment about INPUT prompt handling contradicts the actual implementation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1866 comment: "# Note: We don't append the prompt to output here because the interpreter
# has already printed it via io.output() before setting input_prompt state"

This same comment appears twice (lines ~1866 and ~1891), but there's no verification in the code that the interpreter actually did print the prompt. If the interpreter didn't print it, the user would see no prompt at all.

---

#### internal_code_inconsistency

**Description:** Inconsistent timer cancellation patterns - defensive programming not applied uniformly

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _menu_continue (line ~2234): "# Cancel any existing timer first (defensive programming - prevents multiple timers)
if self.exec_timer:
    self.exec_timer.cancel()
    self.exec_timer = None"

But in _menu_run (line ~1783), the timer is cancelled without the "defensive programming" comment, and in _menu_stop (line ~1949) it's also cancelled. The comment suggests this is a special concern for Continue, but it should apply to all timer management.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC only if exec_timer is active, but the actual logic is about preventing accidental execution starts, not about preserving state during active execution

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says: 'Preserves current PC/execution state only if exec_timer is active; otherwise resets PC to halted. This allows LIST and other commands to see the current program without starting execution.'

But the comment in the code says: '# This logic is about PRESERVING vs RESETTING state, not about preventing accidental starts'

These two explanations contradict each other about the purpose of the conditional PC restoration.

---

#### code_vs_comment

**Description:** Comment in _on_editor_change describes detecting paste by content difference, but the threshold (>5 chars) seems arbitrary and may not reliably detect pastes

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# Detect paste: large content change (more than 1-2 chars difference from last tracked)'
Code: 'if content_diff > 5:'

The comment says '1-2 chars' but the code uses '>5', and this heuristic may fail for small pastes or rapid typing.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'Don't create temporary ones!' but doesn't explain why or what the alternative was

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# Use the session's single interpreter and runtime
# Don't create temporary ones!'

This suggests there was a previous bug or design where temporary objects were created, but without context it's unclear if the current implementation is correct or if there are edge cases.

---

#### code_vs_comment

**Description:** Comment in _check_auto_number says 'Only auto-numbers a line once' but the implementation checks if line existed in previous snapshot, which may not prevent all duplicate numbering

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring: 'Only auto-numbers a line once - tracks the last snapshot to avoid re-numbering lines while user is still typing on them.'

Code checks: 'if stripped and (i < len(old_lines) or len(lines) > len(old_lines)):'

The logic seems to allow numbering if line count increased, which could still number a line multiple times if user adds/removes lines.

---

#### code_vs_comment

**Description:** Comment in _serialize_runtime says 'Close open files first' but _close_all_files method is not shown in the provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Code: '# Close open files first
self._close_all_files()'

The _close_all_files method is called but not defined in the provided code snippet, making it unclear if this is implemented or if the comment is outdated.

---

#### code_vs_comment

**Description:** Docstring says 'Not implemented - raises NotImplementedError' but the method IS implemented (it calls app.shutdown())

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Method: stop()
Docstring: 'Not implemented - raises NotImplementedError.\n\nUse start_web_ui() module function instead for web backend.'
Actual code: 'app.shutdown()'
The docstring is incorrect - the method is implemented and does not raise NotImplementedError.

---

#### documentation_inconsistency

**Description:** Version string 'MBASIC 5.21' in UI title doesn't match VERSION constant usage pattern - VERSION is imported but hardcoded string is used in ui.run()

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~467: 'sys.stderr.write(f"MBASIC Web UI Starting - Version {VERSION}\n")' uses VERSION variable
Line ~540: 'ui.run(title=\'MBASIC 5.21 - Web IDE\', ...' hardcodes '5.21'
If VERSION changes, the title won't update automatically.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for toggling breakpoints between Curses and Tk UIs

**Affected files:**
- `docs/help/common/editor-commands.md`
- `docs/help/common/debugging.md`

**Details:**
editor-commands.md states: 'Toggle breakpoint (Curses: **b**, Tk: **Ctrl+B**)'

But debugging.md under 'Setting Breakpoints' states:
- Tk UI: 'Click the line number gutter next to the line' OR 'position cursor on the line and press **Ctrl+B**'
- Curses UI: 'Position cursor on the line and press **b**'

The Tk UI section in debugging.md mentions both clicking AND Ctrl+B, while editor-commands.md only mentions Ctrl+B for Tk. This is consistent but could be clearer. However, the table format in editor-commands.md makes it look like 'b' is an alternative to Ctrl+B for all UIs, when 'b' is Curses-specific.

---

#### code_documentation_mismatch

**Description:** SessionState class has auto_save_enabled and auto_save_interval fields but no documentation mentions auto-save feature

**Affected files:**
- `src/ui/web/session_state.py`
- `docs/help/common/debugging.md`

**Details:**
src/ui/web/session_state.py defines:
'auto_save_enabled: bool = True'
'auto_save_interval: int = 30'

These fields suggest an auto-save feature for the web UI, but:
- docs/help/common/debugging.md doesn't mention auto-save
- docs/help/common/editor-commands.md doesn't mention auto-save
- No help documentation describes this feature

Either the feature is implemented but undocumented, or these are placeholder fields for a planned feature.

---

#### code_documentation_mismatch

**Description:** Settings dialog implemented in code but not documented in help system

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/editor-commands.md`
- `docs/help/common/debugging.md`

**Details:**
src/ui/web/web_settings_dialog.py implements a full settings dialog with:
- Auto-numbering enable/disable
- Auto-number step configuration
- Resource limits viewing
- Save/Cancel functionality

But the help documentation doesn't mention:
- How to open the settings dialog
- What settings are available
- Keyboard shortcuts for settings (if any)
- That settings are per-session in Redis mode

docs/help/common/editor-commands.md has no 'Settings' or 'Preferences' entry
docs/help/common/debugging.md doesn't mention settings

Users have no way to discover this feature from the help system.

---

#### documentation_inconsistency

**Description:** Loop examples document references FIX function but doesn't demonstrate its use, while FIX documentation doesn't show practical loop-related examples

**Affected files:**
- `docs/help/common/examples/loops.md`
- `docs/help/common/language/functions/fix.md`

**Details:**
loops.md mentions 'FIX' in the 'See Also' section of INT function reference, but the loops examples never actually use FIX. The FIX.md documentation shows basic truncation examples but doesn't demonstrate its use in loop contexts where it might be relevant (e.g., array indexing with floating point calculations).

---

#### documentation_inconsistency

**Description:** Inconsistent precision specifications for SINGLE and DOUBLE types across documents

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/cdbl.md`
- `docs/help/common/language/functions/csng.md`

**Details:**
data-types.md states:
- SINGLE: "approximately 7 digits"
- DOUBLE: "approximately 16 digits"

cdbl.md states: "Double-precision numbers have approximately 16 digits of precision"

csng.md states: "Single-precision numbers have approximately 7 digits of precision"

However, data-types.md also shows identical ranges for both:
- SINGLE: "±2.938736×10^-39 to ±1.701412×10^38"
- DOUBLE: "±2.938736×10^-39 to ±1.701412×10^38"

This is inconsistent - DOUBLE should have a different (larger) range than SINGLE, not just more precision within the same range.

---

#### documentation_inconsistency

**Description:** Character set document references ASCII codes appendix but doesn't consistently link to it for all ASCII-related content

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
character-set.md has a 'See Also' section that includes: "[ASCII Codes](appendices/ascii-codes.md) - Complete ASCII table"

However, the Control Characters section in character-set.md duplicates information from ascii-codes.md without cross-referencing it. The character-set.md shows a subset of control characters (7, 8, 9, 10, 13, 27) while ascii-codes.md has the complete table (0-31). Users might not realize the complete reference exists.

---

#### documentation_inconsistency

**Description:** CVI/CVS/CVD functions reference FIELD and GET statements but error codes for field overflow don't mention these conversion functions

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`
- `docs/help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
cvi-cvs-cvd.md shows example:
"70 FIELD #1, 4 AS N$, 12 AS B$\n80 GET #1\n90 Y = CVS(N$)"

error-codes.md error 50 states: "Field overflow | A FIELD statement is attempting to allocate more bytes than were specified for the record length of a random file."

The error description doesn't mention that this can also occur when using CVI/CVS/CVD with incorrectly sized strings (e.g., calling CVS on a 2-byte string instead of 4-byte). The connection between these functions and potential field-related errors is not documented.

---

#### documentation_inconsistency

**Description:** Double-precision exponent notation inconsistency between documents

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
data-types.md states: "Use D for double-precision exponent notation or E for single-precision (e.g., 1.5D+10 for double, 1.5E+10 for single)"

math-functions.md shows: "BIGNUM# = 1.23456789012345D+100"

However, data-types.md also shows in the DOUBLE section example: "PI# = 3.141592653589793" without using D notation, and in the Constants section of math-functions.md: "PI# = 3.141592653589793" also without D notation.

This creates confusion about when D notation is required vs. optional for double-precision literals.

---

#### documentation_inconsistency

**Description:** LOC and LOF have identical See Also sections despite being different file I/O functions with different purposes

**Affected files:**
- `docs/help/common/language/functions/loc.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
Both LOC and LOF list identical See Also references: CLOSE, EOF, FIELD, FILES, GET, INPUT$, LOC, LOF, LPOS, LSET, OPEN, POS, PRINTi AND PRINTi USING, PUT, RESET, RSET, WRITE #, LINE INPUT#. While both are file-related, their specific use cases differ (LOC for position, LOF for size).

---

#### documentation_inconsistency

**Description:** TAB function example references non-existent statement syntax

**Affected files:**
- `docs/help/common/language/functions/tab.md`
- `docs/help/common/language/statements/val.md`

**Details:**
In tab.md example:
```basic
10 PRINT "NAME" TAB(25) "AMOUNT": PRINT
20 READ A$, B$
30 PRINT A$ TAB(25) B$
40 DATA "G. T. JONES", "$25.00"
```

The example uses READ and DATA statements but tab.md's 'See Also' section doesn't reference the READ or DATA statements, while val.md example uses similar pattern and does reference them in keywords.

---

#### documentation_inconsistency

**Description:** CLEAR documentation contains contradictory information about parameter meanings across BASIC-80 versions

**Affected files:**
- `docs/help/common/language/statements/clear.md`

**Details:**
The CLEAR documentation states:

'**In MBASIC 5.21 (BASIC-80 release 5.0 and later):**
- **expression1**: If specified, sets the highest memory location available for BASIC to use
- **expression2**: Sets the stack space reserved for BASIC (default: 256 bytes or 1/8 of available memory, whichever is smaller)'

Then later states:

'**Historical note:** In earlier versions of BASIC-80 (before release 5.0), the parameters had different meanings:
- expression1 set the amount of string space
- expression2 set the end of memory'

This creates confusion about which version's behavior is actually implemented, especially since the title says 'MBASIC 5.21' but then discusses version differences.

---

#### documentation_inconsistency

**Description:** DEF FN documentation describes implementation extension not present in original MBASIC 5.21

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
The def-fn.md states:

'**Original MBASIC 5.21**: Function names were limited to a single character after FN:
- ✓ `FNA` - single character
- ✓ `FNB$` - single character with type suffix

**This implementation (extension)**: Function names can be multiple characters:
- ✓ `FNA` - single character (compatible with original)
- ✓ `FNABC` - multiple characters'

This documents an extension to the original MBASIC 5.21 behavior, but it's unclear if this extension is actually implemented in the codebase. The documentation should clarify whether this is describing the actual implementation or a planned feature.

---

#### documentation_inconsistency

**Description:** END statement documentation contradicts itself about CONT behavior

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/stop.md`

**Details:**
END.md states: 'Can be continued with CONT (execution resumes at next statement after END)' but also says 'Unlike the STOP statement, END closes all open files'. The STOP.md documentation is referenced but not included. The behavior described suggests END should NOT be continuable since it closes files and returns to command level, which would make continuation problematic.

---

#### documentation_inconsistency

**Description:** EDIT statement documentation describes features not implemented

**Affected files:**
- `docs/help/common/language/statements/edit.md`

**Details:**
The documentation lists traditional MBASIC edit mode commands:
'- **I** - Insert mode
- **D** - Delete characters
- **C** - Change characters
- **L** - List the line
- **Q** - Quit edit mode
- **Space** - Move cursor forward
- **Enter** - Accept changes'

But then states:
'### Implementation Note:
This implementation provides full-screen editing capabilities through the integrated editor (when using the Tk, Curses, or Web UI). The traditional single-character edit mode commands are not implemented.'

This is confusing - it documents features that don't exist in this implementation.

---

#### documentation_inconsistency

**Description:** ERASE statement implementation note contradicts purpose

**Affected files:**
- `docs/help/common/language/statements/erase.md`

**Details:**
The documentation includes:
'**Implementation Note:** This Python implementation of MBASIC fully supports the ERASE statement.'

This note is unnecessary and confusing - it implies there might be implementations that don't support ERASE, but provides no context. If this is standard MBASIC functionality (which it is, as shown by 'Versions: 8K, Extended, Disk' in other docs), why does it need a special implementation note?

---

#### documentation_inconsistency

**Description:** Contradictory information about file closing behavior between LOAD and MERGE

**Affected files:**
- `docs/help/common/language/statements/load.md`
- `docs/help/common/language/statements/merge.md`

**Details:**
LOAD documentation states:
'LOAD closes all open files and deletes all variables and program lines currently residing in memory before it loads the designated program. However, if the ,R option is used with LOAD, the program is RUN after it is LOADed, and all open data files are kept open.'

MERGE documentation states:
'**Open files**: Unlike LOAD, MERGE does NOT close open files. Files that are open before MERGE remain open after MERGE completes.'

The MERGE doc implies LOAD always closes files, but LOAD doc says LOAD with ,R keeps files open. This creates confusion about the default LOAD behavior.

---

#### documentation_inconsistency

**Description:** RENUM example shows duplicate line numbers after renumbering

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
In Example 6 of renum.md:
'10 INPUT CHOICE
20 ON CHOICE GOTO 1000,1100,1200
1000 PRINT "OPTION 1"
1100 END
1100 PRINT "OPTION 2"
1200 END
1200 PRINT "OPTION 3"
1300 END'

This shows line 1100 appearing twice and line 1200 appearing twice, which is impossible in BASIC. This appears to be a copy-paste error in the documentation. The second occurrence of 1100 should probably be 1110, and the second 1200 should be 1210.

---

#### documentation_inconsistency

**Description:** Variable name significance documentation contradicts itself regarding case sensitivity handling

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
In variables.md: 'Variable names are not case-sensitive by default (Count = COUNT = count), but the behavior when using different cases can be configured via the `variables.case_conflict` setting'

In settings.md under variables.case_conflict: Lists options like 'first_wins', 'error', 'prefer_upper', etc.

The contradiction: variables.md says names are 'not case-sensitive' but then describes a setting that controls how case conflicts are handled. If they're truly case-insensitive, there would be no conflicts to handle. The documentation should clarify that variable names ARE case-insensitive for lookup, but the DISPLAY/STORAGE of the name can vary based on the setting.

---

#### documentation_inconsistency

**Description:** WIDTH documentation describes unsupported LPRINT syntax but doesn't clearly mark it in syntax section

**Affected files:**
- `docs/help/common/language/statements/width.md`

**Details:**
The Implementation Note says: 'The "WIDTH LPRINT" syntax is NOT SUPPORTED and will cause a parse error.'

But the Syntax section shows:
```basic
WIDTH <integer expression>
```

Then under 'Original MBASIC 5.21 also supported:' it shows the LPRINT variant.

The main Syntax section should have a note or the unsupported syntax should be more clearly separated to avoid confusion.

---

#### documentation_inconsistency

**Description:** WRITE and WRITE# documentation have inconsistent cross-references

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md (screen output) has in See Also:
- [WRITE#](writei.md) - Write data to a sequential file (file output variant)

writei.md (file output) has in See Also:
- [WRITE](write.md) - Write data to terminal (terminal output variant)

However, the titles are inconsistent:
write.md title: 'WRITE (Screen)'
writei.md title: 'WRITE# (File)'

The cross-reference descriptions use 'terminal' vs 'screen' inconsistently. Should standardize on one term.

---

#### documentation_inconsistency

**Description:** Inconsistent description of file closing behavior

**Affected files:**
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/stop.md`

**Details:**
run.md states: 'When RUN is executed:
- All variables are reset to zero or empty strings
- All open files are closed'

stop.md states: 'Unlike the END statement, the STOP statement does not close files.'

This is consistent, but the documentation should cross-reference each other more clearly. Users might expect STOP to behave like RUN regarding file closure.

---

#### documentation_inconsistency

**Description:** Keyboard shortcuts documentation is inconsistent across UI documentation

**Affected files:**
- `docs/help/common/shortcuts.md`
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
shortcuts.md shows:
- **^R** - Run program
- **^P** - Show help
- **^Q** - Quit IDE

curses/editing.md mentions:
- **Ctrl+R** - Run program
- **Ctrl+N** - New program (clear)
- **Ctrl+S** - Save program
- **Ctrl+L** - Load program
- **Ctrl+P** - Help

tk/index.md shows:
- **Ctrl+N** - New program
- **Ctrl+O** - Open file
- **Ctrl+S** - Save file
- **Ctrl+R** - Run program
- **Ctrl+F** - Find
- **F1** - Help

The shortcuts.md uses caret notation (^R) while UI-specific docs use Ctrl+ notation. More importantly, different UIs have different shortcuts (^P vs F1 for help, ^Q vs Ctrl+N for new). The main shortcuts.md should clarify it's for a specific UI or provide a comparison table.

---

#### documentation_inconsistency

**Description:** Settings storage paths may be incorrect or incomplete

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
settings.md states:
'**Linux/Mac**: `~/.mbasic/settings.json`
**Windows**: `%APPDATA%\mbasic\settings.json`
**Project**: `.mbasic/settings.json` in project directory'

However, there's no documentation about:
1. What happens if these directories don't exist
2. Whether the system creates them automatically
3. What the actual Windows path expands to (e.g., C:\Users\username\AppData\Roaming\mbasic\settings.json)
4. Whether there are any permission requirements

This should be clarified or expanded.

---

#### documentation_inconsistency

**Description:** WAIT documentation has malformed syntax in original text

**Affected files:**
- `docs/help/common/language/statements/wait.md`

**Details:**
The syntax section shows:
'WAIT <port number>, • I[,J]'

The bullet point '•' before 'I' appears to be a formatting error from the original documentation. Should be:
'WAIT <port number>, I[,J]'

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about WIDTH statement support

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states: 'Width statement:
```basic
10 WIDTH 80              ' Accepted (no-op)
```
Note: WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.'

compatibility.md does not mention WIDTH at all in the 'Intentional Differences' section, but features.md mentions 'LPRINT - Line printer output (Note: LPRINT statement is supported, but WIDTH LPRINT syntax is not)'

This information should be consistently documented across all relevant files.

---

#### documentation_inconsistency

**Description:** Inconsistent naming of the project/implementation

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/features.md`

**Details:**
extensions.md states: 'This is **MBASIC-2025**, a modern implementation of Microsoft BASIC-80 5.21 (CP/M era)' and lists multiple project names under consideration:
- MBASIC-2025 (emphasizes the modern update)
- Visual MBASIC 5.21 (emphasizes the multiple UIs)
- MBASIC++ (emphasizes extensions)
- MBASIC-X (extended MBASIC)

However, other documentation files (index.md, getting-started.md, features.md, compatibility.md) consistently refer to it as 'MBASIC 5.21' or 'this MBASIC interpreter' without mentioning the naming uncertainty.

This creates confusion about the official project name.

---

#### documentation_inconsistency

**Description:** Inconsistent count of semantic analyzer optimizations

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/features.md`

**Details:**
architecture.md states: 'The semantic analyzer implements **18 distinct optimizations**' and lists them as 'Core Optimizations (1-8)' and 'Advanced Optimizations (9-18)'.

features.md also states: 'The interpreter includes an advanced semantic analyzer with 18 optimizations' and lists all 18.

However, the numbering and organization differs slightly between the two documents, which could cause confusion when cross-referencing.

---

#### documentation_inconsistency

**Description:** Missing Web UI from getting-started.md interface options

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/index.md`

**Details:**
getting-started.md lists three interfaces:
- Curses UI (Default)
- CLI Mode
- Tkinter GUI

But index.md lists four interfaces:
- Tk (Desktop GUI)
- Curses (Terminal)
- Web Browser
- CLI (Command Line)

The Web UI is completely missing from the getting-started guide, which is inconsistent with the main index.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of debugging command availability

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/features.md`

**Details:**
extensions.md states for BREAK: 'Availability: CLI (command form), Curses (Ctrl+B), Tk (UI controls)'

features.md under 'Debugging' section lists:
- TRON/TROFF - Line tracing
- Breakpoints - Set/clear breakpoints (UI-dependent)
- Step execution - Execute one line at a time (UI-dependent)
- Variable watch - Monitor variables (UI-dependent)
- Stack viewer - View call stack (UI-dependent)

But does not specify which UIs support which features, while extensions.md provides specific UI availability for each command. This information should be consistent.

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

**Description:** Settings management not documented for Curses UI

**Affected files:**
- `docs/help/ui/cli/settings.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/settings.md provides detailed documentation for SHOWSETTINGS and SETSETTING commands, but feature-reference.md for Curses UI makes no mention of settings management capabilities. It's unclear if these commands work in Curses UI or if there's a different interface.

---

#### documentation_inconsistency

**Description:** Variable inspection methods differ between UIs without clear explanation

**Affected files:**
- `docs/help/ui/cli/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/variables.md states 'The CLI does not have a Variables Window feature' and recommends using PRINT for inspection. feature-reference.md documents 'Variables Window (Ctrl+W)' for Curses UI. The relationship between PRINT-based inspection and the Variables Window is not explained - can you use PRINT in Curses UI? Does Variables Window work in CLI?

---

#### documentation_inconsistency

**Description:** Find/Replace availability inconsistently documented

**Affected files:**
- `docs/help/ui/cli/find-replace.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/find-replace.md states 'The CLI backend does not have built-in Find/Replace commands' and recommends Tk UI. feature-reference.md states 'Find/Replace (Not yet implemented)' for Curses UI. However, cli/find-replace.md also says 'See [Find/Replace](find-replace.md) (available via menu)' which contradicts the 'not yet implemented' status.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for clipboard operations

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
feature-reference.md states 'Cut/Copy/Paste (Not implemented)' and explains 'Ctrl+X is used for Stop/Interrupt, Ctrl+C exits the program, and Ctrl+V is used for Save'. However, earlier in the same document under 'Save File (Ctrl+V)', it notes 'Uses Ctrl+V because Ctrl+S is reserved for terminal flow control'. The explanation for why Ctrl+V is used for Save (avoiding Ctrl+S) doesn't explain why it conflicts with paste functionality.

---

#### documentation_inconsistency

**Description:** STEP command syntax differs between CLI and Curses documentation

**Affected files:**
- `docs/help/ui/cli/debugging.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/debugging.md documents 'STEP [n]', 'STEP INTO', 'STEP OVER' as CLI commands. feature-reference.md documents 'Step Statement (Ctrl+T)' and 'Step Line (Ctrl+K)' for Curses UI. It's unclear if the STEP command with parameters works in Curses UI, or if only the keyboard shortcuts are available.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for help command

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md uses: '**^F** | Help (with search)'

index.md uses: '**^F** (Ctrl+F) anytime to open help'

The notation is inconsistent - one uses just ^F, the other explains it as Ctrl+F. Should be standardized across all docs.

---

#### documentation_inconsistency

**Description:** Missing Ctrl+U menu command in getting-started.md

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
quick-reference.md lists: '**^U** | Show menu' under Global Commands

But getting-started.md only mentions: '- **^F** (Ctrl+F) - Help (you're here now!)
- **^R** (Ctrl+R) - Run program
- **^Q** (Ctrl+Q) - Quit'

The menu command (^U) is not mentioned in the getting started guide, which could confuse new users.

---

#### documentation_inconsistency

**Description:** Inconsistent information about List Program command

**Affected files:**
- `docs/help/ui/curses/running.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
running.md states: 'Access through the menu bar to list the program to the output window.'

quick-reference.md states: '**Menu only** | List program' under Program Management

Both indicate it's menu-only, but running.md doesn't specify which menu or how to access it. Should provide consistent navigation instructions.

---

#### documentation_inconsistency

**Description:** Contradictory information about Find/Replace shortcuts

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
features.md states: '**Find text (Ctrl+F):**
- Opens Find dialog with search options
...
**Replace text (Ctrl+H):**
- Opens combined Find/Replace dialog
...
**Note:** Ctrl+F opens the Find dialog. Ctrl+H opens the Find/Replace dialog which includes both Find and Replace functionality.'

feature-reference.md states: '### Find/Replace (Ctrl+F / Ctrl+H)
Powerful search and replace functionality:
- Find: Ctrl+F
- Replace: Ctrl+H'

The note in features.md suggests Ctrl+H opens a combined dialog, but feature-reference.md lists them as separate functions. This is confusing.

---

#### documentation_inconsistency

**Description:** Missing Tk settings documentation

**Affected files:**
- `docs/help/ui/curses/settings.md`
- `docs/help/ui/tk/settings.md`

**Details:**
curses/settings.md provides detailed documentation about the settings widget with keyboard shortcuts, navigation, and all setting categories.

tk/settings.md is referenced in tk/index.md ('Settings & Configuration') but the file doesn't exist in the provided documentation.

Tk UI should have equivalent settings documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent information about default UI

**Affected files:**
- `docs/help/ui/index.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
index.md states under Curses UI: 'mbasic                # Default UI
mbasic --ui curses'

But tk/getting-started.md states: 'Or to use the default curses UI:
mbasic [filename.bas]'

Both claim curses is the default, but the inconsistency is in how it's presented. Should be standardized.

---

#### documentation_inconsistency

**Description:** Inconsistent feature count

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md title states: 'This document covers all 37 features available in the Tkinter (Tk) UI.'

But counting the features listed:
- File Operations: 8
- Execution & Control: 6
- Debugging: 6
- Variable Inspection: 6
- Editor Features: 7
- Help System: 4
Total: 37 features

However, features.md only highlights a subset (Smart Insert, Syntax Checking, Breakpoints, Variables Window, Execution Stack, Find/Replace, Context Help) = 7 features.

The relationship between 'Essential Features' and 'Complete Feature Reference' should be clarified.

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

And under 'Automatic Saving (Planned):'
'- Saves programs to browser localStorage for persistence'

This creates confusion about whether localStorage is used at all currently, and what exactly is stored there.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation status for breakpoint features

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/features.md`

**Details:**
debugging.md states:
'### Currently Implemented
1. Use **Run → Toggle Breakpoint** menu option
2. Enter the line number when prompted
3. A visual indicator appears in the editor
4. Use **Run → Clear All Breakpoints** to remove all'

But features.md under 'Breakpoints' states:
'**Currently Implemented:**
- Line breakpoints (toggle via Run menu)
- Clear all breakpoints
- Visual indicators in editor'

Then debugging.md later says:
'**Note:** Advanced features like clicking line numbers to set breakpoints, conditional breakpoints, and a dedicated breakpoint panel are planned for future releases but not yet implemented.'

While features.md says:
'**Note:** Advanced features like clicking line numbers to set breakpoints, conditional breakpoints, and a dedicated breakpoint panel are planned for future releases but not yet implemented.'

The inconsistency is subtle but debugging.md mentions 'Enter the line number when prompted' suggesting a dialog, while features.md doesn't mention this detail.

---

#### documentation_inconsistency

**Description:** Self-contradictory information about file storage in features.md

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
features.md under 'Local Storage' has contradictory statements:

'**Currently Implemented:**
- Programs stored in Python server memory (session-only, lost on page refresh)'

But then under 'Session Recovery (Planned):'
'- Restores last program from browser storage'

And under 'Data Protection (Currently Implemented):'
'**Currently Implemented:**
- Local storage only (browser localStorage)'

This is contradictory - are programs stored in Python server memory OR in browser localStorage? The document says both.

---

#### documentation_inconsistency

**Description:** Contradictory information about file persistence

**Affected files:**
- `docs/help/ui/web/index.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
index.md states:
'**In-memory filesystem** - File I/O within browser session
**Session isolation** - Private, sandboxed environment
**File I/O** - Files stored in memory, persist during session only'

But getting-started.md under 'Recent Files' states:
'File → Recent Files shows recently opened files (saved in localStorage, persists across browser sessions).'

This is contradictory - if files are in-memory and session-only, how do recent files persist across browser sessions in localStorage?

---

#### documentation_inconsistency

**Description:** Inconsistent instructions for opening files in Web UI

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
settings.md says 'Click File → Open, select the downloaded file' but web-interface.md says 'Open a .bas file from your computer (via browser file picker)' under File Menu → Open. The settings.md implies a two-step process while web-interface.md describes it as a single action. Both should use consistent language about the browser file picker.

---

#### documentation_inconsistency

**Description:** Conflicting cross-references for calendar programs

**Affected files:**
- `docs/library/games/index.md`
- `docs/library/utilities/index.md`

**Details:**
games/index.md has a calendar.bas entry that says 'A simpler calendar utility is also available in the Utilities Library' but utilities/index.md has a calendar.bas entry that says 'A different calendar program is also available in the Games Library'. The descriptions contradict each other - one says 'simpler', the other says 'different'. They should be consistent about which is simpler/more complex.

---

#### documentation_inconsistency

**Description:** Inconsistent description of auto-numbering behavior in Command area

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
web-interface.md clearly states under 'Command (Bottom)' section: 'No automatic line numbering - commands run immediately' and 'Only in Editor: The Command area does NOT auto-number (it runs commands immediately)'. However, settings.md doesn't explicitly mention that auto-numbering settings don't affect the Command area, which could confuse users.

---

#### documentation_inconsistency

**Description:** QUICK_REFERENCE.md is described as Curses UI specific but doesn't clearly state this in its title or opening

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`
- `docs/user/README.md`

**Details:**
QUICK_REFERENCE.md title is 'MBASIC Curses IDE - Quick Reference Card' which is clear, but README.md lists it under 'Reference Documentation' without the UI-specific qualifier in the description. The description says 'Quick command reference (Curses UI specific)' but this could be clearer in the actual document's introduction.

---

#### documentation_inconsistency

**Description:** Missing cross-reference to detailed settings documentation

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
CASE_HANDLING_GUIDE.md has a 'See Also' section that references 'SETTINGS_AND_CONFIGURATION.md - Complete settings reference', but the guide itself is very detailed about case handling settings. It's unclear if SETTINGS_AND_CONFIGURATION.md contains additional information or if this is the complete reference.

---

#### documentation_inconsistency

**Description:** Curses UI limitations differ between documents

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
CHOOSING_YOUR_UI.md lists Curses limitations as:
- Limited mouse support
- Partial variable editing
- No clipboard integration
- Terminal color limits
- No Find/Replace

QUICK_REFERENCE.md doesn't mention 'Partial variable editing' or 'No clipboard integration' in its limitations section, only mentioning:
- Breakpoint not stopping
- Can't type in editor
- Output not visible
- Pressed 's', now every line stops

These appear to be different types of limitations (feature limitations vs usage issues), but the inconsistency could confuse users.

---

#### documentation_inconsistency

**Description:** Assembly source file location may be incorrect

**Affected files:**
- `docs/user/FILE_FORMAT_COMPATIBILITY.md`

**Details:**
FILE_FORMAT_COMPATIBILITY.md states: 'Assembly source files (.mac) in the docs/history/original_mbasic_src/ directory retain their original CRLF line endings'

This references a specific directory path that may not exist or may have moved. The document should verify this path is correct or use a more general reference.

---

#### documentation_inconsistency

**Description:** Missing documentation files referenced

**Affected files:**
- `docs/user/README.md`

**Details:**
README.md references several files that are not included in the provided documentation:
- keyboard-shortcuts.md (listed under 'Reference Documentation')
- sequential-files.md (listed under 'File Operations')
- UI_FEATURE_COMPARISON.md (listed under 'Reference Documentation')
- TK_UI_QUICK_START.md (listed under 'UI-Specific Guides')
- SETTINGS_AND_CONFIGURATION.md (listed under 'Configuration')

These files are referenced but not provided, making it impossible to verify consistency.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Variables window

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states 'The Variables & Resources window (Ctrl+W in TK UI)' but TK_UI_QUICK_START.md documents it as '**Ctrl+W** | Show/hide Variables window' without mentioning 'Resources'. The window name is inconsistent between docs.

---

#### documentation_inconsistency

**Description:** Conflicting keyboard shortcuts for Step functionality

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md states 'Step, Continue, and Stop are available via toolbar buttons or the Run menu (no keyboard shortcuts)' but keyboard-shortcuts.md for Curses UI documents 'Ctrl+K' as 'Step Line' and 'Ctrl+T' as 'Step Statement'. This creates confusion about whether step shortcuts exist.

---

#### documentation_inconsistency

**Description:** Conflicting information about Find/Replace keyboard shortcut

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
UI_FEATURE_COMPARISON.md states 'Find/Replace (Ctrl+F/H)' suggesting Ctrl+F for Find and Ctrl+H for Replace. However, TK_UI_QUICK_START.md only documents '**Ctrl+H** | Find and replace (Tk UI only)' with no mention of Ctrl+F.

---

#### documentation_inconsistency

**Description:** Missing Curses keyboard shortcut documentation

**Affected files:**
- `docs/user/keyboard-shortcuts.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
keyboard-shortcuts.md shows empty key binding (backticks with nothing between) for 'Show/hide execution stack window' in both Global Commands and Debugger sections. UI_FEATURE_COMPARISON.md claims Curses has this feature but the actual key is not documented.

---

#### documentation_inconsistency

**Description:** Inconsistent Save command documentation across UIs

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md shows 'Save (interactive)' as '❌' for CLI with note 'CLI: No interactive save prompt (must use SAVE "filename" command instead)' but 'Save (command)' shows '✅' for all UIs including CLI. The distinction between these two features and why CLI lacks interactive save is not clearly explained in context.

---

#### documentation_inconsistency

**Description:** Ambiguous keyboard shortcut notation

**Affected files:**
- `docs/user/keyboard-shortcuts.md`

**Details:**
keyboard-shortcuts.md uses backticks with empty content (`` ``) to represent a keyboard shortcut in two places: 'Show/hide execution stack window' in Global Commands and Debugger sections. This appears to be a documentation error where the actual key was not filled in.

---

### 🟢 Low Severity

#### Code vs Comment conflict

**Description:** InputStatementNode docstring has confusing/contradictory explanation of suppress_question field

**Affected files:**
- `src/ast_nodes.py`

**Details:**
The docstring states:
"Note: The suppress_question field indicates whether to suppress the question mark prompt:
- suppress_question=False (default): INPUT var or INPUT "prompt", var → shows "? " or "prompt? "
- suppress_question=True: INPUT; var → suppresses "?" completely (no prompt at all)

Semicolon usage:
- After prompt string: INPUT "prompt"; var → semicolon is just a separator (shows "prompt? ")
- Immediately after INPUT: INPUT; var → semicolon signals suppress_question=True"

This is confusing because it says INPUT "prompt"; var shows "prompt? " (with question mark) but also says suppress_question=True "suppresses '?' completely". The distinction between semicolon-as-separator vs semicolon-as-suppressor needs clarification.

---

#### Code vs Comment conflict

**Description:** CallStatementNode has 'arguments' field that parser never populates

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode docstring states:
"Note: The 'arguments' field is reserved for potential future compatibility with other BASIC dialects (e.g., CALL ROUTINE(args)). The parser does not currently populate this field (always empty list). Standard MBASIC 5.21 only accepts a single address expression in the 'target' field."

This creates a dead field in the AST that serves no purpose in the current implementation. It's unclear why this field exists if it's never used - it could confuse code that traverses the AST expecting arguments to be meaningful.

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for 'line number' vs 'line_number' in docstrings

**Affected files:**
- `src/ast_nodes.py`

**Details:**
Throughout ast_nodes.py, some docstrings use 'line number' (two words) and others use 'line_number' (underscore). For example:
- GotoStatementNode: "GOTO line_number" (underscore)
- IfStatementNode: "IF condition THEN line_number" (underscore)
- ResumeStatementNode: "RESUME line_number" (underscore)
- RenumStatementNode: "new starting line number" (two words)
- ListStatementNode: "Start line number" (two words)

This inconsistency makes the documentation harder to search and understand.

---

#### Code vs Comment conflict

**Description:** RemarkStatementNode comment_type field has unclear purpose

**Affected files:**
- `src/ast_nodes.py`

**Details:**
RemarkStatementNode has comment_type field with docstring: "comment_type: str = 'REM'  # 'REM', 'REMARK', or 'APOSTROPHE' - preserves original syntax"

But the field default is 'REM', suggesting it might not always preserve the original syntax. It's unclear whether this field is always set correctly by the parser or if the default 'REM' is used as a fallback. The relationship between this field and source code regeneration needs clarification.

---

#### Documentation inconsistency

**Description:** Missing documentation for position_serializer module referenced in LineNode

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring references: "Text regeneration is handled by the position_serializer module which reconstructs source text from statement nodes and their token information."

However, no position_serializer module is shown in the provided source files. This creates a documentation gap where the mechanism for text regeneration is referenced but not explained or visible.

---

#### Documentation inconsistency

**Description:** ChainStatementNode has delete_range as tuple but no type annotation details

**Affected files:**
- `src/ast_nodes.py`

**Details:**
ChainStatementNode has field: "delete_range: tuple = None  # (start, end) for DELETE option, or None"

The comment says it's a tuple of (start, end) but doesn't specify what type start and end are (int? ExpressionNode?). Other similar fields in the AST use proper type annotations like Optional[int] or List['ExpressionNode']. This inconsistency makes the API unclear.

---

#### Code vs Comment conflict

**Description:** TypeInfo class docstring describes it as both a utilities class and a facade

**Affected files:**
- `src/ast_nodes.py`

**Details:**
TypeInfo docstring states:
"Type information utilities for variables

Provides convenience methods for working with VarType enum and converting between type suffixes, DEF statement tokens, and VarType enum values.

This class provides a facade over VarType with two purposes:
1. Static helper methods for type conversions
2. Class attributes (INTEGER, SINGLE, etc.) that expose VarType enum values for backward compatibility with code that uses TypeInfo.INTEGER instead of VarType.INTEGER"

The term 'facade' is typically used for design patterns that provide a simplified interface to a complex subsystem. Here, TypeInfo is just exposing VarType enum values as class attributes. This is more accurately described as 'aliasing' or 'compatibility layer' rather than a facade pattern. The terminology is confusing.

---

#### code_vs_comment

**Description:** EOF() docstring mentions mode 'I' for binary input, but implementation checks file_info['mode'] == 'I' without explaining where this mode is set

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring states:
Note: For binary input files (mode 'I' from OPEN statement), respects ^Z (ASCII 26)
as EOF marker (CP/M style). Mode 'I' is set by the OPEN statement for binary input,
which opens the file in binary mode ('rb').

However, the OPEN statement implementation is not shown in these files, so we cannot verify if mode 'I' is actually set correctly. The comment assumes OPEN sets this mode but provides no evidence.

---

#### code_vs_comment

**Description:** INPUT() method docstring describes file_info structure but doesn't match the actual extraction pattern used

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment at line 826 states:
# self.runtime.files[file_num] returns a dict with 'handle', 'mode', 'eof' keys
# Extract the file handle from the file_info dict to perform read operations
# (this pattern is used by EOF(), LOC(), LOF(), and other file functions)

This is explanatory but redundant - the code immediately below does exactly this. The comment seems to be teaching rather than documenting a non-obvious behavior.

---

#### documentation_inconsistency

**Description:** Module docstring claims to document MBASIC 5.21 but version number is not verified elsewhere in the codebase

**Affected files:**
- `src/basic_builtins.py`

**Details:**
First line of basic_builtins.py:
Built-in functions for MBASIC 5.21.

This specific version number (5.21) is not cross-referenced or validated. If this is meant to indicate compatibility with a specific BASIC version, it should be documented in a central location.

---

#### code_vs_comment

**Description:** Comment about trailing_minus_only behavior is redundant with the spec definition

**Affected files:**
- `src/basic_builtins.py`

**Details:**
At line 119, the comment states:
# trailing_minus_only: - at end only (always adds 1 char: - or space)

This exactly duplicates information in the docstring at lines 107-109:
Sign behavior:
- trailing_minus_only: - at end, adds - for negative or space for non-negative (always 1 char)

The inline comment adds no new information beyond the docstring.

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for filesystem abstraction purposes

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py states:
"1. FileIO (this file) - Program management operations (LOAD/SAVE/FILES/KILL)
   - Used by: Interactive mode, UI file browsers"

src/filesystem/base.py states:
"1. FileIO (src/file_io.py) - Program management operations
   - Used by: Interactive mode, UI file browsers"

Both files describe the same abstraction but src/file_io.py says "LOAD/SAVE/FILES/KILL" while base.py says "FILES (list), LOAD/SAVE/MERGE (program files), KILL (delete)" - the second is more detailed and includes MERGE which the first omits.

---

#### Code vs Comment conflict

**Description:** InMemoryFileHandle.flush() comment describes different semantics than typical file flush

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The flush() method has this comment:
"""Flush write buffers.

Note: This calls StringIO/BytesIO flush() which are no-ops.
Content is only saved to the virtual filesystem on close().
This differs from file flush() semantics where flush() typically
persists buffered writes. For in-memory files, all writes are
already in memory, so flush() has no meaningful effect.
"""

The comment correctly describes the implementation, but the method docstring "Flush write buffers." suggests standard file semantics. This could mislead users expecting flush() to persist data. The detailed note clarifies this, but the brief docstring is potentially misleading.

---

#### Code vs Documentation inconsistency

**Description:** Error code documentation mentions ambiguous two-letter codes but doesn't explain resolution strategy

**Affected files:**
- `src/error_codes.py`

**Details:**
The module docstring states:
"Note: Some two-letter codes are duplicated (e.g., DD, CN, DF) across different
numeric error codes. This matches the original MBASIC 5.21 specification where
the two-letter codes alone are ambiguous - the numeric code is authoritative."

Looking at ERROR_CODES:
- DD appears at codes 10 ("Duplicate definition") and 68 ("Device unavailable")
- CN appears at codes 17 ("Can't continue") and 69 ("Communication buffer overflow")
- DF appears at codes 25 ("Device fault") and 61 ("Disk full")

The documentation correctly notes the ambiguity but doesn't explain how the system handles this in practice (e.g., does format_error() always use numeric codes to avoid ambiguity?).

---

#### Documentation inconsistency

**Description:** Security note about user_id validation is important but placement could be clearer

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The SandboxedFileSystemProvider docstring contains:
"Security:
- No access to real filesystem
- No path traversal (../ etc.)
- Resource limits enforced
- Per-user isolation via user_id keys in class-level storage
  IMPORTANT: Caller must ensure user_id is securely generated/validated
  to prevent cross-user access (e.g., use session IDs, not user-provided values)"

This critical security requirement is buried in the class docstring. It should also be in the __init__ docstring where user_id is documented as a parameter, since that's where developers will look when using the class.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for state checking in docstrings

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The class docstring lists state names as documentation-only:
"State names used in documentation (not actual enum values):
- 'idle' - No program loaded (halted=True)
- 'paused' - User hit Ctrl+Q/stop (halted=True)
..."

But then uses different terminology in can_execute_immediate() docstring:
"For tick-based interpreters, we must check the interpreter state."

And in execute() docstring:
"IMPORTANT: For tick-based interpreters, this should only be called when
can_execute_immediate() returns True. Calling during 'running' state
may corrupt the interpreter state."

The term 'running' state is used in quotes suggesting it's a specific state name, but the earlier documentation clarifies these are not actual enum values. This could confuse readers about whether these are literal state values or conceptual descriptions.

---

#### code_vs_comment

**Description:** Comment says PC is not saved/restored but doesn't explain implications for all statement types

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Line 207-209 states:
"# Note: We do not save/restore the PC before/after execution.
# This allows statements like RUN to change execution position.
# Normal statements (PRINT, LET, etc.) don't modify PC anyway."

This comment explains the design decision but doesn't address what happens with other control flow statements mentioned in the help text as 'not recommended' (GOTO, GOSUB). The help text says:
"• GOTO, GOSUB, and control flow statements are not recommended
  (they will execute but may produce unexpected results)"

The comment should clarify whether these statements are allowed to modify PC or if there are safeguards, since the help text suggests they work but with caveats.

---

#### documentation_inconsistency

**Description:** Module docstring mentions Python 3.9+ type hints but this is not a functional requirement

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
The module docstring states:
"Note: This module uses Python 3.9+ type hint syntax (tuple[str, bool] instead of Tuple[str, bool])."

This is documentation about implementation details rather than functional behavior. It's not an inconsistency per se, but it's unusual to document syntax choices in the module docstring. This information would be more appropriate in a developer guide or CONTRIBUTING.md file. The code does use tuple[str, bool] in sanitize_and_clear_parity() return type.

---

#### code_vs_comment

**Description:** Help text formatting inconsistency with box drawing characters

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The _show_help() method uses Unicode box-drawing characters for visual formatting:
"═══════════════════════════════════════════════════════════════════"
"───────────────────────────────────────────────────────────────────"

However, the input_sanitizer.py module explicitly filters out non-ASCII characters:
"# Reject everything else (control chars, extended ASCII)"
"if 32 <= code <= 126: return True"

If the help text output goes through sanitization (which it might in some UI contexts), these box-drawing characters (which are outside ASCII 32-126) would be stripped. The help text should either use ASCII-only characters (like ===== and -----) or the documentation should clarify that help output bypasses sanitization.

---

#### code_vs_comment

**Description:** Comment about digit handling in EDIT mode describes behavior but doesn't explain it's intentional

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 1047-1050: 'If digits are entered, they fall through all command handling logic without matching any if/elif branches, resulting in no action (no output, no cursor movement, no error message).'

This describes current behavior but doesn't clarify if this is:
1. A bug (digits should trigger an error)
2. Intentional (digits reserved for future count prefix feature)
3. Legacy behavior from MBASIC

The comment reads like a bug report rather than documentation.

---

#### documentation_inconsistency

**Description:** Module docstring lists features but doesn't mention AUTO and EDIT commands

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 2-9 module docstring lists:
'Implements the interactive REPL with:
- Line entry and editing
- Direct commands (RUN, LIST, SAVE, LOAD, NEW, etc.)
- Immediate mode execution'

But AUTO (line 1202) and EDIT (line 1046) are fully implemented commands not mentioned in the 'etc.' The docstring should explicitly list these important features.

---

#### code_vs_comment

**Description:** Comment about COMMON variable handling describes implementation details that may confuse readers

**Affected files:**
- `src/interactive.py`

**Details:**
Lines 621-632: Long comment about COMMON variable type suffix resolution that describes implementation details ('checks type suffixes (%, $, !, #, and no suffix) in order and save the FIRST matching variable').

This is implementation documentation that belongs in a design doc, not inline comments. The comment is accurate but overly detailed for code maintenance.

---

#### code_vs_comment_conflict

**Description:** Comment about runtime selection mentions 'works for stopped OR finished programs' but doesn't clarify if finished programs should keep their runtime

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in execute_immediate() says: 'If program_runtime exists (from RUN), use it so immediate mode can examine/modify program variables (works for stopped OR finished programs)'

This suggests that even after a program finishes (not just stops), the program_runtime persists and can be accessed. However, it's unclear from the code whether program_runtime is cleared after normal program completion or only after explicit actions like NEW/LOAD. This could lead to confusion about when program variables are accessible in immediate mode.

---

#### documentation_inconsistency

**Description:** FILES command docstring mentions drive A support but implementation comment says it's not supported

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring says: 'FILES "A:*.*" - List files on drive A (not supported, lists current dir)'

This is internally consistent (docstring acknowledges lack of support), but it's unusual to document an unsupported feature in the usage examples. This could confuse users who might try to use drive letters expecting some functionality.

---

#### code_vs_comment_conflict

**Description:** Comment says 'Pass empty line_text_map for immediate mode (line 0 is temporary)' but the actual parameter passed is an empty dict

**Affected files:**
- `src/interactive.py`

**Details:**
Comment: 'Pass empty line_text_map for immediate mode (line 0 is temporary)'
Code: 'self.runtime = Runtime(ast, {})'

The comment correctly describes the intent, but doesn't clarify that line 0 statements in immediate mode won't be available for error reporting with line text. This is probably fine for immediate mode, but the comment could be clearer about the implications.

---

#### code_vs_comment

**Description:** InterpreterState docstring describes execution order but doesn't match actual tick_pc implementation details

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 42-50 describes internal execution order:
"Internal execution order in tick_pc() (for developers understanding control flow):
1. pause_requested check - pauses if pause() was called
2. halted check - stops if already halted
3. break_requested check - handles Ctrl+C breaks
4. breakpoints check - pauses at breakpoints
5. statement execution - where input_prompt may be set
6. error handling - where error_info is set via exception handlers"

But in tick_pc() (lines 327-450), the actual order includes additional steps not mentioned:
- Line 344: Check if halted
- Line 351: Check break_requested
- Line 361: Check breakpoints
- Line 376: Trace output (not mentioned in docstring)
- Line 386: Get statement
- Line 390: Execute statement
- Line 428: Check for input_prompt
- Line 431: Advance PC logic
- Line 441: Check step mode

The trace output step (line 376-383) is not mentioned in the docstring's execution order list.

---

#### documentation_inconsistency

**Description:** Docstring mentions 'OLD EXECUTION METHODS REMOVED' but doesn't specify which version removed them

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 685-690 says:
"# OLD EXECUTION METHODS REMOVED
# Note: The project has an internal implementation version (tracked in src/version.py)
# which is separate from the MBASIC 5.21 language version being implemented.
# Old methods: run_from_current(), _run_loop(), step_once() (removed)
# These used old current_line/next_line fields
# Replaced by tick_pc() and PC-based execution"

This mentions src/version.py tracks the implementation version, but doesn't specify when these methods were removed or what version introduced tick_pc(). This makes it unclear for developers whether they should expect to find these methods in older commits or branches.

---

#### code_vs_comment

**Description:** execute_for docstring says string variables are 'effectively not supported' but doesn't explain parser behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 1044-1051 says:
"The loop variable typically has numeric type suffixes (%, !, #). The variable
type determines how values are stored. String variables ($) in FOR loops
would cause a type error when set_variable() attempts to store the numeric
loop value, so they are effectively not supported despite being parsed."

This says string variables are 'parsed' but 'effectively not supported'. However, it doesn't clarify:
1. Does the parser accept 'FOR A$ = 1 TO 10' as valid syntax?
2. At what point does the error occur - during FOR execution or during NEXT?
3. What is the exact error message?

The comment creates ambiguity about whether this is a parser limitation, runtime limitation, or intentional design choice.

---

#### code_vs_comment

**Description:** Comment about RESUME 0 vs RESUME None distinction is misleading

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1115 states:
"# RESUME or RESUME 0 - retry the statement that caused the error
# Note: Parser preserves the distinction (None vs 0) for accurate source
# text regeneration, but the interpreter treats both identically at runtime."

The code checks 'if stmt.line_number is None or stmt.line_number == 0:' which correctly treats both as identical. However, the comment implies this is only for 'source text regeneration' when actually MBASIC syntax allows both 'RESUME' and 'RESUME 0' as equivalent forms. The distinction is syntactic, not semantic.

---

#### code_vs_comment

**Description:** INPUT statement comment describes state machine but implementation details differ

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1330 describes INPUT state machine:
"State machine for keyboard input (file input is synchronous):
1. If state.input_buffer has data: Use buffered input (from provide_input())
2. Otherwise: Set state.input_prompt, input_variables, input_file_number and return (pauses execution)
3. UI calls provide_input() with user's input line
4. On next tick(), buffered input is used (step 1) and state vars are cleared"

The code sets:
'self.state.input_prompt = full_prompt
self.state.input_variables = stmt.variables
self.state.input_file_number = None'

But the comment at line ~1365 says 'None indicates keyboard input (not file)' which is correct. However, step 4 says 'state vars are cleared' but the actual clearing happens at line ~1400:
'self.state.input_variables = []
self.state.input_prompt = None'

This only clears input_variables and input_prompt, not input_file_number. Minor inconsistency in what 'state vars' means.

---

#### code_vs_comment

**Description:** OPTION BASE comment describes 'Duplicate Definition' error conditions but explanation could be clearer

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1310 states:
"# MBASIC 5.21 gives 'Duplicate Definition' if:
# 1. OPTION BASE has already been executed, OR
# 2. Any arrays have been created (both explicitly via DIM and implicitly via first use like A(5)=10)
#    This applies regardless of the current array base (0 or 1).
# Note: The check len(self.runtime._arrays) > 0 catches all array creation because both
# explicit DIM and implicit array access (via set_array_element) update runtime._arrays."

The code checks:
'if self.runtime.option_base_executed:
    raise RuntimeError("Duplicate Definition")
if len(self.runtime._arrays) > 0:
    raise RuntimeError("Duplicate Definition")'

The comment is accurate. However, it says 'This applies regardless of the current array base (0 or 1)' which is slightly confusing - it means the error occurs even if arrays were created with the same base value that OPTION BASE would set. This is correct MBASIC behavior but the phrasing could be clearer.

---

#### code_vs_comment_conflict

**Description:** Comment in evaluate_binaryop() says 'len() counts characters, not bytes' but then mentions field buffers use latin-1 where byte count matters - potential confusion

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment states: 'Note: len() counts characters, not bytes. For ASCII this is equivalent. Field buffers (LSET/RSET) explicitly use latin-1 encoding where byte count matters.'

This is technically correct but potentially misleading. For latin-1 encoding, character count equals byte count (latin-1 is a single-byte encoding). The comment seems to suggest there's a difference when there isn't one for latin-1. The distinction would only matter for multi-byte encodings like UTF-8.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of string length limits across different operations

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_binaryop() for string concatenation:
'# Enforce 255 character string limit for concatenation (MBASIC 5.21 compatibility)'
'# Note: This check only applies to concatenation via PLUS operator.'
'# Other string operations (MID$, LSET, RSET, INPUT) do not enforce this limit.'

However, in execute_lset() and execute_rset(), field variables are explicitly width-limited by the FIELD definition, and the code truncates strings to fit. The comment suggests LSET/RSET don't enforce limits, but they do enforce field width limits. The distinction between 'string length limit' (255 chars) and 'field width limit' (defined by FIELD) is not clearly documented.

---

#### code_vs_comment_conflict

**Description:** Comment in execute_list() claims line_text_map is kept in sync during RENUM and MERGE, but this is only an assertion without verification

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment states: 'The line_text_map is maintained by ProgramManager and is kept in sync with the AST during program modifications (add_line, delete_line, RENUM, MERGE). The sync is handled by ProgramManager methods and should remain consistent during normal operation.'

This is a claim about behavior in another module (ProgramManager) that cannot be verified from this code. If ProgramManager doesn't actually maintain this sync properly, the LIST command would show stale or incorrect line text. This is a documentation of assumed behavior rather than verified behavior.

---

#### Documentation inconsistency

**Description:** Module docstring mentions CursesIOHandler but the actual class name in curses_io.py is CursesIOHandler (correct), however the import statement and __all__ list correctly use CursesIOHandler. No actual inconsistency in code, but worth noting the naming is consistent.

**Affected files:**
- `src/iohandler/__init__.py`

**Details:**
The __init__.py correctly imports and exports 'CursesIOHandler' from curses_io module, matching the class name in curses_io.py. This is actually consistent.

---

#### Code vs Comment conflict

**Description:** The web_io.py has backward compatibility aliases (print() and get_char()) with comments explaining they are deprecated, but these methods are not mentioned in the base IOHandler interface or other implementations. This suggests these were web-specific methods that were later standardized.

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py contains:
'# Backward compatibility alias
# This method was renamed from print() to output() to avoid conflicts with Python's
# built-in print function. The print() alias is maintained for backward compatibility
# with older code that may still call io_handler.print().'

And:
'# Backward compatibility alias
# This method was renamed from get_char() to input_char() for consistency with
# the IOHandler base class interface.'

These aliases don't exist in other IOHandler implementations (console, curses, gui), suggesting web_io.py had different method names initially.

---

#### Code vs Documentation inconsistency

**Description:** ConsoleIOHandler.input_char() has a fallback for Windows without msvcrt that calls input(), but the comment says this 'defeats the purpose of single-char input' and has 'severe limitations'. However, the code doesn't raise an exception or warning, silently providing broken behavior.

**Affected files:**
- `src/iohandler/console.py`

**Details:**
console.py lines in input_char():
'# Fallback for Windows without msvcrt: use input() with severe limitations
# WARNING: This fallback calls input() which:
# - Waits for Enter key (defeats the purpose of single-char input)
# - Returns the entire line, not just one character
# This is a known limitation when msvcrt is unavailable.
# For proper single-character input on Windows, msvcrt is required.
line = input()
return line[:1] if line else ""'

The code silently returns broken behavior instead of raising NotImplementedError or warning the user.

---

#### Documentation inconsistency

**Description:** web_io.py documents get_screen_size() method which returns (24, 80), but this method is not part of the IOHandler base interface and is not implemented in other handlers (console, curses, gui).

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py has:
'def get_screen_size(self):
    """Get terminal size.
    Returns:
        Tuple of (rows, cols) - returns reasonable defaults for web
    """
    return (24, 80)'

This method is not in base.py IOHandler interface, and not in console.py, curses_io.py, or gui.py implementations.

---

#### Code vs Documentation inconsistency

**Description:** web_io.py input_char() docstring says 'Note: Character input not supported in web UI (always returns empty string)' but the method signature has blocking parameter that is ignored. This could confuse users who expect blocking=True to wait for input.

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py input_char():
'def input_char(self, blocking=True):
    """Get single character input (for INKEY$, INPUT$).
    Args:
        blocking: If True, wait for keypress. If False, return "" if no key ready.
    Returns:
        Single character string, or "" if not available
    Note: Character input not supported in web UI (always returns empty string).
    """
    return ""'

The blocking parameter is accepted but completely ignored, always returning empty string regardless of blocking value.

---

#### Documentation inconsistency

**Description:** The module docstring mentions SimpleKeywordCase (src/simple_keyword_case.py) as an alternative for simpler force-based policies, but this file is not included in the provided source code files, making it impossible to verify the relationship or whether SimpleKeywordCase actually exists.

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
keyword_case_manager.py docstring:
'Note: This class provides advanced case policies (first_wins, preserve, error) via
CaseKeeperTable and is used by parser.py and position_serializer.py. For simpler
force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py)
which only supports force_lower, force_upper, and force_capitalize.'

The referenced file src/simple_keyword_case.py is not in the provided source files.

---

#### Code vs Comment conflict

**Description:** ConsoleIOHandler.input_line() comment says 'For console, this delegates to self.input() (same behavior)' but then notes it doesn't preserve spaces as documented in base class. The comment could be clearer that this is an intentional limitation, not just delegation.

**Affected files:**
- `src/iohandler/console.py`

**Details:**
console.py input_line():
'def input_line(self, prompt: str = '') -> str:
    """Input a complete line from console.
    For console, this delegates to self.input() (same behavior).
    Note: Current implementation does NOT preserve leading/trailing spaces
    as documented in base class. Python's input() automatically strips them.
    This is a known limitation - see input_line() documentation in base.py.
    """
    return self.input(prompt)'

The phrase 'same behavior' is ambiguous - same as what? Same as input()? The note clarifies but could be integrated better.

---

#### code_vs_comment

**Description:** Comment about Token class location may be incorrect

**Affected files:**
- `src/lexer.py`

**Details:**
In read_identifier() method around line 280:
"# Preserve original case for display. Identifiers use the original_case field
# to store the exact case as typed. Keywords use original_case_keyword to store
# the case determined by the keyword case policy (see Token class in token_types.py)."

The comment references 'token_types.py' but the import at the top of the file is:
"from src.tokens import Token, TokenType, KEYWORDS"

This suggests the Token class is in 'tokens.py' not 'token_types.py'. This is a minor documentation inconsistency.

---

#### code_vs_comment

**Description:** Comment about type suffix placement contradicts actual implementation behavior

**Affected files:**
- `src/lexer.py`

**Details:**
In read_identifier() around line 235:
"# Type suffix - only allowed at end of identifier
ident += self.advance()
break"

The comment says type suffix is "only allowed at end" but the code doesn't validate this - it just breaks after finding one. If a user types 'A$B', the code would accept 'A$' as the identifier and leave 'B' for the next token. The comment implies validation that doesn't exist, though the break does enforce single-suffix behavior.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for comment handling

**Affected files:**
- `src/lexer.py`

**Details:**
The code uses both 'apostrophe comment' and 'REM comment' terminology:

Line ~320: "# Apostrophe comment (like REM)"
Line ~323: "self.tokens.append(Token(TokenType.APOSTROPHE, comment_text, start_line, start_column))"

But also:
Line ~350: "# Special handling for REM/REMARK - read comment text"

The apostrophe (') is treated as a separate token type (APOSTROPHE) while REM/REMARK are keywords. The documentation could be clearer about this distinction.

---

#### code_vs_comment

**Description:** Comment about semicolon handling in parse_line() is potentially misleading about MBASIC behavior

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines 353-358 states:
"Allow trailing semicolon at end of line only (treat as no-op).
Context matters: Semicolons WITHIN PRINT/LPRINT are item separators (parsed there),
but semicolons BETWEEN statements are NOT valid in MBASIC.
MBASIC uses COLON (:) to separate statements, not semicolon (;)."

This is correct, but the code then allows semicolons and treats them as no-ops, which may not match actual MBASIC 5.21 behavior. The comment describes the standard but the code is more permissive.

---

#### documentation_inconsistency

**Description:** Docstring claims parse_print_using parses format string as expression but doesn't mention semicolon requirement

**Affected files:**
- `src/parser.py`

**Details:**
Docstring at lines 1267-1275 states:
"The format string is parsed as an expression, allowing:
- String literals: PRINT USING "###.##"; X
- String variables: PRINT USING F$; X
- Any expression that evaluates to a string"

But the implementation at lines 1283-1285 requires a semicolon:
```
if not self.match(TokenType.SEMICOLON):
    raise ParseError(f"Expected ';' after PRINT USING format string at line {self.current().line}")
```

The docstring examples show semicolons but don't explicitly state they are required.

---

#### code_vs_comment

**Description:** Comment about optional comma after file number in PRINT statement doesn't match typical MBASIC behavior description

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines 1242-1247 states:
"Optionally consume comma after file number
Note: MBASIC 5.21 typically uses comma (PRINT #1, "text").
Our parser makes the comma optional for flexibility.
If semicolon appears instead of comma, it will be treated as an item
separator in the expression list below (not as a file number separator)."

This describes intentional deviation from MBASIC 5.21 standard for 'flexibility', but doesn't explain why this flexibility is needed or if it could cause compatibility issues.

---

#### code_vs_comment

**Description:** Comment in at_end_of_line() explicitly states it does NOT check for comments, but at_end_of_statement() does

**Affected files:**
- `src/parser.py`

**Details:**
Comment at lines 152-155 states:
"Note: This method does NOT check for comment tokens (REM, REMARK, APOSTROPHE).
Comments are handled separately in parse_line() where they are parsed as
statements. In practice, comments end the line regardless of COLON presence."

But at_end_of_statement() at lines 167-169 includes:
```
return token.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.COLON,
                      TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE)
```

This is intentional design (different methods for different purposes), but the relationship between these two methods and when to use each could be clearer.

---

#### code_vs_comment

**Description:** Comment about INPUT statement separator behavior may be incomplete

**Affected files:**
- `src/parser.py`

**Details:**
In parse_input() docstring:

"Note: In MBASIC 5.21, the separator after prompt affects '?' display:
- INPUT "Name"; X  displays "Name? " (semicolon AFTER prompt shows '?')
- INPUT "Name", X  displays "Name " (comma AFTER prompt suppresses '?')
Different behavior: INPUT; (semicolon IMMEDIATELY after INPUT keyword, no prompt)
suppresses the default '?' prompt entirely (tracked by suppress_question flag above)."

The code implements suppress_question flag for INPUT; syntax, but the comment doesn't clarify what happens when both INPUT; and a prompt with semicolon are used together (e.g., INPUT;"Name";X). The interaction between these two mechanisms is not documented.

---

#### code_vs_comment

**Description:** LPRINT comment about separator handling is unclear about implementation details

**Affected files:**
- `src/parser.py`

**Details:**
In parse_lprint() method:

"# Add newline if there's no trailing separator
# For N expressions: N-1 separators (between items) = no trailing separator
#                    N separators (between items + at end) = has trailing separator
if len(separators) < len(expressions):
    separators.append('\n')"

The comment explains the logic but doesn't clarify what happens when there are MORE separators than expressions (len(separators) > len(expressions)), which could occur with syntax like "LPRINT ;". The code only handles the case where separators < expressions, leaving the other case undocumented.

---

#### code_vs_comment

**Description:** DEFTYPE comment about batch vs interactive mode is incomplete

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deftype() docstring:

"Note: This method always updates def_type_map during parsing.
In batch mode (two-pass), first pass collects types, second pass uses them.
In interactive mode (single-pass), this immediately updates the type map.
The AST node is created for program serialization/documentation."

The comment describes two different modes (batch/interactive) but the code implementation doesn't show any conditional logic for these modes. The method "always updates def_type_map" regardless of mode, which suggests either: (1) the comment is describing behavior elsewhere in the system, not in this method, or (2) the two-pass behavior is not actually implemented differently in this method. The comment creates confusion about what this specific method does vs. what the overall system does.

---

#### code_vs_comment

**Description:** Comment describes CALL statement syntax incompletely compared to implementation

**Affected files:**
- `src/parser.py`

**Details:**
Comment says:
"MBASIC 5.21 syntax:
    CALL address           - Call machine code at numeric address

Extended syntax (for compatibility with other BASIC dialects):
    CALL ROUTINE(X,Y)      - Call with arguments"

But the implementation also handles CALL with FunctionCallNode, not just VariableNode with subscripts. The code checks:
- isinstance(target, VariableNode) and target.subscripts
- isinstance(target, FunctionCallNode)

The comment doesn't mention that function call syntax is also parsed.

---

#### code_vs_comment

**Description:** RESUME statement comment doesn't explain the 0 value behavior mentioned in code

**Affected files:**
- `src/parser.py`

**Details:**
Comment says: "Parse RESUME statement - Syntax: RESUME [NEXT | line_number]"

But code comment says:
"# Note: RESUME 0 means 'retry error statement' (interpreter treats 0 and None equivalently)"

The docstring doesn't document that RESUME 0 has special meaning (retry error statement), only mentioning NEXT and line_number as options.

---

#### code_vs_comment

**Description:** WIDTH statement docstring describes device parameter differently than inline comment

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

This suggests 'device' is a general device expression, but the inline comment in parse_width says:
"# device: Optional device expression (typically screen or printer)"

However, the actual MBASIC WIDTH syntax is typically WIDTH columns or WIDTH #file,columns or WIDTH LPRINT columns. The docstring's description of 'device' as 'screen or printer' may not match actual MBASIC behavior where the second parameter in WIDTH width,device form is not standard.

---

#### code_vs_comment

**Description:** COMMON statement docstring says 'just a marker' but implementation stores variable names as strings

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"The empty parentheses () indicate an array variable (all elements shared).
This is just a marker - no subscripts are specified or stored."

Then later:
"# Just store the variable name as a string
variables.append(var_name)"

The phrase 'just a marker' is ambiguous - it's unclear if it means the parentheses are a marker (which is true) or if the variable storage is just a marker (which is false - they're actually stored). The comment could be clearer that the parentheses are consumed but not stored, while the variable names themselves are stored.

---

#### code_vs_comment

**Description:** DATA statement docstring doesn't mention LINE_NUMBER token handling in unquoted strings

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"DATA items can be:
- Numbers: DATA 1, 2, 3
- Quoted strings: DATA 'HELLO', 'WORLD'
- Unquoted strings: DATA HELLO WORLD, FOO BAR

Unquoted strings extend until comma, colon, end of line, or unrecognized token"

But the code explicitly handles TokenType.LINE_NUMBER:
"elif tok.type == TokenType.LINE_NUMBER:
    string_parts.append(str(tok.value))
    self.advance()"

The docstring doesn't mention that line numbers can appear in unquoted DATA strings.

---

#### code_vs_comment

**Description:** Comment in _adjust_statement_positions mentions 'AssignmentStatementNode' as historical name but code uses 'LetStatementNode'

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_let_statement() docstring:
"Note: LetStatementNode represents both explicit LET statements (LET A=5)
and implicit assignments (A=5) in MBASIC. The node name 'LetStatementNode'
is used consistently throughout the codebase.

In _adjust_statement_positions(), 'AssignmentStatementNode' was used historically
but has been replaced by 'LetStatementNode' for consistency."

However, in _adjust_statement_positions() code, only 'LetStatementNode' is checked:
if stmt_type == 'LetStatementNode':

The comment references historical usage that no longer exists in the code.

---

#### documentation_inconsistency

**Description:** apply_keyword_case_policy docstring says 'function handles normalization internally' but implementation shows only first_wins policy normalizes to lowercase

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring: "Args:
    keyword: The keyword to transform (may be any case - function handles normalization internally)"

And: "Note: The first_wins policy normalizes keywords to lowercase for lookup purposes.
Other policies transform the keyword directly."

This is contradictory - the note says only first_wins normalizes, but the Args description implies all policies handle normalization internally. The code shows most policies just call .lower(), .upper(), or .capitalize() directly on the input without normalization.

---

#### code_vs_comment

**Description:** renumber_with_spacing_preservation docstring says 'caller should call serialize_line()' twice in different phrasings

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring contains:
"3. Adjusts token column positions to account for line number length changes
4. Text can then be regenerated from updated AST using serialize_line()
   (caller should call serialize_line() on each returned LineNode to regenerate text)"

And in Returns section:
"Returns:
    Dict of new_line_number -> LineNode (with updated positions)
    Caller should serialize these LineNodes using serialize_line() to get text"

This instruction is repeated unnecessarily, suggesting possible documentation debt or unclear responsibility boundaries.

---

#### code_vs_comment

**Description:** Comment says operators are not stored as separate tokens but code emits them as tokens with None column

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_let_statement:
"# Equals sign (operator position not tracked - using None for column)
# Operators are not stored as separate tokens in AST, so position is inferred
result += self.emit_token("=", None, "LetOperator")"

The comment says operators are not stored as tokens, but the code calls emit_token() to emit them. The comment should say 'operator positions are not tracked in AST' rather than 'operators are not stored as separate tokens' since they clearly are emitted as tokens during serialization.

---

#### documentation_inconsistency

**Description:** apply_keyword_case_policy has 'preserve' policy that docstring says should be handled by caller, but function provides fallback implementation

**Affected files:**
- `src/position_serializer.py`

**Details:**
In apply_keyword_case_policy:
elif policy == "preserve":
    # The "preserve" policy should be handled by the caller passing in the original case
    # rather than calling this function. However, we provide a defensive fallback
    # (capitalize) in case this function is called with "preserve" policy.
    return keyword.capitalize()

This suggests unclear API design - if preserve should be handled by caller, why accept it as a policy value? The defensive fallback indicates the responsibility boundary is unclear.

---

#### code_vs_comment_conflict

**Description:** Comment in check_array_allocation says calculation matches execute_dim() but we cannot verify without seeing that code

**Affected files:**
- `src/resource_limits.py`

**Details:**
Line 163-164 comment states:
# Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21
# This calculation matches the array creation logic in src/interpreter.py execute_dim()

Line 168-169 code:
for dim_size in dimensions:
    total_elements *= (dim_size + 1)  # +1 for 0-based indexing

Without access to src/interpreter.py execute_dim(), we cannot verify if these actually match. The comment claims they do, but this is unverifiable from the provided code.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for string length limit description across different preset functions

**Affected files:**
- `src/resource_limits.py`

**Details:**
In create_web_limits():
max_string_length=255,              # 255 bytes (MBASIC 5.21 compatibility)

In create_local_limits():
max_string_length=255,              # 255 bytes (MBASIC 5.21 compatibility)

In create_unlimited_limits():
max_string_length=1024*1024,        # 1MB strings (for testing/development - not MBASIC compatible)

The comment in create_unlimited_limits() says 'not MBASIC compatible' but the parameter docstring at line 50 says 'Maximum length for a string variable (bytes)' without mentioning MBASIC compatibility as a general constraint. This could be clarified in the main docstring.

---

#### code_vs_comment_conflict

**Description:** Comment says 'length + overhead' but code adds fixed 4 bytes regardless of actual overhead

**Affected files:**
- `src/resource_limits.py`

**Details:**
Line 145-147:
elif var_type == TypeInfo.STRING:
    # String: length + overhead
    if isinstance(value, str):
        return len(value.encode('utf-8')) + 4  # +4 for length prefix

The comment says 'length + overhead' which is vague, but the inline comment '+4 for length prefix' is more specific. The actual overhead might be different in the real MBASIC implementation. This is a minor documentation clarity issue.

---

#### documentation_inconsistency

**Description:** Module docstring mentions 'basic programs' but find_basic_dir() explicitly states it's development-only and not distributed

**Affected files:**
- `src/resource_locator.py`

**Details:**
Line 1 docstring:
"""Resource locator for finding package data files (docs, basic programs, etc.)"""

But line 115-120:
def find_basic_dir() -> Optional[Path]:
    """Find the basic programs directory (development only).

    Returns:
        Path to basic/ directory, or None if not in development mode
    """
    # basic/ directory is development-only, not distributed

The module docstring suggests 'basic programs' are package data files that can be located, but the function clearly states they're development-only. The module docstring should clarify this distinction.

---

#### code_vs_comment

**Description:** Comment in dimension_array() says DIM is tracked as both read and write for debugger purposes, but this is implementation detail not clearly justified

**Affected files:**
- `src/runtime.py`

**Details:**
In dimension_array() method:
"# Note: DIM is tracked as both read and write for debugger display purposes.
# Technically DIM is an allocation/initialization (write-only), but tracking it
# as both allows debuggers to show 'last accessed' info for unaccessed arrays."

The code sets both last_read and last_write to the same tracking_info, but the justification 'allows debuggers to show last accessed info for unaccessed arrays' is unclear. If an array is unaccessed after DIM, showing DIM location as 'last read' is semantically incorrect - it was never read, only allocated.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'canonical case' vs 'original case' in variable tracking

**Affected files:**
- `src/runtime.py`

**Details:**
In _check_case_conflict() method, the return value is described as:
"Returns:
    str: The canonical case to use for this variable (might differ from original_case)"

But in set_variable() and get_variable(), the parameter is named 'original_case' and stored as 'original_case' in the variable entry:
"self._variables[full_name]['original_case'] = canonical_case  # Store canonical case"

The field name 'original_case' suggests it stores the original case from source, but the comment says it stores the canonical case. This naming is confusing - should either rename the field to 'canonical_case' or clarify that 'original_case' means 'the original case to use for display' (i.e., the canonical one).

---

#### code_vs_comment

**Description:** Comment in push_for_loop says nested FOR loops with same variable not allowed, but error message says 'already active'

**Affected files:**
- `src/runtime.py`

**Details:**
In push_for_loop() method:
Comment: "# This prevents nested FOR loops with the same variable (e.g., FOR I=1 TO 10 / FOR I=1 TO 5)"
Error message: "raise RuntimeError(f'FOR loop variable {var_name} already active - nested FOR loops with same variable not allowed')"

The comment example 'FOR I=1 TO 10 / FOR I=1 TO 5' is unclear - the '/' separator is not BASIC syntax. Should probably be 'FOR I=1 TO 10: FOR I=1 TO 5' or use line breaks to show nesting more clearly.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for statement offset indexing - sometimes described as '0-based index' and other times with explicit examples showing '0 = 1st statement'

**Affected files:**
- `src/runtime.py`

**Details:**
Multiple locations use different phrasings:

1. get_gosub_stack() docstring:
"Note: stmt_offset is a 0-based index where 0 = 1st statement, 1 = 2nd statement, etc."

2. set_breakpoint() docstring:
"Note: offset 0 = 1st statement, offset 1 = 2nd statement, offset 2 = 3rd statement, etc."

3. get_execution_stack() docstring:
"This shows: FOR I at line 100, statement 0 (1st statement)"

While all are technically correct, the inconsistent phrasing (sometimes '0-based index', sometimes explicit enumeration) could be standardized for clarity.

---

#### code_vs_comment

**Description:** Comment in parse_name() helper function describes a fallback behavior for variables without type suffixes, but this scenario should not occur according to the comment itself

**Affected files:**
- `src/runtime.py`

**Details:**
In get_variables() method, parse_name() helper:

Comment says:
"# No explicit suffix - default to single precision (!)
# Note: In _variables, all names should already have resolved type suffixes
# from _resolve_variable_name() which applies DEF type rules. This fallback
# handles edge cases where a variable was stored without a type suffix."

The comment acknowledges that all names in _variables should already have type suffixes, making the fallback code theoretically unreachable. This suggests either:
1. The comment is outdated and the fallback is actually needed
2. The fallback is defensive programming for impossible cases
3. There are edge cases not mentioned

---

#### documentation_inconsistency

**Description:** get_loop_stack() marked as deprecated but no deprecation timeline or version information provided

**Affected files:**
- `src/runtime.py`

**Details:**
Method definition:
def get_loop_stack(self):
    """Deprecated: Use get_execution_stack() instead."""
    return self.get_execution_stack()

The deprecation notice doesn't indicate when it was deprecated, when it might be removed, or what version introduced the replacement. Standard deprecation practices include this information.

---

#### code_vs_comment

**Description:** Docstring claims file-level settings infrastructure exists but is not implemented, yet the code has full implementation

**Affected files:**
- `src/settings.py`

**Details:**
SettingsManager docstring says:
"Note: File-level settings infrastructure exists (file_settings dict, FILE scope), but there are currently no settings defined with FILE scope in settings_definitions.py, and there is no UI or command to manage per-file settings yet. This is reserved for future use."

However, the code fully implements file-level settings:
- file_settings dict is initialized
- get() method checks file_settings first in precedence
- set() method supports SettingScope.FILE
- reset_to_defaults() supports SettingScope.FILE

The infrastructure is complete, not partial. The comment should clarify that the implementation is complete but unused (no FILE-scoped settings defined, no UI).

---

#### code_vs_comment

**Description:** Token dataclass docstring claims original_case and original_case_keyword should be mutually exclusive, but dataclass doesn't enforce this

**Affected files:**
- `src/tokens.py`

**Details:**
Token dataclass docstring states:
"Note: These fields serve different purposes and should be mutually exclusive (identifiers use original_case, keywords use original_case_keyword):
- original_case: For identifiers (user variables) - preserves what user typed
- original_case_keyword: For keywords - stores policy-determined display case
The dataclass doesn't enforce this exclusivity, but code should maintain it."

The comment acknowledges the dataclass doesn't enforce exclusivity but says "code should maintain it". This creates ambiguity - if it's important enough to document as a rule, it should either be enforced in code or the comment should explain why it's not enforced and what happens if both are set.

---

#### code_vs_documentation

**Description:** Module docstring references src/lexer.py and src/parser.py but these files are not provided in the source code listing

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
simple_keyword_case.py docstring mentions:
"This is a simplified keyword case handler used by the lexer (src/lexer.py)."
"For advanced policies (first_wins, preserve, error) via CaseKeeperTable, see KeywordCaseManager (src/keyword_case_manager.py) which is used by src/parser.py and src/position_serializer.py."
"The lexer (src/lexer.py) uses SimpleKeywordCase..."

Files src/lexer.py, src/parser.py, src/position_serializer.py, and src/keyword_case_manager.py are referenced but not included in the provided source code. Cannot verify if these references are accurate or if the integration works as described.

---

#### code_vs_comment

**Description:** Comment claims tab_size setting is not included because tab key is used for window switching, but this is UI-specific reasoning in a general settings module

**Affected files:**
- `src/settings_definitions.py`

**Details:**
In SETTING_DEFINITIONS comments:
"# Note: Tab key is used for window switching in curses UI, not indentation
# editor.tab_size setting not included - not relevant for BASIC"

This comment conflates UI behavior (curses window switching) with settings definitions. The settings module should be UI-agnostic. The real reason tab_size isn't relevant is that BASIC uses line numbers, not indentation for structure. The curses UI detail is implementation-specific and doesn't belong in settings_definitions.py.

---

#### documentation_inconsistency

**Description:** SettingsManager.__init__ docstring mentions Redis backend but FileSettingsBackend is the only concrete backend imported

**Affected files:**
- `src/settings.py`

**Details:**
SettingsManager.__init__ docstring:
"Args:
    project_dir: Optional project directory for project-level settings
    backend: Optional settings backend (defaults to FileSettingsBackend)"

And in __init__:
```
# Settings backend (file or Redis)
if backend is None:
    backend = FileSettingsBackend(project_dir)
self.backend = backend
```

The comment says "file or Redis" but only FileSettingsBackend is imported and used as default. RedisSettingsBackend exists in settings_backend.py but is never imported or used in settings.py. The factory function create_settings_backend() in settings_backend.py handles Redis, but SettingsManager doesn't use it.

---

#### code_vs_documentation

**Description:** Settings widget footer shows keyboard shortcuts that don't match the keybindings constants used in the code

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Footer text in _create_body: 'f"↑↓ {key_to_display(ENTER_KEY)}=OK  {key_to_display(ESC_KEY)}/{key_to_display(SETTINGS_KEY)}=Cancel  {key_to_display(SETTINGS_APPLY_KEY)}=Apply  {key_to_display(SETTINGS_RESET_KEY)}=Reset"'
But keypress method shows: 'elif key == SETTINGS_RESET_KEY: self._on_reset()'
The SETTINGS_RESET_KEY constant is imported but its actual value is not defined in the visible code, making it unclear if the display matches the actual key binding.

---

#### code_vs_comment

**Description:** Comment in _create_setting_widget mentions 'strip force_ prefix for cleaner display' but the implementation uses removeprefix with a fallback that doesn't match the comment's intent

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment: '# Create display label (strip force_ prefix for cleaner display)\n# Use removeprefix to only strip from the beginning, not anywhere in the string'
Code: 'display_label = choice.removeprefix(\'force_\') if hasattr(str, \'removeprefix\') else (choice[6:] if choice.startswith(\'force_\') else choice)'
The fallback code 'choice[6:]' assumes 'force_' is exactly 6 characters, which is correct, but the comment about 'not anywhere in the string' is misleading since both implementations only strip from the beginning.

---

#### documentation_inconsistency

**Description:** UIBackend docstring lists 'Future/potential backend types (not yet implemented)' including HeadlessBackend for batch processing, but this contradicts the purpose of a UI backend

**Affected files:**
- `src/ui/base.py`

**Details:**
base.py docstring: 'Future/potential backend types (not yet implemented):\n- WebBackend: Browser-based interface\n- HeadlessBackend: No UI, for batch processing'
A 'HeadlessBackend' with 'No UI' seems contradictory to the purpose of a UIBackend class. This might be better suited as a separate execution mode rather than a UI backend.

---

#### code_vs_comment

**Description:** TODO comment in _add_debug_help suggests integration with help system but no indication of what help system exists or how to integrate

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
_add_debug_help method:
'def _add_debug_help(self):\n    """Add debug commands to help system (not yet implemented)"""\n    # TODO: Integrate debug commands with help system\n    pass'
No context provided about what help system this refers to or where it's defined.

---

#### code_vs_comment

**Description:** Comment in _on_reset says 'Set all widgets to default values' but the enum handling uses get_label() comparison which compares display labels, not actual values

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
_on_reset method for ENUM type:
'elif defn.type == SettingType.ENUM:\n    # Set radio button to default\n    for rb in widget:\n        rb.set_state(rb.get_label() == defn.default)'
This compares the display label (which has 'force_' prefix stripped) against defn.default (which likely has the prefix), so it may not work correctly.

---

#### code_vs_comment

**Description:** Comment in keypress method describes column positions that don't match variable-width implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress method:
"Handle key presses for column-aware editing and auto-numbering.

Format: 'S<linenum> CODE' (where <linenum> is variable width)
- Column 0: Status (●, ?, space) - read-only
- Columns 1+: Line number (variable width) - editable
- After line number: Space
- After space: Code - editable"

This is accurate, but later in _sort_and_position_line:
"target_column: Column to position cursor at (default: 7). This value is an
              approximation for typical line numbers. Since line numbers have
              variable width, the actual code area start position varies."

The default value of 7 suggests an assumption about typical line number width (status=1, number=5, space=1), but this is not documented in the main format description.

---

#### code_vs_comment

**Description:** Comment about auto-numbering bug fix references wrong symptom

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_display method:
"# DON'T increment counter here - that happens only on Enter
# This was the bug causing '0    1' issue"

The comment references a '0    1' issue but doesn't explain what this means or how not incrementing here fixes it. The context suggests it's about not incrementing next_auto_line_num when displaying an empty program, but the symptom description is unclear.

---

#### code_vs_comment

**Description:** Comment about syntax error checking timing is misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress method:
"# Check syntax when leaving line or pressing control keys
# (Not during normal typing - avoids annoying errors for incomplete lines)"

But the code checks syntax on ANY control key, up/down arrow, other nav key, or tab - which could include keys pressed during typing (like Ctrl+A to select all). The comment implies it only checks when navigating away, but the implementation is broader.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of empty lines in syntax checking

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_syntax_errors:
"# Skip empty code lines
if not code_area.strip() or line_number is None:
    # Clear error status for empty lines, but preserve breakpoints
    if line_number is not None and line_number > 0:
        new_status = self._get_status_char(line_number, has_syntax_error=False)"

But in _check_line_syntax:
"if not code_text or not code_text.strip():
    # Empty lines are valid
    return (True, None)"

The first checks 'line_number > 0' but the second doesn't check line number at all. This could lead to inconsistent behavior for line 0 (if it exists).

---

#### code_vs_comment

**Description:** Comment about urwid automatic redraw is redundant

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _on_enter_idle method, the comment appears twice:
"# urwid automatically redraws screen after this callback returns"

Once in the middle of the method and once at the end. This redundancy suggests the comment may have been copied during refactoring.

---

#### code_vs_comment

**Description:** Comment about toolbar removal contradicts implementation in _create_ui

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _create_ui() method around line ~1150, comment says:
"# Toolbar removed from UI layout - use Ctrl+U menu instead for keyboard navigation
# (_create_toolbar method still exists but is not called)"

This confirms the toolbar is not used, but the _create_toolbar method is fully functional and could be called. The comment suggests it 'still exists' as if it's a stub, but it's actually a complete implementation.

---

#### code_vs_comment

**Description:** Comment about interpreter lifecycle contradicts actual behavior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment around line ~920 states:
"# Interpreter Lifecycle:
# Created ONCE here in __init__ and reused throughout the session.
# The interpreter is NOT recreated in start() - only ImmediateExecutor is."

This is accurate for the interpreter, but the following comment says:
"# Note: The immediate_io handler created here is temporary - ImmediateExecutor
# will be recreated in start() with a fresh OutputCapturingIOHandler, but
# this same interpreter instance will be reused with the new executor."

However, in start() method around line ~1000, a NEW interpreter is NOT passed to ImmediateExecutor - the existing self.interpreter is reused. The comment is correct but could be clearer that the interpreter object itself is never recreated.

---

#### documentation_inconsistency

**Description:** Comment about Clear Output keyboard shortcut is outdated

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1420 states:
"# Note: Clear output removed from keyboard shortcuts (^Y now used for quit)
# Clear output still available via menu: Ctrl+U -> Output -> Clear Output"

However, QUIT_ALT_KEY is defined as Ctrl+C (not Ctrl+Y) based on the _handle_input() method around line ~1350 which checks 'key == QUIT_ALT_KEY' alongside the Ctrl+C handler. The comment incorrectly states ^Y is used for quit.

---

#### code_vs_comment

**Description:** Comment about editor.lines vs editor_lines storage is confusing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment around line ~850 states:
"# Note: self.editor_lines is the CursesBackend's storage dict
# self.editor.lines is the ProgramEditorWidget's storage dict (different object)"

This suggests two separate storage locations, but throughout the code, only self.editor.lines is used for line storage (e.g., in _refresh_editor(), _smart_insert_line()). The self.editor_lines dict is initialized but appears to be used differently (for execution state, not editing). The comment makes it sound like they serve the same purpose but are different objects, which is misleading.

---

#### code_vs_comment

**Description:** Multiple comments say 'Status bar stays at default' but the default status is not defined in visible code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Throughout the file, comments like:
"# Status bar stays at default - error is displayed in output"
"# No status bar update - status bar stays at default"
"# Status bar stays at default - error is in output"

appear multiple times, but the actual 'default' status bar text (STATUS_BAR_SHORTCUTS) is referenced but not shown in this code snippet. The comment pattern suggests a convention but the default value is not visible for verification.

---

#### code_vs_comment

**Description:** Comment describes main widget retrieval strategy inconsistently across methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _show_help(), _show_keymap(), _show_settings():
"Main widget retrieval: Use self.base_widget (stored at UI creation time in __init__)
rather than self.loop.widget (which reflects the current widget and might be a menu
or other overlay). This approach is used consistently by _show_help, _show_keymap,
and _show_settings since they create overlays and don't need to unwrap existing ones."

But in _activate_menu():
"Main widget storage: Unlike _show_help/_show_keymap/_show_settings which use
self.base_widget directly, this method extracts base_widget from self.loop.widget
to unwrap any existing overlay. This differs from _show_help/_show_keymap/_show_settings
which use self.base_widget directly, since menu needs to work even when other overlays are already present."

The comments acknowledge the inconsistency but don't explain why _activate_menu needs different behavior when the other methods claim to handle overlays correctly.

---

#### internal_inconsistency

**Description:** Inconsistent error message formatting between different error handlers

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _run_program() parse errors use:
"┌─ Parse Error ────────────────────────────────────┐"

In _execute_tick() runtime errors use:
"┌─ Runtime Error ──────────────────────────────────┐"

In _run_program() startup errors use:
"┌─ Startup Error ──────────────────────────────────┐"

In _run_program() unexpected errors use:
"┌─ Unexpected Error ───────────────────────────────┐"

The box width and dash count varies slightly (some have more dashes than others), creating visual inconsistency in error display formatting.

---

#### code_vs_comment

**Description:** Comment says output is logged to output pane 'not separate immediate history', but there's no evidence of a separate immediate history feature anywhere

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1040: "# Log the command to output pane (not separate immediate history)\nself.output_walker.append(make_output_line(f\"> {command}\"))"

The parenthetical note suggests there was or could be a separate immediate history, but no such feature exists in the code. This is likely an outdated comment from a design discussion.

---

#### code_vs_comment

**Description:** Comment in _get_input_for_interpreter says 'like BASIC STOP statement' but INPUT cancellation is not the same as STOP

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~240: "# If user cancelled (ESC), stop program execution (like BASIC STOP statement)"

This is misleading because STOP is a deliberate program statement that can be CONTinued from, while ESC during INPUT is user cancellation. The behavior may be similar (setting stopped=True) but the semantics are different.

---

#### code_vs_comment_conflict

**Description:** Comment says 'Project has internal implementation version (src/version.py) separate from this' but this creates confusion about version management strategy.

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Comment at line ~73:
"# Hardcoded MBASIC version for documentation
# Note: Project has internal implementation version (src/version.py) separate from this
return "5.21"  # MBASIC 5.21 language version"

This comment suggests there are two version numbers (documentation version 5.21 and implementation version in src/version.py), which could lead to version mismatch issues. The comment should clarify why these are separate and how they relate.

---

#### code_inconsistency

**Description:** Menu uses keybindings module constants (kb.HELP_KEY, kb.SAVE_KEY, etc.) but help_widget.py hardcodes its navigation keys. This inconsistency in keybinding usage patterns across UI components could confuse developers.

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
interactive_menu.py imports and uses:
"from . import keybindings as kb
from .keybindings import key_to_display"

Then uses constants like:
"(f'Help           {key_to_display(kb.HELP_KEY)}', '_show_help'),
(f'Save           {key_to_display(kb.SAVE_KEY)}', '_save_program'),"

But help_widget.py hardcodes keys in keypress():
"if key in ('q', 'Q', 'esc'):
elif key == '/':
elif key == 'u' or key == 'U':"

This architectural inconsistency means some UI components use centralized keybinding configuration while others hardcode keys.

---

#### code_vs_comment_conflict

**Description:** Comment describes _create_text_markup_with_links as finding 'ALL [text] patterns' but the implementation also handles [text](url) format which isn't mentioned in the summary.

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Docstring at line ~237:
"Convert plain text lines to urwid markup with link highlighting.

Links are marked with [text] in the rendered output. This method
finds ALL [text] patterns for display/navigation, but uses the renderer's
links for target mapping when following links."

But code at line ~258 shows:
"# Match both [text] and [text](url) formats
link_pattern = r'\[([^\]]+)\](?:\([^)]+\))?'"

The docstring should mention that both [text] and [text](url) formats are supported.

---

#### code_vs_comment_conflict

**Description:** Comment in _build_link_mapping says 'For links in headings like [text](url), we parse the URL directly since the renderer doesn't extract them' but doesn't explain why the renderer doesn't extract them or if this is expected behavior.

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~295:
"Build a mapping from visual link indices (all [text] patterns) to
renderer link indices (only links with targets).

This allows us to show all [text] as clickable, but only follow the ones
that have actual targets from the renderer.

For links in headings like [text](url), we parse the URL directly since
the renderer doesn't extract them."

This suggests a limitation or design decision in the renderer that isn't documented. It's unclear if this is a bug in the renderer or intentional behavior.

---

#### documentation_inconsistency

**Description:** KeybindingLoader class provides utilities for Tkinter bindings (get_tk_accelerator, get_tk_bindings, bind_all_to_tk) but the file is in src/ui/ alongside curses-specific files, and there's no indication of how this relates to the curses UI or if it's used by a separate Tk UI.

**Affected files:**
- `src/ui/keybinding_loader.py`

**Details:**
keybinding_loader.py docstring:
"Keybinding loader for UI backends.

Loads keybindings from JSON config and provides utilities for applying them to UI frameworks."

The class has Tk-specific methods:
"def get_tk_accelerator(self, section: str, action: str) -> str:
def get_tk_bindings(self, section: str, action: str) -> List[str]:
def bind_all_to_tk(self, widget, section: str, action: str, handler) -> None:"

But there's no documentation about whether a Tk UI exists, is planned, or if this is dead code. The architecture isn't clear.

---

#### code_vs_comment_conflict

**Description:** Comment says 'QUIT_KEY is None (menu-only)' and 'STACK_KEY is '' (menu-only)' but doesn't explain why these actions don't have keyboard shortcuts or if this is intentional design.

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Comments in menu definition:
"('Quit', 'quit'),  # QUIT_KEY is None (menu-only)
...
('Execution Stack', '_toggle_stack_window'),  # STACK_KEY is '' (menu-only)"

These comments suggest some actions are intentionally menu-only, but there's no documentation explaining the design rationale or whether users can configure shortcuts for these actions.

---

#### Code vs Comment conflict

**Description:** Comment says 'Continue execution (Go) / Go to line' but variable is named CONTINUE_KEY, creating ambiguity about whether it's for continuing execution or going to a line

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line ~155:
# Continue execution (Go) / Go to line
_continue_from_json = _get_key('editor', 'goto_line')
CONTINUE_KEY = _ctrl_key_to_urwid(_continue_from_json) if _continue_from_json else 'ctrl g'

The comment describes two different actions ('Continue execution' and 'Go to line'), but the JSON key is 'goto_line' and the variable is CONTINUE_KEY. The KEYBINDINGS_BY_CATEGORY later shows this as 'Continue execution (Go)' only.

---

#### Code vs Comment conflict

**Description:** Comment says 'Quit - No keyboard shortcut' but then defines QUIT_ALT_KEY with a keyboard shortcut (Ctrl+C)

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines ~95-100:
# Quit - No keyboard shortcut (most Ctrl keys intercepted by terminal or already assigned)
# Use menu: Ctrl+U -> File -> Quit, or Ctrl+C (interrupt) will also quit
QUIT_KEY = None  # No keyboard shortcut

# Alternative quit (interrupt signal)
_quit_alt_from_json = _get_key('editor', 'continue')
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

The comment says there's no keyboard shortcut, but then immediately defines an alternative quit key. Also, QUIT_ALT_KEY loads from 'editor.continue' which seems wrong - it should probably load from a 'quit' action.

---

#### Documentation inconsistency

**Description:** KEYBINDINGS_BY_CATEGORY does not include all defined keybindings - missing CLEAR_BREAKPOINTS_KEY, DELETE_LINE_KEY, RENUMBER_KEY, INSERT_LINE_KEY, STOP_KEY, MAXIMIZE_OUTPUT_KEY, and several others

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Defined but not in KEYBINDINGS_BY_CATEGORY:
- CLEAR_BREAKPOINTS_KEY = 'ctrl shift b'
- STOP_KEY = 'ctrl x'
- MAXIMIZE_OUTPUT_KEY = 'ctrl shift m'
- STACK_KEY (though it's empty)
- Various dialog and settings keys

These are defined as constants but not documented in the help system.

---

#### Code inconsistency

**Description:** keymap_widget.py has its own _format_key_display function that converts Ctrl+ to ^ notation, but keybindings.py already has key_to_display() that does similar formatting - potential duplication

**Affected files:**
- `src/ui/keymap_widget.py`

**Details:**
In keymap_widget.py:
def _format_key_display(key_str):
    if key_str.startswith('Ctrl+'):
        return '^' + key_str[5:]
    elif key_str.startswith('Shift+Ctrl+'):
        return 'Shift+^' + key_str[11:]
    return key_str

In keybindings.py:
def key_to_display(urwid_key):
    # Similar conversion logic

These two functions handle similar conversions but work with different input formats (Ctrl+ vs urwid format).

---

#### Documentation inconsistency

**Description:** Module docstring says keybindings are loaded from curses_keybindings.json but this file is not provided in the source code files

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line ~7:
This module loads keybindings from curses_keybindings.json and provides them
in the format expected by the Curses UI (urwid key names, character codes, display names).

The JSON file curses_keybindings.json is referenced but not included in the provided source files, making it impossible to verify consistency.

---

#### Code vs Documentation inconsistency

**Description:** Return key binding for in-page search navigation not documented

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
In tk_help_browser.py line 139:
self.inpage_search_entry.bind('<Return>', lambda e: self._inpage_find_next())

This Return key binding executes 'find next' when in the in-page search box, but is not documented in tk_keybindings.json under help_browser section. The only 'Return' binding documented is for the main search box, not the in-page search box.

---

#### Code vs Comment conflict

**Description:** Comment says dialog is modal but implementation doesn't use wait_window()

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 48:
# Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())
self.transient(parent)
self.grab_set()

The comment correctly describes the behavior - grab_set() makes it modal in terms of preventing interaction with parent, but without wait_window() it doesn't block code execution. This is accurate documentation of the implementation, not a conflict.

---

#### Code internal inconsistency

**Description:** Inconsistent handling of link tag prefixes in context menu

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In tk_help_browser.py line 598-602:
for tag in tags:
    if tag.startswith("link_") or tag.startswith("result_link_"):
        link_tag = tag
        break

The code checks for both 'link_' and 'result_link_' prefixes. However, in _execute_search() at line 424, result links use tag name 'result_link_{counter}', while in _render_line_with_links() at line 267, regular links use 'link_{counter}'. Both are stored in self.link_urls dictionary. This is consistent, but the naming convention could be clearer - 'result_link_' is redundant since all links are stored the same way.

---

#### Documentation inconsistency

**Description:** Docstring mentions features not fully described

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Module docstring at line 1-9 states:
"Provides:
- Scrollable help content display
- Clickable links
- Search across multi-tier help system with ranking and fuzzy matching
- In-page search (Ctrl+F) with match highlighting
- Navigation history (back button)"

This list doesn't mention:
- Context menu with 'Open in New Window' for links
- Home button navigation
- Search result display with tier markers
- Table formatting

While not critical, the docstring could be more complete.

---

#### Code vs Comment conflict

**Description:** Comment about table formatting duplication may be outdated

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In tk_help_browser.py line 663-666:
"""Format a markdown table row for display.

Note: This implementation is duplicated in src/ui/markdown_renderer.py.
Consider extracting to a shared utility module if additional changes are needed.
"""

This comment suggests code duplication exists in markdown_renderer.py, but that file is not provided in the source files. Cannot verify if this is accurate or if the duplication has been resolved.

---

#### Code vs Comment conflict

**Description:** Comment about tooltip is inaccurate

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In tk_settings_dialog.py line 169-172:
else:
    # Show short help as inline label (not a hover tooltip, just a gray label)
    if defn.help_text:
        help_label = ttk.Label(frame, text=defn.help_text,

The comment says 'not a hover tooltip, just a gray label' which accurately describes the implementation. This is correct documentation, not a conflict.

---

#### Code internal inconsistency

**Description:** Inconsistent path normalization approach

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In _follow_link() method (lines 283-318), path resolution uses multiple approaches:
1. Checks for absolute paths with startswith('/') or 'common/' or ':/' or ':\\'
2. Uses Path.resolve() and relative_to() for relative paths
3. Normalizes with replace('\\', '/')

In _open_link_in_new_window() method (lines 625-648), similar logic is duplicated with slight variations. This duplication could lead to inconsistent behavior if one is updated without the other.

---

#### code_vs_comment

**Description:** Comment states immediate_history and immediate_status are set to None for defensive programming, but this contradicts the earlier docstring claim about immediate mode features

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 244-247 state:
        # Set immediate_history and immediate_status to None
        # These attributes are not currently used but are set to None for defensive programming
        # in case future code tries to access them (will get None instead of AttributeError)
        self.immediate_history = None
        self.immediate_status = None

However, the class docstring at lines 44-67 describes 'Immediate mode input line' as a feature, and line 113 initializes self.immediate_history = None and self.immediate_status = None in __init__. The comment suggests these are unused placeholders, but the architecture implies they should be functional components.

---

#### code_vs_comment

**Description:** Comment at line 113 says 'Immediate mode' but the attributes initialized are set to None and described as unused in later comments

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line 113 comment:
        # Immediate mode

Followed by:
        self.immediate_executor = None
        self.immediate_history = None
        self.immediate_entry = None
        self.immediate_status = None

But lines 244-247 explicitly state immediate_history and immediate_status are 'not currently used'. This creates confusion about whether immediate mode is fully implemented or partially stubbed out.

---

#### code_vs_comment

**Description:** Comment at line 406 states 'Note: Toolbar has been simplified' but doesn't explain what was removed or why

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 406-411:
        # Note: Toolbar has been simplified to show only essential execution controls.
        # Additional features are accessible via menus:
        # - List Program → Run > List Program
        # - New Program (clear) → File > New
        # - Clear Output → Run > Clear Output

This comment suggests a refactoring occurred but doesn't provide context about the previous state or the rationale for simplification. This is informational but could confuse developers looking at the history.

---

#### documentation_inconsistency

**Description:** Usage example in docstring references ConsoleIOHandler but the actual implementation uses TkIOHandler

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 64-72 show usage example:
        from src.iohandler.console import ConsoleIOHandler
        from src.editing.manager import ProgramManager
        from src.ui.tk_ui import TkBackend

        io = ConsoleIOHandler()
        def_type_map = {}  # Type suffix defaults for variables (DEFINT, DEFSNG, etc.)
        program = ProgramManager(def_type_map)
        backend = TkBackend(io, program)
        backend.start()  # Runs Tk mainloop until window closed

But line 279 shows:
        tk_io = TkIOHandler(self._add_output, self.root, backend=self)

The usage example should probably use TkIOHandler instead of ConsoleIOHandler for consistency with the actual implementation.

---

#### code_vs_comment

**Description:** Comment says formatting may occur elsewhere but contradicts itself about preserving compatibility

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1750-1755 in _refresh_editor:
Comment: "Insert line exactly as stored from program manager - no formatting applied here
Note: Some formatting may occur elsewhere (e.g., variable display, stack display)
This preserves compatibility with real MBASIC for program text"

The comment claims no formatting is applied to preserve compatibility, but then notes formatting may occur elsewhere. This is confusing - either formatting occurs or it doesn't. The note about 'elsewhere' suggests formatting does happen, contradicting the preservation claim.

---

#### code_vs_comment

**Description:** Comment about validation timing doesn't match when method is actually called

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1830-1835 in _validate_editor_syntax:
Comment: "Note: This method is called with a delay (100ms) after cursor movement/clicks to avoid excessive validation during rapid editing"

However, looking at the callers:
- _on_cursor_move: calls with 100ms delay (matches comment)
- _on_mouse_click: calls with 100ms delay (matches comment)
- _on_focus_out: calls immediately with no delay (contradicts comment)
- _check_line_change: not shown but likely calls it

The comment is incomplete - it doesn't mention the immediate call from _on_focus_out.

---

#### code_vs_comment

**Description:** Comment about when _remove_blank_lines is called is incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1900-1905 in _remove_blank_lines:
Comment: "Currently called only from _on_enter_key (after each Enter key press), not after pasting or other modifications."

This comment describes current behavior but doesn't explain why it's limited to Enter key only. If blank line removal is desirable, why not after paste? The comment raises questions about design intent without answering them.

---

#### code_vs_comment

**Description:** Comment about error display behavior is vague and potentially misleading

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1850-1855 in _validate_editor_syntax:
Comment: "Only show error list in output if there are multiple errors or this is the first time
Don't spam output on every keystroke"

Code:
should_show_list = len(errors_found) > 1

The code only checks for multiple errors, not 'first time'. The comment mentions 'first time' but there's no tracking of whether this is the first validation. The comment is misleading about what the code actually does.

---

#### code_vs_comment

**Description:** Comment about clearing yellow highlight doesn't explain why or when it's restored

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~1885 in _on_mouse_click:
Comment: "Clear yellow statement highlight when clicking (allows text selection to be visible)"

The comment explains why the highlight is cleared but doesn't mention when/how it gets restored. This is incomplete information for understanding the highlighting behavior lifecycle.

---

#### code_vs_comment

**Description:** Comment says 'Allow editing keys (backspace, delete)' but these keys DO modify text, contradicting the comment's categorization

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1186 says:
# Allow editing keys (backspace, delete) - these modify text but aren't input

This comment is confusing because it says 'these modify text but aren't input'. Backspace and delete ARE input keys that modify text. The distinction being made is unclear - perhaps it means they aren't 'character input' but they are still 'editing input'.

---

#### code_vs_comment

**Description:** Comment says 'DON'T save to program yet' but doesn't explain what happens if user never types anything

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1548 says:
# DON'T save to program yet - the line is blank and would be filtered out by
# _save_editor_to_program() which skips blank lines. Just position the cursor on
# the new line so user can start typing. The line will be saved to program when:
# 1. User types content and triggers _on_key_release -> _save_editor_to_program()
# 2. User switches focus or saves the file
# If user never types anything, the blank line remains in editor but won't be saved.

The last sentence says 'blank line remains in editor but won't be saved', but there's a _remove_blank_lines() function that gets called. The interaction between these mechanisms isn't clear from the comment.

---

#### code_vs_comment

**Description:** Docstring for _setup_immediate_context_menu() says it's unused/dead code but method is fully implemented

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring states: "NOTE: This method is currently unused - immediate_history is always None in the Tk UI (see __init__). This is dead code retained for potential future use if immediate mode gets its own output widget."

However, the method contains complete implementation with menu creation, event handlers, and bindings. If truly dead code, it should either be removed or the comment should clarify whether it's actually called anywhere.

---

#### documentation_inconsistency

**Description:** Method name _add_immediate_output() is described as 'historical' but still used throughout codebase

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring states: "This method name is historical - it simply forwards to _add_output(). In the Tk UI, immediate mode output goes to the main output pane."

If the name is historical and the method just forwards, it should be refactored to call _add_output() directly at call sites, or the comment should explain why the indirection is maintained.

---

#### code_vs_comment

**Description:** Docstring for _on_status_click() says it shows 'breakpoint confirmation' but implementation shows 'breakpoint info' message

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring: "Handle click on status column (show error details for ?, breakpoint confirmation for ●)."

Implementation shows:
messagebox.showinfo(
    f"Breakpoint on Line {line_num}",
    f"Line {line_num} has a breakpoint set.\n\nUse the debugger menu or commands to manage breakpoints."
)

This is informational, not a confirmation dialog. The term 'confirmation' typically implies a yes/no dialog.

---

#### documentation_inconsistency

**Description:** Class docstring describes status priority but doesn't mention that clearing an error reveals the breakpoint

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring states:
"Status priority (when both error and breakpoint):
- ? takes priority (error shown)
- After fixing error, ● becomes visible"

This implies automatic behavior, but the actual mechanism is in set_error() method which explicitly checks has_breakpoint when clearing an error. The docstring could be clearer that this is implemented behavior, not just a description of desired behavior.

---

#### code_vs_comment

**Description:** Comment in _on_cursor_move() says 'Need to schedule this after current event processing to avoid issues' but doesn't specify what issues

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment: "# Need to schedule this after current event processing to avoid issues"
Code: "self.text.after_idle(self._delete_line, self.current_line)"

The comment doesn't explain what specific issues would occur without after_idle(). This could be modifying the text widget during event processing, cursor position issues, or undo stack problems, but it's not documented.

---

#### code_vs_comment

**Description:** Comment in _redraw() mentions _parse_line_number() extraction logic but the actual parsing logic details are only in that method's docstring

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment in _redraw(): "Note: BASIC line numbers are parsed from text content (not drawn in canvas). See _parse_line_number() for the extraction logic."

The _parse_line_number() docstring only says "Extract BASIC line number from line text" without detailing the regex logic. The detailed regex explanation is only in a comment within the method itself. Cross-referencing could be clearer.

---

#### code_vs_comment

**Description:** Comment in serialize_line() mentions fallback behavior for missing source_text, but doesn't explain when source_text might be unavailable or what causes inconsistent indentation.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment says: "# Note: If source_text doesn't match pattern, falls back to relative_indent=1\n# This can cause inconsistent indentation for programmatically inserted lines"

The comment warns about inconsistent indentation but doesn't explain:
1. When would source_text be missing or not match the pattern?
2. What are 'programmatically inserted lines'?
3. Should this be considered a bug or expected behavior?

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No UI-framework dependencies' but doesn't mention that it depends on AST node types from parser module.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring says: "No UI-framework dependencies (Tk, curses, web)\nare allowed. Standard library modules (os, glob, re) and core interpreter\nmodules (runtime, parser, AST nodes) are permitted."

While it mentions 'AST nodes' are permitted, the module heavily depends on specific AST node types (LineNode, PrintStatementNode, GotoStatementNode, etc.) without importing them or documenting which node types are required. The serialize_statement() function explicitly handles many node types by string name comparison, creating a tight coupling that isn't clearly documented.

---

#### code_vs_documentation

**Description:** Module docstring says 'for all UIs (Tk, Curses, Web)' but doesn't mention CLI, while ui_helpers.py mentions CLI in its list of supported UIs.

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
variable_sorting.py: "Common variable sorting logic for all UIs (Tk, Curses, Web)."

ui_helpers.py: "This module contains UI-agnostic helper functions that can be used by\nany UI (CLI, Tk, Web, Curses)."

Inconsistent list of supported UIs between the two modules.

---

#### code_vs_comment

**Description:** cycle_sort_mode() comment says 'This matches the Tk UI implementation' but the module is supposed to be UI-agnostic common logic.

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Comment: "The cycle order is: accessed -> written -> read -> name -> (back to accessed)\n    This matches the Tk UI implementation."

If this is common logic for all UIs, it shouldn't be described as 'matching' a specific UI implementation. Either:
1. This IS the canonical implementation that all UIs should use (comment should say 'This is used by all UIs')
2. Or this is copied from Tk UI and might differ from other UIs (which would be a design inconsistency)

---

#### Code vs Comment conflict

**Description:** Comment in cmd_run() mentions 'program_ast variable' but code doesn't use such a variable

**Affected files:**
- `src/ui/visual.py`

**Details:**
Comment says: '(Runtime accesses program.line_asts directly, no need for program_ast variable)'
But there's no code that would have used a 'program_ast' variable - this appears to be a leftover comment from refactoring.

---

#### Code vs Comment conflict

**Description:** get_cursor_position() docstring says it returns dict but comment says 'not implemented'

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Docstring: 'Get current cursor position (placeholder implementation).\n\nReturns:\n    Dict with \'line\' and \'column\' keys (always returns {0, 0} - not implemented)'

The docstring contradicts itself - it says it returns a dict but also says 'not implemented'. The code does return {'line': 0, 'column': 0}, so it IS implemented as a placeholder.

---

#### Code vs Documentation inconsistency

**Description:** value property getter docstring mentions dict handling but doesn't explain why dicts would occur

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Property docstring: 'Get current editor content.\n\nAlways returns a string, even if internal value is dict or None.'

Code:
'if isinstance(self._value, dict):\n    # Sometimes event args are dict - return empty string\n    return \'\'

The comment 'Sometimes event args are dict' suggests this is a workaround for an event handling issue, but there's no documentation explaining when or why this happens.

---

#### Code vs Documentation inconsistency

**Description:** add_breakpoint docstring describes BASIC line numbers but implementation details are unclear

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
Docstring: 'Add breakpoint marker (red background) to BASIC line number.\n\nArgs:\n    line_num: BASIC line number (e.g., 10, 20, 30)'

This suggests the method expects BASIC line numbers (10, 20, 30) but the JavaScript method being called might expect 0-based editor line numbers. The relationship between BASIC line numbers and editor line positions is not documented.

---

#### Code vs Documentation inconsistency

**Description:** set_current_statement docstring describes BASIC line numbers but scroll_to_line uses 0-based line numbers

**Affected files:**
- `src/ui/web/codemirror5_editor.py`

**Details:**
set_current_statement docstring: 'Args:\n    line_num: BASIC line number, or None to clear highlighting'

scroll_to_line docstring: 'Args:\n    line: 0-based line number'

Inconsistent documentation about whether line numbers are BASIC line numbers or 0-based editor line numbers.

---

#### code_vs_comment

**Description:** Comment claims input echoing is handled by inline input handler, but code shows it's actually not echoed at all

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~70-72 comment says:
# Note: The input echoing (displaying what user typed) is handled by the
# inline input handler in the NiceGUIBackend class, not here.

But the input() method doesn't echo anything, and there's no evidence in the visible code that the backend's inline input handler echoes the input either. The comment suggests echoing happens elsewhere, but this may be outdated or incorrect.

---

#### code_vs_comment

**Description:** Comment references _enable_inline_input() method that is not visible in the provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~66-68 comment says:
# Don't print prompt here - the input_callback (backend._get_input) handles
# prompt display via _enable_inline_input() method in the NiceGUIBackend class

The _enable_inline_input() method is referenced but not shown in the provided code snippet. This could be in part 2 of the file, but the comment assumes its existence without verification.

---

#### code_internal_inconsistency

**Description:** Variables dialog sort defaults claim to match Tk UI but reference line numbers that may not be accurate

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~119-120 comment:
# Sort state (matches Tk UI defaults: see src/ui/tk_ui.py lines 91-92)
self.sort_mode = 'accessed'  # Current sort mode
self.sort_reverse = True  # Sort direction

The comment references specific line numbers in another file (tk_ui.py lines 91-92) which may become outdated as that file changes. This is a maintenance risk rather than a current inconsistency, but worth noting.

---

#### code_vs_comment

**Description:** Comment about CodeMirror scroll position restoration may be inaccurate

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~806 in FindReplaceDialog.on_close():
# Note: CodeMirror maintains its own scroll position, no need to restore

This comment assumes CodeMirror automatically maintains scroll position, but this behavior may depend on how the editor is implemented and whether it's being recreated or just hidden/shown. Without seeing the full CodeMirror integration, this assumption may be incorrect.

---

#### documentation_inconsistency

**Description:** Docstring references external documentation file that may not exist or be outdated

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1008 in NiceGUIBackend docstring:
Based on TK UI feature set (see docs/dev/TK_UI_FEATURE_AUDIT.md).

This references an external documentation file that is not provided in the source code. The file may not exist, may be outdated, or may have moved.

---

#### code_vs_comment

**Description:** Comment references line numbers that may be outdated

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1569 comment: "# The _on_editor_change method (defined at line ~2609) handles:"

This hardcoded line reference will become outdated as code changes. Should use relative references or remove specific line numbers.

---

#### code_vs_comment

**Description:** Comment about Ctrl+C handling is misleading about where the handling occurs

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1851 comment in _execute_tick: "Note on Ctrl+C handling (external to this method):
Ctrl+C interrupts are handled at the top level (in mbasic main, which wraps
start_web_ui() in a try/except)."

This comment suggests Ctrl+C is handled elsewhere, but doesn't clarify that in a web UI context, Ctrl+C in the browser doesn't send signals to the Python process the same way it does in a terminal. The comment may be misleading about the actual behavior in the web environment.

---

#### code_vs_comment

**Description:** Comment about runtime/interpreter reuse is unclear about what state is preserved

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2106 comment: "# Create new IO handler for execution (interpreter/runtime reused to preserve session state)"

This comment suggests interpreter/runtime are reused, but the code immediately calls runtime.reset_for_run() which clears variables. The comment should clarify what "session state" means (breakpoints are preserved, but variables are not).

---

#### code_vs_comment

**Description:** Comment in _remove_blank_lines assumes cursor is at end after Enter, but acknowledges this may not be true

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment states: 'The last line is preserved even if blank, since it's likely where the cursor is after pressing Enter. This prevents removing the blank line user just created. Note: This assumes cursor is at the end, which may not always be true if user clicks elsewhere.'

The code preserves the last line unconditionally, but the comment admits the assumption may be wrong, suggesting the implementation may not handle all cases correctly.

---

#### code_vs_comment

**Description:** Comment about architecture note in _execute_immediate explains why NOT to sync editor from AST, but this seems like it should be in design docs rather than inline

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# Architecture note: We do NOT sync editor from AST after immediate commands. This preserves the one-way data flow: editor text → AST → execution. Syncing AST → editor would lose user's exact text, spacing, and comments. Some immediate commands (like RENUM) modify the AST directly, but we rely on those commands to update the editor text themselves, not via automatic sync.'

This is important architectural information that should be documented elsewhere, not just in a code comment that could be missed during refactoring.

---

#### code_vs_comment

**Description:** Comment in _sync_program_from_editor says 'If sync fails, log but don't crash' but uses sys.stderr.write instead of the logging infrastructure

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# If sync fails, log but don't crash - we'll serialize what we have'
Code: 'sys.stderr.write(f"Warning: Failed to sync program from editor: {e}\n")'

The code uses sys.stderr.write directly instead of the log_web_error function used elsewhere in the file, which is inconsistent with the logging pattern.

---

#### code_vs_comment

**Description:** Comment claims 'all SINGLE precision' but code creates TypeInfo.SINGLE which may not match the comment's intent if TypeInfo enum values changed

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~485: '# Create default DEF type map (all SINGLE precision)'
Code: 'def_type_map[letter] = TypeInfo.SINGLE'
This is likely correct, but if TypeInfo.SINGLE was renamed or changed, the comment would be outdated.

---

#### code_vs_comment

**Description:** Comment says 'Save state periodically' but the timer callback doesn't handle the case where backend might be in an invalid state during execution

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment: '# Save state periodically'
Code: 'ui.timer(5.0, save_state_periodic)'
The save_state_periodic function catches exceptions but the comment doesn't mention this defensive behavior or potential failure modes.

---

#### documentation_inconsistency

**Description:** Inconsistent command key documentation format and completeness

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md provides detailed UI-specific shortcuts in prose and tables:
- 'Tk UI: Debug → Variables or **Ctrl+V**'
- 'Curses UI: **Ctrl+V** during execution'
- 'Web UI: Debug → Variables Window or Variables button'

editor-commands.md has a simpler table:
'| **Ctrl+V** | | Open Variables window |'

The editor-commands.md doesn't specify which UIs support which shortcuts, while debugging.md is explicit about UI differences. This could confuse users about whether Ctrl+V works in Web UI.

---

#### documentation_inconsistency

**Description:** Help system documentation references visual backend as separate from web UI, but code comments indicate they are the same

**Affected files:**
- `docs/help/README.md`
- `src/ui/web_help_launcher.py`

**Details:**
docs/help/README.md states:
'**Note:** The visual backend is part of the web UI implementation.'

This note appears at the end of the entry points list, suggesting there might have been confusion about whether 'visual' was a separate backend.

src/ui/web_help_launcher.py has:
'HELP_BASE_URL = "http://localhost/mbasic_docs"'

And the open_help_in_browser function has:
'ui_type: UI type for UI-specific help ("tk", "curses", "web", "cli")'

No mention of 'visual' as a UI type in the code, confirming the README note is correct but suggests there may have been historical confusion.

---

#### code_documentation_mismatch

**Description:** SessionState tracks find/replace state but no documentation describes find/replace feature

**Affected files:**
- `src/ui/web/session_state.py`
- `docs/help/common/debugging.md`

**Details:**
src/ui/web/session_state.py defines:
'last_find_text: str = ""'
'last_find_position: int = 0'
'last_case_sensitive: bool = False'

These fields suggest a find/replace feature, but:
- docs/help/common/editor-commands.md doesn't list find/replace commands
- docs/help/common/debugging.md doesn't mention find/replace
- No keyboard shortcuts documented for find/replace

Either the feature exists but is undocumented, or these are placeholder fields.

---

#### code_comment_conflict

**Description:** Comment says 'Legacy class kept for compatibility' but no indication of what code depends on it

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
src/ui/web_help_launcher.py line 67:
'# Legacy class kept for compatibility - new code should use direct web URL instead'
'# The help site is already built and served at http://localhost/mbasic_docs'

Then defines:
'class WebHelpLauncher_DEPRECATED:'

The comment suggests this class is deprecated and kept for compatibility, but:
1. No indication of what code still uses this class
2. No deprecation warning in the class docstring
3. The class name has _DEPRECATED suffix but no @deprecated decorator
4. No migration guide for code using the old class

This makes it unclear whether the class is actually used or can be safely removed.

---

#### documentation_inconsistency

**Description:** Compiler documentation states code generation is 'In Progress' but provides no timeline or status details

**Affected files:**
- `docs/help/common/compiler/index.md`
- `docs/help/common/compiler/optimizations.md`

**Details:**
docs/help/common/compiler/index.md:
'### Code Generation
**Status:** In Progress

Documentation for the code generation phase will be added as the compiler backend is developed.'

docs/help/common/compiler/optimizations.md:
'## Code Generation

**Status:** In Progress

Additional optimizations will be added during code generation:'

Both files indicate code generation is in progress, but:
1. No indication of what percentage is complete
2. No list of what's implemented vs planned
3. No timeline for completion
4. The optimizations.md lists planned features but doesn't indicate if any are partially implemented

This makes it unclear to users whether the compiler is usable or experimental.

---

#### documentation_inconsistency

**Description:** Examples documentation has duplicate Hello World content in different formats

**Affected files:**
- `docs/help/common/examples.md`
- `docs/help/common/examples/hello-world.md`

**Details:**
docs/help/common/examples.md includes:
'## Hello World

```
10 PRINT "Hello, World!"
20 END
```'

docs/help/common/examples/hello-world.md provides the same example but with:
- Full tutorial format
- Detailed explanations
- Variations
- Common mistakes
- Next steps

The examples.md file appears to be a quick reference index, while hello-world.md is the full tutorial. However:
1. No link from examples.md to hello-world.md
2. No indication that more detailed versions exist
3. Users might not discover the detailed tutorials

The examples.md should link to the detailed versions.

---

#### code_comment_conflict

**Description:** Version comment says 'Increment VERSION after each commit' but version is at 1.0.739 suggesting automated versioning

**Affected files:**
- `src/version.py`

**Details:**
src/version.py comment:
'Increment VERSION after each commit to track which code is running.
This appears in debug output so Claude can verify the user has latest code.'

But VERSION = "1.0.739" suggests:
1. Either 739 commits have been made (unlikely to be manual)
2. Or automated versioning is used (contradicting 'increment after each commit')
3. Or the comment is outdated and versioning strategy changed

The comment implies manual versioning but the high build number suggests automation. This should be clarified.

---

#### documentation_inconsistency

**Description:** Math functions appendix states ATN is evaluated in single precision with ~7 digits, but ATN function doc doesn't mention precision limitations

**Affected files:**
- `docs/help/common/language/appendices/math-functions.md`
- `docs/help/common/language/functions/atn.md`

**Details:**
math-functions.md states: "PI can be computed with ATN(1) * 4\n(Note: ATN is evaluated in single precision, ~7 digits)"

However, atn.md only states: "The expression X may be any numeric type, but the evaluation of ATN is always performed in single precision." without mentioning the ~7 digit precision limitation or its implications for PI calculation.

---

#### documentation_inconsistency

**Description:** EOF function documentation references 'Input past end' error but error codes document uses different wording

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`
- `docs/help/common/language/functions/eof.md`

**Details:**
eof.md states: "Use EOF to test for end-of-file while INPUTting, to avoid 'Input past end' errors."

error-codes.md lists error 62 as: "Input past end | An INPUT statement is executed after all data in the file has been read, or for an empty file."

The wording matches, but eof.md uses quotes around the error name while error-codes.md presents it as a formal error message. Minor inconsistency in presentation style.

---

#### documentation_inconsistency

**Description:** Getting started references loop examples with inconsistent path format

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/examples/loops.md`

**Details:**
getting-started.md 'Next Steps' section links to:
- [Loop Examples](examples/loops.md)

But also links to:
- [Hello World Example](examples/hello-world.md)

The hello-world.md file is not provided in the documentation set, suggesting either a missing file or an incorrect reference. This creates an inconsistency where one example file exists (loops.md) but another referenced example (hello-world.md) is missing.

---

#### documentation_inconsistency

**Description:** FIX documentation references INT but INT documentation is not provided to show the comparison

**Affected files:**
- `docs/help/common/language/functions/fix.md`
- `docs/help/common/language/functions/int.md`

**Details:**
fix.md states: "The major difference between FIX and INT is that FIX does not return the next lower number for negative X."

And shows: "FIX(X) is equivalent to SGN(X)*INT(ABS(X))"

However, the int.md file is referenced in multiple 'See Also' sections but is not provided in the documentation set. This makes it impossible for users to understand the full comparison between FIX and INT that the FIX documentation promises.

---

#### documentation_inconsistency

**Description:** Index page lists STRING$ function but the actual function documentation file is named string_dollar.md, not string.md

**Affected files:**
- `docs/help/common/language/functions/index.md`

**Details:**
In index.md, the link is [STRING$](string_dollar.md) which is correct, but this is just noting the naming convention is consistent.

---

#### documentation_inconsistency

**Description:** See Also sections contain identical lists across multiple system functions, but some references may not be equally relevant to all functions

**Affected files:**
- `docs/help/common/language/functions/fre.md`
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/inp.md`
- `docs/help/common/language/functions/peek.md`

**Details:**
FRE, INKEY$, INP, and PEEK all have identical 'See Also' lists including: HELP SET, INKEY$, INP, LIMITS, NULL, PEEK, RANDOMIZE, REM, SET, SHOW SETTINGS, TRON/TROFF, USR, VARPTR, WIDTH. This seems like copy-paste without customization for each function's specific use case.

---

#### documentation_inconsistency

**Description:** See Also sections contain identical lists across multiple string functions, appearing to be copy-pasted without customization

**Affected files:**
- `docs/help/common/language/functions/hex_dollar.md`
- `docs/help/common/language/functions/instr.md`
- `docs/help/common/language/functions/left_dollar.md`
- `docs/help/common/language/functions/len.md`
- `docs/help/common/language/functions/mid_dollar.md`
- `docs/help/common/language/functions/oct_dollar.md`
- `docs/help/common/language/functions/right_dollar.md`
- `docs/help/common/language/functions/space_dollar.md`
- `docs/help/common/language/functions/str_dollar.md`

**Details:**
Multiple string functions (HEX$, INSTR, LEFT$, LEN, MID$, OCT$, RIGHT$, SPACE$, STR$) all have identical 'See Also' lists including: ASC, CHR$, HEX$, INSTR, LEFT$, LEN, MID$, MID$ Assignment, OCT$, RIGHT$, SPACE$, SPC, STR$, STRING$, VAL. While comprehensive, this doesn't highlight the most relevant related functions for each specific function.

---

#### documentation_inconsistency

**Description:** See Also sections contain identical lists across multiple mathematical functions

**Affected files:**
- `docs/help/common/language/functions/int.md`
- `docs/help/common/language/functions/log.md`
- `docs/help/common/language/functions/rnd.md`
- `docs/help/common/language/functions/sgn.md`
- `docs/help/common/language/functions/sin.md`
- `docs/help/common/language/functions/sqr.md`

**Details:**
Multiple mathematical functions (INT, LOG, RND, SGN, SIN, SQR) all have identical 'See Also' lists including: ABS, ATN, COS, EXP, FIX, INT, LOG, RND, SGN, SIN, SQR, TAN. This appears to be a standard template applied to all math functions.

---

#### documentation_inconsistency

**Description:** Control-C behavior notes differ slightly between INKEY$ and INPUT$ documentation

**Affected files:**
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/input_dollar.md`

**Details:**
INKEY$ states: 'Note: Control-C behavior varied in original implementations. In MBASIC 5.21 interpreter, Control-C would terminate the program. In the BASIC Compiler, Control-C was passed through. This implementation follows compiler behavior and passes Control-C through (CHR$(3)) for program detection and handling.'

INPUT$ states: 'Note: In MBASIC 5.21 interpreter, Control-C would interrupt INPUT$ and terminate the wait. This implementation passes Control-C through (CHR$(3)) for program detection and handling, matching compiler behavior.'

Both describe similar behavior but with slightly different wording about what the original MBASIC did.

---

#### documentation_inconsistency

**Description:** Index categorizes functions but some categorizations could be debated

**Affected files:**
- `docs/help/common/language/functions/index.md`

**Details:**
SPC and TAB are listed under 'String Functions' but they are primarily formatting functions used in PRINT statements, not string manipulation functions. They might be better categorized separately or under a 'Formatting Functions' category.

---

#### documentation_inconsistency

**Description:** MKI$/MKS$/MKD$ See Also section includes unrelated functions

**Affected files:**
- `docs/help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md`

**Details:**
The See Also section includes: CLOAD, CDBL, CHR$, CSAVE, CVI/CVS/CVD, DEFINT/SNG/DBL/STR, ERR AND ERL VARIABLES, INPUT#, LINE INPUT, LPRINT AND LPRINT USING, SPACE$, TAB. Some of these (like CLOAD, CSAVE, ERR/ERL, LPRINT) seem less directly related to the MK* functions' purpose of converting numbers to strings for file storage.

---

#### documentation_inconsistency

**Description:** PEEK documentation states it returns random values but doesn't clearly state POKE is non-functional

**Affected files:**
- `docs/help/common/language/functions/peek.md`

**Details:**
PEEK documentation says 'PEEK is traditionally the complementary function to the POKE statement. However, in this implementation, PEEK returns random values and POKE is a no-op, so they are not functionally related.' This is clear, but could be more prominent as a warning since users might expect PEEK/POKE to work together.

---

#### documentation_inconsistency

**Description:** LPOS See Also section suggests alternatives but doesn't include SPACE$ or STRING$ which could be useful for manual position tracking

**Affected files:**
- `docs/help/common/language/functions/lpos.md`

**Details:**
LPOS documentation suggests using POS or tracking position manually when writing to files, but the See Also section doesn't include SPACE$ or STRING$ which would be useful for creating padding/spacing when manually tracking position.

---

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' sections - string_dollar.md references SPC as 'Prints I blanks on the terminal' but val.md references it identically, yet TAB is described differently

**Affected files:**
- `docs/help/common/language/functions/string_dollar.md`
- `docs/help/common/language/functions/val.md`

**Details:**
In string_dollar.md:
- [SPC](spc.md) - Prints I blanks on the terminal

In val.md:
- [SPC](spc.md) - Prints I blanks on the terminal

Both have identical SPC descriptions, but string_dollar.md doesn't reference TAB while val.md does. The descriptions should be consistent across all files.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting and wording across unimplemented features

**Affected files:**
- `docs/help/common/language/functions/usr.md`
- `docs/help/common/language/functions/varptr.md`
- `docs/help/common/language/statements/call.md`
- `docs/help/common/language/statements/def-usr.md`

**Details:**
usr.md uses:
'⚠️ **Not Implemented**: This feature calls machine language (assembly) routines and is not implemented in this Python-based interpreter.
**Behavior**: Always returns 0'

varptr.md uses:
'⚠️ **Not Implemented**: This feature requires direct memory access and is not implemented in this Python-based interpreter.
**Behavior**: Function is not available (runtime error when called)'

call.md uses:
'⚠️ **Not Implemented**: This feature calls machine language (assembly) subroutines and is not implemented in this Python-based interpreter.
**Behavior**: Statement is parsed but no operation is performed'

def-usr.md uses:
'⚠️ **Not Implemented**: This feature defines the starting address of assembly language subroutines and is not implemented in this Python-based interpreter.
**Behavior**: Statement is parsed but no operation is performed'

The behavior descriptions are inconsistent: USR returns 0, VARPTR throws error, CALL/DEF USR are parsed but do nothing.

---

#### documentation_inconsistency

**Description:** AUTO documentation uses inconsistent comment syntax in examples

**Affected files:**
- `docs/help/common/language/statements/auto.md`

**Details:**
In auto.md example:
```basic
AUTO 100,50    # Generates line numbers 100, 150, 200 •••
AUTO           # Generates line numbers 10, 20, 30, 40 •••
```

The example uses '#' for comments, but BASIC-80 uses REM for comments. This is inconsistent with all other documentation examples which use REM or no comments at all.

---

#### documentation_inconsistency

**Description:** DATA statement documentation example output doesn't match code spacing

**Affected files:**
- `docs/help/common/language/statements/data.md`

**Details:**
In data.md example:
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

Line 40 uses semicolons (compact spacing) but line 60 uses commas (tab spacing). The output shows different spacing but doesn't explain why or demonstrate the difference clearly.

---

#### documentation_inconsistency

**Description:** CLOAD/CSAVE documentation has inconsistent version information

**Affected files:**
- `docs/help/common/language/statements/cload.md`
- `docs/help/common/language/statements/csave.md`

**Details:**
cload.md title: 'CLOAD - THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION'
csave.md title: 'CSAVE - THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION'

But csave.md has '**Versions:** 8K (cassette), Extended (cassette)' while cload.md has no version tag.

Both should have consistent version information formatting.

---

#### documentation_inconsistency

**Description:** CLOSE documentation example doesn't demonstrate multiple file closing

**Affected files:**
- `docs/help/common/language/statements/close.md`

**Details:**
The CLOSE syntax shows:
```basic
CLOSE[[#]<file number>[,[#]<file number>...]]
```

This indicates multiple files can be closed in one statement, but the example only shows:
```basic
10 OPEN "O", 1, "OUTPUT.TXT"
20 PRINT #1, "Hello, World!"
30 CLOSE 1
```

The example should demonstrate closing multiple files to match the syntax description, e.g., 'CLOSE 1, 2, 3' or 'CLOSE' (close all).

---

#### documentation_inconsistency

**Description:** Operators documentation references non-existent data-types.md file

**Affected files:**
- `docs/help/common/language/operators.md`

**Details:**
At the end of operators.md 'See Also' section:
- [Data Types](data-types.md) - Variable types and declarations

But there is no data-types.md file in the provided documentation files. This is a broken reference.

---

#### documentation_inconsistency

**Description:** FOR...NEXT loop termination condition description is ambiguous

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
The documentation states:
'4. If variable exceeds ending value (y) considering STEP direction, loop terminates'
But then clarifies:
'- Negative STEP counts backward (loop terminates when variable < end after increment)'
'- Positive STEP counts forward (loop terminates when variable > end after increment)'

This is correct but the initial statement 'exceeds ending value' is ambiguous - it should specify that 'exceeds' means different things for positive vs negative STEP.

---

#### documentation_inconsistency

**Description:** Example 30 in DEFINT/SNG/DBL/STR has overlapping range definitions

**Affected files:**
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
Line 30 defines: 'DEFINT I-N, W-Z' which makes I,J,K,L,M,N integers.
But line 10 already defined: 'DEFDBL L-P' which makes L,M,N,O,P double precision.
This creates a conflict for L, M, N which are defined as both DEFINT and DEFDBL. The documentation doesn't explain which declaration takes precedence when ranges overlap.

---

#### documentation_inconsistency

**Description:** FIELD statement example doesn't match total bytes in comment

**Affected files:**
- `docs/help/common/language/statements/field.md`

**Details:**
Example shows:
'20 FIELD #1, 30 AS NAME$, 20 AS ADDR$, 15 AS CITY$, 2 AS STATE$, 5 AS ZIP$'
Comment breakdown:
'40 ' Positions 1-30: NAME$ (30 bytes)
50 ' Positions 31-50: ADDR$ (20 bytes)
60 ' Positions 51-65: CITY$ (15 bytes)
70 ' Positions 66-67: STATE$ (2 bytes)
80 ' Positions 68-72: ZIP$ (5 bytes)'

Total: 30+20+15+2+5 = 72 bytes, which matches. However, line 10 opens with record length 128, and the documentation should clarify that 56 bytes remain unused.

---

#### documentation_inconsistency

**Description:** INPUT statement behavior for too many values is unclear

**Affected files:**
- `docs/help/common/language/statements/input.md`

**Details:**
Documentation states: 'If too many values are entered, the extras are ignored with a ?Redo from start message'

This is contradictory - if extras are 'ignored', why does it say 'Redo from start'? The '?Redo from start' message typically means the user must re-enter ALL values, not that extras are ignored.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about .BAS extension auto-addition

**Affected files:**
- `docs/help/common/language/statements/kill.md`
- `docs/help/common/language/statements/files.md`
- `docs/help/common/language/statements/delete.md`

**Details:**
KILL.md states: '**Note**: CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files.'

FILES.md states: '**Note**: CP/M automatically adds .BAS extension if none is specified for BASIC program files.'

DELETE.md (which deletes program lines, not files) doesn't mention this.

This note about CP/M behavior appears in multiple places but is inconsistent - it's unclear if this is a CP/M OS behavior or MBASIC behavior, and whether it applies to all file operations or just specific ones.

---

#### documentation_inconsistency

**Description:** LIST statement syntax format is incomplete in Remarks section

**Affected files:**
- `docs/help/common/language/statements/list.md`

**Details:**
The Syntax section shows two formats:
'Format 1: LIST [<line number>]           (8K version)
Format 2: LIST [<line number>[-[<line number>]]]  (Extended, Disk)'

But the Remarks section is completely empty, providing no explanation of the different formats or their behavior.

---

#### documentation_inconsistency

**Description:** INPUT# statement has inconsistent title formatting

**Affected files:**
- `docs/help/common/language/statements/input_hash.md`

**Details:**
The title field shows: 'title: "INPUT# (File)"'
But other file I/O statements use different conventions:
- LINE INPUT# uses: 'title: "LINE INPUT# (File)"'
- PRINT# uses: 'title: PRINT#'

The '(File)' suffix is inconsistent across file I/O statements.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting and wording between LLIST and LPRINT

**Affected files:**
- `docs/help/common/language/statements/llist.md`
- `docs/help/common/language/statements/lprint-lprint-using.md`

**Details:**
LLIST uses:
⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.
**Behavior**: Statement is parsed but no listing is sent to a printer

LPRINT uses:
⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented in this Python-based interpreter.
**Behavior**: Statement is parsed but no output is sent to a printer

Both describe the same type of feature (line printer) but use slightly different wording ('no listing is sent' vs 'no output is sent'). Should be standardized.

---

#### documentation_inconsistency

**Description:** PUT documentation mentions PRINT# and WRITE# can be used before PUT, but this is not mentioned in LSET/RSET docs

**Affected files:**
- `docs/help/common/language/statements/lset.md`
- `docs/help/common/language/statements/put.md`

**Details:**
PUT doc states:
'**Note:** PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer before a PUT statement. In the case of WRITE#, BASIC-80 pads the buffer with spaces up to the carriage return. Any attempt to read or write past the end of the buffer causes a "Field overflow" error.'

This important information about alternative ways to populate the buffer is not mentioned in LSET or RSET documentation, which are the primary statements for preparing random file data.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting between OUT and POKE

**Affected files:**
- `docs/help/common/language/statements/out.md`
- `docs/help/common/language/statements/poke.md`

**Details:**
OUT uses:
⚠️ **Emulated as No-Op**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.
**Behavior**: Statement is parsed and executes successfully, but performs no operation

POKE uses:
⚠️ **Emulated as No-Op**: This feature requires direct memory access and cannot be implemented in a Python-based interpreter.
**Behavior**: Statement is parsed and executes successfully, but performs no operation

Both have the same implementation status but use slightly different wording ('is not implemented' vs 'cannot be implemented'). Should be standardized for consistency.

---

#### documentation_inconsistency

**Description:** PRINT# documentation references PRINT USING but the link points to lprint-lprint-using.md instead of print.md

**Affected files:**
- `docs/help/common/language/statements/print.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
In printi-printi-using.md, the 'See Also' section includes:
- [PRINT USING](print.md) - Formatted output to the screen

However, PRINT USING is documented in the same file as PRINT (print.md), not in lprint-lprint-using.md. The link is correct but the description might be confusing since PRINT USING functionality is part of the PRINT statement documentation.

---

#### documentation_inconsistency

**Description:** RANDOMIZE example output formatting is inconsistent with other documentation examples

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
The RANDOMIZE example uses unusual indentation and formatting:
'10 RANDOMIZE
             20 FOR 1=1 TO 5
             30 PRINT RND;
             40 NEXT I
             RUN'

This excessive indentation is not present in other documentation files and appears to be a formatting error. Other examples use standard left-aligned formatting.

---

#### documentation_inconsistency

**Description:** READ documentation has inconsistent tilde usage in 'See Also' section

**Affected files:**
- `docs/help/common/language/statements/read.md`

**Details:**
In read.md 'See Also' section:
'- [DATA](data.md) - To store the numeric and string constants that are accessed by the program~s READ statement(s)'

Uses '~s' instead of "'s" or 's, which appears to be a character encoding or formatting error. Should be consistent with other documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent version labeling format

**Affected files:**
- `docs/help/common/language/statements/rset.md`
- `docs/help/common/language/statements/run.md`

**Details:**
rset.md uses: '**Versions:** Disk'
run.md uses: '**Versions:** 8K, Extended, Disk'

Most other files use the format with multiple versions listed. The inconsistency is minor but should be standardized.

---

#### documentation_inconsistency

**Description:** SAVE documentation has formatting inconsistency in syntax

**Affected files:**
- `docs/help/common/language/statements/save.md`

**Details:**
Syntax shows: 'SAVE <filename> [,A][,P]'

But in Remarks it refers to options as ',A' and ',P' with commas.

The syntax should be clearer about whether the comma is part of the option or a separator. Standard BASIC syntax would be 'SAVE filename[,A][,P]' where the comma is part of the option syntax.

---

#### documentation_inconsistency

**Description:** SYSTEM documentation mentions CP/M specifically but other docs use generic 'operating system'

**Affected files:**
- `docs/help/common/language/statements/system.md`

**Details:**
system.md: 'To exit MBASIC and return control to the operating system (CP/M).'

Most other documentation uses generic 'operating system' without mentioning CP/M specifically. Should be consistent - either always mention CP/M as the historical context or always use generic terms.

---

#### documentation_inconsistency

**Description:** SWAP example has inconsistent formatting

**Affected files:**
- `docs/help/common/language/statements/swap.md`

**Details:**
The example shows:
'LIST
              10 A$=" ONE " : B$=" ALL " : C$="FOR"'

The excessive leading spaces before line numbers appear to be a formatting error from the original documentation that wasn't cleaned up. Should be:
'LIST
10 A$=" ONE " : B$=" ALL " : C$="FOR"'

---

#### documentation_inconsistency

**Description:** TRON-TROFF example has inconsistent formatting

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
Similar to SWAP, the example has excessive leading spaces:
'TRON
             Ok
             LIST
             10 K=lO'

Should be cleaned up to standard formatting without the extra spaces.

---

#### documentation_inconsistency

**Description:** CLI documentation mentions EDIT command but doesn't link to its documentation

**Affected files:**
- `docs/help/common/ui/cli/index.md`

**Details:**
cli/index.md states:
'The CLI includes a line editor accessed with the **EDIT** command:
```
Ok
EDIT 10
```
See: [EDIT Command](../../language/statements/edit.md)'

This link should be verified to exist. If EDIT is not documented, it should be added to the language reference.

---

#### documentation_inconsistency

**Description:** SAVE documentation has inconsistent keyword formatting

**Affected files:**
- `docs/help/common/language/statements/save.md`

**Details:**
In the keywords section:
'keywords: ['command', 'file', 'for', 'if', 'program', 'read', 'save', 'statement', 'string']'

Keywords like 'for', 'if', 'read' are BASIC keywords but are listed alongside generic terms like 'command', 'file', 'program'. This seems inconsistent - are these meant to be BASIC keywords or search terms? Other files have more focused keyword lists.

---

#### documentation_inconsistency

**Description:** Inconsistent emphasis on Web UI file storage limitations

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md provides detailed information about Web UI file storage: 'Files stored in Python-side memory (not browser localStorage)' and 'Files persist only during browser session - lost on page refresh'

extensions.md does not mention this critical limitation when discussing the Web UI, only stating it's a 'Browser-based IDE'.

This important limitation should be consistently mentioned when discussing the Web UI across all documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent file naming convention documentation for Web UI

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
compatibility.md states: 'Automatically uppercased by the virtual filesystem (CP/M style)' and then clarifies 'The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage'

This clarification seems oddly placed and defensive, suggesting there may have been confusion about this feature. The documentation should be clearer about whether uppercasing is a feature or implementation detail.

---

#### documentation_inconsistency

**Description:** Incomplete Web UI feature documentation

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md lists Web UI features as:
- Browser-based IDE
- Syntax highlighting
- Auto-save
- Three-panel layout
- In-memory filesystem
- Basic debugging

But does not mention critical limitations documented in compatibility.md:
- Session-only storage (lost on refresh)
- No persistent storage
- 50 file limit
- 1MB per file limit
- No path support

These limitations should be mentioned in the features list for completeness.

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

**Description:** String garbage collection document not linked from main index

**Affected files:**
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`
- `docs/help/mbasic/index.md`

**Details:**
The comprehensive string-allocation-and-garbage-collection.md document exists under Implementation Details but is only linked once in index.md. Given its depth and importance, it should potentially be featured more prominently or cross-referenced from other relevant sections like features.md or architecture.md.

---

#### documentation_inconsistency

**Description:** Placeholder document with minimal content

**Affected files:**
- `docs/help/ui/common/running.md`

**Details:**
running.md is marked as 'PLACEHOLDER - Documentation in progress' with only basic bullet points. This is referenced from multiple other documents but provides no substantial information. Status: incomplete documentation.

---

#### documentation_inconsistency

**Description:** Missing cross-reference between features and not-implemented docs

**Affected files:**
- `docs/help/mbasic/not-implemented.md`
- `docs/help/mbasic/features.md`

**Details:**
not-implemented.md lists features 'not in MBASIC 5.21' and references features.md at the end ('See Also' section), but features.md does not reference not-implemented.md. Users reading features.md might not know to check what's NOT available.

---

#### documentation_inconsistency

**Description:** Document describes historical implementation but unclear if current implementation matches

**Affected files:**
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`

**Details:**
string-allocation-and-garbage-collection.md provides 'comprehensive analysis of how string memory management worked in CP/M era Microsoft BASIC-80' and includes section 'Implementation for Modern Emulation' with requirements. However, it's not explicitly stated whether the current Python implementation follows this exact algorithm or if it's just documentation of the historical behavior for reference.

---

#### documentation_inconsistency

**Description:** Inconsistent sort mode descriptions

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
variables.md states: '**Accessed**: Most recently accessed (read or written) - default, newest first'

quick-reference.md states: '**Accessed**: Most recently accessed (read or written) - shown first'

The phrase 'default, newest first' vs 'shown first' is inconsistent. Should clarify if 'Accessed' is the default mode and what 'shown first' means.

---

#### documentation_inconsistency

**Description:** Inconsistent command for starting Tk UI

**Affected files:**
- `docs/help/ui/tk/getting-started.md`
- `docs/help/ui/tk/index.md`

**Details:**
getting-started.md states: 'mbasic --ui tk [filename.bas]

Or to use the default curses UI:
mbasic [filename.bas]'

index.md states: 'mbasic --ui tk'

The getting-started.md suggests curses is the default UI, but this should be verified and made consistent across all UI documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent search key documentation

**Affected files:**
- `docs/help/ui/curses/help-navigation.md`
- `docs/help/ui/curses/index.md`

**Details:**
help-navigation.md states: '| **/** | Open search prompt |'

index.md states: 'Press **/** to search across all help content.'

Both agree on the key, but help-navigation.md provides more detail about the search functionality that should be cross-referenced or consolidated.

---

#### documentation_inconsistency

**Description:** Tk tips.md and workflows.md reference features (Smart Insert, Variables Window, Execution Stack) that are described as planned in settings.md

**Affected files:**
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`

**Details:**
tk/tips.md extensively uses features:
'Use **Ctrl+I** (Smart Insert) to insert blank lines'
'Press **Ctrl+W** (Toggle Variables Window)'
'Press **Ctrl+K** (Toggle Stack)'

tk/workflows.md also references:
'Press **Ctrl+I** (Smart Insert) to insert blank line'
'Press **Ctrl+W** to open Variables window'

But tk/settings.md states at the top:
'**Implementation Status:** The Tk (Tkinter) desktop GUI is planned to provide the most comprehensive settings dialog. **The features described in this document represent planned/intended implementation and are not yet available.** This is a design document for future development.'

This creates confusion about whether Tk GUI features are implemented or planned.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for step commands

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/features.md`

**Details:**
debugging.md states:
'**Currently implemented:**
- **Run (Ctrl+R)** - Start program from beginning
- **Continue (Ctrl+G)** - Run to next breakpoint
- **Step Statement (Ctrl+T)** - Execute one statement
- **Step Line (Ctrl+K)** - Execute one line (all statements on line)'

But features.md under 'Execution Control' states:
'**Currently Implemented:**
- Run (Ctrl+R)
- Continue (Ctrl+G)
- Step statement (Ctrl+T)
- Step line (Ctrl+K)'

The capitalization differs ('Step Statement' vs 'Step statement'), which while minor, should be consistent across documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent feature status markers within same document

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
features.md uses inconsistent markers for implementation status:

Some sections use:
'**Currently Implemented:**'
'(Planned)'
'(Partially Implemented)'

Others use:
'**Note:** ... are planned for future releases'
'**Planned for Future Releases:**'

For example, 'Mobile Support' section uses:
'**Currently Implemented:**'
'**Partially Implemented**'
'**Planned:**'

While 'Advanced Features' uses:
'**Note:** Collaboration features ... are not currently implemented'

This inconsistency makes it harder to quickly scan what's available vs planned.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for accessing settings

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
settings.md says 'Click the ⚙️ Settings icon in the navigation bar' and 'Click menu → Settings', but web-interface.md only mentions 'Edit Menu → Settings'. The navigation bar method is not mentioned in web-interface.md.

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
Most library index pages say 'Open the file: Web/Tkinter UI: Click File → Open, select the downloaded file' but some say 'Load the file' instead of 'Open the file'. Specifically:
- business, data_management, demos, education, electronics, games, ham_radio use 'Open the file'
- telecommunications, utilities use 'Load the file'
All should use consistent terminology.

---

#### documentation_inconsistency

**Description:** Settings dialog shows 'Limits' tab as view-only but doesn't explain why or when it might become editable

**Affected files:**
- `docs/help/ui/web/settings.md`

**Details:**
The Limits Tab section states 'These limits are for information only and cannot be changed via the UI (they're set in the interpreter configuration)' and mentions '(view-only in current version)' which implies future versions might allow editing, but there's no explanation of why this limitation exists or what the roadmap is. The Future Features section doesn't mention making limits editable.

---

#### documentation_inconsistency

**Description:** File Menu mentions 'Open Example' feature as planned but doesn't appear in settings.md future features

**Affected files:**
- `docs/help/ui/web/web-interface.md`

**Details:**
web-interface.md states 'Note: An "Open Example" feature to choose from sample BASIC programs is planned for a future release.' under File Menu, but settings.md's Future Features section doesn't mention integration with example programs or any File menu enhancements.

---

#### documentation_inconsistency

**Description:** CLI debugging capabilities described inconsistently

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states: 'CLI has full debugging capabilities through commands (BREAK, STEP, WATCH, STACK), but lacks the visual debugging interface (Variables Window, clickable breakpoints, etc.) found in Curses, Tk, and Web UIs.'

However, QUICK_REFERENCE.md (for Curses) only mentions breakpoint debugging with F9/b keys and c/s/e commands at breakpoints. It doesn't mention BREAK, STEP, WATCH, or STACK commands that are supposedly available in CLI and presumably also in Curses.

---

#### documentation_inconsistency

**Description:** Duplicate installation documentation with redirect

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/INSTALLATION.md`

**Details:**
INSTALLATION.md is a redirect file that says 'This file exists for compatibility with different documentation linking conventions. All installation documentation has been consolidated in [INSTALL.md](INSTALL.md).' This creates potential confusion about which file is canonical.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
In CHOOSING_YOUR_UI.md, the Curses section mentions 'Keyboard shortcuts' as an advantage, but doesn't specify what notation is used. QUICK_REFERENCE.md uses 'Ctrl+N', 'Ctrl+L', etc., but it's unclear if this is consistent across all documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent Python command notation

**Affected files:**
- `docs/user/INSTALL.md`

**Details:**
INSTALL.md uses both 'python3' and 'python' throughout the document. While it does explain the difference in the Troubleshooting section ('python3: command not found'), it would be clearer to consistently use 'python3' in examples and note the alternative once.

---

#### documentation_inconsistency

**Description:** Inconsistent command syntax examples

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`

**Details:**
CASE_HANDLING_GUIDE.md shows commands in two different formats:
1. Without quotes: SHOW SETTINGS
2. With quotes: SET "variables.case_conflict" "error"

While this may be correct syntax, it's not explained why some commands use quotes and others don't, which could confuse users.

---

#### documentation_inconsistency

**Description:** Help access key inconsistency

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md doesn't specify the help key for Curses UI.

QUICK_REFERENCE.md shows 'Ctrl+P' as the help key in the main table, but in the Help System section it says 'Ctrl+P' and also mentions '^F' in the 'More Information' section: 'Press Ctrl+P (or ^F) within the Curses UI'.

It's unclear if both Ctrl+P and Ctrl+F work, or if this is an error.

---

#### documentation_inconsistency

**Description:** Inconsistent feature status terminology

**Affected files:**
- `docs/user/INSTALL.md`

**Details:**
INSTALL.md uses checkmarks (✓) for 'What Works' and X marks (✗) for 'What Doesn't Work', but the section title 'Feature Status' doesn't clearly indicate this is about implementation completeness vs. platform limitations. The 'What Doesn't Work' section explains these are 'hardware-specific features that cannot work in a modern environment', but this could be stated more prominently.

---

#### documentation_inconsistency

**Description:** Missing keyboard shortcut for Execution Stack window in TK_UI_QUICK_START.md

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md lists '**Ctrl+K** | Show/hide Execution Stack window' but keyboard-shortcuts.md (for Curses UI) shows an empty key binding for 'Show/hide execution stack window'. The actual key for Curses is not documented.

---

#### documentation_inconsistency

**Description:** Inconsistent boolean value format in documentation

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md shows inconsistent boolean formats. In 'Type Conversion' section it says 'Booleans: true or false (lowercase, no quotes in commands; use true/false in JSON files)' but examples show 'SET "editor.show_line_numbers" true' without clarifying if this is the command or JSON format.

---

#### documentation_inconsistency

**Description:** Inconsistent feature status markers

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md uses '⚠️' to mean 'Partially implemented or planned' but doesn't clearly distinguish between 'partially implemented' and 'planned'. For example, 'Auto-save' shows '⚠️' for Tk with note 'Tk: planned/optional' but 'Save (interactive)' shows '❌' for CLI, creating ambiguity about what ⚠️ means.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for step operations

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md uses both 'Step' and 'Stmt' to refer to stepping operations. In one place it says 'Click the **Stmt** toolbar button (step statement)' and later 'Click the **Step** toolbar button (step line)'. The relationship between these terms and whether they're different buttons is unclear.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of UI element names

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md inconsistently capitalizes 'Variables window' vs 'Variables Window' and 'Execution Stack window' vs 'Execution Stack Window' throughout the document. For example: 'Variables window (**Ctrl+W**)' vs 'Variables Window Features:'.

---


## Summary

- Total issues found: 654
- Code/Comment conflicts: 225
- Other inconsistencies: 429
