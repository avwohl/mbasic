# Enhanced Consistency Report (Code + Documentation)

Generated: 2025-11-09 15:40:41
Analyzed: Source code (.py, .json) and Documentation (.md)

## 🔧 Code vs Comment Conflicts


## 📋 General Inconsistencies

### 🔴 High Severity

#### code_vs_comment

**Description:** CHAIN docstring describes variable preservation incorrectly for MERGE mode

**Affected files:**
- `src/interactive.py`

**Details:**
The cmd_chain() docstring at line ~380 states:
'Save variables based on CHAIN options:
- MERGE: preserves all variables (overlay mode)
- ALL: passes all variables to new program
- Neither: passes only COMMON variables'

But the code at line ~410 shows:
if all_flag or merge:
    # Save all variables
    saved_variables = self.program_runtime.get_all_variables()

This means MERGE and ALL both save all variables. However, the comment at line ~408 says 'MERGE: preserves all variables (overlay mode)' which is correct, but the docstring's categorization suggests MERGE is different from ALL, when the code treats them identically for variable preservation.

---

#### code_vs_comment

**Description:** serialize_let_statement docstring claims it 'ALWAYS outputs the implicit assignment form (A=5) without the LET keyword' but this contradicts the function name and the LetStatementNode's purpose. The comment suggests the AST doesn't track whether LET was present, but this is a design decision that may not match user expectations.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring states:
'LetStatementNode represents both explicit LET statements and implicit assignments in the AST. However, this serializer ALWAYS outputs the implicit assignment form (A=5) without the LET keyword, regardless of whether the original source used LET.

This is because:
- The AST doesn\'t track whether LET was originally present
- LET is optional in MBASIC and functionally equivalent to implicit assignment
- Both forms use the same AST node type for consistency throughout the codebase'

This means source code with 'LET A=5' will be serialized as 'A=5', losing the original syntax. This is a significant behavior that should be verified as intentional.

---

#### code_vs_comment

**Description:** emit_keyword docstring requires lowercase input but apply_keyword_case_policy docstring says it accepts any case. These two functions have conflicting requirements.

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword docstring:
'Args:
    keyword: The keyword to emit (must be normalized lowercase by caller, e.g., "print", "for")'

And:
'Note: This function requires lowercase input because it looks up the display case from the keyword case manager using the normalized form.'

But apply_keyword_case_policy docstring:
'Args:
    keyword: The keyword to transform (may be any case)'

If emit_keyword calls apply_keyword_case_policy (or vice versa), there's a contract mismatch.

---

#### Code vs Documentation inconsistency

**Description:** Settings widget keybindings not documented in curses keybindings JSON

**Affected files:**
- `src/ui/curses_settings_widget.py`
- `src/ui/curses_keybindings.json`

**Details:**
curses_settings_widget.py implements these keybindings:
- ESC or SETTINGS_KEY: Cancel
- ENTER_KEY: OK
- SETTINGS_APPLY_KEY: Apply
- SETTINGS_RESET_KEY: Reset

The footer displays: "↑↓ {ENTER_KEY}=OK {ESC_KEY}/{SETTINGS_KEY}=Cancel {SETTINGS_APPLY_KEY}=Apply {SETTINGS_RESET_KEY}=Reset"

However, curses_keybindings.json only has one settings-related entry:
"show_settings": {"keys": ["SHOW SETTINGS"], "primary": "SHOW SETTINGS", "description": "View all settings or filter by pattern (e.g., SHOW SETTINGS \"auto\")"}

This is actually in cli_keybindings.json, not curses_keybindings.json. The curses keybindings file has no settings-related entries at all, despite the settings widget being part of the curses UI.

---

#### code_vs_comment

**Description:** Critical comment in _continue_smart_insert explains lost context but doesn't match actual implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _on_insert_line_renumber_response() at line ~1050:
# Continue with insert line after dialog
# Note: We can't continue the insert here because we've lost the context
# (lines, line_index, insert_num variables). User will need to retry insert.

This comment suggests the operation cannot complete, but then _continue_smart_insert() method exists (line ~1056) which takes exactly those parameters (insert_num, line_index, lines). The comment is either outdated (from before _continue_smart_insert was extracted) or incorrect about the limitation.

---

#### code_vs_comment

**Description:** Comment about status bar behavior contradicts multiple code paths

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple functions have comments like:
'# Status bar stays at default - error is displayed in output'
'# No status bar update - status bar stays at default'
'# Status bar stays at default (STATUS_BAR_SHORTCUTS) - error is in output'

But in _run_program() there's:
'# No status bar update - program output will show in output window'

And in _execute_tick() when program completes:
'self._update_status_with_errors("Ready")'

The comments claim 'no status bar update' or 'stays at default', but _update_status_with_errors() is explicitly called, which updates the status bar. This is contradictory.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC when execution is running, but code resets PC to halted when paused_at_breakpoint is True

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sync_program_to_runtime method:
Docstring says: "Sync program to runtime without resetting PC.

Updates runtime's statement_table and line_text_map from self.program,
but preserves current PC/execution state."

But code does:
"if self.running and not self.paused_at_breakpoint:
    # Execution is running - preserve execution state
    self.runtime.pc = old_pc
    self.runtime.halted = old_halted
else:
    # No execution in progress or paused at breakpoint - ensure halted
    self.runtime.pc = PC.halted_pc()
    self.runtime.halted = True"

The docstring claims it preserves PC, but when paused_at_breakpoint=True, it explicitly resets PC to halted. The inline comment explains this is intentional to prevent accidental resumption, but the docstring is misleading.

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

1. keybinding_loader.py: Loads from JSON files (e.g., curses_keybindings.json)
   - Used for: Runtime event handling
   - Comment: "This loads keybindings for runtime event handling (binding keys to actions)"

2. help_macros.py: Loads same JSON files via _load_keybindings()
   - Used for: Macro expansion in help content ({{kbd:action}})
   - Comment: "This loads the same keybinding JSON files as keybinding_loader.py, but for a different purpose: macro expansion in help content"

3. interactive_menu.py: Imports keybindings module with constants
   - Used for: Menu display
   - Code: from . import keybindings as kb
   - Uses: kb.NEW_KEY, kb.OPEN_KEY, etc.

4. help_widget.py: Hardcoded keys in keypress() method
   - Used for: Help navigation
   - Comment: "Help navigation keys are HARDCODED (not loaded from keybindings JSON)"

This creates confusion about:
- Which system is authoritative
- Whether keybindings.py (constants) is deprecated or still in use
- Why help_widget.py doesn't use the JSON system
- How these systems interact or conflict

---

#### code_vs_comment

**Description:** Comment in _execute_immediate() claims to avoid calling interpreter.start() to preserve PC, but then manually replicates part of start()'s initialization, creating maintenance risk

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment block starting at line ~1180:
"NOTE: Don't call interpreter.start() because it calls runtime.setup() which resets PC to the first statement. The RUN command has already set PC to the correct line (e.g., RUN 120 sets PC to line 120). We only need to clear the halted flag and mark this as first line. This avoids the full initialization that start() does:
  - runtime.setup() (rebuilds tables, resets PC)
  - Creates new InterpreterState
  - Sets up Ctrl+C handler"

Then code does:
self.runtime.halted = False
self.interpreter.state.is_first_line = True

This creates a maintenance issue: if interpreter.start() changes its initialization logic, this code won't be updated. The comment documents WHY start() isn't called, but the manual replication of partial initialization is fragile. If start() adds new required initialization steps, this code path will miss them.

---

#### documentation_inconsistency

**Description:** Help system documentation contradicts implementation - README says web UI help may be served externally, but web_help_launcher.py shows help is served at http://localhost/mbasic_docs

**Affected files:**
- `docs/help/README.md`
- `src/ui/web_help_launcher.py`

**Details:**
README.md states: 'Web UI help may be served externally rather than through the built-in help system.'

But web_help_launcher.py shows:
HELP_BASE_URL = "http://localhost/mbasic_docs"

The code clearly expects help to be served at a specific local URL, not 'externally'. The documentation should clarify that web help is served locally at /mbasic_docs, not externally.

---

#### documentation_inconsistency

**Description:** LINE INPUT# documentation has incorrect filename and title

**Affected files:**
- `docs/help/common/language/statements/inputi.md`
- `docs/help/common/language/statements/line-input.md`

**Details:**
File inputi.md has:
- title: "LINE INPUT# (File)"
- syntax: LINE INPUT#<file number>,<string variable>

But the filename is 'inputi.md' which suggests INPUT# not LINE INPUT#. The 'See Also' section in line-input.md references it as 'inputi.md' for LINE INPUT#, but inputi.md should be for INPUT# based on naming convention. The content describes LINE INPUT# but the filename doesn't match.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting and detail level for unimplemented features.

**Affected files:**
- `docs/help/common/language/statements/width.md`
- `docs/help/common/language/statements/wait.md`

**Details:**
WIDTH.md has detailed implementation note:
"⚠️ **Emulated as No-Op**: This statement is parsed for compatibility but performs no operation.
**Behavior**: The simple "WIDTH <number>" statement parses and executes successfully without errors...
**Why**: Terminal and UI width is controlled by the operating system...
**Limitations**: The "WIDTH LPRINT" syntax is NOT supported..."

WAIT.md has simpler note:
"⚠️ **Not Implemented**: This feature requires direct hardware I/O port access and is not implemented in this Python-based interpreter.
**Behavior**: Statement is parsed but no operation is performed
**Why**: Cannot access hardware I/O ports..."

Both are unimplemented but have different levels of detail and structure. Should be consistent.

---

#### documentation_inconsistency

**Description:** Broken internal documentation links

**Affected files:**
- `docs/help/index.md`
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/ui/tk/index.md`

**Details:**
Multiple docs reference links that may not exist:
- CLI: '[EDIT Command](../../language/statements/edit.md)'
- CLI: '[AUTO Command](../../language/statements/auto.md)'
- Curses: '[RENUM Command](../../language/statements/renum.md)'
- Curses: '[AUTO Command](../../language/statements/auto.md)'
- Curses: '[DELETE Command](../../language/statements/delete.md)'
- Curses: '[Running Programs](../../../ui/curses/running.md)'
- Tk: '[Examples](../../examples/hello-world.md)'
- Index: '[Hello World](common/examples/hello-world.md)'
- Index: '[Loops and Control Flow](common/examples/loops.md)'
These links should be verified to exist at the referenced paths.

---

#### documentation_inconsistency

**Description:** Find/Replace feature availability contradiction

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/find-replace.md`

**Details:**
features.md under 'Tkinter GUI' section states: 'Find and Replace - Search and replace text ({{kbd:find:tk}}/{{kbd:replace:tk}})'

cli/find-replace.md states: 'The CLI backend does not have built-in Find/Replace commands' and recommends: 'For built-in Find/Replace, use the Tk UI'

This is consistent for CLI not having it and Tk having it. However, features.md doesn't mention whether Curses UI or Web UI have Find/Replace, creating an incomplete picture.

---

#### documentation_inconsistency

**Description:** Contradictory information about variable inspection methods between Curses and CLI UIs

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/cli/variables.md`

**Details:**
docs/help/ui/curses/variables.md states: 'The Curses UI provides a visual variable inspector window for viewing and managing variables during program execution and debugging.' with keyboard shortcut {{kbd:toggle_variables:curses}}.

However, docs/help/ui/cli/variables.md states: 'The CLI uses the PRINT statement for variable inspection during debugging' and explicitly says 'The CLI does not have a Variables Window feature.'

But then docs/help/ui/cli/variables.md also says: 'For visual variable inspection, use: - **Curses UI** - Full-screen terminal with Variables Window ({{kbd:toggle_variables:curses}})'

This creates confusion about whether the Variables Window is a Curses-only feature or available in CLI mode.

---

#### documentation_inconsistency

**Description:** Typo in keyboard shortcut for Clear All Breakpoints

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`

**Details:**
feature-reference.md shows:
'Clear All Breakpoints ({{kbd:file_save:tk}}hift+B)'

This appears to be a typo - should likely be '{{kbd:file_save:tk}}+Shift+B' or 'Shift+B' alone. The 'hift' fragment suggests a copy-paste error where 'S' was replaced with the kbd macro.

---

#### documentation_inconsistency

**Description:** Stop/Interrupt shortcut conflicts with Cut operation

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`

**Details:**
feature-reference.md states:
'Stop/Interrupt ({{kbd:cut:tk}}): Stop a running program immediately.'

But also states:
'Cut/Copy/Paste ({{kbd:cut:tk}}/C/V): Standard clipboard operations'

The same shortcut {{kbd:cut:tk}} is assigned to both Stop Program and Cut text. This is a serious conflict.

---

#### documentation_inconsistency

**Description:** Contradictory information about function key shortcuts

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md states:
'**Currently implemented:**
- Run ({{kbd:run:web}}) - Start program from beginning
- Continue ({{kbd:continue:web}}) - Run to next breakpoint
- Step Statement ({{kbd:step:web}}) - Execute one statement
- Step Line ({{kbd:step_line:web}}) - Execute one line
- Stop ({{kbd:stop:web}}) - End execution

**Note:** Function key shortcuts ({{kbd:continue:web}}, {{kbd:step:web}}, {{kbd:help:web}}1, etc.) are not implemented in the Web UI.'

But then in 'Keyboard Shortcuts' section it lists:
'**Currently Implemented:**
- {{kbd:run:web}} - Run program
- {{kbd:continue:web}} - Continue
- {{kbd:step:web}} - Step statement
- {{kbd:step_line:web}} - Step line
- {{kbd:stop:web}} - Stop execution'

And in 'Planned for Future Releases' it lists:
'- {{kbd:continue:web}} - Start/Continue debugging
- {{kbd:toggle_breakpoint:web}} - Toggle breakpoint
- {{kbd:step:web}} - Step over
- {{kbd:help:web}}1 - Step into'

This creates confusion about which shortcuts are implemented, which are function keys, and which are planned.

---

#### documentation_inconsistency

**Description:** Contradictory information about toolbar buttons and their functions

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md under 'Interface Overview > 2. Toolbar' lists these buttons:
'New, Open, Save, Save As, Run, Stop, Step Line, Step Stmt, Continue'.

However, web-interface.md under 'Main Components' only mentions:
'Program Editor (Top), Output (Middle), Command (Bottom), Menu Bar'.

There's no mention of a toolbar in web-interface.md at all. This is a significant structural difference in the UI description.

---

### 🟡 Medium Severity

#### Code vs Comment conflict

**Description:** InputStatementNode suppress_question documentation may not match actual behavior

**Affected files:**
- `src/ast_nodes.py`

**Details:**
InputStatementNode lines 211-220:
'Note: The suppress_question field controls "?" display:
- suppress_question=False (default): Adds "?" after prompt
  Examples: INPUT var → "? ", INPUT "Name", var → "Name? ", INPUT "Name"; var → "Name? "
- suppress_question=True: No "?" added, no prompt displayed
  Examples: INPUT; var → "" (no prompt, no "?")

Semicolon usage:
- INPUT; var → semicolon immediately after INPUT (suppress_question=True, no "?")
- INPUT "prompt"; var → semicolon after prompt is just separator (suppress_question=False, shows "?")'

The documentation states that when suppress_question=True, 'no prompt displayed', but the prompt field is Optional[ExpressionNode] and could theoretically be set even when suppress_question=True. The documentation doesn't clarify if this is a validation error or if the prompt is simply ignored.

---

#### code_vs_comment_conflict

**Description:** Comment claims trailing_minus_only adds 1 char total, but code adds 1 char to content_width regardless of sign value

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 232 comment: 'trailing_minus_only: - at end, adds - for negative OR space for non-negative (1 char total)'
Line 327-328 code: 'if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
    content_width += 1'
The comment says trailing_minus_only adds 1 char total (implying it's conditional), but the code unconditionally adds 1 to content_width for trailing_minus_only, same as trailing_sign. The behavior is actually correct (always reserves space), but the comment's phrasing '(1 char total)' vs '(2 chars total)' for trailing_sign is misleading.

---

#### code_vs_comment_conflict

**Description:** EOF function comment describes mode 'I' as binary input but doesn't clarify relationship to OPEN statement syntax

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 717-723 comment: 'Note: For binary input files (mode 'I' from OPEN statement), respects ^Z (ASCII 26)
as EOF marker (CP/M style). In MBASIC syntax, mode 'I' stands for "Input" but is
specifically BINARY INPUT mode, implemented as 'rb' by execute_open() in interpreter.py.
This binary mode allows ^Z detection for CP/M compatibility. Text mode files (output,
append) use standard Python EOF detection without ^Z checking.'
Line 738-741 code: 'if file_info['mode'] == 'I':'
The comment explains mode 'I' is binary input opened as 'rb', but the code checks file_info['mode'] == 'I' which suggests the mode is stored as 'I' not 'rb'. This creates confusion about whether 'I' is the BASIC syntax mode or the Python file mode. The comment references execute_open() in interpreter.py but that file is not provided for verification.

---

#### code_vs_comment_conflict

**Description:** Comment claims identifier_table infrastructure exists but is not used, contradicting the implementation

**Affected files:**
- `src/case_string_handler.py`

**Details:**
Lines 54-61 comment: 'Note: We return original_text directly. An identifier_table infrastructure
exists (see get_identifier_table) but is not currently used for identifiers,
as they always preserve their original case without policy enforcement.'
Lines 28-31 code: '@classmethod
def get_identifier_table(cls, policy: str = "force_lower") -> CaseKeeperTable:
    """Get or create the identifier case keeper table."""
    if cls._identifier_table is None:
        cls._identifier_table = CaseKeeperTable(policy=policy)'
The comment says the identifier_table is 'not currently used', but the code implements a full get_identifier_table method that creates and returns a table. If it's truly unused, this is dead code. If it's used elsewhere, the comment is wrong.

---

#### Code vs Documentation inconsistency

**Description:** load_from_file() uses Python's open() directly instead of FileIO abstraction

**Affected files:**
- `src/editing/manager.py`

**Details:**
The manager.py docstring says:
"FILE I/O ARCHITECTURE:
This manager provides direct Python file I/O methods (load_from_file, save_to_file) for local UIs (CLI, Curses, Tk) to load/save .BAS program files via UI menus/dialogs. This is separate from the two filesystem abstractions"

And later:
"Why ProgramManager has its own file I/O methods:
- Provides simpler API for local UI menu operations (File > Open/Save dialogs)
- Only used by local UIs (CLI, Curses, Tk) where filesystem access is safe"

But the implementation of load_from_file() uses:
with open(filename, 'r') as f:

This directly accesses the filesystem, which contradicts the file_io.py documentation that says FileIO.load_file() should be used for loading program files. The architecture documentation is inconsistent about when to use FileIO vs direct file access.

---

#### code_vs_comment

**Description:** CONT docstring claims editing clears execution state, but doesn't mention this applies to all edit operations

**Affected files:**
- `src/interactive.py`

**Details:**
The cmd_cont() docstring at line ~200 states:
'IMPORTANT: CONT will fail with "?Can't continue" if the program has been edited (lines added, deleted, or renumbered) because editing clears the GOSUB/RETURN and FOR/NEXT stacks to prevent crashes from invalidated return addresses and loop contexts. See clear_execution_state() for details.'

However, clear_execution_state() is called in multiple places:
1. process_line() when adding/deleting lines (line ~150, ~157)
2. cmd_renum() after renumbering (implied by docstring)

But the EDIT command (cmd_edit) at line ~860 updates the statement_table but does NOT call clear_execution_state(). This is inconsistent - editing a line should also invalidate GOSUB/FOR stacks, but doesn't.

---

#### code_vs_comment

**Description:** Comment about readline Ctrl+A binding conflicts with actual edit mode trigger

**Affected files:**
- `src/interactive.py`

**Details:**
At line ~90, the _setup_readline() method has this comment:
'# Bind Ctrl+A to insert the character instead of moving cursor to beginning-of-line
# This overrides default Ctrl+A (beginning-of-line) behavior.
# When user presses Ctrl+A, the terminal sends ASCII 0x01, and 'self-insert'
# tells readline to insert it as-is instead of interpreting it as a command.
# The \x01 character in the input string triggers edit mode (see start() method)'

But in start() at line ~110, the code checks:
if line and line[0] == '\x01':
    # Ctrl+A pressed - enter edit mode

This creates a contradiction: the readline binding makes Ctrl+A insert the character (so it appears in the input string), but then the start() method interprets that inserted character as a command. This works, but the comment makes it sound like readline is being bypassed, when actually readline is being configured to pass the character through.

---

#### code_vs_comment

**Description:** Comment about NEXT processing order conflicts with implementation details

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 1088-1095 says:
"NEXT I, J, K processes variables left-to-right: I first, then J, then K.
For each variable, _execute_next_single() is called to increment it and check if
the loop should continue. If _execute_next_single() returns True (loop continues),
execution jumps back to the FOR body and remaining variables are not processed.
If it returns False (loop finished), that loop is popped and the next variable is processed.

This differs from separate statements (NEXT I: NEXT J: NEXT K) which would
always execute sequentially, processing all three NEXT statements."

But the code at lines 1110-1117 shows:
```python
for var_node in var_list:
    var_name = var_node.name + (var_node.type_suffix or "")
    should_continue = self._execute_next_single(var_name, var_node=var_node)
    if should_continue:
        return
