# Documentation Fixes - Inconsistencies Report v12

**Generated from:** docs_inconsistencies_report-v12.md
**Date:** 2025-11-07
**Total Issues:** 415

These are issues where the **DOCUMENTATION should be updated** (not the code).
The code behavior is generally correct, but comments, docstrings, or documentation files are wrong/outdated/misleading.

---

## High Severity Documentation Fixes (27 issues)

### 1. ProgramManager.load_from_file() return value
**Files:** `src/editing/manager.py`, `src/file_io.py`
**Issue:** Documentation emphasizes distinction unnecessarily; both return same tuple format
**Fix:** Clarify docstring - no distinction needed

### 2. CONT command clear_execution_state() timing
**Files:** `src/interactive.py`
**Issue:** Docstring says editing clears execution state, but code only clears in cmd_new() and cmd_renum(), not on line edits
**Fix:** Update docstring to accurately reflect when clear_execution_state() is called

### 3. DELETE command return value
**Files:** `src/interactive.py`
**Issue:** Docstring says returns deleted line numbers but cmd_delete ignores it; comment is documenting unused functionality
**Fix:** Update docstring to remove mention of unused return value

### 4. STEP command infrastructure
**Files:** `src/interpreter.py`
**Issue:** Docstring claims tick_pc() has step infrastructure but execute_step() is a no-op; misleading documentation
**Fix:** Update docstring to reflect actual step implementation status

### 5. Status bar update comments
**Files:** `src/ui/curses_ui.py`
**Issue:** Multiple comments say "No status bar update" but code shows status_bar.set_text() calls
**Fix:** Remove or correct misleading comments

### 6. cmd_delete/cmd_renum runtime sync
**Files:** `src/ui/curses_ui.py`
**Issue:** Comments claim sync occurs automatically but timing analysis shows it happens before command, not after
**Fix:** Clarify comment about sync timing

### 7. Help navigation keys loading
**Files:** `src/ui/help_widget.py`
**Issue:** Comment about keybindings loading is accurate, not a conflict
**Fix:** No fix needed (verified accurate)

### 8. QUIT_ALT_KEY loading
**Files:** `src/ui/keybindings.py`
**Issue:** Loads from 'editor.continue' JSON key which is semantically wrong
**Fix:** Document the semantic mismatch or use correct JSON key

### 9. Variables window sort default
**Files:** `src/ui/tk_ui.py`
**Issue:** Comment about default sort implementation but actual sort function not visible
**Fix:** Clarify comment or verify implementation

### 10. TkIOHandler.input() docstring
**Files:** `src/ui/tk_ui.py`
**Issue:** Contradictory about comma-separated values handling
**Fix:** Clarify docstring

### 11. serialize_statement() error handling
**Files:** `src/ui/ui_helpers.py`
**Issue:** Comment describes prevention strategy but implementation differs
**Fix:** Update comment to match implementation

### 12. Breakpoint type documentation
**Files:** `src/ui/web/nicegui_backend.py`
**Issue:** Comments suggest PC-only but implementation handles both
**Fix:** Update comments to reflect both PC and line breakpoints

### 13. RUN clears variables but preserves breakpoints
**Files:** `src/ui/web/nicegui_backend.py`
**Issue:** Comment makes assertions about reset_for_run() behavior not verified in file
**Fix:** Verify and update comment

### 14. start()/stop() method docstrings
**Files:** `src/ui/web/nicegui_backend.py`
**Issue:** Docstrings identical but implementations differ
**Fix:** Update docstrings to reflect actual differences

### 15. Redis session storage
**Files:** `test_redis_settings.py`, `docs/help/`
**Issue:** Feature implemented and tested but not documented for users
**Fix:** Add user documentation for Redis session storage

### 16. EXP function overflow limit
**Files:** `docs/help/common/language/data-types.md`, `docs/help/common/language/functions/exp.md`
**Issue:** Contradicts documented SINGLE/DOUBLE ranges
**Fix:** Reconcile documentation

### 17. Settings documentation as extension
**Files:** `docs/help/common/settings.md`
**Issue:** settings.md treats features as standard but other docs say "MBASIC Extension"
**Fix:** Consistent labeling across docs

### 18. PEEK/POKE implementation
**Files:** `docs/help/index.md`, `docs/help/mbasic/architecture.md`
**Issue:** Same info but index.md lacks context
**Fix:** Add context to index.md or cross-reference

