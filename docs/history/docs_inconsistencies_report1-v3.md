# Documentation Inconsistencies Report

Generated: 2025-11-03 16:33:30
Scanned directories: help, library, stylesheets, user

Found 123 inconsistencies:

## 🔴 High Severity

### contradictory_information

**Description:** LSET syntax and purpose documented inconsistently between files

**Affected files:**
- `help/common/language/statements/lprint-lprint-using.md`
- `help/common/language/statements/lset.md`

**Details:**
In lprint-lprint-using.md, LSET is documented with syntax 'LSET <string variable> = <string expression>' under the LPRINT section with purpose 'To move data from memory to a random file buffer'. In lset.md, LSET has its own dedicated page with the same syntax but purpose 'To left-justify a string in a field for random file I/O operations.' The lprint-lprint-using.md file incorrectly groups LSET with LPRINT commands when LSET is a separate file I/O command.

---

### contradictory_information

**Description:** RSET syntax documented in wrong file

**Affected files:**
- `help/common/language/statements/lprint-lprint-using.md`
- `help/common/language/statements/lset.md`

**Details:**
In lprint-lprint-using.md, RSET syntax 'RSET <string variable> = <string expression>' is listed alongside LPRINT and LSET, but RSET is a separate file I/O command unrelated to line printer output. The lset.md file correctly references RSET as a related command for right-justification in random file operations.

---

### contradictory_information

**Description:** SET statement syntax conflicts with settings documentation

**Affected files:**
- `help/common/language/statements/setsetting.md`
- `help/common/settings.md`

**Details:**
setsetting.md shows syntax as 'SET "setting.name" value' (quoted string), but settings.md shows CLI usage as 'SETSETTING editor.auto_number_step 100' (unquoted, different command name). The command name differs: 'SET' vs 'SETSETTING'.

---

### contradictory_information

**Description:** Conflicting information about Find/Replace availability

**Affected files:**
- `help/mbasic/extensions.md`
- `help/common/ui/tk/index.md`

**Details:**
extensions.md states 'Find/Replace (Tk only currently)' implying Replace is available in Tk. However, help/common/ui/tk/index.md only documents 'Find (Ctrl+F)' in the Edit Menu with no mention of Replace functionality at all.

---

### feature_availability_conflict

**Description:** Contradictory information about Find/Replace availability in Curses UI

**Affected files:**
- `help/ui/curses/find-replace.md`
- `help/ui/curses/feature-reference.md`

**Details:**
help/ui/curses/find-replace.md states 'The Curses UI currently **does not have** Find/Replace functionality. This feature is planned for future implementation.' However, help/ui/curses/feature-reference.md lists 'Find/Replace (Ctrl+F / Ctrl+H)' as an available Editor Feature with full functionality including 'Search for text in your program and optionally replace it' with options for 'Case-sensitive or insensitive search, Whole word matching, Replace single or replace all'.

---

### keyboard_shortcut_conflict

**Description:** Conflicting keyboard shortcuts for Continue command

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/quick-reference.md`

**Details:**
help/ui/curses/feature-reference.md lists 'Continue (Ctrl+C)' under Execution & Control, but help/ui/curses/quick-reference.md shows '{{kbd:continue}}' (a placeholder) in the Global Commands table and also lists '{{kbd:continue}}' under Debugger section. The actual key binding is inconsistent.

---

### keyboard_shortcut_conflict

**Description:** Inconsistent Save keyboard shortcut documentation

**Affected files:**
- `help/ui/curses/files.md`
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/quick-reference.md`

**Details:**
help/ui/curses/files.md states 'Press **Ctrl+V**' for saving and notes 'Ctrl+S unavailable due to terminal flow control'. help/ui/curses/feature-reference.md lists 'Save File (Ctrl+V)' with the same note. However, help/ui/curses/quick-reference.md shows '{{kbd:save}}' as a placeholder without specifying the actual key.

---

### feature_availability_conflict

**Description:** Breakpoint implementation status is contradictory between files

**Affected files:**
- `help/ui/web/features.md`
- `help/ui/web/getting-started.md`

**Details:**
In features.md under 'Debugging Tools > Breakpoints', it states 'Currently Implemented: Line breakpoints (toggle via Debug menu)' and describes using 'Debug → Toggle Breakpoint' menu. However, getting-started.md describes breakpoints under 'Debugging Features > Breakpoints' using 'Debug → Toggle Breakpoint' menu, but the getting-started.md interface overview only lists 'File', 'Run', and 'Help' menus - no 'Debug' menu is mentioned. The toolbar section also doesn't mention any Debug menu.

---

### ui_component_inconsistency

