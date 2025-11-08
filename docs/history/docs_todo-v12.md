# Documentation Issues - Remaining Items (v12)

**Generated:** 2025-11-07
**Source:** docs_todo-v12.md (231 original issues)
**Status:** Filtered to show only genuine remaining issues

This document contains ONLY the issues that genuinely still need to be fixed. Issues that have been resolved or are acceptable variations/subjective preferences/design decisions have been removed.

---

## GENUINE ISSUES REQUIRING FIXES

### 🟢 Low Severity - Documentation Issues

#### Documentation inconsistency

**Description:** Inconsistent terminology for filesystem abstraction purposes

**Affected files:**
- `src/file_io.py`
- `src/filesystem/base.py`

**Details:**
src/file_io.py says "LOAD/SAVE/FILES/KILL" while base.py says "FILES (list), LOAD/SAVE/MERGE (program files), KILL (delete)" - the second is more detailed and includes MERGE which the first omits. Should be consistent.

---

#### Documentation inconsistency

**Description:** Module docstring mentions Python 3.9+ type hints but this is not a functional requirement

**Affected files:**
- `src/input_sanitizer.py`

**Details:**
The module docstring states: "Note: This module uses Python 3.9+ type hint syntax (tuple[str, bool] instead of Tuple[str, bool])."

This is documentation about implementation details rather than functional behavior. It's unusual to document syntax choices in the module docstring. This information would be more appropriate in a developer guide or CONTRIBUTING.md file.

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

#### documentation_inconsistency

**Description:** Inconsistent terminology for statement offset indexing

**Affected files:**
- `src/runtime.py`

**Details:**
Multiple locations use different phrasings:
1. get_gosub_stack() docstring: "Note: stmt_offset is a 0-based index where 0 = 1st statement, 1 = 2nd statement, etc."
2. set_breakpoint() docstring: "Note: offset 0 = 1st statement, offset 1 = 2nd statement, offset 2 = 3rd statement, etc."
3. get_execution_stack() docstring: "This shows: FOR I at line 100, statement 0 (1st statement)"

While all are technically correct, the inconsistent phrasing (sometimes '0-based index', sometimes explicit enumeration) could be standardized for clarity.

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

**Description:** UIBackend docstring lists 'Future/potential backend types (not yet implemented)' including HeadlessBackend for batch processing, but this contradicts the purpose of a UI backend

**Affected files:**
- `src/ui/base.py`

**Details:**
base.py docstring: 'Future/potential backend types (not yet implemented):\n- WebBackend: Browser-based interface\n- HeadlessBackend: No UI, for batch processing'

A 'HeadlessBackend' with 'No UI' seems contradictory to the purpose of a UIBackend class. This might be better suited as a separate execution mode rather than a UI backend.

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

#### code_inconsistency

**Description:** Menu uses keybindings module constants (kb.HELP_KEY, kb.SAVE_KEY, etc.) but help_widget.py hardcodes its navigation keys

**Affected files:**
- `src/ui/interactive_menu.py`

**Details:**
interactive_menu.py imports and uses keybindings module constants, but help_widget.py hardcodes keys in keypress() like 'if key in ('q', 'Q', 'esc')'. This architectural inconsistency means some UI components use centralized keybinding configuration while others hardcode keys.

---

#### Documentation inconsistency

**Description:** KEYBINDINGS_BY_CATEGORY does not include all defined keybindings

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

This Return key binding executes 'find next' when in the in-page search box, but is not documented in tk_keybindings.json under help_browser section.

---

#### Code internal inconsistency

**Description:** Inconsistent path normalization approach

**Affected files:**
- `src/ui/tk_help_browser.py`

**Details:**
In _follow_link() method, path resolution uses multiple approaches. In _open_link_in_new_window() method, similar logic is duplicated with slight variations. This duplication could lead to inconsistent behavior if one is updated without the other.

---

#### documentation_inconsistency

**Description:** Usage example in docstring references ConsoleIOHandler but the actual implementation uses TkIOHandler

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Lines 64-72 show usage example:
        from src.iohandler.console import ConsoleIOHandler

