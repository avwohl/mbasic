# Code Behavior Issues - v20

Generated: 2025-11-10
Source: docs_inconsistencies_report-v20.md
Category: Code behavior changes needed (bugs, incorrect logic, missing features)

## Issues

#### Code vs Comment conflict

**Description:** InputStatementNode.suppress_question field is documented as parsed but not implemented in interpreter

**Affected files:**
- `src/ast_nodes.py`

**Details:**
InputStatementNode docstring states: 'Note: The suppress_question field is parsed by the parser when INPUT; (semicolon immediately after INPUT) is used, but it is NOT currently checked by the interpreter. Current behavior: "?" is always displayed (either "? " alone or "prompt? ").' This indicates a feature gap where the parser sets a field that the interpreter ignores, leading to incorrect behavior.

---

---

#### documentation_inconsistency

**Description:** Contradictory documentation about FileIO usage between module docstring and inline comments

**Affected files:**
- `src/editing/manager.py`

**Details:**
Module docstring (lines 3-42) states:
'Note: Web UI should use FileIO abstraction in interactive.py instead of this manager, as this module uses direct filesystem access which may not work in web environments.'

And later:
'Why ProgramManager has its own file I/O methods:
- Provides simpler API for local UI menu operations (File > Open/Save dialogs)
- Only used by local UIs (CLI, Curses, Tk) where filesystem access is safe'

But then contradicts itself:
'Note: ProgramManager.load_from_file() returns (success, errors) tuple where errors is a list of (line_number, error_message) tuples for direct UI error reporting, while FileIO.load_file() returns raw file text. These serve different purposes: ProgramManager integrates with the editor and provides error details, FileIO provides raw file content for the LOAD command to parse.'

This last note suggests FileIO.load_file() returns raw text that needs to be parsed, but earlier it says 'caller passes to ProgramManager'. The relationship between FileIO and ProgramManager for the LOAD command flow is unclear.

---

---

#### Code vs Documentation inconsistency

**Description:** SandboxedFileIO documentation claims list_files() is FULLY IMPLEMENTED but implementation has potential bugs

**Affected files:**
- `src/file_io.py`

**Details:**
Documentation states: "list_files(): FULLY IMPLEMENTED - delegates to backend.sandboxed_fs to list in-memory files created by BASIC programs (OPEN/PRINT#/CLOSE)"

However, the implementation has issues:
1. Returns empty list [] if backend.sandboxed_fs doesn't exist (silent failure)
2. Catches all exceptions with bare 'except:' and returns (filename, None, False) - loses error information
3. No validation that backend.sandboxed_fs has the expected methods before calling them

This is not "FULLY IMPLEMENTED" - it's partially implemented with error handling gaps.

---

---

#### code_vs_comment

**Description:** Comment says CONT fails if program edited, but clear_execution_state() doesn't clear stopped flag as claimed

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in clear_execution_state() (line ~145): 'Note: We do NOT clear the stopped flag here. The stopped flag is checked by CONT to determine if there's anything to continue. When the program is edited, CONT will still see stopped=True but will fail because the PC and execution state are now invalid (this is the intended behavior documented in cmd_cont()).'

Comment in cmd_cont() (line ~280): 'IMPORTANT: CONT will fail with "?Can't continue" if the program has been edited (lines added, deleted, or renumbered). While the stopped flag remains True after editing, the PC and execution stacks (GOSUB/RETURN and FOR/NEXT) become invalid, causing CONT to fail. The stopped flag is intentionally NOT cleared by clear_execution_state() so that CONT can detect the invalid state.'

However, cmd_cont() only checks: 'if not self.program_runtime or not self.program_runtime.stopped:' - it doesn't actually detect that the program was edited. If stopped=True and stacks are cleared, CONT would proceed and likely crash or behave incorrectly. The comment claims CONT will fail, but the code doesn't implement this check.

---

---

#### code_vs_comment_conflict

**Description:** STEP command implementation status is contradictory

**Affected files:**
- `src/interpreter.py`

**Details:**
execute_step() docstring (line ~2893) states:
"CURRENT STATUS: This method outputs an informational message but does NOT actually perform stepping. It's a partial implementation that acknowledges the command but doesn't execute the intended behavior."

But then says:
"The tick_pc() method DOES have working step infrastructure (modes 'step_statement' and 'step_line'), which is used by UI debuggers."

