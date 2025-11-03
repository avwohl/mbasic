# Documentation Inconsistencies Report

Generated: 2025-11-03 13:35:38
Scanned directories: help, library, stylesheets, user

Found 122 inconsistencies:

## 🔴 High Severity

### function_name_inconsistency

**Description:** CHR$ function has two different filenames and inconsistent references

**Affected files:**
- `help/common/language/functions/chr_dollar.md`
- `help/common/language/functions/crr_dollar.md`
- `help/common/language/functions/index.md`

**Details:**
The CHR$ function appears as both 'chr_dollar.md' and 'crr_dollar.md'. In chr_dollar.md, the title is 'CHR$' with syntax 'CHR$(I)'. In crr_dollar.md, the title is 'CRR$' with syntax 'CHR$(I)'. The index.md file references it as 'CHR$' but links to 'crr_dollar.md'. The 'See Also' sections in other files link to 'chr_dollar.md'.

---

### function_name_inconsistency

**Description:** CDBL function has two different filenames with different titles

**Affected files:**
- `help/common/language/functions/cdbl.md`
- `help/common/language/functions/cobl.md`
- `help/common/language/functions/index.md`

**Details:**
The function appears as both 'cdbl.md' (title: CDBL, syntax: CDBL(X)) and 'cobl.md' (title: COBL, syntax: COBL(X)). The index.md references it as 'CDBL' but links to 'cobl.md'. The 'See Also' sections reference 'cdbl.md'.

---

### contradictory_information

**Description:** DEF FN documentation states function names can be multiple characters, but DEFINT/SNG/DBL/STR documentation contains a DEF USR section that appears to be incorrectly placed and formatted

**Affected files:**
- `help/common/language/statements/def-fn.md`
- `help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
In defint-sng-dbl-str.md, there is a section '2.13 ~ USR' with 'Format: DEF USR[<digit>]=<integer expression>' that appears to be documentation for a different statement (DEF USR) incorrectly included in the DEFINT/SNG/DBL/STR file. This content should likely be in a separate DEF USR documentation file or removed if it's legacy content.

---

### missing_information

**Description:** DEF USR content appears incomplete and improperly formatted

**Affected files:**
- `help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
The DEF USR section in defint-sng-dbl-str.md shows: '2.13 ~ USR' with unusual formatting ('~' character), and the example section ends abruptly with '."' suggesting truncated or corrupted content. This appears to be legacy content that was not properly integrated.

---

### contradictory_information

**Description:** ERASE documentation states MBASIC compiler does not support ERASE, but this is a MBASIC interpreter implementation

**Affected files:**
- `help/common/language/statements/erase.md`

**Details:**
ERASE.md states 'NOTE: The MBASIC compiler does not support ERASE.' This note refers to a compiler vs interpreter distinction that may be confusing in the context of this Python-based MBASIC interpreter implementation.

---

### duplicate_documentation

**Description:** Two separate documentation files exist for the MID$ assignment statement with different content and organization

**Affected files:**
- `help/common/language/statements/mid-assignment.md`
- `help/common/language/statements/mid_dollar.md`

**Details:**
mid-assignment.md provides comprehensive documentation with clear syntax 'MID$(string-var, start[, length]) = string-expression' and detailed examples. mid_dollar.md has incomplete/malformed syntax 'MID$«string expl>,n[,m])=<string exp2>' with unusual character encoding and less clear documentation. Both claim to document the same MID$ assignment statement but with different quality and completeness.

---

### contradictory_information

**Description:** RESUME and RESTORE statements have conflicting 'related' metadata

**Affected files:**
- `help/common/language/statements/resume.md`
- `help/common/language/statements/restore.md`

**Details:**
RESUME.md lists 'related: [error, on-error-goto]' but links to ERROR and ON ERROR GOTO in See Also. RESTORE.md lists 'related: [read, data]' and links match. However, RESUME.md's See Also section includes links to ERROR and ON ERROR GOTO statements, but these don't appear to have corresponding documentation files based on the naming pattern used elsewhere.

---

### contradictory_information

**Description:** Implementation note contradicts syntax documentation

**Affected files:**
- `help/common/language/statements/width.md`

**Details:**
WIDTH.md states 'The "WIDTH LPRINT" syntax is not supported (parse error). Only the simple "WIDTH <number>" form is accepted.' but the Syntax section shows 'WIDTH LPRINT <integer expression>' as part of original MBASIC 5.21 syntax. The implementation note should clarify this is historical documentation only.

---

### broken_reference

**Description:** Reference to non-existent running.md file

**Affected files:**
- `help/common/ui/curses/editing.md`

**Details:**
The 'See Also' section references '../../../ui/curses/running.md' but this file is not included in the provided documentation set. The correct path should likely be '../../ui/curses/running.md' or the file is missing.

---

### feature_availability_conflict

**Description:** Debugging features availability inconsistency

**Affected files:**
- `help/mbasic/extensions.md`
- `help/mbasic/features.md`

**Details:**
extensions.md states debugging commands (BREAK, STEP, WATCH, STACK) are 'CLI Only' and 'exclusive to the CLI backend'. However, features.md under 'Debugging' section lists 'Breakpoints', 'Step execution', 'Variable watch', and 'Stack viewer' as '(UI-dependent)' suggesting they work in multiple UIs, not just CLI.

---

### command_inconsistency

**Description:** CLI debugging documentation mentions WATCH command that doesn't exist in the command reference

**Affected files:**
- `help/ui/cli/debugging.md`
- `help/ui/cli/variables.md`

**Details:**
In help/ui/cli/index.md under 'Debugging Commands', it lists 'WATCH - Inspect variables', but help/ui/cli/debugging.md only documents BREAK, STEP, and STACK commands. The help/ui/cli/variables.md file explains that CLI uses PRINT for variable inspection, not a WATCH command.

---

### keyboard_shortcut_conflict

**Description:** Ctrl+L shortcut assigned to two different functions

**Affected files:**
- `help/ui/curses/feature-reference.md`

**Details:**
In help/ui/curses/feature-reference.md, Ctrl+L is listed both as 'List Program' under 'Execution & Control' and as 'Step Line (Ctrl+L when paused)' under 'Debugging'. The same shortcut cannot perform two different functions.

---

### keyboard_shortcut_conflict

**Description:** Ctrl+X shortcut assigned to two different functions

**Affected files:**
- `help/ui/curses/feature-reference.md`

**Details:**
In help/ui/curses/feature-reference.md, Ctrl+X is listed as 'Stop/Interrupt' under 'Execution & Control' but also as 'Cut' under 'Editor Features' (Cut/Copy/Paste section states 'Cut: Ctrl+X').

---

### keyboard_shortcut_inconsistency

**Description:** Conflicting keyboard shortcuts for loading programs

**Affected files:**
- `help/ui/curses/files.md`
- `help/ui/curses/keyboard-commands.md`

**Details:**
files.md states 'Press **b** or **Ctrl+O**' for loading, but keyboard-commands.md only lists 'Ctrl+O' for Load program. The 'b' key is listed as 'Toggle breakpoint' in keyboard-commands.md, creating a direct conflict.

