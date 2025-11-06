# Medium Severity Issues - Fix Progress

**Total Issues:** 174 medium severity issues from docs_inconsistencies_report-v10.md

## Completed Fixes (5)

### 1. ✅ Version mismatch between setup.py and documentation
**Files:** `setup.py`
**Fix:** Added clear documentation explaining version 0.99.0 means 99% implementation status

### 2. ✅ LineNode docstring - text regeneration explanation
**Files:** `src/ast_nodes.py`
**Fix:** Clarified that text is regenerated from statement tokens (char_start/char_end, original_case)

### 3. ✅ Comment about original_negative capture location
**Files:** `src/basic_builtins.py`
**Fix:** Changed "line 263" to "line 263 above" for clarity

### 4. ✅ Comment about bypassing identifier_table
**Files:** `src/case_string_handler.py`
**Fix:** Clarified that identifiers directly return original_text without consulting table

### 5. ✅ CRITICAL BUG: RSET truncation direction
**Files:** `src/interpreter.py`
**Fix:** Changed `value[:width]` to `value[-width:]` - RSET should truncate from LEFT (keep rightmost chars)

### 6. ✅ execute_return validation comment clarity
**Files:** `src/interpreter.py`
**Fix:** Clarified valid range for return_stmt with better formatting

## Remaining High-Priority Issues (20)

### Code vs Comment Conflicts (need review)
1. `src/immediate_executor.py` - INPUT statement behavior vs error message
2. `src/interactive.py` - EDIT mode digit handling
3. `src/interactive.py` - CHAIN variable passing logic oversimplified
4. `src/interactive.py` - GOTO/GOSUB in immediate mode contradictions
5. `src/parser.py` - RND/INKEY$ "standard BASIC" should be "MBASIC 5.21 behavior"
6. `src/parser.py` - CALL statement MBASIC 5.21 vs extended syntax confusion
7. `src/lexer.py` - Policy validation comment vs actual behavior
8. `src/lexer.py` - Old BASIC handling contradiction (PRINT# special case)
9. `src/runtime.py` - line=-1 marker categories inconsistency
10. `src/interpreter.py` - File encoding latin-1 vs CP/M code pages

### Documentation Inconsistencies (need updates)
11. `docs/help/common/language/data-types.md` vs function docs - precision specs ("~7" vs "approximately 7")
12. `docs/help/common/language/functions/input_dollar.md` vs `inkey_dollar.md` - Control-C behavior
13. `docs/help/common/language/statements/for-next.md` - Loop execution contradictions
14. `docs/help/common/language/statements/lprint-lprint-using.md` vs `print.md` - PRINT USING not documented
15. `docs/help/ui/curses/variables.md` vs `tk/feature-reference.md` - Variable editing capabilities differ
16. `docs/help/ui/web/getting-started.md` vs `features.md` - localStorage auto-save status
17. `docs/user/UI_FEATURE_COMPARISON.md` - CLI save functionality contradiction
18. `src/file_io.py` vs `src/filesystem/base.py` - Terminology inconsistencies
19. `src/iohandler/base.py` - input_line() preservation of spaces limitation
20. `src/ui/curses_ui.py` - Line format variable width vs fixed width inconsistency

## Lower Priority Issues (149)

### Comment Clarifications Needed
- TypeInfo class wrapper vs alternative interface
- File I/O architecture overlaps
- Immediate mode state descriptions
- Help text references
- Keyboard shortcut documentation
- Settings implementation status
- Debug feature availability

### Documentation Alignment
- Precision specifications terminology
- Keyboard shortcut notation (^F vs Ctrl+F)
- UI feature parity across backends
- Cross-reference completeness
- Implementation status markers

## Fix Strategy

1. **Phase 1 (DONE):** Critical bugs and high-impact clarity issues (6 fixes)
2. **Phase 2 (IN PROGRESS):** High-priority comment/doc mismatches (targeting 20)
3. **Phase 3:** Documentation standardization (targeting 50)
4. **Phase 4:** Lower priority clarifications (targeting 100)
5. **Phase 5:** Final review and summary

## Files Modified So Far
1. `setup.py`
2. `src/ast_nodes.py`
3. `src/basic_builtins.py`
4. `src/case_string_handler.py`
5. `src/interpreter.py` (2 fixes including critical RSET bug)

## Next Steps
- Continue with high-priority code vs comment conflicts
- Update documentation files for consistency
- Generate final comprehensive summary
