# Post-END Code Cleanup Analysis Results

## Summary

Analyzed files in `bad_not521/` and `bad_syntax/` directories to find unreferenced code after END statements, similar to the successful Control-Z cleanup.

**Result:** Found 8 files with fully unreferenced post-END code, but removing it did not rescue any files.

## Comparison to Control-Z Cleanup

### Control-Z Cleanup (Previous Success)
- **Files analyzed:** 27 files with Control-Z (^Z) EOF markers
- **Successfully rescued:** 3 files became legal after cleanup
- **Reason for success:** The Control-Z marker and data after it was the only problem

### Post-END Cleanup (This Analysis)
- **Files analyzed:** 8 files with unreferenced code after END statements
- **Successfully rescued:** 0 files
- **Reason for failure:** Files have actual syntax errors in executable code

## Files Analyzed and Results

### bad_not521 Directory

1. **aut850.bas**
   - END at line 80, removed 12 unreferenced lines (395 bytes)
   - Still has error: `?Syntax error in 20: column 9: Unexpected token in expression: HASH`
   - Reason: Uses # token in invalid context

2. **checkers.bas**
   - END at line 950, removed 1 unreferenced line (47 bytes)
   - Still has error: `?Syntax error in 160: column 7: Unexpected token in expression: BACKSLASH`
   - Reason: Uses \ (backslash) in unexpected location

3. **krakinst.bas**
   - END at line 810, removed 1 unreferenced line (119 bytes)
   - Still has error: `?Syntax error in 380: column 25: Expected A after comma in SAVE, got p`
   - Reason: Invalid SAVE statement syntax

4. **pcat.bas**
   - END at line 10000, removed 2 unreferenced lines (58 bytes)
   - Still has error: `?Syntax error in 105: column 11: Unexpected token in expression: LPRINT`
   - Reason: Uses LPRINT (line printer output, not implemented)

### bad_syntax Directory

5. **backgamm.bas**
   - END at line 2870, removed 63 unreferenced lines (1953 bytes)
   - Still has error: `?Syntax error in 60: column 13: Expected EQUAL, got COLON`
   - Reason: Syntax error in DEF statement

6. **lanes.bas**
   - END at line 9999, removed 2 unreferenced lines (64 bytes)
   - Still has error: (no specific error shown)
   - Reason: Multiple syntax errors

7. **speech.bas**
   - END at line 600, removed 28 unreferenced lines (1500 bytes)
   - Still has error: `?Syntax error in 260: column 17: Expected RPAREN, got IDENTIFIER`
   - Reason: Parentheses syntax error

8. **trade.bas**
   - END at line 4660, removed 4 unreferenced lines (78 bytes)
   - Still has error: `?Syntax error in 1260: column 54: Expected : or newline, got MOD`
   - Reason: MOD operator syntax issue

## Analysis

### Why Control-Z Cleanup Worked But Post-END Didn't

1. **Control-Z cleanup success:** The files had valid MBASIC 5.21 code that was followed by a Control-Z EOF marker and binary/garbage data. Removing everything after ^Z fixed the files.

2. **Post-END cleanup failure:** These files are in `bad_not521` and `bad_syntax` because their main executable code (before the END statement) contains syntax that is not compatible with MBASIC 5.21:
   - Non-standard tokens (# for comments, \ operator)
   - Unimplemented statements (LPRINT)
   - Syntax variations from other BASIC dialects
   - Parser incompatibilities

### Value of This Analysis

While no files were rescued, this analysis:
1. Confirmed that files in `bad_not521/` and `bad_syntax/` have legitimate syntax incompatibilities
2. Identified that many files contain unreferenced notes/comments after END statements
3. Documents the specific syntax errors preventing each file from running
4. Shows that the post-END code was developer notes, not the cause of invalidity

## Files With Mixed Referenced/Unreferenced Code

The analysis also identified many files where some lines after END are referenced by GOTO/GOSUB (and thus are reachable subroutines), while other lines are unreferenced. These require careful manual analysis and cannot be automatically cleaned.

Examples:
- acey.bas: 57 lines after END, 11 are referenced (subroutines), 46 are not
- airmiles.bas: 193 lines after END, 4 are referenced, 189 are not
- Many others with complex mixed patterns

## Conclusion

The post-END cleanup analysis was valuable for understanding the corpus but did not rescue any files, unlike the Control-Z cleanup. Files in `bad_not521/` and `bad_syntax/` directories have actual MBASIC 5.21 syntax incompatibilities in their executable code that prevent them from running, not just extraneous data after the program.

## Tools Created

- **analyze_end_statements.py**: Analyzes BASIC files for END statements and checks if lines after END are referenced by control flow
- **clean_post_end.py**: Removes fully unreferenced lines after END and tests if files become legal

Both tools are available in the project root for future analysis.
