10 REM Test improper nesting - NEXT across GOSUB boundary
20 FOR I = 1 TO 3
30   GOSUB 100
40 NEXT I
50 END
100 PRINT "In subroutine"
110 NEXT I
120 RETURN
