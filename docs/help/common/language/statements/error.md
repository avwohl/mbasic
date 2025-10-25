# ERROR

## Syntax

```basic
ERROR <integer expression>
```

**Versions:** Extend~d,   Disk

## Purpose

1) To simulate the occurrence of a BASIC-80 error1   or 2) to allow error codes to be defined by the user.

## Remarks

The value of <integer expression> must        be greater than 0 and less than 255. If the value of <integer expression> equals an error code already in use by BASIC-80 (see Appendix J), the ERROR statement will simulate the occurrence of that error, and the corresponding error message will be printed. (See Example 1.) To define your own error code, use a value that is greater than any used by BASIC-80~s error codes. (It is preferable to use the highest available   values,    so compatibility may be maintained when more error codes are added to BASIC-80.) This user-defined error code may then be conveniently handled in an       error   trap routine. (Se..e Example 2.) If an ERROR statement specifies a CQcle for which no error message has been defined, BASIC-80 responds with the message UNPRINTABLE ERROR. Execution of an ERROR statement for which there is no error trap routine causes an error message to be printed and execution to halt. Example 1:     LIST 10 S = 10 20 T = 5 30 ERROR S + T 40 END Ok RUN String too long in line 30 Or, in direct mode: Ok ERROR 15              (you type this line) String too long       (BASIC-80 types this line) Ok BASIC-SO COMMANDS AND STATEMENTS                    Page 2-27 Example 2: . 110 ON ERROR GOTO 400 120 INPUT "WHAT IS YOUR BET";B 130 IF B > 5000 THEN ERROR 210 400 IF ERR = 210 THEN PRINT "HOUSE LIMIT IS $5000" 410 IF ERL = 130 THEN RESUME 120 BASIC-80 COMMANDS AND STATEMENTS                     Page 2-28

## See Also

*Related statements will be linked here*