---

### keyboard_shortcut_inconsistency

**Description:** Different shortcuts listed for the same actions

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
keyboard-commands.md lists 'Ctrl+E' for 'Renumber program lines (RENUM command)', but quick-reference.md shows 'Ctrl+E' under Editing section without mentioning renumber. Also, keyboard-commands.md shows 'Ctrl+A' and 'Ctrl+E' as alternatives for Home/End, but quick-reference.md doesn't mention these alternatives.

---

### keyboard_shortcut_inconsistency

**Description:** Function key references conflict with stated design

**Affected files:**
- `help/ui/curses/running.md`
- `help/ui/curses/keyboard-commands.md`

**Details:**
running.md mentions 'Press **F2** or **Ctrl+R**' and 'Press **F3** or **Ctrl+L**', but keyboard-commands.md explicitly states 'No function keys required! All commands use Ctrl or regular keys.'

---

### keyboard_shortcut_inconsistency

**Description:** Conflicting shortcuts for Step Line command

**Affected files:**
- `help/ui/curses/quick-reference.md`
- `help/ui/curses/keyboard-commands.md`

**Details:**
quick-reference.md shows 'Ctrl+L' as 'Step Line - execute all statements on current line' in debugger section, but keyboard-commands.md shows 'Ctrl+L' as 'List program to output window' in Program Commands section.

---

### keyboard_shortcut_conflict

**Description:** Ctrl+H is mapped to two different functions in Tk UI documentation

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/tk/index.md`

**Details:**
In keyboard-shortcuts.md, Ctrl+H is listed as 'Find and replace (opens Replace dialog)' under Editor Commands. However, in index.md under Help System section, it states 'F1 or Ctrl+H - Open help topics'. The same shortcut cannot perform both functions.

---

### feature_availability_conflict

**Description:** Contradictory information about debugger support in Web UI

**Affected files:**
- `help/ui/web/keyboard-shortcuts.md`
- `help/ui/web/web-interface.md`

**Details:**
keyboard-shortcuts.md extensively documents debugging features (breakpoints, variables window, stack window, step debugging) with statements like 'Click line number → Toggle breakpoint on that line' and 'Variables Window' section. However, web-interface.md states under Limitations: 'No debugger or breakpoint support (yet)'. This is a direct contradiction about whether debugging features are available.

---

### keyboard_shortcut_inconsistency

**Description:** Inconsistent keyboard shortcuts for Variables window across different UI documentation

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md mentions 'Ctrl+W in TK UI' for Variables & Resources window. TK_UI_QUICK_START.md lists both 'Ctrl+V' for Variables window and 'Ctrl+W' for Variables & Resources window. keyboard-shortcuts.md (Curses UI) uses 'Ctrl+W' for toggle variables watch window. This creates confusion about which shortcut does what in which UI.

---

## 🟡 Medium Severity

### missing_reference

**Description:** README.md lists entry points for common and curses help, but omits tk, cli, and visual backend entry points that are mentioned in the structure section

**Affected files:**
- `help/README.md`
- `help/common/index.md`

**Details:**
README.md 'Entry Points' section only lists:
- **Common Help**: [common/index.md](common/index.md)
- **Curses Help**: [ui/curses/index.md](ui/curses/index.md)

But earlier mentions '/ui/cli', '/ui/tk', and '/ui/visual' directories without providing their index.md entry points.

---

### inconsistent_reference

**Description:** Conflicting information about UI-specific help locations

**Affected files:**
- `help/common/getting-started.md`
- `help/common/editor-commands.md`

**Details:**
getting-started.md says 'See your UI-specific help for how to type programs' and links to:
- [Curses UI](ui/curses/editing.md)
- [Tkinter UI](ui/tk/index.md)
- [CLI](ui/cli/index.md)

But editor-commands.md doesn't mention being UI-specific and provides generic commands without clarifying which UI they apply to.

---

### inconsistent_information

**Description:** Optimization count mismatch in documentation

**Affected files:**
- `help/common/compiler/optimizations.md`
- `help/common/compiler/index.md`

**Details:**
optimizations.md states '27 optimizations implemented' in both the title metadata and Summary section. However, when counting the documented optimizations, there are exactly 27 listed, so this is actually consistent. No inconsistency found here upon recount.

---

### function_name_inconsistency

**Description:** SPACE$ function has inconsistent filename references

**Affected files:**
- `help/common/language/functions/space_dollar.md`
- `help/common/language/functions/spaces.md`
- `help/common/language/functions/index.md`

**Details:**
The function is referenced as both 'space_dollar.md' and 'spaces.md'. In index.md under 'String Functions', it links to 'spaces.md'. In 'See Also' sections of other files, it's referenced as 'space_dollar.md'.

---

### missing_reference

**Description:** Typo in ABS function syntax section

**Affected files:**
- `help/common/language/functions/abs.md`

**Details:**
In abs.md, the syntax is listed as 'ASS (X)' instead of 'ABS(X)' - appears to be a typo with double 'S'.

---

### inconsistent_see_also_references

**Description:** String function files have inconsistent references to MID$ in their See Also sections

**Affected files:**
- `help/common/language/functions/instr.md`
- `help/common/language/functions/len.md`
- `help/common/language/functions/mid_dollar.md`
- `help/common/language/functions/oct_dollar.md`
- `help/common/language/functions/space_dollar.md`
- `help/common/language/functions/spc.md`
- `help/common/language/functions/str_dollar.md`
- `help/common/language/functions/string_dollar.md`
- `help/common/language/functions/left_dollar.md`
- `help/common/language/functions/right_dollar.md`

**Details:**
Most string functions (instr.md, len.md, mid_dollar.md, oct_dollar.md, space_dollar.md, spc.md, str_dollar.md, string_dollar.md) reference only '[MID$ Assignment](../statements/mid-assignment.md)'. However, left_dollar.md and right_dollar.md reference both '[MID$](mid_dollar.md)' as a function AND '[MID$](../statements/mid_dollar.md)' as a statement, plus '[MID$ Assignment](../statements/mid-assignment.md)'. This creates three different ways of referencing MID$ across the documentation.

---

### missing_description_placeholder

**Description:** SGN function has 'NEEDS_DESCRIPTION' in both description field and See Also references

**Affected files:**
- `help/common/language/functions/sgn.md`

**Details:**
sgn.md has 'description: NEEDS_DESCRIPTION' in the frontmatter, and multiple other mathematical function files reference it as '- [SGN](sgn.md) - NEEDS_DESCRIPTION' in their See Also sections. This is the only function with an incomplete description.

---

### missing_cross_reference

**Description:** DEF FN documentation does not reference USR function in See Also section, but USR is mentioned in defint-sng-dbl-str.md

**Affected files:**
- `help/common/language/statements/def-fn.md`
- `help/common/language/functions/usr.md`

**Details:**
The defint-sng-dbl-str.md file contains DEF USR documentation that references 'See Appendix C, Assembly_ Language Subroutines' and mentions USR function, but def-fn.md (which documents user-defined functions) does not cross-reference USR in its See Also section, even though both deal with user-defined functionality.

---

### inconsistent_formatting

**Description:** VAL function example has malformed code with incomplete IF statement and misplaced comment

**Affected files:**
- `help/common/language/functions/val.md`

**Details:**
In val.md, the example code shows: '10 READ NAME$,CITY$,STATE$,ZIP$
 20 IF VAL(ZIP$) <90000 OR VAL(ZIP$) >96699 THEN
 PRINT NAME$ TAB(25) "OUT OF STATE"
 30 IF VAL(ZIP$) >=90801 AND VAL(ZIP$) <=90815 THEN
 PRINT NAME$ TAB(25) "LONG BEACH"
 See the STR$ function for numeric to string
 conversion.' The code is incomplete (missing line continuation or THEN clause) and has a comment mixed into the code block.

---

### version_information_inconsistency

**Description:** Inconsistent version notation format

**Affected files:**
- `help/common/language/statements/clear.md`
- `help/common/language/statements/end.md`

**Details:**
In clear.md: '**Versions:** SK, -Extended, Disk' uses 'SK' and '-Extended', while end.md uses '**Versions:** SK, Extended, Disk' without the hyphen. The notation should be consistent across all files.

---

### incomplete_documentation

**Description:** Missing Remarks section content

**Affected files:**
- `help/common/language/statements/chain.md`
- `help/common/language/statements/edit.md`

**Details:**
Both chain.md and edit.md have empty Remarks sections ('## Remarks' with no content following), while other similar documentation files have detailed remarks explaining usage and behavior.

---

### missing_cross_reference

**Description:** FILES statement documentation is incomplete - missing Remarks and detailed Purpose sections that other file I/O statements have

**Affected files:**
- `help/common/language/statements/files.md`

**Details:**
FILES.md has a complete modern-style documentation with Remarks, Examples, and Notes sections, but the original MBASIC documentation structure shows only 'To display the directory of files on the current or specified disk drive' as Purpose. Other file I/O statements like FIELD.md, GET.md have more detailed Remarks sections from original documentation.

---

### incomplete_documentation

**Description:** Multiple statements have empty or missing Remarks sections

**Affected files:**
- `help/common/language/statements/error.md`
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/if-then-else-if-goto.md`

