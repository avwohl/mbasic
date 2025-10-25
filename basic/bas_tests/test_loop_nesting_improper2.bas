10 REM Test improper loop nesting - should error
20 REM WHILE...FOR...WEND...NEXT is invalid
30 J = 0
40 WHILE J < 3
50   FOR I = 1 TO 3
60   WEND
70 NEXT I
80 END
