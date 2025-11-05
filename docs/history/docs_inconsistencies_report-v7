# Enhanced Consistency Report (Code + Documentation)

Generated: 2025-11-05 05:38:44
Analyzed: Source code (.py, .json) and Documentation (.md)

## 🔧 Code vs Comment Conflicts


## 📋 General Inconsistencies

### 🔴 High Severity

#### code_vs_documentation

**Description:** ProgramManager uses file_io.py's FileIO abstraction for LOAD/SAVE/MERGE operations, but the documentation claims it uses direct filesystem operations

**Affected files:**
- `src/file_io.py`
- `src/editing/manager.py`

**Details:**
ProgramManager.save_to_file() docstring says 'Raises: IOError: If file cannot be written' and uses direct 'open(filename, 'w')' calls. However, file_io.py defines a FileIO abstraction layer (RealFileIO and SandboxedFileIO) that should be used instead. The manager.py code directly accesses filesystem:

```python
def save_to_file(self, filename: str) -> None:
    with open(filename, 'w') as f:
        for line_number in sorted(self.lines.keys()):
            f.write(self.lines[line_number] + '\n')
```

But file_io.py provides:
```python
class FileIO(ABC):
    @abstractmethod
    def save_file(self, filename: str, content: str) -> None:
```

This means ProgramManager bypasses the abstraction layer entirely.

---

#### code_vs_documentation

**Description:** Two competing filesystem abstraction layers exist with different APIs and purposes

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
file_io.py defines FileIO abstract class with methods:
- list_files(filespec: str) -> List[Tuple[str, int, bool]]
- load_file(filename: str) -> str
- save_file(filename: str, content: str) -> None
- delete_file(filename: str) -> None
- file_exists(filename: str) -> bool

filesystem/base.py defines FileSystemProvider with different API:
- open(filename: str, mode: str, binary: bool) -> FileHandle
- exists(filename: str) -> bool
- delete(filename: str)
- list_files(pattern: Optional[str]) -> list
- get_size(filename: str) -> int
- reset()

The FileSystemProvider uses a FileHandle abstraction for file operations, while FileIO uses direct string content. These appear to be two different architectural approaches to the same problem, with no clear indication of which should be used where.

---

#### code_vs_comment

**Description:** Docstring for cmd_edit() claims count prefixes and search commands are not implemented, but doesn't show if they're parsed or rejected

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring says:
"Note: Count prefixes ([n]D, [n]C) and search commands ([n]S, [n]K) are not yet implemented."

But the implementation only handles single-character commands (D, C, I, X, H, L, E, Q, A, Space, CR). There's no code to detect or reject count prefixes or search commands - they would just be treated as unknown commands and ignored. The docstring implies they might be added later, but the code doesn't validate or warn about them.

---

#### code_vs_comment

**Description:** Comment claims return_stmt > len(statements) is invalid, but code allows return_stmt == len(statements) as valid, creating confusion about boundary condition

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 1009: '# return_stmt is 0-indexed offset. Valid range: 0 to len(statements) inclusive.'
Comment at line 1010: '# return_stmt == len(statements) is valid: "continue at next line" (GOSUB was last stmt)'
Comment at line 1011: '# return_stmt > len(statements) is invalid: statement was deleted (validation error)'

But then code at line 1012: 'if return_stmt > len(line_statements):  # Check for strictly greater than (== len is OK)'

The comment says 'Valid range: 0 to len(statements) inclusive' which is ambiguous. Does 'inclusive' mean <= len or < len? The code clarifies it means <= len is valid, but the comment could be clearer by saying 'Valid range: 0 to len(statements) (where len means continue at next line)'.

---

#### code_vs_comment

**Description:** OPTION BASE comment says 'Duplicate Definition' for arrays existing, but doesn't clarify implicit vs explicit dimensioning

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_optionbase() at line ~1330, comment states:
# MBASIC 5.21 gives 'Duplicate Definition' if:
# 1. OPTION BASE has already been executed, OR
# 2. Any arrays have been created (even with implicit BASE 0)

The code checks:
if len(self.runtime._arrays) > 0:
    raise RuntimeError('Duplicate Definition')

This doesn't distinguish between explicitly dimensioned arrays (via DIM) and implicitly created arrays (via first use like A(5)=10). MBASIC 5.21 behavior may differ for these cases. The comment says 'even with implicit BASE 0' but it's unclear if this means implicitly-created arrays or implicitly-assumed base.

---

#### code_vs_comment

**Description:** OPEN statement comment lists valid modes but error message differs

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_open() at line ~1850, comment states:
# Valid modes: I (input), O (output), A (append), R (random access)
# Any other mode raises 'Invalid OPEN mode' error

But the actual error raised is:
raise RuntimeError(f'Invalid OPEN mode: {mode}')

The comment says the error message is 'Invalid OPEN mode' but the code includes the actual mode value. This is a minor inconsistency but could affect error handling code that matches on exact error messages.

---

#### code_vs_comment

**Description:** apply_keyword_case_policy function has 'preserve' policy that docstring says shouldn't be called but code handles anyway

**Affected files:**
- `src/position_serializer.py`

**Details:**
In apply_keyword_case_policy:
elif policy == "preserve":
    # Preserve is handled by caller passing in original case
    # This shouldn't be called with "preserve", but if it is, use capitalize
    return keyword.capitalize()

This is contradictory - if preserve is handled by caller, why does this function need to handle it? Either:
1. The function should raise an error for 'preserve' policy
2. The comment is wrong and 'preserve' IS a valid policy here
3. The implementation is defensive but the comment should explain why

---

#### documentation_inconsistency

**Description:** max_string_length documented as '255 bytes (MBASIC 5.21 limit - standard for 8-bit BASIC)' but this appears in multiple places with inconsistent justification

**Affected files:**
- `src/resource_limits.py`

**Details:**
The 255-byte string limit appears in:
1. ResourceLimits.__init__ default: max_string_length=255 with comment '255 bytes (MBASIC 5.21 limit - standard for 8-bit BASIC)'
2. create_web_limits: max_string_length=255 with same comment
3. create_local_limits: max_string_length=255 with same comment
4. create_unlimited_limits: max_string_length=1024*1024 (1MB)

The 'unlimited' preset breaks the '255 is MBASIC standard' rule. Either:
1. The comment should say '255 is recommended for compatibility' not 'standard'
2. The unlimited preset should also use 255 for MBASIC compatibility
3. The comment should explain that unlimited is for testing only

---

#### Code vs Documentation inconsistency

**Description:** STEP command documentation conflicts with keybinding description for statement vs line execution

**Affected files:**
- `src/ui/cli_debug.py`
- `src/ui/curses_keybindings.json`

**Details:**
cli_debug.py cmd_step() docstring says:
"Executes a single statement (not a full line). If a line contains multiple
statements separated by colons, each statement is executed separately.

This matches the curses UI 'Step Statement' command (Ctrl+T).
For line-based stepping, see the UI-specific step_line command."

But curses_keybindings.json shows TWO different step commands:
- "step_line" (Ctrl+K): "Step Line (execute all statements on current line)"
- "step" (Ctrl+T): "Step statement (execute one statement)"

The CLI documentation claims STEP matches Ctrl+T (statement stepping), but also references a separate step_line command that doesn't exist in CLI.

---

#### internal_code_inconsistency

**Description:** Inconsistent line number width handling between parsing (variable) and formatting (fixed)

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
_parse_line_number method uses variable-width parsing:
space_idx = line.find(' ', 1)
if space_idx > 1:
    line_num = int(line[1:space_idx])
    code_start_col = space_idx + 1

This allows any number of digits for line numbers.

But _parse_line_numbers method formats with fixed width:
line_num_formatted = f"{num_str:>5}"
new_line = f" {line_num_formatted} {rest}"

This creates inconsistency: parsing accepts variable width but formatting always produces 5 characters.

---

#### code_internal_inconsistency

**Description:** Variable name inconsistency: editor_lines vs self.editor.lines

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line ~99: 'if self.program.has_lines() and not self.editor_lines:'

But throughout the rest of the code, the pattern is 'self.editor.lines' (e.g., line ~577: 'if line_number in self.editor.lines:', line ~619: 'self.editor.lines[insert_num] = ""').

There's no visible initialization of self.editor_lines as a separate attribute, suggesting this may be a typo or outdated reference.

---

#### code_vs_comment

**Description:** Comment says 'NOTE: Don't call interpreter.start() because it resets PC!' but then immediately clears halted flag and manipulates state, which may have similar effects

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment: '# NOTE: Don't call interpreter.start() because it resets PC!
# RUN 120 already set PC to line 120, so just clear halted flag'
Code then does:
if not hasattr(self.interpreter, 'state') or self.interpreter.state is None:
    self.interpreter.state = InterpreterState(_interpreter=self.interpreter)
self.runtime.halted = False
self.interpreter.state.is_first_line = True

The comment warns against resetting PC, but the code creates a new InterpreterState if none exists, which may have initialization side effects. The relationship between these operations and PC preservation is unclear.

---

#### code_vs_documentation

**Description:** Help widget footer shows 'u=Back' but keybindings.py documents 'U' (uppercase) for back navigation

**Affected files:**
- `src/ui/help_widget.py`
- `src/ui/keybindings.py`

**Details:**
help_widget.py line 72:
self.footer = urwid.Text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search u=Back ESC/Q=Exit ")

help_widget.py line 289:
elif key == 'u' or key == 'U':

This accepts both, but the footer only shows lowercase 'u', which may confuse users expecting consistency with other uppercase key displays like 'Q'.

---

#### code_vs_comment

**Description:** Comment says 'Execution stack window (menu only - no dedicated key, step_line uses Ctrl+K)' but LIST_KEY is defined as step_line with Ctrl+K, creating confusion about what Ctrl+K does

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
keybindings.py line 103-106:
# Execution stack window (menu only - no dedicated key, step_line uses Ctrl+K)
STACK_KEY = ''  # No keyboard shortcut
STACK_CHAR = ''
STACK_DISPLAY = 'Menu only'

keybindings.py line 127-130:
# Step Line (Ctrl+K) - execute all statements on current line
_list_key = _get_key('editor', 'step_line') or 'Ctrl+K'
LIST_KEY = _ctrl_key_to_urwid(_list_key)
LIST_CHAR = _ctrl_key_to_char(_list_key)

The comment about stack window mentions 'step_line uses Ctrl+K' as if explaining why stack can't use it, but this creates confusion about the relationship between these features.

---

#### code_vs_documentation

**Description:** KEYBINDINGS_BY_CATEGORY shows 'Shift+Ctrl+B' for Clear all breakpoints but CLEAR_BREAKPOINTS_KEY is defined as 'ctrl shift b' (different order)

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
keybindings.py line 165-167:
# Clear all breakpoints (hardcoded)
CLEAR_BREAKPOINTS_KEY = 'ctrl shift b'
CLEAR_BREAKPOINTS_DISPLAY = 'Ctrl+Shift+B'

The urwid key format is 'ctrl shift b' but the display format is 'Ctrl+Shift+B'. While these may be equivalent, the inconsistency in modifier order (ctrl shift vs Shift+Ctrl) could cause confusion.

---

#### code_vs_documentation

**Description:** LIST_KEY is documented as 'Step Line' but STATUS_BAR_SHORTCUTS shows '^K stack', suggesting Ctrl+K has conflicting purposes

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
keybindings.py line 127-130:
# Step Line (Ctrl+K) - execute all statements on current line
_list_key = _get_key('editor', 'step_line') or 'Ctrl+K'
LIST_KEY = _ctrl_key_to_urwid(_list_key)
LIST_DISPLAY = _list_key

keybindings.py line 260:
STATUS_BAR_SHORTCUTS = "MBASIC - ^F help  ^U menu  ^W vars  ^K stack  Tab cycle  ^Q quit"

Ctrl+K is defined as 'Step Line' in the keybindings but the status bar shows it as 'stack'. These are different functions.

---

#### incomplete_implementation

**Description:** Method _edit_simple_variable is incomplete - cuts off mid-implementation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
The _edit_simple_variable method at line ~840 ends abruptly:

# Create a token with line=-1 to indicate immediate mode / variable editor
class ImmediateModeToken:
    def __init__(self):
        self.line = -1
        self.position = None

The method doesn't complete - it defines a token class but never uses it to actually update the variable. The implementation is cut off.

---

#### internal_logic_inconsistency

**Description:** Array element editing uses inconsistent array_base logic

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _edit_array_element() at lines 95-103:
"if not default_subscripts and dimensions:\n            array_base = self.runtime.array_base\n            if array_base == 0:\n                # OPTION BASE 0: use all zeros\n                default_subscripts = ','.join(['0'] * len(dimensions))\n            else:\n                # OPTION BASE 1: use all ones\n                default_subscripts = ','.join(['1'] * len(dimensions))"

This assumes array_base can only be 0 or 1, but the else clause treats ANY non-zero value as base 1. This could be incorrect if array_base has an invalid value. Should explicitly check for array_base == 1 in the else-if.

---

#### code_vs_comment

**Description:** Comment in cmd_cont() describes CONT command behavior but implementation doesn't match typical BASIC CONT semantics

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In cmd_cont() method around line 1450:
Docstring: 'Execute CONT command - continue after STOP.\n\nResumes execution after:\n- STOP statement\n- Ctrl+C/Break\n- END statement (in some cases)\n\nInvalid if program was edited after stopping.'

But the implementation:
1. Only checks 'self.runtime.stopped' flag - doesn't validate if program was edited
2. Uses 'self.runtime.stop_line' and 'self.runtime.stop_stmt_index' which aren't set anywhere in the visible code
3. Calls '_tick()' method which doesn't exist (should be '_execute_tick()')
4. Sets 'self.is_running' which doesn't exist (should be 'self.running')

This suggests the cmd_cont() implementation is incomplete or outdated.

---

#### code_internal_inconsistency

**Description:** cmd_cont() calls non-existent '_tick()' method instead of '_execute_tick()'

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In cmd_cont() method (line 1472): 'self._tick()'

But the actual method defined in the class is '_execute_tick()' (line 1100). The '_tick()' method doesn't exist, so CONT command would crash with AttributeError.

---

#### code_vs_documentation

**Description:** The renum_program() function's docstring says it takes a 'renum_callback' parameter that 'Should handle GOTO, GOSUB, ON GOTO, ON GOSUB, IF THEN/ELSE line numbers', but the actual implementation walks the AST and calls the callback for ALL statements, not just those with line number references.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring:
renum_callback: Function that takes (stmt, line_map) to update statement references
                Should handle GOTO, GOSUB, ON GOTO, ON GOSUB, IF THEN/ELSE line numbers

Implementation:
for stmt in line_node.statements:
    renum_callback(stmt, line_map)  # Called for EVERY statement

This means the callback will be invoked for PRINT, LET, REM, etc. statements that have no line number references. The docstring should clarify that the callback is responsible for filtering which statements need updates.

---

#### code_vs_comment

**Description:** Comment says 'reuse existing interpreter to preserve session' but code creates new exec_io handler which may not preserve session

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _menu_step_line() and _menu_step_stmt():
# Update IO handler for execution (reuse existing interpreter to preserve session)
self.exec_io = SimpleWebIOHandler(self._append_output, self._get_input)
self.interpreter.io = self.exec_io

Creating a new IO handler and replacing the interpreter's IO may not preserve the session state. The comment suggests session preservation is the goal, but the implementation creates a fresh IO handler.

---

#### code_internal_inconsistency

**Description:** Inconsistent check for empty program between _menu_run and step functions

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _menu_run():
# If empty program, just show Ready (variables cleared, nothing to execute)
if not self.program.lines:
    self._set_status('Ready')
    self.running = False
    return

But in _menu_step_line() and _menu_step_stmt():
if not self.program.lines:
    self._notify('No program loaded', type='warning')
    return

RUN silently succeeds on empty program (just sets status), but STEP shows a warning. This inconsistency may confuse users.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'Don't sync editor from AST' but there's a TODO suggesting future architecture change

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1590:
# Don't sync editor from AST after immediate command - editor text is the source!
# Current flow: editor text → parsed to AST → execution
# (Never reverse: AST → text, as that would lose user's exact text/formatting)
# TODO: Future architecture: parse lines immediately into AST,
# text only kept for syntax errors

This TODO contradicts the 'Never reverse' statement above it. The TODO suggests a future where AST becomes the source of truth, which would require syncing editor from AST. This is a design inconsistency that needs resolution.

---

#### documentation_inconsistency

**Description:** README.md lists 'visual' backend but common/index.md does not mention it in the main help topics

**Affected files:**
- `docs/help/README.md`
- `docs/help/common/index.md`

**Details:**
README.md states: 'Entry Points... Visual Help: ui/visual/index.md' but common/index.md only lists shortcuts, language reference, and examples without any UI-specific navigation

---

#### code_vs_documentation

**Description:** Settings dialog in web UI doesn't implement breakpoint management but debugging.md describes Web UI breakpoint features

**Affected files:**
- `src/ui/web/web_settings_dialog.py`
- `docs/help/common/debugging.md`

**Details:**
web_settings_dialog.py only implements editor settings (auto-numbering) and limits settings (read-only)
debugging.md describes: 'Web UI: Click the line number to toggle breakpoint, Use the "Breakpoint" button in the toolbar'
No breakpoint settings or management visible in WebSettingsDialog class

---

#### documentation_inconsistency

**Description:** Error codes table has inconsistent numbering

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`

**Details:**
The error codes documentation shows gaps in numbering:
- Codes 1-18 are listed in General Errors
- Then jumps to 19-23, 26, 29-30 in Extended errors
- Then jumps to 50-58, 61-64, 66-67 in Disk I/O errors

Codes 24-25, 27-28, 31-49, 59-60, 65 are missing without explanation. This could confuse users who encounter these error numbers.

---

#### documentation_inconsistency

**Description:** HELPSETTING command name inconsistency

**Affected files:**
- `docs/help/common/language/statements/helpsetting.md`
- `docs/help/common/language/statements/index.md`

**Details:**
helpsetting.md title: 'HELPSETTING'
index.md lists it as: 'HELP SET'

These are different command names. Should be consistent - either 'HELPSETTING' or 'HELP SET' throughout.

---

#### documentation_inconsistency

**Description:** Contradictory information about PEEK/POKE implementation

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states: "PEEK/POKE - Emulated for compatibility" and "POKE: Parsed and executes successfully, but performs no operation (no-op)" and "PEEK: Returns random integer 0-255"

compatibility.md states: "PEEK/POKE - Emulated for compatibility" with same description but adds: "PEEK does NOT return values written by POKE"

Both documents describe the same feature but architecture.md is more detailed. The key point about PEEK not returning POKE values should be consistent across both documents.

---

#### documentation_inconsistency

**Description:** Self-contradictory statements about file handling in Web UI

**Affected files:**
- `docs/help/mbasic/compatibility.md`

**Details:**
Within the same section of compatibility.md, there are contradictory statements:

"**Web UI** - In-memory virtual filesystem:
The Web UI uses a sandboxed in-memory filesystem for security:"

But earlier in the same document:
"**IMPORTANT:** File handling differs between UIs:
**CLI, Tk, and Curses UIs** - Real filesystem access:"

Then later: "Files stored in browser memory (not browser localStorage)"

But also: "Files persist only during browser session"

These statements need to be reconciled - does Web UI use memory only, localStorage, or both? The documentation should clearly state the storage mechanism.

---

#### documentation_inconsistency

**Description:** Broken internal documentation link

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
curses/feature-reference.md references 'See [Find/Replace Status](find-replace.md)' but this file does not exist in the provided documentation. The only find-replace documentation is at 'docs/help/ui/cli/find-replace.md', not in the curses directory.

---

#### documentation_inconsistency

**Description:** Contradictory keyboard shortcuts for Save operation

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
files.md states: 'Press **Ctrl+V** (Note: Ctrl+S unavailable due to terminal flow control)' for saving programs.

However, quick-reference.md lists: '**Ctrl+V** | Save program' in the Program Management section.

But the note in files.md explicitly says Ctrl+S is unavailable, yet quick-reference.md doesn't mention Ctrl+V at all for saving - it only shows 'Menu only' for some operations but lists Ctrl+V for Save without the caveat about Ctrl+S.

---

#### documentation_inconsistency

**Description:** Contradictory help keyboard shortcuts

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
quick-reference.md states: '**?** | Help (with search)' under Global Commands.

But getting-started.md states: '**Ctrl+P** - Help (you're here now!)' in the Essential Keys section.

These are two completely different key combinations for the same function. Users following getting-started.md would press Ctrl+P, but quick-reference.md says to press ?.

---

#### documentation_inconsistency

**Description:** Menu access keyboard shortcut discrepancy

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/index.md`

**Details:**
quick-reference.md states: '**Ctrl+U** | Show menu' under Global Commands.

But index.md does not mention Ctrl+U at all in its help navigation table, and the curses UI documentation generally doesn't emphasize menu access as a primary interaction method.

---

#### documentation_inconsistency

**Description:** Find and Replace keyboard shortcuts inconsistency

**Affected files:**
- `docs/help/ui/tk/feature-reference.md`
- `docs/help/ui/tk/features.md`

**Details:**
feature-reference.md documents:
'### Find/Replace (Ctrl+F / Ctrl+H)'
And later: '- Find: Ctrl+F
- Replace: Ctrl+H
- Find Next: F3'

But features.md documents:
'**Find text ({{kbd:find}}):**'
'**Replace text ({{kbd:find_replace}}):**'

The template notation {{kbd:find}} and {{kbd:find_replace}} should expand to the same shortcuts as feature-reference.md, but this isn't clear. If they expand to different shortcuts, that's an inconsistency.

---

#### documentation_inconsistency

**Description:** Tk settings documentation claims 'more configuration options than the Web UI' and lists Keywords, Variables, Interpreter, and UI tabs, but Web settings documentation only shows Editor and Limits tabs with minimal options

**Affected files:**
- `docs/help/ui/tk/settings.md`
- `docs/help/ui/web/settings.md`

**Details:**
Tk settings.md states:
'The Tk (Tkinter) desktop GUI provides the most comprehensive settings dialog with tabbed interface for all MBASIC settings. It offers more configuration options than the Web UI, including keyword display, variable case handling, interpreter settings, and UI themes.'

Tabs listed in Tk:
- Editor Tab
- Keywords Tab (Case Style: force_lower, force_upper, force_capitalize)
- Variables Tab (Case Conflict policies, Show Types In Window)
- Interpreter Tab (Strict Mode, Max Execution Time, Debug Mode)
- UI Tab (Theme, Font Size)

Web settings.md only shows:
- Editor Tab (auto-numbering only)
- Limits Tab (view-only)

This is a major feature discrepancy that needs verification.

---

#### documentation_inconsistency

**Description:** Conflicting information about breakpoint implementation status

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/features.md`

**Details:**
debugging.md states:
'Currently Implemented:
1. Use Run → Toggle Breakpoint menu option
2. Enter the line number when prompted
3. A visual indicator appears in the editor
4. Use Run → Clear All Breakpoints to remove all'

And explicitly notes:
'Note: Advanced features like clicking line numbers to set breakpoints, conditional breakpoints, and a dedicated breakpoint panel are planned for future releases but not yet implemented.'

But features.md under 'Debugging Tools > Breakpoints' lists:
'Line breakpoints
Conditional breakpoints
Hit count breakpoints
Logpoints'

Without any 'future' or 'planned' qualifiers, suggesting they are currently available.

---

#### documentation_inconsistency

**Description:** Features document lists capabilities that are explicitly marked as not implemented in other documents

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
features.md lists under 'Debugging Tools > Breakpoints':
'Management:
- Enable/disable
- Edit conditions
- View all breakpoints
- Export/import'

And under 'Advanced Features':
'Session Management:
- Save sessions
- Load sessions
- Share sessions
- Collaborative editing
- Version control
- Conflict resolution'

But debugging.md explicitly states:
'Note: Advanced features like clicking line numbers to set breakpoints, conditional breakpoints, and a dedicated breakpoint panel are planned for future releases but not yet implemented.'

And getting-started.md states:
'Note: Collaboration features (sharing, collaborative editing, version control) are not currently implemented.'

features.md appears to be aspirational rather than documenting actual current features.

---

#### documentation_inconsistency

**Description:** Duplicate installation documentation with different content

**Affected files:**
- `docs/user/INSTALL.md`
- `docs/user/INSTALLATION.md`

**Details:**
Two separate installation guides exist: INSTALL.md (detailed, complete guide) and INSTALLATION.md (placeholder stating 'PLACEHOLDER - Documentation in progress'). INSTALLATION.md references 'docs/dev/INSTALLATION_FOR_DEVELOPERS.md' which is not in the provided files. This creates confusion about which installation guide to follow.

---

#### documentation_inconsistency

**Description:** Contradictory statements about feature completeness

**Affected files:**
- `docs/user/INSTALL.md`

**Details:**
INSTALL.md states 'This is a complete implementation of MBASIC 5.21. All core language features are implemented and tested.' under 'Feature Status', but then lists 'What Doesn't Work' including PEEK/POKE, INP/OUT, and LPRINT/LLIST. While these are explained as hardware-specific, the claim of 'complete implementation' and 'all core language features' is contradicted by the existence of non-working features.

---

#### documentation_inconsistency

**Description:** Smart Insert feature availability contradiction

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md extensively documents Smart Insert (Ctrl+I) as a Tk feature:
| **Ctrl+I** | Smart insert blank line |
## Smart Insert Workflow
**Smart Insert (Ctrl+I)** is the fastest way to add code...

UI_FEATURE_COMPARISON.md confirms:
| **Smart Insert** | ❌ | ❌ | ✅ | ❌ | Tk exclusive feature |

However, keyboard-shortcuts.md (Curses) does NOT document Ctrl+I at all, but DOES document:
| `Ctrl+J` | Insert line |

This suggests Curses has a 'Insert line' feature (Ctrl+J) that may be similar to Smart Insert, but it's unclear if this is the same feature or different. If different, the distinction should be clarified. If same, the feature comparison table is incorrect.

---

### 🟡 Medium Severity

#### code_internal_inconsistency

**Description:** Duplicate 'column' field definition in DefFnStatementNode

**Affected files:**
- `src/ast_nodes.py`

**Details:**
@dataclass
class DefFnStatementNode:
    """DEF FN statement - define single-line function"""
    name: str
    parameters: List['VariableNode']
    expression: 'ExpressionNode'
    line_num: int = 0
    column: int = 0
    column: int = 0  # <-- Duplicate field

---

#### code_vs_comment

**Description:** Comment claims identifiers preserve original case, but code returns original_text unconditionally without using case keeper table

**Affected files:**
- `src/case_string_handler.py`

**Details:**
In case_keepy_string method:
Comment says: "Identifiers always preserve their original case. Unlike keywords, which can be forced to a specific case policy, identifiers (variable/function names) retain their case as typed. This matches MBASIC 5.21 behavior where identifiers are case-insensitive for matching but preserve display case."

Code: elif setting_prefix == "idents":
    return original_text

The comment describes the behavior correctly, but the implementation bypasses the case keeper table entirely. If identifiers should be case-insensitive for matching (as stated), they should still be registered in the identifier_table for consistency checking, even if they always return original_text.

---

#### code_vs_comment

**Description:** INPUT function docstring uses incorrect syntax for file parameter

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Docstring says:
"INPUT$(n) - read n characters from keyboard
INPUT$(n, #filenum) - read n characters from file"

But the function signature is: def INPUT(self, num, file_num=None)

The docstring shows '#filenum' syntax which is BASIC syntax, not Python. The actual call would be INPUT(n, filenum) without the #. This could confuse developers about how to call the function from Python code.

---

#### code_internal_inconsistency

**Description:** UsingFormatter handles string encoding inconsistently between CVI/CVS/CVD and MKI/MKS/MKD

**Affected files:**
- `src/basic_builtins.py`

**Details:**
CVI/CVS/CVD functions use:
byte_data = s.encode('latin-1')

MKI/MKS/MKD functions use:
return byte_data.decode('latin-1')

This assumes all binary data can be represented as latin-1 strings. However, the INPUT function that reads from files doesn't specify encoding, which could cause issues. The file handling should consistently use binary mode for these operations.

---

#### documentation_inconsistency

**Description:** SandboxedFileIO documentation contradicts its implementation status

**Affected files:**
- `src/file_io.py`

**Details:**
Class docstring says:
"NOTE: Partially implemented. list_files() delegates to backend.sandboxed_fs, but load_file(), save_file(), delete_file(), and file_exists() are STUBS that raise IOError or return empty results."

But the load_file() implementation shows:
```python
def load_file(self, filename: str) -> str:
    raise IOError("LOAD not yet implemented in web UI - requires async refactor")
```

While list_files() shows:
```python
def list_files(self, filespec: str = "") -> List[Tuple[str, int, bool]]:
    if hasattr(self.backend, 'sandboxed_fs'):
        pattern = filespec.strip().strip('"').strip("'") if filespec else None
        files = self.backend.sandboxed_fs.list_files(pattern)
```

This indicates list_files() depends on backend.sandboxed_fs existing, but there's no documentation about what backend.sandboxed_fs is or how it relates to src/filesystem/sandboxed_fs.py's SandboxedFileSystemProvider.

---

#### code_vs_comment

**Description:** FileIO class docstring describes usage pattern that doesn't match actual architecture

**Affected files:**
- `src/file_io.py`

**Details:**
FileIO docstring says:
"Different UIs provide different implementations:
- Local UIs (TK/Curses/CLI): RealFileIO (direct filesystem)
- Web UI: SandboxedFileIO (browser localStorage)"

But SandboxedFileIO.__init__() takes a 'backend' parameter and delegates to backend.sandboxed_fs, suggesting it's a wrapper rather than a direct implementation. The docstring implies SandboxedFileIO directly implements localStorage access, but the code shows it's an adapter to another abstraction layer.

---

#### code_vs_documentation

**Description:** InMemoryFileHandle.flush() implementation doesn't match typical flush semantics

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
The flush() method is documented as 'Flush write buffers' but implementation shows:
```python
def flush(self):
    """Flush write buffers."""
    # StringIO/BytesIO have flush() methods (no-ops) - hasattr check for safety
    if hasattr(self.file_obj, 'flush'):
        self.file_obj.flush()
```

The comment admits StringIO/BytesIO flush() are no-ops, but doesn't actually flush to the virtual filesystem. Content is only saved on close():
```python
def close(self):
    if not self.closed:
        if 'w' in self.mode or 'a' in self.mode or '+' in self.mode:
            # Save content back to virtual filesystem
            self.file_obj.seek(0)
            content = self.file_obj.read()
            self.fs_provider._save_file_content(self.filename, content)
