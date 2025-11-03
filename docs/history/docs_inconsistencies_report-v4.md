# Documentation Inconsistencies Report

Generated: 2025-11-03 17:49:12
Scanned directories: help, library, stylesheets, user

Found 133 inconsistencies:

## 🔴 High Severity

### contradictory_information

**Description:** Inconsistent product name/version references

**Affected files:**
- `help/common/language/appendices/math-functions.md`
- `help/common/language/functions/index.md`

**Details:**
math-functions.md states 'MBASIC 5.21 provides the following built-in mathematical functions' while index.md consistently refers to 'BASIC-80'. The product should be consistently named throughout documentation.

---

### contradictory_information

**Description:** OPEN syntax documentation contains garbled/corrupted text in the Remarks section

**Affected files:**
- `help/common/language/statements/open.md`

**Details:**
The Remarks section contains malformed text: 'o        specifies sequential output mode I       specifies sequential input mode R        specifies random input/output mode' with irregular spacing and formatting. Also contains 'your operating system~s rules' with tilde instead of apostrophe, and 'See also page A-3' which is a reference to a physical manual page that doesn't exist in this documentation system.

---

### contradictory_information

**Description:** PRINT documentation contains severely corrupted and incomplete content

**Affected files:**
- `help/common/language/statements/print.md`

**Details:**
The Remarks section is completely garbled with malformed formatting characters, incomplete sentences like 'be printed, separated by semicolons.     <string', and extensive corrupted text about PRINT USING formatting that is unreadable. The Example section contains the entire documentation text instead of actual examples. This makes the documentation unusable.

---

### missing_reference

**Description:** settings.md references non-existent statement documentation files

**Affected files:**
- `help/common/settings.md`

**Details:**
settings.md 'See Also' section links to '[SHOWSETTINGS Statement](language/statements/showsettings.md)' and '[SETSETTING Statement](language/statements/setsetting.md)' but these files are not included in the provided documentation set

---

### feature_availability_conflict

**Description:** Inconsistent information about Find/Replace feature availability

**Affected files:**
- `help/mbasic/extensions.md`
- `help/mbasic/features.md`

**Details:**
extensions.md states 'Find (Tk has Find, Replace planned for future)' but features.md does not mention Find at all in the Tkinter GUI section. The features.md file lists 'Menu bar', 'Toolbar', 'Status bar' but omits Find functionality that extensions.md claims exists.

---

### feature_availability_conflict

**Description:** Conflicting information about syntax highlighting availability

**Affected files:**
- `help/mbasic/extensions.md`
- `help/mbasic/features.md`

**Details:**
extensions.md states syntax highlighting is available in 'Tk, Web' UIs. features.md for Tkinter GUI says 'Syntax highlighting (if available)' suggesting it's optional/uncertain. This creates ambiguity about whether the feature actually exists in Tk.

---

### feature_availability_conflict

**Description:** Conflicting information about Cut/Copy/Paste shortcuts in Curses UI

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/editing.md`

**Details:**
feature-reference.md states 'Cut: Ctrl+X, Copy: Ctrl+C, Paste: Ctrl+V' but editing.md does not mention these shortcuts at all, and feature-reference.md also states 'Stop/Interrupt (Ctrl+X)' creating a conflict where Ctrl+X is assigned to both Cut and Stop.

---

### keyboard_shortcut_inconsistency

**Description:** Conflicting keyboard shortcuts for loading files

**Affected files:**
- `help/ui/curses/files.md`
- `help/ui/curses/quick-reference.md`

**Details:**
In files.md under 'Loading Programs', the example shows 'Press b' to load a file, but quick-reference.md lists 'Ctrl+O' as the shortcut for 'Open/Load program'. The files.md document also states 'Press Ctrl+O' in step 1, making the example inconsistent with its own instructions.

---

### keyboard_shortcut_inconsistency

**Description:** Conflicting keyboard shortcuts for saving files

**Affected files:**
- `help/ui/curses/files.md`
- `help/ui/curses/quick-reference.md`

**Details:**
files.md states 'Press Ctrl+V' for saving (with note about Ctrl+S being unavailable), but quick-reference.md lists 'Ctrl+V' as 'Save program'. However, the note about Ctrl+S being unavailable due to terminal flow control is only in files.md, not in quick-reference.md, which could confuse users.

---

### feature_availability_conflict

**Description:** Variable editing capability inconsistency

**Affected files:**
- `help/ui/curses/variables.md`
- `help/ui/curses/quick-reference.md`

**Details:**
variables.md states 'e or Enter - Edit selected variable value (simple variables and array elements)' in the Variables Window section, but later has a section titled 'Variable Editing (Limited)' with '⚠️ Partial Implementation' stating 'Cannot edit values directly in window'. This is contradictory.

---

### feature_availability_conflict

**Description:** Contradictory information about breakpoint implementation status in Web UI

**Affected files:**
- `help/ui/web/features.md`
- `help/ui/web/debugging.md`

**Details:**
help/ui/web/features.md states under 'Breakpoints' section: 'Currently Implemented: Line breakpoints (toggle via Run menu), Clear all breakpoints, Visual indicators in editor' and 'Management: Toggle via Run menu → Toggle Breakpoint'. However, help/ui/web/debugging.md describes extensive breakpoint features including 'Click any line number in the editor', 'Red dot appears', 'Right-click line number for menu', 'Breakpoint Panel', 'Conditional Breakpoints', 'Logpoints', and 'Data Breakpoints' - features that appear to be planned/aspirational rather than currently implemented.

---

### feature_availability_conflict

**Description:** Inconsistent breakpoint setting instructions between documents

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/debugging.md`

**Details:**
help/ui/web/getting-started.md states: 'Set breakpoints to pause execution at specific lines: 1. Use Run → Toggle Breakpoint menu option 2. Enter the line number'. However, help/ui/web/debugging.md describes: '1. Click any line number in the editor 2. A red dot appears indicating breakpoint 3. Click again to remove' - these are completely different interaction methods.

---

### Feature availability conflict

**Description:** Web interface documentation states files cannot be loaded from local filesystem, but library documentation instructs users to download and open .bas files

**Affected files:**
- `help/ui/web/web-interface.md`
- `library/index.md`

**Details:**
web-interface.md states under 'Limitations': 'Cannot access local filesystem' and under 'File I/O': 'Files are stored in browser memory only' and 'No access to the server's real filesystem (security)'. However, library/index.md instructs: 'Download the .bas file you want to use' then 'GUI (Web/Tk): File → Open, select the downloaded file'. This suggests the Web UI can open downloaded files, contradicting the limitation that it cannot access local filesystem.

---

### keyboard_shortcut_inconsistency

**Description:** Conflicting keyboard shortcuts for Variables window between Tk UI and Curses UI documentation

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md states 'Ctrl+V' shows Variables window and 'Ctrl+W' shows Variables & Resources window for Tk UI. However, keyboard-shortcuts.md (Curses UI) states 'Ctrl+W' toggles variables watch window. The TK quick start also lists 'Ctrl+K' for Execution Stack, but keyboard-shortcuts.md says 'Menu only' for execution stack window.

---

## 🟡 Medium Severity

### missing_reference

**Description:** Appendices index references a 'Mathematical Functions' document that is not provided in the file set

**Affected files:**
- `help/common/appendices/index.md`
- `help/common/language/appendices/math-functions.md`

**Details:**
help/common/appendices/index.md mentions '### [Mathematical Functions](math-functions.md)' with description 'Derived mathematical functions using BASIC-80's intrinsic functions' but the file help/common/language/appendices/math-functions.md is not included in the documentation set provided.

