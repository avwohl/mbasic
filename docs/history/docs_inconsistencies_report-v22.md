# Enhanced Consistency Report (Code + Documentation)

Generated: 2025-11-10 18:33:30
Analyzed: Source code (.py, .json) and Documentation (.md)

## 🔧 Code vs Comment Conflicts


## 📋 General Inconsistencies

### 🔴 High Severity

#### documentation_inconsistency

**Description:** Contradictory information about FileIO integration status and filesystem abstraction architecture

**Affected files:**
- `src/codegen_backend.py`
- `src/editing/manager.py`

**Details:**
codegen_backend.py states: "See src/file_io.py for planned filesystem abstraction that would support configurable compiler locations and cross-platform paths."

However, manager.py provides extensive documentation claiming FileIO is a "Planned improvement" with detailed architecture:
- "FileIO (src/file_io.py) - Abstraction layer for cross-platform support"
- "RealFileIO: direct filesystem access for local UIs"
- "SandboxedFileIO: in-memory virtual filesystem for web UI (not yet integrated)"

This creates confusion about whether FileIO exists as a planned feature or is already implemented. The codegen_backend.py comment suggests it's planned, while manager.py describes it as if it's an existing module with specific classes.

---

#### code_comment_conflict

**Description:** Comment claims negative STEP loops are a limitation, but code doesn't handle them at all

**Affected files:**
- `src/codegen_backend.py`

**Details:**
In _generate_for method, comment states:
"# LIMITATION: Currently only handles positive steps correctly
# Negative steps (e.g., FOR I = 10 TO 1 STEP -1) would generate incorrect C code
# and loop indefinitely. This is a known limitation that requires runtime step detection."

However, the code immediately after always uses '<=' comparison:
comp = '<='

This means:
1. Positive steps work correctly (as documented)
2. Negative steps generate syntactically valid C code that loops infinitely (as documented)
3. But there's no attempt to detect or warn about negative steps
4. The comment says "requires runtime step detection" but the code doesn't even attempt compile-time detection

The comment accurately describes the limitation, but the code could at least detect constant negative steps at compile time and issue a warning.

---

#### Code vs Documentation inconsistencies

**Description:** SandboxedFileIO.list_files() documentation claims it catches exceptions from list_files() itself, but code shows it doesn't

**Affected files:**
- `src/file_io.py`

**Details:**
Documentation in SandboxedFileIO.list_files() docstring:
"Catches exceptions during listing and size retrieval, returning (filename, None, False)
for files that can't be stat'd. Note: Does not catch exceptions from list_files()
itself - only from size lookups within the loop."

But the code shows:
```python
try:
    files = self.backend.sandboxed_fs.list_files(pattern)
except Exception:
    # If list_files() itself fails, return empty list
    return []
```

The code DOES catch exceptions from list_files() itself and returns empty list, contradicting the docstring that says it doesn't catch those exceptions.

---

#### code_vs_comment_conflict

**Description:** Comment claims INPUT statement fails at parse time, but code implementation shows it fails at runtime

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In OutputCapturingIOHandler.input() method:

Comment says: "INPUT statement not supported in immediate mode - fails at parse time."

But the docstring below says: "User-facing behavior: INPUT statement will fail at runtime in immediate mode. NOT at parse time - INPUT statements parse successfully but execution fails when the interpreter calls this input() method during statement execution."

The code raises RuntimeError when input() is called, which is runtime behavior, not parse-time. The first comment line contradicts the detailed docstring.

---

#### code_vs_comment

**Description:** Comment about ERL renumbering describes intentional deviation but may be incorrect

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~1000 in _renum_erl_comparison() says:
'MBASIC 5.21 Manual Specification: When ERL appears on the left side of a comparison operator (=, <>, <, >, <=, >=), the right-hand number is treated as a line number reference and should be renumbered.'

Then: 'INTENTIONAL DEVIATION FROM MANUAL: This implementation renumbers for ANY binary operator with ERL on left, including arithmetic operators (ERL + 100, ERL * 2, etc.), not just comparison operators.'

And: 'Known limitation: Arithmetic like "IF ERL+100 THEN..." will incorrectly renumber the 100 if it happens to be an old line number. This is rare in practice.'

This is a significant semantic deviation that could break valid programs. The comment acknowledges it's incorrect behavior but justifies it as 'conservative'. This needs human review to determine if this tradeoff is acceptable or if the implementation should be fixed to match the manual.

---

#### code_vs_comment

**Description:** Comment in execute_clear states 'Only OS-level file errors are silently ignored' but the exception handling catches both OSError and IOError, which in Python 3 are the same (IOError is alias for OSError)

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~430:
# Note: Only OS-level file errors are silently ignored to match MBASIC behavior.
# In Python 3, IOError is an alias for OSError, so we catch both for compatibility.
# This differs from RESET which allows errors to propagate.
# We intentionally do NOT catch all exceptions (e.g., AttributeError) to avoid
# hiding programming errors.
for file_num in list(self.runtime.files.keys()):
    try:
        file_obj = self.runtime.files[file_num]
        if hasattr(file_obj, 'close'):
            file_obj.close()
    except (OSError, IOError):
        # Silently ignore OS-level file close errors (e.g., already closed, permission denied)
        pass

The comment correctly notes IOError is an alias in Python 3, making the tuple (OSError, IOError) redundant. However, this is not an inconsistency - it's defensive coding for Python 2/3 compatibility or clarity. The comment accurately describes the code.

---

#### code_vs_comment

**Description:** serialize_let_statement docstring contradicts design claim about AST representation

**Affected files:**
- `src/position_serializer.py`

**Details:**
The serialize_let_statement docstring states:
"Design decision: LetStatementNode represents both explicit LET statements and implicit assignments in the AST. This serializer intentionally ALWAYS outputs the implicit assignment form (A=5) without the LET keyword, regardless of the original source.

Rationale:
- The AST intentionally does not distinguish between explicit LET and implicit assignment forms, as they are semantically equivalent (by design, not limitation)"

However, this contradicts the module-level docstring which says:
"Exception: Some statements intentionally normalize output for semantic equivalence:
- LET statements are always serialized without the LET keyword (implicit form) since explicit LET and implicit assignment are semantically identical in MBASIC 5.21. This represents a deliberate design choice, not a limitation."

The contradiction is subtle: the method docstring claims the AST 'does not distinguish' between forms, but if that were true, the serializer wouldn't need to make a choice - the AST would already have lost the information. The reality is likely that the AST COULD preserve the distinction but the serializer CHOOSES not to output it. This is a documentation accuracy issue.

---

#### code_vs_comment

**Description:** Architecture note claims both systems should read from same settings but SimpleKeywordCase doesn't read settings at all

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
Comment says: "Note: Both systems SHOULD read from the same settings.get('keywords.case_style') setting for consistency. SimpleKeywordCase receives policy via __init__ parameter (caller should pass settings value), while KeywordCaseManager reads settings directly."

This creates a critical inconsistency risk: SimpleKeywordCase depends on caller to pass correct settings value, but there's no enforcement or validation. If caller passes wrong value or settings change between lexer and parser phases, the two systems will be inconsistent. The comment acknowledges this risk but doesn't provide a solution.

---

#### code_vs_comment

**Description:** Comment claims syntax checking happens 'only on special keys' but FAST PATH bypasses ALL editor processing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress() method (lines ~225-230): "# FAST PATH: For normal printable characters, bypass editor-specific processing
# (column protection, line number tracking, focus management) for responsive typing.
# Note: Syntax checking only happens on special keys (below), not during normal typing."

Followed by (lines ~233-235): "# For special keys (non-printable), we DO process them below to handle
# cursor navigation, protection of status column, etc."

However, the FAST PATH (line ~230) returns immediately: 'return super().keypress(size, key)' which bypasses ALL processing including syntax checking. The comment says syntax checking happens on special keys, but the code shows it ONLY happens on control/navigation keys (line ~250), not all special keys. Keys like backspace, delete are 'special' but may not trigger syntax checking based on the conditions.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC when running and not paused at breakpoint, but code logic appears inverted

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1050 states:
"PC handling:
- If running (and not paused at breakpoint): Preserves PC to resume correctly
- If paused at breakpoint: Resets PC to halted to avoid accidental resumption"

But the code at line ~1075 does:
if self.running and not self.paused_at_breakpoint:
    self.runtime.pc = old_pc
else:
    self.runtime.pc = PC.halted_pc()

This matches the comment, but the rationale comment says "When paused at a breakpoint, resetting PC prevents accidental resumption from the wrong location (when user continues via _debug_continue(), the interpreter maintains correct PC)." This suggests the interpreter has its own PC state during breakpoint pause, making the reset here potentially problematic if the interpreter's PC isn't synchronized.

---

#### code_vs_comment_conflict

**Description:** Comment claims help navigation keys are hardcoded and not loaded from keybindings JSON, but code actually does load keybindings via HelpMacros

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~73 states:
"Note: Help navigation keys are HARDCODED (not loaded from keybindings JSON) to avoid circular dependency issues. The help widget uses fixed keys (U for back, / for search, ESC/Q to exit) that work regardless of user keybinding customization.

Note: HelpMacros (instantiated below) DOES load keybindings from JSON, but only for macro expansion in help content ({{kbd:action}} substitution). The help widget's own navigation doesn't consult those loaded keybindings - it uses hardcoded keys."

However, the code at line ~67 does:
self.macros = HelpMacros('curses', help_root)

And HelpMacros.__init__ (help_macros.py line ~23) calls:
self.keybindings = self._load_keybindings()

Which loads keybindings from JSON (help_macros.py line ~26-36). While the comment is correct that the help widget's keypress() method uses hardcoded keys, the statement that keybindings are not loaded is misleading since HelpMacros does load them.

---

#### code_vs_comment_conflict

**Description:** Maintenance comment lists incorrect line numbers for footer text updates

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at lines ~73-82 states:
"MAINTENANCE: If help navigation keys change, update:
1. All footer text assignments (search for 'self.footer' in this file - multiple locations):
   - Initial footer (line ~73 below)
   - _cancel_search() around line ~166
   - _execute_search() around lines ~185, ~204, ~212
   - _start_search() around line ~159
   - keypress() search mode around lines ~444, ~448"

These line numbers are likely outdated. The actual locations in the provided code are:
- Initial footer: line ~73 (correct)
- _cancel_search(): line ~166 (correct)
- _execute_search(): lines ~185, ~204, ~212 (need verification)
- _start_search(): line ~159 (correct)
- keypress() search mode: lines ~444, ~448 (need verification)

Without seeing the full file, some of these line numbers appear suspicious and may be from an older version.

---

#### code_vs_comment

**Description:** Comment claims ARROW_CLICK_WIDTH is for 'typical arrow icon width' but this is a hardcoded guess that may not match actual theme arrow width

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line 1001 states:
    ARROW_CLICK_WIDTH = 20  # Width of clickable arrow area in pixels (typical arrow icon width for standard Tkinter theme)

This hardcoded value of 20 pixels is described as 'typical' but Tkinter themes can vary significantly. The actual arrow width depends on the theme, DPI scaling, and platform. This could cause usability issues where users click the arrow but the code interprets it as clicking the text, or vice versa. The comment should acknowledge this is an approximation.

---

#### code_vs_comment

**Description:** Comment claims line won't be removed by _remove_blank_lines() but the logic contradicts this

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _smart_insert_line() method around line 1590:
Comment says: "# DON'T save to program yet - the line only has a line number with no statement,\n# so _save_editor_to_program() will skip it (only saves lines with statements).\n# Just position the cursor on the new line so user can start typing. The line\n# will be saved to program when:\n# 1. User types a statement and triggers _on_key_release -> _save_editor_to_program()\n# 2. User switches focus or saves the file\n# Note: This line won't be removed by _remove_blank_lines() because it contains\n# the line number (not completely blank), but it won't be saved to the program\n# until content is added."

But in _on_enter_key() method around line 1050:
Code shows: "# Check if line is just a line number with no content (e.g., '20 ')\n# This happens when Enter is pressed on the auto-generated prompt\nmatch_number_only = re.match(r'^\s*(\d+)\s*$', current_line_text)\nif match_number_only:\n    # Line has only a number, no code - remove it and don't create another blank line\n    self.editor_text.text.delete(f'{current_line_index}.0', f'{current_line_index}.end')"

The _on_enter_key() method DOES remove lines with only line numbers, contradicting the comment in _smart_insert_line().

---

#### code_vs_comment

**Description:** Comment describes _add_immediate_output() as adding to immediate output pane, but code actually adds to main output pane

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method _add_immediate_output() docstring:
"Add text to main output pane.

Note: This method name is historical/misleading - it actually adds to the main output pane, not a separate immediate output pane. It simply forwards to _add_output(). In the Tk UI, immediate mode output goes to the main output pane. self.immediate_history is always None (see __init__)."

The method name and its purpose are contradictory. If immediate_history is always None and output goes to main pane, this method should be removed or renamed to avoid confusion.

---

#### code_vs_comment

**Description:** Comment warns about maintenance risk due to code duplication but doesn't follow through with suggested refactoring

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method, comment states:
"MAINTENANCE RISK: This duplicates part of start()'s logic (see interpreter.start() in src/interpreter.py). If start() changes, this code may need to be updated to match."

And later:
"TODO: Consider refactoring start() to accept an optional parameter that allows skipping runtime.setup() for cases like RUN [line_number], reducing duplication."

This is a documented technical debt that creates maintenance burden. The comment acknowledges the problem but the code hasn't been refactored to address it.

---

#### code_vs_comment

**Description:** The _parse_line_number() docstring and inline comments claim that 'MBASIC 5.21 requires whitespace OR end-of-line between line number and statement' and that a standalone line number like '10' is valid, but the regex pattern '^(\d+)(?:\s|$)' would match '10REM' at position 0-2, extracting '10'. The comment says '10REM' is invalid but the regex doesn't enforce this.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment claims:
# Invalid examples:
#   "10REM" - no whitespace between line number and statement

But regex: match = re.match(r'^(\d+)(?:\s|$)', line_text)

The (?:\s|$) is a non-capturing group that matches whitespace OR end of string, but re.match() only needs to match at the START of the string, not consume the entire string. So '10REM' would match and extract '10', contradicting the comment that says this is invalid.

Actually, upon closer inspection: the regex DOES work correctly because (?:\s|$) requires that after the digits, there must be either whitespace or end-of-string. In '10REM', after '10' comes 'R' which is neither whitespace nor end-of-string, so the match would fail. The regex is correct.

---

#### code_vs_comment

**Description:** Comment about breakpoint storage format contradicts implementation - claims both PC objects and plain integers are supported, but code only uses PC objects

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1695 in _update_breakpoint_display(): 'Note: self.runtime.breakpoints is a set that can contain: - PC objects (statement-level breakpoints, created by _toggle_breakpoint) - Plain integers (line-level breakpoints, legacy/compatibility) This implementation uses PC objects exclusively, but handles both for robustness.'

However, examining the code:
- _toggle_breakpoint() only creates PC objects (line ~1665: 'pc = PC(line_num, stmt_offset)')
- _do_toggle_breakpoint() only creates PC objects (line ~1730: 'pc = PC(line_num, 0)')
- No code path creates plain integer breakpoints

The comment claims legacy/compatibility support for plain integers, but no code actually creates them. The 'else' branch at line ~1717 handles plain integers defensively, but they appear to be dead code.

---

#### code_vs_comment

**Description:** Critical protocol documentation in _get_input may be incorrect - claims empty string signals state transition but this is implementation-dependent

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says:
"Protocol: Returns empty string to signal interpreter state transition.

This implements a non-blocking input pattern for the web UI:
1. Show input UI by calling _enable_inline_input(prompt)
2. Return empty string immediately (non-blocking)
3. Interpreter detects empty string and transitions to 'waiting_for_input' state
4. Program execution pauses
5. When user submits via _handle_output_enter(), call interpreter.provide_input()
6. Interpreter resumes execution from waiting state

Implementation note: This relies on interpreter.input() treating empty string
as a signal to enter waiting state. If interpreter behavior changes, this
state transition protocol will break silently (program will hang)."

The comment acknowledges this is fragile ("will break silently") but documents it as a "protocol". This is dangerous - if the interpreter changes, the protocol breaks. The comment should either document this as a temporary hack or the code should use an explicit signal mechanism.

---

#### documentation_inconsistency

**Description:** Error code reference mismatch

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`
- `docs/help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
cvi-cvs-cvd.md states: 'Error: Raises "Illegal function call" (error code FC) if the string length is incorrect'. However, error-codes.md lists FC as error code 5, not as 'FC'. The documentation uses both the mnemonic code 'FC' and the numeric code '5' inconsistently. Error-codes.md shows: '| **FC** | 5 | Illegal function call |'

---

#### documentation_inconsistency

**Description:** Contradictory implementation notes for PEEK vs INP

**Affected files:**
- `docs/help/common/language/functions/peek.md`
- `docs/help/common/language/functions/inp.md`

**Details:**
PEEK.md has extensive 'Implementation Note' stating it returns random values and is NOT related to POKE: 'ℹ️ Emulated with Random Values: PEEK does NOT read actual memory. Instead, it returns a random value between 0-255 (inclusive)... PEEK does NOT return values written by POKE (POKE is a no-op that does nothing)'. However, INP.md simply states: '⚠️ Not Implemented: This feature requires direct hardware I/O port access and is not implemented... Behavior: Always returns 0'. The inconsistency is that PEEK returns random values while INP returns constant 0, despite both being unimplementable hardware access functions.

---

#### documentation_inconsistency

**Description:** FOR-NEXT loop termination test description is ambiguous and potentially contradictory

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
The documentation states:
"### Loop Termination:
The termination test happens AFTER each increment/decrement at the NEXT statement:
- **Positive STEP** (or no STEP): Loop continues while variable <= ending value
- **Negative STEP**: Loop continues while variable >= ending value"

Then provides examples:
"For example:
- `FOR I = 1 TO 10` executes with I=1,2,3,...,10 (10 iterations). After I=10 executes, NEXT increments to 11. Test condition (11 <= 10) is false, loop exits.
- `FOR I = 10 TO 1 STEP -1` executes with I=10,9,8,...,1 (10 iterations). After I=1 executes, NEXT decrements to 0. Test condition (0 >= 1) is false, loop exits."

This is confusing because it says the test happens AFTER increment, but the examples suggest the loop body executes with the final value (10 and 1 respectively) before the increment that causes the test to fail. The order of operations (execute body, increment, test vs. increment, test, execute body) is unclear.

---

#### documentation_inconsistency

**Description:** Implementation status inconsistency for line printer features

**Affected files:**
- `docs/help/common/language/statements/llist.md`
- `docs/help/common/language/statements/lprint-lprint-using.md`

**Details:**
LLIST states: '⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented'
LPRINT states: '⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented'
Both claim to be 'parsed but produces no output', but LLIST says 'Statement is parsed but produces no output' while LPRINT says 'Statement is parsed but produces no output'. The wording is identical, suggesting copy-paste, but the implementation details should be verified as consistent.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation status descriptions

**Affected files:**
- `docs/help/common/language/statements/out.md`
- `docs/help/common/language/statements/poke.md`

**Details:**
OUT: '⚠️ **Emulated as No-Op**: This feature requires direct hardware I/O port access and is not implemented'
'Behavior: Statement is parsed and executes successfully, but performs no operation'

POKE: '⚠️ **Emulated as No-Op**: This feature requires direct memory access and cannot be implemented'
'Behavior: Statement is parsed and executes successfully, but performs no operation'

Both use 'Emulated as No-Op' but OUT says 'is not implemented' while POKE says 'cannot be implemented'. The distinction between 'not implemented' vs 'cannot be implemented' should be clarified or made consistent.

---

#### documentation_inconsistency

**Description:** SETSETTING and SHOWSETTINGS are documented as statements but settings.md describes them as commands available in different UIs with different syntax

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
SETSETTING.md shows syntax: 'SETSETTING setting.name value'

SHOWSETTINGS.md shows syntax: 'SHOWSETTINGS ["pattern"]'

settings.md shows CLI usage:
'SHOWSETTINGS                    ' Show all settings
SHOWSETTINGS editor             ' Show editor settings only
SETSETTING editor.auto_number_step 100   ' Change a setting'

The settings.md examples show SHOWSETTINGS without quotes around 'editor', but the statement doc shows pattern as a quoted string. Need consistency.

---

#### documentation_inconsistency

**Description:** Self-contradictory statement about Web UI file uppercasing

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
In the Web UI section, the documentation states:
'File naming:
- Must be simple names (no slashes, no paths)
- Automatically uppercased by the virtual filesystem (CP/M style)
- 8.3 format recommended but not required
- Examples: DATA.TXT, PROGRAM.BAS, OUTPUT.DAT
- The uppercasing is a programmatic transformation for CP/M compatibility, not evidence of persistent storage'

The last bullet point appears to be defending against an accusation that wasn't made, and creates confusion by linking 'uppercasing' to 'persistent storage' when these are unrelated concepts. This seems like a defensive edit that doesn't belong in user documentation.

---

#### documentation_inconsistency

**Description:** Missing SHOWSETTINGS and SETSETTING from features list

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/settings.md`

**Details:**
features.md lists 'Direct Commands' including RUN, LIST, NEW, SAVE, LOAD, DELETE, RENUM, AUTO, BREAK, but does not mention SHOWSETTINGS or SETSETTING which are documented in cli/settings.md as available commands. These should be added to the features list or clarified as CLI-only commands.

---

#### documentation_inconsistency

**Description:** Contradictory information about variable editing capability in Curses UI

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
variables.md states: "⚠️ **Not Implemented**: You cannot edit variable values directly in the variables window." and "The variables window is read-only."

However, feature-reference.md lists under "Variable Inspection (6 features)":
"### Edit Variable Value (Not implemented)
⚠️ Variable editing is not available in Curses UI. You cannot directly edit values in the variables window. Use immediate mode commands to modify variable values instead."

Both documents agree it's not implemented, but variables.md provides more detailed workaround instructions while feature-reference.md is more concise. This is consistent but could be better cross-referenced.

---

#### documentation_inconsistency

**Description:** Conflicting information about default sort order in Variables Window

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
curses/variables.md states under "Sorting Options":
"Press `s` to cycle through sort orders:
- **Accessed**: Most recently accessed (read or written) - shown first (default)
- **Written**: Most recently written to - shown first
- **Read**: Most recently read from - shown first
- **Name**: Alphabetical by variable name"

feature-reference.md states under "Variable Sorting":
"Cycle through different sort orders:
- **Accessed**: Most recently accessed (read or written) - newest first
- **Written**: Most recently written to - newest first
- **Read**: Most recently read from - newest first
- **Name**: Alphabetically by variable name"

Both agree on the sort modes, but variables.md explicitly states "(default)" for Accessed mode while feature-reference.md does not specify which is default.

---

#### documentation_inconsistency

**Description:** Incomplete documentation with placeholder status

**Affected files:**
- `docs/help/ui/common/errors.md`
- `docs/help/ui/common/running.md`

**Details:**
common/running.md states:
"**Status:** PLACEHOLDER - Documentation in progress

This page will cover:
- How to run BASIC programs
- RUN command
- Program execution
- Stopping programs
- Continuing after STOP

## Placeholder

For now, see:
- Type `RUN` to execute the current program
- Use the Run button in GUI interfaces
- Press Ctrl+C or use STOP button to interrupt
- Type `CONT` to continue after STOP"

This is a placeholder that should be completed. Meanwhile, common/errors.md provides complete documentation about error handling, which is related to running programs. The running.md placeholder should reference errors.md for error handling during execution.

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI debugger capabilities

**Affected files:**
- `docs/help/ui/index.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
docs/help/ui/index.md comparison table states Web debugger is 'Limited' with note 'Web: breakpoints, step, basic variable inspection (planned: advanced panels, watch expressions)'. However, docs/help/ui/tk/feature-reference.md does not mention Web UI debugger limitations in its comparison context, and the Web UI debugging.md file extensively describes many features as 'planned' that the index.md suggests are already basic/implemented.

---

#### documentation_inconsistency

**Description:** Missing keyboard shortcut for Search Help feature

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md lists 'Search Help' under 'Help System (4 features)' and states: '**Note:** Search function is available via the help browser's search box (no dedicated keyboard shortcut).'

However, features.md does not mention Search Help at all in its 'Find and Replace' or other sections. The feature-reference.md claims 4 help features but only documents Help Command (F1), Integrated Docs, Search Help, and Context Help (Shift+F1). The inconsistency is that Search Help is documented in feature-reference.md but completely absent from features.md.

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI debugger implementation status

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/index.md`

**Details:**
index.md comparison table states Web debugger is 'Limited' with note: 'Web: breakpoints, step, basic variable inspection (planned: advanced panels, watch expressions)' - suggesting basic features are implemented.

However, debugging.md extensively marks features as planned:
- '**Implementation Status:** Basic variable viewing via Debug menu is currently available. The detailed variable inspector panels, watch expressions, and interactive editing features described below are **planned for future releases** and not yet implemented.'
- '**Implementation Status:** Basic call stack viewing via Run → Show Stack menu is currently available... The advanced stack panel features described below are planned for future releases.'
- Multiple sections marked as 'Planned Features' or 'Future'

The index.md suggests more is implemented than debugging.md indicates.

---

#### documentation_inconsistency

**Description:** Contradictory information about program storage and auto-save functionality

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/settings.md`

**Details:**
features.md states under 'Local Storage > Currently Implemented': 'Program content stored in Python server memory (session-only, lost on page refresh)' and 'Recent files list (filenames only) stored in browser localStorage (persists across sessions)'. However, it also lists 'Automatic Saving (Planned)' as a future feature that 'Saves programs to browser localStorage for persistence'.

In getting-started.md, it says: 'Note: The Web UI uses browser downloads for saving program files to your computer. Auto-save of program code to browser localStorage is planned for a future release. (Note: Your editor settings ARE already saved to localStorage - see [Settings](settings.md))'

In settings.md under 'Settings Storage', it describes two storage methods: 'Local Storage (Default)' where 'settings are stored in your browser's localStorage' and 'Redis Session Storage (Multi-User Deployments)' where 'settings are stored in Redis with per-session isolation'.

The inconsistency: features.md says program content is in server memory (session-only), but settings.md discusses localStorage and Redis for settings storage. The distinction between 'program content' vs 'settings' storage is unclear, and whether localStorage is currently used for anything beyond settings is contradictory.

---

#### documentation_inconsistency

**Description:** Settings system implementation status contradicts feature status documentation

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
INSTALL.md states under 'Feature Status':
'### What Works
- ✓ Settings system (SET, SHOW SETTINGS commands with global/project configuration files)'

SETTINGS_AND_CONFIGURATION.md has conflicting status information:
'> **Status:** The settings system is implemented and available in all UIs. Core commands (SET, SHOW SETTINGS, HELP SET) work as documented.'

But then lists multiple settings as planned:
'### interpreter.strict_mode
**Status:** 🔧 PLANNED - Not yet implemented'

'### interpreter.debug_mode
**Status:** 🔧 PLANNED - Not yet implemented'

'### ui.theme
**Status:** 🔧 PLANNED - Not yet implemented'

'### ui.font_size
**Status:** 🔧 PLANNED - Not yet implemented'

This creates confusion about what is actually implemented vs planned.

---

#### documentation_inconsistency

**Description:** Boolean value format inconsistency in SET command vs JSON

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states:
'**Type Conversion:**
- Strings: `"value"` (with quotes)
- Numbers: `5` (without quotes)
- Booleans: `true` or `false` (lowercase, no quotes in both commands and JSON files)'