```

This means flush() doesn't actually persist changes, which could be unexpected behavior.

---

#### code_vs_documentation

**Description:** SandboxedFileIO claims to use browser localStorage but SandboxedFileSystemProvider uses in-memory storage

**Affected files:**
- `src/file_io.py`
- `src/filesystem/sandboxed_fs.py`

**Details:**
SandboxedFileIO docstring says:
"Sandboxed file operations for web UI.

Designed for browser localStorage file storage with 'mbasic_file_' prefix.
No access to server filesystem - all files are client-side only."

But SandboxedFileSystemProvider docstring says:
"Sandboxed in-memory filesystem for web UI.

Features:
- All files stored in memory (no disk access)"

And uses class variable:
```python
_user_filesystems: Dict[str, Dict[str, Union[str, bytes]]] = {}
```

This is Python memory, not browser localStorage. The files would be lost on server restart. The documentation claims localStorage persistence but implementation is volatile memory.

---

#### code_vs_comment

**Description:** Docstring claims GOTO/GOSUB are not supported in immediate mode, but code does not explicitly prevent them

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The _show_help() method states:
"• GOTO, GOSUB, and control flow statements are not supported"

However, the execute() method does not check for or reject GOTO/GOSUB statements. It simply executes whatever statement is provided through execute_statement(). There is no validation that prevents control flow statements from being attempted.

---

#### code_vs_comment

**Description:** Comment says 'DO NOT execute when status is: waiting_for_input' but can_execute_immediate() returns True when input_prompt is not None

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The class docstring states:
"DO NOT execute when status is:
- 'waiting_for_input' - Program is waiting for INPUT (use normal input instead)"

But can_execute_immediate() returns True when waiting for input:
"return (self.runtime.halted or
        state.error_info is not None or
        state.input_prompt is not None)"

The condition 'state.input_prompt is not None' means the program IS waiting for input, yet the function returns True (safe to execute), contradicting the docstring.

---

#### code_vs_comment

**Description:** Comment claims RENUM uses AST-based approach but implementation delegates to ui_helpers without showing AST usage

**Affected files:**
- `src/interactive.py`

**Details:**
Comment in cmd_renum() says:
"Delegates to renum_program() from ui_helpers, which uses an AST-based approach:
1. Parse program to AST
2. Build line number mapping (old -> new)
3. Walk AST and update all line number references (via _renum_statement callback)
4. Serialize AST back to source"

But the actual implementation just calls:
old_lines, line_map = renum_program(
    self.program,
    args,
    self._renum_statement,
    self.program_runtime
)

The comment describes the internal workings of renum_program() which is in a different file (ui_helpers), making it unclear if this is documentation or implementation detail.

---

#### code_vs_comment

**Description:** Comment says 'Only AUTO and EDIT are true meta-commands' but then lists many other commands

**Affected files:**
- `src/interactive.py`

**Details:**
In execute_command() method:
Comment says: "Meta-commands (editor commands that manipulate program source)
Only AUTO and EDIT are true meta-commands that can't be parsed - they're
handled specially below. Everything else goes through parser as immediate mode."

But then the code has special handling for:
- AUTO (handled specially)
- EDIT (handled specially)
- Empty command (handled specially)
- Everything else goes to execute_immediate()

The comment is accurate but could be clearer that AUTO/EDIT are the only ones that bypass the parser entirely.

---

#### code_vs_comment

**Description:** Comment about readline Ctrl+A binding conflicts with actual behavior

**Affected files:**
- `src/interactive.py`

**Details:**
In _setup_readline() method:
Comment says: "Bind Ctrl+A to insert literal \x01 character instead of moving cursor
This overrides default Ctrl+A (beginning-of-line). The literal character
appears in input string where it's detected for edit mode (see start() method)"

Code does:
readline.parse_and_bind('Control-a: self-insert')

But 'self-insert' in readline inserts the character that was typed, not a literal \x01. The actual \x01 comes from the terminal sending Ctrl+A as ASCII 0x01, which readline then inserts. The comment makes it sound like the binding creates the \x01, when really it just stops readline from interpreting it as beginning-of-line.

---

#### code_vs_comment

**Description:** Docstring for cmd_delete() delegates to ui_helpers but doesn't mention error handling differences

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring says:
"Delegates to ui_helpers.delete_lines_from_program() which handles:
- Parsing the delete range syntax
- Removing lines from program manager
- Updating runtime statement table if program is loaded"

But the implementation wraps the call in try/except:
try:
    delete_lines_from_program(self, args, self.program_runtime)
except ValueError as e:
    print(f"?{e}")
except Exception as e:
    print(f"?Syntax error")

The docstring doesn't mention that ValueError is caught and printed, while other exceptions are converted to "?Syntax error". This error handling behavior is important for understanding how the command works.

---

#### code_internal_inconsistency

**Description:** Inconsistent error handling between cmd_save/cmd_load and cmd_merge

**Affected files:**
- `src/interactive.py`

**Details:**
cmd_save() and cmd_load() use:
try:
    # operation
except FileNotFoundError:
    print(f"?File not found: {filename}")
except Exception as e:
    print(f"?{type(e).__name__}: {e}")

cmd_merge() uses:
try:
    # operation
except FileNotFoundError:
    print(f"?File not found: {filename}")
except Exception as e:
    print(f"?{type(e).__name__}: {e}")

Both are identical, but cmd_chain() uses different error handling:
except FileNotFoundError:
    print(f"?File not found: {filename}")
except ChainException:
    raise
except Exception as e:
    print_error(e, self.program_runtime if hasattr(self, 'program_runtime') else None)

The inconsistency is that cmd_chain uses print_error() while others use direct print(). This may be intentional (chain runs during execution) but creates inconsistent error reporting.

---

#### code_vs_comment_conflict

**Description:** Comment claims immediate mode does NOT support GOTO/GOSUB, but the code only saves and restores PC without actually preventing GOTO/GOSUB execution

**Affected files:**
- `src/interactive.py`

**Details:**
Comment states: "Immediate mode does NOT support GOTO/GOSUB (see help text), so any PC changes from statements are not meaningful"

However, the code executes statements without any restriction:
for stmt in line_node.statements:
    interpreter.execute_statement(stmt)

The code saves/restores PC to preserve stopped program position, but doesn't actually prevent GOTO/GOSUB from executing. If GOTO/GOSUB are truly unsupported in immediate mode, there should be validation or error handling to prevent their execution.

---

#### code_vs_comment

**Description:** Comment claims skip_next_breakpoint_check prevents re-triggering the same breakpoint immediately, but code shows it's set AFTER hitting a breakpoint and cleared when continuing past it

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 52-53: 'skip_next_breakpoint_check: bool = False  # Allows execution past a breakpoint after stopping on it
                                               # (prevents re-triggering the same breakpoint immediately)'

But code at lines 330-335 shows:
'if at_breakpoint:
    if not self.state.skip_next_breakpoint_check:
        self.runtime.halted = True
        self.state.skip_next_breakpoint_check = True
        return self.state
    else:
        self.state.skip_next_breakpoint_check = False'

The flag is set to True when stopping at a breakpoint, then cleared when passing it again. This means it allows ONE execution past the breakpoint after stopping, not 'prevents re-triggering immediately'.

---

#### code_vs_comment

**Description:** Comment in execute_next says 'NEXT I, J, K closes I first, then J, then K' but this is backwards - it should say 'processes I first, then J, then K' since closing happens in reverse order

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 1088: '# Process variables in order: NEXT I, J, K closes I first, then J, then K'

This is misleading. The code processes variables left-to-right (I, then J, then K), but 'closes' suggests popping from a stack, which would be reverse order. The actual behavior is: increment I and check if it continues (if so, jump back and skip J, K). If I finishes, pop I's loop, then process J, etc. The comment should say 'processes' not 'closes' to avoid confusion with stack operations.

---

#### code_vs_comment

**Description:** Comment says 'OLD EXECUTION METHODS REMOVED (v1.0.300)' but doesn't specify what version the current code is, making it unclear if this is historical or current

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 577-581: '# OLD EXECUTION METHODS REMOVED (v1.0.300)
    # run_from_current(), _run_loop(), step_once() removed
    # These used old current_line/next_line fields
    # Replaced by tick_pc() and PC-based execution
    # CONT command now uses tick() directly'

The file header says 'MBASIC 5.21 Interpreter' (line 2), but the comment references v1.0.300. Are these different versioning schemes? Is v1.0.300 a component version while 5.21 is the MBASIC language version? This needs clarification.

---

#### code_vs_comment

**Description:** Comment in _execute_next_single says 'return_stmt is 0-indexed offset. Valid values are 0 to len(statements)' but then says 'return_stmt == len(statements) means FOR was last statement' which contradicts 0-indexed terminology

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at lines 1149-1152: '# return_stmt is 0-indexed offset. Valid values are 0 to len(statements).
            # return_stmt == len(statements) means FOR was last statement (continue at next line).
            # return_stmt > len(statements) is invalid (statement was deleted).'

If return_stmt is 0-indexed and there are N statements (indices 0 to N-1), then return_stmt == N is not a valid index into the statements array. The comment should clarify that return_stmt can be one-past-the-end to indicate 'continue at next line', which is a special sentinel value, not a valid statement index.

---

#### code_vs_comment

**Description:** Comment says RESUME 0 and RESUME have identical meaning, but code treats them differently

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line ~1050 states:
# RESUME or RESUME 0 - retry the statement that caused the error
# Both forms are valid BASIC syntax with identical meaning

However, the code implementation treats them differently:
if stmt.line_number is None or stmt.line_number == 0:
    # RESUME or RESUME 0 - retry the statement that caused the error

The condition 'stmt.line_number is None' handles RESUME (no argument), while 'stmt.line_number == 0' handles RESUME 0 (explicit zero). These are logically equivalent in the condition, but the comment implies they should be treated identically when in fact the parser may distinguish them.

---

#### code_vs_comment

**Description:** WEND comment describes popping loop before jumping, but this may cause issues with nested loops

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_wend() at line ~1020, comment states:
# Pop the loop from the stack BEFORE jumping back to WHILE.
# The WHILE will re-push if the condition is still true, or skip the
# loop body if the condition is now false. This ensures clean stack state.

This implementation pops the loop info before jumping back to WHILE. However, if the WHILE condition is true and re-pushes, this creates a new loop entry. If the condition is false, the WHILE skips to after WEND. This seems correct, but the comment doesn't explain what happens if there's an error or GOTO during the WHILE re-evaluation - the loop stack state could become inconsistent.

---

#### code_vs_comment

**Description:** INPUT statement comment describes state machine behavior but doesn't document all state variables

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_input() at line ~1410, comment states:
# In tick-based execution mode, this may transition to 'waiting_for_input' state
# instead of blocking. When input is provided via provide_input(), execution
# resumes from the input buffer.

The code sets multiple state variables:
self.state.input_prompt = full_prompt
self.state.input_variables = stmt.variables
self.state.input_file_number = None

But the comment doesn't document that input_variables and input_file_number are also part of the state machine. Additionally, the code clears these at the end but doesn't explain when/how they're used during resumption.

---

#### code_vs_comment

**Description:** CLEAR comment says it closes all files but code doesn't handle close errors gracefully

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_clear() at line ~1270, comment states:
# Close all open files

The code implementation:
for file_num in list(self.runtime.files.keys()):
    try:
        file_obj = self.runtime.files[file_num]
        if hasattr(file_obj, 'close'):
            file_obj.close()
    except:
        pass

The bare 'except: pass' silently ignores all errors. The comment doesn't mention this error handling behavior. If a file close fails (e.g., disk full, permission error), the user has no way to know. This could lead to data loss or corruption.

---

#### code_vs_comment

**Description:** MID$ assignment docstring incomplete - doesn't document what happens when length parameter is omitted

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_midassignment() at line ~2120, docstring states:
Syntax: MID$(string_var, start, length) = value

However, MBASIC allows MID$(string_var, start) = value (length omitted), which replaces from start to end of string or end of value, whichever is shorter. The code evaluates stmt.length, but doesn't document or handle the case where length might be None or omitted. This could cause a runtime error if the parser allows omitting length.

---

#### code_vs_comment

**Description:** Comment claims CONT cannot resume after Ctrl+C Break, but the code doesn't actually check what caused the stop

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment in execute_cont says:
"Note: Ctrl+C (Break) does not set stopped flag, so CONT cannot resume after Break."

However, the code only checks:
if not self.runtime.stopped:
    raise RuntimeError("Can't continue - no program stopped")

The comment describes a limitation but the code doesn't distinguish between STOP and Break - it only checks the stopped flag. The comment may be describing behavior elsewhere in the codebase, but within this function there's no special handling for Break vs STOP.

---

#### code_vs_comment

**Description:** Docstring for execute_stop says 'npc is set by statement execution flow' but doesn't explain what npc is or where it's set

**Affected files:**
- `src/interpreter.py`

**Details:**
The docstring comment states:
"# Save PC position for CONT
# npc is set by statement execution flow to point to next statement
self.runtime.stop_pc = self.runtime.npc"

The comment references 'npc' (next program counter) but this variable is not defined or used anywhere in the visible code. The comment assumes knowledge of implementation details not present in this code section. This could confuse maintainers.

---

#### code_vs_comment

**Description:** MID$ assignment comment claims it calculates minimum of three values, but the actual calculation may not match the description

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment states:
"# Calculate how many characters to actually replace
# This is the minimum of: length parameter, length of new_value, and available space in string
chars_to_replace = min(length, len(new_value), len(current_value) - start_idx)"

The code does take the minimum of these three values, but the comment doesn't explain the semantic meaning: 'length' is how many chars to replace, 'len(new_value)' limits replacement to available replacement text, and 'len(current_value) - start_idx' prevents going past string end. The comment is technically accurate but could be clearer about why this is the correct behavior.

---

#### code_vs_documentation

**Description:** GUIIOHandler is not exported in __init__.py but is documented as a public module

**Affected files:**
- `src/iohandler/__init__.py`
- `src/iohandler/gui.py`

**Details:**
src/iohandler/__init__.py exports: __all__ = ['IOHandler', 'ConsoleIOHandler', 'CursesIOHandler']

But src/iohandler/gui.py exists and contains GUIIOHandler class with full documentation suggesting it should be importable from the package.

---

#### code_vs_documentation

**Description:** WebIOHandler is not exported in __init__.py but is a complete implementation

**Affected files:**
- `src/iohandler/__init__.py`
- `src/iohandler/web_io.py`

**Details:**
src/iohandler/__init__.py exports: __all__ = ['IOHandler', 'ConsoleIOHandler', 'CursesIOHandler']

But src/iohandler/web_io.py exists with WebIOHandler class that is a full implementation for NiceGUI web components.

---

#### code_vs_comment

**Description:** Comment claims KeywordCaseManager exists for complex policies but code uses SimpleKeywordCase

**Affected files:**
- `src/lexer.py`

**Details:**
In src/lexer.py line ~40:
        # Keyword case handler - uses SimpleKeywordCase (simple force-based policies only)
        # Note: KeywordCaseManager class exists for more complex policies (first_wins, preserve)
        self.keyword_case_manager = keyword_case_manager or SimpleKeywordCase(policy="force_lower")

However, src/keyword_case_manager.py shows KeywordCaseManager DOES support first_wins and preserve policies via CaseKeeperTable. The comment suggests a limitation that doesn't exist.

---

#### code_vs_comment

**Description:** error() method uses color_pair(4) without initialization or documentation

**Affected files:**
- `src/iohandler/curses_io.py`

**Details:**
In curses_io.py error() method:
                if curses.has_colors():
                    self.output_win.addstr(message, curses.color_pair(4))

The code assumes color_pair(4) is initialized and represents red, but:
1. CursesIOHandler.__init__() doesn't initialize any color pairs
2. No documentation explains what color_pair(4) should be
3. If color pairs aren't initialized, this will fail or show wrong colors

---

#### code_vs_comment

**Description:** Module docstring says 'Similar to variable case handling' but no variable case handling code is shown

**Affected files:**
- `src/keyword_case_manager.py`

**Details:**
keyword_case_manager.py docstring:
"""Keyword Case Management - Single source of truth for keyword display case

Similar to variable case handling, maintains a table mapping normalized (lowercase)
keywords to their display case based on the configured policy."""

This references 'variable case handling' as if it's a parallel system, but no variable case handling code is provided in the files. This may reference code not included in the analysis.

---

#### code_vs_comment

**Description:** Comment claims APOSTROPHE ends the current statement but not the line, but code implementation treats it as ending the line

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~100 states:
"Note: APOSTROPHE starts a comment statement and ends the current statement,
but not the line itself (the comment content continues on the same line).
This allows comment statements to be preserved in the AST."

However, in parse_line() at line ~300, the code breaks after parsing a comment:
"elif self.match(TokenType.REM, TokenType.REMARK, TokenType.APOSTROPHE):
    # Allow REM/REMARK/' without colon after statement (standard MBASIC)
    # These consume rest of line as a comment
    stmt = self.parse_remark()
    if stmt:
        statements.append(stmt)
    break  # Comment ends the line"

The 'break' statement ends the line parsing, contradicting the comment that says APOSTROPHE doesn't end the line.

---

#### code_vs_comment

**Description:** Comment about MID$ statement detection describes complex lookahead but implementation may have edge cases

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~650 states:
"# MID$ statement (substring assignment)
# Detect MID$ used as statement: MID$(var, start, len) = value"

And later:
"# Look ahead to distinguish MID$ statement from MID$ function
# MID$ statement has pattern: MID$ ( ... ) =
# MID$ is tokenized as single MID token ($ is part of the keyword)
# Complex lookahead: scan past parentheses (tracking depth) to find = sign"

However, the implementation uses a try-except block that catches all exceptions:
"try:
    ...
except:
    pass"

This broad exception handling could hide bugs and doesn't match the comment's description of 'complex lookahead' - it's more like 'speculative parsing with fallback'.

---

#### code_vs_comment

**Description:** Comment claims both comma and semicolon after INPUT prompt show '?' but code doesn't track separator type

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~35 states:
"# Note: In MBASIC, both comma and semicolon after prompt show "?" prompt.
# The separator type doesn't affect behavior (both display "?"), so we just
# consume it without tracking."

However, this contradicts the suppress_question flag logic which specifically handles INPUT; (semicolon immediately after INPUT keyword) to suppress the '?' prompt. The comment suggests separator after prompt doesn't matter, but the code has special handling for semicolon position.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of DEF type suffix application in DIM vs FOR/NEXT statements

**Affected files:**
- `src/parser.py`

**Details:**
In parse_dim() (line ~1180):
"# Determine type suffix based on explicit suffix or DEF type
# If no explicit suffix, check DEF type map and add appropriate suffix
if name and name[-1] not in '$%!#':
    first_letter = name[0].lower()
    if first_letter in self.def_type_map:
        var_type = self.def_type_map[first_letter]
        # Append appropriate suffix based on DEF type
        if var_type == TypeInfo.STRING:
            name = name + '$'"

This modifies the name string by appending the suffix.

However, in parse_for() (line ~880) and parse_next() (line ~950), the code checks def_type_map but assigns to type_suffix variable without modifying the name:
"if not type_suffix:
    first_letter = var_name[0].lower()
    if first_letter in self.def_type_map:
        var_type = self.def_type_map[first_letter]
        if var_type == TypeInfo.STRING:
            type_suffix = '$'"

This inconsistency means DIM modifies the variable name while FOR/NEXT keep name and suffix separate.

---

#### code_vs_comment

**Description:** Comment about REM after THEN line_number contradicts general statement separator rules

**Affected files:**
- `src/parser.py`

**Details:**
In parse_if() at line ~780:
"# Allow optional REM after THEN line_number (without colon)
# Syntax: IF condition THEN 100 REM comment
if self.match(TokenType.REM, TokenType.REMARK):
    # REM consumes rest of line, we're done
    self.parse_remark()
    # Don't check for ELSE since REM consumed the line"

This special-cases REM to not require a colon separator after 'THEN 100', but elsewhere in the code (like after GOTO/GOSUB line numbers), there's no such special handling. This inconsistency in statement separator requirements is not explained.

---

#### code_vs_comment

**Description:** parse_width docstring claims statement is 'no-op in execution' but this is parser code, not executor

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says: 'Both parameters are parsed but the statement is a no-op in execution (see execute_width). Modern terminals handle line width automatically.'

This comment belongs in the executor, not the parser. The parser's job is just to parse the syntax, not to describe execution behavior. The reference to 'execute_width' suggests this docstring was copied from or intended for the executor module.

---

#### code_vs_comment

**Description:** parse_call comment about argument parsing contradicts implementation details

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says: 'CALL ROUTINE(X,Y) - Call with arguments (fully parsed/supported)'

But the implementation comment says: '# Note: CALL ROUTINE(X,Y) is parsed as VariableNode with subscripts'

This reveals that the 'full support' is actually a workaround where function-call-like syntax is initially misparsed as array access, then corrected. The docstring's claim of 'fully parsed/supported' is misleading about the implementation approach.

---

#### code_vs_comment

**Description:** PC class docstring describes stmt_offset as '0-based index' but example shows confusion between offset and index terminology

**Affected files:**
- `src/pc.py`

**Details:**
Docstring says:
"The stmt_offset is a 0-based index into the statements list for a line."
Then example says:
"PC(10, 2)  - Third statement on line 10 (offset 2 = index 2)"

This is redundant/confusing - if stmt_offset IS a 0-based index, then saying 'offset 2 = index 2' is tautological. The comment should clarify that offset 2 means the third statement (since 0-based), not restate that offset equals index.

---

#### code_vs_comment

**Description:** Function serialize_statement has fallback comment that doesn't match actual fallback behavior

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_statement method:
else:
    # Fallback: Use pretty printing from ui_helpers
    from src.ui.ui_helpers import serialize_statement
    return " " + serialize_statement(stmt)

The fallback adds a leading space, but the comment doesn't mention this. Other statement serializers don't add leading spaces - they rely on emit_token for spacing. This inconsistency could cause double-spacing issues.

---

#### documentation_inconsistency

**Description:** Module docstring claims to track position conflicts but doesn't explain what causes them or how they're resolved

**Affected files:**
- `src/position_serializer.py`

**Details:**
Module docstring says:
"Tracks position conflicts when actual output column doesn't match expected token column (conflicts occur during AST modifications)."

But the PositionConflict class and conflict tracking mechanism are not explained. The docstring should clarify:
1. What AST modifications cause conflicts
2. How conflicts are resolved (the 'Strategy: Add single space' approach)
3. Whether conflicts are errors or just warnings

---

#### code_vs_comment

**Description:** Comment in emit_keyword says it uses 'keyword case table' but implementation uses 'keyword case manager'

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring says:
"Emit a keyword token with case from keyword case table."

But code does:
if self.keyword_case_manager:
    keyword_with_case = self.keyword_case_manager.get_display_case(keyword)

The terminology is inconsistent - is it a 'table' or a 'manager'? The __init__ docstring correctly calls it 'KeywordCaseManager instance', so the emit_keyword docstring should match.

---

#### code_vs_comment

**Description:** Function _adjust_statement_positions has case for 'AssignmentStatementNode' but serialize_statement has 'LetStatementNode'

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_statement:
if stmt_type == 'LetStatementNode':
    return self.serialize_let_statement(stmt)

But in _adjust_statement_positions:
if stmt_type == 'AssignmentStatementNode':
    _adjust_expression_positions(stmt.variable, offset)
    _adjust_expression_positions(stmt.expression, offset)

These appear to be the same statement type with different names. This inconsistency could cause position adjustments to fail for LET statements during renumbering.

---

#### code_vs_comment

**Description:** check_array_allocation docstring says it 'Raises RuntimeError if allocation would exceed limits' but also 'Returns estimated size in bytes'

**Affected files:**
- `src/resource_limits.py`

**Details:**
The function both checks limits (raising errors) and returns size. The name 'check_array_allocation' suggests it only validates, but it also computes the size. This dual purpose should be clarified - perhaps rename to 'validate_and_compute_array_size' or split into two functions.

---

#### code_vs_comment

**Description:** Docstring for get_variable() states token is REQUIRED but implementation allows token=None in some cases

**Affected files:**
- `src/runtime.py`

**Details:**
Docstring says:
"This method MUST be called with a token for normal program execution."
"Args:
    token: REQUIRED - Token object with line and position info for tracking."

But implementation has:
```python
if token is None:
    raise ValueError("get_variable() requires token parameter. Use get_variable_for_debugger() instead.")
```

However, later in the code:
```python
tracking_info = {
    'line': getattr(token, 'line', self.pc.line_num if self.pc and not self.pc.halted() else None),
    'position': getattr(token, 'position', None),
    'timestamp': time.perf_counter()
}
```

The getattr with fallback suggests token could be None or missing attributes, contradicting the REQUIRED claim and the ValueError check.

---

#### code_vs_comment

**Description:** Comment in _variables storage says 'line -1 indicates debugger/prompt/internal set' but set_variable() uses line=-1 for debugger_set=True

**Affected files:**
- `src/runtime.py`

**Details:**
Comment at line ~50:
"# Each variable is stored as: name_with_suffix -> {'value': val, 'last_read': {...}, 'last_write': {...}, 'original_case': str, 'case_variants': [...]}
# Note: line -1 in last_write indicates debugger/prompt/internal set (not from program execution)"

But in set_variable_raw() implementation:
```python
class FakeToken:
    def __init__(self):
        self.line = -1
        self.position = None

fake_token = FakeToken()

# Call set_variable for uniform handling
self.set_variable(name, type_suffix, value, token=fake_token)
```

This creates a token with line=-1 for internal/system variables (like ERR%, ERL%), which is different from debugger_set=True. The comment suggests line=-1 is only for debugger sets, but it's also used for system variable initialization.

---

#### code_vs_comment

**Description:** Comment says 'Error PC and details are stored in ErrorInfo (interpreter.py state)' but Runtime class has error_handler attributes

**Affected files:**
- `src/runtime.py`

**Details:**
Comment at line ~130:
"# Note: Actual error state (occurred/active) is tracked in state.error_info, not here
# Runtime only stores the registered handler location, not whether an error occurred
# Error PC and details are stored in ErrorInfo (interpreter.py state)
# ERL%, ERS%, and ERR% system variables are set from ErrorInfo"

But then the code initializes:
```python
# Initialize system variables ERR% and ERL% to 0
# These are integer type variables set by error handling code
self.set_variable_raw('err%', 0)
self.set_variable_raw('erl%', 0)
```

The comment says ERR% and ERL% are set from ErrorInfo, but the code shows they're stored as regular variables in Runtime. This is confusing about where error state actually lives.

---

#### code_vs_comment

**Description:** Docstring for _resolve_variable_name() says 'For special cases like system variables (ERR%, ERL%), see set_variable_raw()' but set_variable_raw() calls set_variable() internally

**Affected files:**
- `src/runtime.py`

**Details:**
Docstring for _resolve_variable_name():
"This is the standard method for determining the storage key for a variable,
applying BASIC type resolution rules (explicit suffix > DEF type > default).
For special cases like system variables (ERR%, ERL%), see set_variable_raw()."

But set_variable_raw() implementation:
```python
def set_variable_raw(self, full_name, value):
    """Set variable by full name (e.g., 'err%', 'erl%').
    ...
    Internally calls set_variable() for uniform handling with line=-1 token.
    """
    # Split the variable name from the type suffix using utility function
    name, type_suffix = split_variable_name_and_suffix(full_name)
    ...
    # Call set_variable for uniform handling
    self.set_variable(name, type_suffix, value, token=fake_token)
