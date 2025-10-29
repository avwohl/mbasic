# Lexer Cleanup - TODO

**Status:** ⏳ TODO
**Priority:** HIGH
**Created:** 2025-10-29 (v1.0.295)

## Problems Identified

### 1. Case-Keeping String Not Factored Out

**Problem:** After adding case-keeping for identifiers, it should have been factored out and applied to keywords too. Instead, lexer got its own case-keeping implementation.

**Solution:** Create a `case_keepy_string()` function that:
- Takes a setting prefix parameter (e.g., "idents" or "keywords")
- Checks settings for whether to enforce case consistency
- Used by both lexer and identifier handling

### 2. STATEMENT_KEYWORDS Tries to Parse Old BASIC

**Problem:** The keyword detection in `STATEMENT_KEYWORDS` attempts to handle old BASIC that allowed:
```basic
fori=0to10
```

This is now handled by scripts to fix old BASIC. The lexer should parse the real language.

**Issue:** As it is, `NextTime=2` would be bad because "Next" is a keyword.

**Solution:** Remove the special handling for keywords running together with identifiers. The lexer should tokenize properly-formed MBASIC code only.

### 3. Multiple Identifier Tables

**Problem:** There are a bunch of identifiers in the KEYWORD table for various tables. Polling multiple tables is weird.

**Solution:**
- Have one identifier table
- If an identifier has some lexical issue, use `ident.lex_fix()` to handle it
- Don't poll multiple tables

### 4. Suffix Stripping Confusion

**Problem:** The suffix stripping handles IO keywords followed by `#` as a special case.

**Confusion:** Either:
- `#` always gets stripped from identifiers (which it does for all)
- OR it's a syntax issue and IO keywords can be followed by a `#` token

**Solution:** Clarify and simplify the suffix stripping logic. Make it consistent.

## Implementation Plan

### Phase 1: Factor Out Case-Keeping String

1. **Create case_keepy_string() function** in a new module (or in case_keeper.py):
   ```python
   def case_keepy_string(text: str, setting_prefix: str) -> str:
       """Apply case-keeping rules based on settings.

       Args:
           text: The string to process
           setting_prefix: "idents" or "keywords" to check settings

       Returns:
           Canonicalized string respecting case-keeping settings
       """
   ```

2. **Update lexer to use case_keepy_string()** for keywords

3. **Update identifier handling to use case_keepy_string()**

### Phase 2: Remove Old BASIC Keyword Handling

1. **Review STATEMENT_KEYWORDS** in lexer.py

2. **Remove special handling** for keywords running together

3. **Ensure proper tokenization** of `NextTime=2` as:
   - IDENTIFIER("NextTime")
   - EQUALS
   - NUMBER(2)

4. **Document** that old BASIC with `fori=0to10` must be preprocessed

### Phase 3: Unify Identifier Tables

1. **Identify all keyword/identifier tables** in lexer

2. **Create single identifier lookup** mechanism

3. **Implement lex_fix()** for identifiers with special handling needs

4. **Remove polling of multiple tables**

### Phase 4: Clarify Suffix Stripping

1. **Review current suffix handling** for `#` with IO keywords

2. **Determine correct behavior:**
   - Should `PRINT#` be tokenized as `PRINT` + `#`?
   - Or as a single identifier with `#` suffix stripped?

3. **Implement consistent rule** across all identifiers

4. **Document the decision**

## Testing

After each phase:

1. **Test basic programs:**
   ```basic
   10 NextTime = 2
   20 PRINT NextTime
   ```

2. **Test IO with #:**
   ```basic
   10 OPEN "O", #1, "test.txt"
   20 PRINT #1, "Hello"
   ```

3. **Test case-keeping:**
   ```basic
   10 myVar = 5
   20 MYVAR = 10
   30 PRINT myVar, MYVAR
   ```

4. **Run existing test suite**

## Estimated Effort

- Phase 1 (Case-keeping): 2 hours
- Phase 2 (Old BASIC): 1 hour
- Phase 3 (Unify tables): 2 hours
- Phase 4 (Suffix clarity): 2 hours
- Testing: 2 hours

**Total:** ~9 hours

## Dependencies

- May need to update parser if lexer tokens change
- May need to update case_keeper.py module
- Documentation of lexer behavior

## References

- `/home/wohl/lexer_sux.txt` - Original issue description
- `src/lexer.py` - Current lexer implementation
- `src/case_keeper.py` - Case-keeping module