**Details:**
ERROR.md has 'Remarks' header with no content. FOR-NEXT.md has 'Remarks' header with no content. IF-THEN-ELSE-IF-GOTO.md has 'Remarks' header with no content. These appear to be incomplete documentation transfers.

---

### missing_implementation_notes

**Description:** LPRINT has implementation note about not being implemented, but LLIST also has same note - inconsistent with other printer-related statements

**Affected files:**
- `help/common/language/statements/lprint-lprint-using.md`
- `help/common/language/statements/llist.md`

**Details:**
Both LLIST.md and LPRINT-LPRINT-USING.md have '⚠️ **Not Implemented**' notes explaining line printer features aren't available. However, the implementation notes are formatted identically, suggesting they were added consistently. This is actually consistent, not an inconsistency.

---

### see_also_self_reference

**Description:** MID$ assignment statement references itself in See Also section

**Affected files:**
- `help/common/language/statements/mid-assignment.md`

**Details:**
mid-assignment.md includes '[MID$](mid_dollar.md) - To replace a portion of one string with another string' in its See Also section, which appears to reference the same functionality it documents, creating circular documentation.

---

### inconsistent_syntax_formatting

**Description:** Inconsistent syntax formatting across documentation files

**Affected files:**
- `help/common/language/statements/lset.md`
- `help/common/language/statements/mid_dollar.md`
- `help/common/language/statements/null.md`
- `help/common/language/statements/out.md`

**Details:**
Most files use clean syntax like 'LSET <string variable> = <string expression>' but mid_dollar.md uses unusual formatting with special characters: 'MID$«string expl>,n[,m])=<string exp2>' with guillemets and inconsistent spacing. This suggests encoding issues or different documentation sources.

---

### incomplete_documentation

**Description:** Several files have incomplete or malformed content in key sections

**Affected files:**
- `help/common/language/statements/mid_dollar.md`
- `help/common/language/statements/option-base.md`
- `help/common/language/statements/print.md`

**Details:**
mid_dollar.md has malformed syntax section. option-base.md is missing Purpose section content entirely (only has 'To declare the minimum value for array subscripts' in description but Purpose section is empty). print.md has Remarks section that says 'Remarks <list of expressions> is comprised of the string and expressions or numeric expressions that are to' which appears to be cut off or merged with example content.

---

### truncated_content

**Description:** PUT statement description appears truncated in See Also sections

**Affected files:**
- `help/common/language/statements/put.md`
- `help/common/language/statements/lset.md`

**Details:**
Multiple files reference PUT with description 'To write a record from a random buffer to a random' which appears incomplete - missing the word 'file' or similar at the end.

---

### inconsistent_terminology

**Description:** Inconsistent file mode terminology

**Affected files:**
- `help/common/language/statements/rset.md`
- `help/common/language/statements/writei.md`

**Details:**
RSET.md uses 'mode "O"' and 'mode "A"' while WRITEI.md uses 'mode "O"' and 'mode "A"' consistently, but other files may use different terminology. Need to verify consistency across all file I/O documentation.

---

### missing_reference

**Description:** Reference to non-existent appendix

**Affected files:**
- `help/common/language/statements/resume.md`

**Details:**
RESUME.md states 'See [Error Codes](../appendices/error-codes.md) for complete list.' but no appendices directory or error-codes.md file is provided in the documentation set.

---

### version_information_inconsistency

**Description:** Inconsistent version notation format

**Affected files:**
- `help/common/language/statements/restore.md`
- `help/common/language/statements/run.md`
- `help/common/language/statements/swap.md`

**Details:**
RESTORE.md uses '**Versions:** SK, Extended, Disk' while RUN.md uses '**Versions:** SK, Extended, Disk' (same format), but SWAP.md uses '**Versions:** EXtended, Disk' with inconsistent capitalization of 'Extended'.

---

### missing_reference

**Description:** Reference to test files not provided

**Affected files:**
- `help/common/language/statements/resume.md`

**Details:**
RESUME.md mentions 'Test file: `tests/test_resume.bas`, `tests/test_resume2.bas`, `tests/test_resume3.bas`' but these test files are not included in the documentation set.

---

### contradictory_information

**Description:** CLI settings commands inconsistency

**Affected files:**
- `help/common/settings.md`
- `help/common/ui/cli/index.md`

**Details:**
settings.md shows CLI commands as 'SHOWSETTINGS' and 'SETSETTING' (one word each), but references 'CLI Settings Commands' documentation. The CLI index.md doesn't mention these commands at all in its command list, suggesting incomplete documentation or naming inconsistency.

---

### path_inconsistency

**Description:** Inconsistent path depth in cross-references

**Affected files:**
- `help/common/ui/curses/editing.md`