```

So set_variable_raw() is not a special case that bypasses _resolve_variable_name() - it still goes through set_variable() which uses _resolve_variable_name(). The comment is misleading.

---

#### code_vs_comment

**Description:** Inconsistency in get_execution_stack() docstring regarding 'from_line' field for GOSUB entries

**Affected files:**
- `src/runtime.py`

**Details:**
The docstring states:
"For GOSUB calls:
{
    'type': 'GOSUB',
    'from_line': 60,      # Line to return to (despite misleading name)
    'return_line': 60,    # Line to return to
    'return_stmt': 0      # Statement offset to return to
}"

But the actual code implementation is:
result.append({
    'type': 'GOSUB',
    'from_line': entry.get('return_line', 0),  # Line to return to
    'return_line': entry.get('return_line', 0),
    'return_stmt': entry.get('return_stmt', 0)  # Statement offset
})

The docstring acknowledges 'from_line' is misleading but still includes it in the documented return format. The field name suggests 'line where GOSUB was called from' but the comment and implementation show it's actually 'line to return to', making it redundant with 'return_line'.

---

#### documentation_inconsistency

**Description:** Comment claims 'interpreter.max_execution_time and interpreter.debug_mode are available' but these settings are not defined in SETTING_DEFINITIONS

**Affected files:**
- `src/settings_definitions.py`

**Details:**
Comment at line ~150 in settings_definitions.py:
# Note: interpreter.max_execution_time and interpreter.debug_mode are available
# but not shown in UI - edit settings file directly if needed

However, SETTING_DEFINITIONS dict only contains:
- variables.case_conflict
- variables.show_types_in_window
- keywords.case_style
- editor.auto_number
- editor.auto_number_start
- editor.auto_number_step

No 'interpreter.max_execution_time' or 'interpreter.debug_mode' settings exist.

---

#### code_vs_documentation

**Description:** settings.py docstring describes scope precedence as 'file > project > global > default' but SettingScope enum only defines GLOBAL, PROJECT, FILE without clear precedence documentation

**Affected files:**
- `src/settings.py`
- `src/settings_definitions.py`

**Details:**
src/settings.py line 5:
"""Handles loading, saving, and accessing user settings with scope precedence.
Supports global settings (~/.mbasic/settings.json) and project settings (.mbasic/settings.json)."""

Line 23:
"""Manages user settings with scope precedence (file > project > global > default)"""

But in settings_definitions.py, SettingScope enum (lines 18-22) only has:
class SettingScope(Enum):
    GLOBAL = "global"      # ~/.mbasic/settings.json
    PROJECT = "project"    # .mbasic/settings.json in project dir
    FILE = "file"          # Per-file metadata

No documentation of precedence order in the enum itself.

---

#### documentation_inconsistency

**Description:** keywords.case_style setting has choice 'force_capitalize' but simple_keyword_case.py docstring says 'Capitalize first letter (modern style)' which is ambiguous

**Affected files:**
- `src/simple_keyword_case.py`
- `src/settings_definitions.py`

**Details:**
In settings_definitions.py (line ~95):
choices=["force_lower", "force_upper", "force_capitalize"],
description="How to handle keyword case in source code",
help_text="lowercase (MBASIC 5.21), UPPERCASE (classic), or Capitalize (modern)",

In simple_keyword_case.py (line ~11):
- force_capitalize: Capitalize first letter (modern style)

The term 'Capitalize first letter' could mean either 'Print' or 'PRINT' depending on interpretation. The code uses keyword.capitalize() which would produce 'Print', but this should be explicitly documented.

---

#### code_vs_comment

**Description:** Comment says 'Future: per-file settings' but FILE scope is already implemented in SettingScope enum and used in code

**Affected files:**
- `src/settings.py`

**Details:**
In settings.py line 32:
self.file_settings: Dict[str, Any] = {}  # Future: per-file settings

But in settings_definitions.py, SettingScope.FILE is already defined and used:
class SettingScope(Enum):
    FILE = "file"          # Per-file metadata

And in settings.py, the set() method already handles FILE scope (line ~186):
elif scope == SettingScope.FILE:
    self.file_settings[key] = value

The comment 'Future:' is outdated - FILE scope is already partially implemented.

---

#### code_vs_documentation

**Description:** CLIBackend imports and uses InteractiveMode but InteractiveMode is not shown in the provided source files

**Affected files:**
- `src/ui/cli.py`

**Details:**
In cli.py (line ~42):
from interactive import InteractiveMode

And line ~47:
self.interactive = InteractiveMode(io_handler)

The 'interactive' module is imported but not provided in the source files. This makes it impossible to verify if the integration is correct or if there are inconsistencies between CLIBackend's interface and InteractiveMode's implementation.

---

#### code_vs_documentation

**Description:** CLIBackend imports cli_debug module that is not shown in the provided source files

**Affected files:**
- `src/ui/cli.py`

**Details:**
In cli.py (lines ~53-54):
from .cli_debug import add_debug_commands
self.debugger = add_debug_commands(self.interactive)

The cli_debug module is imported and used but not provided in the source files. This creates an incomplete picture of the CLI backend's capabilities.

---

#### Code vs Comment conflict

**Description:** Comment says 'without buttons' but code creates footer with keyboard shortcuts

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
In _create_body() method at line creating listbox:
# Create scrollable list (without buttons)
listbox = urwid.ListBox(urwid.SimpleFocusListWalker(content))

# Create footer with keyboard shortcuts hint
footer_text = urwid.Text("Enter=OK  ESC/^P=Cancel  ^A=Apply  ^R=Reset", align='center')

The comment 'without buttons' is misleading - it creates a footer with keyboard shortcuts that act as virtual buttons. The comment appears outdated from a refactoring where physical button widgets were removed.

---

#### Code vs Documentation inconsistency

**Description:** BREAK command documentation incomplete - missing reference to program attribute

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
In cmd_break() method, the code checks:
if line_num in self.interactive.program.lines:

But the docstring for CLIDebugger.__init__() only mentions:
Args:
    interactive_mode: The InteractiveMode instance to extend

It doesn't document that interactive_mode must have a 'program' attribute with a 'lines' dictionary. This is an implicit dependency not documented in the class or method documentation.

---

#### Code vs Documentation inconsistency

**Description:** cmd_step() references program_interpreter.state.program_ended but also checks program_interpreter existence inconsistently

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
In cmd_step() method:
if not self.interactive.program_runtime:
    self.interactive.io_handler.output("No program running. Use RUN first.")
    return

But later in the same method:
if self.interactive.program_interpreter.state.program_ended:

The code checks program_runtime exists but then accesses program_interpreter without checking. This inconsistency suggests either:
1. Both should be checked, or
2. They're always synchronized (not documented)
3. There's a potential AttributeError bug

---

#### Code vs Documentation inconsistency

**Description:** enhance_run_command() modifies cmd_run but doesn't document the signature change

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
Original method signature is preserved in docstring:
def enhanced_run(start_line=None):
    """Enhanced RUN with breakpoint support

    Args:
        start_line: Optional line number to start execution at
    """

But there's no documentation that:
1. The original cmd_run is stored and called
2. What the original cmd_run signature is expected to be
3. Whether start_line parameter is actually passed through (code shows it is: original_run(start_line=start_line))
4. The relationship between this and _install_breakpoint_handler()

---

#### code_vs_comment

**Description:** Comment claims line numbers use variable width but code still uses fixed 5-character formatting

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Class docstring says: 'Note: Line numbers use variable width (not fixed 5 chars) for flexibility with large programs.'

But in _parse_line_numbers method (line ~1050):
line_num_formatted = f"{num_str:>5}"
new_line = f" {line_num_formatted} {rest}"

And again at line ~1090:
line_num_formatted = f"{num_str:>5}"
new_line = f"{status}{line_num_formatted} {rest}"

The code is still using fixed 5-character right-justified formatting (:>5), contradicting the comment about variable width.

---

#### code_vs_comment

**Description:** Multiple comments claim variable-width line numbers but formatting code uses fixed width

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~280: 'Note: Line numbers use variable width (not fixed 5 chars) for flexibility with large programs.'

Comment at line ~320: '# Variable-width line numbers - no need to right-justify'

Comment at line ~330: '# With variable width, check if we're in line number area (before first space after status)'

But the actual formatting in _parse_line_numbers uses:
f"{num_str:>5}" (fixed 5-character right-justified)

And in keypress method line ~460:
'if 1 <= col_in_line <= 6:' suggests fixed 6-column width (status + 5 digits)

---

#### code_vs_comment

**Description:** Format string in _format_line docstring doesn't match implementation

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Docstring at line ~570 says:
'Format: "S<linenum> CODE" (where <linenum> is variable width)'

But the actual implementation creates:
prefix = f"{status}{line_num_str} "

where line_num_str is just str(line_num), which is indeed variable width. However, _parse_line_numbers reformats everything to fixed 5-char width, so the actual format in the editor is 'S     NN CODE' (fixed width), not 'SNN CODE' (variable width).

---

#### code_vs_comment

**Description:** Comment claims ImmediateExecutor will be re-initialized in start() and _run_program(), but _run_program() method does not exist in the provided code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~75: '# Create a proper ImmediateExecutor (will be re-initialized in start() and _run_program())'

The start() method does re-initialize ImmediateExecutor (line ~95), but there is no _run_program() method visible in the code. The actual method is _run_program() which is referenced but not shown in the provided excerpt.

---

#### code_internal_inconsistency

**Description:** Two different CapturingIOHandler classes are created - one inline and one imported

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line ~8: 'from src.immediate_executor import OutputCapturingIOHandler'

Lines ~13-48: A complete CapturingIOHandler class is defined inline with methods like output(), get_and_clear_output(), input(), etc.

Line ~51: 'self.io_handler = CapturingIOHandler()' uses the inline class

Line ~55: 'immediate_io = OutputCapturingIOHandler()' uses the imported class

This creates two different IO handler implementations being used in the same initialization, which could lead to inconsistent behavior.

---

#### code_vs_comment

**Description:** Comment claims _setup_program() is called but this method is not visible in the provided code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Lines ~437-439: 'if not self._setup_program():
    return  # Setup failed (error already displayed)'

The _setup_program() method is called in _debug_step() and _debug_step_line() but is not defined in the visible code excerpt. This could indicate missing code or that the method is defined elsewhere in the file.

---

#### code_vs_comment

**Description:** Comment says 'RUN = CLEAR + GOTO first line (or start_line if specified)' but code behavior differs

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program() method around line 1050:
Comment: '# Reset runtime with current program - RUN = CLEAR + GOTO first line (or start_line if specified)\n# This preserves breakpoints but clears variables'

However, the code calls runtime.reset_for_run() which clears variables, then later sets PC to start_line if specified. The comment suggests this happens atomically as part of 'RUN', but the implementation shows it's a two-step process where start() is called first (which resets PC to first line), then PC is manually overridden if start_line is provided.

---

#### code_vs_comment

**Description:** Comment about preserving PC conflicts with actual conditional logic

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _sync_program_to_runtime() around line 1150:
Comment: '# Restore PC only if execution is running AND not paused at breakpoint\n# (paused programs need PC reset to current breakpoint location)\n# Otherwise ensure halted (don't accidentally start execution)'

The comment says 'paused programs need PC reset to current breakpoint location', but the code in the else branch sets PC to halted_pc(), not to any breakpoint location. The comment implies PC should be set to the breakpoint, but the code just halts it.

---

#### code_vs_comment

**Description:** Comment claims 'Log the command to output pane (not separate immediate history)' but there is no evidence of a separate immediate history feature anywhere in the code

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line comment: '# Log the command to output pane (not separate immediate history)'
This comment suggests there was or could be a separate immediate history, but no such feature exists in the codebase. The comment is misleading.

---

#### code_vs_comment

**Description:** Comment says 'Sync program to runtime (but don't reset PC - keep current execution state)' but the actual behavior and necessity of this is unclear

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment: '# Sync program to runtime (but don't reset PC - keep current execution state)
# This allows LIST to work, but doesn't start execution'
The comment suggests this is specifically to allow LIST to work without affecting execution state, but it's unclear why LIST would need this sync or what _sync_program_to_runtime actually does to the PC.

---

#### code_vs_comment

**Description:** Comment says 'duplicates definition in _run_program - consider extracting to shared location' but this duplication is a code smell that should be addressed

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment: '# (duplicates definition in _run_program - consider extracting to shared location)'
The entire CapturingIOHandler class is defined inline within _execute_immediate, duplicating code from _run_program. This is acknowledged but not fixed, creating maintenance burden.

---

#### code_vs_comment

**Description:** Comment in cmd_renum says 'Need access to InteractiveMode's _renum_statement' but doesn't explain why this private method is being accessed

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment: '# Need access to InteractiveMode's _renum_statement
# Curses UI has self.interpreter which should have interactive_mode'
The code accesses a private method (_renum_statement) from another class without explanation of why this coupling is necessary or whether there should be a public API.

---

#### code_inconsistency

**Description:** Inconsistent error message format across cmd_* methods - some use '?Error' prefix, some don't

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
cmd_save uses: '?Syntax error: filename required' and '?Error saving file:'
cmd_delete uses: '?{e}' and '?Error during delete:'
cmd_renum uses: '?RENUM not available' and '?{e}' and '?Error during renumber:'
cmd_merge uses: '?Syntax error: filename required' and '?Parse error' and '?{e}'
cmd_files uses: '?Error listing files:'
cmd_cont uses: '?Can't continue' and '?Error:'

The error message format is inconsistent - sometimes the exception message is prefixed with '?', sometimes with '?Error:', and the patterns vary.

---

#### code_vs_documentation

**Description:** Help widget footer shows 'U=Back' in one place and 'u=Back' in another, inconsistent capitalization

**Affected files:**
- `src/ui/help_widget.py`
- `src/ui/keybindings.py`

**Details:**
help_widget.py line 72:
self.footer = urwid.Text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search u=Back ESC/Q=Exit ")

help_widget.py line 161:
self.footer.set_text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search U=Back ESC/Q=Exit ")

Line 72 uses lowercase 'u', line 161 uses uppercase 'U' for the same action.

---

#### code_vs_comment

**Description:** Docstring says HelpWidget is 'Urwid-based' and 'curses-specific', but help_macros.py is designed to work with any UI

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
help_widget.py line 1-9:
"""Urwid-based help browser widget for navigating markdown documentation.

Provides:
- Up/Down scrolling through help content
- Enter to follow links
- ESC/Q to exit
- Navigation breadcrumbs
- Search across three-tier help system (/)
"""

help_widget.py line 38:
# HelpWidget is curses-specific (uses urwid), so hardcode 'curses' UI name
self.macros = HelpMacros('curses', help_root)

But help_macros.py is designed to accept any ui_name parameter and load corresponding keybindings. The comment suggests this is a limitation, but it's actually just a choice to hardcode 'curses'.

---

#### code_vs_documentation

**Description:** Keybindings module shows 'Shift+Ctrl+V' for Save As and 'Shift+Ctrl+O' for Recent Files, but these are not documented in the JSON config loading

**Affected files:**
- `src/ui/keybindings.py`
- `src/ui/interactive_menu.py`

**Details:**
keybindings.py line 234-235:
('Shift+Ctrl+V', 'Save As'),
('Shift+Ctrl+O', 'Recent files'),

These appear in KEYBINDINGS_BY_CATEGORY but there's no corresponding _get_key() call or JSON config reference for these bindings. They appear to be hardcoded in the documentation but may not actually work.

---

#### code_vs_documentation

**Description:** Interactive menu shows 'Toggle Breakpoint' with keybinding display but uses hardcoded format conversion instead of loading from JSON

**Affected files:**
- `src/ui/interactive_menu.py`
- `src/ui/keybindings.py`

**Details:**
interactive_menu.py line 30-31:
def fmt_key(display):
    """Convert keybinding display to compact ^X format."""
    if display.startswith('Ctrl+'):
        return '^' + display[5:]
    return display

interactive_menu.py line 48:
(f'Toggle Breakpoint {fmt_key(kb.BREAKPOINT_DISPLAY)}', '_toggle_breakpoint_current_line'),

The menu is using keybindings.py constants (kb.BREAKPOINT_DISPLAY) but then converting them with a local function. This creates a dependency on the format of the display strings from keybindings.py.

---

#### code_vs_comment

**Description:** Comment says 'Search across three-tier help system' but the code only shows two tiers in tier_labels mapping

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
help_widget.py line 8:
- Search across three-tier help system (/)

help_widget.py line 95-98:
tier_labels = {
    'language': '📕 Language',
    'mbasic': '📗 MBASIC',
}

The docstring mentions 'three-tier' but only two tiers are defined in the mapping. The code does handle a third tier ('ui/') but it's not in the tier_labels dict, suggesting incomplete implementation or outdated documentation.

---

#### code_vs_documentation

**Description:** STATUS_BAR_SHORTCUTS shows '^K stack' but STACK_DISPLAY is 'Menu only' with no keyboard shortcut

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
keybindings.py line 103-106:
# Execution stack window (menu only - no dedicated key, step_line uses Ctrl+K)
STACK_KEY = ''  # No keyboard shortcut
STACK_CHAR = ''
STACK_DISPLAY = 'Menu only'

keybindings.py line 260:
STATUS_BAR_SHORTCUTS = "MBASIC - ^F help  ^U menu  ^W vars  ^K stack  Tab cycle  ^Q quit"

The status bar shows '^K stack' but the STACK constants indicate there's no keyboard shortcut and it's menu-only. This is contradictory.

---

#### code_vs_documentation

**Description:** Help browser implements Ctrl+F for in-page search but this keybinding is not documented in tk_keybindings.json

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
tk_help_browser.py line 127-128:
# Make text read-only but allow copy (Ctrl+C) and find (Ctrl+F)
def readonly_key_handler(event):
    # Allow Ctrl+C (copy), Ctrl+A (select all), Ctrl+F (find)
    if event.state & 0x4:  # Control key
        if event.keysym in ('c', 'C', 'a', 'A'):  # Ctrl+C, Ctrl+A
            return  # Allow these
        elif event.keysym in ('f', 'F'):  # Ctrl+F
            self._inpage_search_show()
            return "break"

Line 136:
self.bind("<Control-f>", lambda e: self._inpage_search_show())

tk_keybindings.json has no entry for Ctrl+F in help_browser section

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of link tags - some use 'link_' prefix, some use 'result_link_' prefix, but both are stored in the same link_urls dictionary with potentially overlapping keys

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Line 244:
tag_name = f"link_{self.link_counter}"

Line 330:
tag_name = f"result_link_{self.link_counter}"

Both are stored in self.link_urls and both increment self.link_counter, so there's no actual conflict. However, the naming inconsistency could be confusing. The code checks for both prefixes in _create_context_menu (line 502-503):
for tag in tags:
    if tag.startswith("link_") or tag.startswith("result_link_"):

This is actually consistent behavior, just inconsistent naming convention.

---

#### code_vs_documentation

**Description:** Duplicate entries in keybindings JSON - 'new_program' and 'file_new' both map to Ctrl+N, 'save_file' and 'file_save' both map to Ctrl+S

**Affected files:**
- `src/ui/tk_keybindings.json`

**Details:**
tk_keybindings.json lines 3-9:
"file_new": {
  "keys": ["Ctrl+N"],
  "primary": "Ctrl+N",
  "description": "New file"
},
"new_program": {
  "keys": ["Ctrl+N"],
  "primary": "Ctrl+N",
  "description": "New file"
}

Lines 19-29:
"file_save": {
  "keys": ["Ctrl+S"],
  "primary": "Ctrl+S",
  "description": "Save file"
},
"save_file": {
  "keys": ["Ctrl+S"],
  "primary": "Ctrl+S",
  "description": "Save file"
}

These appear to be duplicate entries with different names for the same action. This could cause confusion about which action name to use in code.

---

#### implementation_inconsistency

**Description:** Inconsistent error handling between _on_apply and _on_cancel methods

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
_on_apply method (lines 193-201):
    try:
        set_setting(key, value, SettingScope.GLOBAL)
    except Exception as e:
        messagebox.showerror(...)
        return False

_on_cancel method (lines 211-217):
    try:
        set_setting(key, value, SettingScope.GLOBAL)
    except Exception:
        pass  # Ignore errors on cancel

The _on_apply method shows error dialogs and stops on failure, while _on_cancel silently ignores all errors. This inconsistency means if settings restoration fails during cancel, the user gets no feedback and settings may be in an inconsistent state.

---

#### code_vs_comment

**Description:** Comment describes 3-pane layout but implementation uses different structure

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Docstring says: '3-pane vertical layout: editor (top), output (middle), immediate mode (bottom)'

But code shows:
- editor_frame with weight=3 (~50%)
- output_frame with weight=2 (~33%)
- immediate_frame with weight=1 (~17%)

The immediate_frame contains only an input line, not a full pane. The comment '# Bottom pane: Immediate Mode - just the input line' contradicts the docstring's description of it as a full pane.

---

#### code_internal_inconsistency

**Description:** Variables window column order inconsistency between setup and usage

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _create_variables_window() at line ~730:
tree = ttk.Treeview(self.variables_window, columns=('Value', 'Type'), show='tree headings')
tree.heading('Value', text='  Value')
tree.heading('Type', text='  Type')

But in _on_variable_heading_click() at line ~780:
if column == '#1':  # Value column (swapped to be first)
    col_x = event.x - self.variables_tree.column('#0', 'width')
elif column == '#2':  # Type column (swapped to be second)

The comment says 'swapped' but the columns are defined in Value, Type order from the start. There's no evidence of swapping.

---

#### missing_implementation

**Description:** Method _edit_array_element is referenced but not shown in code

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_variable_double_click at line ~825:
if 'Array' in value_display:
    # Array variable - edit last accessed element
    self._edit_array_element(variable_display, type_suffix_display, value_display)

The method _edit_array_element is called but its implementation is not included in the provided code. This could be because the file is truncated.

---

#### code_vs_comment

**Description:** Comment says 'No formatting is applied' but code does apply formatting through _refresh_editor

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _refresh_editor() method:
Comment says: "Line numbers are part of the text content as entered by user.\nNo formatting is applied to preserve compatibility with real MBASIC."

But in _on_enter_key() method:
- Line 1234: "# Refresh to sort lines (only if no errors)\n        self._refresh_editor()"
- This sorts/reorders lines, which IS formatting
- The comment at line 1227 says "# Save current program state" followed by _save_editor_to_program() which clears and rebuilds the program, then _refresh_editor() loads it back sorted

---

#### code_vs_comment

**Description:** Inconsistent handling of blank lines between methods

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_enter_key() at line 1234:
Comment: "# At this point, the editor contains only the numbered lines (no blank lines)\n        # because _refresh_editor loads from the program, which filters out blank lines"

But _refresh_editor() at line 1119 does NOT filter blank lines:
"self.editor_text.text.insert(tk.END, line_text + '\n')"
It inserts lines exactly as stored in program.

The filtering happens in _save_editor_to_program() which skips empty lines when parsing, but _refresh_editor() itself doesn't filter - it just loads what's in self.program.

---

#### internal_logic_inconsistency

**Description:** Inconsistent error handling between parse failure paths

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _save_editor_to_program() at lines 1138-1145:
When parse fails: "self.editor_text.set_error(line_num, True, error)\nhad_errors = True"

In _on_enter_key() at lines 1263-1268:
When parse fails: "# Not valid BASIC - don't auto-number, just move to next line\nself.editor_text.text.insert(tk.INSERT, '\n')\nreturn 'break'"

The _on_enter_key() path does NOT call set_error() to mark the line with an error indicator, while _save_editor_to_program() does. This creates inconsistent user feedback - errors are only marked when saving, not when pressing Enter on an invalid line.

---

#### code_vs_comment

**Description:** Comment says 'DON'T save to program yet' but code behavior suggests line should be saved when user moves off it

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _smart_insert_line() method around line 1050:
Comment: '# DON\'T save to program yet - the line is blank and would be filtered out\n# Just position the cursor on the new line so user can start typing\n# The line will be saved when they finish typing and move off it'

However, the _check_line_change() method that handles moving off lines has logic that only triggers sort 'if old_line_num is not None' (line 1000), meaning blank numbered lines (which have no parsed line number) won't trigger save/sort. This creates inconsistency - the comment implies the line will be saved later, but the code won't save blank numbered lines.

---

#### code_vs_comment

**Description:** Comment says 'DON'T sort if just clicking around without editing' but logic may not distinguish clicking from editing

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _check_line_change() method around line 990:
Comment: '# DON\'T sort if just clicking around without editing (old is None means we\'re just tracking)'

However, old_line_num can be None in two cases:
1. First time tracking (just initialized, no previous line)
2. Previous line had no line number

The code treats 'old_line_num is None' as 'just clicking around', but case #2 could be after actual editing (user removed a line number). This may cause missed sorts when user edits a line to remove its number then clicks away.

---

#### code_internal_inconsistency

**Description:** Inconsistent variable naming: 'self.running' vs 'self.is_running'

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Throughout the file, execution state is tracked with 'self.running' (lines 700, 1200, 1300, 1600, etc.).

But in cmd_cont() method (line 1470), code sets 'self.is_running = True' which is a different variable name. This appears to be a typo/bug that would cause CONT to not work properly.

---

#### code_vs_comment

**Description:** Comment says 'DON'T call interpreter.start()' but reasoning may be incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method around line 1580:
Comment: '# NOTE: Don\'t call interpreter.start() because it resets PC!\n# RUN 120 already set PC to line 120, so just clear halted flag'

This assumes RUN 120 was executed, but has_work() could be true for other reasons (like GOTO in immediate mode). The comment's reasoning is specific to one case but the code path handles all cases where has_work() is true.

---

#### code_vs_comment

**Description:** input() docstring says it uses inline input field, but input_line() docstring says it 'always uses modal dialog' - inconsistent behavior description

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
input() docstring: "Used by INPUT statement to read user input (raw string).
Comma-separated parsing happens at interpreter level.
Shows an inline input field below output pane."

input_line() docstring: "Used by LINE INPUT statement for reading entire line as string.
Unlike input(), always uses modal dialog (not inline input field)."

This suggests INPUT uses inline field while LINE INPUT uses modal dialog, but the distinction and reasoning is unclear. Why would LINE INPUT need a modal dialog when INPUT can use inline?

---

#### code_internal_inconsistency

**Description:** Inconsistent widget access patterns between editor and output context menus

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _setup_editor_context_menu():
- Accesses inner widget: self.editor_text.text.tag_ranges(tk.SEL)
- Binds to inner widget: self.editor_text.text.bind("<Button-3>", show_context_menu)

In _setup_output_context_menu():
- Accesses widget directly: self.output_text.tag_ranges(tk.SEL)
- Binds to widget directly: self.output_text.bind("<Button-3>", show_context_menu)

This suggests editor_text is a wrapper object with a .text attribute, while output_text is a direct text widget. The inconsistency could cause confusion or bugs if the pattern isn't maintained.

---

#### code_vs_comment

**Description:** Docstring states line numbers should be part of text content (not drawn separately) and requires Phase 2 refactoring, but code actually parses line numbers from text content already

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Class docstring says:
"Note: Line numbers should be part of the text content (not drawn separately).
This requires Phase 2 refactoring to integrate line numbers into text."

But _redraw() method comment says:
"Note: Line numbers are no longer drawn in canvas - they should be
part of the text content itself (Phase 2 of editor refactoring)."

However, the code already implements this - _parse_line_number() extracts BASIC line numbers from text content, and _redraw() uses this parsed number. The implementation already treats line numbers as part of text content, not drawn separately.

---

#### code_vs_comment

**Description:** Status click handler docstring says it handles breakpoint toggling, but implementation only shows info messages without toggling

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Method docstring:
"Handle click on status column (show error for ?, breakpoint info for ●)."

And the info message says:
"Click the ● again to toggle it off."

But the _on_status_click() method only displays messagebox.showinfo() or messagebox.showerror() - it does not actually toggle breakpoints. There is no code to call set_breakpoint() or modify line_metadata to toggle the breakpoint state.

---

#### code_vs_comment

**Description:** _parse_line_number regex comment says 'Whitespace or end of string' but regex allows both simultaneously

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment in _parse_line_number():
match = re.match(r'^(\d+)(?:\s|$)', line_text)  # Whitespace or end of string

The regex pattern '(?:\s|$)' means 'whitespace OR end of string', which is correct. However, the comment could be misread as requiring one or the other exclusively. The regex will match '10 PRINT' (whitespace after number) and '10' (end of string after number), which is the intended behavior. The comment is technically accurate but could be clearer about the 'or' relationship.

---

#### code_vs_documentation

**Description:** Function serialize_line() is documented and implemented but references serialize_statement() which calls serialize_expression() and serialize_variable(). However, serialize_variable() has inconsistent behavior regarding type suffixes.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
In serialize_variable():
# Comment says: "Only add type suffix if it was explicit in the original source"
# Comment says: "Don't add suffixes that were inferred from DEF statements"
if var.type_suffix and getattr(var, 'explicit_type_suffix', False):
    text += var.type_suffix

But the logic checks for 'explicit_type_suffix' attribute which is not documented anywhere in the module docstring or function docstrings. This attribute's existence and purpose is unclear.

---

#### code_vs_comment

**Description:** The update_line_references() function comment describes a 'Two-pass regex approach' but the implementation actually uses a single-pass approach with two separate regex patterns applied sequentially, not two passes over the data.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment says:
# Two-pass regex approach:
# Pass 1: Match keyword + first line number (GOTO/GOSUB/THEN/ELSE/ON...GOTO/ON...GOSUB)
# Pass 2: Match comma-separated line numbers (for ON...GOTO/GOSUB lists)

But the code does:
code = pattern.sub(replace_line_ref, code)  # First substitution
code = comma_pattern.sub(replace_comma_line, code)  # Second substitution

This is two sequential substitutions on the same string, not two passes. The terminology is misleading.

---

#### code_vs_documentation

**Description:** The serialize_expression() function handles ERR and ERL as special cases (system variables without parentheses), but this behavior is not documented in the function's docstring.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Code:
if expr.name in ('ERR', 'ERL') and len(expr.arguments) == 0:
    return expr.name

Docstring only says:
Serialize an expression node to source text.

Args:
    expr: Expression AST node to serialize

Returns:
    str: Expression source text

No mention of special handling for ERR/ERL system variables.

---

#### code_vs_documentation

**Description:** The delete_lines_from_program() function updates runtime.statement_table if provided, but the docstring doesn't mention this side effect or explain what statement_table is.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring:
Args:
    program_manager: ProgramManager instance with .lines and .line_asts
    args: DELETE command arguments (e.g., "40", "40-100", "-40", "40-")
    runtime: Optional runtime object with statement_table to update

The docstring mentions 'statement_table' but doesn't explain what it is or why it needs updating. This is important for understanding the function's full behavior.

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

**Description:** Comment says 'Don't print prompt here' but doesn't explain why or where prompt IS printed

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In SimpleWebIOHandler.input() method (line 61):
Comment: '# Don't print prompt here - _enable_inline_input will add it'
This references a method _enable_inline_input that is not shown in the provided code. The comment assumes knowledge of implementation details not visible in this file, making it unclear where the prompt actually gets displayed.

---

#### code_internal_inconsistency

**Description:** VariablesDialog uses 'accessed' as default sort mode but comment says 'matches Tk UI defaults'

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In VariablesDialog.__init__ (lines 96-99):
```
# Sort state (matches Tk UI defaults)
self.sort_mode = 'accessed'  # Current sort mode
self.sort_reverse = True  # Sort direction
```
The comment claims this matches Tk UI defaults, but without seeing the Tk UI code or documentation, we cannot verify if 'accessed' with reverse=True is actually the Tk default. This creates a dependency on external code that may not be consistent.

---

#### code_vs_comment

**Description:** Comment says 'RUN at a breakpoint restarts from the beginning' but code doesn't check for breakpoints

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _menu_run() docstring:
"""Run > Run Program - Execute program.

RUN is always valid - it's just CLEAR + GOTO first line.
RUN on empty program is fine (just clears variables).
RUN at a breakpoint restarts from the beginning.
"""

But the code doesn't have any special handling for breakpoints - it just calls runtime.reset_for_run() which preserves breakpoints but doesn't check if currently paused at one.

---

#### code_vs_comment

**Description:** Comment in _execute_tick says 'up to 1000 statements' but code passes max_statements=1000 which may not mean 'up to'

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment:
# Execute one tick (up to 1000 statements)
state = self.interpreter.tick(mode='run', max_statements=1000)

The comment suggests it might execute fewer than 1000, but without seeing the tick() implementation, it's unclear if max_statements is a limit or a target.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of current_statement_char_start/char_end between _execute_tick and _handle_step_result

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _execute_tick():
char_start = state.current_statement_char_start if state.current_statement_char_start > 0 else None
char_end = state.current_statement_char_end if state.current_statement_char_end > 0 else None

But in _handle_step_result() when runtime.halted:
# Get char positions directly from statement_table (state properties return 0 when halted)
char_start = None
char_end = None
stmt = self.runtime.statement_table.get(pc)
if stmt:
    char_start = getattr(stmt, 'char_start', 0) if hasattr(stmt, 'char_start') else 0
    char_end = getattr(stmt, 'char_end', 0) if hasattr(stmt, 'char_end') else 0

The comment in _handle_step_result suggests state properties return 0 when halted, but _execute_tick uses state properties directly. This inconsistency suggests one approach may be wrong.

---

#### code_internal_inconsistency

**Description:** Inconsistent breakpoint storage types - sometimes PC objects, sometimes plain integers

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _toggle_breakpoint():
pc = PC(line_num, stmt_offset)
if pc in self.runtime.breakpoints:
    self.runtime.breakpoints.discard(pc)
else:
    self.runtime.breakpoints.add(pc)

But in _do_toggle_breakpoint():
if line_num in self.runtime.breakpoints:
    self.runtime.breakpoints.remove(line_num)
else:
    self.runtime.breakpoints.add(line_num)

And in _update_breakpoint_display():
for item in self.runtime.breakpoints:
    # Handle both PC objects and plain integers
    if isinstance(item, PC):

The code tries to handle both types, but mixing PC objects and integers in the same set will cause bugs since PC(10, 0) != 10.

---

#### code_vs_comment

**Description:** Comment says 'Use the same logic as current_statement_char_end for consistency' but doesn't show what that logic is

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _update_breakpoint_display():
if stmt and hasattr(stmt, 'char_start') and hasattr(stmt, 'char_end'):
    # Use the same logic as current_statement_char_end for consistency
    char_start = stmt.char_start
    # Check for next statement to calculate proper char_end
    next_pc = PC(item.line_num, item.stmt_offset + 1)

The comment references 'current_statement_char_end' logic but doesn't explain what that logic is or where it's defined. This makes the code harder to understand.

---

#### code_vs_comment

**Description:** Comment claims _sync_program_to_runtime preserves PC conditionally, but code always checks exec_timer state

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment says: 'Preserves current PC/execution state only if exec_timer is active; otherwise resets PC to halted.'

Code at line ~1150:
if self.exec_timer and self.exec_timer.active:
    # Timer is running - preserve execution state
    self.runtime.pc = old_pc
    self.runtime.halted = old_halted
else:
    # No execution in progress - ensure halted
    self.runtime.pc = PC.halted_pc()
    self.runtime.halted = True

This is consistent, but the docstring says 'conditionally preserving PC' which could be clearer about the specific condition (exec_timer.active).

---

#### code_vs_comment

**Description:** Comment says _remove_blank_lines removes all blank lines except current cursor line, but implementation keeps last line regardless of cursor position

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring says: 'Remove blank lines from editor except the current line where cursor is. This prevents removing the blank line user just created with Enter.'

Code at line ~1240:
for i, line in enumerate(lines):
    if line.strip() or i == len(lines) - 1:
        non_blank_lines.append(line)

The code keeps the LAST line if blank, not necessarily where the cursor is. The cursor could be anywhere. The comment assumes cursor is at the end, which may not always be true.

---

#### code_vs_comment

**Description:** Comment in _check_auto_number says 'Only auto-numbers a line once' but implementation checks old_lines snapshot

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Docstring: 'Only auto-numbers a line once - tracks the last snapshot to avoid re-numbering lines while user is still typing on them.'

Code at line ~1450:
if stripped and (i < len(old_lines) or len(lines) > len(old_lines)):
    old_line = old_lines[i] if i < len(old_lines) else ''
    if not re.match(r'^\s*\d+', old_line):
        # Line wasn't numbered before, number it now

The logic checks if the line existed in old snapshot and wasn't numbered. But if user deletes a line number, this would re-number it, which contradicts 'only once'. The 'once' claim is misleading.

---

#### code_internal_inconsistency

**Description:** Two different methods for handling input: _get_input_async and _get_input, but only _get_input is used

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
_get_input_async at line ~1530:
async def _get_input_async(self, prompt):
    loop = asyncio.get_event_loop()
    self.input_future = loop.create_future()
    self._enable_inline_input(prompt)
    result = await self.input_future
    return result

_get_input at line ~1545:
def _get_input(self, prompt):
    self._enable_inline_input(prompt)
    return ''

Both methods exist but serve different purposes. The async version uses futures, the sync version returns empty string. It's unclear when each should be used, and _get_input_async appears unused.

---

#### code_vs_comment

**Description:** Comment in _execute_immediate says 'Query interpreter directly via has_work()' but then checks if interpreter exists

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1600:
# Check if interpreter has work to do (after RUN statement)
# Query interpreter directly via has_work() instead of checking runtime flags
has_work = self.interpreter.has_work() if self.interpreter else False

The comment says to query interpreter directly, but the code has a defensive check 'if self.interpreter'. This suggests interpreter might not exist, which contradicts the 'direct query' approach. If interpreter can be None, the comment should explain when/why.

---

#### code_vs_documentation

**Description:** web_help_launcher.py uses hardcoded URL 'http://localhost/mbasic_docs' but documentation doesn't specify this URL or how to set up the web server

**Affected files:**
- `src/ui/web_help_launcher.py`
- `docs/help/README.md`

**Details:**
Code: HELP_BASE_URL = 'http://localhost/mbasic_docs'
Documentation describes MkDocs building and local servers but doesn't mention the /mbasic_docs path or how to configure Apache/nginx to serve at this location

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut documentation for breakpoints between debugging.md and editor-commands.md

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md states Tk UI uses 'Ctrl+B' for breakpoints
editor-commands.md does not list Ctrl+B at all, only lists 'b' as alternative to 'Ctrl+O' for Load program

---

#### documentation_inconsistency

**Description:** editor-commands.md says 'For debugging-specific commands like breakpoints and stepping, see Debugging Features' but doesn't list any debug shortcuts, while debugging.md lists Ctrl+R, Ctrl+T, Ctrl+G, Ctrl+Q as working in all UIs

**Affected files:**
- `docs/help/common/editor-commands.md`
- `docs/help/common/debugging.md`

**Details:**
editor-commands.md Program Commands section lists 'F2 or Ctrl+R: Run program' but doesn't mention this is also a debug command
debugging.md 'Keyboard Shortcuts Summary' section lists these as debug commands for 'All UIs'

---

#### code_vs_documentation

**Description:** version.py shows VERSION = '1.0.653' but documentation doesn't reference version numbers or where to find them

**Affected files:**
- `src/version.py`
- `docs/help/common/getting-started.md`

**Details:**
version.py comment: 'Increment VERSION after each commit to track which code is running. This appears in debug output so Claude can verify the user has latest code.'
No documentation explains where users can see the version number or what it means

---

#### documentation_inconsistency

**Description:** ASCII codes documentation references non-existent Appendix M

**Affected files:**
- `docs/help/common/language/appendices/ascii-codes.md`
- `docs/help/common/language/functions/asc.md`

**Details:**
In asc.md: "Returns a numerical value that is the ASCII code of the first character of the string X$. (See Appendix M for ASCII codes.)"

However, the actual ASCII codes documentation is located at appendices/ascii-codes.md, not "Appendix M". The reference should point to the correct location.

---

#### documentation_inconsistency

**Description:** Missing cross-reference to error codes in CVI/CVS/CVD documentation

**Affected files:**
- `docs/help/common/language/appendices/error-codes.md`
- `docs/help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
The cvi-cvs-cvd.md file references "Section 3.25 and Appendix B" in the example:
"70 FIELD #1,4 AS N$, 12 AS B$, •••
80 GET #1
90 Y=CVS (N$)
See also MKI$r MKS$, MKD$, Section 3.25 and Appendix B."