But the examples show:
'```basic
SET "editor.show_line_numbers" true
```'

And:
'```json
{
  "editor.auto_number": true,
  "ui.theme": "dark"
}
```'

The note says 'no quotes in both commands and JSON files' but this is redundant since JSON booleans never have quotes. The phrasing suggests there might be a difference between command and JSON format, but there isn't. This could confuse users.

---

### 🟡 Medium Severity

#### Documentation inconsistency

**Description:** Package version number inconsistency between setup.py and ast_nodes.py docstring

**Affected files:**
- `setup.py`
- `src/ast_nodes.py`

**Details:**
setup.py line 23: version="0.99.0"
ast_nodes.py line 5: "package version 0.99.0"
Both claim 0.99.0 but setup.py comment says "99% implementation status - core complete" while ast_nodes.py says "approximately 99% implementation status". The wording differs slightly but both reference the same version.

---

#### Code vs Comment conflict

**Description:** InputStatementNode docstring describes semicolon behavior that may not match parser implementation

**Affected files:**
- `src/ast_nodes.py`

**Details:**
InputStatementNode docstring (lines 267-288) provides detailed explanation:
"Important: Semicolon placement changes meaning:
- INPUT; var → semicolon IMMEDIATELY after INPUT keyword (suppress_question=True)
  This suppresses the '?' question mark entirely
- INPUT "prompt"; var → semicolon AFTER the prompt string (suppress_question=False)
  This is parsed as: prompt="prompt", then semicolon separates the prompt from the variable
  The '?' is still added after the prompt

Parser note: The parser determines suppress_question=True only when it sees INPUT
followed directly by semicolon with no prompt expression between them."

This is very specific parser behavior documentation, but the parser code is not provided to verify this is actually implemented correctly. The comment claims the parser does this, but we cannot verify.

---

#### Code vs Comment conflict

**Description:** VariableNode type_suffix and explicit_type_suffix documentation may be inconsistent with field defaults

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode docstring (lines 1009-1038) states:
"Important: Both fields are ALWAYS present together:
- type_suffix may be non-None even when explicit_type_suffix=False (inferred from DEF statement)
- explicit_type_suffix=True should only occur when type_suffix is also non-None (the suffix was written)
- explicit_type_suffix=False + type_suffix=None means variable has default type (SINGLE) with no explicit suffix"

However, the field definitions are:
type_suffix: Optional[str] = None
explicit_type_suffix: bool = False

The docstring says "Both fields are ALWAYS present together" but the defaults allow type_suffix=None with explicit_type_suffix=False, which the docstring says means "default type (SINGLE) with no explicit suffix". This seems consistent, but the phrase "ALWAYS present together" is misleading since type_suffix can be None. The documentation should clarify that "present together" means "their values are coordinated" not "both are non-None".

---

#### code_vs_comment

**Description:** Comment in EOF() function claims mode 'I' files are opened in binary mode ('rb'), but this is not verifiable in the provided code

**Affected files:**
- `src/basic_builtins.py`

**Details:**
EOF() function comment states:
"Note: For input files (OPEN statement mode 'I'), respects ^Z (ASCII 26)
as EOF marker (CP/M style). Input files are opened in Python binary mode ('rb')
to enable ^Z detection.

Implementation details:
- execute_open() in interpreter.py stores mode ('I', 'O', 'A', 'R') in file_info['mode']
- Mode 'I' (input): Opened in Python binary mode ('rb'), allowing ^Z detection"

However, the execute_open() function is not in the provided files, so this cannot be verified. The EOF() implementation assumes binary mode but the actual file opening code is not visible.

---

#### code_vs_comment

**Description:** format_numeric_field() comment describes sign behavior but implementation for negative zero may not match all described cases

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment in format_numeric_field() states:
"Determine sign - preserve negative sign for values that round to zero.
This matches MBASIC 5.21 behavior: -0.001 rounds to 0 but displays as '-0'.
We use original_negative (captured before rounding) to detect this case,
ensuring: negative values that round to zero display '-0', positive display '0'."

The code implements:
if rounded == 0 and original_negative:
    is_negative = True
else:
    is_negative = rounded < 0

However, for trailing_minus_only format, the comment says 'reserves space for sign (displays - for negative or space for non-negative)' but the implementation adds space for positive values even when they rounded from negative to zero. This may be correct MBASIC behavior but creates subtle inconsistency in the comment's description.

---

#### code_vs_comment

**Description:** parse_numeric_field() docstring describes sign behavior but comment about leading_sign is potentially misleading

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring states:
"Sign behavior:
- leading_sign: + at start, reserves space for sign (displays + or - based on value)
- trailing_sign: + at end, reserves space for sign (displays + or - based on value)
- trailing_minus_only: - at end, reserves space for sign (displays - for negative or space for non-negative)"

However, in the code parsing section:
# Check for leading +
elif format_str[i] == '+':
    spec['leading_sign'] = True
    # Note: leading sign doesn't add to digit_count, it's a format modifier
    i += 1

The comment 'leading sign doesn\'t add to digit_count' contradicts the later code in format_numeric_field() where field_width calculation includes:
if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
    field_width += 1  # Sign takes up one position

This suggests leading_sign DOES affect field width, making the parse comment misleading.

---

#### documentation_inconsistency

**Description:** Contradictory statements about FileSystemProvider purpose and relationship to FileIO

**Affected files:**
- `src/editing/manager.py`

**Details:**
manager.py states: "Related filesystem abstractions:
1. FileSystemProvider (src/filesystem/base.py) - For runtime BASIC file I/O
   - Used during program execution (OPEN, INPUT#, PRINT#, CLOSE, etc.)
   - Separate from program loading (LOAD/SAVE which load .BAS source files)"

This implies FileSystemProvider handles runtime file I/O while FileIO handles program loading. However, the description also says FileIO would provide "RealFileIO: direct filesystem access" and "SandboxedFileIO: in-memory virtual filesystem" which sounds like it would also handle runtime file I/O. The distinction between these two filesystem abstractions is unclear.

---

#### code_comment_conflict

**Description:** Docstring claims arrays are not supported, but code has no array handling at all

**Affected files:**
- `src/codegen_backend.py`

**Details:**
Class docstring states:
"Known limitations (not yet implemented):
- String support (requires runtime library)
- Arrays
- Complex expressions beyond simple binary operations"

In _generate_variable_declarations method:
if var_info.is_array:
    # Skip arrays for now - not supported in initial implementation
    continue

This suggests arrays are partially implemented (symbol table tracks them) but code generation skips them. However, there's no warning generated when arrays are skipped, which could lead to silent failures where array variables simply don't exist in generated code.

---

#### code_comment_conflict

**Description:** Comment about math library linking doesn't match actual usage in code

**Affected files:**
- `src/codegen_backend.py`

**Details:**
In get_compiler_command method, comment states:
"# -lm links the math library for floating point support"

However, the actual command includes '-lm' flag:
return ['/snap/bin/z88dk.zcc', '+cpm', source_file, '-create-app', '-lm', '-o', output_file]

But the code only uses math.h for the pow() function (in _generate_binary_op). The comment implies -lm is needed for "floating point support" in general, but:
1. Basic float operations (+, -, *, /) don't require -lm
2. Only pow() requires -lm
3. The comment doesn't mention pow() specifically

The comment is misleading about why -lm is needed.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for program loading operations

**Affected files:**
- `src/editing/manager.py`

**Details:**
manager.py uses inconsistent terminology:

1. "program loading" vs "loading .BAS program files" vs "loading/saving .BAS program files"
2. "LOAD/SAVE commands" vs "LOAD/SAVE/MERGE commands"
3. "program loading (LOAD/SAVE which load .BAS source files)" - SAVE doesn't load

The documentation mixes loading and saving operations under "program loading" which is confusing. It should distinguish:
- Program loading: LOAD, MERGE (read .BAS files)
- Program saving: SAVE (write .BAS files)
- Program management: All file operations (LOAD/SAVE/MERGE)

---

#### Documentation inconsistencies

**Description:** Contradictory documentation about which abstraction provides list_files() and delete() for runtime use

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py states:
"FileSystemProvider (src/filesystem/base.py) - Runtime file I/O (OPEN/CLOSE/INPUT#/PRINT#)
   - Also provides: list_files() and delete() for runtime use within programs"

But src/filesystem/base.py states:
"Also provides: list_files() and delete() for runtime use
   - Purpose: File I/O from within running BASIC programs"
Then adds:
"Note: There is intentional overlap between the two abstractions.
Both provide list_files() and delete() methods, but serve different contexts:
FileIO is for interactive commands (FILES/KILL), FileSystemProvider is for
runtime access (though not all BASIC dialects support runtime file operations)."

The phrase "though not all BASIC dialects support runtime file operations" contradicts the earlier claim that FileSystemProvider provides these "for runtime use within programs".

---

#### Code vs Documentation inconsistencies

**Description:** SandboxedFileIO documentation describes mixed concerns but implementation status is inconsistent with description

**Affected files:**
- `src/file_io.py`

**Details:**
SandboxedFileIO class docstring states:
"IMPORTANT: This class mixes two concerns for web UI convenience:
- Program file operations (load/save .BAS files for editing) - NOT IMPLEMENTED
- Runtime file listing (FILES command to show in-memory data files) - IMPLEMENTED"

However, the docstring also says:
"Implementation status:
- list_files(): IMPLEMENTED - queries the sandboxed_fs filesystem for in-memory data
                files created by BASIC programs (OPEN/PRINT#/CLOSE)."

This creates confusion: list_files() is described as being for "runtime file listing" (showing data files created by BASIC programs), but FileIO's purpose is "Program management operations" not runtime operations. The mixing of concerns is acknowledged but the justification ("allows FILES command to work") doesn't align with FileIO's stated purpose.

---

#### Documentation inconsistencies

**Description:** SandboxedFileIO docstring has contradictory statements about exception handling in list_files()

**Affected files:**
- `src/file_io.py`

**Details:**
The SandboxedFileIO.list_files() docstring contains:
"Returns empty list if backend.sandboxed_fs doesn't exist. Catches exceptions and returns
(filename, None, False) for files that can't be stat'd."

But later in the same docstring:
"Note: Does not catch exceptions from list_files()
itself - only from size lookups within the loop."

These two statements contradict each other. The first implies broad exception handling, the second limits it to size lookups only. The actual code shows it catches exceptions from list_files() itself (returns empty list) AND from get_size() calls (returns (filename, None, False)).

---

#### code_vs_comment_conflict

**Description:** Comment about PC save/restore contradicts actual code behavior

**Affected files:**
- `src/immediate_executor.py`

**Details:**
After executing immediate mode statements, there's a comment:

"Design: We intentionally do NOT save/restore the PC before/after execution. This allows statements like RUN to properly change execution position."

However, there is NO code anywhere in the execute() method that saves or restores PC. The comment implies there was a design decision to remove such code, but there's no evidence of PC manipulation at all. This suggests the comment may be outdated from a refactoring where PC save/restore was removed.

---

#### code_vs_documentation_inconsistency

**Description:** Numbered line editing validation logic doesn't match documented requirements

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The docstring states:
"Numbered Line Editing:
- Requires interpreter.interactive_mode to reference the UI object
- UI.program must have add_line() and delete_line() methods
- Returns error tuple if UI integration is missing or incomplete"

But the code validates add_line() only when line_content exists, and delete_line() only when line_content is empty:

if line_content and not hasattr(ui.program, 'add_line'):
    return (False, "Cannot edit program lines: add_line method not available\n")
if not line_content and not hasattr(ui.program, 'delete_line'):
    return (False, "Cannot edit program lines: delete_line method not available\n")

This means if you try to add a line but only delete_line() exists, no error is raised until execution. The validation is incomplete compared to what's documented.

---

#### code_vs_comment_conflict

**Description:** Comment about add_line() parameter count contradicts typical API design

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In the numbered line editing section:

"# Add/update line - add_line(line_number, complete_line_text) takes two parameters
complete_line = f"{line_num} {line_content}"
success, error = ui.program.add_line(line_num, complete_line)"

The comment explicitly states add_line() takes two parameters: line_number and complete_line_text. However, the code constructs complete_line to include the line number (f"{line_num} {line_content}"), then passes both line_num AND complete_line. This means the line number appears twice - once as a parameter and once embedded in the text. This seems redundant and the comment may be describing an incorrect API.

---

#### code_vs_comment

**Description:** Comment claims digits 'silently do nothing' in EDIT mode, but code has no explicit handling for digits

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~1050 says: 'INTENTIONAL MBASIC-COMPATIBLE BEHAVIOR: When digits are entered, they silently do nothing (no output, no cursor movement, no error)... Implementation: digits fall through the command checks without matching any elif branch.'

However, the code in cmd_edit() has no explicit digit handling or fall-through case. The while loop only has elif branches for specific commands (Space, D, I, X, H, E, Q, L, A, C). If a digit is entered, it would fall through all elif branches with no action, but there's no comment in the code itself explaining this intentional behavior, and no else clause to document the fall-through.

---

#### code_vs_comment

**Description:** Comment about MERGE passing all variables conflicts with stated limitation

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~730 says: 'Save variables based on CHAIN options:
- ALL: passes all variables to the chained program
- MERGE: merges program lines (overlays code) - NOTE: Currently also passes all vars
- Neither: passes only COMMON variables'

Then at line ~740: 'KNOWN LIMITATION: In MBASIC 5.21, MERGE and ALL are orthogonal options:
- MERGE (without ALL) should only merge lines, keeping existing variables
- ALL should pass all variables, replacing the program entirely
Current implementation: Both MERGE and ALL result in passing all variables.'

The code at line ~750 implements: 'if all_flag or merge: saved_variables = self.program_runtime.get_all_variables()'

This is internally consistent but the comment structure is confusing - it first describes what SHOULD happen, then describes the limitation. The comment should be restructured to clearly state the current behavior first, then note the deviation from spec.

---

#### code_vs_comment

**Description:** Comment says PC is preserved for CONT but implementation details unclear

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~230 in clear_execution_state() says:
'Note: We do NOT clear/reset the PC here. The PC is preserved so that CONT can detect if the program was edited. The cmd_cont() method uses pc.is_valid() to check if the PC position still exists after editing. If PC is still valid, CONT resumes; if not, shows "?Can't continue" matching MBASIC 5.21 behavior.'

However, the clear_execution_state() method only clears gosub_stack and for_loops. It doesn't touch the PC at all. The comment implies this is intentional, but it's not clear from the code itself that NOT clearing PC is the correct behavior. The comment should be in cmd_cont() where the PC validation actually happens, not in clear_execution_state() which doesn't interact with PC.

---

#### code_vs_comment_conflict

**Description:** Comment claims immediate mode runtime gets empty line_text_map, but code shows it receives the AST which contains line 0

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~470 says: "Pass empty line_text_map since immediate mode uses temporary line 0."

But code at line ~471 shows:
    self.runtime = Runtime(ast, {})

The AST passed contains line 0 with the statement (created at line ~456: program_text = "0 " + statement). The comment suggests line_text_map is empty for a reason, but the AST already contains the line information. The design note mentions "Could pass {0: statement}" but that would be redundant since ast already has it.

---

#### code_vs_comment_conflict

**Description:** Comment claims clear_execution_state must be called after statement_table update, but no explanation why order matters

**Affected files:**
- `src/interactive.py`

**Details:**
At lines ~267-269:
"# Clear execution state since line edits invalidate GOSUB/FOR stacks
# (must be called after statement_table update)
self.clear_execution_state()"

The comment asserts a specific ordering requirement but doesn't explain why clear_execution_state() must come after statement_table.replace_line(). Without understanding the reason, future maintainers might reorder these calls. The same pattern appears at line ~360 without the ordering comment.

---

#### code_vs_comment

**Description:** Comment describes skip_next_breakpoint_check behavior incorrectly - says it's set during halting, but code sets it AFTER halting when breakpoint is detected

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 62-66 says:
"Set to True DURING halting at a breakpoint (in tick_pc method), within the breakpoint check itself."

But code at lines 310-314 shows:
if at_breakpoint:
    if not self.state.skip_next_breakpoint_check:
        self.runtime.pc = pc.stop("BREAK")  # Halt first
        self.state.skip_next_breakpoint_check = True  # Then set flag
        return self.state

The flag is set AFTER halting (pc.stop), not DURING the breakpoint check itself.

---

#### code_vs_comment

**Description:** Comment says return_stmt valid range is 0 to len(statements) inclusive, but validation check allows only > len(statements) as error

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 847-854 says:
"return_stmt is 0-indexed offset into statements array.
Valid range: 0 to len(statements) (inclusive).
- 0 to len(statements)-1: Normal statement positions
- len(statements): Sentinel value indicating 'past the last statement'
Values > len(statements) indicate the statement was deleted (validation error)."

But validation code at line 855 only checks:
if return_stmt > len(line_statements):
    raise RuntimeError(...)

This means return_stmt == len(statements) is accepted (sentinel case), but return_stmt > len(statements) is rejected. The comment correctly describes this, but the phrasing 'Values > len(statements)' could be misread as '>= len(statements)'. The code is correct per the comment's detailed explanation.

---

#### code_vs_comment

**Description:** Comment in _invoke_error_handler says error_info is 'always set' at line 385, but actual line number is 392 in provided code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 524-526 says:
"Note: error_info is always set in the exception handler in tick_pc() when an error occurs (line 385), regardless of whether an error handler exists."

But the actual code that sets error_info is at lines 368-373:
error_code = self._map_exception_to_error_code(e)
self.state.error_info = ErrorInfo(
    error_code=error_code,
    pc=pc,
    error_message=str(e)
)

The line number reference (385) doesn't match the actual location (368-373). This could be due to code changes after the comment was written.

---

#### code_vs_comment

**Description:** Comment describes NEXT validation logic incorrectly - states return_stmt > len(statements) is invalid, but code allows return_stmt == len(statements) as a valid sentinel value

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~180 states:
# Valid range:
#   - 0 to len(statements)-1: Normal statement positions (existing statements)
#   - len(statements): Special sentinel value - FOR was last statement on line,
#                      continue execution at next line (no more statements to execute on current line)
#   - > len(statements): Invalid - indicates the statement was deleted
#
# Validation: Check for strictly greater than (== len is OK as sentinel)
if return_stmt > len(line_statements):
    raise RuntimeError(f"NEXT error: FOR statement in line {return_line} no longer exists")

The comment correctly describes the logic, but the phrasing 'return_stmt > len(statements) is invalid' in the description field above is misleading. The comment actually says '> len(statements): Invalid' which matches the code check 'return_stmt > len(line_statements)'. This is consistent, not an inconsistency.

---

#### code_vs_comment

**Description:** Comment in execute_resume states 'MBASIC allows both RESUME and RESUME 0 as equivalent' but this is implementation detail that may not match actual MBASIC 5.21 behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~295:
# RESUME or RESUME 0 - retry the statement that caused the error
# Note: MBASIC allows both 'RESUME' and 'RESUME 0' as equivalent syntactic forms.
# Parser preserves the distinction (None vs 0) for source text regeneration,
# but runtime execution treats both identically.

This comment makes a claim about MBASIC behavior without verification. The code treats None and 0 identically, but the comment should clarify if this is confirmed MBASIC behavior or an assumption.

---

#### code_vs_comment

**Description:** Comment in execute_input describes input_file_number as 'None for keyboard input, file # for file input' but code always sets it to None even for file input

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~570:
# Note: input_file_number is designed to be set to None for keyboard input and file#
# for file input. This would allow the UI to distinguish between keyboard prompts
# (show in UI) and file input (internal, no prompt needed). However, currently always
# set to None because file input (stmt.file_number is not None) takes a separate code
# path that reads synchronously without setting the state machine.

And at line ~610:
self.state.input_file_number = None  # None indicates keyboard input (not file)

The comment acknowledges this design vs implementation gap. File input bypasses the state machine entirely (synchronous read at line ~575), so input_file_number is never set to a file number. This is documented but represents a design that was partially implemented.

---

#### code_vs_comment

**Description:** Comment in execute_delete states 'This implementation preserves variables and ALL runtime state' but does not mention that it also preserves user_functions (DEF FN)

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~1050:
# Note: This implementation preserves variables and ALL runtime state when deleting
# lines. DELETE only removes lines from the program AST, leaving variables, open
# files, error handlers, and loop stacks intact. This differs from NEW which clears
# both lines and variables (via clear_variables/clear_arrays).

The comment lists 'variables, open files, error handlers, and loop stacks' but does not explicitly mention user_functions (DEF FN definitions), which are also preserved. The phrase 'ALL runtime state' covers this, but explicit mention would be clearer for consistency with execute_clear's comment which explicitly lists user_functions.

---

#### code_vs_comment

**Description:** Comment in execute_open states 'MBASIC 5.21: #1 through #15' for file number range but does not cite source or verify this matches actual MBASIC 5.21 limits

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~1185:
# Check file number range (MBASIC 5.21: #1 through #15)
if file_num < 1 or file_num > 15:
    raise RuntimeError("Bad file number")

This comment makes a specific claim about MBASIC 5.21 behavior. If this is verified against MBASIC 5.21 documentation, it's accurate. If it's an assumption, it should be marked as such.

---

#### code_vs_comment

**Description:** RSET truncation behavior comment contradicts code implementation

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~2750 says: "Right-justify: pad on left if too short, truncate from left if too long"
But code at line ~2755 does: "value = value[-width:]" which truncates from the RIGHT (keeps rightmost characters), not from the left.

For right-justification, truncating from the left would mean keeping the leftmost characters (value[:width]), but the code keeps the rightmost characters (value[-width:]), which is correct for right-justification where you want to preserve the end of the string.

---

#### code_vs_comment

**Description:** CONT statement PC handling comment describes behavior not visible in this file

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines ~2865-2873 says:
"PC handling difference:
- STOP: execute_stop() (lines 2828-2831) sets PC via NPC.stop('STOP'), ensuring CONT resumes from the statement AFTER the STOP.
- Break (Ctrl+C): BreakException handler (lines ~376-381) does NOT update PC, leaving PC pointing to the interrupted statement."

However, the BreakException handler referenced at "lines ~376-381" is not present in this code snippet (part 3 of interpreter.py). The comment references code that may be in another part of the file, making it confusing for someone reading this section.

---

#### code_vs_comment

**Description:** String concatenation limit enforcement inconsistency

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~2925 states:
"Enforce 255 character string limit for concatenation (MBASIC 5.21 compatibility)
Note: This check only applies to concatenation via PLUS operator.
Other string operations (MID$, INPUT) and LSET/RSET do not enforce this limit."

However, looking at LSET (line ~2730) and RSET (line ~2755), they DO truncate strings to the field width, which could be less than 255. The comment implies LSET/RSET don't enforce limits, but they enforce field width limits. This is technically different from the 255-char limit, but the comment could be clearer about what "do not enforce this limit" means (they don't enforce the 255 limit, but do enforce field width limits).

---

#### code_vs_comment

**Description:** Function parameter save/restore uses debugger_set flag with extensive explanation that may be outdated

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines ~2975-2985 provides detailed explanation:
"Note: get_variable_for_debugger() and debugger_set=True are used to avoid triggering variable access tracking. This save/restore is internal function call machinery, not user-visible variable access. The tracking system (if enabled) should distinguish between: - User code variable access (tracked for debugging/variables window) - Internal implementation details (not tracked)
Maintainer warning: Ensure all internal variable operations use debugger_set=True"

This extensive comment suggests a complex tracking system, but without seeing the Runtime implementation, it's unclear if this is still accurate or if the tracking system has evolved. The "Maintainer warning" suggests this is fragile and may need updates.

---

#### Code vs Comment conflict

**Description:** Backward compatibility comment for print() method claims it was renamed for consistency, but output() is the standard IOHandler interface method

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment states: "This method was renamed from print() to output() for consistency with IOHandler interface and to support a more semantic naming convention."

This implies print() was the original method name that was changed. However, the IOHandler base class defines output() as the abstract method, so print() was likely added as a convenience alias, not the original name. The comment reverses the actual history.

---

#### Code vs Documentation inconsistency

**Description:** console.py input_char() blocking mode fallback behavior differs from documentation

**Affected files:**
- `src/iohandler/console.py`

**Details:**
For Windows without msvcrt, the fallback code calls input() which:
- Waits for Enter key (defeats single-char purpose)
- Reads entire line but returns only first character

The warning message documents this limitation, but the base.py interface documentation for input_char() does not mention that blocking mode may not work as expected on some platforms. Users would expect blocking=True to wait for a single character, not a full line with Enter.

---

#### code_vs_comment_conflict

**Description:** Comment claims PRINT# handling excludes # and re-tokenizes separately, but code actually rewinds position to re-tokenize #

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line ~280 says: "Note: For PRINT#, INPUT#, etc., special handling occurs before this point (see PRINT# check earlier) where the # is excluded and re-tokenized separately."

But the actual code at lines ~310-325 shows:
1. The # IS consumed as part of identifier (ident += self.advance())
2. Then AFTER checking if it's a file I/O keyword, the code rewinds: self.pos -= 1; self.column -= 1
3. The # is NOT excluded "before this point" - it's consumed and then rewound

The comment describes a different flow than what the code implements.

---

#### code_vs_comment_conflict

**Description:** Comment about old BASIC preprocessing contradicts the actual PRINT# handling implementation

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at lines ~330-335 says: "NOTE: We do NOT handle old BASIC where keywords run together (NEXTI, FORI). MBASIC 5.21 is properly-formed and requires spaces between keywords. Special case handled above: PRINT# and similar file I/O keywords in MBASIC 5.21 allow # without a space (MBASIC 5.21 feature, not old BASIC syntax)."

But the code DOES handle PRINT# without spaces (lines ~310-325), which contradicts the claim that "MBASIC 5.21 is properly-formed and requires spaces between keywords." The comment tries to distinguish this from "old BASIC" but the handling is essentially the same - splitting apart tokens that were written together.

---

#### code_vs_comment

**Description:** Comment claims at_end_of_line() does NOT check for COLON or comment tokens, but the method description contradicts statement parsing guidance

**Affected files:**
- `src/parser.py`

**Details:**
at_end_of_line() docstring says:
"Important: This does NOT check for COLON or comment tokens. For statement parsing, use at_end_of_statement() instead to properly stop at colons and comments."

But at_end_of_statement() docstring says:
"A statement ends at:
- End of line (NEWLINE or EOF)
- Statement separator (COLON) - allows multiple statements per line
- Comment (REM, REMARK, or APOSTROPHE) - everything after is ignored"

The comment in at_end_of_line() warns about using it for statement parsing because it doesn't check COLON/comments, but then says "Most statement parsing should use at_end_of_statement(), not this method. Using at_end_of_line() in statement parsing can cause bugs where comments are parsed as part of the statement instead of ending it."

However, the code implementation shows at_end_of_line() returns: token.type in (TokenType.NEWLINE, TokenType.EOF)
And at_end_of_statement() returns: token.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.COLON, TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE)

The comment is technically correct but confusingly worded - it's warning about what at_end_of_line() does NOT check, which could be clearer.

---

#### documentation_inconsistency

**Description:** Expression parsing notes claim only RND and INKEY$ can be called without parentheses, but code shows this is a special case, not a general MBASIC feature

**Affected files:**
- `src/parser.py`

**Details:**
Module docstring states:
"Expression parsing notes:
- Functions generally require parentheses: SIN(X), CHR$(65)
- Exception: Only RND and INKEY$ can be called without parentheses in MBASIC 5.21
  (this is specific to these two functions, not a general MBASIC feature)"

The code in parse_builtin_function() confirms this:
"# RND can be called without parentheses - MBASIC 5.21 compatibility feature"
"# INKEY$ can be called without parentheses - MBASIC 5.21 compatibility feature"

However, the documentation could be clearer that this is an intentional compatibility feature being preserved, not a bug or oversight. The parenthetical note helps but could be more prominent.

---

#### code_vs_comment

**Description:** Comment about MID$ statement detection describes complex lookahead logic that may have edge cases

**Affected files:**
- `src/parser.py`

**Details:**
In parse_statement() for MID$ detection:
"# MID$ statement (substring assignment)
# Detect MID$ used as statement: MID$(var, start, len) = value
...
# Lookahead strategy: scan past balanced parentheses, check for = sign
...
except (IndexError, ParseError):
    # Catch lookahead failures during MID$ statement detection
    # IndexError: if we run past end of tokens
    # ParseError: if malformed syntax encountered during lookahead
    # Position is restored below, so proper error will be reported later if needed
    pass

The comment says 'proper error will be reported later if needed' but the code then raises:
raise ParseError(f'MID$ must be used as function (in expression) or assignment statement', token)

This error message may not accurately reflect what went wrong if the lookahead failed due to malformed syntax. The error handling silently swallows the real error and reports a generic message instead.

---

#### code_vs_comment

**Description:** Inconsistent approach to applying DEF type suffixes between parse_for/parse_next and parse_dim

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_for (line ~1590) states: "Note: This method modifies type_suffix variable (unlike parse_dim which modifies the name directly). Both approaches are functionally equivalent."

However, examining parse_dim (line ~1780), it DOES modify the name directly by appending suffixes:
  if var_type == TypeInfo.STRING:
      name = name + '$'
  elif var_type == TypeInfo.INTEGER:
      name = name + '%'

But parse_for/parse_next modify type_suffix variable instead:
  if var_type == TypeInfo.STRING:
      type_suffix = '$'
  elif var_type == TypeInfo.INTEGER:
      type_suffix = '%'

These are NOT functionally equivalent - one modifies the variable name itself, the other sets a separate type_suffix field. This could lead to inconsistent variable representation in the AST.

---

#### code_vs_comment

**Description:** parse_deffn docstring claims type suffixes are stripped from function names, but code only strips from raw_name after 'fn' prefix is added

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"Type suffix characters ($, %, !, #) are STRIPPED during normalization"
"Only the 'fn' + base name is kept for function lookup"
"'DEF FNA$' and 'DEF FNA' define the SAME function (both become 'fna')"

But code shows:
For 'DEF FN name' case:
  raw_name = fn_name_token.value
  type_suffix = self.get_type_suffix(raw_name)
  if type_suffix:
      raw_name = raw_name[:-1]
  function_name = 'fn' + raw_name  # Result: 'fn' + name_without_suffix

For 'DEF FNR' case:
  raw_name = fn_name_token.value  # Already 'fnr' from lexer
  type_suffix = self.get_type_suffix(raw_name)
  if type_suffix:
      raw_name = raw_name[:-1]
  function_name = raw_name  # Result: 'fnr' (without suffix if present)

The code correctly strips suffixes, matching the docstring. However, the docstring example 'DEF FNA$' -> 'fna' is misleading because it would actually become 'fna' (fn + a), not just 'fna' as a standalone result.

---

#### code_vs_comment

**Description:** parse_resume docstring describes RESUME 0 behavior but implementation doesn't validate or document how interpreter distinguishes None vs 0

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"RESUME with no argument retries the statement that caused the error.
RESUME 0 also retries the error statement (same as RESUME with no argument)."

And:
"AST representation:
- RESUME (no arg) → line_number=None
- RESUME 0 → line_number=0 (interpreter handles 0 same as None)"

Code implementation:
if self.match(TokenType.LINE_NUMBER, TokenType.NUMBER):
    line_number = int(self.advance().value)

The code stores 0 as 0 and None as None, but the comment claims "interpreter handles 0 same as None" without any code in the parser to enforce or validate this. This creates ambiguity about whether the parser should normalize 0 to None or if the interpreter truly handles both identically.

---

#### code_vs_comment

**Description:** parse_call docstring claims extended syntax is not validated against MBASIC 5.21 spec, but code fully implements and parses it

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"Extended syntax (for compatibility with other BASIC dialects):
    CALL ROUTINE(X,Y)      - Call with arguments

Note: MBASIC 5.21 primarily uses the simple numeric address form. This parser
also accepts the extended syntax (CALL routine_name(args)) for compatibility
with code from other BASIC dialects, though this form is not validated against
the MBASIC 5.21 specification."

However, the code fully parses and handles this syntax:
if isinstance(target, VariableNode) and target.subscripts:
    arguments = target.subscripts
    target = VariableNode(...)
elif isinstance(target, FunctionCallNode):
    arguments = target.arguments
    target = VariableNode(...)

The comment suggests this is a compatibility feature that may not be spec-compliant, but doesn't indicate any limitations or warnings in the implementation. This creates ambiguity about whether this syntax should be supported or if it's a deviation from the target BASIC dialect.

---

#### code_vs_comment

**Description:** PC.statement field documentation inconsistency with stmt_offset property

**Affected files:**
- `src/pc.py`

**Details:**
The PC class docstring states:
"statement: Statement index on the line (0-based)"
and
"The statement index is 0-based: first statement has index 0, second has index 1, etc."

However, the stmt_offset property comment says:
"Compatibility: old code used stmt_offset instead of statement"

This suggests 'statement' is the new name and 'stmt_offset' is legacy, but the main docstring doesn't mention this is a renamed field or that stmt_offset is deprecated. The docstring should clarify that 'statement' replaced 'stmt_offset' for consistency.

---

#### code_vs_comment

**Description:** apply_keyword_case_policy docstring contradicts implementation for 'preserve' policy

**Affected files:**
- `src/position_serializer.py`

**Details:**
The docstring states:
"Args:
    keyword: The keyword to transform. While callers should normalize to lowercase before calling (for consistency with emit_keyword()), this function can handle mixed-case input as the first_wins policy normalizes internally."

And later:
"Recommendation: Callers should normalize keyword to lowercase before calling to ensure consistent behavior across all policies and avoid case-sensitivity issues."

But the 'preserve' policy implementation says:
"# The 'preserve' policy is typically handled at a higher level (keywords passed with original case preserved). If this function is called with 'preserve' policy, we return the keyword as-is if already properly cased, or capitalize as a safe default."

This is contradictory: if callers should normalize to lowercase, then 'preserve' policy can never work (lowercase input would always be returned as lowercase or capitalized, never preserving original case). The comment suggests preserve is handled elsewhere, but then why is it a valid policy option here?

---

#### code_vs_comment

**Description:** emit_keyword docstring says 'must be normalized lowercase' but serialize_rem_statement shows uppercase input

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword docstring states:
"Args:
    keyword: The keyword to emit (must be normalized lowercase by caller, e.g., 'print', 'for')"

And:
"Note: This function requires lowercase input because it looks up the display case from the keyword case manager using the normalized form."

But serialize_rem_statement comment says:
"Note: stmt.comment_type is stored in uppercase by the parser ('APOSTROPHE', 'REM', or 'REMARK'). We convert to lowercase before passing to emit_keyword() which requires lowercase input."

This shows the parser stores keywords in uppercase, requiring conversion. The emit_keyword docstring should acknowledge this pattern (parser stores uppercase, callers must convert) rather than just stating 'must be normalized lowercase' without context.

---

#### code_vs_comment

**Description:** VariableNode serialization comment about explicit_type_suffix contradicts implementation

**Affected files:**
- `src/position_serializer.py`

**Details:**
The comment in serialize_expression for VariableNode says:
"# Only add type suffix if explicitly present in source code (not inferred from DEFINT/DEFSNG/etc)
# Note: explicit_type_suffix attribute may not exist on all VariableNode instances (defaults to False via getattr)
if expr.type_suffix and getattr(expr, 'explicit_type_suffix', False):
    text += expr.type_suffix"

This suggests explicit_type_suffix is optional and may not exist. However, the code checks both expr.type_suffix AND explicit_type_suffix. If explicit_type_suffix doesn't exist (defaults to False), then type_suffix would never be added even if present. This seems like it might be a bug - perhaps the check should be:
if getattr(expr, 'explicit_type_suffix', True) and expr.type_suffix:

Or the comment is wrong about the default behavior.

---

#### Code vs Comment conflict

**Description:** Comment about DIM A(N) indexing convention may not match actual interpreter behavior

**Affected files:**
- `src/resource_limits.py`

**Details:**
In check_array_allocation() method, line ~180:

Comment states: "Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21 due to 0-based indexing
We account for this convention in our size calculation to ensure limit checks match
the actual memory allocation size. The execute_dim() method in interpreter.py uses the
same convention when creating arrays, ensuring consistency between limit checks and allocation."

Code implements: total_elements *= (dim_size + 1)  # +1 for 0-based indexing (0 to N)

This comment references execute_dim() in interpreter.py which is not provided in the source files. Without seeing interpreter.py, we cannot verify if the convention is actually implemented consistently. The comment makes a claim about another file's behavior that cannot be verified.

---

#### Documentation inconsistency

**Description:** create_unlimited_limits() warning about MBASIC compatibility is inconsistent with function purpose

**Affected files:**
- `src/resource_limits.py`

**Details:**
The create_unlimited_limits() docstring contains:
"WARNING: This configuration INTENTIONALLY BREAKS MBASIC 5.21 COMPATIBILITY by setting
max_string_length to 1MB (instead of the required 255 bytes). This is for testing/development
only - programs may pass tests with unlimited limits that would fail with MBASIC-compatible
limits. For MBASIC 5.21 spec compliance, use create_local_limits() or create_web_limits()
which enforce the mandatory 255-byte string limit."

However, the function is named create_unlimited_limits() and its purpose is explicitly for testing. The warning is appropriate but the emphasis on "INTENTIONALLY BREAKS" and "WARNING" seems excessive for a function whose entire purpose is to remove limits for testing. The documentation could be clearer that this is the expected behavior for this specific use case rather than framing it as a warning.

---

#### code_vs_comment

**Description:** Comment claims 'original_case' field stores original case as first typed, but code actually stores policy-resolved canonical case

**Affected files:**
- `src/runtime.py`

**Details:**
Line 48-51 comment: "Note: The 'original_case' field stores the canonical case for display (determined by case_conflict policy).
       Despite its misleading name, this field contains the policy-resolved canonical case variant,
       not the original case as first typed. See _check_case_conflict() for resolution logic."

This comment explicitly states the field name is misleading and stores canonical case, not original case. However, the field is named 'original_case' throughout the codebase, creating confusion.

Line 244: self._variables[full_name]['original_case'] = canonical_case  # Canonical case for display (field name is misleading, see module header)
Line 251: self._variables[full_name]['original_case'] = canonical_case  # Canonical case for display (field name is misleading, see module header)
Line 330: self._variables[full_name]['original_case'] = canonical_case  # Canonical case for display (field name is misleading, see module header)
Line 337: self._variables[full_name]['original_case'] = canonical_case  # Canonical case for display (field name is misleading, see module header)

---

#### code_vs_comment

**Description:** Comment in dimension_array() claims DIM is tracked as both read and write, but implementation only sets tracking_info once

**Affected files:**
- `src/runtime.py`

**Details:**
Line 598-606 comment:
"# Note: DIM is tracked as both read and write to provide consistent debugger display.
# While DIM is technically allocation/initialization (write-only operation), setting
# last_read to the DIM location ensures that debuggers/inspectors can show 'Last accessed'
# information even for arrays that have never been explicitly read. Without this, an
# unaccessed array would show no last_read info, which could be confusing. The DIM location
# provides useful context about where the array was created."

However, the code at lines 598-606:
self._arrays[full_name] = {
    'dims': dimensions,
    'data': [default_value] * total_size,
    'last_read_subscripts': None,
    'last_write_subscripts': None,
    'last_read': tracking_info,
    'last_write': tracking_info
}

Both last_read and last_write are set to the same tracking_info object reference. While this achieves the stated goal, the comment's explanation could be clearer that they're set to the same value/reference, not tracked separately.

---

#### code_vs_comment

**Description:** get_variable() docstring claims ValueError is raised if token is None, but implementation allows token with missing attributes

**Affected files:**
- `src/runtime.py`

**Details:**
Line 207-221 docstring states:
"Args:
    ...
    token: REQUIRED - A token object must be provided (ValueError raised if None).
           The token enables source location tracking for this variable access.

           Token attributes have fallback behavior:
           - token.line: Used for tracking if present, otherwise falls back to self.pc.line_num
           - token.position: Used for tracking if present, otherwise falls back to None

           Why token object is required: Even with attribute fallbacks, the token object
           itself is mandatory to distinguish intentional program execution (which must
           provide a token) from debugging/inspection (which should use get_variable_for_debugger()).
           This design prevents accidental omission of tracking during normal execution."

But line 229-230 implementation:
if token is None:
    raise ValueError("get_variable() requires token parameter. Use get_variable_for_debugger() for debugging.")

The docstring describes elaborate fallback behavior for missing token attributes (line, position), but the implementation simply rejects None tokens entirely. The fallback behavior described in the docstring is implemented at line 246-247:
'line': getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None),
'position': getattr(token, 'position', None),

This is not an inconsistency per se, but the docstring's emphasis on "token object must be provided" and "Why token object is required" explanation is somewhat redundant given the simple None check. The real purpose of requiring a token object (vs allowing None) is to force explicit choice between tracked (get_variable) and untracked (get_variable_for_debugger) access.

---

#### Code vs Comment conflicts

**Description:** Docstring claims get_loop_stack() is deprecated but provides no warning mechanism

**Affected files:**
- `src/runtime.py`

**Details:**
At line 240, get_loop_stack() docstring states:

"Deprecated (as of 2025-10-25): Use get_execution_stack() instead.
...
Deprecated since: 2025-10-25 (commit cda25c84)
Will be removed: No earlier than 2026-01-01"

However, the implementation at line 250 is simply:
"return self.get_execution_stack()"

There is no deprecation warning (e.g., using warnings.warn()) to alert users that this method is deprecated. This means users won't know they're using deprecated functionality until it's removed.

---

#### code_vs_comment

**Description:** SettingsManager.__init__ docstring claims _get_global_settings_path() and _get_project_settings_path() are called, but code shows they are only called by FileSettingsBackend

**Affected files:**
- `src/settings.py`

**Details:**
Comment in _get_global_settings_path() says: "Note: This method is not called directly by SettingsManager. Instead, it is called by FileSettingsBackend.__init__() to compute paths."

However, SettingsManager.__init__() docstring does not mention this delegation pattern. The methods exist in SettingsManager but are only used by FileSettingsBackend, creating confusion about their purpose.

---

#### code_vs_comment

**Description:** File-level settings implementation status is inconsistently described across multiple comments

**Affected files:**
- `src/settings.py`

**Details:**
Class docstring says: "File-level settings (per-file settings) are FULLY IMPLEMENTED for in-memory use... However, persistence is NOT implemented"

But get() method docstring says: "Note: The implementation also supports file-level settings (highest precedence: file > project > global...), but these are not populated in normal usage."

And the file_settings initialization comment says: "# RESERVED FOR FUTURE USE: per-file settings (not persisted)"

These three descriptions use different terminology: 'FULLY IMPLEMENTED for in-memory', 'supports but not populated', and 'RESERVED FOR FUTURE USE'. This creates confusion about the actual implementation status.

---

#### code_vs_comment

**Description:** create_settings_backend docstring says it 'falls back to file backend if not provided' but doesn't mention this is silent behavior

**Affected files:**
- `src/settings_backend.py`

**Details:**
Docstring says: "session_id: Session ID for Redis mode (required for Redis backend, but falls back to file backend if not provided even when NICEGUI_REDIS_URL is set)"

And in Note section: "If NICEGUI_REDIS_URL is set but session_id is None, falls back to FileSettingsBackend (this is expected behavior - Redis requires both URL and session_id, so incomplete config defaults to file mode silently)."

The word 'silently' appears only in the Note, not in the main docstring. This is important behavior that should be more prominent - users might expect a warning when Redis URL is set but session_id is missing.

---

#### code_vs_comment

**Description:** Token dataclass docstring describes convention for original_case fields but doesn't enforce it

**Affected files:**
- `src/tokens.py`

**Details:**
Docstring says: "Note: By convention, these fields are used for different token types:
- original_case: For IDENTIFIER tokens (user variables) - preserves what user typed
- original_case_keyword: For keyword tokens - stores policy-determined display case

The dataclass does not enforce this convention (both fields can technically be set on the same token) to allow implementation flexibility."

This is a design smell - having two fields with overlapping purposes that are only separated by convention (not type system) creates risk of misuse. The comment acknowledges this but doesn't explain why this design was chosen over alternatives like using a union type or separate token classes.

---

#### Documentation inconsistency

**Description:** STEP command documentation inconsistency between implementation and keybindings

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/cli_keybindings.json`