**Details:**
The file references both '../../../ui/curses/running.md' (3 levels up) and '../../language/statements/auto.md' (2 levels up) from the same location (help/common/ui/curses/editing.md). Given the file structure, references to language should be '../../language/' and references to ui should be '../../../ui/' but this seems inconsistent with the actual file locations shown.

---

### feature_availability_conflict

**Description:** Curses UI features conflict with CLI-only debugging claims

**Affected files:**
- `help/common/ui/curses/editing.md`
- `help/mbasic/extensions.md`

**Details:**
editing.md describes Curses UI with 'Variables window - Watch variable values (Ctrl+W)' and 'Stack window - View execution stack (Ctrl+K)', but extensions.md claims WATCH and STACK commands are 'exclusive to the CLI backend'.

---

### feature_description_conflict

**Description:** PEEK function behavior inconsistency

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/features.md`

**Details:**
compatibility.md states 'PEEK: Returns random integer 0-255' and 'PEEK does NOT return values written by POKE'. However, features.md lists 'PEEK, POKE - Memory access (emulated)' without clarifying the random return behavior or the lack of PEEK/POKE interaction.

---

### feature_availability_conflict

**Description:** Find/Replace feature availability inconsistency

**Affected files:**
- `help/common/ui/tk/index.md`
- `help/mbasic/extensions.md`

**Details:**
tk/index.md lists 'Find' (Ctrl+F) in the Edit Menu and mentions 'Find and replace' as an editor feature. However, extensions.md states 'Find/Replace (Tk only currently)' suggesting it's exclusive to Tk, but doesn't clarify if it's find-only or find-and-replace.

---

### feature_availability_conflict

**Description:** Conflicting information about Delete Lines command

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/editing.md`

**Details:**
help/ui/curses/feature-reference.md lists 'Delete Lines (Ctrl+D)' as a file operation feature, but help/ui/curses/editing.md describes deleting lines by clearing text and pressing Enter or typing just the line number - no mention of Ctrl+D shortcut.

---

### command_inconsistency

**Description:** Different command examples for starting MBASIC

**Affected files:**
- `help/mbasic/getting-started.md`
- `help/ui/cli/index.md`

**Details:**
help/mbasic/getting-started.md shows 'mbasic' as the command to run, while the installation section shows 'python3 mbasic' in some contexts. The exact command syntax should be clarified.

---

### feature_availability_conflict

**Description:** Conflicting keyboard shortcuts between documentation

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/mbasic/getting-started.md`

**Details:**
help/mbasic/getting-started.md lists 'Ctrl+L - Step Line' under Curses UI shortcuts, but help/ui/curses/feature-reference.md shows Ctrl+L as 'List Program' and states 'Step Line (Ctrl+L when paused)' - the conditional nature is not mentioned in getting-started.md.

---

### feature_availability_conflict

**Description:** Conflicting information about stopping running programs

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/running.md`

**Details:**
keyboard-commands.md lists 'Ctrl+Q' as 'Stop execution', but running.md states 'Currently no way to interrupt running programs (use Ctrl+C to exit entirely)'

---

### keyboard_shortcut_inconsistency

**Description:** Missing keyboard shortcuts in quick reference

**Affected files:**
- `help/ui/curses/keyboard-commands.md`
- `help/ui/curses/quick-reference.md`

**Details:**
keyboard-commands.md lists 'Ctrl+V' for 'Open variables window' and 'Ctrl+K' for 'Open execution stack window', but quick-reference.md shows these as 'Ctrl+W' and 'Ctrl+K' respectively, with Ctrl+V not mentioned.

---

### feature_description_conflict

**Description:** Variable editing capability inconsistency

**Affected files:**
- `help/ui/curses/variables.md`
- `help/ui/curses/quick-reference.md`

**Details:**
variables.md states 'e or Enter: Edit selected variable value (simple variables and array elements)' in the Variables Window section, but also has a section titled 'Variable Editing (Limited)' that says 'Cannot edit values directly in window' and 'No inline editing'.

---

### keyboard_shortcut_inconsistency

**Description:** Inconsistent keyboard shortcut notation

**Affected files:**
- `help/ui/tk/feature-reference.md`
- `help/ui/tk/features.md`

**Details:**
feature-reference.md uses plain text like 'Ctrl+N', 'Ctrl+O', while features.md uses template notation like '{{kbd:smart_insert}}', '{{kbd:toggle_breakpoint}}'. This inconsistency in documentation style could confuse readers.

---

### feature_availability_conflict

**Description:** Conflicting information about Ctrl+N functionality

**Affected files:**
- `help/ui/curses/files.md`
- `help/ui/curses/keyboard-commands.md`

**Details:**
files.md describes 'Press **Ctrl+N**' under 'Creating a New Program' section, but keyboard-commands.md lists 'Ctrl+N' as 'New program (clear all lines)' in the Program Commands table. However, keyboard-commands.md also shows 'Ctrl+E' for renumbering, which files.md doesn't mention in its file operations.

---

### feature_availability_conflict

**Description:** Find and Replace feature availability differs between UIs

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/web/features.md`

**Details:**
The Tk UI keyboard-shortcuts.md documents full Find and Replace functionality with Ctrl+F and Ctrl+H shortcuts, including detailed features like 'Case sensitive, Whole word' options and 'Replace All' functionality. The Web UI features.md also documents Find (Ctrl+F) and Replace (Ctrl+H) with similar features. However, the Web UI getting-started.md makes no mention of these features, suggesting they may not be implemented or documented consistently.

---

### keyboard_shortcut_conflict

**Description:** Different keyboard shortcuts for same debugging operations across UIs

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/web/debugging.md`

**Details:**
Tk UI uses Ctrl+T for Step, Ctrl+G for Continue, Ctrl+B for Toggle Breakpoint. Web UI uses F10 for Step Over, F11 for Step Into, F5 for Continue, F9 for Toggle Breakpoint. These are completely different shortcut schemes for the same operations.

---

### ui_element_inconsistency

**Description:** Conflicting information about Web UI layout and panels

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/features.md`

**Details:**
getting-started.md describes a 'simple, vertical layout' with numbered components 1-7 in a specific order. However, features.md under 'Layout Options' mentions 'Resizable panels', 'Hide/show panels', and 'Horizontal/vertical split', suggesting a more flexible layout than the fixed vertical layout described in getting-started.md.

---

### feature_availability_conflict

**Description:** Breakpoint functionality not mentioned in getting-started but detailed in features

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/features.md`

**Details:**
getting-started.md makes no mention of breakpoints in its debugging section, only covering Step Execution, Show Variables, and Show Stack. However, features.md and debugging.md extensively document breakpoint functionality including 'Click any line number' to set breakpoints, conditional breakpoints, and breakpoint management. This is a significant omission from the getting-started guide.

---

### feature_availability_conflict

**Description:** Inconsistent information about Ctrl+, keyboard shortcut

**Affected files:**
- `help/ui/web/keyboard-shortcuts.md`
- `help/ui/web/settings.md`