However, these section references (Section 3.25, Appendix B) don't exist in the current documentation structure. Should reference error-codes.md or other relevant docs.

---

#### documentation_inconsistency

**Description:** EOF documentation references non-existent LINE INPUT# page

**Affected files:**
- `docs/help/common/language/functions/eof.md`

**Details:**
In eof.md See Also section, it references:
"[LINE INPUT#](../statements/inputi.md) - Read entire line from file"

The link points to 'inputi.md' but based on other documentation, the correct filename should be 'line-input.md' or 'line-input-hash.md'.

---

#### documentation_inconsistency

**Description:** Inconsistent information about string length limits

**Affected files:**
- `docs/help/common/language/character-set.md`
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
In character-set.md:
"STRING ($) - Text data, up to 255 characters per string."

In data-types.md (referenced from character-set.md):
"Strings are limited to 255 characters"

In appendices/ascii-codes.md:
"Strings can contain any printable ASCII characters (32-126)"

The ascii-codes.md doesn't mention the 255 character limit, which is important information that should be consistent across all string-related documentation.

---

#### documentation_inconsistency

**Description:** Incomplete See Also section with malformed statement reference

**Affected files:**
- `docs/help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
In cvi-cvs-cvd.md, the See Also section includes:
"[CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION](../statements/cload.md)"

This appears to be a malformed reference where version-specific information was incorrectly included in the link text. Should be cleaned up to either:
1. Just "[CLOAD](../statements/cload.md)" with a note about version compatibility
2. Remove if not relevant to CVI/CVS/CVD functions

---

#### documentation_inconsistency

**Description:** Inconsistent error message format in INSTR documentation

**Affected files:**
- `docs/help/common/language/functions/instr.md`

**Details:**
The INSTR documentation shows error message as 'ILLEGAL ARGUMENT IN <line number>' but other documentation files use different error message formats. The example also has formatting issues with extra spaces: '10 X$ = "ABCDEB"
 20 Y$ = "B"' with leading spaces that appear inconsistent.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting and error message in MID$ documentation

**Affected files:**
- `docs/help/common/language/functions/mid_dollar.md`

**Details:**
The MID$ example has:
'LIST\n 10 A$="GOOD "\n 20 B$="MORNING EVENING AFTERNOON"\n 30 PRINT A$;MID$(B$,9,7)\n Ok\n RUN\n GOOD EVENING\n Ok'
with 'LIST' command shown, which is inconsistent with other examples. Also shows error message 'ILLEGAL ARGUMENT IN <line number>' which may be inconsistent with actual error format.

---

#### documentation_inconsistency

**Description:** Inconsistent implementation note formatting across system functions

**Affected files:**
- `docs/help/common/language/functions/peek.md`
- `docs/help/common/language/functions/inp.md`
- `docs/help/common/language/functions/lpos.md`
- `docs/help/common/language/functions/usr.md`

**Details:**
PEEK uses 'ℹ️ **Emulated with Random Values**' while INP, LPOS, and USR use '⚠️ **Not Implemented**'. The formatting and structure of implementation notes varies between these similar system-level functions that cannot be implemented in Python.

---

#### documentation_inconsistency

**Description:** Function count mismatch in language reference index

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/functions/index.md`

**Details:**
The index.md states:
"[Functions](functions/index.md) - 40 intrinsic functions"

However, this is a claim that should be verified against the actual functions/index.md file. If the functions/index.md file lists a different number of functions, this would be an inconsistency. The documentation should either:
1. Match the actual count
2. Remove the specific number if it's subject to change
3. Use approximate language like "over 40" or "approximately 40"

---

#### documentation_inconsistency

**Description:** Statement count mismatch in language reference index

**Affected files:**
- `docs/help/common/language/index.md`
- `docs/help/common/language/statements/index.md`

**Details:**
The index.md states:
"[Statements](statements/index.md) - 63 commands and statements"

Similar to the functions count, this should be verified against the actual statements/index.md file. The specific count may not match the actual number of documented statements.

---

#### documentation_inconsistency

**Description:** Incomplete example in DIM documentation

**Affected files:**
- `docs/help/common/language/statements/dim.md`

**Details:**
The Example section shows:
```basic
10 DIM A(20)
             20 FOR 1=0 TO 20
             30 READ A(I)
             40 NEXT I
                 •
```

Issues:
1. Inconsistent indentation (excessive spaces before line numbers)
2. Variable name inconsistency: line 20 uses '1' (number one) instead of 'I' (letter I) in the FOR statement
3. The bullet point (•) at the end suggests incomplete code
4. Missing DATA statements that would be needed for the READ statement to work

---

#### documentation_inconsistency

**Description:** END statement documentation claims CONT can continue after END, but this contradicts typical BASIC behavior

**Affected files:**
- `docs/help/common/language/statements/end.md`
- `docs/help/common/language/statements/cont.md`

**Details:**
end.md states: 'BASIC-80 always returns to command level after an END is executed' and lists CONT in See Also.

cont.md reference suggests CONT works after END: 'To continue program execution after a Control-C has been typed, or a STOP or END statement has been executed'

This is contradictory - if END closes all files and returns to command level, CONT typically cannot resume execution after END in most BASIC implementations.

---

#### documentation_inconsistency

**Description:** ERR reset behavior documentation is incomplete or contradictory

**Affected files:**
- `docs/help/common/language/statements/err-erl-variables.md`

**Details:**
Documentation states ERR is reset to 0 when:
- RESUME statement is executed
- A new RUN command is issued
- An error handling routine ends normally

However, it also states 'They retain their values until the next error occurs' which contradicts the reset conditions. The behavior when an error handler ends normally needs clarification.

---

#### documentation_inconsistency

**Description:** GET documentation mentions INPUT# and LINE INPUT# usage that seems incorrect

**Affected files:**
- `docs/help/common/language/statements/get.md`

**Details:**
Note states: 'After a GET statement, INPUT# and LINE INPUT# may be used to read characters from the random file buffer.'

This is unusual and potentially incorrect. Typically, random file buffers are accessed via field variables defined with FIELD, not via INPUT# which is for sequential files. This needs verification.

---

#### documentation_inconsistency

**Description:** IF...THEN...ELSE multiple statement syntax unclear

**Affected files:**
- `docs/help/common/language/statements/if-then-else-if-goto.md`

**Details:**
Documentation states: 'Use colon to separate multiple statements in THEN or ELSE clause'

But the formal syntax doesn't show this:
'IF <expression> THEN <statement(s)> | <line number>'

Should be: 'IF <expression> THEN <statement>[:<statement>...] | <line number>'

---

#### documentation_inconsistency

**Description:** INPUT# documentation has garbled text

**Affected files:**
- `docs/help/common/language/statements/input_hash.md`

**Details:**
The Remarks section contains corrupted text:
'<variable list> contains the vari?lble names'
'With INPUT#, no question mark is printed, as with INPUT. The data items in the file should appear just as they would if data were being typed in response to an INPUT statement.    with numeric values'

Multiple formatting issues including '?lble' instead of 'able' and inconsistent spacing.

---

#### documentation_inconsistency

**Description:** LLIST implementation note contradicts documentation structure

**Affected files:**
- `docs/help/common/language/statements/llist.md`

**Details:**
Implementation note states: 'Not Implemented: This feature requires line printer hardware'

But then provides full documentation including 'Remarks' that state 'LLIST assumes a l32-character wide printer' (note: '132' is misspelled as 'l32').

If not implemented, the detailed remarks about printer width are misleading.

---

#### documentation_inconsistency

**Description:** LPRINT USING syntax incomplete

**Affected files:**
- `docs/help/common/language/statements/lprint-lprint-using.md`

**Details:**
Syntax shows:
'LPRINT USING <string exp>;<list of expressions>'

But doesn't show the format string patterns that can be used (like ##, $$, etc.) which are presumably the same as PRINT USING. Should reference PRINT USING documentation or include format string syntax.

---

#### documentation_inconsistency

**Description:** Modern extensions section lists commands with inconsistent names

**Affected files:**
- `docs/help/common/language/statements/index.md`
- `docs/help/common/language/statements/helpsetting.md`
- `docs/help/common/language/statements/limits.md`
- `docs/help/common/language/statements/showsettings.md`

**Details:**
index.md lists:
- 'HELP SET' (links to helpsetting.md)
- 'SET' (links to setsetting.md)
- 'SHOW SETTINGS' (links to showsettings.md)

But the actual file names and titles are:
- helpsetting.md with title 'HELPSETTING'
- setsetting.md (referenced but not in provided files)
- showsettings.md (referenced but not in provided files)

Command names should match between index and actual documentation.

---

#### documentation_inconsistency

**Description:** ON ERROR GOTO documentation has incomplete See Also section

**Affected files:**
- `docs/help/common/language/statements/on-error-goto.md`

**Details:**
The See Also section references 'ERR/ERL' as 'err-erl-variables.md' but the actual documentation structure may differ. The reference should be verified against actual file naming conventions.

---

#### documentation_inconsistency

**Description:** Print zone width inconsistency between PRINT and PRINT# documentation

**Affected files:**
- `docs/help/common/language/statements/print.md`
- `docs/help/common/language/statements/printi-printi-using.md`

**Details:**
PRINT documentation states zones are 14 columns each:
'When items are separated by commas, values are printed in zones of 14 columns each'

PRINT# documentation states:
'Items separated by commas are printed in print zones'

But doesn't specify if the zone width is the same 14 columns. This should be clarified for consistency.

---

#### documentation_inconsistency

**Description:** RENUM documentation has duplicate line numbers in example

**Affected files:**
- `docs/help/common/language/statements/renum.md`

**Details:**
Example 6 shows:
'1000 PRINT "OPTION 1"
1100 END
1100 PRINT "OPTION 2"
1200 END
1200 PRINT "OPTION 3"'

Lines 1100 and 1200 appear twice each, which is impossible. This appears to be a copy-paste error in the documentation.

---

#### documentation_inconsistency

**Description:** SETSETTING is marked as MBASIC Extension but appears in common docs

**Affected files:**
- `docs/help/common/language/statements/setsetting.md`

**Details:**
The file is located in 'docs/help/common/language/statements/' but is marked as 'Versions: MBASIC Extension' and noted as 'This is a modern extension not present in original MBASIC 5.21'. Extension features should be in a separate directory or clearly marked throughout.

---

#### documentation_inconsistency

**Description:** SHOWSETTINGS documentation mentions HELPSETTING statement that doesn't exist in settings system

**Affected files:**
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
showsettings.md lists 'HELPSETTING' in 'See Also' section and describes it as 'Display help for a specific setting', but this statement is not documented anywhere in the settings system documentation (settings.md) and no HELPSETTING command is mentioned in the settings overview.

---

#### documentation_inconsistency

**Description:** SHOWSETTINGS documentation mentions SETSETTING statement but settings.md doesn't document it as a BASIC statement

**Affected files:**
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
showsettings.md references 'SETSETTING' in See Also section and describes it as 'Configure interpreter settings at runtime', but settings.md only shows CLI command usage like 'SETSETTING editor.auto_number_step 100' without documenting it as a formal BASIC statement with syntax and examples.

---

#### documentation_inconsistency

**Description:** Variable name significance behavior documented differently in two places

**Affected files:**
- `docs/help/common/language/variables.md`
- `docs/help/common/settings.md`

**Details:**
variables.md states: 'Note on Variable Name Significance: In the original MBASIC 5.21, only the first 2 characters of variable names were significant (AB, ABC, and ABCDEF would be the same variable). This Python implementation uses the full variable name for identification, allowing distinct variables like COUNT and COUNTER. The case handling is configurable via the `variables.case_conflict` setting.'

However, settings.md documents `variables.case_conflict` as handling case conflicts (COUNT vs count) not name length conflicts. These are two different issues that shouldn't be conflated.

---

#### documentation_inconsistency

**Description:** Keyboard shortcuts documented in multiple places with potential conflicts

**Affected files:**
- `docs/help/common/ui/curses/editing.md`
- `docs/help/common/shortcuts.md`

**Details:**
shortcuts.md documents Ctrl+R as 'Run program' and Ctrl+P as 'Show help', while curses/editing.md mentions 'Ctrl+R - Run program' and 'Ctrl+P - Help' in the tips section. However, shortcuts.md also documents 'b' for toggling breakpoints and debugging shortcuts (c, s, e) that are not mentioned in the editing.md file.

---

#### documentation_inconsistency

**Description:** Settings documentation references UI-specific pages that may not exist

**Affected files:**
- `docs/help/common/settings.md`

**Details:**
settings.md includes links to:
- [CLI Settings Commands](../ui/cli/settings.md)
- [Curses Settings Widget](../ui/curses/settings.md)
- [Tk Settings Dialog](../ui/tk/settings.md)
- [Web Settings Dialog](../ui/web/settings.md)

None of these files are provided in the documentation set, only index files for each UI exist.

---

#### documentation_inconsistency

**Description:** Inconsistent naming of the project

**Affected files:**
- `docs/help/mbasic/extensions.md`
- `docs/help/mbasic/features.md`

**Details:**
extensions.md states: "This is **MBASIC-2025**, a modern implementation of Microsoft BASIC-80 5.21" and lists multiple project names under consideration:
- MBASIC-2025 (emphasizes the modern update)
- Visual MBASIC 5.21 (emphasizes the multiple UIs)
- MBASIC++ (emphasizes extensions)
- MBASIC-X (extended MBASIC)

However, features.md and other documents consistently refer to it as "MBASIC interpreter" or "this MBASIC interpreter" without the -2025 suffix. The project name should be consistent across all documentation.

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI filesystem capabilities

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md states about Web UI: "Files stored in browser memory (not browser localStorage)" and "Files persist only during browser session"

However, extensions.md states about Web UI: "Auto-save - Automatic saving to browser storage"

These statements contradict each other - if files are only in memory and not in localStorage, then auto-save to browser storage is not possible. Need clarification on whether Web UI uses localStorage or only memory.

---

#### documentation_inconsistency

**Description:** Inconsistent information about WIDTH statement support

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/features.md`

**Details:**
compatibility.md states: "WIDTH is parsed for compatibility but performs no operation. Terminal width is controlled by the UI or OS. The 'WIDTH LPRINT' syntax is not supported."

features.md does not mention WIDTH statement at all in its comprehensive feature list, despite it being a recognized statement.

If WIDTH is parsed and accepted (even as no-op), it should be documented in the features list with appropriate notes.

---

#### documentation_inconsistency

**Description:** Inconsistent description of debugging command availability

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
extensions.md states: "**Availability:** CLI (command form), Curses (Ctrl+B), Tk (UI controls)" for BREAK command.

compatibility.md does not mention these debugging commands at all in its feature comparison, despite them being significant extensions.

The compatibility guide should explicitly list debugging commands (BREAK, STEP, STACK) in its feature comparison table to clarify they are extensions not in MBASIC 5.21.

---

#### documentation_inconsistency

**Description:** Inconsistent description of line ending support

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/compatibility.md`

**Details:**
architecture.md states in the interpreter benefits: "**Full compatibility**: Supports all BASIC-80 dynamic features" without mentioning line ending differences.

compatibility.md states: "**Line ending support:** More permissive than MBASIC 5.21
- CP/M MBASIC 5.21: Only recognizes CRLF (`\r\n`)
- This implementation: Recognizes CRLF, LF (`\n`), and CR (`\r`)"

This is an enhancement, not full compatibility. The architecture document should note this difference or the compatibility document should clarify that this doesn't break compatibility (it's backward compatible but more permissive).

---

#### documentation_inconsistency

**Description:** Inconsistent information about Variables Window availability across UIs

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/cli/variables.md`

**Details:**
curses/feature-reference.md states 'Variables Window (Ctrl+W)' is available in Curses UI and describes it as a feature. However, cli/variables.md states 'The CLI does not have a Variables Window feature' and lists 'Curses UI - Full-screen terminal with Variables Window (Ctrl+W)' as an alternative. This suggests Variables Window is a Curses feature, but the feature-reference.md also mentions 'Edit Variable Value (Limited - Not fully implemented)' with a warning that 'Variable editing is currently limited in Curses UI. You cannot directly edit values in the variables window.' This creates confusion about what is actually implemented.

---

#### documentation_inconsistency

**Description:** Contradictory information about Find/Replace implementation status

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/cli/find-replace.md`

**Details:**
curses/feature-reference.md states 'Find/Replace (Not yet implemented)' and 'Find and Replace functionality is not yet available in Curses UI. See [Find/Replace Status](find-replace.md) for workarounds and alternatives.' However, cli/find-replace.md states 'The CLI backend does not have built-in Find/Replace commands' and recommends 'For built-in Find/Replace, use the Tk UI' with details 'Tk UI provides: Ctrl+F for Find dialog, Ctrl+H for Replace dialog, F3 for Find Next, Visual highlighting'. This creates confusion - is Find/Replace not implemented in Curses, or is it only available in Tk UI?

---

#### documentation_inconsistency

**Description:** Different breakpoint management capabilities between UIs

**Affected files:**
- `docs/help/ui/cli/debugging.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/debugging.md documents 'BREAK CLEAR' and 'BREAK CLEAR line_number' commands for clearing breakpoints. curses/feature-reference.md documents 'Clear All Breakpoints (Ctrl+Shift+B)' but does not mention the ability to clear individual breakpoints. The CLI docs show more granular control with 'BREAK CLEAR 100' to clear a specific breakpoint, while Curses only documents clearing all at once.

---

#### documentation_inconsistency

**Description:** Settings management not documented for Curses UI

**Affected files:**
- `docs/help/ui/cli/settings.md`
- `docs/help/ui/curses/feature-reference.md`

**Details:**
cli/settings.md provides detailed documentation for SHOWSETTINGS and SETSETTING commands including examples like 'SETSETTING editor.auto_number_step 100'. curses/feature-reference.md mentions 'Auto Line Numbers' as a feature that can be 'Toggle on/off as needed' but provides no information on how to toggle it or access settings in the Curses UI. It's unclear if the CLI commands work in Curses or if there's a different interface.

---

#### documentation_inconsistency

**Description:** Inconsistent version information for MBASIC implementation

**Affected files:**
- `docs/help/mbasic/implementation/string-allocation-and-garbage-collection.md`
- `docs/help/mbasic/index.md`

**Details:**
string-allocation-and-garbage-collection.md states it covers 'CP/M era Microsoft BASIC-80 (MBASIC)' and mentions 'MBASIC 5.21' in a comparison table. The index.md states 'This is a complete Python implementation of MBASIC-80 (MBASIC) version 5.21 for CP/M' and 'Target compatibility: MBASIC 5.21 for CP/M'. However, the string allocation doc also states 'This implementation was widely used across 8-bit computing platforms including CP/M systems, Commodore 64, Apple II (Applesoft), and TRS-80' which suggests it's describing the original MBASIC, not the Python implementation. The doc should clarify whether it's describing the original MBASIC 5.21 behavior or the Python implementation's behavior.

---

#### documentation_inconsistency

**Description:** Find/Replace feature status unclear

**Affected files:**
- `docs/help/ui/curses/find-replace.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
find-replace.md states: 'The Curses UI currently **does not have** Find/Replace functionality. This feature is planned for future implementation.'

However, quick-reference.md does not mention Find/Replace at all in its keyboard shortcuts table, which is consistent with it not being implemented. But the existence of a dedicated find-replace.md document discussing 'Planned Implementation' with specific keyboard shortcuts (Ctrl+F, F3, Shift+F3) creates confusion about whether this is documentation for a future feature or current feature.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation for help

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/help-navigation.md`

**Details:**
quick-reference.md uses: '**?** | Help (with search)' in the Global Commands section.

But help-navigation.md uses template notation: 'Press **{{kbd:help}}** anytime to open help' and '**{{kbd:search}}** | Open search prompt'.

The actual key is unclear - is it '?' or does {{kbd:help}} expand to something else? Also, quick-reference.md shows '?' opens help with search, but help-navigation.md shows a separate search key {{kbd:search}}.

---

#### documentation_inconsistency

**Description:** Inconsistent back navigation key

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/help-navigation.md`

**Details:**
quick-reference.md does not list a 'back' key in any section.

But help-navigation.md clearly documents: '**{{kbd:back}}** | Go back to previous topic' in the Going Back section.

This is a significant navigation feature that should be in the quick reference.

---

#### documentation_inconsistency

**Description:** Variables window keyboard shortcuts incomplete in quick reference

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/curses/quick-reference.md`

**Details:**
variables.md documents extensive keyboard shortcuts for the variables window:
- 's' to cycle sort mode
- 'd' to toggle sort direction
- 'f' to filter variables
- '/' to search for variable

But quick-reference.md only mentions: '**Ctrl+W** | Toggle variables watch window' and does not document any of the shortcuts available within the variables window itself.

---

#### documentation_inconsistency

**Description:** Feature count mismatch

**Affected files:**
- `docs/help/ui/tk/features.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
feature-reference.md title states: 'This document covers all 37 features available in the Tkinter (Tk) UI.'

However, counting the features listed:
- File Operations: 8 features
- Execution & Control: 6 features
- Debugging: 6 features
- Variable Inspection: 6 features
- Editor Features: 7 features
- Help System: 4 features
Total: 8+6+6+6+7+4 = 37 features ✓

But features.md (the 'Essential' features doc) only covers a subset and doesn't clarify it's showing essential features vs. all features, which could confuse users about what's available.

---

#### documentation_inconsistency

**Description:** Settings documentation exists for Curses but referenced for Tk

**Affected files:**
- `docs/help/ui/curses/settings.md`
- `docs/help/ui/tk/settings.md`

**Details:**
curses/settings.md provides detailed documentation about a Settings Widget with keyboard shortcut Ctrl+, and describes an interactive curses-based settings interface.

However, tk/settings.md is referenced in tk/index.md ('Settings & Configuration') but this file is not provided in the documentation set. This suggests either:
1. The Tk UI doesn't have settings documentation
2. The link is broken
3. Settings work differently in Tk vs Curses

The curses settings.md describes a terminal-based widget which wouldn't apply to Tk GUI.

---

#### documentation_inconsistency

**Description:** Command line loading behavior inconsistency

**Affected files:**
- `docs/help/ui/curses/files.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
files.md states under 'Loading from Command Line':
'```bash
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

The files.md example uses 'python3 mbasic' while getting-started.md uses just 'mbasic'. Also, files.md claims loading a file from command line will 'Automatically run' it, which is a significant behavior that should be mentioned in getting-started.md but isn't.

---

#### documentation_inconsistency

**Description:** Variable editing capability differs between UIs

**Affected files:**
- `docs/help/ui/curses/variables.md`
- `docs/help/ui/tk/feature-reference.md`

**Details:**
curses/variables.md states:
'### Current Status
⚠️ **Partial Implementation**: Variable editing in Curses UI is limited.

### What Doesn't Work Yet
- Cannot edit values directly in window'

But tk/feature-reference.md states:
'### Edit Variable Value
Double-click a variable in the Variables window to edit its value during debugging.'

This is correct - different UIs have different capabilities. However, the comparison table in curses/variables.md shows:
'| Edit values | ⚠️ | ❌ | ✅ | ✅ |'

The ⚠️ for Curses suggests partial implementation, but the documentation clearly states it doesn't work at all ('Cannot edit values directly'). Should be ❌ not ⚠️.

---

#### documentation_inconsistency

**Description:** Debugging documentation describes extensive features marked as 'planned' or 'future', but features.md lists them as current capabilities without such qualifications

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/features.md`

**Details:**
debugging.md clearly marks many features as not implemented:
'Note: Advanced features like clicking line numbers to set breakpoints, conditional breakpoints, and a dedicated breakpoint panel are planned for future releases but not yet implemented.'

And lists entire sections as 'Planned Features':
- Conditional Breakpoints (Future)
- Logpoints (Future)
- Data Breakpoints (Future)
- Debug Console (Future)
- Performance Profiling (Future)

But features.md under 'Debugging Tools' lists:
'Breakpoints:
- Line breakpoints
- Conditional breakpoints
- Hit count breakpoints
- Logpoints'

Without any indication these are future features.

---

#### documentation_inconsistency

**Description:** Features documentation describes collaboration and version control features that getting-started explicitly states are not implemented

**Affected files:**
- `docs/help/ui/web/features.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
features.md under 'Advanced Features > Session Management' mentions:
'Session Management' section exists

But getting-started.md explicitly states:
'Note: Collaboration features (sharing, collaborative editing, version control) are not currently implemented. Programs are stored locally in browser storage only.'

This contradiction needs resolution - either features.md should mark these as future, or getting-started.md is outdated.

---

#### documentation_inconsistency

**Description:** Inconsistent description of file save behavior between documents

**Affected files:**
- `docs/help/ui/web/getting-started.md`
- `docs/help/ui/web/features.md`

**Details:**
getting-started.md states:
'Note: The Web UI uses browser localStorage for auto-save functionality and downloads for explicit saves to your computer.'

But features.md under 'File Management > Save Options' only lists:
'Save to browser
Download as file'

Without clarifying that 'Save to browser' is auto-save via localStorage and explicit saves trigger downloads. This could confuse users about when files are downloaded vs stored in browser.

---

#### documentation_inconsistency

**Description:** Debugging guide describes Variable Inspector with extensive features, but getting-started only mentions 'Show Variables' as a simple popup

**Affected files:**
- `docs/help/ui/web/debugging.md`
- `docs/help/ui/web/getting-started.md`

**Details:**
debugging.md describes elaborate Variable Inspector:
'Variables Panel
Located in right sidebar during debugging:
```
Variables
├─ Scalars
│  ├─ A = 42 (Integer)
│  ├─ B$ = "Hello" (String)
...
```
Interactive Editing:
1. Double-click any variable value
2. Edit dialog appears'

But getting-started.md only mentions:
'Show Variables
While program is paused or after it runs:
- Click Run → Show Variables
- A popup shows all defined variables and their values'

No mention of a persistent panel, tree view, or interactive editing. These seem like different features.

---

#### documentation_inconsistency

**Description:** Web interface documentation describes 'Load Example' menu option, but library documentation only mentions 'Download' and 'Open' for loading files

