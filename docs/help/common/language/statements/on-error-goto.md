# ON ERROR GOTO

## Syntax

```basic
ON ERROR GOTO <line number>
```

## Purpose

To enable error trapping and specify the   first line of the error handling subroutine.

## Remarks

Once error trapping has been enabled all errors detected, including direct mode errors (e.g., Syntax errors), will cause a jump to         the specified error handling subroutine. If <line number> does not exist, an "Undefined line" error   results.   To disable error trapping, execute an ON ERROR ~TO O.    Subsequent errors will print an error message and halt execution. An ON ERROR GOTO 0 statement that appears in an error trapping subroutine causes BASIC-SO to stop and print the error message for the error that caused the trap.     It is recommended that all error trapping subroutines execute an ON ERROR GOTO 0 if an error is encountered for which there is no recovery action. NOTE:         If an error occurs during execution of an error handling subroutine, the BASIC error message is printed   and   execution   terminates.   Error trapping   does   not occur within the error handling subroutine.

## Example

```basic
10 ON ERROR GOTO 1000
BASIC-SO COMMANDS AND STATEMENTS                      Page 2-55
```

## See Also

*Related statements will be linked here*