**Description:** Menu bar structure is inconsistent across documentation

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/features.md`
- `help/ui/web/debugging.md`

**Details:**
getting-started.md states 'At the very top, three menus: File, Run, Help' but features.md and debugging.md both reference a 'Debug' menu with options like 'Debug → Toggle Breakpoint' and 'Debug → Clear All Breakpoints'. This fourth menu is not mentioned in the interface overview.

---

### contradictory_information

**Description:** Conflicting information about auto-numbering configuration location

**Affected files:**
- `help/ui/web/settings.md`
- `help/ui/web/web-interface.md`

**Details:**
settings.md describes auto-numbering as configurable via Settings dialog: 'Enable auto-numbering (checkbox) - When checked, lines typed without numbers get auto-numbered'. However, web-interface.md describes auto-numbering as a fixed feature: 'Automatic line numbering when you press Enter' and 'The Program Editor automatically adds line numbers when you press Enter' with no mention of it being configurable or optional.

---

### keyboard_shortcut_inconsistency

**Description:** Variables window keyboard shortcut is inconsistent across documentation

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md mentions 'Ctrl+W in TK UI' for Variables & Resources window. TK_UI_QUICK_START.md lists both 'Ctrl+V' for Variables window and 'Ctrl+W' for Variables & Resources window as separate shortcuts. keyboard-shortcuts.md (Curses UI) only mentions 'Ctrl+W' for toggle variables watch window. This creates confusion about which shortcut does what in which UI.

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
help/common/examples/hello-world.md references '[PRINT Statement](../language/statements/print.md)', '[END Statement](../language/statements/end.md)'. help/common/examples/loops.md references '[FOR-NEXT Statement](../language/statements/for-next.md)', '[WHILE-WEND Statement](../language/statements/while-wend.md)', '[Arrays (DIM)](../language/statements/dim.md)', '[GOTO Statement](../language/statements/goto.md)'. None of these files are provided.

---

### missing_reference

**Description:** ASCII codes document references function and character set documentation that is not provided

**Affected files:**
- `help/common/language/appendices/ascii-codes.md`

**Details:**
help/common/language/appendices/ascii-codes.md references '[ASC](../functions/asc.md)', '[CHR$](../functions/chr_dollar.md)', '[INKEY$](../functions/inkey_dollar.md)', '[INPUT$](../functions/input_dollar.md)', '[CHR$ Function](../functions/chr_dollar.md)', '[ASC Function](../functions/asc.md)', and '[Character Set](../character-set.md)' - none of these files are provided.

---

### missing_reference

**Description:** Error codes document references statement documentation that is not provided

**Affected files:**
- `help/common/language/appendices/error-codes.md`

**Details:**
help/common/language/appendices/error-codes.md references '[ON ERROR GOTO](../statements/on-error-goto.md)', '[ERR and ERL](../statements/err-erl-variables.md)', '[ERROR](../statements/error.md)', '[RESUME](../statements/resume.md)', '[Error Handling Statements](../statements/index.md#error-handling)', and '[ERR and ERL Variables](../statements/err-erl-variables.md)' - none of these files are provided.

---

### missing_reference

**Description:** README references UI-specific help index files that are not provided

**Affected files:**
- `help/README.md`

**Details:**
help/README.md lists entry points for all UI backends: '[ui/cli/index.md](ui/cli/index.md)', '[ui/curses/index.md](ui/curses/index.md)', '[ui/tk/index.md](ui/tk/index.md)', '[ui/visual/index.md](ui/visual/index.md)', '[ui/web/index.md](ui/web/index.md)' - none of these files are included in the documentation set.

---

### missing_reference

**Description:** CSNG function is not listed in the functions index but has a dedicated documentation file

**Affected files:**
- `help/common/language/functions/index.md`
- `help/common/language/functions/csng.md`

**Details:**
The index.md file lists CINT and CDBL under 'Type Conversion Functions' but omits CSNG. However, csng.md exists and documents this function. The alphabetical quick reference also does not include CSNG.

---

### inconsistent_information

**Description:** Conflicting information about line continuation support

**Affected files:**
- `help/common/language/appendices/math-functions.md`
- `help/common/language/character-set.md`

**Details:**
math-functions.md shows no mention of line continuation limitations. character-set.md explicitly states 'Line continuation: Not supported in MBASIC 5.21. Use `:` to combine statements' under Special Sequences section.

---

### missing_reference

**Description:** ASCII codes appendix referenced but not provided

**Affected files:**
- `help/common/language/character-set.md`
- `help/common/language/appendices/math-functions.md`

**Details:**
character-set.md has 'See Also' section with link to '[ASCII Codes](appendices/ascii-codes.md) - Complete ASCII table', but this file is not included in the provided documentation set. math-functions.md also references appendices but the file structure shows it IS in appendices directory.

---

### feature_availability

**Description:** Index page claims 63 commands and statements, but actual count may differ

**Affected files:**
- `help/common/language/index.md`
- `help/common/language/statements/index.md`

**Details:**
help/common/language/index.md states '63 commands and statements' in Quick Access section. This should be verified against the actual statements/index.md file which is referenced but not provided in the documentation set.

---

### feature_availability

**Description:** Index page claims 40 intrinsic functions, but actual count should be verified

**Affected files:**
- `help/common/language/index.md`
- `help/common/language/statements/index.md`

**Details:**
help/common/language/index.md states '40 intrinsic functions' in Quick Access section. This should be verified against the actual functions/index.md file which is referenced but not provided in the documentation set.

---

### cross-reference-inconsistency

**Description:** err-erl-variables.md lists 'See Also' references to CLOAD and CSAVE which are unrelated to error handling, while error.md correctly references only error-handling related statements

**Affected files:**
- `help/common/language/statements/err-erl-variables.md`
- `help/common/language/statements/error.md`

**Details:**
err-erl-variables.md includes in 'See Also': 'CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION', 'CSAVE THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION', 'CVI, CVS, CVD', 'DEFINT/SNG/DBL/STR', 'INPUT#', 'LINE INPUT', 'LPRINT AND LPRINT USING', 'MKI$, MKS$, MKD$', 'SPACE$', 'TAB' - these are mostly I/O and data conversion functions unrelated to error handling. error.md correctly references only 'ON ERROR GOTO' and 'RESUME'.

---

### cross-reference-inconsistency

**Description:** input_hash.md and line-input.md have identical 'See Also' sections listing CLOAD, CSAVE, CVI/CVS/CVD, and other unrelated commands, which don't make sense for file I/O statements

**Affected files:**
- `help/common/language/statements/input_hash.md`
- `help/common/language/statements/line-input.md`

**Details:**
Both files list: 'CLOAD THIS COMMAND IS NOT INCLUDED IN THE DEC VT180 VERSION', 'CSAVE', 'CVI, CVS, CVD', 'DEFINT/SNG/DBL/STR', 'LPRINT AND LPRINT USING', 'MKI$, MKS$, MKD$', 'SPACE$', 'TAB'. These appear to be copy-pasted incorrectly as they're not relevant to sequential file input operations.

---

### documentation-completeness

**Description:** INPUT statement documentation has empty Remarks section

**Affected files:**
- `help/common/language/statements/input.md`

**Details:**
The input.md file has '## Remarks' header followed by empty content, then jumps directly to '## Example'. This is incomplete documentation compared to other statement files which have detailed Remarks sections.

---

### missing_references

**Description:** RENUM documentation missing from See Also sections

**Affected files:**
- `help/common/language/statements/renum.md`

**Details:**
The renum.md file is a comprehensive documentation for the RENUM command, but it is not referenced in any of the other files' 'See Also' sections, even though files like edit.md, delete.md, auto.md, and list.md would logically reference it as a related editing command.

---

### inconsistent_terminology

**Description:** Inconsistent file naming convention for hash/pound symbol

**Affected files:**
- `help/common/language/statements/lprint-lprint-using.md`
- `help/common/language/statements/printi-printi-using.md`

**Details:**
The file printi-printi-using.md uses 'i' to represent '#' in the filename (PRINTi), while other references in See Also sections use 'hash' (e.g., 'input_hash.md'). The syntax shown is 'PRINTt<filenumb~r>' which appears to have a typo with 't' instead of '#'.

---

### missing_references

**Description:** MID$ assignment statement not cross-referenced

**Affected files:**
- `help/common/language/statements/mid-assignment.md`

**Details:**
The mid-assignment.md file documents the MID$ assignment statement (MID$(string-var, start[, length]) = expression) which is distinct from the MID$ function. However, none of the other string-related documentation files reference this assignment form in their See Also sections, even though it's a related string manipulation feature.

---

### inconsistent_see_also_sections

**Description:** File I/O related statements have inconsistent 'See Also' sections - some include comprehensive lists while others are missing relevant cross-references

**Affected files:**
- `help/common/language/statements/reset.md`
- `help/common/language/statements/rset.md`
- `help/common/language/statements/writei.md`

**Details:**
reset.md has extensive 'See Also' with 17 items including CLOSE, OPEN, FIELD, etc. rset.md has identical list. writei.md also has similar comprehensive list. However, these lists appear to be copy-pasted boilerplate that includes irrelevant items like LPOS (line printer position) for file operations.

---

### inconsistent_see_also_sections

**Description:** Program control statements have identical 'See Also' sections despite different purposes

**Affected files:**
- `help/common/language/statements/run.md`
- `help/common/language/statements/stop.md`
- `help/common/language/statements/system.md`

**Details:**
RUN, STOP, and SYSTEM all have the exact same 'See Also' list (CHAIN, CLEAR, COMMON, CONT, END, NEW, RUN, STOP, SYSTEM), which appears to be boilerplate. This doesn't help users understand the specific differences between these commands.

---

### inconsistent_see_also_sections

**Description:** System/configuration statements have identical 'See Also' sections that mix unrelated commands

**Affected files:**
- `help/common/language/statements/setsetting.md`
- `help/common/language/statements/showsettings.md`
- `help/common/language/statements/tron-troff.md`
- `help/common/language/statements/width.md`

**Details:**
SET, SHOW SETTINGS, TRON/TROFF, and WIDTH all share the same 'See Also' list including FRE, INKEY$, INP, PEEK, USR, VARPTR - mixing memory/hardware functions with configuration commands. This appears to be copy-pasted boilerplate.

---

### missing_documentation

**Description:** SET and SHOW SETTINGS reference HELP SET command that doesn't have its own documentation file

**Affected files:**
- `help/common/language/statements/setsetting.md`
- `help/common/language/statements/showsettings.md`

**Details:**
Both files reference 'HELP SET' in 'See Also' sections (helpsetting.md), but this file is not included in the provided documentation set. The reference appears in multiple files but the target doesn't exist.

---

### inconsistent_terminology

**Description:** Settings command name inconsistency

**Affected files:**
- `help/common/language/statements/setsetting.md`
- `help/common/settings.md`

**Details:**
setsetting.md uses 'SET (setting)' as the title and 'SET "setting.name" value' as syntax. settings.md uses 'SETSETTING editor.auto_number_step 100' in examples. The actual command name is unclear - is it SET or SETSETTING?

---

### incomplete_documentation

**Description:** Variables documentation is marked as placeholder but referenced by other documents

**Affected files:**
- `help/common/language/variables.md`

**Details:**
variables.md is marked 'PLACEHOLDER - Documentation in progress' but is likely referenced by other documentation. This creates broken or incomplete information flow.

---

### contradictory_information

**Description:** WIDTH documentation contradicts itself about LPRINT support

**Affected files:**
- `help/common/language/statements/width.md`

**Details:**
Implementation note says 'The "WIDTH LPRINT" syntax is not supported (parse error)' but the Syntax section shows 'WIDTH LPRINT <integer expression>' as valid original MBASIC syntax. This creates confusion about what's actually supported.

---

### missing_reference

**Description:** Curses editing.md references a non-existent running.md file

**Affected files:**
- `help/common/ui/curses/editing.md`
- `help/common/ui/cli/index.md`

**Details:**
In help/common/ui/curses/editing.md, the 'See Also' section links to '../../../ui/curses/running.md' but this file is not provided in the documentation set. The CLI index.md doesn't have this issue.

---

### feature_availability_conflict

**Description:** Tk UI features described differently in extensions vs UI documentation

**Affected files:**
- `help/mbasic/extensions.md`
- `help/common/ui/tk/index.md`

**Details:**
In extensions.md, Find/Replace is listed as 'Tk only currently' under Editor Enhancements. However, in help/common/ui/tk/index.md under the Edit Menu, Find is listed as 'Ctrl+F' but there's no mention of Replace functionality, only 'Find' is documented.

---

### missing_reference

**Description:** Index references UI-specific help with incorrect paths

**Affected files:**
- `help/index.md`

**Details:**
In help/index.md under 'UI-Specific Help', it lists links like '[Tk (Desktop GUI)](ui/tk/index.md)' and '[CLI (Command Line)](ui/cli/index.md)'. However, based on the provided files, the actual paths should be 'common/ui/tk/index.md' and 'common/ui/cli/index.md' since the files are located at help/common/ui/*/index.md.

---

### feature_availability_conflict

**Description:** Immediate mode panel availability unclear

**Affected files:**
- `help/mbasic/extensions.md`
- `help/common/ui/tk/index.md`

**Details:**
In help/common/ui/tk/index.md, it states 'Some Tk configurations include an immediate mode panel' suggesting it's optional. However, extensions.md doesn't clarify this variability when describing Tk features, potentially misleading users about what to expect.

---

### missing_documentation

**Description:** Features.md mentions SHOWSETTINGS and SETSETTING commands but they are not listed in CLI index.md's common commands section

**Affected files:**
- `help/mbasic/features.md`
- `help/ui/cli/index.md`

**Details:**
help/ui/cli/settings.md documents SHOWSETTINGS and SETSETTING commands, but help/ui/cli/index.md does not mention them in the 'Common Commands' section, only listing LIST, RUN, LOAD, SAVE, NEW, AUTO, RENUM, SYSTEM

---

### placeholder_content

**Description:** Placeholder documentation exists that may conflict with actual implementation

**Affected files:**
- `help/ui/common/errors.md`

**Details:**
help/ui/common/errors.md is marked as 'PLACEHOLDER - Documentation in progress' and references paths like 'docs/help/common/language/statements/on-error-goto.md' which use a different path structure than the actual help files (help/ vs docs/help/)

---

### feature_availability_conflict

**Description:** Conflicting information about variable editing capability

**Affected files:**
- `help/ui/curses/variables.md`
- `help/ui/curses/feature-reference.md`

**Details:**
help/ui/curses/variables.md states '⚠️ **Partial Implementation**: Variable editing in Curses UI is limited' and lists 'Cannot edit values directly in window' under 'What Doesn't Work Yet'. However, help/ui/curses/feature-reference.md lists 'Edit Variable Value (e key in variables window)' as a fully available feature that can 'Modify a variable's value during debugging'.

---

### keyboard_shortcut_conflict

**Description:** Inconsistent Step Line keyboard shortcut

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/quick-reference.md`