And concludes:
"Full STEP command implementation would require: Integration with tick_pc(mode='step_statement')"

This is contradictory - if tick_pc() already has working step infrastructure, why does the comment say full implementation would require integrating with it? Either the infrastructure exists and just needs to be connected, or it doesn't exist. The comment suggests both.

---

---

#### code_vs_comment

**Description:** Docstring for _parse_line_number describes behavior that contradicts the actual parsing logic

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
The docstring states:
"When user edits line numbers, this finds the last valid number before code starts.
Example: User types '10 20' then starts code - returns 20 as the line number.
Example: ' 100 FOR I=1 TO 10' - returns 100, 'FOR' indicates code starts."

However, the code implementation loops through ALL numbers at the start:
"# Loop to find all line numbers at the start, keep the last one
pos = 1  # Start after status character
last_line_num = None
last_code_start = None

while pos < len(line):
    # Skip spaces
    while pos < len(line) and line[pos] == ' ':
        pos += 1
    ...
    # Must be followed by space to be a line number
    if pos < len(line) and line[pos] == ' ':
        try:
            last_line_num = int(line[num_start:pos])
            ...
            # Continue loop to see if there's another number"

This means '10 20 FOR' would return 20, but ' 100 FOR I=1 TO 10' would return 100 and treat 'FOR I=1 TO 10' as code. However, the example ' 100 FOR I=1 TO 10' is misleading because 'FOR' is not a number, so the loop would stop at 100 anyway. The docstring example doesn't demonstrate the 'last valid number' behavior clearly.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about LINE statement implementation

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
not-implemented.md states: 'LINE - Draw line (GW-BASIC graphics version - not the LINE INPUT statement which IS implemented)'. However, features.md under Input/Output lists 'LINE INPUT - Full line input' as implemented. This creates confusion about whether LINE is implemented or not. The clarification in not-implemented.md suggests LINE (graphics) is not implemented but LINE INPUT (text input) is, but this distinction should be clearer in features.md.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about variable editing capability in Curses UI

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
variables.md states: "⚠️ **Not Implemented**: You cannot edit variable values directly in the variables window."

But feature-reference.md states: "### Edit Variable Value (Not implemented)
⚠️ Variable editing is not available in Curses UI. You cannot directly edit values in the variables window."

Both agree it's not implemented, but variables.md has a full section on "Modifying Variables" that could mislead users into thinking it's possible, while feature-reference.md is clearer that it's completely unavailable.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about Cut/Copy/Paste availability

**Affected files:**
- `docs/help/ui/curses/editing.md`
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
editing.md states: "**Note:** Cut/Copy/Paste operations are not available in the Curses UI due to keyboard shortcut conflicts. Use your terminal's native clipboard functions instead (typically Shift+Ctrl+C/V or mouse selection)."

feature-reference.md states: "### Cut/Copy/Paste (Not implemented)
Standard clipboard operations are not available in the Curses UI due to keyboard shortcut conflicts:
- **{{kbd:stop:curses}}** - Used for Stop/Interrupt (cannot be used for Cut)
- **{{kbd:continue:curses}}** - Terminal signal to exit program (cannot be used for Copy)
- **{{kbd:save:curses}}** - Used for Save File (cannot be used for Paste; {{kbd:save:curses}} is reserved by terminal for flow control)"

quick-reference.md states: "**Note:** Cut/Copy/Paste are not available - use your terminal's native clipboard (typically Shift+Ctrl+C/V or mouse selection)."

The feature-reference provides much more detail about WHY these aren't available, which should be consistent across all three documents.

---

---

#### documentation_inconsistency

**Description:** Web UI debugger capabilities inconsistently described

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/index.md`

**Details:**
index.md comparison table shows:
"| Debugger | ✓ | ✗ | ✓ | Limited |"
Indicating Web UI has "Limited" debugger.

But debugging.md describes extensive planned features:
- Breakpoint management (partially implemented)
- Variable inspector (planned)
- Call stack (planned)
- Logpoints (future)
- Data breakpoints (future)
- Debug console (future)
- Performance profiling (future)

The document clearly marks many features as "planned" or "future", but the index.md doesn't clarify what "Limited" means. Users might expect more than is currently available.

---

---

#### documentation_inconsistency

**Description:** Documents reference features marked as not implemented

**Affected files:**
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/settings.md`

