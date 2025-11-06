# Medium Severity Issues - Comprehensive Summary

## Overview

**Source:** `docs/history/docs_inconsistencies_report-v10.md` - Medium Severity section
**Total Issues Reported:** 176 (actual count: 174)
**Issues Fixed:** 8 critical and high-impact fixes
**Approach:** Systematic review and targeted fixes for highest-impact issues

## Issues Fixed (8 Total)

### 1. ✅ Version Documentation Mismatch
**Issue:** setup.py version 0.99.0 not explained in docstring
**Files:** `setup.py`
**Type:** documentation_inconsistency
**Fix:** Added clear explanation that 0.99.0 means ~99% implementation complete
**Impact:** High - clarifies package versioning strategy

### 2. ✅ LineNode Text Regeneration Documentation
**Issue:** Docstring claimed text regenerated from "token positions and formatting" but didn't explain mechanism
**Files:** `src/ast_nodes.py`
**Type:** code_vs_comment_conflict
**Fix:** Clarified that position_serializer reconstructs text from statement char_start/char_end and token original_case fields
**Impact:** High - critical for understanding AST design

### 3. ✅ Comment Line Number Reference
**Issue:** Comment said "line 263" but should reference "above" for clarity
**Files:** `src/basic_builtins.py`
**Type:** code_vs_comment
**Fix:** Changed to "line 263 above" to make cross-reference clear
**Impact:** Low - minor clarity improvement

### 4. ✅ Identifier Table Bypass Comment
**Issue:** Comment about "bypassing identifier_table" was misleading about current vs future use
**Files:** `src/case_string_handler.py`
**Type:** code_vs_comment
**Fix:** Clarified that identifiers directly return original_text, table not consulted for display
**Impact:** Medium - clarifies case handling architecture

### 5. ✅ CRITICAL BUG: RSET Truncation Direction
**Issue:** RSET was truncating from wrong end (left instead of right)
**Files:** `src/interpreter.py` (line 2520)
**Type:** code_vs_comment (discovered during review)
**Fix:** Changed `value[:width]` to `value[-width:]` - RSET right-justifies so must truncate from LEFT to keep rightmost characters
**Impact:** CRITICAL - **This was an actual bug, not just documentation**. RSET would produce wrong output for long strings.
**Example:** RSET with width=5 and value="ABCDEFGH" should give "DEFGH" not "ABCDE"

### 6. ✅ Return Statement Validation Comment Clarity
**Files:** `src/interpreter.py` (line 1235-1239)
**Type:** code_vs_comment
**Fix:** Reformatted comment about return_stmt valid range with clearer bullet points
**Impact:** Medium - improves code readability

### 7. ✅ RND/INKEY$ "Standard BASIC" Claim
**Issue:** Comment claimed no-parentheses syntax was "standard BASIC" but it's MBASIC-specific
**Files:** `src/parser.py` (line 15)
**Type:** code_vs_comment
**Fix:** Changed to "MBASIC 5.21 behavior" and added note it's not universal
**Impact:** Medium - corrects potentially misleading claim about BASIC standards

### 8. ✅ Lexer Policy Validation Documentation
**Issue:** Comment claimed no validation of policy strings, but SimpleKeywordCase does validate
**Files:** `src/lexer.py` (line 21)
**Type:** code_vs_comment
**Fix:** Added note that SimpleKeywordCase validates and defaults to force_lower for invalid policies
**Impact:** Medium - documents actual validation behavior

## Categories of Remaining Issues (166)

### Code vs Comment (83 issues)
Comments that don't match implementation details:
- State machine descriptions
- Method behavior documentation
- Parameter validation claims
- Error handling documentation
- Implementation timing details

### Documentation Inconsistency (71 issues)
Cross-file documentation conflicts:
- Terminology differences (TK vs Tk, command level vs Ok prompt)
- Feature availability across UIs
- Keyboard shortcut notation (^F vs Ctrl+F)
- Settings implementation status
- Help file cross-references
- Precision specifications ("~7" vs "approximately 7")

### Code vs Documentation (9 issues - combined naming)
Higher-level architecture mismatches:
- UI component relationships
- File I/O abstraction boundaries
- Module dependency descriptions

### Internal/Code Inconsistency (3 issues)
Design pattern conflicts within files:
- Variable width vs fixed width line formatting
- Main widget storage strategies
- State checking approaches

## High Priority Remaining Issues (Top 20)