**Details:**
cli_debug.py docstring says: "Executes a single statement (not a full line). If a line contains multiple statements separated by colons, each statement is executed separately."

But cli_keybindings.json says: "Execute next statement or n statements (STEP | STEP n) - attempts statement-level stepping"

The word 'attempts' in the JSON suggests uncertainty about whether statement-level stepping actually works, while the Python docstring confidently states it does. The _execute_single_step() method's comment also notes: "Note: The actual statement-level granularity depends on the interpreter's implementation of tick()/execute_next(). These methods are expected to advance the program counter by one statement, handling colon-separated statements separately. If the interpreter executes full lines instead, this method will behave as line-level stepping rather than statement-level."

---

#### Code vs Documentation inconsistency

**Description:** Module docstring claims UI layer decides when to offer recovery, but format_recovery_prompt() suggests auto-save manager makes this decision

**Affected files:**
- `src/ui/auto_save.py`

**Details:**
Module docstring states: "The UI layer is responsible for:
- Displaying prompts to user (this module provides format_recovery_prompt() helper)
- Deciding when to offer recovery on startup"

However, format_recovery_prompt() method includes logic to decide whether recovery is needed:

def format_recovery_prompt(self, filepath: str) -> Optional[str]:
    """Generate a recovery prompt message.
    ...
    Returns:
        Formatted message or None if no recovery needed
    """
    if not self.is_autosave_newer(filepath):
        return None

This method returns None when no recovery is needed, effectively making the decision about whether to offer recovery, not just formatting the prompt. This contradicts the module docstring's claim that the UI layer decides when to offer recovery.

---

#### Code vs Documentation inconsistency

**Description:** BREAK command docstring says breakpoints can be set 'before or during execution' but implementation doesn't show runtime integration

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
cmd_break() docstring: "Breakpoints can be set before or during execution, but only on existing program lines."

However, the enhance_run_command() and _install_breakpoint_handler() methods show breakpoint checking is only installed when RUN is called with breakpoints already set. There's no evidence in the code that breakpoints can be set during execution (e.g., when program is paused). The implementation only checks breakpoints that existed before RUN was called.

---

#### code_vs_comment

**Description:** Comment claims auto-numbering stops at 99999 but code allows manual entry of higher numbers, yet _parse_line_number() has no such restriction documented

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~730: "# Note: Auto-numbering stops at 99999 for display consistency, but manual
# entry of higher line numbers is not prevented by _parse_line_number()."

However, _parse_line_number() method (lines ~240-310) has no documented limit and will parse any valid integer. The comment suggests intentional design but the method itself has no documentation about this behavior or any upper limit.

---

#### code_vs_comment

**Description:** Comment about line 0 handling is unclear and may indicate a code bug

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_syntax_errors() method (line ~1050): "# Note: line_number > 0 check silently skips line 0 if present (not a valid
# BASIC line number). This avoids setting status for malformed lines."

This comment suggests line 0 is intentionally skipped as invalid, but:
1. BASIC traditionally allows line 0 as a valid line number
2. The code doesn't explicitly validate or reject line 0 elsewhere
3. The check 'line_number > 0' silently ignores it without user feedback
4. No documentation explains why line 0 is considered invalid

---

#### internal_inconsistency

**Description:** Inconsistent handling of empty lines in syntax checking vs error display

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_check_line_syntax() method (line ~880): "if not code_text or not code_text.strip():
    # Empty lines are valid
    return (True, None)"

But _update_syntax_errors() (line ~1045): "# Skip empty code lines
if not code_area.strip() or line_number is None:
    # Clear error status for empty lines, but preserve breakpoints"

The first treats empty lines as valid (returns True), but the second 'skips' them entirely without explicitly clearing errors. The comment says 'Clear error status' but the code only updates status character, not the syntax_errors dict. This could leave stale errors for lines that become empty.

---

#### code_vs_comment

**Description:** Comment claims _renumber_lines() is defined but the method body is cut off/missing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
At line ~1180, there's a method definition:
    def _renumber_lines(self):

But the method body appears to be truncated. Earlier at line ~470, there's a complete implementation of _renumber_lines() that:
- Calls renum_program with default args
- Refreshes the editor
- Handles exceptions silently

The duplicate definition at the end suggests either:
1. Accidental duplication during refactoring
2. File truncation
3. Incomplete merge/edit

---

#### code_vs_comment

**Description:** Docstring for _sort_lines_by_number describes target_column parameter but implementation doesn't use it correctly

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Docstring at line ~130 states:
"target_column: Column to position cursor at (default: 7). Since line numbers have
              variable width, this is approximate. The cursor will be positioned
              at this column or adjusted based on actual line content."

But in the implementation (line ~165), the code does:
"new_cursor_pos = line_start + target_column"

This adds target_column to line_start without any adjustment for actual line content or variable line number width. The docstring promises adjustment but the code doesn't implement it.

---

#### code_internal_inconsistency

**Description:** Duplicate _renumber_lines() method definitions

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Method _renumber_lines() is defined twice:
1. First at line ~470 with full implementation
2. Second at line ~1180 with truncated/missing body

This is clearly an error - either from incomplete file content, merge conflict, or accidental duplication. Only one definition should exist.

---

#### code_vs_comment

**Description:** Comment claims breakpoints are stored in editor as authoritative source and re-applied after reset, but code shows breakpoints are cleared during reset_for_run and then re-applied from editor.breakpoints

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1089 states:
"Note: reset_for_run() clears variables and resets PC. Breakpoints are STORED in
the editor (self.editor.breakpoints) as the authoritative source, not in runtime.
This allows them to persist across runs. After reset_for_run(), we re-apply them
to the interpreter below via set_breakpoint() calls so execution can check them."

This is accurate - the comment correctly describes the implementation where breakpoints persist in editor.breakpoints and are re-applied after reset. However, the phrasing could be clearer that reset_for_run() clears breakpoints from the interpreter/runtime, not from the editor.

---

#### code_vs_comment

**Description:** Multiple comments state 'Don't update immediate status' after errors, but _update_immediate_status() is called in some error paths

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comments at various locations state:
- Line ~1078: "Don't update immediate status here - error is displayed in output"
- Line ~1086: "Don't update immediate status on exception - error is in output"
- Line ~1168: "Don't update immediate status after error so user can continue" (but then calls _update_immediate_status())

The last case contradicts the comment - it says don't update but then does update. The other cases don't update as stated.

---

#### code_vs_comment

**Description:** Comment about main widget storage strategy differs between methods but implementation is consistent

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple comments explain main widget storage:

_show_help (line ~442): "Main widget retrieval: Use self.base_widget (stored at UI creation time in __init__) rather than self.loop.widget (which reflects the current widget and might be a menu or other overlay)."

_activate_menu (line ~520): "Extract base widget from current loop.widget to unwrap any existing overlay. This differs from _show_help/_show_keymap/_show_settings which use self.base_widget directly, since menu needs to work even when other overlays are already present."

The comments accurately describe different strategies for different use cases. This is actually good documentation, not an inconsistency.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says immediate commands don't start execution, but code clearly starts execution after RUN

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1330 states:
"# Sync program to runtime (updates statement table and line text map).
# If execution is running, _sync_program_to_runtime preserves current PC.
# If not running, it sets PC to halted. Either way, this doesn't start execution,
# but allows commands like LIST to see the current program."

However, immediately after at line ~1350, the code checks:
if self.interpreter and has_work:
    if not self.running:
        # ... sets up IO handler ...
        self.running = True
        # Start the tick loop
        self.loop.set_alarm_in(0.01, lambda loop, user_data: self._execute_tick())

This clearly starts execution, contradicting the comment that says syncing "doesn't start execution".

---

#### code_vs_comment

**Description:** Comment says not to call interpreter.start() because RUN already called it, but then creates InterpreterState manually

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1355 states:
"# NOTE: Don't call interpreter.start() here. The RUN command (executed via the
# immediate executor) already called interpreter.start() to set up the program and
# position the PC at the appropriate location. This function only ensures
# InterpreterState exists for tick-based execution tracking. If we called
# interpreter.start() here again, it would reset PC to the beginning, overriding
# the PC set by the RUN command."

But then the code manually creates InterpreterState:
from src.interpreter import InterpreterState
if not hasattr(self.interpreter, 'state') or self.interpreter.state is None:
    self.interpreter.state = InterpreterState(_interpreter=self.interpreter)
self.interpreter.state.is_first_line = True

This manual state creation may not properly initialize all state that interpreter.start() would set up, potentially causing inconsistencies.

---

#### code_vs_comment

**Description:** Comments in cmd_delete and cmd_renum say 'Updates self.program immediately (source of truth), then syncs to runtime' but don't mention editor sync

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Both cmd_delete (line ~1450) and cmd_renum (line ~1470) have comments:
"Note: Updates self.program immediately (source of truth), then syncs to runtime."

Both functions call self._refresh_editor() after syncing to runtime, but this critical step isn't mentioned in the comment. The comment implies a two-step process (program -> runtime) but the actual flow is three steps (program -> runtime -> editor).

---

#### code_vs_comment_conflict

**Description:** Comment describes tier label mapping logic that doesn't match the actual code implementation

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~138 states:
"Note: Tier labels are determined by:
1. Local tier_labels dict (defined below) for 'language' and 'mbasic' tiers
2. startswith('ui/') check for UI tiers ('ui/curses', 'ui/tk')
3. '📙 Other' fallback for unknown tiers"

However, the actual code at lines ~151-157 shows:
tier_name = file_info.get('tier', '')
if tier_name.startswith('ui/'):
    tier_label = '📘 UI'
else:
    tier_label = tier_labels.get(tier_name, '📙 Other')

The comment lists 3 steps but the code only has 2 branches (if/else). The tier_labels dict lookup and fallback happen in a single else branch, not as separate steps.

---

#### code_vs_comment_conflict

**Description:** Comment claims links are found using regex but doesn't mention renderer's link list is also used

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~234 states:
"Links are marked with [text] or [text](url) in the rendered output. This method finds ALL such patterns for display/navigation using regex r'\\[([^\\]]+)\\](?:\\([^)]+\\))?', which matches both formats. The renderer's links list is used for target mapping when following links."

This is accurate but the comment at line ~289 adds:
"For links in headings like [text](url), we parse the URL directly since the renderer doesn't extract them."

This creates confusion: if the renderer doesn't extract [text](url) links, why does the first comment say "renderer's links list is used for target mapping"? The code shows both are true - renderer extracts some links, and [text](url) patterns are parsed separately - but the comments make this sound contradictory.

---

#### code_vs_comment_conflict

**Description:** Comment describes keybindings module usage but doesn't mention JSON keybinding files

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Module docstring and code show:
"from . import keybindings as kb
from .keybindings import key_to_display"

And menu items use:
"f'New            {key_to_display(kb.NEW_KEY)}'"

This suggests keybindings come from a Python module (keybindings.py), but help_macros.py and keybinding_loader.py both load from JSON files (e.g., curses_keybindings.json). The interactive_menu.py doesn't mention or use KeybindingLoader, suggesting it uses a different keybinding system. This inconsistency in how keybindings are accessed across the codebase could lead to maintenance issues.

---

#### documentation_inconsistency

**Description:** Both files claim to load keybindings for different purposes but have nearly identical _load_keybindings methods

**Affected files:**
- `src/ui/help_macros.py`
- `src/ui/keybinding_loader.py`

**Details:**
help_macros.py _load_keybindings() comment (line ~26):
"Load keybindings configuration for current UI.

Note: This loads the same keybinding JSON files as keybinding_loader.py, but for a different purpose: macro expansion in help content (e.g., {{kbd:run}} -> "^R") rather than runtime event handling. This is separate from help_widget.py which uses hardcoded keys for navigation within the help system itself."

keybinding_loader.py _load_config() comment (line ~26):
"Load keybindings configuration for current UI.

Note: This loads keybindings for runtime event handling (binding keys to actions). help_macros.py loads the same JSON files but for macro expansion in help content (e.g., {{kbd:run}} -> "^R"). Both read the same data but use it differently: KeybindingLoader for runtime key event handling, HelpMacros for documentation display."

Both methods load from the same JSON files and have nearly identical implementations. This duplication could lead to maintenance issues if the loading logic needs to change.

---

#### Code vs Comment conflict

**Description:** Comment says QUIT_KEY has no dedicated keybinding and suggests using menu or Ctrl+C, but QUIT_ALT_KEY is loaded from JSON config and provides a keyboard shortcut

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 95-100:
# Quit - No dedicated keybinding in QUIT_KEY (most Ctrl keys intercepted by terminal or already assigned)
# Primary method: Use menu (Ctrl+U -> File -> Quit)
# Alternative method: Ctrl+C (interrupt signal) - handled by QUIT_ALT_KEY below
QUIT_KEY = None  # No standard keybinding (use menu or Ctrl+C instead)

But lines 102-105:
# Note: QUIT_ALT_KEY is loaded from the JSON config (defaults to 'ctrl c')
# and provides an additional way to quit the program via keyboard.
_quit_alt_from_json = _get_key('editor', 'quit')
QUIT_ALT_KEY = _ctrl_key_to_urwid(_quit_alt_from_json) if _quit_alt_from_json else 'ctrl c'

The comment suggests Ctrl+C is an interrupt signal, but the code loads it from JSON as a normal keybinding.

---

#### Code vs Comment conflict

**Description:** Comment says CONTINUE_KEY is for 'Go to line' in editor mode and 'Continue execution (Go)' in debugger mode, but the JSON key name is 'goto_line' which doesn't reflect debugger usage

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 157-161:
# Go to line (also used for Continue execution in debugger context)
# Note: This key serves dual purpose - "Go to line" in editor mode and
# "Continue execution (Go)" in debugger mode. The JSON key is 'goto_line'
# to reflect its primary function, but CONTINUE_KEY name reflects debugger usage.
_continue_from_json = _get_key('editor', 'goto_line')

The comment acknowledges the dual purpose but the JSON config would need to be checked to verify if 'goto_line' action actually implements both behaviors or just one.

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

#### code_vs_comment

**Description:** Comment describes 3-pane layout with specific weights (3:2:1) but code implements different weight distribution

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line 48-52 states:
    - 3-pane vertical layout (weights: 3:2:1 = total 6 units):
      * Editor with line numbers (top, ~50% = 3/6 - weight=3)
      * Output pane (middle, ~33% = 2/6 - weight=2)
      * Immediate mode input line (bottom, ~17% = 1/6 - weight=1)

But code at lines 195-207 shows:
    paned.add(editor_frame, weight=3)  # Editor
    paned.add(output_frame, weight=2)  # Output
    paned.add(immediate_frame, weight=1)  # Immediate

The weights match (3:2:1), but the comment incorrectly describes immediate mode as 'input line' when it's actually a full frame with label, entry, and button. The percentages are correct for the weights.

---

#### code_vs_comment

**Description:** Docstring for _ImmediateModeToken claims it's used for variable inspector edits, but the class is never instantiated in the visible code

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Class docstring at lines 23-31 states:
    '''Token for variable edits from immediate mode or variable editor.

    This class is instantiated when editing variables via the variable inspector
    (see _on_variable_double_click()). Used to mark variable changes that
    originate from the variable inspector or immediate mode, not from program
    execution. The line=-1 signals to runtime.set_variable() that this is a
    debugger/immediate mode edit, allowing correct variable tracking during debugging.'''

However, searching the provided code shows _ImmediateModeToken is defined but never instantiated. The _on_variable_double_click method is declared at line 1009 but its implementation is cut off. This suggests either the implementation is missing or the docstring is outdated.

---

#### code_vs_comment

**Description:** Variables window heading text comment doesn't match the actual heading text format

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line 963 states:
    # Set initial heading text with down arrow (matches self.variables_sort_column='accessed', descending)
    tree.heading('#0', text='↓ Variable (Last Accessed)')

The comment says 'down arrow' but the actual text uses '↓' which is a Unicode down arrow character, not an ASCII arrow. While technically correct, the comment could be clearer about using Unicode. More importantly, the heading text format 'Variable (Last Accessed)' suggests the sort mode is always shown in parentheses, but this may not be consistent with other sort modes.

---

#### code_vs_comment

**Description:** Comment claims formatting may occur elsewhere, but code explicitly avoids formatting to preserve MBASIC compatibility

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _refresh_editor method around line 1150:
Comment says: "(Note: 'formatting may occur elsewhere' refers to the Variables and Stack windows, which DO format data for display - not the editor/program text itself)"

This parenthetical note appears to be a defensive clarification added after confusion, but it's awkwardly placed in a comment about NOT formatting. The comment structure suggests there was previous confusion about where formatting happens.

---

#### code_vs_comment

**Description:** Comment about when _remove_blank_lines is called contradicts potential future usage

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines method around line 1360:
Comment says: "Currently called only from _on_enter_key (after each Enter key press), not after pasting or other modifications."

The word 'Currently' suggests this may change, but the comment doesn't explain why it's limited or what would need to change. This creates ambiguity about whether the limitation is intentional or temporary.

---

#### code_vs_comment

**Description:** Comment about array_base validation references OPTION statement parser but doesn't specify where

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _edit_array_element method around line 680:
Comment says: "OPTION BASE only allows 0 or 1 (validated by OPTION statement parser). The else clause is defensive programming for unexpected values."

This references validation in another component ('OPTION statement parser') without specifying the file or method. If that validation changes or is removed, this defensive code and comment could become misleading.

---

#### code_vs_comment

**Description:** Comment about error display logic contradicts itself about when to show errors

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1250:
Comment says: "Only show full error list in output if there are multiple errors. For single errors, the red ? icon in the editor is sufficient feedback. This avoids cluttering the output pane with repetitive messages during editing."

However, the code shows errors_found list in output when len(errors_found) > 1, but then ALWAYS updates status bar with error count (even for single errors). The comment suggests single errors shouldn't clutter output, but status bar updates happen regardless.

---

#### code_vs_comment

**Description:** Comment claims blank line removal is scheduled asynchronously after key presses, but code shows it's scheduled synchronously with 10ms delay

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_enter_key() method around line 1150:
Comment says: "# At this point, the editor may contain blank lines inserted by user actions.\n# Blank line removal is handled by _remove_blank_lines() which is scheduled\n# asynchronously after key presses via _on_key_press()"

But in _on_key_press() around line 1330:
Code shows: "# Schedule blank line removal after key is processed\nself.root.after(10, self._remove_blank_lines)"

The 10ms delay is not truly asynchronous - it's a scheduled callback. The comment implies a different mechanism than what's implemented.

---

#### code_vs_comment

**Description:** Comment about coordinate system mismatch doesn't match the actual error handling

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _highlight_current_statement() method around line 1650:
Comment says: "# Note: char_start/char_end from runtime are 0-based column offsets within the line.\n# Tk text widget uses 0-based column indexing, so these offsets directly map to\n# Tk indices. The parser ensures positions match the displayed line formatting.\n# If highlighting fails (try/except below), it indicates a mismatch between\n# runtime coordinate system and editor display (which would require investigation)."

But the try/except block just silently ignores TclError with "# Invalid index - ignore". If this truly "would require investigation" as the comment claims, the code should log the error or alert the developer, not silently ignore it.

---

#### code_vs_comment

**Description:** Comment about default behavior handling selection is incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_enter_key() method around line 1030:
Comment says: "# Check if there's a text selection - if yes, let default behavior handle it\n# (default behavior: delete selection, insert newline)"

But the code doesn't let default behavior handle it:
"if self.editor_text.text.tag_ranges(tk.SEL):\n    # There's a selection - delete it and insert newline\n    self.editor_text.text.delete(tk.SEL_FIRST, tk.SEL_LAST)\n    self.editor_text.text.insert(tk.INSERT, '\n')\n    return 'break'"

The code manually deletes and inserts, then returns 'break' to prevent default behavior. The comment is misleading.

---

#### code_vs_comment

**Description:** Comment about paste handling paths is confusing and partially incorrect

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_paste() method around line 1220:
Comment says: "# Multi-line paste or single-line paste into blank line - use auto-numbering logic\n# Note: Single-line paste into existing line uses different logic (inline paste above).\n# The auto-numbering path handles:\n# 1. Multi-line paste: sanitized_text contains \n → multiple lines to process\n# 2. Single-line paste into blank line: current_line_text empty → one line to process"

But the code flow shows:
1. If no newlines AND current line has content → inline paste (handled above)
2. Otherwise → auto-numbering path

The auto-numbering path is reached for:
- Multi-line paste (has \n)
- Single-line paste into blank line (no content)
- Single-line paste into existing line IF the earlier inline paste check was somehow bypassed

The comment's claim that "Single-line paste into existing line uses different logic" is only true if current_line_text is truthy, but the comment doesn't clearly explain this condition.

---

#### code_vs_comment

**Description:** Comment claims immediate mode execution doesn't echo commands, but this contradicts typical BASIC behavior without explaining why

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method:
Comment says: "Execute without echoing (GUI design choice that deviates from typical BASIC behavior: command is visible in entry field, and 'Ok' prompt is unnecessary in GUI context - only results are shown. Traditional BASIC echoes to output.)"

This comment acknowledges deviation from BASIC behavior but the rationale seems weak - the command being visible in entry field doesn't prevent echoing to output for history purposes. Traditional BASIC interpreters echo both command and result to maintain execution history.

---

#### code_vs_comment

**Description:** Dead code methods retained 'for potential future use' but marked as never called

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Three methods are marked as dead code:
1. _setup_immediate_context_menu() - "DEAD CODE: This method is never called because immediate_history is always None"
2. _copy_immediate_selection() - Referenced as dead code
3. _select_all_immediate() - Referenced as dead code

Comment says: "Retained for potential future use if immediate mode gets its own output widget."

Dead code should typically be removed from production code rather than retained with comments. If truly needed for future use, it should be in version control history or a feature branch.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about INPUT vs LINE INPUT behavior strategy

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler class docstring states:
"Input strategy rationale:
- INPUT statement: Uses inline input field when backend available (allowing the user to see program output context while typing input), otherwise uses modal dialog as fallback. This is availability-based, not a UI preference.
- LINE INPUT statement: Always uses modal dialog for consistent UX."

However, the input() method implementation shows:
"Prefers inline input field below output pane when backend is available, but falls back to modal dialog if backend is not available."

And input_line() shows:
"Unlike input() which prefers inline input field, this ALWAYS uses a modal dialog regardless of backend availability."

The documentation is consistent but the rationale for LINE INPUT always using modal dialog ('consistent UX') is weak - it would be more consistent to use the same input method for both INPUT and LINE INPUT.

---

#### code_vs_comment

**Description:** Comment about CLS behavior contradicts typical BASIC interpreter expectations

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In clear_screen() method:
"Design decision: GUI output is persistent for review. Users can manually clear output via Run > Clear Output menu if desired. CLS command is ignored to preserve output history during program execution."

This is a significant deviation from BASIC behavior where CLS is expected to clear the screen. While the rationale is provided, ignoring a standard BASIC command could confuse users expecting standard behavior. The comment doesn't indicate if this is documented elsewhere for users.

---

#### code_vs_comment

**Description:** Comment in _delete_line() describes parameter as 'Tkinter text widget line number (1-based sequential index)' but the implementation uses it as a line number that may no longer exist after deletion, suggesting it's actually a BASIC line number from line_metadata

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment says:
        Args:
            line_num: Tkinter text widget line number (1-based sequential index).
                     This is the position in the editor window (row 1, 2, 3, ...).
                     This is NOT a BASIC line number (e.g., 10, 20, 30).

But the code is called from _on_cursor_move() with self.current_line which tracks Tkinter line positions, and the function correctly uses it as a Tkinter line number. However, the docstring's emphasis suggests confusion about the distinction.

---

#### code_vs_comment

**Description:** The class docstring states 'Status priority (when both error and breakpoint): - ? takes priority (error shown) - After fixing error, ● becomes visible - Both set_error() and set_breakpoint() apply the same priority logic: error > breakpoint > blank (no special handling for clearing vs setting)'. However, the implementation in both set_error() and set_breakpoint() uses identical priority logic, which is correct, but the phrasing 'no special handling for clearing vs setting' is confusing because both methods DO handle clearing (when enabled=False or has_error=False).

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring claims: 'Both set_error() and set_breakpoint() apply the same priority logic: error > breakpoint > blank (no special handling for clearing vs setting)'

Both methods have:
if metadata['has_error']:
    metadata['status'] = '?'
elif metadata['has_breakpoint']:
    metadata['status'] = '●'
else:
    metadata['status'] = ' '

This IS special handling for clearing - when has_error=False and has_breakpoint=True, it shows '●'. The comment seems to mean 'no special case logic for the clearing operation itself' but the phrasing is unclear.

---

#### code_vs_comment

**Description:** The _on_cursor_move() method schedules line deletion with after_idle() and includes a detailed comment explaining why: 'Schedule deletion after current event processing to avoid interfering with ongoing key/mouse event handling (prevents cursor position issues, undo stack corruption, and widget state conflicts during event processing)'. However, the _delete_line() method doesn't have any corresponding comment explaining that it's designed to be called via after_idle(), which could lead to confusion if someone calls it directly.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_on_cursor_move() comment:
# Schedule deletion after current event processing to avoid interfering
# with ongoing key/mouse event handling (prevents cursor position issues,
# undo stack corruption, and widget state conflicts during event processing)
self.text.after_idle(self._delete_line, self.current_line)

_delete_line() has no comment about being designed for after_idle() usage.

---

#### code_vs_comment

**Description:** Comment in serialize_statement() claims 'REMARK is converted to REM during parsing, not here' but the code actually handles REMARK as a comment_type value

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Line ~730: Comment says '# Preserve comments using original syntax (REM or \')\n# Note: REMARK is converted to REM during parsing, not here'

But the code at line ~732 checks stmt.comment_type which could be 'APOSTROPHE', 'REM', 'REMARK', or default, suggesting REMARK is NOT converted during parsing and IS handled here.

The else clause at line ~734 says '# REM, REMARK, or default' confirming REMARK is a valid comment_type value that reaches this serialization code.