**Details:**
workflows.md and tips.md describe using Smart Insert, Variables Window, Execution Stack, and Renumber as if they are fully implemented:

workflows.md:
"2. Press **{{kbd:smart_insert:tk}}** (Smart Insert) to insert blank line"
"2. Press **{{kbd:toggle_variables:tk}}** to open Variables window"
"1. Press **{{kbd:renumber:tk}}** (Renumber)"

tips.md:
"Use **{{kbd:smart_insert:tk}}** (Smart Insert) to insert blank lines"
"Press **{{kbd:toggle_stack:tk}}** (Toggle Stack)"

But settings.md states:
"**Current Status:** Many TK UI features work (auto-save, syntax checking, breakpoints, etc.) but the graphical settings dialog is not yet implemented."

The workflows and tips documents have notes saying "Check Settings for current implementation status" but they don't clarify which specific features in their workflows are or aren't implemented.

---

---

#### Code vs Comment conflict

**Description:** VariableNode type_suffix and explicit_type_suffix documentation may be confusing about when suffix should be regenerated

**Affected files:**
- `src/ast_nodes.py`

**Details:**
VariableNode docstring states: 'Example: In "DEFINT A-Z: X=5", variable X has type_suffix=\'%\' and explicit_type_suffix=False. The suffix must be tracked for type checking but not regenerated in source code.' This implies that when explicit_type_suffix=False, the suffix should not appear in regenerated source. However, the comment 'Both fields must always be examined together to correctly handle variable typing' suggests complexity that may not be fully explained.

---

---

#### code_vs_comment

**Description:** Comment about ERL renumbering behavior doesn't match implementation scope

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in _renum_erl_comparison() (line ~880): 'MBASIC 5.21 Manual Specification: When ERL appears on the left side of a comparison operator (=, <>, <, >, <=, >=), the right-hand number is treated as a line number reference and should be renumbered. Note: Only ERL on LEFT side is checked (ERL = 100, not 100 = ERL).

INTENTIONAL DEVIATION FROM MANUAL: This implementation renumbers for ANY binary operator with ERL on left, including arithmetic operators (ERL + 100, ERL * 2, etc.), not just comparison operators.'

However, the code (line ~920) simply checks: 'if type(expr).__name__ != "BinaryOpNode": return' and then 'if type(left).__name__ == "VariableNode" and left.name == "ERL"'

The comment claims this is intentional deviation, but also says 'Implementation: The code does NOT filter by operator type' - this makes it sound like an implementation limitation rather than an intentional choice. The comment is unclear about whether this is a bug or a feature.

---

---

#### code_vs_comment

**Description:** execute_next docstring describes behavior that contradicts the actual implementation regarding separate statements

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 1046-1057 says:
"This differs from separate statements (NEXT I: NEXT J: NEXT K) which would
always execute sequentially, processing all three NEXT statements."

But this is misleading because the code doesn't handle "separate statements" - it only handles a single NEXT statement with multiple variables. The comparison to "separate statements" suggests the interpreter would behave differently for "NEXT I: NEXT J: NEXT K" vs "NEXT I, J, K", but the code shown only implements the comma-separated case. The docstring makes claims about behavior not shown in this code.

---

---

#### code_vs_comment

**Description:** emit_keyword docstring requires lowercase input but serialize_rem_statement shows uppercase storage

**Affected files:**
- `src/position_serializer.py`

**Details:**
emit_keyword docstring says: 'Args:
    keyword: The keyword to emit (must be normalized lowercase by caller, e.g., "print", "for")'

And: 'Note: This function requires lowercase input because it looks up the display case from the keyword case manager using the normalized form.'

But serialize_rem_statement comment says: 'Note: stmt.comment_type is stored in uppercase by the parser ("APOSTROPHE", "REM", or "REMARK"). We convert to lowercase before passing to emit_keyword() which requires lowercase input.'

This reveals that keywords are stored in uppercase in the AST (from TokenType enum names), requiring conversion. The emit_keyword docstring should mention this architectural detail about why lowercase is required (because parser stores uppercase but manager expects lowercase keys).

---

---

#### code_vs_comment

**Description:** get_variable() docstring claims token is REQUIRED but implementation allows token.line/position to be missing

**Affected files:**
- `src/runtime.py`

