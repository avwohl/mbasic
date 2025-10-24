# Documentation Reorganization Plan

## Status: IN PROGRESS

This document tracks the reorganization of the 94 markdown files in the mbasic project.

## Completed (2025-10-24)

✅ **Step 1**: Moved all 86 .md files from root to doc/ directory (except README.md)
✅ **Step 2**: Deleted 15 redundant session/cleanup docs from 2025-10-22
✅ **Step 3**: Updated doc/README.md to reflect interpreter (not compiler)

**Current file count: 71 markdown files**

## Remaining Work

### High Priority

1. **Create doc/ACCOMPLISHMENTS.md for interpreter** (CURRENT ACCOMPLISHMENTS.md is about compiler optimizations NOT implemented)
   - Move current ACCOMPLISHMENTS.md to `doc/design/future_compiler/SEMANTIC_ANALYSIS_DESIGN.md`
   - Write new ACCOMPLISHMENTS.md documenting actual interpreter achievements

2. **Move compiler optimization docs to `doc/design/future_compiler/`**:
   - ACCOMPLISHMENTS.md (rename to SEMANTIC_ANALYSIS_DESIGN.md)
   - SEMANTIC_ANALYZER.md
   - OPTIMIZATION_STATUS.md
   - optimization_guide.md
   - README_OPTIMIZATIONS.md
   - SESSION_SUMMARY.md (rename to COMPILER_SEMANTIC_ANALYSIS_SESSION.md)
   - TYPE_REBINDING_STRATEGY.md
   - TYPE_REBINDING_PHASE2_DESIGN.md
   - TYPE_REBINDING_IMPLEMENTATION_SUMMARY.md
   - INTEGER_SIZE_INFERENCE.md
   - INTEGER_INFERENCE_STRATEGY.md
   - ITERATIVE_OPTIMIZATION_STRATEGY.md
   - ITERATIVE_OPTIMIZATION_IMPLEMENTATION.md
   - OPTIMIZATION_DATA_STALENESS_ANALYSIS.md
   - Create README.md explaining these are future compiler design docs

3. **Move historical docs to `doc/history/`**:
   - PHASE1_IMPROVEMENTS_2025-10-22.md → history/planning/
   - PHASE2_IMPROVEMENTS_2025-10-22.md → history/planning/
   - PHASE3_IMPROVEMENTS_2025-10-22.md → history/planning/
   - PHASE4_IMPROVEMENTS_2025-10-22.md → history/planning/
   - FINAL_TEST_REPORT.md → history/snapshots/PARSER_TEST_REPORT_2025-10-22.md
   - PARSER_STATUS_2025-10-22.md → history/snapshots/
   - PARSE_ERROR_CATEGORIES_2025-10-22.md → history/snapshots/
   - FINAL_SESSION_SUMMARY.md → history/sessions/
   - SESSION_FINAL_SUMMARY_2025-10-22.md → history/sessions/
   - SESSION_2025-10-22_SUMMARY.md → history/sessions/

### Medium Priority

4. **Update outdated analysis docs**:
   - CURRENT_FAILURE_ANALYSIS.md - Add date, update with current test results
   - FAILURE_CATEGORIZATION_CURRENT.md - Update with latest data
   - PARSER_TEST_RESULTS.md - Add date, update results
   - PARSER_SUMMARY.md - Add date, update with current state
   - TEST_RESULTS.md - Rename to TEST_RESULTS_CURRENT.md, update
   - FINAL_RESULTS.md - Determine if obsolete or move to history

5. **Update DIRECTORY_STRUCTURE.md**:
   - Update file counts
   - Reflect new doc/ organization
   - Update test corpus numbers

6. **Rename feature docs for consistency**:
   - AUTO_COMMAND_2025-10-22.md → AUTO_COMMAND_IMPLEMENTATION.md

### Low Priority