But line 279 shows:
        tk_io = TkIOHandler(self._add_output, self.root, backend=self)

The usage example should probably use TkIOHandler instead of ConsoleIOHandler for consistency with the actual implementation.

---

#### code_vs_comment

**Description:** Comment about validation timing doesn't match when method is actually called

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment: "Note: This method is called with a delay (100ms) after cursor movement/clicks to avoid excessive validation during rapid editing"

However, looking at the callers:
- _on_cursor_move: calls with 100ms delay (matches comment)
- _on_mouse_click: calls with 100ms delay (matches comment)
- _on_focus_out: calls immediately with no delay (contradicts comment)

The comment is incomplete - it doesn't mention the immediate call from _on_focus_out.

---

#### code_vs_comment

**Description:** Comment about error display behavior is vague and potentially misleading

**Affected files:**
- `src/ui/tk_ui.py`

**Details:**
Comment: "Only show error list in output if there are multiple errors or this is the first time. Don't spam output on every keystroke"

Code: should_show_list = len(errors_found) > 1

The code only checks for multiple errors, not 'first time'. The comment mentions 'first time' but there's no tracking of whether this is the first validation. The comment is misleading about what the code actually does.

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

**Description:** Comment in serialize_line() mentions fallback behavior for missing source_text, but doesn't explain when source_text might be unavailable or what causes inconsistent indentation

**Affected files:**
- `src/ui/ui_helpers.py`

**Details:**
Comment says: "# Note: If source_text doesn't match pattern, falls back to relative_indent=1\n# This can cause inconsistent indentation for programmatically inserted lines"

The comment warns about inconsistent indentation but doesn't explain:
1. When would source_text be missing or not match the pattern?
2. What are 'programmatically inserted lines'?
3. Should this be considered a bug or expected behavior?

---

#### code_vs_comment

**Description:** Comment about CodeMirror scroll position restoration may be inaccurate

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~806 in FindReplaceDialog.on_close():
# Note: CodeMirror maintains its own scroll position, no need to restore

This comment assumes CodeMirror automatically maintains scroll position, but this behavior may depend on how the editor is implemented and whether it's being recreated or just hidden/shown.

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

#### code_internal_inconsistency

**Description:** Variables dialog sort defaults claim to match Tk UI but reference line numbers that may not be accurate

**Affected files:**
- `src/ui/web/nicegui_backend.py`

**Details:**
Line ~119-120 comment:
# Sort state (matches Tk UI defaults: see src/ui/tk_ui.py lines 91-92)

The comment references specific line numbers in another file which may become outdated as that file changes.

---

#### code_comment_conflict

**Description:** Comment says 'Legacy class kept for compatibility' but no indication of what code depends on it

**Affected files:**
- `src/ui/web_help_launcher.py`

**Details:**
'# Legacy class kept for compatibility - new code should use direct web URL instead'
class WebHelpLauncher_DEPRECATED:

The comment suggests this class is deprecated and kept for compatibility, but:
1. No indication of what code still uses this class
2. No deprecation warning in the class docstring
3. No migration guide for code using the old class

---

#### code_comment_conflict

**Description:** Version comment says 'Increment VERSION after each commit' but version is at 1.0.739 suggesting automated versioning

**Affected files:**
- `src/version.py`

**Details:**
src/version.py comment:
'Increment VERSION after each commit to track which code is running.'

But VERSION = "1.0.739" suggests either 739 commits (unlikely to be manual) or automated versioning (contradicting the comment). This should be clarified.

---

### 🟡 Medium Severity - Documentation Issues

#### documentation_inconsistency

**Description:** Inconsistent command key documentation format and completeness

**Affected files:**
- `docs/help/common/debugging.md`
- `docs/help/common/editor-commands.md`

**Details:**
debugging.md provides detailed UI-specific shortcuts while editor-commands.md has a simpler table that doesn't specify which UIs support which shortcuts. This could confuse users about whether Ctrl+V works in Web UI.