**Details:**
help/ui/curses/feature-reference.md lists 'Step Line (Ctrl+K)' but help/ui/curses/quick-reference.md shows '{{kbd:step_line}}' as a placeholder in the Debugger section without specifying Ctrl+K.

---

### feature_availability_conflict

**Description:** Execution Stack access method inconsistency

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/quick-reference.md`

**Details:**
help/ui/curses/feature-reference.md states 'Execution Stack (Menu only)' indicating it's only accessible through the menu. However, help/ui/curses/quick-reference.md lists 'Menu only' for 'Toggle execution stack window' in Global Commands, but doesn't clarify if there's a keyboard shortcut.

---

### keyboard_shortcut_conflict

**Description:** Stop/Interrupt keyboard shortcut inconsistency

**Affected files:**
- `help/ui/curses/running.md`
- `help/ui/curses/feature-reference.md`

**Details:**
help/ui/curses/running.md states 'Press **Ctrl+X** to stop a running program' but help/ui/curses/feature-reference.md lists 'Stop/Interrupt (Ctrl+X)' which is consistent. However, the common/running.md placeholder mentions 'Press Ctrl+C or use STOP button to interrupt' which conflicts with Curses-specific documentation.

---

### feature_description_conflict

**Description:** Interface layout description differs between files

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/index.md`