### 19. File persistence in Web UI
**Files:** `docs/help/mbasic/compatibility.md`, `docs/help/mbasic/extensions.md`
**Issue:** Contradictory about auto-save to browser storage
**Fix:** Determine actual behavior and make docs consistent

### 20. STACK command availability
**Files:** `docs/help/ui/curses/feature-reference.md`, `docs/help/ui/cli/debugging.md`
**Issue:** Inconsistent about where STACK works
**Fix:** Verify and document correct availability

### 21. Find/Replace in Curses UI
**Files:** `docs/help/ui/curses/feature-reference.md`
**Issue:** Says "not yet implemented" and "available via menu"
**Fix:** Determine actual status and update

### 22. Save keyboard shortcut
**Files:** `docs/help/ui/curses/files.md`, `docs/help/ui/curses/quick-reference.md`
**Issue:** Minor wording differences
**Fix:** Make wording consistent

### 23. Command-line loading behavior
**Files:** `docs/help/ui/curses/files.md`, `docs/help/ui/curses/getting-started.md`
**Issue:** Contradictory about auto-run
**Fix:** Clarify actual behavior

### 24. Variable window search keys
**Files:** `docs/help/ui/curses/quick-reference.md`, `docs/help/ui/curses/variables.md`
**Issue:** n/N keys not in quick ref
**Fix:** Add to quick reference

### 25. Tk settings.md vs web/settings.md
**Files:** `docs/help/ui/tk/settings.md`, `docs/help/ui/web/settings.md`
**Issue:** Tk describes planned features, web/settings.md missing
**Fix:** Create web/settings.md or clarify Tk status

### 26. Variable Inspector implementation status
**Files:** `docs/help/ui/web/features.md`, `docs/help/ui/web/debugging.md`
**Issue:** Contradictory about what's implemented vs planned
**Fix:** Verify implementation status and update docs

### 27. UI integration requirements
**Files:** `src/immediate_executor.py`
**Issue:** Extensive comment block describes UI integration requirements that cannot be validated from provided code
**Fix:** Verify UI actually provides these methods and update comments

---

## Medium Severity Documentation Fixes (134 issues)

### 28. Version number mismatch
**Files:** `setup.py`, `src/ast_nodes.py`
**Fix:** Clarify relationship between setup.py version (0.99.0) and MBASIC version (5.21)

### 29. LineNode source_text field
**Files:** `src/ast_nodes.py`
**Fix:** Explain relationship to StatementNode offsets

### 30. VariableNode type_suffix vs explicit_type_suffix
**Files:** `src/ast_nodes.py`
**Fix:** Clarify field relationship in docstring

### 31. PrintStatementNode keyword_token inconsistency
**Files:** `src/ast_nodes.py`
**Fix:** Document why some statements have token fields and others don't

### 32. Comment line number reference
**Files:** `src/basic_builtins.py`
**Fix:** Line 272 comment references line 269 but is self-referential - fix reference

### 33. identifier_table infrastructure
**Files:** `src/case_string_handler.py`
**Fix:** Comment says not used but method is implemented - clarify

### 34. EOF() binary mode comment
**Files:** `src/basic_builtins.py`
**Fix:** Validate or document assumption that mode 'I' means binary

### 35. SandboxedFileIO stub status
**Files:** `src/file_io.py`
**Fix:** Make error messages consistent about "async/await refactor"

### 36. FileSystemProvider.list_files() return type
**Files:** `src/filesystem/base.py`, `src/filesystem/sandboxed_fs.py`
**Fix:** Document different return formats

### 37. ProgramManager file I/O methods
**Files:** `src/editing/manager.py`
**Fix:** Clarify why methods exist if Web UI doesn't use them

### 38. INPUT statement blocking
**Files:** `src/immediate_executor.py`
**Fix:** Remove redundant phrasing about runtime blocking

### 39. Microprocessor model terminology
**Files:** `src/immediate_executor.py`
**Fix:** Replace misleading term for boolean checks

### 40. EDIT command status
**Files:** `src/interactive.py`
**Fix:** Comment says not implemented but full implementation exists - remove comment

### 41. RENUM ERL handling
**Files:** `src/interactive.py`
**Fix:** Document if claims are broader than manual or match MBASIC 5.21