**Details:**
settings.md lists 'Use keyboard shortcut: Ctrl+,' as a method to open settings with note '(if enabled)'. However, keyboard-shortcuts.md does not list Ctrl+, anywhere in its comprehensive keyboard shortcuts documentation, suggesting this shortcut may not actually be implemented or available.

---

### feature_documentation_gap

**Description:** Settings dialog not mentioned in main interface guide

**Affected files:**
- `help/ui/web/keyboard-shortcuts.md`
- `help/ui/web/web-interface.md`

**Details:**
settings.md provides extensive documentation of a settings dialog feature, but web-interface.md (the main interface guide) makes no mention of settings, configuration, or preferences in its 'Menu Functions' or 'Main Components' sections. This suggests incomplete documentation of available features.

---

### missing_reference

**Description:** CHOOSING_YOUR_UI.md describes four UIs (CLI, Curses, Tk, Web) but QUICK_REFERENCE.md only documents the Curses UI without mentioning the existence of other UIs

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`
- `user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states 'MBASIC gives you **two separate case handling systems**' and describes CLI, Curses, Tk, and Web UIs. QUICK_REFERENCE.md is titled 'MBASIC Curses IDE - Quick Reference Card' and only covers Curses UI commands without acknowledging other UI options.

---

### missing_reference

**Description:** CASE_HANDLING_GUIDE.md references settings and configuration features not mentioned in QUICK_REFERENCE.md

**Affected files:**
- `user/CASE_HANDLING_GUIDE.md`
- `user/QUICK_REFERENCE.md`

**Details:**
CASE_HANDLING_GUIDE.md extensively documents SET and SHOW SETTINGS commands for configuring case handling. QUICK_REFERENCE.md for Curses UI makes no mention of these commands or how to access settings in the Curses interface.

---

### contradictory_information

**Description:** Feature availability conflict for Find/Replace in Curses UI

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`
- `user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states under Curses limitations: 'No Find/Replace yet'. However, QUICK_REFERENCE.md does not mention Find/Replace at all in its command list, which could imply it doesn't exist or is simply not documented.

---

### contradictory_information

**Description:** Conflicting information about project dependencies

**Affected files:**
- `user/INSTALL.md`
- `user/INSTALLATION.md`

**Details:**
INSTALL.md states 'Since this project has no external dependencies, this step mainly verifies your Python environment'. INSTALLATION.md lists 'Optional: urwid (for Curses UI)' and 'Optional: nicegui (for Web UI)' as requirements, contradicting the 'no external dependencies' claim.

---

### feature_availability_conflict

**Description:** Find and Replace availability inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md states 'Press Ctrl+H (Find and Replace)' as an available feature. However, UI_FEATURE_COMPARISON.md shows 'Find/Replace' with 'Ctrl+H' shortcut but also lists under 'Recently Added (2025-10-29): ✅ Tk: Find/Replace functionality', suggesting it's newly added. The keyboard shortcuts table in UI_FEATURE_COMPARISON.md shows 'Ctrl+H/F1' for Help in Curses, creating potential confusion with Tk's Ctrl+H for Find/Replace.

---

### command_inconsistency

**Description:** Inconsistent command for renumbering programs

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/keyboard-shortcuts.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md uses 'Ctrl+E' for renumber throughout. keyboard-shortcuts.md (Curses UI) states 'Ctrl+E | Renumber all lines (RENUM)', using the command name 'RENUM'. However, SETTINGS_AND_CONFIGURATION.md never mentions the 'RENUM' command name, only referring to the renumber dialog.

---

### keyboard_shortcut_inconsistency

**Description:** Step execution keyboard shortcuts differ between UIs

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+T' for 'Step through code (next statement)' and 'Ctrl+L' for 'Step through code (next line)'. keyboard-shortcuts.md (Curses UI) lists 'Ctrl+K' for 'Step Line' and 'Ctrl+T' for 'Step Statement'. The Ctrl+K shortcut has different meanings: in Tk it's 'Show/hide Execution Stack window', in Curses it's 'Step Line'.

---

### save_command_inconsistency

**Description:** Save keyboard shortcut inconsistency in Curses UI