**Details:**
getting-started.md describes 'a simple, vertical layout' with 7 numbered components (Menu Bar, Toolbar, Program Editor, Output, Input Area, Command Area, Status Bar). However, index.md describes 'Three-pane interface - Editor, Output, Command areas' which is a simplified description that doesn't match the detailed 7-component layout.

---

### feature_availability_conflict

**Description:** File operations description conflicts

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/features.md`

**Details:**
getting-started.md states 'The Web UI uses browser localStorage for auto-save functionality and downloads for explicit saves to your computer' and mentions 'Auto-save enabled: Your work is automatically saved to browser localStorage every 30 seconds'. However, features.md under 'File Management > Local Storage' states 'Automatic Saving: Saves to browser storage, Every 30 seconds' but also mentions 'Session Recovery' features. The getting-started.md doesn't mention session recovery in its file operations section.

---

### ui_component_inconsistency

**Description:** Variables window/panel implementation unclear

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/getting-started.md`

**Details:**
debugging.md describes a 'Variables Panel' with detailed features like 'Located in right sidebar during debugging' with tree view, filtering, and interactive editing. However, getting-started.md only mentions 'Show Variables' as a menu option that shows 'A popup shows all defined variables and their values', suggesting a modal dialog rather than a persistent panel.

---

### keyboard_shortcut_inconsistency

**Description:** Keyboard shortcuts mentioned but not consistently documented

**Affected files:**
- `help/ui/web/debugging.md`
- `help/ui/web/getting-started.md`

**Details:**
debugging.md lists extensive keyboard shortcuts (F5, F9, F10, F11, Ctrl+F, etc.) under 'Keyboard Shortcuts' section. However, getting-started.md makes no mention of these shortcuts and only refers to clicking buttons. The getting-started guide should at least mention that keyboard shortcuts exist and reference the shortcuts documentation.

---

### missing_reference

**Description:** settings.md describes a Settings dialog with keyboard shortcut Ctrl+, and menu access, but web-interface.md does not mention Settings in its Menu Bar section

**Affected files:**
- `help/ui/web/settings.md`
- `help/ui/web/web-interface.md`

**Details:**
settings.md states: 'Opening Settings: 1. Click the ⚙️ Settings icon in the navigation bar 2. Use keyboard shortcut: Ctrl+, (if enabled) 3. Click menu → Settings'. However, web-interface.md's 'Menu Bar' section lists 'File Menu', 'Edit Menu', 'Run Menu', and 'Help Menu' but does not mention a Settings menu option or Settings icon in the navigation bar.

---

### contradictory_information

**Description:** Conflicting information about line number increment configurability

**Affected files:**
- `help/ui/web/settings.md`
- `help/ui/web/web-interface.md`

**Details:**
settings.md describes line number increment as configurable: 'Line number increment (number input) - Range: 1-1000 - Default: 10'. However, web-interface.md describes it as fixed: 'First line: Starts at 10, Subsequent lines: Increment by 10 (20, 30, 40...)' with no mention of this being configurable.

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

