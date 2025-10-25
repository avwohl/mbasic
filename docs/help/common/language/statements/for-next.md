# FOR ••• NEXT

## Syntax

```basic
FOR <variable>=x TO y [STEP z]
NEXT [<variable>] [,<variable> ••• ]
where x, y and z are numeric expressions.
```

**Versions:** SK, Extended, Disk

## Purpose

To allow a series of instructions        to         be performed in a loop a given number of times.

## Remarks

<variable> is used as a counter.      The first numeric expression (x) is the initial value of the counter. The second numeric expression (y) is the final value of the counter. The program lines following the FOR statement are executed until the NEXT statement is encountered. Then the counter is incremented by       the   amount specified by STEP. A check is performed to see if the value of the counter is now greater than the final value (y).       If it is not greater, BASIC-SO branches back to the statement after the FOR· statement and the process is repeated. If it is greater, execution continues with the statement following the NEXT statement. This is a FOR ••• NEXT loop. If STEP is not specified, the increment is assumed to be one. If STEP is negative, the final value of the counter is set to be less than the initial value. The counter is decremented each time through the loop, and the loop is executed until the counter is less than the final value. The body of the loop is skipped if the initial value of the loop times the sign of the step exceeds the final value times the sign of the step. Nested Loops FOR ••• NEXT loops may be nested, that is, a FOR ••• NEXT loop may be placed within the context of another FOR ••• NEXT loop.    When loops are nested, each loop must have a unique variable name as its counter. The NEXT statement for the inside loop must appear before that for the outside loop. If nested loops have the same end point, a single NEXT statement may be used for all of them. The variable(s) in the    NEXT   statement    may   be BASIC-SO COMMANDS AND STATEMENTS                    Page 2-30 omitted, in which case the NEXT statement will match the most recent FOR statement. If a NEXT statement     is    encountered    before  its corresponding FOR statement, a "NEXT without FOR" error message is issued and execution is terminated. Example 1:   10 1(=10 20 FOR I=l TO I( STEP 2 30 PRINT I; 40 1(=1(+10 50 PRINT I( 60 NEXT RUN 1 20 3 30 5 40 7 50 9 60 Ok Example 2:   10 J-O 20 FOR I=l TO J 30 PRINT I 40 NEXT I In this example, the loop does( not execute because the initial value of the loop exceeds the final value. Example 3:   10 I=5 20 FOR I=l TO I+5 30 PRINT I; 40 NEXT RUN 1 2 3 4 5 6        7     8   9   10 Ok In this example, the loop executes ten times. The final value for the loop variable is always set before the initial value is set.     (Note: Previous versions of BASIC-SO set the initial value of the loop variable before setting the final value;    i.e., the above loop would have executed six times.) BASIC-SO COMMANDS AND STATEMENTS                       Page 2-31

## See Also

*Related statements will be linked here*