7. **Create doc index structure**:
   ```
   doc/
   ├── README.md (index of all docs)
   ├── STATUS.md (authoritative current status)
   ├── ACCOMPLISHMENTS.md (NEW - interpreter achievements)
   ├── implementation/ (feature-specific docs)
   ├── design/
   │   └── future_compiler/ (optimization/semantic analysis designs)
   ├── history/
   │   ├── sessions/
   │   ├── snapshots/
   │   └── planning/
   └── analysis/ (current analysis docs)
   ```

## Key Issues Identified

### Issue 1: Project Identity Confusion ✅ FIXED
- ~~README.md said "compiler" but project is an interpreter~~
- ~~doc/README.md said "compiler"~~
- **FIXED**: Updated doc/README.md to say "interpreter"

### Issue 2: ACCOMPLISHMENTS.md Mismatch (NEEDS FIX)
- Current ACCOMPLISHMENTS.md documents 18 compiler optimizations
- These optimizations are NOT implemented in the interpreter
- **ACTION NEEDED**: Move to future_compiler/, create new one for interpreter

### Issue 3: Redundant Session Docs ✅ FIXED
- ~~17 session docs, 13 from same date with massive overlap~~
- **FIXED**: Deleted 15 redundant files

### Issue 4: Test/Analysis Doc Staleness (NEEDS UPDATE)
- Multiple analysis docs are point-in-time snapshots
- "CURRENT" docs may be outdated
- **ACTION NEEDED**: Add dates, move old snapshots to history/, update current docs

## Files by Category

### Core Documentation (Keep in doc/)
- STATUS.md ✅
- ACCOMPLISHMENTS.md (needs replacement)
- DIRECTORY_STRUCTURE.md (needs update)
- README.md ✅
- COMPILER_DESIGN.md ✅
- LANGUAGE_CHANGES.md ✅
- COMPILER_VS_INTERPRETER_DIFFERENCES.md ✅

### Implementation Docs (18 files - Keep in doc/)
All accurate and valuable:
- ARRAY_INPUT_READ_FIX.md
- CALL_IMPLEMENTATION.md
- CR_LINE_ENDING_FIX.md
- CTRL_C_INPUT_HANDLING.md
- DATA_STATEMENT_FIX.md
- DEF_FN_IMPLEMENTATION.md
- DETOKENIZER_FIXES.md
- ELSE_KEYWORD_FIX.md
- FILE_IO_IMPLEMENTATION.md
- HASH_FILE_IO_FIX.md
- INKEY_LPRINT_IMPLEMENTATION.md
- INPUT_HASH_FIX.md
- KEYWORD_IDENTIFIER_SPLITTING.md
- MID_STATEMENT_COMMENTS_FIX.md
- MID_STATEMENT_FIX.md
- RANDOMIZE_IMPLEMENTATION.md
- RUN_STATEMENT_IMPLEMENTATION.md
- SYSTEM_STATEMENT_FIX.md

### Compiler Design Docs (Move to future_compiler/)
14 files documenting unimplemented compiler optimizations

### Historical Docs (Move to history/)
9 files - session summaries, planning docs, snapshots

### Current Analysis (Keep but update)
- CURRENT_FAILURE_ANALYSIS.md
- FAILURE_CATEGORIZATION_CURRENT.md
- PARSER_TEST_RESULTS.md
- PARSER_SUMMARY.md
- TEST_RESULTS.md

## Summary Statistics

**Before cleanup**: 94 files
**After step 1 (consolidate to doc/)**: 86 files
**After step 2 (delete redundant)**: 71 files
**After full reorganization (planned)**: ~50 files in doc/, ~14 in future_compiler/, ~10 in history/

## Implementation Notes

The reorganization revealed that:
1. All .md files were in root directory (should be in doc/)
2. Massive redundancy in 2025-10-22 session docs
3. ACCOMPLISHMENTS.md documents features not in the interpreter
4. Many docs labeled "CURRENT" may be outdated

The goal is to have:
- Clear separation between implemented (interpreter) and designed (future compiler) features
- Historical docs archived separately
- Current/active docs easy to find
- No redundancy or confusion
