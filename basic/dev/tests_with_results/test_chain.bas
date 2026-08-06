10 REM Test CHAIN Statement
20 REM The program CHAINed to is written here rather
30 REM than shipped beside this file, so the test runs
40 REM in whatever directory it is started from - CP/M
50 REM included, where 8.3 is the only name MBASIC can
60 REM open. Q$ builds the quotes: MBASIC has no ""
70 REM escape inside a string literal.
80 PRINT "Testing CHAIN"
90 PRINT "=============="
100 PRINT
110 X = 42
120 Y$ = "Hello"
130 Q$ = CHR$(34)
140 OPEN "O", 1, "CHNTGT.BAS"
150 PRINT #1, "500 PRINT " + Q$ + "In the chained program" + Q$
160 PRINT #1, "510 PRINT " + Q$ + "X =" + Q$ + ";X;" + Q$ + ", Y$ = " + Q$ + ";Y$"
170 PRINT #1, "520 KILL " + Q$ + "CHNTGT.BAS" + Q$
180 PRINT #1, "530 PRINT " + Q$ + "CHAIN tests complete!" + Q$
190 PRINT #1, "540 END"
200 CLOSE 1
210 PRINT "Test 1: CHAIN with ALL flag (preserves variables)"
220 PRINT "Before CHAIN: X ="; X; ", Y$ = "; Y$
230 PRINT
240 CHAIN "CHNTGT.BAS", , ALL
250 REM CHAIN replaces the program - nothing below runs
260 PRINT "This line should never print"
270 END