**Description:** Find and Replace availability conflict between documents

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/UI_FEATURE_COMPARISON.md`

**Details:**
TK_UI_QUICK_START.md states 'Ctrl+H' is for 'Find and replace' and describes it as an available feature. UI_FEATURE_COMPARISON.md shows 'Find/Replace' as available in Tk (✅) but not in Web (❌). However, UI_FEATURE_COMPARISON.md also lists 'Find/Replace in Web UI' under 'Coming Soon' section, creating ambiguity.

---

### keyboard_shortcut_inconsistency

**Description:** Help keyboard shortcut differs between Tk and Curses UI documentation

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md does not list a help shortcut in the Essential Keyboard Shortcuts table, only mentions 'Press F1' in text. keyboard-shortcuts.md (Curses) lists '^F' for help and 'Ctrl+H' is listed under Curses help in UI_FEATURE_COMPARISON.md. This inconsistency in help shortcuts across UIs is not clearly documented.

---

### keyboard_shortcut_inconsistency

**Description:** Step execution shortcuts differ between Tk and Curses

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md shows 'Ctrl+T' as 'Step through code (next statement)' and 'Ctrl+L' as 'Step through code (next line)'. keyboard-shortcuts.md (Curses) shows 'Ctrl+K' as 'Step Line' and 'Ctrl+T' as 'Step Statement'. The Tk UI uses Ctrl+L for line stepping while Curses uses Ctrl+K, which is not clearly documented as a UI difference.

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

### inconsistent_path

**Description:** Index references language/index.md but a language.md file also exists at the same level

**Affected files:**
- `help/common/index.md`
- `help/common/language.md`

**Details:**
help/common/index.md references '[BASIC Language Reference](language/index.md)' but there is also a help/common/language.md file. This could cause confusion about which is the canonical language reference entry point.

---

### missing_reference

**Description:** Index references examples.md which exists but examples.md references back to index.md creating a circular reference

**Affected files:**
- `help/common/index.md`
- `help/common/examples.md`

**Details:**
help/common/index.md links to '[Examples](examples.md)' and help/common/examples.md links back with '[Back to main help](index.md)'. While not technically an error, the examples.md file is very minimal and doesn't link to the more detailed example files in the examples/ subdirectory.

---

### missing_reference

**Description:** Getting started references UI-specific editing documentation that is not provided

**Affected files:**
- `help/common/getting-started.md`

**Details:**
help/common/getting-started.md references '[Curses UI](../ui/curses/editing.md)', '[Tkinter UI](../ui/tk/index.md)', and '[CLI](../ui/cli/index.md)' but none of these files are provided in the documentation set.

---

### inconsistent_terminology

**Description:** Inconsistent naming of BASIC variant

**Affected files:**
- `help/common/language/appendices/math-functions.md`
- `help/common/language/data-types.md`

**Details:**
math-functions.md refers to 'MBASIC 5.21' and 'BASIC-80' interchangeably. The title says 'Mathematical Functions' with description 'Quick reference for all mathematical functions in BASIC-80', but the content says 'MBASIC 5.21 provides the following built-in mathematical functions'. data-types.md consistently uses 'BASIC-80'.

---

### missing_reference

**Description:** CVS function missing from alphabetical quick reference

**Affected files:**
- `help/common/language/functions/index.md`
- `help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
The alphabetical quick reference in index.md lists 'CVD/CVI/CVS' together, but the actual file is named 'cvi-cvs-cvd.md' with title 'CVI, CVS, CVD'. The order is inconsistent (CVD/CVI/CVS vs CVI/CVS/CVD).

---

### inconsistent_information

**Description:** Inconsistent rounding behavior description for CINT

**Affected files:**
- `help/common/language/data-types.md`
- `help/common/language/functions/cint.md`

**Details:**
data-types.md states 'CINT - Rounds to nearest integer' in the conversion functions table. cint.md states 'CINT rounds to the nearest integer (.5 rounds up)' which provides more specific detail about .5 rounding behavior, but both should be consistent in level of detail.

---

### inconsistent_information

**Description:** Inconsistent reference to appendix location

**Affected files:**
- `help/common/language/functions/asc.md`
- `help/common/language/functions/cvi-cvs-cvd.md`

**Details:**
asc.md states 'See Appendix M for ASCII codes' while character-set.md references 'appendices/ascii-codes.md'. The appendix naming/numbering is inconsistent (Appendix M vs appendices/ascii-codes.md).

---

### missing_reference

**Description:** LPOS 'See Also' section references 'LINE INPUT#' with tilde prefix instead of proper link

**Affected files:**
- `help/common/language/functions/lpos.md`

**Details:**
In lpos.md, the See Also section contains '~ INPUTi' instead of 'LINE INPUT#' like other files. Compare to loc.md, lof.md, pos.md which all properly reference 'LINE INPUT#' as '[LINE INPUT#](../statements/inputi.md)'

---

### inconsistent_terminology

**Description:** Inconsistent reference text for LINE INPUT# in See Also sections

**Affected files:**
- `help/common/language/functions/loc.md`
- `help/common/language/functions/lof.md`
- `help/common/language/functions/lpos.md`
- `help/common/language/functions/pos.md`

**Details:**
loc.md uses 'LINE INPUT#' with description 'To read an entire line (up to 254 characters), without delimiters, from a sequential disk data file to a string variable'. lpos.md uses '~ INPUTi' with same description. This should be consistent across all files.

---

### inconsistent_formatting

**Description:** Example output formatting inconsistency in SPC documentation

**Affected files:**
- `help/common/language/functions/spc.md`

**Details:**
In spc.md example output shows 'OVER ~ERE' with tilde character instead of proper spacing. Should likely be 'OVER               THERE' to demonstrate the 15 spaces from SPC(15).

---

### inconsistent_formatting

**Description:** Example output formatting has extra space in LEFT$ documentation

**Affected files:**
- `help/common/language/functions/left_dollar.md`

**Details:**
In left_dollar.md, the example shows '10 A$ = "BASIC-80"
 20 B$ = LEFT$(A$,5)
 30 PRINT B$
 BASIC' with inconsistent line number spacing (extra space before line 20 and 30).

---

### inconsistent_formatting

**Description:** Inconsistent line number spacing in examples

**Affected files:**
- `help/common/language/functions/len.md`
- `help/common/language/functions/right_dollar.md`

**Details:**
len.md shows '10 X$ = "PORTLAND, OREGON"
 20 PRINT LEN (X$)' with extra space before line 20. right_dollar.md shows '10 A$="DISK BASIC-80"
 20 PRINT RIGHT$(A$,8)' with extra space before line 20. This is inconsistent with other examples.

---

### missing_information

**Description:** LEFT$ missing 'Versions' field present in other function docs

**Affected files:**
- `help/common/language/functions/left_dollar.md`

**Details:**
Most function documentation files include a 'Versions:' field (e.g., len.md has '**Versions:** 8K, Extended, Disk'), but left_dollar.md does not include this information.

---

### missing_information

**Description:** MID$ and RIGHT$ missing 'Versions' field present in other function docs

**Affected files:**
- `help/common/language/functions/mid_dollar.md`
- `help/common/language/functions/right_dollar.md`

**Details:**
Functions like LEN, RND, SGN, SIN, SQR, TAN include '**Versions:** 8K, Extended, Disk' or similar, but mid_dollar.md and right_dollar.md do not include version information.

---

### inconsistent_formatting

**Description:** MKI$/MKS$/MKD$ documentation has malformed example section

