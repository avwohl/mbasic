# Persistent Issues Analysis

Analyzed 3424 issues from consistency reports versions: [7, 8, 9, 10, 11, 14, 21, 22]
Identified 334 unique recurring issues

## Top 10 Most Persistent Issues

These issues appear across multiple versions and should be prioritized for fixing:

### 1. Contradictory information about Web UI debugger capabilities

**Persistence Score:** 90.00%
**Appears in versions:** [10, 21, 22]
**Total occurrences:** 5
**Files involved:** docs/help/ui/curses/variables.md, docs/help/ui/index.md, docs/help/ui/tk/feature-reference.md, docs/help/ui/web/debugging.md
**Keywords:** DEBUGGING, FEATURE-REFERENCE, FOR, INDEX, RENUM, RENUMBER, STEP, VARIABLES
**Severity distribution:** High=5, Medium=0, Low=0

**Example details:** docs/help/ui/index.md comparison table states Web debugger is 'Limited' with note 'Web: breakpoints, step, basic variable inspection (planned: advanced panels, watch expressions)'. However, docs/help/...

**Signature:** `docs/help/ui/curses/variables.md + docs/help/ui/index.md + docs/help/ui/tk/feature-reference.md + DEBUGGING + FEATURE-REFERENCE + FOR + INDEX + RENUM`

---

### 2. Contradictory information about FileIO integration status and filesystem abstraction architecture

**Persistence Score:** 86.67%
**Appears in versions:** [21, 22]
**Total occurrences:** 3
**Files involved:** src/codegen_backend.py, src/editing/manager.py
**Keywords:** ABSTRACTION, CODEGEN BACKEND, DOCSTRING, FILEIO, FILESYSTEM, FILE_IO, FOR, INTEGRATION
**Severity distribution:** High=2, Medium=1, Low=0

**Example details:** codegen_backend.py states: "See src/file_io.py for planned filesystem abstraction that would support configurable compiler locations and cross-platform paths."  However, manager.py provides extensive ...

**Signature:** `src/codegen_backend.py + src/editing/manager.py + ABSTRACTION + CODEGEN BACKEND + DOCSTRING + FILEIO + FILESYSTEM`

---

### 3. Inconsistent documentation about accessing Execution Stack

**Persistence Score:** 86.00%
**Appears in versions:** [14, 21, 22]
**Total occurrences:** 10
**Files involved:** docs/help/ui/curses/feature-reference.md, docs/help/ui/curses/find-replace.md, docs/help/ui/curses/quick-reference.md
**Keywords:** FEATURE-REFERENCE, FIND-REPLACE, FOR, IMMEDIATE, LINE, MODE, QUICK-REFERENCE, RENUM
**Severity distribution:** High=6, Medium=4, Low=0

**Example details:** quick-reference.md states: "| **Menu only** (Ctrl+U → Debug) | Toggle execution stack window |"  feature-reference.md states: "### Execution Stack View the call stack showing:  **Access methods:** - V...

**Signature:** `docs/help/ui/curses/feature-reference.md + docs/help/ui/curses/find-replace.md + docs/help/ui/curses/quick-reference.md + FEATURE-REFERENCE + FIND-REPLACE + FOR + IMMEDIATE + LINE`

---

### 4. Help URL inconsistency - code uses http://localhost/mbasic_docs but documentation mentions both this and deprecated http://localhost:8000

**Persistence Score:** 85.71%
**Appears in versions:** [7, 8, 9, 10, 14, 21, 22]
**Total occurrences:** 7
**Files involved:** docs/help/README.md, docs/help/common/index.md, src/ui/web_help_launcher.py
**Keywords:** COMMENT, FOR, INDEX, LINE, PRINT, README, STATEMENT, WEB HELP LAUNCHER
**Severity distribution:** High=4, Medium=3, Low=0

