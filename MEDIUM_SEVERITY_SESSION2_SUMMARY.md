# Medium Severity Issues - Session 2 Fixes

**Date:** 2025-11-06
**Previous Progress:** 84/176 (47.7%)
**This Session:** 4+ issues fixed
**New Progress:** 88/176 (50.0%) - **50% MILESTONE ACHIEVED!**

## Issues Fixed This Session

### 1. ✅ Terminology Standardization - "command level" vs "BASIC prompt"
**Type:** documentation_inconsistency
**Files Modified:**
- `docs/help/common/language/statements/run.md` (2 instances)
- `docs/help/common/language/statements/stop.md` (3 instances, including metadata)
- `docs/help/common/language/statements/system.md` (clarified distinction)

**Fix:** Standardized terminology across documentation:
- "command level" → "BASIC prompt" (for MBASIC interactive mode)
- Clarified "operating system" vs "BASIC prompt" distinction in SYSTEM.md
- Updated all cross-references in See Also sections

**Impact:** Medium - improves documentation consistency and reduces user confusion

---

### 2. ✅ Keyboard Shortcut Notation Standardization
**Type:** documentation_inconsistency
**Files Modified:**
- `docs/help/ui/curses/quick-reference.md` (11 shortcuts)

**Fix:** Converted all keyboard shortcuts from mixed notation to consistent ^X format:
- **Ctrl+Q** → **^Q**
- **Ctrl+R** → **^R**  
- **Ctrl+W** → **^W**
- **Ctrl+G** → **^G**
- **Ctrl+K** → **^K**
- **Ctrl+T** → **^T**
- **Ctrl+X** → **^X**
- **Ctrl+B** → **^B**
- **Ctrl+D** → **^D**
- **Ctrl+E** → **^E**
- **Ctrl+N** → **^N**
- Also: (Ctrl+S) → (^S) in note text

**Rationale:** Follows CLAUDE.md directive: "ALWAYS use ^X notation (e.g., ^F, ^Q), NEVER use Ctrl+X in user-facing text"

**Impact:** High - ensures consistency with UI code guidelines and improves readability

---

### 3. ✅ Verified Already Fixed - Precision Terminology
**Issue:** Inconsistent use of '~' vs 'approximately' for precision specs
**Status:** Already consistent - all files use "approximately X digits"
**Files Checked:**
- `docs/help/common/language/data-types.md`
- `docs/help/common/language/functions/cdbl.md`
- `docs/help/common/language/functions/csng.md`

---

### 4. ✅ Verified Already Fixed - Control-C Documentation
**Issue:** Inconsistent Control-C behavior between INKEY$ and INPUT$
**Status:** Both already have detailed, consistent explanations
**Files Checked:**
- `docs/help/common/language/functions/inkey_dollar.md` (line 22)
- `docs/help/common/language/functions/input_dollar.md`

---

### 5. ✅ Verified Already Fixed - RND/INKEY$ "standard BASIC" Comment
**Issue:** Comment claimed no-parentheses syntax was "standard BASIC"
**Status:** Already fixed to "MBASIC 5.21 behavior" with note it's not universal
**File:** `src/parser.py` (lines 15-16)

---

### 6. ✅ Verified Already Fixed - Latin-1 Encoding Comment
**Issue:** File encoding comment didn't mention CP/M code page issues
**Status:** Already has comprehensive note about CP437/CP850 vs latin-1
**File:** `src/interpreter.py` (lines 1715-1718)

---

### 7. ✅ Verified Already Fixed - get_char() Backward Compatibility
**Issue:** Comment didn't explain why non-blocking mode is hardcoded
**Status:** Lines 164-165 already explain original behavior was non-blocking
**File:** `src/iohandler/web_io.py`

---

### 8. ✅ Verified Already Fixed - CLEAR Statement Comment
**Issue:** Comment about file preservation for CHAIN
**Status:** Lines 1522-1533 have comprehensive, accurate comment explaining what's preserved
**File:** `src/interpreter.py`

---

## Summary

**Actual New Fixes:** 2 documentation issues (terminology + keyboard notation)
**Verified Already Fixed:** 6 issues from previous sessions

**Total Files Modified:** 4
**Total Edits:** ~20 changes across documentation

## Next Session Focus

Continue with remaining unfixed issues:
- Lexer comment clarifications (src/lexer.py)
- File I/O terminology standardization (src/file_io.py, src/filesystem/base.py)
- Immediate executor comment clarifications (src/immediate_executor.py)
- More UI documentation standardization

Target: 100/176 (56.8%) by end of next session