**Affected files:**
- `help/common/language/functions/mki_dollar-mks_dollar-mkd_dollar.md`

**Details:**
The example section in mki_dollar-mks_dollar-mkd_dollar.md contains unrelated content: 'See also CVI, CVS, CVD, Section 3.9 and Appendix B.
3.27 OCT$
PRINT OCT$ (24)
30
Ok
See the HEX $ function for hexadecimal conversion.
3.2S PEEK
A=PEEK (&H5AOO)'. This appears to be OCR or copy-paste errors from the original manual.

---

### inconsistent_formatting

**Description:** TAN documentation has typo in description

**Affected files:**
- `help/common/language/functions/tan.md`

**Details:**
tan.md contains 'TAN (X) is calculated in single preclslon' - 'preclslon' should be 'precision'.

---

### version_inconsistency

**Description:** Inconsistent version notation format

**Affected files:**
- `help/common/language/statements/auto.md`
- `help/common/language/statements/clear.md`
- `help/common/language/statements/end.md`

**Details:**
auto.md uses no version marker, clear.md uses '**Versions:** 8K, -Extended, Disk', and end.md uses '**Versions:** 8K, Extended, Disk' (note the dash before Extended in clear.md)

---

### cross_reference_inconsistency

**Description:** Circular or incomplete cross-references between DEF FN and DEF USR

**Affected files:**
- `help/common/language/statements/def-fn.md`
- `help/common/language/statements/def-usr.md`

**Details:**
def-fn.md 'See Also' references def-usr.md, and def-usr.md 'See Also' references def-fn.md, but def-usr.md also references CALL and POKE which are not reciprocally referenced

---

### terminology_inconsistency

**Description:** Inconsistent capitalization of 'command level'

**Affected files:**
- `help/common/language/statements/chain.md`
- `help/common/language/statements/clear.md`
- `help/common/language/statements/common.md`
- `help/common/language/statements/cont.md`
- `help/common/language/statements/end.md`

**Details:**
Most files use lowercase 'command level', but some instances may vary. For example, auto.md uses 'command level' while others use 'COmmand level' (with unusual capitalization in cont.md)

---

### formatting_inconsistency

**Description:** Inconsistent example formatting

**Affected files:**
- `help/common/language/statements/auto.md`
- `help/common/language/statements/delete.md`

**Details:**
auto.md uses inline comments in examples ('AUTO 100,50      Generates line numbers 100,'), while delete.md uses separate description lines ('DELETE 40         Deletes line 40')

---

### content_accuracy

**Description:** Unclear or potentially incorrect remarks about CLEAR parameters

**Affected files:**
- `help/common/language/statements/clear.md`

**Details:**
clear.md states 'In previous versions of BASIC-SO, <expressionl> set the amount of string space,' but then says 'BASIC-80, release 5.0 and later, allocates string space dynamically.' The syntax shows [<expressionl>] but the description is confusing about what it actually does in version 5.21.

---

### see_also_inconsistency

**Description:** Inconsistent 'See Also' sections across related program control statements

**Affected files:**
- `help/common/language/statements/chain.md`
- `help/common/language/statements/clear.md`
- `help/common/language/statements/common.md`
- `help/common/language/statements/cont.md`
- `help/common/language/statements/end.md`

**Details:**
These five files all have nearly identical 'See Also' sections listing the same 7-8 statements, but the order and exact wording varies slightly. For consistency, they should be standardized.

---

### metadata_inconsistency

**Description:** Missing metadata fields compared to other statement files

**Affected files:**
- `help/common/language/statements/cls.md`

**Details:**
cls.md lacks the 'category' and 'keywords' frontmatter fields that are present in most other statement documentation files

---

### cross-reference-inconsistency

**Description:** File I/O related statements have nearly identical 'See Also' sections that include many unrelated functions

**Affected files:**
- `help/common/language/statements/field.md`
- `help/common/language/statements/files.md`
- `help/common/language/statements/get.md`
- `help/common/language/statements/inputi.md`

**Details:**
All four files list the same extensive 'See Also' section including: CLOSE, EOF, FIELD, FILES, GET, INPUT$, LOC, LOF, LPOS, LSET, OPEN, POS, PRINTi, PUT, RESET, RSET, WRITE#, INPUTi. While some overlap is expected, including LPOS (line printer position) in file I/O documentation seems inconsistent.

---

### metadata-inconsistency