**Affected files:**
- `user/keyboard-shortcuts.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
keyboard-shortcuts.md (Curses UI) lists 'Ctrl+V' for 'Save program' and 'Shift+Ctrl+V' for 'Save As'. However, UI_FEATURE_COMPARISON.md shows 'Ctrl+S' for Save across all UIs including Curses. This is a significant inconsistency as Ctrl+V is also mentioned for Variables window in other contexts.

---

## 🟢 Low Severity

### inconsistent_terminology

**Description:** Inconsistent naming of UI backends - 'Curses/Urwid' vs 'Curses'

**Affected files:**
- `help/common/debugging.md`
- `help/common/editor-commands.md`

**Details:**
debugging.md uses 'Curses UI' consistently, but README.md refers to 'Curses/Urwid Backend' in the structure section, mixing the implementation detail (urwid) with the UI name.

---

### missing_reference

**Description:** index.md references non-existent shortcuts.md and language.md files

**Affected files:**
- `help/common/index.md`
- `help/common/getting-started.md`

**Details:**
index.md links to:
- [Keyboard Shortcuts](shortcuts.md)
- [BASIC Language Reference](language.md)

But these files don't exist in the provided documentation. getting-started.md correctly links to language/index.md and other existing files.

---

### missing_reference

**Description:** debugging.md references shortcuts.md which doesn't exist

**Affected files:**
- `help/common/debugging.md`

**Details:**
debugging.md 'See Also' section includes:
- [Keyboard Shortcuts](shortcuts.md) - Complete shortcut reference

This file is not present in the documentation set.

---

### inconsistent_information

**Description:** Conflicting keyboard shortcuts for help

**Affected files:**
- `help/common/debugging.md`
- `help/common/editor-commands.md`

**Details:**
debugging.md doesn't mention help shortcuts, but editor-commands.md states:
- **F1** or **H** - Open help
- **Ctrl+P** in index.md - Show help

No clarification on which UI uses which shortcut or if they're alternatives.

---

### missing_reference

**Description:** debugging.md references editor-commands.md which exists but may not contain expected content

**Affected files:**
- `help/common/debugging.md`

**Details:**
debugging.md 'See Also' links to [Editor Commands](editor-commands.md), but editor-commands.md focuses on program and editing commands, not debugging-specific editor features.

---

### missing_reference

**Description:** appendices/index.md references math-functions.md which is not provided

**Affected files:**
- `help/common/language/appendices/index.md`

**Details:**
index.md lists under 'Available Appendices':
### [Mathematical Functions](math-functions.md)

This file is not included in the provided documentation set.

---

### inconsistent_reference

**Description:** ascii-codes.md references character-set.md which is not provided

**Affected files:**
- `help/common/language/appendices/ascii-codes.md`

**Details:**
ascii-codes.md 'See Also' section includes:
- [Character Set](../character-set.md) - BASIC-80 character set overview

This file is not present in the documentation set.

---

### missing_reference

**Description:** error-codes.md references statements that may not exist in documentation

**Affected files:**
- `help/common/language/appendices/error-codes.md`

**Details:**
error-codes.md references multiple statement pages in 'See Also' and throughout:
- [ON ERROR GOTO](../statements/on-error-goto.md)
- [ERR and ERL](../statements/err-erl-variables.md)
- [ERROR](../statements/error.md)
- [RESUME](../statements/resume.md)

These specific statement files are not provided to verify they exist.

---

### inconsistent_cross_reference

**Description:** CINT See Also section missing CSNG reference

**Affected files:**
- `help/common/language/functions/cint.md`
- `help/common/language/functions/cdbl.md`

**Details:**
In cint.md, the 'See Also' section only lists CDBL and CSNG, but cdbl.md lists CINT, CSNG, FIX, and INT. The cross-references are not symmetric.

---

### inconsistent_cross_reference

**Description:** Mathematical functions list inconsistency

**Affected files:**
- `help/common/language/appendices/math-functions.md`
- `help/common/language/functions/index.md`

**Details:**
math-functions.md lists CSNG in the 'Related Functions' section but index.md does not list CSNG in the 'Mathematical Functions' category - it's only in 'Type Conversion Functions'.

---

### version_information_inconsistency

**Description:** Malformed version information in HEX$ function

**Affected files:**
- `help/common/language/functions/hex_dollar.md`

**Details:**
In hex_dollar.md, the syntax line includes 'Versionsr Extended, Disk' which appears to be a typo (should be 'Versions:' on a separate line).

---

### inconsistent_terminology

**Description:** Inconsistent naming of BASIC variant

**Affected files:**
- `help/common/language/character-set.md`
- `help/common/language/data-types.md`

**Details:**
character-set.md refers to 'BASIC-80' while data-types.md also uses 'BASIC-80', but some function files use 'MBASIC 5.21'. The documentation should consistently use one name or clarify the relationship.

---

### duplicate_see_also_reference

**Description:** Both LEFT$ and RIGHT$ reference two different MID$ entries in their See Also sections - one as a function and one as a statement

**Affected files:**
- `help/common/language/functions/left_dollar.md`
- `help/common/language/functions/right_dollar.md`

**Details:**
left_dollar.md contains both '- [MID$](mid_dollar.md) - Extract a substring from the middle of a string' and '- [MID$](../statements/mid_dollar.md) - To replace a portion of one string with another string'. right_dollar.md contains the same duplicate references. This is inconsistent with other files like instr.md, len.md, mid_dollar.md, oct_dollar.md, space_dollar.md, spc.md, str_dollar.md, and string_dollar.md which only reference the MID$ Assignment statement version.

---

### missing_syntax_section

**Description:** STRING$ function is missing a Syntax section header while all other function files include it

**Affected files:**
- `help/common/language/functions/string_dollar.md`

**Details:**
string_dollar.md jumps directly from the title to '**Versions:** Extended, Disk-' without a '## Syntax' header and code block, unlike all other function documentation files which follow the pattern of having ## Syntax, ## Description, ## Example sections.

---

### inconsistent_version_formatting

**Description:** Version information formatting is inconsistent across files

**Affected files:**
- `help/common/language/functions/int.md`
- `help/common/language/functions/len.md`
- `help/common/language/functions/instr.md`

**Details:**
int.md shows 'Versions,: 8K, Extended, Disk' (with comma after 'Versions'), len.md shows '**Versions:** 8R, Extended, Disk' (with 8R instead of 8K), and instr.md shows '**Versions:** Extended, Disk'. The comma placement and version naming (8K vs 8R) are inconsistent.

---

### inconsistent_related_field

**Description:** Some files use 'related' field in frontmatter while most use only 'See Also' section

**Affected files:**
- `help/common/language/functions/int.md`
- `help/common/language/functions/left_dollar.md`
- `help/common/language/functions/lof.md`
- `help/common/language/functions/mid_dollar.md`
- `help/common/language/functions/oct_dollar.md`
- `help/common/language/functions/right_dollar.md`
- `help/common/language/functions/space_dollar.md`

**Details:**
Files like int.md ('related: ['fix', 'cint', 'csng', 'cdbl']'), left_dollar.md, lof.md, mid_dollar.md, oct_dollar.md, right_dollar.md, and space_dollar.md include a 'related' field in their YAML frontmatter, while other files like instr.md, len.md, log.md, etc. do not have this field and rely only on the See Also section.

---

### inconsistent_terminology

**Description:** Inconsistent spacing and formatting in DEFINT/SNG/DBL/STR examples

**Affected files:**
- `help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
The example section shows inconsistent indentation and formatting: '10 DEFDBL L-P    All variables beginning with...' with multiple spaces used for alignment in comments, which differs from the standard formatting used in other documentation files.

---

### inconsistent_cross_references

**Description:** Circular and inconsistent See Also references

**Affected files:**
- `help/common/language/statements/cload.md`
- `help/common/language/statements/csave.md`
- `help/common/language/statements/defint-sng-dbl-str.md`

**Details:**
cload.md, csave.md, and defint-sng-dbl-str.md all have identical See Also sections that reference each other and various unrelated functions (COBL, CRR$, CVI/CVS/CVD, etc.). This appears to be copy-paste error as these references don't make logical sense for all three statements.

---

### inconsistent_syntax_formatting

**Description:** Inconsistent syntax block formatting - some use periods before syntax, others don't

**Affected files:**
- `help/common/language/statements/erase.md`
- `help/common/language/statements/field.md`
- `help/common/language/statements/get.md`

**Details:**
ERASE.md shows 'syntax: .       ERASE <list of array variables>' with leading period and spaces, while FIELD.md shows 'syntax: FIELD[i]<file number>,<field width> AS <string variable> •••' without leading period. GET.md shows 'syntax: GET [#]<file number>[,<record number>]' also without leading period.

---

### inconsistent_version_notation

**Description:** Version information formatted inconsistently across statements

**Affected files:**
- `help/common/language/statements/error.md`
- `help/common/language/statements/field.md`
- `help/common/language/statements/for-next.md`

**Details:**
ERROR.md shows '**Versions:** Extend~d,   Disk' with tilde and irregular spacing. FIELD.md shows '**Versions:** Disk'. FOR-NEXT.md shows '**Versions:** SK, Extended, Disk NOTE:' with note inline. Some have clean formatting, others have OCR artifacts like tildes and irregular spacing.

---

### inconsistent_see_also_grouping

**Description:** Some statements have identical See Also sections that appear to be template-based rather than contextually relevant

**Affected files:**
- `help/common/language/statements/err-erl-variables.md`
- `help/common/language/statements/input_hash.md`
- `help/common/language/statements/line-input.md`
- `help/common/language/statements/lprint-lprint-using.md`

**Details:**
ERR-ERL-VARIABLES.md, INPUT_HASH.md, LINE-INPUT.md, and LPRINT-LPRINT-USING.md all share the exact same See Also list including CLOAD, COBL, CRR$, CSAVE, CVI/CVS/CVD, etc. This appears to be a copy-paste error as these references don't all make sense for each statement (e.g., why would ERR/ERL variables reference CLOAD?).

