# Documentation Fixes Tracking
**Source**: docs/history/docs_inconsistencies_report1-v2.md
**Total Issues**: 126
**Last Updated**: 2025-11-03 (Session 2)
**Status**: Active - 41/126 fixed

## Progress Summary
- ✅ **Fixed**: 41 (32.5%)
- ❌ **Remaining**: 85 (67.5%)

## High Severity (17/17 fixed - 100%)

### ✅ Fixed
1. **syntax_inconsistency** - ABS function typo (ASS → ABS)
2. **broken_reference** - running.md file path
3. **contradictory_information** - RESUME and RESTORE conflicting metadata (added related field)
4. **command_inconsistency** - Ctrl+L shortcut conflict (fixed in feature-reference.md, quick-reference.md)
5. **command_inconsistency** - Ctrl+X shortcut conflict (clarified Stop vs Cut)
6. **keyboard_shortcut_inconsistency** - Loading files (removed 'b', kept Ctrl+O)
7. **keyboard_shortcut_inconsistency** - Saving files (fixed to Ctrl+V, removed F5)
8. **keyboard_shortcut_inconsistency** - Running programs (fixed to Ctrl+R, removed F2)
9. **keyboard_shortcut_inconsistency** - Listing programs (changed to Menu only, removed F3 and Ctrl+L)
10. **keyboard_shortcut_inconsistency** - Execution stack (changed to Menu only, removed Ctrl+K)
11. **contradictory_information** - Testing reference claims verification (test files exist, issue was incorrect)
12. **feature_availability_conflict** - Debugging features (fixed CLI Only to UI-dependent)
13. **contradictory_information** - Web UI file persistence (fixed auto-save documentation)
14. **feature_availability_conflict** - Tk vs Web settings dialog (clarified differences)
15. **feature_availability_conflict** - Web UI debugging features (updated to reflect actual implementation)
16. **contradictory_information** - File system handling Tk UI (verified uses native dialogs)
17. **contradictory_information** - DEF FN function name length (fully documented)

## Medium Severity (16/47 fixed)

### ✅ Fixed
1. **incomplete_description** - SGN function
2. **duplicate_function** - SPACE$/SPACES
3. **missing_description** - ERR AND ERL VARIABLES
4. **missing_description** - files.md (added description for Curses file operations)
5. **missing_description** - editing.md (added description for Curses editing)
6. **inconsistent_categorization** - ERR AND ERL → error-handling
7. **inconsistent_categorization** - input_hash.md → file-io
8. **inconsistent_categorization** - line-input.md → file-io
9. **inconsistent_categorization** - lprint-lprint-using.md → file-io
10. **inconsistent_categorization** - cload.md → file-io
11. **inconsistent_categorization** - csave.md → file-io
12. **inconsistent_categorization** - defint-sng-dbl-str.md → type-declaration
13. **missing_category** - CVI/CVS/CVD, MKI$/MKS$/MKD$ → type-conversion
14. **missing_function_reference** - LOF added to functions index
15. **missing_function_reference** - PEEK added to functions index
16. **missing_function_reference** - OCT$ added to functions index

### ❌ Remaining (31)
[List continues with all medium severity issues...]

## Low Severity (6/62 fixed)

### ✅ Fixed
1. **missing_category** - TAB function → output-formatting
2. **version_information_inconsistency** - HEX$ function "Versionsr" typo fixed
3. **syntax_formatting_inconsistency** - INT function syntax and examples fixed
4. **inconsistent_formatting** - WRITE statement OCR errors fixed
5. **typo_in_description** - LEFT$ function "the." typo fixed
6. **typo** - LEFT$ function "I=O" changed to "I=0"

### ❌ Remaining (56)
[List continues with all low severity issues...]

## Next Actions (Priority Order)
1. ✅ DONE: Keyboard shortcuts aligned with actual keybindings
2. ✅ DONE: High severity contradictions resolved
3. **TODO**: Fix Web UI documentation inconsistencies (5 high severity remaining)
4. **TODO**: Complete cross-reference fixes (31 medium severity remaining)
5. **TODO**: OCR error cleanup (56 low severity remaining)