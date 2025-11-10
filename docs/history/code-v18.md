# Code Behavior Issues Report (v18)

Generated: 2025-11-09 21:24:14
Category: Code behavior changes, bug fixes, logic errors
Status: Issues that CHANGE what the code does

## 🔴 High Severity

#### Code vs Comment conflict

**Description:** Missing #include <math.h> for pow() function usage

**Affected files:**
- `src/codegen_backend.py`

**Details:**
In generate() method, the code includes:
code.append('#include <stdio.h>')

But _generate_binary_op() uses pow() function:
if expr.operator == TokenType.POWER:
    return f'pow({left}, {right})'

The comment in get_compiler_command() says:
"# -lm links the math library for floating point support"

But without '#include <math.h>', the generated C code will have an undefined reference to pow(). The -lm flag links the library but doesn't provide the declaration.

---
---

#### code_vs_comment

**Description:** Comment claims CONT fails if program edited, but clear_execution_state() doesn't clear stopped flag

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in cmd_cont() at line ~260 states:
'IMPORTANT: CONT will fail with "?Can't continue" if the program has been edited
(lines added, deleted, or renumbered) because editing clears the GOSUB/RETURN and
FOR/NEXT stacks to prevent crashes from invalidated return addresses and loop contexts.
See clear_execution_state() for details.'

However, clear_execution_state() at line ~145 does:
'self.program_runtime.stopped = False'

This CLEARS the stopped flag, which would make CONT think there's nothing to continue. The comment says editing causes CONT to fail, but the code clears the stopped flag which is what CONT checks. This is contradictory - either clear_execution_state() should NOT clear stopped flag, or the comment is wrong about CONT failing after edits.

---
---

#### code_vs_comment

**Description:** Comment claims CLEAR silently ignores file close errors, but code uses bare except which could hide other errors

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1270 states:
"# Close all open files
# Note: Errors during file close are silently ignored (bare except: pass).
# This differs from RESET which allows errors to propagate to the caller."

Code at line ~1274:
"for file_num in list(self.runtime.files.keys()):
    try:
        file_obj = self.runtime.files[file_num]
        if hasattr(file_obj, 'close'):
            file_obj.close()
    except:
        pass"

The bare except catches ALL exceptions, not just file close errors. This could hide bugs like KeyError, AttributeError, etc. The comment describes the intent (ignore file close errors) but the implementation is broader than documented.

---
---

#### code_vs_comment

**Description:** execute_step() docstring claims method is 'NOT FUNCTIONAL' but the method body appears to execute code

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring states: 'IMPORTANT: This method is a placeholder and does NOT actually perform stepping.'

However, the method body executes:
  count = stmt.count if stmt.count else 1
  self.io.output(f"STEP {count} - Debug stepping not fully implemented")

The method does execute and produce output, so calling it 'NOT FUNCTIONAL' is misleading. It would be more accurate to say it's 'partially implemented' or 'outputs a message but doesn't perform actual stepping'.

---
---

#### code_vs_comment

**Description:** serialize_let_statement() docstring claims it 'always outputs without LET keyword' but the function name and LetStatementNode suggest it should handle LET statements. The comment explains this is intentional but creates semantic confusion.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring: 'Serialize assignment statement (always outputs without LET keyword).'

Design decision comment: 'LetStatementNode represents both explicit LET statements and implicit assignments in the AST. This serializer intentionally ALWAYS outputs the implicit assignment form (A=5) without the LET keyword, regardless of the original source.'

This means the function named 'serialize_let_statement' never outputs 'LET', which is semantically confusing. The AST node is called 'LetStatementNode' but doesn't preserve whether LET was present.

---
---

#### Code vs Documentation inconsistency

**Description:** STEP command behavior differs between CLI and curses UI, but documentation doesn't clearly distinguish them. CLI STEP executes 'one statement' while curses has both 'Step Statement' (Ctrl+T) and 'Step Line' (Ctrl+K). The CLI keybindings.json only documents STEP without mentioning the statement vs line distinction.

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/cli_keybindings.json`
- `src/ui/curses_keybindings.json`

**Details:**
cli_debug.py cmd_step docstring:
"STEP command - execute one statement and pause.

Executes a single statement (not a full line). If a line contains multiple
statements separated by colons, each statement is executed separately.

This implements statement-level stepping similar to the curses UI 'Step Statement'
command (Ctrl+T). The curses UI also has a separate 'Step Line' command (Ctrl+K)
which is not available in the CLI."

cli_keybindings.json:
"step": {
  "keys": ["STEP", "STEP n"],
  "primary": "STEP",
  "description": "Execute next statement or n statements (STEP | STEP n)"
}

curses_keybindings.json has both:
"step_line": {"keys": ["Ctrl+K"], "description": "Step Line (execute all statements on current line)"}
"step": {"keys": ["Ctrl+T"], "description": "Step statement (execute one statement)"}

The CLI lacks the 'step line' functionality but this limitation is only documented in code comments, not in user-facing keybindings.json.

---
---

#### code_internal_inconsistency

**Description:** editor_lines dict is referenced in multiple methods but never populated, causing potential KeyError or incorrect behavior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
editor_lines is used in:
1. Line ~151: self.editor_lines = {}  # Initialized empty
2. Line ~1009: line_code = self.editor_lines.get(state.current_line, "")  # Used in _debug_step
3. Line ~1016: line_code = self.editor_lines.get(state.current_line, "")  # Used in _debug_step
4. Line ~1095: line_code = self.editor_lines.get(state.current_line, "")  # Used in _debug_step_line

But editor_lines is never populated from editor.lines or program.lines. The _save_editor_to_program() method syncs editor.lines to program.lines, but not to editor_lines. This means line_code will always be empty string during debugging.

---
---

#### code_vs_comment

**Description:** Critical inconsistency in _sync_program_to_runtime PC handling logic and comments

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The docstring states:
'PC handling:
- If running and not paused at breakpoint: Preserves PC and execution state
- If paused at breakpoint: Resets PC to halted (prevents accidental resumption)
- If not running: Resets PC to halted for safety'

However, the code comment says:
'# When paused_at_breakpoint=True, we reset PC to halted to prevent accidental resumption. When the user continues from a breakpoint (via _debug_continue), the interpreter's state already has the correct PC and simply clears the halted flag.'

But there is NO _debug_continue method in this file. The comment references a non-existent method, suggesting either:
1. The method was removed/renamed
2. The comment is from a different implementation
3. The feature is incomplete

---
---

#### code_vs_comment

**Description:** Variables window heading text comment claims it matches sort state but uses hardcoded text that may not reflect actual state

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 1088-1089: '# Set initial heading text with down arrow (matches self.variables_sort_column='accessed', descending)
        tree.heading('#0', text='↓ Variable (Last Accessed)')'
Line 122: 'self.variables_sort_column = 'accessed'  # Current sort column (default: 'accessed' for last-accessed timestamp)'
Line 123: 'self.variables_sort_reverse = True  # Sort direction: False=ascending, True=descending (default descending for timestamps)'
The comment claims the heading text matches the sort state, but the heading is set with hardcoded text. If the sort state changes, the heading won't automatically update unless there's code to do so (not visible in snippet).

---
---

#### code_vs_comment_conflict

**Description:** Comment about Tk Text widget design contradicts actual behavior of _remove_blank_lines

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines method around line 1940:
Comment: "Tk Text widgets always end with a newline character (Tk design - text content ends at last newline, so there's always an empty final line)."

But the code that preserves the final line:
for i, line in enumerate(lines):
    if line.strip() or i == len(lines) - 1:
        filtered_lines.append(line)

This preserves the last line regardless of whether it's blank. However, if Tk Text always ends with a newline, then lines[-1] would always be empty string after split('\n'). The code preserves this empty string, which is correct. But the comment makes it sound like this is a Tk quirk being worked around, when actually the code is just preserving the final newline that split() creates. The comment conflates Tk's internal representation with Python's string split behavior.

---
---

#### code_vs_comment

**Description:** Method name _add_immediate_output() contradicts its docstring and implementation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method docstring: "Add text to main output pane. Note: This method name is historical/misleading - it actually adds to the main output pane, not a separate immediate output pane."

The method name suggests it adds to immediate output, but it actually forwards to _add_output() for main output. This is a naming inconsistency that could confuse maintainers.

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

#### documentation_inconsistency

**Description:** Keyboard shortcuts documentation contradicts itself about where to find UI-specific shortcuts

**Affected files:**
- `docs/help/common/editor-commands.md`
- `docs/help/common/debugging.md`

**Details:**
editor-commands.md states: "**Important:** Keyboard shortcuts vary by UI. See your UI-specific help for the exact keybindings" and lists specific UI help pages.

However, debugging.md has a section titled "Keyboard Shortcuts" that says "Debugging keyboard shortcuts vary by UI. See your UI-specific help for complete keyboard shortcut reference" but then also includes placeholder text like "{{kbd:step:curses}}" suggesting it should contain actual shortcuts.

The {{kbd:...}} placeholders appear throughout debugging.md (e.g., "{{kbd:step:curses}}", "{{kbd:continue:curses}}", "{{kbd:quit:curses}}", "{{kbd:toggle_stack:tk}}", "{{kbd:step_line:curses}}") but these are not defined anywhere and appear to be template placeholders that were never filled in.

---
---

#### documentation_inconsistency

**Description:** BREAK command not listed in features but documented in CLI debugging

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
cli/debugging.md extensively documents the BREAK command for breakpoint management: 'BREAK [line_number] - Set breakpoint at line', 'BREAK - List all breakpoints', 'BREAK CLEAR - Clear all breakpoints'

However, features.md under 'Program Control' -> 'Direct Commands' does not list BREAK as an available command.

This is a significant omission as BREAK is a core debugging feature.

---
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
---

#### documentation_inconsistency

**Description:** Inconsistent feature count claims in feature-reference.md

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/tips.md`