---

### ocr_artifacts

**Description:** OCR artifacts present in documentation text

**Affected files:**
- `help/common/language/statements/field.md`
- `help/common/language/statements/get.md`
- `help/common/language/statements/inputi.md`

**Details:**
FIELD.md contains 'und~r' instead of 'under', 'positions. (bytes) in the·' with middle dot. GET.md contains 'into    a' with excessive spacing. INPUTI.md contains 'cont~ining' instead of 'containing'. These suggest the documentation was OCR'd and not fully cleaned.

---

### inconsistent_title_formatting

**Description:** Title uses tilde character instead of proper formatting

**Affected files:**
- `help/common/language/statements/inputi.md`

**Details:**
INPUTI.md has 'title: ~ INPUTi' with leading tilde, and the heading shows '# ~   INPUTi' with tilde and extra spaces. Should be 'LINE INPUT#' based on the syntax shown.

---

### inconsistent_example_formatting

**Description:** Example sections have inconsistent indentation and formatting

**Affected files:**
- `help/common/language/statements/erase.md`
- `help/common/language/statements/field.md`
- `help/common/language/statements/get.md`

**Details:**
ERASE.md shows '450 ERASE A,B' then '                460 DIM B(99)' with excessive leading spaces. FIELD.md shows 'See Appendix B.' with additional NOTE section. GET.md shows 'See Appendix B.' with NOTE section. Some examples show actual code, others just reference appendices.

---

### inconsistent_version_labeling

**Description:** Inconsistent version labeling format across files

**Affected files:**
- `help/common/language/statements/lset.md`
- `help/common/language/statements/merge.md`
- `help/common/language/statements/mid-assignment.md`
- `help/common/language/statements/name.md`

**Details:**
Some files use '**Versions:** Disk' (lset.md, merge.md, name.md) while mid-assignment.md uses '**Versions:** Extended, Disk'. The format is consistent but the level of detail varies - some specify multiple versions while others only mention 'Disk'.

---

### see_also_inconsistency

**Description:** File I/O related statements have nearly identical See Also sections but with minor variations

**Affected files:**
- `help/common/language/statements/lset.md`
- `help/common/language/statements/open.md`
- `help/common/language/statements/printi-printi-using.md`
- `help/common/language/statements/put.md`
- `help/common/language/statements/reset.md`

**Details:**
Files lset.md, open.md, printi-printi-using.md, put.md, and reset.md all share almost identical See Also sections listing the same file I/O functions. However, there are minor inconsistencies in descriptions (e.g., 'PUT' description varies slightly: 'To write a record from a random buffer to a random' appears truncated in multiple files).

---

### inconsistent_formatting

**Description:** Inconsistent syntax formatting in older documentation

**Affected files:**
- `help/common/language/statements/save.md`
- `help/common/language/statements/swap.md`
- `help/common/language/statements/write.md`

**Details:**
SAVE.md uses 'SAVE <filename> [,A   I ,P]' with unusual spacing. SWAP.md uses '<variab1e>' (with number 1 instead of letter l). WRITE.md uses 'WRITE[<list of expressions»' with closing guillemet instead of closing bracket. These appear to be OCR or conversion errors from original documentation.

---

### inconsistent_see_also_links

**Description:** Inconsistent See Also sections for system/settings commands

**Affected files:**
- `help/common/language/statements/setsetting.md`
- `help/common/language/statements/showsettings.md`
- `help/common/language/statements/tron-troff.md`
- `help/common/language/statements/width.md`

**Details:**
SETSETTING.md, SHOWSETTINGS.md, TRON-TROFF.md, and WIDTH.md all have identical See Also sections listing the same 10 commands (FRE, HELP SET, INKEY$, INP, LIMITS, NULL, PEEK, RANDOMIZE, REM, and cross-references). This seems like a template that may not be appropriate for all these commands. For example, why does WIDTH link to RANDOMIZE?

---

### inconsistent_metadata

**Description:** Duplicate metadata field

**Affected files:**
- `help/common/language/statements/while-wend.md`

**Details:**
WHILE-WEND.md has both 'aliases: [while-wend]' and 'related: [for-next, if-then-else-if-goto, goto]' fields, and also includes 'syntax:' field. The 'aliases' field seems redundant since the title already includes the full statement name.

---

### terminology_inconsistency

**Description:** Inconsistent project naming

**Affected files:**
- `help/mbasic/extensions.md`
- `help/index.md`
- `help/mbasic/features.md`

**Details:**
extensions.md mentions 'MBASIC-2025' and lists alternative names under consideration (Visual MBASIC 5.21, MBASIC++, MBASIC-X). However, index.md consistently uses 'MBASIC 5.21' and features.md uses 'this MBASIC interpreter' without mentioning the 2025 designation or naming considerations.

---

### missing_reference

**Description:** Missing UI reference in index

**Affected files:**
- `help/index.md`

**Details:**
index.md lists four UIs: Tk, Curses, Web Browser, and CLI. However, it doesn't mention which is the default UI, while features.md states 'Curses UI (Default)'.

---

### contradictory_information

**Description:** WIDTH statement description ambiguity

**Affected files:**
- `help/mbasic/compatibility.md`

**Details:**
compatibility.md states 'WIDTH is parsed for compatibility but performs no operation' and 'The "WIDTH LPRINT" syntax is not supported.' This creates ambiguity about whether WIDTH is fully parsed or only partially parsed (excluding WIDTH LPRINT).

---

### missing_cross_reference

**Description:** Sequential Files Guide reference without corresponding file

**Affected files:**
- `help/mbasic/compatibility.md`

**Details:**
compatibility.md references 'See [Sequential Files Guide](../../user/sequential-files.md)' but this file is not included in the provided documentation set, and the path structure suggests it should be in a 'user' directory that isn't shown.

---

### missing_reference

**Description:** Placeholder document referenced but incomplete

**Affected files:**
- `help/ui/cli/index.md`
- `help/ui/common/running.md`

**Details:**
help/ui/cli/index.md references help/ui/common/running.md for running programs, but that file is marked as 'PLACEHOLDER - Documentation in progress' with minimal content.

---

### missing_reference

**Description:** Placeholder document referenced but incomplete

**Affected files:**
- `help/ui/cli/index.md`
- `help/ui/common/errors.md`

**Details:**
help/ui/cli/index.md references help/ui/common/errors.md for error messages, but that file is marked as 'PLACEHOLDER - Documentation in progress' with minimal content.

---

### inconsistent_terminology

**Description:** Inconsistent naming of CLI mode

**Affected files:**
- `help/mbasic/getting-started.md`
- `help/ui/cli/index.md`

**Details:**
help/mbasic/getting-started.md refers to 'CLI Mode' and 'CLI mode', while help/ui/cli/index.md uses 'command-line interface' and 'CLI'. The terminology should be consistent throughout.

---

### ui_comparison_inconsistency

**Description:** Feature comparison table doesn't match detailed feature list