1. **src/immediate_executor.py** - INPUT statement documentation vs actual error behavior
2. **src/interactive.py** - EDIT mode digit handling (comment says "silently ignored" but no explicit handling)
3. **src/interactive.py** - CHAIN variable passing logic oversimplified in docstring
4. **src/interactive.py** - GOTO/GOSUB immediate mode behavior contradictions
5. **src/parser.py** - CALL statement MBASIC 5.21 vs extended syntax confusion
6. **src/parser.py** - MID$ statement detection lookahead limitations not documented
7. **src/lexer.py** - Old BASIC handling contradiction (PRINT# special case vs "no support" claim)
8. **src/runtime.py** - line=-1 marker categories (2 vs 3 sources)
9. **src/runtime.py** - _resolve_variable_name "standard" vs "special case" guidance unclear
10. **src/interpreter.py** - File encoding latin-1 vs CP/M code page issues
11. **src/interpreter.py** - RUN statement halted state inconsistency
12. **src/interpreter.py** - CLEAR vs RESET file close error handling differences
13. **src/iohandler/base.py** - input_line() space preservation limitations
14. **src/iohandler/web_io.py** - get_char() blocking mode hardcoded to non-blocking
15. **src/ui/curses_ui.py** - Line format variable vs fixed width
16. **src/ui/curses_ui.py** - Main widget storage strategy inconsistencies
17. **docs/help/common/language/data-types.md** - Precision specs terminology
18. **docs/help/common/language/functions/** - Control-C behavior inconsistencies
19. **docs/help/common/language/statements/for-next.md** - Loop execution contradictions
20. **docs/help/ui/** - Feature parity documentation across UIs

## Files Modified

1. `/home/wohl/cl/mbasic/setup.py`
2. `/home/wohl/cl/mbasic/src/ast_nodes.py`
3. `/home/wohl/cl/mbasic/src/basic_builtins.py`
4. `/home/wohl/cl/mbasic/src/case_string_handler.py`
5. `/home/wohl/cl/mbasic/src/interpreter.py` (2 fixes including critical RSET bug)
6. `/home/wohl/cl/mbasic/src/parser.py`
7. `/home/wohl/cl/mbasic/src/lexer.py`

## Impact Assessment

### Critical Fixes (1)
- **RSET truncation bug** - This would have caused incorrect output in programs using RSET with strings longer than field width

### High Impact (3)
- LineNode text regeneration documentation
- Version numbering explanation
- MBASIC behavior vs "standard BASIC" clarification

### Medium Impact (3)
- Identifier table architecture clarification
- Return statement validation readability
- Lexer policy validation documentation

### Low Impact (1)
- Line number comment reference

## Methodology

1. **Systematic Review:** Read report section by section
2. **Prioritization:** Focus on code correctness issues first, then high-impact documentation
3. **Verification:** Read actual code to confirm issues before fixing
4. **Targeted Fixes:** Address root causes, not just symptoms
5. **Documentation:** Track all changes in this summary

## Recommendations for Remaining Issues

### Phase 1: Critical Code Fixes (Priority 1)
Estimate: 2-4 hours
- Review all "code_vs_comment" issues for actual bugs (like RSET)
- Fix state machine documentation inconsistencies
- Correct behavior descriptions that could mislead developers

### Phase 2: Architecture Documentation (Priority 2)
Estimate: 4-6 hours
- Align file I/O abstraction descriptions across files
- Clarify UI component relationships
- Document state transition behaviors accurately

### Phase 3: User Documentation (Priority 3)
Estimate: 6-8 hours
- Standardize keyboard shortcut notation (decide on ^F vs Ctrl+F)
- Align feature availability across UI documentation
- Fix cross-reference broken links
- Standardize terminology (precision specs, command level, etc.)

### Phase 4: Low-Priority Clarifications (Priority 4)
Estimate: 4-6 hours
- Comment wording improvements
- Redundant documentation cleanup
- Minor terminology alignment

### Total Estimated Effort: 16-24 hours

## Key Insights

1. **Bug Discovery:** The documentation review process discovered an actual bug (RSET), demonstrating the value of thorough documentation audits

2. **Terminology Drift:** Multiple terms used for same concepts (TK/Tk, ~7/approximately 7, command level/Ok prompt/BASIC prompt)

3. **Documentation Lag:** Many comments describe intended behavior or historical state, not current implementation

4. **Cross-File Consistency:** Lack of central terminology authority leads to drift across 60+ documentation files

5. **UI Fragmentation:** Features documented inconsistently across CLI/Curses/Tk/Web UIs, suggesting implementation gaps

## Conclusion

**Completed:** 8 fixes addressing critical bugs and high-impact documentation issues
**Remaining:** 166 issues primarily involving comment alignment and documentation standardization
**Most Important Find:** RSET truncation bug - actual code defect discovered via documentation review

The medium severity issues represent primarily documentation quality concerns, with the occasional code defect (like RSET). A systematic approach addressing highest-impact issues first provides best ROI. The completed fixes establish patterns for addressing remaining issues.
