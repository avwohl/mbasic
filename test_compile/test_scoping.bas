100 REM Comprehensive scoping test
110 REM Test FOR loop with GOSUB
120 FOR I% = 1 TO 3
130 GOSUB 300
140 NEXT I%
150 REM Test WHILE loop with GOTO
160 J% = 1
170 WHILE J% <= 2
180 PRINT J%
190 J% = J% + 1
200 WEND
210 END
300 REM Subroutine with nested WHILE
310 K% = I%
320 WHILE K% > 0
330 PRINT K%
340 K% = K% - 1
350 WEND
360 RETURN