**Affected files:**
- `help/ui/index.md`
- `help/ui/tk/feature-reference.md`

**Details:**
index.md comparison table shows 'Debugger: Limited' for Web UI, but tk/feature-reference.md comparison table shows 'Debugger: ✗' (not available) for CLI, which seems inconsistent with the feature descriptions.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for step execution features

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/web/debugging.md`
- `help/ui/web/getting-started.md`

**Details:**
Tk UI uses 'Step Statement' (Ctrl+T) terminology in keyboard-shortcuts.md. Web UI uses both 'Step Stmt' (in getting-started.md toolbar description) and 'Step over (F10)' / 'Step into (F11)' (in debugging.md). The Web UI also introduces 'Step Line' vs 'Step Statement' distinction not mentioned in Tk documentation.

---

### feature_documentation_gap

**Description:** Settings dialog keyboard shortcut not documented

**Affected files:**
- `help/ui/tk/keyboard-shortcuts.md`
- `help/ui/tk/settings.md`

**Details:**
settings.md states 'Keyboard shortcut: (check your system's menu)' for opening Settings Dialog, but keyboard-shortcuts.md does not list any shortcut for opening settings. This is an incomplete documentation.

---

### version_number_inconsistency

**Description:** Vague version number in status bar description

**Affected files:**
- `help/ui/web/getting-started.md`

**Details:**
getting-started.md states the status bar shows 'Version number (v1.0.xxx)' with 'xxx' as a placeholder. This should either show a specific version or explain that it's a placeholder more clearly.

---

### command_availability_conflict

**Description:** Settings persistence location differs between UIs

**Affected files:**
- `help/ui/tk/settings.md`
- `help/ui/web/features.md`

**Details:**
Tk settings.md specifies exact file locations for settings: '~/.mbasic/settings.json' (Linux/Mac) and '%APPDATA%\mbasic\settings.json' (Windows). Web features.md mentions 'Local storage only' and 'localStorage' under Security Features, suggesting settings are stored in browser localStorage rather than filesystem, but this is not explicitly documented in Web UI settings documentation.

---

### inconsistent_statistics

**Description:** Conflicting game library counts

**Affected files:**
- `help/ui/web/index.md`
- `library/index.md`

**Details:**
help/ui/web/index.md states '113 classic CP/M era games ready to run!' while library/index.md states 'Total Programs: 114+' across all categories. The games/index.md file shows 113 games, but the total library count should be significantly higher than 113 if it includes all categories (utilities, education, business, etc.).

---

### missing_reference

**Description:** Broken 'See Also' reference

**Affected files:**
- `help/ui/web/keyboard-shortcuts.md`

**Details:**
keyboard-shortcuts.md references '[Debugging Features](../../common/debugging.md)' and '[Editor Commands](../../common/editor-commands.md)' in the 'See Also' section, but these files are not included in the provided documentation set, making it unclear if these paths are correct or if the files exist.

---

### inconsistent_terminology

**Description:** Inconsistent naming of settings interface element

**Affected files:**
- `help/ui/web/keyboard-shortcuts.md`
- `help/ui/web/settings.md`

**Details:**
settings.md refers to '⚙️ Settings icon' while keyboard-shortcuts.md does not mention any settings icon or button in its comprehensive button/menu documentation. The settings access method is not consistently documented across files.

---

### contradictory_information

**Description:** Two different installation guides exist with overlapping but different content

**Affected files:**
- `user/INSTALL.md`
- `user/INSTALLATION.md`

**Details:**
INSTALL.md provides detailed installation instructions with three methods. INSTALLATION.md is marked as 'PLACEHOLDER - Documentation in progress' but provides quick install commands that differ from INSTALL.md's approach. INSTALLATION.md suggests 'pip install mbasic-interpreter' which is not mentioned in INSTALL.md.

---

### inconsistent_terminology

**Description:** Inconsistent naming of the Curses UI

**Affected files:**
- `user/CASE_HANDLING_GUIDE.md`
- `user/CHOOSING_YOUR_UI.md`

**Details:**
CASE_HANDLING_GUIDE.md refers to it as 'CURSES (full terminal IDE)' in uppercase. CHOOSING_YOUR_UI.md uses 'Curses (Terminal UI)' with capital C. QUICK_REFERENCE.md uses 'Curses IDE'. The terminology should be consistent across documents.

---

### missing_reference

**Description:** README.md does not list CASE_HANDLING_GUIDE.md in its contents

**Affected files:**
- `user/README.md`
- `user/CASE_HANDLING_GUIDE.md`

**Details:**
README.md in user/ directory lists only three documents (QUICK_REFERENCE.md, URWID_UI.md, FILE_FORMAT_COMPATIBILITY.md) but CASE_HANDLING_GUIDE.md and CHOOSING_YOUR_UI.md exist in the same directory and are not mentioned.

---

### missing_reference

**Description:** README.md does not list CHOOSING_YOUR_UI.md in its contents

**Affected files:**
- `user/README.md`
- `user/CHOOSING_YOUR_UI.md`

**Details:**
README.md lists only QUICK_REFERENCE.md, URWID_UI.md, and FILE_FORMAT_COMPATIBILITY.md but CHOOSING_YOUR_UI.md exists and is not listed.

---

### missing_reference

**Description:** README.md does not list either INSTALL.md or INSTALLATION.md in its contents

**Affected files:**
- `user/README.md`
- `user/INSTALL.md`
- `user/INSTALLATION.md`

**Details:**
README.md mentions 'Installation guides' in its purpose section but does not list the actual installation guide files (INSTALL.md and INSTALLATION.md) in its Contents section.

---

### inconsistent_terminology

**Description:** Inconsistent command naming for starting the Curses UI

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`
- `user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md uses 'python3 mbasic --ui curses' while QUICK_REFERENCE.md uses the same format. However, CHOOSING_YOUR_UI.md also shows 'python3 mbasic' without --ui flag for CLI, creating potential confusion about default behavior.

---

### feature_description_conflict

**Description:** Smart Insert feature availability unclear

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md extensively documents Smart Insert (Ctrl+I) as a Tk feature. UI_FEATURE_COMPARISON.md lists 'Smart Insert' as 'Tk exclusive feature' with checkmark only for Tk. However, the feature matrix shows it as '❌' for all other UIs without explicitly stating it's Tk-only in the matrix itself, which could be clearer.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for Variables window

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md refers to 'Variables & Resources window (Ctrl+W in TK UI)'. TK_UI_QUICK_START.md uses both 'Variables window' and 'Variables & Resources window' seemingly interchangeably, with different shortcuts (Ctrl+V and Ctrl+W). It's unclear if these are the same window or different windows.

---

### feature_availability_conflict

**Description:** Find/Replace status inconsistency within same document

**Affected files:**
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md shows 'Find/Replace' as available (✅) for Tk in the feature matrix, lists it under 'Recently Added (2025-10-29)', but also lists 'Find/Replace in Web UI' under 'Coming Soon (⏳)', creating confusion about current vs. planned features.

---