---

#### code_vs_comment

**Description:** Comment in serialize_statement() about unhandled statement types describes prevention strategy but doesn't match typical error handling patterns

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Lines ~810-817: Comment says:
'# For unhandled statement types, raise an error to prevent silent data corruption\n# Prevention strategy: Explicitly fail (with ValueError) rather than silently omitting\n# statements during RENUM, which would corrupt the program.\n# Note: There is no compile-time verification that all AST statement types are handled.\n# If new statement types are added to the parser, they won\'t be caught until runtime\n# when RENUM is attempted on code containing them. This is acceptable because the error\n# is explicit and prevents corruption (better than silently dropping statements).'

While the code does raise ValueError, the extensive justification in the comment suggests this was a debated design decision. The comment reads more like documentation or a design rationale than a typical inline comment explaining what the code does.

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

**Description:** Comment in FindReplaceDialog.show() says CodeMirror maintains scroll position, but no CodeMirror-specific code visible

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~565:
# Note: CodeMirror maintains scroll position automatically when dialog closes

This comment appears in the on_close() function, but there's no visible CodeMirror-specific code handling scroll position. The editor is self.backend.editor which is created as CodeMirror5Editor, but the automatic scroll position maintenance is not evident in the shown code.

---

#### code_vs_comment

**Description:** Comment claims RUN does NOT clear output, but this contradicts the design rationale comment about ASR33 teletype behavior

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1845 comment: 'Note: This implementation does NOT clear output (see comment at line ~1845 below).'
Line ~1847 comment: 'Don't clear output - continuous scrolling like ASR33 teletype'
Line ~1848 comment: 'Design choice: Unlike some modern BASIC interpreters that clear output on RUN, we preserve historical ASR33 behavior (continuous scrolling, no auto-clear).'

These comments are consistent with each other but the first comment's phrasing 'see comment at line ~1845 below' is self-referential and confusing since it appears AT line 1845.

---

#### code_vs_comment

**Description:** Comment claims INPUT statement prints prompt before setting input_prompt state, but this is stated twice with 'Verified:' suggesting uncertainty

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1932 in _execute_tick(): 'Note: We don't append the prompt to output here because the interpreter has already printed it via io.output() before setting input_prompt state. Verified: INPUT statement calls io.output(prompt) before awaiting user input.'

Line ~1945 (same method, repeated): 'Note: We don't append the prompt to output here because the interpreter has already printed it via io.output() before setting input_prompt state. Verified: INPUT statement calls io.output(prompt) before awaiting user input.'

The exact same comment appears twice in the same method, suggesting either copy-paste error or uncertainty about the behavior that required verification.

---

#### code_vs_comment

**Description:** Comment about interpreter/runtime object reuse contradicts the reset_for_run() behavior description

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2088 in _menu_step_stmt(): 'Note: Interpreter/runtime objects are reused across runs (not recreated each time). The runtime.reset_for_run() call above clears variables but preserves breakpoints.'

However, the code at lines ~2082-2087 shows:
```python
if self.runtime is None:
    self.runtime = Runtime(self.program.line_asts, self.program.lines)
    self.runtime.setup()
else:
    self.runtime.reset_for_run(self.program.line_asts, self.program.lines)
```

The comment says objects are 'reused across runs' but the code creates a NEW Runtime object if self.runtime is None. This suggests the runtime CAN be recreated, not just reused. The comment should clarify when runtime is None vs when it's reused.

---

#### code_vs_comment

**Description:** Comment about RUN with line number references a temporary attribute that may not exist

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1868 in _menu_run(): 'Check if RUN was called with a line number (e.g., RUN 120) This is set by immediate_executor when user types "RUN 120"'

The code checks for self._run_start_line attribute (lines ~1869-1874), but there's no visible code in this file that sets this attribute. The comment claims 'immediate_executor' sets it, but immediate_executor is not shown in the provided code. This creates uncertainty about whether this feature actually works or if the attribute is ever set.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime conditionally preserves PC based on exec_timer state, but code also checks if timer is active, creating redundant logic description

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says:
"PC handling (conditional preservation):
- If exec_timer is active (execution in progress): Preserves PC and halted state,
  allowing program to resume from current position after rebuild.
- Otherwise (no active execution): Resets PC to halted state, preventing
  unexpected execution when LIST/edit commands modify the program."

But then code comment repeats:
"# Conditionally restore PC based on whether execution timer is active
# This logic is about PRESERVING vs RESETTING state, not about preventing accidental starts"

The inline comment adds clarification about intent ("not about preventing accidental starts") that contradicts the docstring's claim about "preventing unexpected execution".

---

#### code_vs_comment

**Description:** Comment in _on_editor_change describes paste detection threshold as 'arbitrary' but provides specific reasoning that contradicts arbitrariness

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says:
"# Detect paste: large content change (threshold: >5 chars)
# This heuristic helps clear auto-number prompts before paste content merges with them.
# The 5-char threshold is arbitrary - balances detecting small pastes while avoiding
# false positives from rapid typing (e.g., typing \"PRINT\" quickly = 5 chars but not a paste)."

The comment claims the threshold is "arbitrary" but then provides specific reasoning (avoiding false positives from typing "PRINT"). If there's specific reasoning, it's not arbitrary - it's a heuristic with rationale.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate claims not to auto-sync editor from AST but doesn't explain why RENUM is an exception

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says:
"# Architecture: We do NOT auto-sync editor from AST after immediate commands.
# This preserves one-way data flow (editor → AST → execution) and prevents
# losing user's formatting/comments. Commands that modify code (like RENUM)
# update the editor text directly."

The comment establishes a rule (no auto-sync) then immediately describes an exception (RENUM updates editor directly) without explaining why RENUM is special or how it avoids the formatting/comment loss problem.

---

#### code_vs_comment

**Description:** Comment in _check_auto_number describes tracking 'last edited line text' but variable name is last_edited_line_text which could be entire content

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says:
"Check if we should auto-number lines without line numbers.

Tracks last edited line text to avoid re-numbering unchanged content."

But code does:
"current_text = self.editor.value or ''

# Don't auto-number if content hasn't changed
if current_text == self.last_edited_line_text:
    return"

The docstring says "last edited line text" (singular line) but the code compares entire editor content. The variable name last_edited_line_text is misleading - should be last_edited_content or similar.

---

#### code_vs_comment

**Description:** Comment in _on_enter_key says method is called by _on_editor_change but the method body is empty (pass equivalent)

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says:
"Handle Enter key press in editor - triggers auto-numbering.

Note: This method is called internally by _on_editor_change when a new line
is detected. The actual auto-numbering logic is in _add_next_line_number."

But method body is:
"# Auto-numbering on Enter is handled by _on_editor_change detecting new lines
# and calling _add_next_line_number via timer
pass"

This suggests the method is vestigial - it's documented as being called but does nothing. Either the method should be removed or the comment should explain why it exists as a no-op.

---

#### code_vs_comment

**Description:** Comment claims 'halted flag removed' and 'PC is now immutable', but code still calls PC.halted_pc() method

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~47 comment: '# Note: halted flag removed - PC is now immutable and indicates running state'
Line ~58 code: 'self.runtime.pc = PC(state['pc']['line'], state['pc']['stmt']) if state['pc'] else PC.halted_pc()'

The comment states the halted flag was removed and PC is immutable, but the code explicitly calls PC.halted_pc() to create a halted PC instance. This suggests either:
1. The comment is outdated and PC.halted_pc() is still a valid pattern
2. The code should use a different pattern to represent halted state

---

#### documentation_inconsistency

**Description:** Help URL inconsistency - code uses http://localhost/mbasic_docs but documentation mentions both this and deprecated http://localhost:8000

**Affected files:**
- `src/ui/web_help_launcher.py`
- `docs/help/README.md`

**Details:**
web_help_launcher.py line 17: HELP_BASE_URL = "http://localhost/mbasic_docs"

README.md mentions: "Help content is built using MkDocs and served locally at `http://localhost/mbasic_docs` for the Tk and Web UIs... (Legacy code may reference `http://localhost:8000`, which is deprecated in favor of the `/mbasic_docs` path.)"

However, the deprecated WebHelpLauncher_DEPRECATED class in web_help_launcher.py still uses port 8000 (line 68: self.server_port = 8000), creating confusion about which URL is actually used.

---

#### code_vs_documentation

**Description:** Settings dialog implements editor.auto_number settings but debugging.md does not mention auto-numbering configuration

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/debugging.md`

**Details:**
web_settings_dialog.py lines 66-82 implement auto-numbering settings:
- editor.auto_number (checkbox)
- editor.auto_number_step (number input with min=1, max=1000)
- Shows help text: "Common values: 10 (classic), 100 (large programs), 1 (dense)"

debugging.md extensively documents debugging features but does not mention that auto-numbering behavior can be configured, which could affect how users interact with line numbers during debugging.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-references between getting-started.md and language.md

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/language.md`

**Details:**
getting-started.md says 'For detailed reference documentation, see [BASIC Language Reference](language.md)' but language.md says 'For a beginner-friendly tutorial, see [Getting Started](getting-started.md)'. However, getting-started.md also links to [BASIC Language Reference](language/statements/index.md) in the 'Next Steps' section, creating confusion about whether language.md or language/statements/index.md is the main reference.

---

#### documentation_inconsistency

**Description:** Inconsistent precision information for SINGLE type

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/atn.md`

**Details:**
data-types.md states SINGLE has '~7 significant digits' and atn.md states 'evaluation of ATN is always performed in single precision (~7 significant digits)'. However, atn.md adds a note: 'When computing PI with ATN(1) * 4, the result is limited to single precision (~7 digits). For higher precision, use ATN(CDBL(1)) * 4 to get double precision.' This suggests ATN can work with double precision when given double precision input, contradicting the statement that it's 'always performed in single precision'.

---

#### documentation_inconsistency

**Description:** Missing INT function documentation but referenced in FIX

**Affected files:**
- `docs/help/common/language/functions/fix.md`
- `docs/help/common/language/functions/int.md`

**Details:**
fix.md states: 'FIX(X) is equivalent to SGN(X)*INT(ABS(X)). The major difference between FIX and INT is that FIX does not return the next lower number for negative X.' It also has 'See Also' link to INT. However, int.md is not provided in the documentation files, only referenced in the title attribute as 'Return the largest integer less than or equal to a number (floor function)'.

---

#### documentation_inconsistency

**Description:** Inconsistent PI precision examples

**Affected files:**
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
math-functions.md shows:
'PI = 3.1415927          ' Single-precision approximation
PI# = 3.141592653589793 ' Double-precision value'

But then states: 'REM Calculate PI (single-precision)
20 PI = ATN(1) * 4'

The computed value from ATN(1)*4 may not exactly match 3.1415927 due to rounding. The documentation should clarify that these are approximate values and the computed result may differ slightly.

---

#### documentation_inconsistency

**Description:** LOF function is documented in detail but missing from the index categorization

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
The index.md file lists LOF under 'File I/O Functions' in the alphabetical quick reference, but LOF is not listed in the 'By Category' section under 'File I/O Functions'. The category section lists: EOF, INPUT$, LOC, LOF (missing), LPOS, but LOF has a complete documentation file at lof.md.

---

#### documentation_inconsistency

**Description:** Inconsistent Control-C behavior documentation

**Affected files:**
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/input_dollar.md`

**Details:**
Both INKEY$ and INPUT$ document Control-C behavior with identical notes: 'Note: Control-C behavior varied in original implementations. In MBASIC 5.21 interpreter mode, Control-C would terminate the program. This implementation passes Control-C through (CHR$(3)) for program detection and handling, allowing programs to detect and handle it explicitly.' However, this note appears to be implementation-specific and may not belong in historical documentation sections.

---

#### documentation_inconsistency

**Description:** LPOS implementation note contradicts function purpose

**Affected files:**
- `docs/help/common/language/functions/lpos.md`

**Details:**
LPOS.md states: '⚠️ Not Implemented: This feature requires line printer hardware and is not implemented... Behavior: Function always returns 0'. However, the description section states: 'Returns the current position of the line printer print head within the line printer buffer. Does not necessarily give the physical position of the print head.' The phrase 'Does not necessarily give the physical position' suggests it should return buffer position, not physical position, but the implementation returns 0 (neither buffer nor physical position).

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

However, defint-sng-dbl-str.md doesn't clarify whether the DEF<type> statements themselves support multi-character variable name prefixes in original MBASIC or if this is also an extension. The example shows single-letter ranges (D-E, A, I-N, W-Z) which suggests original behavior, but multi-character variable names like 'NAME1$' and 'AMOUNT' are used without clarification.

---

#### documentation_inconsistency

**Description:** END documentation states files remain closed after CONT, but this behavior is not mentioned in STOP documentation

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/stop.md`

**Details:**
end.md states:
"Both END and STOP allow continuation with CONT. The key difference is that END closes all files before returning to command level, and these files remain closed even if execution is continued with CONT."

This important detail about file state persistence after CONT is only documented in END.md. The STOP.md file should also mention that files remain open after STOP+CONT for consistency.

---

#### documentation_inconsistency

**Description:** FIELD documentation warns against using FIELDed variables in INPUT/LET, but GET documentation doesn't mention this restriction

**Affected files:**
- `docs/help/common/language/statements/field.md`
- `docs/help/common/language/statements/get.md`

**Details:**
field.md states:
"**Note:** Do not use a FIELDed variable name in an INPUT or LET statement. Once a variable name is FIELDed, it points to the correct place in the random file buffer. If a subsequent INPUT or LET statement with that variable name is executed, the variable's pointer is moved to string space."

get.md shows an example using FIELDed variables (ITEM$, PRICE$, QTY$) but doesn't warn about this restriction. This is important information that should be cross-referenced.

---

#### documentation_inconsistency

**Description:** DEF FN Example 4 uses hexadecimal notation (&H5F) but the explanation could be clearer about the bit manipulation

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
Example 4 states:
"**Explanation:**
- Multi-character function name with type suffix
- Converts a single character to uppercase using bit manipulation
- `&H5F` is hexadecimal notation (hex 5F = decimal 95 = binary 01011111)
- `AND &H5F` clears bit 5 (the lowercase bit in ASCII), converting lowercase to uppercase
- For more on hexadecimal constants, see [Constants](../data-types.md)"

The explanation says 'clears bit 5' but the binary shown (01011111) has bit 5 SET (counting from bit 0). The operation actually CLEARS bit 5 of the input character by ANDing with a mask that has bit 5 clear (bit 5 = 0x20 = 00100000, so ~0x20 = 0xDF, but the code uses 0x5F which has bit 5 set). This appears to be an error in the explanation - AND with 0x5F would SET bit 5 to match the mask, not clear it. The correct mask to clear bit 5 would be 0xDF.

---

#### documentation_inconsistency

**Description:** HELPSETTING is listed in index.md under 'Modern Extensions' but uses 'MBASIC Extension' in its own documentation

**Affected files:**
- `docs/help/common/language/statements/helpsetting.md`
- `docs/help/common/language/statements/index.md`

**Details:**
helpsetting.md states:
"**Versions:** MBASIC Extension"

But index.md lists it under:
"### Modern Extensions (MBASIC only)"

The terminology should be consistent - either 'MBASIC Extension' or 'Modern Extensions (MBASIC only)' throughout.

---

#### documentation_inconsistency

**Description:** DEFINT/SNG/DBL/STR example shows type suffix overriding DEF declaration but doesn't explain precedence rules clearly in Remarks

**Affected files:**
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
The example shows:
"60 NAME1$ = "TEST"  ' String (starts with N, but $ suffix overrides DEFINT)"

And later states:
"**Type Declaration Precedence:**
- **Type suffix always wins:** `NAME1$` is string even though N→Z are declared integer"

However, the Remarks section earlier only says:
"A DEFtype statement declares that the variable names beginning with the letter(s) specified will be that type variable. However, a type declaration character always takes precedence over a DEFtype statement in the typing of a variable."

The precedence rule should be stated more prominently in the Remarks section before the example, not just in the example explanation.

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

#### documentation_inconsistency

**Description:** Incomplete error code information

**Affected files:**
- `docs/help/common/language/statements/kill.md`

**Details:**
KILL documentation mentions: 'a "File already open" error occurs (error code 55)'
This is the only statement documentation that provides a specific error code. Other file operation statements (OPEN, CLOSE, etc.) do not provide error codes, creating inconsistency in documentation completeness.

---

#### documentation_inconsistency

**Description:** LIMITS marked as MBASIC Extension but not consistently documented

**Affected files:**
- `docs/help/common/language/statements/limits.md`

**Details:**
LIMITS documentation states: 'Versions: MBASIC Extension' and 'This is a modern extension not present in original MBASIC 5.21'
However, no other documentation files reference LIMITS in their 'See Also' sections, and it's unclear if this is actually implemented or just documented.

---

#### documentation_inconsistency

**Description:** Contradictory information about file closing behavior

**Affected files:**
- `docs/help/common/language/statements/load.md`
- `docs/help/common/language/statements/merge.md`

**Details:**
LOAD documentation states: 'LOAD (without ,R): Closes all open files and deletes all variables'
'LOAD with ,R option: Program is RUN after loading, and all open data files are kept open'
'Compare with MERGE: Never closes files'

MERGE documentation states: 'Unlike LOAD (without ,R), MERGE does NOT close open files. Files that are open before MERGE remain open after MERGE completes.'

The comparison is clear, but LOAD's statement 'Compare with MERGE: Never closes files' is ambiguous - it could mean 'MERGE never closes files' or 'compare with MERGE which never closes files'. The phrasing should be clarified.

---

#### documentation_inconsistency

**Description:** Inconsistent string modification behavior documentation

**Affected files:**
- `docs/help/common/language/statements/lset.md`
- `docs/help/common/language/statements/mid-assignment.md`

**Details:**
LSET: 'If the string is shorter than the field defined by the string variable, the string is padded on the right with spaces. If the string is longer than the field, the extra characters on the right are truncated.'

MID$ Assignment: 'The string length never changes (no characters are added or removed). If length is specified, at most that many characters are replaced. If the replacement string is shorter than length, only the available characters are replaced.'

Both modify strings in place but with different padding/truncation behavior. LSET pads with spaces, MID$ does not add characters. This difference should be more clearly highlighted.

---

#### documentation_inconsistency

**Description:** Incomplete mode specification documentation

**Affected files:**
- `docs/help/common/language/statements/open.md`

**Details:**
OPEN documentation states modes as:
'"O" - specifies sequential output mode'
'"I" - specifies sequential input mode'
'"R" - specifies random input/output mode'

However, PRINTI-PRINTI-USING.md mentions 'mode "A"' for append:
'PRINT# writes data to a sequential file opened for output (mode "O") or append (mode "A")'

The OPEN documentation does not mention mode "A" for append, creating an inconsistency.

---

#### documentation_inconsistency

**Description:** Incomplete PRINT# USING format string documentation

**Affected files:**
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
PRINT# USING documentation lists format characters:
'# for digit positions'
'. for decimal point'
'$$ for floating dollar sign'
'** for asterisk fill'
', for thousands separator'

This is incomplete compared to full PRINT USING format strings which typically include more options like +, -, ^^^^ for exponential, etc. Either this should reference full PRINT USING docs or list all supported format characters.

---

#### documentation_inconsistency

**Description:** Maximum line number inconsistency

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
RENUM documentation states: 'Cannot create line numbers > 65529'

However, other documentation (e.g., ON...GOSUB) mentions line numbers up to 65535. The specific limit of 65529 should be verified and explained (likely related to internal representation or reserved values).

---

#### documentation_inconsistency

**Description:** Cross-reference inconsistency: RESET warns not to confuse with RSET, but RSET warns not to confuse with RESET. Both should reference each other consistently.

**Affected files:**
- `docs/help/common/language/statements/reset.md`
- `docs/help/common/language/statements/rset.md`

**Details:**
RESET.md says: 'Do not confuse RESET with [RSET](rset.md), which right-justifies strings in random file fields.'

RSET.md says: 'Do not confuse RSET with [RESET](reset.md), which closes all open files.'

Both warnings are correct but the phrasing suggests they are commonly confused. This is appropriate cross-referencing.

---

#### documentation_inconsistency

**Description:** Inconsistent description of file closing behavior across RUN, STOP, and SYSTEM statements

**Affected files:**
- `docs/help/common/language/statements/run.md`
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
RUN.md: 'All open files are closed (unlike STOP, which keeps files open)'

STOP.md: 'Unlike the END statement, the STOP statement does not close files.'

SYSTEM.md: 'When SYSTEM is executed: All open files are closed'

This creates confusion: RUN says STOP keeps files open, but doesn't mention what END does. STOP says END closes files. Need consistent messaging about which statements close files.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting and detail level between WAIT and WIDTH

**Affected files:**
- `docs/help/common/language/statements/wait.md`
- `docs/help/common/language/statements/width.md`

**Details:**
WAIT.md has brief note: '⚠️ **Not Implemented**: This statement is parsed for compatibility but performs no operation.'

WIDTH.md has detailed note with multiple sections:
'⚠️ **Not Implemented**: This statement is parsed for compatibility but performs no operation.

**Behavior**: The simple "WIDTH <number>" statement parses and executes successfully...
**Why**: Terminal and UI width is controlled by the operating system...
**Limitations**: The "WIDTH LPRINT" syntax is NOT supported...
**Alternative**: Terminal width is automatically handled...'

WAIT.md should have similar detailed explanation for consistency.

---

#### documentation_inconsistency

**Description:** Variables.md mentions variables.case_conflict setting but doesn't fully explain all options, while settings.md has complete details

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md: '**Case Sensitivity:** Variable names are not case-sensitive by default (Count = COUNT = count), but the behavior when using different cases can be configured via the `variables.case_conflict` setting, which controls whether the first occurrence wins, an error is raised, or a specific case preference is applied.'

settings.md provides full details:
'- `first_wins` - First occurrence sets the case (silent)
- `error` - Flag conflicts as errors
- `prefer_upper` - Choose most uppercase version
- `prefer_lower` - Choose most lowercase version
- `prefer_mixed` - Prefer mixed case (camelCase)'

variables.md should either link to settings.md or include the full list of options.

---

#### documentation_inconsistency

**Description:** shortcuts.md uses {{kbd:...}} template syntax that is not explained or defined anywhere

**Affected files:**
- `docs/help/common/shortcuts.md`
- `docs/help/common/settings.md`

**Details:**
shortcuts.md contains many instances like:
'{{kbd:run:cli}}'
'{{kbd:run:curses}}'
'{{kbd:run_program:tk}}'

This appears to be a template syntax for keyboard shortcuts, but there's no documentation explaining what these expand to or how they work. Users seeing the raw markdown would be confused.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about EDIT command availability and purpose

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`

**Details:**
CLI docs (index.md) state: 'The CLI includes a line editor accessed with the EDIT command' and 'Use EDIT to fix line 20', implying EDIT is a functional feature.

Curses docs (editing.md) state: 'The EDIT command is supported for compatibility with traditional BASIC, but the Curses UI provides full-screen editing capabilities that make it unnecessary.'

This creates confusion about whether EDIT is a real feature or just compatibility stub, and whether it works differently in CLI vs Curses.

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI file persistence

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
extensions.md states: 'Auto-save behavior varies by UI:
  - CLI, Tk, Curses: Save to local filesystem (persistent)
  - Web UI: Files stored in server-side session memory only (lost on page refresh or session end)'

compatibility.md states: 'Files stored in server-side memory (sandboxed filesystem per session)
- Files are lost on page refresh or when the session ends
- Settings (not files) persist in browser localStorage by default, or via Redis if configured
- Note: Session persistence means files survive multiple page operations within the same session, but a page refresh clears the session memory'

The compatibility.md note about 'Session persistence means files survive multiple page operations within the same session' contradicts the extensions.md claim that files are 'lost on page refresh or session end'. This needs clarification about what 'session' means and when exactly files are lost.

---

#### documentation_inconsistency

**Description:** Inconsistent information about PEEK/POKE implementation

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states: 'PEEK/POKE - Emulated for compatibility:
- POKE: Parsed and executes successfully, but performs no operation (no-op)
- PEEK: Returns random integer 0-255 (for RNG seeding compatibility)
- PEEK does NOT return values written by POKE - no memory state is maintained
- No access to actual system memory'

compatibility.md states the exact same thing in the 'Hardware-Specific Features' section.

However, architecture.md is in a 'Hardware Compatibility Notes' subsection under 'Interpreter Mode', while compatibility.md presents it as an 'Intentional Difference'. The framing is inconsistent - is this a compatibility note about the interpreter implementation, or an intentional difference from MBASIC 5.21?

---

#### documentation_inconsistency

**Description:** Incomplete information about debugging command availability across UIs

**Affected files:**
- `docs/help/mbasic/extensions.md`

**Details:**
The debugging commands section states availability as:
- BREAK: 'CLI (command form), Curses ({{kbd:toggle_breakpoint:curses}}), Tk (UI controls)'
- STEP: 'CLI (command form), Curses ({{kbd:step:curses}}/{{kbd:step_line:curses}}), Tk (UI controls)'
- STACK: 'CLI (command form), Curses (menu access), Tk (stack window)'

But there's no mention of Web UI availability for any of these commands. Given that Web UI is listed as one of the four main UIs, this omission is notable and potentially confusing.

---

#### documentation_inconsistency

**Description:** Contradictory information about WIDTH statement support

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
The compatibility guide states: 'WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The "WIDTH LPRINT" syntax is not supported.'

This creates confusion: if WIDTH is parsed and accepted, why specifically call out that 'WIDTH LPRINT' is not supported? This suggests partial implementation rather than a complete no-op, which contradicts the 'performs no operation' claim.

---

#### documentation_inconsistency

**Description:** Inconsistent information about Find/Replace availability across UIs

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/find-replace.md`
- `docs/help/mbasic/getting-started.md`

**Details:**
features.md states 'Find/Replace is not available in Curses UI. Use the Tk UI' and 'Find/Replace is not available in CLI. Use the Tk UI' and 'Find/Replace is not available in Web UI. Use the Tk UI', but find-replace.md for CLI provides detailed workarounds and alternative methods. The features.md document should either acknowledge these workarounds exist or be more specific that there's no built-in command (as find-replace.md correctly states).

---

#### documentation_inconsistency

**Description:** Debugging features availability inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
features.md states under Debugging: 'Breakpoints - Set/clear breakpoints (available in all UIs; access method varies)' and similar for step execution, variable viewing, and stack viewer. However, cli/debugging.md documents BREAK, STEP, and STACK commands as CLI-specific features. The features.md should clarify that these are CLI commands, while other UIs have different mechanisms (keyboard shortcuts, menu items, etc.).

---

#### documentation_inconsistency

**Description:** Inconsistent dependency information

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/index.md`

**Details:**
features.md states under Dependencies Required: 'Python 3.8+ - Interpreter only' and Optional: 'urwid 2.0+ - For Curses UI' and 'python-frontmatter 1.0+ - For help system'. However, index.md states 'Zero dependencies for core functionality'. This is technically correct but potentially confusing - should clarify that urwid is needed for the default Curses UI, making it effectively required for typical usage.

---

#### documentation_inconsistency

**Description:** LPRINT behavior inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md states 'LPRINT - Line printer output (Note: Statement is parsed but produces no output - see [LPRINT](../common/language/statements/lprint-lprint-using.md) for details)'. This suggests LPRINT is implemented but non-functional. not-implemented.md does not list LPRINT, implying it might be considered implemented. The status should be clarified - is it implemented (parsed) but non-functional, or truly not implemented?

---

#### documentation_inconsistency

**Description:** Web UI file storage limitations incomplete

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md states Web UI has 'Session-based storage - Files persist during browser session only (lost on page refresh)' and lists limitations like '50 file limit maximum, 1MB per file maximum'. However, it also says 'See [Compatibility Guide](compatibility.md) for complete Web UI file storage details' but the compatibility.md file is not provided in the documentation set to verify if this information is consistent or complete.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for toggling variables window

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/cli/variables.md`

**Details:**
curses/variables.md uses placeholder: "Press `{{kbd:toggle_variables:curses}}` to open the variables window."

cli/variables.md states: "The CLI does not have a Variables Window feature. For visual variable inspection, use:
- **Curses UI** - Full-screen terminal with Variables Window ({{kbd:toggle_variables:curses}})"

Both use the same placeholder but neither document shows the actual keyboard shortcut. The placeholder should be resolved to show the actual key combination.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about accessing Execution Stack

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
quick-reference.md states:
"| **Menu only** (Ctrl+U → Debug) | Toggle execution stack window |"

feature-reference.md states:
"### Execution Stack
View the call stack showing:

**Access methods:**
- Via menu: Ctrl+U → Debug → Execution Stack
- Via command: Type `STACK` in immediate mode (same as CLI)"

feature-reference.md mentions two access methods (menu and STACK command) while quick-reference.md only mentions the menu method. The STACK command should be added to quick-reference.md for completeness.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcuts for Variables Window operations

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
curses/variables.md lists under "Keyboard Reference":
"| Key | Action |
|-----|--------|
| `{{kbd:toggle_variables:curses}}` | Open/focus variables window |
| `Esc` | Close window |
| `Tab` | Switch between windows |
| `↑↓` | Navigate variables |
| `/` | Search |
| `f` | Filter |
| `s` | Sort |
| `r` | Refresh |
| `u` | Toggle auto-update |
| `e` | Export to file |
| `h` | Help |"

feature-reference.md lists under "Variables Window (when visible)":
"| Key | Action |
|-----|--------|
| **s** | Cycle sort mode (Accessed → Written → Read → Name) |
| **d** | Toggle sort direction (ascending ↑ / descending ↓) |
| **f** | Cycle filter mode (All → Scalars → Arrays → Modified) |
| **/** | Search for variable |
| **n** | Next search match |
| **N** | Previous search match |"

variables.md includes many more keys (r, u, e, h, Esc, Tab) that are not mentioned in feature-reference.md. feature-reference.md includes 'd' for sort direction and 'n/N' for search navigation that are not in variables.md's table.

---

#### documentation_inconsistency

**Description:** Inconsistent filter mode descriptions

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
curses/variables.md states:
"Press `f` to cycle through filters:
- **All**: Show all variables
- **Scalars**: Hide arrays
- **Arrays**: Show only arrays
- **Modified**: Show recently changed"

feature-reference.md states:
"**f** | Cycle filter mode (All → Scalars → Arrays → Modified)"

Both agree on the filter modes, but variables.md provides descriptions while feature-reference.md only lists the names. The descriptions should be consistent or cross-referenced.

---

#### documentation_inconsistency

**Description:** Inconsistent variable type documentation

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/cli/variables.md`

**Details:**
cli/variables.md lists "MBASIC has four variable types:
### Integer Variables
### Single-Precision (Float)
### Double-Precision
### String Variables"

curses/variables.md under "Variable Types Display" shows:
"### Type Indicators
```
Integer    : 42, -100, 32767
String     : "Hello", "Line 1", ""
Single (!) : 3.14159, -0.001, 1.5E10
Double (#) : 3.14159265359, 1.23E-100
Array      : Type[dimensions]
```"

curses/variables.md includes "Array" as a fifth type, while cli/variables.md only lists four types and mentions arrays separately under "## Arrays". The type system documentation should be consistent across UIs.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about Find/Replace availability

**Affected files:**
- `docs/help/ui/curses/find-replace.md`
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
find-replace.md states:
"## Current Status

The Curses UI currently **does not have** Find/Replace functionality for the editor. This feature is planned for future implementation.

**Note:** Search IS available in the Variables Window (press `/` while in the variables window to search for a variable by name). This document is specifically about Find/Replace in the program editor."

feature-reference.md states:
"### Find/Replace (Not yet implemented)
Find and Replace functionality is not yet available in Curses UI via keyboard shortcuts."

quick-reference.md states:
"**Note:** Find/Replace is not yet available in Curses UI. See [Find/Replace](find-replace.md) for workarounds."

All three documents agree it's not implemented, but find-replace.md provides the most detail including the important clarification about Variables Window search. This clarification should be added to the other documents.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Find/Replace

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md states: 'Find: {{kbd:find:tk}} - Opens Find dialog with search options... Replace: {{kbd:replace:tk}} - Opens combined Find/Replace dialog with find and replace options' with note 'Both dialogs support full search functionality. The Replace dialog includes all Find features plus replacement options.'

However, features.md states: '**Find text ({{kbd:find:tk}}):** Opens Find dialog... **Replace text ({{kbd:replace:tk}}):** Opens combined Find/Replace dialog' with note '{{kbd:find:tk}} opens the Find dialog. {{kbd:replace:tk}} opens the Find/Replace dialog which includes both Find and Replace functionality.'