**Affected files:**
- `docs/help/ui/web/web-interface.md`
- `docs/library/*/index.md`

**Details:**
web-interface.md states:
'Load Example - Choose from sample BASIC programs'

But all library index.md files say:
'Web/Tkinter UI: Click File → Open, select the downloaded file'

No mention of 'Load Example' feature in library docs. Users may be confused about how to access example programs.

---

#### documentation_inconsistency

**Description:** Web UI documentation mentions CLI commands that don't apply to web interface

**Affected files:**
- `docs/help/ui/web/web-interface.md`
- `docs/library/*/index.md`

**Details:**
web-interface.md File I/O section and library docs both show:
'CLI: Type `LOAD "filename.bas"`'

But web-interface.md earlier states:
'Cannot directly access local filesystem (but can load files via browser file picker)'

The LOAD command syntax shown would not work in web UI's sandboxed environment. This could confuse web users.

---

#### documentation_inconsistency

**Description:** Contradictory information about debugger support

**Affected files:**
- `docs/help/ui/web/web-interface.md`

**Details:**
web-interface.md Limitations section states:
'Limited debugger support (basic breakpoints only via Run menu)'

But the Run Menu section only lists:
'Run Program - Parse and execute the current program
Stop - Stop a running program'

No mention of breakpoints or debugger features in the Run menu description. Either the limitation is wrong or the menu description is incomplete.

---

#### documentation_inconsistency

**Description:** Web UI documentation doesn't mention case handling settings available in MBASIC

**Affected files:**
- `docs/help/ui/web/web-interface.md`
- `docs/user/CASE_HANDLING_GUIDE.md`

**Details:**
CASE_HANDLING_GUIDE.md extensively documents:
'SET "variables.case_conflict" "error"'
'SET "keywords.case_style" "force_capitalize"'
'SHOW SETTINGS'

But web-interface.md makes no mention of these settings or the SET/SHOW commands. Web users may not know these features exist.

---

#### documentation_inconsistency

**Description:** File persistence information contradicts session-based claim

**Affected files:**
- `docs/help/ui/web/web-interface.md`

**Details:**
Security & Privacy section states:
'Session-based - Data cleared when session ends'

But File I/O section states:
'Files persist during your session'

And Limitations section states:
'Files don't persist after session ends (stored in browser memory only)'

While technically consistent, the phrasing could confuse users about whether files persist at all or only during session.

---

#### documentation_inconsistency

**Description:** Contradictory information about project dependencies

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/INSTALL.md`

**Details:**
CHOOSING_YOUR_UI.md states 'Requires urwid' for Curses UI and 'Requires nicegui' for Web UI, implying these are mandatory dependencies. However, INSTALL.md states 'Since this project has no external dependencies' and lists these as 'Optional' in INSTALLATION.md. The requirements.txt installation step in INSTALL.md would fail if there are truly no dependencies.

---

#### documentation_inconsistency

**Description:** Feature availability mismatch for Curses UI

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states Curses UI has 'No Find/Replace yet' and 'Partial variable editing' as limitations. However, QUICK_REFERENCE.md makes no mention of these limitations and presents the Curses UI as fully functional for editing and debugging. The decision matrix shows 'Find/Replace' with ❌ for Curses, but doesn't explain what 'partial variable editing' means.

---

#### documentation_inconsistency

**Description:** Incomplete CP/M conversion utility reference

**Affected files:**
- `docs/user/FILE_FORMAT_COMPATIBILITY.md`

**Details:**
FILE_FORMAT_COMPATIBILITY.md mentions 'MBASIC includes a utility script for CP/M conversion' and shows command 'python3 utils/convert_to_cpm.py yourfile.bas', but this utility is not included in the provided files and its existence cannot be verified.

---

#### documentation_inconsistency

**Description:** Incomplete settings documentation cross-references

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md references 'docs/dev/KEYWORD_CASE_HANDLING_TODO.md' for future features, but this file is not provided. Also references 'docs/user/TK_UI_QUICK_START.md' which is not in the provided files. These broken references make it impossible to get complete information.

---

#### documentation_inconsistency

**Description:** Contradictory information about Web UI file access

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
CHOOSING_YOUR_UI.md lists 'No local file access' as a limitation of Web UI, but also states 'Browser storage only' and 'Session-based'. However, it's unclear if this means no file I/O at all or just no access to the local filesystem. The distinction between 'browser storage' and 'local files' needs clarification.

---

#### documentation_inconsistency

**Description:** Unclear debugging feature parity

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
The Decision Matrix shows all UIs (CLI, Curses, Tk, Web) have 'Debugging' marked as ✅, but the detailed sections describe different debugging capabilities. CLI has 'BREAK, STEP, WATCH' commands, Curses has breakpoint debugging with 'c/s/e' keys, Tk has 'visual breakpoints', and Web has 'conditional breakpoints'. These are different features but all marked identically in the matrix.

---

#### documentation_inconsistency

**Description:** Unclear settings persistence behavior

**Affected files:**
- `docs/user/SETTINGS_AND_CONFIGURATION.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md states 'Settings via SET command only affect current session' but doesn't explain what 'current session' means. Does it mean until the program ends, until SYSTEM is called, or until the UI is closed? Also unclear if settings persist when using RUN vs LOAD/RUN.

---

#### documentation_inconsistency

**Description:** Keyboard shortcut documentation mismatch between Tk UI and Curses UI guides

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md documents Ctrl+H as 'Find and replace' for Tk UI:
| **Ctrl+H** | Find and replace |

But keyboard-shortcuts.md (Curses UI) documents ^F (Ctrl+F) as help:
| `^F` | This help |

And Ctrl+H as help in Curses:
| `Ctrl+H/F1` | Help |

This creates confusion about whether Ctrl+H is Find/Replace (Tk) or Help (Curses). The TK_UI_QUICK_START.md should clarify this is Tk-specific.

---

#### documentation_inconsistency

**Description:** Find/Replace feature availability inconsistency

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md states Find and Replace is available in Tk UI:
| **Ctrl+H** | Find and replace |

And later:
### 5. Advanced Editing - Find and Replace
Large program with repeated code?
```
1. Press Ctrl+H (Find and Replace)

But UI_FEATURE_COMPARISON.md shows:
| **Find/Replace** | ❌ | ❌ | ✅ | ❌ | Tk only (new feature) |

However, the 'Recently Added' section states:
### Recently Added (2025-10-29)
- ✅ Tk: Find/Replace functionality

This is consistent, but TK_UI_QUICK_START.md also mentions 'October 2025' updates without specifying the exact date (2025-10-29), creating a minor version/date inconsistency.

---

#### documentation_inconsistency

**Description:** Save shortcut inconsistency between UIs

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md documents:
| **Ctrl+S** | Save file |

keyboard-shortcuts.md (Curses) documents:
| `Ctrl+V` | Save program |
| `Shift+Ctrl+V` | Save As |

This shows Curses uses Ctrl+V for Save (not Ctrl+S), which conflicts with Tk using Ctrl+V for Variables window. This is likely correct (different UIs, different shortcuts), but could be clarified in TK_UI_QUICK_START.md that these shortcuts are Tk-specific.

---

#### documentation_inconsistency

**Description:** Inconsistent menu access documentation

**Affected files:**
- `docs/user/keyboard-shortcuts.md`

**Details:**
keyboard-shortcuts.md shows:
| `Ctrl+U` | Activate menu bar (arrows navigate, Enter selects) |

But also shows:
| `Menu only` | Toggle execution stack window |
| `Menu only` | Show/hide execution stack window |

The 'Menu only' entries suggest some features are only accessible via menu, but it's unclear how to access the menu if Ctrl+U activates the menu bar. The documentation should clarify whether 'Menu only' means 'use Ctrl+U then navigate' or if there's another way to access these features.

---

#### documentation_inconsistency

**Description:** Step execution shortcut inconsistency

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md documents:
| **Ctrl+T** | Step through code (next statement) |
| **Ctrl+L** | Step through code (next line) |

keyboard-shortcuts.md (Curses) documents:
| `Ctrl+K` | Step Line - execute all statements on current line |
| `Ctrl+T` | Step Statement - execute one statement at a time |

This shows:
- Tk: Ctrl+T = statement, Ctrl+L = line
- Curses: Ctrl+T = statement, Ctrl+K = line

The functionality is the same but shortcuts differ (Ctrl+L vs Ctrl+K for line stepping). This should be clarified as UI-specific behavior.

---

### 🟢 Low Severity

#### documentation_inconsistency

**Description:** Version number mismatch between description and version field

**Affected files:**
- `setup.py`

**Details:**
setup.py line 13: version="0.99.0",  # Reflects ~99% implementation status (core complete)
setup.py line 15: description="An interpreter for MBASIC 5.21 (BASIC-80 for CP/M) - Independent open-source implementation"

The version is 0.99.0 but the description says it's for MBASIC 5.21, which could be confusing. The comment clarifies 0.99.0 refers to implementation completeness, not MBASIC version.

---

#### code_vs_comment_conflict

**Description:** LineNode docstring says 'Never store source_text' but this is just a design note, not describing actual fields

**Affected files:**
- `src/ast_nodes.py`

**Details:**
@dataclass
class LineNode:
    """A single line in a BASIC program (line_number + statements)

    The AST is the single source of truth. Text is always regenerated from
    the AST using token positions. Never store source_text - it creates
    a duplicate copy that gets out of sync.
    """
    line_number: int
    statements: List['StatementNode']
    line_num: int = 0
    column: int = 0

The docstring warns against storing source_text, but there's no source_text field defined. This is a design guideline rather than a description of the class, which could be confusing.

---

#### code_internal_inconsistency

**Description:** Inconsistent use of Optional[] vs = None for optional fields

**Affected files:**
- `src/ast_nodes.py`

**Details:**
Some dataclasses use Optional[] type hints:
  file_number: Optional['ExpressionNode'] = None

Others use just = None without Optional[]:
  filter: Optional[Any] = None  # in ShowSettingsStatementNode
  count: int = None  # in StepStatementNode (should be Optional[int])

StepStatementNode.count is particularly problematic: 'int = None' is type-unsafe.

---

#### code_vs_comment_conflict

**Description:** CallStatementNode docstring describes standard MBASIC 5.21 syntax but implementation includes non-standard arguments field

**Affected files:**
- `src/ast_nodes.py`

**Details:**
@dataclass
class CallStatementNode:
    """CALL statement - call machine language routine (MBASIC 5.21)

    Standard MBASIC 5.21 Syntax:
        CALL address           - Call machine code at numeric address

    Examples:
        CALL 16384             - Call decimal address
        CALL &HC000            - Call hex address
        CALL A                 - Call address in variable
        CALL DIO+1             - Call computed address

    Note: Parser also accepts extended syntax for compatibility with
    other BASIC dialects (e.g., CALL ROUTINE(args)), but this is not
    standard MBASIC 5.21.
    """
    target: 'ExpressionNode'  # Memory address expression
    arguments: List['ExpressionNode']  # Arguments (non-standard, for compatibility)

The docstring emphasizes standard MBASIC 5.21 syntax (address only) but the implementation includes an 'arguments' field for non-standard syntax. The note explains this, but it's still a deviation from the stated MBASIC 5.21 focus.

---

#### code_internal_inconsistency

**Description:** Duplicate SetSettingStatementNode and ShowSettingsStatementNode definitions

**Affected files:**
- `src/ast_nodes.py`

**Details:**
SetSettingStatementNode is defined twice:
1. Line ~400: In main statements section with 'key' and 'value' fields
2. Line ~1100: In Settings Commands section with 'setting_name' and 'value' fields

ShowSettingsStatementNode is also defined twice:
1. Line ~420: In main statements section with 'filter' field
2. Line ~1120: In Settings Commands section with 'pattern' field

These duplicate definitions with different field names will cause conflicts.

---

#### code_vs_comment

**Description:** UsingFormatter.format_numeric_field has comment about negative zero handling that may not match actual BASIC behavior

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment in format_numeric_field says:
"Determine sign - preserve negative sign for values that round to zero. This matches BASIC behavior where -0.001 formatted with no decimal places displays as "-0" (not "0"). Positive values that round to zero display as "0"."

Code implements:
if rounded == 0 and original_negative:
    is_negative = True
else:
    is_negative = rounded < 0

This behavior needs verification against actual MBASIC 5.21. Most BASIC implementations do NOT preserve negative sign for values that round to zero.

---

#### documentation_inconsistency

**Description:** Module docstring claims 'MBASIC 5.21' but implementation may include non-standard features

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Module docstring: "Built-in functions for MBASIC 5.21. All BASIC built-in functions (SIN, CHR$, INT, etc.)"

However, the UsingFormatter class implements PRINT USING which has complex formatting rules. The specific behavior for negative zero and other edge cases should be verified against actual MBASIC 5.21 documentation to ensure compatibility claims are accurate.

---

#### code_vs_comment

**Description:** EOF function comment mentions ^Z handling but implementation may not fully match CP/M behavior

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment says: "Note: For input files, respects ^Z (ASCII 26) as EOF marker (CP/M style)"

Code checks: elif next_byte[0] == 26:  # ^Z

However, the code reads next_byte as a string (file_handle.read(1)) and then checks next_byte[0] == 26. In Python 3, reading from a text file returns a string, not bytes, so next_byte[0] would be a character, not an integer. This comparison would fail. The code should either open files in binary mode or compare against chr(26).

---

#### code_vs_comment

**Description:** parse_numeric_field comment about leading sign not adding to digit_count contradicts later code

**Affected files:**
- `src/basic_builtins.py`

**Details:**
Comment in parse_numeric_field says:
"# Note: leading sign doesn't add to digit_count, it's a format modifier"

But later in format_numeric_field:
if spec['leading_sign'] or spec['trailing_sign'] or spec['trailing_minus_only']:
    field_width += 1  # Sign takes up one position

The sign does affect field_width calculation, so the comment is misleading. The distinction between digit_count and field_width should be clarified.

---

#### code_vs_comment

**Description:** CaseKeeperTable docstring example shows 'Print' but policy behavior unclear

**Affected files:**
- `src/case_keeper.py`

**Details:**
Docstring example:
table = CaseKeeperTable()
table.set("PRINT", "Print")  # Key: "print", Display: "Print"

But the default policy is "first_wins", and the example doesn't specify a policy. The example should clarify what policy is being used or show the default behavior explicitly.

---

#### documentation_inconsistency

**Description:** Module docstring mentions 'Claude Code' which is a specific tool, making documentation less general

**Affected files:**
- `src/debug_logger.py`

**Details:**
Docstring says: "When enabled, errors and debug info are output to both the UI and stderr for easy visibility when debugging with Claude Code or other tools."

And: "Outputs error details to stderr (visible to Claude/developer)"

This is overly specific to one tool. The documentation should be more general about debugging tools or IDEs.

---

#### code_vs_documentation

**Description:** ProgramManager.merge_from_file() return type documentation incomplete

**Affected files:**
- `src/editing/manager.py`

**Details:**
Method signature shows:
```python
def merge_from_file(self, filename: str) -> Tuple[bool, List[Tuple[int, str]], int, int]:
```

Docstring says:
"Returns:
    Tuple of (success, errors, lines_added, lines_replaced)
    success: True if at least one line loaded successfully
    errors: List of (line_number, error_message) for failed lines
    lines_added: Count of new lines added
    lines_replaced: Count of existing lines replaced"

But doesn't document that errors is specifically List[Tuple[int, str]] where the tuple is (line_number, error_message). The type hint is more precise than the docstring.

---

#### documentation_inconsistency

**Description:** FileHandle.flush() method missing from abstract base class but implemented in RealFileHandle

**Affected files:**
- `src/filesystem/base.py`
- `src/filesystem/real_fs.py`

**Details:**
FileHandle abstract base class defines:
- read()
- readline()
- write()
- close()
- seek()
- tell()
- is_eof()

But RealFileHandle implements additional method:
```python
def flush(self):
    """Flush write buffers."""
    if not self.closed:
        self.file_obj.flush()
```

This method is not in the abstract base class, creating an inconsistency in the interface contract. InMemoryFileHandle also implements flush(), suggesting it should be part of the base class.

---

#### code_vs_documentation

**Description:** Duplicate error code definitions for different errors

**Affected files:**
- `src/error_codes.py`

**Details:**
ERROR_CODES dictionary has duplicate two-letter codes:
- Code 25: ('DF', 'Device fault')
- Code 61: ('DF', 'Disk full')

Also:
- Code 10: ('DD', 'Duplicate definition')
- Code 68: ('DD', 'Device unavailable')

And:
- Code 17: ('CN', 'Can't continue')
- Code 69: ('CN', 'Communication buffer overflow')

This means format_error() would produce ambiguous error messages like '?DF Error' that could mean either 'Device fault' or 'Disk full'. The two-letter codes should be unique.

---

#### code_vs_comment

**Description:** Comment claims CP/M style uppercase filenames but doesn't explain why

**Affected files:**
- `src/filesystem/sandboxed_fs.py`

**Details:**
In _normalize_filename():
```python
return filename.upper()  # CP/M style: uppercase filenames
```

The comment references CP/M (an old operating system) but doesn't explain why this design choice was made for a web-based sandboxed filesystem. This seems like an arbitrary limitation that could confuse users expecting case-sensitive filenames. The comment should explain the rationale or this should be configurable.

---

#### code_vs_comment

**Description:** Help text claims multi-statement lines work but are not recommended, but no code prevents or warns about them

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The _show_help() method states:
"• Multi-statement lines (: separator) work but are not recommended"

The code parses and executes all statements on line 0 in a loop:
"for stmt in line_node.statements:
    interpreter.execute_statement(stmt)"

This suggests multi-statement lines do work, but there's no warning or recommendation against them in the actual execution path, only in the help text.

---

#### code_vs_comment

**Description:** Comment says 'Note: We do not save/restore the PC' but then explains this allows RUN to work, which contradicts the help text saying control flow is not supported

**Affected files:**
- `src/immediate_executor.py`

**Details:**
In execute() method:
"# Note: We do not save/restore the PC before/after execution.
# This allows statements like RUN to change execution position.
# Normal statements (PRINT, LET, etc.) don't modify PC anyway."

But the help text says:
"• GOTO, GOSUB, and control flow statements are not supported"

If RUN is allowed to change execution position, this suggests some control flow IS supported, creating an inconsistency.

---

#### code_vs_comment

**Description:** Help text says INPUT is not allowed but _format_error suggests INPUT might be attempted

**Affected files:**
- `src/immediate_executor.py`

**Details:**
OutputCapturingIOHandler.input() raises:
"raise RuntimeError('INPUT not allowed in immediate mode')"

And _format_error() has special handling for this:
"elif 'Illegal function call' in error_str:
    return 'Illegal function call\n'"

But the help text doesn't mention INPUT as a limitation. It only appears in the LIMITATIONS section indirectly. This could be clearer.

---

#### documentation_inconsistency

**Description:** Function signature uses modern Python type hints but docstring examples show Python 2 style

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
Function signature:
"def sanitize_and_clear_parity(text: str) -> tuple[str, bool]:"

This uses Python 3.9+ tuple[str, bool] syntax, but the docstring examples and the rest of the module suggest compatibility with earlier Python versions. The doctest examples don't show the tuple type hint syntax in their expected outputs.

---

#### code_vs_comment

**Description:** Docstring example shows numbered line behavior but implementation has complex UI-specific logic that may not work in all contexts

**Affected files:**
- `src/immediate_executor.py`

**Details:**
The execute() method has extensive logic for handling numbered lines:
"if line_match:
    line_num = int(line_match.group(1))
    ...
    if hasattr(self.interpreter, 'interactive_mode') and self.interpreter.interactive_mode:"

This requires specific UI infrastructure (interactive_mode, program manager, _refresh_editor, etc.) but the docstring doesn't mention these requirements or that numbered line editing only works in specific UI contexts.

---

#### code_vs_comment

**Description:** Comment about ERL renumbering is broader than MBASIC manual specification

**Affected files:**
- `src/interactive.py`

**Details:**
In _renum_erl_comparison() docstring:
"MBASIC manual specifies: if ERL appears on left side of comparison operator
(=, <>, <, >, <=, >=), the right-hand number is a line number reference.

Current implementation: Renumbers for ANY binary operator with ERL on left,
including arithmetic (ERL + 100, ERL * 2). This is broader than the manual
specifies but avoids missing valid comparison patterns."

The code implements:
if type(expr).__name__ == 'BinaryOpNode':
    left = expr.left
    if type(left).__name__ == 'VariableNode' and left.name == 'ERL':
        # Right side should be renumbered if it's a literal number

This is intentionally broader than spec, but the comment acknowledges this discrepancy.

---

#### code_vs_comment

**Description:** Comment about CHAIN variable preservation has complex logic that may not match description

**Affected files:**
- `src/interactive.py`

**Details:**
In cmd_chain() method:
Comment says: "Save variables based on CHAIN options:
- MERGE: always preserves all variables (it's an overlay)
- ALL: passes all variables to new program
- Neither: only pass COMMON variables"

Code implements:
if all_flag or merge:
    saved_variables = self.program_runtime.get_all_variables()
elif self.program_runtime.common_vars:
    # Complex logic to find variables with type suffixes

The comment is accurate but doesn't mention the complexity of handling COMMON variables with type suffixes (%, $, !, #), which is a significant implementation detail.

---

#### code_vs_comment

**Description:** Comment about execute_immediate runtime selection doesn't match actual condition

**Affected files:**
- `src/interactive.py`

**Details:**
Docstring says:
"Runtime selection:
- If program_runtime exists (from RUN), use it so immediate mode can
  examine/modify program variables (works for stopped OR finished programs)
- Otherwise use persistent immediate mode runtime for variable isolation"

Code implements:
if self.program_runtime is not None:
    runtime = self.program_runtime
    interpreter = self.program_interpreter
else:
    if self.runtime is None:
        # Initialize immediate mode runtime

The comment says it works for 'stopped OR finished programs' but the code just checks if program_runtime exists (is not None). There's no distinction between stopped and finished states in the condition. The comment may be describing intended behavior rather than actual implementation.

---

#### code_vs_comment_conflict

**Description:** Comment references help text for GOTO/GOSUB restriction but help text is not visible in provided code

**Affected files:**
- `src/interactive.py`

**Details:**
Comment says: "Immediate mode does NOT support GOTO/GOSUB (see help text)"

The help text is referenced but not included in the provided code snippet, making it impossible to verify if the help text actually documents this restriction or if the restriction is actually enforced.

---

#### code_vs_comment

**Description:** InterpreterState docstring says 'check these to determine current status' but lists input_prompt as non-None for waiting, while error_info is also non-None for errors - unclear priority

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 36-40: 'Primary execution states (check these to determine current status):
    - runtime.halted: True if stopped (paused/done/at breakpoint)
    - input_prompt: Non-None if waiting for input
    - error_info: Non-None if an error occurred'

This suggests checking all three, but doesn't clarify precedence. If both input_prompt and error_info are non-None, which takes priority? The tick() method shows error_info takes priority (line 367: 'if self.state.input_prompt is not None: return self.state' comes after error handling), but this isn't documented.

---

#### code_vs_comment

**Description:** Docstring for current_statement_char_end has detailed explanation of max() logic, but the actual implementation is more complex with line_text_map fallback not mentioned in docstring

**Affected files:**
- `src/interpreter.py`

**Details:**
Docstring at lines 84-90: 'Get current statement char_end from statement table (computed property)

        Uses max(char_end, next_char_start - 1) to handle string tokens correctly.
        This works because:
        - If there's a next statement, the colon is at next_char_start - 1
        - If char_end is correct (most tokens), it will be >= next_char_start - 1
        - If char_end is too short (string tokens), next_char_start - 1 is larger'

But code at lines 103-109 has additional logic:
'else:
    # No next statement - use line length if we have line text, otherwise char_end
    if pc.line_num in self._interpreter.runtime.line_text_map:
        line_text = self._interpreter.runtime.line_text_map[pc.line_num]
        # Return length of line (end of line)
        return len(line_text)
    else:
        return stmt_char_end'

The docstring doesn't mention the line_text_map fallback for last statement on a line.

---

#### documentation_inconsistency

**Description:** InterpreterState docstring says 'breakpoints are stored in Runtime, not here' but doesn't explain why skip_next_breakpoint_check is in InterpreterState instead of Runtime

**Affected files:**
- `src/interpreter.py`

**Details:**
Comment at line 50: '# Debugging (breakpoints are stored in Runtime, not here)'

This suggests a design principle (breakpoint state in Runtime), but then skip_next_breakpoint_check is in InterpreterState. The comment should explain why this particular breakpoint-related flag is in InterpreterState (likely because it's execution state, not program state).

---

#### code_vs_comment

**Description:** Comment describes CLEAR preserving COMMON variables but doesn't mention other preserved state

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_clear() at line ~1270, comment states:
# Note: We preserve runtime.common_vars for CHAIN compatibility
# Note: We ignore string_space and stack_space parameters (Python manages memory automatically)

However, the code also preserves:
- runtime.files (file handles)
- runtime.field_buffers (random access file buffers)
- User functions (runtime.user_functions)
- Data pointers and other runtime state

The comment should document all preserved state, not just common_vars.

---

#### code_vs_comment

**Description:** File reading comment mentions three EOF detection methods but implementation may have edge cases

**Affected files:**
- `src/interpreter.py`

**Details:**
In _read_line_from_file() at line ~1490, comment describes three EOF detection methods:
1. EOF flag already set (file_info['eof'] == True) → returns None immediately
2. read() returns empty bytes (physical EOF) → sets EOF flag, returns partial line or None
3. Byte value 26 (^Z) encountered → sets EOF flag, returns partial line or None

However, the code has a potential edge case: if ^Z appears at the start of a line (line_bytes is empty), it returns None. But if ^Z appears mid-line, it returns the partial line. The comment says 'returns partial line or None' but doesn't clarify when each occurs. This could be confusing for users expecting consistent behavior.

---

#### code_vs_comment

**Description:** LSET/RSET comments say 'If not a field variable, just do normal assignment' but this may not match MBASIC behavior

**Affected files:**
- `src/interpreter.py`

**Details:**
In execute_lset() and execute_rset() at lines ~2050 and ~2090, both have:
if not found:
    # If not a field variable, just do normal assignment
    self.runtime.set_variable_raw(var_name, value)

In MBASIC, LSET/RSET are specifically for field variables in random access files. Using them on non-field variables may be an error or undefined behavior. The comment suggests this is intentional fallback behavior, but it's unclear if this matches MBASIC semantics or is a compatibility extension.

---

#### code_vs_comment

**Description:** Comment says get_variable_for_debugger is used because 'we're saving state, not actually reading for use', but this is misleading

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_functioncall, the comment states:
"# Note: We use get_variable_for_debugger here because we're saving state, not actually reading for use"

However, the code IS reading the variable value for actual use (to save and restore it around function calls). The distinction being made seems to be about tracking variable access, not about the purpose of reading. The comment should clarify this is to avoid triggering access tracking, not because the value isn't being used.

---

#### code_vs_comment

**Description:** Comment about debugger_set=True usage is inconsistent with the actual purpose

**Affected files:**
- `src/interpreter.py`

**Details:**
In evaluate_functioncall, when restoring variables:
"# Use debugger_set=True since this is implementation detail, not actual program assignment"

But earlier when saving, the comment says:
"# Note: We use get_variable_for_debugger here because we're saving state, not actually reading for use"

These comments suggest debugger_set and get_variable_for_debugger are about distinguishing implementation details from program behavior, but the terminology is confusing. One uses 'debugger' to mean 'don't track access', the other uses it to mean 'implementation detail'. The naming convention is inconsistent.

---

#### documentation_inconsistency

**Description:** execute_step docstring says it's 'not yet functional' but also says it's a 'placeholder', creating ambiguity about implementation status

**Affected files:**
- `src/interpreter.py`

**Details:**
The docstring states:
"STEP is intended to execute one or more statements, then pause.
Current implementation: Placeholder that prints a message (not yet functional)."

Then the code comment says:
"# For now, just acknowledge the command
# Full implementation would involve:"

This creates confusion about whether STEP is partially implemented, completely unimplemented, or intentionally stubbed. The status should be clearer.

---

#### code_vs_comment

**Description:** Deprecated alias methods suggest backward compatibility but no evidence of prior API

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py contains:
    # Alias for backward compatibility
    def print(self, text="", end="\n"):
        """Deprecated: Use output() instead."""
        self.output(text, end)

    # Alias for backward compatibility
    def get_char(self):
        """Deprecated: Use input_char() instead."""
        return self.input_char(blocking=False)

These suggest a prior API existed, but there's no evidence of when these methods were the primary API or when they were deprecated.

---

#### code_vs_comment

**Description:** input_line() docstring says it delegates to self.input() but comment says 'same behavior'

**Affected files:**
- `src/iohandler/console.py`

**Details:**
In console.py:
    def input_line(self, prompt: str = '') -> str:
        """Input a complete line from console.

        For console, this delegates to self.input() (same behavior).
        """
        return self.input(prompt)

The base class IOHandler.input_line() docstring says: 'Similar to input() but preserves leading/trailing spaces and doesn't interpret commas as field separators.'

The console implementation doesn't actually implement this distinction - it just calls input(). This may be correct for console but the comment should clarify why the distinction doesn't matter.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of error() method color behavior

**Affected files:**
- `src/iohandler/base.py`
- `src/iohandler/curses_io.py`

**Details:**
base.py IOHandler.error() docstring:
        """Output error message.

        Args:
            message: Error message to display

        Examples:
            error("Syntax error in 100")
            error("Type mismatch")
        """

curses_io.py CursesIOHandler.error() docstring:
        """Output error message to curses window.

        Args:
            message: Error message
        """

The curses implementation tries to use red color (curses.color_pair(4)) but this is not documented in either the base class or the implementation. Users wouldn't know errors appear in red.

---

#### code_vs_documentation

**Description:** get_screen_size() method exists but not in base IOHandler interface

**Affected files:**
- `src/iohandler/web_io.py`

**Details:**
web_io.py implements:
    def get_screen_size(self):
        """Get terminal size.

        Returns:
            Tuple of (rows, cols) - returns reasonable defaults for web
        """
        return (24, 80)

This method is not defined in the base IOHandler abstract class, so it's not part of the standard interface. Other implementations don't have it.

---

#### code_vs_comment

**Description:** Comment about preprocessing old BASIC appears twice with slightly different wording

**Affected files:**
- `src/lexer.py`

**Details:**
In read_identifier() method, two comments say essentially the same thing:

Line ~280: "This lexer parses properly-formed MBASIC 5.21 which requires spaces between keywords and identifiers. Old BASIC with NEXTI instead of NEXT I should be preprocessed before parsing."

Line ~330: "NOTE: We do NOT handle old BASIC where keywords run together (NEXTI, FORI). This is properly-formed MBASIC 5.21 which requires spaces. Old BASIC files should be preprocessed with conversion scripts."

The repetition suggests either copy-paste or that one comment is outdated.

---

#### code_vs_comment

**Description:** Docstring claims RND and INKEY$ can be called without parentheses for MBASIC 5.21 compatibility, but this is standard BASIC behavior not specific to version 5.21

**Affected files:**
- `src/parser.py`

**Details:**
Module docstring states:
"Expression parsing notes:
- Functions generally require parentheses: SIN(X), CHR$(65)
- Exception: RND and INKEY$ can be called without parentheses (MBASIC 5.21 compatibility)"

This implies it's a special compatibility feature for version 5.21, but RND and INKEY$ without parentheses is standard BASIC behavior across many versions, not specific to 5.21.

---

#### code_vs_comment

**Description:** Comment about semicolon handling mentions context matters but doesn't fully explain the distinction

**Affected files:**
- `src/parser.py`

**Details:**
In parse_line() at line ~320:
"# Allow trailing semicolon at end of line (treat as no-op).
# Context matters: Semicolons WITHIN PRINT/LPRINT are item separators (parsed there),
# but semicolons BETWEEN statements are treated as trailing no-ops (handled here)."

The comment says semicolons between statements are no-ops, but the code then raises an error if there's content after the semicolon:
"if not self.at_end_of_line() and not self.match(TokenType.COLON):
    token = self.current()
    raise ParseError(f'Expected : or newline after ;, got {token.type.name}', token)"

This means semicolons aren't really 'between statements' as no-ops - they're only allowed as trailing characters at end of line.

---

#### documentation_inconsistency

**Description:** Incomplete documentation of parse_print_using error message format

**Affected files:**
- `src/parser.py`

**Details:**
In parse_print_using() at line ~1050:
"if not self.match(TokenType.SEMICOLON):
    raise ValueError(f'Expected \';\' after PRINT USING format string at line {self.current.line}')"

This uses ValueError instead of ParseError (used elsewhere), and accesses self.current.line directly instead of self.current().line (method call). This is inconsistent with the rest of the parser's error handling pattern.

---

#### code_vs_comment

**Description:** Comment about variable type precedence doesn't mention symbol table

**Affected files:**
- `src/parser.py`

**Details:**
In get_variable_type() docstring at line ~950:
"Determine variable type based on suffix or DEF statement

Type precedence:
1. Explicit suffix ($, %, !, #)
2. DEF statement for first letter
3. Default (SINGLE)"

However, the parser has a symbol_table attribute (line ~60) that maps variable names to types, but this isn't mentioned in the type precedence documentation. It's unclear if/when the symbol table is consulted for type determination.

---

#### code_vs_comment

**Description:** Comment describes LINE modifier syntax that appears incomplete or incorrect

**Affected files:**
- `src/parser.py`

**Details:**
Comment at line ~50 states:
"# Check for LINE modifier after semicolon: INPUT "prompt";LINE var$
# LINE allows input of entire line including commas"

This suggests LINE comes after the semicolon following the prompt, but the code checks for LINE_INPUT token after parsing the prompt and separator, not specifically after a semicolon. The comment may be misleading about when LINE can appear.

---

#### code_vs_comment

**Description:** Comment about malformed FOR loop handling doesn't match actual implementation behavior

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_for() at line ~860 states:
"# Malformed FOR loop like "FOR 1 TO 100"
# Create a dummy variable "I" and use the number as start"

The code creates a dummy variable 'I' but this seems like error recovery rather than intentional support. The comment doesn't indicate this is error handling, making it unclear if this is a feature or a workaround. The docstring doesn't mention this case either.

---

#### documentation_inconsistency

**Description:** Docstring for parse_deffn mentions 'FN' as optional keyword but implementation treats it differently

**Affected files:**
- `src/parser.py`

**Details:**
Docstring states:
"# Handle "DEF FN name" with space (optional FN keyword)"

But the code has two branches:
1. TokenType.FN followed by IDENTIFIER (treats FN as separate token)
2. IDENTIFIER starting with 'fn' (treats FN as part of identifier)

The comment 'optional FN keyword' is misleading - FN is not optional, it's either a separate token or part of the identifier name. The docstring should clarify this is about tokenization differences, not optionality.

---

#### code_internal_inconsistency

**Description:** Inconsistent case handling for letter ranges in parse_deftype

**Affected files:**
- `src/parser.py`

**Details:**
In parse_deftype() at line ~1270:
"first_letter = letter_token.value[0].upper()
first_letter_lower = first_letter.lower()
...
for letter in range(ord(first_letter_lower), ord(last_letter_lower) + 1):
    letter_char = chr(letter)
    self.def_type_map[letter_char] = var_type
    letters.add(letter_char)"

The code converts to upper, then back to lower, then stores lowercase in def_type_map. This is unnecessarily complex and the comment doesn't explain why both conversions are needed. The pattern suggests possible confusion about case normalization.

---

#### code_vs_comment

**Description:** parse_call docstring mentions 'MBASIC 5.21 standard syntax' but no version info elsewhere

**Affected files:**
- `src/parser.py`

**Details:**
Docstring says: 'MBASIC 5.21 standard syntax: CALL address - Call machine code at numeric address'

This is the only reference to a specific MBASIC version (5.21) in the entire code snippet. Other statements don't specify versions. This inconsistency in documentation style could confuse users about which BASIC dialect/version is being implemented.

---

#### code_vs_comment

**Description:** parse_resume docstring says 'RESUME 0' is valid but implementation doesn't document this special case

**Affected files:**
- `src/parser.py`

**Details:**
Comment in parse_resume says: '# Note: RESUME 0 is valid BASIC syntax meaning "retry error statement" (same as RESUME)'

However, the code treats line_number=0 the same as any other line number, not as a special sentinel. The comment suggests RESUME 0 should behave like RESUME (no argument), but the implementation stores 0 as a regular line number. Either the comment is wrong or the code needs special handling for 0.

---

#### documentation_inconsistency

**Description:** Inconsistent docstring format for syntax examples

**Affected files:**
- `src/parser.py`

**Details:**
Most parse methods use 'Syntax:' followed by examples, but formatting varies:
- parse_common: 'Syntax: COMMON variable1, variable2, array1(), string$, ...'
- parse_open: Lists multiple variations with dashes
- parse_close: 'Syntax: CLOSE [#]n [, [#]n ...]'
- parse_field: 'Syntax: FIELD #n, width AS variable$ [, width AS variable$ ...]'
- parse_width: 'Syntax: WIDTH width [, device]' followed by Args section

The parse_width method uniquely includes an 'Args:' section describing parameters, while others don't. This inconsistency makes the documentation harder to follow.

---

#### code_vs_comment

**Description:** Comment in serialize_let_statement says 'Operators are not stored as separate tokens in AST' but this is implementation detail that may not be universally true

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_let_statement method:
# Equals sign (operator position not tracked - using None for column)
# Operators are not stored as separate tokens in AST, so position is inferred

This comment describes current implementation but presents it as absolute fact. Other operators in serialize_expression do have position tracking (BinaryOpNode, UnaryOpNode), so the comment is misleading about the general case.

---

#### code_vs_comment

**Description:** Comment in serialize_expression fallback doesn't match code behavior regarding spacing

**Affected files:**
- `src/position_serializer.py`

**Details:**
In serialize_expression method:
else:
    # Fallback: use pretty printing
    from src.ui.ui_helpers import serialize_expression
    return " " + serialize_expression(expr)

Same issue as serialize_statement - adds leading space but comment doesn't explain why or when this is appropriate. This could cause spacing inconsistencies.

---

#### code_vs_comment

**Description:** renumber_with_spacing_preservation docstring says 'AST is the single source of truth' but then describes updating AST

**Affected files:**
- `src/position_serializer.py`

**Details:**
Docstring says:
"AST is the single source of truth. This function:
1. Updates line numbers in the AST
2. Updates all line number references (GOTO, GOSUB, etc.)
3. Adjusts token column positions to account for line number length changes
4. Text is regenerated from AST by position_serializer"

If AST is the 'single source of truth', then updating it seems contradictory. The comment should clarify that the AST is the source of truth for CONTENT, but this function updates METADATA (line numbers, positions) within the AST.

---

#### code_vs_comment

**Description:** estimate_size method comment says 'TypeInfo (INTEGER, SINGLE, DOUBLE, STRING) or VarType enum' but doesn't explain when each is used

**Affected files:**
- `src/resource_limits.py`

**Details:**
Docstring says:
Args:
    value: The actual value (number, string, array)
    var_type: TypeInfo (INTEGER, SINGLE, DOUBLE, STRING) or VarType enum

The code only checks for TypeInfo values, not VarType enum. Either:
1. VarType enum support is missing (code bug)
2. Comment is outdated and VarType is no longer supported
3. TypeInfo and VarType are the same thing (comment should clarify)

---

#### code_vs_comment

**Description:** Comment in check_array_allocation says 'BASIC is 0-indexed' but this is incorrect for most BASIC dialects

**Affected files:**
- `src/resource_limits.py`

**Details:**
Code comment:
total_elements *= (dim_size + 1)  # +1 because BASIC is 0-indexed

This is misleading. BASIC arrays are 0-indexed by default (0 to N), but the +1 is because DIM A(10) creates 11 elements (0-10), not because of 0-indexing. The comment should say '+1 because DIM A(N) creates N+1 elements (0 to N)' to be clearer.

---

#### documentation_inconsistency

**Description:** StatementTable docstring says 'Uses regular dict which maintains insertion order (Python 3.7+)' but this is now guaranteed in Python 3.7+

**Affected files:**
- `src/pc.py`

**Details:**
The comment 'Python 3.7+' suggests this is a version-specific feature that might not work in older versions. If the codebase requires Python 3.7+, this comment is unnecessary. If it supports older versions, the code would break. The comment should either:
1. Be removed if 3.7+ is required
2. Include a version check if older versions are supported

---

#### code_vs_comment

**Description:** Docstring for get_array_element() says 'optionally tracking read access' but token parameter determines tracking, not optional behavior

**Affected files:**
- `src/runtime.py`

**Details:**
Docstring says:
"Get array element value, optionally tracking read access."

But the implementation shows:
```python
# Track read access if token is provided
if token is not None:
    # Track at array level (for variables window display)
    tracking_info = {...}