**Details:**
feature-reference.md claims specific feature counts:
- File Operations (8 features) - but lists: New, Open, Save, Save As, Recent Files, Auto-Save, Delete Lines, Merge Files = 8 ✓
- Execution & Control (6 features) - lists: Run, Stop, Continue, List, Renumber, Auto Line Numbers = 6 ✓
- Debugging (6 features) - lists: Breakpoints, Step Statement, Step Line, Clear All, Multi-Statement Debug, Current Line Highlight = 6 ✓
- Variable Inspection (6 features) - lists: Variables Window, Edit Variable, Filtering, Sorting, Execution Stack, Resource Usage = 6 ✓
- Editor Features (7 features) - lists: Line Editing, Multi-Line Edit, Cut/Copy/Paste, Find/Replace, Smart Insert, Sort Lines, Syntax Checking = 7 ✓
- Help System (4 features) - lists: Help Command, Integrated Docs, Search Help, Context Help = 4 ✓

However, the 'Search Help' feature has a malformed shortcut and may not be implemented.

---
---

#### documentation_inconsistency

**Description:** Contradictory information about step execution shortcuts

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/features.md`

**Details:**
debugging.md states:
- Step ({{kbd:step:web}}) - Step to next line
- Note: The Web UI uses {{kbd:step:web}} for stepping. Statement-level stepping is not yet implemented.

But features.md Execution Control section states:
- Currently Implemented:
  - Step statement ({{kbd:step:web}})
  - Step line ({{kbd:step_line:web}})

This contradicts whether statement-level stepping exists and what the shortcuts are.

---
---

#### documentation_inconsistency

**Description:** Contradictory keyboard shortcuts documentation

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/features.md`

**Details:**
debugging.md Keyboard Shortcuts section lists:
- Currently Implemented:
  - {{kbd:run:web}} - Run program from beginning
  - {{kbd:continue:web}} - Continue to next breakpoint
  - {{kbd:step:web}} - Step to next line
  - {{kbd:stop:web}} - Stop execution
- Planned for Future Releases:
  - Statement-level stepping (execute one statement at a time)
  - Navigation shortcuts for debugger panels
  - Variable inspector shortcuts
- Note: {{kbd:toggle_breakpoint:web}} is implemented but currently available via menu only (not yet bound to keyboard).

But features.md Execution Control section lists:
- Currently Implemented:
  - Run ({{kbd:run:web}})
  - Continue ({{kbd:continue:web}})
  - Step statement ({{kbd:step:web}})
  - Step line ({{kbd:step_line:web}})
  - Stop ({{kbd:stop:web}})

This contradicts whether {{kbd:step_line:web}} exists and whether {{kbd:step:web}} is for statements or lines.

---
---

#### documentation_inconsistency

**Description:** Conflicting information about CLI debugging capabilities

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
docs/user/CHOOSING_YOUR_UI.md states about CLI:
'Limitations:
- Line-by-line editing only
- No visual debugging (text commands only)
- No mouse support
- No Save without filename'

And includes a note: 'CLI has full debugging capabilities through commands (BREAK, STEP, STACK), but lacks the visual debugging interface'

However, docs/user/QUICK_REFERENCE.md is titled 'MBASIC Curses IDE - Quick Reference Card' and describes breakpoint debugging with visual indicators (● markers) and keyboard shortcuts (b, F9, c, s, e).

The CLI limitations description suggests CLI has text-based debugging commands, but the Quick Reference only documents Curses UI debugging, leaving CLI debugging commands undocumented.

---
---

#### documentation_inconsistency

**Description:** Feature matrix shows conflicting implementation status for 'Edit variables' feature

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In the 'Debugging Features' table:

Row 'Edit variables' shows:
- CLI: ❌
- Curses: ⚠️
- Tk: ✅
- Web: ✅
- Notes: 'CLI: immediate mode only'

The ⚠️ for Curses with no explanation in Notes column is inconsistent with the legend which states '⚠️ | Partially implemented (see Notes column for details)'. The Notes column says 'CLI: immediate mode only' but doesn't explain what 'partially implemented' means for Curses.

Later in 'Detailed UI Descriptions' under Curses Limitations: 'Partial variable editing' is mentioned, but no details given.

Under 'Known Gaps': 'Curses: Limited variable editing' is mentioned.

The exact nature of Curses variable editing capability is unclear and inconsistently described.

---

---

## 🟡 Medium Severity

#### Code vs Comment conflict

**Description:** VariableNode type_suffix and explicit_type_suffix documentation may be confusing

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode docstring lines 1027-1037:
'Type suffix handling:
- type_suffix: The actual suffix character ($, %, !, #) when present
- explicit_type_suffix: Boolean indicating the origin of type_suffix:
    * True: suffix appeared in source code (e.g., "X%" in "X% = 5")
    * False: suffix inferred from DEFINT/DEFSNG/DEFDBL/DEFSTR (e.g., "X" with DEFINT A-Z)

Example: In "DEFINT A-Z: X=5", variable X has type_suffix='%' and explicit_type_suffix=False.
The suffix must be tracked for type checking but not regenerated in source code.
Both fields must always be examined together to correctly handle variable typing.'

VariableNode lines 1040-1042:
'type_suffix: Optional[str] = None  # $, %, !, # - The actual suffix (see explicit_type_suffix for origin)
explicit_type_suffix: bool = False  # True if type_suffix was in original source, False if inferred from DEF'

The documentation states 'type_suffix: The actual suffix character ($, %, !, #) when present' but the type is Optional[str] = None, meaning it can be None. The phrase 'when present' is ambiguous - does it mean 'when the field is not None' or 'when a suffix exists (explicit or inferred)'? The example clarifies that type_suffix='%' even when explicit_type_suffix=False, but this could be clearer.

---
---

#### code_vs_comment

**Description:** Inconsistent handling of sign in format_numeric_field - comment says 'reserves 1 char for sign' but implementation may not always reserve space correctly

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment in parse_numeric_field docstring:
"Sign behavior:
- leading_sign: + at start, always adds + or - sign (reserves 1 char for sign)
- trailing_sign: + at end, always adds + or - sign (reserves 1 char for sign)
- trailing_minus_only: - at end, adds - for negative OR space for non-negative (reserves 1 char)"

In format_numeric_field, the code has:
if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
    field_width += 1  # Sign takes up one position

But later:
if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
    available_width -= 1  # Reserve space for sign (or space for trailing_minus_only)

The comment in the second location adds clarification '(or space for trailing_minus_only)' which suggests the behavior is the same for all three, but the docstring describes different behaviors.

---
---

#### code_vs_comment

**Description:** EOF method comment references execute_open() in interpreter.py but this file is not provided for verification

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment states: "The 'I' mode from BASIC's OPEN statement is stored in file_info['mode'] and corresponds to binary input, which execute_open() in interpreter.py implements by opening the file with Python mode 'rb'."

This creates a dependency on understanding interpreter.py's execute_open() method which is not available in the provided files. If execute_open() doesn't actually store mode as 'I' or doesn't open with 'rb', this comment would be misleading.

---
---

#### Code vs Documentation inconsistency

**Description:** Documentation claims math library support but implementation may not handle all cases

**Affected files:**
- `src/codegen_backend.py`

**Details:**
get_compiler_command() docstring says:
"# -lm links the math library for floating point support"

And the command includes '-lm' flag. However, the _generate_binary_op() method only handles the POWER operator with pow() function:
"if expr.operator == TokenType.POWER:
    # Use pow() function from math.h
    return f'pow({left}, {right})'"

The code includes '#include <stdio.h>' but does NOT include '#include <math.h>' which is required for pow(). This means the generated C code will fail to compile when using the ^ (power) operator.

---
---

#### code_vs_comment

**Description:** Docstring for cmd_chain() describes ChainException behavior but doesn't match when it's raised

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring at line ~457 states:
'Raises ChainException when called during program execution to signal the interpreter's
run() loop to restart with the new program. This avoids recursive run() calls.
When called from command line (not during execution), runs the program directly.'

However, the code at line ~555 raises ChainException when 'self.program_runtime and self.program_interpreter' exist, not specifically 'during program execution'. These objects persist after RUN completes, so ChainException would be raised even when called from command line after a previous RUN. The docstring's distinction between 'during execution' and 'from command line' doesn't match the actual condition.

---
---

#### code_vs_comment

**Description:** Comment about NEXT validation describes return_stmt range incorrectly

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

But the code checks:
"if return_stmt > len(line_statements):
    raise RuntimeError(f"NEXT error: FOR statement in line {return_line} no longer exists")"

This validation allows return_stmt == len(line_statements) as valid (the sentinel), which matches the comment. However, the comment's description of the sentinel as "FOR was last statement on line" is potentially misleading - it's actually the position AFTER the last statement, not the last statement itself.

---
---

#### code_vs_comment

**Description:** Comment in execute_list() warns about line_text_map sync issues but doesn't specify what happens if sync fails

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment states: 'If ProgramManager fails to maintain this sync, LIST output may show stale or incorrect line text.'

The code doesn't handle the case where line_text_map is out of sync. If a line exists in statement_table but not in line_text_map, the code silently skips it (the 'if line_num in self.runtime.line_text_map' check). This behavior should be documented or the code should warn about missing lines.

---
---

#### code_vs_comment

**Description:** execute_lset() and execute_rset() fallback behavior documented as 'deliberate extension' but may cause confusion

**Affected files:**
- `src/interpreter.py`

**Details:**
Both methods have identical comments: 'Compatibility note: In strict MBASIC 5.21, LSET/RSET are only for field variables (used with FIELD statement for random file access). This fallback is a deliberate extension for compatibility with code that uses LSET for general string formatting. This is documented behavior, not a bug.'

However, the fallback just calls set_variable_raw() with no special formatting. For LSET, it doesn't left-justify, and for RSET, it doesn't right-justify. The comment claims this is for 'general string formatting' but the code doesn't actually format the string in the fallback case. This is inconsistent with the stated purpose.

---
---

#### code_vs_documentation

**Description:** Documentation claims RND and INKEY$ are the ONLY functions that can be called without parentheses, but code implementation may allow other patterns

**Affected files:**
- `src/parser.py`

**Details:**
Module docstring states:
"Exception: Only RND and INKEY$ can be called without parentheses in MBASIC 5.21
(this is specific to these two functions, not a general MBASIC feature)"

However, in parse_builtin_function(), the code only checks for RND and INKEY specifically:
if func_token.type == TokenType.RND and not self.match(TokenType.LPAREN):
    # RND without parentheses - valid in MBASIC 5.21
    return FunctionCallNode(...)

if func_token.type == TokenType.INKEY and not self.match(TokenType.LPAREN):
    # INKEY$ without parentheses - valid in MBASIC 5.21
    return FunctionCallNode(...)

The documentation is consistent with implementation, but the claim of 'ONLY' these two functions needs verification against actual MBASIC 5.21 behavior.

---
---

#### code_vs_comment

**Description:** Inconsistent documentation about DEFTYPE statement behavior and def_type_map updates

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deftype() method around line 1870:

Comment states: "Note: This method always updates def_type_map during parsing. The type map is shared across all statements (both in interactive mode where statements are parsed one at a time, and in batch mode where the entire program is parsed). The type map affects variable type inference throughout the program. The AST node is created for program serialization/documentation."

However, the implementation shows the method updates def_type_map using lowercase letters:
self.def_type_map[letter_char] = var_type
letters.add(letter_char)

But throughout other methods (parse_for, parse_next), the code checks def_type_map using lowercase:
first_letter = var_name[0].lower()
if first_letter in self.def_type_map:

This is internally consistent, but the comment doesn't explicitly mention the lowercase normalization strategy, which is an important implementation detail.

---
---

#### code_vs_comment

**Description:** Inconsistent handling of type suffixes in DIM vs other statements

**Affected files:**
- `src/parser.py`

**Details:**
In parse_dim() method around line 1760:

The code adds type suffixes based on def_type_map:
if name and name[-1] not in '$%!#':
    first_letter = name[0].lower()
    if first_letter in self.def_type_map:
        var_type = self.def_type_map[first_letter]
        if var_type == TypeInfo.STRING:
            name = name + '$'
        elif var_type == TypeInfo.INTEGER:
            name = name + '%'
        elif var_type == TypeInfo.DOUBLE:
            name = name + '#'
        # SINGLE (!) is the default, no need to add suffix

However, in parse_for() and parse_next() methods, the code checks def_type_map but assigns type_suffix to a variable field rather than modifying the name:
if not type_suffix:
    first_letter = var_name[0].lower()
    if first_letter in self.def_type_map:
        var_type = self.def_type_map[first_letter]
        if var_type == TypeInfo.STRING:
            type_suffix = '$'
        elif var_type == TypeInfo.INTEGER:
            type_suffix = '%'

This inconsistency in how type suffixes are handled (modifying name vs setting type_suffix field) could lead to bugs or confusion.

---
---

#### code_vs_comment

**Description:** parse_width() docstring claims device parameter is optional and can be file number or device name, but MBASIC 5.21 documentation shows WIDTH statement syntax as 'WIDTH [device$,] width' where device is a string device name, not a file number

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says:
"Syntax: WIDTH width [, device]
...
device: Optional device expression (e.g., file number like 1, or device name).
In MBASIC 5.21, common values are file numbers or omitted for console."

However, MBASIC 5.21 WIDTH syntax is typically 'WIDTH [device$,] width' where device is a string like "SCRN:" or "LPT1:", not a numeric file number. The parameter order in the docstring (width first, device second) also differs from typical MBASIC syntax (device first, width second).

---
---

#### code_vs_comment

**Description:** parse_data() docstring says 'Line numbers (e.g., DATA 100 200) are treated as part of unquoted strings' but the code has a TokenType.LINE_NUMBER case that converts to string, suggesting line numbers might be tokenized separately rather than as identifiers

**Affected files:**
- `src/parser.py`

**Details:**
Docstring: "Unquoted strings extend until comma, colon, end of line, or unrecognized token.
Line numbers (e.g., DATA 100 200) are treated as part of unquoted strings."

Code has:
```python
elif tok.type == TokenType.LINE_NUMBER:
    string_parts.append(str(tok.value))
    self.advance()
```

This suggests LINE_NUMBER tokens exist and are handled specially. If line numbers in DATA statements are truly 'part of unquoted strings', they should be tokenized as identifiers or numbers, not as LINE_NUMBER tokens. The comment may be describing intended behavior that differs from implementation.

---
---

#### code_vs_comment

**Description:** PC class docstring describes stmt_offset as '0-based index' but also calls it an 'offset' which could be confusing. The explanation clarifies it's a list index, but the parameter name 'stmt_offset' suggests byte offset semantics.

**Affected files:**
- `src/pc.py`

**Details:**
Docstring says: 'The stmt_offset is a 0-based index into the statements list for a line.'
Then: 'Note: Throughout the codebase, stmt_offset is consistently used as a list index (0, 1, 2, ...) not an offset in bytes. The parameter name uses "offset" for historical/semantic reasons (it offsets from the start of the line's statement list).'