The descriptions are slightly different in wording but convey the same meaning, which could be consolidated for consistency.

---

#### documentation_inconsistency

**Description:** Contradictory implementation status for Tk Settings Dialog

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/settings.md`

**Details:**
feature-reference.md does not mention that the settings dialog is unimplemented and lists features like 'Auto-Save' as if they are available through UI.

settings.md explicitly states: '**Implementation Status:** The Tk (Tkinter) desktop GUI is planned to provide a comprehensive settings dialog. **The settings dialog itself is not yet implemented - settings are currently managed programmatically.**' and '**Current Status:** Many TK UI features work (auto-save, syntax checking, breakpoints, etc.) but the graphical settings dialog is not yet implemented.'

This creates confusion about what is actually available in the Tk UI.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation about which features are implemented vs planned

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`

**Details:**
tips.md includes note: '**Note:** Some features described below (Smart Insert, Variables Window, Execution Stack) are documented here based on the Tk UI design specifications. Check [Settings](settings.md) for current implementation status...'

workflows.md includes note: '**Note:** The Tk UI has most features described below implemented (Smart Insert, Variables Window, Execution Stack, Renumber). The Settings dialog for configuring these features is planned but not yet implemented...'

feature-reference.md does not include any such implementation status warnings and presents all features as if they are fully implemented. This creates confusion about what is actually available.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for breakpoint toggling

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md states in 'Keyboard Shortcuts' section: '**Note:** {{kbd:toggle_breakpoint:web}} is implemented but currently available via menu only (not yet bound to keyboard).'

This is contradictory - if it's 'not yet bound to keyboard', it shouldn't be listed as a keyboard shortcut. The documentation should either list it as a menu-only feature or clarify that the shortcut binding exists but may not be functional.

---

#### documentation_inconsistency

**Description:** Inconsistent information about default UI

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/getting-started.md`

**Details:**
feature-reference.md does not mention which UI is default.

getting-started.md states: 'Or to use the default curses UI: mbasic [filename.bas]' - suggesting curses is the default.

However, index.md states under Curses UI: 'mbasic # Default UI' - confirming curses is default.

The inconsistency is that getting-started.md presents starting Tk UI first, then mentions curses as default, which could confuse users about which is actually the default interface.

---

#### documentation_inconsistency

**Description:** Contradictory information about step execution granularity

**Affected files:**
- `docs/help/ui/web/debugging.md`

**Details:**
debugging.md states in 'Debug Controls' section: '**Note:** The Web UI uses {{kbd:step:web}} for stepping. Statement-level stepping is not yet implemented.'

However, in 'Keyboard Shortcuts' section it states: '**Planned for Future Releases:** Statement-level stepping (execute one statement at a time)'

This is consistent, but earlier in 'Starting Debug Session' it lists 'Step ({{kbd:step:web}}) - Step to next line' without clarifying that this is line-level only, not statement-level. The documentation should be clearer upfront about the limitation.

---

#### documentation_inconsistency

**Description:** Inconsistent information about file operations and Recent Files feature

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
features.md under 'Local Storage > Currently Implemented' states: 'Recent files list (filenames only) stored in browser localStorage (persists across sessions)'

However, getting-started.md under 'Recent Files' section says: 'File → Recent Files shows recently opened files (saved in localStorage, persists across browser sessions).'

But getting-started.md also states under 'File Operations > Saving a File': 'Note: The Web UI uses browser downloads for saving program files to your computer. Auto-save of program code to browser localStorage is planned for a future release.'

The inconsistency: If program content is NOT saved to localStorage (only downloaded), how can Recent Files show 'recently opened files' that persist? Does it only show filenames without content? This needs clarification.

---

#### documentation_inconsistency

**Description:** Inconsistent descriptions of toolbar buttons and their functions

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
features.md under 'Execution Control > Currently Implemented' lists:
- Run ({{kbd:run:web}})
- Continue ({{kbd:continue:web}})
- Step statement ({{kbd:step:web}})
- Step line ({{kbd:step_line:web}})
- Stop ({{kbd:stop:web}})

getting-started.md under 'Toolbar' describes:
- Run - Parse and execute the program (▶️ green button, {{kbd:run:web}})
- Stop - Stop running program (⏹️ red button, {{kbd:stop:web}})
- Step - Execute all statements on current line, then pause (⏭️ button, {{kbd:step_line:web}})
- Stmt - Execute one statement, then pause (↻ button, {{kbd:step:web}})
- Cont - Resume normal execution after stepping (▶️⏸️ button, {{kbd:continue:web}})

web-interface.md under 'Toolbar' describes:
- Run (▶️ green) - Start program execution
- Stop (⏹️ red) - Stop running program
- Step (⏭️) - Execute all statements on current line
- Stmt (↻) - Execute one statement
- Cont (▶️⏸️) - Continue execution after pause

The inconsistency: The button labeled 'Step' in getting-started.md and web-interface.md corresponds to 'Step line' in features.md, while 'Stmt' corresponds to 'Step statement'. The naming is inconsistent across documents.

---

#### documentation_inconsistency

**Description:** Contradictory information about file I/O persistence and storage location

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
features.md under 'Local Storage > Currently Implemented' states: 'Program content stored in Python server memory (session-only, lost on page refresh)'

web-interface.md under 'File I/O' states: 'File operations in the web UI work with an in-memory filesystem:
- Files are stored in server memory (sandboxed, per-session)
- Each user/session has their own isolated filesystem
- Files persist during your session (but are lost on page refresh or session end)'

The inconsistency: Both describe server memory storage, but features.md says 'lost on page refresh' while web-interface.md says 'persist during your session (but are lost on page refresh or session end)'. The phrase 'persist during your session' followed by 'lost on page refresh' is contradictory since a page refresh typically maintains the session.

---

#### documentation_inconsistency

**Description:** Contradictory information about settings persistence and storage

**Affected files:**
- `docs/help/ui/web/settings.md`
- `docs/help/ui/web/features.md`

**Details:**
settings.md under 'Settings Storage > Local Storage (Default)' states: 'By default, settings are stored in your browser's localStorage. This means:
✅ Advantages:
- Settings persist across page reloads
- No server required'

However, features.md under 'Local Storage > Currently Implemented' states: 'Program content stored in Python server memory (session-only, lost on page refresh)' and 'Editor settings stored in browser localStorage (persists across sessions)'

The inconsistency: settings.md says settings persist across page reloads, but features.md says program content is lost on page refresh. The distinction between 'settings' and 'program content' needs to be clearer. Are settings separate from program content? If so, this should be explicitly stated in both documents.

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

'> **Note:** CLI has full debugging capabilities through text commands (BREAK, STEP, STACK, etc.), but lacks visual debugging features (Variables Window, clickable breakpoints, graphical interface) found in Curses, Tk, and Web UIs.'

However, QUICK_REFERENCE.md is titled 'MBASIC Curses IDE - Quick Reference Card' and only documents Curses UI debugging with keyboard shortcuts like 'b' or 'F9' for breakpoints and 'c', 's', 'e' for continue/step/end. No CLI text commands are documented.

---

#### documentation_inconsistency

**Description:** Contradictory information about CLI dependencies

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
INSTALL.md states:
'| UI Mode | External Dependencies |
|---------|----------------------|
| **CLI** | None (Python standard library only) |'

and

'**If you only want CLI mode**, you can skip all pip dependency installation steps. Just run `python3 mbasic` and you're ready to go!'

CHOOSING_YOUR_UI.md confirms this:
'**CLI**
```bash
# Just Python 3.8+
python3 mbasic
```'

However, CHOOSING_YOUR_UI.md also lists CLI debugging commands (BREAK, STEP, STACK) which are not documented anywhere in the provided files, creating uncertainty about whether these are actually implemented or require additional dependencies.

---

#### documentation_inconsistency

**Description:** Performance measurements lack context and disclaimers are inconsistent

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
CHOOSING_YOUR_UI.md provides specific performance numbers:
'### Startup Time
1. **CLI**: ~0.1s (fastest)
2. **Curses**: ~0.3s
3. **Tk**: ~0.8s
4. **Web**: ~2s (includes browser launch time)'

The disclaimer states:
'> **Note:** These measurements are approximate, taken on typical development hardware (modern CPU, 8GB+ RAM, Python 3.9+). Actual performance varies based on your system. Startup times are "cold start" measurements. Memory usage shown is Python process only; Web UI browser memory not included.'

However, the Memory Usage section contradicts this:
'### Memory Usage (approximate)
1. **CLI**: 20MB (lowest)
2. **Curses**: 25MB
3. **Tk**: 40MB
4. **Web**: 50MB+ (Python process only; browser adds 100MB+)'

The Web UI memory note appears in both the disclaimer and the list, but the disclaimer says 'browser memory not included' while the list says 'browser adds 100MB+', creating confusion about whether browser memory is counted or not.

---

#### documentation_inconsistency

**Description:** Contradictory information about Curses UI mouse support

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
CHOOSING_YOUR_UI.md lists conflicting information about Curses mouse support:

In the comparison table:
'| **Mouse support** | ❌ | ⚠️ Limited | ✅ | ✅ |'
(Curses shows 'Limited')

In the Curses section:
'**Limitations:**
- Limited mouse support'

But also in the Curses section:
'**Unique advantages:**
- Keyboard shortcuts'

And in the Decision Matrix:
'| **Mouse support** | ❌ | ⚠️ Limited | ✅ | ✅ |'

The document never explains what 'Limited' mouse support means in Curses, leaving users uncertain about what mouse functionality is actually available.

---

#### documentation_inconsistency

**Description:** Settings file location inconsistency between documents

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
INSTALL.md mentions settings files:
'Settings files are automatically created in ~/.mbasic/settings.json (Linux/Mac) or %APPDATA%/mbasic/settings.json (Windows).'

SETTINGS_AND_CONFIGURATION.md provides more detail:
'**Location:**
- **Linux/Mac:** `~/.mbasic/settings.json`
- **Windows:** `%APPDATA%/mbasic/settings.json` (typically `C:\Users\YourName\AppData\Roaming\mbasic\settings.json`)'

Both documents agree on the paths, but INSTALL.md says files are 'automatically created' while SETTINGS_AND_CONFIGURATION.md shows manual creation:
'```bash
mkdir -p .mbasic
cat > .mbasic/settings.json << 'EOF'
...'

This creates confusion about whether users need to manually create settings files or if they're auto-generated.

---

#### documentation_inconsistency

**Description:** Incomplete keyboard shortcut documentation

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`

**Details:**
QUICK_REFERENCE.md uses template notation for keyboard shortcuts:
'| `{{kbd:new}}` | New | Clear program, start fresh |'
'| `{{kbd:open}}` | Load | Load program from file |'
'| `{{kbd:save}}` | Save | Save program to file |'
'| `{{kbd:quit}}` | Quit | Exit IDE |'
'| `{{kbd:help}}` | Help | Open help browser |'
'| `{{kbd:run}}` | Run | Execute current program |'

The document explains:
'> **Note:** This reference uses `{{kbd:command}}` notation for keyboard shortcuts (e.g., `{{kbd:run}}` is typically `^R` for Ctrl+R). Actual key mappings are configurable. To see your current key bindings, press the Help key or check `~/.mbasic/curses_keybindings.json` for the full list of default and customized keys.'

However, the document never provides the actual default key mappings (like Ctrl+R for run), forcing users to either press Help or check the JSON file. This makes the quick reference less useful as a standalone document.

---

#### documentation_inconsistency

**Description:** Decision Matrix uses different symbols than comparison table

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
CHOOSING_YOUR_UI.md has two comparison tables with inconsistent symbols:

First table (UI Comparison at a Glance) uses text:
'| UI | Best For | Avoid If |'

Decision Matrix uses symbols:
'| **No dependencies** | ✅ | ❌ | ❌ | ❌ |'
'| **Mouse support** | ❌ | ⚠️ Limited | ✅ | ✅ |'

The Decision Matrix also introduces a new symbol (⚠️) not used in the first table, and uses different terminology ('No dependencies' vs the earlier discussion of dependencies). This inconsistency makes it harder to cross-reference between tables.

---

#### documentation_inconsistency

**Description:** Contradictory information about SET command persistence

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states:
'**Using SET command (in BASIC):**
```basic
SET "variables.case_conflict" "error"
SET "editor.auto_number" true
```'

Then later:
'Note: Both methods are equivalent. SET commands affect the current session; JSON files persist across sessions.'

But in the Troubleshooting section:
'Settings in files persist across sessions. Settings via `SET` command only affect current session.'

The phrase 'Both methods are equivalent' contradicts the statement that SET commands only affect the current session while JSON files persist. They are NOT equivalent in terms of persistence.

---

#### documentation_inconsistency

**Description:** TK_UI_QUICK_START.md references keyboard shortcuts for Tk UI but keyboard-shortcuts.md only documents Curses UI shortcuts

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md uses template notation like {{kbd:run_program}}, {{kbd:file_save}}, {{kbd:smart_insert}}, {{kbd:renumber}}, {{kbd:toggle_variables}}, {{kbd:toggle_stack}}, {{kbd:toggle_breakpoint}}, {{kbd:replace}}, {{kbd:file_open}}, {{kbd:file_new}}, {{kbd:help_topics}}, {{kbd:file_quit}} for Tk UI.

However, keyboard-shortcuts.md is titled 'MBASIC Curses UI Keyboard Shortcuts' and only documents Curses shortcuts like Ctrl+R (Run), Ctrl+V (Save), Ctrl+N (New), Ctrl+O (Open), Ctrl+H (Help), Ctrl+Q (Quit), Ctrl+B (Toggle breakpoint), Ctrl+W (Toggle variables), Ctrl+E (Renumber), Ctrl+T (Step statement), Ctrl+K (Step Line), Ctrl+C (Continue), Ctrl+X (Stop).

No separate keyboard-shortcuts.md file exists for Tk UI, despite TK_UI_QUICK_START.md referencing 'See [Tk Keyboard Shortcuts](keyboard-shortcuts.md)'.

---

#### documentation_inconsistency

**Description:** Conflicting information about Step/Continue/Stop keyboard shortcuts in Tk UI

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md states: 'Note: Step, Continue, and Stop are available via toolbar buttons or the Run menu (no keyboard shortcuts).'

However, UI_FEATURE_COMPARISON.md in the 'Debugging Shortcuts' table shows:
- Step: 'Menu/Toolbar' for Tk
- Continue: 'Menu/Toolbar' for Tk
- Stop: 'Esc' for Tk

This indicates Stop DOES have a keyboard shortcut (Esc) in Tk UI, contradicting the TK_UI_QUICK_START.md statement.

---

#### documentation_inconsistency

**Description:** Conflicting information about CLI save functionality

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md Feature Availability Matrix shows:
- 'Save (interactive)' for CLI: ❌
- 'Save (command)' for CLI: ✅
- Notes: 'Keyboard shortcut prompts for filename'

Under 'Detailed UI Descriptions' → 'CLI (Command Line Interface)' → 'Limitations':
- 'No interactive save prompt (must use SAVE "filename" command)'

Under 'Known Gaps':
- 'CLI: No interactive save prompt (use SAVE "filename" command instead)'

However, the 'Common Shortcuts' table shows:
- Save for CLI: {{kbd:save:cli}}

This suggests CLI has a save keyboard shortcut, but the feature matrix and limitations say there's no interactive save. The Notes column says 'Keyboard shortcut prompts for filename' which contradicts the ❌ for CLI.

---

#### documentation_inconsistency

**Description:** Conflicting information about variable editing in Curses UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md Feature Availability Matrix shows:
- 'Edit variables' for Curses: ⚠️
- Notes: 'CLI: immediate mode only'

Under 'Detailed UI Descriptions' → 'Curses (Terminal UI)' → 'Limitations':
- 'Partial variable editing'

Under 'Coming Soon':
- ⏳ Variable editing in Curses

Under 'Known Gaps':
- Curses: Limited variable editing

The ⚠️ symbol means 'Partially implemented' according to the legend, but 'Coming Soon' lists it as ⏳ (not yet available). This is contradictory - is variable editing partially implemented or planned?

---

### 🟢 Low Severity

#### Code vs Comment conflict

**Description:** LineNode docstring claims text is regenerated but doesn't explain the mechanism fully

**Affected files:**
- `src/ast_nodes.py`

**Details:**
LineNode docstring (lines 127-148) says:
"Design note: This class intentionally does not have a source_text field to avoid
maintaining duplicate copies that could get out of sync with the AST during editing.
Text regeneration is handled by the src.position_serializer module which reconstructs
source text from statement nodes and their token information."

However, the docstring references 'src.position_serializer' module which is not shown in the provided files. This could be correct but cannot be verified from the provided code.

---

#### Code vs Comment conflict

**Description:** RemarkStatementNode comment_type field default may not match actual parser behavior

**Affected files:**
- `src/ast_nodes.py`

**Details:**
RemarkStatementNode (lines 717-729) has:
comment_type: str = "REM"  # Original syntax: "REM", "REMARK", or "APOSTROPHE"

The docstring says: "The parser sets this to 'REM', 'REMARK', or 'APOSTROPHE' based on input"

However, the default value is "REM". If the parser always sets this field explicitly, the default should not matter. If the parser sometimes doesn't set it, then defaulting to "REM" might not preserve the original syntax correctly. This needs clarification about whether the parser always sets this field.

---

#### Documentation inconsistency

**Description:** ChainStatementNode delete_range type annotation inconsistency

**Affected files:**
- `src/ast_nodes.py`

**Details:**
ChainStatementNode (line 507) has:
delete_range: Optional[Tuple[int, int]] = None  # (start_line_number, end_line_number) for DELETE option

The comment says "(start_line_number, end_line_number)" but the type is Tuple[int, int]. This is consistent, but the naming could be clearer. The tuple contains line numbers, not arbitrary integers. Consider using a more descriptive type alias or named tuple.

---

#### Code vs Comment conflict

**Description:** CallStatementNode arguments field default_factory usage

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode (line 768) uses:
arguments: List['ExpressionNode'] = field(default_factory=list)

This is correct usage of dataclasses, but other similar nodes in the file use:
arguments: List['ExpressionNode']

without a default. This inconsistency suggests CallStatementNode was added later or refactored differently. While not technically wrong, it's inconsistent with the pattern used elsewhere (e.g., FunctionCallNode line 1073 has no default for arguments).

---

#### Documentation inconsistency

**Description:** TypeInfo class docstring describes it as both utility class and compatibility layer

**Affected files:**
- `src/ast_nodes.py`

**Details:**
TypeInfo docstring (lines 1145-1157) says:
"This class serves two purposes:
1. Static helper methods for type conversions (from_suffix, from_token, etc.)
2. Compatibility layer: Class attributes (INTEGER, SINGLE, etc.) alias VarType
   enum values to support legacy code that used TypeInfo.INTEGER instead of
   VarType.INTEGER. This allows gradual migration without breaking existing code.
   Note: New code should use VarType enum directly."

However, the class only has from_suffix and from_def_statement methods, not from_token. The docstring mentions "from_token, etc." but from_token doesn't exist. This is a minor documentation error.

---

#### Code vs Comment conflict

**Description:** StatementNode char_start/char_end documentation references UI code not shown

**Affected files:**
- `src/ast_nodes.py`

**Details:**
StatementNode docstring (lines 186-193) says:
"Note: char_start/char_end are populated by the parser and used by:
- UI highlighting: tk_ui._highlight_current_statement() highlights the currently executing
  statement by underlining the text from char_start to char_end
- Position serializer: Preserves exact character positions for text regeneration
- Cursor positioning: Determines which statement the cursor is in during editing"

This references tk_ui._highlight_current_statement() which is not in the provided files. While this is likely correct, it cannot be verified from the provided code. The comment makes specific claims about implementation details in other modules.

---

#### code_vs_comment

**Description:** INPUT() function docstring describes BASIC syntax with # prefix but implementation receives numeric file_num without #

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring states:
"BASIC syntax:
    INPUT$(n) - read n characters from keyboard
    INPUT$(n, #filenum) - read n characters from file

Python call syntax (from interpreter - # prefix already stripped by parser):
    INPUT(n) - read n characters from keyboard
    INPUT(n, filenum) - read n characters from file"

This is actually consistent - the comment correctly explains that the parser strips the # prefix. However, the phrasing 'This method receives the file number WITHOUT the # prefix (parser strips it)' could be clearer that this is expected behavior, not a limitation.

---

#### documentation_inconsistency

**Description:** Module docstring references BASIC-80 Reference Manual Version 5.21 but doesn't specify where to find this reference

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Module docstring states:
"Built-in functions for Microsoft BASIC-80 (from BASIC-80 Reference Manual Version 5.21).

Note: This implementation follows BASIC-80 Reference Manual Version 5.21, which documents
Microsoft BASIC-80 as implemented for CP/M systems."

No URL, ISBN, or other reference information is provided for locating this manual.

---

#### code_vs_comment

**Description:** Comment claims identifiers preserve original case but doesn't explain case-insensitive matching happens elsewhere

**Affected files:**
- `src/case_string_handler.py`

**Details:**
Comment in case_keepy_string() states:
"Identifiers (variable/function names) always preserve original case in display.
Unlike keywords (which follow case_style policy), identifiers retain case as typed.
This matches MBASIC 5.21: identifiers are case-insensitive for matching but
preserve display case. Case-insensitive matching happens at runtime and during
parsing (using normalized forms), while this function only handles display formatting."

The comment correctly describes the behavior but could be clearer that the case-insensitive matching is implemented in other parts of the codebase (not shown in provided files), not in this function.

---

#### code_vs_comment

**Description:** EOF() function comment references execute_open() with search hint but file is not in provided sources

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment states:
"See execute_open() in interpreter.py for file opening implementation (search for 'execute_open')"

The file interpreter.py is not provided in the source files, making this reference unverifiable and potentially confusing for developers working with only the provided files.

---

#### documentation_inconsistency

**Description:** Documentation mentions duplicate two-letter codes but doesn't explain practical implications

**Affected files:**
- `src/error_codes.py`

**Details:**
error_codes.py documents:
"Note: Some two-letter codes are duplicated across different numeric error codes.
This matches the original MBASIC 5.21 specification where the two-letter codes
alone are ambiguous - the numeric code is authoritative.

Specific duplicates (from MBASIC 5.21 specification):
- DD: code 10 (\"Duplicate definition\") and code 68 (\"Device unavailable\")
- DF: code 25 (\"Device fault\") and code 61 (\"Disk full\")
- CN: code 17 (\"Can't continue\") and code 69 (\"Communication buffer overflow\")"

However, the get_error_message and format_error functions only accept numeric codes, making the two-letter code duplication irrelevant to the implementation. The documentation doesn't explain if/how two-letter codes are used elsewhere in the system, or if this is purely historical information.

---

#### code_comment_conflict

**Description:** GOSUB stack size is hardcoded but not documented as a limitation

**Affected files:**
- `src/codegen_backend.py`

**Details:**
In generate method:
code.append(self.indent() + 'int gosub_stack[100];  /* Return IDs (0, 1, 2...) - not line numbers */')

The GOSUB stack is hardcoded to 100 entries, but:
1. Class docstring doesn't mention this as a limitation
2. No runtime check for stack overflow
3. No compile-time warning if program has deeply nested GOSUBs
4. Comment explains what's stored but not the size limitation

Programs with >100 nested GOSUB calls will have undefined behavior (stack overflow).

---

#### code_comment_conflict

**Description:** Comment about type promotion is incomplete

**Affected files:**
- `src/codegen_backend.py`

**Details:**
In _get_expression_type method:
elif isinstance(expr, BinaryOpNode):
    # For simplicity, use the type of the left operand
    # In reality, we'd need type promotion rules
    return self._get_expression_type(expr.left)

The comment acknowledges type promotion is needed but doesn't explain:
1. What the current behavior is (uses left operand type)
2. What problems this causes (e.g., 1 + 2.5 would be treated as integer)
3. Whether this is a known limitation
4. What the correct type promotion rules would be

This could lead to incorrect code generation for mixed-type expressions.

---

#### Code vs Comment conflicts

**Description:** InMemoryFileHandle.flush() docstring says content is saved on close(), but code shows content is saved via _save_file_content() which is only called on close()

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
InMemoryFileHandle.flush() docstring:
"Flush write buffers (no-op for in-memory files).

Calls the underlying StringIO/BytesIO flush() method, which is a no-op.
In-memory file writes are already in memory, so flush() has no practical effect.
Content is only logically 'saved' to the virtual filesystem on close()."

The code in close() method:
```python
if 'w' in self.mode or 'a' in self.mode or '+' in self.mode:
    # Save content back to virtual filesystem
    self.file_obj.seek(0)
    content = self.file_obj.read()
    self.fs_provider._save_file_content(self.filename, content)
```

This is actually consistent - the comment correctly describes the behavior. However, the phrasing "Content is only logically 'saved' to the virtual filesystem on close()" could be clearer that it means _save_file_content() is called on close(), not that close() has special logic beyond calling that method.

---

#### Code vs Documentation inconsistencies

**Description:** SandboxedFileSystemProvider.__init__() docstring has redundant security notes about user_id validation

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The __init__() docstring contains multiple overlapping warnings about user_id security:

1. In Args section: "SECURITY: Must be securely generated/validated (e.g., session IDs)
to prevent cross-user access. Do NOT use user-provided values."

2. After Args: "NOTE: This class does NOT validate user_id - validation is the
caller's responsibility. Passing an untrusted/user-provided value
creates a security vulnerability (cross-user filesystem access)."

3. In code comment: "# NOTE: user_id is accepted as-is without validation. Caller must ensure
# it is securely generated (e.g., from session management, crypto-secure IDs)
# and NOT from user-provided input."

While repetition for security warnings can be justified, having three separate warnings saying essentially the same thing in different words within the same method is excessive and could indicate documentation debt.

---

#### Documentation inconsistencies

**Description:** Inconsistent terminology for storage location in SandboxedFileIO

**Affected files:**
- `src/file_io.py`

**Details:**
SandboxedFileIO class docstring uses multiple terms for the same concept:
- "server memory virtual filesystem" (in load_file, save_file, delete_file, file_exists docstrings)
- "in-memory virtual filesystem" (in class docstring: "in-memory virtual filesystem stored in server memory")
- "Python server memory" (in class docstring: "Storage location: In-memory virtual filesystem stored in server memory")
- "sandboxed filesystem" (in list_files docstring: "List files in sandboxed filesystem")

While these all refer to the same thing, using consistent terminology would improve clarity.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for program state checking

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The class docstring uses multiple terms inconsistently:

1. "PC is not running (program stopped) - Any reason: idle, paused, at breakpoint, done"
2. "state.interpreter.runtime.pc.is_running() is True - Program is executing a statement"
3. In can_execute_immediate(): "Program is halted (paused/done/breakpoint)"
4. "NOT safe when program is actively running"

The terms 'stopped', 'halted', 'not running', and 'paused' are used interchangeably without clear definitions. The relationship between pc.is_running() and pc.halted() is unclear.

---

#### code_vs_comment_conflict

**Description:** Comment about validation contradicts actual function behavior

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
In sanitize_input() docstring:

"Note: This function is typically called after clear_parity_all() in the sanitize_and_clear_parity() pipeline, where parity bits have already been cleared. It filters out characters outside the valid range (32-126, plus tab/newline/CR). This indirectly rejects any characters with bit 7 set (codes >= 128), but does NOT validate that parity clearing actually occurred."

The comment says it "does NOT validate that parity clearing actually occurred" but then the module docstring says:

"Note: sanitize_input() does NOT validate that parity clearing occurred before it's called - it simply filters out any characters with codes >= 128 (which indirectly rejects characters that still have bit 7 set). For proper validation, always use sanitize_and_clear_parity() which explicitly clears parity before filtering."

Both comments agree sanitize_input() doesn't validate parity clearing, but the phrasing suggests there should be validation when there isn't any validation code present. The function just filters characters - it doesn't validate anything about what happened before.

---

#### documentation_inconsistency

**Description:** Inconsistent error message formatting in help text vs implementation

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The help text shows:
"LIMITATIONS:
  • INPUT statement will fail at runtime in immediate mode (use direct assignment instead)"

But _format_error() returns various error formats:
- "Type mismatch\n"
- "Syntax error\n"
- "?RuntimeError: {exception}\n"
- "Undefined variable\n"

There's no specific error message for INPUT failures mentioned in the help, and the error formatting is inconsistent (some with ?, some without, some with error type names).

---

#### code_vs_comment

**Description:** Comment says 'Not yet implemented: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K)' but doesn't specify implementation plan

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring at line ~1030 states: 'Not yet implemented: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K).'

Later comment at line ~1050 says: 'Future enhancement will add explicit digit parsing to accumulate count prefixes for commands like [n]D, [n]C, [n]S.'

These comments describe the same missing feature but with slightly different wording and placement. The docstring should be the authoritative source for what's implemented vs not implemented.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'immediate mode' vs 'direct command'

**Affected files:**
- `src/interactive.py`

**Details:**
Module docstring uses both terms:
- Line 7: 'Direct commands: AUTO, EDIT, HELP (special-cased before parser, see execute_command())'
- Line 8: 'Immediate mode statements: Most commands (RUN, LIST, SAVE, LOAD, NEW, MERGE, FILES, SYSTEM, DELETE, RENUM, CONT, CHAIN, etc.) are parsed as BASIC statements and executed via execute_immediate()'

But execute_command() docstring at line ~280 says: 'Execute a direct command or immediate mode statement'

This suggests 'direct command' and 'immediate mode statement' are different things, but the distinction isn't clearly defined. The module docstring implies AUTO/EDIT/HELP are 'direct commands' while RUN/LIST/etc are 'immediate mode statements', but execute_command() treats them as overlapping categories.

---

#### code_vs_comment

**Description:** Comment about readline Ctrl+A binding is verbose but accurate

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at line ~90 explains Ctrl+A binding:
'Bind Ctrl+A to insert the character (ASCII 0x01) into the input line, overriding the default Ctrl+A (beginning-of-line) behavior. When the user presses Ctrl+A, readline\'s \'self-insert\' action inserts the 0x01 character into the input buffer (the input line becomes just "^A"). When the user then presses Enter, the input is returned to the application. The start() method detects this character in the returned input and enters edit mode.'

This is accurate and matches the code at line ~140 in start() which checks 'if line and line[0] == '\x01''. However, the comment is very detailed for a simple keybinding. This is more of a style issue than an inconsistency.

---

#### code_vs_comment_conflict

**Description:** Comment about GOTO/GOSUB behavior in immediate mode describes complex transient jump behavior that may confuse users

**Affected files:**
- `src/interactive.py`

**Details:**
Comment at lines ~485-493 describes:
"Note: GOTO/GOSUB in immediate mode work but PC restoration affects CONT behavior:
They execute and jump during execute_statement(), but we restore the
original PC afterward to preserve CONT functionality. This means:
- The jump happens and target code runs during execute_statement()
- The final PC change is then reverted, preserving the stopped position
- CONT will resume at the original stopped location, not the GOTO target"

This describes a potentially confusing behavior where GOTO/GOSUB execute but their PC changes are reverted. The comment warns "use this feature cautiously" but this behavior is not documented in user-facing help or documentation.

---

#### documentation_inconsistency

**Description:** cmd_files docstring mentions drive letter syntax is not supported, but this limitation is not mentioned in cmd_help

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_files docstring (line ~425):
"Note: Drive letter syntax (e.g., \"A:*.*\") from CP/M and DOS is not supported.
This is a modern implementation running on Unix-like and Windows systems where
CP/M-style drive letter prefixes don't apply."

But cmd_help (line ~395) only shows:
"  FILES [\"pattern\"]  - List files"

No mention of the drive letter limitation in the help text that users would see.

---

#### code_vs_comment_conflict

**Description:** Comment about sanitize_and_clear_parity return value is unnecessarily verbose for unused value

**Affected files:**
- `src/interactive.py`

**Details:**
At line ~350:
"# Sanitize input: clear parity bits and filter control characters
# (second return value is bool indicating if parity bits were found; not needed here)
line_text, _ = sanitize_and_clear_parity(line_text)"

The comment explains the second return value in detail even though it's immediately discarded with underscore. This pattern appears only here; similar calls elsewhere don't have this verbose comment about unused return values.

---

#### code_vs_comment

**Description:** InterpreterState docstring lists execution order but omits error_info clearing step that occurs in execute_goto and execute_return

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 44-56 describes tick_pc() execution order:
"1. pause_requested check
2. is_running() check
3. break_requested check
4. breakpoints check
5. trace output
6. statement execution (with error handling in try/except) - sets input_prompt or error_info
7. input_prompt check
8. PC advancement"

But execute_goto (line 717) and execute_return (line 843) both clear error_info:
if self.state.error_info is not None:
    self.state.error_info = None
    self.runtime.set_variable_raw('err%', 0)

This error clearing happens during step 6 (statement execution) but isn't mentioned in the execution order description.

---

#### code_vs_comment

**Description:** execute_next docstring says method doesn't handle colon-separated NEXT statements, but this is parser behavior not interpreter behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 920-927 says:
"Note: This method handles a single NEXT statement, which may contain comma-separated variables (NEXT I, J, K). The parser treats colon-separated NEXT statements (NEXT I: NEXT J: NEXT K) as distinct statements, each calling execute_next() independently. This method does NOT handle the colon-separated case - that's handled by the parser creating multiple statements."

This note is technically correct but potentially confusing - execute_next() doesn't need to 'handle' colon-separated statements because the parser already split them into separate statements. The note implies execute_next() is making a choice not to handle them, when really it never sees them as a single statement. The comment is accurate but could be clearer about the division of responsibility.

---

#### documentation_inconsistency

**Description:** Comment mentions 'version 1.0.299' for removal of old execution methods, but no version tracking is visible in the provided code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 502-509 says:
"# OLD EXECUTION METHODS REMOVED (version 1.0.299)
# Note: The project has an internal implementation version (tracked in src/version.py)
# which is separate from the MBASIC 5.21 language version being implemented."

The comment references src/version.py for version tracking, but this file is not included in the provided source code. This makes it impossible to verify the version claim or understand the versioning scheme. This is a documentation completeness issue rather than an inconsistency within the provided file.

---

#### code_vs_comment

**Description:** Comment says error handler check is at line 392, but actual check is at line 376

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 526 says:
"This method is only called if a handler exists (checked at line 392)"

But the actual handler existence check is at line 376:
if self.runtime.has_error_handler() and not already_in_error_handler:

The line number reference is incorrect, likely due to code modifications after the comment was written.

---

#### code_vs_comment

**Description:** Comment states WEND pops loop 'after setting npc above, before WHILE re-executes' but the timing explanation could be clearer about why this ordering matters

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~270:
# Pop the loop from the stack (after setting npc above, before WHILE re-executes).
# Timing: We pop NOW so the stack is clean before WHILE condition re-evaluation.
# The WHILE will re-push if its condition is still true, or skip the loop body
# if false. This ensures clean stack state and proper error handling if the
# WHILE condition evaluation fails (loop already popped, won't corrupt stack).
self.limits.pop_while_loop()
self.runtime.pop_while_loop()

The comment is accurate but verbose. The key insight is that popping before re-evaluation prevents stack corruption on errors, which is clearly stated.

---

#### code_vs_comment

**Description:** Comment in _read_line_from_file discusses CP/M encoding (CP437/CP850) but implementation uses latin-1 without conversion option

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~650:
# Encoding:
# Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
# CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
# Unicode U+0000-U+00FF, allowing round-trip byte preservation.
# Note: CP/M systems often used code pages like CP437 or CP850 for characters
# 128-255, which do NOT match latin-1. Latin-1 preserves the BYTE VALUES but
# not necessarily the CHARACTER MEANING for non-ASCII CP/M text.
# Future enhancement: Add optional encoding conversion setting for CP437/CP850 display.

The comment mentions 'Future enhancement' for CP437/CP850 support, but this is not tracked anywhere else. This is documentation of a known limitation rather than an inconsistency.

---

#### code_vs_comment

**Description:** Comment in execute_renum states 'RENUM not yet implemented - TODO' in fallback error but the function actually delegates to interactive_mode.cmd_renum which IS implemented

**Affected files:**
- `src/interpreter.py`

**Details:**
At line ~1120:
raise RuntimeError("RENUM not yet implemented - TODO")

This error is only raised when interactive_mode is not available (non-interactive context). The comment at line ~1095 correctly states:
# Note: RENUM is implemented via delegation to interactive_mode.cmd_renum.
# This architecture allows the interactive UI to handle AST modifications directly.

The error message 'not yet implemented - TODO' is misleading because RENUM IS implemented in interactive mode. A better message would be 'RENUM not available in this context' to match other similar statements (LOAD, SAVE, CHAIN, etc.).

---

#### code_vs_comment

**Description:** LSET/RSET fallback behavior has redundant documentation

**Affected files:**
- `src/interpreter.py`

**Details:**
Both execute_lset() (lines ~2740-2745) and execute_rset() (lines ~2775-2780) have nearly identical comments about fallback behavior:

LSET: "Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field variables... This fallback is a deliberate extension that performs simple assignment without left-justification."

RSET: "Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field variables... This fallback is a deliberate extension that performs simple assignment without right-justification."

The RSET comment adds: "This is documented behavior, not a bug." while LSET says: "Note: This extension behavior allows LSET/RSET to work as simple assignment operators when not used with FIELD, which is intentional flexibility in this implementation, not a bug or incomplete feature."

These should be consolidated or one should reference the other to avoid maintenance issues.

---

#### code_vs_comment

**Description:** STEP command implementation status is unclear

**Affected files:**
- `src/interpreter.py`

**Details:**
The execute_step() docstring (lines ~2885-2900) states:
"CURRENT STATUS: This method outputs an informational message but does NOT actually perform stepping. It's a stub that acknowledges the command but doesn't execute the intended behavior."

However, it also says:
"Note: The tick_pc() method has working step infrastructure (modes 'step_statement' and 'step_line') that is used by UI debuggers."

This creates confusion about whether stepping is implemented or not. The comment suggests the infrastructure exists but isn't connected to this command, but doesn't clearly state whether this is a TODO or intentional design.

---

#### code_vs_comment

**Description:** LIST statement comment references ProgramManager sync requirements not visible in code

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines ~2805-2810 states:
"Implementation note: Outputs from line_text_map (original source text), not regenerated from AST. This preserves original formatting/spacing/case. The line_text_map is maintained by ProgramManager and should be kept in sync with the AST during program modifications (add_line, delete_line, RENUM, MERGE). If ProgramManager fails to maintain this sync, LIST output may show stale or incorrect line text."

This comment describes a dependency on ProgramManager behavior that cannot be verified from this code alone. It's a warning about potential bugs in another component, which may be useful but could also become outdated if ProgramManager's implementation changes.

---

#### Documentation inconsistency

**Description:** Module docstring states WebIOHandler has dependencies on nicegui and is not exported, but web_io.py is a complete implementation that could be imported

**Affected files:**
- `src/iohandler/__init__.py`
- `src/iohandler/web_io.py`

**Details:**
__init__.py says: "WebIOHandler has dependencies on nicegui. They are not exported here to keep this module focused on core I/O handlers"

However, web_io.py is a fully functional implementation with nicegui imports. The statement is accurate about not exporting it, but could clarify that the implementation exists and is usable via direct import.

---

#### Code vs Comment conflict

**Description:** get_char() backward compatibility comment incorrectly describes the original method behavior

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment states: "Note: Always calls input_char(blocking=False) for non-blocking behavior to match the expected behavior of the original get_char() method."

However, get_char() has no parameters in its definition, so there was no way to specify blocking behavior. The comment assumes get_char() was non-blocking, but this cannot be verified from the code. The alias simply calls input_char(blocking=False) as an implementation choice.

---

#### Documentation inconsistency

**Description:** web_io.py documents get_screen_size() as web-specific but doesn't mention it's not in base interface in the method docstring itself

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/web_io.py`