```

The comment says _execute_next_single() returns True if loop continues, but looking at the method signature at line 1119, there's no clear indication of what it returns. The method needs to be checked to verify this behavior matches the comment.

---

#### code_vs_comment

**Description:** INPUT statement comment describes state machine but doesn't mention file input bypass

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1240 states:
# State machine for keyboard input (file input is synchronous):
# 1. If state.input_buffer has data: Use buffered input (from provide_input())
# 2. Otherwise: Set state.input_prompt, input_variables, input_file_number and return (pauses execution)
# 3. UI calls provide_input() with user's input line
# 4. On next tick(), buffered input is used (step 1) and input_prompt/input_variables are cleared
#
# File input bypasses the state machine and reads synchronously.

The comment correctly describes the behavior, but the code structure doesn't clearly separate the file input path from the keyboard input path until later in the function. The comment at the top suggests file input is a special case that bypasses the state machine, but the code checks 'if stmt.file_number is not None' first, then handles file input, then handles keyboard input. This is correct but the comment could be clearer that the entire state machine description only applies to keyboard input (when file_number is None).

---

#### Code vs Documentation inconsistency

**Description:** Module docstring references SimpleKeywordCase in src/simple_keyword_case.py but this file is not provided in the source code files

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
Docstring says: "For simpler force-based policies in the lexer, see SimpleKeywordCase (src/simple_keyword_case.py) which only supports force_lower, force_upper, and force_capitalize."

The file src/simple_keyword_case.py is not included in the provided source code files, making this reference unverifiable and potentially broken.

---

#### documentation_inconsistency

**Description:** apply_keyword_case_policy function has inconsistent documentation about input requirements. The docstring says 'may be any case' but the Note says 'callers should pass lowercase keywords for consistency'.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Function docstring:
'Args:
    keyword: The keyword to transform (may be any case)'

But the Note says:
'Note: While this function can handle keywords in any case, callers should pass lowercase keywords for consistency (emit_keyword() requires lowercase). The first_wins policy normalizes to lowercase for lookup. Other policies transform based on input case.'

This creates ambiguity about the contract - can callers pass any case or should they normalize first?

---

#### code_vs_comment

**Description:** serialize_rem_statement uses stmt.comment_type but the logic suggests it should be uppercase ('APOSTROPHE', 'REM', 'REMARK') while emit_keyword expects lowercase. There's a case mismatch in the flow.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Code:
'if stmt.comment_type == "APOSTROPHE":
    result = self.emit_token("\'", stmt.column, "RemKeyword")
else:
    # Apply keyword case to REM/REMARK
    result = self.emit_keyword(stmt.comment_type.lower(), stmt.column, "RemKeyword")'

The comparison uses uppercase 'APOSTROPHE' but then calls .lower() for emit_keyword. This suggests comment_type is stored in uppercase, but it's not documented whether this is consistent across the codebase.

---

#### code_vs_comment

**Description:** PositionSerializer.__init__ accepts keyword_case_manager parameter but the docstring describes it as 'KeywordCaseManager instance (from parser) with keyword case table' without explaining what happens if it's None (which is the default).

**Affected files:**
- `src/position_serializer.py`

**Details:**
Code:
'def __init__(self, debug=False, keyword_case_manager=None):
    ...
    # Store reference to keyword case manager from parser
    self.keyword_case_manager = keyword_case_manager'

And in emit_keyword:
'if self.keyword_case_manager:
    keyword_with_case = self.keyword_case_manager.get_display_case(keyword)
else:
    # Fallback if no manager (shouldn\'t happen)
    keyword_with_case = keyword.lower()'

The comment says 'shouldn\'t happen' but None is the default value, suggesting this is expected to happen in some contexts.

---

#### code_vs_comment_conflict

**Description:** Comment in check_array_allocation() claims to account for MBASIC array sizing convention, but the actual array creation is delegated to execute_dim() in interpreter.py. The comment suggests this function handles the convention, but it only uses it for limit checking.

**Affected files:**
- `src/resource_limits.py`

**Details:**
Comment says: 'This calculation accounts for the MBASIC array sizing convention for limit checking. The actual array creation/initialization is done by execute_dim() in interpreter.py.'

The comment is somewhat misleading because it first says 'accounts for' which could imply full handling, then clarifies it's only for limit checking. The code does: total_elements *= (dim_size + 1)  # +1 for 0-based indexing (0 to N)

This is correct for limit checking but the comment could be clearer about the division of responsibility.

---

#### code_vs_documentation_inconsistency

**Description:** create_unlimited_limits() has inconsistent string length limit compared to other presets

**Affected files:**
- `src/resource_limits.py`

**Details:**
create_web_limits() and create_local_limits() both use:
max_string_length=255,  # 255 bytes (MBASIC 5.21 compatibility)

But create_unlimited_limits() uses:
max_string_length=1024*1024,  # 1MB strings (for testing/development - not MBASIC compatible)

The comment acknowledges it's not MBASIC compatible, but this creates an inconsistency where 'unlimited' limits actually break MBASIC compatibility. This could cause tests to pass with unlimited limits but fail with realistic limits. The function name 'create_unlimited_limits' suggests it's for testing MBASIC programs without constraints, but it actually changes behavior.

---

#### code_vs_comment

**Description:** Module docstring claims SimpleKeywordCase is used by lexer but doesn't document the relationship with KeywordCaseManager

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
Module docstring states:
'This is a simplified keyword case handler used by the lexer (src/lexer.py). It supports only three force-based policies...'

And:
'For advanced policies (first_wins, preserve, error) via CaseKeeperTable, see KeywordCaseManager (src/keyword_case_manager.py) which is used by src/parser.py and src/position_serializer.py.'

However, the docstring doesn't explain:
1. Why two separate case handling systems exist
2. How they interact or coordinate
3. What happens if settings change between lexer and parser phases
4. Whether they share any state

This creates confusion about the architecture.

---

#### documentation_inconsistency

**Description:** SettingScope.FILE is defined and partially implemented but no FILE-scoped settings exist in definitions

**Affected files:**
- `src/settings.py`
- `src/settings_definitions.py`

**Details:**
In settings.py:
- SettingScope.FILE is imported and used
- file_settings dict exists and is checked in get()
- set() method supports SettingScope.FILE
- reset_to_defaults() supports SettingScope.FILE

In settings_definitions.py:
- SettingScope.FILE is defined in the enum
- No settings in SETTING_DEFINITIONS use scope=SettingScope.FILE
- No documentation explains what FILE scope would be used for

The class docstring in SettingsManager mentions FILE scope is 'reserved for future use' but this isn't documented in settings_definitions.py where developers would look to add new settings.

---

#### code_vs_comment

**Description:** create_settings_backend() docstring says session_id is 'required if NICEGUI_REDIS_URL is set' but code falls back to FileSettingsBackend

**Affected files:**
- `src/settings_backend.py`

**Details:**
Function docstring:
'session_id: Session ID for Redis mode (required if NICEGUI_REDIS_URL is set)'

But the implementation:
if redis_url and session_id:
    # Create Redis backend
else:
    # File mode: traditional filesystem storage
    return FileSettingsBackend(project_dir)

If redis_url is set but session_id is None, it silently falls back to file mode. The docstring should say 'required for Redis mode' not 'required if NICEGUI_REDIS_URL is set', or the code should raise an error when redis_url is set but session_id is missing.

---

#### Code vs Documentation inconsistency

**Description:** Readline keybindings documented in code but not in JSON configuration

**Affected files:**
- `src/ui/cli.py`
- `src/ui/cli_keybindings.json`

**Details:**
cli.py contains get_additional_keybindings() function that returns readline keybindings:

"These are readline keybindings that are handled by Python's readline module, not by the keybinding system. They're documented here for completeness."

Returns keybindings like Ctrl+E, Ctrl+K, Ctrl+U, Ctrl+W, Ctrl+T, Up/Down arrows, etc.

However, cli_keybindings.json does not include these keybindings. The function comment says they're "documented here for completeness" but they're not in the official keybindings documentation file.

Note: Ctrl+A is mentioned as "overridden by MBASIC to trigger edit mode" in the code comment, and it does appear in cli_keybindings.json as the edit command.

---

#### Documentation inconsistency

**Description:** Inconsistent key naming conventions in keybindings

**Affected files:**
- `src/ui/curses_keybindings.json`

**Details:**
curses_keybindings.json uses inconsistent arrow key notation:

In help_browser section:
- "scroll_up": {"keys": ["↑", "k"]}
- "scroll_down": {"keys": ["↓", "j"]}

But in curses_settings_widget.py footer:
- "↑↓ {key_to_display(ENTER_KEY)}=OK"

The JSON uses Unicode arrow symbols (↑, ↓) while other parts of the codebase might use "Up Arrow", "Down Arrow" (as seen in cli.py get_additional_keybindings()).

This inconsistency in notation could cause confusion when cross-referencing keybindings.

---

#### Code vs Documentation inconsistency

**Description:** BREAK command clear syntax not documented in keybindings

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/cli_keybindings.json`

**Details:**
cli_debug.py cmd_break() docstring shows:
"Usage:
    BREAK           - List all breakpoints
    BREAK 100       - Set breakpoint at line 100
    BREAK 100-      - Clear breakpoint at line 100
    BREAK CLEAR     - Clear all breakpoints"

cli_keybindings.json only shows:
"toggle_breakpoint": {"keys": ["BREAK line"], "primary": "BREAK line", "description": "Set breakpoint at line"}

The keybindings file doesn't document the listing, clearing, or clear-all functionality of the BREAK command.

---

#### Code vs Documentation inconsistency