### 42. Ctrl+A readline binding
**Files:** `src/interactive.py`
**Fix:** Document assumptions about terminal behavior

### 43. MERGE runtime update timing
**Files:** `src/interactive.py`
**Fix:** Clarify when runtime update happens

### 44. CHAIN ChainException raising
**Files:** `src/interactive.py`
**Fix:** Clarify when exception is raised

### 45. GOTO/GOSUB immediate mode semantics
**Files:** `src/interactive.py`
**Fix:** Clarify behavior description

### 46. skip_next_breakpoint_check timing
**Files:** `src/interpreter.py`
**Fix:** Correct comment about timing

### 47. return_stmt validation explanation
**Files:** `src/interpreter.py`
**Fix:** Either complete validation or simplify explanation

### 48. execute_next docstring
**Files:** `src/interpreter.py`
**Fix:** Clarify distinction about separate statements

### 49. WEND loop popping
**Files:** `src/interpreter.py`
**Fix:** Clarify phrasing about sequence

### 50. RUN statement behavior
**Files:** `src/interpreter.py`
**Fix:** Clarify what halted=True means

### 51. STOP vs Break PC handling
**Files:** `src/interpreter.py`
**Fix:** Clarify phrasing about differences

### 52. evaluate_functioncall() restore
**Files:** `src/interpreter.py`
**Fix:** Document asymmetry in save/set/restore tracking

### 53. IOHandler.input_line() documentation
**Files:** `src/iohandler/base.py`
**Fix:** Resolve contradiction about space preservation

### 54. SimpleKeywordCase validation
**Files:** `src/lexer.py`
**Fix:** Document validation claims

### 55. Identifiers with periods
**Files:** `src/lexer.py`
**Fix:** Clarify if Extended BASIC mode is always enabled

### 56. RND/INKEY$ parentheses
**Files:** `src/parser.py`
**Fix:** Comment accurate but could be clearer

### 57. MID$ lookahead error handling
**Files:** `src/parser.py`
**Fix:** Document that bare except could hide bugs

### 58. MID$ token representation
**Files:** `src/parser.py`
**Fix:** Clarify lexer tokenization

### 59. SETSETTING docstring
**Files:** `src/parser.py`
**Fix:** Remove redundant comment about field name

### 60. DIM expression flexibility
**Files:** `src/parser.py`
**Fix:** Document if matches MBASIC 5.21 exactly

### 61. DEF FN lowercase 'fn' handling
**Files:** `src/parser.py`
**Fix:** Docstring should explain normalization

### 62. PC stmt_offset terminology
**Files:** `src/pc.py`
**Fix:** Rename field or add clear documentation about misleading name

### 63. emit_keyword normalization
**Files:** `src/position_serializer.py`
**Fix:** Clarify caller vs callee responsibility

### 64. serialize_let_statement terminology
**Files:** `src/position_serializer.py`
**Fix:** Move or remove historical name note

### 65. resource_limits vs resource_locator naming
**Files:** `src/resource_limits.py`, `src/resource_locator.py`
**Fix:** Add module docstrings to distinguish similar names

### 66. line=-1 variable marking
**Files:** `src/runtime.py`
**Fix:** Resolve contradiction about what line=-1 indicates

### 67. get_variable() token requirement
**Files:** `src/runtime.py`
**Fix:** Update docstring - says REQUIRED but allows missing attributes

### 68. from_line redundancy
**Files:** `src/runtime.py`
**Fix:** Clarify if truly identical or just redundant

### 69. load() method flattening
**Files:** `src/settings.py`
**Fix:** Comment contradicts actual format handling - update

### 70. Global settings path
**Files:** `src/settings.py`, `src/settings_backend.py`
**Fix:** Document Windows path consistently

### 71. RedisSettingsBackend initialization
**Files:** `src/settings_backend.py`
**Fix:** Claims initialization always happens but it's optional - clarify

### 72. BREAK command activation
**Files:** `src/ui/cli_debug.py`
**Fix:** Says only at RUN time but checks during execution - update

### 73. Footer shortcuts vs button widgets
**Files:** `src/ui/curses_settings_widget.py`
**Fix:** Clarify why buttons not used

### 74. UIBackend command methods
**Files:** `src/ui/base.py`, `src/ui/cli.py`
**Fix:** Document that methods are optional but CLI implements all

### 75. SettingsWidget signal handling
**Files:** `src/ui/curses_settings_widget.py`
**Fix:** Remove or implement actual signal emission mechanism