The note acknowledges the naming is potentially misleading but justifies it as 'historical/semantic'. This could cause confusion for new developers.

---
---

#### code_vs_comment

**Description:** apply_keyword_case_policy() docstring requires lowercase input but doesn't validate it. The function silently accepts any case and may produce incorrect results if given non-lowercase input.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring: 'Args:
    keyword: The keyword to transform (must be normalized lowercase)'

Note in docstring: 'Note: This function requires lowercase input to ensure consistent behavior with emit_keyword(). The first_wins policy uses lowercase for lookup; other policies apply transformations based on the lowercase input.'

However, the function implementation does not validate that input is lowercase. It calls keyword.lower() in some branches but not others, and doesn't raise an error if given uppercase input. This could lead to bugs if callers don't follow the contract.

---
---

#### code_vs_comment

**Description:** emit_keyword() docstring requires lowercase input but serialize_rem_statement() converts to lowercase before calling it. This suggests the requirement is not enforced at the API boundary.

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword() docstring: 'Args:
    keyword: The keyword to emit (must be normalized lowercase by caller, e.g., "print", "for")'

Note: 'Note: This function requires lowercase input because it looks up the display case from the keyword case manager using the normalized form.'

But serialize_rem_statement() does: 'result = self.emit_keyword(stmt.comment_type.lower(), stmt.column, "RemKeyword")'

With comment: 'Note: stmt.comment_type is stored in uppercase by the parser ("APOSTROPHE", "REM", or "REMARK"). We convert to lowercase before passing to emit_keyword() which requires lowercase input.'

This shows callers must remember to lowercase before calling, which is error-prone. The function should either validate/normalize input itself or the requirement should be removed.

---
---

#### code_vs_comment

**Description:** serialize_expression() has fallback code that uses ui_helpers.serialize_expression for unknown expression types, but this creates a circular dependency risk and inconsistent formatting.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Code in serialize_expression():
    'else:
        # Fallback: use pretty printing
        from src.ui.ui_helpers import serialize_expression
        return " " + serialize_expression(expr)'

Similar fallback in serialize_statement():
    'else:
        # Fallback: Use pretty printing from ui_helpers
        from src.ui.ui_helpers import serialize_statement
        return " " + serialize_statement(stmt)'

These fallbacks import from ui_helpers at runtime, which could create circular dependencies. Also, the fallback adds a leading space but ui_helpers functions may already include spacing, leading to inconsistent output. The comment says 'pretty printing' but doesn't explain why this is acceptable when the module's purpose is position preservation.

---
---

#### code_vs_comment_conflict

**Description:** Comment in check_array_allocation() describes implementation detail that may confuse readers about responsibility

**Affected files:**
- `src/resource_limits.py`

**Details:**
In check_array_allocation() method around line 165:

Comment says: "# Note: DIM A(N) creates N+1 elements (0 to N) in MBASIC 5.21
# We use this convention here to calculate the correct size for limit checking only.
# The actual array creation/initialization is handled by execute_dim() in interpreter.py."

The comment explains that the +1 calculation is for limit checking only and that actual array creation is elsewhere. However, this creates potential confusion because:
1. The method name 'check_array_allocation' suggests it only checks, not allocates
2. But there's also an 'allocate_array' method that does the actual tracking
3. The comment references execute_dim() in interpreter.py, creating a cross-module dependency in documentation

The code correctly calculates: total_elements *= (dim_size + 1) for each dimension, which is correct for MBASIC 5.21 behavior. The comment is trying to clarify this is just for size calculation, but it may be overly detailed for this module's scope.

---
---

#### code_vs_comment

**Description:** SettingsManager docstring claims file_settings dict is 'partially implemented' but it is fully implemented for runtime manipulation

**Affected files:**
- `src/settings.py`

**Details:**
Docstring says: 'File-level settings infrastructure is partially implemented (file_settings dict, FILE scope support in get/set/reset methods for runtime manipulation), but persistence is not implemented'

Code shows:
- file_settings dict exists and is initialized
- get() method checks file_settings first in precedence
- set() method supports SettingScope.FILE and writes to file_settings
- reset_to_defaults() supports SettingScope.FILE

The infrastructure is fully implemented for runtime use. Only persistence (load/save) is not implemented, which is intentional design for future use.

---
---

#### code_vs_comment

**Description:** load() docstring describes format handling but implementation doesn't match description

**Affected files:**
- `src/settings.py`