**Details:**
base.py docstring states: "Note: Implementations may provide additional methods beyond this interface for backend-specific functionality (e.g., web_io.get_screen_size()). Such methods are not part of the core interface and should only be used by backend-specific code."

web_io.py get_screen_size() docstring says: "Note: This is a web_io-specific method, not part of the IOHandler base interface."

This is consistent, but the base.py example specifically mentions web_io.get_screen_size() which creates tight coupling in documentation. If web_io changes, base.py documentation would need updating.

---

#### Documentation inconsistency

**Description:** Inconsistent documentation about which whitespace is stripped in input_line()

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/curses_io.py`

**Details:**
base.py states: "curses: getstr() strips trailing whitespace (spaces, tabs, newlines)"

curses_io.py input_line() docstring states: "Note: Current implementation does NOT preserve trailing spaces as documented in base class. curses getstr() strips trailing whitespace (spaces, tabs, newlines). Leading spaces are preserved."

Both mention the same limitation, but base.py is more general while curses_io.py is more specific. The information is consistent but could be consolidated.

---

#### Code vs Documentation inconsistency

**Description:** input_char() docstring says blocking parameter is 'not used' but code accepts it for interface compatibility

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Docstring states: "Args:
    blocking: Accepted for interface compatibility. The parameter is not used in web UI since character input is not supported."

The method signature is: def input_char(self, blocking=True)

The parameter has a default value of True, but the implementation always returns "" immediately regardless of the value. The docstring correctly notes it's not used, but the default value of True is misleading since it suggests blocking behavior is the default when in fact no blocking ever occurs.

---

#### Documentation inconsistency

**Description:** Module docstring references settings.get() but doesn't import or show the settings module

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
Docstring states: "Both should read the same settings.get('keywords.case_style') to ensure consistency"

However, the KeywordCaseManager class doesn't use or import any settings module. The policy is passed as a constructor parameter. The comment suggests both systems should read from settings, but doesn't show how KeywordCaseManager would do this.

---

#### code_vs_comment_conflict

**Description:** Comment says type suffix terminates identifier but doesn't mention the break statement applies only to type suffixes

**Affected files:**
- `src/lexer.py`

**Details:**
Comment at line ~273: "Type suffix - terminates identifier (e.g., A$ reads as A$, not A$B)"

The code has a break statement after consuming type suffix, but the comment could be clearer that this break is what enforces termination, and that periods (.) do NOT terminate (they continue the while loop).

---

#### documentation_inconsistency

**Description:** Docstring claims 'All documented MBASIC 5.21 tokens and keywords are supported' but doesn't specify what those are

**Affected files:**
- `src/lexer.py`

**Details:**
Module docstring states: "All documented MBASIC 5.21 tokens and keywords are supported."

However, there's no reference to where these are documented or what the complete list is. The KEYWORDS are imported from src.tokens but not enumerated in this file's documentation.

---

#### code_vs_comment_conflict

**Description:** Comment about identifier case preservation is redundant and potentially confusing

**Affected files:**
- `src/lexer.py`

**Details:**
At line ~340, comment says: "Preserve original case for display. For identifiers (user-defined variables), store the exact case as typed in the original_case field for later display. (Keywords handle case separately via original_case_keyword - see Token class in tokens.py)"

This comment appears after the code already set token.original_case = ident. The parenthetical about keywords is confusing here because this code path is specifically for identifiers (not keywords), and the keyword case was already handled earlier in the function.

---

#### code_vs_comment_conflict

**Description:** Comment about REM/REMARK being keywords conflicts with apostrophe comment being distinct

**Affected files:**
- `src/lexer.py`

**Details:**
At line ~420, comment says: "Apostrophe comment - distinct token type (unlike REM/REMARK which are keywords)"

This is accurate but potentially misleading. REM/REMARK ARE keywords (TokenType.REM, TokenType.REMARK), but they receive special handling at lines ~470-477 where their comment text is read. The distinction isn't just that apostrophe is a distinct token type - it's that apostrophe is an operator/delimiter (TokenType.APOSTROPHE) while REM/REMARK are keyword tokens that trigger comment reading.

---

#### code_vs_comment

**Description:** Docstring for parse_print_using is incomplete/truncated

**Affected files:**
- `src/parser.py`

**Details:**
The parse_print_using method docstring ends abruptly:
"# Parse list of expressions (separated by semicolons)
expressions: List[ExpressionNode] = []

while not self.at_end_of_line() and not self.match(TokenType.COLON) and not self.match(TokenType.ELSE):
    # Check for separator first (skip it)
    if self.match(TokenType.SEMICOLON):
        self.advance()
        # Check if more expressions follow"

The method implementation appears to be cut off in the provided source. This suggests either the file is truncated or there's missing code.

---

#### code_vs_comment

**Description:** Comment about comma being optional after file number in PRINT statement may not match MBASIC 5.21 spec

**Affected files:**
- `src/parser.py`

**Details:**
In parse_print() method:
"# Optionally consume comma after file number
# Note: MBASIC 5.21 typically requires comma (PRINT #1, 'text').
# Our parser makes the comma optional for compatibility with BASIC variants
# that allow PRINT #1; 'text' or PRINT #1 'text'."

The comment admits this deviates from MBASIC 5.21 spec (which "typically requires comma") for compatibility with other variants. This is a design decision but creates inconsistency with the stated goal of being a "Parser for MBASIC 5.21" as stated in the module docstring. The parser is more permissive than the documented target dialect.

---

#### code_vs_comment

**Description:** Comment describes LINE_INPUT tokenization behavior that may not match actual lexer implementation

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1180 states: "Note: The lexer tokenizes LINE keyword as LINE_INPUT token both when standalone (LINE INPUT statement) and when used as modifier (INPUT...LINE). The parser distinguishes these cases by context - LINE INPUT is a statement, INPUT...LINE uses LINE as a modifier within the INPUT statement."

This comment describes lexer behavior but appears in parser code. Without seeing the lexer implementation, cannot verify if this is accurate or if the lexer actually produces different tokens for these cases.

---

#### code_vs_comment

**Description:** Comment about MID$ tokenization may be misleading about token representation

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1850 states: "Note: The lexer tokenizes 'MID$' from source as TokenType.MID. The token TYPE is named 'MID' (enum constant), but the token represents the full 'MID$' keyword with the dollar sign as an integral part (not a separate type suffix token)."

This suggests the dollar sign is part of the token value, but the code only checks for TokenType.MID without verifying the dollar sign is present. If the lexer can produce TokenType.MID for both 'MID' and 'MID$', this could cause parsing issues.

---

#### documentation_inconsistency

**Description:** Comment about dimension expressions evaluation timing may not match all BASIC implementations

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_dim (line ~1770) states: "Dimension expressions: This implementation accepts any expression for array dimensions (e.g., DIM A(X*2, Y+1)), with dimensions evaluated at runtime. This matches MBASIC 5.21 behavior which evaluates dimension expressions at runtime (not compile-time). Note: Some compiled BASICs (e.g., QuickBASIC) may require constants only."

This is documentation about compatibility but doesn't clarify if the current implementation actually enforces runtime evaluation or if it's just accepted syntax. The note about QuickBASIC suggests potential compatibility issues that may not be handled.

---

#### code_vs_comment

**Description:** Comment about separator behavior in LPRINT may not accurately describe the logic

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~1110 explains: "Separator count vs expression count:
- If separators < expressions: no trailing separator, add newline
- If separators >= expressions: has trailing separator, no newline added
Examples: 'LPRINT A;B;C' has 2 separators for 3 items (no trailing sep, adds \n)
          'LPRINT A;B;C;' has 3 separators for 3 items (trailing sep, no \n)
          'LPRINT ;' has 1 separator for 0 items (trailing sep, no \n)"

However, the code logic at line ~1125:
  if len(separators) < len(expressions):
      separators.append('\n')

This doesn't match the third example. For 'LPRINT ;' with 0 expressions and 1 separator, len(separators) (1) is NOT < len(expressions) (0), so no newline would be added. But the comment says it has a trailing separator and no \n is added, which matches the code. The comment's phrasing is confusing.

---

#### code_vs_comment

**Description:** parse_width docstring mentions MBASIC 5.21 but doesn't specify if this is the target version for the entire parser

**Affected files:**
- `src/parser.py`

**Details:**
parse_width docstring:
"In MBASIC 5.21, common values are file numbers or omitted for console."

parse_call docstring:
"MBASIC 5.21 syntax:
    CALL address"
"Note: MBASIC 5.21 primarily uses the simple numeric address form."

These are the only two methods that explicitly mention MBASIC 5.21 version. Other methods don't specify version, creating ambiguity about whether the entire parser targets MBASIC 5.21 or if only these specific features are version-specific.

---

#### code_vs_comment

**Description:** parse_data docstring mentions line numbers in DATA but doesn't explain why LINE_NUMBER tokens would appear in DATA statements

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"Line numbers (e.g., DATA 100 200): These are tokenized as LINE_NUMBER tokens
but are converted to strings and included in unquoted string values."

This is confusing because line numbers typically appear at the start of lines (e.g., '100 DATA ...'). The comment suggests line numbers can appear as DATA values (e.g., 'DATA 100 200'), but doesn't explain the context where the lexer would produce LINE_NUMBER tokens within a DATA statement rather than NUMBER tokens. This may indicate either:
1. The comment is outdated and LINE_NUMBER tokens don't actually appear here
2. There's a special lexer behavior for DATA statements not documented
3. The comment is describing a theoretical case that doesn't occur in practice

---

#### code_vs_comment

**Description:** PC.__repr__ docstring says 'String representation for debugging' but implementation shows it's also used for user-facing display

**Affected files:**
- `src/pc.py`

**Details:**
The __repr__ method docstring:
"""String representation for debugging"""

But the implementation produces formatted output like:
"PC(10.2 STOPPED:ERROR Error#11)"

This appears to be user-facing output (based on the careful formatting), not just debug output. The comment should clarify if this is intended for both debugging and user display.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for statement index field name

**Affected files:**
- `src/position_serializer.py`

**Details:**
The position_serializer.py uses 'stmt_offset' in variable names:
"for stmt_offset, stmt in enumerate(line_node.statements):
    pc = PC.running_at(line_num, stmt_offset)"

But src/pc.py documentation consistently uses 'statement' as the field name and says stmt_offset is legacy:
"statement: Statement index on the line (0-based)"
"@property
def stmt_offset(self):
    '''Compatibility: old code used stmt_offset instead of statement'''"

The position_serializer should use 'statement_index' or similar to match the current naming convention, not the deprecated 'stmt_offset' name.

---

#### code_vs_comment

**Description:** serialize_expression docstring incomplete - doesn't mention all handled expression types

**Affected files:**
- `src/position_serializer.py`

**Details:**
The serialize_expression method handles these expression types:
- NumberNode
- StringNode
- VariableNode
- BinaryOpNode
- UnaryOpNode
- FunctionCallNode

But the docstring only says:
"""Serialize an expression node.

Args:
    expr: Expression node to serialize

Returns:
    Serialized expression text
"""

It should list the supported expression types for completeness, similar to how serialize_statement lists supported statement types.

---

#### Documentation inconsistency

**Description:** Module docstrings have asymmetric cross-references

**Affected files:**
- `src/resource_limits.py`
- `src/resource_locator.py`

**Details:**
resource_limits.py states: "Note: This is distinct from resource_locator.py which locates package data files."

resource_locator.py states: "Note: This is distinct from resource_limits.py which enforces runtime execution limits."

Both modules correctly distinguish themselves from each other, but the phrasing is slightly different. resource_limits.py says resource_locator "locates package data files" while resource_locator.py says resource_limits "enforces runtime execution limits". This is consistent in meaning but could be more parallel in structure.

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for string length limits

**Affected files:**
- `src/resource_limits.py`

**Details:**
The docstring for __init__ parameter max_string_length states:
"Maximum byte length for a string variable (UTF-8 encoded).
MBASIC 5.21 limit is 255 bytes (mandatory for spec compliance)."

The docstring for check_string_length() states:
"Note:
    String limits are measured in bytes (UTF-8 encoded), not character count.
    This matches MBASIC 5.21 behavior which limits string storage size."

The first says "byte length" and the second says "measured in bytes" - both correct but could use consistent phrasing. Also, the first says "mandatory for spec compliance" while the second says "matches MBASIC 5.21 behavior" - slightly different emphasis.

---

#### code_vs_comment

**Description:** Comment about line=-1 usage is inconsistent between two locations

**Affected files:**
- `src/runtime.py`

**Details:**
Line 48-56 in __init__ comment states:
"Note: line -1 in last_write indicates non-program execution sources:
       1. System/internal variables (ERR%, ERL%) via set_variable_raw() with FakeToken(line=-1)
       2. Debugger/interactive prompt via set_variable() with debugger_set=True (always uses line=-1)
       Both use line=-1, making them indistinguishable from each other in last_write alone.
       However, line=-1 distinguishes these special sources from normal program execution (line >= 0)."

But line 408-414 in set_variable_raw() comment states:
"The line=-1 marker in last_write indicates system/internal variables.
However, debugger sets also use line=-1 (via debugger_set=True),
making them indistinguishable from system variables in last_write alone.
Both are distinguished from normal program execution (line >= 0)."

These say the same thing but with slightly different wording. The second comment doesn't mention the two numbered sources (system/internal vs debugger) as clearly.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for 'debugger_set' parameter purpose

**Affected files:**
- `src/runtime.py`

**Details:**
Line 289 docstring: "debugger_set: True if this set is from debugger/interactive prompt, not program execution"

But line 305 comment: "# Check for case conflicts and get canonical case (skip for debugger sets)"
And line 306-309 comment: "# Note: If not debugger_set, token is guaranteed to be non-None by the ValueError check above.
# Debugger sets skip case conflict checking because they don't have source location context
# and are used for internal/system variables that don't need case consistency enforcement."

The docstring says debugger_set is for "debugger/interactive prompt", but the comment says it's also "used for internal/system variables". This is inconsistent - internal/system variables use set_variable_raw() which calls set_variable() with a FakeToken(line=-1), not with debugger_set=True.

---

#### code_vs_comment

**Description:** Comment in set_variable() describes two paths but implementation has three branches

**Affected files:**
- `src/runtime.py`

**Details:**
Line 343-346 comment:
"# Non-debugger path: normal program execution (token.line >= 0) OR internal/system set (token.line = -1)
# Both use this branch; line value from token distinguishes them"

However, the actual code has three branches:
1. Line 335-340: if debugger_set (line=-1, position=None)
2. Line 341-347: elif token is not None (uses token.line and token.position)
3. Implicit else: no tracking update

The comment describes the elif branch as handling both normal execution and internal/system sets, which is correct. But it doesn't mention that there's also a third implicit case where neither debugger_set is True nor token is provided (though this should be prevented by the ValueError check at line 285).

---

#### Code vs Comment conflicts

**Description:** Comment claims default type suffix fallback should not occur in practice, but code implements it as defensive programming

**Affected files:**
- `src/runtime.py`

**Details:**
In get_variables() method around line 60-65:

Comment says: "Note: In normal operation, all names in _variables have resolved type suffixes from _resolve_variable_name() which applies DEF type rules. This fallback is defensive programming for robustness - it should not occur in practice, but protects against potential edge cases in legacy code or future changes."

Code implements: "return full_name, '!'" as fallback when no type suffix present.

The comment suggests this is purely defensive and shouldn't happen, but doesn't explain if there are actual edge cases where this occurs or if it's truly unreachable code.

---

#### Documentation inconsistencies

**Description:** Redundant field documentation acknowledges redundancy but doesn't explain why it exists

**Affected files:**
- `src/runtime.py`

**Details:**
In get_execution_stack() docstring around line 180:

"Note: 'from_line' is redundant with 'return_line' - both contain the same value (the line number to return to after RETURN). The 'from_line' field exists for backward compatibility with code that expects it. Use 'return_line' for new code as it more clearly indicates the field's purpose."

This documents the redundancy but the actual implementation at line 200 shows:
"'from_line': entry.get('return_line', 0),  # Line to return to"

The comment "# Line to return to" is redundant with the docstring explanation. Minor documentation verbosity issue.

---

#### Documentation inconsistencies

**Description:** Inconsistent terminology for statement offset indexing explanation

**Affected files:**
- `src/runtime.py`

**Details:**
Multiple locations describe statement offset indexing differently:

1. Line 145: "Note: stmt_offset uses 0-based indexing (offset 0 = 1st statement, offset 1 = 2nd statement, etc.)"

2. Line 175: "This shows: FOR I at line 100, statement offset 0 (1st statement)"

3. Line 280: "Note: Uses 0-based indexing (offset 0 = 1st statement, offset 1 = 2nd statement, offset 2 = 3rd statement, etc.)"

While all are technically correct, the third example adds "offset 2 = 3rd statement" which is more explicit. The inconsistency in level of detail across similar explanations could be confusing.

---

#### code_vs_comment

**Description:** SettingsManager.load() docstring describes flexible format handling but implementation shows backend determines format entirely

**Affected files:**
- `src/settings.py`

**Details:**
Docstring says: "The backend determines the format (flat vs nested) based on what was saved. Internal representation is flexible: _get_from_dict() handles both flat keys like 'editor.auto_number' and nested dicts like {'editor': {'auto_number': True}}."

This is accurate but could be clearer that SettingsManager doesn't control format - it's entirely backend-dependent. The comment makes it sound like SettingsManager has format logic when it's just consuming whatever the backend returns.

---

#### documentation_inconsistency

**Description:** RedisSettingsBackend docstring mentions 'nicegui or redis-py' but create_settings_backend only uses redis-py

**Affected files:**
- `src/settings_backend.py`

**Details:**
RedisSettingsBackend.__init__ docstring: "redis_client: Redis client instance (from nicegui or redis-py)"

But create_settings_backend() implementation only shows:
import redis
redis_client = redis.from_url(redis_url, decode_responses=True)

No nicegui client usage is shown. Either the docstring should remove 'nicegui' reference or the implementation should show how nicegui clients are supported.

---

#### documentation_inconsistency

**Description:** Comments about excluded settings mention rationale but don't explain where those decisions are documented

**Affected files:**
- `src/settings_definitions.py`

**Details:**
Two comments explain why settings are NOT included:
"# Note: editor.tab_size setting not included - BASIC uses line numbers for program structure, not indentation, so tab size is not a meaningful setting for BASIC source code"

"# Note: Line numbers are always shown - they're fundamental to BASIC! editor.show_line_numbers setting not included - makes no sense for BASIC"

These are design decisions but there's no reference to where these decisions were made or documented. If someone wants to understand why these settings don't exist, they have to find these inline comments.

---

#### documentation_inconsistency

**Description:** KEYWORDS dict comment mentions special handling for 'LINE INPUT' but doesn't explain where that handling occurs

**Affected files:**
- `src/tokens.py`

**Details:**
Comment in KEYWORDS dict: "'line': TokenType.LINE_INPUT,  # Will need special handling for 'LINE INPUT'"

This suggests special handling is needed but doesn't reference where this handling is implemented (presumably in lexer). A reader would need to search the codebase to find the implementation.

---

#### code_vs_documentation

**Description:** Module docstring claims to provide 'abstract interfaces and implementations for different UI types' but only shows imports

**Affected files:**
- `src/ui/__init__.py`

**Details:**
Docstring: "This module provides abstract interfaces and implementations for different UI types (CLI, GUI, web, mobile, etc.)."

But the file only contains imports and conditional import logic. The actual interfaces and implementations are in other files (base.py, cli.py, etc.). The docstring should clarify this is a convenience import module, not where the implementations live.

---

#### code_vs_comment

**Description:** RedisSettingsBackend.load_project and save_project docstrings say 'returns empty dict' and 'no-op' but don't explain why project settings aren't supported in Redis mode

**Affected files:**
- `src/settings_backend.py`

**Details:**
load_project docstring: "Load project settings (returns empty dict in Redis mode). In Redis mode, all settings are session-scoped, not project-scoped. This method returns an empty dict rather than None for consistency."

save_project docstring: "Save project settings (no-op in Redis mode). In Redis mode, all settings are session-scoped, not project-scoped. This method does nothing (no write operation) for consistency."

These explain WHAT happens but not WHY project settings aren't supported in Redis mode. Is it a technical limitation? Design decision? Future enhancement? The rationale is missing.

---

#### Documentation inconsistency

**Description:** Inconsistent terminology for step commands between CLI and curses UI

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/curses_keybindings.json`

**Details:**
cli_debug.py cmd_step() docstring: "This implements statement-level stepping similar to the curses UI 'Step Statement' command (Ctrl+T). The curses UI also has a separate 'Step Line' command (Ctrl+K) which is not available in the CLI."

curses_keybindings.json:
- Ctrl+K: "Step Line (execute all statements on current line)"
- Ctrl+T: "Step statement (execute one statement)"

The CLI documentation correctly references the curses UI commands, but there's potential confusion because CLI's STEP command attempts statement-level stepping (like Ctrl+T) but may actually do line-level stepping depending on interpreter implementation, yet doesn't offer an explicit line-level step command like curses's Ctrl+K.

---

#### Documentation inconsistency

**Description:** get_additional_keybindings() comment about Ctrl+A override is misleading

**Affected files:**
- `src/ui/cli.py`

**Details:**
Comment states: "Note: Ctrl+A is overridden by MBASIC to trigger edit mode (not readline's default move-to-start-of-line)"

However, cli_keybindings.json shows:
"edit": {
  "keys": ["Ctrl+A"],
  "primary": "Ctrl+A",
  "description": "Edit line (last line or Ctrl+A followed by line number)"
}

The comment suggests Ctrl+A always triggers edit mode, but the description indicates it can be used in two ways: editing the last line OR followed by a line number. This is not clearly explained as an 'override' of readline behavior.

---

#### Code vs Comment conflict

**Description:** Comment about stripping 'force_' prefix uses hasattr check for removeprefix method

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Code in _create_setting_widget():
# Strip 'force_' prefix from beginning for cleaner display
display_label = choice.removeprefix('force_') if hasattr(str, 'removeprefix') else (choice[6:] if choice.startswith('force_') else choice)

The comment says it strips the prefix for cleaner display, but the code has a fallback for Python versions without removeprefix (added in Python 3.9). The comment doesn't mention this version compatibility consideration. Also, the fallback uses hardcoded index [6:] which assumes 'force_' is exactly 6 characters - this is correct but fragile.

---

#### Documentation inconsistency

**Description:** UIBackend docstring lists future backend types but marks them as 'not yet implemented' inconsistently

**Affected files:**
- `src/ui/base.py`

**Details:**
Docstring states:
"Different UIs can implement this interface:
- CLIBackend: Terminal-based REPL (interactive command mode)
- CursesBackend: Full-screen terminal UI with visual editor
- TkBackend: Desktop GUI using Tkinter

Future/potential backend types (not yet implemented):
- WebBackend: Browser-based interface"

TkBackend is listed as a current implementation alongside CLIBackend and CursesBackend, but there's no TkBackend implementation in the provided files. It should either be moved to the 'Future/potential' section or the files are incomplete.

---

#### Code vs Comment conflict

**Description:** Comment about comparing actual values vs display labels is verbose and could be clearer

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
In _on_reset() method:
# Note: Compares actual value (stored in _actual_value) not display label
# since display labels have 'force_' prefix stripped (see _create_setting_widget)
for rb in widget:
    rb.set_state(rb._actual_value == defn.default)

The comment explains the comparison logic, but the code structure makes this obvious since it's using _actual_value attribute. The comment is helpful but could be more concise. This is a minor style issue rather than a true conflict.

---

#### Documentation inconsistency

**Description:** Footer text construction comment doesn't match implementation detail

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Comment states: "# Create footer with keyboard shortcuts (instead of button widgets)
# Note: All shortcuts use constants from keybindings module to ensure
# footer display matches actual key handling in keypress() method"

The comment emphasizes using constants from keybindings module, but the actual footer construction uses key_to_display() function calls rather than directly using the constants. While technically the constants are used (passed to key_to_display), the comment could be clearer about this indirection.

---

#### code_vs_comment

**Description:** Comment says 'default target_column of 7' but this assumes fixed-width line numbers, contradicting variable-width design

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In keypress() method docstring (line ~220): "Note: Methods like _sort_and_position_line use a default target_column of 7,
which assumes typical line numbers (status=1 char + number=5 digits + space=1 char).
This is an approximation since line numbers have variable width."

This comment contradicts the module's core design principle stated in class docstring: "Line numbers use as many digits as needed (10, 100, 1000, 10000, etc.) rather
than fixed-width formatting." The assumption of 5-digit line numbers conflicts with variable-width design.

---

#### code_vs_comment

**Description:** Comment about BASIC statements starting with digits contradicts parsing assumption

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_numbers() method (line ~1130): "# In this context, we assume lines starting with digits are numbered program lines (e.g., '10 PRINT').
# Note: While BASIC statements can start with digits (numeric expressions), when pasting
# program code, lines starting with digits are conventionally numbered program lines."

This comment acknowledges that BASIC statements CAN start with digits (like numeric expressions), but the code unconditionally treats ANY line starting with a digit as a numbered program line. This could incorrectly reformat valid BASIC code that starts with a numeric expression.

---

#### code_vs_comment

