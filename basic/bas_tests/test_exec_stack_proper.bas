10 REM Test proper nesting of GOSUB, FOR, WHILE
20 PRINT "Testing proper nesting"
30 FOR I = 1 TO 2
40   PRINT "FOR I="; I
50   GOSUB 100
60 NEXT I
70 PRINT "All done"
80 END
100 REM Subroutine
110 J = 0
120 WHILE J < 2
130   PRINT "  WHILE J="; J
140   J = J + 1
150 WEND
160 RETURN