### 76. Line number format comment
**Files:** `src/ui/curses_ui.py`
**Fix:** Rephrase confusing variable width comment

### 77. _parse_line_number behavior
**Files:** `src/ui/curses_ui.py`
**Fix:** Improve example to illustrate behavior

### 78. Syntax error display timing
**Files:** `src/ui/curses_ui.py`
**Fix:** Complete docstring about when errors shown

### 79. FAST PATH comment
**Files:** `src/ui/curses_ui.py`
**Fix:** Correct misleading comment about expensive processing

### 80. Toolbar removal
**Files:** `src/ui/curses_ui.py`
**Fix:** Method fully implemented despite removal comment - update

### 81. IO handler lifecycle
**Files:** `src/ui/curses_ui.py`
**Fix:** Comment suggests both recreated but only one is - clarify

### 82. Breakpoint storage
**Files:** `src/ui/curses_ui.py`
**Fix:** Comment says NOT in runtime but code re-applies them - update

### 83. GOSUB statement precision
**Files:** `src/ui/curses_ui.py`
**Fix:** Default value comment misleading - clarify

### 84. _sync_program_to_runtime PC preservation
**Files:** `src/ui/curses_ui.py`
**Fix:** Comment incomplete about paused_at_breakpoint - expand

### 85. interpreter.start() calling
**Files:** `src/ui/curses_ui.py`
**Fix:** Document assumption about contract maintenance

### 86. CapturingIOHandler duplication
**Files:** `src/ui/curses_ui.py`
**Fix:** Should be extracted - add TODO or document why duplicated

### 87. Tier label mapping
**Files:** `src/ui/help_widget.py`
**Fix:** Comment accurate, actually consistent - no fix needed

### 88. HelpMacros keybindings
**Files:** `src/ui/help_macros.py`, `src/ui/help_widget.py`
**Fix:** Document generic vs specific implementation difference

### 89. Help navigation keys
**Files:** `src/ui/help_widget.py`
**Fix:** Complete maintenance instructions

### 90. Keybindings duplication
**Files:** `src/ui/help_macros.py`, `src/ui/keybinding_loader.py`
**Fix:** Document why nearly identical loading code exists

### 91. LIST_KEY naming
**Files:** `src/ui/keybindings.py`
**Fix:** Variable name doesn't match action - document or rename

### 92. Step Line vs Step Statement
**Files:** `src/ui/keybindings.py`
**Fix:** Use terminology consistently

### 93. STATUS_BAR_SHORTCUTS LIST_KEY
**Files:** `src/ui/keybindings.py`
**Fix:** Inconsistent with variable naming - document

### 94. ESC key binding documentation
**Files:** `src/ui/tk_help_browser.py`, `src/ui/tk_keybindings.json`
**Fix:** Document ESC key despite implementation

### 95. 3-pane layout weights
**Files:** `src/ui/tk_ui.py`
**Fix:** Percentages correct but could be clearer

### 96. INPUT row visibility
**Files:** `src/ui/tk_ui.py`
**Fix:** Clarify implementation via pack/pack_forget

### 97. _ImmediateModeToken description
**Files:** `src/ui/tk_ui.py`
**Fix:** Clarify if actually used

### 98. _on_variable_heading_click
**Files:** `src/ui/tk_ui.py`
**Fix:** Document cycling behavior not visible in code

### 99. OPTION BASE else clause
**Files:** `src/ui/tk_ui.py`
**Fix:** Comment says defensive but validation elsewhere - clarify

### 100. Final blank line preservation
**Files:** `src/ui/tk_ui.py`
**Fix:** Clarify comment about Tk behavior

### 101. Highlight clearing on keypress
**Files:** `src/ui/tk_ui.py`
**Fix:** Justification doesn't match behavior - update

### 102. Multi-line paste cases
**Files:** `src/ui/tk_ui.py`
**Fix:** Comment suggests two cases but code treats identically - clarify

### 103. Lines displayed exactly as stored
**Files:** `src/ui/tk_ui.py`
**Fix:** Contradicts modification logic - update

### 104. CONT runtime.stopped check
**Files:** `src/ui/tk_ui.py`
**Fix:** Critical validation not in docstring - add

### 105. immediate_history None
**Files:** `src/ui/tk_ui.py`
**Fix:** Contradictory about whether it exists - clarify