**Description:** STEP command with count argument not documented in keybindings

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/cli_keybindings.json`

**Details:**
cli_debug.py cmd_step() docstring shows:
"Usage:
    STEP        - Execute next statement and pause
    STEP n      - Execute n statements"

cli_keybindings.json only shows:
"step": {"keys": ["STEP"], "primary": "STEP", "description": "Step to next statement"}

The keybindings file doesn't document that STEP can take a numeric argument to execute multiple statements.

---

#### code_vs_comment

**Description:** Comment claims bare identifiers are rejected, but code allows them in some cases

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _check_line_syntax() method:
Comment: "Reject bare identifiers (the parser treats them as implicit REMs for
old BASIC compatibility, but in the editor we want to be stricter)"

Code checks:
if (first_token.type == TokenType.IDENTIFIER and
    second_token.type in (TokenType.EOF, TokenType.COLON)):
    return (False, f"Invalid statement: '{first_token.value}' is not a BASIC keyword")

However, this only rejects bare identifiers followed by EOF or COLON. A bare identifier followed by other tokens (like operators or parentheses) would pass this check and potentially be treated as an implicit REM by the parser.

---

#### code_vs_comment

**Description:** Comment about pasted lines starting with digits conflicts with BASIC expression syntax

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_numbers() method:
"# In this context, we assume lines starting with digits are numbered program lines (e.g., '10 PRINT').
# Note: While BASIC statements can start with digits (numeric expressions), when pasting
# program code, lines starting with digits are conventionally numbered program lines."

The code treats ANY line starting with a digit as a numbered program line:
if line[0].isdigit():
    # Raw pasted line like '10 PRINT' - reformat it

This creates ambiguity: if a user pastes a line like '123 + 456' (a numeric expression), it would be incorrectly reformatted as line number 123 with code '+ 456'. The comment acknowledges this issue but the code doesn't handle it.

---

#### code_vs_comment

**Description:** Comment about IO Handler lifecycle contradicts actual implementation pattern

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at lines ~145-155 says:
# IO Handler Lifecycle:
# 1. self.io_handler (CapturingIOHandler) - Used for RUN program execution
#    Created ONCE here, reused throughout session (NOT recreated in start())
# 2. immediate_io (OutputCapturingIOHandler) - Used for immediate mode commands
#    Created here temporarily, then RECREATED in start() with fresh instance each time

However, in start() method (line ~220), the code creates:
immediate_io = OutputCapturingIOHandler()
self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)

This recreates the executor but the comment emphasizes the IO handler recreation. The pattern is actually 'executor recreation with new IO handler' not just 'IO handler recreation'.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of status bar behavior across methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple methods have comments like:
# (No status bar update - execution will show output in output window)
# Status bar stays at default (STATUS_BAR_SHORTCUTS) - error message is in output

But _debug_step_line() at line ~820 explicitly updates status bar:
self.status_bar.set_text(f"Paused at {pc_display} - {key_to_display(STEP_KEY)}=Step, {key_to_display(CONTINUE_KEY)}=Continue, {key_to_display(STOP_KEY)}=Stop")

Similar updates occur in _debug_step() at line ~750. The comments claim 'no status bar update' but code clearly updates it when paused.

---

#### code_inconsistency

**Description:** Inconsistent cursor positioning after delete line operation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _delete_current_line() at line ~920:
# Always position at column 1 (start of line number field)
if line_index < len(lines):
    # Position at start of line that moved up (column 1)
    if line_index > 0:
        new_cursor_pos = sum(len(lines[i]) + 1 for i in range(line_index)) + 1
    else:
        new_cursor_pos = 1  # First line, column 1
else:
    # Was last line, position at end of previous line
    if lines:
        new_cursor_pos = sum(len(lines[i]) + 1 for i in range(len(lines) - 1)) + len(lines[-1])

Comment says 'Always position at column 1' but the else branch positions at end of previous line, not column 1. This is inconsistent behavior.

---

#### code_vs_comment

**Description:** Comment claims column 7 is start of code area, but code uses variable code_start from _parse_line_number

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _insert_line_after_current():
Comment says: '# Position cursor on the new line, at the code area (column 7)'
and 'new_cursor_pos = 7  # Column 7 is start of code area'

But in _toggle_breakpoint_current_line(), the code uses:
line_number, code_start = self.editor._parse_line_number(line)
code_area = line[7:] if len(line) > 7 else ""

This suggests column 7 is hardcoded in some places but _parse_line_number returns a variable code_start in others. The comment may be outdated if line number width is variable.

---

#### code_vs_comment

**Description:** Comment about breakpoint storage contradicts implementation details

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program() comment:
'Note: reset_for_run() clears variables and resets PC. Breakpoints are STORED in the editor (self.editor.breakpoints) as the authoritative source, not in runtime. This allows them to persist across runs. After reset_for_run(), we re-apply them to the interpreter below via set_breakpoint() calls so execution can check them.'

But the code shows breakpoints are re-applied AFTER interpreter.start():
'# Start interpreter (sets up statement table, etc.)
state = self.interpreter.start()
...
# Re-apply breakpoints from editor
for line_num in self.editor.breakpoints:
    self.interpreter.set_breakpoint(line_num)'

The comment says 'below' but doesn't clarify that it's after interpreter.start(), which is important timing information.

---

#### internal_inconsistency

**Description:** Inconsistent handling of code_start position across methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_insert_line_after_current() hardcodes column 7:
'new_cursor_pos = 7  # Column 7 is start of code area'

_toggle_breakpoint_current_line() uses both:
'line_number, code_start = self.editor._parse_line_number(line)'
and
'code_area = line[7:] if len(line) > 7 else ""'

This suggests the code area position may be variable (from _parse_line_number) but is hardcoded as 7 in some places. If line numbers can be variable width, this is a bug.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says immediate executor already called interpreter.start() for RUN commands, but this may not be accurate for all cases

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method:
Comment says: "# NOTE: Don't call interpreter.start() here - the immediate executor already
# called it if needed (e.g., 'RUN 120' called interpreter.start(start_line=120)
# to set PC to line 120). Calling it again would reset PC to the beginning."

This assumes the immediate executor handles all start() calls, but the code then checks 'if not hasattr(self.interpreter, 'state') or self.interpreter.state is None' and creates InterpreterState. The comment claims we don't call start() to avoid resetting PC, but the actual behavior depends on whether the immediate executor properly initialized state.

---

#### code_vs_comment

**Description:** Comment in _sync_program_to_runtime claims it doesn't start execution, but the method is called from _execute_immediate which then starts execution

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method:
Comment says: "# Sync program to runtime (updates statement table and line text map).
# If execution is running, _sync_program_to_runtime preserves current PC.
# If not running, it sets PC to halted. Either way, this doesn't start execution,
# but allows commands like LIST to see the current program."

However, immediately after calling _sync_program_to_runtime(), the code checks if interpreter.has_work() and starts execution if needed. While technically _sync_program_to_runtime itself doesn't start execution, the comment's claim that 'this doesn't start execution' is misleading in context since execution starts right after in the same method.

---

#### code_vs_comment

**Description:** cmd_delete and cmd_renum comments claim they update self.program then sync to runtime, but pass runtime=None to helper functions

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_delete:
Comment says: "Note: Updates self.program immediately (source of truth), then syncs to runtime."
Code calls: "deleted = delete_lines_from_program(self.program, args, runtime=None)"

In cmd_renum:
Comment says: "Note: Updates self.program immediately (source of truth), then syncs to runtime."
Code calls: "old_lines, line_map = renum_program(..., runtime=None)"

Both pass runtime=None to the helper functions, which suggests the helpers don't directly update runtime. The comment is accurate that _sync_program_to_runtime() is called after, but the 'Note' might be misleading about the helper functions' behavior.

---

#### internal_inconsistency

**Description:** Inconsistent handling of program state synchronization between editor and runtime

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The code has multiple sync methods:
1. _parse_editor_content() - parses editor text into self.editor_lines
2. _sync_program_to_runtime() - syncs self.program to runtime
3. _sync_program_to_editor() - syncs self.program to editor
4. _refresh_editor() - appears to be missing but referenced in cmd_delete and cmd_renum

The flow is inconsistent:
- _execute_immediate calls _parse_editor_content() then manually loads into self.program, then calls _sync_program_to_runtime()
- cmd_delete and cmd_renum call _refresh_editor() which is not defined in this file
- _load_program_file calls _sync_program_to_editor()

There's no clear single source of truth or consistent sync pattern.

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

#### Code vs Comment conflict

**Description:** Comment about widget types is incorrect

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 186 comment states:
# All widgets are tk.Variable instances (BooleanVar, StringVar, IntVar)

However, this is misleading. The self.widgets dictionary stores tk.Variable instances (BooleanVar, StringVar, IntVar), not the actual widget objects (Checkbutton, Spinbox, Entry, Combobox). The variables are associated with widgets, but they are not the widgets themselves. The comment should say 'All entries in self.widgets are tk.Variable instances' to be accurate.

---

#### code_vs_comment

**Description:** Comment about arrow click width uses specific pixel value without explaining rationale

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_variable_heading_click() (lines 1135-1139):
# Determine click action based on horizontal position within column header:
# - Left 20 pixels (arrow area) = toggle sort direction
# - Rest of header = cycle/set sort column
ARROW_CLICK_WIDTH = 20  # Width of clickable arrow area in pixels

The comment documents the behavior but doesn't explain why 20 pixels was chosen. This magic number should either be a configurable constant or have a comment explaining the rationale (e.g., 'typical arrow icon width', 'tested for usability', etc.).

---

#### code_vs_comment

**Description:** Comment in _update_immediate_status() describes checking 'not self.running' to prevent race conditions, but the actual race condition scenario is unclear

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment: "The 'not self.running' check prevents immediate mode execution when a program is running, even if the tick hasn't completed yet. This prevents race conditions where immediate mode could execute while the program is still running but between tick cycles."

However, the code structure shows:
1. can_exec_immediate = self.immediate_executor.can_execute_immediate()
2. can_execute = can_exec_immediate and not self.running

The comment suggests a race condition between ticks, but if self.running is True, the program is running. The 'between tick cycles' scenario described doesn't match the synchronous nature of the Tk event loop where _execute_tick() is scheduled via after(). The comment may be describing a theoretical race condition that doesn't actually exist in this single-threaded Tk implementation.

---

#### documentation_inconsistency

**Description:** TkIOHandler docstring claims input() prefers inline input field but input_line() ALWAYS uses modal dialog, but the distinction rationale is not explained

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler class docstring:
"Input strategy:
- INPUT statement: Uses inline input field when backend available, otherwise uses modal dialog (not a preference, but availability-based)
- LINE INPUT statement: Always uses modal dialog for consistent UX"

And in input_line() method:
"Unlike input() which prefers inline input field, this ALWAYS uses a modal dialog regardless of backend availability."

The documentation states LINE INPUT always uses modal dialog 'for consistent UX' but doesn't explain why LINE INPUT needs different UX than INPUT. Both read user input, so the design rationale for treating them differently is unclear and potentially inconsistent.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate() says 'This is the only location in tk_ui.py that calls has_work()' but doesn't explain why this constraint exists or if it's enforced

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment: "Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command). This is the only location in tk_ui.py that calls has_work()."

The comment makes a claim about being the 'only location' but:
1. Doesn't explain WHY it should be the only location
2. Doesn't indicate if this is enforced by design or just current state
3. Could become outdated if has_work() is called elsewhere in future

This type of comment is fragile and may mislead future maintainers.

---

#### code_vs_comment

**Description:** _parse_line_number() docstring claims MBASIC 5.21 requires whitespace between line number and statement, but regex allows end-of-string, making standalone line numbers valid

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment in _parse_line_number() says:
"# Match line number followed by whitespace OR end of string (both valid)
# Valid: '10 PRINT' (whitespace after), '10' (end after), '  10  REM' (leading whitespace ok)
# Invalid: '10REM' (no whitespace), 'ABC10' (non-digit prefix), '' (empty after strip)
# MBASIC 5.21 requires whitespace (or end of line) between line number and statement"

The comment says 'MBASIC 5.21 requires whitespace (or end of line) between line number and statement' but then validates '10' (standalone line number with no statement) as valid. This is contradictory - if there's no statement, there's nothing to separate. The regex '^(\d+)(?:\s|$)' correctly implements 'whitespace OR end', but the MBASIC 5.21 claim about 'between line number and statement' is misleading when no statement exists.

---

#### code_vs_comment

**Description:** _on_status_click() uses different regex pattern than _parse_line_number() for extracting BASIC line numbers, potentially causing inconsistent behavior

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_parse_line_number() uses:
match = re.match(r'^(\d+)(?:\s|$)', line_text)

_on_status_click() uses:
match = re.match(r'^\s*(\d+)', line_text)

The first pattern requires whitespace OR end-of-string after the number.
The second pattern allows anything after the number (no lookahead constraint).

This means _on_status_click() would match '10REM' as line 10, while _parse_line_number() would reject it. This inconsistency could cause the status click handler to show error messages for lines that the main parsing logic doesn't recognize as valid.

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

#### code_vs_comment

**Description:** Comment in _sync_program_from_editor says it's important for serialization but doesn't explain why or what breaks without it

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says: "This ensures the program manager reflects the current editor content,
even if the user hasn't run the program yet. Important for serialization."

The comment states it's 'Important for serialization' but doesn't explain what would happen if we serialized without syncing. Would we lose unsaved edits? Would the program be empty? This context would help maintainers understand the requirement.

---

#### code_vs_documentation

**Description:** Settings dialog implemented in web UI but not documented in editor commands or web UI help

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/editor-commands.md`

**Details:**
web_settings_dialog.py implements a full settings dialog with:
- Auto-numbering enable/disable
- Auto-number step configuration
- Resource limits viewing

But editor-commands.md only mentions 'Standard text editing operations' and 'UI-specific help' without documenting the settings dialog feature. No mention of how to access settings in any UI.

---

#### documentation_inconsistency

**Description:** Debugging documentation uses placeholder syntax {{kbd:*}} that doesn't match actual keybindings in web_keybindings.json

**Affected files:**
- `docs/help/common/debugging.md`
- `src/ui/web_keybindings.json`

**Details:**
debugging.md uses placeholders like:
- {{kbd:step:curses}}
- {{kbd:continue:curses}}
- {{kbd:quit:curses}}
- {{kbd:toggle_stack:tk}}

But web_keybindings.json shows actual keys:
- "step": {"keys": ["F10"], "primary": "F10"}
- "continue": {"keys": ["F5"], "primary": "F5"}
- "stop": {"keys": ["Esc"], "primary": "Esc"}
- "toggle_variables": {"keys": ["Ctrl+Alt+V"]}

The documentation should either use actual keys or explain the placeholder system. Also, 'quit' in docs vs 'stop' in JSON.

---

#### code_vs_documentation

**Description:** Session state tracks auto-numbering state but debugging docs don't mention auto-numbering affects debugging

**Affected files:**
- `src/ui/web/session_state.py`
- `docs/help/common/debugging.md`

**Details:**
session_state.py tracks:
# Auto-numbering state
last_edited_line_index: Optional[int] = None
last_edited_line_text: Optional[str] = None

And web_settings_dialog.py shows auto-numbering is configurable.

But debugging.md doesn't mention how auto-numbering interacts with breakpoints, stepping, or line numbers during debugging. If lines are auto-renumbered, do breakpoints move? This should be documented.

---

#### documentation_inconsistency

**Description:** Documentation mentions 'toggle_variables' but JSON has no 'toggle_stack' keybinding

**Affected files:**
- `docs/help/common/debugging.md`
- `src/ui/web_keybindings.json`

**Details:**
debugging.md mentions:
'Execution Stack Window
Opening Stack Window
Tk UI: Debug → Execution Stack or {{kbd:toggle_stack:tk}}'

But web_keybindings.json only has:
"toggle_variables": {"keys": ["Ctrl+Alt+V"]}

No 'toggle_stack' keybinding is defined. Either the documentation is wrong or the keybinding is missing from the JSON.

---

#### documentation_inconsistency

**Description:** Inconsistent precision information for SINGLE type

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/atn.md`

**Details:**
data-types.md states SINGLE has 'approximately 7 digits' of precision, while atn.md states 'the evaluation of ATN is always performed in single precision (~7 significant digits)'. The atn.md note about PI calculation says 'the result is limited to single precision (~7 digits)' but then says 'For higher precision, use ATN(CDBL(1)) * 4 to get double precision' - this is misleading because ATN itself is always single precision according to the same document.

---

#### documentation_inconsistency

**Description:** Missing cross-reference to overflow error documentation

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
data-types.md mentions 'ERROR: Overflow' in examples but doesn't link to the error codes documentation. The error-codes.md file exists and documents overflow as error code 6 (OV), but there's no cross-reference from the data types page.

---

#### documentation_inconsistency

**Description:** Incomplete cross-reference in appendices index

**Affected files:**
- `docs/help/common/language/appendices/index.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
appendices/index.md says error-codes.md includes 'Error handling references (see [Error Handling](../statements/index.md#error-handling) for detailed examples)' but error-codes.md itself has a 'See Also' section that references individual statements like 'ON ERROR GOTO', 'ERR and ERL', 'ERROR', and 'RESUME' without mentioning the general error handling section.

---

#### documentation_inconsistency

**Description:** Error code reference format inconsistency

**Affected files:**
- `docs/help/common/language/functions/cvi-cvs-cvd.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
cvi-cvs-cvd.md states 'Raises "Illegal function call" (error code FC)' using the two-letter code 'FC', while error-codes.md shows this as 'Code: FC, Number: 5'. The documentation should be consistent about whether to use the letter code, number, or both when referencing errors.

---

#### documentation_inconsistency

**Description:** Inconsistent navigation between main index and getting started

**Affected files:**
- `docs/help/common/index.md`
- `docs/help/common/getting-started.md`

**Details:**
index.md shows a table with keyboard shortcuts for different UIs and links to UI-specific guides, but getting-started.md has a 'How to Enter Programs' section that also links to UI-specific help. The index.md says 'For complete shortcuts, see your UI-specific guide' while getting-started.md says 'See your UI-specific help for how to type programs'. These should be coordinated to avoid redundancy.

---

#### documentation_inconsistency

**Description:** LINE INPUT# documentation references non-existent input_hash.md file

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
In inputi.md 'See Also' section:
- [INPUT#](input_hash.md) - Read data from sequential file

But there is no input_hash.md file in the provided documentation. This should likely reference a file about INPUT# statement for sequential file reading.

---

#### documentation_inconsistency

**Description:** PRINT# documentation references non-existent input_hash.md file

**Affected files:**
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
In printi-printi-using.md 'See Also' section:
- [INPUT#](input_hash.md) - Read data from sequential file

But there is no input_hash.md file in the provided documentation.

---

#### documentation_inconsistency

**Description:** OPEN documentation references non-existent input_hash.md file

**Affected files:**
- `docs/help/common/language/statements/open.md`

**Details:**
In open.md 'See Also' section:
- [INPUT#](input_hash.md) - Read from sequential file

But there is no input_hash.md file in the provided documentation.

---

#### documentation_inconsistency

**Description:** PRINT# documentation missing WRITE# reference in See Also

**Affected files:**
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
The printi-printi-using.md file mentions WRITE# in the remarks:
"PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer"

But the 'See Also' section includes:
- [WRITE#](writei.md) - Write data with automatic delimiters

However, no writei.md file is provided in the documentation set, so this reference is broken.

---

#### documentation_inconsistency

**Description:** Contradictory information about file closing behavior

**Affected files:**
- `docs/help/common/language/statements/load.md`
- `docs/help/common/language/statements/merge.md`

**Details:**
load.md states:
"LOAD (without ,R): Closes all open files"
"LOAD with ,R option: all open data files are kept open"
"Compare with MERGE: Never closes files"

merge.md states:
"Unlike LOAD (without ,R), MERGE does NOT close open files. Files that are open before MERGE remain open after MERGE completes."

This is consistent, but the emphasis and wording differs. The key point is clear: LOAD without ,R closes files, LOAD with ,R keeps files open, MERGE never closes files. However, the documentation could be more consistently worded.

---

#### documentation_inconsistency

**Description:** PUT documentation mentions WRITE# but no file provided

**Affected files:**
- `docs/help/common/language/statements/put.md`

**Details:**
The put.md file states in the Note:
"PRINT#, PRINT# USING, and WRITE# may be used to put characters in the random file buffer before a PUT statement."

But no writei.md file is provided in the documentation set, making this reference incomplete.

---

#### documentation_inconsistency

**Description:** Cross-reference inconsistency: RESET doc warns not to confuse with RSET, but RSET doc warns not to confuse with RESET. Both warnings exist but point in opposite directions.

**Affected files:**
- `docs/help/common/language/statements/reset.md`
- `docs/help/common/language/statements/rset.md`

**Details:**
RESET.md: "**Note:** Do not confuse RESET with [RSET](rset.md), which right-justifies strings in random file fields."

RSET.md: "**Note:** Do not confuse RSET with [RESET](reset.md), which closes all open files."

Both documents have the same warning structure, which is redundant. Only one needs the warning, or they should be phrased differently.

---

#### documentation_inconsistency

**Description:** Inconsistent description of file closing behavior across program termination commands.

**Affected files:**
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
RUN.md: "All open files are closed (unlike STOP, which keeps files open)"

STOP.md: "Unlike the END statement, the STOP statement does not close files."

SYSTEM.md: "When SYSTEM is executed: - All open files are closed"

The documentation clearly states RUN closes files and STOP doesn't, but doesn't mention whether END closes files (though STOP.md implies END does close files). This should be explicitly stated in all three docs for clarity.

---

#### documentation_inconsistency

**Description:** Variable name significance documentation differs between variables.md and settings.md regarding case sensitivity behavior.

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md: "**Note on Variable Name Significance:** In the original MBASIC 5.21, only the first 2 characters of variable names were significant (AB, ABC, and ABCDEF would be the same variable). This Python implementation uses the full variable name for identification, allowing distinct variables like COUNT and COUNTER.

**Case Sensitivity:** Variable names are not case-sensitive by default (Count = COUNT = count), but the behavior when using different cases can be configured via the `variables.case_conflict` setting..."

settings.md: "**Choices for `variables.case_conflict`:**

BASIC is case-insensitive by default (Count = COUNT = count are the same variable). This setting controls which case version is displayed when the same variable is referenced with different cases:

- `first_wins` - First occurrence sets the case (silent) - e.g., if `Count` is used first, all references display as `Count`"

The variables.md says case behavior "can be configured" but doesn't clearly explain that the variables ARE the same (just displayed differently), while settings.md is clearer that they're the same variable with different display. This could confuse users about whether case_conflict creates different variables or just affects display.

---

#### documentation_inconsistency

**Description:** Inconsistent title formatting: WRITE uses quotes in title, WRITE# uses quotes in title, but they're formatted differently.

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md: 'title: "WRITE (Screen)"'
writei.md: 'title: "WRITE# (File)"'

Both use quotes around the title, which is inconsistent with other statement docs that don't use quotes. Also, the parenthetical descriptions (Screen) vs (File) are helpful but not used consistently across other I/O commands like PRINT/PRINT# or INPUT/INPUT#.

---

#### documentation_inconsistency

**Description:** Incomplete STEP command documentation

**Affected files:**
- `docs/help/mbasic/extensions.md`

**Details:**
Extensions.md shows 'STEP INTO' and 'STEP OVER' with '(planned)' status, but doesn't clarify if basic 'STEP' and 'STEP 5' are fully implemented or also planned. The status line says 'MBASIC-2025 Extension' suggesting it exists, but the planned features create ambiguity.

---

#### documentation_inconsistency

**Description:** Contradictory WIDTH statement behavior

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
Compatibility.md states 'WIDTH is parsed for compatibility but performs no operation' and then immediately says 'The "WIDTH LPRINT" syntax is not supported'. If WIDTH is a no-op, why specifically call out that WIDTH LPRINT is not supported? This suggests either:
1. WIDTH is partially implemented (some forms work, some don't)
2. The documentation is imprecise about what 'no-op' means
3. There's a parsing vs execution distinction not clearly explained

---

#### documentation_inconsistency

**Description:** Unclear semantic analyzer status

**Affected files:**
- `docs/help/mbasic/architecture.md`

**Details:**
Architecture.md states 'Semantic Analyzer: ✅ Complete (18 optimizations)' and 'The semantic analyzer is production-ready' but also says 'Code Generation: ❌ Not implemented (future work)'. This creates confusion about what 'production-ready' means if the analyzer can't generate code. The doc should clarify that it's production-ready for analysis/reporting purposes only, not for compilation.

---

#### documentation_inconsistency

**Description:** Inconsistent UI listing - Web UI mentioned in some places but not others

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/getting-started.md`
- `docs/help/mbasic/index.md`

