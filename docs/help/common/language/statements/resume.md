---
category: error-handling
description: Continue program execution after error recovery
keywords:
- error
- error handling
- on error
- resume
- resume next
- erl
- err
syntax: |
  RESUME
  RESUME NEXT
  RESUME <line number>
title: RESUME
type: statement
---

# RESUME

## Purpose

To continue program execution after an error recovery procedure has been performed.

## Syntax

RESUME has three forms:

```basic
RESUME                  ' Retry the statement that caused the error
RESUME NEXT             ' Continue at the statement after the error
RESUME <line number>    ' Continue at a specific line number
```

## Remarks

### Form 1: RESUME

Execution resumes at the statement that caused the error.

Use this form when:
- You've fixed the condition that caused the error
- You want to retry the same operation
- Example: User entered invalid data, now it's corrected

### Form 2: RESUME NEXT

Execution resumes at the statement immediately following the one that caused the error.

Use this form when:
- You want to skip the statement that caused the error
- The error is expected and can be safely ignored
- Example: Optional file operation failed, continue anyway

### Form 3: RESUME <line number>

Execution resumes at the specified line number.

Use this form when:
- You want to continue at a different location
- Error recovery requires jumping to a specific section
- Example: Fatal error, jump to cleanup routine

### Important Notes

- RESUME can only be used inside an error handler (set up with ON ERROR GOTO)
- Using RESUME outside an error handler causes "RESUME without error" error
- After RESUME executes, the error handler is still active for future errors
- Use ON ERROR GOTO 0 to disable error trapping

## Examples

### Example 1: RESUME - Retry After Fixing Error

```basic
10 ON ERROR GOTO 1000
20 PRINT "Enter a non-zero number:"
30 INPUT A
40 X = 100 / A
50 PRINT "Result: "; X
60 END

1000 REM Error handler
1010 PRINT "Error: Division by zero"
1020 PRINT "Please enter a non-zero number:"
1030 INPUT A
1040 RESUME
```

**Output:**
```
Enter a non-zero number:
? 0
Error: Division by zero
Please enter a non-zero number:
? 5
Result: 20
```

**Explanation:**
- Line 40 causes division by zero error
- Error handler gets new value for A
- RESUME (line 1040) retries line 40 with new value

### Example 2: RESUME NEXT - Skip Error and Continue

```basic
10 ON ERROR GOTO 1000
20 OPEN "I", #1, "DATA.TXT"
30 PRINT "File opened successfully"
40 CLOSE #1
50 PRINT "Program continues"
60 END

1000 REM Error handler
1010 PRINT "Warning: Could not open file"
1020 PRINT "Continuing without file..."
1030 RESUME NEXT
```

**Output (if file doesn't exist):**
```
Warning: Could not open file
Continuing without file...
Program continues
```

**Explanation:**
- Line 20 fails (file not found)
- Error handler prints warning
- RESUME NEXT (line 1030) skips to line 30
- Program continues

### Example 3: RESUME <line number> - Jump to Specific Location

```basic
10 ON ERROR GOTO 1000
20 PRINT "Opening files..."
30 OPEN "I", #1, "INPUT.DAT"
40 OPEN "O", #2, "OUTPUT.DAT"
50 PRINT "Processing..."
60 REM ... processing code ...
70 CLOSE #1, #2
80 END

1000 REM Error handler
1010 PRINT "Error "; ERR; " at line "; ERL
1020 IF ERR = 53 THEN PRINT "File not found"
1030 PRINT "Closing files and exiting..."
1040 RESUME 2000

2000 REM Cleanup routine
2010 CLOSE
2020 PRINT "Program terminated"
2030 END
```

**Explanation:**
- Error in file operations
- Handler identifies error type
- RESUME 2000 jumps to cleanup routine
- All files closed, program exits cleanly

### Example 4: Using ERR and ERL with RESUME

```basic
10 ON ERROR GOTO 1000
20 FOR I = 1 TO 5
30   PRINT "Attempting operation "; I
40   X = 100 / (I - 3)
50   PRINT "Success: "; X
60 NEXT I
70 END

1000 REM Error handler
1010 PRINT "Error "; ERR; " at line "; ERL
1020 IF ERR = 11 THEN PRINT "Division by zero - skipping"
1030 RESUME NEXT
```

**Output:**
```
Attempting operation  1
Success:  -50
Attempting operation  2
Success:  -100
Attempting operation  3
Error  11  at line  40
Division by zero - skipping
Attempting operation  4
Success:  100
Attempting operation  5
Success:  50
```

**Explanation:**
- Loop processes 5 operations
- Operation 3 causes division by zero (I-3 = 0)
- ERR = 11 (division by zero error code)
- ERL = 40 (line where error occurred)
- RESUME NEXT skips the error, continues loop

### Example 5: Multiple Error Types

```basic
10 ON ERROR GOTO 1000
20 INPUT "Enter line number to jump to: ", L
30 GOTO L
40 END

1000 REM Error handler
1010 PRINT "Error "; ERR; " occurred"
1020 IF ERR = 8 THEN PRINT "Line does not exist": RESUME 20
1030 IF ERR = 6 THEN PRINT "Overflow": RESUME 20
1040 PRINT "Unknown error": END
```

**Explanation:**
- Handles multiple error types
- ERR = 8: Undefined line number
- ERR = 6: Overflow
- Different RESUME behavior based on error type

## Error Codes Reference

Common error codes used with RESUME:

| ERR | Error |
|-----|-------|
| 2 | Syntax error |
| 6 | Overflow |
| 11 | Division by zero |
| 13 | Type mismatch |
| 53 | File not found |
| 55 | File already open |
| 57 | Device I/O error |
| 62 | Input past end of file |

See [Error Codes](../../appendices/error-codes.md) for complete list.

## Testing RESUME

Test file: `tests/test_resume.bas`, `tests/test_resume2.bas`, `tests/test_resume3.bas`

Verified behavior against real MBASIC 5.21:
- ✅ RESUME retries error line
- ✅ RESUME NEXT skips to next statement
- ✅ RESUME <line number> jumps to specified line
- ✅ ERR and ERL variables work correctly
- ✅ "RESUME without error" when used outside error handler

## See Also

- [ON ERROR GOTO](on-error-goto.md) - Set up error handler
- [ERR and ERL Variables](err-erl-variables.md) - Error information
- [ERROR](error.md) - Simulate errors for testing
