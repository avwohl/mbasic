10 REM Test improper nesting - RETURN inside FOR without matching GOSUB
20 FOR I = 1 TO 5
30   PRINT I
40   RETURN
50 NEXT I
60 END