**Example details:** web_help_launcher.py line 17: HELP_BASE_URL = "http://localhost/mbasic_docs"  README.md mentions: "Help content is built using MkDocs and served locally at `http://localhost/mbasic_docs` for the Tk an...

**Signature:** `docs/help/README.md + docs/help/common/index.md + src/ui/web_help_launcher.py + COMMENT + FOR + INDEX + LINE + PRINT`

---

### 5. FOR-NEXT loop termination test description is ambiguous and potentially contradictory

**Persistence Score:** 85.33%
**Appears in versions:** [7, 21, 22]
**Total occurrences:** 3
**Files involved:** FOR I = 1 TO 10, FOR I = 10 TO 1 STEP -1, docs/help/common/language/statements/for-next.md
**Keywords:** FOR, FOR I = 1 TO 10, FOR I = 10 TO 1 STEP -1, FOR-NEXT, STATEMENT, STEP
**Severity distribution:** High=2, Medium=0, Low=1

**Example details:** The documentation states: "### Loop Termination: The termination test happens AFTER each increment/decrement at the NEXT statement: - **Positive STEP** (or no STEP): Loop continues while variable <= e...

**Signature:** `FOR I = 1 TO 10 + FOR I = 10 TO 1 STEP -1 + docs/help/common/language/statements/for-next.md + FOR + FOR I = 1 TO 10 + FOR I = 10 TO 1 STEP -1 + FOR-NEXT + STATEMENT`

---

### 6. Implementation status inconsistency for line printer features

**Persistence Score:** 84.00%
**Appears in versions:** [7, 9, 21, 22]
**Total occurrences:** 4
**Files involved:** docs/help/common/language/statements/llist.md, docs/help/common/language/statements/lprint-lprint-using.md
**Keywords:** FOR, LINE, LLIST, LPRINT-LPRINT-USING, PARSE, PRINT, STATEMENT
**Severity distribution:** High=2, Medium=1, Low=1

**Example details:** LLIST states: '⚠️ **Not Implemented**: This feature requires line printer hardware and is not implemented' LPRINT states: '⚠️ **Not Implemented**: This feature requires line printer hardware and is no...

**Signature:** `docs/help/common/language/statements/llist.md + docs/help/common/language/statements/lprint-lprint-using.md + FOR + LINE + LLIST + LPRINT-LPRINT-USING + PARSE`

---

### 7. Settings system implementation status contradicts feature status documentation

**Persistence Score:** 84.00%
**Appears in versions:** [8, 21, 22]
**Total occurrences:** 5
**Files involved:** docs/user/INSTALL.md, docs/user/SETTINGS_AND_CONFIGURATION.md
**Keywords:** FOR, INSTALL, MODE, SETTINGS AND CONFIGURATION
**Severity distribution:** High=2, Medium=3, Low=0

**Example details:** INSTALL.md states under 'Feature Status': '### What Works - ✓ Settings system (SET, SHOW SETTINGS commands with global/project configuration files)'  SETTINGS_AND_CONFIGURATION.md has conflicting stat...

**Signature:** `docs/user/INSTALL.md + docs/user/SETTINGS_AND_CONFIGURATION.md + FOR + INSTALL + MODE + SETTINGS AND CONFIGURATION`

---

### 8. Inconsistent implementation note formatting and detail level between WAIT and WIDTH

**Persistence Score:** 83.33%
**Appears in versions:** [14, 21, 22]
**Total occurrences:** 3
**Files involved:** docs/help/common/language/statements/wait.md, docs/help/common/language/statements/width.md
**Keywords:** ERROR, FOR, PARSE, PRINT, STATEMENT, WAIT, WIDTH
**Severity distribution:** High=1, Medium=2, Low=0

**Example details:** WAIT.md has brief note: '⚠️ **Not Implemented**: This statement is parsed for compatibility but performs no operation.'  WIDTH.md has detailed note with multiple sections: '⚠️ **Not Implemented**: Thi...