**Details:**
Lines 257-268 docstring: "Args:
    ...
    token: REQUIRED - Token object for tracking (ValueError raised if None).

           Token object is required but its attributes are optional:
           - token.line: Preferred for tracking, falls back to self.pc.line_num if missing
           - token.position: Preferred for tracking, falls back to None if missing

           This allows robust handling of tokens from various sources (lexer, parser,
           fake tokens) while enforcing that some token object must be provided."

The docstring says token is REQUIRED but then says its attributes are optional with fallbacks. This is contradictory - if attributes can be missing and have fallbacks, the token isn't truly required in the strict sense. The implementation (line 295) does check for None token, but the 'required but optional attributes' phrasing is confusing.

---

---

#### code_vs_comment

**Description:** SettingsManager class docstring claims file-level settings infrastructure is FULLY IMPLEMENTED but persistence is NOT IMPLEMENTED, contradicting the actual state

**Affected files:**
- `src/settings.py`

**Details:**
Class docstring states:
    """Manages user settings with scope precedence.

    Precedence: project > global > default

    Note: File-level settings (per-file settings) infrastructure is FULLY IMPLEMENTED for
    runtime manipulation (file_settings dict, FILE scope support in get/set/reset methods),
    but persistence is NOT IMPLEMENTED (load() doesn't populate it, save() doesn't persist it).
    Files can have temporary settings set programmatically via set() with scope=SettingScope.FILE,
    but these won't survive program restarts. Reserved for future use with persistence layer.
    """

However, the get() method docstring contradicts this:
        """Get setting value with scope precedence.

        Precedence order: file > project > global > definition default > provided default

        Note: File-level settings (first in precedence) are not populated in normal usage,
        but can be set programmatically via set(key, value, scope=SettingScope.FILE).
        The file_settings dict is checked first, but no persistence layer exists (not saved/loaded)
        and no UI/command manages per-file settings. In practice, typical precedence order is:
        project > global > definition default > provided default.
        """

The class docstring says infrastructure is "FULLY IMPLEMENTED" while get() says "not populated in normal usage" and "no UI/command manages per-file settings". These statements conflict - if there's no UI/command and it's not populated normally, it's not "fully implemented" for practical use.

---

---

#### documentation_inconsistency

**Description:** The class docstring states 'Status priority (when both error and breakpoint): ? takes priority (error shown) - After fixing error, ● becomes visible (automatically handled by set_error() method which checks has_breakpoint flag when clearing errors)' but this description is somewhat misleading. The set_error() method doesn't 'check' the has_breakpoint flag when clearing - it always updates status based on priority regardless of whether clearing or setting.

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring: 'After fixing error, ● becomes visible (automatically handled by set_error() method which checks has_breakpoint flag when clearing errors)'

Actual set_error() implementation:
'# Update status symbol (error takes priority)
if metadata['has_error']:
    metadata['status'] = '?'
elif metadata['has_breakpoint']:
    metadata['status'] = '●'
else:
    metadata['status'] = ' ''

The logic is the same whether setting or clearing errors - it's not a special 'check when clearing' behavior, it's just the standard priority logic that always runs.

---

---

#### code_vs_comment

**Description:** Comment in serialize_statement() describes prevention strategy but implementation may not handle all statement types

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment states: "Prevention strategy: Explicitly fail (with ValueError) rather than silently omitting
statements during RENUM, which would corrupt the program.
All statement types must be handled above - if we reach here, serialization failed."

The else clause raises ValueError for unhandled statement types, which is good. However, the comment claims "All statement types must be handled above" but there's no verification that the handled types match all possible statement types in the AST. If new statement types are added to the parser, they won't be caught until runtime during RENUM.

---

---

#### code_vs_comment

**Description:** Comment in _serialize_runtime says 'Handles complex objects like AST nodes using pickle' but the shown code doesn't demonstrate pickle usage

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _serialize_runtime() method:

Docstring says: "Serialize runtime state.

Handles complex objects like AST nodes using pickle.

Returns:
    dict: Serialized runtime state"

The code shown imports pickle and closes files, but the actual serialization of AST nodes using pickle is not visible in the provided code snippet. This makes it unclear if pickle is actually used or if the comment is outdated.

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

