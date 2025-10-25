10 REM Test proper loop nesting - WHILE inside FOR
20 FOR I = 1 TO 2
30   PRINT "Outer FOR I="; I
40   J = 0
50   WHILE J < 2
60     PRINT "  Inner WHILE J="; J
70     J = J + 1
80   WEND
90 NEXT I
100 PRINT "Proper nesting complete"
110 END