**Description:** Comment about 'use None instead of not' is misleading about the actual issue

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _display_syntax_errors() method (line ~1075): "# Check if output walker is available (use 'is None' instead of 'not' to avoid false positive on empty walker)
if self._output_walker is None:"

The comment suggests using 'is None' to avoid false positives on empty walkers, but an empty walker would still be truthy (it's an object, not None). The real reason to use 'is None' is to check for uninitialized state, not to handle empty walkers. The comment conflates two different concepts.

---

#### code_vs_comment

**Description:** Comment about editor_lines vs editor.lines relationship may be outdated

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~230 states:
"# Note: self.editor_lines stores execution state (lines loaded from file for RUN)
# self.editor.lines (in ProgramEditorWidget) stores the actual editing state
# These serve different purposes and are synchronized as needed"

However, looking at _save_editor_to_program() (line ~330), it iterates over self.editor.lines and reconstructs full lines with line numbers. The _refresh_editor() method (line ~390) syncs FROM program manager TO editor.lines. This suggests editor.lines is the primary editing state, and editor_lines may be redundant or used differently than described.

---

#### code_vs_comment

**Description:** Comment about ImmediateExecutor lifecycle contradicts actual behavior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~270 states:
"# ImmediateExecutor Lifecycle:
# Created here with an OutputCapturingIOHandler, then recreated in start() with
# a fresh OutputCapturingIOHandler."

But in start() method (line ~290), the code creates a NEW ImmediateExecutor:
"immediate_io = OutputCapturingIOHandler()
self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)"

This means the executor created in __init__ is completely replaced, not just given a fresh IO handler. The comment suggests the executor is reused with a new IO handler, but the code creates an entirely new executor instance.

---

#### code_vs_comment

**Description:** Comment about Interpreter lifecycle claims it's never recreated, but this may conflict with cleanup behavior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~260 states:
"# Interpreter Lifecycle:
# Created ONCE here in __init__ and reused throughout the session.
# The interpreter object itself is NEVER recreated - the same instance is used
# for the lifetime of the UI session."

However, in _cleanup() method (line ~320), there's code:
"if hasattr(self, 'interpreter') and self.interpreter:
    try:
        # Try to stop cleanly
        pass
    except:
        pass"

The empty try block suggests incomplete cleanup logic. If the interpreter is truly never recreated and reused across sessions, there should be proper cleanup/reset logic, but the pass statement indicates this wasn't implemented.

---

#### code_vs_comment

**Description:** Comment about toolbar removal contradicts its presence in code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~540 states:
"# Toolbar removed from UI layout - use Ctrl+U interactive menu bar instead for keyboard navigation"

But there's no toolbar widget created or referenced in the surrounding code. This comment appears to be a historical note about a removed feature, but it's unclear if this is documenting current state or a past change. The comment placement suggests it's explaining why something is missing, but without context of what was removed.

---

#### code_vs_comment

**Description:** Comment about immediate mode status updates during execution may be misleading

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple comments throughout the code state things like:
"# (output shows in output window, immediate mode updates via tick loop)" (line ~810)
"# (Immediate mode status remains disabled during execution - output shows in output window)" (line ~900)

These comments suggest immediate mode status is updated during execution via tick loop, but the actual _update_immediate_status() calls happen AFTER execution completes (after state.error_info checks, after program completion). The comments imply continuous updates during execution, but the code shows updates only at completion/error/pause points.

---

#### code_vs_comment

**Description:** Comment about PC setting timing may be confusing - states it must happen AFTER start() because start() resets PC, but this is expected behavior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1110 states:
"If start_line is specified (e.g., RUN 100), set PC to that line
This must happen AFTER interpreter.start() because start() calls setup()
which resets PC to the first line in the program. By setting PC here,
we override that default and begin execution at the requested line."

This accurately describes the implementation and the reason for the ordering. Not a true inconsistency, just verbose.

---

#### code_vs_comment

**Description:** Comment about immediate mode status during execution may be incomplete

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1143 states:
"Immediate mode status remains disabled during execution - program output shows in output window"

This comment doesn't explain what happens to immediate mode status after execution completes or on error, though the code does handle these cases by calling _update_immediate_status().

---

#### code_vs_comment

**Description:** Comment in _get_input_for_interpreter describes behavior as 'similar to STOP' but doesn't clarify if STOP also preserves PC

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1005 states:
"# If user cancelled (ESC), stop program execution
# Note: This stops the UI tick. The interpreter's PC (program counter) is already at
# the position where execution should resume if user presses CONT.
# The behavior is similar to STOP: user can examine variables and continue with CONT."

This implies STOP also preserves PC for CONT, but there's no explicit documentation of this behavior elsewhere in the visible code. The cmd_cont implementation checks if PC is_running() and says "?Can't continue" if true, but doesn't document what state PC should be in for CONT to work.

---

#### code_vs_comment

**Description:** Comment in _on_input_complete says 'PC already contains the position for CONT to resume from' but doesn't explain how this position was set

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~1007 states:
"# Stop execution - PC already contains the position for CONT to resume from"

This assumes PC was set to the correct position before the input dialog was shown, but there's no visible code in this function or its caller that explicitly sets PC to the resume position. It's unclear if this happens automatically in the interpreter or if there's missing context.

---

#### documentation_inconsistency

**Description:** Docstring example format inconsistency with actual macro format

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
Module docstring shows examples:
"{{kbd:help}} → looks up 'help' action in current UI's keybindings
{{kbd:save:curses}} → looks up 'save' action in Curses UI specifically"

But _expand_kbd docstring at line ~88 describes different format:
"Formats:
- 'action' - searches current UI (e.g., 'help', 'save', 'run')
- 'action:ui' - searches specific UI (e.g., 'save:curses', 'run:tk')"

The module docstring shows {{kbd:save:curses}} but the method docstring describes the format as 'save:curses' (without the {{kbd: wrapper). While technically both are correct (one shows the full macro, one shows the argument), this could be clearer.

---

#### code_vs_documentation_inconsistency

**Description:** Version macro returns hardcoded value with unclear relationship to src/version.py

**Affected files:**
- `src/ui/help_macros.py`

**Details:**
In _expand_macro() at line ~72:
return "5.21"  # MBASIC 5.21 language version

Comment states:
"# Hardcoded MBASIC version for documentation
# Note: Project has internal implementation version (src/version.py) separate from this"

This creates potential confusion: there are two version numbers (5.21 for language, and whatever is in src/version.py for implementation). Documentation using {{version}} will show 5.21, but this may not match the actual running version. This isn't necessarily wrong, but could lead to user confusion if not clearly documented.

---

#### code_vs_comment_conflict

**Description:** Comment describes search result format but doesn't match actual tuple structure

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Method _search_indexes() docstring at line ~119 states:
"Returns list of (tier, path, title, description) tuples."

But the actual return statement at lines ~157-162 shows:
results.append((
    tier_label,
    file_info.get('path', ''),
    file_info.get('title', ''),
    file_info.get('description', '')
))

The variable name is 'tier_label' not 'tier', which is technically correct but the docstring could be more precise about returning the formatted label (e.g., '📕 Language') rather than the raw tier name.

---

#### Documentation inconsistency

**Description:** Comment lists keys not included in KEYBINDINGS_BY_CATEGORY but doesn't mention QUIT_ALT_KEY which IS included

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Lines 197-204 comment:
# Note: This dictionary contains keybindings shown in the help system.
# Some defined constants are not included here:
# - CLEAR_BREAKPOINTS_KEY (Shift+Ctrl+B) - Available in menu under Edit > Clear All Breakpoints
# - STOP_KEY (Ctrl+X) - Shown in debugger context in the Debugger category
# - MAXIMIZE_OUTPUT_KEY (Shift+Ctrl+M) - Menu-only feature, not documented as keyboard shortcut
# - STACK_KEY (empty string) - No keyboard shortcut assigned, menu-only
# - Dialog-specific keys (DIALOG_YES_KEY, DIALOG_NO_KEY, SETTINGS_APPLY_KEY, SETTINGS_RESET_KEY) - Shown in dialog prompts
# - Context-specific keys (VARS_SORT_MODE_KEY, VARS_SORT_DIR_KEY, etc.) - Shown in Variables Window category

But STOP_KEY is actually included in the 'Debugger (when program running)' category (line 229), and QUIT_ALT_KEY is included in 'Global Commands' (line 207) but not mentioned in the comment.

---

#### Documentation inconsistency

**Description:** KEYBINDINGS_BY_CATEGORY shows different descriptions for the same key in different contexts

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
In 'Global Commands' (line 211):
(key_to_display(VARIABLES_KEY), 'Toggle variables window'),

In 'Debugger (when program running)' (line 230):
(key_to_display(VARIABLES_KEY), 'Show/hide variables window'),

Both describe the same action but use different wording ('Toggle' vs 'Show/hide'). While semantically similar, consistency would be better.

---

#### Code vs Documentation inconsistency

**Description:** Keymap widget shows 'ESC/Q close' but only ESC and lowercase 'q' are handled in keypress method

**Affected files:**
- `src/ui/keymap_widget.py`

**Details:**
Line 35 shows:
instructions = urwid.AttrMap(
    urwid.Text("↑/↓ scroll  ESC/Q close", align='center'),
    'help_text'
)

But line 72 handles:
if key in ('esc', 'q', 'Q'):

The code does handle both 'q' and 'Q', so this is actually consistent. However, the display shows 'Q' (uppercase) which might mislead users to think only uppercase Q works.

---

#### Code vs Comment conflict

**Description:** Module docstring says 'Not thread-safe (no locking mechanism)' but doesn't explain why this matters or when it would be an issue

**Affected files:**
- `src/ui/recent_files.py`

**Details:**
Lines 1-20 docstring includes:
- Note: Not thread-safe (no locking mechanism)

This warning is present but the module doesn't indicate if MBASIC uses multiple threads or if this is a theoretical concern. If MBASIC is single-threaded, this note may be unnecessary and confusing.

---

#### Documentation inconsistency

**Description:** STATUS_BAR_SHORTCUTS includes STEP_LINE_KEY but EDITOR_STATUS does not, suggesting inconsistent context awareness

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
Line 242:
STATUS_BAR_SHORTCUTS = f"MBASIC - {key_to_display(HELP_KEY)} help  {key_to_display(MENU_KEY)} menu  {key_to_display(VARIABLES_KEY)} vars  {key_to_display(STEP_LINE_KEY)} step line  {key_to_display(TAB_KEY)} cycle  ↑↓ scroll"

Line 243:
EDITOR_STATUS = f"Editor - {key_to_display(HELP_KEY)} help  {key_to_display(MENU_KEY)} menu  {key_to_display(TAB_KEY)} cycle"

STEP_LINE_KEY is a debugger command, so showing it in STATUS_BAR_SHORTCUTS (which appears to be general) but not in EDITOR_STATUS may be inconsistent. It's unclear when each status bar is used.

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

#### Code vs Comment conflict

**Description:** Comment about modal behavior may be misleading about blocking

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
In __init__() method (line 44):
# Make modal (prevents interaction with parent, but doesn't block code execution - no wait_window())

The comment clarifies that grab_set() makes the dialog modal but doesn't block code execution because wait_window() is not called. This is accurate, but the phrasing 'prevents interaction with parent' might be misunderstood as blocking, when it only prevents UI interaction while allowing code to continue. The comment is technically correct but could be clearer about the distinction between UI modality and code blocking.

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

#### code_vs_comment

**Description:** Comment states immediate_history and immediate_status are 'always None' but provides detailed explanation suggesting they might have been used previously

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines 147-151 states:
    # Immediate mode widgets and executor
    # Note: immediate_history and immediate_status are always None in Tk UI
    # (Tk uses immediate_entry Entry widget directly instead of separate history/status widgets)
    # immediate_entry is the actual Entry widget created in start()

Then at lines 267-270:
    # Set immediate_history and immediate_status to None
    # These attributes are not currently used but are set to None for defensive programming
    # in case future code tries to access them (will get None instead of AttributeError)

The first comment says they are 'always None' while the second says 'not currently used', suggesting uncertainty about their purpose. This indicates possible refactoring residue.

---

#### code_vs_comment

**Description:** Comment about Ctrl+I binding location contradicts actual binding location

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line 598 in _create_menu() states:
    # Note: Ctrl+I is bound directly to editor text widget in start() (not root window)
    # to prevent tab key interference - see editor_text.text.bind('<Control-i>', ...)

But the actual binding is at line 221 in start():
    self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)

The comment is correct about the location (in start()) but the explanation 'to prevent tab key interference' is misleading - the Tab key is separately bound at line 214 with its own handler. The Ctrl+I binding is for smart insert line functionality, not tab interference prevention.

---

#### documentation_inconsistency

**Description:** Toolbar comment mentions removed features but doesn't explain why they were removed or where to find them

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines 488-493 states:
    # Note: Toolbar has been simplified to show only essential execution controls.
    # Additional features are accessible via menus:
    # - List Program → Run > List Program
    # - New Program (clear) → File > New
    # - Clear Output → Run > Clear Output

This suggests a recent simplification but doesn't explain the rationale. The comment would be more useful if it explained why these buttons were removed (e.g., 'to reduce clutter' or 'based on user feedback').

---

#### code_vs_comment

**Description:** Comment about INPUT row visibility uses 'pack_forget()' but doesn't mention 'pack()' for showing

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at lines 237-238 states:
    # INPUT row (hidden by default, shown when INPUT statement needs input)
    # Visibility controlled via pack() when showing, pack_forget() when hiding

This is accurate and complete, but the next comment at line 240 says:
    # Don't pack yet - will be packed when needed

The second comment is redundant given the first comment already explained the visibility mechanism.

---

#### code_vs_comment

**Description:** Comment about validation timing is overly detailed and may become outdated

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1230:
Comment says: "Note: This method is called:
- With 100ms delay after cursor movement/clicks (to avoid excessive validation during rapid editing)
- Immediately when focus leaves editor (to ensure validation before switching windows)"

This implementation detail comment could become outdated if the calling pattern changes. The timing values (100ms) are hardcoded in multiple places and could drift.

---

#### code_vs_comment

**Description:** Comment about Tk Text widget design is explanatory but could be in docstring instead

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines method around line 1363:
Comment says: "Tk Text widgets always end with a newline character (Tk design - text content ends at last newline, so there's always an empty final line)."

This is useful information but appears mid-implementation. It would be better in the method's docstring where it explains the 'except final line' behavior mentioned in the docstring.

---

#### code_vs_comment

**Description:** Comment about clearing yellow highlight references behavior not visible in this code section

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_mouse_click method around line 1310:
Comment says: "Clear yellow statement highlight when clicking and paused at breakpoint (allows text selection to be visible). The highlight is restored when execution resumes or when stepping to the next statement."

The restoration behavior mentioned is not visible in this code section, making it hard to verify the comment's accuracy. The comment references _clear_statement_highlight() but doesn't show where/how restoration happens.

---

#### documentation_inconsistency

**Description:** Multiple comments reference 'immediate mode' and '_ImmediateModeToken' but no documentation explains what this is

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _edit_simple_variable (line 570) and _edit_array_element (line 850):
Comments say: "Use _ImmediateModeToken to mark this as a debugger/immediate mode edit"

The _ImmediateModeToken class is used but never defined or imported in this file section. There's no documentation explaining what 'immediate mode' means in this context or why it needs special marking.

---

#### code_vs_comment

**Description:** Comment about parity bit clearing contradicts actual character validation flow

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_key_press() method around line 1340:
Comment says: "# Clear parity bit\nfrom src.input_sanitizer import clear_parity\nchar = clear_parity(event.char)"

But the code flow shows:
1. First clears parity bit
2. Then validates with is_valid_input_char(char)
3. Then checks if parity was set and inserts cleared char

The comment implies parity clearing is the primary purpose, but the validation step is actually more important. The comment doesn't mention that invalid characters are blocked entirely, regardless of parity.

---

#### code_vs_comment

**Description:** Comment about inline paste logic doesn't match actual condition check

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_paste() method around line 1200:
Comment says: "# If current line has content (not blank), do simple inline paste\n# (cursor can be at start, middle, or end - we just paste at cursor position)"

But the condition only checks if line is not blank:
"if current_line_text:"

The comment implies cursor position matters for the decision, but the code only checks if the line has any content. The cursor position is irrelevant to the branching logic.

---

#### code_vs_comment

**Description:** Comment about has_work() usage location may be inaccurate

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment in _execute_immediate() states:
"Use has_work() to check if the interpreter is ready to execute (e.g., after RUN command). This is the only location in tk_ui.py that calls has_work()."

The claim 'This is the only location in tk_ui.py that calls has_work()' cannot be verified from this code snippet alone. If other parts of tk_ui.py also call has_work(), this comment would be misleading.

---

#### code_vs_comment

**Description:** Comment about PC/NPC relationship in CONT command may be incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In cmd_cont() method:
"The interpreter moves NPC to PC when STOP is executed (see execute_stop() in interpreter.py). CONT resumes tick-based execution, which continues from the PC position."

And later:
"The interpreter maintains the execution position in PC (moved by STOP). When CONT is executed, tick() will continue from runtime.pc, which was set by execute_stop() to point to the next statement after STOP. No additional position restoration is needed here."

The comment references execute_stop() in interpreter.py but we cannot verify this cross-reference is accurate without seeing that file. If execute_stop() behavior changes, this comment could become outdated.

---

#### code_vs_comment

**Description:** The _on_status_click() docstring says it 'Displays informational messages about line status' and 'does NOT toggle breakpoints', but the implementation shows both error messages and breakpoint confirmation messages, which is consistent. However, the docstring mentions 'confirmation message for ●' which might be misleading - it's more of an 'information message' than a 'confirmation'.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Docstring: 'Handle click on status column (show error details for ?, confirmation message for ●).'

The message shown for breakpoints is:
messagebox.showinfo(
    f"Breakpoint on Line {line_num}",
    f"Line {line_num} has a breakpoint set.\n\nUse the debugger menu or commands to manage breakpoints."
)

This is an informational message, not a confirmation. The term 'confirmation message' typically implies confirming an action that was just taken, but here it's just displaying status.

---

#### documentation_inconsistency

**Description:** The _redraw() docstring says 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas)' and references _parse_line_number() for 'regex-based extraction logic that validates line number format (requires whitespace or end-of-string after the number)'. However, the class docstring also mentions this same information, creating redundancy.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring: 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas). Line numbers are parsed from the text using _parse_line_number() to map status indicators to the correct lines.'

_redraw() docstring: 'Note: BASIC line numbers are part of the text content (not drawn separately in the canvas). See _parse_line_number() for the regex-based extraction logic that validates line number format (requires whitespace or end-of-string after the number).'

---

#### code_vs_comment

**Description:** Comment in serialize_line() about fallback behavior is overly detailed and potentially confusing

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Lines ~680-687: The comment explains:
'# Note: If source_text doesn\'t match pattern (or is unavailable), falls back to relative_indent=1.\n# When does this occur?\n# 1. Programmatically inserted lines (no source_text attribute)\n# 2. Lines where source_text doesn\'t start with line_number + spaces (edge case)\n# Result: These lines get single-space indentation instead of preserving original spacing.\n# This is expected behavior - programmatically inserted lines use standard formatting.'

This is accurate but the level of detail about edge cases and expected behavior seems excessive for inline comments. The code logic is straightforward (default to 1 space if no match), and the comment could be simplified.

---

#### code_vs_comment

**Description:** Comment in serialize_variable() about explicit_type_suffix attribute handling is defensive but may indicate incomplete implementation

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Lines ~838-841: Comment says:
'# Only add type suffix if it was explicit in the original source\n# Don\'t add suffixes that were inferred from DEF statements\n# Note: explicit_type_suffix is not always set (depends on parser implementation),\n# so getattr defaults to False if missing, preventing incorrect suffix output'

The comment acknowledges that explicit_type_suffix 'is not always set (depends on parser implementation)' which suggests inconsistent behavior across the codebase. The defensive getattr with False default may be masking incomplete parser implementation rather than being a proper design.

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No UI-framework dependencies' but doesn't mention the glob and os imports which are filesystem dependencies

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Module docstring at top says:
'This module contains UI-agnostic helper functions that can be used by\nany UI (CLI, Tk, Web, Curses). No UI-framework dependencies (Tk, curses, web)\nare allowed. Standard library modules (os, glob, re) and core interpreter\nmodules (runtime, parser, AST nodes) are permitted.'

The docstring does mention 'Standard library modules (os, glob, re)' are permitted, so this is actually consistent. However, the phrasing 'No UI-framework dependencies' followed by listing allowed dependencies could be clearer - it reads as if no dependencies are allowed, then contradicts itself.

---

#### code_vs_documentation

**Description:** Function cycle_sort_mode() comment says 'This matches the Tk UI implementation' but there's no verification this is actually true

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Line ~27: Comment says 'This matches the Tk UI implementation.'

Without seeing the Tk UI code, we cannot verify this claim. If the Tk UI changes its cycle order, this comment would become outdated. The comment creates a dependency claim that may not be maintained.

---

#### code_vs_comment

**Description:** Function get_sort_key_function() has inconsistent comment style for default case

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
Lines ~70-72: The default case comment says:
'# Default to name sorting (unknown modes fall back to this)'

This is the only case with a parenthetical explanation. Other cases (name, accessed, written, read) have simple comments or none. The inconsistent style suggests this was added later or by a different author.

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

**Description:** Multiple references to MBASIC version '5.21' as language version, but inconsistent labeling

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~598: # Note: '5.21' is the MBASIC language version (intentionally hardcoded)
Line ~599: ui.label('MBASIC 5.21 Web IDE').classes('text-lg')
Line ~1062: ui.page_title('MBASIC 5.21 - Web IDE')
Line ~1117: self.output_text = f'MBASIC 5.21 Web IDE - {VERSION}\n'

The comment clarifies 5.21 is the language version, but the UI labels mix 'MBASIC 5.21 Web IDE' with implementation VERSION. This could be clearer about which version is which.

---

#### code_vs_comment

**Description:** Comment about Step commands preserving output appears in RUN section but applies to step commands elsewhere

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1849 comment in _menu_run(): 'Note: Step commands also preserve output (no clearing during debugging either)'

This comment is in the _menu_run() method but describes behavior of _menu_step_line() and _menu_step_stmt() methods which appear later in the file. The comment is accurate but misplaced.

---

#### code_vs_comment

**Description:** Comment about PC manipulation is misleading - claims 'no need to manipulate flags' but PC is a program counter object, not a flags register

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~2030 in _menu_step_line(): 'PC will be updated by tick - no need to manipulate flags'
Line ~2048 in _menu_step_stmt(): 'PC will be updated by tick - no need to manipulate flags'

The term 'flags' typically refers to CPU status flags (zero, carry, etc.) in microprocessor terminology. However, PC is a Program Counter object that tracks line_num and stmt_offset. The comment seems to conflate PC state with 'flags', which is confusing. It should say 'no need to manipulate PC state' or 'no need to manually update PC'.

---

#### code_vs_comment

**Description:** Comment about readonly output textarea contradicts the inline input feature comment

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~1577: 'The output textarea remains readonly.'
Line ~1582: 'Set up Enter key handler for output textarea (for future inline input feature)'

These comments suggest conflicting designs: the output is readonly, but there's a handler for Enter key suggesting future inline input. Additionally, line ~1996 shows code that makes output readonly again after input, suggesting output CAN be made writable. The comments don't clearly explain when/why output would be writable vs readonly.

---

#### code_vs_comment

**Description:** Comment in _save_editor_to_program mentions CP/M EOF marker handling but this seems unnecessary for web editor

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says:
"# Normalize line endings and remove CP/M EOF markers
# \r\n -> \n (Windows line endings, may appear if user pastes text)
# \r -> \n (old Mac line endings, may appear if user pastes text)
# \x1a (Ctrl+Z, CP/M EOF marker - included for consistency with file loading)"

The \x1a (CP/M EOF) handling is described as "for consistency with file loading", but in a web editor context where users are typing/pasting, CP/M EOF markers are extremely unlikely. This suggests the comment may be copy-pasted from file loading code.

---

#### code_vs_comment

**Description:** Comment in _handle_output_enter describes TWO mechanisms for providing input but doesn't explain when each is used

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says:
"# Provide input to interpreter via TWO mechanisms (we check both in case either is active):
# 1. interpreter.provide_input() - Used when interpreter is waiting synchronously
#    (checked via interpreter.state.input_prompt). Stores input for retrieval.
if self.interpreter and self.interpreter.state.input_prompt:
    self.interpreter.provide_input(user_input)

# 2. input_future.set_result() - Used when async code is waiting via asyncio.Future
#    (see _get_input_async method). Only one path will be active at a time, but we
#    check both to handle whichever path the interpreter is currently using."

The comment claims "Only one path will be active at a time" but then checks both unconditionally. This suggests either the comment is wrong (both could be active) or the code is defensive (checking both just in case).

---

#### code_vs_comment

**Description:** Comment in _serialize_runtime mentions closing open files but the actual close call is not shown in the provided code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says:
"Serialize runtime state.

Uses pickle for complex objects:
- statement_table: Contains StatementTable with AST statement nodes (pickled)
- user_functions: Contains DefFnStatementNode AST nodes (pickled)
Other fields use direct serialization (dicts, lists, primitives).

Returns:
    dict: Serialized runtime state
"

Then code shows:
"import pickle

# Close open files first"

But the actual file closing code is not shown (code is cut off). The comment promises file closing but we can't verify it happens.

---

#### code_vs_comment

**Description:** Comment mentions 'PC.stop_reason' for stop state, but no code uses this attribute

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~50 comment: '# Note: stopped flag removed - PC.stop_reason now indicates stop state (display only)'
Line ~68 comment: '# Note: stopped flag removed - PC.stop_reason now indicates stop state (display only)'

The comments reference 'PC.stop_reason' as the new way to indicate stop state, but this attribute is never accessed or used in the visible code. The serialization/restoration code doesn't handle stop_reason at all.

---

#### code_vs_comment

**Description:** Backwards compatibility comments mention ignoring 'halted' and 'stopped' keys, but no actual code implements this

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~60 comment: '# Ignore 'halted' key if present (backwards compatibility with old saved states)'
Line ~69 comment: '# Ignore 'stopped' key if present (backwards compatibility with old saved states)'

The comments claim the code will ignore these keys for backwards compatibility, but there's no actual code that checks for or ignores these keys. The restoration simply doesn't reference them, which means they would be silently ignored anyway, but the comment implies intentional handling.

---

#### code_vs_documentation

**Description:** SessionState tracks auto_save_enabled and auto_save_interval but these features are not documented in editor commands

**Affected files:**
- `src/ui/web/session_state.py`
- `docs/help/common/editor-commands.md`

**Details:**
session_state.py lines 31-32:
    auto_save_enabled: bool = True
    auto_save_interval: int = 30

These auto-save configuration options are stored in session state but are not mentioned in the editor-commands.md documentation, which only mentions "Save/Load programs" without describing auto-save behavior.

---

#### documentation_inconsistency

**Description:** Debugging documentation uses placeholder {{kbd:...}} syntax but actual keybindings are defined in web_keybindings.json

**Affected files:**
- `docs/help/common/debugging.md`
- `src/ui/web_keybindings.json`

**Details:**
debugging.md uses placeholders like:
- "Shortcuts: Tk/Curses/Web: **{{kbd:step:curses}}** or Step button"
- "Press **{{kbd:continue:curses}}** or click **Continue**"
- "Press **{{kbd:quit:curses}}** or click **Stop**"

web_keybindings.json defines actual keys:
- "step": {"keys": ["F10"], "primary": "F10"}
- "continue": {"keys": ["F5"], "primary": "F5"}
- "stop": {"keys": ["Esc"], "primary": "Esc"}

The documentation appears to use a template system that should be replaced with actual keybindings, but this replacement mechanism is not evident in the code.

---

#### documentation_inconsistency

**Description:** Inconsistent guidance on where to find keyboard shortcuts

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md states: "Debugging keyboard shortcuts vary by UI. See your UI-specific help for complete keyboard shortcut reference" and lists specific UI help pages.

editor-commands.md states: "**Important:** Keyboard shortcuts vary by UI. See your UI-specific help for the exact keybindings" and also lists UI-specific help.

Both documents provide the same guidance but use slightly different wording. This is minor but could be standardized for consistency.

---

#### code_comment_conflict

**Description:** Comment describes WebHelpLauncher_DEPRECATED as legacy but provides detailed migration guide suggesting it's still relevant

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Lines 46-54 comment:
"# Legacy class kept for compatibility - new code should use direct web URL instead
# The help site is already built and served at http://localhost/mbasic_docs
#
# Migration guide for code using this class:
# OLD: launcher = WebHelpLauncher(); launcher.open_help("statements/print")
# NEW: open_help_in_browser("statements/print")  # Uses directory-style URLs: /statements/print/
# NEW: In NiceGUI backend, use: ui.navigate.to('/mbasic_docs/statements/print/', new_tab=True)
# Note: MkDocs uses directory-style URLs by default (/path/ not /path.html)"

The extensive migration guide suggests this class is still being actively used and migrated away from, contradicting the "legacy" designation. If truly deprecated, the class could be removed or the comment should clarify it's kept only for backward compatibility with existing code.

---

#### code_vs_documentation

**Description:** SessionState tracks last_edited_line_index and last_edited_line_text for auto-numbering but this state is not documented

**Affected files:**
- `src/ui/web/session_state.py`
- `docs/help/common/debugging.md`

**Details:**
session_state.py lines 42-43:
    last_edited_line_index: Optional[int] = None
    last_edited_line_text: Optional[str] = None

These fields track auto-numbering state but the debugging documentation does not explain how auto-numbering interacts with debugging features like breakpoints or stepping through code.

---

#### documentation_inconsistency

**Description:** Compiler documentation states code generation is 'In Progress' but optimizations.md describes it as if analysis phase is complete

**Affected files:**
- `docs/help/common/compiler/index.md`
- `docs/help/common/compiler/optimizations.md`

**Details:**
index.md states: "**Status:** In Progress\n\nDocumentation for the code generation phase will be added as the compiler backend is developed."

optimizations.md states: "**27 optimizations analyzed** in the semantic analysis phase.\n\nThese optimizations are designed to preserve the original program behavior while identifying opportunities for performance improvement and resource reduction. The actual code transformations will be applied during code generation (currently in development)."

Both indicate code generation is incomplete, but optimizations.md suggests the analysis phase is fully implemented with all 27 optimizations working, while index.md is more vague about overall status.

---

#### documentation_inconsistency

**Description:** Loop examples documentation has internal note about MBASIC 5.21 lacking EXIT FOR/EXIT WHILE but doesn't clarify if this is a limitation or intentional compatibility

**Affected files:**
- `docs/help/common/examples/loops.md`

**Details:**
loops.md lines in "Breaking Out of Loops" section:
"Use GOTO to exit early from a loop.\n\n**Note:** MBASIC 5.21 does not have EXIT FOR or EXIT WHILE statements (those were added in later BASIC versions). GOTO is the standard way to exit loops early in BASIC-80."

This note is helpful but could be cross-referenced with the main language reference to clarify whether this is:
1. A limitation being worked on
2. Intentional for MBASIC 5.21 compatibility
3. Available as an optional extension

The version.py file states "COMPATIBILITY = '100% MBASIC 5.21 compatible with optional extensions'" suggesting extensions might be available, but this isn't clarified in the loops documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent statement about line number range

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/language.md`

**Details:**
getting-started.md states 'Numbers can be 1-65535' but language.md does not specify the valid range for line numbers. This creates an incomplete reference.

---

#### documentation_inconsistency

**Description:** Inconsistent notation for exponent representation

**Affected files:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
data-types.md explains: 'Exponent Notation:
- D notation (e.g., 1.5D+10) forces double-precision representation in the code itself
- E notation (e.g., 1.5E+10) uses single-precision representation by default, but will convert to double if assigned to a # variable
- For practical purposes, both work with # variables, though D notation makes the intent explicit'

However, math-functions.md uses only D notation in examples (e.g., 'BIGNUM# = 1.23456789012345D+100') without explaining the difference or mentioning E notation as an alternative.

---

#### documentation_inconsistency

**Description:** Incomplete cross-reference between character set and ASCII codes

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
character-set.md has a 'See Also' section linking to ascii-codes.md, but ascii-codes.md does not link back to character-set.md in its 'See Also' section. The relationship should be bidirectional for better navigation.

---

#### documentation_inconsistency

**Description:** Inconsistent range notation for INTEGER type

**Affected files:**
- `docs/help/common/language/data-types.md`

**Details:**
data-types.md shows INTEGER range as '-32768 to 32767' in the table, but in the overflow example it shows 'X% = 32767' followed by 'X% = X% + 1' causing overflow. This is correct, but the documentation could be clearer that 32767 is the maximum positive value (2^15 - 1) and -32768 is the minimum (not -32767).

---

#### documentation_inconsistency

**Description:** Incomplete keyboard shortcut table

**Affected files:**
- `docs/help/common/index.md`

**Details:**
index.md shows a table with keyboard shortcuts using template syntax like '{{kbd:run:cli}}' but doesn't explain what these templates resolve to or provide the actual key combinations. Users would need to navigate to UI-specific guides to find the actual shortcuts.

---

#### documentation_inconsistency

**Description:** Cross-reference inconsistency between LOC and LOF

**Affected files:**
- `docs/help/common/language/functions/loc.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
LOC.md 'See Also' section does not reference LOF, but LOF.md 'See Also' section references LOC with description 'Returns current file position/record number (LOF returns total size in bytes)'. This creates an asymmetric cross-reference relationship.

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