### 106. has_work() usage
**Files:** `src/ui/tk_ui.py`
**Fix:** Comment implies widespread use but only one location - update

### 107. execute() echoing
**Files:** `src/ui/tk_ui.py`
**Fix:** Document design choice deviation from typical BASIC

### 108. input_line() modal dialog
**Files:** `src/ui/tk_ui.py`
**Fix:** Clarify preference vs absolute difference

### 109. _parse_line_number whitespace
**Files:** `src/ui/tk_widgets.py`
**Fix:** Comment incomplete about valid inputs - expand

### 110. _delete_line() line_num
**Files:** `src/ui/tk_widgets.py`
**Fix:** Clarify dual numbering system

### 111. _on_status_click() breakpoint toggling
**Files:** `src/ui/tk_widgets.py`
**Fix:** Add reference to what handles it

### 112. update_line_references() pattern
**Files:** `src/ui/ui_helpers.py`
**Fix:** Document that pattern should handle correctly

### 113. serialize_variable() explicit_type_suffix
**Files:** `src/ui/ui_helpers.py`
**Fix:** Clarify if always set

### 114. renum_program() callback
**Files:** `src/ui/ui_helpers.py`
**Fix:** Complete documentation

### 115. cmd_save() example
**Files:** `src/ui/visual.py`
**Fix:** Make consistent with other examples

### 116. cmd_delete/cmd_renum/cmd_cont stubs
**Files:** `src/ui/visual.py`
**Fix:** Documented but not implemented - update status

### 117. Breakpoint support status
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** May be outdated - verify and update

### 118. RUN output clearing
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Contradicts typical behavior - document why

### 119. INPUT handling line reference
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Make line reference precise

### 120. INPUT prompt handling
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Verify interpreter printed it

### 121. Timer cancellation patterns
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Document why not applied uniformly

### 122. _sync_program_to_runtime purpose
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Resolve contradictory explanations

### 123. Paste detection threshold
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Document arbitrary 5-char threshold

### 124. Temporary interpreter creation
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Explain alternative approach

### 125. Auto-numbering "once"
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Document that logic may allow multiple numbering

### 126. _close_all_files method
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Method not shown in code - verify

### 127. VERSION constant usage
**Files:** `src/ui/web/nicegui_backend.py`
**Fix:** Hardcoded '5.21' won't update - document or fix

### 128. Breakpoint toggle shortcuts
**Files:** `docs/help/common/editor-commands.md`, `docs/help/common/debugging.md`
**Fix:** Make table format consistent

### 129. SessionState auto-save
**Files:** `src/ui/web/session_state.py`
**Fix:** Fields suggest feature but undocumented - add docs

### 130. Settings dialog
**Files:** `src/ui/web/web_settings_dialog.py`
**Fix:** Implemented but not in help - add docs

### 131. Loop FIX reference
**Files:** `docs/help/common/examples/loops.md`, `docs/help/common/language/functions/fix.md`
**Fix:** Mentioned but not demonstrated - add example

### 132. SINGLE/DOUBLE precision
**Files:** `docs/help/common/language/data-types.md`
**Fix:** Identical ranges for both types - differentiate

### 133. Character set ASCII reference
**Files:** `docs/help/common/language/character-set.md`
**Fix:** Add cross-referencing

### 134. CVI/CVS/CVD error codes
**Files:** `docs/help/common/language/appendices/error-codes.md`, `docs/help/common/language/functions/cvi-cvs-cvd.md`
**Fix:** Document connection

### 135. Double-precision exponent notation
**Files:** `docs/help/common/language/data-types.md`
**Fix:** Clarify when D notation required

### 136. LOC and LOF See Also
**Files:** `docs/help/common/language/functions/loc.md`, `docs/help/common/language/functions/lof.md`
**Fix:** Differentiate despite similar purposes

### 137. TAB function example
**Files:** `docs/help/common/language/functions/tab.md`
**Fix:** Add READ/DATA in See Also

### 138. CLEAR parameter meanings
**Files:** `docs/help/common/language/statements/clear.md`
**Fix:** Resolve contradictory version info

### 139. DEF FN extension
**Files:** `docs/help/common/language/statements/def-fn.md`
**Fix:** Clarify if implemented

### 140. END vs CONT
**Files:** `docs/help/common/language/statements/end.md`
**Fix:** Resolve contradiction

