10 REM Test IF/THEN/ELSE with integers only
20 LET A% = 10
30 LET B% = 20
40 IF A% < B% THEN LET C% = 1
50 IF A% > B% THEN LET C% = 2 ELSE LET C% = 3
60 REM C should be 3 now
70 IF C% = 3 THEN GOTO 100
80 LET D% = 99
90 GOTO 110
100 LET D% = 42
110 REM Test nested
120 IF A% < B% THEN IF C% = 3 THEN LET E% = 7
130 END