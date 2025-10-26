10 REM Test proper loop nesting - FOR inside WHILE
20 J = 0
30 WHILE J < 2
40   PRINT "Outer WHILE J="; J
50   FOR I = 1 TO 3
60     PRINT "  Inner FOR I="; I
70   NEXT I
80   J = J + 1
90 WEND
100 PRINT "Proper nesting complete"
110 END