### 141. EDIT features
**Files:** `docs/help/common/language/statements/edit.md`
**Fix:** Remove docs for features not implemented

### 142. ERASE implementation note
**Files:** `docs/help/common/language/statements/erase.md`
**Fix:** Remove unnecessary note

### 143. LOAD vs MERGE file closing
**Files:** `docs/help/common/language/statements/load.md`, `docs/help/common/language/statements/merge.md`
**Fix:** Resolve contradiction

### 144. RENUM example line numbers
**Files:** `docs/help/common/language/statements/renum.md`
**Fix:** Fix duplicate line numbers in example

### 145. Variable case sensitivity
**Files:** `docs/help/common/language/variables.md`, `docs/help/common/settings.md`
**Fix:** Make explanations consistent

### 146. WIDTH documentation
**Files:** `docs/help/common/language/statements/width.md`
**Fix:** Clearly mark unsupported syntax

### 147. WRITE and WRITE# references
**Files:** `docs/help/common/language/statements/write.md`, `docs/help/common/language/statements/writei.md`
**Fix:** Use consistent terminology

### 148. RUN vs STOP file closing
**Files:** `docs/help/common/language/statements/run.md`, `docs/help/common/language/statements/stop.md`
**Fix:** Add cross-reference

### 149. Keyboard shortcuts docs
**Files:** `docs/help/common/shortcuts.md`
**Fix:** Make consistent across UIs

### 150. Settings storage paths
**Files:** `docs/help/common/settings.md`
**Fix:** Complete information

### 151. WAIT syntax
**Files:** `docs/help/common/language/statements/wait.md`
**Fix:** Fix formatting error

### 152. WIDTH support
**Files:** `docs/help/mbasic/architecture.md`, `docs/help/mbasic/compatibility.md`
**Fix:** Document consistently

### 153. Project naming
**Files:** `docs/help/mbasic/extensions.md`, `docs/help/mbasic/features.md`
**Fix:** Use consistent naming

### 154. Semantic analyzer count
**Files:** `docs/help/mbasic/architecture.md`, `docs/help/mbasic/features.md`
**Fix:** Make numbering consistent

### 155. Web UI missing
**Files:** `docs/help/mbasic/getting-started.md`, `docs/help/index.md`
**Fix:** Add to getting started

### 156. Debugging command availability
**Files:** `docs/help/mbasic/extensions.md`, `docs/help/mbasic/features.md`
**Fix:** Make UI specifics consistent

### 157. Delete lines categorization
**Files:** `docs/help/ui/curses/feature-reference.md`, `docs/help/ui/curses/editing.md`
**Fix:** Clarify file vs editing operation

### 158. Settings management Curses
**Files:** `docs/help/ui/cli/settings.md`, `docs/help/ui/curses/feature-reference.md`
**Fix:** Add documentation

### 159. Variable inspection methods
**Files:** `docs/help/ui/cli/variables.md`, `docs/help/ui/curses/feature-reference.md`
**Fix:** Explain relationship

### 160. Find/Replace availability
**Files:** `docs/help/ui/cli/find-replace.md`, `docs/help/ui/curses/feature-reference.md`
**Fix:** Resolve contradiction

### 161. Clipboard operations
**Files:** `docs/help/ui/curses/feature-reference.md`
**Fix:** Clarify conflict explanation

---

## Low Severity Documentation Fixes (254 issues)

Issues #162-415 follow the same pattern:
- Minor wording inconsistencies
- Missing cross-references
- Incomplete examples
- Formatting errors
- Redundant comments
- Terminology inconsistencies
- Missing contextual information
- Implementation details in wrong locations
- Outdated references
- Ambiguous phrasing

**See original report for complete list of remaining 254 low-severity documentation fixes.**

---

## Summary

**Total Documentation Fixes: 415**

**Categories:**
- Comments/docstrings don't match correct code behavior: ~180
- Help documentation inconsistencies: ~120
- Missing/incomplete documentation: ~60
- Redundant/misleading comments: ~40
- Cross-reference issues: ~15

**Priority Actions:**
1. Update comments in `src/interactive.py` about clear_execution_state() timing
2. Fix status bar update comments in `src/ui/curses_ui.py`
3. Document Redis session storage feature
4. Resolve contradictions in Web UI file persistence docs
5. Make keyboard shortcut documentation consistent across UIs