**Details:**
features.md lists four UIs: 'MBASIC supports four interfaces: Curses UI (Default), CLI Mode, Tkinter GUI, Web UI' with detailed Web UI section.

getting-started.md lists four UIs: 'MBASIC supports four interfaces: Curses UI (Default), CLI Mode, Tkinter GUI, Web UI'

index.md only mentions three UIs: 'Choice of user interfaces (CLI, Curses, Tkinter)' and 'UI-Specific Guides' section only links to Curses, CLI, and Tk - no Web UI link.

The Quick Links section in index.md says 'Choose your UI: [CLI](../ui/cli/index.md), [Curses](../ui/curses/index.md), [Tk](../ui/tk/index.md), or Web' but 'Web' is not a link.

---

#### documentation_inconsistency

**Description:** Debugging features availability inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
features.md states under Debugging section: 'Breakpoints - Set/clear breakpoints (available in all UIs; access method varies)' and similar for step execution, variable viewing, and stack viewer.

cli/debugging.md documents BREAK, STEP, and STACK commands for CLI, confirming these are available.

However, features.md says 'See UI-specific documentation for details: [CLI Debugging](../ui/cli/debugging.md), [Curses UI](../ui/curses/feature-reference.md), [Tk UI](../ui/tk/feature-reference.md)' but the Curses and Tk links point to 'feature-reference.md' which may not exist or may not be the correct debugging documentation path.

---

#### documentation_inconsistency

**Description:** Keyboard shortcut notation inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/getting-started.md`

**Details:**
features.md uses template notation: '{{kbd:run:curses}}', '{{kbd:save:curses}}', '{{kbd:help:curses}}', '{{kbd:quit:curses}}', '{{kbd:find:tk}}', '{{kbd:replace:tk}}', '{{kbd:step_line:curses}}'

getting-started.md also uses template notation in 'Common keyboard shortcuts (Curses UI)' section with same format.

However, it's unclear if these templates are meant to be processed/replaced with actual key combinations or if they're meant to be displayed as-is. The documentation doesn't explain this notation system.

---

#### documentation_inconsistency

**Description:** LPRINT implementation status unclear

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md states: 'LPRINT - Line printer output (Note: Statement is parsed but produces no output - see [LPRINT](../common/language/statements/lprint-lprint-using.md) for details)'

not-implemented.md does not mention LPRINT at all in its list of not-implemented features.

This creates ambiguity: is LPRINT 'implemented' (parsed) or 'not implemented' (produces no output)? The distinction between 'parsed but non-functional' vs 'not implemented' should be clearer.

---

#### documentation_inconsistency

**Description:** STEP INTO/OVER documented but marked as not implemented

**Affected files:**
- `docs/help/ui/cli/debugging.md`

**Details:**
cli/debugging.md documents syntax: 'STEP INTO - Step into subroutines' and 'STEP OVER - Step over subroutine calls'

But then under 'Limitations' section states: 'STEP INTO/OVER not yet implemented (use STEP)'

This is contradictory - the syntax section implies they work, but limitations say they don't. The syntax section should either be removed or marked as 'planned' or 'future'.

---

#### documentation_inconsistency

**Description:** Web UI file storage limitations may be incomplete

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md states for Web UI: 'In-memory filesystem - Virtual filesystem with limitations: 50 file limit maximum, 1MB per file maximum, No path support (simple filenames only), No persistent storage across sessions'

Then says: 'See [Compatibility Guide](compatibility.md) for complete Web UI file storage details.'

However, the provided compatibility.md file is not in the documentation set, so we cannot verify if there are additional limitations or if the list in features.md is actually complete.

---

#### documentation_inconsistency

**Description:** Inconsistent information about Variables Window keyboard shortcut

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/quick-reference.md under 'Global Commands' states: '**Menu only** | Toggle variables window'

However, docs/help/ui/curses/feature-reference.md under 'Variable Inspection' states: 'Variables Window (Menu only)' and says 'Open/close the variables inspection window showing all program variables and their current values. **Note:** Access via menu only - no keyboard shortcut assigned.'

But docs/help/ui/curses/variables.md shows: 'Press `{{kbd:toggle_variables:curses}}` to open the variables window.'

This is contradictory - either there is a keyboard shortcut or there isn't.

---

#### documentation_inconsistency

**Description:** Inconsistent information about Execution Stack access method

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/quick-reference.md under 'Global Commands' states: '**Menu only** | Toggle execution stack window'

However, docs/help/ui/curses/feature-reference.md under 'Variable Inspection > Execution Stack' provides multiple access methods:
- 'Via menu: Ctrl+U → Debug → Execution Stack'
- 'Via command: Type `STACK` in immediate mode (same as CLI)'

This contradicts the 'menu only' designation in the quick reference.

---

#### documentation_inconsistency

**Description:** Contradictory information about variable sorting default order

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/variables.md under 'Sorting Options' states: 'Press `s` to cycle through sort orders:
- **Accessed**: Most recently accessed (read or written) - shown first
- **Written**: Most recently written to - shown first
- **Read**: Most recently read from - shown first
- **Name**: Alphabetical by variable name'

However, docs/help/ui/curses/feature-reference.md under 'Variable Sorting' states: '- **Accessed**: Most recently accessed (read or written) - newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name - A to Z'

The difference between 'shown first' and 'newest first' is unclear, and the Name sort adds 'A to Z' in one place but not the other.

---

#### documentation_inconsistency

**Description:** Contradictory information about variable editing capability

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/variables.md under 'Modifying Variables' states: '### Direct Editing Not Available
⚠️ **Not Implemented**: You cannot edit variable values directly in the variables window.'

However, docs/help/ui/curses/feature-reference.md under 'Variable Inspection' states: 'Edit Variable Value (Not implemented)
⚠️ Variable editing is not available in Curses UI. You cannot directly edit values in the variables window. Use immediate mode commands to modify variable values instead.'

Both say it's not available, but variables.md says 'Not Implemented' (implying future implementation) while feature-reference.md says 'not available' (more permanent). The status should be consistent.

---

#### documentation_inconsistency

**Description:** Inconsistent information about Settings access method

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/feature-reference.md under 'Settings & Configuration' states: 'Settings Widget (Menu only)
Interactive settings dialog for configuring MBASIC behavior. Adjust auto-numbering, keyword case style, variable handling, themes, and more.
**Note:** Access via menu only - no keyboard shortcut assigned.'

However, docs/help/ui/curses/settings.md states: '## Opening the Settings Widget

**Keyboard shortcut:** `Ctrl+,`'

This is contradictory - either there is a Ctrl+, shortcut or it's menu-only.

---

#### documentation_inconsistency

**Description:** Inconsistent filter mode options between documents

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/variables.md under 'Filtering and Searching > Filter Options' states: 'Press `f` to cycle through filters:
- **All**: Show all variables
- **Scalars**: Hide arrays
- **Arrays**: Show only arrays
- **Modified**: Show recently changed'

However, docs/help/ui/curses/quick-reference.md under 'Variables Window (when visible)' states: '**f** | Cycle filter mode (All → Scalars → Arrays → Modified)'

The quick-reference shows the cycle order but doesn't explain what each filter does. The descriptions should be consistent.

---

#### documentation_inconsistency

**Description:** Inconsistent shortcut notation for Search Help

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`

**Details:**
feature-reference.md shows:
'Search Help ({{kbd:file_save:tk}}hift+F)'

Similar typo as above - should likely be 'Shift+F' or '{{kbd:file_save:tk}}+Shift+F'. The pattern suggests {{kbd:file_save:tk}} macro was incorrectly used.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut references for Run Program

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
feature-reference.md states:
'Run Program ({{kbd:run_program:tk}} or F5)'

But getting-started.md uses:
'{{kbd:run_program}}' (without :tk suffix)

Inconsistent macro usage across documents.

---

#### documentation_inconsistency

**Description:** Settings dialog implementation status unclear

**Affected files:**
- `docs/help/ui/tk/settings.md`

**Details:**
settings.md states at the top:
'**Implementation Status:** The Tk (Tkinter) desktop GUI is planned to provide the most comprehensive settings dialog. **The features described in this document represent planned/intended implementation and are not yet available.**'

But then later states:
'**Note:** Settings storage is implemented, but the settings dialog itself is not yet available in the Tk UI.'

This creates confusion about what is actually implemented vs planned.

---

#### documentation_inconsistency

**Description:** Inconsistent notation for keyboard shortcuts

**Affected files:**
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`

**Details:**
tips.md uses:
'{{kbd:smart_insert:tk}}', '{{kbd:toggle_variables:tk}}', '{{kbd:toggle_stack:tk}}', '{{kbd:run_program:tk}}', '{{kbd:file_save:tk}}', '{{kbd:renumber:tk}}'

workflows.md uses:
'{{kbd:file_new:tk}}', '{{kbd:run_program:tk}}', '{{kbd:file_save:tk}}', '{{kbd:smart_insert:tk}}', '{{kbd:toggle_variables:tk}}', '{{kbd:renumber:tk}}'

Both use :tk suffix consistently, but getting-started.md and features.md sometimes omit it.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for browser DevTools

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md states:
'Press {{kbd:help:web}}2 to open browser tools'

This appears to be a typo - should likely be 'F12' (standard browser DevTools shortcut). The {{kbd:help:web}}2 notation suggests a macro error.

---

#### documentation_inconsistency

**Description:** Quick Reference table shows inconsistent shortcuts

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`

**Details:**
The Quick Reference table at the bottom of feature-reference.md shows:
'| {{kbd:cut:tk}} | Stop Program |'

But earlier in the document, Stop/Interrupt is described with the same shortcut, and Cut is also assigned to {{kbd:cut:tk}}. The table should clarify this conflict or use different shortcuts.

---

#### documentation_inconsistency

**Description:** Contradictory information about 'Open Example' feature availability

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
features.md under 'File Operations > Open Files (Planned)' lists 'Recent files list' as a planned feature.

However, web-interface.md under 'File Menu' states: 'Note: An "Open Example" feature to choose from sample BASIC programs is planned for a future release.'

But features.md under 'Local Storage > Currently Implemented' says: 'Recent files list stored in browser localStorage'.

This is contradictory - the recent files list is described as both currently implemented (in localStorage) and planned.

---

#### documentation_inconsistency

**Description:** Contradictory information about settings storage mechanisms

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/features.md`

**Details:**
settings.md describes two storage mechanisms:
1. 'Local Storage (Default)' - settings stored in browser localStorage
2. 'Redis Session Storage (Multi-User Deployments)' - settings stored in Redis

However, features.md under 'Local Storage > Currently Implemented' only mentions: 'Programs stored in Python server memory (session-only, lost on page refresh)' and 'Recent files list stored in browser localStorage'.

There's no mention of Redis storage option in features.md, creating an incomplete picture of storage capabilities.

---

#### documentation_inconsistency

**Description:** Inconsistent description of input area behavior

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md under 'Interface Overview > 5. Input Area' describes: 'When your program uses INPUT, a blue row appears with: Prompt text, Input field, Submit button'.

However, web-interface.md makes no mention of this input area component at all in its 'Main Components' section. This is a significant UI element that should be documented consistently.

---

#### documentation_inconsistency

**Description:** Inconsistent information about settings dialog tabs

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/settings.md`

**Details:**
settings.md under 'Tabs' describes two tabs: 'Editor Tab' and 'Limits Tab'.

However, features.md under 'Settings and Preferences > Currently Implemented' only mentions: 'See Settings for currently available settings (auto-numbering, line increment)'.

The Limits Tab is not mentioned in features.md at all, creating an incomplete picture of available settings.

---

#### documentation_inconsistency

**Description:** Calendar program appears in both Games and Utilities libraries with cross-references, but the descriptions and metadata differ

**Affected files:**
- `docs/library/games/index.md`
- `docs/library/utilities/index.md`

