---
category: error-handling
description: 1) To simulate the occurrence of a BASIC-80 error1   or 2) to allow error codes to be defined by the user
keywords: ['command', 'error', 'for', 'goto', 'if', 'input', 'line', 'print', 'put', 'read']
syntax: ERROR <integer expression>
title: ERROR
type: statement
---

# ERROR

## Syntax

```basic
ERROR <integer expression>
```

**Versions:** Extend~d,   Disk

## Purpose

1) To simulate the occurrence of a BASIC-80 error1   or 2) to allow error codes to be defined by the user.

## Remarks

The ERROR statement simulates an error condition, triggering error handling as if a real error occurred.

### Parameters:
- **integer expression** - The error code to simulate (1-255)

### Standard Error Codes:
- Codes 1-255 are predefined BASIC error codes
- The error will trigger ON ERROR GOTO if active
- ERR variable will contain the error code
- ERL variable will contain the line number where ERROR was executed

### Custom Error Codes:
You can use ERROR with custom codes (typically > 200) to implement your own error handling for application-specific conditions.

### Example:
```basic
10 ON ERROR GOTO 1000
20 IF X < 0 THEN ERROR 200  ' Custom error
30 PRINT SQR(X)
...
1000 IF ERR = 200 THEN PRINT "Negative number not allowed"
1010 RESUME NEXT
```

## See Also
- [ON ERROR GOTO](on-error-goto.md) - To enable error trapping and specify the   first line of the error handling subroutine
- [RESUME](resume.md) - Continue program execution after error recovery