**Details:**
Docstring says: 'Format handling: Settings are stored on disk in flattened format (e.g., {\'editor.auto_number\': True}) but this method loads them as-is without unflattening. Internal representation is flexible: _get_from_dict() handles both flat keys like \'editor.auto_number\' and nested dicts like {\'editor\': {\'auto_number\': True}}. Loaded settings remain flat; settings modified via set() become nested; both work.'

But the code simply does:
self.global_settings = self.backend.load_global()
self.project_settings = self.backend.load_project()

The backend (FileSettingsBackend) loads from JSON which has format {'version': '1.0', 'settings': {...}} and returns data.get('settings', {}). The settings dict inside is already flattened on disk. The docstring's claim about 'flexible internal representation' is accurate for _get_from_dict(), but the description of load() behavior is confusing and doesn't clearly explain that flattened format is preserved.

---
---

#### code_vs_comment

**Description:** create_settings_backend() docstring claims 'silently falls back' but code prints warnings

**Affected files:**
- `src/settings_backend.py`

**Details:**
Docstring says:
'Note: If NICEGUI_REDIS_URL is set but session_id is None, silently falls back to FileSettingsBackend. If Redis connection fails, also falls back to FileSettingsBackend with warning.'

But code shows:
except ImportError:
    print('Warning: redis package not installed, falling back to file backend')
except Exception as e:
    print(f'Warning: Could not connect to Redis: {e}, falling back to file backend')

The first case (session_id is None) is indeed silent, but the docstring says 'silently falls back' for both cases, which is incorrect. The Redis connection failure case prints a warning.

---
---

#### code_vs_comment

**Description:** Token dataclass docstring describes convention but doesn't enforce it, creating potential confusion

**Affected files:**
- `src/tokens.py`

**Details:**
Docstring says:
'Note: By convention, these fields are used for different token types:
- original_case: For IDENTIFIER tokens (user variables) - preserves what user typed
- original_case_keyword: For keyword tokens - stores policy-determined display case

The dataclass does not enforce this convention (both fields can technically be set on the same token) to allow implementation flexibility. However, the lexer/parser follow this convention and only populate the appropriate field for each token type.'

This is a design choice that could lead to bugs if code doesn't follow the convention. The comment acknowledges this but doesn't explain why enforcement wasn't added (e.g., via validation or separate token subclasses). This creates ambiguity about whether violating the convention is acceptable.

---
---

#### code_vs_comment

**Description:** RedisSettingsBackend load_project() and save_project() docstrings say 'no-op' but load_project returns empty dict

**Affected files:**
- `src/settings_backend.py`

**Details:**
load_project() docstring says:
'Load project settings (returns empty in Redis mode). In Redis mode, all settings are session-scoped, not project-scoped.'

save_project() docstring says:
'Save project settings (no-op in Redis mode). In Redis mode, all settings are session-scoped, not project-scoped.'

load_project() returns {} (empty dict), which is not a no-op - it's a valid return value. save_project() is a true no-op (pass statement). The docstrings should be consistent: either both are 'no-op' (ignoring return value semantics) or load_project should say 'returns empty dict' and save_project should say 'no-op'.

---
---

#### Code vs Comment conflict

**Description:** The _execute_single_step() method's docstring claims it executes 'one statement' with statement-level granularity, but then admits this depends on the interpreter's implementation and may actually behave as line-level stepping.

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

This contradicts the confident claim in cmd_step() that it 'implements statement-level stepping similar to the curses UI'.

---
---

#### code_vs_comment

**Description:** Comment claims editor_lines stores execution state and is synced from editor, but code shows editor_lines is never actually populated or synced from editor.lines

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~150 says:
# Note: self.editor_lines stores execution state (lines loaded from file for RUN)
# self.editor.lines (in ProgramEditorWidget) stores the actual editing state
# These serve different purposes and are synchronized as needed

However, editor_lines is initialized as empty dict (line ~151: self.editor_lines = {}) and is never populated from editor.lines anywhere in the visible code. The _sync_program_to_editor() method is referenced but not shown. The _save_editor_to_program() method syncs FROM editor TO program manager, not to editor_lines.

---
---

#### code_vs_comment

**Description:** Comment says immediate mode status is disabled during execution, but _update_immediate_status() is never called during execution ticks

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Multiple comments say:
'(Immediate mode status remains disabled - execution will show output in output window)' (line ~933)
'(Immediate mode status remains disabled during execution - output shows in output window)' (lines ~1000, ~1082)

But in the execution flow (_debug_step, _debug_step_line, _debug_continue), _update_immediate_status() is only called AFTER execution completes/errors/pauses, not during. The comments suggest status is actively managed during execution, but code shows it's only updated at state transitions.

---
---

#### code_internal_inconsistency

**Description:** Inconsistent handling of immediate_io lifecycle between __init__ and start() methods

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In __init__ (line ~186):
immediate_io = OutputCapturingIOHandler()
self.interpreter = Interpreter(self.runtime, immediate_io, limits=create_unlimited_limits())

Then in __init__ (line ~197):
immediate_io = OutputCapturingIOHandler()  # Creates NEW instance, shadows previous
self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)

Then in start() (line ~234):
immediate_io = OutputCapturingIOHandler()  # Creates ANOTHER new instance
self.immediate_executor = ImmediateExecutor(self.runtime, self.interpreter, immediate_io)

This means:
1. Interpreter is created with one immediate_io instance
2. ImmediateExecutor is created with a different immediate_io instance
3. In start(), ImmediateExecutor is recreated with yet another immediate_io instance
4. The Interpreter still has the original immediate_io from __init__, which is never used again

This creates orphaned IO handlers and potential confusion about which IO handler is active.

---
---

#### code_vs_comment

**Description:** Inconsistent handling of runtime parameter in cmd_delete and cmd_renum

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In cmd_delete:
deleted = delete_lines_from_program(self.program, args, runtime=None)

In cmd_renum:
old_lines, line_map = renum_program(
    self.program,
    args,
    self.interpreter.interactive_mode._renum_statement,
    runtime=None
)

Both pass runtime=None, then call self._sync_program_to_runtime() afterwards. The comments say 'Updates self.program immediately (source of truth), then syncs to runtime.'

However, this pattern suggests the helper functions might expect a runtime parameter but it's being explicitly set to None. This could indicate:
1. The helpers were refactored to not need runtime
2. The curses UI is using them incorrectly
3. There's a missing sync step in the helpers

---
---

#### Code duplication warning

**Description:** Path normalization logic duplicated between _follow_link() and _open_link_in_new_window() with warning comments

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
_follow_link() lines 244-248:
Note: Path normalization logic is duplicated in _open_link_in_new_window().
Both methods use similar approach: resolve relative paths, normalize to help_root,
handle path separators. If modification needed, update both methods consistently.

_open_link_in_new_window() lines 625-628:
Note: Path normalization logic is duplicated from _follow_link().
Both methods resolve paths relative to help_root with similar logic.
If modification needed, update both methods consistently.

Both methods implement similar path resolution logic (lines 250-276 and 630-651) with explicit warnings about keeping them synchronized.

---
---

#### code_vs_comment

**Description:** Comment states immediate_history and immediate_status are 'always None' but code explicitly sets them to None with defensive programming justification

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line 143: Comment says 'Note: immediate_history and immediate_status are always None in Tk UI (see lines 293-297)'
Lines 293-297: Code sets these to None with comment 'These attributes are not currently used but are set to None for defensive programming in case future code tries to access them (will get None instead of AttributeError)'
Conflict: The line 143 comment implies these should never exist or be used, while lines 293-297 suggest they might be accessed by future code.

---
---

#### code_vs_comment_conflict

**Description:** Comment claims formatting may occur elsewhere, but code explicitly preserves exact text without formatting

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _refresh_editor method:
Comment says: "(Note: 'formatting may occur elsewhere' refers to the Variables and Stack windows, which DO format data for display - not the editor/program text itself)"

But the comment appears in a context where it's explaining that NO formatting is applied to preserve MBASIC compatibility. The parenthetical note seems to be defending against a misunderstanding, but it's confusing because it suggests formatting happens somewhere when the whole point is that it doesn't happen to program text.

---
---

#### code_vs_comment_conflict

**Description:** Comment about when _validate_editor_syntax is called doesn't match actual call sites

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax method around line 1850:
Comment: "# Note: This method is called:\n# - With 100ms delay after cursor movement/clicks (to avoid excessive validation during rapid editing)\n# - Immediately when focus leaves editor (to ensure validation before switching windows)"

But looking at actual call sites:
- _on_cursor_move: calls with 100ms delay (matches comment)
- _on_mouse_click: calls with 100ms delay (matches comment)
- _on_focus_out: calls immediately with NO delay (matches comment)
- _save_editor_to_program: calls immediately (NOT mentioned in comment)

The comment is incomplete - it doesn't mention the call from _save_editor_to_program.

---
---

#### code_vs_comment_conflict

**Description:** Comment about clearing yellow highlight contradicts when highlight is actually restored

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_mouse_click method around line 1920:
Comment: "# Clear yellow statement highlight when clicking (allows text selection to be visible).\n# The highlight is restored when execution resumes or when stepping to the next statement."

The comment claims the highlight is restored 'when execution resumes or when stepping', but there's no code visible in this file that shows where/how this restoration happens. The comment makes a promise about behavior that isn't implemented in the visible code, suggesting either:
1. The restoration logic is elsewhere (should be referenced)
2. The restoration doesn't actually happen as described
3. The comment is outdated

---
---

#### code_vs_comment

**Description:** Comment claims immediate mode doesn't echo commands, but this contradicts typical BASIC behavior documentation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method:
Comment: "Execute without echoing (GUI design choice that deviates from typical BASIC behavior: command is visible in entry field, and 'Ok' prompt is unnecessary in GUI context - only results are shown. Traditional BASIC echoes to output.)"

This comment acknowledges deviation from documented BASIC behavior but doesn't clarify if this is intentional design or a bug.