**Description:** Control flow statements have inconsistent metadata fields - some have 'related' field, others don't

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/gosub-return.md`
- `help/common/language/statements/goto.md`
- `help/common/language/statements/if-then-else-if-goto.md`

**Details:**
for-next.md has 'related: ['while-wend', 'goto', 'gosub-return']', gosub-return.md has 'related: ['goto', 'on-gosub', 'for-next']', goto.md has 'related: ['gosub-return', 'if-then-else-if-goto', 'on-goto', 'on-gosub']', but if-then-else-if-goto.md has 'related: ['while-wend', 'for-next', 'goto', 'on-goto']'. The presence and content of the 'related' field is inconsistent across similar statement types.

---

### formatting-inconsistency

**Description:** Title formatting inconsistency with bullet characters

**Affected files:**
- `help/common/language/statements/for-next.md`
- `help/common/language/statements/gosub-return.md`
- `help/common/language/statements/if-then-else-if-goto.md`

**Details:**
for-next.md uses 'FOR ••• NEXT', gosub-return.md uses 'GOSUB •.. RETURN' (two dots), and if-then-else-if-goto.md uses 'IF ••• THEN[ ••• ELSE]' (three dots). The number of dots in the ellipsis is inconsistent.

---

### cross-reference-inconsistency

**Description:** FILES statement 'See Also' section includes file I/O functions that are not directly related to directory listing

**Affected files:**
- `help/common/language/statements/files.md`

**Details:**
files.md includes in 'See Also': FIELD, GET, PUT, LSET, RSET, LOC, LOF, LPOS, INPUT$, POS, PRINTi, WRITE#, INPUTi. Most of these are for random/sequential file operations, not directory operations. Only KILL, NAME, OPEN, and CLOSE are truly related to file management.

---

### version-information-inconsistency

**Description:** Modern extension statements marked as 'MBASIC Extension' but no version information provided for other statements

**Affected files:**
- `help/common/language/statements/helpsetting.md`
- `help/common/language/statements/limits.md`

**Details:**
helpsetting.md and limits.md are marked with '**Versions:** MBASIC Extension' and noted as 'This is a modern extension not present in original MBASIC 5.21', but other files use version markers like '**Versions:** 8K, Extended, Disk' or '**Versions:** Disk' without clarifying what these versions mean or their relationship to MBASIC 5.21.

---

### contradictory_information

**Description:** OPTION BASE documentation incomplete

**Affected files:**
- `help/common/language/statements/option-base.md`

**Details:**
The option-base.md file has empty 'Purpose' and 'Remarks' sections, providing no actual documentation content despite having a complete frontmatter and structure. This is inconsistent with all other documentation files which provide complete information.

---

### inconsistent_terminology

**Description:** PRINT USING documentation duplicated and inconsistent

**Affected files:**
- `help/common/language/statements/lprint-lprint-using.md`
- `help/common/language/statements/print.md`

**Details:**
Both lprint-lprint-using.md and print.md contain extensive PRINT USING formatting documentation. The print.md file shows 'PRINT USING <string   exp>~<list   of expressions>' while lprint-lprint-using.md shows 'LPRINT USING <string exp>i<list of expressions>'. The formatting character documentation appears to be duplicated between files with potential inconsistencies in the special characters used (~ vs i).

---

### inconsistent_terminology

**Description:** RENUM example shows duplicate line numbers

**Affected files:**
- `help/common/language/statements/renum.md`

**Details:**
In renum.md Example 6, after renumbering with 'RENUM 1000,100,100', the output shows '1100 END' appearing twice (once at line 1100 and once at line 1200), which appears to be a documentation error in the example output.

---

### missing_cross_reference

**Description:** RESET and RESTORE have similar names but completely different purposes, yet neither document cross-references the other to clarify the distinction

**Affected files:**
- `help/common/language/statements/reset.md`
- `help/common/language/statements/restore.md`

**Details:**
RESET closes files ('To close all open disk files'), while RESTORE resets DATA pointers ('To reset the DATA pointer'). Users might confuse these commands, but there's no 'See Also' cross-reference between them to prevent confusion.

---

### irrelevant_see_also_references

**Description:** File I/O statements include 'See Also' references to unrelated functions

**Affected files:**
- `help/common/language/statements/reset.md`
- `help/common/language/statements/rset.md`
- `help/common/language/statements/writei.md`

**Details:**
RESET, RSET, and WRITE# all reference 'LPOS' (line printer position) and 'POS' (cursor position) in their 'See Also' sections, which are not relevant to disk file operations.

---

### missing_cross_reference

**Description:** RESUME and RESTORE have similar names but different purposes, with no cross-reference to clarify

**Affected files:**
- `help/common/language/statements/resume.md`
- `help/common/language/statements/restore.md`

**Details:**
RESUME continues after error handling ('Continue program execution after error recovery'), while RESTORE resets DATA pointers. No cross-reference exists between them despite potential for user confusion.

---

### inconsistent_formatting

**Description:** SAVE statement has malformed syntax and example sections with unusual formatting

**Affected files:**
- `help/common/language/statements/save.md`

**Details:**
Syntax shows 'SAVE <filename> [,A   I ,P]' with odd spacing. Example shows 'SAVE nCOM2 n ,A' and 'SAVEnpRoo n , P' which appear to be OCR errors or formatting issues. Also references 'Appendix B' which doesn't exist in the provided files.

---

### missing_cross_reference

**Description:** Shortcuts documentation doesn't reference settings despite Ctrl+, shortcut

**Affected files:**
- `help/common/shortcuts.md`
- `help/common/settings.md`

**Details:**
shortcuts.md mentions '^,' (Ctrl+,) opens settings widget in Curses UI, but doesn't link to settings.md for more information. settings.md mentions this shortcut but shortcuts.md doesn't link back.

---

### inconsistent_formatting

**Description:** Implementation notes have different formatting styles

**Affected files:**
- `help/common/language/statements/wait.md`
- `help/common/language/statements/width.md`

**Details:**
wait.md uses '⚠️ **Not Implemented**' with detailed explanation. width.md uses '⚠️ **Emulated as No-Op**' with different structure. Both serve similar purposes but use inconsistent formatting and terminology.

---

### path_inconsistency

**Description:** Inconsistent path depth in See Also links

**Affected files:**
- `help/common/ui/curses/editing.md`

**Details:**
In help/common/ui/curses/editing.md, some links use '../../../ui/curses/running.md' (3 levels up) while others use '../../language/statements/auto.md' (2 levels up). Given the file is at help/common/ui/curses/editing.md, the correct depth to reach help/ui/curses/ should be '../../../ui/curses/' but to reach help/common/language/ should be '../../language/'. The running.md link appears to be trying to reach help/ui/curses/running.md instead of help/common/ui/curses/running.md.

---

### inconsistent_terminology

**Description:** Inconsistent naming of the implementation

**Affected files:**
- `help/mbasic/extensions.md`
- `help/mbasic/compatibility.md`

**Details:**
In extensions.md, the implementation is called 'MBASIC-2025' with a note about 'Project Names Under Consideration' including alternatives. However, in compatibility.md, it's referred to as 'MBASIC-2025' in one place and 'This implementation' or 'This MBASIC' in others, without mentioning the naming consideration.

---

### inconsistent_terminology

**Description:** Inconsistent capitalization of 'Ok' prompt

**Affected files:**
- `help/common/ui/cli/index.md`
- `help/common/ui/tk/index.md`

**Details:**
In help/common/ui/cli/index.md, the prompt is consistently shown as 'Ok' with capital O and lowercase k. However, this is a minor style point that should be verified for consistency across all documentation.

---

### inconsistent_feature_claims

**Description:** Features.md claims STEP INTO/OVER support, but debugging.md says they are not yet implemented

**Affected files:**
- `help/mbasic/features.md`
- `help/ui/cli/debugging.md`

**Details:**
help/mbasic/features.md lists 'STEP execution - Execute one line at a time (UI-dependent)' without caveats, but help/ui/cli/debugging.md explicitly states under Limitations: 'STEP INTO/OVER not yet implemented (use STEP)'

---

### missing_cross_reference

**Description:** Features.md does not mention settings system despite it being a significant feature

**Affected files:**
- `help/mbasic/features.md`
- `help/ui/cli/settings.md`

**Details:**
help/mbasic/features.md has comprehensive feature lists including 'Program Control' and 'User Interface Features' sections, but does not mention the settings system (SHOWSETTINGS/SETSETTING) documented in help/ui/cli/settings.md

---

### inconsistent_ui_listing

**Description:** Different UI lists mentioned across documents

**Affected files:**
- `help/mbasic/getting-started.md`
- `help/ui/cli/variables.md`

**Details:**
help/mbasic/getting-started.md lists three UIs: 'CLI, Curses, or Tkinter', while help/ui/cli/variables.md mentions four: 'Curses UI, Tk UI, Web UI' plus CLI. The 'Web UI' is not mentioned in getting-started.md

---

### path_inconsistency

**Description:** Placeholder references use 'docs/help/' prefix while actual files use 'help/' prefix

**Affected files:**
- `help/ui/common/errors.md`

**Details:**
help/ui/common/errors.md references paths like 'docs/help/common/language/statements/on-error-goto.md' but the actual file structure shown in other documents uses 'help/common/language/statements/' without the 'docs/' prefix

---

### feature_availability_conflict

**Description:** Cut/Copy/Paste availability unclear

**Affected files:**
- `help/ui/curses/quick-reference.md`
- `help/ui/curses/feature-reference.md`

**Details:**
help/ui/curses/feature-reference.md lists 'Cut/Copy/Paste' as an Editor Feature with 'Standard clipboard operations using system clipboard: Cut: Ctrl+X, Copy: Ctrl+C, Paste: Ctrl+V'. However, help/ui/curses/quick-reference.md doesn't mention these shortcuts at all, and Ctrl+X is listed as Stop/Interrupt in the Debugger section.

---

### keyboard_shortcut_conflict

**Description:** Help keyboard shortcut inconsistency

**Affected files:**
- `help/ui/curses/getting-started.md`
- `help/ui/curses/quick-reference.md`

**Details:**
help/ui/curses/getting-started.md lists '**Ctrl+P** - Help' but help/ui/curses/quick-reference.md shows '{{kbd:help}}' as a placeholder without specifying the actual key binding.

---

### terminology_inconsistency

**Description:** Inconsistent naming for Load operation

**Affected files:**
- `help/ui/curses/feature-reference.md`
- `help/ui/curses/quick-reference.md`

**Details:**
help/ui/curses/feature-reference.md uses 'Open/Load File (Ctrl+O)' while help/ui/curses/quick-reference.md uses 'Open/Load program' for what appears to be the same operation.

---

### missing_reference

**Description:** Settings documentation not linked from index

**Affected files:**
- `help/ui/curses/settings.md`
- `help/ui/curses/index.md`

**Details:**
help/ui/curses/settings.md provides comprehensive documentation about the Settings Widget (Ctrl+,) but this document is not referenced in help/ui/curses/index.md's list of Curses UI Guide topics.

---

### placeholder_inconsistency

**Description:** Inconsistent use of placeholder syntax

**Affected files:**
- `help/ui/curses/quick-reference.md`
- `help/ui/curses/help-navigation.md`

**Details:**
help/ui/curses/quick-reference.md uses '{{kbd:quit}}', '{{kbd:help}}', '{{kbd:run}}' etc. as placeholders, while help/ui/curses/help-navigation.md also uses the same placeholder format. However, other documents like feature-reference.md specify actual key bindings directly.

---

### terminology_inconsistency

**Description:** Inconsistent naming of the web interface

**Affected files:**
- `help/ui/web/getting-started.md`
- `help/ui/web/index.md`

**Details:**
getting-started.md consistently uses 'Web UI' in the title and text, while index.md uses 'Web IDE' in the title and throughout. Both terms are used interchangeably without clarification.

---

### feature_description_conflict

**Description:** File persistence description differs

**Affected files:**
- `help/ui/web/features.md`
- `help/ui/web/index.md`

**Details:**
features.md states files are saved 'to browser storage' with 'Session Recovery' implying persistence across sessions. However, index.md states 'Files stored in memory, persist during session only' which suggests files don't persist across browser sessions.

---

### inconsistent_terminology

**Description:** Inconsistent naming of UI areas

**Affected files:**
- `help/ui/web/settings.md`
- `help/ui/web/web-interface.md`

**Details:**
web-interface.md refers to 'Program Editor (Top)', 'Output (Middle)', and 'Command (Bottom)'. settings.md refers to 'editor' without the 'Program Editor' designation, which could cause confusion about which component is being discussed.

---

### missing_reference

**Description:** Settings dialog references features not documented in web-interface.md

**Affected files:**
- `help/ui/web/settings.md`

**Details:**
settings.md mentions 'Limits Tab' showing 'Maximum variables, Maximum string length, Maximum array dimensions' but web-interface.md does not document these limits or where users can find this information.

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

### command_reference_inconsistency

**Description:** Settings command syntax presentation differs

**Affected files:**
- `user/SETTINGS_AND_CONFIGURATION.md`
- `user/TK_UI_QUICK_START.md`

**Details:**
SETTINGS_AND_CONFIGURATION.md shows 'SHOW SETTINGS' as a command to view settings. TK_UI_QUICK_START.md mentions 'SHOW SETTINGS "case"' in the Variable Case Preservation section but doesn't include SHOW SETTINGS in any command reference or shortcut table, potentially confusing users about how to access settings in the Tk UI.

---

### feature_description_inconsistency

**Description:** Execution Stack window shortcut inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md lists 'Ctrl+K' as 'Show/hide Execution Stack window' in the Essential Keyboard Shortcuts table. However, keyboard-shortcuts.md (Curses UI) shows 'Ctrl+K' as 'Step Line - execute all statements on current line' in the Debugger section, and lists Execution Stack toggle as 'Menu only'. This creates confusion about what Ctrl+K does in different UIs.

---

### terminology_inconsistency

**Description:** Variables window naming inconsistency

**Affected files:**
- `user/TK_UI_QUICK_START.md`
- `user/keyboard-shortcuts.md`

**Details:**
TK_UI_QUICK_START.md uses 'Variables window', 'Variables & Resources window', and 'Variables Window' interchangeably. keyboard-shortcuts.md uses 'variables watch window'. SETTINGS_AND_CONFIGURATION.md uses 'Variable window' and 'Variables & Resources window'. The inconsistent naming and capitalization makes it unclear if these refer to the same feature or different features.

---

