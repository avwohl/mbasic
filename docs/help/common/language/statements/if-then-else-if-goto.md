---
category: control-flow
description: Make decisions and control program flow based on conditional expressions
keywords:
- if
- then
- else
- goto
- condition
- test
- decision
- branch
- nested
aliases: [if-then, if-goto, if-then-else]
syntax: "IF expression THEN statement|line_number [ELSE statement|line_number]"
related: [while-wend, for-next, goto, on-goto]
title: IF ••• THEN[ ••• ELSE] AND IF ••• GOTO
type: statement
---

# IF ••• THEN[ ••• ELSE] AND IF ••• GOTO

## Syntax

```basic
IF <expression> THEN <statement(s»          <line number>
,
[ELSE <statement(s)>     I <line number>]
IF <expression> GOTO <line number>
[ELSE <statement(s)>     I <line number>]
```

**Versions:** SK, Extended, Disk NOTE:          The ELSE clause is allowed only in Extended        and Disk versions.

## Purpose

To make a decision regarding program flow       based on the result returned by an expression.

## Remarks

If the result of <expression> is not zero, the THEN or GOTO clause is executed. THEN may be followed by either a line number for branching or one or more statements to be executed. GOTO is always followed by a line number.     If the result of <expression> is zero, the THEN or GOTO clause is ignored and the ELSE clause, if present, is executed. Execution continues with the next executable statement.  (ELSE is allowed only -in Extended and Disk versions.) Extended and Disk versions allow a comma before THEN. Nesting of IF Statements In     the      Extended    and   Disk   versions, IF ••• THEN ••• ELSE   statements  may be nested. Nesting is limited only by the length of the line. For example IF X>Y THEN PRINT "GREATER" ELSE IF Y>X THEN PRINT "LESS THAN" ELSE PRINT "EQUAL" is a legal statement. If the statement does not contain   the same number of ELSE and THEN clauses, each ELSE is matched with the closest unmatched THEN. For example IF A=B THEN IF B=C THEN PRINT "A=C" ELSE PRINT "A<>C" will not print nA<>C" when A<>B. If an IF ••• THEN statement is followed by a line number in the direct mode, an "Undefined line" error results unless a statement with         the specified     line    number had previously been entered in the indirect mode. BASIC-SO COMMANDS AND STATEMENTS                     Page 2-35 NOTE:        When using IF to test equality for a value that is the result of a floating point computation, remember that the internal representation of the value may not be exact. Therefore, the test should be against the' range over which the accuracy of the value may vary. For example, to test a computed variable 'A against the value 1.0, use: IF ABS (A-1.0)<1.0E-6 THEN ••• This test returns true if the value of A is   1.0 with a relative error of less than 1.OE-6. Example 1:   200 IF I THEN GETt1,I This statement GETs record number I if I is   not zero. Example 2:   100 IF(I<20)*(I>10) THEN DB=1979-1:GOTO 300 110 PRINT "OUT OF RANGE" In this example, a test determines if I     is greater than 10 and less than 20. If I is in this range, DB is calculated and execution branches to line 300.      If I is not in this range, execution continues with line 110. Example 3:   210 IF IOFLAG THEN PRINT A$ ELSE LPRINT A$ This statement causes printed output to go either to the terminal or the line printer, depending on the value of a variable    (IOFLAG). If I OF LAG is zero, output goes to the line printer, otherwise output goes to the terminal. BASIC-80 COMMANDS AND STATEMENTS                           Page 2-36

## See Also

*Related statements will be linked here*