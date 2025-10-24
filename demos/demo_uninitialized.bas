10 REM ================================================================
20 REM Uninitialized Variable Detection Demo
30 REM ================================================================
40 REM
50 REM This demonstrates the compiler's ability to detect variables
60 REM that are used before being assigned a value.
70 REM
80 REM Even though BASIC defaults all variables to 0, using a variable
90 REM before initialization can indicate:
100 REM   - Typos in variable names
110 REM   - Logic errors
120 REM   - Missing initialization code
130 REM
140 REM ================================================================
150 REM Example 1: Simple uninitialized use
160 REM ================================================================
170 PRINT "Example 1: Uninitialized variable"
180 PRINT "Value of X before assignment:"; X
190 REM The compiler will warn: X used before assignment
200 X = 10
210 PRINT "Value of X after assignment:"; X
220 PRINT
230 REM
240 REM ================================================================
250 REM Example 2: Initialized variable - no warning
260 REM ================================================================
270 PRINT "Example 2: Properly initialized"
280 Y = 20
290 PRINT "Value of Y:"; Y
300 PRINT
310 REM
320 REM ================================================================
330 REM Example 3: FOR loop - automatically initialized
340 REM ================================================================
350 PRINT "Example 3: FOR loop (automatically initialized)"
360 FOR I = 1 TO 3
370 PRINT "Loop variable I:"; I
380 NEXT I
390 PRINT
400 REM
410 REM ================================================================
420 REM Example 4: INPUT statement - initializes variable
430 REM ================================================================
440 REM PRINT "Example 4: INPUT statement"
450 REM INPUT "Enter a number: ", NUM
460 REM PRINT "You entered:"; NUM
470 REM PRINT
480 REM
490 REM ================================================================
500 REM Example 5: Expression with uninitialized variable
510 REM ================================================================
520 PRINT "Example 5: Uninitialized in expression"
530 A = 5
540 B = A + C
550 REM The compiler will warn: C used before assignment
560 PRINT "A ="; A; ", B ="; B; ", C ="; C
570 C = 15
580 PRINT "After initializing C:"; C
590 PRINT
600 REM
610 REM ================================================================
620 PRINT "Demo complete!"
630 PRINT "Check the compiler warnings to see uninitialized variable detection."
640 END