**Description:** Inconsistent descriptions of debugging features implementation status

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/web-interface.md`

**Details:**
features.md under 'Debug Mode (Partially Implemented)' states: 'Basic breakpoint support (via Run menu)', 'Step execution ({{kbd:step:web}}, {{kbd:step_line:web}})', 'Basic variable inspection (via Debug menu)', 'Call stack (planned)'.

However, getting-started.md under 'Debugging Features > Show Stack' says: 'See the current execution stack: Click Run → Show Stack'.

This is contradictory - features.md says call stack is 'planned', but getting-started.md describes it as a currently available feature accessible via 'Run → Show Stack'. Which is correct?

---

---

#### documentation_inconsistency

**Description:** Curses UI resizable panels feature marked as partially implemented with misleading note

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In the 'User Interface' section of the feature matrix:
| **Resizable panels** | ❌ | ⚠️ | ✅ | ✅ | Curses: fixed 70/30 split (not user-resizable) |

The Curses column shows ⚠️ (partially implemented) but the note says 'fixed 70/30 split (not user-resizable)', which suggests it should be ❌ (not available) rather than ⚠️ (partially implemented). A fixed split is not a partial implementation of resizable panels - it's the absence of that feature.

---

---

#### documentation_inconsistency

**Description:** Contradictory information about Find/Replace in Web UI

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
In the 'Editing Features' section:
| **Find/Replace** | ❌ | ❌ | ✅ | ⚠️ | Tk: implemented, Web: planned |

Web UI is marked as ⚠️ (partially implemented) with note 'Web: planned'.

However, in 'Coming Soon' section:
'- ⏳ Find/Replace in Web UI'

And in 'Known Gaps' section:
'- Web: No Find/Replace yet'

⚠️ means 'partially implemented' according to the legend, but the notes say it's 'planned' and 'not yet' available. This should be 📋 (planned) or ❌ (not available), not ⚠️.

---

---

#### Documentation inconsistency

**Description:** TypeInfo class documentation mentions 'legacy code' and 'gradual migration' without context

**Affected files:**
- `src/ast_nodes.py`

**Details:**
TypeInfo docstring states: 'Compatibility layer: Class attributes (INTEGER, SINGLE, etc.) alias VarType enum values to support legacy code that used TypeInfo.INTEGER instead of VarType.INTEGER. This allows gradual migration without breaking existing code. Note: New code should use VarType enum directly.' This references a migration strategy but doesn't indicate timeline, deprecation plans, or which parts of the codebase still use the old pattern.

---

---

#### code_vs_comment

**Description:** Comment about leading sign format contradicts general asterisk fill behavior

**Affected files:**
- `src/basic_builtins.py`

**Details:**
In format_numeric_field:
"# For leading sign: padding comes first (spaces only), then sign immediately before number
# Note: Leading sign format uses spaces for padding, never asterisks (even if ** specified)"

This comment suggests that ** (asterisk_fill) is ignored when leading_sign is True, but the code doesn't explicitly check for this conflict. The parse_numeric_field allows both leading_sign and asterisk_fill to be set simultaneously, which could lead to unexpected behavior.

---

---

#### Code vs Comment conflict

**Description:** Security comment about user_id validation is repeated but implementation doesn't validate

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The docstring states twice: "SECURITY: Must be securely generated/validated (e.g., session IDs) to prevent cross-user access. Do NOT use user-provided values."

And: "IMPORTANT: Caller must ensure user_id is securely generated/validated to prevent cross-user access (e.g., use session IDs, not user-provided values)"

However, the __init__ method does no validation of user_id whatsoever - it accepts any string. The security warning is for the caller, but the repeated emphasis suggests this is a critical security boundary. If it's truly critical, the class should validate or at least document what constitutes a valid user_id format.

---

---

#### code_vs_comment

**Description:** execute_input comment mentions input_file_number but says it's 'Currently always None'

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment says:
"Note: input_file_number is set to None for keyboard input and file# for file input.
This allows the UI to distinguish between keyboard prompts (show in UI) and file input
(internal, no prompt needed). Currently always None since file input bypasses this path."

The code sets:
self.state.input_file_number = None  # None indicates keyboard input (not file)

This is consistent with the comment, but the phrase 'Currently always None' suggests incomplete implementation or future work, which may be outdated if file input is fully implemented via the synchronous path.

---

---

#### documentation_inconsistency

**Description:** MID$ assignment validation comment has redundant explanation

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_midassignment() (line ~2745), comment states:
"Validate start position (must be within string: 0 <= start_idx < len)
Note: start_idx == len(current_value) is considered out of bounds (can't start replacement past end)"

The "Note" is redundant - if start_idx < len(current_value) is required, then start_idx == len(current_value) is obviously out of bounds. This suggests the comment was added during debugging and never cleaned up.

---

---

#### Code vs Comment conflict

**Description:** get_char() backward compatibility comment claims it preserves non-blocking behavior, but original implementation details are not visible

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
Comment states:
    # Backward compatibility alias
    # This method was renamed from get_char() to input_char() for consistency with
    # the IOHandler base class interface. The get_char() alias is maintained for
    # backward compatibility with older code.
    def get_char(self):
        '''Deprecated: Use input_char() instead.
        This is a backward compatibility alias. New code should use input_char().
        Note: Always calls input_char(blocking=False) for non-blocking behavior.
        The original get_char() implementation was non-blocking, so this preserves
        that behavior for backward compatibility.'''
        return self.input_char(blocking=False)

The comment claims the original get_char() was non-blocking, but we cannot verify this from the provided code. Also, input_char() in web_io always returns "" immediately regardless of blocking parameter, so the distinction is meaningless.

---

---

#### code_vs_comment

**Description:** Token dataclass docstring describes convention for original_case vs original_case_keyword but implementation doesn't enforce it

**Affected files:**
- `src/tokens.py`

**Details:**
Token dataclass docstring:
    """Represents a single token in MBASIC source code.

    Attributes:
        type: Token type (keyword, identifier, number, etc.)
        value: Normalized value (lowercase for identifiers/keywords)
        line: Line number where token appears
        column: Column number where token starts
        original_case: Original case for user-defined identifiers (variable names) before normalization.
                      Only set for IDENTIFIER tokens. Example: "myVar" stored here, "myvar" in value.
        original_case_keyword: Original case for keywords, determined by keyword case policy.
                              Only set for keyword tokens (PRINT, IF, GOTO, etc.). Used by serializer
                              to output keywords with consistent or preserved case style.

    Note: By convention, these fields are used for different token types:
    - original_case: For IDENTIFIER tokens (user variables) - preserves what user typed
    - original_case_keyword: For keyword tokens - stores policy-determined display case

    The dataclass does not enforce this convention (both fields can technically be set on the
    same token) to allow implementation flexibility. However, the lexer/parser follow this
    convention and only populate the appropriate field for each token type. Serializers check
    token type to determine which field to use: original_case_keyword for keywords,
    original_case for identifiers.
    """

The docstring explicitly states "The dataclass does not enforce this convention" and "both fields can technically be set on the same token", which is accurate. However, the phrasing "By convention" and "However, the lexer/parser follow this convention" suggests this is a soft rule that could be violated. This is intentional flexibility but could lead to confusion if future code doesn't follow the convention.

---

---

#### Documentation inconsistency

**Description:** UIBackend docstring lists potential future backends but doesn't mention curses backend

**Affected files:**
- `src/ui/base.py`

**Details:**
base.py UIBackend docstring states:
"Different UIs can implement this interface:
- CLIBackend: Terminal-based REPL (interactive command mode)
- CursesBackend: Full-screen terminal UI with visual editor
- TkBackend: Desktop GUI using Tkinter

Future/potential backend types (not yet implemented):
- WebBackend: Browser-based interface"

However, curses_keybindings.json and curses_settings_widget.py exist, suggesting CursesBackend is at least partially implemented. The docstring should clarify which backends are fully implemented vs. in progress.

---

---

#### code_vs_comment

**Description:** Comment about pasted BASIC code assumption may not match all use cases

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_numbers() method:
"# FIRST: Check if line starts with a digit (raw pasted BASIC with line numbers)
# In this context, we assume lines starting with digits are numbered program lines (e.g., '10 PRINT').
# Note: While BASIC statements can start with digits (numeric expressions), when pasting
# program code, lines starting with digits are conventionally numbered program lines."

This assumption could be incorrect if a user manually types a numeric expression at the start of a line without a line number. The comment acknowledges this ambiguity but the code doesn't handle it - it will always treat digit-starting lines as numbered program lines.

---

---

#### code_vs_comment

**Description:** Comment states 'Ctrl+I is bound directly to editor text widget in start()' but the actual binding location is not in start() method

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~467 comment in _create_menu():
'# Note: Ctrl+I is bound directly to editor text widget in start() (not root window)'

Line ~209 in start() method:
# Bind Ctrl+I for smart insert line (must be on text widget to prevent tab)
self.editor_text.text.bind('<Control-i>', self._on_ctrl_i)

The comment is technically correct but could be clearer that it's explaining why it's NOT bound in _create_menu() where other shortcuts are bound.

---

---

#### code_vs_comment

**Description:** Docstring for start() method says 'NOT IMPLEMENTED - raises NotImplementedError' but this is redundant with the actual implementation that always raises the exception

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring at line ~420:
    def start(self):
        """NOT IMPLEMENTED - raises NotImplementedError.

        Web backend cannot be started per-instance. Use start_web_ui() module
        function instead, which creates backend instances per user session.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError("Web backend uses start_web_ui() function, not backend.start()")

The docstring is accurate and helpful, but 'NOT IMPLEMENTED' in all caps might be misleading - the method IS implemented, it just intentionally raises an exception. This is more of a style issue than an inconsistency.

---

---

#### code_comment_conflict

**Description:** Comment describes class as 'Legacy' and 'DEPRECATED' but class name is WebHelpLauncher_DEPRECATED which is redundant

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Class definition: 'class WebHelpLauncher_DEPRECATED:'
Comment above it: '# Legacy class kept for compatibility - new code should use direct web URL instead'

The _DEPRECATED suffix in the class name already indicates it's deprecated, making the comment partially redundant. However, the comment provides useful migration guidance.

---

---

#### code_comment_conflict

**Description:** Function docstring says 'ui_type' parameter but doesn't explain what values are valid

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
open_help_in_browser() docstring:
'Args:
    topic: Specific help topic (e.g., "statements/print", "ui/tk/index")
    ui_type: UI type for UI-specific help ("tk", "curses", "web", "cli")'

The examples show 4 UI types, but the function constructs URL as f'{HELP_BASE_URL}/ui/{ui_type}/' without validation. If an invalid ui_type is passed, it would create a broken URL. The docstring should clarify these are the only valid values or the code should validate them.

---

---

#### documentation_inconsistency

**Description:** CLS implementation status unclear between documents

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/not-implemented.md`