**Signature:** `docs/help/common/language/statements/wait.md + docs/help/common/language/statements/width.md + ERROR + FOR + PARSE + PRINT + STATEMENT`

---

### 9. Error code reference mismatch

**Persistence Score:** 83.20%
**Appears in versions:** [7, 14, 21, 22]
**Total occurrences:** 5
**Files involved:** docs/help/common/language/appendices/error-codes.md, docs/help/common/language/functions/cvi-cvs-cvd.md
**Keywords:** CVI-CVS-CVD, ERROR, ERROR-CODES, FOR
**Severity distribution:** High=2, Medium=2, Low=1

**Example details:** cvi-cvs-cvd.md states: 'Error: Raises "Illegal function call" (error code FC) if the string length is incorrect'. However, error-codes.md lists FC as error code 5, not as 'FC'. The documentation uses ...

**Signature:** `docs/help/common/language/appendices/error-codes.md + docs/help/common/language/functions/cvi-cvs-cvd.md + CVI-CVS-CVD + ERROR + ERROR-CODES + FOR`

---

### 10. Missing SHOWSETTINGS and SETSETTING from features list

**Persistence Score:** 83.00%
**Appears in versions:** [21, 22]
**Total occurrences:** 2
**Files involved:** docs/help/mbasic/features.md, docs/help/ui/cli/settings.md
**Keywords:** FEATURES, RENUM, SETTINGS
**Severity distribution:** High=1, Medium=0, Low=1

**Example details:** features.md lists 'Direct Commands' including RUN, LIST, NEW, SAVE, LOAD, DELETE, RENUM, AUTO, BREAK, but does not mention SHOWSETTINGS or SETSETTING which are documented in cli/settings.md as availab...

**Signature:** `docs/help/mbasic/features.md + docs/help/ui/cli/settings.md + FEATURES + RENUM + SETTINGS`

---

## Summary Statistics

- Issues still active in v21/v22: 210

### Most Affected Files

- `docs/help/mbasic/features.md`: appears in 12 issue clusters
- `docs/help/ui/curses/feature-reference.md`: appears in 11 issue clusters
- `docs/help/ui/curses/quick-reference.md`: appears in 10 issue clusters
- `docs/help/ui/tk/feature-reference.md`: appears in 7 issue clusters
- `docs/help/ui/curses/variables.md`: appears in 6 issue clusters
- `docs/help/ui/web/web-interface.md`: appears in 6 issue clusters
- `docs/help/ui/web/features.md`: appears in 6 issue clusters
- `docs/help/common/language/functions/index.md`: appears in 6 issue clusters
- `docs/user/SETTINGS_AND_CONFIGURATION.md`: appears in 5 issue clusters
- `docs/help/mbasic/compatibility.md`: appears in 5 issue clusters

### Most Common Keywords

- **FOR**: 291 clusters
- **LINE**: 152 clusters
- **STATEMENT**: 148 clusters
- **PRINT**: 78 clusters
- **ERROR**: 72 clusters
- **COMMENT**: 71 clusters
- **MODE**: 64 clusters
- **DOCSTRING**: 63 clusters
- **INPUT**: 53 clusters
- **INDEX**: 46 clusters
- **STEP**: 46 clusters
- **PARSE**: 36 clusters
- **ERL**: 33 clusters
- **IMMEDIATE**: 29 clusters
- **RUNTIME**: 28 clusters

## Recommended Priority Order

Based on persistence analysis, fix issues in this order:

1. **docs/help/ui/curses/variables.md + docs/help/ui/index.md + docs/help/ui/tk/feature-reference.md + DEBUGGING + FEATURE-REFERENCE + FOR + INDEX + RENUM** (Score: 90.0%)
2. **src/codegen_backend.py + src/editing/manager.py + ABSTRACTION + CODEGEN BACKEND + DOCSTRING + FILEIO + FILESYSTEM** (Score: 86.7%)
3. **docs/help/ui/curses/feature-reference.md + docs/help/ui/curses/find-replace.md + docs/help/ui/curses/quick-reference.md + FEATURE-REFERENCE + FIND-REPLACE + FOR + IMMEDIATE + LINE** (Score: 86.0%)
4. **docs/help/README.md + docs/help/common/index.md + src/ui/web_help_launcher.py + COMMENT + FOR + INDEX + LINE + PRINT** (Score: 85.7%)
5. **FOR I = 1 TO 10 + FOR I = 10 TO 1 STEP -1 + docs/help/common/language/statements/for-next.md + FOR + FOR I = 1 TO 10 + FOR I = 10 TO 1 STEP -1 + FOR-NEXT + STATEMENT** (Score: 85.3%)
6. **docs/help/common/language/statements/llist.md + docs/help/common/language/statements/lprint-lprint-using.md + FOR + LINE + LLIST + LPRINT-LPRINT-USING + PARSE** (Score: 84.0%)
7. **docs/user/INSTALL.md + docs/user/SETTINGS_AND_CONFIGURATION.md + FOR + INSTALL + MODE + SETTINGS AND CONFIGURATION** (Score: 84.0%)
8. **docs/help/common/language/statements/wait.md + docs/help/common/language/statements/width.md + ERROR + FOR + PARSE + PRINT + STATEMENT** (Score: 83.3%)
9. **docs/help/common/language/appendices/error-codes.md + docs/help/common/language/functions/cvi-cvs-cvd.md + CVI-CVS-CVD + ERROR + ERROR-CODES + FOR** (Score: 83.2%)
10. **docs/help/mbasic/features.md + docs/help/ui/cli/settings.md + FEATURES + RENUM + SETTINGS** (Score: 83.0%)
11. **docs/help/mbasic/compatibility.md + docs/help/mbasic/extensions.md + COMPATIBILITY + EXTENSIONS + FILESYSTEM + FOR + LINE** (Score: 82.9%)
12. **src/ui/cli_debug.py + src/ui/curses_keybindings.json + CLI DEBUG + CURSES KEYBINDINGS + DOCSTRING + FOR + LINE** (Score: 82.7%)
13. **docs/help/mbasic/architecture.md + docs/help/mbasic/compatibility.md + ARCHITECTURE + COMPATIBILITY + FOR + LINE + PARSE** (Score: 82.2%)
14. **docs/help/ui/cli/variables.md + docs/help/ui/curses/feature-reference.md + docs/help/ui/curses/variables.md + FEATURE-REFERENCE + FOR + IMMEDIATE + MODE + VARIABLES** (Score: 82.0%)
15. **src/file_io.py + src/filesystem/sandboxed_fs.py + ABSTRACTION + COMMENT + DOCSTRING + ERROR + FILE IO** (Score: 81.7%)
16. **docs/help/ui/tk/feature-reference.md + docs/help/ui/tk/features.md + docs/help/ui/tk/workflows.md + FEATURE-REFERENCE + FEATURES + FOR + PRINT + STATEMENT** (Score: 81.6%)
17. **docs/help/common/ui/cli/index.md + docs/help/mbasic/compatibility.md + docs/help/mbasic/extensions.md + COMPATIBILITY + EXTENSIONS + FEATURES + FOR + INDEX** (Score: 81.4%)
18. **docs/help/ui/web/features.md + docs/help/ui/web/web-interface.md + FEATURES + FILESYSTEM + FOR + INPUT + SANDBOX** (Score: 81.1%)
19. **src/ui/help_widget.py + src/ui/keybindings.py + COMMENT + DOCSTRING + FILESYSTEM + FOR + HELP WIDGET** (Score: 81.0%)
20. **docs/help/common/debugging.md + docs/help/common/editor-commands.md + src/ui/web/web_settings_dialog.py + DEBUGGING + EDITOR-COMMANDS + FOR + INPUT + LINE** (Score: 80.9%)
