# Language Documentation Completion TODO

**Status:** ✅ DONE (2025-10-29)
**Priority:** HIGH
**Created:** 2025-10-29

## Overview

Now that the help system infrastructure is complete and deployed, we need to ensure complete documentation coverage for all MBASIC 5.21 language features.

## Background

- Help system is live at http://localhost/mbasic_docs
- TK and Web UIs successfully open help in browser
- Curses UI has internal help widget
- Created `utils/check_doc_coverage.py` to audit documentation completeness

## Current Status

**From latest coverage report:**
- **Functions:** 45 implemented, 45 documented (but 17 have doc/impl name mismatches)
- **Statements:** 65 implemented, 63 documented (22 have name mismatches)
- **Total gap:** ~39 items need documentation fixes

### Major Issues

1. **$ Suffix Mismatch** - Implementation uses `CHR`, docs use `CHR$` (or vice versa)
2. **Statement Name Mismatches** - e.g., `LINEINPUT` vs `line-input.md`
3. **Missing Core Functions:**
   - CDBL (convert to double precision)
   - CSNG (convert to single precision)
   - CHR (character from ASCII)
   - HEX (hex conversion)
   - OCT (octal conversion)
   - STRING/SPACE (string generation)

4. **Missing Statements:**
   - CLS (clear screen)
   - SYSTEM (exit to OS)
   - RUN (execute program)
   - RESTORE (reset DATA pointer)
   - ON ERROR, ON GOTO, ON GOSUB variants

## Tasks

### Phase 1: Fix Name Mismatches (High Priority)

1. **Audit $ suffix conventions**
   - [ ] Review basic_builtins.py function names
   - [ ] Review docs/help/common/language/functions/ filenames
   - [ ] Decide on canonical naming: `STR` or `STR$`?
   - [ ] Align implementation and documentation

2. **Fix statement name mappings**
   - [ ] Map `LINEINPUT` → `line-input.md`
   - [ ] Map `PRINTUSING` → `print-using.md` (may exist as `printi-printi-using.md`)
   - [ ] Map `ONERROR` → `on-error-goto.md`
   - [ ] Map `ONGOTO` → `on-gosub-on-goto.md`
   - [ ] Map `OPTIONBASE` → `option-base.md`

3. **Update check_doc_coverage.py**
   - [ ] Add name normalization rules
   - [ ] Handle compound statement docs (e.g., "for-next.md" covers both FOR and NEXT)
   - [ ] Generate actionable report with specific file paths

### Phase 2: Create Missing Function Documentation

Create documentation files for these 17 functions:

#### Type Conversion Functions
- [ ] `csng.md` - Convert to single precision
- [ ] `cdbl.md` - Convert to double precision
- [ ] `chr.md` - Convert ASCII code to character

#### String Functions
- [ ] `left.md` - Left substring (may exist as `left_dollar.md`)
- [ ] `right.md` - Right substring (may exist as `right_dollar.md`)
- [ ] `mid.md` - Middle substring (may exist as `mid_dollar.md`)
- [ ] `str.md` - Convert number to string (may exist as `str_dollar.md`)
- [ ] `space.md` - Generate spaces (may exist as `spaces.md`)
- [ ] `string.md` - Generate repeated character (may exist as `string_dollar.md`)

#### Numeric Conversion
- [ ] `hex.md` - Convert to hexadecimal string (may exist as `hex_dollar.md`)
- [ ] `oct.md` - Convert to octal string

#### I/O Functions
- [ ] `inkey.md` - Read keyboard without waiting (may exist as `inkey_dollar.md`)
- [ ] `input_str.md` - Read from file (may exist as `input_dollar.md`)
- [ ] `lof.md` - Length of file

#### Binary File I/O
- [ ] `mki.md`, `mks.md`, `mkd.md` - Convert to binary format (may exist as compound doc)

**Note:** Many of these likely exist with `_dollar` suffix in filename. Check before creating!

### Phase 3: Create Missing Statement Documentation

Create documentation files for these 22 statements:

#### Core Statements
- [ ] `cls.md` - Clear screen
- [ ] `system.md` - Exit to operating system
- [ ] `run.md` - Execute program
- [ ] `restore.md` - Reset DATA read pointer

#### Type Definition
- [ ] `def-fn.md` - Define function (may already exist)
- [ ] `defint-sng-dbl-str.md` - Define default types (may already exist)

#### Error Handling (likely documented but name mismatch)
- [ ] Verify `on-error-goto.md` exists
- [ ] Verify `on-gosub-on-goto.md` covers ON GOSUB and ON GOTO

#### File I/O
- [ ] `lset.md` - Left-justify string in field
- [ ] `rset.md` - Right-justify string in field
- [ ] `reset.md` - Close all files
- [ ] `files.md` - List directory

#### Modern Extensions (MBASIC-2025 specific)
- [ ] `helpsetting.md` - Configure help system
- [ ] `setsetting.md` - Set configuration
- [ ] `showsettings.md` - Display settings
- [ ] `limits.md` - Show resource limits

### Phase 4: Add Test Coverage

Once documentation is complete:

1. **Create test suite based on documentation**
   - [ ] Extract examples from each function doc
   - [ ] Create `tests/language/functions/test_<function>.py`
   - [ ] Extract examples from each statement doc
   - [ ] Create `tests/language/statements/test_<statement>.py`

2. **Verify examples work**
   - [ ] Run each documented example against real MBASIC 5.21
   - [ ] Compare outputs with our implementation
   - [ ] Fix any discrepancies

3. **Generate test coverage report**
   - [ ] Create `utils/check_test_coverage.py`
   - [ ] Compare against `LANGUAGE_FEATURES_TEST_COVERAGE.md`
   - [ ] Identify remaining gaps

4. **Integration with CI/CD**
   - [ ] Add doc-based test generation to build process
   - [ ] Ensure examples in docs are always tested
   - [ ] Fail build if documented feature doesn't work

## Acceptance Criteria

- [ ] `python3 utils/check_doc_coverage.py` reports 0 missing items
- [ ] All documented functions have working examples
- [ ] All documented statements have working examples
- [ ] Test coverage for language features is >90%
- [ ] Every function/statement doc links to related features
- [ ] Search works for all documented features

## Implementation Notes

### Documentation Template

Each function/statement doc should have:
- Title and syntax
- Versions where available (SK, Extended, Disk Extended, Disk)
- Clear description
- Working example(s)
- Notes section (edge cases, gotchas)
- See Also section with links

### Naming Conventions

**Decision needed:** Should we use `STR` or `STR$` in docs?
- MBASIC 5.21 prints functions with `$` suffix
- Implementation uses `_DOLLAR` suffix internally
- Docs currently inconsistent

**Recommendation:** Use `STR$` in docs (user-visible), `STR` in implementation

### Automated Testing Strategy

```python
# Example: Auto-generate tests from docs
def test_from_docs():
    for func_doc in glob('docs/help/.../functions/*.md'):
        examples = extract_examples(func_doc)
        for example in examples:
            with subtest(example):
                assert run_basic(example) == expected_output(example)
```

## Related Files

- `utils/check_doc_coverage.py` - Audit tool (created today)
- `docs/dev/LANGUAGE_FEATURES_TEST_COVERAGE.md` - Test coverage tracking
- `docs/dev/UI_FEATURE_PARITY_TRACKING.md` - UI feature tracking (similar approach)
- `src/basic_builtins.py` - Function implementations
- `src/interpreter.py` - Statement implementations

## Timeline Estimate

- **Phase 1 (Name fixes):** 2-4 hours
- **Phase 2 (Function docs):** 8-12 hours (if starting from scratch, less if just renaming)
- **Phase 3 (Statement docs):** 6-10 hours
- **Phase 4 (Test coverage):** 10-15 hours

**Total:** 26-41 hours of work

## Notes

- PDF source documents likely have more content to extract
- Check `basic/` directory for example programs to use in docs
- Compare with original Microsoft BASIC-80 5.21 manual for accuracy
- Use tnylpo/MBASIC 5.21 to verify examples produce correct output
