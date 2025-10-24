10 REM Test Expression Reassociation
20 REM This program tests the expression reassociation optimizer
30 REM
40 REM Addition chain: (A + 1) + 2 should become A + 3
50 A = 10
60 B = (A + 1) + 2
70 PRINT "B ="; B
80 REM
90 REM Multiplication chain: (A * 2) * 3 should become A * 6
100 C = (A * 2) * 3
110 PRINT "C ="; C
120 REM
130 REM Mixed: 2 + (A + 3) should become A + 5
140 D = 2 + (A + 3)
150 PRINT "D ="; D
160 REM
170 REM Complex chain: (A * B) * 2 * 3 should become (A * B) * 6
180 B = 5
190 E = (A * B) * 2 * 3
200 PRINT "E ="; E
210 REM
220 REM Longer addition chain: 1 + A + 2 + 3 should become A + 6
230 F = 1 + A + 2 + 3
240 PRINT "F ="; F
250 REM
260 REM Longer multiplication chain: 2 * A * 3 * 4 should become A * 24
270 G = 2 * A * 3 * 4
280 PRINT "G ="; G
290 END
