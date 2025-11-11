10 REM Test IF/THEN/ELSE statements
20 LET A% = 10
30 LET B% = 20
40 PRINT "Testing IF/THEN/ELSE with A="; A%; " and B="; B%
50 IF A% < B% THEN PRINT "A is less than B"
60 IF A% > B% THEN PRINT "A is greater than B" ELSE PRINT "A is not greater than B"
70 IF A% = 10 THEN GOTO 100
80 PRINT "This should not print"
90 GOTO 110
100 PRINT "A equals 10 (GOTO worked)"
110 REM Test nested condition
120 LET C% = 15
130 IF C% > A% THEN IF C% < B% THEN PRINT "C is between A and B"
140 END