```

The tracking is not 'optional' in the sense of a flag - it's determined by whether token is provided. The wording suggests there might be a parameter to control tracking, but there isn't.

---

#### documentation_inconsistency

**Description:** Module docstring lists 'case_variants' in variable storage but implementation uses '_variable_case_variants' as separate dict

**Affected files:**
- `src/runtime.py`

**Details:**
Module docstring at top:
"Variable storage (PRIVATE - use get_variable/set_variable methods)
Each variable is stored as: name_with_suffix -> {'value': val, 'last_read': {...}, 'last_write': {...}, 'original_case': str, 'case_variants': [...]}"

But implementation shows:
```python
self._variables = {}  # name_with_suffix -> {'value': val, 'last_read': {...}, 'last_write': {...}, 'original_case': str}
self._variable_case_variants = {}  # Maps normalized name (lowercase) to list of all case variants
```

The 'case_variants' is not stored in each variable entry, but in a separate tracking dict.

---

#### code_vs_comment

**Description:** Docstring for set_variable() says 'token can be None' when debugger_set=True, but earlier says 'MUST be called with a token'

**Affected files:**
- `src/runtime.py`

**Details:**
Docstring for set_variable():
"This method MUST be called with a token for normal program execution.
For debugger writes, pass debugger_set=True (token can be None)."

This is internally consistent but contradicts the general pattern established by get_variable() which says to use a separate method (get_variable_for_debugger) instead of allowing token=None.

---

#### code_vs_comment

**Description:** Comment in get_all_variables() says 'line -1 in last_write indicates debugger/prompt/internal set' but set_variable_raw uses line=-1 for system variables

**Affected files:**
- `src/runtime.py`

**Details:**
In get_all_variables() docstring:
"Note: line -1 in last_write indicates debugger/prompt/internal set"

But set_variable_raw() creates FakeToken with line=-1 for system variables like ERR% and ERL%, which are not debugger/prompt sets but internal initialization. This overloads the meaning of line=-1.

---

#### code_vs_comment

**Description:** Missing 'stmt' field in FOR loop example in get_execution_stack() docstring

**Affected files:**
- `src/runtime.py`

**Details:**
The docstring example shows:
"Example with nested control flow:
[
    {'type': 'FOR', 'var': 'I', 'current': 1, 'end': 10, 'step': 1, 'line': 100},
    {'type': 'GOSUB', 'from_line': 130, 'return_line': 130},
    {'type': 'WHILE', 'line': 500}
]"

But the documented FOR loop structure includes:
"For FOR loops:
{
    'type': 'FOR',
    'var': 'I',
    'current': 5,
    'end': 10,
    'step': 1,
    'line': 100,
    'stmt': 0             # Statement offset
}"

The example is missing the 'stmt' field that is documented and implemented in the actual code.

---

#### code_vs_comment

**Description:** Missing 'return_stmt' field in GOSUB example in get_execution_stack() docstring

**Affected files:**
- `src/runtime.py`

**Details:**
The docstring example shows:
"{'type': 'GOSUB', 'from_line': 130, 'return_line': 130}"

But the documented GOSUB structure includes:
"For GOSUB calls:
{
    'type': 'GOSUB',
    'from_line': 60,
    'return_line': 60,
    'return_stmt': 0      # Statement offset to return to
}"

The example is missing the 'return_stmt' field that is documented and implemented in the actual code.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for statement offset indexing in docstrings

**Affected files:**
- `src/runtime.py`

**Details:**
In set_breakpoint() docstring:
"stmt_offset: Optional statement offset (0-based). If None, breaks on entire line."
"set_breakpoint(100, 2)        # Statement-level (line 100, 3rd statement)"

This shows stmt_offset=2 refers to the "3rd statement" (1-based description) but the parameter is described as "0-based". While technically correct (offset 2 = 3rd item), the mixed terminology could be confusing. The same pattern appears in get_gosub_stack() docstring:
"- line 500, statement 2 (third statement on line 500)"

Consistency in describing offsets vs ordinal positions would improve clarity.

---

#### documentation_inconsistency

**Description:** Comment claims 'ui.theme not implemented yet' but no placeholder or definition exists for this setting

**Affected files:**
- `src/settings_definitions.py`

**Details:**
Comment at line ~153 in settings_definitions.py:
# Note: ui.theme not implemented yet

This suggests ui.theme was planned but there's no SettingDefinition for it, not even a placeholder. This is inconsistent with the pattern of defining all settings even if not fully implemented.

---

#### code_vs_comment

**Description:** Comment says 'Tab key is used for window switching in curses UI, not indentation' but there's no curses UI context in this file

**Affected files:**
- `src/settings_definitions.py`

**Details:**
Comment at line ~145:
# Note: Tab key is used for window switching in curses UI, not indentation
# Removed editor.tab_size setting as it's not relevant for BASIC

This comment references curses UI implementation details in a settings definition file, which is a layer violation. The comment explains why a setting was removed, but the reasoning is UI-specific and doesn't belong in the settings definitions module.

---

#### code_vs_comment

**Description:** Comment says 'Line numbers are always shown - they're fundamental to BASIC!' but this is a UI decision documented in a settings definition file

**Affected files:**
- `src/settings_definitions.py`

**Details:**
Comment at line ~148:
# Note: Line numbers are always shown - they're fundamental to BASIC!
# Removed editor.show_line_numbers setting as it makes no sense for BASIC

This is another UI implementation detail in the settings definitions. The comment explains a removed setting but the reasoning is architectural, not about the setting system itself.

---

#### code_vs_documentation

**Description:** Token class has both original_case and original_case_keyword fields but documentation doesn't explain when each is used

**Affected files:**
- `src/tokens.py`

**Details:**
In tokens.py Token dataclass (lines ~245-250):
original_case: Any = None  # Original case for identifiers (before lowercasing)
original_case_keyword: str = None  # Original case for keywords (e.g., "PRINT", "Print", "print")

The comments suggest original_case is for identifiers and original_case_keyword is for keywords, but the __repr__ method shows both can be present simultaneously. The relationship and usage pattern is not clearly documented.

---

#### documentation_inconsistency

**Description:** Comment says 'Curses UI not available' when import fails, but doesn't explain why or what's needed

**Affected files:**
- `src/ui/__init__.py`

**Details:**
In ui/__init__.py (lines ~16-19):
except ImportError:
    # Curses UI not available
    _has_curses = False
    CursesBackend = None

The comment doesn't explain that urwid is an optional dependency or how to install it. This could confuse users who see CursesBackend = None.

---

#### code_vs_documentation

**Description:** AutoSaveManager docstring says 'Emacs-style auto-save' but doesn't explain what that means for users unfamiliar with Emacs

**Affected files:**
- `src/ui/auto_save.py`

**Details:**
In auto_save.py (lines ~4-12):
"""Auto-Save Manager for MBASIC IDE

Provides Emacs-style auto-save functionality:
- Saves to temp files (#filename#) automatically
- Never overwrites user-saved files without permission
- Offers recovery on startup if autosave is newer
- Cleans up old autosaves

The term 'Emacs-style' is jargon that may not be clear to all users. The bullet points explain it, but the term itself could be removed or explained.

---

#### code_vs_comment

**Description:** UIBackend docstring lists 'HeadlessBackend: No UI, for batch processing' but no such backend exists in the codebase

**Affected files:**
- `src/ui/base.py`

**Details:**
In base.py (lines ~24-28):
Different UIs can implement this interface:
- CLIBackend: Terminal-based REPL (current InteractiveMode)
- GUIBackend: Desktop GUI with visual editor
- MobileBackend: Touch-based mobile UI
- WebBackend: Browser-based interface
- HeadlessBackend: No UI, for batch processing

Only CLIBackend, VisualBackend, CursesBackend, and TkBackend are defined in ui/__init__.py. GUIBackend, MobileBackend, WebBackend, and HeadlessBackend don't exist.

---

#### Documentation inconsistency

**Description:** Footer text shows ESC/^P for Cancel but keypress handler only implements ESC

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
Footer text displays:
"Enter=OK  ESC/^P=Cancel  ^A=Apply  ^R=Reset"

But keypress() method only handles:
if key == 'esc':
    self._on_cancel()
    return None

There is no handler for 'ctrl p' to cancel. The ^P shortcut is documented but not implemented.

---

#### Code vs Comment conflict

**Description:** TODO comment about help system integration never implemented

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
In _add_debug_help() method:
def _add_debug_help(self):
    """Add debug commands to help system (not yet implemented)"""
    # TODO: Integrate debug commands with help system
    pass

This method is called during initialization but does nothing. The docstring and TODO indicate planned functionality that was never completed. This creates confusion about whether the debug commands appear in any help system.

---

#### Code vs Documentation inconsistency

**Description:** Enum radio button implementation comment doesn't match actual storage mechanism

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
In _create_setting_widget() for ENUM type:
# Create display label (strip force_ prefix for cleaner display)
display_label = choice.replace('force_', '')
rb = urwid.RadioButton(group, display_label, state=(choice == current_value))
# Store the actual value as user_data for later retrieval
rb._actual_value = choice

The comment says 'Store the actual value as user_data' but the code stores it as a private attribute '_actual_value', not using urwid's user_data mechanism. This is misleading about the implementation approach.

---

#### Code vs Comment conflict

**Description:** Comment about showing error dialog doesn't match actual implementation

**Affected files:**
- `src/ui/curses_settings_widget.py`

**Details:**
In _apply_settings() method:
except Exception as e:
    # Show error (in real implementation would show dialog)
    return False

The comment suggests this is placeholder code ('in real implementation would show dialog'), but the method is used in production code by _on_apply() and _on_ok(). This creates ambiguity about whether error handling is complete or still needs implementation.

---

#### Documentation inconsistency

**Description:** STACK command docstring incomplete - doesn't document actual output format

**Affected files:**
- `src/ui/cli_debug.py`

**Details:**
cmd_stack() docstring says:
"""STACK command - show call stack.

Shows current GOSUB call stack and FOR loop stack.
"""

But doesn't document:
1. What happens when no program is running
2. The specific format of output (numbered list with 'Line X' format)
3. The FOR loop details shown (variable, current, limit)
4. That it checks hasattr() for stack existence (defensive programming not documented)

---

#### code_vs_comment

**Description:** Comment describes format with fixed-width line numbers but implementation uses variable width parsing

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _parse_line_numbers method comment (line ~1030):
'Handles both:
- Lines with column structure: " [space]     10 PRINT"
- Raw pasted lines: "10 PRINT"'

The comment shows '     10' (5 spaces for line number), but the _parse_line_number method uses variable-width parsing:
space_idx = line.find(' ', 1)
if space_idx > 1:
    line_num = int(line[1:space_idx])

This suggests variable width, but the formatting code still uses fixed 5 chars.

---

#### code_vs_comment

**Description:** Comment about column positions assumes fixed width but code checks variable positions

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~460:
'# Sort if we're in the line number area
if 1 <= col_in_line <= 6:'

This assumes columns 1-6 are line number area (fixed 5 digits + space), but the actual check should be dynamic based on where the space after the line number is located, since _parse_line_number uses variable-width parsing.

---

#### code_vs_comment

**Description:** Comment says toolbar is removed from UI layout but _create_toolbar method still exists and is fully implemented

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~213: '# Toolbar removed from UI layout - use Ctrl+U menu instead for keyboard navigation
# (_create_toolbar method still exists but is not called)'

The _create_toolbar() method (lines ~177-211) is fully implemented with all button handlers, suggesting it may have been used recently or could be re-enabled. The comment acknowledges this but the extensive implementation seems inconsistent with 'removed' status.

---

#### code_vs_comment

**Description:** Comment says 'don't create multiple' interpreters but code creates interpreter twice in different contexts

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at line ~53: '# Create one interpreter for the session - don't create multiple!'

However, the code creates the interpreter once in __init__ (line ~56) and then re-initializes ImmediateExecutor with it in start() (line ~95). While technically reusing the same interpreter object, the pattern of re-initialization could be clearer.

---

#### code_vs_comment

**Description:** Comment about syncing pre-loaded program mentions command line loading but no command line argument handling is visible

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment at lines ~97-98: '# Sync any pre-loaded program to the editor
# (e.g., when loading a file from command line)'

The code checks if self.program.has_lines() but there's no visible code in this file showing how a program would be pre-loaded from command line arguments. This may be handled elsewhere but the comment suggests it should be relevant to this initialization.

---

#### code_internal_inconsistency

**Description:** Inconsistent reference to self.editor_lines which is not initialized as an instance variable

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Line ~99: 'if self.program.has_lines() and not self.editor_lines:'

No initialization of self.editor_lines is visible in __init__. The editor widget has self.editor.lines (a dict), but self.editor_lines as a direct attribute of the UI class is never created. This will cause an AttributeError.

---

#### code_vs_comment

**Description:** Comment about PC setting timing is confusing given the actual flow

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program() around line 1075:
Comment: '# If start_line is specified, set PC AFTER start() has called setup()\n# because setup() resets PC to first line'

This comment suggests setup() resets PC, but the actual method called is start(), not setup(). The comment may be referring to an internal method called by start(), but this creates confusion about the actual call chain.

---

#### code_internal_inconsistency

**Description:** Inconsistent handling of self.running flag in _setup_program

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _setup_program() method:
- Line ~1070: Sets 'self.running = False' when program is empty
- Line ~1085: Sets 'self.running = False' on startup error
- But never sets 'self.running = True' on successful setup

The method returns True/False to indicate success, but doesn't consistently manage the self.running flag. The caller (_run_program) may be responsible for setting it to True, but this creates an asymmetric pattern where _setup_program sets it to False but not to True.

---

#### code_vs_comment

**Description:** Comment about 'focus highlighting on first char' doesn't match typical urwid behavior

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_output() around line 1175 and _update_output_with_lines() around line 1190:
Comment: '# Add all lines from buffer with focus highlighting on first char'

This comment appears in multiple places but the code just calls make_output_line(line) without any special focus highlighting logic visible in this file. The comment may be describing behavior implemented in make_output_line(), but without seeing that function, it's unclear if this comment is accurate or outdated.

---

#### documentation_inconsistency

**Description:** Variable window title shows conflicting keyboard shortcuts

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
In _update_variables_window() around line 680:
Title format: 'Variables (Sort: {mode_label} {arrow}) - s=mode d=dir f=filter e=edit Ctrl+W=toggle'

But in the same method around line 650, the title when filtered shows:
'Variables ({len}/{total} filtered: '{filter}') Sort: {mode_label} {arrow} - s=mode d=dir f=filter e=edit Ctrl+W=toggle'

The shortcuts are the same, but there's no indication what 'Ctrl+W=toggle' toggles. Looking at other window titles, this likely toggles window visibility, but it's not documented consistently with other windows.

---

#### code_vs_comment

**Description:** Comment 'No state checking - just ask the interpreter' is misleading as the code does check if interpreter exists

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment: '# No state checking - just ask the interpreter'
Code: has_work = self.interpreter.has_work() if self.interpreter else False
The comment suggests no checking is done, but the code does check if self.interpreter exists before calling has_work().

---

#### code_vs_comment

**Description:** Comment 'Use main_widget as base (not current loop.widget which might be a menu)' suggests defensive programming but doesn't explain when loop.widget would be a menu

**Affected files:**
- `src/ui/curses_ui.py`

**Details:**
Comment: '# Use main_widget as base (not current loop.widget which might be a menu)'
The comment warns about loop.widget potentially being a menu, but there's no context about when this would happen or what problems it would cause. This suggests incomplete understanding or documentation of the widget state management.

---

#### code_vs_documentation

**Description:** Help widget search footer shows inconsistent capitalization for ESC

**Affected files:**
- `src/ui/help_widget.py`
- `src/ui/keybindings.py`

**Details:**
help_widget.py line 161:
self.footer.set_text(" /=New Search ESC=Back ")

help_widget.py line 72:
self.footer.set_text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search u=Back ESC/Q=Exit ")

First uses 'ESC=Back', second uses 'ESC/Q=Exit'. The capitalization is consistent, but the inconsistency is in showing 'ESC' alone vs 'ESC/Q' for similar exit actions.

---

#### code_vs_comment

**Description:** Comment says 'Ctrl+L is context-sensitive' but there's no CTRL_L constant defined or used in the keybindings

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
keybindings.py line 207-209:
# Note: Ctrl+L is context-sensitive in curses UI:
# - When debugging: Step Line (execute all statements on current line)
# - When editing: List program (same as LIST_KEY)

This comment describes Ctrl+L behavior but there's no corresponding constant or configuration for Ctrl+L. The LIST_KEY is defined as Ctrl+K, not Ctrl+L.

---

#### code_vs_documentation

**Description:** Search results show '📘 UI' tier but this emoji is not defined in tier_labels dictionary

**Affected files:**
- `src/ui/help_widget.py`

**Details:**
help_widget.py line 95-98:
tier_labels = {
    'language': '📕 Language',
    'mbasic': '📗 MBASIC',
}

help_widget.py line 115-118:
if tier_name.startswith('ui/'):
    tier_label = '📘 UI'
else:
    tier_label = tier_labels.get(tier_name, '📙 Other')

The '📘 UI' tier is hardcoded in the conditional but not in the tier_labels dictionary, and there's also a fallback '📙 Other' that's not in the dictionary. This suggests the tier_labels dict is incomplete.

---

#### code_vs_comment

**Description:** Comment says 'Ctrl+S unavailable - terminal flow control' but doesn't explain why Ctrl+V was chosen as alternative

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
keybindings.py line 143-145:
# Save program (Ctrl+S unavailable - terminal flow control)
# Use Ctrl+V instead (V for saVe)
_save_key = _get_key('editor', 'save') or 'Ctrl+V'

The comment explains why Ctrl+S can't be used but the mnemonic 'V for saVe' is weak. This could confuse users expecting Ctrl+S. The comment should perhaps mention that Ctrl+V is also commonly used for paste in other applications.

---

#### code_vs_comment

**Description:** Comment says 'Ctrl+I unavailable - identical to Tab' but doesn't explain why Ctrl+J was chosen for insert line

**Affected files:**
- `src/ui/keybindings.py`

**Details:**
keybindings.py line 176-179:
# Smart Insert Line (Ctrl+I unavailable - identical to Tab)
# Use Ctrl+J instead (J for inJect/insert)
INSERT_LINE_KEY = 'ctrl j'
INSERT_LINE_CHAR = '\x0a'

The mnemonic 'J for inJect/insert' is weak and 'inject' is not a common term for inserting lines. Also, Ctrl+J is actually the newline character (\x0a), which could cause confusion.

---

#### code_vs_comment

**Description:** Comment says 'title=None creates border without title text (still has top border line)' but this is misleading - title=None creates a LineBox with no title, which is the standard behavior

**Affected files:**
- `src/ui/keymap_widget.py`

**Details:**
Line 48-49:
# Wrap in line box with black background
# title=None creates border without title text (still has top border line)
linebox = urwid.LineBox(
    urwid.AttrMap(self.listbox, 'body'),
    title=None
)

The comment suggests something special about title=None, but this is just the default LineBox behavior. The comment is unnecessarily explanatory.

---

#### code_vs_documentation

**Description:** Help browser implements Escape key to close in-page search but this is not documented in tk_keybindings.json

**Affected files:**
- `src/ui/tk_help_browser.py`
- `src/ui/tk_keybindings.json`

**Details:**
tk_help_browser.py line 103:
self.inpage_search_entry.bind('<Escape>', lambda e: self._inpage_search_close())

tk_keybindings.json has no entry for Escape key in help_browser section

---

#### code_vs_comment

**Description:** Docstring says 'Note: Not thread-safe (no locking mechanism)' but this is more of a limitation note than a documentation inconsistency. However, it's worth noting that the class doesn't document what happens in concurrent access scenarios

**Affected files:**
- `src/ui/recent_files.py`

**Details:**
Line 13-14:
- Cross-platform (uses pathlib)
- Note: Not thread-safe (no locking mechanism)

This is actually consistent - just a limitation note. No inconsistency here.

---

#### code_vs_comment

**Description:** Comment in _format_table_row says 'Format columns with consistent spacing (15 chars each)' and this exact same comment appears in tk_help_browser.py _format_table_row method, suggesting code duplication

**Affected files:**
- `src/ui/markdown_renderer.py`

**Details:**
markdown_renderer.py line 127:
# Format columns with consistent spacing (15 chars each)

tk_help_browser.py line 555:
# Format columns with consistent spacing (15 chars each)

Both methods have identical implementation for table formatting. This is code duplication, not an inconsistency per se, but suggests the code should be refactored to use a shared utility.

---

#### documentation_inconsistency

**Description:** Instructions text says '↑/↓ scroll  ESC/Q close' but the keypress handler accepts both lowercase 'q' and uppercase 'Q', which is redundant information

**Affected files:**
- `src/ui/keymap_widget.py`

**Details:**
Line 38:
instructions = urwid.AttrMap(
    urwid.Text("↑/↓ scroll  ESC/Q close", align='center'),
    'help_text'
)

Line 85:
if key in ('esc', 'q', 'Q'):

The display shows 'Q' (uppercase) but the code accepts both 'q' and 'Q'. This is not really an inconsistency since urwid typically handles both cases, but the display could just say 'ESC/q' to be clearer.

---

#### code_vs_comment

**Description:** Comment says 'Raise search tags so they appear above other formatting' but this is standard tkinter behavior for tag_raise, not a special implementation detail

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
Line 122-124:
# Raise search tags so they appear above other formatting
self.text_widget.tag_raise("search_highlight")
self.text_widget.tag_raise("search_current")

The comment is accurate but overly explanatory for standard tkinter API usage.

---

#### code_vs_comment

**Description:** Comment says dialog is 'non-blocking' but implementation uses grab_set() which blocks input to other windows

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 33 comment: '# Make modal (grab input focus, but non-blocking - no wait_window())'
Line 34 code: 'self.grab_set()'

The comment claims the dialog is 'non-blocking' because it doesn't call wait_window(), but grab_set() still makes it modal by blocking input to other windows in the application. The dialog is modal (blocks other windows) but doesn't block code execution (no wait_window). The comment is misleading about what 'non-blocking' means in this context.

---

#### code_vs_comment

**Description:** Comment describes inline help as 'not a hover tooltip' but doesn't explain what it actually is

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Line 157 comment: '# Show short help as inline label (not a hover tooltip, just a gray label)'

The comment emphasizes what it's NOT (a hover tooltip) rather than clearly describing what it IS. This is a minor clarity issue - the comment could be more direct by saying 'Show short help as inline gray label' without the negative comparison.

---

#### implementation_inconsistency

**Description:** Redundant type check in _get_current_widget_values method

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Lines 176-181:
    for key, widget in self.widgets.items():
        if isinstance(widget, tk.Variable):
            values[key] = widget.get()
        else:
            values[key] = widget.get()

Both branches of the if/else statement do exactly the same thing (widget.get()). The isinstance check serves no purpose and the else branch is unreachable in practice since all stored widgets are tk.Variable instances based on the _create_setting_widget implementation.

---

#### documentation_inconsistency

**Description:** Module docstring doesn't mention that dialog is modal

**Affected files:**
- `src/ui/tk_settings_dialog.py`

**Details:**
Module docstring (lines 1-5):
"""TK Settings Dialog for MBASIC

Provides a GUI dialog for modifying settings."""

The docstring is very brief and doesn't mention important characteristics like the dialog being modal, having Apply/OK/Cancel buttons, or being organized into category tabs. While not technically incorrect, it's incomplete for a user-facing component.

---

#### code_vs_comment

**Description:** Comment references removed history widget that no longer exists

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Line ~260 comment: '# Create dummy immediate_history and immediate_status for compatibility\n# (some code still references these)'

Code sets: self.immediate_history = None

But there's no evidence in the visible code of anything referencing immediate_history. This appears to be a leftover comment from refactoring that removed the history widget.

---

#### code_vs_comment

**Description:** Toolbar comment mentions removed utility buttons but doesn't reflect current state

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment at line ~420: '# Utility buttons removed - use menus instead:\n# - List → Run > List Program\n# - Clear Prog → File > New\n# - Clear Out → Run > Clear Output'

This comment describes what was removed but doesn't describe what the toolbar currently contains. The comment is historical rather than descriptive of current implementation.

---

#### code_vs_comment

**Description:** Comment about accepting both 'tree' and 'cell' regions is redundant

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~810:
# Check if we clicked on a row (accept 'tree' for first column or 'cell' for other columns)
region = self.variables_tree.identify_region(event.x, event.y)
if region not in ('cell', 'tree'):
    return

The comment explains why both are accepted, but this is standard Treeview behavior and doesn't need explanation. The comment adds no value.

---

#### code_vs_comment

**Description:** Comment about column sorting contradicts implementation

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At line ~770:
# Click on rest = cycle/set sort column
if col_x < ARROW_CLICK_WIDTH:
    self._toggle_variable_sort_direction()
else:
    if column == '#0':  # Variable column - only sortable column
        self._cycle_variable_sort()
    # Type and Value columns are not sortable

Comment says 'cycle/set sort column' but only Variable column is sortable. The comment should say 'cycle sort column (Variable only)' to be accurate.

---

#### code_vs_comment

**Description:** Comment about blank line removal contradicts actual behavior

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _remove_blank_lines() docstring:
"Remove all blank lines from the editor (except final line).\n\nRemoves blank lines to keep program clean, but preserves the final\nline which is always blank in Tk Text widget (internal Tk behavior).\nCalled after any modification (typing, pasting, etc.)"

But the method is NOT called after every modification - it's not bound to any event handler in the visible code. The comment "Called after any modification" appears to be outdated or aspirational rather than actual behavior.

---

#### code_vs_comment

**Description:** Comment about validation timing is misleading

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _validate_editor_syntax() docstring:
"Validates each line independently as entered - immediate feedback."

But the method is called:
1. After cursor movement (100ms delay) - line 1182
2. After mouse click (100ms delay) - line 1191
3. On focus out - line 1196

This is NOT "immediate feedback as entered" - it's delayed feedback after navigation. True immediate feedback would require binding to <KeyRelease> or similar.

---

#### code_vs_comment

**Description:** Comment about preventing blank lines contradicts actual behavior

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_enter_key() at line 1207:
"# If line is completely blank, don't do anything (prevent blank lines)\n        if not current_line_text:\n            return 'break'"

But this doesn't actually prevent blank lines - it just prevents processing them. The blank line still exists in the editor. To truly prevent blank lines, the code would need to delete the line or prevent the newline insertion. The comment is misleading about what the code does.

---

#### code_vs_comment

**Description:** Comment about 'half yellow line' issue doesn't match when highlight is cleared

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _on_key_press() method around line 850:
Comment: '# Clear yellow statement highlight when user starts editing\n# This prevents the "half yellow line" issue when editing error/breakpoint lines'

But the code clears highlight only 'if self.paused_at_breakpoint', which means it won't clear the highlight during normal running execution (when lines flash yellow briefly). The comment suggests it should clear on any editing to prevent visual issues, but the condition is more restrictive.

---

#### code_vs_comment

**Description:** Comment says 'Query interpreter directly via has_work()' but then checks runtime flags anyway

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
In _execute_immediate() method around line 1570:
Comment: '# Check if interpreter has work to do (after RUN statement)\n# Query interpreter directly via has_work() instead of checking runtime flags'

Code: 'has_work = self.interpreter.has_work()'

But then immediately after (line 1580): 'self.runtime.halted = False  # Clear halted flag to start execution'

This shows the code is still manipulating runtime flags directly, contradicting the comment's suggestion to use has_work() instead of runtime flags.

---

#### code_vs_comment

**Description:** Comment about updating variables/stack windows is incomplete

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
At end of _execute_immediate() method (line 1590):
Comment: '# Update variables/stack windows if they exist'

But there's no code following this comment - it's just a TODO note. Either the comment should be removed or the code should be implemented.

---

#### code_vs_comment

**Description:** Comment says 'immediate mode has no history widget' but code shows immediate_history widget exists

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Method _add_immediate_output has comment:
"""Add text to main output pane (immediate mode has no history widget)."""

But later in the file, methods like _setup_immediate_context_menu, _copy_immediate_selection, and _select_all_immediate all reference self.immediate_history widget, which clearly exists.

---

#### code_vs_comment

**Description:** clear_screen() docstring says 'GUI output not clearable like terminal' but this is misleading

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
clear_screen() docstring: "Clear screen - no-op for Tk UI (GUI output not clearable like terminal)."

This is misleading because GUI text widgets CAN be cleared programmatically (e.g., self.output_text.delete('1.0', tk.END)). The comment should clarify that it's a design decision not to clear, not a technical limitation.

---

#### code_vs_comment

**Description:** input_char() docstring says 'limited to 1 character' but implementation doesn't enforce this in the dialog

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
input_char() docstring: "For Tk UI, shows a simple input dialog limited to 1 character."

But the implementation uses:
result = simpledialog.askstring(
    "INPUT$ (Single Character)",
    "Enter a single character:",
    parent=self.root
)

askstring() doesn't limit input length - user can type multiple characters. The code only takes the first character after submission: 'return result[0] if result else ""', but the dialog itself isn't limited.

---

#### code_vs_comment

**Description:** Canvas width comment says '20px for one status character' but actual width is set to 20 without unit specification

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
Comment states:
"# Width: 20px for one status character (●, ?, or space)"

But code uses:
self.canvas = tk.Canvas(
    self,
    width=20,
    ...
)

In Tkinter, the width parameter is in pixels by default, so the comment is technically correct, but the 'px' notation suggests CSS/web context rather than Tkinter convention.

---

#### code_vs_comment

**Description:** Blank line removal feature is implemented but not documented in class docstring

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
The class implements automatic blank line removal when cursor moves away from a blank line:
- _on_cursor_move() method tracks cursor movement
- _delete_line() method removes blank lines
- Bindings set up for '<KeyPress>' and '<ButtonPress-1>'

However, the class docstring only documents:
"Layout: [Status (●/?/ )][ Code with line numbers ]

Status symbols:
- ● : Breakpoint set on this line
- ? : Parse error on this line
- ' ': Normal line (no breakpoint, no error)"

The blank line removal behavior is a significant feature that affects user experience but is not mentioned in the documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for line number types - 'BASIC line number' vs 'editor line' vs 'text widget line number'

**Affected files:**
- `src/ui/tk_widgets.py`

**Details:**
The code uses multiple terms for different line number concepts:
- 'BASIC line number' (the actual line number in BASIC code like 10, 20, 30)
- 'editor line' (mentioned in _on_status_click)
- 'text widget line number' (mentioned in _delete_line docstring)
- 'line_num' variable used for both BASIC and Tkinter line numbers

This creates confusion. For example:
- line_metadata uses BASIC line numbers as keys
- Tkinter text widget uses 1-based sequential line numbers
- Comments don't always clarify which type is being used

---

#### documentation_inconsistency

**Description:** Module docstring claims 'No UI-specific dependencies allowed' but the list_files() function uses glob and os modules which are filesystem-specific, not truly UI-agnostic portable logic.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Module docstring:
"This module contains UI-agnostic helper functions that can be used by
any UI (CLI, Tk, Web, Curses). No UI-specific dependencies allowed."

But list_files() implementation:
import glob
import os

These are filesystem operations, not UI operations, so technically correct but the claim of 'portable logic for all UIs' is slightly misleading since filesystem access patterns differ across platforms.

---

#### code_vs_comment

**Description:** The serialize_statement() function has a comment about REMARK being converted to REM, but this conversion logic is not present in the function itself.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment in RemarkStatementNode handling:
# Preserve comments using original syntax (REM or ')
# Note: REMARK is converted to REM for consistency

But the code only checks:
if stmt.comment_type == "APOSTROPHE":
    return f"' {stmt.text}"
else:  # REM, REMARK, or default
    return f"REM {stmt.text}"

The conversion from REMARK to REM must happen elsewhere (likely in the parser), not in this serialization function. The comment is misleading about where the conversion occurs.

---

#### code_vs_comment

**Description:** The serialize_line() function comment mentions 'preserving indentation' but the implementation only preserves RELATIVE indentation (spaces after line number), not absolute indentation.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring:
Serialize a LineNode back to source text, preserving indentation.

Comment in code:
# Preserve RELATIVE indentation (spaces after line number) from original source
# This ensures indentation survives RENUM when line numbers change width

The docstring should clarify that only relative indentation is preserved, not absolute column positions.

---

#### code_vs_documentation

**Description:** The update_line_references() regex pattern comment says it matches 'ON <expr> GOTO/GOSUB' but the actual regex pattern is 'ON\s+[^G]+\s+GOTO' which matches 'ON' + spaces + anything except G + spaces + GOTO. This doesn't accurately match expressions.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment:
# Keywords: GOTO, GOSUB, THEN, ELSE, or "ON <expr> GOTO/GOSUB"

Regex:
r'\b(GOTO|GOSUB|THEN|ELSE|ON\s+[^G]+\s+GOTO|ON\s+[^G]+\s+GOSUB)\s+(\d+)'

The pattern [^G]+ means 'one or more characters that are not G', which would fail on expressions like 'ON G GOTO 100' or 'ON X+G GOTO 100'. This is a potential bug or the comment is inaccurate.

---

#### documentation_inconsistency

**Description:** The get_variable_sort_modes() function returns sort modes including 'accessed', 'written', 'read', 'name', but the comment in get_sort_key_function() mentions 'old type/value modes' that are not in the current list.

**Affected files:**
- `src/ui/variable_sorting.py`

**Details:**
In get_sort_key_function():
else:
    # Default to name sorting (unknown modes fall back to this, e.g., old 'type'/'value')
    return lambda v: v['name'].lower()

But get_variable_sort_modes() only returns: 'accessed', 'written', 'read', 'name'

The comment references 'type' and 'value' modes that don't exist in the current implementation, suggesting these were removed but the comment wasn't updated.

---

#### code_vs_documentation

**Description:** The parse_delete_args() function docstring shows examples with sorted line numbers [10, 20, 30, 40, 50], but the function doesn't require or verify that all_line_numbers is sorted.

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Docstring examples:
>>> parse_delete_args("40", [10, 20, 30, 40, 50])
(40, 40)

But the function implementation:
min_line = min(all_line_numbers) if all_line_numbers else 0
max_line = max(all_line_numbers) if all_line_numbers else 0

The function uses min() and max() which work on unsorted lists, but the examples suggest sorted input. This could be misleading.

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

**Description:** Comment says input handler 'already echoes the input with newline' but SimpleWebIOHandler.input() doesn't echo anything

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In SimpleWebIOHandler.input() method (lines 60-70):
Comment says: '# The inline input handler already echoes the input with newline\n# So we don't need to echo it again here'
But the input() method code shows:
```
def input(self, prompt=""):
    # Don't print prompt here - _enable_inline_input will add it
    # Get input from UI (this will block until user enters input)
    result = self.input_callback(prompt)
    # The inline input handler already echoes the input with newline
    # So we don't need to echo it again here
    return result
