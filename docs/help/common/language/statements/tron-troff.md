# TRON/TROFF

## Syntax

```basic
TRON
TROFF
```

## Purpose

To trace the execution of program statements.

## Remarks

As an aid in debugging, the TRON statement (executed in either the direct or indirect mode) enables a trace flag that prints each line number of the program as it is executed. The numbers appear enclosed in square brackets. The trace flag is disabled with the TROFF statement (or when a NEW command is executed).

## Example

```basic
TRON
             Ok
             LIST
             10 K=lO
             20 FOR J=l TO 2
             30 L=K + 10
             40 PRINT J~K~L
             50 K=K+lO
             60 NEXT
             70 END
             Ok
             RUN
             [10] [20] [30] [40] 1   10   20
             [50] [60] [30] [40] 2   20   30
             [50] [60] [70]
             Ok
             TROFF
             Ok
BASIC-80 COMMANDS AND STATEMENTS                       Page 2-81
```

## See Also

*Related statements will be linked here*
