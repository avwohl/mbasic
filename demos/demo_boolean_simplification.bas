10 REM ================================================================
20 REM Boolean Simplification Optimization Demo
30 REM ================================================================
40 REM
50 REM This demonstrates how the compiler simplifies Boolean and
60 REM relational expressions for more efficient code generation.
70 REM
80 REM The semantic analyzer automatically:
90 REM   1. Inverts relational operators to eliminate NOT
100 REM   2. Applies De Morgan's laws to distribute NOT
110 REM   3. Applies absorption laws to eliminate redundancy
120 REM
130 REM ================================================================
140 REM Example 1: Relational Operator Inversion
150 REM ================================================================
160 PRINT "Example 1: Relational Operator Inversion"
170 PRINT
180 A = 10
190 B = 20
200 IF NOT(A > B) THEN PRINT "  NOT(A > B) optimized to A <= B"
210 IF NOT(A < B) THEN PRINT "  NOT(A < B) optimized to A >= B"
220 IF NOT(A = B) THEN PRINT "  NOT(A = B) optimized to A <> B"
230 PRINT
240 REM
250 REM ================================================================
260 REM Example 2: De Morgan's Laws
270 REM ================================================================
280 PRINT "Example 2: De Morgan's Laws"
290 PRINT
300 X = 1: Y = 0
310 REM NOT(X AND Y) becomes (NOT X) OR (NOT Y)
320 IF NOT(X AND Y) THEN PRINT "  NOT(X AND Y) -> (NOT X) OR (NOT Y)"
330 REM NOT(X OR Y) becomes (NOT X) AND (NOT Y)
340 IF NOT(X OR Y) THEN PRINT "  NOT(X OR Y) would be (NOT X) AND (NOT Y)"
350 PRINT
360 REM
370 REM ================================================================
380 REM Example 3: Absorption Laws
390 REM ================================================================
400 PRINT "Example 3: Absorption Laws"
410 PRINT
420 A = 1: B = 1: C = 0
430 REM (A OR B) AND A simplifies to just A
440 RESULT1 = (A OR B) AND A
450 PRINT "  (A OR B) AND A -> A ="; RESULT1
460 REM A OR (A AND B) simplifies to just A
470 RESULT2 = A OR (A AND B)
480 PRINT "  A OR (A AND B) -> A ="; RESULT2
490 REM (A AND B) OR A simplifies to just A
500 RESULT3 = (A AND B) OR A
510 PRINT "  (A AND B) OR A -> A ="; RESULT3
520 REM A AND (A OR B) simplifies to just A
530 RESULT4 = A AND (A OR B)
540 PRINT "  A AND (A OR B) -> A ="; RESULT4
550 PRINT
560 REM
570 REM ================================================================
580 REM Example 4: Real-World Use - Complex Conditionals
590 REM ================================================================
600 PRINT "Example 4: Real-World Conditional Simplification"
610 PRINT
620 MIN = 0
630 MAX = 100
640 VALUE = 50
650 REM Check if value is out of range
660 REM NOT(VALUE >= MIN AND VALUE <= MAX)
670 REM Gets optimized via De Morgan:
680 REM (NOT (VALUE >= MIN)) OR (NOT (VALUE <= MAX))
690 REM Which then becomes: (VALUE < MIN) OR (VALUE > MAX)
700 IF NOT(VALUE >= MIN AND VALUE <= MAX) THEN PRINT "  Value out of range": GOTO 760
710 PRINT "  Value in range: optimized to"
720 PRINT "  (VALUE < MIN) OR (VALUE > MAX)"
760 PRINT
770 REM
780 REM ================================================================
790 REM Example 5: Combined with Other Optimizations
800 REM ================================================================
810 PRINT "Example 5: Combined Optimizations"
820 PRINT
830 A = 5
840 B = 10
850 REM Multiple optimizations: NOT inversion + constant folding
860 IF NOT(A + 5 > B) THEN PRINT "  NOT(A + 5 > B)": PRINT "  -> NOT(10 > 10)  [constant folding]": PRINT "  -> 10 <= 10      [NOT inversion]": PRINT "  -> TRUE          [constant evaluation]": PRINT "  Condition is TRUE"
930 PRINT
940 REM
950 REM ================================================================
960 PRINT "All Boolean simplifications applied!"
970 PRINT "The compiler eliminates NOT operations and redundancy"
980 PRINT "for cleaner, faster code generation."
990 END