```
The method doesn't call self.output() to echo anything. The comment suggests echoing happens elsewhere (_enable_inline_input), but this creates confusion about where echoing actually occurs.

---

#### code_vs_comment

**Description:** Docstring says 'Uses asyncio.Future for coordination' but no Future is visible in the code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In SimpleWebIOHandler.input() docstring (lines 54-59):
"""Get input from user via inline input field.

Uses asyncio.Future for coordination between synchronous interpreter
and async web UI. The input field appears below the output pane,
allowing users to see all previous output while typing.
"""
The method implementation doesn't show any asyncio.Future usage:
```
def input(self, prompt=""):
    result = self.input_callback(prompt)
    return result
```
The Future coordination likely happens inside input_callback, but the docstring makes it sound like it's in this method.

---

#### code_vs_comment

**Description:** Comment about 'Content change handlers via CodeMirror's on_change callback' is incomplete

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line 1046-1053:
```
# Content change handlers via CodeMirror's on_change callback
# The _on_editor_change method (defined below) handles:
# - Removing blank lines
# - Auto-numbering
# - Placeholder clearing

# Click and blur handlers registered separately
self.editor.on('click', self._on_editor_click, throttle=0.05)
self.editor.on('blur', self._on_editor_blur)
```
The comment says '_on_editor_change method (defined below)' but the method definition is not shown in the provided code snippet. This makes it impossible to verify if the listed behaviors are actually implemented.

---

#### documentation_inconsistency

**Description:** Module docstring mentions 'Breakpoint support' but no breakpoint-related code is visible

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Class docstring (lines 906-922) lists features:
"Features:
- Web-based interface accessible via browser
- Modern, responsive design
- Split-pane editor and output
- Menu system
- File management
- Execution controls
- Variables window
- Breakpoint support

Based on TK UI feature set (see docs/dev/TK_UI_FEATURE_AUDIT.md)."

The 'Breakpoint support' feature is mentioned but no breakpoint-related methods, UI elements, or functionality is shown in the provided code. This could mean the feature is not yet implemented or the code is incomplete.

---

#### code_vs_comment

**Description:** Comment about 'Current line indicator' is incomplete/cut off

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
At line 1056, the code ends with:
```
# Current line indicator
```
This comment appears to be incomplete as there's no code following it. The file seems to be truncated at this point, making it unclear what the current line indicator implementation looks like or if it exists.

---

#### code_vs_comment

**Description:** Comment says 'Don't clear output' but earlier code in _menu_step_line and _menu_step_stmt calls _clear_output()

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _menu_run():
# Don't clear output - continuous scrolling like ASR33 teletype
self._set_status('Running...')

But in _menu_step_line() and _menu_step_stmt():
# Start execution
self._clear_output()

This is inconsistent - stepping clears output but running doesn't.

---

#### code_vs_comment

**Description:** Comment says 'Don't append prompt - interpreter already printed it' but this assumes interpreter behavior not shown in code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _execute_tick() and _handle_step_result():
if not self.waiting_for_input:
    self.waiting_for_input = True
    self.input_prompt_text = state.input_prompt
    # Don't append prompt - interpreter already printed it via io.output()

This comment assumes the interpreter has already output the prompt, but there's no visible code confirming this behavior. If the interpreter doesn't output the prompt, the user won't see it.

---

#### code_vs_comment

**Description:** Comment about Ctrl+C handling describes implementation not visible in this code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
In _execute_tick() docstring:
"""Execute one tick of the interpreter.

Note on Ctrl+C handling:
This method is called every 10ms by ui.timer(). During long-running programs,
this can make Ctrl+C unresponsive because Python signal handlers only run
between bytecode instructions, and the event loop stays busy.

The KeyboardInterrupt handling is done at the top level in mbasic,
which wraps start_web_ui() in a try/except.
"""

This describes behavior in a different file (mbasic) that isn't shown. While informative, it's documenting external behavior rather than this method's behavior.

---

#### code_vs_comment

**Description:** Comment in _save_editor_to_program mentions CP/M EOF markers but implementation is straightforward

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1180:
# Normalize line endings and remove CP/M EOF markers
# \r\n -> \n (Windows line endings)
# \r -> \n (old Mac line endings)
# \x1a (Ctrl+Z, CP/M EOF marker)

Code:
text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\x1a', '')

The comment is accurate and helpful, no inconsistency. This is actually good documentation.

---

#### code_vs_comment

**Description:** Comment in _on_editor_change describes paste detection heuristic but logic seems fragile

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1270:
# Detect paste: large content change (more than 1-2 chars difference from last tracked)
# This helps clear auto-number prompts before paste content merges with them

Code:
content_diff = abs(len(current_text) - len(last_text))
if content_diff > 5:
    # Check if first line is just an auto-number prompt (e.g., '10 ')
    lines = current_text.split('\n')
    if lines and re.match(r'^\d+\s+\d+\s+', lines[0]):

The comment says '>1-2 chars' but code checks '>5 chars'. Also, the regex pattern looks for double line numbers which is very specific. This might miss other paste scenarios.

---

#### code_vs_comment

**Description:** Comment in _get_input says it returns empty string to signal interpreter, but behavior depends on interpreter implementation

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1550:
# Return empty string - signals interpreter to transition to 'waiting_for_input'
# state (state transition happens in interpreter when it receives empty string
# from input()). Execution pauses until _submit_input() calls provide_input().

This assumes specific interpreter behavior that isn't verified in this code. If the interpreter changes how it handles empty input, this will break. The comment should note this is a contract/assumption.

---

#### code_vs_comment

**Description:** Comment in _flush_output_batch mentions 'running slowly' but no slow-running detection in code

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Comment at line ~1500:
# Flush after 50ms of inactivity, or immediately if running slowly

Code:
self.output_batch_timer = ui.timer(0.05, self._flush_output_batch, once=True)

There's no 'running slowly' detection. The code always uses 50ms timer. The comment suggests conditional behavior that doesn't exist.

---

#### code_comment_conflict

**Description:** Comment says 'Legacy class removed' but the deprecated class is still present in the file

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
Line comment: '# Legacy class removed - using direct web URL instead'
But WebHelpLauncher_DEPRECATED class with full implementation follows immediately after

---

#### documentation_inconsistency

**Description:** getting-started.md references UI-specific help paths that don't match the structure in index.md

**Affected files:**
- `docs/help/common/getting-started.md`
- `docs/help/common/index.md`

**Details:**
getting-started.md: 'See your UI-specific help for how to type programs: [Curses UI](../ui/curses/editing.md)'
But index.md doesn't provide navigation to UI-specific sections, only lists common topics

---

#### code_comment_conflict

**Description:** Function docstring says it returns bool but doesn't document what True/False means in all cases

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
open_help_in_browser() docstring: 'Returns: bool: True if browser opened successfully, False otherwise'
But the function returns webbrowser.open(url) result directly, and the code comments suggest uncertainty: 'sys.stderr.write(f"webbrowser.open() returned: {result}\n")' - indicating the return value semantics may not be well understood

---

#### documentation_inconsistency

**Description:** index.md says 'Code Generation Status: In Progress' but optimizations.md also has a 'Code Generation' section with same status

**Affected files:**
- `docs/help/common/compiler/index.md`
- `docs/help/common/compiler/optimizations.md`

**Details:**
Both files have identical 'Code Generation Status: In Progress' sections, creating redundancy and potential for one to become outdated

---

#### documentation_inconsistency

**Description:** debugging.md describes Variables Window editing features but doesn't explain what happens if you enter an invalid value

**Affected files:**
- `docs/help/common/debugging.md`

**Details:**
Section 'Editing Variables' describes the UI for changing values in all three UIs but doesn't document error handling, validation, or what happens if you enter a string for an integer variable, etc.

---

#### code_comment_conflict

**Description:** Docstring says 'Provides a NiceGUI dialog' but class name is WebSettingsDialog suggesting it might be more general

**Affected files:**
- `src/ui/web/web_settings_dialog.py`

**Details:**
Module docstring: 'Web UI Settings Dialog for MBASIC\n\nProvides a NiceGUI dialog for viewing and modifying settings.'
Class uses NiceGUI-specific imports and methods (ui.dialog, ui.card, etc.) so it's NiceGUI-specific, but the naming suggests it could be a general web dialog

---

#### documentation_inconsistency

**Description:** ASCII table shows DEL (127) in two different locations

**Affected files:**
- `docs/help/common/language/appendices/ascii-codes.md`

**Details:**
The ASCII codes documentation shows DEL (decimal 127, hex 7F) both:
1. In the main printable characters table (32-126) at the end
2. In a separate "Special Character: DEL" section

This is redundant and potentially confusing. DEL should either be in the printable table OR in its own section, not both.

---

#### documentation_inconsistency

**Description:** Typo in See Also reference

**Affected files:**
- `docs/help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
In cvi-cvs-cvd.md See Also section:
"See also MKI$r MKS$, MKD$"

Should be "MKI$, MKS$, MKD$" (comma instead of 'r' after MKI$)

---

#### documentation_inconsistency

**Description:** Mathematical constants precision inconsistency

**Affected files:**
- `docs/help/common/language/appendices/math-functions.md`

**Details:**
In math-functions.md Constants section:
"PI = 3.141592653589793   ' Use ATN(1) * 4 for pi
E = 2.718281828459045    ' Use EXP(1) for e"

The comment says to use ATN(1) * 4 for pi, but ATN(1) would give approximately 0.7854 (pi/4), so ATN(1) * 4 is correct. However, for E, the comment says "Use EXP(1) for e" which is circular - EXP(1) means e^1 = e, so this doesn't help calculate e.

---

#### documentation_inconsistency

**Description:** Inconsistent exponent notation examples

**Affected files:**
- `docs/help/common/language/data-types.md`

**Details:**
In data-types.md DOUBLE Precision section:
"BIGNUM# = 1.23456789012345D+100"

Then in the note:
"Use D or E for exponent notation (e.g., 1.5D+10 or 1.5E+10)"

This suggests D and E are interchangeable, but typically in BASIC-80, D is for double precision and E is for single precision. The documentation should clarify this distinction.

---

#### documentation_inconsistency

**Description:** Inconsistent description text in INKEY$ 'See Also' reference to itself

**Affected files:**
- `docs/help/common/language/functions/inkey_dollar.md`
- `docs/help/common/language/functions/inp.md`

**Details:**
In inp.md, the 'See Also' link to INKEY$ has description: 'Returns either a one-character string cont~ining a character read from the terminal...' with a typo 'cont~ining' instead of 'containing'. This appears to be a copy-paste error with a tilde character corruption.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in INT documentation

**Affected files:**
- `docs/help/common/language/functions/int.md`

**Details:**
The INT examples show:
'PRINT INT(99.89)\n 99\nOk\n\nPRINT INT(-12.11)\n -13\nOk'
with inconsistent spacing and 'Ok' placement compared to other function documentation examples.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in LEFT$ documentation

**Affected files:**
- `docs/help/common/language/functions/left_dollar.md`

**Details:**
The LEFT$ example shows:
'10 A$ = "BASIC-80"\n 20 B$ = LEFT$(A$,5)\n 30 PRINT B$\n BASIC\n Ok'
with leading spaces before line numbers that are inconsistent with other documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in LEN documentation

**Affected files:**
- `docs/help/common/language/functions/len.md`

**Details:**
The LEN example shows:
'10 X$ = "PORTLAND, OREGON"\n 20 PRINT LEN (X$)\n 16\n Ok'
with leading spaces that differ from other examples.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in LOG documentation

**Affected files:**
- `docs/help/common/language/functions/log.md`

**Details:**
The LOG example shows:
'PRINT LOG ( 45/7 )\n 1.86075\nOk'
without line numbers, unlike most other function examples.

---

#### documentation_inconsistency

**Description:** Incomplete and fragmented documentation in MKI$/MKS$/MKD$ file

**Affected files:**
- `docs/help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md`

**Details:**
The MKI$/MKS$/MKD$ documentation contains fragmented text:
'90 AMT= (K+T)\n 100 FIELD #1, 8 AS D$, 20 AS N$\n 110 LSET D$ = MKS$(AMT)\n 120 LSET N$ = A$\n 130 PUT #1\n See also CVI, CVS, CVD, Section 3.9 and Appendix\n B.\n 3.27 OCT$\nPRINT OCT$ (24)\n 30\n Ok\n See the HEX $ function for hexadecimal\n conversion.\n3.2S PEEK\nA=PEEK (&H5AOO)'
This appears to be corrupted with multiple function descriptions merged together.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in OCT$ documentation

**Affected files:**
- `docs/help/common/language/functions/oct_dollar.md`

**Details:**
The OCT$ documentation has two separate examples with different formatting styles, and the second example doesn't show the 'Ok' prompt consistently.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in RIGHT$ documentation

**Affected files:**
- `docs/help/common/language/functions/right_dollar.md`

**Details:**
The RIGHT$ example shows:
'10 A$="DISK BASIC-80"\n 20 PRINT RIGHT$(A$,8)\n RUN\n BASIC-80\n Ok'
with leading spaces before line numbers.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in RND documentation

**Affected files:**
- `docs/help/common/language/functions/rnd.md`

**Details:**
The RND example shows:
'10 FOR I=l TO 5\n 20 PRINT INT(RND*100);\n 30 NEXT\n RUN\n 24 30 31 51 5\n Ok'
with 'I=l' using lowercase 'l' instead of '1', which could be confusing.

---

#### documentation_inconsistency

**Description:** Incomplete example in SGN documentation

**Affected files:**
- `docs/help/common/language/functions/sgn.md`

**Details:**
The SGN example shows:
'ON SGN(X)+2 GOTO 100,200,300 branches to 100 if\n X is negative, 200 if X is 0 and 300 if X is\n positive.'
This is descriptive text mixed with code, not a proper runnable example like other functions.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in SIN documentation

**Affected files:**
- `docs/help/common/language/functions/sin.md`

**Details:**
The SIN example shows:
'PRINT SIN(1.5)\n .997495\n Ok'
without line numbers, unlike most other function examples.

---

#### documentation_inconsistency

**Description:** Inconsistent example formatting in SQR documentation

**Affected files:**
- `docs/help/common/language/functions/sqr.md`

**Details:**
The SQR example shows:
'10 FOR X = 10 TO 25 STEP 5\n 20 PRINT X, SQR(X)\n 30 NEXT\n RUN\n 10 3.16228\n 15 3.87298\n 20 4.47214\n 25 5\n Ok'
with leading spaces before line numbers.

---

#### documentation_inconsistency

**Description:** Incomplete example in STR$ documentation

**Affected files:**
- `docs/help/common/language/functions/str_dollar.md`

**Details:**
The STR$ example shows:
'5 REM ARITHMETIC FOR KIDS\n 10 INPUT "TYPE A NUMBER";N\n 20 ON LEN(STR$(N» GOSUB 30,100,200,300,400,500\n Also see the VAL function.'
The example is incomplete (no subroutines shown) and has a double closing parenthesis '»' which appears to be a formatting error.

---

#### documentation_inconsistency

**Description:** Typo in TAN documentation description

**Affected files:**
- `docs/help/common/language/functions/tan.md`

**Details:**
The TAN description contains 'TAN (X) is calculated in single preclslon.' with 'preclslon' misspelled (should be 'precision').

---

#### documentation_inconsistency

**Description:** Incomplete example in USR documentation

**Affected files:**
- `docs/help/common/language/functions/usr.md`

**Details:**
The USR example shows:
'40 B = T*SIN (Y)\n 50 C = USR (B/2)\n 60 D = USR(B/3)'
with leading spaces before line numbers and starting at line 40, suggesting it's a fragment of a larger program.

---

#### documentation_inconsistency

**Description:** Typo in VAL function example - missing closing parenthesis

**Affected files:**
- `docs/help/common/language/functions/val.md`

**Details:**
In the Description section, the example text reads:
"For example, VAL (" -3) returns -3."

Should be:
"For example, VAL (" -3") returns -3."

The closing quote and parenthesis are missing.

---

#### documentation_inconsistency

**Description:** Incomplete example code in VAL function documentation

**Affected files:**
- `docs/help/common/language/functions/val.md`

**Details:**
The Example section contains incomplete BASIC code:

```basic
10 READ NAME$,CITY$,STATE$,ZIP$
 20 IF VAL(ZIP$) <90000 OR VAL(ZIP$) >96699 THEN
 PRINT NAME$ TAB(25) "OUT OF STATE"
 30 IF VAL(ZIP$) >=90801 AND VAL(ZIP$) <=90815 THEN
 PRINT NAME$ TAB(25) "LONG BEACH"
 See the STR$ function for numeric to string
 conversion.
```

Issues:
1. Line 20 THEN statement is incomplete (no line number or statement)
2. Line 30 THEN statement is incomplete
3. The text "See the STR$ function..." appears to be documentation mixed into the code example
4. Missing line numbers for continuation
5. Inconsistent indentation

---

#### documentation_inconsistency

**Description:** Inconsistent spacing guidance in DEF FN documentation

**Affected files:**
- `docs/help/common/language/statements/def-fn.md`

**Details:**
The DEF FN documentation provides conflicting guidance about spacing:

In the Syntax section, it shows:
"Alternative forms (all valid):"
DEF FN<name> [(<parameter list>)] = <function definition>  ' With spaces
DEF FN<name>(<parameter list>)=<function definition>       ' Without spaces

But then in the "Spacing" subsection under "Syntax Notes", it states:
"Space after FN is optional. Both styles are valid:"
- `DEF FN A(X) = X * 2` - with space after FN (FN and A are separate)
- `DEF FNA(X) = X * 2` - without space after FN (FNA is one token)

