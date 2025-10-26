10 REM Test DATA/READ/RESTORE
20 PRINT "Reading colors:"
30 FOR I = 1 TO 3
40   READ C$
50   PRINT I; ": "; C$
60 NEXT I
70 PRINT "Restoring and reading again:"
80 RESTORE
90 READ C$
100 PRINT "First color: "; C$
110 DATA "Red", "Green", "Blue"
999 END