**Details:**
not-implemented.md states: 'Note: Basic CLS (clear screen) IS implemented in MBASIC - see [CLS](../common/language/statements/cls.md). The GW-BASIC extended CLS with optional parameters is not implemented.' However, features.md does not list CLS under any section (Program Control, Input/Output, etc.), making it unclear whether CLS is a documented feature or an undocumented one.

---

---

#### documentation_inconsistency

**Description:** LPRINT behavior inconsistently described

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md states: 'LPRINT - Line printer output (Note: Statement is parsed but produces no output - see [LPRINT](../common/language/statements/lprint-lprint-using.md) for details)'. This suggests LPRINT is implemented but non-functional, which is confusing. It should either be listed as 'not implemented' or the behavior should be clarified (e.g., 'parsed for compatibility but no-op').

---

---

#### documentation_inconsistency

**Description:** Curses UI limitations list 'No Find/Replace' but doesn't clarify if this is a permanent limitation or planned feature

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
Under Curses UI limitations:
'- No Find/Replace'

It's unclear if this is a fundamental limitation of terminal UIs or just not implemented yet. The Tk UI has Find/Replace, so it's a language feature, just not exposed in Curses.

---

---

#### documentation_inconsistency

**Description:** Inconsistent use of ⚠️ symbol in feature matrix

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
The legend states:
'| ⚠️ | Partially implemented (see Notes column for details) |'

However, some ⚠️ entries don't represent partial implementation:
- 'Curses: fixed 70/30 split (not user-resizable)' - This is not partial, it's a different feature (fixed vs resizable)
- 'CLI: limited' for keyboard shortcuts - 'limited' is vague and doesn't clearly indicate what's partially implemented
- 'Curses: basic' for syntax highlighting - 'basic' suggests reduced functionality, not partial implementation

The ⚠️ symbol is being used inconsistently to mean 'different implementation', 'limited functionality', and 'partial implementation'.

---

---