---

### missing_reference

**Description:** Getting started guide references statement documentation files that are not provided

**Affected files:**
- `help/common/getting-started.md`
- `help/common/language/statements/index.md`

**Details:**
help/common/getting-started.md references multiple statement files: '[PRINT statement](language/statements/print.md)', '[INPUT statement](language/statements/input.md)', '[FOR-NEXT loops](language/statements/for-next.md)', '[IF-THEN-ELSE](language/statements/if-then-else-if-goto.md)', and '[BASIC Language Reference](language/statements/index.md)' - none of these files are included in the documentation set.

---

### missing_reference

**Description:** Example files reference statement and function documentation that is not provided

**Affected files:**
- `help/common/examples/hello-world.md`
- `help/common/examples/loops.md`

**Details:**
help/common/examples/hello-world.md references '[PRINT Statement](../language/statements/print.md)', '[END Statement](../language/statements/end.md)'. help/common/examples/loops.md references '[FOR-NEXT Statement](../language/statements/for-next.md)', '[WHILE-WEND Statement](../language/statements/while-wend.md)', '[Arrays (DIM)](../language/statements/dim.md)', '[GOTO Statement](../language/statements/goto.md)' - none of these files are provided.

---

### missing_reference

**Description:** ASCII codes document references function and character set documentation that is not provided

**Affected files:**
- `help/common/language/appendices/ascii-codes.md`

**Details:**
help/common/language/appendices/ascii-codes.md references '[ASC](../functions/asc.md)', '[CHR$](../functions/chr_dollar.md)', '[INKEY$](../functions/inkey_dollar.md)', '[INPUT$](../functions/input_dollar.md)', '[CHR$ Function](../functions/chr_dollar.md)', '[ASC Function](../functions/asc.md)', '[Character Set](../character-set.md)' - none of these files are provided.

---

### missing_reference

**Description:** Error codes document references statement documentation that is not provided

**Affected files:**
- `help/common/language/appendices/error-codes.md`

**Details:**
help/common/language/appendices/error-codes.md references '[ON ERROR GOTO](../statements/on-error-goto.md)', '[ERR and ERL](../statements/err-erl-variables.md)', '[ERROR](../statements/error.md)', '[RESUME](../statements/resume.md)', '[Error Handling Statements](../statements/index.md#error-handling)', '[ERR and ERL Variables](../statements/err-erl-variables.md)' - none of these files are provided.

---

### inconsistent_path

**Description:** Compiler documentation references language documentation with inconsistent paths

**Affected files:**
- `help/common/compiler/index.md`
- `help/common/compiler/optimizations.md`

**Details:**
help/common/compiler/index.md uses '[BASIC-80 Language Reference](../language/index.md)' while help/common/compiler/optimizations.md uses the same path. However, help/common/language.md exists as a standalone file, creating ambiguity about which is the actual language reference entry point.

---

### missing_reference

**Description:** Missing TAB function in categorized lists

**Affected files:**
- `help/common/language/functions/index.md`

**Details:**
The TAB function appears in the alphabetical quick reference at the bottom of index.md but is not listed in any of the categorized sections (Mathematical, String, Type Conversion, File I/O, or System Functions). It should be categorized appropriately.

---

### contradictory_information

**Description:** Incorrect formula for ARCCOT

**Affected files:**
- `help/common/language/appendices/math-functions.md`

**Details:**
The formula 'ARCCOT(X) = ATN(X) + 1.5708' is incorrect. The correct formula should be 'ARCCOT(X) = ATN(1/X)' or 'ARCCOT(X) = -ATN(X) + 1.5708'. The current formula would give ATN(X) + π/2, which is not the inverse cotangent.

---

### inconsistent_see_also_sections

**Description:** File I/O functions have inconsistent 'See Also' sections - some are comprehensive, others are minimal

**Affected files:**
- `help/common/language/functions/loc.md`
- `help/common/language/functions/lof.md`
- `help/common/language/functions/pos.md`
- `help/common/language/functions/lpos.md`

