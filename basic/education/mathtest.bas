10 REM Math Precision Test Suite
20 REM Tests float vs double precision across function ranges
30 REM Focus on trig functions known for poor accuracy in MBASIC
40 PRINT "MBASIC Math Precision Test Suite"
50 PRINT "=================================="
60 PRINT
100 REM Test ATN (arctangent) - notorious for poor accuracy
110 PRINT "ATN (Arctangent) Tests:"
120 PRINT "Input", "ATN(x)", "Expected (approx)"
130 PRINT "-----", "------", "----------------"
140 REM Test points covering full range
150 FOR I = 1 TO 20
160   READ X
170   Y = ATN(X)
180   PRINT X, Y
190 NEXT I
200 PRINT
210 DATA 0, 0.1, 0.5, 0.7071068, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0
220 DATA -0.1, -0.5, -1.0, -2.0, -10.0, 0.0001, 0.001, 100.0, 1000.0, 0.00001
300 REM Test SIN (sine) at critical points
310 PRINT "SIN Tests:"
320 PRINT "Input (rad)", "SIN(x)", "Expected"
330 PRINT "----------", "------", "--------"
340 FOR I = 1 TO 15
350   READ X
360   Y = SIN(X)
370   PRINT X, Y
380 NEXT I
390 PRINT
400 DATA 0, 0.523599, 0.785398, 1.0472, 1.5708, 2.0944, 3.14159
410 DATA -0.785398, -1.5708, 6.28319, 0.1, 0.01, 0.001, 3.0, 4.0
500 REM Test COS (cosine) at critical points
510 PRINT "COS Tests:"
520 PRINT "Input (rad)", "COS(x)", "Expected"
530 PRINT "----------", "------", "--------"
540 FOR I = 1 TO 15
550   READ X
560   Y = COS(X)
570   PRINT X, Y
580 NEXT I
590 PRINT
600 DATA 0, 0.523599, 0.785398, 1.0472, 1.5708, 2.0944, 3.14159
610 DATA -0.785398, -1.5708, 6.28319, 0.1, 0.01, 0.001, 3.0, 4.0
700 REM Test TAN (tangent) - prone to errors near asymptotes
710 PRINT "TAN Tests:"
720 PRINT "Input (rad)", "TAN(x)"
730 PRINT "----------", "------"
740 FOR I = 1 TO 12
750   READ X
760   Y = TAN(X)
770   PRINT X, Y
780 NEXT I
790 PRINT
800 DATA 0, 0.785398, 0.523599, 1.0472, -0.785398, 0.1, 0.01
810 DATA 1.0, 1.5, 0.001, 3.0, 0.5
900 REM Test EXP (exponential)
910 PRINT "EXP Tests:"
920 PRINT "Input", "EXP(x)"
930 PRINT "-----", "------"
940 FOR I = 1 TO 15
950   READ X
960   Y = EXP(X)
970   PRINT X, Y
980 NEXT I
990 PRINT
1000 DATA 0, 1, 2, 3, 5, 10, -1, -2, -5, -10
1010 DATA 0.5, 0.1, 0.01, 15, 20
1100 REM Test LOG (natural logarithm)
1110 PRINT "LOG Tests:"
1120 PRINT "Input", "LOG(x)"
1130 PRINT "-----", "------"
1140 FOR I = 1 TO 15
1150   READ X
1160   Y = LOG(X)
1170   PRINT X, Y
1180 NEXT I
1190 PRINT
1200 DATA 1, 2, 10, 100, 1000, 0.5, 0.1, 0.01, 0.001
1210 DATA 2.71828, 7.389056, 0.367879, 1.648721, 20.085537, 54.59815
1300 REM Test SQR (square root)
1310 PRINT "SQR Tests:"
1320 PRINT "Input", "SQR(x)"
1330 PRINT "-----", "------"
1340 FOR I = 1 TO 12
1350   READ X
1360   Y = SQR(X)
1370   PRINT X, Y
1380 NEXT I
1390 PRINT
1400 DATA 0, 1, 2, 4, 9, 16, 25, 100, 1000, 0.25, 0.5, 10000
1500 REM Test compound expressions prone to rounding errors
1510 PRINT "Compound Expression Tests:"
1520 PRINT "============================"
1530 PRINT
1540 REM ATN identity: ATN(1/x) + ATN(x) = PI/2 for x > 0
1550 PRINT "ATN Identity Test: ATN(1/x) + ATN(x) should = 1.5708 (PI/2)"
1560 FOR I = 1 TO 8
1570   READ X
1580   Y = ATN(1/X) + ATN(X)
1590   PRINT "x="; X, "Result="; Y, "Error="; ABS(Y - 1.5708)
1600 NEXT I
1610 PRINT
1620 DATA 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 100.0, 0.1
1700 REM SIN^2 + COS^2 = 1 identity
1710 PRINT "Pythagorean Identity: SIN^2(x) + COS^2(x) should = 1"
1720 FOR I = 1 TO 10
1730   READ X
1740   S = SIN(X)
1750   C = COS(X)
1760   Y = S*S + C*C
1770   PRINT "x="; X, "Result="; Y, "Error="; ABS(Y - 1)
1780 NEXT I
1790 PRINT
1800 DATA 0, 0.5, 1.0, 1.5708, 3.14159, 6.28319, 0.1, 2.0, 4.0, 5.0
1900 REM Division precision test
1910 PRINT "Division Precision Tests:"
1920 PRINT "1/3 * 3 should = 1"
1930 Y = (1/3) * 3
1940 PRINT "Result="; Y, "Error="; ABS(Y - 1)
1950 PRINT "1/7 * 7 should = 1"
1960 Y = (1/7) * 7
1970 PRINT "Result="; Y, "Error="; ABS(Y - 1)
1980 PRINT "1/49 * 49 should = 1"
1990 Y = (1/49) * 49
2000 PRINT "Result="; Y, "Error="; ABS(Y - 1)
2010 PRINT
2100 REM Very small number handling
2110 PRINT "Small Number Tests:"
2120 PRINT "1E-10 + 1E-10 ="; 1E-10 + 1E-10
2130 PRINT "1E-20 * 1E20 ="; 1E-20 * 1E20
2140 PRINT "1E-30 (should not be 0) ="; 1E-30
2150 PRINT
2200 REM Very large number handling
2210 PRINT "Large Number Tests:"
2220 PRINT "1E20 + 1E20 ="; 1E20 + 1E20
2230 PRINT "1E30 / 1E15 ="; 1E30 / 1E15
2240 PRINT
9999 END
