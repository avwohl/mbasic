10 REM ================================================================
20 REM COMPREHENSIVE OPTIMIZATION DEMONSTRATION
30 REM Showcases all 18 compiler optimizations
40 REM ================================================================
50 REM
60 REM This program demonstrates every optimization implemented in
70 REM the MBASIC compiler's semantic analysis phase.
80 REM
90 REM Run with: python3 mbasic demo_all_optimizations.bas
100 REM
110 REM ================================================================
120 REM OPTIMIZATION 1: Constant Folding
130 REM ================================================================
140 PRINT "1. Constant Folding"
150 X = 10 + 20 * 3
160 REM Compiler evaluates: 10 + 60 = 70 at compile time
170 PRINT "  X = 10 + 20 * 3 ="; X
180 PRINT
190 REM
200 REM ================================================================
210 REM OPTIMIZATION 2: Runtime Constant Propagation
220 REM ================================================================
230 PRINT "2. Runtime Constant Propagation"
240 N = 10
250 REM Compiler knows N=10 here, propagates into DIM
260 DIM A(N)
270 PRINT "  DIM A(N) where N=10 - propagated!"
280 PRINT
290 REM
300 REM ================================================================
310 REM OPTIMIZATION 3: Common Subexpression Elimination (CSE)
320 REM ================================================================
330 PRINT "3. Common Subexpression Elimination"
340 A = 5: B = 10
350 X = A + B
360 Y = A + B
370 REM Compiler detects A+B computed twice
380 PRINT "  X = A + B, then Y = A + B"
390 PRINT "  CSE opportunity: compute once, reuse"
400 PRINT
410 REM
420 REM ================================================================
430 REM OPTIMIZATION 4: Subroutine Side-Effect Analysis
440 REM ================================================================
450 PRINT "4. Subroutine Side-Effect Analysis"
460 C = 100
470 GOSUB 2000
480 REM Compiler knows subroutine doesn't modify C
490 REM So C+C can be CSE'd before and after GOSUB
500 PRINT "  Subroutine analyzed for side effects"
510 PRINT
520 REM
530 REM ================================================================
540 REM OPTIMIZATION 5: Loop Analysis
550 REM ================================================================
560 PRINT "5. Loop Analysis (FOR, WHILE, IF-GOTO)"
570 PRINT "  FOR loop with 5 iterations:"
580 FOR I = 1 TO 5
590   PRINT "    Iteration"; I
600 NEXT I
610 REM Compiler calculates iteration count = 5
620 REM Marks as candidate for unrolling
630 PRINT
640 REM
650 REM ================================================================
660 REM OPTIMIZATION 6: Loop-Invariant Code Motion
670 REM ================================================================
680 PRINT "6. Loop-Invariant Code Motion"
690 A = 10: B = 20
700 FOR I = 1 TO 5
710   X = A * B
720   REM Compiler detects A*B doesn't change in loop
730   REM Can be hoisted outside loop
740 NEXT I
750 PRINT "  A*B is loop-invariant - hoist outside"
760 PRINT
770 REM
780 REM ================================================================
790 REM OPTIMIZATION 7: Multi-Dimensional Array Flattening
800 REM ================================================================
810 PRINT "7. Multi-Dimensional Array Flattening"
820 DIM M(5, 3)
830 M(2, 1) = 42
840 REM Compiler transforms M(2,1) to M(2*4 + 1) = M(9)
850 PRINT "  M(2,1) flattened to 1D index"
860 PRINT "  Value stored: 42"
870 PRINT
880 REM
890 REM ================================================================
900 REM OPTIMIZATION 8: Dead Code Detection
910 REM ================================================================
920 PRINT "8. Dead Code Detection"
930 IF 0 THEN GOTO 960
940 PRINT "  Code after always-false condition"
950 GOTO 970
960 PRINT "  This line is dead code (unreachable)"
970 PRINT
980 REM
990 REM ================================================================
1000 REM OPTIMIZATION 9: Strength Reduction
1010 REM ================================================================
1020 PRINT "9. Strength Reduction"
1030 N = 5
1040 RESULT = N * 2
1050 REM Compiler transforms N*2 to N+N (addition cheaper)
1060 PRINT "  N * 2 reduced to N + N ="; RESULT
1070 PRINT
1080 REM
1090 REM ================================================================
1100 REM OPTIMIZATION 10: Copy Propagation
1110 REM ================================================================
1120 PRINT "10. Copy Propagation"
1130 SRC = 100
1140 DEST = SRC
1150 RESULT = DEST + 1
1160 REM Compiler can use SRC directly in line 1150
1170 PRINT "  DEST = SRC, then use DEST"
1180 PRINT "  Propagates SRC ="; RESULT
1190 PRINT
1200 REM
1210 REM ================================================================
1220 REM OPTIMIZATION 11: Algebraic Simplification
1230 REM ================================================================
1240 PRINT "11. Algebraic Simplification"
1250 X = 5
1260 Y = X * 1
1270 REM Compiler simplifies X*1 to X
1280 Z = X + 0
1290 REM Compiler simplifies X+0 to X
1300 PRINT "  X * 1 simplified to X"
1310 PRINT "  X + 0 simplified to X"
1320 PRINT
1330 REM
1340 REM ================================================================
1350 REM OPTIMIZATION 12: Induction Variable Optimization
1360 REM ================================================================
1370 PRINT "12. Induction Variable Optimization"
1380 DIM ARR(100)
1390 FOR I = 1 TO 10
1400   ARR(I * 2) = I
1410   REM Compiler detects I*2 pattern
1420   REM Can use pointer arithmetic instead
1430 NEXT I
1440 PRINT "  I*2 in array subscript optimized"
1450 PRINT
1460 REM
1470 REM ================================================================
1480 REM OPTIMIZATION 13: OPTION BASE Support
1490 REM ================================================================
1500 PRINT "13. OPTION BASE Support"
1510 REM OPTION BASE 1 would make arrays start at 1
1520 REM Compiler handles both BASE 0 and BASE 1
1530 PRINT "  Supports OPTION BASE 0 and 1"
1540 PRINT
1550 REM
1560 REM ================================================================
1570 REM OPTIMIZATION 14: Expression Reassociation
1580 REM ================================================================
1590 PRINT "14. Expression Reassociation"
1600 X = 5: Y = 10
1610 RESULT = X + Y + 100 + 200
1620 REM Compiler regroups: X + Y + (100 + 200)
1630 REM Then folds: X + Y + 300
1640 PRINT "  X+Y+100+200 reassociated for folding"
1650 PRINT "  Result ="; RESULT
1660 PRINT
1670 REM
1680 REM ================================================================
1690 REM OPTIMIZATION 15: Boolean Simplification
1700 REM ================================================================
1710 PRINT "15. Boolean Simplification"
1720 A = 10: B = 20
1730 IF NOT(A > B) THEN PRINT "  NOT(A > B) simplified to A <= B"
1740 PRINT
1750 REM
1760 REM ================================================================
1770 REM OPTIMIZATION 16: Forward Substitution
1780 REM ================================================================
1790 PRINT "16. Forward Substitution"
1800 A = 10: B = 20
1810 TEMP = A + B
1820 PRINT "  TEMP ="; TEMP
1830 REM Compiler detects TEMP used once
1840 REM Can substitute A+B directly
1850 PRINT "  Single-use temp can be eliminated"
1860 PRINT
1870 REM
1880 REM ================================================================
1890 REM OPTIMIZATION 17: Branch Optimization
1900 REM ================================================================
1910 PRINT "17. Branch Optimization"
1920 IF 1 THEN PRINT "  Always-true branch detected"
1930 IF 0 THEN PRINT "  This won't execute"
1940 PRINT
1950 REM
1960 REM ================================================================
1970 REM OPTIMIZATION 18: Uninitialized Variable Detection
1980 REM ================================================================
1990 PRINT "18. Uninitialized Variable Detection"
2000 PRINT "  Warns about use-before-assignment"
2010 PRINT "  (See compiler analysis report)"
2020 PRINT
2030 REM
2040 REM ================================================================
2050 PRINT "All 18 optimizations demonstrated!"
2060 PRINT
2070 PRINT "Run semantic analysis to see optimization report:"
2080 PRINT "  - Constant folding opportunities"
2090 PRINT "  - CSE detections"
2100 PRINT "  - Loop analysis results"
2110 PRINT "  - Strength reductions"
2120 PRINT "  - And much more!"
2130 END
2140 REM
2150 REM ================================================================
2160 REM Subroutine for GOSUB demonstration (doesn't modify C)
2170 REM ================================================================
2000 PRINT "  Inside subroutine"
2010 RETURN