---
---

#### code_vs_comment

**Description:** Dead code documented but never called

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
_setup_immediate_context_menu() docstring states: "DEAD CODE: This method is never called because immediate_history is always None in the Tk UI (see __init__). Retained for potential future use if immediate mode gets its own output widget. Related dead code: _copy_immediate_selection() and _select_all_immediate()."

Three methods (_setup_immediate_context_menu, _copy_immediate_selection, _select_all_immediate) are documented as dead code but remain in the codebase. This creates maintenance burden and confusion.

---
---

#### code_vs_comment

**Description:** TkIOHandler docstring describes input strategy but implementation details may not match all claims

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
TkIOHandler class docstring states:
"Input strategy rationale:
- INPUT statement: Uses inline input field when backend available (allowing the user to see program output context while typing input), otherwise uses modal dialog as fallback. This is availability-based, not a UI preference.
- LINE INPUT statement: Always uses modal dialog for consistent UX."

However, the input() method shows fallback logic, while input_line() always uses modal dialog. The docstring claims this is 'availability-based' for INPUT but 'intentional' for LINE INPUT, which may confuse readers about the design intent.

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

**Description:** The class docstring states 'After fixing error, ● becomes visible (automatically handled by set_error() method which checks has_breakpoint flag when clearing errors)', but examining set_error() shows it updates status based on has_breakpoint without any special 'checking' logic - it's just a simple if/elif/else priority check.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring: 'After fixing error, ● becomes visible (automatically handled by set_error() method which checks has_breakpoint flag when clearing errors)'

set_error() implementation:
'# Update status symbol (error takes priority)
if metadata['has_error']:
    metadata['status'] = '?'
elif metadata['has_breakpoint']:
    metadata['status'] = '●'
else:
    metadata['status'] = ' '

The docstring makes it sound like there's special logic for 'checking has_breakpoint flag when clearing errors', but it's just the standard priority logic that runs every time set_error() is called. The phrasing is misleading.

---
---

#### code_vs_comment

**Description:** Docstring for VariablesDialog.__init__ says 'matches Tk UI defaults' but references specific file that may not match

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~127-128:
# Sort state (matches Tk UI defaults: see sort_mode and sort_reverse in src/ui/tk_ui.py)
self.sort_mode = 'accessed'  # Current sort mode
self.sort_reverse = True  # Sort direction

This references tk_ui.py for verification, but without seeing that file, cannot confirm if these defaults actually match. The comment creates a dependency that may become outdated if tk_ui.py changes.

---
---

#### documentation_inconsistency

**Description:** LOF function missing from index.md categorization but has its own documentation file

**Affected files:**
- `docs/help/common/language/functions/index.md`
- `docs/help/common/language/functions/lof.md`

**Details:**
The index.md file lists LOF in the alphabetical quick reference at the bottom, but does not include it in the 'File I/O Functions' category section at the top. LOF is documented in lof.md and should be listed alongside EOF, INPUT$, LOC, LPOS, and POS in the File I/O Functions category.

---
---

#### documentation_inconsistency

**Description:** Broken or inconsistent internal link structure

**Affected files:**
- `docs/help/index.md`
- `docs/help/common/ui/cli/index.md`

**Details:**
Main help index references 'UI-Specific Help' with links like '[CLI (Command Line)](ui/cli/index.md)' but the actual file path shown in the provided docs is 'docs/help/common/ui/cli/index.md'. The link path 'ui/cli/index.md' is relative and may not resolve correctly depending on where the help index is located. This suggests either the file structure doesn't match the documentation or the links need to be updated.

---
---

#### documentation_inconsistency

**Description:** Debugging features availability inconsistency between MBASIC features overview and CLI debugging documentation

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
features.md states: 'Breakpoints - Set/clear breakpoints (available in all UIs; access method varies)' and 'Step execution - Execute one line at a time (available in all UIs; access method varies)'

However, cli/debugging.md documents STEP INTO/OVER commands but then states in Limitations: 'STEP INTO/OVER not yet implemented (use STEP)'

This creates confusion about what's actually available in CLI mode.

---
---

#### documentation_inconsistency

**Description:** Variable viewing method inconsistency

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
features.md states: 'Variable viewing - Monitor variables (available in all UIs; access method varies)'

cli/debugging.md under 'Debug Mode' states: 'Examine variables with PRINT' and under 'Limitations': 'Variable inspection uses PRINT statement (no dedicated inspection command)'

While not contradictory, features.md implies a dedicated variable viewing feature exists in all UIs, but CLI documentation clarifies it's just using PRINT. This could mislead users expecting a dedicated variable viewer in CLI mode.

---
---

#### documentation_inconsistency

**Description:** STEP and STACK commands not listed in features

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
cli/debugging.md documents STEP and STACK commands:
- 'STEP [n] - Execute n statements (default: 1)'
- 'STACK - Show full call stack'

features.md under 'Program Control' -> 'Direct Commands' does not list STEP or STACK.

These are important debugging commands that should be in the feature list.

---
---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for Execution Stack

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
docs/help/ui/curses/quick-reference.md under 'Global Commands' states: '**Menu only** | Toggle execution stack window'

But docs/help/ui/curses/feature-reference.md under 'Variable Inspection > Execution Stack' provides detailed access methods:
'**Access methods:**
- Via menu: Ctrl+U → Debug → Execution Stack
- Via command: Type `STACK` in immediate mode (same as CLI)'

And adds: 'Note: There is no dedicated keyboard shortcut to avoid conflicts with editor typing.'

The 'Menu only' designation is consistent, but the feature-reference provides much more detail about access methods that should be in the quick-reference.

---
---

#### documentation_inconsistency