The first example shows spacing around the equals sign and parameters, while the second focuses only on the space after FN. The documentation should clarify that multiple spacing variations are acceptable (after FN, around =, around parameters).

---

#### documentation_inconsistency

**Description:** Formatting error in CLOAD documentation title

**Affected files:**
- `docs/help/common/language/statements/cload.md`

**Details:**
The title contains inconsistent spacing:
"CLOAD     THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION"

Should be:
"CLOAD - THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION"

or use consistent spacing throughout.

---

#### documentation_inconsistency

**Description:** Formatting error in CSAVE documentation title

**Affected files:**
- `docs/help/common/language/statements/csave.md`

**Details:**
The title contains inconsistent spacing:
"CSAVE      THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION"

Should match the formatting used in other similar warnings.

---

#### documentation_inconsistency

**Description:** Incomplete example in CLOSE documentation

**Affected files:**
- `docs/help/common/language/statements/close.md`

**Details:**
The Example section states:
"See PART II, Chapter 3, MBASIC       Disk
              I/O, of the MBASIC User's Guide."

This is a reference to external documentation rather than an actual example. The documentation should either:
1. Provide a concrete example of CLOSE usage
2. Remove the Example section if no example is available
3. Provide a more helpful reference

---

#### documentation_inconsistency

**Description:** Inconsistent spacing in AUTO example

**Affected files:**
- `docs/help/common/language/statements/auto.md`

**Details:**
The Example section shows:
```basic
AUTO 100,50      Generates line numbers 100,
                              150, 200 •••
             AUTO             Generates line numbers 10,
                              20,30,40 •••
```

The indentation and spacing are inconsistent. The second AUTO command has excessive leading spaces, and the continuation lines have irregular indentation.

---

#### documentation_inconsistency

**Description:** Unclear example formatting in CLEAR documentation

**Affected files:**
- `docs/help/common/language/statements/clear.md`

**Details:**
The Example section shows:
```basic
CLEAR
                CLEAR ,32768
                CLEAR ,,2000
                CLEAR ,32768,2000
```

The excessive indentation before the last three examples is inconsistent and unclear. These should either:
1. Be formatted consistently with no indentation
2. Include explanatory comments about what each does
3. Be presented as a proper numbered list

---

#### documentation_inconsistency

**Description:** Inconsistent spacing in DELETE example

**Affected files:**
- `docs/help/common/language/statements/delete.md`

**Details:**
The Example section shows:
```basic
DELETE 40         Deletes line 40
                DELETE 40-100     Deletes lines 40 through
                                  100, inclusive
                DELETE-40         Deletes all lines up to
                                  and including line 40
```

The indentation is inconsistent - the first example has no leading spaces, while the second and third have excessive leading spaces.

---

#### documentation_inconsistency

**Description:** Inconsistent spacing in CSAVE example

**Affected files:**
- `docs/help/common/language/statements/csave.md`

**Details:**
The Example section shows:
```basic
CSAVE "TIMER"
                Saves the program currently in memory on
                cassette under filename "T".
```

The explanation has excessive leading spaces and should be formatted as a comment or separate description.

---

#### documentation_inconsistency

**Description:** ERASE documentation has incomplete syntax specification

**Affected files:**
- `docs/help/common/language/statements/erase.md`

**Details:**
Syntax shows: 'ERASE <list of array variables>'

But the example shows: '450 ERASE A,B'

The syntax should clarify the format of the list (comma-separated) like: 'ERASE <array>[,<array>...]'

---

#### documentation_inconsistency

**Description:** FIELD documentation has inconsistent file number syntax

**Affected files:**
- `docs/help/common/language/statements/field.md`

**Details:**
Syntax shows: 'FIELD [#]<file number>'

Example shows: 'FIELD #1, 30 AS NAME$'

The syntax should clarify multiple field definitions like: 'FIELD [#]<file number>,<field width> AS <string variable>[,<field width> AS <string variable>...]'

---

#### documentation_inconsistency

**Description:** FOR...NEXT loop execution behavior description is incorrect

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
Documentation states: 'Loop always executes at least once if start equals end'

This is incorrect for standard BASIC behavior. If start > end (with positive STEP) or start < end (with negative STEP), the loop body should not execute at all. The condition is checked before the first iteration.

---

#### documentation_inconsistency

**Description:** GOSUB documentation syntax is incomplete

**Affected files:**
- `docs/help/common/language/statements/gosub-return.md`

**Details:**
Syntax shows:
'GOSUB <line number>'
'RETURN'

But doesn't show they must be on separate lines or that RETURN can optionally specify a line number in some BASIC variants. The relationship between the two statements could be clearer.

---

#### documentation_inconsistency

**Description:** GOTO example output formatting is unclear

**Affected files:**
- `docs/help/common/language/statements/goto.md`

**Details:**
Example shows output with unusual formatting:
'R = 5                AREA = 7S.5'

The spacing and the 'S' in '7S.5' (should be '75.5') appears to be a typo. Also 'l53.S6' should be '153.86'.

---

#### documentation_inconsistency

**Description:** INPUT statement semicolon behavior description is confusing

**Affected files:**
- `docs/help/common/language/statements/input.md`

**Details:**
Documentation mentions two different uses of semicolon:
1. 'The semicolon after INPUT suppresses the carriage return after the user presses Enter'
2. 'A semicolon after the prompt string causes the prompt to be displayed without a question mark'

The syntax 'INPUT[:] [<"prompt string">:]' uses colons in the syntax description but discusses semicolons in remarks. This is confusing.

---

#### documentation_inconsistency

**Description:** LINE INPUT# example has formatting issues

**Affected files:**
- `docs/help/common/language/statements/inputi.md`

**Details:**
Example code shows:
'10 OPEN "O",l,"LIST"'
'20 LINE INPUT "CUSTOMER INFORMATION? " :C$'

Inconsistent use of 'l' vs '1' for file number, and unusual spacing in the LINE INPUT statement with space before colon.

---

#### documentation_inconsistency

**Description:** LET example has formatting issues

**Affected files:**
- `docs/help/common/language/statements/let.md`

**Details:**
Example shows:
'120 LET E=12A2'
'130 LET F=12A4'

Should use exponentiation operator: '12^2' and '12^4' or '12**2' and '12**4', not 'A'.

---

#### documentation_inconsistency

**Description:** LIST documentation has unclear formatting and version differences

**Affected files:**
- `docs/help/common/language/statements/list.md`

**Details:**
Documentation shows:
'Format 2:     LIST [<line number>[-[<line number>]]] Extended, Disk'

The version information 'Extended, Disk' appears to be part of the syntax line rather than a separate version note. Formatting is confusing.

---

#### documentation_inconsistency

**Description:** LOAD documentation uses inconsistent quote characters

**Affected files:**
- `docs/help/common/language/statements/load.md`

**Details:**
Remarks section uses 'nRn' with straight quotes in some places:
'if the nRn option is used'

But example shows: 'LOAD nSTRTRKn,R'

Should consistently use either straight quotes or explain the 'n' prefix notation.

---

#### documentation_inconsistency

**Description:** Index has inconsistent command name formatting

**Affected files:**
- `docs/help/common/language/statements/index.md`

**Details:**
Some entries use spaces in names:
- 'ERR and ERL' (lowercase 'and')
- 'DEFINT/SNG/DBL/STR' (slashes)
- 'FOR...NEXT' (ellipsis)
- 'IF...THEN...ELSE/IF...GOTO' (mixed ellipsis and slash)

Inconsistent formatting makes it harder to know the actual command syntax.

---

#### documentation_inconsistency

**Description:** MERGE documentation has spacing issues

**Affected files:**
- `docs/help/common/language/statements/merge.md`

**Details:**
Text contains irregular spacing:
'BASIC-80 always returns to command   level     after executing a MERGE command.'

Extra spaces between 'command' and 'level'.

---

#### documentation_inconsistency

**Description:** MID$ assignment documentation has incorrect 'related' reference

**Affected files:**
- `docs/help/common/language/statements/mid-assignment.md`

**Details:**
The 'related' field lists 'mid_dollar' but should list 'mid-dollar' to match the actual function documentation filename pattern. The See Also section correctly references MID$ as a function.

---

#### documentation_inconsistency

**Description:** NAME statement example formatting is inconsistent

**Affected files:**
- `docs/help/common/language/statements/name.md`

**Details:**
The example section shows:
```basic
Ok
              NAME "ACCTS" AS "LEDGER"
              Ok
              In this example, the file that was
              formerly named ACCTS will now be named LEDGER.
```
This mixes code and explanation in an unusual format with excessive indentation. Other docs separate code examples from explanatory text more clearly.

---

#### documentation_inconsistency

**Description:** NULL statement example has inconsistent formatting

**Affected files:**
- `docs/help/common/language/statements/null.md`

**Details:**
Example shows:
```basic
Ok
              NULL 2
              Ok
              100 INPUT X
              200 IF X<50 GOTO 800
              Two null characters will be printed after each
              line.
```
Mixes direct mode commands with program lines and explanation text in a confusing way.

---

#### documentation_inconsistency

**Description:** OPTION BASE example comment is misleading

**Affected files:**
- `docs/help/common/language/statements/option-base.md`

**Details:**
The comment states 'Without OPTION BASE 1, the array would have elements A(0) through A(10)' but this is only true if DIM A(10) is used. The actual behavior depends on whether OPTION BASE is set before the DIM statement.

---

#### documentation_inconsistency

**Description:** RANDOMIZE example has excessive whitespace in output

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
The example output shows inconsistent spacing:
'Random Number Seed (-32768    to 32767)? 3'
with multiple spaces between 'to' and '32767'. This appears to be a formatting artifact rather than actual output.

---

#### documentation_inconsistency

**Description:** READ documentation has incomplete remarks about array elements

**Affected files:**
- `docs/help/common/language/statements/read.md`

**Details:**
States 'Array elements must be dimensioned before being referenced in a READ statement' but doesn't mention that simple variables in arrays with default dimensions (10 elements) don't require explicit DIM statements.

---

#### documentation_inconsistency

**Description:** REM example has inconsistent line numbering

**Affected files:**
- `docs/help/common/language/statements/rem.md`

**Details:**
Example shows:
'120 REM CALCULATE AVERAGE VELOCITY
130 FOR I=1 TO 20
140 SUM=SUM + V(I)'

Then shows alternative:
'120 FOR I=l TO 20     'CALCULATE   AVERAGE VELOCITY
130 SUM=SUM+V(I)
140 NEXT I'

The line numbers don't align (120/130/140 vs 120/130/140) and the second version has 'I=l' (lowercase L) instead of 'I=1'.

---

#### documentation_inconsistency

**Description:** RESUME documentation references non-existent error.md file

**Affected files:**
- `docs/help/common/language/statements/resume.md`

**Details:**
See Also section references 'error.md' but the actual file might be named differently (e.g., 'error-statement.md'). Cross-references should use consistent naming.

---

#### documentation_inconsistency

**Description:** SAVE documentation has unclear CP/M-specific note

**Affected files:**
- `docs/help/common/language/statements/save.md`

**Details:**
States '(With CP/M, the default extension .BAS is supplied.)' but doesn't clarify if this applies to all versions or only CP/M. Modern implementations may have different default behavior.

---

#### documentation_inconsistency

**Description:** Implementation notes formatting inconsistency

**Affected files:**
- `docs/help/common/language/statements/poke.md`
- `docs/help/common/language/statements/out.md`

**Details:**
POKE uses '⚠️ **Emulated as No-Op**' while OUT uses '⚠️ **Not Implemented**'. These should use consistent terminology and formatting for similar situations (both are hardware access features that can't be implemented).

---

#### documentation_inconsistency

**Description:** SHOWSETTINGS references LIMITS statement that is not documented

**Affected files:**
- `docs/help/common/language/statements/showsettings.md`
- `docs/help/common/settings.md`

**Details:**
showsettings.md See Also section includes '[LIMITS](limits.md) - Display resource usage and interpreter limits' but no limits.md file is provided in the documentation set.

---

#### documentation_inconsistency

**Description:** WIDTH documentation claims 'WIDTH LPRINT' syntax is not supported but doesn't clarify if this is a parse error or silent ignore

**Affected files:**
- `docs/help/common/language/statements/width.md`

**Details:**
width.md states 'Limitations: The "WIDTH LPRINT" syntax is not supported (parse error). Only the simple "WIDTH <number>" form is accepted.' This conflicts with the general implementation note that says 'Statement executes successfully without errors' - unclear if LPRINT variant causes parse error or is silently ignored.

---

#### documentation_inconsistency

**Description:** Inconsistent cross-references in See Also sections

**Affected files:**
- `docs/help/common/language/statements/stop.md`
- `docs/help/common/language/statements/system.md`

**Details:**
stop.md See Also includes SYSTEM but system.md See Also includes STOP. However, stop.md references system.md as 'Exit MBASIC and return to the operating system' while system.md references stop.md as 'To terminate program execution and return to command level' - these describe different behaviors (exiting interpreter vs pausing program).

---

#### documentation_inconsistency

**Description:** Inconsistent file naming and cross-references for WRITE variants

**Affected files:**
- `docs/help/common/language/statements/write.md`
- `docs/help/common/language/statements/writei.md`

**Details:**
write.md is titled 'WRITE (Screen)' and writei.md is titled 'WRITE# (File)'. The cross-references use different formats:
- write.md references 'WRITE#' as writei.md
- writei.md references 'WRITE' as write.md
The '#' symbol in filenames vs titles is inconsistent (writei.md vs WRITE#).

---

#### documentation_inconsistency

**Description:** Tk interface keyboard shortcuts differ from general shortcuts documentation

**Affected files:**
- `docs/help/common/ui/tk/index.md`
- `docs/help/common/shortcuts.md`

**Details:**
tk/index.md documents Ctrl+Break for stopping programs, while shortcuts.md doesn't mention this. Additionally, tk/index.md shows F1 for help while shortcuts.md shows Ctrl+P. These may be UI-specific differences but should be clarified.

---

#### documentation_inconsistency

**Description:** Broken link reference in main index

**Affected files:**
- `docs/help/index.md`
- `docs/help/mbasic/getting-started.md`

**Details:**
index.md references '[Getting Started](mbasic/getting-started.md)' in the 'About MBASIC 5.21' section, but the actual path shown in the documentation set is 'docs/help/common/getting-started.md' not 'docs/help/mbasic/getting-started.md'.

---

#### documentation_inconsistency

**Description:** TRON-TROFF See Also section has incomplete cross-references

**Affected files:**
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
tron-troff.md references 'ON ERROR GOTO' with link [ON ERROR GOTO](on-error-goto.md) but the actual file naming convention in other docs uses lowercase with hyphens. Should verify if this link target exists and matches naming convention.

---

#### documentation_inconsistency

**Description:** SWAP See Also section has incomplete reference format

**Affected files:**
- `docs/help/common/language/statements/swap.md`

**Details:**
swap.md See Also section has: '[LET](let.md) - To assign     the   value   of   an   expression   to   a variable' with excessive spacing in the description, suggesting copy-paste error or formatting issue.

---

#### documentation_inconsistency

**Description:** Different counts of optimizations in semantic analyzer

**Affected files:**
- `docs/help/mbasic/architecture.md`
- `docs/help/mbasic/features.md`

**Details:**
architecture.md states: "The semantic analyzer implements **18 distinct optimizations**" and lists all 18.

features.md states: "The interpreter includes an advanced semantic analyzer with 18 optimizations" and also lists all 18.

While both documents agree on the count (18), the lists should be verified to ensure they're identical and in the same order for consistency.

---

#### documentation_inconsistency

**Description:** Installation instructions reference non-existent repository

**Affected files:**
- `docs/help/mbasic/getting-started.md`

**Details:**
getting-started.md provides installation instructions:
"# Clone the repository
git clone https://github.com/avwohl/mbasic.git
cd mbasic"

This appears to be a placeholder URL. The actual repository URL should be verified and updated, or this should be noted as an example.

---

#### documentation_inconsistency

**Description:** Inconsistent description of Web UI debugging capabilities

**Affected files:**
- `docs/help/mbasic/features.md`
- `docs/help/mbasic/extensions.md`

**Details:**
features.md states about Web UI: "**Basic debugging** - Simple breakpoint support via menu"

extensions.md does not mention Web UI debugging capabilities at all in its debugging commands section, only listing CLI, Curses, and Tk.

If Web UI has basic debugging support, it should be documented in the extensions guide alongside the other UIs.

---

#### documentation_inconsistency

**Description:** Different keyboard shortcuts documented for Step functionality

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/cli/debugging.md`

**Details:**
curses/feature-reference.md documents 'Step Statement (Ctrl+T)' and 'Step Line (Ctrl+K)' as separate features. However, cli/debugging.md only documents 'STEP [n]' command with no mention of separate statement vs line stepping, and notes 'STEP INTO/OVER not yet implemented (use STEP)'. This suggests the Curses UI has more advanced stepping features than CLI, but the distinction between statement and line stepping is not explained in the CLI docs.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut usage explanation

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
curses/feature-reference.md states 'Cut/Copy/Paste (Not implemented)' and explains 'Note: Ctrl+X is used for Stop/Interrupt, Ctrl+C exits the program, and Ctrl+V is used for Save.' However, earlier in the same document under 'Save File (Ctrl+V)' it states 'Note: Uses Ctrl+V because Ctrl+S is reserved for terminal flow control.' This is consistent, but the Cut/Copy/Paste section also says 'Use your terminal's native copy/paste functions instead (typically Shift+Ctrl+C/V or mouse selection)' which suggests Shift+Ctrl+V might conflict with the documented Shift+Ctrl+V for Save As.

---

#### documentation_inconsistency

**Description:** Ambiguous feature count claim

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
curses/feature-reference.md title states 'This document covers all 36 features available in the Curses UI' but when counting the documented features: File Operations (8) + Execution & Control (6) + Debugging (6) + Variable Inspection (6) + Editor Features (6) + Help System (4) = 36 features. However, some items like 'Cut/Copy/Paste (Not implemented)' and 'Find/Replace (Not yet implemented)' are counted as features despite not being implemented. This inflates the feature count.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of line deletion methods

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`
- `docs/help/ui/curses/editing.md`

**Details:**
curses/feature-reference.md documents 'Delete Lines (Ctrl+D)' as a file operation feature. However, curses/editing.md documents a different method: 'To delete a line: 1. Navigate to the line 2. Delete all text after the line number 3. Press Enter' or 'type just the line number: Type: 10, Press Enter → Line 10 deleted'. No mention of Ctrl+D in the editing guide.

---

#### documentation_inconsistency

**Description:** Placeholder documentation marked as in progress

**Affected files:**
- `docs/help/ui/common/running.md`

**Details:**
running.md is marked as 'PLACEHOLDER - Documentation in progress' and states 'This page will cover: How to run BASIC programs, RUN command, Program execution, Stopping programs, Continuing after STOP'. This is incomplete documentation that should be finished or removed.

---

#### documentation_inconsistency

**Description:** Menu-only features not explained

**Affected files:**
- `docs/help/ui/curses/feature-reference.md`

**Details:**
curses/feature-reference.md mentions several features as 'Menu only' including 'List Program (Menu only)' and 'Execution Stack (Menu only)' but provides no information about how to access the menu bar, what key opens it, or how to navigate it. Users are told these features exist but not how to use them.

---

#### documentation_inconsistency

**Description:** Quit key inconsistency

**Affected files:**
- `docs/help/ui/curses/quick-reference.md`
- `docs/help/ui/curses/getting-started.md`

**Details:**
quick-reference.md lists: '**Ctrl+Q** | Quit' under Global Commands.

But getting-started.md lists: '**Q** - Quit' in the Essential Keys section (without Ctrl modifier).

These are different keys - one requires Ctrl, the other doesn't.

---

#### documentation_inconsistency

**Description:** Default UI startup command inconsistency

**Affected files:**
- `docs/help/ui/tk/getting-started.md`
- `docs/help/ui/index.md`

**Details:**
tk/getting-started.md states:
'```bash
mbasic --ui tk [filename.bas]
```

Or to use the default curses UI:
```bash
mbasic [filename.bas]
```'

This implies curses is the default. However, ui/index.md under Curses UI section states:
'```bash
mbasic                # Default UI
mbasic --ui curses
```'

Both documents agree curses is default, but the tk/getting-started.md phrasing 'Or to use the default curses UI' in a Tk getting started guide is confusing.

---

#### documentation_inconsistency

**Description:** Referenced file not provided

**Affected files:**
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/index.md`

**Details:**
tk/index.md references: '[Tips & Tricks](tips.md) - Best practices and productivity tips'

But the tips.md file for the Tk UI is not included in the provided documentation set. This is a broken link.

---

#### documentation_inconsistency

**Description:** Tips document references Ctrl+I for Smart Insert but workflows document doesn't mention this feature

**Affected files:**
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`

**Details:**
tips.md extensively uses Smart Insert:
'Use Ctrl+I (Smart Insert) to add details under each section without calculating line numbers!'
'Add comments with Ctrl+I (Smart Insert).'

workflows.md mentions it once:
'2. Press Ctrl+I (Smart Insert) to insert blank line'

But workflows.md doesn't explain what Smart Insert does or how it differs from just pressing Enter. This could confuse users following the workflow guide.

---

#### documentation_inconsistency

**Description:** Settings persistence location differs between Tk and Web but Web doc doesn't clearly explain localStorage limitations

**Affected files:**
- `docs/help/ui/tk/settings.md`
- `docs/help/ui/web/settings.md`

**Details:**
Tk settings.md clearly states:
'Location:
- Linux/Mac: ~/.mbasic/settings.json
- Windows: %APPDATA%\mbasic\settings.json'

Web settings.md mentions localStorage but buries important limitations:
'Settings are per-browser, per-domain
Clearing browser data clears settings
Settings don't sync across devices/browsers
Not shared with CLI/desktop versions'

This should be more prominent since it's a significant difference from Tk's persistent file storage.

---

#### documentation_inconsistency

**Description:** Workflows suggest using Ctrl+R to run without saving, but tips warn against this

**Affected files:**
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/tips.md`

**Details:**
workflows.md states:
'Fastest workflow:
```
Type → Ctrl+R (Run) → Check → Edit → Ctrl+R (Run) → Check → ...
```
No need to save between test runs! Save with Ctrl+S only when satisfied.'

But tips.md warns:
'Common Mistakes to Avoid
❌ Running without saving → Save often with Ctrl+S'

These contradict each other about when to save during development.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for loading files in web UI

**Affected files:**
- `docs/help/ui/web/web-interface.md`
- `docs/library/*/index.md`

**Details:**
web-interface.md uses:
'Load a .bas file from your computer (via browser file picker)'

library docs use:
'Click File → Open, select the downloaded file using browser file picker'

Both describe same action but use different menu names: 'Open' vs 'Load'

---

#### documentation_inconsistency

**Description:** Library statistics count mismatch

**Affected files:**
- `docs/library/index.md`
- `docs/library/*/index.md`

**Details:**
docs/library/index.md states:
'Total Programs: 114+'

But counting all programs listed in category index files:
- Games: 141 programs
- Utilities: 18 programs
- Education: 3 programs
- Business: 8 programs
- Electronics: 13 programs
- Ham Radio: 7 programs
- Data Management: 5 programs
- Telecommunications: 5 programs
- Demos: 5 programs
Total: 205 programs

The '114+' count is significantly lower than actual count.

---

#### documentation_inconsistency

**Description:** Category count mismatch in library statistics

**Affected files:**
- `docs/library/index.md`

**Details:**
Library index states:
'Categories: 9'

But lists 9 categories in the page. This is actually consistent, but the phrasing 'Categories: 9' appears after listing all 9, making it redundant rather than a summary.

---

#### documentation_inconsistency

**Description:** Settings dialog mentioned but not documented in menu sections

**Affected files:**
- `docs/help/ui/web/web-interface.md`

**Details:**
web-interface.md Auto-Numbering section mentions:
'Use the Settings dialog (⚙️ icon) to change the increment or disable auto-numbering entirely'

But the Menu Functions section does not list a Settings menu or ⚙️ icon option. Users won't know where to find this feature.

---

#### documentation_inconsistency

**Description:** Malformed program entry in utilities index

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
One entry shows:
'### Remarks:  This program will con

**Year:** 1980s
**Tags:** 

**[Download hex2data.bas](hex2data.bas)**'

The title 'Remarks: This program will con' appears to be truncated program comments rather than a proper title. Should likely be '### Hex2data' or similar.

---

#### documentation_inconsistency

**Description:** Inconsistent program entry formatting

**Affected files:**
- `docs/library/utilities/index.md`

**Details:**
Most entries have format:
'### ProgramName

**Year:** 1980s
**Tags:**'

But some have additional fields:
'### Survival

**Author:** R Logan & Ian Lycholm CBASIC 2 VER
**Year:** 1982'

'### Un-Prot

Fixup for ** UN.COM **

**Year:** 1980s'

'### Xextract

0 -->END PAGE / 1-20 -->EXTRACT ITEM / 21 -->RESTART'

Inconsistent metadata structure across entries.

---

#### documentation_inconsistency

**Description:** Duplicate calendar program in games and utilities

**Affected files:**
- `docs/library/games/index.md`

**Details:**
Calendar.bas appears in both:
- docs/library/games/index.md
- docs/library/utilities/index.md

Same filename, same year (1980s). Unclear if this is intentional (same program in multiple categories) or an error.

---

#### documentation_inconsistency

**Description:** Inconsistent UI name capitalization

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`
- `docs/user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md uses 'Curses' (capitalized) throughout, while QUICK_REFERENCE.md title uses 'MBASIC Curses IDE' but the filename and other references use lowercase 'curses'. The command line flag is '--ui curses' (lowercase) in both documents.

---

#### documentation_inconsistency

**Description:** Inconsistent mouse support indicators

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
In the Decision Matrix table, Curses UI shows mouse support as '⚠️' (warning/partial), but in the 'Unique advantages' section for Curses, it lists 'Limited mouse support' as a limitation. The CLI section says 'No mouse support' with ❌. The distinction between 'limited' (⚠️) and 'no' (❌) mouse support is unclear.

---

#### documentation_inconsistency

**Description:** Inconsistent feature availability timeline

**Affected files:**
- `docs/user/CHOOSING_YOUR_UI.md`

**Details:**
The document states 'Which UI gets new features first?' with an ordered list (Tk, Web, Curses, CLI), but earlier states that Curses has 'No Find/Replace yet' implying it's planned, while the Tk section shows Find/Replace as already available. The timeline for when features move between UIs is unclear.

---

#### documentation_inconsistency

**Description:** Missing file references in examples

**Affected files:**
- `docs/user/QUICK_REFERENCE.md`

**Details:**
QUICK_REFERENCE.md references example files 'test_continue.bas', 'demo_continue.bas', and 'test_continue_manual.sh' but these files are not provided and their location is not specified. Also references multiple .md files (DEBUGGER_COMMANDS.md, CONTINUE_FEATURE.md, BREAKPOINT_SUMMARY.md, HELP_SYSTEM_SUMMARY.md) that are not in the provided documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent Python command usage

**Affected files:**
- `docs/user/INSTALL.md`

**Details:**
INSTALL.md uses 'python3' throughout most examples but then suggests 'Try using python instead of python3' in troubleshooting. The guide should be consistent about which command to use or clearly explain when to use each.

---

#### documentation_inconsistency

**Description:** Incomplete directory description

**Affected files:**
- `docs/user/README.md`

**Details:**
README.md states this directory contains 'Installation guides' (plural) but only lists QUICK_REFERENCE.md, URWID_UI.md, and FILE_FORMAT_COMPATIBILITY.md. It doesn't mention INSTALL.md, INSTALLATION.md, CHOOSING_YOUR_UI.md, or SETTINGS_AND_CONFIGURATION.md which are all present in the same directory.

---

#### documentation_inconsistency

**Description:** Inconsistent documentation of Variables window shortcut

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`
- `docs/user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md documents two different shortcuts for Variables window:
| **Ctrl+V** | Show/hide Variables window |
| **Ctrl+W** | Show/hide Variables & Resources window |

keyboard-shortcuts.md (Curses) documents:
| `Ctrl+W` | Toggle variables watch window |

UI_FEATURE_COMPARISON.md shows:
| **Variables** | WATCH | Ctrl+W | Ctrl+V | Ctrl+Alt+V |

This suggests Ctrl+V is Tk-specific and Ctrl+W is Curses-specific, but TK_UI_QUICK_START.md lists both Ctrl+V and Ctrl+W for Tk, which may be confusing or incorrect.

---

#### documentation_inconsistency

**Description:** Inconsistent date format in documentation

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md uses 'October 2025' in two places:
## Variable Case Preservation (New in October 2025)
## Improved Debugging Features (October 2025)

But UI_FEATURE_COMPARISON.md uses specific date:
### Recently Added (2025-10-29)

For consistency, either both should use 'October 2025' or both should use '2025-10-29'.

---

#### documentation_inconsistency

**Description:** Incomplete feature status in comparison table

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md shows:
| **Find/Replace** | ❌ | ❌ | ✅ | ❌ | Tk only (new feature) |

But the 'Coming Soon' section states:
### Coming Soon
- ⏳ Find/Replace in Web UI

This suggests Web UI Find/Replace is planned, but the main table shows it as ❌ (Not Available) rather than ⏳ (Coming Soon). The table should use a consistent symbol for planned features.

---

#### documentation_inconsistency

**Description:** Duplicate Execution Stack window shortcut documentation

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
TK_UI_QUICK_START.md documents:
| **Ctrl+K** | Show/hide Execution Stack window |

But later in the same document:
### Execution Stack Window
Press **Ctrl+K** to see the execution stack...

This is consistent within the document, but keyboard-shortcuts.md (Curses) shows:
| `Ctrl+K` | Step Line - execute all statements on current line |

And:
| `Menu only` | Show/hide execution stack window |

This indicates Ctrl+K has different meanings in Tk (Execution Stack) vs Curses (Step Line), and Curses requires menu access for Execution Stack. TK_UI_QUICK_START.md should clarify this is Tk-specific.

---

#### documentation_inconsistency

**Description:** Incomplete cross-reference in sequential files documentation

**Affected files:**
- `docs/user/sequential-files.md`

**Details:**
sequential-files.md has a 'See Also' section:
- [OPEN Statement](../help/common/language/statements/open.md)
- [INPUT# Statement](../help/common/language/statements/input_hash.md)
- [LINE INPUT# Statement](../help/common/language/statements/line-input.md)
- [EOF Function](../help/common/language/functions/eof.md)
- [Compatibility Guide](../help/mbasic/compatibility.md)

However, these referenced files are not provided in the documentation set, so it's impossible to verify if the links are correct or if the referenced documentation exists. This is a potential broken link issue.

---

#### documentation_inconsistency

**Description:** Inconsistent feature status symbols

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md uses:
✅ Available | ⚠️ Partial | ❌ Not Available

But in 'Coming Soon' section uses:
- ⏳ DATA/READ/RESTORE statements

The ⏳ symbol is not defined in the legend at the top of the document. For consistency, either add ⏳ to the legend or use ⚠️ for planned features.

---


## Summary

- Total issues found: 705
- Code/Comment conflicts: 238
- Other inconsistencies: 467