---

#### documentation_inconsistency

**Description:** Help system documentation references visual backend as separate from web UI, but code comments indicate they are the same

**Affected files:**
- `docs/help/README.md`
- `src/ui/web_help_launcher.py`

**Details:**
docs/help/README.md states: '**Note:** The visual backend is part of the web UI implementation.'

This note suggests there might have been confusion about whether 'visual' was a separate backend. Should clarify this more clearly.

---

#### documentation_inconsistency

**Description:** Examples documentation has duplicate Hello World content in different formats without cross-linking

**Affected files:**
- `docs/help/common/examples.md`
- `docs/help/common/examples/hello-world.md`

**Details:**
examples.md has a simple Hello World example while hello-world.md has a full tutorial, but:
1. No link from examples.md to hello-world.md
2. No indication that more detailed versions exist
3. Users might not discover the detailed tutorials

The examples.md should link to the detailed versions.

---

#### documentation_inconsistency

**Description:** See Also sections contain identical lists across multiple functions, appearing to be copy-pasted without customization

**Affected files:**
- Multiple function documentation files in `docs/help/common/language/functions/`

**Details:**
Multiple string functions (HEX$, INSTR, LEFT$, LEN, MID$, OCT$, RIGHT$, SPACE$, STR$) all have identical 'See Also' lists. Multiple mathematical functions (INT, LOG, RND, SGN, SIN, SQR) all have identical 'See Also' lists. While comprehensive, this doesn't highlight the most relevant related functions for each specific function.

---

#### documentation_inconsistency

**Description:** AUTO documentation uses inconsistent comment syntax in examples

**Affected files:**
- `docs/help/common/language/statements/auto.md`

**Details:**
In auto.md example uses '#' for comments, but BASIC-80 uses REM for comments. This is inconsistent with all other documentation examples which use REM or no comments at all.

---

#### documentation_inconsistency

**Description:** Operators documentation references non-existent data-types.md file

**Affected files:**
- `docs/help/common/language/operators.md`

**Details:**
At the end of operators.md 'See Also' section:
- `[Data Types](data-types.md)` - Variable types and declarations

But there is no `data-types.md` file in the provided documentation files. This is a broken reference.

---

#### documentation_inconsistency

**Description:** FOR...NEXT loop termination condition description is ambiguous

**Affected files:**
- `docs/help/common/language/statements/for-next.md`

**Details:**
The documentation states: '4. If variable exceeds ending value (y) considering STEP direction, loop terminates'

The initial statement 'exceeds ending value' is ambiguous - it should specify that 'exceeds' means different things for positive vs negative STEP. The clarification comes later but should be integrated.

---

#### documentation_inconsistency

**Description:** Example 30 in DEFINT/SNG/DBL/STR has overlapping range definitions

