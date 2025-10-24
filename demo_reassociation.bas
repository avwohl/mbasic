10 REM ================================================================
20 REM Expression Reassociation Optimization Demo
30 REM ================================================================
40 REM
50 REM This demonstrates how the compiler optimizes associative
60 REM expressions by grouping constants together.
70 REM
80 REM The semantic analyzer automatically:
90 REM   1. Detects chains of + or * operations
100 REM   2. Collects all constants and non-constants
110 REM   3. Folds constants into a single value
120 REM   4. Rebuilds the expression optimally
130 REM
140 REM ================================================================
150 REM Example 1: Simple Addition Chain
160 REM ================================================================
170 PRINT "Example 1: Addition Chain"
180 A = 100
190 B = (A + 5) + 10
200 PRINT "  (A + 5) + 10 where A = 100"
210 PRINT "  Optimized to: A + 15"
220 PRINT "  Result: B ="; B
230 PRINT
240 REM
250 REM ================================================================
260 REM Example 2: Simple Multiplication Chain
270 REM ================================================================
280 PRINT "Example 2: Multiplication Chain"
290 C = (A * 2) * 3
300 PRINT "  (A * 2) * 3 where A = 100"
310 PRINT "  Optimized to: A * 6"
320 PRINT "  Result: C ="; C
330 PRINT
340 REM
350 REM ================================================================
360 REM Example 3: Long Addition Chain
370 REM ================================================================
380 PRINT "Example 3: Long Addition Chain"
390 D = 1 + A + 2 + 3 + 4
400 PRINT "  1 + A + 2 + 3 + 4 where A = 100"
410 PRINT "  Optimized to: A + 10"
420 PRINT "  Result: D ="; D
430 PRINT
440 REM
450 REM ================================================================
460 REM Example 4: Long Multiplication Chain
470 REM ================================================================
480 PRINT "Example 4: Long Multiplication Chain"
490 E = 2 * A * 3 * 5
500 PRINT "  2 * A * 3 * 5 where A = 100"
510 PRINT "  Optimized to: A * 30"
520 PRINT "  Result: E ="; E
530 PRINT
540 REM
550 REM ================================================================
560 REM Example 5: Real-World Use Case - Array Indexing
570 REM ================================================================
580 PRINT "Example 5: Array Indexing Optimization"
590 DIM ARR(1000)
600 I = 10
610 REM Calculate index: (base + offset1) + offset2
620 IDX = (I * 10 + 5) + 15
630 PRINT "  Index = (I * 10 + 5) + 15 where I = 10"
640 PRINT "  Optimized to: I * 10 + 20"
650 PRINT "  Index ="; IDX
660 PRINT
670 REM
680 REM ================================================================
690 REM Example 6: Real-World Use Case - Physics Calculation
700 REM ================================================================
710 PRINT "Example 6: Physics - Distance Calculation"
720 V = 25: REM velocity
730 T = 10: REM time
740 REM Distance = (velocity * time * 3600) * conversion_factor
750 REM where 3600 = seconds/hour and 0.001 = km/m conversion
760 D = (V * T * 3600) * 0.001
770 PRINT "  D = (V * T * 3600) * 0.001"
780 PRINT "  Optimized to: V * T * 3.6"
790 PRINT "  Distance ="; D; "km"
800 PRINT
810 REM
820 REM ================================================================
830 PRINT "Optimization complete!"
840 PRINT "The compiler groups constants together to minimize"
850 PRINT "runtime calculations and improve performance."
860 END
