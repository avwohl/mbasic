10 REM Test improper loop nesting - should error
20 REM FOR...WHILE...NEXT...WEND is invalid
30 FOR I = 1 TO 3
40   WHILE I < 5
50   NEXT I
60 WEND
70 END