**Details:**
LOC, LOF, and POS have extensive 'See Also' sections with 17 related items each (CLOSE, EOF, FIELD, FILES, GET, INPUT$, LOC/LOF/LPOS, LSET, OPEN, POS, PRINTi, PUT, RESET, RSET, WRITE #, LINE INPUT#). However, LPOS only has 3 items (POS, LPRINT, WIDTH LPRINT) despite being in the same category.

---

### version_availability_inconsistency

**Description:** Inconsistent version availability documentation across similar command-level statements

**Affected files:**
- `help/common/language/statements/auto.md`
- `help/common/language/statements/clear.md`
- `help/common/language/statements/end.md`

**Details:**
AUTO.md does not specify versions, CLEAR.md specifies 'Versions: 8K, -Extended, Disk', and END.md specifies 'Versions: 8K, Extended, Disk' (note the dash difference in '-Extended' vs 'Extended'). These are all basic command-level statements that should have consistent version availability documentation.

---

### cassette_version_inconsistency

**Description:** Inconsistent version specification for cassette commands

**Affected files:**
- `help/common/language/statements/cload.md`
- `help/common/language/statements/csave.md`

**Details:**
CLOAD.md does not specify versions in the frontmatter, while CSAVE.md specifies 'Versions: 8K (cassette), Extended (cassette)'. Both are cassette-related commands and should have consistent version documentation.

---

### implementation_note_inconsistency

**Description:** Implementation notes appear in different locations and with different formatting

**Affected files:**
- `help/common/language/statements/call.md`
- `help/common/language/statements/def-usr.md`

**Details:**
CALL.md has the implementation note at the top of the document (after title, before Syntax), while DEF-USR.md has it at the bottom (after Example, before See Also). Both should follow a consistent placement pattern for implementation notes.

---

### version_availability_missing

**Description:** Many statement files missing version availability information

**Affected files:**
- `help/common/language/statements/auto.md`
- `help/common/language/statements/call.md`
- `help/common/language/statements/cload.md`
- `help/common/language/statements/close.md`
- `help/common/language/statements/common.md`
- `help/common/language/statements/cont.md`
- `help/common/language/statements/data.md`
- `help/common/language/statements/delete.md`
- `help/common/language/statements/dim.md`
- `help/common/language/statements/edit.md`
- `help/common/language/statements/erase.md`
- `help/common/language/statements/error.md`
- `help/common/language/statements/field.md`

**Details:**
Multiple files do not specify which versions (8K, Extended, Disk) support the command, while some files like CLEAR.md, END.md, CLS.md, CHAIN.md, DEF-USR.md, ERROR.md, and FIELD.md do specify versions. This should be consistent across all statement documentation.

---

### cross-reference inconsistency

**Description:** Inconsistent cross-reference formatting in 'See Also' sections

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/gosub-return.md`
- `help/common/language/statements/goto.md`
- `help/common/language/statements/if-then-else-if-goto.md`

**Details:**
The 'See Also' sections use inconsistent formatting for the same references. For example, 'IF ••• THEN[ ••• ELSE] AND IF ••• GOTO' appears with different bullet character representations (••• vs •..) across files. In for-next.md and goto.md it's 'IF ••• THEN[ ••• ELSE] AND IF ••• GOTO', while in gosub-return.md it's 'IF ••• THEN[ ••• ELSE] AND IF ••• GOTO', and the actual file title uses 'IF ••• THEN[ ••• ELSE] AND IF ••• GOTO'.

---

### cross-reference inconsistency

**Description:** Inconsistent reference to GOSUB...RETURN statement

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/gosub-return.md`
- `help/common/language/statements/goto.md`
- `help/common/language/statements/if-then-else-if-goto.md`

**Details:**
The GOSUB...RETURN statement is referenced inconsistently: 'GOSUB •.. RETURN' (with two dots) in some files vs 'GOSUB...RETURN' (with three dots) in others. The actual file title is 'GOSUB •.. RETURN' but references vary.

---

### cross-reference inconsistency

**Description:** Inconsistent reference to ON GOSUB/GOTO statement

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/gosub-return.md`
- `help/common/language/statements/goto.md`
- `help/common/language/statements/if-then-else-if-goto.md`

**Details:**
The ON GOSUB/GOTO statement is referenced as 'ON ••• GOSUB AND ON ••• GOTO' in See Also sections, but this doesn't match common naming patterns and uses 'AND' instead of a separator like '/'.

---

### cross-reference target mismatch

**Description:** LINE INPUT cross-reference points to wrong file

**Affected files:**
- `help/common/language/statements/input.md`
- `help/common/language/statements/line-input.md`

**Details:**
input.md references '[LINE INPUT](line-input.md)' but line-input.md's See Also section references '[LINE INPUT#](input_hash.md)' suggesting potential confusion between LINE INPUT (keyboard) and LINE INPUT# (file).

---

### cross-reference inconsistency

**Description:** LINE INPUT references itself incorrectly

**Affected files:**
- `help/common/language/statements/line-input.md`
- `help/common/language/statements/inputi.md`

**Details:**
line-input.md's See Also section references '[LINE INPUT#](input_hash.md)' but LINE INPUT# is actually documented in inputi.md, not input_hash.md.

---

### missing_reference

**Description:** PRINT# documentation references non-existent file

**Affected files:**
- `help/common/language/statements/printi-printi-using.md`

**Details:**
See Also section references 'inputi.md' for LINE INPUT#, but the actual filename should likely be 'line-input_hash.md' or 'input_hash.md' based on naming conventions used elsewhere.

---

### outdated_information

**Description:** Implementation notes indicate features are not implemented but documentation preserved

**Affected files:**
- `help/common/language/statements/out.md`
- `help/common/language/statements/poke.md`

**Details:**
OUT and POKE both have implementation notes stating they are not implemented or emulated as no-ops in the Python interpreter, but full historical documentation is preserved. This could confuse users about actual functionality.

---

### contradictory_information

**Description:** PUT Purpose section has duplicate/redundant text

**Affected files:**
- `help/common/language/statements/put.md`

**Details:**
Purpose states 'To write a record from a random buffer to a random file. disk file.' - 'disk file' appears to be a duplicate/error.

---

### missing_reference

**Description:** shortcuts.md references a 'status line' for debugging that is not documented in the curses editing guide

**Affected files:**
- `help/common/shortcuts.md`
- `help/common/ui/curses/editing.md`

**Details:**
shortcuts.md states 'When breakpoint hits (status line appears at top)' but the curses editing.md does not mention or document this status line feature in its layout or description

---

### missing_reference

**Description:** settings.md references CLI settings commands but cli/index.md does not document them

**Affected files:**
- `help/common/settings.md`
- `help/common/ui/cli/index.md`

**Details:**
settings.md shows 'SHOWSETTINGS' and 'SETSETTING' commands for CLI with link to 'CLI Settings Commands' but cli/index.md does not list these commands in its 'Common Commands' table or anywhere else

---

### inconsistent_feature_availability

**Description:** Inconsistent documentation of immediate mode availability across UIs

**Affected files:**
- `help/common/ui/tk/index.md`
- `help/common/ui/curses/editing.md`

**Details:**
tk/index.md states 'Some Tk configurations include an immediate mode panel' (implying it's optional), while curses/editing.md documents 'Direct Mode' as a standard feature with 'Lines without numbers execute immediately'. The availability and consistency of this feature across UIs is unclear

---

### inconsistent_information

**Description:** Conflicting information about AUTO mode exit method

**Affected files:**
- `help/common/ui/curses/editing.md`
- `help/common/ui/cli/index.md`

**Details:**
curses/editing.md states 'Exit AUTO mode with Ctrl+C or by typing a line number manually' while cli/index.md only mentions 'Press Ctrl+C to stop AUTO mode' without mentioning the manual line number method

---

### terminology_inconsistency

**Description:** Inconsistent project naming throughout documentation

**Affected files:**
- `help/mbasic/architecture.md`
- `help/mbasic/extensions.md`
- `help/mbasic/features.md`

**Details:**
architecture.md refers to 'MBASIC' throughout. extensions.md introduces multiple potential names: 'MBASIC-2025', 'Visual MBASIC 5.21', 'MBASIC++', 'MBASIC-X' and states 'This is MBASIC-2025'. features.md uses 'this MBASIC interpreter' without specifying a version name. No consistent project name is established.

---

### missing_reference

**Description:** Web UI mentioned in some files but not consistently documented

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/extensions.md`
- `help/mbasic/features.md`
- `help/mbasic/getting-started.md`

**Details:**
extensions.md mentions 'Web' UI multiple times and compatibility.md has a detailed 'Web UI' section. However, getting-started.md only lists three interfaces (Curses, CLI, Tkinter) and provides no instructions for launching Web UI. features.md does not document Web UI at all.

---

### command_inconsistency

**Description:** Inconsistent command for launching MBASIC

**Affected files:**
- `help/mbasic/getting-started.md`
- `help/mbasic/features.md`

**Details:**
getting-started.md shows 'mbasic' as the command throughout examples. However, the installation section shows 'python3 mbasic' in extensions.md. No clear indication of whether 'mbasic' is a script, alias, or requires 'python3' prefix.

---

### contradictory_information

**Description:** Conflicting statements about WIDTH statement support

**Affected files:**
- `help/mbasic/compatibility.md`
- `help/mbasic/extensions.md`

**Details:**
compatibility.md states 'WIDTH is parsed for compatibility but performs no operation' and 'The WIDTH LPRINT syntax is not supported.' However, extensions.md does not mention WIDTH at all in its compatibility notes, creating potential confusion about what is actually supported.

---

### feature_availability_conflict

**Description:** Inconsistent information about Find/Replace availability across UIs

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/cli/find-replace.md`

**Details:**
feature-reference.md states 'Find/Replace (Not yet implemented)' for Curses UI, while cli/find-replace.md states 'For built-in Find/Replace, use the Tk UI' and mentions 'Ctrl+F for Find dialog, Ctrl+H for Replace dialog' but does not mention whether Curses UI has this feature or not.

---

### command_inconsistency

**Description:** Settings commands documented for CLI but not mentioned for Curses UI

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/cli/settings.md`

**Details:**
cli/settings.md documents SHOWSETTINGS and SETSETTING commands extensively, but feature-reference.md for Curses UI does not mention these commands or whether they are available in the Curses interface.

---

### documentation_gap

**Description:** Debugging commands documented differently between CLI and Curses

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/cli/debugging.md`

**Details:**
cli/debugging.md documents BREAK, STEP, and STACK commands in detail, while feature-reference.md for Curses documents Ctrl+B, Ctrl+T, Ctrl+K shortcuts but doesn't clarify if the CLI commands (BREAK, STEP, STACK) are also available in Curses UI or if only the keyboard shortcuts work.

---

### feature_availability_conflict

**Description:** Execution Stack access method differs between UIs

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/cli/index.md`

**Details:**
feature-reference.md states 'Execution Stack (Menu only)' for Curses UI, while cli/index.md documents 'STACK - View call stack' as a command, suggesting different access methods for the same feature across UIs.

---

### feature_availability_conflict

**Description:** Menu access inconsistency for List and Stack features

**Affected files:**
- `help/ui/curses/quick-reference.md`
- `help/ui/curses/index.md`

**Details:**
quick-reference.md states 'Menu only' for 'List program' and 'Show/hide execution stack window', but doesn't specify how to access the menu. The index.md and other documents don't clearly explain menu access in Curses UI.

---

### keyboard_shortcut_inconsistency

**Description:** Inconsistent help keyboard shortcut

**Affected files:**
- `help/ui/curses/quick-reference.md`
- `help/ui/curses/help-navigation.md`

**Details:**
quick-reference.md lists '?' as the key for 'Help (with search)', but help-navigation.md uses placeholder '{{kbd:help}}' and '{{kbd:search}}' without specifying the actual keys. The quick-reference should be the authoritative source but uses '?' while other docs suggest Ctrl+P.

---

### keyboard_shortcut_inconsistency

**Description:** Inconsistent quit/exit keyboard shortcuts

**Affected files:**
- `help/ui/curses/quick-reference.md`
- `help/ui/curses/help-navigation.md`

**Details:**
quick-reference.md lists 'Ctrl+Q' for Quit and help-navigation.md shows '{{kbd:quit}}' for exiting help. It's unclear if these are the same key or different keys for different contexts.

---

### keyboard_shortcut_inconsistency

**Description:** Inconsistent run program shortcuts

**Affected files:**
- `help/ui/tk/getting-started.md`
- `help/ui/tk/features.md`
- `help/ui/tk/feature-reference.md`

**Details:**
getting-started.md shows '{{kbd:run_program}}' without specifying the actual key, features.md also uses '{{kbd:run_program}}', but feature-reference.md specifies 'Ctrl+R / F5' and 'Ctrl+R or F5'. The documentation should consistently show both shortcuts.

---

### feature_availability_conflict

**Description:** Stop execution shortcut inconsistency

**Affected files:**
- `help/ui/curses/quick-reference.md`
- `help/ui/curses/running.md`

**Details:**
quick-reference.md lists 'Ctrl+X' for 'Stop execution' in the Debugger section, but running.md states 'Press Ctrl+X to stop a running program' in a note without clearly documenting it as the official shortcut.

---

### feature_availability_conflict

**Description:** Variable Inspector features described in debugging.md may not be implemented

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/features.md`

**Details:**
help/ui/web/debugging.md describes extensive Variable Inspector features including 'Tree view', 'Double-click any variable value', 'Edit dialog appears', 'Filtering', 'Watch Expressions', and 'Add Watch button'. However, help/ui/web/features.md only mentions basic 'Variable Inspector' with 'Display Features' and 'Editing' without confirming these advanced features are implemented. help/ui/web/getting-started.md only mentions 'Run → Show Variables' showing 'a popup shows all defined variables and their values'.

---

### feature_availability_conflict

**Description:** Call Stack visualization features may not be implemented

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/features.md`

**Details:**
help/ui/web/debugging.md describes detailed 'Call Stack Panel' with 'Shows execution path', 'Click to view source location', and 'FOR Loop Stack' features. help/ui/web/features.md mentions 'Call stack' under Debug Mode but doesn't detail these features. help/ui/web/getting-started.md only mentions 'Run → Show Stack' showing 'function/subroutine call stack' without the interactive features.

---

### feature_availability_conflict

**Description:** Debug Console features described may not be implemented

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/features.md`
- `help/ui/web/getting-started.md`

**Details:**
help/ui/web/debugging.md describes a 'Debug Console' with 'Bottom panel during debugging' that accepts 'Direct BASIC statements', 'Variable assignments', and 'Debug commands' like 'PRINT var', 'STACK', 'BREAK', 'CONT', 'STEP'. This is not mentioned in help/ui/web/features.md or help/ui/web/getting-started.md, which only describe a 'Command Area' for immediate commands that is always present, not specific to debugging.

---

### feature_availability_conflict

**Description:** Settings availability mismatch between features.md and settings.md

**Affected files:**
- `help/ui/web/features.md`
- `help/ui/web/settings.md`

**Details:**
help/ui/web/features.md describes extensive 'Settings and Preferences' including 'General Settings', 'Editor Preferences', 'Debug Preferences', 'Advanced Options' with many checkboxes and options. However, help/ui/web/settings.md states 'The web UI provides a simplified settings dialog for configuring essential MBASIC options' and only describes 'Editor Tab' (auto-numbering settings) and 'Limits Tab' (view-only). The extensive settings in features.md appear to be aspirational rather than implemented.

---

### UI reference inconsistency

**Description:** Web interface documentation mentions four UIs (Web, Tkinter, Curses, CLI) but library documentation only mentions three UIs (Web, Tkinter, Curses) and omits CLI

**Affected files:**
- `help/ui/web/web-interface.md`
- `library/business/index.md`
- `library/data_management/index.md`
- `library/demos/index.md`
- `library/education/index.md`
- `library/electronics/index.md`
- `library/games/index.md`
- `library/ham_radio/index.md`
- `library/telecommunications/index.md`
- `library/utilities/index.md`

**Details:**
web-interface.md states: 'Open MBASIC in your preferred UI (Web, Tkinter, Curses, or CLI)' in the 'About MBASIC 5.21' section. However, all library index.md files state: 'Open MBASIC in your preferred UI (Web, Tkinter, Curses, or CLI)' in the 'How to Use' section, which is actually consistent. But the web-interface.md also says 'Compared to desktop UIs' suggesting there are multiple desktop UIs, while library docs list all four equally.

---

### Menu option naming inconsistency

**Description:** File menu options are inconsistent between different sections of the same document

**Affected files:**
- `help/ui/web/web-interface.md`

**Details:**
In the 'Menu Functions' section, the File Menu lists: 'New', 'Load Example', 'Clear Output'. However, in the 'Writing Programs' section, it says 'Click Run → Run Program' suggesting a Run menu exists. But there's no mention of how to save programs or a 'Save' option, yet the document discusses writing programs you 'want to save and run multiple times'.

---

### duplicate_documentation

**Description:** Two installation guides exist with overlapping purposes but different content levels

**Affected files:**
- `user/INSTALL.md`
- `user/INSTALLATION.md`

**Details:**
INSTALL.md is a complete installation guide with detailed instructions for virtual environments, multiple installation methods, and troubleshooting. INSTALLATION.md is marked as a PLACEHOLDER with minimal content that redirects to other files. This creates confusion about which file is the authoritative installation guide.

---

### feature_availability_conflict

**Description:** Conflicting information about Curses UI variable editing capabilities

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`
- `user/QUICK_REFERENCE.md`

**Details:**
CHOOSING_YOUR_UI.md states under Curses limitations: 'Partial variable editing'. However, QUICK_REFERENCE.md does not mention any variable editing features at all for the Curses UI, suggesting either the feature doesn't exist or the documentation is incomplete.

---

### feature_availability_conflict

**Description:** Find/Replace availability inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+H' for 'Find and replace' in the Essential Keyboard Shortcuts table. However, UI_FEATURE_COMPARISON.md shows Find/Replace as 'Tk only (new feature)' with checkmark for Tk but X for Web, and states it was 'Recently Added (2025-10-29)'. But the comparison matrix shows it as available in Tk with 'Ctrl+F/H' in the keyboard shortcuts comparison section.

---

### keyboard_shortcut_inconsistency

**Description:** Help shortcut key conflict

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md does not list a help shortcut in the Essential Keyboard Shortcuts table, but mentions 'Press F1' in the Getting Help section. keyboard-shortcuts.md (Curses UI) lists '^F' for help and 'Ctrl+H' is listed separately. UI_FEATURE_COMPARISON.md shows 'F1' for Tk help.

---

### keyboard_shortcut_inconsistency

**Description:** Save shortcut inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
keyboard-shortcuts.md (Curses UI) lists 'Ctrl+V' for Save program, but TK_UI_QUICK_START.md lists 'Ctrl+S' for Save file. This creates confusion as Ctrl+V is also listed for Variables window in Tk UI.

---

### keyboard_shortcut_inconsistency

**Description:** Run program shortcut inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md lists only 'Ctrl+R' for Run program. UI_FEATURE_COMPARISON.md's keyboard shortcuts table shows 'Ctrl+R/F5' for Tk. This inconsistency should be clarified.

---

## 🟢 Low Severity

### inconsistent_terminology

**Description:** Inconsistent naming of 'Execution Stack' vs 'Stack' window

**Affected files:**
- `help/common/debugging.md`
- `help/common/editor-commands.md`

**Details:**
help/common/debugging.md uses 'Execution Stack Window' as the section header and 'Execution Stack' in shortcuts, while help/common/editor-commands.md references it as just 'Stack' in the See Also section: 'For debugging-specific commands like breakpoints and stepping, see [Debugging Features](debugging.md).'

---

### missing_reference

**Description:** Debugging documentation references a shortcuts.md file that is not provided

**Affected files:**
- `help/common/debugging.md`
- `help/common/shortcuts.md`

**Details:**
help/common/debugging.md has a 'See Also' section that includes '[Keyboard Shortcuts](shortcuts.md)' but the file help/common/shortcuts.md is not included in the documentation set.

---

### missing_reference

**Description:** Getting started guide references a data-types.md file that is not provided

**Affected files:**
- `help/common/getting-started.md`
- `help/common/language/data-types.md`

**Details:**
help/common/getting-started.md references 'See: [Variables and Data Types](language/data-types.md)' but the file help/common/language/data-types.md is not included in the documentation set.

---

### missing_reference

**Description:** Main index references language.md but also has language/index.md creating potential confusion

**Affected files:**
- `help/common/index.md`
- `help/common/language.md`

**Details:**
help/common/index.md references '[BASIC Language Reference](language/index.md)' while help/common/language.md exists as a separate file. The language.md file has '[Back to main help](index.md)' suggesting it's meant to be the language reference, but the index points to language/index.md instead.

---

### inconsistent_terminology

**Description:** Inconsistent function description for SPACE$

**Affected files:**
- `help/common/language/functions/space_dollar.md`
- `help/common/language/functions/index.md`

**Details:**
In index.md under String Functions, SPACE$ is described as 'Returns a string of spaces' but in the See Also sections of multiple files (asc.md, chr_dollar.md, etc.) it's described as 'Returns a string of I spaces'. The latter is more accurate and should be used consistently.

---

### missing_reference

**Description:** Incomplete See Also reference

**Affected files:**
- `help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
The See Also section references 'MKI$, MKS$, MKD$' but the actual file is named 'mki_dollar-mks_dollar-mkd_dollar.md' based on the index.md references. The link text should match: [MKI$, MKS$, MKD$](mki_dollar-mks_dollar-mkd_dollar.md)

---

### inconsistent_terminology

**Description:** Inconsistent capitalization of 'SINGLE' and 'DOUBLE' precision

**Affected files:**
- `help/common/language/character-set.md`
- `help/common/language/data-types.md`

**Details:**
character-set.md uses 'Single precision' and 'Double precision' (title case) while data-types.md uses 'SINGLE Precision' and 'DOUBLE Precision' (mixed case with uppercase type name). Should be standardized.

---

### missing_reference

**Description:** Incorrect See Also reference

**Affected files:**
- `help/common/language/functions/eof.md`

**Details:**
eof.md references 'LINE INPUT#' with link to '../statements/inputi.md' but based on naming conventions elsewhere, this should likely be '../statements/line-input-hash.md' or similar. The filename 'inputi.md' appears to be a typo.

---

### inconsistent_terminology

**Description:** Inconsistent spelling of 'Control-C'

**Affected files:**
- `help/common/language/functions/inkey_dollar.md`

**Details:**
The description uses both 'Contro1-C' (with number 1) and 'Control-C' (with letter l). Should consistently use 'Control-C'.

---

### missing_cross_reference

**Description:** LPOS documentation references POS function but does not include it in the 'See Also' section

**Affected files:**
- `help/common/language/functions/lpos.md`

**Details:**
The LPOS description states 'Also see the LPOS function' in the example section, but POS is not listed in the 'See Also' section. Other file I/O functions like LOC, LOF, and POS all have comprehensive 'See Also' sections that cross-reference each other.

---

### inconsistent_formatting

**Description:** Inconsistent formatting in example sections - some use 'Also see' inline, others use proper 'See Also' sections

**Affected files:**
- `help/common/language/functions/spc.md`
- `help/common/language/functions/pos.md`

**Details:**
SPC.md has 'Also see the SPACE$ function.' in the example section. POS.md has 'Also see the LPOS function.' in the example section. These should be in the 'See Also' section for consistency with other documentation.

---

### missing_cross_reference

**Description:** MID$ and RIGHT$ reference LEFT$ in their descriptions but inconsistently

**Affected files:**
- `help/common/language/functions/mid_dollar.md`
- `help/common/language/functions/right_dollar.md`

**Details:**
MID$.md states 'Also see the LEFT$ and RIGHT$ functions.' in the example section. RIGHT$.md states 'Also see the MID$ and LEFT$ functions.' in the example section. These informal references should be in the 'See Also' sections, and both should reference each other consistently.

---

### inconsistent_see_also_sections

**Description:** STR$ and VAL are complementary functions but have different 'See Also' sections

**Affected files:**
- `help/common/language/functions/str_dollar.md`
- `help/common/language/functions/val.md`

**Details:**
STR$.md has a full 'See Also' section with 14 string-related functions. VAL.md also has a full 'See Also' section with 14 string-related functions. Both mention each other in their descriptions ('Also see the VAL function' and 'See the STR$ function') but this is redundant since they're already in each other's 'See Also' sections.

---

### inconsistent_description_format

**Description:** MKI$/MKS$/MKD$ documentation has malformed example section with unrelated content

**Affected files:**
- `help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md`

**Details:**
The example section contains: '90 AMT= (K+T)
 100 FIELD #1, 8 AS D$, 20 AS N$
 110 LSET D$ = MKS$(AMT)
 120 LSET N$ = A$
 130 PUT #1
 See also CVI, CVS, CVD, Section 3.9 and Appendix
 B.
 3.27 OCT$
PRINT OCT$ (24)
 30
 Ok
 See the HEX $ function for hexadecimal
 conversion.
3.2S PEEK
A=PEEK (&H5AOO)' - This appears to be corrupted text from multiple sections merged together.

---

### inconsistent_terminology

**Description:** Inconsistent use of 'X$' vs 'string' in syntax descriptions

**Affected files:**
- `help/common/language/functions/len.md`
- `help/common/language/functions/loc.md`
- `help/common/language/functions/lof.md`

**Details:**
LEN uses 'LEN (X$)' in syntax and 'X$' throughout description. LOC and LOF use 'LOC(file number)' and 'LOF(file number)' with descriptive parameter names. This inconsistency exists across many function documentations.

---

### version_format_inconsistency

**Description:** Inconsistent formatting of 'Extended' version designation

**Affected files:**
- `help/common/language/statements/clear.md`
- `help/common/language/statements/end.md`

**Details:**
CLEAR.md uses '-Extended' (with hyphen) while END.md uses 'Extended' (without hyphen) in the Versions field. This should be standardized.

---

### see_also_inconsistency

**Description:** Inconsistent 'See Also' sections for related program control statements

**Affected files:**
- `help/common/language/statements/chain.md`
- `help/common/language/statements/clear.md`
- `help/common/language/statements/common.md`
- `help/common/language/statements/cont.md`
- `help/common/language/statements/end.md`

**Details:**
These files all reference each other in 'See Also' sections but with inconsistent groupings. For example, CHAIN.md's 'See Also' includes CLEAR, COMMON, CONT, END, NEW, RUN, STOP, SYSTEM. However, CONT.md's 'See Also' includes the same list. END.md also includes the same list. This suggests they should all have identical 'See Also' sections, but some may be missing entries or have different ordering.

---

### title_inconsistency

**Description:** Inconsistent title formatting for DEC VT180 exclusion note

**Affected files:**
- `help/common/language/statements/cload.md`
- `help/common/language/statements/csave.md`

**Details:**
CLOAD.md title: 'CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION' (5 spaces before 'THIS'). CSAVE.md title: 'CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION' (6 spaces before 'THIS'). The spacing should be consistent.

---

### cross_reference_inconsistency

**Description:** Asymmetric cross-references between related statements

**Affected files:**
- `help/common/language/statements/call.md`
- `help/common/language/statements/def-usr.md`

**Details:**
CALL.md references USR function in 'See Also' but does not reference DEF-USR. DEF-USR.md references USR, DEF FN, POKE, and PEEK but does not reference CALL. Since CALL and DEF USR are closely related (both for assembly language subroutines), they should cross-reference each other.

---

### see_also_reference_inconsistency

**Description:** FIELD.md references CLOSE.md but CLOSE.md does not reference FIELD.md

**Affected files:**
- `help/common/language/statements/close.md`
- `help/common/language/statements/field.md`

**Details:**
FIELD.md includes CLOSE in its 'See Also' section, but CLOSE.md does not include FIELD. Since FIELD is specifically for random file operations and CLOSE is used to close files, they should cross-reference each other.

---

### missing cross-reference

**Description:** FILES statement references non-existent LOAD and SAVE documentation

**Affected files:**
- `help/common/language/statements/files.md`

**Details:**
The FILES statement See Also section references '[LOAD](load.md) - Load a BASIC program' and '[SAVE](save.md) - Save a BASIC program', but the actual LOAD and SAVE documentation describe them as loading/saving 'a file from disk into memory' and 'a program file on disk' respectively, not specifically 'a BASIC program'.

---

### inconsistent related links

**Description:** Inconsistent 'related' field in frontmatter

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/gosub-return.md`

**Details:**
for-next.md has related: ['while-wend', 'goto', 'gosub-return'] while gosub-return.md has related: ['goto', 'on-gosub', 'for-next']. The references use different naming conventions (gosub-return vs on-gosub).

---

### inconsistent syntax formatting

**Description:** Inconsistent use of angle brackets and spacing in syntax blocks

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/get.md`
- `help/common/language/statements/input.md`

**Details:**
Some files use '<variable>' while others use 'variable' or '<list of variables>'. For example, for-next.md uses 'FOR <variable>=x TO y' while input.md uses 'INPUT[:] [<"prompt string">:]<list of variables>' with inconsistent spacing and bracket usage.

---

### version information inconsistency

**Description:** Inconsistent version information formatting

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/goto.md`

**Details:**
for-next.md states '**Versions:** 8K, Extended, Disk' while goto.md also states '**Versions:** 8K, Extended, Disk' but the formatting and placement relative to other content differs slightly.

---

### inconsistent file naming

**Description:** Inconsistent file naming for INPUT# and LINE INPUT#

**Affected files:**
- `help/common/language/statements/input_hash.md`
- `help/common/language/statements/inputi.md`

**Details:**
INPUT# is in file 'input_hash.md' (using underscore and hash) while LINE INPUT# is in file 'inputi.md' (using 'i' suffix). This is inconsistent naming convention.

---

### missing example content

**Description:** LINE INPUT example section references non-existent content

**Affected files:**
- `help/common/language/statements/line-input.md`

**Details:**
The Example section states 'See Example, Section 2.32, LINE INPUT#.' but this is a reference to external documentation that doesn't exist in this file set.

---

### inconsistent category naming

**Description:** Inconsistent category naming for I/O operations

**Affected files:**
- `help/common/language/statements/files.md`
- `help/common/language/statements/get.md`
- `help/common/language/statements/input_hash.md`
- `help/common/language/statements/inputi.md`
- `help/common/language/statements/line-input.md`
- `help/common/language/statements/lprint-lprint-using.md`

**Details:**
files.md uses 'category: file-io', get.md uses 'category: file-io', input_hash.md uses 'category: file-io', inputi.md uses 'category: file-io', but line-input.md also uses 'category: file-io' even though it's for keyboard input, not file I/O. lprint-lprint-using.md also uses 'category: file-io' for printer output.

---

### inconsistent_terminology

**Description:** Inconsistent use of bullet points and formatting in ON...GOSUB documentation

**Affected files:**
- `help/common/language/statements/on-gosub-on-goto.md`
- `help/common/language/statements/option-base.md`
- `help/common/language/statements/out.md`

**Details:**
The ON...GOSUB documentation uses 'ON ••• GOSUB' and 'ON ••• GOTO' with bullet points in the title and remarks, while other similar control flow statements use standard ellipsis or no special formatting.

---

### inconsistent_terminology

**Description:** Inconsistent spacing in syntax descriptions

**Affected files:**
- `help/common/language/statements/open.md`
- `help/common/language/statements/option-base.md`

**Details:**
OPEN documentation has irregular spacing in mode descriptions ('o        specifies', 'I       specifies', 'R        specifies') while OPTION BASE has inconsistent spacing in 'To declare      the     minimum   value   for   array subscripts'.

---

### inconsistent_terminology

**Description:** Inconsistent spacing in syntax parameter descriptions

**Affected files:**
- `help/common/language/statements/out.md`
- `help/common/language/statements/poke.md`

**Details:**
OUT syntax shows 'where I and J are    integer   expressions     in   the range' with irregular spacing. POKE has similar issues with 'The integer expression I is the address of the memory   location'.

---

### missing_reference

**Description:** PRINT See Also section references incomplete or incorrect filenames

**Affected files:**
- `help/common/language/statements/print.md`

**Details:**
References 'print-using' and 'lprint' without file extensions, inconsistent with other documentation that uses full filenames like 'input.md'.

---

### inconsistent_terminology

**Description:** Inconsistent spacing in Purpose descriptions

**Affected files:**
- `help/common/language/statements/option-base.md`
- `help/common/language/statements/poke.md`

**Details:**
Multiple files have irregular spacing in Purpose sections, e.g., 'To declare      the     minimum   value' and 'The integer expression I is the address of the memory   location'.

---

### inconsistent_terminology

**Description:** Inconsistent spacing in Remarks section

**Affected files:**
- `help/common/language/statements/randomize.md`

**Details:**
Text contains 'If <expression> is    omitted' with irregular spacing between 'is' and 'omitted'.

---

### inconsistent_terminology

**Description:** Inconsistent spacing and formatting in syntax

**Affected files:**
- `help/common/language/statements/save.md`

**Details:**
Syntax shows 'SAVE <filename> [,A   I ,P]' with irregular spacing between options, should likely be '[,A|,P]' or similar.

---

### inconsistent_terminology

**Description:** Inconsistent use of quotes in Remarks

**Affected files:**
- `help/common/language/statements/save.md`

**Details:**
Uses 'your   operating   system"'s   requirements' with escaped quotes and irregular spacing instead of standard apostrophe or proper quote formatting.

---

### inconsistent_terminology

**Description:** Inconsistent command for exiting MBASIC between documentation files

**Affected files:**
- `help/common/language/statements/system.md`
- `help/common/ui/cli/index.md`

**Details:**
system.md documents 'SYSTEM' as the exit command, while cli/index.md lists 'SYSTEM' in the commands table but also mentions 'Ctrl+D' (Unix/Linux) and 'Ctrl+Z' (Windows) as exit methods without clarifying the relationship

---

### missing_cross_reference

**Description:** write.md references PRINT but not WIDTH, despite WIDTH being related to output formatting

**Affected files:**
- `help/common/language/statements/width.md`
- `help/common/language/statements/write.md`

**Details:**
write.md's 'See Also' section includes PRINT but not WIDTH, even though WIDTH controls output line width which affects both PRINT and WRITE output

---

### inconsistent_terminology

**Description:** Inconsistent terminology for variable name significance

**Affected files:**
- `help/common/language/variables.md`
- `help/common/settings.md`

**Details:**
variables.md states 'Only the first 2 characters are significant' but settings.md uses 'case conflict' terminology without explaining the 2-character significance rule, which is critical to understanding when conflicts occur

---

### missing_reference

**Description:** Main index does not reference the shortcuts documentation

**Affected files:**
- `help/index.md`
- `help/common/shortcuts.md`

**Details:**
help/index.md provides comprehensive navigation to all major sections but does not mention or link to the shortcuts.md file, which contains important keyboard shortcut information

---

### inconsistent_path

**Description:** Broken relative path in See Also section

**Affected files:**
- `help/common/ui/curses/editing.md`

**Details:**
curses/editing.md links to '../../../ui/curses/running.md' which appears to have an extra '../' in the path (should likely be '../../curses/running.md' or './running.md')

---

### feature_availability_conflict

**Description:** Auto-save feature mentioned only for Web UI but not documented in features

**Affected files:**
- `help/mbasic/features.md`
- `help/mbasic/extensions.md`

**Details:**
extensions.md lists 'Auto-save (Web)' as an editor enhancement. features.md does not document Web UI at all, so this feature is not listed in the comprehensive features document.

---

### missing_reference

**Description:** Semantic analyzer optimization count mismatch in presentation

**Affected files:**
- `help/mbasic/architecture.md`
- `help/mbasic/features.md`

**Details:**
architecture.md provides detailed documentation of '18 distinct optimizations' with full descriptions. features.md also mentions '18 optimizations' but provides a numbered list. Both agree on the count, but the presentation and level of detail differs significantly, which could confuse readers about whether they're the same features.

---

### version_reference_inconsistency

**Description:** Inconsistent references to MBASIC version

**Affected files:**
- `help/mbasic/architecture.md`
- `help/mbasic/compatibility.md`
- `help/mbasic/features.md`
- `help/mbasic/getting-started.md`

**Details:**
Documents variously refer to 'MBASIC 5.21', 'MBASIC-80', 'MBASIC 5.21 for CP/M-80', and 'Microsoft BASIC-80 5.21'. While these likely refer to the same thing, the inconsistent naming could confuse readers about whether these are different versions.

---

### feature_availability_conflict

**Description:** Variables Window availability inconsistency

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/cli/variables.md`

**Details:**
cli/variables.md states 'The CLI does not have a Variables Window feature' and lists 'Curses UI - Full-screen terminal with Variables Window (Ctrl+W)' as an alternative. This is consistent with feature-reference.md which documents Ctrl+W for Variables Window, but the cross-reference could be clearer.

---

### missing_cross_reference

**Description:** Placeholder document referenced but not complete

**Affected files:**
- `help/mbasic/index.md`
- `help/ui/common/running.md`

**Details:**
mbasic/index.md links to 'Running Programs' as '../common/running.md' but that file is marked as 'PLACEHOLDER - Documentation in progress' with minimal content, creating a broken user experience.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for execution control

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/cli/debugging.md`

**Details:**
feature-reference.md uses 'Step Statement (Ctrl+T)' and 'Step Line (Ctrl+K)' while cli/debugging.md uses 'STEP [n]', 'STEP INTO', 'STEP OVER' without clarifying the relationship between these different stepping modes.

---

### keyboard_shortcut_inconsistency

**Description:** Settings shortcut not mentioned in main index

**Affected files:**
- `help/ui/curses/settings.md`
- `help/ui/curses/index.md`

**Details:**
settings.md documents 'Ctrl+,' as the keyboard shortcut to open settings, but this shortcut is not listed in index.md or quick-reference.md, making it difficult for users to discover.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for clearing program

**Affected files:**
- `help/ui/curses/files.md`
- `help/ui/curses/quick-reference.md`

**Details:**
files.md uses 'Creating a New Program' with Ctrl+N that 'clears the current program', while quick-reference.md calls it 'New program'. The action is the same but terminology differs.

---

### feature_availability_conflict

**Description:** Find/Replace shortcut inconsistency

**Affected files:**
- `help/ui/tk/feature-reference.md`
- `help/ui/tk/features.md`

**Details:**
feature-reference.md lists 'Find: Ctrl+F' and 'Replace: Ctrl+H', but features.md uses placeholders '{{kbd:find}}' and '{{kbd:find_replace}}' without clarifying if these resolve to the same shortcuts.

---

### missing_reference

**Description:** Find/Replace documentation not linked from main navigation

**Affected files:**
- `help/ui/curses/find-replace.md`
- `help/ui/curses/index.md`
- `help/ui/curses/quick-reference.md`

**Details:**
find-replace.md exists and documents that Find/Replace is not implemented in Curses UI, but this document is not linked from index.md or quick-reference.md, making it hard to discover.

---

### command_inconsistency

**Description:** Inconsistent command line syntax for starting MBASIC

**Affected files:**
- `help/ui/curses/files.md`
- `help/ui/tk/getting-started.md`

**Details:**
files.md shows 'python3 mbasic --ui curses myprogram.bas' while tk/getting-started.md shows 'mbasic --ui tk [filename.bas]'. The python3 prefix is inconsistent - either both should show it or neither should.

---

### feature_availability_conflict

**Description:** Performance Profiling and Memory Usage monitoring may not be implemented

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/features.md`

**Details:**
help/ui/web/debugging.md describes 'Performance Profiling' with 'Line execution counts', 'Time spent per line', 'Hotspot identification' and 'Memory Usage' monitoring. These features are not mentioned in help/ui/web/features.md or any other Web UI documentation.

---

### inconsistent_terminology

**Description:** Inconsistent capitalization of 'auto-numbering' vs 'Auto-Numbering'

**Affected files:**
- `help/ui/tk/settings.md`
- `help/ui/web/settings.md`

**Details:**
help/ui/tk/settings.md uses 'Auto Number' and 'Auto-Numbering' (capitalized), while help/ui/web/settings.md uses 'auto-numbering' (lowercase) in some places and 'Auto-Numbering' in headers. The terminology should be consistent across documents.

---

### missing_reference

**Description:** Keyboard shortcut placeholders not resolved

**Affected files:**
- `help/ui/tk/tips.md`
- `help/ui/tk/workflows.md`

**Details:**
help/ui/tk/tips.md and help/ui/tk/workflows.md use placeholder syntax like '{{kbd:smart_insert}}', '{{kbd:run_program}}', '{{kbd:save_file}}', etc. These appear to be template variables that should be replaced with actual keyboard shortcuts but are left unresolved.

---

### feature_availability_conflict

**Description:** Collaboration and Version Control features may not be implemented

**Affected files:**
- `help/ui/web/features.md`

**Details:**
help/ui/web/features.md describes 'Collaboration' features including 'Share via link', 'Read-only mode', 'Collaborative editing', 'Live output sharing' and 'Version Control' with 'Local history', 'Snapshot saves', 'Diff viewer'. These advanced features are not mentioned in any other Web UI documentation and appear aspirational.

---

### inconsistent_information

**Description:** Auto-save interval inconsistency

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/features.md`

**Details:**
help/ui/web/getting-started.md states 'Your work is automatically saved to browser localStorage every 30 seconds' in two places. help/ui/web/features.md under 'Automatic Saving' also says 'Every 30 seconds'. However, under 'Customization' → 'Behavior Settings', it mentions 'Auto-save interval' as a configurable setting, suggesting the 30 seconds may not be fixed.

---

### File loading instruction inconsistency

**Description:** Library documentation uses inconsistent terminology for file loading between GUI and CLI methods

**Affected files:**
- `library/business/index.md`
- `library/data_management/index.md`
- `library/demos/index.md`
- `library/education/index.md`
- `library/electronics/index.md`
- `library/games/index.md`
- `library/ham_radio/index.md`
- `library/telecommunications/index.md`
- `library/utilities/index.md`

**Details:**
All library index files say 'Web/Tkinter UI: Click File → Open, select the downloaded file' but this conflicts with web-interface.md which describes the menu as having 'Load Example' not 'Open'. The web interface documentation shows 'File Menu' with 'New', 'Load Example', 'Clear Output' but no 'Open' option.

---

### Terminology inconsistency

**Description:** Inconsistent category naming in 'About' sections

**Affected files:**
- `library/business/index.md`
- `library/data_management/index.md`
- `library/demos/index.md`
- `library/education/index.md`
- `library/electronics/index.md`
- `library/games/index.md`
- `library/ham_radio/index.md`
- `library/telecommunications/index.md`
- `library/utilities/index.md`

**Details:**
Most library files say 'About These [Category Name]' using plural form (e.g., 'About These Games', 'About These Utilities'), but some use singular or inconsistent forms. For example: 'About These Data Management' (should be 'Programs'), 'About These Ham Radio' (should be 'Programs'), 'About These Electronics' (should be 'Programs'), 'About These Telecommunications' (should be 'Programs').

---

### Missing documentation reference

**Description:** Case handling guide references documentation files that are not included in the provided set

**Affected files:**
- `user/CASE_HANDLING_GUIDE.md`

**Details:**
CASE_HANDLING_GUIDE.md references 'SETTINGS_AND_CONFIGURATION.md', 'TK_UI_QUICK_START.md', and 'QUICK_REFERENCE.md' in the 'See Also' section, but these files are not present in the documentation set provided for analysis.

---

### missing_reference

**Description:** CHOOSING_YOUR_UI.md is not listed in the user/README.md contents section

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`
- `user/README.md`

**Details:**
user/README.md lists only three documents in its Contents section: QUICK_REFERENCE.md, URWID_UI.md, and FILE_FORMAT_COMPATIBILITY.md. However, CHOOSING_YOUR_UI.md is a substantial user-facing document that should be included in this index.

---

### missing_reference

**Description:** SETTINGS_AND_CONFIGURATION.md is not listed in the user/README.md contents section

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/README.md`

**Details:**
user/README.md does not list SETTINGS_AND_CONFIGURATION.md in its Contents section, despite it being a comprehensive user-facing guide for configuring MBASIC.

---

### inconsistent_terminology

**Description:** Inconsistent naming of the Curses UI

**Affected files:**
- `user/QUICK_REFERENCE.md`
- `user/CHOOSING_YOUR_UI.md`

**Details:**
QUICK_REFERENCE.md refers to 'MBASIC Curses IDE' and 'Curses UI' while CHOOSING_YOUR_UI.md consistently uses 'Curses' or 'Curses (Terminal UI)'. The term 'IDE' is applied to Curses in QUICK_REFERENCE.md but CHOOSING_YOUR_UI.md describes it as a 'TUI' (Terminal UI).

---

### missing_reference

**Description:** References non-existent UI_FEATURE_COMPARISON.md file

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`

**Details:**
At the end of CHOOSING_YOUR_UI.md, under 'More Information', it references '[UI Feature Comparison](UI_FEATURE_COMPARISON.md)' but this file is not included in the provided documentation set.

---

### inconsistent_command_syntax

**Description:** Inconsistent use of python3 vs python command

**Affected files:**
- `user/CHOOSING_YOUR_UI.md`
- `user/INSTALL.md`

**Details:**
CHOOSING_YOUR_UI.md consistently uses 'python3 mbasic' throughout all examples. INSTALL.md uses both 'python3' and 'python' interchangeably, with a troubleshooting section suggesting to try 'python' if 'python3' doesn't work. This inconsistency may confuse users about which command to use.

---

### outdated_reference

**Description:** References example files that may not exist in user documentation directory

**Affected files:**
- `user/QUICK_REFERENCE.md`

**Details:**
QUICK_REFERENCE.md references 'test_continue.bas', 'demo_continue.bas', and 'test_continue_manual.sh' under Examples section, but these files are not present in the user/ directory and their location is not specified.

---

### inconsistent_terminology

**Description:** Inconsistent capitalization of UI names

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/CHOOSING_YOUR_UI.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md refers to 'TK UI' (all caps) in the Related Documentation section, while CHOOSING_YOUR_UI.md uses 'Tk' (mixed case) consistently throughout the document.

---

### feature_availability_conflict

**Description:** Smart Insert feature availability unclear

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md extensively documents Smart Insert (Ctrl+I) as a Tk feature. UI_FEATURE_COMPARISON.md confirms it as 'Tk exclusive feature' with checkmark only for Tk. However, the comparison doesn't explicitly mention this in the 'Unique Features' section for Tk, only listing 'Smart Insert mode'.

---

### terminology_inconsistency

**Description:** Inconsistent terminology for execution control

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md uses 'Step through code (next statement)' for Ctrl+T and 'Step through code (next line)' for Ctrl+L. keyboard-shortcuts.md uses 'Step Statement' for Ctrl+T and 'Step Line' for Ctrl+K (different key). The terminology and key mappings differ between UIs.

---

### feature_documentation_mismatch

**Description:** Auto-save feature documentation inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
UI_FEATURE_COMPARISON.md shows Tk as having 'optional' auto-save with ⚠️ symbol, while Web has automatic auto-save. However, TK_UI_QUICK_START.md does not mention auto-save functionality at all, only manual save with Ctrl+S.

---

