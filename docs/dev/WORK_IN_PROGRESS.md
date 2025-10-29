# Work in Progress

## Task
Documentation Coverage - Phase 1 Complete, Phase 2 Ready to Start

## Status
- ✅ Phase 1: Name normalization completed
- ⏸️ Phase 2: Create missing documentation (ready to start after lunch)

## What Was Completed

### Phase 1: Fix Name Mismatches (COMPLETE)
- ✅ Created `utils/check_doc_coverage.py` audit tool
- ✅ Added function name normalization (handles `$` suffix, `_dollar` filenames)
- ✅ Added statement name normalization (handles compound docs like `for-next.md`)
- ✅ Reduced documentation gaps from 42 to 26 items (38% improvement)
- ✅ Generated accurate coverage report at `docs/dev/DOCUMENTATION_COVERAGE.md`

### Results
**Before normalization:** 42 missing items
**After normalization:** 26 missing items

**Functions:** 45 implemented, 45 documented
- Missing docs: 7 functions (CDBL, CHR, CSNG, INPUT_STR, LOF, OCT, SPACE)
- Extra docs: 7 functions (COBL, CRR, FRE, LPOS, VARPTR, INPUT, SPACES)

**Statements:** 65 implemented, 76 documented
- Missing docs: 19 statements (CLS, DEFTYPE, FILES, HELPSETTING, LIMITS, LSET, MIDASSIGNMENT, ONERROR, ONGOSUB, ONGOTO, PRINTUSING, REMARK, RESET, RESTORE, RSET, RUN, SETSETTING, SHOWSETTINGS, SYSTEM)

## Next Steps

### Phase 2: Create Missing Function Documentation (7 functions)

#### Type Conversion (3)
1. `docs/help/common/language/functions/csng.md` - Convert to single precision
2. `docs/help/common/language/functions/cdbl.md` - Convert to double precision
3. `docs/help/common/language/functions/chr.md` or `chr_dollar.md` - ASCII to character

#### String Functions (1)
4. Fix SPACE vs SPACES naming issue (implementation uses SPACE, doc says SPACES)

#### Numeric Conversion (1)
5. `docs/help/common/language/functions/oct.md` or `oct_dollar.md` - Octal conversion

#### I/O Functions (2)
6. Fix INPUT_STR vs INPUT$ naming issue
7. `docs/help/common/language/functions/lof.md` - Length of file

### Phase 3: Create Missing Statement Documentation (19 statements)

Priority order:
1. **Core statements:** CLS, SYSTEM, RUN, RESTORE (4)
2. **Error handling:** ONERROR, ONGOSUB, ONGOTO (may already exist with different names) (3)
3. **File I/O:** LSET, RSET, RESET, FILES (4)
4. **Type definition:** DEFTYPE (already exists as defint-sng-dbl-str.md?) (1)
5. **Formatting:** PRINTUSING (may exist as print-using.md or printi-printi-using.md) (1)
6. **Modern extensions:** HELPSETTING, SETSETTING, SHOWSETTINGS, LIMITS (4)
7. **Other:** MIDASSIGNMENT, REMARK (2)

## Files Modified

- `utils/check_doc_coverage.py` - Created and improved with normalization
- `docs/dev/DOCUMENTATION_COVERAGE.md` - Updated coverage report
- `docs/dev/LANGUAGE_DOCUMENTATION_COMPLETION_TODO.md` - Master TODO created
- `docs/help/common/language/functions/cos.md` - Fixed (removed CSNG conflation)
- `docs/help/common/language/functions/cint.md` - Fixed See Also section
- `docs/help/ui/web/index.md` - Added clickable help links
- `src/ui/web_help_launcher.py` - Fixed URL, removed legacy build code
- `src/ui/tk_ui.py` - Updated help path
- `src/ui/web/nicegui_backend.py` - Added help functionality

## Context/Notes

### Naming Conventions Discovered
- **Implementation:** Functions named after token types (CHR, STR, HEX) without `$`
- **Documentation:** Filenames use `_dollar` suffix (chr_dollar.md), but titles use `$` (CHR$)
- **Lexer:** Tokenizes `CHR$` as `TokenType.CHR` with value `chr$`
- **Solution:** Normalize both sides by removing `$` and `_dollar` for comparison

### Statement Documentation Pattern
- Compound statements in single file: `for-next.md` documents both FOR and NEXT
- Use hyphens in filenames: `line-input.md`, `on-error-goto.md`
- Implementation uses CamelCase: LINEINPUT, PRINTUSING, ONERROR

### Testing Strategy (Phase 4)
Once docs complete:
1. Extract examples from each doc
2. Create `tests/language/functions/test_<function>.py`
3. Verify examples work against real MBASIC 5.21 (using tnylpo)
4. Auto-generate tests from documentation examples

## Version

Current: 1.0.300 (committed and pushed)

## Time Estimate

- Phase 2 (7 function docs): 2-3 hours
- Phase 3 (19 statement docs): 4-6 hours
- Phase 4 (test coverage): Will tackle separately

Total remaining: 6-9 hours