#### documentation_inconsistency

**Description:** Inconsistent 'See Also' ordering in mathematical functions

**Affected files:**
- `docs/help/common/language/functions/int.md`
- `docs/help/common/language/functions/sgn.md`
- `docs/help/common/language/functions/sin.md`
- `docs/help/common/language/functions/sqr.md`

**Details:**
Mathematical functions have 'See Also' sections with the same functions but in different orders. For example, INT lists: ABS, ATN, CDBL, CINT, COS, CSNG, EXP, FIX, LOG, RND, SGN, SIN, SQR, TAN. SGN lists: ABS, ATN, COS, EXP, FIX, INT, LOG, RND, SIN, SQR, TAN (missing CDBL, CINT, CSNG). This inconsistency makes it unclear which functions are truly related.

---

#### documentation_inconsistency

**Description:** Inconsistent error handling documentation for zero index

**Affected files:**
- `docs/help/common/language/functions/instr.md`
- `docs/help/common/language/functions/mid_dollar.md`

**Details:**
INSTR.md states: 'Note: If I=0 is specified, an "Illegal function call" error will occur.' MID$.md states: 'Note: If I=0 is specified, an "Illegal function call" error will occur.' However, INSTR description says 'If I>LEN(X$) or if X$ is null or if Y$ cannot be found, INSTR returns O' and 'If Y$ is null, INSTR returns I or 1', suggesting I can be omitted (defaulting to 1) but not explicitly stating what happens when I=0.

---

#### documentation_inconsistency

**Description:** SPACE$ references STRING$ but relationship not fully explained

**Affected files:**
- `docs/help/common/language/functions/space_dollar.md`
- `docs/help/common/language/functions/string_dollar.md`

**Details:**
SPACE$.md states: 'This is equivalent to STRING$(I, 32) since 32 is the ASCII code for a space character.' However, STRING$ is listed in 'See Also' but the documentation doesn't explain that STRING$ is the more general function. Users might not understand that SPACE$ is essentially a convenience wrapper for STRING$.

---

#### documentation_inconsistency

**Description:** FRE documentation has inconsistent argument description

**Affected files:**
- `docs/help/common/language/functions/fre.md`

**Details:**
FRE.md title and description state 'Arguments to FRE are dummy arguments' but the syntax shows two different forms: 'FRE(0)' and 'FRE(X$)'. The description then states 'FRE("") forces a garbage collection' which contradicts the claim that arguments are dummy. The numeric vs string argument appears to have different behavior (garbage collection), so they are not truly 'dummy' arguments.

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

#### documentation_inconsistency

**Description:** Inconsistent formatting of version information in frontmatter

**Affected files:**
- `docs/help/common/language/statements/auto.md`
- `docs/help/common/language/statements/chain.md`

**Details:**
auto.md does not have a 'Versions:' field in its content, while chain.md explicitly states '**Versions:** Disk' in the content body. Other documents like string_dollar.md show versions in a consistent format. The version information should be consistently placed either in frontmatter or in a standard location in the content.

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

#### documentation_inconsistency

**Description:** CLS documentation states it works in all UI backends but doesn't mention which backends exist

**Affected files:**
- `docs/help/common/language/statements/cls.md`

**Details:**
The documentation states:
'**Note:** CLS is implemented in MBASIC and works in all UI backends.'

This implies multiple UI backends exist but doesn't reference where to find information about them. Other system-level commands don't mention UI backends at all.

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

The cross-references are asymmetric - DEF FN references DEF USR but includes GOSUB-RETURN, while DEF USR references DEF FN but includes POKE/PEEK instead.

---

#### documentation_inconsistency

**Description:** EDIT documentation mentions 'Modern MBASIC Implementation' but DELETE does not, despite both being editing commands

**Affected files:**
- `docs/help/common/language/statements/edit.md`
- `docs/help/common/language/statements/delete.md`

**Details:**
edit.md includes:
"### Implementation Note:
**Modern MBASIC Implementation:** This implementation provides full-screen editing capabilities through the integrated editor (Tk, Curses, or Web UI). The EDIT command is recognized for compatibility, but line editing is performed directly in the full-screen editor rather than entering a special edit mode."

delete.md has no such implementation note, even though it's also an editing command that might have modern vs. historical differences.

---

#### documentation_inconsistency

**Description:** INPUT documentation has inconsistent formatting in the Remarks section

**Affected files:**
- `docs/help/common/language/statements/input.md`

**Details:**
The Remarks section uses both 'Key behaviors:' as a subheading with bullet points, but earlier text is in paragraph form. The formatting should be consistent throughout - either all bullets or all paragraphs.

---

#### documentation_inconsistency

**Description:** Index page lists 'LINE INPUT#' with link to inputi.md but the actual file is input_hash.md for INPUT#

**Affected files:**
- `docs/help/common/language/statements/index.md`

**Details:**
In the alphabetical listing under 'I':
"- [LINE INPUT#](inputi.md) - Input entire line from file"

But earlier:
"- [INPUT#](input_hash.md) - Input from file"

The file naming convention is inconsistent - INPUT# uses input_hash.md but LINE INPUT# uses inputi.md. This should be standardized.

---

#### documentation_inconsistency

**Description:** GOSUB-RETURN has 'aliases' field in frontmatter but GOTO does not, despite both being control flow statements

**Affected files:**
- `docs/help/common/language/statements/gosub-return.md`
- `docs/help/common/language/statements/goto.md`

**Details:**
gosub-return.md frontmatter includes:
"aliases: ['gosub-return']"

goto.md frontmatter does not have an aliases field. For consistency, either both should have aliases or neither should (or the aliases should be meaningful alternatives, not just the canonical name).

---

#### documentation_inconsistency

**Description:** Filename inconsistency in title vs syntax

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
Title shows: 'LINE INPUT# (File)'
Syntax shows: 'LINE INPUT#<file number>,<string variable>'
The title adds '(File)' for disambiguation but this is not part of the actual statement name.

---

#### documentation_inconsistency

**Description:** CP/M-specific behavior not marked as platform-specific

**Affected files:**
- `docs/help/common/language/statements/kill.md`

**Details:**
KILL documentation states: 'CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files.'
This is platform-specific behavior but is not clearly marked as such (no 'Note:' prefix or platform indicator like other docs use).

---

#### documentation_inconsistency

**Description:** Inconsistent CP/M extension handling documentation

**Affected files:**
- `docs/help/common/language/statements/load.md`
- `docs/help/common/language/statements/merge.md`
- `docs/help/common/language/statements/kill.md`

**Details:**
LOAD: '(With CP/M, the default extension .BAS is supplied.)'
MERGE: '(With CP/M, the default extension .BAS is supplied if none is specified.)'
KILL: 'CP/M automatically adds .BAS extension if none is specified when deleting BASIC program files.'

The phrasing varies between 'supplied', 'supplied if none is specified', and 'automatically adds'. This should be standardized.

---

#### documentation_inconsistency

**Description:** Inconsistent format numbering in examples

**Affected files:**
- `docs/help/common/language/statements/list.md`

**Details:**
LIST documentation shows:
'Format 1: LIST [<line number>]           (8K version)'
'Format 2: LIST [<line number>[-[<line number>]]]  (Extended, Disk)'

Then in examples:
'Format 1:
            LIST            Lists the program currently
                            in memory.
            LIST 500        In the 8K version, lists
                            all programs lines from
                            500 to the end.
                            In Extended and Disk,
                            lists line 500.
            Format 2:'

The example section uses 'Format 1:' and 'Format 2:' labels but the examples under 'Format 1' include both 8K and Extended/Disk behavior, which is confusing.

---

#### documentation_inconsistency

**Description:** Inconsistent print zone width documentation

**Affected files:**
- `docs/help/common/language/statements/print.md`

**Details:**
PRINT documentation states: 'When items are separated by commas, values are printed in zones of 14 columns each'

However, the zone listing shows:
'Columns 1-14 (first zone)'
'Columns 15-28 (second zone)'
'Columns 29-42 (third zone)'
'Columns 43-56 (fourth zone)'
'Columns 57-70 (fifth zone)'

This is correct for 14-column zones, but should verify this matches actual implementation and is consistent with WIDTH statement behavior.

---

#### documentation_inconsistency

**Description:** Inconsistent seed range documentation

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
RANDOMIZE documentation shows prompt: 'Random Number Seed (-32768 to 32767)?'

This is the range for a 16-bit signed integer, but the documentation doesn't explicitly state this limitation or what happens if a value outside this range is provided.

---

#### documentation_inconsistency

**Description:** Carriage return/line feed sequence handling ambiguity

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
LINE INPUT# documentation states: 'LINE INPUT# reads all characters in the sequential file up to a carriage return. It then skips over the carriage return/line feed sequence'

Then: '(If a line feed/carriage return sequence is encountered, it is preserved.)'

This is contradictory - it says CR/LF is skipped but LF/CR is preserved. The distinction between CR/LF vs LF/CR should be clarified, as this is unusual.

---

#### documentation_inconsistency

**Description:** Similar command names (RESTORE vs RESET) with completely different purposes may cause confusion, but no explicit cross-reference warning exists in RESTORE.md

**Affected files:**
- `docs/help/common/language/statements/restore.md`
- `docs/help/common/language/statements/reset.md`

**Details:**
RESTORE.md is about resetting DATA pointers for READ statements.
RESET.md is about closing all open files.

These are completely different operations but have similar names. RESTORE.md does not warn about confusion with RESET, while RESET warns about RSET.

---

#### documentation_inconsistency

**Description:** RESUME and RESTORE have similar names but completely different purposes (error handling vs DATA pointer), with no cross-reference warnings

**Affected files:**
- `docs/help/common/language/statements/resume.md`
- `docs/help/common/language/statements/restore.md`

**Details:**
RESUME.md: 'To continue program execution after an error recovery procedure has been performed.'

RESTORE.md: 'To reset the DATA pointer so that the next READ statement will access data from the beginning of the program or from a specified line number.'

No warnings about potential confusion between these similar-sounding commands.

---

#### documentation_inconsistency

**Description:** SAVE.md mentions file extensions but RUN.md also mentions default .BAS extension - inconsistent level of detail

**Affected files:**
- `docs/help/common/language/statements/save.md`
- `docs/help/common/language/statements/run.md`

**Details:**
SAVE.md: '(With CP/M, the default extension .BAS is supplied.)'

RUN.md: 'File extension defaults to .BAS if not specified'

Both mention .BAS default but SAVE specifically mentions CP/M while RUN is generic. Should be consistent about OS-specific behavior.

---

#### documentation_inconsistency

**Description:** Inconsistent title formatting between WRITE and WRITE# statements

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md has title: 'WRITE (Screen)'
writei.md has title: 'WRITE# (File)'

The parenthetical clarifications are helpful but the # symbol in the title doesn't match the filename 'writei.md'. Should be consistent.

---

#### documentation_inconsistency

**Description:** Variables.md has conflicting information about variable name significance

**Affected files:**
- `docs/help/common/language/variables.md`

**Details:**
variables.md states:
'**Note on Variable Name Significance:** In the original MBASIC 5.21, only the first 2 characters of variable names were significant (AB, ABC, and ABCDEF would be the same variable). This Python implementation uses the full variable name for identification, allowing distinct variables like COUNT and COUNTER.'

But then under 'Variable Naming Rules' it says:
'Are limited to 40 characters'

If only 2 characters were significant in original MBASIC, why would names be limited to 40 characters? This seems contradictory. Need clarification on whether the 40-character limit is from original MBASIC or this implementation.

---

#### documentation_inconsistency

**Description:** Inconsistent version availability notation

**Affected files:**
- `docs/help/common/language/statements/swap.md`
- `docs/help/common/language/statements/while-wend.md`

**Details:**
swap.md: '**Versions:** Extended, Disk'

while-wend.md: No version information provided

Most statement docs include version info (8K, Extended, Disk), but some are missing it. Should be consistent across all statements.

---

#### documentation_inconsistency

**Description:** TRON-TROFF.md has inconsistent title format (hyphenated) compared to other multi-keyword statements

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
tron-troff.md title: 'TRON-TROFF'

Other multi-keyword statements use different formats:
- while-wend.md title: 'WHILE...WEND'
- for-next.md would likely be 'FOR...NEXT'

Should use consistent separator (either hyphen or ellipsis) for multi-keyword statement titles.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for stopping AUTO mode

**Affected files:**
- `docs/help/common/ui/cli/index.md`
- `docs/help/common/ui/curses/editing.md`

**Details:**
CLI docs use: '{{kbd:stop:cli}}' to stop AUTO mode
Curses docs use: '{{kbd:continue:curses}}' to exit AUTO mode

These appear to be different placeholders for the same action (stopping AUTO mode), but use different names ('stop' vs 'continue'), which is confusing.

---

#### documentation_inconsistency

**Description:** Inconsistent information about immediate mode panel availability

**Affected files:**
- `docs/help/common/ui/tk/index.md`

**Details:**
The Tk UI documentation states: 'Some Tk configurations include an immediate mode panel for quick calculations' but doesn't specify which configurations have it or how to enable it. This creates uncertainty about whether this feature exists in the current implementation.

---

#### documentation_inconsistency

**Description:** Incomplete keyboard shortcuts table

**Affected files:**
- `docs/help/common/ui/cli/index.md`

**Details:**
The CLI keyboard shortcuts table shows:
- Ctrl+D: Exit MBASIC (Unix/Linux)
- Ctrl+Z: Exit MBASIC (Windows)

But earlier in the same document, it mentions '{{kbd:stop:cli}}' for interrupting programs and stopping AUTO mode. This keyboard shortcut is not included in the shortcuts table, creating an incomplete reference.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut placeholder usage

**Affected files:**
- `docs/help/index.md`
- `docs/help/common/ui/cli/index.md`

**Details:**
The main help index uses '{{kbd:find:curses}}' as an example of keyboard shortcut notation.

However, CLI docs use '{{kbd:stop:cli}}' without explaining what this notation means or how it gets resolved.

There's no documentation explaining the {{kbd:action:ui}} placeholder system, making these references potentially confusing to users reading the raw documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent UI count - three vs four interfaces

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/getting-started.md`

**Details:**
getting-started.md section 'Choosing a User Interface' states 'MBASIC supports four interfaces' and lists CLI, Curses, Tkinter, and Web UI. However, features.md in multiple places refers to 'three UIs' or lists only CLI, Curses, and Tk without mentioning Web UI in the main features list. The Web UI section appears later but isn't consistently included in counts.

---

#### documentation_inconsistency

**Description:** Redundant information about graphics LINE statement

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
features.md under Input/Output states: 'LINE INPUT - Full line input (Note: Graphics LINE statement is not implemented)'. not-implemented.md also mentions 'LINE - Draw line (GW-BASIC graphics version - not the LINE INPUT statement which IS implemented)'. This information is duplicated and could be consolidated or cross-referenced.

---

#### documentation_inconsistency

**Description:** Incomplete function count

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md states 'Functions (45+)' but then lists only a subset of functions in categories. The actual count should be verified against the complete function list referenced at 'For the complete list of all functions, see [Functions Index](../common/language/functions/index.md)' to ensure accuracy.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation

**Affected files:**
- `docs/help/mbasic/getting-started.md`
- `docs/help/ui/cli/index.md`

**Details:**
getting-started.md uses template notation like '{{kbd:run:curses}}' for keyboard shortcuts, while cli/index.md and other docs spell out the actual keys or commands. The template notation suggests these are placeholders that should be replaced with actual key combinations, but they appear in the final documentation.

---

#### documentation_inconsistency

**Description:** Planned features documented as current limitations

**Affected files:**
- `docs/help/ui/cli/debugging.md`

**Details:**
cli/debugging.md under STEP command shows 'Planned (not yet implemented): STEP INTO, STEP OVER' and under Limitations states 'STEP INTO/OVER not yet implemented (use STEP)'. This is consistent internally but should be verified that these features are actually planned and not just wishful thinking in the documentation.

---

#### documentation_inconsistency

**Description:** String allocation documentation placement

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`

**Details:**
features.md mentions 'See [Architecture](architecture.md) for details on interpreter vs. compiler modes' but the detailed string allocation document is in implementation/ subdirectory. The architecture.md reference should potentially also point to the string allocation document, or the features.md should reference it directly when discussing string handling.

---

#### documentation_inconsistency

**Description:** Inconsistent explanation of Cut/Copy/Paste unavailability

**Affected files:**
- `docs/help/ui/curses/editing.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
editing.md states:
"**Note:** Cut/Copy/Paste operations are not available in the Curses UI due to keyboard shortcut conflicts:
- **{{kbd:stop:curses}}** (Ctrl+C) - Used for Stop/Interrupt, cannot be used for Copy
- **{{kbd:save:curses}}** (Ctrl+S) - Used for Save File, cannot be used for Paste (also reserved by terminal for flow control)
- Cut would require Ctrl+X which isn't used but omitted for consistency"

feature-reference.md states:
"Standard clipboard operations are not available in the Curses UI due to keyboard shortcut conflicts:
- **{{kbd:stop:curses}}** - Used for Stop/Interrupt (cannot be used for Cut)
- **{{kbd:continue:curses}}** - Terminal signal to exit program (cannot be used for Copy)
- **{{kbd:save:curses}}** - Used for Save File (cannot be used for Paste; {{kbd:save:curses}} is reserved by terminal for flow control)"

The two documents give different explanations for which shortcuts conflict with which clipboard operations. editing.md says Ctrl+C conflicts with Copy, while feature-reference.md says Ctrl+C conflicts with Cut.

---

#### documentation_inconsistency

**Description:** Inconsistent note about Ctrl+S unavailability

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/editing.md`

**Details:**
quick-reference.md states:
"| **{{kbd:save:curses}}** | Save program (Ctrl+S unavailable - terminal flow control) |"

editing.md states:
"### Save File ({{kbd:save:curses}})
Save the current program to disk. If no filename is set, prompts for one.
Note: Uses {{kbd:save:curses}} because {{kbd:save:curses}} is reserved for terminal flow control."

quick-reference.md says "Ctrl+S unavailable" while editing.md says "Ctrl+S is reserved". Both convey the same meaning but use different wording. Should be standardized.

---

#### documentation_inconsistency

**Description:** Self-contradictory keyboard shortcut in variables.md

**Affected files:**
- `docs/help/ui/curses/variables.md`

**Details:**
In the "Window Controls" section, variables.md states:
"### Resize and Position
- **Ctrl+Arrow**: Move window
- **Alt+Arrow**: Resize window
- **Ctrl+M**: Maximize/restore
- **{{kbd:stop:curses}}**: Close window"

But earlier in the same document under "Keyboard Reference", it states:
"| `Esc` | Close window |"

The document lists two different ways to close the window (Esc and {{kbd:stop:curses}}), which may be intentional (multiple shortcuts for same action) but should be clarified.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut references for Continue execution

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/workflows.md`

**Details:**
feature-reference.md states: 'Continue: Resume execution after pausing at a breakpoint. Menu: Run → Continue, Toolbar: "Cont" button, No keyboard shortcut'

workflows.md in 'Debug with Breakpoints' workflow states: 'Use Continue (Run menu) to continue' without mentioning toolbar button.

While not contradictory, the documentation could be more consistent in mentioning all available methods.

---

#### documentation_inconsistency

**Description:** Inconsistent shortcut notation for Run Program

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`

**Details:**
feature-reference.md lists 'Run Program ({{kbd:run_program:tk}} or F5)' in the feature description but in the Quick Reference table only shows '{{kbd:run_program:tk}} / F5'.

While both convey the same information, using consistent notation ('or' vs '/') throughout would improve clarity.

---

#### documentation_inconsistency

**Description:** Inconsistent button capitalization in planned UI mockup

**Affected files:**
- `docs/help/ui/tk/settings.md`

**Details:**
settings.md shows planned dialog mockup with buttons: '[ Reset to Defaults ]  [ Apply ]' and '[ Cancel ] [OK]'

Later in 'Button Actions' section, buttons are referred to as 'OK', 'Cancel', 'Apply', 'Reset to Defaults' with consistent capitalization.

The mockup should use consistent capitalization matching the descriptions.

---

#### documentation_inconsistency

**Description:** Inconsistent information about Open Example feature availability

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
features.md under 'File Operations > Open Files (Planned)' lists as a planned feature: 'Recent files list'

However, getting-started.md under 'Recent Files' section describes it as currently available: 'File → Recent Files shows recently opened files (saved in localStorage, persists across browser sessions).'

Additionally, web-interface.md under 'File Menu' states: 'Note: An "Open Example" feature to choose from sample BASIC programs is planned for a future release.'

The inconsistency: Recent Files appears to be implemented (per getting-started.md) but is listed as planned in features.md. Also, 'Open Example' is mentioned as planned but not consistently documented.

---

#### documentation_inconsistency

**Description:** Missing Games Library reference in library category index files

**Affected files:**
- `docs/help/ui/web/index.md`
- `docs/library/business/index.md`
- `docs/library/data_management/index.md`
- `docs/library/demos/index.md`
- `docs/library/education/index.md`

**Details:**
index.md under 'Games Library' section prominently features: '- **[Games Library](../../../library/games/index.md)** - 113 classic CP/M era games to download and load!'

However, the other library category index files (business/index.md, data_management/index.md, demos/index.md, education/index.md) do not include any cross-references to the Games Library or other library categories.

The inconsistency: The Games Library is highlighted in the main help index but not cross-referenced in other library category indexes, making it harder for users browsing other categories to discover the games collection.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation format

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
features.md uses the format: {{kbd:run:web}}, {{kbd:continue:web}}, {{kbd:step:web}}, etc.

getting-started.md uses the same format in some places but also includes it in parentheses with button descriptions: '(▶️ green button, {{kbd:run:web}})'

The inconsistency: The notation is consistent, but the presentation style varies. Some places show just the shortcut, others show it with button icons and descriptions. This is minor but could be standardized for consistency.

---

#### documentation_inconsistency

**Description:** Inconsistent menu structure documentation

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
features.md under 'Debugging Tools > Breakpoints > Management' states: 'Toggle via Run menu → Toggle Breakpoint'

web-interface.md under 'Menu Functions > Run Menu' lists: '- Toggle Breakpoint - Set or remove a breakpoint at a specific line number'

However, web-interface.md also lists a 'View Menu' with: '- Show Variables - Open the Variables Window to view and monitor program variables in real-time'

But features.md under 'Variable Inspector > Currently Implemented' states: 'Basic variable viewing via Debug menu'

The inconsistency: features.md mentions a 'Debug menu' for variable viewing, but web-interface.md shows it under 'View Menu'. There's no 'Debug menu' listed in web-interface.md's menu structure.

---

#### documentation_inconsistency

**Description:** Category name mismatch in header and footer

**Affected files:**
- `docs/library/electronics/index.md`

**Details:**
Header says '# MBASIC Electronics Programs' but the footer section says '## About These Electronics' (missing 'Programs'). Other library docs consistently use the full category name in the footer (e.g., 'About These Games', 'About These Ham Radio', 'About These Telecommunications').

---

#### documentation_inconsistency

**Description:** Inconsistent footer section naming pattern

**Affected files:**
- `docs/library/ham_radio/index.md`
- `docs/library/telecommunications/index.md`

**Details:**
Ham Radio footer says '## About These Ham Radio' and Telecommunications says '## About These Telecommunications', but these should probably be '## About These Ham Radio Programs' and '## About These Telecommunications Programs' to match the pattern in other libraries (Games, Utilities, etc.).

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

#### documentation_inconsistency

**Description:** Million.bas categorization inconsistency

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
Million.bas is described as 'Millionaire life simulation game - make financial decisions to accumulate wealth' with tags 'simulation, financial, game', but it's placed in the Utilities library rather than the Games library where it would seem to belong based on its description.

---

#### documentation_inconsistency

**Description:** Rotate.bas categorization inconsistency

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
Rotate.bas is described as 'Letter rotation puzzle game - order letters A-P by rotating groups clockwise' with tags 'puzzle, game, logic', but it's placed in the Utilities library rather than the Games library where games typically belong.

---

#### documentation_inconsistency

**Description:** Bearing.bas categorization inconsistency

**Affected files:**
- `docs/library/electronics/index.md`

**Details:**
Bearing.bas is described as 'Compute bearings between geographic coordinates - calculates distance and bearing between two latitude/longitude positions' with tags 'geography, navigation, coordinates, bearing'. This appears to be a navigation/geography utility rather than an electronics program. It might be better suited for a different category or the Utilities library.

---

#### documentation_inconsistency

**Description:** Reference to non-existent bug report link

**Affected files:**
- `docs/user/CASE_HANDLING_GUIDE.md`

**Details:**
The CASE_HANDLING_GUIDE.md is in docs/user/ but references features that aren't mentioned in the library documentation. More importantly, the library index.md states '⚠️ **Important:** These programs have had minimal testing by humans. If you encounter issues, please submit a bug report (link coming soon).' - the bug report link is marked as 'coming soon' but no actual link or instructions are provided.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation between documents

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md uses plain text for shortcuts:
'**Unique advantages:**
- Keyboard shortcuts'

QUICK_REFERENCE.md uses template notation:
'| `{{kbd:new}}` | New | Clear program, start fresh |'
'| `{{kbd:open}}` | Load | Load program from file |'

The {{kbd:command}} notation is explained in QUICK_REFERENCE.md but not in CHOOSING_YOUR_UI.md, which could confuse users reading both documents.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of UI names

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
Throughout CHOOSING_YOUR_UI.md, UI names are capitalized inconsistently:
- Sometimes 'Curses' (capitalized)
- Sometimes 'curses' (lowercase)
- Sometimes 'Tk' (capitalized)
- Sometimes 'tk' (lowercase)

Examples:
'### 📟 Curses (Terminal UI)' vs 'python3 mbasic --ui curses'
'### 🪟 Tk (Desktop GUI)' vs 'python3 mbasic --ui tk'

This inconsistency appears throughout the document in headings, commands, and prose.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for line ending types

**Affected files:**
- `docs/user/FILE_FORMAT_COMPATIBILITY.md`

**Details:**
FILE_FORMAT_COMPATIBILITY.md uses inconsistent terminology:

'MBASIC saves all program files using **LF line endings** (Line Feed, `\n`, Unix-style).'

Then later:
'- LF (`\n`, Unix/Linux/Mac)'

The first reference says 'Unix-style' while the second says 'Unix/Linux/Mac', which could be confusing since Mac historically used CR (before OS X). The document should clarify this refers to modern macOS (OS X and later).

---

#### documentation_inconsistency

**Description:** README claims keyboard-shortcuts.md is Curses-specific but QUICK_REFERENCE.md also covers Curses shortcuts

**Affected files:**
- `docs/user/README.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
README.md states:
'- **[keyboard-shortcuts.md](keyboard-shortcuts.md)** - Keyboard shortcuts reference (Curses UI specific; Tk shortcuts in TK_UI_QUICK_START.md)'

And:
'- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference (Curses UI specific)'

Both documents are described as Curses-specific and both cover keyboard shortcuts. The relationship between these two documents is unclear - are they duplicates? Does one supersede the other? Should users read both?

---

#### documentation_inconsistency

**Description:** Inconsistent command examples for Python invocation

**Affected files:**
- `docs/user/INSTALL.md`

**Details:**
INSTALL.md states:
'> **Note:** This guide uses `python3` in all examples. On some systems (especially Windows), Python 3 is available as `python` instead.'

But then provides Windows-specific examples using `python`:
'**On Windows:**
```cmd
python -m venv venv
```'

This is correct but contradicts the earlier note that says the guide uses `python3` in ALL examples. The guide should either consistently use `python3` with a note about substitution, or use the platform-appropriate command in each example.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut template notation between documents

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md uses notation like {{kbd:run_program}}, {{kbd:file_save}}, {{kbd:smart_insert}} without UI suffix.

UI_FEATURE_COMPARISON.md uses notation with UI suffix like {{kbd:run:cli}}, {{kbd:run:curses}}, {{kbd:run_program:tk}}, {{kbd:run:web}}, {{kbd:save:cli}}, {{kbd:save:curses}}, {{kbd:file_save:tk}}, {{kbd:save:web}}.

The comparison guide explicitly states: 'This guide uses {{kbd:action:ui}} notation for keyboard shortcuts' but TK_UI_QUICK_START.md does not follow this convention consistently (no :tk suffix).

---

#### documentation_inconsistency

**Description:** Inconsistent feature status for Find/Replace in Web UI

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md Feature Availability Matrix shows:
- Find/Replace for Web: 📋 (Planned for future implementation)
- Notes column: 'Tk: implemented, Web: planned'

UI_FEATURE_COMPARISON.md 'Feature Implementation Status' section under 'Recently Added (2025-10-29)' lists:
- ✅ Tk: Find/Replace functionality

But under 'Coming Soon' it lists:
- ⏳ Find/Replace in Web UI

This is consistent within UI_FEATURE_COMPARISON.md but TK_UI_QUICK_START.md doesn't mention that Find/Replace is Tk-exclusive, only noting '(Tk UI only)' in the keyboard shortcuts table.

---

#### documentation_inconsistency

**Description:** Inconsistent feature status notation for Curses mouse support

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In the 'Feature Availability Matrix' under 'User Interface' section:
- Mouse support for Curses: ⚠️ with Notes: 'Curses: limited, terminal-dependent'

In the 'Detailed UI Descriptions' under 'Curses (Terminal UI)' Limitations:
- 'Limited mouse support'

In the 'User Interface' feature table:
- 'Resizable panels' for Curses: ❌ with Notes: 'Curses: fixed 70/30 split (not user-resizable)'

The Notes column for 'Resizable panels' provides specific implementation details (fixed 70/30 split) but the 'Mouse support' entry only says 'limited, terminal-dependent' without clarifying what 'limited' means or which mouse features work.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of 'Execution Stack Window' vs 'Variables Window'

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
Throughout TK_UI_QUICK_START.md:
- 'Variables Window' is consistently capitalized (appears 15+ times)
- 'Execution Stack Window' is consistently capitalized (appears 5+ times)

However, in keyboard shortcuts table:
- {{kbd:toggle_variables}} | Show/hide Variables Window
- {{kbd:toggle_stack}} | Show/hide Execution Stack Window

But in section headers:
- '## Variable Case Preservation' (not 'Variables')
- '### Variables Window Features:' (plural)
- '### Execution Stack Window' (singular 'Stack')

The inconsistency is minor but 'Variable' vs 'Variables' and whether to capitalize 'Window' varies slightly.

---

#### documentation_inconsistency

**Description:** Document references FILE_FORMAT_COMPATIBILITY.md which is not provided

**Affected files:**
- `docs/user/sequential-files.md`

**Details:**
At the end of sequential-files.md under 'See Also' section:
- [File Format Compatibility](FILE_FORMAT_COMPATIBILITY.md) - Line endings and file format compatibility

This file is not included in the provided documentation files. It's unclear if this is a missing file or an incorrect reference.

---

#### documentation_inconsistency

**Description:** Inconsistent reference to help documentation location

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md 'Next Steps' section lists:
- **Debugging**: See [Debugging Features](../help/common/debugging.md)
- **Keyboard Shortcuts**: See [Tk Keyboard Shortcuts](keyboard-shortcuts.md)
- **BASIC Language**: See [Language Reference](../help/common/language/index.md)
- **Editor Features**: See [Editor Commands](../help/common/editor-commands.md)

The paths are inconsistent:
- Some use ../help/common/ prefix (debugging.md, language/index.md, editor-commands.md)
- One uses no prefix (keyboard-shortcuts.md)

Also, as noted earlier, keyboard-shortcuts.md is for Curses UI, not Tk UI.

---


## Summary

- Total issues found: 673
- Code/Comment conflicts: 234
- Other inconsistencies: 439