**Description:** Inconsistent implementation status for breakpoint features

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/features.md`

**Details:**
debugging.md states:
- Currently Implemented: Basic breakpoint management (via Run menu)
- Note: Advanced features like clicking line numbers to set breakpoints and a dedicated breakpoint panel are planned for future releases but not yet implemented.

But features.md Breakpoints section states:
- Currently Implemented:
  - Line breakpoints (toggle via Run menu)
  - Clear all breakpoints
  - Visual indicators in editor
- Management:
  - Toggle via Run menu → Toggle Breakpoint

The note about {{kbd:toggle_breakpoint:web}} being 'implemented but currently available via menu only (not yet bound to keyboard)' suggests the feature exists but the shortcut doesn't, which is different from debugging.md's description.

---
---

#### documentation_inconsistency

**Description:** Conflicting information about Step/Continue/Stop keyboard shortcuts in Tk UI

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states: 'Note: Step, Continue, and Stop are available via toolbar buttons or the Run menu (no keyboard shortcuts).'

TK_UI_QUICK_START.md Essential Keyboard Shortcuts table states: '**Note:** Step, Continue, and Stop are available via toolbar buttons or the Run menu (no keyboard shortcuts).'

However, UI_FEATURE_COMPARISON.md Debugging Shortcuts table shows:
- Step: 'Menu/Toolbar' for Tk
- Continue: 'Menu/Toolbar' for Tk

This is consistent. But the comparison table also shows CLI has {{kbd:step:cli}} and {{kbd:continue:cli}}, and Curses has {{kbd:step:curses}} and {{kbd:continue:curses}}, suggesting these actions DO have keyboard shortcuts in other UIs, making the Tk limitation notable but consistently documented.

---
---

## 🟢 Low Severity

#### Code vs Comment conflict

**Description:** InputStatementNode.suppress_question field is documented as parsed but not implemented

**Affected files:**
- `src/ast_nodes.py`

**Details:**
InputStatementNode docstring lines 318-332:
'Note: The suppress_question field is parsed by the parser when INPUT; (semicolon
immediately after INPUT) is used, but it is NOT currently checked by the interpreter.
Current behavior: "?" is always displayed (either "? " alone or "prompt? ").

Expected behavior (when suppress_question is implemented):
- suppress_question=False (default): Adds "?" after prompt
  Examples: INPUT var → "? ", INPUT "Name", var → "Name? "
- suppress_question=True: No "?" added (for INPUT; syntax)
  Examples: INPUT; var → "" (no prompt), INPUT "prompt"; var → "prompt" (no "?")'

The field exists in the dataclass (line 339: 'suppress_question: bool = False') but the comment explicitly states it's not used by the interpreter. This is a known incomplete feature, not a bug.

---
---

#### Code vs Comment conflict

**Description:** keyword_token fields documented as 'legacy, not currently used' but still present in code

**Affected files:**
- `src/ast_nodes.py`

**Details:**
PrintStatementNode line 289: 'keyword_token: Optional[Token] = None  # Token for PRINT keyword (legacy, not currently used)'
IfStatementNode lines 368-370: 'keyword_token: Optional[Token] = None  # Token for IF keyword (legacy, not currently used)
then_token: Optional[Token] = None     # Token for THEN keyword (legacy, not currently used)
else_token: Optional[Token] = None     # Token for ELSE keyword (legacy, not currently used)'
ForStatementNode lines 387-389: 'keyword_token: Optional[Token] = None  # Token for FOR keyword (legacy, not currently used)
to_token: Optional[Token] = None       # Token for TO keyword (legacy, not currently used)
step_token: Optional[Token] = None     # Token for STEP keyword (legacy, not currently used)'

Also documented in PrintStatementNode docstring lines 276-279:
'Note: keyword_token fields are present in some statement nodes (PRINT, IF, FOR) but not
others. These were intended for case-preserving keyword regeneration but are not currently
used by position_serializer, which handles keyword case through case_keepy_string() instead.
The fields remain for potential future use and backward compatibility.'

These fields exist but are explicitly marked as unused. This is intentional technical debt for backward compatibility.

---
---

#### Code vs Comment conflict

**Description:** CallStatementNode.arguments field documented as unused but still present

**Affected files:**
- `src/ast_nodes.py`

**Details:**
CallStatementNode docstring lines 817-826:
'Implementation Note: The 'arguments' field is currently unused (always empty list).
It exists for potential future support of BASIC dialects that allow CALL with
arguments (e.g., CALL ROUTINE(args)). Standard MBASIC 5.21 only accepts a single
address expression in the 'target' field. Code traversing the AST can safely ignore
the 'arguments' field for MBASIC 5.21 programs.'

CallStatementNode line 829: 'arguments: List['ExpressionNode']  # Reserved for future (parser always sets to empty list)'

The field exists but is documented as always empty and unused. This is intentional forward compatibility design.

---
---

#### Documentation inconsistency

**Description:** RemarkStatementNode.comment_type default value documentation

**Affected files:**
- `src/ast_nodes.py`

**Details:**
RemarkStatementNode docstring lines 752-756:
'Note: comment_type preserves the original comment syntax used in source code.
The parser sets this to "REM", "REMARK", or "APOSTROPHE" based on input.
Default value "REM" is used only when creating nodes programmatically.'

RemarkStatementNode line 758: 'comment_type: str = "REM"'

The docstring says the default is used 'only when creating nodes programmatically', implying the parser always sets it explicitly. However, if the parser fails to set it, the default would still apply. This is a minor documentation imprecision about when defaults are used.

---
---

#### code_vs_comment

**Description:** INPUT method docstring describes BASIC syntax with # prefix but notes it's stripped by parser, creating potential confusion

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring states:
"BASIC syntax:
    INPUT$(n) - read n characters from keyboard
    INPUT$(n, #filenum) - read n characters from file

Python call syntax (from interpreter):
    INPUT(n) - read n characters from keyboard
    INPUT(n, filenum) - read n characters from file

Note: The # prefix in BASIC syntax is stripped by the parser before calling this method."

This is informative but the note about parser stripping # references behavior in another component (parser) that isn't provided, making it unverifiable.

---
---

#### code_vs_comment

**Description:** Comment in EOF describes binary mode read behavior but doesn't handle potential exceptions

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment states: "Binary mode files ('rb'): read(1) returns bytes object
next_byte[0] accesses the first byte value as integer (0-255)"

Code:
next_byte = file_handle.read(1)
if not next_byte:
    # Physical EOF
elif next_byte[0] == 26:  # ^Z (ASCII 26)

If file_handle is not actually in binary mode, next_byte[0] would fail with TypeError. The code doesn't validate the file mode or handle this potential error, but the comment assumes binary mode is guaranteed.

---
---

#### Code vs Documentation inconsistency

**Description:** Docstring example shows formatted_msg usage but function doesn't always return formatted message

**Affected files:**
- `src/debug_logger.py`

**Details:**
Module docstring shows:
"if is_debug_mode():
    formatted_msg = debug_log_error('Error details', exception, context_info)
    # formatted_msg can be displayed in UI"

But debug_log_error() returns different formats depending on debug mode:
- Debug mode OFF: returns simple message or 'message: exception'
- Debug mode ON: returns 'message: exception' (same as OFF)

The function always returns a UI-suitable message, but the docstring implies the formatted_msg is only useful in debug mode. The actual behavior is that debug mode controls stderr output, not the return value format.

---
---

#### code_vs_comment

**Description:** ImmediateExecutor.execute() docstring mentions state names like 'idle', 'paused', 'at_breakpoint', 'done', 'error', 'waiting_for_input', 'running' but explicitly states these are NOT actual enum values, just documentation names

**Affected files:**
- `src/immediate_executor.py`

**Details:**
Docstring says: "State names used in documentation (not actual enum values):
- 'idle' - No program loaded (halted=True)
- 'paused' - User hit Ctrl+Q/stop (halted=True)
...
Note: The actual implementation checks boolean flags (halted, error_info, input_prompt),
not string state values."

This is internally consistent but could be confusing. The docstring correctly clarifies that these are documentation names only, not actual implementation values. However, using state names in documentation that don't exist in code could lead to confusion.

---
---

#### code_vs_documentation

**Description:** Module docstring mentions Python 3.9+ requirement for type hints but doesn't specify what happens on earlier versions

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Docstring says:
"Implementation note: Uses standard Python type hints (e.g., tuple[str, bool])
which require Python 3.9+. For earlier Python versions, use Tuple[str, bool] from typing."

This is a note to developers but doesn't indicate if the code will fail on Python 3.8 or if it's just a style recommendation. The code uses tuple[str, bool] which will cause a TypeError on Python 3.8 and earlier.

---
---

#### code_vs_comment

**Description:** Security comment about user_id validation is repeated in both __init__ docstring and class docstring with slightly different wording

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
Class docstring says:
"- Per-user isolation via user_id keys in class-level storage
  IMPORTANT: Caller must ensure user_id is securely generated/validated
  to prevent cross-user access (e.g., use session IDs, not user-provided values)"

__init__ docstring says:
"Args:
    user_id: Unique identifier for this user/session
            SECURITY: Must be securely generated/validated (e.g., session IDs)
            to prevent cross-user access. Do NOT use user-provided values."

The repetition is good for emphasis but the wording differs slightly ('Caller must ensure' vs 'Must be'). Minor consistency issue.

---
---

#### code_vs_comment

**Description:** Docstring claims EDIT subcommands are 'implemented subset' but doesn't specify which are missing

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring at line ~714 states:
'Edit mode subcommands (implemented subset of MBASIC EDIT):'

Then lists commands including 'Note: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K) are not yet implemented.'

This is accurate, but the phrase 'implemented subset' in the header is vague. The note clarifies what's missing, so this is minor.

---
---

#### code_vs_comment

**Description:** Comment says 'Bare except is acceptable' but doesn't explain why all exceptions should be caught

**Affected files:**
- `src/interactive.py`

**Details:**
In _read_char() at line ~825:
'# Fallback for non-TTY/piped input or any terminal errors.
# Bare except is acceptable here because we're degrading gracefully to basic read()
# on any error (AttributeError, termios.error, ImportError on Windows, etc.)'

While the comment justifies bare except, catching ALL exceptions (including SystemExit, KeyboardInterrupt) could mask serious issues. The comment lists specific exceptions but code catches everything.

---
---

#### documentation_inconsistency

**Description:** HELP command shows 'BREAK line' but doesn't document BREAK without arguments

**Affected files:**
- `src/interactive.py`

**Details:**
The HELP output shows:
  BREAK line         - Set breakpoint at line

But doesn't mention that BREAK can be called without arguments (which is a common pattern in BASIC debuggers to list breakpoints or clear all breakpoints).

---
---

#### code_vs_comment_conflict

**Description:** Comment about sanitize_and_clear_parity mentions 'clear parity bits' but this may be outdated terminology

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in AUTO mode: '# Sanitize input: clear parity bits and filter control characters'

The mention of 'parity bits' suggests legacy serial communication concerns that may not be relevant to modern Python input() usage. The function name and comment may be outdated.

---
---

#### code_vs_comment

**Description:** execute_for docstring mentions string variables cause Type mismatch but doesn't explain this happens in set_variable, not in FOR itself

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 1046-1055 states:
"The loop variable typically has numeric type suffixes (%, !, #). The variable
type determines how values are stored. String variables ($) are syntactically
valid (parser accepts them) but cause a 'Type mismatch' error at runtime when
set_variable() attempts to assign numeric loop values to a string variable."

This is accurate and explains the behavior correctly. The comment properly attributes the error to set_variable() call. No inconsistency found upon closer inspection.

---
---

#### code_vs_comment

**Description:** Comment about WEND timing is verbose but accurate

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1063 states:
"# Pop the loop from the stack (after setting npc above, before WHILE re-executes).
# Timing: We pop NOW so the stack is clean before WHILE condition re-evaluation.
# The WHILE will re-push if its condition is still true, or skip the loop body
# if false. This ensures clean stack state and proper error handling if the
# WHILE condition evaluation fails (loop already popped, won't corrupt stack)."

The code does:
"self.runtime.npc = PC(loop_info['while_line'], loop_info['while_stmt'])
self.limits.pop_while_loop()
self.runtime.pop_while_loop()"

This is consistent - the comment accurately describes the timing. However, the verbosity suggests this was a bug-prone area. Not an inconsistency, just noting the defensive documentation style.

---
---

#### code_vs_comment

**Description:** Comment about latin-1 encoding mentions CP/M code pages but doesn't explain the mismatch implications

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1540 states:
"Encoding:
Uses latin-1 (ISO-8859-1) to preserve byte values 128-255 unchanged.
CP/M and MBASIC used 8-bit characters; latin-1 maps bytes 0-255 to
Unicode U+0000-U+00FF, allowing round-trip byte preservation.
Note: CP/M systems often used code pages like CP437 or CP850 for characters
128-255, which do NOT match latin-1. Latin-1 preserves the BYTE VALUES but
not necessarily the CHARACTER MEANING for non-ASCII CP/M text. Conversion
may be needed for accurate display of non-English CP/M files."

This is accurate but could be clearer about when this matters. The comment warns about character meaning but doesn't explain that this only affects display/interpretation, not file I/O correctness. Not a bug, but could be clearer.

---
---

#### code_vs_comment

**Description:** Comment about debugger_set parameter usage is inconsistent between two locations

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_functioncall(), comment states: 'Note: get_variable_for_debugger() and debugger_set=True are used to avoid triggering variable access tracking.'

However, the actual restore code uses: 'self.runtime.set_variable(base_name, type_suffix, saved_value, debugger_set=True)'

But the save code uses: 'self.runtime.get_variable_for_debugger(param.name, param.type_suffix)' without any debugger_set parameter (get_variable_for_debugger is a different method).

The comment implies both save and restore avoid tracking, but they use different mechanisms. This could be clearer.

---
---

#### code_vs_comment

**Description:** execute_midassignment() comment about start_idx bounds check is verbose and could be simplified

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment states: 'Note: start_idx == len(current_value) is considered out of bounds (can't start replacement past end)'

The code check is: 'if start_idx < 0 or start_idx >= len(current_value)'

The comment is correct but overly explanatory. The >= check naturally handles the case where start_idx equals length. This is more of a style issue than an inconsistency.

---
---

#### Code vs Comment conflict

**Description:** Backward compatibility comment for print() method is misleading about the reason for renaming

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment states: 'This method was renamed from print() to output() to avoid conflicts with Python's built-in print function.'

However, the base class IOHandler defines output() as the abstract method, not print(). The real reason is interface compliance, not avoiding conflicts with built-in print().

---
---

#### Code vs Comment conflict

**Description:** get_char() backward compatibility comment incorrectly describes original behavior

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment states: 'The original get_char() implementation was non-blocking, so this preserves that behavior for backward compatibility.'

However, the current input_char() implementation always returns empty string immediately regardless of blocking parameter, which is documented as 'not supported'. The comment implies get_char() had working non-blocking behavior, but the code shows it never worked in web UI.

---
---

#### code_vs_comment

**Description:** Comment in at_end_of_line() warns about bugs when using it in statement parsing, but the actual implementation is correct

**Affected files:**
- `src/parser.py`

**Details:**
at_end_of_line() comment says:
"Note: Most statement parsing should use at_end_of_statement(), not this method.
Using at_end_of_line() in statement parsing can cause bugs where comments are
parsed as part of the statement instead of ending it."

The implementation is:
def at_end_of_line(self) -> bool:
    if self.at_end_of_tokens():
        return True
    token = self.current()
    return token.type in (TokenType.NEWLINE, TokenType.EOF)

The comment is correct that at_end_of_line() doesn't check for COLON or comments, but the warning seems overly cautious since the method is correctly implemented for its stated purpose.

---
---

#### code_vs_comment

**Description:** parse_resume() docstring states 'RESUME 0 also retries the error statement (interpreter treats 0 and None equivalently)' but the code stores the actual value 0, not None

**Affected files:**
- `src/parser.py`

**Details:**
Comment says: "Note: RESUME 0 means 'retry error statement' (interpreter treats 0 and None equivalently)
We store the actual value (0 or other line number) for the AST"

The comment claims 0 and None are treated equivalently by the interpreter, but the code explicitly stores 0 when parsed, not None. This creates ambiguity about whether line_number=0 and line_number=None should be treated identically downstream.

---
---

#### code_vs_comment

**Description:** parse_call() docstring claims MBASIC 5.21 primarily uses simple numeric address form, but then says 'this parser fully supports both forms for broader compatibility' without clarifying if extended syntax is actually valid MBASIC 5.21

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"MBASIC 5.21 syntax:
    CALL address           - Call machine code at numeric address

Extended syntax (for compatibility with other BASIC dialects):
    CALL ROUTINE(X,Y)      - Call with arguments

Note: MBASIC 5.21 primarily uses the simple numeric address form, but this
parser fully supports both forms for broader compatibility."

This is unclear whether CALL ROUTINE(X,Y) is valid MBASIC 5.21 syntax or an extension. The phrase 'for broader compatibility' suggests it's not standard MBASIC 5.21, but the implementation treats both equally.

---
---

#### code_vs_comment

**Description:** parse_common() docstring says 'Non-empty parentheses are an error (parser enforces empty parens only)' but the error message says 'subscripts not allowed' which is slightly different semantics

**Affected files:**
- `src/parser.py`

**Details:**
Docstring: "The empty parentheses () indicate an array variable (all elements shared).
This is just a marker - no subscripts are specified or stored. Non-empty
parentheses are an error (parser enforces empty parens only)."

Error message: "COMMON arrays must use empty parentheses () - subscripts not allowed"

The docstring says 'non-empty parentheses are an error' but the error message specifically says 'subscripts not allowed'. These are subtly different - the former suggests any content is invalid, the latter suggests specifically subscript expressions are invalid. This could matter if someone writes COMMON A( ) with spaces.

---
---

#### code_vs_comment

**Description:** apply_keyword_case_policy() has 'preserve' policy that returns keyword.capitalize() as fallback, but the comment says this 'shouldn't normally execute in correct usage'. This suggests dead code or incomplete implementation.

**Affected files:**
- `src/position_serializer.py`

**Details:**
Code for 'preserve' policy:
    'elif policy == "preserve":
        # The "preserve" policy is typically handled at a higher level (keywords passed with
        # original case preserved). If this function is called with "preserve" policy, we
        # return the keyword as-is if already properly cased, or capitalize as a safe default.
        # Note: This fallback shouldn't normally execute in correct usage.
        return keyword.capitalize()'

The comment admits this code path 'shouldn't normally execute', which suggests either:
1. The preserve policy is handled elsewhere and this is dead code
2. The implementation is incomplete
3. The function contract is unclear about when it should be called

The code doesn't actually check 'if already properly cased' - it just capitalizes unconditionally.

---
---

#### code_vs_comment_conflict

**Description:** estimate_size() method has inconsistent handling of var_type parameter

**Affected files:**
- `src/resource_limits.py`

**Details:**
The estimate_size() docstring says:
"Args:
    value: The actual value (number, string, array)
    var_type: TypeInfo (INTEGER, SINGLE, DOUBLE, STRING) or VarType enum"

The docstring mentions 'or VarType enum' but the code only handles TypeInfo comparisons:
- if var_type == TypeInfo.INTEGER:
- elif var_type == TypeInfo.SINGLE:
- elif var_type == TypeInfo.DOUBLE:
- elif var_type == TypeInfo.STRING:

There's no code path that handles VarType enum. Either the docstring is wrong (VarType is not actually supported) or the code is incomplete (should handle VarType enum). This needs clarification about what types are actually accepted.

---
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
---

#### code_vs_comment

**Description:** get() method docstring claims file_settings is 'not populated in normal usage' but doesn't explain what 'normal usage' means

**Affected files:**
- `src/settings.py`

**Details:**
Docstring says: 'Note: File-level settings (first in precedence) are not populated in normal usage. The file_settings dict can be set programmatically and is checked first, but no persistence layer exists (not saved/loaded) and no UI/command manages per-file settings. In practice, precedence is: project > global > definition default > provided default.'

This is accurate but vague. 'Normal usage' is undefined. The comment should clarify that file_settings is only populated by direct programmatic calls to set(key, value, SettingScope.FILE), which is not exposed through any CLI/UI commands.

---
---

#### code_vs_comment

**Description:** Module docstring claims 'both should use consistent settings' but doesn't explain how to ensure consistency

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
Docstring says:
'Note: Both systems read from the same settings.get("keywords.case_style") setting, so they should normally be configured with the same policy.'

This implies both SimpleKeywordCase and KeywordCaseManager read from settings, but SimpleKeywordCase.__init__() takes a policy parameter directly, not from settings. The caller must ensure consistency by reading settings and passing the same policy to both. The docstring should clarify this is the caller's responsibility.

---
---

#### code_vs_comment

**Description:** register_keyword() docstring says parameters are 'unused' but should clarify they're ignored

**Affected files:**
- `src/simple_keyword_case.py`

**Details:**
Docstring says:
'Maintains signature compatibility with KeywordCaseManager.register_keyword() which uses line_num and column for advanced policies (first_wins, preserve, error). SimpleKeywordCase only supports force-based policies, so these parameters are unused.'

The word 'unused' is ambiguous - it could mean they're not passed in, or they're passed but ignored. The docstring should say 'these parameters are ignored' or 'these parameters are accepted but not used' to be clearer.

---
---

#### code_vs_comment

**Description:** RedisSettingsBackend docstring says 'optionally initialized from default file-based settings' but implementation always initializes if not exists

**Affected files:**
- `src/settings_backend.py`

**Details:**
Docstring says:
'- Optionally initialized from default file-based settings (if provided and not already in Redis)'

But __init__ code shows:
if default_settings and not self._exists():
    self.save_global(default_settings)

This is not 'optional' - if default_settings is provided and Redis key doesn't exist, it always initializes. The word 'optionally' is misleading. It should say 'automatically initialized' or 'initialized if default_settings provided'.

---
---

#### Code vs Comment conflict

**Description:** get_additional_keybindings() docstring says 'Ctrl+A is overridden by MBASIC to trigger edit mode' but cli_keybindings.json shows Ctrl+A is for 'Edit line' which is the same thing. The comment makes it sound like a conflict when it's actually intentional design.

**Affected files:**
- `src/ui/cli.py`

**Details:**
get_additional_keybindings() docstring:
"# Standard readline/Emacs keybindings available when readline is loaded
# Note: Ctrl+A is overridden by MBASIC to trigger edit mode"

cli_keybindings.json:
"edit": {
  "keys": ["Ctrl+A"],
  "primary": "Ctrl+A",
  "description": "Edit line (last line or Ctrl+A followed by line number)"
}

The word 'overridden' suggests a conflict, but MBASIC's edit mode IS the intended behavior. The comment should say 'Ctrl+A is used by MBASIC for edit mode instead of readline's move-to-beginning-of-line'.

---
---

#### code_vs_comment

**Description:** Multiple comments state 'Don't update immediate status here' after errors, but _update_immediate_status() is called in some error paths

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
At line ~1165 (parse error path):
"# Don't update immediate status here - error is displayed in output
return False"

But at line ~1260 (runtime error path):
"self._update_output()
# Don't update immediate status here - error is displayed in output
self._update_immediate_status()"

And at line ~1275 (halted/paused path):
"self._update_output()
self.status_bar.set_text(f"Paused at line {state.current_line}...")
self._update_immediate_status()"

The comment says 'don't update' but code does call _update_immediate_status(). This is inconsistent.

---
---

#### code_vs_comment_conflict

**Description:** Comment about link pattern matching doesn't fully describe the regex

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
Comment at line ~227 states:
"Links are marked with [text] or [text](url) in the rendered output. This method finds ALL such patterns for display/navigation using regex r'\\[([^\\]]+)\\](?:\\([^)]+\\))?', which matches both formats."

The regex pattern shown in the comment has escaped backslashes (\\[) which is the Python string representation, but it would be clearer to show the actual regex pattern: r'\[([^\]]+)\](?:\([^)]+\))?' or describe it in plain English. The double-escaped version is confusing in documentation.

---
---

#### code_vs_comment_conflict

**Description:** Comment about QUIT_KEY and STACK_KEY being None/empty is not verifiable from provided code

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
Comments at lines ~37 and ~52 state:
"('Quit', 'quit'),  # QUIT_KEY is None (menu-only)"
"('Execution Stack', '_toggle_stack_window'),  # STACK_KEY is '' (menu-only)"

These comments reference QUIT_KEY and STACK_KEY constants that are not defined in the provided code files. The comments claim these keys are None or empty (menu-only), but without seeing the keybindings module or JSON config, we cannot verify this claim. If these keys are defined in keybindings.py or the JSON config, the comments may be incorrect.

---
---

#### Code duplication warning

**Description:** Table formatting may be duplicated in markdown_renderer.py

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
_format_table_row() method at line 655 has comment:
Note: This implementation may be duplicated in src/ui/markdown_renderer.py.
If both implementations exist and changes are needed to table formatting logic,
consider extracting to a shared utility module to maintain consistency.

Warns about potential duplication with another file not included in the analysis.

---
---

#### code_vs_comment

**Description:** Docstring describes 3-pane layout with specific weights (3:2:1) but implementation uses ttk.PanedWindow which doesn't use those exact weight values

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring lines 48-53: '3-pane vertical layout (weights: 3:2:1 = total 6 units):
      * Editor with line numbers (top, ~50% = 3/6 - weight=3)
      * Output pane (middle, ~33% = 2/6 - weight=2)
        - Contains INPUT row (shown/hidden dynamically for INPUT statements)
      * Immediate mode input line (bottom, ~17% = 1/6 - weight=1)'
Implementation lines 177-191: Uses ttk.PanedWindow with paned.add(editor_frame, weight=3), paned.add(output_frame, weight=2), paned.add(immediate_frame, weight=1)
Note: ttk.PanedWindow weights work differently than described - they control resize behavior, not initial proportions.

---
---

#### code_vs_comment

**Description:** Toolbar comment mentions features removed but doesn't explain why or when

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 476-481: '# Note: Toolbar has been simplified to show only essential execution controls.
        # Additional features are accessible via menus:
        # - List Program → Run > List Program
        # - New Program (clear) → File > New
        # - Clear Output → Run > Clear Output'
This comment suggests a refactoring occurred but provides no context about when or why these buttons were removed from the toolbar.

---
---

#### code_vs_comment_conflict

**Description:** Comment about OPTION BASE validation contradicts defensive else clause

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _edit_array_element method around line 1150:
Comment: "# OPTION BASE only allows 0 or 1 (validated by OPTION statement parser).\n# The else clause is defensive programming for unexpected values."

Code:
if array_base == 0:
    default_subscripts = ','.join(['0'] * len(dimensions))
elif array_base == 1:
    default_subscripts = ','.join(['1'] * len(dimensions))
else:
    # Defensive fallback for invalid array_base (should not occur)
    default_subscripts = ','.join(['0'] * len(dimensions))

The comment claims the else clause is for 'unexpected values' and 'should not occur', but if OPTION BASE truly only allows 0 or 1 and this is validated, the else clause is unreachable dead code. Either the validation isn't as strict as claimed, or the else clause is unnecessary.

---
---

#### code_vs_comment_conflict

**Description:** Comment about when blank line removal is called contradicts potential future usage

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines method around line 1950:
Comment: "Currently called only from _on_enter_key (after each Enter key press), not after pasting or other modifications."

This comment describes current behavior but uses 'Currently' which suggests it might change. However, the method has no parameters or design that would support being called from other contexts. If it's meant to be called from paste operations, the comment should explain why it isn't yet. If it's not meant to be called from paste, the word 'Currently' is misleading.

---
---

#### code_vs_comment

**Description:** Comment says 'Clear yellow statement highlight on any keypress when paused at breakpoint' but then explains it clears on 'ANY key (even arrows/function keys)' - this is redundant and could be simplified

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~1168:
# Clear yellow statement highlight on any keypress when paused at breakpoint
# Clears on ANY key (even arrows/function keys) because: 1) user interaction during
# debugging suggests intent to modify/inspect code, making highlight less relevant,
# and 2) prevents visual artifacts when text IS modified (highlight is tag-based and
# editing shifts character positions, causing highlight to drift or split incorrectly).

The phrase 'on any keypress' is immediately repeated as 'on ANY key' - redundant wording.

---
---

#### code_vs_comment

**Description:** clear_screen() docstring explains design decision that may not be documented elsewhere

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
clear_screen() docstring: "Clear screen - no-op for Tk UI. Design decision: GUI output is persistent for review. Users can manually clear output via Run > Clear Output menu if desired. CLS command is ignored to preserve output history during program execution."

This documents that CLS command is intentionally ignored, which is a significant deviation from BASIC behavior. This design decision should be documented in user-facing documentation, not just code comments.

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

**Description:** The _parse_line_number() inline comment references 'MBASIC 5.21' as requiring whitespace or end-of-line between line number and statement, but no other part of the file mentions this version number or specification, making it unclear if this is the actual target version for the entire project.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
_parse_line_number() comment: 'Note: MBASIC 5.21 requires whitespace OR end-of-line between line number and statement.'

This is the only reference to 'MBASIC 5.21' in the entire file. The module docstring says 'Custom Tkinter widgets for MBASIC Tk UI' but doesn't specify which version of MBASIC is being targeted.

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

#### code_inconsistency

**Description:** Inconsistent use of .props() vs .classes() for button styling

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Some buttons use:
ui.button(...).props('dense flat size=sm')

Others use:
ui.button(...).classes('bg-blue-500')

And some combine both:
ui.button(...).classes('bg-blue-500').props('no-caps')

While not necessarily wrong, the inconsistent patterns suggest lack of clear styling guidelines.

---
---

#### code_comment_conflict

**Description:** Comment says class is deprecated but it's still fully implemented with working code

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
The comment above WebHelpLauncher_DEPRECATED class says:
"# Legacy class kept for compatibility - new code should use direct web URL instead
# The help site is already built and served at http://localhost/mbasic_docs"

But the class contains a full implementation with methods like _build_help(), _start_help_server(), _is_server_running(), etc. If it's truly deprecated and the help is already served elsewhere, this code should either:
1. Be removed entirely
2. Raise deprecation warnings
3. Simply redirect to the new URL

Instead it has 100+ lines of functional server management code.

---
---

#### documentation_inconsistency

**Description:** Documentation uses template placeholders that were never replaced with actual content

**Affected files:**
- `docs/help/common/debugging.md`

**Details:**
The debugging.md file contains multiple instances of {{kbd:...}} placeholders:
- "{{kbd:step:curses}}"
- "{{kbd:continue:curses}}"
- "{{kbd:quit:curses}}"
- "{{kbd:toggle_stack:tk}}"
- "{{kbd:step_line:curses}}"

These appear to be template variables that should have been replaced with actual keyboard shortcuts during documentation generation, but were left as-is. This makes the documentation confusing as users see literal "{{kbd:step:curses}}" text instead of the actual key combination.

---
---

#### code_documentation_mismatch

**Description:** SessionState has auto_save fields but WebSettingsDialog doesn't expose them

**Affected files:**
- `src/ui/web/session_state.py`
- `src/ui/web/web_settings_dialog.py`

**Details:**
SessionState defines:
- auto_save_enabled: bool = True
- auto_save_interval: int = 30

These fields are documented as "Configuration" in the SessionState class.

However, WebSettingsDialog only exposes:
- editor.auto_number
- editor.auto_number_step
- limits.* (read-only)

The auto-save settings are not exposed in the settings dialog, despite being part of the session state. Either:
1. These should be added to the settings dialog
2. They should be removed from SessionState if not used
3. Documentation should explain why they're in SessionState but not configurable

---
---

#### code_documentation_mismatch

**Description:** Keybindings JSON defines shortcuts but documentation says to see UI-specific help

**Affected files:**
- `src/ui/web_keybindings.json`
- `docs/help/common/debugging.md`

**Details:**
web_keybindings.json defines specific keyboard shortcuts for the web UI:
- "run": ["Ctrl+R", "F5"]
- "stop": ["Esc"]
- "save": ["Ctrl+S"]
- "help": ["F1"]
- "toggle_breakpoint": ["F9"]
- "step": ["F10"]
- "continue": ["F5"]
- "toggle_variables": ["Ctrl+Alt+V"]

But debugging.md and editor-commands.md both say "See your UI-specific help for keyboard shortcuts" without actually documenting what those shortcuts are. The JSON file exists but isn't referenced in the documentation, and users are told to look elsewhere for information that could be documented directly.

---
---

#### documentation_inconsistency

**Description:** Cross-reference to utilities library that doesn't exist in provided files

**Affected files:**
- `docs/library/games/index.md`
- `docs/library/utilities/index.md`

**Details:**
docs/library/games/index.md contains a note under the Calendar game entry:
"**Note:** A simpler calendar utility is also available in the [Utilities Library](../utilities/index.md#calendar)"

However, docs/library/utilities/index.md was not provided in the documentation files list. This creates a broken reference if the utilities library documentation doesn't exist or doesn't have a calendar entry.

---
---

## Summary

- Total code behavior issues: 120
- High severity: 20
- Medium severity: 47
- Low severity: 53
