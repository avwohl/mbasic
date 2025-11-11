10 REM Test logical operators AND, OR, NOT
20 LET A% = 5
30 LET B% = 10
40 LET C% = 15
50 REM Test AND
60 IF A% < B% AND B% < C% THEN LET D% = 1 ELSE LET D% = 0
70 REM D should be 1 (true)
80 IF A% > B% AND B% < C% THEN LET E% = 1 ELSE LET E% = 0
90 REM E should be 0 (false)
100 REM Test OR
110 IF A% > B% OR B% < C% THEN LET F% = 1 ELSE LET F% = 0
120 REM F should be 1 (true)
130 IF A% > B% OR B% > C% THEN LET G% = 1 ELSE LET G% = 0
140 REM G should be 0 (false)
150 REM Test NOT
160 IF NOT A% > B% THEN LET H% = 1 ELSE LET H% = 0
170 REM H should be 1 (true, since A is not > B)
180 IF NOT A% < B% THEN LET I% = 1 ELSE LET I% = 0
190 REM I should be 0 (false, since A is < B)
200 REM Complex expression
210 IF (A% < B%) AND (B% < C%) OR NOT (A% = C%) THEN LET J% = 1
220 END