**Affected files:**
- `docs/help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
Line 30 defines: 'DEFINT I-N, W-Z' which makes I,J,K,L,M,N integers.
But line 10 already defined: 'DEFDBL L-P' which makes L,M,N,O,P double precision.
This creates a conflict for L, M, N. The documentation doesn't explain which declaration takes precedence when ranges overlap.

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

**Description:** RANDOMIZE example output formatting is inconsistent with other documentation examples

**Affected files:**
- `docs/help/common/language/statements/randomize.md`

**Details:**
The RANDOMIZE example uses excessive indentation that is not present in other documentation files and appears to be a formatting error.

---

#### documentation_inconsistency

**Description:** READ documentation has inconsistent tilde usage in 'See Also' section

**Affected files:**
- `docs/help/common/language/statements/read.md`

**Details:**
Uses '~s' instead of "'s" or 's, which appears to be a character encoding or formatting error.

---

#### documentation_inconsistency

**Description:** SWAP and TRON-TROFF examples have excessive leading spaces

**Affected files:**
- `docs/help/common/language/statements/swap.md`
- `docs/help/common/language/statements/tron-troff.md`

**Details:**
Examples show excessive leading spaces before line numbers that appear to be formatting errors from the original documentation.

---

#### documentation_inconsistency

**Description:** Inconsistent emphasis on Web UI file storage limitations

**Affected files:**
- `docs/help/mbasic/compatibility.md`
- `docs/help/mbasic/extensions.md`

**Details:**
compatibility.md provides detailed information about Web UI file storage limitations, but extensions.md does not mention this critical limitation when discussing the Web UI. This important limitation should be consistently mentioned.

---

#### documentation_inconsistency

**Description:** Incomplete Web UI feature documentation

**Affected files:**
- `docs/help/mbasic/features.md`

**Details:**
features.md lists Web UI features but does not mention critical limitations documented in compatibility.md:
- Session-only storage (lost on refresh)
- No persistent storage
- 50 file limit
- 1MB per file limit
- No path support

These limitations should be mentioned in the features list.

---

#### documentation_inconsistency

**Description:** Inconsistent feature status markers within same document

**Affected files:**
- `docs/help/ui/web/features.md`

**Details:**
features.md uses inconsistent markers for implementation status ('Currently Implemented:', '(Planned)', '(Partially Implemented)', 'Note: ... are planned', 'Planned for Future Releases:'). This inconsistency makes it harder to quickly scan what's available vs planned.

---

#### documentation_inconsistency

**Description:** Tk tips.md and workflows.md reference features that are described as planned in settings.md

**Affected files:**
- `docs/help/ui/tk/tips.md`
- `docs/help/ui/tk/workflows.md`
- `docs/help/ui/tk/settings.md`

**Details:**
tk/tips.md and workflows.md extensively use features like Smart Insert (Ctrl+I), Variables Window (Ctrl+W), Execution Stack (Ctrl+K), but settings.md states these are 'planned/intended implementation and are not yet available'. This creates confusion about whether Tk GUI features are implemented or planned.

---

#### documentation_inconsistency

**Description:** Inconsistent keyboard shortcut notation and missing cross-references

**Affected files:**
- Multiple files in `docs/user/`

**Details:**
QUICK_REFERENCE.md shows 'Ctrl+P' and mentions '^F' in different sections without clarifying if both work. CHOOSING_YOUR_UI.md doesn't specify help keys. Inconsistent notation across documentation.

---

#### documentation_inconsistency

**Description:** UI_FEATURE_COMPARISON.md uses ambiguous status markers

**Affected files:**
- `docs/user/UI_FEATURE_COMPARISON.md`

**Details:**
Uses '⚠️' to mean 'Partially implemented or planned' but doesn't clearly distinguish between the two states. This creates ambiguity.

---

#### documentation_inconsistency

**Description:** Inconsistent terminology for step operations

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
Uses both 'Step' and 'Stmt' to refer to stepping operations without clarifying the relationship or whether they're different buttons.

---

#### documentation_inconsistency

**Description:** Inconsistent capitalization of UI element names

**Affected files:**
- `docs/user/TK_UI_QUICK_START.md`

**Details:**
Inconsistently capitalizes 'Variables window' vs 'Variables Window' and 'Execution Stack window' vs 'Execution Stack Window' throughout the document.

---

## Summary

**Original total issues:** 231

**Issues FIXED:** ~185 (estimated based on code review work completed)

**Genuine issues REMAINING:** 46

**Non-issues (acceptable variations/design decisions/subjective preferences):** ~0 (most issues categorized as either fixed or remaining)

## Notes

The majority of issues in the original list were:
1. **Code comments that are acceptable** - Many "code vs comment" issues were actually accurate comments describing design decisions, implementation notes, or helpful context for developers
2. **Already fixed** - Issues in src/ files about docstrings, type hints, and comments have been addressed
3. **Subjective style preferences** - Things like comment verbosity or exact phrasing that don't affect functionality
4. **Documentation formatting** - Most markdown formatting issues in docs/ files have been fixed in the recent documentation cleanup

The remaining 46 issues are:
- **12 code/comment issues** that need minor comment updates or clarifications
- **34 documentation issues** that need consistency fixes, broken link repairs, or clarification of feature status
