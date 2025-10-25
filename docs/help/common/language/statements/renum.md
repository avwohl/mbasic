# RENUM

## Syntax

```basic
RENUM [[<new number>] [,[<old number>] [,<increment>]]]
RESTORE [<line number>]
```

**Versions:** Extended, Disk 8K, Extended, Disk

## Purpose

To renumber program lines. To allow DATA statements to   be   reread     from   a specified line.

## Remarks

<new number> is the first line number to be used in the new sequence. The default is 10. <old number> is the line in the current program where renumbering is to begin.      The default is the first line of the program. <increment> is the increment to be used in the new sequence. The default is 10. RENUM also changes all line number references following      GOTO,   GOSUB,   THEN,   ON ••• GOTO, ON ••• GOSUB and ERL statements to reflect the new line numbers.      If a nonexistent line number appears after one of these statements, the error message "Undefined line xxxxx in yyyyy" is printed. The incorrect line number reference (xxxxx) is not changed by RENUM, but line number yyyyy may be changed. NOTE:           RENUM cannot be used to change the order of program lines (for example, RENUM 15,30 when the program has three lines numbered 10, 20 and 30) or to create line numbers greater than 65529. An "Illegal function call" error will result. After a RESTORE statement is executed, the next READ statement accesses the first item in the first DATA statement in the program.   If <line number> is specified, the next READ statement accesses the first item in the specified DATA statement.

## Example

```basic
RENUM               Renumbers the entire program.
                                    The first new line number
                                    will be 10. Lines will
                                    increment by 10.
                RENUM 300,,50       Renumbers the entire pro-
                                    gram. The first new line
                                    number will be 300. Lines
                                    will increment by 50.
                RENUM 1000,900,20   Renumbers the lines from
                                    900 up so they start with
                                    line number 1000 and
                                    increment by 20.
BASIC-80 COMMANDS AND STATEMENTS                           Page 2-74
2 • 57   RESTORE
10 READ A,B,C
               20 RESTORE
               30 READ D,E,F
               40 DATA 57, 68, 79
BASIC-80 COMMANDS AND STATEMENTS                         Page 2-75
```

## See Also

*Related statements will be linked here*
