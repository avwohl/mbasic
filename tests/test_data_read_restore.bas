10 REM Comprehensive DATA/READ/RESTORE test
20 PRINT "=== DATA, READ, RESTORE Test ==="
30 PRINT
40 REM Test 1: Basic READ
50 PRINT "Test 1: Basic READ"
60 READ A, B, C
70 PRINT "  A="; A; "B="; B; "C="; C
80 DATA 10, 20, 30
90 PRINT
100 REM Test 2: READ strings
110 PRINT "Test 2: READ strings"
120 READ N$, C$
130 PRINT "  N$=["; N$; "] C$=["; C$; "]"
140 DATA "Alice", "NYC"
150 PRINT
160 REM Test 3: Mixed types
170 PRINT "Test 3: Mixed types"
180 READ X, Y$, Z
190 PRINT "  X="; X; "Y$=["; Y$; "] Z="; Z
200 DATA 100, "test", 200
210 PRINT
220 REM Test 4: RESTORE and re-read
230 PRINT "Test 4: RESTORE and re-read"
240 RESTORE
250 READ A1, B1, C1
260 PRINT "  After RESTORE: A1="; A1; "B1="; B1; "C1="; C1
270 PRINT
280 REM Test 5: Multiple DATA statements
290 PRINT "Test 5: Multiple DATA statements"
300 READ D, E, F, G
310 PRINT "  D="; D; "E="; E; "F="; F; "G="; G
320 DATA 1, 2
330 DATA 3, 4
340 PRINT
350 REM Test 6: DATA with quoted strings
360 PRINT "Test 6: Quoted strings in DATA"
370 READ S1$, S2$, S3$
380 PRINT "  S1$=["; S1$; "]"
390 PRINT "  S2$=["; S2$; "]"
400 PRINT "  S3$=["; S3$; "]"
410 DATA "Hello, World", "Test 123", "A,B,C"
420 PRINT
430 REM Test 7: DATA at different locations
440 PRINT "Test 7: DATA at different locations"
450 GOTO 490
460 DATA 77, 88, 99
470 GOTO 530
480 DATA "hidden"
490 READ V1, V2, V3
500 PRINT "  V1="; V1; "V2="; V2; "V3="; V3
510 PRINT
520 REM Test 8: RESTORE mid-program
530 PRINT "Test 8: RESTORE mid-program"
540 READ T1$
550 PRINT "  Before RESTORE: T1$=["; T1$; "]"
560 RESTORE
570 READ T2, T3, T4
580 PRINT "  After RESTORE: T2="; T2; "T3="; T3; "T4="; T4
590 PRINT
600 REM Test 9: Empty string in DATA
610 PRINT "Test 9: Empty string in DATA"
620 READ E1$, E2$, E3$
630 PRINT "  E1$=["; E1$; "] len="; LEN(E1$)
640 PRINT "  E2$=["; E2$; "] len="; LEN(E2$)
650 PRINT "  E3$=["; E3$; "] len="; LEN(E3$)
660 DATA "", "middle", ""
670 PRINT
680 REM Test 10: Numbers with decimals
690 PRINT "Test 10: Decimal numbers"
700 READ F1, F2, F3
710 PRINT "  F1="; F1; "F2="; F2; "F3="; F3
720 DATA 1.5, 2.75, 3.125
730 PRINT
740 REM Test 11: Negative numbers
750 PRINT "Test 11: Negative numbers"
760 READ N1, N2, N3
770 PRINT "  N1="; N1; "N2="; N2; "N3="; N3
780 DATA -10, -20, -30
790 PRINT
800 REM Test 12: Scientific notation
810 PRINT "Test 12: Scientific notation"
820 READ S1, S2
830 PRINT "  S1="; S1; "S2="; S2
840 DATA 1E5, 2.5E-3
850 PRINT
860 REM Test 13: Multiple RESTOREs
870 PRINT "Test 13: Multiple RESTOREs"
880 RESTORE
890 READ R1
900 RESTORE
910 READ R2
920 RESTORE
930 READ R3
940 PRINT "  R1="; R1; "R2="; R2; "R3="; R3
950 PRINT
960 REM Test 14: Strings with special chars
970 PRINT "Test 14: Strings with numbers"
980 READ SP1$, SP2$
990 PRINT "  SP1$=["; SP1$; "]"
1000 PRINT "  SP2$=["; SP2$; "]"
1010 DATA "123", "456"
1020 PRINT
1030 PRINT "=== All DATA/READ/RESTORE tests complete ==="
1040 END
