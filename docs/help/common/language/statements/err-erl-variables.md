---
category: error-handling
description: Error code and error line number variables used in error handling
keywords: ['erl', 'err', 'error', 'error handling', 'variable', 'variables']
title: ERR AND ERL VARIABLES
type: statement
---

# ERR AND ERL VARIABLES

## Syntax

```basic
ERR
ERL
```

## Description

ERR and ERL are special variables that contain information about the most recent error:

- **ERR** - Contains the error code of the most recent error (see Error Codes appendix)
- **ERL** - Contains the line number where the most recent error occurred

These variables are automatically set when an error occurs and can be used in error handling routines (ON ERROR GOTO).

## Remarks

- ERR and ERL are read-only variables
- They retain their values until the next error occurs
- ERR is reset to 0 when:
  - RESUME statement is executed
  - A new RUN command is issued
  - An error handling routine ends normally
- ERL returns 0 if the error occurred in direct mode (no line number)

## Example

```basic
10 ON ERROR GOTO 1000
20 INPUT "Enter a number: ", N
30 PRINT 100 / N
40 END
1000 PRINT "Error"; ERR; "occurred at line"; ERL
1010 IF ERR = 11 THEN PRINT "Division by zero!"
1020 RESUME NEXT
```

This example sets up an error handler that prints the error code and line number when an error occurs.

## See Also
- [ON ERROR GOTO](on-error-goto.md) - Set up error handling routine
- [RESUME](resume.md) - Continue program execution after error handling
- [ERROR](error.md) - Generate an error with specific code
- [Error Codes](../appendices/error-codes.md) - Complete list of error codes