**Details:**
Games library shows:
### Calendar
Year-long calendar display program from Creative Computing
**Source:** Creative Computing, Morristown, NJ
**Year:** 1979
**Tags:** calendar, display
**Note:** A simpler calendar utility is also available in the [Utilities Library](../utilities/index.md#calendar)

Utilities library shows:
### Calendar
Simple calendar generator - prints a formatted calendar for any month/year (1900-2099)
**Source:** Dr Dobbs Nov 1981
**Year:** 1982
**Tags:** date, calendar, utility
**Note:** A different calendar program is also available in the [Games Library](../games/index.md#calendar)

The sources differ (Creative Computing vs Dr Dobbs), years differ (1979 vs 1982), and descriptions conflict (year-long vs month/year, simpler vs different)

---

#### documentation_inconsistency

**Description:** CLI debugging capabilities described inconsistently

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
CASE_HANDLING_GUIDE.md does not mention CLI debugging limitations.

CHOOSING_YOUR_UI.md states:
**Limitations:**
- Line-by-line editing only
- No visual debugging (text commands only)
- No mouse support
- No Save without filename

And includes a note:
> **Note:** CLI has full debugging capabilities through commands (BREAK, STEP, STACK), but lacks the visual debugging interface (Variables Window, clickable breakpoints, etc.) found in Curses, Tk, and Web UIs.

This distinction between 'full debugging capabilities' and 'no visual debugging' could be clearer and should be consistent across documentation.

---

#### documentation_inconsistency

**Description:** Conflicting information about Curses UI variable editing capability

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
In the Curses section under 'Unique advantages', it lists features without mentioning variable editing limitations.

But under 'Limitations' it states:
- Partial variable editing

However, in the 'Detailed UI Profiles' section for Curses, there's no explanation of what 'partial variable editing' means or how it differs from other UIs. The Tk section mentions 'Smart Insert mode' but doesn't clarify if this is what Curses lacks.

---

### 🟢 Low Severity

#### Documentation inconsistency

**Description:** Inconsistent documentation style for statement nodes - some have detailed syntax examples, others don't

**Affected files:**
- `src/ast_nodes.py`

**Details:**
Some nodes have extensive syntax documentation:
- InputStatementNode (lines 202-220): Detailed explanation of suppress_question and semicolon usage
- ChainStatementNode (lines 524-541): Multiple syntax examples and parameter explanations
- RenumStatementNode (lines 619-632): Detailed parameter documentation

Others have minimal documentation:
- EndStatementNode (lines 577-583): Just 'END' syntax
- TronStatementNode (lines 586-592): Just 'TRON' syntax
- SystemStatementNode (lines 605-615): Brief description

This inconsistency makes the documentation less useful for understanding complex statements.

---

#### Documentation inconsistency

**Description:** VariableNode documentation has redundant explanation of explicit_type_suffix

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode lines 862-875:
The docstring explains explicit_type_suffix twice:
1. In the 'Type suffix handling' section (lines 864-870)
2. In the example (lines 872-873)

The explanation 'Both fields must always be examined together to correctly handle variable typing' appears at line 874, but the relationship between type_suffix and explicit_type_suffix could be clearer. The documentation doesn't explain what happens when explicit_type_suffix=True but type_suffix=None (is this valid?).

---

#### Documentation inconsistency

**Description:** RemarkStatementNode comment_type default value explanation is confusing

**Affected files:**
- `src/ast_nodes.py`

**Details:**
RemarkStatementNode lines 697-707:
'Note: comment_type preserves the original comment syntax used in source code. The parser sets this to "REM", "REMARK", or "APOSTROPHE" based on input. Default value "REM" is used only when creating nodes programmatically.'

The note says 'Default value "REM" is used only when creating nodes programmatically', but the dataclass definition shows:
comment_type: str = "REM"  # Tracks original syntax: "REM", "REMARK", or "APOSTROPHE"

This implies the parser might not always set comment_type, contradicting the statement 'The parser sets this to...'.

---

#### Documentation inconsistency

**Description:** ChainStatementNode delete_range type annotation inconsistency

**Affected files:**
- `src/ast_nodes.py`

**Details:**
ChainStatementNode line 540:
delete_range: Optional[Tuple[int, int]] = None  # (start_line_number, end_line_number) for DELETE option - tuple of int line numbers

The comment '(start_line_number, end_line_number) for DELETE option - tuple of int line numbers' is redundant with the type annotation 'Tuple[int, int]'. The comment adds 'tuple of int line numbers' which is already clear from the type. This is inconsistent with other fields that don't repeat type information in comments.

---

#### code_vs_comment_conflict

**Description:** Comment describes sign determination logic but references wrong line number after code changes

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 274 comment: 'Determine sign - preserve negative sign for values that round to zero.
Use original_negative (captured at line 272 before rounding)...'
However, original_negative is actually captured at line 270, not line 272. The comment references an outdated line number from before code was modified.

---

#### code_vs_comment_conflict

**Description:** Comment about leading sign padding behavior contradicts general padding logic

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Line 337-338 comment: '# For leading sign: padding comes first, then sign immediately before number
if spec['leading_sign']:
    # Add padding first (but only spaces, not asterisks for leading sign)'
Line 342-346 code: 'if spec['asterisk_fill']:
    result_parts.append('*' * max(0, padding_needed))
else:
    result_parts.append(' ' * max(0, padding_needed))'
The comment at line 338 says 'but only spaces, not asterisks for leading sign', but the code at lines 342-346 (in the else branch after leading_sign) still checks asterisk_fill and can add asterisks. The comment implies leading_sign prevents asterisk_fill, but the code structure doesn't enforce this - it's just that the padding happens in the if branch for leading_sign (line 340) which only uses spaces.

---

#### documentation_inconsistency

**Description:** CaseKeeperTable supports 'error' policy but case_string_handler.py doesn't document error handling behavior

**Affected files:**
- `src/case_keeper.py`
- `src/case_string_handler.py`

**Details:**
src/case_keeper.py lines 104-113: Policy 'error' raises ValueError on case conflicts
src/case_string_handler.py lines 48-49: 'policy = get("keywords.case_style", "force_lower")' with no mention of error policy or exception handling
The case_keeper module implements an 'error' policy that raises exceptions, but case_string_handler doesn't document this behavior or wrap calls in try-except for this specific case (only has a general exception handler at line 62).

---

#### code_vs_comment_conflict

**Description:** INPUT function docstring describes BASIC syntax with # but comment says # is stripped by parser

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Lines 862-869 docstring: 'BASIC syntax:
    INPUT$(n) - read n characters from keyboard
    INPUT$(n, #filenum) - read n characters from file

Python call syntax (from interpreter):
    INPUT(n) - read n characters from keyboard
    INPUT(n, filenum) - read n characters from file

Note: The # prefix in BASIC syntax is stripped by the parser before calling this method.'
The docstring clearly documents both syntaxes and explains the # is stripped, but this creates potential confusion about whether the method should handle # or not. The note clarifies it, but the dual documentation might be clearer if it only showed the Python call syntax since that's what the method actually receives.

---

#### code_vs_comment

**Description:** ImmediateExecutor.execute() docstring mentions state names like 'idle', 'paused', 'at_breakpoint', 'done', 'error', 'waiting_for_input', 'running' but these are not actual enum values

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Docstring says: "State names used in documentation (not actual enum values):
- 'idle' - No program loaded (halted=True)
- 'paused' - User hit Ctrl+Q/stop (halted=True)
- 'at_breakpoint' - Hit breakpoint (halted=True)
- 'done' - Program finished (halted=True)
- 'error' - Program encountered error (error_info is not None)
- 'waiting_for_input' - Waiting for INPUT (input_prompt is not None)
- 'running' - Program executing (halted=False) - DO NOT execute immediate mode

Note: The actual implementation checks boolean flags (halted, error_info, input_prompt),
not string state values."

This is technically correct but potentially confusing. The docstring explicitly states these are "not actual enum values" and that the implementation uses boolean flags, so this is more of a documentation style issue than a true inconsistency.

---

#### documentation_inconsistency

**Description:** ImmediateExecutor._show_help() help text claims 'Multi-statement lines (: separator) are fully supported' but this is not demonstrated or validated in the code

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Help text states: "• Multi-statement lines (: separator) are fully supported"

The execute() method builds a program with "0 " + statement and parses it, then executes each statement in line_node.statements. While this suggests multi-statement support should work (since the parser would handle : separators), there's no explicit test or validation that this actually works correctly in immediate mode. This is a minor documentation claim without clear code evidence.

---

#### code_vs_comment

**Description:** Comment says 'add_line expects complete line text with line number' but then constructs the line by concatenating line_num and line_content

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Comment: "# Add/update line - add_line expects complete line text with line number"

Code:
complete_line = f"{line_num} {line_content}"
success, error = ui.program.add_line(line_num, complete_line)

If add_line expects "complete line text with line number", why does it also take line_num as a separate first parameter? This suggests either the comment is wrong about what add_line expects, or the API design is redundant (passing line number twice).

---

#### code_vs_comment

**Description:** OutputCapturingIOHandler.input() docstring says 'INPUT statements are parsed and executed normally, but fail at runtime' but the method immediately raises RuntimeError without any parsing/execution

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Docstring: "Input not supported in immediate mode.

Note: INPUT statements are parsed and executed normally, but fail
at runtime when the interpreter calls this input() method."

Code:
def input(self, prompt=""):
    """Input not supported in immediate mode..."""
    raise RuntimeError("INPUT not allowed in immediate mode")

The docstring's note about "parsed and executed normally" is misleading. The INPUT statement is parsed and the interpreter begins execution, but when it calls this input() method, it immediately fails. The docstring makes it sound like more execution happens than actually does.

---

#### documentation_inconsistency

**Description:** Module docstring mentions 'Implementation note: Uses standard Python type hints (e.g., tuple[str, bool]) which require Python 3.9+' but doesn't specify what the project's minimum Python version is or if this is a problem

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Docstring: "Implementation note: Uses standard Python type hints (e.g., tuple[str, bool])
which require Python 3.9+. For earlier Python versions, use Tuple[str, bool] from typing."

This note warns about Python 3.9+ requirement but doesn't indicate:
1. What the project's actual minimum Python version is
2. Whether this is acceptable or needs to be changed
3. Whether other files in the project use the older Tuple syntax

This creates uncertainty about whether the code is consistent with project requirements.

---

#### code_vs_comment

**Description:** Module docstring claims 'There is intentional overlap between the two abstractions' for list_files() and delete() but doesn't explain why this design choice was made or if it causes any issues

**Affected files:**
- `src/filesystem/base.py`

**Details:**
Docstring: "Note: There is intentional overlap between the two abstractions.
Both provide list_files() and delete() methods, but serve different contexts:
FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for
runtime access (though not all BASIC dialects support runtime file operations)."

While the docstring acknowledges the overlap is intentional, it doesn't explain:
1. Why this duplication is necessary/beneficial
2. Whether the implementations should be identical or can differ
3. If there are any synchronization concerns between the two

This is more of a documentation completeness issue than a true inconsistency.

---

#### code_vs_comment

**Description:** Comment about ERL renumbering describes broader behavior than MBASIC manual specifies

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~580 states:
'INTENTIONAL DEVIATION FROM MANUAL:
This implementation renumbers for ANY binary operator with ERL on left, including arithmetic operators (ERL + 100, ERL * 2, etc.), not just comparison operators.'

This is documented as intentional deviation, but the severity of the deviation is unclear. The comment mentions 'Known limitation: Arithmetic like "IF ERL+100 THEN..." will incorrectly renumber the 100 if it happens to be an old line number.'

This creates ambiguity: is this a bug that needs fixing, or accepted behavior? The comment suggests both ('INTENTIONAL' but also 'incorrectly renumber').

---

#### code_vs_comment

**Description:** Module docstring lists commands in two categories but implementation doesn't distinguish them

**Affected files:**
- `src/interactive.py`

**Details:**
Module docstring at line ~1 states:
'- Direct commands: AUTO, EDIT, HELP (handled specially, not parsed as BASIC statements)
- Immediate mode statements: RUN, LIST, SAVE, LOAD, NEW, MERGE, FILES, SYSTEM, DELETE, RENUM, etc. (parsed as BASIC statements and executed in immediate mode)'

However, in execute_command() at line ~120, the implementation shows:
- AUTO, EDIT, HELP are handled directly (matches docstring)
- But LIST, DELETE, RENUM are ALSO handled directly (cmd_list, cmd_delete, cmd_renum methods exist)

The docstring claims these are 'parsed as BASIC statements' but they have dedicated command methods, suggesting they're also 'handled specially'. The categorization is misleading.

---

#### code_vs_comment_conflict

**Description:** Comment about line_text_map being empty for immediate mode may be misleading

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states: '# Pass empty line_text_map since immediate mode uses temporary line 0
# (no source line text available for error reporting, but this is fine
# for immediate mode where the user just typed the statement)'

However, the statement text IS available (it's the 'statement' parameter), so an empty map isn't strictly necessary. The code could populate line_text_map with {0: statement} for better error reporting.

---

#### documentation_inconsistency

**Description:** cmd_files docstring mentions drive letter syntax but doesn't explain why it's not supported

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring states: 'Note: Drive letter syntax (e.g., "A:*.*") is not supported in this implementation.'

This is a limitation note but doesn't explain if this is intentional (modern OS compatibility) or a missing feature. The help text from cmd_help doesn't mention this limitation at all.

---

#### code_vs_comment_conflict

**Description:** Comment about program_runtime persistence contradicts typical lifecycle expectations

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in execute_immediate says: 'Works for stopped programs (via STOP/Break) AND finished programs (program_runtime persists until NEW/LOAD/next RUN).'

This suggests program_runtime persists after program completion, which is unusual. Typically runtimes are cleared after program ends. This behavior should be verified as intentional or may indicate the runtime isn't being properly cleaned up.

---

#### documentation_inconsistency

**Description:** Docstring mentions 'idle' state but InterpreterState has no such state value

**Affected files:**
- `src/interpreter.py`

**Details:**
In start() method docstring (line 241):
"Returns:
    InterpreterState: Initial state (typically 'idle' or 'error' if setup fails)"

But InterpreterState is a dataclass with specific fields (input_prompt, error_info, etc.) and no 'state' or 'status' field that could be 'idle'. The state is determined by checking multiple fields (error_info, input_prompt, runtime.halted) as described in the class docstring.

---

#### code_vs_comment

**Description:** Comment about error_info being set 'just before' calling _invoke_error_handler is misleading

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 667-669 says:
"Note: error_info is set in the exception handler in tick_pc() just before
calling this method. We're now ready to invoke the error handler."

But looking at tick_pc() lines 410-437, error_info is set at line 418, then there's a check for error handler at line 421, and _invoke_error_handler is called at line 422. Between setting error_info and calling _invoke_error_handler, there's the check `if self.runtime.has_error_handler() and not already_in_error_handler:`. So it's not 'just before' - there's conditional logic in between.

---

#### code_vs_comment

**Description:** Comment about latin-1 encoding mentions CP437/CP850 but doesn't explain when conversion is needed

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1430 states:
# Encoding:
# Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
# CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
# Unicode U+0000-U+00FF, allowing round-trip byte preservation.
# Note: CP/M systems often used code pages like CP437 or CP850 for characters
# 128-255, which do NOT match latin-1. Latin-1 preserves the BYTE VALUES but
# not necessarily the CHARACTER MEANING for non-ASCII CP/M text. Conversion
# may be needed for accurate display of non-English CP/M files.

The comment mentions 'Conversion may be needed' but doesn't specify where or how this conversion should happen. This creates ambiguity about whether the interpreter should handle this conversion or if it's the user's responsibility.

---

#### code_vs_comment

**Description:** Comment in execute_midassignment() states 'start_idx == len(current_value) is considered out of bounds' but this contradicts typical string indexing behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment states: 'Note: start_idx == len(current_value) is considered out of bounds (can't start replacement past end)'

Code shows: if start_idx < 0 or start_idx >= len(current_value):

This means if a string is 'HELLO' (length 5), you cannot use MID$(A$, 6, 1) = 'X' to append. This is MBASIC 5.21 behavior according to the comment, but it's worth noting this differs from some BASIC dialects that allow this for appending.

---

#### Code vs Documentation inconsistency

**Description:** input_line() implementations claim to have known limitations about preserving spaces, but the limitation description is inconsistent across files

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/console.py`
- `src/iohandler/curses_io.py`
- `src/iohandler/web_io.py`

**Details:**
base.py says: "KNOWN LIMITATION (not a bug - platform limitation): Current implementations (console, curses, web) CANNOT fully preserve leading/trailing spaces due to underlying platform API constraints"

console.py says: "Note: Current implementation does NOT preserve leading/trailing spaces as documented in base class. Python's input() automatically strips them."

curses_io.py says: "Note: Current implementation does NOT preserve leading/trailing spaces as documented in base class. curses getstr() strips trailing spaces."

web_io.py says: "Note: Current implementation does NOT preserve leading/trailing spaces as documented in base class. HTML input fields strip spaces."

The base.py says Python input() strips "trailing newline/spaces" but console.py says it strips "leading/trailing spaces". Also, base.py says curses "strips trailing spaces" but doesn't mention leading spaces, while curses_io.py doesn't specify which spaces are stripped.

---

#### Code vs Comment conflict

**Description:** print() method has backward compatibility comment but the method was never renamed from print() to output() in this class

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment says: "# Backward compatibility alias
# This method was renamed from print() to output() to avoid conflicts with Python's
# built-in print function. The print() alias is maintained for backward compatibility
# with older code that may still call io_handler.print()."

But looking at the code, print() is defined first and calls output(). The comment suggests print() is the alias, but the implementation shows print() as the primary method that delegates to output(). The comment is backwards - output() should be the primary method with print() as the deprecated alias.

---

#### documentation_inconsistency

**Description:** Module docstring claims implementation is based on MBASIC-80 Reference Manual Version 5.21 but provides no verification of compliance

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring:
"Lexer for MBASIC 5.21 (CP/M era MBASIC-80)
Based on BASIC-80 Reference Manual Version 5.21"

This is a strong claim about standards compliance but there's no reference documentation provided to verify the implementation matches the manual. This could be considered incomplete documentation.

---

#### code_vs_comment

**Description:** Comment about Extended BASIC features enabling periods in identifiers lacks implementation verification

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring states:
"MBASIC 5.21 Extended BASIC features: This implementation enables Extended BASIC
features (e.g., periods in identifiers like 'RECORD.FIELD') as they are part of MBASIC 5.21."

The code does implement period handling in read_identifier() at line ~230:
"if char.isalnum() or char == '.'"

However, there's no validation that periods are only allowed in Extended BASIC mode or any configuration to enable/disable this feature. The comment implies this is a special Extended BASIC feature but it's always enabled in the implementation.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'end of line' vs 'end of statement' in method names and comments

**Affected files:**
- `src/parser.py`

**Details:**
The parser has two similar methods:
1. at_end_of_line() at line 234 - checks for NEWLINE or EOF
2. at_end_of_statement() at line 246 - checks for NEWLINE, EOF, COLON, REM, REMARK, or APOSTROPHE

The comment for at_end_of_line() at lines 236-240 says:
"Note: This method does NOT check for comment tokens (REM, REMARK, APOSTROPHE)
or statement separators (COLON). Use at_end_of_statement() when parsing statements
that should stop at comments/colons."

However, throughout the code, both methods are used inconsistently. For example, in parse_print() at line 1228, the code uses 'at_end_of_line()' but also checks for COLON and REM tokens separately, suggesting at_end_of_statement() should have been used instead.

---

#### code_vs_comment

**Description:** Incomplete comment about function name normalization

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deffn() method around line 2110:

Comment states: "Function name normalization: All function names are normalized to lowercase with 'fn' prefix (e.g., "FNR" becomes "fnr", "FNA$" becomes "fna$") for consistent lookup. This matches the lexer's identifier normalization and ensures function"

The comment is cut off mid-sentence ("ensures function"). This appears to be truncated documentation that should explain what the normalization ensures (likely "ensures function names are case-insensitive" or similar).

---

#### documentation_inconsistency

**Description:** Comment about MBASIC 5.21 behavior lacks verification context

**Affected files:**
- `src/parser.py`

**Details:**
In parse_dim() method around line 1890:

Comment states: "Dimension expressions: This implementation accepts any expression for array dimensions (e.g., DIM A(X*2, Y+1)), with dimensions evaluated at runtime. This matches MBASIC 5.21 behavior. Note: Some compiled BASICs (e.g., QuickBASIC) may require constants only."

This comment claims to match MBASIC 5.21 behavior but provides no reference or verification. It also mentions QuickBASIC as a contrast, but doesn't clarify if this implementation is specifically targeting MBASIC 5.21 compatibility or a more general BASIC dialect. This could lead to confusion about the intended compatibility target.

---

#### code_vs_comment

**Description:** apply_keyword_case_policy 'preserve' policy documentation says it's 'typically handled at a higher level' but then provides fallback behavior, creating ambiguity about when this code path executes.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Code comment:
'elif policy == "preserve":
    # The "preserve" policy is typically handled at a higher level (keywords passed with
    # original case preserved). If this function is called with "preserve" policy, we
    # return the keyword as-is if already properly cased, or capitalize as a safe default.
    # Note: This fallback shouldn\'t normally execute in correct usage.
    return keyword.capitalize()'

The phrase 'shouldn\'t normally execute in correct usage' suggests this is defensive code for an error condition, but it's not clear if this is a bug or expected fallback.

---

#### documentation_inconsistency

**Description:** renumber_with_spacing_preservation docstring says 'Caller should serialize these LineNodes using serialize_line()' but doesn't specify which serialize_line function (method vs module function).

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring:
'Returns:
    Dict of new_line_number -> LineNode (with updated positions)
    Caller should serialize these LineNodes using serialize_line() to regenerate text'

There's both PositionSerializer.serialize_line() (instance method) and serialize_line_with_positions() (module function). The documentation should clarify which to use.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for string length limits across docstrings and comments

**Affected files:**
- `src/resource_limits.py`

**Details:**
In __init__ docstring: 'Maximum byte length for a string variable (UTF-8 encoded). MBASIC 5.21 limit is 255 bytes.'

In check_string_length() docstring: 'String limits are measured in bytes (UTF-8 encoded), not character count. This matches MBASIC 5.21 behavior which limits string storage size.'

The first says 'byte length' and the second says 'measured in bytes' - consistent but could use unified terminology. Also, the second note says 'storage size' which is slightly different from 'byte length'.

---

#### code_vs_comment_conflict

**Description:** Comment in check_array_allocation() uses inline comment style that duplicates information already in the preceding block comment

**Affected files:**
- `src/resource_limits.py`

**Details:**
Line has: total_elements *= (dim_size + 1)  # +1 for 0-based indexing (0 to N)

But preceding comment already explains: 'Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21'

The inline comment '0-based indexing (0 to N)' is technically correct but could be confusing since MBASIC arrays are 0-based but DIM A(N) creates indices 0 through N (N+1 elements), not N elements.

---

#### documentation_inconsistency

**Description:** Module docstring describes three usage patterns but doesn't mention the preset configuration functions that implement them

**Affected files:**
- `src/resource_limits.py`

**Details:**
Module docstring shows:
'Usage:
    # Web UI
    limits = create_web_limits()
    interpreter = Interpreter(runtime, io, limits=limits)'

But doesn't mention that create_web_limits(), create_local_limits(), and create_unlimited_limits() are defined at the bottom of the file. A reader might think these are external functions. The docstring could reference 'See create_web_limits(), create_local_limits(), create_unlimited_limits() below'.

---

#### code_vs_comment

**Description:** Comment about set_variable() token requirement doesn't mention FakeToken usage pattern

**Affected files:**
- `src/runtime.py`

**Details:**
Lines 295-310 docstring says token is REQUIRED unless debugger_set=True, but doesn't mention the FakeToken pattern used by set_variable_raw().

Line 437-451 set_variable_raw() docstring explains:
"Internally calls set_variable() with a FakeToken(line=-1) to mark this as
a system/internal set (not from program execution)."

This FakeToken pattern is a third way to call set_variable() (beyond normal token and debugger_set=True), but it's not documented in set_variable()'s docstring. Users reading set_variable() won't know about this pattern.

---

#### Documentation inconsistency

**Description:** Deprecation notice uses inconsistent date format

**Affected files:**
- `src/runtime.py`

**Details:**
In get_loop_stack() deprecation notice:
"Deprecated since: 2025-10-25 (commit cda25c84)"

This date (2025-10-25) is in the future relative to typical software development timelines, suggesting either:
1. The date format is incorrect (should be 2024-10-25)
2. This is placeholder documentation
3. The codebase uses a non-standard dating convention

The date should be verified for accuracy.

---

#### code_vs_comment

**Description:** register_keyword() docstring says 'For compatibility with existing code' but doesn't explain what code or why compatibility is needed

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
The register_keyword() method has docstring:
'Register a keyword and return the display case.

For compatibility with existing code. Just applies the policy.'

This raises questions:
1. What existing code requires this method?
2. Why not remove it if it's just a wrapper for apply_case()?
3. Is this method deprecated?
4. The parameters line_num and column are marked unused - why accept them?

---

#### code_vs_documentation

**Description:** RedisSettingsBackend docstring says 'Optionally initialized from default file-based settings' but doesn't document when this happens

**Affected files:**
- `src/settings_backend.py`

**Details:**
RedisSettingsBackend.__init__() docstring:
'Optionally initialized from default file-based settings (if provided and not already in Redis)'

The implementation shows:
if default_settings and not self._exists():
    self.save_global(default_settings)

But the docstring doesn't explain:
1. When default_settings would be None vs provided
2. What happens on subsequent sessions (settings persist in Redis)
3. How to force reload from disk if Redis has stale data
4. Whether this is a one-time initialization or per-session

---

#### documentation_inconsistency

**Description:** Module docstring describes two scopes (global and project) but implementation has three (global, project, file)

**Affected files:**
- `src/settings.py`

**Details:**
Module docstring in settings.py:
'Supports global settings and project settings:
- Global: ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows)
- Project: .mbasic/settings.json in project directory'

But the implementation has:
- self.global_settings
- self.project_settings
- self.file_settings

And SettingScope enum has GLOBAL, PROJECT, and FILE.

The module docstring should mention FILE scope even if it's not yet fully implemented.

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for non-interactive execution mode

**Affected files:**
- `src/ui/base.py`

**Details:**
base.py docstring mentions multiple terms for the same concept:

"Future/potential backend types (not yet implemented):
- WebBackend: Browser-based interface
- BatchBackend: Non-interactive execution mode for running programs from command line
  (Note: 'headless' typically means no UI, which seems contradictory to UIBackend purpose;
  batch/non-interactive execution may be better handled outside the UIBackend abstraction)"

Uses both "BatchBackend" and "headless" to describe similar concepts, with a note questioning whether this even belongs in UIBackend. This creates confusion about the intended architecture.

---

#### Code vs Comment conflict

**Description:** Comment about prefix stripping is overly detailed and potentially confusing

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
In _create_setting_widget() method:

"# Create display label (strip 'force_' prefix from beginning for cleaner display)
# Note: Both removeprefix() and the fallback [6:] only strip from the beginning,
# ensuring we don't modify 'force_' appearing elsewhere in the string"

The comment emphasizes that both methods only strip from the beginning, but this is obvious from the code (removeprefix() by definition only removes prefix, and [6:] only removes first 6 chars). The comment seems to defend against a non-existent concern.

Later in _on_reset():
"# Note: Compares actual value (stored in _actual_value) not display label
# since display labels have 'force_' prefix stripped (see _create_setting_widget)"

This is helpful context, but the earlier comment's defensive tone about "elsewhere in the string" is unnecessary.

---

#### Documentation inconsistency

**Description:** Inconsistent command naming between CLI and curses for same functionality

**Affected files:**
- `src/ui/cli_keybindings.json`
- `src/ui/curses_keybindings.json`

**Details:**
CLI uses command-style keybindings:
- "run": {"keys": ["RUN"]}
- "new": {"keys": ["NEW"]}
- "save": {"keys": ["SAVE \"file\""]}
- "open": {"keys": ["LOAD \"file\""]}
- "quit": {"keys": ["SYSTEM"]}

Curses uses Ctrl key combinations:
- "run": {"keys": ["Ctrl+R"]}
- "new": {"keys": ["Ctrl+N"]}
- "save": {"keys": ["Ctrl+V"]}
- "open": {"keys": ["Ctrl+O"]}
- "quit": {"keys": ["Ctrl+Q"]}

While this is expected (different UIs have different interaction models), the JSON structure uses the same action names ("run", "new", etc.) which could cause confusion when trying to understand which keybinding applies to which UI.

---

#### Code vs Documentation inconsistency

**Description:** STACK command not documented in keybindings

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/cli_keybindings.json`

**Details:**
cli_debug.py implements cmd_stack() which "Shows current GOSUB call stack and FOR loop stack."

This command is not present in cli_keybindings.json at all.

---

#### Documentation inconsistency

**Description:** Module docstring describes purpose but doesn't mention which UI backends use it

**Affected files:**
- `src/ui/capturing_io_handler.py`

**Details:**
Module docstring: "This module provides a simple IO handler that captures output to a buffer, used by various UI backends for executing commands and capturing their output."

It says "various UI backends" but doesn't specify which ones. Based on the file structure, this appears to be used internally but the documentation doesn't clarify the relationship to CLIBackend, CursesBackend, etc.

---

#### code_vs_comment

**Description:** Comment about target_column default value doesn't match actual column calculation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress() method comment:
"Note: Methods like _sort_and_position_line use a default target_column of 7,
which assumes typical line numbers (status=1 char + number=5 digits + space=1 char)."

But the calculation '1 + 5 + 1 = 7' assumes fixed 5-digit line numbers. Since line numbers are variable width, the actual code start position varies. For line 10, it would be at column 4 (status=1 + '10'=2 + space=1), not column 7.

---

#### code_vs_comment

**Description:** Comment about line 0 edge case doesn't match actual BASIC line number constraints

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_syntax_errors() method:
"# Note: line_number > 0 check handles edge case of line 0 (if present)"

But BASIC line numbers typically start at 1, and the auto-numbering code uses self.auto_number_start which defaults to 10. Line 0 would be invalid in standard BASIC. The comment suggests line 0 is a valid edge case, but the code doesn't explicitly validate or reject it.

---

#### code_vs_comment

**Description:** Bug fix comment references wrong behavior about next_auto_line_num

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_display() method:
"# DON'T increment counter here - that happens only on Enter
# Bug fix: Incrementing here caused next_auto_line_num to advance prematurely,
# displaying the wrong line number before the user typed anything"

But the code in keypress() for Enter DOES increment next_auto_line_num:
self.next_auto_line_num = next_num + self.auto_number_increment

The comment suggests incrementing in _update_display() was the bug, but doesn't clarify that incrementing DOES happen elsewhere (in keypress). This could be confusing for future maintainers.

---

#### code_vs_comment

**Description:** Comment says _create_toolbar is 'UNUSED' but provides detailed explanation that could be misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~260 states:
STATUS: UNUSED - not called anywhere in current implementation.

The toolbar was removed from the UI in favor of Ctrl+U menu for better keyboard navigation. This fully-implemented method is retained for reference in case toolbar functionality is desired in the future. Can be safely removed if no plans to restore.

This is accurate documentation of unused code, but the phrase 'Can be safely removed if no plans to restore' suggests uncertainty about whether to keep it. This is more of a TODO/decision item than a pure comment.

---

#### code_vs_comment

**Description:** Comment about interpreter lifecycle is verbose and potentially confusing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at lines ~160-168 provides extensive explanation:
# Interpreter Lifecycle:
# Created ONCE here in __init__ and reused throughout the session.
# The interpreter object itself is NEVER recreated - the same instance is used
# for the lifetime of the UI session.
# Note: The immediate_io handler created here is temporary - ImmediateExecutor
# will be recreated in start() with a fresh OutputCapturingIOHandler, but that
# new executor will receive this same interpreter instance (not a new interpreter).

This is accurate but overly detailed. The key point (interpreter created once, reused) is buried in repetitive explanation. The note about temporary immediate_io adds confusion since it's explaining future behavior in __init__.

---

#### code_vs_comment

**Description:** Comment about toolbar removal references Ctrl+U menu but doesn't explain why toolbar was inferior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
At line ~262:
# The toolbar was removed from the UI in favor of Ctrl+U menu for better keyboard navigation.

The comment states toolbar was removed for 'better keyboard navigation' but doesn't explain why a menu provides better keyboard navigation than toolbar buttons. Both can be keyboard-navigated. This may be accurate but lacks justification.

---

#### code_vs_comment

**Description:** Comment about main widget storage strategy is inconsistent with actual implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _activate_menu() comment:
'Main widget storage: Unlike _show_help/_show_keymap/_show_settings which close existing overlays first (and thus can use self.base_widget directly), this method extracts base_widget from self.loop.widget to unwrap any existing overlay.'

But _show_help() does NOT close existing overlays first - it directly uses self.base_widget:
'overlay = urwid.Overlay(
    urwid.AttrMap(help_widget, 'body'),
    self.base_widget,  # Uses self.base_widget directly
    ...'

The comment claims _show_help closes overlays first, but the code shows it just uses self.base_widget directly without any closing logic.

---

#### code_vs_comment

**Description:** Comment about statement-level precision uses inconsistent terminology

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_stack_window():
'# Show statement-level precision for GOSUB return address
# return_stmt is statement offset (0-based index): 0 = first statement, 1 = second, etc.'

But later in the same function for FOR loops:
'stmt = entry.get('stmt', 0)'

The comment uses 'return_stmt' for GOSUB but the code uses 'stmt' for FOR/WHILE. The terminology is inconsistent - both refer to statement offsets but use different variable names without explanation.

---

#### code_vs_comment

**Description:** Comment about overlay closing behavior in _show_keymap is misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment in _show_keymap():
'Main widget storage: Uses self.base_widget (stored at UI creation time in __init__) rather than self.loop.widget (which reflects the current widget and might be a menu or other overlay). Same approach as _show_help and _show_settings.'

But _show_keymap has toggle behavior:
'# Check if keymap is already open (toggle behavior)
if hasattr(self, '_keymap_overlay') and self._keymap_overlay:
    # Close keymap'

While _show_help does NOT have this toggle check - it just creates a new overlay. The comment claims 'same approach' but the implementations differ significantly.

---

#### code_vs_comment

**Description:** Comment mentions duplicated CapturingIOHandler definition but then imports it from shared location

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _execute_immediate method:
Comment says: "# Need to create the CapturingIOHandler class inline
# (duplicates definition in _run_program - consider extracting to shared location)
# Import shared CapturingIOHandler"

The comment suggests it needs to be created inline and duplicates another definition, but then immediately imports it from a shared module. The comment is outdated - the extraction to shared location has already been done.

---

#### code_vs_comment

**Description:** Comment in _on_autosave_recovery_response mentions filtering blank lines but the logic filters lines with no code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment says: "# Filter out blank lines (lines with only line number, no code)"

Code does:
"if code:
    lines.append(line)"

The comment says 'blank lines' but the code filters lines where code.strip() is empty after extracting it. These are lines with line numbers but no code, not truly blank lines (which would have no line number either). The comment is slightly imprecise.

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

#### Code vs Comment conflict

**Description:** Comment about link tag prefixes is incomplete

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Line 632 comment states:
Note: Both "link_" (from _render_line_with_links) and "result_link_"
(from _execute_search) prefixes are checked. Both types are stored
identically in self.link_urls, but the prefixes distinguish their origin.

However, the code at line 636 checks for three prefixes:
for tag in tags:
    if tag.startswith("link_") or tag.startswith("result_link_"):

But earlier in the code, _render_line_with_links() creates tags with prefix "link_" (line 234), and _execute_search() creates tags with prefix "result_link_" (line 437). The comment correctly identifies these two, but the implementation in _on_link_click() at line 262 only checks for "link_" prefix, not "result_link_". This suggests either the comment is incomplete about where these prefixes are used, or there's an inconsistency in how result links are handled.

---

#### Documentation inconsistency

**Description:** Inline help display described as 'not a hover tooltip' but implementation unclear

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 169 comment states:
# Show short help as inline label (not a hover tooltip, just a gray label)

This comment clarifies that the help text is displayed as a static label, not a tooltip. However, the module docstring and other documentation don't explain this UI design choice or the distinction between short help (inline) vs long help (button with dialog). Users might expect tooltips based on common UI patterns, but the implementation deliberately avoids them. This design decision is only documented in a code comment, not in user-facing documentation.

---

#### Code vs Comment conflict

**Description:** Comment about modal behavior contradicts typical understanding of modal dialogs

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 48 comment states:
# Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())

This comment clarifies that the dialog uses grab_set() but not wait_window(), meaning it's modal for user interaction but not for code execution. However, this is a subtle distinction that might confuse developers expecting standard modal behavior. The comment is helpful but the term 'modal' is being used in a non-standard way. Typically, 'modal' implies both UI blocking and code blocking (via wait_window()). The implementation is actually 'modeless with grab', not truly modal.

---

#### Code implementation issue

**Description:** Context menu dismiss helper function defined but binding may not work as intended

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Lines 645-649 define dismiss_menu helper:
def dismiss_menu():
    try:
        menu.unpost()
    except:
        pass

Then lines 657-658 bind it:
menu.bind("<FocusOut>", lambda e: dismiss_menu())
menu.bind("<Escape>", lambda e: dismiss_menu())

However, tk.Menu widgets typically don't receive keyboard focus in the same way as other widgets, so the <FocusOut> binding may not trigger as expected. Additionally, <Escape> binding on a menu might not work because tk_popup() handles its own event loop. The implementation suggests these bindings will dismiss the menu, but they may not function reliably in practice.

---

#### code_vs_comment

**Description:** Comment about region types in _on_variable_double_click is incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_variable_double_click() (lines 1152-1154):
# Check if we clicked on a row (accept both 'tree' and 'cell' regions)
# 'tree' = first column area, 'cell' = other column areas
region = self.variables_tree.identify_region(event.x, event.y)

The comment explains 'tree' and 'cell' but doesn't mention other possible region values that identify_region() might return (e.g., 'heading', 'separator', 'nothing'). The code only checks for 'cell' and 'tree', so the comment is accurate but incomplete about the full API.

---

#### code_vs_comment

**Description:** Comment about preventing default Enter behavior is redundant

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Multiple locations in _on_enter() end with:
Comment: "return 'break'  # Prevent default Enter behavior"

This comment appears 3+ times in the same function. After the first occurrence, it's redundant since the pattern is established. This is a minor code style issue.

---

#### code_vs_comment

**Description:** Dead code comment for _setup_immediate_context_menu() references related dead code methods but doesn't explain why they're retained

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment: "DEAD CODE: This method is never called because immediate_history is always None in the Tk UI (see __init__). Retained for potential future use if immediate mode gets its own output widget. Related dead code: _copy_immediate_selection() and _select_all_immediate()."

The comment identifies dead code and related methods, but doesn't explain the design decision to keep dead code in the codebase. Typically dead code should be removed and restored from version control if needed. The 'potential future use' rationale is vague.

---

#### code_vs_comment

**Description:** _on_status_click() docstring says it shows 'confirmation message for ●' but the actual message is informational, not a confirmation

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring says:
"Handle click on status column (show error details for ?, confirmation message for ●)."

But the code shows:
messagebox.showinfo(
    f'Breakpoint on Line {line_num}',
    f'Line {line_num} has a breakpoint set.\n\nUse the debugger menu or commands to manage breakpoints.'
)

This is an informational message, not a confirmation dialog. A confirmation typically asks for user input (yes/no), but this just displays information using showinfo().

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

#### code_vs_comment

**Description:** Comment references _enable_inline_input() method that is not visible in the provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~70 references:
# by _enable_inline_input() in the NiceGUIBackend class.

This method is not shown in the provided code snippet (part 1 of nicegui_backend.py). Either the method exists in part 2 (not shown), or the comment is outdated.

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

#### code_vs_comment

**Description:** Comment in _check_auto_number describes tracking 'last edited line text' but variable name is last_edited_line_text which could be entire editor content

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says: "Tracks last edited line text to avoid re-numbering unchanged content."

But in the code:
"if current_text == self.last_edited_line_text:
    return"

The variable name suggests it's a single line, but it's being compared to current_text which is the entire editor content. The variable should be named last_editor_content or the comment should say 'last editor content'.

---

#### code_vs_comment

**Description:** Comment about CP/M EOF marker in _save_editor_to_program claims it's for consistency with file loading but doesn't reference where file loading does this

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says: "# \x1a (Ctrl+Z, CP/M EOF marker - included for consistency with file loading)"

This claims consistency with file loading but doesn't reference which method or file handles this during loading. Without the reference, it's hard to verify the consistency claim or find the related code.

---

#### code_vs_comment

**Description:** Comment says class is deprecated but provides migration guide suggesting features not shown in code

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Comment states:
'# Migration guide for code using this class:
# OLD: launcher = WebHelpLauncher(); launcher.open_help("statements/print")
# NEW: Open http://localhost/mbasic_docs/statements/print.html directly in browser
# NEW: In NiceGUI backend, use: ui.navigate.to('/mbasic_docs/statements/print.html', new_tab=True)'

But the open_help_in_browser() function at the top of the file doesn't add .html extension:
url = HELP_BASE_URL + topic

Inconsistency: migration guide says use .html extension, but actual function doesn't add it.

---

#### documentation_inconsistency

**Description:** Loop examples documentation doesn't mention EXIT FOR/EXIT WHILE are not available, but compiler docs don't clarify this either

**Affected files:**
- `docs/help/common/examples/loops.md`
- `docs/help/common/compiler/optimizations.md`

**Details:**
loops.md states:
'Note: MBASIC 5.21 does not have EXIT FOR or EXIT WHILE statements (those were added in later BASIC versions). GOTO is the standard way to exit loops early in BASIC-80.'

But optimizations.md discusses loop optimizations without mentioning this limitation. When documenting 'Loop-Invariant Code Motion' and 'Induction Variable Optimization', it should note that early exit requires GOTO, which affects optimization opportunities.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for keyboard shortcuts between documents

**Affected files:**
- `docs/help/common/editor-commands.md`
- `docs/help/common/debugging.md`

**Details:**
editor-commands.md says:
'Important: Keyboard shortcuts vary by UI. See your UI-specific help for the exact keybindings'

But debugging.md uses both 'keyboard shortcuts' and 'shortcuts' interchangeably, and also says:
'Debugging keyboard shortcuts vary by UI. See your UI-specific help for complete keyboard shortcut reference'

Should standardize on either 'keyboard shortcuts' or 'keybindings' throughout documentation.

---

#### code_vs_documentation

**Description:** Version info shows MBASIC 5.21 compatibility but compiler docs don't specify which BASIC-80 version features are compiled

**Affected files:**
- `src/version.py`
- `docs/help/common/compiler/index.md`

**Details:**
version.py states:
MBASIC_VERSION = "5.21"  # The MBASIC version we implement
COMPATIBILITY = "100% MBASIC 5.21 compatible with optional extensions"

But compiler/index.md and optimizations.md don't specify if the compiler supports all MBASIC 5.21 features or only a subset. The 'Code Generation Status: In Progress' suggests incomplete implementation, but compatibility claims are unclear.

---

#### code_vs_comment

**Description:** Function docstring says it returns bool but doesn't document what True/False means in all cases

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
open_help_in_browser() docstring:
'Returns:
    bool: True if browser opened successfully, False otherwise'

But the code shows:
result = webbrowser.open(url)
sys.stderr.write(f"webbrowser.open() returned: {result}\n")
return result

The function returns whatever webbrowser.open() returns, which according to Python docs can be True/False but behavior varies by platform. The docstring should clarify this platform-dependent behavior.

---

#### documentation_inconsistency

**Description:** Inconsistent statement about line number range

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/language.md`

**Details:**
getting-started.md states 'Numbers can be 1-65535' but language.md does not specify the valid range for line numbers. This should be consistent across both documents.

---

#### documentation_inconsistency

**Description:** Circular reference in FIX documentation

**Affected files:**
- `docs/help/common/language/functions/fix.md`
- `docs/help/common/language/functions/int.md`

**Details:**
fix.md states 'FIX(X) is equivalent to SGN(X)*INT(ABS(X))' and says 'The major difference between FIX and INT is that FIX does not return the next lower number for negative X.' However, int.md is referenced in the 'See Also' section but the actual int.md file content is not provided in the documentation set, making it impossible to verify the consistency of this explanation.

---

#### documentation_inconsistency

**Description:** Inconsistent ASCII code references

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
character-set.md has a table of control characters with codes (7=BEL, 8=BS, 9=TAB, 10=LF, 13=CR, 27=ESC) and says 'See [ASCII Codes](appendices/ascii-codes.md) for a complete reference.' The ascii-codes.md file exists and provides the complete table, but character-set.md could be clearer that it's showing a subset.

---

#### documentation_inconsistency

**Description:** Missing error code reference in EOF documentation

**Affected files:**
- `docs/help/common/language/functions/eof.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
eof.md mentions 'to avoid "Input past end" errors' but doesn't reference the error code. According to error-codes.md, this is error 62 'Input past end'. The documentation should include the error code reference for consistency.

---

#### documentation_inconsistency

**Description:** Inconsistent overflow error behavior description

**Affected files:**
- `docs/help/common/language/functions/exp.md`
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
exp.md states 'If EXP overflows, the "Overflow" error message is displayed, machine infinity with the appropriate sign is supplied as the result, and execution continues.' However, error-codes.md for error 6 (OV) states 'The result of a calculation is too large to be represented in BASIC-80's number format' without mentioning that execution continues with infinity. This behavior difference should be clarified.

---

#### documentation_inconsistency

**Description:** Example shows incorrect variable type behavior

**Affected files:**
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
In defint-sng-dbl-str.md example:
'70 AMOUNT = 100     ' String variable (starts with A, DEFSTR applies)'
This comment is incorrect. AMOUNT would be a string variable name, but assigning the numeric value 100 to it would cause a type mismatch error. The example should either use AMOUNT$ or assign a string value like '100' or clarify that this would cause an error.

---

#### documentation_inconsistency

**Description:** Missing information about readline functionality mentioned in keywords

**Affected files:**
- `docs/help/common/language/statements/input.md`

**Details:**
input.md includes 'readline' in keywords list but the documentation doesn't mention any readline functionality or line editing capabilities during INPUT. Either the keyword should be removed or the documentation should explain what readline features are available.

---

#### documentation_inconsistency

**Description:** Missing FILES statement in alphabetical listing

**Affected files:**
- `docs/help/common/language/statements/index.md`

**Details:**
index.md has a 'G' section with GET, GOSUB...RETURN, and GOTO, but the 'F' section only lists FIELD and FOR...NEXT. The FILES statement (documented in files.md) is missing from the alphabetical listing, though it appears in the 'File Management' category section.

---

#### documentation_inconsistency

**Description:** Incorrect title formatting

**Affected files:**
- `docs/help/common/language/statements/input_hash.md`

**Details:**
input_hash.md has title 'INPUT# (File)' with parenthetical, while other file I/O statements like printi-printi-using.md use 'PRINT# (File)' format. However, the filename is input_hash.md (with underscore) while the syntax shows 'INPUT#' (with hash). This inconsistency in naming could cause confusion.

---

#### documentation_inconsistency

**Description:** LINE INPUT# documentation has inconsistent keyword list

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
The keywords list includes 'inputi' which is the filename, not a BASIC keyword:
keywords: ['close', 'command', 'data', 'field', 'file', 'for', 'if', 'input', 'inputi', 'line']

'inputi' should not be in the keywords list as it's not a valid BASIC statement or keyword.

---

#### documentation_inconsistency

**Description:** LPRINT documentation references non-existent printi-printi-using.md for PRINT#

**Affected files:**
- `docs/help/common/language/statements/lprint-lprint-using.md`

**Details:**
In lprint-lprint-using.md 'See Also' section:
- [PRINT#](printi-printi-using.md) - To write data to a sequential disk file

This creates a circular reference since the current file IS printi-printi-using.md. The reference should point to itself or be removed.

---

#### documentation_inconsistency

**Description:** Inconsistent spacing in 'See Also' references

**Affected files:**
- `docs/help/common/language/statements/list.md`
- `docs/help/common/language/statements/llist.md`

**Details:**
In list.md:
- [AUTO](auto.md) - To generate a line number   automatically     after every carriage return

In llist.md:
- [AUTO](auto.md) - To generate a line number   automatically     after every carriage return

Both have excessive spacing between 'number' and 'automatically' and between 'automatically' and 'after'. This appears to be a formatting error.

---

#### documentation_inconsistency

**Description:** MERGE documentation has inconsistent spacing in title

**Affected files:**
- `docs/help/common/language/statements/merge.md`

**Details:**
The description field has extra spaces:
"To merge a specified disk file into the      program currently in memory"

Should be:
"To merge a specified disk file into the program currently in memory"

---

#### documentation_inconsistency

**Description:** PRINT documentation has inconsistent alias format

**Affected files:**
- `docs/help/common/language/statements/print.md`

**Details:**
The print.md file has:
aliases: ['?']

But in the Remarks section it says:
"? - Shorthand for PRINT"

The alias is documented but the format in the frontmatter uses an array while other files don't have this field. This is inconsistent with other statement documentation files.

---

#### documentation_inconsistency

**Description:** MID$ Assignment documentation has inconsistent related field format

**Affected files:**
- `docs/help/common/language/statements/mid-assignment.md`

**Details:**
The mid-assignment.md file has:
related: ['mid_dollar', 'left_dollar', 'right_dollar']

This uses a 'related' field instead of the standard 'See Also' section used by other documentation files. While the content is in the 'See Also' section, the frontmatter field name is inconsistent.

---

#### documentation_inconsistency

**Description:** LSET documentation has inconsistent related field format

**Affected files:**
- `docs/help/common/language/statements/lset.md`

**Details:**
The lset.md file has:
related: ['rset', 'field', 'get', 'put', 'open']

This uses a 'related' field instead of the standard 'See Also' section format used by other documentation files. While the content is in the 'See Also' section, the frontmatter field name is inconsistent.

---

#### documentation_inconsistency

**Description:** ON...GOSUB/ON...GOTO documentation has incomplete example

**Affected files:**
- `docs/help/common/language/statements/on-gosub-on-goto.md`

**Details:**
The example section only shows:
100 ON L-1 GOTO 150,300,320,390

This is incomplete - it doesn't show what L is, what happens at those line numbers, or demonstrate the ON...GOSUB variant mentioned in the title. Other documentation files typically provide more complete, runnable examples.

---

#### documentation_inconsistency

**Description:** Keyword overlap in 'keywords' field: Both RESTORE and RESET use 'reset' as a keyword, which could cause confusion in search/indexing.

**Affected files:**
- `docs/help/common/language/statements/restore.md`
- `docs/help/common/language/statements/reset.md`

**Details:**
RESTORE.md keywords: ['restore', 'data', 'read', 'reset', 'pointer']
RESET.md keywords: ['reset', 'close', 'file', 'disk', 'buffer']

Both documents include 'reset' in their keywords array, but they describe completely different operations (DATA pointer vs file closing).

---

#### documentation_inconsistency

**Description:** Similar command names with different purposes could benefit from cross-reference warnings like RESET/RSET have.

**Affected files:**
- `docs/help/common/language/statements/resume.md`
- `docs/help/common/language/statements/restore.md`

**Details:**
RESUME (error handling) and RESTORE (DATA pointer) have similar names but completely different purposes. Unlike RESET/RSET which warn about confusion, these don't have similar warnings despite potential for confusion.

---

#### documentation_inconsistency

**Description:** File extension handling inconsistency: SAVE mentions CP/M default .BAS extension, RUN mentions default but doesn't specify CP/M.

**Affected files:**
- `docs/help/common/language/statements/save.md`
- `docs/help/common/language/statements/run.md`

**Details:**
SAVE.md: "(With CP/M, the default extension .BAS is supplied.)"

RUN.md: "File extension defaults to .BAS if not specified"

RUN should also mention this is CP/M-specific behavior, or both should clarify if this applies to all versions or just CP/M.

---

#### documentation_inconsistency

**Description:** Settings documentation doesn't mention HELPSETTING command consistently.

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
setsetting.md See Also: "- [SHOWSETTINGS](showsettings.md) - Display current interpreter settings
- [HELPSETTING](helpsetting.md) - Display help for a specific setting"

showsettings.md See Also: "- [SETSETTING](setsetting.md) - Configure interpreter settings at runtime
- [HELPSETTING](helpsetting.md) - Display help for a specific setting"

settings.md mentions HELPSETTING in CLI section but doesn't have it in the main "Available commands" list:
"**Available commands:**
- [SHOWSETTINGS](language/statements/showsettings.md) - Display current settings
- [SETSETTING](language/statements/setsetting.md) - Change a setting value
- [HELPSETTING](language/statements/helpsetting.md) - Get help for a setting"

Actually, settings.md DOES list it. This is not an inconsistency. Retracting this item.

---

#### documentation_inconsistency

**Description:** Shortcuts documentation uses placeholder syntax {{kbd:...}} that appears to be a template system, but no documentation explains what this syntax means or how it's processed.

**Affected files:**
- `docs/help/common/shortcuts.md`

**Details:**
shortcuts.md contains entries like:
"| **Run program** | {{kbd:run:cli}} | {{kbd:run:curses}} | {{kbd:run_program:tk}} | {{kbd:run:web}} |"

This appears to be a template/macro system for keyboard shortcuts, but there's no explanation of:
1. What the {{kbd:...}} syntax means
2. How it gets processed/rendered
3. What the actual keyboard shortcuts are
4. Whether this is documentation for developers or end users

---

#### documentation_inconsistency

**Description:** Inconsistent 'related' field usage: Some statements have it, others don't, with no clear pattern.

**Affected files:**
- `docs/help/common/language/statements/swap.md`
- `docs/help/common/language/statements/while-wend.md`

**Details:**
swap.md has related: ['lset', 'field', 'get', 'put', 'open'] in rset.md
swap.md has related: ['let'] 
while-wend.md has related: ['for-next', 'if-then-else-if-goto', 'goto']

Many other statement docs don't have a 'related' field at all. There should be consistency - either all statements should have related links, or there should be clear criteria for when to include them.

---

#### documentation_inconsistency

**Description:** Vague reference to 'some Tk configurations'

**Affected files:**
- `docs/help/common/ui/tk/index.md`

**Details:**
Tk docs state 'Some Tk configurations include an immediate mode panel' without clarifying:
1. Which configurations have this feature
2. How to enable/disable it
3. Whether it's a compile-time or runtime option
This creates uncertainty about feature availability.

---

#### documentation_inconsistency

**Description:** Auto-save behavior inconsistency

**Affected files:**
- `docs/help/mbasic/extensions.md`

**Details:**
Extensions.md states 'Auto-save behavior varies by UI' and lists CLI, Tk, Curses as 'Save to local filesystem (persistent)' but doesn't explain what 'auto-save' means. None of the UI-specific docs (cli/index.md, tk/index.md, curses/editing.md) mention auto-save functionality. This suggests either:
1. Auto-save is not actually implemented
2. It's implemented but undocumented in UI docs
3. The term means something different than expected

---

#### documentation_inconsistency

**Description:** Typo in example creates confusion

**Affected files:**
- `docs/help/common/ui/curses/editing.md`

**Details:**
Curses editing docs show an example of a typo: '1O PRINT "Oops"   ← Letter O instead of zero' and states 'Creates a new variable 1O (syntax error)!'. However, this is contradictory - if it creates a variable, it's not a syntax error. The example likely means it would be parsed as a variable assignment attempt, which would fail. The explanation needs clarification.

---

#### documentation_inconsistency

**Description:** Inconsistent function count - features.md says '50+' but not-implemented.md implies different count

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md states: 'Functions (50+)' and lists categories of functions.

not-implemented.md has a 'String Enhancements' section listing functions from 'Later BASIC' that aren't in MBASIC 5.21, but doesn't provide a definitive count of what IS available.

The '50+' claim should be verifiable against the actual function list, but no comprehensive enumeration is provided in either document.

---

#### documentation_inconsistency

**Description:** CLS implementation status unclear

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md does not explicitly list CLS in the 'Program Control' or 'Input/Output' sections.

not-implemented.md states: 'Note: Basic CLS (clear screen) IS implemented in MBASIC - see [CLS](../common/language/statements/cls.md). The GW-BASIC extended CLS with optional parameters is not implemented.'

This creates confusion - CLS should be listed in features.md if it's implemented, but it's only mentioned in the 'not-implemented' document as a clarification.

---

#### documentation_inconsistency

**Description:** Semantic analyzer optimization count mismatch in description

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md states: 'The interpreter includes an advanced semantic analyzer with 18 optimizations:' and then lists exactly 18 numbered items (1-18).

This is internally consistent, but should be verified against actual implementation to ensure all 18 are actually implemented.

---

#### documentation_inconsistency

**Description:** GET/PUT statement ambiguity

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md under 'File I/O' lists: 'Random files: FIELD, GET, PUT, LSET, RSET'

not-implemented.md under 'Graphics (Not in MBASIC 5.21)' states: 'GET/PUT - Graphics block operations (not the file I/O GET/PUT which ARE implemented)'

While this is technically consistent, the clarification in not-implemented.md suggests there might be confusion. The features.md should perhaps explicitly note 'GET/PUT (file I/O only, not graphics)' to prevent confusion.

---

#### documentation_inconsistency

**Description:** Settings commands not mentioned in features list

**Affected files:**
- `docs/help/ui/cli/settings.md`
- `docs/help/mbasic/features.md`

**Details:**
cli/settings.md documents SHOWSETTINGS and SETSETTING commands as part of CLI functionality.

features.md does not mention these commands in any section (not in 'Direct Commands', 'Program Control', or 'CLI Mode' sections).

If these are CLI-specific commands, they should be mentioned in the CLI Mode section of features.md.

---

#### documentation_inconsistency

**Description:** CLI mode invocation inconsistency

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/ui/cli/index.md`

**Details:**
getting-started.md shows CLI mode started with: 'mbasic --ui cli'

cli/index.md shows: 'mbasic --ui cli' in the Quick Start section.

Both are consistent, but getting-started.md also shows 'mbasic' without arguments starts Curses UI, while cli/index.md doesn't clarify this distinction. Users might be confused about when CLI vs Curses is the default.

---

#### documentation_inconsistency

**Description:** Missing Web UI documentation link

**Affected files:**
- `docs/help/mbasic/index.md`

**Details:**
index.md lists 'UI-Specific Guides' with links to Curses, CLI, and Tk, but no link to Web UI documentation despite Web UI being mentioned elsewhere.

The 'See Also' section at bottom also lists: 'Curses UI Guide', 'CLI Guide', 'Tk GUI Guide' but no Web UI Guide.

Either Web UI documentation doesn't exist (and shouldn't be mentioned in features.md), or it exists and should be linked here.

---

#### documentation_inconsistency

**Description:** Statement count not provided

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md mentions 'All 63 statements' in the Language Reference quick link section of getting-started.md and cli/index.md.

However, features.md itself doesn't provide a count of implemented statements, only categories.

not-implemented.md lists many statements that are NOT in MBASIC 5.21, but doesn't confirm the '63 statements' count.

The count should be verifiable and consistent across all documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for Save command

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
docs/help/ui/curses/feature-reference.md states: 'Save File ({{kbd:save:curses}})' and 'Note: Uses {{kbd:save:curses}} because {{kbd:save:curses}} is reserved for terminal flow control.'

This appears to be a template variable that wasn't properly expanded, showing the same placeholder twice. The second instance should likely show Ctrl+S.

docs/help/ui/curses/quick-reference.md clarifies: '**{{kbd:save:curses}}** | Save program (Ctrl+S unavailable - terminal flow control)'

The feature-reference.md needs correction to properly explain which key is used vs which is unavailable.

---

#### documentation_inconsistency

**Description:** Inconsistent information about Cut/Copy/Paste availability

**Affected files:**
- `docs/help/ui/curses/editing.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/editing.md states: '**Note:** Cut/Copy/Paste operations are not available in the Curses UI due to keyboard shortcut conflicts. Use your terminal's native clipboard functions instead (typically Shift+Ctrl+C/V or mouse selection).'

However, docs/help/ui/curses/feature-reference.md provides more detailed explanation: 'Standard clipboard operations are not available in the Curses UI due to keyboard shortcut conflicts:
- **{{kbd:stop:curses}}** - Used for Stop/Interrupt (cannot be used for Cut)
- **{{kbd:continue:curses}}** - Terminal signal to exit program (cannot be used for Copy)
- **{{kbd:save:curses}}** - Used for Save File (cannot be used for Paste; {{kbd:save:curses}} is reserved by terminal for flow control)'

The feature-reference provides more technical detail about why each shortcut is unavailable, which should be consistent across both documents.

---

#### documentation_inconsistency

**Description:** Placeholder documentation conflicts with detailed UI-specific documentation

**Affected files:**
- `docs/help/ui/common/running.md`
- `docs/help/ui/curses/running.md`

**Details:**
docs/help/ui/common/running.md is marked as '**Status:** PLACEHOLDER - Documentation in progress' and says 'For UI-specific instructions: - CLI: `docs/help/ui/cli/` - Curses: `docs/help/ui/curses/running.md`'

However, docs/help/ui/curses/running.md is a complete, detailed guide with full documentation. The common/running.md placeholder should either be removed or updated to reference the complete UI-specific docs properly.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut for stopping execution

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/variables.md`

**Details:**
docs/help/ui/curses/quick-reference.md under 'Debugger (when program running)' states: '**{{kbd:stop:curses}}** | Stop execution'

However, docs/help/ui/curses/variables.md under 'Window Controls' states: '**{{kbd:stop:curses}}**: Close window'

The same keyboard shortcut ({{kbd:stop:curses}}) is documented as both stopping program execution and closing the variables window. This is likely a documentation error in variables.md.

---

#### documentation_inconsistency

**Description:** Missing Settings keyboard shortcut in quick reference

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/settings.md`

**Details:**
docs/help/ui/curses/quick-reference.md under 'Global Commands' states: '**Menu only** | Settings'

However, docs/help/ui/curses/settings.md clearly states: '**Keyboard shortcut:** `Ctrl+,`'

The quick reference should include this keyboard shortcut instead of marking it as 'Menu only'.

---

#### documentation_inconsistency

**Description:** Inconsistent sort direction toggle key documentation

**Affected files:**
- `docs/help/ui/curses/variables.md`

**Details:**
docs/help/ui/curses/variables.md has two different statements about toggling sort direction:

1. Under 'Sorting Options': 'Press `d` to toggle sort direction (ascending/descending).'
2. Under 'Variables Window (when visible)' table: '**d** | Toggle sort direction (ascending ↑ / descending ↓)'

While both say 'd' toggles direction, the second uses symbols (↑ / ↓) while the first uses words. This should be consistent throughout the document.

---

#### documentation_inconsistency

**Description:** Inconsistent feature count for Execution & Control

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states '## Execution & Control (6 features)' and lists:
1. Run Program
2. Stop/Interrupt
3. Continue
4. List Program
5. Renumber
6. Auto Line Numbers

But 'List Program' and 'Auto Line Numbers' are more editor features than execution control features.

---

#### documentation_inconsistency

**Description:** Inconsistent command line examples for starting UI

**Affected files:**
- `docs/help/ui/tk/index.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
index.md shows:
'mbasic --ui tk [filename.bas]'

getting-started.md shows:
'mbasic --ui tk [filename.bas]'
Or to use the default curses UI:
'mbasic [filename.bas]'

Both are consistent, but getting-started.md provides additional context about the default UI that index.md lacks.

---

#### documentation_inconsistency

**Description:** Missing implementation status note for some features

**Affected files:**
- `docs/help/ui/tk/features.md`

**Details:**
features.md describes Smart Insert, Breakpoints, Variables Window, and Execution Stack without implementation status notes, but tips.md and workflows.md include notes like:
'**Note:** Some features described below (Smart Insert, Variables Window, Execution Stack) are documented here based on the Tk UI design specifications. Check [Settings](settings.md) for current implementation status...'

This inconsistency makes it unclear which features are actually implemented in features.md.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation format

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
features.md uses placeholder notation like '{{kbd:find:web}}', '{{kbd:replace:web}}', '{{kbd:run:web}}', '{{kbd:step:web}}', etc.

However, getting-started.md uses the same notation: '{{kbd:run:web}}', '{{kbd:stop:web}}', '{{kbd:step_line:web}}', '{{kbd:step:web}}', '{{kbd:continue:web}}'.

But web-interface.md under 'Keyboard Shortcuts' uses different notation: '{{kbd:paste:web}}', '{{kbd:select_all:web}}', '{{kbd:copy:web}}'.

The notation is consistent, but it's unclear if these placeholders are meant to be replaced with actual key combinations or if they're the final format. The documentation should clarify this is a template system.

---

#### documentation_inconsistency

**Description:** Inconsistent menu structure descriptions

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
getting-started.md under 'Interface Overview > 1. Menu Bar' lists: 'File - New, Open, Save, Save As, Recent Files, Exit
Run - Run Program, Stop, Step, Continue, List Program, Show Variables, Show Stack, Clear Output
Help - Help Topics, About'.

However, web-interface.md under 'Menu Functions' lists:
'File Menu: New, Open, Clear Output' (no Save, Save As, Recent Files, Exit)
'Edit Menu: Copy, Paste, Select All, Sort Lines, Smart Insert, Settings'
'Run Menu: Run Program, Stop, Toggle Breakpoint, Clear All Breakpoints, Continue, Step Line, Step Statement'
'View Menu: Show Variables'
'Help Menu: Help'.

These are significantly different menu structures. The Edit and View menus are missing from getting-started.md, and the menu items don't match.

---

#### documentation_inconsistency

**Description:** Incomplete library index pages with missing metadata

**Affected files:**
- `docs/library/business/index.md`
- `docs/library/data_management/index.md`
- `docs/library/demos/index.md`
- `docs/library/education/index.md`
- `docs/library/electronics/index.md`

**Details:**
All library index pages (business, data_management, demos, education, electronics) list programs with empty Year and Tags fields:
'**Year:** 1980s
**Tags:**'

Only some programs have tags (e.g., 'test' tag in demos). This suggests incomplete metadata population. The 'Year: 1980s' is vague and should be more specific if known.

---

#### documentation_inconsistency

**Description:** Inconsistent description of command area behavior

**Affected files:**
- `docs/help/ui/web/index.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
index.md under 'Key Features' states: 'Command area - Execute immediate BASIC commands'.

However, getting-started.md provides much more detail: 'Command Area - Small text area labeled "Command" at the bottom with an Execute button. Use this for immediate commands that don't get added to your program'.

The index.md description is too brief and doesn't mention the Execute button or the key distinction that commands don't get added to the program.

---

#### documentation_inconsistency

**Description:** Library statistics claim 202 programs but actual count may differ

**Affected files:**
- `docs/library/index.md`

**Details:**
The index states:
**Library Statistics:**
- 202 programs from the 1970s-1980s

However, this is a static number that may not reflect the actual count of programs listed across all category pages. No verification mechanism is mentioned.

---

#### documentation_inconsistency

**Description:** Contradictory information about assembly source file location and line endings

**Affected files:**
- `docs/user/FILE_FORMAT_COMPATIBILITY.md`

**Details:**
The document states:
**Note**: Assembly source files (`.mac`) in the `docs/history/original_mbasic_src/` directory retain their original CRLF line endings because they are intended for use with the CP/M M80 assembler, which requires CRLF format.

This implies:
1. There are .mac files in docs/history/original_mbasic_src/
2. These files have CRLF line endings
3. This is intentional for CP/M compatibility

However, earlier in the same document it states that MBASIC saves ALL files with Unix line endings (LF). This creates ambiguity about whether .mac files are an exception to the general rule, and whether they are managed by MBASIC or are external reference files.

---

#### documentation_inconsistency

**Description:** Inconsistent program descriptions - some have detailed descriptions, others are minimal or missing

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
Examples of detailed descriptions:
### Bigcal2
Extended precision calculator with up to 100-digit precision for arithmetic operations

### Charfreq
Character frequency analyzer - counts occurrence of each character in text

Examples of minimal/unclear descriptions:
### Un-Prot
Fixup for ** UN.COM **

### Xextract
0 -->END PAGE / 1-20 -->EXTRACT ITEM / 21 -->RESTART

### Xscan
0 -->END PAGE / 1-20 -->DELETE ITEM / 21 -->RESTART

The last three descriptions appear to be copied from program output or menus rather than being proper descriptions of what the programs do.

---

#### documentation_inconsistency

**Description:** Web UI limitations mention 'Browser storage only' and 'No local file access' but don't explain the actual file handling mechanism

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
The Web UI limitations state:
- Browser storage only
- No local file access

But the document doesn't explain:
1. How files are actually stored (localStorage, sessionStorage, IndexedDB?)
2. Whether files persist between sessions
3. How to export/import files to/from local filesystem
4. Storage size limits

This conflicts with the 'Auto-save' feature mentioned in advantages, which implies some form of persistence.

---

#### documentation_inconsistency

**Description:** Many game entries have empty metadata fields (no description, empty tags)

**Affected files:**
- `docs/library/games/index.md`

**Details:**
Most game entries follow this pattern:
### 23Matches



**Year:** 1980s
**Tags:** 

**[Download 23matches.bas](23matches.bas)**

With no description and empty tags. Only a few entries like Calendar have actual descriptions and tags. This inconsistency makes it unclear whether:
1. The metadata is incomplete/missing
2. The programs genuinely have no additional information
3. The documentation is still being populated

---

#### documentation_inconsistency

**Description:** Auto-save status unclear for Tk UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'File Operations' table, Tk Auto-save is marked '⚠️' with note 'Tk: planned/optional, Web: automatic'. The '⚠️' symbol means 'Partially implemented' per the legend, but 'planned' suggests not yet implemented. This should be either 📋 (planned) or clarified what part is implemented vs planned.

---

#### documentation_inconsistency

**Description:** Recent files status inconsistent for Web UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'File Operations' table, Web 'Recent files' is marked '⚠️' with note 'Tk: menu, Web: localStorage'. This suggests Web has partial implementation via localStorage, but it's unclear what's missing to make it fully implemented (✅) vs partially implemented (⚠️).

---

#### documentation_inconsistency

**Description:** Keyboard shortcuts status unclear for CLI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'User Interface' table, CLI 'Keyboard shortcuts' is marked '⚠️' with note 'CLI: limited'. It's unclear what shortcuts are available vs missing. The 'Common Shortcuts' table shows CLI has shortcuts for run, stop, save, new, open, help, quit, and debugging, which seems fairly complete.

---

#### documentation_inconsistency

**Description:** Themes status unclear for Tk UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'User Interface' table, Tk 'Themes' is marked '⚠️' with note 'Web: light/dark'. This implies Tk has partial theme support, but doesn't specify what theme capabilities Tk has vs lacks.

---

#### documentation_inconsistency

**Description:** Resizable panels status unclear for Curses UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'User Interface' table, Curses 'Resizable panels' is marked '⚠️' with no note explaining what's implemented vs missing. The legend requires checking Notes column for ⚠️ entries, but no note is provided.

---

#### documentation_inconsistency

**Description:** Syntax highlighting status unclear for Curses UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In 'Editing Features' table, Curses 'Syntax highlighting' is marked '⚠️' with note 'Curses: basic'. It's unclear what 'basic' means - which syntax elements are highlighted vs not highlighted.

---


## Summary

- Total issues found: 485
- Code/Comment conflicts: 234
- Other inconsistencies: 251
- Ignored (already reviewed): 208
